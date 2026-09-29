# Curriculum v2 — animation projects, Vim fluency, and durable mastery

Status: revision `.54` contains 215 cards and 395 manually authored questions.
The clean-Neovim suite passes all 174 recipe-bearing paths. The base headed
popup path renders the stage tree at 80x24, 100x36, and 188x49; the full
post-M2 route matrix and real-config suite remain separate acceptance evidence.
Stage ownership/order is implemented; manual disposition and migration of
older temporal content still assigned to S0-S7 is not complete. The
runtime/data owners are `share/v2_runtime.py`,
`share/gen_curriculum_v2.py`, and generated `share/curriculum-v2.json`. The old
46-drill path remains available and its state is not migrated destructively.
Implementation history is in [CURRICULUM_V2_PLAN.md](CURRICULUM_V2_PLAN.md).
The longer-form proposed hour-by-hour sequence is in
[CURRICULUM_V2_CARD_CATALOG.md](CURRICULUM_V2_CARD_CATALOG.md); it is an authoring
roadmap retained as `roadmap_contract`, not a claim that each roadmap outcome is
the implemented card. The generated card's `prompt`, `start`, `target`, question
IDs, methods, and tests are the normative implemented contract.
The open still-stage content migration is enumerated card by card in
[`audits/stage-content-disposition-v35.md`](audits/stage-content-disposition-v35.md).

## 1. Product contract

An hourly popup is the next short step in an animation project, not a random worksheet.
The learner uses real Neovim to alter a persistent plain-text frame strip. Every module
mixes guided drawing, independent editing, paired conceptual retrieval, a second way to make
the same edit, and a check on an unfamiliar variant. The skill tree advances only on
demonstrated understanding and a verified artifact. A streak remains optional
context, never the definition of mastery.

Every edit surface keeps five things visible or one toggle away: `DO THIS`, the
complete target artifact, an action-level hint, the current Neovim mode, and an
F1 movement/edit cheat sheet. Independent, comparison, transfer, review, and
module-check edits hide the exact command sequence—not the target. The art
window's task bar must survive scrolling the read-only teaching split. A result
page must place `YOU TYPED` beside `THE RECIPE ASKS FOR`, including at 80×24;
a one-line actual/taught summary is not a substitute for the ledger.

Every conceptual item is cross-domain by construction. Its visible `ANIMATION`
half asks the learner to read motion or authoring evidence; its `NEOVIM` half asks
for the bounded edit, scope, or command decision that realizes or preserves that
motion. Every answer choice answers both halves, including distractors with only
one half correct, so animation vocabulary alone and Vim trivia alone are both
insufficient for credit.

The two things learned together are (1) Vim/Neovim's editing grammar and (2) how to
make readable animation with monospaced glyphs. Touch typing is practiced inside those
edits, not split into a separate typing product (existing [VD-01](../FAILURE_LOG.md)).

Non-goals: importing a browser trainer engine; reproducing proprietary lesson prose;
making every popup a long art session; scoring speed as skill; automatically inventing
glyph in-betweens; or replacing the user's private practice ledger with a cloud account.

## 2. Evidence ledger — current state, not inferred intent

The current working tree is dirty and contains user-owned changes. These observations
refer to its 2026-09-26 state; no existing user edits were reverted to prepare this spec.

