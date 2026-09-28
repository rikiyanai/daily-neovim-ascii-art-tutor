# Grammar-first sequence audit: M10-M14

Status: complete audit of the current generated curriculum and runtime
surfaces. This report is evidence for the frozen pre-insertion audit boundary.
It does not edit curriculum, generator, runtime, launcher, or tests.

## Snapshot and scope

The audit uses repository HEAD 17f87121baddc958e23e17aafdf2ac0857e5091f,
the preserved dirty worktree, generated curriculum revision .22 in
share/curriculum-v2.json, cards M10.01-M14.08, their question banks, generator
definitions, runtime brief/result/review code, legacy attachments, and tests.

The requirement ledger is share/audits/GRAMMAR_FIRST_REQUIREMENT.md:10-25.
Its exclusions are binding: a key in expected or recipe, a validator token, a
legacy attachment, a distractor, or a generic cheat sheet is not teaching
(share/audits/GRAMMAR_FIRST_REQUIREMENT.md:27-37).

The report uses these evidence labels:

- E: explicit grammar decomposition before the card.
- I: prior interpretation question.
- C: prior command-completion question.
- G: prior guided performance.
- H: later key-hidden retrieval.
- R: changed-art review evidence.
- Q: the executable card declares a paired conceptual question.
- K: card-owned KEYS WORTH KEEPING vocabulary.
- S: the hint adds strategy or diagnostic information beyond DO THIS.

Yes means the current artifact contains the surface. Strict no means the
surface exists only after first use, is answer-key material, or fails the
grammar-first definition. A changed-art bank is marked post-pass when the
runtime schedules it after the card has already passed; that is not evidence
before a mastery claim.

## Executive findings

1. There are 40 cards in M10-M14. The 30 executable cards are .01, .02, .04,
   .05, .06, and .08 in each module. The ten .03 and .07 cards are conceptual.
2. Every module has paired four-choice questions with mistake-specific feedback
   in its question bank. The banks are at share/curriculum-v2.json:17155-18795,
   and the generator enforces four choices, paired animation/Neovim fields,
   and non-generic feedback at share/gen_curriculum_v2.py:3115-3220 and
   3563-3634.
3. The question bank is not sequenced as grammar teaching. Questions are
   attached only to concept cards .03, .07, and module checks .08; ordinary
   executable cards have no question_ids. The card builder adds question IDs
   only for ordinals 3, 7, and 8
   (share/gen_curriculum_v2.py:3443-3477). Thus 25 of the 30 executable cards
   have no paired conceptual check.
4. No M10-M14 command family has a current-card explicit decomposition of
   Normal operator grammar [count] operator [count] motion-or-text-object,
   standalone-command grammar, or Ex grammar
   :[address-or-range] command /pattern/replacement/ flags <Enter> before its
   first required use. The current cards provide action prose such as copy or
   replace, not grammar parts.
5. The current M10-M14 review banks are the source-linked banks listed at
   share/curriculum-v2.json:20527-20709. They omit M10.01, M10.02, M10.04,
   M10.05, M10.08, M11.01, M12.01, M12.02, M12.08, M13.01, M13.02, M13.08,
   and M14.02. Even where a bank exists, the runtime schedules it after the
   source card passes (share/v2_runtime.py:319-325, 1834-1854, 1885-1933),
   while module mastery is computed from passed cards alone
   (share/v2_runtime.py:326-341). No changed-art review is a prerequisite
   for a mastery claim.
6. Hidden briefs do not preserve command-family vocabulary. When no
   key_vocabulary exists, KEYS WORTH KEEPING falls back to F1, undo/redo,
   and save/quit reminders (share/v2_runtime.py:663-676, 716-727).
   M10-M14 hidden cards generally have no key_vocabulary.
7. The runtime result page offers Enter for the progress page, but it does not
   offer a second explicit action for the next eligible concept or lesson
   (share/v2_runtime.py:1180-1197, 1371-1397). This leaves GF-09 open.
