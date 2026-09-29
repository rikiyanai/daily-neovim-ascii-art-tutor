"""Runtime for the project-based v2 curriculum (VD-09).

No third-party packages. Progress is a projection of events-v2.jsonl; deleting
the projection cannot erase learning history. The legacy runner imports this
module and passes its editor/keylog helpers in through RuntimeConfig.
"""

from __future__ import annotations

import datetime as dt
import fcntl
import hashlib
import json
import os
import random
import re
import shutil
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


# The launcher reads this after a held result so `r` can repeat the exact
# lesson route rather than accidentally selecting the next card.
LAST_RUN_CARD_ID = None
LAST_RUN_KIND = None


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
                      "question_placement", "master_habits", "master_stages"):
            if not card.get(field):
                raise ValueError("card %s is missing grammar-first field %s" % (
                    card["id"], field))
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
                       and candidate.get("show_recipe") is False), None)
        if review is None:
            raise ValueError("%s has no hidden changed-art review for %s" % (guided_id, family))
        variants = review.get("review_variants") or review.get("variants") or []
        command_review_rows.append({
            "grammar_family": family,
            "guided_card_id": guided_id,
            "review_card_id": review["id"],
            "changed_art_variants": len(variants),
            "keys_hidden": True,
            "evidence": "target-linked changed-art retrieval; method enforcement reported separately",
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


def append_event(cfg, event):
    paths = _paths(cfg)
    paths["events"].parent.mkdir(parents=True, exist_ok=True)
    row = dict(event)
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
    modules = {}
    for module in cur["modules"]:
        done = sum(1 for cid in module["card_ids"] if cid in passed)
        required_review_ids = module.get("required_review_card_ids", [])
        reviews_done = sum(
            1 for cid in required_review_ids
            if any(key == cid and stage >= 1 for key, stage in earned_review_stages)
        )
        prerequisites_met = all(modules[p]["state"] == "mastered"
                                for p in module.get("prerequisites", []))
        if done == len(module["card_ids"]) and reviews_done == len(required_review_ids):
            state = "mastered"
        elif done == len(module["card_ids"]):
            state = "review_pending"
        elif not prerequisites_met:
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
        }
    out = {
        "schema": "vim-daily/progress@2", "revision": cur["revision"], "passed_cards": sorted(passed),
        "attempts": attempts, "question_attempts": question_attempts, "reviews": reviews,
        "passed_questions": sorted(passed_questions),
        "check_concepts": sorted(check_concepts),
        "modules": modules, "completed_at": completed_at, "ledger_errors": errors,
        "active_remediations": active_remediations,
    }
    badges = []
    if passed:
        badges.append("first-step")
    if any(cid.endswith(".06") for cid in passed):
        badges.append("transfer")
    if modules["M0"]["state"] == "mastered":
        badges.append("first-module")
    if modules["M4"]["state"] == "mastered":
        badges.append("midpoint-tween")
    if modules["M7"]["state"] == "mastered":
        badges.append("playable-strip")
    if modules["M9"]["state"] == "mastered":
        badges.append("animator")
    if modules.get("M10", {}).get("state") == "mastered":
        badges.append("corpus-reader")
    out["xp"] = 10 * len(passed) + 3 * len(earned_review_stages)
    out["badges"] = badges
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
    for module in cur["modules"]:
        cell = progress["modules"][module["id"]]
        if cell["state"] == "locked":
            continue
        for cid in module["card_ids"]:
            if cid not in passed:
                return next(c for c in cur["cards"] if c["id"] == cid)
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


def _compact_question_text(value, width=64):
    """Wrap compact prompts deliberately instead of letting the terminal do it."""
    paragraphs = []
    for paragraph in str(value).split("\n\n"):
        # ASCII evidence is layout, not prose. Joining these rows destroys the
        # before/after comparison precisely on the small popup that needs the
        # compact prompt.
        if "│" in paragraph:
            paragraphs.append(paragraph.rstrip())
            continue
        line = " ".join(part.strip() for part in paragraph.splitlines() if part.strip())
        if line:
            paragraphs.append(textwrap.fill(line, width=width))
    return "\n".join(paragraphs)


def _compact_choice_text(value, width=62):
    """Keep both halves readable as two labeled compact rows."""
    value = " ".join(str(value).split())
    for marker in (" · V: ", " | NEOVIM: "):
        if marker in value:
            animation, neovim = value.split(marker, 1)
            animation = animation.removeprefix("ANIMATION: ").removeprefix("A: ")
            neovim = neovim.removeprefix("NEOVIM: ").removeprefix("V: ")
            return "ANIM: %s\n     VIM: %s" % (
                textwrap.shorten(animation, width=width - 6, placeholder="…"),
                textwrap.shorten(neovim, width=width - 5, placeholder="…"),
            )
    return textwrap.shorten(value, width=width, placeholder="…")


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
    if __import__("sys").stdout.isatty():
        # Neovim has just exited on paired after-questions. Without a fresh
        # page its final grid remains behind the short question text and makes
        # choices appear interleaved with unrelated terminal content.
        print("\033[2J\033[H", end="")
    prompt = q.get("compact_prompt", q["prompt"]) if compact else q["prompt"]
    displayed_choices = q["choices"]
    if compact:
        prompt = _compact_question_text(prompt)
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
        prompt,
        "\n".join("%s) %s" % (letters[shown], displayed_choices[original])
                  for shown, original in enumerate(order)),
    )
    if rendered:
        rendered(q, order)
    while True:
        try:
            answer = input_fn(
                "  answer (a-%s) · y copies this question: " % letters[-1]
            ).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None, None
        if answer == "y":
            if _copy_text_to_clipboard(clipboard_page):
                print("  copied the complete question and choices to the macOS clipboard")
            else:
                print("  clipboard copy is unavailable; this did not count as an attempt")
            continue
        if answer in letters and len(answer) == 1:
            break
        print("  answer with %s, or y to copy; this did not count as an attempt" %
              ", ".join(letters))
    chosen = order[letters.index(answer)]
    if evidence is not None:
        evidence.update({"raw_answer": answer, "semantic_choice": chosen})
    right = chosen == q["correct_choice"]
    print("  %s" % q["feedback"][chosen])
    return right, chosen


