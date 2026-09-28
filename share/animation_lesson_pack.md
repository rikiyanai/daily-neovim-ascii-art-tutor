# Standalone ASCII-animation lesson pack

**Status:** authoring source only; not wired into `gen_curriculum_v2.py`,
`curriculum-v2.json`, or the tutor runtime.  
**Purpose:** teach animation decisions and Neovim editing grammar with original,
fixed-width exercises.  
**Rights rule:** the Stone Story corpus and tutorial archive are research
references only. Every exact source use is `integration: blocked` in this pack.
No source frame, logo, worm, dome, brick, pit, sapling, rampart, font, or
lightly altered source derivative appears below.

## How to use this source

Each lesson is a complete specification, not a generated card. A future
integrator may split a lesson into guided, hidden, comparison, transfer, and
review cards, but must preserve these contracts:

1. Show the complete fixed-width target and the requested answer format.
2. Guided work may show a concrete Neovim sequence; hidden work names the
   grammar and scope but withholds exact keys.
3. Ask a question only after the prerequisite observation or edit has been
   taught. Every question below has an answer, a format, a prior-teaching
   basis, a clarity check, and a placement rationale.
4. Every changed-art review has at least two new variants. A correct old frame
   does not prove that the learner can transfer the decision.
5. Keep frames as blank-line-delimited, equal-width objects. A layer may be
   static, but its registration contract must be named.

## Finish-line vocabulary

| Code | Habit or stage | What the learner must be able to do |
|---|---|---|
| H1 | overwrite, never insert | Replace the nominated cell or band without changing frame height or width. |
| H2 | exact-cell landing | Reach a declared row/column landmark before editing it. |
| H3 | frame/layer objects | Select, copy, compare, and move a complete frame or layer as one object. |
| H4 | column editing | Change a registered column or vertical feature without disturbing neighbors. |
| H5 | repeat at scale | Make one precise edit repeatable with `.`, a macro, or a bounded range. |
| H6 | register palette | Keep a small, named glyph palette and reuse it consistently. |
| H7 | frame comparison | Inspect adjacent frames or layers side by side and name the visual change. |
| H8 | cleanup and padding | Remove accidental trailing cells and pad every frame to a common box. |
| H9 | safe variant exploration | Make, compare, undo, and retain only an intentional variant. |
| S0 | grid/glyph alphabet | Establish the fixed-width grid and overwrite vocabulary. |
| S1 | slopes/runs | Build and judge a consistent shallow run or stair-step. |
| S2 | hand mirror | Reverse a pose by hand, respecting glyph asymmetry. |
| S3 | block/clear | Isolate an unsure still region and clear it without deleting its rows. |
| S4 | joints/anti-alias | Choose a joint height and the least-wrong near-vertical glyph. |
| S5 | materials/variants | Use a stable material palette while comparing alternatives. |
| S6 | layers/seams | Separate layers at contacts and preserve their registration. |
| S7 | ground/shadow | Make repeated ground, dither, and shadow material read as one system. |
| A0 | plan/key pose | Name subject, bounds, anchor, extremes, and timing before drawing. |
| A1 | extremes/breakdowns | Author extremes first, then choose a breakdown between them. |
| A2 | in-between/onion skin | Bisect a change while comparing adjacent frames. |
| A3 | coherence/holds | Hold unchanged parts and vary only the nominated feature. |
| A4 | spacing/arc/overlap | Control spacing, arcs, overshoot, drag, and follow-through. |
| A5 | subtract/reorder/pad | Build by subtraction when useful, reorder playback, and equalize bounds. |
| A6 | mirror/reverse | Reuse an action by hand-mirroring or reversing it without a seam pop. |
| A7 | preview/polish | Preview a short original loop, diagnose jitter, and polish the seam. |

## Lesson map

| ID | Focus | Habits | Stages |
|---|---|---|---|
| AL01 | frame objects, key pose, registration | H2 H3 H8 | S0 S3 A0 |
| AL02 | extremes, breakdowns, joints, exact cells | H1 H2 H4 | S1 S4 A1 |
| AL03 | in-betweens, onion skin, frame comparison | H2 H3 H7 | A2 |
| AL04 | spacing, holds, stagger, repeat | H3 H5 H7 | A3 A4 |
| AL05 | arcs, overshoot, settle, safe variants | H2 H7 H9 | S4 A4 |
| AL06 | layers, seams, drag/follow-through | H3 H4 H5 | S6 A4 |
| AL07 | loop seam, reverse action, cleanup | H1 H3 H8 H9 | S2 A6 A7 |
| AL08 | columns, padding, ground and shadows | H1 H4 H8 | S0 S7 A5 |
| AL09 | palette/registers, material variants | H5 H6 H9 | S5 |
| AL10 | hand mirror and asymmetric glyphs | H2 H3 H4 | S2 A6 |
| AL11 | subtractive build, frame/layer objects | H3 H5 H8 H9 | S3 A5 |
| AL12 | original 4+4+2 capstone | H1 H2 H3 H4 H5 H6 H7 H8 H9 | S0–S7 A0–A7 |

The source audit that motivated these families is
`share/audits/ANIMATION_CORPUS_RIGHTS_AUDIT.md`. Its qualifying evidence is
the local inventory `share/audits/animation-frame-paths.txt:1-972`, including
Mech (52 sheets/49 distinct poses), Skully (46/37), Panda (28/28), Dragon
(29/28), Knight (34/27), TowerDefense (21/21), BurgerRush (18/18), FaceHUD
(12/11), and Calculator (15/15). These counts select *where to teach*; they do
not authorize copying those assets.

In this pack, a **keyframe** is a complete registered frame chosen because it
states a meaningful pose or timing decision; a breakdown and an in-between are
also complete frames, not partial source excerpts.

## AL01 — Register the object before changing it

