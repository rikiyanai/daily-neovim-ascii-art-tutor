# Socratic course audit — revision 2026-09-28.22

Status: review, log, and proposal only. This file changes no generator,
runtime, test, or curriculum data. It is the operator gate before any such
implementation work.

## Scope and method

I re-read the finish-line brief in
`/Users/r/.codex/attachments/499fbe13-648c-423a-855d-39c9339aede0/pasted-text-1.txt`
in full. The audit target is the generated `.22` file, not the older `.19`
count in `FAILURE_LOG.md` or an earlier partition report. The generated file
contains 19 modules, 152 cards, 114 executable cards, 38 conceptual cards,
and 190 questions (`share/curriculum-v2.json:1-6,594-13678,13855-20828`).
Exactly 57 cards own `question_ids` (38 `.03`/`.07` concept cards and 19
`.08` checks); the other 95 cards own none. All 190 questions are four-choice
multiple choice: there are no open typed-key, decode, complete, predict, or
why items in the current data. Thirty-one executable cards have explicit
`review_variants` (62 variants), and all 19 transfer cards have two changed-art
`variants`, so 50/114 executable cards are source-linked review-capable and 64
have no changed-art review bank. These counts are direct `.22` counts, not
copied from the earlier VD-12 total.

The strict teaching test is:

```text
grammar explanation → interpretation → completion → guided visible keys
→ paired performance question → exact-key-hidden retrieval
→ changed-art spaced review
```

An answer key, recipe, distractor, random question pool, source citation, or
attached legacy lesson is not a stage. A question counts as paired only when
the same performance attempt requires it; a nearby `.03`, `.07`, or `.08`
question does not count. A review variant counts as a review fixture, but the
current scheduler runs it after the source pass and the module check does not
require it before mastery (`share/v2_runtime.py:1412-1442,1885-1933`).

## Finish-line coverage ledger

The current schema has no machine-readable habit or S/A-stage field. The
following mapping is therefore an audit classification of the current card
contracts, not a claim that the generator enforces it. `H1`–`H9` use the
operator's nine habits in the attachment; a module can serve more than one.

| Code | Finish-line habit or stage | Current semantic homes | Hidden + changed-art finding |
|---|---|---|---|
| H1 | Overwrite, never insert | M0, M11, M18 | M11.04/M11.08 and M18.04 have hidden paths plus variants, but no grammar/completion pairing; no integrated S0 proof. |
| H2 | Land on an exact cell | M1, M4, M10, M12, M13, M17 | Some transfer/check cards review landmark edits, but no typed-key effect grading and no family ledger. |
| H3 | Treat each frame/layer as an object | M0, M3, M5, M6, M14, M16 | `yy/p`, `yap`, `:t`, and `:m` are hidden in several first-use paths; review is not required before mastery. |
| H4 | Edit columns | M4, M5, M11, M15 | Visual-block and fixed-grid work lacks a prior guided paired lesson; no all-habit coverage assertion. |
| H5 | Repeat edits instead of redoing | M7, M11, M12, M13, M17 | Dot, `;`/`,`, and macro paths first appear hidden or without completion; no open-key repeat grading. |
| H6 | Keep a glyph palette in registers | M14 | Named-register and `<C-r>` paths have variants on some cards, but no paired decode/complete stage. |
| H7 | Compare frames | M4/M5/M9 conceptually | No current card requires `:diffthis`, a scroll-bound split, or an onion-skin comparison; H7 has no qualifying hidden + spaced review. |
| H8 | Clean up and pad | M8/M15 conceptually | No current card requires the finish-line trailing-whitespace cleanup `:%s/\s\+$//e` or `>` with `shiftwidth=1` as a hidden reviewed habit. |
| H9 | Explore variants safely | M3/M6/M14/M16/M18 | `:t`/`:m` appear, but undo-tree `g-`, `g+`, `:earlier` and a reviewed variant decision are absent. |
| S0 | Grid/glyph alphabet; overwrite medium | M0/M11 | Partial hidden overwrite evidence; no explicit S0 label or complete reviewed habit bundle. |
| S1 | Stair-step slopes and typed runs | M1/M10 | No dedicated hidden reviewed counted `R`/typed-run lesson; proportional SJIS work is not the same stage. |
| S2 | Hand mirroring | M12 and M18 | M18 hand-mirror is hidden and reviewed, but it is labelled A6; M12 is bilateral accent timing, not full S2. |
| S3 | Block a still and clear unsure cells | M2/M13 | Local edits exist; no stage-owned typed-key + changed-art coverage record. |
| S4 | Joint heights/anti-aliased near-verticals | M4/M12 | M4.08/M12.04 variants exist, but Visual-block grammar is first hidden and no completion item precedes it. |
| S5 | Variants/material/symbol table | M14 | M14 has reviewed cards, but no paired register grammar and no stable hidden habit claim. |
| S6 | Layers and seams | M5 | M5.06 has transfer variants; no stage metadata and no required reviewed layer comparison. |
| S7 | Dither/brick/shadow/isometric ground | M15 | M15 has variants, but `:set`/`>>` and block/range syntax are not grammar-first. |
| A0 | References, key pose, size test, written plan | M0/M16 | M16.02/.08 have variants, but `:read`, labels, and plan grammar are not paired before use. |
| A1 | Extremes first; copy then vary | M1/M2 | Art progression exists; no card-level hidden+review stage field. |
| A2 | Midpoint/bisecting/onion skin/symmetry | M3/M4 | Midpoint work exists; H7 onion-skin command is absent. |
| A3 | Keep unchanged glyphs identical across frames | M17 | M17 has reviewed cards, but search/`n`/dot grammar and macro pairing are absent. |
| A4 | Holds, stagger, overshoot, drag; no dead frame | M5/M7/M8/M9 | Holds/overshoot are exercised, but only some source cards have variants and no dead-frame reviewed requirement is enforced. |
| A5 | Subtractive build, playback order, padding | M6/M8 | `:m`/`D` are hidden-first; padding/cleanup habit is absent. |
| A6 | Mirrored action, reuse by reversal | M7/M18 | M18.01/.04/.08 have variants, but expression validation and `:t` lack grammar pairing. |
| A7 | Preview, jitter, polish; original 4+4+2 walk | M8/M9 | No reviewed capstone requires the complete A7 bundle; current checks are module-local. |

### Structural verdict

The current cards contain useful art contracts, but the finish line is not
met. H7 and H8 are absent as executable reviewed habits; H9 is partial. All
S/A stages lack an owned coverage link, and several have only a related card
rather than a stage-specific hidden retrieval plus changed-art review. The
current `.22` data also violates the method requirement globally: every
question is multiple choice, ordinary performance cards have no paired
question, and no command family has an explicit grammar → interpretation →
completion contract.

## Per-card audit matrix and proposal

Legend: `G` = visible guided card, `I` = interpretation, `C` = completion,
`H` = exact-key-hidden retrieval, `R2` = two changed-art review fixtures,
`R0` = none. `P0` means no paired question is owned by the current card;
`P-MC` means the card owns the existing multiple-choice pool, but not a
grammar/completion pair. The question after `Q:` is the full proposed text;
the parenthetical form and placement are part of the proposal. Every row has
at least one question. `Before` means before the card's edit, `After` means
after its artifact result, and `Both` means two short prompts around it.

### M0 — Spark loop (`S0/A0`; H1/H3)

