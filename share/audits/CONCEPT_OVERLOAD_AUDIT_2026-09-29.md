# Concept-overload audit · 2026-09-29

Scope: read-only audit of all 221 cards in `share/curriculum-v2.json`
(revision on disk at 2026-09-29, after the VD-34 M11.CC/M11.TR fix), in module
order (`modules[].card_ids`: M0, M11, M1, M19, M2, M12, M14, M10, M5, M15, M16,
M3, M4, M17, M13, M7, M6, M18, M8, M9). 180 cards have `expected` keys; 41 are
concept/question cards.

Trigger: the operator's M11.WS complaint (VD-34): one guided card taught four
new ideas at once, carried a generic hint, and led straight into key-hidden
retrieval. This audit looks for the same failure shape across the course,
plus the related complaints in VD-12..VD-33 (tested before taught, jargon,
template wording, typing walls, too many literal characters).

Method (reproducible; nothing in the repo was edited except this file):

- `v2_runtime._new_concepts(card, cur)` on every card (families no earlier
  guided card displayed; `j/k/h/l` excluded as in the runtime).
- `v2_keys.explain(card['expected'])` for chunk counts and for literal typed
  text (text inside `i/a/o/O/A/I/C/R/gR/c…<Esc>` and `:s` replacements).
- `v2_keys.explain_lines` scanned for lines that echo the command
  (`run the command-line command …`, `press …`, `g_ = g_`, `:g` raw echo,
  unglossed `\=`/escapes).
- Hint text counted verbatim and by template prefix.
- For each family: first guided card that displays it, and whether the next
  card using it is hidden-recipe.
- For each family: presence in `v2_keys.FAMILY_TEACH` and `v2_keys.EXAMPLES`.
- Every finding below was confirmed by reading the card (title, prompt,
  recipe, hint, key_vocabulary, explain_lines). Script output is in the
  appendices.

Severity scale:
- **S1** wrong or unanswerable: the tutor teaches the wrong meaning, the shown
  recipe fails, or the card needs input the course never taught.
- **S2** overload: several new ideas in one card, or retrieval with no
  single-idea practice (the M11.WS shape).
- **S3** wording: generic/template hints or explanations that restate the
  command.
- **S4** coverage: missing FAMILY_TEACH / EXAMPLES entries.

## Counts

| Category | Count |
|---|---|
| 1a. Cards with `_new_concepts` >= 3 | 7 (M0.01, M0.YP, M11.WS, M11.UT, M11.VE, M4.DIFF, M13.BE) |
| 1b. Guided cards with >= 4 recipe chunks | 60 of 83 guided edit cards; 13 with >= 9 chunks |
| 1c. Cards with > 12 literal typed characters | 16 (5 guided, 11 hidden); 6 of them need non-keyboard glyphs |
| 2. Hints | only 6 of 180 hints are card-specific; 54 cards share 3 generic strings (26 / 17 / 11); 120 use the "Vim toolbox: … Scope: Treat each N-row block … Check against this failure: …" template; 17 template hints name a tool the card never uses |
| 2'. Guided cards that introduce >= 1 new idea and carry a generic hint | 29 |
| 3. Explanation lines that echo or mis-state the command | 24 lines on 14 cards, plus 3 parser misreads that teach a wrong meaning (digraph after `r`, `zy`, `<C-w>p`) and 1 (`R<C-r>a`) that misses the idea |
| 4. Guided -> hidden jumps (family first shown, next use hidden) | 57 family jumps; 34 come from a guided card that itself introduced >= 2 ideas |
| 4'. Hidden cards needing a family never shown on any guided card | 10 (6 on the primary `expected`, 4 on accepted alternatives), plus syntax-level gaps on 6 cards that the family check cannot see |
| 5. Families with no FAMILY_TEACH | 9 (2 are parser artefacts: `!`, `z`) |
| 5'. Families with FAMILY_TEACH but no EXAMPLES | 20 |

## Ranked findings

### F1 · S1+S2 · M4.DIFF / M4.DIFFH (M4): eight new ideas, one mis-explained key, then a hidden copy

Evidence: `expected = :vnew<CR>:silent 0read #<CR>ggdd:diffthis<CR>:set scrollbind<CR><C-w>p:diffthis<CR>:set scrollbind<CR>2G0f'r.:diffoff!<CR><C-w>p:bwipeout!<CR>`;
18 explain chunks; `_new_concepts` = `:vnew, :silent, dd, :diffthis, :set scrollbind, <C-w>, :diffoff!, :bwipeout!` (8).
Hint: generic "Follow the visible grammar once, then inspect the registered result."
explain_lines:
```
:vnew<CR>           = run the command-line command 'vnew' (Enter runs it)
:silent 0read #<CR> = run the command-line command 'silent 0read #' (Enter runs it)
<C-w>               = press <C-w>
p                   = put (paste) after the cursor / below this line     <- WRONG: <C-w>p = go to previous window
:diffthis<CR>       = on the current line, join this window to the diff  <- "on the current line" is false
:diffoff!<CR>       = run the command-line command 'diffoff!'
:bwipeout!<CR>      = run the command-line command 'bwipeout!'
```
`#` (alternate file) and `0read` (read above line 1) are never glossed.
M4.DIFFH, 6 cards later, retrieves the whole 18-chunk sequence with the
recipe hidden and the generic hint "Name the acting cells first…".

