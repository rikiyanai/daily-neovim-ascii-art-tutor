# Grammar-first sequence audit — M15–M18

Status: audit complete; implementation intentionally not changed by this report.

Baseline: generated curriculum revision `2026-09-28.22`, current preserved dirty
worktree. The module definitions are in `share/gen_curriculum_v2.py:1711-2453`;
the generated executable cards are in `share/curriculum-v2.json:10344-13723`;
their paired question bank is in `share/curriculum-v2.json:18805-20125`.
Legacy prose and answer-key occurrences were not counted as teaching evidence.

## Verdict

All 24 executable cards in M15–M18 are mechanically passable, and the generated
data has changed-art banks for most method-bearing cards. The grammar-first
contract is not met. The main defects are sequencing and ownership defects, not
missing ASCII targets:

1. There is no machine-readable grammar stage or completion-question stage. The
   generator creates only `visual_reading`, `principle_choice`, `diagnosis`,
   `command_prediction`, `method_comparison`, `transfer_reasoning`,
   `coherence_check`, `principle_application`, `output_prediction`, and
   `risk_diagnosis` questions (`share/gen_curriculum_v2.py:3206-3219`). None is a
   command-completion item that checks a missing address, command, replacement,
   flag, or `<Enter>`.
2. Executable cards do not carry paired question IDs. `make_cards` attaches
   questions only to `.03`, `.07`, and `.08` (`share/gen_curriculum_v2.py:3443-3477`).
   Thus the nearest conceptual card is not evidence paired to the edit that
   follows it, and the first conceptual encounter is generally after a guided
   performance rather than before it.
3. New M15–M18 families are often first used by a guided recipe or a hidden
   compare/check path, without the required explanation → interpretation →
   completion → guided sequence.
4. Hidden cards have no `key_vocabulary` in M15–M18. The runtime therefore falls
   back to generic F1/undo/redo/save prose (`share/v2_runtime.py:720-730`), or
   imports a legacy attachment. Legacy attachment is explicitly not valid proof
   under the requirement.
5. Reviews are scheduled after a card passes, but module mastery checks require
   only a passed transfer artifact, not a passed changed-art review
   (`share/v2_runtime.py:1412-1442`). A future review is therefore not evidence
   available before the mastery claim.
6. The current tests prove 152 recipes, paired four-choice questions, method
   coverage, and review-bank execution, but no grammar ordering, completion
   evidence, card-to-question pairing, or review-before-mastery invariant
   (`share/test_v2.py:88-193,206-238,788-900`). `python3 share/test_v2.py` passes
   the existing suite; that passing result does not close these gaps.

## Evidence codes

The tables use the following strict meanings:

- `G` — a visible guided edit with a displayed recipe.
- `I` — a conceptual interpretation item tied to the command family.
- `F` — a command-completion item (missing grammar component supplied by the
  learner). No current M15–M18 item qualifies as `F`.
- `H` — a later key-hidden retrieval of that family.
- `R` — a changed-art review bank explicitly linked to the source card.
- `KWK` — card-owned `KEYS WORTH KEEPING` vocabulary. A recipe shown on a
  guided card is not a grammar explanation; generic F1 text is not vocabulary.

Normal-mode operator grammar is recorded as `[count] operator [count]
motion-or-text-object`; linewise `yy` is the self-motion form of the yank
operator. Standalone commands such as `p`, `P`, `r`, `C`, `q`, `@`, `<C-a>`, and
Visual-block append are not forced into that grammar. Ex commands are recorded
as `:[address-or-range] command /pattern/replacement/ flags <Enter>` where that
shape applies; `:set`, `:t`, `:m`, and `:read` are separate Ex command families
with their own command-specific grammar.

## Command-family ledger

