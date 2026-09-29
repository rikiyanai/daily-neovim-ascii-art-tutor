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
            send_text(socket, pane, "".join(literal))
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
         failed_card=None, failed_attempts=0):
    state = root / "state" / "vim-daily"
    state.mkdir(parents=True)
    rows = []
    m0_ids = next(module for module in CUR["modules"] if module["id"] == "M0")["card_ids"]
    seed_ids = list(m0_ids[:passed])
    if progress_to:
        seed_ids = []
        found = False
        for module in CUR["modules"]:
            for candidate in module["card_ids"]:
                if candidate == progress_to:
                    found = True
                    break
                seed_ids.append(candidate)
            if found:
                break
        if not found:
            raise AssertionError("unknown progress target %s" % progress_to)
    for card_id in seed_ids:
        module_id = card_id.split(".", 1)[0]
        rows.append({
            "type": "card", "result": "pass", "card_id": card_id, "module_id": module_id,
            "at": "2026-09-20T12:00:00-04:00",
            "next_due": ("2026-09-20T13:00:00-04:00" if due_review and card_id == "M0.01"
                         else "2099-01-01T00:00:00-05:00"),
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
             progress_to=progress_to, failed_card=card_id, failed_attempts=failed_attempts)

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

            if route not in ("concept", "review"):
                card = CARDS[card_id]
                for qid in card.get("question_placement", {}).get("before", []):
                    wait_signal(inner, question)
                    paired_prompt = " ".join(capture(outer, pane).split())
                    assert "ANIMATION" in paired_prompt and "NEOVIM" in paired_prompt
                    send_text(outer, pane, answer_for(qid))
                    tmux(outer, "send-keys", "-t", pane, "Enter")

            if route in ("concept", "check", "review"):
                wait_signal(inner, question)
                prompt_raw = capture(outer, pane)
                prompt = " ".join(prompt_raw.split())
                assert "DO THIS" in prompt and "answer (a-d)" in prompt, prompt
                assert "ANIMATION" in prompt and "NEOVIM" in prompt and "both" in prompt.lower(), prompt

                def assert_compact_choices_fit(screen):
                    if ROWS >= 38:
                        return
                    choice_lines = [line for line in screen.splitlines()
                                    if re.search(r"\s[abcd]\)\s", line)]
                    assert len(choice_lines) >= 4, screen
                    assert all("· V:" in line for line in choice_lines[-4:]), screen

                assert_compact_choices_fit(prompt_raw)

            if route == "concept":
                question_id = CARDS[card_id]["question_ids"][
                    failed_attempts % len(CARDS[card_id]["question_ids"])]
                assert card_id in prompt, prompt
                if card_id == "M0.P0":
                    assert "TEACH FIRST" in prompt and "4j" in prompt and "5j" in prompt, prompt
                    assert all(token not in prompt for token in ("3daw", "rO", ":8s/")), prompt
                else:
                    assert "complete" in prompt.lower(), prompt
                if question_id.endswith("Q07"):
                    assert "FRAME 1" in prompt and "FRAME 5" in prompt, prompt
                if choice_order:
                    assert all("%s)" % letter in prompt for letter in "abcd")
                send_text(outer, pane, answer_for(question_id,
                                                  choice_order or (0, 1, 2, 3)))
                tmux(outer, "send-keys", "-t", pane, "Enter")
            elif route == "review":
                assert "Spaced review" in prompt
                send_text(outer, pane, answer_for("M0.Q01"))
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
                for number in range(1, 6):
                    send_text(outer, pane, answer_for("M0.Q%02d" % number))
                    tmux(outer, "send-keys", "-t", pane, "Enter")
                    if number < 5:
                        wait_signal(inner, question)
                        assert_compact_choices_fit(capture(outer, pane))
                try:
                    wait_signal(inner, ready)
                except AssertionError as exc:
                    raise AssertionError("module check never opened editor:\n" +
                                         capture(outer, pane)) from exc
                brief = " ".join(capture(outer, pane).split())
                assert "M0.08" in brief and "exact command keys" in brief
                assert "TARGET" in brief and "HINT" in brief
                assert CARDS["M0.08"]["expected"] not in brief
                send_spec(outer, pane, CARDS["M0.08"]["expected"] + "ZZ")
            else:
                wait_signal(inner, ready)
                brief_raw = capture(outer, pane)
                brief = " ".join(brief_raw.split())
                card = CARDS[card_id]
                assert card_id in brief and card["prompt"][:30] in brief, brief
                assert "TARGET" in brief, brief
                visible_target_rows = card["target"] if ROWS >= 28 else card["target"][:6]
                for target_row in visible_target_rows:
                    assert "│" + target_row in brief_raw, brief_raw
                if card.get("show_recipe", card.get("show_target", False)):
                    assert "TARGET" in brief and "RECIPE" in brief, brief
                    assert all(keys.strip() in brief for keys, _why in card["recipe"]), brief
                else:
                    assert "HINT" in brief and "hidden" in brief, brief
                    assert card["expected"] not in brief
                    for method in card.get("method_alternatives", []):
                        assert method["keys"] not in brief
                if route == "compare":
                    assert "comparison appears after verification" in brief.lower(), brief
                send_spec(outer, pane, key_sequence or card["expected"] + "ZZ")

            if route not in ("concept", "review"):
                for qid in CARDS[card_id].get("question_placement", {}).get("after", []):
                    wait_signal(inner, question)
                    post_prompt = " ".join(capture(outer, pane).split())
                    assert "ANIMATION" in post_prompt and "NEOVIM" in post_prompt
                    send_text(outer, pane, answer_for(qid))
                    tmux(outer, "send-keys", "-t", pane, "Enter")

            wait_signal(inner, feedback)
            feedback_screen = " ".join(capture(outer, pane).split())
            if route == "review":
                assert "REVIEW RETRIEVED" in feedback_screen and "CONCEPT REPLAY" in feedback_screen
                assert "EDIT REPLAY" in feedback_screen and "exact target" in feedback_screen
            else:
                assert "LESSON COMPLETE" in feedback_screen, feedback_screen
            if route == "concept":
                assert "CONCEPT REPLAY" in feedback_screen
            if route == "compare":
                assert all(method["label"] in feedback_screen
                           for method in CARDS[card_id]["method_alternatives"]), feedback_screen
                assert CARDS[card_id]["expected"] in feedback_screen, feedback_screen
                expected_family = next(method["label"] for method in CARDS[card_id]["method_alternatives"]
                                       if method["keys"] == CARDS[card_id]["expected"])
                assert "METHOD EVIDENCE" in feedback_screen and expected_family in feedback_screen
            if route == "check":
                assert "MODULE CHECK REPLAY" in feedback_screen and "5/5" in feedback_screen
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
                expected_family = next(method["label"] for method in CARDS[card_id]["method_alternatives"]
                                       if method["keys"] == CARDS[card_id]["expected"])
                assert passed_event.get("method_family") == expected_family, passed_event
                keylog = Path(passed_event.get("keylog", ""))
                assert re.fullmatch(r"keys-M0\.05-attempt-\d{4}\.log", keylog.name), passed_event
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
