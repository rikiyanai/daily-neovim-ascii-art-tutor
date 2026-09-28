# Grammar-first sequencing audit: M0–M4

Status: audit-only report. This report was written against generated curriculum
revision `2026-09-28.22` in the preserved dirty worktree. It does not modify
the curriculum, generator, runtime, tests, launcher, or failure log. It is the
M0–M4 partition required by `share/audits/GRAMMAR_FIRST_REQUIREMENT.md`.

## Verdict

The current M0–M4 paths are executable, but they are not yet a grammar-first
curriculum. There are 30 executable cards (six per module). Only the five
module-check cards own question IDs; the other 25 executable cards have no
paired conceptual question attached to their performance attempt. The current
tests prove that recipes reach their targets under clean and real Neovim, not
that the learner received the required grammar → interpretation → completion
→ guided performance → hidden retrieval → changed-art review sequence.

The most urgent concrete defect remains M0.04: `yy/p` and substitution are
shown on M0.02, but no current card decomposes `:8s/-/=/g` into address,
command, pattern, replacement, flag, and Enter before M0.04 hides the exact
path. Ex copy `:t` is first hidden on M0.05 without any current guided card.
`dd`, `o`, Visual block, named-register Visual-line copying, `ci(`, and the
digraph path likewise appear first in hidden or check paths without a prior
current guided performance card.

## Audit method and evidence map

The requirement says that a command is taught only by a current grammar
explanation plus a guided edit. A legacy attachment, answer key, recipe token,
distractor, or source citation is evidence of provenance, not teaching. The
audit therefore records a stage as absent unless the current v2 learner is
required to see and perform it.

Abbreviations used below:

- `G` = explicit current grammar decomposition; `I` = interpretation question;
  `C` = completion/parse question. `~` means a related selection question
  exists, but it is not an actual syntax decomposition or fill-in completion.
- `guided` = an earlier current `guided_edit` with its recipe visible and a
  real artifact edit; `H` = exact keys hidden on an independent, comparison,
  transfer, or module-check card.
- `R` = a changed-art review link. `transfer×2` means two changed transfer
  variants exist, but they are not proof of a later spaced review before
  mastery. `after pass` is important: the runtime schedules review after the
  source card passes, not before the module mastery claim.
- `K` = card-owned `key_vocabulary` rendered under `KEYS WORTH KEEPING`.
  `recipe` means the runtime prints the visible recipe on a guided card;
  `legacy` means only an attached legacy lesson contributes vocabulary;
  `fallback` means the generic F1/undo/redo/save block. Neither `legacy` nor
  `fallback` is a grammar stage.
- `Δ+` = the hint adds useful strategy/scope information beyond `DO THIS`;
  `Δ~` = it adds scope but also misidentifies a tool; `Δ−` = it is misleading
  for the required path.
- `P` = a question is paired with the same performance attempt. The current
  ordinary edit cards have no `paired_question_ids`; only module checks run
  five questions before their artifact edit.

Primary source locations:

| Evidence | Current lines |
|---|---|
| Requirement ledger, what does not count, required audit row | `share/audits/GRAMMAR_FIRST_REQUIREMENT.md:10-35,69-90` |
| Legacy grammar prose (not creditable as v2 teaching) | `share/curriculum.json:26-48` |
| v2 step schema: recipe, method evidence, review variants, optional vocabulary; no grammar contract | `share/gen_curriculum_v2.py:70-87` |
| M0–M4 authored starts, targets, recipes, and review/transfer data | `share/gen_curriculum_v2.py:109-565` |
| Question prompts and answer pairs for M0–M4 | `share/gen_curriculum_v2.py:2622-2710,2853-2913` |
| Question generation: paired art/Vim choices, but no syntax-completion stage | `share/gen_curriculum_v2.py:3115-3220` |
| Hint generation: strategy/scope/failure text, no grammar teaching | `share/gen_curriculum_v2.py:3236-3301` |
| Card ordering: only ordinals 1–2 show recipes; 3/7 are concept cards; 4/5/6/8 hide keys; reviews only when variants/transfer exist | `share/gen_curriculum_v2.py:3398-3492` |
| Generator validation: four-choice pairing and review-variant shape, but no first-use sequencing validator | `share/gen_curriculum_v2.py:3594-3785` |
| Rendered brief and `KEYS WORTH KEEPING` merge/fallback | `share/v2_runtime.py:604-754` |
| Concept card: one question, then completion; ordinary edits do not call this | `share/v2_runtime.py:1465-1511,1605-1618` |
| Module check: five questions, then artifact; mastery evidence | `share/v2_runtime.py:1545-1602,1412-1462` |
| Spaced review: one concept item plus changed-art edit, scheduled after pass | `share/v2_runtime.py:1417-1419,1885-1933` |
| Existing tests: M0.02/M0.04 special case, headings, method/review shape, not grammar order | `share/test_v2.py:94-150,175-193,788-880,905-965` |
| Existing failure-log first-use inventory and operator correction | `FAILURE_LOG.md:1709-1710,1830-1855` |

