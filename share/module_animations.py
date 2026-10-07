"""Canonical, original text-art studies for the twenty animation modules.

The module curriculum names subjects and editing decisions, but the old reward
art only showed a pair of frames.  This file is the small, source-independent
animation catalogue consumed by the future lesson generator.  Frames remain
plain text: no raster assets, source frame imports, or generated images are
hidden behind this API.

The Stone Story / AAHub material named in ``provenance`` is method and metric
context only.  Every sequence below is credited as an original study authored
for this tutor.  M10 is deliberately limited to proportional idioms already
present in the authored M10 curriculum transcription; it makes no new corpus
or glyph-admission claim.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable


ORIGINAL_CREDIT = (
    "Original sequence authored for daily-neovim-ascii-art-tutor; "
    "research sources inform method only and contribute no copied frame."
)


def _frame(width: int, *rows: str) -> tuple[str, ...]:
    """Return one registered text frame with equal row bounds."""

    if not rows:
        raise ValueError("an animation frame needs at least one row")
    # ``width`` is the intended box width.  A hand-authored row can be a
    # little longer while a study is being tuned; _sequence normalizes the
    # complete sequence to the largest authored row so no frame silently
    # acquires a different registration box.
    return tuple(rows)


def _sequence(
    module_id: str,
    title: str,
    subject: str,
    width: int,
    frames: Iterable[tuple[str, ...]],
    *,
    anchor: dict[str, Any],
    key_poses: list[dict[str, Any]],
    fps: int,
    holds: list[int],
    pacing: str,
    source_ref: str,
    stages: tuple[str, ...],
    medium: str = "monospace",
    extra_provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raw_frames = tuple(tuple(row for row in frame) for frame in frames)
    actual_width = max(width, *(len(row) for frame in raw_frames for row in frame))
    materialized = tuple(
        tuple(row.ljust(actual_width) for row in frame) for frame in raw_frames
    )
    if len(materialized) < 8:
        raise ValueError(f"{module_id} needs at least eight frames")
    rows = len(materialized[0])
    if any(len(frame) != rows for frame in materialized):
        raise ValueError(f"{module_id} has unequal frame heights")
    if any(any(len(row) != actual_width for row in frame) for frame in materialized):
        raise ValueError(f"{module_id} has unequal row widths")
    if not 6 <= len(set(materialized)):
        raise ValueError(f"{module_id} needs six meaningful poses; found {len(set(materialized))}")
    interval = {
        "fps": fps,
        "duration_seconds": round(len(materialized) / fps, 3),
        "holds": holds,
        "tutorial_pacing": pacing,
    }
    provenance = {
        "kind": "original-authored",
        "credit": ORIGINAL_CREDIT,
        "source_use": "method and topic context only; no source frame imported",
        "source_ref": source_ref,
    }
    if extra_provenance:
        provenance.update(extra_provenance)
    return {
        "module_id": module_id,
        "title": title,
        "subject": subject,
        "credit": ORIGINAL_CREDIT,
        "provenance": provenance,
        "source_ref": source_ref,
        "rights_gate": {
            "original_art_only": True,
            "source_frames_imported": False,
            "new_unlicensed_source_import": False,
        },
        "medium": medium,
        "bounds": {
            "rows": rows,
            "columns": actual_width,
            "metric": "Saitamaar codepoint/advance audit" if medium == "proportional-sjis" else "monospace codepoints",
        },
        "anchor": anchor,
        "key_poses": key_poses,
        "interval": interval,
        "stages": list(stages),
        "frame_count": len(materialized),
        "distinct_pose_count": len(set(materialized)),
        "frames": materialized,
    }


# The fixed-grid studies are intentionally small enough to read at playback
# speed.  Their changing parts are named in key_poses; repeated frames below
# are declared holds, never padding.
M0_FRAMES = (
    _frame(15, "       .       ", "      /|\\      ", "   --  o  --   ", "      \\|/      ", "       |       "),
    _frame(15, "       .       ", "     ./|\\      ", "   --  o  --   ", "      \\|/      ", "       |       "),
    _frame(15, "      .        ", "     /|\\       ", "  ---  O  --   ", "      \\|/      ", "       |       "),
    _frame(15, "      .        ", "   . /|\\       ", " --    O  ---  ", "      \\|/ .    ", "       |       "),
    _frame(15, "     *         ", "   . /|\\ .     ", "--    ***  --- ", "   . \\|/ .     ", "       |       "),
    _frame(15, "     *         ", "  . / | \\ .    ", "--   * O * --- ", "  .  \\|/  .    ", "       |       "),
    _frame(15, "      .        ", "       |       ", "   --  O  --   ", "       |       ", "       |       "),
    _frame(15, "       .       ", "      /|\\      ", "   --  O  --   ", "      \\|/      ", "       |       "),
)

M11_FRAMES = (
    _frame(19, "        .          ", "       /\\         ", "  <====[ o ]====>  ", "       \\/         ", "        |          "),
    _frame(19, "       .           ", "      /==\\        ", " <====[ o ]====>   ", "      \\/         ", "       .|.         "),
    _frame(19, "      .            ", "     //==\\       ", "<====[ O ]====>    ", "     \\/         ", "      ..|..        "),
    _frame(19, "     .             ", "    //==\\        ", "<===[ O ]====>     ", "    \\/         ", "    ...|...        "),
    _frame(19, "    .              ", "    //==\\        ", "<===[ * ]====>     ", "    \\/         ", "  ... | ...        "),
    _frame(19, "     .             ", "     /==\\        ", "<====[ * ]====>    ", "     \\/         ", "    .. | ..        "),
    _frame(19, "      .            ", "      /==\\       ", " <====[ O ]====>   ", "      \\/       ", "      . | .        "),
    _frame(19, "        .          ", "       /\\         ", "  <====[ O ]====>  ", "       \\/         ", "        |          "),
)

M1_FRAMES = (
    _frame(17, "      .---.       ", "  <---| o |--->   ", "      |/\\|       ", "      | ||        ", "      `-'-        ", "        |         "),
    _frame(17, "     .---.        ", " <---| o |--->    ", "      |/\\|       ", "      | ||        ", "      `-'-        ", "        |         "),
    _frame(17, "    .---.         ", "<---| O |--->     ", "      |/\\|       ", "      | ||        ", "      `-'-        ", "        |         "),
    _frame(17, "   .---.          ", "<--| O |--->      ", "      |/\\|       ", "      | ||        ", "      `-'-        ", "        |         "),
    _frame(17, "    .---.         ", "<---| O |--->     ", "      |:|         ", "      | ||        ", "      `-'-        ", "        |         "),
    _frame(17, "     .---.        ", " <---| o |--->    ", "      |:|         ", "      | ||        ", "      `-'-        ", "        |         "),
    _frame(17, "      .---.       ", "  <---| o |--->   ", "      |:|         ", "      | ||        ", "      `-'-        ", "        |         "),
    _frame(17, "      .---.       ", "  <---| o |--->   ", "      |/\\|       ", "      | ||        ", "      `-'-        ", "        |         "),
)

M19_OLD_FRAMES = (
    _frame(19, "    .------.       ", "   /  o  o  \\      ", "  |    ^     |      ", "  |  `---'   |      ", "   \\  ___  /       ", "    `-----'        "),
    _frame(19, "    .------.       ", "   /  O  o  \\      ", "  |    ^     |      ", "  |  `---'   |      ", "   \\  ___  /       ", "    `-----'        "),
    _frame(19, "    .------.       ", "   /  O  O  \\      ", "  |    ^     |      ", "  |  `---'   |      ", "   \\  ___  /       ", "    `-----'        "),
    _frame(19, "    .------.       ", "   /  *  O  \\      ", "  |    ^     |      ", "  |  `---'   |      ", "   \\  ___  /       ", "    `-----'        "),
    _frame(19, "    .------.       ", "   /  *  *  \\      ", "  |    ^     |      ", "  |  `-.-'   |      ", "   \\  ___  /       ", "    `-----'        "),
    _frame(19, "    .------.       ", "   /  O  *  \\      ", "  |    ^     |      ", "  |  `---'   |      ", "   \\  ___  /       ", "    `-----'        "),
    _frame(19, "    .------.       ", "   /  o  O  \\      ", "  |    ^     |      ", "  |  `---'   |      ", "   \\  ___  /       ", "    `-----'        "),
    _frame(19, "    .------.       ", "   /  o  o  \\      ", "  |    ^     |      ", "  |  `---'   |      ", "   \\  ___  /       ", "    `-----'        "),
)

M19_FRAMES = (
    _frame(19, "    .------.       ", "   /  o  o  \\      ", "  |    ^     |     ", "  |  \x60---'   |     ", "   \\  ___  /       ", "    \x60-----'        ", "    _____________  "),
    _frame(19, "    .------.       ", "   /  o  o  \\      ", "  |   <^>    |     ", "  |  \x60---'   |     ", "   \\ _____ /       ", "    _--------_     ", "    _____________  "),
    _frame(19, "                 ", "      .------.     ", "     /  O  o  \\    ", "    |    ^     |   ", "    |  \x60---'   |   ", "     \\  __  /     ", "    _____________  "),
    _frame(19, "                 ", "      .------.     ", "     /  O  O  \\    ", "    |    ^     |   ", "    |  \x60-.-'   |   ", "     \\  __  /     ", "    _____________  "),
    _frame(19, "                 ", "       .------.    ", "      /  *  O  \\   ", "     |    ^     |  ", "     |  \x60---'   |  ", "      \\  __  /    ", "    _____________  "),
    _frame(19, "    .------.       ", "   /  *  *  \\      ", "  |    ^     |     ", "  |  \x60-.-'   |     ", "   \\_______/       ", "    _--------_     ", "    _____________  "),
    _frame(19, "      .------.     ", "     /  O  *  \\    ", "    |    ^     |   ", "    |  \x60---'   |   ", "     \\  __  /     ", "                    ", "    _____________  "),
    _frame(19, "    .------.       ", "   /  o  o  \\      ", "  |    ^     |     ", "  |  \x60---'   |     ", "   \\  ___  /       ", "    \x60-----'        ", "    _____________  "),
)

M2_OLD_FRAMES = (
    _frame(15, "    .------.     ", "   /  o  o  \\    ", "  |    ^     |   ", "   \\  ---  /    ", "    `------'     "),
    _frame(15, "    .------.     ", "   /  O  o  \\    ", "  |    ^     |   ", "   \\  ---  /    ", "    `------'     "),
    _frame(15, "    .------.     ", "   /  O  O  \\    ", "  |    ^     |   ", "   \\  ---  /    ", "    `------'     "),
    _frame(15, "    .------.     ", "   /  -  O  \\    ", "  |    ^     |   ", "   \\  ---  /    ", "    `------'     "),
    _frame(15, "    .------.     ", "   /  .  O  \\    ", "  |    ^     |   ", "   \\  ---  /    ", "    `------'     "),
    _frame(15, "    .------.     ", "   /  o  o  \\    ", "  |    ^     |   ", "   \\  -.-  /    ", "    `------'     "),
    _frame(15, "    .------.     ", "   /  o  o  \\    ", "  |    ^     |   ", "   \\  ---  /    ", "    `------'     "),
    _frame(15, "    .------.     ", "   /  o  o  \\    ", "  |    ^     |   ", "   \\  ---  /    ", "    `------'     "),
)

M3_OLD_FRAMES = (
    _frame(15, "      .-.        ", "     / o \\       ", "    |  _  |      ", "    | /|\\ |      ", "    |  |  |      ", "    `--'--'      "),
    _frame(15, "      .-.        ", "     / O \\       ", "    |  _  |      ", "    | /|\\ |      ", "    |  |  |      ", "    `--'--'      "),
    _frame(15, "      .-.        ", "     / O \\       ", "    |  -  |      ", "    | /|\\ |      ", "    |  |  |      ", "    `--'--'      "),
    _frame(15, "      .-.        ", "     / O \\       ", "    |  _  |      ", "    | /|\\ |      ", "    | /   |      ", "    `--'--'      "),
    _frame(15, "      .-.        ", "     / o \\       ", "    |  _  |      ", "    | /|\\ |      ", "    | /   |      ", "    `--'--'      "),
    _frame(15, "      .-.        ", "     / o \\       ", "    |  _  |      ", "    | /|\\ |      ", "    |  |  |      ", "    `--'--'      "),
    _frame(15, "      .-.        ", "     / - \\       ", "    |  _  |      ", "    | /|\\ |      ", "    |  |  |      ", "    `--'--'      "),
    _frame(15, "      .-.        ", "     / o \\       ", "    |  _  |      ", "    | /|\\ |      ", "    |  |  |      ", "    `--'--'      "),
)

M2_FRAMES = (
    _frame(17, "    .------.     ", "   /  o  o  \\    ", "  |    ^     |   ", "  |   /|\\    |   ", "   \\  ---  /    ", "    \x60------'     "),
    _frame(17, "     .------.    ", "    /  o  o  \\   ", "   |    ^     |  ", "   |   /|\\    |  ", "    \\  ---  /   ", "     \x60------'    "),
    _frame(17, "    .------.     ", "   /  O  O  \\    ", "  |    ^     |   ", "  |  / | \\   |   ", "   \\  ---  /    ", "    \x60------'     "),
    _frame(17, "   .------.      ", "  /  -  O  \\     ", " |    ^     |    ", " |   /|     |    ", "  \\  ---  /     ", "   \x60------'      "),
    _frame(17, "     .-----.     ", "    /  .  O  \\   ", "   |   <^>   |   ", "   |   /|\\   |   ", "    \\  -.-  /   ", "     \x60-----'     "),
    _frame(17, "    .------.     ", "   /  o  o  \\    ", "  |    ^     |   ", "  |  / | \\   |   ", "   \\  ---  /    ", "    \x60------'     "),
    _frame(17, "     .------.    ", "    /  o  o  \\   ", "   |    ^     |  ", "   |   /|\\    |  ", "    \\  ---  /   ", "     \x60------'    "),
    _frame(17, "    .------.     ", "   /  o  o  \\    ", "  |    ^     |   ", "  |   /|\\    |   ", "   \\  ---  /    ", "    \x60------'     "),
)

M3_FRAMES = (
    _frame(15, "      .-.        ", "     / o \\       ", "    |  _  |      ", "    | /|\\ |      ", "    |  |  |      ", "    \x60--'--'      "),
    _frame(15, "       .-.       ", "      / O \\      ", "     |  _  |     ", "     | /|\\ |     ", "     |  /  |     ", "     \x60--'--'     "),
    _frame(15, "      .-.        ", "     / O \\       ", "    |  -  |      ", "    | /|\\ |      ", "    | /   |      ", "    \x60--'--'      "),
    _frame(15, "     .-.         ", "    / O \\        ", "   |  _  |       ", "   | /|  |       ", "   |  /  |       ", "   \x60--'--'       "),
    _frame(15, "      .-.        ", "     / * \\       ", "    |  _  |      ", "    | /|\\ |      ", "    |  |  |      ", "    \x60--'--'      "),
    _frame(15, "       .-.       ", "      / o \\      ", "     |  _  |     ", "     | /|\\ |     ", "     |  |\\ |     ", "     \x60--'--'     "),
    _frame(15, "      .-.        ", "     / o \\       ", "    |  _  |      ", "    | /|\\ |      ", "    | /   |      ", "    \x60--'--'      "),
    _frame(15, "      .-.        ", "     / o \\       ", "    |  _  |      ", "    | /|\\ |      ", "    |  |  |      ", "    \x60--'--'      "),
)

M4_FRAMES = (
    _frame(17, "       \\         ", "        \\        ", "    -- + --      ", "        /         ", "       /          "),
    _frame(17, "      \\          ", "       |          ", "    -- + --      ", "        /         ", "         /        "),
    _frame(17, "       |          ", "       |          ", "    -- + --      ", "       |          ", "       |          "),
    _frame(17, "        /         ", "       /          ", "    -- + --      ", "      \\          ", "       \\         "),
    _frame(17, "       /          ", "      /           ", "    -- + --      ", "     \\           ", "      \\          "),
    _frame(17, "       |          ", "       |          ", "    -- + --      ", "       |          ", "       |          "),
    _frame(17, "      \\          ", "       \\         ", "    -- + --      ", "         /        ", "        /         "),
    _frame(17, "       \\         ", "        \\        ", "    -- + --      ", "        /         ", "       /          "),
)

M5_FRAMES = (
    _frame(21, "..  ..      ..  ..", "   .       .       ", "        \\          ", "         +----      ", "           \\       ", ". . . . . . . . . . ", "====================="),
    _frame(21, "..  ..      ..  ..", "   .       .       ", "         \\         ", "          +---      ", "           \\       ", ". . . . . . . . . . ", "====================="),
    _frame(21, "..  ..      ..  ..", "   .       .       ", "          \\        ", "           +--      ", "           \\       ", ". . . . . . . . . . ", "====================="),
    _frame(21, "..  ..      ..  ..", "   .       .       ", "           |        ", "           +        ", "           |        ", ". . . . . . . . . . ", "====================="),
    _frame(21, "..  ..      ..  ..", "   .       .       ", "           /        ", "          +--       ", "          /         ", ". . . . . . . . . . ", "====================="),
    _frame(21, "..  ..      ..  ..", "   .       .       ", "          /         ", "         +---       ", "        /           ", ". . . . . . . . . . ", "====================="),
    _frame(21, "..  ..      ..  ..", "   .       .       ", "         /          ", "        +----       ", "       /            ", ". . . . . . . . . . ", "====================="),
    _frame(21, "..  ..      ..  ..", "   .       .       ", "        \\          ", "         +----      ", "           \\       ", ". . . . . . . . . . ", "====================="),
)

M6_FRAMES = (
    _frame(15, "       .       ", "      / \\      ", "     /   \\     ", "    /_____\\    ", "      ||        "),
    _frame(15, "       .       ", "      / .\\     ", "     /   \\     ", "    /_____\\    ", "      ||        "),
    _frame(15, "               ", "      / \\      ", "     /   \\     ", "    /_____\\    ", "      ||        "),
    _frame(15, "               ", "      / \\      ", "     /  .\\     ", "    /_____\\    ", "      ||        "),
    _frame(15, "               ", "               ", "     /   \\     ", "    /_____\\    ", "      ||        "),
    _frame(15, "               ", "               ", "               ", "    /___  \\    ", "      ||        "),
    _frame(15, "               ", "               ", "               ", "    /__   \\    ", "      ||        "),
    _frame(15, "       o       ", "      / \\      ", "     /   \\     ", "    /_____\\    ", "      ||        "),
)

# A static patterned ground keeps even the nearly erased pyramid readable
# without changing the height or inventing visible pyramid cells.
M6_FRAMES = tuple((*frame, "_ . _ . _ . _  ") for frame in M6_FRAMES)

M7_FRAMES = (
    _frame(15, "       .       ", "      / \\      ", "     /___\\     ", "      ||        ", "   =========    "),
    _frame(15, "       .       ", "      / \\      ", "     /___\\     ", "      ||        ", "   =========    "),
    _frame(15, "       .       ", "      /|\\      ", "     /___\\     ", "      ||        ", "   =========    "),
    _frame(15, "       .       ", "      /|\\  .   ", "     /_O_\\     ", "      ||        ", "   =========    "),
    _frame(15, "       .       ", "      /|\\      ", "    __/_O_\\__   ", "      ||        ", "   =========    "),
    _frame(15, "       .       ", "      /|\\      ", "    __/_O_\\__   ", "      ||        ", "   =========    "),
    _frame(15, "       .       ", "      /|\\  ;   ", "     /_O_\\     ", "      ||        ", "   =========    "),
    _frame(15, "       .       ", "      /|\\      ", "     /_._\\     ", "      ||        ", "   =========    "),
)

M8_FRAMES = (
    _frame(15, "      o         ", "     /|\\        ", "      |          ", "     / \\        ", "   __^__         "),
    _frame(15, "      o         ", "     /|\\        ", "      |          ", "    __/ \\       ", "      ^          "),
    _frame(15, "      o         ", "     /|\\        ", "      |          ", "   __/   \\      ", "      ^          "),
    _frame(15, "      o         ", "     /|\\        ", "      |          ", "  __/     \\     ", "      ^          "),
    _frame(15, "      o         ", "     /|          ", "      |          ", "  __/\\    \\    ", "      ^          "),
    _frame(15, "      o         ", "     /|          ", "      |          ", "   __/ \\  \\    ", "      ^          "),
    _frame(15, "      o         ", "     /|\\        ", "      |          ", "    __/ \\       ", "      ^          "),
    _frame(15, "      o         ", "     /|\\        ", "      |          ", "     / \\        ", "   __^__         "),
)

M9_FRAMES = (
    _frame(15, "      o         ", "               ", "               ", "      ^         ", "==============="),
    _frame(15, "      o         ", "      |        ", "               ", "      ^         ", "==============="),
    _frame(15, "      .         ", "     / \\       ", "               ", "      ^         ", "==============="),
    _frame(15, "               ", "    _---_      ", "               ", "      ^         ", "==============="),
    _frame(15, "      .         ", "     / \\       ", "               ", "      ^         ", "==============="),
    _frame(15, "      o         ", "      |        ", "               ", "      ^         ", "==============="),
    _frame(15, "      O         ", "               ", "               ", "      ^         ", "==============="),
    _frame(15, "      o         ", "               ", "      .        ", "      ^         ", "==============="),
)

# M10 is the sole proportional sequence.  Every non-space spelling below is
# already present in the authored M10 curriculum cards; in particular the
# full-width U+3000 and half-width U+0020 spaces are retained verbatim.
M10_FRAMES = (
    _frame(12, "　　⌒?", "　（　　）", "　　ヽ_ノ"),
    _frame(12, "　　⌒ヽ", "　（　　）", "　　ヽ_ノ"),
    _frame(12, "　　r'⌒?.", "　 (　　 　 )", "　　　)ノ´"),
    _frame(12, "　　r'⌒ヽ.", "　 (　　 　 )", "　　　)ノ´"),
    _frame(12, "　／￣＼", "（　　　）", "　＼＿／"),
    _frame(12, "　／￣＼", "（　　　）", "　＼＿／"),
    _frame(12, "／￣￣＼", "|ﾆ二ニ|", "＼＿＿／"),
    _frame(12, "　　⌒ヽ", "　（　　）", "　　ヽ_ノ"),
)

M12_FRAMES = (
    _frame(17, "  :----+----:  ", " /      |      \\", "<       o       >"),
    _frame(17, "  !----+----:  ", " /      |      \\", "<       o       >"),
    _frame(17, "  !----+----:  ", " /      |      \\", "<       o       >"),
    _frame(17, "  !----+----;  ", " /      |      \\", "<       o       >"),
    _frame(17, "  :----+----;  ", " /      |      \\", "<       o       >"),
    _frame(17, "  :----+----!  ", " /      |      \\", "<       o       >"),
    _frame(17, "  :----+----!  ", " /      |      \\", "<       o       >"),
    _frame(17, "  :----+----:  ", " /      |      \\", "<       O       >"),
)

M13_FRAMES = (
    _frame(19, "  ..    ::    --  ", "      .  .       ", "  --    +    ::  "),
    _frame(19, "  !.    ::    --  ", "      .  .       ", "  --    +    ::  "),
    _frame(19, "  !!    ::    --  ", "      .  .       ", "  --    +    ::  "),
    _frame(19, "  !!    !:    --  ", "      .  .       ", "  --    +    ::  "),
    _frame(19, "  !!    !!    --  ", "      .  .       ", "  --    +    ::  "),
    _frame(19, "  !!    !!    !-  ", "      .  .       ", "  --    +    ::  "),
    _frame(19, "  !!    !!    !!  ", "      .  .       ", "  --    +    ::  "),
    _frame(19, "  ..    ::    --  ", "      .  .       ", "  --    +    ::  "),
)

M14_FRAMES = (
    _frame(17, "   .-----.       ", "  /  o o  \\      ", " |    ^    |      ", "  \\  ---  /      "),
    _frame(17, "   .-----.       ", "  /  O o  \\      ", " |    ^    |      ", "  \\  ---  /      "),
    _frame(17, "   .-----.       ", "  /  O O  \\      ", " |    ^    |      ", "  \\  ---  /      "),
    _frame(17, "   .-----.       ", "  /  * O  \\      ", " |    ^    |      ", "  \\  ---  /      "),
    _frame(17, "   .-----.       ", "  /  * *  \\      ", " |    ^    |      ", "  \\  ---  /      "),
    _frame(17, "   .-----.       ", "  /  O *  \\      ", " |    ^    |      ", "  \\  ---  /      "),
    _frame(17, "   .-----.       ", "  /  o O  \\      ", " |    ^    |      ", "  \\  ---  /      "),
    _frame(17, "   .-----.       ", "  /  o o  \\      ", " |    ^    |      ", "  \\  ---  /      "),
)

M15_FRAMES = (
    _frame(19, "__..__..__..__..__", "  / / / / / / /   ", "   \\      \\      ", "==================="),
    _frame(19, "__..__..__..__..__", "   / / / / / / /  ", "   \\      \\      ", "==================="),
    _frame(19, "__..__..__..__..__", "    / / / / / / / ", "   \\      \\      ", "==================="),
    _frame(19, "__  __  __  __  __", "    / / / / / / / ", "   \\      \\      ", "==================="),
    _frame(19, "__  __  __  __  __", "     / / / / / / /", "   \\      \\      ", "==================="),
    _frame(19, "__  __  __  __  __", "     /   /   /   /", "   \\      \\      ", "==================="),
    _frame(19, "__..__..__..__..__", "     /   /   /   /", "   \\      \\      ", "==================="),
    _frame(19, "__..__..__..__..__", "  / / / / / / /   ", "   \\      \\      ", "==================="),
)

M16_FRAMES = (
    _frame(19, "F01  .-.         ", "     / o \\      ", "     `-'         ", "T08  8fps        ", "A0   KEY POSE    "),
    _frame(19, "F02  .-.         ", "     / o \\      ", "     `-'         ", "T08  8fps        ", "A0   KEY POSE    "),
    _frame(19, "F03  .-.         ", "     / O \\      ", "     `-'         ", "T08  8fps        ", "A1   EXTREME     "),
    _frame(19, "F04  .-.         ", "     / O \\      ", "     `-'         ", "T08  8fps        ", "A1   BREAKDOWN   "),
    _frame(19, "F05  .-.         ", "     / * \\      ", "     `-'         ", "T08  8fps        ", "A2   IN-BETWEEN  "),
    _frame(19, "F06  .-.         ", "     / O \\      ", "     `-'         ", "T08  8fps        ", "A2   IN-BETWEEN  "),
    _frame(19, "F07  .-.         ", "     / o \\      ", "     `-'         ", "T08  8fps        ", "A3   HOLD        "),
    _frame(19, "F08  .-.         ", "     / o \\      ", "     `-'         ", "T08  8fps        ", "A3   SETTLE      "),
)

M17_FRAMES = (
    _frame(19, "  .---.  ..  .. ", " / o o \\  ::   ", "|   ^   |  ..   "),
    _frame(19, " .---.   ..  .. ", "/ o o \\   ::   ", "|   ^   |  ..   "),
    _frame(19, ".---.    ..  .. ", "o o \\    ::   ", "| ^ |    ..   "),
    _frame(19, " .---.   ..  .. ", "/ O o \\   ::   ", "|   ^   |  ..   "),
    _frame(19, "  .---.  ..  .. ", " / O O \\  ::   ", "|   ^   |  ..   "),
    _frame(19, " .---.   ..  .. ", "/ O O \\   !:   ", "|   ^   |  ..   "),
    _frame(19, "  .---.  ..  .. ", " / O o \\  !:   ", "|   ^   |  ..   "),
    _frame(19, "  .---.  ..  .. ", " / o o \\  ::   ", "|   ^   |  ..   "),
)

M18_FRAMES = (
    _frame(17, "  >--o          ", "    /|          ", "   / |          ", "  /__|====      "),
    _frame(17, "   >-o          ", "    /|          ", "   / |          ", "  /__|===       "),
    _frame(17, "    >o          ", "    /|          ", "   / |          ", "  /__|==        "),
    _frame(17, "     o          ", "    /|          ", "   / |          ", "  /__|=         "),
    _frame(17, "     o<         ", "    |\\         ", "    | \\        ", "====|__\\       "),
    _frame(17, "     o          ", "    |\\         ", "    | \\        ", "  ==|__\\       "),
    _frame(17, "    o<          ", "    |\\         ", "    | \\        ", "   ===|__\\     "),
    _frame(17, "   o<           ", "    |\\         ", "    | \\        ", "    ====|__\\   "),
)


_COMMON = {
    "M0": dict(title="Fireworks radial loop", subject="radial firework ignition, bloom, dissipation, and settle", width=15, frames=M0_FRAMES, anchor={"name": "core", "row": 3, "column": 8}, key_poses=[{"frame": 0, "name": "launch", "decision": "single dim core with registered rays"}, {"frame": 2, "name": "brighten", "decision": "core changes before rays spread"}, {"frame": 4, "name": "bloom", "decision": "asymmetric particles widen the burst"}, {"frame": 6, "name": "dissipation", "decision": "particles collapse toward the registered core"}, {"frame": 7, "name": "settle", "decision": "same shell, one bounded core edit"}], fps=8, holds=[], pacing="Name the core anchor, copy the complete five-row frame, then preview launch → bloom → dissipation → settle.", source_ref="ascii-art-authoring §§1,9-10; curriculum M0 A1/V0", stages=("S0", "A1")),
    "M11": dict(title="Missile fixed-width redraw", subject="moving replace-mode roof, hull, trails, undo redraw, and recovery", width=19, frames=M11_FRAMES, anchor={"name": "nose", "row": 3, "column": 16}, key_poses=[{"frame": 0, "name": "idle", "decision": "hull and nose are fixed"}, {"frame": 2, "name": "travel", "decision": "roof and hull translate together"}, {"frame": 4, "name": "trail", "decision": "virtual-column motion blur stays aligned"}, {"frame": 5, "name": "undo-redraw", "decision": "undo and redo recover the moving hull"}, {"frame": 7, "name": "recovered", "decision": "stable hull closes the registered path"}], fps=8, holds=[], pacing="Mark the nose, redraw the moving roof in place, add aligned virtual trails, undo and redo the redraw, then settle.", source_ref="ascii-art-authoring §§4.4,9h-10; curriculum M11 S0/V11", stages=("S0", "A3")),
    "M1": dict(title="Acronian wing joint", subject="wing opening, feather joint, and hand-mirrored close", width=17, frames=M1_FRAMES, anchor={"name": "body_axis", "row": 6, "column": 9}, key_poses=[{"frame": 0, "name": "closed", "decision": "feathers meet the axis"}, {"frame": 3, "name": "open", "decision": "wing endpoint travels left"}, {"frame": 4, "name": "joint", "decision": "colon is a deliberate mid-height seam"}, {"frame": 7, "name": "close", "decision": "hand-mirrored spelling returns"}], fps=8, holds=[], pacing="Land on the joint, overwrite one glyph, compare the opposite wing by eye, and keep the body axis fixed.", source_ref="ascii-art-authoring §§4.4,4.7; curriculum M1 S1/V1", stages=("S1",)),
    "M19": dict(title="Mirror key-pose bounce", subject="full-body squash, flight, contact bounce, and hand-mirrored settle", width=19, frames=M19_FRAMES, anchor={"name": "ground_baseline", "row": 7, "column": 8}, key_poses=[{"frame": 0, "name": "contact", "decision": "feet and shadow register on the ground"}, {"frame": 1, "name": "squash", "decision": "body compresses before takeoff"}, {"frame": 3, "name": "apex", "decision": "whole body rises while ground stays fixed"}, {"frame": 5, "name": "impact", "decision": "contact squash returns on landing"}, {"frame": 6, "name": "rebound", "decision": "body overshoots with a mirrored lean"}, {"frame": 7, "name": "settle", "decision": "registered silhouette closes the bounce"}], fps=6, holds=[], pacing="Register the ground, compress the complete body, move it through flight and contact, then compare the mirrored rebound before settling.", source_ref="ascii-art-authoring §§4.4,4.7.7,9-10; curriculum M19 S2/V19", stages=("S2",)),
    "M2": dict(title="Face focus", subject="whole-body nod with eye focus, blink, and changing support", width=17, frames=M2_FRAMES, anchor={"name": "left_eye", "row": 2, "column": 7}, key_poses=[{"frame": 0, "name": "rest", "decision": "contour, shoulders, and mouth register"}, {"frame": 2, "name": "focus", "decision": "both eyes open while arms lift"}, {"frame": 3, "name": "lean", "decision": "head and support travel together"}, {"frame": 4, "name": "blink-squash", "decision": "body compresses around the blink"}, {"frame": 7, "name": "return", "decision": "same shell and baseline"}], fps=8, holds=[], pacing="Search the eye landmark, redraw the complete support pose, and preview the nod, lean, blink, and return as one body.", source_ref="ascii-art-authoring §§2,4.6,9-10; curriculum M2 S3/V2", stages=("S3",)),
    "M3": dict(title="Pose copy", subject="whole-pose copy with travelling stance, lean, and one acting feature", width=15, frames=M3_FRAMES, anchor={"name": "feet_baseline", "row": 6, "column": 8}, key_poses=[{"frame": 0, "name": "primary", "decision": "approved six-row key pose"}, {"frame": 2, "name": "step", "decision": "support leg travels with the copied body"}, {"frame": 3, "name": "lean", "decision": "head, torso, and foot share the lean"}, {"frame": 4, "name": "accent", "decision": "acting eye follows the body"}, {"frame": 7, "name": "settle", "decision": "copied body is still registered"}], fps=8, holds=[], pacing="Copy all six rows as one object, move the stance and lean with it, alter the acting feature, then inspect temporal coherence.", source_ref="ascii-art-authoring §§9c-9f,9-10; curriculum M3 A2/V3", stages=("A2",)),
    "M4": dict(title="Rotation tween", subject="two-cell prop rotating around a fixed pivot", width=17, frames=M4_FRAMES, anchor={"name": "pivot", "row": 3, "column": 7}, key_poses=[{"frame": 0, "name": "back extreme", "decision": "prop points back"}, {"frame": 2, "name": "vertical midpoint", "decision": "pivot is unchanged"}, {"frame": 4, "name": "front extreme", "decision": "prop points forward"}, {"frame": 7, "name": "return", "decision": "same pivot and baseline"}], fps=8, holds=[], pacing="Author both extremes around the plus pivot, then insert the vertical midpoint and compare the arc.", source_ref="ascii-art-authoring §§4.4,9f-9g; curriculum M4 A2/V4", stages=("A2",)),
    "M5": dict(title="Layered scene", subject="foreground blade swing with negative-space background seam", width=21, frames=M5_FRAMES, anchor={"name": "ground_registration", "row": 7, "column": 1}, key_poses=[{"frame": 0, "name": "left swing", "decision": "background texture is behind blade"}, {"frame": 3, "name": "contact", "decision": "covered stroke is erased"}, {"frame": 6, "name": "right swing", "decision": "foreground silhouette stays intact"}, {"frame": 7, "name": "loop", "decision": "seam remains clear"}], fps=6, holds=[], pacing="Keep background and foreground layers visible as separate objects; erase only false seams while the blade moves.", source_ref="ascii-art-authoring §§3,11; curriculum M5 S6/V5", stages=("S6", "A3")),
    "M6": dict(title="Pyramid build", subject="subtractive pyramid build and playback reorder", width=15, frames=M6_FRAMES, anchor={"name": "ground_bar", "row": 5, "column": 8}, key_poses=[{"frame": 0, "name": "finished", "decision": "drawn keyframe first"}, {"frame": 2, "name": "upper erase", "decision": "blank a unit, keep row"}, {"frame": 5, "name": "base only", "decision": "subtractive authoring"}, {"frame": 7, "name": "playback start", "decision": "reordered without height drift"}], fps=8, holds=[], pacing="Start at the finished keyframe, subtract one bounded unit per frame, then reorder into forward playback.", source_ref="ascii-art-authoring §10 subtractive animation; curriculum M6 A5/V6", stages=("A5",)),
    "M7": dict(title="Timed build", subject="anticipatory hold before scoped completion replacements", width=15, frames=M7_FRAMES, anchor={"name": "ground", "row": 5, "column": 8}, key_poses=[{"frame": 0, "name": "incomplete", "decision": "unfinished state reads"}, {"frame": 1, "name": "anticipation hold", "decision": "intentional repeated frame"}, {"frame": 3, "name": "completion", "decision": "one scoped completion mark changes"}, {"frame": 7, "name": "settle", "decision": "no accidental duplicate"}], fps=8, holds=[1,5], pacing="Name why each hold exists, repeat each bounded replacement on its held copy, then make the completion and settle edits without deleting rows.", source_ref="ascii-art-authoring §10 timing; curriculum M7 A4/V7", stages=("A4",)),
    "M8": dict(title="Walk study", subject="alternating foot contacts with a lagging arm", width=15, frames=M8_FRAMES, anchor={"name": "torso_axis", "row": 3, "column": 7}, key_poses=[{"frame": 0, "name": "contact left", "decision": "left foot plants"}, {"frame": 2, "name": "passing", "decision": "torso crosses the support"}, {"frame": 4, "name": "contact right", "decision": "right foot plants"}, {"frame": 7, "name": "loop", "decision": "arm lags and catches up"}], fps=8, holds=[], pacing="Track the planted contact cell across the loop, then let the arm arrive on a different frame.", source_ref="ascii-art-authoring §§9g-10; curriculum M8 A7/V8", stages=("A7",)),
    "M9": dict(title="Original bounce capstone", subject="ball fall, squash, rebound, overshoot, and settle", width=15, frames=M9_FRAMES, anchor={"name": "ground", "row": 5, "column": 8}, key_poses=[{"frame": 0, "name": "high", "decision": "planned high extreme"}, {"frame": 2, "name": "fall", "decision": "midpoint approaches ground"}, {"frame": 3, "name": "squash", "decision": "contact changes silhouette"}, {"frame": 6, "name": "overshoot", "decision": "rebound passes rest"}, {"frame": 7, "name": "settle", "decision": "loop seam is readable"}], fps=8, holds=[], pacing="Write the motion and ground anchor first; author extremes, bisect the fall, preview the squash, then polish the seam.", source_ref="ascii-art-authoring §§9-10; curriculum M9 A7/V9", stages=("A7",)),
    "M10": dict(title="SJIS puff tween", subject="proportional lobe, arch, bounded hatch, and settle", width=12, frames=M10_FRAMES, anchor={"name": "lobe_shoulder", "row": 1, "column": 5}, key_poses=[{"frame": 0, "name": "redacted shoulder", "decision": "existing authored ⌒? transcription"}, {"frame": 1, "name": "complete lobe", "decision": "existing ⌒ヽ idiom"}, {"frame": 3, "name": "transfer lobe", "decision": "existing r'⌒ヽ. idiom"}, {"frame": 4, "name": "arch", "decision": "existing ／￣＼ contour"}, {"frame": 6, "name": "bounded hatch", "decision": "existing impact transcription"}, {"frame": 7, "name": "settle", "decision": "existing lobe returns"}], fps=6, holds=[5], pacing="Transcribe exact UTF-8 first; judge the lobe, arch, and hatch in native Saitamaar metrics, never terminal columns.", source_ref="sjis_corpus_findings.v1.json; curriculum M10 P/V10; ascii-art-authoring §§15.3-15.7", stages=("P",), medium="proportional-sjis", extra_provenance={"font": "Saitamaar.ttf", "font_size_px": 16, "line_pitch_px": 17, "space_codepoints": ["U+0020", "U+3000"], "idiom_boundary": "Existing authored M10 idioms only; no new corpus/admission claims."}),
    "M12": dict(title="Joint sweep", subject="staggered bilateral punctuation joints", width=17, frames=M12_FRAMES, anchor={"name": "centre_axis", "row": 3, "column": 9}, key_poses=[{"frame": 0, "name": "left joint", "decision": "one upper joint is active"}, {"frame": 1, "name": "left hit", "decision": "colon becomes bang"}, {"frame": 3, "name": "right stagger", "decision": "lower timing follows later"}, {"frame": 5, "name": "right hit", "decision": "opposite joint activates"}, {"frame": 7, "name": "return", "decision": "shell and axis never moved"}], fps=8, holds=[2,6], pacing="Use visible punctuation landmarks and till motions; stagger the joints before returning to the paired shell.", source_ref="ascii-art-authoring §§4.6,9-10; curriculum M12 S4/V12", stages=("S4", "A4")),
    "M13": dict(title="Texture pulse", subject="WORD-landmark accent travelling across texture clusters", width=19, frames=M13_FRAMES, anchor={"name": "centre_cluster", "row": 1, "column": 10}, key_poses=[{"frame": 0, "name": "centre", "decision": "clusters are separated words"}, {"frame": 2, "name": "centre flash", "decision": "bounded punctuation changes"}, {"frame": 4, "name": "right travel", "decision": "support rows anchor"}, {"frame": 6, "name": "right flash", "decision": "all widths remain fixed"}, {"frame": 7, "name": "exit", "decision": "pulse returns to calm material"}], fps=8, holds=[], pacing="Navigate by WORD landmarks, replace one cluster cell at a time, and inspect support rows after every pulse.", source_ref="ascii-art-authoring §§5,10; curriculum M13 A4/V13", stages=("A4",)),
    "M14": dict(title="Variant palette", subject="registered face variants and named glyph palette", width=17, frames=M14_FRAMES, anchor={"name": "left_eye", "row": 2, "column": 7}, key_poses=[{"frame": 0, "name": "saved palette", "decision": "first face is the source object"}, {"frame": 2, "name": "open variant", "decision": "eye glyph changes in place"}, {"frame": 4, "name": "star variant", "decision": "named palette remains coherent"}, {"frame": 7, "name": "return", "decision": "silhouette never shifts"}], fps=6, holds=[], pacing="Treat each blank-line-separated face as one object; compare palette variants and return without retyping the contour.", source_ref="ascii-art-authoring §§1.7,2,3; curriculum M14 S5/V14", stages=("S5",)),
    "M15": dict(title="Texture ground", subject="dither, one-cell brick offset, shadow, and settle", width=19, frames=M15_FRAMES, anchor={"name": "ground_baseline", "row": 4, "column": 1}, key_poses=[{"frame": 0, "name": "dense ground", "decision": "brick material is coherent"}, {"frame": 2, "name": "offset", "decision": "one-cell indentation"}, {"frame": 4, "name": "lighten", "decision": "erase dither members"}, {"frame": 5, "name": "occluding edge", "decision": "shadow base remains fixed"}, {"frame": 7, "name": "settle", "decision": "material loop closes"}], fps=6, holds=[], pacing="Measure the one-cell offset, erase density instead of swapping material, and keep the angled shadow as a depth anchor.", source_ref="ascii-art-authoring §§3,6,8; curriculum M15 S7/V15", stages=("S7", "A4")),
    "M16": dict(title="Key-pose plan", subject="saved plate, frame labels, timing, and written key-pose plan", width=19, frames=M16_FRAMES, anchor={"name": "frame_label", "row": 1, "column": 2}, key_poses=[{"frame": 0, "name": "plan", "decision": "subject and timing are written"}, {"frame": 2, "name": "extreme", "decision": "approved key pose is named"}, {"frame": 3, "name": "breakdown", "decision": "middle is planned, not guessed"}, {"frame": 4, "name": "in-between", "decision": "F05 states its intent"}, {"frame": 7, "name": "settle", "decision": "plan survives reorder"}], fps=8, holds=[], pacing="Read a saved plate, test the smallest readable pose, then copy explicit plan blocks while incrementing only their labels.", source_ref="ascii-art-authoring §§2,7.1,9; curriculum M16 A0/V16", stages=("A0",)),
    "M17": dict(title="Coherent anchors", subject="unchanged eye material across travelling shell poses", width=19, frames=M17_FRAMES, anchor={"name": "eye_anchor", "row": 2, "column": 5}, key_poses=[{"frame": 0, "name": "registered eye", "decision": "eye is a temporal anchor"}, {"frame": 2, "name": "shell travel", "decision": "body changes, eye stays"}, {"frame": 5, "name": "palette pass", "decision": "homologous eyes change together"}, {"frame": 7, "name": "coherent return", "decision": "anchor returns to source material"}], fps=8, holds=[], pacing="Prove the homologous landmark, repeat only that cell across frames, then inspect for collateral changes before playback.", source_ref="ascii-art-authoring §§7.3,7.4,8.1; curriculum M17 A3/V17", stages=("A3",)),
    "M18": dict(title="Hand-mirrored return", subject="directional mirror, overshoot, turnaround, and reverse reuse", width=17, frames=M18_FRAMES, anchor={"name": "rail_distance", "row": 4, "column": 5}, key_poses=[{"frame": 0, "name": "right action", "decision": "arrow and slash point right"}, {"frame": 3, "name": "contact", "decision": "actor reaches the turnaround"}, {"frame": 4, "name": "left return", "decision": "directional glyphs redrawn by eye"}, {"frame": 5, "name": "turnaround", "decision": "directional change at the turnaround"}, {"frame": 7, "name": "reverse settle", "decision": "approved return is reused in reverse"}], fps=8, holds=[], pacing="Author the mirror as a new still, validate without generating art, then reuse approved frames in reverse around a declared turnaround.", source_ref="ascii-art-authoring §§7.2,7.5,8.2; curriculum M18 A6/V18", stages=("A6",)),
}


MODULE_ANIMATIONS: dict[str, dict[str, Any]] = {
    module_id: _sequence(module_id, **spec) for module_id, spec in _COMMON.items()
}

# Geometry is deliberately explicit rather than inferred from frame hashes.
# It gives the generator/tests semantic guardrails against satisfying the
# eight-frame requirement with a face-only blink or a repeated short flash.
_GEOMETRY = {
    "M0": {"kind": "radial-launch", "moving_regions": ["core", "rays", "particles"], "axes": ["vertical", "radial"], "minimum_changed_rows": 3, "minimum_motion_frames": 6},
    "M11": {"kind": "translated-redraw", "moving_regions": ["roof", "hull", "trail"], "axes": ["horizontal", "vertical"], "minimum_changed_rows": 3, "minimum_motion_frames": 6},
    "M1": {"kind": "wing-joint", "moving_regions": ["wing-endpoints", "feather-joint"], "axes": ["horizontal"], "minimum_changed_rows": 2, "minimum_motion_frames": 5},
    "M19": {"kind": "squash-flight-contact-bounce", "moving_regions": ["whole-body", "shadow", "ground-registration"], "axes": ["vertical", "horizontal", "scale"], "minimum_changed_rows": 4, "minimum_motion_frames": 6, "contact_frames": [0, 1, 5, 7]},
    "M2": {"kind": "whole-body-nod", "moving_regions": ["head", "shoulders", "arms", "mouth"], "axes": ["vertical", "horizontal", "scale"], "minimum_changed_rows": 3, "minimum_motion_frames": 6},
    "M3": {"kind": "whole-pose-copy", "moving_regions": ["head", "torso", "arms", "support-legs"], "axes": ["horizontal", "lean"], "minimum_changed_rows": 3, "minimum_motion_frames": 6},
    "M4": {"kind": "pivot-rotation", "moving_regions": ["upper-arm", "lower-arm"], "axes": ["angular"], "minimum_changed_rows": 3, "minimum_motion_frames": 6},
    "M5": {"kind": "layered-swing", "moving_regions": ["blade", "negative-space-seam", "ground"], "axes": ["angular", "horizontal"], "minimum_changed_rows": 3, "minimum_motion_frames": 6},
    "M6": {"kind": "subtractive-build", "moving_regions": ["pyramid-levels", "spark"], "axes": ["vertical", "scale"], "minimum_changed_rows": 3, "minimum_motion_frames": 6},
    "M7": {"kind": "timed-build", "moving_regions": ["completion-mark", "body", "hold"], "axes": ["scale", "timing"], "minimum_changed_rows": 2, "minimum_motion_frames": 5},
    "M8": {"kind": "walk-cycle", "moving_regions": ["legs", "lagging-arm", "contact"], "axes": ["horizontal", "alternating-contact"], "minimum_changed_rows": 2, "minimum_motion_frames": 6},
    "M9": {"kind": "bounce", "moving_regions": ["ball", "squash-silhouette", "ground"], "axes": ["vertical", "scale"], "minimum_changed_rows": 2, "minimum_motion_frames": 6},
    "M10": {"kind": "proportional-lobe-tween", "moving_regions": ["lobe", "arch", "hatch"], "axes": ["horizontal", "scale"], "minimum_changed_rows": 2, "minimum_motion_frames": 6},
    "M12": {"kind": "staggered-joints", "moving_regions": ["left-joint", "right-joint"], "axes": ["timing"], "minimum_changed_rows": 2, "minimum_motion_frames": 5},
    "M13": {"kind": "texture-pulse", "moving_regions": ["left-cluster", "centre-cluster", "right-cluster"], "axes": ["horizontal"], "minimum_changed_rows": 1, "minimum_motion_frames": 6},
    "M14": {"kind": "palette-variant", "moving_regions": ["eye-palette", "face-shell"], "axes": ["local-glyph"], "minimum_changed_rows": 1, "minimum_motion_frames": 5},
    "M15": {"kind": "texture-ground", "moving_regions": ["dither", "brick-offset", "shadow"], "axes": ["horizontal", "density"], "minimum_changed_rows": 2, "minimum_motion_frames": 5},
    "M16": {"kind": "key-pose-plan", "moving_regions": ["frame-label", "pose-label", "acting-glyph"], "axes": ["label-sequence"], "minimum_changed_rows": 3, "minimum_motion_frames": 6},
    "M17": {"kind": "coherent-shell", "moving_regions": ["shell", "homologous-eye"], "axes": ["horizontal", "local-glyph"], "minimum_changed_rows": 2, "minimum_motion_frames": 5},
    "M18": {"kind": "mirrored-return", "moving_regions": ["actor", "directional-rail", "turnaround"], "axes": ["horizontal", "directional"], "minimum_changed_rows": 3, "minimum_motion_frames": 6},
}
for _module_id, _geometry in _GEOMETRY.items():
    MODULE_ANIMATIONS[_module_id]["geometry"] = deepcopy(_geometry)
    MODULE_ANIMATIONS[_module_id]["trajectory"] = {
        "kind": _geometry["kind"],
        "moving_regions": list(_geometry["moving_regions"]),
        "axes": list(_geometry["axes"]),
        "minimum_changed_rows": _geometry["minimum_changed_rows"],
        "minimum_motion_frames": _geometry["minimum_motion_frames"],
    }


def animation_for(module_id: str) -> dict[str, Any]:
    """Return the canonical animation metadata for ``module_id``.

    A deep copy keeps a generator from accidentally mutating the shared
    catalogue while preserving the stable mapping/API shape.
    """

    try:
        return deepcopy(MODULE_ANIMATIONS[module_id])
    except KeyError as exc:
        raise KeyError(f"unknown animation module: {module_id}") from exc


def _diff_positions(start: tuple[str, ...], target: tuple[str, ...]) -> list[dict[str, Any]]:
    changes = []
    for row, (before, after) in enumerate(zip(start, target), start=1):
        for column, (old, new) in enumerate(zip(before, after), start=1):
            if old != new:
                changes.append({"row": row, "column": column, "from": old, "to": new})
    return changes


def _legacy_endcap_study_contract(module_id: str = "M0") -> dict[str, Any]:
    """Return an 8+ frame bounded-edit contract for a generator owner.

    M0's first and last frames differ only at the named core cell.  Its recipe
    is therefore executable in a clean Neovim instance and demonstrates the
    intended endcap: a known edit on the full registered frame, not a passive
    reward animation.  Other modules expose the same complete frame slices and
    a conservative row-scoped Ex recipe for a generator to specialize.
    """

    animation = MODULE_ANIMATIONS[module_id]
    frames = animation["frames"]
    changes = _diff_positions(frames[0], frames[-1])
    if module_id == "M0":
        expected_recipe = "gg2j0forO"
        recipe_steps = [
            {"keys": "gg2j0f", "purpose": "land on the registered core landmark"},
            {"keys": "rO", "purpose": "overwrite the core without inserting or deleting a cell"},
        ]
        cursor = {"start": {"row": 3, "column": 8}, "target": {"row": 3, "column": 8}, "anchor": "core"}
    else:
        expected_recipe = "copy the complete frame, then apply only the declared changed cells"
        recipe_steps = [
            {"keys": "frame-copy", "purpose": "select the complete registered frame"},
            {"keys": "bounded-overwrite", "purpose": "edit only the listed changed cells"},
        ]
        anchor = animation["anchor"]
        cursor = {
            "start": {"row": anchor["row"], "column": anchor["column"]},
            "target": {"row": anchor["row"], "column": anchor["column"]},
            "anchor": anchor["name"],
        }
    return {
        "module_id": module_id,
        "title": animation["title"],
        "start": list(frames[0]),
        "target": list(frames[-1]),
        "expected_recipe": expected_recipe,
        "recipe_steps": recipe_steps,
        "cursor": cursor,
        "frame_slices": [
            {
                "index": index,
                "label": pose["name"] if (pose := next((p for p in animation["key_poses"] if p["frame"] == index), None)) else f"frame-{index + 1:02d}",
                "rows": list(frame),
                "bounds": dict(animation["bounds"]),
                "anchor": dict(animation["anchor"]),
                "changed_from_start": _diff_positions(frames[0], frame),
            }
            for index, frame in enumerate(frames)
        ],
        "changed_cells": changes,
        "frame_count": len(frames),
        "contract": "bounded-known-neovim-edit-on-full-sequence",
    }


def _contract_edits(animation: dict[str, Any]) -> list[dict[str, Any]]:
    """Resolve semantic edit plans to stable 1-based frame coordinates."""

    module_id = animation["module_id"]
    edits = []
    for frame_index, local_row, old, new in _ENDCAP_EDIT_PLAN[module_id]:
        row = animation["frames"][frame_index][local_row - 1]
        column = row.find(old)
        if column < 0:
            raise ValueError(
                f"{module_id} endcap plan cannot find {old!r} in frame "
                f"{frame_index} row {local_row}"
            )
        edits.append({
            "frame": frame_index,
            "row": local_row,
            "column": column + 1,
            "from": old,
            "to": new,
        })
    # Editing one copy of an intentional hold must also edit its identical
    # neighbours, otherwise the endcap quietly removes the timing beat.
    for edit in list(edits):
        first = last = edit["frame"]
        frames = animation["frames"]
        while first > 0 and frames[first - 1] == frames[edit["frame"]]:
            first -= 1
        while last + 1 < len(frames) and frames[last + 1] == frames[edit["frame"]]:
            last += 1
        for frame_index in range(first, last + 1):
            candidate = dict(edit, frame=frame_index)
            if candidate not in edits:
                edits.append(candidate)
    return edits


def _apply_contract_edits(frames: tuple[tuple[str, ...], ...],
                          edits: list[dict[str, Any]]) -> tuple[tuple[str, ...], ...]:
    mutable = [list(frame) for frame in frames]
    for edit in edits:
        frame = mutable[edit["frame"]]
        row_index = edit["row"] - 1
        column_index = edit["column"] - 1
        if frame[row_index][column_index] != edit["from"]:
            raise ValueError("endcap edit plan drifted from canonical frame")
        row = list(frame[row_index])
        row[column_index] = edit["to"]
        frame[row_index] = "".join(row)
    return tuple(tuple(frame) for frame in mutable)


def _normal_recipe(edits: list[dict[str, Any]], frame_rows: list[int],
                   *, undo_redraw: bool = False) -> str:
    """Build a literal Normal-mode key string from bounded cell edits."""

    offsets = []
    total = 0
    for rows in frame_rows:
        offsets.append(total)
        total += rows
    absolute = sorted(
        (offsets[edit["frame"]] + edit["row"], edit)
        for edit in edits
    )
    keys = "gg0"
    current_row = 1
    for edit_index, (absolute_row, edit) in enumerate(absolute):
        delta = absolute_row - current_row
        if delta > 0:
            keys += "j" if delta == 1 else f"{delta}j"
        elif delta < 0:
            keys += "k" if delta == -1 else f"{-delta}k"
        keys += "0"
        if edit["column"] > 1:
            count = edit["column"] - 1
            keys += "l" if count == 1 else f"{count}l"
        keys += "r" + edit["to"]
        if undo_redraw and edit_index == 0:
            # The first real cell edit creates the history being traversed.
            # Undo/redo before any edit would be a no-op demonstration.
            keys += "u<C-r>"
        current_row = absolute_row
    return keys


def endcap_study_contract(module_id: str = "M0") -> dict[str, Any]:
    """Return the executable full-sequence learner study for one module.

    Start and target are flattened plates, while frame_details retains the
    canonical eight frame boundaries and local pose metadata. Expected is an
    actual Normal-mode key string that the generator can feed directly to the
    isolated Neovim grader.
    """

    animation = MODULE_ANIMATIONS[module_id]
    frames = animation["frames"]
    edits = _contract_edits(animation)
    frame_rows = [len(frame) for frame in frames]
    target_frames = _apply_contract_edits(frames, edits)
    expected = _normal_recipe(edits, frame_rows, undo_redraw=module_id == "M11")
    pose_names = {
        pose["frame"]: pose["name"] for pose in animation.get("key_poses", [])
    }
    frame_details = []
    for index, frame in enumerate(frames):
        frame_details.append({
            "index": index,
            "label": pose_names.get(index, f"frame-{index + 1:02d}"),
            "rows": list(frame),
            "bounds": dict(animation["bounds"]),
            "anchor": dict(animation["anchor"]),
            "changed_from_start": _diff_positions(frames[0], frame),
        })
    absolute_changes = []
    offsets = []
    offset = 0
    for count in frame_rows:
        offsets.append(offset)
        offset += count
    for edit in edits:
        absolute_changes.append({
            **edit,
            "absolute_row": offsets[edit["frame"]] + edit["row"],
        })
    holds = animation["interval"].get("holds", [])
    hold = (
        "Intentional hold at frame(s) %s; the repeated pose is a timing beat, not padding."
        % ", ".join(str(index + 1) for index in holds)
        if holds else
        "No repeated hold; every registered pose advances the declared motion."
    )
    key_pose = "; ".join(
        "F%02d %s" % (pose["frame"] + 1, pose["name"])
        for pose in animation.get("key_poses", [])
    )
    timing = (
        "%s fps over %.3fs; %s"
        % (animation["interval"]["fps"], animation["interval"]["duration_seconds"],
           animation["interval"]["tutorial_pacing"])
    )
    # Positioning is a worked example, not another required transcript.
    known = ["r" + edits[0]["to"]]
    if module_id == "M11":
        known = ["u", "<C-r>", *known]
    return {
        "module_id": module_id,
        "title": animation["title"],
        "subject": animation["subject"],
        "start": [row for frame in frames for row in frame],
        "target": [row for frame in target_frames for row in frame],
        "expected": expected,
        "expected_recipe": expected,
        "recipe_steps": [
            {"keys": "gg0", "purpose": "start in Normal mode at the registered sequence origin"},
            {"keys": "j/0/l/r", "purpose": "overwrite the four declared bounded cells across separate meaningful poses"},
        ],
        "cursor": "gg0",
        "frame_slices": frame_rows,
        "frame_details": frame_details,
        "changed_cells": absolute_changes,
        "frame_count": len(frames),
        "key_pose": key_pose,
        "timing": timing,
        "hold": hold,
        "known_taught_commands": known,
        "geometry": deepcopy(animation["geometry"]),
        "contract": "bounded-known-neovim-edit-on-full-sequence",
    }


_ENDCAP_EDIT_PLAN = {
    "M0": [(0, 3, "o", "O"), (1, 3, "o", "O"), (3, 1, ".", "*"), (6, 1, ".", "*")],
    "M11": [(0, 3, "o", "O"), (2, 2, "/", "="), (4, 5, ".", "*"), (7, 3, "O", "!")],
    "M1": [(0, 2, "o", "O"), (2, 3, "\\", ":"), (4, 3, "|", "!"), (7, 1, "-", "*")],
    "M19": [(0, 2, "o", "O"), (1, 3, "^", "*"), (3, 5, "-", "="), (5, 5, "_", "-")],
    "M2": [(0, 2, "o", "O"), (2, 4, "/", "\\"), (3, 2, "O", "*"), (4, 3, "^", "-")],
    "M3": [(0, 2, "o", "O"), (2, 5, "/", "\\"), (3, 4, "|", "!"), (4, 2, "*", "o")],
    "M4": [(0, 3, "+", "*"), (2, 1, "|", "!"), (4, 4, "\\", "/"), (7, 5, "/", "\\")],
    "M5": [(0, 3, "\\", "|"), (3, 4, "+", "*"), (6, 3, "/", "|"), (7, 6, ".", ":")],
    "M6": [(0, 1, ".", "*"), (3, 3, ".", "*"), (5, 4, "_", "="), (7, 1, "o", "O")],
    "M7": [(0, 1, ".", "*"), (3, 2, "|", "!"), (4, 3, "_", "="), (7, 3, "_", "-")],
    "M8": [(0, 1, "o", "O"), (2, 4, "_", "="), (4, 2, "|", "!"), (7, 5, "_", "-")],
    "M9": [(0, 1, "o", "O"), (3, 2, "_", "="), (6, 1, "O", "*"), (7, 3, ".", "!")],
    "M10": [(0, 1, "?", "!"), (2, 1, "?", "!"), (4, 1, "＼", "／"), (6, 2, "ニ", "二")],
    "M12": [(0, 1, ":", "*"), (3, 1, "!", "."), (5, 1, "-", "="), (7, 3, "O", "*")],
    "M13": [(0, 1, ".", ":"), (2, 1, "!", ":"), (4, 1, "!", "+"), (6, 1, "!", "*")],
    "M14": [(0, 2, "o", "*"), (2, 2, "O", "!"), (4, 2, "*", "o"), (7, 3, "^", "+")],
    "M15": [(0, 1, ".", ":"), (2, 1, ".", "+"), (4, 2, "/", "|"), (7, 3, "\\", "/")],
    "M16": [(0, 1, "1", "9"), (2, 1, "3", "4"), (4, 2, "/", "\\"), (7, 5, "A", "B")],
    "M17": [(0, 2, "o", "O"), (2, 2, "o", "*"), (4, 2, "O", "o"), (6, 2, "O", "*")],
    "M18": [(0, 1, "o", "O"), (2, 1, "o", "*"), (4, 1, "o", "O"), (7, 4, "=", "-")],
}

__all__ = ["MODULE_ANIMATIONS", "animation_for", "endcap_study_contract"]
