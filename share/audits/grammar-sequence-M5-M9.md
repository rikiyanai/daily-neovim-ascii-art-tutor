# Grammar-sequence audit: M5–M9

**Audit scope.** This is a read-only audit of the generated v2 curriculum,
its generator, runtime lesson brief, legacy attachments, and current tests. It
covers the 30 executable cards (`.01`, `.02`, `.04`, `.05`, `.06`, `.08` in
M5–M9) and the 50 module questions. It does not edit curriculum or runtime.

**Requirement audited.** A command family is counted as taught only when the
learner has first received a grammar explanation, then a paired conceptual
interpretation/completion check, then a guided ASCII-animation performance
card, then a later key-hidden retrieval, and finally a changed-art spaced
review before a mastery claim. A legacy attachment or answer-key occurrence is
not teaching evidence. The three grammars must remain distinct:

```text
Normal operator: [count] operator [count] motion-or-text-object
Normal standalone: r<char>, p, x, o/O, ., q/@, and similar commands
Ex: :[address-or-range] command /pattern/replacement/ flags <Enter>
```

## Executive finding

The M5–M9 strip is strong as an animation project and as a source of paired
animation/Neovim multiple-choice items, but it is not yet grammar-first. The
generator creates recipes and action-level hints, not a dependency ledger for
grammar → conceptual interpretation → guided performance → retrieval → review.
The first-use gate is violated for Visual-line yank, `D`, `:t`, `:m`, `dd`,
`o`, `.`, macros, `:global`/`:normal`, `x`, and standalone `i`. Several of
these first appear in hidden or comparison paths. Most executable cards have no
changed-art review bank, while module mastery is still awarded from five
questions plus one artifact edit.

The existing question bank does pair an animation half with a Neovim half and
has four choices with choice-specific feedback. That is valuable evidence, but
it is not the required command-completion sequence: the questions ask the
learner to choose an already-written explanation, rather than fill a missing
grammar component. The concept card is also normally after the first two
guided cards, not before the first use of the new family.

The legacy disposition correctly warns that nearest-card mapping is not
mastery migration (`share/LEGACY_CURRICULUM_DISPOSITION.md:3-15`). The runtime
still renders the attached legacy prose and keys in the brief
(`share/v2_runtime.py:604-622,667-678,720-741`), so those lines were recorded
for visibility only, never as proof that the family was sequenced correctly.

## Evidence anchors

| Area | Direct evidence | Audit implication |
|---|---|---|
| M5–M9 authored recipes | `share/gen_curriculum_v2.py:567-663` (M5), `:665-757` (M6), `:760-857` (M7), `:859-933` (M8), `:935-1010` (M9) | These are the source-of-truth executable recipes. |
| Card construction | `share/gen_curriculum_v2.py:3398-3493` | Only ordinals 1/2 show recipes; 4/5/6/8 hide them. Concepts are attached at ordinals 3/7 and module checks at 8. No grammar dependency is generated. |
| Concept question construction | `share/gen_curriculum_v2.py:3115-3220` | Questions have animation and Neovim halves, four choices, and feedback, but no separate grammar decomposition or completion-item field. |
| Question/card ordering | `share/gen_curriculum_v2.py:3443-3477` | Mx.03/Mx.07 questions are selected after Mx.01/Mx.02 and before Mx.08; they are not linked to each command family or guaranteed before its first use. |
| Briefs and hints | `share/v2_runtime.py:625-753` | Hidden cards receive a generic fallback key list unless `key_vocabulary` or a legacy payload is attached; `action_hint()` explains scope but not grammar. |
| Review gate | `share/gen_curriculum_v2.py:3483-3491`; `share/v2_runtime.py:116-135,1834-1854,1885-1933` | Only transfer cards and cards with explicit `review_variants` become changed-art reviews. Most M5–M9 executable cards do not. |
| Existing tests | `share/test_v2.py:88-108,141-151,175-193,767-815` | Tests enforce counts, paired question shape, recipe hiding, and real-Neovim passability; they do not enforce first-use grammar ordering, completion questions, or review coverage for every family. |
| Scope principle | `share/CURRICULUM_V2_SPEC.md:228-253` | The design already says answer-key occurrence is not coverage, but the implementation has no family-level evidence ledger to enforce that principle. |

## Command-family sequence audit

