#!/usr/bin/env python3
"""Generate the VD-09 v2 project curriculum.

The source below is deliberately ordinary Python rather than hand-escaped JSON.
It owns stable card/question ids; curriculum-v2.json is the installed artifact.
Primary scaffolds are authored for the tutor. Audited Stone Story excerpts used
by local-only review and transfer surfaces live in ``stone_story_variants.py``;
their public-repository publication boundary remains unresolved.
"""

import json
import re
import textwrap
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stone_story_variants  # noqa: E402  (VD-29 art table beside this file)


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "curriculum-v2.json"
CATALOG = ROOT / "CURRICULUM_V2_CARD_CATALOG.md"
LEGACY = ROOT / "curriculum.json"
ANIMATION_PACK = ROOT / "animation_lesson_pack.md"
AUTHORED_QUESTION_FILES = (
    ROOT / "questions-authored-v2.json",
    ROOT / "questions-authored-v2-stills-a.json",
    ROOT / "questions-authored-v2-stills-b.json",
    ROOT / "questions-authored-v2-motion-a.json",
    ROOT / "questions-authored-v2-motion-b.json",
    ROOT / "questions-authored-v2-mastery.json",
)

# The standalone pack is deliberately attached to existing v2 cards instead
# of becoming a second scheduler.  These links give the generated artifact a
# real guided and key-hidden delivery route while keeping the source pack's
# original-art and rights boundary intact.
ANIMATION_PACK_DELIVERY = {
    "AL01": ("M0.01", "M0.06"),
    "AL02": ("M4.01", "M4.06"),
    "AL03": ("M9.01", "M9.06"),
    "AL04": ("M7.01", "M7.06"),
    "AL05": ("M18.01", "M18.06"),
    "AL06": ("M5.01", "M5.06"),
    "AL07": ("M6.01", "M6.08"),
    "AL08": ("M8.01", "M8.06"),
    "AL09": ("M14.01", "M14.06"),
    "AL10": ("M3.01", "M3.06"),
    "AL11": ("M11.01", "M11.06"),
    "AL12": ("M16.01", "M16.06"),
}

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
    expected = {f"M{module}.{ordinal:02d}" for module in range(20) for ordinal in range(1, 9)}
    if set(rows) != expected:
        missing = sorted(expected - set(rows))
        extra = sorted(set(rows) - expected)
        raise SystemExit(f"catalog card mismatch: missing={missing} extra={extra}")
    return rows


def _pack_sections(text):
    """Return the authored AL01..AL12 sections without copying source art."""
    matches = list(re.finditer(r"^## (AL\d{2}) — (.*?)$", text, re.MULTILINE))
    sections = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1)] = {
            "title": match.group(2).strip(),
            "text": text[match.start():end],
        }
    return sections


def _pack_region(section, heading, next_headings):
    """Extract one markdown heading region, retaining authored whitespace."""
    start = section.find(heading)
    if start < 0:
        return ""
    start += len(heading)
    ends = [section.find(candidate, start) for candidate in next_headings]
    ends = [end for end in ends if end >= 0]
    return section[start:min(ends) if ends else len(section)]


def _pack_bullets(region):
    """Group markdown bullets and their indented continuation lines."""
    items, current = [], None
    for line in region.splitlines():
        match = re.match(r"^\s*-\s+(.*)$", line)
        if match:
            current = match.group(1).strip()
            items.append(current)
        elif current and line.strip():
            current += " " + line.strip()
            items[-1] = current
    return items


def _pack_fields(region):
    """Parse the labeled bullets used by pack questions."""
    fields, current = {}, None
    for line in region.splitlines():
        match = re.match(r"^\s*-\s+([A-Za-z][A-Za-z -]+):\s*(.*)$", line)
        if match:
            current = match.group(1).strip().lower().replace(" ", "_")
            fields[current] = match.group(2).strip()
        elif current and line.strip():
            fields[current] += " " + line.strip()
    return fields


def _pack_codes(map_text):
    """Expand the pack's compact H/S/A ranges into auditable metadata."""
    codes = []
    for prefix in ("H", "S", "A"):
        for match in re.finditer(
                rf"\b{prefix}(\d)\s*[–-]\s*{prefix}?(\d)\b", map_text):
            codes.extend(f"{prefix}{number}"
                         for number in range(int(match.group(1)), int(match.group(2)) + 1))
    for code in re.findall(r"\b[HSA]\d\b", map_text):
        if code not in codes:
            codes.append(code)
    return codes


def _pack_question_blocks(region):
    matches = list(re.finditer(r"^#### (AL\d{2}-Q\d+) — (.*?)$", region, re.MULTILINE))
    questions = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(region)
        body = region[match.end():end]
        fields = _pack_fields(body)
        questions.append({"id": match.group(1), "title": match.group(2).strip(), **fields})
    return questions