Source card lines: `share/curriculum-v2.json:594-1207`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M0.01 (G; :594) | New `j`, `0`, `f{char}`, `r{char}` (standalone motions/replace). Visible recipe is the first use, with no prior I/C; not worked out first. | G only; P0; later hidden use; R2 (after pass). | Q: “You are on the top ray. Move to the acting row, find the visible dot, and replace only it. Type keys; any scratch-buffer path with the same cursor/result passes.” (open typed-key, **Before**). Q: “Why is `r` safer than `x` for this cell?” (why, **After**). Effect grading teaches exact-cell grammar before revealing the recipe. |
| M0.02 (G; :722) | New `gg`, `3yy`, `p`, and `:[range]s/pat/repl/g<CR>`. Recipe/key vocabulary is shown, but no prior parse question; `:s` is not worked out before typing. | G only; P0; hidden M0.04; R0. | Q1: “Starting at the top, copy this complete three-row frame and put it below. Type the keys; row/block result, not spelling, is graded.” (open typed-key, **Before**). Q2: “Decode `:4,6s/o/O/g<CR>`: what are the range, command, pattern, replacement, flag, and execution key?” (decode, **Before**). Q3: “Why does `3yy` matter here, and what would `p` do?” (why, **After**). The range question must precede the first shown `:s`. |
| M0.03 (C; :823) | No new edit; current five-question MC pool only interprets prior work. | P-MC; no H/R. | Q: “Complete `:8s/-/=/___<CR>` so every dash on row 8 changes; state what `g` contributes.” (complete, **Before** the conceptual decision). It makes the missing Ex parts explicit instead of accepting a distractor. |
| M0.04 (H; :848) | Hidden `G`, `3yy/p`, and `:8s/-/=/g<CR>`; `G` and the exact Ex path are not first worked out. | H; P0; R0. | Q1: “What does `:8s/-/=/g<CR>` do? Name address, command, pattern, replacement, flag, and Enter.” (decode, **Before**). Q2: “The flare is copied but only the new row’s dashes should change. Complete `:8s/-/=/___<CR>`.” (complete, **Before**). Q3: “Predict the art after the copy and substitution.” (predict, **After**). This directly repairs the operator’s M0.04 gap before exact keys are hidden. |
| M0.05 (X; :920) | Hidden first use of `:7,9t$<CR>` (Ex range copy); no visible guided `:t`, I, or C. | H; P0; R0. | Q: “Decode `:7,9t$<CR>`: which lines are copied, where is the destination, and when does it run?” (decode, **Before**). Q: “Complete `:7,9t___<CR>` to copy the range after the file.” (complete, **Before**). Q: “Why is this less cursor-dependent than `yy/p`?” (why, **After**). Ex copy must be worked out before the comparison. |
| M0.06 (T; :1005) | Transfer uses `j/f/r` and row-scoped `:s`; no new family, but hidden transfer has no paired question. | H; P0; R2 transfer review. | Q: “On this unfamiliar comet, type a key sequence that finds the marked core and changes every dash only on the acting row; grade the resulting buffer.” (open typed-key, **Before**). Q: “Which part of `:s/-/=/g<CR>` limits the change to this row?” (decode, **After**). A changed-art transfer is the first proper effect check. |
| M0.07 (C; :1101) | No new edit; current pool asks broad animation/Neovim choices. | P-MC; no H/R. | Q: “The strip has a bright frame held once and then settles. Predict which frame should be copied next and complete the Ex copy address.” (predict + complete, **Before**). The question is placed before the checkpoint decision so timing and range grammar are linked. |
| M0.08 (K; :1126) | Hidden `:1,3t$<CR>`, `G`, `f/r`, and `.`; dot and Ex copy are not sequence-complete. | H; P-MC; R0. | Q1: “Decode `:1,3t$<CR>` and say why the destination is `$`.” (decode, **Before**). Q2: “You changed one flare cell and want the same change on the next matching frame. Type a valid dot-repeat path; grade the artifact effect.” (open typed-key, **Before**). Q3: “Why is the duplicate a hold rather than a dead frame?” (why, **After**). Check questions must gate the artifact and require review before mastery. |

### M1 — Contour run (`S1/A1`; H2)

Source card lines: `share/curriculum-v2.json:1223-1669`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M1.01 (G; :1223) | New `/pattern<CR>` search plus `r`; visible recipe is first search use, no I/C. | G only; P0; no review. | Q: “Search for the marked comma, then replace only that joint. Type the keys; the cursor/result effect is graded.” (open typed-key, **Before**). Q: “What does `/comma<CR>` do, and why is `r` not an operator with a motion?” (decode/why, **After**). |
| M1.02 (G; :1290) | Reuses `3yy/p`; no new family, but no paired question. | G; P0; H later; R0. | Q: “This contour is one frame. Type the keys that copy all three rows, not just the row under the cursor.” (open typed-key, **Before**). Q: “What does the count belong to in `3yy`?” (decode, **After**). |
| M1.03 (C; :1352) | No edit; current MC reading does not complete landmark grammar. | P-MC; no H/R. | Q: “Complete `/comma<CR>` and then state which key reaches the next match without restarting the search.” (complete, **Before**). |
| M1.04 (H; :1377) | Hidden first use of absolute `G`, `3dd` (count plus linewise delete), and `o/O` insert-line entry. None was worked out or shown before this requirement. | H; P0; R0. | Q1: “Complete the whole-line deletion `___dd` so it removes exactly three rows. What does the count apply to?” (complete, **Before**; answer `3`). Q2: “You need a new row below without shifting existing glyphs. Type a valid `o`/`O` path; grade the row count and columns.” (open typed-key, **Before**). Q3: “Predict which anchor survives after the hand-authored descending frame.” (predict, **After**). |
| M1.05 (X; :1431) | Hidden `:%s/:/;/g<CR>` and `.`; substitution was visible in M0 but no parse; dot first appears hidden here/M0.08. | H; P0; R0. | Q1: “Decode `:%s/:/;/g<CR>` and identify why `%` is broader than a frame range.” (decode, **Before**). Q2: “Repeat the prior local change on the next matching joint. Type keys; any effect-equivalent dot path passes.” (open typed-key, **Before**). |
| M1.06 (T; :1493) | Hidden transfer of `G/0/f/r`; `G` itself was not guided. | H; P0; R2 transfer. | Q: “In the changed contour, type keys that go to the last line, land at column 0, find the joint, and replace only it.” (open typed-key, **Before**). Q: “Why does `G` differ from `gg`?” (why, **After**). |
| M1.07 (C; :1589) | No edit; diagnosis pool is not grammar completion. | P-MC; no H/R. | Q: “The contour end drifted after a line deletion. Which scope is wrong, and complete the bounded command that would preserve the anchor?” (diagnose + complete, **Before**). |
| M1.08 (K; :1614) | Hidden `:1,3t$<CR>` plus `G/0/f/r`; Ex copy still has no pre-use guided sequence. | H; P-MC; R0. | Q1: “Decode `:1,3t$<CR>` and complete the destination if the range must go to the end.” (decode/complete, **Before**). Q2: “Type a valid effect-equivalent path to find and replace the softened joint in the unfamiliar frame.” (open typed-key, **Before**). Q3: “Predict whether the endpoint stays fixed.” (predict, **After**). |

### M2 — Face focus (`S3/A1`; H1/H2)

Source card lines: `share/curriculum-v2.json:1685-2174`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M2.01 (G; :1685) | New `daw` (operator + text object) and search; visible first use, no grammar I/C. | G; P0; no review. | Q: “Remove only the face annotation, not the eye or silhouette. Type a valid operator-plus-object answer; the resulting buffer is graded.” (open typed-key, **Before**). Q: “Break `daw` into operator and text object; why is it safer than `dd`?” (decode/why, **After**). |
| M2.02 (G; :1769) | Reuses counted `4yy/p`; no new family, no pair. | G; P0; H later; R0. | Q: “Copy exactly these four face rows. Type the keys; any linewise path with the same result passes.” (open typed-key, **Before**). |
| M2.03 (C; :1834) | No edit; current MC principle item is after earlier face work. | P-MC; no H/R. | Q: “Complete `d___` with the text object that removes the annotation around the cursor while preserving the eye.” (complete, **Before**). |
| M2.04 (H; :1859) | Hidden `G/f/r`; absolute last-line motion is not guided. | H; P0; R0. | Q: “Type keys that reach the copied eye from the shown cursor and replace only that glyph; grade effect, not spelling.” (open typed-key, **Before**). Q: “Why does a visible landmark beat repeated `l` here?” (why, **After**). |
| M2.05 (X; :1917) | Hidden `:%s/[.o]/O/g<CR>`; `:s` was shown but pattern class/`%`/`g` never completed. | H; P0; R0. | Q1: “Decode `:%s/[.o]/O/g<CR>`: scope, pattern class, replacement, and flag.” (decode, **Before**). Q2: “Complete `:%s/[.o]/O/___<CR>` to change every matching eye.” (complete, **Before**). |
| M2.06 (T; :1994) | Hidden local `j/f/r` transfer; no new family, no paired question. | H; P0; R2 transfer. | Q: “On this unfamiliar face, type keys that change only its eye while preserving mouth and contour.” (open typed-key, **Before**). Q: “Predict which rows must be byte-identical afterward.” (predict, **After**). |
| M2.07 (C; :2096) | No edit; current diagnosis does not test operator grammar. | P-MC; no H/R. | Q: “A proposed `dd` consumes the mouth. Why is that scope wrong, and what operator/object completes a feature-only edit?” (why + complete, **Before**). |
| M2.08 (K; :2121) | Hidden `:1,4t$<CR>` plus `G/f/r`; Ex copy is still hidden-first. | H; P-MC; R0. | Q1: “Complete `:1,4t___<CR>` to copy the complete face after the current block.” (complete, **Before**). Q2: “Type a valid eye-close edit on the copied face; grade result.” (open typed-key, **Before**). Q3: “Why must the silhouette remain unchanged?” (why, **After**). |

### M3 — Pose copy (`A2`; H3)

