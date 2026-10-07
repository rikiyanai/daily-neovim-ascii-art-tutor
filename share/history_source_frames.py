"""Source-frame provenance for the M11 undo-history exercises.

The history lessons teach Neovim state traversal, but their visible drawings
are credited Stone Story excerpts.  This module is the small, explicit
allow-list used by the generator and its tests: a history card may show only
one of these source frames (or a sequence of complete frames) for the named
character.  It intentionally does not manufacture a "take" by replacing a
source glyph with punctuation.
"""

from __future__ import annotations

from copy import deepcopy
import re

import stone_story_variants as ss


HISTORY_FRAME_ROWS = 3
_DIAGRAM_ROW = re.compile(r"│([^│]*)│")


# Keep the source path beside every frame name.  The rows themselves come from
# the audited source table; this manifest is the provenance boundary, not a
# second hand-transcribed pose table.
HISTORY_SOURCE_FRAMES = {
    "skully": {
        "idle": {
            "source": "official-Pets/Skully res01",
            "rows": tuple(ss.SKULLY_IDLE),
        },
        "look": {
            "source": "official-Pets/Skully res01 + res02 look overlay",
            "rows": tuple(ss.SKULLY_LOOK),
        },
        "blink": {
            "source": "official-Pets/Skully res01 + res04 blink overlay",
            "rows": tuple(ss.SKULLY_BLINK),
        },
    },
    "frog": {
        "open": {
            "source": "official-Pets/Frog res01",
            "rows": tuple(ss.FROG_OPEN),
        },
        "one_open": {
            "source": "official-Pets/Frog res01 + res05 right-eye overlay",
            "rows": tuple(ss.FROG_ONE_OPEN),
        },
        "half": {
            "source": "official-Pets/Frog res01 + res06 half-blink overlay",
            "rows": tuple(ss.FROG_HALF),
        },
        "shut": {
            "source": "official-Pets/Frog res01 + res07 shut-eye overlay",
            "rows": tuple(ss.FROG_SHUT),
        },
    },
    "missile": {
        "f1": {
            "source": "official-Games/TowerDefense res18 frame 1",
            "rows": tuple(ss.MISSILE_F1),
        },
        "f2": {
            "source": "official-Games/TowerDefense res18 frame 2",
            "rows": tuple(ss.MISSILE_F2),
        },
        "f3": {
            "source": "official-Games/TowerDefense res18 frame 3",
            "rows": tuple(ss.MISSILE_F3),
        },
        "f4": {
            "source": "official-Games/TowerDefense res18 frame 4",
            "rows": tuple(ss.MISSILE_F4),
        },
    },
    "chick": {
        "egg_f1": {
            "source": "official-Pets/Chick res01 frame 1",
            "rows": tuple(ss.CHICK_EGG_F1),
        },
        "egg_f2": {
            "source": "official-Pets/Chick res01 frame 2",
            "rows": tuple(ss.CHICK_EGG_F2),
        },
        "egg_f3": {
            "source": "official-Pets/Chick res01 frame 3",
            "rows": tuple(ss.CHICK_EGG_F3),
        },
        "egg_f4": {
            "source": "official-Pets/Chick res01 frame 4",
            "rows": tuple(ss.CHICK_EGG_F4),
        },
    },
    "snowbunny": {
        "idle": {
            "source": "official-Pets/SnowBunny res01",
            "rows": tuple(ss.SNOWBUNNY_IDLE),
        },
        "blink": {
            "source": "official-Pets/SnowBunny res01 + res03 blink overlay",
            "rows": tuple(ss.SNOWBUNNY_BLINK),
        },
    },
}


# Card id -> source character.  A card can contain a complete frame strip;
# validation below splits it into three-row frames before checking it.
HISTORY_CARD_CHARACTERS = {
    "M11.UR": "snowbunny",
    "M11.BR": "skully",
    "M11.GM": "frog",
    "M11.GP": "frog",
    "M11.ER": "missile",
    "M11.UB": "chick",
    "M11.UG": "frog",
    "M11.UE": "missile",
    "M11.UT": "skully",
    "M11.UTH": "snowbunny",
}


def source_rows(character: str, frame: str) -> list[str]:
    """Return a copy of one explicitly registered source frame."""

    return list(HISTORY_SOURCE_FRAMES[character][frame]["rows"])


def source_frame_names(character: str) -> tuple[str, ...]:
    """Return the stable frame names available for one source character."""

    return tuple(HISTORY_SOURCE_FRAMES[character])


def source_frame_sources(character: str) -> dict[str, str]:
    """Return frame-name to source-credit mapping for diagnostics."""

    return {
        name: record["source"]
        for name, record in HISTORY_SOURCE_FRAMES[character].items()
    }


def _strip_registration_prefix(rows: list[str], prefix: str | None) -> list[str]:
    if prefix is None:
        return rows
    if not all(row.startswith(prefix) for row in rows):
        return rows
    return [row[len(prefix):] for row in rows]


