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
| `delete-word` | partial | `M2.01` | V2 applies `daw` to remove an annotation without shifting the face, but does not yet contrast `dw`, `de`, and `daw`. |
| `delete-eol` | adapted | `M6.05` | `D` removes the upper unit remainder while preserving the frame row. |
| `count-motion` | retained-only | `M2.01` | Operator grammar is present, but the legacy `d2W` count-plus-WORD lesson has no v2 executable path. |
| `delete-line` | adapted | `M7.08` | `5dd` removes exactly one complete five-row dead duplicate. |
| `undo` | adapted | `M11.04` | A real `R` redraw changes the copied animation pose; `u` removes it and `<C-r>` restores the required saved extreme under a runtime method check and card-specific changed-art review. |
| `put` | adapted | `M0.02` | `3yy` plus `Gp` copies a complete three-row keyframe. |
| `replace-char` | adapted | `M0.01` | `r` changes one acting glyph without disturbing registered rays. |
| `change-word` | partial | `M3.04` | V2 uses `ci(` as a structural change, but has no `cw` animation exercise. |
| `change-eol` | adapted | `M4.01` | `C` redraws one bounded diagonal row while preserving the pivot contract. |
| `search` | adapted | `M1.01` | `/` locates an animation landmark before a one-cell edit. |
| `match-paren` | adapted | `M3.01` | `%` traverses the face pair before changing only the acting eye. |
| `substitute` | adapted | `M0.06` | Current-line `:s` changes the transfer frame's ray material without touching other frames. |
| `substitute-all` | adapted | `M7.05` | `:%s` harmonizes one exact material band across the complete timed strip. |
| `open-line` | retained-only | `M8.04` | V2 constructs a pose with lowercase `o`; uppercase `O` is not an executable v2 lesson. |
| `append` | retained-only | `M8.04` | The padded `I`/`A` fragments were removed; the current card opens and types complete pose rows, so append-mode coverage is still missing. |
| `yank-put` | adapted | `M0.02` | A counted yank and put duplicates the whole frame rather than a single row. |
| `join` | retained-only | `M6.04` | The no-op `J` then `u` demonstration was removed; no v2 animation task currently requires a join. |
| `toggle-case` | retained-only | `M7.05` | Material polish exists, but `~`/`g~` is absent from v2 key paths. |
| `text-object-paren` | partial | `M3.04` | `ci(` is executable; the inner-versus-around `ca(` contrast is not. |
| `paragraph-object` | adapted | `M14.05` | `yap` owns a complete blank-line-separated three-row frame plus its separator; the comparison and changed-art review require an objectwise copy. |
| `named-register` | adapted | `M3.06` | Visual-line pose rows are yanked to register `a` and put on changed art. |
| `yank-register-0` | retained-only | `M3.06` | Named registers are taught, but the yank register `"0` after deletion is not. |
| `marks` | retained-only | `M3.08` | The set-and-immediately-return detour was removed; the eye is directly addressed, so a meaningful mark-based animation task remains absent. |
| `visual-delete` | partial | `M3.06` | Linewise `V` scopes a complete pose for yank; deleting a Visual selection is not practised. |
| `block-insert` | retained-only | `M4.04` | Blockwise selection is executable, but block `I` insertion is not. |
| `block-append` | adapted | `M15.05` | Blockwise `<C-v>...$A` appends an occluding edge at the true end of three differently sized texture rows; the exact method and a changed-art review are runtime-required. |
| `block-erase` | retained-only | `M4.04` | Blockwise selection is executable, but block deletion is not. |
| `block-replace` | adapted | `M4.04` | `<C-v>` plus `r` replaces an actually aligned vertical midpoint column. |
| `macro` | adapted | `M7.05` | The compare path records and replays a bounded Visual material edit with `q`/`@`. |
| `symbol-table` | adapted | `M14.04` | A one-glyph palette entry is yanked characterwise into register `a` and retrieved with `<C-r>a` through Replace mode on a copied animation variant. |
| `dot-repeat` | adapted | `M7.04` | `.` repeats the same timing-accent edit one frame-height away. |
| `find-char` | adapted | `M7.06` | `f` locates the acting glyph on changed transfer art before a repeat. |
| `ex-copy` | adapted | `M5.05` | An addressed `:t` copies one complete seven-row layered frame. |
| `hold-frame` | adapted | `M7.01` | `:t` duplicates a complete five-row frame as an explicitly justified anticipation hold. |
| `tween-frame` | adapted | `M9.05` | A complete copied frame is redrawn into the falling in-between between readable extremes. |
| `break-seam` | adapted | `M5.01` | `f` plus `r` removes a background seam directly below the registered foreground pivot. |
| `playback-order` | partial | `M6.08` | Exact five-line ranges are reordered with `:m`; the compact `ddp` adjacent swap remains legacy-only. |
| `range-normal` | adapted | `M7.05` | The compare path uses `:global` plus `normal!` only on exact material-band rows. |
| `mirror-run` | adapted | `M18.01` | Three exact full-row overwrites hand-author actor position, arrowhead, slash limbs, and whitespace; byte reversal and expression-generated art are explicitly rejected, and changed-art reviews require the same method. |
| `pad-frames` | partial | `M8.04` | V2 opens the rows required for a complete equal-height pose, but does not teach `O` followed by dot repeat as padding. |
| `macro-frames` | adapted | `M7.05` | The recorded edit includes the five-row frame stride and replays across homologous bands. |
| `ant-drop` | adapted | `M7.08` | Counted line deletion removes a complete unwanted frame while preserving the surrounding strip. |
| `centipede-hold` | adapted | `M7.01` | A complete-frame copy is explicitly classified as a timing hold rather than accidental duplication. |
| `cheer-eyes` | adapted | `M3.04` | A local eye change creates the acting feature in a duplicated full-body pose. |
| `candle-join` | retained-only | `M6.04` | The padded join/undo demonstration was removed; the legacy join task remains available only through the legacy route. |

Current count: 30 adapted, 6 partial, 10 retained-only. Therefore this document
closes the missing-disposition process finding, but it does **not** establish
complete legacy command parity. The 16 partial/retained-only rows remain visible
curriculum work and must not be described as ported.
