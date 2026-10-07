# Legacy curriculum disposition

This is the release-gate decision record for all 46 stable drill IDs in
`curriculum.json`. It deliberately distinguishes three states:

- `adapted`: the legacy command family is executable in an animation-specific
  v2 key path.
- `partial`: v2 teaches the larger idea, but not every operation in the legacy
  recipe. The named gap remains required work.
- `retained-only`: the drill remains reachable through the legacy route; v2
  does not yet teach that command family.

“Nearest v2 card” is traceability, not mastery migration. A legacy pass never
awards a v2 node. The test suite requires every generated legacy ID to occur
exactly once below and every cited v2 card to exist.

| Legacy ID | Disposition | Nearest v2 card | Evidence and remaining gap |
|---|---|---|---|
| `move-x` | adapted | `M9.04` | `x` removes the temporary squash centre before a replacement is inserted; the edit changes an animation extreme. |
| `delete-word` | adapted | `M2.DW` | `dw`, `de`, and `daw` now have distinct executable scopes; M2.DWH and M2.DEH retrieve word deletions on changed art. |
| `delete-eol` | adapted | `M6.05` | `D` removes the upper unit remainder while preserving the frame row. |
| `count-motion` | adapted | `M2.D2W` | `d2W` deletes two WORDs; M2.D2WH requires the counted operation on changed text. |
| `delete-line` | adapted | `M7.08` | `5dd` removes exactly one complete five-row dead duplicate. |
| `undo` | adapted | `M11.04` | A real `R` redraw changes the copied animation pose; `u` removes it and `<C-r>` restores the required saved extreme under a runtime method check and card-specific changed-art review. |
| `put` | adapted | `M0.02` | `3yy` plus `Gp` copies a complete three-row keyframe. |
| `replace-char` | adapted | `M0.01` | `r` changes one acting glyph without disturbing registered rays. |
| `change-word` | adapted | `M3.CW` | `cw` changes a word while preserving its neighbours; M3.CWH retrieves the same operation on changed material. |
| `change-eol` | adapted | `M4.01` | `C` redraws one bounded diagonal row while preserving the pivot contract. |
| `search` | adapted | `M1.01` | `/` locates an animation landmark before a one-cell edit. |
| `match-paren` | adapted | `M3.01` | `%` traverses the face pair before changing only the acting eye. |
| `substitute` | adapted | `M0.06` | Current-line `:s` changes the transfer frame's ray material without touching other frames. |
| `substitute-all` | adapted | `M7.05` | `:%s` harmonizes one exact material band across the complete timed strip. |
| `open-line` | adapted | `M8.O` | Uppercase `O` opens above the addressed row; M8.OH and its two review variants require the operation. |
| `append` | adapted | `M15.APP` | `a` and `A` have guided and hidden pairs (M15.APPH and M15.APPAH); reviews distinguish insertion after the cursor from row-end append. |
| `yank-put` | adapted | `M0.02` | A counted yank and put duplicates the whole frame rather than a single row. |
| `join` | adapted | `M6.J` | `J` joins supplied fragments into the target row; M6.JH and changed-art reviews require actual joining. |
| `toggle-case` | adapted | `M7.TC` | `~` and `g~` have guided and hidden pairs; M7.TCH and M7.GTCH reviews require case changes. |
| `text-object-paren` | adapted | `M3.CA` | `ci(` and `ca(` have executable inner-versus-around contrast; M3.CAH retrieves around-parenthesis replacement. |
| `paragraph-object` | adapted | `M14.05` | `yap` owns a complete blank-line-separated three-row frame plus its separator; the comparison and changed-art review require an objectwise copy. |
| `named-register` | adapted | `M3.06` | Visual-line pose rows are yanked to register `a` and put on changed art. |
| `yank-register-0` | adapted | `M3.Y0` | Yank, intervening deletion, and `"0p` retrieve the original yank; M3.Y0H reviews require register zero. |
| `marks` | adapted | `M3.MARK` | A mark survives a distant edit before the learner returns to it; M3.MARKH reviews require set-and-return travel. |
| `visual-delete` | adapted | `M3.VD` | Visual-line deletion removes the selected rows; M3.VDH reviews preserve the surrounding rows. |
| `block-insert` | adapted | `M4.BI` | Blockwise `I` insertion has a guided card, M4.BIH, and two changed-art reviews. |
| `block-append` | adapted | `M15.05` | Blockwise `<C-v>...$A` appends an occluding edge at the true end of three differently sized texture rows; the exact method and a changed-art review are runtime-required. |
| `block-erase` | adapted | `M4.BD` | Blockwise deletion removes the selected column; M4.BDH and two reviews require the operation. |
| `block-replace` | adapted | `M4.04` | `<C-v>` plus `r` replaces an actually aligned vertical midpoint column. |
| `macro` | adapted | `M7.05` | The compare path records and replays a bounded Visual material edit with `q`/`@`. |
| `symbol-table` | adapted | `M14.04` | A one-glyph palette entry is yanked characterwise into register `a` and retrieved with `<C-r>a` through Replace mode on a copied animation variant. |
| `dot-repeat` | adapted | `M7.04` | `.` repeats the same timing-accent edit one frame-height away. |
| `find-char` | adapted | `M7.06` | `f` locates the acting glyph on changed transfer art before a repeat. |
| `ex-copy` | adapted | `M5.05` | An addressed `:t` copies one complete seven-row layered frame. |
| `hold-frame` | adapted | `M7.01` | `:t` duplicates a complete five-row frame as an explicitly justified anticipation hold. |
| `tween-frame` | adapted | `M9.05` | A complete copied frame is redrawn into the falling in-between between readable extremes. |
| `break-seam` | adapted | `M5.01` | `f` plus `r` removes a background seam directly below the registered foreground pivot. |
| `playback-order` | adapted | `M6.DDP` | `ddp` swaps adjacent rows into the requested order; M6.DDPH reviews require the same operation on changed identities. |
| `range-normal` | adapted | `M7.05` | The compare path uses `:global` plus `normal!` only on exact material-band rows. |
| `mirror-run` | adapted | `M18.01` | Three exact full-row overwrites hand-author actor position, arrowhead, slash limbs, and whitespace; byte reversal and expression-generated art are explicitly rejected, and changed-art reviews require the same method. |
| `pad-frames` | adapted | `M8.PAD` | `O` followed by dot repeat adds repeated padding rows; M8.PADH reviews require both operations. |
| `macro-frames` | adapted | `M7.05` | The recorded edit includes the five-row frame stride and replays across homologous bands. |
| `ant-drop` | adapted | `M7.08` | Counted line deletion removes a complete unwanted frame while preserving the surrounding strip. |
| `centipede-hold` | adapted | `M7.01` | A complete-frame copy is explicitly classified as a timing hold rather than accidental duplication. |
| `cheer-eyes` | adapted | `M3.04` | A local eye change creates the acting feature in a duplicated full-body pose. |
| `candle-join` | adapted | `M6.J` | The meaningful join and its M6.JH changed-art reviews replace the old join-then-undo demonstration. |

Current count: 46 adapted, 0 partial, 0 retained-only. The former 16 gaps now
have executable v2 paths. The added 17 guided/hidden pairs carry two changed-art
review variants each. `test_course_completion.py` executes their effects in
clean Neovim. Command parity is not a claim that the learner has mastered them.
The record also includes explicit text-label studies; not every row is animation.
