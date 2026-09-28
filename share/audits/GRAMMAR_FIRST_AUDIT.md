# Grammar-first Socratic curriculum audit

Status: audit and proposal complete; awaiting operator approval. This document
is not approval to edit the generator or runtime. The operator approval
boundary in `GRAMMAR_FIRST_REQUIREMENT.md` remains binding.

Baseline: repository HEAD `17f87121baddc958e23e17aafdf2ac0857e5091f`,
preserved dirty worktree, generated curriculum revision `2026-09-28.22`.

## Scope and evidence set

The four strict card-range audits cover every one of the 114 executable cards:

- `grammar-sequence-M0-M4.md`: 30 executable cards.
- `grammar-sequence-M5-M9.md`: 30 executable cards.
- `grammar-sequence-M10-M14.md`: 30 executable cards.
- `grammar-sequence-M15-M18.md`: 24 executable cards.

`SOCRATIC_COURSE_AUDIT.md` covers all 152 cards, including the 38 current
concept cards, their exact proposed questions, placement, placement rationale,
and the nine-habit/S0–S7/A0–A7 finish-line matrix. `SOCRATIC_RUNTIME_DESIGN.md`
defines the proposed effect-grading and interaction mechanics, while
`NEOVIM_HINT_PLUGIN_RESEARCH.md` defines the advisory-plugin boundary.

## Current structural result

The current course is executable but does not meet the operator's teaching
contract:

| Surface | Current `.22` evidence | Required result |
|---|---:|---|
| Modules / cards | 19 / 152 | Preserve useful art projects; sequence by the explicit master-stage contract. |
| Executable cards | 114 | Each has a command-family declaration and an authored question-placement decision. |
| Questions | 190, all four-choice | Use open typed-key, decode, complete, predict, why, and diagnostic multiple choice intentionally. |
| Ordinary executable cards with questions | 0/95 | At least one paired question unless that card records a defensible exception. |
| Module checks with question banks | 19/19 | Retain as mixed checks; do not let them stand in for prior teaching. |
| Cards with grammar metadata | 0/152 | Declare grammar class, parts, stage dependencies, and evidence owners. |
| Executable cards with card-owned key vocabulary | 2/114 | Every hidden card names useful family grammar without revealing the answer. |
| Review-capable executable cards | 50/114: 31 explicit review banks + 19 transfer banks | Every mastered family has a later unfamiliar-art spaced review. |
| Cards with a question-placement reason | 0/152 | Record before/after/both/exception and the card-specific reason. |
| Explicit motivated-continuation action | none | Offer close and next-eligible actions without bypassing evidence. |

The generator step schema has no grammar or placement contract
(`share/gen_curriculum_v2.py:70-87`). It assigns question IDs only to concept
cards and module checks (`share/gen_curriculum_v2.py:3443-3477`). The runtime
asks a question on an ordinary route only when the card is a module check
(`share/v2_runtime.py:1545-1618`). Its only question renderer is shuffled
multiple choice (`share/v2_runtime.py:457-498`).

## Systemic gaps

### G-01 — Recipes precede understanding

The dominant order is visible recipe first, later concept card, then hidden
retrieval. It is not explanation → learner interpretation → learner completion
→ guided performance → hidden retrieval → changed-art review. Even the repaired
M0.02 shows `3yy/p` and ranged substitution before the learner has to work out
their grammar.

### G-02 — Hidden first uses remain widespread

Verified examples across the partition reports include absolute `G`, `:t`,
`dd`, `o/O`, dot repeat, `ci(`, Visual-line/register operations, digraphs,
Visual block operations, `D`, `:m`, macros, `:global ... normal`, `x`, `i`,
undo/redo, virtual columns, `;`/`,`, `E`/`B`, paragraph navigation/put,
`:set shiftwidth`, `>>`, `<C-a>`, `:read`, and expression substitution. An
attached legacy chapter or answer-key token does not close any of these gaps.

### G-03 — The question system is single-form and detached

All 190 current questions are multiple choice. None stores a semantic key
effect, missing grammar part, decoded components, predicted buffer/cursor state,
or per-card placement rationale. Ordinary edits do not execute a paired
question. Random selection from a module pool can therefore skip the exact
concept a hidden edit assumes.

### G-04 — Grammar is not a recurring dependency

The data has no family-level evidence graph. Normal operators, standalone
commands, and Ex statements are not distinguished in validation. A learner can
pass a later artifact without proving the relevant grammar parts on unfamiliar
art, and a target-only path can receive credit for a method-specific family
unless a card happens to declare exact method evidence.

### G-05 — Review happens after mastery or not at all

The runtime schedules due review after a source passes
(`share/v2_runtime.py:1417-1419`). Module mastery requires a transfer event but
not a passed family review (`share/v2_runtime.py:1421-1442`). Sparse review
banks and post-mastery scheduling therefore cannot prove the requested
key-hidden spaced retrieval before mastery.

### G-06 — Hidden-card help is usually generic

Only M0.02 and M0.04 own `key_vocabulary`. Other hidden briefs either inherit
legacy prose or fall back to F1/undo/redo/save reminders
(`share/v2_runtime.py:636-640,667-674,720-730`). This fails to give a stuck
learner the command family and grammar while keeping the exact recipe hidden.

### G-07 — Heuristic hints can teach the wrong method

The audits found false positives caused by scanning recipe text rather than
authored command metadata: M3.06 is mislabeled as a paragraph-object operation;
M4.01 and M18 C-based redraw cards receive search advice because `/` is literal
art; M4.08 claims dot repeat although its path is `13G3dd`; M15.06 suggests dot
without using it. These are teaching defects, not cosmetic copy issues.