Source card lines: `share/curriculum-v2.json:2208-2822`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M3.01 (G; :2208) | New `%` matching-delimiter motion and `f(`/`r`; no prior I/C. | G; P0; no review. | Q: “Starting on the pose edge, reach the eye inside its delimiters and replace it without touching the body. Type keys; scratch result is graded.” (open typed-key, **Before**). Q: “What does `%` move between, and why does `r` preserve row width?” (decode/why, **After**). |
| M3.02 (G; :2285) | Reuses `6yy/p`; no pair. | G; P0; H later; R0. | Q: “Type a counted linewise copy of this complete six-row pose, then put it below.” (open typed-key, **Before**). |
| M3.03 (C; :2356) | No edit; current MC selects whole-pose intent but no completion. | P-MC; no H/R. | Q: “Complete the whole-pose copy: `___yy` followed by `p`, so it copies six rows. What does the count count?” (complete, **Before**; answer `6`). |
| M3.04 (H; :2381) | Hidden first use of `ci(` (operator + text object); attached legacy prose is not current teaching. | H; P0; R0. | Q1: “Why is `ci(` the right scope for changing the eye inside parentheses? Name operator and object.” (why/decode, **Before**). Q2: “Type any valid `ci(` edit that leaves torso and feet identical.” (open typed-key, **Before**). |
| M3.05 (X; :2493) | Hidden first-use Ex `:1,6t$<CR>`; `yy/p` alternative is known only by recipe. | H; P0; R0. | Q1: “Decode `:1,6t$<CR>` and complete its destination.” (decode/complete, **Before**). Q2: “Why is an addressed range safer when the cursor is not on the pose?” (why, **After**). |
| M3.06 (T; :2574) | Hidden first use of Visual-line `V` and named register `"a`/`"ap`; no guided current card. | H; P0; R2 transfer. | Q: “Copy this unfamiliar six-row pose into register `a`, put it below, and edit only the copied eye. Type keys; grade buffer effect.” (open typed-key, **Before**). Q: “Decode the roles of `V`, `"a`, and `"ap`.” (decode, **After**). |
| M3.07 (C; :2758) | No edit; diagnosis pool does not complete register/selection grammar. | P-MC; no H/R. | Q: “The copied pose has only three rows. Which selection scope failed, and complete the command that selects all six?” (diagnose + complete, **Before**). |
| M3.08 (K; :2783) | Hidden digraph `<C-k>.M` and `G/f/r`; no guided digraph. | H; P-MC; R0. | Q1: “Complete the digraph entry for the middle dot: `<C-k>___`.” (complete, **Before**). Q2: “Type the effect-equivalent one-cell accent edit on the final pose.” (open typed-key, **Before**). Q3: “Why is this a glyph-palette decision, not a body redraw?” (why, **After**). |

### M4 — Rotation tween (`S4/A2`; H2/H4)

Source card lines: `share/curriculum-v2.json:2891-3471`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M4.01 (G; :2891) | New `C` (`c$`) and absolute `G`; visible recipe but no prior grammar I/C. | G; P0; no review. | Q: “Overwrite the rest of this row while keeping its left cells fixed. Type a valid `C`/`c$` path; grade the result.” (open typed-key, **Before**). Q: “Decode `C` as `c$`; why is it different from `x`?” (decode/why, **After**). |
| M4.02 (G; :2966) | Reuses `G` and `3yy/p`; no pair. | G; P0; H later; R0. | Q: “Copy the complete diagonal extreme, including its blank-free rows. Type keys; target state is graded.” (open typed-key, **Before**). |
| M4.03 (C; :3040) | No edit; current MC midpoint choices do not complete block/range grammar. | P-MC; no H/R. | Q: “Complete `C`’s hidden expansion: `C = c___`. Which motion preserves the pivot-side cells?” (complete, **Before**). |
| M4.04 (H; :3065) | Hidden first use of `:1,3t3<CR>` and Visual block `<C-v>jr|`; block `r` is not guided. | H; P0; R0. | Q1: “Decode `:1,3t3<CR>` and complete the destination for a third-row copy.” (decode/complete, **Before**). Q2: “Select the true aligned midpoint column and type a blockwise replace; grade columns, not exact keys.” (open typed-key, **Before**). |
| M4.05 (X; :3195) | Hidden `:1,3t$<CR>` plus `C`; Ex copy still lacks pre-use guided path. | H; P0; R0. | Q: “Why does `:1,3t$<CR>` copy a range without moving the cursor, and when is that safer than `yy/p`?” (why/decode, **Before**). |
| M4.06 (T; :3279) | Hidden Ex copy transfer plus `C`; no paired question. | H; P0; R2 transfer. | Q: “In the unfamiliar prop, copy its three-row extreme by any valid range/counted method, then overwrite only the midpoint cells.” (open typed-key, **Before**). Q: “Predict the fixed pivot cells.” (predict, **After**). |
| M4.07 (C; :3407) | No edit; current diagnosis does not test block selection completion. | P-MC; no H/R. | Q: “The midpoint column is one cell off. Which boundary motion would you change, and complete the block selection before `r`?” (diagnose + complete, **Before**). |
| M4.08 (K; :3432) | Hidden `3dd`; no guided linewise delete. Existing hint incorrectly suggests dot although expected keys use `dd`. | H; P-MC; R2 after pass. | Q1: “Decode `3dd` as count + operator + linewise motion; what rows disappear?” (decode, **Before**). Q2: “Type a valid effect-equivalent deletion that removes only the redundant frame.” (open typed-key, **Before**). Q3: “Predict whether the pivot survives.” (predict, **After**). |

### M5 — Layered scene (`S6/A4`; H3/H4)

Source card lines: `share/curriculum-v2.json:3621-4169`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M5.01 (G; :3621) | Reuses landmark navigation and standalone `r<Space>`; no new grammar, but no paired question. | G; P0; no review. | Q: “The background bar touches the pivot. Type keys that erase only that cell without shifting the foreground.” (open typed-key, **Before**). Q: “Why is `r<Space>` safer than `x` for a fixed-width seam?” (why, **After**). |
| M5.02 (G; :3693) | Uses Visual-line `V6jy` and `Gp`; first current visible recipe after hidden M3.06, still no paired grammar. | G; P0; H later; R0. | Q1: “Select exactly this seven-row layer frame and put a complete copy below; grade the block effect.” (open typed-key, **Before**). Q2: “What does `V6j` select, and why is it not a rectangle?” (decode, **After**). |
| M5.03 (C; :3767) | No edit; current pool tests seam reading but not `r`/Visual-line completion. | P-MC; no H/R. | Q: “A seam glyph joins foreground and background. Complete the smallest standalone replace that clears only the seam cell.” (complete, **Before**). |
| M5.04 (H; :3792) | Hidden `C`/`c$` plus `f/r`; C was visible M4 but no grammar pair. | H; P0; R0. | Q: “Type a valid row overwrite that swings only the copied foreground while preserving its pivot break; grade effect.” (open typed-key, **Before**). Q: “Decode why `C` changes to end-of-line and does not mean ‘copy’.” (decode/why, **After**). |
| M5.05 (X; :3862) | Hidden first-use addressed `:1,7t7<CR>`; no prior Ex grammar stage. | H; P0; R0. | Q1: “Decode `:1,7t7<CR>`: range, command, destination, Enter.” (decode, **Before**). Q2: “Complete `:1,7t___<CR>` to put the copy at line 7.” (complete, **Before**). |
| M5.06 (T; :3968) | Hidden transfer `r<Space>`/landmarks; no new family, but no paired question. | H; P0; R2 transfer. | Q: “Repair the unfamiliar overlap by typing any valid keys that preserve layer order and clear only the nominated foreground edge.” (open typed-key, **Before**). Q: “Which row is invariant, and why?” (why, **After**). |
| M5.07 (C; :4088) | No edit; diagnosis pool has no grammar completion. | P-MC; no H/R. | Q: “Predict which seam remains after removing the touching background bar, then complete the single-cell replace.” (predict + complete, **Before**). |
| M5.08 (K; :4113) | Hidden landmark `f` + `rO`; current five-question pool runs first but is not a paired grammar gate. | H; P-MC; R0. | Q1: “Type a valid effect-equivalent landmark replace on the key-hidden layered frame.” (open typed-key, **Before**). Q2: “Why must the negative-space break stay registered through the swing?” (why, **After**). |

### M6 — Pyramid build (`A5`; H3/H9)

