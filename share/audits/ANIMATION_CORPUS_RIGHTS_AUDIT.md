# Animation corpus source, use, and rights audit

**Audit date:** 2026-09-28 (America/New_York)  
**Owner:** standalone animation lesson-pack research  
**Decision:** research-only. No source sheet, tutorial plate, HTML art, game asset,
font, screenshot, GIF, or lightly edited derivative is vendored by this lesson
pack. Any exact-source integration is **blocked** until the owner records a
license and redistribution permission that covers this repository.

> **2026-09-29 status correction.** This document records the boundary at its
> 2026-09-28 audit date. The operator later authorized exact excerpts for the
> local tutor only; revision `.54` contains 70 changed-art review banks, with
> 92 variant rows citing 16 `official-*` subjects. That local-use decision did
> **not** supply a redistribution license
> or authorize a push from this public repository. Statements below saying
> “0 tutor use” are historical measurements, not the current tree. Archive
> provenance intake and the publication decision remain open.

## Executive decision

The local Stone Story corpus is valuable evidence for *animation structure* but
not cleared lesson content. The pack may teach general, transferable techniques
such as extremes, breakdowns, holds, arcs, layer offsets, and registration. It
must use newly authored, small geometric exercises. The following are
reference-only and remain outside `share/`:

| Evidence family | Exact local evidence | Observed use | License / permission finding | Integration decision |
|---|---|---|---|---|
| Animation-grade extracted corpus | `/Users/r/Downloads/stone-story-consolidated/official-*/.../res*.txt`; the complete relative-file inventory is `share/audits/animation-frame-paths.txt:1-972` | 86 sets, 885 sheets, 0 archive MANIFEST rows, 0 tutor use. Used only for counts and technique selection. | No license, copyright notice, or redistribution grant is present in the corpus root or representative set manifests. | **Blocked:** do not copy, vendor, quote, or make a substantially similar derivative. |
| In-archive Sacrificial Pit plate | `/Users/r/Projects/ascii-art-archive/collections/y9-2-articles/2026-09-07-stone-story-video-transcripts-media/o5v-NS9o4yc/ascii-tutorial-page/01-sacrificial-pit-layers.txt` (1,122 lines; SHA-256 `749ecc92194cef6348af596cc09b05f7f7781bfd6eaf16cba025729c5d8e94c6`) and duplicate archive copy under `collections/glyph-morph/assets/glyphs/authored/stone_story_tutorial_plates/` | Layer/frame ordering evidence only; not imported into this repository. | `MEDIA.md` records the tutorial page as third-party creator work and the page copyright as `Martian Rex, Inc. 2020`; no redistribution license was found. | **Blocked:** cite section/rules, never ship the plate or a near-copy. |
| Sapling & Ramparts | `/Users/r/Projects/ascii-art-archive/collections/downloads/ssrpg Sapling & Ramparts.txt` (355 lines; SHA-256 `33c6f56f906cc691d06abbdb177a2a7bd92091c7c7fd687b907a39ebb96c24ac`); original download is indexed at `docs/reference-art-index.txt:74` as local-game-derived | Look-target and provenance lead only. | Index says `blank:local-game-derived`; no license or permission grant was found. | **Blocked:** no frames, outlines, or recognizable reconstruction. |
| Tutorial HTML and inline examples | `/Users/r/Projects/ascii-art-archive/collections/y9-2-articles/2026-09-07-stone-story-video-transcripts-media/o5v-NS9o4yc/ascii-tutorial-page/ascii_tutorial.html` (1,584 physical lines; SHA-256 `f97bfaa11f9611c4aea5f3925b54f8a2c3e8ffeb21059ed86a34d6c51a607425`), extracted text at `ascii_tutorial-extracted.txt` (1,568 lines; SHA-256 `6eb5ec0e09fabd05bff8f305a578a1c756eb013d48facad38f928b3291609428`) | Sections 12–14 inform vocabulary and sequence design; worm/dome/brick/logo material is not lesson art. | Page contains `Copyright Martian Rex, Inc. 2020` at HTML line 1,577 / extracted line 1,562; platform page supplies no reuse license. | **Blocked:** no HTML art, logo, worm, dome, brick, or other page block may be copied or lightly transformed. |

