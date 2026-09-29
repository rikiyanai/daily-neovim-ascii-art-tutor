# Stone Story animation audit — batch-1

- Date: 2026-09-28
- Auditor: subagent batch-1 (manual view of every listed sheet)
- Base: `~/Downloads/stone-story-consolidated/` (sheets), `~/Downloads/stone-story-official/<Category>/<Name>.txt` (StoneScript source)
- Sheet list: `share/audits/animation-frame-paths.txt`
- Conventions: `#` converted to space, rows right-trimmed. Size = rows x max cols. Composite frames (part layers drawn over a base block at the script's shared origin) are marked `A+B` and keep the shared canvas (leading blank rows shown only where the vertical offset is the animation).
- Width note: box-drawing (`─ └ ┘ ╪ ╞ ╡ ├ ┤`), Greek (`ε ∆`), `´ ¯ ° ‾` are East-Asian-Ambiguous width. They are single-width in Western monospace fonts (Menlo, Inconsolata) but can render double in a CJK-ambiguous-wide terminal (`ambiwidth=double`). Flagged per set.

## official-Pets/Skully

- Sheets viewed (46/46): res01–res46 (every file opened; res23 is an empty block).
- Source: `~/Downloads/stone-story-official/Pets/Skully.txt`
- Non-ASCII: `´ ε ╪ └ ─ ┘ ╞ ╡ ∆ ¯ ├ ┤` (all Ambiguous width; OK in Menlo/Inconsolata, flag for ambiwidth=double).

**What it depicts.** A floating pet skull (`,--.` / `(_o,o)` / `` `"´ ``) following the player.
Blocks, all drawn at the same origin `>o@myX@,@myZ@`:
- res01 idle skull (3x10 in a 6-row canvas). res02/res03 eye-look layer `O,o` / `o,O` (alternate on `time % 4`, 2 frames each, only while `face = "°°"`). res04/res05/res06 blink layer `=,=` → `-,-` → `=,=` (stateTime%50 in 44–45, 46–47, 48–49).
- res07–res16 victory "chest" sequence (face `( ^^`): skull rises one row per stage (res07 row 3, res08 row 2, res11 row 1, res14 row 0) while a chest layer (bone res09/12/15 or delta res10/13/16) appears below and opens. chestTime ≤5, ≤10, ≤15, ≤30, then reverses 30→40.
- res17–res22 "moving" skull: six identical copies of res01 (stateTime/2 = 0..5) — frames identical.
- res23–res46 movement-trail layers (cloud/sparks/wings/chesttrail, four per stateTime/2 step, drawn after the skull). Wings trail res25→res29→res33→res37→res41→res45 is a 3x8 flap cycle (up, mid, down, mid, up, fold); cloud/sparks/chesttrail are 1–3-cell puffs.

**True frame sequences.**
1. Blink/look (res01 + res02..res06): 5 frames, 3x10, same origin. IDEAL fit.
2. Chest rise (res07, res08+res09, res11+res12, res14+res15): 4 frames, 6x11 canvas. IDEAL fit.
3. Wing flap (res19 + res25/29/33/37/41/45): 6 frames, 6x10 composite (wing layer alone 3x8). IDEAL fit.

**Diffs and edits.**
- idle → blink1: row 2 cols 7 and 9 (`o`→`=` twice). Edit: `2G0for=;r=` (or `2G7|R=,=<Esc>`).
- blink1 → blink2: same 2 cells `=`→`-`. Edit: `:2s/=,=/-,-/`.
- idle → look-left: 1 cell (col 7 `o`→`O`). Edit: `2G0forO`. look-left → look-right: 2 cells (col 7 `O`→`o`, col 9 `o`→`O`). Edit: `2G0fOro2lrO`.
- chest stage 2 → 3: skull block moves up one row (3 rows shifted) and chest row gains `=o=`. Edit: `1Gdd` then `3G0f r=` … too big for 1–6 cells; teach as `:1d` + `Go<row>` "hold the chest, move the head" (layer exercise), 3 cells change in the chest lid (`   `→`=o=`: `5G0f╪lR=o=<Esc>`).
- chest stage 3 → 4: new lid row `___` inserted above chest, skull shifts up 1. Edit: `4GO      ___<Esc>` + `1Gdd`.
- wing up (res25) → mid (res29): all 3 wing rows change (~10 cells) — too many for one lesson edit; up → fold (res41 → res45) removes row 1 and 3 cells: `2Gd$` then `3G0f.r ` … bounded at ~4 cells.

Frames (blink/look, 3x10):
```
     ,--.
    (_o,o)
      `"´

     ,--.
    (_=,=)
      `"´

     ,--.
    (_-,-)
      `"´

     ,--.
    (_O,o)
      `"´

     ,--.
    (_o,O)
      `"´
```

Frames (chest rise, 6-row canvas, 6x11):
```



     ,--.
    (_o,o)
      `"´


     ,--.
    (_o,o)
    ε╪`"´╪3
     └───┘

     ,--.
    (_o,o)
      `"´
    ε╪=o=╪3
     └───┘
     ,--.
    (_o,o)
      `"´
      ___
    ε╪=o=╪3
     └───┘
```

Frames (wing flap composites, 6-row canvas, 6x10):
```

  .\   ;
  ( \ |
    ¯,--.
    (_o,o)
      `"´

  __   _
 \  \ /
  `¯¯,--.
    (_o,o)
      `"´


 ___
/_.'¯,¯-.
    (_o,o)
      `"´


   (\ |
    ¯,--.
    (_o,o)
      `"´
```

**Tutor fit.** Blink/look is a textbook M2 Face focus / M11 Fixed-width redraw exercise: a stable contour with a 1–2 cell acting change inside `(`…`)`, and a real hold/blink timing (open 44 ticks, `=` 2, `-` 2, `=` 2). Chest rise fits M5 Layered scene (chest layer with transparent cells letting the skull's jaw `` `"´ `` show through — real negative-space seam) or M7 Timed build (script holds: ≤5, ≤10, ≤15, ≤30 then reverse). Wing flap fits M4 Rotation tween (extremes up/down with mid), but row-wide edits.

**Verdict: USE** — blink/look → **M2 Face focus** (edit `:2s/o,o/=,=/` or `2G0fo r=;r=`), also M11. Chest rise → **MAYBE M5**. Wing flap → **MAYBE M4**. The six "moving" copies are identical (REJECT as frames).

## official-Pets/Panda

- Sheets viewed (28 listed + 4 unlisted = 32/32): res01–res28 (walk frames), res29–res32 (eye "phiz" layers `o   o`, `=   =`, blank, `^   ^`).
- Source: `~/Downloads/stone-story-official/Pets/Panda.txt`
- Non-ASCII: `▄ ▀ █ ░ ▒ ▓ ´ ¡ ╩` — block elements and box drawing, all Ambiguous width. Heavy use of solid blocks; risky under ambiwidth=double and visually dense for a beginner.

**What it depicts.** A walking panda pet. Two arrays, each 14 frames at the same origin `>o@sx@,@sy@`:
- `animationFramesSide` = res01–res14: side-view walk cycle, advanced one frame per movement tick (`frame = (frame + 1) % count`), speed 1–3 by distance; `frame = 0` when stopped.
- `animationFrames` = res15–res28: same walk with head turned toward camera; used when `side` is false (stopped with `phizTimer <= 28`, or boss-kill happy face). Eye layer res29–res32 drawn at `+26,+4` (open; blink `=` at phizTimer 4 and 0; closed 1–3; `^` happy).

**Sizes.** res01–08 9x30, res09–14 9x31, res15–28 9x33 → ACCEPTABLE (≤10x34), not IDEAL. Clean crops: legs rows 6–9 (4x30, still too wide for IDEAL); head rows 1–7 cols 20–33 of the front-facing frames (7x14, IDEAL) for the eye blink.

**Diffs.** Walk res01→res02: 6 cells, rows 6–8 (front paw lifts: r6c23 ` `→`\`, r7c22–24 `   `→`|_)`, r8c22–23 `_)`→`  `). Every other walk pair: 31–86 cells over rows 4–9 (all legs + body sag). res01→res15 head turn: 64 cells. Eye layer: 2 cells.

**Edits.**
- res01→res02 (6 cells): `6G23|r\` then `7GA|_)<Esc>` (row 7 ends at col 21) then `8G22|D` (paw lift).
- head crop open → blink: `:5s/o/=/g` (2 cells); blink → closed: `:5s/=/ /g`.

Frames (walk contact → paw lift, 9x30, ACCEPTABLE):
```
         ▄▄▄▄▄▄▄▄▄▄-▄▄▄  _
      ▄██████████▀´ `▀██( ▄
    ▄████████████     ▀██▄██
  ▄▓▓▓███████████      ▓███o██
  ░░████▒▒▓▓▓████     |▒▒████▄
  ; `▀▀█▓▓▓██████|   /   ▀▀▀
 /  /  \   \     |  /
|  |    `   \    !  `_)
 .__)    `___)    \__)

         ▄▄▄▄▄▄▄▄▄▄-▄▄▄  _
      ▄██████████▀´ `▀██( ▄
    ▄████████████     ▀██▄██
  ▄▓▓▓███████████      ▓███o██
  ░░████▒▒▓▓▓████     |▒▒████▄
  ; `▀▀█▓▓▓██████|   /\  ▀▀▀
 /  /  \   \     |  /|_)
|  |    `   \    !  `
 .__)    `___)    \__)