| Family required by M15–M18 | Grammar class | Prior evidence that is actually valid | Sequence finding and insertion point |
|---|---|---|---|
| `3yy`/`yy` plus `p`/`P` whole-frame copy | Normal operator + standalone put | `M0.02` is a visible guided recipe and now has generic frame-copy vocabulary (`share/curriculum-v2.json:750-768`). `M0.Q02`/`Q08` interpret count/scope, but after the guided card; no completion item. `M0.04` is hidden retrieval (`:882-896`) but has no changed-art bank. | Grammar is partly present, but interpretation is late, completion is absent, and no source-linked changed-art review proves this family for M15.02/M18.02. Add a prelude before the first guided copy and a changed-art copy review before any module claim relying on it. |
| `:set shiftwidth=1` | Ex option command (`:set option=value <Enter>`) | None before M15.01. First use is the guided recipe in `share/gen_curriculum_v2.py:1722-1731`. | First-use-before-grammar gap. Add an addressed option grammar explanation, interpretation, completion, then guided one-cell registration edit before M15.01. |
| `>>` | Normal operator grammar: `>` operator + `>` linewise self-motion; one indent step is controlled by `shiftwidth` | None before M15.01; the same step definition is `gen_curriculum_v2.py:1722-1731`. M15.Q01/Q03 explain the effect only after the guided edit (`gen_curriculum_v2.py:2803-2807`). | First-use-before-grammar and no completion. Add operator decomposition and a completion item for the second `>`/count before M15.01. |
| `:s` substitution, including `:4s/:/./g` and `:4,6s/$/|/` | Ex substitution: `:[address/range]s/pattern/replacement/flags<Enter>` | M0.02 now displays the abstract `:{start},{end}s/old/new/g` vocabulary (`curriculum-v2.json:766-768`); M0.Q03 interprets a bounded substitution after the guided edit. M0.04 is hidden retrieval. No completion item parses address, `s`, pattern, replacement, `g`, and Enter separately. | The family has a useful seed explanation, but the required interpretation/completion-before-guided order is missing. Add explicit parse and fill-in items before any M15 substitution. |
| Visual block `<C-v>…$A` | Standalone Visual-block selection + append; not Normal operator grammar | First current use is hidden independent `M4.04` (`share/gen_curriculum_v2.py:442-483`; its legacy `block-append` attachment is not evidence). M15.05 is the next hidden compare use (`gen_curriculum_v2.py:1792-1821`). | Severe first-use-before-teaching gap: no visible guided blockwise performance or prior paired interpretation/completion. Insert a guided Visual-block card before M15.05 and teach `$A` versus `I` scope on differently sized rows. |
| Addressed Ex copy `:range t destination` | Ex copy grammar: `:[range]t{destination}<Enter>` | `M0.05` first mentions it in a hidden compare; `M6.02` is the first visible guided `:1,5t$` (`share/gen_curriculum_v2.py:665-700`). `M6.Q02` interprets range copy after that guided card. No completion item. | A guided path exists before M15, but grammar and completion are missing, and M15.08/M16.04/M18.08 hide the family without card-owned vocabulary. Add an Ex-range copy prelude and paired retrieval. |
| Macro record/replay `qq…q`, `@q`, `3@q` | Standalone Normal macro commands | No valid guided introduction. The first executable use is the hidden comparison alternative on M7.05 (`gen_curriculum_v2.py:809-824`); M15.08 is the first required primary/check path (`:1824-1857`), and M17.08 repeats it (`:2208-2251`). Same-card legacy macro prose does not count. M15.Q09 interprets macro count only within the module check. | Severe first-use-before-teaching gap. Add a visible macro guided edit, grammar interpretation, completion of register/replay count before M7.05, then retain M15.08 as later retrieval. |
| `<C-a>` number increment | Standalone Normal command | First use is guided M16.01 (`gen_curriculum_v2.py:1891-1916`). M16.Q01/Q03 explain effect after that card (`gen_curriculum_v2.py:2815-2819`). | First-use-before-grammar and no completion. Add `CTRL-A` meaning/scope parse and completion before M16.01; keep changed-art review. |
| `:read %` | Ex read grammar: `:read {file-or-register}<Enter>` | First use is guided M16.02 (`gen_curriculum_v2.py:1918-1946`). M16.Q02/Q10 explain saved-source semantics only after it. | First-use-before-grammar and no completion. Add a source/file/register interpretation and completion item before M16.02. |
| `:m` and linewise delete/put reorder | Ex move `:[range]m{destination}<Enter>` plus Visual-line/linewise delete-put | `:m` first appears hidden in M6.06/M6.08; M16.05 is a hidden compare (`gen_curriculum_v2.py:1982-2018`). The linewise alternative also first appears in that compare. M16.Q05 is held until M16.08. | Severe first-use-before-teaching gap for both methods. Add a guided whole-block reorder, Ex-range grammar/completion, and paired method comparison before M16.05. |
| Search `/pattern<Enter>`, `n`, and dot `.` | Search command + standalone next-match and repeat | `/` has an earlier guided search in M1.01; no grammar decomposition or completion. `n`/dot are not given a valid prior guided grammar stage; M17.01 is the visible recipe that first combines them (`gen_curriculum_v2.py:2092-2130`). | M17.01 is a guided first combination, but no pre-grammar interpretation/completion and no earlier paired search-repeat lesson. Add search grammar and a completion item before M17.01. |
| `:global/pattern/normal! …<Enter>` | Ex global selector + Normal command payload | First appears as the hidden comparison alternative on M7.05 (`gen_curriculum_v2.py:809-824`) and appears again on M17.05 (`:2163-2206`); M17.Q05 asks for selector safety only in the later check bank. | Severe first-use-before-teaching gap. Add a guided `:global`/`:normal` card, then a completion item for pattern and payload before M7.05; keep M17.05 as changed-art retrieval. |
| `C` change-to-end-of-line | Normal operator shorthand for `c$`, followed by Insert text and `<Esc>` | `C` has a visible guided use in M4.01; M18.01 repeats it with a recipe (`gen_curriculum_v2.py:2293-2320`). No explicit operator decomposition or completion precedes either. | Prior performance exists, but grammar evidence is absent. Add `C = c$` interpretation/completion and require row-width/registration reasoning before M18.01. |
| `r{char}` single-cell replace | Standalone Normal replace command | Earlier guided single-cell replacements exist (for example M0.01/M1.01), but no explicit standalone grammar stage or completion. M18.05 uses `r1` in a hidden comparison (`gen_curriculum_v2.py:2364-2393`). | Interpretation is late and expression alternative is first-use hidden. Add standalone `r{char}` parse/completion before the M18 comparison. |
| Expression substitute `:line s/0/\=getline(...)/<Enter>` | Ex substitution with expression replacement; `\=` changes replacement semantics, `getline()` reads existing art | First use is hidden alternate on M18.05 (`gen_curriculum_v2.py:2364-2393`). M18.Q05/Q10 explain validation-only scope only in the module-check bank (`gen_curriculum_v2.py:2839-2851`). | Severe first-use-before-teaching gap. Add a guided validation-only expression card and a completion item distinguishing `\=` from art generation before M18.05. |

