# Course completion ledger — 2026-10-01

Repository: `/Users/r/Projects/daily-neovim-ascii-art-tutor`.
Starting HEAD: `20d9c70`. Implementation is the uncommitted worktree.

The operator explicitly authorized continuing the full handoff and course work
with parallel agents. This supersedes the previous pause before handoff §9.5.
It does not authorize a commit, push, foreign-demo mutation, live learner-state
rewrite, global configuration change, or external feedback publication.

## Acceptance requirements and owners

| ID | Requirement and source | Implementation owner | Observed correct | Open reason / stage |
|---|---|---|---|---|
| C01 | Plain learner wording; handoff §9.3 | `share/learner_text.py`; authored banks | 491-question quality gate PASS on .77 | none for wording gate; headless |
| C02 | M0 one-idea first-edit sequence; handoff §9.4 | `share/gen_curriculum_v2.py:4864`; `bin/vim-daily-gate:854` | actual clean Neovim cursor suite: seven controls PASS; L0/F0 NEW 1 | none for first-edit scope; actual PTY |
| C03 | M4.DIFF remaining concepts separated; handoff §9.5.1 | `share/gen_curriculum_v2.py:7654`; authored pedagogy bank | course test: SIL/TRIM/SCB precede DIFF; DIFF NEW 0 | none; source + clean Neovim |
| C04 | M11.VE wording and one idea; handoff §9.5.2 | M11.VE authored hint and virtualedit prerequisite | source projection: only :set virtualedit is NEW; operation-specific hint | none for scoped teaching; source |
| C05 | M13 counted WORD/backward steps before retrieval; handoff §9.5.3 | M13.BE/M13.BEB before M13.04 | course ordering/effect tests PASS; BE NEW 0, BEB NEW B | none; source + clean Neovim |
| C06 | M16 counted increment first guided; handoff §9.5.4 | M16.INC before M16.04 | course test and source NEW [count]<C-a> | none; source + clean Neovim |
| C07 | Recording before counted macro replay; handoff §9.5.4 | M15.MACR → MAC → MAC3 → .08 | course ordering/effect tests PASS; one NEW operation per step | none; source + clean Neovim |
| C08 | Authored operation-specific hints, no unused toolbox; handoff §9.5.5 | authored card hints; runtime scoped hints | course and grading tests reject unused generic toolbox reminders | none; source + headless |
| C09 | Range-delete teaching/example; handoff §9.5.6 | `share/v2_keys.py`; range-delete example :2,3d | course test verifies explicit inclusive range teaching | none; source + headless |
| C10 | Real macro recipe, no placeholder; handoff §9.5.7 | M15 recording/replay recipes | placeholder rejection and real recipe effects PASS | none; source + clean Neovim |
| C11 | Guided zero inside count before 10G; handoff §9.5.8 | M2.TEN; counted-address teaching | course order and explicit 10G hint inspected | none for bridge; source |
| C12 | Undo-tree backward/forward separately taught; handoff §9.5.9 | M11.BR/GM/GP/ER separated operations; UT/UTH two-take comparison | final .77 ten source-history cards pass all 30 actual gate/question/result routes; primary and review source-frame effects pass | none for tested history scope; source + actual PTY |
| C13 | Personal-best streak treatment unified; handoff §9.5.10 and demo lane3a | shared dashboard_theme streak rule | runtime/UI/theme tests PASS; shared best-ever treatment | operator aesthetic approval remains; source + headless |
| C14 | Row-offset incorrectness; saved M11.TR/M11.LS notes and operator reaffirmation | `share/v2_runtime.py:1038` | five source-data border/gap controls and six actual paired-question viewport controls PASS at all three sizes | none for reproduced saved layout defect; source-data + actual PTY |
| C15 | Navigation cursor receipt and mode-aware method proof; adversarial R1 | `bin/vim-daily-gate:854`; `share/v2_runtime.py:2884` | ten actual Neovim cursor controls PASS; fourteen actual C31 controls PASS; nine focused mode/type/recovery tests PASS; independent scoped re-review found no remaining high-confidence defect | none for tested receipt/mode/recovery scope; actual PTY + isolated fixtures |
| C16 | Whitespace-preserving grade/preview/gallery; adversarial R2 | M10 flags; runtime/viewer preservation | grading, viewer, strict-byte and native-gate tests PASS; trailing U+3000/U+0020 mutation denied | actual Ghostty display is separate C22; headless + PTY |
| C17 | Tail/row-deletion diffs with onion disabled; adversarial R3 | viewer union-extent diff | viewer and native raster deletion-tail/removed-row controls PASS | none for diff extent; headless + PTY |
| C18 | Named display/pixel coordinates; adversarial R4 | `share/v2_runtime.py:3058`; native metric raster | wide actual receipt and display-column diagnostic PASS; native advances/registration tests PASS | artist-intent approval is separate; headless + actual PTY |
| C19 | GM/ER/06 art rows remain separate and borders align; feedback 00:55/01:16/01:32 on 10-01 | authored GM/ER/06 box rows; question renderer | course stable-inner-width checks and quality 491 PASS; source-history and saved-offset actual routes PASS at all three sizes | none for tested source-data alignment; headless + actual PTY |
| C20 | Correct target / missing taught command explanation plus command colours; M0.SL feedback 17:30 on 10-01 | runtime target-correct message and focal command ledger | grading/style tests: result ✓/method ✗ distinction; actual GP/BR/ER correct-target controls say TARGET CORRECT and offer instant retry; used commands green, missing focal commands red, NO_COLOR | none for tested diagnostics; headless + actual PTY |
| C21 | Strict Shift_JIS/CP932 tutor import/export; handoff §9.7 | `share/sjis_authoring.py`; `share/sjis_tutor.py`; bin helper | 15 backend + 5 lifecycle tests PASS; strict import/export, CP932 duplicate bytes, overwrite/stale/font controls | none for tested byte/lifecycle boundary; headless |
| C22 | Native Saitamaar terminal preview before credit; handoff §9.7 and Ghostty selection | `share/sjis_terminal.py`; `share/native_window_route.py`; gate re-entry | six actual final-runtime .77 M10.06/M10.REWARD Ghostty runs pass at all three sizes: four native panels, real edit, after-question, held PRACTICE COMPLETE, all eight timed frames and owned-window closure; thirteen routing controls PASS; parent/global options restored | operator contour approval remains; actual uncredited-practice grade and result, not learner mastery |
| C23 | Separate transcription and visual/join acceptance; handoff §9.7 | native transcription/raster/registration gates | connected M10: undisplayed exact denied; displayed exact accepted; equal-pixel blank-tail mutation denied | human contour/join approval remains; connected protocol fixture |
| C24 | Substantive original avatar options Lv3–Lv7; handoff §9.6 | `share/avatar_options.py` | 15 original Lv3–7 candidates; option/style tests PASS; archived avatars preserved | operator selection and aesthetic approval remain; source + headless |
| C25 | Full final suite and headed 80×24 / 100×36 / 188×49; handoff §9.8 | final suite and three-size matrix | frozen d27b95b1/.77: clean/personal 311 lessons/270 primary effects and 296 reviews PASS; 90 non-native, 30 history, 57 non-native endcap, six saved-offset, 24 changed-card and six actual Ghostty routes PASS; Textual/first-reward, catch-up, cursor and adversarial controls PASS | none for specified integration matrix; independent mode/receipt re-review is scoped, not exhaustive Vim certification; actual PTY + clean/personal Neovim |
| C26 | Textual lessons/results; operator answer 10-01 | `share/lesson_tui.py`; runtime routes | actual lesson/source-motion/result-reward/Next/Watch/dashboard/feedback/Close routes PASS at 80×24, 100×36 and 188×49 | none for exercised routes; headless + actual PTY |
| C27 | Repeat the same lesson; M0.L0 feedback 17:57 | gate repeat/practice routing; failed-result retry bridge | actual failed Repeat and credited practice return to the same card at all three sizes; practice does not award another event | none for exercised Repeat routes; actual PTY |
| C28 | Demonstrate navigation rather than label a static frame animation; M0.L0/F0 feedback | `share/lesson_tui.py:152`; runtime truthful viewer kinds | navigation overlays preserve canonical rows; still-study is not animation; source poses have separate tab and m key | none for truthfulness/controls in Pilot; source + headless |
| C29 | M11.02 lesson critique; feedback 17:54 | M11.02 prompt; still-study mode; separate source motion | copy complete missile as second redraw candidate, not invented animation; all variants and source-motion controls PASS | operator teaching preference remains; source + headless |
| C30 | All 16 legacy parity gaps; disposition ledger | 17 new guided/hidden pairs; disposition table | 10 course tests PASS, including 68 clean Neovim paths; all 46 legacy IDs adapted | not a learner mastery claim; source + clean Neovim |
| C31 | Correct target + actual taught commands used anywhere passes, including reordered/exploratory input; never exact recipe order; operator addendum and saved note 18 | `share/method_policy.py`; runtime unordered atomic commands and focal ledger; UT/UTH two-take art | eleven policy tests and fourteen actual gate controls PASS; genuine Normal/Visual/register/block commands accepted; Insert/Ex/search/Visual-history impostors denied; nine focused mode/type/owned-recovery tests PASS | none for tested policy boundary; exhaustive Vim interpreter is not claimed; source + actual gate PTY + isolated recovery fixture |
| C32 | Learner reaches a multi-frame art reward on the actual result page; report eligible lessons and first encounter; operator addendum | `share/lesson_tui.py`; runtime successful-result reward lane | actual .77 M0.P0 conceptual grade from empty isolated state reaches all eight module frames on the default result panel at all three sizes; all 311 cards carry module rewards | none for reached M0 reward; actual grade + result-page PTY, not direct player fixture |
| C33 | Reject invented takes inside credited art; handoff §12 at operator request | ten source-faithful M11 history cards, reviews, diagrams and actual recipe-step gate | .77 fourteen positive/negative controls PASS; independent UR/UTH literal-source audit; all ten source-history cards pass 30 actual routes on final runtime | none for expanded ten-card scope; source + clean Neovim + actual PTY |
| C34 | Substantive whole-module animation content, at least eight frames per module, plus retroactive M0/M11 reward and gallery; handoff §12 | `share/module_animations.py`; generator endcaps; runtime result/startup/gallery | 20 labelled original eight-frame sequences with at least six distinct poses; 20 clean-Neovim endcap recipes PASS; 57 non-native endcap and three actual Ghostty M10.REWARD routes PASS; six catch-up controls PASS; first reached M0.P0 plays all eight frames at all three sizes | operator aesthetic acceptance remains; no learner-state seeding; source + actual grade/result PTY + copied-state catch-up |
| C35 | Top-priority reaffirmation of rejected `(_!,o)` takes, with stable live attempts and non-null event revision; operator follow-up 10-02 | C33 source-frame lane; `share/curriculum_publish.py`; runtime launch lock, bound identity and attempt snapshots | ten publication/identity/preservation and thirteen native handoff controls pass; nonce-bound child-load acknowledgement, non-TTY deck locks and missing/active-lock refusal are implemented; actual .77 operator events retain exact contracts | no ordinary-path lock gap remains in exercised controls; arbitrary hard-kill crash resilience is not certified; old events and rejected strips remain intact; no `r!` workaround |

