# Local source-excerpt provenance register

**Recorded:** 2026-09-29 (America/New_York)
**Scope:** local tutor evidence only
**Publication (updated 2026-09-29, VD-60):** the operator confirmed rights for the
Stone Story RPG excerpts ("StoneScript people use everywhere, just cite the
author/Stone Story RPG"); they are published with credit to Gabriel Santos,
Martian Rex, Inc. A second confirmation the same day (VD-61: "same with AAHub and the rest,
credit") covers the AAHub `bakuhatsu-kemuri` rows below
(aahub.org/mlt/a60392576bd5eefca3ed22d55606b85f) and the non-Stone-Story
`share/art.json` pieces (jgs = Joan G. Stark; "pb"; "tre"; candle unknown),
each credited in the README and in art.json `credit`. The paragraph below is the original 2026-09-29 record.
**Original status:** blocked; do not push the 53 local commits that contain these excerpts

This register resolves the exact local files used by `share/stone_story_variants.py`
and the source-backed `.06` transfers in `share/gen_curriculum_v2.py`. It does
not grant redistribution permission and it does not add any source sheet to the
repository. The operator authorized local tutor use in VD-18; no license or
permission text authorizing publication was found. The repository therefore
remains intentionally ahead of `origin/main` and must not be pushed as part of
curriculum verification.

## Roots and transformations

- Stone Story extraction root:
  `/Users/r/Downloads/stone-story-consolidated/`.
- AAHub extraction root:
  `/Users/r/Downloads/aahub-consolidated/bakuhatsu-kemuri/`.
- Stone Story manifests identify their upstream script path, for example
  `official/Cosmetics/AcronianGuardian.txt`; they do not contain a license or
  redistribution grant.
- Exact excerpts preserve source glyph order. Documented tutor transforms are:
  `#` transparency to spaces, removal of trailing transparent cells, a crop,
  fixed tutor rails, a visible palette label, or an explicitly named learner
  edit. Snail's source `@` spiral is adapted to `O` for the tutor alphabet.
- The AAHub rows come from the rendered DOM extraction documented by that
  corpus's `manifest.txt`; the source page and Saitamaar rendering metadata are
  external evidence, not a redistribution grant.

## Exact Stone Story file sets

Each set digest is SHA-256 over one UTF-8 line per listed file:
`filename<TAB>sha256(file bytes)<LF>`, in the displayed order. This binds both
the file list and every source byte without copying the sheets into this repo.

| Relative directory | Exact files used | Set digest |
|---|---|---|
| `official-Cosmetics/AcronianGuardian` | `res06.txt, res07.txt, res08.txt, res10.txt, res11.txt, res12.txt` | `2fa21342db71975aab06a15929933b359598cd2fed6a00c0f949f57daeeac8bc` |
| `official-Cosmetics/CaveParty` | `res06.txt` | `f43067b71704493ac5e598eef2fcd8380c5dcce278fd6c0ee7cc4121fff5a8aa` |
| `official-Cosmetics/Drill` | `res04.txt, res26.txt` | `4fb20450b31f64e64376e1bc4a07a2d578ac27032a97a0e71512d90ccedec3bd` |
| `official-Cosmetics/Fireworks` | `res03.txt, res06.txt` | `486aa8998ee2fab16c4ab4810bfc6de6dda17d4d1855f39b204be1bd9767fa1f` |
| `official-Foes/PallasCrown` | `res01.txt, res02.txt, res03.txt, res04.txt` | `31562760ad43f8ad84f440ebafb8ad9b6e2494aaa8a08500a4207a9742249d24` |
| `official-Games/FrogBog` | `res05.txt, res06.txt, res07.txt` | `a087a31dfb0a764d9f18249599084dc54e76c65c3c5b023f9451cbe1ec8439de` |
| `official-Games/GrowPlants` | `res03.txt` | `921c5db0605aac3590ede1fa727567fe1fd88dfacd03325caf105e1dad805f69` |
| `official-Games/TowerDefense` | `res18.txt` | `a9156a6ccef293f958ad509aca288bff03ce2655f17a319c4a21d66517d17c7a` |
| `official-Hats/IroncladMask` | `res01.txt, res02.txt, res03.txt, res04.txt` | `147afd58a44dbfe246d70c7684f1fecd2ac28286fa7891372ed2ce21d86786d1` |
| `official-Hats/Skully` | `res01.txt, res02.txt, res04.txt, res06.txt` | `d3275fc6d04a8453fd61e5214cd4aed4071be30d00d7b73da4957f9fd48f0ce6` |
| `official-Pets/Boo` | `res01.txt` | `a7467903cc9f5b32753b3d69d5b1c726b70b2f00e8bd642a90a1d7da35aa21e1` |
| `official-Pets/Chick` | `res01.txt, res03.txt` | `8e2ca9f017ddb1721a01773c4f82f7871e42d45ba5fec6eb2a0d47e88d21e1b6` |
| `official-Pets/Cranius` | `res01.txt, res04.txt, res06.txt, res07.txt` | `5f89de896783fe202c177f2526ffb917efa686cc7bd3f9418e0946417597a5d3` |
| `official-Pets/Dracula` | `res01.txt` | `f7cf1b71c32322bafb77bd42a6ab05d0a4d3cc082b86c990557289f87f19e04e` |
| `official-Pets/Frog` | `res01.txt, res05.txt, res06.txt, res07.txt` | `085421846810925b7ae6755eb8fabf9edba554406ecc9e6381dc4b6004477160` |
| `official-Pets/Skully` | `res01.txt, res02.txt, res04.txt, res06.txt` | `76b43288fa66c47924e9068388730694f27eb913354dbbbec200f5365e5234ba` |
| `official-Pets/Snail` | `res05.txt, res06.txt, res07.txt, res12.txt, res13.txt, res14.txt, res15.txt, res28.txt, res29.txt, res30.txt, res31.txt, res32.txt, res33.txt, res34.txt, res35.txt` | `aa7c9ccbb9c51eca55c7d3796c02298adccdea258422fda441bd60839271361e` |
| `official-Pets/Snake` | `res01.txt, res04.txt, res05.txt, res06.txt` | `55bd94b5f6f5601833f761f973748cdae9e1341b03fda98b409da1e7861fbfb9` |
| `official-Pets/SnowBunny` | `res01.txt, res03.txt` | `cc76da65d09f672d801c1d6a4a43f1336353e4b5021166b348f8c5c8cbe91f62` |
| `official-Pets/Snowman` | `res01.txt, res06.txt, res08.txt` | `3dcd0bda4d8e4d64a2d7516bf9391cca0ccbc1a99be28c50f3f5a3bc2e691482` |
| `official-UI/FaceHUD` | `res02.txt, res08.txt, res10.txt` | `4dbe5e5f881d6a147aef8e48ea2f3ac93b830bb92d473cf80e82fc13ebfea050` |

## Exact AAHub files

| Relative file | SHA-256 of file bytes | Tutor use |
|---|---|---|
| `bakuhatsu-kemuri/resK-119.txt` | `1621910df0406de69cce42dd1a794a6ce43d36184f8b05f7953d32f4fef9c1cb` | M10.06 base: first complete four-row smoke puff, one glyph redacted for retrieval |
| `bakuhatsu-kemuri/resK-123.txt` | `0d578d7275d4a558e0430833a534b52a7d50d5f7f959271c455f3c58d86b1ef7` | M10.06 alternate: first complete three-row puff, one glyph redacted for retrieval |

## Curriculum linkage

- Primary transfers: M0 Fireworks; M1 AcronianGuardian; M2 Frog/Skully;
  M3 FaceHUD; M4 TowerDefense/Chick; M5 IroncladMask; M6 FrogBog;
  M7 Skully/Frog; M8 Dracula; M9 Boo; M10 AAHub smoke; M11 Snail;
  M12 Snowman; M13 Fireworks; M14 Skully/SnowBunny; M15 Drill/CaveParty;
  M16 FrogBog; M17 Cranius; M18 PallasCrown; M19 AcronianGuardian.
- Spaced changed-art reviews additionally use TowerDefense, Chick, Dracula,
  Frog, Skully, SnowBunny, Snake, GrowPlants, Hats/Skully, Fireworks,
  FrogBog, Drill, CaveParty, and FaceHUD. Their per-card `source` strings are
  generated into `share/curriculum-v2.json` and exercised by
  `share/test_stone_story_variants.py`.

## Boundary that remains open

This is a provenance index, not archive ingestion and not publication
clearance. `ascii-art-archive/MANIFEST.tsv` still has no rows for the 885-sheet
animation corpus. Copying those sheets into that archive or pushing the local
tutor commits would publish third-party material. Either action remains
blocked until the operator supplies a redistribution decision with exact
scope, notice requirements, and source ownership evidence.
