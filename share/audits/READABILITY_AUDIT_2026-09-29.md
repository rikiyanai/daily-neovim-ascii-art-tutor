# Popup readability audit — 2026-09-29

This audit is read-only. It proposes changes and does not make them.
Line numbers are from the working tree at 13:10 on 2026-09-29. At that time
another agent had uncommitted edits in `share/v2_runtime.py` and
`bin/vim-daily-gate`, so the numbers can move. Find each place by the function
name.

## How the screens were captured

All captures are headed tmux popups driven by the repo's own route drivers,
using the real user config. The text is plain, so colour was read from the code.

| Screen | Command | Sizes |
|---|---|---|
| Guided brief M0.01, M11.WS, M11.TR, M11.WSH (keys hidden) | `shots.py` (scratchpad) → `test_tmux_v2_routes.exercise(route="guided")` | 80x24, 188x49 (M0.01, M11.WS) |
| Brief scrolled, fail page, unchanged progress, pass page, awarded progress | `share/test_tmux_v2.py --show-capture` | 80x24 |
| Question pages, concept pass page | `exercise(route="concept", card_id="M0.P0" / "M0.03")` | 80x24 |
| Module check (5 questions, key-hidden brief, pass, progress) | `exercise(route="check", card_id="M0.08")` | 80x24 |
| Full tree | `python3 bin/vim-daily-gate --tree` (real state, read-only) | terminal |

Facts that apply to every finding:

- At 80x24 the popup's usable interior is **70 columns** (the border plus the
  tmux popup inset). Several clip widths were sized for 76–80 columns.
- The brief is a plain Neovim buffer. `brief_lua` in `bin/vim-daily-gate`
  (`run_editor`, around line 783) sets `wrap` and `linebreak` only. It has no
  highlighting, no `breakindent`, and no filetype. **Nothing in the brief has
  emphasis today.** Headings and the NEW CONCEPT ALERT are the same weight as
  body text.
- Result, question and progress pages are printed by Python. Bold comes from
  `cfg.colours` (`BOLD, DIM, OFF, GREEN, RED, YELLOW`, set in
  `bin/vim-daily-gate:74-75`). `RED` and `YELLOW` are unpacked as
  `_red, _yellow` in every renderer and **never used**.

---

## P0 — the learner loses content (fix first)

### 1. The concept/primer teaching is erased before the learner sees it
- **Screen:** every concept card, including the grammar primer. Checked on M0.P0 and M0.03 at 80x24.
- **Current:** `run_concept` (`v2_runtime.py` ~2700) prints the card id, the
  progress line, `TEACH FIRST` + `teaching_lines`, and `DO THIS ...`. It then
  calls `ask_question`, which runs `print("\033[2J\033[H")` (~806) whenever
  stdout is a tty. The captured question page starts at
  `ANIMATION Move the cursor through the Fireworks canopy…`. The M0.P0 teaching
  (`Vim's first small sentence is [count] + motion.` …) never appears on screen.
- **Problem:** content loss. The primer asks a question about material it has
  not shown. Neither the card id nor any progress context is on the page.
- **Change:** move the clear out of `ask_question` into its callers, before the
  page header, or pass a `header_lines` argument that `ask_question` prints
  after the clear. On the question page, print a bold title line
  `M0.P0 · Vim grammar primer · question 1/1`, then `TEACH FIRST` (bold) and
  its lines, then the question.

### 2. The DO THIS task sentence is cut to 54 characters in the compact brief
- **Screen:** compact brief at 80x24, every card.
- **Current:** `DO THIS · Inspect the padded missile still with visible…`
  (M11.WS), `DO THIS · The snow bunny's rows carry invisible trailing…`
  (M11.TR), `DO THIS · Answer five checks, then perform this key-hidden art…`
  (M0.08).
