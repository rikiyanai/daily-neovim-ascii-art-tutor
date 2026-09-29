# Symbol and recipe-notation audit · 2026-09-29

Scope: all 226 cards in `share/curriculum-v2.json`, read in module order
(`modules[].card_ids`). FAILURE_LOG entry: VD-40.

Trigger: operator feedback after M11.TR (`:%s/\s\+$//e`): "what are these
called? what is the concept diff between / and \ i thought \ was an escape seq
or something. also do not remember learning this ... how do i not memorize
these things? a reminder line about the syntax maybe helpful".

Question asked of every card: does the card use a symbol in a job that
depends on context (`$`, `%`, `.`, `^`, `|`, `0`, `,`, `/`, `\`, `@`, `*`,
`"`, `#`, `<C-r>`) or a piece of recipe notation (`<CR>`, `<Esc>`, `<C-x>`,
`{char}`, `{N}`, `[count]`, `:`), and did the card or an earlier card say in
plain words what that job is?

## Method

- `v2_keys.symbol_roles(keys)` (new, VD-40) lists the (symbol, job) pairs a
  key string uses. It works from `v2_keys.explain()` chunks: range and
  destination addresses of `:` commands, the separator and pattern pieces of
  `:s`/`:g`, `/` searches, `{char}` targets, typed Insert text, motions,
  registers and key notation.
- For each pair: the first card in module order whose `expected` uses it,
  whether that card is guided (recipe shown) or hidden, and the first guided
  card.
- "Explained before the fix" was confirmed by reading the card's recipe,
  hint, key_vocabulary, `explain_lines` and the NEW CONCEPT ALERT printed by
  `v2_runtime._new_concept_alert` at revision 66ca46c.
- The scan is a candidate list. Each row below was confirmed by reading the
  card.

## Ranked findings

Severity: **S1** the learner meets a second meaning with no signal that the
meaning changed, or a hidden card needs it first; **S2** first meeting of a
job has no plain-word explanation; **S3** notation or jargon used before it
is defined.

| # | Sev | Symbol / notion | First use (card, mode) | Other jobs already met | Explained before the fix? |
|---|---|---|---|---|---|
| 1 | S1 | `\` pattern prefix (`\s`, `\+`) | M11.WS guided | `\` typed as an art glyph in `/!\` (M0.O) | Partly: VD-39 SLASH_NOTE said "\ ... it is not a key you press", which is wrong (the learner does type it) and gave no contrast with M0.O. This is the operator's question. |
| 2 | S1 | `$` three jobs | last-line address `:1,3t$` M0.T; pattern anchor `\s\+$` M11.WS; end-of-row motion `2G$` M11.LS | each met before the next | Each job glossed on its own card only ("after the last line", "the end of the line"); no card said the same key had changed job. |
| 3 | S1 | `@` as `:s`/`:g` separator; `\\` = one backslash | M11.05 hidden (`:s@/@\\@g`), then M7.05, M17.06, all hidden | `/` separator (M0.SR), `\` prefix (M11.WS) | No. Never on a guided card; the alert listed nothing because the family `:s/old/new/g` was already "shown". |
| 4 | S1 | `\` before `. * /` = literal | M17.06 hidden | `\` glyph, `\` prefix | No; never guided. |
| 5 | S1 | `0` as line address (`:m0`, `0read`) | M16.05 hidden; first guided M4.DIFF | `0` = column 1 (M0.01), `0` inside a count (`10G`, M2.08) | M16.05: no. `_dest_words` said "before line 1" only in the answer breakdown after the attempt. |
| 6 | S1 | `.` = dot repeat | M1.05 hidden; first guided M17.01 | `.` as a glyph target (`f.`, `r.`, M0.08) | Alert named the family (VD-37 digraph fix); no contrast with `.` the glyph. Still tested before a guided card (open). |
| 7 | S2 | `:` command line / "Ex" | M0.SR guided | Normal mode keys only | No. Recipe said "execute the complete Ex statement"; "Ex" and "command line" were never defined. |
| 8 | S2 | `<CR>` notation | key_vocabulary of M0.01 (`/pattern<CR>`), keys of M0.SR | — | Only in the "READING THE RECIPE" footer at the very bottom of the brief; the compact (80×24) footer did not list `<CR>` at all. |
| 9 | S2 | `<C-r>` style notation (hold Ctrl) | M11.UR guided | — | No. `<C-v> Ctrl-v` in the footer only; "hold Ctrl" never said. |
| 10 | S2 | `{char}`, `{N}`, `{reg}`, `{range}`, `[count]` placeholders | alert of M0.01 (`f{char}`, `r{char}`), vocabulary of M0.YP/M0.02 | — | No card said braces are placeholders that are never typed. |
| 11 | S2 | `\|` column motion vs `\|` glyph in one card | M11.VE guided (`12\|i\|<Esc>`) | — | No contrast; both are new on the same card. |
| 12 | S2 | `<C-r>` redo vs `<C-r>{reg}` paste | M11.UR / M14.01 guided | redo | Explain line for M14.01 contrasted it (VD-37); alert did not. |
| 13 | S2 | `"a` register prefix | M14.01 guided | — | Only jargon vocabulary: `"{register} selects storage`. |
| 14 | S2 | `#` alternate file | M4.DIFF guided | — | No: explained as "run the command-line command 'silent 0read #'". |
| 15 | S2 | `%` every line vs this file vs bracket motion | `:%s` M11.WS, `:read %` M16.02, `%` M3.01 | | `:read %` contrasted (VD-37); `:%s` and `%` motion never contrasted. |
| 16 | S2 | `,` range (`4,6`) vs `,` motion | M0.02 / M12.FIND guided | | Range glossed as "lines 4-6"; no contrast later. |
| 17 | S3 | M11.UR alert printed "u undo; Ctrl-r redo" twice | M11.UR | | Duplicate teaching line (families `u` and `<C-r>` share one line). |
| 18 | S3 | Echo lines on M4.DIFF/M4.DIFFH | `:vnew`, `:silent 0read #`, `:diffoff!`, `:bwipeout!` | | "run the command-line command 'vnew'"; `!` broke the EX_NAMES lookup. |
| 19 | S4 | 6 families without FAMILY_TEACH, 22 without EXAMPLES | M4.DIFF, M16.02, M0.01, M11.LS, … | | Alert fell back to the echo meaning or printed no example. |

