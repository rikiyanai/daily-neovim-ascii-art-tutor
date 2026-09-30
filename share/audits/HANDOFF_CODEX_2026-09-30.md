# Handoff to Codex — daily Neovim ASCII-art tutor (2026-09-30)

Written by the Claude session that built VD-42…VD-63. Read this first, then the
failure-log entries it cites. `FAILURE_LOG.md` is the durable owner for every
defect, decision and piece of evidence; this document is the index and work
queue. It does not replace FL entries — append a new VD entry for each change.

## 1. Tree state at handoff

- Branch `main`, HEAD `e811653`, pushed to `origin/main` (public repo
  `rikiyanai/daily-neovim-ascii-art-tutor`).
- Uncommitted, NOT ours: `share/demo_ui_proposals.py` and
  `share/demo_notes.json`. They were written by the omp session (tmux pane
  main:4.5): a stdlib design demo where the operator leaves notes with
  `--note ID "text"`. Do not delete them. Read `demo_notes.json` for operator
  design notes, and ask the operator before committing either file.
- Suite green at `e811653`. The commands are in §5.

## 2. Operator standing rules (learned the hard way; FL cites in brackets)

- **Evidence before claims.** A completion word needs a headed tmux capture or
  test output from after the last change. Headed popup evidence is required at
  80x24, and also at 100x36 and 188x49 for layout changes.
- **No template or "validator prose" text shown to the learner.** That covers
  internal ids, "family", "Ex", "address", card-design jargon and generic hint
  templates [VD-28, VD-47, VD-53]. `share/test_question_quality.py` and the
  deck gate in `share/deck.py` enforce part of this. Read your own screens
  anyway.
- **One idea per step.** No bundling. A NEW concept gets a ★ banner, an alert
  and reinforcement before any retrieval [VD-42, VD-45].
- **No "…" clipping of prose.** Wrap with a hanging indent. Only art rows may
  clip [VD-44, VD-49].
- **Copying must work in normal tmux panes.** Never change global tmux
  options. Tests kill orphaned `nvim --embed` with `pkill -9` scoped to their
  temp dir [VD-31].
- **Rights: CLEARED with credit** [VD-60, VD-61]. The operator confirmed that
  Stone Story RPG (Gabriel Santos, Martian Rex, Inc.), AAHub, Joan G. Stark
  (jgs), and the "pb", "tre" and unsigned art in `share/art.json` may be
  published if credited.
  - This supersedes VD-52's "keep all push/publication blocked".
  - Every `art.json` entry now has a `credit` field.
  - New third-party art needs a credit before it is shipped.
- **Commits:** conventional format. The repo's commit hook rejects attribution
  trailers. Commit and push when the operator asks ("commit and push all").
- **Other agents work in this tree at the same time** (Claude, omp, you).
  Check `git status` and diff before editing. Never revert hunks you did not
  write. Check the max VD id right before appending to FAILURE_LOG.

## 3. Architecture map (what lives where)

| Area | Files | Notes |
|---|---|---|
| Gate / popup | `bin/vim-daily-gate`, `tmux/*.sh` | `v2_modes`; `hold_open` keys: Enter, r, n, f, d (dashboard), v (watch again) |
| Runtime | `share/v2_runtime.py` | `run()` modes; `project()`; lesson flow; `watch_your_work`, `completed_gallery`, `project_view`, `open_dashboard` |
| Key explanations | `share/v2_keys.py` | `explain`, `anatomy` (Normal + `:s` trees), `substitute_anatomy`, SYMBOL_ROLES |
| Curriculum | `share/gen_curriculum_v2.py` → `share/curriculum-v2.json`; `share/questions-authored-v2*.json` | always regenerate; hand-authored questions only |
| Stone Story art | `share/stone_story_variants.py`, `share/audits/stone-story-animation-audit/` | real frames; provenance in `share/audits/STONE_STORY_LOCAL_PROVENANCE.md` |
| Flashcards | `share/deck-v2.json`, `share/deck.py` | `--deck`, `--quiz [N]`, `--deck-miss`, daily warm-up (skip `s`) [VD-59] |
| Dashboard | `share/dashboard_tui.py`, `share/dashboard_theme.py`, `share/requirements-dashboard.txt` | Textual 8.2.8 in venv `~/.local/share/vim-daily-venv` (install.sh); static fallback [VD-58, VD-63] |
| Viewer | `share/viewer.py` | stdlib; WATCH YOUR WORK after a pass; `--view [MODULE|LESSON]` [VD-62, VD-63] |
| Feedback | `~/.local/state/vim-daily/feedback.jsonl` | `f` anywhere; `--feedback` prints [VD-43, VD-46] |
| Learner state | `~/.local/state/vim-daily/` | `events-v2.jsonl` is append-only; `projects/*/checkpoints/<card>-{before,after}.txt` |