**Map:** H2, H3, H8 · S0, S3, A0  
**Source evidence:** Layer/frame ordering is documented as a general technique
in the archived tutorial plate
`/Users/r/Projects/ascii-art-archive/collections/y9-2-articles/2026-09-07-stone-story-video-transcripts-media/o5v-NS9o4yc/ascii-tutorial-page/01-sacrificial-pit-layers.txt:1-1122`.
The exact plate is blocked; this exercise is unrelated geometry.

### Original exercise

Create a four-row, seven-column beacon. The `|` in row 4 is the ground anchor;
the frame must remain 7 columns wide.

```text
  /\  
 /==\ 
| .. |
  ||  
```

Copy the whole frame to make a second object, then replace only the two dots
with `::`. Do not insert a row or move the anchor.

### Guided sequence

- `key-hidden: no`; place the cursor on row 1 and select exactly four lines.
- Use `4yy` then `p` to copy the frame as one object.
- On the copied row 3, use `f.` then `r:` twice; verify four rows and seven
  columns before previewing.
- Compare the original and copy with the cursor on their anchor columns.

### Hidden sequence

- `key-hidden: yes; keys: withheld`.
- Vocabulary: linewise object, exact row/column landmark, overwrite, fixed box.
- Hint 1 names the object size (four lines). Hint 2 names “replace the two
  material cells in the copy”; no key sequence is shown.
- Pass only if the copy has the new material, the original is unchanged, and
  both objects have identical bounds.

### Questions

#### AL01-Q1 — What is the anchor?

- Placement: before the guided copy.
- Ask: Which visible cell must stay in the same column when the frame is copied?
- Expected answer: The `|` ground anchor in row 4, column 3.
- Answer format: `row, column, reason`.
- Prior teaching basis: S0 fixed-width grid and H2 exact-cell landing are
  taught in the pack preamble; the prompt names the candidate and coordinate.
- Clarity check: clear — it asks for one cell and one reason, not a drawing.
- Placement rationale: before copying, so the learner has a registration test.

#### AL01-Q2 — Is this a frame or a cell edit?

- Placement: after the guided copy.
- Ask: Which operation should be repeated as one object if the beacon gains a
  third timing variant: the four-row copy or the row-3 replacement?
- Expected answer: Copy the four-row frame first; the row-3 replacement is the
  later local variation.
- Answer format: `object first: frame | cell; explanation`.
- Prior teaching basis: the guided sequence has just demonstrated both scopes.
- Clarity check: clear — the two choices are named and the requested format is
  explicit.
- Placement rationale: after seeing the two scopes, not before.

### Changed-art review

- Variants: a six-column bell (`/--\\`, `|oo|`, `\\__/'`) and an eight-column
  signal (`<++>`, `|  |`, `|  |`, `__||__`) with a nominated anchor column.
- Review asks the learner to identify the complete object, copy it, and change
  only the nominated material cell. Both variants require equal-height,
  equal-width checks.

### Question audit

- student-can-answer-from-prior-teaching: yes — the object size, anchor, and
  overwrite distinction were taught before each question.
- request-is-clear: yes — each question specifies one decision and answer shape.
- placement-makes-sense: yes — Q1 precedes the edit; Q2 follows the observed
  scope contrast.

### Rights gate

- integration: blocked — source plate is reference-only and no source glyphs are
  used.
- source use: technique and line citation only; no source frame is reproduced.
- original exercise: yes — beacon geometry was authored for this pack.

## AL02 — Extremes and the readable breakdown

**Map:** H1, H2, H4 · S1, S4, A1  
**Source evidence:** The corpus contains many long pose sets, including
`/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/Mech` (52
sheets, 49 distinct poses) and
`official-Cosmetics/Knight` (34/27), recorded at
`share/audits/animation-frame-paths.txt:101-187`. Only the general idea of
multiple poses is used.

### Original exercise

Author two extremes of a five-row kite around a fixed `+` pivot in column 5,
then a breakdown halfway between them. Every frame is 11 columns wide.

```text
   /\      
  /  \     
--  +  --  
  \  /     
   \/      
```

Extreme B tilts the top point two columns right while the pivot stays put. The
breakdown moves it one column right and changes only the two adjacent slopes.

### Guided sequence

- `key-hidden: no`; mark the `+` pivot with `mK` and verify the two extreme
  frames before authoring any middle.
- Use a complete-frame copy (`5yy`, `p`) and overwrite the changed slope cells
  with `r` rather than opening new rows.
- On the copied extreme, use `V` plus `:t$` to create a breakdown scaffold;
  redraw only the four cells adjacent to the pivot.
- Preview extremes → breakdown → extreme and note whether the motion reads as
  one-column spacing.

### Hidden sequence

- `key-hidden: yes; keys: withheld`.
- Vocabulary: extreme, pivot, breakdown, exact column, overwrite, spacing.
- Hint 1: “copy a complete five-row object”; hint 2: “change the four cells
  adjacent to the fixed pivot”; no key sequence is revealed.
- Pass requires both extremes to remain intact, the breakdown to be unique, and
  the pivot column to match in all three frames.

### Questions

#### AL02-Q1 — Which pose is the breakdown?

- Placement: before hidden authoring.
- Ask: If A points left and B points right, which pose should sit between them:
  a second copy of A, a midpoint scaffold, or a new unrelated pose?
- Expected answer: A midpoint scaffold that preserves the pivot and moves the
  top point about halfway from A to B.
- Answer format: `choice + one invariant`.
- Prior teaching basis: AL01 taught copy-as-object and named invariants; this
  question adds the terms extreme and breakdown before the hidden edit.
- Clarity check: clear — choices and the invariant requested are explicit.
- Placement rationale: vocabulary is needed before the learner authors the
  breakdown.

#### AL02-Q2 — Which cells are safe to overwrite?

