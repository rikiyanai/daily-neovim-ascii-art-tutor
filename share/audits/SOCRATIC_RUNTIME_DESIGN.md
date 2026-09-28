# Socratic runtime design review (proposal only)

Status: reviewed and proposed; **operator approval is required before any
generator, curriculum, runtime, or test implementation**.

This document is the runtime/mechanics companion to the card-by-card grammar
audits. It does not change `share/gen_curriculum_v2.py`, `share/v2_runtime.py`,
the generated curriculum, or tests. It records the data contracts, state
transitions, safety boundaries, and acceptance tests that implementation must
follow.

## 1. Review basis and current boundary

The finish line is the operator-provided nine-habit inventory and the ordered
still stages `S0`–`S7`, followed by authoring stages `A0`–`A7`, with the
proportional Shift_JIS branch after `S5`. The source says that a command is
learned only after an unhinted method check/keystroke-budget requirement and a
spaced edit review, and that all still stages precede animation
(`pasted-text-1.txt:121-137`). The nine habits and stage-to-family mapping are
listed in the same source (`pasted-text-1.txt:11-119`).

The frozen curriculum has 19 modules, 152 cards, and 190 questions, but only
module checks own `question_ids`; ordinary executable cards have no required
paired concept check (`share/audits/GRAMMAR_FIRST_REQUIREMENT.md:45-72`). The
generator's `step` schema has no grammar family, grammar stage, paired-question,
or placement contract (`share/gen_curriculum_v2.py:70-87`), while card/question
assignment is confined to ordinals 3, 7, and 8
(`share/gen_curriculum_v2.py:3398-3492`).

All current questions are four-choice records and `ask_question` accepts only a
single shuffled letter (`share/v2_runtime.py:457-498`). The question schema and
runtime therefore have no typed-key semantic effect, decode parts, completion
blank, or authored placement rationale. The existing tests confirm the current
four-choice and paired-prompt invariants (`share/test_v2.py:104-128`) but do not
test these new forms.

The edit path prints a recipe when `show_recipe` is true and otherwise prints a
hint while hiding exact keys (`share/v2_runtime.py:1714-1731`), but the session
brief imports legacy key payloads into `KEYS WORTH KEEPING`
(`share/v2_runtime.py:604-640,720-729`). Result feedback can print the taught
path and method keys (`share/v2_runtime.py:1277-1351`), and completion prints a
next card before unconditionally holding the popup open
(`share/v2_runtime.py:1412-1461`). These are important information-leak and
continuation constraints for the proposed flow.

The partition audits identify the same structural defects at card level:

- M0–M4: no ordinary-card pairing, sparse review, and false-positive hint
  detection (`share/audits/grammar-sequence-M0-M4.md:177-237`).
- M5–M9: hidden first uses for `D`, `:m`, dot, macros, `:global`, `o`, `x`,
  and `i`, with no family-level review gate
  (`share/audits/grammar-sequence-M5-M9.md:104-165`).
- M10–M14: no before-use interpretation/completion stages, no ordinary-card
  pairing, and no changed-art requirement before mastery
  (`share/audits/grammar-sequence-M10-M14.md:115-191`).
- M15–M18: no card-owned pair or completion stage for the new families, and
  misleading slash-based hints on `C` cards
  (`share/audits/grammar-sequence-M15-M18.md:102-140`).

The implementation must preserve the existing target/method/review evidence
model rather than treating a matching final buffer as proof of a particular
method. Current method evidence is captured from the keylog and checked
separately (`share/v2_runtime.py:891-970`); changed-art review is built only
from a source-linked bank (`share/v2_runtime.py:1834-1882`).

## 2. Common authored contracts

### 2.1 Card contract

Every exercise card, including a module check and a spaced-review source, gets
these fields in the generated curriculum. Names are normative; implementation
may choose an equivalent representation only if the validator emits the same
meaning.

```text
grammar_families: [family-id, ...]
grammar_stage: one of [explanation, interpretation, completion, guided,
                       hidden, changed_art_review]
paired_question_ids: [question-id, ...]       # at least one for every exercise
pairing_exception: null | {
  reason: non-empty authored reason,
  approved_scope: non-empty authored scope
}
question_placement: {
  before: [question-id, ...],
  after: [question-id, ...],
  rationale: non-empty text per question-id
}
key_vocabulary: [grammar vocabulary lines, ...]
master_habits: [H1..H9, ...]
master_stages: [S0..S7, A0..A7, P?]
review_contract: {
  source_card_id: card id,
  changed_art_variants: at least 2 distinct starts,
  method_family: family-id,
  required_before_mastery: true
}
```

