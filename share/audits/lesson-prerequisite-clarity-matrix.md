# Live lesson/question prerequisite and clarity audit

Artifact: share/curriculum-v2.json at commit 124292f (HEAD at audit time), revision 2026-09-28.24.
Read-only scope: every live card/question, edit brief, module check, transfer, and changed-art review linkage. No generator/runtime/curriculum/test file was edited.

> Resolution note (revision `.25`, 2026-09-28): this file remains the immutable
> `.24` audit snapshot. The 21 early-bank violations were removed by limiting
> every M*.03 bank to its two preceding guided concepts; compound decode
> contracts now include every inferred family; all 19 why questions now have
> card-specific prompts and contracts; Visual-line `V` and `C`/change-to-end
> are represented in the generated family/review ledger. A new test also scans
> command-looking backticks in every before-question against earlier guided
> performance, so metadata labels cannot mask the old M0.P0-style failure.

## Result

Generated inventory: 174 cards / 326 questions.

- 21 live multiple-choice questions fail G1/G3 when first used on a M*.03 concept card: later command families and/or later timing concepts are tested before their guided bridge.
- 8 decode contracts under-require their compound command. M5.02.P01 is the clearest direct failure: ggV6jyGp is Visual-line yank/put while its accepted vocabulary is motion/landmark.
- All 19 why contracts are under-specified: the prompt asks for method safety and the alternative risk, but the generic contract/sample need not name either method or concrete risk.
- Family metadata omits Visual-line V in M3.REG, M3.06, M5.02 and Normal C{text}<Esc> in the C-list below. Earlier visible recipes often make those actions learnable, but the family ledger is not truthful.
- Review skeleton passes at family level: all 28 command families have changed-art review rows; 73 cards have direct two-variant banks. M0.04, M0.05, M0.08 lack direct banks but map to later family reviews.

## Gate and evidence rule

Only an earlier visible guided recipe/bridge in modules[].card_ids order counts as teaching. Runtime generic hints and response-format examples do not. G1 = answer/perform from prior teaching; G2 = clear ask and accepted response/effect; G3 = sensible placement and review timing.

## Violation inventory

### V1: 21 future-prerequisite question uses

