# Curriculum v2 card catalog — implemented 152-card spine

Status: these 152 row-level contracts describe the implemented teaching intent
and are retained in generated data as `roadmap_contract` for traceability. The
executable `prompt`, `start`, `target`, question IDs, and recipes in
`curriculum-v2.json` remain the grading authority; generator-artifact equality
and real-Neovim replay are required before a row may be called implemented.
Read with [the evidence-backed spec](CURRICULUM_V2_SPEC.md) and
[implementation plan](CURRICULUM_V2_PLAN.md). A card is a short *eligible hourly
session*, not a promise that a learner must wait exactly 152 elapsed hours or
complete a long animation step inside one popup. The scheduler may interleave
varied reviews. The eight cards in each module edit one persistent `strip.txt`;
M6 and M7 deliberately continue the same strip across a module boundary.

## Evidence and provenance for this sequence

- The absence of a tree, fixed repetition, manual-only questions, dated
  standalone files, and unused multi-frame walk are established in spec E01-E08
  with exact current-repo line citations. This catalog is a proposed successor,
  not a claim about what the current binary does.
- The original animation order is grounded in archived Part 1 transcript
  `o5v-NS9o4yc-transcript-timestamped.txt:339-401` (00:52:45-01:01:05:
  reference, concept, primary pose, size/shot, plan, extremes, middle
  in-betweens, early playback, polish), `:402-410` (subtractive authoring),
  Part 2 `h6a2BKPHPqA-transcript-timestamped.txt:59-65,87-141`
  (midpoints, offset parts, occlusion, preview/holds/padding), and tutorial
  `02-poison-adept-walk-cycle.txt:1-72` / `06-animation-subtractive.txt:1-80`.
  Full archive paths, timestamp caveat, and public links are in spec §2.
- Neovim command coverage follows the installed tutor chapters cited in spec
  §3, with specific legacy drill IDs mapped exactly once in spec §5. Any card
  using `:t`, a block operation, `.` or a macro needs an exact Neovim help tag
  and a real-Neovim golden path before it ships (plan P1/P6). The catalog's
  Vim sequences are teaching intentions, not a claim that all are currently
  implemented or pass the existing one-recipe evaluator.
- A complete public ten-frame walk or full pyramid plate must **not** be
  copied into new content merely because the archive contains it. The current
  bundled-content tension and review gate are recorded in spec E11/§3 and
  plan P0. Create original/user-local scaffold art unless rights are cleared.

## Card contract and symbols

Every row below is an authoring slot with a stable ID and one observable
outcome. `G` = guided buffer edit (recipe may be revealed after an initial
prediction), `Q` = answer-hidden conceptual check, `X` = compare two *valid*
Neovim approaches to the same result, `T` = key-hidden transfer on a different
`transfer.txt` subject, and `K` = module checkpoint. A `K` card checks an
unfamiliar variant and the project artifact; it may be resumed over multiple
eligible sessions. A wrong `Q`, `T`, or `K` schedules a changed variant and a
named remediation, not the same four choices or identical target next hour.

The card's `strip_delta` is the only permitted change to the learner project.
Question text and tutorial prose live outside `strip.txt`; after submission,
`compare.txt` can reveal both methods. Every edit target is shown. Guided cards
may also show the exact recipe; T/K edits show a non-key action hint and keep
the command answer hidden until evaluated. The module check samples
five unseen conceptual items. Every conceptual item is itself a paired check:
one `ANIMATION` reading plus one `NEOVIM` edit-scope or command decision, with
credit awarded only when both halves of the selected answer are correct. The
check also requires two key-hidden edits including its `T` evidence and the verified strip,
as defined in spec §4/§9. Items are selected from the separate 190-item bank;
the two Q slots are *encounters*, not merely two questions total per module.

## M0 — `spark-loop`: modes, cells, and a readable five-frame event