- Placement: after the hidden edit.
- Ask: In this kite, which region may change while preserving registration:
  the four cells beside the pivot or the pivot and ground columns too?
- Expected answer: Only the four cells beside the pivot; pivot and ground stay
  fixed.
- Answer format: `region + reason`.
- Prior teaching basis: the guided pivot/column contract and hidden pass check.
- Clarity check: clear — the competing regions are named.
- Placement rationale: after execution lets the learner diagnose the artifact.

### Changed-art review

- Variants: a 9-column folded ribbon with a fixed `^` at column 4, and a
  13-column sail with a fixed `o` at column 7. Each supplies two extremes and
  asks for one breakdown; no old glyphs are reused.

### Question audit

- student-can-answer-from-prior-teaching: yes — AL01 supplied scope and
  registration; this lesson defines extremes/breakdown before using them.
- request-is-clear: yes — each stem names the exact region or choice and format.
- placement-makes-sense: yes — Q1 teaches the temporal role; Q2 diagnoses the
  finished registration.

### Rights gate

- integration: blocked — local pose paths are evidence only.
- source use: counts and technique selection only; no Mech or Knight art is
  copied or imitated.
- original exercise: yes — kite and ribbon geometry are new.

## AL03 — Bisect the change with onion-skin comparison

**Map:** H2, H3, H7 · A2  
**Source evidence:** The audit's tutorial evidence records midpoint and partial
merge methods in the archived authoring references; the lesson uses only the
general operation and a new ring.

### Original exercise

Frames are four rows by nine columns. A ring opens from a dot to a four-cell
horizontal oval. Author the in-between that changes one dimension at a time.

```text
    .    
   /|\   
    |    
   / \   
```

Target extreme:

```text
  .---.  
 /     \ 
|       |
 \     / 
```

The in-between must keep the center column fixed and introduce the side walls
before the full top/bottom span.

### Guided sequence

- `key-hidden: no`; duplicate the four-row source as a frame object.
- Open a vertical split with `:vnew`, place source and target side by side, and
  keep their cursor rows aligned; use `:diffthis` only for comparison.
- In the copy, edit the center row first, then the top/bottom corners; do not
  change the center column.
- Close the comparison split only after naming the first visible difference.

### Hidden sequence

- `key-hidden: yes; keys: withheld`.
- Vocabulary: side-by-side comparison, onion skin, midpoint, unchanged anchor,
  one dimension at a time.
- Hint 1 says “compare source and target”; hint 2 says “add side walls before
  completing the span.”
- Pass requires an in-between that is visibly closer to both neighbors than a
  copied extreme and keeps the center column registered.

### Questions

#### AL03-Q1 — What should the onion-skin reveal?

- Placement: before authoring the midpoint.
- Ask: When the dot becomes an oval, which evidence should you compare before
  choosing a cell: only the target, or target plus the unchanged center line?
- Expected answer: Target plus unchanged center line; the center line is the
  registration anchor.
- Answer format: `comparison evidence + anchor`.
- Prior teaching basis: AL01–AL02 taught target visibility, anchors, and changed
  regions; “onion skin” is defined in the stem.
- Clarity check: clear — the two comparison choices and anchor are explicit.
- Placement rationale: before the midpoint so comparison guides the decision.

#### AL03-Q2 — Why is a copied extreme a failed in-between?

- Placement: after review.
- Ask: What evidence distinguishes a real in-between from simply duplicating one
  extreme in this ring: changed spacing, fixed center, or an unrelated subject?
- Expected answer: Changed spacing while the center stays fixed.
- Answer format: `evidence + invariant`.
- Prior teaching basis: the guided side-by-side comparison and hidden pass rule.
- Clarity check: clear — it asks for two observable properties.
- Placement rationale: after seeing the comparison makes diagnosis concrete.

### Changed-art review

- Variants: a 7-column three-stage fan and a 10-column two-stage window. Each
  requires a side-by-side comparison and one midpoint; neither reuses the ring.

### Question audit

- student-can-answer-from-prior-teaching: yes — anchors, changed regions, and
  object scope precede the onion-skin term.
- request-is-clear: yes — questions name evidence and invariant and specify the
  answer shape.
- placement-makes-sense: yes — Q1 prepares comparison; Q2 follows the artifact.

### Rights gate

- integration: blocked — only general midpoint/comparison technique is cited.
- source use: no tutorial frame or glyph arrangement is used.
- original exercise: yes — ring, fan, and window shapes are authored here.

## AL04 — Spacing, holds, and a repeatable stagger

**Map:** H3, H5, H7 · A3, A4  
**Source evidence:** The tutorial archive's animation notes distinguish holds
from dead duplicates; the lesson tests that distinction with original beads.

### Original exercise

Use a six-column, three-row bead with a stationary rail. The bead travels
rightward in four frames; hold frame 2 for two beats and offset the trailing
tail by one column.

```text
o--| 
---| 
---| 
```

The rail `|` stays in column 4 in every frame. The copy/edit must not alter the
rail or frame height.

### Guided sequence

- `key-hidden: no`; copy the three-row object with `3yy`, `p`, and move only the
  `o` one cell right in the copy.
- Create the hold by addressed `:copy` of the whole frame, then use `.` to apply
  the same tail-cell edit to the second held frame.
- Mark timing in a comment outside the art object: `beats 1,2,2,1`.
- Preview at slow speed and decide whether the hold reads as intentional.

### Hidden sequence

- `key-hidden: yes; keys: withheld`.
- Vocabulary: spacing, hold, tail lag, repeatable local edit, stationary rail.
- Hint 1: name the rail and the beat chart; hint 2: “repeat the one-cell tail
  edit on the matching hold.”
- Pass requires four distinct positions, a declared hold, and no rail drift.

### Questions

#### AL04-Q1 — Hold or dead duplicate?