| Question | First live use | Later first teaching | Missing evidence | JSON locations |
|---|---|---|---|---|
| M0.Q07 | M0.03 | M0.T / M0.08 | Ex copy and the settle/check sequence arrive later. | share/curriculum-v2.json#/cards[id=M0.03]/question_ids; #/questions[id=M0.Q07] |
| M0.Q06 | M0.03 | M0.SL / M0.06 | Current-line substitute and unfamiliar transfer arrive later. | share/curriculum-v2.json#/cards[id=M0.03]/question_ids; #/questions[id=M0.Q06] |
| M0.Q09 | M0.03 | M0.T / M0.08 | Addressed copy and final settle command arrive later. | share/curriculum-v2.json#/cards[id=M0.03]/question_ids; #/questions[id=M0.Q09] |
| M1.Q03 | M1.03 | M2.01 | dW/operator-object is not guided before M1.03. | share/curriculum-v2.json#/cards[id=M1.03]/question_ids; #/questions[id=M1.Q03] |
| M1.Q09 | M1.03 | M1.05 | The % whole-file range is not taught before this stem. | share/curriculum-v2.json#/cards[id=M1.03]/question_ids; #/questions[id=M1.Q09] |
| M2.Q09 | M2.03 | M2.05 | The [.o] character-class substitute arrives later. | share/curriculum-v2.json#/cards[id=M2.03]/question_ids; #/questions[id=M2.Q09] |
| M3.Q04 | M3.03 | M3.CI | ci( is first guided in the later bridge. | share/curriculum-v2.json#/cards[id=M3.03]/question_ids; #/questions[id=M3.Q04] |
| M3.Q06 | M3.03 | M3.REG | Named-register pose storage arrives later. | share/curriculum-v2.json#/cards[id=M3.03]/question_ids; #/questions[id=M3.Q06] |
| M3.Q09 | M3.03 | M3.DI | Digraph entry arrives later. | share/curriculum-v2.json#/cards[id=M3.03]/question_ids; #/questions[id=M3.Q09] |
| M6.Q03 | M6.03 | M6.D | D/content-clear arrives later. | share/curriculum-v2.json#/cards[id=M6.03]/question_ids; #/questions[id=M6.Q03] |
| M6.Q06 | M6.03 | M6.MOVE | Ex move arrives later. | share/curriculum-v2.json#/cards[id=M6.03]/question_ids; #/questions[id=M6.Q06] |
| M6.Q09 | M6.03 | M6.D | D/content-clear arrives later. | share/curriculum-v2.json#/cards[id=M6.03]/question_ids; #/questions[id=M6.Q09] |
| M7.Q03 | M7.03 | M7.DOT | Dot-repeat arrives later. | share/curriculum-v2.json#/cards[id=M7.03]/question_ids; #/questions[id=M7.Q03] |
| M7.Q06 | M7.03 | M7.DOT | Dot-repeat arrives later. | share/curriculum-v2.json#/cards[id=M7.03]/question_ids; #/questions[id=M7.Q06] |
| M7.Q09 | M7.03 | M7.GLOBAL | Global-normal arrives later. | share/curriculum-v2.json#/cards[id=M7.03]/question_ids; #/questions[id=M7.Q09] |
| M11.Q04 | M11.03 | M11.UR | Undo/redo arrives later. | share/curriculum-v2.json#/cards[id=M11.03]/question_ids; #/questions[id=M11.Q04] |
| M11.Q08 | M11.03 | M11.VE | Virtual-column editing arrives later. | share/curriculum-v2.json#/cards[id=M11.03]/question_ids; #/questions[id=M11.Q08] |
| M12.Q04 | M12.03 | M12.FIND | ;/, character-find repeat arrives later. | share/curriculum-v2.json#/cards[id=M12.03]/question_ids; #/questions[id=M12.Q04] |
| M13.Q04 | M13.03 | M13.BE | E/count-W/B WORD work arrives later. | share/curriculum-v2.json#/cards[id=M13.03]/question_ids; #/questions[id=M13.Q04] |
| M13.Q06 | M13.03 | M13.BE | Counted W/B transfer arrives later. | share/curriculum-v2.json#/cards[id=M13.03]/question_ids; #/questions[id=M13.Q06] |
| M14.Q08 | M14.03 | M14.PARA | Paragraph-object/frame-boundary navigation arrives later. | share/curriculum-v2.json#/cards[id=M14.03]/question_ids; #/questions[id=M14.Q08] |

The runtime rotates the five IDs in each concept card question_ids, so these are live presentations, not dead bank rows. The same questions can be safe when selected later by the module check after the module is taught.

### V2: 8 compound decode contracts

| Question | Contract defect | JSON location |
|---|---|---|
| M0.02.P01 | compound copy + substitute, but contract only requires Ex substitute terms. | share/curriculum-v2.json#/questions[id=M0.02.P01]/answer_contract |
| M3.REG.P01 | Visual-line selection and final eye replacement are omitted from required terms. | share/curriculum-v2.json#/questions[id=M3.REG.P01]/answer_contract |
| M5.02.P01 | ggV6jyGp is Visual-line yank/put, but contract asks only motion/landmark. | share/curriculum-v2.json#/questions[id=M5.02.P01]/answer_contract |
| M8.02.P01 | yank/put + landmark navigation + C edits are not all required. | share/curriculum-v2.json#/questions[id=M8.02.P01]/answer_contract |
| M12.02.P01 | yank/put + T:/h/r joint edit are not all required. | share/curriculum-v2.json#/questions[id=M12.02.P01]/answer_contract |
| M13.02.P01 | yank/put + WORD movement/r edits are not all required. | share/curriculum-v2.json#/questions[id=M13.02.P01]/answer_contract |
| M14.PARA.P01 | final put-before P is omitted from required terms. | share/curriculum-v2.json#/questions[id=M14.PARA.P01]/answer_contract |
| M16.02.P01 | :read % and numeric increment are omitted from required terms. | share/curriculum-v2.json#/questions[id=M16.02.P01]/answer_contract |

### V3: 19 why contracts

All 19 are correctly placed after compare-method cards, but their two generic term groups and identical sample answer do not require the two clauses stated in the prompt.

| Questions | JSON locations |
|---|---|
| M0.05.P01, M1.05.P01, M2.05.P01, M3.05.P01, M4.05.P01 | share/curriculum-v2.json#/questions[id=M0.05.P01]/answer_contract, share/curriculum-v2.json#/questions[id=M1.05.P01]/answer_contract, share/curriculum-v2.json#/questions[id=M2.05.P01]/answer_contract, share/curriculum-v2.json#/questions[id=M3.05.P01]/answer_contract, share/curriculum-v2.json#/questions[id=M4.05.P01]/answer_contract |
| M5.05.P01, M6.05.P01, M7.05.P01, M8.05.P01, M9.05.P01 | share/curriculum-v2.json#/questions[id=M5.05.P01]/answer_contract, share/curriculum-v2.json#/questions[id=M6.05.P01]/answer_contract, share/curriculum-v2.json#/questions[id=M7.05.P01]/answer_contract, share/curriculum-v2.json#/questions[id=M8.05.P01]/answer_contract, share/curriculum-v2.json#/questions[id=M9.05.P01]/answer_contract |
| M10.05.P01, M11.05.P01, M12.05.P01, M13.05.P01, M14.05.P01 | share/curriculum-v2.json#/questions[id=M10.05.P01]/answer_contract, share/curriculum-v2.json#/questions[id=M11.05.P01]/answer_contract, share/curriculum-v2.json#/questions[id=M12.05.P01]/answer_contract, share/curriculum-v2.json#/questions[id=M13.05.P01]/answer_contract, share/curriculum-v2.json#/questions[id=M14.05.P01]/answer_contract |
| M15.05.P01, M16.05.P01, M17.05.P01, M18.05.P01 | share/curriculum-v2.json#/questions[id=M15.05.P01]/answer_contract, share/curriculum-v2.json#/questions[id=M16.05.P01]/answer_contract, share/curriculum-v2.json#/questions[id=M17.05.P01]/answer_contract, share/curriculum-v2.json#/questions[id=M18.05.P01]/answer_contract |

### V4: family-ledger omissions

| Cards | Omitted executable family | JSON location |
|---|---|---|
| M3.REG, M3.06, M5.02 | Visual-line V selection | share/curriculum-v2.json#/cards[id=M3.REG]/grammar_families and corresponding IDs |
| M4.05, M4.06, M5.04, M5.05, M8.02, M8.08, M9.02, M9.05, M10.02, M18.01, M18.04, M18.06 | Normal C{text}<Esc> change-to-end | share/curriculum-v2.json#/cards[id=M4.05]/grammar_families (same field for each listed ID) |

## Confirmed non-violations

- All 326 prompts have visible ANIMATION and NEOVIM sections.
- Forms: 190 multiple_choice, 39 typed_keys, 40 decode, 19 complete, 19 predict_art, 19 why. Runtime supplies explicit response-format examples; those examples were not counted as prior command teaching.
- All 76 hidden cards have an earlier guided family in the generated ledger; all 28 families have changed-art review coverage.
- All 19 compare-method questions are after their card; module checks ask their bank after prior module lessons and before the final artifact; transfers have two changed-art variants.

## Complete card matrix (174/174)

Question failures are listed at the card that first presents them. Card PASS means its own brief/target/effect/placement passed; family metadata notes remain in the review column.

| Card | Module/ord | Kind/stage | Families | Live questions | G1 | G2 | G3 | Review | First-use question failures |
|---|---:|---|---|---|---|---|---|---|---|
| M0.P0 | M0/0 | concept/explanation | operator-motion-object,normal-replace,ex-substitute | M0.P0.P01 | N/A | PASS | PASS | concept/check bank | — |
| M0.01 | M0/1 | guided_edit/guided | normal-replace,search-landmark,normal-motion | M0.01.P01 | GUIDED | PASS | PASS | direct changed-art x2 | — |
| M0.02 | M0/2 | guided_edit/guided | ex-substitute-range,linewise-yank-put,normal-motion | M0.02.P01 | GUIDED | PASS | PASS | family ex-substitute-range>M15.04, linewise-yank-put>M12.04, normal-motion>M1.06 | — |
| M0.O | M0/2.5 | guided_edit/guided | normal-open-line | M0.O.P01 | GUIDED | PASS | PASS | family normal-open-line>M8.04 | — |
| M0.03 | M0/3 | concept/interpretation | paired-animation-neovim-diagnosis | M0.Q01,M0.Q07,M0.Q02,M0.Q06,M0.Q09 | N/A | PASS | PASS | concept/check bank | M0.Q07,M0.Q06,M0.Q09 |
| M0.04 | M0/4 | independent_edit/hidden | ex-substitute-range,linewise-yank-put,normal-motion | M0.04.P01 | PASS | PASS | PASS | family ex-substitute-range>M15.04, linewise-yank-put>M12.04, normal-motion>M1.06 | — |
| M0.T | M0/4.5 | guided_edit/guided | ex-copy | M0.T.P01 | GUIDED | PASS | PASS | family ex-copy>M4.06 | — |
| M0.05 | M0/5 | compare_methods/hidden | ex-copy,linewise-yank-put,normal-motion | M0.05.P01 | PASS | PASS | PASS | family ex-copy>M4.06, linewise-yank-put>M12.04, normal-motion>M1.06 | — |
| M0.SL | M0/5.5 | guided_edit/guided | ex-substitute-line | M0.SL.P01 | GUIDED | PASS | PASS | direct changed-art x2 | — |
| M0.06 | M0/6 | transfer/hidden | ex-substitute-line,normal-replace,search-landmark | M0.06.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M0.07 | M0/7 | concept/interpretation | paired-animation-neovim-diagnosis | M0.Q03,M0.Q07,M0.Q10,M0.Q08,M0.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M0.08 | M0/8 | module_check/hidden | ex-copy,normal-replace,search-landmark,normal-motion | M0.Q01,M0.Q02,M0.Q03,M0.Q04,M0.Q05,M0.Q06,M0.Q07,M0.Q08,M0.Q09,M0.Q10 | PASS | PASS | PASS | family ex-copy>M4.06, normal-replace>M0.06, search-landmark>M0.06, normal-motion>M1.06 | — |
| M1.01 | M1/1 | guided_edit/guided | normal-replace,char-find-repeat,search-landmark | M1.01.P01 | GUIDED | PASS | PASS | family normal-replace>M0.06, char-find-repeat>M1.06, search-landmark>M0.06 | — |
| M1.02 | M1/2 | guided_edit/guided | linewise-yank-put,normal-motion | M1.02.P01 | PASS | PASS | PASS | family linewise-yank-put>M12.04, normal-motion>M1.06 | — |
| M1.03 | M1/3 | concept/interpretation | paired-animation-neovim-diagnosis | M1.Q01,M1.Q03,M1.Q02,M1.Q06,M1.Q09 | N/A | PASS | PASS | concept/check bank | M1.Q03,M1.Q09 |
| M1.DD | M1/3.5 | guided_edit/guided | linewise-delete | M1.DD.P01 | GUIDED | PASS | PASS | direct changed-art x2 | — |
| M1.04 | M1/4 | independent_edit/hidden | linewise-delete,normal-open-line,normal-motion | M1.04.P01 | PASS | PASS | PASS | family linewise-delete>M4.08, normal-open-line>M8.04, normal-motion>M1.06 | — |
| M1.05 | M1/5 | compare_methods/hidden | ex-substitute-range,normal-motion | M1.05.P01 | PASS | PASS | PASS | family ex-substitute-range>M15.04, normal-motion>M1.06 | — |
| M1.06 | M1/6 | transfer/hidden | normal-replace,char-find-repeat,search-landmark,normal-motion | M1.06.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M1.07 | M1/7 | concept/interpretation | paired-animation-neovim-diagnosis | M1.Q03,M1.Q07,M1.Q10,M1.Q08,M1.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M1.08 | M1/8 | module_check/hidden | ex-copy,normal-replace,char-find-repeat,search-landmark,normal-motion | M1.Q01,M1.Q02,M1.Q03,M1.Q04,M1.Q05,M1.Q06,M1.Q07,M1.Q08,M1.Q09,M1.Q10 | PASS | PASS | PASS | family ex-copy>M4.06, normal-replace>M0.06, char-find-repeat>M1.06, search-landmark>M0.06, normal-motion>M1.06 | — |
| M2.01 | M2/1 | guided_edit/guided | operator-motion-object,search-landmark,normal-motion | M2.01.P01 | GUIDED | PASS | PASS | family operator-motion-object>M3.04, search-landmark>M0.06, normal-motion>M1.06 | — |
| M2.02 | M2/2 | guided_edit/guided | linewise-yank-put,normal-motion | M2.02.P01 | PASS | PASS | PASS | family linewise-yank-put>M12.04, normal-motion>M1.06 | — |
| M2.03 | M2/3 | concept/interpretation | paired-animation-neovim-diagnosis | M2.Q04,M2.Q10,M2.Q02,M2.Q06,M2.Q09 | N/A | PASS | PASS | concept/check bank | M2.Q09 |
| M2.04 | M2/4 | independent_edit/hidden | normal-replace,search-landmark,normal-motion | M2.04.P01 | PASS | PASS | PASS | family normal-replace>M0.06, search-landmark>M0.06, normal-motion>M1.06 | — |
| M2.05 | M2/5 | compare_methods/hidden | ex-substitute-range,normal-replace,search-landmark,normal-motion | M2.05.P01 | PASS | PASS | PASS | family ex-substitute-range>M15.04, normal-replace>M0.06, search-landmark>M0.06, normal-motion>M1.06 | — |
| M2.06 | M2/6 | transfer/hidden | normal-replace,search-landmark | M2.06.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M2.07 | M2/7 | concept/interpretation | paired-animation-neovim-diagnosis | M2.Q03,M2.Q07,M2.Q10,M2.Q08,M2.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M2.08 | M2/8 | module_check/hidden | ex-copy,normal-replace,search-landmark,normal-motion | M2.Q01,M2.Q02,M2.Q03,M2.Q04,M2.Q05,M2.Q06,M2.Q07,M2.Q08,M2.Q09,M2.Q10 | PASS | PASS | PASS | family ex-copy>M4.06, normal-replace>M0.06, search-landmark>M0.06, normal-motion>M1.06 | — |
| M3.01 | M3/1 | guided_edit/guided | normal-replace,search-landmark,normal-motion | M3.01.P01 | PASS | PASS | PASS | family normal-replace>M0.06, search-landmark>M0.06, normal-motion>M1.06 | — |
| M3.02 | M3/2 | guided_edit/guided | linewise-yank-put,normal-motion | M3.02.P01 | PASS | PASS | PASS | family linewise-yank-put>M12.04, normal-motion>M1.06 | — |
| M3.03 | M3/3 | concept/interpretation | paired-animation-neovim-diagnosis | M3.Q04,M3.Q05,M3.Q01,M3.Q06,M3.Q09 | N/A | PASS | PASS | concept/check bank | M3.Q04,M3.Q06,M3.Q09 |
| M3.CI | M3/3.25 | guided_edit/guided | operator-motion-object | M3.CI.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M3.04 | M3/4 | independent_edit/hidden | operator-motion-object,normal-motion | M3.04.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M3.05 | M3/5 | compare_methods/hidden | ex-copy,linewise-yank-put,normal-motion | M3.05.P01 | PASS | PASS | PASS | family ex-copy>M4.06, linewise-yank-put>M12.04, normal-motion>M1.06 | — |
| M3.REG | M3/5.5 | guided_edit/guided | register | M3.REG.P01 | GUIDED | PASS | PASS | direct changed-art x2; NOTE omit V | — |
| M3.06 | M3/6 | transfer/hidden | normal-replace,register,search-landmark,normal-motion | M3.06.P01 | PASS | PASS | PASS | direct changed-art x2; NOTE omit V | — |
| M3.07 | M3/7 | concept/interpretation | paired-animation-neovim-diagnosis | M3.Q03,M3.Q07,M3.Q10,M3.Q08,M3.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M3.DI | M3/7.5 | guided_edit/guided | digraph | M3.DI.P01 | GUIDED | PASS | PASS | direct changed-art x2 | — |
| M3.08 | M3/8 | module_check/hidden | normal-replace,digraph,search-landmark,normal-motion | M3.Q01,M3.Q02,M3.Q03,M3.Q04,M3.Q05,M3.Q06,M3.Q07,M3.Q08,M3.Q09,M3.Q10 | PASS | PASS | PASS | direct changed-art x2 | — |
| M4.01 | M4/1 | guided_edit/guided | normal-replace,search-landmark,normal-motion | M4.01.P01 | PASS | PASS | PASS | family normal-replace>M0.06, search-landmark>M0.06, normal-motion>M1.06 | — |
| M4.02 | M4/2 | guided_edit/guided | linewise-yank-put,normal-motion | M4.02.P01 | PASS | PASS | PASS | family linewise-yank-put>M12.04, normal-motion>M1.06 | — |
| M4.03 | M4/3 | concept/interpretation | paired-animation-neovim-diagnosis | M4.Q01,M4.Q02,M4.Q03,M4.Q06,M4.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M4.VB | M4/3.5 | guided_edit/guided | visual-scope | M4.VB.P01 | GUIDED | PASS | PASS | direct changed-art x2 | — |
| M4.04 | M4/4 | independent_edit/hidden | ex-copy,visual-scope,normal-replace,normal-motion | M4.04.P01 | PASS | PASS | PASS | family ex-copy>M4.06, visual-scope>M15.05, normal-replace>M0.06, normal-motion>M1.06 | — |
| M4.05 | M4/5 | compare_methods/hidden | ex-copy,linewise-yank-put,normal-motion | M4.05.P01 | PASS | PASS | PASS | family ex-copy>M4.06, linewise-yank-put>M12.04, normal-motion>M1.06; NOTE omit C | — |
| M4.06 | M4/6 | transfer/hidden | ex-copy,normal-motion | M4.06.P01 | PASS | PASS | PASS | direct changed-art x2; NOTE omit C | — |
| M4.07 | M4/7 | concept/interpretation | paired-animation-neovim-diagnosis | M4.Q03,M4.Q07,M4.Q10,M4.Q08,M4.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M4.08 | M4/8 | module_check/hidden | linewise-delete,normal-motion | M4.Q01,M4.Q02,M4.Q03,M4.Q04,M4.Q05,M4.Q06,M4.Q07,M4.Q08,M4.Q09,M4.Q10 | PASS | PASS | PASS | direct changed-art x2 | — |
| M5.01 | M5/1 | guided_edit/guided | normal-replace,normal-motion | M5.01.P01 | PASS | PASS | PASS | family normal-replace>M0.06, normal-motion>M1.06 | — |
| M5.02 | M5/2 | guided_edit/guided | normal-motion | M5.02.P01 | PASS | PASS | PASS | family normal-motion>M1.06; NOTE omit V | — |
| M5.03 | M5/3 | concept/interpretation | paired-animation-neovim-diagnosis | M5.Q03,M5.Q10,M5.Q02,M5.Q06,M5.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M5.04 | M5/4 | independent_edit/hidden | normal-motion | M5.04.P01 | PASS | PASS | PASS | family normal-motion>M1.06; NOTE omit C | — |
| M5.05 | M5/5 | compare_methods/hidden | ex-copy,linewise-yank-put,normal-motion | M5.05.P01 | PASS | PASS | PASS | family ex-copy>M4.06, linewise-yank-put>M12.04, normal-motion>M1.06; NOTE omit C | — |
| M5.06 | M5/6 | transfer/hidden | normal-replace,normal-motion | M5.06.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M5.07 | M5/7 | concept/interpretation | paired-animation-neovim-diagnosis | M5.Q03,M5.Q07,M5.Q10,M5.Q08,M5.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M5.08 | M5/8 | module_check/hidden | normal-replace,search-landmark,normal-motion | M5.Q01,M5.Q02,M5.Q03,M5.Q04,M5.Q05,M5.Q06,M5.Q07,M5.Q08,M5.Q09,M5.Q10 | PASS | PASS | PASS | family normal-replace>M0.06, search-landmark>M0.06, normal-motion>M1.06 | — |
| M6.01 | M6/1 | guided_edit/guided | normal-replace,normal-motion | M6.01.P01 | PASS | PASS | PASS | family normal-replace>M0.06, normal-motion>M1.06 | — |
| M6.02 | M6/2 | guided_edit/guided | ex-copy | M6.02.P01 | PASS | PASS | PASS | family ex-copy>M4.06 | — |
| M6.03 | M6/3 | concept/interpretation | paired-animation-neovim-diagnosis | M6.Q02,M6.Q03,M6.Q01,M6.Q06,M6.Q09 | N/A | PASS | PASS | concept/check bank | M6.Q03,M6.Q06,M6.Q09 |
| M6.D | M6/3.5 | guided_edit/guided | linewise-delete | M6.D.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M6.04 | M6/4 | independent_edit/hidden | linewise-delete,normal-motion | M6.04.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M6.05 | M6/5 | compare_methods/hidden | ex-copy,linewise-yank-put,linewise-delete,normal-motion | M6.05.P01 | PASS | PASS | PASS | family ex-copy>M4.06, linewise-yank-put>M12.04, linewise-delete>M4.08, normal-motion>M1.06 | — |
| M6.MOVE | M6/5.5 | guided_edit/guided | ex-move | M6.MOVE.P01 | GUIDED | PASS | PASS | direct changed-art x2 | — |
| M6.06 | M6/6 | transfer/hidden | ex-move | M6.06.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M6.07 | M6/7 | concept/interpretation | paired-animation-neovim-diagnosis | M6.Q03,M6.Q07,M6.Q10,M6.Q08,M6.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M6.08 | M6/8 | module_check/hidden | ex-move | M6.Q01,M6.Q02,M6.Q03,M6.Q04,M6.Q05,M6.Q06,M6.Q07,M6.Q08,M6.Q09,M6.Q10 | PASS | PASS | PASS | family ex-move>M6.06 | — |
| M7.01 | M7/1 | guided_edit/guided | ex-copy | M7.01.P01 | PASS | PASS | PASS | family ex-copy>M4.06 | — |
| M7.02 | M7/2 | guided_edit/guided | ex-copy | M7.02.P01 | PASS | PASS | PASS | family ex-copy>M4.06 | — |
| M7.03 | M7/3 | concept/interpretation | paired-animation-neovim-diagnosis | M7.Q03,M7.Q07,M7.Q02,M7.Q06,M7.Q09 | N/A | PASS | PASS | concept/check bank | M7.Q03,M7.Q06,M7.Q09 |
| M7.DOT | M7/3.5 | guided_edit/guided | repeat | M7.DOT.P01 | GUIDED | PASS | PASS | direct changed-art x2 | — |
| M7.MAC | M7/4.5 | guided_edit/guided | macro | M7.MAC.P01 | GUIDED | PASS | PASS | direct changed-art x2 | — |
| M7.VIS | M7/4.75 | guided_edit/guided | visual-characterwise | M7.VIS.P01 | GUIDED | PASS | PASS | direct changed-art x2 | — |
| M7.04 | M7/4 | independent_edit/hidden | visual-characterwise,normal-replace,repeat,search-landmark,normal-motion | M7.04.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M7.GLOBAL | M7/4.75 | guided_edit/guided | global-normal | M7.GLOBAL.P01 | GUIDED | PASS | PASS | direct changed-art x2 | — |
| M7.05 | M7/5 | compare_methods/hidden | ex-substitute-range,global-normal,visual-characterwise,normal-replace,macro,search-landmark,normal-motion | M7.05.P01 | PASS | PASS | PASS | family ex-substitute-range>M15.04, global-normal>M17.05, visual-characterwise>M7.04, normal-replace>M0.06, macro>M15.08, search-landmark>M0.06, normal-motion>M1.06 | — |
| M7.06 | M7/6 | transfer/hidden | normal-replace,repeat,search-landmark,normal-motion | M7.06.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M7.07 | M7/7 | concept/interpretation | paired-animation-neovim-diagnosis | M7.Q03,M7.Q07,M7.Q10,M7.Q08,M7.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M7.08 | M7/8 | module_check/hidden | linewise-delete,normal-motion | M7.Q01,M7.Q02,M7.Q03,M7.Q04,M7.Q05,M7.Q06,M7.Q07,M7.Q08,M7.Q09,M7.Q10 | PASS | PASS | PASS | family linewise-delete>M4.08, normal-motion>M1.06 | — |
| M8.01 | M8/1 | guided_edit/guided | normal-replace,normal-motion | M8.01.P01 | PASS | PASS | PASS | family normal-replace>M0.06, normal-motion>M1.06 | — |
| M8.02 | M8/2 | guided_edit/guided | linewise-yank-put,search-landmark,normal-motion | M8.02.P01 | PASS | PASS | PASS | family linewise-yank-put>M12.04, search-landmark>M0.06, normal-motion>M1.06; NOTE omit C | — |
| M8.03 | M8/3 | concept/interpretation | paired-animation-neovim-diagnosis | M8.Q01,M8.Q03,M8.Q02,M8.Q06,M8.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M8.04 | M8/4 | independent_edit/hidden | normal-open-line,search-landmark,normal-motion | M8.04.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M8.05 | M8/5 | compare_methods/hidden | ex-substitute-range,normal-replace,search-landmark,normal-motion | M8.05.P01 | PASS | PASS | PASS | family ex-substitute-range>M15.04, normal-replace>M0.06, search-landmark>M0.06, normal-motion>M1.06 | — |
| M8.06 | M8/6 | transfer/hidden | normal-replace,normal-motion | M8.06.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M8.07 | M8/7 | concept/interpretation | paired-animation-neovim-diagnosis | M8.Q03,M8.Q07,M8.Q10,M8.Q08,M8.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M8.08 | M8/8 | module_check/hidden | ex-copy,search-landmark,normal-motion | M8.Q01,M8.Q02,M8.Q03,M8.Q04,M8.Q05,M8.Q06,M8.Q07,M8.Q08,M8.Q09,M8.Q10 | PASS | PASS | PASS | family ex-copy>M4.06, search-landmark>M0.06, normal-motion>M1.06; NOTE omit C | — |
| M9.01 | M9/1 | guided_edit/guided | normal-replace,search-landmark | M9.01.P01 | PASS | PASS | PASS | family normal-replace>M0.06, search-landmark>M0.06 | — |
| M9.02 | M9/2 | guided_edit/guided | linewise-yank-put,normal-motion | M9.02.P01 | PASS | PASS | PASS | family linewise-yank-put>M12.04, normal-motion>M1.06; NOTE omit C | — |
| M9.03 | M9/3 | concept/interpretation | paired-animation-neovim-diagnosis | M9.Q02,M9.Q05,M9.Q01,M9.Q06,M9.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M9.04 | M9/4 | independent_edit/hidden | normal-replace,search-landmark,normal-motion | M9.04.P01 | PASS | PASS | PASS | family normal-replace>M0.06, search-landmark>M0.06, normal-motion>M1.06 | — |
| M9.05 | M9/5 | compare_methods/hidden | ex-copy,normal-open-line,normal-motion | M9.05.P01 | PASS | PASS | PASS | family ex-copy>M4.06, normal-open-line>M8.04, normal-motion>M1.06; NOTE omit C | — |
| M9.06 | M9/6 | transfer/hidden | normal-replace,search-landmark | M9.06.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M9.07 | M9/7 | concept/interpretation | paired-animation-neovim-diagnosis | M9.Q03,M9.Q07,M9.Q10,M9.Q08,M9.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M9.08 | M9/8 | module_check/hidden | ex-copy,normal-replace,search-landmark,normal-motion | M9.Q01,M9.Q02,M9.Q03,M9.Q04,M9.Q05,M9.Q06,M9.Q07,M9.Q08,M9.Q09,M9.Q10 | PASS | PASS | PASS | family ex-copy>M4.06, normal-replace>M0.06, search-landmark>M0.06, normal-motion>M1.06 | — |
| M10.01 | M10/1 | guided_edit/guided | normal-replace,normal-motion | M10.01.P01 | PASS | PASS | PASS | family normal-replace>M0.06, normal-motion>M1.06 | — |
| M10.02 | M10/2 | guided_edit/guided | linewise-yank-put,normal-motion | M10.02.P01 | PASS | PASS | PASS | family linewise-yank-put>M12.04, normal-motion>M1.06; NOTE omit C | — |
| M10.03 | M10/3 | concept/interpretation | paired-animation-neovim-diagnosis | M10.Q01,M10.Q02,M10.Q03,M10.Q06,M10.Q07 | N/A | PASS | PASS | concept/check bank | — |
| M10.04 | M10/4 | independent_edit/hidden | normal-open-line,normal-motion | M10.04.P01 | PASS | PASS | PASS | family normal-open-line>M8.04, normal-motion>M1.06 | — |
| M10.05 | M10/5 | compare_methods/hidden | ex-copy,linewise-yank-put,normal-motion | M10.05.P01 | PASS | PASS | PASS | family ex-copy>M4.06, linewise-yank-put>M12.04, normal-motion>M1.06 | — |
| M10.06 | M10/6 | transfer/hidden | normal-replace,normal-motion | M10.06.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M10.07 | M10/7 | concept/interpretation | paired-animation-neovim-diagnosis | M10.Q03,M10.Q07,M10.Q10,M10.Q08,M10.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M10.08 | M10/8 | module_check/hidden | ex-copy | M10.Q01,M10.Q02,M10.Q03,M10.Q04,M10.Q05,M10.Q06,M10.Q07,M10.Q08,M10.Q09,M10.Q10 | PASS | PASS | PASS | family ex-copy>M4.06 | — |
| M11.01 | M11/1 | guided_edit/guided | replace-mode,normal-motion | M11.01.P01 | GUIDED | PASS | PASS | family replace-mode>M11.04, normal-motion>M1.06 | — |
| M11.02 | M11/2 | guided_edit/guided | linewise-yank-put,normal-motion | M11.02.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M11.03 | M11/3 | concept/interpretation | paired-animation-neovim-diagnosis | M11.Q01,M11.Q04,M11.Q03,M11.Q06,M11.Q08 | N/A | PASS | PASS | concept/check bank | M11.Q04,M11.Q08 |
| M11.UR | M11/3.5 | guided_edit/guided | undo-redo | M11.UR.P01 | GUIDED | PASS | PASS | direct changed-art x2 | — |
| M11.04 | M11/4 | independent_edit/hidden | register,undo-redo,replace-mode,normal-motion | M11.04.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M11.05 | M11/5 | compare_methods/hidden | ex-substitute-line,normal-replace,search-landmark,normal-motion | M11.05.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M11.06 | M11/6 | transfer/hidden | replace-mode,normal-motion | M11.06.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M11.07 | M11/7 | concept/interpretation | paired-animation-neovim-diagnosis | M11.Q03,M11.Q07,M11.Q10,M11.Q08,M11.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M11.VE | M11/7.5 | guided_edit/guided | virtual-column | M11.VE.P01 | GUIDED | PASS | PASS | direct changed-art x2 | — |
| M11.08 | M11/8 | module_check/hidden | repeat,virtual-column,normal-motion | M11.Q01,M11.Q02,M11.Q03,M11.Q04,M11.Q05,M11.Q06,M11.Q07,M11.Q08,M11.Q09,M11.Q10 | PASS | PASS | PASS | direct changed-art x2 | — |
| M12.01 | M12/1 | guided_edit/guided | normal-replace,search-landmark,normal-motion | M12.01.P01 | PASS | PASS | PASS | family normal-replace>M0.06, search-landmark>M0.06, normal-motion>M1.06 | — |
| M12.02 | M12/2 | guided_edit/guided | linewise-yank-put,normal-replace,search-landmark,normal-motion | M12.02.P01 | PASS | PASS | PASS | family linewise-yank-put>M12.04, normal-replace>M0.06, search-landmark>M0.06, normal-motion>M1.06 | — |
| M12.03 | M12/3 | concept/interpretation | paired-animation-neovim-diagnosis | M12.Q01,M12.Q04,M12.Q03,M12.Q06,M12.Q08 | N/A | PASS | PASS | concept/check bank | M12.Q04 |
| M12.FIND | M12/3.5 | guided_edit/guided | char-find-repeat | M12.FIND.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M12.04 | M12/4 | independent_edit/hidden | linewise-yank-put,normal-replace,char-find-repeat,search-landmark,normal-motion | M12.04.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M12.05 | M12/5 | compare_methods/hidden | ex-substitute-line,ex-copy,normal-replace,char-find-repeat,search-landmark,normal-motion | M12.05.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M12.06 | M12/6 | transfer/hidden | normal-replace,search-landmark,normal-motion | M12.06.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M12.07 | M12/7 | concept/interpretation | paired-animation-neovim-diagnosis | M12.Q03,M12.Q07,M12.Q10,M12.Q08,M12.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M12.08 | M12/8 | module_check/hidden | ex-copy,normal-replace,search-landmark,normal-motion | M12.Q01,M12.Q02,M12.Q03,M12.Q04,M12.Q05,M12.Q06,M12.Q07,M12.Q08,M12.Q09,M12.Q10 | PASS | PASS | PASS | family ex-copy>M4.06, normal-replace>M0.06, search-landmark>M0.06, normal-motion>M1.06 | — |
| M13.01 | M13/1 | guided_edit/guided | normal-replace,word-boundary,normal-motion | M13.01.P01 | GUIDED | PASS | PASS | family normal-replace>M0.06, word-boundary>M13.04, normal-motion>M1.06 | — |
| M13.02 | M13/2 | guided_edit/guided | linewise-yank-put,normal-replace,word-boundary,normal-motion | M13.02.P01 | PASS | PASS | PASS | family linewise-yank-put>M12.04, normal-replace>M0.06, word-boundary>M13.04, normal-motion>M1.06 | — |
| M13.03 | M13/3 | concept/interpretation | paired-animation-neovim-diagnosis | M13.Q01,M13.Q04,M13.Q03,M13.Q06,M13.Q08 | N/A | PASS | PASS | concept/check bank | M13.Q04,M13.Q06 |
| M13.BE | M13/3.5 | guided_edit/guided | word-boundary | M13.BE.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M13.04 | M13/4 | independent_edit/hidden | linewise-yank-put,normal-replace,word-boundary,normal-motion | M13.04.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M13.05 | M13/5 | compare_methods/hidden | ex-substitute-line,ex-copy,normal-replace,char-find-repeat,search-landmark,normal-motion | M13.05.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M13.06 | M13/6 | transfer/hidden | normal-replace,word-boundary,normal-motion | M13.06.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M13.07 | M13/7 | concept/interpretation | paired-animation-neovim-diagnosis | M13.Q03,M13.Q07,M13.Q10,M13.Q08,M13.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M13.08 | M13/8 | module_check/hidden | ex-copy,normal-replace,word-boundary,normal-motion | M13.Q01,M13.Q02,M13.Q03,M13.Q04,M13.Q05,M13.Q06,M13.Q07,M13.Q08,M13.Q09,M13.Q10 | PASS | PASS | PASS | family ex-copy>M4.06, normal-replace>M0.06, word-boundary>M13.04, normal-motion>M1.06 | — |
| M14.01 | M14/1 | guided_edit/guided | register,replace-mode,search-landmark,normal-motion | M14.01.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M14.02 | M14/2 | guided_edit/guided | linewise-yank-put,normal-motion | M14.02.P01 | PASS | PASS | PASS | family linewise-yank-put>M12.04, normal-motion>M1.06 | — |
| M14.03 | M14/3 | concept/interpretation | paired-animation-neovim-diagnosis | M14.Q01,M14.Q04,M14.Q03,M14.Q06,M14.Q08 | N/A | PASS | PASS | concept/check bank | M14.Q08 |
| M14.04 | M14/4 | independent_edit/hidden | register,replace-mode,search-landmark,normal-motion | M14.04.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M14.PARA | M14/4.5 | guided_edit/guided | paragraph-next,put-before | M14.PARA.P01 | GUIDED | PASS | PASS | direct changed-art x2 | — |
| M14.05 | M14/5 | compare_methods/hidden | ex-copy,linewise-yank-put,put-before,paragraph-next,normal-motion | M14.05.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M14.06 | M14/6 | transfer/hidden | register,replace-mode,search-landmark,normal-motion | M14.06.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M14.07 | M14/7 | concept/interpretation | paired-animation-neovim-diagnosis | M14.Q03,M14.Q07,M14.Q10,M14.Q08,M14.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M14.08 | M14/8 | module_check/hidden | register,replace-mode,search-landmark,paragraph-next,normal-motion | M14.Q01,M14.Q02,M14.Q03,M14.Q04,M14.Q05,M14.Q06,M14.Q07,M14.Q08,M14.Q09,M14.Q10 | PASS | PASS | PASS | direct changed-art x2 | — |
| M15.01 | M15/1 | guided_edit/guided | ex-command | M15.01.P01 | GUIDED | PASS | PASS | direct changed-art x2 | — |
| M15.02 | M15/2 | guided_edit/guided | linewise-yank-put,normal-motion | M15.02.P01 | PASS | PASS | PASS | family linewise-yank-put>M12.04, normal-motion>M1.06 | — |
| M15.03 | M15/3 | concept/interpretation | paired-animation-neovim-diagnosis | M15.Q01,M15.Q04,M15.Q03,M15.Q06,M15.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M15.04 | M15/4 | independent_edit/hidden | ex-substitute-range,normal-motion | M15.04.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M15.BA | M15/4.5 | guided_edit/guided | block-append | M15.BA.P01 | GUIDED | PASS | PASS | direct changed-art x2 | — |
| M15.05 | M15/5 | compare_methods/hidden | ex-substitute-range,visual-scope,block-append,normal-motion | M15.05.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M15.06 | M15/6 | transfer/hidden | ex-command | M15.06.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M15.07 | M15/7 | concept/interpretation | paired-animation-neovim-diagnosis | M15.Q03,M15.Q07,M15.Q10,M15.Q08,M15.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M15.08 | M15/8 | module_check/hidden | ex-copy,normal-replace,macro,search-landmark,normal-motion | M15.Q01,M15.Q02,M15.Q03,M15.Q04,M15.Q05,M15.Q06,M15.Q07,M15.Q08,M15.Q09,M15.Q10 | PASS | PASS | PASS | direct changed-art x2 | — |
| M16.01 | M16/1 | guided_edit/guided | search-landmark,normal-motion | M16.01.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M16.02 | M16/2 | guided_edit/guided | search-landmark,ex-command,normal-motion | M16.02.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M16.03 | M16/3 | concept/interpretation | paired-animation-neovim-diagnosis | M16.Q01,M16.Q02,M16.Q03,M16.Q06,M16.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M16.04 | M16/4 | independent_edit/hidden | ex-copy,search-landmark,normal-motion | M16.04.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M16.05 | M16/5 | compare_methods/hidden | ex-move,put-before,normal-motion | M16.05.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M16.06 | M16/6 | transfer/hidden | search-landmark,normal-motion | M16.06.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M16.07 | M16/7 | concept/interpretation | paired-animation-neovim-diagnosis | M16.Q03,M16.Q07,M16.Q10,M16.Q08,M16.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M16.08 | M16/8 | module_check/hidden | ex-copy,search-landmark,normal-motion | M16.Q01,M16.Q02,M16.Q03,M16.Q04,M16.Q05,M16.Q06,M16.Q07,M16.Q08,M16.Q09,M16.Q10 | PASS | PASS | PASS | direct changed-art x2 | — |
| M17.01 | M17/1 | guided_edit/guided | normal-replace,repeat,search-landmark | M17.01.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M17.02 | M17/2 | guided_edit/guided | linewise-yank-put,normal-motion | M17.02.P01 | PASS | PASS | PASS | family linewise-yank-put>M12.04, normal-motion>M1.06 | — |
| M17.03 | M17/3 | concept/interpretation | paired-animation-neovim-diagnosis | M17.Q01,M17.Q04,M17.Q03,M17.Q06,M17.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M17.04 | M17/4 | independent_edit/hidden | normal-replace,search-landmark,normal-motion | M17.04.P01 | PASS | PASS | PASS | family normal-replace>M0.06, search-landmark>M0.06, normal-motion>M1.06 | — |
| M17.05 | M17/5 | compare_methods/hidden | global-normal,normal-replace,repeat,search-landmark,ex-command | M17.05.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M17.06 | M17/6 | transfer/hidden | normal-replace,repeat,search-landmark | M17.06.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M17.07 | M17/7 | concept/interpretation | paired-animation-neovim-diagnosis | M17.Q03,M17.Q07,M17.Q10,M17.Q08,M17.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M17.08 | M17/8 | module_check/hidden | normal-replace,macro,search-landmark | M17.Q01,M17.Q02,M17.Q03,M17.Q04,M17.Q05,M17.Q06,M17.Q07,M17.Q08,M17.Q09,M17.Q10 | PASS | PASS | PASS | direct changed-art x2 | — |
| M18.01 | M18/1 | guided_edit/guided | search-landmark,normal-motion | M18.01.P01 | PASS | PASS | PASS | direct changed-art x2; NOTE omit C | — |
| M18.02 | M18/2 | guided_edit/guided | linewise-yank-put,normal-motion | M18.02.P01 | PASS | PASS | PASS | family linewise-yank-put>M12.04, normal-motion>M1.06 | — |
| M18.03 | M18/3 | concept/interpretation | paired-animation-neovim-diagnosis | M18.Q01,M18.Q04,M18.Q03,M18.Q06,M18.Q08 | N/A | PASS | PASS | concept/check bank | — |
| M18.04 | M18/4 | independent_edit/hidden | search-landmark,normal-motion | M18.04.P01 | PASS | PASS | PASS | direct changed-art x2; NOTE omit C | — |
| M18.EXPR | M18/4.5 | guided_edit/guided | expression-substitute | M18.EXPR.P01 | GUIDED | PASS | PASS | direct changed-art x2 | — |
| M18.05 | M18/5 | compare_methods/hidden | ex-substitute-range,expression-substitute,normal-replace,search-landmark,normal-motion | M18.05.P01 | PASS | PASS | PASS | direct changed-art x2 | — |
| M18.06 | M18/6 | transfer/hidden | search-landmark,normal-motion | M18.06.P01 | PASS | PASS | PASS | direct changed-art x2; NOTE omit C | — |
| M18.07 | M18/7 | concept/interpretation | paired-animation-neovim-diagnosis | M18.Q03,M18.Q07,M18.Q10,M18.Q08,M18.Q09 | N/A | PASS | PASS | concept/check bank | — |
| M18.08 | M18/8 | module_check/hidden | ex-copy | M18.Q01,M18.Q02,M18.Q03,M18.Q04,M18.Q05,M18.Q06,M18.Q07,M18.Q08,M18.Q09,M18.Q10 | PASS | PASS | PASS | direct changed-art x2 | — |

## Complete question matrix (326/326)

Uses lists every live card that can present a stem. FAIL@M*.03 is a real first-use failure even if a later module-check use passes. Prior evidence is exact guided card IDs before first use.

| Question | Uses | Form/contract | G1 | Prior evidence or defect | G2 | G3 |
|---|---|---|---|---|---|---|
| M0.Q01 | M0.03,M0.08 | multiple_choice/a-d paired A/V | PASS | guided before M0.03: M0.01,M0.02,M0.O | PASS | PASS |
| M0.Q02 | M0.03,M0.08 | multiple_choice/a-d paired A/V | PASS | guided before M0.03: M0.01,M0.02,M0.O | PASS | PASS |
| M0.Q03 | M0.07,M0.08 | multiple_choice/a-d paired A/V | PASS | guided before M0.07: M0.01,M0.02,M0.O,M0.T,M0.SL | PASS | PASS |
| M0.Q04 | M0.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M0.Q05 | M0.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M0.Q06 | M0.03,M0.08 | multiple_choice/a-d paired A/V | FAIL@M0.03 | FAIL: Current-line substitute and unfamiliar transfer arrive later. First later teaching: M0.SL / M0.06 | PASS | FAIL@M0.03 |
| M0.Q07 | M0.03,M0.07,M0.08 | multiple_choice/a-d paired A/V | FAIL@M0.03 | FAIL: Ex copy and the settle/check sequence arrive later. First later teaching: M0.T / M0.08 | PASS | FAIL@M0.03 |
| M0.Q08 | M0.07,M0.08 | multiple_choice/a-d paired A/V | PASS | guided before M0.07: M0.01,M0.02,M0.O,M0.T,M0.SL | PASS | PASS |
| M0.Q09 | M0.03,M0.07,M0.08 | multiple_choice/a-d paired A/V | FAIL@M0.03 | FAIL: Addressed copy and final settle command arrive later. First later teaching: M0.T / M0.08 | PASS | FAIL@M0.03 |
| M0.Q10 | M0.07,M0.08 | multiple_choice/a-d paired A/V | PASS | guided before M0.07: M0.01,M0.02,M0.O,M0.T,M0.SL | PASS | PASS |
| M0.P0.P01 | M0.P0 | decode/term groups | PASS | guided before M0.P0:  | PASS | PASS |
| M1.Q01 | M1.03,M1.08 | multiple_choice/a-d paired A/V | PASS | guided before M1.03: M1.01,M1.02 | PASS | PASS |
| M1.Q02 | M1.03,M1.08 | multiple_choice/a-d paired A/V | PASS | guided before M1.03: M1.01,M1.02 | PASS | PASS |
| M1.Q03 | M1.03,M1.07,M1.08 | multiple_choice/a-d paired A/V | FAIL@M1.03 | FAIL: dW/operator-object is not guided before M1.03. First later teaching: M2.01 | PASS | FAIL@M1.03 |
| M1.Q04 | M1.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M1.Q05 | M1.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M1.Q06 | M1.03,M1.08 | multiple_choice/a-d paired A/V | PASS | guided before M1.03: M1.01,M1.02 | PASS | PASS |
| M1.Q07 | M1.07,M1.08 | multiple_choice/a-d paired A/V | PASS | guided before M1.07: M1.01,M1.02,M1.DD | PASS | PASS |
| M1.Q08 | M1.07,M1.08 | multiple_choice/a-d paired A/V | PASS | guided before M1.07: M1.01,M1.02,M1.DD | PASS | PASS |
| M1.Q09 | M1.03,M1.07,M1.08 | multiple_choice/a-d paired A/V | FAIL@M1.03 | FAIL: The % whole-file range is not taught before this stem. First later teaching: M1.05 | PASS | FAIL@M1.03 |
| M1.Q10 | M1.07,M1.08 | multiple_choice/a-d paired A/V | PASS | guided before M1.07: M1.01,M1.02,M1.DD | PASS | PASS |
| M2.Q01 | M2.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M2.Q02 | M2.03,M2.08 | multiple_choice/a-d paired A/V | PASS | guided before M2.03: M2.01,M2.02 | PASS | PASS |
| M2.Q03 | M2.07,M2.08 | multiple_choice/a-d paired A/V | PASS | guided before M2.07: M2.01,M2.02 | PASS | PASS |
| M2.Q04 | M2.03,M2.08 | multiple_choice/a-d paired A/V | PASS | guided before M2.03: M2.01,M2.02 | PASS | PASS |
| M2.Q05 | M2.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M2.Q06 | M2.03,M2.08 | multiple_choice/a-d paired A/V | PASS | guided before M2.03: M2.01,M2.02 | PASS | PASS |
| M2.Q07 | M2.07,M2.08 | multiple_choice/a-d paired A/V | PASS | guided before M2.07: M2.01,M2.02 | PASS | PASS |
| M2.Q08 | M2.07,M2.08 | multiple_choice/a-d paired A/V | PASS | guided before M2.07: M2.01,M2.02 | PASS | PASS |
| M2.Q09 | M2.03,M2.07,M2.08 | multiple_choice/a-d paired A/V | FAIL@M2.03 | FAIL: The [.o] character-class substitute arrives later. First later teaching: M2.05 | PASS | FAIL@M2.03 |
| M2.Q10 | M2.03,M2.07,M2.08 | multiple_choice/a-d paired A/V | PASS | guided before M2.03: M2.01,M2.02 | PASS | PASS |
| M3.Q01 | M3.03,M3.08 | multiple_choice/a-d paired A/V | PASS | guided before M3.03: M3.01,M3.02 | PASS | PASS |
| M3.Q02 | M3.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M3.Q03 | M3.07,M3.08 | multiple_choice/a-d paired A/V | PASS | guided before M3.07: M3.01,M3.02,M3.CI,M3.REG | PASS | PASS |
| M3.Q04 | M3.03,M3.08 | multiple_choice/a-d paired A/V | FAIL@M3.03 | FAIL: ci( is first guided in the later bridge. First later teaching: M3.CI | PASS | FAIL@M3.03 |
| M3.Q05 | M3.03,M3.08 | multiple_choice/a-d paired A/V | PASS | guided before M3.03: M3.01,M3.02 | PASS | PASS |
| M3.Q06 | M3.03,M3.08 | multiple_choice/a-d paired A/V | FAIL@M3.03 | FAIL: Named-register pose storage arrives later. First later teaching: M3.REG | PASS | FAIL@M3.03 |
| M3.Q07 | M3.07,M3.08 | multiple_choice/a-d paired A/V | PASS | guided before M3.07: M3.01,M3.02,M3.CI,M3.REG | PASS | PASS |
| M3.Q08 | M3.07,M3.08 | multiple_choice/a-d paired A/V | PASS | guided before M3.07: M3.01,M3.02,M3.CI,M3.REG | PASS | PASS |
| M3.Q09 | M3.03,M3.07,M3.08 | multiple_choice/a-d paired A/V | FAIL@M3.03 | FAIL: Digraph entry arrives later. First later teaching: M3.DI | PASS | FAIL@M3.03 |
| M3.Q10 | M3.07,M3.08 | multiple_choice/a-d paired A/V | PASS | guided before M3.07: M3.01,M3.02,M3.CI,M3.REG | PASS | PASS |
| M4.Q01 | M4.03,M4.08 | multiple_choice/a-d paired A/V | PASS | guided before M4.03: M4.01,M4.02 | PASS | PASS |
| M4.Q02 | M4.03,M4.08 | multiple_choice/a-d paired A/V | PASS | guided before M4.03: M4.01,M4.02 | PASS | PASS |
| M4.Q03 | M4.03,M4.07,M4.08 | multiple_choice/a-d paired A/V | PASS | guided before M4.03: M4.01,M4.02 | PASS | PASS |
| M4.Q04 | M4.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M4.Q05 | M4.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M4.Q06 | M4.03,M4.08 | multiple_choice/a-d paired A/V | PASS | guided before M4.03: M4.01,M4.02 | PASS | PASS |
| M4.Q07 | M4.07,M4.08 | multiple_choice/a-d paired A/V | PASS | guided before M4.07: M4.01,M4.02,M4.VB | PASS | PASS |
| M4.Q08 | M4.07,M4.08 | multiple_choice/a-d paired A/V | PASS | guided before M4.07: M4.01,M4.02,M4.VB | PASS | PASS |
| M4.Q09 | M4.03,M4.07,M4.08 | multiple_choice/a-d paired A/V | PASS | guided before M4.03: M4.01,M4.02 | PASS | PASS |
| M4.Q10 | M4.07,M4.08 | multiple_choice/a-d paired A/V | PASS | guided before M4.07: M4.01,M4.02,M4.VB | PASS | PASS |
| M5.Q01 | M5.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M5.Q02 | M5.03,M5.08 | multiple_choice/a-d paired A/V | PASS | guided before M5.03: M5.01,M5.02 | PASS | PASS |
| M5.Q03 | M5.03,M5.07,M5.08 | multiple_choice/a-d paired A/V | PASS | guided before M5.03: M5.01,M5.02 | PASS | PASS |
| M5.Q04 | M5.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M5.Q05 | M5.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M5.Q06 | M5.03,M5.08 | multiple_choice/a-d paired A/V | PASS | guided before M5.03: M5.01,M5.02 | PASS | PASS |
| M5.Q07 | M5.07,M5.08 | multiple_choice/a-d paired A/V | PASS | guided before M5.07: M5.01,M5.02 | PASS | PASS |
| M5.Q08 | M5.07,M5.08 | multiple_choice/a-d paired A/V | PASS | guided before M5.07: M5.01,M5.02 | PASS | PASS |
| M5.Q09 | M5.03,M5.07,M5.08 | multiple_choice/a-d paired A/V | PASS | guided before M5.03: M5.01,M5.02 | PASS | PASS |
| M5.Q10 | M5.03,M5.07,M5.08 | multiple_choice/a-d paired A/V | PASS | guided before M5.03: M5.01,M5.02 | PASS | PASS |
| M6.Q01 | M6.03,M6.08 | multiple_choice/a-d paired A/V | PASS | guided before M6.03: M6.01,M6.02 | PASS | PASS |
| M6.Q02 | M6.03,M6.08 | multiple_choice/a-d paired A/V | PASS | guided before M6.03: M6.01,M6.02 | PASS | PASS |
| M6.Q03 | M6.03,M6.07,M6.08 | multiple_choice/a-d paired A/V | FAIL@M6.03 | FAIL: D/content-clear arrives later. First later teaching: M6.D | PASS | FAIL@M6.03 |
| M6.Q04 | M6.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M6.Q05 | M6.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M6.Q06 | M6.03,M6.08 | multiple_choice/a-d paired A/V | FAIL@M6.03 | FAIL: Ex move arrives later. First later teaching: M6.MOVE | PASS | FAIL@M6.03 |
| M6.Q07 | M6.07,M6.08 | multiple_choice/a-d paired A/V | PASS | guided before M6.07: M6.01,M6.02,M6.D,M6.MOVE | PASS | PASS |
| M6.Q08 | M6.07,M6.08 | multiple_choice/a-d paired A/V | PASS | guided before M6.07: M6.01,M6.02,M6.D,M6.MOVE | PASS | PASS |
| M6.Q09 | M6.03,M6.07,M6.08 | multiple_choice/a-d paired A/V | FAIL@M6.03 | FAIL: D/content-clear arrives later. First later teaching: M6.D | PASS | FAIL@M6.03 |
| M6.Q10 | M6.07,M6.08 | multiple_choice/a-d paired A/V | PASS | guided before M6.07: M6.01,M6.02,M6.D,M6.MOVE | PASS | PASS |
| M7.Q01 | M7.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M7.Q02 | M7.03,M7.08 | multiple_choice/a-d paired A/V | PASS | guided before M7.03: M7.01,M7.02 | PASS | PASS |
| M7.Q03 | M7.03,M7.07,M7.08 | multiple_choice/a-d paired A/V | FAIL@M7.03 | FAIL: Dot-repeat arrives later. First later teaching: M7.DOT | PASS | FAIL@M7.03 |
| M7.Q04 | M7.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M7.Q05 | M7.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M7.Q06 | M7.03,M7.08 | multiple_choice/a-d paired A/V | FAIL@M7.03 | FAIL: Dot-repeat arrives later. First later teaching: M7.DOT | PASS | FAIL@M7.03 |
| M7.Q07 | M7.03,M7.07,M7.08 | multiple_choice/a-d paired A/V | PASS | guided before M7.03: M7.01,M7.02 | PASS | PASS |
| M7.Q08 | M7.07,M7.08 | multiple_choice/a-d paired A/V | PASS | guided before M7.07: M7.01,M7.02,M7.DOT,M7.MAC,M7.VIS,M7.GLOBAL | PASS | PASS |
| M7.Q09 | M7.03,M7.07,M7.08 | multiple_choice/a-d paired A/V | FAIL@M7.03 | FAIL: Global-normal arrives later. First later teaching: M7.GLOBAL | PASS | FAIL@M7.03 |
| M7.Q10 | M7.07,M7.08 | multiple_choice/a-d paired A/V | PASS | guided before M7.07: M7.01,M7.02,M7.DOT,M7.MAC,M7.VIS,M7.GLOBAL | PASS | PASS |
| M8.Q01 | M8.03,M8.08 | multiple_choice/a-d paired A/V | PASS | guided before M8.03: M8.01,M8.02 | PASS | PASS |
| M8.Q02 | M8.03,M8.08 | multiple_choice/a-d paired A/V | PASS | guided before M8.03: M8.01,M8.02 | PASS | PASS |
| M8.Q03 | M8.03,M8.07,M8.08 | multiple_choice/a-d paired A/V | PASS | guided before M8.03: M8.01,M8.02 | PASS | PASS |
| M8.Q04 | M8.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M8.Q05 | M8.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M8.Q06 | M8.03,M8.08 | multiple_choice/a-d paired A/V | PASS | guided before M8.03: M8.01,M8.02 | PASS | PASS |
| M8.Q07 | M8.07,M8.08 | multiple_choice/a-d paired A/V | PASS | guided before M8.07: M8.01,M8.02 | PASS | PASS |
| M8.Q08 | M8.07,M8.08 | multiple_choice/a-d paired A/V | PASS | guided before M8.07: M8.01,M8.02 | PASS | PASS |
| M8.Q09 | M8.03,M8.07,M8.08 | multiple_choice/a-d paired A/V | PASS | guided before M8.03: M8.01,M8.02 | PASS | PASS |
| M8.Q10 | M8.07,M8.08 | multiple_choice/a-d paired A/V | PASS | guided before M8.07: M8.01,M8.02 | PASS | PASS |
| M9.Q01 | M9.03,M9.08 | multiple_choice/a-d paired A/V | PASS | guided before M9.03: M9.01,M9.02 | PASS | PASS |
| M9.Q02 | M9.03,M9.08 | multiple_choice/a-d paired A/V | PASS | guided before M9.03: M9.01,M9.02 | PASS | PASS |
| M9.Q03 | M9.07,M9.08 | multiple_choice/a-d paired A/V | PASS | guided before M9.07: M9.01,M9.02 | PASS | PASS |
| M9.Q04 | M9.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M9.Q05 | M9.03,M9.08 | multiple_choice/a-d paired A/V | PASS | guided before M9.03: M9.01,M9.02 | PASS | PASS |
| M9.Q06 | M9.03,M9.08 | multiple_choice/a-d paired A/V | PASS | guided before M9.03: M9.01,M9.02 | PASS | PASS |
| M9.Q07 | M9.07,M9.08 | multiple_choice/a-d paired A/V | PASS | guided before M9.07: M9.01,M9.02 | PASS | PASS |
| M9.Q08 | M9.07,M9.08 | multiple_choice/a-d paired A/V | PASS | guided before M9.07: M9.01,M9.02 | PASS | PASS |
| M9.Q09 | M9.03,M9.07,M9.08 | multiple_choice/a-d paired A/V | PASS | guided before M9.03: M9.01,M9.02 | PASS | PASS |
| M9.Q10 | M9.07,M9.08 | multiple_choice/a-d paired A/V | PASS | guided before M9.07: M9.01,M9.02 | PASS | PASS |
| M10.Q01 | M10.03,M10.08 | multiple_choice/a-d paired A/V | PASS | guided before M10.03: M10.01,M10.02 | PASS | PASS |
| M10.Q02 | M10.03,M10.08 | multiple_choice/a-d paired A/V | PASS | guided before M10.03: M10.01,M10.02 | PASS | PASS |
| M10.Q03 | M10.03,M10.07,M10.08 | multiple_choice/a-d paired A/V | PASS | guided before M10.03: M10.01,M10.02 | PASS | PASS |
| M10.Q04 | M10.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M10.Q05 | M10.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M10.Q06 | M10.03,M10.08 | multiple_choice/a-d paired A/V | PASS | guided before M10.03: M10.01,M10.02 | PASS | PASS |
| M10.Q07 | M10.03,M10.07,M10.08 | multiple_choice/a-d paired A/V | PASS | guided before M10.03: M10.01,M10.02 | PASS | PASS |
| M10.Q08 | M10.07,M10.08 | multiple_choice/a-d paired A/V | PASS | guided before M10.07: M10.01,M10.02 | PASS | PASS |
| M10.Q09 | M10.07,M10.08 | multiple_choice/a-d paired A/V | PASS | guided before M10.07: M10.01,M10.02 | PASS | PASS |
| M10.Q10 | M10.07,M10.08 | multiple_choice/a-d paired A/V | PASS | guided before M10.07: M10.01,M10.02 | PASS | PASS |
| M11.Q01 | M11.03,M11.08 | multiple_choice/a-d paired A/V | PASS | guided before M11.03: M11.01,M11.02 | PASS | PASS |
| M11.Q02 | M11.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M11.Q03 | M11.03,M11.07,M11.08 | multiple_choice/a-d paired A/V | PASS | guided before M11.03: M11.01,M11.02 | PASS | PASS |
| M11.Q04 | M11.03,M11.08 | multiple_choice/a-d paired A/V | FAIL@M11.03 | FAIL: Undo/redo arrives later. First later teaching: M11.UR | PASS | FAIL@M11.03 |
| M11.Q05 | M11.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M11.Q06 | M11.03,M11.08 | multiple_choice/a-d paired A/V | PASS | guided before M11.03: M11.01,M11.02 | PASS | PASS |
| M11.Q07 | M11.07,M11.08 | multiple_choice/a-d paired A/V | PASS | guided before M11.07: M11.01,M11.02,M11.UR | PASS | PASS |
| M11.Q08 | M11.03,M11.07,M11.08 | multiple_choice/a-d paired A/V | FAIL@M11.03 | FAIL: Virtual-column editing arrives later. First later teaching: M11.VE | PASS | FAIL@M11.03 |
| M11.Q09 | M11.07,M11.08 | multiple_choice/a-d paired A/V | PASS | guided before M11.07: M11.01,M11.02,M11.UR | PASS | PASS |
| M11.Q10 | M11.07,M11.08 | multiple_choice/a-d paired A/V | PASS | guided before M11.07: M11.01,M11.02,M11.UR | PASS | PASS |
| M12.Q01 | M12.03,M12.08 | multiple_choice/a-d paired A/V | PASS | guided before M12.03: M12.01,M12.02 | PASS | PASS |
| M12.Q02 | M12.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M12.Q03 | M12.03,M12.07,M12.08 | multiple_choice/a-d paired A/V | PASS | guided before M12.03: M12.01,M12.02 | PASS | PASS |
| M12.Q04 | M12.03,M12.08 | multiple_choice/a-d paired A/V | FAIL@M12.03 | FAIL: ;/, character-find repeat arrives later. First later teaching: M12.FIND | PASS | FAIL@M12.03 |
| M12.Q05 | M12.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M12.Q06 | M12.03,M12.08 | multiple_choice/a-d paired A/V | PASS | guided before M12.03: M12.01,M12.02 | PASS | PASS |
| M12.Q07 | M12.07,M12.08 | multiple_choice/a-d paired A/V | PASS | guided before M12.07: M12.01,M12.02,M12.FIND | PASS | PASS |
| M12.Q08 | M12.03,M12.07,M12.08 | multiple_choice/a-d paired A/V | PASS | guided before M12.03: M12.01,M12.02 | PASS | PASS |
| M12.Q09 | M12.07,M12.08 | multiple_choice/a-d paired A/V | PASS | guided before M12.07: M12.01,M12.02,M12.FIND | PASS | PASS |
| M12.Q10 | M12.07,M12.08 | multiple_choice/a-d paired A/V | PASS | guided before M12.07: M12.01,M12.02,M12.FIND | PASS | PASS |
| M13.Q01 | M13.03,M13.08 | multiple_choice/a-d paired A/V | PASS | guided before M13.03: M13.01,M13.02 | PASS | PASS |
| M13.Q02 | M13.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M13.Q03 | M13.03,M13.07,M13.08 | multiple_choice/a-d paired A/V | PASS | guided before M13.03: M13.01,M13.02 | PASS | PASS |
| M13.Q04 | M13.03,M13.08 | multiple_choice/a-d paired A/V | FAIL@M13.03 | FAIL: E/count-W/B WORD work arrives later. First later teaching: M13.BE | PASS | FAIL@M13.03 |
| M13.Q05 | M13.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M13.Q06 | M13.03,M13.08 | multiple_choice/a-d paired A/V | FAIL@M13.03 | FAIL: Counted W/B transfer arrives later. First later teaching: M13.BE | PASS | FAIL@M13.03 |
| M13.Q07 | M13.07,M13.08 | multiple_choice/a-d paired A/V | PASS | guided before M13.07: M13.01,M13.02,M13.BE | PASS | PASS |
| M13.Q08 | M13.03,M13.07,M13.08 | multiple_choice/a-d paired A/V | PASS | guided before M13.03: M13.01,M13.02 | PASS | PASS |
| M13.Q09 | M13.07,M13.08 | multiple_choice/a-d paired A/V | PASS | guided before M13.07: M13.01,M13.02,M13.BE | PASS | PASS |
| M13.Q10 | M13.07,M13.08 | multiple_choice/a-d paired A/V | PASS | guided before M13.07: M13.01,M13.02,M13.BE | PASS | PASS |
| M14.Q01 | M14.03,M14.08 | multiple_choice/a-d paired A/V | PASS | guided before M14.03: M14.01,M14.02 | PASS | PASS |
| M14.Q02 | M14.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M14.Q03 | M14.03,M14.07,M14.08 | multiple_choice/a-d paired A/V | PASS | guided before M14.03: M14.01,M14.02 | PASS | PASS |
| M14.Q04 | M14.03,M14.08 | multiple_choice/a-d paired A/V | PASS | guided before M14.03: M14.01,M14.02 | PASS | PASS |
| M14.Q05 | M14.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M14.Q06 | M14.03,M14.08 | multiple_choice/a-d paired A/V | PASS | guided before M14.03: M14.01,M14.02 | PASS | PASS |
| M14.Q07 | M14.07,M14.08 | multiple_choice/a-d paired A/V | PASS | guided before M14.07: M14.01,M14.02,M14.PARA | PASS | PASS |
| M14.Q08 | M14.03,M14.07,M14.08 | multiple_choice/a-d paired A/V | FAIL@M14.03 | FAIL: Paragraph-object/frame-boundary navigation arrives later. First later teaching: M14.PARA | PASS | FAIL@M14.03 |
| M14.Q09 | M14.07,M14.08 | multiple_choice/a-d paired A/V | PASS | guided before M14.07: M14.01,M14.02,M14.PARA | PASS | PASS |
| M14.Q10 | M14.07,M14.08 | multiple_choice/a-d paired A/V | PASS | guided before M14.07: M14.01,M14.02,M14.PARA | PASS | PASS |
| M15.Q01 | M15.03,M15.08 | multiple_choice/a-d paired A/V | PASS | guided before M15.03: M15.01,M15.02 | PASS | PASS |
| M15.Q02 | M15.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M15.Q03 | M15.03,M15.07,M15.08 | multiple_choice/a-d paired A/V | PASS | guided before M15.03: M15.01,M15.02 | PASS | PASS |
| M15.Q04 | M15.03,M15.08 | multiple_choice/a-d paired A/V | PASS | guided before M15.03: M15.01,M15.02 | PASS | PASS |
| M15.Q05 | M15.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M15.Q06 | M15.03,M15.08 | multiple_choice/a-d paired A/V | PASS | guided before M15.03: M15.01,M15.02 | PASS | PASS |
| M15.Q07 | M15.07,M15.08 | multiple_choice/a-d paired A/V | PASS | guided before M15.07: M15.01,M15.02,M15.BA | PASS | PASS |
| M15.Q08 | M15.07,M15.08 | multiple_choice/a-d paired A/V | PASS | guided before M15.07: M15.01,M15.02,M15.BA | PASS | PASS |
| M15.Q09 | M15.03,M15.07,M15.08 | multiple_choice/a-d paired A/V | PASS | guided before M15.03: M15.01,M15.02 | PASS | PASS |
| M15.Q10 | M15.07,M15.08 | multiple_choice/a-d paired A/V | PASS | guided before M15.07: M15.01,M15.02,M15.BA | PASS | PASS |
| M16.Q01 | M16.03,M16.08 | multiple_choice/a-d paired A/V | PASS | guided before M16.03: M16.01,M16.02 | PASS | PASS |
| M16.Q02 | M16.03,M16.08 | multiple_choice/a-d paired A/V | PASS | guided before M16.03: M16.01,M16.02 | PASS | PASS |
| M16.Q03 | M16.03,M16.07,M16.08 | multiple_choice/a-d paired A/V | PASS | guided before M16.03: M16.01,M16.02 | PASS | PASS |
| M16.Q04 | M16.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M16.Q05 | M16.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M16.Q06 | M16.03,M16.08 | multiple_choice/a-d paired A/V | PASS | guided before M16.03: M16.01,M16.02 | PASS | PASS |
| M16.Q07 | M16.07,M16.08 | multiple_choice/a-d paired A/V | PASS | guided before M16.07: M16.01,M16.02 | PASS | PASS |
| M16.Q08 | M16.07,M16.08 | multiple_choice/a-d paired A/V | PASS | guided before M16.07: M16.01,M16.02 | PASS | PASS |
| M16.Q09 | M16.03,M16.07,M16.08 | multiple_choice/a-d paired A/V | PASS | guided before M16.03: M16.01,M16.02 | PASS | PASS |
| M16.Q10 | M16.07,M16.08 | multiple_choice/a-d paired A/V | PASS | guided before M16.07: M16.01,M16.02 | PASS | PASS |
| M17.Q01 | M17.03,M17.08 | multiple_choice/a-d paired A/V | PASS | guided before M17.03: M17.01,M17.02 | PASS | PASS |
| M17.Q02 | M17.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M17.Q03 | M17.03,M17.07,M17.08 | multiple_choice/a-d paired A/V | PASS | guided before M17.03: M17.01,M17.02 | PASS | PASS |
| M17.Q04 | M17.03,M17.08 | multiple_choice/a-d paired A/V | PASS | guided before M17.03: M17.01,M17.02 | PASS | PASS |
| M17.Q05 | M17.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M17.Q06 | M17.03,M17.08 | multiple_choice/a-d paired A/V | PASS | guided before M17.03: M17.01,M17.02 | PASS | PASS |
| M17.Q07 | M17.07,M17.08 | multiple_choice/a-d paired A/V | PASS | guided before M17.07: M17.01,M17.02 | PASS | PASS |
| M17.Q08 | M17.07,M17.08 | multiple_choice/a-d paired A/V | PASS | guided before M17.07: M17.01,M17.02 | PASS | PASS |
| M17.Q09 | M17.03,M17.07,M17.08 | multiple_choice/a-d paired A/V | PASS | guided before M17.03: M17.01,M17.02 | PASS | PASS |
| M17.Q10 | M17.07,M17.08 | multiple_choice/a-d paired A/V | PASS | guided before M17.07: M17.01,M17.02 | PASS | PASS |
| M18.Q01 | M18.03,M18.08 | multiple_choice/a-d paired A/V | PASS | guided before M18.03: M18.01,M18.02 | PASS | PASS |
| M18.Q02 | M18.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M18.Q03 | M18.03,M18.07,M18.08 | multiple_choice/a-d paired A/V | PASS | guided before M18.03: M18.01,M18.02 | PASS | PASS |
| M18.Q04 | M18.03,M18.08 | multiple_choice/a-d paired A/V | PASS | guided before M18.03: M18.01,M18.02 | PASS | PASS |
| M18.Q05 | M18.08 | multiple_choice/a-d paired A/V | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M18.Q06 | M18.03,M18.08 | multiple_choice/a-d paired A/V | PASS | guided before M18.03: M18.01,M18.02 | PASS | PASS |
| M18.Q07 | M18.07,M18.08 | multiple_choice/a-d paired A/V | PASS | guided before M18.07: M18.01,M18.02,M18.EXPR | PASS | PASS |
| M18.Q08 | M18.03,M18.07,M18.08 | multiple_choice/a-d paired A/V | PASS | guided before M18.03: M18.01,M18.02 | PASS | PASS |
| M18.Q09 | M18.07,M18.08 | multiple_choice/a-d paired A/V | PASS | guided before M18.07: M18.01,M18.02,M18.EXPR | PASS | PASS |
| M18.Q10 | M18.07,M18.08 | multiple_choice/a-d paired A/V | PASS | guided before M18.07: M18.01,M18.02,M18.EXPR | PASS | PASS |
| M0.01.P01 | M0.01 | typed_keys/effect-exact keys | PASS | guided before M0.01:  | PASS | PASS |
| M0.02.P01 | M0.02 | decode/term groups | PASS | guided before M0.02: M0.01 | FAIL:UNDER-CONTRACT | PASS |
| M0.O.P01 | M0.O | typed_keys/effect-exact keys | PASS | guided before M0.O: M0.01,M0.02 | PASS | PASS |
| M0.04.P01 | M0.04 | predict_art/a-d target/scope | PASS | guided before M0.04: M0.01,M0.02,M0.O | PASS | PASS |
| M0.T.P01 | M0.T | decode/term groups | PASS | guided before M0.T: M0.01,M0.02,M0.O | PASS | PASS |
| M0.05.P01 | M0.05 | why/two term groups | PASS | guided before M0.05: M0.01,M0.02,M0.O,M0.T | WARN:WHY-CONTRACT | PASS |
| M0.SL.P01 | M0.SL | decode/term groups | PASS | guided before M0.SL: M0.01,M0.02,M0.O,M0.T | PASS | PASS |
| M0.06.P01 | M0.06 | typed_keys/effect-exact keys | PASS | guided before M0.06: M0.01,M0.02,M0.O,M0.T,M0.SL | PASS | PASS |
| M0.08.P01 | M0.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M1.01.P01 | M1.01 | typed_keys/effect-exact keys | PASS | guided before M1.01:  | PASS | PASS |
| M1.02.P01 | M1.02 | decode/term groups | PASS | guided before M1.02: M1.01 | PASS | PASS |
| M1.DD.P01 | M1.DD | decode/term groups | PASS | guided before M1.DD: M1.01,M1.02 | PASS | PASS |
| M1.04.P01 | M1.04 | predict_art/a-d target/scope | PASS | guided before M1.04: M1.01,M1.02,M1.DD | PASS | PASS |
| M1.05.P01 | M1.05 | why/two term groups | PASS | guided before M1.05: M1.01,M1.02,M1.DD | WARN:WHY-CONTRACT | PASS |
| M1.06.P01 | M1.06 | typed_keys/effect-exact keys | PASS | guided before M1.06: M1.01,M1.02,M1.DD | PASS | PASS |
| M1.08.P01 | M1.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M2.01.P01 | M2.01 | typed_keys/effect-exact keys | PASS | guided before M2.01:  | PASS | PASS |
| M2.02.P01 | M2.02 | decode/term groups | PASS | guided before M2.02: M2.01 | PASS | PASS |
| M2.04.P01 | M2.04 | predict_art/a-d target/scope | PASS | guided before M2.04: M2.01,M2.02 | PASS | PASS |
| M2.05.P01 | M2.05 | why/two term groups | PASS | guided before M2.05: M2.01,M2.02 | WARN:WHY-CONTRACT | PASS |
| M2.06.P01 | M2.06 | typed_keys/effect-exact keys | PASS | guided before M2.06: M2.01,M2.02 | PASS | PASS |
| M2.08.P01 | M2.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M3.01.P01 | M3.01 | typed_keys/effect-exact keys | PASS | guided before M3.01:  | PASS | PASS |
| M3.02.P01 | M3.02 | decode/term groups | PASS | guided before M3.02: M3.01 | PASS | PASS |
| M3.CI.P01 | M3.CI | decode/term groups | PASS | guided before M3.CI: M3.01,M3.02 | PASS | PASS |
| M3.04.P01 | M3.04 | predict_art/a-d target/scope | PASS | guided before M3.04: M3.01,M3.02,M3.CI | PASS | PASS |
| M3.05.P01 | M3.05 | why/two term groups | PASS | guided before M3.05: M3.01,M3.02,M3.CI | WARN:WHY-CONTRACT | PASS |
| M3.REG.P01 | M3.REG | decode/term groups | PASS | guided before M3.REG: M3.01,M3.02,M3.CI | FAIL:UNDER-CONTRACT | PASS |
| M3.06.P01 | M3.06 | typed_keys/effect-exact keys | PASS | guided before M3.06: M3.01,M3.02,M3.CI,M3.REG | PASS | PASS |
| M3.DI.P01 | M3.DI | decode/term groups | PASS | guided before M3.DI: M3.01,M3.02,M3.CI,M3.REG | PASS | PASS |
| M3.08.P01 | M3.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M4.01.P01 | M4.01 | typed_keys/effect-exact keys | PASS | guided before M4.01:  | PASS | PASS |
| M4.02.P01 | M4.02 | decode/term groups | PASS | guided before M4.02: M4.01 | PASS | PASS |
| M4.VB.P01 | M4.VB | decode/term groups | PASS | guided before M4.VB: M4.01,M4.02 | PASS | PASS |
| M4.04.P01 | M4.04 | predict_art/a-d target/scope | PASS | guided before M4.04: M4.01,M4.02,M4.VB | PASS | PASS |
| M4.05.P01 | M4.05 | why/two term groups | PASS | guided before M4.05: M4.01,M4.02,M4.VB | WARN:WHY-CONTRACT | PASS |
| M4.06.P01 | M4.06 | typed_keys/effect-exact keys | PASS | guided before M4.06: M4.01,M4.02,M4.VB | PASS | PASS |
| M4.08.P01 | M4.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M5.01.P01 | M5.01 | typed_keys/effect-exact keys | PASS | guided before M5.01:  | PASS | PASS |
| M5.02.P01 | M5.02 | decode/term groups | PASS | guided before M5.02: M5.01 | FAIL:UNDER-CONTRACT | PASS |
| M5.04.P01 | M5.04 | predict_art/a-d target/scope | PASS | guided before M5.04: M5.01,M5.02 | PASS | PASS |
| M5.05.P01 | M5.05 | why/two term groups | PASS | guided before M5.05: M5.01,M5.02 | WARN:WHY-CONTRACT | PASS |
| M5.06.P01 | M5.06 | typed_keys/effect-exact keys | PASS | guided before M5.06: M5.01,M5.02 | PASS | PASS |
| M5.08.P01 | M5.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M6.01.P01 | M6.01 | typed_keys/effect-exact keys | PASS | guided before M6.01:  | PASS | PASS |
| M6.02.P01 | M6.02 | decode/term groups | PASS | guided before M6.02: M6.01 | PASS | PASS |
| M6.D.P01 | M6.D | decode/term groups | PASS | guided before M6.D: M6.01,M6.02 | PASS | PASS |
| M6.04.P01 | M6.04 | predict_art/a-d target/scope | PASS | guided before M6.04: M6.01,M6.02,M6.D | PASS | PASS |
| M6.05.P01 | M6.05 | why/two term groups | PASS | guided before M6.05: M6.01,M6.02,M6.D | WARN:WHY-CONTRACT | PASS |
| M6.MOVE.P01 | M6.MOVE | decode/term groups | PASS | guided before M6.MOVE: M6.01,M6.02,M6.D | PASS | PASS |
| M6.06.P01 | M6.06 | typed_keys/effect-exact keys | PASS | guided before M6.06: M6.01,M6.02,M6.D,M6.MOVE | PASS | PASS |
| M6.08.P01 | M6.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M7.01.P01 | M7.01 | typed_keys/effect-exact keys | PASS | guided before M7.01:  | PASS | PASS |
| M7.02.P01 | M7.02 | decode/term groups | PASS | guided before M7.02: M7.01 | PASS | PASS |
| M7.DOT.P01 | M7.DOT | decode/term groups | PASS | guided before M7.DOT: M7.01,M7.02 | PASS | PASS |
| M7.MAC.P01 | M7.MAC | decode/term groups | PASS | guided before M7.MAC: M7.01,M7.02,M7.DOT | PASS | PASS |
| M7.VIS.P01 | M7.VIS | decode/term groups | PASS | guided before M7.VIS: M7.01,M7.02,M7.DOT,M7.MAC | PASS | PASS |
| M7.04.P01 | M7.04 | predict_art/a-d target/scope | PASS | guided before M7.04: M7.01,M7.02,M7.DOT,M7.MAC,M7.VIS | PASS | PASS |
| M7.GLOBAL.P01 | M7.GLOBAL | decode/term groups | PASS | guided before M7.GLOBAL: M7.01,M7.02,M7.DOT,M7.MAC,M7.VIS | PASS | PASS |
| M7.05.P01 | M7.05 | why/two term groups | PASS | guided before M7.05: M7.01,M7.02,M7.DOT,M7.MAC,M7.VIS,M7.GLOBAL | WARN:WHY-CONTRACT | PASS |
| M7.06.P01 | M7.06 | typed_keys/effect-exact keys | PASS | guided before M7.06: M7.01,M7.02,M7.DOT,M7.MAC,M7.VIS,M7.GLOBAL | PASS | PASS |
| M7.08.P01 | M7.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M8.01.P01 | M8.01 | typed_keys/effect-exact keys | PASS | guided before M8.01:  | PASS | PASS |
| M8.02.P01 | M8.02 | decode/term groups | PASS | guided before M8.02: M8.01 | FAIL:UNDER-CONTRACT | PASS |
| M8.04.P01 | M8.04 | predict_art/a-d target/scope | PASS | guided before M8.04: M8.01,M8.02 | PASS | PASS |
| M8.05.P01 | M8.05 | why/two term groups | PASS | guided before M8.05: M8.01,M8.02 | WARN:WHY-CONTRACT | PASS |
| M8.06.P01 | M8.06 | typed_keys/effect-exact keys | PASS | guided before M8.06: M8.01,M8.02 | PASS | PASS |
| M8.08.P01 | M8.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M9.01.P01 | M9.01 | typed_keys/effect-exact keys | PASS | guided before M9.01:  | PASS | PASS |
| M9.02.P01 | M9.02 | decode/term groups | PASS | guided before M9.02: M9.01 | PASS | PASS |
| M9.04.P01 | M9.04 | predict_art/a-d target/scope | PASS | guided before M9.04: M9.01,M9.02 | PASS | PASS |
| M9.05.P01 | M9.05 | why/two term groups | PASS | guided before M9.05: M9.01,M9.02 | WARN:WHY-CONTRACT | PASS |
| M9.06.P01 | M9.06 | typed_keys/effect-exact keys | PASS | guided before M9.06: M9.01,M9.02 | PASS | PASS |
| M9.08.P01 | M9.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M10.01.P01 | M10.01 | typed_keys/effect-exact keys | PASS | guided before M10.01:  | PASS | PASS |
| M10.02.P01 | M10.02 | decode/term groups | PASS | guided before M10.02: M10.01 | PASS | PASS |
| M10.04.P01 | M10.04 | predict_art/a-d target/scope | PASS | guided before M10.04: M10.01,M10.02 | PASS | PASS |
| M10.05.P01 | M10.05 | why/two term groups | PASS | guided before M10.05: M10.01,M10.02 | WARN:WHY-CONTRACT | PASS |
| M10.06.P01 | M10.06 | typed_keys/effect-exact keys | PASS | guided before M10.06: M10.01,M10.02 | PASS | PASS |
| M10.08.P01 | M10.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M11.01.P01 | M11.01 | typed_keys/effect-exact keys | PASS | guided before M11.01:  | PASS | PASS |
| M11.02.P01 | M11.02 | decode/term groups | PASS | guided before M11.02: M11.01 | PASS | PASS |
| M11.UR.P01 | M11.UR | decode/term groups | PASS | guided before M11.UR: M11.01,M11.02 | PASS | PASS |
| M11.04.P01 | M11.04 | predict_art/a-d target/scope | PASS | guided before M11.04: M11.01,M11.02,M11.UR | PASS | PASS |
| M11.05.P01 | M11.05 | why/two term groups | PASS | guided before M11.05: M11.01,M11.02,M11.UR | WARN:WHY-CONTRACT | PASS |
| M11.06.P01 | M11.06 | typed_keys/effect-exact keys | PASS | guided before M11.06: M11.01,M11.02,M11.UR | PASS | PASS |
| M11.VE.P01 | M11.VE | decode/term groups | PASS | guided before M11.VE: M11.01,M11.02,M11.UR | PASS | PASS |
| M11.08.P01 | M11.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M12.01.P01 | M12.01 | typed_keys/effect-exact keys | PASS | guided before M12.01:  | PASS | PASS |
| M12.02.P01 | M12.02 | decode/term groups | PASS | guided before M12.02: M12.01 | FAIL:UNDER-CONTRACT | PASS |
| M12.FIND.P01 | M12.FIND | decode/term groups | PASS | guided before M12.FIND: M12.01,M12.02 | PASS | PASS |
| M12.04.P01 | M12.04 | predict_art/a-d target/scope | PASS | guided before M12.04: M12.01,M12.02,M12.FIND | PASS | PASS |
| M12.05.P01 | M12.05 | why/two term groups | PASS | guided before M12.05: M12.01,M12.02,M12.FIND | WARN:WHY-CONTRACT | PASS |
| M12.06.P01 | M12.06 | typed_keys/effect-exact keys | PASS | guided before M12.06: M12.01,M12.02,M12.FIND | PASS | PASS |
| M12.08.P01 | M12.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M13.01.P01 | M13.01 | typed_keys/effect-exact keys | PASS | guided before M13.01:  | PASS | PASS |
| M13.02.P01 | M13.02 | decode/term groups | PASS | guided before M13.02: M13.01 | FAIL:UNDER-CONTRACT | PASS |
| M13.BE.P01 | M13.BE | decode/term groups | PASS | guided before M13.BE: M13.01,M13.02 | PASS | PASS |
| M13.04.P01 | M13.04 | predict_art/a-d target/scope | PASS | guided before M13.04: M13.01,M13.02,M13.BE | PASS | PASS |
| M13.05.P01 | M13.05 | why/two term groups | PASS | guided before M13.05: M13.01,M13.02,M13.BE | WARN:WHY-CONTRACT | PASS |
| M13.06.P01 | M13.06 | typed_keys/effect-exact keys | PASS | guided before M13.06: M13.01,M13.02,M13.BE | PASS | PASS |
| M13.08.P01 | M13.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M14.01.P01 | M14.01 | typed_keys/effect-exact keys | PASS | guided before M14.01:  | PASS | PASS |
| M14.02.P01 | M14.02 | decode/term groups | PASS | guided before M14.02: M14.01 | PASS | PASS |
| M14.04.P01 | M14.04 | predict_art/a-d target/scope | PASS | guided before M14.04: M14.01,M14.02 | PASS | PASS |
| M14.PARA.P01 | M14.PARA | decode/term groups | PASS | guided before M14.PARA: M14.01,M14.02 | FAIL:UNDER-CONTRACT | PASS |
| M14.05.P01 | M14.05 | why/two term groups | PASS | guided before M14.05: M14.01,M14.02,M14.PARA | WARN:WHY-CONTRACT | PASS |
| M14.06.P01 | M14.06 | typed_keys/effect-exact keys | PASS | guided before M14.06: M14.01,M14.02,M14.PARA | PASS | PASS |
| M14.08.P01 | M14.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M15.01.P01 | M15.01 | typed_keys/effect-exact keys | PASS | guided before M15.01:  | PASS | PASS |
| M15.02.P01 | M15.02 | decode/term groups | PASS | guided before M15.02: M15.01 | PASS | PASS |
| M15.04.P01 | M15.04 | predict_art/a-d target/scope | PASS | guided before M15.04: M15.01,M15.02 | PASS | PASS |
| M15.BA.P01 | M15.BA | decode/term groups | PASS | guided before M15.BA: M15.01,M15.02 | PASS | PASS |
| M15.05.P01 | M15.05 | why/two term groups | PASS | guided before M15.05: M15.01,M15.02,M15.BA | WARN:WHY-CONTRACT | PASS |
| M15.06.P01 | M15.06 | typed_keys/effect-exact keys | PASS | guided before M15.06: M15.01,M15.02,M15.BA | PASS | PASS |
| M15.08.P01 | M15.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M16.01.P01 | M16.01 | typed_keys/effect-exact keys | PASS | guided before M16.01:  | PASS | PASS |
| M16.02.P01 | M16.02 | decode/term groups | PASS | guided before M16.02: M16.01 | FAIL:UNDER-CONTRACT | PASS |
| M16.04.P01 | M16.04 | predict_art/a-d target/scope | PASS | guided before M16.04: M16.01,M16.02 | PASS | PASS |
| M16.05.P01 | M16.05 | why/two term groups | PASS | guided before M16.05: M16.01,M16.02 | WARN:WHY-CONTRACT | PASS |
| M16.06.P01 | M16.06 | typed_keys/effect-exact keys | PASS | guided before M16.06: M16.01,M16.02 | PASS | PASS |
| M16.08.P01 | M16.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M17.01.P01 | M17.01 | typed_keys/effect-exact keys | PASS | guided before M17.01:  | PASS | PASS |
| M17.02.P01 | M17.02 | decode/term groups | PASS | guided before M17.02: M17.01 | PASS | PASS |
| M17.04.P01 | M17.04 | predict_art/a-d target/scope | PASS | guided before M17.04: M17.01,M17.02 | PASS | PASS |
| M17.05.P01 | M17.05 | why/two term groups | PASS | guided before M17.05: M17.01,M17.02 | WARN:WHY-CONTRACT | PASS |
| M17.06.P01 | M17.06 | typed_keys/effect-exact keys | PASS | guided before M17.06: M17.01,M17.02 | PASS | PASS |
| M17.08.P01 | M17.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |
| M18.01.P01 | M18.01 | typed_keys/effect-exact keys | PASS | guided before M18.01:  | PASS | PASS |
| M18.02.P01 | M18.02 | decode/term groups | PASS | guided before M18.02: M18.01 | PASS | PASS |
| M18.04.P01 | M18.04 | predict_art/a-d target/scope | PASS | guided before M18.04: M18.01,M18.02 | PASS | PASS |
| M18.EXPR.P01 | M18.EXPR | decode/term groups | PASS | guided before M18.EXPR: M18.01,M18.02 | PASS | PASS |
| M18.05.P01 | M18.05 | why/two term groups | PASS | guided before M18.05: M18.01,M18.02,M18.EXPR | WARN:WHY-CONTRACT | PASS |
| M18.06.P01 | M18.06 | typed_keys/effect-exact keys | PASS | guided before M18.06: M18.01,M18.02,M18.EXPR | PASS | PASS |
| M18.08.P01 | M18.08 | complete/accepted token | PASS | module check after preceding module lessons (late use) | PASS | PASS |

## Sources inspected

- share/curriculum-v2.json — live artifact, 174 cards, 326 questions, revision 2026-09-28.24.
- share/gen_curriculum_v2.py:3417 (family inference); :3488-3600 (paired-question generation/contracts); :4319-4429 (bank placement/card order).
- share/v2_runtime.py:719-807 (answer guidance/grading); :847-880 (paired placement); :2206-2330 (concept/check rotation); :2620-2708 (changed-art review).
- share/v2_keys.py — key-by-key command/effect family cross-check.

## Handoff

This is a new audit report only. It does not modify generator/runtime/curriculum/tests/bin/vim-daily-gate or unrelated worktree changes. Repair priority: remove or move the 21 future-content IDs from M*.03 banks, expand compound decode/why contracts, and fix family inference before regenerating.
