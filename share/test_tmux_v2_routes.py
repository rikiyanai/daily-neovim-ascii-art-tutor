#!/usr/bin/env python3
"""Headed regression coverage for every v2 lesson route in a real tmux popup."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import time
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
GATE = Path.home() / ".local" / "bin" / "vim-daily-gate"
HOOK = Path.home() / ".tmux" / "scripts" / "vim-drill-popup.sh"
CUR = json.loads((ROOT / "share" / "curriculum-v2.json").read_text(encoding="utf-8"))
CARDS = {card["id"]: card for card in CUR["cards"]}
QUESTIONS = {question["id"]: question for question in CUR["questions"]}
M0_CARD_IDS = next(module for module in CUR["modules"] if module["id"] == "M0")["card_ids"]
COLUMNS = int(os.environ.get("VIM_DAILY_TEST_COLUMNS", "188"))
ROWS = int(os.environ.get("VIM_DAILY_TEST_ROWS", "49"))


def passed_before(card_id):
    """Seed every earlier M0 card without freezing a stale numeric ordinal."""
    return M0_CARD_IDS.index(card_id)


def run(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, **kwargs)


def tmux(socket, *args, **kwargs):
    return run("tmux", "-L", socket, *args, **kwargs)


def wait_signal(socket, signal):
    try:
        tmux(socket, "wait-for", "-L", signal, timeout=20)
        subprocess.run(["tmux", "-L", socket, "wait-for", "-U", signal],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.TimeoutExpired as exc:
        raise AssertionError("timed out waiting for tmux signal %s" % signal) from exc


def capture(socket, pane):
    return tmux(socket, "capture-pane", "-p", "-t", pane, "-S", "-80",
                capture_output=True).stdout


def send_text(socket, pane, text):
    tmux(socket, "send-keys", "-t", pane, "-l", text)


def send_spec(socket, pane, spec):
    """Send the curriculum's angle-bracket key notation through real tmux."""
    tokens = re.findall(r"<(?:[A-Za-z]-)?[A-Za-z0-9]+>|.", spec)
    literal = []
    special = {"<Esc>": "Escape", "<CR>": "Enter", "<NL>": "Enter",
               "<Tab>": "Tab", "<BS>": "BSpace"}
    def flush():
        if literal:
            # Feed discrete learner-paced key events.  Thirty milliseconds
            # still outran Flash/Hardtime mappings on several transfer cards:
            # the key log contained the recipe but Neovim had not applied the
            # motion or change.  120 ms remains quick while representing
            # actual individual presses instead of a terminal byte burst.
            for char in literal:
                send_text(socket, pane, char)
                time.sleep(0.12)
            literal.clear()
    for token in tokens:
        if token in special or re.fullmatch(r"<C-[A-Za-z]>", token):
            flush()
            tmux(socket, "send-keys", "-t", pane,
                 special.get(token, "C-" + token[3].lower()))
            # Keep an immediately following `:` from being decoded as one
            # Meta-colon token. Real learners naturally release Escape before
            # starting `:wq`; the tmux driver otherwise has no key boundary.
            if token == "<Esc>":
                # Neovim's default terminal-key timeout may be one second.
                # Wait past it so `-w` records a standalone <Esc> instead of
                # folding the next printable byte into <M-x>.
                time.sleep(1.10)
        else:
            literal.append(token)
    flush()