Project starts from an original three-row spark. Outcome: a five-frame appearance,
brightening, dimming, return/hold loop. The Q prompts distinguish visible
motion from a changed glyph with no intentional timing. Source spine: spec §5
M0; legacy `move-x`, `undo`, `open-line`, `put`, `ant-drop`; animation process
transcript Part 1 `:339-401`.

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M0.01 | G | Replace Fireworks `*` with `o`; preserve every ray and accent. |
| M0.02 | G | Copy all three frame rows, then brighten only the core in the copy. |
| M0.03 | Q | Read complete multi-row frames and choose the change actually supported by the visible evidence. |
| M0.04 | G | Copy the bright keyframe, then widen only the new frame's horizontal rays into a flare. |
| M0.05 | X | Create one deliberate whole-frame flare hold using ONE method: counted yank/put or addressed `:t`; after success, compare cursor dependence. |
| M0.06 | T | Brighten and widen an unfamiliar three-row comet without shifting its registered rays. |
| M0.07 | Q | Read the ordered five-frame strip and distinguish a purposeful flare hold from drift or an arbitrary duplicate. |
| M0.08 | K | Add the registered dim settle frame and pass the mixed conceptual/artifact checkpoint. |

## M1 — `line-run`: glyph geometry and precise landmarks

Continue the original small-scene lineage with a moving slash/line run, but
checkpoint it as its own `strip.txt` revision. Source spine: spec §5 M1;
legacy `count-motion`, `search`, `find-char`, `replace-char`, `mirror-run`,
`cheer-eyes`, `append`; archived tutorial page sections 5-6 as cited in spec.

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M1.01 | G | Find an uncertain comma joint inside a three-row contour and replace only it with the chosen colon material. |
| M1.02 | G | Copy the complete anchored contour as a working frame. |
| M1.03 | Q | Read the complete contour and choose the interpretation that preserves its anchor and slope vocabulary. |
| M1.04 | G | Replace the copied frame with a hand-authored descending counterpart instead of software-flipping the glyphs. |
| M1.05 | X | Change the joint material in both frames by local edit-plus-dot and by a bounded substitute. |
| M1.06 | T | Repair the corresponding joint in an unfamiliar anchored or mirrored contour. |
| M1.07 | Q | Diagnose endpoint drift, broken material, or an unsafe scope in a changed contour. |
| M1.08 | K | Return to the registered rising contour and pass a mixed landmark/material checkpoint. |

## M2 — `shape-edit`: operator/motion grammar on a contour

The strip now develops a compact body/contour. One lesson teaches a simple
local change; a later one chooses a larger text object/range only when the
shape requires it. Source spine: spec §5 M2 and legacy
`delete-word`, `delete-eol`, `delete-line`, `change-word`, `change-eol`,
`substitute`; installed tutor coverage in spec §3.

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M2.01 | G | Delete an annotation from one face row without consuming the eye, mouth, or silhouette. |
| M2.02 | G | Copy the complete four-row face before making an acting change. |
| M2.03 | Q | Choose the command scope that changes a facial feature without damaging the registered contour. |
| M2.04 | G | Find the copied eye and change only its focus glyph. |
| M2.05 | X | Normalize two eye spellings by two local replacements and by a narrowly matched substitute. |
| M2.06 | T | Change only the eye inside an unfamiliar complete face. |
| M2.07 | Q | Diagnose an edit that consumed the mouth/contour or used a strip-wide match without proof. |
| M2.08 | K | Copy a complete face and close only its eye for the blink checkpoint. |

## M3 — `pose-copy`: duplicate a whole key pose, not just a line

Begin a multi-row original character strip. The point is *intention*: copy the
entire block and change only the named glyph in the copy. This is the user's
specific example, with four-choice predictions before editing. Source spine:
spec §5 M3, §6 method contrast; legacy `yank-put`, `named-register`,
`yank-register-0`, `symbol-table`, `centipede-hold`; archived Part 1 `:339-401`.

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M3.01 | G | Verify the original six-row primary pose by changing only its eye placeholder. |
| M3.02 | G | Use a counted linewise yank/put to duplicate all six rows. |
| M3.03 | Q | Four complete command sequences: which duplicates the *whole* pose and replaces just the accent without destroying the source? |
| M3.04 | G | Change only the eye in the copied six-row pose; torso and feet must remain registered. |
| M3.05 | X | Append the same complete pose with counted `y/p` and precisely addressed `:t`. |
| M3.06 | T | Copy an unfamiliar six-row body and change one acting feature only in the copy. |
| M3.07 | Q | Diagnose partial-pose copying, body drift, or an unjustified unchanged hold. |
| M3.08 | K | Give only the final complete pose a middle-dot accent and pass the whole-block transfer check. |