- Placement: before timing the strip.
- Ask: When two adjacent bead frames are identical, what makes the duplicate a
  deliberate hold rather than a mistake: a timing plan or a larger glyph?
- Expected answer: A timing plan that assigns the duplicate a beat.
- Answer format: `choice + test`.
- Prior teaching basis: AL02–AL03 taught distinct poses and comparison; this
  question defines timing evidence before a hold is authored.
- Clarity check: clear — both choices and the test are named.
- Placement rationale: before repetition prevents accidental duplicates.

#### AL04-Q2 — What can repeat at scale?

- Placement: after the hidden edit.
- Ask: Which edit is safe to repeat on the matching hold: the one-cell tail
  change, or the entire frame including the rail?
- Expected answer: The one-cell tail change, bounded to the matching frame;
  the rail is an invariant.
- Answer format: `edit + scope + invariant`.
- Prior teaching basis: guided `.` use and the hidden rail pass rule.
- Clarity check: clear — action, scope, and invariant are explicit.
- Placement rationale: after repeating lets the learner inspect blast radius.

### Changed-art review

- Variants: a drifting flag with a fixed pole and a sliding seed with a fixed
  soil line. Each uses a different beat chart and asks for one held frame plus
  one trailing part.

### Question audit

- student-can-answer-from-prior-teaching: yes — comparison precedes hold
  vocabulary, and guided work demonstrates bounded repeat.
- request-is-clear: yes — the question specifies the candidate edit and scope.
- placement-makes-sense: yes — Q1 sets timing criteria; Q2 checks repeat after
  execution.

### Rights gate

- integration: blocked — source timing language is general method evidence only.
- source use: no source pose or timing strip is copied.
- original exercise: yes — bead, flag, and seed strips are new.

## AL05 — Arc, overshoot, and settle

**Map:** H2, H7, H9 · S4, A4  
**Source evidence:** The local audit prioritizes long pose families because they
  support spacing and arc analysis; no individual pose is reused.

### Original exercise

Animate a four-row pebble from left perch to right perch in a nine-column box.
The center row is the baseline. Use a high arc, an overshoot one cell beyond the
right perch, then a settle back to the perch.

```text
o      o
         
---------
```

The authored target has an original `+` landing mark on each perch; the arc is
judged by center-of-mass spacing, not by copying this diagram.

### Guided sequence

- `key-hidden: no`; make three full-frame copies for high point, overshoot, and
  settle before editing any local cell.
- Use a named mark on each landing row, `mL` and `mR`; use `f+` and `r` for the
  nominated landing cells.
- Preview source → high → right → overshoot → settle. Undo the first variant
  with `u`, make a second arc, and keep the one whose spacing reads best.
- Record why the overshoot is intentional and why the final settle is not a
  dead duplicate.

### Hidden sequence

- `key-hidden: yes; keys: withheld`.
- Vocabulary: arc, spacing, overshoot, settle, landing mark, safe variant.
- Hint 1 names the five temporal roles; hint 2 names “one-cell past the landing,
  then return.” Exact keys stay hidden.
- Pass requires a monotonic arc to the apex, a visible overshoot, and a settle
  frame with a stated timing purpose.

### Questions

#### AL05-Q1 — Where does overshoot belong?

- Placement: before the hidden arc.
- Ask: In a landing sequence, should overshoot happen before the target landing,
  after it, or replace the starting extreme?
- Expected answer: After the target landing and before the settle return.
- Answer format: `position + reason`.
- Prior teaching basis: AL04 established ordered timing and holds; this lesson
  defines overshoot and settle in the stem.
- Clarity check: clear — temporal alternatives are explicit.
- Placement rationale: the learner needs the order before authoring.

#### AL05-Q2 — Which variant survives?

- Placement: after the two-arc comparison.
- Ask: Which arc should be kept: the one with a readable apex and landing
  spacing, or the one with more glyph changes but a broken anchor?
- Expected answer: Readable apex/landing spacing with the anchor intact.
- Answer format: `variant criterion + invariant`.
- Prior teaching basis: H7 comparison and H9 safe exploration were practiced in
  AL03–AL04 and the guided undo cycle.
- Clarity check: clear — criteria and invariant are named.
- Placement rationale: after comparison, because the answer depends on observed
  motion rather than a memorized label.

### Changed-art review

- Variants: a five-row falling leaf with a fixed stem and a four-row swinging
  weight with fixed suspension. Each requires a distinct arc, overshoot, and
  settle, then a safe undo/keep decision.

### Question audit

- student-can-answer-from-prior-teaching: yes — temporal order and comparison
  criteria are taught before the questions.
- request-is-clear: yes — Q1 asks placement; Q2 asks a criterion and invariant.
- placement-makes-sense: yes — Q1 precedes the edit; Q2 follows observation.

### Rights gate

- integration: blocked — pose-set counts inform the need for arc variants only.
- source use: no source silhouette or sequence is reconstructed.
- original exercise: yes — pebble, leaf, and weight are original prompts.

## AL06 — Layer offset, drag, and follow-through

**Map:** H3, H4, H5 · S6, A4  
**Source evidence:** The archived pit material documents back-to-front layers
and separately moving sub-details; the exact 1,122-line plate is blocked. This
lesson uses a new flag-and-pole scene.

### Original exercise

Keep a three-row pole layer fixed while a two-row pennant layer lags one frame
behind the pole and its loose tip follows through after the pole stops.

```text
   |\   
---| \  
   |  \ 
```

Frame width is 9 columns; pole column is 4. A seam is a blank column between
the pole and pennant when they overlap.

### Guided sequence

- `key-hidden: no`; select the pole as one three-row layer and the pennant as a
  separate two-row layer, leaving a blank separator row in the strip.
- Copy the pennant layer with `2yy`, put it after the pole layer, then use a
  Visual-block selection to shift only its registered columns.