def load_animation_lesson_pack():
    """Compile the standalone authoring source into live curriculum metadata.

    The parser intentionally reads only original exercises, lesson contracts,
    and question prose.  The cited corpus paths remain evidence strings; no
    corpus frame, tutorial plate, or derivative is imported into the output.
    """
    if not ANIMATION_PACK.exists():
        raise SystemExit(f"missing animation lesson pack: {ANIMATION_PACK}")
    text = ANIMATION_PACK.read_text(encoding="utf-8")
    sections = _pack_sections(text)
    expected_ids = [f"AL{number:02d}" for number in range(1, 13)]
    if list(sections) != expected_ids:
        raise SystemExit(f"animation pack lesson mismatch: {list(sections)}")

    lessons = []
    for lesson_id in expected_ids:
        section = sections[lesson_id]["text"]
        heading = sections[lesson_id]["title"]
        map_match = re.search(r"^\*\*Map:\*\* (.*?)\s*$", section, re.MULTILINE)
        if not map_match:
            raise SystemExit(f"{lesson_id}: missing map")
        map_text = map_match.group(1)
        codes = _pack_codes(map_text)
        habits = [code for code in codes if code.startswith("H")]
        stages = [code for code in codes if code.startswith(("S", "A"))]
        source_region = _pack_region(
            section, "**Source evidence:**", ("### Original exercise",))
        source_evidence = " ".join(line.strip() for line in source_region.splitlines()).strip()
        original_region = _pack_region(
            section, "### Original exercise",
            ("### Guided sequence", "### Hidden sequence"))
        code_frames = [frame.rstrip("\n").splitlines()
                       for frame in re.findall(r"```(?:text)?\n(.*?)```", original_region, re.DOTALL)]
        paragraphs = []
        in_code = False
        current = []
        for line in original_region.splitlines():
            if line.startswith("```"):
                if in_code and current:
                    current = []
                in_code = not in_code
                continue
            if in_code:
                continue
            if line.strip():
                current.append(line.strip())
            elif current:
                paragraphs.append(" ".join(current))
                current = []
        if current:
            paragraphs.append(" ".join(current))
        do_this_text = paragraphs[0] if paragraphs else heading
        guided_region = _pack_region(
            section, "### Guided sequence", ("### Hidden sequence",))
        hidden_region = _pack_region(
            section, "### Hidden sequence", ("### Questions",))
        guided = _pack_bullets(guided_region)
        hidden = _pack_bullets(hidden_region)
        questions_region = _pack_region(
            section, "### Questions", ("### Changed-art review",))
        source_questions = _pack_question_blocks(questions_region)
        if len(source_questions) != 2:
            raise SystemExit(f"{lesson_id}: expected two authored questions")
        questions = []
        for source_question in source_questions:
            placement_text = source_question.get("placement", "").lower()
            placement = ("before" if placement_text.startswith("before") else
                         "after" if placement_text.startswith("after") else "")
            ask = source_question.get("ask", "")
            expected = source_question.get("expected_answer", "")
            answer_format = source_question.get("answer_format", "")
            # The pack's animation decision is paired with a Neovim scope
            # check.  Exact keys remain hidden for hidden work; the answer
            # contract still names the required operation and invariant.
            neovim_answer = (
                f"Use the {placement} lesson scope; preserve the fixed-width, "
                f"registration, or timing invariant named by the task."
            )
            questions.append({
                "id": source_question["id"],
                "title": source_question["title"],
                "placement": placement,
                "animation_prompt": ask,
                "animation_answer": expected,
                "neovim_prompt": (
                    "Name the Neovim edit scope that demonstrates the same "
                    "animation decision, and state one invariant to preserve."
                ),
                "neovim_answer": neovim_answer,
                "answer_format": answer_format,
                "paired_answer_format": (
                    f"ANIMATION: {answer_format}; NEOVIM: scope + invariant"
                ),
                "prior_teaching_basis": source_question.get("prior_teaching_basis", ""),
                "clarity_check": source_question.get("clarity_check", ""),
                "placement_rationale": source_question.get("placement_rationale", ""),
                "explicit_answer": f"ANIMATION: {expected} NEOVIM: {neovim_answer}",
            })
        review_region = _pack_region(
            section, "### Changed-art review", ("### Question audit",))
        review_items = _pack_bullets(review_region)
        review_summary = " ".join(review_items).strip()
        variant_source = review_items[0] if review_items else "Two original changed-art variants."
        variant_source = re.sub(r"^Variants:\s*", "", variant_source)
        variant_descriptions = re.split(
            r"\s+and\s+(?=(?:an?|the)\s|\(\d)", variant_source, maxsplit=1)
        if len(variant_descriptions) != 2:
            variant_descriptions = [
                "first original variant described by the lesson",
                "second original variant described by the lesson",
            ]
        audit_region = _pack_region(
            section, "### Question audit", ("### Rights gate",))
        audit_text = audit_region.lower()
        question_audit = {
            "student_can_answer_from_prior_teaching": (
                "student-can-answer-from-prior-teaching: yes" in audit_text),
            "request_is_clear": "request-is-clear: yes" in audit_text,
            "placement_makes_sense": "placement-makes-sense: yes" in audit_text,
        }
        hint = next((item for item in hidden if item.lower().startswith("hint")),
                    "Use the named invariant before changing a cell.")
        target = next((item for item in hidden if item.lower().startswith("pass")),
                      "Preserve the declared fixed-width registration contract.")
        guided_card, hidden_card = ANIMATION_PACK_DELIVERY[lesson_id]
        lessons.append({
            "id": lesson_id,
            "title": heading,
            "domains": ["ascii_animation", "neovim"],
            "source": "share/animation_lesson_pack.md",
            "source_evidence": source_evidence,
            "master_habits": habits,
            "master_stages": stages,
            "do_this": f"DO THIS — {do_this_text}",
            "target": f"TARGET — {target}",
            "hint": f"HINT — {hint}",
            "ascii_exercise": {
                "original": True,
                "frames": code_frames,
                "fixed_width": True,
                "registration": "Keep every frame in one equal-width, blank-line-delimited box.",
            },
            "neovim_exercise": {
                "guided": {"key_hidden": False, "steps": guided},
                "hidden": {"key_hidden": True, "keys": "withheld", "steps": hidden},
            },
            "guided_sequence": guided,
            "hidden_sequence": hidden,
            "questions": questions,
            "question_audit": question_audit,
            "changed_art_review": {
                "hidden": True,
                "variant_count": 2,
                "variants": [
                    {"id": f"{lesson_id}-V1",
                     "description": f"New variant 1 — {variant_descriptions[0].strip(' .')}"},
                    {"id": f"{lesson_id}-V2",
                     "description": f"New variant 2 — {variant_descriptions[1].strip(' .')}"},
                ],
                "source": "original pack art only; changed variants are authored at delivery time",
            },
            "earlier_guided_family_gate": {
                "required": True,
                "guided_card_id": guided_card,
                "hidden_card_id": hidden_card,
                "hidden_after_guided": True,
                "prior_pack_lessons": expected_ids[:expected_ids.index(lesson_id)],
            },
            "delivery": {"guided_card_id": guided_card, "hidden_card_id": hidden_card},
            "rights_gate": {
                "integration": "blocked",
                "source_art_used": False,
                "source_use": "research evidence and general technique only",
                "original_art_only": True,
            },
        })
    return lessons


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
        "id": "M0", "title": "Spark loop", "node": "A1/V0", "project": "spark-loop",
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
        "transfer": dict(step(
            stone_story_variants.FIREWORK_RADIAL_F3,
            [stone_story_variants.FIREWORK_RADIAL_F3[0], "   =—O—=", stone_story_variants.FIREWORK_RADIAL_F3[2]],
            "j0f*rO:s/-/=/g<CR>",
            [["j0f*rO", "find and brighten the Fireworks shell core"],
             [":s/-/=/g", "change both outer rays on that row without touching other rows"]],
        ), source="official-Cosmetics/Fireworks res06 radial frame 3 crop; authored core-and-outer-ray brightness pass",
           prompt=(
               "Brighten the Fireworks shell core from * to O and both outer rays from - to =; "
               "preserve the vertical accents and all row widths."
           )),
        "transfer_alt": dict(step(
            stone_story_variants.FIREWORK_RADIAL_F4,
            [stone_story_variants.FIREWORK_RADIAL_F4[0], "  •=—O—=•", stone_story_variants.FIREWORK_RADIAL_F4[2]],
            "j0f*rO:s/-/=/g<CR>",
            [["j0f*rO", "find and brighten the wider radial core"],
             [":s/-/=/g", "change only its two outer ASCII rays; keep the em-dash spokes"]],
        ), source="official-Cosmetics/Fireworks res06 radial frame 4 crop; authored core-and-outer-ray brightness pass",
           prompt=(
               "Brighten the wider radial core from * to O and only its outer ASCII rays from - to =; "
               "preserve both inner em-dash spokes and the upper/lower accents."
           )),
        "migration_starts": {
            4: [[" · ", " o "], [" · ", " · "]],
        },
    },
    {
        "id": "M1", "title": "Contour run", "node": "S1/V1", "project": "line-run",
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
                "4G3ddGo´<CR> `-.:<CR>o_.-<Esc>",
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
        "id": "M2", "title": "Face focus", "node": "S3/V2", "project": "shape-edit",
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
        "transfer": dict(step(
            stone_story_variants.FROG_HALF + [""],
            stone_story_variants.FROG_ONE_OPEN + [""],
            "0f=rO",
            [["0f=", "find Frog's half-closed left eye on the visible face row"],
             ["rO", "open only that eye without shifting the paired right eye"]],
            method_requirement=require_method(
                "reach the eye row, find the eye, and replace it in place",
                exact_any_of=["0f=rO"]),
        ), source="official-Pets/Frog res01 half-eye overlay to res05 one-open-eye overlay; blank fourth registration row",
           prompt=(
               "Open only Frog's left eye from = to O; preserve the right dash, body, "
               "legs, and the blank fourth registration row."
           )),
        "transfer_alt": dict(step(
            stone_story_variants.SKULLY_IDLE + [""],
            stone_story_variants.SKULLY_LOOK + [""],
            "j0forO",
            [["j0fo", "find Skully's left eye on the face row"],
             ["rO", "widen only that eye into the look state"]],
            method_requirement=require_method(
                "reach the eye row, find the eye, and replace it in place",
                exact_any_of=["j0forO"]),
        ), source="official-Pets/Skully res01 idle to res02 look overlay; blank fourth registration row",
           prompt=(
               "Widen only Skully's left eye from o to O; preserve the right eye, "
               "skull contour, mouth, and blank fourth registration row."
           )),
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
        "transfer": dict(step(
            stone_story_variants.FACE_SHOCK,
            stone_story_variants.FACE_SHOCK + [
                "  (O) (o)" if row == "  (o) (o)" else row
                for row in stone_story_variants.FACE_SHOCK
            ],
            "ggV5j\"ayG\"ap9G0forO",
            [["ggV5j\"ay", "select the complete six-row FaceHUD pose into named register a"],
             ["G\"ap", "put that complete registered pose after the original"],
             ["9G0forO", "change only the copied left pupil"]],
        ), source="official-UI/FaceHUD res08 shock pose"),
        "transfer_alt": dict(step(
            stone_story_variants.FACE_NEUTRAL,
            stone_story_variants.FACE_NEUTRAL + [
                "  <O) (o>" if row == "  <o) (o>" else row
                for row in stone_story_variants.FACE_NEUTRAL
            ],
            "ggV5j\"ayG\"ap9G0forO",
            [["ggV5j\"ay", "select the complete six-row neutral FaceHUD pose"],
             ["G\"ap", "put the stored pose after the original"],
             ["9G0forO", "change only the copied left pupil"]],
        ), source="official-UI/FaceHUD res02 neutral pose"),
    },
    {
        "id": "M4", "title": "Rotation tween", "node": "A2/V4", "project": "rotation-tween",
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
        "transfer": dict(step(
            stone_story_variants.MISSILE_F1 + stone_story_variants.MISSILE_F4,
            stone_story_variants.MISSILE_F1 + stone_story_variants.MISSILE_F2
            + stone_story_variants.MISSILE_F4,
            ":1,3t3<CR>5G$r'",
            [[":1,3t3", "copy the complete first missile frame into the gap"],
             ["5G$r'", "advance only the copied exhaust endpoint from dot to apostrophe"]],
        ), source="official-Games/TowerDefense res18 missile frames 1, 2, and 4",
           prompt=(
               "Insert missile exhaust frame 2 between frames 1 and 4: copy the complete "
               "first frame, then change only the copied exhaust endpoint from . to '."
           )),
        "transfer_alt": dict(step(
            stone_story_variants.CHICK_EGG_F1 + stone_story_variants.CHICK_EGG_F4,
            stone_story_variants.CHICK_EGG_F1 + stone_story_variants.CHICK_EGG_F2
            + stone_story_variants.CHICK_EGG_F4,
            ":1,3t3<CR>5G0f:2lR;<Esc>",
            [[":1,3t3", "copy the complete uncracked egg frame into the gap"],
             ["5G0f:2lR;<Esc>", "replace the centred blank with the first crack mark"]],
        ), source="official-Pets/Chick res01 hatch frames 1, 2, and 4",
           prompt=(
               "Insert hatch frame 2 between the uncracked egg and frame 4: copy the "
               "complete first egg, then add only its first semicolon crack."
           )),
    },
    {
        "id": "M5", "title": "Layered scene", "node": "S6/V5", "project": "layered-scene",
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
        "transfer": dict(step(
            stone_story_variants.PAD_2 + stone_story_variants.PAD_1,
            stone_story_variants.PAD_1 + stone_story_variants.PAD_2,
            ":1,5m$<CR>",
            [[":1,5m$", "move complete lily-pad frame 2 after frame 1"]],
        ), source="official-Games/FrogBog res06 and res05 lily-pad frames 2 then 1",
           labels=True,
           prompt=(
               "Correct the reversed FrogBog plan: move the complete five-row pad 2 "
               "after pad 1 without copying or separating its numbered centre."
           )),
        "transfer_alt": dict(step(
            stone_story_variants.PAD_3 + stone_story_variants.PAD_2,
            stone_story_variants.PAD_2 + stone_story_variants.PAD_3,
            ":1,5m$<CR>",
            [[":1,5m$", "move complete lily-pad frame 3 after frame 2"]],
        ), source="official-Games/FrogBog res07 and res06 lily-pad frames 3 then 2",
           labels=True,
           prompt=(
               "Correct the second FrogBog plan: move the complete five-row pad 3 "
               "after pad 2 while preserving every contour and water-mark row."
           )),
    },
    {
        "id": "M7", "title": "Timed build", "node": "A4/V7", "project": "timed-pyramid-build",
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
        "transfer": dict(step(
            (stone_story_variants.SKULLY_IDLE + ["", ""]) * 2,
            (stone_story_variants.SKULLY_LOOK + ["", ""]) * 2,
            "2G0forO5j.",
            [["2G0forO", "make the first held Skully look left"],
             ["5j.", "repeat that one-cell eye edit in its timed duplicate"]],
        ), source="official-Pets/Skully res01 idle + res02 look overlay, held twice",
           prompt=(
               "Both padded Skully hold frames must look left: change the first "
               "eye, move exactly one five-row frame, and repeat the same edit."
           )),
        "transfer_alt": dict(step(
            (stone_story_variants.FROG_OPEN + ["", ""]) * 2,
            (stone_story_variants.FROG_ONE_OPEN + ["", ""]) * 2,
            "gg$r-5j.",
            [["gg$r-", "close the right eye in the first held frog frame"],
             ["5j.", "repeat that one-cell blink edit in the timed duplicate"]],
        ), source="official-Pets/Frog res01 + res05 blink overlay, held twice",
           prompt=(
               "Close the right eye in both padded Frog hold frames: edit the first "
               "frame at its visible row end, then move five rows and repeat."
           )),
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
                "Go \\o<Esc>o  |\\<Esc>o  |<Esc>o /|<Esc>o/  _\\<Esc>",
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
        "transfer": dict(step(
            stone_story_variants.DRACULA_WALK_F3 + ["", ""],
            stone_story_variants.DRACULA_WALK_F4 + ["", ""],
            "3G0f>r|",
            [["3G0f>", "find the trailing foot on the Dracula hem row"],
             ["r|", "plant that foot for walk frame 4"]],
        ), source="official-Pets/Dracula res01 walk frame 3 to frame 4",
           prompt=(
               "Advance Dracula walk frame 3 to frame 4 by planting only the trailing "
               "foot `>` as `|`; keep the cape, torso, and five-row padding fixed."
           )),
        "transfer_alt": dict(step(
            stone_story_variants.DRACULA_WALK_F4 + ["", ""],
            stone_story_variants.DRACULA_WALK_F5 + ["", ""],
            "3G$r>",
            [["3G$", "reach the planted foot at the end of the Dracula hem row"],
             ["r>", "kick that foot forward for walk frame 5"]],
        ), source="official-Pets/Dracula res01 walk frame 4 to frame 5",
           prompt=(
               "Advance Dracula walk frame 4 to frame 5 by changing only the final "
               "foot from backslash to `>`; preserve every other source cell."
           )),
    },
    {
        "id": "M9", "title": "Original bounce capstone", "node": "A7/V9", "project": "original-micro",
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
        "transfer": dict(step(
            stone_story_variants.BOO_HOVER_F3,
            stone_story_variants.BOO_HOVER_F4,
            "3G0C /   \\<Esc>",
            [["3G0", "address only Boo's acting skirt row"],
             ["C /   \\<Esc>", "redraw the flare as the inward-folded squash contour"]],
        ), source="official-Pets/Boo res01 hover frame 3 to frame 4",
           prompt=(
               "Fold Boo's lower contour inward for the squash phase; redraw only the "
               "third row and keep the crown and body registered."
           )),
        "transfer_alt": dict(step(
            stone_story_variants.BOO_HOVER_F2,
            stone_story_variants.BOO_HOVER_F3,
            "2G0r $xj0R-´   `-<Esc>",
            [["2G0r $x", "remove the two body anchors without shifting its interior"],
             ["j0R-´   `-<Esc>", "overwrite the complete skirt contour for the outward settle"]],
        ), source="official-Pets/Boo res01 hover frame 2 to frame 3",
           prompt=(
               "Settle Boo's hover outward by removing both underscore body anchors, "
               "then restore the flared skirt contour; keep the crown fixed."
           )),
    },
    {
        "id": "M10", "title": "SJIS puff tween", "node": "P/V10", "project": "sjis-puff-tween",
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
        "id": "M11", "title": "Fixed-width redraw", "node": "S0/V11", "project": "redraw-lab",
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
                ":set virtualedit=all<CR>2G13|i|<Esc>3j13|i|<Esc>",
                [[":set virtualedit=all", "permit an exact column target beyond the short acting rows"],
                 ["2G13|i|<Esc>", "position before display column 14 and insert the first blur trail there"],
                 ["3j13|i|<Esc>", "move to the homologous row, address column 14 explicitly, and insert its trail"]],
                method_requirement=require_method(
                    "enable virtual editing and place both trails at exact column 14",
                    exact_any_of=[":set virtualedit=all<CR>2G13|i|<Esc>3j13|i|<Esc>"]),
                review_variants=[
                    step(["/--\\  /--\\", "| x|  |x |", "\\__|  |__/",
                          "/..\\  /--\\", "| X|  |X |", "\\__|  |__/"],
                         ["/--\\  /--\\", "| x|  |x |  |", "\\__|  |__/",
                          "/..\\  /--\\", "| X|  |X |  |", "\\__|  |__/"],
                         ":set virtualedit=all<CR>2G13|i|<Esc>3j13|i|<Esc>",
                         [["virtualedit / 13| twice", "align both changed-art trails without relying on dot"]]),
                    step([".==.  .--.", "| *|  |* |", "'__'  '__'",
                          ".~~.  .--.", "| +|  |+ |", "'__'  '__'"],
                         [".==.  .--.", "| *|  |* |  |", "'__'  '__'",
                          ".~~.  .--.", "| +|  |+ |  |", "'__'  '__'"],
                         ":set virtualedit=all<CR>2G13|i|<Esc>3j13|i|<Esc>",
                         [["virtualedit / 13| twice", "align the alternate trails without relying on dot"]]),
                ],
            ),
        ],
        "transfer": dict(step(
            stone_story_variants.SNAIL_OPEN,
            stone_story_variants.SNAIL_BLINK,
            "0fOR--<Esc>",
            [["0fO", "find the first open eye on Snail's face row"],
             ["R--<Esc>", "overwrite both eyes shut without shifting the shell"]],
            method_requirement=require_method(
                "transfer the two-cell blink with Replace mode",
                exact_any_of=["0fOR--<Esc>"]),
        ), source="official-Pets/Snail res05-res07 + res12 to res15 blink composite; @ spiral adapted to O",
           prompt=(
               "Close Snail's two eyes with one fixed-width Replace-mode redraw; "
               "preserve the shell, spiral, slash, and moving baseline."
           )),
        "transfer_alt": dict(step(
            stone_story_variants.SNAIL_CRAWL_F4,
            stone_story_variants.SNAIL_CRAWL_IDLE,
            "3G0r¯",
            [["3G0", "address the first cell of Snail's acting crawl baseline"],
             ["r¯", "settle the one high accent back to the flat baseline"]],
        ), source="official-Pets/Snail res28-res31 to res32-res35 crawl composites; @ spiral adapted to O",
           prompt=(
               "Close Snail's crawl loop by settling only the baseline's first accent "
               "from acute to macron; keep eyes, shell, and the other three baseline cells fixed."
           )),
    },
    {
        "id": "M12", "title": "Joint sweep", "node": "S4/V12", "project": "mirror-sweep",
        "skill": "staggered bilateral accents with till motions and repeated character searches",
        "frame_rows": 3,
        "source_ref": "ascii-art-authoring §4.6 joint height and off-vertical anti-aliasing; §10 stagger and drag; Neovim help f, t, ;, comma, visual-mode, gv",
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
        "transfer": dict(step(
            stone_story_variants.SNOWMAN_OPEN_CROP,
            stone_story_variants.SNOWMAN_BLINK_CROP,
            "2j0t•lr-$T•hr-",
            [["2j0t•lr-", "approach the left eye from the row start and close it"],
             ["$T•hr-", "approach the right eye from the row end and close it"]],
            method_requirement=require_method(
                "close both Snowman eyes with forward and backward till motions",
                exact_any_of=["2j0t•lr-$T•hr-"]),
        ), source="official-Pets/Snowman res01 face crop + res08 blink overlay",
           prompt=(
               "Close both Snowman eyes from bullet to dash; preserve the hat, comma, "
               "parentheses, cheek punctuation, and row width."
           )),
        "transfer_alt": dict(step(
            stone_story_variants.SNOWMAN_BLINK_CROP,
            stone_story_variants.SNOWMAN_CHEER_CROP,
            "2j0t-lr^$T-hr^",
            [["2j0t-lr^", "approach the left closed eye from the row start and lift it"],
             ["$T-hr^", "approach the right closed eye from the row end and lift it"]],
            method_requirement=require_method(
                "lift both Snowman eyes with paired till motions",
                exact_any_of=["2j0t-lr^$T-hr^"]),
        ), source="official-Pets/Snowman res01 face crop + res08 blink overlay to res06 raised-eye overlay",
           prompt=(
               "Lift both Snowman eyes from dash to caret; preserve the hat, comma, "
               "parentheses, cheek punctuation, and row width."
           )),
    },
    {
        "id": "M13", "title": "Texture pulse", "node": "A4/V13", "project": "texture-pulse",
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
        "transfer": dict(step(
            stone_story_variants.FIREWORK_WILLOW_NODES,
            [stone_story_variants.FIREWORK_WILLOW_NODES[0],
             "  ·  !  !",
             stone_story_variants.FIREWORK_WILLOW_NODES[2]],
            "j03Wr!Br!",
            [["j0", "select the willow canopy's three separated lower nodes"],
             ["3Wr!", "cross leading whitespace and reach the right node in place"],
             ["Br!", "return one WORD and brighten the centre node"]],
            method_requirement=require_method(
                "use counted W and B on visible Fireworks node groups",
                exact_any_of=["j03Wr!Br!"]),
        ), source="official-Cosmetics/Fireworks res03 willow frame 5 lower canopy; authored centre/right node pulse",
           prompt=(
               "Brighten the centre and right nodes of the willow canopy in place; "
               "keep the upper spark row, left node, and lower apostrophe row registered."
           )),
        "transfer_alt": dict(step(
            stone_story_variants.FIREWORK_RADIAL_NODES,
            ["   ! : !",
             stone_story_variants.FIREWORK_RADIAL_NODES[1],
             stone_story_variants.FIREWORK_RADIAL_NODES[2]],
            "0Er!2Er!",
            [["0Er!", "reach and brighten the first separated radial node"],
             ["2Er!", "cross the centre node and brighten the third"]],
            method_requirement=require_method(
                "use WORD-end motions on the first and third radial nodes",
                exact_any_of=["0Er!2Er!"]),
        ), source="official-Cosmetics/Fireworks res06 radial frame 5 crop; authored outer-node pulse",
           prompt=(
               "Brighten only the two outer nodes of the radial firework; keep the centre "
               "colon and the two lower structural rows registered."
           )),
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
        "transfer": dict(step(
            stone_story_variants.SKULLY_O_PALETTE + [""],
            stone_story_variants.SKULLY_O_PALETTE_LOOK + [""],
            "fO\"aylj0foR<C-r>a<Esc>",
            [["fO\"ayl", "copy the visible O material into named register a"],
             ["j0foR<C-r>a<Esc>", "retrieve it over Skully's left eye without shifting the face"]],
            method_requirement=require_method(
                "transfer the visible O palette through named register a",
                exact_any_of=["fO\"aylj0foR<C-r>a<Esc>"]),
        ), source="official-Pets/Skully res01 to res02 look overlay with tutor palette annotation",
           prompt=(
               "Copy the visible O material from Skully's palette into register a, "
               "then widen only the left eye into the look pose."
           )),
        "transfer_alt": dict(step(
            stone_story_variants.SNOWBUNNY_FACE_PALETTE + [""],
            stone_story_variants.SNOWBUNNY_FACE_PALETTE_BLINK + [""],
            "f-\"aylj0fnR<C-r>a<Esc>2lR<C-r>a<Esc>",
            [["f-\"ayl", "copy the visible dash material into named register a"],
             ["j0fnR<C-r>a<Esc>", "retrieve it over the first eye"],
             ["2lR<C-r>a<Esc>", "reuse the same register over the second eye to complete the blink"]],
            method_requirement=require_method(
                "reuse one named palette register for both blink eyes",
                exact_any_of=["f-\"aylj0fnR<C-r>a<Esc>2lR<C-r>a<Esc>"]),
        ), source="official-Pets/SnowBunny res01 to res03 blink overlay with tutor palette annotation",
           prompt=(
               "Copy the visible dash material into register a, then reuse it over both "
               "SnowBunny eyes to complete the blink without shifting the face."
           )),
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
        "transfer": dict(step(
            stone_story_variants.DRILL_TREAD_SCENE,
            [stone_story_variants.DRILL_TREAD_SCENE[0],
             " " + stone_story_variants.DRILL_TREAD_SCENE[1],
             stone_story_variants.DRILL_TREAD_SCENE[2]],
            "j:set shiftwidth=1<CR>>>",
            [["j", "select only the Drill's repeated tread band"],
             [":set shiftwidth=1<CR>", "bind one indent step to one animation cell"],
             [">>", "pan the complete tread band right by that one-cell step"]],
            method_requirement=require_method(
                "pan the source tread with an explicit one-cell indent",
                exact_any_of=["j:set shiftwidth=1<CR>>>"]),
        ), source="official-Cosmetics/Drill res26 tread shimmer layer",
           prompt=(
               "Pan only the Drill's repeated tread band one cell right; keep the machine "
               "edge above and the angled support row below registered."
           )),
        "transfer_alt": dict(step(
            stone_story_variants.CAVE_LAVA_B,
            stone_story_variants.CAVE_LAVA_A,
            "2j:set shiftwidth=1<CR>>>",
            [["2j", "select only the CaveParty lava band"],
             [":set shiftwidth=1<CR>", "bind one indent step to one animation cell"],
             [">>", "advance the lava phase right by that one-cell step"]],
            method_requirement=require_method(
                "advance the source lava phase with an explicit one-cell indent",
                exact_any_of=["2j:set shiftwidth=1<CR>>>"]),
        ), source="official-Cosmetics/CaveParty res06 lava frame 2 to frame 1 crop",
           prompt=(
               "Advance only the CaveParty lava band one cell right; keep the figure's "
               "head and torso rows registered above it."
           )),
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
            ["    _", " ,'   `.", "/    1  \\", "\\       /", " \\/|..-'"],
            ["    _", " ,'   `.", "/    2  \\", "\\       /", " \\/|..-'"],
            "3G0f1<C-a>",
            [["3G0f1", "address the number drawn inside the FrogBog pad"],
             ["<C-a>", "advance pad frame 1 to frame 2 without moving its contour"]],
            method_requirement=require_method(
                "increment the embedded FrogBog frame number without redrawing the pad",
                exact_any_of=["3G0f1<C-a>"]),
        ),
        "transfer_alt": step(
            ["    _", " ,'   `.", "/    2  \\", "\\       /", " \\/|..-'"],
            ["    _", " ,'   `.", "/    3  \\", "\\       /", " \\/|..-'"],
            "3G0f2<C-a>",
            [["3G0f2", "address the next number drawn inside the FrogBog pad"],
             ["<C-a>", "advance pad frame 2 to frame 3 without moving its contour"]],
            method_requirement=require_method(
                "increment the alternate embedded FrogBog frame number",
                exact_any_of=["3G0f2<C-a>"]),
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
        "transfer": dict(step(
            stone_story_variants.CRANIUS_OPEN_CROP,
            stone_story_variants.CRANIUS_HAPPY_CROP,
            "/\\*<CR>r^n.",
            [["/\\*<CR>", "search for the first Cranius eye material"],
             ["r^", "lift the first eye in place"],
             ["n.", "find the homologous second eye and repeat only that replacement"]],
            method_requirement=require_method(
                "use search repeat and dot on both Cranius eye anchors",
                exact_any_of=["/\\*<CR>r^n."]),
        ), source="official-Pets/Cranius res01 open face crop + res04 happy overlay",
           prompt=(
               "Lift both Cranius eye stars into carets with search repeat and dot; "
               "preserve sockets, nose, jaw, and row width."
           )),
        "transfer_alt": dict(step(
            stone_story_variants.CRANIUS_HALF_CROP,
            stone_story_variants.CRANIUS_SHUT_CROP,
            "/==<CR>R--<Esc>n.",
            [["/==<CR>", "search for the first half-blink eye pair"],
             ["R--<Esc>", "close that two-cell eye material without shifting its socket"],
             ["n.", "find the second eye pair and repeat the bounded overwrite"]],
            method_requirement=require_method(
                "use search repeat and dot on both Cranius blink pairs",
                exact_any_of=["/==<CR>R--<Esc>n."]),
        ), source="official-Pets/Cranius res06 half-blink crop to res07 shut-eye overlay",
           prompt=(
               "Close both Cranius half-blink eye pairs from == to --; preserve sockets, "
               "nose, jaw, and row width."
           )),
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
    {
        "id": "M19", "title": "Mirror key-pose still", "node": "S2/V19",
        "stage": "S2", "project": "mirror-key-pose-still", "frame_rows": 5,
        "labels_steps": [1, 2, 4, 5, 6, 8],
        "skill": "hand mirroring a complete still with virtual replace and directional glyph judgment",
        "source_ref": "ascii-art-authoring §§4.4,4.7.7; Neovim help gR, f, ;, :copy",
        "meaning": "a left-facing key-pose still is copied and redrawn by hand as a right-facing animation extreme before any in-betweens are attempted",
        "first_reading": "the placeholder eye is approved without shifting the fixed-width rails",
        "principle": "a mirrored animation extreme is a newly authored still: exchange directional glyphs and spacing by eye instead of reversing stored bytes",
        "defect": "the actor moves across the frame but its arrowhead, slash direction, or distance from the rails does not mirror",
        "basic": "use gR to overwrite a nominated cell or complete fixed-width row without insertion",
        "scaled": "copy the complete five-row key pose, then hand-author every directional row of its mirrored extreme",
        "steps": [
            step(
                ["|   /^\\   |", "| _/ ? \\  |", "|<--/|\\   |", "|   / \\   |", "|  /___\\  |"],
                ["|   /^\\   |", "| _/ o \\  |", "|<--/|\\   |", "|   / \\   |", "|  /___\\  |"],
                "2G0f?gRo<Esc>",
                [["2G0f?", "land on the visible eye placeholder"],
                 ["gRo<Esc>", "Virtual Replace the one eye cell and return to Normal mode"]],
                method_requirement=require_method(
                    "replace the nominated still cell with virtual replace",
                    exact_any_of=["2G0f?gRo<Esc>"]),
            ),
            step(
                ["|   /^\\   |", "| _/ o \\  |", "|<--/|\\   |", "|   / \\   |", "|  /___\\  |"],
                ["|   /^\\   |", "| _/ o \\  |", "|<--/|\\   |", "|   / \\   |", "|  /___\\  |",
                 "|   /^\\   |", "| _/ o \\  |", "|<--/|\\   |", "|   / \\   |", "|  /___\\  |"],
                "gg5yyGp",
                [["gg5yy", "copy the complete approved five-row still"],
                 ["Gp", "append one working extreme below it"]],
            ),
            step(
                ["|   /^\\   |", "| _/ o \\  |", "|<--/|\\   |", "|   / \\   |", "|  /___\\  |",
                 "|   /^\\   |", "| _/ o \\  |", "|<--/|\\   |", "|   / \\   |", "|  /___\\  |"],
                ["|   /^\\   |", "| _/ o \\  |", "|<--/|\\   |", "|   / \\   |", "|  /___\\  |",
                 "|   /^\\   |", "|  / o \\_ |", "|   /|\\-->|", "|   / \\   |", "|  /___\\  |"],
                "6G0gR|   /^\\   |<Esc>j0gR|  / o \\_ |<Esc>j0gR|   /|\\-->|<Esc>j0gR|   / \\   |<Esc>j0gR|  /___\\  |<Esc>",
                [["6G0gR…<Esc>", "redraw the copied head row without changing its width"],
                 ["j0gR…<Esc> ×4", "hand-author the remaining mirrored rows, including slash direction, arrowhead, and spacing"]],
                method_requirement=require_method(
                    "hand-author all five copied mirror rows with virtual replace",
                    exact_any_of=["6G0gR|   /^\\   |<Esc>j0gR|  / o \\_ |<Esc>j0gR|   /|\\-->|<Esc>j0gR|   / \\   |<Esc>j0gR|  /___\\  |<Esc>"]),
            ),
            step(
                ["|   /^\\   |", "| _/ o \\  |", "|<--/|\\   |", "|   / \\   |", "|  /___\\  |",
                 "|   /^\\   |", "|  / o \\_ |", "|   /|\\-->|", "|   / \\   |", "|  /___\\  |"],
                ["|   /^\\   |", "| _/ o \\  |", "|<--/|\\   |", "|   / \\   |", "|  /___\\  |",
                 "|   /^\\   |", "|  / o \\_ |", "|   /|\\==>|", "|   / \\   |", "|  /___\\  |"],
                "8G0f-gR==<Esc>",
                [["8G0f-", "find the mirrored arrow material by its visible dash"],
                 ["gR==<Esc>", "overwrite the two-cell material run without moving its arrowhead"]],
                alternatives=[
                    method("virtual replace run", "8G0f-gR==<Esc>", "replace exactly two display cells while keeping the row width"),
                    method("replace-mode run", "8G0f-R==<Esc>", "replace the same two existing cells, then stop before the arrowhead"),
                ],
            ),
            step(
                ["|   /^\\   |", "| _/ o \\  |", "|<--/|\\   |", "|   / \\   |", "|  /___\\  |",
                 "|   /^\\   |", "|  / o \\_ |", "|   /|\\==>|", "|   / \\   |", "|  /___\\  |"],
                ["|   /^\\   |", "| _/ o \\  |", "|<--/|\\   |", "|   / \\   |", "|  /___\\  |",
                 "|   /^\\   |", "|  / o \\_ |", "|   /|\\==>|", "|   / \\   |", "|  /___\\  |",
                 "|   /^\\   |", "| _/ O \\  |", "|<--/|\\   |", "|   / \\   |", "|  /___\\  |"],
                ":1,5t$<CR>12G0forO",
                [[":1,5t$", "retain the approved original as a third animation key-pose candidate"],
                 ["12G0forO", "change only its eye so the variant remains a distinct authored still"]],
                method_requirement=require_method(
                    "retain the complete key-pose still and vary one nominated cell",
                    exact_any_of=[":1,5t$<CR>12G0forO"]),
            ),
        ],
        "transfer": step(
            ["|   /+\\   |", "| __/x\\   |", "|<==/|\\   |", "|   / \\   |", "|__/___\\__|"],
            ["|   /+\\   |", "|   /x\\__ |", "|   /|\\==>|", "|   / \\   |", "|__/___\\__|"],
            "0gR|   /+\\   |<Esc>j0gR|   /x\\__ |<Esc>j0gR|   /|\\==>|<Esc>",
            [["gR on three directional rows", "hand-author the unfamiliar mirrored key pose while preserving both fixed rails"]],
            method_requirement=require_method(
                "transfer hand mirroring with virtual replace to unfamiliar art",
                exact_any_of=["0gR|   /+\\   |<Esc>j0gR|   /x\\__ |<Esc>j0gR|   /|\\==>|<Esc>"]),
        ),
        "transfer_alt": step(
            ["|   /o\\   |", "| _/!\\    |", "|<--/|\\   |", "|   / \\   |", "|__/___\\__|"],
            ["|   /o\\   |", "|    /!\\_ |", "|   /|\\-->|", "|   / \\   |", "|__/___\\__|"],
            "0gR|   /o\\   |<Esc>j0gR|    /!\\_ |<Esc>j0gR|   /|\\-->|<Esc>",
            [["gR on three directional rows", "hand-author the alternate mirror without reversing bytes"]],
            method_requirement=require_method(
                "transfer hand mirroring with virtual replace to alternate art",
                exact_any_of=["0gR|   /o\\   |<Esc>j0gR|    /!\\_ |<Esc>j0gR|   /|\\-->|<Esc>"]),
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

PREREQUISITES = {module["id"]: [] for module in MODULES}

# Modules are storage/project units.  Stages are the learner's actual gated
# journey.  Keeping those concepts separate lets the S0 command primer live in
# M0 without forcing the Spark animation project to precede the still course.
MODULE_SEQUENCE = [
    "M0", "M11", "M1", "M19", "M2", "M12", "M14", "M10", "M5",
    "M15", "M16", "M3", "M4", "M17", "M13", "M7", "M6", "M18",
    "M8", "M9",
]

MAIN_STAGE_SEQUENCE = [
    *(f"S{number}" for number in range(8)),
    *(f"A{number}" for number in range(8)),
]

STAGE_TITLES = {
    "S0": "Grid and overwrite", "S1": "Stroke runs", "S2": "Hand mirroring",
    "S3": "Block a still", "S4": "Joint heights", "S5": "Variants and palette",
    "S6": "Layers and seams", "S7": "Texture and ground",
    "A0": "Plan and key poses", "A1": "Extremes and copy-vary",
    "A2": "In-betweens and onion skin", "A3": "Coherent anchors",
    "A4": "Timing and holds", "A5": "Subtractive build",
    "A6": "Mirrored return", "A7": "Playback polish",
    "P": "Proportional Shift_JIS branch",
}

PRIMARY_STAGE_BY_MODULE = {
    "M11": "S0", "M1": "S1", "M19": "S2", "M2": "S3",
    "M12": "S4", "M14": "S5", "M5": "S6", "M15": "S7",
    "M16": "A0", "M0": "A1", "M3": "A2", "M4": "A2",
    "M17": "A3", "M13": "A4", "M7": "A4", "M6": "A5",
    "M18": "A6", "M8": "A7", "M9": "A7", "M10": "P",
}

# These are still-authoring command labs, not playback lessons.  They teach
# the grammar later stages rely on using one still or a non-playing working
# copy; the remaining M0 cards own A1 and form the first animation strip.
STAGE_OWNER_OVERRIDES = {
    card_id: "S0" for card_id in (
        "M0.P0", "M0.01", "M0.YP", "M0.O", "M0.SR", "M0.T", "M0.SL",
    )
}
STAGE_OWNER_OVERRIDES.update({
    # These cards author, diagnose, or validate temporal change.  They cannot
    # supply evidence for the still-only S stages even though their parent
    # modules also contain still-authoring foundations.
    "M11.08": "A3",
    "M5.04": "A3", "M5.07": "A3",
    "M12.02": "A4", "M12.03": "A4", "M12.04": "A4",
    "M12.05": "A4", "M12.07": "A4", "M12.08": "A4",
    "M15.08": "A4",
})

ARTIFACT_MODE_BY_STAGE = {
    **{f"S{number}": "still-study" for number in range(8)},
    **{f"A{number}": "animation-strip" for number in range(8)},
    "P": "optional-proportional",
}

# These are individually written dispositions, not a prose template.  Their
# source cards remain useful still-authoring work, but their old wording falsely
# described candidates, paragraphs, or working copies as playback artifacts.
STILL_PROMPT_REWRITES = {
    "M0.SL": "On one changed still, replace every small core on the current line with one line-scoped substitute; leave the two contour rows alone.",
    "M11.02": "Copy the complete three-row machine as a second redraw candidate.",
    "M11.WS": "Inspect the padded missile still with visible whitespace and column guides, then remove only trailing spaces. Every visible missile and exhaust glyph must remain unchanged.",
    "M11.UT": "Try ! as an exaggerated left-eye take, undo it, author the chosen O look, visit the abandoned ! take with chronological history, then return to and submit the O-eye still.",
    "M11.WSH": "On the unfamiliar Chick still, turn on the whitespace and column guides, then remove only the three invisible tail spaces from each row. Preserve every visible drawing cell.",
    "M11.UTH": "On the unfamiliar SnowBunny still, try ! as an exaggerated left-eye take, undo and author the chosen dash, inspect the abandoned take chronologically, then return to the half-closed eye for submission.",
    "M11.07": "Diagnose the displayed fixed-width redraw, then choose the bounded repair that preserves every registered cell outside the named change.",
    "M1.02": "Copy the complete anchored contour as a second still candidate.",
    "M1.DD": "Remove only the second redundant three-row contour candidate; keep the first candidate registered.",
    "M1.04": "Replace the copied still with a hand-authored descending counterpart instead of software-flipping the glyphs.",
    "M1.07": "Diagnose the displayed contour run, then choose the bounded repair that preserves its line quality, anchor, and declared material.",
    "M19.01": "Approve one uncertain eye cell with `gR`, preserving both fixed-width rails of the five-row still.",
    "M19.02": "Copy the complete five-row still as the working opposite-facing candidate.",
    "M19.03": "Inspect the complete hand-mirrored still below, then choose the interpretation supported by its visible glyph and spacing evidence.",
    "M19.06": "Transfer full-row Virtual Replace mirroring to unfamiliar fixed-rail still art with the exact keys hidden.",
    "M19.07": "Diagnose the displayed hand-mirrored still, then choose the repair that preserves fixed rails and directional glyph roles.",
    "M19.08": "Answer five checks, then perform this key-hidden artifact task: retain the approved still as a third candidate and vary one eye without treating the plate as an ordered sequence. The target stays visible; the exact command path stays hidden until evaluation.",
    "M2.07": "Diagnose the displayed face study, then choose the bounded repair that preserves silhouette, focus, and fixed width.",
    "M2.08": "Answer five checks, then perform this key-hidden artifact task: copy the complete face as a second expression candidate and close only its eye. The target stays visible; the exact command path stays hidden until evaluation.",
    "M12.AA": "On this single four-row stroke study, replace the hard vertical bars with the shown off-vertical anti-aliasing glyphs: apostrophe, dot, exclamation, then inverted exclamation. The four rows form one drawing.",
    "M14.01": "Yank a visible glyph from the drawing's palette into register `a`, then retrieve it with `<C-r>a` in Replace mode so the acting eye changes without shifting the wall.",
    "M14.DAP": "The first Skully candidate is an accidental duplicate before the closed-eye candidate. Delete that complete still and its separator as one paragraph object.",
    "M14.04": "On the copied candidate, store the second palette glyph and replace only its eye through the named register.",
    "M14.PARA": "Yank the first blank-line-separated still, cross the paragraph boundary with }, and put the stored still above the next candidate.",
    "M14.DAPH": "On the unfamiliar SnowBunny plate, remove the complete open-eyed paragraph so the closed-eye still remains registered.",
    "M14.07": "Diagnose the displayed variant plate, then choose the repair that preserves palette and material consistency.",
    "M14.08": "Answer five checks, then perform this key-hidden artifact task: store the first eye material, navigate across two paragraph-separated candidates with `}`, and retrieve the register in the third candidate so it reuses the first material. The target stays visible; the exact command path stays hidden until evaluation.",
    "M15.02": "Copy the complete three-row material stack as the working still for a lighter offset treatment.",
    "M15.ZPH": "On the unfamiliar Chick still, copy the ragged three-row drawing from its padded palette into the `>` destination rows without carrying invisible right-edge padding.",
    "M15.07": "Diagnose the displayed texture-and-ground study, then choose the repair that preserves dither density, offset, and shadow rules.",
}

# Variant-accurate transfer questioning.  Every transfer card's second
# changed-art variant owns its own manually authored question; runtime
# card.update(variant) selects that question before the editor.
ALT_VARIANT_QUESTION_CARDS = {
    "M0.06", "M1.06", "M2.06", "M3.06", "M4.06", "M5.06",
    "M6.06", "M7.06", "M8.06", "M9.06", "M10.06", "M11.06",
    "M12.06", "M13.06", "M14.06", "M15.06", "M16.06", "M17.06",
    "M18.06", "M19.06",
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
    "M19": [
        "the eye is inserted, shifting the right rail one display cell",
        "the placeholder remains unchanged, so this is not yet an approved key-pose still",
        "the whole row is redrawn even though only the nominated eye cell was uncertain",
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
    "M19": "three approved still variants preserve fixed rails while directional spacing, slash roles, and arrowheads are authored deliberately",
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
    "M19": [
        ("Which visible change approves the eye without moving either fixed rail?", "How does `gR` differ from inserting a new glyph at the placeholder?"),
        ("Why copy all five rows before authoring the opposite-facing key pose?", "Which count makes `yy` own the complete still rather than one row?"),
        ("The body moved right but the arrow still points left. What mirror defect remains?", "Which overwrite mode forces the author to choose every directional glyph in place?"),
        ("Which rows must change when the copied pose becomes its hand-authored mirror?", "Why must the row width remain unchanged through each `gR` pass?"),
        ("When do `R` and `gR` legitimately produce the same two-cell material result?", "What explicit stopping point protects the arrowhead after the two-cell run?"),
        ("The transfer uses a different eye and arrow material. What still defines a valid mirror?", "Which three-row `gR` path proves the unfamiliar directional rows were authored rather than flipped?"),
        ("Read the original, mirror, and changed-eye variant as a key-pose plate. What is not animation yet?", "Which complete-frame operation keeps each candidate available for comparison?"),
        ("Why is the third still a variant rather than an accidental duplicate?", "Which local replacement makes it observably distinct while preserving its five-row bounds?"),
        ("A byte-reversed row puts the arrow on the other side but corrupts `/` and `\\`. What principle failed?", "Which command family overwrites chosen display cells without reversing stored bytes?"),
        ("One mirrored row is a cell shorter than the original. Why can it not become an animation extreme?", "Which invariant must be checked after every full-row virtual replacement?"),
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
        ("secondary arm motion may lag the primary foot contact to avoid every part arriving together", "o creates each bounded new row; the art buffer disables automatic indentation, so each row starts at column one"),
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
        ("a one-column trail mismatch reads as secondary-motion jitter between otherwise registered frames", "2G13|i|<Esc>3j13|i|<Esc> addresses column 14 explicitly in both homologous rows"),
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
    "M19": [
        ("the eye changes from ? to o while both fixed rails remain in their original columns", "gR overwrites the existing display cell; insertion would grow the row and shift its right rail"),
        ("the full body, rails, slash limbs, and arrow belong to one approved still", "5yy is the complete-frame yank; yy alone copies only the head row"),
        ("relocation without exchanging the arrowhead and slash semantics is not a hand mirror", "gR makes each replacement explicit while keeping the fixed row width"),
        ("the copied directional torso and arrow rows change while stable head, legs, and base remain registered", "each gR pass overwrites existing display cells and must end at the unchanged right rail"),
        ("both modes may replace the same bounded two-cell run when neither crosses into the arrowhead", "Escape immediately after the second replacement cell protects the following > glyph"),
        ("fixed rails and body height persist while the new eye, slashes, arrowhead, and spacing exchange direction", "the exact gR path redraws each unfamiliar directional row and contains no reverse operation"),
        ("the plate contains candidate stills; no timing, in-betweens, or playback spacing has been authored yet", "a five-row yank or addressed copy retains each complete candidate for comparison"),
        ("the changed eye makes a deliberate material variant while every other registered cell stays fixed", "the addressed rO replacement changes one visible cell inside the copied five-row object"),
        ("visual mirroring requires semantic glyph exchange, not byte-order reversal", "gR or R overwrites the author-chosen display cells without transforming the stored row"),
        ("unequal widths move the rail and prevent frame registration during later playback", "after each gR row, verify equal display width and matching left/right rail columns"),
    ],
}


def visual_pair(before, after):
    """Render a concept stimulus as art, never as a flattened slash summary."""
    width = max([len(row) for row in before + after] or [1])
    lines = ["    " + "BEFORE".ljust(width + 2) + "   AFTER"]
    for index in range(max(len(before), len(after))):
        left = before[index] if index < len(before) else ""
        right = after[index] if index < len(after) else ""
        lines.append(f"    │{left.ljust(width)}│   │{right.ljust(width)}│")
    return "\n".join(lines)


def visual_delta(before, after, max_rows=5):
    """Render the rows that materially distinguish BEFORE from AFTER.

    Small terminals still need real art evidence, but printing an entire strip
    can push the choices off a 24-row popup.  Keep changed rows and one row of
    context on either side, then mark omissions explicitly.
    """
    row_count = max(len(before), len(after))
    changed = [
        index for index in range(row_count)
        if (before[index] if index < len(before) else "")
        != (after[index] if index < len(after) else "")
    ]
    if not changed:
        changed = list(range(min(row_count, max_rows)))
    selected = set(changed)
    if len(selected) < max_rows:
        for index in list(changed):
            for neighbor in (index - 1, index + 1):
                if 0 <= neighbor < row_count and len(selected) < max_rows:
                    selected.add(neighbor)
    indices = sorted(selected)
    if len(indices) > max_rows:
        indices = indices[:max_rows]
    width = max([
        len(before[index]) if index < len(before) else 0
        for index in indices
    ] + [
        len(after[index]) if index < len(after) else 0
        for index in indices
    ] + [1])
    lines = ["    " + "BEFORE".ljust(width + 2) + "   AFTER"]
    previous = None
    for index in indices:
        if previous is not None and index != previous + 1:
            lines.append("    " + "…".ljust(width + 2) + "   …")
        left = before[index] if index < len(before) else ""
        right = after[index] if index < len(after) else ""
        lines.append(f" {index + 1:>2} │{left.ljust(width)}│   │{right.ljust(width)}│")
        previous = index
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
    }.get(number, comparison if number <= 6 else sequence)
    compact_visual = {
        6: visual_delta(module["transfer"]["start"], module["transfer"]["target"]),
    }.get(number, visual_delta(first["start"], first["target"]))
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
    compact_prompt = (
        "ANIMATION: read the complete frames; choose the supported motion."
        f"\n\n{compact_visual}\n\nNEOVIM: "
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
    "lowercase-word-motion": {
        "class": "standalone_normal",
        "grammar": "w moves to the next lowercase word/punctuation run; a count repeats that exact boundary motion",
        "terms": [["lowercase w", "w"], ["next", "boundary"], ["count", "repeat"], ["word", "punctuation", "run"]],
    },
    "last-nonblank": {
        "class": "standalone_normal",
        "grammar": "g_ lands on the last nonblank glyph while ignoring trailing alignment spaces",
        "terms": [["g_", "last nonblank"], ["trailing", "spaces"], ["glyph", "cell"]],
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
    "block-insert": {
        "class": "visual",
        "grammar": "Ctrl-v selects a column block; I inserts the same prefix at the start of every selected row; <Esc> applies it",
        "terms": [["ctrl-v", "block"], ["I", "insert"], ["each row", "column"], ["escape", "apply"]],
    },
    "block-change": {
        "class": "visual",
        "grammar": "Ctrl-v selects registered cells; c replaces that block on every row; <Esc> applies the typed replacement",
        "terms": [["ctrl-v", "block"], ["c", "change"], ["each row", "registered"], ["escape", "apply"]],
    },
    "visual-reselect": {
        "class": "visual",
        "grammar": "gv restores the previous Visual selection so the same registered cells can be refined without rebuilding the scope",
        "terms": [["gv", "reselect"], ["previous", "selection"], ["same", "cells", "scope"]],
    },
    "trimmed-block-copy": {
        "class": "visual",
        "grammar": "Visual Block zy yanks each selected row without its trailing spaces; zp pastes the block without manufacturing a padded rectangle",
        "terms": [["zy", "yank"], ["trailing", "spaces", "padding"], ["zp", "paste", "put"], ["block", "ragged"]],
    },
    "whitespace-column-audit": {
        "class": "ex",
        "grammar": ":set list reveals whitespace, cursorcolumn tracks the active registration column, colorcolumn marks the width boundary, and :%s/\\s\\+$//e removes only trailing whitespace",
        "terms": [["list", "whitespace"], ["cursorcolumn", "active column"], ["colorcolumn", "boundary"], ["substitute", "trailing", "cleanup"]],
    },
    "onion-diff-view": {
        "class": "window",
        "grammar": "a disposable vertical reference window holds the prior frame; :diffthis and scrollbind align both views; the reference closes after the changed cells are checked",
        "terms": [["vnew", "reference", "window"], ["diffthis", "compare"], ["scrollbind", "align"], ["close", "disposable"]],
    },
    "undo-tree-travel": {
        "class": "history",
        "grammar": "u returns before a change so a second variant creates a branch; g-/g+ travel changes chronologically; :earlier 1 revisits the previous authored state",
        "terms": [["u", "undo", "branch"], ["g-", "older"], ["g+", "newer"], ["earlier", "history", "state"]],
    },
    "glyph-inspect": {
        "class": "standalone_normal",
        "grammar": "ga reports the glyph under the cursor before a deliberate fixed-cell replacement",
        "terms": [["ga", "inspect"], ["glyph", "codepoint", "value"], ["cursor", "cell"]],
    },
    "paragraph-delete": {
        "class": "operator",
        "grammar": "d is the delete operator and ap is the complete paragraph object, including its blank-line frame separator",
        "terms": [["delete", "d"], ["paragraph", "ap"], ["blank", "separator"], ["frame", "object"]],
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
    "virtual-replace": {
        "class": "standalone_normal",
        "grammar": "gR enters Virtual Replace; typed glyphs overwrite display cells until <Esc>",
        "terms": [["virtual replace", "gR"], ["display cell", "overwrite"], ["escape", "normal"], ["width", "rail", "registered"]],
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
    "M19.05": {
        "question": "When do R and gR produce the same two-cell arrow-material change, and which boundary must both preserve?",
        "groups": [["R", "replace"], ["gR", "virtual replace"], ["two", "2", "cells"], ["arrowhead", "boundary", "width"]],
        "sample": "R and gR both overwrite the two selected material cells; Escape after cell two preserves the arrowhead and fixed row width.",
    },
}


MASTER_COVERAGE = {
    "M0": (["H1", "H3"], ["A1"]),
    "M1": (["H2"], ["S1"]),
    "M2": (["H1", "H2"], ["S3"]),
    "M3": (["H3"], ["A2"]),
    "M4": (["H2", "H4", "H7"], ["A2"]),
    "M5": (["H3", "H4", "H7"], ["S6"]),
    "M6": (["H3", "H9"], ["A5"]),
    "M7": (["H5"], ["A4"]),
    "M8": (["H2", "H8"], ["A7"]),
    "M9": (["H1", "H3", "H9"], ["A7"]),
    "M10": (["H2"], ["P"]),
    "M11": (["H1", "H4", "H5"], ["S0"]),
    "M12": (["H2", "H5"], ["S4"]),
    "M13": (["H2", "H5"], ["A4"]),
    "M14": (["H3", "H6", "H9"], ["S5"]),
    "M15": (["H4", "H8"], ["S7"]),
    "M16": (["H3", "H9"], ["A0"]),
    "M17": (["H2", "H5"], ["A3"]),
    "M18": (["H1", "H3", "H9"], ["A6"]),
    "M19": (["H1", "H2", "H3"], ["S2"]),
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
    if re.search(r":[^<]*(?:s|substitute)[/@][^<]*\\=", keys):
        add("expression-substitute")
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
    if re.search(r'"[a-z0-9]', keys) or re.search(r"<C-r>[A-Za-z0-9]", keys):
        add("register")
    if "u<C-r>" in keys: add("undo-redo")
    if "<C-k>" in keys: add("digraph")
    if "virtualedit" in keys or re.search(r"\d+\|", plain_normal): add("virtual-column")
    if re.search(r"[WBE]", plain_normal): add("word-boundary")
    if "gR" in plain_normal: add("virtual-replace")
    if re.search(r"(?<!g)R", plain_normal): add("replace-mode")
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


def _multiple_choice_pair(question, card, module):
    """Turn every card-owned check into an explicit four-choice pair.

    The earlier free-text contracts rejected reasonable paraphrases and made
    the answer format guesswork.  We retain the pedagogical intent as
    ``learning_form`` metadata, but the learner always sees four paired
    animation/Neovim choices with mistake-specific feedback.
    """
    old_form = question["form"]
    if old_form == "multiple_choice":
        return question

    original_contract = question.get("answer_contract", {})
    if old_form in ("predict_art",) and question.get("choices"):
        action = "; ".join(
            f"{keys}: {why}" for keys, why in card.get("recipe", []))
        neovim_correct = f"`{card['expected']}` performs the bounded edit: {action}"
        neovim_wrong = (
            "use insertion or deletion even if it shifts registered cells to the right"
        )
    elif old_form == "typed_keys":
        neovim_correct = (
            f"`{card['expected']}` is one bounded path whose effect matches TARGET exactly"
        )
        neovim_wrong = (
            f"for {card['id']}, navigation alone is equivalent to `{card['expected']}` "
            "because the final art is not graded"
        )
        # Showing a concrete valid sequence before a key-hidden transfer would
        # reveal the answer.  Ask the choice check after the learner performs
        # the edit instead.
        question["placement"] = "after"
        question["placement_reason"] = (
            "The key-hidden transfer comes first; afterward, four explicit choices "
            "check the command path and animation scope without free-text grading."
        )
    elif old_form == "decode":
        breakdown = "; ".join(question.get("grammar_breakdown", []))
        shown = original_contract.get("display", card.get("expected", "the shown command"))
        neovim_correct = f"`{shown}` follows this grammar: {breakdown}"
        neovim_wrong = (
            f"`{shown}` is an indivisible shortcut, so its count, action, motion, "
            "and scope do not need decoding"
        )
    elif old_form == "why":
        neovim_correct = original_contract.get(
            "sample_answer", "the bounded method preserves the named animation scope")
        neovim_wrong = (
            f"cursor position and range scope cannot affect {card['title']}; "
            "either demonstrated method is always safe"
        )
    else:
        neovim_correct = "the missing grammar part is `%s`" % original_contract.get(
            "sample_answer", "the stated motion or object")
        neovim_wrong = (
            f"the missing grammar part for {card['id']} is an unrelated "
            "project-wide command"
        )

    animation_correct = card["prompt"].rstrip(".")
    animation_wrong = "This visible failure occurs: %s" % module["defect"].rstrip(".")
    art_visual = visual_pair(card.get("start", []), card.get("target", []))
    compact_art_visual = visual_delta(card.get("start", []), card.get("target", []))

    def paired(animation, neovim):
        return f"ANIMATION: {animation} | NEOVIM: {neovim}"

    records = [
        (animation_correct, neovim_correct, None),
        (animation_correct, neovim_wrong,
         f"The animation reading is right for {card['id']}, but the Neovim half ignores the bounded command path. {neovim_correct}."),
        (animation_wrong, neovim_correct,
         f"The Neovim reading is right for {card['id']}, but shifted or project-wide art breaks this card's registration contract."),
        (animation_wrong, neovim_wrong,
         f"Both halves break {card['id']}: preserve the named animation scope and use the bounded Neovim reading. {neovim_correct}."),
    ]
    # Do not let a stable answer position become a second grading shortcut.
    shift = sum(ord(char) for char in question["id"]) % 4
    records = records[shift:] + records[:shift]
    choices = [paired(animation, neovim) for animation, neovim, _ in records]
    correct_choice = next(index for index, record in enumerate(records) if record[2] is None)
    feedback = [
        (f"Correct for {card['id']}: {animation_correct}; {neovim_correct}."
         if error is None else error)
        for _animation, _neovim, error in records
    ]
    compact_choices = [
        "A: %s · V: %s" % (
            textwrap.shorten(animation, width=29, placeholder="…"),
            textwrap.shorten(neovim, width=29, placeholder="…"),
        )
        for animation, neovim, _ in records
    ]
    old_neovim_prompt = question["prompt"].split("\n\nNEOVIM\n", 1)[-1]
    neovim_prompt = {
        "typed_keys": (
            "After the hidden edit, which option identifies one bounded command path "
            "that reaches TARGET exactly?"
        ),
        "decode": (
            "Which explanation correctly decomposes the command you just used and "
            "keeps its animation scope bounded?"
        ),
        "why": (
            "Which explanation correctly compares the demonstrated methods and their "
            "animation-registration risk?"
        ),
        "complete": (
            "Which option correctly completes the reusable Vim grammar?"
        ),
    }.get(old_form, old_neovim_prompt)
    question.update({
        "form": "multiple_choice",
        "learning_form": old_form,
        "prompt": (
            f"ANIMATION\n{card['prompt']}\n\n{art_visual}\n\n"
            f"NEOVIM\n{neovim_prompt}\n\n"
            "Choose the option whose ANIMATION and NEOVIM halves are BOTH correct."
        ),
        "choices": choices,
        "correct_choice": correct_choice,
        "feedback": feedback,
        "animation_prompt": f"{card['prompt']}\n\n{art_visual}",
        "animation_answer": animation_correct,
        "neovim_prompt": neovim_prompt,
        "neovim_answer": neovim_correct,
        "compact_prompt": (
            "ANIMATION: %s\n\n%s\n\nNEOVIM: %s\n"
            "Choose the option whose A and V halves are BOTH correct."
            % (textwrap.shorten(card["prompt"], width=64, placeholder="…"),
               compact_art_visual,
               textwrap.shorten(neovim_prompt, width=64, placeholder="…"))
        ),
        "compact_choices": compact_choices,
        "source_answer_contract": original_contract,
        "answer_contract": {"form": "multiple_choice", "answer_mode": "choice"},
    })
    return question


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
    return _multiple_choice_pair(common, card, module)


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
    yank_put = dict(base, **{
        "id": "M0.YP", "ordinal": 1.5, "kind": "guided_edit",
        "title": "Spark loop · Copy one complete frame with yy/p",
        "project_id": "m0-yank-put-lab", "artifact": "transfer",
        "variant_group": "M0.yank-put", "lesson_benefit": (
            "copy a complete fixed-width frame without retyping any of its rows"
        ),
        "prompt": (
            "Copy the complete three-row spark once below itself. Do not redraw the rays "
            "character by character."
        ),
        "start": ["  \\|/", "-- o --", "  /|\\"],
        "target": ["  \\|/", "-- o --", "  /|\\",
                   "  \\|/", "-- o --", "  /|\\"],
        "expected": "gg3yyGp",
        "recipe": [["gg", "go to the first row"],
                   ["3yy", "copy three whole rows into Vim's yank register"],
                   ["G", "go to the last existing row"],
                   ["p", "put the copied whole rows below it"]],
        "cursor": "^", "show_target": True, "show_recipe": True,
        "hint": (
            "Vim's copy sentence is [count]yy; a linewise p creates new rows below, so "
            "you do not need Insert mode or literal retyping."
        ),
        "frame_slices": [3, 3],
        "grammar_families": ["linewise-yank-put", "normal-motion"],
        "grammar_stage": "guided",
        "duplicate_frames": [{
            "frames": [1, 2], "role": "scaffold",
            "reason": "an exact whole-frame copy used to learn linewise yank and put",
            "playback": False,
        }],
    })
    open_line = dict(base, **{
        "id": "M0.O", "ordinal": 1.75, "kind": "guided_edit",
        "title": "Spark loop · Open one missing row",
        "project_id": "m0-open-line-lab", "artifact": "transfer",
        "variant_group": "M0.open-line", "lesson_benefit": (
            "open one registered row below the cursor and return to Normal mode"
        ),
        "prompt": (
            "Finish the second spark by adding only its missing lower-ray row. The first five "
            "rows are already correct; do not retype them."
        ),
        "start": ["  \\|/", "-- o --", "  /|\\", "  \\|/", "-- O --"],
        "target": ["  \\|/", "-- o --", "  /|\\", "  \\|/", "-- O --", "  /|\\"],
        "expected": "Go  /|\\<Esc>",
        "recipe": [["G", "go to the last existing row"],
                   ["o", "open one new row below and enter Insert mode"],
                   ["  /|\\", "type the missing registered lower-ray row exactly"],
                   ["<Esc>", "leave Insert mode and return to Normal"]],
        "cursor": "^", "show_target": True, "show_recipe": True,
        "hint": (
            "Use G to reach the last supplied row, then o once. The art buffer disables "
            "automatic indentation, so type the two leading spaces shown in TARGET yourself."
        ),
        "frame_slices": [3, 3], "grammar_families": ["normal-open-line"],
        "grammar_stage": "guided",
        "accepted_legacy_starts": [["  \\|/", "-- o --", "  /|\\"]],
        "incomplete_start_frame": {
            "frame": 2, "missing_rows": 1,
            "reason": "the single learner action is to open the missing lower-ray row",
        },
    })
    addressed_substitute = dict(base, **{
        "id": "M0.SR", "ordinal": 1.9, "kind": "guided_edit",
        "title": "Spark loop · Address one row and substitute",
        "project_id": "m0-addressed-substitute-lab", "artifact": "transfer",
        "variant_group": "M0.addressed-substitute", "lesson_benefit": (
            "read an Ex substitute as address + command + old/new arguments + flag + Enter"
        ),
        "prompt": (
            "On row 2 only, replace every small core o with O. Keep both ray rows unchanged."
        ),
        "start": ["  \\|/", "-- o --", "  /|\\"],
        "target": ["  \\|/", "-- O --", "  /|\\"],
        "expected": ":2s/o/O/g<CR>",
        "recipe": [[":2", "address row 2 only"],
                   ["s", "start the substitute command"],
                   ["/o/O/", "name the old glyph and its replacement"],
                   ["g", "replace every match on that addressed row"],
                   ["<CR>", "execute the complete Ex statement"]],
        "cursor": "^", "show_target": True, "show_recipe": True,
        "hint": (
            "Read :2s/o/O/g as address + command + old/new arguments + all-matches flag; "
            "press Enter only after the full sentence is assembled."
        ),
        "frame_slices": [3], "grammar_families": ["ex-substitute-range"],
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
    for card in (primer, yank_put, open_line, addressed_substitute, ex_copy):
        card["roadmap_contract"] = card["prompt"]
        card.setdefault("key_vocabulary", _family_breakdown(card["grammar_families"]))
    return primer, yank_put, open_line, addressed_substitute, ex_copy


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
    elif mid == "M5":
        change_tail = bridge(
            "C", "Redraw one layer tail without moving its seam",
            "On the middle layer only, change the two dotted tail cells to dashes and retype its closing rail. Preserve the cloud and ground rows byte-for-byte.",
            ["| .:::. |", "| /___..|", "|_/_____|"],
            ["| .:::. |", "| /___--|", "|_/_____|"],
            "2G0f.C--|<Esc>",
            [["2G0f.", "land on the first cell of the layer tail"],
             ["C", "change from that cell through the row end"],
             ["--|<Esc>", "redraw the two tail cells and the closing rail at the same width"]],
            "change-to-end", 3.5,
        )
        # M5.04/M5.05 are the hidden changed-art retrieval for this family;
        # do not create synthetic border-swap reviews for the guided lab.
        change_tail.pop("review_variants", None)
        change_tail.pop("review_source_card_id", None)
        change_tail.pop("review_method_family", None)
        rows.append(("M5.04", change_tail))
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
        aa = bridge(
            "AA", "Shape one off-vertical stroke with the full glyph palette",
            "On this single four-row stroke study, replace the hard vertical bars with the shown off-vertical anti-aliasing glyphs: apostrophe, dot, exclamation, then inverted exclamation. This is one still study, not four animation frames.",
            ["|    | |", "|   |  |", "|  |   |", "| |    |"],
            ["|    ' |", "|   .  |", "|  !   |", "| ¡    |"],
            "gg6|r'j5|r.j4|r!j3|r<C-k>!I",
            [["gg6|r'", "replace the top sample with the high apostrophe"],
             ["j5|r.", "replace the next sample with the low dot"],
             ["j4|r!", "replace the next sample with exclamation"],
             ["j3|r<C-k>!I", "enter inverted exclamation by its !I digraph"]],
            "digraph", 0.7,
        )
        aa.pop("review_variants", None)
        aa.pop("review_source_card_id", None)
        aa.pop("review_method_family", None)

        joint_height = bridge(
            "JH", "Centre three joints without moving their strokes",
            "In this non-playing three-sample still sheet, each dot sits too low between its two strokes. Replace the aligned joint column with colons, whose marks occupy the middle of the cell; keep every slash, bracket, and row width fixed.",
            ["|/ .\\|", "|< .>|", "|\\ ./|"],
            ["|/ :\\|", "|< :>|", "|\\ :/|"],
            "gg4|<C-v>2jr:",
            [["gg4|", "address display column 4 on the first sample"],
             ["<C-v>2j", "select the same registered joint cell on all three rows"],
             ["r:", "replace the selected low dots with centred colons"]],
            "visual-scope", 0.8,
        )
        joint_height["grammar_families"].append("block-change")
        joint_height["key_vocabulary"] = _family_breakdown(joint_height["grammar_families"])
        joint_height.pop("review_variants", None)
        joint_height.pop("review_source_card_id", None)
        joint_height.pop("review_method_family", None)

        reselect = bridge(
            "GV", "Try a high joint, then refine the same selection",
            "On a second non-playing joint sheet, first try apostrophes in the aligned joint column. Then use gv to restore that exact block and refine all three joints to centred colons without rebuilding the selection.",
            ["|< .>|", "|[ .]|", "|{ .}|"],
            ["|< :>|", "|[ :]|", "|{ :}|"],
            "gg4|<C-v>2jr'gvr:",
            [["gg4|<C-v>2j", "select the three aligned joint cells"],
             ["r'", "try the high apostrophe candidate across the block"],
             ["gv", "restore the exact previous block selection"],
             ["r:", "refine that same block to the centred joint glyph"]],
            "visual-reselect", 3.6,
        )
        reselect["grammar_families"].extend(["visual-scope", "block-change"])
        reselect["key_vocabulary"] = _family_breakdown(reselect["grammar_families"])
        reselect.pop("review_variants", None)
        reselect.pop("review_source_card_id", None)
        reselect.pop("review_method_family", None)

        rows.extend([
            ("M12.01", aa),
            ("M12.01", joint_height),
            ("M12.04", bridge(
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
                "char-find-repeat", 3.5)),
            ("M12.06", reselect),
        ])
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
        rows.extend([
            ("M15.08", bridge(
                "MAC", "Record one material edit and replay it",
                "Record one colon-to-dot material edit, then replay it at the next two visible landmarks on the same fixed-width row.",
                ["| : : : |", "|_______|", "| shadow |"],
                ["| . . . |", "|_______|", "| shadow |"],
                "gg0qqf:r.q0@q0@q",
                [["qq", "start recording register q"],
                 ["f:r.", "find and replace one material landmark"],
                 ["q", "stop recording"],
                 ["0@q0@q", "replay the bounded edit at the two remaining landmarks"]],
                "macro", 7.25, labels=True)),
            ("M15.08", bridge(
                "GLOBAL", "Apply one bounded edit only to matching rows",
                "Replace lowercase core glyphs only on rows selected by a global pattern; preserve the uppercase hold row.",
                ["| a |", "| A |", "| a |"],
                ["| + |", "| A |", "| + |"],
                ":g/a/normal! far+<CR>",
                [[":g/a/", "select only rows containing lowercase a"],
                 ["normal! far+", "run one bounded find-and-replace payload on each selected row"],
                 ["<CR>", "execute the complete global command"]],
                "global-normal", 7.5, labels=True)),
        ])
    elif mid == "M16":
        rows.append(("M16.05", bridge(
            "MOVE", "Move one complete plan block by addressed range",
            "Move the complete three-row A plan after the complete B plan without copying or splitting either block.",
            ["| A |", "|aaa|", "|---|", "| B |", "|bbb|", "|---|"],
            ["| B |", "|bbb|", "|---|", "| A |", "|aaa|", "|---|"],
            ":1,3m$<CR>",
            [[":1,3", "address every row owned by plan A"],
             ["m$", "move that complete range after the final line"],
             ["<CR>", "execute the addressed move"]],
            "ex-move", 4.5, labels=True)))
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


def mastery_extension_cards(module):
    """Manually authored guided -> hidden -> changed-art mastery pairs.

    These are not token-coverage cards.  Every hidden card requires the named
    command path at runtime, carries two source-linked reviews, and is required
    before its module can master.  The paired questions are authored separately
    in ``questions-authored-v2-mastery.json``.
    """
    habits, stages = MASTER_COVERAGE[module["id"]]

    def review(start, target, expected, recipe, source, label, prompt, hint):
        return {
            "start": start, "target": target, "expected": expected,
            "recipe": recipe, "cursor": "^", "source": source,
            "prompt": prompt, "hint": hint,
            "method_requirement": require_method(label, exact_any_of=[expected]),
        }

    def card(suffix, title, prompt, start, target, expected, recipe, family,
             ordinal, source, *, guided, reviews=None, extra_families=None,
             preserve_trailing_whitespace=False):
        card_id = "%s.%s" % (module["id"], suffix)
        families = [family, *(extra_families or [])]
        row = {
            "id": card_id, "module_id": module["id"], "ordinal": ordinal,
            "kind": "guided_edit" if guided else "independent_edit",
            "title": "%s · %s" % (module["title"], title),
            "project_id": "mastery-" + card_id.lower().replace(".", "-"),
            "artifact": "transfer", "variant_group": card_id + ".mastery",
            "skill": module["skill"],
            "source_ref": "%s; %s" % (module["source_ref"], source),
            "source": source, "medium": "monospace",
            "node_ids": [module["node"]], "master_habits": habits,
            "master_stages": stages,
            "lesson_benefit": (
                "perform %s with visible keys" % family if guided else
                "retrieve %s on unfamiliar animation art with the key path hidden" % family
            ),
            "prompt": prompt, "roadmap_contract": prompt,
            "start": start, "target": target, "expected": expected,
            "recipe": recipe, "cursor": "^", "show_target": True,
            "show_recipe": guided,
            "hint": (
                "Follow the visible grammar once, then inspect the registered result."
                if guided else
                "Name the acting cells first. The exact key sequence remains hidden until evaluation."
            ),
            "grammar_families": families,
            "grammar_stage": "guided" if guided else "hidden",
            "key_vocabulary": _family_breakdown(families),
            "frame_rows": module.get("frame_rows"),
            "frame_slices": ([module["frame_rows"]] *
                             (len(target) // module["frame_rows"])
                             if module.get("frame_rows") else [len(target)]),
            "method_requirement": require_method(
                "use the taught %s path" % family, exact_any_of=[expected]),
        }
        if preserve_trailing_whitespace:
            row["preserve_trailing_whitespace"] = True
        if reviews:
            row["review_variants"] = reviews
            row["review_source_card_id"] = card_id
            row["review_method_family"] = family
            row["required_before_mastery"] = True
        return row

    ss = stone_story_variants
    rows = []
    if module["id"] == "M12":
        checkpoint_label = "restore the exact joint block with gv before the centred replacement"
        checkpoint = card(
            "JHH", "Joint-height still checkpoint",
            "On this unfamiliar non-playing ornament study, test the high apostrophe in all three aligned joint cells, then restore that exact block with gv and refine it to the centred colon. Preserve every surrounding stroke and the four-cell row width.",
            ["|( .)|", "|[ .]|", "|{ .}|"],
            ["|( :)|", "|[ :]|", "|{ :}|"],
            "gg4|<C-v>2jr'gvr:",
            [["gg4|<C-v>2j", "select the complete aligned joint column"],
             ["r'", "test the high joint glyph on the selected cells"],
             ["gvr:", "restore the same selection and refine it to centred colons"]],
            "visual-reselect", 5.5,
            "ascii-art-authoring §4.6.5 joint-height test; non-playing authored sample sheet",
            guided=False,
            extra_families=["visual-scope", "block-change"],
            reviews=[
                review(
                    ["|/ .\\|", "|< .>|", "|\\ ./|"],
                    ["|/ :\\|", "|< :>|", "|\\ :/|"],
                    "gg4|<C-v>2jr'gvr:",
                    [["block r'", "test the high glyph on the complete joint column"],
                     ["gvr:", "restore and centre the same three cells"]],
                    "ascii-art-authoring §4.6.5 mirrored joint sample",
                    checkpoint_label,
                    "Changed-stroke review: refine the three aligned slash joints to centred colons after testing apostrophes.",
                    "Address the visible joint column once; gv must restore that exact block.",
                ),
                review(
                    ["|< .>|", "|[ .]|", "|{ .}|"],
                    ["|< :>|", "|[ :]|", "|{ :}|"],
                    "gg4|<C-v>2jr'gvr:",
                    [["block r'", "test the high glyph across the bracket joints"],
                     ["gvr:", "restore and centre the same block"]],
                    "ascii-art-authoring §4.6.5 bracket joint sample",
                    checkpoint_label,
                    "Changed-bracket review: centre the shared joint column while every delimiter stays fixed.",
                    "The final art alone is insufficient; retrieve the previous block with gv.",
                ),
            ],
        )
        checkpoint["lesson_benefit"] = (
            "prove joint-height judgement, fixed-column block replacement, gv retrieval, "
            "and changed-art recall on one still before animation unlocks"
        )
        rows.append(("M12.06", checkpoint))

    if module["id"] == "M5":
        seam_label = "break only the background-to-foreground seam with one replacement space"
        seam_checkpoint = card(
            "S6C", "Layer and seam still checkpoint",
            "On this unfamiliar four-row composite, preserve the cloud texture, roof material, and ground as separate back-to-front layers. Replace only the final cloud colon touching the roof with one space so the roof reads in front; do not move either layer.",
            ["| .::::. |", "| .:::/\\ |", "|    /__\\|", "|___/____|"],
            ["| .::::. |", "| .:: /\\ |", "|    /__\\|", "|___/____|"],
            "2G0f/hr ",
            [["2G0f/", "find the foreground roof slash from the acting background row"],
             ["h", "step back onto the touching background colon"],
             ["r ", "replace that one background cell with negative space"]],
            "search-landmark", 7.5,
            "ascii-art-authoring §3 depth checklist and §2.8 negative-space seams; authored single-composite study",
            guided=False,
            reviews=[
                review(
                    ["| ..;;;; |", "| ..;;;/\\|", "|   /___\\|", "|__/_____|"],
                    ["| ..;;;; |", "| ..;; /\\|", "|   /___\\|", "|__/_____|"],
                    "2G0f/hr ",
                    [["f/ then h", "address the final background hatch touching the roof"],
                     ["r ", "erase only that background cell"]],
                    "ascii-art-authoring §3 negative-space seam; hatch-material composite",
                    seam_label,
                    "Changed-hatch review: open one negative-space seam before the roof while preserving the hatch and ground materials.",
                    "Search for the foreground slash, then step back to the background cell that falsely joins it.",
                ),
                review(
                    ["| ~~~~~~ |", "| ~~~~/\\ |", "|   /___\\|", "|__/_____|"],
                    ["| ~~~~~~ |", "| ~~~ /\\ |", "|   /___\\|", "|__/_____|"],
                    "2G0f/hr ",
                    [["f/ then h", "address the touching background wave"],
                     ["r ", "make the one-cell separation"]],
                    "ascii-art-authoring §3 negative-space seam; wave-material composite",
                    seam_label,
                    "Changed-wave review: separate the foreground roof from its wave-texture background with one blank cell.",
                    "Do not delete or insert: the fixed-width layers must stay registered.",
                ),
            ],
        )
        seam_checkpoint["frame_rows"] = 4
        seam_checkpoint["frame_slices"] = [4]
        seam_checkpoint["lesson_benefit"] = (
            "prove back-to-front layer reading, material preservation, and one-cell "
            "negative-space seam separation on unfamiliar still art"
        )
        rows.append(("M5.08", seam_checkpoint))

    if module["id"] == "M13":
        w_label = "use lowercase w to count exact glyph-run boundaries"
        rows.extend([
            ("M13.04", card(
                "W", "Count lowercase word boundaries in a lava phase",
                "In the real Cave Party lava row, move by two lowercase-w boundaries and mark only the second crest; the figure rows stay fixed.",
                ss.CAVE_LAVA_A,
                [ss.CAVE_LAVA_A[0], ss.CAVE_LAVA_A[1], "    ~ ! ~ ~ ~ ~ ~"],
                "3G0wwr!",
                [["3G0", "start at the lava row's left edge"],
                 ["ww", "cross exactly two lowercase-w boundaries to the second crest"],
                 ["r!", "mark that one crest without shifting the phase"]],
                "lowercase-word-motion", 3.1,
                "official-Cosmetics/CaveParty res06 lava frame 1", guided=True)),
            ("M13.06", card(
                "WH", "Retrieve lowercase word motion on a moving tread",
                "On the unfamiliar Drill tread, mark only the third separated tread cell; keep the hull and lower track registered.",
                ss.DRILL_TREAD_SCENE,
                [ss.DRILL_TREAD_SCENE[0], " - - + - - -", ss.DRILL_TREAD_SCENE[2]],
                "2G0wwwr+",
                [["2G0", "start at the moving tread row"],
                 ["www", "count to the third punctuation run with lowercase w"],
                 ["r+", "replace only that tread cell"]],
                "lowercase-word-motion", 5.1,
                "official-Cosmetics/Drill res26 tread shimmer layer", guided=False,
                reviews=[
                    review(ss.CAVE_LAVA_B,
                           [ss.CAVE_LAVA_B[0], ss.CAVE_LAVA_B[1], "   ~ ~ ? ~ ~ ~ ~"],
                           "3G0wwwr?", [["3G0www", "reach the third shifted lava crest"], ["r?", "mark it"]],
                           "official-Cosmetics/CaveParty res06 lava frame 2", w_label,
                           "Cave Party shifted phase: mark only its third separated crest with lowercase w.",
                           "Count punctuation runs, not display columns."),
                    review(ss.DRILL_TREAD_SCENE,
                           [ss.DRILL_TREAD_SCENE[0], " - - - ! - -", ss.DRILL_TREAD_SCENE[2]],
                           "2G0wwwwr!", [["2G0wwww", "reach the fourth tread cell"], ["r!", "mark it"]],
                           "official-Cosmetics/Drill res26 tread shimmer layer", w_label,
                           "Drill tread review: mark only the fourth separated cell; preserve both surrounding rows.",
                           "Each dash is one punctuation run for lowercase w."),
                ])),
        ])

        gu_label = "use g_ to address the last nonblank glyph"
        missile_3_padded = [row + "   " for row in ss.MISSILE_F3]
        missile_4_padded = [row + "   " for row in ss.MISSILE_F4]
        chick_3_padded = [row + "   " for row in ss.CHICK_PEEP_F3]
        chick_4_padded = [row + "   " for row in ss.CHICK_PEEP_F4]
        rows.extend([
            ("M13.04", card(
                "GU", "Land on the final visible exhaust glyph",
                "Turn the missile's final exhaust apostrophe into the next frame's dot while ignoring the three alignment spaces after it.",
                missile_3_padded, missile_4_padded, "2Gg_r.",
                [["2G", "go to the exhaust row"],
                 ["g_", "land on its last nonblank glyph, not the padded row end"],
                 ["r.", "write the next exhaust cell in place"]],
                "last-nonblank", 3.2,
                "official-Games/TowerDefense res18 missile frame 3 -> 4", guided=True)),
            ("M13.06", card(
                "GH", "Retrieve last-nonblank motion on a peep frame",
                "Close only the chick's final beak glyph from < to -; trailing registration spaces must remain untouched.",
                chick_3_padded, chick_4_padded, "ggg_r-",
                [["gg", "go to the peep frame's first row"],
                 ["g_", "land on its last visible glyph"],
                 ["r-", "close the beak without changing row width"]],
                "last-nonblank", 5.2,
                "official-Pets/Chick res03 peep frame 3 -> 4", guided=False,
                reviews=[
                    review(missile_4_padded,
                           [missile_4_padded[0], ss.MISSILE_F3[1] + "   ", missile_4_padded[2]],
                           "2Gg_r'", [["2Gg_", "land on the exhaust row's last nonblank glyph"], ["r'", "restore the apostrophe puff"]],
                           "official-Games/TowerDefense res18 missile frame 4 -> 3", gu_label,
                           "Missile review: restore the final exhaust apostrophe without entering the padding.",
                           "g_ ignores the spaces after the visible puff."),
                    review(chick_4_padded, chick_3_padded, "ggg_r<",
                           [["ggg_", "land on the final visible beak glyph"], ["r<", "reopen it"]],
                           "official-Pets/Chick res03 peep frame 4 -> 3", gu_label,
                           "Chick review: reopen the last beak cell while preserving the padded row width.",
                           "Use the last nonblank cell, not the physical end after padding."),
                ])),
        ])

    if module["id"] == "M4":
        def prefixed(art, glyph="|"):
            return [glyph + row for row in art]
        def column(art, one_based, glyph):
            return [row[:one_based - 1] + glyph + row[one_based:] for row in art]

        bi_label = "insert one registration rail with blockwise I"
        rows.extend([
            ("M4.04", card(
                "BI", "Insert one onion-skin rail across a lava frame",
                "Add one left registration rail to every row of the three-row lava frame in one blockwise insert.",
                ss.CAVE_LAVA_A, prefixed(ss.CAVE_LAVA_A),
                "gg0<C-v>2jI|<Esc>",
                [["gg0<C-v>2j", "select column 1 through all three frame rows"],
                 ["I|<Esc>", "insert the same rail on every selected row"]],
                "block-insert", 3.1,
                "official-Cosmetics/CaveParty res06 lava frame 1", guided=True)),
            ("M4.06", card(
                "BIH", "Retrieve block insert on a missile frame",
                "On the unfamiliar missile frame, add one left onion-skin rail to all three rows; do not type three separate rails.",
                ss.MISSILE_F1, prefixed(ss.MISSILE_F1),
                "gg0<C-v>2jI|<Esc>",
                [["gg0<C-v>2j", "select the shared first column"],
                 ["I|<Esc>", "apply one rail to every frame row"]],
                "block-insert", 5.1,
                "official-Games/TowerDefense res18 missile frame 1", guided=False,
                reviews=[
                    review(ss.SNOWBUNNY_IDLE, prefixed(ss.SNOWBUNNY_IDLE, "!"),
                           "gg0<C-v>2jI!<Esc>", [["gg0<C-v>2j", "select all bunny rows at column 1"], ["I!<Esc>", "add one comparison rail"]],
                           "official-Pets/SnowBunny res01", bi_label,
                           "Snow bunny review: add a single left comparison rail to all three pose rows.",
                           "One block insert owns the complete pose height."),
                    review(ss.SKULLY_IDLE, prefixed(ss.SKULLY_IDLE, "+"),
                           "gg0<C-v>2jI+<Esc>", [["gg0<C-v>2j", "select all skull rows at column 1"], ["I+<Esc>", "add the rail"]],
                           "official-Pets/Skully res01", bi_label,
                           "Skully review: prefix the complete pose with one blockwise registration rail.",
                           "Do not repeat a separate Insert-mode edit on each row."),
                ])),
        ])

        bc_label = "replace one registered column with blockwise c"
        rows.extend([
            ("M4.04", card(
                "BC", "Change one onion-skin axis as a block",
                "On the missile, replace display column 3 across all three rows with one temporary onion-skin axis.",
                ss.MISSILE_F1, column(ss.MISSILE_F1, 3, "|"),
                "gg3|<C-v>2jc|<Esc>",
                [["gg3|<C-v>2j", "select display column 3 through the frame"],
                 ["c|<Esc>", "change the complete selected column to the axis glyph"]],
                "block-change", 3.2,
                "official-Games/TowerDefense res18 missile frame 1", guided=True)),
            ("M4.06", card(
                "BCH", "Retrieve block change on shifted lava",
                "On the unfamiliar shifted lava frame, change only column 3 across all three rows into a registration axis.",
                ss.CAVE_LAVA_B, column(ss.CAVE_LAVA_B, 3, "|"),
                "gg3|<C-v>2jc|<Esc>",
                [["gg3|<C-v>2j", "select one registered column"],
                 ["c|<Esc>", "change that column on every selected row"]],
                "block-change", 5.2,
                "official-Cosmetics/CaveParty res06 lava frame 2", guided=False,
                reviews=[
                    review(ss.SNOWBUNNY_IDLE, column(ss.SNOWBUNNY_IDLE, 3, "!"),
                           "gg3|<C-v>2jc!<Esc>", [["gg3|<C-v>2j", "select column 3 of the whole pose"], ["c!<Esc>", "change that block"]],
                           "official-Pets/SnowBunny res01", bc_label,
                           "Snow bunny review: replace only the third registered column across the pose with an inspection axis.",
                           "Blockwise c owns the same column on every selected row."),
                    review(ss.SKULLY_IDLE, column(ss.SKULLY_IDLE, 3, "+"),
                           "gg3|<C-v>2jc+<Esc>", [["gg3|<C-v>2j", "select the skull's third display column"], ["c+<Esc>", "change it on all rows"]],
                           "official-Pets/Skully res01", bc_label,
                           "Skully review: mark the third registered column through all pose rows with one block change.",
                           "The selection is vertical; no other columns move."),
                ])),
        ])

        def onion_diff_keys(edit_keys):
            return (":vnew<CR>:silent 0read #<CR>ggdd:diffthis<CR>:set scrollbind<CR>"
                    "<C-w>p:diffthis<CR>:set scrollbind<CR>" + edit_keys +
                    ":diffoff!<CR><C-w>p:bwipeout!<CR>")

        diff_label = "compare a working frame against a scroll-bound reference"
        missile_diff = onion_diff_keys("2G0f'r.")
        chick_diff = onion_diff_keys("gg0f<r-")
        skully_diff = onion_diff_keys("2G0for=;r=")
        bunny_diff = onion_diff_keys("2G0fnr-;r-")
        rows.extend([
            ("M4.04", card(
                "DIFF", "Onion-skin a missile exhaust frame in a bound diff view",
                "Open a disposable vertical reference of missile frame 3, enable diff and scroll binding in both views, change only the final exhaust puff to frame 4, then close only the reference window.",
                ss.MISSILE_F3, ss.MISSILE_F4, missile_diff,
                [[":vnew<CR>:silent 0read #<CR>ggdd", "make a disposable reference from the saved prior frame"],
                 [":diffthis<CR>:set scrollbind<CR>", "enable aligned comparison in the reference"],
                 ["<C-w>p:diffthis<CR>:set scrollbind<CR>", "return to the working frame and bind its comparison view"],
                 ["2G0f'r.", "advance only the final exhaust puff"],
                 [":diffoff!<CR><C-w>p:bwipeout!<CR>", "end comparison and discard only the disposable reference buffer"]],
                "onion-diff-view", 3.4,
                "official-Games/TowerDefense res18 missile frame 3 -> 4", guided=True)),
            ("M4.06", card(
                "DIFFH", "Retrieve onion-skin diff on a Chick peep frame",
                "On the unfamiliar Chick pose, build a disposable scroll-bound diff reference, close only the beak from < to -, then tear down the comparison without closing the tutor brief.",
                ss.CHICK_PEEP_F3, ss.CHICK_PEEP_F4, chick_diff,
                [[":vnew<CR>:silent 0read #<CR>ggdd", "copy the prior Chick frame into a disposable reference"],
                 [":diffthis<CR>:set scrollbind<CR>", "align that reference"],
                 ["<C-w>p:diffthis<CR>:set scrollbind<CR>", "bind the working pose to it"],
                 ["gg0f<r-", "close only the beak endpoint"],
                 [":diffoff!<CR><C-w>p:bwipeout!<CR>", "remove diff mode and discard the reference buffer"]],
                "onion-diff-view", 5.4,
                "official-Pets/Chick res03 peep frame 3 -> 4", guided=False,
                reviews=[
                    review(ss.SKULLY_IDLE, ss.SKULLY_BLINK, skully_diff,
                           [["reference + diffthis", "open the prior Skully pose beside the work"],
                            ["scrollbind", "keep corresponding pose rows aligned"],
                            ["2G0for=;r=", "close both eyes with repeated bounded find and replace"],
                            ["diffoff + bwipeout", "tear down only the disposable reference"]],
                           "official-Pets/Skully res01 -> res04 blink overlay", diff_label,
                           "Skully review: compare the open pose beside the working blink, keep rows bound, and close the disposable reference after verifying both eye changes.",
                           "The reference is a temporary window; the working art remains the submitted buffer."),
                    review(ss.SNOWBUNNY_IDLE, ss.SNOWBUNNY_BLINK, bunny_diff,
                           [["reference + diffthis", "open the prior bunny pose beside the work"],
                            ["scrollbind", "align the three pose rows"],
                            ["2G0fnr-;r-", "close the two eyes around the unchanged nose"],
                            ["diffoff + bwipeout", "remove only the reference view"]],
                           "official-Pets/SnowBunny res01 -> res03 blink overlay", diff_label,
                           "SnowBunny review: onion-skin the open pose, make the blink in the working frame, then close only the disposable comparison window.",
                           "Use window-local comparison tools; do not close the tutor's upper brief."),
                ])),
        ])

        gv_label = "restore and refine the same block with gv"
        rows.extend([
            ("M4.04", card(
                "GV", "Reselect an onion-skin axis for refinement",
                "Try a vertical axis in missile column 3, then reselect that exact block with gv and refine it to ! without rebuilding the selection.",
                ss.MISSILE_F1, column(ss.MISSILE_F1, 3, "!"),
                "gg3|<C-v>2jc|<Esc>gvr!",
                [["gg3|<C-v>2jc|<Esc>", "make the first axis candidate"],
                 ["gv", "restore the exact previous three-cell block"],
                 ["r!", "refine every selected axis cell in place"]],
                "visual-reselect", 3.3,
                "official-Games/TowerDefense res18 missile frame 1", guided=True,
                extra_families=["block-change"])),
            ("M4.06", card(
                "GVH", "Retrieve gv on a shifted lava axis",
                "On the unfamiliar lava frame, create a temporary column-3 axis and then refine the same selection to : with gv.",
                ss.CAVE_LAVA_B, column(ss.CAVE_LAVA_B, 3, ":"),
                "gg3|<C-v>2jc|<Esc>gvr:",
                [["gg3|<C-v>2jc|<Esc>", "create the temporary axis"],
                 ["gvr:", "reselect it and replace every selected cell with the final marker"]],
                "visual-reselect", 5.3,
                "official-Cosmetics/CaveParty res06 lava frame 2", guided=False,
                extra_families=["block-change"],
                reviews=[
                    review(ss.SNOWBUNNY_IDLE, column(ss.SNOWBUNNY_IDLE, 3, "+"),
                           "gg3|<C-v>2jc|<Esc>gvr+", [["block c", "make the first three-row axis"], ["gvr+", "restore and refine it"]],
                           "official-Pets/SnowBunny res01", gv_label,
                           "Snow bunny review: refine the just-made three-row axis to + by restoring its previous selection.",
                           "gv should recover the exact block; do not navigate and rebuild it."),
                    review(ss.SKULLY_IDLE, column(ss.SKULLY_IDLE, 3, "!"),
                           "gg3|<C-v>2jc|<Esc>gvr!", [["block c", "make the temporary skull axis"], ["gvr!", "restore and refine it"]],
                           "official-Pets/Skully res01", gv_label,
                           "Skully review: use gv to refine the same selected axis, preserving all neighbouring cells.",
                           "The second replacement must act on the restored selection."),
                ])),
        ])

    if module["id"] == "M3":
        ga_label = "inspect the acting glyph with ga before replacing it"
        shock_look = list(ss.FACE_SHOCK)
        shock_look[2] = shock_look[2].replace("(o)", "(O)", 1)
        neutral_look = list(ss.FACE_NEUTRAL)
        neutral_look[2] = neutral_look[2].replace("<o)", "<O)", 1)
        rows.extend([
            ("M3.04", card(
                "GA", "Inspect a pupil before widening it",
                "On the six-row FaceHUD shock pose, use ga on the left pupil before widening only that cell from o to O.",
                ss.FACE_SHOCK, shock_look, "3G0fogarO",
                [["3G0fo", "land on the left pupil"],
                 ["ga", "inspect the exact glyph under the cursor"],
                 ["rO", "widen that one pupil without shifting the face"]],
                "glyph-inspect", 3.1,
                "official-UI/FaceHUD res08 shock pose", guided=True)),
            ("M3.06", card(
                "GAH", "Retrieve glyph inspection on a neutral face",
                "On the unfamiliar FaceHUD neutral pose, inspect the left pupil with ga before changing only it to O.",
                ss.FACE_NEUTRAL, neutral_look, "3G0fogarO",
                [["3G0fo", "land on the left pupil"], ["ga", "inspect it"],
                 ["rO", "replace that pupil only"]],
                "glyph-inspect", 5.1,
                "official-UI/FaceHUD res02 neutral pose", guided=False,
                reviews=[
                    review(ss.FACE_SHOCK_WOUND,
                           [ss.FACE_SHOCK_WOUND[0], ss.FACE_SHOCK_WOUND[1], "  (o) (O)", *ss.FACE_SHOCK_WOUND[3:]],
                           "3G0f(;fogarO", [["3G0f(;fo", "reach the right pupil"], ["ga", "inspect it"], ["rO", "widen it"]],
                           "official-UI/FaceHUD res08 + res10 wound overlay", ga_label,
                           "FaceHUD wound review: inspect the right pupil before widening only that eye.",
                           "Use the second opening parenthesis as the landmark, then inspect the pupil."),
                    review(ss.FACE_NEUTRAL,
                           [ss.FACE_NEUTRAL[0], ss.FACE_NEUTRAL[1], "  <o) (O>", *ss.FACE_NEUTRAL[3:]],
                           "3G0f(;fogarO", [["3G0f(;fo", "reach the right pupil"], ["ga", "inspect it"], ["rO", "widen it"]],
                           "official-UI/FaceHUD res02 neutral pose", ga_label,
                           "Neutral FaceHUD review: inspect the other pupil before changing its width.",
                           "ga reports the glyph you are about to replace; it does not move the cursor."),
                ])),
        ])

    if module["id"] == "M14":
        dap_label = "delete one complete blank-line-separated frame with dap"
        skully_pair = ss.SKULLY_IDLE + [""] + ss.SKULLY_BLINK + [""]
        bunny_pair = ss.SNOWBUNNY_IDLE + [""] + ss.SNOWBUNNY_BLINK + [""]
        rows.extend([
            ("M14.04", card(
                "DAP", "Delete one complete paragraph frame",
                "The first Skully pose is an accidental duplicate before the blink. Delete that complete frame and its separator as one paragraph object.",
                skully_pair, ss.SKULLY_BLINK + [""], "ggdap",
                [["gg", "land inside the first frame paragraph"],
                 ["dap", "delete around the paragraph: all pose rows plus its separator"]],
                "paragraph-delete", 3.1,
                "official-Pets/Skully res01 + res04 blink overlay", guided=True)),
            ("M14.06", card(
                "DAPH", "Retrieve paragraph deletion on a bunny blink",
                "On the unfamiliar snow-bunny strip, remove the complete open-eyed paragraph so the blink frame remains registered.",
                bunny_pair, ss.SNOWBUNNY_BLINK + [""], "ggdap",
                [["gg", "land in the first frame"],
                 ["dap", "delete the complete frame object and blank separator"]],
                "paragraph-delete", 5.1,
                "official-Pets/SnowBunny res01 + res03 blink overlay", guided=False,
                reviews=[
                    review(ss.FROG_OPEN + [""] + ss.FROG_SHUT + [""], ss.FROG_SHUT + [""], "ggdap",
                           [["ggdap", "delete the complete open-eye frog paragraph"]],
                           "official-Pets/Frog res01 + res07 blink overlay", dap_label,
                           "Frog review: remove the complete open-eye frame and its separator; leave the blink intact.",
                           "ap owns the whole blank-line-separated frame."),
                    review(ss.SKULLY_LOOK + [""] + ss.SKULLY_BLINK + [""], ss.SKULLY_BLINK + [""], "ggdap",
                           [["ggdap", "delete the complete look pose paragraph"]],
                           "official-Pets/Skully res01 + res02/res04 overlays", dap_label,
                           "Skully review: remove the complete look pose paragraph before the blink.",
                           "Delete the frame object, not three guessed rows."),
                ])),
        ])

    if module["id"] == "M15":
        def trimmed_copy_art(art):
            width = max(len(row) for row in art)
            start = [row.ljust(width) for row in art] + ["|>--[]", "|>--[]", "|>--[]"]
            target = start[:3] + ["|>" + row.rstrip() + "--[]" for row in art]
            expected = "gg0<C-v>2j%d|zy4G2|zp" % width
            return start, target, expected, width

        zp_label = "copy a ragged pose without adding trailing block padding"
        missile_start, missile_target, missile_expected, missile_width = trimmed_copy_art(ss.MISSILE_F1)
        chick_start, chick_target, chick_expected, chick_width = trimmed_copy_art(ss.CHICK_PEEP_F3)
        skully_start, skully_target, skully_expected, skully_width = trimmed_copy_art(ss.SKULLY_IDLE)
        bunny_start, bunny_target, bunny_expected, bunny_width = trimmed_copy_art(ss.SNOWBUNNY_IDLE)
        rows.extend([
            ("M15.04", card(
                "ZP", "Copy a ragged missile pose without padding its short rows",
                "Copy the three-row missile from its padded palette into the three > destination rows. Preserve each source row's real visible width; do not paste a rectangular tail of spaces.",
                missile_start, missile_target, missile_expected,
                [["gg0<C-v>2j%d|" % missile_width, "select the complete padded palette block"],
                 ["zy", "yank each row without its trailing alignment spaces"],
                 ["4G2|zp", "paste after the > marker without rebuilding a padded rectangle"]],
                "trimmed-block-copy", 3.15,
                "official-Games/TowerDefense res18 missile frame 1", guided=True)),
            ("M15.06", card(
                "ZPH", "Retrieve trimmed block copy on a chick peep pose",
                "On the unfamiliar Chick frame, copy the ragged three-row pose from its padded palette into the > destination rows without carrying invisible right-edge padding.",
                chick_start, chick_target, chick_expected,
                [["gg0<C-v>2j%d|" % chick_width, "select the padded Chick palette block"],
                 ["zy", "drop trailing spaces from each yanked row"],
                 ["4G2|zp", "paste the ragged pose after the destination markers"]],
                "trimmed-block-copy", 5.15,
                "official-Pets/Chick res03 peep frame 3", guided=False,
                reviews=[
                    review(skully_start, skully_target, skully_expected,
                           [["gg0<C-v>2j%d|" % skully_width, "select the padded Skully pose"],
                            ["zy", "yank without right-edge padding"],
                            ["4G2|zp", "paste the ragged pose after the markers"]],
                           "official-Pets/Skully res01", zp_label,
                           "Skully review: copy the full ragged pose into the destination rows without padding every row to the skull's widest line.",
                           "Use zy for the block yank and zp for the block put."),
                    review(bunny_start, bunny_target, bunny_expected,
                           [["gg0<C-v>2j%d|" % bunny_width, "select the padded SnowBunny pose"],
                            ["zy", "trim each row's invisible tail while yanking"],
                            ["4G2|zp", "paste without a rectangular space tail"]],
                           "official-Pets/SnowBunny res01", zp_label,
                           "SnowBunny review: copy the uneven pose after the destination markers and leave no manufactured trailing-space rectangle.",
                           "The z-prefixed yank and put preserve the pose's ragged visible edge."),
                ])),
        ])

    if module["id"] == "M11":
        def padded_cleanup_art(art, padding=3):
            start = [row + (" " * padding) for row in art]
            target = [row.rstrip() for row in start]
            boundary = max(len(row) for row in art) + 1
            expected = (":set list<CR>:set cursorcolumn<CR>"
                        ":set colorcolumn=%d<CR>:%%s/\\s\\+$//e<CR>" % boundary)
            return start, target, expected, boundary

        audit_label = "inspect registration columns, then remove only trailing whitespace"
        missile_start, missile_target, missile_audit, missile_boundary = padded_cleanup_art(ss.MISSILE_F3)
        chick_start, chick_target, chick_audit, chick_boundary = padded_cleanup_art(ss.CHICK_PEEP_F3)
        skully_start, skully_target, skully_audit, skully_boundary = padded_cleanup_art(ss.SKULLY_IDLE)
        bunny_start, bunny_target, bunny_audit, bunny_boundary = padded_cleanup_art(ss.SNOWBUNNY_IDLE)
        rows.extend([
            ("M11.04", card(
                "WS", "Expose and clean only the invisible row tails",
                "Inspect the padded missile frame with visible whitespace and column guides, then remove only trailing spaces. Every visible missile and exhaust glyph must remain unchanged.",
                missile_start, missile_target, missile_audit,
                [[":set list<CR>", "show otherwise invisible whitespace"],
                 [":set cursorcolumn<CR>", "track the active registered column"],
                 [":set colorcolumn=%d<CR>" % missile_boundary, "mark the first column beyond the intended frame width"],
                 [":%s/\\s\\+$//e<CR>", "remove whitespace only when it reaches a row end"]],
                "whitespace-column-audit", 3.6,
                "official-Games/TowerDefense res18 missile frame 3", guided=True,
                preserve_trailing_whitespace=True)),
            ("M11.06", card(
                "WSH", "Retrieve whitespace inspection on a padded Chick pose",
                "On the unfamiliar Chick frame, turn on the whitespace and column guides, then remove only the three invisible tail spaces from each row. Preserve every visible pose cell.",
                chick_start, chick_target, chick_audit,
                [[":set list<CR>", "reveal the padded row tails"],
                 [":set cursorcolumn<CR>", "keep the current registration column visible"],
                 [":set colorcolumn=%d<CR>" % chick_boundary, "mark the pose-width boundary"],
                 [":%s/\\s\\+$//e<CR>", "trim only whitespace anchored at row ends"]],
                "whitespace-column-audit", 5.6,
                "official-Pets/Chick res03 peep frame 3", guided=False,
                preserve_trailing_whitespace=True,
                reviews=[
                    review(skully_start, skully_target, skully_audit,
                           [[":set list<CR>", "show Skully's padded tails"],
                            [":set cursorcolumn<CR>", "track the active column"],
                            [":set colorcolumn=%d<CR>" % skully_boundary, "mark the intended right edge"],
                            [":%s/\\s\\+$//e<CR>", "remove only trailing whitespace"]],
                           "official-Pets/Skully res01", audit_label,
                           "Skully review: inspect the registered right edge, then trim the invisible tail without touching the visible skull contour.",
                           "Make whitespace visible before the end-anchored cleanup."),
                    review(bunny_start, bunny_target, bunny_audit,
                           [[":set list<CR>", "show SnowBunny's padded tails"],
                            [":set cursorcolumn<CR>", "track the active column"],
                            [":set colorcolumn=%d<CR>" % bunny_boundary, "mark the intended right edge"],
                            [":%s/\\s\\+$//e<CR>", "remove only trailing whitespace"]],
                           "official-Pets/SnowBunny res01", audit_label,
                           "SnowBunny review: reveal and remove only invisible row tails; the ears, face, and body must remain byte-for-byte visible.",
                           "The cleanup pattern is anchored at each row end."),
                ])),
        ])

        undo_label = "visit alternate animation takes through the undo tree"
        skully_undo = "2G0for!urOg-g+:earlier 1<CR>g+"
        bunny_undo = "2G0fnr!ur-g-g+:earlier 1<CR>g+"
        missile_undo = "2G0f'r!ur.g-g+:earlier 1<CR>g+"
        chick_undo = "gg0f<r!ur-g-g+:earlier 1<CR>g+"
        bunny_half = [ss.SNOWBUNNY_IDLE[0],
                      ss.SNOWBUNNY_IDLE[1].replace("n", "-", 1),
                      ss.SNOWBUNNY_IDLE[2]]
        rows.extend([
            ("M11.04", card(
                "UT", "Compare two Skully look takes through the undo tree",
                "Try ! as an exaggerated left eye, undo it, author the chosen O look, visit the abandoned ! take with chronological history, then return to and submit the O-eye frame.",
                ss.SKULLY_IDLE, ss.SKULLY_LOOK, skully_undo,
                [["2G0for!", "author the exaggerated ! eye take"],
                 ["u", "return before that take so the next edit creates a branch"],
                 ["rO", "author the chosen look take"],
                 ["g-g+", "visit the abandoned older take, then return to the newer choice"],
                 [":earlier 1<CR>g+", "repeat the history comparison and finish on the chosen O eye"]],
                "undo-tree-travel", 3.7,
                "official-Pets/Skully res01 -> res02 look overlay", guided=True)),
            ("M11.06", card(
                "UTH", "Retrieve undo-tree comparison on a SnowBunny half-blink",
                "On the unfamiliar SnowBunny pose, try ! as an exaggerated left eye, undo and author the chosen -, inspect the abandoned take chronologically, then return to the half-blink for submission.",
                ss.SNOWBUNNY_IDLE, bunny_half, bunny_undo,
                [["2G0fnr!", "author the exaggerated first-eye take"],
                 ["ur-", "undo it and create the chosen half-blink branch"],
                 ["g-g+", "walk to the abandoned take and back chronologically"],
                 [":earlier 1<CR>g+", "revisit the older state once more and finish on the chosen branch"]],
                "undo-tree-travel", 5.7,
                "official-Pets/SnowBunny res01 half-blink study", guided=False,
                reviews=[
                    review(ss.MISSILE_F3, ss.MISSILE_F4, missile_undo,
                           [["r! then u", "try and undo an exaggerated exhaust puff"],
                            ["r.", "author the chosen settled exhaust"],
                            ["g-/g+ and :earlier", "inspect the abandoned take and return"]],
                           "official-Games/TowerDefense res18 missile frame 3 -> 4", undo_label,
                           "Missile review: branch between an exaggerated exhaust puff and the chosen settle, visit the abandoned take chronologically, and submit the dot.",
                           "History travel compares takes; the newest chosen take must be restored before saving."),
                    review(ss.CHICK_PEEP_F3, ss.CHICK_PEEP_F4, chick_undo,
                           [["r! then u", "try and undo an exaggerated beak"],
                            ["r-", "author the chosen closed beak"],
                            ["g-/g+ and :earlier", "inspect the abandoned branch and return"]],
                           "official-Pets/Chick res03 peep frame 3 -> 4", undo_label,
                           "Chick review: compare an exaggerated beak against the chosen closed endpoint through the undo tree, then finish on the dash.",
                           "The art result and the visited history commands are both graded."),
                ])),
        ])
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
            "evidence": "target-linked changed-art retrieval; method enforcement reported separately",
        })
    return rows


def primer_question(module):
    before = ["  @  ", " /|\\ ", " / \\ ", ".....", "     ", "  ?  "]
    after = list(before)
    primer_visual = visual_pair(before, after)
    compact_visual = visual_delta(before, after, max_rows=4)
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
            f"{primer_visual}\n\n"
            "NEOVIM\nThe lesson just taught `4j`. What does the unfamiliar command `5j` mean?"
        ),
        "animation_prompt": "Inspect a lower animation row while leaving every glyph registered.",
        "animation_answer": "cursor inspection leaves every art cell unchanged",
        "neovim_prompt": "Transfer the taught 4j pattern to 5j.",
        "neovim_answer": "5 is the count and j is the down-one-row motion, so the cursor moves down five rows",
        "compact_prompt": (
            "ANIMATION: inspect a lower row without changing art.\n\n"
            f"{compact_visual}\n\n"
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
    "M19.02": [duplicate((1, 2), "scaffold", "working copy reserved for the hand-authored opposite-facing still", False)],
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
                # An unseen transfer is the module's first honest method
                # retrieval. Reaching the target by an unrelated route must
                # not create mastery evidence, and a later changed-art variant
                # must be retrieved before the module is mastered.
                card.setdefault("method_requirement", require_method(
                    "perform the unfamiliar-art transfer with its taught command path",
                    exact_any_of=[card["expected"]]))
                for variant in card["variants"]:
                    variant.setdefault("method_requirement", require_method(
                        "repeat the taught transfer method on changed art",
                        exact_any_of=[variant["expected"]]))
                card["required_before_mastery"] = True
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
    module_defs = {module["id"]: module for module in MODULES}
    if set(module_defs) != set(MODULE_SEQUENCE):
        raise SystemExit("MODULE_SEQUENCE must name every module exactly once")
    for module_id in MODULE_SEQUENCE:
        module = module_defs[module_id]
        module_cards = make_cards(module, catalog_prompts)
        if module["id"] == "M0":
            primer, yank_put, open_line, addressed_substitute, ex_copy = m0_extra_cards(module)
            module_cards = [primer, module_cards[0], yank_put, open_line,
                            addressed_substitute, module_cards[1], module_cards[2],
                            module_cards[3], ex_copy] + module_cards[4:]
        bridge_rows = [*guided_bridge_cards(module), *mastery_extension_cards(module)]
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
        # VD-29: real Stone Story frames replace same-subject "changed art".
        stone_story_variants.apply(module_cards)
        for card in module_cards:
            if card["id"] in STILL_PROMPT_REWRITES:
                card["prompt"] = STILL_PROMPT_REWRITES[card["id"]]
                card["roadmap_contract"] = STILL_PROMPT_REWRITES[card["id"]]
            owner = STAGE_OWNER_OVERRIDES.get(
                card["id"], PRIMARY_STAGE_BY_MODULE[module["id"]])
            card["stage_owner"] = owner
            card["artifact_mode"] = ARTIFACT_MODE_BY_STAGE[owner]
            # One card supplies evidence to one progression stage.  The old
            # mixed labels made a single pass appear to advance unrelated
            # still and animation stages simultaneously.
            card["master_stages"] = [owner]
        stage_ids = []
        for card in module_cards:
            if card["stage_owner"] not in stage_ids:
                stage_ids.append(card["stage_owner"])
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
            "stage_ids": stage_ids,
            "card_ids": [card["id"] for card in module_cards],
            "required_review_card_ids": [
                card["id"] for card in module_cards
                if card.get("required_before_mastery")
            ],
        })
        cards.extend(module_cards)
        questions.extend(question(module, n) for n in range(1, 11))
        if module["id"] == "M0":
            questions.append(primer_question(module))
    module_map = module_defs
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
    for card in cards:
        if card["id"] not in ALT_VARIANT_QUESTION_CARDS:
            continue
        variant = card["variants"][1]
        variant_card = dict(card)
        variant_card.update(variant)
        variant_card["id"] = card["id"] + ".V2"
        pair = paired_question(module_map[card["module_id"]], variant_card)
        pair["card_id"] = card["id"]
        questions.append(pair)
        qmap[pair["id"]] = pair
        variant["paired_question_ids"] = [pair["id"]]
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
                "evidence": ("runtime-required ordered command path plus exact target" if exact else
                             "runtime-required token pattern and optional key limit"),
            })
        for taught in card.get("method_alternatives", []):
            verified_methods.append({
                "card_id": card["id"], "label": taught["label"],
                "evidence": "runtime-recognized comparison method",
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
    required_mastery_reviews = [{
        "module_id": card["module_id"],
        "source_card_id": card["id"],
        "method_label": card["method_requirement"]["label"],
        "changed_art_variants": len(card.get("variants") or card.get("review_variants") or []),
        "keys_hidden": card.get("show_recipe") is False,
        "required_before_mastery": True,
        "evidence": "method-required hidden transfer plus changed-art spaced review",
    } for card in cards if card.get("required_before_mastery")]
    animation_lessons = load_animation_lesson_pack()
    output_module_map = {module["id"]: module for module in modules}
    for lesson in animation_lessons:
        guided_card_id = lesson["delivery"]["guided_card_id"]
        hidden_card_id = lesson["delivery"]["hidden_card_id"]
        guided_card = card_map[guided_card_id]
        hidden_card = card_map[hidden_card_id]
        lesson["earlier_guided_family_gate"]["guided_families"] = list(
            guided_card.get("grammar_families", []))
        lesson["earlier_guided_family_gate"]["hidden_families"] = list(
            hidden_card.get("grammar_families", []))
        pack_question_ids = [question["id"] for question in lesson["questions"]]
        for card in (guided_card, hidden_card):
            card.setdefault("animation_pack_lesson_ids", []).append(lesson["id"])
            card.setdefault("animation_pack_question_ids", []).extend(pack_question_ids)
        output_module_map[guided_card["module_id"]].setdefault(
            "animation_pack_lesson_ids", []).append(lesson["id"])
    # Question wording is curriculum, not boilerplate. Explicitly authored
    # records replace the scaffold wholesale; the generator only installs the
    # exact prose, choices, and feedback written in the bank.
    authored_questions = {}
    for authored_path in AUTHORED_QUESTION_FILES:
        authored_file = json.loads(authored_path.read_text(encoding="utf-8"))
        duplicates = set(authored_questions) & set(authored_file)
        if duplicates:
            raise ValueError("question ids are authored in more than one file: %r" %
                             sorted(duplicates))
        authored_questions.update(authored_file)
    question_map = {question["id"]: question for question in questions}
    unknown_authored = set(authored_questions) - set(question_map)
    if unknown_authored:
        raise ValueError("authored question ids are not in the curriculum: %r" %
                         sorted(unknown_authored))
    missing_authored = set(question_map) - set(authored_questions)
    if missing_authored:
        raise ValueError(
            "every curriculum question must have an explicit hand-authored record; "
            "missing: %r" % sorted(missing_authored))
    for question_id, authored in authored_questions.items():
        question_map[question_id].update(authored)
        question_map[question_id]["authorship"] = "manual"

    stage_order = [*MAIN_STAGE_SEQUENCE, "P"]
    stages = []
    for index, stage_id in enumerate(stage_order):
        stage_cards = [card for card in cards if card["stage_owner"] == stage_id]
        prerequisites = ([MAIN_STAGE_SEQUENCE[index - 1]]
                         if stage_id in MAIN_STAGE_SEQUENCE and index else [])
        if stage_id == "P":
            prerequisites = ["S5"]
        stages.append({
            "id": stage_id,
            "title": STAGE_TITLES[stage_id],
            "track": ("still" if stage_id.startswith("S") else
                      "animation" if stage_id.startswith("A") else "optional"),
            "optional": stage_id == "P",
            "prerequisites": prerequisites,
            "card_ids": [card["id"] for card in stage_cards],
            "required_review_card_ids": [
                card["id"] for card in stage_cards
                if card.get("required_before_mastery")
            ],
        })
    return {
        "schema": "vim-daily/curriculum@4", "revision": "2026-09-29.53",
        "review_intervals_hours": [4, 24, 72, 168, 336],
        "main_stage_sequence": MAIN_STAGE_SEQUENCE,
        "stages": stages, "modules": modules, "cards": cards, "questions": questions,
        "animation_lesson_pack": animation_lessons,
        "animation_lesson_pack_contract": {
            "source": "share/animation_lesson_pack.md",
            "lesson_count": len(animation_lessons),
            "question_count": sum(len(lesson["questions"]) for lesson in animation_lessons),
            "domains": ["ascii_animation", "neovim"],
            "changed_art_variants_min": 2,
            "rights": "integration blocked for unresolved source art; generated exercises are original",
            "master_habits": [f"H{number}" for number in range(1, 10)],
            "master_stages": [*(f"S{number}" for number in range(8)),
                              *(f"A{number}" for number in range(8))],
        },
        "verified_method_coverage": verified_methods,
        "verified_review_coverage": verified_reviews,
        "verified_grammar_sequence": verified_sequence,
        "verified_command_review_coverage": command_reviews,
        "required_mastery_review_coverage": required_mastery_reviews,
    }


def validate(cur):
    errors = []
    modules, cards, questions = cur["modules"], cur["cards"], cur["questions"]
    module_map = {module["id"]: module for module in modules}
    stage_ids = [stage.get("id") for stage in cur.get("stages", [])]
    expected_stage_ids = [*MAIN_STAGE_SEQUENCE, "P"]
    if cur.get("main_stage_sequence") != MAIN_STAGE_SEQUENCE:
        errors.append("main stage sequence must be exactly S0-S7 then A0-A7")
    if stage_ids != expected_stage_ids:
        errors.append("stage records must be S0-S7, A0-A7, then optional P")
    stage_map = {stage.get("id"): stage for stage in cur.get("stages", [])}
    all_stage_cards = []
    for index, stage_id in enumerate(MAIN_STAGE_SEQUENCE):
        stage = stage_map.get(stage_id, {})
        expected_prerequisites = [] if index == 0 else [MAIN_STAGE_SEQUENCE[index - 1]]
        if stage.get("prerequisites") != expected_prerequisites:
            errors.append(f"{stage_id}: stage prerequisite is not the prior main stage")
        if stage.get("optional") is not False or stage.get("track") not in {
                "still", "animation"}:
            errors.append(f"{stage_id}: main stage metadata is invalid")
        if not stage.get("card_ids") or not stage.get("required_review_card_ids"):
            errors.append(f"{stage_id}: needs executable cards and a spaced-review gate")
        all_stage_cards.extend(stage.get("card_ids", []))
    proportional = stage_map.get("P", {})
    if (proportional.get("prerequisites") != ["S5"]
            or proportional.get("optional") is not True
            or proportional.get("track") != "optional"):
        errors.append("P must be an optional branch unlocked by S5")
    all_stage_cards.extend(proportional.get("card_ids", []))
    card_ids = [card["id"] for card in cards]
    if len(all_stage_cards) != len(set(all_stage_cards)) or set(all_stage_cards) != set(card_ids):
        errors.append("every card must belong to exactly one progression stage")
    for card in cards:
        owner = card.get("stage_owner")
        if owner not in stage_map or card.get("master_stages") != [owner]:
            errors.append(f"{card['id']}: stage ownership is absent or still mixed")
    for stage in cur.get("stages", []):
        expected_reviews = [
            card["id"] for card in cards
            if card.get("stage_owner") == stage.get("id")
            and card.get("required_before_mastery")
        ]
        if stage.get("required_review_card_ids") != expected_reviews:
            errors.append(f"{stage.get('id')}: spaced-review gate does not match owned cards")
    # Validate the order learners can actually encounter, not the generator's
    # module-storage order.  P branches after S5; no hidden command may depend
    # on a guide trapped in a later stage.
    reachable_stage_order = [*MAIN_STAGE_SEQUENCE[:6], "P", *MAIN_STAGE_SEQUENCE[6:]]
    first_guided_by_stage = {}
    for stage_id in reachable_stage_order:
        for card in cards:
            if card.get("stage_owner") != stage_id:
                continue
            if card.get("grammar_stage") == "guided":
                for family in card.get("grammar_families", []):
                    first_guided_by_stage.setdefault(family, card["id"])
            elif card.get("grammar_stage") == "hidden":
                for family in card.get("grammar_families", []):
                    if family not in first_guided_by_stage:
                        errors.append(
                            f"{card['id']}: stage path hides {family} before guided performance")
    animation_lessons = cur.get("animation_lesson_pack", [])
    animation_contract = cur.get("animation_lesson_pack_contract", {})
    expected_animation_ids = [f"AL{number:02d}" for number in range(1, 13)]
    if [lesson.get("id") for lesson in animation_lessons] != expected_animation_ids:
        errors.append("animation lesson pack must contain AL01..AL12 in authored order")
    if animation_contract.get("lesson_count") != len(animation_lessons):
        errors.append("animation lesson contract count does not match generated lessons")
    if animation_contract.get("question_count") != 24:
        errors.append("animation lesson pack must retain 24 paired questions")
    animation_cards = {card["id"]: card for card in cards}
    animation_card_order = {card["id"]: index for index, card in enumerate(cards)}
    seen_animation_questions = set()
    for index, lesson in enumerate(animation_lessons):
        lesson_id = lesson.get("id", f"animation-{index}")
        for field in ("title", "source", "source_evidence", "do_this", "target", "hint",
                      "master_habits", "master_stages", "ascii_exercise",
                      "neovim_exercise", "questions", "changed_art_review",
                      "question_audit", "earlier_guided_family_gate", "rights_gate",
                      "delivery"):
            if not lesson.get(field):
                errors.append(f"{lesson_id}: missing live animation lesson field {field}")
        if set(lesson.get("domains", [])) != {"ascii_animation", "neovim"}:
            errors.append(f"{lesson_id}: lesson must name both ASCII animation and Neovim")
        for label, prefix in (("do_this", "DO THIS —"), ("target", "TARGET —"),
                              ("hint", "HINT —")):
            if not lesson.get(label, "").startswith(prefix):
                errors.append(f"{lesson_id}: {label} must be an explicit learner contract")
        ascii_exercise = lesson.get("ascii_exercise", {})
        if not ascii_exercise.get("original") or not ascii_exercise.get("fixed_width"):
            errors.append(f"{lesson_id}: generated art must be original and fixed-width")
        if not ascii_exercise.get("frames"):
            errors.append(f"{lesson_id}: generated lesson has no original art")
        neovim = lesson.get("neovim_exercise", {})
        if neovim.get("guided", {}).get("key_hidden") is not False:
            errors.append(f"{lesson_id}: guided Neovim sequence must be visible")
        if (neovim.get("hidden", {}).get("key_hidden") is not True
                or neovim.get("hidden", {}).get("keys") != "withheld"):
            errors.append(f"{lesson_id}: hidden Neovim sequence must withhold keys")
        review = lesson.get("changed_art_review", {})
        if not review.get("hidden") or review.get("variant_count", 0) < 2:
            errors.append(f"{lesson_id}: changed-art review needs two hidden variants")
        if lesson.get("question_audit") != {
                "student_can_answer_from_prior_teaching": True,
                "request_is_clear": True,
                "placement_makes_sense": True}:
            errors.append(f"{lesson_id}: question audit must affirm prior teaching, clarity, and placement")
        rights = lesson.get("rights_gate", {})
        if (rights.get("integration") != "blocked"
                or rights.get("source_art_used") is not False
                or rights.get("original_art_only") is not True):
            errors.append(f"{lesson_id}: unresolved source-art boundary is not closed")
        delivery = lesson.get("delivery", {})
        guided_id, hidden_id = delivery.get("guided_card_id"), delivery.get("hidden_card_id")
        if guided_id not in animation_cards or hidden_id not in animation_cards:
            errors.append(f"{lesson_id}: delivery cards are missing")
        else:
            guided_card, hidden_card = animation_cards[guided_id], animation_cards[hidden_id]
            if animation_card_order[guided_id] >= animation_card_order[hidden_id]:
                errors.append(f"{lesson_id}: hidden delivery card precedes guided delivery")
            if guided_card.get("grammar_stage") != "guided":
                errors.append(f"{lesson_id}: guided delivery card is not a guided stage")
            if hidden_card.get("grammar_stage") != "hidden":
                errors.append(f"{lesson_id}: hidden delivery card is not a hidden stage")
            question_ids = {question.get("id") for question in lesson.get("questions", [])}
            for delivery_card in (guided_card, hidden_card):
                if set(delivery_card.get("animation_pack_question_ids", [])) != question_ids:
                    errors.append(f"{lesson_id}: paired questions are not attached to delivery cards")
            gate = lesson.get("earlier_guided_family_gate", {})
            if (gate.get("guided_card_id") != guided_id
                    or gate.get("hidden_card_id") != hidden_id
                    or gate.get("hidden_after_guided") is not True
                    or not set(guided_card.get("grammar_families", []))
                    <= set(gate.get("guided_families", []))):
                errors.append(f"{lesson_id}: earlier-guided-family gate is incomplete")
        lesson_questions = lesson.get("questions", [])
        if len(lesson_questions) != 2:
            errors.append(f"{lesson_id}: paired lesson questions must number two")
        for question_row in lesson_questions:
            question_id = question_row.get("id", "unknown")
            if question_id in seen_animation_questions:
                errors.append(f"{question_id}: duplicate animation question id")
            seen_animation_questions.add(question_id)
            for field in ("animation_prompt", "animation_answer", "neovim_prompt",
                          "neovim_answer", "answer_format", "paired_answer_format",
                          "prior_teaching_basis", "clarity_check", "placement_rationale"):
                if not question_row.get(field):
                    errors.append(f"{question_id}: missing paired answer field {field}")
            if question_row.get("placement") not in ("before", "after"):
                errors.append(f"{question_id}: placement must be before or after")
            if not question_row.get("explicit_answer", "").startswith("ANIMATION:"):
                errors.append(f"{question_id}: explicit paired answer is missing")
    if len(seen_animation_questions) != 24:
        errors.append("animation lesson question ids must number 24")
    if {habit for lesson in animation_lessons for habit in lesson.get("master_habits", [])} != {
            f"H{number}" for number in range(1, 10)}:
        errors.append("animation lessons must cover H1-H9")
    if {stage for lesson in animation_lessons for stage in lesson.get("master_stages", [])} != {
            *(f"S{number}" for number in range(8)), *(f"A{number}" for number in range(8))}:
        errors.append("animation lessons must cover S0-S7 and A0-A7")
    legacy_ids = [lesson["id"] for card in cards for lesson in card.get("legacy_lessons", [])]
    expected_legacy = set(LEGACY_CARD_MAP)
    if set(legacy_ids) != expected_legacy or len(legacy_ids) != len(expected_legacy):
        errors.append("legacy lesson teaching payloads must attach exactly once: %r" % legacy_ids)

    def check_visual(card_id, label, rows, frame_rows=None, incomplete_last=None):
        """Reject the one-glyph/toy stimuli that prompted the 2026-09-27 audit."""
        if not rows:
            errors.append(f"{card_id}: {label} is empty")
            return
        frames = ([rows[index:index + frame_rows] for index in range(0, len(rows), frame_rows)]
                  if frame_rows else [rows])
        for index, frame in enumerate(frames, 1):
            if (incomplete_last and index == len(frames)
                    and incomplete_last.get("frame") == index
                    and incomplete_last.get("missing_rows") == frame_rows - len(frame)
                    and incomplete_last.get("reason")):
                # A guided missing-row exercise intentionally begins with one
                # partial final pose.  The finished target is still checked as
                # full multi-row art below.
                continue
            nonblank = [row for row in frame if row.strip()]
            ink = sum(sum(not char.isspace() for char in row) for row in frame)
            width = max((len(row.rstrip()) for row in frame), default=0)
            if len(nonblank) < 3 or ink < 7 or width < 5:
                errors.append(
                    f"{card_id}: {label} frame {index} is a toy stimulus "
                    f"(nonblank_rows={len(nonblank)}, ink={ink}, width={width})")
    if len(modules) != 20: errors.append(f"expected 20 modules, got {len(modules)}")
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
    expected_required_reviews = [{
        "module_id": card["module_id"],
        "source_card_id": card["id"],
        "method_label": card["method_requirement"]["label"],
        "changed_art_variants": len(card.get("variants") or card.get("review_variants") or []),
        "keys_hidden": card.get("show_recipe") is False,
        "required_before_mastery": True,
        "evidence": "method-required hidden transfer plus changed-art spaced review",
    } for card in cards if card.get("required_before_mastery")]
    if cur.get("required_mastery_review_coverage") != expected_required_reviews:
        errors.append("required mastery-review coverage does not match enforced transfer reviews")
    for q in questions:
        if not q.get("source_ref"): errors.append(f"{q['id']}: missing source reference")
        if q.get("form") != "multiple_choice":
            errors.append(f"{q['id']}: every learner question must be four-choice multiple choice")
        if ("ANIMATION\n" not in q.get("prompt", "")
                or "NEOVIM\n" not in q.get("prompt", "")):
            errors.append(f"{q['id']}: prompt does not visibly pair animation and Neovim")
        for field in ("card_id", "form", "grammar_family", "grammar_breakdown_id",
                      "paired_invariant", "placement", "placement_reason", "answer_contract"):
            if not q.get(field): errors.append(f"{q['id']}: missing paired-question field {field}")
        if q.get("form") == "multiple_choice" and q.get("choices"):
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
            if ("ANIMATION" not in q.get("compact_prompt", "")
                    or "NEOVIM" not in q.get("compact_prompt", "")):
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
    def contains_ascii_visual(value):
        if "│" in value:
            return True
        for block in value.split("\n\n"):
            art_rows = []
            for line in block.splitlines():
                punctuation = sum(not char.isalnum() and not char.isspace()
                                  for char in line)
                non_ascii = sum(ord(char) > 127 for char in line)
                if punctuation >= 2 or non_ascii >= 2:
                    art_rows.append(line)
            if len(art_rows) >= 2:
                return True
        return False

    if any(not contains_ascii_visual(q["prompt"])
           or not contains_ascii_visual(q.get("compact_prompt", ""))
           for q in mc_questions):
        errors.append("every multiple-choice question must print ASCII-art evidence")
    for q in mc_questions:
        if len(set(q["choices"])) != 4:
            errors.append(f"{q['id']}: all four answer choices must be distinct")
    nodes = [module["node"] for module in modules]
    if len(nodes) != len(set(nodes)) or not any(node.startswith("A3/") for node in nodes):
        errors.append("skill-tree nodes must be unique and the A3 stage must be assigned")
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
        expected_mode = ARTIFACT_MODE_BY_STAGE.get(card.get("stage_owner"))
        if card.get("artifact_mode") != expected_mode:
            errors.append(
                f"{card['id']}: artifact_mode {card.get('artifact_mode')!r} does not match "
                f"stage {card.get('stage_owner')} ({expected_mode!r})")
        if card.get("stage_owner", "").startswith("S") and card.get("artifact_mode") == "animation-strip":
            errors.append(f"{card['id']}: still stage cannot contain an animation-strip card")
        if (card.get("stage_owner", "").startswith("S")
                and re.search(r"\b(animation|playback|loop|tween|frame|motion)\b",
                              card.get("prompt", ""), re.IGNORECASE)):
            errors.append(
                f"{card['id']}: still-stage prompt uses temporal authoring language")
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
        if card.get("required_before_mastery"):
            variants = card.get("review_variants") or card.get("variants") or []
            if (card.get("grammar_stage") != "hidden"
                    or card.get("show_recipe") is not False
                    or not card.get("method_requirement")
                    or len(variants) < 2
                    or any(not variant.get("method_requirement") for variant in variants)):
                errors.append(
                    f"{card['id']}: required mastery review needs hidden method evidence and two enforced variants")
        if card.get("start"):
            frame_rows = card.get("frame_rows", module_map[card["module_id"]].get("frame_rows"))
            check_visual(card["id"], "start", card["start"], frame_rows,
                         card.get("incomplete_start_frame"))
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
                            f"{card['id']}: review variant {index} expected keys are not a declared method")
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
                if index > 1 and not variant.get("paired_question_ids"):
                    errors.append(
                        f"{card['id']}: transfer variant {index} inherits a mismatched question")
                for qid in variant.get("paired_question_ids", []):
                    if qid not in qids:
                        errors.append(
                            f"{card['id']}: transfer variant {index} lacks paired question {qid}")
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