## M4 — `rotation-tween`: extremes before the middle

The persistent strip is a rotating prop. Author two real diagonals first, then
the vertical middle pose; pivot and baseline stay stable. Local redraws handle
separated diagonal cells, while Visual block is reserved for the true aligned
midpoint column. Source spine: spec §5 M4,
archived Part 1 `:28-45,339-401`, Part 2 `:59-65,87-125`.

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M4.01 | G | Move the upper tip across the axis and turn the lower stroke while the pivot remains fixed. |
| M4.02 | G | Copy the complete forward diagonal as a working frame. |
| M4.03 | Q | Given extremes and four proposed middle frames, choose the one that reads as an in-between around the same pivot. |
| M4.04 | G | Copy a complete extreme, align its upper stroke, then replace the true two-cell midpoint column with Visual-block `r`. |
| M4.05 | X | Build the returning diagonal by `C` plus `r` and by `d$` plus `A` plus `r`; compare scope and recovery risk. |
| M4.06 | T | Tween a different original rotating glyph between unseen extremes without changing its fixed base. |
| M4.07 | Q | Spot one-frame glyph jitter or half-cell ambiguity; decide whether to redraw, hold, or accept the limit. |
| M4.08 | K | Preview a coherent rotation and pass an independent midpoint plus method-choice check. |

## M5 — `layered-scene`: foreground, background, and negative space

The strip composites a moving foreground above material bands and ground. A
background bar directly below the pivot creates a visible false seam; the
learner edits only the layer that must give way at that contact. Source spine:
spec §5 M5; legacy `match-paren`, `text-object-paren`, `paragraph-object`,
`visual-delete`, `block-erase`, `break-seam`, `join`, `candle-join`; Stone Story
layer/seam method indexed in the authoring skill §§3, 11.

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M5.01 | G | Erase the background bar directly touching the foreground pivot without shifting its row. |
| M5.02 | G | Copy the complete seven-row composite before moving the blade. |
| M5.03 | Q | From four composites, identify the false seam that makes foreground and background read as one object. |
| M5.04 | G | Swing the copied foreground while keeping the pivot and negative-space break registered. |
| M5.05 | X | Return to the first full layered frame by counted yank/put and addressed `:t`; preserve every material row. |
| M5.06 | T | Repair an unfamiliar overlapping scene, preserving layer order and the nominated foreground edge. |
| M5.07 | Q | Predict when a break glyph attaches to the wrong object or an erasure destroys the silhouette. |
| M5.08 | K | Preview the layered sequence and pass independent seam, selection-scope, and artifact checks. |

## M6 — `pyramid-build`: subtractive authoring, forward playback

Use an **original** pyramid/build-up scaffold pending the source-rights review;
do not publish a reconstructed third-party plate. Work backward from the
finished key pose, deleting units in authoring order, then reorder for playback.
M7 continues this exact strip. Source spine: spec §5 M6; legacy
`playback-order`, `ex-copy`, `block-erase`; archived Part 1 `:402-410`, page
`06-animation-subtractive.txt:1-80`. Reduction removes upper units first so the
reordered strip grows from the base upward.

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M6.01 | G | Draw/inspect the finished object as the primary key pose and count its units. |
| M6.02 | G | Copy the complete pose before any subtractive change. |
| M6.03 | Q | Choose why copying then erasing can be easier than drawing an accretive build-up forward. |
| M6.04 | G | Clear only the copied apex row while preserving that empty row and every lower layer of the five-row frame. |
| M6.05 | X | Copy the first reduction by counted yank and addressed `:t`, then clear the next upper unit with `D`. |
| M6.06 | T | Move an unfamiliar finished five-row build after its reduced state to establish forward playback order. |
| M6.07 | Q | Given authoring order and four playback orders, pick the sequence that visibly builds rather than vanishes. |
| M6.08 | K | Reorder complete equal-height frame ranges and prove that the strip visibly builds rather than deconstructs. |