| ID | Observed fact and direct evidence | Product consequence |
|---|---|---|
| E01 | Legacy `share/curriculum.json:10-20` has only three tier thresholds, 0/8/16 lifetime passes; legacy `unlocked` at `bin/vim-daily-gate:325-328` checks total passes, not prerequisites. | A learner could unlock later legacy material by repeating unrelated easy drills. V2 supersedes this route with module prerequisites. |
| E02 | Legacy `bin/vim-daily-gate:331-355` chooses by `passed - failed`; the three-item recency exclusion sorts `last`, which legacy `do_drill` sets only on success (`:723-750`). | A failed legacy drill can reappear after one intervening slot, while repeats remain exact. V2 reviews use item variants and explicit due times. |
| E03 | Legacy `bin/vim-daily-gate:390-427` defines eight fixed questions only for `grammar` and `modes`; `:879-881` runs them only by explicit `--quiz`; `:469-474` stores best score, total, and last date. | The legacy bank has no animation-reading, interstitial, or unlock role. V2 provides 395 item-level questions and check evidence. |
| E04 | Legacy `bin/vim-daily-gate:499-546` prints the full concept, recipe, and visible target before an edit. | V2 keeps the visible target on every edit. Guided cards also expose the recipe; retrieval/check cards expose a non-key hint while withholding only the exact command answer. |
| E05 | Legacy `bin/vim-daily-gate:723-750` writes a date-and-drill-specific lesson file and records one drill result. | V2 adds authoritative continuing `strip.txt`, transfer, manifest, checkpoint, and next-card state. |
| E06 | Legacy `bin/vim-daily-gate:358-383` calls one-pass coverage `concept_mastery`; `:866-903` exposes it in manual export/status. | Legacy evidence remains visible through `--legacy-status`; V2 `--tree` now exposes prerequisite-backed module state. |
| E07 | `share/art.json:5-114` holds all ten Poison Adept walk frames; `share/gen_curriculum.py:447-471` uses only walk1 and walk2 in two isolated tier-3 drills. | The source's ten-frame temporal lesson has not become a continuing draw-along. |
| E08 | `share/test_drills.py:58-105` replays one prescribed recipe per drill against one final target, checks source/size/glyph gates, and has no scheduler/quiz/project assertions. A 2026-09-26 clean-config run passed 46/46. | Recipe passability is a real strength, but it does not establish progression or retention. |
| E09 | `share/gen_curriculum.py:27-37` emits one static block task per call; `:602-615` states a Vimtutor sequence and three broad tiers. Current JSON has 46 drills (23/15/8 by tier). | The existing data spine is a migration asset, not a complete course. |
| E10 | On 2026-09-26 `share/DESIGN.md` still described schema `@1`, 42 drills, and 16/16 acceptance, while the generated legacy curriculum was `@3` with 46. `DESIGN.md:25-50,61-67,99-111` was reconciled on 2026-09-27 and now separates v2 from legacy. | Resolved documentation mismatch; historical counts remain only where explicitly describing an earlier expansion. |
| E11 | `README.md:86-89,217-220` says the art contains all ten walk and seven pyramid frames while also saying the tutorial plates are not redistributed; `share/extract_art.py:34-45` extracts those sequences and `share/art.json:5-114` holds the ten walk entries. | Before expanding published draw-alongs, review the exact existing/extracted content and attribution boundary. This is a documentation/content-inventory tension, not a legal conclusion. |
| E12 | `share/art.json` contains 49 keys (`README.md:86-91`); a static inventory of `a("...")` calls in `share/gen_curriculum.py` finds only 12 distinct loaded art keys. Other drills use hand-built starts/targets or only cite a source. | The archive/library offers more possible visual contexts than the current fixed cards use. This is an opportunity for *review variants*, not a mandate to publish every source excerpt. |

### Source provenance and reading limits

