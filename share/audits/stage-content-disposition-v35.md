# Revision .35 still-stage content disposition

This audit separates the new stage scheduler from the older lesson content it
currently schedules. It answers one narrow question for every S0-S7 card whose
prompt contains an explicit temporal term: is the card a non-playing still
study/variant, or does it genuinely ask the learner to author animation before
A0? The prompt-term scan is only the intake list; the disposition below is the
manual decision.

Legend:

- `KEEP-STILL`: a copied block is a non-playing working copy, candidate still,
  palette take, or diagnostic view. Retain it in S after making that boundary
  explicit in the card.
- `REWORD`: the exercise is still work, but generated prose falsely calls it an
  animation/loop/frame. Rewrite the card and its manually authored questions.
- `MOVE-A`: the card performs timing, in-betweening, playback, or temporal pose
  change and belongs at A0 or later.
- `REBUILD-STAGE`: moving the card exposes a missing still lesson; add the named
  still exercise before claiming the stage is complete.

## S0 — Grid and overwrite

| card | disposition | evidence / required change |
|---|---|---|
| M0.SL | KEEP-STILL | One row-scoped substitute on one supplied drawing; rename “changed frame” to “changed still”. |
| M11.02 | KEEP-STILL | Its duplicate metadata already says `scaffold`, `playback=false`; call the copy a second redraw take, not a second pose. |
| M11.WS | KEEP-STILL | One padded missile still; “frame” is source identity, not playback work. |
| M11.UT | KEEP-STILL | Undo-tree comparison of two eye takes; only one state is saved. |
| M11.WSH | KEEP-STILL | Whitespace cleanup on one complete Chick pose. |
| M11.UTH | KEEP-STILL | Undo-tree comparison of two SnowBunny eye takes; only one state is saved. |
| M11.07 | REWORD | Generic “preserves intended animation” diagnosis must instead test fixed-grid redraw invariants. |
| M11.08 | MOVE-A | Aligning motion blur “across both complete frames” is temporal authoring. Move to A3/A4 and add an S0 fixed-grid checkpoint that uses one still. |

## S1 — Stroke runs

| card | disposition | evidence / required change |
|---|---|---|
| M1.02 | KEEP-STILL | Non-playing working copy for a second hand-drawn contour candidate. |
| M1.DD | KEEP-STILL | Removes an accidental duplicate candidate; no playback decision is required. |
| M1.04 | KEEP-STILL | Hand-authors the opposite contour as a comparison still; forbid treating the pair as a loop. |
| M1.07 | REWORD | Generic animation diagnosis must become line-quality/stroke-material diagnosis. |

## S2 — Hand mirroring

| card | disposition | evidence / required change |
|---|---|---|
| M19.01 | KEEP-STILL | Explicit five-row key-pose still. |
| M19.02 | REWORD | Calls the copied still an “animation extreme”; it is a non-playing opposite-facing candidate at S2. |
| M19.03 | KEEP-STILL | Reads a mirror key-pose still. |
| M19.06 | KEEP-STILL | Hidden full-row hand mirror on unfamiliar still art. |
| M19.07 | REWORD | Generic animation diagnosis must test hand-mirror glyph and spacing decisions. |
| M19.08 | KEEP-STILL | Prompt explicitly says the third candidate must not become premature playback. |

## S3 — Block a still

| card | disposition | evidence / required change |
|---|---|---|
| M2.07 | REWORD | Generic animation diagnosis must test silhouette/readability and bounded edit scope. |
| M2.08 | KEEP-STILL | Closed-eye result is an expression candidate still; do not call or preview it as a blink here. |

## S4 — Joint heights

| card | disposition | evidence / required change |
|---|---|---|
| M12.02 | MOVE-A | Creates a second staggered key pose. |
| M12.04 | MOVE-A | Metadata and prompt explicitly teach drag/in-between timing. |
| M12.07 | MOVE-A | Diagnoses the Joint Sweep animation. |
| M12.08 | MOVE-A | Authors an opposite-side loop exit. |

`REBUILD-STAGE`: M12.01/FIND/05/06 teach character landmarks and paired-joint
scope, but they do not teach the S4 authoring contract from the master plan:
joint glyph height (`.` too low, `'` too high, `:` centred), off-vertical
anti-aliasing with `¡ ! . '`, and column-true `<C-v> r` / `gv` work on a single
still. S4 needs a guided still, a key-hidden unfamiliar still, a changed-art
review, and a stage checkpoint for those exact decisions before the four timing
cards move to A4.

