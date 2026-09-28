#!/usr/bin/env python3
"""Focused checks for the live generated animation lesson-pack contract."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("v2_curriculum_generator", HERE / "gen_curriculum_v2.py")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


def check() -> list[str]:
    errors: list[str] = []
    generated = generator.build()
    installed = json.loads((HERE / "curriculum-v2.json").read_text(encoding="utf-8"))
    if generated != installed:
        errors.append("curriculum-v2.json is not generated from the current lesson pack")
    lessons = generated.get("animation_lesson_pack", [])
    if len(lessons) != 12:
        errors.append(f"expected 12 live animation lessons, found {len(lessons)}")
    if sum(len(lesson.get("questions", [])) for lesson in lessons) != 24:
        errors.append("live animation pack must retain 24 paired questions")
    cards = {card["id"]: card for card in generated["cards"]}
    habits = set()
    stages = set()
    blocked_names = ("stone story", "sacrificial pit", "worm", "dome", "brick", "logo")
    for lesson in lessons:
        habits.update(lesson.get("master_habits", []))
        stages.update(lesson.get("master_stages", []))
        if lesson.get("domains") != ["ascii_animation", "neovim"]:
            errors.append(f"{lesson['id']}: missing paired domains")
        if not all(lesson.get(field, "").startswith(prefix) for field, prefix in (
                ("do_this", "DO THIS —"), ("target", "TARGET —"), ("hint", "HINT —"))):
            errors.append(f"{lesson['id']}: missing explicit DO THIS/target/hint")
        if lesson.get("rights_gate", {}).get("integration") != "blocked":
            errors.append(f"{lesson['id']}: unresolved-source rights gate is not blocked")
        if lesson.get("changed_art_review", {}).get("variant_count", 0) < 2:
            errors.append(f"{lesson['id']}: changed-art review has fewer than two variants")
        if lesson.get("question_audit") != {
                "student_can_answer_from_prior_teaching": True,
                "request_is_clear": True,
                "placement_makes_sense": True}:
            errors.append(f"{lesson['id']}: question audit is not affirmative")
        delivery = lesson.get("delivery", {})
        guided, hidden = cards.get(delivery.get("guided_card_id")), cards.get(delivery.get("hidden_card_id"))
        if not guided or not hidden:
            errors.append(f"{lesson['id']}: delivery route is not attached to live cards")
        elif guided.get("grammar_stage") != "guided" or hidden.get("grammar_stage") != "hidden":
            errors.append(f"{lesson['id']}: delivery route violates guided-before-hidden gate")
        else:
            question_ids = {question["id"] for question in lesson.get("questions", [])}
            for card in (guided, hidden):
                if set(card.get("animation_pack_question_ids", [])) != question_ids:
                    errors.append(f"{lesson['id']}: paired questions are not attached to delivery cards")
        for question in lesson.get("questions", []):
            for field in ("animation_prompt", "animation_answer", "neovim_prompt",
                          "neovim_answer", "answer_format", "paired_answer_format",
                          "explicit_answer"):
                if not question.get(field):
                    errors.append(f"{question['id']}: missing explicit paired answer field {field}")
            if question.get("placement") not in ("before", "after"):
                errors.append(f"{question['id']}: missing placement gate")
        for frame in lesson.get("ascii_exercise", {}).get("frames", []):
            if any(name in "\n".join(frame).lower() for name in blocked_names):
                errors.append(f"{lesson['id']}: generated original art names blocked source material")
    if habits != {f"H{number}" for number in range(1, 10)}:
        errors.append("live animation pack does not cover H1-H9")
    if stages != {*(f"S{number}" for number in range(8)), *(f"A{number}" for number in range(8))}:
        errors.append("live animation pack does not cover S0-S7/A0-A7")
    return errors


if __name__ == "__main__":
    failures = check()
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)
    print("PASS: live animation lesson pack: 12 lessons, 24 paired questions, guided-before-hidden")