“Blocked” is an engineering/content gate, not a legal conclusion. A future
clearance record must identify the rightsholder, exact files, grant text, scope,
notice requirements, and intended transformation before changing this decision.

## Method and count reconciliation

The input inventory is `share/audits/animation-frame-paths.txt`. Its header
states: animation-grade sets require at least two distinct full-pose blocks of
at least four lines; base path `~/Downloads/stone-story-consolidated/`; zero
MANIFEST rows; and zero tutor use. The file contains 86 set headers and 885
listed `res*.txt` sheets (the 86/885 totals are independently reproducible by
counting headers and indented paths).

For this audit, “distinct poses” means the number of distinct SHA-256 hashes of
normalized `res*.txt` contents after retaining files with at least four lines.
Normalization is only CRLF-to-LF conversion and removal of terminal newlines;
the art bytes are not saved here. This explains why a manifest's `blocks` count
can exceed the distinct-pose count: a set may contain duplicate blocks or
short/part-only material. The 158 singleton/part-only directories reported by
the source audit remain excluded.

The pack does not depend on any exact pose count for grading; these values are
research evidence used to prioritize lesson concepts.

## Qualifying-set inventory

Every row below is a qualifying set from `animation-frame-paths.txt`. `sheets`
is the number of listed local files. `distinct full poses` is the direct local
hash count described above. `source directory` is deliberately absolute so a
future reviewer can resolve the evidence without guessing a repository root.