8. Current tests validate generated counts, paired question fields, target
   replay, method coverage, and selected review banks. They do not validate
   grammar decomposition, prior interpretation/completion order,
   executable-card question pairing, or review-before-mastery
   (share/test_v2.py:88-150, 175-205, 788-814, 852-904).

## Command-family first-use register

The table distinguishes current guided use from strict teaching. A legacy
concept can contain excellent grammar prose and still be excluded.

| Command family | Grammar class | First current required use | Prior current evidence | Strict result | Proposed insertion |
|---|---|---|---|---|---|
| 3yy or yy plus p/P | Normal operator plus standalone linewise put | M0.02, then M10.02 and later frame copies | M0.02 has a guided recipe and two vocabulary bullets, but no [count] operator [count] motion/text-object decomposition; M0.Q02/Q08 follow first use (curriculum-v2.json:6930, 17155-17483) | E no; I/C no before first use; later guided use yes | Add grammar before M0.02; pair parse/completion with a linewise frame-copy edit |
| :[range]s/pat/repl/g<CR> | Ex substitute grammar | M0.02 guided, M0.06 hidden transfer, then M11.05/M12.05/M13.05 | M0.02 says :{start},{end}s/old/new/g and explains g, but does not decompose address, s, pattern, replacement, flag, and Enter; M0.Q03 is in the later module check | E no; I/C no before first use; later guided use yes | Add ranged-substitute grammar before M0.02, including :8s/-/=/g and :4,6s/o/O/g interpretation and completion |
| :[range]t{address}<CR> | Ex addressed-copy grammar | M0.05 hidden comparison | A hint names addressed copy, but no grammar card decomposes source range, t, destination, and Enter (curriculum-v2.json:7064) | E/I/C no; first use hidden | Add Ex-copy grammar, guided range copy, hidden comparison, and changed-art review before M0.05 |
| r{char} | Standalone Normal replace-one-cell command | M0.01 guided | The recipe says r replaces a core; legacy prose is excluded (curriculum-v2.json:6883, gen_curriculum_v2.py:24-44) | E/I/C no before first use | Add standalone-command card before M0.01: Normal mode, one cell, no Insert transition |
| $, 0, G, f{char}, t{char}, T{char}, l, h, j | Standalone Normal motions | Scattered uses begin in M0; M10-M14 continue them | Recipes and hints name motions but do not teach motion vocabulary as composable operands | E/I/C no | Add a compact motion grammar bank before the first operator-family card |
| o/O | Standalone open-line commands | First hidden on M1.04; repeated hidden on M8.04 and M10.04; there is no current visible guided card | Hints say open-line mode creates a row, but no current grammar teaches below/above, indentation behavior, or the linewise alternative | E/I/C/G no before hidden use | Add yy/p versus o guided comparison before M1.04; include the art-buffer indent invariant |
| C (c$) plus Insert text and <Esc> | Normal change-to-end-of-line contraction | M4.01 guided; M10.02 uses it visibly | No decomposition that C is c$, or that it enters Insert mode until Escape | E/I/C no | Add a C = c$ completion item and bounded redraw before M10.02 |
| R...<Esc> | Standalone Replace mode | M11.01 guided | Hint names Replace mode and in-place redraw, but no mode-transition grammar or completion precedes it (curriculum-v2.json:7363) | E/I/C no | Add Replace-mode grammar and fixed-width guided roof edit before M11.01 |
| u/<C-r> | Standalone undo/redo | M11.04 hidden | Only richer explanation is the legacy undo attachment, which is excluded (curriculum-v2.json:7549, gen_curriculum_v2.py:26, v2_runtime.py:606-623) | E/I/C no; first current use hidden | Add causal redraw -> u -> <C-r> guided card before M11.04 |
| :set virtualedit=all<CR>, |, i, j, . | Ex option plus exact-column insert and dot repeat | M11.08 hidden module check | No guided card teaches :set grammar, virtual columns, or dot replay before this card | E/G/H sequence absent; mastery card is first use | Insert guided exact-column trail card before M11.08 |
| t{char}/T{char} plus l/h | Till motions plus one-cell replace | M12.01/.02 guided | Recipes explain stop before/after but no grammar or completion precedes either use | E/I/C no | Add paired t/T approach-and-replace lesson before M12.01 |
| f{char}, ;, , | Find and repeat/reverse-find commands | f appears earlier; ;/, first in M12.04 hidden | M12.04 names character search but not last-search state or repeat direction (curriculum-v2.json:8221) | ;/, have no E/I/C/G before hidden use | Add guided repeated-search lower-joint edit before M12.04 |
| W, E, B | Standalone WORD motions | W guided M13.01; E/B hidden M13.04 | M13 questions explain punctuation behavior only after use | E/B first use hidden; no prior guided stage | Add WORD-motion grammar and guided three-edge edit before M13.04 |
| . | Standalone repeat-last-change | Earlier M7.04; M13.02/M13.08 use it | Hints name dot only when a recipe pattern matches (gen_curriculum_v2.py:3278-3283) | No explicit grammar or completion | Add repeat-state interpretation and completion before first hidden dot use |
| "a/"b plus yl and <C-r>a/<C-r>b | Named-register capture and insertion | Register use M3.06; M14.01 guided; M14.08 hidden b | M14 prose names registers but does not decompose prefix, operator, motion, and retrieval | E/I/C no | Add register grammar before M14.01 and retrieval completion before M14.08 |
| yap, P, }, and :[range]t | Paragraph object, paragraph motion, put-above, Ex alternative | yap M14.02 guided; }/P hidden M14.05 | Legacy paragraph prose is provenance and cannot count (gen_curriculum_v2.py:32, v2_runtime.py:606-623) | yap guided but not grammar-taught; }/P/Ex first hidden | Add paragraph-boundary interpretation/completion before M14.02 and a guided semantic-object copy before M14.05 |