Why hard: this is M11.WS doubled. Eight window/buffer ideas arrive in one
card; one key pair is taught with the wrong meaning (a learner who reads
"p = paste" and presses it in the wrong window corrupts the art).

Fix:
- Split into four guided micro-cards before any hidden copy:
  1. **M4.WIN** `:vsplit<CR><C-w>p<C-w>p:q<CR>` — open a second window, move
     between windows, close one. Hint: "Ctrl-w p jumps to the window you were
     in last; :q closes only the window the cursor is in."
  2. **M4.REF** `:vnew<CR>:read #<CR>` — a scratch window holding the saved
     frame (`#` = the file you were editing before). Hint names `#`.
  3. **M4.DT** `:diffthis` in each window only, observe highlighted cells,
     `:diffoff!`.
  4. **M4.DIFF** (existing, now pure reinforcement) with `:set scrollbind`
     explained by OPTION_NOTES (already present).
  Then M4.DIFFH.
- `v2_keys.explain`: treat `<C-w>{x}` as one chunk:
  `{"<C-w>p": "jump to the previous window", "<C-w>w": "jump to the next window", "<C-w>l": "jump to the window on the right"}`, family `<C-w>{x}`.
- `EX_NAMES` additions: `vnew` "open an empty window on the left",
  `vsplit`, `silent` "run the following command without messages",
  `bwipeout` "remove the buffer completely", `diffoff` "leave diff mode (! = in every window)".
- `_explain_ex`: do not prefix "on the current line" for commands that take
  no range (`diffthis`, `diffoff`, `earlier`, `later`, `vnew`, `vsplit`, `set`).
- FAMILY_TEACH/EXAMPLES: `:vnew`, `:silent`, `:bwipeout!`, `:diffoff!`,
  `<C-w>{x}`, `:set scrollbind` (teach line missing today),
  `dd` (example missing: "on 3 rows, 2G dd removes row 2; the rows below move up").

### F2 · S1 · M12.AA and M3.DI: digraph after `r` is mis-parsed, so the NEW CONCEPT ALERT teaches wrong commands

Evidence (M3.DI, `expected = 2G0fOr<C-k>.M`):
```
r<C-k> = replace the character under the cursor with '<C-k>'
.      = repeat the last change        <- wrong
M      = to the middle of the window   <- wrong
NEW: ['.', 'M']
```
M12.AA (`…j3|r<C-k>!I`): `! = press !`, `I = insert at the start of the line '', then Esc`; NEW: `['!', 'I{text}<Esc>']`.
`FAMILY_TEACH['<C-k>{a}{b}']` exists but is unreachable: the `<C-k>` branch
only fires when `<C-k>` starts a command.

Knock-on effect: because M3.DI "shows" `.`, the runtime no longer marks dot
repeat as new on M17.01, the first guided card that really uses it.

Why hard: the one card whose whole purpose is the digraph tells the learner
that `.` repeats and `M` moves the cursor. Neither is true here.

Fix:
- In the `r{char}` branch (and inside `_typed_until_esc` output for
  `i/a/o/R/C/gR`), when the next token is `<C-k>`, consume three tokens and
  emit `r<C-k>.M = replace the character with the digraph .M (·)`, family
  `r<C-k>{a}{b}`.
- FAMILY_TEACH `r<C-k>{a}{b}`: "r then Ctrl-k {a}{b}: replace one cell with a
  digraph glyph (Ctrl-k .M = ·, Ctrl-k !I = ¡)". EXAMPLES: "on `(o)` at o:
  r Ctrl-k .M makes `(·)`".
- After the fix, re-run `_new_concepts` on M17.01: it must list `.` as new.

### F3 · S1 · Non-keyboard glyph typing walls with no entry method taught (M10, M1, M19, M18)

Evidence (literal typed characters, from explain):

| Card | Stage | Literal chars | Glyphs not on a US keyboard |
|---|---|---|---|
| M10.02 | guided | 13 | `／ ￣ ＼ （ ） ＿` and U+3000 ideographic spaces (look like ASCII `/ ‾ \ ( ) _` and space) |
| M10.04 | hidden | 13 | `／ ￣ ＼ ﾆ 二 ニ ＿` |
| M1.04 | hidden | 53 over 5 `o` rows | `´ ‾` |
| M19.04 | hidden | 72 over 6 `gR` rows | `´ ‾` and a backtick |
| M19.06 | hidden | 96 over 6 `gR` rows | `´ ‾` |
| M18.06 | hidden | 72 over 6 `C` rows | `´ ‾` |
| M18.01 / M18.04 | guided / hidden | 33 / 33 | ASCII only, but 3 full 11-cell rows each |
| M8.02 / M8.04 / M8.08 | guided / hidden / hidden | 18 / 18 / 14 | ASCII |
| M9.02 / M9.05, M5.04 | guided / hidden, hidden | 14 / 14, 13 | ASCII |
| M18.EXPR / M18.EXPRH | guided / hidden | 17 | Vimscript `\=getline(1)[-1:]` (see F11) |

