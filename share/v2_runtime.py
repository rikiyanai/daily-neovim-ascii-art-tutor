"""Runtime for the project-based v2 curriculum (VD-09).

No third-party packages. Progress is a projection of events-v2.jsonl; deleting
the projection cannot erase learning history. The legacy runner imports this
module and passes its editor/keylog helpers in through RuntimeConfig.
"""

from __future__ import annotations

import datetime as dt
import contextlib
import fcntl
import hashlib
import io
import json
import os
import random
import secrets
import re
import shutil
import socket
import subprocess
import tempfile
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RuntimeConfig:
    state: str
    share: str
    editor: str
    max_tries: int
    target: int
    cooldown: int
    stamp: str
    run_editor: object
    decode_keylog: object
    hold_open: object
    colours: tuple[str, str, str, str, str, str]
    keystroke_table: object | None = None
    tokenize: object | None = None
    feedback_rendered: object | None = None
    post_page_break: object | None = None
    post_rendered: object | None = None
    question_rendered: object | None = None
    question_answer: object | None = None
    practice: bool = False
    native_preview_factory: object | None = None
    curriculum_revision: str | None = None
    curriculum_contract_sha256: str | None = None


# The launcher reads this after a held result so `r` can repeat the exact
# lesson route rather than accidentally selecting the next card.
LAST_RUN_CARD_ID = None
LAST_RUN_KIND = None
LAST_FEEDBACK_CONTEXT = None
LAST_FEEDBACK_DETAILS = []

_UI_STYLE = None
_DASHBOARD_THEME = None
_LESSON_TUI = None
_RETRO_MODULE_REWARDS = None
_METHOD_POLICY = None

# A Textual result screen returns its held action to the launcher.  The
# existing launcher still owns repeat/next state, so this is a small bridge,
# not a second grading or progress authority.
TEXTUAL_ROUTE = None


def _sibling_module(name):
    """The installed gate need not put share/ on sys.path."""
    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location("vim_daily_" + name,
                                                  Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    # Dataclasses and other reflection resolve annotations through the import
    # registry, including modules loaded from the installed sibling directory.
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(spec.name, None)
        raise
    return module


def _ui_style():
    global _UI_STYLE
    if _UI_STYLE is None:
        _UI_STYLE = _sibling_module("ui_style")
    return _UI_STYLE


def _dashboard_theme():
    global _DASHBOARD_THEME
    if _DASHBOARD_THEME is None:
        _DASHBOARD_THEME = _sibling_module("dashboard_theme")
    return _DASHBOARD_THEME


def _lesson_tui():
    """Load the optional lesson/result surface beside this runtime."""
    global _LESSON_TUI
    if _LESSON_TUI is None:
        _LESSON_TUI = _sibling_module("lesson_tui")
    return _LESSON_TUI


def _retro_module_rewards():
    """Load the read-only C34 reward selector beside this runtime."""
    global _RETRO_MODULE_REWARDS
    if _RETRO_MODULE_REWARDS is None:
        _RETRO_MODULE_REWARDS = _sibling_module("retro_module_rewards")
    return _RETRO_MODULE_REWARDS


def _textual_enabled():
    try:
        return bool(_lesson_tui().enabled())
    except (ImportError, OSError, SyntaxError):
        return False


class _TtyCapture(io.StringIO):
    """Capture a fully expanded result page while retaining TTY colour paths."""

    def isatty(self):
        return True


def _capture_tty(function, *args, **kwargs):
    """Capture output for Textual without invoking compact/ellipsis paths."""
    output = _TtyCapture()
    old_size = shutil.get_terminal_size
    # The Textual body is scrollable.  Give the existing prose renderer enough
    # rows to emit every sentence, while preserving its real terminal-width
    # wrapping and ANSI role markup for Rich/Textual to consume.
    shutil.get_terminal_size = lambda *_a, **_k: os.terminal_size((120, 1000))
    try:
        with contextlib.redirect_stdout(output):
            function(*args, **kwargs)
    finally:
        shutil.get_terminal_size = old_size
    # Page bodies are rendered inside Textual; a legacy clear-screen control
    # would otherwise become literal content or repaint the host surface.
    return output.getvalue().replace("\033[2J\033[H", "")


def _show_lesson_screen(cfg, card, lesson):
    """Paint the lesson brief, then return whether the editor may open."""
    global TEXTUAL_ROUTE
    if not _textual_enabled():
        return True
    try:
        body = Path(lesson).read_text(encoding="utf-8")
        route = _lesson_tui().show(
            _lesson_tui().lesson_pages(body, card=card), result=False)
    except (OSError, ImportError, SyntaxError):
        return True
    # Enter is the only action that proceeds to the actual Neovim editor.
    # Closing a lesson screen is a learner cancellation, never a credit path.
    if route != "edit":
        TEXTUAL_ROUTE = "close"
    return route == "edit"


def _show_concept_screen(cfg, cur, progress, card, context):
    """Paint a concept lesson before its authored question."""
    global TEXTUAL_ROUTE
    if not _textual_enabled():
        return True
    lines = ["%s — %s" % (card["id"], card["title"]),
             _progress_line(cfg, progress, card),
             "WHY: %s" % context["why"][1],
             "BUYS: %s" % context["buys"],
             "SOURCE: %s" % context["source"]]
    if card.get("teaching_lines"):
        lines += ["", "TEACH FIRST"]
        lines += ["  " + str(line) for line in card["teaching_lines"]]
    lines += ["", "DO THIS: %s" % card["prompt"],
              "CHECK YOUR UNDERSTANDING: both the animation reading and Neovim decision must be correct."]
    try:
        route = _lesson_tui().show(
            _lesson_tui().lesson_pages("\n".join(lines), card=card), result=False)
    except (ImportError, OSError, SyntaxError):
        return True
    if route != "edit":
        TEXTUAL_ROUTE = "close"
    return route == "edit"


def _module_reward_view(motion, *, module_id=None, status=None):
    """Build a production viewer View from canonical complete-frame motion."""
    V = _viewer_module()
    frames = [list(frame) for frame in motion.get("frames", ())]
    if len(frames) < 8:
        raise ValueError("module reward playback requires at least eight frames")
    title = motion.get("title", "complete module animation")
    if module_id:
        label = ("prior study · preview only" if status == "prior_study"
                 else "mastered endcap" if status == "mastered" else "complete reward")
        title = "RETROSPECTIVE MODULE REWARD · %s · %s · %d frames · not learner output" % (
            module_id, label, len(frames))
    labels = ["pose %02d" % (index + 1) for index in range(len(frames))]
    holds = {index: "hold" for index in range(1, len(frames))
             if frames[index] == frames[index - 1]}
    return V.View(title, frames, labels=labels, holds=holds, kind="module_reward")


def _show_result_screen(cfg, cur, card, progress, replay, completed):
    """Show feedback + progress tabs and route controls to existing owners."""
    global TEXTUAL_ROUTE
    selected_motion = (_retro_module_rewards().completion_reward(cur, card)
                       if completed else None)
    # Preserve the existing failure surface for an explicitly supplied but
    # malformed native reward: its transport error is visible and never
    # changes grading, rather than being silently skipped by the selector.
    if (completed and selected_motion is None
            and isinstance(card.get("module_reward"), dict)
            and card.get("module_reward")):
        selected_motion = card["module_reward"]
    result_card = card
    if selected_motion and not card.get("module_reward"):
        result_card = dict(card, module_reward=selected_motion)
    if completed and result_card.get("medium") == "proportional-sjis" and result_card.get("module_reward"):
        # Native-font motion is a result reward, not a terminal-cell alignment
        # fallback or a second grading authority. Failure never revokes credit.
        try:
            transport = _native_module("sjis_terminal")
            with transport.temporary_tmux_passthrough():
                receipt = _native_module("module_native_playback").play(result_card["module_reward"])
            if replay and replay.get("keylog"):
                # Bind reward playback to this actual attempt without adding
                # learner credit or changing the already-recorded verdict.
                reward_path = Path(replay["keylog"]).with_suffix(".reward.json")
                record = dict(receipt, schema="vim-daily/native-result-reward@1",
                              card_id=card["id"], curriculum_revision=cur["revision"],
                              keylog_sha256=_hash_file(Path(replay["keylog"])))
                _write_lines_atomic(reward_path, [json.dumps(record, sort_keys=True)])
        except Exception as exc:
            print("Native module reward unavailable: %s. Your grade is unchanged." % exc)
    if not _textual_enabled():
        # The stdlib result surface still uses the real production viewer for
        # fixed-grid module rewards.  This keeps the complete sequence visible
        # when Textual is deliberately disabled in a headed gate run.
        if completed and result_card.get("medium") != "proportional-sjis" and selected_motion:
            viewer = _viewer_module()
            if viewer.enabled():
                viewer.play([_module_reward_view(selected_motion,
                                                 module_id=card.get("module_id"),
                                                 status=("mastered"
                                                         if card.get("kind") in ("module_check", "module_reward")
                                                         else None))])
        return False
    TEXTUAL_ROUTE = None
    feedback = _capture_tty(_post_feedback, cfg, cur, card, replay,
                            completed=completed)
    progress_body = _capture_tty(_post_progress, cfg, cur, card, progress,
                                 completed=completed)
    # C32: an eligible completed lesson reaches moving art on Feedback itself.
    # The source poses are credited rewards, never presented as learner output.
    ui = _lesson_tui()
    reward = ui.result_reward_spec(result_card) if completed else None
    pages = ui.result_pages(feedback, progress_body, reward=reward)

    def mounted():
        # The headed tests use this callback as the actual painted-screen
        # boundary; it runs after Textual has mounted and refreshed the tabs.
        callback = getattr(cfg, "feedback_rendered", None)
        if callback:
            callback()

    while True:
        try:
            route = _lesson_tui().show(pages, result=True, mounted=mounted)
        except (ImportError, OSError, SyntaxError):
            return False
        if route in ("feedback", "f"):
            collect_feedback(input, screen="result")
            continue
        if route in ("dashboard", "d"):
            open_dashboard(cfg, cur, progress)
            continue
        if route in ("watch", "v", "w"):
            replay_last_view()
            continue
        # ``hold_open`` consumes this value and keeps the established launcher
        # state machine responsible for repeat/next and practice credit.
        TEXTUAL_ROUTE = route or "close"
        return True


def _paint(text, role):
    style = _ui_style()
    enabled = __import__("sys").stdout.isatty() and style.colour_enabled()
    return style.ansi(role, enabled=enabled) + str(text) + (style.RESET if enabled else "")


def _wrap_prose(text, width=None, indent="", subsequent=None):
    width = width or max(40, shutil.get_terminal_size((80, 24)).columns - 4)
    return textwrap.wrap(str(text), width=width, initial_indent=indent,
                         subsequent_indent=subsequent if subsequent is not None else indent + "  ",
                         break_long_words=False, break_on_hyphens=False) or [indent]


def _command_spans(text):
    """Commands actually shown in feedback, not guesses about prose words."""
    pattern = r"`([^`]+)`|(:[0-9%,$]*s[^\w\s][^\s`]+)"
    return [(m.start(1) if m.group(1) is not None else m.start(2),
             m.end(1) if m.group(1) is not None else m.end(2))
            for m in re.finditer(pattern, text)]


def _partial_key_colours(text, correct):
    """Only differing key spans are red; matching parts remain green."""
    import difflib
    mine, theirs = _command_spans(text), _command_spans(correct)
    out, cursor = [], 0
    for index, (start, end) in enumerate(mine):
        out.append(text[cursor:start])
        expected = correct[slice(*theirs[min(index, len(theirs) - 1)])] if theirs else ""
        keys = text[start:end]
        for tag, a, b, _c, _d in difflib.SequenceMatcher(None, keys, expected,
                                                        autojunk=False).get_opcodes():
            # Keep matching spans visible and green.  The previous renderer
            # only appended non-equal spans, so a correct command disappeared
            # from the correction comparison and a partial answer could not
            # be read as "right here, wrong there".
            if tag == "equal":
                out.append(_paint(keys[a:b], "ok"))
            elif a != b:
                out.append(_paint(keys[a:b], "fail"))
        cursor = end
    out.append(text[cursor:])
    return "".join(out)


def _concept_shape():
    slots = ((":", "meta"), ("{where}", "warn"), ("s", "ok"), ("/", "meta"),
             ("{find}", "key"), ("/", "meta"), ("{replace}", "ok"),
             ("/", "meta"), ("{flags}", "flags"))
    return "".join(_paint(text, role) for text, role in slots)


# VD-43: the learner can send a message about what is wrong from any
# question prompt or result page (`f`). Rows go to <state>/feedback.jsonl with
# the lesson context so a maintainer can reproduce the exact screen.
FEEDBACK = {"path": None, "context": {}}


def feedback_path(state):
    return Path(state) / "feedback.jsonl"


def note_feedback_context(**fields):
    """Remember what the learner is looking at; None clears a field."""
    for key, value in fields.items():
        if value is None:
            FEEDBACK["context"].pop(key, None)
        else:
            FEEDBACK["context"][key] = value


def _drain_pasted_lines(settle=0.25, limit=200):
    """Return lines that are already waiting on a terminal stdin (a paste)."""
    import select
    import sys as _sys
    lines = []
    try:
        if not _sys.stdin.isatty():
            return lines
        while len(lines) < limit:
            ready, _w, _x = select.select([_sys.stdin], [], [], settle)
            if not ready:
                break
            line = _sys.stdin.readline()
            if not line:
                break
            lines.append(line.rstrip("\n"))
    except (OSError, ValueError):
        pass
    return lines


def collect_feedback(input_fn=input, screen=None):
    """Ask for one feedback message and append it; never counts as an answer."""
    try:
        message = input_fn("  FEEDBACK · what is wrong or confusing here? "
                           "(paste or type; Enter alone cancels)\n  > ")
    except (EOFError, KeyboardInterrupt, StopIteration):
        print()
        return False
    if input_fn is input:
        # A pasted message arrives as several lines at once. Keep reading
        # while more pasted text is already waiting, so the rest is not
        # swallowed by the next prompt as answers or menu choices.
        message = "\n".join([message or "", *_drain_pasted_lines()]).strip()
    message = (message or "").strip()
    if not message:
        print("  feedback cancelled")
        return False
    path = FEEDBACK["path"]
    if path is None:
        print("  feedback could not be saved: no state directory is configured")
        return False
    row = dict(FEEDBACK["context"])
    row.update({"at": _now().isoformat(), "screen": screen or row.get("screen"),
                "message": message})
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print("  %s feedback saved — thank you (%s)" % (_paint("✓", "ok"), path))
    return True


def print_feedback(state, limit=20):
    """`--feedback`: show the most recent learner feedback rows."""
    path = feedback_path(state)
    if not path.exists():
        print("no feedback yet (%s)" % path)
        return
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]
    for row in rows[-limit:]:
        where = " ".join(str(row[key]) for key in ("card_id", "question_id", "screen")
                         if row.get(key))
        print("%s  %s\n    %s" % (row.get("at", "")[:16], where, row.get("message", "")))
    print("%d feedback row(s) in %s" % (len(rows), path))


def load_curriculum(share):
    path = os.environ.get("VIM_DAILY_CURRICULUM_V2",
                          os.path.join(share, "curriculum-v2.json"))
    with open(path, encoding="utf-8") as f:
        cur = json.load(f)
    validate_curriculum(cur)
    return cur


def validate_curriculum(cur):
    def validate_method_rule(owner, rule):
        if (not rule.get("label") or not (
                rule.get("exact_any_of") or rule.get("any_of") or rule.get("all_of"))):
            raise ValueError("%s has an incomplete method requirement" % owner)
        if rule.get("max_tokens") is not None and rule["max_tokens"] < 1:
            raise ValueError("%s has an invalid method key limit" % owner)

    if cur.get("schema") != "vim-daily/curriculum@4":
        raise ValueError("unsupported v2 curriculum schema")
    module_count = len(cur.get("modules", []))
    if module_count < 1 or not cur.get("cards"):
        raise ValueError("v2 curriculum must contain modules and cards")
    declared_cards = sum(len(module.get("card_ids", [])) for module in cur["modules"])
    if len(cur["cards"]) != declared_cards:
        raise ValueError("v2 card inventory does not match module card_ids")
    if not cur.get("questions"):
        raise ValueError("v2 curriculum must contain authored questions")
    cids = [c["id"] for c in cur["cards"]]
    qids = [q["id"] for q in cur["questions"]]
    if len(cids) != len(set(cids)) or len(qids) != len(set(qids)):
        raise ValueError("duplicate v2 ids")
    qset = set(qids)
    main_stages = [*("S%d" % number for number in range(8)),
                   *("A%d" % number for number in range(8))]
    if cur.get("main_stage_sequence") != main_stages:
        raise ValueError("v2 curriculum must gate S0-S7 before A0-A7")
    stage_ids = [stage.get("id") for stage in cur.get("stages", [])]
    if stage_ids != [*main_stages, "P"]:
        raise ValueError("v2 stage inventory must end with optional P")
    stage_map = {stage["id"]: stage for stage in cur["stages"]}
    staged_cards = [cid for stage in cur["stages"] for cid in stage.get("card_ids", [])]
    if len(staged_cards) != len(set(staged_cards)) or set(staged_cards) != set(cids):
        raise ValueError("every v2 card must belong to exactly one stage")
    for index, stage_id in enumerate(main_stages):
        stage = stage_map[stage_id]
        expected = [] if index == 0 else [main_stages[index - 1]]
        if (stage.get("prerequisites") != expected or stage.get("optional") is not False
                or not stage.get("required_review_card_ids")):
            raise ValueError("invalid main-stage gate at %s" % stage_id)
    if (stage_map["P"].get("prerequisites") != ["S5"]
            or stage_map["P"].get("optional") is not True):
        raise ValueError("P must be an optional branch after S5")
    card_index = {card["id"]: card for card in cur["cards"]}
    for stage in cur["stages"]:
        expected_reviews = [
            cid for cid in stage["card_ids"]
            if card_index[cid].get("required_before_mastery")
        ]
        if stage.get("required_review_card_ids") != expected_reviews:
            raise ValueError("stage %s has an invalid spaced-review gate" % stage["id"])
    module_ids = [module["id"] for module in cur["modules"]]
    if len(module_ids) != len(set(module_ids)):
        raise ValueError("duplicate module ids")
    module_set = set(module_ids)
    module_map = {module["id"]: module for module in cur["modules"]}
    seen_modules = set()
    for module in cur["modules"]:
        for field in ("meaning", "principle", "defect", "basic", "scaled", "source_ref"):
            if not module.get(field):
                raise ValueError("module %s is missing teaching field %s" % (module["id"], field))
        if any(p not in seen_modules for p in module.get("prerequisites", [])):
            raise ValueError("invalid or cyclic prerequisite at %s" % module["id"])
        seen_modules.add(module["id"])
    first_guided = {}
    expected_sequence = []
    for card in cur["cards"]:
        if card.get("module_id") not in module_set:
            raise ValueError("card %s refers to an unknown module" % card["id"])
        if any(qid not in qset for qid in card.get("question_ids", [])):
            raise ValueError("dangling question reference at %s" % card["id"])
        if not card.get("lesson_benefit"):
            raise ValueError("card %s is missing its executable lesson benefit" % card["id"])
        for field in ("grammar_families", "grammar_stage", "paired_question_ids",
                      "question_placement", "master_habits", "master_stages",
                      "stage_owner"):
            if not card.get(field):
                raise ValueError("card %s is missing grammar-first field %s" % (
                    card["id"], field))
        if card["stage_owner"] not in stage_map or card["master_stages"] != [card["stage_owner"]]:
            raise ValueError("card %s has mixed or invalid stage ownership" % card["id"])
        if any(qid not in qset for qid in card.get("paired_question_ids", [])):
            raise ValueError("card %s has a dangling paired question" % card["id"])
        if not card.get("paired_question_ids") and not (
                card.get("pairing_exception") or {}).get("reason"):
            raise ValueError("card %s needs a paired question or written exception" % card["id"])
        if card.get("expected") and (not card.get("show_target") or not card.get("hint")):
            raise ValueError("edit card %s must expose its target and action hint" % card["id"])
        if (card.get("expected") and not card.get("show_recipe", False)
                and card["expected"] in card.get("hint", "")):
            raise ValueError("edit card %s leaks its hidden command through the hint" % card["id"])
        if card.get("kind") == "compare_methods":
            methods = card.get("method_alternatives", [])
            if len(methods) != 2 or any(not all(m.get(k) for k in ("label", "keys", "why"))
                                        for m in methods):
                raise ValueError("compare card %s needs two executable methods" % card["id"])
        rule = card.get("method_requirement")
        if rule:
            validate_method_rule("card %s" % card["id"], rule)
        if card.get("kind") == "transfer":
            variants = card.get("variants", [])
            if len(variants) < 2:
                raise ValueError("transfer card %s needs changed-art variants" % card["id"])
            starts = [tuple(variant.get("start", [])) for variant in variants]
            if len(starts) != len(set(starts)) or any(
                    not all(variant.get(field) for field in ("start", "target", "expected", "recipe"))
                    for variant in variants):
                raise ValueError("transfer card %s has invalid/repeated variants" % card["id"])
            for index, variant in enumerate(variants, 1):
                if variant.get("method_requirement"):
                    validate_method_rule(
                        "card %s transfer variant %d" % (card["id"], index),
                        variant["method_requirement"])
        review_variants = card.get("review_variants", [])
        if review_variants:
            starts = [tuple(variant.get("start", [])) for variant in review_variants]
            if len(review_variants) < 2 or len(starts) != len(set(starts)) or any(
                    not all(variant.get(field) for field in
                            ("start", "target", "expected", "recipe"))
                    for variant in review_variants):
                raise ValueError("card %s has invalid/repeated review variants" % card["id"])
            for index, variant in enumerate(review_variants, 1):
                if variant.get("method_requirement"):
                    validate_method_rule(
                        "card %s review variant %d" % (card["id"], index),
                        variant["method_requirement"])
        review_capable = bool(review_variants or card.get("kind") == "transfer")
        if review_capable:
            if (card.get("review_source_card_id") != card["id"]
                    or not card.get("review_method_family")):
                raise ValueError("card %s lacks explicit review source/family linkage" % card["id"])
        elif card.get("review_source_card_id") or card.get("review_method_family"):
            raise ValueError("card %s declares review linkage without changed art" % card["id"])
        if card.get("required_before_mastery"):
            variants = card.get("review_variants") or card.get("variants") or []
            if (card.get("grammar_stage") != "hidden"
                    or card.get("show_recipe") is not False
                    or not card.get("method_requirement")
                    or len(variants) < 2
                    or any(not variant.get("method_requirement") for variant in variants)):
                raise ValueError(
                    "card %s cannot gate mastery without hidden method evidence and two enforced reviews" %
                    card["id"])
        frame_rows = card.get("frame_rows", module_map[card["module_id"]].get("frame_rows"))
        if frame_rows and card.get("target"):
            frames = [card["target"][index:index + frame_rows]
                      for index in range(0, len(card["target"]), frame_rows)]
            actual_pairs = [[index + 1, index + 2]
                            for index in range(len(frames) - 1)
                            if frames[index] == frames[index + 1]]
            declared = card.get("duplicate_frames", [])
            if [row.get("frames") for row in declared] != actual_pairs:
                raise ValueError("card %s has unclassified adjacent duplicates" % card["id"])
            for row in declared:
                if (not row.get("reason") or row.get("role") not in
                        {"hold", "scaffold", "material-normalization", "reviewable-duplicate"}
                        or "playback" not in row):
                    raise ValueError("card %s has invalid duplicate metadata" % card["id"])
                if row["role"] == "hold" and (
                        row["playback"] is not True or row.get("duration_frames", 0) < 2):
                    raise ValueError("card %s has an unbounded hold" % card["id"])
        if card.get("animation"):
            if not all(card["animation"].get(field) for field in ("role", "timing")):
                raise ValueError("card %s has incomplete animation metadata" % card["id"])
            if card["animation"].get("role") == "hold" and not card["animation"].get("hold_reason"):
                raise ValueError("card %s has a hold without a reason" % card["id"])
        if card.get("grammar_stage") == "guided":
            for family in card.get("grammar_families", []):
                first_guided.setdefault(family, card["id"])
        elif card.get("grammar_stage") == "hidden":
            for family in card.get("grammar_families", []):
                prior = first_guided.get(family)
                if not prior:
                    raise ValueError("card %s hides %s before guided performance" % (
                        card["id"], family))
                expected_sequence.append({
                    "hidden_card_id": card["id"], "grammar_family": family,
                    "prior_guided_card_id": prior,
                })
    if cur.get("verified_grammar_sequence") != expected_sequence:
        raise ValueError("verified grammar sequence does not match card order")
    # A family is not covered by an answer-key token alone.  It must return
    # later as a key-hidden card with source-linked changed art, so the spaced
    # review contract proves retrieval rather than mere exposure.
    first_guided = {}
    command_review_rows = []
    for index, card in enumerate(cur["cards"]):
        if card.get("grammar_stage") != "guided" or not card.get("expected"):
            continue
        for family in card.get("grammar_families", []):
            first_guided.setdefault(family, (index, card["id"]))
    for family, (guided_index, guided_id) in first_guided.items():
        review = next((candidate for candidate in cur["cards"][guided_index + 1:]
                       if candidate.get("grammar_stage") == "hidden"
                       and family in candidate.get("grammar_families", [])
                       and (candidate.get("review_variants")
                            or candidate.get("kind") == "transfer")
                       and candidate.get("show_recipe") is False
                       and candidate.get("method_requirement")
                       and candidate.get("required_before_mastery")), None)
        if review is None:
            raise ValueError("%s has no hidden changed-art review for %s" % (guided_id, family))
        variants = review.get("review_variants") or review.get("variants") or []
        command_review_rows.append({
            "grammar_family": family,
            "guided_card_id": guided_id,
            "review_card_id": review["id"],
            "changed_art_variants": len(variants),
            "keys_hidden": True,
            "evidence": "method-required hidden target plus source-linked spaced review",
        })
    if cur.get("verified_command_review_coverage") != command_review_rows:
        raise ValueError("verified command review coverage does not match hidden changed-art retrieval")
    required_review_rows = [{
        "module_id": card["module_id"],
        "source_card_id": card["id"],
        "method_label": card["method_requirement"]["label"],
        "changed_art_variants": len(card.get("variants") or card.get("review_variants") or []),
        "keys_hidden": card.get("show_recipe") is False,
        "required_before_mastery": True,
        "evidence": "method-required hidden transfer plus changed-art spaced review",
    } for card in cur["cards"] if card.get("required_before_mastery")]
    if cur.get("required_mastery_review_coverage") != required_review_rows:
        raise ValueError("required mastery-review coverage does not match enforced cards")
    for module in cur["modules"]:
        expected = [card["id"] for card in cur["cards"]
                    if card["module_id"] == module["id"]
                    and card.get("required_before_mastery")]
        if module.get("required_review_card_ids") != expected:
            raise ValueError("module %s has stale required review ids" % module["id"])

    def contains_ascii_visual(value):
        if "│" in value:
            return True
        for block in value.split("\n\n"):
            rows = []
            for line in block.splitlines():
                punctuation = sum(not char.isalnum() and not char.isspace()
                                  for char in line)
                non_ascii = sum(ord(char) > 127 for char in line)
                if punctuation >= 2 or non_ascii >= 2:
                    rows.append(line)
            if len(rows) >= 2:
                return True
        return False

    for q in cur["questions"]:
        form = q.get("form")
        if form != "multiple_choice":
            raise ValueError(
                "question %s must be four-choice multiple choice, got %r" %
                (q["id"], form))
        for field in ("card_id", "grammar_family", "grammar_breakdown_id",
                      "paired_invariant", "placement", "placement_reason", "answer_contract"):
            if not q.get(field):
                raise ValueError("question %s is missing paired field %s" % (q["id"], field))
        if len(q.get("choices", [])) != 4 or len(q.get("feedback", [])) != 4:
            raise ValueError("choice question %s must have four choices and feedback messages" % q["id"])
        if not 0 <= q.get("correct_choice", -1) < len(q["choices"]):
            raise ValueError("question %s has an invalid correct choice" % q["id"])
        if q.get("module_id") not in module_set:
            raise ValueError("question %s refers to an unknown module" % q["id"])
        if not q.get("source_ref"):
            raise ValueError("question %s has no source reference" % q["id"])
        if "ANIMATION\n" not in q.get("prompt", "") or "NEOVIM\n" not in q.get("prompt", ""):
            raise ValueError("question %s does not display both paired prompts" % q["id"])
        if (not contains_ascii_visual(q.get("prompt", ""))
                or not contains_ascii_visual(q.get("compact_prompt", ""))):
            raise ValueError("question %s does not print art in both layouts" % q["id"])
        if form == "multiple_choice":
            paired_fields = ("animation_prompt", "animation_answer", "neovim_prompt", "neovim_answer")
            if any(not q.get(field) for field in paired_fields):
                raise ValueError("question %s is not paired across animation and Neovim" % q["id"])
            if any("ANIMATION:" not in choice or "NEOVIM:" not in choice
                   for choice in q["choices"]):
                raise ValueError("question %s has a one-sided answer choice" % q["id"])
            if (len(q.get("compact_choices", [])) != len(q["choices"])
                    or any("A:" not in choice or "V:" not in choice
                           for choice in q.get("compact_choices", []))):
                raise ValueError("question %s has an invalid compact paired choice" % q["id"])
            if ("ANIMATION" not in q.get("compact_prompt", "")
                    or "NEOVIM" not in q.get("compact_prompt", "")):
                raise ValueError("question %s has an invalid compact paired prompt" % q["id"])
            if any("Not yet" in message or "one or both halves" in message.lower()
                   for message in q["feedback"]):
                raise ValueError("question %s has generic wrong-answer feedback" % q["id"])
            if len(set(q["choices"])) != 4:
                raise ValueError("question %s repeats an answer choice" % q["id"])
    question_signatures = [
        (" ".join(q["prompt"].split()).casefold(),
         tuple(" ".join(choice.split()).casefold() for choice in q.get("choices", [])))
        for q in cur["questions"]
    ]
    if len(question_signatures) != len(set(question_signatures)):
        raise ValueError("duplicate conceptual question/choice set")
    card_map = {card["id"]: card for card in cur["cards"]}
    for module in cur["modules"]:
        actual_ids = [card["id"] for card in cur["cards"]
                      if card["module_id"] == module["id"]]
        if module.get("card_ids") != actual_ids:
            raise ValueError("module %s card list does not match its cards" % module["id"])
        for card_id in module.get("card_ids", []):
            if card_id not in card_map or card_map[card_id]["module_id"] != module["id"]:
                raise ValueError("module %s has an invalid card reference %s" % (
                    module["id"], card_id))
    review_rows = cur.get("verified_review_coverage", [])
    expected_review_ids = [card["id"] for card in cur["cards"]
                           if card.get("review_source_card_id")]
    if [row.get("source_card_id") for row in review_rows] != expected_review_ids:
        raise ValueError("verified review coverage does not match source-linked review banks")


