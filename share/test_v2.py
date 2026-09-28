#!/usr/bin/env python3
"""Structural, scheduler, and real-Neovim checks for curriculum v2."""

import importlib.util
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("v2_runtime", HERE / "v2_runtime.py")
v2 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v2
spec.loader.exec_module(v2)

generator_spec = importlib.util.spec_from_file_location(
    "v2_curriculum_generator", HERE / "gen_curriculum_v2.py")
generator = importlib.util.module_from_spec(generator_spec)
generator_spec.loader.exec_module(generator)

keys_spec = importlib.util.spec_from_file_location("v2_keys", HERE / "v2_keys.py")
v2_keys = importlib.util.module_from_spec(keys_spec)
keys_spec.loader.exec_module(v2_keys)

gate_spec = importlib.util.spec_from_loader(
    "legacy_gate", importlib.machinery.SourceFileLoader(
        "legacy_gate", str(HERE.parent / "bin" / "vim-daily-gate")))
legacy_gate = importlib.util.module_from_spec(gate_spec)
gate_spec.loader.exec_module(legacy_gate)


def tokenize(value):
    out, i = [], 0
    while i < len(value):
        if value[i] == "<":
            match = re.match(r"<(?:[A-Za-z]-)?[A-Za-z0-9]+>", value[i:])
            if match:
                out.append(match.group(0))
                i += len(match.group(0))
                continue
        out.append(value[i])
        i += 1
    return out


SPECIAL = {"<Esc>": b"\x1b", "<CR>": b"\r", "<NL>": b"\n", "<Tab>": b"\t", "<BS>": b"\x7f"}


def to_bytes(value):
    data = b""
    for token in tokenize(value):
        if token in SPECIAL:
            data += SPECIAL[token]
        elif re.fullmatch(r"<C-([A-Za-z])>", token):
            data += bytes([ord(token[3].lower()) - 0x60])
        else:
            data += token.encode("utf-8")
    return data


def answer_question(question):
    if question.get("choices"):
        return "abcd"[question["correct_choice"]]
    return question["answer_contract"]["sample_answer"]


with (HERE / "curriculum-v2.json").open(encoding="utf-8") as f:
    cur = json.load(f)
v2.validate_curriculum(cur)
assert generator.build() == cur, "generated artifact drifted from gen_curriculum_v2.py"
use_real = "--real" in sys.argv

# Every legacy lesson contributes its original key vocabulary, concept prose,
# benefit, and exact source to one mapped v2 animation card. Mapping does not
# award v2 mastery and does not claim the 16 command-family gaps are closed.
legacy_source = json.loads((HERE / "curriculum.json").read_text(encoding="utf-8"))
legacy_drills = {drill["id"]: drill for drill in legacy_source["drills"]}
legacy_payloads = {
    lesson["id"]: lesson
    for card in cur["cards"] for lesson in card.get("legacy_lessons", [])
}
assert set(legacy_payloads) == set(legacy_drills) and len(legacy_payloads) == 46
for legacy_id, drill in legacy_drills.items():
    payload = legacy_payloads[legacy_id]
    concept = legacy_source["concepts"][drill["concept"]]
    assert payload["keys"] == drill["keys"]
    assert payload["source"] == drill["source"]
    assert payload["buys"] == drill["buys"]
    assert payload["paradigm"] == concept["paradigm"]

assert len(cur["modules"]) == 19
assert len(cur["cards"]) == 174
assert len(cur["questions"]) == 326
assert len({card["title"] for card in cur["cards"]}) == 174
assert len({card["prompt"] for card in cur["cards"]}) == 174
card_by_id = {card["id"]: card for card in cur["cards"]}
question_by_id = {question["id"]: question for question in cur["questions"]}
mc_questions = [question for question in cur["questions"]
                if question["form"] == "multiple_choice"]
assert {question["form"] for question in cur["questions"]} == {
    "multiple_choice", "typed_keys", "decode", "complete", "predict_art", "why"}
assert all(card.get("paired_question_ids") for card in cur["cards"])
assert all(qid in question_by_id
           for card in cur["cards"] for qid in card["paired_question_ids"])

# A generic why contract let the same stock sentence pass all 19 comparison
# cards. Every comparison must instead ask about—and grade—the two methods and
# animation scope on that exact card.
why_questions = [question for question in cur["questions"] if question["form"] == "why"]
assert len(why_questions) == 19
assert len({question["prompt"] for question in why_questions}) == 19
assert len({json.dumps(question["answer_contract"], sort_keys=True)
            for question in why_questions}) == 19
for question in why_questions:
    right, missing = v2._term_group_result(
        question["answer_contract"]["sample_answer"],
        question["answer_contract"]["required_term_groups"])
    assert right and not missing, (question["id"], missing)

# Metadata tags cannot hide a prerequisite failure. Scan command-looking text
# quoted by every before-question and require its parsed key families to have
# appeared in earlier visible guided performance (the primer explicitly owns
# only counted j). This catches the old M0.P0 3daw/rO/:s interrogation even if
# somebody labels it merely "vim-language-primer" again.
def normalized_key_family(family):
    family = family.replace(":[range]", ":")
    return "r{char}" if family == "r" else family


taught_quoted_families = {"[count]j"}
single_key_commands = set("hjklwWeEbB0$^G{};,xJDu~%") | {"r"}
for card in cur["cards"]:
    for question_id in card.get("question_placement", {}).get("before", []):
        question = question_by_id[question_id]
        for quoted in re.findall(r"`([^`]+)`", question.get("prompt", "")):
            key_like = (quoted.startswith((":", "/", "?")) or "<" in quoted
                        or bool(re.match(r"\d", quoted)) or quoted in single_key_commands)
            if not key_like or quoted.startswith("["):
                continue
            # `<C-r>a` is register insertion inside the Replace-mode sentence
            # taught on M14.01; parsing it as a standalone Normal command would
            # misread the trailing register name as `a` Insert mode.
            families = ({"R{text}<Esc>"} if quoted == "<C-r>a" else
                        {normalized_key_family(family)
                         for family, _meaning in v2_keys.families(quoted)})
            unknown = families - taught_quoted_families
            assert not unknown, (card["id"], question_id, quoted, sorted(unknown))
    if card.get("grammar_stage") == "guided" and card.get("expected"):
        taught_quoted_families.update(
            normalized_key_family(family)
            for family, _meaning in v2_keys.families(card["expected"]))
assert [card["id"] for card in cur["cards"] if card["module_id"] == "M0"] == [
    "M0.P0", "M0.01", "M0.02", "M0.O", "M0.03", "M0.04",
    "M0.T", "M0.05", "M0.SL", "M0.06", "M0.07", "M0.08"]
# M0.04 must not demand substitution before it has been shown. M0.02 is the
# guided introduction; M0.04 names the family but keeps its exact line/keys
# hidden as retrieval practice.
assert card_by_id["M0.02"]["kind"] == "guided_edit"
assert card_by_id["M0.02"]["expected"] == "gg3yyGp:4,6s/o/O/g<CR>"
assert any(":{start},{end}s/old/new/g" in line and "g means all matches" in line
           for line in card_by_id["M0.02"]["key_vocabulary"])
assert card_by_id["M0.04"]["show_recipe"] is False
assert any(":{start},{end}s/old/new/g" in line
           for line in card_by_id["M0.04"]["key_vocabulary"])
assert "USE ONE METHOD" in card_by_id["M0.05"]["prompt"]
assert {method["evidence"]["kind"] for method in
        card_by_id["M0.05"]["method_alternatives"]} == {
            "linewise_yank_put", "ex_copy"}
assert all(len(q["choices"]) == 4 and len(q["feedback"]) == 4
           for q in mc_questions)
assert all(all(q.get(field) for field in (
    "animation_prompt", "animation_answer", "neovim_prompt", "neovim_answer"))
           for q in mc_questions)
assert all("ANIMATION\n" in q["prompt"] and "NEOVIM\n" in q["prompt"]
           and all("ANIMATION:" in choice and "NEOVIM:" in choice
                   for choice in q["choices"])
           for q in mc_questions)
assert all("ANIMATION:" in q["compact_prompt"] and "NEOVIM:" in q["compact_prompt"]
           and len(q["compact_choices"]) == len(q["choices"])
           and all("A:" in choice and "V:" in choice for choice in q["compact_choices"])
           for q in mc_questions)
assert all(q["type"] == "output_prediction" and len(q["choices"]) == 4
           for q in cur["questions"] if q["id"].endswith("Q09"))
assert len({q["animation_prompt"].split("\n\n", 1)[0].casefold()
            for q in mc_questions}) == len(mc_questions) == 191
assert sum("│" in q["animation_prompt"] for q in mc_questions) >= 55
assert all("Not yet" not in feedback and "one or both halves" not in feedback.lower()
           for q in mc_questions for feedback in q["feedback"])
for q in mc_questions:
    animation_halves = [choice.split(" | NEOVIM: ", 1)[0] for choice in q["choices"]]
    neovim_halves = [choice.split(" | NEOVIM: ", 1)[1] for choice in q["choices"]]
    assert sorted(animation_halves.count(value) for value in set(animation_halves)) == [2, 2]
    assert sorted(neovim_halves.count(value) for value in set(neovim_halves)) == [2, 2]
nodes = [module["node"] for module in cur["modules"]]
assert len(nodes) == len(set(nodes)) and "A3/V4" in nodes
assert all(card.get("animation", {}).get("pivot") == "column 4"
           for card in cur["cards"] if card["module_id"] == "M4" and card.get("animation"))
assert all(all(module.get(field) for field in
               ("meaning", "first_reading", "principle", "defect", "basic", "scaled", "source_ref"))
           for module in cur["modules"])