Source card lines: `share/curriculum-v2.json:4211-4838`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M6.01 (G; :4211) | Reuses standalone `r^`; no paired question. | G; P0; no review. | Q: “Replace only the nominated unit in the finished key pose and keep the row count. Type keys; effect is graded.” (open typed-key, **Before**). Q: “Why is replacement preferable to deleting a cell?” (why, **After**). |
| M6.02 (G; :4266) | First visible guided `:1,5t$<CR>`, but hidden first use was M0.05; no Ex parse. | G; P0; H later; R0. | Q1: “Decode `:1,5t$<CR>` and complete the destination.” (decode/complete, **Before**). Q2: “Type the complete-pose copy; grade result.” (open typed-key, **Before**). |
| M6.03 (C; :4330) | No edit; current MC asks subtractive principle but no `D`/`:t` completion. | P-MC; no H/R. | Q: “Complete `:[range]t___<CR>` for a range copied after the current frame, then say why copy-before-erase helps.” (complete + why, **Before**). |
| M6.04 (H; :4355) | Hidden first use of `D` (`d$`); `J`/undo in attached legacy text are not proof. | H; P0; R2 after pass. | Q1: “Decode `D` as `d$`: what is deleted and what row remains?” (decode, **Before**). Q2: “Clear only the copied apex with a row-preserving delete-to-end operation; grade that the row remains and every lower layer is unchanged.” (open typed-key, **Before**). Q3: “Why is row-preserving clear safer than `dd` here?” (why, **After**). Recovery must be taught on a separate causal mistake, not padded with a join immediately undone. |
| M6.05 (X; :4537) | Hidden `:6,10t$<CR>` plus `D`; D’s first hidden use was M6.04 and no paired parse. | H; P0; R0. | Q: “Complete and decode `:6,10t___<CR>`; then name the operator in `D=d$`.” (complete/decode, **Before**). |
| M6.06 (T; :4632) | Hidden first use of Ex `:1,5m$<CR>` range move; no guided `:m`. | H; P0; R2 transfer. | Q1: “Decode `:1,5m$<CR>` and explain how move differs from copy.” (decode/why, **Before**). Q2: “Type any valid effect-equivalent range move on the unfamiliar build.” (open typed-key, **Before**). |
| M6.07 (C; :4758) | No edit; current pool asks playback order but not `:m` completion. | P-MC; no H/R. | Q: “Complete `:1,5m___<CR>` so authoring-order frames move to the playback destination.” (complete, **Before**). |
| M6.08 (K; :4783) | Hidden two `:m` moves; current check owns MC only, no completion or review requirement. | H; P-MC; R0. | Q1: “Type a valid range-move sequence that makes the strip build upward; grade visible playback order.” (open typed-key, **Before**). Q2: “Predict whether all frames retain equal height.” (predict, **After**). |

### M7 — Timed build (`A4/A5`; H5/H9)

Source card lines: `share/curriculum-v2.json:4889-5729`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M7.01 (G; :4889) | Visible `:1,5t5<CR>`; Ex range not parsed before use. | G; P0; no review. | Q: “Decode `:1,5t5<CR>` and type a valid copy that creates an anticipation hold.” (decode + open typed-key, **Before**). |
| M7.02 (G; :5010) | Visible `:16,20t$<CR>`; no pair or changed-art review. | G; P0; no review. | Q: “Is this duplicate a hold or dead frame? Explain using the timing plan, then type the range copy.” (why + open typed-key, **Before**). |
| M7.03 (C; :5121) | No edit; current pool identifies holds but does not complete `:t`/dot/macro grammar. | P-MC; no H/R. | Q: “Complete the addressed copy that makes one declared hold, and predict which cell may then be repeated.” (complete + predict, **Before**). |
| M7.04 (H; :5146) | Hidden dot `.`; first current hidden requirement, with `f/r`; no guided dot card. | H; P0; R0. | Q1: “What change is stored for `.` after `r=`? Type the keys that repeat it on the matching held row; grade effect.” (decode + open typed-key, **Before**). Q2: “Why does `j.` preserve the chosen edit while redoing it?” (why, **After**). |
| M7.05 (X; :5283) | Hidden alternatives first use macro `q…q/@q` and `:g/pattern/normal!`; `:s` has no completion. | H; P0; R0. | Q1: “Complete the macro skeleton `q___…q` and the replay `@___`; what does the register name mean?” (complete, **Before**). Q2: “Decode `:g/pattern/normal! {keys}<CR>` into selector and payload.” (decode, **Before**). |
| M7.06 (T; :5484) | Hidden dot transfer; no new family after M7.04 but no pair. | H; P0; R2 transfer. | Q: “On the changed build, make one meaningful hold edit and repeat it by effect, not exact spelling.” (open typed-key, **Before**). Q: “Predict whether an unrelated row changes.” (predict, **After**). |
| M7.07 (C; :5649) | No edit; current pool asks range safety but no completion. | P-MC; no H/R. | Q: “Complete a safe selected-frame substitute and state why `%` would be too broad.” (complete + why, **Before**). |
| M7.08 (K; :5674) | Hidden `5dd`; `dd` first appears hidden in M1.04; attached legacy delete lesson is not prior teaching. | H; P-MC; R0. | Q1: “Decode `5dd` as count/operator/linewise motion; which frame disappears?” (decode, **Before**). Q2: “Type an effect-equivalent deletion that removes only the unjustified duplicate.” (open typed-key, **Before**). Q3: “Why must the anticipation hold remain?” (why, **After**). |

### M8 — Walk study (`A7/A4`; H2/H3)

Source card lines: `share/curriculum-v2.json:5815-6335`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M8.01 (G; :5815) | Reuses `r_`; no paired question. | G; P0; no review. | Q: “Plant the leading foot by replacing one cell; type keys and preserve torso/arm rows.” (open typed-key, **Before**). Q: “Why is the foot cell a landmark?” (why, **After**). |
| M8.02 (G; :5870) | Visible `5yy/p` plus `C`; no pair. | G; P0; no review. | Q: “Copy all five pose rows and change only the copied limbs. Type any effect-equivalent path.” (open typed-key, **Before**). |
| M8.03 (C; :5927) | No edit; current pool asks motion reading but not copy/open-line grammar. | P-MC; no H/R. | Q: “Predict which foot leads, then complete the five-row copy before editing it.” (predict + complete, **Before**). |
| M8.04 (H; :5952) | Hidden first use of `o` and literal Insert authoring; legacy open-line prose is same-card only. | H; P0; R0. | Q1: “You need five new rows below without changing existing columns. Type a valid `o`/`O` sequence and grade row count/registration.” (open typed-key, **Before**). Q2: “Why must `<Esc>` end the insertion before the next row?” (why, **After**). |
| M8.05 (X; :6066) | Hidden `:1,5s@o/@o\@<CR>` range substitution; Ex range parse absent. | H; P0; R0. | Q: “Decode `:1,5s@o/@o\@<CR>` and complete its range if only the five-row frame may change.” (decode + complete, **Before**). |
| M8.06 (T; :6147) | Hidden transfer `r_`; no new family, no pair. | H; P0; R2 transfer. | Q: “Type keys that plant one foot in the unfamiliar walker while torso and arm remain unchanged.” (open typed-key, **Before**). |
| M8.07 (C; :6255) | No edit; current diagnosis does not test open-line completion. | P-MC; no H/R. | Q: “A foot slides one cell. Diagnose whether row count or column registration failed, then complete the smallest repair.” (diagnose + complete, **Before**). |
| M8.08 (K; :6280) | Hidden `:6,10t$<CR>` plus C; no paired grammar/review. | H; P-MC; R0. | Q1: “Decode `:6,10t$<CR>` and type a valid return-pose copy.” (decode + open typed-key, **Before**). Q2: “Predict which torso cells must stay identical.” (predict, **After**). |

### M9 — Original bounce (`A7`; H1/H3/H9)

Source card lines: `share/curriculum-v2.json:6376-6855`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M9.01 (G; :6376) | Visible `f/r`; no new family but no pair. | G; P0; no review. | Q: “Find the planned high marker and replace it without moving rails or ground. Type keys; effect is graded.” (open typed-key, **Before**). |
| M9.02 (G; :6427) | Visible `3yy/p` + C; no pair. | G; P0; no review. | Q: “Copy the complete high pose, then create a readable squash inside the same bounds. Type a valid path.” (open typed-key, **Before**). Q: “Why do extremes precede the middle?” (why, **After**). |
| M9.03 (C; :6486) | No edit; current plan MC does not require a command completion. | P-MC; no H/R. | Q: “Complete the plan’s frame-copy command and state which range is safe before the squash edit.” (complete, **Before**). |
| M9.04 (H; :6511) | Hidden first uses `x` (cell deletion) and `i` (insert entry); neither has prior current guided grammar. | H; P0; R0. | Q1: “Why is `x` unsafe when following glyphs must keep their columns? Type a fixed-cell repair using `r` or `x`+insert; grade effect.” (why + open typed-key, **Before**). Q2: “Complete the standalone insert sequence `i___<Esc>` that restores the intended cell.” (complete, **Before**). |
| M9.05 (X; :6588) | Hidden `:1,3t3<CR>`/C and an `o` authoring alternative; several families are not paired. | H; P0; R0. | Q: “Compare direct three-row authoring with copy-then-vary: which preserves registered rails, and complete the safer copy range.” (why + complete, **Before**). |
| M9.06 (T; :6680) | Hidden transfer `f/r`; no paired question. | H; P0; R2 transfer. | Q: “On changed bounds, type a valid high-pose edit without moving ground.” (open typed-key, **Before**). Q: “Predict the fixed baseline cells.” (predict, **After**). |
| M9.07 (C; :6776) | No edit; diagnosis pool does not complete `x/i/:t`. | P-MC; no H/R. | Q: “The squash is unreadable and the ground moved. Diagnose the first scope error and complete the range-copy repair.” (diagnose + complete, **Before**). |
| M9.08 (K; :6801) | Hidden `:1,3t$<CR>` + f/r; no changed-art review for capstone. | H; P-MC; R0. | Q1: “Type a valid range-copy and rebound edit that returns to frame one; grade the loop result.” (open typed-key, **Before**). Q2: “Why is the rebound an overshoot rather than a duplicate?” (why, **After**). |

