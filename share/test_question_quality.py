"""VD-28 gate: judge questions by the text the learner actually sees.

Earlier gates checked only form (four choices, `A:`/`V:` markers, raw strings
distinct).  They passed a bank in which the displayed choices collapsed to two
strings, the answer was findable by boilerplate wording, the correct answer
restated the prompt, and a before-edit question printed the hidden recipe.

Usage: python3 share/test_question_quality.py [curriculum.json]
Exit 1 with a per-rule report when any rule fails.
"""
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import v2_runtime as v2  # noqa: E402
import learner_text  # noqa: E402
import v2_keys  # noqa: E402

cur = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else HERE / "curriculum-v2.json")
                 .read_text(encoding="utf-8"))
cards = {card["id"]: card for card in cur["cards"]}

# Generator vocabulary no lesson teaches; each came from a fill-in template.
BANNED = [
    "makes only its named change", "named defect", "accepts the module's",
    "stated scope stays", "This visible failure occurs",
    "performs the bounded edit", "registration contract",
]
# Curriculum-author and runtime labels are not teaching language. These were
# found only after reading the authored records and seeing the operator's
# failed-result page; this gate prevents those exact regressions after the
# manual corrections, rather than attempting to judge prose quality itself.
INTERNAL_BANNED = [
    "question replay", "concept replay", "hidden artifact recipe",
    "hidden recipe", "mastery strip", "checkpoint statement",
    "checkpoint claim", "this card exists", "method evidence",
    "checkpoint requires", "artifact subpart", "source contract",
]
INTERNAL_PATTERN = re.compile(
    r"\b(?:card|module|curriculum)\b|"
    r"\bM\d+(?:\.[A-Z0-9]+)+\b|\bvariant\s+\d+\b",
    re.IGNORECASE,
)
# Popup interior widths: 90% of an 80, 100 and 188 column client.
POPUP_COLUMNS = (72, 90, 169)
MAX_WRONG_HALF_REUSE = 3

failures = collections.defaultdict(list)

# Negative controls cover both the normal lesson and the less-visible review
# and compact-question surfaces. A green scan must exercise the rejection.
for phrase in ("scope marker", "an command-line substitute", "Ex command",
               "line address", "addressed row", "addresses column 12"):
    fixture = {"cards": [{"id": "fixture", "variants": [{"hint": phrase}]}],
               "questions": [{"id": "fixture.P01", "compact_choices": [phrase]}]}
    assert len(learner_text.learner_text_failures(fixture)) == 2, phrase
assert not learner_text.prose_issue("Select row 2; type :2s/o/O/g and press Enter.")
failures["learner wording regression"].extend(
    "%s: %r" % row for row in learner_text.learner_text_failures(cur))
for (symbol, role), (meaning, short) in v2_keys.SYMBOL_ROLES.items():
    for text in (meaning, short):
        if issue := learner_text.prose_issue(text):
            failures["learner wording regression"].append(f"symbol {symbol}/{role}: {issue!r}")
for table in (v2_keys.FAMILY_TEACH, v2_keys.EXAMPLES):
    for family, text in table.items():
        if issue := learner_text.prose_issue(text):
            failures["learner wording regression"].append(f"key teaching {family}: {issue!r}")


def norm(text):
    return re.sub(r"[\W_]+", " ", str(text)).strip().lower()


def halves(choice):
    if " | NEOVIM: " in choice:
        animation, neovim = choice.split(" | NEOVIM: ", 1)
        return animation.removeprefix("ANIMATION: "), neovim
    return None, choice


def has_art(text):
    """Require visible multi-row glyph evidence, not an art-related noun."""
    if "│" in text:
        return True
    for paragraph in text.split("\n\n"):
        rows = []
        for line in paragraph.splitlines():
            punctuation = sum(not char.isalnum() and not char.isspace()
                              for char in line)
            non_ascii = sum(ord(char) > 127 for char in line)
            if punctuation >= 2 or non_ascii >= 2:
                rows.append(line)
        if len(rows) >= 2:
            return True
    return False


half_use = collections.defaultdict(set)
for q in cur["questions"]:
    if q.get("form") != "multiple_choice":
        continue
    qid, choices = q["id"], q["choices"]
    if q.get("authorship") != "manual":
        failures["not explicitly authored"].append(qid)
    for field in ("prompt", "compact_prompt"):
        if not has_art(q.get(field, "")):
            failures["missing visible art"].append("%s.%s" % (qid, field))
    compact_lines = (
        len(v2._compact_question_text(q["compact_prompt"]).splitlines())
        + sum(len(v2._compact_choice_text(choice, width=72).splitlines())
              for choice in q["compact_choices"])
        + 3
    )
    if compact_lines > 22:
        failures["80-column screen overflow"].append(
            "%s: %d estimated lines" % (qid, compact_lines))
    text = " ".join(choices + q.get("feedback", []))
    for phrase in BANNED:
        if phrase in text:
            failures["template phrase"].append("%s: %r" % (qid, phrase))
            break
    learner_text = " ".join(str(q.get(field, "")) for field in (
        "prompt", "compact_prompt", "animation_prompt", "animation_answer",
        "neovim_prompt", "neovim_answer",
    )) + " " + text
    for phrase in INTERNAL_BANNED:
        if phrase in learner_text.casefold():
            failures["internal workflow prose"].append("%s: %r" % (qid, phrase))
            break
    match = INTERNAL_PATTERN.search(learner_text)
    if match:
        failures["internal workflow prose"].append(
            "%s: %r" % (qid, match.group(0)))
    for columns in POPUP_COLUMNS:
        width = max(42, min(78, columns - 8))
        shown = [v2._compact_choice_text(choice, width=width) for choice in choices]
        if len(set(shown)) != len(shown):
            failures["choices identical as displayed"].append("%s @%d cols" % (qid, columns))
            break
    card = cards.get(q.get("card_id"), {})
    correct_animation, correct_neovim = halves(choices[q["correct_choice"]])
    if correct_animation and card.get("prompt") and (
            norm(correct_animation) == norm(card["prompt"])
            or norm(correct_animation) == norm(q.get("animation_prompt", ""))):
        failures["correct answer restates the prompt"].append(qid)
    expected = card.get("expected")
    if (q.get("placement") == "before" and expected and card.get("show_recipe") is False
            and any(expected in choice for choice in choices)):
        failures["before-question reveals hidden recipe"].append("%s: %s" % (qid, expected))
    for index, choice in enumerate(choices):
        if index == q["correct_choice"]:
            continue
        animation, neovim = halves(choice)
        for half in (animation, neovim):
            if half and len(half) > 12:
                half_use[norm(half)].add(qid)

for half, qids in half_use.items():
    if len(qids) > MAX_WRONG_HALF_REUSE:
        failures["wrong half reused across questions"].append(
            "%d questions: %s…" % (len(qids), half[:60]))

feedback_use = collections.defaultdict(list)
for q in cur["questions"]:
    for index, message in enumerate(q.get("feedback", [])):
        feedback_use[message].append("%s[%d]" % (q["id"], index))
for message, locations in feedback_use.items():
    if len(locations) > 1:
        failures["feedback reused verbatim"].append(
            "%s: %s" % (", ".join(locations), message[:80]))

total = sum(1 for q in cur["questions"] if q.get("form") == "multiple_choice")
if any(failures.values()):
    for rule, rows in failures.items():
        print("FAIL %-40s %4d  e.g. %s" % (rule, len(rows), "; ".join(rows[:3])))
    print("questions checked: %d" % total)
    sys.exit(1)
print("PASS all question-quality rules on %d multiple-choice questions" % total)