Generated-card line anchors used in the tables below are in
`share/curriculum-v2.json`: M0 cards begin at lines `594,725,848,923,1008,1129`;
M1 at `1223,1290,1377,1431,1493,1614`; M2 at
`1685,1769,1859,1917,1994,2121`; M3 at
`2208,2285,2381,2493,2574,2783`; and M4 at
`2891,2966,3065,3195,3279,3432`. The corresponding ten-question banks
are M0 `13855-14152`, M1 `14185-14482`, M2 `14515-14812`, M3
`14845-15142`, and M4 `15175-15472`.

## Card-by-card gap register

The rows cover every executable card in M0–M4. The `Prior stages` column is
deliberately strict: a question in a later concept card is not moved backward
to make a hidden card appear taught.

### M0 — Spark loop

| Card (generated JSON line; kind) | Required families and grammar class | Prior stages (`G/I/C`; guided) | Retrieval and review | Keys / hint | Pairing, invariant, and gap |
|---|---|---|---|---|---|
| `M0.01` (`594`; guided_edit) | `j`, `0`, `f{char}` standalone motions; `r{char}` standalone Normal replace | `G—; I—; C—`; guided own card, first use | Later hidden use in `M0.06`/`.08`; `R=M0.01` two changed variants, after pass | `K=recipe+legacy`; `Δ+` visible landmark, frame scope, ray-drift failure | `P=none`; core changes while six rays remain registered. Gap: first command family is performed before any paired conceptual stage (`GF-01/04/05`). |
| `M0.02` (`725`; guided_edit) | `gg`; counted linewise `3yy` + standalone linewise `p/P`; Ex substitute `:[range]s/pat/repl/g<CR>` | `G—; I—; C—`; guided own card, first current `yy/p` and `:s` performance. The two K lines are shorthand, not a decomposition of address/command/pattern/replacement/flag/Enter | Hidden `M0.04` (`yy/p`, `:s`); `.06` (`:s`); no later card-specific R | `K=yes` (`{count}yy…`, `:{start},{end}s…`); `Δ+` frame-sized copy and scoped substitution, but no grammar | `P=none`; copy a complete 3-row frame, brighten only copied core. Gap: grammar and paired interpretation/completion must precede the guided card, not follow it (`GF-01/03/04/05/06`). |
| `M0.04` (`848`; independent_edit) | `G`; `3yy/p`; Ex one-line substitute `:8s/-/=/g<CR>` | `G=raw K on M0.02, not decomposition; I~M0.Q02/Q06; C—`; guided `yy/p/:s` M0.02, no guided `G` | `H=self`; no R | `K=yes`; `Δ+` says counted copy + line/range substitution and frame scope | `P=none`; bright copy widens only new horizontal rays. Gap: first hidden `G`; `:8s/-/=/g` still lacks parse/completion, exactly the operator failure (`GF-01/03/04/05/07`). |
| `M0.05` (`923`; compare_methods) | Ex addressed copy `:[range]t{address}<CR>`; linewise yank/put alternative | `G—; I—; C—`; no prior guided Ex copy | `H=self`; no R | `K=fallback` (does not name `:t`); `Δ+` addressed range/cursor independence | `P=none`; duplicate complete flare for an intentional hold. Gap: first hidden `:t` with no current guided introduction or parse question (`GF-03/05/06`). |
| `M0.06` (`1008`; transfer) | `j/f/r` standalone/local edit; current-row Ex substitute `:s/-/=/g<CR>` | `G` for `j/f/r/:s` exists on M0.01/M0.02; `I~M0.Q06`; `C—`; prior guided yes, but no grammar | `H=self`; `R=transfer×2`, linked and due after pass | `K=fallback`; `Δ+` row-scoped substitution and landmark strategy | `P=none`; unfamiliar comet preserves contour while core/tail brighten. Gap: no paired question on this attempt and no explicit Ex completion (`GF-03/04/05/06`). |
| `M0.08` (`1129`; module_check) | Ex `:1,3t$<CR>`; `G`, `f`, `r`; standalone dot repeat `.` | `G— for :t/G/.; I~M0.Q07/Q08 in preceding `.07`; C—`; prior guided only for `f/r/yy`, not `:t`, `G`, or `.` | `H=self`; no R before/after check | `K=fallback` (does not name `:t` or `.`); `Δ+` addressed copy, but says nothing about dot repeat | `P=Q01–Q10 bank; runtime selects five, then artifact`; dim→bright→flare hold→settle. Gap: mastery may claim `:t/G/.` without guided stages or spaced review (`GF-01/03/04/05/06`). |