def frame_sequence_matches(
    art: list[str] | tuple[str, ...],
    character: str,
    *,
    registration_prefix: str | None = None,
    frame_rows: int = HISTORY_FRAME_ROWS,
) -> bool:
    """Return whether *art* is a sequence of complete source frames.

    A one-cell registration rail is allowed only when the caller names it
    explicitly.  This prevents a guessed prefix or an invented interior glyph
    from passing as a source pose.  Blank separator rows are not accepted in a
    history card; the cards use contiguous frame strips and preserve frame
    boundaries through ``frame_slices``.
    """

    if frame_rows < 1 or len(art) == 0 or len(art) % frame_rows:
        return False
    rows = _strip_registration_prefix(list(art), registration_prefix)
    if len(rows) != len(art) or any(row == "" for row in rows):
        return False
    allowed = {
        tuple(record["rows"])
        for record in HISTORY_SOURCE_FRAMES[character].values()
    }
    frames = [tuple(rows[index:index + frame_rows])
              for index in range(0, len(rows), frame_rows)]
    return all(frame in allowed for frame in frames)


def validate_history_card_art(
    card_id: str,
    start: list[str] | tuple[str, ...],
    target: list[str] | tuple[str, ...],
) -> list[str]:
    """Return provenance errors for a registered history card's art."""

    character = HISTORY_CARD_CHARACTERS.get(card_id)
    if character is None:
        return []
    # BR, GM, and the single-frame history cards retain one tutor registration
    # space.  UT/UTH are contiguous source-frame strips without that rail.
    prefix = (" " if card_id in {"M11.BR", "M11.GM", "M11.GP", "M11.ER"}
              else None)
    errors = []
    if not frame_sequence_matches(start, character, registration_prefix=prefix):
        errors.append(f"{card_id}: start is not a complete {character} source frame")
    if not frame_sequence_matches(target, character, registration_prefix=prefix):
        errors.append(f"{card_id}: target contains a non-source {character} frame")
    return errors


def validate_history_review_art(card_id: str, variant: dict) -> list[str]:
    """Return provenance errors for one hidden-card review variant."""

    character = HISTORY_CARD_CHARACTERS.get(card_id)
    if character is None:
        return []
    if not frame_sequence_matches(variant.get("start", []), character):
        return [f"{card_id}: review start is not a complete {character} source frame"]
    if not frame_sequence_matches(variant.get("target", []), character):
        return [f"{card_id}: review target contains a non-source {character} frame"]
    return []


def validate_history_recipe(
    card_id: str,
    expected: str,
    recipe: list[list[str]] | tuple[tuple[str, str], ...],
    *,
    frames: list[list[str] | tuple[str, ...] | dict] | None = None,
) -> list[str]:
    """Validate every visible history intermediate against the source manifest.

    ``frames`` is the explicit ordered sequence shown or implied by the
    learner-facing recipe.  A history recipe is not source-safe merely because
    it avoids ``!``: every complete frame in that sequence must be present in
    the named character's manifest.  A future authored original can opt out
    only by keeping its art outside the credited source sequence and labelling
    that separate original in its recipe prose.
    """

    if card_id not in HISTORY_CARD_CHARACTERS:
        return []
    character = HISTORY_CARD_CHARACTERS[card_id]
    prefix = (" " if card_id in {"M11.BR", "M11.GM", "M11.GP", "M11.ER"}
              else None)
    if not frames:
        return [f"{card_id}: recipe lacks an explicit source-frame sequence"]
    errors = []
    for index, frame in enumerate(frames, 1):
        label = ""
        rows = frame
        if isinstance(frame, dict):
            rows = frame.get("rows", [])
            label = str(frame.get("label", ""))
        if not frame_sequence_matches(rows, character, registration_prefix=prefix):
            if "authored original" in label.lower():
                continue
            errors.append(
                f"{card_id}: recipe intermediate {index} is not a complete {character} source frame")
    steps = [[str(part) for part in step] for step in recipe]
    for step_index, step in enumerate(steps, 1):
        if any("!" in part for part in step):
            if not any("authored original" in part.lower() for part in step):
                errors.append(
                    f"{card_id}: recipe step {step_index} contains an unlabelled authored punctuation take")
    expected_has_label = any(
        any("!" in part for part in step)
        and any("authored original" in part.lower() for part in step)
        for step in steps
    )
    if "!" in expected and not expected_has_label:
        errors.append(f"{card_id}: expected keys contain an unlabelled authored punctuation take")
    return errors


def diagram_frames(text: str) -> list[tuple[str, ...]]:
    """Extract complete three-row rail diagrams from learner-facing text."""

    lines = text.splitlines()
    found = []
    for index in range(len(lines) - HISTORY_FRAME_ROWS + 1):
        rows = [_DIAGRAM_ROW.findall(lines[index + offset])
                for offset in range(HISTORY_FRAME_ROWS)]
        if not rows[0] or any(len(row) != len(rows[0]) for row in rows):
            continue
        for column in range(len(rows[0])):
            # Right padding belongs to the diagram's rectangular display rail,
            # not to the canonical source text. Never strip leading spaces or
            # normalize the learner's actual artifact at this boundary.
            frame = tuple(row[column].rstrip(" ") for row in rows)
            if all(frame) and frame not in found:
                found.append(frame)
    return found


def validate_history_diagram_text(card_id: str, text: str) -> list[str]:
    """Reject complete learner-visible diagrams that are not source frames."""

    character = HISTORY_CARD_CHARACTERS.get(card_id)
    if character is None:
        return []
    errors = []
    for index, frame in enumerate(diagram_frames(text), 1):
        if not frame_sequence_matches(frame, character):
            errors.append(
                f"{card_id}: diagram frame {index} is not a complete {character} source frame")
    return errors


def manifest_snapshot() -> dict:
    """Provide immutable-ish data for tests without exposing mutable rows."""

    return deepcopy(HISTORY_SOURCE_FRAMES)