| Set | Sheets | Distinct full poses | Source directory |
|---|---:|---:|---|
| `official-Cosmetics/Acrocorn` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/Acrocorn` |
| `official-Cosmetics/AcronianGuardian` | 12 | 10 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/AcronianGuardian` |
| `official-Cosmetics/Beach` | 6 | 6 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/Beach` |
| `official-Cosmetics/Bolesh` | 17 | 10 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/Bolesh` |
| `official-Cosmetics/CaveParty` | 17 | 17 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/CaveParty` |
| `official-Cosmetics/ChristmasTree` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/ChristmasTree` |
| `official-Cosmetics/ConfettiHead` | 8 | 8 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/ConfettiHead` |
| `official-Cosmetics/CultGroup` | 15 | 15 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/CultGroup` |
| `official-Cosmetics/Drill` | 3 | 3 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/Drill` |
| `official-Cosmetics/Fireworks` | 7 | 7 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/Fireworks` |
| `official-Cosmetics/Knight` | 34 | 27 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/Knight` |
| `official-Cosmetics/Mech` | 52 | 49 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/Mech` |
| `official-Cosmetics/MineManager` | 12 | 5 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/MineManager` |
| `official-Cosmetics/MushroomAnt` | 6 | 6 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/MushroomAnt` |
| `official-Cosmetics/MushroomHead` | 7 | 7 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/MushroomHead` |
| `official-Cosmetics/Party` | 12 | 8 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/Party` |
| `official-Cosmetics/Portobello` | 4 | 4 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/Portobello` |
| `official-Cosmetics/PumpkinCarving` | 3 | 3 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/PumpkinCarving` |
| `official-Cosmetics/Pumpkins` | 3 | 3 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/Pumpkins` |
| `official-Cosmetics/SillyGoose` | 44 | 26 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/SillyGoose` |
| `official-Cosmetics/SpringBloom` | 13 | 13 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/SpringBloom` |
| `official-Cosmetics/StoneClause` | 8 | 8 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/StoneClause` |
| `official-Cosmetics/StoneHeadless` | 8 | 8 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/StoneHeadless` |
| `official-Cosmetics/SuperStoneHead` | 6 | 6 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/SuperStoneHead` |
| `official-Cosmetics/TheSun` | 4 | 4 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/TheSun` |
| `official-Cosmetics/Turret` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/Turret` |
| `official-Cosmetics/TwinSuns` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-Cosmetics/TwinSuns` |
| `official-Foes/FlowerFoes` | 7 | 7 | `/Users/r/Downloads/stone-story-consolidated/official-Foes/FlowerFoes` |
| `official-Foes/PallasCrown` | 5 | 5 | `/Users/r/Downloads/stone-story-consolidated/official-Foes/PallasCrown` |
| `official-Foes/PumpkinWraith` | 3 | 3 | `/Users/r/Downloads/stone-story-consolidated/official-Foes/PumpkinWraith` |
| `official-Games/2048` | 3 | 3 | `/Users/r/Downloads/stone-story-consolidated/official-Games/2048` |
| `official-Games/Arena` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-Games/Arena` |
| `official-Games/Asteroids` | 5 | 5 | `/Users/r/Downloads/stone-story-consolidated/official-Games/Asteroids` |
| `official-Games/BurgerRush` | 18 | 18 | `/Users/r/Downloads/stone-story-consolidated/official-Games/BurgerRush` |
| `official-Games/FeedABat` | 5 | 5 | `/Users/r/Downloads/stone-story-consolidated/official-Games/FeedABat` |
| `official-Games/FrogBog` | 12 | 12 | `/Users/r/Downloads/stone-story-consolidated/official-Games/FrogBog` |
| `official-Games/FrogJump` | 22 | 8 | `/Users/r/Downloads/stone-story-consolidated/official-Games/FrogJump` |
| `official-Games/GrowPlants` | 3 | 3 | `/Users/r/Downloads/stone-story-consolidated/official-Games/GrowPlants` |
| `official-Games/KillerRPG` | 7 | 7 | `/Users/r/Downloads/stone-story-consolidated/official-Games/KillerRPG` |
| `official-Games/Metallophone` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-Games/Metallophone` |
| `official-Games/PlayingCards` | 3 | 3 | `/Users/r/Downloads/stone-story-consolidated/official-Games/PlayingCards` |
| `official-Games/SpearThrowing` | 18 | 18 | `/Users/r/Downloads/stone-story-consolidated/official-Games/SpearThrowing` |
| `official-Games/StoneasaurGame` | 11 | 11 | `/Users/r/Downloads/stone-story-consolidated/official-Games/StoneasaurGame` |
| `official-Games/TowerDefense` | 21 | 21 | `/Users/r/Downloads/stone-story-consolidated/official-Games/TowerDefense` |
| `official-Games/WhackaMole` | 11 | 11 | `/Users/r/Downloads/stone-story-consolidated/official-Games/WhackaMole` |
| `official-Hats/CatHat` | 3 | 3 | `/Users/r/Downloads/stone-story-consolidated/official-Hats/CatHat` |
| `official-Hats/IroncladMask` | 4 | 4 | `/Users/r/Downloads/stone-story-consolidated/official-Hats/IroncladMask` |
| `official-Hats/MushroomHat` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-Hats/MushroomHat` |
| `official-Hats/Skully` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-Hats/Skully` |
| `official-Hats/StarCloak` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-Hats/StarCloak` |
| `official-Hats/Treeman` | 3 | 3 | `/Users/r/Downloads/stone-story-consolidated/official-Hats/Treeman` |
| `official-Hats/WitchHat` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-Hats/WitchHat` |
| `official-Pets/Bear` | 6 | 6 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Bear` |
| `official-Pets/BlackHole` | 4 | 4 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/BlackHole` |
| `official-Pets/Boo` | 5 | 5 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Boo` |
| `official-Pets/Bunny` | 10 | 10 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Bunny` |
| `official-Pets/CatBalloon` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/CatBalloon` |
| `official-Pets/CavePets` | 8 | 8 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/CavePets` |
| `official-Pets/Chick` | 7 | 7 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Chick` |
| `official-Pets/Crab` | 10 | 9 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Crab` |
| `official-Pets/Cranius` | 45 | 21 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Cranius` |
| `official-Pets/Dog` | 11 | 11 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Dog` |
| `official-Pets/Dracula` | 4 | 4 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Dracula` |
| `official-Pets/Dragon` | 29 | 28 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Dragon` |
| `official-Pets/FoesNoMore` | 20 | 18 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/FoesNoMore` |
| `official-Pets/Frog` | 7 | 7 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Frog` |
| `official-Pets/LegsTurkey` | 27 | 23 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/LegsTurkey` |
| `official-Pets/Mushroom` | 18 | 18 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Mushroom` |
| `official-Pets/Panda` | 28 | 28 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Panda` |
| `official-Pets/Skully` | 46 | 37 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Skully` |
| `official-Pets/Snail` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Snail` |
| `official-Pets/Snake` | 10 | 10 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Snake` |
| `official-Pets/SnowBunny` | 7 | 7 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/SnowBunny` |
| `official-Pets/Snowman` | 22 | 17 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Snowman` |
| `official-Pets/Stonehead` | 8 | 8 | `/Users/r/Downloads/stone-story-consolidated/official-Pets/Stonehead` |
| `official-UI/CDTime` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-UI/CDTime` |
| `official-UI/Calculator` | 15 | 15 | `/Users/r/Downloads/stone-story-consolidated/official-UI/Calculator` |
| `official-UI/FaceHUD` | 12 | 11 | `/Users/r/Downloads/stone-story-consolidated/official-UI/FaceHUD` |
| `official-UI/LiveSplit` | 5 | 5 | `/Users/r/Downloads/stone-story-consolidated/official-UI/LiveSplit` |
| `official-UI/OkamiroyUtils` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-UI/OkamiroyUtils` |
| `official-UI/RecordPlayer` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-UI/RecordPlayer` |
| `official-Weapons/EmbueDaggers` | 6 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-Weapons/EmbueDaggers` |
| `official-Weapons/MajVines` | 6 | 6 | `/Users/r/Downloads/stone-story-consolidated/official-Weapons/MajVines` |
| `official-Weapons/PsyCrusher` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-Weapons/PsyCrusher` |
| `official-Weapons/RootBats` | 10 | 8 | `/Users/r/Downloads/stone-story-consolidated/official-Weapons/RootBats` |
| `official-Weapons/Scythe` | 2 | 2 | `/Users/r/Downloads/stone-story-consolidated/official-Weapons/Scythe` |