- Add a one-frame drag by offsetting the tip, not the pole; use `.` for the
  matching tip cell in the follow-through frame.
- Preview back layer → pole → pennant and inspect the seam at contact.

### Hidden sequence

- `key-hidden: yes; keys: withheld`.
- Vocabulary: layer object, back-to-front order, seam, drag, follow-through,
  column scope.
- Hint 1 names the moving layer; hint 2 says “offset the tip after the pole
  stops.”
- Pass requires the pole column unchanged, a visible drag, a follow-through tip,
  and a preserved separator at contact.

### Questions

#### AL06-Q1 — Which part may lag?

- Placement: before the layer edit.
- Ask: To show drag while preserving the pole's registration, which part may
  change first: the pennant tip or the pole column?
- Expected answer: The pennant tip; the pole column remains fixed.
- Answer format: `part + invariant`.
- Prior teaching basis: AL01's frame/layer object and AL02's fixed pivot provide
  scope and invariant vocabulary.
- Clarity check: clear — two parts and one invariant are named.
- Placement rationale: before selecting a column prevents a destructive scope.

#### AL06-Q2 — Where does the seam go?

- Placement: after the hidden layer edit.
- Ask: At the pole/pennant contact, what keeps layers readable: a blank
  separator column or merging both glyphs into one stroke?
- Expected answer: A blank separator column, unless the plan explicitly calls
  for a contact overlap.
- Answer format: `choice + depth reason`.
- Prior teaching basis: hidden pass rule and guided seam inspection.
- Clarity check: clear — the alternatives and requested reason are explicit.
- Placement rationale: after the edit, because the learner can inspect the
  resulting contact.

### Changed-art review

- Variants: a wheel with a loose spoke layer and a hinged sign with a trailing
  chain layer. Both require column-scoped drag and a seam decision.

### Question audit

- student-can-answer-from-prior-teaching: yes — object scope, fixed landmarks,
  and separators are taught before each question.
- request-is-clear: yes — each stem names the affected part and answer shape.
- placement-makes-sense: yes — Q1 establishes scope; Q2 checks the observed
  composite.

### Rights gate

- integration: blocked — the pit plate is cited as layer-order evidence only.
- source use: no pit, cultist, candle, or particle layer is copied.
- original exercise: yes — pole, pennant, wheel, sign, and chain are new.

## AL07 — Close the loop without a seam pop

**Map:** H1, H3, H8, H9 · S2, A6, A7  
**Source evidence:** The tutorial archive discusses preview, padding, and loop
settle in its animation sections; the pack applies those decisions to a new
four-frame rotating tile.

### Original exercise

Build four equal 5×7 frames of a hollow tile turning a quarter-step. Frame 4
must settle into frame 1 without a one-column jump. The pivot is `+` at row 3,
column 4.

```text
 .---. 
| + | 
 '---' 
  |   
```

All four frames are original and must remain 7 columns wide. Hand-reverse the
turn for the return half; do not use a grid flip.

### Guided sequence

- `key-hidden: no`; duplicate the complete 5×7 object into four frame blocks.
- Change one edge at a time with overwrite commands; keep the pivot and frame
  bounds fixed.
- Use `:set virtualedit=onemore` only if inspecting a trailing cell, then
  remove the option before the final check.
- Compare frame 4 to frame 1, delete accidental trailing spaces, and replay
  forward then reverse. Use `u` to explore one seam variant safely.

### Hidden sequence

- `key-hidden: yes; keys: withheld`.
- Vocabulary: loop seam, equal bounds, hand mirror, reverse reuse, trailing
  whitespace, safe undo.
- Hint 1 names the pivot and frame size; hint 2 says “compare last to first,
  then remove the cell that jumps.”
- Pass requires equal frame widths, no trailing spaces, a readable reverse, and
  no seam pop at the loop boundary.

### Questions

#### AL07-Q1 — What must match at the seam?

- Placement: before cleanup.
- Ask: Which comparison catches a loop pop first: frame 4 versus frame 1 at the
  pivot and bounds, or frame 2 versus an unrelated drawing?
- Expected answer: Frame 4 versus frame 1 at the pivot and bounds.
- Answer format: `comparison pair + two checks`.
- Prior teaching basis: AL01 fixed bounds, AL03 introduced side-by-side
  comparison, and AL05 introduced safe variant choice.
- Clarity check: clear — the pair and checks are specified.
- Placement rationale: before cleanup gives a concrete seam test.

#### AL07-Q2 — Why remove trailing spaces?

- Placement: after cleanup.
- Ask: What does removing trailing spaces protect here: equal visible frame
  width and deterministic comparison, or a new animation pose?
- Expected answer: Equal visible frame width and deterministic comparison.
- Answer format: `purpose + affected contract`.
- Prior teaching basis: H8 and the guided cleanup just demonstrated.
- Clarity check: clear — one purpose and one contract are requested.
- Placement rationale: after cleanup ties the housekeeping to the observed seam.

### Changed-art review

- Variants: a 6×9 rotating diamond with a fixed center and a 4×8 folding tab
  with a fixed hinge. Each requires forward/reverse playback and last/first
  comparison.

### Question audit

- student-can-answer-from-prior-teaching: yes — bounds, comparison, and safe
  undo were established in AL01, AL03, and AL05.
- request-is-clear: yes — stems specify the comparison and answer format.
- placement-makes-sense: yes — Q1 precedes seam repair; Q2 follows cleanup.

### Rights gate

- integration: blocked — tutorial preview/padding ideas are general only.
- source use: no tutorial tile, logo, or HTML art is reproduced.
- original exercise: yes — hollow tile, diamond, and tab are new.

## AL08 — Column repair, padding, and readable ground

