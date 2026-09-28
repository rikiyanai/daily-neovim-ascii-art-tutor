#!/usr/bin/env python3
"""Focused structural validator for the standalone animation lesson pack.

This test intentionally does not import the curriculum generator or runtime.
The pack is an authoring source, and this validator checks the contracts that
must survive a future integration: original-art boundary, hidden/guided
separation, question clarity/placement evidence, changed-art review, and
finish-line coverage.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACK = ROOT / "animation_lesson_pack.md"
AUDIT = ROOT / "audits" / "ANIMATION_CORPUS_RIGHTS_AUDIT.md"
LESSON_IDS = [f"AL{i:02d}" for i in range(1, 13)]
HABITS = [f"H{i}" for i in range(1, 10)]
STAGES = [*(f"S{i}" for i in range(8)), *(f"A{i}" for i in range(8))]
REQUIRED_TERMS = {
    "keyframe": "keyframes",
    "extreme": "extremes",
    "breakdown": "breakdowns",
    "in-between": "in-betweens",
    "hold": "holds",
    "arc": "arcs",
    "overshoot": "overshoot",
    "settle": "settle",
    "drag": "drag",
    "follow-through": "follow-through",
    "loop seam": "loop seams",
    "onion-skin": "onion-skin comparison",
    "frame/layer": "frame/layer objects",
    "fixed-width": "fixed-width registration",
}


def sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"^## (AL\d{2}) — .*?$", text, re.MULTILINE))
    result: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result[match.group(1)] = text[match.start() : end]
    return result


def question_blocks(section: str) -> list[str]:
    matches = list(re.finditer(r"^#### (AL\d{2}-Q\d+) — .*?$", section, re.MULTILINE))
    blocks = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else section.find("### Changed-art review")
        blocks.append(section[match.start() : end])
    return blocks


def check() -> list[str]:
    errors: list[str] = []
    if not PACK.exists():
        return [f"missing pack: {PACK}"]
    if not AUDIT.exists():
        errors.append(f"missing audit: {AUDIT}")
    text = PACK.read_text(encoding="utf-8")
    lower = text.lower()
    by_lesson = sections(text)

    if list(by_lesson) != LESSON_IDS:
        errors.append(f"lesson ids/order mismatch: {list(by_lesson)}")
    if "standalone" not in lower or "not wired" not in lower:
        errors.append("pack does not declare standalone/non-integrated status")
    if "no source frame" not in lower or "integration: blocked" not in lower:
        errors.append("pack does not declare source-art exclusion and blocked integration")
    if not re.search(r"4\+4\+2", text):
        errors.append("missing 4+4+2 capstone timing")

    for needle, description in REQUIRED_TERMS.items():
        if needle not in lower:
            errors.append(f"missing required animation term ({description}): {needle}")

    # Coverage is checked from lesson-owned map lines, not merely the preamble.
    for code in HABITS + STAGES:
        if not any(re.search(rf"\b{re.escape(code)}\b", section) for section in by_lesson.values()):
            errors.append(f"{code} has no lesson-owned mapping")

    all_questions: list[str] = []
    for lesson_id in LESSON_IDS:
        section = by_lesson.get(lesson_id, "")
        for heading in (
            "### Original exercise",
            "### Guided sequence",
            "### Hidden sequence",
            "### Questions",
            "### Changed-art review",
            "### Question audit",
            "### Rights gate",
        ):
            if heading not in section:
                errors.append(f"{lesson_id} missing section: {heading}")
        if "**Map:**" not in section:
            errors.append(f"{lesson_id} missing explicit map")
        if "key-hidden: yes" not in section:
            errors.append(f"{lesson_id} has no key-hidden sequence")
        if "keys: withheld" not in section:
            errors.append(f"{lesson_id} hidden sequence does not withhold keys")
        if "key-hidden: no" not in section:
            errors.append(f"{lesson_id} has no guided sequence")
        if "integration: blocked" not in section:
            errors.append(f"{lesson_id} missing blocked rights gate")
        if "original exercise: yes" not in section:
            errors.append(f"{lesson_id} does not assert original exercise")
        changed = section.split("### Changed-art review", 1)[-1].split("### Question audit", 1)[0]
        if "Variants:" not in changed:
            errors.append(f"{lesson_id} changed-art review has no variants")

        questions = question_blocks(section)
        if len(questions) < 2:
            errors.append(f"{lesson_id} has fewer than two questions")
        all_questions.extend(questions)
        audit = section.split("### Question audit", 1)[-1].split("### Rights gate", 1)[0]
        for audit_line in (
            "student-can-answer-from-prior-teaching: yes",
            "request-is-clear: yes",
            "placement-makes-sense: yes",
        ):
            if audit_line not in audit:
                errors.append(f"{lesson_id} missing question audit: {audit_line}")

    if len(all_questions) != 24:
        errors.append(f"expected 24 question blocks, found {len(all_questions)}")
    question_ids = re.findall(r"^#### (AL\d{2}-Q\d+) —", text, re.MULTILINE)
    if len(question_ids) != len(set(question_ids)):
        errors.append("question ids are not unique")
    for block in all_questions:
        match = re.search(r"^#### (AL\d{2}-Q\d+) —", block, re.MULTILINE)
        question_id = match.group(1) if match else "unknown-question"
        ask_region = block.split("- Ask:", 1)[-1].split("- Expected answer:", 1)[0]
        if "?" not in ask_region:
            errors.append(f"{question_id} has no clear question ending in '?'")
        for field in (
            "- Placement:",
            "- Expected answer:",
            "- Answer format:",
            "- Prior teaching basis:",
            "- Clarity check:",
            "- Placement rationale:",
        ):
            if field not in block:
                errors.append(f"{question_id} missing {field}")
        clarity_region = block.lower().split("- clarity check:", 1)[-1]
        if "clear" not in clarity_region.splitlines()[0]:
            errors.append(f"{question_id} clarity check is not affirmative")

    # The audit must be tied to exact local evidence and must preserve the
    # distinction between sheet count and distinct full-pose count.
    if AUDIT.exists():
        audit_text = AUDIT.read_text(encoding="utf-8")
        for needle in (
            "86 sets, 885 sheets",
            "158 singleton/part-only",
            "distinct full poses",
            "Sapling & Ramparts",
            "01-sacrificial-pit-layers.txt",
            "ascii_tutorial.html",
            "logo, worm, dome, brick",
            "integration is **blocked**",
        ):
            if needle.lower() not in audit_text.lower():
                errors.append(f"audit missing evidence/boundary phrase: {needle}")
        inventory = audit_text.split("## Qualifying-set inventory", 1)[-1].split(
            "## Source-to-lesson boundary", 1
        )[0]
        rows = re.findall(r"^\| `official-[^|]+` \| (\d+) \| (\d+) \| `([^`]+)` \|$", inventory, re.MULTILINE)
        if len(rows) != 86:
            errors.append(f"audit inventory should have 86 qualifying rows, found {len(rows)}")
        if rows and sum(int(sheets) for sheets, _poses, _path in rows) != 885:
            errors.append("audit inventory sheet total is not 885")
        expected_top = {
            "official-Cosmetics/Mech": (52, 49),
            "official-Pets/Skully": (46, 37),
            "official-Pets/Panda": (28, 28),
            "official-Pets/Dragon": (29, 28),
            "official-Cosmetics/Knight": (34, 27),
            "official-Games/TowerDefense": (21, 21),
            "official-Games/BurgerRush": (18, 18),
            "official-UI/FaceHUD": (12, 11),
            "official-UI/Calculator": (15, 15),
        }
        actual_top = {path.rsplit("/official-", 1)[-1]: (int(sheets), int(poses)) for sheets, poses, path in rows}
        for rel, counts in expected_top.items():
            # The table stores absolute paths; normalize just the source root.
            full = f"/Users/r/Downloads/stone-story-consolidated/{rel}"
            found = next(((int(sheets), int(poses)) for sheets, poses, path in rows if path == full), None)
            if found != counts:
                errors.append(f"audit top-set count mismatch for {rel}: {found} != {counts}")

    return errors


if __name__ == "__main__":
    failures = check()
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)
    print(f"PASS: {PACK.name}: {len(LESSON_IDS)} lessons, 24 audited questions, H1-H9, S0-S7, A0-A7")