```

Frames (front head crop of res15 + eye layer res29/res30, 7x14, IDEAL):
```
▄-▄▄▄▄▄
´ `▀██████▄_
    ░( )███ )
   ░▒▓▄█████▄
 __.░▒█o███o█▄
 \ /-▀███╩███▀
 |_)   ▀▄▄▄▀

▄-▄▄▄▄▄
´ `▀██████▄_
    ░( )███ )
   ░▒▓▄█████▄
 __.░▒█=███=█▄
 \ /-▀███╩███▀
 |_)   ▀▄▄▄▀
```

**Tutor fit.** The only full 14-frame quadruped walk cycle in this batch — real contact/passing positions and equal frame height, which is what M8 Walk study teaches. But frames are 30–33 cols (two side by side = 62–68 cols, fits 80 only with a thin gutter), per-frame edits are 30–60 cells, and the solid-block glyphs are ambiguous-width. The head-crop blink is a clean M2-style 2-cell change but is a crop through the body (paw fragment at left).

**Verdict: MAYBE** — M8 Walk study (study/playback only, not per-frame authoring; teach res01→res02 paw lift as the one bounded edit). Head blink crop: MAYBE for M2. REJECT as IDEAL-size art.

## official-Games/FrogJump

- Sheets viewed (22 listed + res03 unlisted = 23/23; there is no res24): res01 logo, res02 river (10 frames `%%`), res03 bank edge, res04–res11 lily pads, res12–res19 coins, res20 eagle, res21 FrogJump (8 frames), res22 FrogEye (8 frames), res23 JumpArrow (6 frames).
- Source: `~/Downloads/stone-story-official/Games/FrogJump.txt` (ui.AddAnim blocks; `%%` separates frames inside one block).
- Non-ASCII: `´ ‾ ·` in the frog; `ò` in the eagle; `‾` in logo/coins. All Latin-1/Ambiguous; single-width in Menlo/Inconsolata. `´` and `‾` need digraphs to type (`<C-k>''`, `<C-k>'-`).

**What it depicts / true sequences.**
- **res21 FrogJump + res22 FrogEye**: a frog's full jump, 8 frames, `FrogJump.duration = 30` by default, then `duration = round(sqrt(200*presstime))` (charge-to-jump); `loop = true` in the menu. FrogEye is a same-origin, same-timing eye layer (`--` shut → `=-` → `O-` → `Oo`) drawn in white over the green frog; in plain text it adds no cells. Order: sit (eyes shut) → crouch/tuck → launch stretch → airborne extension → apex → descending → landing → sit. Every frame 5x9 → **IDEAL**.
- res23 JumpArrow: 6 frames, the dotted arc of the jump trajectory growing one segment per frame (frame = charge level). 9x7 → 9x17 → ACCEPTABLE.
- res02 River: 10 frames x 14 rows x 100 cols, each frame the same wave texture shifted 1 column (scroll loop, duration 50) — TOO-LARGE; crop 5x26 works as a texture scroll.
- res04–res11 lily pads (8 identical copies; frame 1 is blank = hidden), res12–res19 coins (8 identical), res20 eagle (single 20x35 pose), res01 logo, res03 edge: not animations.

**Diffs (frog, 5x9 frames).** f0→f1 18 cells (rows 2–5), f1→f2 21, f2→f3 13, **f3→f4 8 cells** (r1c8 `-`→`o`; r3c1–4 ` _(/`→`` -´-` ``; r4c1–3 `-´‾`→blank), f4→f5 19, f5→f6 26, **f6→f7 9 cells** (rows 3–5). JumpArrow: every step 25 cells but one rule (shift up 1, right 2, add tail row).

**Edits.**
- frog f3→f4 (8 cells, one eye opens + tail lifts): `1G$ro` then `` 3G0R-´-`<Esc> `` (type `´` as `<C-k>''`) then `4G0D`.
- frog f6→f7 (9 cells, landing settle): `3G0R     ,<Esc>` then `4G2|R (\/<Esc>` then `5G3|R´ ·<Esc>`.
- JumpArrow n→n+1: `:%s/^\ze./  /` then `ggdd` then `Go.;;;:<Esc>` (shift + new segment; exercises Ex range + `o`).

Frames (frog jump, 8 x 5x9, IDEAL):
```
f0 (sit)


     ,--
   (! .-)
   '·-((

f1 (tuck)

     ,--
    / .-)
  _(;-//
   `

f2 (launch)
     .=-
    / .-)
  _(/-)´`
 -´‾

f3 (stretch)
     .O-
   ,´ .-)
 _(/--‾´‾
-´‾

f4 (apex)
     .Oo
   ,´ .-)
-´-`--‾´‾


f5 (descend)

     .Oo
-´-`´ .-)
    `-‾´‾

f6 (land)


  _  .Oo
 /-`´ .-)
   `--\´\

f7 (settle)


     ,Oo
  (\/ .-)
  ´ ·-\´\
```

Frames (JumpArrow f0–f2 of 6, growing arc):
```




.......
  ;;;:;
.;;;::;
      '



  .......
    ;;;:;
  .;;;::;
.;;;:   '


    .......
      ;;;:;
    .;;;::;
  .;;;:   '
.;;;:
```

**Tutor fit.** The frog jump is a complete, real squash-and-stretch jump arc at IDEAL size — the natural replacement for invented art in **M9 Bounce capstone** (plan, keyframe, tween, squash: f1 tuck = squash, f3 = stretch, f4 = apex, f6 = landing squash). Also M3 Pose copy (duplicate f3, change one acting feature: eye `-`→`o`). Frame height is 5 (M9 currently uses 3; the module would need 5-row frames). JumpArrow fits M6 Pyramid build / M16 Key-pose plan (additive build, playback order).

**Verdict: USE** — frog jump (res21[+res22]) → **M9 Bounce capstone** (edit f3→f4: `1G$ro` + `` 3G0R-´-`<Esc> `` + `4G0D`). JumpArrow → MAYBE M6. River → MAYBE M15 (crop). Pads/coins/eagle/logo/edge → REJECT (identical copies / single pose / UI).

## official-Games/BurgerRush

- Sheets viewed (18 listed + res19–res22 unlisted = 22/22; no res23): res01 plate, res02 arrow, res03 bottom bun, res04 patty, res05 cheese, res06 tomato, res07 lettuce, res08 top bun, res09 inboundHelper, res10 readyHelper, res11 outboundHelper, res12–res18 held-item icons (0–6), res19–res22 title/instruction text.
- Source: `~/Downloads/stone-story-official/Games/BurgerRush.txt`
- Non-ASCII: helper uses `‾` only (Ambiguous, single in Menlo). Burger layers use `≡ ═ ╤ γ τ ε Ω σ ρ α ·` (Greek + box drawing, Ambiguous) — poor for a beginner buffer.

**What it depicts / true sequences.**
- **Helper on a boat (res09 → res10 → res11)**, same origin `>`@helperAnimX@,11`: state 0 inbound (paddles in, box lid closed `___`, arm raised `o/`), state 1 ready/standing by (lid flipped open `\`), state 2 outbound (lid closed again, box empty `| |`, arm down `<|\`). Held-item icon (res12–res18) is drawn on top at the same origin. State-driven, not timed: inbound until x=23, ready until the player takes the item, outbound until x=-14. Each 7x14 (5 content rows + 2 blank top rows) → **IDEAL**.
- **Burger stack (res03 → +res04 → … → +res08)**: layers drawn in order at the same centered origin `>c@plateX@,@plateY@` as the player adds ingredients (plate1State 1..5). 7x12 → IDEAL. Alignment inferred: all layers treated as top-left aligned (res03 is 12 cols, the rest 11, so `>c` centering may shift by ≤1 col).
- Plate/arrow/held icons/text: single stills or UI.

**Diffs and edits.**
- res09→res10 (lid opens): 3 cells, row 4 cols 3–5 `___`→`\  `. Edit: `4G3|R\  <Esc>` (or `4G0f_r\lD`… simpler `4G3|3r ` then `r\`).
- res10→res11 (hand-off done, turn to leave): 7 cells over rows 3–5 (r3c9 `/`→` `, r4 `\ `→`___`, r4c7 `/`→`<`, r4c9 ` `→`\`, r5c4 `X`→` `). Edit: `3G$x` then `4G3|R___<Esc>` then `4G0f/r<A\<Esc>`, `5G0fXr `.
- Burger stack step (e.g. +tomato): 10 cells, one new row: `4G0R ==========<Esc>` (or `O` above the cheese).

Frames (helper, 5 content rows x 14 — blank top rows dropped):
```
       o/
  ___ /|
  |X| / \
\‾‾‾‾‾‾‾‾‾‾‾‾/
 \__________/

       o/
  \   /|
  |X| / \
\‾‾‾‾‾‾‾‾‾‾‾‾/
 \__________/

       o
  ___ <|\
  | | / \
\‾‾‾‾‾‾‾‾‾‾‾‾/
 \__________/
```

Frames (burger stack, final build step shown; 7x12, alignment inferred):
```
 εΩσραΩρεΩσ
 ==========
 ╤════╤═══╤
 γ≡≡≡≡τ≡≡≡!
'.________.'

   .·::·.
 /________\
 εΩσραΩρεΩσ
 ==========
 ╤════╤═══╤
 γ≡≡≡≡τ≡≡≡!