`guided` means a card whose exact recipe is visible and which performs an
animation edit. `hidden` means the exact path is withheld. `post-Q` means a
concept item exists, but only after the first use or after the card being
audited. `review` means a source-linked changed-art bank is actually present;
the mere existence of a transfer card is counted only for that transfer card.

| Family and grammar to teach | First/early use in current course | Prior grammar + conceptual check | Later hidden retrieval | Changed-art review before mastery | Finding |
|---|---|---|---|---|---|
| `r<char>` — standalone Normal replace; fixed-width one-cell edit | M0.01 guided, then M5.01/M5.06/M5.08, M6.01, M8.01/M8.06, M9.01/M9.06 | M0.01 is a guided recipe, but no pre-use grammar/completion item. M5 questions Q01/Q03/Q09/Q10 interpret `r` only after use (`curriculum-v2.json:15505-15834`). | M5.04/M5.08 and later transfer/check cards | Only M5.06, M8.06, M9.06 have transfer review; M5.01/M5.08/M6.01/M8.01/M9.01 do not | Grammar explanation and completion retrieval are missing even though the operation is familiar. |
| `f{char}`/`F{char}` — standalone landmark search, not an operator object | Visible in M0.01 (`0f.`); used in M5.08, M7.04–.06, M9.01/.06/.08 | M0.01 exposes a recipe, but no prior interpretation/completion check for `f`; module Qs later ask a landmark question. | M5.08, M7.04/.06, M9.06/.08 | Only transfer cards M7.06 and M9.06 review changed art | Treat as its own standalone family; do not infer it from `r` or from a legacy `find-char` attachment. |
| `[count]yy` plus `p/P` — Normal linewise operator/put grammar | Guided at M0.02; repeated at M3.02/M4.02 and M5.02/M8.02/M9.02 | M0.02 has explicit key vocabulary (`curriculum-v2.json:766-768`), but the M0.03 conceptual item is after that guided card. M5.Q02/Q08 and later Qs are post-use checks. | M5.05 alternatives, M8.04 onward, M9.05 comparison | No review bank on M5.02/M8.02/M9.02; transfer-only reviews do not cover all linewise-copy sources | Partial teaching exists; strict grammar-before-concept ordering is not satisfied. |
| `V{motion}y/p` — Visual-line selection followed by linewise yank/put | First real use is hidden M3.06; first visible recipe is M5.02 `ggV6jyGp` (`curriculum-v2.json:3693`) | No guided Visual-line introduction before M3.06. M5.Q02/Q08 explain the result after M5.02. | M5.05 comparison and M5.08 check can retrieve whole-frame scope | No M5 Visual-line review bank | First-use-before-guided and first-use-before-concept gap. Add a guided Visual-line grammar card before M5.02 or move M5.02 earlier as that card. |
| `C` = `c$` — Normal change-to-end-of-line alias, followed by Insert text/Escape | Guided M4.01; used M5.04/.05, M8.02/.08, M9.02/.05 | M4.01 has a visible recipe and legacy `C = c$` prose, but no prior completion item. M5/M8/M9 Qs explain row scope only after use. | M5.04/.05, M8.02/.08, M9.02/.05 | None of these source cards has a changed-art bank | Teach the alias as operator grammar (`c` + `$`) and separately identify Insert-mode completion. |
| `D` = `d$` — Normal delete-to-end-of-line alias; preserve the line | First required at hidden M6.04 `6G0D` (`curriculum-v2.json:4355`; source `gen_curriculum_v2.py:689-698`) | No prior guided `D` card. `delete-eol` legacy prose appears only on M6.05 (`LEGACY_CURRICULUM_DISPOSITION.md:21`), after the first hidden use. M6.Q03/Q04/Q09/Q10 are post-use. | M6.05 comparison and M6.08 check | M6.04 has two changed-art variants, but the first use itself is hidden and the review is not a preceding teaching stage | **Hard first-use gap.** Insert grammar + completion + guided D edit before M6.04. |
| `dd` / `Ndd` — Normal operator grammar with linewise motion; deletes whole rows | First appears hidden in M1.04 `3dd`; M7.08 uses `5dd` (`curriculum-v2.json:5674`) | No guided `dd` card before the first hidden use. `delete-line` legacy attachment at M7.08 is not prior teaching. M7.Q07/Q10 are post-use. | M7.08 module check | No changed-art review bank | **Inherited first-use gap.** Add a guided linewise-delete card and a count/operator/linewise completion item before any `dd` check. |
| `:t`/`:copy` — Ex grammar `:[range]t{address}<CR>` | First appears hidden M0.05 `:7,9t$`; guided only at M6.02 `:1,5t$` (`gen_curriculum_v2.py:682-688`) | No grammar/completion item before M0.05. M5.Q05 and M6.Q02 are interpretation questions after prior uses; the legacy `ex-copy` attachment is on M5.05, not an earlier lesson. | M5.05, M6.05, M7.01/.02, M8.08, M9.05/.08 | None of those source cards has review variants | **Hard first-use gap.** Teach address/range + `t` + destination + Enter before M0.05; M6.02 can be the guided project card only if the earlier path is changed. |
| `:m`/`:move` — Ex grammar `:[range]m{address}<CR>` | First appears hidden M6.06 `:1,5m$` (`curriculum-v2.json:4632`); M6.08 repeats it | No guided `:m` card before M6.06. `playback-order` is attached at M6.08 after first use (`LEGACY_CURRICULUM_DISPOSITION.md:56`). M6.Q06/Q07/Q08 are post-use. | M6.08 module check | M6.06 is a transfer with changed-art variants; M6.08 has no review bank | **Hard first-use gap.** Add a guided range-move card and completion item before M6.06. |
| `:s` — Ex grammar `:[range]s/pattern/replacement/flags<CR>`; range and `g` are semantic | Guided M0.02 `:4,6s/o/O/g`; M7.05 `%s`, M8.05 `:1,5s` | M0.02 now has explicit key vocabulary, including range and `g`, but the paired concept is after the guided edit. M0.03/M0.04 should be the completion/interpretation gate; current M5–M9 questions only retrieve later scope. | M7.05 and M8.05 hidden comparisons; M9 does not add a substitute | No M7.05 or M8.05 changed-art review bank | Content is present, ordering is still incomplete. The range/pattern/replacement/flag decomposition must be a required pre-M0.04 check, not merely brief text. |
| `.` — standalone Normal dot-repeat of the last change | First appears hidden in M0.08; M7.04 requires `5j.` (`gen_curriculum_v2.py:794-807`) | No guided dot card before M0.08 or M7.04. M7.Q03/Q04/Q06/Q10 explain repeat after use; the legacy `dot-repeat` payload is attached to M7.04. | M7.04 and M7.06 | Only M7.06 transfer has review variants | **Hard first-use gap.** Add a guided bounded edit + dot-repeat card before M7.04. |
| `q{reg}…q` and `@{reg}` — standalone macro record/replay | First appears as a hidden alternative in M7.05 (`gen_curriculum_v2.py:820-824`) | No grammar/completion item or guided macro performance before the comparison. The legacy `macro` payload is attached to M7.05 and cannot count as prior teaching. M7.Q05/Q09/Q10 cover macro reasoning after use. | M7.05 comparison only; M15/M17 are later modules | No M7.05 review bank | **Hard first-use gap.** Split macro into a guided card, completion check, and later comparison. |
| `:g{pattern}normal!{keys}<CR>` — Ex selection plus Normal command | First appears only as M7.05 hidden comparison alternative | No grammar/completion or guided card before use; Q09 explains its scope after use. `range-normal` legacy attachment is on the same card. | M7.05 only | No changed-art review | **Hard first-use gap.** It is a distinct Ex composition, not implied by `:s` or macros. |
| `o/O` — standalone open-line Insert-mode entry; line creation changes row count | First hidden in M1.04; required visibly as hidden M8.04 (`curriculum-v2.json:5952`) and as an M9.05 alternative | No guided open-line card before first use. Legacy `open-line`/`append`/`pad-frames` appears only on M8.04 (`LEGACY_CURRICULUM_DISPOSITION.md:33-34,59`). M8.Q04 is post-use. | M8.04 and M9.05 comparison | No M8.04/M9.05 review bank | **Hard first-use gap.** Teach `o` versus `O`, Insert-mode entry, `<Esc>`, and fixed-height consequences before M8.04. |
| `x` — standalone Normal delete-character; deletion shifts following cells | First required hidden M9.04 `...x...` (`curriculum-v2.json:6511`) | No guided `x` animation card or completion item. The `move-x` legacy attachment is on M9.04 and is not prior teaching. M9.Q03/Q10 are post-use. | M9.04 only (M9.05 alternative uses open-line instead) | No M9.04 review bank | **Hard first-use gap.** Add a guided fixed-width-versus-shifting deletion card before M9.04. |
| `i` — standalone Insert entry and literal text, ended by `<Esc>` | First required hidden M9.04 `i=<Esc>` | No guided `i` card or completion item. M8 legacy prose names `i`, but it is attached legacy material, not executable prior evidence. M9.Q03 is post-use. | M9.04 only | No review | **Hard first-use gap.** Teach `i` and why `x`+`i` can preserve/repair a fixed cell before M9.04. |