## Executable-card audit

The card line identifies the exact generated object. Q: no means the card
does not declare a conceptual question even though a nearby concept card has
one. R: post-pass means a source-linked bank exists but can only be retrieved
after the card has already passed.

### M10 - SJIS puff tween

Source definitions: gen_curriculum_v2.py:1012-1090. Generated cards:
curriculum-v2.json:6883-7330.

| Card | Required families and grammar class | Prior E/I/C/G | Later H | R | K/S/Q | Gap and insertion |
|---|---|---|---|---|---|---|
| M10.01, guided_edit, JSON:6883 | $ motion; r{char} standalone replace | E/I/C no; G this card | M10.06 hides $r | none | exact visible recipe; S n/a; Q no | GF-01/02/04/05/06. Add standalone motion/replace interpretation and completion before this guided edit; add review |
| M10.02, guided_edit, JSON:6930 | 3yy/p; G/line motions; C=c$ plus Insert/Escape | E no; prior G M0.02 for 3yy/p without strict grammar; I/C no; G this card for C | partial yank/put in M10.05; no hidden C retrieval | none | exact visible recipe; S n/a; Q no | GF-01/04/05/06. Add count/operator/put and C=c$ grammar before this card; add paired questions and review |
| M10.04, independent_edit, JSON:7006 | G; standalone o; three Insert rows and Escape | E/I/C no; M1.04/M8.04 are recipes, not grammar | this is first hidden o use for M10 | none | generic fallback; open-line scope adds strategy; Q no | GF-02/04/05/06/11. Insert yy/p versus o guided comparison; require art-buffer indent proof |
| M10.05, compare_methods, JSON:7064 | :7,9t$<CR>; alternate 7G3yyGp | E/I/C no; prior G M0.02; :t first appears hidden | this card hides both paths | none | generic fallback; addressed-copy scope adds strategy; Q no | GF-03/04/05/06/10. Insert addressed-copy grammar, completion, guided range copy, and review |
| M10.06, transfer, JSON:7149 | $, 0, f{char}, r{char} | E/I/C no; earlier recipes only; no current guided stage | this transfer is hidden | yes, 2 variants, post-pass | generic fallback; landmark scope adds strategy; Q no | GF-01/02/04/06. Add paired retrieval and make review evidence part of mastery |
| M10.08, module_check, JSON:7270 | :1,3t$<CR>; range/destination grammar; five-frame check | E/I/C no; prior :t only hidden; no guided Ex-copy stage | this card hidden | none; mastery not review-gated | generic fallback; Ex scope only; Q yes, 10 questions | GF-03/04/05/06. Add grammar/guided Ex copy and gate mastery on changed-art review |