### G-08 — The finish-line stages are overloaded

Current display nodes reuse `A0`–`A7` for the older skill tree and later reuse
`A0`, `A3`, and `A6` for the operator's master authoring stages. Only S2, S3,
S5, and S7 have explicit later module owners. A separate `master_stage` contract
is required; display-node names cannot prove nine-habit/S0–S7/A0–A7 coverage.

### G-09 — Mistakes and motivation end at a held page

Wrong multiple-choice answers print only the selected feedback and schedule a
variant; they do not re-show the relevant grammar breakdown. Completion prints
the next card but then unconditionally holds the popup
(`share/v2_runtime.py:1450-1461`). There is no explicit continue-now action.

### G-10 — Plugin assistance must not replace or rewrite the real environment

The operator's configured Hardtime, WhichKey, lualine, theme, relative numbers,
and mappings are part of the default learning environment. Keycast and hint
plugins cannot grade the semantic result, and the tutor must not silently
disable or reconfigure an operator-owned plugin. A future exam-isolation mode
may suppress selected hints only when the operator explicitly opts into it.
Precognition remains unsuitable for the fixed-width art surface because its
virtual text, virtual lines, and signs alter the visible evidence surface.

## Required M0 teaching sequence

M0 must become the concrete grammar foundation without becoming the only place
grammar appears:

1. **Primer:** distinguish Normal operator sentences, standalone commands, and
   Ex statements. Ask a decode/predict question before any recipe.
2. **One-cell overwrite:** work out why `r{char}` changes one cell without
   shifting the grid; perform it with keys visible; later retrieve on changed
   art.
3. **Whole-frame copy:** decompose counted linewise `3yy` and standalone `p/P`;
   ask an open-key or completion question; perform on the three-row spark.
4. **Opening rows:** teach `o` versus `O`, Insert-mode entry, `<Esc>`, and why
   linewise put is safer for copying an existing frame. Exercise it under the
   real-config, art-buffer-only indentation invariant.
5. **Ex substitution:** decode address/range, `s`, pattern, replacement, `g`,
   and `<CR>`; ask what `:8s/-/=/g` means and what completes
   `:8s/-/=/`; perform a visible bounded substitution.
6. **M0.04 retrieval:** keep the target and useful family vocabulary visible,
   hide the exact path, and require the learner to copy the bright frame and
   widen only the new frame's rays.
7. **After-question and review:** ask the learner to explain the chosen scope
   or predict a changed-art result; later require an unfamiliar spark/comet edit
   with the keys hidden.

Ex copy `:[range]t{destination}<CR>` must receive the same sequence before the
current M0.05 comparison. Dot repeat must not first appear inside M0.08.

## Proposed data contracts

These names are proposal-level and require operator approval:

- `command_families`: stable IDs and grammar class for every executable path.
- `grammar_parts`: count/operator/motion-or-object; standalone command operand,
  mode, and scope; or Ex address/range/command/arguments/flags/Enter.
- `teaching_evidence`: explanation, interpretation question, completion
  question, guided card, hidden retrieval, and changed-art review IDs.
- `paired_questions`: ordered before/after question IDs plus an authored
  placement reason; an exception requires `question_exception_reason`.
- `master_habits` and `master_stages`: explicit links to the nine habits and
  S0–S7/A0–A7/P finish line, separate from display-tree node IDs.
- `semantic_key_scenario`: isolated start buffer, cursor, mode, accepted effect,
  forbidden effects, optional method constraint, timeout, and captured evidence.
- `grammar_breakdown`: safe explanation to re-show after an incorrect answer;
  it must not contain the hidden card's accepted recipe.
- `continuation`: close and next-eligible actions resolved by the same
  prerequisite/remediation/review scheduler used for normal selection.

## Validator contract

Generation or tests must fail when:

1. an executable card omits family, master-habit, master-stage, or placement
   metadata;
2. a hidden family appears before explanation, interpretation, completion, and
   guided evidence;
3. an exercise lacks a paired question and has no written exception;
4. an open-key answer is checked by string equality instead of declared effect;
5. a hidden brief leaks the exact answer or omits useful family grammar;
6. a method-specific mastery claim lacks captured method evidence;
7. a family can be mastered without changed-art spaced review;
8. a hint is inferred from literal art glyphs or prose tokens rather than its
   declared family;
9. a wrong answer cannot display its relevant grammar breakdown;
10. continuation can skip remediation, prerequisites, unfinished check parts,
    due review, or the daily policy;
11. any of the nine habits or S0–S7/A0–A7 stages lacks key-hidden performance
    and changed-art review evidence.
12. a submitted wrong question or failed artifact fails to count exactly once
    toward daily practice, or accidentally grants XP/mastery;
13. any viewport drops the artifact replay, two-column actual-versus-taught
    keystroke ledger, method diagnosis, skill tree/module status, XP, level,
    daily count, or streak from the post-attempt journey.
14. the tutor silently installs, disables, or reconfigures an operator-owned
    plugin, or accepts plugin output as grading evidence.

## Verification boundary

After operator approval and implementation, evidence must include data
validators, semantic-key scenarios, clean and real-config recipe paths,
failure/retry/remediation flows, review-before-mastery falsifiers, and headed
journeys at 80×24, 100×36, and 188×49. Screen labels alone are not proof; the
test must perform the interaction and inspect the resulting buffer, cursor,
event evidence, and visible result pages.

## Approval gate

Do not edit the generator, runtime, generated curriculum, or implementation
tests from this proposal. Complete the 152-card Socratic proposal, plugin hint
research, runtime-mechanics review, failure-log receipt, and audit-only commit;
then show the operator the proposal and wait for explicit approval.