'.________.'
```

**Tutor fit.** Helper: **M3 Pose copy** (duplicate the key pose with `yap`/`:t`, change one acting feature — the lid `___`→`\`) or M2 Face focus-style bounded edit inside a stable contour (boat and figure stay fixed). All-ASCII except `‾`. Burger stack: M6 Pyramid build / M5 Layered scene (additive layer order) but the Greek/box glyphs make it a poor typing target.

**Verdict: USE** — helper res09→res10→res11 → **M3 Pose copy** (edit `4G3|R\  <Esc>`). Burger stack → MAYBE M6 (glyph set is the blocker; an ASCII-substituted version would be USE). Rest REJECT (UI/stills).

## official-Cosmetics/CaveParty

- Sheets viewed (17 listed + res10–res13, res16 unlisted = 22/22; no res23): res01 Backflip (13 frames), res02 stickyStickGuy (7), res03 ladder, res04 annoyingGuy (37), res05 lavaPool, res06 lavaAnim (4), res07 uulaaIdle (2), res08 fireChargeUp (13), res09 fireBlast (16), res10 cake, res11 sprinkles, res12 table, res13 sorceress, res14 musicNotes (21), res15 magicStaff (5), res16 speaker, res17–res22 speech boxes.
- Source: `~/Downloads/stone-story-official/Cosmetics/CaveParty.txt` (all via `MakeUIAnim(x,y,art,color,duration,loop,play,…)`, `%%` frame separators).
- Non-ASCII: Backflip uses `¯ ─` (2 cells total); stickyStickGuy `¯`; magicStaff `§ ·`; fire `☼ ʘ ·`; notes `♪ ♫`; boxes `─ │`; lava ASCII only. `♪ ♫ § ·` are Ambiguous width; `☼ ʘ` often missing from fonts.

**What it depicts / true sequences.**
- **res01 Backflip** (John, played on click; duration 26 ticks for 13 frames = 2 ticks/frame, no loop): stand → crouch-rise → tuck → horizontal `>->o` → inverted `))/_\¯/o` → inverted `\)/|//o\` → `)>/─/_/o` → horizontal `o<-<` → landing crouch → stand (f9–f12 identical hold). A genuine 360° rotation about a near-fixed pivot. All frames in a 6x5 canvas → **IDEAL**.
- **res06 lavaAnim** (duration 40, loop): 3x17 bubbling `~ ~ ~` texture; each frame shifts one row by one column (14–15 cells, but a single `x`/`I <Esc>` edit). IDEAL.
- res04 annoyingGuy (32 ticks, 37 frames): an `!` bobbing over a stick figure (2-cell moves), then the figure vanishes and its head `o` flies right along an arc 1 col/frame into the lava, ending in a splash (9x17). The `!` bob and flying `o` are 2-cell `xp`-style moves. ACCEPTABLE (12-row canvas, crop 9 rows).
- res02 stickyStickGuy (90 ticks loop, 7 frames): 3x7 figure sitting then leaning out (f0–f2 identical, f3/f6 identical, f4/f5 identical); 11–13 cells per change.
- res07 uulaaIdle: 2 frames 5x12 (caveman face; arm/hand at rows 4–5 changes, 8 cells) but duration 1 / play false — frame 1 used as a pose swap by dialogue.
- res15 magicStaff (20 ticks loop): 7x7, staff tip `{§/`→`{§|`→`{§\` sway + three `·` sparkles orbiting, 7 cells per frame.
- res08/res09 fire charge/blast: particles `☼ ʘ` and a 17-row fireball — REJECT (glyphs, size). res14 music notes `♪♫` — REJECT (glyphs). res03/05/10–13/16/17–22 stills/UI.

**Diffs and edits (Backflip, 6x5 canvas).**
- f0→f1: 6 cells (figure rises one row, arm bends). f1→f2: 8. f2→f3: 9. f3→f4: 7. f4→f5: 9. f5→f6: 9. f6→f7: 7. f7→f8: 8. f8→f9: 6 (landing stand). All ≤9 cells — every step a bounded lesson edit.
- f3→f4 (horizontal → first inverted, 7 cells): `2Gi ))<Esc>` (row 2 is empty) then `3G2|R_\¯ <Esc>` (type `¯` as `<C-k>'m`) then `4Gi   o<Esc>` (row 4 is empty).
- f8→f9 (landing crouch → stand, 6 cells): `5G0R/|\ <Esc>` then `6G0R/ \  <Esc>`.
- Midpoint lesson (M4): given f3 `>->o` and f7 `o<-<` as extremes, author f5 (inverted) as the midpoint.
- Lava f0→f1: 14 cells, one edit: `3GI <Esc>` (or `3G0x` for the reverse). Lava f1→f2: `2G0x`.
- annoyingGuy f21→f22 (head flies 1 col): `6G0foxp`.

Frames (Backflip f0–f9, 6-row canvas, IDEAL):
```
f0


  o
 /|\
 / \

f1

  o
  |)
 / \


f2

   o
 ¯/_
 ((


f3

 >->o



f4
 ))
 _\¯
   o



f5
  \)
  |
 /o\



f6

   )>
 ─/_
 o


f7


 o<-<



f8


 o
 (\;
  < \

f9


 o
/|\
/ \
```

Frames (lavaAnim, 4 frames of 3x17 — first row blank):
```

    ~ ~ ~ ~ ~ ~ ~
   ~ ~ ~ ~ ~ ~ ~

    ~ ~ ~ ~ ~ ~ ~
    ~ ~ ~ ~ ~ ~ ~

   ~ ~ ~ ~ ~ ~ ~ ~
    ~ ~ ~ ~ ~ ~ ~

   ~ ~ ~ ~ ~ ~ ~ ~
   ~ ~ ~ ~ ~ ~ ~
```

Frames (stickyStickGuy key poses f0, f3, f4; 3x7):
```
 o_
 |¯\
 )\ \

  o_
 /,¯\
/ \  \

   o_
  / ¯\
 /)   \
```

**Tutor fit.** Backflip is the best **M4 Rotation tween** source seen so far: a real full rotation, 4–5-cell-wide frames, stable pivot, two readable horizontal extremes (`>->o` / `o<-<`) and an inverted midpoint; every step 6–9 cells. Also M9 (squash at f1/f8). Lava is a ready-made **M13 Texture pulse** / M15 texture exercise (row shift by one `I <Esc>`/`x`). stickyStickGuy: M3/M8 secondary motion, MAYBE. magicStaff: MAYBE M12 (`t`/`f` to the tip glyph), but `§ ·` glyphs.

**Verdict: USE** — Backflip res01 → **M4 Rotation tween** (edit f3→f4: `2Gi ))<Esc>` + `3G2|R_\¯ <Esc>` + `4Gi   o<Esc>`). lavaAnim res06 → **USE M13** (`3GI <Esc>`). stickyStickGuy → MAYBE M3. annoyingGuy → MAYBE M0/M17 (`xp` moves). magicStaff → MAYBE M12. Rest REJECT (UI, stills, wide/missing glyphs, too large).

## official-Cosmetics/Party

- Sheets viewed (12 listed + res01, res02, res05, res16, res17 unlisted = 17/17; no res18): res01/res02 party hat (big/normal head), res03 present, res04 commented-out present, res05 balloon pin, res06 balloon1 (4 frames), res07 balloon2 string (4 frames), res08 confetti (6 glyph frames), res09–res15 cake pet, res16 UI button, res17 UI back.
- Source: `~/Downloads/stone-story-official/Cosmetics/Party.txt` (cake pet code is copied from PetFrog: stateIdle / stateJump, `stateTime/2` = 0..5).
- Non-ASCII: cake uses `¡ ¯ │ ─` (Ambiguous); present `│ ¯`; pin `┬`. Balloon + string + confetti are ASCII only.

**What it depicts / true sequences.**
- **Cake pet hop (res09 idle; jump: res10 st/2=0 squash, res11 =1 rise (= idle), res12/13/14 =2..4 airborne (identical), res15 =5 land (= idle))**, drawn at `>o@myX@,@myZ@`, 12-tick jump, 2 ticks per block. Distinct frames: idle, squash, air. 6x9 canvas → **IDEAL**. The body moves as a block (1 row down for squash, 1 row up for air) and only the base changes shape.
- **Balloon (res06) + string (res07)**: `duration 60`, loop; balloon bobs 1 row/1 col, string sways (`|`/`!`/`'` tip, 2–3 cells per step). String alone 5x3; composite 6x6 (alignment inferred from `a1.x=1, a1.y=-1`).
- res08 confetti: one cell cycling `. - , * ` +` (particle, 1x1).
- Presents, hats, pin, UI: stills.

**Diffs.** Cake idle→squash 32 raw cells but structurally: content shifts down one row + new base `'──___──'` replaces `!__'-'__!`/`¯¯¯`. idle→air: content up one row + base becomes `│  '-'  │` / ` ¯¯───¯¯`. String f0→f1: 3 cells; f1→f2: 2; f2→f3: 2.

**Edits.**
- Cake idle→squash: `5,6d` then `ggO<Esc>` then `Go'──___──'<Esc>` (shift by line ops + one new base row).
- Cake idle→air: `ggdd` then `4G0R│  '-'  │<Esc>` then `5G0R ¯¯───¯¯<Esc>` then `Go<Esc>`.
- String f1→f2: `2G3|r|` then `3G3|r'` (2 cells).

Frames (cake idle / squash / air, 6x9, IDEAL):
```

    ¡
 ¡_¯¯¯_¡
│ o¯¯¯o │
!__'-'__!
   ¯¯¯


    ¡
 ¡_¯¯¯_¡
│ o¯¯¯o │
'──___──'
    ¡
 ¡_¯¯¯_¡
│ o¯¯¯o │
│  '-'  │
 ¯¯───¯¯

```