M10.Q01 asks for $r, Q02 for gg3yyGp, and Q04 for contour placement at
curriculum-v2.json:17155-17286. These are paired post-use questions, not prior
grammar interpretation/completion stages.

### M11 - Fixed-width redraw

Source definitions: gen_curriculum_v2.py:1092-1233. Generated cards:
curriculum-v2.json:7363-8000.

| Card | Required families and grammar class | Prior E/I/C/G | Later H | R | K/S/Q | Gap and insertion |
|---|---|---|---|---|---|---|
| M11.01, guided_edit, JSON:7363 | 0/l; standalone R...<Esc> | E/I/C no; G this card | M11.04/.06 hide R | none | exact visible recipe; S n/a; Q no | GF-01/02/04/05/06. Add Replace-mode grammar and fixed-width interpretation/completion before this card; add review |
| M11.02, guided_edit, JSON:7416 | 3yy/p; complete-frame copy | E no; M0.02 recipe; I/C no; G this card | M11.04 hides related frame edit | yes, 2 variants, post-pass | exact visible recipe; S n/a; Q no | GF-01/04/05/06. Link paired questions and require review before method mastery |
| M11.04, independent_edit, JSON:7549 | G/0/l; R; u; <C-r> | E/I/C no; R in M11.01; undo/redo hidden here; legacy attachment excluded | this card hidden | yes, 2 variants, post-pass | generic fallback; register wording is unrelated to undo; Q no | GF-02/04/05/06. Insert causal undo/redo guided card and completion before hidden edit |
| M11.05, compare_methods, JSON:7697 | current-row :s/o/O/g<CR>; local f/r alternative | E/I/C no; prior :s recipes but no decomposition | this card hidden | yes, 2 variants, post-pass | generic fallback; line scope stated; Q no | GF-03/04/05/06/10. Add current-row substitute grammar and completion |
| M11.06, transfer, JSON:7827 | 0lR==<Esc> | E no; G M11.01 recipe; I/C no | this transfer hidden | yes, 2 variants, post-pass | generic fallback; fixed-width scope useful; Q no | GF-02/04/06. Add paired changed-art retrieval and review gate |
| M11.08, module_check, JSON:7948 | :set virtualedit=all<CR>; |; i; .; j | E/I/C/G no; first current virtualedit/exact-column/dot path | this card hidden | yes, 2 variants, post-pass | generic fallback; exact-column hint useful but not grammar; Q yes, 10 questions | GF-02/03/04/05/06. Insert option/column/dot grammar and guided trail; make review prerequisite |

M11.Q01/Q03 explain Replace mode after M11.01, and Q08 explains virtualedit
after M11.08 (curriculum-v2.json:17485-17813).

### M12 - Joint sweep

Source definitions: gen_curriculum_v2.py:1235-1381. Generated cards:
curriculum-v2.json:8081-8714.

