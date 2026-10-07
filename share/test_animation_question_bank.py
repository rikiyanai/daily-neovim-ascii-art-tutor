"""Static quality gate for the manually authored whole-sequence question bank.

This test intentionally reads the source bank only.  The generator owns art
placeholder expansion; this gate protects the authored prose before that
expansion can hide recipe leakage or collapse all twenty subjects into one
template.
"""

from __future__ import annotations

import json
from pathlib import Path


BANK = Path(__file__).with_name("questions-authored-v2-animation-expansion.json")
EXPECTED_IDS = {f"M{index}.REWARD.P01" for index in range(20)}
ALLOWED_MARKERS = {"{{FULL_EVIDENCE}}", "{{COMPACT_EVIDENCE}}"}

FOCAL_TERMS = {
    "M0": ("fireworks", "radial", "core", "rays"),
    "M1": ("acronian", "wing", "joint", "axis"),
    "M2": ("face", "eye", "blink", "shell"),
    "M3": ("pose", "acting", "eye", "baseline"),
    "M4": ("rotation", "prop", "pivot", "midpoint"),
    "M5": ("blade", "texture", "background", "seam"),
    "M6": ("pyramid", "subtractive", "ground", "rows"),
    "M7": ("timed", "anticipation", "hold", "completion"),
    "M8": ("walk", "planted", "contact", "arm"),
    "M9": ("bounce", "squash", "rebound", "ground"),
    "M10": ("sjis", "proportional", "lobe", "utf-8"),
    "M11": ("missile", "roof", "trail", "hull"),
    "M12": ("joint", "punctuation", "axis", "stagger"),
    "M13": ("texture", "pulse", "cluster", "word"),
    "M14": ("palette", "face", "eye", "contour"),
    "M15": ("dither", "brick", "shadow", "material"),
    "M16": ("key-pose", "label", "timing", "breakdown"),
    "M17": ("eye", "shell", "homologous", "coherent"),
    "M18": ("mirrored", "rail", "turnaround", "directional"),
    "M19": ("bounce", "ground", "body", "squash"),
}


def test_animation_question_bank_is_manual_and_subject_specific():
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    assert set(bank) == EXPECTED_IDS
    assert len(bank) == 20
    feedback = []
    for question_id, record in bank.items():
        module_id = question_id.split(".", 1)[0]
        required = {
            "prompt", "compact_prompt", "choices", "compact_choices",
            "correct_choice", "feedback", "animation_prompt",
            "animation_answer", "neovim_prompt", "neovim_answer",
        }
        assert required <= set(record), question_id
        assert record["prompt"].count("{{FULL_EVIDENCE}}") == 1
        assert record["compact_prompt"].count("{{COMPACT_EVIDENCE}}") == 1
        all_text = json.dumps(record, ensure_ascii=False)
        markers = {
            token for token in ("{{FULL_EVIDENCE}}", "{{COMPACT_EVIDENCE}}",
                                "{{EXPECTED}}", "{{KNOWN_COMMANDS}}")
            if token in all_text
        }
        assert markers <= ALLOWED_MARKERS, (question_id, markers)
        assert "ANIMATION" in record["prompt"] and "NEOVIM" in record["prompt"]
        assert "ANIMATION" in record["compact_prompt"] and "NEOVIM" in record["compact_prompt"]
        assert len(record["choices"]) == 4
        assert len(record["compact_choices"]) == 4
        assert len(record["feedback"]) == 4
        assert 0 <= record["correct_choice"] < 4
        assert len(set(record["choices"])) == 4
        assert len(set(record["compact_choices"])) == 4
        assert all("ANIMATION: " in choice and " | NEOVIM: " in choice
                   for choice in record["choices"])
        assert all("A: " in choice and " · V: " in choice
                   for choice in record["compact_choices"])
        assert all(len(choice) <= 72 for choice in record["compact_choices"])
        lower = all_text.casefold()
        assert not any(term in lower for term in (
            "project-wide", "whole-file", "global substitute", "hidden recipe",
            "registration contract", "makes only its named change",
        )), question_id
        subject_hits = sum(term in lower for term in FOCAL_TERMS[module_id])
        assert subject_hits >= 3, (question_id, subject_hits)
        feedback.extend(record["feedback"])
    assert len(feedback) == len(set(feedback))