`paired_question_ids` is the machine-readable floor. `question_placement` is
not inferred from question order: each pair states why it belongs before the
performance, after it, or both. A card-specific exception is allowed only for
an exercise that genuinely cannot support a question; it must carry a written
reason and is a validator failure if used merely to avoid authoring a pair.

The card's `key_vocabulary` names grammar and scope without reproducing the
accepted sequence. For example, it may say “`[count] operator
[count] motion/text-object`” or “address/range + `:s` + pattern/replacement +
flags + `<CR>`”; it must not contain `gg3yyGp:4,6s/o/O/g<CR>` for a hidden
card. This directly implements the grammar-first requirement that hidden
cards expose vocabulary but not exact keys
(`share/audits/GRAMMAR_FIRST_REQUIREMENT.md:14-20`).

`master_habits` and `master_stages` are distinct from display `node`. The audit
notes that current `node` values overload old and new `A` labels and cannot
prove the finish-line sequence (`share/audits/GRAMMAR_FIRST_REQUIREMENT.md:76-82`).

### 2.2 Question common contract

Every question has:

```text
id, card_id, module_id, form, prompt, source_ref
grammar_family, grammar_breakdown_id
paired_invariant             # the ASCII-art invariant being tested
placement: before | after | both
placement_reason             # non-empty, card-specific
answer_contract              # form-specific object below
feedback: form-specific breakdowns, not answer recipes
```

`card_id` is mandatory even when a question is also useful in a module bank.
Module checks may sample several card-owned questions, but the sampled event
retains the owning card and the module-check subpart. A question cannot satisfy
pairing for a different card merely because it has the same module.

The `form` value is one of `typed_keys`, `decode`, `complete`, `predict_art`,
`why`, or `multiple_choice`. Multiple choice remains available for a
diagnostic misconception, but it is not the default generated form. The
question author must select the form because it tests the card's specific
operation, not because it is the only form supported by the current runtime.

### 2.3 Evidence contract

Each attempt writes one append-only `question` event containing:

```text
question_id, card_id, module_id, form, result, attempt_number
raw_answer                  # exact typed response or selected option id
normalized_answer           # parser output, when safe to retain
evidence: {
  prompt_sha256,
  rendered_artifact_sha256,
  grammar_breakdown_id,
  placement,
  effect_before,
  effect_after,
  method_evidence,
  forbidden_side_effects,
  evaluator_version
}
feedback_breakdown_id       # on failure
```

Raw key bytes are retained only in the per-attempt scratch/session evidence
file, with restrictive permissions, and are referenced from the event by hash
plus path. The event must not contain command history, environment variables,
or arbitrary command output. Existing events are append-only and projected into
progress (`share/v2_runtime.py:255-366`); the new event fields must preserve
that property.

## 3. Typed-key open questions

### 3.1 Purpose and grading rule

The learner sees an intention such as “go down four lines—type it,” then types
keys. The evaluator grades the declared semantic effect, not literal text. A
motion scenario may therefore accept both `4j` and `:+4<CR>` if both produce
the required cursor result and no forbidden side effect. The scenario may add a
method constraint only when the learning claim is family-specific (for example,
“use single-cell replace to preserve the grid”); effect equality alone must not
award that claim.

This is the required behavior in GF-14
(`share/audits/GRAMMAR_FIRST_REQUIREMENT.md:26-31`) and is intentionally
different from the current exact/token method checks
(`share/v2_runtime.py:939-970`).

### 3.2 Scenario schema

```text
answer_contract: {
  form: typed_keys,
  scenario_id,
  prompt,
  initial: {
    lines: [string, ...],
    cursor: {row: 1-based int, col: 0-based int},
    mode: normal | insert | visual_char | visual_line | visual_block,
    visual_anchor: optional {row, col},
    options: allowlisted option/value pairs,
    registers: allowlisted seeded registers only
  },
  required_effect: {
    buffer: unchanged | exact_lines | changed_region,
    changed_region: optional row/column bounds,
    cursor: exact | delta | predicate,
    mode: optional final mode,
    selection: optional predicate,
    registers: optional allowlisted predicates
  },
  allowed_methods: optional [method-family or token predicates],
  forbidden_methods: optional [method-family or token predicates],
  forbidden_side_effects: [write, shell, option_change, register_change,
                           mark_change, extra_window, extra_tab, ...],
  termination: {sentinel: <F12>, timeout_seconds: 90},
  grading: {effect_version, method_version}
}
```