for question in [q for q in cur["questions"] if q["id"].endswith("Q01") and q["module_id"] != "M10"]:
    assert "BEFORE" in question["prompt"] and "AFTER" in question["prompt"]
    assert question["prompt"].count("│") >= 6, question["id"]
assert all([c["ordinal"] for c in cur["cards"]
            if c["module_id"] == m["id"] and re.fullmatch(r"M\d+\.\d\d", c["id"])]
           == list(range(1, 9)) for m in cur["modules"])
assert all(len(c.get("question_ids", [])) == 10
           for c in cur["cards"] if c["kind"] == "module_check")
assert all("key-hidden" in c["prompt"] and c["expected"] not in c["prompt"]
           and all(why not in c["prompt"] for _keys, why in c["recipe"])
           for c in cur["cards"] if c["kind"] == "module_check")
assert all(c.get("question_ids", []) == [c["module_id"] + ".Q01",
                                          c["module_id"] + ".Q02"]
           for c in cur["cards"] if c["kind"] == "concept" and c["id"].endswith(".03"))
assert all(len(c.get("question_ids", [])) == 5
           for c in cur["cards"] if c["kind"] == "concept" and c["id"].endswith(".07"))
assert card_by_id["M0.P0"]["question_ids"] == ["M0.P0.P01"]
primer_question = question_by_id["M0.P0.P01"]
assert primer_question["form"] == "multiple_choice"
assert "5j" in primer_question["prompt"]
assert not any(token in primer_question["prompt"] for token in ("3daw", "rO", ":8s/"))
assert any("4j" in line and "down four" in line
           for line in card_by_id["M0.P0"]["teaching_lines"])
for guided in [c for c in cur["cards"] if c.get("grammar_stage") == "guided"]:
    paired = question_by_id[guided["paired_question_ids"][0]]
    assert paired["placement"] == "after", guided["id"]
    assert paired["form"] != "typed_keys", guided["id"]
# Concept cards before the later guided bridges may only ask about their two
# preceding guided edits. Later material stays available in .07/check cards.
future_before_guidance = {
    "M0.Q06", "M0.Q07", "M0.Q09", "M1.Q03", "M1.Q09", "M2.Q09",
    "M3.Q04", "M3.Q06", "M3.Q09", "M6.Q03", "M6.Q06", "M6.Q09",
    "M7.Q03", "M7.Q06", "M7.Q09", "M11.Q04", "M11.Q08", "M12.Q04",
    "M13.Q04", "M13.Q06", "M14.Q08",
}
early_concept_questions = {
    qid for card in cur["cards"] if card["kind"] == "concept" and card["id"].endswith(".03")
    for qid in card.get("question_ids", [])
}
assert not (future_before_guidance & early_concept_questions)
assert all("roadmap_contract" in c and "catalog_contract" not in c for c in cur["cards"])
edit_signatures = [(tuple(c["start"]), tuple(c["target"]))
                   for c in cur["cards"] if c.get("start")]
assert len(edit_signatures) == len(set(edit_signatures))
animation_roles = {c.get("animation", {}).get("role") for c in cur["cards"]}
assert {"extremes", "midpoint-tween", "hold", "contact-keyframe",
        "finished-keyframe"}.issubset(animation_roles)
# Every adjacent identical frame is classified as a playback hold or an
# authoring-only state; no duplicate can hide behind an unannotated final buffer.
module_map = {module["id"]: module for module in cur["modules"]}
for card in cur["cards"]:
    frame_rows = module_map[card["module_id"]].get("frame_rows")
    if not frame_rows or not card.get("target"):
        continue
    frames = [card["target"][index:index + frame_rows]
              for index in range(0, len(card["target"]), frame_rows)]
    actual_pairs = [[index + 1, index + 2]
                    for index in range(len(frames) - 1)
                    if frames[index] == frames[index + 1]]
    declared = card.get("duplicate_frames", [])
    assert [row["frames"] for row in declared] == actual_pairs, card["id"]
    assert all(row["reason"] and "playback" in row for row in declared)
    assert all(row.get("duration_frames", 0) >= 2 and row["playback"] is True
               for row in declared if row["role"] == "hold")
# Coverage is counted only where the runtime grades the demonstrated method.
# Merely placing a command in an answer key is not coverage.
verified = cur["verified_method_coverage"]
assert verified and all(row["card_id"] and row["label"] and row["evidence"] for row in verified)
expected_verified = []
for card in cur["cards"]:
    if card.get("method_requirement"):
        expected_verified.append((card["id"], card["method_requirement"]["label"]))
    expected_verified.extend((card["id"], taught["label"])
                             for taught in card.get("method_alternatives", []))
assert [(row["card_id"], row["label"]) for row in verified] == expected_verified
verified_reviews = cur["verified_review_coverage"]
review_capable = [card for card in cur["cards"]
                  if card.get("review_variants") or card["kind"] == "transfer"]
assert [row["source_card_id"] for row in verified_reviews] == [
    card["id"] for card in review_capable]
assert all(row["method_family"] and row["changed_art_variants"] >= 2
           and row["evidence"] == "source-linked changed-art review bank"
           for row in verified_reviews)
# Command-level spacing is stricter than card-level review counts: every
# family first shown in a visible recipe must return later on changed art with
# its exact keys hidden.  The generator and runtime derive the same contract;
# this assertion makes a missing family fail the focused suite.
command_reviews = cur["verified_command_review_coverage"]
assert command_reviews and all(
    row["grammar_family"] and row["guided_card_id"] and row["review_card_id"]
    and row["changed_art_variants"] >= 2 and row["keys_hidden"] is True
    and row["evidence"] == "runtime-validated source-linked changed-art retrieval"
    for row in command_reviews)
assert {row["grammar_family"] for row in command_reviews} >= {
    "ex-substitute-line", "ex-substitute-range", "char-find-repeat",
    "paragraph-next", "put-before", "visual-characterwise", "block-append",
}
assert all(card_by_id[row["review_card_id"]].get("show_recipe") is False
           for row in command_reviews)
key_paths = "\n".join(card.get("expected", "") for card in cur["cards"])
for padding in ("jwbewbwro", "6GJu04lr.", "13Gma2G'aj", "Go<Esc>I "):
    assert padding not in key_paths
assert next(c for c in cur["cards"] if c["id"] == "M0.01")["method_requirement"]
assert next(c for c in cur["cards"] if c["id"] == "M6.04")["method_requirement"]
m14 = {c["id"]: c for c in cur["cards"] if c["module_id"] == "M14"}
assert "<C-r>a" in m14["M14.01"]["expected"]
assert "yap" in m14["M14.02"]["expected"]
assert any("P" in method["keys"] for method in m14["M14.05"]["method_alternatives"])
assert "}}" in m14["M14.08"]["expected"] and "<C-r>b" in m14["M14.08"]["expected"]
assert all(m14[card_id].get("review_source_card_id") == card_id
           for card_id in ("M14.01", "M14.04", "M14.05", "M14.06", "M14.08"))
m15 = {c["id"]: c for c in cur["cards"] if c["module_id"] == "M15"}
assert "shiftwidth=1" in m15["M15.01"]["expected"] and ">>" in m15["M15.01"]["expected"]
assert ":4s/:/./g" in m15["M15.04"]["expected"]
assert {method["keys"] for method in m15["M15.05"]["method_alternatives"]} == {
    "4G0<C-v>2j$A|<Esc>", ":4,6s/$/|/<CR>"}
assert "qq" in m15["M15.08"]["expected"] and "3@q" in m15["M15.08"]["expected"]
assert all(m15[card_id].get("review_source_card_id") == card_id
           for card_id in ("M15.01", "M15.04", "M15.05", "M15.06", "M15.08"))
m16 = {c["id"]: c for c in cur["cards"] if c["module_id"] == "M16"}
assert "<C-a>" in m16["M16.01"]["expected"]
assert ":read %" in m16["M16.02"]["expected"]
assert ":1,5t$" in m16["M16.04"]["expected"]
assert {method["keys"] for method in m16["M16.05"]["method_alternatives"]} == {
    ":6,10m0<CR>", "6GV4jdggP"}
assert all(m16[card_id].get("review_source_card_id") == card_id
           for card_id in ("M16.01", "M16.02", "M16.04", "M16.05", "M16.06", "M16.08"))
m17 = {c["id"]: c for c in cur["cards"] if c["module_id"] == "M17"}
assert "/x<CR>ron.n." == m17["M17.01"]["expected"]
assert {method["keys"] for method in m17["M17.05"]["method_alternatives"]} == {
    "/o<CR>r*n.n.n.", ":g/o/normal! 0for*<CR>"}
assert "qq" in m17["M17.08"]["expected"] and "3@q" in m17["M17.08"]["expected"]
assert all(m17[card_id].get("review_source_card_id") == card_id
           for card_id in ("M17.01", "M17.05", "M17.06", "M17.08"))
m18 = {c["id"]: c for c in cur["cards"] if c["module_id"] == "M18"}
assert m18["M18.01"]["expected"].count("0C") == 3
assert {method["keys"] for method in m18["M18.05"]["method_alternatives"]} == {
    "4G$r18G$r1",
    ":4s/0/\\=getline(1)=~'<---'?'1':'0'/<CR>:8s/0/\\=getline(5)=~'<---'?'1':'0'/<CR>",
}
assert m18["M18.08"]["expected"] == ":5,8t$<CR>:1,4t$<CR>"
assert m18["M18.08"]["duplicate_frames"][0]["role"] == "hold"
assert all(m18[card_id].get("review_source_card_id") == card_id
           for card_id in ("M18.01", "M18.04", "M18.05", "M18.06", "M18.08"))