## M7 — `timed-pyramid`: holds, repeat, and a polish pass

Continue M6's `strip.txt`; do not reset the project. Timing means intentional
holds/offsets, not merely more frames. Source spine: spec §5 M7; legacy
`toggle-case`, `macro`, `dot-repeat`, `range-normal`, `macro-frames`,
`substitute-all`; archived Part 2 `:126-141`.

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M7.01 | G | Duplicate the complete incomplete frame as a declared anticipation hold before completion. |
| M7.02 | G | Append a complete settle duplicate that later diagnosis must either justify or remove. |
| M7.03 | Q | Distinguish a deliberate hold from a dead duplicate using the timing plan, not buffer equality alone. |
| M7.04 | G | Change the apex in the first held frame and repeat that exact cell edit in the matching hold with `.`. |
| M7.05 | X | Harmonize one three-cell material band across every frame by substitution, a Visual macro, and `:global` plus `:normal`. |
| M7.06 | T | Give a fresh build-up a meaningful hold and a scoped batch edit without modifying instructions or other projects. |
| M7.07 | Q | Choose safe `:s`/`:normal` range versus `%` for a selected set of frames and predict blast radius. |
| M7.08 | K | Remove the unjustified trailing duplicate while retaining the anticipation hold, then pass timing/range checks. |

## M8 — `walk-study`: legs, prop offset, and contact continuity

Study the documented 4+4+2 timing relationship of the Poison Adept walk, but
author an original/user-local short walk scaffold unless the exact bundled-art
rights review approves more. The public source is a reference, not an asset
copy instruction. Source spine: spec §5 M8; legacy `hold-frame`, `tween-frame`,
`pad-frames`, `marks`; archived Part 1 `:28-45`, Part 2 `:59-65,87-141`, page
`02-poison-adept-walk-cycle.txt:1-72`.

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M8.01 | G | Plant the leading foot in a complete five-row contact pose while torso and raised arm stay fixed. |
| M8.02 | G | Copy the full pose, then change only the copied arm and legs into a passing pose. |
| M8.03 | Q | Given adjacent frames, choose the perceived motion and name which part leads or lags. |
| M8.04 | G | Append the opposite contact pose as five complete rows, keeping the torso registered. |
| M8.05 | X | Change a repeated arm direction by local replacements and by a bounded substitute. |
| M8.06 | T | Plant one foot in an unfamiliar five-row walker without moving torso or secondary arm. |
| M8.07 | Q | Diagnose a one-frame foot slide, staff pop, or mismatched row count; select the first repair. |
| M8.08 | K | Add a distinct return passing pose, preview the walk study, and pass motion-reading, method-choice, missing-frame, and registration checks. |

## M9 — `original-micro`: original bounce capstone

This is a bounded original three-row bounce study, not the M2 blink with a new
border. It applies the full plan-first process to high, falling, squash, rebound,
and loop-settle decisions. Source spine: spec §5 M9, archived Part 1 `:339-401`
and Part 2 `:1-5,126-141`.

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M9.01 | G | Commit the planned high ball while the side rails and ground stay registered. |
| M9.02 | G | Copy the full high pose and block a readable squash extreme inside the same bounds. |
| M9.03 | Q | Choose a plan that names motion, frame size, extremes, timing, and the ground anchor. |
| M9.04 | G | Replace the squash scaffold's round centre with one horizontal material band. |
| M9.05 | X | Insert the falling midpoint by direct three-row authoring and by copy-then-vary; compare registration risk. |
| M9.06 | T | Commit a high keyframe in unfamiliar bracketed or angled bounds without moving its ground. |
| M9.07 | Q | Diagnose ground drift, an unreadable squash, a missing fall, or an unjustified duplicate. |
| M9.08 | K | Add a larger rebound overshoot, preview its settle into frame one, and pass the mixed capstone checkpoint. |

## M10 — `sjis-puff-tween`: proportional glyph motion from corpus evidence