Basic navigation (`gg`, `G`, `j`, `k`, `0`, `f{char}`, numeric `G`) is used throughout these cards. It has earlier executable exposure, but it is not decomposed or paired at the point of use; when a new landmark motion is material to a family, the insertion should name it rather than silently treating it as recipe glue.

## Executable-card audit

The card ranges cited below are the generated source of truth: M15 is
`share/curriculum-v2.json:10344-11118`, M16 `:11120-12126`, M17 `:12128-12991`,
and M18 `:12993-13653` (with each `.08` check continuing immediately after the
shown range). `Pairing` means card-owned question IDs; a nearby `.03`/`.07`
question is not a pairing unless the runtime links it to this edit.

### M15 — Texture ground

| Card | Required families (class) | Prior teaching / current G | Conceptual pair and completion | Later H | R | KWK / strategy hint | Gap IDs and insertion |
|---|---|---|---|---|---|---|---|
| M15.01 | `:set shiftwidth=1` (Ex option), `>>` (Normal operator), `j` (motion) | `:set`/`>>`: none; current card is visible G with recipe (`gen_curriculum_v2.py:1722-1747`) | No card-owned pair; nearest M15.Q01/Q03 follows G. No F. | M15.04 and M15.06 hide the offset, but neither teaches the grammar first. | Own two changed-art variants. | Recipe is visible; hint is generic and omits both `shiftwidth` and `>>`, adding only frame scope/failure diagnosis. | GF-01/03/04/05/06/07/08. Insert option/operator grammar + I/F before M15.01; add card `paired_question_ids` and vocabulary. |
| M15.02 | `3yy` (Normal operator), `p` (standalone put), `gg/G` (motions) | Prior M0.02 G; its vocabulary explains `{count}yy` and `p/P`, but M0.Q02/Q08 are late I-only. Current G is visible (`gen_curriculum_v2.py:1749-1759`). | No pair; no F. | No later M15–M18 hidden card requires this exact `yy/p` family; M17.02/M18.02 are visible G copies. | No source-linked R for M15.02. | Counted linewise yank/put hint is useful and adds scope. | GF-01/04/05/08/10. Add a changed-art linewise-copy review and a hidden retrieval before module mastery. |
| M15.04 | `:set`, `>>`, `:4s/:/./g` (Ex substitution), `5G` | `:s`: M0.02 vocabulary/G and late M0.Q03 I; `:set`/`>>`: M15.01 G only. Current card is hidden H (`gen_curriculum_v2.py:1760-1790`). | No pair; no F. | Current card is the first hidden combined retrieval for the new offset family. | Own two changed-art variants. | Hint names bounded substitution and failure scope, but not Ex grammar or the option/operator. | GF-01/03/04/05/06/08. Add prelude I/F and KWK syntax before this hidden card. |
| M15.05 | `<C-v>2j$A` (Visual block + standalone append), `:4,6s/$/|/` (Ex substitution) | Visual block first appears hidden in M4.04; legacy block-append text is not evidence. `:s` has M0.02 G/vocabulary only. Current card is hidden compare H (`gen_curriculum_v2.py:1792-1822`). | No pair; M15.Q05 is only in `.08`, after this H. No F. | Current compare is the first exercise of both methods in this module. | Own two changed-art variants. | Visual-block hint adds real scope information; legacy attachment would display keys but is excluded from evidence. | GF-01/02/03/04/05/06/08/10. Insert guided block card + `:s` range parse before compare; add method-specific pair and vocabulary. |
| M15.06 | `:set`, `>>` (Normal/Ex offset) | M15.01 G only; no grammar/I/F. Current transfer is hidden H (`gen_curriculum_v2.py:1861-1878`). | No pair. No F. | Current card is changed-art H for the offset. | Own two changed-art transfer variants. | Hint leads with dot-repeat even though expected keys do not use dot; partial/misaligned strategy information. | GF-01/04/05/06/07/08. Replace with offset-specific hint, add pair and grammar vocabulary. |
| M15.08 | `:1,3t$` (Ex copy), `q…q`/`@q` (macro), `f:` (find), `r.` (standalone replace), `7G/0` (motions) | `:t`: M6.02 G but no grammar/I/F; macro first appeared in the hidden M7.05 comparison and still has no guided stage; `r`/find have older G but no grammar stage. Current module check hides the artifact path (`gen_curriculum_v2.py:1824-1859`). | `.08` has all ten questions, including Q09, before the edit; they are interpretation/prediction, not F, and not card-paired to individual families. | Current card is H for macro and Ex-copy composition. | Own two changed-art variants. | Hint gives useful Ex-copy/landmark strategy but no macro or Ex grammar vocabulary. | GF-01/03/04/05/06/08/10. Insert macro and Ex-copy prelude; require R evidence before mastery. |