## Card-by-card executable ledger

The table below is the requested per-card evidence ledger. `post-Q` means that
the listed questions exist in the module but are not a precondition before the
card shown. `K:yes` means the rendered brief names the useful family in
`KEYS WORTH KEEPING`; `K:recipe` means the card exposes its recipe; `K:no`
means the runtime falls back to F1/undo/redo/save keys or otherwise omits the
family. `H:good` means the hint gives a scoped strategy tied to the animation;
`H:partial` means it falls back to “choose the smallest operation” or fails to
name the new grammar. `R:yes` is an actual changed-art bank, not a promise.

### M5 — Layered scene

Source recipes: `share/gen_curriculum_v2.py:567-663`; generated cards:
`share/curriculum-v2.json:3621,3693,3792,3862,3968,4113`.

| Card | Required family/intent | Prior teaching and paired concept | Later hidden retrieval | Review / brief / hint | Sequence verdict |
|---|---|---|---|---|---|
| M5.01 | `0`/`l` navigation + `r<Space>` standalone replace | `r` guided in M0.01, but no grammar/completion gate; post-Q M5.Q01/Q03/Q09/Q10 | M5.04, M5.06, M5.08 | `R:no`; `K:legacy seam prose`, not `r`; `H:good` fixed-width seam strategy | Guided performance exists; grammar-first and review gates do not. |
| M5.02 | `V6jy` Visual-line selection + `Gp` | First actual Visual-line use was hidden M3.06; post-Q M5.Q02/Q08 | M5.05 and M5.08 | `R:no`; `K:recipe`; `H:partial` (“smallest normal-mode operation” does not teach `V` grammar) | First-use-before-guided gap for `V`. |
| M5.04 | `C`/`c$` plus Insert redraw on two rows | Prior guided M4.01; post-Q M5.Q04 | M5.05 and M5.08 | `R:no`; `K:no` for `C`; `H:partial` generic | Retrieval is present, but no card-specific review or pre-use grammar check. |
| M5.05 | `:1,7t7<CR>` plus `C` | `:t` had already appeared hidden in M0.05; post-Q M5.Q05 | M5.08 | `R:no`; `K:yes` via legacy `ex-copy` (`:t`, `:m`, `yyp`); `H:good` range-copy scope | Ex grammar is still first-use-before-teaching; legacy keys cannot close it. |
| M5.06 | landmark navigation + `r<Space>` on transfer art | post-Q M5.Q06; the transfer itself is hidden | none after the transfer except module check | `R:yes` (two transfer variants); `K:no`; `H:good` changed-art seam scope | This is the only M5 executable with actual changed-art review evidence. |
| M5.08 | `f` + `rO` on the key-hidden module check | five selected Qs from M5.Q01–Q10 are asked first in runtime; they are not grammar/completion items | artifact is key-hidden after questions | `R:no`; `K:no` for `f/r`; `H:good` visible-landmark strategy | Concept-before-artifact is good locally, but no family review and no grammar gate. |