The initial state is explicit, including mode and cursor. A scenario that
tests `r` versus `x` must seed a fixed-width row and assert that the changed
cell is replaced while the row length and all out-of-scope cells remain equal.
A scenario that tests Ex range grammar must seed enough rows to distinguish a
one-line address from a range and record the final buffer and cursor.

### 3.3 Scratch-Neovim execution boundary

The evaluator runs a short-lived scratch Neovim process, never the learner's
project buffer. It uses:

1. a temporary directory and temporary artifact only;
2. `-u NONE`, `-i NONE`, `-n`, and `--noplugin`-equivalent clean startup;
3. a sanitized environment with temporary `HOME`, XDG data/state/config/cache,
   locale, and working directory;
4. an OS-level process/filesystem sandbox if available, with write access only
   to the harness temporary directory and no network; and
5. a tutor-owned finish mapping on `<F12>` in Normal, Visual, Insert, and
   command-line mode.

`<F12>` is a submission sentinel, not part of the learner's answer. The
mode-specific mapping snapshots state *before* it exits/aborts the current
mode, writes the evaluator record, and quits. If the answer is in an Ex
command line, the record includes `getcmdtype()`, the command-line text, and
cursor position before the sentinel aborts it. A command ending in `<CR>` is
captured after execution. This makes termination unambiguous for all four
answer states:

| Answer state at sentinel | Captured evidence | Accepted only if |
|---|---|---|
| Normal | buffer, cursor, mode, registers/options diff | required Normal effect and final mode pass |
| Visual char/line/block | buffer, cursor, visual anchor/extent, mode | selection/effect and scope pass |
| Insert | buffer, cursor, mode, inserted span | required bytes/region and final mode pass |
| Ex command line | command type/text/position plus post-command buffer/cursor | command was executed or intentionally completed per scenario; no forbidden side effect |

The process is killed with its whole process group at timeout. A crash,
terminal loss, incomplete sentinel, or non-zero harness exit is an ungraded
failure and schedules remediation; it is never treated as a wrong key answer.
The evaluator records `timeout`, `crash`, or `sandbox_violation` separately
from `effect_mismatch`.

### 3.4 State and effect capture

Capture these snapshots before and after the answer:

```text
buffer_sha256, lines, line_count, line_lengths
cursor: row, col, byte_col, virtual_col
mode, visual_anchor, visual_cursor
options: only allowlisted names
registers/marks: only allowlisted names
window_count, tab_count, current_file, modified, write_events
shell_events, terminal_events, external_command_events
raw_keylog_sha256, normalized_tokens
```

`buffer` comparison is byte-aware and preserves trailing spaces. The effect
matcher supports exact lines, bounded changed region, cursor delta, and
predicates such as “same column after four downward moves.” It reports the
first differing row/column and the first forbidden event. It must not reduce a
cursor effect to a key-string comparison.

The answer is accepted iff all required effects pass, every forbidden-side-
effect set is empty, and any declared method constraint passes. For a generic
“go down four lines” question, `allowed_methods` is absent; for a question
whose paired invariant is fixed-width overwrite, `allowed_methods` may require
the `r`/`R` family and reject an Insert/delete route even if the final bytes
happen to match.

### 3.5 Ex, Normal, Visual, and Insert answer policy

The harness must permit ordinary Ex answers needed by the question, including
`:...<CR>`, but reject or abort these before execution:

- `:!`, `:shell`, `:terminal`, `:make`, `:w !`, `:read !`, `:write !`, and
  shell/filter forms;
- `:source`, `:runtime`, `:packadd`, `:lua`, `:python`, `:perl`, `:ruby`, and
  other interpreter/plugin-loading forms;
- writes (`:w`, `:update`, `:wall`, `:saveas`, `:write`) unless a scenario
  explicitly declares a temporary output and a write proof; and
- commands that open extra windows/tabs, alter the process, or modify
  non-allowlisted options/registers.

The command-line gate is an allowlist for the scenario's declared Ex family,
not a blacklist. A rejected command is recorded as a forbidden side effect and
does not enter command history. Normal/Visual/Insert answers use the clean
default maps plus the finish sentinel; tutor mappings are excluded from method
tokens. The art-buffer route continues to use the operator's configured
Neovim, as required by GF-11/GF-12; only the semantic scratch evaluator is
clean and isolated (`share/audits/GRAMMAR_FIRST_REQUIREMENT.md:24-25`).

## 4. Decode, complete, predict, why, and multiple choice

### 4.1 Decode