## Operator-only boundaries

- Commit/push remains unauthorized. Foreign demo files remain untouched.
- The operator selected Ghostty terminal rendering. Browser display is optional.
- The operator selected Textual lessons and results as well as the dashboard.
- Pink-purple palette visual acceptance, avatar selection, level cut-offs, signature placement,
  GitHub feedback target/auth and foreign-demo commit choices remain explicit.
- Public redistribution permission for borrowed source-art excerpts remains
  unresolved. Local integration proof does not grant publication permission.
- Do not equate course-source implementation with the operator completing the
  learning path. Never seed successful progress into real learner state.

## Evidence and provenance

The root owns this ledger, `FAILURE_LOG.md` and final handoff updates. Workers
own disjoint source lanes and return one final receipt each. Product findings
remain in the tutor records; skill observations use the pinned observer owner.

C35 is the operator's new tracking reference for the original §12 C33
requirement. Both rows remain visible. C34 owns animation content; neither
numbering change discards the source-art rejection.

Source documents: handoff §9/§10, adversarial review R1–R4, read-only
`share/demo_notes.json`, and `/Users/r/.local/state/vim-daily/feedback.jsonl`.
Legacy command parity is separately tracked in
`share/LEGACY_CURRICULUM_DISPOSITION.md`. The former 16 gaps now have executable
paths with guided/hidden effects and changed-art reviews; vocabulary alone is
not accepted as parity.