### M6 — Pyramid build

Source recipes: `share/gen_curriculum_v2.py:665-757`; generated cards:
`share/curriculum-v2.json:4211,4266,4355,4537,4632,4783`.

| Card | Required family/intent | Prior teaching and paired concept | Later hidden retrieval | Review / brief / hint | Sequence verdict |
|---|---|---|---|---|---|
| M6.01 | `r^` standalone replace | Prior M0.01 guided; post-Q M6.Q01 | M6.04/.05/.08 | `R:no`; `K:recipe`; `H:good` | Familiar cell edit, but no explicit standalone grammar/completion path. |
| M6.02 | `:1,5t$<CR>` Ex copy | First `:t` was hidden M0.05; M6.Q02 is post-use | M6.05 and M6.08 | `R:no`; `K:recipe`; `H:good` range-scope strategy | This is the first visible `:t` recipe, but it arrives too late to make earlier use valid. |
| M6.04 | `D` (`d$`) content clear while retaining row | **No prior guided D.** Post-Q M6.Q03/Q04/Q09/Q10; attached legacy `join` teaches J, not D | M6.05 and M6.08 | `R:yes` (two variants); `K:no` for D; `H:partial` generic | **Hard gap: hidden first use of D.** |
| M6.05 | `:6,10t$<CR>` plus `D` | D was first hidden in M6.04; post-Q M6.Q05/Q10 | M6.08 | `R:no`; `K:yes` for D only because `delete-eol` legacy payload is attached here; `H:partial` for D | The brief teaches D after the first required use. |
| M6.06 | `:1,5m$<CR>` Ex move | **No prior guided :m.** Post-Q M6.Q06/Q07/Q08 | M6.08 | `R:yes` (transfer variants); `K:no`; `H:good` whole-range move | **Hard gap: hidden first use of :m.** |
| M6.08 | two `:m` range moves, key-hidden module artifact | five Qs from M6.Q01–Q10 precede the artifact; no completion item | terminal module check | `R:no`; `K:yes` only through legacy playback-order attachment; `H:good` range move | Mastery can be claimed without a changed-art :m review. |