Glyph-only uses with no competing job at that point (`*` in `f*` M0.01, `/`
in `/!\` M0.O, `^` as a glyph M17.04) are not findings by themselves; they
become the contrast for rows 1, 2 and 3.

Not found in any card's keys: `^` first-glyph motion, `*` word search, `*`
pattern repeat, `'<,'>` range, `.` current-line address, `.` any-character
(M2.05 uses `[.o]`, where `.` is literal inside brackets).

## Fixes made (VD-40)

- `share/v2_keys.py`
  - `SYMBOL_ROLES`: 42 (symbol, job) pairs, each with one plain sentence and
    a short contrast label. `symbol_roles(keys)` detects them (cached).
  - `RECIPE_READING`: the one-time "HOW TO READ A RECIPE" block (keys left to
    right; `<CR>`/`<Esc>`/`<C-r>`; placeholders never typed; Normal, Insert
    and command-line modes).
  - `_explain_ex`: `!` no longer breaks the name lookup; `:vnew`, `:silent`
    (recursive), `:read #`/`:read %` with `0` = above line 1, `:diffoff!`,
    `:bwipeout!` explained in words.
  - FAMILY_TEACH: 9 entries added; EXAMPLES: 24 added. Every family in the
    course now has a teaching line; only `h j k l` lack an example.
- `share/v2_runtime.py`
  - `_symbol_lines` (in the NEW CONCEPT ALERT / REMEMBER block, below the
    first screen): `★ NEW` the first time a job appears, `REMEMBER` on
    guided cards when the symbol has another job the learner met, each with
    "elsewhere $ = last line (:1,3t$) (in M0.T)". Key notation and
    single-job symbols (`:`, `"`, `#`) get one `★ NEW` line the first time.
  - The first guided recipe card (M0.01) carries the HOW TO READ A RECIPE
    block.
  - `_new_concept_banner` names new symbol jobs (`★ NEW 2: :t{dest} · $ =
    last line ↓ alert below`), so a card with no new command still announces
    the new job on the first screen, in the row the banner already used.
  - SLASH_NOTE corrected ("you type it, it is not Esc") and dropped where the
    SYMBOLS block already covers `/` and `\`.
  - Alert teaching lines de-duplicated (M11.UR).
  - READING THE RECIPE footers list `<CR>` (compact) and placeholders.
  - `--learned` ends with "SYMBOLS WHOSE JOB DEPENDS ON WHERE THEY STAND":
    one reminder line per symbol met in 2+ jobs (`learned_symbols`).
- `share/gen_curriculum_v2.py`: the three `<CR>` recipe rows "execute the
  complete Ex statement" / "execute the Ex sentence" now read "press Enter
  to run the whole : command line".
- `share/test_v2.py`: assertions for rows 1, 2, 3, 5, 9, 10, 11, 17, 18 and
  the learned-symbols deck.

## Still open

- Rows 3, 4, 6: `@` separator, `\\`, `\.`-style escapes, dot repeat and `0`
  address are still first required on hidden cards; they now get a ★ NEW
  symbol line there, but no guided single-idea card precedes them. Adding
  cards needs authored questions and count updates.
- "Ex", "address", "linewise" remain in question stems and key_vocabulary
  prose (authored records); the `:` symbol line now defines "Ex commands".
- M0.01 recipe rows still omit the `0` that `expected` uses (overload audit
  F7).