### M1 — Contour run

| Card (generated JSON line; kind) | Required families and grammar class | Prior stages (`G/I/C`; guided) | Retrieval and review | Keys / hint | Pairing, invariant, and gap |
|---|---|---|---|---|---|
| `M1.01` (`1223`; guided_edit) | `/pattern<CR>` search; `r{char}` standalone replace | `G` for `r` M0.01; `G/I/C—` for search; guided own search card | No hidden search retrieval in M0–M4; no R | `K=recipe+legacy`; `Δ+` homologous-anchor search and scope | `P=none`; change joint only, endpoint fixed. Gap: first search performance has no prior interpretation/completion and no later hidden search retrieval (`GF-01/04/05`). |
| `M1.02` (`1290`; guided_edit) | counted linewise `3yy/p` | `G` M0.02; `I/C—` before this card; guided own repetition | Hidden later in M1.04/M1.08 and other modules; no R | `K=recipe`; `Δ+` complete multi-row copy | `P=none`; complete anchored contour copied. Gap: no paired question before this repetition (`GF-04/05`). |
| `M1.04` (`1377`; independent_edit) | `G`; linewise delete `3dd`; standalone open-line `o/O` plus Insert text | `G—` for `G/dd/o`; `I/C—` (M1.03 omits Q04/Q08); no prior guided `dd` or `o` | `H=self`; no R | `K=fallback`; `Δ+` open-line strategy, but no `o` grammar or registration repair | `P=none`; hand-author descending frame while retaining anchor. Gap: `dd` and `o` first appear hidden, before all required stages (`GF-01/02/04/05/06`). |
| `M1.05` (`1431`; compare_methods) | Ex file-range substitute `:%s/:/;/g<CR>`; local `r` plus dot repeat `.` | `G` for `:s` M0.02 and `r` M0.01; `I~M1.Q09` before card; `C—`; no guided dot | `H=self`; no R | `K=fallback` (does not name `:s` or `.`); `Δ+` bounded substitute vs local repeat | `P=none`; same material correction in both frames. Gap: no explicit Ex parse or guided dot stage (`GF-01/03/04/05/06`). |
| `M1.06` (`1493`; transfer) | absolute `G`, `0`, `f{char}`, `r{char}` | `G` for `0/f/r` M0.01; no guided `G`; `I~M1.Q06`; `C—` | `H=self`; `R=transfer×2`, after pass | `K=fallback`; `Δ+` visible landmark over repeated motions | `P=none`; mirrored transfer retains material and endpoint. Gap: `G` first hidden on M0.04/M1.06; no paired performance question (`GF-01/04/05`). |
| `M1.08` (`1614`; module_check) | Ex `:1,3t$<CR>`; `G/0/f/r` | `G—` for `:t/G`; `I~M1.Q10` only addresses `:s`, not `:t`; `C—`; guided only for `0/f/r` | `H=self`; no R | `K=fallback`; `Δ+` addressed copy + fixed-width replacement | `P=Q01–Q10 bank; five selected before artifact`; return contour and softened joint. Gap: check can claim `:t` without guided stage and no changed-art review (`GF-03/04/05/06`). |

### M2 — Face focus

