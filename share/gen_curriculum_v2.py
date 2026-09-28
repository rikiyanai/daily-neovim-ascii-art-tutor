#!/usr/bin/env python3
"""Generate the VD-09 v2 project curriculum.

The source below is deliberately ordinary Python rather than hand-escaped JSON.
It owns stable card/question ids; curriculum-v2.json is the installed artifact.
All art here is original, tiny practice scaffolding. Third-party tutorial plates
are cited as method references only and are not copied into this file.
"""

import json
import re
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "curriculum-v2.json"
CATALOG = ROOT / "CURRICULUM_V2_CARD_CATALOG.md"
LEGACY = ROOT / "curriculum.json"

# Every original lesson is attached to the nearest v2 animation card. This is
# teaching-content provenance, not mastery migration: v2 still grades its own
# changed art and method requirements.
LEGACY_CARD_MAP = {
    "move-x": "M9.04", "delete-word": "M2.01", "delete-eol": "M6.05",
    "count-motion": "M2.01", "delete-line": "M7.08", "undo": "M11.04",
    "put": "M0.02", "replace-char": "M0.01", "change-word": "M3.04",
    "change-eol": "M4.01", "search": "M1.01", "match-paren": "M3.01",
    "substitute": "M0.02", "substitute-all": "M7.05", "open-line": "M8.04",
    "append": "M8.04", "yank-put": "M0.02", "join": "M6.04",
    "toggle-case": "M7.05", "text-object-paren": "M3.04",
    "paragraph-object": "M14.05", "named-register": "M3.06",
    "yank-register-0": "M3.06", "marks": "M3.08",
    "visual-delete": "M3.06", "block-insert": "M4.04",
    "block-append": "M15.05", "block-erase": "M4.04",
    "block-replace": "M4.04", "macro": "M7.05",
    "symbol-table": "M14.04", "dot-repeat": "M7.04",
    "find-char": "M7.06", "ex-copy": "M5.05", "hold-frame": "M7.01",
    "tween-frame": "M9.05", "break-seam": "M5.01",
    "playback-order": "M6.08", "range-normal": "M7.05",
    "mirror-run": "M18.01", "pad-frames": "M8.04",
    "macro-frames": "M7.05", "ant-drop": "M7.08",
    "centipede-hold": "M7.01", "cheer-eyes": "M3.04",
    "candle-join": "M6.04",
}

PHASE_TITLES = {
    1: "Foundation edit", 2: "Develop the strip", 3: "Read the motion",
    4: "Independent edit", 5: "Compare editing methods", 6: "Unseen transfer",
    7: "Diagnose the animation", 8: "Module mastery check",
}


def load_catalog_prompts():
    """Load the authored lesson contracts from the human-readable catalog."""
    rows = {}
    pattern = re.compile(r"^\| (M\d+\.\d{2}) \| ([GQXTK]) \| (.*) \|$")
    for line in CATALOG.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            rows[match.group(1)] = match.group(3)
    expected = {f"M{module}.{ordinal:02d}" for module in range(19) for ordinal in range(1, 9)}
    if set(rows) != expected:
        missing = sorted(expected - set(rows))
        extra = sorted(set(rows) - expected)
        raise SystemExit(f"catalog card mismatch: missing={missing} extra={extra}")
    return rows


def step(start, target, expected, recipe, cursor="^", alternatives=None,
         method_requirement=None, review_variants=None, key_vocabulary=None):
    row = {
        "start": start,
        "target": target,
        "expected": expected,
        "recipe": recipe,
        "cursor": cursor,
    }
    if alternatives:
        row["alternatives"] = alternatives
    if method_requirement:
        row["method_requirement"] = method_requirement
    if review_variants:
        row["review_variants"] = review_variants
    if key_vocabulary:
        row["key_vocabulary"] = key_vocabulary
    return row


def method(label, keys, why, evidence=None):
    row = {"label": label, "keys": keys, "why": why}
    if evidence:
        row["evidence"] = evidence
    return row


def require_method(label, any_of=None, max_tokens=None, all_of=None,
                   exact_any_of=None):
    """Declare a method the runtime must observe, rather than merely print."""
    rule = {"label": label}
    if any_of:
        rule["any_of"] = any_of
    if all_of:
        rule["all_of"] = all_of
    if exact_any_of:
        rule["exact_any_of"] = exact_any_of
    if max_tokens is not None:
        rule["max_tokens"] = max_tokens
    return rule