sjis_findings = json.loads((HERE / "sjis_corpus_findings.v1.json").read_text(encoding="utf-8"))
assert sjis_findings["schema"] == "vim-daily/sjis-corpus-findings@1"
assert sjis_findings["source_dataset_sha256"] == "61b0537df3a37cd08904f9be09bd0d48a5e78e6a7a57ff2fbd412590289f8258"
assert sjis_findings["coverage"] == {
    "slugs": 114, "pages": 23363, "lines": 457065, "viewable_combinations": 435,
    "page_tags": {"outline": 6542, "tone": 5728, "mixed": 11093},
}
assert sjis_findings["idioms"]["⌒ヽ"]["count"] == 6788
assert sjis_findings["idioms"]["ゝ__ノ"]["slugs"] == 10
assert sjis_findings["whitespace_exceptions"] == {
    "adjacent_half_space_pairs": 147,
    "lines_starting_with_half_space": 78,
    "interpretation": "The no-double/no-leading-half-space rule is a strong convention, not a zero-exception law.",
}
assert sjis_findings["vertical_stacks"]["overscore_over_underscore_0px"] == 5949
assert next(m for m in cur["modules"] if m["id"] == "M10")["medium"] == "proportional-sjis"
assert all(c["medium"] == "proportional-sjis" for c in cur["cards"] if c["module_id"] == "M10")
assert v2._without_brief_navigation(
    ["<C-w>", "k", "G", "<C-w>", "j", "r", "x"]
) == ["r", "x"]

concept_variant = next(c for c in cur["cards"] if c["id"] == "M0.03")
variant_questions = []
for attempt_count in range(5):
    simulated = [{"type": "card", "result": "fail", "card_id": concept_variant["id"],
                  "module_id": "M0"} for _ in range(attempt_count)]
    variant_questions.append(v2._question_for_card(
        cur, v2.project(cur, simulated), concept_variant)["id"])
assert variant_questions == ["M0.Q01", "M0.Q02", "M0.Q01", "M0.Q02", "M0.Q01"]

# A typo at a multiple-choice prompt is neither evidence nor a crash. It must
# reprompt until a valid choice (or EOF) without re-rendering/shuffling.
sample_question = cur["questions"][0]
answers = iter(["x", "", "abcd"[sample_question["correct_choice"]]])
rendered_questions = []
question_evidence = {}
output = io.StringIO()
with contextlib.redirect_stdout(output):
    right, chosen = v2.ask_question(
        sample_question, input_fn=lambda _prompt: next(answers), shuffle=False,
        rendered=lambda q, order: rendered_questions.append((q["id"], order)),
        evidence=question_evidence)
assert right and chosen == sample_question["correct_choice"]
assert output.getvalue().count("did not count as an attempt") == 2
assert len(rendered_questions) == 1
assert question_evidence["displayed_choice_indices"] == list(range(len(sample_question["choices"])))
assert question_evidence["raw_answer"] == "abcd"[sample_question["correct_choice"]]
assert question_evidence["semantic_choice"] == sample_question["correct_choice"]
assert len(question_evidence["question_prompt_sha256"]) == 64

output_prediction = next(q for q in cur["questions"] if q["id"] == "M0.Q09")
assert len(output_prediction["choices"]) == 4
with contextlib.redirect_stdout(io.StringIO()):
    right, chosen = v2.ask_question(
        output_prediction, input_fn=lambda _prompt: "abcd"[output_prediction["correct_choice"]],
        shuffle=False)
assert right and chosen == output_prediction["correct_choice"]

# Typed-key questions are graded by their effect in an isolated Neovim, not
# by string equality. Both valid paths pass; a different resulting glyph does
# not. Question evidence alone never awards card XP.
typed_question = question_by_id["M0.06.P01"]
for equivalent in (typed_question["answer_contract"]["sample_answer"],):
    right, evidence, _message = v2._safe_typed_effect(
        typed_question["answer_contract"], equivalent)
    assert right and evidence["result_lines_sha256"] == evidence["target_lines_sha256"]
wrong, _evidence, _message = v2._safe_typed_effect(
    typed_question["answer_contract"], "j0f.rx")
assert not wrong
wrong_output = io.StringIO()
with contextlib.redirect_stdout(wrong_output):
    right, answer = v2.ask_authored_question(
        typed_question, input_fn=lambda _prompt: "j0f.rx", shuffle=False)
assert not right and answer == "j0f.rx"
assert "GRAMMAR BREAKDOWN" in wrong_output.getvalue()
assert "ANSWER FORMAT" in wrong_output.getvalue()
assert "OTHER EXAMPLE" in wrong_output.getvalue()
assert "ONE WORKING ANSWER" not in wrong_output.getvalue()

# Free-text forms explain their response shape before input. Blank input is a
# recoverable UI mistake, not a failed curriculum attempt, and a real wrong
# answer shows one accepted answer after the grammar breakdown.
decode_question = question_by_id["M0.02.P01"]
decode_answers = iter(["", "operator"])
decode_output = io.StringIO()
with contextlib.redirect_stdout(decode_output):
    right, answer = v2.ask_authored_question(
        decode_question, input_fn=lambda _prompt: next(decode_answers), shuffle=False)
assert not right and answer == "operator"
assert "Blank input did not count as an attempt" in decode_output.getvalue()
assert "ANSWER FORMAT" in decode_output.getvalue()
assert "OTHER EXAMPLE" in decode_output.getvalue()
assert "ONE ACCEPTED ANSWER" not in decode_output.getvalue()
assert decode_question["answer_contract"]["sample_answer"] not in decode_output.getvalue()

# Exact/accepted answers belong on the held correction page, not in transient
# pre-clear output. This prevents a hidden transfer from leaking its recipe
# before evaluation while still leaving a durable worked correction.
held_correction = io.StringIO()
with contextlib.redirect_stdout(held_correction):
    v2._post_feedback_ultra(
        card_by_id["M0.06"],
        {"type": "paired_question", "question": typed_question,
         "answer": "j0f.rx", "right": False},
        False,
        {"source": "test"},
        False, None, "", "")
assert "ONE WORKING ANSWER" in held_correction.getvalue()
assert typed_question["answer_contract"]["sample_answer"] in held_correction.getvalue()
question_only = v2.project(cur, [{
    "type": "question", "result": "pass", "card_id": "M0.01",
    "module_id": "M0", "question_id": typed_question["id"],
}])
assert typed_question["id"] in question_only["passed_questions"]
assert question_only["xp"] == 0 and not question_only["passed_cards"]

# Merely opening and interrupting a popup cannot consume the hourly cooldown.
# append_event advances the stamp only for a durable pass/fail attempt.
with tempfile.TemporaryDirectory() as tmp:
    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=1,
                           target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
                           run_editor=lambda *_: None, decode_keylog=lambda _: [],
                           hold_open=lambda: None, colours=("", "", "", "", "", ""),
                           question_answer=answer_question)
    assert not Path(cfg.stamp).exists()
    v2.append_event(cfg, {"type": "session_open", "card_id": "M0.03"})
    assert not Path(cfg.stamp).exists()
    v2.append_event(cfg, {"type": "question", "result": "fail",
                          "card_id": "M0.03", "module_id": "M0",
                          "question_id": "M0.Q01"})
    assert Path(cfg.stamp).exists()

# Result-page repeat after a pass runs in an isolated practice artifact and
# cannot duplicate ledger, XP, daily, or streak credit.
with tempfile.TemporaryDirectory() as tmp:
    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=1,
                           target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
                           run_editor=lambda *_: None, decode_keylog=lambda _: [],
                           hold_open=lambda: None, colours=("", "", "", "", "", ""),
                           practice=True)
    row = v2.append_event(cfg, {"type": "card", "result": "pass",
                                "card_id": "M0.01", "module_id": "M0"})
    assert row["practice"] is True
    assert not Path(tmp, "events-v2.jsonl").exists()
    v2._legacy_credit(cfg, "M0.01")
    v2._legacy_attempt(cfg, "M0.01")
    assert not list(Path(tmp).glob("*.log"))
    practice_path = v2._artifact_path(cfg, card_by_id["M0.01"])
    assert "sessions/practice" in str(practice_path)

# The held result control visibly offers all three routes. `r` and `n` are
# distinct state transitions; Enter sets neither.
old_popup = os.environ.get("VIM_DAILY_POPUP")
os.environ["VIM_DAILY_POPUP"] = "1"
prompts = []
try:
    legacy_gate._OFFER_NEXT = True
    legacy_gate._NEXT_REQUESTED = False
    legacy_gate._RETRY_REQUESTED = False
    legacy_gate.input = lambda prompt: prompts.append(prompt) or "r"
    legacy_gate.hold_open()
    assert legacy_gate._RETRY_REQUESTED and not legacy_gate._NEXT_REQUESTED
    assert "r = repeat this lesson" in prompts[-1]
    assert "n = next lesson" in prompts[-1]
finally:
    legacy_gate.__dict__.pop("input", None)
    if old_popup is None:
        os.environ.pop("VIM_DAILY_POPUP", None)
    else:
        os.environ["VIM_DAILY_POPUP"] = old_popup

# The user's already-credited one-row-era M0.02 artifact is upgraded only when
# M0.04 starts. Both historical two-line outcomes are recognized, checkpointed,
# and replaced with the revised multi-row start without revoking M0.01/M0.02.
with tempfile.TemporaryDirectory() as tmp:
    migration_card = next(c for c in cur["cards"] if c["id"] == "M0.04")
    assert [" · ", " · "] in migration_card["accepted_legacy_starts"]

    def finish_migrated_artifact(path, *_args):
        Path(path).write_text("\n".join(migration_card["target"]) + "\n", encoding="utf-8")

    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=1,
                           target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
                           run_editor=finish_migrated_artifact, decode_keylog=lambda _: [],
                           hold_open=lambda: None, colours=("", "", "", "", "", ""),
                           question_answer=answer_question)
    artifact = v2._artifact_path(cfg, migration_card)
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(" · \n · \n", encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()):
        assert v2.run_edit(cfg, cur, v2.project(cur, []), migration_card) == 0
    migration_events = [event for event in v2.read_events(cfg)
                        if event.get("type") == "curriculum_migration"]
    assert len(migration_events) == 1
    assert migration_events[0]["curriculum_revision"] == cur["revision"]
    assert (artifact.parent / "checkpoints" / "M0.04-pre-curriculum-migration-2.txt").exists()
    assert artifact.read_text(encoding="utf-8").splitlines() == migration_card["target"]