### M10 — SJIS puff tween (`P/S1`; H2/H3)

Source card lines: `share/curriculum-v2.json:6883-7319`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M10.01 (G; :6883) | Visible standalone `r<char>` on a proportional glyph; no prior I/C and no paired question. | G; P0; R0. | Q: “On the displayed lobe, reach the marked cell and replace it without changing the lower contour. Type keys; exact effect passes.” (open typed-key, **Before**). Q: “Why does fixed-width key grading not prove Saitamaar visual width?” (why, **After**). |
| M10.02 (G; :6930) | Visible `3yy/p` plus `C` for three SJIS rows; no grammar parse/pair. | G; P0; R0. | Q: “Copy all three lobe rows, then overwrite the copied rows into the wider extreme. Type any valid effect-equivalent path.” (open typed-key, **Before**). Q: “Which cells are registered even when the proportional advance changes?” (predict, **After**). |
| M10.03 (C; :6981) | No edit; current MC reads proportional expansion but does not complete copy/overwrite grammar. | P-MC; R0. | Q: “Decode the displayed three-row expansion and complete the command family that copies the whole lobe before a row overwrite.” (decode + complete, **Before**). |
| M10.04 (H; :7006) | Hidden first current use of `o`/Insert authoring for three rows; M1/M8 already used `o` hidden, never guided. | H; P0; R0. | Q1: “Type keys that append exactly three impact rows and escape Insert mode after each row; grade row count and outline.” (open typed-key, **Before**). Q2: “Why must `ﾆ二ニ` remain inside its outline?” (why, **After**). |
| M10.05 (X; :7064) | Hidden Ex `:7,9t$<CR>`; no prior paired Ex decode and no review. | H; P0; R0. | Q1: “Decode `:7,9t$<CR>` and complete the destination.” (decode/complete, **Before**). Q2: “Which of counted `yy/p` and `:t` is cursor-independent, and why?” (why, **After**). |
| M10.06 (T; :7149) | Hidden transfer of standalone `r` to unseen proportional shoulder; no paired question. | H; P0; R2 transfer review. | Q: “On the unseen shoulder, type keys that complete the missing glyph while preserving the two lower rows; grade effect, not exact path.” (open typed-key, **Before**). |
| M10.07 (C; :7245) | No edit; diagnosis pool does not test proportional-boundary completion. | P-MC; R0. | Q: “The hatching escapes the outline. Diagnose whether the error is glyph choice or row scope, then complete the smallest repair.” (diagnose + complete, **Before**). |
| M10.08 (K; :7270) | Hidden `:1,3t$<CR>` plus lobe return; Ex copy not grammar-first and no review. | H; P-MC; R0. | Q1: “Type a valid effect-equivalent copy that returns the lobe as the settle frame.” (open typed-key, **Before**). Q2: “Predict which contour rows must match frame one and which metric judgment remains external.” (predict, **After**). |

### M11 — Fixed-width redraw (`S0/A4`; H1/H5/H9)

Source card lines: `share/curriculum-v2.json:7363-8023`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M11.01 (G; :7363) | New standalone Replace mode `R`; visible first use with no interpretation/completion. | G; P0; R0. | Q: “Overwrite the two roof cells without inserting or shifting either wall. Type a valid `R…<Esc>` path; grade columns.” (open typed-key, **Before**). Q: “How does `R` differ from `r<char>` and Insert mode?” (decode, **After**). |
| M11.02 (G; :7416) | Visible `3yy/p`; no paired question; two review variants exist but are not a grammar review. | G; P0; R2 after pass. | Q: “Copy the complete three-row machine before developing the tension pose; type keys and preserve both walls.” (open typed-key, **Before**). |
| M11.03 (C; :7524) | No edit; current MC explains fixed width but does not parse `R`. | P-MC; R0. | Q: “Complete the standalone redraw sequence `R___<Esc>` and say why insertion would shift the walls.” (complete + why, **Before**). |
| M11.04 (H; :7549) | Hidden combined `R`, `u`, `<C-r>`; undo/redo first current hidden requirement and no paired grammar stage. | H; P0; R2 after pass. | Q1: “Type a redraw, undo it, and redo it; grade that the artifact visits all three states.” (open typed-key, **Before**). Q2: “Decode `u` and `<C-r>` as standalone recovery commands.” (decode, **Before**). Q3: “Why does a no-op undo fail the lesson?” (why, **After**). |
| M11.05 (X; :7697) | Hidden `5G:s/o/O/g<CR>`; Ex substitution prior shown but no completion. | H; P0; R2. | Q1: “Decode `5G:s/o/O/g<CR>` and identify its current-row scope.” (decode, **Before**). Q2: “Complete `:s/o/O/___<CR>` to brighten every indicator on the row.” (complete, **Before**). |
| M11.06 (T; :7827) | Hidden transfer of Replace mode `R`; no paired question. | H; P0; R2 transfer review. | Q: “On the unfamiliar shell, type a bounded Replace-mode redraw that keeps both endpoints in their original columns.” (open typed-key, **Before**). |
| M11.07 (C; :7923) | No edit; diagnosis pool does not complete recovery or virtual-column grammar. | P-MC; R0. | Q: “The roof moved after an insert and undo did nothing. Diagnose the mode/scope error and complete a row-preserving recovery.” (diagnose + complete, **Before**). |
| M11.08 (K; :7948) | Hidden `:set virtualedit=all<CR>`, exact-column `i`, and dot; `:set`, `i`, and `.` are not paired before this check. | H; P-MC; R2 after pass. | Q1: “Decode `:set virtualedit=all<CR>` and state what empty-space motion it permits.” (decode, **Before**). Q2: “Type any valid effect-equivalent edit that repeats one blur cell across both frames.” (open typed-key, **Before**). Q3: “Why must virtual editing be limited to the art buffer?” (why, **After**). |

### M12 — Joint sweep (`S2/S4`; H2/H5)

Source card lines: `share/curriculum-v2.json:8081-8737`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M12.01 (G; :8081) | New standalone `t{char}` plus `r`; visible first `t`, no I/C/pair. | G; P0; R0. | Q: “Approach the cell just before the next colon and replace only the joint. Type a valid till-and-replace path; effect is graded.” (open typed-key, **Before**). Q: “What is the difference between `t:` and `f:`?” (decode, **After**). |
| M12.02 (G; :8139) | Visible `T:` backward till plus `yy/p`; no paired grammar. | G; P0; R0. | Q: “Copy the full pose, then approach the right joint from the opposite direction and change it. Type keys.” (open typed-key, **Before**). Q: “Why does `T:` stop on the other side of the landmark?” (why, **After**). |
| M12.03 (C; :8196) | No edit; current MC does not complete till syntax. | P-MC; R0. | Q: “Complete the backward till command `T___` for a colon, then predict the cursor cell before `r!`.” (complete + predict, **Before**). |
| M12.04 (H; :8221) | Hidden first use of `;` and `,` repeat directions; `t/T` only visible, no repeat grammar. | H; P0; R2. | Q1: “After `f:`, type the key that finds the next same landmark, then the key that reverses it; grade cursor/result.” (open typed-key, **Before**). Q2: “Decode `;` versus `,` and explain why column counting is not required.” (decode/why, **After**). |
| M12.05 (X; :8364) | Hidden `:1,3t$<CR>` and `O`; uppercase open-line has no guided current card. | H; P0; R2. | Q1: “Complete `:1,3t___<CR>` and type a valid `O`/replace repair for the paired base cells.” (complete + open typed-key, **Before**). Q2: “Why is `O` different from `o` in a fixed-height frame?” (why, **After**). |
| M12.06 (T; :8527) | Hidden transfer `t/T`; no paired question. | H; P0; R2 transfer review. | Q: “In the unfamiliar shell, type forward and backward till motions to reach paired joints without memorised columns.” (open typed-key, **Before**). |
| M12.07 (C; :8637) | No edit; current diagnosis does not complete repeat grammar. | P-MC; R0. | Q: “The cursor lands one cell away after a reversed search. Diagnose whether `t/T` or `;/,` is wrong and complete the repair.” (diagnose + complete, **Before**). |
| M12.08 (K; :8662) | Hidden `:t`, `t/T`, and `r`; current pool is not per-family paired. | H; P-MC; R0. | Q1: “Type a valid range-copy and till-motion path that exchanges the left accent for its hand-mirrored right accent.” (open typed-key, **Before**). Q2: “Predict which centre-axis cells remain unchanged.” (predict, **After**). |