### M16 — Key-pose plan

| Card | Required families (class) | Prior teaching / current G | Conceptual pair and completion | Later H | R | KWK / strategy hint | Gap IDs and insertion |
|---|---|---|---|---|---|---|---|
| M16.01 | `<C-a>` (standalone Normal increment), `G/k/0/f0` (motions) | `<C-a>` first appears as visible G (`gen_curriculum_v2.py:1891-1917`). | No card-owned pair; M16.Q01/Q03 follow; no F. | M16.06 and M16.08 hide/transfer numeric increment. | Own two changed-art variants. | Hint explains counted number increment, but not the command grammar or numeric field scope. | GF-01/04/05/06/08. Add interpretation/completion before this G and pair the question with the edit. |
| M16.02 | `:read %` (Ex read), `<C-a>` | `:read` first appears visible G (`gen_curriculum_v2.py:1918-1946`); `<C-a>` comes from M16.01. | No pair; M16.Q02/Q10 are late I; no F. | M16.04/08 hide addressed copy plus increment but do not retrieve `:read`. | Own two changed-art variants. | Hint only explains number increment; it gives no source-file/read strategy, so it adds little over DO THIS. | GF-03/04/05/06/07/08. Add `:read {source}` grammar, source freshness completion, and card vocabulary. |
| M16.04 | `:1,5t$` (Ex copy), counted `<C-a>`, `14G/0/f12` | Ex copy has M6.02 G but no grammar/I/F; `<C-a>` M16.01 G. Current card hidden H (`gen_curriculum_v2.py:1947-1981`). | No pair; no F. | Current card is H for a complete five-line range copy plus numeric update. | Own two changed-art variants. | Hint names addressed copy and counted increment and adds scope; no grammar vocabulary. | GF-01/03/04/05/06/08. Add Ex-copy completion and pair before H. |
| M16.05 | `:6,10m0` (Ex move), Visual-line `V…d…P` alternative | `:m` first appears hidden in M6.06/M6.08; linewise delete/put alternative first appears here. Current compare is hidden H (`gen_curriculum_v2.py:1982-2018`). | No pair; M16.Q05 arrives only in `.08`; no F. | Current card is first comparison H for both methods. | Own two changed-art variants. | Ex move hint is useful, but no explanation or completion of destination semantics. | GF-01/03/04/05/06/08/10. Insert guided whole-block move and linewise alternative before this compare. |
| M16.06 | `<C-a>` plus motions | M16.01 G only; no grammar/I/F. Current transfer hidden H. | No pair; no F. | Changed-art H for increment. | Own two changed-art transfer variants. | Hint is reasonably specific for numeric increment but still lacks grammar vocabulary. | GF-01/04/05/06/08. Add pair and completion evidence. |
| M16.08 | `:1,5t$`, `<C-a>`, motions | Prior G exists for `:t`/`<C-a>` but grammar/I/F are absent. Current check hides the artifact (`curriculum-v2.json:11910-12126`). | All ten questions run before edit, but no F and no per-family pairing. | H for copy + increment. | Own two changed-art variants. | Hint is useful for range copy and increment but hidden card has generic KWK. | GF-01/03/04/05/06/08/10. Require review evidence before module mastery and add explicit family pairs. |

