#!/usr/bin/env python3
"""Structural and clean-Neovim tests for the canonical module animations."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile

from module_animations import MODULE_ANIMATIONS, animation_for, endcap_study_contract
import v2_runtime


MODULE_IDS = [f"M{index}" for index in range(20)]


def check_catalogue() -> list[str]:
    errors: list[str] = []
    if set(MODULE_ANIMATIONS) != set(MODULE_IDS):
        errors.append(f"catalogue ids mismatch: {sorted(MODULE_ANIMATIONS)}")
    for module_id in MODULE_IDS:
        animation = MODULE_ANIMATIONS.get(module_id)
        if animation is None:
            continue
        frames = animation.get("frames", ())
        bounds = animation.get("bounds", {})
        if len(frames) < 8:
            errors.append(f"{module_id}: fewer than eight frames")
        if len(set(frames)) < 6:
            errors.append(f"{module_id}: fewer than six distinct meaningful poses")
        if not frames:
            errors.append(f"{module_id}: no frames")
            continue
        rows = len(frames[0])
        columns = bounds.get("columns")
        if bounds.get("rows") != rows or not columns:
            errors.append(f"{module_id}: bounds do not describe frame rows")
        anchor = animation.get("anchor", {})
        if not (1 <= anchor.get("row", 0) <= rows and 1 <= anchor.get("column", 0) <= columns):
            errors.append(f"{module_id}: anchor falls outside the registered frame box")
        for index, frame in enumerate(frames):
            if len(frame) != rows:
                errors.append(f"{module_id}: frame {index} has unequal height")
            if any(len(row) != columns for row in frame):
                errors.append(f"{module_id}: frame {index} has unequal width")
        if not animation.get("title") or not animation.get("credit"):
            errors.append(f"{module_id}: missing title or original credit")
        provenance = animation.get("provenance", {})
        if provenance.get("kind") != "original-authored":
            errors.append(f"{module_id}: provenance is not original-authored")
        if animation.get("rights_gate", {}).get("source_frames_imported"):
            errors.append(f"{module_id}: source frame import is enabled")
        interval = animation.get("interval", {})
        for field in ("fps", "duration_seconds", "tutorial_pacing"):
            if not interval.get(field):
                errors.append(f"{module_id}: interval missing {field}")
        repeated = [index for index in range(1, len(frames)) if frames[index] == frames[index - 1]]
        if interval.get("holds") != repeated:
            errors.append(f"{module_id}: hold claims do not match actual repeated poses")
        if len(animation.get("key_poses", [])) < 3:
            errors.append(f"{module_id}: key-pose metadata is too thin")
        geometry = animation.get("geometry", {})
        trajectory = animation.get("trajectory", {})
        for field in ("kind", "moving_regions", "axes", "minimum_changed_rows", "minimum_motion_frames"):
            if not geometry.get(field):
                errors.append(f"{module_id}: geometry missing {field}")
        if trajectory.get("kind") != geometry.get("kind"):
            errors.append(f"{module_id}: trajectory does not mirror geometry kind")
        changed_rows = set()
        motion_frames = 0
        for before, after in zip(frames, frames[1:]):
            rows = {row for row, (left, right) in enumerate(zip(before, after), 1) if left != right}
            changed_rows.update(rows)
            motion_frames += bool(rows)
        if len(changed_rows) < geometry.get("minimum_changed_rows", 0):
            errors.append(f"{module_id}: semantic geometry has too few moving rows")
        if motion_frames < geometry.get("minimum_motion_frames", 0):
            errors.append(f"{module_id}: semantic geometry has too few motion transitions")

    m10 = MODULE_ANIMATIONS["M10"]
    if m10["medium"] != "proportional-sjis":
        errors.append("M10: wrong medium")
    if m10["bounds"]["metric"] != "Saitamaar codepoint/advance audit":
        errors.append("M10: missing native Saitamaar metric declaration")
    if m10["provenance"].get("space_codepoints") != ["U+0020", "U+3000"]:
        errors.append("M10: U+0020/U+3000 preservation metadata missing")
    if "no new corpus/admission claims" not in m10["provenance"].get("idiom_boundary", ""):
        errors.append("M10: corpus/admission boundary missing")
    # A repeated ASCII half-space would violate the proportional authoring
    # whitespace law. Full-width U+3000 spacing and registration padding are
    # intentionally allowed.
    for frame in m10["frames"]:
        for row in frame:
            authored = row.rstrip(" ")
            if "  " in authored:
                errors.append("M10: adjacent U+0020 half spaces introduced")
                break
    return errors


def check_endcap_contract() -> list[str]:
    errors: list[str] = []
    required = {
        "start", "target", "expected", "cursor", "frame_slices",
        "frame_details", "key_pose", "timing", "hold", "known_taught_commands",
    }
    for module_id in MODULE_IDS:
        contract = endcap_study_contract(module_id)
        missing = required - set(contract)
        if missing:
            errors.append(f"{module_id} endcap missing fields: {sorted(missing)}")
            continue
        animation = animation_for(module_id)
        expected_start = [row for frame in animation["frames"] for row in frame]
        if contract["start"] != expected_start:
            errors.append(f"{module_id} endcap start is not the flattened canonical sequence")
        if len(contract["frame_slices"]) != 8:
            errors.append(f"{module_id} endcap does not expose eight frame slices")
        if any(not isinstance(size, int) or size < 1 for size in contract["frame_slices"]):
            errors.append(f"{module_id} endcap frame slices are not positive row counts")
        if (sum(contract["frame_slices"]) != len(contract["start"])
                or sum(contract["frame_slices"]) != len(contract["target"])):
            errors.append(f"{module_id} endcap frame slices do not cover both plates")
        if contract["start"] == contract["target"]:
            errors.append(f"{module_id} endcap has no learner-visible edit")
        if not isinstance(contract["expected"], str) or not contract["expected"].strip():
            errors.append(f"{module_id} endcap expected recipe is not a key string")
        if not isinstance(contract["cursor"], str) or not contract["cursor"].strip():
            errors.append(f"{module_id} endcap cursor is not a Normal-mode key string")
        if (not isinstance(contract["known_taught_commands"], list)
                or any(not isinstance(command, str) or not command
                       for command in contract["known_taught_commands"])):
            errors.append(f"{module_id} endcap known commands are incomplete")
        details = contract["frame_details"]
        if len(details) != 8:
            errors.append(f"{module_id} endcap frame_details is not eight frames")
        for index, detail in enumerate(details):
            if detail.get("index") != index:
                errors.append(f"{module_id} frame detail {index} has unstable index")
            if detail.get("rows") != list(animation["frames"][index]):
                errors.append(f"{module_id} frame detail {index} lost canonical text")
            if detail.get("bounds") != animation["bounds"]:
                errors.append(f"{module_id} frame detail {index} lost bounds")
        # Four edits are deliberately distributed over separate poses so the
        # learner changes the sequence rather than a detached reward cell.
        start_frames, target_frames = [], []
        cursor = 0
        for size in contract["frame_slices"]:
            start_frames.append(contract["start"][cursor:cursor + size])
            target_frames.append(contract["target"][cursor:cursor + size])
            cursor += size
        if sum(before != after for before, after in zip(start_frames, target_frames)) < 3:
            errors.append(f"{module_id} endcap edits do not span meaningful poses")
        for index in range(1, len(start_frames)):
            if (start_frames[index] == start_frames[index - 1]) != (target_frames[index] == target_frames[index - 1]):
                errors.append(f"{module_id} endcap changed an intentional hold boundary")
    return errors


def check_c33_semantics() -> list[str]:
    """Protect the four semantic repairs that shape the learner contract."""

    errors: list[str] = []

    # The M0 core is the registration point for the radial study.  A three-star
    # bloom has a centre star; the other poses have one o/O core glyph.
    def core_column(frame: tuple[str, ...]) -> int | None:
        row = frame[2]
        if row.count("*") == 3:
            return row.index("*") + 2
        marks = [index + 1 for index, char in enumerate(row) if char in "oO"]
        return marks[0] if len(marks) == 1 else None

    m0_columns = [core_column(frame) for frame in MODULE_ANIMATIONS["M0"]["frames"]]
    if m0_columns != [8] * 8:
        errors.append(f"M0 core columns drift from the registered centre: {m0_columns}")

    # M18's directional rail is intentionally translated and turned through
    # the turnaround; the content contract must not regress to a fixed rail.
    m18_rails = [
        tuple(index + 1 for index, char in enumerate(frame[3]) if char == "=")
        for frame in MODULE_ANIMATIONS["M18"]["frames"]
    ]
    expected_m18_rails = [
        (7, 8, 9, 10), (7, 8, 9), (7, 8), (7,),
        (1, 2, 3, 4), (3, 4), (4, 5, 6), (5, 6, 7, 8),
    ]
    if m18_rails != expected_m18_rails:
        errors.append(f"M18 rail trajectory changed unexpectedly: {m18_rails}")

    # The M19 ground is the fixed registration baseline.  All eight frames
    # retain it on row 7, including the rebound frame.
    m19_ground_rows = [
        [index + 1 for index, row in enumerate(frame) if "_____________" in row]
        for frame in MODULE_ANIMATIONS["M19"]["frames"]
    ]
    if m19_ground_rows != [[7]] * 8:
        errors.append(f"M19 ground baseline is not fixed on row 7: {m19_ground_rows}")

    # M7 has two repeated holds.  Endcap edits must be copied onto both
    # members of each hold, producing six cell replacements in total.
    m7 = endcap_study_contract("M7")
    if len(m7["changed_cells"]) != 6 or m7["expected"].count("r") != 6:
        errors.append(
            "M7 endcap no longer represents six in-place replacements: "
            f"{len(m7['changed_cells'])} cells / {m7['expected'].count('r')} r commands"
        )
    cursor = 0
    target_frames = []
    for size in m7["frame_slices"]:
        target_frames.append(m7["target"][cursor:cursor + size])
        cursor += size
    for hold in MODULE_ANIMATIONS["M7"]["interval"]["holds"]:
        if target_frames[hold] != target_frames[hold - 1]:
            errors.append(f"M7 held-copy edit diverges at frame index {hold}")

    return errors


def check_clean_neovim_recipe() -> list[str]:
    """Apply every published recipe in isolated clean Neovim."""

    if not shutil_which("nvim"):
        return ["nvim is required for the endcap recipe proof"]
    for module_id in MODULE_IDS:
        contract = endcap_study_contract(module_id)
        ok, evidence, detail = v2_runtime._safe_typed_effect(
            {
                "initial_lines": contract["start"],
                "target_lines": contract["target"],
                "effect_version": 1,
            },
            contract["expected"],
        )
        if not ok:
            return [f"{module_id} clean Neovim recipe failed: {detail} {evidence}"]
    return []


def shutil_which(command: str) -> str | None:
    """Small local which helper; keeps this test dependency-free."""

    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / command
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def check() -> list[str]:
    return (
        check_catalogue()
        + check_endcap_contract()
        + check_c33_semantics()
        + check_clean_neovim_recipe()
    )


def test_catalogue() -> None:
    assert check_catalogue() == []


def test_endcap_contract() -> None:
    assert check_endcap_contract() == []


def test_c33_semantics() -> None:
    assert check_c33_semantics() == []


def test_clean_neovim_recipe() -> None:
    assert check_clean_neovim_recipe() == []


if __name__ == "__main__":
    failures = check()
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)
    print("PASS: M0-M19 canonical animations, bounds, metadata, and clean-Neovim endcap")