### M13 — Texture pulse (`S3`; H2/H5)

Source card lines: `share/curriculum-v2.json:8758-9405`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M13.01 (G; :8758) | New standalone `W`; visible first use, no I/C/pair. | G; P0; R0. | Q: “Reach the next whitespace-separated texture cluster and replace its first acting cell. Type keys; grade cursor and result.” (open typed-key, **Before**). Q: “How does `W` differ from lowercase `w` on punctuation texture?” (decode, **After**). |
| M13.02 (G; :8815) | Visible `3yy/p`, `W`, `r`; no paired question. | G; P0; R0. | Q: “Copy the complete pose, clear the centre accent, and advance it one WORD to the right. Type a valid effect-equivalent path.” (open typed-key, **Before**). |
| M13.03 (C; :8872) | No edit; current MC does not complete WORD motion. | P-MC; R0. | Q: “Complete the WORD landmark sequence that reaches the next spaced punctuation cluster, and predict its stopping cell.” (complete + predict, **Before**). |
| M13.04 (H; :8897) | Hidden first uses `E` and `B`; only `W` was visible. | H; P0; R2. | Q1: “Type a valid sequence using `E`, counted `W`, and `B` that expands the pulse across three texture edges; grade effect.” (open typed-key, **Before**). Q2: “Decode the boundary differences among `W`, `E`, and `B`.” (decode, **After**). |
| M13.05 (X; :9047) | Hidden `:7,9t$<CR>` and `:s/!/*/g`; no Ex completion. | H; P0; R2. | Q1: “Decode `:s/!/*/g<CR>` and state its current-row scope.” (decode, **Before**). Q2: “Complete `:7,9t___<CR>` for the copied pulse range.” (complete, **Before**). |
| M13.06 (T; :9210) | Hidden transfer `W/B/E`; no paired question. | H; P0; R2 transfer review. | Q: “On unfamiliar spaced texture, type keys that reach the nominated cluster without relying on column counts.” (open typed-key, **Before**). |
| M13.07 (C; :9324) | No edit; current diagnosis does not test lowercase/WORD completion. | P-MC; R0. | Q: “A lowercase motion stops inside punctuation. Diagnose the motion-family error and complete the WORD-based repair.” (diagnose + complete, **Before**). |
| M13.08 (K; :9349) | Hidden `:1,3t$<CR>` plus `W/B/E`; no paired grammar/review. | H; P-MC; R0. | Q1: “Type a valid copy and WORD-motion path that moves the accent left to finish the loop.” (open typed-key, **Before**). Q2: “Predict which support rows cannot change.” (predict, **After**). |

### M14 — Variant palette (`S5`; H3/H4/H6/H9)

Source card lines: `share/curriculum-v2.json:9444-10201`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M14.01 (G; :9444) | New named register `"a`, `yl`, Replace-mode `<C-r>a`; visible first use, no register grammar I/C. | G; P0; R2 after pass. | Q1: “Yank the visible palette glyph into register `a` and retrieve it in Replace mode; type keys, grade eye/wall result.” (open typed-key, **Before**). Q2: “Decode `"ayl` and `<C-r>a`; why does register retrieval avoid retyping?” (decode/why, **After**). |
| M14.02 (G; :9568) | New `yap` paragraph-object and `p`; visible first use, no operator/object grammar pair. | G; P0; R0. | Q: “Treat the blank-line-separated face as one paragraph object, copy it, and put it below. Type any effect-equivalent keys.” (open typed-key, **Before**). Q: “Break `yap` into operator and object.” (decode, **After**). |
| M14.03 (C; :9639) | No edit; current MC reads variants but not register/paragraph completion. | P-MC; R0. | Q: “Complete `y___` with the object that copies the full blank-line-separated frame, then name the register that stores a glyph.” (complete, **Before**). |
| M14.04 (H; :9664) | Hidden named-register palette retrieval; visible M14.01 precedes but no completion/pair. | H; P0; R2. | Q1: “Type a valid named-register sequence that changes only the copied eye to the stored palette glyph.” (open typed-key, **Before**). Q2: “Why is `<C-r>a` in Replace mode not an insertion shift?” (why, **After**). |
| M14.05 (X; :9826) | Hidden first `}` paragraph/frame boundary and `P`, plus Ex `:t` range; no grammar pair. | H; P0; R2. | Q1: “Decode `yap`, `P`, and `:1,4t$<CR>` as three scopes for the same complete variant.” (decode, **Before**). Q2: “Type an effect-equivalent duplicate and predict cursor/frame location.” (open typed-key + predict, **Before**). |
| M14.06 (T; :10012) | Hidden named-register transfer; no paired question. | H; P0; R2 transfer review. | Q: “On the unfamiliar shell, store its palette glyph in a named register and retrieve it in Replace mode; grade effect.” (open typed-key, **Before**). |
| M14.07 (C; :10132) | No edit; diagnosis pool does not complete register/object grammar. | P-MC; R0. | Q: “A one-row copy shifted the wall. Diagnose paragraph versus line scope and complete the object that preserves the frame.” (diagnose + complete, **Before**). |
| M14.08 (K; :10157) | Hidden `}` plus register `b`; current pool precedes artifact but lacks completion and per-family pair. | H; P-MC; R2. | Q1: “Type a valid path that stores the first eye material, crosses two frame boundaries, and retrieves it in the third; grade result.” (open typed-key, **Before**). Q2: “Why does `}` move between blank-line-separated objects?” (decode/why, **After**). |

### M15 — Texture ground (`S7`; H4/H5/H8/H9)

Source card lines: `share/curriculum-v2.json:10344-11086`. This partition is
also covered by the existing detailed report
`share/audits/grammar-sequence-M15-M18.md:102-120`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M15.01 (G; :10344) | New Ex `:set shiftwidth=1<CR>` and Normal `>>`; visible recipe, no grammar I/C. | G; P0; R2 after pass. | Q1: “Decode `:set shiftwidth=1<CR>`: command, option, value, Enter.” (decode, **Before**). Q2: “Type a valid one-cell offset of the acting row; grade effect, not exact `>>` spelling.” (open typed-key, **Before**). Q3: “Why must `shiftwidth=1` be set before `>>`?” (why, **After**). |
| M15.02 (G; :10462) | Reuses `3yy/p` and `gg/G`; no pair or review. | G; P0; R0. | Q: “Copy the complete three-row material stack as one frame. Type keys; grade that no dither/shadow row is omitted.” (open typed-key, **Before**). |
| M15.03 (C; :10530) | No edit; current MC does not complete `:set`/`>>`. | P-MC; R0. | Q: “Complete `:set shiftwidth=___<CR>` and say what the second `>` contributes in `>>`.” (complete + decode, **Before**). |
| M15.04 (H; :10555) | Hidden combined `:set`, `>>`, and `:4s/:/./g<CR>`; no paired grammar. | H; P0; R2. | Q1: “Decode `:4s/:/./g<CR>` into range, command, pattern, replacement, flag, Enter.” (decode, **Before**). Q2: “Type a valid one-cell offset and row-bounded lightening on the copied stack.” (open typed-key, **Before**). |
| M15.05 (X; :10688) | Hidden first current Visual block `<C-v>2j$A` and addressed `:4,6s/$/|/`; block append has no guided current stage. | H; P0; R2. | Q1: “Select the row-end rectangle and append one edge; grade block shape, not exact keys.” (open typed-key, **Before**). Q2: “Complete `:4,6s/$/|/___<CR>` and compare its explicit range to the block selection.” (complete/compare, **Before**). |
| M15.06 (T; :10833) | Hidden transfer `:set`/`>>`; current hint mentions dot although expected keys do not use it. | H; P0; R2 transfer review. | Q: “On unfamiliar brick/dither/shadow rows, type an effect-equivalent one-cell offset without leaking into the shadow.” (open typed-key, **Before**). |
| M15.07 (C; :10935) | No edit; current diagnosis does not complete macro/range grammar. | P-MC; R0. | Q: “A two-cell lurch occurred. Diagnose whether `shiftwidth`, operator count, or range leaked, then complete the one-cell command.” (diagnose + complete, **Before**). |
| M15.08 (K; :10960) | Hidden `:1,3t$<CR>`, macro `q…q/@q`, `f:`, `r.`; macro already appeared as a hidden alternative at M7.05 but has never had a guided card or per-family pair. | H; P-MC; R2. | Q1: “Complete `q___…q` and `@___` for a three-replay landmark edit.” (complete, **Before**). Q2: “Decode `:1,3t$<CR>` and type a valid effect-equivalent frame append.” (decode + open typed-key, **Before**). Q3: “Why must the replay remain inside the dither row?” (why, **After**). |