- `A1`: archived Part 1 auto-caption transcript in this operator's sibling archive, `../../ascii-art-archive/collections/y9-2-articles/2026-09-07-stone-story-video-transcripts-media/o5v-NS9o4yc/o5v-NS9o4yc-transcript-timestamped.txt`. Lines 28-45 (00:03:32-00:05:45) describe keyframes first and the 4+4+2 Poison Adept timing. Lines 339-401 (00:52:45-01:01:05) explain references, concept, primary pose, size, plan, keyframes, middle in-betweens, early playback, and polish. Lines 402-410 (01:01:12-01:02:17) cover subtractive authoring and playback reordering. [Video](https://www.youtube.com/watch?v=o5v-NS9o4yc).
- `A2`: archived Part 2 auto-caption transcript, sibling `h6a2BKPHPqA/h6a2BKPHPqA-transcript-timestamped.txt`. Lines 1-5 state the end-to-end draw-along; 59-65 (00:13:18-00:14:56) show midpoint/partial-merge tweening; 87-125 (00:25:20-00:37:55) show stagger, overshoot, dragged arms, occlusion, glyph rotation, and the half-cell limit; 126-141 (00:39:03-00:44:19) show preview, padding, timing, holds, and final testing. [Video](https://www.youtube.com/watch?v=h6a2BKPHPqA).
- `PAGE`: archived `o5v-NS9o4yc/ascii-tutorial-page/02-poison-adept-walk-cycle.txt:1-72` and `06-animation-subtractive.txt:1-80` under the same directory; also the [author's public tutorial page](https://stonestoryrpg.com/ascii_tutorial.html), sections 2, 12, and 13. The archive is third-party reference material, not a grant to redistribute whole plates or transcripts.
- The operator-local `/Users/r/.claude/skills/ascii-art-authoring/SKILL.md:298-458` organizes the same eight-stage animation process and records caption provenance. This spec uses the archived transcripts and page as primary evidence; the skill is a method index, not a separate source of ownership.
- General animation cross-check: [Blender's keyframe taxonomy](https://docs.blender.org/manual/en/latest/animation/keyframes/introduction.html) distinguishes extremes, breakdowns, and moving holds; [Disney Animation](https://www.disneyanimation.com/process/animation/) identifies timing, anticipation, follow-through, and secondary action. These are general principles; no automatic interpolation of ASCII glyph identity is assumed.
- Learning-science basis: [Karpicke and Roediger 2008](https://doi.org/10.1126/science.1152408) supports retrieval after initial success; [Cepeda et al. 2008](https://escholarship.org/uc/item/0kp5q19x) supports spaced rather than massed review. The exact review intervals below are a product hypothesis to test, not a number prescribed by those studies.

Auto-captions in `A1` and `A2` are noisy. Use timestamps plus the archived page/visual
plate for ambiguous glyphs, and do not present reconstructed speech as a verbatim quote.

## 3. Curriculum-source decision

Use the installed Neovim `:Tutor` chapter order as a *command coverage checklist*, not
as copied lesson text. On this machine, `vim-01-beginner.tutor:44-960` covers motion,
insertion, operator/motion grammar, counts, undo, put/change, search/substitute,
file/range operations, copy/paste, options, help, and completion; `vim-02-beginner.tutor:17-242`
covers text objects, registers, and marks. The [official tutor file](https://github.com/neovim/neovim/blob/master/runtime/tutor/en/vim-01-beginner.tutor)
is the stable mapping target. Record exact Neovim help tags for every new technique.

VimHero publicly describes a 50+ lesson, dynamically repeated course with proficiency
tracking; this is useful design comparison, not permission to copy its text or challenges
([site](https://www.vim-hero.com/)). VIM Master has JSON lessons and an explicit
[MIT license](https://github.com/renzorlive/vimmaster/blob/main/LICENSE); OpenVim is
also [MIT licensed](https://github.com/egaga/openvim/blob/master/LICENSE). A later
implementation may import selected *licensed* content only after recording repository
commit, exact files, license notice, transformation, and why it is better than native
content. Do not import VimHero's authored prose, paywalled challenges, or assets.
Likewise do not expand the existing Stone Story excerpts into a new bundled full
plate or video transcript. E11's current content boundary needs a separate review;
the code's MIT license does not decide third-party art rights.

The practical v2 choice is original ASCII-art cards aligned to Neovim tutor nodes,
using the existing `tutor` IDs as migration keys. This permits a full native Neovim
exercise harness and explicit alternative editing methods without browser-emulator
behavior differences. Neovim documents linewise yank/put and `:copy`/`:t` as alternate
copy operations ([change help](https://neovim.io/doc/user/change/)); blockwise `I`,
`A`, and `r` operate across selected columns ([visual help](https://neovim.io/doc/user/visual/));
dot and macros have distinct repeat semantics ([repeat help](https://neovim.io/doc/user/repeat/)).

## 4. Progression model

The implemented main path is strict: `S0 → S1 → … → S7 → A0 → A1 → … → A7`.
P is an optional proportional-Shift_JIS branch unlocked by S5; it is never a
prerequisite for S6. Completion count alone never unlocks a stage.

Modules are project/storage units, while stages are mastery units. Every card has
one `stage_owner`; a pass cannot advance both a still and animation stage. A stage
becomes mastered only when all owned cards pass and every owned
`required_before_mastery` card has a successful changed-art review at stage 1 or
higher. Until then the successor remains locked. This is enforced by the runtime
projection and validated against the actual card inventory.

```text
S0 grid/overwrite → S1 stroke runs → S2 hand mirror → S3 block a still
 → S4 joint heights → S5 variants/palette → S6 layers/seams
 → S7 texture/ground → A0 plan/key poses → A1 extremes/copy-vary
 → A2 in-betweens/onion skin → A3 coherent anchors → A4 timing/holds
 → A5 subtractive build → A6 mirrored return → A7 playback polish
                              ↘ P proportional Shift_JIS (optional after S5)
```

Stage states: `locked → available → learning → check_ready → review_pending → mastered`.
A failed
check returns to `learning` with a named misconception/remediation card. `skip`,
let-through, and forced practice do not award a node. Manual `--drill` remains
available but cannot bypass the module check.

Mastery rule: pass every card owned by the stage, including each module check's
4-of-5 conceptual threshold and verified artifact, then pass the stage's declared
key-hidden changed-art reviews. A failed subpart reschedules only that subpart.
Module completion remains visible, but it cannot override the stage gate.

## 5. Module sequence and lesson inventory

Implemented content is **20 modules / 215 cards**, plus **395 distinct paired
conceptual items** and transfer/review variants. Each card has one
new decision or edit; no popup silently expands into a 45-minute session. A module
shares one `strip.txt` across its eight cards. The table is the authoring order,
not a promise that every user sees all cards on consecutive clock hours.

Every module transfer has two changed-art variants. Variant 1 uses the card's
manually authored paired question; variant 2 owns a different manually authored
question with its own full and compact ASCII evidence. The generator rejects a
later transfer variant that merely inherits the first variant's question.

| Module / artifact | Cards 1-4: introduce, act, contrast | Cards 5-8: transfer, inspect, check | Neovim / source coverage |
|---|---|---|---|
| M0 `spark-loop` | Read and edit a registered three-row spark; copy whole frames; brighten the core and widen only the flare rays. | Compare counted and addressed whole-frame copies; transfer to a comet; add a purposeful hold and settle; check the five-frame loop. | Tutor 1.1-1.6; whole-frame copy; ascii-art-authoring §§1,9. |
| M1 `line-run` | Edit one joint in a complete three-row anchored contour; copy the full frame; hand-author its descending counterpart. | Compare local-dot and bounded-substitute material edits; transfer to changed/mirrored contours; return to the rising pose. | Tutor 2.1, 2.4, 4.2; ascii-art-authoring §§4.4,4.7. |
| M2 `shape-edit` | Remove a note without damaging a four-row face; copy the full contour; change only the acting eye. | Compare local and matched eye edits; transfer to unfamiliar faces; add a registered closed-eye frame. | Tutor 2.1-3.4; ascii-art-authoring §§2,4.6. |
| M3 `pose-copy` | Approve one eye inside a six-row body; copy all six rows; change only the eye in the copy. | Compare `6yy/p` with addressed `:t`; transfer the whole-pose intention; add a final accent without body drift. | Tutor 3.1, 6.4; ascii-art-authoring §§9c-9f. |
| M4 `rotation-tween` | Author complete diagonal backslash/forward-slash extremes around one pivot; copy full three-row frames; insert the vertical midpoint. | Compare two local redraw strategies for separated diagonal cells; use block scope only on a true aligned column; transfer to changed extremes. | Tutor Visual block and `:t`; ascii-art-authoring §§4.4,9f-9g. |
| M5 `layered-scene` | Break a visible background seam directly below a foreground pivot in a seven-row composite; copy the full frame. | Swing only the foreground while the registered pivot break stays fixed; compare counted/addressed whole-frame return; transfer seam repair. | Neovim range copy; ascii-art-authoring §§3,11. |
| M6 `pyramid-build` | Finish a five-row keyframe; copy it; subtract by blanking a unit without deleting the row. | Compare full-frame copies; reorder exact five-line ranges from authoring order into forward playback; check equal bounds. | Neovim `:copy`/`:move`; ascii-art-authoring §10. |
| M7 `timed-pyramid` | Continue M6; duplicate a full incomplete frame as an anticipation hold; create a reviewable settle duplicate. | Repeat one held-frame timing edit with `.`, compare macro/global-normal material polish across every pose, transfer to changed held art, and remove the unjustified duplicate. | Dot, macros, `:global`/`:normal`; ascii-art-authoring §10. |
| M8 `walk-study` | Plant a foot in a complete five-row walker; copy the pose; move legs and secondary arm without torso drift. | Append the opposite contact, compare local/scoped arm edits, transfer foot contact, and close a four-frame walk. | Contact/secondary-motion method reference; ascii-art-authoring §§9g-10. |
| M9 `original-micro` | Plan an original three-row bounce; commit the high pose; copy its registered rails/ground and establish the squash extreme before the middle. | Insert the falling pose by direct authoring and copy-then-vary; transfer to changed bounds; add rebound overshoot and inspect the loop settle. | Planning, keyframes, squash/overshoot; ascii-art-authoring §§9-10. |
| M10 `sjis-puff-tween` | Complete a three-row proportional lobe, derive a wider arch extreme, and add a bounded hatched impact pose. | Compare complete-frame copy methods; hold the impact; settle to the lobe; transfer to changed proportional contours while separating exact text grading from Saitamaar visual judgment. | `sjis_corpus_findings.v1.json`; ascii-art-authoring §§9-10,15.3-15.7; viewer commit `661b220`. |
| M11 `redraw-lab` | Overwrite a two-cell roof band with `R`, copy the full three-row pose, and use a real undo/redo cycle while developing the slack extreme. | Compare local and row-scoped indicator edits; transfer the redraw; align motion-blur trails past end-of-line with `virtualedit=all`, exact-column motion, and dot repeat. | Neovim `R`, `u`/`<C-r>`, `virtualedit`, `N\|`; ascii-art-authoring §§4.4,9h-10. |
| M12 `joint-sweep` | Accent the left joint with `t`, copy the complete pose, then approach its right partner backward with `T`. | Stagger the lower pair with `;`/`,`, compare repeated search with scoped substitution, transfer to changed shells, and author the opposite-side return. This is joint timing, not proof of full-row manual mirroring. | Neovim `t`/`T`/`;`/`,`; ascii-art-authoring §10. |
| M13 `texture-pulse` | Use `W` to reach whitespace-separated punctuation clusters, copy the complete pose, then advance the acting accent across texture WORDs. | Expand the pulse with `E`, counted `W`, and `B`; compare landmark edits with a scoped material substitution; transfer to changed clusters and author the opposite-side loop exit. | Neovim `W`/`B`/`E`; ascii-art-authoring §§4.4,10. |
| M14 `variant-palette` | Store a visible glyph in a named register and retrieve it through Replace mode; duplicate the complete blank-line-separated frame with `yap`. | Change the copied variant from the same palette, compare paragraph-object and addressed-range copies, transfer to changed shells, navigate frames with `}`, and return the third variant to its first material. | Neovim `yap`, `}`, named registers, insert-mode `<C-r>` under Replace mode; ascii-art-authoring §§1.7,2,3. |
| M15 `texture-ground` | Offset one repeated brick-material row by one declared cell and copy its complete material stack. | Lighten dither by bounded replacement, compare block `$A` with range append, transfer the offset, and record/replay a dither macro while the angled ground shadow remains fixed. | Neovim `shiftwidth=1`, `>>`, block `$A`, range `:s`, `q`/`@`; ascii-art-authoring §§3,4,6,8. |
| M16 `key-pose-plan` | Verify a playback-size primary key pose, write frame/FPS identity, and import the saved plate with `:read %`. | Copy and count-number complete plan blocks, compare addressed `:m` with linewise delete/put, transfer numeric labels, and append a fourth planned key pose. | Neovim `:read`, `:t`, `:m`, `<C-a>`; ascii-art-authoring §§2,7.1 and archived Part 1 planning sequence. |
| M17 `coherent-anchors` | Correct homologous eye anchors across changing shells with `/`, `n`, and dot, then develop a fourth contour around the stable cell. | Compare search-repeat with `:global ... normal`, transfer to unfamiliar shells, and record/replay a search-bearing macro across four proven anchors. | Neovim `/`, `n`, `.`, `:global`, `:normal`, `q`/`@`; ascii-art-authoring §§7.3,7.4,8.1. |
| M18 `hand-mirrored-return` | Hand-author all directional rows of a full mirror and a one-cell return overshoot; no byte reversal or art-generating expression is accepted. | Compare manual check markers with validation-only `\=`/`getline()`, transfer the full hand mirror, and reuse approved ranges in reverse around a declared turnaround hold. | Neovim `C`, `:sub-replace-expression` as check only, range `:t`; ascii-art-authoring §§7.2,7.5,8.2. |

M6-M7 continue the same pyramid strip. M8 uses an original compact walker while
the Poison Adept material remains a method reference, not a redistributed plate.
M9 uses an original bounded bounce study. Exact per-card contracts are in the card
catalog; generated fixtures remain the executable grading authority.

An early guided card may preview a later command (one-line `yy/p` in M0, blockwise
editing in M4). Preview does not award the later node: independent transfer and its
module check still happen in M3 or M5. This keeps the project coherent without
making the DAG claim premature mastery.

Every eight-card module contains at least two meaning questions, three performed
edits, one compare-method task, one transfer to different art, and one check. A
guided card may show a recipe; an independent/check card hides both the answer and
the target until submission. Repeated paradigm prose is collapsed to a one-line cue
with an explicit `show why` expansion; the current full prose remains available.

### Legacy drill migration inventory

This assigns each of the 46 current stable IDs one *primary* v2 home. It is a
content-audit map, not automatic mastery credit: a past v1 pass remains visible
but cannot by itself pass a new module check. Some existing exercises can be
adapted as review or guided cards; others need a new project-aware variant.

| Module | Existing IDs to adapt or retain (46 total, each listed once) |
|---|---|
| M0 | `move-x`, `undo`, `open-line`, `put`, `ant-drop` |
| M1 | `count-motion`, `search`, `find-char`, `replace-char`, `mirror-run`, `cheer-eyes`, `append` |
| M2 | `delete-word`, `delete-eol`, `delete-line`, `change-word`, `change-eol`, `substitute` |
| M3 | `yank-put`, `named-register`, `yank-register-0`, `symbol-table`, `centipede-hold` |
| M4 | `block-insert`, `block-append`, `block-replace` |
| M5 | `match-paren`, `text-object-paren`, `paragraph-object`, `visual-delete`, `block-erase`, `break-seam`, `join`, `candle-join` |
| M6 | `playback-order`, `ex-copy` |
| M7 | `toggle-case`, `macro`, `dot-repeat`, `range-normal`, `macro-frames`, `substitute-all` |
| M8 | `hold-frame`, `tween-frame`, `pad-frames`, `marks` |
| M9 | None: original capstone content, not a recycled recipe. |

This inventory is derived from the generated `share/curriculum.json` `drills[*].id`
list. The executable status and remaining command-level gaps are recorded in
`LEGACY_CURRICULUM_DISPOSITION.md`; its test-enforced totals are 28 `adapted`,
7 `partial`, and 11 `retained-only`. Eighteen rows remain gaps. “Primary home” must not be read as full
command parity.

## 6. Multiple valid Neovim methods are curriculum content

Teach one transparent method first, then a method that scales when the *task shape*
changes. Do not claim a more complex command is universally faster; measure on the
actual text and let readability, repeatability, and error risk count. A method-contrast
card must (a) state the same desired buffer outcome, (b) run both real Neovim paths,
(c) show the key/decision tradeoff, and (d) ask when the alternate wins.

| Editing intention | First path | Later/alternative path | Concept check |
|---|---|---|---|
| Duplicate one row/frame | `yy` then `p`, or counted `3yy` then `p` | Visual-line selection and `y/p`, or range-scoped `:t` | Which preserves the whole three-row pose without manually selecting it? |
| Change one moving cell | Navigate then `r<char>` | `f<char>r<char>` for a landmark, then `.` on like-positioned rows | Why does untouched glyph pattern matter between frames? |
| Change one column in several frames | Repeat a single-cell `r` | `<C-v>` selection then blockwise `r` | Why is blockwise editing useful here but unnecessary for a single cell? |
| Delete one unit in each copied pyramid pose | `x`/`dd` on one frame | Blockwise deletion, or a recorded macro when the edit includes navigation | Which method scales without deleting lesson instructions above the marker? |
| Make a hold or repeat an edit | Duplicate a frame with `yyp` | Counted put for holds; dot for last change; macro for a multi-action edit | Is an identical frame a deliberate hold or a dead frame? |
| Reorder authored frames | Move one line/block manually | Address-scoped `:m` or a visual selection and move | Why can authoring order differ from playback order? |
| Replace a glyph across a selected region | Repeat `r`/`x` | Scoped `:s` or `:'<,'>normal` where appropriate | What is the blast radius of `%` versus a range? |

The evaluator grades the exact artifact plus any declared method contract. Most
cards permit any bounded edit that reaches the target. A card may additionally
require a captured token pattern and impose a keystroke ceiling when its purpose is
to teach one command family. Compare-method cards accept only one of their two
captured taught paths; an unrecognized path that happens to reach the target does
not establish either method. Transfer/capstone checks use unseen art variants.
Never assert operation mastery because a command string merely appears in an answer
key; coverage comes only from runtime-enforced evidence and later spaced retrieval.

## 7. Question model and sample authored checks

Question data lives beside curriculum data, not as a hard-coded runner dict. Each
item has `id`, `node_ids`, `module_id`, `type`, `prompt`, optional frame/strip
reference, exactly four plausible choices for MC, `correct_choice`, per-choice
misconception feedback, `source_ref`, `difficulty`, `variant_group`, and a revision.
Shuffle choice order while preserving the keyed answer. Persist item-level outcomes,
not only a chapter best score. Check types: motion interpretation, predicted buffer,
choose editing method, key order, find the changed cell, compare two animations,
error diagnosis, and short key-hidden edit. A free-text explanation can be retained
as self-check but must not be machine-marked as mastery without a reliable rubric.

Examples to author and validate, not a complete 100-item bank:

1. Show two walk frames. “What changed: leg pose, staff position, body size, or
   layer order?” Follow with “what motion does this read as?” and explanation.
2. “To duplicate this *entire six-line pose*, then replace only the accent in the
   copy, which sequence keeps the original unchanged?” Include four complete
   sequences with realistic `yy`, `6yy`, `p`, `r`, and delete mistakes.
3. “Three copied frames need the same column replaced. Which method expresses a
   rectangle?” Distractors must be viable for *different* task shapes, not jokes.
4. “These two frames have identical legs but different staff positions. What does
   that offset do to the motion?” Cite A1 00:05:13-00:05:45 in author notes.
5. “Is frame 4 a purposeful hold or an accidental dead frame? What evidence in
   the timing plan decides?” Cite A2 00:27:48 and 00:31:09.
6. “The moving arm ends before the torso. Which frame change adds follow-through?”
   Cite A2 00:25:20-00:28:42.
7. “You want only the project block changed, not the lesson prose. Which Ex
   range is safe?” Test against the actual file layout, not imagined offsets.

Questions occur before the answer is exposed, between edit steps when a decision
matters, and in the module check. On a wrong answer, explain the specific
misconception and present a *new* variant later; do not immediately replay the
same fixed four choices until memorized. Early modules may allow one hint; a
check records whether a hint was used and does not award independent mastery.

## 8. Files, state, scheduling, and progress display

The persistent source of truth is an append-only event ledger plus versioned
artifact checkpoints, under the private XDG state directory. Existing daily logs
remain readable and migration never deletes them. Proposed paths:

```text
$XDG_STATE_HOME/vim-daily/events-v2.jsonl
$XDG_STATE_HOME/vim-daily/progress-v2.json       # rebuildable projection
$XDG_STATE_HOME/vim-daily/projects/M6/strip.txt # learner-owned plain text
$XDG_STATE_HOME/vim-daily/projects/M6/manifest.json
$XDG_STATE_HOME/vim-daily/projects/M6/checkpoints/
$XDG_STATE_HOME/vim-daily/sessions/<id>/lesson.txt
$XDG_STATE_HOME/vim-daily/sessions/<id>/transfer.txt
$XDG_STATE_HOME/vim-daily/sessions/<id>/compare.txt
```

`strip.txt` is the continuing animation. `manifest.json` records frame boundaries,
frame order, target row height, timing/holds, source/provenance, and curriculum
revision. `lesson.txt` is disposable instructions. `transfer.txt` is a separate
unseen subject on which the learner applies the same skill; `compare.txt` shows
the basic and scaled Neovim solutions only *after* an attempt. “Cross-exercise
TXT” is interpreted here as that explicit linked project/transfer/comparison
surface; the formats remain ordinary editable text, not screenshots.

Event fields: `event_id`, time with offset, session ID, curriculum revision,
module/card/node/item/variant IDs, artifact hash before/after, result
(`pass`, `fail`, `skip`, `let_through`, `hint`, `abandon`), attempts, method family,
question choice or answer class, elapsed time (diagnostic only), and next due.
Do not store the full private project in the public repo or export raw keystrokes
by default. Atomically checkpoint `strip.txt` and progress; protect concurrent
launchd/shell/tmux triggers with a single active-session lock. A crash/restart
must resume the same card and preserved strip without double-credit.

Proposed review schedule after first independent pass: a different variant at
+4 hours (or the next eligible session), then +1, +3, +7, and +14 calendar days;
after stable success, longer intervals. A wrong review shortens the interval and
targets the misconception. This is a tunable starting hypothesis, not a
universal memory law. Reviews retrieve *intent/operation* on changed art; each
requires one paired conceptual answer and one exact key-hidden Neovim edit on a
rotated transfer-art variant. They do not replay the exact same rows and choice
ordering. The normal hourly
choice is the next project card; at most one out of four eligible sessions is
a short spaced review, unless a module check is due. Never schedule two
unrelated reviews back-to-back. If no review is due, keep advancing the strip.
The existing cooldown and daily cap still govern prompts, not learning credit.

Visible progress after every result and via `--tree`/`--status`:

```text
M6 Pyramid build  5/8 cards · next: reorder for playback
V3 Copy a pose    mastered ✓  · review due in 3 days
A4 Tween          learning 2/4 evidence pieces
Project           5 frames · 8 rows each · preview available
```

Keep daily streak and all-time count in a secondary line. Add distinct modules
completed, nodes mastered, review retention, animation strips finished, and a
clear next action. Award badges for actual firsts (first independent keyframe,
first midpoint tween, first playable strip, first safe range edit). XP is
optional and capped per unique card/meaningful review, never farmable by
repeating a solved static exercise. No streak loss or speed penalty for a skip.

## 9. Acceptance and falsifiers

1. First run starts M0 at card 1; a pass advances to card 2 in the same
   `strip.txt` on the next due popup. Restart and a missed day preserve it.
2. Completing 16 copies of M0 cannot unlock the Poison Adept. Required DAG
   evidence and module checks, not lifetime count, unlock it.
3. A failed attempt is logged and diagnosed but not selected again unchanged
   after one unrelated success. A later review changes art, decision, or method.
4. A concept question is presented before command-answer disclosure; all four
   choices are plausible, shuffled, and given choice-specific feedback.
5. A module check mixes at least one motion-meaning question, one Vim-method
   question, the preceding unseen transfer edit, and a distinct key-hidden
   persisted-artifact edit. It automatically previews the verified strip and
   visibly changes tree state immediately on passing.
6. Two documented Neovim paths that yield the same valid buffer can pass a
   method-agnostic edit; a method-contrast card verifies each taught family.
7. Project preview plays frames in manifest order at two selectable speeds,
   with holds visible. Unequal frame heights are diagnosed before playback.
8. Progress projection rebuilds exactly from events, preserving old logs,
   skips, quiz attempts, stable IDs, and private user art. A forced drill or
   review never silently grants capstone mastery.
9. Content tests assert source and license metadata, glyph contract, question
   answer/feedback completeness, no prerequisite cycles, all expected variants,
   and real-Neovim passability under clean and normal config. Scheduler tests
   cover clock gaps, daily caps, failures, crashes, concurrent triggers, and
   curriculum migrations. Existing 46/46 recipe regression remains green.
10. One learner can complete M0-M2 without seeing an identical question stem,
    target, or recipe twice except a deliberately identified spaced review.

The completed implementation is judged against these observable outcomes, not
against the presence of a tree-shaped display or a larger drill count alone.