The highest-evidence sets are therefore Mech (52 sheets / **49 poses**), Skully
(46 / **37**), Panda (28 / **28**), Dragon (29 / **28**), Knight (34 / **27**),
TowerDefense (21 / **21**), BurgerRush (18 / **18**), FaceHUD (12 / **11**),
and Calculator (15 / **15**). The corresponding audit headers are at
`animation-frame-paths.txt:101,136,369,480,662,768,797,901,917`; representative
manifests report raw block counts of 52, 46, 32, 29, 34, 27, 22, 16, and 12,
respectively, which is why this audit does not call raw manifest blocks “poses.”

## Source-to-lesson boundary

The standalone pack at `share/animation_lesson_pack.md` contains no source art.
Its exercises are original: abstract beacons, kites, rings, ribbons, reeds,
lanterns, and other small geometry authored for this pack. The source corpus is
used only to select a technique and to justify why a lesson needs a particular
check. Each lesson names the applicable evidence path without importing its
glyphs. The pack's validator rejects a missing rights gate, missing question
audit, missing changed-art review, missing habit/stage mapping, or a missing
“integration blocked” statement.

## Re-audit checklist for future integration

Before any exact source use, a reviewer must answer all of these in a new audit
entry: (1) who owns the exact file; (2) where the license/permission text is;
(3) whether redistribution and derivative lessons are covered; (4) what notice
must ship; (5) whether the proposed transformation is more than a substantial
similarity; (6) whether the source is still excluded from the tutor and generated
curriculum; and (7) whether the lesson's question is answerable from prior
teaching, unambiguous about its requested format, and placed after the concepts
it presupposes. Until all seven are evidenced, keep `integration: blocked`.