def seed(root, passed, *, artifact_card=None, due_review=False, progress_to=None,
         target_card=None, failed_card=None, failed_attempts=0):
    state = root / "state" / "vim-daily"
    state.mkdir(parents=True)
    rows = []
    s0_ids = next(stage for stage in CUR["stages"] if stage["id"] == "S0")["card_ids"]
    seed_ids = list(s0_ids[:passed])
    target = progress_to or target_card
    if target:
        if target not in CARDS:
            raise AssertionError("unknown progress target %s" % target)
        owner = CARDS[target]["stage_owner"]
        main = CUR["main_stage_sequence"]
        # P becomes eligible after S5, but the scheduler continues to prefer
        # unfinished main-path stages.  A targeted P-route fixture therefore
        # has to finish the competing main path as well; seeding only through
        # S5 opens M5.01 (S6) instead of the requested optional card.
        stage_ids = ([*main[:main.index(owner)], owner] if owner in main else
                     [*main, "P"])
        seed_ids = []
        for stage_id in stage_ids:
            stage = next(row for row in CUR["stages"] if row["id"] == stage_id)
            for candidate in stage["card_ids"]:
                if candidate == target:
                    break
                seed_ids.append(candidate)
            if stage_id == owner:
                break
    for card_id in seed_ids:
        module_id = card_id.split(".", 1)[0]
        rows.append({
            "type": "card", "result": "pass", "card_id": card_id, "module_id": module_id,
            "at": "2026-09-20T12:00:00-04:00",
            "next_due": ("2026-09-20T13:00:00-04:00" if due_review and card_id == "M0.01"
                         else "2099-01-01T00:00:00-05:00"),
        })
    # Progress-targeted route fixtures must satisfy the same stage mastery
    # contract as a real learner. Card-pass rows alone leave a completed stage
    # review_pending, which locks its successor and produces no popup.
    seeded = set(seed_ids)
    card_map = {card["id"]: card for card in CUR["cards"]}
    for stage in CUR["stages"]:
        if not set(stage["card_ids"]).issubset(seeded):
            continue
        for review_key in stage.get("required_review_card_ids", []):
            question_ids = card_map[review_key].get("question_ids", [])
            rows.append({
                "type": "review", "result": "pass", "review_key": review_key,
                "review_stage": 1, "card_id": review_key,
                "module_id": card_map[review_key]["module_id"],
                "question_id": question_ids[0] if question_ids else None,
                "at": "2026-09-20T12:15:00-04:00",
                "next_due": "2099-01-01T00:00:00-05:00",
            })
    for _ in range(failed_attempts):
        rows.append({
            "type": "card", "result": "fail", "card_id": failed_card,
            "module_id": failed_card.split(".", 1)[0], "reason": "concept-answer",
            "at": "2026-09-20T12:30:00-04:00",
        })
    if rows:
        (state / "events-v2.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    if artifact_card:
        card = CARDS[artifact_card]
        project = state / "projects" / card["project_id"]
        project.mkdir(parents=True)
        (project / "strip.txt").write_text("\n".join(card["start"]) + "\n", encoding="utf-8")


def answer_for(question_id, order=(0, 1, 2, 3)):
    question = QUESTIONS[question_id]
    if question.get("choices"):
        return "abcd"[list(order).index(question["correct_choice"])]
    return question["answer_contract"]["sample_answer"]


def exercise(name, *, passed, route, card_id=None, artifact_card=None, due_review=False,
             progress_to=None, choice_order=None, failed_attempts=0,
             key_sequence=None):
    with tempfile.TemporaryDirectory(prefix="vim-daily-routes-") as tmp:
        root = Path(tmp)
        data = root / "data"
        data.mkdir()
        (data / "vim-daily").symlink_to(ROOT / "share", target_is_directory=True)
        seed(root, passed, artifact_card=artifact_card, due_review=due_review,
             progress_to=progress_to,
             target_card=None if route == "review" else card_id,
             failed_card=card_id, failed_attempts=failed_attempts)

        token = uuid.uuid4().hex[:10]
        inner = "vdr-inner-" + token
        outer = "vdr-outer-" + token
        ready = "vdr-ready-" + token
        question = "vdr-question-" + token
        feedback = "vdr-feedback-" + token
        post = "vdr-post-" + token
        done = "vdr-done-" + token
        env = {
            # VD-12: real data dir so the learner's LazyVim plugins load.
            "XDG_DATA_HOME": os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share")), "XDG_STATE_HOME": str(root / "state"),
            "EDITOR": "nvim", "TERM": "xterm-256color",
            "VIM_DAILY_TMUX_READY_SIGNAL": ready,
            "VIM_DAILY_TMUX_QUESTION_SIGNAL": question,
            "VIM_DAILY_TMUX_FEEDBACK_SIGNAL": feedback,
            "VIM_DAILY_TMUX_POST_SIGNAL": post,
            "VIM_DAILY_TMUX_FINISHED_SIGNAL": done,
        }
        if choice_order:
            env["VIM_DAILY_TEST_CHOICE_ORDER"] = "".join(str(value) for value in choice_order)
        else:
            env["VIM_DAILY_TEST_ORDERED_CHOICES"] = "1"
        try:
            run("tmux", "-L", inner, "-f", "/dev/null", "new-session", "-d",
                "-s", "lesson", "-x", str(COLUMNS), "-y", str(ROWS),
                "/bin/zsh", "-f")
            for key, value in env.items():
                tmux(inner, "set-environment", "-g", key, value)
            tmux(inner, "set-hook", "-g", "client-attached", "run-shell -b %s" % HOOK)
            for signal in (ready, question, feedback, post, done):
                tmux(inner, "wait-for", "-L", signal)
            command = "env -u TMUX tmux -L %s attach-session -t lesson" % inner
            run("tmux", "-L", outer, "-f", "/dev/null", "new-session", "-d",
                "-s", "terminal", "-x", str(COLUMNS), "-y", str(ROWS), command)
            pane = tmux(outer, "list-panes", "-t", "terminal", "-F", "#{pane_id}",
                        capture_output=True).stdout.strip()

            route_card = CARDS.get(card_id)
            if route == "transfer" and route_card and route_card.get("variants"):
                route_card = dict(route_card)
                route_card.update(route_card["variants"][
                    failed_attempts % len(route_card["variants"])])

            if route not in ("concept", "review"):
                card = route_card
                before_qids = [
                    qid for qid in card.get("paired_question_ids", [])
                    if QUESTIONS[qid].get("placement") in ("before", "both")
                ]
                for qid in before_qids:
                    wait_signal(inner, question)
                    paired_prompt = " ".join(capture(outer, pane).split())
                    assert "ANIMATION" in paired_prompt and "NEOVIM" in paired_prompt
                    send_text(outer, pane, answer_for(qid))
                    tmux(outer, "send-keys", "-t", pane, "Enter")

            if route in ("concept", "check", "review"):
                wait_signal(inner, question)
                prompt_raw = capture(outer, pane)
                prompt = " ".join(prompt_raw.split())
                # Authored questions no longer use one generated "DO THIS" /
                # "choose both halves" stem. Assert the learner-visible
                # contract instead: paired domains, four answer choices, and
                # the actual answer prompt.
                assert "answer (a-d)" in prompt, prompt
                assert "ANIMATION" in prompt and "NEOVIM" in prompt, prompt
                assert all("%s)" % letter in prompt for letter in "abcd"), prompt

                def assert_compact_choices_fit(screen):
                    if ROWS >= 38:
                        return
                    choice_lines = [line for line in screen.splitlines()
                                    if re.search(r"\s[abcd]\)\s+ANIM:", line)]
                    vim_lines = [line for line in screen.splitlines()
                                 if "VIM:" in line]
                    assert len(choice_lines) >= 4, screen
                    assert len(vim_lines) >= 4, screen

                assert_compact_choices_fit(prompt_raw)

            if route == "concept":
                question_id = CARDS[card_id]["question_ids"][
                    failed_attempts % len(CARDS[card_id]["question_ids"])]
                authored_prompt = (
                    QUESTIONS[question_id].get(
                        "compact_prompt", QUESTIONS[question_id]["prompt"])
                    if ROWS < 38 else QUESTIONS[question_id]["prompt"]
                )
                stem = next(
                    line.strip() for line in authored_prompt.splitlines()
                    if line.strip() not in ("ANIMATION", "NEOVIM")
                )
                assert stem[:24] in prompt, prompt
                if choice_order:
                    assert all("%s)" % letter in prompt for letter in "abcd")
                send_text(outer, pane, answer_for(question_id,
                                                  choice_order or (0, 1, 2, 3)))
                tmux(outer, "send-keys", "-t", pane, "Enter")
            elif route == "review":
                review_question = QUESTIONS["M0.01.P01"]
                review_authored = (
                    review_question.get("compact_prompt", review_question["prompt"])
                    if ROWS < 38 else review_question["prompt"]
                )
                review_stem = next(
                    line.strip() for line in review_authored.splitlines()
                    if line.strip() not in ("ANIMATION", "NEOVIM")
                )
                assert review_stem[:24] in prompt, prompt
                send_text(outer, pane, answer_for("M0.01.P01"))
                tmux(outer, "send-keys", "-t", pane, "Enter")
                wait_signal(inner, ready)
                review_brief = " ".join(capture(outer, pane).split())
                assert "DO THIS" in review_brief and "Spaced edit retrieval" in review_brief
                # The due row belongs to M0.01. Review art must come from that
                # exact source card's bank; borrowing M0.06 would recreate the
                # module-transfer fallback that the runtime now rejects.
                review_variant = CARDS["M0.01"]["review_variants"][0]
                send_spec(outer, pane, review_variant["expected"] + "ZZ")
            elif route == "check":
                check_qids = card["question_ids"][:5]
                for number, check_qid in enumerate(check_qids, start=1):
                    send_text(outer, pane, answer_for(check_qid))
                    tmux(outer, "send-keys", "-t", pane, "Enter")
                    if number < len(check_qids):
                        wait_signal(inner, question)
                        assert_compact_choices_fit(capture(outer, pane))
                try:
                    wait_signal(inner, ready)
                except AssertionError as exc:
                    raise AssertionError("module check never opened editor:\n" +
                                         capture(outer, pane)) from exc
                brief = " ".join(capture(outer, pane).split())
                assert card_id in brief and "exact command keys" in brief
                assert "TARGET" in brief and "HINT" in brief
                assert card["expected"] not in brief
                send_spec(outer, pane, card["expected"] + "ZZ")
            else:
                try:
                    wait_signal(inner, ready)
                except AssertionError as exc:
                    raise AssertionError(
                        "popup did not reach editor-ready state:\n" + capture(outer, pane)
                    ) from exc
                brief_raw = capture(outer, pane)
                brief = " ".join(brief_raw.split())
                # At 80 columns a long recipe may wrap at a word boundary.
                # Remove the popup's left/right border before flattening so
                # the border glyphs do not become fake text inside a key
                # sequence such as ``:set colorcolumn=11<CR>``.
                brief_content = " ".join(
                    line.strip().strip("│").strip()
                    for line in brief_raw.splitlines()
                )
                brief_compact = "".join(brief_content.split())
                card = route_card
                assert card_id in brief and card["prompt"][:30] in brief, brief
                assert "TARGET" in brief, brief
                visible_target_rows = card["target"] if ROWS >= 28 else card["target"][:6]
                for target_row in visible_target_rows:
                    assert "│" + target_row in brief_raw, brief_raw
                if card.get("show_recipe", card.get("show_target", False)):
                    assert "TARGET" in brief and "RECIPE" in brief, brief
                    assert all("".join(keys.strip().split()) in brief_compact
                               for keys, _why in card["recipe"]), brief
                else:
                    assert "HINT" in brief and "hidden" in brief, brief
                    assert card["expected"] not in brief
                    for method in card.get("method_alternatives", []):
                        assert method["keys"] not in brief
                if route == "compare":
                    assert any(marker in brief.lower() for marker in (
                        "compare after pass", "comparison appears after verification"
                    )), brief
                route_keys = key_sequence
                send_spec(outer, pane, route_keys or card["expected"] + "ZZ")

            if route not in ("concept", "review"):
                after_qids = [
                    qid for qid in route_card.get("paired_question_ids", [])
                    if QUESTIONS[qid].get("placement") in ("after", "both")
                ]
                for qid in after_qids:
                    try:
                        wait_signal(inner, question)
                    except AssertionError as exc:
                        raise AssertionError(
                            "popup did not open after-question %s:\n%s" %
                            (qid, capture(outer, pane))
                        ) from exc
                    post_prompt = " ".join(capture(outer, pane).split())
                    assert "ANIMATION" in post_prompt and "NEOVIM" in post_prompt
                    send_text(outer, pane, answer_for(qid))
                    tmux(outer, "send-keys", "-t", pane, "Enter")

            wait_signal(inner, feedback)
            feedback_screen = " ".join(capture(outer, pane).split())
            if route == "review":
                assert "REVIEW RETRIEVED" in feedback_screen and "ANSWER EXPLANATION" in feedback_screen, feedback_screen
                assert "EDIT RESULT" in feedback_screen and "exact target" in feedback_screen
            else:
                assert ("LESSON COMPLETE" in feedback_screen
                        or ("verified outcome" in feedback_screen
                            and "exact target" in feedback_screen)
                        or "RESULT COMPARISON exact target" in feedback_screen), feedback_screen
                if ROWS < 28:
                    assert "LESSON COMPLETE" in feedback_screen, feedback_screen
            if route == "concept":
                assert "ANSWER EXPLANATION" in feedback_screen
                assert "QUESTION REPLAY" not in feedback_screen
                assert "CONCEPT REPLAY" not in feedback_screen
                assert "retain the principle" not in feedback_screen
            if route == "compare":
                assert all(method["label"] in feedback_screen
                           for method in CARDS[card_id]["method_alternatives"]), feedback_screen
                assert CARDS[card_id]["expected"] in feedback_screen, feedback_screen
                submitted_method = (key_sequence[:-2]
                                    if key_sequence and key_sequence.endswith("ZZ")
                                    else CARDS[card_id]["expected"])
                expected_family = next(
                    method["label"] for method in CARDS[card_id]["method_alternatives"]
                    if method["keys"] == submitted_method)
                assert "METHOD CHECK" in feedback_screen and expected_family in feedback_screen
            if route == "check":
                assert "CHECK ANSWERS" in feedback_screen and "5/5" in feedback_screen
                assert "all 5 choices correct" in feedback_screen
                assert "PLAYBACK VERIFIED" in feedback_screen

            tmux(outer, "send-keys", "-t", pane, "Enter")
            wait_signal(inner, post)
            progress = " ".join(capture(outer, pane).split())
            assert "SKILL TREE / MODULE PROGRESS" in progress, progress
            assert "CURRENT MODULE MAP" in progress and "LEVEL" in progress and "streak:" in progress
            held_before = capture(outer, pane)
            time.sleep(0.15)
            held_after = capture(outer, pane)
            if "SKILL TREE / MODULE PROGRESS" not in held_before or \
                    "SKILL TREE / MODULE PROGRESS" not in held_after:
                raise AssertionError("progress page did not remain held before close")
            tmux(outer, "send-keys", "-t", pane, "Enter")
            wait_signal(inner, done)
            time.sleep(0.15)
            if "SKILL TREE / MODULE PROGRESS" in capture(outer, pane):
                raise AssertionError("popup remained visible after explicit close")
            event_path = root / "state" / "vim-daily" / "events-v2.jsonl"
            events = [json.loads(line) for line in event_path.read_text(
                encoding="utf-8").splitlines()]
            if route == "compare":
                passed_event = next(row for row in reversed(events)
                                    if row.get("card_id") == card_id and row.get("result") == "pass")
                assert passed_event.get("method_family") == expected_family, passed_event
                keylog = Path(passed_event.get("keylog", ""))
                assert re.fullmatch(
                    r"keys-%s-attempt-\d{4}\.log" % re.escape(card_id),
                    keylog.name,
                ), passed_event
                assert keylog.is_file(), passed_event
                assert len(passed_event.get("keylog_sha256", "")) == 64, passed_event
            if route in ("concept", "review", "check"):
                evidence_type = "review" if route == "review" else "question"
                question_event = next(row for row in reversed(events)
                                      if row.get("type") == evidence_type)
                evidence = question_event.get("question_evidence", {})
                assert question_event.get("curriculum_revision") == CUR["revision"]
                assert len(evidence.get("question_prompt_sha256", "")) == 64
                assert evidence.get("displayed_choice_indices")
                if route == "concept" and choice_order:
                    assert evidence["displayed_choice_indices"] == list(choice_order)
                    semantic = QUESTIONS[question_id]["correct_choice"]
                    expected_letter = "abcd"[list(choice_order).index(semantic)]
                    assert evidence.get("raw_answer") == expected_letter
                assert evidence.get("raw_answer") in "abcd"
                assert isinstance(evidence.get("semantic_choice"), int)
            if route == "transfer":
                project = root / "state" / "vim-daily" / "projects" / CARDS[card_id]["project_id"]
                assert (project / "transfer-manifest.json").exists()
                assert not (project / "manifest.json").exists()
            print("PASS headed popup route: %s (%dx%d)" % (name, COLUMNS, ROWS))
        finally:
            for socket in (outer, inner):
                subprocess.run(["tmux", "-L", socket, "kill-server"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # VD-31: reap `nvim --embed` servers orphaned by kill-server.
            subprocess.run(["pkill", "-9", "-f", tmp], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)


if GATE.resolve() != ROOT / "bin" / "vim-daily-gate":
    raise AssertionError("installed gate does not resolve to this checkout")

only_card = next((arg.split("=", 1)[1] for arg in sys.argv
                  if arg.startswith("--only-card=")), None)
if only_card:
    if only_card not in CARDS:
        raise AssertionError("unknown card: " + only_card)
    only = CARDS[only_card]
    route_by_kind = {
        "guided_edit": "guided",
        "independent_edit": "independent",
        "compare_methods": "compare",
        "concept": "concept",
        "module_check": "check",
        "transfer": "transfer",
    }
    route = route_by_kind.get(only["kind"])
    if route is None:
        raise AssertionError("unsupported card kind: %s" % only["kind"])
    override_keys = os.environ.get("VIM_DAILY_TEST_KEYS")
    exercise("%s direct card" % only_card, passed=0, route=route,
             card_id=only_card,
             artifact_card=(only_card if only.get("expected") else None),
             progress_to=only_card,
             key_sequence=(override_keys + "ZZ") if override_keys else None)
    raise SystemExit(0)

only_transfer = next((arg.split("=", 1)[1] for arg in sys.argv
                      if arg.startswith("--only-transfer=")), None)
if only_transfer:
    if only_transfer not in CARDS or CARDS[only_transfer].get("kind") != "transfer":
        raise AssertionError("unknown transfer card: " + only_transfer)
    override_keys = os.environ.get("VIM_DAILY_TEST_KEYS")
    exercise("%s live transfer" % only_transfer, passed=0, route="transfer",
             card_id=only_transfer, artifact_card=only_transfer,
             progress_to=only_transfer,
             key_sequence=(override_keys + "ZZ") if override_keys else None)
    raise SystemExit(0)

only_transfer_alt = next((arg.split("=", 1)[1] for arg in sys.argv
                          if arg.startswith("--only-transfer-alt=")), None)
if only_transfer_alt:
    if (only_transfer_alt not in CARDS
            or CARDS[only_transfer_alt].get("kind") != "transfer"):
        raise AssertionError("unknown transfer card: " + only_transfer_alt)
    variants = CARDS[only_transfer_alt]["variants"]
    if len(variants) < 2 or not variants[1].get("paired_question_ids"):
        raise AssertionError("transfer has no question-bound alternate variant: " + only_transfer_alt)
    exercise("%s alternate live transfer" % only_transfer_alt, passed=0,
             route="transfer", card_id=only_transfer_alt,
             artifact_card=only_transfer_alt, progress_to=only_transfer_alt,
             failed_attempts=1, key_sequence=variants[1]["expected"] + "ZZ")
    raise SystemExit(0)

if "--only-m005" in sys.argv:
    # Reproduce the operator's valid-but-non-pristine interaction: look around,
    # correct a typo inside the addressed copy, then save and quit separately.
    # The exact target plus the semantic :{range}t{destination} command must pass.
    exercise("M0.05 corrected method evidence", passed=passed_before("M0.05"), route="compare",
             card_id="M0.05", artifact_card="M0.05",
             key_sequence="jj:7,9t$<CR>:ew<BS><BS>wq<CR>")
    raise SystemExit(0)

if "--only-m0-prereqs" in sys.argv:
    exercise("M0 linewise yank/put prerequisite", passed=passed_before("M0.YP"),
             route="guided", card_id="M0.YP")
    exercise("M0 one-row open-line prerequisite", passed=passed_before("M0.O"),
             route="guided", card_id="M0.O")
    exercise("M0 addressed substitute prerequisite", passed=passed_before("M0.SR"),
             route="guided", card_id="M0.SR")
    raise SystemExit(0)

if "--only-m0yp" in sys.argv:
    exercise("M0 linewise yank/put prerequisite", passed=passed_before("M0.YP"),
             route="guided", card_id="M0.YP")
    raise SystemExit(0)

if "--only-m0o" in sys.argv:
    exercise("M0 one-row open-line prerequisite", passed=passed_before("M0.O"),
             route="guided", card_id="M0.O")
    raise SystemExit(0)

if "--only-m0sr" in sys.argv:
    exercise("M0 addressed substitute prerequisite", passed=passed_before("M0.SR"),
             route="guided", card_id="M0.SR")
    raise SystemExit(0)

if "--only-check" in sys.argv:
    exercise("five-question module check", passed=passed_before("M0.08"), route="check", card_id="M0.08",
             artifact_card="M0.08")
    raise SystemExit(0)

if "--only-primer" in sys.argv:
    exercise("grammar primer", passed=0, route="concept", card_id="M0.P0")
    raise SystemExit(0)

exercise("grammar primer", passed=0, route="concept", card_id="M0.P0")
exercise("conceptual check", passed=passed_before("M0.03"), route="concept", card_id="M0.03",
         choice_order=(2, 3, 0, 1))
exercise("conceptual changed-stem retry", passed=passed_before("M0.03"), route="concept", card_id="M0.03",
         failed_attempts=1, choice_order=(2, 3, 0, 1))
exercise("guided full task and target", passed=passed_before("M0.01"), route="guided", card_id="M0.01")
exercise("independent retrieval", passed=passed_before("M0.04"), route="independent", card_id="M0.04",
         artifact_card="M0.04")
exercise("two executable methods", passed=passed_before("M0.05"), route="compare", card_id="M0.05",
         artifact_card="M0.05")
exercise("five-question module check", passed=passed_before("M0.08"), route="check", card_id="M0.08",
         artifact_card="M0.08")
exercise("spaced review", passed=4, route="review", due_review=True)

# Every module's distinct transfer artifact is exercised in the live popup,
# rather than inferring UI safety from generated JSON alone.
for module_number in range(len(CUR["modules"])):
    card_id = "M%d.06" % module_number
    exercise("%s live transfer" % card_id, passed=0, route="transfer",
             card_id=card_id, artifact_card=card_id, progress_to=card_id)