### M17 — Coherent anchors

| Card | Required families (class) | Prior teaching / current G | Conceptual pair and completion | Later H | R | KWK / strategy hint | Gap IDs and insertion |
|---|---|---|---|---|---|---|---|
| M17.01 | `/x<Enter>` (search), `n` (next match), `.` (repeat), `r` (standalone replace) | `/` has earlier M1.01 G; `n`/dot have no valid prior grammar stage. Current combined card is visible G (`gen_curriculum_v2.py:2092-2130`). | No pair; M17.Q01 follows in `.03`; no F. | M17.05/06/08 hide search-repeat/macro variants. | Own two changed-art variants. | Search/landmark/dot hint adds strategy and scope, but not command grammar. | GF-01/02/04/05/06/08. Add search/next/dot grammar and completion before this G. |
| M17.02 | `3yy`, `p`, `7G/G` | Earlier M0.02 G/vocabulary; no family-specific H/R in this card. Current G (`gen_curriculum_v2.py:2132-2161`). | No pair; no F. | No later hidden card tests this exact whole-pose copy. | No source-linked R. | Counted linewise copy hint is useful. | GF-01/04/05/08/10. Add changed-art review and a hidden whole-pose retrieval. |
| M17.04 | `f^r-`, `f_r-`, `2j/10G/0` (landmark motions + standalone replace) | `r` has old G but no grammar/I/F; current card is hidden H (`gen_curriculum_v2.py:2147-2162`). | No pair; M17.Q04 is only in `.08`; no F. | Current card is H for the new two-landmark operation. | No review bank on M17.04. | Hint falls back to generic smallest-operation wording; it does not teach visible landmark find/replace. | GF-01/02/04/05/06/07/08/10. Add guided landmark replace, completion, pair, and changed-art R before mastery. |
| M17.05 | Search + dot; `:g/o/normal! …` (Ex global + Normal payload) | Search/dot current M17.01 G; `:global`/`:normal` first appeared in the hidden M7.05 comparison and is repeated here (`gen_curriculum_v2.py:2163-2206`) without any guided stage. | No pair; M17.Q05 occurs only in `.08`; no F. | Current compare is a later H for the Ex family. | Own two changed-art variants. | Hint explains search/dot and warns about global scope, but does not expose global/normal grammar or completion. | GF-01/03/04/05/06/08/10. Add guided global-normal card and selector/payload completion before M7.05; retain this as changed-art retrieval. |
| M17.06 | Search, `n`, dot | M17.01 G only; no grammar/I/F. Current transfer H. | No pair; no F. | Changed-art H for search-repeat. | Own two changed-art transfer variants. | Hint is strategy-specific and useful, but no grammar vocabulary. | GF-01/04/05/06/08. Add pair and completion evidence. |
| M17.08 | Search, macro `q/@`, `r`, `n` | Search/dot G in M17.01; macro has only hidden uses in M7.05 and M15.08. Current module check H (`gen_curriculum_v2.py:2208-2251`). | All ten questions precede edit; Q09 interprets macro travel but no F and no card-level pairing. | H for macro replay. | Own two changed-art variants. | Macro/search hint is strategic but exact grammar vocabulary is absent. | GF-01/02/04/05/06/08/10. Add guided macro stage and require review before mastery. |