def _review_variants(card):
    """Return only changed art explicitly linked to this source card."""
    if card.get("review_variants"):
        return card["review_variants"]
    if card.get("kind") == "transfer":
        return card.get("variants", [])
    return []


def _paths(cfg):
    root = Path(cfg.state)
    return {
        "events": root / "events-v2.jsonl",
        "projection": root / "progress-v2.json",
        "projects": root / "projects",
        "sessions": root / "sessions",
        "lock": root / ".v2-session.lock",
    }


def read_events(cfg):
    path = _paths(cfg)["events"]
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError:
                # Preserve the ledger. A corrupt tail is visible in status but
                # cannot destroy prior valid events.
                rows.append({"type": "ledger_error", "line": lineno})
                continue
            rows.append(row)
    return rows


def _bind_curriculum(cfg, cur):
    """Pin the in-memory contract used for this attempt, not the live symlink."""
    cfg.curriculum_revision = cur["revision"]
    cfg.curriculum_contract_sha256 = hashlib.sha256(
        json.dumps(cur, sort_keys=True, ensure_ascii=False,
                   separators=(",", ":")).encode("utf-8")).hexdigest()


def _native_handoff_ack(cur):
    """Acknowledge child lock plus curriculum load to the native selector."""
    socket_path = os.environ.get("VIM_DAILY_NATIVE_ACK_SOCKET")
    nonce = os.environ.get("VIM_DAILY_NATIVE_ACK_NONCE")
    if not (os.environ.get("VIM_DAILY_NATIVE_WINDOW") and socket_path and nonce):
        return
    # A continuation in this same child must not send a second acknowledgement
    # to the selector after its bounded listener has closed.
    os.environ.pop("VIM_DAILY_NATIVE_ACK_SOCKET", None)
    os.environ.pop("VIM_DAILY_NATIVE_ACK_NONCE", None)
    payload = json.dumps({"nonce": nonce, "phase": "curriculum-loaded",
                          "pid": os.getpid(), "revision": cur.get("revision")},
                         separators=(",", ":"))
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(2.0)
            client.connect(socket_path)
            client.sendall((payload + "\n").encode("utf-8"))
    except (OSError, ValueError) as exc:
        # Stop before artifact creation or grading when the parent cannot
        # receive this child. The selector owns timeout/window cleanup.
        raise RuntimeError("Native tutor session acknowledgement failed; no lesson was attempted.") from exc


