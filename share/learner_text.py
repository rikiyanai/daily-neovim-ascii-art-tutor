"""Inspect authored learner prose without rewriting it or touching metadata."""
import re

JARGON = re.compile(r"\b(?:Ex|address(?:es|ed|ing)?)\b", re.IGNORECASE)
BROKEN_ENGLISH = re.compile(r"scope marker|\ban command-line\b", re.IGNORECASE)
PROSE_FIELDS = (
    "title", "prompt", "compact_prompt", "hint", "roadmap_contract",
    "lesson_benefit", "key_vocabulary", "key_shape", "teaching_lines", "recipe",
    "animation_prompt", "animation_answer", "neovim_prompt", "neovim_answer",
    "choices", "compact_choices", "feedback", "grammar_breakdown",
    "principle", "basic", "scaled", "meaning", "defect", "first_reading",
)


def strings(value, path):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from strings(item, f"{path}[{index}]")


def learner_prose(cur):
    for kind in ("stages", "modules", "cards", "questions"):
        for row in cur.get(kind, []):
            yield from row_prose(row, row["id"])


def row_prose(row, path):
    for field in PROSE_FIELDS:
        yield from strings(row.get(field), f"{path}.{field}")
    for field in ("method_requirement", "method_alternatives"):
        methods = row.get(field, [])
        if isinstance(methods, dict):
            methods = [methods]
        for index, method in enumerate(methods):
            for key in ("label", "why"):
                yield from strings(method.get(key), f"{path}.{field}[{index}].{key}")
    for field in ("review_variants", "variants"):
        for index, variant in enumerate(row.get(field, [])):
            yield from row_prose(variant, f"{path}.{field}[{index}]")


def prose_issue(text):
    match = BROKEN_ENGLISH.search(text) or JARGON.search(text)
    return match.group(0) if match else None


def learner_text_failures(cur):
    return [(path, issue) for path, text in learner_prose(cur)
            if (issue := prose_issue(text))]