### M16 — Key-pose plan (`A0`; H3/H9)

Source card lines: `share/curriculum-v2.json:11120-12070`. Existing detail:
`share/audits/grammar-sequence-M15-M18.md:113-120`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M16.01 (G; :11120) | New standalone `<C-a>` numeric increment; visible first use, no I/C/pair. | G; P0; R2. | Q1: “Type the key that increments only the frame number under the cursor; grade the number and unchanged art.” (open typed-key, **Before**). Q2: “Decode `<C-a>` as a standalone command, not count + operator.” (decode, **After**). |
| M16.02 (G; :11247) | New Ex `:read %<CR>`; visible first use with no source/read grammar. | G; P0; R2. | Q1: “Decode `:read %<CR>`: what is the source and where is it inserted?” (decode, **Before**). Q2: “Type the import and increment only its frame label; grade source freshness.” (open typed-key, **Before**). |
| M16.03 (C; :11385) | No edit; current MC plan check does not complete `:read`. | P-MC; R0. | Q: “Complete `:read ___<CR>` for the saved current plate, then predict which line receives it.” (complete + predict, **Before**). |
| M16.04 (H; :11410) | Hidden `:1,5t$<CR>` plus counted `<C-a>`; Ex copy lacks completion. | H; P0; R2. | Q1: “Decode and complete `:1,5t___<CR>`; then type a count-increment for the copied frame label.” (decode + open typed-key, **Before**). Q2: “Why must the FPS line remain unchanged?” (why, **After**). |
| M16.05 (X; :11584) | Hidden `:6,10m0<CR>` and Visual-line delete/put alternative; the `:m` family already appeared hidden at M6.06/M6.08 but has no guided move. | H; P0; R2. | Q1: “Decode `:6,10m0<CR>` and compare it with selecting, deleting, and putting a whole block.” (decode/compare, **Before**). Q2: “Type either valid method; grade final block order and scope.” (open typed-key, **Before**). |
| M16.06 (T; :11770) | Hidden transfer `<C-a>`; no paired question. | H; P0; R2 transfer review. | Q: “On the unfamiliar plan, type a valid numeric increment that changes only the frame label.” (open typed-key, **Before**). |
| M16.07 (C; :11885) | No edit; diagnosis pool does not complete copy/move/read grammar. | P-MC; R0. | Q: “A copied plan has a duplicate identifier and split block. Diagnose the address error and complete the move/copy repair.” (diagnose + complete, **Before**). |
| M16.08 (K; :11910) | Hidden `:1,5t$<CR>` + `<C-a>`; MC pool precedes artifact but no grammar pair. | H; P-MC; R2. | Q1: “Type any valid whole-block copy and count-increment path that adds the fourth plan while preserving art and FPS.” (open typed-key, **Before**). Q2: “Predict which frame identities are now unique.” (predict, **After**). |

### M17 — Coherent anchors (`A3`; H2/H5)

Source card lines: `share/curriculum-v2.json:12128-12865`. Existing detail:
`share/audits/grammar-sequence-M15-M18.md:124-130`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M17.01 (G; :12128) | Visible `/x<CR>`, `n`, dot, and `r`; `/` has earlier use, but `n`/dot lack grammar I/C. | G; P0; R2. | Q1: “Search for the homologous eye, type `n` to reach the next one, and repeat a one-cell change; grade the three anchors.” (open typed-key, **Before**). Q2: “Decode `/pattern<CR>`, `n`, and `.` as three standalone steps.” (decode, **After**). |
| M17.02 (G; :12284) | Visible `3yy/p` + `G`; no pair/review. | G; P0; R0. | Q: “Copy the complete third pose as a scaffold while leaving its correct eye attached. Type keys; grade whole-frame result.” (open typed-key, **Before**). |
| M17.03 (C; :12366) | No edit; current MC reads temporal anchors but no search/dot completion. | P-MC; R0. | Q: “Complete the search-and-repeat sequence that changes an unchanged eye across frames without touching contours.” (complete, **Before**). |
| M17.04 (H; :12391) | Hidden landmark `f^r-`, `f_r-`, `r`; no paired grammar and no review. | H; P0; R0. | Q: “Type keys that find each nominated contour landmark and replace only it; grade unchanged eye row.” (open typed-key, **Before**). Q: “Why are two `f` landmarks safer than moving by columns?” (why, **After**). |
| M17.05 (X; :12470) | Hidden `:g/o/normal!…<CR>` alongside search/dot; the global-normal family already appeared as a hidden alternative at M7.05 but has no guided card. | H; P0; R2. | Q1: “Decode `:g/o/normal! {keys}<CR>` into selector and Normal payload.” (decode, **Before**). Q2: “Complete `:g/o/normal! ___<CR>` so only matching eye lines are changed.” (complete, **Before**). |
| M17.06 (T; :12642) | Hidden search/`n`/dot transfer; no paired question. | H; P0; R2 transfer review. | Q: “On three unfamiliar shells, type a search/next/repeat path that changes only homologous eyes; grade effects.” (open typed-key, **Before**). |
| M17.07 (C; :12780) | No edit; diagnosis pool does not complete global selector/payload. | P-MC; R0. | Q: “A global selector also matches contours. Diagnose the pattern scope and complete a safer selector/payload.” (diagnose + complete, **Before**). |
| M17.08 (K; :12805) | Hidden macro `q/@` plus search/dot; macro only appeared hidden at M15.08. | H; P-MC; R2. | Q1: “Complete the macro record/replay `q___…q`, `@___`, and count; type any effect-equivalent anchor pass.” (complete + open typed-key, **Before**). Q2: “Why does the stable eye remain unchanged in the macro’s selector set?” (why, **After**). |

### M18 — Hand-mirrored return (`S2/A6`; H1/H9)

Source card lines: `share/curriculum-v2.json:12993-13711`. Existing detail:
`share/audits/grammar-sequence-M15-M18.md:135-140`.

| Card | Current command/new-use audit | Current stages and review | Proposed paired question(s), form, placement, reason |
|---|---|---|---|
| M18.01 (G; :12993) | Visible `C`/row overwrites for hand mirror; no `C=c$` grammar or paired question. Literal slashes cause the current hint to suggest search/dot incorrectly. | G; P0; R2. | Q1: “Hand-author the three mirrored rows. Type row-overwrite keys; grade actor, arrowhead, limbs, spacing, and unchanged row height.” (open typed-key, **Before**). Q2: “Decode `C` as `c$`, and explain why a byte reversal is not a hand mirror.” (decode/why, **After**). |
| M18.02 (G; :13135) | Visible `4yy/p`; no pair/review. | G; P0; R0. | Q: “Copy the complete mirrored extreme and its validation line as one scaffold. Type keys; grade all four rows.” (open typed-key, **Before**). |
| M18.03 (C; :13207) | No edit; current MC distinguishes manual mirror but no overwrite completion. | P-MC; R0. | Q: “Complete `C` as `c___` for a row overwrite, then predict which mirrored cells must be authored manually.” (complete + predict, **Before**). |
| M18.04 (H; :13232) | Hidden `C` plus row motions; no grammar pair, though R2 exists. | H; P0; R2. | Q1: “Type any valid effect-equivalent row overwrite one cell past the return extreme; grade the hand-authored overshoot.” (open typed-key, **Before**). Q2: “Why must `C` preserve the row’s left prefix?” (why, **After**). |
| M18.05 (X; :13378) | Hidden expression substitute `:4s/0/\=getline(1)…/`; first use is hidden and current hint is generic. | H; P0; R2. | Q1: “Decode `\=` in an Ex replacement and explain why `getline()` may validate CHECK digits but must not generate art.” (decode/why, **Before**). Q2: “Complete `:4s/0/___/` with a validation-only expression marker.” (complete, **Before**). |
| M18.06 (T; :13521) | Hidden hand-mirror transfer using `C`; no paired question. | H; P0; R2 transfer review. | Q: “Hand-mirror the unfamiliar actor through three explicit row overwrites; type keys and grade semantic cells, not byte reversal.” (open typed-key, **Before**). |
| M18.07 (C; :13630) | No edit; current diagnosis pool does not complete expression/manual-mirror grammar. | P-MC; R0. | Q: “The slash limb points inward and CHECK digits changed art. Diagnose manual-row and validation-expression errors, then complete the safe check-only form.” (diagnose + complete, **Before**). |
| M18.08 (K; :13655) | Hidden `:5,8t$<CR>` and `:1,4t$<CR>`; Ex range copy still lacks completion/pair. | H; P-MC; R2. | Q1: “Decode and complete both addressed range copies, then type any valid reverse-order reuse path.” (decode + open typed-key, **Before**). Q2: “Why is the two-frame turnaround hold intentional rather than a dead duplicate?” (why, **After**). |