| Card | Required families and grammar class | Prior E/I/C/G | Later H | R | K/S/Q | Gap and insertion |
|---|---|---|---|---|---|---|
| M12.01, guided_edit, JSON:8081 | 0t{char}; l; r{char} | E/I/C no; G this card | M12.06 hides t/r transfer | none | exact visible recipe; S n/a; Q no | GF-01/02/04/05/06. Add t-before-target and r grammar plus completion before this edit; add review |
| M12.02, guided_edit, JSON:8139 | 3yy/p; $T{char}; h; r | E no; frame-copy recipe; I/C no; G this card | M12.06 hidden | none | exact visible recipe; S n/a; Q no | GF-01/02/04/05/06. Add backward-till grammar and paired approach-direction check |
| M12.04, independent_edit, JSON:8221 | 3yy/p; f{char}; ;; ,; r | E/I/C no; f earlier, ;/, first hidden here | this card hidden | yes, 2 variants, post-pass | generic fallback; repeat-search scope not decomposed; Q no | GF-01/02/04/05/06. Insert repeated-search grammar, completion, guided edit, and review |
| M12.05, compare_methods, JSON:8364 | :1,3t$<CR>; current-row :s/o/O/g; f/r/;/, alternative | E/I/C no; recipes only | this card hidden | yes, 2 variants, post-pass | generic fallback; scope/repeatability comparison useful; Q no | GF-03/04/05/06/10. Add paired Ex range/substitute interpretation and completion |
| M12.06, transfer, JSON:8527 | 0t/$T; l/h; r | E no; G M12.01/.02 recipes; I/C no | this transfer hidden | yes, 2 variants, post-pass | generic fallback; changed-shell scope useful; Q no | GF-01/02/04/06. Link paired concept evidence and review gate |
| M12.08, module_check, JSON:8662 | :1,3t$<CR>; t/T; l/h; r | E/I/C no; no new guided return stage | this card hidden | none; mastery not review-gated | generic fallback; addressed copy only; Q yes, 10 questions | GF-01/03/04/05/06. Add mirrored-return grammar/guided stage and review prerequisite |

M12 questions test timing and t/T placement at curriculum-v2.json:17815-18143,
but remain post-use paired questions.

### M13 - Texture pulse

Source definitions: gen_curriculum_v2.py:1383-1532. Generated cards:
curriculum-v2.json:8758-9401.