`decode` displays a command and asks the learner to identify its parts and total
effect. Example prompt: “What does `:8s/-/=/g` do?”

```text
answer_contract: {
  form: decode,
  display: ":8s/-/=/g",
  parts: [address_or_range, command, pattern, replacement, flags, execution],
  accepted_parts: {
    address_or_range: "line 8",
    command: "substitute",
    pattern: "-",
    replacement: "=",
    flags: [global],
    execution: "Ex command execution / <CR> when typed"
  },
  accepted_effect: "replace every '-' with '=' on line 8"
}
```

The learner may enter structured labels or a short free response. Normalization
maps synonyms (`line 8`, `8`, `single-line address 8`) to the same semantic
part, but does not accept an answer that confuses range, pattern, replacement,
or flag. Evidence stores the raw response, normalized part map, missing/wrong
parts, and the matched breakdown id.

### 4.2 Complete

`complete` removes one meaningful component, not a cosmetic character:
“`:8s/-/=/ …` — what finishes it?”

```text
answer_contract: {
  form: complete,
  template: ":8s/-/=/…",
  missing: execution,       # or address/range, command, pattern, replacement, flag
  accepted_tokens: ["g", "<CR>"],
  accepted_semantics: "global replacement on line 8, then execute",
  forbidden_tokens: ["%", "<C-u>"],
  placement: before
}
```

When the missing component is execution, `<CR>` is part of the answer
contract. When the missing component is a range, the answer is graded as an
address/range structure rather than exact punctuation where equivalent Ex
addresses are allowed. Evidence records the filled template, parsed grammar,
and whether the learner supplied the execution step.

### 4.3 Predict art

`predict_art` presents the starting artifact and a visible command or command
family, then asks for the resulting art/cursor state before running it. It may
use an authored output artifact answer when exact rows are appropriate, or a
small diagnostic choice bank when free-text art would be ambiguous. A choice
bank must remain a diagnostic form, not the generator default.

```text
answer_contract: {
  form: predict_art,
  before_lines: [...],
  command_display: ":8s/-/=/g",
  expected: {lines: [...], cursor: optional {...}, invariant_tags: [...]},
  answer_mode: artifact_text | semantic_tags | choice,
  distractor_diagnostics: [scope_error, omitted_g, row_shift, ...]
}
```

For `artifact_text`, compare normalized rows while preserving meaningful
spaces and report the first mismatch. For `semantic_tags`, require the changed
row/region plus the preserved animation invariant. For `choice`, evidence
stores the artifact option id and its rendered-artifact hash, not only a letter.

### 4.4 Why

`why` asks for the authoring reason behind a command choice: “Why `r` and not
`x` here?” The answer contract requires transferable invariant tags and permits
short explanation text:

```text
answer_contract: {
  form: why,
  contrast: ["r", "x"],
  required_claims: [fixed_width, overwrite_in_place, no_right_shift],
  forbidden_claims: ["x is always wrong"],
  paired_invariant: "frame columns remain registered"
}
```

The rubric grades claims, not prose similarity. A response can be correct in
different words if it establishes the fixed-width consequence. Evidence stores
the raw response, extracted tags, omitted tags, and feedback breakdown.

### 4.5 Multiple choice

The current four-choice pair remains a valid `multiple_choice` record when its
distractors distinguish a specific misconception. It must continue to include
both animation and Neovim halves and mistake-specific feedback, as required by
GF-08 (`share/audits/GRAMMAR_FIRST_REQUIREMENT.md:21-23`). It is not acceptable
to convert every new question to a choice merely to reuse `ask_question`.

## 5. Placement and grammar recurrence

The authored order for a new family is:

```text
explanation -> interpretation -> completion -> guided performance
           -> hidden retrieval -> changed-art spaced review
```

This is the frozen teaching-order requirement (`share/audits/GRAMMAR_FIRST_REQUIREMENT.md:14-20`), and the grammar primer is a bridge rather than permanent
proof. Every later unfamiliar-art use repeats the relevant grammar components,
with the exact keys hidden where the stage is retrieval.

For each card, the generator author records placement as follows:

- `before`: interpretation/decode/complete/why question makes the learner work
  out the command before the exercise; use this for first family use or a
  hidden family that has not yet had completion evidence.
- `after`: predict/why/generalization question uses the just-completed art to
  name the invariant or distinguish a valid alternate method; use this when
  performance is needed to make the visual evidence concrete.
- `both`: a pre-question makes the operation predictable and a post-question
  generalizes it to changed art; use this for first use of a family tied to a
  high-risk grid invariant (`r`/`x`, block edits, frame copies, Ex ranges).