def append_event(cfg, event):
    paths = _paths(cfg)
    paths["events"].parent.mkdir(parents=True, exist_ok=True)
    row = dict(event)
    if getattr(cfg, "curriculum_revision", None):
        row.setdefault("curriculum_revision", cfg.curriculum_revision)
        row.setdefault("curriculum_contract_sha256", cfg.curriculum_contract_sha256)
    row.setdefault("event_id", "%s-%08x" % (
        dt.datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%f%z"), random.getrandbits(32)))
    row.setdefault("at", dt.datetime.now().astimezone().isoformat())
    if getattr(cfg, "practice", False):
        row["practice"] = True
        return row
    data = (json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(paths["events"], os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
    if row.get("type") in ("card", "question", "review", "check_concepts") \
            and row.get("result") in ("pass", "fail"):
        stamp = Path(cfg.stamp)
        stamp.parent.mkdir(parents=True, exist_ok=True)
        stamp.touch()
    return row


def project(cur, events):
    card_map = {card["id"]: card for card in cur["cards"]}
    passed = set()
    attempts = {}
    question_attempts = {}
    passed_questions = set()
    check_concepts = set()
    reviews = {}
    earned_review_stages = set()
    completed_at = {}
    active_remediations = {}
    errors = 0
    for event in events:
        if event.get("type") == "ledger_error":
            errors += 1
            continue
        card_id = event.get("card_id")
        if card_id and event.get("type") == "card":
            attempts[card_id] = attempts.get(card_id, 0) + 1
        if event.get("type") == "card" and event.get("result") == "pass":
            passed.add(card_id)
            completed_at[card_id] = event.get("at")
            active_remediations.pop(card_id, None)
        if event.get("type") == "remediation_scheduled":
            active_remediations[card_id] = {
                "id": event.get("remediation_id"),
                "family": event.get("family"),
                "name": event.get("name"),
                "changed_variant": event.get("changed_variant"),
            }
        if event.get("question_id") and event.get("type") in ("question", "review"):
            qid = event["question_id"]
            question_attempts[qid] = question_attempts.get(qid, 0) + 1
            if event.get("result") == "pass":
                passed_questions.add(qid)
        if event.get("type") == "check_concepts" and event.get("result") == "pass":
            check_concepts.add(card_id)
        if event.get("type") == "review":
            reviews[event["review_key"]] = {
                "stage": event.get("review_stage", 0), "next_due": event.get("next_due"),
                "module_id": event.get("module_id"), "question_id": event.get("question_id"),
            }
            if event.get("result") == "pass":
                earned_review_stages.add((event["review_key"], int(event.get("review_stage", 0))))
                active_remediations.pop(event["review_key"], None)
        if (event.get("type") == "card" and event.get("result") == "pass"
                and event.get("next_due")
                and _review_variants(card_map.get(card_id, {}))):
            reviews.setdefault(card_id, {
                "stage": 0, "next_due": event["next_due"], "module_id": event.get("module_id"),
                "question_id": event.get("question_id"),
            })
    stages = {}
    for stage in cur["stages"]:
        done = sum(1 for cid in stage["card_ids"] if cid in passed)
        required_review_ids = stage.get("required_review_card_ids", [])
        reviews_done = sum(
            1 for cid in required_review_ids
            if any(key == cid and review_stage >= 1
                   for key, review_stage in earned_review_stages)
        )
        prerequisites_met = all(stages[p]["state"] == "mastered"
                                for p in stage.get("prerequisites", []))
        if done == len(stage["card_ids"]) and reviews_done == len(required_review_ids):
            state = "mastered"
        elif done == len(stage["card_ids"]):
            state = "review_pending"
        elif not prerequisites_met:
            state = "locked"
        elif done == len(stage["card_ids"]) - 1 and stage["card_ids"][-1] not in passed:
            state = "check_ready"
        elif done:
            state = "learning"
        else:
            state = "available"
        stages[stage["id"]] = {
            "state": state, "done": done, "total": len(stage["card_ids"]),
            "reviews_done": reviews_done, "reviews_total": len(required_review_ids),
            "optional": stage.get("optional", False), "title": stage["title"],
        }

    modules = {}
    card_stages = {card["id"]: card["stage_owner"] for card in cur["cards"]}
    for module in cur["modules"]:
        done = sum(1 for cid in module["card_ids"] if cid in passed)
        required_review_ids = module.get("required_review_card_ids", [])
        reviews_done = sum(
            1 for cid in required_review_ids
            if any(key == cid and review_stage >= 1
                   for key, review_stage in earned_review_stages)
        )
        incomplete_stage_ids = {
            card_stages[cid] for cid in module["card_ids"] if cid not in passed
        }
        if done == len(module["card_ids"]) and reviews_done == len(required_review_ids):
            state = "mastered"
        elif done == len(module["card_ids"]):
            state = "review_pending"
        elif incomplete_stage_ids and all(
                stages[stage_id]["state"] == "locked" for stage_id in incomplete_stage_ids):
            state = "locked"
        elif done == len(module["card_ids"]) - 1 and module["card_ids"][-1] not in passed:
            state = "check_ready"
        elif done:
            state = "learning"
        else:
            state = "available"
        modules[module["id"]] = {
            "state": state, "done": done, "total": len(module["card_ids"]),
            "reviews_done": reviews_done, "reviews_total": len(required_review_ids),
            "stage_ids": module.get("stage_ids", []),
        }
    current_stage = next((stage_id for stage_id in cur["main_stage_sequence"]
                          if stages[stage_id]["state"] != "mastered"), None)
    out = {
        "schema": "vim-daily/progress@2", "revision": cur["revision"], "passed_cards": sorted(passed),
        "attempts": attempts, "question_attempts": question_attempts, "reviews": reviews,
        "passed_questions": sorted(passed_questions),
        "check_concepts": sorted(check_concepts),
        "stages": stages, "current_stage": current_stage, "modules": modules,
        "completed_at": completed_at, "ledger_errors": errors,
        "active_remediations": active_remediations,
    }
    badges = []
    if passed:
        badges.append("first-step")
    if any(cid.endswith(".06") for cid in passed):
        badges.append("transfer")
    if stages["S0"]["state"] == "mastered":
        badges.append("grid-author")
    if stages["S7"]["state"] == "mastered":
        badges.append("still-artist")
    if stages["A2"]["state"] == "mastered":
        badges.append("inbetweener")
    if stages["A4"]["state"] == "mastered":
        badges.append("timing-editor")
    if stages["A7"]["state"] == "mastered":
        badges.append("animator")
    if stages["P"]["state"] == "mastered":
        badges.append("corpus-reader")
    out["xp"] = 10 * len(passed) + 3 * len(earned_review_stages)
    out["badges"] = badges
    # Memory plan 2026-09-29: deck boxes and the weak set. Folded here so the
    # projection is rebuilt from the ledger; deck events add no XP.
    out["deck"] = (_deck_module().fold(cur, events) if cur.get("deck")
                   else {"items": {}, "weak": [], "weak_families": []})
    return out


def save_projection(cfg, progress):
    path = _paths(cfg)["projection"]
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="progress-v2-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(progress, f, indent=1, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def rebuild(cfg, cur):
    p = project(cur, read_events(cfg))
    save_projection(cfg, p)
    return p


def _now():
    return dt.datetime.now().astimezone()


def _due(iso):
    if not iso:
        return False
    try:
        return dt.datetime.fromisoformat(iso) <= _now()
    except ValueError:
        return False


def next_card(cur, progress):
    passed = set(progress["passed_cards"])
    card_map = {card["id"]: card for card in cur["cards"]}
    current = progress.get("current_stage")
    if current and progress["stages"][current]["state"] not in {
            "locked", "review_pending", "mastered"}:
        stage = next(row for row in cur["stages"] if row["id"] == current)
        for cid in stage["card_ids"]:
            if cid not in passed:
                return card_map[cid]
    # The proportional course is a non-blocking branch.  Offer it while the
    # main path is waiting on spaced retrieval, or after the main path ends;
    # never let it pre-empt an available S/A lesson.
    proportional = progress["stages"]["P"]
    if proportional["state"] not in {"locked", "review_pending", "mastered"}:
        stage = next(row for row in cur["stages"] if row["id"] == "P")
        for cid in stage["card_ids"]:
            if cid not in passed:
                return card_map[cid]
    return None


def due_review(cur, progress):
    card_map = {card["id"]: card for card in cur["cards"]}
    due = []
    for key, review in progress["reviews"].items():
        if not _review_variants(card_map.get(key, {})):
            continue
        value = review.get("next_due")
        if not _due(value):
            continue
        try:
            due_at = dt.datetime.fromisoformat(value).timestamp()
        except (TypeError, ValueError):
            continue
        due.append((due_at, key, review))
    if not due:
        return None
    _, key, review = sorted(due)[0]
    return key, review


def should_review(events, review):
    if not review:
        return False
    completed = sum(1 for e in events if e.get("result") == "pass" and e.get("type") in ("card", "review"))
    return completed > 0 and completed % 4 == 0


def should_run_review(events, review, candidate, explicit_force=False):
    if not review or explicit_force:
        return False
    if candidate and candidate.get("kind") == "module_check":
        return False
    # With no project card left, spaced practice is the remaining course loop
    # and must not be starved by a cadence defined in terms of new completions.
    return candidate is None or should_review(events, review)


def _question_map(cur):
    return {q["id"]: q for q in cur["questions"]}


def _align_question_art(value):
    """Align display-only box borders without changing authored question text."""
    lines = str(value).splitlines()
    if not any("│" in line for line in lines):
        return str(value)
    parts_by_line = [line.split("│") if "│" in line else None for line in lines]
    widths = {}
    for parts in parts_by_line:
        if not parts:
            continue
        for index in range(1, len(parts) - 1, 2):
            widths[index] = max(widths.get(index, 0), _cell_width(parts[index]))
        # Authored gaps sometimes compensate for a shorter BEFORE row.
        # Once that row is padded, retaining the old compensation offsets
        # the AFTER border. Each gap is a separate layout column.
        for index in range(2, len(parts) - 1, 2):
            widths[index] = max(widths.get(index, 0), _cell_width(parts[index]))
    aligned = []
    for line, parts in zip(lines, parts_by_line):
        if not parts:
            aligned.append(line)
            continue
        for index in range(1, len(parts) - 1, 2):
            target = widths.get(index, _cell_width(parts[index]))
            parts[index] += " " * max(0, target - _cell_width(parts[index]))
        for index in range(2, len(parts) - 1, 2):
            target = widths[index]
            gap = parts[index].strip()
            room = max(0, target - _cell_width(gap))
            parts[index] = " " * (room // 2) + gap + " " * (room - room // 2)
        aligned.append("│".join(parts))
    return "\n".join(aligned)


def _question_display_text(value, width=None):
    """Render prose and preserve multiline art rows in a display copy."""
    paragraphs = []
    for paragraph in str(value).split("\n\n"):
        if "│" in paragraph:
            rows = []
            for row in _align_question_art(paragraph.rstrip()).splitlines():
                if "│" in row or not width:
                    rows.append(row)
                else:
                    rows.extend(_wrap_prose(row, width))
            paragraphs.append("\n".join(rows))
            continue
        line = " ".join(part.strip() for part in paragraph.splitlines() if part.strip())
        if not line:
            continue
        paragraphs.append("\n".join(_wrap_prose(line, width)) if width else line)
    return "\n\n".join(paragraphs)


def _compact_question_text(value, width=64):
    """Wrap compact prompts deliberately instead of letting the terminal do it."""
    # ASCII evidence is layout, not prose. Keep its row breaks and pad only a
    # display copy so right borders line up even when an authored row is short.
    rendered = _question_display_text(value, width=width)
    return rendered.replace("\n\n", "\n")


def _compact_choice_text(value, width=62):
    """Keep both halves readable as two labeled compact rows."""
    if "│" in str(value) or "\n" in str(value):
        return _align_question_art(str(value))
    value = " ".join(str(value).split())
    for marker in (" · V: ", " | NEOVIM: "):
        if marker in value:
            animation, neovim = value.split(marker, 1)
            animation = animation.removeprefix("ANIMATION: ").removeprefix("A: ")
            neovim = neovim.removeprefix("NEOVIM: ").removeprefix("V: ")
            return "\n".join(
                _wrap_prose(animation, width, indent="ANIM: ", subsequent="      ")
                + _wrap_prose(neovim, width, indent="VIM:  ", subsequent="      "))
    return "\n".join(_wrap_prose(value, width))


def _copy_text_to_clipboard(value):
    """Copy a question page without relying on tmux mouse-selection state."""
    if not shutil.which("pbcopy"):
        return False
    try:
        return subprocess.run(
            ["pbcopy"], input=value, text=True, check=False,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        ).returncode == 0
    except OSError:
        return False


def ask_question(q, *, input_fn=input, shuffle=True, rendered=None, evidence=None):
    order = list(range(len(q["choices"])))
    letters = "abcd"[:len(order)]
    forced_order = os.environ.get("VIM_DAILY_TEST_CHOICE_ORDER")
    if forced_order:
        candidate = [int(value) for value in forced_order]
        if len(candidate) == len(order):
            if sorted(candidate) != order:
                raise ValueError("VIM_DAILY_TEST_CHOICE_ORDER must permute the displayed choices")
            order = candidate
    elif shuffle and os.environ.get("VIM_DAILY_TEST_ORDERED_CHOICES") != "1":
        random.shuffle(order)
    compact = (__import__("sys").stdout.isatty()
               and shutil.get_terminal_size((80, 24)).lines < 38)
    if __import__("sys").stdout.isatty() and q.get("evidence", {}).get("full"):
        # Eight complete side-by-side frame plates cannot fit even the large
        # popup. Show named changed-row samples here; the complete sequence
        # remains in its lesson/animation tab and the clipboard question.
        compact = True
    if __import__("sys").stdout.isatty():
        # Neovim has just exited on paired after-questions. Without a fresh
        # page its final grid remains behind the short question text and makes
        # choices appear interleaved with unrelated terminal content.
        print("\033[2J\033[H", end="")
    prompt = q.get("compact_prompt", q["prompt"]) if compact else q["prompt"]
    # Compact choices are separately authored, not truncated full sentences.
    # They retain both domains while leaving the question stem on screen.
    displayed_choices = q.get("compact_choices", q["choices"]) if compact else q["choices"]
    if compact:
        prompt = _compact_question_text(prompt)
    else:
        prompt = _align_question_art(prompt)
    if __import__("sys").stdout.isatty():
        columns = shutil.get_terminal_size((80, 24)).columns
        displayed_choices = [
            _compact_choice_text(choice, width=max(42, min(78, columns - 8)))
            for choice in displayed_choices
        ]
    if evidence is not None:
        evidence.update({
            "question_prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "displayed_choice_indices": list(order),
            "displayed_choices": [displayed_choices[original] for original in order],
        })
    print("\n%s" % prompt)
    for shown, original in enumerate(order):
        print("  %s) %s" % (letters[shown], displayed_choices[original]))
    clipboard_page = "%s\n%s" % (
        q["prompt"] if q.get("evidence", {}).get("full") else prompt,
        "\n".join("%s) %s" % (letters[shown],
                  q["choices"][original] if q.get("evidence", {}).get("full")
                  else displayed_choices[original])
                  for shown, original in enumerate(order)),
    )
    if rendered:
        rendered(q, order)
    while True:
        try:
            answer = input_fn(
                "  answer (a-%s) · y copies this question · f feedback: " % letters[-1]
            ).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None, None
        if answer == "f":
            note_feedback_context(question_id=q.get("id"),
                                  question_prompt=_clip(" ".join(prompt.split()), 160))
            collect_feedback(input_fn, screen="question")
            continue
        if answer == "y":
            if _copy_text_to_clipboard(clipboard_page):
                print("  copied the complete question and choices to the macOS clipboard")
            else:
                print("  clipboard copy is unavailable; this did not count as an attempt")
            continue
        if answer in letters and len(answer) == 1:
            break
        print("  answer with %s, y to copy, or f to send feedback; this did not count as an attempt" %
              ", ".join(letters))
    chosen = order[letters.index(answer)]
    if evidence is not None:
        evidence.update({"raw_answer": answer, "semantic_choice": chosen})
    right = chosen == q["correct_choice"]
    note_feedback_context(question_id=q.get("id"), answer="abcd"[chosen] if chosen < 4 else chosen,
                          answer_correct=bool(right), screen="after-answer")
    print("  %s" % q["feedback"][chosen])
    return right, chosen


_KEY_TOKEN = re.compile(r"<((?:[A-Za-z]-)?[A-Za-z0-9]+)>")
_FORBIDDEN_EX = re.compile(
    r"(?i):\s*(?:!|w(?:rite)?\b|wa\b|x\b|xit\b|q(?:uit)?\b|qa\b|e(?:dit)?\b|"
    r"source\b|so\b|runtime\b|packadd\b|lua\b|python\w*\b|perl\b|ruby\b|"
    r"terminal\b|term\b|call\b|execute\b|redir\b|cd\b|lcd\b|tcd\b|"
    r"vnew\b|new\b|split\b|vsplit\b|tabnew\b)")


def _notation_bytes(text):
    """Convert displayed Vim key notation into the bytes consumed by `nvim -s`."""
    controls = {
        "esc": b"\x1b", "cr": b"\r", "enter": b"\r", "return": b"\r",
        "nl": b"\n", "bs": b"\x7f", "tab": b"\t", "space": b" ",
        "lt": b"<", "bar": b"|",
    }
    out = bytearray()
    cursor = 0
    for match in _KEY_TOKEN.finditer(text):
        out.extend(text[cursor:match.start()].encode("utf-8"))
        token = match.group(1)
        lowered = token.casefold()
        if lowered in controls:
            out.extend(controls[lowered])
        elif lowered.startswith("c-") and len(token[2:]) == 1:
            char = token[2:]
            out.append(ord(char.upper()) & 0x1f)
        else:
            raise ValueError("unsupported key notation <%s>" % token)
        cursor = match.end()
    out.extend(text[cursor:].encode("utf-8"))
    return bytes(out)


def _safe_typed_effect(contract, answer):
    """Run learner keys in an isolated scratch Neovim and compare their effect."""
    evidence = {"effect_version": contract.get("effect_version", 1),
                "raw_answer": answer}
    if not answer.strip():
        return False, evidence, "No keys were entered."
    if _FORBIDDEN_EX.search(answer) or "<C-z>" in answer or "<C-\\>" in answer:
        evidence["rejected"] = "unsafe-or-external-command"
        return False, evidence, "That answer leaves the bounded scratch-edit sandbox."
    try:
        typed = _notation_bytes(answer)
    except ValueError as exc:
        evidence["rejected"] = "unsupported-notation"
        return False, evidence, str(exc)
    executable = shutil.which("nvim")
    if not executable:
        evidence["rejected"] = "nvim-unavailable"
        return False, evidence, "Neovim is unavailable, so the semantic answer could not be checked."
    with tempfile.TemporaryDirectory(prefix="vim-daily-question-") as tmp:
        root = Path(tmp)
        artifact = root / "scratch.txt"
        script = root / "keys.bin"
        result_path = root / "result.json"
        initial = contract.get("initial_lines", [])
        artifact.write_text("\n".join(initial) + "\n", encoding="utf-8")
        result_lua = (
            "lua local p=%s; local r={lines=vim.api.nvim_buf_get_lines(0,0,-1,true),"
            "cursor=vim.api.nvim_win_get_cursor(0),wins=#vim.api.nvim_list_wins(),"
            "tabs=#vim.api.nvim_list_tabpages()}; vim.fn.writefile({vim.json.encode(r)},p)"
            % json.dumps(str(result_path))
        )
        bootstrap = b":set noautoindent nosmartindent nocindent indentexpr=\rgg^"
        trailer = b"\x1b:" + result_lua.encode("utf-8") + b"\r:qa!\r"
        script.write_bytes(bootstrap + typed + trailer)
        isolated = root / "xdg"
        isolated.mkdir()
        env = dict(os.environ)
        env.update({"HOME": str(root), "XDG_CONFIG_HOME": str(isolated),
                    "XDG_DATA_HOME": str(isolated), "XDG_STATE_HOME": str(isolated),
                    "XDG_CACHE_HOME": str(isolated)})
        proc = subprocess.run(
            [executable, "-u", "NONE", "-i", "NONE", "-n", "-s", str(script),
             str(artifact)], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=env, timeout=10, check=False)
        evidence["nvim_returncode"] = proc.returncode
        evidence["input_sha256"] = hashlib.sha256(
            ("\n".join(initial) + "\n").encode("utf-8")).hexdigest()
        if proc.returncode != 0 or not result_path.exists():
            evidence["stderr"] = proc.stderr.decode("utf-8", "replace")[-500:]
            return False, evidence, "Neovim could not evaluate that key sequence."
        result = json.loads(result_path.read_text(encoding="utf-8"))
    target = contract.get("target_lines", [])
    evidence.update({
        "result_lines_sha256": hashlib.sha256(
            ("\n".join(result["lines"]) + "\n").encode("utf-8")).hexdigest(),
        "target_lines_sha256": hashlib.sha256(
            ("\n".join(target) + "\n").encode("utf-8")).hexdigest(),
        "result_cursor": result.get("cursor"), "window_count": result.get("wins"),
        "tab_count": result.get("tabs"),
    })
    right = result.get("lines") == target
    if contract.get("target_cursor"):
        right = right and result.get("cursor") == contract["target_cursor"]
    right = right and result.get("wins") == 1 and result.get("tabs") == 1
    return right, evidence, ("The scratch art matches TARGET exactly." if right else
                             "The scratch art does not yet match TARGET exactly.")


def _term_group_result(answer, groups):
    normalized = " ".join(answer.casefold().split())
    missing = [group for group in groups
               if not any(term.casefold() in normalized for term in group)]
    return not missing, missing


def _print_grammar_breakdown(q, missing=None):
    print("  GRAMMAR BREAKDOWN")
    for part in q.get("grammar_breakdown", []):
        if isinstance(part, list):
            part = " + ".join(part)
        print("    • %s" % part)
    # VD-13: decode the actual commands the question quoted, key by key, so a
    # wrong answer teaches `3daw`, `rO`, `:8s/-/=/g` instead of only the rules.
    quoted = []
    for text in re.findall(r"`([^`]+)`", q.get("prompt", "")):
        if text not in quoted and not text.startswith("[") and len(text) <= 40:
            quoted.append(text)
    if quoted:
        K = _keys_module()
        print("  THOSE COMMANDS, KEY BY KEY")
        for text in quoted:
            for line in K.explain_lines(text):
                print("    %s" % line)
    if missing:
        print("  Reconsider: %s" % "; ".join(" / ".join(group) for group in missing))


def _concept_text(value):
    """Turn answer feedback into a learner-facing explanation sentence."""
    text = str(value or "").strip()
    for prefix in ("Correct. ", "Correct: "):
        if text.casefold().startswith(prefix.casefold()):
            text = text[len(prefix):]
            break
    if text.casefold() in ("correct.", "correct:"):
        text = ""
    return text


def _print_choice_explanation(q, chosen, *, compact=False):
    """Explain a selected choice without exposing curriculum/runtime metadata.

    VD-49: the operator could not read clipped sentences ("…") here. Every
    field now wraps with a hanging indent at the real popup width, and paired
    answers print their ANIMATION and NEOVIM halves on separate lines.
    """
    correct = q["correct_choice"]
    choices = q.get("choices", [])
    feedback = q.get("feedback", [])
    width = max(40, shutil.get_terminal_size((80, 24)).columns - 4)

    def field(label, text, correct_text=None, role=None):
        raw_text = str(text)
        # Keep authored art rows as rows.  Only prose is wrapped/flattened;
        # borders are padded in this display copy and the canonical question
        # payload remains untouched.
        if "│" in raw_text or "\n" in raw_text:
            head = "  %s  " % label
            indent = " " * 4
            for index, row in enumerate(_align_question_art(raw_text).splitlines()):
                prefix = head if index == 0 else indent
                rendered = _partial_key_colours(row, correct_text) if correct_text else (
                    _paint(row, role) if role else row)
                print(prefix + rendered)
            return
        text = " ".join(raw_text.split())
        halves = text.split(" | NEOVIM: ", 1) if " | NEOVIM: " in text else [text]
        if len(halves) == 2:
            halves = ["ANIM: " + halves[0].removeprefix("ANIMATION: "),
                      "VIM: " + halves[1]]
        head = "  %s  " % label
        indent = " " * 4
        for index, half in enumerate(halves):
            first = head if index == 0 else indent
            for row in textwrap.wrap(half, width=width, initial_indent=first,
                                     subsequent_indent=indent + "  ") or [first]:
                print(_partial_key_colours(row, correct_text) if correct_text else
                      (_paint(row, role) if role else row))

    if not isinstance(chosen, int) or chosen < 0 or chosen >= len(choices):
        print("  YOUR ANSWER  (not recorded)")
        return
    field("YOUR ANSWER", choices[chosen], correct_text=choices[correct])
    if chosen != correct:
        why_missed = (feedback[chosen] if chosen < len(feedback)
                      else "That choice does not match the shown result.")
        field("WHY IT MISSES", _concept_text(why_missed))
        field("CORRECT ANSWER", choices[correct], correct_text=choices[correct])
    concept = feedback[correct] if correct < len(feedback) else ""
    concept = _concept_text(concept)
    if concept:
        field("CONCEPT", concept)
    if any(_command_spans(text) for text in (choices[chosen], choices[correct])) and any(
            re.search(r":[0-9%,$]*s[^\w\s]", text) for text in choices):
        print("  CONCEPT SHAPE  " + _concept_shape())


def _question_answer_guidance(form):
    """Show the response shape before free text is graded.

    Examples deliberately use a different command/problem, so they teach the
    interface without giving away the authored answer under examination.
    """
    if form == "typed_keys":
        return [
            "ANSWER FORMAT: keys only. OTHER EXAMPLE: `2jfxrO` (<CR>=Enter).",
        ]
    if form == "decode":
        return [
            "ANSWER FORMAT: parts + effect. OTHER EXAMPLE: `2dw` = 2+delete+word.",
        ]
    if form == "complete":
        return [
            "ANSWER FORMAT: missing keys only. OTHER EXAMPLE: execute `:3s/a/b/g` with `<CR>`.",
        ]
    if form == "why":
        return [
            "ANSWER FORMAT: `Use X because …; avoid Y because …`. OTHER EXAMPLE: r keeps width; x shifts.",
        ]
    return ["ANSWER FORMAT  answer the question in one plain-language sentence."]


def ask_authored_question(q, *, input_fn=input, shuffle=True, rendered=None,
                          evidence=None):
    """Ask one authored form; return (right, semantic answer)."""
    form = q.get("form", "multiple_choice")
    if form in ("multiple_choice", "predict_art"):
        return ask_question(q, input_fn=input_fn, shuffle=shuffle, rendered=rendered,
                            evidence=evidence)
    compact = (__import__("sys").stdout.isatty()
               and shutil.get_terminal_size((80, 24)).lines < 38)
    prompt_text = q["prompt"]
    if compact and form == "typed_keys":
        sections = q["prompt"].split("\n\n")
        animation = sections[0].removeprefix("ANIMATION\n") if sections else q["prompt"]
        prompt_text = _compact_question_text(
            "ANIMATION: %s\n\nNEOVIM: make START become TARGET; type keys only; effect is graded."
            % animation)
    print("\n%s" % prompt_text)
    if form == "typed_keys":
        contract = q["answer_contract"]
        if compact:
            print("\n  START%27sTARGET" % "")
            initial, target = contract["initial_lines"], contract["target_lines"]
            for index in range(max(len(initial), len(target))):
                before = initial[index] if index < len(initial) else ""
                after = target[index] if index < len(target) else ""
                print("  │%-30s │%s" % (before[:30], after[:30]))
        else:
            print("\n  START")
            for line in contract["initial_lines"]:
                print("  │" + line)
            print("  TARGET")
            for line in contract["target_lines"]:
                print("  │" + line)
        prompt = "  keys (Vim notation such as <Esc> or <CR>): "
    else:
        prompt = "  your answer: "
    for line in _question_answer_guidance(form):
        print("  %s" % line)
    if rendered:
        rendered(q, [])
    while True:
        try:
            raw_answer = input_fn(prompt)
            # VD-13: typed keys are graded by effect, and a trailing space is a real
            # key (`r ` erases a cell). .strip() turned `4G05lr ` into `4G05lr`.
            answer = (raw_answer.rstrip("\r\n") if form == "typed_keys"
                      else raw_answer.strip())
        except (EOFError, KeyboardInterrupt):
            print()
            return None, None
        if answer:
            break
        print("  Blank input did not count as an attempt. Use the ANSWER FORMAT above, or Ctrl-c to leave.")
    if evidence is not None:
        evidence.update({"raw_answer": answer, "question_form": form,
                         "question_prompt_sha256": hashlib.sha256(
                             q["prompt"].encode("utf-8")).hexdigest()})
    contract = q["answer_contract"]
    missing = None
    if form == "typed_keys":
        right, effect_evidence, message = _safe_typed_effect(contract, answer)
        if evidence is not None:
            evidence.update(effect_evidence)
    elif form == "complete":
        normalized = " ".join(answer.casefold().split())
        accepted = {" ".join(value.casefold().split())
                    for value in contract.get("accepted_answers", [])}
        right = normalized in accepted
        message = ("That completes the grammar." if right else
                   "That does not complete the stated grammar yet.")
    else:
        right, missing = _term_group_result(answer, contract.get("required_term_groups", []))
        message = ("Your explanation names every required part." if right else
                   "Your explanation is missing one or more required parts.")
    print("  %s" % message)
    if not right:
        _print_grammar_breakdown(q, missing)
    return right, answer


def _configured_question_input(cfg, q):
    if cfg.question_answer is None:
        return input
    return lambda _prompt: cfg.question_answer(q)


def _question_for_card(cur, progress, card):
    qmap = _question_map(cur)
    # VD-13: the grammar-primer concept card (M0.P0) owns only
    # paired_question_ids; without this fallback run_concept crashed on None.
    qids = card.get("question_ids") or card.get("paired_question_ids") or []
    qids = [qid for qid in qids if qid in qmap]
    if not qids:
        return None
    # Rotate within the card bank so a retry is not the same immediate stem.
    n = progress["attempts"].get(card["id"], 0)
    return qmap[qids[n % len(qids)]]


def _question_event(cur, card, q, right, answer, evidence, **extra):
    row = {
        "type": "question", "result": "pass" if right else "fail",
        "card_id": card["id"], "module_id": card["module_id"],
        "question_id": q["id"], "question_form": q.get("form"),
        "placement": q.get("placement"), "curriculum_revision": cur["revision"],
        "question_evidence": evidence,
    }
    if isinstance(answer, int):
        row["choice"] = answer
    else:
        row["answer"] = answer
    row.update(extra)
    return row


def run_paired_questions(cfg, cur, progress, card, placement):
    """Run unanswered card-owned questions at the authored pre/post position."""
    qmap = _question_map(cur)
    passed = set(progress.get("passed_questions", []))
    qids = [qid for qid in card.get("paired_question_ids", [])
            if qid not in passed and qmap[qid].get("placement") == placement]
    replay = None
    for qid in qids:
        q = qmap[qid]
        evidence = {}
        right, answer = ask_authored_question(
            q, input_fn=_configured_question_input(cfg, q),
            shuffle=cfg.question_answer is None,
            rendered=cfg.question_rendered, evidence=evidence)
        if right is None:
            return None, replay
        append_event(cfg, _question_event(
            cur, card, q, right, answer, evidence, paired=True))
        replay = {"type": "paired_question", "question": q,
                  "answer": answer, "right": bool(right),
                  "question_evidence": evidence}
        progress = rebuild(cfg, cur)
        if not right:
            append_event(cfg, {
                "type": "card", "result": "fail", "card_id": card["id"],
                "module_id": card["module_id"], "reason": "paired-question",
                "question_id": qid, "placement": placement,
            })
            _schedule_remediation(
                cfg, card, "Q", "%s question %s with its grammar breakdown" % (
                    placement, qid),
                "paired %s question not yet demonstrated" % q.get("form"))
            return False, replay
        passed.add(qid)
    return True, replay


def _review_question(cur, progress, module_id, previous_qid=None):
    bank = [q for q in cur["questions"]
            if q["module_id"] == module_id and q["id"] != previous_qid
            and q.get("form") == "multiple_choice"]
    return min(bank, key=lambda q: (progress["question_attempts"].get(q["id"], 0), q["id"]))


def _schedule_remediation(cfg, card, family, changed_variant, reason):
    """Record and name the next changed attempt instead of silently repeating."""
    names = {
        "Q": "Read motion, then choose the Neovim operation",
        "T": "Changed-art transfer recovery",
        "K": "Concept-to-art checkpoint recovery",
    }
    row = append_event(cfg, {
        "type": "remediation_scheduled", "result": "scheduled",
        "card_id": card["id"], "module_id": card["module_id"],
        "family": family, "name": names[family],
        "remediation_id": "%s-%s" % (family, card["id"]),
        "changed_variant": changed_variant, "reason": reason,
    })
    if getattr(cfg, "practice", False):
        print("PRACTICE RESULT  no remediation or progress event was recorded")
    else:
        print("REMEDIATION SCHEDULED  %s · %s" % (
            row["remediation_id"], row["name"]))
        print("NEXT CHANGED VARIANT  %s" % changed_variant)
    return row


def _next_due(cur, stage):
    hours = cur["review_intervals_hours"][min(stage, len(cur["review_intervals_hours"]) - 1)]
    return (_now() + dt.timedelta(hours=hours)).isoformat()


def _artifact_path(cfg, card):
    if getattr(cfg, "practice", False):
        base = _paths(cfg)["sessions"] / "practice" / card["project_id"] / card["id"]
    else:
        base = _paths(cfg)["projects"] / card["project_id"]
        if card.get("history_source_provenance"):
            # C35: a new source-faithful task must not overwrite the operator's
            # rejected old strip or its checkpoints. Start a separate study
            # keyed to this card's exact art contract, not a migrated old file.
            contract = {key: card.get(key) for key in
                        ("id", "start", "target", "expected", "history_source_provenance")}
            identity = hashlib.sha256(json.dumps(contract, sort_keys=True,
                ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()[:20]
            base = base / "source-history" / card["id"] / identity
    if card.get("artifact") == "transfer":
        return base / ("transfer-%s.txt" % card["id"])
    if card.get("artifact") == "animation-study":
        return base / ("animation-%s.txt" % card["id"])
    return base / "strip.txt"


def _read_lines(path, preserve_trailing_whitespace=False):
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    if preserve_trailing_whitespace:
        return lines
    return [line.rstrip() for line in lines]


def _card_lines(card, lines):
    if card.get("preserve_trailing_whitespace"):
        return list(lines)
    return [line.rstrip() for line in lines]


def _write_new(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _write_lines_atomic(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + "-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _module_for_card(cur, card):
    return next(module for module in cur["modules"] if module["id"] == card["module_id"])


def _lesson_context(cur, card):
    """Return the authored teaching contract shared by briefs and debriefs."""
    module = _module_for_card(cur, card)
    context = {
        "module": module,
        "why": [
            "Motion intent: %s." % module["meaning"].rstrip("."),
            "Authoring principle: %s." % module["principle"].rstrip("."),
            "Failure to watch: %s." % module["defect"].rstrip("."),
        ],
        "buys": card["lesson_benefit"],
        "source": card.get("source_ref") or module["source_ref"],
    }
    # A module's missile narrative does not explain a Dracula alignment step.
    if card.get("review_source_card_id", card["id"]) == "M11.CUC":
        context["why"] = [
            "Motion intent: align the walking cape with the standing cape.",
            "Authoring principle: use one screen column as a registration guide.",
            "Failure to watch: deleting a contour glyph instead of the extra leading space.",
        ]
        context["buys"] = "Compare the two cape rows with a column guide, then remove only the extra space."
    return context


_KEYS_MODULE = None
_DECK_MODULE = None
# Families missed in the deck lately; run() sets it so the next lesson that
# uses one shows a REMEMBER line (memory plan §2, resurfacing).
DECK_WEAK = set()


def _deck_module():
    """Load share/deck.py (flashcards, spacing, warm-up) next to this file."""
    global _DECK_MODULE
    if _DECK_MODULE is None:
        import importlib.util
        path = Path(__file__).with_name("deck.py")
        spec = importlib.util.spec_from_file_location("vim_daily_v2_deck", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _DECK_MODULE = module
    return _DECK_MODULE


def _keys_module():
    """Load share/v2_keys.py (key-by-key explanations, VD-13) next to this file."""
    global _KEYS_MODULE
    if _KEYS_MODULE is None:
        import importlib.util
        path = Path(__file__).with_name("v2_keys.py")
        spec = importlib.util.spec_from_file_location("vim_daily_v2_keys", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _KEYS_MODULE = module
    return _KEYS_MODULE


def _card_key_strings(card):
    keys = [card.get("expected") or ""]
    keys += [method.get("keys", "") for method in card.get("method_alternatives", [])]
    return [k for k in keys if k]


def _families_shown_before(cur, card):
    """Command families whose exact keys an earlier guided lesson displayed."""
    if not cur:
        return None
    K = _keys_module()
    order = [cid for module in cur["modules"] for cid in module["card_ids"]]
    cards = {c["id"]: c for c in cur["cards"]}
    source = card.get("review_source_card_id") or card["id"]
    shown = set()
    for cid in order:
        if cid == source:
            break
        other = cards.get(cid, {})
        if other.get("show_recipe") and other.get("expected"):
            shown.update(family for family, _m in K.families(other["expected"]))
    return shown


def _new_concepts(card, cur):
    """Command families this lesson uses that no earlier guided lesson showed."""
    shown_before = _families_shown_before(cur, card)
    strings = _card_key_strings(card)
    if shown_before is None or not strings:
        return []
    K = _keys_module()
    trivial = {"j", "k", "h", "l", "[count]j", "[count]k", "[count]h", "[count]l"}
    return [(family, meaning) for family, meaning in K.families(strings[0])
            if family not in shown_before and family not in trivial]


def _new_concept_banner(card, cur, width=66):
    """VD-42: one-line compact banner naming each new idea."""
    new = _new_concepts(card, cur)
    # VD-48: a symbol taking a new job ($ as the last line, @ as a divider)
    # is announced like a new command, so the learner scrolls to its line.
    K = _keys_module()
    met = _symbols_met_before(cur, card) or {}
    multi = {}
    for symbol, _role in K.SYMBOL_ROLES:
        multi[symbol] = multi.get(symbol, 0) + 1
    symbol_names = ["%s = %s" % (symbol, K.SYMBOL_ROLES[(symbol, role)][1].split(" (")[0])
                    for symbol, role in K.symbol_roles(card.get("expected") or "")
                    if cur and (symbol, role) not in met and role not in ("key", "glyph")
                    and multi.get(symbol, 0) > 1]
    if not new and not symbol_names:
        return None
    names = []
    for family, _meaning in new:
        name = family.replace("[range]", "").replace("{text}<Esc>", "").replace("[count]", "")
        if name.startswith(":s/"):
            name = ":s///" + name.rsplit("/", 1)[1]
        if name.startswith(":set ") and any(n.startswith(":set ") for n in names):
            name = name[5:]
        if name not in names:
            names.append(name)
    for name in symbol_names:
        bare = name.split(" = ")[0]
        for index, existing in enumerate(names):
            if existing in (bare, "{N}" + bare):
                names[index] = name
                break
        else:
            if name not in names:
                names.append(name)
    # Readability audit #10: keep the pointer; shorten the names instead.
    tail = " ↓ alert below"
    head = "★ NEW %d: " % len(names)
    return head + _clip(" · ".join(names), max(10, width - len(head) - len(tail))) + tail


# Operator feedback 2026-09-29 13:33: "what is the concept diff between / and
# \\ ... i thought \\ was an escape seq". Every pattern breakdown says it.
SLASH_NOTE = [
    "     /    separates the parts: s/pattern/replacement/flags",
    "     \\    inside a pattern makes the next letter special (\\s, \\+); you type it, it is not Esc",
]


def _symbols_met_before(cur, card):
    """VD-48: (symbol, role) -> first card id, over every earlier card's answer."""
    if not cur:
        return None
    K = _keys_module()
    cards = {c["id"]: c for c in cur["cards"]}
    source = card.get("review_source_card_id") or card["id"]
    met = {}
    for cid in (cid for module in cur["modules"] for cid in module["card_ids"]):
        if cid == source:
            break
        for pair in K.symbol_roles(cards.get(cid, {}).get("expected") or ""):
            met.setdefault(pair, cid)
    return met


def _first_recipe_card(cur):
    for cid in (cid for module in cur["modules"] for cid in module["card_ids"]):
        other = next((c for c in cur["cards"] if c["id"] == cid), {})
        if other.get("show_recipe") and other.get("expected"):
            return cid
    return None


def _symbol_lines(card, cur, wrap):
    """VD-48: name a symbol's job when it changes meaning with context.

    The learner met `$` as a line address (:1,3t$), then as a pattern anchor
    (\\s\\+$), then as the end-of-row motion (2G$), and `\\` as an art glyph
    before it became a pattern prefix; nothing said which job was which.
    """
    K = _keys_module()
    met = _symbols_met_before(cur, card)
    if met is None:
        return [], set()
    roles = K.symbol_roles(card.get("expected") or "")
    multi = {}
    for symbol, role in K.SYMBOL_ROLES:
        multi[symbol] = multi.get(symbol, 0) + 1
    lines, covered = [], set()
    source = card.get("review_source_card_id") or card["id"]
    if source == _first_recipe_card(cur):
        lines += K.RECIPE_READING
    for symbol, role in roles:
        long, _short = K.SYMBOL_ROLES[(symbol, role)]
        new = (symbol, role) not in met
        if role == "key" or multi.get(symbol, 0) < 2:
            if new and not (role == "key" and lines and lines[0] == K.RECIPE_READING[0]):
                lines += wrap("★ NEW  " + long, "  ")
                covered.add((symbol, role))
            continue
        others = [(K.SYMBOL_ROLES[pair][1], cid) for pair, cid in met.items()
                  if pair[0] == symbol and pair[1] != role]
        others += [(K.SYMBOL_ROLES[pair][1], "this lesson") for pair in roles
                   if pair[0] == symbol and pair[1] != role]
        if not (new or card.get("show_recipe")):
            continue
        if not others and (role == "glyph" or not new):
            continue
        seen = []
        for short, cid in others:
            if short not in [s for s, _c in seen]:
                seen.append((short, cid))
        contrast = "; ".join("%s (%s)" % (short, cid if cid == "this lesson" else "in " + cid)
                             for short, cid in seen)
        lines += wrap("%s  %s%s" % ("★ NEW" if new else "REMEMBER", long,
                                     (" · elsewhere %s = %s" % (symbol, contrast)) if seen else ""),
                      "  ")
        covered.add((symbol, role))
    if lines and lines[0] != K.RECIPE_READING[0] or len(lines) > len(K.RECIPE_READING):
        head = "SYMBOLS · the same key can do a different job; read it by where it stands"
        if lines[0] == K.RECIPE_READING[0]:
            lines = lines[:len(K.RECIPE_READING)] + [head] + lines[len(K.RECIPE_READING):]
        else:
            lines = [head] + lines
    return lines, covered


def _substitute_anatomy_lines(card, wrap, heading, width=None):
    """VD-49: the operator's favourite chat explanation, folded into lessons.

    Any visible :s recipe is drawn as a labelled tree, then read back in plain
    English, then reduced to its reusable shape.
    """
    K = _keys_module()
    anatomy = K.substitute_anatomy(card.get("expected", ""))
    if not anatomy:
        # Memory plan §1: Normal-mode recipes get the same tree (count,
        # operator, motion ...). None when it would not fit: no clipped rows.
        rows = K.anatomy(card.get("expected", ""), width,
                         shape=card.get("key_shape")) if width else None
        return [heading] + rows if rows else []
    rows, english = anatomy
    lines = [heading]
    lines += rows
    lines += wrap(english, "  ")
    lines += wrap("Remember the shape, not the characters: :s/find/replace/flags is a "
                  "fill-in-the-blanks form; a range before s picks the lines.", "  ")
    return lines


def _new_concept_alert(card, cur, width=None):
    """VD-42: explain every first-time idea before the learner edits.

    A guided lesson used to print a recipe such as `:%s/\\s\\+$//e` with the
    generic hint "follow the visible grammar once"; four new ideas arrived with
    no explanation. Each new family now gets its meaning, a neutral example
    and, when the recipe is visible, a piece-by-piece pattern breakdown.
    """
    new = _new_concepts(card, cur)
    K = _keys_module()
    wrap = (lambda text, indent: textwrap.wrap(text, width=width, initial_indent=indent,
                                              subsequent_indent=indent + "   ")
            ) if width else (lambda text, indent: [indent + text])
    symbols, covered = _symbol_lines(card, cur, wrap)
    # VD-48: the SYMBOLS block already says what / and \\ do, with a contrast.
    slash_note = [line for line, pair in zip(SLASH_NOTE, (("/", "separator"), ("\\", "special")))
                  if pair not in covered]
    # Memory plan §2: a family missed in the deck lately gets a REMEMBER line.
    remember = _deck_module().remember_lines(card, cur or {}, DECK_WEAK, wrap)
    if not new:
        # A reinforcement lesson reuses an earlier idea: remind, do not alert.
        lines = []
        if card.get("show_recipe"):
            lines += _substitute_anatomy_lines(card, wrap, "REMEMBER · HOW TO READ IT", width)
        return remember + lines + symbols
    lines = ["★ NEW CONCEPT ALERT · %d new idea%s · %s" % (
        len(new), "" if len(new) == 1 else "s",
        "Ctrl-W W, then scroll to read all" if width and width <= 66 else "read before editing")]
    taught = []
    for family, meaning in new:
        base = family.replace('"{reg}', "")
        teach = K.FAMILY_TEACH.get(base) or K.FAMILY_TEACH.get(base.replace("[count]", "")) or meaning
        # VD-48: u and Ctrl-r share one teaching line; print it once.
        if teach in [t for t, _f in taught]:
            continue
        taught.append((teach, family))
    for number, (teach, family) in enumerate(taught, 1):
        lines += wrap("%d. %s" % (number, teach), "  ")
        example = K.example_for(family)
        if example:
            lines += wrap("example: " + example, "     ")
    if card.get("show_recipe"):
        lines += _substitute_anatomy_lines(card, wrap, "HOW TO READ IT", width)
    return lines + remember + symbols


def _key_teaching(card, width=None, cur=None):
    """VD-13: teach how the needed keys work; reveal the exact answer only when shown.

    With the curriculum, a family that no earlier guided lesson displayed is
    marked NEW and taught with a worked example on neutral text, so no lesson
    silently demands a command the learner has never seen.
    """
    strings = _card_key_strings(card)
    if not strings:
        return []
    K = _keys_module()
    clip = (lambda text: _clip(text, width)) if width else (lambda text: text)
    shown_before = None if card.get("show_recipe") else _families_shown_before(cur, card)
    trivial = {"j", "k", "h", "l", "[count]j", "[count]k", "[count]h", "[count]l"}
    new_lines = []
    if shown_before is not None:
        for keys in strings[:1]:
            for family, _meaning in K.families(keys):
                if family in shown_before or family in trivial:
                    continue
                teach = K.FAMILY_TEACH.get(family.replace('"{reg}', "")) or \
                    K.FAMILY_TEACH.get(family.replace('"{reg}', "").replace("[count]", ""))
                example = K.example_for(family)
                if teach and ("  NEW  " + teach) not in new_lines:
                    new_lines.append("  NEW  " + teach)
                    if example:
                        new_lines.append("       example: " + example)
    if card.get("show_recipe"):
        lines = ["THE RECIPE, KEY BY KEY"]
        lines += ["  " + clip(line) for line in K.explain_lines(strings[0])]
        return lines
    lines = ["HOW THE KEYS YOU NEED WORK  (the exact answer stays hidden)",
             "  " + clip(K.GRAMMAR)]
    seen = []
    for keys in strings:
        for line in K.teach_lines(keys):
            if line not in seen:
                seen.append(line)
    lines += ["  " + clip(line) for line in seen]
    return lines


def _answer_breakdown(card, width=None):
    """VD-13: after an attempt, the answer split into commands with meanings."""
    keys = card.get("expected") or ""
    if not keys:
        return []
    K = _keys_module()
    lines = ["THE ANSWER, KEY BY KEY"]
    for line in K.explain_lines(keys):
        lines.append("  " + (_clip(line, width) if width else line))
    for method in card.get("method_alternatives", []):
        if method.get("keys") and method["keys"] != keys:
            lines.append("  or (%s):" % method.get("label", "other method"))
            lines += ["    " + (_clip(line, width - 2) if width else line)
                      for line in K.explain_lines(method["keys"])]
    return lines


def _bar(done, total, width=10):
    """Readability audit #5: a module bar such as ▕███░░░░░░░▏."""
    filled = 0 if not total else round(width * min(done, total) / total)
    return "▕" + "█" * filled + "░" * (width - filled) + "▏"


def _progress_line(cfg, progress, card):
    cell = progress["modules"][card["module_id"]]
    stage_id = card["stage_owner"]
    stage = progress["stages"][stage_id]
    streak, best, total = _legacy_streak(cfg.state)
    flame = " 🔥" if streak >= 3 else ""
    level, title, into, needed = _level(progress["xp"])
    return ("PROGRESS  %s %d/%d %s  ·  %s %d/%d %s  ·  XP %d  ·  LEVEL %d %s %d/%d  ·  today %d/%d  ·  streak %d day%s%s  ·  best %d  ·  %d drill%s all time" % (
        stage_id, stage["done"], stage["total"], stage["state"],
        card["module_id"], cell["done"], cell["total"], _bar(cell["done"], cell["total"]),
        progress["xp"], level, title, into, needed,
        _legacy_today(cfg.state), cfg.target, streak, "" if streak == 1 else "s",
        flame, best, total, "" if total == 1 else "s"))


def _legacy_teaching(card):
    """Return de-duplicated legacy key, source, and concept teaching payloads."""
    keys = []
    sources = []
    concepts = []
    seen_concepts = set()
    for lesson in card.get("legacy_lessons", []):
        for line in lesson.get("keys", []):
            if line not in keys:
                keys.append(line)
        source = "%s · %s" % (lesson["id"], lesson["source"])
        if source not in sources:
            sources.append(source)
        concept_id = lesson.get("concept_id")
        if concept_id not in seen_concepts:
            seen_concepts.add(concept_id)
            concepts.append((lesson.get("concept_title", concept_id),
                             lesson.get("paradigm", "")))
    return keys, sources, concepts


def _compact_target_lines(card, width=66):
    """Place equal-height animation frames side by side in a short brief."""
    target = card.get("target", [])
    slices = card.get("frame_slices", [])
    if (not slices or sum(slices) != len(target) or len(set(slices)) != 1
            or len(slices) < 2):
        return ["  │" + line for line in target]
    frames = []
    start = 0
    for size in slices:
        frames.append(target[start:start + size])
        start += size
    if card.get("kind") == "module_reward":
        # Eight complete poses must not disappear behind horizontal clipping.
        # Lesson scrolling exposes each separately labelled canonical plate.
        return [line for index, frame in enumerate(frames, 1)
                for line in ["FRAME %02d" % index, *["  │" + row for row in frame]]]
    rows = []
    # Readability audit #4: pad each frame to its own width so the frame
    # separators stay in one column and the frames read as registered.
    widths = [max(len(line) for line in frame) for frame in frames]
    for row_number in range(slices[0]):
        row = "   ".join("│" + frame[row_number].ljust(width)
                         for frame, width in zip(frames, widths))
        # Do not use prose clipping here: textwrap collapses runs of spaces,
        # which would silently destroy fixed-width registration in TARGET.
        available = width - 2
        if len(row) > available:
            row = row[:max(0, available - 1)] + "…"
        rows.append("  " + row)
    return rows


def _recipe_shape(card, width=66):
    if not card.get("show_recipe", card.get("show_target", True)):
        return None
    keys = card.get("expected") or ""
    if not keys:
        return None
    if card.get("key_shape"):
        return "SHAPE  " + card["key_shape"]
    K = _keys_module()
    rows = K.anatomy(keys, width)
    if rows:
        for index, line in enumerate(rows):
            if line.strip().lower().startswith("shape"):
                return "SHAPE  " + " ".join(row.strip() for row in rows[index:]).split(":", 1)[1].strip()
    if K.substitute_anatomy(keys):
        return "SHAPE  :{where}s/{find}/{replace}/{flags}"
    return None


def _reminder_matches_recipe(reminder, expected):
    """Drop authored generic reminders whose command is outside this recipe."""
    reminder = str(reminder)
    expected = str(expected or "")
    checks = (
        ("/pattern", "/" in expected and "<CR>" in expected),
        ("f*", "f*" in expected),
        ("g-/g+", "g-" in expected or "g+" in expected),
        (":earlier", ":earlier" in expected),
        ("R enters", "R" in expected),
        ("current-line selector", ":s" in expected),
    )
    return all(marker not in reminder or present for marker, present in checks)


def _brief_key_reminders(card):
    """Retain only keys this step actually uses; never sibling lesson prose."""
    expected = card.get("expected") or ""
    if card.get("key_vocabulary"):
        return [row for row in card["key_vocabulary"]
                if _reminder_matches_recipe(row, expected)]
    K = _keys_module()
    rows = []
    for family, meaning in K.families(expected):
        base = family.replace('"{reg}', "")
        reminder = K.FAMILY_TEACH.get(base) or K.FAMILY_TEACH.get(
            base.replace("[count]", "")) or meaning
        if reminder not in rows and _reminder_matches_recipe(reminder, expected):
            rows.append(reminder)
    return rows


def _scoped_hint(card):
    """Keep hidden-card guidance about this operation, not a generic sibling."""
    hint = str(card.get("hint") or "").strip()
    expected = card.get("expected") or ""
    if not hint:
        return "; then ".join(why for _keys, why in card.get("recipe", []))
    if "Vim toolbox" in hint:
        clauses = re.split(r"(?<=[.!?])\s+", hint)
        kept = [clause for clause in clauses if _reminder_matches_recipe(clause, expected)]
        hint = " ".join(kept).strip()
    if "/pattern" in hint and "/" not in expected:
        hint = hint.replace("/pattern<CR> searches; ", "")
    if "f*" in hint and "f*" not in expected:
        hint = hint.replace("f*", "the visible landmark")
    return hint or "Follow the scoped operation described in DO THIS."


def _write_session_lesson(cfg, cur, progress, card):
    """Today's task first; repeated reference material in a closed MORE fold."""
    note_feedback_context(revision=cur.get("revision"), card_id=card.get("id"),
                          card_title=card.get("title"), module_id=card.get("module_id"),
                          question_id=None, answer=None, answer_correct=None,
                          lesson_result=None, screen="lesson")
    lesson = _paths(cfg)["sessions"] / card["project_id"] / (card["id"] + ".txt")
    context = _lesson_context(cur, card)
    compact = (__import__("sys").stdout.isatty()
               and shutil.get_terminal_size((80, 24)).lines < 38)
    width = 66 if compact else 78
    show_target = card.get("show_target", True)
    show_recipe = card.get("show_recipe", show_target)
    hint = _scoped_hint(card)
    if "choose the smallest normal-mode operation" in hint:
        hint = "use the commands explained under HOW THE KEYS YOU NEED WORK"
    cell = progress["modules"][card["module_id"]]
    level, _title, into, needed = _level(progress["xp"])
    header = _wrap_prose("PROGRESS  %s · %s %s %d/%d · Lv%d %d/%d" % (
        card["id"], card["module_id"], _bar(cell["done"], cell["total"], 8),
        cell["done"], cell["total"], level, into, needed), width)
    header += _wrap_prose(card["prompt"], width, indent="DO THIS · ",
                          subsequent="          ")
    banner = _new_concept_banner(card, cur, width)
    if banner:
        header += banner.splitlines()
    if not show_recipe and not show_target:
        header.append("HINT · Exact keystrokes stay hidden until evaluation.")
    if show_target:
        header.append("TARGET" if show_recipe else
                      "TARGET · HINT: Exact keystrokes stay hidden until evaluation.")
        header += (_compact_target_lines(card, width) if compact else
                   ["  │" + row for row in card["target"]])
    if show_recipe:
        if compact:
            header += _wrap_prose("RECIPE  " + " → ".join(
                keys for keys, _why in card.get("recipe", [])), width)
        else:
            header.append("COMMAND RECIPE")
            for keys, why in card.get("recipe", []):
                header += _wrap_prose("%-14s %s" % (keys, why), width, indent="  ")
        shape = _recipe_shape(card, width)
        if shape:
            header += _wrap_prose(shape, width)
    else:
        header += _wrap_prose(hint, width, indent="  ")
    header += _new_concept_alert(card, cur, width=width)
    header += _key_teaching(card, width=width, cur=cur)
    header += ["", "── MORE · za opens/closes · / finds ──"]
    header += _wrap_prose(card["title"], width)
    header += _wrap_prose(card["skill"], width, indent="SKILL  ", subsequent="       ")
    header += ["WHY THIS EXISTS"]
    for line in context["why"]:
        header += _wrap_prose(line, width, indent="  ")
    header += ["WHAT THIS LESSON BUYS YOU",
               *_wrap_prose(context["buys"], width, indent="  "),
               "KEYS WORTH KEEPING"]
    reminders = _brief_key_reminders(card)
    # Hidden retrieval must not leak the exact answer through a reminder.
    if not show_recipe:
        reminders = [row for row in reminders if card.get("expected", "") not in row]
    for row in reminders:
        header += _wrap_prose(row, width, indent="  ")
    _keys, sources, concepts = _legacy_teaching(card)
    header += ["WHERE THIS METHOD COMES FROM",
               *_wrap_prose(context["source"], width, indent="  ")]
    for source in sources:
        header += _wrap_prose("LEGACY SOURCE  " + source, width)
    for title, paradigm in concepts:
        header += ["LEGACY VIM CONCEPT", *_wrap_prose(title, width, indent="  ")]
        for row in paradigm.splitlines():
            if row.strip():
                header += _wrap_prose(row, width, indent="  ")
    header += ["READING THE RECIPE",
               "  <CR> Enter · <Esc> Escape · <C-r> hold Ctrl, press r",
               "  <C-k>.M middle-dot digraph · Ctrl-K, then . then M",
               "  {char} any glyph · {N} any number · no braces typed",
               "SUBMIT / STUCK",
               "  :wq submits · :q! exits without submission",
               "  Ctrl-W W switches between the brief and the art.",
               "BASIC HELP",
               "  F1 cheat sheet · Space waits for WhichKey · u undo",
               "COPY / PASTE",
               "  Drag selects · Cmd-C copies · y copies a question · Cmd-V pastes"]
    _write_lines_atomic(lesson, header)
    return lesson


def _checkpoint(cfg, card, path, suffix):
    dest = path.parent / "checkpoints"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest / (card["id"] + "-" + suffix + ".txt"))


def _hash_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _update_manifest(cur, card, path):
    # A transfer is deliberately an unseen, separate artifact.  It must not
    # become the module's playable strip merely because it was verified last.
    manifest_name = ("transfer-manifest.json" if card.get("artifact") == "transfer"
                     else "animation-%s-manifest.json" % card["id"]
                     if card.get("artifact") == "animation-study" else "manifest.json")
    manifest_path = path.parent / manifest_name
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        manifest = {"schema": "vim-daily/project@1", "project_id": card["project_id"],
                    "module_id": card["module_id"], "history": [], "source_refs": []}
    entry = {"card_id": card["id"], "at": _now().isoformat(),
             "sha256": _hash_file(path),
             "rows": len(_read_lines(path, card.get("preserve_trailing_whitespace", False)))}
    if card.get("animation"):
        entry["animation"] = card["animation"]
    if card.get("duplicate_frames"):
        entry["duplicate_frames"] = card["duplicate_frames"]
    manifest["history"] = [row for row in manifest.get("history", []) if row.get("card_id") != card["id"]]
    manifest["history"].append(entry)
    manifest["current_card"] = card["id"]
    manifest["curriculum_revision"] = cur["revision"]
    manifest["artifact"] = path.name
    manifest["artifact_sha256"] = entry["sha256"]
    manifest["row_count"] = entry["rows"]
    if card.get("animation"):
        manifest["animation"] = card["animation"]
    if card.get("duplicate_frames"):
        manifest["duplicate_frames"] = card["duplicate_frames"]
    manifest["updated_at"] = entry["at"]
    manifest["source_refs"] = sorted(set(manifest.get("source_refs", []) + [card["source_ref"]]))
    fd, tmp = tempfile.mkstemp(prefix="manifest-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=1, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, manifest_path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _write_compare(card, path):
    methods = card.get("method_alternatives")
    if not methods:
        return None
    compare_path = path.parent / "compare.txt"
    lines = ["Compare methods — %s" % card["id"], "", "Same required buffer outcome:"]
    lines += ["  │" + line for line in card["target"]]
    lines += ["", "%s:" % methods[0]["label"],
              "  %-18s %s" % (methods[0]["keys"], methods[0]["why"]),
              "", "%s:" % methods[1]["label"],
              "  %-18s %s" % (methods[1]["keys"], methods[1]["why"]),
              "", "Choose by task shape, edit scope, repeatability, and error risk—not key count alone."]
    fd, tmp = tempfile.mkstemp(prefix="compare-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, compare_path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return compare_path


def _legacy_credit(cfg, card_id):
    """Keep the existing streak/cap ledger working without granting v1 mastery."""
    if getattr(cfg, "practice", False):
        return
    now = _now()
    path = Path(cfg.state) / (now.date().isoformat() + ".log")
    row = "completed_at=%s\tdrill=%s\tskill=v2\tconcept=project\tid=%s\tattempts=1\n" % (
        now.strftime("%Y-%m-%dT%H:%M:%S%z"), card_id, card_id)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, row.encode("utf-8"))
    finally:
        os.close(fd)


ATTEMPT_RESULT = "attempt"


def _legacy_attempt(cfg, card_id):
    """Record a failed v2 attempt as daily practice (VD-11/VD-13).

    The ``result=`` field keeps the row out of all-time completion and legacy
    mastery readers. ``_legacy_today`` deliberately includes ``attempt`` rows,
    because effort counts toward the daily 12 even when mastery/XP does not.
    """
    if getattr(cfg, "practice", False):
        return
    now = _now()
    path = Path(cfg.state) / (now.date().isoformat() + ".log")
    row = ("completed_at=%s\tdrill=%s\tskill=v2\tconcept=project\tid=%s"
           "\tattempts=1\tresult=%s\n" % (
               now.strftime("%Y-%m-%dT%H:%M:%S%z"), card_id, card_id, ATTEMPT_RESULT))
    Path(cfg.state).mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, row.encode("utf-8"))
    finally:
        os.close(fd)


class _TypedInputTokens(list):
    """Decoded physical keys with the Vim mode observed for each token.

    The ordinary keylog path intentionally remains a plain list.  A typed
    receipt is different: its mode is evidence, not a hint that may be
    reconstructed from the key characters after a state-changing Ex command.
    """

    def __init__(self, tokens, modes):
        super().__init__(tokens)
        self.modes = list(modes)
        if len(self) != len(self.modes):
            raise ValueError("typed-input token/mode length mismatch")


def _without_brief_navigation(typed):
    """Remove keystrokes used only to inspect the tutor's read-only split."""
    out, out_modes, index = [], [], 0
    modes = getattr(typed, "modes", None)
    while index < len(typed):
        # VD-13: the brief is now reached with <C-w>w (or <C-w>h in the wide
        # layout); keys typed there (scrolling, /search) are not art edits.
        for go, back in ((["<C-w>", "w"], ["<C-w>", "w"]),
                         (["<C-w>", "h"], ["<C-w>", "l"])):
            if typed[index:index + 2] == go:
                end = index + 2
                while end < len(typed) and typed[end:end + 2] != back:
                    end += 1
                if typed[end:end + 2] == back:
                    index = end + 2
                    break
        else:
            go = None
        if go is not None:
            continue
        if typed[index:index + 2] == ["<C-w>", "k"]:
            end = index + 2
            while end < len(typed) and typed[end:end + 2] != ["<C-w>", "j"]:
                end += 1
            if typed[end:end + 2] == ["<C-w>", "j"]:
                index = end + 2
                continue
        out.append(typed[index])
        if modes is not None:
            out_modes.append(modes[index])
        index += 1
    return _TypedInputTokens(out, out_modes) if modes is not None else out


def _typed_input_tokens(cfg, receipt):
    """Decode the nonce-validated pre-mapping receipt, not mapping replay."""
    if receipt is None:
        return None
    # A legacy outer cursor receipt predates the typed-input field.  Keep its
    # old scriptout fallback, but fail closed for a fresh-shaped receipt that
    # has an input list with a missing/wrong schema.
    if receipt.get("input_schema") != "vim-daily/typed-input@1":
        return [] if "input" in receipt else None
    rows = receipt.get("input")
    if not isinstance(rows, list):
        return []
    try:
        tokens, modes = [], []
        previous = None
        for row in rows:
            if (not isinstance(row, dict) or not isinstance(row.get("mode"), str)
                    or not isinstance(row.get("typed_hex"), str)
                    or not re.fullmatch(r"(?:[0-9a-f]{2})+", row["typed_hex"])):
                return []
            chunk = bytes.fromhex(row["typed_hex"])
            # WhichKey re-feeds operator keys with the typed flag. Native dd
            # has modes n,no; a genuine following d starts in n, not no. Two
            # identical doubled-operator endings both reported in no therefore
            # describe one pending operation's replay, not two typed commands.
            # Never deduplicate Normal-mode d, text, counts or compound motions.
            current = (row["mode"], chunk)
            if (previous == current and row["mode"].startswith("no")
                    and chunk in (b"d", b"y", b"c", b">", b"<", b"=")):
                continue
            decoded = cfg.decode_keylog(chunk)
            if not isinstance(decoded, list):
                return []
            tokens.extend(decoded)
            modes.extend([row["mode"]] * len(decoded))
            previous = current
        return _TypedInputTokens(tokens, modes)
    except (ValueError, TypeError):
        return []


def _typed_input_required(cfg):
    """Fresh Neovim attempts require the pre-mapping receipt contract."""
    name = os.path.basename(str(getattr(cfg, "editor", ""))).lower()
    if not (name.startswith("nvim") or name == "neovide"):
        return False
    # Test/embedding adapters may intentionally provide a legacy editor
    # callback while retaining ``editor='nvim'`` in their fixture config.  The
    # production callback is the gate's own run_editor function; only that
    # fresh Neovim transport can claim the typed-input contract automatically.
    callback = getattr(cfg, "run_editor", None)
    source = getattr(getattr(callback, "__code__", None), "co_filename", "")
    return Path(source).name == "vim-daily-gate"


def _attempt_replay(cfg, card, keylog, before, got, receipt=None,
                    require_typed_input=False):
    """Return the visible actual-vs-taught key table for one edit attempt."""
    try:
        typed = _without_brief_navigation(cfg.decode_keylog(Path(keylog).read_bytes()))
    except OSError:
        typed = []
    physical = _typed_input_tokens(cfg, receipt)
    typed_contract = (receipt is not None
                      and receipt.get("input_schema") == "vim-daily/typed-input@1"
                      and isinstance(receipt.get("input"), list))
    if physical is not None:
        typed = _without_brief_navigation(physical)
    elif require_typed_input:
        # Never grade a fresh Neovim attempt from -w: personal mappings can
        # rewrite that stream.  An empty typed stream is deliberately
        # evidence-poor and therefore cannot satisfy a method requirement.
        typed = _TypedInputTokens([], [])
    expected = cfg.tokenize(card.get("expected", "")) if cfg.tokenize else []
    if cfg.keystroke_table:
        table = cfg.keystroke_table(typed, expected, width=24)
    else:
        table = ["  actual: %s" % ("".join(typed) or "(none)"),
                 "  taught: %s" % (card.get("expected") or "(none)")]
    return {"type": "edit", "keylog": str(keylog), "table": table, "actual_tokens": typed,
            "input_source": ("typed-input-receipt" if physical is not None and typed_contract else
                              "typed-input-receipt-invalid" if physical is not None else
                              "typed-input-missing" if require_typed_input
                              else "scriptout-legacy"),
            "actual_keys": "".join(typed) or "(none)",
            "taught_keys": "".join(expected) or "(none)",
            "before": before, "got": got,
            "target": _card_lines(card, card["target"])}


def _next_attempt_keylog(directory, stem):
    """Allocate a durable per-attempt keylog path without overwriting history."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    pattern = re.compile(r"^%s-attempt-(\d+)\.log$" % re.escape(stem))
    highest = 0
    for path in directory.glob(stem + "-attempt-*.log"):
        match = pattern.match(path.name)
        if match:
            highest = max(highest, int(match.group(1)))
    return directory / ("%s-attempt-%04d.log" % (stem, highest + 1))


def _latest_attempt_keylog(directory, stem):
    """Return the newest durable keylog, falling back to the legacy filename."""
    directory = Path(directory)
    paths = sorted(directory.glob(stem + "-attempt-*.log"))
    if paths:
        return paths[-1]
    legacy = directory / (stem + ".log")
    return legacy if legacy.exists() else None


def _keylog_fields(path):
    path = Path(path)
    if not path.exists():
        return {}
    fields = {"keylog": str(path), "keylog_sha256": _hash_file(path)}
    contract = path.with_suffix(".contract.json")
    if contract.is_file():
        fields.update({"attempt_contract": str(contract),
                       "attempt_contract_sha256": _hash_file(contract)})
    input_receipt = path.with_suffix(".cursor.json")
    if input_receipt.is_file():
        fields.update({"input_receipt": str(input_receipt),
                       "input_receipt_sha256": _hash_file(input_receipt)})
    return fields


class _CursorReceiptEnv:
    """Context manager keeping the fresh cursor-receipt environment live."""

    def __init__(self, path, keylog, attempt):
        self.path = path
        self.keylog = keylog
        self.attempt = attempt
        self.receipt = Path(keylog).with_suffix(".cursor.json")
        self.token = "%s:%s:%s:%s" % (Path(path).resolve(), os.getpid(), attempt,
                                     secrets.token_hex(16))
        self.previous = {}

    def __enter__(self):
        try:
            self.receipt.unlink()
        except OSError:
            pass
        for name, value in (("VIM_DAILY_CURSOR_RECEIPT", str(self.receipt.resolve())),
                            ("VIM_DAILY_CURSOR_ATTEMPT", self.token)):
            self.previous[name] = os.environ.get(name)
            os.environ[name] = value
        return self

    def __exit__(self, *_):
        for name, value in self.previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def _read_cursor_receipt(receipt, token, path):
    """Accept only a fresh receipt bound to this attempt and art buffer."""
    try:
        data = json.loads(Path(receipt).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    expected_path = str(Path(path).resolve())
    def same_art_path(value):
        try:
            return str(Path(value).resolve()) == expected_path
        except (OSError, TypeError, ValueError):
            return False
    if (data.get("schema") != "vim-daily/cursor-receipt@1"
            or data.get("attempt") != token
            or data.get("event") != "VimLeavePre"
            or not same_art_path(data.get("artifact"))
            or not same_art_path(data.get("buffer_path"))):
        return None
    cursor = data.get("cursor")
    if (not isinstance(cursor, dict) or type(cursor.get("row")) is not int
            or type(cursor.get("column")) is not int
            or type(data.get("display_column")) is not int
            or min(cursor["row"], cursor["column"], data["display_column"]) < 1):
        return None
    return data


def _cursor_goal_error(card, replay):
    """Return a visible failure when a navigation card lacks final cursor proof."""
    goal = card.get("cursor_goal")
    if not goal:
        return None
    receipt = replay.get("cursor_receipt")
    if not receipt:
        return ("✓ Your result matches the target. ✗ Not counted yet: no fresh art-buffer "
                "cursor receipt was captured at submission; navigation credit is withheld.")
    row = receipt["cursor"].get("row")
    column = receipt.get("display_column")
    if row != goal.get("row") or column != goal.get("column"):
        return ("✓ Your result matches the target. ✗ Not counted yet: final art cursor was "
                "row %s, display column %s; expected row %s, display column %s." % (
                    row, column, goal.get("row"), goal.get("column")))
    return None


def _recovery_input_receipt(keylog, path, card, before):
    """Recover typed evidence only through its original owning contract."""
    try:
        contract = json.loads(Path(keylog).with_suffix(".contract.json").read_text())
    except (OSError, ValueError, TypeError):
        return None
    if (not isinstance(contract, dict)
            or contract.get("schema") != "vim-daily/attempt-contract@1"
            or contract.get("card") != card or contract.get("before") != before
            or not isinstance(contract.get("cursor_attempt"), str)
            or not contract["cursor_attempt"]):
        return None
    return _read_cursor_receipt(Path(keylog).with_suffix(".cursor.json"),
                                contract["cursor_attempt"], path)


def _executed_ex_commands(tokens):
    """Return executed Ex command text after applying common cmdline edits."""
    commands = []
    tokens = list(tokens)
    index = 0
    while index < len(tokens):
        if tokens[index] != ":":
            index += 1
            continue
        start = index
        index += 1
        command = []
        while index < len(tokens):
            token = tokens[index]
            if token == "<CR>":
                commands.append((start, index + 1, "".join(command)))
                index += 1
                break
            if token in ("<Esc>", "<C-c>"):
                index += 1
                break
            if token in ("<BS>", "<C-h>"):
                if command:
                    command.pop()
            elif token == "<C-u>":
                command = []
            elif token == "<C-w>":
                while command and command[-1].isspace():
                    command.pop()
                while command and not command[-1].isspace():
                    command.pop()
            elif len(token) == 1:
                command.append(token)
            index += 1
        else:
            break
    return commands


def _is_submit_ex(command):
    """True when every command segment only saves and/or leaves Neovim."""
    submit_names = {
        "w", "write", "up", "update", "wa", "wall",
        "q", "quit", "qa", "qall", "cq", "cquit",
        "wq", "wqa", "x", "xit", "exit",
    }
    segments = [segment.strip() for segment in command.split("|")]
    if not segments or any(not segment for segment in segments):
        return False
    for segment in segments:
        # Arguments are not a save operation.  In particular, `:write !cmd`
        # is a shell command whose argument text must remain evidence; treating
        # it as cleanup let arbitrary command-line text satisfy an edit path.
        match = re.match(r"^([A-Za-z]+)!?$", segment)
        if not match or match.group(1).lower() not in submit_names:
            return False
    return True


def _edit_tokens_without_submit(tokens):
    """Remove save/quit Ex commands and Normal-mode exit commands anywhere."""
    tokens = list(tokens)
    removed = set()
    for start, end, command in _executed_ex_commands(tokens):
        if _is_submit_ex(command):
            removed.update(range(start, end))
    out = []
    index = 0
    while index < len(tokens):
        if index in removed:
            index += 1
            continue
        if tokens[index:index + 2] in (["Z", "Z"], ["Z", "Q"]):
            index += 2
            continue
        out.append(tokens[index])
        index += 1
    return out


def _semantic_tokens(tokens):
    """Project captured keys into normal, insert, and executed-Ex events.

    Required paths are authored as operations, not as arbitrary characters in
    a command-line argument or inserted payload.  This projection keeps the
    exact method-path tolerance for real navigation, mappings, corrections,
    and recovery while making mode boundaries observable.
    """
    projected = []
    source_modes = getattr(tokens, "modes", None)
    mode = "normal"
    argument = None
    operator = None
    prefix = None
    text_object = False
    recording = False
    visual = None
    index = 0
    # ``list(tokens)`` below intentionally keeps ordinary callers unchanged,
    # but a typed receipt carries a parallel mode ledger.  Preserve it across
    # that copy so state-changing Ex commands cannot make later Insert bytes
    # look like Normal commands.
    tokens = list(tokens)
    recorded_modes = source_modes

    def recorded_mode_at(position):
        if recorded_modes is None or position >= len(recorded_modes):
            return None
        value = recorded_modes[position]
        if not isinstance(value, str):
            return None
        if value.startswith("i"):
            return "insert"
        if value.startswith("Rv"):
            return "virtual_replace"
        if value.startswith("R"):
            return "replace"
        if value[:1] in ("v", "V", "s", "S", "\x16", "\x13"):
            return "visual"
        if value.startswith("n"):
            return "normal"
        if value in ("r", "rm", "r?"):
            return "argument"
        # c/t/prompt states cannot become Normal commands merely because
        # a mapping or Ex operation entered them without a typed delimiter.
        return "unattributed"

    while index < len(tokens):
        token = tokens[index]
        observed = recorded_mode_at(index)
        if observed == "insert":
            mode = "insert"
            argument = None
            operator = prefix = None
            text_object = False
            visual = None
        elif observed in ("replace", "virtual_replace"):
            # Neovim reports R while consuming the single-character Normal
            # r argument too. Only an already witnessed r owns that literal;
            # an R entered by Ex/mapping remains Replace-mode payload.
            if not (observed == "replace" and argument in (
                    "replace", "digraph-first", "digraph-second")):
                mode = observed
                argument = None
                operator = prefix = None
                text_object = False
                visual = None
        elif observed == "visual":
            if mode != "normal":
                argument = operator = prefix = None
                text_object = False
            mode = "normal"
            # A Visual register/prefix spans callbacks. Resetting it for
            # every selected-mode byte loses the genuine "ay operation.
            visual = visual or True
        elif observed == "normal" and mode in ("insert", "replace", "virtual_replace"):
            mode = "normal"
            operator = prefix = None
            text_object = False
        elif observed == "unattributed" or (observed == "argument" and not argument):
            argument = operator = prefix = None
            text_object = False
            visual = None
            projected.append(("unattributed", token))
            index += 1
            continue
        if argument:
            projected.append(("argument", token))
            if argument == "replace" and token == "<C-k>":
                argument = "digraph-first"
            elif argument == "digraph-first":
                argument = "digraph-second"
            elif argument == "change-motion":
                mode = "insert"
                argument = None
            else:
                argument = None
            index += 1
            continue
        if mode == "normal" and token in (":", "/", "?"):
            command = []
            end = index + 1
            while end < len(tokens):
                value = tokens[end]
                if value == "<CR>":
                    # Case and pattern spaces are semantically significant.
                    text = "".join(command).strip()
                    if token == ":" and visual:
                        # Visual ':' supplies this range before the typed text.
                        # ':earlier' in that context is not the taught Normal
                        # history command, even when its letters are identical.
                        text = "'<,'>" + text
                        visual = None
                    projected.append(("ex" if token == ":" else "search", text))
                    index = end + 1
                    break
                if value in ("<Esc>", "<C-c>"):
                    index = end + 1
                    break
                if value in ("<BS>", "<C-h>"):
                    if command:
                        command.pop()
                elif value == "<C-u>":
                    command = []
                elif value == "<C-w>":
                    while command and command[-1].isspace():
                        command.pop()
                    while command and not command[-1].isspace():
                        command.pop()
                elif len(value) == 1:
                    command.append(value)
                end += 1
            else:
                index = len(tokens)
            continue
        if mode == "normal" and visual and token in ("u", "U"):
            projected.append(("visual", token))
            visual = None
            index += 1
            continue
        projected.append((mode, token))
        if mode in ("insert", "replace", "virtual_replace"):
            if token in ("<Esc>", "<C-c>"):
                mode = "normal"
        elif token in ("<Esc>", "<C-c>"):
            operator = prefix = None
            text_object = False
            visual = None
        elif visual and token in ("d", "y", "c", "x", "p", "P", "I", "A", "J", "~", ">", "<", "=", "r"):
            visual = None
            operator = prefix = None
            if token in ("c", "I", "A"):
                mode = "insert"
            elif token == "r":
                argument = "replace"
        elif token in ("v", "V", "<C-v>"):
            visual = None if visual == token else token
        elif text_object:
            text_object = False
            if operator == "c":
                mode = "insert"
            operator = None
        elif operator:
            if token.isdigit():
                pass
            elif token in ("i", "a"):
                text_object = True
            elif token in ("f", "F", "t", "T"):
                argument = "change-motion" if operator == "c" else "motion"
                operator = None
            else:
                if operator == "c":
                    mode = "insert"
                operator = None
        elif prefix:
            if prefix == "g" and token in ("R", "i", "I"):
                mode = "virtual_replace" if token == "R" else "insert"
            elif prefix == "z" and token == "y" and visual:
                visual = None
            elif prefix == "g" and token == "v":
                visual = "v"
            elif prefix == "g" and token in ("~", "u", "U"):
                operator = "case"
            prefix = None
        elif token in ("g", "z", "<C-w>"):
            prefix = token
        elif token == "q":
            if not recording:
                argument = "register"
            recording = not recording
        elif token in ("r", "f", "F", "t", "T", '"', "m", "'", "`", "@"):
            argument = "replace" if token == "r" else "literal"
        elif token in ("d", "c", "y"):
            operator = token
        elif token in ("i", "I", "a", "A", "o", "O", "C", "S", "s", "R"):
            mode = "replace" if token == "R" else "insert"
        index += 1
    return projected


def _semantic_command_events(events):
    """Keep command prefixes and their arguments as one evidence event.

    ``gg`` followed by ``+`` is not ``g+``. Likewise ``fX`` followed by
    ``r*`` did not practise ``f*``. Harmless events may surround a command,
    but cannot donate characters to construct a command that never ran.
    """
    grouped = []
    index = 0
    events = list(events)
    while index < len(events):
        mode, value = events[index]
        if mode == "normal" and index + 1 < len(events):
            next_mode, next_value = events[index + 1]
            if ((value in ("g", "z", "<C-w>") and next_mode == "normal")
                    or (value in ("r", "f", "F", "t", "T", '"', "m", "'", "`", "@", "q")
                        and next_mode == "argument")):
                grouped.append((mode, value + next_value))
                index += 2
                continue
        grouped.append((mode, value))
        index += 1
    return grouped


def _method_operation_tokens(tokens):
    """Ignore incidental positioning, but retain operator/Visual motions.

    ``j`` before ``dw`` merely reaches the row; ``j`` after ``d`` owns the
    deletion scope. Insert, argument, search and Ex events remain distinct,
    so text which happens to spell a Normal-mode command cannot earn credit.
    """
    events = _semantic_tokens(tokens)
    kept = []
    operator = False
    visual = None
    prefix = None
    for index, (mode, value) in enumerate(events):
        event = (mode, value)
        if mode != "normal":
            kept.append(event)
            if mode == "argument":
                operator = False
            continue
        if value in ("<Esc>", "<C-c>"):
            operator = visual = False
            prefix = None
        elif visual or operator:
            if value in ("d", "y", "c") and visual:
                visual = False
            if not value.isdigit() and value not in ("i", "a", "f", "F", "t", "T"):
                operator = False
        elif prefix:
            if prefix == "g" and value in ("~", "u", "U"):
                operator = True
            prefix = None
        elif value in ("v", "V", "<C-v>"):
            visual = True
        elif value in ("d", "y", "c"):
            operator = True
        elif value in ("g", "z", "<C-w>"):
            prefix = value
        elif value in ("h", "j", "k", "l", "0", "^", "$"):
            # Zero inside a count is not the column-zero motion: 10G must
            # not be weakened to 1G while incidental 0 is ignored.
            if not (value == "0" and index and events[index - 1][0] == "normal"
                    and events[index - 1][1].isdigit()):
                continue
        kept.append(event)
    return _semantic_command_events(kept)


def _method_path_matches(actual, expected, card):
    """C31: command presence, never the order of a worked recipe.

    Commands stay atomic: unrelated ``d`` presses cannot manufacture ``dd``;
    literal Insert/Ex text cannot manufacture a Normal-mode command. Repeating
    a command in the example does not impose a repetition quota on the learner.
    The caller independently checks the exact target and any cursor receipt.
    """
    wanted = set(_method_commands(expected, navigation=card.get("navigation_only", False)))
    used = set(_method_commands(actual, navigation=card.get("navigation_only", False)))
    return bool(wanted) and wanted.issubset(used)


def _method_commands(tokens, *, navigation=False):
    """Mode-bound, complete commands used anywhere in an attempt.

    Text entered in Insert/Replace mode is the artifact, not an additional
    method requirement. Counts and operator motions belong to their command;
    free positioning and selection-size motions do not belong to a recipe.
    """
    events = _semantic_tokens(tokens)
    commands = []
    index = 0
    visual = None
    register = ""
    incidental = {"h", "j", "k", "l", "0", "^", "$"}
    while index < len(events):
        mode, value = events[index]
        if mode in ("ex", "search"):
            commands.append((mode, value))
            if mode == "ex":
                visual = None
                register = ""
            index += 1
            continue
        if mode == "visual":
            commands.append(("normal", "Visual " + value))
            visual = None
            register = ""
            index += 1
            continue
        if mode in ("insert", "replace", "virtual_replace") and value in ("<C-r>", "<C-k>"):
            size = 1 if value == "<C-r>" else 2
            arguments = events[index + 1:index + 1 + size]
            if len(arguments) == size and all(m == mode and len(v) == 1 for m, v in arguments):
                commands.append((mode, value + "".join(v for _m, v in arguments)))
                index += size + 1
                continue
        if mode != "normal":
            index += 1
            continue
        if value in ("<Esc>", "<C-c>"):
            visual = None
            register = ""
            index += 1
            continue
        count = ""
        while (index < len(events) and events[index][0] == "normal"
               and events[index][1].isdigit()
               and (events[index][1] != "0" or count)):
            count += events[index][1]
            index += 1
        if index >= len(events) or events[index][0] != "normal":
            continue
        value = events[index][1]
        index += 1
        if value in ("g", "z", "<C-w>"):
            if index >= len(events) or events[index][0] != "normal":
                continue
            value += events[index][1]
            index += 1
        elif value in ("r", "f", "F", "t", "T", '"', "m", "'", "`", "@", "q"):
            if index < len(events) and events[index][0] == "argument":
                value += events[index][1]
                index += 1
                if value == "r<C-k>":
                    arguments = events[index:index + 2]
                    if len(arguments) != 2 or any(m != "argument" for m, _v in arguments):
                        continue
                    value += "".join(v for _m, v in arguments)
                    index += 2
            elif value != "q":
                continue
        if value.startswith('"'):
            # A register prefix owns the next command; it cannot be combined
            # with a yank/put executed somewhere else in the attempt.
            register = count + value
            continue
        if value in ("v", "V", "<C-v>", "gv"):
            visual = None if visual == value else value
        elif visual and (value in ("d", "y", "c", "x", "p", "P", "I", "A", "J", "~", ">", "<", "=")
                         or value.startswith("r")):
            value = "Visual " + value
            visual = None
        elif visual and value == "zy":
            value = "Visual zy"
            visual = None
        elif visual and value not in incidental:
            # History, g-prefixed and other commands typed in a selection
            # cannot supply their Normal-mode counterparts. Selection-size
            # motions remain incidental; explicit Visual operators above
            # retain their established command spelling.
            value = "Visual " + value
        elif value in ("d", "y", "c", ">", "<", "=", "g~", "gu", "gU"):
            motion = ""
            while (index < len(events) and events[index][0] == "normal"
                   and events[index][1].isdigit()):
                motion += events[index][1]
                index += 1
            if index >= len(events) or events[index][0] != "normal":
                continue
            part = events[index][1]
            index += 1
            if part in ("<Esc>", "<C-c>"):
                continue
            motion += part
            if part in ("i", "a"):
                if index >= len(events) or events[index][0] != "normal":
                    continue
                motion += events[index][1]
                index += 1
            elif part in ("f", "F", "t", "T"):
                if index >= len(events) or events[index][0] != "argument":
                    continue
                motion += events[index][1]
                index += 1
            value += motion
        if value in incidental and not navigation:
            register = ""
            continue
        commands.append(("normal", count + value))
        if register:
            commands.append(("normal", register + count + value))
            register = ""
    return commands


def _linewise_yank_put_matches(tokens, rows):
    """Recognize complete linewise yank and put commands in any order."""
    count = list(str(rows))
    yanks = [count + ["y", "y"]]
    if rows > 1:
        offset = list(str(rows - 1)) if rows > 2 else []
        yanks.extend([
            ["V"] + offset + ["j", "y"],
            ["y"] + offset + ["j"],
        ])
    return any(_method_path_matches(tokens, yank + [put], {})
               for yank in yanks for put in ("p", "P"))


def _normalise_ex(command):
    return re.sub(r"\s+", "", command).lower()


def _mode_text_matches(tokens, mode, text):
    """Attribute an actual Replace/Virtual Replace entry under C31.

    ``text`` is historical example metadata, not a required payload recipe.
    The operator permits taught keys anywhere, including exploration later
    undone; the exact saved target independently checks the resulting art.
    Register/digraph commands still retain their actual input-mode context.
    """
    # The exact saved artifact checks the text. This check only attributes the
    # demonstrated Replace/Virtual Replace operation, not its recipe payload.
    return ("normal", mode) in _method_commands(tokens)


def _method_evidence_matches(method, actual, executed_commands):
    evidence = method.get("evidence") or {}
    kind = evidence.get("kind")
    if kind == "linewise_yank_put":
        return _linewise_yank_put_matches(actual, int(evidence["rows"]))
    if kind == "ex_copy":
        start = int(evidence["start"])
        end = int(evidence["end"])
        destination = str(evidence["destination"])
        accepted = {
            "%d,%dt%s" % (start, end, destination),
            "%d,%dco%s" % (start, end, destination),
            "%d,%dcopy%s" % (start, end, destination),
        }
        return any(command.replace(" ", "") in accepted
                   for mode, command in _semantic_tokens(actual) if mode == "ex")
    if kind == "mode_text":
        return _mode_text_matches(
            actual, str(evidence["mode"]), str(evidence["text"])
        )
    return False


def _method_family(cfg, card, replay):
    """Name a demonstrated comparison method inside an otherwise valid attempt."""
    raw = replay.get("actual_tokens", [])
    actual = raw
    if not actual:
        return None
    executed_commands = [row for row in _executed_ex_commands(raw)
                         if not _is_submit_ex(row[2])]
    for method in card.get("method_alternatives", []):
        expected = cfg.tokenize(method["keys"]) if cfg.tokenize else list(method["keys"])
        # A named comparison method does not require its example line-address
        # route. Exact target equality already verifies where the edits landed.
        wanted = set(_method_commands(expected))
        wanted = {event for event in wanted if not (
            event[0] == "normal" and re.fullmatch(r"(?:[0-9]*G|[0-9]*gg)", event[1]))}
        if ((bool(wanted) and wanted.issubset(set(_method_commands(actual))))
                or _method_evidence_matches(method, actual, executed_commands)):
            return method["label"]
    return None


def _contains_tokens(tokens, wanted):
    """Return true when wanted occurs contiguously in tokens."""
    if not wanted or len(wanted) > len(tokens):
        return False
    return any(tokens[index:index + len(wanted)] == wanted
               for index in range(len(tokens) - len(wanted) + 1))


def _method_goal(card):
    """VD-49: the commands a lesson practises, in the learner's words."""
    K = _keys_module()
    names = []
    for family, _meaning in K.families(card.get("expected", "")):
        if family in ("j", "k", "h", "l", "[count]j", "[count]k", "0", "^", "$",
                      "[count]G", "gg", "<CR>"):
            continue
        base = family.replace('"{reg}', "")
        teach = K.FAMILY_TEACH.get(base) or K.FAMILY_TEACH.get(base.replace("[count]", ""))
        name = teach.split("  ", 1)[0] if teach else base
        if name not in names:
            names.append(name)
    return ", ".join(names) or "the method shown in the recipe"


def _method_miss_message(card, detail=None):
    return ("✓ Target correct. Your result matches the target, but you did not use "
            "the taught command: %s. Press r for an instant retry. Extra, reordered "
            "and exploratory keys are accepted.%s" % (
                (card.get("method_requirement") or {}).get("label") or _method_goal(card),
                (" " + detail) if detail else ""))


def _required_method_error(cfg, card, replay):
    """Grade declared method evidence separately from the final buffer."""
    rule = card.get("method_requirement")
    if not rule:
        return None
    # Declared alternatives still need captured, positively recognized keys.
    # Exact artifact equality is enforced by the caller, never by this helper.
    if _method_family(cfg, card, replay):
        return None
    actual = replay.get("actual_tokens", [])
    focal = _taught_method_paths(card)
    if focal:
        tokenize = cfg.tokenize or _keys_module().tokens
        if any(all(_method_path_matches(actual, tokenize(command), card)
                   for command in path) for path in focal):
            return None
        return _method_miss_message(card)
    exact_paths = [
        cfg.tokenize(keys) if cfg.tokenize else list(keys)
        for keys in rule.get("exact_any_of", [])
    ]
    alternatives = [
        cfg.tokenize(keys) if cfg.tokenize else list(keys)
        for keys in rule.get("any_of", [])
    ]
    required = [
        cfg.tokenize(keys) if cfg.tokenize else list(keys)
        for keys in rule.get("all_of", [])
    ]
    # Legacy exact_any_of is a carrier of example commands, not an exact or
    # ordered transcript contract. All three rule forms use C31 presence.
    captured = replay.get("actual_tokens", [])
    if exact_paths and not any(_method_path_matches(captured, path, card)
                               for path in exact_paths):
        return _method_miss_message(card)
    if alternatives and not any(_method_path_matches(actual, wanted, card) for wanted in alternatives):
        return _method_miss_message(card)
    if required and not all(_method_path_matches(actual, wanted, card) for wanted in required):
        return _method_miss_message(card)
    # C31 forbids rejecting a correct taught-method result for extra keys.
    return None


def _taught_method_paths(card):
    """The card's explicit primitive rule wins over a legacy recipe carrier."""
    rule = card.get("method_requirement") or {}
    if rule.get("all_of"):
        paths = [list(rule["all_of"])]
    else:
        global _METHOD_POLICY
        if _METHOD_POLICY is None:
            _METHOD_POLICY = _sibling_module("method_policy")
        paths = _METHOD_POLICY.taught_paths(card, rule)
    # zy is a Visual-only primitive, not a Normal command. The focal list
    # stores fragments, so supply its block context when interpreting that
    # taught fragment. Actual traces still need a real selection and zy.
    return [["<C-v>zy" if command == "zy" else command for command in path]
            for path in paths]


def _unrecognized_method_message(replay):
    actual = replay.get("actual_tokens", [])
    if not actual:
        return ("The target matches, but no edit keystrokes were captured; "
                "comparison credit requires a demonstrated method.")
    shown = replay.get("actual_keys") or "".join(actual)
    return ("The target matches and edit keys were captured, but neither taught "
            "method was recognized in this attempt. Captured keys: %s" % shown)


def _defer_taught_method(cfg, cur, card, progress, replay):
    """A declared alternate counts; the taught commands return as due practice."""
    if not replay or not replay.get("method_family"):
        return
    actual = replay.get("actual_tokens", [])
    tokenize = cfg.tokenize or _keys_module().tokens
    focal = _taught_method_paths(card) or [[card.get("expected", "")]]
    if any(all(_method_path_matches(actual, tokenize(command), card)
               for command in path) for path in focal):
        return
    D = _deck_module()
    from types import SimpleNamespace
    recorder = SimpleNamespace(append_event=append_event, _now=_now)
    taught = {family for family, _ in _keys_module().families(card.get("expected", ""))}
    method = next((m for m in card.get("method_alternatives", [])
                   if m["label"] == replay["method_family"]), None)
    demonstrated = {family for family, _ in _keys_module().families(method["keys"])} if method else set()
    taught -= demonstrated
    for family in cur.get("deck", {}).get("families", []):
        if taught.intersection(family.get("parser_families", [])):
            for item in family.get("items", []):
                D.record(recorder, cfg, cur, progress, item["id"], "again", "alternate-method")


def _badge_rows(cfg, cur, progress):
    streak = _legacy_streak(cfg.state)[1] if cfg else 0
    cards = {c["id"]: c for c in cur["cards"]}
    ranged = sum(1 for cid in progress.get("passed_cards", [])
                 if any("[range]" in family for family, _meaning in
                        _keys_module().families(cards.get(cid, {}).get("expected") or "")))
    return _dashboard_theme().badge_status(cur, progress, {
        "events": read_events(cfg) if cfg else [], "target": cfg.target if cfg else 12,
        "values": {"best_streak": streak, "commands": len(learned_deck(cur, progress)),
                   "range": ranged},
    })


def _celebrate_progress(cfg, cur, before, progress, before_badges):
    if getattr(cfg, "practice", False):
        return
    T = _dashboard_theme()
    rewards = []
    for badge in _badge_rows(cfg, cur, progress):
        if badge["earned"] and badge["id"] not in before_badges:
            trophy = T.trophy_for(badge["id"]) or {
                "art": [badge.get("icon", badge["glyph"])], "credit": T.TUTOR_CREDIT}
            rewards.append(dict(trophy, title=badge["name"], kind="badge"))
    old_level = _level(before["xp"])[0]
    level, title, _into, _need = _level(progress["xp"])
    if level > old_level:
        rewards.append({"title": "Level %d · %s" % (level, title), "kind": "level",
                        "art": T.avatar_for_level(level), "credit": T.TUTOR_CREDIT})
    if rewards:
        _viewer_module().celebrate(rewards, duration=2.0)


def _legacy_today(state):
    path = Path(state) / (_now().date().isoformat() + ".log")
    try:
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines()
                   if line.strip() and (
                       "result=" not in line or "result=%s" % ATTEMPT_RESULT in line))
    except OSError:
        return 0


def _first_difference(want, got):
    column = 0
    while column < min(len(want), len(got)) and want[column] == got[column]:
        column += 1
    return column


def _cell_width(text):
    import unicodedata
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


def _fit_cells(text, width):
    """Clip or pad ``text`` to ``width`` terminal cells (wide glyphs count 2)."""
    out, used = [], 0
    for ch in text:
        w = _cell_width(ch)
        if used + w > width:
            if out:
                out[-1] = "…" if _cell_width(out[-1]) == 1 else out[-1]
            break
        out.append(ch)
        used += w
    return "".join(out) + " " * max(0, width - used)


def _two_column_replay(left, right, left_label, right_label, *, width=None, max_rows=None,
                       mark_glyph="✗", minimal=False):
    """Render two artifacts row by row: left column vs right column (VD-11)."""
    if width is None:
        width = max(40, shutil.get_terminal_size((80, 24)).columns - 4)
    col = max(8, (width - 9) // 2)
    total = max(len(left), len(right))
    differing = [i for i in range(total)
                 if (left[i] if i < len(left) else None) != (right[i] if i < len(right) else None)]
    first, last = 0, total
    if max_rows and total > max_rows:
        # One leading context row only when there is room for it; a single
        # visible row must be the first differing row, not an unchanged one.
        context = 0 if (minimal or max_rows < 2) else 1
        first = max(0, (differing[0] if differing else 0) - context)
        first = min(first, total - max_rows)
        last = first + max_rows
    lines = ["       %s │ %s" % (_fit_cells(left_label, col), right_label)]
    if first and not minimal:
        lines.append("       … rows 1-%d unchanged" % first)
    for i in range(first, last):
        a = left[i] if i < len(left) else "<missing>"
        b = right[i] if i < len(right) else "<missing>"
        mark = (_paint("✗", "fail") if mark_glyph == "✗" else mark_glyph) if i in differing else " "
        lines.append("%s %3d  %s │ %s" % (mark, i + 1, _fit_cells(a, col), _fit_cells(b, col).rstrip()))
    hidden = [i for i in differing if i >= last]
    if last < total and not minimal:
        lines.append("       … %d more row%s%s" % (
            total - last, "" if total - last == 1 else "s",
            " (%d differ)" % len(hidden) if hidden else ""))
    return lines, differing


def _artifact_replay(replay, completed, *, width=None, max_rows=None, minimal=False):
    before = replay.get("before", [])
    got = replay.get("got", [])
    target = replay.get("target", [])
    if completed:
        lines, _diff = _two_column_replay(before, got, "BEFORE", "AFTER (yours)",
                                          width=width, max_rows=max_rows, mark_glyph="•",
                                          minimal=minimal)
        if not minimal:
            lines.append("  • = row you changed · RESULT exact saved target verified")
        return lines
    lines, differing = _two_column_replay(got, target, "YOURS (what you saved)",
                                          "TARGET (what it should be)",
                                          width=width, max_rows=max_rows, minimal=minimal)
    if differing and not minimal:
        row = differing[0]
        if row < len(target) and row < len(got):
            column = _first_difference(target[row], got[row])
            display_column = _cell_width(target[row][:column]) + 1
            lines.append("  ✗ = row differs · first difference at column %d "
                         "(character %d) of row %d" % (
                             display_column, column + 1, row + 1))
        else:
            lines.append("  ✗ = row differs · row %d is %s" % (
                row + 1, "extra in yours" if row >= len(target) else "missing from yours"))
    return lines


def _print_check_replay(replay, bold, off, *, compact=False):
    outcomes = replay.get("outcomes", [])
    if not outcomes:
        return
    print("\n%sCHECK ANSWERS%s  %d/%d correct; threshold %d" % (
        bold, off, replay.get("score", 0), len(outcomes), replay.get("threshold", len(outcomes))))
    for index, outcome in enumerate(outcomes, 1):
        q = outcome["question"]
        chosen = outcome["chosen"]
        correct = q["correct_choice"]
        mark = _paint("✓", "ok") if chosen == correct else _paint("✗", "fail")
        print("  %s%d chose: %s" % (mark, index, q["choices"][chosen]))
        if chosen == correct and not compact:
            print("     why: %s" % q["feedback"][correct])
        elif chosen != correct:
            print("     correct: %s · why: %s" % (
                q["choices"][correct], q["feedback"][correct]))


def _clear_if_tty():
    if __import__("sys").stdout.isatty():
        print("\033[2J\033[H", end="")


def _clip(value, width=48):
    """Legacy name: prose is wrapped, never silently discarded."""
    return "\n".join(_wrap_prose(" ".join(str(value).split()), width, subsequent="  "))


# Reserve the prompt, popup borders, and the outer tmux status row.
_FEEDBACK_TRAILER_LINES = 5


def _result_key_ledger(card, replay):
    """A correct artifact has no 'wrong extra keys' or recipe-order diff."""
    if not replay.get("target_matches"):
        return replay.get("table", [])
    actual = replay.get("actual_tokens", [])
    used = _method_commands(actual, navigation=True)
    used_set = set(used)
    rule = card.get("method_requirement") or {}
    focal = _taught_method_paths(card)
    if not focal:
        paths = rule.get("all_of") or rule.get("any_of") or rule.get("exact_any_of")
        focal = [list(paths)] if paths else [[card.get("expected", "")]]
    # Show the closest accepted alternative, not red keys from every other
    # valid alternative. Used commands remain green under every outcome.
    paths = max(focal, key=lambda path: sum(
        command in used_set for keystring in path for command in _method_commands(
            _keys_module().tokens(keystring), navigation=card.get("navigation_only", False))))
    taught = []
    for path in paths:
        for command in _method_commands(_keys_module().tokens(path),
                                        navigation=card.get("navigation_only", False)):
            if command not in taught:
                taught.append(command)
    def show(command):
        mode, value = command
        return (":" + value + "<CR>" if mode == "ex" else
                "/" + value + "<CR>" if mode == "search" else value)
    # Both columns describe executed operations. All used commands are green;
    # only an absent taught command is red. The full ledger remains on k.
    lines = ["  YOU TYPED                         THE RECIPE ASKS FOR (taught commands)",
             "  --------------------------------  --------------------------------"]
    used = list(dict.fromkeys(used))
    for index in range(max(len(used), len(taught))):
        mine = show(used[index]) if index < len(used) else ""
        command = taught[index] if index < len(taught) else None
        theirs = show(command) if command else ""
        role = "ok" if command in used_set else "fail"
        note = "used" if command in used_set else "not used" if command else "extra accepted"
        lines.append("  %s  │ %s  %s" % (
            _paint(mine, "ok"), _paint(theirs, role), note))
    return lines


def _post_feedback_ultra(card, replay, completed, context, concept_replay,
                         check_replay, bold, off, replay_rows=None, minimal=False,
                         ledger_rows=None, breakdown_packed=False, defer_breakdown=False):
    """Fit essential result evidence in an 80x24 popup without scrolling it away."""
    if replay and replay.get("type") == "edit":
        print("%sRESULT COMPARISON%s  %s" % (
            bold, off, "exact target" if completed or replay.get("target_matches")
            else "mismatch: yours vs target"))
        for line in _artifact_replay(replay, completed, max_rows=replay_rows,
                                     minimal=minimal):
            print(line)
        print("%sKEYSTROKE LEDGER%s  YOU TYPED │ THE RECIPE ASKS FOR" % (bold, off))
        table = _result_key_ledger(card, replay)
        if table:
            # VD-12: the popup is always "compact" (<55 rows), and printing only
            # table[2:3] hid every ledger row after the first. Show every row
            # that fits; the caller shrinks ledger_rows only when the page
            # would otherwise scroll.
            body = table[2:] if len(table) > 2 else table
            limit = len(body) if ledger_rows is None else max(1, ledger_rows)
            for line in body[:limit]:
                print(line)
            if len(body) > limit:
                print("  … %d more ledger row(s)" % (len(body) - limit))
        else:
            print("  %-24s  %-24s" % (
                _clip(replay.get("actual_keys", "(unavailable)"), 24),
                _clip(replay.get("taught_keys", card.get("expected", "(none)")), 24)))
        if replay.get("method_evidence_error"):
            for row in textwrap.wrap("METHOD CHECK  " + replay["method_evidence_error"],
                                     width=max(40, shutil.get_terminal_size((80, 24)).columns - 4),
                                     subsequent_indent="  "):
                print(row.replace("✓", _paint("✓", "ok")).replace("✗", _paint("✗", "fail")))
        elif replay.get("method_family"):
            print("METHOD CHECK  demonstrated: %s" % replay["method_family"])
            for method in ([] if defer_breakdown else card.get("method_alternatives", [])):
                print("  %s  %s: %s" % (
                    method["label"], method["keys"], _clip(method["why"], 28)))
    elif replay and replay.get("type") == "paired_question":
        q = replay["question"]
        print("%sANSWER EXPLANATION%s  %s" % (
            bold, off, "correct" if replay.get("right") else "needs work"))
        chosen = replay.get("answer")
        if q.get("choices") and isinstance(chosen, int):
            _print_choice_explanation(q, chosen, compact=True)
        else:
            print("  YOUR ANSWER  %s" % _clip(
                chosen if chosen is not None else "(none)", 64))
            _print_grammar_breakdown(q)
    elif replay and replay.get("type") in ("concept", "review"):
        q, chosen = replay["question"], replay["chosen"]
        if q.get("choices"):
            print("%sANSWER EXPLANATION%s" % (bold, off))
            _print_choice_explanation(q, chosen, compact=True)
        else:
            print("%sANSWER EXPLANATION%s" % (bold, off))
            print("  YOUR ANSWER  %s" % _clip(replay.get("answer", chosen), 64))
            _print_grammar_breakdown(q)
            sample = q.get("answer_contract", {}).get("sample_answer")
            if sample:
                print("ONE ACCEPTED ANSWER  %s" % _clip(sample, 64))
        edit = replay.get("edit_replay")
        if edit:
            print("%sEDIT RESULT%s  %s" % (
                bold, off, "exact target" if completed else "mismatch: yours vs target"))
            for line in _artifact_replay(edit, completed, max_rows=replay_rows,
                                         minimal=minimal):
                print(line)
            print("keys: actual %s · taught %s" % (
                _clip(edit.get("actual_keys", "(none)"), 20),
                _clip(edit.get("taught_keys", "(none)"), 20)))
    if check_replay:
        outcomes = check_replay.get("outcomes", [])
        print("%sCHECK ANSWERS%s  %d/%d; threshold %d" % (
            bold, off, check_replay.get("score", 0), len(outcomes),
            check_replay.get("threshold", len(outcomes))))
        wrong = [(index, outcome) for index, outcome in enumerate(outcomes, 1)
                 if outcome["chosen"] != outcome["question"]["correct_choice"]]
        if outcomes and not wrong:
            print(_paint("✓", "ok") + " all %d choices correct; detailed explanations remain in the attempt record" %
                  len(outcomes))
        for index, outcome in wrong[:2]:
            q, chosen = outcome["question"], outcome["chosen"]
            correct = q["correct_choice"]
            print(_paint("✗", "fail") + "%d chose: %s → %s" % (
                index, _clip(q["choices"][chosen], 38), _clip(q["choices"][correct], 22)))
    if replay and replay.get("playback_verified"):
        print("%sPLAYBACK VERIFIED%s  automatic equal-height strip preview completed" % (
            bold, off))
    if not concept_replay:
        path = " → ".join(keys for keys, _why in card.get("recipe", [])
                          if keys != card.get("cursor"))
        print("%sDO / AVOID%s  %s · exact target" % (
            bold, off, path or card.get("expected", "(none)")))
        width = max(40, shutil.get_terminal_size((80, 24)).columns - 4)
        method_compare = bool(replay and replay.get("method_family")
                              and card.get("method_alternatives"))
        breakdown = [] if method_compare else _answer_breakdown(card, width=width)
        if defer_breakdown:
            print("THE ANSWER, KEY BY KEY · k opens the full explanation")
        elif method_compare:
            pass
        elif breakdown and (breakdown_packed or minimal):
            # Tight popup: one wrapped paragraph instead of one row per command.
            items = " · ".join(line.strip() for line in breakdown[1:])
            wrapped = textwrap.wrap("%s  %s" % (breakdown[0], items), width=width) or [""]
            for line in wrapped:
                print(line)
        elif breakdown:
            print("%s%s%s" % (bold, breakdown[0], off))
            for line in breakdown[1:]:
                print(line)
        else:
            for method in card.get("method_alternatives", []):
                print("ALSO %s: %s" % (method["label"], method["keys"]))
    for row in _wrap_prose(context["source"],
                            max(40, shutil.get_terminal_size((80, 24)).columns - 4),
                            indent="SOURCE  ", subsequent="        "):
        print(row)


def _print_feedback_do_this(card, replay, completed, concept_replay, compact, bold, off):
    """Every result page states the learner's next action (VD-11)."""
    if completed:
        action = "press Enter for skill-tree progress."
    elif replay and replay.get("target_matches") and replay.get("method_evidence_error"):
        action = "target correct; press r for an instant retry with the red taught command."
    elif concept_replay:
        action = "read why the correct answer is right, then press Enter."
    else:
        action = ("compare YOURS with TARGET (✗ = row differs), press Enter, "
                  "then retry the task shown in the lesson brief.")
    if compact:
        width = max(40, shutil.get_terminal_size((80, 24)).columns - 4)
        wrapped = textwrap.wrap(action, width=width - 9) or [""]
        print("%sDO THIS%s  %s" % (bold, off, wrapped[0]))
        for extra in wrapped[1:]:
            print("         " + extra)
        return len(wrapped)
    print("%sDO THIS%s  %s" % (bold, off, action))
    return 1


def _post_feedback(cfg, cur, card, replay=None, *, completed=True):
    """Render held page one: artifact evidence and authored correction."""
    global LAST_FEEDBACK_CONTEXT, LAST_FEEDBACK_DETAILS
    LAST_FEEDBACK_CONTEXT = (cfg, cur, card, replay, completed)
    LAST_FEEDBACK_DETAILS = []
    note_feedback_context(revision=cur.get("revision"), card_id=card.get("id"),
                          card_title=card.get("title"), module_id=card.get("module_id"),
                          lesson_result="complete" if completed else "not passed",
                          screen="result")
    bold, dim, off, green, red, yellow = cfg.colours
    context = _lesson_context(cur, card)
    compact = (__import__("sys").stdout.isatty()
               and shutil.get_terminal_size((80, 24)).lines < 55)
    concept_replay = bool(replay and replay.get("type") in (
        "concept", "review", "paired_question"))
    review_replay = bool(replay and replay.get("type") == "review")
    check_replay = replay if replay and replay.get("type") == "module_check" else (
        replay.get("check_replay") if replay else None)
    _clear_if_tty()
    if review_replay:
        print("%s%s%s  ·  %s  ·  %s" % (
            green + bold if completed else bold,
            "REVIEW RETRIEVED" if completed else "REVIEW NEEDS WORK",
            off, card["module_id"], card["title"]))
        print("%s: concept + changed-art edit %s; spaced-review progress %s" % (
            "verified" if completed else "not verified",
            "both passed" if completed else "did not both pass",
            "was awarded" if completed else "was not awarded"))
    elif completed:
        heading = "PRACTICE COMPLETE" if getattr(cfg, "practice", False) else "LESSON COMPLETE"
        print("%s%s%s  ·  %s  ·  %s" % (green + bold, heading, off, card["id"], card["title"]))
        if concept_replay:
            print("verified outcome: the conceptual choice is correct")
        elif not (compact and check_replay):
            print("verified outcome: the saved project matches the target exactly")
    else:
        method_miss = bool(replay and replay.get("target_matches") and replay.get("method_evidence_error"))
        heading = "RESULT ✓ · METHOD ✗" if method_miss else "ATTEMPT NOT PASSED"
        shown_heading = (_paint("RESULT ", "warn") + _paint("✓", "ok")
                         + _paint(" · METHOD ", "warn") + _paint("✗", "fail")) if method_miss else heading
        print("%s%s%s  ·  %s  ·  %s" % (
            (yellow if method_miss else red) + bold, shown_heading, off, card["id"], card["title"]))
        if concept_replay:
            print("no progress awarded: the conceptual choice was incorrect")
        elif check_replay:
            if not compact:
                print("no progress awarded: the module-check concept threshold was not met")
        elif replay and replay.get("target_matches"):
            print("TARGET CORRECT · the taught command still needs practice; instant retry: r")
        else:
            print("no progress awarded: the saved project did not match the exact target")

    do_lines = _print_feedback_do_this(card, replay, completed, concept_replay,
                                       compact, bold, off)
    if compact:
        # VD-11: measure the rendered page and shrink only the artifact replay
        # until title, status, DO THIS, replay, and the Enter prompt all fit.
        import contextlib
        import io
        # The popup's usable text width is narrower than the outer terminal.
        # Result headings that include a card title therefore occupy two rows
        # at 80 columns, followed by the one-line outcome.  Reserving only two
        # rows let tmux scroll the ATTEMPT/COMPLETE heading off the top.
        status_lines = 3
        available = (shutil.get_terminal_size((80, 24)).lines
                     - status_lines - do_lines - _FEEDBACK_TRAILER_LINES)
        ledger_total = max(1, len((replay or {}).get("table", [])) - 2)

        packed = False
        deferred = False

        def render(rows, minimal=False, ledger=None):
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                _post_feedback_ultra(card, replay, completed, context, concept_replay,
                                     check_replay, bold, off, replay_rows=rows,
                                     minimal=minimal, ledger_rows=ledger,
                                     breakdown_packed=packed, defer_breakdown=deferred)
            return buffer.getvalue()

        def screen_rows(text):
            columns = shutil.get_terminal_size((80, 24)).columns
            plain = re.sub(r"\x1b\[[0-9;]*m", "", text)
            return sum(max(1, (_cell_width(line) + columns - 1) // columns)
                       for line in plain.splitlines())

        rows = max(1, available)
        ledger = ledger_total
        text = render(rows, ledger=ledger)
        # Shrink the ledger to three rows first, then pack the key-by-key
        # answer into a paragraph (VD-13), then the artifact replay, then the
        # ledger to one row, so both two-column comparisons stay visible.
        while screen_rows(text) > available and ledger > 3:
            ledger -= 1
            text = render(rows, ledger=ledger)
        if screen_rows(text) > available:
            packed = True
            text = render(rows, ledger=ledger)
        while screen_rows(text) > available and rows > 1:
            rows -= 1
            text = render(rows, ledger=ledger)
        while screen_rows(text) > available and ledger > 1:
            ledger -= 1
            text = render(rows, ledger=ledger)
        if screen_rows(text) > available:
            # Tight page (e.g. module check at 80x24): keep both columns but
            # show only the first changed row, without elision/legend lines.
            text = render(1, minimal=True, ledger=1)
        if screen_rows(text) > available and replay and replay.get("type") == "edit":
            # Keep every sentence on explicit held detail pages rather than
            # silently cutting tails from the artifact evidence screen.
            deferred = True
            LAST_FEEDBACK_DETAILS = _answer_breakdown(
                card, width=max(40, shutil.get_terminal_size((80, 24)).columns - 8))
            for method in card.get("method_alternatives", []):
                LAST_FEEDBACK_DETAILS += _wrap_prose("%s · %s · %s" % (
                    method["label"], method["keys"], method["why"]),
                    width=max(40, shutil.get_terminal_size((80, 24)).columns - 8))
            text = render(1, minimal=True, ledger=1)
        print(text, end="")
        return

    if replay and replay.get("type") == "edit":
        print("\n%sRESULT COMPARISON%s  saved buffer before and after evaluation" % (bold, off))
        for line in _artifact_replay(replay, completed):
            print(line)
        print("\n%sKEYSTROKE LEDGER%s  actual input vs taught path" % (bold, off))
        if compact:
            print("  actual: %s" % replay.get("actual_keys", "(unavailable)"))
            print("  taught: %s  ·  alternate keys pass when the exact target matches" %
                  replay.get("taught_keys", card.get("expected", "(none)")))
        else:
            print("%sThe save/quit command is ignored. A different path may still be valid when the target matches.%s"
                  % (dim, off))
            for line in _result_key_ledger(card, replay):
                print(line)
        if replay.get("method_evidence_error"):
            print("  METHOD CHECK: %s" % replay["method_evidence_error"].replace(
                "✓", _paint("✓", "ok")).replace("✗", _paint("✗", "fail")))
        elif replay.get("method_family"):
            print("  METHOD CHECK: demonstrated %s" % replay["method_family"])
    elif replay and replay.get("type") == "paired_question":
        q = replay["question"]
        print("\n%sANSWER EXPLANATION%s" % (bold, off))
        chosen = replay.get("answer")
        if q.get("choices") and isinstance(chosen, int):
            _print_choice_explanation(q, chosen)
            if chosen != q["correct_choice"]:
                _print_grammar_breakdown(q)
        else:
            print("  YOUR ANSWER  %s" % (
                chosen if chosen is not None else "(none)"))
            _print_grammar_breakdown(q)
    elif replay and replay.get("type") in ("concept", "review"):
        q = replay["question"]
        chosen = replay["chosen"]
        print("\n%sANSWER EXPLANATION%s" % (bold, off))
        if q.get("choices"):
            _print_choice_explanation(q, chosen)
            if chosen != q["correct_choice"]:
                _print_grammar_breakdown(q)
        else:
            print("  YOUR ANSWER  %s" % replay.get("answer", chosen))
            _print_grammar_breakdown(q)
            sample = q.get("answer_contract", {}).get("sample_answer")
            if sample:
                print("  ONE ACCEPTED ANSWER: %s" % sample)
        edit = replay.get("edit_replay")
        if edit:
            print("\n%sCHANGED-ART EDIT RESULT%s" % (bold, off))
            for line in _artifact_replay(edit, completed):
                print(line)
            print("  actual keys: %s" % edit.get("actual_keys", "(none)"))
            print("  taught path: %s" % edit.get("taught_keys", "(none)"))
    if check_replay:
        _print_check_replay(check_replay, bold, off, compact=compact)
    if replay and replay.get("playback_verified"):
        print("\n%sPLAYBACK VERIFIED%s" % (bold, off))
        print("  The completed equal-height strip was played automatically in frame order.")

    if concept_replay:
        # The authored answer explanation is the lesson here. Card-design
        # rationale and generic "retain the principle" advice are internal
        # scaffolding; printing them repeats the VD-33 failure in new words.
        pass
    elif compact and replay and replay.get("type") == "edit":
        pass
    elif check_replay:
        print("\n%sCHECK PURPOSE%s  %s" % (bold, off, context["buys"]))
    else:
        print("\n%sWHY THIS EXISTS%s" % (bold, off))
        for line in context["why"]:
            print("  " + line)
        print("\n%sWHAT THIS LESSON BUYS YOU%s" % (bold, off))
        print("  " + context["buys"])

    if not concept_replay:
        print("\n%sDO / AVOID%s" % (bold, off))
        if compact:
            path = " → ".join(keys for keys, _why in card.get("recipe", [])
                              if keys != card.get("cursor"))
            print("  DO    taught path: %s" % (path or card.get("expected", "(none)")))
            if card.get("method_alternatives"):
                for method in card["method_alternatives"]:
                    print("  ALSO  %s: %s" % (method["label"], method["keys"]))
            print("  AVOID out-of-scope cells or an inexact target.")
        else:
            for keys, why in card.get("recipe", []):
                label = "START" if keys == card.get("cursor") and "cursor starts" in why else "DO"
                print("  %-5s %-14s %s" % (label, keys, why))
        if not compact and card.get("method_alternatives"):
            for method in card["method_alternatives"]:
                print("  ALSO  %-18s %-18s %s" % (
                    method["label"], method["keys"], method["why"]))
            print("  AVOID choosing by key count alone; choose by scope, repeatability, and error risk.")
        elif not compact:
            print("  AVOID editing the read-only brief or changing cells outside the requested scope.")
            print("  AVOID treating a similar-looking buffer as correct; the exact saved target is graded.")

    print("\n%sSOURCE%s  %s" % (bold, off, context["source"]))
    if review_replay:
        footer = "REVIEW RETRIEVED" if completed else "REVIEW NEEDS WORK"
    else:
        footer = ("PRACTICE COMPLETE" if getattr(cfg, "practice", False) else "LESSON COMPLETE") if completed else (
            "RESULT ✓ · METHOD ✗" if replay and replay.get("target_matches")
            and replay.get("method_evidence_error") else "ATTEMPT NOT PASSED")
    print("\n%s%s%s  ·  %s  ·  result summary above" % (
        green + bold if completed else (
            yellow + bold if footer == "RESULT ✓ · METHOD ✗" else red + bold),
        footer.replace("✓", _paint("✓", "ok")).replace("✗", _paint("✗", "fail")), off, card["id"]))


def show_feedback_details(input_fn=input):
    """Read every deferred explanation row, then restore the result screen."""
    if not LAST_FEEDBACK_DETAILS:
        print("The full key explanation is already on this result page.")
        return
    budget = max(4, shutil.get_terminal_size((80, 24)).lines - 5)
    width = max(20, shutil.get_terminal_size((80, 24)).columns - 4)
    # A breakdown item can contain several wrapped rows. Pagination budgets
    # terminal rows, not items, so no sentence can scroll its page heading away.
    lines = [row for item in LAST_FEEDBACK_DETAILS for logical in item.splitlines()
             for row in _wrap_prose(logical, width)]
    pages = [lines[i:i + budget] for i in range(0, len(lines), budget)]
    for index, page in enumerate(pages):
        _clear_if_tty()
        print("FULL KEY EXPLANATION · %d/%d" % (index + 1, len(pages)))
        print("\n".join(page))
        try:
            answer = input_fn("Enter = continue · q = return to result: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        if answer == "q":
            break
    if LAST_FEEDBACK_CONTEXT:
        cfg, cur, card, replay, completed = LAST_FEEDBACK_CONTEXT
        _post_feedback(cfg, cur, card, replay, completed=completed)


def progress_full_rows(cur):
    """Terminal rows the full progress page needs; smaller popups use the compact tree.

    VD-11: a fixed 28-row threshold let the 14-module tree scroll the page's
    PROGRESS header off a 100x36 popup.
    """
    return len(cur["stages"]) + len(cur["modules"]) + 28


def _post_progress(cfg, cur, card, progress, *, completed=True):
    """Render held page two: progression only, without feedback scrolling away."""
    bold, _dim, off, green, _red, yellow = cfg.colours
    _clear_if_tty()
    if getattr(cfg, "practice", False):
        label = "PRACTICE COMPLETE · PROGRESS UNCHANGED"
    else:
        label = "PROGRESS AWARDED" if completed else "PROGRESS UNCHANGED"
    # Readability audit #8: an unchanged result reads as a warning, not success.
    colour = green + bold if completed else yellow + bold
    ultra = (__import__("sys").stdout.isatty()
             and shutil.get_terminal_size((80, 24)).lines < progress_full_rows(cur))
    print("%s%s%s  ·  %s  ·  %s" % (colour, label, off, card["id"], card["title"]))
    if completed and progress.get("awarded_xp") and not getattr(cfg, "practice", False):
        print(_paint("+%d XP · +%d commands" % (
            progress["awarded_xp"], progress.get("new_commands", 0)), "ok"))
    print("\n%sSKILL TREE / MODULE PROGRESS%s%s" % (
        bold, off, " · S stills → A animation · P optional" if ultra else ""))
    print_tree(cur, progress, cfg, compact=ultra)
    if ultra:
        module = next(m for m in cur["modules"] if m["id"] == card["module_id"])
        passed = set(progress["passed_cards"])
        cells = " ".join("%s%s" % (
            (lambda sfx: "%02d" % int(sfx) if sfx.isdigit() else sfx)(cid.rsplit(".", 1)[1]),
            "✓" if cid in passed else "○")
            for cid in module["card_ids"])
        # VD-13: new card labels (P0, O, T) lengthened the map; keep the
        # daily count on its own line so it is never split by wrapping.
        # Readability audit #3: wrap between cards, never inside a card id.
        width = max(40, shutil.get_terminal_size((80, 24)).columns - 10)
        for row in textwrap.wrap("CURRENT MODULE MAP  %s %s" % (module["id"], cells),
                                 width=width, subsequent_indent="  ",
                                 break_long_words=False):
            print(row.replace("✓", _paint("✓", "ok")))
        print("today %d/%d" % (_legacy_today(cfg.state), cfg.target))
    else:
        print("\n%sCURRENT MODULE MAP%s" % (bold, off))
        print(_module_card_map(cur, progress, card["module_id"]))
    if progress.get("new_unlocks"):
        print("NEW UNLOCKS: %s" % ", ".join(progress["new_unlocks"]))
    if not ultra:
        print("today: %d/%d lessons" % (_legacy_today(cfg.state), cfg.target))


def _post_lesson(cfg, cur, card, progress, replay=None, *, completed=True):
    """Render separate held feedback and progression pages."""
    if not completed:
        _legacy_attempt(cfg, card["id"])
    # Textual owns the mounted feedback/progress surface when it is available;
    # the runtime still produces both bodies and remains the only owner of
    # feedback, progress and credit decisions.  Its route is consumed by the
    # launcher's existing held-action loop below.
    # Native result playback also belongs to the non-Textual route. The
    # screen helper performs it before selecting the available text surface.
    if _show_result_screen(cfg, cur, card, progress, replay, completed):
        return
    _post_feedback(cfg, cur, card, replay, completed=completed)
    if cfg.feedback_rendered:
        cfg.feedback_rendered()
    if cfg.post_page_break:
        cfg.post_page_break()
    _post_progress(cfg, cur, card, progress, completed=completed)


def _complete(cfg, cur, card, *, question_id=None, extra=None, replay=None):
    before_progress = project(cur, read_events(cfg))
    before_badges = {b["id"] for b in _badge_rows(cfg, cur, before_progress) if b["earned"]}
    event = {"type": "card", "result": "pass", "card_id": card["id"],
             "module_id": card["module_id"], "curriculum_revision": cur["revision"],
             "question_id": question_id}
    if _review_variants(card):
        event["next_due"] = _next_due(cur, 0)
    if extra:
        event.update(extra)
    if replay and replay.get("method_family"):
        method = next((m for m in card.get("method_alternatives", [])
                       if m["label"] == replay["method_family"]), {})
        event["method_tier"] = "taught" if method.get("keys") == card.get("expected") else "declared"
        event["method_family"] = replay["method_family"]
    if card.get("kind") == "module_check":
        # A mastered module points at both its final checkpoint and the unseen
        # transfer artifact that preceded it.  The hashes remain in the
        # append-only ledger even if a projection is rebuilt later.
        transfer_ids = {c["id"] for c in cur["cards"]
                        if c["module_id"] == card["module_id"]
                        and c.get("artifact") == "transfer"}
        transfer_event = next((row for row in reversed(read_events(cfg))
                               if row.get("type") == "card"
                               and row.get("result") == "pass"
                               and row.get("card_id") in transfer_ids), None)
        if transfer_event is None:
            raise RuntimeError(
                "module mastery cannot be awarded without a passed unseen-transfer artifact")
        event["module_evidence"] = {
            "checkpoint_artifact": event.get("artifact"),
            "checkpoint_sha256": event.get("artifact_sha256"),
            "transfer_card_id": transfer_event.get("card_id"),
            "transfer_artifact": transfer_event.get("artifact"),
            "transfer_sha256": transfer_event.get("artifact_sha256"),
        }
    append_event(cfg, event)
    _defer_taught_method(cfg, cur, card, before_progress, replay)
    _legacy_credit(cfg, card["id"])
    streak, best_streak, all_time = _legacy_streak(cfg.state)
    if getattr(cfg, "practice", False):
        print("PRACTICE COMPLETE  ·  no duplicate XP, mastery, daily credit, or streak credit")
    elif streak:
        bold, _dim, off, green, _red, _yellow = cfg.colours
        flame = " 🔥" if streak >= 3 else ""
        print("%s%sStreak extended to %d day%s.%s  best %d · %d drill%s all time%s" % (
            green, bold, streak, "" if streak == 1 else "s", flame,
            best_streak, all_time, "" if all_time == 1 else "s", off))
    progress = rebuild(cfg, cur)
    progress["awarded_xp"] = progress["xp"] - before_progress["xp"]
    progress["new_commands"] = max(0, len(learned_deck(cur, progress))
                                  - len(learned_deck(cur, before_progress)))
    progress["new_unlocks"] = [
        stage["id"] for stage in cur["stages"]
        if before_progress["stages"][stage["id"]]["state"] == "locked"
        and progress["stages"][stage["id"]]["state"] != "locked"
    ]
    cell = progress["modules"][card["module_id"]]
    print("\n%s %s complete — %s %d/%d (%s)" % (
        _paint("✓", "ok"), card["id"], card["module_id"], cell["done"], cell["total"], cell["state"]))
    nxt = next_card(cur, progress)
    if nxt:
        print("next: %s  %s" % (nxt["id"], nxt["title"]))
    else:
        current = progress.get("current_stage")
        print("%s" % ("stage %s is waiting on spaced review" % current
                       if current else "main S0-A7 path mastered"))
    _celebrate_progress(cfg, cur, before_progress, progress, before_badges)
    _post_lesson(cfg, cur, card, progress, replay)
    if cfg.post_rendered:
        cfg.post_rendered()
    cfg.hold_open()
    return 0


def run_concept(cfg, cur, progress, card):
    _bind_curriculum(cfg, cur)
    context = _lesson_context(cur, card)
    q = _question_for_card(cur, progress, card)
    if _textual_enabled():
        if not _show_concept_screen(cfg, cur, progress, card, context):
            return 0
    else:
        print("\n%s — %s" % (card["id"], card["title"]))
    ultra = (__import__("sys").stdout.isatty()
             and shutil.get_terminal_size((80, 24)).lines < 28)
    if not _textual_enabled():
        print(_clip(_progress_line(cfg, progress, card), 70) if ultra
              else _progress_line(cfg, progress, card))
        if not ultra:
            print("WHY: %s" % context["why"][1])
            print("BUYS: %s" % context["buys"])
            print("SOURCE: %s" % context["source"])
    teaching = card.get("teaching_lines", [])
    if teaching and not _textual_enabled():
        print("TEACH FIRST")
        for line in teaching:
            print("  %s" % line)
        # Readability audit #1: the question page clears the screen, which
        # erased this teaching before it could be read. Hold it on its own
        # page first when a person is at the keyboard.
        if (__import__("sys").stdin.isatty() and __import__("sys").stdout.isatty()
                and cfg.question_answer is None):
            while True:
                try:
                    answer = input("\nEnter = show the question  ·  f = feedback ")
                except (EOFError, KeyboardInterrupt):
                    return 0
                if answer.strip().lower() not in ("f", "feedback"):
                    break
                note_feedback_context(revision=cur.get("revision"), card_id=card["id"],
                                      card_title=card.get("title"), screen="teach-first")
                collect_feedback(input, screen="teach-first")
    if ultra and not _textual_enabled():
        print("DO THIS %s: choose the answer whose ANIMATION and NEOVIM halves are both correct."
              % card["id"])
    elif not _textual_enabled():
        print("DO THIS: %s" % card["prompt"])
    if not ultra and not _textual_enabled():
        print("CHECK YOUR UNDERSTANDING: both the animation reading and Neovim decision must be correct.")
    question_evidence = {}
    right, chosen = ask_authored_question(
        q, input_fn=_configured_question_input(cfg, q),
        shuffle=cfg.question_answer is None,
        rendered=cfg.question_rendered, evidence=question_evidence)
    if right is None:
        return 0
    append_event(cfg, _question_event(
        cur, card, q, right, chosen, question_evidence))
    if not right:
        append_event(cfg, {"type": "card", "result": "fail", "card_id": card["id"],
                           "module_id": card["module_id"], "reason": "concept-answer"})
        failed_progress = rebuild(cfg, cur)
        next_question = _question_for_card(cur, failed_progress, card)
        _schedule_remediation(
            cfg, card, "Q", "new stem %s with reshuffled choices" % next_question["id"],
            "incorrect paired animation/Neovim choice")
        failed_progress = rebuild(cfg, cur)
        _post_lesson(cfg, cur, card, failed_progress,
                     {"type": "concept", "question": q, "chosen": chosen,
                      "answer": chosen}, completed=False)
        print("\nA different variant will be used next time; the card did not advance.")
        if cfg.post_rendered:
            cfg.post_rendered()
        cfg.hold_open()
        return 1
    return _complete(cfg, cur, card, question_id=q["id"],
                     replay={"type": "concept", "question": q, "chosen": chosen,
                             "answer": chosen})


def _latest_check_replay(cfg, cur, card):
    """Rebuild the last passed five-question table for an artifact retry."""
    events = read_events(cfg)
    qmap = _question_map(cur)
    for index in range(len(events) - 1, -1, -1):
        event = events[index]
        if (event.get("type") == "check_concepts" and event.get("result") == "pass"
                and event.get("card_id") == card["id"]):
            question_events = []
            for previous in reversed(events[:index]):
                if previous.get("card_id") != card["id"]:
                    continue
                if previous.get("type") == "question" and previous.get("check"):
                    question_events.append(previous)
                    if len(question_events) == 5:
                        break
                elif previous.get("type") == "check_concepts":
                    break
            question_events.reverse()
            outcomes = [{
                "question": qmap[row["question_id"]],
                "right": row.get("result") == "pass",
                "chosen": row["choice"],
            } for row in question_events if row.get("question_id") in qmap]
            if outcomes:
                return {"type": "module_check", "outcomes": outcomes,
                        "score": sum(int(row["right"]) for row in outcomes),
                        "threshold": card.get("pass_questions", len(outcomes))}
    return None


def run_check_questions(cfg, cur, progress, card):
    if card["id"] in progress.get("check_concepts", []):
        print("check concepts already passed; resuming the editing task")
        return True, _latest_check_replay(cfg, cur, card)
    qmap = _question_map(cur)
    context = _lesson_context(cur, card)
    print("\n" + _progress_line(cfg, progress, card))
    print("MODULE CHECK WHY: %s" % context["why"][1])
    print("MODULE CHECK BUYS: %s" % context["buys"])
    print("DO THIS: answer five checks, then complete the unhinted art edit.")
    declared = card.get("question_ids", [])
    module_bank = declared or [q["id"] for q in cur["questions"]
                               if q["module_id"] == card["module_id"]]
    # Prefer genuinely unseen stems.  When the bank is exhausted, least-seen
    # stems come first; card attempts rotate ties deterministically.
    offset = progress["attempts"].get(card["id"], 0) % len(module_bank)
    rotated = module_bank[offset:] + module_bank[:offset]
    ranked = sorted(enumerate(rotated),
                    key=lambda pair: (progress["question_attempts"].get(pair[1], 0),
                                      pair[0]))
    selected = [qid for _index, qid in ranked[:5]]
    score = 0
    outcomes = []
    for qid in selected:
        question_evidence = {}
        right, chosen = ask_authored_question(
            qmap[qid], input_fn=_configured_question_input(cfg, qmap[qid]),
            shuffle=cfg.question_answer is None,
            rendered=cfg.question_rendered, evidence=question_evidence)
        if right is None:
            return None, None
        score += int(right)
        outcomes.append({"question": qmap[qid], "right": bool(right), "chosen": chosen})
        append_event(cfg, _question_event(
            cur, card, qmap[qid], right, chosen, question_evidence, check=True))
    print("check questions: %d/%d" % (score, len(outcomes)))
    replay = {"type": "module_check", "outcomes": outcomes, "score": score,
              "threshold": card.get("pass_questions", len(outcomes))}
    if score < card.get("pass_questions", len(outcomes)):
        append_event(cfg, {"type": "check_concepts", "result": "fail", "card_id": card["id"],
                           "module_id": card["module_id"], "score": score})
        append_event(cfg, {"type": "card", "result": "fail", "card_id": card["id"],
                           "module_id": card["module_id"], "reason": "concept-threshold",
                           "score": score})
        failed_progress = rebuild(cfg, cur)
        next_ranked = sorted(
            module_bank,
            key=lambda qid: (failed_progress["question_attempts"].get(qid, 0), qid))[:5]
        _schedule_remediation(
            cfg, card, "K", "changed five-check set: %s" % ", ".join(next_ranked),
            "module-check concept threshold not met")
        rebuild(cfg, cur)
        print("The module stays in learning. The next attempt uses shuffled choices and retained feedback.")
        return False, replay
    append_event(cfg, {"type": "check_concepts", "result": "pass", "card_id": card["id"],
                       "module_id": card["module_id"], "score": score})
    return True, replay


def _native_module(name):
    """Load the installed sibling while retaining its normal dataclass imports."""
    import importlib
    import sys
    directory = str(Path(__file__).resolve().parent)
    inserted = directory not in sys.path
    if inserted:
        sys.path.insert(0, directory)
    try:
        return importlib.import_module(name)
    finally:
        if inserted:
            sys.path.remove(directory)


def _native_adapter():
    return _native_module("sjis_tutor")


def _run_native_editor(cfg, card, path, keylog, lesson, before):
    """Connect proportional editing to a live, displayed native preview."""
    # Keep the exact loaded task beside its unique attempt keylog. A hash is
    # an identity, not a recoverable copy of a later-edited live curriculum.
    contract_path = Path(keylog).with_suffix(".contract.json")
    _write_lines_atomic(contract_path, [json.dumps({
        "schema": "vim-daily/attempt-contract@1",
        "curriculum_revision": getattr(cfg, "curriculum_revision", None),
        "curriculum_contract_sha256": getattr(cfg, "curriculum_contract_sha256", None),
        "cursor_attempt": os.environ.get("VIM_DAILY_CURSOR_ATTEMPT"),
        "card": card, "before": before,
    }, sort_keys=True, ensure_ascii=False)])
    args = (str(path), 1, card.get("cursor", "^"), str(keylog), str(lesson),
            card["prompt"], _scoped_hint(card))
    if card.get("medium") != "proportional-sjis":
        cfg.run_editor(*args)
        return None
    receipt_path = Path(keylog).with_suffix(".native.json")
    try:
        adapter = _native_adapter()
        factory = getattr(cfg, "native_preview_factory", None)
        if factory is None:
            factory = (adapter.TutorPreview if os.environ.get("VIM_DAILY_NATIVE_SURFACE") == "browser"
                       else _sibling_module("sjis_terminal").TerminalPreview)
        with factory(path, card["target"], before_rows=before) as preview:
            print("NATIVE PROPORTIONAL PREVIEW: %s" % preview.url)
            print("Inspect the native Saitamaar BEFORE / YOURS / TARGET and changed-pixel panels. Editable text remains in Neovim.")
            cfg.run_editor(*args)
            receipt = preview.final_receipt()
        adapter.write_receipt(receipt_path, receipt)
        receipt["evidence_path"] = str(receipt_path)
        return receipt
    except Exception as exc:
        # Renderer failures deny credit; no monospace alignment fallback.
        receipt = {"schema": "vim-daily/proportional-attempt@1", "ready": False,
                   "reasons": ["Native preview unavailable: %s" % exc],
                   "operator_visual_acceptance": "required"}
        print(receipt["reasons"][0])
        return receipt


def _native_recovery_receipt(card, path, keylog, before_path):
    if card.get("medium") != "proportional-sjis":
        return None
    try:
        receipt_path = Path(keylog).with_suffix(".native.json")
        data = json.loads(receipt_path.read_text(encoding="utf-8"))
        adapter = _native_adapter()
        metrics = adapter.native.load_font_metrics(
            os.environ.get("VIM_DAILY_SAITAMAAR_FONT") or adapter.native.DEFAULT_FONT_PATH)
        identity = data["display"]["identity"]
        target_hash = hashlib.sha256(adapter.art_text(card["target"]).encode("utf-8")).hexdigest()
        if (data.get("schema") != "vim-daily/proportional-attempt@1" or not data.get("ready")
                or data.get("artifact_sha256") != _hash_file(path)
                or identity.get("yours_text_sha256") != _hash_file(path)
                or identity.get("source_byte_sha256") != _hash_file(before_path)
                or identity.get("target_text_sha256") != target_hash
                or identity.get("font_sha256") != metrics.font_sha256
                or identity.get("font_size_px") != metrics.font_size_px
                or identity.get("line_pitch_px") != metrics.line_pitch_px):
            return {"ready": False, "reasons": ["The saved target has no current bound native-preview receipt. Reopen the native page on a fresh attempt."]}
        data["evidence_path"] = str(receipt_path)
        return data
    except Exception as exc:
        return {"ready": False, "reasons": ["The saved target has no usable native display receipt; transcription alone cannot advance this lesson. %s" % exc]}


def run_edit(cfg, cur, progress, card):
    _bind_curriculum(cfg, cur)
    check_replay = None
    path = _artifact_path(cfg, card)
    variants = card.get("variants", [])
    if variants:
        chosen = None
        existing = (_read_lines(path, card.get("preserve_trailing_whitespace", False))
                    if path.exists() else None)
        if existing is not None:
            chosen = next((variant for variant in variants
                           if existing == _card_lines(card, variant["target"])), None)
        if chosen is None:
            chosen = variants[progress["attempts"].get(card["id"], 0) % len(variants)]
        card = dict(card)
        # Shape and vocabulary belong to the selected drawing/command path.
        # A retry must not inherit the primary drawing's literal landmarks.
        for field in ("key_shape", "key_vocabulary"):
            if field not in chosen:
                card.pop(field, None)
        card.update(chosen)
        card["variant_index"] = variants.index(chosen)
        if existing is not None and existing != _card_lines(card, card["start"]):
            known_starts = [_card_lines(card, variant["start"]) for variant in variants]
            if existing in known_starts:
                _write_lines_atomic(path, card["start"])
    if getattr(cfg, "practice", False):
        # A repeat is a fresh rehearsal.  Never reuse the passed target (which
        # would skip the editor through recovery), and never touch the learner's
        # real project artifact.
        _write_lines_atomic(path, card["start"])
    pair_passed, pair_replay = run_paired_questions(cfg, cur, progress, card, "before")
    if pair_passed is None:
        return 0
    if not pair_passed:
        failed_progress = rebuild(cfg, cur)
        _post_lesson(cfg, cur, card, failed_progress, pair_replay, completed=False)
        print("\nThe paired question did not advance the card. Its grammar breakdown is retained above.")
        if cfg.post_rendered:
            cfg.post_rendered()
        cfg.hold_open()
        return 1
    progress = rebuild(cfg, cur)
    if card["kind"] == "module_check":
        check_passed, check_replay = run_check_questions(cfg, cur, progress, card)
        if check_passed is None:
            return 0
        if not check_passed:
            failed_progress = rebuild(cfg, cur)
            _post_lesson(cfg, cur, card, failed_progress, check_replay, completed=False)
            print("\nThe module check did not advance. A later attempt will use changed choices.")
            if cfg.post_rendered:
                cfg.post_rendered()
            cfg.hold_open()
            return 1
    if not path.exists():
        _write_new(path, card["start"])
    current = _read_lines(path, card.get("preserve_trailing_whitespace", False))
    legacy_starts = [
        _card_lines(card, legacy)
        for legacy in card.get("accepted_legacy_starts", [])
    ]
    if current in legacy_starts:
        migration_number = legacy_starts.index(current) + 1
        before_hash = _hash_file(path)
        _checkpoint(cfg, card, path, "pre-curriculum-migration-%d" % migration_number)
        _write_lines_atomic(path, card["start"])
        append_event(cfg, {
            "type": "curriculum_migration", "result": "pass",
            "card_id": card["id"], "module_id": card["module_id"],
            "curriculum_revision": cur["revision"],
            "artifact": str(path), "artifact_before_sha256": before_hash,
            "artifact_sha256": _hash_file(path),
        })
        current = _read_lines(path, card.get("preserve_trailing_whitespace", False))
        print("Upgraded the verified project checkpoint to the revised multi-row lesson art; "
              "the prior text remains in checkpoints/.")
    target_lines = _card_lines(card, card["target"])
    # Window/reference exercises deliberately leave the art unchanged.  A
    # freshly seeded start is not a recovered attempt: the learner must still
    # open the editor and demonstrate the workflow recorded in the key log.
    if current == target_lines and current != _card_lines(card, card["start"]):
        recovery_extra = {"artifact": str(path), "artifact_sha256": _hash_file(path),
                          "recovered": True}
        recovery_replay = check_replay
        recovery_keylog = _latest_attempt_keylog(path.parent, "keys-%s" % card["id"])
        recovery_before = path.parent / "checkpoints" / (card["id"] + "-before.txt")
        native_recovery = _native_recovery_receipt(card, path, recovery_keylog, recovery_before)
        if native_recovery and not native_recovery["ready"]:
            _checkpoint(cfg, card, path, "uncredited-native-target")
            if recovery_before.exists():
                shutil.copy2(recovery_before, path)
            else:
                _write_lines_atomic(path, card["start"])
            append_event(cfg, {"type": "card", "result": "fail", "card_id": card["id"],
                              "module_id": card["module_id"], "reason": "missing-native-preview",
                              "native_preview": native_recovery, "recovered": True})
            print(" ".join(native_recovery["reasons"]))
            cfg.hold_open()
            return 1
        if native_recovery:
            recovery_extra["native_preview"] = native_recovery
        if card.get("method_alternatives") or card.get("method_requirement"):
            recovered_keylog = _latest_attempt_keylog(
                path.parent, "keys-%s" % card["id"])
            keylog = str(recovered_keylog or path.parent / ("keys-%s.log" % card["id"]))
            recovery_extra.update(_keylog_fields(keylog))
            before_path = path.parent / "checkpoints" / (card["id"] + "-before.txt")
            before = (_read_lines(before_path, card.get("preserve_trailing_whitespace", False))
                      if before_path.exists() else card["start"])
            recovered_receipt = _recovery_input_receipt(keylog, path, card, before)
            recovery_replay = _attempt_replay(
                cfg, card, keylog, before, current, recovered_receipt,
                require_typed_input=_typed_input_required(cfg))
            recovery_replay["target_matches"] = True
            method_family = (_method_family(cfg, card, recovery_replay)
                             if card.get("method_alternatives") else None)
            method_error = _required_method_error(cfg, card, recovery_replay)
            if ((card.get("method_alternatives") and not method_family)
                    or method_error):
                failure_number = progress["attempts"].get(card["id"], 0) + 1
                _checkpoint(cfg, card, path, "uncredited-target-%d" % failure_number)
                if before_path.exists():
                    shutil.copy2(before_path, path)
                else:
                    _write_lines_atomic(path, card["start"])
                recovery_failure = {
                    "type": "card", "result": "fail", "card_id": card["id"],
                    "module_id": card["module_id"],
                    "reason": "missing-method-evidence", "recovered": True,
                }
                recovery_failure.update(_keylog_fields(keylog))
                append_event(cfg, recovery_failure)
                failed_progress = rebuild(cfg, cur)
                recovery_replay["method_evidence_error"] = (
                    method_error or _unrecognized_method_message(recovery_replay))
                _post_lesson(cfg, cur, card, failed_progress, recovery_replay, completed=False)
                if cfg.post_rendered:
                    cfg.post_rendered()
                cfg.hold_open()
                return 1
            if method_family:
                recovery_replay["method_family"] = method_family
                recovery_extra["method_family"] = method_family
            if card.get("method_requirement"):
                recovery_extra["required_method"] = card["method_requirement"]["label"]
        print("Recovered verified target already present in %s." % path)
        _update_manifest(cur, card, path)
        if card.get("kind") == "module_check":
            print("\nAUTOMATIC PLAYBACK CHECK")
            playback_ok = preview_project(
                cfg, cur, card["module_id"],
                0.12 if __import__("sys").stdout.isatty() else 0) == 0
            if recovery_replay is None:
                recovery_replay = {"type": "module_check", "outcomes": [],
                                   "score": 0, "threshold": 0}
            recovery_replay["playback_verified"] = playback_ok
        after_passed, after_replay = run_paired_questions(
            cfg, cur, rebuild(cfg, cur), card, "after")
        if after_passed is None:
            return 0
        if not after_passed:
            failed_progress = rebuild(cfg, cur)
            _post_lesson(cfg, cur, card, failed_progress, after_replay, completed=False)
            print("\nThe saved target is preserved; explain the method before this card advances.")
            if cfg.post_rendered:
                cfg.post_rendered()
            cfg.hold_open()
            return 1
        watch_your_work(cfg, cur, card, path)
        return _complete(cfg, cur, card, extra=recovery_extra, replay=recovery_replay)
    if current != _card_lines(card, card["start"]):
        print("Project checkpoint differs from the start required by %s:" % card["id"])
        print("  %s" % path)
        print("Your text was preserved. Compare it with the latest file in checkpoints/ before retrying.")
        return 1

    print("\n%s — %s" % (card["id"], card["title"]))
    print(card["prompt"])
    show_target = card.get("show_target", True)
    show_recipe = card.get("show_recipe", card.get("show_target", False))
    if show_target:
        print("target:")
        for line in card["target"]:
            print("  │" + line)
    if show_recipe:
        print("recipe:")
        for keys, why in card["recipe"]:
            print("  %-14s %s" % (keys, why))
    else:
        print("hint: %s" % _scoped_hint(card))
        print("Exact command keys stay hidden until this attempt is evaluated.")
        if card.get("method_alternatives"):
            print("After success both taught approaches are shown.")
    _checkpoint(cfg, card, path, "before")
    before_hash = _hash_file(path)
    tries = 0
    while tries < cfg.max_tries:
        tries += 1
        keylog_path = _next_attempt_keylog(path.parent, "keys-%s" % card["id"])
        keylog = str(keylog_path)
        lesson = _write_session_lesson(cfg, cur, progress, card)
        if not _show_lesson_screen(cfg, card, lesson):
            cfg.hold_open()
            return 0
        with _CursorReceiptEnv(path, keylog_path, tries) as cursor_env:
            native_receipt = _run_native_editor(cfg, card, path, keylog, lesson, current)
        got = _read_lines(path, card.get("preserve_trailing_whitespace", False))
        receipt = _read_cursor_receipt(cursor_env.receipt, cursor_env.token, path)
        replay = _attempt_replay(
            cfg, card, keylog, current, got, receipt,
            require_typed_input=_typed_input_required(cfg))
        if receipt:
            replay["cursor_receipt"] = receipt
        if check_replay:
            replay["check_replay"] = check_replay
        exact_target = got == target_lines
        replay["target_matches"] = exact_target
        if native_receipt:
            replay["native_preview"] = native_receipt
            if not native_receipt["ready"]:
                exact_target = False
                replay["method_evidence_error"] = " ".join(native_receipt["reasons"])
        method_family = (_method_family(cfg, card, replay)
                         if card.get("method_alternatives") else None)
        method_error = _required_method_error(cfg, card, replay)
        if method_family:
            replay["method_family"] = method_family
        if exact_target and card.get("method_alternatives") and method_family is None:
            exact_target = False
            replay["method_evidence_error"] = _unrecognized_method_message(replay)
        if exact_target and method_error:
            exact_target = False
            replay["method_evidence_error"] = method_error
        cursor_error = _cursor_goal_error(card, replay)
        if exact_target and cursor_error:
            exact_target = False
            replay["method_evidence_error"] = cursor_error
        if exact_target:
            _checkpoint(cfg, card, path, "after")
            _update_manifest(cur, card, path)
            if card.get("kind") == "module_check":
                print("\nAUTOMATIC PLAYBACK CHECK")
                replay["playback_verified"] = preview_project(
                    cfg, cur, card["module_id"],
                    0.12 if __import__("sys").stdout.isatty() else 0) == 0
            if card.get("method_alternatives"):
                print("\nTwo valid approaches:")
                for method in card["method_alternatives"]:
                    print("  • %-18s %-18s %s" % (
                        method["label"], method["keys"], method["why"]))
                print("saved: %s" % _write_compare(card, path))
            extra = {"artifact": str(path), "attempts": tries,
                     "artifact_before_sha256": before_hash,
                     "artifact_sha256": _hash_file(path)}
            extra.update(_keylog_fields(keylog_path))
            if "variant_index" in card:
                extra["variant_index"] = card["variant_index"]
            if replay.get("cursor_receipt"):
                extra["cursor_receipt"] = replay["cursor_receipt"]
            if native_receipt:
                extra["native_preview"] = native_receipt
            if method_family:
                extra["method_family"] = method_family
            if card.get("method_requirement"):
                extra["required_method"] = card["method_requirement"]["label"]
            after_passed, after_replay = run_paired_questions(
                cfg, cur, rebuild(cfg, cur), card, "after")
            if after_passed is None:
                return 0
            if not after_passed:
                failed_progress = rebuild(cfg, cur)
                _post_lesson(cfg, cur, card, failed_progress, after_replay, completed=False)
                print("\nThe saved target is preserved; explain the method before this card advances.")
                if cfg.post_rendered:
                    cfg.post_rendered()
                cfg.hold_open()
                return 1
            watch_your_work(cfg, cur, card, path)
            return _complete(cfg, cur, card, extra=extra,
                             replay=replay)
        failure_event = {"type": "card", "result": "fail", "card_id": card["id"],
                         "module_id": card["module_id"], "attempt": tries,
                         "artifact": str(path),
                         "reason": ("missing-method-evidence"
                                    if replay.get("method_evidence_error")
                                    else "target-mismatch")}
        failure_event.update(_keylog_fields(keylog_path))
        if native_receipt:
            failure_event["native_preview"] = native_receipt
        append_event(cfg, failure_event)
        if card.get("kind") == "transfer":
            variants = card.get("variants", [])
            next_index = ((card.get("variant_index", 0) + 1) % len(variants)) if variants else 0
            _schedule_remediation(
                cfg, card, "T", "unseen transfer variant %d" % (next_index + 1),
                "saved changed-art artifact did not match its stated contract")
        elif card.get("kind") == "module_check":
            _schedule_remediation(
                cfg, card, "K", "row-diff recovery followed by the retained checkpoint edit",
                "module-check artifact did not match its stated contract")
        failure_number = progress["attempts"].get(card["id"], 0) + tries
        _checkpoint(cfg, card, path, "failed-%d" % failure_number)
        shutil.copy2(path.parent / "checkpoints" / (card["id"] + "-before.txt"), path)
        failed_progress = rebuild(cfg, cur)
        _post_lesson(cfg, cur, card, failed_progress, replay, completed=False)
        if replay.get("method_evidence_error"):
            print(replay["method_evidence_error"])
        print("failed snapshot preserved; working artifact restored to this card's checkpoint")
        if TEXTUAL_ROUTE is not None:
            # The mounted result has already collected Repeat/Next/Close.
            # Let the launcher consume that action; a second plain retry
            # prompt would swallow the result-screen Repeat request.
            if cfg.post_rendered:
                cfg.post_rendered()
            cfg.hold_open()
            return 1
        # VD-13: a failed transfer used to stop here ("changed-art variant is
        # next"), so the learner could not retry. It now falls through to the
        # same retry prompt as every other edit; the remediation stays scheduled.
        if tries >= cfg.max_tries:
            print("Attempt limit reached; no progress was awarded.")
            if cfg.post_rendered:
                cfg.post_rendered()
            cfg.hold_open()
            return 1
        if cfg.post_rendered:
            cfg.post_rendered()
        while True:
            try:
                answer = input("Restore this card's checkpoint and retry? [Y/n] "
                               "· f = feedback ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                cfg.hold_open()
                return 0
            if answer not in ("f", "feedback"):
                break
            collect_feedback(input, screen="retry")
        if answer in ("n", "no", "q"):
            cfg.hold_open()
            return 0
    return 1


def _changed_review_card(cur, review, key):
    """Build an unhinted review only from changed art linked to its source."""
    source = next((card for card in cur["cards"] if card["id"] == key), None)
    variants = _review_variants(source or {})
    if not source or not variants:
        raise ValueError("card %s has no source-linked changed-art review bank" % key)
    variant_index = int(review.get("stage", 0)) % len(variants)
    card = dict(source)
    variant = variants[variant_index]
    for field in ("key_shape", "key_vocabulary"):
        if field not in variant:
            card.pop(field, None)
    card.update(variant)
    card.update({
        "id": "%s.R" % review["module_id"],
        "title": "Spaced changed-art edit",
        "kind": "review_edit", "artifact": "review",
        "show_target": True, "show_recipe": False, "variant_index": variant_index,
        "review_source_card_id": source["id"],
        "review_method_family": source["review_method_family"],
        "prompt": "Spaced edit retrieval on changed art: %s" % card["prompt"],
        "lesson_benefit": (
            "retrieve the module's Neovim operation on unfamiliar art, not only its wording"),
    })
    return card


def _run_review_edit(cfg, cur, progress, key, review):
    card = _changed_review_card(cur, review, key)
    base = (_artifact_path(cfg, card).parent / "reviews"
            if card.get("history_source_provenance") else
            _paths(cfg)["projects"] / card["project_id"] / "reviews")
    path = base / ("review-%s.txt" % key.replace(".", "-"))
    if path.exists():
        _checkpoint(cfg, card, path, "previous")
    _write_lines_atomic(path, card["start"])
    before = _card_lines(card, card["start"])
    keylog = str(_next_attempt_keylog(base, "keys-%s" % key.replace(".", "-")))
    print("\nSPACED EDIT RETRIEVAL  ·  changed-art variant %d" % (
        card["variant_index"] + 1))
    print("DO THIS: %s" % card["prompt"])
    lesson = _write_session_lesson(cfg, cur, progress, card)
    if not _show_lesson_screen(cfg, card, lesson):
        cfg.hold_open()
        return False, card, path, None
    with _CursorReceiptEnv(path, keylog, 1) as cursor_env:
        native_receipt = _run_native_editor(cfg, card, path, keylog, lesson, before)
    got = _read_lines(path, card.get("preserve_trailing_whitespace", False))
    receipt = _read_cursor_receipt(cursor_env.receipt, cursor_env.token, path)
    replay = _attempt_replay(
        cfg, card, keylog, before, got, receipt,
        require_typed_input=_typed_input_required(cfg))
    if receipt:
        replay["cursor_receipt"] = receipt
    method_error = _required_method_error(cfg, card, replay)
    if method_error:
        replay["method_evidence_error"] = method_error
    passed = (got == _card_lines(card, card["target"])
              and method_error is None)
    cursor_error = _cursor_goal_error(card, replay)
    if cursor_error:
        replay["method_evidence_error"] = cursor_error
        passed = False
    if native_receipt:
        replay["native_preview"] = native_receipt
        if not native_receipt["ready"]:
            passed = False
            replay["method_evidence_error"] = " ".join(native_receipt["reasons"])
    if not passed:
        _checkpoint(cfg, card, path, "failed")
        _write_lines_atomic(path, card["start"])
    return passed, card, path, replay


def run_review(cfg, cur, progress, key, review):
    _bind_curriculum(cfg, cur)
    before_progress = project(cur, read_events(cfg))
    before_badges = {b["id"] for b in _badge_rows(cfg, cur, before_progress) if b["earned"]}
    q = _review_question(cur, progress, review["module_id"], review.get("question_id"))
    print("Spaced review — changed conceptual variant for %s" % review["module_id"])
    print("DO THIS: retrieve the principle and choose the best-supported answer.")
    question_evidence = {}
    right, chosen = ask_question(q, rendered=cfg.question_rendered,
                                 evidence=question_evidence)
    if right is None:
        return 0
    edit_passed, review_card, artifact_path, edit_replay = (False, None, None, None)
    if right:
        edit_passed, review_card, artifact_path, edit_replay = _run_review_edit(
            cfg, cur, progress, key, review)
    completed = bool(right and edit_passed)
    max_stage = len(cur["review_intervals_hours"]) - 1
    stage = min(max_stage, review.get("stage", 0) + (1 if completed else 0))
    if not completed:
        stage = max(0, stage - 1)
    event = {"type": "review", "result": "pass" if completed else "fail",
                       "review_key": key, "review_stage": stage, "module_id": review["module_id"],
                       "question_id": q["id"], "choice": chosen,
                       "curriculum_revision": cur["revision"],
                       "question_evidence": question_evidence,
                       "edit_variant": (review_card or {}).get("variant_index"),
                       "next_due": _next_due(cur, stage if completed else 0)}
    if artifact_path is not None:
        event.update({"artifact": str(artifact_path),
                      "artifact_sha256": _hash_file(artifact_path)})
    if edit_replay and edit_replay.get("native_preview"):
        event["native_preview"] = edit_replay["native_preview"]
    append_event(cfg, event)
    if completed:
        _legacy_credit(cfg, "review-" + review["module_id"])
    else:
        changed = ("new paired stem plus changed-art edit variant"
                   if not right else "alternate changed-art edit variant")
        _schedule_remediation(cfg, {
            "id": key, "module_id": review["module_id"]
        }, "Q", changed, "spaced retrieval requires both concept and exact edit")
    updated = rebuild(cfg, cur)
    if completed:
        _celebrate_progress(cfg, cur, before_progress, updated, before_badges)
    card = next((c for c in cur["cards"] if c["id"] == key), None)
    if card is None:
        card = next(c for c in cur["cards"] if c["module_id"] == review["module_id"])
    replay = {"type": "review", "question": q, "chosen": chosen,
              "edit_replay": edit_replay,
              "edit_variant": (review_card or {}).get("variant_index")}
    _post_lesson(cfg, cur, card, updated, replay, completed=completed)
    if cfg.post_rendered:
        cfg.post_rendered()
    cfg.hold_open()
    return 0 if completed else 1


class SessionLock:
    def __init__(self, path):
        self.path = path
        self.owned = False
        self.token = "%d-%08x" % (os.getpid(), random.getrandbits(32))
        self.fd = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.fd = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(self.fd)
            self.fd = None
            raise RuntimeError("another v2 session is active")
        os.ftruncate(self.fd, 0)
        os.write(self.fd, self.token.encode("ascii"))
        os.fsync(self.fd)
        self.owned = True
        return self

    def __exit__(self, *_):
        if self.owned and self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
            self.fd = None
            self.owned = False


def _legacy_streak(state):
    counts, active = activity_days(state)
    today = _now().date()
    anchor = today if today in active else today - dt.timedelta(days=1)
    current, cursor = 0, anchor
    while cursor in active:
        current += 1
        cursor -= dt.timedelta(days=1)
    best = run = 0
    previous = None
    for day in sorted(active):
        run = run + 1 if previous and (day - previous).days == 1 else 1
        best = max(best, run)
        previous = day
    return current, best, sum(counts.values())


def done_today(events):
    """Lessons and reviews passed today; the daily-goal count used by run()."""
    today = _now().date().isoformat()
    return sum(1 for e in events if e.get("type") in ("card", "review")
               and e.get("result") == "pass" and str(e.get("at", "")).startswith(today))


def activity_days(state):
    """({day: completions}, {days with any practice}) from the dated logs.

    Shared by the streak line and the dashboard's 14-day strip (VD-58).
    """
    counts = {}
    root = Path(state)
    active = set()
    for path in root.glob("????-??-??.log") if root.exists() else []:
        try:
            day = dt.date.fromisoformat(path.stem)
            rows = [line for line in path.read_text(encoding="utf-8").splitlines()
                    if line.strip()]
        except (OSError, ValueError):
            continue
        count = sum(1 for line in rows if "result=" not in line)
        # VD-11: a failed v2 attempt is practice.  It keeps the daily streak
        # alive, but it never adds cap credit, all-time completions, or XP.
        attempted = any("result=%s" % ATTEMPT_RESULT in line for line in rows)
        if count:
            counts[day] = count
        if count or attempted:
            active.add(day)
    return counts, active


def _level(xp):
    titles = ["Apprentice", "Cell Editor", "Pose Builder", "Frame Crafter", "Tween Reader",
              "Scene Author", "Timing Artist", "Motion Editor", "Animator", "ASCII Director",
              "Loop Designer", "Texture Animator", "Motion Systems Artist",
              "Terminal Animation Director"]
    level = xp // 80 + 1
    title = (titles[level - 1] if level <= len(titles) else
             "%s +%d" % (titles[-1], level - len(titles)))
    floor = (level - 1) * 80
    return level, title, xp - floor, 80


def _module_card_map(cur, progress, module_id):
    module = next(m for m in cur["modules"] if m["id"] == module_id)
    passed = set(progress["passed_cards"])
    cells = []
    for card_id in module["card_ids"]:
        # VD-13: non-numeric ids such as the M0.P0 grammar primer crashed here.
        suffix = card_id.rsplit(".", 1)[1]
        label = "%02d" % int(suffix) if suffix.isdigit() else suffix
        cells.append("%s%s" % (label, _paint("✓", "ok") if card_id in passed else "○"))
    return "%s cards: %s" % (module_id, " ".join(cells))


def _revisit_rows(cur, progress):
    """VD-47: remediation in the learner's words, not validator ids."""
    cards = {card["id"]: card for card in cur["cards"]}
    rows = []
    for card_id, row in progress.get("active_remediations", {}).items():
        card = cards.get(card_id, {})
        title = card.get("title", card_id).split(" · ", 1)[-1]
        variant = row.get("changed_variant", "")
        if "edit" in variant and "question" not in variant:
            action = "redo the edit on new art"
        elif "edit" in variant:
            action = "a fresh question, then the edit on new art"
        else:
            action = "answer a fresh version of its question"
        rows.append((card_id, title, action))
    return rows


def learned_deck(cur, progress):
    """VD-47: every command family the learner has passed, oldest first.

    Returns [(family, reminder, times_used, first_card_id)]. This is the
    learner's flashcard deck: what they are expected to know already.
    """
    K = _keys_module()
    passed = set(progress.get("passed_cards", []))
    order = [cid for module in cur["modules"] for cid in module["card_ids"]]
    cards = {card["id"]: card for card in cur["cards"]}
    seen = {}
    for cid in order:
        card = cards.get(cid, {})
        if cid not in passed or not card.get("expected"):
            continue
        for family, meaning in K.families(card["expected"]):
            if family in ("[count]",):
                continue
            base = family.replace('"{reg}', "")
            reminder = (K.FAMILY_TEACH.get(base)
                        or K.FAMILY_TEACH.get(base.replace("[count]", "")) or meaning)
            key = reminder  # u and Ctrl-r share one card; so do 0 ^ $
            if key not in seen:
                seen[key] = [family, reminder, 0, cid]
            seen[key][2] += 1
    return [tuple(row) for row in seen.values()]


def print_learned(cur, progress):
    """`--learned`: the flashcard deck of commands already covered."""
    K = _keys_module()
    deck = learned_deck(cur, progress)
    print("WHAT YOU HAVE LEARNED · %d commands · oldest first" % len(deck))
    print("(× = lessons that used it; review the ones with low counts first)")
    for family, reminder, times, first in deck:
        print("  %s %-3s %s" % (_paint("✓", "ok"), "×%d" % times, reminder))
        example = K.example_for(family)
        if example:
            print("         e.g. %s" % example)
        print("         first met in %s" % first)
    symbols = learned_symbols(cur, progress)
    if symbols:
        print("")
        print("SYMBOLS WHOSE JOB DEPENDS ON WHERE THEY STAND")
        for symbol, jobs in symbols:
            print("  %-5s %s" % (symbol, " · ".join(jobs)))


def learned_symbols(cur, progress):
    """VD-48: one reminder line per symbol the learner has met in 2+ jobs."""
    K = _keys_module()
    passed = set(progress.get("passed_cards", []))
    cards = {card["id"]: card for card in cur["cards"]}
    jobs = {}
    for cid in (cid for module in cur["modules"] for cid in module["card_ids"]):
        if cid not in passed:
            continue
        for symbol, role in K.symbol_roles(cards.get(cid, {}).get("expected") or ""):
            if role == "key":
                continue
            short = K.SYMBOL_ROLES[(symbol, role)][1]
            jobs.setdefault(symbol, [])
            if short not in jobs[symbol]:
                jobs[symbol].append(short)
    return [(symbol, found) for symbol, found in jobs.items() if len(found) > 1]


def _journey_rows(cur, progress):
    marks = {"locked": "·", "available": "○", "learning": "◐",
             "check_ready": "◆", "review_pending": "↻", "mastered": _paint("✓", "ok")}
    current = progress.get("current_stage")
    rows = []
    for stage in cur["stages"]:
        cell = progress["stages"][stage["id"]]
        here = "  ← you are here" if stage["id"] == current else ""
        rows.append("%s %-2s %-29s %s %d/%d%s" % (
            marks[cell["state"]], stage["id"], stage["title"],
            _bar(cell["done"], cell["total"]), cell["done"], cell["total"], here))
    return rows


def print_tree(cur, progress, cfg=None, *, compact=False):
    marks = {"locked": "·", "available": "○", "learning": "◐",
             "check_ready": "◆", "review_pending": "↻", "mastered": _paint("✓", "ok")}
    if compact:
        nodes = []
        for stage in cur["stages"]:
            cell = progress["stages"][stage["id"]]
            nodes.append("%s%s %d/%d" % (
                marks[cell["state"]], stage["id"], cell["done"], cell["total"]))
        print("KEY  ○ open · ◐ learning · ◆ check · ↻ review · %s mastered · locked" % _paint("✓", "ok"))
        for start in range(0, len(nodes), 6):
            print(("STAGES  " if start == 0 else "        ") + " | ".join(nodes[start:start + 6]))
        due = sum(1 for r in progress["reviews"].values() if _due(r.get("next_due")))
        level, title, into, needed = _level(progress["xp"])
        print(_clip("XP %d · LEVEL %d %s %d/%d · reviews %d · learned %d (--learned)" % (
            progress["xp"], level, title, into, needed, due,
            len(learned_deck(cur, progress))), 70))
        revisit = _revisit_rows(cur, progress)
        if revisit:
            shown = " · ".join(card_id for card_id, _t, _a in revisit[:5])
            print(_clip("TO REVISIT  %s%s" % (shown, " +%d more" % (len(revisit) - 5)
                                               if len(revisit) > 5 else ""), 68))

        if cfg:
            streak, best, total = _legacy_streak(cfg.state)
            bold, _dim, off, _green, _red, _yellow = cfg.colours
            flame = _paint("🔥", "warn") if streak else ""
            best_text = (_paint("★ best ever", "warn") if streak and streak >= best
                         else "best %d" % best)
            print("%sstreak: %d day%s %s · %s · all-time %d%s" % (
                bold, streak, "" if streak == 1 else "s", flame, best_text, total, off))
        current = progress.get("current_stage") or "complete"
        nxt = next_card(cur, progress)
        print("current stage: %s · next: %s" % (
            current, nxt["id"] if nxt else "spaced review or course complete"))
        return
    print("YOUR JOURNEY · Neovim × ASCII animation")
    print("stills first (S0 → S7), then animation (A0 → A7); P is an optional side branch")
    for row in _journey_rows(cur, progress):
        print(row)
    revisit = _revisit_rows(cur, progress)
    if revisit:
        print("\nTO REVISIT · lessons coming back for spaced practice")
        for card_id, title, action in revisit:
            print("  ↻ %-7s %s — %s" % (card_id, title, action))
    deck = learned_deck(cur, progress)
    print("\nWHAT YOU HAVE LEARNED · %d commands (full deck with examples: vim-daily-gate --learned)"
          % len(deck))
    for _family, reminder, times, _first in deck:
        print("  %s %-3s %s" % (_paint("✓", "ok"), "×%d" % times, _clip(reminder, 90)))
    print("\nMODULES · each is one art project")
    for module in cur["modules"]:
        cell = progress["modules"][module["id"]]
        owners = ",".join(module.get("stage_ids", []))
        print("%s %-3s %-26s %d/%d  %-14s [%s] stages %s" % (
            marks[cell["state"]], module["id"], module["title"], cell["done"], cell["total"],
            cell["state"], module["node"], owners))
    due = sum(1 for r in progress["reviews"].values() if _due(r.get("next_due")))
    print("reviews due: %d   ledger errors: %d" % (due, progress["ledger_errors"]))
    level, title, into, needed = _level(progress["xp"])
    print("XP: %d   LEVEL %d %s: %d/%d toward next level" % (
        progress["xp"], level, title, into, needed))
    print("\nBADGES")
    for badge in _badge_rows(cfg, cur, progress):
        mark = _paint("✓", "ok") if badge["earned"] else "○"
        icon = _paint(badge.get("icon", badge["glyph"]), badge.get("style", "warn"))
        print("  %s %s %s · %d/%d" % (
            mark, icon, badge["name"], badge["have"], badge["need"]))
    if cfg:
        streak, best, total = _legacy_streak(cfg.state)
        bold, _dim, off, _green, _red, _yellow = cfg.colours
        flame = _paint("🔥", "warn") if streak else ""
        best_text = (_paint("★ best ever", "warn") if streak and streak >= best
                     else "best: %d" % best)
        print("%sstreak: %d day%s %s   %s   all-time completions: %d%s" % (
            bold, streak, "" if streak == 1 else "s", flame, best_text, total, off))
    nxt = next_card(cur, progress)
    print("current stage: %s" % (progress.get("current_stage") or "main path complete"))
    print("next: %s" % ((nxt["id"] + " " + nxt["title"])
                        if nxt else "spaced review or course complete"))


# VD-58: the interactive dashboard is a Textual app in a managed venv
# (install.sh). The runtime itself stays stdlib-only: it launches the app as a
# child process and falls back to the static print_tree when the venv, a
# terminal, or colour-capable TERM is missing.
DASHBOARD_UNAVAILABLE = 3  # dashboard_tui.py exit code: Textual not importable


def dashboard_python():
    venv = os.environ.get("VIM_DAILY_VENV") or os.path.join(
        os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share"),
        "vim-daily-venv")
    python = os.path.join(venv, "bin", "python")
    return python if os.access(python, os.X_OK) else None


def open_dashboard(cfg, cur, progress):
    """`--dashboard` / `--tree` in a terminal: the interactive journey view."""
    sys_ = __import__("sys")
    tty = sys_.stdin.isatty() and sys_.stdout.isatty()
    reason = None
    python = None
    if not tty:
        reason = "not a terminal"
    elif os.environ.get("TERM", "") in ("", "dumb"):
        reason = "TERM=dumb"
    else:
        python = dashboard_python()
        if python is None:
            reason = "Textual venv missing; run install.sh"
    if python:
        script = Path(__file__).resolve().with_name("dashboard_tui.py")
        code = subprocess.call([python, str(script), "--state", str(cfg.state),
                                "--share", str(cfg.share), "--target", str(cfg.target)])
        if code != DASHBOARD_UNAVAILABLE:
            return code
        reason = "Textual is not importable by %s; run install.sh" % python
    print_tree(cur, progress, cfg)
    if tty:
        print("(interactive dashboard unavailable: %s)" % reason)
    return 0


def export_progress(cur, progress):
    payload = dict(progress)
    payload["next_card"] = (next_card(cur, progress) or {}).get("id")
    payload["due_reviews"] = sum(1 for r in progress["reviews"].values() if _due(r.get("next_due")))
    json.dump(payload, __import__("sys").stdout, indent=1, ensure_ascii=False)
    print()


LAST_VIEW = {"views": None}


_VIEWER_MODULE = None


def _viewer_module():
    """Load share/viewer.py next to this file (the gate does not put share/ on sys.path)."""
    global _VIEWER_MODULE
    if _VIEWER_MODULE is None:
        import importlib.util
        path = Path(__file__).with_name("viewer.py")
        spec = importlib.util.spec_from_file_location("vim_daily_viewer", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _VIEWER_MODULE = module
    return _VIEWER_MODULE


def _project_directory(cfg, module):
    """Resolve a current or historical folder by the manifest's module identity."""
    base = _paths(cfg)["projects"] / module["project_id"]
    if not (base / "manifest.json").exists():
        # A project renamed after the learner saved work keeps its old folder;
        # find it by the module id its manifest records.
        for manifest_path in sorted(_paths(cfg)["projects"].glob("*/manifest.json")):
            try:
                if json.loads(manifest_path.read_text(encoding="utf-8")).get("module_id") == module["id"]:
                    base = manifest_path.parent
                    break
            except (OSError, ValueError):
                continue
    return base


def _lesson_view_preserving_whitespace(card, rows, before=None):
    """Build a viewer View without normalising width-bearing trailing spaces."""
    V = _viewer_module()
    frames = V.split_frames(rows, card.get("frame_slices"))
    title = "%s · %s" % (card["id"], card.get("title", ""))
    if card.get("navigation_only"):
        # This is cursor travel over untouched art, not artwork animation.
        study = _lesson_tui()
        first = rows[0] if rows else ""
        initial = {"row": 1, "column": _cell_width(first[:len(first) - len(first.lstrip())]) + 1}
        diagnostic_frames = []
        for position in (initial, card["cursor_goal"]):
            art, carets = study._navigation_overlay(rows, position)
            diagnostic_frames.append([line for row, caret in zip(art, carets)
                                      for line in (row, caret)])
        return V.View(title + " · unchanged artwork · not animation",
                      diagnostic_frames, labels=["cursor start", "cursor goal"], kind="navigation")
    if frames and len(frames) > 1 and card.get("artifact_mode") != "still-study":
        holds = {i: "hold" for i in range(1, len(frames)) if frames[i] == frames[i - 1]}
        return V.View(title, frames, holds=holds)
    start = list(before if before is not None else card.get("start", []))
    if not start or start == list(rows):
        return V.View(title + " · still study · not animation", [list(rows)], labels=["yours"], kind="still")
    return V.View(title, [start, list(rows)], labels=["before", "yours"], kind="edit")


def project_view(cfg, cur, module_id):
    """The module's verified project strip as a viewer View, or None."""
    V = _viewer_module()
    module = next((m for m in cur["modules"] if m["id"] == module_id), None)
    if not module or module.get("preview_mode") == "layers":
        return None
    base = _project_directory(cfg, module)
    try:
        manifest = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    card = next((c for c in cur["cards"] if c["id"] == manifest.get("current_card")), None)
    if not card:
        return None
    lines = _read_lines(base / "strip.txt", card.get("preserve_trailing_whitespace", False))
    frames = V.split_frames(lines, card.get("frame_slices") if card else None)
    if not frames or len(frames) < 2:
        return None
    holds = {i: "hold" for i in range(1, len(frames)) if frames[i] == frames[i - 1]}
    return V.View("%s · %s (whole project)" % (module_id, module.get("title", "")),
                  frames, holds=holds, kind="project")


def watch_your_work(cfg, cur, card, path):
    """VD-62: after a pass, play what the learner just made (first-class viewer)."""
    V = _viewer_module()
    try:
        rows = _read_lines(path, card.get("preserve_trailing_whitespace", False))
    except OSError:
        return None
    views = []
    if card.get("kind") == "module_check":
        views.append(project_view(cfg, cur, card["module_id"]))
    views.append(_lesson_view_preserving_whitespace(card, rows))
    if card.get("kind") != "module_check" and card.get("artifact") != "transfer":
        views.append(project_view(cfg, cur, card["module_id"]))
    views = [v for v in views if v]
    if not views:
        return None
    LAST_VIEW["views"] = views
    # The preference disables automatic playback, not the explicit Watch
    # action on the held result screen. Keep the current views available.
    if not V.enabled():
        return None
    return V.play(views)


def completed_gallery(cfg, cur, progress):
    """Every passed lesson plus eligible canonical module rewards as Views.

    Uses the per-lesson checkpoints (`<card>-before.txt`, `<card>-after.txt`)
    that every pass already writes, so a later lesson overwriting the project
    strip does not lose earlier animations.  Retrospective module entries are
    read-only reward previews and are never learner checkpoints."""
    V = _viewer_module()
    passed = set(progress.get("passed_cards", []))
    order = {card["id"]: index for index, card in enumerate(cur["cards"])}
    cards = {card["id"]: card for card in cur["cards"]}
    found = {}
    for after in _paths(cfg)["projects"].glob("**/checkpoints/*-after.txt"):
        card_id = after.name[:-len("-after.txt")]
        card = cards.get(card_id)
        if card is None or card_id not in passed:
            continue
        try:
            rows = _read_lines(after, card.get("preserve_trailing_whitespace", False))
            before_path = after.with_name(card_id + "-before.txt")
            before = (_read_lines(before_path, card.get("preserve_trailing_whitespace", False))
                      if before_path.exists() else None)
        except OSError:
            continue
        view = _lesson_view_preserving_whitespace(card, rows, before=before)
        previous = found.get(card_id)
        if previous is None or after.stat().st_mtime > previous["mtime"]:
            found[card_id] = {"card_id": card_id, "module_id": card["module_id"],
                              "title": card.get("title", ""), "view": view,
                              "frames": len(view.frames), "kind": view.kind,
                              "mtime": after.stat().st_mtime}
    gallery = sorted(found.values(), key=lambda row: order.get(row["card_id"], 0))
    # C34: older learners have genuine passed-card evidence but no generated
    # reward-endcap event.  Add a read-only canonical animation entry; this is
    # deliberately separate from the learner's checkpoint and never changes
    # ``passed_cards`` or the append-only ledger.
    for reward in _retro_module_rewards().gallery_rewards(cur, progress):
        animation = reward["animation"]
        view = _module_reward_view(animation, module_id=reward["module_id"],
                                   status=reward["status"])
        gallery.append({
            "card_id": "%s.RETRO" % reward["module_id"],
            "module_id": reward["module_id"],
            "title": "%s · %s" % (reward["title"],
                                    "prior study preview" if reward["status"] == "prior_study"
                                    else "mastered endcap"),
            "view": view,
            "frames": len(view.frames),
            "kind": "module_reward",
            "status": reward["status"],
            "prior_study": reward["prior_study"],
            "mastered": reward["mastered"],
            "legacy_completion": reward["legacy_completion"],
            "credit": reward["credit"],
            "mtime": 0,
        })
    return gallery


def _show_retroactive_module_rewards(cfg, cur, progress):
    """Preview unmastered retro rewards once during a normal launch.

    This is a display-only route.  It intentionally runs before the daily
    cap/cooldown decision, so an existing learner sees the new reward on the
    next launch even when no lesson is due, while ``VIM_DAILY_SKIP`` and
    machine-facing quiet modes remain silent.
    """

    rewards = _retro_module_rewards().startup_rewards(cur, progress)
    if not rewards:
        return False
    viewer = _viewer_module()
    if not viewer.enabled():
        return False
    views = [_module_reward_view(row["animation"], module_id=row["module_id"],
                                status=row["status"])
             for row in rewards]
    print("RETROSPECTIVE MODULE REWARDS · prior study previews · no mastery awarded")
    LAST_VIEW["views"] = views
    viewer.play(views)
    return True


def replay_last_view():
    """`v` on the held result page: watch the last passed work again."""
    views = LAST_VIEW.get("views")
    if not views:
        return None
    return _viewer_module().play(views)


def view_command(cfg, cur, progress, args):
    """`--view [MODULE|LESSON]`: play a module's project strip (default: latest
    module) or one passed lesson's saved work."""
    module_id = args[0] if args else None
    if module_id and any(module["id"] == module_id for module in cur["modules"]):
        # A retroactive reward is a complete canonical sequence even when the
        # learner has no saved module strip for the newly inserted endcap.
        reward_items = [row for row in completed_gallery(cfg, cur, progress)
                        if row["module_id"] == module_id and row.get("kind") == "module_reward"]
        if reward_items:
            _viewer_module().play([reward_items[-1]["view"]])
            return 0
    if module_id and any(card["id"] == module_id for card in cur["cards"]):
        item = next((row for row in completed_gallery(cfg, cur, progress)
                     if row["card_id"] == module_id), None)
        if item is None:
            print("%s has no saved work to watch yet" % module_id)
            return 1
        project = project_view(cfg, cur, item["module_id"])
        _viewer_module().play([item["view"]] + ([project] if project else []))
        return 0
    if module_id is None:
        passed = [row for row in read_events(cfg)
                  if row.get("type") == "card" and row.get("result") == "pass"]
        module_id = passed[-1].get("module_id") if passed else None
    if module_id is None:
        print("nothing to watch yet: pass a lesson first")
        return 1
    view = project_view(cfg, cur, module_id)
    if view is None:
        print("%s has no playable project strip yet" % module_id)
        return 1
    _viewer_module().play([view])
    return 0


def preview_project(cfg, cur, module_id, speed=0.35):
    module = next((m for m in cur["modules"] if m["id"] == module_id), None)
    if not module:
        print("no such module: %s" % module_id)
        return 1
    base = _project_directory(cfg, module)
    path = base / "strip.txt"
    manifest_path = base / "manifest.json"
    if not path.exists() or not manifest_path.exists():
        print("%s has no verified project strip yet" % module_id)
        return 1
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except ValueError:
        print("invalid project manifest: %s" % manifest_path)
        return 1
    card = next((c for c in cur["cards"] if c["id"] == manifest.get("current_card")), None)
    lines = _read_lines(path, card.get("preserve_trailing_whitespace", False))
    if not card:
        print("manifest refers to an unknown card")
        return 1
    if card.get("preview_mode") == "layers" or module.get("preview_mode") == "layers":
        print("%s is a back-to-front layer study, not a frame list:" % module_id)
        print(path.read_text(encoding="utf-8"), end="")
        return 0
    slices = card.get("frame_slices")
    if not slices or sum(slices) != len(lines):
        print("cannot parse verified frame boundaries for %s" % card["id"])
        return 1
    if len(set(slices)) != 1:
        print("preview blocked: unequal frame heights %s" % slices)
        print("Pad the shorter frames before playback; the strip was preserved at %s" % path)
        return 1
    frames, offset = [], 0
    for height in slices:
        frames.append(lines[offset:offset + height])
        offset += height
    interactive = __import__("sys").stdout.isatty() and speed > 0
    for index, frame in enumerate(frames):
        hold = index > 0 and frame == frames[index - 1]
        if interactive:
            print("\033[2J\033[H", end="")
        hold_reason = (card.get("animation", {}).get("hold_reason") if hold else None)
        suffix = "  HOLD" + ((": " + hold_reason) if hold_reason else "") if hold else ""
        print("%s frame %d/%d%s" % (module_id, index + 1, len(frames), suffix))
        print("\n".join(frame))
        if interactive:
            time.sleep(speed)
    return 0


def run(cfg, argv, *, force=False):
    """Lock interactive launches before loading their curriculum contract."""
    mode = argv[0] if argv else "run"
    interactive_modes = {"run", "--force", "--if-due", "--continue", "--card",
                         "--practice-card", "--practice-review", "--quiz"}
    sys_ = __import__("sys")
    deck_write = mode in ("--deck-miss", "--quiz")
    interactive = (mode in interactive_modes and sys_.stdin.isatty()
                   and sys_.stdout.isatty())
    native_handoff = bool(os.environ.get("VIM_DAILY_NATIVE_WINDOW")
                          and os.environ.get("VIM_DAILY_NATIVE_ACK_SOCKET"))
    if not deck_write and not interactive and not native_handoff:
        return _run_session(cfg, argv, force=force)
    lock = SessionLock(_paths(cfg)["lock"])
    try:
        lock.__enter__()
    except RuntimeError as exc:
        print("Tutor session not started: %s." % exc)
        print("The active popup owns progress; close it before starting another lesson.")
        cfg.hold_open()
        return 1
    try:
        return _run_session(cfg, argv, force=force, session_lock=lock)
    finally:
        lock.__exit__(None, None, None)


def _run_session(cfg, argv, *, force=False, session_lock=None):
    global LAST_RUN_CARD_ID, LAST_RUN_KIND, TEXTUAL_ROUTE
    LAST_RUN_CARD_ID = None
    LAST_RUN_KIND = None
    TEXTUAL_ROUTE = None
    LAST_VIEW["views"] = None
    cur = load_curriculum(cfg.share)
    _bind_curriculum(cfg, cur)
    events = read_events(cfg)
    progress = project(cur, events)
    save_projection(cfg, progress)
    _native_handoff_ack(cur)
    mode = argv[0] if argv else "run"
    continuation = mode == "--continue"
    cfg.practice = mode in ("--practice-card", "--practice-review")
    FEEDBACK["path"] = feedback_path(cfg.state)
    note_feedback_context(revision=cur.get("revision"))
    if mode == "--feedback":
        print_feedback(cfg.state)
        return 0
    if mode == "--view":
        return view_command(cfg, cur, progress, argv[1:])
    if mode == "--learned":
        print_learned(cur, progress)
        return 0
    # Memory plan 2026-09-29: flashcard deck routes (share/deck.py).
    if mode == "--deck":
        return _deck_module().browse(cur, progress, argv[1] if len(argv) > 1 else None)
    if mode == "--deck-miss":
        return _deck_module().record_misses(__import__("sys").modules[__name__], cfg, cur,
                                            progress, argv[1:])
    if mode == "--quiz":
        count = int(argv[1]) if len(argv) > 1 and argv[1].isdigit() else None
        return _deck_module().run_quiz(__import__("sys").modules[__name__], cfg, cur, progress,
                                       count or _deck_module().QUIZ_DEFAULT)
    DECK_WEAK.clear()
    DECK_WEAK.update(progress.get("deck", {}).get("weak_families", []))
    if mode == "--dashboard" or (mode == "--tree" and "--static" not in argv[1:]):
        return open_dashboard(cfg, cur, progress)
    if mode in ("--tree", "--status"):
        print_tree(cur, progress, cfg)
        return 0
    if mode == "--export-progress":
        export_progress(cur, progress)
        return 0
    if mode == "--list":
        passed = set(progress["passed_cards"])
        for card in cur["cards"]:
            print("%s  %-16s %-22s %s" % (_paint("✓", "ok") if card["id"] in passed else "·", card["id"], card["kind"], card["title"]))
        return 0
    card = None
    practice_review = None
    if mode in ("--card", "--practice-card"):
        wanted = argv[1] if len(argv) > 1 else ""
        card = next((c for c in cur["cards"] if c["id"] == wanted), None)
        if not card:
            print("no such v2 card: %s" % wanted)
            return 1
        if mode == "--card":
            stage_id = card["stage_owner"]
            state = progress["stages"][stage_id]["state"]
            if state == "locked":
                print("%s is locked by stage %s prerequisites" % (wanted, stage_id))
                return 1
            if wanted in set(progress["passed_cards"]):
                print("%s is already complete; use the result-page repeat control for uncredited practice" % wanted)
                return 1
            stage = next(row for row in cur["stages"] if row["id"] == stage_id)
            stage_next = next((cid for cid in stage["card_ids"]
                               if cid not in set(progress["passed_cards"])), None)
            if wanted != stage_next:
                print("%s is not the current card for stage %s; complete %s first" % (
                    wanted, stage_id, stage_next or "the stage"))
                return 1
        force = True
    elif mode == "--practice-review":
        wanted = argv[1] if len(argv) > 1 else ""
        card = next((c for c in cur["cards"] if c["id"] == wanted), None)
        if not card or not _review_variants(card):
            print("no changed-art review bank for: %s" % wanted)
            return 1
        practice_review = (wanted, {
            "module_id": card["module_id"], "stage": 0, "question_id": None,
        })
        force = True
    elif mode == "--project":
        wanted = argv[1] if len(argv) > 1 else None
        module = next((m for m in cur["modules"] if m["id"] == wanted), None)
        if not module:
            print("usage: vim-drill --project M0")
            return 1
        path = _paths(cfg)["projects"] / module["project_id"] / "strip.txt"
        print(path)
        if path.exists():
            print(path.read_text(encoding="utf-8"), end="")
        return 0
    elif mode == "--preview":
        wanted = argv[1] if len(argv) > 1 else ""
        try:
            speed = float(argv[2]) if len(argv) > 2 else 0.35
        except ValueError:
            print("preview speed must be seconds per frame")
            return 1
        return preview_project(cfg, cur, wanted, speed)
    elif mode not in ("run", "--force", "--if-due", "--due-quiet", "--continue"):
        return None

    # Normal CLI, manual popup and hourly popup all own the same catch-up
    # display. Explicit card/practice and quiet machine checks stay scoped.
    if (mode in ("run", "--force", "--if-due") and not cfg.practice
            and __import__("sys").stdin.isatty() and __import__("sys").stdout.isatty()
            and not any(os.environ.get(name) for name in
                        ("VIM_DAILY_SKIP", "VIM_DAILY_ACTIVE", "NVIM"))):
        _show_retroactive_module_rewards(cfg, cur, progress)
    explicit_force = force or mode in ("--force", "--card", "--practice-card", "--practice-review")
    if not explicit_force:
        if (not continuation and
                (os.environ.get("VIM_DAILY_SKIP") or os.environ.get("VIM_DAILY_ACTIVE")
                 or os.environ.get("NVIM"))):
            return 1 if mode == "--due-quiet" else 0
        done = done_today(events)
        try:
            since = _now().timestamp() - os.stat(cfg.stamp).st_mtime
        except OSError:
            since = 999999
        # `--continue` is an explicit request made inside the already-open
        # popup. It preserves the daily cap and normal review/card scheduler;
        # only the hourly re-prompt cooldown is waived for this same session.
        if done >= cfg.target or (not continuation and since < cfg.cooldown):
            if mode == "--due-quiet":
                return 1
            if mode != "--if-due":
                print("No v2 lesson due. %d/%d done today." % (done, cfg.target))
            return 0
        if mode == "--due-quiet":
            return 0
    if not __import__("sys").stdin.isatty() or not __import__("sys").stdout.isatty():
        return 0
    review = due_review(cur, progress)
    candidate = card or next_card(cur, progress)
    review_due_now = (False if cfg.practice else
                      should_run_review(events, review, candidate, explicit_force))
    native_card = (next((row for row in cur["cards"] if row["id"] == review[0]), None)
                   if review_due_now else candidate)
    if practice_review:
        native_card = card
    if (os.environ.get("VIM_DAILY_POPUP") and os.environ.get("TMUX")
            and (native_card or {}).get("medium") == "proportional-sjis"):
        # No lock, attempt or grade is created in the popup. The same gate
        # resumes the chosen scheduler route in a normal native-capable pane.
        # The child loads and locks its own contract before showing a lesson.
        # Release the selector's launch lock before the child starts.
        if session_lock is not None:
            session_lock.__exit__(None, None, None)
        try:
            window = _native_module("native_window_route").open_window(cfg, argv)
        except Exception as exc:
            print("Native tutor window unavailable: %s. No lesson was attempted." % exc)
            return 1
        print("Native JIS lesson opened in temporary tmux window %s." % window)
        return 0
    lock = session_lock or SessionLock(_paths(cfg)["lock"])
    if session_lock is None:
        try:
            lock.__enter__()
        except RuntimeError as exc:
            print("Tutor session not started: %s." % exc)
            print("The active popup owns progress; close it before starting another lesson.")
            cfg.hold_open()
            return 1
    try:
        # A held result may leave wrapped prompt fragments in a compact tmux
        # popup. Every newly selected route starts on a clean terminal page.
        _clear_if_tty()
        if practice_review:
            LAST_RUN_CARD_ID = practice_review[0]
            LAST_RUN_KIND = "review"
            return run_review(cfg, cur, progress, practice_review[0], practice_review[1])
        # Memory plan 2026-09-29: before the first lesson of the day, up to
        # three deck items from the upcoming lesson's families (s skips).
        if mode in ("run", "--force", "--if-due") and not cfg.practice:
            upcoming = review[0] if review_due_now else (candidate or {}).get("id")
            if _deck_module().maybe_warmup(__import__("sys").modules[__name__], cfg, cur,
                                           progress, events, upcoming):
                _clear_if_tty()
        if review_due_now:
            LAST_RUN_CARD_ID = review[0]
            LAST_RUN_KIND = "review"
            return run_review(cfg, cur, progress, review[0], review[1])
        card = candidate
        if not card:
            print_tree(cur, progress, cfg)
            return 0
        LAST_RUN_CARD_ID = card["id"]
        LAST_RUN_KIND = card["kind"]
        if card["kind"] == "concept":
            return run_concept(cfg, cur, progress, card)
        return run_edit(cfg, cur, progress, card)
    finally:
        if session_lock is None:
            lock.__exit__(None, None, None)
