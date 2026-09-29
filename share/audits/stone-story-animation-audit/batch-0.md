# Stone Story animation audit — batch-0 — 2026-09-28 — auditor: subagent batch-0 (manual view of every listed sheet)

Base: `~/Downloads/stone-story-consolidated/`. Sources: `~/Downloads/stone-story-official/<Category>/<Name>.txt`.
Frames shown with `#` converted to spaces and rows right-trimmed. Sizes are rows x max cols counted in code points
(a fullwidth glyph occupies 2 display cells, so its real display width is larger; this is called out per set).
Width classes are from Python `unicodedata.east_asian_width`: W/F = wide (unsafe in a fixed-width buffer), A = ambiguous
(single-width in most mono fonts with `ambiwidth=single`; noted, OK), N/Na = narrow.
Cell diffs were computed by a script (row/col, 1-based, after `#`->space); the verdicts and edits are manual.

## official-Cosmetics/Mech

Sheets viewed: res01–res52 (all 52 opened).
Source: `~/Downloads/stone-story-official/Cosmetics/Mech.txt` (by EdisniDaed).

1. Depicts a bipedal mech suit worn by the player. Blocks: res01 `MechIdle`; res02–res09 `MechWlkR` array (8-frame
   walk cycle), drawn at `>o-9,-5` with index `time/4 % 8` (`time/2` when holding triskelion). res10–res12 repeating-
   crossbow gunner (body + gun + ammo layers). res13–res24 crossbow R/L state 1–3 (body layer + weapon layer pairs).
   res25–res26 Blade of a Fallen God (body at `-13,-5` + blade layer at `-9,-5`). res27–res38 sword R/L state 1–3
   (body + weapon pairs). res39–res40 shield (body + shield). res41–res52 wand R/L state 1–3 (body + wand pairs).
   Only the walk cycle is a true time-driven sequence at one origin. The weapon states are driven by `item.*.state`
   (attack wind-up/strike/recover), each a body-part layer plus a weapon layer; they are not full poses.
   res01 and res02 and res06 are cell-identical (idle = walk contact frame). True distinct walk frames: 7
   (res02=res06, res03, res04, res05, res07, res08, res09).
2. Sizes: walk frames 12x19 (code points) — TOO-LARGE for the popup height. Clean crop: legs rows 8–12 (5 rows x 16
   cols) holds all walk change; every diff falls in rows 8–12. Weapon layers 1–9 rows, 5–29 cols, all fragments.
   Glyphs: fullwidth `［ ］ ｛ ｝` (F) and `《 》` (W) in every body frame — UNSAFE, each renders 2 cells and shifts
   the row. Ambiguous-but-OK: `‾ • ´ ¤ ≡ í Í Ì ì ° │ ║ ═ ╬ ─ ┘` (box-drawing is double-width under `ambiwidth=double`).
3. Walk diffs (script-counted cells): 02->03 16; 03->04 12; 04->05 18; 05->06 19; 06->07 16; 07->08 15; 08->09 11;
   09->02 14. Every consecutive pair changes 11–19 cells over 4–5 rows: above the 1–6 cell beginner bound. Smallest
   pair 08->09 (left leg straightens: knee `\`->`|`, foot drops a row). Edit sketch for 08->09 on the crop:
   `2G0f/r•` then `3G0f\r|;r|` then foot row: `4G0R  | |<Esc>` + `5G0R  (_/}<Esc>` — about 10 cells, too many for M8's
   one-feature budget.
4. Tutor fit: M8 Walk study (5-row frames, contact + passing) is the only module shaped like this, via the leg crop,
   and only after replacing `｛ ｝` with `{ }` and `］U［` with `]U[` (changes the art).
5. Verdict: MAYBE (M8 reference sequence, leg crop, glyph substitution required; diffs are too large for a single
   graded edit, usable as a "watch the cycle" example). Weapon states: REJECT (part layers).

Leg crop (rows 8–12, first 3 cols removed), original glyphs, order = playback order:

```
res02 (=res06, contact)
 /  /］U［\  \_.'
‾  / / \ \
  í Í   Ì ì
  | |   | |
 (_/｝   ｛\_)
res03
 /  /］U［‾) \_.'
‾  / /  \ \
  í Í   | /
  | |   ｛\_)
 (_/｝
res04
 /  /］U［‾`•\_.'
‾  / /  `• |
  í Í   | \
  | |    ｛\_)
 (_/｝
res05
 /  /］U［‾• \_.'
‾  / /  \ \
  í Í    \ Ì
  | |    | \
 (_/｝    ｛\_)
res07
 / •‾］U［\  \_.'
‾ / /  \ \
  \ |   Ì ì
 (_/｝   | |
        ｛\_)
res08
 /  /］U［\  \_.'
‾  / / \ \
   \ \  Ì ì
  (_/｝  | |
        ｛\_)
res09
 /  /］U［\  \_.'
‾  • / \ \
   | |  Ì ì
   | |  | |
  (_/｝  ｛\_)
```

## official-Pets/LegsTurkey

Sheets viewed: listed res03–res28, res32; also opened the unlisted res01, res02, res29–res31, res33–res37 because the
listed legs frames are drawn under them (all 37 opened).
Source: `~/Downloads/stone-story-official/Pets/LegsTurkey.txt` (by link2_thepast).

1. Depicts a turkey body on two long stick legs that follows the player. State machine SITTING -> STAND_UP ->
   STANDING -> WALK_L/WALK_R alternating -> SIT_DOWN, 1 tick per frame. Legs are their own layer at `(lx, ly) =
   (tx+3, ty+3)`; body res31 + highlights res32 + hat res33 + beak res34 + eye res36 (open) / res35 (blink, 5 ticks
   every 115) are drawn at `(tx, ty)` after the legs.
   - STAND_UP frm 0–3: res01 `<<`, res02, res03, res04 (legs 1, 2, 4, 6 rows); body rises `ty` -1,-1,-2,-2, so the
     feet stay on the ground row (bottom-anchored).
   - STANDING: res05 (== res04 == res06 == res16 == res27).
   - WALK_L frm 0–14: res06, 07, 08, res09 held frm 3–5, res10, 11, res12 held frm 8–10, 13, 14, 15, 16 (11 distinct
     frames; 15 ticks). Body `tx` advances +1/+2/+2/+1 on frm 6/7/8/12, legs `lx += 6` after the cycle.
   - WALK_R frm 0–14: res17–res27 same structure, mirrored lead leg.
   - SIT_DOWN frm 0–2: res28 (4 rows), res29 (2), res30 (1); frm 3 draws body only.
2. Sizes: legs frames 6x8 max (IDEAL). Composite turkey standing 9x7 (ACCEPTABLE); sitting 4x7; stand-up
   composites 4/5/7/9 rows x 7 (bottom-anchored, so pad above for equal height). Glyphs: `• ´ ≈ ° ≥` ambiguous (OK),
   `◘` U+25D8 and `¯` U+00AF narrow. No wide glyphs. Typing `° ¯ ≥ ◘ ≈` needs digraphs; an edit lesson should only
   touch ASCII cells.
3. Diffs.
   - Stand-up / sit-down (composite, top-aligned): each step only inserts or deletes whole `   ||` rows under the
     body. sit -> frm0: `4GA<<<Esc>` (2 cells). frm0 -> frm1: `4G$r|hr|` + `o   <<<Esc>` (4 cells). frm1 -> frm2 and
     frm2 -> STANDING: `5GO   ||<Esc>.` (the dot repeats the whole open-line insert; +2 rows each). Reverse
     (SIT_DOWN): STANDING -> res28: `5G2dd`; res28 -> res29: `.`; res29 -> res30: `5Gdd` + `4G$hR<<<Esc>`.
   - Walk legs (script-counted cells, WALK_L): 05->06 0; 06->07 7; 07->08 10; 08->09 11; 09->10 1; 10->11 14;
     11->12 15; 12->13 10; 13->14 11; 14->15 5; 15->16 3. WALK_R: 17->18 7; 18->19 9; 19->20 11; 20->21 13;
     21->22 15; 22->23 14; 23->24 12; 24->25 10; 25->26 8; 26->27 5.
     Teachable pairs: res09->res10 (1 cell, toe flick `´`: `1G$a´` needs a digraph — use as a hold/accent example);
     res15->res16 (3 cells, trailing leg closes: `4G$r|` `5GA|<Esc>` `6GA<<Esc>`); res14->res15 (5 cells) and
     res26->res27 (5 cells, `4G$r|` `5G6|R |<Esc>` `6G6|R <<Esc>` approx.); res06->res07 (7 cells, lead knee bends:
     `3G0r:` `4G0R \<Esc>` `5G0R |\<Esc>` `6G0R <<<Esc>`).
   - Blink: res36 -> res35 is 1 cell on the composite (row 2 col 6 `°` -> `¯`, `2G6|r¯` with digraph `<C-k>'m`).
4. Tutor fit: M7 Timed build (holds + dot repeat): the stand-up is literally "open a leg row, then `.`" and the source
   holds res09/res12 for 3 ticks each. M6 Pyramid build: SIT_DOWN is subtractive (`5G2dd`, `.`) and playback order
   matters (the source plays stand-up forward and sit-down as the reverse). M8 Walk study: the legs cycle has equal
   6-row height, clear contact (res06/res16) and passing (res11/res12) positions.
5. Verdict: USE. Best slot M7 (stand-up `O   ||<Esc>` + `.`; 1–4 row inserts, 2–4 cells per step), second M6
   (sit-down `2dd` + `.`), third M8 (legs-only walk; frame diffs mostly 7–15 cells, so use res14->res15->res16 as
   the graded edits).

Composite stand-up (bottom-anchored in the game; shown top-aligned, as a tutor buffer would hold it):

```
sit (SITTING)
 _  _◘_
(≈`.;°≥
 •,;_)
  ´
