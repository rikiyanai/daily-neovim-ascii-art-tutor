# Dashboard and UI style — design proposal (2026-09-29, for discussion)

Status: PROPOSAL, not implemented. Produced by a planning agent from rendered
screens (`--tree`, `--learned`, `test_tmux_v2.py --show-capture`, an in-memory
M11.CUC brief). Operator asked for a design discussion (feedback 15:05, 15:30).

## 1. Style guide — semantic roles
| role | used for | ANSI | Neovim group | no-colour fallback |
|---|---|---|---|---|
| heading | section labels | BOLD | VimDailyHeading → Title,bold | ALL CAPS |
| key | keystrokes/commands | BOLD+CYAN (new) | VimDailyKey → String | backticks |
| new | ★ banner / alert / REMEMBER | YELLOW+BOLD | VimDailyAlert → DiagnosticWarn | ★ |
| success | LESSON COMPLETE, ✓ rows, filled bars | GREEN(+BOLD) | VimDailyOk → DiagnosticOk | ✓ |
| failure | ATTEMPT NOT PASSED, ✗ rows | RED+BOLD | VimDailyErr → DiagnosticError | ✗ |
| warning | PROGRESS UNCHANGED, ↻ revisit, METHOD CHECK | YELLOW | DiagnosticWarn | ↻ / ! |
| meta | ids, sources, e.g., prompts, empty bar cells | DIM | VimDailyMeta → Comment | — |
| art | TARGET/YOURS/BEFORE rows | never coloured | never matched | — |

- Groups take only the colorscheme's fg + bold. Honour `NO_COLOR` and `TERM=dumb`.
- Glyphs: ✓ ✗ ◐ ○ ◆ ↻ ▫(locked; `·` collides with the list separator) ★ → ▸/▾ `▕██░░▏`.
  Drop 🔥 (double width); bold the streak number instead.
- Density: heading + two spaces; no `…` in prose (wrap with hanging indent);
  clip only art rows. First screen = today's task only; the rest in a closed
  "MORE" fold.

Brief order at every size: status row (`M11.CUC M11 ▕███░░░░░░░▏ 7/21 · Lv3 40/80`),
DO THIS, ★ banner, TARGET, RECIPE, KEY BY KEY, ★ ALERT, `── MORE · za opens · / finds ──`.

### "Unrelated stuff" found in the M11.CUC brief (→ move into MORE or fix)
- SKILL line = module skill (replace-mode, undo, virtual columns); card uses none.
- WHY THIS EXISTS describes the TowerDefense missile while the art is Dracula.
- WHAT THIS LESSON BUYS YOU prints an internal family id.
- KEYS WORTH KEEPING lists sibling cards' commands (filter by this card's families).
- WHERE THIS METHOD COMES FROM / LEGACY, READING THE RECIPE, SUBMIT/STUCK,
  BASIC HELP, COPY/PASTE: identical on every card (→ MORE / F1).
- 9-stat PROGRESS row (`today 31/12`, `57 drills all time`) → status row only.
- Module title "Missile fixed-width redraw" over Dracula art.
- Compact TARGET shows side-by-side copies while the task says "below".

Highlight mechanism: A) extend matchadd + a manual fold (now); B) sidecar span
file → extmarks (if regexes misfire).

## 2. Dashboard / skill tree
Options: A) static flags `--tree` (current stage expanded), `--tree --all`,
`--tree S3` (first); B) in-popup `t` + stage keys; C) dashboard as a read-only
Neovim buffer with folds (zo/zc/za/zR/zM) — real Vim practice (later).
Motivation: level bar naming the next title; 14-day streak strip; daily goal
`today 32 · goal 12 ✓`; "+N commands" on the awarded page; next-badge progress
(badge rules → data table); milestone banner only on stage mastery / level-up.
No nags or loss framing.

80×24 awarded-page mock:
```
PROGRESS AWARDED  M11.CUC                                   +10 XP
Line up two copies with the cursorcolumn guide
+1 command  :set cursorcolumn
Lv3 Pose Builder    ▕█████████░░░░░░░▏ 50/80 → Lv4 Frame Crafter
streak 15 · best 15  ■■■■■■■■■■■■■■  today 32 · goal 12 ✓
next badge  grid-author: master S0  ▕█████████░░░░░░░▏ 15/27
YOUR JOURNEY  stills S0–S7 → animation A0–A7 · P side branch
▾ ◐ S0 Grid and overwrite  ▕█████░░░░░▏ 15/27  ← you are here
    ◐ M11 Missile redraw  8/21  WS✓ CUC✓ TR↻ LS✓ … 13 left
    ◆ M0  Fireworks loop 13/14  08 check ready
▸ ▫ S1–S7 stills 0/65          ▸ ◐ A1 Extremes 6/7 (after S7)
▸ ▫ A0 A2–A7 animation 0/119   ▸ ▫ P  Shift_JIS  0/8
↻ 5 to revisit · 20 commands learned
Enter close · r repeat · n next · t tree · f feedback
```

## 3. Implementation order
1. Brief restructure (`_write_session_lesson`: status row, family-filtered
   KEYS WORTH KEEPING, MORE fold; `BRIEF_HIGHLIGHT_LUA` Meta/Ok/Err + fold) ~120 lines.
2. Style object (`Style` namedtuple, NO_COLOR/TERM=dumb) ~80 lines.
3. Remaining `…` clips (`_compact_choice_text`, `✗ chose` line, key-by-key cut) ~60 lines.
4. Dashboard option A (`print_tree(expand=)`, level bar, streak strip, badge
   table, `t` in `hold_open`) ~150 lines; tests to update: test_v2 streak
   strings, test_tmux_v2 `streak:` checks (keep words, change punctuation).
5. Option C Neovim dashboard buffer ~120 lines + a headed route test.

New tests: NO_COLOR has no `\x1b`; no progress/result row wider than
columns-2 at 80×24; DO THIS/TARGET/RECIPE before the first `──` rule.
Risks: fold plugins (nvim-ufo) overriding folds; regex false positives;
card-level WHY/BUYS needs authoring.
