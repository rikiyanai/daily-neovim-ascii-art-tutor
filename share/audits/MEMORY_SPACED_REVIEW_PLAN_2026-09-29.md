# Memory, repetition and anatomy — plan (2026-09-29, for discussion)

Status: PLAN, not implemented (except the substitute anatomy diagram, VD-49).
Produced by a planning agent. Driven by operator feedback 13:33 ("lots of
repetition in different convos … flashcard deck … memory anchor … reminder
line about the syntax") and the chat quiz of 2026-09-29.

## Quiz evidence (chat, 2026-09-29) — misconceptions to target
1. `3G` read as "end of three blocks" (it is line 3; G alone = last line of the FILE).
2. `fo` read as a whole-file search (f = current row only; `/` = file).
4. `3yy G p` described only as "yank three lines" (missed G = last line, p = put below).
5. Described only the ranged `:4,6s`; missed that no range = current line only.
6. Asked how to change the whole file (`%` goes BEFORE s) or only 3 matches.
9. Guessed the undo-branch / `g-` answer.
10. `2G$` read as "down 2 lines" (it is absolute line 2); pattern `$` read as
    "up to end of line" (it is an anchor that only matches at the end).
Correct: 3 (rO), 6 (g flag), 7 (colorcolumn), 8 (x vs r).

## 1. Anatomy diagrams (generalise VD-49's `substitute_anatomy`)
`v2_keys.anatomy(keys, width)` over structural slots: `:` commands (range,
command, dividers, pattern atoms, replacement, flags) and Normal keys from
`explain()` (count, register, operator, motion — e.g. `3yyGp`). Right-to-left
`│ └` tree, labels from SYMBOL_ROLES/pattern_parts, then IN PLAIN WORDS and a
SHAPE line (`:{where}s/{find}/{replace}/{flags}`, `{N}G = line N from the top`,
`[count] verb where`, `f{char} = this row only`). ≤10 slots / ≤78 cells else
fall back. Brief first screen gets only the SHAPE line; full diagram in the
alert/REMEMBER, the deck back, and after a wrong drill answer.

## 2. Flashcard deck with spacing
- `share/deck-v2.json` (authored): per family `{id, family, front, back,
  anchor, shape, contrasts, items[]}`; items are predict / typed_keys /
  decode with a named misconception. Generator validates and embeds as `cur["deck"]`.
- Anchors: G "ground floor = bottom of the file"; gg top; f "finger along this
  row"; / "search the whole file"; $ "the end: row end / last line / pattern
  wall"; % "100% of lines"; p/P "put below / Put above"; :s "fill-in form";
  g flag "global on the line"; e flag "excuse the errors"; \ "power-up for the
  next letter"; u "one step back"; g- "time machine across branches".
- Contrast pairs drilled together: f vs /, {N}G vs {N}j, G vs gg, $ roles,
  p vs P, :s vs :4,6s vs :%s, g flag vs none, x vs r, u vs g-, / vs \.
- Scheduling: `deck` events → `progress["deck"][item] = {box, next_due,
  lapses}` + a weak set; boxes reuse review_intervals_hours; again/hard/good;
  not counted toward XP or mastery.
- Runs: `--deck` (browse; `--learned` alias), `--quiz [N]` popup drill (weak →
  due → new), daily warm-up of ≤3 items before the first lesson (skippable,
  picked from the upcoming lesson's families + contrasts).
- Resurfacing: a failed paired question or remediation makes that family's
  items due; external misses via `--deck-miss ITEM…`; weak families get a
  REMEMBER diagram in the next lesson that uses them.

## 3. The eight misconception items
DK.G.01 (3G from line 5 → line 3), DK.F.01 (fo on a row without o → nothing;
reach it with /o or 3Gfo), DK.YP.01 (decode + do 3yyGp), DK.S.01 (`:s` with no
range changes only the current line), DK.S.02 (whole file: `:%s/-/=/g`),
DK.S.03 (exactly 3 matches: a number after `:s` counts lines, not matches; use
`f-r=` then `;.` `;.`), DK.U.01 (u vs g-), DK.D.01/02 (2G$ = end of line 2;
pattern `$` is a wall, `:%s/-$//` changes only rows ending in -).

## 4. Result right, method different
Tier 1 taught method: pass. Tier 2 declared alternative
(`method_requirement.accepted_alternatives`): pass, record it, make the taught
family's deck item due, say "your way counts". Tier 3 undeclared method with an
exact result: yellow `RESULT ✓ · METHOD ✗`, name both methods, log keys for
promotion. Keep a strict method gate only on single-idea guided cards.

## 5. Implementation order (≈1,300 lines, 3–4 sessions)
1. `anatomy`/`slots`/`SHAPES` in v2_keys + snapshot tests (incl. every card's
   expected ≤78 cells).
2. deck-v2.json (~40 families + 8 items) + generator validation (every family
   in any expected has a card; typed items pass `_safe_typed_effect`).
3. `project()` deck fold, `deck_due`, `record_deck`, remediation hooks; test_deck.py.
4. `--deck`, `--quiz`, `--deck-miss`; warm-up in `run()`.
5. Method tiers in `_required_method_error` / `_post_feedback`.
6. Headed evidence at 80×24/100×36/188×49 (quiz right+wrong, warm-up skip,
   M11.LS alternative wording), routes 28/28, 0 orphans; FL entry.
Risks: 80×24 brief budget; deck ids keyed to parser family strings; warm-up
friction; loose alternative regexes.