Initial protected foreign-file SHA-256:

- `share/demo_notes.json`: `f34e114f31cc58634b1688e4db05714dd3715e6a987ea356adfb8a419a3e88c6`
- `share/demo_ui_proposals.py`: `ee0b397e054e431cc1a997144aafcfab6610a315479d4b9e18bd6b895b5d4883`

The requirement rows above are the current scoped implementation and proof
record. Historical sections retain their original source snapshots and failures.

## Current .77 integration — specified engineering matrix complete

Installed revision: `2026-10-02.77`, 311 cards and 491 paired questions.
Every successful result card carries its whole module's eight-frame sequence;
all 20 sequences have at least six distinct poses. M0 and M11 each have eight
distinct poses. The first encounter is M0.P0, not the end-of-module reward
card. The first M11 encounter is M11.01. Failed attempts do not award this
successful-result reward. The older eligible-source-motion table below is a
separate credited-reference lane, not the current result-reward frame count.

The three formerly repeated primary/review studies are corrected in .77.
M4.BD deletes exactly two columns while preserving both outer contours.
M6.DDP reviews swap genuinely different authored rows. M8.PAD reviews pad
genuinely different authored studies with O and dot. Five focused controls
include a repeated-build mutation negative; the combined source-history,
endcap, question and authored-review suite passes 29 controls. Generation is
deterministic across repeated builds, and installed/source equality passes.