MODULES = [
    {
        "id": "M0", "title": "Spark loop", "node": "A0/V0", "project": "spark-loop",
        "skill": "modes, whole-frame copying, and readable change", "frame_rows": 3,
        "source_ref": "ascii-art-authoring §§1,9; Neovim tutor 1.1-1.6",
        "meaning": "a registered three-row spark brightens into a wider flare, holds, then settles",
        "first_reading": "the core changes from a placeholder point to a dim spark while every ray stays registered",
        "principle": "test the smallest readable multi-row subject before adding frames",
        "defect": "only the centre glyph changes while the surrounding rays drift or a duplicate has no timing purpose",
        "basic": "find and replace one feature inside a readable three-row frame",
        "scaled": "duplicate the complete three-row frame before changing only the copy",
        "steps": [
            step(
                ["  \\|/  ", "-- . --", "  /|\\  "],
                ["  \\|/  ", "-- o --", "  /|\\  "],
                "j0f.ro",
                [["j", "move to the acting row"],
                 ["f.", "find the visible placeholder without padding the path with unused word motions"],
                 ["ro", "replace only the core while keeping all six rays registered"]],
                method_requirement=require_method(
                    "find the visible core, then replace it in place",
                    exact_any_of=["j0f.ro"]),
                review_variants=[
                    step(["  /|\\  ", "== ? ==", "  \\|/  "],
                         ["  /|\\  ", "== * ==", "  \\|/  "],
                         "j0f?r*", [["j0f?r*", "find and replace the changed core in place"]],
                         method_requirement=require_method(
                             "find the changed core, then replace it in place",
                             exact_any_of=["j0f?r*"])),
                    step(["  \\!/  ", "-- x --", "  /!\\  "],
                         ["  \\!/  ", "-- O --", "  /!\\  "],
                         "j0fxrO", [["j0fxrO", "find and replace the alternate core in place"]],
                         method_requirement=require_method(
                             "find the alternate core, then replace it in place",
                             exact_any_of=["j0fxrO"])),
                ],
            ),
            step(
                ["  \\|/  ", "-- o --", "  /|\\  "],
                ["  \\|/  ", "-- o --", "  /|\\  ",
                 "  \\|/  ", "-- O --", "  /|\\  "],
                "gg3yyGp:4,6s/o/O/g<CR>",
                [["gg3yy", "copy the complete three-row dim keyframe"],
                 ["Gp", "put the copy after the original"],
                 [":4,6s/o/O/g", "on rows 4 through 6 substitute O for every o; only the copied core matches, and g means every match on each addressed row"]],
                key_vocabulary=[
                    "{count}yy then p/P — yank complete frame rows and put them below/above",
                    ":{start},{end}s/old/new/g — across addressed rows replace every match; g means all matches per row",
                ],
            ),
            step(
                ["  \\|/  ", "-- o --", "  /|\\  ",
                 "  \\|/  ", "-- O --", "  /|\\  "],
                ["  \\|/  ", "-- o --", "  /|\\  ",
                 "  \\|/  ", "-- O --", "  /|\\  ",
                 "  \\|/  ", "== O ==", "  /|\\  "],
                "4G3yyGp:8s/-/=/g<CR>",
                [["4G3yyGp", "copy the bright three-row keyframe as the flare extreme"],
                 [":8s/-/=/g", "widen only the new frame's horizontal rays"]],
                key_vocabulary=[
                    "{count}yy then p/P — yank complete frame rows and put them below/above",
                    ":{start},{end}s/old/new/g — across addressed rows replace every match; a one-line address is the bounded form",
                ],
            ),
            step(
                ["  \\|/  ", "-- o --", "  /|\\  ",
                 "  \\|/  ", "-- O --", "  /|\\  ",
                 "  \\|/  ", "== O ==", "  /|\\  "],
                ["  \\|/  ", "-- o --", "  /|\\  ",
                 "  \\|/  ", "-- O --", "  /|\\  ",
                 "  \\|/  ", "== O ==", "  /|\\  ",
                 "  \\|/  ", "== O ==", "  /|\\  "],
                ":7,9t$<CR>",
                [[":7,9t$", "copy the whole flare extreme to create a deliberate two-frame hold"]], alternatives=[
                method("counted yank and put", "7G3yyGp", "copy the three-row flare from its first row",
                       {"kind": "linewise_yank_put", "rows": 3}),
                method("addressed copy", ":7,9t$<CR>", "copy the exact flare range without relying on cursor position",
                       {"kind": "ex_copy", "start": 7, "end": 9, "destination": "$"}),
            ]),
            step(
                ["  \\|/  ", "-- o --", "  /|\\  ",
                 "  \\|/  ", "-- O --", "  /|\\  ",
                 "  \\|/  ", "== O ==", "  /|\\  ",
                 "  \\|/  ", "== O ==", "  /|\\  "],
                ["  \\|/  ", "-- o --", "  /|\\  ",
                 "  \\|/  ", "-- O --", "  /|\\  ",
                 "  \\|/  ", "== O ==", "  /|\\  ",
                 "  \\|/  ", "== O ==", "  /|\\  ",
                 "  \\|/  ", "-- . --", "  /|\\  "],
                ":1,3t$<CR>14Gfor.",
                [[":1,3t$", "copy the registered dim frame as a settle scaffold"],
                 ["14Gfor.", "lower only the settle core so the loop seam is a transition, not a dead duplicate"]],
            ),
        ],
        "transfer": step(
            ["  /|   ", "< o >--", "  \\|   "],
            ["  /|   ", "< O >==", "  \\|   "],
            "jforO:s/-/=/g<CR>",
            [["jforO", "brighten the unfamiliar comet core"],
             [":s/-/=/g", "widen only its tail rays"]],
        ),
        "transfer_alt": step(
            ["   |\\  ", "--< o >", "   |/  "],
            ["   |\\  ", "==< O >", "   |/  "],
            "jforO:s/-/=/g<CR>",
            [["jforO", "brighten the mirrored comet core"],
             [":s/-/=/g", "widen only the changed tail"]],
        ),
        "migration_starts": {
            4: [[" · ", " o "], [" · ", " · "]],
        },
    },
    {
        "id": "M1", "title": "Contour run", "node": "A1/V1", "project": "line-run",
        "skill": "glyph geometry, shallow curves, and precise landmarks", "frame_rows": 3,
        "source_ref": "ascii-art-authoring §§4.4,4.7; Neovim tutor 2.1,2.4,4.2",
        "meaning": "an anchored shallow contour rises and falls without moving its endpoint",
        "first_reading": "the uncertain comma joint becomes the chosen colon joint while the contour and anchor stay fixed",
        "principle": "reuse one memorised slope vocabulary across every frame",
        "defect": "the endpoint or material spelling shifts when only the contour angle should change",
        "basic": "reach a visible joint with f and replace only that joint",
        "scaled": "use a bounded substitute or dot repeat for the same joint in several complete frames",
        "steps": [
            step(
                ["       ´", "    _., ", "o_.-    "],
                ["       ´", "    _.: ", "o_.-    "],
                "/,<CR>r:",
                [["/,", "search forward for the uncertain joint instead of counting columns"],
                 ["<CR>", "accept the match inside the full contour"],
                 ["r:", "choose the middle-height joint while leaving its anchor fixed"]],
            ),
            step(
                ["       ´", "    _.: ", "o_.-    "],
                ["       ´", "    _.: ", "o_.-    ",
                 "       ´", "    _.: ", "o_.-    "],
                "gg3yyGp",
                [["gg3yy", "copy the complete three-row contour frame"],
                 ["Gp", "put the working copy after the approved frame"]],
            ),
            step(
                ["       ´", "    _.: ", "o_.-    ",
                 "       ´", "    _.: ", "o_.-    "],
                ["       ´", "    _.: ", "o_.-    ",
                 "´       ", " `-.:   ", "o_.-    "],
                "4G3ddGo´<CR> `-.:<CR><C-u>o_.-<Esc>",
                [["4G3ddGo", "remove only the copied frame and open its replacement"],
                 ["´ / `-.: / o_.-", "hand-author the opposite contour while keeping the o anchor fixed"]],
            ),
            step(
                ["       ´", "    _.: ", "o_.-    ",
                 "´       ", " `-.:   ", "o_.-    "],
                ["       ´", "    _.; ", "o_.-    ",
                 "´       ", " `-.;   ", "o_.-    "],
                ":%s/:/;/g<CR>",
                [[":%s/:/;/g", "change the declared joint material in both complete frames"]], alternatives=[
                method("local plus dot", "2G0f:r;3j0f:.", "edit the first joint and repeat that change at the second"),
                method("bounded substitute", ":%s/:/;/g<CR>", "replace only the known joint glyph throughout this two-frame strip"),
            ]),
            step(
                ["       ´", "    _.; ", "o_.-    ",
                 "´       ", " `-.;   ", "o_.-    "],
                ["       ´", "    _.; ", "o_.-    ",
                 "´       ", " `-.;   ", "o_.-    ",
                 "       ´", "    _.: ", "o_.-    "],
                ":1,3t$<CR>8G0f;r:",
                [[":1,3t$", "copy the registered rising contour as the settle scaffold"],
                 ["8G0f;r:", "soften only the settle joint so the loop seam is not a dead duplicate"]],
            ),
        ],
        "transfer": step(
            ["      _.´", "   _.-   ", "o_.,     "],
            ["      _.´", "   _.-   ", "o_.:     "],
            "G0f,r:",
            [["G0f,", "find the uncertain joint in an unfamiliar anchored contour"],
             ["r:", "apply the same material vocabulary without moving the endpoint"]],
        ),
        "transfer_alt": step(
            ["´._      ", "   `-._  ", "     ,._o"],
            ["´._      ", "   `-._  ", "     :._o"],
            "G0f,r:",
            [["G0f,", "find the corresponding joint in the mirrored contour"],
             ["r:", "use the same declared joint glyph"]],
        ),
    },
    {
        "id": "M2", "title": "Face focus", "node": "A1/V2", "project": "shape-edit",
        "skill": "operator/motion grammar inside a stable contour", "frame_rows": 4,
        "labels_steps": [1],
        "source_ref": "ascii-art-authoring §§2,4.6; Neovim tutor 2.1-3.4",
        "meaning": "a four-row face changes focus and blinks while its silhouette stays registered",
        "first_reading": "the annotation disappears, but all four rows of the face remain unchanged",
        "principle": "make an operator no larger than the facial feature it is meant to change",
        "defect": "a command consumes the mouth or contour when only the eye should change",
        "basic": "find the eye and replace one glyph with r",
        "scaled": "use a narrowly matched substitute only when several frames need the same facial edit",
        "steps": [
            step(
                [" /---\\", "|  .  |  note", "| \\_/ |", " \\___/"],
                [" /---\\", "|  .  |", "| \\_/ |", " \\___/"],
                "/note<CR>daw",
                [["/note", "search for the annotation instead of navigating by a memorised column"],
                 ["<CR>", "land on the annotation word"],
                 ["daw", "delete the annotation text object together with its separating space"]],
            ),
            step(
                [" /---\\", "|  .  |", "| \\_/ |", " \\___/"],
                [" /---\\", "|  .  |", "| \\_/ |", " \\___/",
                 " /---\\", "|  .  |", "| \\_/ |", " \\___/"],
                "gg4yyGp",
                [["gg4yy", "copy the complete four-row face"],
                 ["Gp", "put the new acting frame after it"]],
            ),
            step(
                [" /---\\", "|  .  |", "| \\_/ |", " \\___/",
                 " /---\\", "|  .  |", "| \\_/ |", " \\___/"],
                [" /---\\", "|  .  |", "| \\_/ |", " \\___/",
                 " /---\\", "|  o  |", "| \\_/ |", " \\___/"],
                "6Gf.ro",
                [["6Gf.", "find the copied frame's eye without counting columns"],
                 ["ro", "change only its focus glyph"]],
            ),
            step(
                [" /---\\", "|  .  |", "| \\_/ |", " \\___/",
                 " /---\\", "|  o  |", "| \\_/ |", " \\___/"],
                [" /---\\", "|  O  |", "| \\_/ |", " \\___/",
                 " /---\\", "|  O  |", "| \\_/ |", " \\___/"],
                ":%s/[.o]/O/g<CR>",
                [[":%s/[.o]/O/g", "normalize only the two known eye glyphs across both frames"]], alternatives=[
                method("two local replacements", "2Gf.rO4jfOrO", "visit and replace each eye without touching the contour"),
                method("scoped substitute", ":%s/[.o]/O/g<CR>", "match only the eye spellings used in this strip"),
            ]),
            step(
                [" /---\\", "|  O  |", "| \\_/ |", " \\___/",
                 " /---\\", "|  O  |", "| \\_/ |", " \\___/"],
                [" /---\\", "|  O  |", "| \\_/ |", " \\___/",
                 " /---\\", "|  O  |", "| \\_/ |", " \\___/",
                 " /---\\", "|  -  |", "| \\_/ |", " \\___/"],
                ":1,4t$<CR>10GfOr-",
                [[":1,4t$", "copy the whole registered face as a third frame"],
                 ["10GfOr-", "turn only its eye into a blink"]],
            ),
        ],
        "transfer": step(
            [" /---\\", "|  o  |", "|  _  |", " \\___/"],
            [" /---\\", "|  O  |", "|  _  |", " \\___/"],
            "jforO",
            [["jfo", "find the unfamiliar face's eye"], ["rO", "change only that feature"]],
        ),
        "transfer_alt": step(
            [" /===\\", "|  o  |", "| --- |", " \\___/"],
            [" /===\\", "|  O  |", "| --- |", " \\___/"],
            "jforO",
            [["jfo", "find the eye inside the changed silhouette"], ["rO", "replace only it"]],
        ),
    },
    {
        "id": "M3", "title": "Pose copy", "node": "A2/V3", "project": "pose-copy",
        "skill": "duplicate a whole key pose and change one acting feature", "frame_rows": 6,
        "source_ref": "ascii-art-authoring §§9c-9f; Neovim tutor 3.1 and 6.4",
        "meaning": "one registered six-row body carries a small eye change across key poses",
        "first_reading": "the eye changes from a placeholder to the approved open focus while the six-row body stays fixed",
        "principle": "derive every later frame from the approved complete primary pose",
        "defect": "only part of the body was copied, or stable torso and feet drift with the eye",
        "basic": "copy all six pose rows with 6yy/p, then edit only the copy",
        "scaled": "copy the addressed six-line pose with :t, then change one acting feature",
        "steps": [
            step(
                ["  /\\   ", " (.)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  "],
                ["  /\\   ", " (o)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  "],
                "2G0f(%hro",
                [["2G0f(", "land on the opening parenthesis around the eye"],
                 ["%", "verify the matching closing parenthesis before editing inside it"],
                 ["h", "return to the enclosed eye glyph"],
                 ["ro", "approve its primary expression"]],
            ),
            step(
                ["  /\\   ", " (o)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  "],
                ["  /\\   ", " (o)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  ",
                 "  /\\   ", " (o)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  "],
                "gg6yyGp",
                [["gg6yy", "copy all six rows of the approved key pose"],
                 ["Gp", "put the full copy after the original"]],
            ),
            step(
                ["  /\\   ", " (o)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  ",
                 "  /\\   ", " (o)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  "],
                ["  /\\   ", " (o)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  ",
                 "  /\\   ", " (O)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  "],
                "8Gci(O<Esc>",
                [["8G", "move to the copied pose's eye row"],
                 ["ci(", "change only the text object inside the matching parentheses"],
                 ["O<Esc>", "set the acting feature and leave the enclosing head intact"]],
            ),
            step(
                ["  /\\   ", " (o)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  ",
                 "  /\\   ", " (O)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  "],
                ["  /\\   ", " (o)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  ",
                 "  /\\   ", " (O)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  ",
                 "  /\\   ", " (o)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  "],
                ":1,6t$<CR>",
                [[":1,6t$", "copy the addressed primary pose to the end"]], alternatives=[
                method("counted yank", "gg6yyGp", "copy the first six-row pose and put it at the end"),
                method("addressed copy", ":1,6t$<CR>", "copy lines 1 through 6 directly to the end"),
            ]),
            step(
                ["  /\\   ", " (o)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  ",
                 "  /\\   ", " (O)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  ",
                 "  /\\   ", " (o)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  "],
                ["  /\\   ", " (o)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  ",
                 "  /\\   ", " (O)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  ",
                 "  /\\   ", " (·)   ", " /|\\   ", "  |    ", " / \\   ", "/___\\  "],
                "14Gfor<C-k>.M",
                [["14Gfo", "go directly to the final pose's acting eye"],
                 ["r<C-k>.M", "give only that frame a middle-dot accent"]],
            ),
        ],
        "transfer": step(
            ["  /\\   ", " (o)   ", "--|--  ", "  |    ", " / \\   ", "/___\\  "],
            ["  /\\   ", " (o)   ", "--|--  ", "  |    ", " / \\   ", "/___\\  ",
             "  /\\   ", " (O)   ", "--|--  ", "  |    ", " / \\   ", "/___\\  "],
            "ggV5j\"ayG\"ap8GforO",
            [["ggV5j\"ay", "select the full unfamiliar pose and preserve it in named register a"],
             ["G\"ap", "put that complete registered pose after the original"],
             ["8GforO", "change one eye only in the copy"]],
        ),
        "transfer_alt": step(
            ["  /\\   ", " (x)   ", " \\|/   ", "  |    ", " / \\   ", "/___\\  "],
            ["  /\\   ", " (x)   ", " \\|/   ", "  |    ", " / \\   ", "/___\\  ",
             "  /\\   ", " (X)   ", " \\|/   ", "  |    ", " / \\   ", "/___\\  "],
            "gg6yyGp8GfxrX",
            [["gg6yyGp", "copy the complete alternate pose"],
             ["8GfxrX", "change one accent in the copy"]],
        ),
    },
    {
        "id": "M4", "title": "Rotation tween", "node": "A3/V4", "project": "rotation-tween",
        "skill": "multi-row extremes, midpoint, and stable pivot", "frame_rows": 3,
        "source_ref": "ascii-art-authoring §§4.4,9f-9g; P2 00:37:34; Neovim help visual-block, :copy",
        "meaning": "a two-cell prop rotates around a registered body pivot through a vertical midpoint",
        "first_reading": "only the copied prop turns from backslashes to forward slashes around the same pivot",
        "principle": "draw both complete extremes before inserting the middle in-between",
        "defect": "the body pivot or baseline drifts while only the two prop cells should rotate",
        "basic": "replace the moving prop cells while preserving the pivot row",
        "scaled": "use visual block only for a true aligned prop column inside complete frames",
        "steps": [
            step(
                ["  \\    ", "   \\   ", "---o---",
                 "  \\    ", "   \\   ", "---o---"],
                ["  \\    ", "   \\   ", "---o---",
                 "    /  ", "   /   ", "---o---"],
                "4G0C    /<Esc>5G03lr/",
                [["4G0C    /<Esc>", "move the copied upper tip across the pivot axis"],
                 ["5G03lr/", "turn the lower stroke at the fixed pivot column"]],
            ),
            step(
                ["  \\    ", "   \\   ", "---o---",
                 "    /  ", "   /   ", "---o---"],
                ["  \\    ", "   \\   ", "---o---",
                 "    /  ", "   /   ", "---o---",
                 "    /  ", "   /   ", "---o---"],
                "4G3yyGp",
                [["4G3yy", "copy the complete forward extreme"],
                 ["Gp", "put a working frame after both key poses"]],
            ),
            step(
                ["  \\    ", "   \\   ", "---o---",
                 "    /  ", "   /   ", "---o---",
                 "    /  ", "   /   ", "---o---"],
                ["  \\    ", "   \\   ", "---o---",
                 "   |   ", "   |   ", "---o---",
                 "    /  ", "   /   ", "---o---",
                 "    /  ", "   /   ", "---o---"],
                ":1,3t3<CR>4G0C   \\<Esc>4G03l<C-v>jr|",
                [[":1,3t3", "copy a complete extreme into the middle position"],
                 ["4G C", "register the copied upper stroke over the pivot axis"],
                 ["03l<C-v>jr|", "replace the now-aligned two-cell column as the vertical midpoint"]],
            ),
            step(
                ["  \\    ", "   \\   ", "---o---",
                 "   |   ", "   |   ", "---o---",
                 "    /  ", "   /   ", "---o---",
                 "    /  ", "   /   ", "---o---"],
                ["  \\    ", "   \\   ", "---o---",
                 "   |   ", "   |   ", "---o---",
                 "    /  ", "   /   ", "---o---",
                 "   |   ", "   |   ", "---o---",
                 "  \\    ", "   \\   ", "---o---"],
                "10G0C   |<Esc>11G0C   |<Esc>:1,3t$<CR>",
                [["10G/11G C", "turn the copied forward extreme into the return midpoint"],
                 [":1,3t$", "append a seam candidate that the mastery check must inspect"]], alternatives=[
                method("addressed seam candidate", "10G0C   |<Esc>11G0C   |<Esc>:1,3t$<CR>", "redraw the return midpoint, then copy the exact first frame"),
                method("counted seam candidate", "10G0C   |<Esc>11G0C   |<Esc>gg3yyGp", "redraw the return midpoint, then yank and put the complete first frame"),
            ]),
            step(
                ["  \\    ", "   \\   ", "---o---",
                 "   |   ", "   |   ", "---o---",
                 "    /  ", "   /   ", "---o---",
                 "   |   ", "   |   ", "---o---",
                 "  \\    ", "   \\   ", "---o---"],
                ["  \\    ", "   \\   ", "---o---",
                 "   |   ", "   |   ", "---o---",
                 "    /  ", "   /   ", "---o---",
                 "   |   ", "   |   ", "---o---"],
                "13G3dd",
                [["13G3dd", "remove the repeated first pose at the loop boundary; playback wraps frame 4 to frame 1"]],
                method_requirement=require_method(
                    "delete exactly the redundant three-row seam frame",
                    exact_any_of=["13G3dd"]),
                review_variants=[
                    step(["  /    ", "  |    ", "--o--  ",
                          "  |    ", "  |    ", "--o--  ",
                          "    \\  ", "    |  ", "--o--  ",
                          "  |    ", "  |    ", "--o--  ",
                          "  /    ", "  |    ", "--o--  "],
                         ["  /    ", "  |    ", "--o--  ",
                          "  |    ", "  |    ", "--o--  ",
                          "    \\  ", "    |  ", "--o--  ",
                          "  |    ", "  |    ", "--o--  "],
                         "13G3dd", [["13G3dd", "remove exactly the repeated seam pose"]],
                         method_requirement=require_method(
                             "delete exactly the changed three-row seam frame",
                             exact_any_of=["13G3dd"])),
                    step(["    \\  ", "    |  ", "--x--  ",
                          "  |    ", "  |    ", "--x--  ",
                          "  /    ", "  |    ", "--x--  ",
                          "  |    ", "  |    ", "--x--  ",
                          "    \\  ", "    |  ", "--x--  "],
                         ["    \\  ", "    |  ", "--x--  ",
                          "  |    ", "  |    ", "--x--  ",
                          "  /    ", "  |    ", "--x--  ",
                          "  |    ", "  |    ", "--x--  "],
                         "13G3dd", [["13G3dd", "remove the alternate repeated seam pose"]],
                         method_requirement=require_method(
                             "delete exactly the alternate three-row seam frame",
                             exact_any_of=["13G3dd"])),
                ],
            ),
        ],
        "transfer": step(
            ["  \\    ", "   \\   ", "===O===",
             "    /  ", "   /   ", "===O==="],
            ["  \\    ", "   \\   ", "===O===",
             "   |", "   |", "===O===",
             "    /  ", "   /   ", "===O==="],
            ":1,3t3<CR>4G0C   |<Esc>5G0C   |<Esc>",
            [[":1,3t3", "copy a complete unfamiliar extreme into the gap"],
             ["4G/5G C", "redraw only its moving strokes as the midpoint"]],
        ),
        "transfer_alt": step(
            ["    /  ", "   /   ", "---x---",
             "  \\    ", "   \\   ", "---x---"],
            ["    /  ", "   /   ", "---x---",
             "   |", "   |", "---x---",
             "  \\    ", "   \\   ", "---x---"],
            ":1,3t3<CR>4G0C   |<Esc>5G0C   |<Esc>",
            [[":1,3t3", "copy the reversed unfamiliar extreme"],
             ["4G/5G C", "resolve a registered vertical midpoint"]],
        ),
    },
    {
        "id": "M5", "title": "Layered scene", "node": "A4/V5", "project": "layered-scene",
        "skill": "foreground, background, and negative-space seams", "frame_rows": 7,
        "source_ref": "ascii-art-authoring §§3,11; Neovim help visual-line, /, :copy",
        "meaning": "a swinging foreground blade stays separate from a textured background in every frame",
        "first_reading": "one covered background stroke is erased so it no longer joins the foreground pivot",
        "principle": "erase from the background layer at every false seam while preserving the foreground silhouette",
        "defect": "a background stroke touches the pivot and makes the blade and ground read as one object",
        "basic": "erase one covered background cell in the complete layered frame",
        "scaled": "copy the entire seven-row layered frame before moving the foreground and its background hole",
        "steps": [
            step(
                ["  /       ", "   /      ", "----o-----",
                 "....|.....", "..........", "==========", "__________"],
                ["  /       ", "   /      ", "----o-----",
                 ".... .....", "..........", "==========", "__________"],
                "4G04lr ",
                [["4G04l", "reach the background cell directly touching the pivot"],
                 ["r ", "erase from the background layer, not from the blade"]],
            ),
            step(
                ["  /       ", "   /      ", "----o-----",
                 ".... .....", "..........", "==========", "__________"],
                ["  /       ", "   /      ", "----o-----",
                 ".... .....", "..........", "==========", "__________",
                 "  /       ", "   /      ", "----o-----",
                 ".... .....", "..........", "==========", "__________"],
                "ggV6jyGp",
                [["ggV6jy", "select and yank the complete seven-row composited frame"],
                 ["Gp", "put the layered working copy after it"]],
            ),
            step(
                ["  /       ", "   /      ", "----o-----",
                 ".... .....", "..........", "==========", "__________",
                 "  /       ", "   /      ", "----o-----",
                 ".... .....", "..........", "==========", "__________"],
                ["  /       ", "   /      ", "----o-----",
                 ".... .....", "..........", "==========", "__________",
                 "      \\   ", "     \\    ", "----o-----",
                 ".... .....", "..........", "==========", "__________"],
                "8G0C      \\<Esc>9G0C     \\<Esc>",
                [["8G/9G C", "redraw only the copied foreground stroke on the opposite side"],
                 ["registered pivot", "keep the existing negative-space break directly below the fixed pivot"]],
            ),
            step(
                ["  /       ", "   /      ", "----o-----",
                 ".... .....", "..........", "==========", "__________",
                 "      \\   ", "     \\    ", "----o-----",
                 ".... .....", "..........", "==========", "__________"],
                ["  /       ", "   /      ", "----o-----",
                 ".... .....", "..........", "==========", "__________",
                 "    |     ", "    |     ", "----o-----",
                 ".... .....", "..........", "==========", "__________",
                 "      \\   ", "     \\    ", "----o-----",
                 ".... .....", "..........", "==========", "__________"],
                ":1,7t7<CR>8G0C    |<Esc>9G0C    |<Esc>",
                [[":1,7t7", "insert the complete left extreme into the temporal gap"],
                 ["8G/9G C", "redraw only its blade rows as a distinct vertical midpoint"]], alternatives=[
                method("addressed midpoint", ":1,7t7<CR>8G0C    |<Esc>9G0C    |<Esc>", "copy the exact seven-row frame into the gap, then redraw its moving rows"),
                method("counted midpoint", "gg7yy7Gp8G0C    |<Esc>9G0C    |<Esc>", "yank seven rows into the gap, then redraw its moving rows"),
            ]),
            step(
                ["  /       ", "   /      ", "----o-----",
                 ".... .....", "..........", "==========", "__________",
                 "    |     ", "    |     ", "----o-----",
                 ".... .....", "..........", "==========", "__________",
                 "      \\   ", "     \\    ", "----o-----",
                 ".... .....", "..........", "==========", "__________"],
                ["  /       ", "   /      ", "----o-----",
                 ".... .....", "..........", "==========", "__________",
                 "    |     ", "    |     ", "----O-----",
                 ".... .....", "..........", "==========", "__________",
                 "      \\   ", "     \\    ", "----o-----",
                 ".... .....", "..........", "==========", "__________"],
                "10G0forO",
                [["10G0fo", "find the pivot in the middle layered frame"],
                 ["rO", "mark the intended foreground junction without reconnecting the background"]],
            ),
        ],
        "transfer": step(
            ["  /\\      ", " /  \\     ", "/____o----",
             ".....|....", "..........", "==========", "__________"],
            ["  /\\      ", " /  \\     ", "/____o----",
             "..... ....", "..........", "==========", "__________"],
            "4G05lr ",
            [["4G05l", "reach the background stroke touching the new foreground pivot"],
             ["r ", "break the false connection from the background side"]],
        ),
        "transfer_alt": step(
            ["    /\\    ", "---/  \\   ", "  /___x---",
             "......|...", "..........", "~~~~~~~~~~", "__________"],
            ["    /\\    ", "---/  \\   ", "  /___x---",
             "...... ...", "..........", "~~~~~~~~~~", "__________"],
            "4G06lr ",
            [["4G06l", "find the changed composition's touching background seam"],
             ["r ", "erase only that covered cell"]],
        ),
    },
    {
        "id": "M6", "title": "Pyramid build", "node": "A5/V6", "project": "pyramid-build",
        "skill": "subtractive authoring and playback order", "frame_rows": 5,
        "source_ref": "ascii-art-authoring §10 subtractive animation; Neovim :copy/:move",
        "meaning": "a five-row finished form is deconstructed without changing frame height, then reordered for forward playback",
        "first_reading": "the placeholder apex becomes the finished keyframe apex without changing the other four rows",
        "principle": "author an accretive effect backward from its finished keyframe while preserving equal frame bounds",
        "defect": "authoring order is mistaken for playback order or deletion collapses a frame's height",
        "basic": "copy a complete frame, then blank one unit without deleting its row",
        "scaled": "copy or move exact five-line frame ranges with :t and :m",
        "steps": [
            step(
                ["    .    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                ["    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                "r^",
                [["^", "the cursor starts on the primary apex"],
                 ["r^", "complete the full five-row keyframe"]],
            ),
            step(
                ["    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                ["    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                ":1,5t$<CR>",
                [[":1,5t$", "copy the complete finished frame before subtracting from the copy"]],
            ),
            step(
                ["    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                ["    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                "6G0D",
                [["6G0D", "clear the copied apex row without deleting it; the shoulder below remains attached"]],
                method_requirement=require_method(
                    "clear the apex row while retaining the five-row frame",
                    exact_any_of=["6G0D"]),
                review_variants=[
                    step(["    +    ", "   /-\\   ", "  /---\\  ", " /-----\\ ", "/-------\\" ,
                          "    +    ", "   /-\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                         ["    +    ", "   /-\\   ", "  /---\\  ", " /-----\\ ", "/-------\\" ,
                          "", "   /-\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                         "6G0D", [["6G0D", "clear the changed apex without deleting its row"]],
                         method_requirement=require_method(
                             "clear the changed apex row while retaining frame height",
                             exact_any_of=["6G0D"])),
                    step(["    *    ", "   /_\\   ", "  /___\\  ", " /_____\\ ", "/_______\\" ,
                          "    *    ", "   /_\\   ", "  /___\\  ", " /_____\\ ", "/_______\\"],
                         ["    *    ", "   /_\\   ", "  /___\\  ", " /_____\\ ", "/_______\\" ,
                          "", "   /_\\   ", "  /___\\  ", " /_____\\ ", "/_______\\"],
                         "6G0D", [["6G0D", "clear the alternate apex while keeping five rows"]],
                         method_requirement=require_method(
                             "clear the alternate apex row while retaining frame height",
                             exact_any_of=["6G0D"])),
                ],
            ),
            step(
                ["    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                ["    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "", "", "  /---\\  ", " /-----\\ ", "/-------\\"],
                ":6,10t$<CR>12G0D",
                [[":6,10t$", "copy the complete first reduced frame"],
                 ["12G0D", "remove the next upper unit without deleting its row"]], alternatives=[
                method("counted yank then clear", "6G5yyGp12G0D", "copy five rows, then clear the copied shoulder row"),
                method("addressed copy then clear", ":6,10t$<CR>12G0D", "copy the exact frame range, then clear its next upper unit"),
            ]),
            step(
                ["    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "", "", "  /---\\  ", " /-----\\ ", "/-------\\"],
                ["", "", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                ":11,15m0<CR>:11,15m5<CR>",
                [[":11,15m0", "move the most reduced complete frame to playback start"],
                 [":11,15m5", "place the intermediate reduction before the finished keyframe"]],
            ),
        ],
        "transfer": step(
            ["   ^   ", "  /_\\  ", " /---\\ ", "/-----\\", "=======",
             "   .   ", "  /_\\  ", " /---\\ ", "/-----\\", "======="],
            ["   .   ", "  /_\\  ", " /---\\ ", "/-----\\", "=======",
             "   ^   ", "  /_\\  ", " /---\\ ", "/-----\\", "======="],
            ":1,5m$<CR>",
            [[":1,5m$", "move the unfamiliar finished frame after its reduced predecessor"]],
        ),
        "transfer_alt": step(
            ["   O   ", "  /-\\  ", " /---\\ ", "/-----\\", "=======",
             "   o   ", "  /-\\  ", " /---\\ ", "/-----\\", "======="],
            ["   o   ", "  /-\\  ", " /---\\ ", "/-----\\", "=======",
             "   O   ", "  /-\\  ", " /---\\ ", "/-----\\", "======="],
            ":1,5m$<CR>",
            [[":1,5m$", "move the alternate finished build after its reduced state"]],
        ),
    },
    {
        "id": "M7", "title": "Timed build", "node": "A6/V7", "project": "pyramid-build",
        "skill": "holds, dot repeat, macro, and scoped polish", "frame_rows": 5,
        "source_ref": "ascii-art-authoring §10 timing; Neovim help q, @, ., :substitute",
        "meaning": "the five-row build pauses before completion and removes an accidental trailing duplicate",
        "first_reading": "a complete five-row incomplete build is repeated before completion to create anticipation",
        "principle": "a hold repeats a complete frame for a declared timing reason",
        "defect": "an identical frame is added without a timing role or a range edit leaks into the completed pose",
        "basic": "repeat one bounded feature change in the matching held frame with dot",
        "scaled": "record a frame-local substitution as a macro or use an exact frame range",
        "steps": [
            step(
                ["", "", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                ["", "", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "", "", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                ":1,5t5<CR>",
                [[":1,5t5", "duplicate the complete incomplete frame as an anticipation hold"]],
            ),
            step(
                ["", "", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "", "", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                ["", "", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "", "", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                ":16,20t$<CR>",
                [[":16,20t$", "copy the complete settle frame as a deliberately reviewable duplicate"]],
            ),
            step(
                ["", "", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "", "", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                ["", "", "  /===\\  ", " /-----\\ ", "/-------\\",
                 "", "", "  /===\\  ", " /-----\\ ", "/-------\\",
                 "", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                "3G0f-v2lr=5j.",
                [["3G0f-v2lr=", "change the first held frame's complete three-cell material band"],
                 ["5j.", "repeat the same bounded band edit in the matching hold"]],
            ),
            step(
                ["", "", "  /===\\  ", " /-----\\ ", "/-------\\",
                 "", "", "  /===\\  ", " /-----\\ ", "/-------\\",
                 "", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /---\\  ", " /-----\\ ", "/-------\\"],
                ["", "", "  /===\\  ", " /-----\\ ", "/-------\\",
                 "", "", "  /===\\  ", " /-----\\ ", "/-------\\",
                 "", "   /_\\   ", "  /===\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /===\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /===\\  ", " /-----\\ ", "/-------\\"],
                ":%s@/---\\\\@/===\\\\@g<CR>",
                [[":%s@/---\\\\@/===\\\\@g", "harmonize the exact three-cell material band across every visible frame"]], alternatives=[
                     method("recorded visual macro", "13Gqq0f-v2lr=5jq2@q", "record one characterwise-Visual band edit plus a five-row step, then replay it on the two remaining unmatched frames"),
                     method("global normal", ":g@^  /---@normal! 0f-v2lr=<CR>", "apply the same bounded Visual replacement only on exact material-band rows"),
                 ]),
            step(
                ["", "", "  /===\\  ", " /-----\\ ", "/-------\\",
                 "", "", "  /===\\  ", " /-----\\ ", "/-------\\",
                 "", "   /_\\   ", "  /===\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /===\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /===\\  ", " /-----\\ ", "/-------\\"],
                ["", "", "  /===\\  ", " /-----\\ ", "/-------\\",
                 "", "", "  /===\\  ", " /-----\\ ", "/-------\\",
                 "", "   /_\\   ", "  /===\\  ", " /-----\\ ", "/-------\\",
                 "    ^    ", "   /_\\   ", "  /===\\  ", " /-----\\ ", "/-------\\"],
                "21G5dd",
                [["21G5dd", "remove the accidental trailing duplicate while retaining the anticipation hold"]],
            ),
        ],
        "transfer": step(
            ["  /\\   ", " (o)  ", " /--\\ ", "/----\\", "______",
             "  /\\   ", " (o)  ", " /--\\ ", "/----\\", "______"],
            ["  /\\   ", " (O)  ", " /--\\ ", "/----\\", "______",
             "  /\\   ", " (O)  ", " /--\\ ", "/----\\", "______"],
            "2GforO5j.",
            [["2GforO", "change the acting feature in the first complete held frame"],
             ["5j.", "repeat that exact edit in its timed duplicate"]],
        ),
        "transfer_alt": step(
            ["  /\\   ", " (x)  ", " /==\\ ", "/====\\", "------",
             "  /\\   ", " (x)  ", " /==\\ ", "/====\\", "------"],
            ["  /\\   ", " (X)  ", " /==\\ ", "/====\\", "------",
             "  /\\   ", " (X)  ", " /==\\ ", "/====\\", "------"],
            "2GfxrX5j.",
            [["2GfxrX", "change the alternate hold's acting feature"],
             ["5j.", "repeat it in the duplicate frame"]],
        ),
    },
    {
        "id": "M8", "title": "Walk study", "node": "A7/V8", "project": "walk-study",
        "skill": "contact, secondary motion, and equal frame height", "frame_rows": 5,
        "source_ref": "ascii-art-authoring §§9g-10; walk timing 4+4+2 as method reference",
        "meaning": "a four-frame five-row walker plants alternating feet while its raised arm lags the body",
        "first_reading": "the leading foot gains a ground-contact mark while the torso and raised arm stay registered",
        "principle": "track the planted contact cell and let the secondary arm arrive on a different frame",
        "defect": "the planted foot slides, the torso shifts, or the arm flips without an adjacent transition",
        "basic": "change only the moving foot or arm inside a copied complete pose",
        "scaled": "use a bounded pattern or range when the same secondary-motion spelling recurs",
        "steps": [
            step(
                ["  o/     ", " /|      ", "  |      ", " / \\     ", "/   \\    "],
                ["  o/     ", " /|      ", "  |      ", " / \\     ", "/_  \\    "],
                "G0lr_",
                [["G0l", "reach the leading foot's ground-contact cell"],
                 ["r_", "plant it while leaving torso and raised arm unchanged"]],
            ),
            step(
                ["  o/     ", " /|      ", "  |      ", " / \\     ", "/_  \\    "],
                ["  o/     ", " /|      ", "  |      ", " / \\     ", "/_  \\    ",
                 "  o\\     ", " /|\\     ", "  |      ", "  |\\     ", " /  \\_   "],
                "gg5yyGp6G0C  o\\<Esc>7G0C /|\\<Esc>9G0C  |\\<Esc>10G0C /  \\_<Esc>",
                [["gg5yyGp", "copy the complete contact pose"],
                 ["6G/7G/9G/10G C", "change only the arm and legs in the copied passing pose"]],
            ),
            step(
                ["  o/     ", " /|      ", "  |      ", " / \\     ", "/_  \\    ",
                 "  o\\     ", " /|\\     ", "  |      ", "  |\\     ", " /  \\_   "],
                ["  o/     ", " /|      ", "  |      ", " / \\     ", "/_  \\    ",
                 "  o\\     ", " /|\\     ", "  |      ", "  |\\     ", " /  \\_   ",
                 " \\o      ", "  |\\     ", "  |      ", " /|      ", "/  _\\    "],
                "Go<C-u> \\o<Esc>o<C-u>  |\\<Esc>o<C-u>  |<Esc>o<C-u> /|<Esc>o<C-u>/  _\\<Esc>",
                [["G then o", "append each complete row of the opposite-contact pose directly"],
                 ["five bounded rows", "keep the torso column registered without padding the key path with unrelated I/A commands"]],
            ),
            step(
                ["  o/     ", " /|      ", "  |      ", " / \\     ", "/_  \\    ",
                 "  o\\     ", " /|\\     ", "  |      ", "  |\\     ", " /  \\_   ",
                 " \\o      ", "  |\\     ", "  |      ", " /|      ", "/  _\\    "],
                ["  o\\     ", " /|      ", "  |      ", " / \\     ", "/_  \\    ",
                 "  o\\     ", " /|\\     ", "  |      ", "  |\\     ", " /  \\_   ",
                 " \\o      ", "  |\\     ", "  |      ", " /|      ", "/  _\\    "],
                ":1,5s@o/@o\\\\@<CR>",
                [[":1,5s@o/@o\\\\@", "change only the first pose's delayed raised-arm spelling"]], alternatives=[
                method("local replacement", "gg0f/r\\", "find and replace the first pose's arm directly"),
                method("scoped substitute", ":1,5s@o/@o\\\\@<CR>", "limit the arm pattern to the complete first five-row pose"),
            ]),
            step(
                ["  o\\     ", " /|      ", "  |      ", " / \\     ", "/_  \\    ",
                 "  o\\     ", " /|\\     ", "  |      ", "  |\\     ", " /  \\_   ",
                 " \\o      ", "  |\\     ", "  |      ", " /|      ", "/  _\\    "],
                ["  o\\     ", " /|      ", "  |      ", " / \\     ", "/_  \\    ",
                 "  o\\     ", " /|\\     ", "  |      ", "  |\\     ", " /  \\_   ",
                 " \\o      ", "  |\\     ", "  |      ", " /|      ", "/  _\\    ",
                 " /o      ", "/|\\     ", "  |      ", " /|      ", "/_  \\   "],
                ":6,10t$<CR>16G0C /o<Esc>17G0C/|\\<Esc>19G0C /|<Esc>20G0C/_  \\<Esc>",
                [[":6,10t$", "copy the complete first passing pose as a scaffold"],
                 ["16G/17G/19G/20G C", "mirror its arm and leg action into a distinct return passing pose"]],
            ),
        ],
        "transfer": step(
            ["   o/   ", "  /|    ", "   |    ", "  / \\   ", " /   \\  "],
            ["   o/   ", "  /|    ", "   |    ", "  / \\   ", " /_  \\  "],
            "G0llr_",
            [["G0ll", "reach the unfamiliar pose's planted-foot cell"],
             ["r_", "restore contact without moving the torso"]],
        ),
        "transfer_alt": step(
            ["  \\O   ", "   |\\  ", "   |   ", "  /|   ", " /  \\  "],
            ["  \\O   ", "   |\\  ", "   |   ", "  /|   ", " / _\\  "],
            "G0lllr_",
            [["G0lll", "reach the opposite-contact cell in a changed subject"],
             ["r_", "plant it while keeping the secondary arm intact"]],
        ),
    },
    {
        "id": "M9", "title": "Original bounce capstone", "node": "A8/V9", "project": "original-micro",
        "skill": "plan, keyframe, tween, preview, and revise", "frame_rows": 3,
        "source_ref": "ascii-art-authoring §§9-10; all mastered Neovim nodes",
        "meaning": "an original three-row ball falls, squashes on a registered ground, rebounds with overshoot, then settles through the loop seam",
        "first_reading": "the planned high keyframe replaces its placeholder while the ground row remains registered",
        "principle": "state the motion, frame size, extremes, timing, and ground anchor before inserting the falling midpoint",
        "defect": "a recycled subject or unplanned middle pose is mistaken for original keyframe authoring",
        "basic": "author one readable high extreme and one squash extreme inside equal three-row bounds",
        "scaled": "copy complete frames, insert the fall midpoint, preview squash and rebound, then revise the seam",
        "steps": [
            step(
                ["|  x  |", "|     |", "|_____|"],
                ["|  o  |", "|     |", "|_____|"],
                "fxro",
                [["fx", "find the planned subject placeholder in the high extreme"],
                 ["ro", "commit the ball without moving the registered ground"]],
            ),
            step(
                ["|  o  |", "|     |", "|_____|"],
                ["|  o  |", "|     |", "|_____|",
                 "|     |", "| =O= |", "|_____|"],
                "gg3yyGp4G0C|     |<Esc>5G0C| =O= |<Esc>",
                [["gg3yyGp", "copy the complete high extreme, including its ground anchor"],
                 ["4G C", "clear the copied high row inside its retained side rails"],
                 ["5G C", "block the squash extreme around a visible acting centre"]],
            ),
            step(
                ["|  o  |", "|     |", "|_____|",
                 "|     |", "| =O= |", "|_____|"],
                ["|  o  |", "|     |", "|_____|",
                 "|     |", "| === |", "|_____|"],
                "5GfOr=",
                [["5GfO", "reach the squash scaffold's temporary centre"],
                 ["r=", "overwrite that one cell so the three-cell squash stays registered"]],
            ),
            step(
                ["|  o  |", "|     |", "|_____|",
                 "|     |", "| === |", "|_____|"],
                ["|  o  |", "|     |", "|_____|",
                 "|     |", "|  o  |", "|_____|",
                 "|     |", "| === |", "|_____|"],
                ":1,3t3<CR>4G0C|     |<Esc>5G0C|  o  |<Esc>",
                [[":1,3t3", "copy the high extreme into the temporal gap"],
                 ["4G/5G C", "move the ball down one row while preserving rails and ground"]], alternatives=[
                method("direct three-row insert", "3G3o<Esc>4G0C|     |<Esc>5G0C|  o  |<Esc>6G0C|_____|<Esc>", "open three bounded rows and author the falling midpoint explicitly"),
                method("copy then vary", ":1,3t3<CR>4G0C|     |<Esc>5G0C|  o  |<Esc>", "copy the registered rails and ground, then move only the subject"),
            ]),
            step(
                ["|  o  |", "|     |", "|_____|",
                 "|     |", "|  o  |", "|_____|",
                 "|     |", "| === |", "|_____|"],
                ["|  o  |", "|     |", "|_____|",
                 "|     |", "|  o  |", "|_____|",
                 "|     |", "| === |", "|_____|",
                 "|  O  |", "|     |", "|_____|"],
                ":1,3t$<CR>10GforO",
                [[":1,3t$", "copy the high keyframe as a registered rebound scaffold"],
                 ["10GforO", "make the rebound a larger overshoot so the loop settles into the first frame"]],
            ),
        ],
        "transfer": step(
            ["[ x ]", "[   ]", "[___]"],
            ["[ o ]", "[   ]", "[___]"],
            "fxro",
            [["fx", "find the changed bounce subject's planned high point"],
             ["ro", "commit its primary keyframe without moving the ground"]],
        ),
        "transfer_alt": step(
            ["<  x  >", "<     >", "<=====>"],
            ["<  X  >", "<     >", "<=====>"],
            "fxrX",
            [["fx", "find the alternate plan marker independent of its horizontal offset"],
             ["rX", "commit the changed subject while preserving the ground anchor"]],
        ),
    },
    {
        "id": "M10", "title": "SJIS puff tween", "node": "P1/V10", "project": "sjis-puff-tween",
        "skill": "proportional contour motion, occlusion stacks, bounded hatching, and true-metric review",
        "frame_rows": 3, "medium": "proportional-sjis",
        "phase_titles": {3: "Read the proportional motion", 7: "Diagnose the proportional motion"},
        "source_ref": "sjis_corpus_findings.v1.json; ascii-art-authoring §§9-10,15.3-15.7",
        "meaning": "a three-row proportional puff expands from a lobe into an arch, holds at impact with bounded hatching, then settles",
        "first_reading": "the missing partner becomes ⌒ヽ while the lower two contour rows remain registered",
        "principle": "keep complete equal-height frames and stable contour landmarks, but judge proportional alignment in Saitamaar at true advances",
        "defect": "a shoulder changes without its lower contour, hatching escapes the outline, or terminal-cell alignment is mistaken for proportional visual evidence",
        "basic": "edit one measured pair inside a complete three-row puff frame and preserve the other contour rows",
        "scaled": "copy the complete three-row frame, transform its outline as one pose, and preview the ordered strip in Saitamaar",
        "steps": [
            step(
                ["　　⌒?", "　（　　）", "　　ヽ_ノ"],
                ["　　⌒ヽ", "　（　　）", "　　ヽ_ノ"],
                "$rヽ",
                [["$", "reach the missing partner inside the complete puff frame"],
                 ["rヽ", "complete the ⌒ヽ shoulder without disturbing the registered base"]],
            ),
            step(
                ["　　⌒ヽ", "　（　　）", "　　ヽ_ノ"],
                ["　　⌒ヽ", "　（　　）", "　　ヽ_ノ",
                 "　／￣＼", "（　　　）", "　＼＿／"],
                "gg3yyGp4G0C　／￣＼<Esc>5G0C（　　　）<Esc>6G0C　＼＿／<Esc>",
                [["gg3yyGp", "copy the complete three-row lobe as the expansion scaffold"],
                 ["4G/5G/6G C", "redraw all three copied rows as the wider arch extreme"]],
            ),
            step(
                ["　　⌒ヽ", "　（　　）", "　　ヽ_ノ",
                 "　／￣＼", "（　　　）", "　＼＿／"],
                ["　　⌒ヽ", "　（　　）", "　　ヽ_ノ",
                 "　／￣＼", "（　　　）", "　＼＿／",
                 "／￣￣＼", "|ﾆ二ニ|", "＼＿＿／"],
                "Go／￣￣＼<Esc>o|ﾆ二ニ|<Esc>o＼＿＿／<Esc>",
                [["G", "go to the end of the two-frame proportional strip"],
                 ["three bounded rows", "append the impact pose with hatching contained by its outline"]],
            ),
            step(
                ["　　⌒ヽ", "　（　　）", "　　ヽ_ノ",
                 "　／￣＼", "（　　　）", "　＼＿／",
                 "／￣￣＼", "|ﾆ二ニ|", "＼＿＿／"],
                ["　　⌒ヽ", "　（　　）", "　　ヽ_ノ",
                 "　／￣＼", "（　　　）", "　＼＿／",
                 "／￣￣＼", "|ﾆ二ニ|", "＼＿＿／",
                 "／￣￣＼", "|ﾆ二ニ|", "＼＿＿／"],
                ":7,9t$<CR>",
                [[":7,9t$", "repeat the complete impact pose as a deliberate two-frame hold"]], alternatives=[
                method("counted yank and put", "7G3yyGp", "copy all three impact rows from their first line",
                       {"kind": "linewise_yank_put", "rows": 3}),
                method("addressed copy", ":7,9t$<CR>", "copy the exact impact-frame range without relying on cursor position",
                       {"kind": "ex_copy", "start": 7, "end": 9, "destination": "$"}),
            ]),
            step(
                ["　　⌒ヽ", "　（　　）", "　　ヽ_ノ",
                 "　／￣＼", "（　　　）", "　＼＿／",
                 "／￣￣＼", "|ﾆ二ニ|", "＼＿＿／",
                 "／￣￣＼", "|ﾆ二ニ|", "＼＿＿／"],
                ["　　⌒ヽ", "　（　　）", "　　ヽ_ノ",
                 "　／￣＼", "（　　　）", "　＼＿／",
                 "／￣￣＼", "|ﾆ二ニ|", "＼＿＿／",
                 "／￣￣＼", "|ﾆ二ニ|", "＼＿＿／",
                 "　　⌒ヽ", "　（　　）", "　　ヽ_ノ"],
                ":1,3t$<CR>",
                [[":1,3t$", "return to the complete lobe frame as the proportional settle"]],
            ),
        ],
        "transfer": step(
            ["　　｀?", "　（　　）", "　　ヽ_ノ"],
            ["　　｀ヽ", "　（　　）", "　　ヽ_ノ"],
            "$rヽ",
            [["$", "reach the unknown partner in a changed complete puff"],
             ["rヽ", "complete the ｀ヽ shoulder while preserving both registered rows"]],
        ),
        "transfer_alt": step(
            ["　／?＼", "（　　　）", "　＼＿／"],
            ["　／￣＼", "（　　　）", "　＼＿／"],
            "0f?r￣",
            [["0f?", "find the missing shoulder partner in the alternate expansion pose"],
             ["r￣", "complete the ／￣ shoulder without changing the bowl"]],
        ),
    },
    {
        "id": "M11", "title": "Fixed-width redraw", "node": "A9/V11", "project": "redraw-lab",
        "skill": "replace-mode redraw, meaningful undo/redo, and virtual-column motion blur",
        "frame_rows": 3,
        "source_ref": "ascii-art-authoring §§4.4,9h-10; Neovim help R, undo-redo, virtualedit, bar",
        "meaning": "a paired three-row machinery loop changes surface tension in place, proves recovery, and adds aligned motion-blur trails past short rows",
        "first_reading": "the first roof changes from a loose -- band to a taut == band without shifting either side wall",
        "principle": "overwrite fixed-width art when the row length must remain stable, and use virtual columns only when the intended glyph lies beyond end-of-line",
        "defect": "inserted or deleted cells shift the machinery walls, undo/redo is performed as a no-op demonstration, or blur trails land in different columns",
        "basic": "redraw a bounded run with Replace mode while preserving both endpoints",
        "scaled": "recover and reapply a real redraw, compare Replace with Visual replacement, then place homologous trails at one virtual column",
        "steps": [
            step(
                ["/--\\  /--\\", "| o|  |o |", "\\__|  |__/"],
                ["/==\\  /--\\", "| o|  |o |", "\\__|  |__/"],
                "0lR==<Esc>",
                [["0l", "stand on the first cell inside the fixed roof endpoints"],
                 ["R==<Esc>", "overwrite exactly two material cells without shifting either wall"]],
                method_requirement=require_method(
                    "overwrite the fixed-width roof with Replace mode",
                    exact_any_of=["0lR==<Esc>"]),
            ),
            step(
                ["/==\\  /--\\", "| o|  |o |", "\\__|  |__/"],
                ["/==\\  /--\\", "| o|  |o |", "\\__|  |__/",
                 "/==\\  /--\\", "| o|  |o |", "\\__|  |__/"],
                "gg3yyGp",
                [["gg3yyGp", "copy the complete three-row registered machine pose before changing its tension"]],
                review_variants=[
                    step(["/--\\  /--\\", "| x|  |x |", "\\..|  |.. /"],
                         ["/--\\  /--\\", "| x|  |x |", "\\..|  |.. /",
                          "/--\\  /--\\", "| x|  |x |", "\\..|  |.. /"],
                         "gg3yyGp", [["gg3yyGp", "copy all three changed rows"]]),
                    step([".==.  .==.", "| *|  |* |", "'__'  '__'"],
                         [".==.  .==.", "| *|  |* |", "'__'  '__'",
                          ".==.  .==.", "| *|  |* |", "'__'  '__'"],
                         "gg3yyGp", [["gg3yyGp", "copy the alternate complete pose"]]),
                ],
            ),
            step(
                ["/==\\  /--\\", "| o|  |o |", "\\__|  |__/",
                 "/==\\  /--\\", "| o|  |o |", "\\__|  |__/"],
                ["/==\\  /--\\", "| o|  |o |", "\\__|  |__/",
                 "/~~\\  /--\\", "| o|  |o |", "\\__|  |__/"],
                "4G0lR~~<Esc>u<C-r>",
                [["4G0lR~~<Esc>", "redraw the copied roof as the slack extreme"],
                 ["u", "actually remove that redraw so the registered == pose returns"],
                 ["<C-r>", "redo the redraw so the required slack extreme is again the saved result"]],
                method_requirement=require_method(
                    "undo and redo a real fixed-width redraw",
                    exact_any_of=["4G0lR~~<Esc>u<C-r>"]),
                review_variants=[
                    step(["/++\\  /--\\", "| x|  |x |", "\\__|  |__/",
                          "/++\\  /--\\", "| x|  |x |", "\\__|  |__/"],
                         ["/++\\  /--\\", "| x|  |x |", "\\__|  |__/",
                          "/..\\  /--\\", "| x|  |x |", "\\__|  |__/"],
                         "4G0lR..<Esc>u<C-r>",
                         [["R.. / u / <C-r>", "redraw, remove, and restore the changed roof"]],
                         method_requirement=require_method(
                             "undo and redo the changed roof redraw",
                             exact_any_of=["4G0lR..<Esc>u<C-r>"])),
                    step([".==.  .--.", "| *|  |* |", "'__'  '  '",
                          ".==.  .--.", "| *|  |* |", "'__'  '  '"],
                         [".==.  .--.", "| *|  |* |", "'__'  '  '",
                          ".--.  .--.", "| *|  |* |", "'__'  '  '"],
                         "4G0lR--<Esc>u<C-r>",
                         [["R-- / u / <C-r>", "recover and reapply the alternate redraw"]],
                         method_requirement=require_method(
                             "undo and redo the alternate roof redraw",
                             exact_any_of=["4G0lR--<Esc>u<C-r>"])),
                ],
            ),
            step(
                ["/==\\  /--\\", "| o|  |o |", "\\__|  |__/",
                 "/~~\\  /--\\", "| o|  |o |", "\\__|  |__/"],
                ["/==\\  /--\\", "| o|  |o |", "\\__|  |__/",
                 "/~~\\  /--\\", "| O|  |O |", "\\__|  |__/"],
                "5G:s/o/O/g<CR>",
                [["5G:s/o/O/g", "change only the copied pose's two acting indicators"]], alternatives=[
                method("two local replacements", "5G0forO5lrO", "find and replace each acting indicator on the one copied row"),
                method("current-row substitute", "5G:s/o/O/g<CR>", "replace both indicators while keeping the substitution scoped to the copied row"),
            ], review_variants=[
                step(["/==\\  /--\\", "| x|  |x |", "\\__|  |__/",
                      "/~~\\  /--\\", "| x|  |x |", "\\__|  |__/"],
                     ["/==\\  /--\\", "| x|  |x |", "\\__|  |__/",
                      "/~~\\  /--\\", "| X|  |X |", "\\__|  |__/"],
                     "5G:s/x/X/g<CR>", [["5G:s/x/X/g", "bound the changed indicators to one row"]],
                     method_requirement=require_method(
                         "use a bounded indicator edit on changed art",
                         exact_any_of=["5G:s/x/X/g<CR>"])),
                step([".==.  .--.", "| *|  |* |", "'__'  '__'",
                      ".~~.  .--.", "| *|  |* |", "'__'  '__'"],
                     [".==.  .--.", "| *|  |* |", "'__'  '__'",
                      ".~~.  .--.", "| +|  |+ |", "'__'  '__'"],
                     "5G:s/\\*/+/g<CR>", [["5G:s/\\*/+/g", "change the alternate indicators on one row"]],
                     method_requirement=require_method(
                         "use a bounded indicator edit on changed art",
                         exact_any_of=["5G:s/\\*/+/g<CR>"])),
            ]),
            step(
                ["/==\\  /--\\", "| o|  |o |", "\\__|  |__/",
                 "/~~\\  /--\\", "| O|  |O |", "\\__|  |__/"],
                ["/==\\  /--\\", "| o|  |o |  |", "\\__|  |__/",
                 "/~~\\  /--\\", "| O|  |O |  |", "\\__|  |__/"],
                ":set virtualedit=all<CR>2G13|i|<Esc>3j.",
                [[":set virtualedit=all", "permit an exact column target beyond the short acting rows"],
                 ["2G13|i|<Esc>", "position before display column 14 and insert the first blur trail there"],
                 ["3j.", "repeat the same insertion in the homologous row of the next complete frame"]],
                method_requirement=require_method(
                    "enable virtual editing and place both trails at exact column 14",
                    exact_any_of=[":set virtualedit=all<CR>2G13|i|<Esc>3j."]),
                review_variants=[
                    step(["/--\\  /--\\", "| x|  |x |", "\\__|  |__/",
                          "/..\\  /--\\", "| X|  |X |", "\\__|  |__/"],
                         ["/--\\  /--\\", "| x|  |x |  |", "\\__|  |__/",
                          "/..\\  /--\\", "| X|  |X |  |", "\\__|  |__/"],
                         ":set virtualedit=all<CR>2G13|i|<Esc>3j.",
                         [["virtualedit / 13| / .", "align both changed-art trails"]]),
                    step([".==.  .--.", "| *|  |* |", "'__'  '__'",
                          ".~~.  .--.", "| +|  |+ |", "'__'  '__'"],
                         [".==.  .--.", "| *|  |* |  |", "'__'  '__'",
                          ".~~.  .--.", "| +|  |+ |  |", "'__'  '__'"],
                         ":set virtualedit=all<CR>2G13|i|<Esc>3j.",
                         [["virtualedit / 13| / .", "align the alternate trails"]]),
                ],
            ),
        ],
        "transfer": step(
            ["/..\\  /..\\", "| x|  |x |", "\\__|  |__/"],
            ["/==\\  /..\\", "| x|  |x |", "\\__|  |__/"],
            "0lR==<Esc>",
            [["0lR==<Esc>", "overwrite the unfamiliar roof run without shifting its walls"]],
            method_requirement=require_method(
                "transfer the fixed-width redraw with Replace mode",
                exact_any_of=["0lR==<Esc>"]),
        ),
        "transfer_alt": step(
            [".--.  .--.", "| *|  |* |", "'__'  '  '"],
            [".==.  .--.", "| *|  |* |", "'__'  '  '"],
            "0lR==<Esc>",
            [["0lR==<Esc>", "apply the same bounded overwrite to a changed silhouette"]],
        ),
    },
    {
        "id": "M12", "title": "Joint sweep", "node": "S2/V12", "project": "mirror-sweep",
        "skill": "staggered bilateral accents with till motions and repeated character searches",
        "frame_rows": 3,
        "source_ref": "ascii-art-authoring §10 stagger and drag; Neovim help f, t, ;, comma",
        "meaning": "a three-row mirrored mechanism passes a joint accent from left to right, then staggers the lower joints before returning on the opposite side",
        "first_reading": "the left upper joint changes from : to ! while the centre axis, mirrored outline, and right joint stay registered",
        "principle": "preserve the already paired shell and centre axis while addressing homologous punctuation by its visible landmark rather than memorised columns",
        "defect": "the stable shell is reversed unnecessarily, a character search lands on the delimiter instead of beside it, or both joint accents change at the same time despite a planned stagger",
        "basic": "use t or T to approach a visible joint from either direction, then make one in-place replacement",
        "scaled": "repeat a character search across homologous joints, compare it with a row-scoped substitute, and author the mirrored return pose",
        "steps": [
            step(
                ["\\..:..|..:../", " \\.:..|..:./ ", "  \\_o_|_o_/  "],
                ["\\..!..|..:../", " \\.:..|..:./ ", "  \\_o_|_o_/  "],
                "0t:lr!",
                [["0t:", "stop immediately before the first visible upper joint"],
                 ["lr!", "step onto that joint and accent it without shifting the mirrored row"]],
                method_requirement=require_method(
                    "approach the left joint with t before replacing it",
                    exact_any_of=["0t:lr!"]),
            ),
            step(
                ["\\..!..|..:../", " \\.:..|..:./ ", "  \\_o_|_o_/  "],
                ["\\..!..|..:../", " \\.:..|..:./ ", "  \\_o_|_o_/  ",
                 "\\..!..|..!../", " \\.:..|..:./ ", "  \\_o_|_o_/  "],
                "gg3yyGp4G$T:hr!",
                [["gg3yyGp", "copy the complete left-accent key pose"],
                 ["4G$T:hr!", "approach the copied right joint backward and accent its mirror"]],
                method_requirement=require_method(
                    "copy the pose and approach its right joint with T",
                    exact_any_of=["gg3yyGp4G$T:hr!"]),
            ),
            step(
                ["\\..!..|..:../", " \\.:..|..:./ ", "  \\_o_|_o_/  ",
                 "\\..!..|..!../", " \\.:..|..:./ ", "  \\_o_|_o_/  "],
                ["\\..!..|..:../", " \\.:..|..:./ ", "  \\_o_|_o_/  ",
                 "\\..!..|..!../", " \\.:..|..:./ ", "  \\_o_|_o_/  ",
                 "\\..!..|..!../", " \\.!..|..!./ ", "  \\_o_|_o_/  "],
                "4G3yyGp8G0f:;r!,r!",
                [["4G3yyGp", "copy the complete two-upper-joint extreme"],
                 ["8G0f:;r!,r!", "reach the second lower joint with ;, edit it, then return with , to edit the first"]],
                method_requirement=require_method(
                    "repeat the lower-joint character search with semicolon",
                    exact_any_of=["4G3yyGp8G0f:;r!,r!"]),
                review_variants=[
                    step(["\\..*..|..+../", " \\.+..|..+. /", "  \\_x_|_x_/  ",
                          "\\..*..|..*../", " \\.+..|..+. /", "  \\_x_|_x_/  "],
                         ["\\..*..|..+../", " \\.+..|..+. /", "  \\_x_|_x_/  ",
                          "\\..*..|..*../", " \\.+..|..+. /", "  \\_x_|_x_/  ",
                          "\\..*..|..*../", " \\.*..|..*. /", "  \\_x_|_x_/  "],
                         "4G3yyGp8G0f+;r*,r*",
                         [["f+ / ; / ,", "visit the second changed joint, then return to the first"]],
                         method_requirement=require_method(
                             "repeat the changed lower-joint search with semicolon",
                             exact_any_of=["4G3yyGp8G0f+;r*,r*"])),
                    step(["/..O..|..x..\\", " / .x..|..x.\\ ", "  /_+_|_+_\\  ",
                          "/..O..|..O..\\", " / .x..|..x.\\ ", "  /_+_|_+_\\  "],
                         ["/..O..|..x..\\", " / .x..|..x.\\ ", "  /_+_|_+_\\  ",
                          "/..O..|..O..\\", " / .x..|..x.\\ ", "  /_+_|_+_\\  ",
                          "/..O..|..O..\\", " / .O..|..O.\\ ", "  /_+_|_+_\\  "],
                         "4G3yyGp8G0fx;rO,rO",
                         [["fx / ; / ,", "visit the second alternate joint, then return to the first"]],
                         method_requirement=require_method(
                             "repeat the alternate lower-joint search with semicolon",
                             exact_any_of=["4G3yyGp8G0fx;rO,rO"])),
                ],
            ),
            step(
                ["\\..!..|..:../", " \\.:..|..:./ ", "  \\_o_|_o_/  ",
                 "\\..!..|..!../", " \\.:..|..:./ ", "  \\_o_|_o_/  ",
                 "\\..!..|..!../", " \\.!..|..!./ ", "  \\_o_|_o_/  "],
                ["\\..!..|..:../", " \\.:..|..:./ ", "  \\_o_|_o_/  ",
                 "\\..!..|..!../", " \\.:..|..:./ ", "  \\_o_|_o_/  ",
                 "\\..!..|..!../", " \\.!..|..!./ ", "  \\_o_|_o_/  ",
                 "\\..!..|..:../", " \\.:..|..:./ ", "  \\_O_|_O_/  "],
                ":1,3t$<CR>12G0forO;rO",
                [[":1,3t$", "copy the complete left-accent pose as the release scaffold"],
                 ["12G0forO;rO", "brighten both homologous base cells with one repeated search"]],
                alternatives=[
                    method("repeated character search", ":1,3t$<CR>12G0forO;rO", "find the first base cell and repeat that search for the second"),
                    method("row-scoped substitution", ":1,3t$<CR>12G:s/o/O/g<CR>", "replace only the two base cells on the copied row"),
                ],
                review_variants=[
                    step(["\\..*..|..+../", " \\.+..|..+. /", "  \\_x_|_x_/  ",
                          "\\..*..|..*../", " \\.+..|..+. /", "  \\_x_|_x_/  ",
                          "\\..*..|..*../", " \\.*..|..*. /", "  \\_x_|_x_/  "],
                         ["\\..*..|..+../", " \\.+..|..+. /", "  \\_x_|_x_/  ",
                          "\\..*..|..*../", " \\.+..|..+. /", "  \\_x_|_x_/  ",
                          "\\..*..|..*../", " \\.*..|..*. /", "  \\_x_|_x_/  ",
                          "\\..*..|..+../", " \\.+..|..+. /", "  \\_X_|_X_/  "],
                         ":1,3t$<CR>12G0fxrX;rX",
                         [["fx / ;", "brighten both changed base cells locally"]],
                         method_requirement=require_method(
                             "repeat a bounded base-cell search on changed art",
                             exact_any_of=[":1,3t$<CR>12G0fxrX;rX"])),
                    step(["/..O..|..x..\\", " / .x..|..x.\\ ", "  /_+_|_+_\\  ",
                          "/..O..|..O..\\", " / .x..|..x.\\ ", "  /_+_|_+_\\  ",
                          "/..O..|..O..\\", " / .O..|..O.\\ ", "  /_+_|_+_\\  "],
                         ["/..O..|..x..\\", " / .x..|..x.\\ ", "  /_+_|_+_\\  ",
                          "/..O..|..O..\\", " / .x..|..x.\\ ", "  /_+_|_+_\\  ",
                          "/..O..|..O..\\", " / .O..|..O.\\ ", "  /_+_|_+_\\  ",
                          "/..O..|..x..\\", " / .x..|..x.\\ ", "  /_#_|_#_\\  "],
                         ":1,3t$<CR>12G:s/+/\\#/g<CR>",
                         [[":s/+/\\#/g", "change only the copied alternate base row"]],
                         method_requirement=require_method(
                             "use a row-scoped changed-art base edit",
                             exact_any_of=[":1,3t$<CR>12G:s/+/\\#/g<CR>"])),
                ],
            ),
            step(
                ["\\..!..|..:../", " \\.:..|..:./ ", "  \\_o_|_o_/  ",
                 "\\..!..|..!../", " \\.:..|..:./ ", "  \\_o_|_o_/  ",
                 "\\..!..|..!../", " \\.!..|..!./ ", "  \\_o_|_o_/  ",
                 "\\..!..|..:../", " \\.:..|..:./ ", "  \\_O_|_O_/  "],
                ["\\..!..|..:../", " \\.:..|..:./ ", "  \\_o_|_o_/  ",
                 "\\..!..|..!../", " \\.:..|..:./ ", "  \\_o_|_o_/  ",
                 "\\..!..|..!../", " \\.!..|..!./ ", "  \\_o_|_o_/  ",
                 "\\..!..|..:../", " \\.:..|..:./ ", "  \\_O_|_O_/  ",
                 "\\..:..|..!../", " \\.:..|..:./ ", "  \\_o_|_o_/  "],
                ":1,3t$<CR>13G0t!lr:$T:hr!",
                [[":1,3t$", "copy the complete first accent as the return scaffold"],
                 ["13G0t!lr:$T:hr!", "move the acting accent from left to its hand-mirrored partner"]],
                method_requirement=require_method(
                    "author the opposite mirrored return with both t and T",
                    exact_any_of=[":1,3t$<CR>13G0t!lr:$T:hr!"]),
            ),
        ],
        "transfer": step(
            ["/..+..|..+..\\", " /.+..|..+.\\ ", "  /_x_|_x_\\  "],
            ["/..*..|..*..\\", " /.+..|..+.\\ ", "  /_x_|_x_\\  "],
            "0t+lr*$T+hr*",
            [["0t+lr*", "approach and replace the unfamiliar left joint"],
             ["$T+hr*", "approach and replace its right mirrored partner"]],
            method_requirement=require_method(
                "transfer forward and backward till motions to unfamiliar joints",
                exact_any_of=["0t+lr*$T+hr*"]),
        ),
        "transfer_alt": step(
            ["<..:..|..:..>", " <.:..|..:.> ", "  <_o_|_o_>  "],
            ["<..!..|..!..>", " <.:..|..:.> ", "  <_o_|_o_>  "],
            "0t:lr!$T:hr!",
            [["t: / T:", "approach both changed-shell joints from opposite directions"]],
            method_requirement=require_method(
                "transfer both till directions to the alternate shell",
                exact_any_of=["0t:lr!$T:hr!"]),
        ),
    },
    {
        "id": "M13", "title": "Texture pulse", "node": "S3/V13", "project": "texture-pulse",
        "skill": "WORD landmarks across separated texture clusters and a travelling material accent",
        "frame_rows": 3,
        "source_ref": "ascii-art-authoring §§5,10; Neovim help WORD, W, B, E",
        "meaning": "an accent travels from the centre texture cluster to the right, expands to three cluster edges, flashes, then exits left while the support rows stay registered",
        "first_reading": "the first cell of the centre punctuation cluster changes from . to ! while all three cluster widths and both support rows remain fixed",
        "principle": "treat whitespace-separated texture clusters as WORD landmarks, but replace cells in place so the animation does not collapse its fixed-width layout",
        "defect": "a lowercase word motion stops inside punctuation, a delete shifts every later cluster, or the pulse changes support rows that should remain temporal anchors",
        "basic": "use W to reach the next punctuation cluster and replace its first cell without changing row length",
        "scaled": "combine E, counted W, and B to address opposite cluster edges, then compare local repeated edits with a row-scoped material substitution",
        "steps": [
            step(
                ["..:: ..:: ..::", ".:::..|..:::.", "_____.|._____"],
                ["..:: !.:: ..::", ".:::..|..:::.", "_____.|._____"],
                "Wr!",
                [["W", "jump to the next whitespace-separated texture cluster"],
                 ["r!", "accent its first cell without moving either neighbouring cluster"]],
                method_requirement=require_method(
                    "reach the centre texture WORD with W and replace in place",
                    exact_any_of=["Wr!"]),
            ),
            step(
                ["..:: !.:: ..::", ".:::..|..:::.", "_____.|._____"],
                ["..:: !.:: ..::", ".:::..|..:::.", "_____.|._____",
                 "..:: ..:: !.::", ".:::..|..:::.", "_____.|._____"],
                "gg3yyGp4GWr.Wr!",
                [["gg3yyGp", "copy the complete centre-pulse pose"],
                 ["4GWr.Wr!", "clear the copied centre accent and advance it one WORD to the right"]],
                method_requirement=require_method(
                    "copy the pose and move the pulse between texture WORDs",
                    exact_any_of=["gg3yyGp4GWr.Wr!"]),
            ),
            step(
                ["..:: !.:: ..::", ".:::..|..:::.", "_____.|._____",
                 "..:: ..:: !.::", ".:::..|..:::.", "_____.|._____"],
                ["..:: !.:: ..::", ".:::..|..:::.", "_____.|._____",
                 "..:: ..:: !.::", ".:::..|..:::.", "_____.|._____",
                 "..:! !.:: ..:!", ".:::..|..:::.", "_____.|._____"],
                "4G3yyGp7GEr!2Wr.Er!2Br!",
                [["4G3yyGp", "copy the complete right-pulse pose as the expansion scaffold"],
                 ["7GEr!", "accent the end of the first texture WORD"],
                 ["2Wr.Er!", "clear the old right start and accent that WORD's far edge"],
                 ["2Br!", "return to the centre WORD and accent its first cell"]],
                method_requirement=require_method(
                    "address three texture edges with E, counted W, and B",
                    exact_any_of=["4G3yyGp7GEr!2Wr.Er!2Br!"]),
                review_variants=[
                    step(["--++ !-++ --++", "-+++--|--+++-", "_____-|-_____",
                          "--++ --++ x-++", "-+++--|--+++-", "_____-|-_____"],
                         ["--++ !-++ --++", "-+++--|--+++-", "_____-|-_____",
                          "--++ --++ x-++", "-+++--|--+++-", "_____-|-_____",
                          "--+! !-++ .-+!", "-+++--|--+++-", "_____-|-_____"],
                         "4G3yyGp7GEr!2Wr.Er!2Br!",
                         [["E / 2W / E / 2B", "address all three changed texture edges"]],
                         method_requirement=require_method(
                             "address the changed texture edges with E, W, and B",
                             exact_any_of=["4G3yyGp7GEr!2Wr.Er!2Br!"])),
                    step(["__.. !_.. __..", "_...__|__..._", "-----+|+-----",
                          "__.. __.. O_..", "_...__|__..._", "-----+|+-----"],
                         ["__.. !_.. __..", "_...__|__..._", "-----+|+-----",
                          "__.. __.. O_..", "_...__|__..._", "-----+|+-----",
                          "__.! !_.. __.!", "_...__|__..._", "-----+|+-----"],
                         "4G3yyGp7GEr!2Wr_Er!2Br!",
                         [["E / 2W / E / 2B", "address the alternate texture edges"]],
                         method_requirement=require_method(
                             "address the alternate texture edges with E, W, and B",
                             exact_any_of=["4G3yyGp7GEr!2Wr_Er!2Br!"])),
                ],
            ),
            step(
                ["..:: !.:: ..::", ".:::..|..:::.", "_____.|._____",
                 "..:: ..:: !.::", ".:::..|..:::.", "_____.|._____",
                 "..:! !.:: ..:!", ".:::..|..:::.", "_____.|._____"],
                ["..:: !.:: ..::", ".:::..|..:::.", "_____.|._____",
                 "..:: ..:: !.::", ".:::..|..:::.", "_____.|._____",
                 "..:! !.:: ..:!", ".:::..|..:::.", "_____.|._____",
                 "..:* *.:: ..:*", ".:::..|..:::.", "_____.|._____"],
                ":7,9t$<CR>10G:s/!/*/g<CR>",
                [[":7,9t$", "copy the complete expanded-pulse pose"],
                 ["10G:s/!/*/g", "change only its three acting texture cells into the flash material"]],
                alternatives=[
                    method("repeated landmark edits", ":7,9t$<CR>10G0f!r*;r*;r*", "find and replace each acting cell on the copied row"),
                    method("row-scoped material substitution", ":7,9t$<CR>10G:s/!/*/g<CR>", "replace the three acting cells only on the copied row"),
                ],
                review_variants=[
                    step(["--++ !-++ --++", "-+++--|--+++-", "_____-|-_____",
                          "--++ --++ x-++", "-+++--|--+++-", "_____-|-_____",
                          "--+! !-++ .-+!", "-+++--|--+++-", "_____-|-_____"],
                         ["--++ !-++ --++", "-+++--|--+++-", "_____-|-_____",
                          "--++ --++ x-++", "-+++--|--+++-", "_____-|-_____",
                          "--+! !-++ .-+!", "-+++--|--+++-", "_____-|-_____",
                          "--+# #-++ .-+#", "-+++--|--+++-", "_____-|-_____"],
                         ":7,9t$<CR>10G:s/!/#/g<CR>",
                         [[":s/!/#/g", "flash only the changed copied texture row"]],
                         method_requirement=require_method(
                             "use a row-scoped material flash on changed art",
                             exact_any_of=[":7,9t$<CR>10G:s/!/#/g<CR>"])),
                    step(["__.. !_.. __..", "_...__|__..._", "-----+|+-----",
                          "__.. __.. O_..", "_...__|__..._", "-----+|+-----",
                          "__.! !_.. __.!", "_...__|__..._", "-----+|+-----"],
                         ["__.. !_.. __..", "_...__|__..._", "-----+|+-----",
                          "__.. __.. O_..", "_...__|__..._", "-----+|+-----",
                          "__.! !_.. __.!", "_...__|__..._", "-----+|+-----",
                          "__.# #_.. __.#", "_...__|__..._", "-----+|+-----"],
                         ":7,9t$<CR>10G:s/!/#/g<CR>",
                         [[":s/!/#/g", "flash the alternate copied texture row"]],
                         method_requirement=require_method(
                             "use a row-scoped alternate material flash",
                             exact_any_of=[":7,9t$<CR>10G:s/!/#/g<CR>"])),
                ],
            ),
            step(
                ["..:: !.:: ..::", ".:::..|..:::.", "_____.|._____",
                 "..:: ..:: !.::", ".:::..|..:::.", "_____.|._____",
                 "..:! !.:: ..:!", ".:::..|..:::.", "_____.|._____",
                 "..:* *.:: ..:*", ".:::..|..:::.", "_____.|._____"],
                ["..:: !.:: ..::", ".:::..|..:::.", "_____.|._____",
                 "..:: ..:: !.::", ".:::..|..:::.", "_____.|._____",
                 "..:! !.:: ..:!", ".:::..|..:::.", "_____.|._____",
                 "..:* *.:: ..:*", ".:::..|..:::.", "_____.|._____",
                 "!.:: ..:: ..::", ".:::..|..:::.", "_____.|._____"],
                ":1,3t$<CR>13GWr.Br!",
                [[":1,3t$", "copy the complete centre-pulse pose as the loop exit scaffold"],
                 ["13GWr.Br!", "clear the centre start, move back one WORD, and place the exit accent on the left"]],
                method_requirement=require_method(
                    "move the return pulse from centre to left with W and B",
                    exact_any_of=[":1,3t$<CR>13GWr.Br!"]),
            ),
        ],
        "transfer": step(
            ["--:: --:: --::", "-:::--|--:::-", "=====-|-====="],
            ["--:: +-:: +-::", "-:::--|--:::-", "=====-|-====="],
            "2Wr+Br+",
            [["2Wr+", "reach and accent the third unfamiliar texture WORD"],
             ["Br+", "return to its centre partner and accent it"]],
            method_requirement=require_method(
                "transfer counted W and B across changed texture WORDs",
                exact_any_of=["2Wr+Br+"]),
        ),
        "transfer_alt": step(
            ["__.. __.. __..", "_...__|__..._", "-----+|+-----"],
            ["__.! __.. __.!", "_...__|__..._", "-----+|+-----"],
            "Er!2Er!",
            [["Er!", "accent the first unfamiliar WORD's far edge"],
             ["2Er!", "advance by WORD ends and accent the third far edge"]],
            method_requirement=require_method(
                "transfer counted E across alternate texture WORDs",
                exact_any_of=["Er!2Er!"]),
        ),
    },
    {
        "id": "M14", "title": "Variant palette", "node": "S5/V14",
        "project": "variant-palette", "frame_rows": 4,
        "skill": "paragraph frame objects, named glyph registers, and non-shifting palette replacement",
        "source_ref": "ascii-art-authoring §§1.7,2,3; Neovim help text-objects, quote_alpha, i_CTRL-R, virtual-replace-mode",
        "meaning": "three blank-line-separated face variants keep one silhouette while their registered eye glyph changes from the saved palette",
        "first_reading": "the first face keeps its three-row outline while only its eye changes from o to the palette glyph *",
        "principle": "keep variants in the file, treat each blank-line-separated frame as one object, and reuse a deliberate glyph vocabulary instead of retyping it from memory",
        "defect": "a put copies only one row, a register paste inserts and shifts the right wall, or a palette glyph is retyped inconsistently between variants",
        "basic": "yank one visible palette glyph into a named register and insert it through Replace mode over the acting cell",
        "scaled": "copy an entire paragraph frame with yap, navigate variants with }, and compare objectwise put with an addressed range copy",
        "steps": [
            step(
                ["/^\\  [*+]", "|o|       ", "\\_/       ", ""],
                ["/^\\  [*+]", "|*|       ", "\\_/       ", ""],
                "f*\"aylj0foR<C-r>a<Esc>",
                [["f*\"ayl", "store the visible star palette glyph in named register a"],
                 ["j0fo", "reach the acting eye without counting its column"],
                 ["R<C-r>a<Esc>", "replace the eye from register a without shifting the right wall"]],
                method_requirement=require_method(
                    "use named register a through Replace mode for the palette glyph",
                    exact_any_of=["f*\"aylj0foR<C-r>a<Esc>"]),
                review_variants=[
                    step(["/o\\  [#@]", "|.|       ", "\\_/       ", ""],
                         ["/o\\  [#@]", "|#|       ", "\\_/       ", ""],
                         "f#\"aylj0f.R<C-r>a<Esc>",
                         [["\"ayl / R<C-r>a", "retrieve the changed palette glyph without inserting a cell"]],
                         method_requirement=require_method(
                             "retrieve the changed palette through named register a",
                             exact_any_of=["f#\"aylj0f.R<C-r>a<Esc>"])),
                    step(["<^>  [x+]", "[o]       ", "-_-       ", ""],
                         ["<^>  [x+]", "[x]       ", "-_-       ", ""],
                         "fx\"aylj0foR<C-r>a<Esc>",
                         [["\"ayl / R<C-r>a", "reuse the alternate palette in a changed shell"]],
                         method_requirement=require_method(
                             "retrieve the alternate palette through named register a",
                             exact_any_of=["fx\"aylj0foR<C-r>a<Esc>"])),
                ],
            ),
            step(
                ["/^\\  [*+]", "|*|       ", "\\_/       ", ""],
                ["/^\\  [*+]", "|*|       ", "\\_/       ", "",
                 "/^\\  [*+]", "|*|       ", "\\_/       ", ""],
                "ggyapGp",
                [["ggyap", "yank the complete blank-line-separated first frame as one paragraph object"],
                 ["Gp", "put the complete frame after the existing paragraph"]],
                method_requirement=require_method(
                    "duplicate the complete paragraph frame with yap",
                    exact_any_of=["ggyapGp"]),
            ),
            step(
                ["/^\\  [*+]", "|*|       ", "\\_/       ", "",
                 "/^\\  [*+]", "|*|       ", "\\_/       ", ""],
                ["/^\\  [*+]", "|*|       ", "\\_/       ", "",
                 "/^\\  [*+]", "|+|       ", "\\_/       ", ""],
                "5Gf+\"aylj0f*R<C-r>a<Esc>",
                [["5Gf+\"ayl", "store the second visible palette glyph from the copied variant"],
                 ["j0f*R<C-r>a<Esc>", "replace only the copied eye from that register"]],
                method_requirement=require_method(
                    "change only the second variant through its named palette register",
                    exact_any_of=["5Gf+\"aylj0f*R<C-r>a<Esc>"]),
                review_variants=[
                    step(["/o\\ [#@]", "|#|      ", "\\_/      ", "",
                          "/o\\ [#@]", "|#|      ", "\\_/      ", ""],
                         ["/o\\ [#@]", "|#|      ", "\\_/      ", "",
                          "/o\\ [#@]", "|@|      ", "\\_/      ", ""],
                         "5Gf@\"aylj0f#R<C-r>a<Esc>",
                         [["\"ayl / R<C-r>a", "change only the copied unfamiliar eye"]],
                         method_requirement=require_method(
                             "retrieve the second changed-art palette glyph",
                             exact_any_of=["5Gf@\"aylj0f#R<C-r>a<Esc>"])),
                    step(["<^> [x+]", "[x]     ", "-_-     ", "",
                          "<^> [x+]", "[x]     ", "-_-     ", ""],
                         ["<^> [x+]", "[x]     ", "-_-     ", "",
                          "<^> [x+]", "[+]     ", "-_-     ", ""],
                         "5Gf+\"aylj0fxR<C-r>a<Esc>",
                         [["\"ayl / R<C-r>a", "change only the alternate copied eye"]],
                         method_requirement=require_method(
                             "retrieve the alternate second palette glyph",
                             exact_any_of=["5Gf+\"aylj0fxR<C-r>a<Esc>"])),
                ],
            ),
            step(
                ["/^\\  [*+]", "|*|       ", "\\_/       ", "",
                 "/^\\  [*+]", "|+|       ", "\\_/       ", ""],
                ["/^\\  [*+]", "|*|       ", "\\_/       ", "",
                 "/^\\  [*+]", "|+|       ", "\\_/       ", "",
                 "/^\\  [*+]", "|+|       ", "\\_/       ", ""],
                "5Gyapgg}jP",
                [["5Gyap", "yank the complete second variant as a paragraph object"],
                 ["gg}jP", "move to the next frame boundary and put the object as a complete third variant"]],
                alternatives=[
                    method("paragraph object copy", "5Gyapgg}jP", "copy the current blank-line-separated frame with yap and place it at a frame boundary with P"),
                    method("addressed four-line copy", ":5,8t$<CR>", "copy the exact three art rows plus their separator by address"),
                ],
                review_variants=[
                    step(["/o\\ [#@]", "|#|      ", "\\_/      ", "",
                          "/o\\ [#@]", "|@|      ", "\\_/      ", ""],
                         ["/o\\ [#@]", "|#|      ", "\\_/      ", "",
                          "/o\\ [#@]", "|@|      ", "\\_/      ", "",
                          "/o\\ [#@]", "|@|      ", "\\_/      ", ""],
                         "5Gyapgg}jP", [["yap / } / P", "copy and place the changed paragraph frame as an object"]],
                         method_requirement=require_method(
                             "copy the changed paragraph frame as an object",
                             exact_any_of=["5Gyapgg}jP"])),
                    step(["<^> [x+]", "[x]     ", "-_-     ", "",
                          "<^> [x+]", "[+]     ", "-_-     ", ""],
                         ["<^> [x+]", "[x]     ", "-_-     ", "",
                          "<^> [x+]", "[+]     ", "-_-     ", "",
                          "<^> [x+]", "[+]     ", "-_-     ", ""],
                         ":5,8t$<CR>", [[":5,8t$", "copy the alternate frame and its separator by range"]],
                         method_requirement=require_method(
                             "copy the alternate paragraph frame by exact range",
                             exact_any_of=[":5,8t$<CR>"])),
                ],
            ),
            step(
                ["/^\\  [*+]", "|*|       ", "\\_/       ", "",
                 "/^\\  [*+]", "|+|       ", "\\_/       ", "",
                 "/^\\  [*+]", "|+|       ", "\\_/       ", ""],
                ["/^\\  [*+]", "|*|       ", "\\_/       ", "",
                 "/^\\  [*+]", "|+|       ", "\\_/       ", "",
                 "/^\\  [*+]", "|*|       ", "\\_/       ", ""],
                "ggf*\"bylgg}}jj0f+R<C-r>b<Esc>",
                [["ggf*\"byl", "store the first eye material in register b"],
                 ["gg}}jj", "jump across two blank-line-separated frame objects to the third eye row"],
                 ["0f+R<C-r>b<Esc>", "replace only the third eye so the variant sequence returns to its first material"]],
                method_requirement=require_method(
                    "navigate paragraph frames and retrieve a named glyph register",
                    exact_any_of=["ggf*\"bylgg}}jj0f+R<C-r>b<Esc>"]),
                review_variants=[
                    step(["/o\\ [#@]", "|#|      ", "\\_/      ", "",
                          "/o\\ [#@]", "|@|      ", "\\_/      ", "",
                          "/o\\ [#@]", "|@|      ", "\\_/      ", ""],
                         ["/o\\ [#@]", "|#|      ", "\\_/      ", "",
                          "/o\\ [#@]", "|@|      ", "\\_/      ", "",
                          "/o\\ [#@]", "|#|      ", "\\_/      ", ""],
                         "ggf#\"bylgg}}jj0f@R<C-r>b<Esc>",
                         [["}} / R<C-r>b", "retrieve the first changed palette in the third frame"]],
                         method_requirement=require_method(
                             "navigate changed paragraph frames and retrieve register b",
                             exact_any_of=["ggf#\"bylgg}}jj0f@R<C-r>b<Esc>"])),
                    step(["<^> [x+]", "[x]     ", "-_-     ", "",
                          "<^> [x+]", "[+]     ", "-_-     ", "",
                          "<^> [x+]", "[+]     ", "-_-     ", ""],
                         ["<^> [x+]", "[x]     ", "-_-     ", "",
                          "<^> [x+]", "[+]     ", "-_-     ", "",
                          "<^> [x+]", "[x]     ", "-_-     ", ""],
                         "ggfx\"bylgg}}jj0f+R<C-r>b<Esc>",
                         [["}} / R<C-r>b", "retrieve the alternate first palette in the third frame"]],
                         method_requirement=require_method(
                             "navigate alternate paragraph frames and retrieve register b",
                             exact_any_of=["ggfx\"bylgg}}jj0f+R<C-r>b<Esc>"])),
                ],
            ),
        ],
        "transfer": step(
            ["/--\\ [xo]", "| .|      ", "\\__/      ", ""],
            ["/--\\ [xo]", "| x|      ", "\\__/      ", ""],
            "fx\"aylj0f.R<C-r>a<Esc>",
            [["fx\"ayl", "capture the unfamiliar x palette in register a"],
             ["j0f.R<C-r>a<Esc>", "replace the acting cell without shifting its wall"]],
            method_requirement=require_method(
                "transfer a named palette glyph through Replace mode",
                exact_any_of=["fx\"aylj0f.R<C-r>a<Esc>"]),
        ),
        "transfer_alt": step(
            ["<==> [@+]", "[ .]      ", "-__-      ", ""],
            ["<==> [@+]", "[ @]      ", "-__-      ", ""],
            "f@\"aylj0f.R<C-r>a<Esc>",
            [["f@\"ayl", "capture the alternate @ palette"],
             ["j0f.R<C-r>a<Esc>", "reuse it in the changed shell without insertion"]],
            method_requirement=require_method(
                "transfer the alternate named palette glyph through Replace mode",
                exact_any_of=["f@\"aylj0f.R<C-r>a<Esc>"]),
        ),
    },
    {
        "id": "M15", "title": "Texture ground", "node": "S7/V15",
        "project": "texture-ground", "frame_rows": 3,
        "skill": "dither, offset brick, isometric ground shadow, one-cell indentation, block edges, range edits, and reusable macros",
        "source_ref": "ascii-art-authoring §§3,4,6,8; Neovim help shiftwidth, >>, visual-block, v_b_A, :substitute, q, @",
        "meaning": "a three-frame ground treatment pans its brick layer, lightens its dither, gains an occluding edge, and settles without moving the angled shadow base",
        "first_reading": "the brick row shifts exactly one cell while the dither and angled ground-shadow row remain registered",
        "principle": "texture is a material system: offset repeated motifs by measured cells, lighten dither by erasing density, and keep the shadow or isometric base as a stable depth cue",
        "defect": "the brick offset is more than one cell, a block append pads or misses a selected row, a broad substitute changes the shadow, or a macro alters support glyphs outside the acting texture row",
        "basic": "set one-cell indentation explicitly and shift only the brick material row",
        "scaled": "compare a blockwise end append with a bounded range substitute, then record and replay one landmark replacement across repeated dither cells",
        "steps": [
            step(
                ["..::..::..", "[]__[]__[]", "\\________/"],
                ["..::..::..", " []__[]__[]", "\\________/"],
                "j:set shiftwidth=1<CR>>>",
                [["j", "select only the brick material row"],
                 [":set shiftwidth=1", "declare that one indentation step equals one animation cell"],
                 [">>", "offset that row by exactly one cell without redrawing its motifs"]],
                method_requirement=require_method(
                    "use explicit shiftwidth=1 and >> for the one-cell brick offset",
                    exact_any_of=["j:set shiftwidth=1<CR>>>"]),
                review_variants=[
                    step(["!!::!!::!!", "<>__<>__<>", "\\========/"],
                         ["!!::!!::!!", " <>__<>__<>", "\\========/"],
                         "j:set shiftwidth=1<CR>>>",
                         [["shiftwidth=1 / >>", "offset the unfamiliar brick band by one cell"]],
                         method_requirement=require_method(
                             "repeat the one-cell offset on changed texture",
                             exact_any_of=["j:set shiftwidth=1<CR>>>"])),
                    step(["++..++..++", "{}__{}__{}", "\\~~~~~~~~/"],
                         ["++..++..++", " {}__{}__{}", "\\~~~~~~~~/"],
                         "j:set shiftwidth=1<CR>>>",
                         [["shiftwidth=1 / >>", "offset the alternate material band by one cell"]],
                         method_requirement=require_method(
                             "repeat the alternate one-cell material offset",
                             exact_any_of=["j:set shiftwidth=1<CR>>>"])),
                ],
            ),
            step(
                ["..::..::..", " []__[]__[]", "\\________/"],
                ["..::..::..", " []__[]__[]", "\\________/",
                 "..::..::..", " []__[]__[]", "\\________/"],
                "gg3yyGp",
                [["gg3yy", "yank the complete three-row material frame"],
                 ["Gp", "append its registered copy as the next working frame"]],
                method_requirement=require_method(
                    "copy all three material rows as one frame",
                    exact_any_of=["gg3yyGp"]),
            ),
            step(
                ["..::..::..", " []__[]__[]", "\\________/",
                 "..::..::..", " []__[]__[]", "\\________/"],
                ["..::..::..", " []__[]__[]", "\\________/",
                 "..........", "  []__[]__[]", "\\________/"],
                ":set shiftwidth=1<CR>5G>>:4s/:/./g<CR>",
                [[":set shiftwidth=1 / 5G>>", "move only the copied brick row one more cell"],
                 [":4s/:/./g", "lighten the copied dither row by replacing dense marks with sparse dots"]],
                method_requirement=require_method(
                    "combine a one-cell brick shift with a row-bounded dither lightening",
                    exact_any_of=[":set shiftwidth=1<CR>5G>>:4s/:/./g<CR>"]),
                review_variants=[
                    step(["!!::!!::!!", " <>__<>__<>", "\\========/",
                          "!!::!!::!!", " <>__<>__<>", "\\========/"],
                         ["!!::!!::!!", " <>__<>__<>", "\\========/",
                          "!!..!!..!!", "  <>__<>__<>", "\\========/"],
                         ":set shiftwidth=1<CR>5G>>:4s/:/./g<CR>",
                         [[">> / :4s/:/./g", "offset and lighten only the copied unfamiliar materials"]],
                         method_requirement=require_method(
                             "repeat offset plus bounded lightening on changed texture",
                             exact_any_of=[":set shiftwidth=1<CR>5G>>:4s/:/./g<CR>"])),
                    step(["++::++::++", " {}__{}__{}", "\\~~~~~~~~/",
                          "++::++::++", " {}__{}__{}", "\\~~~~~~~~/"],
                         ["++::++::++", " {}__{}__{}", "\\~~~~~~~~/",
                          "++..++..++", "  {}__{}__{}", "\\~~~~~~~~/"],
                         ":set shiftwidth=1<CR>5G>>:4s/:/./g<CR>",
                         [[">> / :4s/:/./g", "offset and lighten only the alternate copied materials"]],
                         method_requirement=require_method(
                             "repeat alternate offset plus bounded lightening",
                             exact_any_of=[":set shiftwidth=1<CR>5G>>:4s/:/./g<CR>"])),
                ],
            ),
            step(
                ["..::..::..", " []__[]__[]", "\\________/",
                 "..........", "  []__[]__[]", "\\________/"],
                ["..::..::..", " []__[]__[]", "\\________/",
                 "..........|", "  []__[]__[]|", "\\________/|"],
                "4G0<C-v>2j$A|<Esc>",
                [["4G0<C-v>2j$A|<Esc>", "append one occluding edge at the true end of every row in the copied frame"]],
                alternatives=[
                    method("blockwise end append", "4G0<C-v>2j$A|<Esc>", "select the three frame rows and append at each row end"),
                    method("bounded range append", ":4,6s/$/|/<CR>", "append the same edge only to the owned three-line frame range"),
                ],
                review_variants=[
                    step(["!!::!!::!!", " <>__<>__<>", "\\========/",
                          "!!..!!..!!", "  <>__<>__<>", "\\========/"],
                         ["!!::!!::!!", " <>__<>__<>", "\\========/",
                          "!!..!!..!!|", "  <>__<>__<>|", "\\========/|"],
                         "4G0<C-v>2j$A|<Esc>",
                         [["blockwise $A", "append at each changed row's true end"]],
                         method_requirement=require_method(
                             "use blockwise end append on the changed frame",
                             exact_any_of=["4G0<C-v>2j$A|<Esc>"])),
                    step(["++::++::++", " {}__{}__{}", "\\~~~~~~~~/",
                          "++..++..++", "  {}__{}__{}", "\\~~~~~~~~/"],
                         ["++::++::++", " {}__{}__{}", "\\~~~~~~~~/",
                          "++..++..++|", "  {}__{}__{}|", "\\~~~~~~~~/|"],
                         ":4,6s/$/|/<CR>",
                         [[":4,6s/$/|/", "append only inside the alternate owned frame range"]],
                         method_requirement=require_method(
                             "use a bounded range append on the alternate frame",
                             exact_any_of=[":4,6s/$/|/<CR>"])),
                ],
            ),
            step(
                ["..::..::..", " []__[]__[]", "\\________/",
                 "..........|", "  []__[]__[]|", "\\________/|"],
                ["..::..::..", " []__[]__[]", "\\________/",
                 "..........|", "  []__[]__[]|", "\\________/|",
                 "..........", " []__[]__[]", "\\________/"],
                ":1,3t$<CR>7G0qqf:r.q3@q",
                [[":1,3t$", "append the original registered material frame as the settle scaffold"],
                 ["7G0qqf:r.q", "record one landmark-driven colon-to-dot lightening in register q"],
                 ["3@q", "replay that exact texture edit at the three remaining dither landmarks"]],
                method_requirement=require_method(
                    "record and replay the dither-lightening macro across four landmarks",
                    exact_any_of=[":1,3t$<CR>7G0qqf:r.q3@q"]),
                review_variants=[
                    step(["!!::!!::!!", " <>__<>__<>", "\\========/",
                          "!!..!!..!!|", "  <>__<>__<>|", "\\========/|"],
                         ["!!::!!::!!", " <>__<>__<>", "\\========/",
                          "!!..!!..!!|", "  <>__<>__<>|", "\\========/|",
                          "!!..!!..!!", " <>__<>__<>", "\\========/"],
                         ":1,3t$<CR>7G0qqf:r.q3@q",
                         [["qq ... q / 3@q", "record once and replay across the changed dither row"]],
                         method_requirement=require_method(
                             "replay the dither macro on changed texture",
                             exact_any_of=[":1,3t$<CR>7G0qqf:r.q3@q"])),
                    step(["++::++::++", " {}__{}__{}", "\\~~~~~~~~/",
                          "++..++..++|", "  {}__{}__{}|", "\\~~~~~~~~/|"],
                         ["++::++::++", " {}__{}__{}", "\\~~~~~~~~/",
                          "++..++..++|", "  {}__{}__{}|", "\\~~~~~~~~/|",
                          "++..++..++", " {}__{}__{}", "\\~~~~~~~~/"],
                         ":1,3t$<CR>7G0qqf:r.q3@q",
                         [["qq ... q / 3@q", "record once and replay across the alternate dither row"]],
                         method_requirement=require_method(
                             "replay the macro on alternate texture",
                             exact_any_of=[":1,3t$<CR>7G0qqf:r.q3@q"])),
                ],
            ),
        ],
        "transfer": step(
            ["!!::!!::!!", "<>__<>__<>", "\\========/"],
            ["!!::!!::!!", " <>__<>__<>", "\\========/"],
            "j:set shiftwidth=1<CR>>>",
            [["shiftwidth=1 / >>", "move the unfamiliar repeated material exactly one cell"]],
            method_requirement=require_method(
                "transfer the explicit one-cell material offset",
                exact_any_of=["j:set shiftwidth=1<CR>>>"]),
        ),
        "transfer_alt": step(
            ["++..++..++", "{}__{}__{}", "\\~~~~~~~~/"],
            ["++..++..++", " {}__{}__{}", "\\~~~~~~~~/"],
            "j:set shiftwidth=1<CR>>>",
            [["shiftwidth=1 / >>", "move the alternate repeated material exactly one cell"]],
            method_requirement=require_method(
                "transfer the alternate one-cell material offset",
                exact_any_of=["j:set shiftwidth=1<CR>>>"]),
        ),
    },
    {
        "id": "M16", "title": "Key-pose plan", "node": "A0/V16",
        "project": "key-pose-plan", "frame_rows": 5, "labels_steps": [1, 2, 4, 5, 6, 8],
        "skill": "reference intake, size tests, written frame plans, saved-plate import, addressed copy/move, and numeric frame labels",
        "source_ref": "ascii-art-authoring §§2,7.1; archived animation workflow transcript Part 1 00:52:45–01:01:05; Neovim help :read, :copy, :move, CTRL-A",
        "meaning": "one approved small key pose becomes a written multi-block plan whose frame numbers can be copied, incremented, and reordered without retyping the art",
        "first_reading": "the small three-row pose is already readable at playback size, while its F01 and T08 FPS lines state frame identity and timing before in-betweening begins",
        "principle": "collect a reference, test the smallest readable key pose, write timing and frame intent down, then preserve that approved plate while planning later poses",
        "defect": "a copied plan block loses an art row, two blocks retain the same frame number, a move cuts through a five-line plate, or an imported plate comes from unsaved buffer state instead of the named source",
        "basic": "increment a numeric frame label in place with CTRL-A while the pose and timing line remain unchanged",
        "scaled": "read a saved plate, copy complete five-line plan blocks by address, and compare addressed move with a linewise delete-and-put reorder",
        "steps": [
            step(
                ["   o   ", "  /|\\  ", "  / \\  ", "F00 KEY", "T08 FPS"],
                ["   o   ", "  /|\\  ", "  / \\  ", "F01 KEY", "T08 FPS"],
                "Gk0f0<C-a>",
                [["Gk", "reach the frame-label line without touching the approved small pose"],
                 ["0f1<C-a>", "increment the numeric label in place while preserving its zero padding"]],
                method_requirement=require_method(
                    "increment the written frame number with CTRL-A",
                    exact_any_of=["Gk0f0<C-a>"]),
                review_variants=[
                    step(["   *   ", "  /|\\  ", "  / \\  ", "F03 KEY", "T12 FPS"],
                         ["   *   ", "  /|\\  ", "  / \\  ", "F04 KEY", "T12 FPS"],
                         "Gk0f3<C-a>",
                         [["CTRL-A", "increment the changed plan label without retyping it"]],
                         method_requirement=require_method(
                             "increment a changed written frame number",
                             exact_any_of=["Gk0f3<C-a>"])),
                    step(["   +   ", "  <|>  ", "  / \\  ", "F07 KEY", "T06 FPS"],
                         ["   +   ", "  <|>  ", "  / \\  ", "F08 KEY", "T06 FPS"],
                         "Gk0f7<C-a>",
                         [["CTRL-A", "increment the alternate plan label in place"]],
                         method_requirement=require_method(
                             "increment an alternate written frame number",
                             exact_any_of=["Gk0f7<C-a>"])),
                ],
            ),
            step(
                ["   o   ", "  /|\\  ", "  / \\  ", "F01 KEY", "T08 FPS"],
                ["   o   ", "  /|\\  ", "  / \\  ", "F01 KEY", "T08 FPS",
                 "   o   ", "  /|\\  ", "  / \\  ", "F02 KEY", "T08 FPS"],
                "G:read %<CR>9G0f1<C-a>",
                [["G:read %", "read the saved planning plate into the buffer as a second complete block"],
                 ["9G0f1<C-a>", "give the imported copy its next frame number without retyping the label"]],
                method_requirement=require_method(
                    "read the saved plate and increment the imported frame label",
                    exact_any_of=["G:read %<CR>9G0f1<C-a>"]),
                review_variants=[
                    step(["   *   ", "  /|\\  ", "  / \\  ", "F03 KEY", "T12 FPS"],
                         ["   *   ", "  /|\\  ", "  / \\  ", "F03 KEY", "T12 FPS",
                          "   *   ", "  /|\\  ", "  / \\  ", "F04 KEY", "T12 FPS"],
                         "G:read %<CR>9G0f3<C-a>",
                         [[":read % / CTRL-A", "import and renumber the changed saved plate"]],
                         method_requirement=require_method(
                             "read and renumber a changed saved plate",
                             exact_any_of=["G:read %<CR>9G0f3<C-a>"])),
                    step(["   +   ", "  <|>  ", "  / \\  ", "F07 KEY", "T06 FPS"],
                         ["   +   ", "  <|>  ", "  / \\  ", "F07 KEY", "T06 FPS",
                          "   +   ", "  <|>  ", "  / \\  ", "F08 KEY", "T06 FPS"],
                         "G:read %<CR>9G0f7<C-a>",
                         [[":read % / CTRL-A", "import and renumber the alternate saved plate"]],
                         method_requirement=require_method(
                             "read and renumber an alternate saved plate",
                             exact_any_of=["G:read %<CR>9G0f7<C-a>"])),
                ],
            ),
            step(
                ["   o   ", "  /|\\  ", "  / \\  ", "F01 KEY", "T08 FPS",
                 "   o   ", "  /|\\  ", "  / \\  ", "F02 KEY", "T08 FPS"],
                ["   o   ", "  /|\\  ", "  / \\  ", "F01 KEY", "T08 FPS",
                 "   o   ", "  /|\\  ", "  / \\  ", "F02 KEY", "T08 FPS",
                 "   o   ", "  /|\\  ", "  / \\  ", "F03 KEY", "T08 FPS"],
                ":1,5t$<CR>14G0f12<C-a>",
                [[":1,5t$", "copy the complete approved five-line plate by its written boundary"],
                 ["14G0f12<C-a>", "advance the copied F01 label by two so it becomes F03"]],
                method_requirement=require_method(
                    "copy a complete plan block and count-increment its frame label",
                    exact_any_of=[":1,5t$<CR>14G0f12<C-a>"]),
                review_variants=[
                    step(["   *   ", "  /|\\  ", "  / \\  ", "F03 KEY", "T12 FPS",
                          "   *   ", "  /|\\  ", "  / \\  ", "F04 KEY", "T12 FPS"],
                         ["   *   ", "  /|\\  ", "  / \\  ", "F03 KEY", "T12 FPS",
                          "   *   ", "  /|\\  ", "  / \\  ", "F04 KEY", "T12 FPS",
                          "   *   ", "  /|\\  ", "  / \\  ", "F05 KEY", "T12 FPS"],
                         ":1,5t$<CR>14G0f32<C-a>",
                         [[":t / counted CTRL-A", "copy and advance the changed plan block by two"]],
                         method_requirement=require_method(
                             "copy and count-increment a changed plan block",
                             exact_any_of=[":1,5t$<CR>14G0f32<C-a>"])),
                    step(["   +   ", "  <|>  ", "  / \\  ", "F07 KEY", "T06 FPS",
                          "   +   ", "  <|>  ", "  / \\  ", "F08 KEY", "T06 FPS"],
                         ["   +   ", "  <|>  ", "  / \\  ", "F07 KEY", "T06 FPS",
                          "   +   ", "  <|>  ", "  / \\  ", "F08 KEY", "T06 FPS",
                          "   +   ", "  <|>  ", "  / \\  ", "F09 KEY", "T06 FPS"],
                         ":1,5t$<CR>14G0f72<C-a>",
                         [[":t / counted CTRL-A", "copy and advance the alternate plan block by two"]],
                         method_requirement=require_method(
                             "copy and count-increment an alternate plan block",
                             exact_any_of=[":1,5t$<CR>14G0f72<C-a>"])),
                ],
            ),
            step(
                ["   o   ", "  /|\\  ", "  / \\  ", "F01 KEY", "T08 FPS",
                 "   o   ", "  /|\\  ", "  / \\  ", "F02 KEY", "T08 FPS",
                 "   o   ", "  /|\\  ", "  / \\  ", "F03 KEY", "T08 FPS"],
                ["   o   ", "  /|\\  ", "  / \\  ", "F02 KEY", "T08 FPS",
                 "   o   ", "  /|\\  ", "  / \\  ", "F01 KEY", "T08 FPS",
                 "   o   ", "  /|\\  ", "  / \\  ", "F03 KEY", "T08 FPS"],
                ":6,10m0<CR>",
                [[":6,10m0", "move exactly the second complete planning block before the first"]],
                alternatives=[
                    method("addressed plan-block move", ":6,10m0<CR>", "move the verified five-line block directly by range"),
                    method("linewise delete and put", "6GV4jdggP", "select the same five complete lines, delete them, and put them before line one"),
                ],
                review_variants=[
                    step(["   *   ", "  /|\\  ", "  / \\  ", "F03 KEY", "T12 FPS",
                          "   *   ", "  /|\\  ", "  / \\  ", "F04 KEY", "T12 FPS",
                          "   *   ", "  /|\\  ", "  / \\  ", "F05 KEY", "T12 FPS"],
                         ["   *   ", "  /|\\  ", "  / \\  ", "F04 KEY", "T12 FPS",
                          "   *   ", "  /|\\  ", "  / \\  ", "F03 KEY", "T12 FPS",
                          "   *   ", "  /|\\  ", "  / \\  ", "F05 KEY", "T12 FPS"],
                         ":6,10m0<CR>",
                         [[":m", "move the changed complete plan block by exact range"]],
                         method_requirement=require_method(
                             "use addressed move on changed planning blocks",
                             exact_any_of=[":6,10m0<CR>"])),
                    step(["   +   ", "  <|>  ", "  / \\  ", "F07 KEY", "T06 FPS",
                          "   +   ", "  <|>  ", "  / \\  ", "F08 KEY", "T06 FPS",
                          "   +   ", "  <|>  ", "  / \\  ", "F09 KEY", "T06 FPS"],
                         ["   +   ", "  <|>  ", "  / \\  ", "F08 KEY", "T06 FPS",
                          "   +   ", "  <|>  ", "  / \\  ", "F07 KEY", "T06 FPS",
                          "   +   ", "  <|>  ", "  / \\  ", "F09 KEY", "T06 FPS"],
                         "6GV4jdggP",
                         [["V / d / P", "move the alternate complete block with a linewise selection"]],
                         method_requirement=require_method(
                             "use linewise delete-and-put on alternate planning blocks",
                             exact_any_of=["6GV4jdggP"])),
                ],
            ),
            step(
                ["   o   ", "  /|\\  ", "  / \\  ", "F02 KEY", "T08 FPS",
                 "   o   ", "  /|\\  ", "  / \\  ", "F01 KEY", "T08 FPS",
                 "   o   ", "  /|\\  ", "  / \\  ", "F03 KEY", "T08 FPS"],
                ["   o   ", "  /|\\  ", "  / \\  ", "F02 KEY", "T08 FPS",
                 "   o   ", "  /|\\  ", "  / \\  ", "F01 KEY", "T08 FPS",
                 "   o   ", "  /|\\  ", "  / \\  ", "F03 KEY", "T08 FPS",
                 "   o   ", "  /|\\  ", "  / \\  ", "F04 KEY", "T08 FPS"],
                ":1,5t$<CR>19G0f22<C-a>",
                [[":1,5t$", "copy the current primary key-pose plan as the fourth planning block"],
                 ["19G0f22<C-a>", "advance its F02 label by two to create F04"]],
                method_requirement=require_method(
                    "append a complete key-pose plan and count-increment the new label",
                    exact_any_of=[":1,5t$<CR>19G0f22<C-a>"]),
                review_variants=[
                    step(["   *   ", "  /|\\  ", "  / \\  ", "F04 KEY", "T12 FPS",
                          "   *   ", "  /|\\  ", "  / \\  ", "F03 KEY", "T12 FPS",
                          "   *   ", "  /|\\  ", "  / \\  ", "F05 KEY", "T12 FPS"],
                         ["   *   ", "  /|\\  ", "  / \\  ", "F04 KEY", "T12 FPS",
                          "   *   ", "  /|\\  ", "  / \\  ", "F03 KEY", "T12 FPS",
                          "   *   ", "  /|\\  ", "  / \\  ", "F05 KEY", "T12 FPS",
                          "   *   ", "  /|\\  ", "  / \\  ", "F06 KEY", "T12 FPS"],
                         ":1,5t$<CR>19G0f42<C-a>",
                         [[":t / counted CTRL-A", "append and renumber the changed fourth plan block"]],
                         method_requirement=require_method(
                             "append and renumber a changed fourth plan block",
                             exact_any_of=[":1,5t$<CR>19G0f42<C-a>"])),
                    step(["   +   ", "  <|>  ", "  / \\  ", "F08 KEY", "T06 FPS",
                          "   +   ", "  <|>  ", "  / \\  ", "F07 KEY", "T06 FPS",
                          "   +   ", "  <|>  ", "  / \\  ", "F09 KEY", "T06 FPS"],
                         ["   +   ", "  <|>  ", "  / \\  ", "F08 KEY", "T06 FPS",
                          "   +   ", "  <|>  ", "  / \\  ", "F07 KEY", "T06 FPS",
                          "   +   ", "  <|>  ", "  / \\  ", "F09 KEY", "T06 FPS",
                          "   +   ", "  <|>  ", "  / \\  ", "F10 KEY", "T06 FPS"],
                         ":1,5t$<CR>19G0f82<C-a>",
                         [[":t / counted CTRL-A", "append and renumber the alternate fourth plan block"]],
                         method_requirement=require_method(
                             "append and renumber an alternate fourth plan block",
                             exact_any_of=[":1,5t$<CR>19G0f82<C-a>"])),
                ],
            ),
        ],
        "transfer": step(
            ["   *   ", "  /|\\  ", "  / \\  ", "F03 KEY", "T12 FPS"],
            ["   *   ", "  /|\\  ", "  / \\  ", "F04 KEY", "T12 FPS"],
            "Gk0f3<C-a>",
            [["CTRL-A", "advance the unfamiliar reference plate's written frame number"]],
            method_requirement=require_method(
                "transfer numeric frame-label increment to a changed plan",
                exact_any_of=["Gk0f3<C-a>"]),
        ),
        "transfer_alt": step(
            ["   +   ", "  <|>  ", "  / \\  ", "F07 KEY", "T06 FPS"],
            ["   +   ", "  <|>  ", "  / \\  ", "F08 KEY", "T06 FPS"],
            "Gk0f7<C-a>",
            [["CTRL-A", "advance the alternate plan's written frame number"]],
            method_requirement=require_method(
                "transfer numeric increment to the alternate plan",
                exact_any_of=["Gk0f7<C-a>"]),
        ),
    },
    {
        "id": "M17", "title": "Coherent anchors", "node": "A3/V17",
        "project": "coherent-anchors", "frame_rows": 3,
        "skill": "unchanged-glyph coherence across frames with search repeat, dot repeat, :global normal, and recorded macros",
        "source_ref": "ascii-art-authoring §§7.3,7.4,8.1; Neovim help /, n, ., :global, :normal, q, @",
        "meaning": "four changing shell poses keep one eye material coherent until an intentional strip-wide palette pass changes that homologous cell in every frame",
        "first_reading": "the shells change pose while the eye is the same semantic anchor in every frame; the first pass corrects only those homologous eye cells",
        "principle": "unchanged glyphs are temporal anchors: batch-edit only a proven homologous landmark, then inspect every frame for collateral changes before playback",
        "defect": "one frame keeps the old eye, a repeat lands on contour punctuation, :global selects an unrelated line, or a macro wraps beyond the owned landmark count",
        "basic": "replace the first searched eye and use n plus dot to repeat the exact edit at the next frame landmarks",
        "scaled": "compare search-and-dot with :global normal, then record a search-bearing macro and replay it across a known number of frame anchors",
        "steps": [
            step(
                [" /^\\ ", "|x|", "/_\\",
                 " /-\\ ", "|x|", "\\_/",
                 " \\^/ ", "|x|", "/_\\"],
                [" /^\\ ", "|o|", "/_\\",
                 " /-\\ ", "|o|", "\\_/",
                 " \\^/ ", "|o|", "/_\\"],
                "/x<CR>ron.n.",
                [["/x", "find the first homologous eye landmark without using a stored column"],
                 ["ro", "correct the first eye in place"],
                 ["n. / n.", "move to each next searched eye and repeat the same replacement"]],
                method_requirement=require_method(
                    "use search repeat plus dot at all three eye anchors",
                    exact_any_of=["/x<CR>ron.n."]),
                review_variants=[
                    step([" /~\\ ", "[x]", "\\_/",
                          " <^> ", "[x]", "-_-",
                          " \\~/ ", "[x]", "/_\\"],
                         [" /~\\ ", "[o]", "\\_/",
                          " <^> ", "[o]", "-_-",
                          " \\~/ ", "[o]", "/_\\"],
                         "/x<CR>ron.n.",
                         [["/ / n / .", "repeat the correction at all changed shell anchors"]],
                         method_requirement=require_method(
                             "use n plus dot on changed frame anchors",
                             exact_any_of=["/x<CR>ron.n."])),
                    step([" /+\\ ", "<x>", "\\-_/",
                          " /^\\ ", "<x>", "/__\\",
                          " \\+/ ", "<x>", "/-\\"],
                         [" /+\\ ", "<o>", "\\-_/",
                          " /^\\ ", "<o>", "/__\\",
                          " \\+/ ", "<o>", "/-\\"],
                         "/x<CR>ron.n.",
                         [["/ / n / .", "repeat the alternate anchor correction without contour edits"]],
                         method_requirement=require_method(
                             "use n plus dot on alternate frame anchors",
                             exact_any_of=["/x<CR>ron.n."])),
                ],
            ),
            step(
                [" /^\\ ", "|o|", "/_\\",
                 " /-\\ ", "|o|", "\\_/",
                 " \\^/ ", "|o|", "/_\\"],
                [" /^\\ ", "|o|", "/_\\",
                 " /-\\ ", "|o|", "\\_/",
                 " \\^/ ", "|o|", "/_\\",
                 " \\^/ ", "|o|", "/_\\"],
                "7G3yyGp",
                [["7G3yy", "yank the complete third shell pose"],
                 ["Gp", "append it as the working scaffold for a fourth pose"]],
                method_requirement=require_method(
                    "copy the complete three-row pose scaffold",
                    exact_any_of=["7G3yyGp"]),
            ),
            step(
                [" /^\\ ", "|o|", "/_\\",
                 " /-\\ ", "|o|", "\\_/",
                 " \\^/ ", "|o|", "/_\\",
                 " \\^/ ", "|o|", "/_\\"],
                [" /^\\ ", "|o|", "/_\\",
                 " /-\\ ", "|o|", "\\_/",
                 " \\^/ ", "|o|", "/_\\",
                 " \\-/ ", "|o|", "/-\\"],
                "10G0f^r-2j0f_r-",
                [["10G0f^r-", "change only the copied upper contour's acting joint"],
                 ["2j0f_r-", "change only its lower material while leaving the eye anchor untouched"]],
                method_requirement=require_method(
                    "develop the fourth shell without editing its coherent eye",
                    exact_any_of=["10G0f^r-2j0f_r-"]),
            ),
            step(
                [" /^\\ ", "|o|", "/_\\",
                 " /-\\ ", "|o|", "\\_/",
                 " \\^/ ", "|o|", "/_\\",
                 " \\-/ ", "|o|", "/-\\"],
                [" /^\\ ", "|*|", "/_\\",
                 " /-\\ ", "|*|", "\\_/",
                 " \\^/ ", "|*|", "/_\\",
                 " \\-/ ", "|*|", "/-\\"],
                "/o<CR>r*n.n.n.",
                [["/o then r*", "change the first coherent eye material"],
                 ["n. three times", "repeat only at the remaining searched eye anchors"]],
                alternatives=[
                    method("search repeat plus dot", "/o<CR>r*n.n.n.", "repeat one verified replacement at the next three eye matches"),
                    method("global normal pass", ":g/o/normal! 0for*<CR>", "run one bounded Normal-mode eye replacement on every line selected by the eye pattern"),
                ],
                review_variants=[
                    step([" /~\\ ", "[o]", "\\_/",
                          " <^> ", "[o]", "-_-",
                          " \\~/ ", "[o]", "/_\\",
                          " <- > ", "[o]", "/-\\"],
                         [" /~\\ ", "[*]", "\\_/",
                          " <^> ", "[*]", "-_-",
                          " \\~/ ", "[*]", "/_\\",
                          " <- > ", "[*]", "/-\\"],
                         "/o<CR>r*n.n.n.",
                         [["/ / n / .", "change all four changed-art anchors by search repeat"]],
                         method_requirement=require_method(
                             "use search repeat plus dot on four changed anchors",
                             exact_any_of=["/o<CR>r*n.n.n."])),
                    step([" /+\\ ", "<o>", "\\-_/",
                          " /^\\ ", "<o>", "/__\\",
                          " \\+/ ", "<o>", "/-\\",
                          " \\--/ ", "<o>", "\\__/"],
                         [" /+\\ ", "<*>", "\\-_/",
                          " /^\\ ", "<*>", "/__\\",
                          " \\+/ ", "<*>", "/-\\",
                          " \\--/ ", "<*>", "\\__/"],
                         ":g/o/normal! 0for*<CR>",
                         [[":g / normal", "select only alternate eye rows and replace their anchor"]],
                         method_requirement=require_method(
                             "use global normal on alternate coherent anchors",
                             exact_any_of=[":g/o/normal! 0for*<CR>"])),
                ],
            ),
            step(
                [" /^\\ ", "|*|", "/_\\",
                 " /-\\ ", "|*|", "\\_/",
                 " \\^/ ", "|*|", "/_\\",
                 " \\-/ ", "|*|", "/-\\"],
                [" /^\\ ", "|+|", "/_\\",
                 " /-\\ ", "|+|", "\\_/",
                 " \\^/ ", "|+|", "/_\\",
                 " \\-/ ", "|+|", "/-\\"],
                "/\\*<CR>qqr+nq3@q",
                [["/\\*", "find the first literal star eye anchor"],
                 ["qqr+nq", "record replacement plus search for the next homologous anchor"],
                 ["3@q", "replay the search-bearing macro at the three remaining frames"]],
                method_requirement=require_method(
                    "record and replay a search-bearing macro across four frame anchors",
                    exact_any_of=["/\\*<CR>qqr+nq3@q"]),
                review_variants=[
                    step([" /~\\ ", "[!]", "\\_/",
                          " <^> ", "[!]", "-_-",
                          " \\~/ ", "[!]", "/_\\",
                          " <- > ", "[!]", "/-\\"],
                         [" /~\\ ", "[:]", "\\_/",
                          " <^> ", "[:]", "-_-",
                          " \\~/ ", "[:]", "/_\\",
                          " <- > ", "[:]", "/-\\"],
                         "/!<CR>qqr:nq3@q",
                         [["q / @q", "record and replay the changed anchor traversal"]],
                         method_requirement=require_method(
                             "replay a search-bearing macro on changed anchors",
                             exact_any_of=["/!<CR>qqr:nq3@q"])),
                    step([" /+\\ ", "<o>", "\\-_/",
                          " /^\\ ", "<o>", "/__\\",
                          " \\+/ ", "<o>", "/-\\",
                          " \\--/ ", "<o>", "\\__/"],
                         [" /+\\ ", "<*>", "\\-_/",
                          " /^\\ ", "<*>", "/__\\",
                          " \\+/ ", "<*>", "/-\\",
                          " \\--/ ", "<*>", "\\__/"],
                         "/o<CR>qqr*nq3@q",
                         [["q / @q", "record and replay the alternate anchor traversal"]],
                         method_requirement=require_method(
                             "replay a search-bearing macro on alternate anchors",
                             exact_any_of=["/o<CR>qqr*nq3@q"])),
                ],
            ),
        ],
        "transfer": step(
            [" /~\\ ", "[x]", "\\_/",
             " <^> ", "[x]", "-_-",
             " \\~/ ", "[x]", "/_\\"],
            [" /~\\ ", "[o]", "\\_/",
             " <^> ", "[o]", "-_-",
             " \\~/ ", "[o]", "/_\\"],
            "/x<CR>ron.n.",
            [["/x / ro / n.", "correct the unfamiliar homologous anchors across three frames"]],
            method_requirement=require_method(
                "transfer search repeat plus dot to unfamiliar frame anchors",
                exact_any_of=["/x<CR>ron.n."]),
        ),
        "transfer_alt": step(
            [" /+\\ ", "<x>", "\\-_/",
             " /^\\ ", "<x>", "/__\\",
             " \\+/ ", "<x>", "/-\\"],
            [" /+\\ ", "<o>", "\\-_/",
             " /^\\ ", "<o>", "/__\\",
             " \\+/ ", "<o>", "/-\\"],
            "/x<CR>ron.n.",
            [["/x / ro / n.", "correct the alternate homologous anchors across three frames"]],
            method_requirement=require_method(
                "transfer search repeat plus dot to alternate anchors",
                exact_any_of=["/x<CR>ron.n."]),
        ),
    },
    {
        "id": "M18", "title": "Hand-mirrored return", "node": "A6/V18",
        "project": "hand-mirrored-return", "frame_rows": 4,
        "labels_steps": [1, 2, 4, 5, 6, 8],
        "skill": "full directional hand mirrors, validation-only expression substitution, and reverse-order frame reuse",
        "source_ref": "ascii-art-authoring §§7.2,7.5,8.2; Neovim help :sub-replace-expression, getline(), :copy",
        "meaning": "a right-facing action is redrawn by hand as a left-facing return, checked without generating art, eased into an overshoot, and reused in reverse around an intentional turnaround hold",
        "first_reading": "the actor, arrowhead, slash limbs, and whitespace all exchange direction by authored judgment while the frame width and rails remain fixed",
        "principle": "never reverse stored bytes to mirror ASCII art; redraw directional glyphs and spacing by eye, validate the result separately, then reuse approved frames in reverse when the motion physically returns",
        "defect": "a slash points inward after mirroring, the actor shifts to the wrong distance from the rail, an expression replacement generates the art instead of only checking it, or reverse reuse adds an unexplained duplicate",
        "basic": "overwrite all three art rows with a deliberate hand-authored mirror while leaving the validation line pending",
        "scaled": "compare manual validation with a check-only \\= expression, then append approved frame ranges in reverse order with an explicit turnaround hold",
        "steps": [
            step(
                ["|o--->....|", "|./|......|", "|./.\\.....|", "CHECK=0"],
                ["|....<---o|", "|......|\\.|", "|...../.\\.|", "CHECK=0"],
                "0C|....<---o|<Esc>j0C|......|\\.|<Esc>j0C|...../.\\.|<Esc>",
                [["0C...", "overwrite the complete top row with the actor and arrowhead exchanged by hand"],
                 ["j0C...", "redraw the arm slash and spacing rather than reversing bytes"],
                 ["j0C...", "redraw the leg slashes at their mirrored positions while preserving width"]],
                method_requirement=require_method(
                    "hand-author all three mirrored art rows without a software flip",
                    exact_any_of=["0C|....<---o|<Esc>j0C|......|\\.|<Esc>j0C|...../.\\.|<Esc>"]),
                review_variants=[
                    step(["|*===>....|", "|.<|......|", "|./.\\.....|", "CHECK=0"],
                         ["|....<===*|", "|......|>.|", "|...../.\\.|", "CHECK=0"],
                         "0C|....<===*|<Esc>j0C|......|>.|<Esc>j0C|...../.\\.|<Esc>",
                         [["C on three rows", "hand-author every directional changed-art row"]],
                         method_requirement=require_method(
                             "hand-author the changed full-frame mirror",
                             exact_any_of=["0C|....<===*|<Esc>j0C|......|>.|<Esc>j0C|...../.\\.|<Esc>"])),
                    step(["|+--->....|", "|.\\|......|", "|.\\./.....|", "CHECK=0"],
                         ["|....<---+|", "|......|/.|", "|.....\\./.|", "CHECK=0"],
                         "0C|....<---+|<Esc>j0C|......|/.|<Esc>j0C|.....\\./.|<Esc>",
                         [["C on three rows", "hand-author the alternate full-frame mirror"]],
                         method_requirement=require_method(
                             "hand-author the alternate full-frame mirror",
                             exact_any_of=["0C|....<---+|<Esc>j0C|......|/.|<Esc>j0C|.....\\./.|<Esc>"])),
                ],
            ),
            step(
                ["|....<---o|", "|......|\\.|", "|...../.\\.|", "CHECK=0"],
                ["|....<---o|", "|......|\\.|", "|...../.\\.|", "CHECK=0",
                 "|....<---o|", "|......|\\.|", "|...../.\\.|", "CHECK=0"],
                "gg4yyGp",
                [["gg4yy", "yank the complete mirrored frame plus its validation line"],
                 ["Gp", "append the approved return as the overshoot scaffold"]],
                method_requirement=require_method(
                    "copy the complete four-line mirrored frame",
                    exact_any_of=["gg4yyGp"]),
            ),
            step(
                ["|....<---o|", "|......|\\.|", "|...../.\\.|", "CHECK=0",
                 "|....<---o|", "|......|\\.|", "|...../.\\.|", "CHECK=0"],
                ["|....<---o|", "|......|\\.|", "|...../.\\.|", "CHECK=0",
                 "|...<---o.|", "|.....|\\..|", "|..../.\\..|", "CHECK=0"],
                "5G0C|...<---o.|<Esc>j0C|.....|\\..|<Esc>j0C|..../.\\..|<Esc>",
                [["5G0C...", "move the copied top action one cell past the return extreme"],
                 ["j0C... twice", "redraw both limb rows at the same one-cell overshoot"]],
                method_requirement=require_method(
                    "hand-author the copied return overshoot across all three art rows",
                    exact_any_of=["5G0C|...<---o.|<Esc>j0C|.....|\\..|<Esc>j0C|..../.\\..|<Esc>"]),
                review_variants=[
                    step(["|....<===*|", "|......|>.|", "|...../.\\.|", "CHECK=0",
                          "|....<===*|", "|......|>.|", "|...../.\\.|", "CHECK=0"],
                         ["|....<===*|", "|......|>.|", "|...../.\\.|", "CHECK=0",
                          "|...<===*.|", "|.....|>..|", "|..../.\\..|", "CHECK=0"],
                         "5G0C|...<===*.|<Esc>j0C|.....|>..|<Esc>j0C|..../.\\..|<Esc>",
                         [["C on copied rows", "hand-author the changed return overshoot"]],
                         method_requirement=require_method(
                             "hand-author the changed return overshoot",
                             exact_any_of=["5G0C|...<===*.|<Esc>j0C|.....|>..|<Esc>j0C|..../.\\..|<Esc>"])),
                    step(["|....<---+|", "|......|/.|", "|.....\\./.|", "CHECK=0",
                          "|....<---+|", "|......|/.|", "|.....\\./.|", "CHECK=0"],
                         ["|....<---+|", "|......|/.|", "|.....\\./.|", "CHECK=0",
                          "|...<---+.|", "|.....|/..|", "|....\\./..|", "CHECK=0"],
                         "5G0C|...<---+.|<Esc>j0C|.....|/..|<Esc>j0C|....\\./..|<Esc>",
                         [["C on copied rows", "hand-author the alternate return overshoot"]],
                         method_requirement=require_method(
                             "hand-author the alternate return overshoot",
                             exact_any_of=["5G0C|...<---+.|<Esc>j0C|.....|/..|<Esc>j0C|....\\./..|<Esc>"])),
                ],
            ),
            step(
                ["|....<---o|", "|......|\\.|", "|...../.\\.|", "CHECK=0",
                 "|...<---o.|", "|.....|\\..|", "|..../.\\..|", "CHECK=0"],
                ["|....<---o|", "|......|\\.|", "|...../.\\.|", "CHECK=1",
                 "|...<---o.|", "|.....|\\..|", "|..../.\\..|", "CHECK=1"],
                "4G$r18G$r1",
                [["4G$r1 / 8G$r1", "mark each frame verified only after inspecting its hand-authored art"]],
                alternatives=[
                    method("manual verification markers", "4G$r18G$r1", "inspect both frames, then replace only their pending check digits"),
                    method("expression validation only", ":4s/0/\\=getline(1)=~'<---'?'1':'0'/<CR>:8s/0/\\=getline(5)=~'<---'?'1':'0'/<CR>", "derive only each check digit from its already-authored top row; never generate mirrored art"),
                ],
                review_variants=[
                    step(["|....<===*|", "|......|>.|", "|...../.\\.|", "CHECK=0",
                          "|...<===*.|", "|.....|>..|", "|..../.\\..|", "CHECK=0"],
                         ["|....<===*|", "|......|>.|", "|...../.\\.|", "CHECK=1",
                          "|...<===*.|", "|.....|>..|", "|..../.\\..|", "CHECK=1"],
                         "4G$r18G$r1",
                         [["r1", "manually mark both inspected changed-art frames"]],
                         method_requirement=require_method(
                             "use manual validation markers on changed mirrored art",
                             exact_any_of=["4G$r18G$r1"])),
                    step(["|....<---+|", "|......|/.|", "|.....\\./.|", "CHECK=0",
                          "|...<---+.|", "|.....|/..|", "|....\\./..|", "CHECK=0"],
                         ["|....<---+|", "|......|/.|", "|.....\\./.|", "CHECK=1",
                          "|...<---+.|", "|.....|/..|", "|....\\./..|", "CHECK=1"],
                         ":4s/0/\\=getline(1)=~'<---'?'1':'0'/<CR>:8s/0/\\=getline(5)=~'<---'?'1':'0'/<CR>",
                         [["\\=getline()", "validate only the alternate check digits from already-authored rows"]],
                         method_requirement=require_method(
                             "use expression substitution only as an alternate validation check",
                             exact_any_of=[":4s/0/\\=getline(1)=~'<---'?'1':'0'/<CR>:8s/0/\\=getline(5)=~'<---'?'1':'0'/<CR>"])),
                ],
            ),
            step(
                ["|....<---o|", "|......|\\.|", "|...../.\\.|", "CHECK=1",
                 "|...<---o.|", "|.....|\\..|", "|..../.\\..|", "CHECK=1"],
                ["|....<---o|", "|......|\\.|", "|...../.\\.|", "CHECK=1",
                 "|...<---o.|", "|.....|\\..|", "|..../.\\..|", "CHECK=1",
                 "|...<---o.|", "|.....|\\..|", "|..../.\\..|", "CHECK=1",
                 "|....<---o|", "|......|\\.|", "|...../.\\.|", "CHECK=1"],
                ":5,8t$<CR>:1,4t$<CR>",
                [[":5,8t$", "append the approved overshoot as the turnaround frame"],
                 [":1,4t$", "append the earlier return extreme to reuse the motion in reverse"]],
                method_requirement=require_method(
                    "reuse complete approved frame ranges in reverse order",
                    exact_any_of=[":5,8t$<CR>:1,4t$<CR>"]),
                review_variants=[
                    step(["|....<===*|", "|......|>.|", "|...../.\\.|", "CHECK=1",
                          "|...<===*.|", "|.....|>..|", "|..../.\\..|", "CHECK=1"],
                         ["|....<===*|", "|......|>.|", "|...../.\\.|", "CHECK=1",
                          "|...<===*.|", "|.....|>..|", "|..../.\\..|", "CHECK=1",
                          "|...<===*.|", "|.....|>..|", "|..../.\\..|", "CHECK=1",
                          "|....<===*|", "|......|>.|", "|...../.\\.|", "CHECK=1"],
                         ":5,8t$<CR>:1,4t$<CR>",
                         [[":t in reverse order", "reuse the changed approved frames around their turnaround"]],
                         method_requirement=require_method(
                             "reuse changed approved frames in reverse order",
                             exact_any_of=[":5,8t$<CR>:1,4t$<CR>"])),
                    step(["|....<---+|", "|......|/.|", "|.....\\./.|", "CHECK=1",
                          "|...<---+.|", "|.....|/..|", "|....\\./..|", "CHECK=1"],
                         ["|....<---+|", "|......|/.|", "|.....\\./.|", "CHECK=1",
                          "|...<---+.|", "|.....|/..|", "|....\\./..|", "CHECK=1",
                          "|...<---+.|", "|.....|/..|", "|....\\./..|", "CHECK=1",
                          "|....<---+|", "|......|/.|", "|.....\\./.|", "CHECK=1"],
                         ":5,8t$<CR>:1,4t$<CR>",
                         [[":t in reverse order", "reuse the alternate approved frames around their turnaround"]],
                         method_requirement=require_method(
                             "reuse alternate approved frames in reverse order",
                             exact_any_of=[":5,8t$<CR>:1,4t$<CR>"])),
                ],
            ),
        ],
        "transfer": step(
            ["|*===>....|", "|.<|......|", "|./.\\.....|", "CHECK=0"],
            ["|....<===*|", "|......|>.|", "|...../.\\.|", "CHECK=0"],
            "0C|....<===*|<Esc>j0C|......|>.|<Esc>j0C|...../.\\.|<Esc>",
            [["C on three rows", "hand-author every directional row in the unfamiliar full-frame mirror"]],
            method_requirement=require_method(
                "transfer full-frame hand mirroring to unfamiliar directional art",
                exact_any_of=["0C|....<===*|<Esc>j0C|......|>.|<Esc>j0C|...../.\\.|<Esc>"]),
        ),
        "transfer_alt": step(
            ["|+--->....|", "|.\\|......|", "|.\\./.....|", "CHECK=0"],
            ["|....<---+|", "|......|/.|", "|.....\\./.|", "CHECK=0"],
            "0C|....<---+|<Esc>j0C|......|/.|<Esc>j0C|.....\\./.|<Esc>",
            [["C on three rows", "hand-author every directional row in the alternate full-frame mirror"]],
            method_requirement=require_method(
                "transfer full-frame hand mirroring to alternate directional art",
                exact_any_of=["0C|....<---+|<Esc>j0C|......|/.|<Esc>j0C|.....\\./.|<Esc>"]),
        ),
    },
]


def _add_registration_rails(edit):
    """Give every M17 frame a visible, stable width reference."""
    for field in ("start", "target"):
        edit[field] = [
            line if line.startswith("| ") and line.endswith(" |") else f"| {line} |"
            for line in edit[field]
        ]
    for variant in edit.get("review_variants", []):
        _add_registration_rails(variant)


_m17 = next(module for module in MODULES if module["id"] == "M17")
for _edit in [*_m17["steps"], _m17["transfer"], _m17["transfer_alt"]]:
    _add_registration_rails(_edit)


KINDS = {1: "guided_edit", 2: "guided_edit", 3: "concept", 4: "independent_edit",
         5: "compare_methods", 6: "transfer", 7: "concept", 8: "module_check"}

PREREQUISITES = {
    "M0": [],
    "M1": ["M0"],
    "M2": ["M0"],
    "M3": ["M2"],
    "M4": ["M1", "M3"],
    "M5": ["M2", "M3"],
    "M6": ["M3"],
    "M7": ["M6"],
    "M8": ["M4", "M7"],
    "M9": ["M5", "M8"],
    "M10": ["M1"],
    "M11": ["M0"],
    "M12": ["M1", "M11"],
    "M13": ["M1", "M12"],
    "M14": ["M3", "M13"],
    "M15": ["M13", "M14"],
    "M16": ["M14", "M15"],
    "M17": ["M15", "M16"],
    "M18": ["M16", "M17"],
}

FIRST_READING_DISTRACTORS = {
    "M0": [
        "the whole spark translates one cell even though its core keeps the same value",
        "every ray widens at once, so this is already the flare extreme",
        "nothing changes; the second frame is only an intentional hold",
    ],
    "M1": [
        "the anchor moves right while the joint keeps its original spelling",
        "the entire contour is mirrored into a descending pose",
        "the comma is deleted, leaving a break in the material",
    ],
    "M2": [
        "the eye closes while the annotation remains attached",
        "the mouth and lower contour are deleted with the label",
        "the complete face shifts left by the width of the removed note",
    ],
    "M3": [
        "only the head row was copied and moved away from the body",
        "the eye changes and the torso widens in the same pose",
        "the six-row body is duplicated as an unchanged timing hold",
    ],
    "M4": [
        "the fixed pivot moves while the prop keeps its backslash angle",
        "one prop cell turns but the other remains at the old angle",
        "the whole three-row frame translates instead of rotating",
    ],
    "M5": [
        "the foreground blade is erased while the background seam remains",
        "the background texture and ground line both disappear",
        "the blade moves to a new frame without moving its background hole",
    ],
    "M6": [
        "the bottom row is deleted, collapsing the keyframe to four rows",
        "the finished frame is moved before its apex is repaired",
        "the pyramid plays backward from complete to empty",
    ],
    "M7": [
        "the completed build is repeated after the settle with no declared purpose",
        "only one row is copied, so the next frame loses its five-row bounds",
        "the build is shortened by deleting its blank padding row",
    ],
    "M8": [
        "the torso moves sideways while the foot remains above the ground",
        "the raised arm flips at the same instant as every leg glyph",
        "the full pose is duplicated without changing its contact state",
    ],
    "M9": [
        "the side rails and ground move with the ball, hiding its vertical travel",
        "the squash keeps a round centre and never flattens into an impact pose",
        "an unchanged high frame is repeated instead of a distinct rebound overshoot",
    ],
    "M10": [
        "the missing partner is guessed from terminal-cell centering alone",
        "the lower contour is replaced even though only the shoulder is unknown",
        "the fragment is accepted visually without a Saitamaar true-metric view",
    ],
    "M11": [
        "both side walls shift right because two new glyphs were inserted instead of overwritten",
        "the second machine changes tension even though only the first roof was selected",
        "the roof keeps its original -- material and only an indicator changes case",
    ],
    "M12": [
        "both upper joints change together, eliminating the intended left-to-right stagger",
        "the centre axis shifts one column while the accent itself stays on the left",
        "the row is byte-reversed, so the slash endpoints point inward incorrectly",
    ],
    "M13": [
        "the three texture clusters slide together because one was deleted instead of edited in place",
        "the support rows pulse with the material even though they are declared temporal anchors",
        "the first accent lands inside a punctuation cluster because a lowercase word motion stopped at punctuation",
    ],
    "M14": [
        "the right wall moves because the palette glyph was inserted rather than replacing the eye cell",
        "the whole face changes material even though only its eye is the acting variant",
        "the star is retyped from memory and no longer matches the visible palette glyph",
    ],
    "M15": [
        "the whole ground translates even though only the brick material should offset by one cell",
        "the angled shadow row becomes lighter together with the dither, erasing the depth cue",
        "the macro edits every punctuation mark in the file instead of the four landmarks on its acting row",
    ],
    "M16": [
        "the plan starts with in-betweens before any readable key pose or size test exists",
        "only the frame label changes, so the unreadable small silhouette is accepted without review",
        "the timing line is treated as decoration and no playback rate is committed before drawing",
    ],
    "M17": [
        "the entire shell is redrawn identically, so no pose change remains to animate",
        "the eye shifts with each contour even though it should be the stable temporal anchor",
        "every punctuation cell changes because the batch operation has no homologous landmark scope",
    ],
    "M18": [
        "the stored row is reversed byte-for-byte, leaving slash limbs and arrowheads facing the wrong way",
        "only the actor moves across the frame while all directional glyphs keep their original orientation",
        "the return is regenerated by an expression substitute, so no authored mirror judgment is exercised",
    ],
}

SEQUENCE_READINGS = {
    "M0": "registered rays; the core brightens, flares, holds, then settles",
    "M1": "fixed anchors; the shallow contour rises, falls, and returns",
    "M2": "fixed face contour; focus opens, holds, then closes into a blink",
    "M3": "fixed six-row body; only the eye accent changes across poses",
    "M4": "fixed pivot; the two-cell prop passes through a vertical midpoint",
    "M5": "fixed pivot; the background break stays directly below it while the blade swings",
    "M6": "equal five-row bounds; reordered frames visibly build the pyramid",
    "M7": "a declared anticipation hold remains; the stray settle copy is removed",
    "M8": "registered torso; planted feet alternate while the arm arrives later",
    "M9": "fixed rails and ground; high, falling, squash, and rebound overshoot read in order",
    "M10": "the complete puff expands from lobe to arch, holds at the hatched impact, then returns to its registered settle",
    "M11": "registered walls; the copied roof slackens, its indicators brighten, and aligned blur trails appear at one virtual column",
    "M12": "fixed centre axis; the joint accent travels left, both, lower pair, release, then right",
    "M13": "fixed support rows; the material accent travels centre, right, expanded edges, flash, then left",
    "M14": "one registered face silhouette; its palette-owned eye changes star, plus, then returns to star across paragraph frames",
    "M15": "fixed angled ground shadow; the brick material offsets, the dither lightens, an edge occludes the middle frame, and a macro-built settle returns without drift",
    "M16": "one approved playback-size key pose remains intact while complete written plan blocks are imported, numbered, copied, and reordered",
    "M17": "four distinct shell poses retain one homologous eye anchor, then one deliberate palette pass changes that anchor coherently across the strip",
    "M18": "a full hand-authored return and overshoot are validated separately, then reused in reverse around a declared turnaround hold",
}

# Every pair is authored for its own art and its own Vim operation.  This is
# deliberately data, not a stem template with a module title substituted into
# it: a learner should have to inspect the actual pose and reason about the
# actual edit on every item.
QUESTION_PROMPTS = {
    "M0": [
        ("Which visible change turns the placeholder spark into the first readable pose?", "Starting on the top-left ray, which bounded Normal-mode path goes to the acting row, finds the visible dot, and replaces only that core?"),
        ("What must be true before this small spark is worth extending into more frames?", "Which command copies the complete three-row keyframe rather than only the row under the cursor?"),
        ("A brighter core is visible, but one ray also moved. What is the animation defect?", "Which bounded substitution changes the flare row without touching the slash rays above and below it?"),
        ("The next pose must widen while its centre stays registered. What motion constraint governs the edit?", "Which one-character command changes the core without entering Insert mode or shifting neighbouring rays?"),
        ("Why can two identical wide-flare frames be intentional in this strip?", "For a known three-line flare at lines 7–9, when is :7,9t$ the safer copy method?"),
        ("The transfer comet faces the other direction. What must remain invariant as its core and tail brighten?", "Which search-and-replace sequence reaches the unfamiliar core and limits the dash replacement to its current row?"),
        ("Read the five spark poses in order. What timing pattern do they show?", "Which Ex range copies a complete three-row settle pose to the end of the file?"),
        ("What distinguishes the repeated flare from an accidental duplicate?", "What count must accompany yy so the yank contains the whole spark frame?"),
        ("After the hold, what should the final dim frame communicate?", "Why does the settle copy lines 1–3 and then lower only its core from o to .?"),
        ("A proposed global change would also rewrite stable rays. What repair preserves the animation?", "Which scope check should happen before replacing '-' with '=' in an ASCII frame?"),
    ],
    "M1": [
        ("At the contour joint, what changed while the anchor and slope remained fixed?", "Which search command reaches the comma joint without counting punctuation columns?"),
        ("Why should one slope spelling be reused across the rising and falling poses?", "How does a count with yy or dd keep a three-row contour operation frame-sized?"),
        ("The endpoint moved although only the joint was meant to change. What failed?", "Which operator-plus-motion deletes one punctuation WORD without consuming the anchored row?"),
        ("A descending pose must be authored from the approved rise. What must remain registered?", "When should 3dd be used instead of dd while replacing a complete three-line pose?"),
        ("Two joint glyphs need the same local correction. What makes dot repeat appropriate?", "Which sequence edits the first joint and repeats that exact replacement at the second?"),
        ("The mirrored transfer changes direction but not material. What property should carry over?", "Which / search and r replacement is independent of the mirrored joint's column?"),
        ("Across rise, fall, and return, what is the stable visual landmark?", "Which command returns to the next search match when the same joint glyph recurs?"),
        ("Why is hand-authoring the mirror more instructive than reversing bytes?", "Which Visual-line selection covers exactly one complete three-row contour candidate?"),
        ("If :%s/:/;/g is run on the strip, what visual property changes and what stays fixed?", "What does the % range add to :s compared with a substitution on the current row?"),
        ("A shorter command would change every colon in unrelated art. What bounded alternative fits?", "How can a line range before :s constrain the edit to the contour frames under review?"),
    ],
    "M2": [
        ("After the note disappears, which parts prove the face silhouette did not move?", "Which text-object command removes 'note' together with its adjacent space?"),
        ("Why is the four-row face copied before changing its expression?", "Which counted yank preserves the complete face rather than duplicating only its eye row?"),
        ("The mouth vanished with the annotation. Why is that a scope failure?", "What search should precede daw so the deletion begins on the annotation, not the face?"),
        ("Only the copied eye should open. Which visual landmark must not change?", "Which f search and r replacement edits the eye without moving the mouth or contour?"),
        ("When is a scoped substitute preferable to two local eye replacements?", "What pattern matches only the two known eye spellings '.' and 'o'?"),
        ("The transfer face has a different mouth. What feature is still the acting focus?", "Which find-character command reaches the eye without assuming its column from the old face?"),
        ("Open, focused, and blink poses share four rows. What makes them coherent?", "Which exact line range should be copied before turning the new eye into '-'?"),
        ("Why does the blink edit belong inside the existing contour rather than on a new one-row symbol?", "Which operator can change a word-sized facial feature while preserving its surrounding row?"),
        ("What would an unbounded eye substitution risk in a larger character sheet?", "How does :1,8s/.../.../g differ from :%s/.../.../g on this two-frame study?"),
        ("A command consumes the mouth with the eye. What should be narrowed?", "Which text object or single-character replacement matches the actual feature boundary?"),
    ],
    "M3": [
        ("Which change approves the primary pose without altering the six-row body?", "How do f( and % verify the eye's matching parentheses before r changes the enclosed glyph?"),
        ("Why must all six rows be copied before the second acting pose is edited?", "Which count makes yy include head, torso, legs, and baseline together?"),
        ("Only the head row was duplicated. What continuity evidence is missing?", "Which Visual-line span selects the complete six-row pose for a named register?"),
        ("The copied eye changes from o to O. What must stay identical around it?", "Why does ci( fit the eye edit better than C on the entire head row?"),
        ("When is :1,6t$ clearer than gg6yyGp for this pose?", "What cursor-dependence does an addressed :t copy remove?"),
        ("The transfer body has different arms. What still defines a valid whole-pose copy?", "How do V, \"ay, and \"ap preserve the selected pose while other deletes may overwrite the unnamed register?"),
        ("Across the three poses, which body rows are temporal anchors?", "Which direct line address reaches the final pose's eye row without adding an unused mark-and-return detour?"),
        ("Why is a changed eye not permission to redraw the torso?", "After reaching line 14, which find motion locates the eye inside that row without touching the torso?"),
        ("What does changing the last eye to a middle dot add to the acting sequence?", "Which digraph replacement changes only that directly addressed eye?"),
        ("A copy omits the feet. What correction restores a usable keyframe?", "Which linewise selection or six-line range guarantees the baseline travels with the pose?"),
    ],
    "M4": [
        ("Which two diagonal stroke cells cross the fixed pivot axis between the readable extremes?", "Why must the upper tip be redrawn with C while the lower stroke can use a local r?"),
        ("Why must the backslash and slash extremes read before a vertical tween is inserted?", "Which three-line copy preserves the registered pivot row while making a working frame?"),
        ("The upper tip moved but the lower stroke did not turn. What rigid-part defect appears?", "Which two addressed line edits finish the diagonal without touching the pivot row?"),
        ("Where must the vertical midpoint sit relative to both diagonal extremes?", "Which :copy address inserts a complete extreme before C aligns row 4 and a two-row block replaces the column?"),
        ("Why is the returning vertical pose a distinct frame rather than a copied diagonal?", "How do the addressed-copy and counted-yank alternatives append the same complete seam candidate after redrawing that midpoint?"),
        ("The transfer prop is offset, but its pivot remains registered. What must carry into the tween?", "Which copied rows does C redraw to produce the complete vertical midpoint?"),
        ("Read backslash, vertical, slash, vertical, then wrap to the first frame. What loop results?", "Which exact three-line deletion removes the redundant copied first pose from the loop boundary?"),
        ("Why does pivot column 4 remain invariant while the upper tip changes columns?", "Which local motion reaches column 4 for the lower-stroke replacement?"),
        ("What continuity is lost if only one row of a three-row rotation pose is inserted?", "Which count or :copy range guarantees the pivot row travels with the prop?"),
        ("When is a Visual block appropriate in this module despite diagonal extremes?", "What must be true before a blockwise r is used on the vertical midpoint's two aligned cells?"),
    ],
    "M5": [
        ("Which background bar visibly touches the foreground pivot, and what does removing it clarify?", "Which r<Space> edit breaks that one-cell seam without shifting the texture row?"),
        ("Why must foreground, contact row, texture bands, and ground travel as one seven-row frame?", "Which Visual-line span selects that complete composited frame?"),
        ("The blade swings but the break below its fixed pivot is refilled. What false object appears?", "Which search or find motion should locate the touching background bar before r<Space>?"),
        ("When the blade changes sides, which layer still owns the negative-space break?", "Why may C redraw only the copied foreground rows while leaving the pivot/contact rows intact?"),
        ("What makes :1,7t7 clearer than a cursor-relative yank for this composite?", "Which addressed range inserts every texture and ground row into the temporal gap before the blade rows are redrawn?"),
        ("The transfer uses a triangular foreground ending at a new pivot. Where must the break sit?", "Which counted l motion reaches the bar directly below that visible pivot?"),
        ("Across all frames, what proves foreground and background remain distinct despite contact?", "Which scoped r command can accent the pivot without refilling the erased bar below it?"),
        ("Why is erasing the blade instead of the background the wrong depth repair?", "How does linewise Visual mode expose the full seven-row ownership boundary before yanking?"),
        ("What alignment evidence shows the seam repair belongs directly below the pivot?", "How can 0 plus a counted l motion verify the exact fixed-width column before replacement?"),
        ("Why would a global replacement damage the dotted texture?", "Which one-cell r edit preserves row length and every neighbouring material glyph?"),
    ],
    "M6": [
        ("What change completes the finished pyramid keyframe without moving its base?", "Which one-character replacement changes the apex while preserving all five rows?"),
        ("Why is the finished five-row form copied before anything is erased?", "Which :copy range duplicates the complete keyframe, including its base?"),
        ("Why must the first subtractive edit clear content without deleting the copied apex row?", "Which 0D command blanks that row while retaining the five-row boundary?"),
        ("How should the first subtractive frame differ from the finished keyframe for bottom-up growth?", "Why does clearing the apex leave the attached shoulder and base as the next readable state?"),
        ("When is a five-line :copy safer than a counted yank?", "Which follow-up D clears the next upper unit while retaining its padding row?"),
        ("An unfamiliar strip begins finished then reduced. What order makes forward playback grow bottom-up?", "Which :move sends the finished five-row frame after its reduced predecessor?"),
        ("Read the equal-height frames forward. What growth action becomes visible?", "Which command preserves five-row slices while reordering authoring order into playback order?"),
        ("Why is reverse authoring valid for an accretive effect?", "What line-count check catches a missing padding row before :move?"),
        ("Why is a join-and-immediate-undo demonstration not counted as useful coverage here?", "Which direct content-clearing edit performs the actual subtractive task without collapsing and restoring a row?"),
        ("A deletion shortens one pose. What recovery keeps the strip animatable?", "Why should D clear a chosen upper row rather than dd remove that row?"),
    ],
    "M7": [
        ("Why does the incomplete build repeat before the completed frame?", "Which addressed copy inserts a five-row anticipation hold after the first frame?"),
        ("When is a duplicate settle frame accidental rather than a hold?", "Which range copies the full five-row settle candidate for review?"),
        ("Two held frames have different three-cell material bands. What timing defect does that create?", "How can dot repeat apply the same bounded Visual replacement exactly five rows later?"),
        ("What property must both anticipation frames share?", "Which initial v2lr= change establishes the band edit that . will replay?"),
        ("Why must a material-band polish affect every visible build frame rather than only the hold?", "How can a five-row-step macro replay one three-cell Visual replacement at each homologous band?"),
        ("The transfer hold uses a different character. What still makes dot repeat valid?", "Which motion lands on the same acting feature five rows later before . repeats the edit?"),
        ("Read the strip after the duplicate is removed. Where is the remaining pause?", "Which five-line deletion removes only the accidental trailing frame?"),
        ("Why is a hold a timing decision rather than merely duplicated text?", "Why is whole-strip material consistency a separate concern from the two-frame hold range?"),
        ("What does :g on exact `  /---` rows prevent during global-normal polish?", "Why should :normal receive only matching band rows rather than every strip row?"),
        ("A macro steps into the wrong row between frames. What should be corrected?", "Why must the recorded 5j equal the frame height before @q replays the Visual band edit?"),
    ],
    "M8": [
        ("Which new ground mark proves the leading foot has planted?", "Which end-of-line motion and r replacement change only the contact cell?"),
        ("Why is the entire five-row contact pose copied before the passing pose is drawn?", "Which count keeps the head, torso, legs, and both ground cells together?"),
        ("The foot changed but the torso also shifted. What coherence defect appears?", "Which C edits are limited to the copied pose's moving rows?"),
        ("Why may the raised arm arrive later than the planted foot?", "Why does the independent build type each complete new pose row after o instead of padding the recipe with unrelated I and A commands?"),
        ("When is a scoped arm substitution safer than a direct local replacement?", "Why must the range end at line 5 rather than spill into the next pose's head row?"),
        ("The transfer walker is horizontally offset. What contact evidence must still be added?", "Which l count should be derived from the visible foot, not memorised from the original pose?"),
        ("Read contact, passing, opposite contact, and return passing. How do feet and arms differ in tempo?", "Which five-line copy scaffolds the distinct return passing pose before its limbs are mirrored?"),
        ("Why must every walk pose retain five rows?", "What does a counted yank include that a one-line yy would omit?"),
        ("What would a global slash replacement do to this walk cycle?", "Which local f/r path changes one raised arm while leaving leg diagonals alone?"),
        ("A planted foot slides one cell between adjacent frames. What should be repaired?", "Which search or mark can revisit the contact column across full poses before editing?"),
    ],
    "M9": [
        ("Which planned change commits the high ball keyframe while rails and ground remain fixed?", "Which f/r sequence replaces only the x plan marker?"),
        ("Why is the complete high frame copied before the squash extreme is blocked?", "Which counted yank carries both side rails and the ground anchor?"),
        ("The squash centre remains round instead of horizontal. What pose-reading defect remains?", "How do x and i= replace only that centre cell without shifting the row?"),
        ("Why must the high and squash extremes read before the falling midpoint is inserted?", "Which copied rows are redrawn to move the ball from row 1 to row 2?"),
        ("When is copy-then-vary safer than inserting three new midpoint rows?", "Which :copy command preserves the registered rails and ground automatically?"),
        ("The transfer bounce uses brackets or angle rails. What still defines a valid keyframe edit?", "Which fx plus r operation ignores the changed horizontal offset and container glyphs?"),
        ("Read high, falling, squash, overshoot. What makes the motion return coherently to high?", "Which three-line copy provides the rebound scaffold before o becomes O?"),
        ("Why is the larger rebound O an overshoot rather than an accidental material change?", "Which local rO edit changes only the rebound subject after its complete frame is copied?"),
        ("What would drawing the falling midpoint before planning both extremes obscure?", "Which buffer order keeps high and squash visible before :t inserts between them?"),
        ("A one-row ball or dash is presented as a complete pose. What bounds are missing?", "Which count or range guarantees rails and ground travel with every three-row frame?"),
    ],
    "M10": [
        ("Which contour change completes the first proportional puff pose?", "Which end-of-line replacement fills the missing partner without shifting the lower rows?"),
        ("Why must the lobe remain a complete three-row frame before it expands?", "Which counted yank copies all three proportional rows as an expansion scaffold?"),
        ("The top shoulder widens but the bowl stays narrow. What motion defect results?", "Which C edits redraw all three copied rows as one wider extreme?"),
        ("What role does the ￣ over ＿ relationship play in the wider puff?", "Which Neovim edit preserves their vertical row relationship instead of joining them?"),
        ("Why is a second identical hatched impact frame legitimate?", "Which addressed :t range copies the complete three-row impact pose?"),
        ("The transfer shoulder uses ｀ヽ. What must stay registered below it?", "Which $ and r sequence completes the pair without relying on terminal cell width?"),
        ("Read lobe, arch, impact, hold, settle. What is the animation arc?", "Which first-frame range is copied to close the strip after the impact hold?"),
        ("Why must hatching remain inside the impact outline?", "Which row-local edit can change the hatching without replacing either contour row?"),
        ("What evidence is still needed after Neovim contains the exact Unicode text?", "Which command proves transcription only, and which Saitamaar preview supplies visual evidence?"),
        ("A terminal preview looks aligned but Saitamaar does not. Which judgement wins?", "Which edit should be revised only after measuring the true-advance render rather than counting terminal columns?"),
    ],
    "M11": [
        ("Which roof cells change while both machine walls remain registered?", "Which Replace-mode path overwrites the two-cell -- run without inserting or deleting columns?"),
        ("Why is the complete three-row machine copied before its tension changes?", "Which counted yank and put preserves roof, indicators, and base as one pose?"),
        ("A redraw shifts the right wall two columns. What fixed-width failure occurred?", "Why is R over the existing run safer here than i followed by two new glyphs?"),
        ("Why must undo remove the slack roof before redo restores it?", "Which adjacent u and <C-r> pair proves recovery on the actual R~~ redraw rather than acting as a no-op?"),
        ("The copied pose brightens both indicators while its walls stay still. What is the acting change?", "When do two local r edits and one current-line :s describe the same bounded result?"),
        ("The transfer machine has dots or a rounded shell. What redraw contract remains unchanged?", "Which R== sequence is independent of the unfamiliar endpoint glyphs?"),
        ("Read taut, slack, and the two aligned trail rows. What secondary motion is being added?", "Why must both trail glyphs use the same exact virtual column?"),
        ("The acting rows end before column 14. Why is that empty area still an intentional target?", "Which :set option plus exact-column motion permits inserting a glyph at column 14 without hand-counted padding?"),
        ("What buffer result should R== produce between / and \\?", "How does Replace mode differ from inserting == into the roof run?"),
        ("One blur trail lands at column 13 and the other at 14. What playback defect results?", "Which 13| then insert plus dot-repeat workflow places both glyphs at column 14?"),
    ],
    "M12": [
        ("Which joint changes first while the mirrored outline and centre axis stay fixed?", "How does t: approach the left joint without landing on it, and which final motion reaches the joint for replacement?"),
        ("Why is the entire three-row left-accent pose copied before the right joint activates?", "Which backward till motion approaches the copied right : from the row end?"),
        ("Both upper joints flash at once in the first pose. What timing decision was lost?", "Which exact t-based edit limits the first change to the left joint?"),
        ("Why do the lower joints activate one frame after the upper pair?", "How do ; and , revisit the two homologous joints after one f: search?"),
        ("Two base cells brighten together in the release. When are repeated search and row substitution equivalent?", "Which two accepted paths change only the copied base row's two o cells?"),
        ("The transfer shell reverses slash directions but keeps its axis. What must manual mirroring preserve?", "Which forward and backward till motions reach the changed shell's paired joints without column counts?"),
        ("Read left accent, both upper accents, lower stagger, bright release, and right accent. What motion travels across the strip?", "Which addressed copy supplies the return scaffold before the accent is moved to its mirror?"),
        ("Why is reversing the row's bytes not a valid way to make the return pose?", "What must happen to \\ and / while the left ! becomes : and the right : becomes !?"),
        ("After 0t: on the upper row, where is the cursor relative to the joint?", "Which l then r! sequence changes the joint while preserving row width?"),
        ("A return pose keeps the left ! and also adds the right !. What loop defect remains?", "Which t! and T: edits exchange the acting accent instead of duplicating it?"),
    ],
    "M13": [
        ("Which texture cluster receives the first pulse while both support rows stay fixed?", "Which uppercase WORD motion reaches that whitespace-separated punctuation cluster?"),
        ("Why is the complete centre-pulse frame copied before the accent moves right?", "Which two W-based replacements clear the old cluster and activate the next one?"),
        ("A delete closes the gap between texture clusters. What animation defect does that create?", "Why must r be used after W or E instead of x or d on the fixed-width row?"),
        ("What does the three-edge expansion communicate after the right-only pose?", "How do E, counted W, E, and counted B address those three different cluster landmarks?"),
        ("Why can three ! cells change to * in one copied frame without changing the supports?", "When are repeated f/; replacements and a current-row substitute equivalent?"),
        ("The transfer texture uses dashes instead of dots. What timing intention survives?", "How do counted W and B reach the third and centre clusters without punctuation-sensitive lowercase stops?"),
        ("Read centre, right, expanded edges, flash, and left. What path does the material accent trace?", "Which addressed copy supplies the final left-exit scaffold?"),
        ("Why are the second and third rows temporal anchors rather than part of the pulse?", "Which line address keeps every WORD edit confined to the acting first row?"),
        ("Starting at the first cell, where does W land on '..:: ..:: ..::'?", "How does that differ from lowercase w when punctuation boundaries are present?"),
        ("The flash edits every *-eligible glyph in the file. What scope failure appears?", "Which current-row or explicit-range substitute protects the support rows and earlier poses?"),
    ],
    "M14": [
        ("Which visible change creates the first palette-owned face variant without moving its outline?", "How do named register `a`, Replace mode, and `<C-r>a` change only the eye cell?"),
        ("Why keep the palette text beside the frame instead of retyping a similar glyph from memory?", "Which named-register yank preserves the exact selected glyph for later retrieval?"),
        ("The right wall moves one column after the eye changes. What fixed-grid error occurred?", "Why must `<C-r>a` be used from Replace mode rather than ordinary insertion at the eye?"),
        ("The copied variant changes from star to plus while its silhouette stays identical. What is the animation reading?", "Which line-local search, named-register yank, and Replace-mode retrieval perform that change?"),
        ("Why can paragraph-object copy and an addressed four-line copy produce the same third variant?", "When is `yap` plus frame-boundary `P` safer than `:5,8t$`, and when is the explicit range clearer?"),
        ("The transfer shell and palette glyphs differ. What invariant proves the technique transferred?", "Which exact path stores the unfamiliar palette glyph and replaces the acting cell without insertion?"),
        ("Read star, plus, star across the three complete face blocks. What makes this a variant sequence rather than three unrelated drawings?", "How does `}` move between blank-line-separated frame objects before register retrieval?"),
        ("Why is one copied eye row not a valid saved variant?", "Which paragraph text object owns the three art rows plus their separator?"),
        ("What does returning the third eye to the first palette glyph communicate?", "Which named register and paragraph navigation make that return causal rather than retyped?"),
        ("A paragraph copy includes neighbouring prose or omits the separator. What boundary should be repaired?", "How should blank lines and the cursor position be checked before `yap` or an addressed `:t`?"),
    ],
    "M15": [
        ("Which material moves in the first texture-ground edit while the depth cue remains fixed?", "Why are `shiftwidth=1` and `>>` both required for the one-cell offset?"),
        ("Why copy all three material rows before developing the lighter ground frame?", "Which counted yank preserves the dither, brick band, and angled shadow as one registered pose?"),
        ("The brick motifs move two cells but the plan called for one. What visual defect appears?", "Which option setting makes one `>>` equal one fixed-grid animation cell?"),
        ("How does replacing colons with dots change the material reading without changing its silhouette?", "Which row-bounded substitute lightens only the copied dither band?"),
        ("Why do blockwise `$A` and `:4,6s/$/|/` create the same occluding edge?", "What scope difference should decide between the visual block and explicit range?"),
        ("The transfer uses new brick and shadow glyphs. What proves the texture method transferred?", "Which exact one-cell indent changes only its unfamiliar repeated-material row?"),
        ("Read offset, lightened edge frame, and settle. What makes the shadow row a depth anchor?", "Which line addresses prevent texture edits from leaking into earlier frames?"),
        ("Why is the angled base not lightened together with the top dither?", "How does a current-line or addressed substitute protect a different material rule?"),
        ("What advantage does a recorded landmark edit have across four repeated dither cells?", "How do `qq...q` and `3@q` make the same bounded replacement four times?"),
        ("A macro reaches support punctuation after the last dither mark. What failed?", "Which search landmark and replay count must be checked before accepting the macro?"),
    ],
    "M16": [
        ("What evidence says this three-row figure is ready to become the first key pose?", "How does CTRL-A update F01 without retyping or damaging the plan line?"),
        ("Why should the approved plate and its T08 FPS line be saved before more poses are authored?", "What does `:read %` import, and why must the file on disk be the intended source?"),
        ("Two plan blocks both say F01. What planning defect does that create?", "Which numeric command advances the imported label while preserving zero padding?"),
        ("Why copy one complete five-line plan block instead of redrawing its small pose?", "How do `:1,5t$` and counted CTRL-A create a later numbered plate?"),
        ("When is reordering a planned key pose legitimate before any in-betweens are drawn?", "How do addressed `:m` and linewise delete/put move the same whole block?"),
        ("The transfer changes pose glyphs and timing. What invariant proves planning skill transferred?", "Which exact path increments its unfamiliar F03 label without touching T12 FPS?"),
        ("Read the key-pose blocks as a plan rather than playback. What remains provisional?", "Which five-line boundary must a copy or move preserve?"),
        ("Why write FPS before recursive in-betweening begins?", "Which line should remain unchanged while frame identifiers are incremented?"),
        ("What is lost if a range move cuts through the pose and leaves its timing line behind?", "Which range owns all three art rows plus F and T plan lines?"),
        ("An imported copy reflects stale disk content. What planning failure follows?", "What must be written or verified before `:read %` is used as the source plate?"),
    ],
    "M17": [
        ("Which glyph is the unchanged semantic anchor across the first three shell poses?", "How do `/x`, `n`, and dot change only the three homologous eye cells?"),
        ("Why duplicate the complete third pose before changing its fourth shell contour?", "Which counted yank preserves all three rows and the already-correct eye anchor?"),
        ("One frame still shows x while the others show o. What temporal defect appears?", "Which missing search-repeat or dot-repeat step caused the incomplete coherent pass?"),
        ("How can the fourth shell change shape while its eye remains a stable anchor?", "Which two landmark replacements alter only the copied contour rows?"),
        ("Why can search-plus-dot and `:g/o/normal! ...` legitimately reach the same four eyes?", "What proof must exist before the global line selector is safe?"),
        ("The transfer shells use brackets and different contours. What invariant identifies corresponding cells?", "Which exact search-repeat path updates their three x anchors?"),
        ("Read the strip after every eye becomes star. What changed, and what did not?", "Which command family batch-edited one homologous landmark without changing shell geometry?"),
        ("Why is an unchanged eye useful while surrounding contours move?", "How should matches be counted before replaying a macro across frames?"),
        ("What makes a macro with `n` suitable for a known run of frame anchors?", "Which part of the macro advances to the next verified landmark?"),
        ("The macro wraps and changes the first frame twice. What method error occurred?", "How should the replay count relate to the number of remaining matches?"),
    ],
    "M18": [
        ("Which directional features must be redrawn, not merely relocated, in the mirrored action?", "Why do three explicit `C` overwrites demonstrate a hand mirror rather than a software flip?"),
        ("Why copy the complete mirrored return before authoring its overshoot?", "Which counted yank includes three art rows and the pending validation line?"),
        ("The actor moved left but its arrowhead and limbs still face right. What failed?", "Which rowwise overwrite boundary makes every directional decision explicit?"),
        ("What does the one-cell overshoot add after the return extreme?", "How do addressed row overwrites keep all three body parts at the same offset?"),
        ("Why may a `\\=` expression update CHECK but never generate the mirrored art here?", "How does `getline()` inspect an already-authored row while substitution changes only one digit?"),
        ("The transfer uses a different actor and limb vocabulary. What proves it was mirrored by hand?", "Which exact three-row overwrite redraws every directional glyph and space?"),
        ("Read return, overshoot, overshoot, return. What timing event does the duplicate express?", "Which two addressed copies reuse approved frames in reverse order?"),
        ("Why is the middle duplicate acceptable here but not as an unexplained loop seam?", "What evidence declares it as a turnaround hold rather than a stale scaffold?"),
        ("A byte reversal puts the actor on the other side but corrupts slash direction. What rule was violated?", "Which manual edit family forces the author to judge `/`, `\\`, `<`, and `>`?"),
        ("An expression substitution rewrites all three art rows into a mirror. Why is that not mastery?", "What is the permitted validation-only scope of `\\=` in this module?"),
    ],
}

QUESTION_ANSWERS = {
    "M0": [
        ("only the core changes from . to o; all six rays stay registered", "j0f.ro goes to the acting row, finds the visible dot, and r changes only that cell"),
        ("the three-row spark must already read at playback size before more frames are added", "gg3yyGp copies all three rows; yy without the count would copy only one ray row"),
        ("ray drift is collateral motion because only the brightness core should change", ":8s/-/=/g changes dashes only on the flare row; it does not touch either slash row"),
        ("the centre remains on one registered cell while the horizontal rays widen around it", "r changes the one core cell in place, so neighbouring ray columns do not shift"),
        ("the duplicate creates a deliberate two-frame impact hold before the settle", ":7,9t$ copies the exact flare-frame range and is independent of the current cursor row"),
        ("the comet's contour and registration stay fixed while its core and tail alone brighten", "jforO reaches the unfamiliar core, then :s/-/=/g limits the tail change to that one row"),
        ("dim, bright, flare, flare, lower settle reads as anticipation, impact hold, and release", ":1,3t$ copies the complete dim scaffold, then 14Gfor. lowers only the settle core"),
        ("both frames repeat a complete readable flare for a declared timing pause", "3yy is the required yank; yy alone omits two rows of the frame"),
        ("the final lower core releases the impact without duplicating the first pose at the loop seam", ":1,3t$ appends the frame scaffold and 14Gfor. makes the settle distinct"),
        ("restrict the change to the intended flare row and verify stable glyphs before accepting it", "use a line address or current-row :s before the substitution; do not use an unchecked % range"),
    ],
    "M1": [
        ("the comma joint becomes a colon while the anchored slope remains unchanged", "/,<CR> searches to the comma joint and r: replaces only that match"),
        ("one consistent slope alphabet lets rise and fall read as one material in motion", "a count of 3 makes yy or dd operate on the entire three-row contour frame"),
        ("the endpoint drifted even though the animation called for only a joint change", "dW deletes one whitespace-delimited punctuation run; dw may stop inside line-art punctuation"),
        ("the mirrored pose keeps the same endpoint and material vocabulary while its direction reverses", "3dd removes the full three-line candidate before its replacement is authored"),
        ("the same joint correction recurs at a known corresponding landmark", "2G0f:r;3j0f:. makes the first r: change and repeats it with . at the second joint"),
        ("the mirrored contour keeps its anchor and declared joint material", "/,<CR>r: finds and replaces the joint without relying on its old column"),
        ("the o endpoint stays fixed while the shallow contour rises, falls, and returns", "; repeats the last f/F/t/T character search; n repeats a / search"),
        ("manual mirroring forces each directional glyph and its placement to be judged", "V2j selects exactly three complete lines before a yank, delete, or replacement"),
        ("only the declared joint material changes from : to ; across the strip", "% gives :s the whole file as its range; an explicit smaller range is safer when unrelated colons exist"),
        ("apply the substitution only to the reviewed contour-frame range", ":1,6s/:/;/g confines the material change to the six owned lines"),
    ],
    "M2": [
        ("the note disappears while all four contour, eye, mouth, and chin rows stay registered", "/note<CR>daw lands on the annotation and deletes that word plus its adjacent space"),
        ("copying the approved whole face preserves its silhouette while a new expression is developed", "gg4yyGp yanks and puts the complete four-row face"),
        ("deleting the mouth with the note exceeds the annotation's text-object boundary", "/note<CR> must establish the correct object before daw runs"),
        ("the eye changes inside an otherwise identical four-row face", "6Gf.ro finds the copied eye and r changes that one character"),
        ("a scoped substitute is useful only when the same known eye spellings recur in owned frames", ":%s/[.o]/O/g matches only . or o, though its range still must be checked"),
        ("the eye remains the acting feature even when the mouth and outer contour differ", "jforO finds the transfer eye by glyph and replaces it without assuming its column"),
        ("the contour stays fixed while the eye progresses from open focus to blink", ":1,4t$ copies the complete four-row face before 10GfOr- changes the new eye"),
        ("the blink belongs to the registered face; an isolated dash has no facial context", "ciw can change a word-sized alphanumeric feature, while r is safer for a single punctuation cell"),
        ("an unbounded substitution could change dots or letters in unrelated faces and annotations", ":1,8s/[.o]/O/g limits the match to two four-row faces; :%s scans the whole file"),
        ("reduce the operator to the eye's actual one-cell or text-object boundary", "use r for one glyph or ciw/ci( only when the feature really occupies that object"),
    ],
    "M3": [
        ("the eye changes from . to o while every body row remains the primary pose", "2G0f(%hro checks the matching head delimiter with %, returns one cell, and replaces the eye"),
        ("a derived key pose must inherit head, torso, legs, and baseline from the approved primary pose", "6yy is the complete-pose yank; yy copies only the current row"),
        ("without torso, legs, and baseline, the copied head is not a registered animation pose", "ggV5j selects all six pose rows before a named-register yank"),
        ("the eye becomes O inside the unchanged parenthesized head and stable body", "8Gci(O<Esc> changes the contents of the parentheses while retaining both delimiters"),
        ("an addressed copy communicates the owned six-line boundary and avoids dependence on cursor position", ":1,6t$ copies exactly the primary pose to the end"),
        ("the unfamiliar arm shape is preserved because the complete selected pose is copied before the eye changes", "ggV5j\"ay stores the pose in register a and G\"ap appends it even if the unnamed register changes"),
        ("head outline, torso, leg spacing, and baseline stay fixed across the acting changes", "14G reaches the final pose's eye row directly; no unused mark detour is needed"),
        ("the acting feature is local; stable anatomy is the continuity evidence between poses", "14Gfo locates the final eye on its own row without revisiting unrelated poses"),
        ("the middle dot supplies a smaller settle accent in the final complete pose", "r<C-k>.M enters the middle-dot digraph at the directly addressed eye cell"),
        ("restore the omitted feet and baseline by copying the complete six-row key pose", "use ggV5j or :1,6t$ so every body row travels together"),
    ],
    "M4": [
        ("the separated upper tip crosses the axis while the lower stroke turns at the fixed column-4 pivot", "C redraws the shifted upper-tip row; a local r turns the lower stroke without touching the pivot row"),
        ("the two readable extremes define the motion arc that the vertical midpoint must bisect", "4G3yyGp copies all three rows of the forward extreme as a working frame"),
        ("one moved tip with an unturned lower stroke reads as a bent or broken prop, not a rigid rotation", "redraw the upper row and replace the lower row's column-4 glyph while excluding the pivot row"),
        ("the vertical tween shares the pivot axis and lies temporally between both complete diagonals", ":1,3t3 inserts a complete frame, C aligns row 4, and <C-v>jr| replaces the true two-cell column"),
        ("the return midpoint is a distinct vertical pose; the appended seam candidate exists only to test loop-boundary diagnosis", "both taught paths redraw rows 10–11, then append the complete first pose by :t or 3yyGp"),
        ("the offset artwork still keeps its pivot registered while a complete middle pose is inserted", ":1,3t3 inserts the frame, then C redraws only its two moving stroke rows"),
        ("backslash, vertical, slash, vertical wraps cleanly to backslash without an adjacent duplicate", "13G3dd removes the repeated first pose from the loop boundary"),
        ("column 4 is the invariant lower-stroke and pivot axis even though the upper tip visits columns 3 and 5", "0 then 3l reaches display column 4 for the lower-stroke r replacement"),
        ("a one-row insertion would leave the prop and pivot split across incompatible frame boundaries", "use 3yy or a three-line :t range for every rotation-frame copy"),
        ("blockwise replacement is valid only for the vertical tween where both moving cells truly share one column", "verify the block covers exactly two midpoint cells at column 4 and excludes the pivot row before r"),
    ],
    "M5": [
        ("one blank directly below the pivot breaks the visible foreground-to-background seam", "4G04lr<Space> replaces exactly the touching background bar without shifting its row"),
        ("all seven composited rows define one frame, so contact, texture bands, and ground must stay registered", "ggV6jyGp selects and appends the complete seven-row composite"),
        ("refilling the break makes the fixed pivot appear fused to the background band", "locate the touching bar on the row below the pivot, then r<Space> changes that one cell"),
        ("the background owns the hole; the swinging foreground rows change while pivot and break remain fixed", "C is safe only on the explicitly chosen copied foreground rows"),
        ("the addressed range states the whole seven-row composite and its insertion point independent of cursor position", ":1,7t7 copies every foreground, contact, texture, and ground row into the gap"),
        ("erase the bar directly below the unfamiliar triangle's visible pivot", "4G05lr<Space> reaches and breaks the transfer seam without editing the foreground"),
        ("every frame retains a fixed pivot with a blank immediately below it, so the layers touch without fusing", "10G0forO accents only the middle pivot and leaves its row-11 break intact"),
        ("erasing foreground damages the readable silhouette instead of separating it from the background", "V6j makes the entire seven-row ownership boundary visible before yanking"),
        ("the seam repair is valid only when its blank shares the fixed pivot's display column", "0 plus the counted l motion makes that fixed-width column explicit before r<Space>"),
        ("replace only the covered stroke with one space and preserve every surrounding texture dot", "r<Space> is a fixed-width one-cell repair; x would shift the remaining texture left"),
    ],
    "M6": [
        ("the apex changes from placeholder to finished form while the base and height stay fixed", "r^ changes the one apex cell in place"),
        ("subtractive authoring begins from a complete approved result so each later omission is deliberate", ":1,5t$ copies the entire finished five-row frame"),
        ("deleting the apex row would collapse the five-row boundary; clearing its content preserves registration", "6G0D blanks the copied apex row without deleting it"),
        ("the first reduction removes the apex while keeping the attached shoulder and complete base", "0D clears the apex row in place, so the remaining form does not float"),
        ("the addressed range protects all five rows before the next upper unit is cleared", ":6,10t$ copies the frame and 12G0D clears row 2 of that copy without deleting it"),
        ("the reduced pose must precede the finished pose so forward playback adds upper units", ":1,5m$ moves the finished transfer frame after its reduced predecessor"),
        ("equal-height frames reveal the pyramid accumulating from reduced form to finished keyframe", "move or copy exact five-line ranges; never reorder single rows independently"),
        ("reverse authoring is efficient because each earlier playback frame removes a bounded unit from the finished form", "verify five rows per pose before a :move so blank padding is not lost"),
        ("a join followed immediately by undo changes nothing and therefore does not count as method coverage", "use 6G0D for the actual subtractive edit and reserve J/u for a lesson where their result matters"),
        ("clear only the chosen upper row while keeping five total rows", "use D on the row's content; dd would remove the padding row"),
    ],
    "M7": [
        ("the repeated incomplete frame creates anticipation immediately before completion", ":1,5t5 copies the complete five-row frame after itself"),
        ("an identical frame is accidental when it has no named timing role and sits after the intended settle", ":16,20t$ copies the full candidate so its later removal can be diagnosed"),
        ("different material bands make the supposed hold flicker instead of pause", "3G0f-v2lr= establishes the bounded band edit and 5j. repeats it in the next frame"),
        ("both anticipation frames preserve the same complete pose for the duration of the hold", "the initial v2lr= change must be repeatable before . is used"),
        ("the material band must remain coherent across holds, intermediate build, completion, and the removable duplicate", "13Gqq0f-v2lr=5jq2@q records the edit on the first unmatched band and replays it on the other two"),
        ("changed art still supports dot repeat when the second acting feature is exactly one frame height away", "2GforO5j. edits the first feature and moves five rows before repeating"),
        ("the anticipation pause remains before completion; the purposeless trailing duplicate is gone", "21G5dd removes exactly the final five-row frame"),
        ("a hold is justified by timing, while material spelling must remain consistent across every frame", "use the hold range for timing edits and a whole-strip exact-pattern operation for shared material"),
        ("the anchored pattern selects only the third row of each five-row frame, not longer hyphen bands", ":g@^  /---@normal! 0f-v2lr= sends the Visual replacement only to matching band rows"),
        ("the recorded vertical move must equal five rows so replay reaches each homologous material band", "record 5j inside q before @q repeats the three-cell Visual edit"),
    ],
    "M8": [
        ("the added underscore marks the leading foot's stable contact with the ground", "G0lr_ reaches the contact cell and replaces it without moving the rest of the foot"),
        ("the passing pose needs the complete registered body as its scaffold before limbs change", "gg5yyGp copies all five rows of the contact pose"),
        ("torso drift breaks registration even if the foot contact itself changes correctly", "use C only on the copied moving rows named by 6G, 7G, 9G, and 10G"),
        ("secondary arm motion may lag the primary foot contact to avoid every part arriving together", "o<C-u> creates each bounded new row; the recipe then types that row directly without filler I/A operations"),
        ("a scoped pattern is useful only when it cannot also match the next pose's head or leg diagonals", ":1,5s@o/@o\\@ confines the arm change to the complete first pose"),
        ("the offset transfer still needs one planted-foot cell while its torso remains registered", "derive the l motion from the visible target cell, then r_ changes only that contact"),
        ("contact and passing poses alternate while the raised arm lags rather than flipping at contact", ":6,10t$ copies the first passing scaffold before lines 16, 17, 19, and 20 are mirrored"),
        ("equal five-row bounds keep head, torso, legs, and contact ground aligned during playback", "5yy copies the whole pose; yy omits four required rows"),
        ("a global slash replacement would corrupt arms, legs, and contour diagonals with different roles", "gg0f/r\\ changes the one raised-arm slash locally"),
        ("repair the planted contact cell while retaining the registered torso and secondary arm", "mark or search the contact landmark in each full pose, verify the column, then use r_ locally"),
    ],
    "M9": [
        ("x becomes the high ball while both rails and the ground line remain registered", "fxro finds and replaces only the plan marker"),
        ("the squash extreme inherits the approved three-row bounds before its subject changes shape", "gg3yyGp copies rails, acting area, and ground together"),
        ("a round O left inside =O= fails to read as the intended flattened squash", "5GfOxi=<Esc> deletes O and inserts = at the same fixed-width cell"),
        ("the readable high and squash extremes define the vertical distance the falling midpoint must connect", "after :1,3t3, C redraws copied rows 4 and 5 while row 6 keeps the ground"),
        ("copy-then-vary is safer when rails and ground remain identical between poses", ":1,3t3 inserts the high frame between extremes before only its acting rows change"),
        ("the x marker remains the acting subject even when transfer rails and horizontal offset change", "fx followed by r finds the marker by glyph instead of memorised column"),
        ("high, falling, squash, and larger rebound O create descent, impact, overshoot, then seam settle", ":1,3t$ copies the complete high frame before 10GforO enlarges only its rebound subject"),
        ("the larger O follows the squash as a rebound extreme and then resolves to the smaller first-frame o", "10GforO changes only the copied rebound subject"),
        ("drawing the midpoint first hides whether the high and squash extremes independently communicate the action", "author both extremes first, then use :t to insert the falling frame between them"),
        ("a one-row subject omits the rails and registered ground needed to judge vertical motion", "use 3yy or a three-line :t range for every bounce frame"),
    ],
    "M10": [
        ("the missing shoulder partner becomes ヽ while the two lower contour rows stay registered", "$rヽ changes the final glyph of the first row without shifting the frame"),
        ("the full lobe is the readable primary pose from which the wider extreme is derived", "gg3yyGp copies all three proportional rows as the expansion scaffold"),
        ("a wide shoulder over a narrow old bowl makes the puff shear instead of expand as one pose", "C redraws lines 4, 5, and 6 so the copied outline changes as a complete frame"),
        ("￣ above ＿ carries complementary horizontal contour positions across adjacent rows", "keep them on separate rows; J would destroy the vertical occlusion relationship"),
        ("the duplicate sustains the hatched impact for two frames before the settle", ":7,9t$ copies all three rows of the impact pose"),
        ("the two lower rows remain the registered body of the changed shoulder pose", "$rヽ completes ｀ヽ without using a terminal-column assumption"),
        ("lobe, arch, hatched impact, impact hold, lobe reads as expansion, impact, and settle", ":1,3t$ appends the complete primary lobe as the settle"),
        ("bounded hatching reads as an impact material only while the outline contains it", "edit only the middle hatching row; do not substitute across either contour row"),
        ("exact text proves transcription, but the intended shape still requires a Saitamaar true-advance render", "the Neovim command proves the Unicode buffer; the Saitamaar preview supplies the visual evidence"),
        ("the Saitamaar render wins because proportional advance widths—not terminal cells—define the authored shape", "revise the glyph-and-space combination after measuring the true-advance preview, then re-enter that bounded text edit"),
    ],
    "M11": [
        ("the first roof changes from -- to == while both / and \\ endpoints remain in their columns", "0lR==<Esc> overwrites exactly the two roof cells"),
        ("the derived tension pose needs the same roof bounds, paired indicators, and base", "gg3yyGp copies all three registered rows"),
        ("inserting two extra cells changed row length and moved the right wall, so the pose no longer registers", "R replaces the existing cells in place; i would grow the row unless old cells were deleted"),
        ("undo visibly returns the copied roof to == and redo reapplies ~~ as the saved slack extreme", "4G0lR~~<Esc>u<C-r> makes both recovery operations causally necessary"),
        ("only the two copied-pose indicators brighten from o to O; the shell and base remain stable", "5G0forO5lrO and 5G:s/o/O/g<CR> are the two accepted bounded paths"),
        ("the shell glyphs may change, but the owned two-cell roof run must be overwritten without changing width", "0lR==<Esc> transfers the method without depending on slash endpoints"),
        ("two registered vertical trails lag the material change and read as aligned motion blur", "both insertions target display column 14, so the secondary effect does not jitter"),
        ("column 14 is part of the planned frame even where the stored line is shorter", ":set virtualedit=all permits 13| to position before that column before i| writes the trail"),
        ("the two original roof cells become == and the endpoint columns do not move", "Replace mode consumes the old cells; Insert mode would push the remainder right"),
        ("a one-column trail mismatch reads as secondary-motion jitter between otherwise registered frames", "2G13|i|<Esc>3j. inserts at column 14, moves one frame height, and repeats there"),
    ],
    "M12": [
        ("only the left upper joint changes from : to !; the axis, outline, and right joint stay registered", "0t: stops before the first :, then l reaches it and r! replaces it in place"),
        ("the copied pose preserves all three rows so the right activation is a coherent derived key pose", "4G$T: stops just after the right :, then h reaches it for r!"),
        ("the intended left-to-right stagger disappeared because the first pose activated both sides", "0t:lr! changes only the first visible joint and leaves its mirror for the next pose"),
        ("the one-frame delay makes the lower response read as drag rather than simultaneous flashing", "8G0f:;r!,r! reaches the second joint with ;, edits it, then returns with , to edit the first"),
        ("both base cells are one bounded material change on the copied release row", ":1,3t$ then 12G0forO;rO or 12G:s/o/O/g reaches the same scoped result"),
        ("the centre axis and homologous distances remain fixed while directional endpoints are redrawn by eye", "0t+lr*$T+hr* approaches the paired changed-art joints from opposite directions"),
        ("the acting accent travels left to both upper joints, drags into the lower pair, releases, then exits right", ":1,3t$ copies the complete first pose before line 13 receives the mirrored accent exchange"),
        ("the slash endpoints must keep their outward directions; only the acting punctuation exchanges sides", "change the left ! back to : and the right : to ! without reversing the stored row"),
        ("t: leaves the cursor on the cell immediately before the colon, not on the colon itself", "l advances onto the joint and r! overwrites that one cell without shifting its neighbours"),
        ("retaining both bangs turns the return into another simultaneous hold instead of an opposite-side exit", "13G0t!lr:$T:hr! clears the left accent and creates only its right mirror"),
    ],
    "M13": [
        ("only the centre cluster's first cell changes to ! while all widths and support rows stay registered", "W reaches the next whitespace-separated punctuation WORD and r! changes its first cell in place"),
        ("copying all three rows preserves the material and its anchors before the acting accent advances", "4GWr.Wr! clears the copied centre start, advances one WORD, and accents the right start"),
        ("closing a gap shifts later landmarks, so the texture no longer registers between frames", "r overwrites one cell after a WORD motion; x or d would shorten the row and move every later cluster"),
        ("the pulse broadens from one cluster to three separated edges before the brighter flash", "Er!2Wr.Er!2Br! addresses first end, third start/end, and centre start without column counts"),
        ("the three acting cells share one material change on the copied row while both supports remain stable", "10G0f!r*;r*;r* and 10G:s/!/*/g are accepted bounded paths to the same row result"),
        ("the accent still moves across three whitespace-separated clusters despite their changed material", "2Wr+ reaches the third WORD and Br+ returns to the centre WORD"),
        ("the accent travels centre to right, expands, flashes, and exits left across registered supports", ":1,3t$ copies the complete centre-pulse pose before 13GWr.Br! moves its accent left"),
        ("stable support rows make the changing first-row texture readable as material motion rather than camera drift", "the line-7/10/13 addresses constrain edits to acting rows and leave both support rows untouched"),
        ("W lands on the first cell of the second whitespace-delimited punctuation cluster", "uppercase W treats each punctuation run as one WORD; lowercase w may stop at internal punctuation classes"),
        ("an unbounded flash destroys earlier timing states or stable support material", "use a current-row :s after an exact line address, or an explicit owned range, rather than :%s"),
    ],
    "M14": [
        ("only the eye changes from o to the exact visible * palette glyph; the three-row outline stays registered", "f*\"ayl stores * in register a, then j0foR<C-r>a<Esc> overwrites the eye from that register"),
        ("a declared palette keeps variant glyph identity consistent across the saved file", "\"ayl yanks the selected one-cell palette entry into register a without relying on the unnamed register"),
        ("insertion changed row width and therefore broke silhouette registration", "Replace mode consumes the old eye cell while `<C-r>a` supplies the register text; ordinary Insert mode would shift the wall"),
        ("the second complete face is a plus-eye variant of the same silhouette", "5Gf+\"aylj0f*R<C-r>a<Esc> stores + and replaces only the copied eye"),
        ("both methods append the complete second face plus its blank separator as the third variant", "5Gyapgg}jP uses semantic paragraph scope and frame-boundary put; :5,8t$ uses a verified numeric range"),
        ("the changed shell stays fixed while its acting cell receives the exact unfamiliar palette glyph", "fx\"aylj0f.R<C-r>a<Esc> stores x and retrieves it through Replace mode"),
        ("one silhouette persists while its palette-owned eye reads star, plus, then star", "gg}}jj reaches the third frame's eye row after two paragraph boundaries"),
        ("a valid variant contains all three art rows and its separator, not an isolated eye row", "yap owns the current blank-line-separated paragraph before Gp appends it"),
        ("the return to star closes the material-variant sequence without redrawing the face", "register b stores the first star and R<C-r>b retrieves it after paragraph navigation"),
        ("each frame must be bounded by one blank separator before objectwise copying is safe", "inspect the paragraph boundary for yap, or state all four owned lines explicitly in the :t range"),
    ],
    "M15": [
        ("only the repeated brick band shifts one cell; the dither and angled shadow stay registered", "shiftwidth=1 defines a one-cell indent and >> applies exactly one such indent to the selected row"),
        ("the three-row copy preserves the material stack before a derived texture treatment is authored", "gg3yyGp yanks and appends all three rows; yy alone would detach one material band"),
        ("a two-cell jump breaks the planned stagger and makes the brick pan visibly lurch", ":set shiftwidth=1 makes one >> operation equal one fixed-grid cell"),
        ("lower dither density reads as a lighter surface while row width and support geometry remain unchanged", ":4s/:/./g changes only colon marks on the copied top row"),
        ("both methods append one vertical occluder at each of the three owned row ends", "blockwise $A follows selected row ends; :4,6s/$/|/ states the owned line range directly"),
        ("the unfamiliar motifs change, but exactly one repeated-material row moves exactly one cell", "j:set shiftwidth=1<CR>>> selects the changed brick row and applies one declared indent"),
        ("the stable angled base preserves depth while the surface treatment changes above it", "addresses 4 through 6 own the middle frame, while line 7 owns only the appended settle dither"),
        ("the shadow has its own dense material rule and must remain a stable depth cue", "use :4s/:/./g or another exact line address instead of a file-wide substitution"),
        ("recording removes four opportunities to mistype the same landmark edit and preserves its rhythm", "qqf:r.q records one search-and-replace; 3@q repeats it at the remaining three colons"),
        ("the replay count exceeded the four owned colon landmarks and escaped the acting dither row", "verify f: has four matches on line 7, record one replacement, and replay exactly three times"),
    ],
    "M16": [
        ("the compact pose is readable at intended size and the plan records both identity and 8 FPS timing", "Gk0f0<C-a> reaches F00 and increments its numeric field to F01 without retyping the line"),
        ("saving the plate makes the approved reference, size test, identity, and playback rate one reproducible source", ":read % reads the current file from disk, so that saved file must be the reviewed source plate"),
        ("duplicate identifiers make later pose order and timing evidence ambiguous", "CTRL-A increments the number under the cursor and retains the F02 zero-padded spelling"),
        ("copying preserves the approved size-test silhouette and timing while only planned identity advances", ":1,5t$ copies all five owned lines and 2<C-a> advances F01 to F03"),
        ("whole-block reordering can test key-pose priority without changing the drawings themselves", ":6,10m0 and 6GV4jdggP both move exactly the second five-line block before the first"),
        ("the unfamiliar pose still remains intact while only its written frame number advances", "Gk0f3<C-a> increments F03 and leaves T12 FPS untouched"),
        ("key-pose order and timing are still a written hypothesis until in-betweens and playback test it", "the owned boundary is three art rows plus the F label and T FPS line"),
        ("FPS determines how many planned frames fit the intended duration before detail work grows", "the T08 FPS line stays fixed while CTRL-A operates only on the F label"),
        ("a split block destroys provenance between the pose, identifier, and timing decision", "the complete owned range is five lines, such as :1,5 or :6,10"),
        ("the new plan would inherit an obsolete pose or timing decision and no longer match its claimed reference", "write and inspect the intended source file before reading it back with :read %"),
    ],
    "M17": [
        ("the eye cell is homologous while the surrounding upper and lower contours form distinct poses", "/x<CR>ro changes the first anchor and each n. reaches the next match and repeats ro"),
        ("copying preserves the complete coherent anchor before a new shell extreme is authored around it", "7G3yyGp copies all three rows; a one-line yank would detach the eye from its pose"),
        ("the old glyph flashes for one frame and breaks temporal coherence at a supposedly stable feature", "one of the two required n. repetitions was omitted after the first searched replacement"),
        ("only the copied top joint and lower material change; the middle eye row stays byte-for-byte stable", "10G0f^r-2j0f_r- replaces the two declared contour landmarks and never visits the eye row"),
        ("both methods perform one intentional material pass over the same four proven eye lines", "the o pattern must select only one eye-bearing row per frame before :global normal is safe"),
        ("the shell vocabulary changes, but x occupies the same semantic eye role in all three frames", "/x<CR>ron.n. updates exactly those three matches without stored columns"),
        ("eye material changes coherently from o to star while all four shell poses remain distinct", "search-plus-dot or the bounded :global normal pass edits one homologous cell per frame"),
        ("a stable eye lets viewers attribute motion to the changing shell rather than camera or registration drift", "count the owned eye matches and replay only across the remaining anchors"),
        ("the macro packages replacement and traversal so each replay begins on the next corresponding eye", "the n inside qqr+nq advances from the edited anchor to the next search match"),
        ("the replay count exceeded the three remaining eye anchors, wrapped, and edited an already-processed frame", "after recording one of four matches, use exactly 3@q and inspect all four results"),
    ],
    "M18": [
        ("the actor, arrowhead, arm slash, leg slashes, and spacing all exchange direction while rail width stays fixed", "three explicit C overwrites author the target rows directly and contain no reverse or transform command"),
        ("the approved return preserves directional decisions before a controlled one-cell overshoot is developed", "gg4yyGp copies the three art rows together with CHECK=0"),
        ("the pose is not a mirror because its directional vocabulary contradicts its new screen position", "overwrite each complete art row so every arrowhead, slash, and space is deliberately chosen"),
        ("the overshoot carries momentum one cell beyond the return extreme before the motion reverses", "line 5 and two following row overwrites place all three body rows at the same new offset"),
        ("the expression is evidence about finished art, not an authoring shortcut for directional geometry", "the substitute targets only 0 on CHECK and getline() merely tests the already-authored top row"),
        ("all directional marks and spacing are newly judged even though the unfamiliar materials differ", "the exact C path overwrites all three rows and leaves CHECK pending for separate validation"),
        ("the repeated overshoot creates a turnaround hold before the approved poses play backward", ":5,8t$ appends the overshoot and :1,4t$ appends the earlier return extreme"),
        ("its duplicate metadata names a two-frame turnaround hold that playback intentionally preserves", "the two copied four-line ranges produce an explicit F1, F2, F2, F1 sequence"),
        ("byte order is not visual mirroring because directional glyph semantics must also exchange", "complete-row C overwrites force explicit decisions for slash pairs and arrowheads"),
        ("automation could reach the pixels without proving the learner can author a mirror by eye", "\\= may calculate only the CHECK digit from existing art; it may not emit any art row"),
    ],
}


def visual_pair(before, after):
    """Render a concept stimulus as art, never as a flattened slash summary."""
    width = max([len(row) for row in before + after] or [1])
    lines = ["    " + "BEFORE".ljust(width + 2) + "   AFTER"]
    for left, right in zip(before, after):
        lines.append(f"    │{left.ljust(width)}│   │{right.ljust(width)}│")
    return "\n".join(lines)


def visual_sequence(rows, frame_rows):
    """Present a short strip with explicit frame boundaries for motion questions."""
    if not frame_rows:
        return "\n".join(f"    │{row}│" for row in rows)
    frames = [rows[index:index + frame_rows] for index in range(0, len(rows), frame_rows)]
    width = max([len(row) for row in rows] or [1])
    blocks = []
    columns = max(1, 68 // (width + 5))
    for first in range(0, len(frames), columns):
        group = frames[first:first + columns]
        labels = [f"FRAME {first + offset + 1}".ljust(width + 2)
                  for offset in range(len(group))]
        blocks.append("    " + "   ".join(labels).rstrip())
        for row_index in range(frame_rows):
            cells = [f"│{frame[row_index].ljust(width)}│" for frame in group]
            blocks.append("    " + "   ".join(cells))
        if first + columns < len(frames):
            blocks.append("")
    return "\n".join(blocks)


def question(module, number):
    mid, title = module["id"], module["title"]
    first = module["steps"][0]
    comparison = visual_pair(first["start"], first["target"])
    sequence = visual_sequence(module["steps"][-1]["target"], module.get("frame_rows"))
    animation_prompt, neovim_prompt = QUESTION_PROMPTS[mid][number - 1]
    animation_correct, neovim_correct = QUESTION_ANSWERS[mid][number - 1]

    visual = {
        1: comparison,
        3: comparison,
        6: visual_pair(module["transfer"]["start"], module["transfer"]["target"]),
        7: sequence,
        10: comparison,
    }.get(number)
    if visual:
        animation_prompt = f"{animation_prompt}\n\n{visual}"

    if number == 1:
        animation_wrong = FIRST_READING_DISTRACTORS[mid]
    elif number == 3:
        animation_wrong = [
            f"the intended acting change occurs while the registered {title} landmarks stay fixed",
            f"the {title} frame keeps its declared height and complete subject boundary",
            "a repeated complete frame has an explicit, declared timing role in the sequence",
        ]
    else:
        animation_wrong = [
            f"move the registered {title} subject while leaving its intended acting feature unchanged",
            "redraw every row so no stable landmark survives between adjacent frames",
            "treat any identical text as motion even when no hold or timing purpose was declared",
        ]
    other_vim = QUESTION_ANSWERS[mid][number % 10][1]
    if other_vim == neovim_correct:
        other_vim = QUESTION_ANSWERS[mid][(number + 1) % 10][1]
    neovim_wrong = [
        f"{other_vim} — this performs a different {title} task",
        "dd — delete the entire cursor line even though the requested edit owns a smaller object",
        ":%s/.../.../g — rewrite every match in the project without first proving that scope is safe",
    ]

    prompt = (
        f"ANIMATION\n{animation_prompt}\n\n"
        f"NEOVIM\n{neovim_prompt}\n\n"
        "Choose the option that gets BOTH the animation/authoring reading and "
        "the Neovim decision right."
    )

    def paired(animation, neovim):
        return f"ANIMATION: {animation} | NEOVIM: {neovim}"

    correct = paired(animation_correct, neovim_correct)
    records = [
        (animation_correct, neovim_correct, None),
        (animation_correct, neovim_wrong[0],
         f"The animation half is supported, but the Vim half chooses the wrong task: {neovim_wrong[0]}. Use {neovim_correct}."),
        (animation_wrong[0], neovim_correct,
         f"The Vim half is bounded correctly, but the animation half claims '{animation_wrong[0]}'. The visible evidence supports: {animation_correct}."),
        (animation_wrong[0], neovim_wrong[0],
         f"Both halves fail: the animation claim '{animation_wrong[0]}' contradicts the displayed frames, and the Vim path chooses another task: {neovim_wrong[0]}. The supported pair is animation '{animation_correct}' with Vim '{neovim_correct}'."),
    ]
    choices = [paired(animation, neovim) for animation, neovim, _error in records]
    compact_choices = []
    for choice in choices:
        animation_part, neovim_part = choice.split(" | NEOVIM: ", 1)
        animation_part = animation_part.removeprefix("ANIMATION: ")
        compact_choices.append("A: %s · V: %s" % (
            textwrap.shorten(animation_part, width=30, placeholder="…"),
            textwrap.shorten(neovim_part, width=30, placeholder="…"),
        ))
    visual = ""
    if "\n\n" in animation_prompt:
        _lead, visual = animation_prompt.split("\n\n", 1)
        visual = "\n\n" + visual
    compact_prompt = (
        "ANIMATION: read the complete frames; choose the supported motion."
        f"{visual}\n\nNEOVIM: "
        f"{textwrap.shorten(neovim_prompt, width=64, placeholder='…')}\n"
        "Choose the option whose A and V halves are BOTH correct."
    )
    # Rotate the correct answer so the bank does not teach “always choose a”.
    shift = (number + int(mid[1:])) % len(choices)
    records = records[shift:] + records[:shift]
    choices = choices[shift:] + choices[:shift]
    compact_choices = compact_choices[shift:] + compact_choices[:shift]
    correct_index = choices.index(correct)
    feedback = [
        (f"Correct for {title}. Animation: {animation_correct}. Neovim: {neovim_correct}."
         if error is None else error)
        for _animation, _neovim, error in records
    ]
    return {
        "id": f"{mid}.Q{number:02d}", "module_id": mid,
        "card_id": f"{mid}.03" if number <= 5 else f"{mid}.07",
        "form": "multiple_choice",
        "grammar_family": "paired-animation-neovim-diagnosis",
        "grammar_breakdown_id": "paired-animation-neovim-diagnosis",
        "grammar_breakdown": [
            "read the visible animation evidence",
            "name the bounded Neovim action and scope",
            "reject any answer whose animation or Neovim half is wrong",
        ],
        "paired_invariant": module["principle"],
        "placement": "before",
        "placement_reason": (
            "The learner must interpret the visible animation evidence and bounded edit "
            "before the concept or diagnosis card can advance."
        ),
        "type": {
            1: "visual_reading", 2: "principle_choice", 3: "diagnosis",
            4: "command_prediction", 5: "method_comparison", 6: "transfer_reasoning",
            7: "coherence_check", 8: "principle_application", 9: "output_prediction",
            10: "risk_diagnosis",
        }[number],
        "prompt": prompt, "choices": choices, "correct_choice": correct_index,
        "feedback": feedback, "variant_group": f"{mid}.concept-{(number - 1) // 2}",
        "source_ref": module["source_ref"], "difficulty": 1 + (number - 1) // 4,
        "animation_prompt": animation_prompt, "animation_answer": animation_correct,
        "neovim_prompt": neovim_prompt, "neovim_answer": neovim_correct,
        "compact_prompt": compact_prompt, "compact_choices": compact_choices,
        "answer_contract": {"form": "multiple_choice"},
    }


FAMILY_DEFS = {
    "normal-motion": {
        "class": "standalone_normal",
        "grammar": "motion or landmark command + optional count; movement alone must not change art",
        "terms": [["motion", "move", "cursor"], ["landmark", "row", "column", "cell"]],
    },
    "normal-replace": {
        "class": "standalone_normal",
        "grammar": "r + replacement glyph; overwrite one cell without shifting the row",
        "terms": [["replace", "overwrite", "r"], ["cell", "glyph"], ["width", "shift", "registered"]],
    },
    "change-to-end": {
        "class": "operator",
        "grammar": "C is c$; change from the cursor through row end, type replacement text, then <Esc>",
        "terms": [["change", "operator", "C"], ["end", "row", "line"], ["escape", "normal"], ["width", "shift"]],
    },
    "linewise-yank-put": {
        "class": "standalone_normal",
        "grammar": "count + yy copies whole rows; p/P puts the linewise object below/above",
        "terms": [["yank", "copy"], ["line", "row", "frame"], ["put", "paste"]],
    },
    "linewise-delete": {
        "class": "operator",
        "grammar": "count + dd deletes whole rows; D is d$ and deletes from the cursor to row end",
        "terms": [["delete", "operator"], ["line", "row", "end"], ["count", "scope"]],
    },
    "normal-open-line": {
        "class": "standalone_normal",
        "grammar": "o/O opens one row below/above and enters Insert; <Esc> returns to Normal",
        "terms": [["open", "new line", "new row", "o"], ["below", "above"], ["escape", "normal"]],
    },
    "ex-substitute": {
        "class": "ex",
        "grammar": ["address/range", "s command", "pattern", "replacement", "flags", "<CR> execution"],
        "terms": [["range", "address", "line"], ["substitute", "replace"], ["pattern"], ["flag", "global", "g"], ["enter", "execute"]],
    },
    "ex-substitute-line": {
        "class": "ex",
        "grammar": "current-line address + s command + pattern + replacement + flags + <CR>",
        "terms": [["current line", "line"], ["substitute", "replace"], ["pattern"], ["replacement"], ["flag", "global", "g"], ["enter", "execute"]],
    },
    "ex-substitute-range": {
        "class": "ex",
        "grammar": "explicit line range + s command + pattern + replacement + flags + <CR>",
        "terms": [["range", "address", "lines"], ["substitute", "replace"], ["pattern"], ["replacement"], ["flag", "global", "g"], ["enter", "execute"]],
    },
    "ex-copy": {
        "class": "ex",
        "grammar": ["source address/range", "t/copy command", "destination address", "<CR> execution"],
        "terms": [["range", "source", "lines", "rows"], ["copy", "t"], ["destination", "after", "end"], ["enter", "execute"]],
    },
    "ex-move": {
        "class": "ex",
        "grammar": ["source address/range", "m/move command", "destination address", "<CR> execution"],
        "terms": [["range", "source", "lines", "rows"], ["move"], ["destination", "after", "before"]],
    },
    "operator-motion-object": {
        "class": "operator",
        "grammar": "[count] operator [count] motion-or-text-object",
        "terms": [["operator", "verb"], ["motion", "object", "noun"], ["scope", "count"]],
    },
    "visual-scope": {
        "class": "visual",
        "grammar": "Visual mode + bounded selection + operator; selection shape owns the edit scope",
        "terms": [["visual", "selection"], ["line", "block", "column", "scope"]],
    },
    "repeat": {
        "class": "standalone_normal",
        "grammar": ". repeats the last change; n/N and ;/, repeat searches or character finds",
        "terms": [["repeat", "dot", "next"], ["change", "search", "find"]],
    },
    "char-find-repeat": {
        "class": "standalone_normal",
        "grammar": "f/t landmark + ; repeat in the same direction or , repeat in reverse",
        "terms": [["find", "landmark", "f", "t"], ["semicolon", ";", "repeat"], ["comma", ",", "backwards"]],
    },
    "paragraph-next": {
        "class": "standalone_normal",
        "grammar": "} moves to the next blank-line-separated paragraph/frame",
        "terms": [["paragraph", "frame", "blank line"], ["next", "forward", "}"], ["boundary", "scope"]],
    },
    "put-before": {
        "class": "standalone_normal",
        "grammar": "P puts the yanked object before the cursor or above the current line",
        "terms": [["put", "paste", "P"], ["before", "above"], ["register", "yank", "copy"]],
    },
    "visual-characterwise": {
        "class": "visual",
        "grammar": "v starts a characterwise selection; a Visual operator acts only on selected cells",
        "terms": [["visual", "v", "selection"], ["character", "cell"], ["scope", "operator"]],
    },
    "block-append": {
        "class": "visual",
        "grammar": "Ctrl-v block + $A appends the typed glyph at the end of every selected row",
        "terms": [["block", "Ctrl-v", "column"], ["end", "$", "A", "append"], ["each row", "scope"]],
    },
    "register": {
        "class": "standalone_normal",
        "grammar": "\"{register} selects storage; yank fills it and p/P or <C-r>{register} retrieves it",
        "terms": [["register", "palette"], ["yank", "copy"], ["put", "retrieve", "paste"]],
    },
    "macro": {
        "class": "standalone_normal",
        "grammar": "q{register} records bounded edits; q stops; @{register} replays at a homologous anchor",
        "terms": [["record", "macro"], ["register"], ["replay", "repeat"]],
    },
    "global-normal": {
        "class": "ex",
        "grammar": ["global selector", "matching pattern", "normal! command", "bounded Normal payload", "<CR> execution"],
        "terms": [["global", ":g", "selector"], ["pattern", "match"], ["normal", "payload"], ["enter", "execute"]],
    },
    "digraph": {
        "class": "standalone_normal",
        "grammar": "in Insert/Replace entry, <C-k> plus a two-character digraph inserts one Unicode glyph",
        "terms": [["digraph", "unicode"], ["ctrl-k", "<c-k>"], ["glyph", "character"]],
    },
    "virtual-column": {
        "class": "ex",
        "grammar": ":set virtualedit=all permits N| to address an empty fixed-width column past row end",
        "terms": [["virtualedit", "empty"], ["column", "n|", "exact"], ["padding", "registered"]],
    },
    "undo-redo": {
        "class": "standalone_normal",
        "grammar": "u undoes one change; <C-r> redoes it so recovery can be inspected without retyping",
        "terms": [["undo", "u"], ["redo", "ctrl-r", "<c-r>"], ["change", "restore"]],
    },
    "word-boundary": {
        "class": "standalone_normal",
        "grammar": "W/B move by WORD starts; E lands at a WORD end; counts scale the boundary motion",
        "terms": [["word", "boundary"], ["start", "end"], ["forward", "backward"], ["count", "scope"]],
    },
    "expression-substitute": {
        "class": "ex",
        "grammar": ["address/range", "s command", "pattern", "\\= expression replacement", "<CR> execution"],
        "terms": [["range", "address"], ["substitute", "pattern"], ["expression", "\\="], ["getline", "validation"], ["enter", "execute"]],
    },
    "replace-mode": {
        "class": "standalone_normal",
        "grammar": "R enters Replace mode; typed glyphs overwrite cells until <Esc>",
        "terms": [["replace mode", "overwrite"], ["escape", "normal"], ["width", "shift"]],
    },
    "search-landmark": {
        "class": "standalone_normal",
        "grammar": "/pattern<CR> searches; f/t land on or before a visible character landmark",
        "terms": [["search", "find", "landmark"], ["pattern", "character"], ["cursor", "cell"]],
    },
    "ex-command": {
        "class": "ex",
        "grammar": ["address/range when needed", "command", "arguments", "flags when needed", "<CR> execution"],
        "terms": [["command"], ["argument", "range", "address"], ["enter", "execute"]],
    },
}


# Comparison cards ask a free-text "why" only after the learner has used one
# method and the debrief has named both.  Each contract below is tied to that
# exact animation and those exact methods; a stock answer from another module
# must not pass (VD-21/22).
WHY_SPECS = {
    "M0.05": {
        "question": "When is addressed copy safer than counted yank/put, and what complete object must both methods duplicate?",
        "groups": [["address", "range", "7,9"], ["cursor", "position"], ["three-row", "three row", "flare", "frame"]],
        "sample": "Addressed copy does not depend on cursor position; both methods must duplicate the complete three-row flare frame.",
    },
    "M1.05": {
        "question": "How do local edit plus dot and bounded substitution differ, and which joint-only scope must both preserve?",
        "groups": [["dot", "repeat", "local"], ["substitute", "pattern"], ["joint", "colon", "semicolon"]],
        "sample": "Dot repeats a verified local joint edit; substitution uses a joint pattern, and both must change only the colon joints to semicolons.",
    },
    "M2.05": {
        "question": "Why might two local eye replacements be safer than a regex, and what must a scoped substitute avoid matching?",
        "groups": [["local", "each eye", "two eye"], ["substitute", "regex", "pattern"], ["contour", "outline"]],
        "sample": "Local replacements visit each eye explicitly; a scoped regex is shorter but must match only eye spellings and never the contour.",
    },
    "M3.05": {
        "question": "What cursor assumption separates counted yank/put from addressed copy, and how many pose rows belong to the object?",
        "groups": [["cursor", "position"], ["address", "1,6", "range"], ["six", "6", "pose rows"]],
        "sample": "Counted yank starts from the correct cursor row; addressed copy names lines 1 through 6, and both copy all six pose rows.",
    },
    "M4.05": {
        "question": "Why must either seam method copy the complete first frame after redrawing the return midpoint, rather than only the changed cells?",
        "groups": [["return", "midpoint"], ["complete", "three-row", "three row", "first frame"], ["seam", "loop", "registration"]],
        "sample": "After redrawing the return midpoint, both methods copy the complete three-row first frame so registration closes the loop seam.",
    },
    "M5.05": {
        "question": "What does an addressed seven-row midpoint protect that counted yank must track by cursor, and which rows are redrawn afterward?",
        "groups": [["seven", "7", "range"], ["cursor", "count"], ["moving", "foreground", "rows"]],
        "sample": "The addressed range protects all seven midpoint rows; counted yank relies on cursor and count, then only the moving foreground rows are redrawn.",
    },
    "M6.05": {
        "question": "After copying the five-row build, why does either method clear the copied shoulder row instead of deleting that row?",
        "groups": [["five", "5", "frame", "build"], ["clear", "D"], ["delete row", "height", "registration"]],
        "sample": "Both methods copy the complete five-row build and clear the shoulder with D; deleting the row would collapse frame height and registration.",
    },
    "M7.05": {
        "question": "When is a recorded five-row-step macro appropriate, when is :global safer, and which material-band rows may change?",
        "groups": [["macro", "record"], ["global", ":g", "pattern"], ["material", "band", "matching rows"]],
        "sample": "The macro is safe at homologous anchors five rows apart; :global is safer when a pattern selects only the exact material-band rows.",
    },
    "M8.05": {
        "question": "Why does the ranged substitute name the complete first pose, while the local method may touch only its arm cell?",
        "groups": [["range", "1,5", "first pose"], ["local", "arm", "cell"], ["other pose", "outside", "unchanged"]],
        "sample": "The substitution range limits the pattern to lines 1–5 of the first pose; the local method changes one arm cell and leaves other poses unchanged.",
    },
    "M9.05": {
        "question": "What registration does copy-then-vary preserve, and what must direct row authoring reproduce exactly in the falling midpoint?",
        "groups": [["copy", "registered"], ["rail", "ground"], ["three", "3", "rows", "midpoint"]],
        "sample": "Copy-then-vary preserves the registered rails and ground; direct authoring must reproduce all three bounded midpoint rows exactly.",
    },
    "M10.05": {
        "question": "Why can an addressed range be safer than counted yank for the impact pose, and what three-row hatched object must stay intact?",
        "groups": [["address", "range", "7,9"], ["cursor", "position"], ["impact", "three-row", "hatch"]],
        "sample": "The addressed range avoids cursor-position dependence; both methods copy the complete three-row hatched impact pose.",
    },
    "M11.05": {
        "question": "How does current-row substitution bound the two indicator changes, and what would an unbounded substitution risk?",
        "groups": [["current row", "copied row"], ["two", "2", "indicator"], ["other row", "outside", "unbounded"]],
        "sample": "Current-row substitution changes both indicators on the copied row only; an unbounded substitute could alter indicators in other frames.",
    },
    "M12.05": {
        "question": "Compare repeated character search with row-scoped substitution: what two base cells are owned, and which scope must not expand?",
        "groups": [["search", ";", "repeat"], ["substitute", "row"], ["two", "2", "base cells"]],
        "sample": "Repeated search visits the two base cells; row-scoped substitution changes those same two cells without expanding beyond the copied row.",
    },
    "M13.05": {
        "question": "Why are repeated landmark edits and a row-scoped material substitute equivalent only when exactly three acting cells are owned?",
        "groups": [["landmark", "find", ";"], ["substitute", "row"], ["three", "3", "acting cells"]],
        "sample": "Landmark repeats visit each of the three acting cells; the row-scoped substitute is equivalent only because it matches those three cells and no others.",
    },
    "M14.05": {
        "question": "What boundary does yap discover that an addressed copy must count explicitly, and why must the blank separator travel with the frame?",
        "groups": [["paragraph", "yap", "boundary"], ["address", "four", "4", "lines"], ["blank", "separator", "frame"]],
        "sample": "yap discovers the paragraph boundary; addressed copy must name all four lines, including the blank separator that keeps frames distinct.",
    },
    "M15.05": {
        "question": "How do blockwise $A and a bounded range substitution reach the same row ends without shifting the texture frame?",
        "groups": [["block", "$A", "visual"], ["range", "substitute"], ["three", "3", "row ends", "width"]],
        "sample": "Blockwise $A appends at all three selected row ends; bounded substitution owns the same three-row range, and neither shifts existing cells.",
    },
    "M16.05": {
        "question": "Why must both the addressed move and linewise delete/put own the same five-line plan block rather than individual rows?",
        "groups": [["move", ":m", "address"], ["delete", "put", "visual"], ["five", "5", "block", "lines"]],
        "sample": "The Ex move addresses the five-line block directly; Visual delete/put selects those same five lines so the plan stays intact.",
    },
    "M17.05": {
        "question": "When does search plus dot risk the wrong match, and how does :global restrict the eye replacement pass?",
        "groups": [["search", "dot", "next match"], ["global", ":g", "pattern"], ["eye", "o", "matching lines"]],
        "sample": "Search plus dot depends on each next match being an eye; :global restricts the Normal replacement to lines selected by the eye pattern.",
    },
    "M18.05": {
        "question": "Why may the expression method derive check digits but never generate mirrored art, and what does the manual method inspect?",
        "groups": [["expression", "derive"], ["check", "digit", "marker"], ["art", "mirror", "top row", "frame"]],
        "sample": "The expression derives only each check digit from an already-authored frame row; the manual method inspects both frames, and neither generates mirrored art.",
    },
}


MASTER_COVERAGE = {
    "M0": (["H1", "H3"], ["S0", "A0"]),
    "M1": (["H2"], ["S1", "A1"]),
    "M2": (["H1", "H2"], ["S3", "A1"]),
    "M3": (["H3"], ["S2", "A2"]),
    "M4": (["H2", "H4", "H7"], ["S4", "A2"]),
    "M5": (["H3", "H4", "H7"], ["S6", "A4"]),
    "M6": (["H3", "H9"], ["A5"]),
    "M7": (["H5"], ["A4", "A6"]),
    "M8": (["H2", "H8"], ["A4", "A7"]),
    "M9": (["H1", "H3", "H9"], ["A0", "A4", "A7"]),
    "M10": (["H2"], ["S5", "P"]),
    "M11": (["H1", "H4", "H5"], ["S0", "A3"]),
    "M12": (["H2", "H5"], ["S1", "A4"]),
    "M13": (["H2", "H5"], ["S2", "A4"]),
    "M14": (["H3", "H6", "H9"], ["S5", "A1"]),
    "M15": (["H4", "H8"], ["S7", "A5"]),
    "M16": (["H3", "H9"], ["A0"]),
    "M17": (["H2", "H5"], ["A3", "A7"]),
    "M18": (["H1", "H3", "H9"], ["A6", "A7"]),
}


def infer_grammar_families(card):
    """Classify commands from executable syntax, with no scan of art prose."""
    # Comparison cards have three accepted executable routes: the primary
    # recipe and the two named alternatives.  Coverage must inspect all of
    # them, otherwise a hidden alternative can smuggle in an unintroduced
    # grammar (notably characterwise Visual mode).
    keys = " ".join([card.get("expected", "")] + [
        method.get("keys", "") for method in card.get("method_alternatives", [])
    ])
    # Only strip a real command-line sentence.  A literal `:` may be the
    # landmark searched by f:/;/, in an otherwise normal-mode recipe.
    normal_keys = re.sub(r":[^<]*<CR>", "", keys)
    plain_normal = re.sub(r"<[^>]+>", "", normal_keys)
    families = []
    def add(name):
        if name not in families:
            families.append(name)
    substitute_commands = re.findall(r":([^<\r\n]*?)(?:s|substitute)(?=[/@])", keys)
    if substitute_commands:
        # A current-row :s and an addressed :range s are distinct teaching
        # families: seeing :1,3s does not teach the learner what an omitted
        # range means, and vice versa.
        if any(command.strip() for command in substitute_commands):
            add("ex-substitute-range")
        else:
            add("ex-substitute-line")
    if "\\=" in keys: add("expression-substitute")
    if re.search(r":[^<]*(?:t|co(?:py)?)(?:\$|\d)", keys): add("ex-copy")
    if re.search(r":[^<]*(?:m|move)(?:\$|\d)", keys): add("ex-move")
    if re.search(r":(?:%|\d+(?:,\d+)?)?g[/@]", keys): add("global-normal")
    if re.search(r"(?:\d+)?yy|yap", keys): add("linewise-yank-put")
    if "<C-v>" in keys or "V" in plain_normal: add("visual-scope")
    if "<C-v>" in keys and re.search(r"\$A", keys): add("block-append")
    if re.search(r"(?:^|[^A-Za-z])v(?:[^A-Za-z]|$)", plain_normal): add("visual-characterwise")
    if re.search(r"(?:\d+)?dd|D", plain_normal): add("linewise-delete")
    if re.search(r"(?:daw|ci\()", plain_normal): add("operator-motion-object")
    if re.search(r"r.", plain_normal): add("normal-replace")
    if re.search(r"(?:^|[0-9G])(?:o|O)", plain_normal): add("normal-open-line")
    if "qq" in plain_normal or re.search(r"@\w", plain_normal): add("macro")
    if re.search(r"(?:j|k|n|N|;|,)\.", plain_normal):
        add("repeat")
    if ";" in plain_normal or "," in plain_normal:
        add("char-find-repeat")
    if re.search(r'"[a-z0-9]', keys) or "<C-r>" in keys: add("register")
    if "u<C-r>" in keys: add("undo-redo")
    if "<C-k>" in keys: add("digraph")
    if "virtualedit" in keys or re.search(r"\d+\|", plain_normal): add("virtual-column")
    if re.search(r"[WBE]", plain_normal): add("word-boundary")
    if "R" in plain_normal: add("replace-mode")
    if "C" in plain_normal: add("change-to-end")
    if re.search(r"/[^<]+", plain_normal) or re.search(r"[ftFT].", plain_normal):
        add("search-landmark")
    if (re.search(r":[^<]+<CR>", keys) and "virtual-column" not in families
            and not any(name.startswith("ex-") for name in families)):
        add("ex-command")
    if "P" in plain_normal: add("put-before")
    if "}" in plain_normal: add("paragraph-next")
    if re.search(r"(?:gg|G|\d+[hjkl|]|[wWeEbB$^0{}])", plain_normal): add("normal-motion")
    if not families and keys: add("normal-motion")
    return families


def _family_breakdown(families):
    rows = []
    for name in families:
        if name not in FAMILY_DEFS:
            continue
        grammar = FAMILY_DEFS[name]["grammar"]
        rows.append(" + ".join(grammar) if isinstance(grammar, list) else grammar)
    return rows


def paired_question(module, card):
    """One card-owned non-template question grounded in this exact art edit."""
    families = card["grammar_families"]
    primary = families[0]
    family = FAMILY_DEFS[primary]
    required_terms = []
    for family_name in families:
        for group in FAMILY_DEFS.get(family_name, {}).get("terms", []):
            if group not in required_terms:
                required_terms.append(group)
    qid = card["id"] + ".P01"
    ordinal = card["ordinal"]
    common = {
        "id": qid, "card_id": card["id"], "module_id": card["module_id"],
        "grammar_family": primary, "grammar_breakdown_id": primary,
        "grammar_breakdown": _family_breakdown(families),
        "paired_invariant": module["principle"], "source_ref": module["source_ref"],
        "difficulty": 1 + int(ordinal >= 4),
    }
    is_bridge = not re.fullmatch(r"M\d+\.\d\d", card["id"]) and card["id"] not in {
        "M0.O", "M0.T",
    }
    if is_bridge:
        common.update({
            "form": "decode", "placement": "after",
            "placement_reason": (
                "This inserted bridge first shows and practises the new command, then asks "
                "the learner to name every command part and its animation scope."
            ),
            "prompt": (
                "ANIMATION\n%s\n\nNEOVIM\nYou just used `%s`. Decode it in plain language. "
                "Name every command part and the exact animation scope it owned."
            ) % (card["prompt"], card["expected"]),
            "answer_contract": {
                "form": "decode", "display": card["expected"],
                "required_term_groups": required_terms,
                "sample_answer": " ".join(group[0] for group in required_terms),
            },
        })
    elif ordinal == 6:
        common.update({
            "form": "typed_keys", "placement": "before",
            "placement_reason": (
                "The learner must work out a real edit on a scratch copy before the recipe "
                "or transfer attempt can become performance evidence."
            ),
            "prompt": (
                "ANIMATION\n%s\n\nNEOVIM\nOn the scratch copy, make START become TARGET. "
                "Type any safe key sequence with the same effect; spelling is not graded."
            ) % card["prompt"],
            "answer_contract": {
                "form": "typed_keys", "initial_lines": card["start"],
                "target_lines": card["target"], "initial_cursor": card.get("cursor", "^"),
                "forbidden_side_effects": ["write", "shell", "extra_window", "extra_tab"],
                "sample_answer": card["expected"], "effect_version": 1,
            },
        })
    elif ordinal == 1 or card["id"] == "M0.O":
        action = "; ".join(why for _keys, why in card.get("recipe", []))
        common.update({
            "form": "predict_art", "placement": "after",
            "placement_reason": (
                "The learner first sees and types the new command in the guided edit; this "
                "short choice then checks the resulting scope without demanding a second key sequence."
            ),
            "prompt": (
                "ANIMATION\n%s\n\nNEOVIM\nYou just completed the guided command. Which "
                "summary correctly describes what it did?"
            ) % card["prompt"],
            "choices": [
                "It made the stated bounded edit while preserving every registered cell outside that scope.",
                "It only moved the cursor; no requested art cell changed.",
                "It inserted extra cells and shifted the rest of the fixed-width row.",
                "It rewrote every similar glyph in the project, including unrelated frames.",
            ],
            "correct_choice": 0,
            "feedback": [
                "Correct: %s." % action,
                "The guided result required an art change, not navigation alone.",
                "Shifting the row would violate fixed-width registration.",
                "The command was bounded to the stated subject; project-wide scope was not requested.",
            ],
            "answer_contract": {"form": "predict_art", "answer_mode": "choice"},
        })
    elif ordinal == 2 or card["id"] == "M0.T":
        common.update({
            "form": "decode", "placement": "after",
            "placement_reason": (
                "The complete recipe is shown and practised first; the learner then decomposes "
                "the command without being asked to infer untaught keys."
            ),
            "prompt": (
                "ANIMATION\n%s\n\nNEOVIM\nYou just used `%s`. Decode it in plain language. Explain its scope "
                "and why that scope preserves the complete animation object."
            ) % (module["principle"], card["expected"]),
            "answer_contract": {
                "form": "decode", "display": card["expected"],
                "required_term_groups": required_terms,
                "sample_answer": " ".join(group[0] for group in required_terms),
            },
        })
    elif ordinal == 4:
        common.update({
            "form": "predict_art", "placement": "before",
            "placement_reason": (
                "Prediction makes the learner state the intended changed region before a "
                "key-hidden retrieval, without revealing its command path."
            ),
            "prompt": (
                "ANIMATION\n%s\n\nNEOVIM\nBefore editing, which result and scope are correct?"
            ) % card["prompt"],
            "choices": [
                "TARGET exactly; only the acting frame/region changes.",
                "START unchanged; navigation alone proves the skill.",
                "TARGET shifted one column; insertion is harmless in fixed-width art.",
                "Every similar glyph in the project changes, even outside the stated frame.",
            ],
            "correct_choice": 0,
            "feedback": [
                "Correct: the named acting region changes and registered cells remain fixed.",
                "Navigation without the requested art change does not satisfy the card.",
                "A one-column shift breaks frame registration.",
                "Project-wide scope exceeds the visible animation contract.",
            ],
            "answer_contract": {"form": "predict_art", "answer_mode": "choice"},
        })
    elif ordinal == 5:
        why_spec = WHY_SPECS[card["id"]]
        common.update({
            "form": "why", "placement": "after",
            "placement_reason": (
                "The exact result must exist before the learner compares cursor dependence, "
                "scope, and animation risk across the two valid methods."
            ),
            "prompt": (
                "ANIMATION\n%s\n\nNEOVIM\n%s"
            ) % (module["principle"], why_spec["question"]),
            "answer_contract": {
                "form": "why",
                "required_term_groups": why_spec["groups"],
                "sample_answer": why_spec["sample"],
            },
        })
    else:
        grammar = family["grammar"]
        ex = family["class"] == "ex"
        common.update({
            "form": "complete", "placement": "before",
            "placement_reason": (
                "The learner completes the reusable grammar before the checkpoint; the card's "
                "exact hidden recipe remains undisclosed."
            ),
            "prompt": (
                "ANIMATION\n%s\n\nNEOVIM\nComplete the reusable grammar: %s"
            ) % (module["principle"],
                 "an Ex statement runs only after ____" if ex else
                 "[count] operator [count] ____ names the operated scope"),
            "answer_contract": {
                "form": "complete",
                "accepted_answers": (["<CR>", "Enter", "the Enter key"] if ex else
                                     ["motion", "text object", "motion or text object"]),
                "sample_answer": "<CR>" if ex else "motion or text object",
            },
        })
    return common


def m0_extra_cards(module):
    """Migration-safe prerequisite inserts; existing M0 ids never move."""
    base = {
        "module_id": "M0", "skill": module["skill"], "source_ref": module["source_ref"],
        "medium": "monospace", "node_ids": [module["node"]],
        "master_habits": ["H1", "H3"], "master_stages": ["S0", "A0"],
    }
    primer = dict(base, **{
        "id": "M0.P0", "ordinal": 0, "kind": "concept",
        "title": "Spark loop · Vim grammar primer", "project_id": module["project"],
        "variant_group": "M0.grammar-primer", "lesson_benefit": (
            "distinguish operator sentences, standalone Normal commands, and Ex statements"
        ),
        "prompt": (
            "Use the movement grammar taught above to interpret one new command. "
            "Do not decode operators, text objects, or Ex commands yet."
        ),
        "teaching_lines": [
            "Vim's first small sentence is [count] + motion.",
            "j moves down one row; 4j moves down four. Neither changes art.",
            "Operators, text objects, replacement and : commands come later.",
        ],
        "grammar_families": ["normal-motion"],
        "grammar_stage": "explanation", "key_vocabulary": [
            "[count] + motion",
            "j = down one row; 4j = down four rows",
        ],
    })
    open_line = dict(base, **{
        "id": "M0.O", "ordinal": 2.5, "kind": "guided_edit",
        "title": "Spark loop · Open rows without indentation drift",
        "project_id": "m0-open-line-lab", "artifact": "transfer",
        "variant_group": "M0.open-line", "lesson_benefit": (
            "learn o/O and mode exit before a hidden card can require newly authored rows"
        ),
        "prompt": (
            "Create the second three-row spark below the first with open-line entry; keep every "
            "ray in its original column and return to Normal mode."
        ),
        "start": ["  \\|/", "-- o --", "  /|\\"],
        "target": ["  \\|/", "-- o --", "  /|\\", "  \\|/", "-- O --", "  /|\\"],
        "expected": "Go<C-u>  \\|/<Esc>o<C-u>-- O --<Esc>o  /|\\<Esc>",
        "recipe": [["G", "start from the last existing row"],
                   ["o<C-u>…<Esc>", "open below, clear inherited indent, type the registered row, and return to Normal"]],
        "cursor": "^", "show_target": True, "show_recipe": True,
        "hint": (
            "o opens below and enters Insert; O opens above. <C-u> clears inherited indent; "
            "the tutor also disables indentation only in the art buffer so columns survive."
        ),
        "frame_slices": [3, 3], "grammar_families": ["normal-open-line"],
        "grammar_stage": "guided",
    })
    ex_copy = dict(base, **{
        "id": "M0.T", "ordinal": 4.5, "kind": "guided_edit",
        "title": "Spark loop · Addressed whole-frame copy",
        "project_id": "m0-ex-copy-lab", "artifact": "transfer",
        "variant_group": "M0.ex-copy", "lesson_benefit": (
            "work out source range, copy command, destination, and Enter before M0.05 hides them"
        ),
        "prompt": (
            "Copy the complete three-row flare after the file with one addressed Ex statement."
        ),
        "start": ["  \\|/", "== O ==", "  /|\\"],
        "target": ["  \\|/", "== O ==", "  /|\\", "  \\|/", "== O ==", "  /|\\"],
        "expected": ":1,3t$<CR>",
        "recipe": [[":1,3", "source range: all three frame rows"],
                   ["t$", "copy that range after the last line"],
                   ["<CR>", "execute the complete Ex statement"]],
        "cursor": "^", "show_target": True, "show_recipe": True,
        "hint": (
            "Ex copy grammar is source range + t/copy + destination + Enter; `$` means the "
            "last line, independent of cursor position."
        ),
        "frame_slices": [3, 3], "grammar_families": ["ex-copy"],
        "grammar_stage": "guided",
        "duplicate_frames": [{
            "frames": [1, 2], "role": "scaffold",
            "reason": "a working whole-frame copy used to learn addressed Ex scope",
            "playback": False,
        }],
    })
    for card in (primer, open_line, ex_copy):
        card["roadmap_contract"] = card["prompt"]
        card.setdefault("key_vocabulary", _family_breakdown(card["grammar_families"]))
    return primer, open_line, ex_copy


def guided_bridge_cards(module):
    """Visible microcards inserted before a command family is required hidden."""
    habits, stages = MASTER_COVERAGE[module["id"]]

    def bridge(suffix, title, prompt, start, target, expected, recipe, family,
               ordinal, *, labels=False):
        card_id = "%s.%s" % (module["id"], suffix)
        card = {
            "id": card_id, "module_id": module["id"], "ordinal": ordinal,
            "kind": "guided_edit", "title": "%s · %s" % (module["title"], title),
            "project_id": "grammar-" + card_id.lower().replace(".", "-"),
            "artifact": "transfer", "variant_group": card_id + ".guided-bridge",
            "skill": module["skill"], "source_ref": module["source_ref"],
            "medium": "monospace", "node_ids": [module["node"]],
            "master_habits": habits, "master_stages": stages,
            "lesson_benefit": "perform %s visibly before a later key-hidden animation edit requires it" % family,
            "prompt": prompt, "roadmap_contract": prompt,
            "start": start, "target": target, "expected": expected,
            "recipe": recipe, "cursor": "^", "show_target": True,
            "show_recipe": True, "hint": "Work out the scope first; then follow the visible grammar once.",
            "grammar_families": [family], "grammar_stage": "guided",
            "key_vocabulary": _family_breakdown([family]),
            "frame_rows": len(start), "frame_slices": [len(target)],
        }
        if labels:
            card["labels"] = True
        def changed(rows, marker):
            # Perturb only the stable left registration rail.  Replacing the
            # first bar anywhere can accidentally replace the cell that the
            # lesson is meant to edit (for example M4.VB's top-centre x -> |).
            # Keeping width and every command-addressed column unchanged also
            # makes these genuine changed-art transfers rather than new paths.
            return [marker + row[1:] if row.startswith("|") else row for row in rows]
        card["review_variants"] = [{
            "start": changed(start, marker), "target": changed(target, marker),
            "expected": expected, "recipe": recipe,
        } for marker in ("!", "+")]
        card["review_source_card_id"] = card_id
        card["review_method_family"] = family
        return card

    mid = module["id"]
    rows = []
    if mid == "M0":
        rows.append(("M0.06", bridge(
            "SL", "Scope a substitute to the current line",
            "On one changed frame, replace every small core on the current line with one line-scoped substitute; leave the two contour rows alone.",
            ["| /---\\ |", "| o o   |", "| \\---/ |"],
            ["| /---\\ |", "| O O   |", "| \\---/ |"],
            "2G:s/o/O/g<CR>",
            [["2G", "land on the row whose repeated material changes"],
             [":s/o/O/g<CR>", "use the current row as the implicit address and replace every o there"]],
            "ex-substitute-line", 5.5)))
    elif mid == "M1":
        rows.append(("M1.04", bridge(
            "DD", "Delete one complete redundant frame",
            "Remove only the second three-row contour frame; keep the first frame registered.",
            [" /---\\ ", "|  o  |", " \\---/ ", " /---\\ ", "|  O  |", " \\---/ "],
            [" /---\\ ", "|  o  |", " \\---/ "], "4G3dd",
            [["4G", "land on the first row of the redundant frame"],
             ["3dd", "count three whole rows and delete them linewise"]],
            "linewise-delete", 3.5)))
    elif mid == "M3":
        register_bridge = bridge(
            "REG", "Copy a complete pose through a named register",
            "Store the complete three-row pose in register a, put it below, then change only the copied eye.",
            [" /---\\ ", "|  o  |", " \\---/ "],
            [" /---\\ ", "|  o  |", " \\---/ ", " /---\\ ", "|  O  |", " \\---/ "],
            "ggV2j\"ayG\"ap5G0forO",
            [["ggV2j", "select the complete pose linewise"],
             ["\"ay", "yank the selection into register a"],
             ["G\"ap", "put that register after the file"],
             ["5G0forO", "change only the copied eye"]],
            "register", 5.5)
        register_bridge["grammar_families"].append("visual-scope")
        register_bridge["key_vocabulary"] = _family_breakdown(register_bridge["grammar_families"])
        rows.extend([
            ("M3.04", bridge(
                "CI", "Change inside the eye object",
                "Change only the glyph inside the parenthesized eye; keep both delimiters and the silhouette.",
                [" /---\\ ", "| (.) |", " \\---/ "],
                [" /---\\ ", "| (O) |", " \\---/ "], "2G0f(ci(O<Esc>",
                [["2G0f(", "land on the eye delimiter"],
                 ["ci(", "change the text object inside parentheses"],
                 ["O<Esc>", "type the new pupil and return to Normal"]],
                "operator-motion-object", 3.25)),
            ("M3.06", register_bridge),
            ("M3.08", bridge(
                "DI", "Enter one Unicode accent by digraph",
                "Replace the pose core with a middle dot using the digraph entry, without shifting its row.",
                [" /---\\ ", "|  O  |", " \\---/ "],
                [" /---\\ ", "|  ·  |", " \\---/ "], "2G0fOr<C-k>.M",
                [["2G0fO", "land on the one-cell core"],
                 ["r<C-k>.M", "replace it with the .M middle-dot digraph"]],
                "digraph", 7.5)),
        ])
    elif mid == "M4":
        rows.append(("M4.04", bridge(
            "VB", "Replace one registered column as a block",
            "Select the aligned centre column across all three tween rows and replace it without shifting neighbours.",
            [" /x\\ ", "| x |", " \\x/ "], [" /|\\ ", "| | |", " \\|/ "],
            "gg02l<C-v>2jr|",
            [["gg02l", "land on the top centre cell"],
             ["<C-v>2j", "select that exact column through three rows"],
             ["r|", "replace every selected cell in place"]],
            "visual-scope", 3.5)))
    elif mid == "M6":
        rows.extend([
            ("M6.04", bridge(
                "D", "Erase a layer tail without deleting its row",
                "Remove the temporary layer tail after the left anchor; keep the three-row build and its anchor.",
                [" /---\\ ", "|====| tail", " \\---/ "],
                [" /---\\ ", "|", " \\---/ "], "2G0lD",
                [["2G0l", "land just after the preserved anchor"],
                 ["D", "delete from the cursor through the end of this row"]],
                "linewise-delete", 3.5, labels=True)),
            ("M6.06", bridge(
                "MOVE", "Move a complete build range",
                "Move the first complete three-row build after the second; do not copy or split either build.",
                [" /---\\ ", "|  o  |", " \\---/ ", " /===\\ ", "|  O  |", " \\===/ "],
                [" /===\\ ", "|  O  |", " \\===/ ", " /---\\ ", "|  o  |", " \\---/ "],
                ":1,3m$<CR>",
                [[":1,3", "source range: the first complete build"],
                 ["m$", "move it after the final row"], ["<CR>", "execute the Ex sentence"]],
                "ex-move", 5.5)),
        ])
    elif mid == "M7":
        rows.extend([
            ("M7.04", bridge(
                "DOT", "Repeat one tween-cell change",
                "Change the same registered dash to equals on three homologous rows by making one change and repeating it.",
                ["| - |", "| - |", "| - |"], ["| = |", "| = |", "| = |"],
                "gg0f-r=j.j.",
                [["gg0f-r=", "make the first one-cell change"],
                 ["j.", "move to the homologous row and repeat that change twice"]],
                "repeat", 3.5)),
            ("M7.04", bridge(
                "MAC", "Record a bounded landmark macro",
                "Record one colon-to-dot texture change plus the move to the next row, then replay it across four rows.",
                ["| : |", "| : |", "| : |", "| : |"],
                ["| . |", "| . |", "| . |", "| . |"], "ggqaf:r.qj0@aj0@aj0@a",
                [["qa", "start recording into register a"],
                 ["f:r.", "change one landmark while recording"],
                 ["qj0@aj0@aj0@a", "stop, reset each row anchor, and replay on three more rows"]],
                "macro", 4.5)),
            ("M7.05", bridge(
                "GLOBAL", "Apply one bounded Normal payload to matching rows",
                "On every row containing a lowercase core, replace that core with a star; leave the uppercase hold unchanged.",
                ["| o |", "| O |", "| o |"], ["| * |", "| O |", "| * |"],
                ":g/o/normal! for*<CR>",
                [[":g/o/", "select only rows whose pattern contains lowercase o"],
                 ["normal! for*", "run the bounded find-and-replace payload on each match"],
                 ["<CR>", "execute the global command"]],
                "global-normal", 4.75)),
            ("M7.04", bridge(
                "VIS", "Select a character band in Visual mode",
                "Select the three-cell material band characterwise, then replace the selection in place so the row width and rails stay registered.",
                ["| --- |", "| --- |", "| --- |"],
                ["| --- |", "| === |", "| --- |"],
                "2G0f-v2lr=",
                [["2G0f-", "land on the first dash of the acting band"],
                 ["v2l", "select exactly the three character cells"],
                 ["r=", "replace the selected cells without shifting the row"]],
                "visual-characterwise", 4.75)),
        ])
    elif mid == "M12":
        rows.append(("M12.04", bridge(
            "FIND", "Repeat a character find in both directions",
            "Use one forward character find, repeat it forward once, then reverse the find and brighten the two selected landmarks.",
            ["| /---\\ |", "| : : : |", "| \\---/ |"],
            ["| /---\\ |", "| ! ! : |", "| \\---/ |"],
            "2G0f:;r!,r!",
            [["2G0f:", "find the first colon landmark"],
             [";", "repeat the character find forward"],
             ["r!", "replace that second landmark in place"],
             [",", "repeat the find in the reverse direction"],
             ["r!", "replace the earlier landmark in place"]],
            "char-find-repeat", 3.5)))
    elif mid == "M14":
        para = bridge(
            "PARA", "Cross a frame boundary and put above it",
            "Yank the first blank-line-separated frame, cross the boundary with }, and put the stored frame above the next frame.",
            ["| /^\\  |", "| |o|   |", "| \\_/   |", "",
             "| /^\\  |", "| |+|   |", "| \\_/   |", ""],
            ["| /^\\  |", "| |o|   |", "| \\_/   |", "",
             "| /^\\  |", "| |o|   |", "| \\_/   |", "",
             "| /^\\  |", "| |+|   |", "| \\_/   |", ""],
            "ggyapgg}jP",
            [["ggyap", "yank one complete blank-line-separated frame object"],
             ["gg}", "jump from the first frame to the next paragraph boundary"],
             ["jP", "place the stored frame above the next frame"]],
            "paragraph-next", 4.5)
        para["grammar_families"].append("put-before")
        para["key_vocabulary"] = _family_breakdown(para["grammar_families"])
        para["frame_rows"] = module.get("frame_rows")
        rows.append(("M14.05", para))
    elif mid == "M15":
        rows.append(("M15.05", bridge(
            "BA", "Append one glyph to a selected column block",
            "Select the final three-row block and append one occluding edge at the true end of each row without redrawing the rows.",
            ["|..::..::..|", "| []__[]__[]|", "|\\________/|",
             "|..........|", "|  []__[]__[]|", "|\\________/|"],
            ["|..::..::..|", "| []__[]__[]|", "|\\________/|",
             "|..........||", "|  []__[]__[]||", "|\\________/||"],
            "4G0<C-v>2j$A|<Esc>",
            [["4G0", "land on the first row of the selected final frame"],
             ["<C-v>2j", "select one rectangular block through the three rows"],
             ["$A|<Esc>", "append the edge at every selected row end and return to Normal"]],
            "block-append", 4.5)))
    elif mid == "M11":
        rows.extend([
            ("M11.04", bridge(
                "UR", "Inspect undo and redo on one fixed cell",
                "Replace the middle glyph, undo once, then redo once so the final registered cell is the replacement.",
                [" /---\\ ", "|  .  |", " \\---/ "],
                [" /---\\ ", "|  !  |", " \\---/ "], "2G0f.r!u<C-r>",
                [["2G0f.r!", "replace the one-cell core"], ["u", "undo that change"],
                 ["<C-r>", "redo it without retyping"]],
                "undo-redo", 3.5)),
            ("M11.08", bridge(
                "VE", "Address an empty registered column",
                "Place one right edge at exact column 9 on each short row, padding empty cells without drifting the cores.",
                ["| o |", "| o |", "| o |"], ["| o |   |", "| o |   |", "| o |   |"],
                ":set virtualedit=all<CR>gg9|i|<Esc>2G9|i|<Esc>3G9|i|<Esc>",
                [[":set virtualedit=all<CR>", "allow cursor addresses past physical row ends"],
                 ["N|", "land on an exact one-based column"],
                 ["i|<Esc>", "insert the registered edge and return to Normal"]],
                "virtual-column", 7.5)),
        ])
    elif mid == "M13":
        rows.append(("M13.04", bridge(
            "BE", "Traverse texture by WORD boundaries",
            "Use WORD starts and ends to retouch three bounded texture clusters on the middle row.",
            ["| aa bb cc |", "| aa bb cc |", "| aa bb cc |"],
            ["| a! +b ?c |", "| aa bb cc |", "| aa bb cc |"],
            "gg0WEr!2Wr?Br+",
            [["W/E", "move to a WORD start, then its end"],
             ["2W", "count two WORD starts forward"],
             ["B", "move back one WORD start before the final replacement"]],
            "word-boundary", 3.5, labels=True)))
    elif mid == "M18":
        rows.append(("M18.05", bridge(
            "EXPR", "Use an expression only for validation metadata",
            "Update the CHECK digit from frame metadata while leaving the animation row untouched.",
            ["CHECK 1", "|  o  |", "CHECK 0"],
            ["CHECK 1", "|  o  |", "CHECK 1"],
            ":3s/0/\\=getline(1)[-1:]/<CR>",
            [[":3s/0/", "on CHECK row 3, replace the zero"],
             ["\\=getline(1)[-1:]", "evaluate a validation-only replacement from row 1"],
             ["<CR>", "execute without generating any art row"]],
            "expression-substitute", 4.5, labels=True)))
    return rows


def command_review_contract(cards):
    """Prove every visibly taught command family returns as hidden changed art."""
    first_guided = {}
    for index, card in enumerate(cards):
        if card.get("grammar_stage") != "guided" or not card.get("expected"):
            continue
        for family in card.get("grammar_families", []):
            first_guided.setdefault(family, (index, card["id"]))
    rows = []
    for family, (guided_index, guided_card_id) in first_guided.items():
        review = next((card for card in cards[guided_index + 1:]
                       if card.get("grammar_stage") == "hidden"
                       and family in card.get("grammar_families", [])
                       and (card.get("review_variants") or card.get("kind") == "transfer")
                       and card.get("show_recipe") is False), None)
        if review is None:
            raise ValueError(
                "%s: taught family %s never returns as hidden changed art" %
                (guided_card_id, family))
        variants = review.get("review_variants") or review.get("variants") or []
        rows.append({
            "grammar_family": family,
            "guided_card_id": guided_card_id,
            "review_card_id": review["id"],
            "changed_art_variants": len(variants),
            "keys_hidden": True,
            "evidence": "runtime-validated source-linked changed-art retrieval",
        })
    return rows


def primer_question(module):
    return {
        "id": "M0.P0.P01", "card_id": "M0.P0", "module_id": "M0",
        "form": "multiple_choice", "grammar_family": "vim-language-primer",
        "grammar_breakdown_id": "vim-language-primer",
        "grammar_breakdown": [
            "count: how many times the following motion runs",
            "motion: where the cursor moves without changing art",
            "5j: repeat the down-one-row j motion five times",
        ],
        "paired_invariant": "fixed-width animation edits need an explicit scope before keys are chosen",
        "placement": "before",
        "placement_reason": (
            "The card first teaches count + motion with 4j, then asks the learner to transfer only that taught grammar to 5j."
        ),
        "prompt": (
            "ANIMATION\nYou want to inspect the fifth row below the cursor without changing any art.\n\n"
            "NEOVIM\nThe lesson just taught `4j`. What does the unfamiliar command `5j` mean?"
        ),
        "animation_prompt": "Inspect a lower animation row while leaving every glyph registered.",
        "animation_answer": "cursor inspection leaves every art cell unchanged",
        "neovim_prompt": "Transfer the taught 4j pattern to 5j.",
        "neovim_answer": "5 is the count and j is the down-one-row motion, so the cursor moves down five rows",
        "compact_prompt": (
            "ANIMATION: inspect a lower row without changing art.\n"
            "NEOVIM: transfer the taught `4j` pattern to `5j`."
        ),
        "choices": [
            "ANIMATION: cursor inspection leaves every art cell unchanged | NEOVIM: 5 is the count and j is the down-one-row motion, so the cursor moves down five rows",
            "ANIMATION: cursor inspection leaves every art cell unchanged | NEOVIM: 5 addresses line five and j deletes that line",
            "ANIMATION: moving the cursor rewrites the five crossed art cells | NEOVIM: 5 is the count and j is the down-one-row motion, so the cursor moves down five rows",
            "ANIMATION: moving the cursor rewrites the five crossed art cells | NEOVIM: 5 addresses line five and j deletes that line",
        ],
        "compact_choices": [
            "A: art unchanged · V: 5=count, j=down",
            "A: art unchanged · V: line 5 is deleted",
            "A: five cells change · V: 5=count, j=down",
            "A: five cells change · V: line 5 is deleted",
        ],
        "correct_choice": 0,
        "feedback": [
            "Correct: count 5 repeats the j down motion five times and does not edit the buffer.",
            "No: 5j is Normal-mode count plus motion; it neither addresses nor deletes line five.",
            "No: neither character enters Insert mode; 5j only moves the cursor.",
            "No: the digits form the count and j is the motion; movement leaves the art unchanged.",
        ],
        "source_ref": module["source_ref"], "difficulty": 1,
        "answer_contract": {"form": "multiple_choice"},
    }


def lesson_benefit(module, ordinal):
    return {
        1: f"establish the next verified {module['project']} state while practising the smallest clear edit",
        2: f"extend the same saved {module['project']} strip instead of solving a disposable drill",
        3: f"explain the motion intent and authoring principle for {module['title']} from a changed visual prompt",
        4: "retrieve an edit from a visible outcome and action hint without a revealed command recipe",
        5: "produce one exact outcome, then compare two executable methods that reach that same buffer",
        6: "apply the module intention to unfamiliar ASCII art instead of memorised coordinates",
        7: f"diagnose the observable {module['title']} defect and select a bounded repair",
        8: "combine five conceptual decisions with one key-hidden artifact before mastery is awarded",
    }[ordinal]


def action_hint(module, card):
    """Teach scope and command families without disclosing the answer path."""
    keys = card.get("expected", "")
    normal_keys = re.sub(r":[^<]*<CR>", "", keys)
    normal_keys = re.sub(r"<[^>]+>", "", normal_keys)
    descriptions = " ".join(why.lower() for _key, why in card.get("recipe", []))
    tools = []

    def add(label):
        if label not in tools:
            tools.append(label)

    if "yap" in keys or "ip" in keys or "ap" in keys:
        add("a paragraph text object can own one blank-line-separated frame")
    if "<C-v>" in keys:
        add("blockwise Visual mode can constrain one rectangular cell column")
    if "yy" in keys or re.search(r"\d+y", keys):
        add("a counted linewise yank and put can copy a complete multi-row frame")
    if re.search(r":[^<]*(?:t|copy)(?:\$|\d)", keys):
        add("an addressed Ex copy can duplicate a complete row range without moving the cursor through it")
    if re.search(r":[^<]*(?:m|move)(?:\$|\d)", keys):
        add("an addressed Ex move can reorder a complete frame range as one unit")
    if re.search(r":[^<]*s[/@]", keys):
        add("a line- or range-scoped substitution can change repeated material without redrawing the row")
    if ":global" in keys or re.search(r":g[/@]", keys):
        add("a global selection can apply one normal-mode edit only to matching rows")
    if "qq" in keys or "@q" in keys:
        add("record one bounded edit plus its travel, then replay that macro only at homologous anchors")
    if "<C-r>" in keys or re.search(r'"[a-z0-9]', keys):
        add("a named register can preserve a glyph or frame while another edit changes the buffer")
    if "<C-a>" in keys:
        add("counted number incrementing can update a frame label without retyping it")
    if "<C-k>" in keys or "<C-v>u" in keys:
        add("use Neovim's Unicode/digraph input so the intended glyph remains one cell")
    if "virtualedit" in keys or re.search(r"\d+\|", keys):
        add("virtual editing plus exact-column motion can reach aligned empty cells")
    if "daw" in keys or "ci(" in keys:
        add("a text object can change the semantic unit without counting its characters")
    if re.search(r"(?:^|[0-9Ghjklwbe/$;,.])R", normal_keys):
        add("Replace mode can redraw cells in place without shifting the rest of the row")
    elif re.search(r"(?:^|[0-9Ghjklwbeft;/])r", normal_keys):
        add("single-cell replace preserves the row width and surrounding registration")
    if "find" in descriptions or "landmark" in descriptions:
        add("a visible character landmark is safer than repeated unit motions")
    if "/" in keys and not re.search(r":[^<]*s[/@]", keys):
        add("search can jump between homologous animation anchors")
    if "repeat" in descriptions or re.search(r"(?:^|[0-9Ghjklwbe;/]),?\.", normal_keys):
        add("dot repeat can replay the last bounded edit after moving to the matching anchor")
    if re.search(r"(?:^|[0-9Ghjkl])(?:o|O)", normal_keys):
        add("open-line mode creates a new row without manually inserting a newline")
    if not tools:
        add("choose the smallest normal-mode operation whose scope matches the visible change")

    start = card.get("start", [])
    rows = module.get("frame_rows")
    if rows:
        scope = "Treat each %d-row block as one frame; do not count only the nonblank glyph rows." % rows
    elif "" in start:
        scope = "Blank separators are frame boundaries; keep the earlier frame byte-for-byte unchanged."
    elif len(start) > 1:
        scope = "Compare corresponding rows first, then edit only the row or column that changes."
    else:
        scope = "Keep the edit on the acting row and preserve its fixed width."
    defect = module["defect"].rstrip(".")
    return "Vim toolbox: %s. Scope: %s Check against this failure: %s." % (
        "; ".join(tools[:3]), scope, defect)


# Machine-readable animation decisions.  These are evidence for preview and
# manifests, not decorative prose: the role/timing/pivot survive generation.
ANIMATION_META = {
    "M4.01": {"role": "extremes", "timing": "start/end", "pivot": "column 4"},
    "M4.02": {"role": "extreme-copy", "timing": "working frame", "pivot": "column 4"},
    "M4.04": {"role": "midpoint-tween", "timing": "between extremes", "pivot": "column 4"},
    "M4.06": {"role": "unseen-midpoint-transfer", "timing": "between extremes", "pivot": "column 4"},
    "M4.08": {"role": "verified-tween-strip", "timing": "ordered playback", "pivot": "column 4"},
    "M6.01": {"role": "finished-keyframe", "timing": "authoring start / playback end"},
    "M6.04": {"role": "subtractive-inbetween", "timing": "reverse authoring order"},
    "M6.08": {"role": "ordered-build-checkpoint", "timing": "equal-height reverse-to-forward playback"},
    "M7.01": {"role": "hold", "timing": "two frames",
               "hold_reason": "anticipation before the completed build"},
    "M7.02": {"role": "reviewable-duplicate", "timing": "candidate settle later removed during diagnosis"},
    "M7.04": {"role": "hold-timing-edit", "timing": "two repeated frames",
               "hold_reason": "anticipation before the completed build"},
    "M7.05": {"role": "material-polish", "timing": "same band across every frame"},
    "M7.08": {"role": "verified-timed-strip", "timing": "playback with hold",
               "hold_reason": "anticipation before the completed build"},
    "M8.01": {"role": "contact-keyframe", "timing": "planted foot"},
    "M8.04": {"role": "secondary-motion-pose", "timing": "prop lags body"},
    "M8.08": {"role": "verified-contact-strip", "timing": "contact / passing / opposite contact / return passing"},
    "M9.01": {"role": "planned-high-keyframe", "timing": "first extreme"},
    "M9.02": {"role": "squash-scaffold", "timing": "impact extreme scaffold"},
    "M9.04": {"role": "squash-extreme", "timing": "impact key pose"},
    "M9.05": {"role": "falling-inbetween", "timing": "between high and squash extremes"},
    "M9.08": {"role": "rebound-overshoot", "timing": "after squash / before loop settle"},
    "M12.01": {"role": "left-accent-extreme", "timing": "first staggered key pose", "pivot": "centre axis"},
    "M12.04": {"role": "drag-inbetween", "timing": "lower joints one frame after upper joints", "pivot": "centre axis"},
    "M12.08": {"role": "mirrored-return", "timing": "opposite-side loop exit", "pivot": "centre axis"},
    "M13.01": {"role": "centre-pulse-keyframe", "timing": "material accent enters at centre"},
    "M13.04": {"role": "expanded-pulse", "timing": "three-edge anticipation before flash"},
    "M13.08": {"role": "left-exit", "timing": "opposite-side loop exit"},
    "M14.01": {"role": "palette-variant", "timing": "first saved material choice", "pivot": "eye cell"},
    "M14.04": {"role": "second-palette-variant", "timing": "contrasting saved material choice", "pivot": "eye cell"},
    "M14.08": {"role": "palette-return", "timing": "third variant returns to first material", "pivot": "eye cell"},
    "M15.01": {"role": "brick-offset", "timing": "one-cell material pan", "pivot": "angled ground shadow"},
    "M15.04": {"role": "lightened-offset", "timing": "second material pan with reduced dither density", "pivot": "angled ground shadow"},
    "M15.08": {"role": "macro-settle", "timing": "registered return with lighter dither", "pivot": "angled ground shadow"},
    "M16.01": {"role": "written-size-test", "timing": "frame identity and 8 FPS declared before expansion", "pivot": "approved small key pose"},
    "M16.04": {"role": "planned-key-pose-copy", "timing": "third numbered planning block", "pivot": "approved small key pose"},
    "M16.08": {"role": "planned-fourth-pose", "timing": "fourth numbered planning block before in-betweening", "pivot": "approved small key pose"},
    "M17.01": {"role": "coherence-repair", "timing": "one stable eye across three shell poses", "pivot": "eye cell"},
    "M17.04": {"role": "new-shell-extreme", "timing": "fourth distinct contour around the stable eye", "pivot": "eye cell"},
    "M17.08": {"role": "macro-coherence-pass", "timing": "one palette change across four frame anchors", "pivot": "eye cell"},
    "M18.01": {"role": "hand-mirrored-extreme", "timing": "authored return extreme", "pivot": "fixed side rails"},
    "M18.04": {"role": "return-overshoot", "timing": "one cell past the mirrored return extreme", "pivot": "fixed side rails"},
    "M18.08": {"role": "reverse-reuse-turnaround", "timing": "return / overshoot / hold / reverse", "pivot": "fixed side rails", "hold_reason": "turnaround at the overshoot before reverse reuse"},
}


def duplicate(pair, role, reason, playback, duration_frames=None):
    row = {"frames": list(pair), "role": role, "reason": reason,
           "playback": playback}
    if duration_frames is not None:
        row["duration_frames"] = duration_frames
    return row


# A command family is not spaced practice merely because its token appears in
# an answer key.  These four late hidden cards are deliberately assigned a
# second changed-art bank so the newly visible prerequisite (digraph, text
# object, characterwise Visual, and open-line authoring) returns as retrieval
# rather than as a one-time worked example.  The perturbation is on a stable
# non-acting cell in the first frame; the same cell is changed in start and
# target, so the authored key path still has to produce the animation edit.
REVIEW_PERTURB_ROWS = {
    "M3.04": 0,   # head rail; ci( acts on line 8
    "M3.08": 0,   # first pose rail; digraph acts on line 14
    "M7.04": 2,   # left contour of the first held frame; v acts on its dashes
    "M8.04": 0,   # first pose; o appends rows after the existing strip
}


def attach_command_review_variants(card):
    """Attach two changed-art, key-hidden reviews for a late first-use card."""
    row_index = REVIEW_PERTURB_ROWS.get(card["id"])
    if row_index is None or card.get("review_variants") or card.get("kind") == "transfer":
        return
    start = list(card.get("start", []))
    target = list(card.get("target", []))
    if row_index >= len(start) or row_index >= len(target):
        raise ValueError("review perturbation row outside %s" % card["id"])
    row = start[row_index]
    positions = [index for index, char in enumerate(row) if not char.isspace()]
    if not positions:
        raise ValueError("review perturbation row has no stable art in %s" % card["id"])
    position = positions[0]
    if start[row_index][position] != target[row_index][position]:
        raise ValueError("review perturbation would alter acting cell in %s" % card["id"])
    variants = []
    for marker in ("!", "+"):
        changed_start, changed_target = list(start), list(target)
        changed_start[row_index] = changed_start[row_index][:position] + marker + changed_start[row_index][position + 1:]
        changed_target[row_index] = changed_target[row_index][:position] + marker + changed_target[row_index][position + 1:]
        variants.append({
            "start": changed_start, "target": changed_target,
            "expected": card["expected"], "recipe": card.get("recipe", []),
            "cursor": card.get("cursor", "^"),
        })
    card["review_variants"] = variants


# Adjacent identical frames must be intentional and machine-readable. A
# scaffold is an authoring state that later cards must change; it is not a hold.
DUPLICATE_META = {
    "M0.05": [duplicate((3, 4), "hold", "sustain the flare impact before release", True, 2)],
    "M0.08": [duplicate((3, 4), "hold", "retain the verified flare impact hold", True, 2)],
    "M1.02": [duplicate((1, 2), "scaffold", "working copy for the descending contour", False)],
    "M2.02": [duplicate((1, 2), "scaffold", "working copy for the changed focus", False)],
    "M2.05": [duplicate((1, 2), "material-normalization", "method comparison normalizes two eye spellings; not accepted as a timing hold", False)],
    "M2.08": [duplicate((1, 2), "material-normalization", "the normalized open-focus pair remains visible before the blink", False)],
    "M3.02": [duplicate((1, 2), "scaffold", "working whole-pose copy for the acting eye", False)],
    "M4.02": [duplicate((2, 3), "scaffold", "working forward extreme for midpoint construction", False)],
    "M4.04": [duplicate((3, 4), "scaffold", "working forward extreme reserved for the return midpoint", False)],
    "M5.02": [duplicate((1, 2), "scaffold", "working composite for the moving foreground", False)],
    "M6.02": [duplicate((1, 2), "scaffold", "working finished frame for subtractive authoring", False)],
    "M7.01": [duplicate((1, 2), "hold", "anticipation before the completed build", True, 2)],
    "M7.02": [duplicate((1, 2), "hold", "retain the anticipation hold", True, 2),
                duplicate((4, 5), "reviewable-duplicate", "candidate settle must later be justified or removed", False)],
    "M7.04": [duplicate((1, 2), "hold", "retain the edited anticipation hold", True, 2),
                duplicate((4, 5), "reviewable-duplicate", "candidate settle remains pending diagnosis", False)],
    "M7.05": [duplicate((1, 2), "hold", "retain the polished anticipation hold", True, 2),
                duplicate((4, 5), "reviewable-duplicate", "candidate settle remains pending diagnosis", False)],
    "M7.06": [duplicate((1, 2), "hold", "changed-art retrieval explicitly constructs a two-frame hold", True, 2)],
    "M7.08": [duplicate((1, 2), "hold", "verified anticipation hold after removing the stale settle", True, 2)],
    "M10.05": [duplicate((3, 4), "hold", "sustain the hatched impact before settle", True, 2)],
    "M10.08": [duplicate((3, 4), "hold", "retain the verified proportional impact hold", True, 2)],
    "M11.02": [duplicate((1, 2), "scaffold", "working copy for the slack-tension redraw", False)],
    "M14.02": [duplicate((1, 2), "scaffold", "working paragraph-frame copy for the second palette variant", False)],
    "M14.PARA": [duplicate((1, 2), "scaffold", "working paragraph-frame copy used to make } and P visible", False)],
    "M14.05": [duplicate((2, 3), "scaffold", "working paragraph-frame copy reserved for the return variant", False)],
    "M15.02": [duplicate((1, 2), "scaffold", "working material-frame copy for offset and lightening", False)],
    "M17.02": [duplicate((3, 4), "scaffold", "working copy of the third shell for a fourth distinct pose", False)],
    "M18.02": [duplicate((1, 2), "scaffold", "working copy of the mirrored return for overshoot development", False)],
    "M18.08": [duplicate((2, 3), "hold", "turnaround hold at the overshoot before approved frames play in reverse", True, 2)],
}


def make_cards(module, catalog_prompts):
    mid = module["id"]
    cards = []
    edit_by_ordinal = {1: module["steps"][0], 2: module["steps"][1],
                       4: module["steps"][2], 5: module["steps"][3],
                       6: module["transfer"], 8: module["steps"][4]}
    for ordinal in range(1, 9):
        card_id = f"{mid}.{ordinal:02d}"
        card = {
            "id": card_id, "module_id": mid, "ordinal": ordinal,
            "kind": KINDS[ordinal],
            "title": f"{module['title']} · {module.get('phase_titles', {}).get(ordinal, PHASE_TITLES[ordinal])}",
            "roadmap_contract": catalog_prompts[card_id],
            "lesson_benefit": lesson_benefit(module, ordinal),
            "skill": module["skill"], "source_ref": module["source_ref"],
            "medium": module.get("medium", "monospace"),
            "node_ids": [module["node"]], "project_id": module["project"],
            "variant_group": f"{mid}.card-{ordinal}",
        }
        if ordinal in edit_by_ordinal:
            card.update(edit_by_ordinal[ordinal])
            card["prompt"] = catalog_prompts[card_id]
            if ordinal in module.get("labels_steps", []):
                card["labels"] = True
            card["artifact"] = "transfer" if ordinal == 6 else "project"
            if ordinal == 6:
                card["variants"] = [module["transfer"], module["transfer_alt"]]
            # Every edit needs a visible result to aim at. Retrieval cards hide
            # the exact keystrokes, not the target or the action-level hint.
            card["show_target"] = True
            card["show_recipe"] = ordinal in (1, 2)
            card["hint"] = action_hint(module, card)
            if ordinal == 5:
                card["method_alternatives"] = card.pop("alternatives")
                labels = [method["label"] for method in card["method_alternatives"]]
                card["prompt"] = (
                    "%s · USE ONE METHOD — choose one accepted path: %s. Do not perform both. "
                    "Complete the target with the one method you selected; the tutor compares "
                    "the method evidence only after that single path passes."
                    % (card_id, " or ".join(labels))
                )
            if card["artifact"] == "project":
                migration_starts = module.get("migration_starts", {}).get(ordinal, [])
                if migration_starts:
                    card["accepted_legacy_starts"] = migration_starts
                if module.get("frame_rows"):
                    rows = module["frame_rows"]
                    card["frame_slices"] = [rows] * (len(card["target"]) // rows)
                elif module.get("frame_slices", {}).get(ordinal):
                    card["frame_slices"] = module["frame_slices"][ordinal]
                elif module.get("preview_mode") == "layers":
                    card["preview_mode"] = "layers"
        if ordinal == 3:
            card["prompt"] = (
                f"Inspect the complete {module['title']} art or scenario below, then choose "
                "the interpretation supported by the visible evidence and authoring principle.")
            # At .03 only the two preceding guided edits are prerequisites.
            # Later command/timing questions remain in .07 and the module
            # check, after their guided bridges. This is deliberately small:
            # more variants do not justify testing material before teaching it.
            concept_ids = (1, 2)
            card["question_ids"] = [f"{mid}.Q{number:02d}" for number in concept_ids]
        elif ordinal == 7:
            card["prompt"] = (
                f"Diagnose the displayed {module['title']} strip or workflow, then choose "
                "the bounded repair or explanation that preserves the intended animation.")
            card["question_ids"] = [f"{mid}.Q{number:02d}"
                                    for number in (3, 7, 10, 8, 9)]
        elif ordinal == 8:
            card["prompt"] = (
                "Answer five checks, then perform this key-hidden artifact task: "
                f"{catalog_prompts[card_id]} The target remains visible; the exact command path stays hidden until evaluation.")
            if card_id == "M6.08":
                card["lesson_benefit"] = (
                    "prove that subtractive authoring preserved five-row bounds and that playback order visibly builds")
            card["question_ids"] = [f"{mid}.Q{number:02d}" for number in range(1, 11)]
            card["pass_questions"] = 4
        animation = ANIMATION_META.get(card_id)
        if animation:
            card["animation"] = animation
        if card_id in DUPLICATE_META:
            card["duplicate_frames"] = DUPLICATE_META[card_id]
        attach_command_review_variants(card)
        if card.get("review_variants") or card.get("kind") == "transfer":
            card["review_source_card_id"] = card_id
            if card.get("method_requirement"):
                family = "required:%s" % card["method_requirement"]["label"]
            elif card.get("method_alternatives"):
                family = "comparison:%s" % card_id
            else:
                family = "technique:%s" % card_id
            card["review_method_family"] = family
        habits, stages = MASTER_COVERAGE[mid]
        card["master_habits"] = habits
        card["master_stages"] = stages
        if card.get("expected"):
            card["grammar_families"] = infer_grammar_families(card)
            # Inserted bridge cards declare their own guided stage even when
            # their fractional ordinal sits beside a hidden card.  Do not
            # recategorise those visible prerequisite performances by the
            # eight-card phase table.
            if not card.get("grammar_stage"):
                card["grammar_stage"] = (
                    "guided" if ordinal in (1, 2) else
                    "hidden" if ordinal in (4, 5, 6, 8) else "interpretation"
                )
            card.setdefault("key_vocabulary", _family_breakdown(card["grammar_families"]))
        else:
            card["grammar_families"] = ["paired-animation-neovim-diagnosis"]
            card["grammar_stage"] = "interpretation"
        cards.append(card)
    return cards


def build():
    modules, cards, questions = [], [], []
    catalog_prompts = load_catalog_prompts()
    for module in MODULES:
        module_cards = make_cards(module, catalog_prompts)
        if module["id"] == "M0":
            primer, open_line, ex_copy = m0_extra_cards(module)
            module_cards = [primer, module_cards[0], module_cards[1], open_line,
                            module_cards[2], module_cards[3], ex_copy] + module_cards[4:]
        bridge_rows = guided_bridge_cards(module)
        if bridge_rows:
            by_before = {}
            for before, bridge_card in bridge_rows:
                if bridge_card["id"] in DUPLICATE_META:
                    bridge_card["duplicate_frames"] = DUPLICATE_META[bridge_card["id"]]
                by_before.setdefault(before, []).append(bridge_card)
            expanded = []
            for existing in module_cards:
                expanded.extend(by_before.get(existing["id"], []))
                expanded.append(existing)
            module_cards = expanded
        modules.append({
            "id": module["id"], "title": module["title"], "node": module["node"],
            "project_id": module["project"], "skill": module["skill"],
            "preview_mode": module.get("preview_mode", "frames"),
            "frame_rows": module.get("frame_rows"),
            "meaning": module["meaning"], "first_reading": module["first_reading"],
            "principle": module["principle"],
            "defect": module["defect"], "basic": module["basic"],
            "scaled": module["scaled"], "source_ref": module["source_ref"],
            "medium": module.get("medium", "monospace"),
            "prerequisites": PREREQUISITES[module["id"]],
            "card_ids": [card["id"] for card in module_cards],
        })
        cards.extend(module_cards)
        questions.extend(question(module, n) for n in range(1, 11))
        if module["id"] == "M0":
            questions.append(primer_question(module))
    module_map = {module["id"]: module for module in MODULES}
    qmap = {q["id"]: q for q in questions}
    for card in cards:
        if card["id"] == "M0.P0":
            pair_ids = ["M0.P0.P01"]
            card["question_ids"] = list(pair_ids)
        elif card.get("expected"):
            pair = paired_question(module_map[card["module_id"]], card)
            questions.append(pair)
            qmap[pair["id"]] = pair
            pair_ids = [pair["id"]]
        else:
            pair_ids = card.get("question_ids", [])[:1]
            for qid in pair_ids:
                qmap[qid]["card_id"] = card["id"]
        card["paired_question_ids"] = pair_ids
        paired = [qmap[qid] for qid in pair_ids]
        card["question_placement"] = {
            "before": [q["id"] for q in paired if q["placement"] in ("before", "both")],
            "after": [q["id"] for q in paired if q["placement"] in ("after", "both")],
            "rationale": {q["id"]: q["placement_reason"] for q in paired},
        }
        card["pairing_exception"] = None
    legacy = json.loads(LEGACY.read_text(encoding="utf-8"))
    legacy_drills = {drill["id"]: drill for drill in legacy["drills"]}
    card_map = {card["id"]: card for card in cards}
    for legacy_id, card_id in LEGACY_CARD_MAP.items():
        drill = legacy_drills[legacy_id]
        concept = legacy["concepts"][drill["concept"]]
        card_map[card_id].setdefault("legacy_lessons", []).append({
            "id": legacy_id,
            "title": drill["title"],
            "concept_id": drill["concept"],
            "concept_title": concept["title"],
            "paradigm": concept["paradigm"],
            "keys": drill["keys"],
            "buys": drill["buys"],
            "source": drill["source"],
        })
    verified_methods = []
    verified_reviews = []
    verified_sequence = []
    first_guided = {}
    for card in cards:
        if card.get("method_requirement"):
            exact = bool(card["method_requirement"].get("exact_any_of"))
            verified_methods.append({
                "card_id": card["id"],
                "label": card["method_requirement"]["label"],
                "evidence": ("runtime-required exact accepted key path" if exact else
                             "runtime-required token pattern and optional key limit"),
            })
        for taught in card.get("method_alternatives", []):
            verified_methods.append({
                "card_id": card["id"], "label": taught["label"],
                "evidence": "runtime-recognized exact comparison path",
            })
        if card.get("review_source_card_id"):
            variants = (card.get("review_variants") or card.get("variants") or [])
            verified_reviews.append({
                "source_card_id": card["review_source_card_id"],
                "method_family": card["review_method_family"],
                "changed_art_variants": len(variants),
                "evidence": "source-linked changed-art review bank",
            })
        if card.get("grammar_stage") == "guided":
            for family in card.get("grammar_families", []):
                first_guided.setdefault(family, card["id"])
        elif card.get("grammar_stage") == "hidden":
            for family in card.get("grammar_families", []):
                verified_sequence.append({
                    "hidden_card_id": card["id"], "grammar_family": family,
                    "prior_guided_card_id": first_guided.get(family),
                })
    command_reviews = command_review_contract(cards)
    return {
        "schema": "vim-daily/curriculum@4", "revision": "2026-09-28.25",
        "review_intervals_hours": [4, 24, 72, 168, 336],
        "modules": modules, "cards": cards, "questions": questions,
        "verified_method_coverage": verified_methods,
        "verified_review_coverage": verified_reviews,
        "verified_grammar_sequence": verified_sequence,
        "verified_command_review_coverage": command_reviews,
    }


def validate(cur):
    errors = []
    modules, cards, questions = cur["modules"], cur["cards"], cur["questions"]
    module_map = {module["id"]: module for module in modules}
    legacy_ids = [lesson["id"] for card in cards for lesson in card.get("legacy_lessons", [])]
    expected_legacy = set(LEGACY_CARD_MAP)
    if set(legacy_ids) != expected_legacy or len(legacy_ids) != len(expected_legacy):
        errors.append("legacy lesson teaching payloads must attach exactly once: %r" % legacy_ids)

    def check_visual(card_id, label, rows, frame_rows=None):
        """Reject the one-glyph/toy stimuli that prompted the 2026-09-27 audit."""
        if not rows:
            errors.append(f"{card_id}: {label} is empty")
            return
        frames = ([rows[index:index + frame_rows] for index in range(0, len(rows), frame_rows)]
                  if frame_rows else [rows])
        for index, frame in enumerate(frames, 1):
            nonblank = [row for row in frame if row.strip()]
            ink = sum(sum(not char.isspace() for char in row) for row in frame)
            width = max((len(row.rstrip()) for row in frame), default=0)
            if len(nonblank) < 3 or ink < 7 or width < 5:
                errors.append(
                    f"{card_id}: {label} frame {index} is a toy stimulus "
                    f"(nonblank_rows={len(nonblank)}, ink={ink}, width={width})")
    if len(modules) != 19: errors.append(f"expected 19 modules, got {len(modules)}")
    expected_cards = sum(len(module["card_ids"]) for module in modules)
    if len(cards) != expected_cards:
        errors.append(f"module card inventories name {expected_cards} cards, got {len(cards)}")
    if len(cards) <= 152: errors.append("grammar insertion must grow the 152-card baseline")
    if len(questions) <= 190: errors.append("mixed-form pairing must grow the 190-question baseline")
    for label, rows in (("card", cards), ("question", questions)):
        ids = [row["id"] for row in rows]
        if len(ids) != len(set(ids)): errors.append(f"duplicate {label} ids")
    qids = {q["id"] for q in questions}
    first_guided = {}
    expected_sequence = []
    for card in cards:
        if card.get("grammar_stage") == "guided":
            for family in card.get("grammar_families", []):
                first_guided.setdefault(family, card["id"])
        elif card.get("grammar_stage") == "hidden":
            for family in card.get("grammar_families", []):
                prior = first_guided.get(family)
                expected_sequence.append({
                    "hidden_card_id": card["id"], "grammar_family": family,
                    "prior_guided_card_id": prior,
                })
                if not prior:
                    errors.append(
                        f"{card['id']}: hidden {family} has no earlier guided performance")
    if cur.get("verified_grammar_sequence") != expected_sequence:
        errors.append("verified grammar sequence does not match card order")
    try:
        expected_command_reviews = command_review_contract(cards)
    except ValueError as exc:
        errors.append(str(exc))
        expected_command_reviews = []
    if cur.get("verified_command_review_coverage") != expected_command_reviews:
        errors.append(
            "verified command review coverage must match each guided family and its later hidden retrieval")
    for q in questions:
        if not q.get("source_ref"): errors.append(f"{q['id']}: missing source reference")
        if ("ANIMATION\n" not in q.get("prompt", "")
                or "NEOVIM\n" not in q.get("prompt", "")):
            errors.append(f"{q['id']}: prompt does not visibly pair animation and Neovim")
        for field in ("card_id", "form", "grammar_family", "grammar_breakdown_id",
                      "paired_invariant", "placement", "placement_reason", "answer_contract"):
            if not q.get(field): errors.append(f"{q['id']}: missing paired-question field {field}")
        if q.get("form") in ("multiple_choice", "predict_art") and q.get("choices"):
            if len(q["choices"]) != 4 or len(q["feedback"]) != 4:
                errors.append(f"{q['id']}: choice form requires four choices and feedback messages")
            if not 0 <= q.get("correct_choice", -1) < len(q["choices"]):
                errors.append(f"{q['id']}: invalid answer")
        if q.get("form") == "multiple_choice":
            paired_fields = ("animation_prompt", "animation_answer", "neovim_prompt", "neovim_answer")
            if any(not q.get(field) for field in paired_fields):
                errors.append(f"{q['id']}: missing animation/Neovim paired-question fields")
            if any("ANIMATION:" not in choice or "NEOVIM:" not in choice for choice in q["choices"]):
                errors.append(f"{q['id']}: every choice must answer both halves")
            if (len(q.get("compact_choices", [])) != len(q["choices"])
                    or any("A:" not in choice or "V:" not in choice
                           for choice in q.get("compact_choices", []))):
                errors.append(f"{q['id']}: compact choices must preserve both paired halves")
            if "ANIMATION:" not in q.get("compact_prompt", "") or "NEOVIM:" not in q.get("compact_prompt", ""):
                errors.append(f"{q['id']}: compact prompt must preserve both domains")
            if any("Not yet" in message or "one or both halves" in message.lower()
                   for message in q["feedback"]):
                errors.append(f"{q['id']}: generic wrong-answer feedback is forbidden")
            if q["id"].endswith("Q01") and q["module_id"] != "M10":
                if "BEFORE" not in q["prompt"] or "AFTER" not in q["prompt"] or q["prompt"].count("│") < 6:
                    errors.append(f"{q['id']}: visual reading must preserve multi-row BEFORE/AFTER art")
    signatures = [(" ".join(q["prompt"].split()).casefold(),
                   tuple(" ".join(choice.split()).casefold() for choice in q.get("choices", [])))
                  for q in questions]
    if len(signatures) != len(set(signatures)):
        errors.append("duplicate conceptual question/choice set")
    mc_questions = [q for q in questions if q.get("form") == "multiple_choice"]
    stems = [q["animation_prompt"].split("\n\n", 1)[0].casefold() for q in mc_questions]
    if len(stems) != len(set(stems)):
        errors.append("every conceptual item needs its own authored animation stem")
    if sum("│" in q["animation_prompt"] for q in mc_questions) < 55:
        errors.append("at least half the conceptual bank must show the art it asks about")
    for q in mc_questions:
        animation_halves = [choice.split(" | NEOVIM: ", 1)[0] for choice in q["choices"]]
        neovim_halves = [choice.split(" | NEOVIM: ", 1)[1] for choice in q["choices"]]
        if sorted(animation_halves.count(value) for value in set(animation_halves)) != [2, 2]:
            errors.append(f"{q['id']}: animation halves leak the answer by frequency")
        if sorted(neovim_halves.count(value) for value in set(neovim_halves)) != [2, 2]:
            errors.append(f"{q['id']}: Neovim halves leak the answer by frequency")
    nodes = [module["node"] for module in modules]
    if len(nodes) != len(set(nodes)) or "A3/V4" not in nodes:
        errors.append("skill-tree nodes must be unique and the A3 bridge must be assigned")
    for module in modules:
        for field in ("meaning", "first_reading", "principle", "defect", "basic", "scaled", "source_ref"):
            if not module.get(field): errors.append(f"{module['id']}: missing teaching field {field}")
        own = [c for c in cards if c["module_id"] == module["id"]]
        if module["card_ids"] != [c["id"] for c in own]:
            errors.append(f"{module['id']}: card_ids do not match owned cards")
        original_ordinals = [c["ordinal"] for c in own
                             if re.fullmatch(r"M\d+\.\d\d", c["id"])]
        if original_ordinals != list(range(1, 9)):
            errors.append(f"{module['id']}: original card sequence is not 1..8")
        project_steps = [c for c in own if c.get("artifact") == "project"]
        for before, after in zip(project_steps, project_steps[1:]):
            if before["target"] != after["start"]:
                errors.append(f"{after['id']}: start does not continue {before['id']}")
    for before_module, after_module in zip(modules, modules[1:]):
        if before_module["project_id"] == after_module["project_id"]:
            before_steps = [c for c in cards if c["module_id"] == before_module["id"] and c.get("artifact") == "project"]
            after_steps = [c for c in cards if c["module_id"] == after_module["id"] and c.get("artifact") == "project"]
            if before_steps[-1]["target"] != after_steps[0]["start"]:
                errors.append(f"{after_module['id']}: shared project does not continue {before_module['id']}")
    for card in cards:
        if not card.get("prompt"): errors.append(f"{card['id']}: missing authored prompt")
        if not card.get("lesson_benefit"): errors.append(f"{card['id']}: missing honest lesson benefit")
        for field in ("grammar_families", "grammar_stage", "paired_question_ids",
                      "question_placement", "master_habits", "master_stages"):
            if not card.get(field):
                errors.append(f"{card['id']}: missing grammar-first field {field}")
        for qid in card.get("paired_question_ids", []):
            if qid not in qids:
                errors.append(f"{card['id']}: missing paired question {qid}")
        if card.get("pairing_exception"):
            if not card["pairing_exception"].get("reason"):
                errors.append(f"{card['id']}: pairing exception lacks a written reason")
        elif not card.get("paired_question_ids"):
            errors.append(f"{card['id']}: every card needs a paired question")
        if card.get("start"):
            frame_rows = card.get("frame_rows", module_map[card["module_id"]].get("frame_rows"))
            check_visual(card["id"], "start", card["start"], frame_rows)
            check_visual(card["id"], "target", card["target"], frame_rows)
        for qid in card.get("question_ids", []):
            if qid not in qids: errors.append(f"{card['id']}: missing question {qid}")
        if card["kind"] not in ("concept",) and card["ordinal"] not in (3, 7):
            if card["ordinal"] in (1, 2, 4, 5, 6, 8) and not card.get("expected"):
                errors.append(f"{card['id']}: missing executable recipe")
        if card.get("frame_slices") and sum(card["frame_slices"]) != len(card["target"]):
            errors.append(f"{card['id']}: frame slices do not cover target rows")
        frame_rows = card.get("frame_rows", module_map[card["module_id"]].get("frame_rows"))
        if frame_rows and card.get("target"):
            frames = [card["target"][index:index + frame_rows]
                      for index in range(0, len(card["target"]), frame_rows)]
            actual_pairs = [[index + 1, index + 2]
                            for index in range(len(frames) - 1)
                            if frames[index] == frames[index + 1]]
            declared = card.get("duplicate_frames", [])
            declared_pairs = [row.get("frames") for row in declared]
            if actual_pairs != declared_pairs:
                errors.append(
                    f"{card['id']}: adjacent duplicate roles do not match {actual_pairs}")
            for row in declared:
                if (row.get("role") not in
                        {"hold", "scaffold", "material-normalization", "reviewable-duplicate"}
                        or not row.get("reason") or "playback" not in row):
                    errors.append(f"{card['id']}: incomplete adjacent duplicate metadata")
                if row.get("role") == "hold" and (
                        row.get("playback") is not True
                        or row.get("duration_frames", 0) < 2):
                    errors.append(f"{card['id']}: hold lacks explicit playback duration")
        if card["kind"] == "compare_methods":
            methods = card.get("method_alternatives", [])
            if len(methods) != 2 or any(not all(m.get(k) for k in ("label", "keys", "why")) for m in methods):
                errors.append(f"{card['id']}: needs two executable named alternatives")
        rule = card.get("method_requirement")
        if rule:
            if (not rule.get("label")
                    or not (rule.get("exact_any_of") or rule.get("any_of")
                            or rule.get("all_of"))):
                errors.append(f"{card['id']}: incomplete runtime method requirement")
            if rule.get("max_tokens") is not None and rule["max_tokens"] < 1:
                errors.append(f"{card['id']}: invalid method key limit")
            any_ok = (not rule.get("any_of")
                      or any(pattern in card.get("expected", "")
                             for pattern in rule["any_of"]))
            all_ok = all(pattern in card.get("expected", "")
                         for pattern in rule.get("all_of", []))
            exact_ok = (not rule.get("exact_any_of")
                        or card.get("expected") in rule["exact_any_of"])
            if not (any_ok and all_ok and exact_ok):
                errors.append(f"{card['id']}: taught path does not satisfy its method requirement")
        review_variants = card.get("review_variants", [])
        if review_variants:
            starts = [tuple(variant.get("start", [])) for variant in review_variants]
            if len(review_variants) < 2 or len(starts) != len(set(starts)):
                errors.append(f"{card['id']}: needs two distinct card-specific review variants")
            if any(not all(variant.get(field) for field in
                           ("start", "target", "expected", "recipe"))
                   for variant in review_variants):
                errors.append(f"{card['id']}: incomplete card-specific review variant")
            for index, variant in enumerate(review_variants, 1):
                frame_rows = card.get("frame_rows", module_map[card["module_id"]].get("frame_rows"))
                check_visual(card["id"], f"review variant {index} start",
                             variant.get("start", []), frame_rows)
                check_visual(card["id"], f"review variant {index} target",
                             variant.get("target", []), frame_rows)
                review_rule = variant.get("method_requirement")
                if review_rule:
                    if (not review_rule.get("label") or not (
                            review_rule.get("exact_any_of")
                            or review_rule.get("any_of")
                            or review_rule.get("all_of"))):
                        errors.append(
                            f"{card['id']}: review variant {index} has an incomplete method requirement")
                    if (review_rule.get("exact_any_of")
                            and variant.get("expected") not in review_rule["exact_any_of"]):
                        errors.append(
                            f"{card['id']}: review variant {index} does not satisfy its exact method")
        review_capable = bool(review_variants or card["kind"] == "transfer")
        if review_capable:
            if (card.get("review_source_card_id") != card["id"]
                    or not card.get("review_method_family")):
                errors.append(f"{card['id']}: review bank lacks explicit source/family linkage")
        elif card.get("review_source_card_id") or card.get("review_method_family"):
            errors.append(f"{card['id']}: declares review linkage without changed-art variants")
        if card["kind"] == "transfer":
            variants = card.get("variants", [])
            starts = [tuple(variant.get("start", [])) for variant in variants]
            if len(variants) < 2 or len(starts) != len(set(starts)):
                errors.append(f"{card['id']}: needs distinct changed-art variants")
            if any(not all(variant.get(field) for field in ("start", "target", "expected", "recipe"))
                   for variant in variants):
                errors.append(f"{card['id']}: incomplete transfer variant")
            for index, variant in enumerate(variants, 1):
                frame_rows = module_map[card["module_id"]].get("frame_rows")
                check_visual(card["id"], f"transfer variant {index} start", variant["start"], frame_rows)
                check_visual(card["id"], f"transfer variant {index} target", variant["target"], frame_rows)
        if card.get("animation"):
            if not all(card["animation"].get(field) for field in ("role", "timing")):
                errors.append(f"{card['id']}: incomplete animation metadata")
            if card["animation"].get("role") == "hold" and not card["animation"].get("hold_reason"):
                errors.append(f"{card['id']}: hold needs a reason")
    # Linear prerequisites must point backward; this also catches cycles here.
    seen = set()
    for module in modules:
        if any(p not in seen for p in module["prerequisites"]):
            errors.append(f"{module['id']}: invalid/cyclic prerequisite")
        seen.add(module["id"])
    if len({card["title"] for card in cards}) != len(cards):
        errors.append("every card needs a distinct learner-visible title")
    if len({card["prompt"] for card in cards}) != len(cards):
        errors.append("every card needs a distinct authored prompt")
    expected_verified = sum(
        1 + len(card.get("method_alternatives", []))
        for card in cards if card.get("method_requirement")
    ) + sum(
        len(card.get("method_alternatives", []))
        for card in cards if not card.get("method_requirement")
    )
    if len(cur.get("verified_method_coverage", [])) != expected_verified:
        errors.append("verified method coverage must be derived only from runtime-enforced paths")
    expected_reviews = sum(
        1 for card in cards if card.get("review_variants") or card["kind"] == "transfer")
    if len(cur.get("verified_review_coverage", [])) != expected_reviews:
        errors.append("verified review coverage must be derived only from source-linked changed art")
    if errors:
        raise SystemExit("\n".join(errors))


def main():
    cur = build()
    validate(cur)
    OUT.write_text(json.dumps(cur, indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {OUT}: {len(cur['modules'])} modules, {len(cur['cards'])} cards, {len(cur['questions'])} questions")


if __name__ == "__main__":
    main()