**Map:** H1, H4, H8 · S0, S7, A5  
**Source evidence:** The archived tutorial describes repeated ground/material
patterns and subtraction; its HTML and inline brick material are blocked. This
lesson creates a new rail and shadow vocabulary.

### Original exercise

Make a four-row, 12-column ground strip. A three-column shadow advances one
column per frame; the top row is a fixed rail, and every frame is padded to 12
columns.

```text
------------
..  ..  ..  
  ___      
____________
```

The only animated feature is the `___` shadow. Do not insert lines or change
the rail, bottom ground, or frame width.

### Guided sequence

- `key-hidden: no`; select the shadow column with Visual block mode and replace
  it in place; verify the fixed rail/bottom columns.
- Duplicate the complete frame with `:t$`; use a bounded range substitution for
  the shadow material, never `%`.
- Run the cleanup conceptually equivalent to `:%s/\\s\\+$//e` only on a copy;
  then pad every frame to 12 columns with explicit spaces in the art contract.
- Preview the ground at two speeds and reject any shadow that reads as a new
  object rather than a moving value.

### Hidden sequence

- `key-hidden: yes; keys: withheld`.
- Vocabulary: Visual block, column scope, bounded range, trailing whitespace,
  pad, ground material.
- Hint 1 names the shadow columns; hint 2 says “copy the frame, then apply a
  bounded material edit.”
- Pass requires fixed rail/bottom, equal 12-column frames, and one moving shadow.

### Questions

#### AL08-Q1 — Which scope is safe?

- Placement: before column editing.
- Ask: To move only the shadow, is the safe scope its selected columns or the
  entire file with a global substitute?
- Expected answer: The selected shadow columns in the nominated frame range.
- Answer format: `scope + blast-radius reason`.
- Prior teaching basis: AL06 taught column-scoped layer edits; AL04 taught
  bounded repeat.
- Clarity check: clear — safe and unsafe scopes are named.
- Placement rationale: before the first command prevents a whole-strip edit.

#### AL08-Q2 — What does padding preserve?

- Placement: after the hidden cleanup.
- Ask: Why pad all frames to 12 columns: to preserve registration/comparison, or
  to make the shadow taller?
- Expected answer: To preserve registration and deterministic comparison.
- Answer format: `purpose + invariant`.
- Prior teaching basis: AL01 bounds and AL07 seam cleanup.
- Clarity check: clear — two alternatives and one invariant are explicit.
- Placement rationale: after cleanup connects spacing to artifact correctness.

### Changed-art review

- Variants: a 10-column waterline with a two-cell glint and a 14-column stone
  floor with a diagonal shade. Each requires column-scoped movement, pad, and
  cleanup without changing the ground material.

### Question audit

- student-can-answer-from-prior-teaching: yes — column scope, bounded repeat,
  registration, and cleanup precede the questions.
- request-is-clear: yes — the requested scope/purpose and answer formats are
  explicit.
- placement-makes-sense: yes — Q1 gates scope; Q2 follows padding.

### Rights gate

- integration: blocked — brick/ground tutorial material is method evidence only.
- source use: no HTML brick or extracted ground block is copied.
- original exercise: yes — rail, shadow, waterline, and floor are new.

## AL09 — Build a palette and compare material variants

**Map:** H5, H6, H9 · S5  
**Source evidence:** The tutorial archive teaches that a material's glyph set
  should remain coherent; its exact glyph table is not adopted. The pack uses
  named registers as a Neovim exercise.

### Original exercise

Create a three-row, nine-column reed using a palette of `.` (dust), `:` (mid),
and `#` (dark). The silhouette stays fixed while two material variants swap
  only internal cells.

```text
  ||   
 /##\  
..::..
```

Variant A is sparse (`.`/`:`), variant B is dense (`:`/`#`). No frame may mix
the two palettes without an explicit note.

### Guided sequence