## S5 — Variants and palette

| card | disposition | evidence / required change |
|---|---|---|
| M14.01 | KEEP-STILL | First saved material candidate, not a playback pose. |
| M14.DAP | KEEP-STILL | Deletes an accidental duplicate candidate from a still-variant sheet. |
| M14.04 | KEEP-STILL | Second material candidate. |
| M14.PARA | KEEP-STILL | Copies one blank-line-separated still object. |
| M14.DAPH | KEEP-STILL | Removes one duplicate candidate from an unfamiliar still sheet. |
| M14.07 | REWORD | Generic animation diagnosis must test palette/material consistency. |
| M14.08 | REWORD | “variant sequence returns” implies playback; make it a three-candidate palette comparison with no timing claim. |

## S6 — Layers and seams

| card | disposition | evidence / required change |
|---|---|---|
| M5.04 | MOVE-A | Explicitly swings the copied foreground while keeping a pivot registered. |
| M5.07 | MOVE-A | Diagnoses the layered sequence as animation. |

`REBUILD-STAGE`: keep M5.01, M5.C, and M5.06 as still layer/seam work. Inspect
M5.02/03/05/08 and their questions manually: any requirement to move the blade,
compare temporal poses, or preview a sequence moves to A3/A4. S6 still needs a
module/stage check that grades back-to-front layer order, material rules, and
negative-space seam separation on one unfamiliar composite.

## S7 — Texture and ground

| card | disposition | evidence / required change |
|---|---|---|
| M15.02 | KEEP-STILL | Non-playing material-stack copy used to compare a lighter offset treatment. |
| M15.ZPH | KEEP-STILL | Ragged block copy of one complete Chick pose. |
| M15.07 | REWORD | Generic animation diagnosis must test dither/ground/shadow material rules. |
| M15.08 | MOVE-A | “registered starting frame” and “lighter settle row” create a temporal settle. Move to A4 or rewrite as a non-playing macro-generated material variant. |

## Enforcement still required

The next content patch must add explicit `artifact_mode` values (`still-study`,
`animation-strip`, or `optional-proportional`) and reject an S-stage card whose
mode is `animation-strip`. `duplicate_frames.playback=false` is supporting
evidence for a working copy, not a substitute for the card-level declaration.
Questions move with their card and must be manually rewritten; changing only a
stage label or prompt is not a valid disposition.

## Revision .36 disposition result

Revision `.36` implements the first migration slice and corrects one omission
in the table above:

- `M12.02`, `.03`, `.04`, `.05`, `.07`, and `.08` now belong to A4. The
  original audit missed `.05`; its copied release scaffold and comparison of
  temporal results make it animation work too.
- S4 receives four individually authored cards: `M12.AA` for the full
  `¡ ! . '` off-vertical palette, `M12.JH` for centred joint height with
  blockwise `r`, `M12.GV` for candidate refinement with `gv`, and hidden
  checkpoint `M12.JHH` with two changed-art reviews.
- `M11.08` moves to A3; `M5.04` and `M5.07` move to A3; `M15.08` moves to A4.
- Every generated card now carries `artifact_mode`. Generation rejects an
  S-stage animation-strip, and separately rejects temporal authoring language
  in an S-stage task prompt.
- The remaining KEEP-STILL/REWORD prompts in S0-S3 and S5-S7 were rewritten
  one by one as candidate stills, drawing plates, material studies, or
  paragraph-separated still objects. This is wording cleanup only where the
  audit classified the operation as still work; no temporal operation was
  hidden by renaming it.

The generated `.36` S0-S7 task prompts contain zero matches for `animation`,
`playback`, `loop`, `tween`, `frame`, or `motion`. Questions still make the
animation relevance explicit, but the executable task does not ask the learner
to author timing before A0.

Revision `.37` closes the S6 rebuild item with `M5.S6C`: one unfamiliar
four-row composite whose cloud, roof, and ground retain distinct material
languages while the learner removes exactly one background cell at the false
cloud/roof connection. Its hidden `f/`, `h`, `r<Space>` path is required, its
paired question prints the complete composite, and two changed-material reviews
repeat the seam decision. The card passes headed at 80x24, 100x36, and 188x49.