_KEY_TOKEN = re.compile(r"<([^>]+)>")
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
    """Explain a selected choice without exposing curriculum/runtime metadata."""
    correct = q["correct_choice"]
    choices = q.get("choices", [])
    feedback = q.get("feedback", [])
    clip_width = 64 if compact else 120
    if not isinstance(chosen, int) or chosen < 0 or chosen >= len(choices):
        print("  YOUR ANSWER  (not recorded)")
        return
    print("  YOUR ANSWER  %s" % _clip(choices[chosen], clip_width))
    if chosen != correct:
        why_missed = (feedback[chosen] if chosen < len(feedback)
                      else "That choice does not match the shown result.")
        print("  WHY IT MISSES  %s" % _clip(_concept_text(why_missed), clip_width))
        print("  CORRECT ANSWER  %s" % _clip(choices[correct], clip_width))
    concept = feedback[correct] if correct < len(feedback) else ""
    concept = _concept_text(concept)
    if concept:
        print("  CONCEPT  %s" % _clip(concept, clip_width))


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
    if card.get("artifact") == "transfer":
        return base / ("transfer-%s.txt" % card["id"])
    return base / "strip.txt"


def _read_lines(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
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
    return {
        "module": module,
        "why": [
            "Motion intent: %s." % module["meaning"].rstrip("."),
            "Authoring principle: %s." % module["principle"].rstrip("."),
            "Failure to watch: %s." % module["defect"].rstrip("."),
        ],
        "buys": card["lesson_benefit"],
        "source": card.get("source_ref") or module["source_ref"],
    }


_KEYS_MODULE = None


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
    if new_lines:
        lines.append("FIRST TIME YOU NEED THESE  (no earlier lesson showed them)")
        lines += [clip(line) for line in new_lines]
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


def _progress_line(cfg, progress, card):
    cell = progress["modules"][card["module_id"]]
    streak, best, total = _legacy_streak(cfg.state)
    flame = " 🔥" if streak >= 3 else ""
    level, title, into, needed = _level(progress["xp"])
    return ("PROGRESS  %s %d/%d %s  ·  XP %d  ·  LEVEL %d %s %d/%d  ·  today %d/%d  ·  streak %d day%s%s  ·  best %d  ·  %d drill%s all time" % (
        card["module_id"], cell["done"], cell["total"], cell["state"], progress["xp"], level, title, into, needed,
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
    rows = []
    for row_number in range(slices[0]):
        row = "   ".join("│" + frame[row_number] for frame in frames)
        # Do not use prose clipping here: textwrap collapses runs of spaces,
        # which would silently destroy fixed-width registration in TARGET.
        available = width - 2
        if len(row) > available:
            row = row[:max(0, available - 1)] + "…"
        rows.append("  " + row)
    return rows


def _write_session_lesson(cfg, cur, progress, card):
    """Build the brief rendered above an art-only project strip by Neovim."""
    lesson = _paths(cfg)["sessions"] / card["project_id"] / (card["id"] + ".txt")
    context = _lesson_context(cur, card)
    compact_brief = (__import__("sys").stdout.isatty()
                     and shutil.get_terminal_size((80, 24)).lines < 38)
    show_target = card.get("show_target", True)
    show_recipe = card.get("show_recipe", card.get("show_target", False))
    recipe = " → ".join(keys for keys, _why in card.get("recipe", []))
    hint = card.get("hint") or "; then ".join(
        why for _keys, why in card.get("recipe", []))
    if "choose the smallest normal-mode operation" in hint:
        # VD-13: a generic hint teaches nothing; point at the per-key teaching.
        hint = "use the commands explained under HOW THE KEYS YOU NEED WORK"
    legacy_keys, legacy_sources, legacy_concepts = _legacy_teaching(card)
    key_vocabulary = list(card.get("key_vocabulary", []))
    for line in legacy_keys:
        if line not in key_vocabulary:
            key_vocabulary.append(line)
    if compact_brief:
        header = [
            "NEOVIM × ASCII ANIMATION · %s" % card["id"],
            # VD-13: own line, so XP/today survive the 68-cell clip.
            _clip(_progress_line(cfg, progress, card), 68),
            "DO THIS · " + _clip(card["prompt"], 54),
        ]
        if not show_recipe:
            boundary = "keys hidden · compare after pass" if card.get(
                "method_alternatives") else "exact command keys hidden"
            header.append("HINT · %s · %s" % (boundary, _clip(hint, 30)))
        else:
            header.append("HINT · " + _clip(hint, 59))
        if show_target:
            header.append("TARGET")
            header.extend(_compact_target_lines(card))
        if show_recipe:
            header.append("RECIPE  " + recipe)
        else:
            header.append("EVIDENCE  exact command keys remain hidden")
        header.extend(_key_teaching(card, width=66, cur=cur))
        if card.get("method_alternatives"):
            header.append("USE ONE METHOD  either one passes; both are compared after you pass")
        header.extend([
            "WHY THIS EXISTS",
            "Motion intent: " + _clip(context["module"]["meaning"], 57),
            "Authoring principle: " + _clip(context["module"]["principle"], 51),
            "Failure to watch: " + _clip(context["module"]["defect"], 55),
            "WHAT THIS LESSON BUYS YOU  " + _clip(context["buys"], 42),
        ])
        header.append("KEYS WORTH KEEPING")
        if key_vocabulary:
            header.extend("  " + _clip(line, 64) for line in key_vocabulary)
        elif show_recipe:
            header.append("  " + _clip(recipe, 64))
        else:
            header.append("  F1 help · u undo · <C-r> redo · :wq submit")
        header.append("WHERE THIS METHOD COMES FROM  " + _clip(context["source"], 39))
        header.extend("LEGACY SOURCE  " + _clip(source, 50) for source in legacy_sources)
        for title, paradigm in legacy_concepts:
            header.append("LEGACY VIM CONCEPT  " + _clip(title, 46))
            header.extend("  " + _clip(line, 64) for line in paradigm.splitlines() if line.strip())
        header.extend([
            "BASIC HELP  o new line below · O above · Space waits for WhichKey · clean mode F1",
            "COPY / PASTE  drag selects · Cmd-C copies · y copies a whole question · Cmd-V pastes",
            "READING THE RECIPE  <C-k>.M middle-dot digraph · <Esc> Escape",
            "SUBMIT / STUCK  :wq submits · :q! exits without submission",
        ])
        _write_lines_atomic(lesson, header)
        return lesson
    header = [
        "NEOVIM × ASCII ANIMATION  ·  %s" % card["id"],
        card["title"],
        _progress_line(cfg, progress, card),
        "SKILL  %s" % card["skill"],
    ]
    if not show_recipe:
        evidence = "exact command keys remain hidden; target and action hint remain visible"
        if card.get("method_alternatives"):
            evidence += "; comparison appears after verification"
        header.append("EVIDENCE  " + evidence)
    header.extend(["DO THIS", "  %s" % card["prompt"]])
    if show_target:
        header.append("TARGET")
        header.extend("  │" + line for line in card["target"])
    if show_recipe:
        header.append("COMMAND RECIPE")
        header.extend("  %-14s %s" % (keys, why) for keys, why in card["recipe"])
    else:
        header.extend(["HINT", "  " + hint, "  Exact keystrokes stay hidden until evaluation."])
    header.extend(_key_teaching(card, cur=cur))
    if not show_recipe and card.get("method_alternatives"):
        header.extend([
            "CHALLENGE",
            "  Make the outcome with one method; comparison appears after verification.",
        ])
    elif not show_recipe:
        header.append("INDEPENDENT ATTEMPT")
    header.append("WHY THIS EXISTS")
    header.extend("  " + line for line in context["why"])
    header.extend([
        "",
        "WHAT THIS LESSON BUYS YOU",
        "  " + context["buys"],
        "",
        "KEYS WORTH KEEPING",
    ])
    if key_vocabulary:
        header.extend("  " + line for line in key_vocabulary)
    elif show_recipe and card.get("recipe"):
        header.extend("  %-14s %s" % (keys, why) for keys, why in card["recipe"])
    else:
        header.extend([
            "  F1 cheat sheet  <C-w>w switch task/art  u undo  <C-r> redo.",
            "  :wq submit  :q! exit without submission.",
        ])
    header.extend([
        "",
        "WHERE THIS METHOD COMES FROM",
        "  " + context["source"],
    ])
    if legacy_sources:
        header.extend(["", "LEGACY LESSON SOURCES"])
        header.extend("  " + source for source in legacy_sources)
    for title, paradigm in legacy_concepts:
        header.extend(["", "LEGACY VIM CONCEPT", "  " + title])
        header.extend("  " + line for line in paradigm.splitlines())
    header.extend([
        "",
        "READING THE RECIPE",
        "  <CR> Enter  <Esc> Escape  <BS> Backspace  <C-v> Ctrl-v  <C-k>.M middle-dot digraph",
        "",
        "SUBMIT / STUCK",
        "  :wq submits. :q! exits without submission. Retry restores this card's checkpoint.",
        "  The task brief is read-only. <C-w>w switches between the brief and art.",
        "  o opens a new line below; O opens one above.",
        "  Drag to select popup text, then Cmd-C; press y to copy a whole question; Cmd-V pastes.",
        "  Personal config keeps Hardtime and WhichKey (press Space and wait); clean mode uses F1.",
    ])
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
    manifest_path = path.parent / ("transfer-manifest.json"
                                   if card.get("artifact") == "transfer"
                                   else "manifest.json")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        manifest = {"schema": "vim-daily/project@1", "project_id": card["project_id"],
                    "module_id": card["module_id"], "history": [], "source_refs": []}
    entry = {"card_id": card["id"], "at": _now().isoformat(),
             "sha256": _hash_file(path), "rows": len(_read_lines(path))}
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


def _without_brief_navigation(typed):
    """Remove keystrokes used only to inspect the tutor's read-only split."""
    out, index = [], 0
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
        index += 1
    return out


def _attempt_replay(cfg, card, keylog, before, got):
    """Return the visible actual-vs-taught key table for one edit attempt."""
    try:
        typed = _without_brief_navigation(cfg.decode_keylog(Path(keylog).read_bytes()))
    except OSError:
        typed = []
    expected = cfg.tokenize(card.get("expected", "")) if cfg.tokenize else []
    if cfg.keystroke_table:
        table = cfg.keystroke_table(typed, expected, width=24)
    else:
        table = ["  actual: %s" % ("".join(typed) or "(none)"),
                 "  taught: %s" % (card.get("expected") or "(none)")]
    return {"type": "edit", "table": table, "actual_tokens": typed,
            "actual_keys": "".join(typed) or "(none)",
            "taught_keys": "".join(expected) or "(none)",
            "before": before, "got": got,
            "target": [line.rstrip() for line in card["target"]]}


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
    return {"keylog": str(path), "keylog_sha256": _hash_file(path)}


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
        match = re.match(r"^([A-Za-z]+)!?(?:\s+.*)?$", segment)
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


def _contains_ordered(tokens, sequences):
    """Return true when token sequences occur in order with other keys between."""
    cursor = 0
    for wanted in sequences:
        found = None
        for index in range(cursor, len(tokens) - len(wanted) + 1):
            if tokens[index:index + len(wanted)] == wanted:
                found = index + len(wanted)
                break
        if found is None:
            return False
        cursor = found
    return True


def _linewise_yank_put_matches(tokens, rows):
    """Recognize a whole-frame linewise yank followed later by p/P."""
    count = list(str(rows))
    yanks = [count + ["y", "y"]]
    if rows > 1:
        offset = list(str(rows - 1)) if rows > 2 else []
        yanks.extend([
            ["V"] + offset + ["j", "y"],
            ["y"] + offset + ["j"],
        ])
    return any(_contains_ordered(tokens, [yank, [put]])
               for yank in yanks for put in ("p", "P"))


def _normalise_ex(command):
    return re.sub(r"\s+", "", command).lower()


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
        return any(_normalise_ex(command) in accepted
                   for _first, _last, command in executed_commands)
    return False


def _method_family(cfg, card, replay):
    """Name a demonstrated comparison method inside an otherwise valid attempt."""
    raw = replay.get("actual_tokens", [])
    actual = _edit_tokens_without_submit(raw)
    if not actual:
        return None
    executed_commands = [row for row in _executed_ex_commands(raw)
                         if not _is_submit_ex(row[2])]
    for method in card.get("method_alternatives", []):
        expected = cfg.tokenize(method["keys"]) if cfg.tokenize else list(method["keys"])
        expected = _edit_tokens_without_submit(expected)
        if (_contains_tokens(actual, expected)
                or _method_evidence_matches(method, actual, executed_commands)):
            return method["label"]
    return None


def _contains_tokens(tokens, wanted):
    """Return true when wanted occurs contiguously in tokens."""
    if not wanted or len(wanted) > len(tokens):
        return False
    return any(tokens[index:index + len(wanted)] == wanted
               for index in range(len(tokens) - len(wanted) + 1))


def _contains_ordered_tokens(tokens, wanted):
    """True when every required token occurs in order, allowing other input.

    The final buffer remains an exact equality gate.  This trace gate proves
    that the taught commands were present without treating look-around keys,
    undo/correction, Hardtime-blocked presses, or mapping-prefix replay from
    the operator's real config as a failed lesson.
    """
    if not wanted:
        return False
    cursor = 0
    for token in tokens:
        if token == wanted[cursor]:
            cursor += 1
            if cursor == len(wanted):
                return True
    return False


def _required_method_error(cfg, card, replay):
    """Grade declared method evidence separately from the final buffer."""
    rule = card.get("method_requirement")
    if not rule:
        return None
    actual = _edit_tokens_without_submit(replay.get("actual_tokens", []))
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
    if exact_paths and not any(_contains_ordered_tokens(actual, path)
                               for path in exact_paths):
        return ("The target matches, but the required command path was not demonstrated: %s."
                % rule["label"])
    if alternatives and not any(_contains_tokens(actual, wanted) for wanted in alternatives):
        return ("The target matches, but the required method was not demonstrated: %s."
                % rule["label"])
    if required and not all(_contains_tokens(actual, wanted) for wanted in required):
        return ("The target matches, but the required method was not demonstrated: %s."
                % rule["label"])
    maximum = rule.get("max_tokens")
    if maximum is not None and len(actual) > maximum:
        return ("The target matches, but this constrained transfer used %d keys; "
                "the limit for '%s' is %d." % (len(actual), rule["label"], maximum))
    return None


def _unrecognized_method_message(replay):
    actual = replay.get("actual_tokens", [])
    if not actual:
        return ("The target matches, but no edit keystrokes were captured; "
                "comparison credit requires a demonstrated method.")
    shown = replay.get("actual_keys") or "".join(actual)
    return ("The target matches and edit keys were captured, but neither taught "
            "method was recognized in this attempt. Captured keys: %s" % shown)


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
        mark = mark_glyph if i in differing else " "
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
            lines.append("  ✗ = row differs · first difference at column %d of row %d" % (
                column + 1, row + 1))
        else:
            lines.append("  ✗ = row differs · row %d is %s" % (
                row + 1, "extra in yours" if row >= len(target) else "missing from yours"))
    return lines


def _print_check_replay(replay, bold, off, *, compact=False):
    outcomes = replay.get("outcomes", [])
    if not outcomes:
        return
    print("\n%sMODULE CHECK REPLAY%s  %d/%d correct; threshold %d" % (
        bold, off, replay.get("score", 0), len(outcomes), replay.get("threshold", len(outcomes))))
    for index, outcome in enumerate(outcomes, 1):
        q = outcome["question"]
        chosen = outcome["chosen"]
        correct = q["correct_choice"]
        mark = "✓" if chosen == correct else "✗"
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
    return textwrap.shorten(" ".join(str(value).split()), width=width, placeholder="…")


# Reserve the prompt, popup borders, and the outer tmux status row.
_FEEDBACK_TRAILER_LINES = 5


def _post_feedback_ultra(card, replay, completed, context, concept_replay,
                         check_replay, bold, off, replay_rows=None, minimal=False,
                         ledger_rows=None, breakdown_packed=False):
    """Fit essential result evidence in an 80x24 popup without scrolling it away."""
    if replay and replay.get("type") == "edit":
        print("%sARTIFACT REPLAY%s  %s" % (
            bold, off, "exact target" if completed else "mismatch: yours vs target"))
        for line in _artifact_replay(replay, completed, max_rows=replay_rows,
                                     minimal=minimal):
            print(line)
        print("%sKEYSTROKE LEDGER%s  YOU TYPED │ THE RECIPE ASKS FOR" % (bold, off))
        table = replay.get("table", [])
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
            print("METHOD EVIDENCE  %s" % _clip(
                replay["method_evidence_error"], 68))
        elif replay.get("method_family"):
            print("METHOD EVIDENCE  demonstrated: %s" % replay["method_family"])
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
            print("%sEDIT REPLAY%s  %s" % (
                bold, off, "exact target" if completed else "mismatch: yours vs target"))
            for line in _artifact_replay(edit, completed, max_rows=replay_rows,
                                         minimal=minimal):
                print(line)
            print("keys: actual %s · taught %s" % (
                _clip(edit.get("actual_keys", "(none)"), 20),
                _clip(edit.get("taught_keys", "(none)"), 20)))
    if check_replay:
        outcomes = check_replay.get("outcomes", [])
        print("%sMODULE CHECK REPLAY%s  %d/%d; threshold %d" % (
            bold, off, check_replay.get("score", 0), len(outcomes),
            check_replay.get("threshold", len(outcomes))))
        wrong = [(index, outcome) for index, outcome in enumerate(outcomes, 1)
                 if outcome["chosen"] != outcome["question"]["correct_choice"]]
        if outcomes and not wrong:
            print("✓ all %d choices correct; detailed explanations remain in the attempt record" %
                  len(outcomes))
        for index, outcome in wrong[:2]:
            q, chosen = outcome["question"], outcome["chosen"]
            correct = q["correct_choice"]
            print("✗%d chose: %s → %s" % (
                index, _clip(q["choices"][chosen], 38), _clip(q["choices"][correct], 22)))
    if replay and replay.get("playback_verified"):
        print("%sPLAYBACK VERIFIED%s  automatic equal-height strip preview completed" % (
            bold, off))
    if not concept_replay:
        path = " → ".join(keys for keys, _why in card.get("recipe", [])
                          if keys != card.get("cursor"))
        print("%sDO / AVOID%s  %s · required commands in order · exact saved target" % (
            bold, off, path or card.get("expected", "(none)")))
        width = max(40, shutil.get_terminal_size((80, 24)).columns - 4)
        breakdown = _answer_breakdown(card, width=width)
        if breakdown and (breakdown_packed or minimal):
            # Tight popup: one wrapped paragraph instead of one row per command.
            items = " · ".join(line.strip() for line in breakdown[1:])
            wrapped = textwrap.wrap("%s  %s" % (breakdown[0], items), width=width) or [""]
            for line in wrapped[:3]:
                print(line)
        elif breakdown:
            print("%s%s%s" % (bold, breakdown[0], off))
            for line in breakdown[1:]:
                print(line)
        else:
            for method in card.get("method_alternatives", []):
                print("ALSO %s: %s" % (method["label"], method["keys"]))
    print("%sSOURCE%s  %s" % (bold, off, context["source"]))


def _print_feedback_do_this(card, replay, completed, concept_replay, compact, bold, off):
    """Every result page states the learner's next action (VD-11)."""
    if completed:
        action = "press Enter for skill-tree progress."
    elif concept_replay:
        action = "read why the correct answer is right, then press Enter."
    else:
        action = ("compare YOURS with TARGET (✗ = row differs), press Enter, "
                  "then redo: " + card.get("prompt", ""))
    if compact:
        width = max(40, shutil.get_terminal_size((80, 24)).columns - 4)
        wrapped = textwrap.wrap(action, width=width - 9) or [""]
        print("%sDO THIS%s  %s" % (bold, off, wrapped[0]))
        for extra in wrapped[1:3]:
            print("         " + extra)
        return min(3, len(wrapped))
    print("%sDO THIS%s  %s" % (bold, off, action))
    return 1


def _post_feedback(cfg, cur, card, replay=None, *, completed=True):
    """Render held page one: artifact evidence and authored correction."""
    bold, dim, off, green, _red, _yellow = cfg.colours
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
        print("%sLESSON COMPLETE%s  ·  %s  ·  %s" % (green + bold, off, card["id"], card["title"]))
        if concept_replay:
            print("verified outcome: the conceptual choice is correct")
        elif not (compact and check_replay):
            print("verified outcome: the saved project matches the target exactly")
    else:
        print("%sATTEMPT NOT PASSED%s  ·  %s  ·  %s" % (bold, off, card["id"], card["title"]))
        if concept_replay:
            print("no progress awarded: the conceptual choice was incorrect")
        elif check_replay:
            if not compact:
                print("no progress awarded: the module-check concept threshold was not met")
        elif replay and replay.get("target_matches"):
            print("no progress awarded: the saved project matches the exact target, "
                  "but the required method was not demonstrated")
        else:
            print("no progress awarded: the saved project did not match the exact target")

    do_lines = _print_feedback_do_this(card, replay, completed, concept_replay,
                                       compact, bold, off)
    if compact:
        # VD-11: measure the rendered page and shrink only the artifact replay
        # until title, status, DO THIS, replay, and the Enter prompt all fit.
        import contextlib
        import io
        status_lines = 2
        available = (shutil.get_terminal_size((80, 24)).lines
                     - status_lines - do_lines - _FEEDBACK_TRAILER_LINES)
        ledger_total = max(1, len((replay or {}).get("table", [])) - 2)

        packed = False

        def render(rows, minimal=False, ledger=None):
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                _post_feedback_ultra(card, replay, completed, context, concept_replay,
                                     check_replay, bold, off, replay_rows=rows,
                                     minimal=minimal, ledger_rows=ledger,
                                     breakdown_packed=packed)
            return buffer.getvalue()

        rows = max(1, available)
        ledger = ledger_total
        text = render(rows, ledger=ledger)
        # Shrink the ledger to three rows first, then pack the key-by-key
        # answer into a paragraph (VD-13), then the artifact replay, then the
        # ledger to one row, so both two-column comparisons stay visible.
        while text.count("\n") > available and ledger > 3:
            ledger -= 1
            text = render(rows, ledger=ledger)
        if text.count("\n") > available:
            packed = True
            text = render(rows, ledger=ledger)
        while text.count("\n") > available and rows > 1:
            rows -= 1
            text = render(rows, ledger=ledger)
        while text.count("\n") > available and ledger > 1:
            ledger -= 1
            text = render(rows, ledger=ledger)
        if text.count("\n") > available:
            # Tight page (e.g. module check at 80x24): keep both columns but
            # show only the first changed row, without elision/legend lines.
            text = render(1, minimal=True, ledger=1)
        print(text, end="")
        return

    if replay and replay.get("type") == "edit":
        print("\n%sARTIFACT REPLAY%s  saved buffer before and after evaluation" % (bold, off))
        for line in _artifact_replay(replay, completed):
            print(line)
        print("\n%sKEYSTROKE REPLAY%s  actual input vs taught path" % (bold, off))
        if compact:
            print("  actual: %s" % replay.get("actual_keys", "(unavailable)"))
            print("  taught: %s  ·  alternate keys pass when the exact target matches" %
                  replay.get("taught_keys", card.get("expected", "(none)")))
        else:
            print("%sThe save/quit command is ignored. A different path may still be valid when the target matches.%s"
                  % (dim, off))
            for line in replay.get("table", []):
                print(line)
        if replay.get("method_evidence_error"):
            print("  METHOD EVIDENCE: %s" % replay["method_evidence_error"])
        elif replay.get("method_family"):
            print("  METHOD EVIDENCE: demonstrated %s" % replay["method_family"])
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
            print("\n%sCHANGED-ART EDIT REPLAY%s" % (bold, off))
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
        footer = "LESSON COMPLETE" if completed else "ATTEMPT NOT PASSED"
    print("\n%s%s%s  ·  %s  ·  result summary above" % (
        green + bold if completed else bold, footer, off, card["id"]))


def progress_full_rows(cur):
    """Terminal rows the full progress page needs; smaller popups use the compact tree.

    VD-11: a fixed 28-row threshold let the 14-module tree scroll the page's
    PROGRESS header off a 100x36 popup.
    """
    return len(cur["modules"]) + 24


def _post_progress(cfg, cur, card, progress, *, completed=True):
    """Render held page two: progression only, without feedback scrolling away."""
    bold, _dim, off, green, _red, _yellow = cfg.colours
    _clear_if_tty()
    if getattr(cfg, "practice", False):
        label = "PRACTICE COMPLETE · PROGRESS UNCHANGED"
    else:
        label = "PROGRESS AWARDED" if completed else "PROGRESS UNCHANGED"
    colour = green + bold if completed else bold
    ultra = (__import__("sys").stdout.isatty()
             and shutil.get_terminal_size((80, 24)).lines < progress_full_rows(cur))
    print("%s%s%s  ·  %s  ·  %s" % (colour, label, off, card["id"], card["title"]))
    print("\n%sSKILL TREE / MODULE PROGRESS%s%s" % (
        bold, off, " · A craft / V editor" if ultra else ""))
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
        print("CURRENT MODULE MAP  %s %s" % (module["id"], cells))
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
    _post_feedback(cfg, cur, card, replay, completed=completed)
    if cfg.feedback_rendered:
        cfg.feedback_rendered()
    if cfg.post_page_break:
        cfg.post_page_break()
    _post_progress(cfg, cur, card, progress, completed=completed)


def _complete(cfg, cur, card, *, question_id=None, extra=None, replay=None):
    before_progress = project(cur, read_events(cfg))
    event = {"type": "card", "result": "pass", "card_id": card["id"],
             "module_id": card["module_id"], "curriculum_revision": cur["revision"],
             "question_id": question_id}
    if _review_variants(card):
        event["next_due"] = _next_due(cur, 0)
    if extra:
        event.update(extra)
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
    progress["new_unlocks"] = [
        module["id"] for module in cur["modules"]
        if before_progress["modules"][module["id"]]["state"] == "locked"
        and progress["modules"][module["id"]]["state"] != "locked"
    ]
    cell = progress["modules"][card["module_id"]]
    print("\n✓ %s complete — %s %d/%d (%s)" % (
        card["id"], card["module_id"], cell["done"], cell["total"], cell["state"]))
    nxt = next_card(cur, progress)
    if nxt:
        print("next: %s  %s" % (nxt["id"], nxt["title"]))
    else:
        print("all %d modules mastered" % len(cur["modules"]))
    _post_lesson(cfg, cur, card, progress, replay)
    if cfg.post_rendered:
        cfg.post_rendered()
    cfg.hold_open()
    return 0


def run_concept(cfg, cur, progress, card):
    print("\n%s — %s" % (card["id"], card["title"]))
    context = _lesson_context(cur, card)
    q = _question_for_card(cur, progress, card)
    ultra = (__import__("sys").stdout.isatty()
             and shutil.get_terminal_size((80, 24)).lines < 28)
    print(_clip(_progress_line(cfg, progress, card), 70) if ultra
          else _progress_line(cfg, progress, card))
    if not ultra:
        print("WHY: %s" % context["why"][1])
        print("BUYS: %s" % context["buys"])
        print("SOURCE: %s" % context["source"])
    teaching = card.get("teaching_lines", [])
    if teaching:
        print("TEACH FIRST")
        for line in teaching:
            print("  %s" % line)
    if ultra:
        print("DO THIS %s: choose the answer whose ANIMATION and NEOVIM halves are both correct."
              % card["id"])
    else:
        print("DO THIS: %s" % card["prompt"])
    if not ultra:
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
        print("check concepts already passed; resuming the artifact subpart")
        return True, _latest_check_replay(cfg, cur, card)
    qmap = _question_map(cur)
    context = _lesson_context(cur, card)
    print("\n" + _progress_line(cfg, progress, card))
    print("MODULE CHECK WHY: %s" % context["why"][1])
    print("MODULE CHECK BUYS: %s" % context["buys"])
    print("DO THIS: answer five checks, then complete the unhinted artifact edit.")
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


def run_edit(cfg, cur, progress, card):
    check_replay = None
    path = _artifact_path(cfg, card)
    variants = card.get("variants", [])
    if variants:
        chosen = None
        existing = _read_lines(path) if path.exists() else None
        if existing is not None:
            chosen = next((variant for variant in variants
                           if existing == [line.rstrip() for line in variant["target"]]), None)
        if chosen is None:
            chosen = variants[progress["attempts"].get(card["id"], 0) % len(variants)]
        card = dict(card)
        card.update(chosen)
        card["variant_index"] = variants.index(chosen)
        if existing is not None and existing != [line.rstrip() for line in card["start"]]:
            known_starts = [[line.rstrip() for line in variant["start"]] for variant in variants]
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
    current = _read_lines(path)
    legacy_starts = [
        [line.rstrip() for line in legacy]
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
        current = _read_lines(path)
        print("Upgraded the verified project checkpoint to the revised multi-row lesson art; "
              "the prior text remains in checkpoints/.")
    target_lines = [x.rstrip() for x in card["target"]]
    if current == target_lines:
        recovery_extra = {"artifact": str(path), "artifact_sha256": _hash_file(path),
                          "recovered": True}
        recovery_replay = check_replay
        if card.get("method_alternatives") or card.get("method_requirement"):
            recovered_keylog = _latest_attempt_keylog(
                path.parent, "keys-%s" % card["id"])
            keylog = str(recovered_keylog or path.parent / ("keys-%s.log" % card["id"]))
            recovery_extra.update(_keylog_fields(keylog))
            before_path = path.parent / "checkpoints" / (card["id"] + "-before.txt")
            before = _read_lines(before_path) if before_path.exists() else card["start"]
            recovery_replay = _attempt_replay(cfg, card, keylog, before, current)
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
        return _complete(cfg, cur, card, extra=recovery_extra, replay=recovery_replay)
    if current != [x.rstrip() for x in card["start"]]:
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
        print("hint: %s" % (card.get("hint") or "; then ".join(
            why for _keys, why in card.get("recipe", []))))
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
        cfg.run_editor(str(path), 1, card.get("cursor", "^"), keylog, str(lesson),
                       card["prompt"], card.get("hint"))
        got = _read_lines(path)
        replay = _attempt_replay(cfg, card, keylog, current, got)
        if check_replay:
            replay["check_replay"] = check_replay
        exact_target = got == target_lines
        replay["target_matches"] = exact_target
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
            return _complete(cfg, cur, card, extra=extra,
                             replay=replay)
        failure_event = {"type": "card", "result": "fail", "card_id": card["id"],
                         "module_id": card["module_id"], "attempt": tries,
                         "artifact": str(path),
                         "reason": ("missing-method-evidence"
                                    if replay.get("method_evidence_error")
                                    else "target-mismatch")}
        failure_event.update(_keylog_fields(keylog_path))
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
        try:
            answer = input("Restore this card's checkpoint and retry? [Y/n] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            cfg.hold_open()
            return 0
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
    card.update(variants[variant_index])
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
    base = _paths(cfg)["projects"] / card["project_id"] / "reviews"
    path = base / ("review-%s.txt" % key.replace(".", "-"))
    if path.exists():
        _checkpoint(cfg, card, path, "previous")
    _write_lines_atomic(path, card["start"])
    before = [line.rstrip() for line in card["start"]]
    keylog = str(_next_attempt_keylog(base, "keys-%s" % key.replace(".", "-")))
    print("\nSPACED EDIT RETRIEVAL  ·  changed-art variant %d" % (
        card["variant_index"] + 1))
    print("DO THIS: %s" % card["prompt"])
    lesson = _write_session_lesson(cfg, cur, progress, card)
    cfg.run_editor(str(path), 1, card.get("cursor", "^"), keylog, str(lesson),
                   card["prompt"], card.get("hint"))
    got = _read_lines(path)
    replay = _attempt_replay(cfg, card, keylog, before, got)
    method_error = _required_method_error(cfg, card, replay)
    if method_error:
        replay["method_evidence_error"] = method_error
    passed = (got == [line.rstrip() for line in card["target"]]
              and method_error is None)
    if not passed:
        _checkpoint(cfg, card, path, "failed")
        _write_lines_atomic(path, card["start"])
    return passed, card, path, replay


def run_review(cfg, cur, progress, key, review):
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
        cells.append("%s%s" % (label, "✓" if card_id in passed else "○"))
    return "%s cards: %s" % (module_id, " ".join(cells))


def print_tree(cur, progress, cfg=None, *, compact=False):
    if compact:
        marks = {"locked": "·", "available": "○", "learning": "◐",
                 "check_ready": "◆", "review_pending": "↻", "mastered": "✓"}
        nodes = []
        for module in cur["modules"]:
            cell = progress["modules"][module["id"]]
            nodes.append("%s%s %d/%d" % (
                marks[cell["state"]], module["id"], cell["done"], cell["total"]))
        print("STATE  ○ available · locked ◐ learning ◆ check-ready ↻ review-pending ✓ mastered")
        for start in range(0, len(nodes), 5):
            print(("TREE  " if start == 0 else "      ") + " | ".join(nodes[start:start + 5]))
        due = sum(1 for r in progress["reviews"].values() if _due(r.get("next_due")))
        level, title, into, needed = _level(progress["xp"])
        print("XP %d · LEVEL %d %s %d/%d · reviews %d · badges %d" % (
            progress["xp"], level, title, into, needed, due, len(progress["badges"])))
        if progress.get("active_remediations"):
            print("REMEDIATION  " + " | ".join(
                "%s %s" % (row["id"], row["changed_variant"])
                for row in progress["active_remediations"].values()))
        if cfg:
            streak, best, total = _legacy_streak(cfg.state)
            bold, _dim, off, _green, _red, _yellow = cfg.colours
            flame = " 🔥" if streak >= 3 else ""
            print("%sstreak: %d day%s%s · best %d · all-time %d%s" % (
                bold, streak, "" if streak == 1 else "s", flame, best, total, off))
        nxt = next_card(cur, progress)
        print("next: %s" % (nxt["id"] if nxt else "course complete"))
        return
    print("Neovim × ASCII animation skill tree")
    print("tracks: A = ASCII craft level; V = Neovim editing level")
    for module in cur["modules"]:
        cell = progress["modules"][module["id"]]
        marks = {"locked": "·", "available": "○", "learning": "◐",
                 "check_ready": "◆", "review_pending": "↻", "mastered": "✓"}
        requires = ",".join(module.get("prerequisites", [])) or "start"
        print("%s %-3s %-26s %d/%d  %-14s [%s] requires %s" % (
            marks[cell["state"]], module["id"], module["title"], cell["done"], cell["total"],
            cell["state"], module["node"], requires))
    due = sum(1 for r in progress["reviews"].values() if _due(r.get("next_due")))
    print("reviews due: %d   ledger errors: %d" % (due, progress["ledger_errors"]))
    level, title, into, needed = _level(progress["xp"])
    print("XP: %d   LEVEL %d %s: %d/%d toward next level" % (
        progress["xp"], level, title, into, needed))
    print("badges: %s" % (", ".join(progress["badges"]) or "none yet"))
    if progress.get("active_remediations"):
        print("active remediation:")
        for row in progress["active_remediations"].values():
            print("  %s  %s  next: %s" % (
                row["id"], row["name"], row["changed_variant"]))
    if cfg:
        streak, best, total = _legacy_streak(cfg.state)
        bold, _dim, off, _green, _red, _yellow = cfg.colours
        flame = " 🔥" if streak >= 3 else ""
        print("%sstreak: %d day%s%s   best: %d   all-time completions: %d%s" % (
            bold, streak, "" if streak == 1 else "s", flame, best, total, off))
    nxt = next_card(cur, progress)
    print("next: %s" % ((nxt["id"] + " " + nxt["title"]) if nxt else "course complete"))


def export_progress(cur, progress):
    payload = dict(progress)
    payload["next_card"] = (next_card(cur, progress) or {}).get("id")
    payload["due_reviews"] = sum(1 for r in progress["reviews"].values() if _due(r.get("next_due")))
    json.dump(payload, __import__("sys").stdout, indent=1, ensure_ascii=False)
    print()


def preview_project(cfg, cur, module_id, speed=0.35):
    module = next((m for m in cur["modules"] if m["id"] == module_id), None)
    if not module:
        print("no such module: %s" % module_id)
        return 1
    base = _paths(cfg)["projects"] / module["project_id"]
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
    lines = _read_lines(path)
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
    global LAST_RUN_CARD_ID, LAST_RUN_KIND
    LAST_RUN_CARD_ID = None
    LAST_RUN_KIND = None
    cur = load_curriculum(cfg.share)
    events = read_events(cfg)
    progress = project(cur, events)
    save_projection(cfg, progress)
    mode = argv[0] if argv else "run"
    continuation = mode == "--continue"
    cfg.practice = mode in ("--practice-card", "--practice-review")
    if mode in ("--tree", "--status"):
        print_tree(cur, progress, cfg)
        return 0
    if mode == "--export-progress":
        export_progress(cur, progress)
        return 0
    if mode == "--list":
        passed = set(progress["passed_cards"])
        for card in cur["cards"]:
            print("%s  %-16s %-22s %s" % ("✓" if card["id"] in passed else "·", card["id"], card["kind"], card["title"]))
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
            state = progress["modules"][card["module_id"]]["state"]
            if state == "locked":
                print("%s is locked by its module prerequisites" % wanted)
                return 1
            if wanted in set(progress["passed_cards"]):
                print("%s is already complete; use the result-page repeat control for uncredited practice" % wanted)
                return 1
            module = _module_for_card(cur, card)
            module_next = next((cid for cid in module["card_ids"]
                                if cid not in set(progress["passed_cards"])), None)
            if wanted != module_next:
                print("%s is not the current card for %s; complete %s first" % (
                    wanted, module["id"], module_next or "the module"))
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

    explicit_force = force or mode in ("--force", "--card", "--practice-card", "--practice-review")
    if not explicit_force:
        if (not continuation and
                (os.environ.get("VIM_DAILY_SKIP") or os.environ.get("VIM_DAILY_ACTIVE")
                 or os.environ.get("NVIM"))):
            return 1 if mode == "--due-quiet" else 0
        today = _now().date().isoformat()
        done = sum(1 for e in events if e.get("type") in ("card", "review") and e.get("result") == "pass" and str(e.get("at", "")).startswith(today))
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
    lock = SessionLock(_paths(cfg)["lock"])
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
        review_due_now = (False if cfg.practice else
                          should_run_review(events, review, candidate, explicit_force))
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
        lock.__exit__(None, None, None)