### M7 — Timed build

Source recipes: `share/gen_curriculum_v2.py:760-857`; generated cards:
`share/curriculum-v2.json:4889,5010,5146,5283,5484,5674`.

| Card | Required family/intent | Prior teaching and paired concept | Later hidden retrieval | Review / brief / hint | Sequence verdict |
|---|---|---|---|---|---|
| M7.01 | `:1,5t5<CR>` deliberate hold copy | Visible `:t` at M6.02, but no grammar/completion gate; post-Q M7.Q01 | M7.02/.05/.08 | `R:no`; `K:yes` from legacy hold-frame; `H:good` declared timing/range strategy | Animation intent is clear; Ex grammar sequence is not. |
| M7.02 | `:16,20t$<CR>` reviewable duplicate | Same `:t` gap; post-Q M7.Q02 | M7.04/.05/.08 | `R:no`; `K:no`; `H:good` | No changed-art review despite “reviewable” meaning only an in-strip duplicate. |
| M7.04 | `f`/`r` bounded material edit + `j.` | `f/r` guided earlier; **dot first appeared hidden M0.08**; post-Q M7.Q03/Q04 | M7.06 and M7.08 | `R:no`; `K:yes` via attached dot-repeat; `H:good` for dot but no grammar decomposition | **Hard dot first-use gap.** |
| M7.05 | `:%s...g`; macro `q…q/@q`; `:g…normal!` alternatives | `:s` guided M0.02; macro and Ex composition first appear as hidden alternatives here; post-Q M7.Q05/Q09/Q10 | comparison paths only | `R:no`; `K:yes` via same-card legacy attachments, not prior teaching; `H:good` for substitution, `H:partial` for macro/global | **Hard first-use gaps for macro and `:global`/`:normal`; no review.** |
| M7.06 | `f`/`r` + dot on changed transfer art | post-Q M7.Q06/Q10; transfer hides exact path | none after transfer except M7.08 | `R:yes` (two variants); `K:yes` for f, legacy; `H:good` | Review exists for this transfer, not for the source families generally. |
| M7.08 | `5dd` linewise delete of one five-row frame | `dd` first hidden in M1.04; post-Q selected from M7 bank | terminal module check | `R:no`; `K:yes` only via attached delete-line; `H:partial` generic | **Inherited dd gap; mastery has no changed-art delete review.** |

### M8 — Walk study

Source recipes: `share/gen_curriculum_v2.py:859-933`; generated cards:
`share/curriculum-v2.json:5815,5870,5952,6066,6147,6280`.