- `pairing_exception`: only with a written card-specific reason, such as a
  pure playback/hold exercise whose only new evidence is a previously mastered
  timing state. The exception still appears in coverage reports and cannot
  hide a missing family review.

The floor is one paired question per exercise. A module-check question bank may
add checks, but it cannot be the sole pair for an ordinary executable card.
The partition reports document the current absence of this floor
(`share/audits/grammar-sequence-M15-M18.md:142-152`).

## 6. Wrong-answer flow without recipe leakage

### 6.1 Transition

Use this state machine for every question form:

```text
READY
  -> PRESENT(question, grammar_breakdown_id)
  -> CAPTURE(answer/effect)
  -> PASS -> RECORD(question pass) -> PERFORMANCE or RESULT
  -> FAIL -> RECORD(question fail + breakdown id)
          -> RECORD_DAILY_PRACTICE_ONCE(no XP/card/family/mastery credit)
          -> SHOW_BREAKDOWN(relevant grammar only)
          -> REMEDIATION_SCHEDULED(changed stem/variant)
          -> RETRY(question or eligible remediation)
```

The fail path must not call the existing generic concept replay as-is. Current
feedback prints the selected and correct choices (`share/v2_runtime.py:1295-1310`)
and then prints taught paths/alternatives in the non-compact debrief
(`share/v2_runtime.py:1328-1351`), which can reveal the hidden exercise recipe.
The daily-practice event is distinct from mastery evidence: one genuine
submitted wrong question counts toward today's practice and streak, exactly as
a failed artifact attempt does, while progress, XP, card completion, and
family/module mastery remain unchanged.

### 6.2 Breakdown content

Each authored question points to a `grammar_breakdown_id` whose content is
limited to the relevant grammar:

- Normal operator: `[count] + operator + [count] + motion/text-object`, with
  scope and the animation invariant; do not print the accepted sequence.
- Standalone Normal: command, operand, scope, and mode exit; do not print the
  exact key path unless the exercise is explicitly in the explanation stage.
- Ex: address/range + command + pattern/replacement/arguments + flags +
  execution; keep the missing component blank for a failed completion item.
- Visual/Insert: selection shape or insertion/replace scope and the fixed-width
  consequence.

For typed-key failure, the breakdown includes the observed effect mismatch:
“cursor ended two rows lower than required,” “row length changed,” or
“forbidden write command attempted.” It includes the relevant grammar row and
the next question prompt, but never the hidden accepted key sequence.

For decode/complete failure, re-show the exact component names and the learner's
wrong/missing component; keep the unrevealed token blank. For predict/why,
re-show the violated art invariant and grammar scope, not the answer recipe.

The renderer must expose `breakdown_id`, `grammar_family`, and a compact
explanation, while an internal event retains full evidence. A regression test
must assert that a failed hidden card's feedback contains no `expected`, method
alternative keys, or recipe key line.

## 7. Optional “next eligible item”

### 7.1 Result-page controls

Every result page offers exactly two explicit actions:

```text
Enter / q  close this result and return to the popup caller
n          continue to the next eligible lesson/question
```

`n` is optional and never implicit. The page must say when no eligible item
exists. The current result page has only “press Enter for skill-tree progress”
(`share/v2_runtime.py:1180-1197`), and `_complete` only prints the next card
before `hold_open` (`share/v2_runtime.py:1451-1461`); the new action therefore
needs a distinct transition rather than a second print line.

### 7.2 Eligibility ordering

Compute an immutable eligibility snapshot when the result page opens. The
candidate order is:

1. the current card's active remediation, including a failed typed question or
   failed method/effect attempt;
2. a due changed-art review, unless it would interrupt an unfinished module
   check subpart;
3. an unfinished module-check subpart: remaining concept questions first, then
   its key-hidden artifact;
4. the next unpassed card in the first unlocked module; and
5. the next due review or no candidate.

The remediation row must be consumed before an unrelated card. Existing
progress tracks active remediations and reviews (`share/v2_runtime.py:277-347`)
and `next_card` currently skips only locked modules and passed cards
(`share/v2_runtime.py:404-413`). The proposed selector extends, rather than
replaces, those predicates.

Eligibility rejects a candidate when:

- a module prerequisite is not mastered;
- an earlier card in the same module is not passed;
- an active remediation for that card has not been completed;
- a module-check concept threshold is pending or its artifact subpart is
  pending;
