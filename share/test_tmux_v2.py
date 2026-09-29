#!/usr/bin/env python3
"""Acceptance test for the real client-attached tmux popup route.

This deliberately does not invoke the lesson directly. A nested tmux client
attaches to an isolated server, that server fires the installed
``client-attached`` hook, and an outer tmux pane captures the popup exactly as
the attached terminal renders it.
"""

from __future__ import annotations

import json
import os
import fcntl
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
GATE = Path.home() / ".local" / "bin" / "vim-daily-gate"
HOOK = Path.home() / ".tmux" / "scripts" / "vim-drill-popup.sh"
COLUMNS = int(os.environ.get("VIM_DAILY_TEST_COLUMNS", "188"))
ROWS = int(os.environ.get("VIM_DAILY_TEST_ROWS", "49"))
CLEAN_MODE = os.environ.get("VIM_DAILY_TEST_CLEAN") == "1"
CURRICULUM = json.loads((ROOT / "share" / "curriculum-v2.json").read_text(encoding="utf-8"))
M0_FIRST = next(card for card in CURRICULUM["cards"] if card["id"] == "M0.01")
M0_FIRST_QUESTION = next(question for question in CURRICULUM["questions"]
                         if question["id"] == "M0.01.P01")
QUESTION_ORDER = (1, 2, 0, 3)  # Put semantic choice 0 at displayed letter c.
M0_CARD_IDS = next(module for module in CURRICULUM["modules"]
                   if module["id"] == "M0")["card_ids"]
M0_TOTAL = len(M0_CARD_IDS)
M0_AFTER_FIRST = M0_CARD_IDS[M0_CARD_IDS.index("M0.01") + 1]
S0_TOTAL = len(next(stage for stage in CURRICULUM["stages"]
                    if stage["id"] == "S0")["card_ids"])


def run(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, **kwargs)


def tmux(socket, *args, **kwargs):
    return run("tmux", "-L", socket, *args, **kwargs)


def capture_outer(socket, pane):
    return tmux(socket, "capture-pane", "-p", "-t", pane, "-S", "-60",
                capture_output=True).stdout


def capture_until(socket, pane, needles, timeout=5.0):
    """Capture until every needle is rendered, or return the last screen.

    A capture taken immediately after send-keys can precede the redraw. This
    bounds the wait; it never weakens the assertion made on the returned screen.
    """
    import time
    deadline = time.monotonic() + timeout
    while True:
        screen = capture_outer(socket, pane)
        flat = " ".join(screen.split())
        if all(any(n in flat for n in (needle if isinstance(needle, tuple) else (needle,)))
               for needle in needles) or time.monotonic() >= deadline:
            return screen
        time.sleep(0.1)


def capture_until_absent(socket, pane, needles, timeout=5.0):
    """Capture after transient UI text has disappeared."""
    deadline = time.monotonic() + timeout
    while True:
        screen = capture_outer(socket, pane)
        flat = " ".join(screen.split())
        if all(needle not in flat for needle in needles) or time.monotonic() >= deadline:
            return screen
        time.sleep(0.1)