# Re-extracting tutorial plates must merge, not delete, separately ingested
# user art; the merged library must still generate the legacy curriculum.
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    plate = root / "plate"
    plate.mkdir()
    for name in ("01-sacrificial-pit-layers.txt", "02-poison-adept-walk-cycle.txt",
                 "03-styles-fonts-alphabet.txt", "04-lines-materials-antialiasing.txt",
                 "05-depth-dithering-shadows.txt", "06-animation-subtractive.txt"):
        (plate / name).write_text("\n".join(["x"] * 110) + "\n", encoding="utf-8")
    merged_art = root / "art.json"
    shutil.copy2(HERE / "art.json", merged_art)
    env = dict(os.environ, VIM_DAILY_ART_OUT=str(merged_art))
    subprocess.run([sys.executable, str(HERE / "extract_art.py"), str(plate)],
                   env=env, check=True, stdout=subprocess.DEVNULL)
    merged = json.loads(merged_art.read_text(encoding="utf-8"))
    assert merged["schema"] == "vim-daily/art@2"
    assert all(key in merged["art"] for key in ("ant", "centipede", "cheer", "candle", "cicada"))
    generated = root / "curriculum.json"
    env.update(VIM_DAILY_ART_JSON=str(merged_art), VIM_DAILY_CURRICULUM_OUT=str(generated))
    subprocess.run([sys.executable, str(HERE / "gen_curriculum.py")], env=env,
                   check=True, stdout=subprocess.DEVNULL)
    assert len(json.loads(generated.read_text(encoding="utf-8"))["drills"]) == 46
    intake_source = root / "new-art.txt"
    intake_source.write_text("x\n", encoding="utf-8")
    intake_env = dict(os.environ, VIM_DAILY_ART_JSON=str(merged_art))
    incomplete = subprocess.run(
        [sys.executable, str(HERE / "intake_art.py"), str(intake_source),
         "--key", "new-art", "--block", "0", "--source", "test source"],
        env=intake_env, text=True, capture_output=True)
    assert incomplete.returncode == 1 and "rights metadata is required" in incomplete.stdout
    repository_refusal = subprocess.run(
        [sys.executable, str(HERE / "intake_art.py"), str(intake_source),
         "--key", "must-not-land-in-repo", "--block", "0", "--source", "test source",
         "--author", "unknown", "--license", "unknown",
         "--permission", "not documented", "--redistribution", "unverified"],
        text=True, capture_output=True)
    assert repository_refusal.returncode == 1
    assert "cannot be added to the repository library" in repository_refusal.stdout
    subprocess.run(
        [sys.executable, str(HERE / "intake_art.py"), str(intake_source),
         "--key", "new-art", "--block", "0", "--source", "test source",
         "--author", "test author", "--license", "test license",
         "--permission", "test permission", "--redistribution", "private-only"],
        env=intake_env, check=True, stdout=subprocess.DEVNULL)
    ingested = json.loads(merged_art.read_text(encoding="utf-8"))["art"]["new-art"]
    assert ingested["origin"]["kind"] == "user_download"
    assert ingested["redistribution"] == "private-only"

# An installed symlink still finds checkout data under an alternate XDG root,
# and v1/v2 curriculum overrides are intentionally separate.
with tempfile.TemporaryDirectory() as tmp:
    env = dict(os.environ, XDG_DATA_HOME=str(Path(tmp) / "empty-data"),
               XDG_STATE_HOME=str(Path(tmp) / "state"))
    installed_gate = Path.home() / ".local" / "bin" / "vim-daily-gate"
    assert installed_gate.resolve() == HERE.parent / "bin" / "vim-daily-gate"
    listed = subprocess.run([str(installed_gate), "--list"],
                            env=env, text=True, capture_output=True, check=True)
    assert "M0.01" in listed.stdout and "M13.08" in listed.stdout
    alternate = json.loads(json.dumps(cur))
    alternate["cards"][0]["title"] = "OVERRIDE V2 TITLE"
    alternate_path = Path(tmp) / "alternate-v2.json"
    alternate_path.write_text(json.dumps(alternate), encoding="utf-8")
    env["VIM_DAILY_CURRICULUM_V2"] = str(alternate_path)
    listed = subprocess.run([str(installed_gate), "--list"],
                            env=env, text=True, capture_output=True, check=True)
    assert "OVERRIDE V2 TITLE" in listed.stdout

basic = set("`~!^*()-_+=;:'\",.\\/|<>[]{}")
extended = set("´‾¡·")
alnum = set("oOvVTL7UcCxX")
allowed = basic | extended | alnum | {" "}
for card in cur["cards"]:
    if card.get("labels") or card.get("medium") == "proportional-sjis":
        continue
    for line in card.get("start", []) + card.get("target", []):
        assert not (set(line) - allowed), (card["id"], set(line) - allowed)

# A fresh projection exposes only M0. Mastering it opens both foundation
# branches instead of pretending the curriculum is one long linear list.
p = v2.project(cur, [])
assert p["modules"]["M0"]["state"] == "available"
assert p["modules"]["M1"]["state"] == "locked"
assert p["modules"]["M2"]["state"] == "locked"
assert v2.next_card(cur, p)["id"] == "M0.P0"
# Level progression remains monotonic and bounded within each 80-XP band even
# after the old ten-title ceiling and the full course/review XP maximum.
level_samples = [v2._level(xp) for xp in range(0, 2801)]
assert all(level_samples[index][0] <= level_samples[index + 1][0]
           for index in range(len(level_samples) - 1))
assert all(0 <= into < needed for _level, _title, into, needed in level_samples)
assert v2._level(800)[0] == 11 and v2._level(800)[2] == 0
events = [{"type": "card", "result": "pass", "card_id": card_id,
           "module_id": "M0", "at": "2026-09-27T00:00:00+00:00"}
          for card_id in next(module for module in cur["modules"]
                              if module["id"] == "M0")["card_ids"]]
p = v2.project(cur, events)
assert p["modules"]["M0"]["state"] == "mastered"
assert p["modules"]["M1"]["state"] == "available"
assert p["modules"]["M2"]["state"] == "available"
assert p["modules"]["M3"]["state"] == "locked"
assert v2.next_card(cur, p)["id"] == "M1.01"
assert p["xp"] == 120 and "first-module" in p["badges"]
almost = v2.project(cur, events[:-1])
assert almost["modules"]["M0"]["state"] == "check_ready"
with contextlib.redirect_stdout(io.StringIO()):
    v2.print_tree(cur, almost, compact=True)

# Manual card selection may choose between available branches, but it cannot
# jump within a module or replay a solved card for secondary daily credit.
with tempfile.TemporaryDirectory() as tmp:
    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=3,
                           target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
                           run_editor=lambda *_: None, decode_keylog=lambda _: [],
                           hold_open=lambda: None, colours=("", "", "", "", "", ""))
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        assert v2.run(cfg, ["--card", "M0.03"]) == 1
    assert "complete M0.P0 first" in output.getvalue()
    v2.append_event(cfg, {"type": "card", "result": "pass", "card_id": "M0.P0",
                          "module_id": "M0"})
    v2.append_event(cfg, {"type": "card", "result": "pass", "card_id": "M0.01",
                          "module_id": "M0"})
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        assert v2.run(cfg, ["--card", "M0.01"]) == 1
    assert "already complete" in output.getvalue()
    for event in events:
        v2.append_event(cfg, event)
    # M0 mastery opens two real choices. M2.01 is valid even though iteration
    # order would otherwise select M1.01 as the automatic next card.
    assert v2.run(cfg, ["--card", "M2.01"]) == 0
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        assert v2.run(cfg, ["--card", "M2.03"]) == 1
    assert "complete M2.01 first" in output.getvalue()

# Duplicate passes and duplicate review stages do not farm XP.
assert v2.project(cur, events + [dict(events[0])])["xp"] == p["xp"]
review_once = events + [{"type": "review", "result": "pass", "review_key": "M0.01",
                         "review_stage": 1, "module_id": "M0"}]
review_twice = review_once + [dict(review_once[-1])]
assert v2.project(cur, review_once)["xp"] == v2.project(cur, review_twice)["xp"] == p["xp"] + 3

# Review selection is bounded to every fourth successful session and keeps its
# explicit due time in the rebuildable projection.
review_events = [
    {"type": "card", "result": "pass", "card_id": "M0.%02d" % n,
     "module_id": "M0", "at": "2026-09-26T00:00:00+00:00",
     "next_due": "2026-09-26T04:00:00+00:00"}
    for n in range(1, 5)
]
review_progress = v2.project(cur, review_events)
assert v2.due_review(cur, review_progress) is not None
assert not v2.should_review(review_events[:3], v2.due_review(cur, review_progress))
assert v2.should_review(review_events, v2.due_review(cur, review_progress))
review = v2.due_review(cur, review_progress)
assert v2.should_run_review(review_events, review, None)
assert not v2.should_run_review(review_events, review, None, explicit_force=True)
module_check = next(c for c in cur["cards"] if c["id"] == "M0.08")
assert not v2.should_run_review(review_events, review, module_check)

# Review stages and XP stop at the final configured interval.
max_stage = len(cur["review_intervals_hours"]) - 1
capped_events = events + [
    {"type": "review", "result": "pass", "review_key": "M0.01",
     "review_stage": max_stage, "module_id": "M0"},
    {"type": "review", "result": "pass", "review_key": "M0.01",
     "review_stage": max_stage, "module_id": "M0"},
]
assert v2.project(cur, capped_events)["xp"] == p["xp"] + 3