Current content SHA-256:

| File | SHA-256 |
|---|---|
| `share/curriculum-v2.json` | `f1097d008bb47d01623a992f2389e4e323cb1169dae928ac21c0cf4736cbf39e` |
| `share/gen_curriculum_v2.py` | `ab3acb74369e8532cd9097d0ea930529a56734ffc06a7708d030f1fcfa2650d5` |
| `share/stone_story_variants.py` | `955df41d20861e792386a471671045b2f49c5218ecae235c18c923a949fd44dd` |
| `share/authored_review_variants.py` | `4821e876fbed49bff32a9d6222d73a03d2410ba509be39008f3a2ffa2ab553ad` |

Final executed runtime SHA-256:

| File | SHA-256 |
|---|---|
| `share/v2_runtime.py` | `d27b95b1876a71cc06076f9eb9aff82611605344c886f307a701d5e509c8e5c7` |
| `bin/vim-daily-gate` | `e015fa2206fff9533132ff1af518d5d18fd48f26c25c064bc1bd46bb86527659` |
| `share/test_typed_input_modes.py` | `b11dcd43500250c51d1f19f84e962896089513b4361d585fa3620676a86c92e3` |
| `share/test_c31_real.py` | `24a3ca7cfc7d6a17cbe7b60d7ce336c63326332b38953a432a71a73e17d7e7e8` |

Final terminal collection, 2026-10-02 10:10 UTC, all exited 0:

- `test_tmux_v2_routes.py --without-native-display`: 90 routes across the
  three sizes. Its three explicit M10.06 exclusions are not native proof.
- The same harness with `--history-source`, `--endcaps`, and `--saved-offsets`:
  30, 57 and six routes respectively.
- Direct changed-card matrix: 24 routes for M4.BD/BDH, M6.DDP/DDPH,
  M8.PAD/PADH and M15.ZP/ZPH.
- `test_native_window_route_real.py --textual`: M10.06 and M10.REWARD at all
  three sizes in actual Ghostty. Each completed its real uncredited-practice
  edit/grade, four native panels, eight reward frames, held completion,
  owned-window cleanup and exact option restoration.
- Actual Textual routes and the first M0.P0 reward: each passes all three
  sizes. Six copied-progress catch-up controls and ten actual cursor controls
  pass. Tests do not seed real learner progress.
- Clean and personal `test_v2.py --real`: each passes 311 executable cards
  and 270 primary effects. `test_review_effects.py` passes its two tests,
  covering 296 changed-art review effects.
- Fourteen actual C31 gate controls pass. The independent read-only final
  review found no remaining high-confidence false accept/reject in its
  mode, receipt and recovery scope. This is not exhaustive Vim certification.
- Fresh mode/native-route/publication/adversarial pytest batch: 39 tests and
  three subtests pass. Fresh history/module-animation/authored-review batch:
  20 tests pass. The standalone quality gate passes all 491 questions.
- Repeated builds equal each other and installed JSON. All 311 cards retain
  whole-module rewards. Protected foreign-file hashes still equal their
  initial values. `git diff --check` passes.

Typed commands retain their actual modes. Fresh production Neovim attempts
with missing or malformed typed-input evidence cannot fall back to scriptout.
Cold recovery requires the original card, BEFORE rows and cursor nonce.
Legacy artifacts remain checkpointed, not relabelled. Normal `r` consumes its
mode-R argument only after an observed owning command. Visual `g+` is not
Normal history evidence. Genuine named-register Visual copy and block `zy`/`zp`
remain accepted. C31 compares unordered atomic command presence, not a recipe.