Env switches: `VIM_DAILY_VIEWER=off`, `VIM_DAILY_ANIM=off`, `VIM_DAILY_NO_WARMUP=1`,
`NO_COLOR`, `VIM_DAILY_TEST_COLUMNS/ROWS`.

## 4. Shipped today (newest first)

`e811653` gallery · `fa4ae61` viewer · `b72360d` AAHub/others credit ·
`3a4da10` trophy art · `e0bc208` Textual dashboard + deck/warm-up · `d512e12`
wrong-answer page, method-miss wording, `:s` anatomy · `0a2cd74` symbol jobs ·
`66ca46c` dashboard journey · `4710d8b` pasted feedback · `097469e` M11 splits ·
`0a1240a` readable screens · `5f76730` feedback key · `94ec213` NEW CONCEPT ALERT.
Details: VD-42…VD-63 in FAILURE_LOG.md.

## 5. How to verify (run from the repo root)

```
python3 share/test_v2.py                 # 226/226 lessons, 185/185 recipes
python3 share/test_question_quality.py   # 406 questions
python3 share/test_feedback.py
python3 share/test_deck.py               # includes a headed 80x24 warm-up
python3 share/test_dashboard_tui.py      # Textual Pilot + pty NO_COLOR
python3 share/test_viewer.py             # model + pty playback + gallery
python3 share/test_stone_story_variants.py
python3 share/test_stone_story_provenance.py
python3 share/test_drills.py
python3 share/test_tmux_v2_routes.py     # 28 headed routes, viewer off
for s in 80x24 100x36 188x49; do          # headed popup incl. viewer + v
  VIM_DAILY_TEST_COLUMNS=${s%x*} VIM_DAILY_TEST_ROWS=${s#*x} python3 share/test_tmux_v2.py
done
pgrep -fl 'nvim --embed'                 # must be empty afterwards
```

zsh gotchas: `timeout` does not exist on macOS, and zsh does not word-split
unquoted variables. Use `${s%x*}` as above, or functions.

## 6. Work queue

### 6A. Planned, approved direction, NOT executed (UI)

Source: `share/audits/DASHBOARD_UI_DESIGN_PROPOSAL_2026-09-29.md` (see its
"Operator decisions" section) and the operator's `demo_notes.json`.

1. **One style guide for all surfaces.**
   - Today there are three palettes: the gate's ANSI 6-tuple, `viewer.Style`,
     and `dashboard_theme.STYLE`. Make one role table (heading, key, new, ok,
     fail, warn, meta, concept, flags, art-never-coloured) that all three read.
   - Honour NO_COLOR and TERM=dumb.
   - Operator notes lane2 / lane3a:
     - every ✓ is green;
     - "+N" is green;
     - 🔥 appears next to the streak and glows on a best-ever streak;
     - level tiers: beginner no colour, intermediate bronze, advanced gold,
       pro "gemini".
2. **Partial-credit wrong-answer page** (operator note lane2c).
   - In `_print_choice_explanation` / `_post_feedback`, colour only the wrong
     keys red and keep the right keys green.
   - Colour-code the CONCEPT line by slot: `:{where}s/{find}/{replace}/{flags}`.
   - omp designed this in `demo_ui_proposals.py` (STYLE / lane2c sections).
     Port it into the runtime.
3. **Lesson brief restructure** (proposal §1).
   - Status row first, then DO THIS / TARGET / RECIPE.
   - Everything identical on every card (SKILL, WHY, BUYS, sources, help,
     copy/paste) goes into a closed `MORE` fold.
   - Filter KEYS WORTH KEEPING to this card's families.
   - Fix the "unrelated stuff" list in the M11.CUC brief (proposal §1).
4. **Level ladder and avatars.**
   - Operator note (style, 22:12): "ALL THE AVATARS FOR LV3 TO LV7 ARE ASS.
     PROPOSE MULTIPLE AVATARS FOR EACH."
   - Produce 3+ original options per level, as a reviewable demo, then let the
     operator pick.
   - The tier cut-offs (4/8/12) in `dashboard_theme.TIERS` are a first
     proposal.
5. **Badges.**
   - The static `--tree` lists only the 8 runtime badges; the dashboard has 21.
     Unify on `dashboard_theme.BADGES`.
   - The operator wants more badges, each with a colour ASCII icon.
6. **Trophy / unlock moment.** When a badge or level is earned, play its trophy
   (`dashboard_theme.trophy_for`) in the viewer with the combined effects the
   operator asked for (pulse + gradient + sparkle; demo notes anima, animb,
   animd). Today trophies only appear on the dashboard badge page.