frm0 (res01 legs)
 _  _◘_
(≈`.;°≥
 •,;_)
  ´<<
frm1 (res02 legs)
 _  _◘_
(≈`.;°≥
 •,;_)
  ´||
   <<
frm2 (res03 legs; SIT_DOWN res28 is identical)
 _  _◘_
(≈`.;°≥
 •,;_)
  ´||
   ||
   ||
   <<
STANDING (res05 legs)
 _  _◘_
(≈`.;°≥
 •,;_)
  ´||
   ||
   ||
   ||
   ||
   <<
```

WALK_L legs (6x8, `lx` fixed during the cycle), playback order:

```
res06   res07   res08   res09(x3)   res10     res11
||      ||      :|       \           \´          \´
||      ||       \       |\          |\         / \
||      :|       |\      | \         | \       ;   \
||       \       | \     |  \        |  \      |    :
||       |\      |  <    |   \       |   \     |    |
<<       <<      <       <    <      <    <    <    <
res12(x3)   res13     res14      res15      res16
     \´          \;         ||         ||         ||
    / :          /:         |;         ||         ||
   /  |         / |         |          ||         ||
  /   |        /  |        /|          |;         ||
 /    |       <   |       < |          |          ||
 <    <           <         <          <          <<
```

## official-Pets/FoesNoMore

Sheets viewed: listed res01–res12, res21–res25, res27–res29; also opened unlisted res13–res20 and res26 (snek wings,
body and skeletimmy stand layers) (all 29 opened). res21, res22, res24, res25, res27, res28, res29 are multi-frame
`ui.AddAnim` strings with `%%` frame separators; they were split and each frame viewed.
Source: `~/Downloads/stone-story-official/Pets/FoesNoMore.txt` (by Malathor).

1. Depicts former foes following the player:
   - Flying serpent ("snek"): head res01–res12 at `(-8,-5)`; `SnekHeadFrame` += 1 every 3 ticks; frames < 20 show
     res01, frames 20–30 show res02..res12 (tongue flick, 33 ticks), then wraps. Wings res13/res14 at `(-14,-4)`
     alternate every 3 ticks. Body res15–res20 at `(-19,-2)` cycle every 2 ticks. Three layers, three clocks.
   - res21 ant walk (3 frames, 12-tick loop), res22 cultist walk (5 frames, 15-tick loop), res23 ice-elemental beam
     (60-col strips), res24 ice guy (10 frames, eye-only change, 40-tick loop), res25 skeletimmy walk (3 frames,
     15-tick loop) + res26 stand, res27 scout walk (7 frames, 42-tick loop), res28 blast sparkle (49 frames, mostly
     empty), res29 wasp fly-in/fly-away (22 frames, sprite translating diagonally).
2. Sizes: snek head 4x7 (IDEAL); snek composite 6x13 (IDEAL); cultist 5x7 (IDEAL); ice guy 3x6 (IDEAL);
   skeletimmy 3x4 (IDEAL); ant 2x8 (IDEAL, very thin); scout 9x11 (ACCEPTABLE, legs-only crop rows 7–9 = 3x9);
   res23 ~6x60 (TOO-LARGE, no crop); res29 translating over 22x~24 (TOO-LARGE as a canvas, sprite 4x8).
   Glyphs: `´ · ¡ ─ ═ └ •` ambiguous (OK), `¯` narrow. No wide glyphs. `´ ¯` need digraphs to type.
3. Diffs (script-counted cells):
   - Snek head: 01->02 1, 02->03 1, 03->04 1, 04->05 1, 05->06 4, 06->07 4, 07->08 1, 08->09 3, 09->10 3, 10->11 2,
     11->12 1, 12->01 1. Edits: 01->02 `2GA-<Esc>`; 02->03 `.`; 03->04 `2G$r<`; 04->05 `2G$r,`; 10->11 `2G$xr,`;
     11->12 `r.`; 12->01 `x`. All on row 2, cols 6–7.
   - Ice guy (res24): f1->f2 1 (`3G3|r.`), f2->f3 1 (`•`), f3->f4 1 (`3G3|rO`), f5->f6 1 (`3G3|r-`), then back to `o`.
   - Cultist (res22): f1->f2 4, f2->f3 6, f3->f4 2, f4->f5 6, f5->f1 4. f3->f4 is pure ASCII: `4G0r/j0r``.
     f1->f2: `4G0r(` + `5G0R ´¯¯¯<Esc>` (3 cells changed, needs digraphs).
   - Skeletimmy (res25): f1->f2 2 (`3G3|R(V<Esc>`), f2->f3 2 (`3G3|R<|<Esc>`).
   - Ant (res21): 5, 4, 4 cells, all on row 2 (`2G3|R/`/|-<Esc>` for f1->f2).
   - Scout (res27): 8, 9, 8, 9, 7, 6, 10 cells, all in rows 7–9 (legs).
   - Snek body (res15–20): 6, 6, 11, 12, 6, 12 cells.
4. Tutor fit: M2 Face focus (4-row head, stable contour, edits `A`, `.`, `r`, `x` on one feature) or M11 Fixed-width
   redraw (R/r then `u`/`<C-r>` to scrub the flick) for the snek head. M0 Spark loop (3 rows, one readable change)
   for the ice guy's eye. M8 Walk study for the cultist (5 rows, equal height, 5-frame cycle, 2–6 cell steps).
   M1/M12 for skeletimmy (`f/` or `t(` landing then `R`). M5 Layered scene could use the snek composite (head over
   body, wings over body) but the three clocks make it an advanced example.
5. Verdict: USE. Best slot M2 (snek head tongue flick, 1-cell steps); also USE cultist walk for M8 and ice guy for
   M0; MAYBE snek composite for M5, scout legs for M8, skeletimmy for M12, ant for M13. REJECT res23 (too large,
   beam strips), res28 (sparkle mostly empty frames), res29 (translation, not a pose change).

Snek head tongue flick (res01 is the idle; flick plays res02..res12, 3 ticks each):

```
res01  res02   res03    res04    res05    res06
 .-.    .-.     .-.      .-.      .-.      .-.
((`-'  ((`-'-  ((`-'--  ((`-'-<  ((`-'-,  ((`-',
 \\     \\      \\       \\       \\       \   ´
 _))    _))     _))      _))      _))      _))
res07    res08    res09    res10    res11   res12
 .-.      .-.      .-.  ,   .-.      .-.     .-.
((`-'-,  ((`-'-´  ((`-'´   ((`-'-´  ((`-',  ((`-'.
 \\       \\       \\       \\       \\      \\
 _))      _))      _))      _))      _))     _))