| Card | Required family/intent | Prior teaching and paired concept | Later hidden retrieval | Review / brief / hint | Sequence verdict |
|---|---|---|---|---|---|
| M8.01 | `r_` standalone contact-cell replacement | Prior M0.01 guided; post-Q M8.Q01 | M8.02/.04/.06/.08 | `R:no`; `K:recipe`; `H:good` | Familiar operation; no family-level grammar/review evidence. |
| M8.02 | `5yy/p` plus `C` on selected rows | Prior linewise copy and C guided; post-Q M8.Q02/Q03 | M8.04/.08 | `R:no`; `K:recipe`; `H:good` frame-copy scope | Good guided animation practice, but no changed-art review. |
| M8.04 | `o` plus literal row authoring; Insert/Escape | **No prior guided `o`.** Post-Q M8.Q04; attached legacy open-line/append/pad is same card | M8.05/.08 | `R:no`; `K:yes` only because same-card legacy keys name o/O/i/A; `H:partial` (names open-line but not grammar or row-height consequences) | **Hard first-use gap.** |
| M8.05 | `:1,5s@...@<CR>` bounded substitute | `:s` guided M0.02; post-Q M8.Q05/Q09 | M8.08 | `R:no`; `K:no`; `H:good` scope | Ex range syntax is used correctly but not revisited on changed art. |
| M8.06 | `r_` on offset transfer art | post-Q M8.Q06/Q10; hidden transfer | none after transfer except module check | `R:yes` (two variants); `K:no`; `H:good` derive visible column | Review exists only for the transfer source. |
| M8.08 | `:6,10t$` plus row-local C, key-hidden check | five Qs from M8 bank precede artifact; no completion item | terminal module check | `R:no`; `K:no`; `H:good` | Mastery can pass without changed-art copy/C review. |

### M9 — Original bounce capstone

Source recipes: `share/gen_curriculum_v2.py:935-1010`; generated cards:
`share/curriculum-v2.json:6376,6427,6511,6588,6680,6801`.

| Card | Required family/intent | Prior teaching and paired concept | Later hidden retrieval | Review / brief / hint | Sequence verdict |
|---|---|---|---|---|---|
| M9.01 | `f` + `r` on the planned marker | Prior M0.01 guided; post-Q M9.Q01 | M9.04/.06/.08 | `R:no`; `K:recipe`; `H:good` landmark strategy | Familiar family, no changed-art source review. |
| M9.02 | `3yy/p` plus C redraw | Prior linewise copy/C; post-Q M9.Q02 | M9.05/.08 | `R:no`; `K:recipe`; `H:good` | Guided frame registration is good; grammar/completion/review ledger is absent. |
| M9.04 | `fO`, standalone `x`, standalone `i=<Esc>` | **x and i first required here, hidden.** Post-Q M9.Q03; `move-x` legacy payload is same card | M9.05/.08 | `R:no`; `K:yes` for x only via same-card legacy; `K:no` for i; `H:partial` generic | **Two hard first-use gaps.** |
| M9.05 | `:1,3t3<CR>` + C; alternative `3o`/row authoring | `:t` guided M6.02 and C guided M4.01; `o` remains unrehearsed before this alternative; post-Q M9.Q04/Q05/Q09 | M9.08 | `R:no`; `K:yes` only for legacy tween yyp, not the actual Ex/C/o grammar; `H:good` for range copy | Comparison exposes multiple methods before all families have guided grammar. |
| M9.06 | `f` + `r` changed transfer | post-Q M9.Q06; hidden transfer | none after transfer except check | `R:yes` (two variants); `K:no`; `H:good` | Transfer review is present, but not a review of M9.01 or M9.04 families. |
| M9.08 | `:1,3t$` + `f/rO`, key-hidden capstone | five Qs from M9 bank precede artifact; no completion item | terminal module check | `R:no`; `K:no`; `H:good` | Capstone mastery has no changed-art review for Ex copy or marker replacement. |

## Question and review coverage by module

The question pairing is real but late and incomplete as a grammar curriculum.
The generated concept cards select these question IDs
(`share/gen_curriculum_v2.py:3443-3477`; generated card starts are cited below):

| Module | Concept card question IDs | What they cover | Missing sequence element |
|---|---|---|---|
| M5 | M5.03: Q03,Q10,Q02,Q06,Q09 (`curriculum-v2.json:3767`); M5.07: Q03,Q07,Q10,Q08,Q09 (`:4088`); M5.08: Q01–Q10 (`:4113`) | Seam ownership, Visual-line scope, `r`, addressed copy, fixed columns | No grammar decomposition; no command-completion item; Qs follow M5.01/.02 first use. |
| M6 | M6.03: Q02,Q03,Q01,Q06,Q09 (`:4330`); M6.07: Q03,Q07,Q10,Q08,Q09 (`:4758`); M6.08: Q01–Q10 (`:4783`) | Ex copy/move intent, D row preservation, equal frame bounds | `D` and `:m` are first used before their questions; no completion item. |
| M7 | M7.03: Q03,Q07,Q02,Q06,Q09 (`:5121`); M7.07: Q03,Q07,Q10,Q08,Q09 (`:5649`); M7.08: Q01–Q10 (`:5674`) | Holds, dot, substitution, macro/global scope, delete | Macro and `:global` are first hidden alternatives; no completion item or review. |
| M8 | M8.03: Q01,Q03,Q02,Q06,Q09 (`:5927`); M8.07: Q03,Q07,Q10,Q08,Q09 (`:6255`); M8.08: Q01–Q10 (`:6280`) | Contact registration, full-pose copy, C, bounded substitute, open-line intent | `o` first hidden; no grammar decomposition or changed-art review. |
| M9 | M9.03: Q02,Q05,Q01,Q06,Q09 (`:6486`); M9.07: Q03,Q07,Q10,Q08,Q09 (`:6776`); M9.08: Q01–Q10 (`:6801`) | Whole-frame copy, `:t`, marker/range decisions, bounce bounds | `x`/`i` first hidden; no completion item or changed-art source review. |