- `key-hidden: no`; place `. : #` in named registers using `"add`, `"amm`, and
  `"adk` (or record an equivalent palette table if the operator's maps differ).
- Copy the complete frame into two variants; use `<C-r>a`, `<C-r>m`, and
  `<C-r>k` only inside nominated cells.
- Compare both variants side by side and undo a noisy substitution before
  selecting one.
- Record the chosen material contract: “dust, mid, dark; no unplanned mix.”

### Hidden sequence

- `key-hidden: yes; keys: withheld`.
- Vocabulary: named register, palette contract, internal material, variant,
  safe undo.
- Hint 1 names three material roles; hint 2 says “retrieve the named glyph,
  then replace only an internal cell.”
- Pass requires a stable palette, unchanged silhouette, and a written reason for
  the selected variant.

### Questions

#### AL09-Q1 — What belongs in the palette?

- Placement: before register authoring.
- Ask: Which palette is coherent for this reed: three named density roles used
  consistently, or every visually interesting glyph available?
- Expected answer: Three named density roles used consistently.
- Answer format: `choice + three roles`.
- Prior teaching basis: AL08 taught material consistency and bounded region;
  this lesson names the register mechanism before use.
- Clarity check: clear — choice and role count are explicit.
- Placement rationale: before storing registers, so the learner knows what to
  name.

#### AL09-Q2 — Which variant is safe to keep?

- Placement: after comparison.
- Ask: Which variant is safer: one with a coherent palette and unchanged
  silhouette, or one with more symbols but an altered outline?
- Expected answer: Coherent palette with unchanged silhouette.
- Answer format: `variant criterion + invariant`.
- Prior teaching basis: H7 comparison from AL03 and H9 safe selection from AL05.
- Clarity check: clear — the criteria and invariant are named.
- Placement rationale: after seeing both variants, because it requires judgment.

### Changed-art review

- Variants: a four-row lantern using `·`, `+`, `*`, and a six-row woven gate
  using `.` `:` `=`. Each requires a named palette and one safely selected
  internal-material variant.

### Question audit

- student-can-answer-from-prior-teaching: yes — consistency, comparison, and
  safe variant criteria precede both questions.
- request-is-clear: yes — palette count and variant criteria are specified.
- placement-makes-sense: yes — Q1 precedes register use; Q2 follows comparison.

### Rights gate

- integration: blocked — only the general material-consistency principle is
  cited; no source glyph table is copied.
- source use: exact source palettes and page art remain excluded.
- original exercise: yes — reed, lantern, and gate are new.

## AL10 — Hand-mirror an asymmetric action

**Map:** H2, H3, H4 · S2, A6  
**Source evidence:** The tutorial archive warns that manual mirroring matters
  because glyphs are not symmetric. The source's characters are not copied.

### Original exercise

Create a five-row, 11-column scoop action with an asymmetric `>` latch. Reverse
the action by hand so the latch becomes `<`, the arm order reverses, and the
center body remains registered.

```text
   ___>   
  /   \   
 |  o  |  
  \___/   
    |     
```

The central `o` is the registration cell; frame width stays 11 columns.

### Guided sequence

- `key-hidden: no`; copy the complete five-row frame before making a reverse.
- Use a Visual block selection to inspect columns, then hand-replace each
  directional glyph; do not use a grid flip or external transform.
- Search for the center `o` and verify its column in both frames.
- Preview forward/reverse and mark any latch pop for a safe variant pass.

### Hidden sequence

- `key-hidden: yes; keys: withheld`.
- Vocabulary: hand mirror, asymmetric glyph, registration cell, column scope,
  reverse reuse.
- Hint 1 names the latch and arm order; hint 2 says “rewrite each directional
  glyph by hand around the fixed center.”
- Pass requires reversed directional meaning, unchanged center column, and no
  accidental row insertion.

### Questions

#### AL10-Q1 — Why not flip the grid?

- Placement: before the mirror edit.
- Ask: Why is a manual mirror required for the scoop: directional glyphs carry
  meaning, or because the frame must become taller?
- Expected answer: Directional glyphs carry meaning and are not symmetric under
  a blind grid flip.
- Answer format: `reason + affected glyph class`.
- Prior teaching basis: AL01 fixed objects and AL06 columns; the lesson defines
  asymmetric glyphs before asking.
- Clarity check: clear — reason and class are requested.
- Placement rationale: before the operation prevents an invalid shortcut.

#### AL10-Q2 — What must not move?

- Placement: after reverse authoring.
- Ask: Which landmark proves the mirror stayed registered: the center `o` column
  or the outer latch column?
- Expected answer: The center `o` column; the latch is intentionally reversed.
- Answer format: `landmark + intentional change`.
- Prior teaching basis: guided mirror and hidden pass contract.
- Clarity check: clear — one invariant and one changed feature are named.
- Placement rationale: after authoring lets the learner verify the artifact.

### Changed-art review

- Variants: a left/right hooked lever with a fixed rivet and a five-row wing
  fold with a fixed shoulder. Each requires hand reversal of asymmetric glyphs.

### Question audit

- student-can-answer-from-prior-teaching: yes — object, column, and landmark
  contracts are established before mirror vocabulary.
- request-is-clear: yes — each asks for one reason or landmark/change pair.
- placement-makes-sense: yes — Q1 prevents the shortcut; Q2 checks the result.

### Rights gate

- integration: blocked — the manual-mirror principle is general; no source
  character is copied.
- source use: no tutorial character, pose, or glyph sequence is reproduced.
- original exercise: yes — scoop, lever, and wing are original.

## AL11 — Subtract, reorder, and retain frame objects

**Map:** H3, H5, H8, H9 · S3, A5  
**Source evidence:** Archived tutorial notes describe subtractive authoring and
  reordering playback. The exact tutorial build plate is blocked.

### Original exercise

Start with a finished six-row, nine-column tower. Make a three-frame build by
copying the complete tower and clearing one upper band per frame; then reorder
the frames so playback grows upward.

```text
   /\\   
  /##\\  
 /####\\ 
 | || |  
 | || |  
_||||||_
```

Rows and columns are fixed; clearing means overwriting cells with spaces, not
deleting rows.

### Guided sequence

- `key-hidden: no`; select all six lines and save the object in a named register.
- Make two full-frame copies. On each copy, use blockwise selection plus
  overwrite to clear only the next upper band.
- Use `:m` on complete frame ranges to put the seed first and the finished tower
  last; inspect blank separators after moving.
- Undo one wrong ordering, redo it, and run the equal-height/padding check.

### Hidden sequence

- `key-hidden: yes; keys: withheld`.
- Vocabulary: subtractive edit, clear-not-delete, frame object, range move,
  playback order, separator.
- Hint 1 says “preserve six rows”; hint 2 says “move complete ranges, not
  individual art rows.”
- Pass requires a visibly growing playback order, equal frame heights, and no
  lost separator or instruction text.

### Questions

#### AL11-Q1 — Clear or delete?

- Placement: before the subtractive edit.
- Ask: To preserve fixed-height frames, should an upper band be overwritten with
  spaces or deleted with `dd`?
- Expected answer: Overwritten with spaces; deleting a row changes the object.
- Answer format: `operation + frame-height reason`.
- Prior teaching basis: AL01 fixed object bounds and AL08 separated cleanup from
  structural edits.
- Clarity check: clear — operations and consequence are explicit.
- Placement rationale: before the destructive temptation.

#### AL11-Q2 — Which order plays as a build?

- Placement: after range moves.
- Ask: Which order reads as growth: seed → partial → finished, or finished →
  partial → seed?
- Expected answer: Seed → partial → finished.
- Answer format: `order + visual effect`.
- Prior teaching basis: guided subtractive frames and A5 vocabulary.
- Clarity check: clear — the two orders and requested effect are stated.
- Placement rationale: after moving ranges makes playback evidence available.

### Changed-art review

- Variants: a five-row bridge assembled by removing planks and a seven-row
  spiral assembled by clearing rings. Each requires complete-object copies,
  clear-not-delete edits, and a reordered build.

### Question audit

- student-can-answer-from-prior-teaching: yes — object bounds, cleanup, and
  subtractive vocabulary are taught before the questions.
- request-is-clear: yes — each asks for a binary operation or an explicit order.
- placement-makes-sense: yes — Q1 guards the edit; Q2 follows playback reorder.

### Rights gate

- integration: blocked — subtractive/reorder technique is general only.
- source use: no tutorial build-up plate is copied or reconstructed.
- original exercise: yes — tower, bridge, and spiral are new.

## AL12 — Original capstone: a 4+4+2 registered loop

**Map:** H1–H9 · S0–S7, A0–A7  
**Source evidence:** The source audit identifies long animation sets as useful
  evidence for a capstone's need for timing, holds, layers, and review. The
  archived tutorial's walk-cycle discussion is a method reference only. This
  capstone is an original “signal seed” and shares no source silhouette.

### Original exercise

Plan and author a 10-frame signal-seed loop in a 9×13 fixed box. Timing is
**4+4+2**: four beats on the rising contact, four on the falling contact, and
two on the settle. The anchor is the bottom `+` in column 7. The shot must
include: two extremes, one breakdown, at least one in-between, a moving hold,
an arc, a one-cell overshoot/settle, a dragged side mark, a layer seam, and a
loop comparison.

The seed starts as this original key pose:

```text
     .     
    /|\    
   / | \   
  -- + --  
     |     
```

The learner chooses the changed glyphs and timing chart; no source frame is
provided as a visual answer.

### Guided sequence

- `key-hidden: no`; write a one-line plan naming subject, 9×13 bounds, anchor,
  extremes, breakdown, timing, and loop test before touching the art.
- Author two complete extreme objects, copy them into the strip, and add a
  breakdown/in-between by comparing both neighbors.
- Add a four-beat hold, a one-cell overshoot, and two settle frames. Keep the
  anchor and seam column registered; use named registers for the chosen palette.
- Make a second variant safely with `u`/redo, choose it by side-by-side
  comparison, then clean/pad all frames and preview forward/reverse.
- Run a final ledger: frame objects, layer objects, columns, repeated edits,
  palette, comparison, cleanup, and variant rationale.

### Hidden sequence

- `key-hidden: yes; keys: withheld`.
- Vocabulary: plan → extremes → breakdown → in-between → hold → arc →
  overshoot/settle → drag → seam → pad → preview.
- Hint 1 names only the next decision; hint 2 names the required anchor or
  layer scope; exact command keys remain hidden.
- Pass requires an original 10-frame loop, readable 4+4+2 timing, fixed box,
  no dead duplicate, and a written diagnosis of any remaining jitter.

### Questions

#### AL12-Q1 — Is the plan complete enough to start?

- Placement: before capstone authoring.
- Ask: Which plan is actionable: “make a cool loop,” or “9×13 seed, bottom
  anchor, two extremes, one breakdown, 4+4+2 timing, and a loop check”?
- Expected answer: The second plan because it names bounds, anchor, poses,
  timing, and a test.
- Answer format: `choice + five named plan fields`.
- Prior teaching basis: AL01–AL11 have taught each field separately; this is an
  explicit retrieval check before the original task.
- Clarity check: clear — choices and required fields are visible.
- Placement rationale: before drawing, because planning is the A0 gate.

#### AL12-Q2 — What proves mastery after preview?

- Placement: after capstone review.
- Ask: Which evidence is sufficient: a matching final frame, or a changed-art
  review showing timing, registration, comparison, cleanup, and a safe variant?
- Expected answer: The changed-art review with timing, registration,
  comparison, cleanup, and safe-variant evidence; final pixels alone are not
  method proof.
- Answer format: `evidence bundle + why final pixels alone fail`.
- Prior teaching basis: every earlier lesson separated artifact correctness from
  method/decision evidence; this question gathers the finish line.
- Clarity check: clear — alternatives, evidence fields, and explanation format
  are explicit.
- Placement rationale: after preview, because the learner can cite the actual
  ledger and changed variant.

### Changed-art review

- Variants: (1) a 9×13 “signal seed” with a diagonal arc and side drag, and (2)
  a 9×13 “hinged glow” with a vertical arc and delayed top layer. Both require
  the same S/A and H coverage but different glyph choices, anchors, and timing.
- Review sequence: hide exact keys; ask the learner to plan, author, compare,
  preview, and explain one rejected variant. A pass must name the one decision
  that changed between variants and the invariant that did not.

### Question audit

- student-can-answer-from-prior-teaching: yes — each plan field and evidence
  type was explicitly taught in AL01–AL11; no new term is required.
- request-is-clear: yes — Q1 requests fields; Q2 requests an evidence bundle
  and a reason, with formats stated.
- placement-makes-sense: yes — Q1 is a preflight gate; Q2 follows the final
  preview and ledger.

### Rights gate

- integration: blocked — no exact corpus, tutorial HTML, pit scene, Sapling &
  Ramparts, worm, dome, brick, logo, or extracted plate is used.
- source use: research evidence selects the skill coverage only; all art and
  wording in this capstone are original.
- original exercise: yes — signal seed and hinged glow are author-created.

## Integration handoff contract

This file is intentionally standalone. The owning curriculum workflow may later
translate lessons into cards, but must preserve: (a) the `key-hidden` boundary;
(b) the exact answer format and question-placement audit; (c) two changed-art
variants; (d) H1–H9 and S0–S7/A0–A7 links; (e) fixed-width frame/layer
registration; and (f) `integration: blocked` for every unresolved source. The
focused validator is `share/test_animation_lesson_pack.py`.