| Card (generated JSON line; kind) | Required families and grammar class | Prior stages (`G/I/C`; guided) | Retrieval and review | Keys / hint | Pairing, invariant, and gap |
|---|---|---|---|---|---|
| `M2.01` (`1685`; guided_edit) | `/pattern<CR>` search; operator + text object `daw` (`[operator] [text object]`) | `G—; I—; C—`; guided own first `daw` performance | No later hidden `daw` in M0–M4; no R | `K=recipe+legacy`; `Δ+` semantic text-object scope and search | `P=none`; delete annotation without consuming eye/mouth/contour. Gap: `daw` has no grammar explanation or paired question before its guided use (`GF-01/04/05`). |
| `M2.02` (`1769`; guided_edit) | counted linewise `4yy/p` | `G` M0.02; `I/C—`; guided own repetition | Hidden M2.04/M2.08; no R | `K=recipe`; `Δ+` complete face copy | `P=none`; all four rows remain registered. Gap: no paired question before performance (`GF-04/05`). |
| `M2.04` (`1859`; independent_edit) | `G`, `f{char}`, `r{char}` | `G` for `f/r` M0.01; no guided `G`; `I~M2.Q04`; `C—` | `H=self`; no R | `K=fallback`; `Δ+` landmark strategy | `P=none`; only copied eye changes. Gap: absolute `G` first hidden; no attempt-level concept pair (`GF-01/04/05/06`). |
| `M2.05` (`1917`; compare_methods) | Ex substitute `:%s/[.o]/O/g<CR>`; local `r` alternative | `G` for `:s/r` M0.01/.02; `I~M2.Q09` scope question, but no Q05 pattern completion before card; `C—` | `H=self`; no R | `K=fallback` (does not name character class, range, or `g`); `Δ+` scope vs local strategy | `P=none`; normalize only two eye spellings across two faces. Gap: pattern/range/`g` grammar and paired completion missing (`GF-03/04/05/06`). |
| `M2.06` (`1994`; transfer) | `j/f/r` local replacement | `G` M0.01; `I~M2.Q06`; `C—` | `H=self`; `R=transfer×2`, after pass | `K=fallback`; `Δ+` landmark on changed face | `P=none`; eye remains focus despite changed mouth/contour. Gap: no paired question attached; review is transfer-only (`GF-04/05`). |
| `M2.08` (`2121`; module_check) | Ex `:1,4t$<CR>`; `G/f/r` | `G—` for `:t/G`; `I/C—` for `:t`; guided only for `f/r/yy` | `H=self`; no R | `K=fallback`; `Δ+` addressed copy | `P=Q01–Q10 bank; five selected before artifact`; copy face and blink only. Gap: check/mastery path relies on untaught `:t/G`, no changed-art review (`GF-03/04/05/06`). |

### M3 — Pose copy

| Card (generated JSON line; kind) | Required families and grammar class | Prior stages (`G/I/C`; guided) | Retrieval and review | Keys / hint | Pairing, invariant, and gap |
|---|---|---|---|---|---|
| `M3.01` (`2208`; guided_edit) | `G`, `0`, `f(`, `%`, `h`, `r`; `%` is matching-delimiter motion | `G` for `0/f/r` M0.01; `G/I/C—` for `%/h`; guided own `%` performance | No later hidden `%` retrieval in M0–M4; no R | `K=recipe+legacy`; `Δ+` single-cell scope, but no `%` grammar | `P=none`; eye changes while six-row body stays fixed. Gap: several motion families first occur in a guided recipe without preceding paired interpretation/completion (`GF-01/04/05`). |
| `M3.02` (`2285`; guided_edit) | counted linewise `6yy/p` | `G` M0.02; `I/C—`; guided own repetition | Hidden M3.04/.05/.06; no R | `K=recipe`; `Δ+` complete pose copy | `P=none`; six-row pose copied intact. Gap: no paired question before card (`GF-04/05`). |
| `M3.04` (`2381`; independent_edit) | operator + text object `ci(`; `G` | `G—` for `ci(`; `I~M3.Q04` before card asks why `ci(` fits; `C~` choice, not parse; no guided `ci(` | `H=self`; no R | `K=legacy only` (`ci(`/`ca(` appears in attached lesson, not current grammar); `Δ+` text-object scope | `P=none`; eye changes inside delimiters, body stable. Gap: hidden first use despite question mention; no current guided performance or review (`GF-01/04/05/06`). |
| `M3.05` (`2493`; compare_methods) | Ex addressed copy `:1,6t$<CR>`; linewise `6yy/p` alternative | `G—` for `:t`; `I~M3.Q05` before card; `C—`; guided only `yy/p` | `H=self`; no R | `K=fallback`; `Δ+` cursor-independent range strategy | `P=none`; whole six-row pose duplicated. Gap: Ex copy is still hidden-first; concept question does not precede a guided edit (`GF-03/04/05/06`). |
| `M3.06` (`2574`; transfer) | Visual-line `V`, named register `"a`/`"ap`, `G/f/r` | `G—` for Visual-line/register; `I~M3.Q06`; `C—`; no guided register/Visual-line performance | `H=self`; `R=transfer×2`, after pass | `K=legacy only` (`V`, registers shown only through attachment); `Δ~` also claims a paragraph object because `ap` is heuristically detected, although path is Visual-line + register | `P=none`; unfamiliar six-row pose copied before one eye edit. Gap: Visual/register grammar, performance, and accurate hint missing (`GF-01/04/05/06/07`). |
| `M3.08` (`2783`; module_check) | `G/f/r`; digraph `<C-k>.M` for middle dot | `G—` for digraph; `I~M3.Q09` before card; `C—`; no guided digraph | `H=self`; no R | `K=legacy marks only`; `Δ+` digraph tool, but not a prior guided stage | `P=Q01–Q10 bank; five selected before artifact`; final pose gets middle-dot accent. Gap: check can claim digraph without guided practice or changed-art review (`GF-01/04/05/06`). |