```

Snek composite (body res15 or res18, wings res13 or res14, head res01):

```
         .-.                 .-.
  (\ |  ((`-'               ((`-'
  ( \|   \\           `-._:´ \\
   .´ `-._))           .´ `-._))
 .'´ ¯ `--´          .'´ ¯ `--´
(_                   (_
```

Cultist walk (res22, 5 frames, 3 ticks each):

```
f1       f2       f3        f4        f5
,_       ,_       ,_        ,_        ,_
{\\      {\\      {\\       {\\       {\\
( `\     ( `\     ( `\      ( `\      ( `\
/`o'._   (`o'._   (`o`-._   /`o`-._   /`o'.__
`¯¯'¯     ´¯¯¯     ¯¯¯¯¯    `¯¯¯¯¯    ¯¯´¯¯
```

Ice guy (res24; f5 = f4, f7 = f6, f8–f10 = f1):

```
f1       f2       f3       f4       f6
  /|       /|       /|       /|       /|
`/| \,   `/| \,   `/| \,   `/| \,   `/| \,
 \o_/     \._/     \•_/     \O_/     \-_/
```

Skeletimmy walk (res25) and stand (res26); ant walk (res21):

```
f1     f2     f3     stand
 _{)    _{)    _{)   {)
''¯)   ''¯)   ''¯)   //\
  /(     (V     <|    / \
f1         f2         f3
-, _,-.    -, _,-.    -, _,-.
 O'|\-\`    O/`/|-`    O(`|-)`
```

Scout walk (res27, full f1 then legs rows 7–9 of all 7 frames, 6 ticks each):

```
      /
   ),_ ____
   `o/(  -´
  ,/_\ );
  /  /\´
 / -´ _)_
└    /  /
    ;  (
   /    \
f1          f2          f3          f4          f5          f6          f7
└    /  /   └    / .´   └    /.-´   └    (.'´   └    ( .´   └    / .´   └    / .´
    ;  (        ( (_         ¡           /\           /-,        `¡,         \(
   /    \        \  '        '\         ´  \         /            |          ´ \
```


## official-Pets/Mushroom

Sheets viewed: listed res01–res17, res20; also opened unlisted res18, res19 (both a single `#`, i.e. empty
"hide" blocks) (all 20 opened).
Source: `~/Downloads/stone-story-official/Pets/Mushroom.txt` (by Pyro).

1. Depicts a small mushroom pet with a `•w•` face that hops beside the player. `MushroomFrame` += 1 every 3 ticks,
   res01..res12 while walking (12-frame hop, 36 ticks), pinned to res01 when not walking. All frames share one draw
   origin `(-14,-2)`; vertical travel is done with leading blank rows (res06/res07 apex has 0, res11/res12 landing
   has 5), horizontal lean by leading spaces. Boss fights: `Mushroom` becomes empty res18 and `Mushscared` shows
   res13 (`-w-`), res14 (`'OwO`), res16 (`＂OwO`, overrides res15 at frame 3), res17 (`'•w•`, frame 7); empty res19
   after. Boss killed: res20 (`^w^`) for 9 steps. res15/res16 contain fullwidth `＂` U+FF02 (WIDE, unsafe).
2. Sizes: face frames 5x8 content (IDEAL; the 3 leading blank rows are canvas padding). Hop canvas 9 rows x 11 cols
   (ACCEPTABLE). Glyphs: `¯` narrow, `• ´` ambiguous (OK), `＂` wide in res15/res16 only (REJECT those two).
3. Diffs (script-counted cells, full canvas):
   - Hop: 01->02 8 (squash: base row becomes `'------'`, one row: `8G0R'------'<Esc>`); 02->03 4 (anticipation:
     eyes `>w<`, feet `´ `` : `7G0f•r>2lr<` needs a digraph for `•` as a target, or `:7s/•w•/>w</`, plus `8G0r´$r``);
     03->04 42, 04->05 37, 05->06 40, 07->08 40, 08->09 39, 09->10 40, 10->11 38, 12->01 36 (whole sprite moves:
     in Vim this is `ggO<Esc>` / `ggdd` plus shape edits, not a cell edit); 06->07 10 (apex: face drops one row,
     `3G` row returns to `|¯¯¯¯|`, `4G` gets `>w<`, bottom `'--'` -> `¯¯¯¯`); 11->12 6 (landing: `9G0R '----'<Esc>`).
   - Faces (content rows 1–5): res01->res13 6 (eyes `-w-` + base `'----'`); res13->res14 3 (`4G0f-hR'OwO<Esc>`,
     or `:4s/ -w-/'OwO/`); res13->res17 3; res13->res20 2 (`:4s/-w-/^w^/` or `4Gf-r^;r^`, pure ASCII).
4. Tutor fit: M2 Face focus — a stable cap contour with the expression the only thing that changes; res13 -> res20
   (`4Gf-r^;r^`) and res13 -> res14 are 2–3 cell ASCII edits inside `| ... |`. M14 Variant palette — the four
   expressions (`-w-`, `'OwO`, `'•w•`, `^w^`) are ideal register variants (`"ayiW` style yanks of the face row).
   M9 Bounce capstone — the hop has real squash (res02, res12), anticipation (res03), stretch (res04–res06) and apex
   (res07), but the frames are 9 rows tall and most steps are whole-sprite moves.
5. Verdict: USE. Best slot M2 (expression swaps, 2–3 cells, ASCII-only for res13/res14/res20). Second M14.
   Hop cycle: MAYBE for M9 (reference keyframes; too many cells per step to grade). res15/res16: REJECT (wide `＂`).

Face frames (content rows only):

```
res01 idle   res13 scared1   res14 scared2   res16 (wide)   res17 scared7   res20 win
  .--.         .--.            .--.            .--.           .--.            .--.
.'  '_'.     .'  '_'.        .'  '_'.        .'  '_'.       .'  '_'.        .'  '_'.
 |¯¯¯¯|       |¯¯¯¯|          |¯¯¯¯|          |¯¯¯¯|         |¯¯¯¯|          |¯¯¯¯|
 | •w•|       | -w-|          |'OwO|          |＂OwO|         |'•w•|          | ^w^|
 '____'       '----'          '----'          '----'         '----'          '----'
```

Hop cycle (full canvas, top-aligned at the draw origin, 3 ticks per frame):

```
01        02        03        04         05          06
                                                          .--.
                                             .--.       .'  '_'.
                                 .--.      .'  '_'.      |¯>w<|
  .--.      .--.      .--.     .'  '_'.     |¯>w<|       |    |
.'  '_'.  .'  '_'.  .'  '_'.    |¯>w<|      |    |       .    .
 |¯¯¯¯|    |¯¯¯¯|    |¯¯¯¯|     |    |      .    .        '--'
 | •w•|    | •w•|    | >w<|     ,____,       '--'
 '____'   '------'  ´------`
07           08          09          10         11        12
     .--.
   .'  '_'.      .--.
    |¯¯¯¯|     .'  '_'.      .--.
    | >w<|      |¯¯¯¯|     .'  '_'.     .--.
    .    .      |    |      |¯¯¯¯|    .'  '_'.    .--.      .--.
     ¯¯¯¯       . •w•.      |    |     |¯¯¯¯|   .'  '_'.  .'  '_'.
                 ¯¯¯¯       . •w•.     | •w•|    |¯¯¯¯|    |¯¯¯¯|
                             ¯¯¯¯      '____'    | •w•|    | •w•|
                                                  ¯¯¯¯     '----'
```

## official-Cosmetics/SpringBloom

Sheets viewed: listed res03–res15; also opened unlisted res01 (flower button icon) and res02 (shovel icon)
(all 15 opened). res03–res12 are 5-frame `ui.AddAnim` strings (`%%` separators); each frame was split and viewed.
Source: `~/Downloads/stone-story-official/Cosmetics/SpringBloom.txt` (by TeumessianSven).

1. Depicts five flowers growing from a seed: sunflower (res03 stem layer + res04 bloom layer), dandelion (res05+06),
   tulip (res07+08), sage (res09+10), mushroom (res11+12). `Bloom()` adds both anims to one 5x4 panel,
   `duration = 20` over 5 frames (4 ticks each), non-looping (grows once, then holds the last frame). The two layers
   have the same origin and frame count; the bloom layer only adds colour cells (spaces and `#` transparent), so the
   stem layer composited with the bloom layer is one 5-frame growth sequence per flower. res13–res15 are the
   Deadwood Waterfall tree (wood, leaves, flowers layers, one frame each, static). res01/res02 are UI button icons.
2. Sizes: every flower frame 4x5 (IDEAL). Tree 6x10 (IDEAL) but static. Glyphs: `γ` U+03B3 and `ι` U+03B9
   (Greek, ambiguous: single-width with `ambiwidth=single`, wide in CJK fonts), `Ü õ` narrow, `´ ─ ░ │ ┬`
   ambiguous. Typing `γ ι Ü õ ´` needs digraphs (`g*`, `i*`, `U:`, `o~`, `''`).
3. Diffs on the composites (script-counted cells):
   sun 2, 5, 5, 9; dandelion 2, 3, 3, 10; tulip 2, 4, 2, 4; sage 2, 3, 2, 4; mushroom 1, 4, 7, 10.
   ASCII-only steps: sun f3->f4 (`1GI  _<Esc>` `2G2|R(@)<Esc>` `4G2|r``, 5 cells); dandelion f3->f4 (`2G2|R(@)<Esc>`,
   3 cells); mushroom f3->f4->f5 (`2GI  ,<Esc>` `3G0R (_)<Esc>` `4G0R  0 <Esc>`; then `2G2|R,~.<Esc>`
   `3G1|R(___)<Esc>` `4G2|R(_)<Esc>`). Subtractive direction (author f5, derive earlier frames): sun f5->f4 is
   `1G0R  _ <Esc>` `2G0R (@) <Esc>` `3G0R `( <Esc>` (9 cells, three row replaces); dandelion f5->f4 is `1G0D`
   `2G0R (@) <Esc>` `3G0R  { <Esc>` (10 cells).
4. Tutor fit: M6 Pyramid build (subtractive authoring and playback order): each flower is a 5-frame build where
   the final bloom is authored first and earlier frames are derived by removing cells; playback runs sprout ->
   bloom. M7 Timed build: the source holds each frame 4 ticks and then holds the bloom forever, so the lesson can
   teach "hold the last frame". Tulip and sage steps are 2–4 cells. Tree: M5 Layered scene candidate (wood / leaves
   / flowers layers) but it never animates.
5. Verdict: USE. Best slot M6 (mushroom and sunflower: 4x5, 5 frames, 1–10 cells per step, ASCII-only
   intermediate steps). Tree res13–res15: MAYBE for M5 (static layer study, not an animation). res01/res02: REJECT
   (UI icons). Greek `γ ι` in the sprout frames: substitute `y`/`i` or accept `ambiwidth=single`.

Composited growth frames (stem layer + bloom layer, top-aligned at the panel origin, 4 ticks each):

```
sun-f1   f2    f3     f4     f5
                        _     .γ,
                 γ     (@)   :>@<;
           γ    `(     `(     ´(`
  γ        (     )´    `)´    `)´
dandy-f1   f2    f3    f4     f5
                               .~.
                   γ    (@)   :~*~;
             γ     {     {     `{´
  γ          {     }     }      }
tulip-f1   f2    f3     f4     f5
                          ,      ,
                   u      Ü     (_)
             γ     (,     (,     (,
  γ          (     )      )     `)
sage-f1   f2    f3     f4     f5

                   ,      ,   ., ,
            γ    `γ     `γ,   ,`γ,´
  γ         ι     ι´    `ι´    `ι´
shroom-f1   f2    f3     f4     f5

                           ,     ,~.
                    ,     (_)   (___)
  .           õ    (_)     0     (_)
```

Tree layers (res13 wood, res14 leaves, res15 flowers; static):

```
res13        res14        res15
  ,:;*;,       ,:; ;,          *
,:;*|'/*:,   ,:;  '  :,      *   *
*─\'|*|;─;      '   ; ;   *    *
`,*\`;;─*    `,  `;;        *     *
  `'  ´´       `'  ´´
      ´            ´
```

## official-Cosmetics/MineManager

Sheets viewed: listed res03, res08–res13, res18–res22; also opened unlisted res01, res02, res04–res07, res14–res17
(all 22 opened).
Source: `~/Downloads/stone-story-official/Cosmetics/MineManager.txt`.

1. Depicts the player riding a Mine Walker (two-legged boiler mech). Screen-space HUD (`>``): res01 portrait, res02
   `O :hp/maxhp` text, res03 box frame, res04–res07 item-state icons — UI. World-space mech at `>o`: body res13
   `(-6,-4)`; flame res14 `VV` always + res15 `VV/vv` when `time % 10 < 5` (5-tick flicker); eye res16 `(_)` at
   `(2,-3)` except `time % 300 <= 7` when res17 `———` at `(2,-2)` (blink every 300 ticks, 8 ticks closed); left
   leg/arm res08 (state 1/-1; res09 same art in cyan for the first 3 ticks), res10 (state 2 raise), res11 (state 3
   strike), res12 (state 4, res11 art in cyan) at `(1,-1)`/`(1,-2)`; right leg/arm res18–res22 the same at
   `(-3,-1)`/`(-3,-2)`. The limbs are part layers; the only full-subject sequences are the composites below.
   res08 == res09 == res18 == res19, res10 == res20, res11 == res12 == res21 == res22 (colour-only differences).
2. Sizes: composite mech 8 rows x 17 cols (ACCEPTABLE); single limb layers 4–5 rows x 4–10 cols. Glyphs: `— ‾ •
   │ ┌ ┐ └ ┘` ambiguous (OK); the body row 1 and the blink use em dash `—` (typing needs digraph `-M`).
3. Diffs (composites, script-counted): flame A -> B 2 cells (`6G3|Rvv<Esc>`, pure ASCII); idle -> blink 4 cells
   (`2G10|r ` then `3G9|R———<Esc>`; ASCII alternative `R---`); idle -> left state 2 23 cells (the whole left limb
   is replaced by the raised arm); left state 2 -> state 3 9 cells (`3G14|R___<Esc>` `4G15|R——:<Esc>`
   `5G14|R‾‾‾<Esc>`: three row replaces, non-ASCII glyphs).
4. Tutor fit: M13 Texture pulse / M0 Spark loop for the flame flicker (`VV`/`vv`, 2 cells, strictly periodic).
   M3 Pose copy for idle -> attack (duplicate the idle pose, change the one acting limb), but the limb swap is
   23 cells and state 2 -> 3 is 9 non-ASCII cells, so neither is a beginner edit. M2 for the eye blink (4 cells inside the boiler contour).
5. Verdict: MAYBE. The composite is a good 8-row subject with three small loops (flame, blink, strike), but every
   sequence is assembled from part layers at different offsets and the pose change is large. Best slot M13 (flame
   flicker) or M3 (strike, state 2 -> 3). HUD res01–res07: REJECT (UI).

Composites (left limb drawn first, then body, flame, eye, right limb, as in the script):

```
idle (flame A)   flame B          eye blink
   _,—-.___         _,—-.___         _,—-.___
  _\     _ \       _\     _ \       _\       \
 | |)   (_) \     | |)   (_) \     | |)   ——— \
 |_/_//______|    |_/_//______|    |_/_//______|
  VV//  //         VV//  //         VV//  //
    \\  \\         vv\\  \\           \\  \\
    /|\ /|\          /|\ /|\          /|\ /|\
    \v/ \v/          \v/ \v/          \v/ \v/
left state2        left state3         right state3
   _,—-.___           _,—-.___            _,—-.___
  _\     _ \         _\     _ \          _\     _ \
 | |)   (_) \/‾\    | |)   (_) \___     | |)   (___\
 |_/_//______|-•    |_/_//______|——:    |_/_//_/———:|
  VV//   \\//\_/     VV//   \\//‾‾‾      VV \\//‾‾‾
    \\    ‾‾           \\    ‾‾              ‾‾\\
    /|\                /|\                     /|\
    \v/                \v/                     \v/
```

## official-Games/StoneasaurGame

Sheets viewed: res01–res11 (all 11 listed, all opened). Multi-frame `ui.AddAnim` strings (res01, res02, res05,
res07, res08, res09, res11) were split on `%%` and each frame viewed.
Source: `~/Downloads/stone-story-official/Games/StoneasaurGame.txt` (by xx; Chrome-Dino style runner).

1. Depicts a Chrome-Dino style runner at Deadwood Waterfall:
   - res01 `moveAnim`: stick-figure run cycle, 4 frames, `duration = 20` (5 ticks each), loop. Jumps are done by
     `pivotY = ceil(sin(t*pi/30)*8)` on the same art (frame reset to f1 while airborne).
   - res02 obstacle 1 (4 variants, `frame = rng % 4` per spawn — variants, not a sequence); res03 obstacle 2
     (single 5x7 gravestone/chest).
   - res04 starfield background (30x100), res05 background captions (text), res06 scrolling ground (9x104 brick
     tiling) — scenery.
   - res07 `delta` (5 frames; `delta.frame` stepped 4 -> 0 every 5 ticks in `watch_goodStart`).
   - res08 `badAnim` (7 frames, `duration 30`, once): figure falls flat (`>──>O`) and gets up to standing.
   - res09 `goodAnim` (13 frames, `duration 45`, once): figure lands arms-up, crouches, stands, walks right.
   - res10 green jam gem (static 9x21); res11 `jamShiny` sparkle (8 frames, once, random position).
2. Sizes: run 3x3 (IDEAL); badAnim 3x6 (IDEAL); goodAnim 4x10 (IDEAL); obstacle 3x5 (IDEAL); delta 4x5 (IDEAL);
   sparkle 6x5 (IDEAL); gem 9x21 (ACCEPTABLE, static); res04 30x100 and res06 9x104 TOO-LARGE (res06 tiles every 8
   cols, so a clean 24-col crop exists). Glyphs: box drawing `─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼ ╞ ╡ ╤ ╒ ╕`, `• ´ · ‾ Ω`
   ambiguous (OK with `ambiwidth=single`), `∆ ¯` narrow. No wide glyphs. The run cycle is pure ASCII.
3. Diffs (script-counted cells):
   - Run (res01): f1->f2 2 (`3G0R ><Esc>`), f2->f3 1 (`3G2|r|`), f3->f4 1 (`3G$r>`), f4->f1 3 (`3G0R/ \<Esc>`).
     All changes are on row 3 (the legs); rows 1–2 are identical in every frame.
   - badAnim (res08): 10, 5, 5, 4, 7, 4 cells — a lying-to-standing rotation about the feet.
   - goodAnim (res09): 3, 2, 4, 5, 2, 7, 8, 8, 2, 2, 8, 10 cells. f9->f10 2 cells (`2G6|r ` `3G6|r/`),
     f10->f11 2 cells (`4G6|R/<<Esc>`).
   - delta (res07): 7, 8, 5, 9 cells (box-drawing, non-ASCII). Sparkle (res11): 2, 6, 12, 12, 12, 12, 6.
4. Tutor fit: M0 Spark loop — the run cycle is a 3-row, 4-frame, pure-ASCII loop where one readable change (the
   legs) happens per frame; whole-frame copy + one `r` is exactly the lesson. M12 Joint sweep also fits (`3Gt\`,
   `;` landings on the leg row). M4 Rotation tween: badAnim is a 3-row rotation from lying to standing with a
   stable pivot at the feet (f1 lying, f4 midpoint, f7 standing) — good extremes/midpoint material, but the box
   glyphs `─ ┘` must be typed with digraphs or replaced with `-`/`'`. M16 Key-pose plan: goodAnim is a 13-frame
   acted sequence (land, crouch, stand, walk) with 4-row frames. M14 Variant palette: obstacle res02 is four
   variants of one 3x5 box chosen at random.
5. Verdict: USE. Best slot M0 (run cycle, 1–3 cells per frame, ASCII). MAYBE: badAnim for M4, goodAnim for M16,
   obstacle variants for M14, ground res06 crop for M15. REJECT: res04 (starfield, too large), res05 (text),
   res10 (static gem), res11 (sparkle, frames too sparse), res07 (box-drawing morph, 5–9 non-ASCII cells).

Run cycle (res01, 5 ticks each, loop):

```
f1    f2    f3    f4
 O     O     O     O
/|\   /|\   /|\   /|\
/ \    >\    |\    |>
```

badAnim (res08, once; frames top-aligned in a 3-row box):

```
f1     f2      f3      f4     f5     f6    f7
>──>O                                   O    O
                  _      __     _\O    (\   /|\
        >─/O>   `┘<O\   |\/O   |\ \   / \   / \
```

goodAnim (res09, once; f1 is empty):

```
f1 f2   f3   f4   f5     f6     f7
                O    O      O       O
    \O/  _O_  ,((   '))`    ))V    //\
                                     /V
f8      f9       f10      f11      f12       f13

    _O       _O        O        O         O          O
     ´)       |\      /|\      /|\       /|\        /|\
     ¯\      ´(       ´(       /<        <|          |\
```

Obstacle variants (res02) and ground crop (res06 rows 1–9, cols 1–24):

```
f1     f2     f3     f4
 ___    ___   ┌-─-┐   ___
├─•─┤  ├─o─┤  ╞╤8╤╡  ┼┬Ω┬┼
└───┘  └───┘  └┴─┴┘  └┴─┴┘
-^-------^-^^---^---^-^-
 ┌   ┐   ┌   ┐   ┌   ┐
 │   │   │   │   │   │
┐   ┌   ┐   ┌   ┐   ┌
│   │   │   │   │   │
   ┐   ┌   ┐   ┌   ┐   ┌
   │   │   │   │   │   │
  ┌   ┐   ┌   ┐   ┌   ┐
  │   │   │   │   │   │
```

## official-Pets/Bunny

Sheets viewed: listed res01, res04–res12; also opened unlisted res02, res03 (ear overlays) (all 12 opened).
Source: `~/Downloads/stone-story-official/Pets/Bunny.txt` (by Kash, after standardcombo's PetFrog).

1. Depicts a white rabbit pet that sits (idle) and hops after the player. Idle: res01. When the player's face is
   `°°`, an ear overlay alternates every 2 ticks (`time % 4 <= 1` res02 `||`, else res03 `((`), drawn over res01
   at the same origin (its leading space is opaque and erases the idle ear). Jump: 16 ticks, `stateTime/2` selects
   res04..res12 (9 frames, 2 ticks each), all at the same origin while `myX` advances 1 col per tick; the body rises
   inside the 5-row canvas (res06–res08 are the airborne frames) and lands at res11/res12, then returns to res01.
2. Sizes: 5 rows x 9–10 cols canvas (IDEAL); the rabbit itself is 3 rows tall in every frame. Glyphs: `α` U+03B1
   (Greek alpha, tail; ambiguous), `‾ ´` ambiguous. No wide glyphs. The ear twitch is pure ASCII.
3. Diffs (script-counted cells): ear twitch idle -> res02 composite 3 cells (`3G7|R ||<Esc>`); res02 <-> res03 2 cells
   (`3G8|R((<Esc>` / `3G8|R||<Esc>`). Jump: 01->04 8, 04->05 7, 05->06 17, 06->07 12, 07->08 6, 08->09 20, 09->10 13,
   10->11 12, 11->12 12, 12->01 4 (landing settle: `3G7|R\\<Esc>` `4G7|r_` `5G8|r\`).
4. Tutor fit: M0 Spark loop — a 3-row still with one readable 2-cell change that loops (ears `||` <-> `((`); pure
   ASCII. M9 Bounce capstone — the hop has a real arc (rise res05/res06, apex res07/res08, fall res09/res10, land
   res11/res12, settle res01), 2 ticks per frame, but steps are 6–20 cells.
5. Verdict: USE. Best slot M0 (ear twitch, 2 cells, `R`); MAYBE for M9 (hop arc as a planning/keyframe reference).

Idle with ear overlays (3-row content; rows 1–2 of the canvas are blank):

```
idle res01   idle+res02   idle+res03
      \\            ||           ((
     __()         __()         __()
   α(_-\        α(_-\        α(_-\
```

Jump (res04..res12, 2 ticks each, same origin, 5-row canvas):

```
04         05         06         07         08         09          10         11        12
                             _         \\         ((
                            ‾()       __()       __()
                  _        /´)      α( -\      α(_-‾'       __((        _                      _
     _\\        _‾()     α(_          )                   α(_-.()     α( \\       _\\        _‾()
   α(_.()     α(_-/                                            ‾'       \.()    α(_.()     α(_-(
```

## official-Cosmetics/ConfettiHead

Sheets viewed: res01–res08 (all 8 listed, all opened).
Source: `~/Downloads/stone-story-official/Cosmetics/ConfettiHead.txt` (by Sterrella).

1. Depicts a confetti pop above the player's head: res01 is the pop (a `|`, `\ /`, `— —` burst), res02–res08
   show five particles drifting outward and down while each particle cycles its glyph (acute `´`, bullet `•`, comma, backtick, period, apostrophe). Array
   indexed by `totaltime % 10`; frames 0–7 drawn 1 tick each at `(-3,-2)` in `#rainFF`, frames 8–9 empty (2-tick
   gap), loop.
2. Sizes: 4–7 rows x 6–7 cols; common canvas 7x7 (IDEAL). Glyphs: `— • ´` ambiguous (OK). No wide glyphs.
3. Diffs (script-counted cells): 01->02 10, 02->03 6, 03->04 7, 04->05 7, 05->06 7, 06->07 9, 07->08 7. Every step
   moves and re-glyphs all five particles (one or two cells each). A single particle's change is 1–2 cells, e.g.
   02->03 top particle `1G4|r•`; but a full frame step needs 5 separate edits.
4. Tutor fit: M13 Texture pulse — the particles are single-glyph WORDs separated by spaces, so `W`/`B`/`E` hop
   between them on a row and `r` re-glyphs each; the glyph cycle (acute, bullet, comma, backtick, period) is a texture pulse. But the frames are
   sparse and have no stable contour to anchor a beginner.
5. Verdict: MAYBE (M13 WORD-hop + `r` practice on a sparse particle row; 6–10 cells per frame step).

```
01      02       03       04       05       06       07       08
           ´        •
   |     '   ,    ´        , `        •        ,
  \ /                 '        `    ´   .    .          ´        ,
 —   —  •     `  ,     •        .                ,    •
                          '        •     ´        •       `    `   •
                                            `        .     `        .
                                                              `
```

## official-Pets/Stonehead

Sheets viewed: listed res02–res09; also opened unlisted res01 (a single `#`, the empty "disabled" block) (all 9
opened).
Source: `~/Downloads/stone-story-official/Pets/Stonehead.txt` (by Mallathor).

1. Depicts a Roof Overhead student carrying a stick (`,` `/-` `o_/`) who follows the player. Walk: res02..res05,
   `StoneheadPetFrame` += 1 every 3 ticks (4 frames, 12-tick loop); res02 is also the standing pose when not
   walking. When a `phase` foe is within 25, the student panics and runs off to the right: res06..res09 (arms up
   `\o/`, caption `AAAAAHHHHHH` baked into the art), same 3-tick clock, `x` += 1 every 2 ticks, then res01 (empty)
   once off screen. Same origin for all frames in each set.
2. Sizes: walk 5x6 (IDEAL); run 5x12 (IDEAL; row 1 blank, row 2 is the caption). Glyphs: only `‾` (U+203E,
   ambiguous, OK); everything else ASCII. No wide glyphs.
3. Diffs (script-counted cells; every change is on row 5, the legs):
   walk f1->f2 2 (`5G0R ><Esc>`), f2->f3 2 (`5G2|R|><Esc>`), f3->f4 1 (`5G3|r\`), f4->f1 2 (`5G0R/ <Esc>`).
   run f1->f2 2 (`5G6|R< <Esc>`), f2->f3 2 (`5G5|R<|<Esc>`), f3->f4 1 (`5G5|r/`), f4->f1 2 (`5G6|R \<Esc>`).
   The run legs are the walk legs mirrored left-right (`>\` <-> `/<`, `|>` <-> `<|`, `|\` <-> `/|`, `/ \` symmetric).
4. Tutor fit: M8 Walk study — 5-row frames of equal height, a stable upper body, contact (`/ \`) and passing
   (`|>`, `|\`) positions, 1–2 cells per step, all ASCII in the edited row. M18 Hand-mirrored return — the panic run
   is exactly the walk's legs mirrored, so the lesson "mirror `>`/`<` and `/`/`\` by hand" has a real source.
   M12 Joint sweep also fits (`5Gt>`, `;` on the leg row).
5. Verdict: USE. Best slot M8 (walk res02–res05). Second M18 (run res06–res09 as the mirrored return).

```
res02 f1   res03 f2   res04 f3   res05 f4
     ,          ,          ,          ,
    /-         /-         /-         /-
 o_/        o_/        o_/        o_/
 |‾         |‾         |‾         |‾
/ \         >\         |>         |\
res06 f1      res07 f2      res08 f3      res09 f4

 AAAAAHHHHHH   AAAAAHHHHHH   AAAAAHHHHHH   AAAAAHHHHHH
    \o/           \o/           \o/           \o/
     |             |             |             |
    / \           /<            <|            /|
```

## official-Pets/Chick

Sheets viewed: res01–res07 (all 7 listed) plus unlisted res08–res10 (text bubbles `Chirp!`, `Peep!`, `♣Sven`)
(all 10 opened). res01–res07 are `ui.AddAnim` strings; each `%%` frame was split and viewed; res01 (egg layers) and
res02 (chick layer) share frame indices and were composited per frame (spaces and `#` transparent in the overlay).
Source: `~/Downloads/stone-story-official/Pets/Chick.txt` (by TeumessianSven).

1. Depicts an egg that cracks and hatches a chick, which then follows the player hopping and flying.
   - Hatch: res01 (egg, drawn twice in grey/cream) + res02 (chick) 12 frames, `duration 50` (~4 ticks each),
     once. f1 whole egg, f2–f4 the crack grows by one glyph per frame (`;`, `·`, `,`), f5 the chick's head pokes out,
     f6 it rises out, f7 stands on the broken shell, f8–f12 settle (shell pieces alternate on/off).
   - Idle/peep res03 (4 frames, `duration 25`, played once per peep): wings flap up with beak open, back down,
     beak closes. Alert res04 (2 frames, `duration 7`). Jump res05 (4), fly res06 (2, loop, `duration 7`: wing flap),
     land res07 (4). Every body frame is 3 rows x 6 cols; jump/land raise it inside a 5-row panel.
2. Sizes: hatch 5x11 (IDEAL); chick 3x6 (IDEAL); jump/land 5x6 (IDEAL). Glyphs: `· ´ ♣` ambiguous (OK), `¯` narrow.
   No wide glyphs. Crack glyph `·` needs digraph `.M`.
3. Diffs (script-counted cells):
   - Hatch: f1->f2 1 (`3G8|r;`), f2->f3 1 (`3G7|r·`), f3->f4 1 (`3G9|r,`), f4->f5 14, f5->f6 15, f6->f7 16,
     f7->f8 2 (`2G10|r-` `3G5|r``), f8->f9 0 (hold), f9..f12 15 each (shell toggles).
   - Idle: f1->f2 8, f2->f3 7, f3->f4 1 (beak closes: `1G6|r-`). Fly f1<->f2 7. Alert f1->f2 8.
4. Tutor fit: M11 Fixed-width redraw (3-row egg, `r` one crack glyph per frame, then `u` / `<C-r>` to scrub the crack
   forward and back); M0 Spark loop also fits (one readable change per frame). M7 Timed build: the hatch has a
   genuine hold (f8 = f9) and a build-up of cracks. The chick idle f3->f4 (`1G6|r-`) is a 1-cell beak close for M2.
   The 2-frame wing flap could illustrate M4 extremes, but there is no midpoint frame.
5. Verdict: USE. Best slot M11 (egg crack f1->f4, 1 cell each). MAYBE: chick flap for M4, full hatch for M7.

Hatch (composited, 12 frames):

```
1          2          3          4          5           6
                                                  ,-.        ,-,
      ,-.        ,-.        ,-.        ,-.       :·;,:      :,`_O-
     :   :      : ; :      :·; :      :·;,:     `({_,O-     `{/_;,
     '._.'      '._.'      '._.'      '._.'      '._.'       '._.'
7          8          9          10         11         12

      __O<       __O-       __O-       __O-       __O-       __O-
    ,{/_;,     `{/_;,     `{/_;,     `{/ ;      `{/_;,     `{/ ;
:';´:'._.' :';´:'._.' :';´:'._.'       ^^   :';´:'._.'       ^^
 `-´        `-´        `-´                   `-´
```

Chick idle/peep (res03) and fly (res06):

```
idle f1   f2       f3       f4       fly f1   fly f2
  __O-     {\\O<     __O<     __O-    {\\O-     __O-
`{/ ;     ,( ¯;    `{/ ;    `{/ ;    ,( ¯/    `{/ /
  ^^        ^^       ^^       ^^      ´´       ´´
```

Jump (res05) and land (res07), 5-row panel:

```
jump f1   f2       f3       f4       land f1   f2       f3       f4
                             {\\O-    {\\O-
                     __O-   `( ¯/    `( ¯/       __O-
  __O-     {\\O-   `{/ /     ´´       ´´       `{/ /     {\\O-     __O-
`{/ ;     ,( ¯;     ´´                           ^^     ,( ¯;    `{/ ;
  ^^        ^^                                            ^^       ^^
```

## official-Cosmetics/MushroomAnt

Sheets viewed: res01–res06 (all 6 listed, all opened).
Source: `~/Downloads/stone-story-official/Cosmetics/MushroomAnt.txt` (by michael.g.g.).

1. Depicts an ant with mushrooms growing from its head, panicking in the Mushroom Forest. Three frames, 3 ticks
   each (`antFrame` 0–2, 3–5, 6–8), loop; screen-space `>`` at y 16 with `antX` 69, 70, 71 per frame (the body
   shuffles one column right per frame, then snaps back). Two cap variants by star level: `loc.stars > 10` twin
   caps res01/res03/res05; otherwise one wide cap res02/res04/res06. Only row 5 (the legs) changes between frames.
2. Sizes: 5x8 (IDEAL); with the x shuffle 5x10. All ASCII, no ambiguous or wide glyphs.
3. Diffs (script-counted cells, frames at the same origin): f1->f2 5, f2->f3 5, f3->f1 5, all on row 5. Edits:
   f1->f2 `5G0R-@( |-)<Esc>`; f2->f3 `5G0R>@'|\-\<Esc>`; f3->f1 `5G0R>@/ /|-<Esc>` (one bounded R-replace of 7
   cells; 5 of them differ). Variant swap (twin cap -> single cap) is 14 cells over rows 1–4, i.e. a paragraph-sized
   block: yank rows 1–4 of the other variant into a register and put them.
4. Tutor fit: M8 Walk study — 5-row frames, stable upper body, only the leg row cycles; frame height constant.
   M14 Variant palette — two cap variants over an identical body are a natural register exercise (`"ay4j` /
   `"ap`). M11 R replace — each step is one `R` over the leg row.
5. Verdict: USE. Best slot M8 (leg-row cycle, ASCII, 5 changed cells per step); second M14 (cap variants).

```
res01 f1   res03 f2   res05 f3   res02 f1   res04 f2   res06 f3
    _          _          _        __         __         __
 _ (_)      _ (_)      _ (_)      (__)       (__)       (__)
(_)(       (_)(       (_)(          )          )          )
-,\),-.    -,\),-.    -,\),-.    -,( ,-.    -,( ,-.    -,( ,-.
>@/ /|-`   -@( |-)`   >@'|\-\`   >@/ /|-`   -@( |-)`   >@'|\-\`
positioned (antX 69/70/71):
f1         f2          f3
    _           _            _
 _ (_)       _ (_)        _ (_)
(_)(        (_)(         (_)(
-,\),-.     -,\),-.      -,\),-.
>@/ /|-`    -@( |-)`     >@'|\-\`
```

## official-Weapons/MajVines

Sheets viewed: listed res02, res03, res05, res06, res10, res12; also opened unlisted res01, res04, res07, res08, res09,
res11, res13, res14, res15 (all 15 opened).
Source: `~/Downloads/stone-story-official/Weapons/MajVines.txt` (by Poly; depends on `Components/OVERHAUL`).

1. Depicts a vine hanging from a wand held in either hand. Every block's first row is the template placeholder
   `@base.IRI@` / `@base.ILI@` (the wand icon string, substituted at runtime), followed by 1–3 rows of vine
   (`)`, `(`, `\`, `` ` ``, `´`, `'`). Right hand: idle sway res02 (`time % 20 <= 10`) / res03 (else), 10 ticks each,
   over the wand-handle layer res01; attack state 2 res05 (first 3 ticks) -> res06, handle res04; state 3 res07
   then res08 (`.___,` lash). Left hand mirrors: res10 idle, res12/res13 state 2, res14/res15 state 3, handles
   res09/res11.
2. Sizes: vine 2–3 rows x 2–4 cols plus the placeholder row (a template token of 10–15 chars, not art). Glyph `´`.
3. Diffs: idle sway res02 -> res03 is 1 cell (row 4: backtick -> `´`); the attack blocks are drawn at different
   offsets (`(2,0)`, `(1,-1)`, `(0,-1)`, `(1,0)`, `(2,2)`), so they are not one origin.
4. Tutor fit: none. The only same-origin pair is a 1-cell change on a 3x2 fragment that means nothing without the
   player sprite and the substituted wand icon.
5. Verdict: REJECT (part layers only; template placeholder rows; subject too small).

## official-Cosmetics/Portobello

Sheets viewed: res01–res04 (all 4 listed) plus unlisted res05–res08 (feet cycle) (all 8 opened).
Source: `~/Downloads/stone-story-official/Cosmetics/Portobello.txt` (by Sterella).

1. Depicts the player replaced by a portobello mushroom: a big cap head (res01–res04, indexed by the held item's
   attack state, `headstate - 1`) at `(-10,-3)` and a 4-frame feet cycle (res05–res08) at `(-2,2)` that tucks into
   the gap under the chin. Feet advance one frame every `feetdelay + 1` ticks (10 by default, 7 with triskelion, 13
   with towering), backwards when `player.direction` is -1. Heads: res01 neutral `o o`, res04 same cap with `> <`
   eyes, res02 and res03 the cap tilted back/forward during the attack (swing poses). The feet layer's spaces are
   opaque, so it rewrites the chin row.
2. Sizes: head 6x18 (row 1 blank; IDEAL); head + feet composite 6x18 (IDEAL); feet 2x3. Glyphs: `• ´ … — ò ó`
   ambiguous (OK), `¯ ö` narrow. No wide glyphs. The neutral-to-squint edit is ASCII.
3. Diffs (composites, script-counted): res01 -> res04 2 cells (`5Gfor>;r<`); res01 -> res02 46 cells; res04 ->
   res03 29 cells (whole-cap re-draws). Feet cycle f0->f1->f2->f3->f0: 5 cells each (rows 5–6); f1 uses `ö`.
4. Tutor fit: M2 Face focus — the cap contour is identical and only the eyes change (`o o` -> `> <`), a 2-cell edit
   done with `f` + `r` + `;`; also M1 (landmark `fo`, `;`). The feet cycle could be an M8 aside but the feet are 2x3
   and use `ö`. The swing heads are too different to tween by hand.
5. Verdict: USE. Best slot M2 (res01 -> res04, `5Gfor>;r<`). MAYBE: feet cycle for M8. REJECT res02/res03 as
   edit targets (46/29 cells).

```
head res01          res02              res03                res04
                             ___……_                  -…_
  •´¯¯¯¯¯¯¯¯¯¯¯`•     _…——´¯¯      `•    •´¯¯¯¯¯¯¯¯¯¯¯¯`•     •´¯¯¯¯¯¯¯¯¯¯¯`•
 (_______________)  ,´      ____……——'   (´      _________)   (_______________)
      |     |       L…——T¯¯¯   \        L…———/¯¯    |  .´         |     |
      |  o o|            \   ò ó|            |  > < /             |  > <|
      \_ ___/             \_ ___|            \_ ___/              \_ ___/
        U U                 U U                U U                  U U

walk f0 (res05)     f1 (res06)          f2 (res07)          f3 (res08)
  •´¯¯¯¯¯¯¯¯¯¯¯`•     •´¯¯¯¯¯¯¯¯¯¯¯`•     •´¯¯¯¯¯¯¯¯¯¯¯`•     •´¯¯¯¯¯¯¯¯¯¯¯`•
 (_______________)   (_______________)   (_______________)   (_______________)
      |     |             |     |             |     |             |     |
      |  o o|             |  o o|             |  o o|             |  o o|
      \_ ___/             \__ __/             \___ _/             \__ __/
        U U                  ö                  U U                  U
```

## official-Cosmetics/TheSun

Sheets viewed: listed res01, res02, res04, res05; also opened unlisted res03 (all 5 opened).
Source: `~/Downloads/stone-story-official/Cosmetics/TheSun.txt` (by Insult).

1. Depicts a stage-prop sun lowered on two ropes at screen centre on Icy Ridge / Rocky Plateau / Cross Bridge:
   ropes res01/res02 (`┊` x5), pulley res03, sun face res04 (`▼-▼` eyes), rays res05. No block changes over time;
   the only motion is `ropedown` / `altropedown` moving the same blocks down 1 row every 3 ticks until row 2, then
   a 1-row bounce back, and raising again when a boss is near. `bighead` adds `>( ▼-▼` to the player.
2. Sizes: sun 7x10 (IDEAL), rays 7x13 (IDEAL), composite with ropes ~12x13. Glyphs `┊ ─ ▼ ´` ambiguous, `¯` narrow.
3. Diffs: none between blocks — every frame is the same art at a different y (pure translation).
4. Tutor fit: none as a frame sequence. The rope descent + 1-row bounce is a translation-only example.
5. Verdict: REJECT (not an animation: static blocks translated by offset; frames identical).

## official-Cosmetics/Drill

Sheets viewed: listed res02, res03, res04; also opened unlisted res01, res05–res31 (all 31 opened; res11–res24 are
single gem glyphs `♥ ∞ ❄ φ * o @`, res05–res10 single-glyph/2-row status marks, res28–res31 bomb/launcher bits).
Source: `~/Downloads/stone-story-official/Cosmetics/Drill.txt` (by Poly).

1. Depicts the player driving a drill tank: body res04 at `(-14,-2)` with the rider `o /|\`, drill bit res02 at
   `(0,0)` with res03 drawn over it on odd ticks while attacking (`time % 2 = 1`), tread base res25 at `(-12,3)`
   plus a tread shimmer res26 (`time % 40 <= 20` or idle) / res27 (else) whose `#` cells are transparent — in the
   game it only recolours alternate tread cells. HUD res01 (`［O］>:`, fullwidth brackets) and status overlays
   res05–res10, gem sockets res11–res24, weapon bits res28–res31 are layers or UI.
2. Sizes: composite tank 7x21 (IDEAL width, ACCEPTABLE height 7); drill bit 4x4; tread layers 2x13. Glyphs:
   `≈ ‾ ´ — ≤ ♥ ∞ φ` ambiguous, `❄` narrow; res03 contains fullwidth `＂` U+FF02 and res01 `［ ］` (WIDE, unsafe).
3. Diffs: drill bit res02 -> res03 14 of 16 cells (every cell re-glyphed, includes the wide `＂`). Tread res26 ->
   res27 26 cells when drawn alone (the dash pattern shifts one column: ` ‾ ‾ ‾` <-> `/ ‾ ‾ \`); composited over
   res25 the monochrome result is identical (0 cells).
4. Tutor fit: the tread layers alone are a 2-row alternating dash texture (M13/M15 flavour: shift a dithered row by
   one column with `:s/ ‾/‾ /g` or `0x$p`), but they only exist as a colour shimmer. The drill spin is all-cell
   noise with a wide glyph.
5. Verdict: REJECT for the drill bit (all cells change, wide `＂`) and the body (static). MAYBE for the tread layers
   res26/res27 as an M15 "shift the texture one column" example (needs `‾` -> `-` substitution to be ASCII).

```
idle tread A         tread B              drilling (res03 over res02)

          o                    o                    o
 /‾\     /|\_         /‾\     /|\_         /‾\     /|\_
´  |‾‾‾‾‾‾‾‾‾|≈~.    ´  |‾‾‾‾‾‾‾‾‾|≈~.    ´  |‾‾‾‾‾‾‾‾‾|=-,
   |: |‾|   :|=-~\      |: |‾|   :|=-~\      |: |‾|   :|≈~-)
   |:  ‾    :|≈~-/      |:  ‾    :|≈~-/      |:  ‾    :|=-~)
  /‾‾‾‾‾‾‾‾‾‾‾\-'      /‾‾‾‾‾‾‾‾‾‾‾\-'      /‾‾‾‾‾‾‾‾‾‾‾\~＂
  \___________/        \___________/        \___________/
tread layers alone (res26, res27):
res26           res27
 ‾ ‾ ‾ ‾ ‾ ‾    / ‾ ‾ ‾ ‾ ‾ \
\ _ _ _ _ _ /    _ _ _ _ _ _
```

## official-Games/2048

Sheets viewed: res01–res03 (all 3 listed, all opened).
Source: `~/Downloads/stone-story-official/Games/2048.txt` (by ArtificialPotato).

1. Depicts UI text for a 2048 clone: res01 the `2048` block-letter title (`█ ╗ ║ ═ ░`), res02 the `GAME OVER` banner
   with "Press a button/Title(C) to return to menu", res03 the PC key tips (`↑↓←→: Move`, ...). Tiles are drawn
   with `draw.Box`/text at runtime, not ascii blocks. No block is sequenced by time; there is no animation.
2. Sizes: res01 6x32, res02 5x52 (TOO-LARGE), res03 4x20. Glyphs: box/block drawing and arrows (ambiguous).
3. Diffs: n/a (three unrelated UI strings).
4. Tutor fit: none.
5. Verdict: REJECT (UI / title text; not an animation).

## official-Hats/Treeman

Sheets viewed: res01–res03 (all 3 listed, all opened).
Source: `~/Downloads/stone-story-official/Hats/Treeman.txt` (by Radak).

1. Depicts a tree-stump hat in three colour layers drawn at the same hat offset `(-4,-4)` every frame: res01 white
   outline (with face `o`, `°`, `└─┘`), res02 green bark, res03 rainbow accents (`@`, `＂`, `o`, `°`). No time or
   state condition selects between them; all three are always drawn. Not an animation.
2. Sizes: 6x8, 5x8, 4x6 (IDEAL). Glyphs: fullwidth `＂` U+FF02 in res01 and res03 (WIDE, unsafe); `° ´ ‾ ─ └ ┘`
   ambiguous.
3. Diffs: n/a (simultaneous colour layers, not frames).
4. Tutor fit: none as animation; as a static layered still it would need the wide `＂` replaced.
5. Verdict: REJECT (not an animation; static colour layers; wide glyph).

## official-Hats/MushroomHat

Sheets viewed: res01–res02 (both listed, both opened).
Source: `~/Downloads/stone-story-official/Hats/MushroomHat.txt` (by TeumessianSven).

1. Depicts a mushroom hat: res01 red top layer and res02 white bottom layer, both drawn every frame at `(-5,-4)`.
   No time or state condition; not an animation.
2. Sizes: 6x10 each (IDEAL). Glyphs: `° — •` ambiguous (OK); no wide glyphs.
3. Diffs: n/a (simultaneous colour layers).
4. Tutor fit: none as animation (possible M5 two-layer still, but the layers only split colour, not depth).
5. Verdict: REJECT (not an animation; static colour layers).

## official-Pets/CatBalloon

Sheets viewed: res01–res02 (both listed, both opened); res02 is a 10-frame `ui.AddAnim` string, split and viewed.
Source: `~/Downloads/stone-story-official/Pets/CatBalloon.txt` (by bitty45; balloon art tomatobulb, cat art sun).

1. Depicts a hot-air balloon (res01, static) with a cat (res02) in the basket at `(+4,+8)`, drifting along a
   parabolic height arc (`LOOP_TIME 300`). Cat anim: 10 frames over `ANIM_LOOP_TIME 80` (8 ticks each), loop:
   f1–f8 identical (a 64-tick hold), f9 the cat stretches/yawns (ears and body shift, `-` eye), f10 blink
   (`-ω´`), then back to f1.
2. Sizes: cat 3x7 (IDEAL); balloon 13x14 (ACCEPTABLE, static); balloon + cat composite ~16x14 (TOO-LARGE for the
   popup height). Glyphs: `ω` U+03C9 (Greek, ambiguous), `° ´ ¡ • ‾ ─ │ ┴` ambiguous. No wide glyphs.
3. Diffs (script-counted cells): f1..f8 0 (hold); f8->f9 11; f9->f10 9; f10->f1 2 (`3G4|ro` then `3G6|r°`, the
   second needs digraph `DG`).
4. Tutor fit: M7 Timed build — a textbook hold: eight identical frames, then two acting frames. The lesson can build
   the loop with `yyp`-style frame duplication and a count (8 copies), then edit f9/f10. M2 for the 2-cell blink.
5. Verdict: MAYBE (M7 hold/timing example; the acting frames are 9–11 cells and use `ω ° ´`).

```
f1 (f2-f8 same, hold)   f9 stretch   f10 blink
     ,                        ,           ,
 -.-´'\                 __.-~´|       -.-´'\
 \ oω°)                 `. -ω´)       \ -ω´)
```

## official-UI/RecordPlayer

Sheets viewed: res02, res03 (both listed, both opened; res02 5 frames and res03 2 frames split and viewed).
Source: `~/Downloads/stone-story-official/UI/RecordPlayer.txt` (by Mind Stone Thief).

1. Depicts a record-player music UI: res02 `RProll` the turntable (12x43) whose platter grooves carry `m` / `´` /
   `.` highlights that move around the record, 5 frames, `duration 50` (10 ticks each), loop while music plays;
   res03 `RPswitch` the tone arm at `(-5,-2)`, 2 frames (arm on the record vs lifted off). res01 (text background)
   is not in the listed set.
2. Sizes: turntable 12x43 (TOO-LARGE); clean crop of the platter rows 4–9, cols 6–33 = 6x28 (ACCEPTABLE); tone arm
   8x33 (sparse; the arm itself is 8x8). Glyphs: `‾ ´ ┊` ambiguous; no wide glyphs.
3. Diffs (script-counted cells, full frame): f1->f2 9, f2->f3 10, f3->f4 7, f4->f5 7, f5->f1 14; every change is a
   highlight glyph hopping along the groove (e.g. f3->f4 starts with `4G22|rm`, then six more scattered single-cell `r` edits). Tone arm
   f1->f2 29 cells (the arm swings; different geometry).
4. Tutor fit: M13 Texture pulse — the highlights move along a fixed groove, so each step is a few scattered `r`
   edits reached with `W`/`E`/`f`; but 7–14 changes per step and a 28-col crop make it an advanced exercise.
5. Verdict: MAYBE (M13, platter crop; too many scattered cells for a beginner). Tone arm: REJECT (part layer,
   29-cell swing).

Platter crop (rows 4–9, cols 6–33):

```
f1                            f2                            f3
 |  __,--'    `--.__     ‾‾‾   |  __,--'    `--.__     ‾‾‾   |  __mm-'    `--m__     ‾‾‾
/,-'      ,-"-.     ‾`-       /,m´      ,-"-.     ‾`-       /,-'      ,-"-.     ‾`-
(        (  ^  )       )      (        (  ^  )       )      (        (  ^  )       )
 `m.__    `-.-'      .m        mm.__    `-.-'      .´        mm._     `-.-'      .´
   `""mm.______,mm""'            `""mm.______,m.""              ""'m.______,..""
        `""""""'                      `"""" '                       `"""""'
f4                            f5
 |  __mm-'    `-mm__     ‾‾‾   |  __,--'    `-m.__     ‾‾‾
/m-'      ,-"-.     ‾`m       /,-'      ,-"-.     ‾mm
(        (  ^  )       )      (        (  ^  )       )
 ".._     `-.-'      .´        ".._     `-.-'      .´
    ""'..______,.m""              ""'m.______,.mm"
        `"""""'                       `"""""'
```

## Summary

Counts: USE 10, MAYBE 5, REJECT 6 (21 sets). Sizes are rows x cols of the frame the lesson would use.

| set | frames | size | verdict | best module | proposed edit |
|---|---|---|---|---|---|
| official-Cosmetics/Mech | walk 8 slots, 7 distinct (res02–res09) | 12x19; leg crop 5x16; wide `［］｛｝《》` | MAYBE | M8 (leg crop, glyph substitution) | 08->09 leg straighten, ~10 cells (`3G0f\r\|;r\|` + foot rows) |
| official-Pets/LegsTurkey | stand-up 4, walk 11+11, sit-down 3 | legs 6x8; composite 9x7 | USE | M7 (also M6, M8) | stand-up `5GO   \|\|<Esc>.`; sit-down `5G2dd` `.` |
| official-Pets/FoesNoMore | snek head 12; cultist walk 5; ice guy 10 | 4x7; 5x7; 3x6 | USE | M2 (cultist M8, ice guy M0) | tongue `2GA-<Esc>` `.` `2G$r<` `2G$r,` |
| official-Pets/Mushroom | hop 12; faces 5 | faces 5x8; hop 9x11 | USE | M2 (also M14; hop MAYBE M9) | `-w-` -> `^w^`: `4Gf-r^;r^` |
| official-Cosmetics/SpringBloom | 5 flowers x 5 growth frames | 4x5 | USE | M6 (also M7) | mushroom f4->f5 `2G2\|R,~.<Esc>` `3G1\|R(___)<Esc>` `4G2\|R(_)<Esc>`; dandelion f3->f4 `2G2\|R(@)<Esc>` |
| official-Cosmetics/MineManager | flame 2, blink 2, strike 3 (composites) | 8x17 | MAYBE | M13 (strike M3) | flame `6G3\|Rvv<Esc>` |
| official-Games/StoneasaurGame | run 4; badAnim 7; goodAnim 13 | 3x3; 3x6; 4x10 | USE | M0 (badAnim M4, goodAnim M16) | run f2->f3 `3G2\|r\|`, f3->f4 `3G$r>` |
| official-Pets/Bunny | ear twitch 2; jump 9 | 5x9 (3-row rabbit) | USE | M0 (jump MAYBE M9) | ears `3G8\|R((<Esc>` |
| official-Cosmetics/ConfettiHead | 8 (+2 empty) | 7x7 | MAYBE | M13 | per particle `1G4\|r•`; 6–10 cells per frame |
| official-Pets/Stonehead | walk 4; panic run 4 | 5x6; 5x12 | USE | M8 (run M18) | walk f3->f4 `5G3\|r\`; f1->f2 `5G0R ><Esc>` |
| official-Pets/Chick | hatch 12; idle 4; fly 2; jump 4; land 4 | 5x11; 3x6 | USE | M11 (hatch M7) | crack `3G8\|r;`, `3G9\|r,`; `u`/`<C-r>` to scrub |
| official-Cosmetics/MushroomAnt | 3 (x2 cap variants) | 5x8 | USE | M8 (also M14) | `5G0R-@( \|-)<Esc>` |
| official-Weapons/MajVines | vine layers, 1-cell sway | 3x2 fragments + placeholder row | REJECT | — | part layers; template `@base.IRI@` |
| official-Cosmetics/Portobello | head 4 states; feet 4 | 6x18 | USE | M2 (also M1) | `5Gfor>;r<` (`o o` -> `> <`) |
| official-Cosmetics/TheSun | static blocks translated | 7x10 | REJECT | — | frames identical; offset motion only |
| official-Cosmetics/Drill | drill bit 2; tread shimmer 2 | 4x4; 2x13; tank 7x21 | REJECT (tread MAYBE M15) | — | drill 14/16 cells + wide `＂`; tread colour-only |
| official-Games/2048 | 3 UI strings | 6x32, 5x52, 4x20 | REJECT | — | UI/title text |
| official-Hats/Treeman | 3 colour layers | 6x8 | REJECT | — | static layers; wide `＂` |
| official-Hats/MushroomHat | 2 colour layers | 6x10 | REJECT | — | static layers |
| official-Pets/CatBalloon | cat 10 (8 held) | 3x7 | MAYBE | M7 | blink back `3G4\|ro` `3G6\|r°` |
| official-UI/RecordPlayer | platter 5; tone arm 2 | 12x43; crop 6x28 | MAYBE | M13 | 7–14 scattered `r` per step |