The only digraph lesson is M3.DI, which comes after M10, M1 and M19 in module
order. M10.02's recipe does not even show the text: it reads
`4G/5G/6G C` "redraw all three copied rows". M10.04 key_vocabulary lists only
`o/O`. Hints on M1.04, M19.04, M19.06, M18.06 are the template
"search can jump between homologous animation anchors", which the recipe
never uses (see F13).

Why hard: this is VD-25's M0.O typing wall plus characters the learner
cannot type. A fullwidth `／` and an ASCII `/` look almost the same, so an
exact-target check fails with no visible difference.

Fix:
- Move a digraph micro-card (M3.DI's idea) before M1: **M0.DG** `r<C-k>''`
  (´) and **M0.DG2** `r<C-k>'-` (‾). Check these codes with `:digraphs`
  before authoring. Fullwidth forms have no RFC1345 digraph, so for M10 use a
  palette row + register (the M14.01 `"ayl … R<C-r>a` method) or yank/put of
  a supplied row. Do not ask for fullwidth glyphs to be typed.
- Cap literal typing per guided card at one row (<= 12 cells). For
  M19.04/M19.06/M18.06 (hidden, 6 rows): supply 5 rows and ask for 1, or
  switch to `r`/`gR` on the 1-3 cells that actually mirror.
- explain_lines: for non-ASCII glyphs inside typed text, add
  `(´ = Ctrl-k '')`-style notes, or say "copy from the palette row".

### F4 · S2 · M11.UT -> M11.UTH (M11): three new undo-tree commands in a 10-chunk recipe (VD-34 left this open)

Evidence: `expected = 2G0for!urOg-g+:earlier 1<CR>g+`; NEW = `g-, g+, :earlier`
(plus the branch idea behind `u` + new edit). Hint: generic "Follow the
visible grammar once…". explain_lines: `:earlier 1<CR> = on the current line,
visit an older undo-tree state 1` ("on the current line" is false; "state 1"
does not say "one step"). The operator failed this card at 12:43
(FAILURE_LOG VD-34 "Still open"). The next use is M11.UTH, hidden, 4 cards
later, with only hidden cards in between (M11.04, M11.05, M11.WSH).

Fix:
- **M11.BR** (branch): `2G0for!urO` only. Hint: "u went back before `!`;
  typing rO now starts a second branch, and the `!` take is still in history."
- **M11.GM** `g-g+` only, on the same buffer: "g- steps back in time through
  every state, including the abandoned `!`; g+ steps forward again."
- **M11.ER** `:earlier 1<CR>g+` only: "`:earlier 1` = one step back in time,
  same as g-."
- Then M11.UT as reinforcement, then M11.UTH.
- `_explain_ex`: `earlier`/`later` -> "go N step(s) back / forward in undo
  history"; no range prefix.
- EXAMPLES `:earlier` exists; add `u` + branch example: "on `a`: ra→b, u, rc:
  g- shows b, g+ shows c".

### F5 · S2 · M11.WS residual: `:set list` and `:set cursorcolumn` still have no single-idea card before M11.WSH

Evidence: VD-34 added M11.CC (colorcolumn) and M11.TR (trailing-space
pattern). `:set list` and `:set cursorcolumn` appear only on M11.WS (4 new
ideas) and then on M11.WSH (hidden, 6 cards later). M11.WS keeps the generic
hint "Follow the visible grammar once, then inspect the registered result."
in the data; the runtime banner replaces it only on compact guided screens.

Fix:
- **M11.LS**: `:set list<CR>` then `$x` on the one row whose `$` mark shows a
  stray trailing space. Hint: "`:set list` changes only the display: a
  trailing space shows as a mark before `$`."
- **M11.CUC**: `:set cursorcolumn<CR>` then `j` down a column and `r` the one
  misaligned cell. Hint: "the highlighted column shows which glyph is one
  cell off."
- Replace the M11.WS data hint with a card-specific one: "Four display
  helpers first, then one cleanup: list shows spaces, cursorcolumn and
  colorcolumn show columns, `:%s/\s\+$//e` deletes spaces at row ends."

### F6 · S2 · M11.VE -> M11.08 (M11): virtualedit + column motion + first `i` insert in one card; recipe hides the keys

Evidence: `expected = :set virtualedit=all<CR>gg12|i|<Esc>2G12|i|<Esc>3G12|i|<Esc>` (10 chunks);
NEW = `:set virtualedit, [count]|, i{text}<Esc>`. The shown recipe is
`[':set virtualedit=all<CR>', 'N|', 'i|<Esc>']`: `N|` is a placeholder, not
keys. `i` (Insert mode) is introduced here as a side idea, in module 2 of
the course. Hint: generic "Work out the scope first…". M11.08 (hidden) is the
next card.

Fix:
- **M11.COL** `12|r|` on full-width rows: column motion alone.
- **M11.INS** `i|<Esc>` at a marked cell: Insert mode alone (better placed in
  M0 next to `o`).
- **M11.VE** reinforcement: `:set virtualedit=all<CR>` + `12|` on a short row,
  with the literal keys shown for each row (`gg12|i|<Esc>`…), not `N|`.
- EXAMPLES `i{text}<Esc>`: "on `ac` at c: ib<Esc> makes `abc` (the row gets
  longer)". EXAMPLES `[count]|` exists.

