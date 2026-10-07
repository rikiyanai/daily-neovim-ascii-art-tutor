"""C33 provenance gates for M11 undo-history art."""

from __future__ import annotations

import sys
import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import gen_curriculum_v2 as generator  # noqa: E402
import v2_runtime  # noqa: E402
from history_source_frames import (  # noqa: E402
    HISTORY_CARD_CHARACTERS,
    HISTORY_SOURCE_FRAMES,
    frame_sequence_matches,
    source_rows,
    validate_history_diagram_text,
    validate_history_card_art,
    validate_history_recipe,
)


HISTORY_IDS = tuple(HISTORY_CARD_CHARACTERS)


def actual_recipe_source_errors(card_id, card, *, registration_prefix=None):
    """Measure complete visible step states, not just their declared poses."""
    from test_review_effects import run_clean_effect
    prefix = ""
    errors = []
    for index, (keys, _why) in enumerate(card["recipe"], 1):
        prefix += keys
        _matches_target, result, detail = run_clean_effect({
            "start": card["start"], "target": card["target"], "expected": prefix})
        if result is None:
            errors.append((card_id, index, detail))
        elif not frame_sequence_matches(result["lines"], HISTORY_CARD_CHARACTERS[card_id],
                                        registration_prefix=registration_prefix):
            errors.append((card_id, index, result["lines"]))
    return errors


def test_manifest_does_not_credit_tutor_palette_labels_as_source_poses():
    assert not any("palette" in name for name in HISTORY_SOURCE_FRAMES["snowbunny"])


def test_actual_visible_recipe_steps_are_source_frames():
    if not shutil.which("nvim"):
        return
    cards = {card["id"]: card for card in generator.build()["cards"]}
    for card_id in HISTORY_IDS:
        prefix = " " if card_id in {"M11.BR", "M11.GM", "M11.GP", "M11.ER"} else None
        assert actual_recipe_source_errors(card_id, cards[card_id], registration_prefix=prefix) == []
        for variant in cards[card_id].get("review_variants", []):
            assert actual_recipe_source_errors(card_id, variant) == []


def test_actual_intermediate_rejects_a_lied_source_manifest_even_if_final_is_restored():
    if not shutil.which("nvim"):
        return
    source = source_rows("skully", "idle")
    card = {"start": source, "target": source,
            "recipe": [["2G0forX", "claimed source take"], ["u", "restore the source"]]}
    errors = actual_recipe_source_errors("M11.UT", card)
    assert len(errors) == 1 and errors[0][1] == 1, errors


def test_manifest_is_explicit_and_nonempty():
    assert set(HISTORY_SOURCE_FRAMES) == {"skully", "frog", "missile", "chick", "snowbunny"}
    for character, frames in HISTORY_SOURCE_FRAMES.items():
        assert frames, character
        for name, record in frames.items():
            assert record["source"].startswith("official-")
            assert len(record["rows"]) == 3, (character, name)
            assert all(isinstance(row, str) and row for row in record["rows"])


def test_source_frames_accept_complete_cards_and_registration_rail():
    assert frame_sequence_matches(source_rows("skully", "look"), "skully")
    railed = [" " + row for row in source_rows("skully", "look")]
    assert frame_sequence_matches(railed, "skully", registration_prefix=" ")
    strip = source_rows("skully", "look") + source_rows("skully", "idle")
    assert frame_sequence_matches(strip, "skully")


def test_negative_control_rejects_invented_skully_eye():
    invented = source_rows("skully", "idle")
    invented[1] = invented[1].replace("o", "!", 1)
    assert not frame_sequence_matches(invented, "skully")
    errors = validate_history_card_art("M11.BR", [" " + row for row in source_rows("skully", "blink")],
                                       [" " + row for row in invented])
    assert any("non-source" in error for error in errors)


def test_negative_control_rejects_invented_snowbunny_nose():
    invented = source_rows("snowbunny", "idle")
    invented[1] = invented[1].replace(".", "!", 1)
    assert not frame_sequence_matches(invented, "snowbunny")
    errors = validate_history_card_art(
        "M11.UR", source_rows("snowbunny", "idle"), invented)
    assert any("non-source" in error for error in errors)


def test_negative_control_rejects_unlabelled_recipe_take():
    errors = validate_history_recipe(
        "M11.BR", "2G:s/=/!/g<CR>", [["!", "invented take"]],
        frames=[source_rows("skully", "idle")])
    assert errors
    assert any("unlabelled authored punctuation" in error for error in errors)


def test_negative_control_rejects_non_punctuation_invented_take():
    invented = source_rows("skully", "idle")
    invented[1] = invented[1].replace("o", "x", 1)
    errors = validate_history_recipe(
        "M11.BR", "r*", [["r*", "invented source take"]], frames=[invented])
    assert any("not a complete skully source frame" in error for error in errors)


def test_diagram_gate_accepts_source_and_rejects_invented_frame():
    source = source_rows("skully", "idle")
    text = "\n".join("│" + row + "│" for row in source)
    assert validate_history_diagram_text("M11.BR", text) == []
    invented = list(source)
    invented[1] = invented[1].replace("o", "x", 1)
    bad = "\n".join("│" + row + "│" for row in invented)
    errors = validate_history_diagram_text("M11.BR", bad)
    assert any("diagram frame" in error for error in errors)


def test_authored_original_recipe_punctuation_is_explicitly_allowed():
    assert validate_history_recipe(
        "M11.BR", "r!", [["r!", "use the authored original punctuation take"]],
        frames=[[" " + row for row in source_rows("skully", "idle")]]) == []


def test_explicit_authored_original_frame_is_the_only_non_source_exception():
    invented = source_rows("skully", "idle")
    invented[1] = invented[1].replace("o", "x", 1)
    assert validate_history_recipe(
        "M11.BR", "r*", [["r*", "use the authored original frame"]],
        frames=[{"rows": [" " + row for row in invented],
                 "label": "authored original learner study"}]) == []


def test_generated_history_cards_and_reviews_are_source_backed():
    curriculum = generator.build()
    cards = {card["id"]: card for card in curriculum["cards"]}
    for card_id in HISTORY_IDS:
        card = cards[card_id]
        assert card["history_source_provenance"]["character"] == HISTORY_CARD_CHARACTERS[card_id]
        assert validate_history_card_art(card_id, card["start"], card["target"]) == []
        for variant in card.get("review_variants", []):
            assert not generator.validate_history_review_art(card_id, variant)


def test_history_recipes_reach_targets_in_clean_neovim():
    if not shutil.which("nvim"):
        return
    curriculum = generator.build()
    cards = {card["id"]: card for card in curriculum["cards"]}
    for card_id in HISTORY_IDS:
        card = cards[card_id]
        contract = {"initial_lines": card["start"], "target_lines": card["target"]}
        ok, _evidence, detail = v2_runtime._safe_typed_effect(contract, card["expected"])
        assert ok, (card_id, card["expected"], detail)
        for index, variant in enumerate(card.get("review_variants", []), 1):
            contract = {"initial_lines": variant["start"], "target_lines": variant["target"]}
            ok, _evidence, detail = v2_runtime._safe_typed_effect(contract, variant["expected"])
            assert ok, (card_id, "review", index, variant["expected"], detail)