- its grammar prerequisite/hidden stage is not satisfied;
- the daily practice cap has been reached; or
- it is a duplicate already passed item that would award progress.

Explicit `n` may continue practice only when the daily cap policy allows it.
It may never bypass a cap by awarding a result after the cap, and it may not
turn a preview into a pass. Existing automatic routing enforces a daily cap and
cooldown before selecting a card (`share/v2_runtime.py:2198-2215`); the
continuation selector must call the same policy with an explicit reason.

### 7.3 Popup lifecycle and locking

The result flow is:

```text
feedback page -> progress page -> choice page
  Enter/q -> close, signal post-render, release session lock
  n       -> signal/clear old page, select eligible item, keep one session lock,
             render the new question/brief, then run it
```

There must be no recursive call that leaves an old `hold_open` or lock active.
The implementation should return a typed continuation result to the top-level
router, which reacquires or retains the single `SessionLock` exactly once. A
user-config popup remains the outer UI; the art buffer and question scratch
buffer are separate. Headed route tests already model question/feedback/post
signals and real-config loading (`share/test_tmux_v2_routes.py:121-210`), so
the continuation test must assert that no stale signal causes a second popup or
consumes cooldown without a durable pass/fail event.

## 8. Validator and regression design

### 8.1 Curriculum/generator validators

Add proposal-level validators with these failure conditions:

1. Every executable card declares at least one `grammar_family` and one
   `paired_question_id`, or carries a non-empty card-specific exception with a
   reason. Every pair points to that card's question and names both the
   Neovim operation and ASCII-art invariant.
2. Every question has a form-specific `answer_contract`, a placement reason,
   `grammar_breakdown_id`, and `paired_invariant`.
3. For every family, the first hidden use has preceding explanation,
   interpretation, completion, and guided evidence. A later changed-art review
   is required before family-specific mastery. Legacy payloads, distractors,
   answer keys, and generic hints do not count, matching the audit's “does not
   count as teaching” rules (`share/audits/GRAMMAR_FIRST_REQUIREMENT.md:33-43`).
4. Hidden briefs include family vocabulary but not exact accepted sequences or
   method-alternative keys. Card-owned vocabulary is required; legacy prose is
   provenance only.
5. `master_habits` covers all nine habits and `master_stages` covers every
   `S0`–`S7` and `A0`–`A7`, plus the proportional branch after `S5`. For every
   item, the report finds at least one hidden performance card and at least one
   source-linked changed-art spaced review card.
6. Every review source has at least two distinct changed-art starts, a declared
   method family, and `required_before_mastery=true`. Transfer identity alone
   does not satisfy changed-art review.
7. Every new Normal family declares whether it is operator grammar or a
   standalone command. Every Ex family declares address/range, command,
   arguments/pattern/replacement, flags, and execution key. The current audit
   already calls for these classifications (`share/audits/GRAMMAR_FIRST_REQUIREMENT.md:214-229`).
8. A typed-key contract cannot specify literal answer equality as its only
   grader. It must contain a semantic effect predicate and an explicit
   forbidden-side-effect set.
9. A `next` transition cannot be generated without remediation, prerequisite,
   module-check, review, daily-cap, and popup-lifecycle predicates.

### 8.2 Runtime unit tests

Use deterministic fake scenarios plus real Neovim subprocesses:

- **Typed effect equivalence:** seed five lines and a cursor; run `4j` and
  `:+4<CR>` in separate scratch processes; assert equal required cursor/buffer
  effect and distinct normalized key logs. Run a wrong motion and assert an
  effect mismatch. This specifically proves GF-14 rather than string equality.
- **Mode termination:** submit from Normal, Visual, Insert, and a pending Ex
  command line with `<F12>`; assert the pre-sentinel mode/selection/command
  line was captured and the process exited cleanly.
- **Safety:** attempt `:w`, `:wq`, `:!true`, `:read !true`, `:source`, and a
  plugin/interpreter command; assert no external command, repo write, extra
  window, or persisted history, and that the event is a sandbox/forbidden
  failure rather than a pass.
- **Decode/complete:** test each missing Ex part (range, command, pattern,
  replacement, flag, `<CR>`) and assert the normalized component evidence and
  mistake-specific breakdown.
- **Predict/why:** assert changed-art rows and required invariant tags; ensure a
  visually similar but width-shifting result fails.
- **Placement:** for a sample of every family, assert the before question is
  recorded before guided/hidden performance and the after question follows the
  resulting artifact. Assert a missing placement reason fails generation.