# Subtractive authoring keeps frame bounds equal by blanking a row instead of
# deleting it; the intermediate strip remains previewable.
m6_four = next(c for c in cur["cards"] if c["id"] == "M6.04")
assert m6_four["frame_slices"] == [5, 5]
m4_check = next(c for c in cur["cards"] if c["id"] == "M4.08")
m5_check = next(c for c in cur["cards"] if c["id"] == "M5.08")
for check, rows in ((m4_check, 3), (m5_check, 7)):
    frames = [check["target"][i:i + rows] for i in range(0, len(check["target"]), rows)]
    assert frames[0] != frames[-1], (check["id"], "loop boundary repeats frame 1")
m6_check = next(c for c in cur["cards"] if c["id"] == "M6.08")
assert m6_check["target"][:2] == ["", ""]
assert m6_check["target"][2].strip(), "first build frame needs an attached lower layer"


# A v2 popup must keep its teaching brief separate from the art buffer so gg/G
# and line-addressed commands still operate on art only.
with tempfile.TemporaryDirectory() as tmp:
    first = next(c for c in cur["cards"] if c["id"] == "M0.01")
    first_module = next(m for m in cur["modules"] if m["id"] == first["module_id"])

    def finish_visible_lesson(path, start_line, cursor, keylog, brief, task, hint):
        text = Path(brief).read_text(encoding="utf-8")
        assert "NEOVIM × ASCII ANIMATION" in text
        assert first["title"] in text and first["prompt"] in text
        assert "DO THIS" in text
        assert "TARGET" in text and "COMMAND RECIPE" in text
        assert "PROGRESS  M0 0/12 available" in text and "XP 0" in text
        assert "WHY THIS EXISTS" in text
        assert first_module["meaning"] in text
        assert first_module["principle"] in text
        assert first_module["defect"] in text
        assert "WHAT THIS LESSON BUYS YOU" in text and first["lesson_benefit"] in text
        assert "KEYS WORTH KEEPING" in text
        replace_legacy = legacy_payloads["replace-char"]
        assert all(line in text for line in replace_legacy["keys"])
        assert "LEGACY LESSON SOURCES" in text and replace_legacy["source"] in text
        assert "LEGACY VIM CONCEPT" in text
        assert " ".join(replace_legacy["paradigm"].split()) in " ".join(text.split())
        assert "WHERE THIS METHOD COMES FROM" in text and first["source_ref"] in text
        assert "READING THE RECIPE" in text and "<C-k>.M middle-dot digraph" in text
        assert "SUBMIT / STUCK" in text and ":q! exits without submission" in text
        assert task == first["prompt"] and hint == first["hint"]
        assert start_line == 1
        script = Path(keylog)
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_bytes(to_bytes(first["expected"] + ":wq<CR>"))
        cmd = ["nvim"]
        if not use_real:
            cmd += ["-u", "NONE", "-i", "NONE"]
        cmd += ["+%d" % start_line, "+normal! " + cursor, "-s", str(script), str(path)]
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        assert result.returncode == 0

    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=3,
                           target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
                           run_editor=finish_visible_lesson,
                           decode_keylog=lambda _: tokenize(first["expected"]),
                           hold_open=lambda: None, colours=("", "", "", "", "", ""),
                           question_answer=answer_question)
    progress = v2.project(cur, [])
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        assert v2.run_edit(cfg, cur, progress, first) == 0
    artifact = Path(tmp) / "projects" / first["project_id"] / "strip.txt"
    assert [line.rstrip() for line in artifact.read_text(encoding="utf-8").splitlines()] == [
        line.rstrip() for line in first["target"]
    ], output.getvalue()
    rendered = output.getvalue()
    assert "SKILL  " + first["skill"] in rendered or first["skill"] in (
        Path(tmp) / "sessions" / first["project_id"] / (first["id"] + ".txt")
    ).read_text(encoding="utf-8")
    assert "LESSON COMPLETE" in rendered
    assert "Streak extended to 1 day." in rendered
    assert "best 1" in rendered and "1 drill all time" in rendered
    assert "SKILL TREE / MODULE PROGRESS" in rendered
    assert "M0  Spark loop" in rendered and "1/12" in rendered
    assert "XP: 10" in rendered and "today: 1/12 lessons" in rendered
    assert "next: M0.P0" in rendered
    assert v2.project(cur, v2.read_events(cfg))["passed_cards"] == ["M0.01"]

    # Surface-job parity for one representative legacy lesson. Command/content
    # migration is tracked separately by LEGACY_CURRICULUM_DISPOSITION.md.
    legacy_cur = legacy_gate.load_curriculum()
    legacy_drill = legacy_cur["drills"][0]
    legacy_lesson = Path(tmp) / "legacy-lesson.txt"
    legacy_gate.write_lesson(legacy_lesson, legacy_drill,
                             legacy_cur["concepts"][legacy_drill["concept"]],
                             "Concept: parity")
    legacy_text = legacy_lesson.read_text(encoding="utf-8")
    v2_text = (Path(tmp) / "sessions" / first["project_id"] /
               (first["id"] + ".txt")).read_text(encoding="utf-8")
    parity = {
        "WHY THIS EXISTS": "WHY THIS EXISTS",
        "WHAT THIS DRILL BUYS YOU": "WHAT THIS LESSON BUYS YOU",
        "WHERE THIS SHAPE COMES FROM": "WHERE THIS METHOD COMES FROM",
        "DO THIS": "DO THIS",
        "KEYS WORTH KEEPING": "KEYS WORTH KEEPING",
        "READING THE RECIPE": "READING THE RECIPE",
        "STUCK?": "SUBMIT / STUCK",
    }
    for legacy_job, v2_job in parity.items():
        assert legacy_job in legacy_text, legacy_job
        assert v2_job in v2_text, (legacy_job, v2_job)
    assert legacy_drill["buys"] in legacy_text
    assert first["lesson_benefit"] in v2_text
    assert " ".join(legacy_drill["source"].split()) in " ".join(legacy_text.split())
    assert first["source_ref"] in v2_text

    disposition = (HERE / "LEGACY_CURRICULUM_DISPOSITION.md").read_text(
        encoding="utf-8")
    rows = re.findall(
        r"^\| `([^`]+)` \| (adapted|partial|retained-only) \| `([^`]+)` \|",
        disposition, flags=re.MULTILINE)
    legacy_ids = [drill["id"] for drill in legacy_cur["drills"]]
    mapped_ids = [legacy_id for legacy_id, _status, _card_id in rows]
    assert len(mapped_ids) == 46
    assert len(mapped_ids) == len(set(mapped_ids))
    assert set(mapped_ids) == set(legacy_ids)
    card_ids = {card["id"] for card in cur["cards"]}
    assert all(card_id in card_ids for _legacy_id, _status, card_id in rows)

    failed_replay = {
        "type": "edit", "table": ["  YOU TYPED", "  THE RECIPE ASKS FOR"],
        "before": first["start"], "got": first["start"], "target": first["target"],
    }
    today_before = v2._legacy_today(cfg.state)
    _s, _b, all_time_before = v2._legacy_streak(cfg.state)
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        v2._post_lesson(cfg, cur, first, v2.project(cur, []), failed_replay,
                        completed=False)
    failed_text = output.getvalue()
    assert "ARTIFACT REPLAY" in failed_text
    # VD-11: two-column replay (yours | target), a DO THIS action, and a
    # failed attempt that counts as daily practice and keeps the streak without
    # granting mastery XP or an all-time completion.
    assert "YOURS (what you saved)" in failed_text and "TARGET (what it should be)" in failed_text
    assert any(line.startswith("✗") and " │ " in line for line in failed_text.splitlines())
    assert "first difference at column" in failed_text
    assert "DO THIS" in failed_text and "then redo:" in failed_text
    streak_now, _best, all_time = v2._legacy_streak(cfg.state)
    assert streak_now >= 1, "a failed attempt must keep today's streak"
    assert v2._legacy_today(cfg.state) == today_before + 1, "attempts count toward daily practice"
    assert all_time == all_time_before, "attempts never add all-time completions"
    assert "WHY THIS EXISTS" in failed_text and first_module["principle"] in failed_text
    assert "WHAT THIS LESSON BUYS YOU" in failed_text and first["lesson_benefit"] in failed_text
    assert "PROGRESS UNCHANGED" in failed_text and "SKILL TREE / MODULE PROGRESS" in failed_text

    concept = next(c for c in cur["cards"] if c["id"] == "M0.03")
    question = next(q for q in cur["questions"] if q["id"] == concept["question_ids"][0])
    wrong = next(i for i in range(len(question["choices"])) if i != question["correct_choice"])
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        v2._post_lesson(cfg, cur, concept, v2.project(cur, v2.read_events(cfg)),
                        {"type": "concept", "question": question, "chosen": wrong},
                        completed=False)
    rendered = output.getvalue()
    assert "ATTEMPT NOT PASSED" in rendered and "conceptual choice was incorrect" in rendered
    assert "CONCEPT REPLAY" in rendered and "you chose:" in rendered and "correct:" in rendered
    assert "retain the principle" in rendered and "shuffled answer letter" in rendered