### M18 — Hand-mirrored return

| Card | Required families (class) | Prior teaching / current G | Conceptual pair and completion | Later H | R | KWK / strategy hint | Gap IDs and insertion |
|---|---|---|---|---|---|---|---|
| M18.01 | `C` (`c$` operator shorthand), `r` in later check, `0/j` (motions) | `C` has M4.01 G; `r` has older G; neither has grammar/I/F before use. Current C path is visible G (`gen_curriculum_v2.py:2293-2320`). | No pair; M18.Q01 is reached later; no F. | M18.04/06 hide repeated hand-authoring. | Own two changed-art variants. | The generated hint is misleading: literal `/` in the art causes `action_hint` to suggest search/dot even though the method is `C` row overwrite (`gen_curriculum_v2.py:3236-3301`; card hint in generated block). Legacy `mirror-run` prose is not evidence. | GF-01/02/04/05/06/07/08. Add `C=c$` grammar/completion and fix slash-literal hint classification before G. |
| M18.02 | `4yy`, `p`, `G/gg` | Earlier M0.02 G/vocabulary; current G (`gen_curriculum_v2.py:2321-2331`). | No pair; no F. | No hidden whole-frame copy retrieval specific to this card. | No source-linked R. | Counted linewise copy hint is useful. | GF-01/04/05/08/10. Add changed-art R and hidden retrieval. |
| M18.04 | `C` plus motions | M4.01/M18.01 G but no grammar/I/F. Current card is hidden H (`gen_curriculum_v2.py:2332-2363`). | No pair; M18.Q04 only arrives in `.08`; no F. | Current H for the overshoot. | Own two changed-art variants. | Same misleading search/dot hint as M18.01; no C/row-overwrite strategy. | GF-01/02/04/05/06/07/08. Fix hint and add card-paired C grammar evidence. |
| M18.05 | `r1` (standalone replace); expression `:4s/0/\=getline(1)…/` (Ex expression substitute) | `r` has old G; expression substitution first appears hidden alternative (`gen_curriculum_v2.py:2364-2393`). | No pair; M18.Q05 is only in `.08`; no F. | Current compare is H for expression validation. | Own two changed-art variants. | Generic hint does not teach check-only expression scope; it adds almost no information beyond DO THIS. | GF-01/03/04/05/06/07/08/10. Insert guided validation-only expression card and completion before compare. |
| M18.06 | `C` plus row motions | M18.01 G only; no grammar/I/F. Current transfer H. | No pair; no F. | Changed-art H for hand mirror. | Own two changed-art transfer variants. | Misleading search/dot hint; no C vocabulary. | GF-01/02/04/05/06/07/08. Fix hint, add pair and completion. |
| M18.08 | `:5,8t$`, `:1,4t$` (Ex range copy) | `:t` has M6.02 G but no grammar/I/F. Current check hides both paths (`gen_curriculum_v2.py:2396-2433`). | All ten questions precede edit; Q07/Q08 interpret range/hold but no F and no per-family pair. | H for reverse range reuse. | Own two changed-art variants and duplicate/hold metadata. | Ex-copy hint is useful but generic KWK is absent. | GF-03/04/05/06/08/10. Add Ex-copy completion and require changed-art review before mastery. |

