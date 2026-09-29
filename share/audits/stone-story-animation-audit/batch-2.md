# Stone Story animation audit — batch-2

- Date: 2026-09-28
- Auditor: subagent batch-2 (manual view of every listed sheet)
- Base: `~/Downloads/stone-story-consolidated/` (sheets), `~/Downloads/stone-story-official/<Category>/<Name>.txt` (StoneScript source)
- Sheet list: `share/audits/animation-frame-paths.txt`
- Conventions: `#` converted to space, rows right-trimmed. Size = rows x max cols. A sheet that contains `%%` separators is a `ui.AddAnim` frame strip: `fN` = the Nth `%%`-separated frame inside that sheet. Composite frames (part layers drawn over a base block at the script's shared origin) are marked `A+B`.
- Cell diffs were counted with a throwaway script (row/col 1-based, after `#`->space); every verdict and edit is a manual judgement after viewing the art.
- Width note: `´ ° ¯ ‾ ─ │ ☆ ● ♥` etc. are East-Asian-Ambiguous width: single-width in Western monospace fonts, double in a terminal with `ambiwidth=double`. Flagged per set. `´` is the most common one here; a tutor copy can swap `´` -> `'` with no loss.

## official-Pets/Boo

- Sheets viewed: res01, res02, res03, res04, res05 (all listed). Every sheet is a `%%` frame strip.
- Source: `~/Downloads/stone-story-official/Pets/Boo.txt`
- Script structure: one panel; each block is `ui.AddAnim(...)` added at x=0 and a row offset `y`: res01 body y=0 dur 40 loop; res02 eyes y=1 dur 30 one-shot (played every 180 frames = blink); res03 mouth y=2 dur 156 loop (played only while quipping); res04 tail y=3 dur 18 loop; res05 sleep overlay y=0 dur 60 loop (visible when idle 150 frames). res06 `^_^` happy eyes (unlisted, 2 rows).
- Depicts: a small ghost pet. res01 = body hover (4 frames, 10 ticks each), res02 = blink (6 frames x 5 ticks: `o o`,`= =`,`- -`,`- -`,`= =`,`o o`), res03 = talking mouth (13 frames x 12 ticks, 1 cell), res04 = trailing tail swish (6 frames x 3 ticks), res05 = sleeping face with drifting `Z z` (4 frames x 15 ticks).
- Sizes: res01 3x7 (IDEAL); res02 1x5 (part layer); res03 1x4 (part layer); res04 2x6 (part layer); res05 3x11 (IDEAL). Composite body+eyes+tail = 5x7 (IDEAL).
- Glyphs: `´` (ambiguous, swap to `'`), `°` (ambiguous).
- Diffs:
  - res01 f1->f2: 6 cells (row2 col1,7 `_` added; row3 cols1,2,6,7 `-´`->`` `. `` and `` `- ``->`.´`). Edit: `2G0r_$r_` then `3G0R`.<Esc>$hR.´<Esc>`.
  - res01 f3->f4: 4 cells (row3 `-´   `-` -> ` /   \`). Edit: `3G0R /<Esc>$hR\ <Esc>` — the skirt folds in (squash/stretch of a hover).
  - res02 f1->f2 (over body row2): 2 cells `o o` -> `= =`. Edit: `:2s/o o/= =/`; f2->f3 `:2s/=/-/g`.
  - res04 f1->f2: 4 cells (row1 `)`->`\`, `/`->`(`; row2 `´`->`-`, `´` appended). Edit: `1G0f)r\f/r(` then `2G$r-a´<Esc>`.
  - res05 f1->f2: 5 cells (Z/z shift right 2 cols, `°`->`O` snore mouth). Edit: `1GI  <Esc>` (insert two leading spaces, the Zz drift right) then `3G0f°rO`.
- Tutor fit: res01 hover is a 3-row loop with a readable 4–6-cell change: M0 Spark loop or M9 Bounce capstone (f3->f4 skirt fold = squash). res02 blink on the body contour is a textbook M2 Face focus (`ci(`/`:s` inside a stable `( )`). Composite body+eyes+tail (5x7) gives M8 Walk study a secondary-motion subject (tail drags behind hover). res05 sleep suits M7 Timed build (holds: 15-tick frames).
- Verdict: **USE** — best slot M2 Face focus (body+blink composite, 3–4 rows, eyes inside stable parens); also M0/M9 (res01), M8 (composite with res04 tail).

```
res01 f1        res01 f2        res01 f3        res01 f4
  .-.             .-.             .-.             .-.
 (   )          _(   )_          (   )           (   )
-´   `-         `.   .´         -´   `-           /   \
```

```
res02 f1..f6 (eyes, drawn at row 2 of res01)
  o o   |   = =   |   - -   |   - -   |   = =   |   o o
```

```
Composite res01 f1 + res02 f1 + res04 f1 (M2 / M8 candidate, 5x7)
  .-.
 (o o)
-´   `-
,_) /
 `-´
```

```
res04 f1..f6 (tail, drawn at row 4)
,_) /    ,_\ (     ,\ (      \ (      ) /     ,) /
 `-´      `--´      `--'      '-'     '-'     '-´
```

```
res05 f1          res05 f2
     Z  z               Z  z
  - -             - -
   °                O
```

## official-Hats/StarCloak

- Sheets viewed: res01, res02 (all listed).
- Source: `~/Downloads/stone-story-official/Hats/StarCloak.txt`
- Script: `Draw()` picks res01 when `bighead` else res02, both at `>h-3,-2`; a `☆` is overprinted at `-2,-1` coloured by star count. No time condition.
- Depicts: a hooded cloak with a face `^.^`. Two variants, not frames: they differ in 2 cells (row3 `(   )` vs `( '')`).
- Size: 6x7 each (IDEAL).
- Glyphs: `´` (ambiguous), `☆` overprint (ambiguous/wide in CJK fonts — drop it).
- Diff res01->res02: 2 cells, row3 cols 4-5 `  ` -> `''`. Edit: `3G0f(llR''<Esc>`.
- Tutor fit: not an animation; could illustrate M14 Variant palette (two register variants of one still) but the change is too small to carry that lesson.
- Verdict: **REJECT** — not an animation (state variant, 2-cell difference).

## official-Weapons/Scythe

- Sheets viewed: res05, res07 (listed). Also opened the unlisted res01-04, res06, res08-10 to understand the script (they are 1-3-row player/weapon layers).
- Source: `~/Downloads/stone-story-official/Weapons/Scythe.txt`
- Script: all blocks keyed on `item.right = "bardiche"` and `item.right.state`. state=1: player stick-figure res01 (standing) or a walk loop res02/res03/res04 by `time % 15` (0-5, 6-10, 11-14 = 5 ticks each) at `>o-1,1`; scythe res05 at `>o0,-2`. state 2/4 (attack): player res06 at `>o-1,1`, scythe swing res07 at `>o-4,-4`. state 3: res08 player + res09/res10 ground slash.
- Depicts: res05 = scythe held upright (blade `_╤__` / `¯-╬-¯¯¯`` on a `║` shaft); res07 = the same scythe swung diagonal (blade top-right, shaft `/X` / `'/ \` running down-left). Two extremes of one weapon rotation, different origins (0,-2 vs -4,-4).
- Sizes: res05 6x8 (IDEAL); res07 7x7 (IDEAL). Unlisted walk frames res01-04 3x3.
- Glyphs: `╤ ╬ ║ ¯` (all ambiguous). `║` could become `|`, `╬` `+`, `╤` `T`, `¯` `-` for a safe copy.
- Diff res05->res07: 26+ cells, whole redraw (rotation ~45 degrees); no minimal edit. Walk loop (unlisted) res02->res03: 3 cells, row3 `/ >` -> ` >\`, edit `3G0R >\<Esc>`; res03->res04: 2 cells (`>`->`X`, `\`->space), edit `3G0lRX <Esc>`.
- Tutor fit: res05/res07 are two rotation extremes around a hand pivot — raw material for M4 Rotation tween (student draws the midpoint), but at 6-7 rows not 3, the pivot is not at a stable cell (origins differ by 4,2), and the glyphs need ASCII substitution. The 3x3 walk loop is too small for M8 (5 rows).
- Verdict: **MAYBE** — M4 Rotation tween extremes only after an ASCII-safe re-render and origin alignment; not usable as-is.

```
res05 (held, origin 0,-2)   res07 (swing, origin -4,-4)
 _╤__                          __
¯-╬-¯¯¯`                     \//¯¯`
  ║                          /X
  ║                         '/ \
  ║                             \
  '                              \
                                  `
```

```
Unlisted walk loop res01 | res02 | res03 | res04 (player, 3x3)
  O      O      O      O
 /´     /´     /´     /´
/ \    / >     >\     X
```

## official-UI/CDTime

- Sheets viewed: res01, res02 (all listed).
- Source: `~/Downloads/stone-story-official/UI/CDTime.txt`
- Script: cooldown-time HUD window. res01 = English window chrome (`╔═══ CD Time ═══╗` with labels PT/BD/HC/DS/BS/MS/QS), res02 = the Chinese-label version, chosen by `CDTimeShow` vs `CDTimeShowCHS`. Text fields are filled at runtime.
- Size: 5x17 each.
- Glyphs: `╔ ═ ╗ ║` (ambiguous); res02 contains CJK wide ideographs (药水, 冷却时间 …) — breaks a fixed-width buffer.
- Diff: labels only; not frames.
- Verdict: **REJECT** — UI (static HUD chrome, language variants), res02 has East-Asian-wide glyphs.

## official-Games/Arena

- Sheets viewed: res08, res09 (all listed).
- Source: `~/Downloads/stone-story-official/Games/Arena.txt`
- Script: `var arena = res08` is a tile map read with `string.Sub(arena, datapos, 2)` (2-char codes WL wall, EM empty, MF, PL); `var uiback = res09` is the inventory/UI border drawn with `ui.AddAnim(uiback)` (layout also shown in a comment block).
- Sizes: res08 17x34; res09 25x86 (TOO-LARGE).
- Glyphs: res09 full of box drawing `─│┌┐└┘├┤┬┴═║╔╗╚╝╞╡╪` (ambiguous).
- Verdict: **REJECT** — res08 is level data, not art; res09 is UI chrome; neither is an animation.

## official-Cosmetics/ChristmasTree

- Sheets viewed: res01, res03 (all listed). Opened the source to see res02 star, res04 trunk, res05 roots, res06 pot, res07 fog.
- Source: `~/Downloads/stone-story-official/Cosmetics/ChristmasTree.txt`
- Script: each frame draws tree res01 at `(rx-4, ry-12)`, star res02 at the same origin in `#rainFF`, lights res03 at `(rx-4, ry-8)` in a rainbow colour, and a location-chosen base (trunk/roots/pot/fog) at `(rx-4, ry-3)`. No time condition: the only motion is the engine's rainbow colour cycle.
- Depicts: a decorated pine tree (11x9) and a separate lights layer of `o` and `°` (5x8) laid over the tree's lower half.
- Sizes: res01 11x9 (TOO-LARGE by rows, crop impossible without losing the tree); res03 5x8.
- Glyphs: res01 uses `λ ☆ • ´ · ‘ ’ ¡` — many ambiguous; `☆ •` risky.
- Diff: n/a (no frames). The tree+lights overlay is a layering example, not an animation.
- Verdict: **REJECT** — not an animation (static layers with colour cycling); also 11 rows and heavy ambiguous glyph use.

## official-Games/PlayingCards

- Sheets viewed: res01, res02, res03 (all listed).
- Source: `~/Downloads/stone-story-official/Games/PlayingCards.txt`
- Script: library. `Draw` prints `cardFront` res01 and overprints value + suit glyph (`♥ ♦ ♣ ♠`); `DrawBack` prints res02 (`::` fill); `DrawCompact` uses res03 (3-col top). No timing.
- Sizes: 4x4 each (IDEAL).
- Glyphs: `│ ‾` (ambiguous); suits `♥♦♣♠` (ambiguous).
- Diff res01->res02: 4 cells (`  ` -> `::` on rows 2-3). Edit `2G0lR::<Esc>j0lR::<Esc>` or `<C-v>` block `2G0l<C-v>jlr:`.
- Tutor fit: front/back is a "card flip" only if the tutor adds in-between frames; the source never animates it.
- Verdict: **REJECT** — UI/library still, not an animation.

## official-Cosmetics/Pumpkins

- Sheets viewed: res01, res02, res03 (all listed).
- Source: `~/Downloads/stone-story-official/Cosmetics/Pumpkins.txt`
- Script: `ui.AddAnim(PumpkinArt)` is `Stop()`ped and given a random `frame = Rand(0,2)`; stem res03 and face res02 are `AddLayer` layers with pivots (-2,1) and (-2,-1) and random frames `Rand(0,50)` (clamped). So the `%%` strips are a **variant palette picked at random**, never played in time order.
- Depicts: res01 = 3 pumpkin body shapes (3x7); res02 = 27 carved faces (1x3: `` `~´ ``, `°^°`, `O_O`, `'u'`, `$o$`, `q~q`, …); res03 = 9 stem/vine curls (2x2-3).
- Sizes: body 3x7 IDEAL; face 1x3; stem 2x3. Composite body+face = 3x7.
- Glyphs: `´ °` ambiguous; res02 also `▼ ❤ ▄ ε Θ ì í ò ó` (ambiguous or wide — the `❤` faces must be dropped). ASCII-safe faces: `O_O`, `O~O`, `@.@`, `@~@`, `'u'`, `q~q`, `$o$`.
- Diffs: body f1->f2 10 cells (rim `.'` ´'.` -> ` .- -.`, sides `\ /` -> `{ }`); face swaps 1-3 cells, e.g. `O_O`->`O~O` = 1 cell: `2G0f_r~`; `@.@`->`O_O` = 3 cells: `:2s/@.@/O_O/`.
- Tutor fit: this is exactly a variant palette — one contour, many interchangeable features — M14 Variant palette (yank faces into registers `"a`..`"e` and paste into the body with `"ap`/`vi` replace). Also M2 Face focus (face inside a stable rind). Not a time animation.
- Verdict: **MAYBE** — strong M14 fit as a variant sheet (3x7, ASCII-safe after dropping `´`/`❤` faces), but it is not an animation sequence; body is 3 rows vs M14's 4.

```
res01 body f1..f3 (with res02 face composited on row 2, cols 3-5)
.'` ´'.     .- -.     .'` ´'.
\ O_O /    { @.@ }    i 'u' ;
 `´'`´      `-'-´      `´'`´
```

```
res02 ASCII-safe faces (1x3): O_O  O~O  @.@  @~@  'u'  q~q  $o$  °^°  °_°
```

## official-Pets/BlackHole

- Sheets viewed: res01, res02, res06, res07 (all listed). Also res03 (2-row eyes), for the composite.
- Source: `~/Downloads/stone-story-official/Pets/BlackHole.txt`
- Script: `blackHole = ui.AddAnim(holeAsci1)` (res01) with ring layer `blackHole.AddLayer(holeAsci2)` (res02, rainbow). The frame is **set by level**: `holeSize` 1..5 -> `frame = 0..4` (grows as kills accumulate; `HoleXP`). At size 5 the eyes res03 are added at (+2,-1). res06 (`╔═╗ ║ ║ … ╚═╝`, 12x3) is the XP bar drawn at `` >`0,9 ``. res07 `holeGun` is declared and never drawn.
- Depicts: res01 = a singularity growing in 5 stages: `Φ` -> `(_)` -> `.-.( )`-´` -> a 4-row ring -> a 6-row ring with `¡ !` sparkle edges; res02 = an accretion streak (`\`, `¯-_`) that lengthens in step. res07 = an unused 3-stage unfolding turret (`──┬──`, `╧Φ╧{`).
- Sizes (shared canvas, blank top rows kept): res01 f1 5x8 … f5 8x14 (ACCEPTABLE; content of f1-f4 fits rows 3-6, f5 rows 1-8); res02 f2-f5 up to 7x14; res06 12x3 (UI); res07 3x5 .. 5x8.
- Glyphs: `Φ ¯ ´ ¡` (ambiguous) in res01; res07 is box-drawing throughout (`─ ┬ ╒ ╕ ╧ ╞ ╡ │ ┴`).
- Diffs (res01): f1->f2 5 cells (`Φ` -> `(_)`/`¯`), edit `5G7|R( )<Esc>` (Φ becomes the ring sides) then `4GS       _<Esc>` and `6GS       ¯<Esc>` (rows 4/6 are blank, so `S` rather than `r`). f2->f3 10 cells (the ring widens one column each side: `(_)`->`.-.`/`( )`/`` `-´ ``). f3->f4 21 cells, f4->f5 44 cells: whole redraws.
- Tutor fit: a scale-up sequence at a fixed centre. Played backwards (f5->f1) it is subtractive authoring: draw the big ring, then delete/replace to shrink — M6 Pyramid build ("subtractive authoring and playback order"). f1-f3 (4 rows once blank rows are cropped) fit M6's 5-row budget; f4-f5 do not without cropping.
- Verdict: **MAYBE** — M6 Pyramid build (f1->f3 growth, or authored in reverse), after replacing `Φ ¯ ´`; f4/f5 steps are too large for a bounded edit. res06 (UI bar) and res07 (unused, box glyphs) REJECT.

```
res01 f1..f5 on the shared 8-row canvas (top-aligned; f1-f4 use rows 3-6 only)
f1              f2              f3              f4              f5
                                                                      __
                                                                  .-¯¯  ¯¯-.
                                                    .-¯¯-.       ¡          ¡
                       _              .-.          .      .     .            .
       Φ              ( )            (   )         '      '     '            '
                       ¯              `-´           `-__-´       !          !
                                                                  '-__  __-'
                                                                      ¯¯
```

## official-Weapons/EmbueDaggers

- Sheets viewed: res08, res10, res12, res22, res24, res26 (all listed).
- Source: `~/Downloads/stone-story-official/Weapons/EmbueDaggers.txt` (header says "Rf : Sword", imports `Components/OVERHAUL`).
- Script: per hand (`base.IR` right / `base.IL` left) and state `IRS`/`ILS` 1-4 with timers `IRT <= 3/6/9`, a white player layer (odd res) and a coloured weapon layer (even res) are drawn at `>o` offsets. The listed sheets are the state-3 weapon layers for timer windows 0-3, 4-6, 7-9, drawn at offsets (2,1), (2,2), (2,1) (right) and (-2,1), (-2,2), (-2,1) (left).
- Depicts: a 4-row dagger/sword glyph column `,` / `@base.IRI@.` / `|/` / `'` whose middle row is a **runtime string interpolation** (`@base.IRI@` / `@base.ILI@`, the item icon). All three right-hand sheets are byte-identical after `#`->space; the left-hand three likewise. The motion comes only from the draw offset jumping one row.
- Size: 4x11 as text (the real rendered width depends on the interpolated icon).
- Diff res08->res10: 0 cells (identical); res08->res22: 1 cell (`R`->`L` inside the variable name).
- Verdict: **REJECT** — frames identical (motion is an offset change), and the art contains a runtime `@var@` placeholder.

## official-Cosmetics/Beach

- Sheets viewed: res01, res02, res03, res04, res05, res06 (all listed).
- Source: `~/Downloads/stone-story-official/Cosmetics/Beach.txt`
- Script (only at `loc = waterfall`): res01 towel `>c-5,-2` and res02 shoreline `>c0,-12` static; res03 static corner sign `` >`85,0 `` yellow; res04 `sandC = ui.AddAnim` dur 100 loop at x=-20 (3 frames ≈ 33 ticks each); res05 `ball = ui.AddAnim` dur 40 loop at x=35 (13 frames ≈ 3 ticks each); res06 `vb = ui.AddAnim` dur 40 loop at x=-30,y=10 (11 frames ≈ 3.6 ticks each).
- Frame alignment: frames inside res05/res06 have 4-6 rows; bottom-aligning them keeps the ground row and net fixed (inferred: ground-row/net continuity; the engine's anim anchor was not checked). res04 reads correctly top-aligned (head row fixed).
- Depicts: res04 = a kid with a shovel building a sandcastle (`,',` bucket -> `_~_` with sand flicks `^` -> `_•_`/`|O|` castle). res05 = two people tossing a beach ball `o` (one gets up from lying `(O-o` in f1-f3, the ball arcs back and forth, `!` surprise, `•` splash). res06 = beach volleyball over a net `\ \ / ||| / ||`: set-up (f1-f2), serve (f3), ball `O` arcs over the net f3->f6 with widening spacing (cols 9,10,13,17), receiver bumps (f7-f9 arms `=\`->`\\`->`=|`), return (f9-f11).
- Sizes: res01 5x12, res02 25x24 (TOO-LARGE, static), res03 4x6 (static); res04 4x8 (IDEAL); res05 5x20 (IDEAL, bottom-aligned); res06 5x24 (IDEAL, bottom-aligned; two frames side by side = 50 cols, fits 80).
- Glyphs: res04 `•` (ambiguous); res05 `—` (ambiguous, swap to `-`) and `•`; res06 pure ASCII.
- Diffs (bottom-aligned 5-row canvas, row/col 1-based):
  - res06 f3->f4: 2 cells, ball `O` row1 col9 -> col10. Edit: `1G9|r 10|rO`.
  - res06 f4->f5: 2 cells, row1 col10 -> col13. Edit: `1G10|r 13|rO`.
  - res06 f5->f6: 2 cells, row1 col13 -> col17. Edit: `1G13|r 17|rO` (spacing 1,3,4 = the ball speeding up).
  - res06 f6->f7: 2 cells, ball drops to row3 col20 beside the receiver. Edit: `1G17|r 3G20|rO`.
  - res06 f7->f8: 5 cells (receiver steps under: row3 `O O` at cols 20/22 -> `O   O` at cols 19/23; arms row4 col22 `=`->`\`). Edit: `3G19|RO   O<Esc>4G22|r\`.
  - res05 f9->f10: 3 cells (ball `o` row1 col8 -> col7; splash row2 col14 `•`->`.`). Edit: `1G8|r 7|ro2G14|r.`.
  - res04 f1->f2 (top-aligned): 7 cells (shovel `O`->`O_`, bucket `,',`->`_~_`, sand `^` on rows 3-4). Edit: `1GA_<Esc>2G5|R_~_<Esc>3GA^<Esc>` then `o   ^<Esc>` (row 4 is new).
- Tutor fit: res06 is the strongest find here — a readable ball arc with 2-cell steps and accelerating spacing, stable net and players: M9 Bounce capstone (plan the arc, keyframe serve/receive, tween the spacing), 5 rows vs M9's 3 (crop impossible: players need rows 3-5), so alternatively M7 Timed build (5 rows: dot-repeat the ball move, macro over frames) or M16 Key-pose plan (5 rows: `:t` copy frame, `<C-a>` frame labels). res05 fits M17 Coherent anchors (`/o` + `n` to find the ball each frame). res04 fits M7 Timed build (a literal build, 33-tick holds).
- Verdict: **USE** — res06 f3..f11 for M9 (or M7/M16 at 5 rows); res05 MAYBE (needs `—`->`-`); res04 MAYBE (M7, `•`->`o`); res01-03 REJECT (static scenery, res02 too large).


```
res06 f3..f6 (bottom-aligned, 5x24): serve, ball crosses the net
f3                        f4                        f5                        f6
        O                          O                            O                                O
         \ \                       \ \                       \ \                       \ \
 O       |||         O     O       |||         O     O       |||         O     O       |||         O
 |/       ||         =\    |/       ||         =\    |/       ||         =\    |/       ||         =\
/ \                  / \  / \                  / \  / \                  / \  / \                  / \
```

## official-Cosmetics/StoneClause

- Sheets viewed: res03, res04, res05, res06, res07, res08, res09, res10 (all listed).
- Source: `~/Downloads/stone-story-official/Cosmetics/StoneClause.txt`
- Script: static layers drawn relative to the player: res03 sleigh runner `h-8,-1` red, res04 reins/sleigh line `h-8,-1` gold, res05 sack `h-20,0` dark red (res01/res02 = Santa hat, unlisted). The reindeer are `animframes = [res06, res07, res08, res09, res10]` drawn at `h-17,-1`, index advancing when `totaltime % 7 = 0` (7 ticks per frame, 5-frame loop).
- Depicts: two reindeer heads `☺` with antler `┴` and a neck `)`/`¯`. After `#`->space and right-trim, res06 = res07 = res09 = res10 (they differ only in trailing `#`/space count); only res08 adds a hoof row `v  v`. So the "gallop" is a 1-in-5 blip of 2 cells.
- Sizes: res03 4x16, res04 6x18, res05 4x8, res06-10 4x13 (res08 5x13). Assembled sleigh scene ≈ 6x26.
- Glyphs: `☺ ┴ ¯ – ´` — `☺` is ambiguous/emoji-prone and is the reindeer head, so the art does not survive ASCII substitution well (`@` would work).
- Diff res07->res08: 2 cells (row5 cols 7,10 `v`). Edit `o      v  v<Esc>` (new row) — nothing else changes.
- Verdict: **REJECT** — frames effectively identical (4 of 5 identical, one adds 2 hoof cells); heads are `☺`.

## official-Games/KillerRPG

- Sheets viewed: res01, res02, res03, res04, res05, res06, res07 (all listed).
- Source: `~/Downloads/stone-story-official/Games/KillerRPG.txt`
- Script: arrays of UI panels chosen by menu/language state: `Rt[0|1]` = res01/res02 REWARDS frames (12x28 / 8x28) drawn at `` >`30,6 ``; `help[0|1]` = res03/res04 help text (English/Portuguese) at `` >`xH,yH ``; `MarketAscii[0|1]` = res05 potion market (11x45) and res06 mutagen lab (13x45); `SearchAscii[0]` = res07 offline-search text (10x29).
- Depicts: windows, tables and paragraphs of text; no characters or motion.
- Sizes: res01 12x28, res02 8x28, res03 92x59, res04 89x51, res05 11x45, res06 13x45, res07 10x29 — all TOO-LARGE or text.
- Glyphs: `— © « » ± ∞ • × ＂` (`＂` is full-width = East-Asian-wide), Portuguese accents in res04.
- Verdict: **REJECT** — UI panels and help text, not animation.

## official-Cosmetics/Fireworks

- Sheets viewed: res01, res02, res03, res04, res05, res06, res07 (all listed). All are `%%` frame strips (some separators carry a comment, `%% //Start fade`; counted as separators).
- Source: `~/Downloads/stone-story-official/Cosmetics/Fireworks.txt`
- Script: `rings`=res01, `rfade`=res02, `willow`=res03, `wfade`=res04, `wcrackle`=res05, `dahlia`=res06, `dfade`=res07. Each firework = a burst anim (`duration 10`, 7 frames ≈ 1.4 ticks each, one-shot) on an 11x5 panel (dahlia 11x7), then when `bframe >= 6` the burst is hidden and the fade anim plays on the same panel/origin (rfade dur 15, wfade dur 30, wcrackle dur 40, dfade dur 40; ~11 frames). During the fade, odd frames move the panel down `fallstep` rows (embers sink). Style is random: willow -> wfade or wcrackle (50/50), rings -> rfade, dahlia -> dfade. One random colour per firework.
- Depicts: three shell types — willow (`*` star opening into a drooping `' . ·` canopy), rings (concentric `: • ·` rings), dahlia (`¡ ! — \ /` spokes + rings). Fades erase from the **centre outward** (the star dies first, the outer ring last); wcrackle is a 4-texture shimmer loop (frames labelled //1..//4 in the source).
- Sizes: willow/rings/wcrackle 5x11 (IDEAL); dahlia/dfade 7x11 (IDEAL). Fixed panel, frames top-aligned (verified: blank top rows are kept in the sheet).
- Glyphs: willow uses `·` (U+00B7, ambiguous) — swap `·` -> `,` for a safe copy; rings add `•` (swap -> `o`); dahlia adds `¡ —` (swap -> `!`, `-`). wcrackle `·` only.
- Diffs:
  - willow res03 f1->f2: 8 cells (`*` gains a 3x3 shell `.'.` / `·*·` / `'.'`). Edit: `1G5|R.'.<Esc>2G5|R·*·<Esc>3G5|R'.'<Esc>` (or yank a 3-cell shell pattern).
  - willow res03 f5->f6: 4 cells (outer droplets row2 col1/11 `·`, row4 col1/11 `'`). Rows 2 and 4 are 9 cols wide in f5, so col 11 is appended: `2G1|r·A ·<Esc>4G1|r'A '<Esc>`.
  - willow res04 f3->f4 (fade start): 8 cells, the 3x3 centre goes blank. Edit: `1G5|<C-v>2j2lr ` (one block replace).
  - willow res04 f4->f5: 4 cells, cols 4 and 8 on rows 1-2. Edit: `1G4|<C-v>jr 1G8|<C-v>jr `.
  - rings res01 f2->f3: 4 cells (`*` gains `.` above, `•` left/right, `'` below). Edit: `2G6|r.3G5|r•7|r•4G6|r'`.
  - rings res02 f7->f8: 2 cells (row3 cols 3,9 `•` -> space). Edit: `3G3|r 9|r `.
  - dahlia res06 f1->f2: 4 cells (`¡` above, `-` either side, `!` below the star). Edit: `3G6|r¡4G5|r-7|r-5G6|r!`.
- Tutor fit: M6 Pyramid build ("subtractive authoring and playback order") is an exact match: 5-row frames, the burst is additive and the fade is literally subtractive, and the playback order (burst forward, fade from centre out) is the lesson. The `<C-v>` block-blank of the fade also serves M5 (negative space). wcrackle (16-18 cells/frame) is a texture shimmer for M13/M15 but too many cells per step for a bounded edit.
- Verdict: **USE** — willow res03+res04 (5x11) for M6 Pyramid build; rings res01+res02 as the alternate M6 set; dahlia MAYBE (7 rows, more ambiguous glyphs); wcrackle MAYBE (M15 texture reference only).

```
willow burst res03 f1..f7 (5x11, top-aligned panel)
                 .'.         '.'.'       ''.'.''     .''.'.''.    .''.'.''.    .''.'.''.
     *           ·*·         ··*··       .··*··.      .··*··.    · .··*··. ·  · .··*··. ·
                 '.'         .'.'.        .'.'.      ' .'.'. '    ' .'.'. '   '' .'.'. ''
                                         ·  .  ·      ·  .  ·    ' ·  .  · '  ' ·  .  · '
                                                      '  .  '      '  .  '      '  .  '
```

```
willow fade res04 f3..f10 (f1-f2 hold the full burst; f11 blank)
 .''.'.''.    .''   ''.    .'     '.    .       .
· .·· ··. ·  · .·   ·. ·  · .     . ·  ·         ·  ·         ·
'' .'.'. ''  '' .   . ''  '' .   . ''  ''       ''  '         '  '         '
' ·  .  · '  ' ·  .  · '  ' ·  .  · '  ' ·  .  · '  ' ·  .  · '  '         '
  '  .  '      '  .  '      '  .  '      '  .  '      '  .  '      '  .  '      '  .  '         .
```

```
rings burst res01 f2..f7 (f1 blank) and fade res02 f3..f9
                                         •         . • .       .·•·.
                 .          ·:·        .·:·.      '.·:·.'     '.·:·.'
     *          •*•        :•*•:      •:•*•:•     •:•*•:•    :•:•*•:•:
                 '          ·:·        '·:·'      .'·:·'.     .'·:·'.
                                         •         ' • '       '·•·'

   .·•·.       .·•·.       .·•·.       .·•·.       .·•·.       .·•·.        · ·
  '.·:·.'     '.·:·.'     '.·'·.'     '.   .'     '     '     '     '
 :•:•*•:•:   :•:• •:•:   :•:   :•:   :•     •:   :•     •:   :       :   :       :
  .'·:·'.     .'·:·'.     .'·.·'.     .'   '.     .     .     .     .
   '·•·'       '·•·'       '·•·'       '·•·'       '·•·'       '·•·'        · ·
```

## official-UI/FaceHUD

- Sheets viewed: res01, res02, res03, res04, res05, res06, res07, res08, res09, res10, res11, res12 (all listed).
- Source: `~/Downloads/stone-story-official/UI/FaceHUD.txt` ("Doom Style Face HUD").
- Script: res01 = frame box `╔═╗` at `` >`screen.w-13,0 ``. Faces res02-res09 are all drawn at the same origin `` >`screen.w-13,1 `` and selected by `fstate`: neutral res02, scowl res03 (foe within 30), blink res04 (`(time/4) % 45 > 40` = 20 of every 180 ticks), raised-eyebrow-right res05 / left res06 (idle look-around: `(time/32) % 3` cycles rer -> neutral -> rel, 32 ticks each, during half of every 320-tick cycle), grin res07 (foe below 25% HP, held 60 ticks), shock res08 (lost >= 15% max HP), dead res09. Wound overlays res10/res11/res12 drawn in red at the same origin below 90/60/30% HP, on top of the face.
- Depicts: a Doom-style player face: stable head outline (rows 1 and 6, the `/ \` and `\ /` cheeks), expressive brows (row 2), eyes (row 3), mouth (rows 4-5).
- Sizes: faces 6x12 (IDEAL); rows 2-5 crop = 4x12 (IDEAL, keeps the cheek contour). Frame res01 8x13 (UI). Wounds 5x9 / 6x9 / 6x10 (part layers).
- Glyphs: `´` and `—` (em dash, ambiguous) appear in most faces — swap `—` -> `-` and `´` -> `'` for the tutor; res11/res12 wounds use `▀ ▄ █` (ambiguous block elements). res01 box-drawing.
- Identity note: res04 (blink) and res09 (dead) are byte-identical after `#`->space.
- Diffs (all at the same origin):
  - neutral res02 -> blink res04: 6 cells, row3 `<o) (o>` -> `` `—   —´ ``. Edit (ASCII copy): `3G4|R`-   -'<Esc>`; or M2 grammar `3G0f<c7l`-   -'<Esc>`.
  - neutral res02 -> look-right res05: 7 cells (pupils shift `<o)`->`<_o`, `(o>`->`(_o`; right brow lifts `__ `->`.——`). Edit: `3G5|R_o<Esc>9|R_o<Esc>` (4 cells) then `2G8|R.--<Esc>`.
  - neutral res02 -> look-left res06: 7 cells (mirror: `<o)`->`o_)`, left brow `__ `->`——.`). Edit: `3G4|Ro_<Esc>8|Ro_<Esc>2G4|R--.<Esc>`.
  - scowl res03 -> grin res07: 6 cells (brow corners `.`->`_`, mouth `´———``->`` `———´ ``, teeth line widens). Edit: `2G4|r_10|r_4G5|r_A_<Esc>5G5|r`9|r'` (row 4 is 8 cols, so the 9th `_` is appended).
  - neutral res02 -> shock res08: 19 cells (whole face) — not a bounded edit.
- Tutor fit: this is the best face set in the batch. M3 Pose copy (6 rows, "duplicate a whole key pose and change one acting feature": `yy`/`6yy` the neutral face, change only the eyes = blink, or only brow+pupils = look). M2 Face focus with the rows 2-5 crop (4x12): `c`/`R` inside a stable cheek contour; shock `(o) (o)` supports `ci(`. The rer/neutral/rel cycle is also a mirror pair for M18 Hand-mirrored return (4 rows cropped). Wounds res10-12 over the face = M5 Layered scene (but `▀▄█` glyphs).
- Verdict: **USE** — M3 Pose copy (neutral -> blink, 6 cells) and M2 Face focus (4-row crop); M18 for the rer/rel mirror pair.

```
res02 neutral  res04 blink   res05 look R  res06 look L  res03 scowl   res07 grin    res08 shock
  .'     `.     .'     `.     .'     `.     .'     `.     .'     `.     .'     `.     .' ._. `.
 / __   __ \   / __   __ \   / __  .—— \   / ——.  __ \   / ._`-´_. \   / __`-´__ \   / ——. .—— \
   <o) (o>       `—   —´       <_o (_o       o_) o_>       <o\ /o>       <o\ /o>       (o) (o)
                                                             ___          _____          ___
 \   ———   /   \   ———   /   \   ———   /   \   ———   /   \  ´———`  /   \  `———´  /   \  /___\  /
  `._   _.´     `._   _.´     `._   _.´     `._   _.´     `._   _.´     `._   _.´     `._   _.´
```

## official-Pets/Crab

- Sheets viewed: res01, res02, res10, res11, res12, res13, res14, res15, res16, res17 (all listed). Unlisted res03-09 and res18-23 are 1-2-cell face/mandible overlays drawn at (x+2, y+3); read in the source only.
- Source: `~/Downloads/stone-story-official/Pets/Crab.txt`
- Script: two layers at the same origin `>o@myX@,@myZ@`: a red body/legs block (odd listed res) and a yellow shell block (even listed res). Idle = res01 + res02. Scuttle (`currentState = stateScuttle`, started when the player walks away, lasts `stateTime` 0-11) = 4 frames chosen by `stateTime/3` = 0,1,2,3 -> (res10+res11), (res12+res13), (res14+res15), (res16+res17): 3 ticks per frame, then back to idle. The body's `{Oo}` face shows through the gap in the shell's bottom row.
- Depicts: a hermit crab — a stacked shell `__ / (__)_ / (_____)_ / (__{Oo}_)` over legs `//(;;)\`. In the scuttle the legs alternate (`>/ … |`, `\> … /`, `|\ … >`, `/| … \`) and the shell sways one column left/right a beat behind (secondary motion).
- Sizes: body 5x9 (rows 1-3 blank), shell 4x10; composite 5x10 (IDEAL). Pure ASCII.
- Diffs (composites; all frames 5 rows):
  - idle -> s1: 7 cells (shell rows 2-3 shift, legs row5 `/`->`>`, `\`->`|`).
  - s1 -> s2: 9 cells = shell sway 6 (rows 1-2) + legs 3 (row5 cols 3,4,9 `>/`…`|` -> `\>`…`/`). Legs-only edit: `5G3|R\><Esc>9|r/`.
  - s2 -> s3: 9 cells = shell 6 (rows 2-3) + legs 3. Legs-only edit: `5G3|R|\<Esc>9|r>`.
  - s3 -> s4: 9 cells; legs `5G3|R/|<Esc>9|r\`.
  - s4 -> s1 (loop): 8 cells; legs `5G3|R>/<Esc>9|r|`.
  - Shell sway alone, s1 -> s2 rows 1-2 (shell top shifts right one column): `1GI <Esc>2GI <Esc>$x`.
- Tutor fit: M8 Walk study — exact 5-row budget, equal frame height, clear contact alternation on one row (3-cell leg edits) and a lagging secondary motion (the shell). Also M12 Joint sweep for the legs (`t(`/`f)` on row 5: `5G0t(` lands on the leg cell before the body).
- Verdict: **USE** — M8 Walk study (idle + 4 scuttle composites, 5x10 ASCII).

```
idle res01+02    s1 res10+11      s2 res12+13      s3 res14+15      s4 res16+17
   __               __                __               __              __
  (__)_            (__)__            (__)_           _(__)            (__)_
 (_____)_          (_____)          (_____)         (_____)_         (_____)_
 (__{Oo}_)        (__{Oo}_)        (__{Oo}_)        (__{Oo}_)        (__{Oo}_)
  //(;;)\          >/(;;)|          \>(;;)/          |\(;;)>          /|(;;)\
```

## official-Cosmetics/AcronianGuardian

- Sheets viewed: res06, res07, res08, res09, res10, res11, res12, res13, res20, res23, res25, res31 (all listed). Unlisted res14-19 (wing tips), res21/22/24/26/27 (pupil/blink), res32-38 (attack FX) read in the source only.
- Source: `~/Downloads/stone-story-official/Cosmetics/AcronianGuardian.txt`
- Script: a winged floating eye replacing the player. Wing flap = `time % 40` in four 10-tick windows. Left wing res06/res07/res08/res09 at `>o-15,-4 / -5 / -4 / -3`; right wing res10/res11/res12/res13 at `>o5,-4 / 4,-5 / 4,-4 / 5,-3` (the vertical offset is part of the flap: up, down, settle). `EH` drops the eye 1 row in the downstroke window. Eye body at `>o-4,-2+EH`: res20 normal, res23 boss/berserk far, res25 boss/berserk near (all 70-tick cycle, `time % 70 > 64` swaps to res27 blink). res31 = intro speech bubble "BE NOT AFRAID" (`time < 99`).
- Depicts: a biblically-accurate-angel eye (`/‾‾‾\ / \___/` iris in a lidded almond) with two feathered wings.
- Sizes: left wing 5x13 / 5x14 / 6x14 / 5x13; right wing 5x12 / 5x13 / 6x11 / 5x12; eye 5x11; bubble 4x17. Whole assembled figure ≈ 9x34 (TOO-LARGE as a composite).
- Glyphs: `‾` and `´` throughout (ambiguous; `‾` single-width in Menlo/Inconsolata), `—` in eye/bubble.
- Identities: res06 = res09 and res10 = res13 byte-for-byte (the 4th flap frame is the 1st drawn one row lower). **The right wing is the exact horizontal mirror of the left** (reverse each row, swap `/`<->`\`, `` ` ``<->`´`): res06 mirrored differs from res10 in 1 cell (row4 `,` vs `.`).
- Diffs: wing flap frames res06->res07 39 cells, res07->res08 51, res08->res09 49 (full redraws — no bounded edit). Eye res20->res23 11 cells, res23->res25 11 cells.
- Mirror edit (left res06 -> right res10): each row is re-typed mirrored with virtual replace, e.g. row 1 `1G0gR   .´‾‾‾‾‾\<Esc>`; the teaching point is the glyph swap table (`/`<->`\`, `` ` ``<->`´`). Bounded 1-row exercise (4 cells): row 5 `  \;` -> `        ;/` = `5G0gR        ;/<Esc>`.
- Tutor fit: M19 Mirror key-pose still (5 rows, `gR`) — the left/right wing pair is an authored mirror with a clean swap table, pure-ASCII after `‾`->`~`/`-` and `´`->`'`. Also M18 Hand-mirrored return (4-row crop rows 1-4). The flap cycle itself is not teachable as small edits.
- Verdict: **USE** — M19 Mirror key-pose still (res06 left wing -> res10 right wing, 5 rows). Flap cycle and eye states REJECT for bounded edits (39-51 / 11 cells).

```
res06 L wing f1  res10 R wing f1  res07 L wing f2  res11 R wing f2  res20 eye        res23 eye boss
  /‾‾‾‾‾`.          .´‾‾‾‾‾\         /‾‾‾‾‾‾‾`.     .´‾‾‾‾‾‾‾\       \   |   /        \       /
 /  `     `.      .´     ´  \       /   `      \   /      ´   \      .´‾‾‾‾‾`.        .-. | .-.
 \   _____` \    / ´_____   /      /`_____     |   |     _____´\    /  /‾‾‾\  \      /  /\_/\  \
  \`/     `,/    \.´     \´/       \/     `. ` |   | ´ .´     \/    \  \___/  /      \  \___/  /
   \;                    ;/                 `.,/   \,.´              `———————´        `———————´
```

## official-Cosmetics/CultGroup

- Sheets viewed: res01, res02, res03, res04, res05, res06, res07, res09, res10, res11, res12, res13, res14, res15, res16 (all listed; res08 `pewpew` unlisted). All are `%%` frame strips; several use hold directives `%% {repeat:N}` / `% {repeat:N}` (the frame is held N times).
- Source: `~/Downloads/stone-story-official/Cosmetics/CultGroup.txt`
- Script: five hooded cultists + leader (the player) as `ui.AddAnim` objects: `leader`=res01, `guard`=res02, `guardattack`=res03, `heavyhitter`=res04, `heavyattack`=res05, `marksman`=res06, `markattack`=res07, `adept`=res09, `adeptattack`=res10, `splat`=res11 (projectile hit), `sorcerer`=res12, `sorcererattack`=res13, `boom`=res14, `pewboom`=res15, `pray`=res16. The idle strips (res01/02/04/06/09/12) are **walk cycles**: each follower `Play()`s while stepping toward its slot (`cultX` +-1 per tick) and is `Stop()`ped on a rest frame (frame 3, or 0/2 for adept/sorcerer) when it arrives. Attack strips are loaded on foe contact; `pray` is loaded for all at the end.
- Depicts: robed, hooded figures (`_` / `{))` hood, `\` staff arm) whose robe hem swings through 4 poses: `( !_` -> `( '._` -> `/ `-._` -> `/ '.__` with the hem shadow `` `¯ `` / `¯´¯` / `` `¯¯¯¯ `` / `¯¯¯¯`. Guard/heavy/marksman reuse the same 4-frame hem cycle under different upper bodies (shield `(∞(`, lantern `[___]/║`, rifle `{══╤)`). res12 sorcerer = same idea at 6 rows with a book `o`. Attack strips (res03/05/07/10/13) are 9-16-frame actions with holds; res11/14/15 are 1-3-row FX.
- Sizes: res01 5x8 (IDEAL); res02 6x9; res04 7x19; res06 5x15; res09 8x8; res12 6x10; res03 6x10; res05 up to 8x22 (ACCEPTABLE); res07 5x14; res10 8x9; res13 6x9; res16 5-6x12.
- Glyphs: `¯ ´` in every hem (swap `¯`->`-`, `´`->`'`); `∞` (shield), `─ ┼ ═ ╤ ║ ┌ ┐ └ ┘ │ ╞ ╡ ¡ ·` in weapons/FX (ambiguous).
- Diffs:
  - leader res01 f1->f2: 6 cells (row4 `!_`->`'._`, row5 `` `¯ ``->`¯´¯`). Edit: `4G5|R'._<Esc>5G4|R¯´¯<Esc>` (ASCII copy: `5G4|R-'-<Esc>`).
  - res01 f2->f3: 8 cells (row4 `( '._` -> `/ `-._`, row5 shadow widens). Edit: `4G3|r/5|R`-._<Esc>5G3|R`¯¯¯¯<Esc>`.
  - res01 f3->f4: 5 cells. Edit: `4G5|R'.__<Esc>5G3|r¯7|r ` .
  - sorcerer res12 f3->f4: 2 cells (row5 `(`->`/`, row6 new `` ` ``). Edit: `5G4|r/6G4|r``.
  - adept attack res10 f1->f2: 2 cells, f2->f3: 2 cells (staff hand `,/` -> `/(` -> `-´(`).
- Tutor fit: res01 leader walk is a clean 5-row, equal-height, 4-contact hem cycle for M8 Walk study (edits confined to rows 4-5), and the same cycle reused under five different upper bodies is a ready M14 Variant palette / M16 Key-pose plan illustration (`:t` copy the hem rows between characters). The `{repeat:N}` hold notation in the attack strips is the M7 Timed build concept (holds) in the original data — but the attack frames themselves change 10-50 cells.
- Verdict: **USE** — leader res01 (5x8) for M8 Walk study (alternate to the Crab); sorcerer res12 (6 rows, 2-6-cell steps) MAYBE for M3; attack strips MAYBE only as M7 hold-timing references; FX strips REJECT.

```
leader res01 f1..f4 (walk, 5x8)
   _         _         _         _
  {))       {))       {))       {))
    \         \         \         \
  ( !_      ( '._     / `-._    / '.__
   `¯        ¯´¯      `¯¯¯¯     ¯¯¯¯

sorcerer res12 f1..f5 (walk, 6x10)

   ,_          ,_          ,_          ,_          ,_
   {\\         {\\         {\\         {\\         {\\
   ( `\        ( `\        ( `\        ( `\        ( `\
   /`o'._      (`o'._      (`o`-._     /`o`-._     /`o'.__
   `¯¯'¯        ´¯¯¯        ¯¯¯¯¯      `¯¯¯¯¯      ¯¯´¯¯
```

## official-Games/SpearThrowing

- Sheets viewed: res01, res02, res03, res04, res05, res06, res07, res08, res09, res10, res11, res12, res13, res14, res15, res20, res21, res22 (all listed).
- Source: `~/Downloads/stone-story-official/Games/SpearThrowing.txt`
- Script: `background`=res01/`background2`=res02 (field grid 18x76), `scorebar`=res03 (UI), `spearrack`=res04 (`rack.frame` set to 1/2/3 as attempts are used — a spear disappears per throw), `idle`=res05, `powerup`=res06, `throw1..throw9`=res07..res15 chosen by power level (3 distances) x accuracy (3 heights) in `DetermineOutcome`; all loaded into one `stonehead = ui.AddAnim` with `duration = 15` (7 throw frames ≈ 2 ticks each). res20-22 = power/accuracy bar layers (`║█║`, UI).
- Depicts: a stick-figure thrower. res06 powerup (3 frames): spear held low -> cocked `.` -> raised overhead. Throw strips (7 frames, 4 rows): the arm whips through `\O` (back) -> `|` (overhead, head hidden by the spear) -> `O/` -> `O.´` -> `O__` -> `O |\` -> `/|\` (follow-through) while the spear `-──────>` flies right on row 1-4; the nine strips differ only in the spear's column/row per frame (identical thrower). res04 rack: 4 frames, one `∆` spear removed per frame.
- Sizes: throw strips 4 rows x 31/44/58 cols (TOO-LARGE wide because of the flying spear); **thrower-only crop rows 2-4, cols 1-7 = 3x7 (IDEAL)**; res05/res06 4x8 (IDEAL); res04 5x11 (IDEAL); res01/res02 18x76, res03 25x13 (TOO-LARGE / UI).
- Glyphs: spear `─` (swap -> `-`), `´` in `O.´` (swap -> `'`); rack `∆ │ ─` (swap -> `^ | -`); bars `║ █ ═ ╔`.
- Diffs (thrower crop, 3x7):
  - f3->f4: 2 cells, row1 `O/` -> `O.´` (arm lowers forward). Edit: `1G6|R.´<Esc>` (ASCII: `R.'`).
  - f4->f5: 2 cells, `O.´` -> `O__`. Edit: `1G6|R__<Esc>`.
  - f5->f6: 3 cells, arm drops: row1 `O__` -> `O`, row2 `|` -> `|\`. Edit: `1G6|D2GA\<Esc>`.
  - f6->f7: 1 cell, row2 ` |\` -> `/|\`. Edit: `2G4|r/`.
  - f1->f3 (`\O`/`|\` -> `O/`/`|`): 3 cells: `1G4|R O/<Esc>2G6|x`.
  - rack res04 f1->f2: 5 cells, one column (col 9): spear removed. Edit: `1G9|<C-v>4jr ` then restore the two rails `2G9|r-4G9|r-` (ASCII copy).
- Tutor fit: the thrower crop is a shoulder-pivot arm rotation with 1-3-cell steps and a stable body — M4 Rotation tween (3 rows: extremes `\O` and `O__`, midpoints `O/`, `O.´`) and M12 Joint sweep (`t`/`f` to the arm joint on row 1). The rack is a one-column-per-frame subtractive sequence for M6 Pyramid build (block-visual column delete).
- Verdict: **USE** — thrower crop (res07 f1,f3-f7, 3x7) for M4 Rotation tween; rack res04 MAYBE for M6 (needs ASCII glyph swap); backgrounds/UI/bars REJECT.

```
res07 thrower crop (rows 2-4, cols 1-7), f1..f7  (f2: head hidden behind the spear in the full frame)
   \O         |         O/        O.´       O__       O         O
    |\        |\        |         |         |         |\       /|\
   / \       / \       / \       / \       / \       / \       / \
```

```
res07 full frames f1, f4, f7 (spear flight, 4 rows)
f1                                f4                                f7
-──────>                                     -──────>
   \O                                 O.´                               O                  -──────>
    |\                                |                                /|\
   / \                               / \                               / \
```

```
res04 spear rack f1..f4
. ∆  ∆  ∆ .   . ∆  ∆    .   . ∆       .   .         .
│─│──│──│─│   │─│──│────│   │─│───────│   │─────────│
│ │  │  │ │   │ │  │    │   │ │       │   │         │
│─│──│──│─│   │─│──│────│   │─│───────│   │─────────│
│ '  '  ' │   │ '  '    │   │ '       │   │         │
```

## official-Pets/Snowman

- Sheets viewed: res01, res02, res04, res07, res11, res12, res14, res15, res16, res18, res19, res20, res22, res23, res24, res26, res27, res28, res30, res31, res32, res34 (all 22 listed). Unlisted 1-row nose layers (res03, res13, res17, res21, res25, res29, res33) and face/blink overlays (res05, res06, res08-10) read in the source and composited.
- Source: `~/Downloads/stone-story-official/Pets/Snowman.txt`
- Script: 4 colour layers at one origin `>o@myX@,@myZ-3@` — white body (res01/11/15/19/23/27/31), coal eyes/buttons/hat (res02/12/16/…/32), carrot nose (res03/13/…/33), stick arms (res04/14/…/34). Idle = res01-04 (+ blink overlays res08-10 at `stateTime % 50 >= 44/46/48`; `^^` face adds res06 + snowflakes res07 `❄`). Moving = 6 frames by `stateTime/3` = 0..5 (3 ticks each, stateTime 0-17 then idle): m0 res11-14, m1 res15-18, m2 res19-22, m3 res23-26, m4 res27-30, m5 res31-34.
- Depicts: a snowman with a top hat `__ / _|__|_`, coal eyes `•`, carrot `,`, twig arms `.` `,.`. The move cycle is a waddle-turn: front (m0) -> turning right (m1) -> right profile `('  •-` (m2) -> front, narrower (m3) -> front with arms out (m4) -> turning left (m5). Hat (rows 1-2) and base (row 6) never change — a stable pivot.
- Sizes: composites 6x11 (IDEAL); middle crop rows 3-5 = 3x11 (IDEAL). Individual layers 3-6 rows (part layers). res07 snowflakes 4x10 (`❄` — East-Asian-ambiguous/emoji, drop).
- Glyphs: `•` (eyes, buttons; swap -> `o`), `´` (swap -> `'`), `❄` (drop).
- Identities: idle composite = m0 composite = m4 body layer (res01 = res11 = res27 byte-identical; res02 = res12 = res28; res04 = res14).
- Diffs (composites; all changes on rows 3-5): m0->m1 16 cells, m1->m2 12, m2->m3 12, m3->m4 11, m4->m5 14, m5->m0 13. No step is a 1-6-cell edit; the nearest is a per-row rewrite, e.g. m2->m3 row 3 (6 cells): `3G0C .( •,•).<Esc>`.
- Tutor fit: rows 3-5 turning around a fixed hat/base is the M4 Rotation tween idea (extremes m1/m5, front midpoint m3, stable pivot rows 1-2 and 6) and M18 Hand-mirrored return (m1 right turn vs m5 left turn are near-mirrors). But every step is an 11-16-cell whole-row rewrite, too large for a beginner edit.
- Verdict: **MAYBE** — M4 Rotation tween extremes (m1 / m3 / m5, 3x11 crop) if the lesson accepts row rewrites (`cc`/`C`) instead of cell edits; not a 1-6-cell lesson.

```
Snowman composites (white + coal + nose + arms), 6x11
m0 res11-14   m1 res15-18   m2 res19-22   m3 res23-26   m4 res27-30   m5 res31-34
    __            __            __            __            __            __
  _|__|_        _|__|_        _|__|_        _|__|_        _|__|_        _|__|_
. ( •,•) ,.     .  •,).       ('  •-       .( •,•).     . ( •,•),..    .( •,•,
'`(  : )'       `   :)        ( `  ;       `(   :)      '`(  : )'       ( :  '
 (    : )      (     :)      (      ;      (     :)      (    : )      (   :  )
  `----´        `----´        `----´        `----´        `----´        `----´
```

## official-Pets/Dragon

- Sheets viewed: res01-res29 (all 29 listed): res01-06 head, res07-15 attack, res16-29 body.
- Source: `~/Downloads/stone-story-official/Pets/Dragon.txt`
- Script: text widgets, not `ascii` draws: `ChineseDragonHead` = [res01..res06], `DragonAttack` = [res07..res15], `ChineseDragonBody` = [res16..res29]. `FlyingAnimation()` advances `MovementFrame` every 4 ticks (`tt % 4 = 0`) and sets `DragonBody.text = Body[MF % 14]`, `DragonHead.text = Head[MF % 6]`; the head widget sits at x=19, y=-1 relative to the body and flips between x=19 and x=18 every 28 ticks (`DragonHead.x = 37 - DragonHead.x`). Attack: head hidden, body replaced by `DragonAttack[Attackframe/4]` (4 ticks per frame, 9 frames), fireball spawned at frame 22.
- Depicts: a Chinese dragon. Head (4x14): horned snout `\`-`~.` / `{_ ` `~;` / jaw `‾`/~´` with a flowing beard on row 4 that ripples through 6 shapes (`´‾‾`´` -> `´‾`-´` -> `´`--´` -> `` `._,´ `` -> `-.-´´` -> `,´‾`´`). Body (6x27): a serpentine body wave travelling tail-to-head across 14 frames. Attack (9x31-34): the dragon rears, coils and snaps.
- Sizes: head 4x14 (IDEAL); head rows 2-4 crop 3x14 (IDEAL); body 6x27 (ACCEPTABLE, 1 col over IDEAL); attack 9x31-34 (ACCEPTABLE edge).
- Glyphs: `‾ ´` throughout (swap `‾` -> `~` or `-`, `´` -> `'`); attack frames res08-15 contain `｛` (U+FF5B FULLWIDTH LEFT CURLY BRACKET — East-Asian **wide**, breaks the grid; replace with `{`).
- Diffs:
  - head (row 4 only, cols 6-9, rows 1-3 identical in all six): f1->f2 2 cells `4G8|R`-<Esc>`; f2->f3 2 cells `4G7|R`-<Esc>`; f3->f4 4 cells `4G6|R`._,<Esc>`; f4->f5 3 cells `4G6|r-8|R-´<Esc>`; f5->f6 4 cells `4G6|R,´‾`<Esc>`; f6->f1 2 cells `4G6|R´‾<Esc>`.
  - body: 30-54 cells per step (whole-body wave) — no bounded edit.
  - attack: 29-78 cells per step (res13 = res14 identical, a hold).
- Tutor fit: the head is an ideal M11 Fixed-width redraw subject — every step is one `R` over a 2-4-cell span on a single row of a fixed 14-col line, in a 6-step loop that exercises `u`/`<C-r>` to scrub back and forth. It also fits M13 Texture pulse (a cyclic texture change on one row). Body/attack are showpieces only.
- Verdict: **USE** — head res01-06 (crop rows 2-4, 3x14) for M11 Fixed-width redraw. Body MAYBE as a watch-only demo (6x27); attack REJECT (size, full-width `｛`, 30-78-cell steps).

```
head res01..res06 (4x14; rows 1-3 fixed, row 4 = beard)
res01           res02           res03           res04           res05           res06
     \`-`~.          \`-`~.          \`-`~.          \`-`~.          \`-`~.          \`-`~.
      {_ ` `~;        {_ ` `~;        {_ ` `~;        {_ ` `~;        {_ ` `~;        {_ ` `~;
        ‾`/~´           ‾`/~´           ‾`/~´           ‾`/~´           ‾`/~´           ‾`/~´
     ´‾‾`´           ´‾`-´           ´`--´           `._,´           -.-´´           ,´‾`´
```

```
body res16, res17 (6x27; 30 cells apart)
                    _   ,                       _    ,
      _..-.._    ,´‾ ‾`´  ,        _.-.._    ,´‾ ‾'-´  ,
   .´‾. --   ‾`-´  _._   ;      .´‾  __   ‾`‾   _     ;
  /´‾  ))  `._  _,´   ((´      /´‾‾ )) `._   _,´ ‾`((´
 '    ,´      ‾‾       `´"    ´    ,´     ‾‾        `´"
     "                            "
```

## official-Pets/Cranius

- Sheets viewed: res01-res45 (all 45 listed). They repeat in triplets (skull body / chest layer / arm layer): body res01 = res09 = res12 = res17 = res22 = res25 = res28 (byte-identical), chest res02 = res10 = res13 = res18 = res23 = res26 = res29; the moving body res31/res34/res37/res40/res43 is the same skull compressed by 1-2 cols in the chest (`-----|` -> `---|`). Described together where identical.
- Source: `~/Downloads/stone-story-official/Pets/Cranius.txt`
- Script: all layers at one origin `>o@myX@,@myZ-12@` in `skullColor` / `chestColor`. Idle = body res01 + chest res02 + arm res03. Idle face overlays: `face = "°°"` alternates res04/res05 on `time % 4` (both `(_^) ,(_^)` — identical, so no visible change); otherwise a blink on `stateTime % 50`: 44-45 res08 `(==)`, 46-47 res07 `(--)`, 48-49 res06 `(==)`. Happy face `( ^^` plays a chest-open sequence on `chestTime`: <=5 res09-11 (arm lifts, hand `_.'‾‾.`), <=10 res12-16 (hand reaches in, `---` bone/delta), <=45 res17-21 (holds out `=o=╪3` or `-∆-╡`), <=50 res22-24, then res25-27. Moving = 6 frames on `stateTime/2` (2 ticks each): body+chest+arm triplets res28-30, 31-33, 34-36, 37-39, 40-42, 43-45 — the skull drags itself with its bony arm (arm reaches, plants `; '`, pulls, sprawls).
- Depicts: a giant skull pet (Cranius) with a ribcage "chest" drawer and one skeletal arm that it crawls with.
- Sizes: full composites 12-13 rows x 29-33 cols (TOO-LARGE). Eye/face crop rows 4-7, cols 7-24 = 4x18 (IDEAL). Eye overlays alone 5x22 (2 rows used).
- Glyphs: body uses `´ ‾` (rows 8-10 only); the face crop is pure ASCII. Chest items `╪ ∆ ╡` (ambiguous).
- Diffs:
  - crawl frames: 24-218 cells between triplets (row shifts + arm redraw) — no bounded edit.
  - face crop open -> half-blink `(_*)` -> `(==)`: 4 cells (row 2 cols 8-9 and 14-15). Edit: `2G0f(ci(==<Esc>;.` (change inside the first eye socket, `;` to the next `(`, `.` to repeat) or `/_\*<CR>R==<Esc>n.`.
  - half -> shut `(==)` -> `(--)`: 4 cells. Edit: `:2s/==/--/g`.
  - open -> happy `(_*)` -> `(_^)`: 2 cells. Edit: `/\*<CR>r^n.`.
- Tutor fit: the face crop is a stable skull contour with two identical sockets, so each blink step is one edit repeated at a second anchor: M17 Coherent anchors (search, `n`, `.`) and M2 Face focus (`ci(` inside the sockets; 4 rows exactly). Full-body crawl is TOO-LARGE and changes too much.
- Verdict: **USE** — face crop (4x18) with blink overlays res06/res07/res04 for M17 Coherent anchors (or M2 Face focus). Full frames REJECT (13x33, whole-body redraws).

```
face crop rows 4-7, cols 7-24 (4x18), idle composite + eye overlay
open res01-03        half res06           shut res07           happy res04
  /    ___,  __,\      /    ___,  __,\      /    ___,  __,\      /    ___,  __,\
 |  \ (_*) ,(_*);-    |  \ (==) ,(==);-    |  \ (--) ,(--);-    |  \ (_^) ,(_^);-
 |   ) _  /!)   )     |   ) _  /!)   )     |   ) _  /!)   )     |   ) _  /!)   )
  `.__,.)     ('       `.__,.)     ('       `.__,.)     ('       `.__,.)     ('

full idle composite res01+res02+res03 (13x33, TOO-LARGE; for context)

           _.-----._ ___///‾`
         .'         '.     '.|
        /    ___,  __,\     |;
       |  \ (_*) ,(_*);-----|.
       |   ) _  /!)   )     | |
        `.__,.)     ('      |  .
      (/ )'.  `'""'´/.______|. '.
      |\\\ \‾._____/ ;.._   `.  |
      |.\'\.__,''._.'    ‾‾-____)
      \ '\_\_,''._.'
     .' \_\\"..______.-‾‾‾`.
    [_.'   (________;__,-\\\>
```

## Addendum: frames for MAYBE sub-candidates named inside USE sets

```
Beach res04 sandcastle f1..f3 (top-aligned, 4x8)
 O          O_         O
 |= ,',     |  _~_     |- _•_
  - |_|      - |_|^     - |O|
              ^          ^ - ^

Beach res05 ball toss f4..f8 (bottom-aligned, 5x14)
      o

                      o                o              O !           o   !
\O/      \O/   (O/      \O/   (O/      <O>   (O/      \O>   (O/      \O>
—--      - -   —--      - --  —--      - --  —--      - --  —--      - --

Fireworks dahlia res06 burst f1..f7 (7x11)
                                                                               .   '   .
                                            .          . : .        .·:·.       '.·:·.'
                  ¡           \¡/         .\¡/.        .\¡/.       ·.\¡/.·     '·.\¡/.·'
     *           -*-         -—*—-       •-—*—-•      •-—*—-•     ·•-—*—-•·   ··•-—*—-•··
                  !           /!\         '/!\'        '/!\'       ·'/!\'·     .·'/!\'·.
                                            '          ' : '        '·:·'       .'·:·'.
                                                                               '   .   '

Fireworks wcrackle res05 textures f3..f6 (5x11)
 . '.' ''.    .'' '.' .    .' .'. '.     ''. .''
  .··  ·. ·  · . · ··  ·  ·  ·· · . ·  · .·  ··.
 ' .' '. '   ''  '.'  ''  '  .'. . ''  '' . .'.  '
' ·  .    '  '    .  · '    ·  .  ·    ' ·     · '
  '  .            .  '      '  .  '      '     '
```

## Summary

Counts: USE 10, MAYBE 4, REJECT 8 (22 sets).

| set | frames | size | verdict | best module | proposed edit |
|---|---|---|---|---|---|
| official-UI/FaceHUD | 8 face states (neutral, blink, look R/L, scowl, grin, shock, dead) at one origin | 6x12 (crop rows 2-5: 4x12) | USE | M3 Pose copy (alt M2, M18) | neutral->blink: `3G4\|R`-   -'<Esc>` (6 cells) |
| official-Pets/Crab | idle + 4 scuttle composites (body+shell layers) | 5x10 | USE | M8 Walk study | s1->s2 legs: `5G3\|R\><Esc>9\|r/` (3 cells) |
| official-Cosmetics/Fireworks | willow burst 7 + fade 11 (also rings, dahlia, crackle) | 5x11 (dahlia 7x11) | USE | M6 Pyramid build | fade f3->f4: `1G5\|<C-v>2j2lr ` (8 cells, one block) |
| official-Pets/Dragon | head 6-frame beard loop (body 14, attack 9) | head 4x14 (crop 3x14); body 6x27 | USE | M11 Fixed-width redraw | f1->f2: `4G8\|R`-<Esc>` (2 cells) |
| official-Games/SpearThrowing | throw 7 frames (thrower crop), rack 4 | crop 3x7; rack 5x11 | USE | M4 Rotation tween (alt M12) | f4->f5: `1G6\|R__<Esc>` (2 cells) |
| official-Cosmetics/Beach | volleyball res06 11 frames (also ball toss 13, sandcastle 3) | 5x24 | USE | M9 Bounce capstone (alt M7/M16) | f4->f5 ball: `1G10\|r 13\|rO` (2 cells) |
| official-Pets/Boo | body 4, blink 6, mouth 13, tail 6, sleep 4 | 3x7 (composite 5x7) | USE | M2 Face focus (alt M0/M9/M8) | blink: `:2s/o o/= =/` (2 cells) |
| official-Pets/Cranius | blink overlays on a 45-sheet crawl/chest pet | face crop 4x18 (full 13x33) | USE | M17 Coherent anchors (alt M2) | open->half: `/_\*<CR>R==<Esc>n.` (4 cells) |
| official-Cosmetics/AcronianGuardian | wing flap 4 L + 4 R, eye 3 states | wing 5x12-14 | USE | M19 Mirror key-pose still (alt M18) | L->R wing row 5: `5G0gR        ;/<Esc>` |
| official-Cosmetics/CultGroup | walk 4 (x5 characters), attacks 9-16 with holds | leader 5x8; sorcerer 6x10 | USE | M8 Walk study (alt M14/M16) | f1->f2: `4G5\|R'._<Esc>5G4\|R-'-<Esc>` (6 cells) |
| official-Weapons/Scythe | held vs swing (2 poses) + unlisted 3x3 walk | 6x8, 7x7 | MAYBE | M4 Rotation tween (extremes only) | none bounded (26+ cells); walk `3G0R >\<Esc>` |
| official-Cosmetics/Pumpkins | 3 bodies x 27 faces x 9 stems, random, not timed | 3x7 | MAYBE | M14 Variant palette | `:2s/@.@/O_O/` (3 cells) |
| official-Pets/BlackHole | 5 growth stages by level + ring layer | 8x14 (f1-f3 fit 4 rows) | MAYBE | M6 Pyramid build | f1->f2: `5G7\|R( )<Esc>` + rows 4/6 |
| official-Pets/Snowman | 6-frame waddle-turn (4 colour layers) | 6x11 (crop 3x11) | MAYBE | M4 Rotation tween | row rewrites only: `3G0C .( •,•).<Esc>` |
| official-Hats/StarCloak | 2 variants (bighead) | 6x7 | REJECT | – | not an animation (2-cell variant) |
| official-UI/CDTime | 2 language variants | 5x17 | REJECT | – | UI; CJK wide glyphs |
| official-Games/Arena | tile map + UI border | 17x34, 25x86 | REJECT | – | data/UI, too large |
| official-Cosmetics/ChristmasTree | static tree + lights layer | 11x9 | REJECT | – | not an animation; ambiguous glyphs |
| official-Games/PlayingCards | card front/back/compact | 4x4 | REJECT | – | UI library still |
| official-Weapons/EmbueDaggers | 3 identical per hand | 4x11 | REJECT | – | frames identical; `@var@` placeholder |
| official-Cosmetics/StoneClause | 5 reindeer frames (4 identical) | 4x13 | REJECT | – | frames identical; `☺` heads |
| official-Games/KillerRPG | 7 UI/text panels | up to 92x59 | REJECT | – | UI and help text |