### M4 — Rotation tween

| Card (generated JSON line; kind) | Required families and grammar class | Prior stages (`G/I/C`; guided) | Retrieval and review | Keys / hint | Pairing, invariant, and gap |
|---|---|---|---|---|---|
| `M4.01` (`2891`; guided_edit) | `G/0`; `C` (`c$` shorthand: operator + end-of-line motion); standalone `r`; Insert text | `G` for `r` M0.01; `G—` for `G/C`; `I/C—`; guided own `C` performance | Hidden M4.04/.05/.06; no R | `K=recipe+legacy`; `Δ~` gives useful fixed-width scope but falsely adds search because `/` is literal art text in the recipe | `P=none`; upper tip and lower stroke turn around fixed pivot. Gap: `C` grammar and absolute `G` lack prior paired stages (`GF-01/04/05/07`). |
| `M4.02` (`2966`; guided_edit) | `G`; counted linewise `3yy/p` | `G` for `yy/p` M0.02; `G—` for `G`; `I/C—`; guided own copy | Hidden M4.04/.05; no R | `K=recipe`; `Δ+` frame-sized copy | `P=none`; complete forward extreme copied. Gap: no paired concept before guided use and no `G` teaching (`GF-01/04/05`). |
| `M4.04` (`3065`; independent_edit) | Ex `:1,3t3<CR>`; `G/C`; Visual block `<C-v>jr|` | `G` for `C` M4.01, but `G—` for `:t` and `<C-v>`; `I~M4.Q01/Q03` for C; `C—` for block/range parse; no guided Ex copy or block edit | `H=self`; no R | `K=legacy only` (block keys are attached legacy prose); `Δ+` names block column, Ex copy, fixed-width replace, but no grammar | `P=none`; vertical midpoint replaces exactly two aligned prop cells while pivot stays fixed. Gap: first hidden Ex copy and Visual block; Q10 block check comes only in `.07` after this card (`GF-01/03/04/05/06`). |
| `M4.05` (`3195`; compare_methods) | `C`; Ex `:1,3t$<CR>`; linewise yank/put alternative | `G` for `C/yy`; `G—` for `:t`; `I/C—` (M4.03 omits Q05); no guided Ex copy | `H=self`; no R | `K=fallback`; `Δ+` cursor-independent copy, but no `:t` vocabulary | `P=none`; compare two complete return-midpoint methods and seam copy. Gap: hidden Ex copy without prior guided grammar (`GF-03/04/05/06`). |
| `M4.06` (`3279`; transfer) | Ex `:1,3t3<CR>`; `G/C` redraw | `G` for C M4.01; `G—` for `:t`; `I~M4.Q06`; `C—` | `H=self`; `R=transfer×2`, after pass | `K=fallback`; `Δ+` addressed copy and changed midpoint strategy | `P=none`; changed prop keeps pivot and inserts complete middle. Gap: :t still lacks guided stage and no paired edit question (`GF-03/04/05`). |
| `M4.08` (`3432`; module_check) | `G`; counted linewise delete `3dd` | `G—` for `G/dd`; `I~M4.Q07/Q09` before check; `C—`; no guided `dd` | `H=self`; `R=M4.08` two changed variants, after pass | `K=fallback`; `Δ−` says dot repeat although expected path is `13G3dd` | `P=Q01–Q10 bank; five selected before artifact`; delete redundant seam frame, preserving clean rotation loop. Gap: `dd` has no guided introduction; hint is wrong; mastery precedes review (`GF-01/04/05/06/07`). |

## Command-family first-use ledger