- **No leak:** render a failed hidden-card result at compact and full widths;
  assert grammar vocabulary and mismatch evidence are present while exact
  `expected`, recipe lines, and method alternatives are absent.
- **Pair floor:** count all executable cards, require one or more paired
  question IDs, and require each question event before method-specific credit.
- **Grammar recurrence:** remove any later family decode/complete stage from a
  fixture and assert the validator fails even when M0 has a primer.
- **Finish-line coverage:** build a coverage matrix for nine habits, `S0`–`S7`,
  `A0`–`A7`, and `P`; assert hidden performance + changed-art spaced review for
  every required item, and assert the overloaded display `node` cannot satisfy
  the matrix by inference.
- **Mastery gate:** pass a hidden edit and transfer while omitting changed-art
  review; assert no family mastery. Pass the linked review and assert the
  review stage/effect/method evidence is recorded before mastery.
- **Continuation matrix:** seed active remediation, due review, unfinished
  module-check questions, locked prerequisites, daily-cap reached, and course
  complete. Assert `n` chooses only the permitted candidate and never awards
  XP without a pass.
- **Failed-practice accounting:** submit one wrong answer and one failed edit;
  assert each increments today's practice exactly once, preserves streak
  participation, and leaves XP/card/family/module mastery unchanged. Retry and
  rendering events must not double-count either attempt.
- **Debrief viewport contract:** at 80×24, 100×36, and 188×49 require the
  artifact replay, actual-versus-taught two-column ledger, method diagnosis,
  skill tree/module status, XP, level, today count, and streak across the held
  feedback/progress journey.

### 8.3 Regression suites to retain

The current tests execute generated targets in real Neovim and verify keylog
round-trips (`share/test_v2.py:775-880`), changed-art banks
(`share/test_v2.py:832-903`), held feedback/progress pages
(`share/test_v2.py:905-974`), and module mastery evidence
(`share/test_v2.py:976-1034`). New tests must be additive and continue to run:

```text
python3 share/test_v2.py
python3 share/test_v2.py --real
python3 share/test_tmux_v2_routes.py
```

Headed runs must cover 80×24, 100×36, and 188×49, with the operator's config
where GF-12 requires it. Existing tests use clean `nvim -u NONE -i NONE` for
deterministic recipe replays (`share/test_v2.py:554-559`); typed-key safety
tests use the same clean route plus the explicit scratch sandbox. A separate
headed test proves the ordinary art route still keeps the user's lualine,
relative numbers, WhichKey, Hardtime, mappings, and theme while tutor-owned
chrome is only used in clean mode.

## 9. Threat and failure analysis

| Threat/failure | Required design response | Proof |
|---|---|---|
| Key notation ambiguity (`<C-v>`, `<CR>`, literal `<`, UTF-8 glyphs) | One tokenizer with explicit token grammar; reject unknown angle tokens; preserve raw bytes and normalized tokens separately; never concatenate strings into a shell command. | Tokenizer round-trip tests extend `share/test_v2.py:35-61`; unknown-token and UTF-8 fixtures. |
| Arbitrary Ex or shell escape | Clean process, command allowlist at command-line submission, OS sandbox, no network, no shell-capable commands, whole-process timeout/kill. | Safety tests above; event must say forbidden/sandbox failure. |
| Plugins/remaps alter semantics | Scratch evaluator uses clean startup and temporary XDG paths; art-buffer exercise remains headed/configured. Capture startup mode/options and evaluator version. | Clean-vs-real-config split; existing real route at `share/test_tmux_v2_routes.py:139-163`. |
| Nondeterminism (`:global`, timing, terminal size, locale) | Fixed locale/env, deterministic seed, no network/time-dependent answer predicates, snapshot exact bytes, rerun same scenario twice and compare effect hashes. | Two-run determinism test; no timestamps in semantic hash. |
| Command-line history or shada leaks | `-i NONE`, temporary HOME/XDG, no persistent shada, no rejected command in history, restrictive evidence permissions, event stores hashes not environment. | Inspect temp tree after exit and assert no history/shada outside it. |
| Terminal control/buffered escape bytes | PTY parser accepts declared key tokens only; escape is a token, terminal CSI/OSC is rejected; `<F12>` sentinel is out-of-band and stripped from learner tokens. | Raw-byte fixtures and terminal-control injection test. |
| Accidental writes or modified repo art | Scratch path only; `:w`/shell/filter commands rejected; artifact writes are temporary and deleted after evidence hash; existing project checkpoints remain untouched on question failure. | Snapshot write-event test; existing checkpoint recovery at `share/test_v2.py:666-719`. |
| Semantically valid but pedagogically forbidden method | Effect predicate is necessary; `allowed_methods`/`forbidden_methods` and method evidence are separately checked for family mastery. Generic effect questions omit the method constraint. | `r` vs `x`, overwrite-vs-insert, and compare-method fixtures. |
| Sentinel pressed during a pending Ex command | Capture command-line type/text before abort; do not claim execution; command must satisfy an execution-aware contract. | Normal/Visual/Insert/Ex termination matrix. |
| Timeout/crash interpreted as learner failure | Separate evaluator status; no mastery/XP; schedule remediation only after a clean effect mismatch or explicit runtime failure policy. | Event-state tests for timeout, crash, and retry. |
| Wrong-answer feedback leaks hidden recipe | Breakdown renderer receives only grammar family, scope, invariant, and observed mismatch; hidden expected/recipe fields are unavailable to it. | Rendered-text no-leak assertions at all viewport sizes. |
| Next action skips remediation/review/cap | Eligibility snapshot is validated before transition; next result stores candidate id and eligibility reasons; no credit on selection. | Continuation matrix and event projection tests. |