Frames (balloon + string composite, alignment inferred, 6x6):
```

 .-.
 \ /
 |^
 !
/

  .-.
  \ /
  !^
 /
/
  .-.
  \ /
  |^
  '
 /
/
```

**Tutor fit.** The cake hop is a real squash → stretch → land cycle with line-level edits (`dd`, `O`, `G o`) — a good **M9 Bounce capstone** alternative, weaker than FrogJump because the airborne frame is a pure translate and uses `│ ─ ¯ ¡`. Balloon string sway is a 2–3-cell loop suitable for M0 Spark loop (readable change, whole-frame copy).

**Verdict: MAYBE** — cake hop → M9 (edit idle→squash: `5,6d` + `ggO<Esc>` + `Go'──___──'<Esc>`); balloon string → MAYBE M0. Hats/presents/pin/confetti/UI → REJECT (stills, 1-cell particle, UI).

## official-Games/WhackaMole

- Sheets viewed (11 listed + res02–res05 = 14/14): res01 stump/decor, res02–res05 dirt clods, res06 mallet on a pole (23 rows), res07 creature portrait, res08 critter, res09 mole anim (10 frames), res10 board frame 27x41, res11 hole grid, res12 title plaque, res13 title letters, res14 plaque border.
- Source: `~/Downloads/stone-story-official/Games/WhackaMole.txt` (`moleanm[i]` = ui anim of `mole`, `duration = anmtime` 60 easy / 40 medium+hard, frame reset to 0 and stopped on hit).
- Non-ASCII: mole uses `… •` (Ambiguous). Board/plaques use `｛ ｝` = **FULLWIDTH (F), double-width in every terminal — unsafe**; plus `─ │ ║ ╫ ╠ ╣ ═ ┊ ´ ¯ ‾ ∞ ¡ ·`.

**What it depicts / true sequences.**
- **res09 mole pop-up** (10 frames, 40–60 ticks per play, no loop): empty → eyes peek → head+snout → full (paws `m   m`) → hold x3 → retreat mirror (full → head → eyes → empty). Symmetric reveal/hide. Each 5x6 (content ≤4x6) → **IDEAL**.
- Everything else: stills, board UI (27x41 TOO-LARGE and full-width braces), title art.

**Diffs.** f0→f1 7 cells (row 3 `…-…`, row 4 `:• •:`); f1→f2 11 (block moves up one row, new row `:>•<:`); f2→f3 16 (up one row + paws row); f3–f6 identical (hold); f6→f9 exact reverse.

**Edits.** Rising pattern = shift up one row and reveal one new bottom row: f1→f2: `ggdd` then `3Go :>•<:<Esc>` (with the canvas held at 5 rows via `Go<Esc>`). f2→f3: `ggdd` then `3Go m   m<Esc>`. Retreat = the same edits reversed (`u` / `<C-r>` demo for M11).

Frames (mole f0–f3, 5x6 canvas; f4–f6 hold f3; f7–f9 mirror f2–f0):
```
(f0 empty)




(f1)


  …-…
 :• •:

(f2)

  …-…
 :• •:
 :>•<:

(f3)
  …-…
 :• •:
 :>•<:
 m   m

```

**Tutor fit.** A clean additive reveal whose playback order is literally "build then un-build" — suits **M6 Pyramid build** (subtractive/additive authoring and playback order) and M11 (undo/redo replays the retreat). Weaknesses: `…` and `•` need digraphs (`<C-k>.,` does not exist; `…` is `<C-k>,.`, `•` is `<C-k>Sb`) — an ASCII substitute (`.-.`, `o o`) would be trivial.

**Verdict: MAYBE** — mole res09 → M6 Pyramid build (edit f1→f2: `ggdd` + `3Go :>•<:<Esc>`); upgrade to USE if `…`/`•` are replaced with ASCII. Board/plaque/decor → REJECT (UI, full-width `｛｝`, too large, stills).

## official-Pets/Snake

- Sheets viewed (10 listed + res01–res05 unlisted = 15/15): res01 idle, res02/res03 eye-look layer `o°`/`°o`, res04–res06 tongue layer `-`, `-<`, `-`, res07–res15 slither walk (9 frames).
- Source: `~/Downloads/stone-story-official/Pets/Snake.txt`
- Non-ASCII: `¯ ´ ·` in the body, `°` in the look layer (all Ambiguous; single in Menlo). The head (rows 1–3) and tongue are pure ASCII.

**What it depicts / true sequences.**
- **Tongue flick** (idle): res01 + res04 (stateTime%30 ≤2) → res05 (≤4) → res06 (≤6) → bare idle for the remaining 24 ticks. Layer drawn at the same origin, row 2 right of the head. 6x13–15; **head crop rows 1–3 = 3x15, IDEAL**.
- **Eye look** (`face = "°°"`): res02/res03 alternate on `time % 4` (2 ticks each).
- **Slither walk** res07→res15 (`stateTime % 9`, one frame per tick): head rows 1–3 fixed, body rows 4–6 ripple. 6x14 → **IDEAL**. (Walk frames sit 1 col right of res01.)

**Diffs.** Tongue: +1 cell (`-`), +1 (`<`), −1. Look: 2 cells. Slither pairs (rows 4–6 only): 17, **9 (res08→res09)**, 15, 18, 16, 14, 13, 12, 20 (res15→res07 loop).

**Edits.**
- idle → tongue out: `2GA-<Esc>`; → fork: `A<<Esc>` (or `.` after `2GA-<<Esc>` on a fresh copy); → retract: `2G$x`.
- look: `1G11|Ro°<Esc>` (2 cells; `°` = `<C-k>DG`).
- slither res08→res09 (9 cells): `` 4G0R`. <Esc> `` (3 cells) then `` 5G0R  ·`-<Esc> `` (4 cells) then `` 6G5|R`'<Esc> `` (2 cells).

Frames (tongue flick, head crop rows 1–3 of res01 + layer, 3x15, IDEAL):
```
         .-.
        ((`-'
         \\

         .-.
        ((`-'-
         \\

         .-.
        ((`-'-<
         \\
```

Frames (slither res07–res15, 6x14, IDEAL):
```
          .-.
         ((`-'
          \\
 .--._    _))
(´ `'.`¯¯.-´
       ¯¯

          .-.
         ((`-'
          \\
.-.      __))
´ `:'--'¯.-´
     `-'¯

          .-.
         ((`-'
          \\
`.       __))
  ·`---'¯.-´
    `'-'¯

          .-.
         ((`-'
          \\
 :      ___))
 \'---'¯_.-´
   `'-'¯

          .-.
         ((`-'
          \\
  .   _,.__))
 ('. ´.--.-´
  ` ¯´

          .-.
         ((`-'
          \\
     .--.__))
(·_.´.''-.-´
 `'-´

          .-.
         ((`-'
          \\
    .---.__))
__.´.' '-.-´
`'´

          .-.
         ((`-'
          \\
   .'¯'-.__))
 /.'´ `'-.-´