## Current-revision first-use ledger

The `.22` check confirms **47 card-level hidden-first violations** under the
strict rule (a family must have a current grammar explanation, interpretation,
completion, and visible guided performance before a hidden requirement). This
is the 46-card VD-12 list at `FAILURE_LOG.md:1830-1895`, still present in the
current expected paths, plus the new expression-substitution requirement in
M18.05 (`share/curriculum-v2.json:13378-13520`). Several rows contain more
than one family, so the number of individual family misses is higher than 47.
The new/most consequential rows are:

| Current `.22` card | Family first required without the full prior sequence | Evidence and required repair |
|---|---|---|
| M0.04 | `G`; `:8s/-/=/g<CR>` | `share/curriculum-v2.json:848-919`; add the M0 primer, typed `yy/p`, `o`, Ex decode/complete before hiding keys. |
| M0.05 | `:[range]t{address}<CR>` | `:920-1004`; add visible addressed-copy grammar and effect-graded practice. |
| M1.04 | `3dd`; `o/O` | `:1377-1430`; add operator/linewise and open-line lessons before the hand-authored frame. |
| M3.04/M3.06/M4.04 | `ci(`; Visual-line/registers; Visual block | `:2381-2573`, `:3065-3194`; add guided text-object, register, and block cards. |
| M6.04/M6.06 | `D`; `:range m{destination}` | `:4355-4631`; add `D=d$` and Ex move grammar/completion before hidden use. |
| M7.04/M7.05 | `.`; macro `q/@`; `:global … normal!` | `:5146-5483`; add guided repeat, macro, and global-normal cards. |
| M8.04/M9.04/M10.04 | `o`; `x`; `i` | `:5952-6065`, `:6511-6587`, `:7006-7148`; teach row-count and fixed-cell consequences before hiding. |
| M11.04/M11.08 | `u/<C-r>`; `:set virtualedit`; `i`; `.` | `:7549-8022`; add recovery, option, and exact-column typed-key stages. |
| M12.04/M13.04/M14.05 | `;/,`; `E/B`; `}/P` | `:8221-8526`, `:8897-9210`, `:9826-10011`; add standalone motion/object interpretation and completion. |
| M15.01/M15.05/M16.05/M17.05 | `:set`/`>>`; Visual block; `:m`; `:global/normal!` | `:10344-10687`, `:11584-11769`, `:12470-12641`; make the grammar bridge precede each hidden comparison. |
| M18.05 | `\=` expression replacement with `getline()` | `:13378-13520`; add a guided validation-only exercise and an explicit completion distinction before the comparison. |

## Four-report reconciliation

The three existing range reports and the requirement ledger were read as
written, not silently narrowed:

- `share/audits/grammar-sequence-M0-M4.md:80-318` covers M0–M4 and correctly
  identifies missing completion stages, hidden-first `:t`, block, `dd`, `o`,
  and `ci(` paths.
- `share/audits/grammar-sequence-M5-M9.md:85-283` covers M5–M9 and correctly
  identifies Visual-line, `D`, `:m`, dot, macro/global, `o`, `x`, and `i`
  gaps.
- `share/audits/grammar-sequence-M15-M18.md:80-252` covers M15–M18 and
  correctly identifies `:set`, `>>`, block append, macro, `:read`, `:m`,
  search/dot, global/normal, and expression gaps.
- `share/audits/grammar-sequence-M10-M14.md` supplies the fourth module
  partition with generated `.22` line anchors. The M10–M14 rows above
  reconcile that report into this full-card matrix. They do not remove any
  requirement from `GRAMMAR_FIRST_REQUIREMENT.md:10-35,69-90`; they add the
  per-card evidence that report requires.

The aggregate in `GRAMMAR_FIRST_REQUIREMENT.md:47-67` says 114 executable cards
and no ordinary card pairing. Against `.22`, the exact refinement is 57 cards
with any question IDs (the 38 concept cards are not paired to an edit), 95
without IDs, 31/114 executable cards with explicit `review_variants`, and 19
transfer cards whose two `variants` also feed the changed-art review route.
Thus 50/114 are review-capable and 64/114 have no changed-art bank. A concept
card's five choices and a module check's ten choices do not close the floor
rule for the other 95 cards.

## Full M0 grammar-first proposal

This is the required sequence to implement only after operator approval. It
does not change `.22` here.

1. **M0.00 grammar primer.** Ask the learner to name the parts, not memorize a
   cheat sheet: “For `3dw`, which part is the count, which is the operator,
   and which is the motion/object? For `:8s/-/=/g<CR>`, point to the address,
   command, pattern, replacement, flag, and execution key.” Follow with a
   completion item and one scratch-buffer effect check. Also state that `r`,
   `p`, `o`, and `.` are standalone commands, not forced into operator
   grammar.
2. **M0.01 — `r`.** Before showing the recipe: “You are on the top ray;
   type a valid path to the core and replace only it.” Grade cursor/result in a
   scratch Neovim buffer. Then show the accepted family vocabulary and ask,
   “Why `r` rather than `x`?”
3. **M0.02 — `yy/p`.** Before the recipe: “Copy all three frame rows and put
   them below; type it.” Grade any valid effect-equivalent answer. Ask,
   “What does the `3` count in `3yy`, and where does `p` put the text?” Then
   show the keys and require a visible guided copy.
4. **M0.02b — `o/O` row insertion.** This is a short guided exercise inserted
   before substitution: “Add one blank row below the frame, type one marker,
   escape, and keep all existing glyph columns.” Grade row count, column 1,
   and restoration after undo. Ask, “Why does `o` change row count while `r`
   does not?” This is the requested `o` stage, and it also prevents the
   learner from meeting open-line entry for the first time in a hidden card.
5. **M0.03a — ranged `:s` interpretation.** Ask: “Decode
   `:8s/-/=/g<CR>`.” Then ask: “Complete `:8s/-/=/___<CR>` so every dash on
   row 8 changes.” Require the learner to say address `8`, command `s`,
   pattern `-`, replacement `=`, flag `g`, and Enter. Ask a predict question
   about the row before any exact recipe is shown.
6. **M0.03b — visible `:s` performance.** “Type a valid range substitution
   that changes only the dashes on the copied flare row.” Grade the scratch
   buffer/result, not exact text; `:8s/-/=/g<CR>` and any semantically valid
   equivalent pass subject to the scope invariant. Show the canonical path
   only after the effect check.
7. **M0.04 — key-hidden retrieval.** Re-show the grammar breakdown after any
   wrong answer, then ask: “The copied flare exists. Change only its
   horizontal dashes. Type the keys.” Hide the exact path. After pass ask,
   “Predict why the rays remain registered and why this is a frame change,
   not a translation.” Only then schedule changed-art spaced review.

The optional control after every result is `Next`: it advances to the next
eligible item only after remediation/evidence rules are satisfied. It is not
an XP bypass.

## Runtime/generator mechanics required after approval

These are names and contracts, not implementation:

1. **Typed-key effect grading.** A question stores a scratch-buffer fixture,
   allowed semantic outcome, forbidden scope changes, and the command family.
   The learner's actual keys are replayed in scratch Neovim; `4j` and
   `:+4<CR>` can both pass a “down four lines” question when they produce the
   required cursor state. Exact text remains available as a test oracle, not
   as the learner's only valid answer.
2. **Grammar breakdown re-show on wrong answer.** A failed decode, completion,
   or typed-key attempt immediately re-shows the relevant breakdown (count,
   operator, motion/object; or address, command, arguments, flags, Enter),
   names the observed scope/result error, and requires a changed retry. A
   wrong answer cannot silently advance or award family evidence.
3. **Optional `Next`.** Result screens expose an explicit `Next` action for
   the next eligible lesson/question, while retaining close/retry. `Next`
   respects prerequisites, remediation, hidden-key evidence, and due review.
4. **Card-owned sequence fields.** Each executable card needs command-family,
   grammar class, teaching stage, `paired_question_ids`, habit/stage links,
   hidden-key policy, and changed-art review linkage. The generator must
   reject first hidden use without prior grammar/I/C/G and must reject a card
   without at least one paired question unless it carries a card-specific
   written exception.
5. **Coverage proof.** A report must fail when any H1–H9 or S0–S7/A0–A7 row
   lacks both a key-hidden required performance and a changed-art spaced
   review. It must separately report related-but-not-qualifying cards such as
   `:diffthis` absent, `:%s/\s\+$//e` absent, and undo-tree exploration absent.

## Operator gate

This audit stops here. No generator, runtime, test, or curriculum JSON change
is authorized by this document. The operator should approve or amend the
matrix, question wording, M0 insertion order, and three mechanics before any
implementation begins.