### F7 · S2 · M0.01 (first edit card): three new ideas after a primer that taught only `j`; recipe omits `0`

Evidence: M0.P0 teaches `[count]j` only. M0.01 `expected = j0f*ro`,
NEW = `0, f{char}, r{char}`. Shown recipe = `j`, `f*`, `ro`; `0` is in
`expected` but not in the recipe. Hint: template "Vim toolbox: a visible
character landmark is safer… Scope: Treat each 3-row block as one frame; do
not count only the nonblank glyph rows. Check against this failure: the
energy cell changes while the Fireworks accents drift, or a duplicate has no
timing purpose." The next use of `0`, `f`, `r` is M0.06, hidden, with the
spaced-review failures recorded in VD-34 (M0.01, M0.06 remediation).

Fix:
- **M0.F** `j0f*`: landmark motion only (the cursor lands; nothing changes).
  Hint: "f* jumps to the next `*` on this row; 0 first puts you at column 1."
- **M0.R** `ro` on the cell under the cursor: replace only.
- M0.01 then combines them. Show `0` in the recipe.
- EXAMPLES `0`: "on `  ab` with the cursor on b: 0 goes to column 1, ^ to a".

### F8 · S2 · M0.YP (M0): four new ideas (gg, 3yy, G, p)

Evidence: `expected = gg3yyGp`; NEW = `gg, [count]yy, [count]G, p`. The
hint is card-specific and good ("Vim's copy sentence is [count]yy…"), but
`gg`/`G` are file motions the primer never introduced.

Fix: extend M0.P0 (motion primer) with `gg` / `G` / `{N}G` next to `j`, so
M0.YP carries only yy + p (one sentence, two keys).

### F9 · S2 · M13.BE -> M13.04 / M13.06 / M13.08 (M13): three WORD motions at once; recipe omits the edits

Evidence: `expected = gg0WEr!2Wr?Br+`; NEW = `E, [count]W, B`. Shown recipe
`W/E`, `2W`, `B` leaves out `r!`, `r?`, `r+`, which the learner must also
type. Hint: generic "Work out the scope first…". Next uses are hidden:
M13.04 (`2B`, a counted B never shown), M13.06, M13.08.

Fix:
- **M13.E** `WEr!` (end of WORD only) and **M13.B** `Br+` (back one WORD only)
  as guided micro-cards; keep M13.BE as reinforcement with all 9 chunks shown.
- EXAMPLES exist for W/B/E; add counted form "2W on `a b c` at a lands on c".

### F10 · S1 · Hidden cards that need a command no guided card showed (tested before taught)

Families never displayed by any earlier guided card:

| Hidden card | Keys | Unseen family |
|---|---|---|
| M1.05 | `4G0f:r!6j0f:.` (primary) | `.` dot repeat. The first real guided dot is M17.01, 12 modules later; M3.DI "shows" it only through the F2 misparse |
| M15.08, M17.08 | `3@q` | `[count]@{reg}` (M15.MAC shows only `0@q` twice) |
| M16.04, M16.08 | `2<C-a>` | `[count]<C-a>` |
| M13.04 | `2B` | `[count]B` |
| M16.05 (alt) | `6GV4jdggP` | `Visual d` |
| M7.05 (alt) | `2@q` | `[count]@{reg}` |
| M9.05 (alt) | `3o<Esc>` | `[count]o` |
| M15.05 (alt) | `:4,6s/$/|/` | `$` as an append-at-row-end pattern |

Syntax-level gaps that the family check cannot detect (same family name,
new syntax):
- `[.o]` character class: M2.05 (hidden) `:%s/[.o]/O/g`.
- Alternate delimiter `@` and escaped backslash `\\`: M11.05 `:s@/@\\@g`,
  M8.05 `:1,5s@o/@o\\@`, M7.05 `:%s@/---\\@/===\\@g` (M7.05's prompt names
  "recorded visual macro or global normal" but its primary `expected` is
  this substitute).
- Escaped search `\*`: M17.06 and M17.08 `/\*<CR>`. `explain` does not gloss
  `/` patterns at all (`search forward for '\*'`).

Fix:
- `_new_concepts`: treat `[count]X` as new when neither `[count]X` nor a
  guided `{N}X` example was shown. Add a pattern-atom novelty check: collect
  `pattern_parts` atoms (`[...]`, `\\`, `\*`, delimiter) from guided cards
  and flag unseen atoms on any card.