This ledger isolates the first current hidden requirement for each family. The
legacy grammar chapters are deliberately listed as source-only. The first
guided column is the earliest current card that performs the family with keys
shown; `—` means no such card exists in M0–M4.

| Family and grammar | First current guided use | First hidden use in M0–M4 | Prior concept/completion before that hidden use | Changed-art review | Safe insertion point / gap |
|---|---|---|---|---|---|
| Normal landmark motions `j`, `0`, `f{char}`; standalone | `M0.01` (`json:594`) | `M0.06` (`1008`) for unfamiliar transfer | `M0.Q06` is a partial paired selection; no parse/completion | `M0.01` changed variants; not a staged family review | Add grammar + interpretation/completion before `M0.01`; add hidden retrieval after guided (`GF-01/04/05`). |
| Absolute line motions `gg` vs `G` | `gg` shown `M0.02` (`725`); `G` has no guided card | `G` first hidden `M0.04` (`848`) | No prior question distinguishes `gg` from `G` | None | Insert a motion-grammar card before M0.04; require a completion choice for “go to last line” (`GF-01/05`). |
| Standalone `r{char}` | `M0.01` (`594`) | `M0.06`/`.08` | Related Q06, but no pre-guided interpretation | `M0.01` variants only | Pair M0.01 with an interpretation/completion item and later changed-art retrieval (`GF-04/05`). |
| Linewise `yy` + `p/P` (`[count]yy`, standalone put) | `M0.02` (`725`) | `M0.04` (`848`) | `M0.Q02` in M0.03 after guided; no prior parse | None | Add a grammar card before M0.02; add explicit `3yy`/`p` interpretation and completion before M0.04; add R (`GF-01/04/05/06`). |
| Ex substitution `:[address/range]s/pattern/replacement/[g]<CR>` | `M0.02` (`725`) | `M0.04` (`848`) | `M0.Q06` is effect selection; it does not parse `8`, `s`, `-`, `=`, `g`, Enter | None | Before M0.02 teach range + `s` + delimiters + replacement + `g` + Enter; before M0.04 ask `:8s/-/=/` completion `g<CR>` (`GF-03/05/06`). |
| Ex addressed copy `:[range]t{address}<CR>` | — | `M0.05` (`923`) | No prior question; Q07 appears only later on M0.07 | None | Insert a visible guided `:t` card before M0.05, then interpretation and completion (`GF-03/04/05/06`). |
| Search `/pattern<CR>` and repeat | `M1.01` (`1223`) | No hidden use in M0–M4 | No later retrieval | None | Pair M1.01 with grammar/interpretation and add a hidden changed-art search card before claiming family mastery (`GF-01/04/05`). |
| Counted linewise delete `dd/3dd` | — | `M1.04` (`1377`) | M1.Q04 (3dd) is not in M1.03’s selected IDs; M4.Q07 appears only later | None | Insert guided linewise deletion before M1.04 and a scope completion item (`GF-01/02/04/05`). |
| Standalone open-line `o/O` plus Insert entry | — | `M1.04` (`1377`) | No prior concept question | None | Add guided `o/O` card after linewise copy, including autoindent/column invariant and escape; only then hide it (`GF-02/04/05/11`). |
| Operator + text object `daw` | `M2.01` (`1685`) | No later hidden use in M0–M4 | No prior question before guided use | None | Precede M2.01 with `[operator] + [text object]` explanation and paired choice/completion (`GF-01/04/05`). |
| Matching `%` and `f(`/`h` motions | `M3.01` (`2208`) | No later hidden use in M0–M4 | No prior question before guided use | None | Add pre-guided delimiter-motion interpretation and completion; add changed-art hidden retrieval (`GF-01/04/05`). |
| Operator + text object `ci(` | — | `M3.04` (`2381`) | `M3.Q04` asks why `ci(` fits, but no grammar decomposition or guided edit | None | Add guided `ci(` card before M3.04; retain Q04 as interpretation and add completion (`GF-01/04/05/06`). |
| Visual-line `V` plus named register `"a`/`"ap` | — | `M3.06` (`2574`) | `M3.Q06` is a partial concept item before transfer | `M3.06` transfer×2 only | Add guided whole-pose Visual-line/register card before M3.06 and a register-scope completion (`GF-01/04/05/06`). |
| Digraph `<C-k>{key}` | — | `M3.08` (`2783`) | `M3.Q09` mentions digraph before check, but no guided performance | None | Add guided one-cell digraph edit before M3.08 and a completion item for `<C-k>.M` (`GF-01/04/05/06`). |
| `C` = `c$` (operator shorthand) | `M4.01` (`2891`) | `M4.04` (`3065`) | M4.Q01/Q03 partially interpret C before hidden; no grammar parse | None | Explain `C` as `c$` and pair a scope completion before M4.01; add R (`GF-01/04/05/06`). |
| Visual block `<C-v>` + blockwise `r` | — | `M4.04` (`3065`) | M4.Q10 appears only on M4.07, after first hidden use | None | Insert guided aligned-column block edit before M4.04; move Q10 before it and add completion (`GF-01/04/05/06`). |
| Dot repeat `.` | — | `M0.08` (`1129`) in `for.` / M1.05 alternative | No prior paired interpretation or guided dot edit | None | Add guided repeat card before first hidden dot, then changed-art retrieval; fix M4.08 hint so it does not claim dot (`GF-01/04/05/07`). |