7. **Deck follow-ups** (VD-59):
   - the one-line SHAPE reminder on the lesson's first screen;
   - REMEMBER blocks drawing Normal-mode trees, not only `:s`;
   - a tmux key for `--quiz` in a popup;
   - deck families beyond M0/M11 (`COVERAGE_MODULES` in `share/deck.py`);
   - bump the curriculum revision string.
8. **Method tiers** (memory plan §4, deferred by the operator): "your way
   counts" for declared alternatives, and yellow `RESULT ✓ · METHOD ✗` for
   undeclared methods.
9. **Viewer follow-ups:**
   - a Pilot test for gallery Enter/`w`;
   - the viewer uses the unified style guide (item 1);
   - `preview_project` (automatic module-check playback) cannot find projects
     saved under an old folder name. `project_view()` already has the fallback;
     reuse it.

### 6B. Curriculum / pedagogy leftovers

- VD-45: split M4.DIFF (8 ideas / 18 steps), M11.VE and M13.BE.
- VD-45: teach digraphs before M1; fix the typing walls in M10, M1.04, M19 and
  M18.06.
- VD-45: count-variant NEW detection (`3@q`, `2<C-a>`); explain M18.EXPR; fix
  the hint template that names unused tools; fill 9 FAMILY_TEACH and 20
  EXAMPLES gaps; replace recipe placeholders (`C...`).
- VD-48: `@`, `\\`, `\.`, dot-repeat and the `0` address are first required on
  hidden cards. Each needs a guided single-idea card before it. Remove "Ex" and
  "address" from stems and key_vocabulary. M0.01 recipe rows omit the `0` that
  `expected` uses.
- VD-42: review M11.UT for bundling.
- VD-47: the M11.TR "art was offset" report was never reproduced.
- VD-29: per-variant questions for transfer variants.
- VD-52 (your own thread): M19 headed proof at all three sizes, and the full
  route matrix.

### 6C. Unspecified — needs an operator decision before building

1. **"Gemini" palette source.** The operator: "GEMINI IS A PALETTE NAME, pink
   purple-ish. SEE THE Y9-2 GRADIENT." I did not find a pink-purple gradient
   in `/Users/r/Projects/asciicker-Y9-2/scripts/` (`anim_B_rainbow.py` is full
   hue, `anim_B_cool.py` is green-cyan-blue, and there is `anim_B_hellish.py`).
   Operator follow-up: the game has a gradient effect on certain enchanted
   items (like Minecraft enchant glint). The best lead is the Stone Story
   StoneScript `Rainbowifier`
   (`asciicker-Y9-2/articles/discord-3d-pixel-art-godot-media/SSRPG/Rainbowifier-139bcfe26295ad62.txt`,
   plus `RainbowWitch-*.txt`). It is a 48-stop colour cycle; its pink→purple
   band is `#FF324F #FC255F #F61A6F #EF1180 #E60A91 #DB04A1 #CE01B1 #C000C0
   #B101CE #A104DB #910AE6 #8011EF`. Use that band, stepped over time like the
   script's NextShade, for the pro tier. Show it to the operator before
   shipping. `dashboard_theme.TIERS["pro"].gradient` is a placeholder until then.
2. **TUI library in the popup.** The operator chose Textual ("i go with tui
   lib"), and the dashboard uses it. omp's demo still says "TUI-lib … reject
   for popup". The operator's choice wins. Confirm whether lesson screens
   (not only the dashboard) should move to Textual.
3. **Where trophies and level-ups play:** in the result page, in the viewer, or
   in both. And how long, given the operator's ≤2 s preference in omp's plan.
4. **"Post to GitHub?"** for feedback (future; VD-47). Decide the target (issue
   vs discussion) and the auth.
5. **Stripped signatures** (jgs / pb / tre) were removed from the lesson art at
   intake. Decide whether to restore them in the art or keep the credit in
   metadata only.
6. **Committing omp's demo files** (`share/demo_ui_proposals.py`,
   `share/demo_notes.json`).

## 7. Known environment facts

- The installed runtime is `~/.local/share/vim-daily` → a symlink to `share/`.
  The gate does NOT put `share/` on `sys.path`, so load sibling modules by file
  path (`_deck_module`, `_keys_module`, `_viewer_module`) [VD-62].
- The operator's real progress: M0 mostly done, M11 in progress (12/20),
  15-day streak. Their chat-quiz misses are seeded as due deck items [VD-59].
- tmux `send-keys` with a lone `;` argument is a command separator; send `\;`.