| Card | Required families and grammar class | Prior E/I/C/G | Later H | R | K/S/Q | Gap and insertion |
|---|---|---|---|---|---|---|
| M13.01, guided_edit, JSON:8758 | W; r{char} | E/I/C no; G this card | M13.02/.06/.08 | none | exact visible recipe; S n/a; Q no | GF-01/02/04/05/06. Add WORD grammar and completion before guided pulse; add review |
| M13.02, guided_edit, JSON:8815 | 3yy/p; G; W; .; r | E no; frame-copy recipe and earlier M7 dot path; I/C no; G this card | M13.04/.08 | none | exact visible recipe; S n/a; Q no | GF-01/02/04/05/06. Insert paired WORD/dot interpretation and completion; add review |
| M13.04, independent_edit, JSON:8897 | 3yy/p; E; counted W; B; r | E/I/C no; W M13.01; E/B first hidden here | this card hidden | yes, 2 variants, post-pass | generic fallback; frame scope useful; Q no | GF-01/02/04/05/06. Insert guided E/W/B edge traversal and completion |
| M13.05, compare_methods, JSON:9047 | :7,9t$<CR>; 10G:s/!/*/g<CR>; local f/;/r | E/I/C no; Ex recipes only | this card hidden | yes, 2 variants, post-pass | generic fallback; exact-row scope useful; Q no | GF-03/04/05/06/10. Add paired range/substitute grammar and guided flash |
| M13.06, transfer, JSON:9210 | counted W; B; r | E no; W earlier, B hidden M13.04; I/C no | this transfer hidden | yes, 2 variants, post-pass | generic fallback; changed-cluster scope useful; Q no | GF-01/02/04/06. Add transfer question and review gate |
| M13.08, module_check, JSON:9349 | :1,3t$<CR>; W; B; .; r | E/I/C no; no guided exit stage | this card hidden | none; mastery not review-gated | generic fallback; addressed copy only; Q yes, 10 questions | GF-01/03/04/05/06. Add return-pulse grammar/guided edit and review prerequisite |

M13.Q09 is an output prediction about W at curriculum-v2.json:18145-18473.
It is not a prior command-completion item.

### M14 - Variant palette

Source definitions: gen_curriculum_v2.py:1534-1690. Generated cards:
curriculum-v2.json:9444-10209.

| Card | Required families and grammar class | Prior E/I/C/G | Later H | R | K/S/Q | Gap and insertion |
|---|---|---|---|---|---|---|
| M14.01, guided_edit, JSON:9444 | f{char}; "a + yl; j/0; R; <C-r>a | E/I/C no; G this card | M14.04/.06/.08 | yes, 2 variants, post-pass | exact visible recipe; S n/a; Q no | GF-01/02/04/05/06. Add register grammar, retrieval completion, and paired palette edit before this card |
| M14.02, guided_edit, JSON:9568 | yap + ap text object; G; p | E no; legacy text-object prose excluded; G this card; I/C no | M14.05 | none | exact visible recipe; S n/a; Q no | GF-01/04/05/06. Add paragraph-object grammar and boundary completion; add review |
| M14.04, independent_edit, JSON:9664 | "a; f; R; <C-r>a | E/I/C no; G M14.01 recipe; hidden retrieval here | this card hidden | yes, 2 variants, post-pass | generic fallback; register scope useful; Q no | GF-01/02/04/05/06. Add paired register retrieval before hidden use |
| M14.05, compare_methods, JSON:9826 | yap; }; j; P; alternate :5,8t$<CR> | E/I/C no; yap M14.02; }/P/Ex hidden here; legacy attachment excluded | this card hidden | yes, 2 variants, post-pass | generic fallback; semantic/range comparison useful; Q no | GF-01/03/04/05/06/10. Add paragraph-boundary guided comparison and Ex grammar |
| M14.06, transfer, JSON:10012 | "a; R; <C-r>a | E no; G M14.01; I/C no | this transfer hidden | yes, 2 variants, post-pass | generic fallback; changed-shell invariant useful; Q no | GF-01/02/04/06. Add paired changed-art register retrieval and review gate |
| M14.08, module_check, JSON:10157 | "b; yl; } twice; j; R; <C-r>b | E/I/C no; no guided register-b/paragraph-navigation stage | this card hidden | yes, 2 variants, post-pass | generic fallback; navigation named but not decomposed; Q yes, 10 questions | GF-01/02/04/05/06. Insert register-b/navigation grammar and review prerequisite |

M14.Q02 interprets "ayl, Q05 compares yap and :5,8t$, and Q08 identifies ap
at curriculum-v2.json:18475-18795. These are useful paired questions after
use, not prior grammar stages.

## Runtime, legacy, and test findings

### Runtime briefs and result flow

share/v2_runtime.py:632-724 builds the brief from card fields. It shows the
recipe only when show_recipe is true and otherwise shows a target plus a hint.
share/gen_curriculum_v2.py:3425-3430 sets show_recipe true only for ordinals
1 and 2. This makes .04, .05, .06, and .08 retrieval cards key-hidden, but
does not create a preceding grammar stage.

share/gen_curriculum_v2.py:3236-3301 derives hints from tokens in the accepted
path. This is useful scope information, but it is reverse-derived from the
answer path. It does not teach a learner to parse a command, and the hidden
brief has no structured grammar fields.

share/v2_runtime.py:663-676 and 716-727 supply generic KEYS WORTH KEEPING
fallback text when a card has no key vocabulary. The fallback is not GF-06
vocabulary for M10-M14 hidden cards because it does not name the command
family, its operands, or its scope.

The feedback page says Enter for skill-tree progress and then returns to the
progress page (share/v2_runtime.py:1180-1197, 1371-1397). It has no explicit
next-eligible-question action. next_card() does enforce module order and
prerequisites (share/v2_runtime.py:404-413), so a continuation action can
reuse it without bypassing evidence.

### Changed-art review and mastery

The review builder requires source-linked review_variants or a transfer bank
(share/v2_runtime.py:1834-1854). The review runner asks one conceptual
question and then performs changed-art edit only when the answer is right
(share/v2_runtime.py:1885-1929). This is a valid paired review mechanism, but
it is scheduled after a card pass.

The completion path records next_due after a pass and requires only a passed
unseen transfer before a module check can award mastery
(share/v2_runtime.py:1412-1458). The module projection changes to mastered
when all card IDs are passed, independent of review-stage events
(share/v2_runtime.py:326-341). GF-05 and GF-06 therefore remain open even
for cards that have two changed-art variants.

### Legacy attachments

The generator declares legacy attachments as provenance, not mastery migration
(share/gen_curriculum_v2.py:21-23). M11.04 receives legacy undo; M14.05
receives legacy paragraph-object (share/gen_curriculum_v2.py:24-44). The
runtime renders attached material under LEGACY LESSON SOURCES and LEGACY VIM
CONCEPT (share/v2_runtime.py:606-623, 677-678, 732-740), but the requirement
ledger excludes that material from teaching evidence. The rich grammar prose in
share/concepts.json:6-28 is a source to adapt, not proof that the current
M10-M14 sequence teaches grammar.

### Tests

Current tests prove:

- 19 modules, 152 cards, 190 paired questions, four choices, and
  mistake-specific feedback (share/test_v2.py:88-128).
- Concept/module-check question counts and key hiding
  (share/test_v2.py:136-150).
- Runtime target replay, method alternatives, transfer variants, and selected
  changed-art banks (share/test_v2.py:175-205, 788-904).
- Real Neovim replay for recipes, with -u NONE -i NONE unless explicitly run
  with the real configuration (share/test_v2.py:823-847).

Current tests do not prove:

- grammar decomposition before first command-family use;
- an appropriate interpretation, decode, or open-key item before first use;
- a command-completion item before first use;
- every executable card declares a paired question;
- KEYS WORTH KEEPING names the hidden card family without leaking the exact
  accepted path;
- changed-art review is passed before mastery;
- a motivated continuation action is present.

The test summary claims executable and compare-path counts, not grammar
sequencing (share/test_v2.py:1122-1125). share/test_drills.py:1-5 states a
recipe-passability falsifier; recipe passability is not teaching evidence.

## Gap register mapped to the requirement ledger

| Gap ID | Ledger requirement | Evidence | Scope | Required correction |
|---|---|---|---|---|
| M10-14-GF01 | GF-01 Normal operator grammar | No decomposition before 3yy, yap, or C; generated recipes are accepted paths only (gen_curriculum_v2.py:3401-3429) | M10.02, M11.02, M12.02/.04, M13.02/.04, M14.02/.05 | Add grammar parts, interpretation, completion, guided edit, hidden retrieval, and review |
| M10-14-GF02 | GF-02 standalone Normal commands | r, R, o, u, <C-r>, ., ;, ,, W/E/B, and virtual-column insertion are hinted or scripted without prior standalone semantics | All five modules | Add standalone command cards with scope, mode, operand, and animation invariant |
| M10-14-GF03 | GF-03 Ex grammar | :s, :t, and :set appear as recipes or hints; no stage identifies address/range, command, arguments, flags, and Enter | All Ex paths; first use begins M0.02/M0.05 | Add ranged substitution, addressed copy, and option grammar before hidden use |
| M10-14-GF04 | GF-04 paired conceptual/performance work | Only .03, .07, .08 carry question_ids; 25 executable cards do not (gen_curriculum_v2.py:3443-3477) | All five modules | Add card-local paired interpretation/completion IDs |
| M10-14-GF05 | GF-05 ordered stages | Current order is guided recipe -> later concept or hidden retrieval; no completion stage; mastery ignores review | All five modules | Add a family stage graph and fail generation on first hidden use before E/I/C/G |
| M10-14-GF06 | GF-06 vocabulary and review | Hidden fallback is generic; review banks omit cards and all reviews are post-pass | Runtime above; JSON:20527-20709 | Add family vocabulary and make review evidence precede mastery |
| M10-14-GF07 | GF-07 strategic hints | action_hint derives up to three token-triggered tools and a scope sentence, but no grammar (gen_curriculum_v2.py:3236-3301) | All hidden cards | State family grammar and an observable failure without exact keys |
| M10-14-GF08 | GF-08 paired questions | Choices/feedback are paired but questions arrive after first use and lack completion type | Question banks JSON:17155-18795 | Add parse and completion question types with animation invariant |
| M10-14-GF09 | GF-09 motivated continuation | Result/progress pages have Enter/hold behavior only (v2_runtime.py:1180-1197, 1371-1397) | Runtime | Add next-eligible question/lesson action using next_card() |
| M10-14-GF10 | GF-10 graded method evidence | Method coverage is generated from method requirements, not teaching sequence (gen_curriculum_v2.py:3530-3553) | Comparison/required-method cards | Link method claims to prior grammar and review |
| M10-14-GF11 | GF-11 column registration | Dirty launcher has art-only indent reset at bin/vim-daily-gate:723-742; tmux test checks cindent at share/test_tmux_v2.py:106-110; ordinary replay defaults clean | M10.04 and open-line paths | Preserve fix and add headed real-config o save/undo proof |
| M10-14-GF12 | GF-12 real Neovim default | Dirty launcher selects user config unless clean mode is requested (bin/vim-daily-gate:648-654); headed proof remains needed | All modules | Keep user-config default and add viewport/config evidence |

## Proposed insertion order

1. Repair the shared M0 grammar foundation first. Add Normal operator grammar,
   standalone r/o/p, and Ex substitute/range-copy grammar before M0.02/M0.05.
   Include parse and completion questions before the first guided edit.
2. Add a reusable grammar-stage schema to the generator. Each family record
   needs grammar class, decomposition, interpretation IDs, completion IDs,
   guided card ID, hidden retrieval IDs, review source IDs, and animation
   invariant.
3. Insert M10 grammar stages before M10.01/.02 for $/r, linewise copy, C=c$,
   and open-line versus linewise put. Insert Ex-copy grammar before M10.05 and
   a review gate before M10.08.
4. Insert M11 stages before M11.01 for Replace mode, before M11.04 for causal
   undo/redo, before M11.05 for :s, and before M11.08 for virtualedit,
   exact-column insertion, and dot.
5. Insert M12 stages before M12.01 for t/T, before M12.04 for f/;/,, and
   before M12.05 for range/substitute comparison.
6. Insert M13 stages before M13.01 for WORD motions, before M13.04 for E/B,
   and before M13.05 for bounded material substitution.
7. Insert M14 stages before M14.01 for named-register capture/retrieval,
   before M14.02 for yap/ap, and before M14.05 for }/P versus range copy.
8. Add card-local paired questions to .01, .02, .04, .05, and .06. Keep .08
   as a mixed checkpoint, but do not let it replace preceding parse,
   completion, and guided stages.
9. Add two changed-art variants to every family-bearing retrieval source.
   Require relevant review evidence before setting module state to mastered;
   retain existing spaced intervals afterward.
10. Add explicit close and continue actions to result/progress flow. The
    continue action must select only the next eligible question or lesson and
    retain evidence and remediation state.

## Acceptance tests for the next implementation phase

- Every M10-M14 executable card has a family-stage record and paired
  interpretation and completion question IDs.
- No hidden accepted path appears before explicit grammar, interpretation,
  completion, and guided evidence for that family.
- Normal operator records distinguish count, operator, motion, and text object.
- Standalone records distinguish command mode, operand, scope, and mode exit.
- Ex records distinguish address/range, command, pattern/replacement/flags,
  destination when applicable, and Enter.
- M10.04 cannot award credit unless the art buffer remains column-registered
  under the operator's real config after o.
- Hidden briefs contain family vocabulary in KEYS WORTH KEEPING without exact
  accepted paths.
- Every changed-art review uses source-linked changed art and is required
  before module mastery; later stages remain spaced.
- Wrong conceptual and artifact methods preserve specific feedback and schedule
  remediation.
- Result pages visibly offer Enter-to-close and a separate continue action.
- Existing M10-M14 target replays, method checks, playback checks, progress,
  streak, debrief, and two-column ledger behavior remain passing.
- Headed runs cover 80x24, 100x36, and 188x49 with user Neovim config, plus
  clean mode as an explicit opt-in.