- Author one guided card for dot before M1 (e.g. **M1.DOT** `f:r!` then
  `j0f:.`), one for `{N}@q`, one for `{N}<C-a>`, and one for escaped
  literals plus an alternate delimiter (**M0.ESC** `:s#/#\\#g` with the hint
  "when the pattern contains /, use # as the separator; \\ means one literal
  backslash").
- Gloss search patterns with `_pattern_gloss` in the `/`/`?` branch.

### F11 · S1/S3 · M18.EXPR / M18.EXPRH (M18): Vimscript expression in a replacement, explained by echo

Evidence: `expected = :3s/0/\=getline(1)[-1:]/<CR>`; explain:
`on line 3, replace '0' with '\=getline(1)[-1:]'; first match on each line only`.
NEW = `:[range]s/old/new/`, a no-g variant, not the real new ideas. The real
new ideas are `\=` (the replacement is an expression), `getline(1)` (text of
line 1), and `[-1:]` (last character), all Vimscript. Hint: generic.

Fix: in `_explain_ex`, when `new` starts with `\=`, output "replace with the
value of the Vim expression `getline(1)[-1:]`: getline(1) = the text of line
1; [-1:] = its last character". Add a FAMILY `:[range]s/old/\=expr/` with
FAMILY_TEACH + EXAMPLES ("`:s/X/\=line('.')/` writes the line number"). Give
it a card-specific hint. If the expression is not a course goal, replace the
card: the artwork gains nothing from it.

### F12 · S3 · `:g/pattern/normal! …` explained by echo (M15.GLOBAL, M7.GLOBAL, M17.GNH)

Evidence: `:g/a/normal! far+<CR> = on every matching line run: '/a/normal! far+'`.
The pattern, `normal!`, and the `!` (ignore mappings) are not separated.
No EXAMPLES entry. M15.GLOBAL (guided, generic hint) -> the next use is
M17.GNH (hidden, 46 cards later).

Fix: in `_explain_ex` for `g`/`v`, split `/pat/cmd`: "on every line
containing `a`, run: normal! far+ (= type the Normal keys `far+` on that
line; ! = ignore your key mappings)". EXAMPLES `:g/pattern/command`: "on
`ao`,`bo`,`ax`: `:g/a/normal! rX` changes the first cell of rows 1 and 3".
Add a guided `:g` reinforcement in M17 before M17.GNH.

### F13 · S3 · Hints: three generic strings on 54 cards, one template on 120, and 17 template hints that name the wrong tool

Verbatim counts:
- 26 × "Work out the scope first; then follow the visible grammar once." —
  on guided cards that introduce: M0.SL, M11.UR, M11.VE, M1.DD, M12.AA,
  M12.JH, M12.FIND, M12.GV, M14.PARA, M15.BA, M15.MAC, M15.GLOBAL, M16.MOVE,
  M3.CI, M3.REG, M3.DI, M13.BE, M7.VIS, M6.D, M18.EXPR (and 6 reuse cards).
- 17 × "Name the acting cells first. The exact key sequence remains hidden
  until evaluation." (every `*H` retrieval card).
- 11 × "Follow the visible grammar once, then inspect the registered
  result." — M11.WS, M11.UT, M14.DAP, M15.ZP, M3.GA, M4.BI, M4.BC, M4.DIFF,
  M4.GV, M13.W, M13.GU.
- 120 × "Vim toolbox: <tool list>. Scope: Treat each N-row block as one
  frame; do not count only the nonblank glyph rows. Check against this
  failure: <module defect>." The Scope sentence repeats verbatim on 54/30/18/
  12/6 cards (3/5/4/6/7-row variants). The first clause repeats on up to 18
  cards ("an addressed Ex copy can duplicate…").
- Only 6 card-specific hints exist: M0.YP, M0.O, M0.SR, M0.T, M11.CC, M11.TR.

Template hints that name a tool the card does not use (misleading):
M1.04, M19.04, M19.06, M18.06, M9.06, M4.01, M8.02, M8.04, M8.08 ("search can
jump…"; none of them search); M18.01, M18.04 ("search… dot repeat");
M10.05, M12.05, M15.06, M4.08 ("dot repeat"; no `.`); M11.04 ("named
register"; none); M3.06 ("paragraph text object"; uses `V5j`).

Fix: generate the hint from the card's own new families and pattern:
`"<first new family teach line>. Watch: <one concrete cell/row from TARGET>."`
For example M15.ZP: "zy copies each selected row without its trailing
spaces; zp pastes without padding. Watch row 2: it must stay 7 cells, not
9." For hidden cards: "You need: <families by name, no keys>. Start on row
<N>." Drop the Scope sentence from every hint (it belongs once per module),
and make the generator refuse a toolbox clause whose family is absent from
`expected` and every alternative.

### F14 · S1/S3 · Other parser misreads and echo lines

- `zy` (M15.ZP, M15.ZPH): `z = press z`, `y = yank (copy) the selection`.
  NEW lists `z`. Fix: parse `zy` as "yank the block without trailing
  spaces", family `zy`; FAMILY_TEACH/EXAMPLES next to `zp`.
- `R<C-r>a<Esc>` (M14.01, M14.04, M14.06, M14.08): "type over the existing
  characters with '<C-r>a'". The idea "Ctrl-r {reg} in Insert/Replace mode
  puts register {reg}" is never flagged new. `<C-r>` means redo in Normal
  mode (M11.UR) and this in Replace mode; the course never contrasts the
  two. Fix: in typed text, render `<C-r>{x}` as "Ctrl-r a = insert register
  a"; family `<C-r>{reg} (Insert)` with FAMILY_TEACH "in Insert/Replace mode,
  Ctrl-r a types the contents of register a (in Normal mode Ctrl-r is redo)".
- `g_` (M13.GU, M13.GH): `g_ = g_`. Fix: add to the `g` meaning table: "to
  the last non-blank glyph (ignores trailing spaces)"; FAMILY_TEACH + EXAMPLES
  ("on `ab   ` : g_ lands on b, $ lands on the last space").
- `:read %` (M16.02): `on the current line, read a file below %`. Fix: "read
  this file's saved copy in below the cursor (% = the current file name)".
- `%` has three meanings in the course and none are contrasted: every line
  (`:%s`, M11.WS/TR), the current file (`:read %`, M16.02), matching bracket
  (motion, M3.01). `#` (alternate file) appears only in M4.DIFF. Add a line to
  each FAMILY_TEACH that uses `%`: "% here means …, not …".

### F15 · S1 · Wrong content in shown recipes and hints

- **M0.O** hint: "type the two leading spaces shown in TARGET yourself".
  TARGET row 6 is `    /!\` (four spaces), and `expected` is
  `Go    /!\<Esc>`. Fix: "type the four leading spaces", or better, count them
  in the task ("4 spaces, then /!\").
- **M16.01** recipe: `0f1<C-a>` "increment the numeric label". The label row
  is `F00 KEY`; it contains no `1`, so `f1` fails. `expected` is
  `Gk0f0<C-a>`. Fix: recipe `0f0<C-a>`. key_vocabulary has no `<C-a>` entry;
  add "Ctrl-a adds 1 to the number at or after the cursor, keeping zero
  padding".
- **M6.01** recipe row `['^', 'the cursor starts on the primary apex']`: `^`
  is a note, not a key, and `^` is also a Vim motion. `expected` is `r^`.
  Remove the row or reword it as a note.
- Guided recipes that show placeholders instead of keys: M11.VE (`N|`),
  M10.02 (`4G/5G/6G C`), M8.02 (`6G/7G/9G/10GC`), M9.02 (`4GC`, `5GC`),
  M18.01 (`0C...`), M13.BE (edits omitted), M0.01 (`0` omitted), M15.MAC and
  M7.MAC (`gg0`/`gg` omitted), M7.DOT (second `j.` omitted). On a guided
  card the recipe is the lesson; show every key.

### F16 · S2 · Two-idea guided cards that go straight to hidden retrieval

Each introduces two ideas that can be separated. The next use of each is a
hidden card:
- M2.01 `/note<CR>daw`: search and a text-object delete (unrelated). Split
  into **M2.S** `/note<CR>` and **M2.DAW** `daw`.
- M14.PARA `ggyapgg}jP`: `}` and `P` new, then hidden M14.05 / M14.PH.
  Add **M14.BR** `}` alone (land on the blank separator line).
- M12.FIND `2G0f:;r!,r!`: `;` and `,` together, then hidden M12.04. Pair
  acceptable; add EXAMPLES for `,` use (exists) and a `;`-only warm-up.
- M15.01 `j:set shiftwidth=1<CR>>>` -> hidden M15.04 / M15.06; add a `>>`
  example (missing today).
- M15.ZP (after the F14 parser fix, NEW = `zy`, `zp`) -> hidden M15.ZPH.
- M3.DI -> hidden M3.08 (after F2, one real idea: the digraph).
- M11.UR `u`, `<C-r>` -> hidden M11.04 (paired; fine once `<C-r>` has an
  example: "after u: Ctrl-r puts the change back").

Single-idea guided -> hidden jumps (acceptable, listed in Appendix C) should
still get at least one guided reuse when the gap is long: `o` (M0.O -> M1.04,
31 cards), `:g` (M15.GLOBAL -> M17.GNH, 46 cards).

### F17 · S4 · Missing FAMILY_TEACH / EXAMPLES

No FAMILY_TEACH (the NEW CONCEPT ALERT falls back to the raw parser meaning):
`:vnew`, `:silent`, `:set scrollbind`, `<C-w>` (as `<C-w>p`), `:diffoff!`,
`:bwipeout!`, `g_`; parser artefacts `!`, `z` (fixed by F2/F14).
(`M` has a teach line but appears only through the F2 misparse.)

FAMILY_TEACH present but no EXAMPLES:
`0`, `$`, `<C-r>`, `i{text}<Esc>`, `[count]dd`, `dd`, `da{object}`,
`T{char}`, `"{reg}y{motion}`, `C{text}<Esc>`, `Visual y`, `Visual d`,
`Visual c{text}<Esc>`, `>>`, `:g/pattern/command`, `:read`, `%`, `w`
(plus `M` and `I{text}<Esc>`, which appear only through the F2 misparse).