This branch does not claim that a terminal renders proportional art correctly.
Neovim owns exact Unicode transcription and scoped editing; visual judgment
belongs to Saitamaar 16 px at the corpus's true advances. Its source is the
training-only aggregate in `sjis_corpus_findings.v1.json`, derived from the
viewer's `sjis_combos.v1` dataset. Held-out slugs remain excluded.

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M10.01 | G | Complete `⌒ヽ` in a full three-row lobe pose while preserving its registered lower contour. |
| M10.02 | G | Copy the complete lobe pose, then transform all three copied rows into the wider `／￣＼` and `＼＿／` extreme. |
| M10.03 | Q | Read the proportional expansion and choose both the supported animation principle and bounded Neovim edit. |
| M10.04 | G | Append a complete three-row impact pose with `ﾆ二ニ` hatching contained by its outline. |
| M10.05 | X | Duplicate the full impact pose as a purposeful hold by counted yank and by addressed `:t`; compare cursor dependence. |
| M10.06 | T | Complete an unseen `｀ヽ` or `／￣` shoulder while preserving the changed pose's two registered lower rows. |
| M10.07 | Q | Diagnose shear, escaped hatching, or false terminal-cell alignment in an ordered proportional strip. |
| M10.08 | K | Return to the complete lobe as the settle and pass a mixed animation, Saitamaar-boundary, and Neovim checkpoint. |

### M11 — TowerDefense missile fixed-width redraw

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M11.01 | G | On the sourced TowerDefense missile, overwrite the first two roof underscores with `==` while every later hull cell remains registered. |
| M11.02 | G | Copy the complete three-row missile before developing its slack-tension pose. |
| M11.03 | Q | Read the missile's bounded roof change and explain why Replace mode preserves fixed-width registration. |
| M11.04 | G | Redraw only the copied roof from `==` to `~~`, undo that real edit, then redo it so the saved missile remains the slack extreme. |
| M11.05 | X | Reverse the copied missile's two inner strokes from `/ /` to `\ \` by local replacements or a current-row substitute; compare scope. |
| M11.06 | T | Close the sourced Snail's adjacent `Oo` eyes with one two-cell Replace redraw while its shell and baseline remain registered. |
| M11.07 | Q | Diagnose insertion drift, no-op undo/redo, unsafe whitespace cleanup, or mismatched trail columns on the sourced art. |
| M11.08 | K | Use `virtualedit=all` and repeated exact-column motion to place aligned trail bars at column 12 on the taut and banked missile poses. |

### M12 — Joint sweep

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M12.01 | G | Approach the left upper joint with `t:` and accent only that cell while the mirrored outline and centre axis remain registered. |
| M12.02 | G | Copy the complete three-row pose, then approach its right joint backward with `T:` to create the second staggered key pose. |
| M12.03 | Q | Pair the visible left-to-right accent timing with the cursor position produced by forward and backward till motions. |
| M12.04 | G | Copy the two-upper-joint extreme, use `;` to reach the second delayed lower joint, then `,` to return and edit its first partner. |
| M12.05 | X | Brighten both base cells by repeated character search and by a row-scoped substitute; compare scope and repeatability. |
| M12.06 | T | Transfer forward and backward till motions to paired joints in unfamiliar mirrored shells without relying on column counts. |
| M12.07 | Q | Diagnose byte-reversed slashes, a lost stagger, or cursor placement one cell away from the intended joint. |
| M12.08 | K | Copy the complete first pose and exchange its left accent for the hand-mirrored right accent so the loop exits on the opposite side. |

### M13 — Texture pulse

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M13.01 | G | Reach the centre whitespace-separated punctuation cluster with `W` and start a material pulse without shifting either support row. |
| M13.02 | G | Copy the complete three-row pose, clear its centre accent, and advance it one texture WORD to the right. |
| M13.03 | Q | Pair the visible centre-to-right pulse with the difference between WORD landmarks and punctuation-sensitive lowercase word stops. |
| M13.04 | G | Copy the right-pulse pose and use `E`, counted `W`, and `B` to expand the accent across three distinct texture edges. |
| M13.05 | X | Flash three acting cells by repeated landmark edits and by a current-row material substitution; compare their scope. |
| M13.06 | T | Transfer counted `W`/`B` or `E` motions to unfamiliar spaced texture clusters without memorised columns. |
| M13.07 | Q | Diagnose shifted clusters, accidental support-row edits, or lowercase motions that stop inside punctuation. |
| M13.08 | K | Copy the complete centre pose and move its accent left with `W` and `B` to finish the opposite-side loop exit. |