def test_questions_match_current_contract_motion_and_hold_facts():
    """Admission follows the executable plates, not the older subject names."""
    import sys

    sys.path.insert(0, str(BANK.parent))
    import module_animations  # noqa: E402

    bank = json.loads(BANK.read_text(encoding="utf-8"))
    for index in range(20):
        module_id = f"M{index}"
        contract = module_animations.endcap_study_contract(module_id)
        question = bank[f"{module_id}.REWARD.P01"]
        text = json.dumps(question, ensure_ascii=False).casefold()
        assert len(contract["start"]) == len(contract["target"])
        assert contract["start"] != contract["target"]
        assert len(contract["changed_cells"]) >= 4
        assert sum(contract["frame_slices"]) == len(contract["start"])

        # Only these three current plates contain intentional repeated holds;
        # every other sequence must be described as advancing poses.
        intentional_hold = module_id in {"M7", "M10", "M12"}
        if intentional_hold:
            assert "hold" in text
        elif module_id != "M1":  # M1 uses “hold the axis” as a verb, not timing.
            assert "intentional hold" not in text
            assert "pause" not in text

        correct = question["choices"][question["correct_choice"]].casefold()
        if module_id == "M0":
            assert "particle" in text and "rays" in text
            assert "impact pause" not in text
        elif module_id == "M2":
            assert "whole-body" in text and "support" in text
        elif module_id == "M6":
            assert "four accent" in correct
            assert "delete" not in correct
        elif module_id == "M11":
            assert "r{char}" in correct and "u" in correct and "<c-r>" in correct
            assert "replace-mode" not in text
        elif module_id == "M15":
            assert "shadow direction" in correct
            assert "shadow base fixed" not in text
        elif module_id == "M17":
            assert "homologous" in text and "coherent" in text
            assert "unchanged eye" not in text
        elif module_id == "M18":
            assert "hold" not in text
        elif module_id == "M19":
            assert all(term in text for term in ("full-body", "squash", "ground"))
            assert "eye still" not in text


def test_endcap_answers_describe_the_supplied_target_not_new_construction():
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    correct = {key.split(".")[0]: row["choices"][row["correct_choice"]].casefold()
               for key, row in bank.items()}
    for module_id in ("M3", "M4", "M5", "M8", "M16"):
        assert "replace" in correct[module_id], module_id
        assert not any(word in correct[module_id] for word in ("append", "yank", "erase", "copy")), module_id
    assert "pivot coordinate" in correct["M4"]
    assert "label digits" in correct["M16"]
    assert "rail glyphs" in correct["M18"]
    assert "rays fixed" not in bank["M0.REWARD.P01"]["compact_choices"][0]


def test_c33_question_wording_matches_trajectory_and_held_copy_contract():
    bank = json.loads(BANK.read_text(encoding="utf-8"))

    m7 = bank["M7.REWARD.P01"]
    m7_text = json.dumps(m7, ensure_ascii=False).casefold()
    assert "six" in m7_text
    assert "held" in m7_text and "copy" in m7_text
    assert "one scoped completion change" not in m7_text
    assert "one local replacement" not in m7_text

    m18 = bank["M18.REWARD.P01"]
    m18_text = json.dumps(m18, ensure_ascii=False).casefold()
    assert "translat" in m18_text and "turn" in m18_text
    assert "rail coordinates stay fixed" not in m18_text
    correct_m18 = m18["choices"][m18["correct_choice"]].casefold()
    assert "translating" in correct_m18 and "turning" in correct_m18