# Three active days restore the legacy flame, best streak, all-time total, and
# bold status treatment in both briefs and progress output.
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    today = v2._now().date()
    for offset in (2, 1, 0):
        day = today - v2.dt.timedelta(days=offset)
        (root / (day.isoformat() + ".log")).write_text(
            "completed_at=%sT12:00:00+0000\tdrill=test\n" % day.isoformat(),
            encoding="utf-8")
    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=3,
                           target=12, cooldown=3600, stamp=str(root / "stamp"),
                           run_editor=lambda *_: None, decode_keylog=lambda _: [],
                           hold_open=lambda: None,
                           colours=("<B>", "", "</B>", "", "", ""))
    line = v2._progress_line(cfg, v2.project(cur, []), card_by_id["M0.01"])
    assert "streak 3 days 🔥" in line and "best 3" in line
    assert "3 drills all time" in line
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        v2.print_tree(cur, v2.project(cur, []), cfg=cfg, compact=True)
    tree = output.getvalue()
    assert "<B>streak: 3 days 🔥 · best 3 · all-time 3</B>" in tree

# A failed editor attempt is archived but cannot poison the next session's
# starting artifact.  Comparison cards additionally require captured method
# evidence, not merely a target file written behind the tutor's back.
with tempfile.TemporaryDirectory() as tmp:
    compare = next(c for c in cur["cards"] if c["id"] == "M0.05")
    def target_without_keys(path, *_args):
        Path(path).write_text("\n".join(compare["target"]) + "\n", encoding="utf-8")
    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=1,
                           target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
                           run_editor=target_without_keys, decode_keylog=lambda _: [],
                           hold_open=lambda: None, colours=("", "", "", "", "", ""),
                           tokenize=tokenize, question_answer=answer_question)
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        assert v2.run_edit(cfg, cur, v2.project(cur, []), compare) == 1
    artifact = Path(tmp) / "projects" / compare["project_id"] / "strip.txt"
    assert artifact.read_text(encoding="utf-8").splitlines() == compare["start"]
    assert (artifact.parent / "checkpoints" / (compare["id"] + "-failed-1.txt")).exists()
    rows = v2.read_events(cfg)
    assert rows[-1]["reason"] == "missing-method-evidence"
    assert "METHOD EVIDENCE" in output.getvalue()
    assert "saved project matches the exact target" in output.getvalue()
    assert "saved project did not match" not in output.getvalue()

with tempfile.TemporaryDirectory() as tmp:
    compare = next(c for c in cur["cards"] if c["id"] == "M0.05")
    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=1,
                           target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
                           run_editor=lambda *_: None, decode_keylog=lambda _: [],
                           hold_open=lambda: None, colours=("", "", "", "", "", ""),
                           tokenize=tokenize, question_answer=answer_question)
    artifact = Path(tmp) / "projects" / compare["project_id"] / "strip.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("\n".join(compare["target"]) + "\n", encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()):
        assert v2.run_edit(cfg, cur, v2.project(cur, []), compare) == 1
    assert artifact.read_text(encoding="utf-8").splitlines() == compare["start"]
    assert any(path.name.startswith(compare["id"] + "-uncredited-target-")
               for path in (artifact.parent / "checkpoints").iterdir())

with tempfile.TemporaryDirectory() as tmp:
    card = next(c for c in cur["cards"] if c["id"] == "M0.04")
    def wrong_edit(path, *_args):
        Path(path).write_text("wrong\n", encoding="utf-8")
    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=1,
                           target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
                           run_editor=wrong_edit, decode_keylog=lambda _: [],
                           hold_open=lambda: None, colours=("", "", "", "", "", ""),
                           tokenize=tokenize, question_answer=answer_question)
    with contextlib.redirect_stdout(io.StringIO()):
        assert v2.run_edit(cfg, cur, v2.project(cur, []), card) == 1
    artifact = Path(tmp) / "projects" / card["project_id"] / "strip.txt"
    assert artifact.read_text(encoding="utf-8").splitlines() == card["start"]
    assert (artifact.parent / "checkpoints" / (card["id"] + "-failed-1.txt")).read_text(
        encoding="utf-8").splitlines() == ["wrong"]

with tempfile.TemporaryDirectory() as tmp:
    transfer = next(c for c in cur["cards"] if c["id"] == "M0.06")
    starts_seen = []
    def fail_transfer(path, *_args):
        starts_seen.append(Path(path).read_text(encoding="utf-8").splitlines())
        Path(path).write_text("wrong\n", encoding="utf-8")
    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=1,
                           target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
                           run_editor=fail_transfer, decode_keylog=lambda _: [],
                           hold_open=lambda: None, colours=("", "", "", "", "", ""),
                           question_answer=answer_question,
                           tokenize=tokenize)
    with contextlib.redirect_stdout(io.StringIO()):
        assert v2.run_edit(cfg, cur, v2.rebuild(cfg, cur), transfer) == 1
        assert v2.run_edit(cfg, cur, v2.rebuild(cfg, cur), transfer) == 1
    assert starts_seen == [transfer["variants"][0]["start"], transfer["variants"][1]["start"]]
    remediations = [row for row in v2.read_events(cfg)
                    if row.get("type") == "remediation_scheduled"]
    assert [row["family"] for row in remediations] == ["T", "T"]
    assert all(row.get("name") and row.get("changed_variant") for row in remediations)

# Failed question and module-check routes create named, visible changed-variant
# remediation records rather than silently replaying an identical attempt.
with tempfile.TemporaryDirectory() as tmp:
    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=1,
                           target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
                           run_editor=lambda *_: None, decode_keylog=lambda _: [],
                           hold_open=lambda: None, colours=("", "", "", "", "", ""))
    concept = next(c for c in cur["cards"] if c["id"] == "M0.03")
    check = next(c for c in cur["cards"] if c["id"] == "M0.08")
    original_ask = v2.ask_question
    v2.ask_question = lambda q, **_: (
        False, next(i for i in range(len(q["choices"])) if i != q["correct_choice"]))
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            assert v2.run_concept(cfg, cur, v2.rebuild(cfg, cur), concept) == 1
            passed, _replay = v2.run_check_questions(cfg, cur, v2.rebuild(cfg, cur), check)
        assert not passed
    finally:
        v2.ask_question = original_ask
    scheduled = [row for row in v2.read_events(cfg)
                 if row.get("type") == "remediation_scheduled"]
    assert {row["family"] for row in scheduled} == {"Q", "K"}
    assert all(row.get("name") and row.get("changed_variant") for row in scheduled)
    active = v2.rebuild(cfg, cur)["active_remediations"]
    assert set(active) == {"M0.03", "M0.08"}


failures = []
edit_cards = [c for c in cur["cards"] if c.get("expected")]
for card in edit_cards:
    with tempfile.TemporaryDirectory() as tmp:
        art = Path(tmp) / "strip.txt"
        art.write_text("\n".join(card["start"]) + "\n", encoding="utf-8")
        script = Path(tmp) / "keys.bin"
        script.write_bytes(to_bytes(card["expected"] + ":wq<CR>"))
        cmd = ["nvim"]
        if not use_real:
            cmd += ["-u", "NONE", "-i", "NONE"]
        cmd += ["+1", "+normal! " + card.get("cursor", "^"), "-s", str(script), str(art)]
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        got = [line.rstrip() for line in art.read_text(encoding="utf-8").splitlines()]
        want = [line.rstrip() for line in card["target"]]
        ok = result.returncode == 0 and got == want
        print("%-4s %-7s %-18s %s" % ("PASS" if ok else "FAIL", card["id"], card["kind"], card["expected"]))
        if not ok:
            print("     got=%r want=%r return=%d" % (got, want, result.returncode))
            failures.append(card["id"])

# Every edit brief exposes DO THIS, TARGET, and an action hint. Independent and
# comparison cards preserve only the key-sequence retrieval boundary.
with tempfile.TemporaryDirectory() as tmp:
    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=3,
                           target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
                           run_editor=lambda *_: None, decode_keylog=lambda _: [],
                           hold_open=lambda: None, colours=("", "", "", "", "", ""))
    progress = v2.project(cur, [])
    for card in [c for c in cur["cards"] if c.get("expected")]:
        cid = card["id"]
        text = v2._write_session_lesson(cfg, cur, progress, card).read_text(encoding="utf-8")
        for heading in ("DO THIS", "PROGRESS", "WHY THIS EXISTS", "WHAT THIS LESSON BUYS YOU",
                        "KEYS WORTH KEEPING", "WHERE THIS METHOD COMES FROM",
                        "READING THE RECIPE", "SUBMIT / STUCK"):
            assert heading in text, (cid, heading)
        assert card["lesson_benefit"] in text and card["source_ref"] in text
        assert "TARGET\n" in text, cid
        assert all("│" + row in text for row in card["target"]), cid
        if card.get("show_recipe", card.get("show_target", False)):
            assert "COMMAND RECIPE" in text and "TARGET\n" in text
            assert all(keys in text for keys, _why in card["recipe"]), cid
        else:
            assert "COMMAND RECIPE" not in text and "HINT\n" in text
            displayed_hint = card["hint"]
            if "choose the smallest normal-mode operation" in displayed_hint:
                displayed_hint = "use the commands explained under HOW THE KEYS YOU NEED WORK"
            assert displayed_hint in text, cid
            assert card["expected"] not in text, (cid, card["expected"])
            for method in card.get("method_alternatives", []):
                assert method["keys"] not in text, (cid, method["keys"])

for card in [c for c in cur["cards"] if c["kind"] == "compare_methods"]:
    assert "USE ONE METHOD" in card["prompt"] and "Do not perform both" in card["prompt"], card["id"]
    for method in card["method_alternatives"]:
        with tempfile.TemporaryDirectory() as tmp:
            art = Path(tmp) / "compare.txt"
            art.write_text("\n".join(card["start"]) + "\n", encoding="utf-8")
            script = Path(tmp) / "keys.bin"
            script.write_bytes(to_bytes(method["keys"] + ":wq<CR>"))
            cmd = ["nvim"]
            if not use_real:
                cmd += ["-u", "NONE", "-i", "NONE"]
            cmd += ["+1", "+normal! " + card.get("cursor", "^"), "-s", str(script), str(art)]
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            got = [line.rstrip() for line in art.read_text(encoding="utf-8").splitlines()]
            want = [line.rstrip() for line in card["target"]]
            assert result.returncode == 0 and got == want, (card["id"], method, got, want)

