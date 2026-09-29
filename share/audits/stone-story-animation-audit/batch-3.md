# Stone Story animation audit — batch 3 — 2026-09-28 — auditor: subagent batch-3 (manual view of every listed sheet)

Scope: 21 sets from `share/audits/animation-frame-paths.txt`, base `~/Downloads/stone-story-consolidated/`.
Method: every listed `resNN.txt` was printed with `#` -> space and rows right-trimmed, and viewed; the StoneScript
source `~/Downloads/stone-story-official/<Category>/<Name>.txt` was outlined (control lines + block index) so each
`resNN` maps to its draw condition and offset. Where a set draws two colour layers at the same origin
(e.g. white body + yellow feet), the frames below are the composite of those layers, which is what the player sees.
Cell diffs were computed by script over the composites; every verdict is the auditor's judgement after viewing.
Compositing convention (checked in the raw sheets, e.g. Pets/Dog res11 `#_`--'`): `#` is transparent, a literal space
is OPAQUE and clears the cell underneath. Composites below honour that; converting `#` to space before layering
would erase the lower layer. Sizes are rows x max cols after trimming. Popup fit: IDEAL <= 7x26, ACCEPTABLE <= 10x34.

## official-Cosmetics/SillyGoose

Sheets viewed (44): res01-res40, res42-res45 (also glanced at unlisted res41, res46-res49: 1-2 row part layers).
Source: `~/Downloads/stone-story-official/Cosmetics/SillyGoose.txt`.

1. Depicts: a goose player skin. Each pose = white body block + yellow beak/feet block, both at `>o-4,-1`.
   - Eat (item within 3 cells, idle): `timerGoose4` ticks 0-25 -> res01+02 (stand, 3f), res03+04 (neck bent, 3f),
     res05+06 (head down, beak `<`, 3f), res07+08 (head down, beak `=`, 3f), res09+10 (neck bent, eye `~`, 3f),
     res11+12 (stand, 10f hold). 6 frames.
   - Walk (`ai.walking`, no near foe): `timerGoose` 0-60 in 5-frame steps, 12 frames res13/14 ... res35/36. The
     body is constant except the neck (`\(`, `\|`, `\\`), two honk-with-head-forward poses (res24, res26) and an
     eye blink (res36 `~`). The feet cycle `<   v` / `L L` (or `L  L`) / `V <`.
   - Idle res37+38 (= stand), boss-idle res39+40+41 (eye `ò`). Combat res42+43 / res44+45 (charging, `*HONK*`),
     2 frames alternating every 3 ticks; res46-49 are 1-row foot layers at `o-5,5`.
2. Sizes: stand/walk composites 7x8 (IDEAL); honk frames 7x16-7x23 (IDEAL); eat frames 7x10-7x11 (IDEAL);
   combat 6x15 / 6x17 (IDEAL). Glyphs: `‾` (U+203E, single-width in most mono fonts, OK), `ì` `ò` (Latin-1,
   single-width, OK). res42/res44 contain `］` U+FF3D FULLWIDTH RIGHT SQUARE BRACKET = East-Asian WIDE -> unsafe;
   replace with `]` if the combat frames are used.
3. Pairs worth teaching:
   - Walk feet, res27+28 -> res29+30 -> res31+32 -> res33+34 (only row 7 changes):
     `   L L` -> `  <   v` = 4 cells (r7c3 `<`, c4 ` `, c6 ` `, c7 `v`): `7G0R  <   v<Esc>`.
     `  <   v` -> `   L L` = 4 cells: `7G0R   L L <Esc>` (or `7G0C   L L<Esc>`).
     `   L L` -> `   V <` = 2 cells: `7G4|rV2lr<`.
   - Blink, res33+34 -> res35+36: eye r2c6 `'` -> `~`, feet `V <` -> `L L` (3 cells): `2Gf'r~` then `7G4|rL2lrL`.
   - Neck, res19+20 -> res21+22: r3c6 `|` -> `\` plus feet: `3G6|r\`.
   - Eat beak flap, res05+06 -> res07+08: 1 cell r5c11 `<` -> `=`: `5G$r=`.
   - Eat neck bend res01+02 -> res03+04: 13 cells (whole head moves) — a pose copy, not a beginner edit.
4. Tutor fit: walk feet -> M8 Walk study (contact alternation on a fixed body, equal frame height, 1-row
   change); the stand -> bent -> down neck trio (res01, res03, res05 composites) -> M4 Rotation tween (two extremes
   and a midpoint around a stable body pivot) though 7 rows vs M4's 3; blink/beak -> M0 or M11 single-cell change.
5. Verdict: **USE** — M8 Walk study (primary), M4 Rotation tween (secondary, neck pivot).

Frames below: each `--- <layers> RxC` line starts one frame (composite of the listed layers).

Walk cycle:
```
--- res27+res28 7x8
     _
    /'l=
    \(
 ,   \\
( ‾‾‾  )
 \____/
   L L
--- res29+res30 7x8
     _
    /'l=
    \(
 ,   \\
( ‾‾‾  )
 \____/
  <   v
--- res31+res32 7x8
     _
    /'l=
    \(
 ,   \\
( ‾‾‾  )
 \____/
   L L
--- res33+res34 7x8
     _
    /'l=
    \(
 ,   \\
( ‾‾‾  )
 \____/
   V <
```

Eat neck tween:
```
--- res01+res02 7x8
     _
    /'l=
    \(
 ,   \\
( ‾‾‾  )
 \____/
   L L
--- res03+res04 7x10

       _
      /'l<
 ,   ((
( ‾‾‾  )
 \____/
   L L
--- res05+res06 7x11



 ,      _
( ‾‾‾.`~'l<
 \____ì'
   L L
--- res07+res08 7x11



 ,      _
( ‾‾‾.`~'l=
 \____ì'
   L L
```

## official-Cosmetics/Knight

Sheets viewed (34): res01-res34. Source: `~/Downloads/stone-story-official/Cosmetics/Knight.txt`.

1. Depicts: an armoured knight player skin. Three arrays drawn every frame at `>o-25,-13`: `KnightAtk` (res01-18,
   grey sword/slash layer only: upright sword res01/02/17/18, slash arcs res03-12, thrust `-------->` res13/14,
   recover res15/16), `KnightWalk` (res19-26, full body 8-frame walk) and `KnightWalkfar` (res27-34, far-leg layer in
   dark grey). Walk frame = `(7*(pos.x+pos.y+pos.z)/12) % 8` (position-driven, not time); attack frame advances
   every 2 ticks while a foe is within 24.
2. Sizes: walk composites 16x31 (18x32 raw) -> TOO-LARGE. The legs crop (rows 11-16) is 6x26 but every walk step
   rewrites 52-65 cells of it, so it is not a small edit. Sword layers 7x26 to 15x32, part layers only.
   Glyphs: box drawing `┌─┬┐├═╬┤║┴┊` and `¡ · ‾ ´` are East-Asian AMBIGUOUS width; res19-21 contain `］` U+FF3D
   (FULLWIDTH, unsafe; res22-26 use ASCII `]` for the same cell).
3. Pairs: res19+27 -> res20+28 = 64 cells, res20+28 -> res21+29 = 52 cells, res21+29 -> res22+30 = 65 cells.
   No 1-6 cell edit exists between consecutive walk frames. Sword res01 -> res02 is a 1-column shift of a 7-row
   part layer (not a subject on its own).
4. Tutor fit: none for a beginner edit; could be shown as a "professional reference" of an 8-contact walk but not
   authored in the popup.
5. Verdict: **REJECT** — too large (16x31) and walk diffs are 50+ cells; attack blocks are part layers only.

## official-Games/TowerDefense

Sheets viewed (21): res01-res09, res11-res15, res18-res23, res25 (res10/16/17/24/26/27 are 1-3 row projectiles, not
listed). Source: `~/Downloads/stone-story-official/Games/TowerDefense.txt`.

1. Depicts: a UI mini-game. Each res is ONE `ascii` literal holding several frames separated by `%%`, played by
   `ui.AddAnim` (`uiAA`). Foes are created by `CreateFoe(...)` with `gfoe.Play(); gfoe.duration = D; gfoe.loop = true`
   (bee/wasp/hornet D=5 ticks per loop, missile/mineflyer/rocket/heli D=10), so frames cycle evenly and loop.
   Bosses (queen bee res15, copter res22) have frames picked by `gametime%8` / `gametime%12` (idle, 2-3 ticks each)
   plus attack sub-sequences on `animtime`. Player archer res08 frames are picked from the reload timer.
   - res01 title logo, res02 shop icon, res05/res06 tower front/back, res07 crystal, res09 force field, res25 crate:
     single stills (UI).
   - res03 forest / res04 volcano backgrounds: 4 frames each (100/75/50/25% HP smoke), 26x105 — TOO-LARGE.
   - res08 archer 7f (3x6), res11 snake 2f (2x9), res12 bee 2f (2x5), res13 wasp 4f (4x7), res14 hornet 2f (4x10),
     res15 queen bee 12f (5-6 x 13), res18 missile 4f (3x10), res19 mine-flyer 3f (4x14), res20 rocket 4f (5x15),
     res21 heli 4f (6x9), res22 copter 8f (6x30), res23 controller 4f (3x6).
2. Sizes: all foe sprites are IDEAL except res22 copter (6x30, ACCEPTABLE). Glyphs: `¯` (U+00AF), `´`, `·`, `•`,
   `≈`, `≤ ≥`, `≡`, box drawing `└ ┘ ┐ ╞ ─ ═ ╤`, Greek `ζ` — all East-Asian AMBIGUOUS width (single cell in Western
   mono fonts; flag for CJK-ambiguous-wide terminals). No FULLWIDTH glyphs.
3. Pairs:
   - Wasp res13 (loop f1-f4, wings up/half/flat/half): each step changes exactly 2 cells in row 1.
     f1 `_|  |` -> f2 `_\  /`: `1G2|r\3lr/`. f2 -> f3 `__  _`: `1G2|r_3lr_`. f3 -> f4 = f2.
   - Heli res21 (rotor foreshortening, pivot `.` fixed at c6): f1 `  ___.___` -> f2 `   __.__` (c3, c9 blank):
     `1G3|r 6lr `. f2 -> f3 `    _._` (c4, c8): `1G4|r 4lr `. f3 -> f4 = f2 (`1G4|r_4lr_`).
   - Missile res18 exhaust: f1 `:.` -> f2 `:'` (1 cell `2G9|r'`), f2 -> f3 `::'` (2 cells c9 `'`->`:`, c10 ` `->`'`:
     `2G9|R:'<Esc>`), f3 -> f4 `::.` (`2G10|r.`).
   - Copter res22 f1-f4: twin rotors counter-phase, 4 cells per step in row 1 (left shrinks, right grows):
     f1 -> f2: `1G0r ` `14lr ` `7lr_` `6lr_` (c1, c15 -> space; c22, c28 -> `_`). Bounded but 4 separate cells.
   - Bee res12 f1 -> f2: 3 cells ` /)` -> ` .-´` (`1G2|R.-'<Esc>` if `´` is normalised to `'`).
   - Queen bee res15 f1-f4 idle wing flap: 5-6 cells per step over rows 1-3 (`─` wings).
   - Archer res08 / controller res23: 5-11 cells per step, whole-bow repositioning — pose swaps, not tweens.
4. Tutor fit: wasp -> M0 Spark loop (a 2-cell, 4-frame loop that reads instantly; 4 rows vs M0's 3 — row 4 is the
   stinger/legs and could be kept). Heli rotor -> M4 Rotation tween (extremes `___.___` and midpoint `_._` around
   a fixed `.` pivot — exactly the spin-by-foreshortening lesson); copter -> M4 extension (two rotors in
   counter-phase). Missile exhaust -> M13 Texture pulse or M7 Timed build (dot-repeat on `:`/`.`/`'`).
5. Verdict: **USE** — heli res21 for M4 (best), wasp res13 for M0/M1, missile res18 for M13. Copter res22 MAYBE
   (30 cols). Backgrounds/UI REJECT (too large / UI).

Heli rotor (res21, loop f1-f4, 10 ticks per loop):
```
--- res21 f1 6x9
  ___.___
    _|_
   ´└O┘`
 _/./|\,\
|_\'¯¯¯'/
 ¯¯`---´
--- res21 f2 6x9
   __.__
    _|_
   ´└O┘`
 _/./|\,\
|_\'¯¯¯'/
 ¯¯`---´
--- res21 f3 6x9
    _._
    _|_
   ´└O┘`
 _/./|\,\
|_\'¯¯¯'/
 ¯¯`---´
--- res21 f4 6x9
   __.__
    _|_
   ´└O┘`
 _/./|\,\
|_\'¯¯¯'/
 ¯¯`---´
```

Wasp wings (res13, loop f1-f4, 5 ticks per loop):
```
--- res13 f1 4x6
_|  |
 O()/\
    )/
   ¯`
--- res13 f2 4x6
_\  /
 O()/\
    )/
   ¯`
--- res13 f3 4x6
__  _
 O()/\
    )/
   ¯`
--- res13 f4 4x6
_\  /
 O()/\
    )/
   ¯`
```

Missile exhaust (res18, loop f1-f4):
```
--- res18 f1 3x9
  ____/
< / / |:.
  ¯¯¯¯\
--- res18 f2 3x9
  ____/
< / / |:'
  ¯¯¯¯\
--- res18 f3 3x10
  ____/
< / / |::'
  ¯¯¯¯\
--- res18 f4 3x10
  ____/
< / / |::.
  ¯¯¯¯\
```

Copter twin rotors (res22 f1-f4, gametime%12, 3 ticks each):
```
--- res22 f1 6x30
_______._______       __.__
  .----'----.________.--'--.
 /[    ] \   [\ _____\   [ ]\
[_________]  []|______|______]
 \¯¯¯¯¯¯¯    [/      /  ¯¯¯¯/
  `----------'------'------´
--- res22 f2 6x30
 ______.______       ___.___
  .----'----.________.--'--.
 /[    ] \   [\ _____\   [ ]\
[_________]  []|______|______]
 \¯¯¯¯¯¯¯    [/      /  ¯¯¯¯/
  `----------'------'------´
--- res22 f3 6x30
  _____._____       ____.____
  .----'----.________.--'--.
 /[    ] \   [\ _____\   [ ]\
[_________]  []|______|______]
 \¯¯¯¯¯¯¯    [/      /  ¯¯¯¯/
  `----------'------'------´
--- res22 f4 6x30
   ____.____       _____._____
  .----'----.________.--'--.
 /[    ] \   [\ _____\   [ ]\
[_________]  []|______|______]
 \¯¯¯¯¯¯¯    [/      /  ¯¯¯¯/
  `----------'------'------´
```

Bee (res12, MAYBE — 2 rows only):
```
--- res12 f1 2x5
 /)
O__)>
--- res12 f2 2x5
 .-´
O__)>
```

## official-Cosmetics/Bolesh

Sheets viewed (17): res03, res08-res13, res20, res21, res28, res31, res34, res36-res40 (also looked at unlisted
res29/res30 for the leg sequence). Source: `~/Downloads/stone-story-official/Cosmetics/Bolesh.txt`.

1. Depicts: two "mount" player skins switched by a hard-coded `mount` var. Mount 6 = a walker mech: hull res13
   (`o-6,-4`), left arm res08-12 (`o1,-1`/`o1,-2`), right arm res36-40 (`o-3,-1`/`o-3,-2`), screen-anchored HUD
   blocks res01-07 (res03 is a `┌——┐` HUD box). Arm pose is chosen by `item.left/right.state` (1 idle, 2 aim `/‾\`,
   3 fire barrel `———:`, 4 fire flash in cyan) — state-driven, not timed; res08/09 and res11/12 and res36/37,
   res39/40 are identical art in a different colour (flash). Mount 2 = a spider rider: res20 + res21 body (`o-20,-3`),
   leg res28-31 by `item.left.state`, buff glyphs res22-27. The source has a broken block (res34 contains the
   literal text `asciiendo2,-3, red,ascii` — an `asciiend` fused into the next draw line).
2. Sizes: arm layers 4x9-5x4; mech composite 8x13-8x16 (ACCEPTABLE); spider composite 8x21 (ACCEPTABLE).
   Glyphs: `— │ ┌ ┐ └ ┘ • ‾ ´` ambiguous width (`—` U+2014).
3. Pairs: mech idle -> aim composite = 45 cells, aim -> fire = 18 cells (both arms), one arm res10 -> res11 = 9
   cells (`1G6|R___<Esc>2G7|R——:<Esc>3G6|R‾‾‾<Esc>`). Spider leg res28 -> res31 = 4 cells but the composite rider
   does not read as a clean single subject.
4. Tutor fit: none strong; arm layers are weapon states, not an animation cycle.
5. Verdict: **REJECT** — part layers driven by weapon state; identical colour-flash duplicates; composites need
   18-45 cell edits.

## official-UI/Calculator

Sheets viewed (15): res01-res12, res14-res16. Source: `~/Downloads/stone-story-official/UI/Calculator.txt`.

1. Depicts: a calculator UI in three sizes (big res01-04, medium res05-08, small res09-12: frame, screen, button
   grid, button labels as separate layers) plus option panels res14 (menu), res15 (colour picker), res16 (placement).
   No time-driven frames; sizes are chosen by a button (`calculatorChangeSize`).
2. Sizes: 20-23 rows x 15-28 cols -> TOO-LARGE. Glyphs: double/single box drawing `╔═║╒╕─│┌┐└┘`, `◘ ☼ • █ ← ↑ → ↓`
   (all AMBIGUOUS width).
3. Pairs: none — the three sizes are re-layouts, not frames; screen/button/number blocks are layers of one still.
4. Tutor fit: none (could at most seed an M15 box-edge texture drill, but it is UI chrome, not art).
5. Verdict: **REJECT** — UI, not an animation; too large.

## official-Games/FrogBog

Sheets viewed (12): res01-res07, res17-res21 (also opened unlisted frog/eye layers res08, res10, res11, res13,
res14, res16 — 3-row frog `,Oo` bodies and `^^` eyes). Source: `~/Downloads/stone-story-official/Games/FrogBog.txt`.

1. Depicts: a frog-launching UI game. res01 river background (26x100), res02 seesaw, res03 target ring, res04 lily
   flower, res05-07 lily pads labelled 1/2/3 (each a 1-frame `ui.AddAnim` with an empty `%%` second frame), res17
   flying frog and res18 landed frog (moved by `x = flightcount - 20`, not frame-swapped), res19-21 "hammer smack"
   drawn at the fixed screen origin `` `2,10 `` for `flightcount` 1-2, 3-4, 5-7 (2, 2, 3 ticks).
   The lily-pad sheets contain `Â´` — a UTF-8 double-encoding artefact of `´` (bytes C3 82 C2 B4); treat `Â` as
   corruption, not art.
2. Sizes: res19 10x22, res20 9x24, res21 10x24 (ACCEPTABLE); lily pads 5x9 (IDEAL); res01 TOO-LARGE.
3. Pairs: hammer smack res19 -> res20 = 79 cells, res20 -> res21 = 73 cells (whole silhouette redrawn; key poses,
   no small edit). Frog res17 -> res18 = 51 cells and a position change. Lily pad res05 -> res06 -> res07 differ
   by one digit (r3c6 `1` -> `2` -> `3`): `3G6|<C-a>` — a label increment, not motion.
4. Tutor fit: lily pads -> M16 Key-pose plan as `<C-a>` label practice (copy pad with `:t`, bump the number);
   hammer smack -> view-only reference of 3 held key poses for M9 (timing 2/2/3 ticks) — too many cells to author.
5. Verdict: **MAYBE** — M16 label drill (res05-07, after replacing `Â´` with `´`/`'`); the smack frames are a
   timing reference only.

Lily pads (res05, res06, res07; `Â` removed, `´` kept), 5x9:
```
    _
 ,´   `.
/    1  \
\       /
 \/|..-´
---
    _
 ,´   `.
/    2  \
\       /
 \/|..-´
---
    _
 ,´   `.
/   3   \
\       /
 \/|..-´
```
Note res07 puts `3` at c5, not c6 (a source inconsistency; the `<C-a>` drill should normalise it).

Hammer smack (res19, res20, res21 at the same origin):
```
--- res19 10x22
    ,----,
   /    ' \`.
  / _      . \
 / (,'     |  \
/          |   .
\   /'    _/.  |
 `.   _.-'  ': |.
   `-.      _.`_ `-.
       ` ' "    `._ `,
                   `'
--- res20 10x24
    ___
   /   \`.
  / _   \ `.
 / (/    \  \
/      . ':. \
\_.- '"     '/-.
  `-.___.' `-.  `-.
               `-.  `-.
                  `-.'_}

--- res21 10x24
    __
   / \`.
  /_  \ `
 /(/   \ \
/   ,. '. |
\_.'     '/`-.
  `-.__.'`-.  `-.
            `-.  `-.
               `-.  `-.
                  `-._)}
```

## official-Pets/Dog

Sheets viewed (11): res01, res15, res16, res25-res32. Also opened the unlisted part layers the idle pose depends on:
res02/03 (face), res11-14 (mouth/pant), res17-24 (tail, 3 rows). Source: `~/Downloads/stone-story-official/Pets/Dog.txt`.

Compositing note: in these sheets `#` is transparent and a literal space is OPAQUE (it clears the cell). Composites
below honour that.

1. Depicts: a pet dog following the player.
   - Idle: body res01 at `o@myX@,@myZ@` + face res03 at (+8,+3) + mouth res11-14 at (+8,+4) (pant: `time%100`) +
     TAIL res17-24 at (+0,+5), picked by `time % 10` (0-1 res17, 2 res18, 3 res19, 4 res20, 5-6 res21, 7 res22,
     8 res23, 9 res24) -> an 8-drawing, 10-tick tail-wag loop on a fixed body. Tail also plays during bark.
   - Bark (`stateBark`, 6 ticks): res15 on the first and last tick, res16 (mouth open) between.
   - Jump/gallop (`stateJump`): res25-res30, 2 ticks each (`stateTime/2`), 6-frame run cycle; stop res31 -> res32.
2. Sizes: idle composite 6x15 (IDEAL); bark 6x15 (IDEAL); gallop 7-8 x 16-17 (IDEAL/ACCEPTABLE rows <= 8).
   Glyphs: `´` (U+00B4) and `‾` (U+203E) — ambiguous width, single cell in Western mono fonts.
3. Pairs:
   - Tail wag (composites): res17 -> res18 = 2 cells (r6c2 `` ` `` -> `\`, r6c3 `-` -> `'`): `6G2|R\'<Esc>`.
     res20 -> res21 = 5 cells, res21 -> res22 = 5 cells, res23 -> res24 = 5 cells; res18 -> res19 = 9 cells.
     Tail sweep is a rotation about the rump (r5c5) — the body never changes.
   - Bark res01 -> res15 = 4 cells (ear/brow lift, rows of the pasted bark frames: `1G7|R| <Esc>`, `` 2G8|r` ``, `` 3G9|r` ``); res15 -> res16 = 13
     cells (jaw opens) — a good M3 "one acting feature" change but over 2 rows.
   - Gallop res25 -> res26 ... = 46-76 cells per step: full redraws.
4. Tutor fit: tail wag -> M4 Rotation tween (extremes res17 low / res21 up, midpoint res20, stable pivot at the
   rump, body identical) or M12 Joint sweep (`t`/`f` to the tail cells on rows 4-6). Bark res15 -> res16 -> M3
   Pose copy (copy the key pose, open the mouth). Gallop -> view-only reference for M8.
5. Verdict: **USE** — M4 Rotation tween (tail wag, 6x15); secondary M3 (bark).

Idle tail wag (composites res01+res03+res11 + tail res17..res24):
```
--- idle+res17@0,5 6x15
         |\´/
         / ''-,
      ,-´ `--'
     / _   ;
 ,--', _)\(
 `- ‾`-'  `"
--- idle+res18@0,5 6x15
         |\´/
         / ''-,
      ,-´ `--'
     / _   ;
 ,--', _)\(
 \' ‾`-'  `"
--- idle+res19@0,5 6x15
         |\´/
         / ''-,
      ,-´ `--'
     / _   ;
,--'´, _)\(
'´ ‾ `-'  `"
--- idle+res20@0,5 6x15
         |\´/
         / ''-,
      ,-´ `--'
 _   / _   ;
 \`'´, _)\(
  `‾ `-'  `"
--- idle+res21@0,5 6x15
         |\´/
         / ''-,
      ,-´ `--'
  ,  / _   ;
 (`'´, _)\(
  ‾  `-'  `"
--- idle+res22@0,5 6x15
         |\´/
         / ''-,
      ,-´ `--'
 ,   / _   ;
 \`-´, _)\(
  ‾‾ `-'  `"
--- idle+res23@0,5 6x15
         |\´/
         / ''-,
      ,-´ `--'
     / _   ;
\---', _)\(
 ` ‾ `-'  `"
--- idle+res24@0,5 6x15
         |\´/
         / ''-,
      ,-´ `--'
     / _   ;
 ,--', _)\(
´‾ ‾‾`-'  `"
```

Bark (res15, res16 — drawn without the face layer; tail omitted):
```
--- res01 6x11
     |\´/
     /   -,
  ,-´ `--´
 / _   ;
 , _)\(
 `-'  `"
--- res15 6x11
     |\|
     /  `-,
  ,-´ `--`
 / _   ;
 , _)\(
 `-'  `"
--- res16 6x11
     \``--,
     / _.-'
  ,-´  '
 / _   ;
 , _)\(
 `-'  `"
```

## official-Weapons/RootBats

Sheets viewed (10): res05, res06, res07, res14, res15, res16, res21, res22, res27, res28 (also opened unlisted res04,
res08, res23 because they complete the two cycles). Source: `~/Downloads/stone-story-official/Weapons/RootBats.txt`
(imports `Components/OVERHAUL`, which supplies `base.T`, `base.IRS/ILS`, `base.IRT/ILT`).

1. Depicts: weapon cosmetics. (a) A BAT that flaps over the hammer: `base.T % 20` in 4-tick steps -> res04 (`o1,-1`),
   res05, res06, res07, res08 (`o1,-2`); res14-16 are the left-hand copies. The body contains the runtime
   placeholder `@HE@` / `@HEL@`, which StoneScript replaces with ONE glyph (the item icon) — raw widths overstate
   the rendered width by 3; frames below substitute `=`. (b) A ROOT SPIKE for the wand/staff attack: `base.ILT`
   (item-state timer) 1, 2, 3 -> res21 (`o..,-1`, 5 rows), res22 (`o..,0`, 4 rows), res23 (`o..,2`, 2 rows); the
   base line stays on the same screen row, so the spike retracts into the ground. res27/28 are the right-hand copies
   (identical art).
2. Sizes: bat frames 5x5-5x9 (IDEAL); spike 5x7 (IDEAL). Glyphs `¯ — ´` ambiguous width.
3. Pairs:
   - Spike res21 -> res22 (aligned on the base line): 6 cells = one `| |` shaft row removed and the tip moves down.
     Equal-height edit: `2Gdd` then `ggO<Esc>` (delete a shaft row, re-open a blank top row). res22 -> res23:
     8 cells = two more rows gone: `2G2dd` then `ggO<Esc>O<Esc>`.
   - Bat res04 -> res05 = 19 cells, res05 -> res06 = 15, res06 -> res07 = 17, res07 -> res08 = 12: wing-flap key
     poses, whole wings redrawn.
4. Tutor fit: spike -> M6 Pyramid build (subtractive authoring: author the tallest frame, derive the shorter ones by
   deleting rows, then play them in reverse for "emerge"). Bat -> M4/M3 reference (wing extremes), too many cells.
5. Verdict: **USE** — spike res21/22/23 for M6. Bat flap **MAYBE** (5-frame loop, 12-19 cells per step).

Root spike (res21, res22, res23 aligned on the base line), 5x7:
```
--- res21@0,-1 5x7
  .^.
  | |
  | |
  |||
.—´¯`—.
--- res22 5x7

  .^.
  | |
  |||
.—´¯`—.
--- res23@0,2 5x7



  .^.
.—´¯`—.
```

Bat flap (res04..res08, `@HE@` rendered as `=`), 5 rows x <= 9:
```
--- res04@0,1 5x7

(¯\_/¯)
  (=)
   ¯

--- res05 5x9
.—.   .—.
   \_/
   (=)
    ¯

--- res06 5x7
.     .
 \   /
  \_/
  (=)
   ¯
--- res07 5x6
   _
  /=\
 ( ¯ )
  ` ´

--- res08 5x7
   _
.—´=`—.
`  ¯  ´


```

## official-Pets/CavePets

Sheets viewed (8): res01-res08. Source: `~/Downloads/stone-story-official/Pets/CavePets.txt`.

1. Depicts: five small cave pets, each a `ui.AddAnim` loop (frames split by `%%`, `loop = true`, `flipX = true` —
   the art is authored facing left and MIRRORED at runtime). Walk/wait anims swap on `ai.walking`.
   - res01 "warmer" 4f (duration 12), res02 "licker" 4f (duration 7) — each frame a different pose (18-26 cells).
   - res03 biter walk 4f (15) / res04 biter wait 4f (50, last frame blinks `∞` -> `-`), 2x5.
   - res05 peeler walk 6f (21) / res06 peeler wait 4f (60, blink on f4), 4x10.
   - res07 chopper walk 10f (30 ticks -> 3 per frame; f1-f5 repeat as f6-f10 except the eye is `-` on f1-f2),
     res08 chopper wait 4f (50 -> 12.5 ticks each; f1-f3 identical hold, f4 blink).
2. Sizes: chopper 6x13 (IDEAL), peeler 4x10, biter 2x5, warmer 5-7 x 9, licker 3x7 (all IDEAL).
   Glyphs: `∞` `¯` `´` `─` ambiguous; res01, res02, res07 contain `＂` U+FF02 FULLWIDTH QUOTATION MARK (WIDE,
   unsafe) — replace with `"`.
3. Pairs:
   - Chopper walk res07: body rows 1-3 and 6 never change; legs (rows 4-5) change 6-7 cells per step.
     f1 -> f2: `4G8|R/< <Esc>` + `4G12|r\` + `` 5G8|r` `` + `` 5G12|R `<Esc> `` (7 cells).
     f4 -> f5: 6 cells (`4G9|R^\(<Esc>` + ```` 5G10|R ``<Esc> ````).
   - Chopper wait res08 f3 -> f4: 1 cell (eye `∞` -> `-`): `4G6|r-`; f1-f3 identical = a held pose.
   - Biter walk res03: 4 cells per step on row 2 (`2G0R/∞(|)<Esc>`), but only 2 rows tall.
   - Peeler walk res05: 10-13 cells per step (legs + arms), warmer/licker 8-26 cells.
4. Tutor fit: chopper walk -> M8 Walk study (fixed body, leg-contact cycle, equal frame height, 6 rows); chopper
   wait -> M7 Timed build (3-frame hold + 1-frame blink = holds and timing); the runtime `flipX` makes every one of
   these a natural M18 Hand-mirrored return source (author the right-facing copy by hand).
5. Verdict: **USE** — chopper res07 for M8 (primary), chopper wait res08 for M7; biter/peeler MAYBE.

Chopper walk (res07 f1-f5; `＂` replaced by `"`), 6x13:
```
--- res07 f1 6x12
        ___
      ()`-.\
 ,--. _`__(/
'´¯¯'-.<`(´|
 _,-- /    '
 ¯¯¯´¯
--- res07 f2 6x13
        ___
      ()`-.\
 ,--. _`__(/
'´¯¯'-./< ´\
 _,-- /`    `
 ¯¯¯´¯
--- res07 f3 6x12
        ___
      ()`-.\
 ,--. _`__(/
'´¯¯'∞.|/-´)
 _,-- /'
 ¯¯¯´¯
--- res07 f4 6x12
        ___
      ()`-.\
 ,--. _`__(/
'´¯¯'∞.,\|^
 _,-- /  "
 ¯¯¯´¯
--- res07 f5 6x12
        ___
      ()`-.\
 ,--. _`__(/
'´¯¯'∞.,^\(
 _,-- /   ``
 ¯¯¯´¯
```

Chopper wait (res08 f3 hold, f4 blink):
```
--- res08 f3 6x13
        ___
      ()`-.\
 ,--. _`__(/
'´¯¯'∞.,)´)\
 _,-- / ` ` `
 ¯¯¯´¯
--- res08 f4 6x13
        ___
      ()`-.\
 ,--. _`__(/
'´¯¯'-.,)´)\
 _,-- / ` ` `
 ¯¯¯´¯
```

## official-Foes/FlowerFoes

Sheets viewed (7): res01, res02, res04, res05, res07, res08, res10. Source: `~/Downloads/stone-story-official/Foes/FlowerFoes.txt`.

1. Depicts: flowery re-skins of four foes (huge snail, big snail, ant hill, ant). `colored=false` draws res01-04 as
   single stills; `colored=true` draws each foe as two colour layers at the same `f` offset (green body res05 /
   res07 / res10 + magenta flowers res06 / res08 / res11). No time or state sequencing — every draw is a still.
2. Sizes: 4x6 to 6x10 (IDEAL). Glyphs `¯ ´` ambiguous; source comment has `☆` (not in art).
3. Pairs: res01 vs res05(+06) and res02 vs res07(+08) are the same picture split into colour layers, not frames.
4. Tutor fit: res05 + res06 is a tidy M5 Layered scene example (body layer + flower layer, `#` seams), but it is not
   an animation.
5. Verdict: **REJECT** as animation (stills + colour layers). Note for M5 only as a layering example.

## official-Pets/SnowBunny

Sheets viewed (7): res01, res04-res09 (also unlisted face layers res02 `^.^`, res03 `-.-`).
Source: `~/Downloads/stone-story-official/Pets/SnowBunny.txt`.

1. Depicts: a pet snow bunny. Idle = res01, with res03 `-.-` drawn over the face at (+6,+2) when
   `stateTime % 50 >= 44` (blink: 44 ticks open, 6 ticks closed). Hop (`stateJump`, 12 ticks) = res04, res05,
   res06, res07, res08, res09 at the same origin, 2 ticks each (`stateTime/2`): crouch, push, rise (head to row 1),
   stretch, reach, land.
2. Sizes: 4x10 / 4x11 (IDEAL). All ASCII.
3. Pairs:
   - Idle blink res01 -> res01+res03: 2 cells, r3c7 and r3c9 `n` -> `-`: `3G/n<CR>r-nr-` or `:3s/n/-/g`.
   - Hop res04 -> res05: 6 cells, row 4 only (`,/ _'| "|` -> `  \_'/_"/`): `4G0R  \_'/_"/<Esc>`.
   - res05 -> res06 = 22, res06 -> res07 = 30, res07 -> res08 = 24, res08 -> res09 = 27 cells (whole body moves).
4. Tutor fit: hop -> M9 Bounce capstone (plan key poses: crouch/push/rise/apex/land, then squash on res04 vs
   stretch on res07 — a real anticipation-squash-stretch hop at 4 rows); blink -> M17 Coherent anchors (search `n`,
   replace, `n`, `.`) or M0 readable change.
5. Verdict: **USE** — M9 (hop key poses) and M17 (2-cell blink).

Idle + blink (res01, res01+res03):
```
--- res01 3x8
   (\(\
  ( n.n)
o(,`_"_)
--- res01+res03@6,2 3x8
   (\(\
  ( -.-)
o(,`_"_)
```

Hop (res04..res09, same origin, 2 ticks each):
```
--- res04 4x10

    (\(\
 o__( n.n)
,/ _'| "|
--- res05 4x10

    (\(\
 o__( n.n)
  \_'/_"/
--- res06 4x10

   /( n.n)
 o,- \ " \
 |_.-  " "
--- res07 4x11
   /( n.n)
 o,-' \" \
,/_.-'  " "

--- res08 4x11
    \ \\
 o--( n.n)
= __' \" \
        " "
--- res09 4x11

  o_ \ \\
=_,  ( n.n)
   `-' \" \
```

## official-Pets/Bear

Sheets viewed (6): res01-res05, res11 (also unlisted body layers res06-res10). Source: `~/Downloads/stone-story-official/Pets/Bear.txt`.

1. Depicts: a pet bear drawn as `head[headindex]` (res01-05) at `o@sx@,@sy@` plus `body[bodyindex]` (res06-10)
   5 rows lower. res11 is an ice-cream prop (commented-out draw). Head: 0 = look right `'-'`, 1 = its blink
   `` `-` `` (`totaltime % 90 < 3` adds 1 -> 3-tick blink every 90), 2 = look left `'-'` shifted 1 col (sit),
   3 = its blink, 4 = `>_<` while running. Body: walk cycle index 0-3 advanced every `speed` ticks
   (speed 1-3 by mode), 4 = sitting legs.
2. Sizes: head 5x9 (IDEAL), head+body 8x9 (IDEAL rows 8 > 7 -> ACCEPTABLE). All ASCII.
3. Pairs:
   - Blink res01 -> res02: 2 cells (r4c5, r4c7 `'` -> `` ` ``): `` 4G5|r`2lr` `` (or `` :4s/'/`/g ``).
   - Look res01 -> res03: 4 cells = the face slides 1 col left: `4G4|x$i <Esc>` (delete a space before the face,
     re-insert one before `)` so the contour stays fixed).
   - Wince res04 -> res05: 4 cells: `4G4|R >_<<Esc>`.
   - Walk body res06 -> res07 = 12 cells, res07 -> res08 = 15, res08 -> res09 = 15 (3 leg rows redrawn).
4. Tutor fit: head -> M2 Face focus (expressions edited with `x`, `r`, `R` inside an unchanging round contour; the
   `'-'` -> `>_<` swap is `ci`-like); blink -> M17 or M0; walk body -> M8 reference (12-15 cells, heavier).
5. Verdict: **USE** — M2 Face focus (res01-05), secondary M8 (res06-09).

Head expressions (res01, res02, res03, res05), 5x9:
```
--- res01 5x9
  _   _
 (_)_(_)
 /     \
(   '-' )
 \_____/
--- res02 5x9
  _   _
 (_)_(_)
 /     \
(   `-` )
 \_____/
--- res03 5x9
  _   _
 (_)_(_)
 /     \
(  '-'  )
 \_____/
--- res05 5x9
  _   _
 (_)_(_)
 /     \
(   >_< )
 \_____/
```

Walk (head res01 + body res06, res07, res08, res09), 8x9:
```
--- res01+res06@0,5 8x9
  _   _
 (_)_(_)
 /     \
(   '-' )
 \_____/
 / /  |\
(_/   |_)
  |_|\_)
--- res01+res07@0,5 8x9
  _   _
 (_)_(_)
 /     \
(   '-' )
 \_____/
 | |  ||
 (_)  |)
  |_|_|
--- res01+res08@0,5 8x9
  _   _
 (_)_(_)
 /     \
(   '-' )
 \_____/
  \ \ |
  |\_)|
   \_)|
```

## official-Games/Asteroids

Sheets viewed (5): res01, res02, res03, res04, res08 (also unlisted res05-07: bullet, small/medium rocks).
Source: `~/Downloads/stone-story-official/Games/Asteroids.txt`.

1. Depicts: an Asteroids UI game. res01 title (5x56), res04 starfield (25x85), res08 big rock (4x6 still).
   res02 = ship sprite with 13 `%%` frames: f1-f12 = the ship at 12 headings (30 degrees apart) with the pilot
   `O` as the centre, f13 = explosion; `shipSprite.frame = shipDirection` where `shipDirection =
   modulo(shipDirection + dir, 12)` on input — state-driven rotation, not a timed loop. res03 = engine flame with
   the matching 12 headings (part layer drawn around the ship).
2. Sizes: ship frames 4x9 (IDEAL); flame 1-5 x 11 part layer. Glyphs `´ ‾ ¡ ·` ambiguous width.
3. Pairs: consecutive headings differ by 10-16 cells (f1 -> f2 = 10, f2 -> f3 = 16, f3 -> f4 = 13): the whole hull
   is redrawn around the `O`. No 1-6 cell edit.
4. Tutor fit: M4 Rotation tween as a copy/reference set — a complete 12-step rotation of one small shape around a
   fixed pivot (`O`), useful to show "extremes (f1, f4, f7, f10) and in-betweens". Too many cells per step to
   author as a beginner edit.
5. Verdict: **MAYBE** — M4 reference (res02 f1-f12). Title/starfield/rocks REJECT (UI/stills).

Ship headings (res02 f1-f4 = right, up-right, up-right-steep, up):
```
--- res02 f1 4x7

  |-._
  |  O>
  |-'‾
--- res02 f2 4x7
  .
   / \
  /  O\
  ‾ ‾‾
--- res02 f3 4x7
     _.
  .-´ |
   `.O|
     `'
--- res02 f4 4x8

   \‾‾‾/
    \O/
     '
```

## official-UI/LiveSplit

Sheets viewed (5): res01, res02, res06, res07, res08. Source: `~/Downloads/stone-story-official/UI/LiveSplit.txt`.

1. Depicts: a speed-run split timer UI; the listed sheets are 4-row slanted-letter title banners for locations
   ("Rocky Plateau", "Deadwood Canyon", "Bronze Mine", "Undead Crypt"/"Temple" style wordmarks). No frames.
2. Sizes: 4x20 to 4x48 (IDEAL rows; up to 48 cols -> TOO-WIDE for the side-by-side popup). All ASCII.
3. Pairs: none — different words, not frames.
4. Tutor fit: none for animation (could feed an M1 glyph-geometry "slanted lettering" still, off-scope).
5. Verdict: **REJECT** — UI text banners, not an animation.

## official-Pets/Dracula

Sheets viewed (4): res01-res04. Source: `~/Downloads/stone-story-official/Pets/Dracula.txt`.

1. Depicts: a tiny caped Dracula pet (one `UI.AddAnim` that `Load()`s four anims). res01 `draculanim` 5 frames:
   f1 = standing still, f2-f5 = walk cycle; while following, `time%3=0` advances the frame and frame 0 is skipped,
   so the walk loops f2 f3 f4 f5 at 3 ticks each. res02 `batanim` 4 frames (bat flap, 2 ticks). res03 `poofanim1`
   (Dracula -> smoke -> bat, 5 frames, 2 ticks) and res04 `poofanim2` (bat -> smoke -> Dracula, 5 frames) — the
   same transformation authored in both directions.
2. Sizes: Dracula frames are 7 rows tall in the file but the art occupies rows 5-7 only -> crop 3x7 (IDEAL);
   bat 4-5 x 10; poof 5-7 x 9. Glyphs `¯ ´ ─` ambiguous width.
3. Pairs:
   - Walk f2 -> f3: 1 cell r3c5 ` ` -> `>`: `3G5|r>`. f3 -> f4: `3G5|r|`. f4 -> f5: `3G6|r>`. f5 -> f2: 2 cells
     `3G5|R \<Esc>`. (Rows given for the 3-row crop.)
   - Stand f1 -> walk f2: 10 cells (cape swings out) — a pose copy.
   - Bat f1 -> f2 = 27, f2 -> f3 = 30, f3 -> f4 = 20; poof steps 12-34 cells.
4. Tutor fit: walk -> M0 Spark loop (exactly 3 rows, one readable cell per frame, 4-frame loop); stand -> walk
   -> M3 (copy the key pose, change the cape); poof1/poof2 -> M6 playback order (the same puff played forward and
   reversed) as a reference.
5. Verdict: **USE** — M0 Spark loop (res01 f2-f5). Poof/bat **MAYBE** (M6 reference).

Walk (res01 f1 stand, f2-f5 walk; rows 5-7 cropped), 3x7:
```
--- f1 (stand)
   \(}_
  ,' ¯/
 '-_.'
--- f2
   \(}_
.-´  ,'
 ¯-´ \
--- f3
   \(}_
.-´  ,'
 ¯-´>\
--- f4
   \(}_
.-´  ,'
 ¯-´|\
--- f5
   \(}_
.-´  ,'
 ¯-´|>
```

## official-Foes/PumpkinWraith

Sheets viewed (3): res01, res02, res03. Source: `~/Downloads/stone-story-official/Foes/PumpkinWraith.txt`.

1. Depicts: a jack-o'-lantern head drawn over the acronian cultist: res01 pumpkin shell (orange), res02 eyes/mouth
   (colour alternates yellow/white every tick — a colour flicker, not new art), res03 stem (brown), all three at the
   same offset. One still picture in three colour layers.
2. Size: 4x10 (IDEAL). Glyph `´` ambiguous.
3. Pairs: none — layers of one still; the only change over time is colour.
4. Tutor fit: M5 Layered scene example at most (shell / face / stem layers with `#` gaps).
5. Verdict: **REJECT** — not an animation (colour-only flicker, part layers).

## official-Hats/CatHat

Sheets viewed (3): res04, res05, res10 (also opened unlisted res01-03, res06-09 tail frames, res11 body, res12-16
ears to reconstruct the cycle). Source: `~/Downloads/stone-story-official/Hats/CatHat.txt`.

1. Depicts: a cat curled on the player's head (`>h` = head-relative). Body res11 (`h-3,-2`) is always drawn; the
   TAIL cycles on `time % 81`: res04 (upright curl, held 63 ticks) then res05, res06, res07, res08, res09, res10
   for 3 ticks each (a tail whip around the body and back), each at its own `h` offset (x -6..-8, y -1..-4). The
   ears/head res14-16 twitch on `time % 114` (3-tick flick). In icy areas a faster 3-frame shiver (res01-03,
   `time % 9`) replaces the tail.
2. Sizes: body + tail composite 5x11 (IDEAL); listed sheets alone 4x4-4x5. Glyphs `· ì • ´ ¯` ambiguous width.
3. Pairs (composites with the body): res04 -> res05 = 9 cells (tail tip flips `)`,` -> `(`.,`):
   `2G2|R(`.,<Esc>` + `1G3|R, <Esc>` + `3G2|R' <Esc>`; res05 -> res06 = 18, res06 -> res07 = 16, res07 -> res08
   = 15, res08 -> res09 = 14, res09 -> res10 = 10 cells. The tail moves around the body, so most steps are
   whole-tail redraws.
4. Tutor fit: M12 Joint sweep / M4 reference (a tail sweeping around a fixed pivot at the body), and M7 Timed build
   for its timing (one 63-tick hold, then six 3-tick frames). Too many cells per step for a beginner edit except
   res04 -> res05.
5. Verdict: **MAYBE** — timing reference for M7 and sweep reference for M12.

Tail whip (tail res04..res10 at their `h` offsets + body res11), 5x11:
```
--- tail res04 + body res11 5x11
   ,
   )`,
  (  ;/` ,|
  `-·(_`,|;

--- tail res05 + body res11 5x11
  ,
 (`.,
 '   ;/` ,|
  `-·(_`,|;

--- tail res06 + body res11 5x11


,_.-·./` ,|
`.   (_`,|;
   '´
--- tail res07 + body res11 5x11


      /` ,|
_,•´¯(_`,|;
`. _.'
--- tail res08 + body res11 5x11


 ,'¯¯`/` ,|
;•´-,(_`,|;

--- tail res09 + body res11 5x11

,-~-,
¯\   `/` ,|
  `-·(_`,|;

--- tail res10 + body res11 5x11
  ,
  ì`.
  ;  :/` ,|
  `-·(_`,|;

```

## official-Cosmetics/Turret

Sheets viewed (2): res02, res12 (also opened unlisted res03-05, res11, res13 for context).
Source: `~/Downloads/stone-story-official/Cosmetics/Turret.txt`.

1. Depicts: a "mount 3" wheeled turret skin. res02 = a HUD icon drawn at screen `` `0,10 `` (a plunger/detonator,
   5x9); res12 = the turret itself at `o-1,1` (4x6, one still). Weapon-state stick figures res03-08 (3 rows) and
   walking wheel dashes res09-11 (1 row, `time % 30`) are separate part layers at other origins.
2. Sizes: res02 5x9, res12 4x6 (IDEAL). Glyphs: `§ │ — ‾ ´ ° ═ ╤ ╧` ambiguous; res12 contains `］` U+FF3D
   (FULLWIDTH, WIDE — unsafe).
3. Pairs: none between the listed sheets (different subjects at different origins); the only timed change is the
   1-row wheel layer.
4. Tutor fit: none.
5. Verdict: **REJECT** — two unrelated stills (HUD icon + turret); animation lives in 1-3 row part layers.

## official-Games/Metallophone

Sheets viewed (2): res01, res02. Source: `~/Downloads/stone-story-official/Games/Metallophone.txt`.

1. Depicts: a piano/metallophone keyboard UI. res01 `key1` = one octave with its left border, drawn at screen x 0;
   res02 `key2` = the same octave without the left border, tiled at x 28 and 56. Tiles of one still keyboard.
2. Sizes: 8x29 each (TOO-LARGE for two side by side; ACCEPTABLE rows, 29 cols).
3. Pairs: res01 vs res02 differ only in column 1 (border) — tiling, not frames.
4. Tutor fit: M15 Texture ground at most (repeated key pattern, macro practice), not animation.
5. Verdict: **REJECT** — UI tiles, not an animation.

## official-Hats/WitchHat

Sheets viewed (2): res01, res02 (also unlisted res03/res04, the small-hat pair). Source: `~/Downloads/stone-story-official/Hats/WitchHat.txt`.

1. Depicts: a witch hat. Big-head mode draws res01 (brim+cone top, `h-5,-3`) and res02 (`h-5,-2`) together as
   two colour layers whose colours are lerped by `math.sin(time*0.05)` — a colour shimmer; res03/res04 are the
   small-head version. The art never changes over time.
2. Sizes: 5x10 / 4x10 (IDEAL). Glyphs `´ · ─` ambiguous.
3. Pairs: none — res01 and res02 overlap as top/bottom colour layers of one hat.
4. Tutor fit: M5 Layered scene (two overlapping colour layers offset by one row) at most.
5. Verdict: **REJECT** — colour-only animation; part layers of one still.

## official-UI/OkamiroyUtils

Sheets viewed (2): res01, res02. Source: `~/Downloads/stone-story-official/UI/OkamiroyUtils.txt`.

1. Depicts: utility UI panels — a "Time" box (res01) and a "Statistics" box (res02) whose values are printed over
   them by `ShowTimer` / `ShowTimeStats`. No frames.
2. Sizes: 6x8 and 7x14. Glyphs: double box drawing `╔═╗║╚╝` (ambiguous width).
3. Pairs: none.
4. Tutor fit: none.
5. Verdict: **REJECT** — UI panels, not an animation.

## Summary

Counts (by set): USE 8, MAYBE 3, REJECT 10 (21 sets; all 220 listed sheets opened, plus the unlisted part layers named per set).

| set | frames | size | verdict | best module | proposed edit |
|---|---|---|---|---|---|
| official-Cosmetics/SillyGoose | walk 12 (feet 4-cycle), eat 6, combat 2 | 7x8 (walk), 7x11 (eat) | USE | M8 Walk study (also M4 neck tween) | walk feet `7G0R  <   v<Esc>` (4 cells, row 7 only) |
| official-Cosmetics/Knight | walk 8, sword 18 | 16x31 | REJECT | - | walk steps are 52-65 cells |
| official-Games/TowerDefense | heli 4, wasp 4, missile 4, copter 8 (+ others) | 6x9 heli, 4x7 wasp, 3x10 missile | USE | M4 Rotation tween (heli rotor); M0 (wasp); M13 (exhaust) | heli `1G3\|r 6lr ` (2 cells); wasp `1G2\|r\3lr/` (2 cells) |
| official-Cosmetics/Bolesh | state-driven arm poses | 8x13-8x21 composites | REJECT | - | 9-45 cells, part layers |
| official-UI/Calculator | 0 (3 sizes of one UI) | 20-23 x 15-28 | REJECT | - | - |
| official-Games/FrogBog | smack 3 (2/2/3 ticks); pads 1/2/3 | 10x24; 5x9 | MAYBE | M16 (`<C-a>` pad labels); M9 timing ref | `3G6\|<C-a>` |
| official-Pets/Dog | tail wag 8 (10 ticks), bark 2, gallop 6 | 6x15 | USE | M4 Rotation tween (tail), M3 (bark) | tail `6G2\|R\'<Esc>` (2 cells) |
| official-Weapons/RootBats | spike 3 (retract), bat 5 | 5x7; 5x9 | USE (spike) / bat MAYBE | M6 Pyramid build | `2Gdd` + `ggO<Esc>` (remove a shaft row, keep height) |
| official-Pets/CavePets | chopper walk 10 (5 unique), chopper wait 4, others | 6x13 | USE | M8 Walk study; M7 (wait hold + blink) | wait blink `4G6\|r-` (1 cell); walk f1->f2 7 cells rows 4-5 |
| official-Foes/FlowerFoes | 0 (stills in colour layers) | 4x6-6x10 | REJECT | (M5 layering example only) | - |
| official-Pets/SnowBunny | hop 6 (2 ticks), blink 2 | 4x11 | USE | M9 Bounce capstone (hop); M17 (blink) | blink `:3s/n/-/g` (2 cells); hop res04->05 `4G0R  \_'/_"/<Esc>` |
| official-Pets/Bear | head 5 expressions, body walk 4 | 5x9 head, 8x9 walk | USE | M2 Face focus | look `4G4\|x$i <Esc>`; blink `` 4G5\|r`2lr` `` |
| official-Games/Asteroids | ship 12 headings + explosion | 4x9 | MAYBE | M4 reference | 10-16 cells per heading |
| official-UI/LiveSplit | 0 (word banners) | 4x20-4x48 | REJECT | - | - |
| official-Pets/Dracula | walk 4 (3 ticks) + stand; bat 4; poof 5+5 | 3x7 (crop) | USE | M0 Spark loop | `3G5\|r>` -> `3G5\|r\|` -> `3G6\|r>` (1 cell each) |
| official-Foes/PumpkinWraith | 0 (colour flicker) | 4x10 | REJECT | - | - |
| official-Hats/CatHat | tail 7 (63-tick hold + six 3-tick frames) | 5x11 | MAYBE | M7 timing / M12 sweep reference | res04->05 9 cells |
| official-Cosmetics/Turret | 0 (two stills) | 5x9, 4x6 | REJECT | - | - |
| official-Games/Metallophone | 0 (UI tiles) | 8x29 | REJECT | - | - |
| official-Hats/WitchHat | 0 (colour lerp) | 5x10 | REJECT | - | - |
| official-UI/OkamiroyUtils | 0 (UI panels) | 6x8, 7x14 | REJECT | - | - |

Counting note: RootBats is counted as USE (spike); its bat flap is a MAYBE inside that set. MAYBE sets: FrogBog,
Asteroids, CatHat, and (within USE sets) TowerDefense copter, CavePets biter/peeler, Dracula bat/poof, RootBats bat.
Wide-glyph hazards to normalise before import: `］` U+FF3D (SillyGoose res42/44, Knight res19-21, Turret res12),
`＂` U+FF02 (CavePets res01/02/07), `Â` mojibake (FrogBog res05-07).