## Cross-cutting findings

### The current generator has no grammar or sequence contract

`step()` accepts only start/target/expected/recipe plus optional alternatives,
method evidence, review variants, and vocabulary (`gen_curriculum_v2.py:70-87`).
`make_cards()` assigns card kinds by ordinal and hides recipes on 4/5/6/8
(`gen_curriculum_v2.py:3398-3429`), while it assigns questions only to concept
cards and module checks (`3443-3477`). There is no field for command families,
grammar class, stage, prerequisite question, or paired question IDs. The
validator checks four choices, paired text halves, and review-shape integrity,
but not first-use ordering (`3594-3634,3712-3785`).

### The runtime pairs concepts with reviews, not ordinary performance cards

`run_concept()` asks one question only for a concept card and then completes
that card (`v2_runtime.py:1465-1511`). `run_edit()` invokes questions only for
module checks (`1605-1618`); ordinary guided, independent, comparison, and
transfer attempts proceed directly to Neovim. The post-pass module check asks
five questions and then one artifact edit (`1545-1602`), which is a useful
checkpoint but not a paired conceptual item for each earlier command family.

### Review links are sparse and scheduled too late for the stated gate

The generator links a card to review only when it has `review_variants` or is a
transfer card (`gen_curriculum_v2.py:3483-3492`). In M0–M4 that yields review
links only for M0.01, M0.06, M1.06, M2.06, M3.06, M4.06, and M4.08. The runtime
sets `next_due` when the source card passes (`v2_runtime.py:1417-1419`), so a
later review cannot be evidence required before that source card or module is
mastered. `run_review()` does correctly combine a conceptual question and a
changed-art edit once a review is due (`1885-1933`); the sequencing gate must be
moved earlier or mastery must explicitly wait for the required review stage.

### Legacy grammar is valuable source material but currently leaks into briefs

The legacy curriculum contains the desired “Vim is a language” framing and
Normal operator examples (`share/curriculum.json:26-48`). The v2 generator
attaches legacy lessons by mapping IDs (`gen_curriculum_v2.py:3514-3529`), and
the runtime merges their keys and paradigm prose into `KEYS WORTH KEEPING`
(`v2_runtime.py:604-681`). This preserves parity context, but it does not make
the current v2 card a grammar stage: the learner is not required to read the
legacy chapter, answer a paired question, and perform a guided edit before a
hidden v2 use. The table marks those rows `legacy` rather than taught.

### Hints usually add strategy, but the heuristic has observable false positives

The generated hints add frame scope and a failure condition (`gen_curriculum_v2.py:3236-3301`),
which is good information gain over most `DO THIS` prompts. Two M0–M4 cases
need correction during implementation:

- M3.06’s hint detects `ap` and claims a paragraph text object, although the
  transfer path is Visual-line selection plus named-register put
  (`curriculum-v2.json:2574-2740`).
- M4.01’s hint detects the literal slash typed as art and claims search; its
  required operation is `C` plus local `r` (`curriculum-v2.json:2891-2965`).
- M4.08’s hint says dot repeat because the recipe explanation contains
  “repeated”, but the required path is `13G3dd`; this is a direct misleading
  hint (`curriculum-v2.json:3432-3618`).

These are not merely cosmetic: `GF-07` requires the hint to teach a strategy
that is true of the accepted operation.

## Proposed insertion sequence

These are insertion points for the implementation phase; this audit does not
apply them.

1. Before `M0.01`, add a short grammar card distinguishing standalone Normal
   motions/replace from operator grammar, then pair interpretation and
   completion with the first one-cell edit.