The engineering matrix closes C25 for this snapshot. Human contour, palette,
avatar and teaching preferences remain operator decisions. No commit or push
was made. Real learning-path completion is not claimed.

## Historical .77 grading repair stages — not final-source receipts

The earlier frozen grading recheck used runtime
`750e3ec0b760bad782192d96dcbdab7741b81320069d6c08ad7e3204ded93631`
and gate `e015fa2206fff9533132ff1af518d5d18fd48f26c25c064bc1bd46bb86527659`.
Typed receipts retain actual mode boundaries and fresh production Neovim
attempts cannot fall back to scriptout when that receipt is missing. Eleven
actual C31 controls pass, including legitimate single-character `r` and the
Ex/Insert exploit denial. The actual `r` argument reports mode `R`; only a
witnessed owning command can consume it. Five focused mode tests pass. The
fresh corrected matrices and independent review remain pending at this
checkpoint. The older runtime receipts below are historical.

The .77 collection passed broad clean/personal effects, 296 review effects,
90 non-native routes, 57 non-native endcaps, 30 source-history routes, six
saved-offset question viewports, actual Textual/first-reward routes, catch-up
controls and six actual Ghostty M10.06/M10.REWARD routes. Native child load
acknowledgement is repaired, with thirteen routing and ten publication controls.
These receipts used runtime `8ab7ade1fa43ce3406096a8fa4240c3bf79b393511517a35d27e94feba9e23ae`.

C25 remains open: the focused changed-card run exposed a correct-target
M6.DDPH rejection caused by WhichKey's replayed operator input. A nonce-bound
typed-input/mode receipt and narrowly scoped pending-operator replay handling
now pass the actual 80×24 reproduction and all nine actual C31 controls.
Fresh three-size changed-card/full-route/native runs and an independent
grading audit are pending. Neither a passing isolated case nor the earlier
runtime's broad receipt is relabelled final-source certification.

The pre-mode-repair runtime passed all 18 changed-card cases and six dedicated
Ghostty cases. Its new broad batch omitted `--without-native-display` and
therefore failed at the unsupported nested M10.06 transport after M9.06;
that batch is not certified. The independent review also found that the reader
discarded recorded mode boundaries (`:startinsert` could launder Insert `ddp`)
and fell back to scriptout when typed schema was missing. Both fixes remain
with the grading owner. C25 stays open until their real negative controls and
the corrected broad invocation pass.

## Historical .71 C31/C32 and native-display receipts

Historical generated revision: `2026-10-01.71`. It contains 20 modules, 291 cards,
250 primary edit recipes, 61 concept/check surfaces, 471 paired questions,
148 two-variant review banks and 75 required reviews. Course-source completion
does not mean the learner has completed this course.

The fresh clean-source suite passes 291 lessons and 250 primary recipes.
The operation-specific sweep passes all 296 review/transfer variant effects.
The worker corrected ten initially failing variant effects in M3.Y0, M4.TRIM,
M6.DDP, M8.O and M8.PAD. Generated/source equality is checked independently.
The .71 real-user-config suite also passed all 291 lessons and 250 primary
recipes. The .71 non-native matrices passed 100×36 and 188×49. A later full
80×24 run failed M3.06; an isolated rerun and a fresh full 30-route non-native
80×24 matrix passed, without an established cause for the prior failure.
C25 remains open for a fresh complete final-source matrix after C33/C34.

`test_c31_real.py` drives nine actual Neovim attempts through production
artifact creation, keylogs, cursor receipts, questions, grading and events.
It injects neither targets nor successful events. GP accepts g+ before the
edit; direct replacement and Insert text containing g+ get target-correct
retry. DWH accepts another row-positioning route. M18.05 accepts G instead of
the example 8G. BR rejects Visual u as Normal undo. ER rejects Visual
`:earlier` with its implicit range as Normal history travel. The latter two
saved artifacts equal their targets, so these are real method-only controls.
Two added controls accept comparison positioning through :4/:8 and reject
an Insert-mode register paste as a Replace-mode paste. All nine actual
controls pass. The eleven policy tests also pass.
An actual taught command later undone still counts under C31. There is no
effect quota or transcript-order requirement.

