"""Contract, parity, and recipe tests for the whole-module animation endcaps."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import v2_runtime  # noqa: E402


def _generator():
    module = importlib.import_module("gen_curriculum_v2")
    assert module.animation_expansion_available(), (
        "module_animations.py and animation_for() are required before this suite"
    )
    return module


def _generated():
    generator = _generator()
    current = generator.build()
    installed = json.loads((ROOT / "curriculum-v2.json").read_text(encoding="utf-8"))
    return generator, current, installed


def test_animation_endcaps_are_generated_and_ordered():
    generator, current, installed = _generated()
    assert current == installed
    assert current["revision"] == "2026-10-02.77"
    assert len(current["modules"]) == 20
    assert len(current["cards"]) == 311
    assert len(current["questions"]) == 491
    assert set(generator.MODULE_ANIMATIONS) == {f"M{index}" for index in range(20)}

    cards_by_id = {card["id"]: card for card in current["cards"]}
    module_by_id = {module["id"]: module for module in current["modules"]}
    reward_cards = []
    for module_id in (f"M{index}" for index in range(20)):
        module = module_by_id[module_id]
        card_ids = module["card_ids"]
        # Late guided bridges may remain between the endcap and .08.
        assert card_ids.index(f"{module_id}.07") < card_ids.index(f"{module_id}.REWARD") < card_ids.index(f"{module_id}.08")
        assert module["module_reward"]["card_id"] == f"{module_id}.REWARD"
        reward = cards_by_id[f"{module_id}.REWARD"]
        reward_cards.append(reward)
        assert reward["kind"] == "module_reward"
        assert reward["artifact"] == "animation-study"
        assert reward["source_ref"].endswith(f"animation_for({module_id})")
        assert "source_motion" not in reward
        assert reward["start"] != reward["target"]
        assert len(reward["frame_slices"]) >= 8
        assert all(isinstance(size, int) and size > 0 for size in reward["frame_slices"])
        assert sum(reward["frame_slices"]) == len(reward["start"]) == len(reward["target"])
        metadata = reward["module_reward"]
        for field in ("key_pose", "timing", "hold", "known_taught_commands"):
            assert metadata.get(field), (module_id, field)
        assert len(metadata["known_taught_commands"]) >= 1
        assert reward["method_requirement"].get("all_of") == metadata["known_taught_commands"]
        assert "exact_any_of" not in reward["method_requirement"]

    # Metadata is attached separately to every existing module card, while
    # each source-motion field remains owned by its original card.
    for card in current["cards"]:
        assert "module_reward" in card
        if card["kind"] != "module_reward":
            assert card["module_reward"]["module_id"] == card["module_id"]
    assert generator.animation_expansion_available()


def test_endcap_questions_are_independent_and_cross_domain():
    _generator_module, current, _installed = _generated()
    rewards = {card["id"]: card for card in current["cards"] if card["kind"] == "module_reward"}
    questions = {question["id"]: question for question in current["questions"]}
    authored = json.loads(
        (ROOT / "questions-authored-v2-animation-expansion.json").read_text(encoding="utf-8")
    )
    assert set(authored) == {f"M{index}.REWARD.P01" for index in range(20)}
    assert len(questions) == len(current["questions"])
    stems = set()
    for card_id, card in rewards.items():
        question = questions[f"{card_id}.P01"]
        assert question["authorship"] == "manual"
        assert question["card_id"] == card_id
        assert question["form"] == "multiple_choice"
        assert "ANIMATION\n" in question["prompt"]
        assert "NEOVIM\n" in question["prompt"]
        assert "ANIMATION" in question["compact_prompt"]
        assert "NEOVIM" in question["compact_prompt"]
        assert len(question["choices"]) == len(question["feedback"]) == 4
        assert len(set(question["choices"])) == 4
        assert all("ANIMATION:" in choice and "NEOVIM:" in choice for choice in question["choices"])
        assert all("A:" in choice and "V:" in choice for choice in question["compact_choices"])
        assert question["evidence"]["frame_count"] == len(card["frame_slices"])
        assert question["evidence"]["frame_slices"] == card["frame_slices"]
        assert question["evidence"]["full"]
        assert question["evidence"]["compact"]
        assert question["module_id"] == card["module_id"]
        stems.add(question["animation_prompt"])
        assert "{{" not in json.dumps(question)
        # Independent questions discuss the operation without printing the
        # full example recipe or every exact primitive as an answer clue.
        authored_text = json.dumps(authored[question["id"]])
        assert "{{EXPECTED}}" not in authored_text
        assert "{{KNOWN_COMMANDS}}" not in authored_text
    assert len(stems) == 20


def test_each_endcap_recipe_changes_the_full_sequence_in_neovim():
    _generator_module, current, _installed = _generated()
    rewards = [card for card in current["cards"] if card["kind"] == "module_reward"]
    for card in rewards:
        ok, evidence, detail = v2_runtime._safe_typed_effect(
            {
                "initial_lines": card["start"],
                "target_lines": card["target"],
                "target_cursor": card.get("target_cursor"),
                "effect_version": 1,
            },
            card["expected"],
        )
        assert ok, (card["id"], card["expected"], detail, evidence)
        assert evidence["window_count"] == 1
        assert evidence["tab_count"] == 1


def test_existing_review_and_source_boundaries_are_not_replaced():
    _generator_module, current, _installed = _generated()
    for card in current["cards"]:
        if card["kind"] == "module_reward":
            continue
        variants = card.get("review_variants", [])
        if variants:
            starts = [tuple(variant.get("start", [])) for variant in variants]
            assert len(variants) >= 2
            assert len(starts) == len(set(starts))
            assert card.get("review_source_card_id") == card["id"]
            assert card.get("review_method_family")
            if card.get("method_requirement"):
                for variant in variants:
                    assert variant.get("method_requirement")
        if card.get("source_motion"):
            assert card["source_motion"].get("frames")
            assert card["source_motion"].get("credit")
            assert "module_animations.py" not in card["source_motion"].get("credit", "")
    for module in current["modules"]:
        reward = module["module_reward"]
        rights = reward.get("rights_gate", {})
        assert rights.get("original_art_only") is True
        assert rights.get("source_frames_imported") is False
        assert rights.get("new_unlicensed_source_import") is False