2. Before `M0.02`, add a guided grammar card for `3yy` + `p/P` and Ex
   `:[range]s/pattern/replacement/g<CR>`. It must name every Ex component and
   perform the edit on a three-row frame.
3. Before `M0.04`, place a decode item that asks what `:8s/-/=/g` means and a
   completion item that asks what follows `8s/-/=/` (`g<CR>`), plus a paired
   `3yy/p` interpretation or open-key item. Multiple choice is appropriate only
   where its distractors diagnose a concrete misconception. M0.04 may then
   remain key-hidden.
4. Before `M0.05`, add a guided Ex-copy card for `:[range]t{address}<CR>` and
   a range/address completion item. Do not treat `:t` in M0.05’s expected path
   as its introduction.
5. Before `M1.04`, add guided linewise delete (`dd/3dd`) and `o/O` cards,
   including the real-config column-registration invariant and an Enter/Escape
   completion check.
6. Before `M2.01`, add the `[count] operator [count] motion/text-object`
   explanation and a guided `daw` card with a paired scope question.
7. Before `M3.04`, add a guided `ci(` card; before `M3.06`, add guided
   Visual-line + named-register copying; before `M3.08`, add guided digraph
   input. Each requires changed-art retrieval before its module check can claim
   the family.
8. Before `M4.04`, add guided `C` grammar (`C=c$`) if M4.01 remains the first
   performance, then guided Ex copy and aligned Visual block `r`; move M4.Q10
   before the hidden block edit. Add a guided `dd`/seam-repair card before
   M4.08 and repair its hint.

## Acceptance tests for implementation

The implementation phase should add tests that fail on the current data and
pass only after the insertion work:

1. Every executable M0–M4 card declares command-family IDs, grammar class,
   `paired_question_ids`, and required review source. The generator rejects a
   missing declaration.
2. For each family in the first-use ledger, a validator computes the first
   hidden card and rejects it unless current grammar, interpretation,
   completion, and guided performance precede it. Legacy attachments,
   answer keys, and distractors are excluded from this computation.
3. Every executable card has at least one paired item whose Vim half tests the
   operation/scope and whose animation half tests the visible invariant. Its
   authored placement may be before or after performance; any exception needs
   a card-specific reason. Tests cover open semantic-key, decode, completion,
   prediction, why, and diagnostic multiple-choice forms. Module checks retain
   an explicit threshold without replacing earlier paired teaching.
4. Ex questions test address/range, command, pattern, replacement, flags, and
   Enter separately. Specifically replay `:8s/-/=/g<CR>` and
   `:4,6s/o/O/g<CR>` as parse/completion cases before M0.04.
5. Hidden cards expose family vocabulary and grammar without exposing their
   exact accepted sequence. The test rejects vocabulary that is only a raw
   recipe or a misleading legacy paragraph.
6. Every hidden family has a changed-art variant that is run as a spaced edit
   review before the relevant mastery claim. The event ledger must show both
   concept and artifact evidence; a future-due review cannot satisfy a
   pre-mastery assertion.
7. Hint tests compare each hint with `DO THIS` and reject false-positive
   family labels such as M3.06 paragraph-object, M4.01 search, and M4.08 dot.
8. Real Neovim tests replay the M0.02 → conceptual parse → M0.04 route with
   the operator configuration. Any `o` test must verify that only the art
   buffer has `autoindent=false`, `smartindent=false`, `cindent=false`, and an
   empty `indentexpr`; the user's other buffers/config remain unchanged.
9. Run the full recipe and runtime suites in both clean and real modes, plus
   headed popup checks at 80×24, 100×36, and 188×49. These are execution and
   presentation gates, not substitutes for the sequencing assertions above.

## Verification performed for this report

- `python3 share/test_v2.py` passed: 114/114 primary recipes, 38/38 transfer
  variants, and 38/38 comparison paths under clean Neovim.
- `python3 share/test_v2.py --real` passed the same M0–M18 recipe suite under
  the real configuration.
- Those passes do not close the gaps in this report: the current tests assert
  M0.02’s guided shape, M0.04’s hidden recipe, paired-choice formatting, and
  review-variant execution, but do not assert grammar-stage ordering or
  ordinary-card question pairing (`share/test_v2.py:94-150,175-193`).

No commit was made by this audit subagent. The parent implementation lane must
commit this report with the other audit partitions before changing curriculum,
generator, runtime, or tests, as required by the commit boundary in
`share/audits/GRAMMAR_FIRST_REQUIREMENT.md:118-122`.