# Every transfer has a changed-art retry variant, and every variant's command
# is executed through real Neovim rather than trusted as data.
for card in [c for c in cur["cards"] if c["kind"] == "transfer"]:
    variants = card.get("variants", [])
    assert len(variants) >= 2, card["id"]
    assert len({tuple(variant["start"]) for variant in variants}) == len(variants)
    for variant in variants:
        with tempfile.TemporaryDirectory() as tmp:
            art = Path(tmp) / "transfer.txt"
            art.write_text("\n".join(variant["start"]) + "\n", encoding="utf-8")
            script = Path(tmp) / "keys.bin"
            script.write_bytes(to_bytes(variant["expected"] + ":wq<CR>"))
            result = subprocess.run(
                ["nvim", "-u", "NONE", "-i", "NONE", "+1",
                 "+normal! " + variant.get("cursor", "^"), "-s", str(script), str(art)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            assert result.returncode == 0
            assert art.read_text(encoding="utf-8").splitlines() == variant["target"], (
                card["id"], variant)

# Distinct techniques with card-specific review banks retrieve and execute that
# changed art instead of collapsing to one module transfer.
review_sources = [c for c in cur["cards"] if c.get("review_variants")]
assert {c["id"] for c in review_sources}.issuperset(
    {"M0.01", "M4.08", "M6.04", "M11.02", "M11.04", "M11.05", "M11.08",
     "M12.04", "M12.05", "M13.04", "M13.05"})
for source in review_sources:
    source_id = source["id"]
    assert len(source["review_variants"]) == 2, source_id
    for stage in (0, 1):
        review_card = v2._changed_review_card(
            cur, {"module_id": source["module_id"], "stage": stage}, source_id)
        assert review_card["expected"] == source["review_variants"][stage]["expected"]
        with tempfile.TemporaryDirectory() as tmp:
            art = Path(tmp) / "review.txt"
            art.write_text("\n".join(review_card["start"]) + "\n", encoding="utf-8")
            script = Path(tmp) / "keys.bin"
            script.write_bytes(to_bytes(review_card["expected"] + ":wq<CR>"))
            result = subprocess.run(
                ["nvim", "-u", "NONE", "-i", "NONE", "+1",
                 "+normal! " + review_card.get("cursor", "^"), "-s", str(script), str(art)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            got = [line.rstrip() for line in art.read_text(encoding="utf-8").splitlines()]
            assert result.returncode == 0 and got == [line.rstrip() for line in review_card["target"]], (
                source_id, stage, got, review_card["target"])
            replay = {"actual_tokens": tokenize(review_card["expected"])}
            assert v2._required_method_error(
                type("Cfg", (), {"tokenize": staticmethod(tokenize)})(),
                review_card, replay) is None

# Comparison evidence recognizes the defining edit inside a real attempt. It
# ignores navigation, Hardtime-blocked keys, corrected command-line typos, and
# every supported save/quit form while the exact target remains the main gate.
method_cfg = type("Cfg", (), {"tokenize": staticmethod(tokenize)})()
m005 = next(c for c in cur["cards"] if c["id"] == "M0.05")
assert v2._method_family(method_cfg, m005, {
    "actual_tokens": tokenize("jj:7,9tt<BS>$<CR>:w<CR>:q<CR>"),
}) == "addressed copy"
assert v2._method_family(method_cfg, m005, {
    "actual_tokens": tokenize("7G3yyGkGp:wq<CR>"),
}) == "counted yank and put"
assert v2._method_family(method_cfg, m005, {
    "actual_tokens": tokenize("7GV2jyGkGpZZ"),
}) == "counted yank and put"
assert v2._method_family(method_cfg, m005, {
    "actual_tokens": tokenize(":7,9copy$<CR>:x<CR>"),
}) == "addressed copy"
for submission in (":wq<CR>", ":w<CR>:q<CR>", ":write<CR>:quit<CR>",
                   ":x<CR>", "ZZ", "ZQ"):
    assert v2._edit_tokens_without_submit(tokenize("jj" + submission)) == ["j", "j"]
truthful = v2._unrecognized_method_message({
    "actual_tokens": tokenize("jj"), "actual_keys": "jj",
})
assert "keys were captured" in truthful and "Captured keys: jj" in truthful
assert "no edit keystrokes were captured" not in truthful
with tempfile.TemporaryDirectory() as tmp:
    key_dir = Path(tmp)
    first_keylog = v2._next_attempt_keylog(key_dir, "keys-M0.05")
    first_keylog.write_bytes(b"first")
    second_keylog = v2._next_attempt_keylog(key_dir, "keys-M0.05")
    second_keylog.write_bytes(b"second")
    assert first_keylog.name == "keys-M0.05-attempt-0001.log"
    assert second_keylog.name == "keys-M0.05-attempt-0002.log"
    assert v2._latest_attempt_keylog(key_dir, "keys-M0.05") == second_keylog
for sequence, family in (
        ("jj:7,9tt<BS>$<CR>:w<CR>:q<CR>", "addressed copy"),
        ("7G3yyGkGp:wq<CR>", "counted yank and put")):
    with tempfile.TemporaryDirectory() as tmp:
        def finish_compare(path, _start, _cursor, keylog, *_rest):
            Path(path).write_text("\n".join(m005["target"]) + "\n", encoding="utf-8")
            Path(keylog).write_bytes(b"per-attempt evidence")

        cfg = v2.RuntimeConfig(
            state=tmp, share=str(HERE), editor="nvim", max_tries=3,
            target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
            run_editor=finish_compare,
            decode_keylog=lambda _data, answer=sequence: tokenize(answer),
            hold_open=lambda: None, colours=("", "", "", "", "", ""),
            tokenize=tokenize, question_answer=answer_question)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            assert v2.run_edit(cfg, cur, v2.project(cur, []), m005) == 0
        events = v2.read_events(cfg)
        passed = next(row for row in reversed(events)
                      if row.get("type") == "card" and row.get("result") == "pass")
        assert passed["method_family"] == family
        assert passed["keylog"].endswith("keys-M0.05-attempt-0001.log")
        assert Path(passed["keylog"]).is_file() and passed["keylog_sha256"]
        assert "LESSON COMPLETE" in output.getvalue()

# Exact contracts reject padded keys even when the target buffer would happen
# to match. Cards without their own source-linked bank are not silently mapped
# to the module transfer and therefore are absent from review coverage.
for source in [c for c in cur["cards"] if c.get("method_requirement")
               and c.get("review_source_card_id")]:
    review_card = v2._changed_review_card(
        cur, {"module_id": source["module_id"], "stage": 0}, source["id"])
    assert review_card.get("method_requirement"), source["id"]
    assert review_card["review_source_card_id"] == source["id"]
    assert review_card["review_method_family"] == source["review_method_family"]
    exact = source["method_requirement"].get("exact_any_of", [])
    if exact:
        replay = {"actual_tokens": tokenize("u" + exact[0])}
        assert v2._required_method_error(method_cfg, source, replay), source["id"]
unsupported_review = next(c for c in cur["cards"] if c["id"] == "M12.01")
assert not unsupported_review.get("review_source_card_id")
try:
    v2._changed_review_card(cur, {"module_id": "M12", "stage": 0}, "M12.01")
    raise AssertionError("unlinked card silently fell back to a module transfer")
except ValueError as exc:
    assert "no source-linked" in str(exc)

# Module checks retain every question/answer/explanation for the held debrief;
# spaced reviews now use that same two-page feedback/progression contract.
with tempfile.TemporaryDirectory() as tmp:
    held = []
    current_tokens = []
    review_variants = {}
    for review_source in [c for c in cur["cards"] if c["module_id"] == "M0"]:
        for variant in (review_source.get("review_variants", [])
                        or review_source.get("variants", [])):
            review_variants[tuple(variant["start"])] = variant
    def complete_review_edit(path, *_args):
        start = tuple(Path(path).read_text(encoding="utf-8").splitlines())
        variant = review_variants[start]
        Path(path).write_text("\n".join(variant["target"]) + "\n", encoding="utf-8")
        Path(_args[2]).write_bytes(b"captured-by-test-double")
        current_tokens[:] = tokenize(variant["expected"])
    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=3,
                           target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
                           run_editor=complete_review_edit,
                           decode_keylog=lambda _: list(current_tokens),
                           hold_open=lambda: held.append(True),
                           colours=("", "", "", "", "", ""))
    check = next(c for c in cur["cards"] if c["id"] == "M0.08")
    progress = v2.project(cur, [])
    original_ask = v2.ask_question
    v2.ask_question = lambda q, **_: (True, q["correct_choice"])
    try:
        passed, replay = v2.run_check_questions(cfg, cur, progress, check)
        assert passed and replay["score"] == 5 and len(replay["outcomes"]) == 5
        resumed, recovered = v2.run_check_questions(cfg, cur, v2.rebuild(cfg, cur), check)
        assert resumed and recovered["score"] == 5 and len(recovered["outcomes"]) == 5
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            v2._post_lesson(cfg, cur, check, v2.rebuild(cfg, cur), replay, completed=True)
        check_text = output.getvalue()
        assert "MODULE CHECK REPLAY" in check_text and "5/5 correct" in check_text
        assert check_text.count("chose:") == 5 and check_text.count("why:") >= 5

        review = {"module_id": "M0", "stage": 0, "question_id": "M0.Q01"}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            assert v2.run_review(cfg, cur, v2.rebuild(cfg, cur), "M0.01", review) == 0
        review_text = output.getvalue()
        assert "REVIEW RETRIEVED" in review_text
        assert "CONCEPT REPLAY" in review_text and "CHANGED-ART EDIT REPLAY" in review_text
        assert "exact saved target verified" in review_text
        assert "SKILL TREE / MODULE PROGRESS" in review_text
        latest_review = [row for row in v2.read_events(cfg)
                         if row.get("type") == "review"][-1]
        assert latest_review["edit_variant"] == 0 and latest_review.get("artifact_sha256")
        assert held == [True]

        capped = {"module_id": "M0", "stage": len(cur["review_intervals_hours"]) - 1,
                  "question_id": "M0.Q01"}
        with contextlib.redirect_stdout(io.StringIO()):
            assert v2.run_review(cfg, cur, v2.rebuild(cfg, cur), "M0.01", capped) == 0
        latest_review = [row for row in v2.read_events(cfg)
                         if row.get("type") == "review"][-1]
        assert latest_review["review_stage"] == len(cur["review_intervals_hours"]) - 1

        v2.ask_question = lambda q, **_: (
            False, next(i for i in range(len(q["choices"])) if i != q["correct_choice"]))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            assert v2.run_review(cfg, cur, v2.rebuild(cfg, cur), "M0.02", review) == 1
        review_text = output.getvalue()
        assert "REVIEW NEEDS WORK" in review_text and "PROGRESS UNCHANGED" in review_text
        assert held == [True, True, True]
    finally:
        v2.ask_question = original_ask

# Module mastery events bind the final checkpoint to the earlier unseen
# transfer evidence so a rebuilt projection does not erase what was assessed.
with tempfile.TemporaryDirectory() as tmp:
    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=3,
                           target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
                           run_editor=lambda *_: None, decode_keylog=lambda _: [],
                           hold_open=lambda: None, colours=("", "", "", "", "", ""))
    v2.append_event(cfg, {"type": "card", "result": "pass", "card_id": "M0.06",
                          "module_id": "M0", "artifact": "/tmp/transfer.txt",
                          "artifact_sha256": "transfer-hash"})
    check = next(c for c in cur["cards"] if c["id"] == "M0.08")
    with contextlib.redirect_stdout(io.StringIO()):
        assert v2._complete(cfg, cur, check,
                            extra={"artifact": "/tmp/strip.txt",
                                   "artifact_sha256": "checkpoint-hash"}) == 0
    event = [row for row in v2.read_events(cfg) if row.get("card_id") == "M0.08"][-1]
    assert event["module_evidence"] == {
        "checkpoint_artifact": "/tmp/strip.txt", "checkpoint_sha256": "checkpoint-hash",
        "transfer_card_id": "M0.06", "transfer_artifact": "/tmp/transfer.txt",
        "transfer_sha256": "transfer-hash",
    }

with tempfile.TemporaryDirectory() as tmp:
    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=3,
                           target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
                           run_editor=lambda *_: None, decode_keylog=lambda _: [],
                           hold_open=lambda: None, colours=("", "", "", "", "", ""))
    check = next(c for c in cur["cards"] if c["id"] == "M0.08")
    try:
        v2._complete(cfg, cur, check,
                     extra={"artifact": "/tmp/strip.txt",
                            "artifact_sha256": "checkpoint-hash"})
        raise AssertionError("module mastery accepted missing transfer evidence")
    except RuntimeError as exc:
        assert "unseen-transfer" in str(exc)
    assert not v2.read_events(cfg), "failed mastery guard wrote a completion event"

with tempfile.TemporaryDirectory() as tmp:
    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=3,
                           target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
                           run_editor=lambda *_: None, decode_keylog=lambda _: [],
                           hold_open=lambda: None, colours=("", "", "", "", "", ""))
    check = next(c for c in cur["cards"] if c["id"] == "M0.08")
    for number in range(1, 6):
        v2.append_event(cfg, {"type": "question", "result": "fail", "card_id": check["id"],
                              "module_id": "M0", "question_id": "M0.Q%02d" % number,
                              "choice": 0, "check": True})
    v2.append_event(cfg, {"type": "card", "result": "fail", "card_id": check["id"],
                          "module_id": "M0", "reason": "concept-threshold"})
    seen = []
    original_ask = v2.ask_question
    v2.ask_question = lambda q, **_: (seen.append(q["id"]) or True, q["correct_choice"])
    try:
        passed, _replay = v2.run_check_questions(cfg, cur, v2.rebuild(cfg, cur), check)
        assert passed
        assert set(seen) == {"M0.Q%02d" % number for number in range(6, 11)}
        assert set(seen).issubset(set(check["question_ids"]))
    finally:
        v2.ask_question = original_ask