Proposed EXAMPLES (neutral text, one line each):
- `0`: "on `  ab` at b: 0 goes to column 1; ^ goes to a"
- `$`: "on `ab--` at a: $ lands on the last -"
- `<C-r>`: "after u undid `rO`: Ctrl-r puts the O back"
- `i{text}<Esc>`: "on `ac` at c: ib<Esc> makes `abc` (row grows by one)"
- `dd` / `[count]dd`: "on rows a,b,c at a: 2dd leaves only c"
- `da{object}`: "on `x note y` at n: daw leaves `x y`"
- `T{char}`: "on `a:bc` at c: T: lands on b, just after the :"
- `"{reg}y{motion}`: "on `*` : \"ayl stores * in register a"
- `C{text}<Esc>`: "on `ab--` at the first -: C==<Esc> makes `ab==`"
- `Visual y` / `Visual d`: "V j y copies 2 rows; V j d deletes them"
- `Visual c{text}<Esc>`: "Ctrl-v 2j c|<Esc> puts | in that column on 3 rows"
- `>>`: "with :set shiftwidth=1, >> on `ab` makes ` ab`"
- `:g/pattern/command`: see F12
- `:read`: "`:read %` appends this file's saved copy below the cursor"
- `%`: "on `(a)` at (: % jumps to )"
- `w`: "on `ab.cd` at a: w lands on `.`, w again on c"