## Runtime and test contract gaps

### 1. Questions are not paired to executable cards

The generator assigns question IDs only to concept cards and module checks
(`share/gen_curriculum_v2.py:3443-3477`). `run_concept` asks a concept card as a
separate route (`share/v2_runtime.py:1465-1511`), while `run_edit` runs the edit
without asking a paired concept (`share/v2_runtime.py:1714-1813`). Add a
machine-readable `paired_question_ids` (at minimum interpretation and completion)
to every executable card, and make the edit route record/pass those outcomes
before awarding family-specific evidence.

### 2. Hidden-card vocabulary is not owned by the card

M15–M18 cards have no `key_vocabulary` field (the generated ranges above show
only `recipe`, `hint`, and generic metadata). `_write_session_lesson` imports
legacy keys and otherwise falls back to the generic save/undo text
(`share/v2_runtime.py:636-640,667-674,720-730`). Add card-owned grammar lines to
every hidden card. Do not rely on `legacy_lessons`, whose attachment is expressly
excluded from teaching evidence.

### 3. Hints can be mechanically wrong

`action_hint` detects a slash anywhere in the expected string and treats it as
search (`share/gen_curriculum_v2.py:3278-3283`). M18 art rows contain literal
slashes, so M18.01/M18.04/M18.06 receive search/dot advice despite using C and
hand-authored row overwrites. Make hint detection token-aware and author a
family-specific fallback for `C`, expression validation, `:set`, and macro paths.

### 4. Review is after, not before, mastery

Passing a review-capable card only writes `next_due` (`share/v2_runtime.py:1417-1419`).
The module check then verifies the existence of a passed transfer event, not a
passed review event (`share/v2_runtime.py:1421-1442`). Change the evidence model so
the module check cannot claim family mastery until the required changed-art review
event(s) exist, or move the changed-art review into the pre-mastery route.

### 5. Result page has no explicit motivated continuation action

The result page's only completion action is “press Enter for skill-tree progress”
(`share/v2_runtime.py:1180-1197`); progress rendering prints the next card in
`_complete` but does not expose a second documented key for “next eligible
question/lesson now” (`share/v2_runtime.py:1451-1461,1371-1397`). Add close and
continue controls, with continuation using `next_card`/question eligibility and
never awarding XP without evidence.