`test_textual_routes_real.py --first-reward` starts with empty isolated state,
grades M0.P0's actual question, then observes distinct authored rows after the
production result page mounts. It passes at all three sizes. This is not a
seeded successful progress fixture. Rewards use declared 0.35-second tutorial
pacing, not an asserted source FPS. The first course encounter is M0.P0;
the first M11 encounter is M11.01.

| Eligible result cards | Frames |
|---|---|
| M0.P0, M0.L0, M0.F0, M0.01, M0.YP, M0.O, M0.SR, M0.02, M0.03, M0.04, M0.T, M0.DG, M0.DGH, M0.05, M0.SL, M0.06, M0.07, M0.08 | 3 |
| M11.01, M11.02, M11.03, M11.UR, M11.WS, M11.LS, M11.CUC, M11.CC, M11.TR, M11.ER, M11.UE, M11.04, M11.AT, M11.05, M11.WSH, M11.06, M11.07, M11.COL, M11.INS, M11.VE, M11.08 | 4 |
| M11.BR, M11.GM, M11.GP, M11.UG, M11.UT | 3 |
| M11.UB, M11.UTH | 2 |

The 46 credited source-art rewards remain a separate reference lane. In .72,
the default successful Feedback panel plays the original whole-module sequence;
space pauses and h/l step. Source art is not relabelled as learner output.
Failed attempts do not receive this successful-result reward.

`test_sjis_ghostty_real.py` and `--tmux` both received actual OK responses
bound to all four production PNG hashes. Font SHA-256 remains
`592bf6be803ed76311841b95a10b20db3df0ec693a15f858757d47420b9b3a28`,
at 16 px and 17 px pitch. The tmux proof owns a new disposable server; it
changes no live server setting. These ACKs are actual transport evidence,
not a human confirmation, passing M10 grade or contour/join approval.

Root independently inspected and reran `test_module_ghostty_real.py` directly
and with `--tmux`. Both runs acknowledged all eight canonical M10 frames.
The harness now uses actual timed holds, not a no-op timing callback. The
normal-pane run restored its inherited-off pane state and left window/global
settings off. The separate ownership-validated popup transport still times
out. Full native learner-route proof remains open; transport is not a grade.

Source identities at this checkpoint (SHA-256):

| File | SHA-256 |
|---|---|
| `bin/vim-daily-gate` | `cf418677456701e2f52cc48929a323dcd248243db7be1e4b8a0237cfba41744f` |
| `share/gen_curriculum_v2.py` | `d575769f16021a360e44df660694f303090ae97eb49f007ced19f9e6c12197aa` |
| `share/curriculum-v2.json` | `43fdb34671afd135cb34a516071577103cbc4efe97440baea733651cc784aa6c` |
| `share/v2_runtime.py` | `203300ee1ddf5aa30af90fc1eca258e81433b200d0418b737f0223ce8e146f0b` |
| `share/method_policy.py` | `532fc263763dac3f3d264608c5b1d5c99d8a7ef6d038f1d35f403ea60caadecf` |
| `share/lesson_tui.py` | `60bdf816f879dcf221618abfa69bd2525a24bc4255b808d35583cdfcaece9648` |
| `share/sjis_terminal.py` | `b5af3f551ff164e53b37820d08d42767b083e068395cc7121e7b8e99d7a274a4` |

Latest intake read all 18 saved feedback rows, including the three later
10-01 entries for M11.02, M0.L0 and M0.F0. Source notes are the reproduction
input; screenshots are not a prerequisite. Correct editor commands do not
establish correct question-box layout.

Root checkpoints: backend 15 tests passed; browser/file adapter 5 passed;
terminal 4 passed; six mode/nonce/box regressions passed; connected M10 runtime
control passed for undisplayed exact text, displayed exact text, and trailing
U+3000/U+0020 mutation. HTTP and terminal ACK emitters in those tests are marked
protocol fixtures, not actual Ghostty display or operator acceptance. The new
Textual screen shell passed a headless Pilot at all three sizes before route
integration; that is not a completed Textual migration.

`test_cursor_real.py` exposed the ordinary `:wq` receipt loss in an actual
clean Neovim PTY. This supersedes any implication that mock receipts proved
interactive navigation credit. The contact guard initially refused the
concrete defect message. After that window cleared, the root delivered the
ordinary-exit falsifier and direct/wide positive contrast to the active UI
owner. No overlapping receipt edit was made. See VD-81 for the required repair.