# Preview uses manifest-owned frame boundaries and identifies declared holds;
# subtractive frames remain equal-height throughout M6.
with tempfile.TemporaryDirectory() as tmp:
    cfg = v2.RuntimeConfig(state=tmp, share=str(HERE), editor="nvim", max_tries=3,
                           target=12, cooldown=3600, stamp=str(Path(tmp) / "stamp"),
                           run_editor=lambda *_: None, decode_keylog=lambda _: [],
                           hold_open=lambda: None, colours=("", "", "", "", "", ""))
    for cid, expected_status in (("M7.08", 0), ("M6.04", 0)):
        card = next(c for c in cur["cards"] if c["id"] == cid)
        base = Path(tmp) / "projects" / card["project_id"]
        base.mkdir(parents=True, exist_ok=True)
        (base / "strip.txt").write_text("\n".join(card["target"]) + "\n", encoding="utf-8")
        (base / "manifest.json").write_text(json.dumps({"current_card": cid}), encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = v2.preview_project(cfg, cur, card["module_id"], speed=0)
        assert status == expected_status, (cid, output.getvalue())
        if expected_status:
            assert "unequal frame heights" in output.getvalue()
        elif cid == "M7.08":
            assert "HOLD: anticipation before the completed build" in output.getvalue()
    compare = next(c for c in cur["cards"] if c["id"] == "M0.05")
    compare_artifact = Path(tmp) / "projects" / compare["project_id"] / "strip.txt"
    compare_artifact.parent.mkdir(parents=True, exist_ok=True)
    compare_path = v2._write_compare(compare, compare_artifact)
    compare_text = compare_path.read_text(encoding="utf-8")
    assert compare_path.exists()
    assert all(method["label"] in compare_text and method["keys"] in compare_text
               for method in compare["method_alternatives"])

    # Verifying a transfer writes separate evidence and leaves the playable
    # strip manifest pointing at the last project card.
    project_card = next(c for c in cur["cards"] if c["id"] == "M0.05")
    transfer_card = next(c for c in cur["cards"] if c["id"] == "M0.06")
    base = Path(tmp) / "projects" / project_card["project_id"]
    base.mkdir(parents=True, exist_ok=True)
    strip = base / "strip.txt"
    strip.write_text("\n".join(project_card["target"]) + "\n", encoding="utf-8")
    v2._update_manifest(cur, project_card, strip)
    transfer = base / ("transfer-" + transfer_card["id"] + ".txt")
    transfer.write_text("\n".join(transfer_card["target"]) + "\n", encoding="utf-8")
    v2._update_manifest(cur, transfer_card, transfer)
    assert json.loads((base / "manifest.json").read_text(encoding="utf-8"))["current_card"] == "M0.05"
    assert json.loads((base / "transfer-manifest.json").read_text(
        encoding="utf-8"))["current_card"] == "M0.06"

    timed = next(c for c in cur["cards"] if c["id"] == "M7.01")
    timed_base = Path(tmp) / "projects" / timed["project_id"]
    timed_base.mkdir(parents=True, exist_ok=True)
    timed_path = timed_base / "strip.txt"
    timed_path.write_text("\n".join(timed["target"]) + "\n", encoding="utf-8")
    v2._update_manifest(cur, timed, timed_path)
    timed_manifest = json.loads((timed_base / "manifest.json").read_text(encoding="utf-8"))
    assert timed_manifest["animation"]["role"] == "hold"
    assert timed_manifest["animation"]["hold_reason"]

# The session lock is advisory and process-owned: an old pathname cannot evict
# a live holder, and releasing it allows a new session without stale cleanup.
with tempfile.TemporaryDirectory() as tmp:
    lock_path = Path(tmp) / "session.lock"
    with v2.SessionLock(lock_path):
        try:
            with v2.SessionLock(lock_path):
                raise AssertionError("second live session acquired the lock")
        except RuntimeError:
            pass
    with v2.SessionLock(lock_path):
        assert lock_path.exists()

# Runtime schema checks reject referential and answer-index corruption.
for mutator in (
    lambda broken: broken["questions"][0].__setitem__("correct_choice", 4),
    lambda broken: broken["cards"][0].__setitem__("module_id", "M404"),
    lambda broken: broken["modules"][0]["card_ids"].__setitem__(0, "M0.99"),
    lambda broken: next(card for card in broken["cards"]
                        if card.get("kind") == "transfer").__setitem__(
                            "variants", [next(card for card in broken["cards"]
                                               if card.get("kind") == "transfer")["variants"][0]]),
    lambda broken: next(card for card in broken["cards"]
                        if card["id"] == "M0.05").pop("duplicate_frames"),
):
    broken = json.loads(json.dumps(cur))
    mutator(broken)
    try:
        v2.validate_curriculum(broken)
        raise AssertionError("invalid curriculum passed validation")
    except ValueError:
        pass

print("\n%d/%d executable lessons present; %d/%d primary edit recipes passable (config=%s); "
      "%d conceptual/check lessons, %d changed-art transfer variants, "
      "%d compare paths, and graph/questions/state valid" % (
          len(cur["cards"]), len(cur["cards"]), len(edit_cards) - len(failures), len(edit_cards),
          "real" if use_real else "none",
          len([c for c in cur["cards"] if c["kind"] in ("concept", "module_check")]),
          len(review_sources),
          len([c for c in cur["cards"] if c["kind"] == "compare_methods"])))
raise SystemExit(1 if failures else 0)