## Suggested order of work

1. Parser fixes (F2 digraph, F14 `zy`/`R<C-r>a`/`g_`/`<C-w>p`/range prefix):
   they are small and they stop the tutor teaching wrong meanings.
2. Content defects (F15 M0.O hint, M16.01 recipe).
3. Split M4.DIFF, M11.UT, M11.VE, M0.01, M13.BE; add the M11.LS/M11.CUC
   singles (F1, F4-F7, F9).
4. Glyph entry (F3) before any more M1/M10/M19 hidden cards are retried.
5. `_new_concepts` count/atom novelty (F10) and the hint generator (F13).
6. EXAMPLES/TEACH entries (F17).

Not covered: `questions` (401 items) were not audited for commands used
before they are taught. That needs a separate pass.

## Appendix A · Category 1 candidates (script output, confirmed rows cited above)

Guided/hidden cards with >= 4 explain chunks or > 12 literal characters:

```
M0.01 guided 4 | M0.YP guided 4 | M0.02 guided 5 | M0.04 hidden 5 | M0.06 hidden 5 | M0.08 hidden 4
M11.02 guided 4 | M11.UR guided 6 | M11.WS guided 4 | M11.CC guided 4 | M11.UT guided 10
M11.04 hidden 6 | M11.WSH hidden 4 | M11.UTH hidden 10 | M11.VE guided 10 (lit 3) | M11.08 hidden 7
M1.01 guided 4 | M1.02 guided 4 | M1.04 hidden 8 (lit 53) | M1.05 hidden 8 | M1.06 hidden 4 | M1.08 hidden 5
M19.01 guided 4 | M19.02 guided 4 | M19.04 hidden 18 (lit 72) | M19.05 hidden 4 | M19.06 hidden 17 (lit 96) | M19.08 hidden 5
M2.02 guided 4 | M2.08 hidden 4
M12.AA guided 14 | M12.JH guided 5 | M12.01 guided 4 | M12.02 guided 9 | M12.FIND guided 7 | M12.04 hidden 11
M12.05 hidden 7 | M12.GV guided 7 | M12.JHH hidden 7 | M12.06 hidden 9 | M12.08 hidden 10
M14.01 guided 6 | M14.02 guided 4 | M14.04 hidden 7 | M14.PARA guided 6 | M14.05 hidden 6 | M14.PH hidden 6
M14.06 hidden 6 | M14.08 hidden 11
M10.02 guided 13 (lit 13, fullwidth) | M10.04 hidden 4 (lit 13, fullwidth)
M5.01 guided 4 | M5.02 guided 6 | M5.C guided 4 | M5.04 hidden 6 (lit 13) | M5.05 hidden 7 (lit 10) | M5.S6C hidden 5 | M5.08 hidden 4
M15.02 guided 4 | M15.ZP guided 10 | M15.04 hidden 4 | M15.BA guided 6 | M15.05 hidden 6 | M15.ZPH hidden 10
M15.BAH hidden 6 | M15.MAC guided 7 | M15.08 hidden 5
M16.01 guided 5 | M16.02 guided 6 | M16.04 hidden 5 | M16.06 hidden 4 | M16.08 hidden 5
M3.01 guided 6 | M3.02 guided 4 | M3.CI guided 4 | M3.GA guided 5 | M3.REG guided 10 | M3.GAH hidden 5 | M3.06 hidden 10
M3.DI guided 6 | M3.08 hidden 5
M4.01 guided 7 | M4.02 guided 4 | M4.VB guided 6 | M4.BI guided 5 | M4.BC guided 5 | M4.DIFF guided 18 | M4.GV guided 7
M4.04 hidden 10 | M4.05 hidden 7 | M4.BIH hidden 5 | M4.BCH hidden 5 | M4.DIFFH hidden 18 | M4.GVH hidden 7 | M4.06 hidden 4
M17.01 guided 6 | M17.02 guided 4 | M17.04 hidden 8 | M17.05 hidden 8 | M17.06 hidden 4
M13.02 guided 9 | M13.BE guided 9 | M13.W guided 5 | M13.04 hidden 13 | M13.WH hidden 6 | M13.06 hidden 6 | M13.08 hidden 6
M7.DOT guided 8 | M7.MAC guided 11 | M7.VIS guided 6 | M7.04 hidden 8 | M7.06 hidden 6
M6.D guided 4 | M6.05 hidden 4
M18.01 guided 8 (lit 33) | M18.02 guided 4 | M18.04 hidden 9 (lit 33) | M18.EXPR guided 1 (lit 17) | M18.05 hidden 6
M18.EXPRH hidden 1 (lit 17) | M18.06 hidden 17 (lit 72)
M8.01 guided 4 | M8.02 guided 16 (lit 18) | M8.04 hidden 6 (lit 18) | M8.06 hidden 4 | M8.08 hidden 13 (lit 14)
M9.02 guided 10 (lit 14) | M9.05 hidden 7 (lit 14) | M9.08 hidden 4
```