## 10. M0 primer and sequence contract

The implementation proposal must author a grammar primer at the beginning of
M0 and make the sequence explicit. The primer is explanation plus interpretation
and completion; it is not hidden performance credit. The complete M0 sequence
is:

1. **Primer (before M0.01):** Normal grammar is `[count] operator [count]
   motion/object`; standalone commands have their own scope (`r`, `R`, `p/P`,
   `o/O`, `u`, `J`); Ex grammar is `:[address/range] command
   /pattern/replacement/flags <CR>`. Ask one decode question and one complete
   question with grammar parts visible, then state the fixed-grid consequence.
2. **M0.01 — `r`:** show a guided one-cell overwrite. Ask before: “The core
   marker is one cell and the rays must not move; which standalone operation
   changes that cell in place?” Ask after: “Why does this preserve registration
   while deletion/insertion would not?” Record `r` as standalone command,
   cursor scope, and fixed-width invariant.
3. **`yy/p` guided step (the copy part of current M0.02):** show the complete
   frame copy with the counted linewise operator and put. The current M0.02
   combines this with substitution (`share/gen_curriculum_v2.py:146-157`),
   so the approved curriculum must either split the visible operation into
   two paired substeps or author an explicit bridge card; it must not pretend
   that the combined recipe taught two families independently. Ask before:
   “You need the three-row frame as one object; what does the count, operator,
   and linewise put each contribute?” Ask after: “What would a one-line yank do
   to the frame boundary?”
4. **`o` guided bridge (before the hidden retrieval):** `o` is a standalone
   row-creation command, not an operator-grammar suffix. The current M0.03 is
   a concept card with question IDs, not an `o` performance card; the approved
   design must insert a guided `o` exercise or explicitly assign this bridge to
   a new pre-M0.04 card. Ask before: “Which standalone command creates a new row
   below without shifting existing glyphs inside a row?” Ask after: “How does
   the new row preserve the frame's registered height?”
5. **`:s` with a range and `g` guided step (the Ex part of current M0.02):** ask
   before: “Complete `:8s/-/=/ …` and identify address, command, pattern,
   replacement, flag, and execution.” Then require a visible bounded
   substitution before any hidden use. Ask after: “Why does the one-line
   address plus `g` alter every dash on row 8 while leaving other rows
   untouched?”
6. **M0.04 hidden retrieval:** after the primer, `r`, `yy/p`, `o`, and bounded
   Ex substitution have each been worked out and typed visibly, require the
   key-hidden M0.04 artifact. Its paired question is before the edit (complete
   or decode on the unfamiliar range) and after the edit (why the range and
   `g` preserve the frame invariant).
7. **M0.04 review:** require a changed-art variant with the same Ex family and
   a different row/material arrangement. Its question is after the fresh art
   performance and asks the learner to decode the same grammar on the new
   address. The review is required before M0 mastery.

The exact M0 key paths remain curriculum data owned by the approved generator;
this document deliberately states the grammar and question contracts without
revealing hidden exercise recipes.

## 11. Operator gate

This review is complete when the operator has seen and approved the complete
audit, including this design, the 152-card placement/coverage proposal, the
new failure-log entry, and the M0 sequence. **No implementation may begin
before that approval.** In particular, do not modify
`share/gen_curriculum_v2.py`, `share/v2_runtime.py`, generated curriculum,
runtime tests, or popup scripts as part of this proposal.
