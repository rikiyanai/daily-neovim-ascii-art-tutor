# Grammar-first paired-learning requirement

Status: audit and proposal complete; awaiting operator approval. Curriculum and
runtime implementation remains frozen until that approval.

Repository baseline: `17f87121baddc958e23e17aafdf2ac0857e5091f` plus the
operator's preserved dirty worktree. Audit target: generated curriculum
revision `.22`.

## Requirement ledger

| ID | Requirement | Evidence required before implementation can be called complete |
|---|---|---|
| GF-01 | Teach Normal-mode operator grammar as `[count] operator [count] motion-or-text-object`. | Each family has an authored decomposition, an appropriate interpretation or open-key item, a guided edit, a later hidden retrieval, and a changed-art review. |
| GF-02 | Teach standalone Normal-mode commands as standalone commands rather than forcing them into operator grammar. | Commands such as `p`, `P`, `r`, `R`, `u`, `J`, `x`, `o`, and `O` have explicit semantics and scope checks before hidden use. |
| GF-03 | Teach Ex grammar as `:[address-or-range] command /pattern/replacement/ flags <Enter>`. | The learner identifies address/range, command, delimiter arguments, flags, and execution key before any hidden Ex use. |
| GF-04 | Pair conceptual retrieval with performed ASCII-animation work. | Every executable card declares paired question IDs that test both Vim semantics and the animation invariant exercised by that edit. |
| GF-05 | Preserve the teaching order: explanation, interpretation, completion, guided performance, hidden retrieval, changed-art review. | A validator rejects any command family whose first hidden requirement precedes one of those stages. |
| GF-06 | Keep exact answers hidden on retrieval cards while exposing useful vocabulary. | `KEYS WORTH KEEPING` names command families and grammar without reproducing the card's exact accepted sequence. |
| GF-07 | Make hints strategic and diagnostic. | The pre-attempt hint adds information not present in `DO THIS`; failure feedback identifies the observed scope, registration, or method error. |
| GF-08 | Keep every question genuinely paired. | Every item tests both a visible animation/authoring decision and Vim semantics/scope; when multiple choice is justified, every choice pairs both halves and every wrong-answer path has mistake-specific feedback. |
| GF-09 | Support motivated continuation after results. | The progress page offers one explicit close action and one explicit next-eligible lesson/question action without bypassing prerequisites or evidence. |
| GF-10 | Grade performed method evidence where a card claims command-family mastery. | Reaching the target by an unrelated method cannot award a family-specific mastery claim. |
| GF-11 | Preserve column registration under the operator's real config. | The art buffer alone has `autoindent`, `smartindent`, and `cindent` disabled with empty `indentexpr` after plugins load; a headed test performs `o`, saves, checks column 1, undoes, and restores the checkpoint. |
| GF-12 | Preserve the operator's Neovim as the default learning environment. | Headed evidence retains lualine, relative numbers, WhichKey, Hardtime, mappings, and theme; tutor-owned chrome exists only under `VIM_DAILY_CLEAN=1`. |
| GF-13 | Teach by questioning rather than defaulting to revealed recipes. | The authored sequence uses open typed-key, decode, complete, predict, and why questions; multiple choice is one form rather than the universal form. |
| GF-14 | Grade open key answers by their effect. | A scratch-Neovim evaluator accepts every declared semantically valid answer that reaches the required cursor or buffer state (for example `4j` and `:+4<CR>`), records the actual keys, and rejects only wrong effects or forbidden scope. |
| GF-15 | Keep both Vim grammars recurring. | Every newly introduced family is decomposed into its parts, and later unfamiliar-art questions require those parts again instead of treating the M0 primer as permanent proof. |
| GF-16 | Give every question a card-specific placement rationale. | Each of the 152 cards records whether its question belongs before performance, after performance, both, or—only with a written exception reason—not at all. The floor is at least one paired question per exercise. |
| GF-17 | Make the nine expert habits and S0–S7/A0–A7 sequence the coverage finish line. | Every habit and stage has a key-hidden required performance plus a changed-art spaced review; a generated coverage report fails on every missing habit/stage/family link. |
| GF-18 | Turn mistakes and momentum into explicit interactions. | A wrong answer re-shows the relevant grammar breakdown before retry; every result screen offers an optional next eligible item without bypassing remediation or prerequisites. |
| GF-19 | Count genuine failed work as daily practice without granting mastery. | A submitted wrong question or failed artifact increments today's practice/streak ledger exactly once, while XP, card completion, family mastery, and module mastery remain unchanged. |
| GF-20 | Preserve the full post-attempt debrief and progress surfaces. | Every edit attempt retains artifact before/after evidence, the two-column actual-versus-taught keystroke ledger, method diagnostics, progress/tree/module status, XP, level, today count, and streak at 80×24, 100×36, and 188×49. |
| GF-21 | Keep plugin advice separate from authority and preserve the operator's chosen config. | User-configured Hardtime, WhichKey, lualine, theme, mappings, and relative numbers remain active by default. Hint/key-display plugins are advisory only and never grade an attempt. The tutor neither installs nor suppresses one without an explicit operator setting; any future exam-isolation mode is opt-in. |