Chunk counts include single motions (`gg`, `0`, `j`), so >= 4 chunks alone
is weak evidence. The findings above rank by new ideas and literal typing.

## Appendix B · explain_lines that echo or mis-state

```
M12.AA  '!'            => press !                                   (F2 misparse)
M3.DI   '.' / 'M'      => repeat the last change / middle of window (F2 misparse)
M15.ZP, M15.ZPH 'z'    => press z                                   (F14)
M15.GLOBAL, M7.GLOBAL, M17.GNH ':g/…/normal! …' => on every matching line run: '/…/normal! …'
M4.DIFF, M4.DIFFH ':vnew' ':silent 0read #' ':diffoff!' ':bwipeout!' => run the command-line command '…'
M4.DIFF, M4.DIFFH '<C-w>' 'p' => press <C-w> / put (paste)          (wrong: previous window)
M4.DIFF ':diffthis' / M11.UT ':earlier 1' / M16.02 ':read %' => "on the current line, …"
M17.06, M17.08 '/\*'   => search forward for '\*'                   (escape not glossed)
M13.GU, M13.GH 'g_'    => g_
M18.EXPR, M18.EXPRH    => replace '0' with '\=getline(1)[-1:]'
M14.01/.04/.06/.08 'R<C-r>a<Esc>' => type over … with '<C-r>a'
```

## Appendix C · Guided -> hidden jumps (family first shown on a guided card; next use hidden)

`MULTI` = the introducing guided card itself had >= 2 new ideas.

```
MULTI  0 / f{char} / r{char}        M0.01 (3)   -> M0.06
single o{text}<Esc>                 M0.O        -> M1.04 (31 cards later)
single :[range]t{dest}              M0.T        -> M0.05
single :s/old/new/g                 M0.SL       -> M0.06
single R{text}<Esc>                 M11.01      -> M11.04
MULTI  <C-r>                        M11.UR (2)  -> M11.04
MULTI  :set list / :set cursorcolumn M11.WS (4) -> M11.WSH
MULTI  g- / g+ / :earlier           M11.UT (3)  -> M11.UTH
MULTI  :set virtualedit / [count]| / i{text}<Esc>  M11.VE (3) -> M11.08
single [count]dd                    M1.DD       -> M1.04
single gR{text}<Esc>                M19.01      -> M19.04
single t{char} / T{char}            M12.01 / M12.02 -> M12.06
MULTI  ; / ,                        M12.FIND (2) -> M12.04
single gv                           M12.GV      -> M12.JHH
single "{reg}y{motion}              M14.01      -> M14.04
MULTI  } / P                        M14.PARA (2) -> M14.05
MULTI  :set shiftwidth / >>         M15.01 (2)  -> M15.04
MULTI  z / zp                       M15.ZP (2)  -> M15.ZPH
single Visual A{text}<Esc>          M15.BA      -> M15.05
MULTI  q{reg}...q                   M15.MAC (2) -> M15.08
single :g/pattern/command           M15.GLOBAL  -> M17.GNH (46 cards later)
single :[range]m{dest}              M16.MOVE    -> M16.05
single ci{object}                   M3.CI       -> M3.04
single ga                           M3.GA       -> M3.GAH
single "{reg}p                      M3.REG      -> M3.06
MULTI  . / M (misparse)             M3.DI (2)   -> M3.08
single Visual I{text}<Esc>          M4.BI       -> M4.BIH
MULTI  :vnew :silent dd :diffthis :set scrollbind <C-w> :diffoff! :bwipeout!  M4.DIFF (8) -> M4.DIFFH
single n                            M17.01      -> M17.05
MULTI  E / [count]W / B             M13.BE (3)  -> M13.04 / M13.06
single w                            M13.W       -> M13.WH
single g_                           M13.GU      -> M13.GH
single v                            M7.VIS      -> M7.04
single D                            M6.D        -> M6.04
single :[range]s/old/new/ (no g)    M18.EXPR    -> M18.EXPRH
```