### M14 — Variant palette

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M14.01 | G | Yank a visible glyph from the frame's palette into register `a`, then retrieve it with `<C-r>a` in Replace mode so the acting eye changes without shifting the wall. |
| M14.02 | G | Treat the complete blank-line-separated face as one paragraph object and duplicate it with `yap` plus put. |
| M14.03 | Q | Distinguish a deliberate saved variant from a shifted redraw, and connect palette consistency to named-register scope. |
| M14.04 | G | On the copied frame, store the second palette glyph and replace only its eye through the named register. |
| M14.05 | X | Duplicate the same complete variant with paragraph-object `yap`, frame-boundary `P`, and with an exact four-line `:t` range; compare semantic object scope with numeric range scope. |
| M14.06 | T | Transfer named-register palette retrieval through Replace mode to an unfamiliar shell and palette. |
| M14.07 | Q | Diagnose a one-row copy, an insertion-shifted wall, or a retyped glyph that diverges from the declared palette. |
| M14.08 | K | Store the first eye material, navigate across two paragraph frames with `}`, and retrieve the register in the third frame so the variant sequence returns to its first material. |

### M15 — Texture ground

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M15.01 | G | Set `shiftwidth=1`, then offset only the repeated brick-material row by one fixed-grid cell with `>>` while the dither and angled shadow stay registered. |
| M15.02 | G | Copy the complete three-row material stack as the working frame for a lighter offset treatment. |
| M15.03 | Q | Pair the visible one-cell brick pan with the option and operator that make one indentation step equal one animation cell. |
| M15.04 | G | Shift the copied brick row one more cell and lighten only its top dither band with a row-bounded substitution. |
| M15.05 | X | Add one occluding edge to each row end with blockwise `$A` and with `:4,6s/$/|/`; compare visual selection with explicit range scope. |
| M15.06 | T | Transfer the explicit one-cell material offset to unfamiliar brick, dither, and shadow glyphs. |
| M15.07 | Q | Diagnose a two-cell lurch, a lightened shadow, a leaking range, or a macro replay that escapes the acting dither row. |
| M15.08 | K | Append the registered starting frame, record one colon-to-dot landmark edit, and replay it exactly three times to build the lighter settle row. |

### M16 — Key-pose plan

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M16.01 | G | Verify the playback-size key-pose plate and increment its written frame label in place with `<C-a>`. |
| M16.02 | G | Import the saved five-line planning plate with `:read %`, then increment only the imported frame label. |
| M16.03 | Q | Connect reference, concept, size-test, frame identity, and FPS evidence to the saved-source semantics of `:read`. |
| M16.04 | G | Copy a complete five-line plan block with `:t` and use counted `<C-a>` to assign the third frame number. |
| M16.05 | X | Reorder one complete planned key-pose block with addressed `:m` and with linewise delete/put; compare verified range scope with selection scope. |
| M16.06 | T | Increment the numeric frame label on an unfamiliar pose and timing plan without altering its art or FPS line. |
| M16.07 | Q | Diagnose duplicate identifiers, stale saved input, a split five-line block, or timing written only after drawing. |
| M16.08 | K | Copy the current primary key-pose plan as a fourth block and count-increment its label while preserving the approved pose and FPS. |