Every question has paired fields and four choices in the generated bank
(`share/curriculum-v2.json:15505-17154`), and the generator constructs the
paired prompt/feedback at `share/gen_curriculum_v2.py:3156-3219`. That passes
the current structural tests (`share/test_v2.py:104-128`). It should be
retained, then supplemented with a distinct completion type such as:

```text
You want to replace every - on line 8. Complete the motion:
  8s/-/=?
Choices: g / % / <CR> / p
```

The completion item must be paired with the same ASCII intention and must
precede the first card that requires the family.

## Runtime brief and hint findings

1. `show_recipe` is generated solely from ordinal (`share/gen_curriculum_v2.py:3425-3429`). Thus `.04`, `.05`, `.06`, and `.08` are hidden by card shape, not by a family-level prerequisite check.
2. `KEYS WORTH KEEPING` uses `key_vocabulary`, then legacy keys, then a fallback (`share/v2_runtime.py:636-640,667-674,720-730`). M5–M9 hidden cards without an attached legacy payload therefore show only F1/undo/redo/save keys, even when their new family is the thing being retrieved. Same-card legacy attachments can make a key visible, but do not establish prior teaching.
3. `action_hint()` names scope and sometimes a strategy (`share/gen_curriculum_v2.py:3236-3301`), but it has no grammar decomposition. The generic branch “choose the smallest normal-mode operation” appears on M5.02/M5.04/M6.04/M7.08/M9.04 and does not tell the learner whether the operation is an operator sentence, standalone command, or Ex statement.
4. The brief's `LEGACY VIM CONCEPT` section renders full legacy paradigms (`share/v2_runtime.py:675-678,739-741`). This is useful reference material, but the curriculum has no event or prerequisite proving that the learner parsed it or completed a related question before the card.
5. The runtime does pair five concept answers before a module-check artifact (`share/v2_runtime.py:1545-1602`), and a spaced review pairs one conceptual answer with one changed-art edit (`:1885-1929`). However, a module check can pass without the relevant family having its own prior guided/completion/review path, and most M5–M9 sources have no review bank at all.

## Proposed insertion points (no implementation in this audit)

These are the smallest curriculum insertions that would close the ordering
gaps while preserving the M5–M9 animation spine.

| Before | Insert | Then allow |
|---|---|---|
| Before M0.04 / before any further `:s` retrieval | Grammar card for `:[range]s/pattern/replacement/flags<CR>`; parse `:8s/-/=/g` and `:4,6s/o/O/g`; interpretation and completion questions; guided M0 edit | M0.04 and later M5/M7/M8 substitution retrieval |
| Before M5.02 | Visual-line grammar (`V` selects whole lines; `y` acts on selection; `p/P` puts below/above) plus completion item; guided seven-row frame copy | M5.02 as key-hidden Visual-line retrieval or keep it guided and move retrieval to M5.04 |
| Before M6.04 | `D = d$` grammar card, animation-preserving row-clear interpretation, completion item, guided copied-apex edit | M6.04 hidden D retrieval and M6.05 comparison |
| Before M6.06 | Ex move grammar `:[range]m{destination}<CR>`, range/destination prediction, completion item, guided five-row reorder | M6.06 hidden transfer and M6.08 check |
| Before M7.04 | Dot grammar (`.` repeats the last change, not the last motion), paired prediction/completion, guided bounded band edit + dot | M7.04/.06 retrieval |
| Before M7.05 | Macro grammar `q{reg}…q` / `@{reg}` and Ex `:g{pattern}normal!{keys}<CR>`; one guided macro and one guided scoped-global edit, each with completion | M7.05 comparison and later M15/M17 reuse |
| Before M8.04 | `o`/`O` and Insert-mode grammar, `<Esc>`, row-height invariant; guided five-row pose insertion | M8.04 hidden open-line retrieval and M9.05 alternative |
| Before M9.04 | `x` standalone delete-character and `i` Insert entry; fixed-width versus shifting-column interpretation/completion; guided squash-centre repair | M9.04 hidden x+i retrieval |