with tempfile.TemporaryDirectory(prefix="vim-daily-tmux-") as tmp:
    root = Path(tmp)
    data = root / "data"
    state = root / "state"
    data.mkdir()
    state.mkdir()
    (data / "vim-daily").symlink_to(ROOT / "share", target_is_directory=True)

    token = uuid.uuid4().hex[:12]
    inner_socket = "vimdaily-inner-" + token
    outer_socket = "vimdaily-outer-" + token
    inner_session = "lesson"
    outer_session = "terminal"
    ready = "vim-daily-ready-" + token
    feedback = "vim-daily-feedback-" + token
    question = "vim-daily-question-" + token
    post = "vim-daily-post-" + token
    done = "vim-daily-done-" + token
    lesson_env = {
        # The default route uses the learner's installed Neovim config. Keep
        # its data root so LazyVim never mistakes the test for a fresh install.
        "XDG_DATA_HOME": os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share")),
        "XDG_STATE_HOME": str(state),
        "EDITOR": "nvim",
        "TERM": "xterm-256color",
        "VIM_DAILY_TMUX_READY_SIGNAL": ready,
        "VIM_DAILY_TMUX_QUESTION_SIGNAL": question,
        "VIM_DAILY_TMUX_FEEDBACK_SIGNAL": feedback,
        "VIM_DAILY_TMUX_POST_SIGNAL": post,
        "VIM_DAILY_TMUX_FINISHED_SIGNAL": done,
        "VIM_DAILY_TEST_CHOICE_ORDER": "".join(str(value) for value in QUESTION_ORDER),
    }
    if CLEAN_MODE:
        lesson_env["VIM_DAILY_CLEAN"] = "1"
    process_env = dict(os.environ, **lesson_env)

    # The grammar primer now precedes the first editor card. Seed only that
    # card so this acceptance test can keep exercising the full live Neovim
    # surface. M0.01's transfer question deliberately follows the guided edit:
    # no learner is interrogated about a command before seeing and using it.
    tutor_state = state / "vim-daily"
    tutor_state.mkdir(parents=True)
    (tutor_state / "events-v2.jsonl").write_text(json.dumps({
        "type": "card", "result": "pass", "card_id": "M0.P0", "module_id": "M0",
        "at": "2026-09-28T00:00:00-04:00",
    }) + "\n", encoding="utf-8")

    if GATE.resolve() != ROOT / "bin" / "vim-daily-gate":
        raise AssertionError("installed gate does not resolve to this checkout: %s" % GATE.resolve())
    gate_source = GATE.read_text(encoding="utf-8")
    if gate_source.count("cindent=false") < 2:
        raise AssertionError("art-local cindent must be disabled initially and after plugins load")
    if not HOOK.is_file():
        raise AssertionError("installed client-attached hook is missing: %s" % HOOK)
    if HOOK.resolve() != ROOT / "tmux" / "vim-drill-popup.sh":
        raise AssertionError("installed hook does not resolve to this checkout: %s" % HOOK.resolve())

    # Parse the real tmux configuration on an isolated server and inspect the
    # resulting hook.  A hand-installed test hook alone could mask stale user
    # configuration.
    config_socket = "vimdaily-config-" + token
    try:
        run("tmux", "-L", config_socket, "-f", str(Path.home() / ".tmux.conf"),
            "new-session", "-d", "-s", "config-check")
        configured = tmux(config_socket, "show-hooks", "-g", "client-attached",
                          capture_output=True).stdout
        if str(HOOK) not in configured:
            raise AssertionError("real tmux config installed a different client-attached hook: " + configured)
    finally:
        subprocess.run(["tmux", "-L", config_socket, "kill-server"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    due = subprocess.run([str(GATE), "--due-quiet"], env=process_env,
                         text=True, capture_output=True)
    if due.returncode != 0 or due.stdout or due.stderr:
        raise AssertionError("fresh isolated state was not silently due: %r" % due)

    try:
        # Start a clean inner server with no client. The only route that starts
        # the lesson below is the same installed client-attached hook used by
        # the real tmux configuration.
        run("tmux", "-L", inner_socket, "-f", "/dev/null", "new-session", "-d",
            "-s", inner_session, "-x", str(COLUMNS), "-y", str(ROWS),
            "/bin/zsh", "-f")
        # Start from the user's common global `mouse on` preference. The popup
        # may override it only on this session while visible, and must remove
        # that local override when it closes.
        tmux(inner_socket, "set-option", "-g", "mouse", "on")
        # Reproduce a killed owner whose numeric PID has already been reused
        # by an unrelated live process (this test runner). PID existence alone
        # must not preserve the stale override.
        stale_owner = str(os.getpid())
        tmux(inner_socket, "set-option", "-t", inner_session, "mouse", "off")
        tmux(inner_socket, "set-option", "-t", inner_session,
             "@vim_daily_mouse_owner", stale_owner)
        tmux(inner_socket, "set-option", "-t", inner_session,
             "@vim_daily_mouse_base", "inherit")
        for key, value in lesson_env.items():
            tmux(inner_socket, "set-environment", "-g", key, value)
        tmux(inner_socket, "set-hook", "-g", "client-attached",
             "run-shell -b %s" % HOOK)
        tmux(inner_socket, "wait-for", "-L", ready)
        tmux(inner_socket, "wait-for", "-L", question)
        tmux(inner_socket, "wait-for", "-L", feedback)
        tmux(inner_socket, "wait-for", "-L", post)
        tmux(inner_socket, "wait-for", "-L", done)

        # The outer server supplies a real terminal for the inner attached
        # client. Capturing this pane therefore captures display-popup itself,
        # not merely the pane hidden underneath the popup.
        nested_attach = "env -u TMUX tmux -L %s attach-session -t %s" % (
            inner_socket, inner_session)
        run("tmux", "-L", outer_socket, "-f", "/dev/null", "new-session", "-d",
            "-s", outer_session, "-x", str(COLUMNS), "-y", str(ROWS), nested_attach)
        outer_pane = tmux(outer_socket, "list-panes", "-t", outer_session,
                          "-F", "#{pane_id}", capture_output=True).stdout.strip()

        try:
            tmux(inner_socket, "wait-for", "-L", ready, timeout=20)
            tmux(inner_socket, "wait-for", "-U", ready)
        except subprocess.TimeoutExpired as exc:
            screen = capture_outer(outer_socket, outer_pane)
            raise AssertionError(
                "client-attached hook did not render a ready popup:\n" + screen
            ) from exc

        screen = capture_outer(outer_socket, outer_pane)
        tmux_options = "\n".join([
            tmux(inner_socket, "show-options", "-g", option,
                 capture_output=True).stdout.strip()
            for option in ("mouse", "set-clipboard")
        ])
        if "mouse on" not in tmux_options:
            raise AssertionError("popup changed the global tmux mouse option: " + tmux_options)
        popup_mouse = tmux(
            inner_socket, "show-options", "-Av", "-t", inner_session, "mouse",
            capture_output=True).stdout.strip()
        if popup_mouse != "off":
            raise AssertionError(
                "popup did not release ordinary drag to the terminal: " + popup_mouse)
        popup_owner = tmux(
            inner_socket, "show-options", "-qv", "-t", inner_session,
            "@vim_daily_mouse_owner", capture_output=True).stdout.strip()
        popup_base = tmux(
            inner_socket, "show-options", "-qv", "-t", inner_session,
            "@vim_daily_mouse_base", capture_output=True).stdout.strip()
        if not popup_owner.isdigit() or popup_owner == stale_owner:
            raise AssertionError("popup did not replace the stale mouse owner: " + popup_owner)
        if popup_base != "inherit":
            raise AssertionError("popup did not preserve the inherited mouse base: " + popup_base)
        copy_bindings = tmux(
            inner_socket, "list-keys", "-T", "copy-mode-vi",
            capture_output=True).stdout
        if "pbcopy" in copy_bindings:
            raise AssertionError("popup rebound the global copy-mode-vi table:\n" + copy_bindings)
        required = [
            "vim drill · drag selects · Cmd-C copies · questions: y copies all",
            "NEOVIM × ASCII ANIMATION",
            "M0.01",
            "DO THIS",
            "NORMAL",
            "PROGRESS S0 1/%d learning · M0 1/%d" % (S0_TOTAL, M0_TOTAL),
            "XP 10",
            "TARGET",
        ]
        if ROWS < 38:
            required += ["RECIPE"]
        else:
            required += ["COMMAND RECIPE", "WHY THIS EXISTS", "Motion intent:",
                         "Authoring principle:", "Failure to watch:"]
        screen = capture_until(outer_socket, outer_pane, required)
        flattened = " ".join(screen.split())
        missing = [text for text in required if text not in flattened]
        if missing:
            raise AssertionError(
                "automatic popup capture missing %r:\n%s" % (missing, screen)
            )
        if "--show-capture" in sys.argv:
            print("--- AUTOMATIC CLIENT-ATTACHED POPUP pane=%s ---" % outer_pane)
            print(screen.rstrip())

        # Inspect the lower half of the same read-only brief. This proves the
        # legacy teaching sections exist in the rendered UI, not merely in a
        # generated file hidden below the split viewport.
        tmux(outer_socket, "send-keys", "-t", outer_pane, "C-w", "w")
        tmux(outer_socket, "send-keys", "-t", outer_pane, "-l", "/KEYS WORTH KEEPING")
        tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter", "z", "t")
        key_required = [
            "KEYS WORTH KEEPING",
            "replace one character",
        ]
        key_brief = capture_until(outer_socket, outer_pane, key_required)
        # At 80x24 the brief pane is ~12 rows, so the source sections sit below
        # the key vocabulary; search for them separately (VD-13).
        tmux(outer_socket, "send-keys", "-t", outer_pane, "-l", "/WHERE THIS METHOD")
        tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter", "z", "t")
        source_required = [
            "WHERE THIS METHOD COMES FROM",
            "ascii-art-authoring",
            ("LEGACY SOURCE", "LEGACY LESSON SOURCES"),
        ]
        key_brief += capture_until(outer_socket, outer_pane, source_required)
        key_required += source_required
        key_flattened = " ".join(key_brief.split())
        key_missing = [text for text in key_required
                       if not any(option in key_flattened for option in
                                  (text if isinstance(text, tuple) else (text,)))]
        if key_missing:
            raise AssertionError(
                "legacy key/source teaching missing %r:\n%s" % (key_missing, key_brief)
            )
        tmux(outer_socket, "send-keys", "-t", outer_pane, "-l", "/LEGACY VIM CONCEPT")
        tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter", "z", "t")
        concept_brief = capture_until(outer_socket, outer_pane,
                                      ["LEGACY VIM CONCEPT", "Motions:"])
        concept_flat = " ".join(concept_brief.split())
        if "LEGACY VIM CONCEPT" not in concept_flat or "Motions:" not in concept_flat:
            raise AssertionError("legacy concept prose missing:\n" + concept_brief)
        tmux(outer_socket, "send-keys", "-t", outer_pane, "G")
        lower_required = [
            "READING THE RECIPE",
            "<C-k>.M middle-dot",  # "digraph" may wrap past the split border
            "SUBMIT / STUCK",
            ":q! exits without submission",
        ]
        lower_brief = capture_until(outer_socket, outer_pane, lower_required)
        lower_flattened = " ".join(lower_brief.split())
        lower_missing = [text for text in lower_required if text not in lower_flattened]
        if lower_missing:
            raise AssertionError(
                "scrollable teaching brief missing %r:\n%s" % (lower_missing, lower_brief)
            )
        if "--show-capture" in sys.argv:
            print("--- LEGACY KEYS/SOURCE BRIEF pane=%s ---" % outer_pane)
            print(key_brief.rstrip())
            print("--- LEGACY CONCEPT BRIEF pane=%s ---" % outer_pane)
            print(concept_brief.rstrip())
            print("--- SCROLLED TEACHING BRIEF pane=%s ---" % outer_pane)
            print(lower_brief.rstrip())
        tmux(outer_socket, "send-keys", "-t", outer_pane, "C-w", "w")

        # tmux releasing the mouse is only half the selection path: Neovim
        # must not request terminal mouse reporting either. Verify the actual
        # headed tutor process after the learner's plugins have loaded.
        tmux(outer_socket, "send-keys", "-t", outer_pane, "-l",
             ":echo empty(&mouse)?'VIM_DAILY_MOUSE_RELEASED':'VIM_DAILY_MOUSE_CAPTURED'")
        tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter")
        mouse_screen = capture_until(outer_socket, outer_pane,
                                     ["VIM_DAILY_MOUSE_RELEASED"])
        mouse_flat = " ".join(mouse_screen.split())
        if "VIM_DAILY_MOUSE_RELEASED" not in mouse_flat:
            raise AssertionError("tutor Neovim still captured drag events:\n" + mouse_screen)
        tmux(outer_socket, "send-keys", "-t", outer_pane, "-l", ":redraw")
        tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter")

        # The personal config owns the default editor chrome. Only the explicit
        # clean fallback owns a TUTOR statusline and F1 help float.
        tmux(outer_socket, "send-keys", "-t", outer_pane, "v")
        visual_screen = capture_until(outer_socket, outer_pane, ["VISUAL"])
        if "VISUAL" not in " ".join(visual_screen.split()):
            raise AssertionError("live mode line did not enter VISUAL:\n" + visual_screen)
        visual_flat = " ".join(visual_screen.split())
        if CLEAN_MODE and "TUTOR" not in visual_flat:
            raise AssertionError("clean fallback tutor chrome is missing:\n" + visual_screen)
        if not CLEAN_MODE and "TUTOR" in visual_flat:
            raise AssertionError("personal lualine was replaced by tutor chrome:\n" + visual_screen)
        tmux(outer_socket, "send-keys", "-t", outer_pane, "Escape")
        if CLEAN_MODE:
            tmux(outer_socket, "send-keys", "-t", outer_pane, "F1")
            help_screen = capture_until(outer_socket, outer_pane,
                                        ["CHEAT SHEET", "NEW LINE BELOW"])
            if "CHEAT SHEET" not in " ".join(help_screen.split()):
                raise AssertionError("clean fallback F1 help did not open:\n" + help_screen)
            tmux(outer_socket, "send-keys", "-t", outer_pane, "F1")
            capture_until_absent(outer_socket, outer_pane, ["CHEAT SHEET"])
        else:
            tmux(outer_socket, "send-keys", "-t", outer_pane, "-l", ":WhichKey")
            tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter")
            which_key_screen = capture_until(
                outer_socket, outer_pane, ["Start of line", "Prev word"])
            which_key_flat = " ".join(which_key_screen.split())
            if "Start of line" not in which_key_flat or "Prev word" not in which_key_flat:
                raise AssertionError("personal WhichKey did not open:\n" + which_key_screen)
            tmux(outer_socket, "send-keys", "-t", outer_pane, "Escape")
            closed_which_key = capture_until_absent(
                outer_socket, outer_pane, ["Start of line", "Prev word"])
            closed_flat = " ".join(closed_which_key.split())
            if "Start of line" in closed_flat or "Prev word" in closed_flat:
                raise AssertionError("personal WhichKey did not close:\n" + closed_which_key)

        # Personal config remains in charge, but `o` in an indented art row
        # must start at column zero. Prove the behavior through the saved file,
        # then undo it so the graded attempt still begins at its checkpoint.
        art_path = (state / "vim-daily" / "projects" /
                    M0_FIRST["project_id"] / "strip.txt")
        before_indent_probe = art_path.read_text(encoding="utf-8")
        tmux(outer_socket, "send-keys", "-t", outer_pane, "o")
        tmux(outer_socket, "send-keys", "-t", outer_pane, "-l", "X")
        tmux(outer_socket, "send-keys", "-t", outer_pane, "Escape")
        tmux(outer_socket, "send-keys", "-t", outer_pane, "-l", ":w")
        tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter")
        deadline = time.monotonic() + 5
        while art_path.read_text(encoding="utf-8") == before_indent_probe and time.monotonic() < deadline:
            time.sleep(0.05)
        probed_lines = art_path.read_text(encoding="utf-8").splitlines()
        if "X" not in probed_lines:
            raise AssertionError("o inherited art indentation or probe keys were lost: %r" % probed_lines)
        tmux(outer_socket, "send-keys", "-t", outer_pane, "u")
        tmux(outer_socket, "send-keys", "-t", outer_pane, "-l", ":w")
        tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter")
        deadline = time.monotonic() + 5
        while art_path.read_text(encoding="utf-8") != before_indent_probe and time.monotonic() < deadline:
            time.sleep(0.05)
        if art_path.read_text(encoding="utf-8") != before_indent_probe:
            raise AssertionError("indent probe did not restore the lesson checkpoint")

        # Legacy coaching parity: the operator's hint-mode Hardtime intervenes
        # on wasteful repeated unit motions while the learner is still editing.
        tmux(outer_socket, "send-keys", "-t", outer_pane, "k", "k", "k", "k", "k")
        coached_screen = capture_until(outer_socket, outer_pane, [
            ("You pressed the k key", "Hardtime", "HARDTIME · k BLOCKED")])
        coached_flat = " ".join(coached_screen.split())
        # hardtime.nvim's notice is titled "Hardtime"; at 80x24 its message is
        # truncated ("You pressed the k key too …"), so accept the title.
        if not ("You pressed the k key" in coached_flat or "Hardtime" in coached_flat
                or "HARDTIME · k BLOCKED" in coached_flat):
            raise AssertionError("repeated-motion coach did not intervene:\n" + coached_screen)

        # First submit no edit. This proves the exact automatic route also
        # keeps a failed attempt visible with replay and unchanged progress.
        tmux(outer_socket, "send-keys", "-t", outer_pane, "-l", ":wq")
        tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter")
        try:
            tmux(inner_socket, "wait-for", "-L", feedback, timeout=20)
            tmux(inner_socket, "wait-for", "-U", feedback)
        except subprocess.TimeoutExpired as exc:
            stuck = capture_outer(outer_socket, outer_pane)
            raise AssertionError(
                "automatic popup did not render failed-attempt feedback:\n" + stuck
            ) from exc

        failed_screen = capture_outer(outer_socket, outer_pane)
        failed_flattened = " ".join(failed_screen.split())
        if not (state / "vim-daily" / "last-prompt").exists():
            raise AssertionError("failed attempt evidence did not start the cooldown")
        failed_required = [
            "DO THIS",
            "ATTEMPT NOT PASSED",
            "no progress awarded",
            "RESULT COMPARISON",
            "KEYSTROKE LEDGER",
            "YOU TYPED",
            "THE RECIPE ASKS FOR",
            "DO / AVOID",
            "SOURCE",
        ]
        if ROWS < 28:
            failed_required += ["YOURS", "TARGET", "✗"]
        elif ROWS < 55:
            failed_required += ["not this"]
        else:
            failed_required += [
                "YOURS (what you saved)", "TARGET (what it should be)",
                "first difference at column",
                "YOU TYPED", "THE RECIPE ASKS FOR", "you skipped this",
                "WHY THIS EXISTS", "Authoring principle:", "Failure to watch:",
                "WHAT THIS LESSON BUYS YOU",
            ]
        failed_missing = [text for text in failed_required if text not in failed_flattened]
        if failed_missing:
            raise AssertionError(
                "failed-attempt popup capture missing %r:\n%s" % (failed_missing, failed_screen)
            )
        if "--show-capture" in sys.argv:
            print("--- FAILED FEEDBACK PAGE pane=%s ---" % outer_pane)
            print(failed_screen.rstrip())

        # Page two owns progress; it cannot be scrolled away by a long key
        # table or buffer diff on page one.
        tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter")
        try:
            tmux(inner_socket, "wait-for", "-L", post, timeout=20)
            tmux(inner_socket, "wait-for", "-U", post)
        except subprocess.TimeoutExpired as exc:
            stuck = capture_outer(outer_socket, outer_pane)
            raise AssertionError("failed attempt did not render progress page:\n" + stuck) from exc
        failed_progress_screen = capture_outer(outer_socket, outer_pane)
        failed_progress_flat = " ".join(failed_progress_screen.split())
        failed_progress_required = [
            "PROGRESS UNCHANGED", "SKILL TREE / MODULE PROGRESS", "S0", "1/%d" % S0_TOTAL,
            "streak: 1 day", "next: M0.01",
        ]
        missing = [text for text in failed_progress_required if text not in failed_progress_flat]
        if not (("XP 10" in failed_progress_flat and "today 1/12" in failed_progress_flat)
                or ("XP: 10" in failed_progress_flat
                    and "today: 1/12 lessons" in failed_progress_flat)):
            missing.append("compact or full XP/today progress evidence")
        if missing:
            raise AssertionError("failed progress page missing %r:\n%s" %
                                 (missing, failed_progress_screen))
        if "--show-capture" in sys.argv:
            print("--- UNCHANGED PROGRESS PAGE pane=%s ---" % outer_pane)
            print(failed_progress_screen.rstrip())

        # Retry from the restored checkpoint. The same popup must then render
        # the successful debrief and wait for an explicit close.
        tmux(inner_socket, "wait-for", "-L", ready)
        tmux(inner_socket, "wait-for", "-L", feedback)
        tmux(inner_socket, "wait-for", "-L", post)
        tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter")
        try:
            tmux(inner_socket, "wait-for", "-L", ready, timeout=20)
            tmux(inner_socket, "wait-for", "-U", ready)
        except subprocess.TimeoutExpired as exc:
            stuck = capture_outer(outer_socket, outer_pane)
            raise AssertionError("automatic popup retry did not reopen Neovim:\n" + stuck) from exc

        tmux(outer_socket, "send-keys", "-t", outer_pane, "-l", M0_FIRST["expected"])
        tmux(outer_socket, "send-keys", "-t", outer_pane, "-l", ":wq")
        tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter")
        try:
            tmux(inner_socket, "wait-for", "-L", question, timeout=20)
            tmux(inner_socket, "wait-for", "-U", question)
        except subprocess.TimeoutExpired as exc:
            stuck = capture_outer(outer_socket, outer_pane)
            raise AssertionError(
                "guided edit did not lead to its after-question:\n" + stuck
            ) from exc
        question_screen = capture_outer(outer_socket, outer_pane)
        question_flat = " ".join(question_screen.split())
        displayed_stem = (M0_FIRST_QUESTION.get("compact_prompt")
                          if ROWS < 38 else M0_FIRST_QUESTION["prompt"])
        displayed_stem_line = next(
            line.strip() for line in displayed_stem.splitlines()
            if line.strip() and line.strip() not in {"ANIMATION", "NEOVIM"}
        )
        if not all(text in question_flat for text in (
                "ANIMATION", "NEOVIM", displayed_stem_line,
                "│", "a)", "b)", "c)", "d)")):
            raise AssertionError("guided after-question is incomplete:\n" + question_screen)
        # Keyboard copy is a second route when drag-selection is inconvenient.
        # It must copy the displayed art question without submitting an answer.
        # pbcopy/pbpaste are process-global.  The private tmux sockets and
        # temporary state roots do not stop a parallel size-matrix run from
        # restoring its old clipboard between this run's copy and read.
        clipboard_lock_path = Path(tempfile.gettempdir()) / "vim-daily-popup-clipboard.lock"
        with clipboard_lock_path.open("a+", encoding="utf-8") as clipboard_lock:
            fcntl.flock(clipboard_lock, fcntl.LOCK_EX)
            clipboard_before = subprocess.run(
                ["pbpaste"], text=True, capture_output=True, check=True).stdout
            try:
                tmux(outer_socket, "send-keys", "-t", outer_pane, "y", "Enter")
                copied_screen = capture_until(
                    outer_socket, outer_pane,
                    ["copied the complete question and choices"])
                if "copied the complete question and choices" not in " ".join(copied_screen.split()):
                    raise AssertionError("question copy control did not remain on the question:\n" + copied_screen)
                copied_page = subprocess.run(
                    ["pbpaste"], text=True, capture_output=True, check=True).stdout
                for copied_text in ("ANIMATION", "NEOVIM", displayed_stem_line,
                                    "│", "a)", "d)"):
                    if copied_text not in copied_page:
                        raise AssertionError(
                            "question clipboard omitted %r:\n%s" % (copied_text, copied_page))
            finally:
                subprocess.run(["pbcopy"], input=clipboard_before, text=True, check=True)
        answer_letter = "abcd"[
            QUESTION_ORDER.index(M0_FIRST_QUESTION["correct_choice"])
        ]
        if answer_letter != "c":
            raise AssertionError("acceptance fixture must exercise answer choice c")
        tmux(outer_socket, "send-keys", "-t", outer_pane,
             answer_letter, "Enter")
        if not (state / "vim-daily" / "last-prompt").exists():
            raise AssertionError("the submitted paired question did not record attempt evidence")
        try:
            tmux(inner_socket, "wait-for", "-L", feedback, timeout=20)
            tmux(inner_socket, "wait-for", "-U", feedback)
        except subprocess.TimeoutExpired as exc:
            stuck = capture_outer(outer_socket, outer_pane)
            raise AssertionError(
                "automatic popup did not render the successful post-lesson screen:\n" + stuck
            ) from exc

        post_screen = capture_outer(outer_socket, outer_pane)
        post_flattened = " ".join(post_screen.split())
        post_required = [
            "LESSON COMPLETE",
            "RESULT COMPARISON",
            "KEYSTROKE LEDGER",
            "YOU TYPED",
            "THE RECIPE ASKS FOR",
            "DO / AVOID",
            "SOURCE",
        ]
        if ROWS < 28:
            post_required += ["BEFORE", "AFTER (yours)", "exact target"]
        elif ROWS < 55:
            post_required += [M0_FIRST["expected"]]
        else:
            post_required += [
                "before", "after", "RESULT exact saved target verified",
                "YOU TYPED", "THE RECIPE ASKS FOR", "WHY THIS EXISTS",
                "WHAT THIS LESSON BUYS YOU",
            ]
        post_missing = [text for text in post_required if text not in post_flattened]
        if post_missing:
            raise AssertionError(
                "post-lesson popup capture missing %r:\n%s" % (post_missing, post_screen)
            )
        if "--show-capture" in sys.argv:
            print("--- SUCCESS FEEDBACK PAGE pane=%s ---" % outer_pane)
            print(post_screen.rstrip())

        tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter")
        try:
            tmux(inner_socket, "wait-for", "-L", post, timeout=20)
            tmux(inner_socket, "wait-for", "-U", post)
        except subprocess.TimeoutExpired as exc:
            stuck = capture_outer(outer_socket, outer_pane)
            raise AssertionError("success did not render progression page:\n" + stuck) from exc
        progress_screen = capture_outer(outer_socket, outer_pane)
        progress_flat = " ".join(progress_screen.split())
        progress_required = [
            "PROGRESS AWARDED", "SKILL TREE / MODULE PROGRESS", "S0", "2/%d" % S0_TOTAL,
            "streak: 1 day", "next: %s" % M0_AFTER_FIRST,
        ]
        missing = [text for text in progress_required if text not in progress_flat]
        if not (("XP 20" in progress_flat and "today 2/12" in progress_flat)
                or ("XP: 20" in progress_flat
                    and "today: 2/12 lessons" in progress_flat)):
            missing.append("compact or full XP/today progress evidence")
        if missing:
            raise AssertionError("success progress page missing %r:\n%s" %
                                 (missing, progress_screen))
        if "--show-capture" in sys.argv:
            print("--- AWARDED PROGRESS PAGE pane=%s ---" % outer_pane)
            print(progress_screen.rstrip())

        # The popup must remain open on the debrief until the learner closes it.
        held_before = capture_outer(outer_socket, outer_pane)
        time.sleep(0.25)
        held_after = capture_outer(outer_socket, outer_pane)
        if "PROGRESS AWARDED" not in held_before or "PROGRESS AWARDED" not in held_after:
            raise AssertionError("progress page did not remain visibly held before explicit close")
        held_flat = " ".join(held_after.split())
        for control in ("r = repeat this lesson",
                        "n = next lesson",
                        "f = feedback",
                        "Enter = close"):
            if control not in held_flat:
                raise AssertionError("held result omitted %r:\n%s" % (control, held_after))

        # VD-43: `f` on the held result records a feedback message with the
        # lesson context, then returns to the same held controls.
        tmux(outer_socket, "send-keys", "-t", outer_pane, "f", "Enter")
        asked = capture_until(outer_socket, outer_pane, ["what is wrong or confusing"])
        if "what is wrong or confusing" not in " ".join(asked.split()):
            raise AssertionError("feedback control did not ask for a message:\n" + asked)
        # A pasted multi-line message must stay one message; before VD-46 only
        # its first line was saved and the rest leaked into later prompts.
        tmux(outer_socket, "set-buffer", "headed feedback probe\nsecond pasted line\nthird line")
        tmux(outer_socket, "paste-buffer", "-t", outer_pane)
        tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter")
        saved = capture_until(outer_socket, outer_pane, ["feedback saved"])
        if "feedback saved" not in " ".join(saved.split()):
            raise AssertionError("feedback was not confirmed:\n" + saved)
        feedback_rows = [
            json.loads(line) for line in
            (state / "vim-daily" / "feedback.jsonl").read_text(encoding="utf-8").splitlines()]
        if not any(row.get("message") == "headed feedback probe\nsecond pasted line\nthird line"
                   and row.get("card_id") == "M0.01" and row.get("screen") == "lesson-end"
                   for row in feedback_rows):
            raise AssertionError("pasted feedback was split or lacks lesson context: %r" % feedback_rows)
        if len(feedback_rows) != 1:
            raise AssertionError("pasted lines leaked into extra feedback rows: %r" % feedback_rows)
        held_again = " ".join(capture_until(outer_socket, outer_pane, ["Enter = close"]).split())
        if "Enter = close" not in held_again:
            raise AssertionError("pasted lines were consumed by the held controls:\n" + held_again)

        # `r` repeats this passed lesson as isolated practice. It must reopen
        # the same card, accept the same edit, and preserve awarded progress.
        tmux(inner_socket, "wait-for", "-L", ready)
        tmux(inner_socket, "wait-for", "-L", feedback)
        tmux(inner_socket, "wait-for", "-L", post)
        tmux(outer_socket, "send-keys", "-t", outer_pane, "r", "Enter")
        try:
            tmux(inner_socket, "wait-for", "-L", ready, timeout=20)
            tmux(inner_socket, "wait-for", "-U", ready)
        except subprocess.TimeoutExpired as exc:
            stuck = capture_outer(outer_socket, outer_pane)
            raise AssertionError("repeat control did not reopen the same lesson:\n" + stuck) from exc
        repeat_screen = capture_outer(outer_socket, outer_pane)
        if "M0.01" not in " ".join(repeat_screen.split()):
            raise AssertionError("repeat control opened a different card:\n" + repeat_screen)
        tmux(outer_socket, "send-keys", "-t", outer_pane, "-l", M0_FIRST["expected"])
        tmux(outer_socket, "send-keys", "-t", outer_pane, "-l", ":wq")
        tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter")
        try:
            tmux(inner_socket, "wait-for", "-L", feedback, timeout=20)
            tmux(inner_socket, "wait-for", "-U", feedback)
        except subprocess.TimeoutExpired as exc:
            stuck = capture_outer(outer_socket, outer_pane)
            raise AssertionError("repeated lesson did not render feedback:\n" + stuck) from exc
        tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter")
        try:
            tmux(inner_socket, "wait-for", "-L", post, timeout=20)
            tmux(inner_socket, "wait-for", "-U", post)
        except subprocess.TimeoutExpired as exc:
            stuck = capture_outer(outer_socket, outer_pane)
            raise AssertionError("repeated lesson did not render practice progress:\n" + stuck) from exc
        practice_screen = capture_outer(outer_socket, outer_pane)
        practice_flat = " ".join(practice_screen.split())
        if "PRACTICE COMPLETE · PROGRESS UNCHANGED" not in practice_flat:
            raise AssertionError("repeat awarded progress instead of practice:\n" + practice_screen)
        if not (("XP 20" in practice_flat and "today 2/12" in practice_flat)
                or ("XP: 20" in practice_flat and "today: 2/12 lessons" in practice_flat)):
            raise AssertionError("repeat changed XP or daily credit:\n" + practice_screen)

        tmux(outer_socket, "send-keys", "-t", outer_pane, "Enter")
        try:
            tmux(inner_socket, "wait-for", "-L", done, timeout=20)
            tmux(inner_socket, "wait-for", "-U", done)
        except subprocess.TimeoutExpired as exc:
            stuck = capture_outer(outer_socket, outer_pane)
            raise AssertionError(
                "automatic popup submission did not finish:\n" + stuck
            ) from exc
        closed_screen = capture_outer(outer_socket, outer_pane)
        if "PROGRESS AWARDED" in closed_screen:
            raise AssertionError("explicit close left the popup visible:\n" + closed_screen)
        restored_mouse = tmux(
            inner_socket, "show-options", "-gv", "mouse",
            capture_output=True).stdout.strip()
        if restored_mouse != "on":
            raise AssertionError(
                "popup did not restore the user's tmux mouse preference: " + restored_mouse)
        restored_local_mouse = tmux(
            inner_socket, "show-options", "-q", "-t", inner_session, "mouse",
            capture_output=True).stdout.strip()
        if restored_local_mouse:
            raise AssertionError(
                "popup left a session-local mouse override: " + restored_local_mouse)
        for option in ("@vim_daily_mouse_owner", "@vim_daily_mouse_base"):
            leftover = tmux(
                inner_socket, "show-options", "-qv", "-t", inner_session,
                option, capture_output=True).stdout.strip()
            if leftover:
                raise AssertionError("popup left mouse ownership metadata: %s=%s" % (
                    option, leftover))

        events = [
            json.loads(line)
            for line in (state / "vim-daily" / "events-v2.jsonl")
            .read_text(encoding="utf-8").splitlines()
        ]
        assert any(row.get("card_id") == "M0.01" and row.get("result") == "pass"
                   for row in events), events
        question_event = next(row for row in events
                              if row.get("question_id") == M0_FIRST_QUESTION["id"])
        assert question_event["question_evidence"]["raw_answer"] == "c", question_event
        profile = "clean fallback" if CLEAN_MODE else "real user config"
        print("PASS client-attached hook rendered and completed the automatic popup (%dx%d, %s)" %
              (COLUMNS, ROWS, profile))
    finally:
        for socket in (outer_socket, inner_socket):
            subprocess.run(["tmux", "-L", socket, "kill-server"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # VD-31: kill-server kills the Neovim TUI but can orphan its
        # `nvim --embed` server (reparented to launchd; it ignores SIGTERM). Kill anything still
        # referring to this test's private state directory.
        subprocess.run(["pkill", "-9", "-f", tmp], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