## What does not count as teaching

- A command appearing only in `expected`, `recipe`, an accepted-key path, or a
  validator token list.
- A legacy lesson attached as provenance without a current-card grammar stage.
- A command named only in a distractor or answer explanation.
- A generic cheat-sheet entry without a paired question and guided edit.
- A target-only grader accepting any method when mastery claims a specific
  family.
- A question about tutor design, evidence files, corpus counts, or curriculum
  metadata.

## Frozen `.22` structural baseline

These are failures to repair after the audit commit, not implementation credit:

- The generated course has 19 modules, 152 cards, and 190 questions. Of the
  114 executable cards, only the 19 module checks own any `question_ids`;
  ordinary guided, independent, comparison, and transfer edits therefore have
  no required concept check immediately paired with their performance.
- No card declares a command-family grammar classification, a teaching stage,
  or a `paired_question_ids` field. The generator's step schema accepts start,
  target, expected keys, recipe, method evidence, review variants, and optional
  key vocabulary, but no grammar-teaching contract
  (`share/gen_curriculum_v2.py:70-87`).
- All 190 current questions are four-choice multiple choice: there are 19 of
  each of the ten existing question types. The question schema has no typed-key
  answer, semantic cursor/buffer expectation, decode parts, missing-token
  completion, or authored placement reason, and `ask_question` accepts only a
  shuffled letter (`share/v2_runtime.py:457-498`).
- Only `M0.02` and `M0.04` have card-owned `key_vocabulary`; the remaining 112
  executable cards rely on generic help or attached legacy prose.
- Thirty-one executable cards have explicit `review_variants`; all 19 transfer
  cards also contribute two changed-art `variants` through `_review_variants`.
  Therefore 50/114 executable cards are review-capable and 64 have no
  changed-art bank (`share/v2_runtime.py:215-220,1834-1854`). This still does
  not prove family/stage-wide review coverage before mastery.
- Questions are assigned to the two standalone concept cards and the module
  check in each module (`share/gen_curriculum_v2.py:3443-3477`). The edit
  runtime asks questions only when the edit is a module check
  (`share/v2_runtime.py:1605-1618`); it does not run a paired interpretation or
  completion item before an ordinary edit.
- After completion, the runtime prints the next card but unconditionally enters
  `hold_open` (`share/v2_runtime.py:1450-1461`). There is no explicit action to
  start the next eligible lesson while motivation is high.
- The current `node` labels cannot prove the operator's finish-line sequence.
  M0–M8 already use `A0`–`A7` for the older skill tree, while M16–M18 reuse
  `A0`, `A3`, and `A6` for the newly added authoring stages. The still stages
  are present only as S2, S3, S5, and S7 on M12–M15; S0, S1, S4, and S6 have no
  explicit module-stage owner. The implementation proposal must add a distinct
  master-stage field rather than inferring the new S/A sequence from these
  overloaded display-node strings (`share/gen_curriculum_v2.py:109-2453`).

The module-range reports must replace these aggregate observations with a
card-by-card and command-family-by-command-family gap register.

## Required audit row

Each executable card must be logged with these fields:

1. Card ID and kind.
2. Required command families.
3. Normal/operator, standalone, or Ex grammar classification.
4. Prior explicit grammar explanation.
5. Prior interpretation question.
6. Prior completion question.
7. Prior guided performance.
8. Later hidden retrieval.
9. Changed-art review.
10. Card-owned `KEYS WORTH KEEPING` vocabulary.
11. Hint information gain over `DO THIS`.
12. Vim and ASCII-animation pairing.
13. Gap IDs and proposed insertion point.

For each newly encountered command family, the report must also identify the
first current hidden use and the earliest safe insertion point for all missing
stages. An attached legacy lesson is cited as source material, not credited as
a stage unless the current learner must read or answer it before performance.

## Validator requirements produced by the audit

The implementation phase must add validators which fail generation or tests
when any of the following occurs:

1. An executable card omits its command-family declarations.
2. A hidden card requires a family before explanation, interpretation,
   completion, and guided-performance evidence in curriculum order.
3. An executable card lacks a paired Vim-plus-animation question.
4. A family-specific mastery card lacks enforceable method evidence.
5. A changed-art review is absent after hidden retrieval.
6. A hidden card's vocabulary reveals its exact accepted key sequence.
7. A question or feedback path tests tutor metadata instead of transferable
   editing or animation knowledge.
8. A continuation action can skip a prerequisite, remediation, or unfinished
   module-check subpart.
9. An open typed-key question is graded by string equality rather than its
   declared cursor/buffer effect.
10. A question lacks an authored before/after/exception placement reason.
11. Any expert habit or S0–S7/A0–A7 stage lacks both a key-hidden performance
    and a later changed-art review.
12. A tutor path silently installs, disables, or reconfigures an operator-owned
    plugin, or treats a plugin hint/key display as grading evidence.

## Socratic question forms

The implementation proposal must use all of these forms intentionally:

- **Open typed keys:** ask for an edit or motion and execute the answer in an
  isolated scratch Neovim buffer. Grade the declared cursor position, buffer
  result, changed region, and any method constraint—not literal key equality.
- **Decode:** ask the learner to explain the parts and total effect of a visible
  command such as `:8s/-/=/g`.
- **Complete:** remove one meaningful grammar component and ask what completes
  the intention, including `<CR>` when execution is the missing step.
- **Predict:** show a start artifact and command, then ask for the resulting art
  or cursor state before executing it.
- **Why:** contrast operations with different grid effects, such as `r` versus
  `x`, and require the fixed-width animation reason.
- **Multiple choice:** retain it where distractors diagnose a meaningful
  misconception; do not use it merely because the current runtime supports it.

The grammar primer is the beginning of retrieval, not the end. Later cards
must revisit grammar components on unfamiliar art and with the keys hidden.

## Course finish-line source

The master-habit and stage inventory is the operator-provided source at
`/Users/r/.codex/attachments/499fbe13-648c-423a-855d-39c9339aede0/pasted-text-1.txt`:

- nine habits: overwrite; exact-cell landing; frame/layer objects; column
  editing; repeat at scale; register palette; frame comparison; cleanup and
  padding; safe variant exploration;
- still-authoring stages S0–S7 before animation stages A0–A7, plus the
  proportional Shift_JIS branch after S5;
- every stage must map its art need to the Neovim family that makes the work
  efficient, then require hidden performance and spaced changed-art review.

## Operator approval boundary

After review, logging, and proposal, stop and show the operator the complete
audit. Do not modify `share/gen_curriculum_v2.py`, `share/v2_runtime.py`, the
generated curriculum, or implementation tests until the operator approves the
proposed sequence and mechanics.

## Audit partitions

- `grammar-sequence-M0-M4.md`
- `grammar-sequence-M5-M9.md`
- `grammar-sequence-M10-M14.md`
- `grammar-sequence-M15-M18.md`
- `GRAMMAR_FIRST_AUDIT.md` will be the synthesized gap register and ordered
  implementation contract.

## Commit boundary

The requirement ledger, all four module-range reports, the synthesized gap
register, and the corresponding failure-log receipt must be committed before
any further curriculum, generator, runtime, or test implementation begins.