For every inserted family, add a card-level `grammar_family` and
`grammar_parts` contract, a `concept_question_ids` pair (interpretation and
completion), a `guided_source_card_id`, a `retrieval_source_card_id`, and a
minimum two-variant changed-art review bank. Do not use `legacy_lessons` as any
of these fields.

## Acceptance tests to add

1. **Family extraction and ordering.** Extract command families from every
   executable `expected` path and comparison method in M0–M9. For each family,
   assert `grammar explanation < interpretation question < completion question
   < guided card < key-hidden retrieval < changed-art review`. Exempt only
   navigation/submit keys explicitly classified as infrastructure.
2. **Grammar-shape checks.** Assert that Normal operator cards record the
   count/operator/motion or text-object parts; standalone cards record their
   command semantics separately; Ex cards record address/range, command,
   pattern, replacement, flags, and `<CR>` as separate fields. A string inside
   an answer key or legacy payload must not satisfy the assertion.
3. **Question pairing.** Require at least one card-paired item and the full
   teaching sequence per new family, using open semantic-key, decode,
   missing-token completion, prediction, why, or diagnostic multiple choice as
   the authored need dictates. Every form must pair the Neovim decision with
   the ASCII-art invariant. When multiple choice is selected, all four wrong
   answers retain mistake-specific feedback. Existing paired-bank assertions
   at `share/test_v2.py:104-128` remain necessary but are not sufficient.
4. **Guided-before-hidden runtime path.** Replay each inserted guided card in
   real Neovim, then the relevant M5–M9 hidden card, under both `-u NONE` and
   the normal configuration. Assert the learner cannot reach the hidden card
   before the guided and both conceptual checks are passed.
5. **Brief evidence.** Render every M5–M9 executable brief and assert that
   `KEYS WORTH KEEPING` contains the family grammar or an explicit pointer to
   the preceding grammar card. The fallback F1-only list must fail this test
   when the card requires a new family.
6. **Review coverage.** For every family that can contribute to M5–M9 mastery,
   assert at least two distinct changed-art variants, exact artifact grading,
   captured method evidence where required, and a scheduled review event before
   the family is marked mastered. A transfer card alone must not satisfy review
   coverage for every source card using the same family.
7. **Card ledger.** Generate a machine-readable audit ledger for all 30
   executable M5–M9 cards with the fields in this report: required families,
   grammar source, interpretation/completion IDs, guided source, hidden
   retrieval, review source, key vocabulary, and hint strategy. Fail generation
   if any field is absent or points only to a legacy attachment.
8. **Real animation invariants.** Keep the current real-Neovim target checks,
   then assert the family-specific invariant: fixed row width for `r`, complete
   frame height for `yy/p`, `:t`, and `:m`, retained rows for `D`/`dd`, fixed
   columns for `C`/`o`/`i`/`x`, and bounded range for `:s`/`:g`.
9. **Mastery falsifier.** Construct a fresh event log in which a learner passes
   all five Mx.08 conceptual checks and the artifact with an alternate method,
   but skips the family completion/guided/review evidence. The module must not
   report that family or the module as grammar-mastered.
10. **Regression.** Keep `generator.build() == curriculum-v2.json`, the current
    152-card/190-question checks, all 30 M5–M9 real-Neovim paths, and the
    existing legacy 46-drill regression green after the new gates are added.

## Bottom line

M5–M9 already demonstrate meaningful ASCII-animation decisions, exact targets,
paired conceptual questions, hidden retrieval surfaces, and six changed-art
transfer sources. They do not yet prove grammar-first command mastery. The
highest-risk violations are hidden first uses of `D`, `:t`, `:m`, dot, macro,
`:global`/`:normal`, `o`, `x`, and `i`; the broadest systemic gap is that
changed-art review is attached to selected cards rather than to every family
that can feed a mastery claim. The audit should be committed as this report
before any curriculum/runtime insertion begins.