- **Problem:** the learner cannot read the task on the only screen that states
  it. For M11.WS the missing half is the actual instruction ("then remove only
  trailing spaces. Every visible missile and exhaust glyph must remain
  unchanged.").
- **Code:** `_write_session_lesson`, compact branch: `"DO THIS · " + _clip(card["prompt"], 54)`.
- **Change:** do not clip. Emit `DO THIS` followed by the prompt, pre-wrapped
  with `textwrap.wrap(prompt, 66)` to at most 2 lines (3 if needed), with a
  2-space hanging indent. To keep the first screen within budget, **delete the
  compact title row** `NEOVIM × ASCII ANIMATION · M11.WS`, because the winbar
  already names the pane, and move the card id into the progress row (see #5).
  DO THIS, TARGET and RECIPE still fit in the first 11 brief rows at 80x24.

### 3. The progress page scrolls its own heading off at 80x24
- **Screen:** module-check pass → awarded progress page (M0.08, 80x24).
- **Current:** the first visible line is `check`, the wrapped tail of
  `PROGRESS AWARDED · M0.08 · Fireworks radial loop · Module mastery c|heck`.
  The page is two rows too tall because four lines wrap in mid-word:
  the title, `STATE … ✓ mastered`, `XP … badg|es 4`, `CURRENT MODULE MAP … 0|7○ 08○`,
  plus the prompt `… f = f|eedback`.
- **Problem:** the outcome (awarded or not) is the first thing lost. Mid-word
  wraps (`ed|it`, `0|7○`, `ch|eckpoint`, `f|eedback`) look broken.
- **Code:** `_post_progress` (~2520), `print_tree(compact=True)` (~3328),
  `hold_open` prompt (`bin/vim-daily-gate` ~905), and the fail-restore line.
- **Change:** create one helper, `_fit(text, width)`, where
  width = `shutil.get_terminal_size().columns - 2`. The popup already reports
  its interior width, so that is 68 at 80x24. Route every result and progress
  line through it: `textwrap.wrap(..., break_long_words=False)` with a hanging
  indent. Title line: `PROGRESS AWARDED · M0.08` on its own line, and the card
  title on the next line in dim. Module map: wrap at `·`/space boundaries with an
  8-space hanging indent. Put the `hold_open` prompt on two short lines, or
  shorten it to `Enter close · r repeat · n next · f feedback`.

### 4. The compact TARGET breaks registration across animation frames
- **Screen:** M0.08 key-hidden brief, 80x24.
- **Current:**
  ```
  │    \¡/   │    \¡/   │    \¡/   │    \¡/   │    \¡/
  │   -—o—-   │   -—O—-   │   =—O—=   │   =—O—=   │   -—.—-
  │    /!\   │    /!\   │    /!\   │    /!\   │    /!\
  ```
- **Problem:** frame rows have different lengths, so the `│` separators drift
  column by column. A learner comparing frames reads the drift as the core
  moving. That is the exact registration defect the course teaches against.
- **Code:** `_compact_target_lines`: `"   ".join("│" + frame[row_number] ...)`.
- **Change:** pad each frame's rows to that frame's max width before joining:
  `w = max(len(r) for r in frame)` and `frame[row].ljust(w)`. Keep the existing
  `…` overflow guard.

### 5. The progress line is unreadable in every layout
- **Screens:** compact brief (80x24) and full brief (188x49).
- **Current:** compact:
  `PROGRESS S0 11/22 learning · M11 4/16 · XP 110 · LEVEL 2 Cell…`.
  Full, wrapped in an 80-column pane:
  `PROGRESS  S0 11/22 learning  ·  M11 4/16  ·  XP 110  ·  LEVEL 2 Cell Editor 30/`
  `80  ·  today 0/12  ·  streak 0 days …`.
- **Problem:** 9 numbers in one run with no visual weight. The level fraction
  splits `30/|80`. The part a learner cares about (how far through this module)
  is the second of nine items.
- **Code:** `_progress_line` (~1410). It is also used clipped to 70 in
  `run_concept`.
- **Change:** split it into a readable bar plus secondary stats.
  - Compact, one row, ≤ 66 cells:
    `M11.WS  M11 ▓▓▓▓░░░░░░░░ 4/16 · S0 11/22 · Lv2 30/80 · today 0/12`
  - Full, two rows:
    `M11 ▓▓▓▓░░░░░░░░░░░░ 4/16   S0 ▓▓▓▓▓▓▓▓░░░░ 11/22 learning` then
    `XP 110 · Level 2 Cell Editor 30/80 · today 0/12 · streak 0 · best 0`
  - Bar helper: `_bar(done, total, cells=12)` →
    `"▓"*round(cells*done/total) + "░"*rest`. Only glyphs already used by the
    course's font set. The `ultra` tree page and `CURRENT MODULE MAP` should use
    the same helper (see #11).

## P1 — hierarchy and emphasis

### 6. The brief has no emphasis: headings, ALERT and body are all plain text
- **Screens:** all briefs, both sizes.
- **Current:** `DO THIS`, `TARGET`, `RECIPE`, `COMMAND RECIPE`,
  `THE RECIPE, KEY BY KEY`, `WHY THIS EXISTS`, `KEYS WORTH KEEPING`,
  `★ NEW CONCEPT ALERT`, `HOW THE KEYS YOU NEED WORK` and `PROGRESS` all render
  exactly like body text.
- **Change (Neovim highlight on the brief buffer):** in `brief_lua` after
  `nvim_buf_set_lines`, add one namespace and extmarks:
  ```lua
  local ns=vim.api.nvim_create_namespace('vim_daily_brief')
  vim.api.nvim_set_hl(0,'VimDailyHeading',{link='Title',default=true})      -- bold in most schemes
  vim.api.nvim_set_hl(0,'VimDailyAlert',{link='DiagnosticWarn',default=true})
  vim.api.nvim_set_hl(0,'VimDailyNew',{link='DiagnosticWarn',default=true})
  vim.api.nvim_set_hl(0,'VimDailyProgress',{link='Special',default=true})
  vim.api.nvim_set_hl(0,'VimDailyKeys',{link='String',default=true})
  for i,l in ipairs(ls) do
    local s,e=vim.fn.matchstrpos(l,[[^\u[A-Z0-9 ×/,.'-]*\u\ze\(\s\s\|\s·\|$\)]])[2],...
    -- ★ lines → VimDailyAlert on the whole line (bold);
    -- heading run → VimDailyHeading on [s,e);
    -- '^  NEW  ' → VimDailyNew; '^PROGRESS\|▓' row → VimDailyProgress;
    -- text after 'RECIPE  ' and the key column of recipe rows → VimDailyKeys
  end
  ```
  Also set `vim.api.nvim_set_hl(0,'VimDailyHeading',{bold=true,underline=false})`
  as a fallback when `Title` has no bold attribute
  (`nvim_get_hl(0,{name='Title'}).bold`). Do **not** highlight the `  │` TARGET
  art rows. Glyph colour must not suggest a difference that isn't there.
  - A more robust alternative to the regex is for `_write_session_lesson` to
    write a sidecar `<card>.hl.json` of `[line, col_start, col_end, group]`,
    which `brief_lua` reads. The Python code then owns what a heading is, and
    the regex never guesses.
- **Code:** `bin/vim-daily-gate` `run_editor` → `brief_lua` (~783–806).

### 7. Heading names and separators are inconsistent
- **Current, all observed:** `DO THIS · …` (compact brief), `DO THIS` on its own
  row (full brief), `DO THIS  …` (result pages), `DO THIS: …` (`run_concept`,
  `run_check`, review), `DO THIS %s: …` (ultra concept).
  `RECIPE` (compact) vs `COMMAND RECIPE` (full) vs `THE RECIPE, KEY BY KEY` vs
  `THE ANSWER, KEY BY KEY` vs `DO / AVOID`. `HINT · …` vs `HINT` on its own row.
  `streak: 1 day · best 1 · all-time 0` (colon) vs `streak: 15 days   best: 15
  all-time completions: 56` (tree) vs `streak 0 days · best 0 · 0 drills all
  time` (brief).
- **Change:** one style. The heading is ALL CAPS and followed by two spaces for
  inline content, or by nothing when the content starts on the next row. No
  colons, no `·` after a heading. Rename: `COMMAND RECIPE` → `RECIPE`
  everywhere. `THE RECIPE, KEY BY KEY` → `KEY BY KEY`. `THE ANSWER, KEY BY
  KEY` → `KEY BY KEY` (it is on the result page, so the context is clear).
  Streak: always `streak 15 days · best 15 · 56 all time`.
- **Code:** `_write_session_lesson`, `_key_teaching`, `_answer_breakdown`,
  `run_concept` (~2652), `run_check` (~2729), review (~3091, ~3111),
  `print_tree` (both branches). Tests assert `DO THIS`, `RECIPE`,
  `KEYS WORTH KEEPING`, `PROGRESS`, `LESSON COMPLETE` and `ATTEMPT NOT PASSED`
  (share/test_v2.py, test_tmux_v2.py, test_tmux_v2_routes.py). Keep those
  tokens and change only the separators around them.

### 8. The fail page is not visibly a failure; RED and YELLOW are unused
- **Screen:** failed feedback page, 80x24.
- **Current:** `ATTEMPT NOT PASSED · M0.01 · …` is bold only, the same weight as
  `RESULT COMPARISON`. `LESSON COMPLETE` is green and bold. The `✗` row marker
  is plain.
- **Change:** `ATTEMPT NOT PASSED` and `REVIEW NEEDS WORK` → `red + bold`.
  `PROGRESS UNCHANGED` → `yellow + bold`. In `_artifact_replay` colour the `✗`
  marker red and the `•` marker green. Put `METHOD CHECK` failures in yellow.
- **Code:** `_post_feedback` (~2330–2350), `_post_progress` (~2528),
  `_two_column_replay` / `_artifact_replay` (~2100–2150). Unpack `red, yellow`
  and stop discarding them.

### 9. The full brief at 188x49 is 80 columns wide beside a mostly empty 86-column art pane
- **Screen:** M11.WS / M0.01 at 188x49.
- **Current:** every explanation wraps to 2–3 rows, and the NEW CONCEPT ALERT
  (below WHY THIS EXISTS) starts on row ~38, which is off the first screen for
  M11.WS. The art pane shows 12-column art in 86 columns.
- **Change:** size the brief from the art rather than a fixed 48%:
  `mw = columns - max(24, art_width + 10)`, capped at ~110. Also set
  `vim.wo[hw].breakindent=true; vim.wo[hw].breakindentopt='shift:4'` so that
  wrapped continuation lines are indented under their item instead of starting
  at column 0 like a heading. The captures show `the line end become visible
  marks…` and `(Enter runs it)` sitting flush-left as if they were headings.
- **Code:** `brief_lua` `wide` branch (`mw=math.min(84,…)`).

### 10. The NEW CONCEPT ALERT is hard to find and its banner is clipped
- **Screens:** compact M11.WS 80x24, full M11.WS 188x49.
- **Current:** banner `★ NEW 4 · :set list · cursorcolumn · colorcolumn ·
  :s///e · read…` (compact, clipped at 66) and `… · read NEW CONCEPT…` (full,
  clipped at 78 inside an 80-column pane). In the full layout the alert block
  itself is placed after WHY THIS EXISTS.
- **Problem:** the pointer to the alert is the part that gets clipped. In the
  full layout the alert is off the first screen on the lessons where it matters
  most (4 new ideas).
- **Change:** banner text `★ NEW · :set list · cursorcolumn · colorcolumn ·
  :s///e ↓`. Drop the count and `read NEW CONCEPT ALERT`: the ↓ plus the
  highlight in #6 do that job. In the full layout, move the alert directly after
  RECIPE and before KEY BY KEY. The comment at ~1573 says it was placed later to
  keep WHY on screen. With #9's wider pane both fit. Frame the alert with a blank
  row above and below, and a rule line `★ NEW CONCEPT ALERT ────────`.
- **Code:** `_new_concept_banner` (~1291), `_new_concept_alert` (~1308), full
  branch of `_write_session_lesson` (~1571–1578).

## P2 — density and polish

### 11. The skill tree: misaligned columns, ambiguous legend, no bars
- **Screen:** `vim-daily-gate --tree` (terminal), and compact tree on progress pages.
- **Current:** `◐ S0 Grid and overwrite            13/22  learning` vs
  `· S5 Variants and palette          0/12  locked` (the `%d/%d` is unpadded, so
  the state column drifts). Legend: `STATE  ○ available · locked ◐ learning …`.
  The `·` locked glyph is also the list separator, so this reads as "available ·
  locked". `A1 … 6/7 locked` and `M0 13/14 locked` read as contradictions.
- **Change:** use `%5s` for the fraction (`"%d/%d" % …` then `%-6s`). Add a
  12-cell bar before the fraction. Legend: `○ open  ◐ learning  ◆ check-ready
  ↻ review  ✓ mastered  ⋯ locked` (a distinct locked glyph such as `⋯` or `▫`,
  and no `·` separators inside the legend). Show a locked row that has progress
  as `6/7 · waits for S7`. Bold the section titles (`STAGES`, `Project/module
  ledger` → `MODULES`).
- **Code:** `print_tree` (~3328), `marks` dict.

### 12. Legacy prose is clipped line by line, which drops words from the middle of sentences
- **Screen:** compact brief scrolled to LEGACY VIM CONCEPT (80x24).
- **Current:** `In most editors, moving the cursor and changing the text are…` /
  `activities. You arrow over to a spot, then you do a thing. In…` /
  `an ingredient of the change, so the two collapse into one…`.
- **Problem:** each source line is clipped to 64 on its own, so the paragraph
  loses the end of every line and cannot be read.
- **Change:** join the paradigm lines into paragraphs and let the brief window
  wrap them (it has `wrap` and `linebreak`), or `textwrap.wrap(..., 66)`. The
  same applies to `key_vocabulary` lines (`_clip(line, 64)`) and the WHY rows
  (`_clip(…, 57/51/55)`). The window wraps, so the compact brief does not need
  clipping below the first screen. Keep clipping only for the first-screen rows
  (#2 budget).
- **Code:** `_write_session_lesson` compact branch (~1511–1531).

### 13. The recipe splits one Ex command into fake steps
- **Screen:** M11.TR compact 80x24.
- **Current:** `RECIPE  :% → s/\s\+$/ → / → e<CR>`.
- **Problem:** `→` means "then press" in every other recipe. Here it cuts one
  `:%s/\s\+$//e<CR>` into four "steps".
- **Change:** when the recipe items concatenate into a single `:`-command,
  display the joined command. Keep the per-piece breakdown under KEY BY KEY or
  REMEMBER only. Alternatively fix the card data so that a recipe step is a
  whole keystroke unit.
- **Code:** recipe join in `_write_session_lesson` (`" → ".join(...)`), or the
  M11.TR entry in `share/curriculum-v2.json` / `gen_curriculum_v2.py`.

### 14. Compact result pages clip or truncate the key-by-key text and choices while rows sit empty
- **Screens:** M0.08 pass page. The packed paragraph ends `r. = replace the
  character under the` because `wrapped[:3]` drops the rest. The M0.01 pass page
  leaves 4 empty rows under a packed paragraph. Question pages leave 5 empty
  rows while every other `VIM:` choice ends in `…`. On the concept pass page,
  `YOUR ANSWER  ANIMATION: … | NEOVIM: Find t|he star…` wraps mid-word, because
  a clip of 64 plus the 15-character prefix is more than 70.
- **Change:**
  - `_post_feedback_ultra`: never cut the packed paragraph in the middle of a
    sentence. If it does not fit, stop after the last complete `·` item and add
    `(+N more)`.
  - `_post_feedback`: measure against the real rows. The `status_lines = 3`
    reserve is too much when the title fits on one line (after #3), so try the
    unpacked layout first.
  - `_compact_choice_text`: allow the `VIM:` half 2 rows, with a hanging indent
    of 10, when the page has spare rows (4 choices × 3 rows + 4 = 16 ≤ 18).
  - `_print_choice_explanation`: set clip width = `columns - len(prefix) - 2`,
    and print `YOUR ANSWER` as the two-row ANIM/VIM form that the question page
    already uses.
- **Code:** `_post_feedback_ultra` (~2270), `_post_feedback` compact loop
  (~2360), `_compact_choice_text` (~757), `_print_choice_explanation` (~1015).

### 15. Question pages lack orientation and emphasis
- **Screens:** M0.08 check questions 1–5 and M0.03 at 80x24.
- **Current:** a check shows 5 pages in a row with no `question 2/5`. `ANIMATION`
  and `NEOVIM` labels and the `answer (a-d)` prompt are plain. The prompt reads
  `answer (a-d) · y copies this question · f feedback:`.
- **Change:** first row, bold: `M0.08 CHECK · question 2/5 · need 4/5`.
  Make the `ANIMATION` and `NEOVIM` labels bold, and the choice letters `a)`
  bold. Prompt: bold `answer a–d`, then dim `· y copy · f feedback`. After
  answering, prefix feedback with a green `✓` or red `✗`.
- **Code:** `ask_question` (~795–860), check loop in `run_check` (~2729+).

### 16. The success page repeats itself
- **Current:** `DO THIS  press Enter for skill-tree progress.`, and again at the
  bottom `Enter = skill-tree progress · f = feedback`. `DO / AVOID  j → f* →
  ro · exact target` repeats the ledger line directly above it.
- **Change:** on pass pages drop the top `DO THIS` (keep it on fail pages,
  where it carries the redo instruction). On compact pass pages drop
  `DO / AVOID` when the ledger row is `ok`.
- **Code:** `_print_feedback_do_this`, `_post_feedback_ultra`.

### 17. The KEY BY KEY list for M0.01 shows a key the RECIPE does not
- **Current:** RECIPE `j → f* → ro`, KEY BY KEY `j`, `0`, `f*`, `ro`, and the
  ledger `j0f*ro`. The `0` comes from `expected`, but the recipe hides it (it
  is the cursor step), so the two lists disagree on screen.
- **Change:** list the cursor step in RECIPE as `(0 cursor start)` or leave it
  out of KEY BY KEY. Either is fine as long as both show the same keys.
- **Code:** recipe join vs `_key_teaching` → `K.explain_lines(strings[0])`.

---

## Constraint check (80x24 first screen after P0 fixes)

Compact brief rows in the 11-row first screen, M11.WS:
1 progress + id (#5), 2–3 DO THIS (#2), 4 NEW banner, 5 TARGET, 6–8 art,
9–10 RECIPE (wraps), 11 ★ ALERT rule. DO THIS, TARGET and RECIPE all stay on
the first screen. The removed title row pays for the second DO THIS row. For a
cell with a 6-row TARGET (the case in the `mh` comment), put DO THIS on one row
plus `…↓` and keep the full text directly under the art. That tradeoff needs a
capture to confirm, and it has not been captured.

## Not verified here
- Colour and highlight rendering: captures are plain text. #6 and #8 are code
  proposals and have not been run.
- Clean mode (`VIM_DAILY_TEST_CLEAN=1`) was not captured.
- The review route, and the fail page for a concept card, were not captured.