·´

          .-.
         ((`-'
          \\
  .'¯¯ -.__))
 (´   `'---´
  `
```

**Tutor fit.** Tongue flick is a perfect **M0 Spark loop** (3 rows, readable 1–2-cell change, insert-mode `A`, whole-frame copy between frames; real hold timing 2/2/2/24). Slither is a 9-frame secondary-motion cycle with a fixed head — good **M8 Walk study** (equal frame height, body wave; edits 9–20 cells, so teach 1–2 pairs, not all).

**Verdict: USE** — tongue flick → **M0 Spark loop** (edit `2GA-<Esc>` then `A<<Esc>`); slither → **USE M8** (res08→res09, 9 cells). Eye look → MAYBE M2.

## official-Cosmetics/StoneHeadless

- Sheets viewed (8/8): res01 smallbat (4 frames), res02 bigbat (4), res03 smallspider (6), res04 bigspider (9), res05 small skeleton (4), res06 big skeleton (8), res07 ghost (6), res08 big ghost (6).
- Source: `~/Downloads/stone-story-official/Cosmetics/StoneHeadless.txt` — UI anims that replace each foe type; frame advanced manually: bats every 2 ticks (`time%2`, loop 4), spiders every 3 ticks (loop 6), skeletons every 5, ghosts every 4. (Attack frames exist in `/* */` comments; the sheets hold the loop frames.)
- Non-ASCII: smallbat, ghost face rows and skeleton legs are ASCII; spiders use `∞` (body), ghosts `° ´`, skeletons `¯ ´`; **bigbat uses `＂` U+FF02 FULLWIDTH (double width — unsafe)**.

**What it depicts / true sequences.**
- **res01 small bat flap** (4 frames, 2 ticks each, loop): wings down/folded → spread level → wings up (body lifts one row) → mid. 4x8 canvas, 3 content rows → **IDEAL**; pure ASCII.
- **res03 small spider scuttle** (6 frames, 3 ticks each): body/head fixed, only the leg row (row 3) changes, 3–4 cells per frame. 3x7 → IDEAL.
- **res05 small skeleton walk** (4 frames, 5 ticks each): only the leg cells change (1–2 cells). 4x4 → IDEAL.
- **res07 ghost float** (6 frames, 4 ticks each): arms alternate `-' ° '-` ↔ `` ^´ ° `^ ``, tail wisp curls; 7–10 cells. 5x7 → IDEAL.
- res04 big spider (9 frames, 4x10, IDEAL; 3–13 cells), res08 big ghost (6 frames, 6x10, IDEAL; 11–17 cells), res06 big skeleton walk (8 frames, 9x11, ACCEPTABLE; legs rows 7–9 change 10–14 cells, torso swaps at f2/f6 → 24–28 cells).
- res02 big bat: 4 frames but full-width `＂` → REJECT.

**Diffs and edits.**
- bat f0→f1 (9 cells, rows 3–4): `` 3G0R .'"-`.<Esc> `` then `4G0R \    /<Esc>`. f1→f2: 14 cells (lift). f2→f3: 11.
- spider f0→f1 (3 cells, row 3 `/∞|¯\`→`(∞/<\`): `3G0f/r(` then `f|r/` then `lr<` — a `f`/`;` landmark drill.
- spider f1→f2 (4 cells): `3G0f(r<` `f/r|` `lr/` `lr>`.
- skeleton f0→f1 (2 cells, row 4 `/(`→`(V`): `4G3|R(V<Esc>`. f1→f2: `4G3|R<|<Esc>`. f2→f3: `4G3|r/`.
- ghost f0→f1 (8 cells): `3G0R^´<Esc>` then `` 3G6|R`^<Esc> `` then `4G3|r)` `4G5|r/` then `5G3|R'-<Esc>`.
- big skeleton f3→f4 (10 cells, legs only): rows 7–9 replaced with `R`.

Frames (small bat, 4x8, IDEAL, ASCII only):
```


   ,,
  ,"-\
  |, |;

   ,,
 .'"-`.
 \    /
 _    __
 `\,,/.'
   "-'


 \_,,_/.
  `"-`'

```

Frames (small spider, 3x7, IDEAL; row 1 blank):
```

   ,-,
 /∞|¯\

   ,-,
 (∞/<\

   ,-,
 <∞|/>

   ,-,
 /∞(|)

   ,-,
 |∞<(|

   ,-,
 /∞|<\
```

Frames (small skeleton, 4x4, IDEAL; row 1 blank):
```

 _{)
''¯)
  /(

 _{)
''¯)
  (V

 _{)
''¯)
  <|

 _{)
''¯)
  /|
```

Frames (ghost, 5x7, IDEAL):
```
  .-.
 (* *)
-' ° '-
  \ (_,
   `-'

  .-.
 (* *)
^´ ° `^
  ) /_,
  '--'

  .-.
 (* *)
-' ° '-
  ) /,
 '--'

  .-.
 (* *)
^´ ° `^
  ) /
 '-'

  .-.
 (* *)
-' ° '-
  \ (
  '-'

  .-.
 (* *)
^´ ° `^
  \ (,
   `-'
```

Frames (big skeleton walk f0, f1 legs, 9x11, ACCEPTABLE):
```
    __
   ,o_)
   "':_
  _.-/)\
 "`,-´_/
  '"   ;
      /¯
    ,-`\
       ,/

    __
   ,o_)
   "':_
  _.-/)\
 "`,-´_/
  '"   ;
      `/
      / \
    ,-' ,/
```

**Tutor fit.**
- Small bat → **M4 Rotation tween** (3 content rows exactly like M4; wing extremes down f0 / up f2 with level midpoint f1). Pure ASCII.
- Small spider → **M12 Joint sweep** or M1 Contour run (one row of legs, landmark hops `f/`, `f|`, `;`), `∞` is typed once and never edited.
- Small skeleton → M11 Fixed-width redraw (`R` of 1–2 leg cells) — very small.
- Ghost → M2 Face focus/M13 (stable face `(* *)`, arms + tail change).
- Big skeleton → MAYBE M8 Walk study (real leg cycle, 9 rows).

**Verdict: USE** — small bat res01 → **M4** (edit f0→f1 `` 3G0R .'"-`.<Esc> `` + `4G0R \    /<Esc>`); small spider res03 → **USE M12** (`3G0f/r(` `f|r/` `lr<`); ghost res07 → USE M2/M13; small skeleton res05 → MAYBE M11; big skeleton res06 → MAYBE M8; big spider/big ghost → MAYBE; big bat res02 → REJECT (full-width `＂`).

## official-Cosmetics/MushroomHead

- Sheets viewed (7/7): res01 idle, res02–res07 jump (stateTime/2 = 0..5).
- Source: `~/Downloads/stone-story-official/Cosmetics/MushroomHead.txt` (PetFrog template; replaces the player with a mushroom). Body block at `>o@myX+10@,@myZ-3@`; eyes printed as text `@LeftEye@ @RightEye@` at `myX+14` on the stem row (row offset follows the body each frame), brows `\ /` in red one row above when an item is active.
- Non-ASCII: `─ ¯ ´` (Ambiguous). Alternate eye glyphs by item: `❤ ❄ φ ∞` — `❤ ❄` are often emoji/wide → exclude those variants.

**What it depicts / true sequences.** A mushroom-cap character hops: idle (res01, squashed base `|_─_|` + `¯` drip) → jump 12 ticks, 2 ticks per block: res02 rise (base `'───'`) → res03 higher → res04 apex → res05 apex with base flipped `'¯¯¯'` → res06 descend (squash base again) → res07 lower. Canvas 9x9 (content 6x9) → ACCEPTABLE (9 rows); crop to content per frame is 6x9 IDEAL but then the vertical travel is lost.

**Diffs.** Body translates one row per frame (26–30 raw cells, but = one `dd`/`O`), base changes at res01→res02 and res05→res06; **res04→res05: 3 cells** (row 6 `───`→`¯¯¯`).

**Edits.**
- res04→res05: `:6s/───/¯¯¯/` (or `6G5|3r¯` — `¯` is digraph `<C-k>'m`).
- res01→res02 (rise + unsquash): `ggdd` then `6G0R   | ─ |<Esc>` then `7G0R   '───'<Esc>` then `Go<Esc>`.
- eye swap (M2): `:4s/o o/* */` (aether variant).

Frames (with eye text composited; res01 idle, res02 rise, res04 apex, res05 apex-flip; 9x9 canvas):
```



    .^.
   /.'.\
  (' " ')
  `|o o|´
   |_─_|
     ¯


    .^.
   /.'.\
  (' " ')
  `|o o|´
   | ─ |
   '───'

    .^.
   /.'.\
  (' " ')
  `|o o|´
   | ─ |
   '───'



    .^.
   /.'.\
  (' " ')
  `|o o|´
   | ─ |
   '¯¯¯'



```

**Tutor fit.** Another PetFrog-template hop (same family as Party cake): translate + base squash. Useful for M9 Bounce capstone as a second example, and the 3-cell apex flip `───`→`¯¯¯` is a clean M11 `R`/`:s` edit. The eye-glyph swap (`o`→`*`/`∞`) is an M2 idea but the item variants use emoji-width glyphs.

**Verdict: MAYBE** — M9 Bounce (edit res04→res05 `:6s/───/¯¯¯/`; idle→rise `ggdd` + two `R` rows). Weaker than FrogJump (translate-only in-between frames).

## official-Pets/Frog

- Sheets viewed (7 listed + res02–res07 unlisted = 13/13): res01 idle, res02 happy face layer, res03/res04 look layers, res05–res07 blink layers, res08–res13 jump.
- Source: `~/Downloads/stone-story-official/Pets/Frog.txt` (the PetFrog template by StandardCombo that Skully, Party cake, MushroomHead, Snake copy). Face layers drawn at `x = myX+5, y = myZ+2` over the idle body.
- Non-ASCII: `´ ·` in the body, `‾` in jump frames (Ambiguous; single in Menlo). Face layers are pure ASCII.

**What it depicts / true sequences.**
- **Blink** (idle, stateTime % 50): 44–45 `,--` (shut) → 46–47 `,=-` → 48–49 `,O-` → back to `,Oo` for 44 ticks. Only the eye cells change. Content 3x9 → **IDEAL**.
- **Happy** (`face = "( ^^"`): `,^^` / `'=` — 4 cells over two rows (eyes + grin).
- **Look** (`face = "°°"`): `,oO`/` *` ↔ `,Oo`/` *` on `time % 4` (2 ticks each); `*` replaces the mouth `.-`.
- **Jump** res08–res13 (stateTime/2 = 0..5, 12 ticks): same frog art as FrogJump res21 minus the apex frame (sit-shut, tuck, launch, stretch, descend, land); 5x9 → IDEAL. See FrogJump for the full 8-frame version.

**Diffs and edits (3-row content, rows numbered 1–3).**
- open → shut: 2 cells. Edit: `:1s/Oo/--/` (or `1G0f,lR--<Esc>`).
- shut → half: 1 cell. Edit: `1G0f-r=`.
- half → one-open: 1 cell. Edit: `1G0f=rO`.
- open → happy: 4 cells over 2 rows. Edit: `1G0fOR^^<Esc>` then `2G0f.R'=<Esc>`.
- open → look: 2 cells (`Oo`→`oO`, mouth `.-`→` *`): `1G0fOR oO`… precise: `1G0fOxp` swaps `Oo`→`oO` (a real `xp` teaching moment), then `2G0f.R *<Esc>`.

Frames (idle blink cycle + happy + look, 3 content rows x 9, IDEAL):
```
     ,Oo
  (\/ .-)
  ´ ·-\´\

     ,--
  (\/ .-)
  ´ ·-\´\

     ,=-
  (\/ .-)
  ´ ·-\´\

     ,O-
  (\/ .-)
  ´ ·-\´\

     ,^^
  (\/ '=)
  ´ ·-\´\

     ,oO
  (\/  *)
  ´ ·-\´\
```

**Tutor fit.** Best **M2 Face focus** candidate in the batch: stable 3-row contour, all acting inside the head, 1–4-cell edits that map to `r`, `R`, `xp`, `:s`. The blink also matches M11 (fixed-width `R`, undo/redo between states) and M0 (3 rows, readable change). Real timing (44-tick hold, 2-tick blink states) is a good "holds" example for M7.

**Verdict: USE** — blink/happy/look → **M2 Face focus** (edit `:1s/Oo/--/`, then `1G0fOxp` for the look). Jump → covered by FrogJump (USE M9).

## official-Cosmetics/SuperStoneHead

- Sheets viewed (6 listed + res01 unlisted = 7/7): res01 eyes `* *`, res02 hair/head layer, res03–res07 aura flame frames.
- Source: `~/Downloads/stone-story-official/Cosmetics/SuperStoneHead.txt` — `>h` draws on the player head; aura cycles `time / 5 % 5` (5 ticks per frame, 5 frames), each frame a different colour (yellow, cyan, yellow, blue, orange-red).
- Non-ASCII: **`｛ ｝ ［ ＂` FULLWIDTH (double width)**, `— •` (Ambiguous).

**What it depicts.** A "super saiyan" style flaming aura around the player's head, 5 flicker frames at the same origin (`>h-6,-5`; last frame `-6,-4`). Each frame 10x16–18 → ACCEPTABLE by rows/cols, but the frames are essentially redrawn each time (38, 40, 33, 15 cells change across rows 1–10) and the fullwidth braces break the fixed-width grid. No clean crop keeps the motion.

**Diffs.** Consecutive aura frames: large, whole-shape changes (not a bounded edit). Eyes/hair layers are stills.

**Verdict: REJECT** — full-width glyphs `｛｝［＂` (unsafe in a fixed-width buffer) and whole-frame redraws with no teachable 1–6-cell step.

## official-Foes/PallasCrown

- Sheets viewed (5 listed + res06, res07 unlisted = 7/7): res01 leftBooo1, res02 leftBooo2, res03 rightBooo1, res04 rightBooo2, res05 crownBase, res06 crownJewels, res07 crownLining.
- Source: `~/Downloads/stone-story-official/Foes/PallasCrown.txt` — two ghosts ("Booos") descend carrying Pallas's crown and sway; `DrawBooos()`: frame 1 on `time % 8 = 0`, frame 2 on `time % 5 = 0` (irregular strain rhythm), drawn `>c` at each ghost's origin; sweat drops are 2-char text layers (`°·`, `` `# ``, `#.`, `·´`) cycling on `time % 5`.
- Non-ASCII: ghosts use `‾ ´` only (Ambiguous; single in Menlo). Crown uses `† ÷ … ∞ ☼` → unsuitable.

**What it depicts / true sequences.**
- **Left ghost res01 → res02** and **right ghost res03 → res04**: calm `(- -)` ↔ straining `(> <)` plus the tail wisp flicking (`) / | / '` → `\ / ' / !`). Left is 6x10, right 6x7 → **IDEAL**.
- res01 and res03 are hand-mirrored versions of one another (left ghost faces right, right ghost faces left) — the artist mirrored `` \ ‾ `-´ `` into `` `-´ ‾ / `` rather than character-reversing it.
- Crown (res05–res07): three stacked layers of one still object; descends/falls by translation only.

**Diffs.** res01→res02: 5 cells (r2 `-`→`>`, `-`→`<`; r4c5 `)`→`\`; r5c5 `|`→`'`; r6c5 `'`→`!`). res03→res04: 5 cells (same, mirrored columns). res01 vs res03 (mirror): every row.

**Edits.**
- calm → strain (left): `:2s/- -/> </` then `4G0f)r\` then `5G0f|r'` then `6G0f'r!`.
- M18 mirror lesson: from res01 produce res03: row 3 `` \ ‾ `-´ `` → `` `-´ ‾ / `` (`` 3G0R`-´ ‾ /<Esc> `` after dedent), rows 4–6 swap `)`↔`(`, `/`↔`\` (`:4,6s/)/(/` then `:4,6s/\//\\/`), shift left 1 col (`:%s/^ //`).

Frames (left ghost calm/strain, right ghost calm/strain):
```
    .-.
   (- -)
   \ ‾ `-´
    ) /
    |/
    '

    .-.
   (> <)
   \ ‾ `-´
    \ /
    '/
    !

   .-.
  (- -)
`-´ ‾ /
   \ (
    \|
     '

   .-.
  (> <)
`-´ ‾ /
   \ /
    \'
     !
```

**Tutor fit.** A real mirrored pair drawn by hand — ideal for **M18 Hand-mirrored return** (mirroring directional art: `(`/`)`, `/`/`\`, the `-´` accent that does *not* mirror cleanly is a good discussion point) and M19. The calm→strain swap is a 5-cell M2 Face focus edit (`:s` inside a stable contour) with an irregular hold rhythm (`%8` vs `%5`).

**Verdict: USE** — ghosts res01–res04 → **M18 Hand-mirrored return** (mirror res01→res03; frame edit `:2s/- -/> </` + 3 `r` on the tail). Crown layers → REJECT (glyphs `† ÷ … ∞ ☼`, still object).

## official-Games/FeedABat

- Sheets viewed (5 listed + res06 unlisted = 6/6): res01 bat (`Main`), res02 far pillars, res03 mid pillars, res04 near pillars, res05 floor dots, res06 candy `>(_)<`.
- Source: `~/Downloads/stone-story-official/Games/FeedABat.txt`
- Non-ASCII: bat is ASCII; pillars use `│` and **`［ ］ ｛ ｝` FULLWIDTH (double width)**.

**What it depicts.** A catch-the-candy mini-game: one static bat sprite (6x15, single pose — no second frame in the source), three parallax pillar layers (9–17 rows x 90–91 cols, one frame each; motion comes from the UI moving the layer, not from frames), a floor dot strip, and a falling candy that only translates. No same-origin frame sequence exists.

**Verdict: REJECT** — not an animation (single poses + translated layers); pillar layers are TOO-LARGE and use full-width brackets. (The three parallax layers are a conceptual M5 foreground/background example, but a 9–17 x 90 crop is not popup-sized and carries `［］｛｝`.)

## official-Hats/IroncladMask

- Sheets viewed (4/4): res01–res04.
- Source: `~/Downloads/stone-story-official/Hats/IroncladMask.txt` — four blocks all drawn every frame at `>h-5,-2` in white, gold `#C09F46`, orange `#DF7C31`, green `#008800`.
- Non-ASCII: none.

**What it depicts.** One still mask over the Stonehead, split into four colour layers (a layer composite, not a sequence). Composite 4x8.

**Verdict: REJECT** — part/colour layers of a single still; no time/state alternation. (As a colour-separation example it could illustrate M5 layer order, but it has no motion.)

## official-Cosmetics/PumpkinCarving

- Sheets viewed (3 listed + res04 unlisted = 4/4): res01 pumpkin (10x25), res02 carve-cell block glyphs (`▀ ▄ █`, 3 frames), res03 2x2 carve-brush frames (3), res04 cursor `┌┐└┘`.
- Source: `~/Downloads/stone-story-official/Cosmetics/PumpkinCarving.txt` — an interactive carving toy: the player paints block cells over a still pumpkin; candle flicker is per-cell colour, not frame art.
- Non-ASCII: `ý ζ ι … ─ │ ┊ ║ ¡ ¯ ´ ·` in the pumpkin, `▀ ▄ █ ┌ ┐ └ ┘` in the tools — all Ambiguous; `ζ ι ý` are unusual to type.

**What it depicts.** One still pumpkin (10x25, ACCEPTABLE by size) plus paint-tool glyph frames (1–2 cells). No same-origin pose sequence; the "animation" is user painting.

**Verdict: REJECT** — not an animation (still + UI brush glyphs). The pumpkin shell could serve as an M15 texture/M1 contour still, but its stem/crease glyphs (`ζ ι ý ┊ ║`) are poor typing targets.

## official-Games/GrowPlants

- Sheets viewed (3 listed + res04, res05 unlisted = 5/5): res01 title logo (15x45), res02 pot (3x9), res03 FLOWER_GROWTH (10 frames), res04 seed icon, res05 status text UI.
- Source: `~/Downloads/stone-story-official/Games/GrowPlants.txt` — `flowerText = ui.AddAnim(FLOWER_GROWTH)`; `flowerText.frame` is set from the `flowerGrowth` value (state-driven stages 0..9), drawn above the pot.
- Non-ASCII: flower uses `•` (bud, f2–f3), `ζ` (stem node, f5+), `´` (f7+) — Ambiguous; `ζ` and `•` need digraphs (`<C-k>z*`, `<C-k>Sb`). Everything else ASCII.

**What it depicts / true sequence.** A flower growing from an empty pot: f0 empty → f1 shoot `^` → f2 bud `•` on a stalk with leaves `.|,` → f3 `o` bud → f4 `O` bud, leaves `\|/` → f5 flower head `( )` opens on `ζ` → f6 petal curl `` `( `` → f7 fuller head → f8 wider → f9 full bloom with leaf `(_\|/_)`. Same origin, bottom-anchored, 8x9 → **ACCEPTABLE** (8 rows; 7-row crop loses the top of f9 only).

**Diffs.** f0→f1 1 cell; f1→f2 4; f2→f3 3; f3→f4 4; f4→f5 6; f5→f6 3; f6→f7 11; f7→f8 11; f8→f9 23. Steps f0→f6 are all 1–6 cells.

**Edits (rows 1–8).**
- f0→f1: `8Gi    ^<Esc>` (row 8 is empty in f0).
- f2→f3: `6Gi    o<Esc>` (row 6 empty) then `7G5|r|` then `8G6|r;`.
- f3→f4: `5Gi    O<Esc>` (row 5 empty) then `6G5|r|` then `8G4|r\` then `8G6|r/`.
- M6 subtractive direction (author f4 from f5): `3G5|r ` `4G4|3r ` → `4G5|` … i.e. delete the head and restore `O`.

Frames (f0 is empty; f1–f9, 8x9):
```
(f1)







    ^

(f2)






    •
   .|,

(f3)





    o
    |
   .|;

(f4)




    O
    |
    |
   \|/

(f5)


    ,
   ( )
    ζ
    |
  . | ,
   \|/

(f6)


   `(
   (()
    ζ
    |
  . | ,
   \|/

(f7)


   ,'(
  (( ,)
   `ζ´
    |
  \ | /
   \|/

(f8)


  , ',(
 `.( ),´
   `ζ´
    |
  \\|//
   \|/

(f9)
     _
    | )
.-. |/__
 `.\•/__)
   `;´
  _ | _
 (_\|/_)
   \|/
```

**Tutor fit.** A real staged build whose early steps are 1–6-cell edits and whose order is the lesson — fits **M6 Pyramid build** (subtractive authoring: draw f8, subtract back to f1; then play forward) and M7 Timed build (stages as holds). Also M16 Key-pose plan (`<C-a>` stage labels over 10 frames). Frame height 8 vs M6's 5: use f1–f6 in rows 3–8 (6 rows) for an IDEAL crop.

**Verdict: USE** — FLOWER_GROWTH res03 → **M6 Pyramid build** (edit f2→f3: `6Gi    o<Esc>` + `7G5|r|` + `8G6|r;`). Logo/pot/seed/status → REJECT (stills/UI).

## official-Cosmetics/Acrocorn

- Sheets viewed (2 listed + 19 unlisted = 21/21): res01 label, res02 rider+mount body, res03 big-head face, res04 triskelion lance, res05 horn, res06 legs idle, res07–res10 legs gallop (4), res11 arm idle, res12/res13 arm raised (item state 3), res14–res21 wand/aether effect glyphs.
- Source: `~/Downloads/stone-story-official/Cosmetics/Acrocorn.txt` — body `>o-9,-1`, horn `>o-11,1`, legs `>o-9,2`, arm `>o-2,-1`. Legs: idle when not walking; walking picks res07/08/09/10 on `time % 20` quarters (5 ticks each), hoof sound at 15 and 20.
- Non-ASCII: body `‾ ¯` (2 cells), arm `´ —`, lance `—`, `☤` in one wand frame. Legs are pure ASCII apart from `´` in res08/res09.

**What it depicts / true sequences.**
- **Gallop legs res07 → res08 → res09 → res10** (loop, 5 ticks each) under a fixed rider+mount body; idle stance res06. Legs block 2x9–2x12. Composite with body/horn/arm at the script offsets (exact from the `>o` coordinates, shifted +11,+1) = **5x16, IDEAL**.
- res11 → res12/res13: arm lowered → raised (item use); 3x7–3x9 part layer.
- res14–res21: 1–3-cell wand effects (UI-level particles).

**Diffs (legs block, rows 1–2).** res07→res08: 6 cells (front pair lifts: r1c8–11 `//  `→` |/'`, r2c8–9 `\,`→` ´`). res08→res09: 10. res09→res10: 14. res10→res07: 8. Idle res06→res07: 3 cells (`||`→`//`, `|,`→`\,`).

**Edits.**
- res06→res07 (start gallop, 3 cells): `4G5|R//<Esc>` then `5G5|r\` (rows 4–5 of the composite).
- res07→res08 (6 cells): `4G10|R |/'<Esc>` then `5G10|R ´<Esc>`.

Frames (composite, idle + 4 gallop frames, 5x16):
```
        O  ,--._
       /|\/ /\|
  ,;(‾)¯7, )  ´
 // ||   //
 '  |,   \,

        O  ,--._
       /|\/ /\|
  ,;(‾)¯7, )  ´
 // //   //
 '  \,   \,

        O  ,--._
       /|\/ /\|
  ,;(‾)¯7, )  ´
 // //    |/'
 '  \,    ´

        O  ,--._
       /|\/ /\|
  ,;(‾)¯7, )  ´
 // |/'    \\
 '  ´       \,

        O  ,--._
       /|\/ /\|
  ,;(‾)¯7, )  ´
 // \\   ||
 '   \,  |,
```

**Tutor fit.** A 4-beat quadruped gallop where only the two leg rows change and the body is a stable anchor — fits **M8 Walk study** (contact/passing, equal frame height, legs-only edits of 4–14 cells) and M12 Joint sweep (hop between leg glyphs with `f/`, `t,`, `;`). Composite legibility is modest (the mount reads as a small beast under a stick rider).

**Verdict: USE** — gallop res06–res10 (+res02/res05/res11 composite) → **M8 Walk study** (edit res07→res08: `4G10|R |/'<Esc>` + `5G10|R ´<Esc>`). Arm raise → MAYBE M3. Wand glyphs/label → REJECT.

## official-Cosmetics/TwinSuns

- Sheets viewed (2 listed + res03, res04 unlisted = 4/4): res01 sun with sunglasses, res02 sun without, res03/res04 small temple sun with/without glasses.
- Source: `~/Downloads/stone-story-official/Cosmetics/TwinSuns.txt` — `glasses` is a config boolean chosen once; res01 vs res02 are alternatives, not frames in time.
- Non-ASCII: `¡ ¯ ´` plus **`｛ ｝ ＂` FULLWIDTH (double width)** in the small second sun.

**What it depicts.** A smiling sun (9x18) wearing sunglasses (res01) or not (res02), and a tiny companion sun. Diff res01→res02: the glasses rows 4–5 (`/-._______\`, `|  |__||__|`) → blank face, plus the companion's `＂`. A clean "variant" pair, but no time/state animation, and the companion uses full-width glyphs.

**Verdict: REJECT** — not an animation (config variant) and full-width `｛｝＂`. (A crop of the big sun rows 1–9 cols 1–15 is ASCII-safe apart from `¡ ¯ ´` and would work as an M14 Variant palette still pair — noted as a MAYBE idea only.)

## official-Hats/Skully

- Sheets viewed (2 listed + res02–res07 unlisted = 8/8): res01 skull `(_o,o)` head, res02 alt ribcage `╪`, res03 boss-entry eyes `ò,ó`, res04/res05 boss-kill look `O,o`/`o,O`, res06/res07/res08 blink `=,=`/`-,-`/`=,=`.
- Source: `~/Downloads/stone-story-official/Hats/Skully.txt` — skull `>h-2,-1`, eye layers `>h0,0` (row 2, cols 3–5 of the skull); same author and timing as Pets/Skully: blink at stateTime%50 44–45 `=`, 46–47 `-`, 48–49 `=`; look alternates on `time % 4`; `ò,ó` shown while `face = "°°"` (boss entry).
- Non-ASCII: `´` (skull chin), `ò ó` (Latin-1, Ambiguous; digraphs `<C-k>o!`, `<C-k>o'`), `╪`.

**What it depicts / true sequences.** The Pets/Skully head worn as a hat: 3x6 skull + 1x3 eye layers. Frames: open `o,o` → `=,=` → `-,-` → `=,=` (blink); `O,o` ↔ `o,O` (look); `ò,ó` (angry). All 3x6 → **IDEAL** (smallest face in the batch).

**Diffs/edits (3x6).** open→blink: 2 cells `:2s/o,o/=,=/`; blink→shut: `:2s/=/-/g`; open→angry: 2 cells `2G0foRò,ó<Esc>` (digraphs); look: 2-cell swap `2G0forO` / `2G0fOro2lrO`.

Frames (3x6, IDEAL):
```
 ,--.
(_o,o)
  `"´

 ,--.
(_=,=)
  `"´

 ,--.
(_-,-)
  `"´

 ,--.
(_ò,ó)
  `"´

 ,--.
(_O,o)
  `"´
```

**Tutor fit.** Same material as Pets/Skully (M2 Face focus / M11), plus one extra acting state (`ò,ó` angry via accents), without the chest sequence. Pets/Skully is the canonical copy; this one's three eye variants suit an **M14 Variant palette** exercise (registers holding `o,o`, `=,=`, `ò,ó`).

**Verdict: USE** (duplicate family of Pets/Skully) → **M14 Variant palette** or M2 (edit `:2s/o,o/=,=/`).

## official-Pets/Snail

- Sheets viewed (2 listed + 40 unlisted = 42/42): res01–res03 mold decoration layers (3 colours of one still), res04–res07 idle (eyes/shell/spiral/body), res08/res09 happy `^^` + `meow!` body, res10 `><` (sad), res11/res12 look, res13–res15 blink, res16–res35 slime crawl (5 frames x 4 layers), res36–res42 the same face/body variants for the slime state.
- Source: `~/Downloads/stone-story-official/Pets/Snail.txt` (PetFrog template). All layers at the same origin `>o@myX@,@myZ@` in four colours (eye, shell, spiral, body). Slime state: `stateTime/3` = 0..4 (3 ticks per frame, 15-tick crawl); blink stateTime%50 44/46/48; look `time % 4`.
- Non-ASCII: body row uses `¯ ´ °` (Ambiguous; `¯` = `<C-k>'m`, `´` = `<C-k>''`). Mold layers use `╤ ≡ ┊`. Eyes/shell/spiral are ASCII.

**What it depicts / true sequences.** A 3-row snail `_ Oo` / `(@)/` / `¯¯¯"`.
- **Slime crawl** (5 frames, 3 ticks each): a bump travels backward along the foot: `¯¯¯"` → `` ¯¯`^ `` (eyes lean forward one col) → `` ¯`´" `` → `` `´¯' `` → `´¯¯"` → `¯¯¯"`. 3x5–6 → **IDEAL** (smallest walk cycle in the batch).
- **Blink**: eyes `Oo` → `O-` → `=-` → `--`… (res13–15 at 48/46/44). Happy: `^^` + `¯¯¯°<meow!` (3x10).
- Mold res01–03: a still hat in three colour layers.

**Diffs.** Crawl f0→f1: 3 cells (row 3 cols 3–4 `¯"`→`` `^ ``, eyes shift right 1); f1→f2: 4 (row 3 `` ¯¯`^ ``→`` ¯`´" ``, eyes back); f2→f3: 4; f3→f4: 3; f4→f0: 1 (`´`→`¯`). Blink: 1–2 cells.

**Edits.**
- crawl f2→f3 (row 3 `` ¯`´" `` → `` `´¯' ``): `` 3G0R`´¯'<Esc> `` (4 cells; `´`=`<C-k>''`, `¯`=`<C-k>'m`).
- crawl f4→f0: `3G0r¯` (1 cell).
- open→blink: `:1s/Oo/--/`.

Frames (idle / crawl f1–f4, 3 rows):
```
 _ Oo
(@)/
¯¯¯"

 _  Oo
(@)/
¯¯`^

 _ Oo
(@)/
¯`´"

 _ Oo
(@)/
`´¯'

 _ Oo
(@)/
´¯¯"
```

**Tutor fit.** A 3-row creature whose whole gait is a bump travelling along one baseline — an exact match for **M1 Contour run** (glyph geometry of shallow curves: `¯ ` ´ '` as heights of a line; `f`/`r` landmarks) and M13 Texture pulse. The glyphs being hard to type is the lesson cost (digraphs), but only one row changes.

**Verdict: USE** — slime crawl (res16–res35 composites) → **M1 Contour run** (edit f2→f3 `` 3G0R`´¯'<Esc> ``). Blink → MAYBE M2 (duplicates Frog). Mold → REJECT (colour layers of a still).

## official-Weapons/PsyCrusher

- Sheets viewed (2 listed + res01–res05 unlisted = 7/7): res01–res05 hand/grip fragments (1x2–1x3), res06 hammer head (7x11 with two `@HevHamSc@` text slots), res07 hammer head with impact sparks (7x16).
- Source: `~/Downloads/stone-story-official/Weapons/PsyCrusher.txt` (uses `Components/OVERHAUL`). Hammer sways `base.T % 12` (x ±1) while walking; the two slot rows cycle on `base.T % 20` (4 phases, 5 ticks each): `HevHamSc1` = `［  | ］`, `［ |  ］`, `［|   ］`, `［   |］` and `HevHamSc2` = `` │`   │ ``, `` │   `│ ``, `` │  ` │ ``, `` │ `  │ ``.
- Non-ASCII: **`［ ］` and `＂` FULLWIDTH (double width)** in the slot strings; `│ ¯ ´`.

**What it depicts.** A psychic hammer whose inner "glow" scans: one `|` and one `` ` `` move 1 cell per phase inside the head (2 cells change per frame) — conceptually a neat M17/M12 moving-landmark loop. But the slot strings wrap the scan in full-width `［ ］`, so the rendered rows are 2 cells wider than the head and misalign in any fixed-width buffer. Grip fragments are part layers.

**Verdict: REJECT** — full-width `［］` inside the animated rows (would need ASCII `[ ]` substitution; with that substitution it becomes a MAYBE for M17 Coherent anchors: `f|` + `xp`/`r` per phase). Grip pieces: part layers only.

## Summary

Counts: **USE 12**, **MAYBE 4**, **REJECT 6** (22 sets; every sheet in each set directory opened, including sheets absent from `animation-frame-paths.txt`).

| set | frames | size | verdict | best module | proposed edit |
|---|---|---|---|---|---|
| official-Pets/Skully | blink/look 5 (res01+02..06); chest rise 4; wing flap 6 | 3x10; 6x11; 6x10 | USE | M2 Face focus (also M11; chest → M5, wings → M4 MAYBE) | `:2s/o,o/=,=/` |
| official-Pets/Panda | walk 14 side + 14 front; eye layer 4 | 9x30–33 | MAYBE | M8 Walk study (study only) | res01→res02 `6G23\|r\` + `7GA\|_)<Esc>` + `8G22\|D` |
| official-Games/FrogJump | frog jump 8 (res21[+res22]); JumpArrow 6; river 10 | 5x9; 9x17; 14x100 | USE | M9 Bounce capstone (JumpArrow → M6 MAYBE) | f3→f4 `1G$ro` + `` 3G0R-´-`<Esc> `` + `4G0D` |
| official-Games/BurgerRush | helper 3 (res09–11); burger stack 6 | 7x14; 7x12 | USE | M3 Pose copy (stack → M6 MAYBE) | res09→res10 `4G3\|R\  <Esc>` |
| official-Cosmetics/CaveParty | backflip 10 (res01); lava 4; stick guy 3 poses | 6x5; 3x17; 3x7 | USE | M4 Rotation tween (lava → M13) | f3→f4 `2Gi ))<Esc>` + `3G2\|R_\¯ <Esc>` + `4Gi   o<Esc>` |
| official-Cosmetics/Party | cake hop 3 distinct (res09–15); balloon string 4 | 6x9; 6x6 | MAYBE | M9 Bounce (string → M0) | idle→squash `5,6d` + `ggO<Esc>` + `Go'──___──'<Esc>` |
| official-Games/WhackaMole | mole pop 10 (res09) | 5x6 | MAYBE | M6 Pyramid build | f1→f2 `ggdd` + `3Go :>•<:<Esc>` |
| official-Pets/Snake | tongue 4 (res01+04..06); slither 9 (res07–15) | 3x15 crop; 6x14 | USE | M0 Spark loop (slither → M8) | `2GA-<Esc>` then `A<<Esc>` |
| official-Cosmetics/StoneHeadless | small bat 4; small spider 6; ghost 6; skeleton 4; big skeleton 8 | 4x8; 3x7; 5x7; 4x4; 9x11 | USE | M4 Rotation tween (spider → M12, ghost → M2) | bat f0→f1 `` 3G0R .'"-`.<Esc> `` + `4G0R \    /<Esc>` |
| official-Cosmetics/MushroomHead | hop 7 (res01–07) | 9x9 (content 6x9) | MAYBE | M9 Bounce | res04→res05 `:6s/───/¯¯¯/` |
| official-Pets/Frog | blink 4 + happy + look (res01+02..07); jump 6 | 3x9 content; 5x9 | USE | M2 Face focus | `:1s/Oo/--/`, look `1G0fOxp` |
| official-Cosmetics/SuperStoneHead | aura 5 | 10x16–18 | REJECT | — (full-width `｛｝［＂`, whole redraws) | — |
| official-Foes/PallasCrown | left ghost 2, right ghost 2 (mirrored) | 6x10; 6x7 | USE | M18 Hand-mirrored return | `:2s/- -/> </` + `4G0f)r\` `5G0f\|r'` `6G0f'r!` |
| official-Games/FeedABat | none (stills + parallax layers) | 6x15; 9–17x90 | REJECT | — (not an animation, full-width) | — |
| official-Hats/IroncladMask | 1 still in 4 colour layers | 4x8 | REJECT | — (colour layers of a still) | — |
| official-Cosmetics/PumpkinCarving | still + brush glyphs | 10x25 | REJECT | — (not an animation) | — |
| official-Games/GrowPlants | flower growth 10 (res03) | 8x9 | USE | M6 Pyramid build (also M7/M16) | f2→f3 `6Gi    o<Esc>` + `7G5\|r\|` + `8G6\|r;` |
| official-Cosmetics/Acrocorn | gallop 4 + idle (res06–10 + body composite) | 5x16 | USE | M8 Walk study (also M12) | res07→res08 `4G10\|R \|/'<Esc>` + `5G10\|R ´<Esc>` |
| official-Cosmetics/TwinSuns | 2 config variants | 9x18 | REJECT | — (variant, full-width) | — |
| official-Hats/Skully | blink/look/angry 6 (res01+03..08) | 3x6 | USE | M14 Variant palette / M2 | `:2s/o,o/=,=/` |
| official-Pets/Snail | slime crawl 5 (composites res16–35); blink 3 | 3x5–6 | USE | M1 Contour run (also M13) | f2→f3 `` 3G0R`´¯'<Esc> `` |
| official-Weapons/PsyCrusher | glow scan 4 (text slots) | 7x11 (+2 full-width) | REJECT | — (full-width `［］`; ASCII-substituted → MAYBE M17) | — |

Notes for the generator owner:
- Four PetFrog-template pets share one timing grammar (idle blink at stateTime%50 44/46/48, look on `time%4`, jump `stateTime/2` 0..5): Frog, Pets/Skully, Snake, Snail (and Party cake, MushroomHead). Their face layers are the most reliable small, same-origin frame sets.
- Composite frames above apply layers at the script's own `>o`/`>h` offsets; the two places where alignment is inferred rather than exact are marked (BurgerRush stack, Party balloon).
- Glyph risk tiers: FULLWIDTH (`｛｝［］＂`) → reject; Ambiguous-but-single in Menlo (`´ ¯ ‾ · ¡ ° … • ─ │ ╪ ≡ ∞ ζ`) → usable but needs digraphs and an `ambiwidth=single` assumption.