## Proposed insertion points

These are content/runtime insertion points, not implementation changes in this
audit.

1. Add a grammar bridge before M15.01 (a prelude card or a new pre-M15 sequence)
   for `:set shiftwidth=1`, `>>`, linewise `yy/p`, Ex substitution, and addressed
   `:t`. It must contain paired interpretation and completion items in the form
   best suited to the intent—including open semantic-key answers—then visible
   edits. Add a separate guided Visual-block `$A` lesson before M15.05 and a
   guided macro lesson before M15.08.
2. Add a M16 prelude before M16.01/M16.02/M16.05 for `<C-a>`, `:read %`, `:m`,
   and linewise delete/put reorder. Put the Ex grammar and completion items before
   the first visible or hidden use.
3. Add a M17 prelude before M17.01 for `/`, `n`, `.`, and before M17.05 for
   `:global/pattern/normal!`. Use one guided changed-anchor edit, one completion
   item for selector/payload, and one hidden retrieval.
4. Add an M18 prelude before M18.01/M18.05 for `C=c$`, standalone `r`, and
   validation-only `\=`/`getline()`. Explicitly contrast manual art authoring
   with a check-only expression.
5. Attach `paired_question_ids`, `grammar_family`, `grammar_stage`, and
   `key_vocabulary` to each executable card. Keep exact keys hidden on H cards;
   vocabulary should name the family and grammar without copying the accepted
   path.
6. Add the review gate and close/continue result controls in the runtime before
   declaring M15–M18 mastery complete.

## Acceptance tests to add

1. **Grammar-order validator:** extract every command family from `expected`,
   method alternatives, and review variants; reject a hidden first use unless a
   preceding grammar explanation, interpretation, completion, and guided card
   exist. Legacy lesson text, answer keys, and distractors do not satisfy the
   query.
2. **Classification validator:** require Normal operator entries to declare
   `[count] operator [count] motion-or-text-object`; require standalone entries
   for `p/P`, `r`, `C`, `q/@`, `<C-a>`, and Visual-block append; require Ex entries
   to declare address/range, command, arguments/flags, and `<Enter>` where
   applicable.
3. **Pairing validator:** every executable M15–M18 card has an interpretation and
   completion question ID whose animation half names the card's invariant and
   whose Neovim half names its bounded operation. The runtime records both before
   method-specific completion credit.
4. **Question-form validator:** require authored schemas and evidence for open
   semantic-key, decode, completion, prediction, why, and diagnostic
   multiple-choice items. When multiple choice is justified, retain four
   mistake-specific feedback messages; completion tests distinguish wrong
   address/range, command, pattern, replacement, flag, and execution key.
5. **KEYS WORTH KEEPING test:** render every hidden M15–M18 brief at full and
   compact widths; assert family grammar vocabulary is present, exact accepted
   paths are absent, and legacy attachment text is not the only vocabulary.
6. **Hint information-gain test:** assert each hint adds scope/strategy or
   diagnostic information not present in DO THIS. Specifically assert M18 C cards
   do not receive search advice merely because art contains `/`.
7. **Real-Neovim paired path:** replay each new grammar question, guided edit,
   hidden retrieval, and changed-art review in real Neovim, in the art buffer with
   the lesson's buffer-local indentation settings. Check both target bytes and
   registered frame columns.
8. **Review-before-mastery test:** pass a module's conceptual/check and transfer
   artifact while omitting review; assert no mastery claim. Pass the changed-art
   review and assert mastery evidence records the review key/stage.
9. **Continuation test:** on result pages at 80×24, 100×36, and 188×49, assert
   one documented close action and one documented next-eligible action. The
   continue path must respect prerequisites and must not add XP without a pass.
10. Run the existing clean and real-config suites (`python3 share/test_v2.py` and
    the real-Neovim route) after the new grammar tests. Preserve the existing
    152-card, 190-question, method, viewport, ledger, and animation invariants.