### M17 — Coherent anchors

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M17.01 | G | Correct the same eye anchor in three changing shell poses with `/`, `n`, and dot while every contour remains untouched. |
| M17.02 | G | Copy the complete third pose as a scaffold whose already-correct eye remains attached to its shell. |
| M17.03 | Q | Identify unchanged glyphs as temporal anchors and distinguish an incomplete coherence pass from intentional pose variation. |
| M17.04 | G | Develop a fourth shell extreme by changing two contour landmarks without editing its stable eye row. |
| M17.05 | X | Change all four eye anchors with search-plus-dot and with `:g/o/normal! ...`; compare enumerated matches with line selection. |
| M17.06 | T | Transfer `/`, `n`, and dot to corresponding eye anchors inside three unfamiliar shell vocabularies. |
| M17.07 | Q | Diagnose a stale eye, a global selector that also matches contours, or a repeat that lands outside the homologous landmark set. |
| M17.08 | K | Record replacement plus `n` in a macro and replay it exactly three times across the four verified frame anchors. |

### M18 — Hand-mirrored return

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M18.01 | G | Hand-author all three rows of a directional mirror, exchanging actor position, arrowhead, slash limbs, and spacing without reversing stored bytes. |
| M18.02 | G | Copy the complete mirrored extreme and its pending validation line as the return-overshoot scaffold. |
| M18.03 | Q | Distinguish a full authored mirror from relocation, byte reversal, or an automated art transform. |
| M18.04 | G | Redraw all three copied art rows one cell past the return extreme to create a coherent overshoot. |
| M18.05 | X | Mark the two frames verified manually and with a `\=`/`getline()` expression that changes only CHECK digits; never use the expression to generate art. |
| M18.06 | T | Hand-mirror an unfamiliar actor, arrow material, limbs, and spacing through three explicit row overwrites. |
| M18.07 | Q | Diagnose an inward slash, inconsistent body offset, generated rather than authored mirror, or unexplained duplicate. |
| M18.08 | K | Append the approved overshoot and return ranges in reverse order, preserving a declared two-frame turnaround hold. |

| Card | Kind | One new decision/edit and artifact result |
|---|---|---|
| M19.01 | G | Approve one uncertain eye cell with `gR`, preserving both fixed-width rails of the five-row key-pose still. |
| M19.02 | G | Copy the complete five-row still as the working opposite-facing animation extreme. |
| M19.03 | Q | Distinguish semantic hand mirroring from relocation, byte reversal, or insertion-driven row drift. |
| M19.04 | G | Hand-author all five copied rows with Virtual Replace, exchanging directional spacing, slashes, and the arrowhead. |
| M19.05 | X | Compare bounded `R` and `gR` runs on the same two-cell arrow material without crossing into its arrowhead. |
| M19.06 | T | Transfer full-row Virtual Replace mirroring to unfamiliar fixed-rail key-pose art with the exact keys hidden. |
| M19.07 | Q | Diagnose wrong-facing glyphs, unequal rails, accidental duplicates, and software-flipped rows. |
| M19.08 | K | Retain a complete approved still as a third candidate and vary one eye without turning the plate into premature playback. |

## Content-authoring and delivery gates

1. This is exactly twenty modules and eight numbered cards per module. Each module
   has two scheduled conceptual encounters (`.03`, `.07`), one method contrast
   (`.05`), one distinct-art transfer (`.06`), and one mixed checkpoint (`.08`).
   The other three are focused guided edits. The generator owns 190 distinct
   conceptual items across visual reading, prediction, diagnosis, comparison,
   transfer, and coherence, with four choices and mistake-specific feedback;
   the catalog owns the 160 learner-visible lesson contracts that frame them.
2. Each implemented card carries machine-readable `prerequisites`, `node_ids`,
   `source_ref`, `project_id`, `strip_delta`, `start_fixture`, `target_predicate`,
   `variant_group`, `hint_policy`, `required_method_family` (if any), and a
   tested real-Neovim path. A `K` card also needs its rubric and two unseen
   transfer fixtures. The evaluator may accept any method yielding a valid
   result except where demonstrating a taught family is explicitly stated.
3. For every source-inspired art fixture, record whether it is original,
   public-domain, licensed with retained notice, or private user-local. This
   catalog authorizes no new third-party plate inclusion. Import of a Vim
   curriculum must follow spec §3/plan P0 with exact file/commit/license.
4. As authoring proceeds, test the continuous journey: each card starts from
   the previous verified checkpoint, changes the intended part only, and
   leaves all earlier frames and private learner edits recoverable. A static
   final-target fixture alone cannot prove that continuity.
