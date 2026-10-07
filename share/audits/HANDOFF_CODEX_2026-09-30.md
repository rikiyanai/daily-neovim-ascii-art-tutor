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
python3 share/test_v2.py                 # current VD-80: 250/250 lessons, 209/209 recipes
python3 share/test_question_quality.py   # current VD-80: 430 questions
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
pgrep -fl 'nvim --embed'                 # inspect ownership; preserve real learner sessions
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

## 8. Codex integration closeout (2026-09-30, VD-64…VD-77)

Sections 6A/6B have implementation and regression coverage in the working
tree: shared roles/partial-key colors, task-first MORE folds, badges/rewards,
method tiers, deck/quiz integration, viewer/gallery/project lookup, guided
prerequisites, split/reinforced concepts, truthful supplied-source edits and
paired transfer/review questions. This is not an operator acceptance or a
commit/push receipt. `demo_notes.json` and `demo_ui_proposals.py` were read and
preserved; current 16:00 M0.01 feedback was included in the corrected recipe
and fresh headed/canonical checks. M11.TR's historical offset report remains
unreproduced; its actual authored command passes headed at all three sizes.

Latest canonical proof: 248 lessons, 207 primary edit recipes, 428 questions;
all registered runtime/style/dashboard/viewer/deck/provenance/encoding/setup
and animation-pack gates pass. Automatic popup/viewer, Prefix+Q, direct
M19.01/.02/.VRH and alternate M19.06 pass at 80x24,100x36,188x49. Fresh full
28-route matrices collected after the last lesson-text edits also exit 0
at all three sizes: 84 headed routes total (VD-77).

Section 6C status:

- Celebrations: decided and verified — viewer only, one skippable batch,
  two seconds maximum, automatically launched whenever a lesson or spaced
  review earns a new badge/level (VD-78), static/no-color/off fallbacks and
  complete credits. No manual viewer launch is required.
- Avatars: fifteen original review candidates in `share/avatar_options.py`
  (`python3 share/avatar_options.py`); no Lv3–Lv7 choice applied.
- Gemini: requested twelve-stop pink-purple band implemented; visual
  acceptance still required. Existing level cutoffs remain the documented
  proposal, not an inferred operator decision.
- Textual lesson/result migration: needs scope confirmation; dashboard is
  already Textual. No unapproved popup-library rewrite was introduced.
- GitHub feedback: local capture works; issue/discussion target and auth
  remain unspecified, and no external publication was made.
- Signatures: metadata credits preserved; no unapproved restoration in art.
- Foreign demo commits: neither file changed or committed. This request did
  not authorize any commit/push.

Shift-JIS: Vim and Neovim both pass strict Shift-JIS/CP932 byte round trips.
M10 remains a Unicode/scoped-edit exercise. The corpus and Saitamaar font
identity/metrics are already pinned, but strict import/export, whitespace
preservation and actual proportional-metric preview/visual acceptance are
not connected as an end-to-end tutor workflow (VD-68/VD-71). Terminal cell
equality is not evidence of proportional joins.

## 9. Independent review and remaining work (2026-10-01) — READ THIS FIRST

Supersedes the status claims in §6 and §8. Claude re-ran the suite and checked
each §6 item against source (FAILURE_LOG VD-79).

This is the review snapshot. §10 records the executed §9.3/§9.4 checkpoint.

### 9.1 Tree state

- HEAD `20d9c70`, which equalled `origin/main` at the last fetch. The network
  was offline on 10-01.
- **All VD-64…VD-78 work is UNCOMMITTED:** 27 modified and 9 new files, about
  +11.7k/−2.0k lines.
  - New: `share/ui_style.py`, `share/avatar_options.py`,
    `share/questions-authored-v2-pedagogy.json`, `share/test_runtime_ui.py`,
    `share/test_ui_style.py`, `share/test_encoding_support.py`,
    `share/test_tmux_quiz_popup.py`, `tmux/vim-drill-quiz.sh`.
  - omp's `share/demo_*.{py,json}` remain untracked and foreign.
- No commit has been authorized. **First decision: fix 9.3 and 9.4, then
  commit (recommended), or commit as-is?**

### 9.2 Re-run by Claude on this exact tree (2026-10-01): all PASS

- `test_v2`: 248/248 lessons, 207/207 primary recipes.
- `test_question_quality`: 428.
- Also passing: feedback, deck (+ headed 80x24 warm-up), dashboard Pilot,
  viewer, runtime_ui, ui_style, encoding_support, stone_story_variants and
  provenance, drills 46, setup_check, animation_lesson_pack,
  animation_curriculum_integration.
- Headed 80x24: `test_tmux_v2`, `test_tmux_quiz_popup` (Prefix+Q),
  `test_tmux_v2_routes` (28 routes).
- No orphaned `nvim --embed` afterwards.
- NOT re-run: 100x36 and 188x49 matrices (Codex claim, VD-77).

### 9.3 New regression: fix before commit

`gen_curriculum_v2.py` (~6759-6770) blindly rewrites learner text: "address" →
"scope marker", "addresses" → "scopes", "ex" → "command-line". This produces
broken English.

- Verified: 4 card title/prompt/hint fields and 30 questions. A broader
  subagent scan counted 56 card fields and 177 question hits.
- Examples:
  - M0.SR "scope marker one row and substitute";
  - M0.SR hint "Read :2s/o/O/g as scope marker + command…";
  - M11.VE "scope marker an empty registered column";
  - "read an command-line substitute".
- `v2_keys.py` symbol alerts (~757-782) still say "line address".
- Fix: remove the regex. Hand-write each string in plain English ("pick one
  row", "the line range", "a `:` command").
- Add a quality-gate rule that rejects "scope marker", "an command-line" and
  "Ex"/"address" in learner text.

### 9.4 Operator feedback 2026-09-30 16:00, M0.01 "lesson has errors/mismatches": only partly fixed

- **Fixed:** the recipe/gate mismatch (recipe `j f* ro` vs gate `j0f*ro`; the
  row is now `j0`).
- **Verified open:** the hint says "Start with 0 at column 1…" with no `j`.
  Rewrite it as `j0` → `f*` → `ro`.
- **Verified open:** `key_vocabulary` cites `/pattern<CR>`, which the lesson
  never uses.
- **Reported by the subagent, verify:** the M0.01.P01 BEFORE/AFTER boxes are
  ragged (row 2 is 8 cells, rows 1 and 3 are 7), so the right `│` borders
  don't align. Pad the art rows inside the box renderer.
- **Reported by the subagent, verify:** the first edit raises ★NEW 3 (`0`,
  `f{char}`, `r{char}`), against one-idea-per-step.
- **Decide:** should `jf*ro` (no `0`) count as a declared alternative?

### 9.5 PARTIAL items (the §8 closeout overstated them)

1. **M4.DIFF.** Bridges were added, but its own recipe is unchanged (5 rows,
   about 10 commands) and still raises ★NEW 3 (`:silent`, `dd`,
   `:set scrollbind`).
2. **M11.VE.** Split, but hit by the 9.3 wording regression.
3. **M13.BE** still raises ★NEW 2 (`2W`, `B`). Hidden M13.04 is the first
   counted `B`.
4. **Ordering.**
   - Hidden M16.04 comes before guided M16.INC, so `2<C-a>` is first required
     on a hidden card.
   - M15.MAC3 comes before M15.MAC: recording and counted replay are
     introduced together.
5. **Hint template.** 112 cards still use the generic "Vim toolbox" template.
   It names unused tools on M12.05, M10.05, M15.06, M4.08 and M17.02.
6. **Missing teach/example entry:** `:[range]d` has none.
7. **Placeholder:** M15.08's review variant still shows `qq ... q / 3@q`.
8. **Minor:** hidden M2.08 (`10G`) is the first card where `0` appears inside
   a count.
9. **M11.GM** introduces `g-` and `g+` together. Split it, or accept the pair
   as one idea.
10. **Static `--tree` 🔥** shows at streak ≥3, while the dashboard glows on a
    best streak. Pick one rule.
11. **M11.TR "art offset"** has never been reproduced. Ask the operator for a
    screenshot or a repro.

### 9.6 Operator decisions and visual acceptance

- **Commit/push authorization** for the VD-64…78 batch.
- **Avatars.** There are 15 candidates (`python3 share/avatar_options.py`).
  The reviewer notes they are still small stick figures much like the rejected
  ones. Expect a redesign before asking for a pick.
- **Gemini band** (implemented in `share/ui_style.py`). The operator has not
  seen it.
- **Level tier cut-offs** (4/8/12).
- **Textual for lesson/result screens**, or the dashboard only.
- **"Post feedback to GitHub?":** target and auth.
- **Stripped signatures** (jgs/pb/tre): restore them in the art, or keep the
  metadata credit only.
- **omp's demo files:** commit, or leave untracked.

### 9.7 Not started / larger design

- **Proportional Shift_JIS workflow.** Byte round-trips are proven
  (VD-64/68/71). Still missing:
  - strict import/export plus whitespace preservation in the tutor flow;
  - a real Saitamaar-metric preview before submit;
  - visual-join acceptance distinct from text equality.
  The preview surface (browser, Textual, or PNG) is undecided.
- **Re-run the 100x36 and 188x49 headed matrices** after the 9.3/9.4 text
  fixes. Text changes invalidate the earlier captures.

### 9.8 Order for the next agent

1. Fix 9.3: hand-written English plus a gate rule.
2. Fix 9.4: M0.01 hint, vocabulary, boxes, NEW-3.
3. Regenerate. Run the full suite and the headed matrices at 80x24, 100x36
   and 188x49.
4. Ask the operator to authorize the commit; commit in hunks by lane.
5. Work through 9.5.
6. Bring the 9.6 visual items to the operator as one review session.

## 10. Execution receipt — 2026-10-01, VD-80

```text
Goal: execute §9.3/§9.4, verify the final source, then request commit authorization.
Repository: /Users/r/Projects/daily-neovim-ascii-art-tutor
HEAD: 20d9c70. All implementation remains uncommitted.

Requirement | Source | Implemented in source | Observed correct | Open reason | Evidence stage
Plain learner wording | share/audits/HANDOFF_CODEX_2026-09-30.md:294 | share/learner_text.py:4; authored banks and generator corrected without runtime rewriting | quality gate passes 430 questions with 12 rejection controls | none for the scoped wording repair | source + headless
One idea per first edit | share/audits/HANDOFF_CODEX_2026-09-30.md:313 | share/gen_curriculum_v2.py:4792; M0.L0 and M0.F0 precede M0.01; each NEW 1 | 250 lessons/209 primary recipes and alternate jf*ro execute; aligned boxes; navigation and both first-edit paths pass all three sizes | none for the scoped first-edit repair | source + headless + headed
Final headed matrices | share/audits/HANDOFF_CODEX_2026-09-30.md:384 | share/test_tmux_v2.py; share/test_tmux_v2_routes.py:656 | all chains exit 0: automatic popup, Prefix+Q, deck/warm-up and 31/31 routes at each of 80x24/100x36/188x49 | none | headed, real user configuration
Commit checkpoint | share/audits/HANDOFF_CODEX_2026-09-30.md:386 | no commit/push attempted | HEAD still 20d9c70; foreign demo hashes unchanged | operator authorization required | operator-open

Removed code: _LEARNER_REWRITES, _clean_learner_value, clean_learner_question,
clean_learner_card and their field tables/call sites. No source art was deleted.

Completed steps: direct prose corrections; read-only rejection gate; M0.01 hint,
vocabulary and eight-cell boxes; navigation prerequisites; declared no-0 path;
regeneration; full suite and three final headed matrices. Rendered briefs honor authored vocabulary and
the first-edit shape. Variant selection clears stale primary vocabulary/shape.

Next step: ask the operator for commit authorization. Do not begin §9.5 before
that checkpoint. §9.5 partial backlog and §9.6/§9.7 decisions remain open.

Visible acceptance: each first-step lab shows NEW 1; source accents do not move;
M0.01 accepts j0f*ro and jf*ro; P01 borders align; real hook and Prefix+Q workflows
hold and close correctly at 80x24, 100x36 and 188x49 with real Neovim configuration.

Falsifiers: any rejection fixture passes; raw/generated curricula drift; a
navigation path moves/edit changes art unexpectedly; ro alone gains credit;
generic unused search wording returns; any final matrix exits nonzero.

Forbidden: commit or push without operator authorization; change foreign demo
files; change global tmux/Neovim settings; remove provenance; claim §9.5–§9.7 done.
Evidence and production hashes: /Users/r/Projects/daily-neovim-ascii-art-tutor/FAILURE_LOG.md, VD-80.
```

## 11. Full continuation — current requirement/evidence boundary

```text
Goal: finish the authorized C01–C32 course continuation and its final verification.
Repository: /Users/r/Projects/daily-neovim-ascii-art-tutor
HEAD: 20d9c70; generated revision 2026-10-01.71; work remains uncommitted.
The operator's full-execution request supersedes §10's pause before §9.5.

Requirement | Source | Implemented in source | Observed correct | Open reason | Evidence stage
Saved wording/layout feedback | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:13; saved feedback.jsonl and share/demo_notes.json | authored banks; learner_text.py; v2_runtime.py | 471-question quality; saved-data row/box regressions | operator aesthetic choices are separate | source + headless
Full course/legacy parity | share/LEGACY_CURRICULUM_DISPOSITION.md; handoff §9.5 | generator .71, 17 guided/hidden pairs; operation-specific reviews | 291 cards/250 primary effects; 296 changed-art effects; 46 legacy IDs mapped | final real-config/matrix collection remains pending | clean Neovim + source
Correct result plus actual taught commands anywhere | operator C31; feedback.jsonl row 18 | share/method_policy.py:278; share/v2_runtime.py:3001; share/v2_runtime.py:3251 | ten focal-policy tests; seven actual gate grades; mode/register/prefix negatives | exhaustive Vim interpreter is not claimed | actual Neovim/gate PTY
Ordinary wq cursor receipt | operator C31/C15; adversarial R1 | bin/vim-daily-gate:850 | seven actual cursor controls, wide byte/display controls | none for exercised receipt boundary | actual PTY
History operation visible in final artifact | operator C31 | UT/UTH two-take comparison; generator:7928 | primary and both review variants execute; g-/g+ presence only | no animation claim for this comparison | actual clean Neovim
Reached multi-frame art reward | operator C32 | share/lesson_tui.py:98; share/lesson_tui.py:326; share/v2_runtime.py:186 | actual first M0.P0 grade/result from empty isolated state; distinct authored frames at all three sizes | reward source art is separate from learner output | actual result-page PTY
Textual lesson/result/retry | operator answer 10-01; saved Repeat note | lesson_tui.py; launcher-owned routes | actual three-size reward/failed Repeat/practice/Next/Watch/dashboard/feedback/Close | none for exercised routes | actual PTY
Ghostty native JIS/diffs | operator Ghostty selection; handoff §9.7 | share/sjis_terminal.py; strict byte/raster/registration owners | four production PNGs acknowledged by actual Ghostty 1.2.3 directly and through disposable tmux | live default passthrough off; human contour approval required | actual transport, not artistic acceptance
Avatar/visual/external choices | handoff §9.6 | original Lv3–7 options and local feedback | 15 candidates; foreign demo hashes unchanged | operator selection, level cut-offs, signatures and external target/auth | operator-open

Delete targets: none in the current closeout. Removed learner rewrite code is
recorded in §10. Preserve credited source art and unrelated worktree edits.

Ordered steps:
1. Read the current completion ledger and VD-81. Read saved notes, not screenshots.
2. Collect pending real-config and three non-native matrix receipts once the
   mandatory passive-poll interval expires. Do not count pending jobs as passes.
3. Run regressions after any source repair; require source/generated equality.
4. Update C25 with exact source identity and terminal receipts.
5. Report live tmux/human visual/operator choices explicitly. Request missing
   authority before a live configuration, commit or external write.

Visible acceptance: GP accepts g+ before the target edit; absent or Insert g+
shows TARGET CORRECT and instant retry. Alternate dw/comparison positioning
passes. Visual u/ranged Visual :earlier do not gain Normal history credit.
M0.P0's successful default result panel shows at least two different art frames
at 80x24/100x36/188x49. Ghostty shows native BEFORE/YOURS/TARGET/DIFF while editable
text stays canonical. All 46 eligible reward cards/counts are in the ledger.

Falsifiers: correct target plus actual taught command rejected for extra/order;
Insert/Visual impostor credited; wq receipt lost; repeat advances/awards twice;
first reward remains a still; any recipe/review target wrong; stale/undisplayed
native image gains credit; equal pixels erase whitespace errors; foreign hash changes.

Forbidden: Git LFS; commit/push without authorization; mutate live learner state;
change global tmux/Neovim settings; edit foreign demo files; select an avatar;
publish feedback; call source/test/ACK evidence human visual approval; claim the
learner completed the course; label source reward art the learner's animation.
```

## 12. Operator addendum 2 — 2026-10-01 22:06 (C33, C34) — HIGHER PRIORITY than remaining C-items

Recorded by Claude at the operator's explicit request ("APPEND IT NOW"). Add C33
and C34 to `share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md` and record the
intake in `FAILURE_LOG.md` (check the max VD id first). No commit/push is authorized.

### C33 — invented "!" takes in credited art are rejected

Operator pasted `(_!,o)` (Skully with a `!` eye): "what is this bs".

- Source: `share/gen_curriculum_v2.py` ~7175–7230. M11.BR/GM/GP/ER/UB/UT/UTH insert
  an invented `!` into official Stone Story frames (Skully eye, Frog eye, missile
  exhaust, Chick crack) as an "exaggerated take". M11.GM's TARGET is the defaced
  frame, so it is saved as the learner's work and replayed in the gallery. The
  committed HEAD curriculum already carries `_!,o` in 6 places.
- Required: every undo-branch "take" is a real source frame of the same character
  (e.g. Frog res01 open vs res05 blink; Skully idle vs look; Chick egg F3 vs F4),
  or an original authored frame labelled as such. No invented glyphs inside
  credited art. No card target may be a non-source frame.
- Gate: every card target and every learner-visible recipe intermediate equals a
  source-backed frame or a labelled authored original. Negative control: the
  current `(_!,o)` target must fail the gate.
- Do NOT rewrite the operator's saved M11 project files that contain `!`; only
  stop producing new ones.

### C34 — real animation content (not only a player)

The operator has passed 31 lessons (15 M0, 16 M11) and has seen no animation
beyond 2-frame flips. Measured on `curriculum-v2.json` revision `2026-10-01.71`
(Claude, 21:22 and 22:06): 195/291 lessons are single stills; frames per lesson
2:45, 3:25, 4:17, 5:8, 6:1; M11 max 2 frames; M0 is one drawing (Fireworks).
`share/module_native_playback.py` requires ≥8 frames, but no content feeds it and
no learner-reachable route calls it.

- Each module gets one authored or credited animation of ≥8 frames (walk cycle,
  bounce, egg hatch — the Stone Story Pets/Chick sources already have frame sets;
  credit as usual). Lessons build its frames; the full sequence plays on module
  completion and in the dashboard gallery.
- Retro-fit M0 and M11 first. The operator already finished them: award their
  module animations on the next launch from existing progress (read-only on the
  real state; no seeded passes).
- Proof: a real gate run from a COPY of the operator's current progress state
  showing the ≥8-frame playback in the monospace viewer at 80x24/100x36/188x49.
  The Kitty/native path does not count until a real Ghostty run is observed.
- Falsifiers: module completion still shows ≤2 frames; gallery lacks the module
  animation; any frame not source-backed or labelled authored; real state mutated.

## 13. Executable final-source handoff — 2026-10-02, VD-82

```text
Goal: Preserve the completed scoped engineering snapshot and resolve only authorized operator choices.
Repository: /Users/r/Projects/daily-neovim-ascii-art-tutor
HEAD: 20d9c70d3b79373261b7352ae5796d46f5e34a34
Installed curriculum: 2026-10-02.77; 311 cards, 491 questions.
This is a dirty, uncommitted worktree. Course-source completion is not learner mastery.
Final runtime SHA-256: d27b95b1876a71cc06076f9eb9aff82611605344c886f307a701d5e509c8e5c7
Final gate SHA-256: e015fa2206fff9533132ff1af518d5d18fd48f26c25c064bc1bd46bb86527659

Requirement | Source | Current boundary
C01 plain wording | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:15 | 491-question gate passes
C02 first-edit prerequisites | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:16 | actual navigation controls pass
C03 separate DIFF concepts | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:17 | source/order/effect controls pass
C04 virtualedit one-idea lesson | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:18 | authored prerequisite and hint
C05 counted WORD/backward bridge | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:19 | source/order/effect controls pass
C06 counted increment bridge | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:20 | source/order/effect controls pass
C07 macro recording before replay | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:21 | source/order/effect controls pass
C08 operation-specific hints | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:22 | scoped hint gate passes
C09 inclusive range-delete teaching | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:23 | source gate passes
C10 executable macro recipe | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:24 | real recipe effects pass
C11 zero-inside-count bridge | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:25 | ordering and 10G teaching inspected
C12 separate history operations | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:26 | ten literal-source cards; actual routes pass
C13 streak treatment | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:27 | implementation tested; operator aesthetic approval remains
C14 saved-note row offsets | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:28 | TR/LS actual viewport checks at all three sizes
C15 ordinary :wq cursor receipt | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:29 | actual exit controls pass
C16 whitespace preservation | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:30 | strict text/native controls pass
C17 deletion-only diff | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:31 | source and negative controls pass
C18 byte/display columns | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:32 | wide cursor controls pass
C19 stable art rows | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:33 | source and paired-question border checks pass
C20 target-correct method retry | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:34 | real diagnostic and mode-negative routes pass
C21 strict Shift_JIS/CP932 bytes | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:35 | backend and lifecycle controls pass
C22 native Ghostty preview | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:36 | six actual .77 runs; human contour approval remains
C23 text versus artistic acceptance | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:37 | ACKs are not human contour acceptance
C24 avatar candidates | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:38 | original options present; operator selection remains
C25 final integration | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:39 | final frozen three-size matrices and broad effects pass
C26 Textual lesson/result routes | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:40 | actual three-size routes pass
C27 Repeat same lesson | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:41 | actual failed Repeat and credited practice pass
C28 truthful moving demonstration | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:42 | source motion separate from static studies
C29 M11.02 teaching critique | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:43 | changed target and source motion; operator preference remains
C30 legacy operation parity | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:44 | executable guided/hidden pairs and distinct reviews
C31 unordered atomic method presence | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:45 | fourteen actual controls pass; scoped independent final re-review complete
C32 reached moving result reward | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:46 | first M0.P0 actual grade reaches all eight frames
C33 literal source history poses | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:47 | no rejected (_!,o); ten-card source gate
C34 whole-module animation/catch-up | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:48 | 20 original eight-frame sequences; copied-state catch-up
C35 stable attempts/publication | share/audits/COURSE_COMPLETION_LEDGER_2026-10-01.md:49 | required locks, snapshots, revision and child acknowledgement

Delete targets: None. Preserve rejected old strips, checkpoints and unversioned events.

Ordered steps:
1. Read the current ledger and VD-82 before changing source. The final engineering
   matrix and scoped independent mode/receipt/recovery review are complete.
2. Read saved feedback before diagnosing a new learner report. Preserve its
   attempt contract, artifact and revision. Do not infer correctness from a screenshot.
3. Ask for the specific remaining operator decision before changing avatar selection,
   palette acceptance, level cut-offs, signature placement, M11.02 teaching preference
   or external feedback target/authentication. No decision is inferred from green tests.
4. If an authorized source change is made, rerun the tests for its affected boundary.
   The C31 regression is share/test_c31_real.py. It includes genuine block zy/zp,
   named-register Visual copy, ordinary r and wrong-mode/exploit negatives.
5. A runtime change requires fresh frozen three-size matrices. The final baseline
   is 90 non-native, 30 history, 57 non-native endcap, six saved-offset and 24
   changed-card routes. Pair native exclusions with six actual Ghostty M10.06/
   M10.REWARD runs. Do not relabel the current receipts with a changed source hash.
6. Publish curriculum changes only through share/curriculum_publish.py with both
   required operator locks available. Preserve old strips and unversioned events.
7. Commit or push only after explicit authorization. Preserve unrelated dirty files.

Visible acceptance:
- A correct target with the actual taught command in its real mode passes,
  regardless of extra, reordered or undone exploratory commands.
- Insert text containing ddp does not earn Normal dd/p credit.
- A correct target without taught-command evidence says TARGET CORRECT and
  shows used commands green, missing commands red, with instant retry.
- Literal Skully/Frog/Chick/SnowBunny source poses replace invented history takes.
- M0.P0's first passing result plays the whole eight-frame module sequence.
- Ghostty shows native Saitamaar BEFORE/YOURS/TARGET/pixel-diff panels and
  all eight result frames. Editable Neovim text remains on its terminal grid.
- TR/LS question boxes keep stable visible border columns at all three sizes.
- Real learner-state files are read-only to tests. Copied progress supplies catch-up.

Falsifiers:
- The :startinsert exploit passes, or missing typed schema earns method credit.
- Literal invalid dp is accepted as a put, or exact recipe order is required.
- A rejected (_!,o) source target returns, or a source intermediate is invented.
- A passing result still offers only one/two frames as the whole-module reward.
- Native ACKs are called artistic acceptance, or nested tmux is called Ghostty proof.
- A pending/failed/mixed-source matrix is described as final passing evidence.
- Live curriculum publication occurs while either required session lock is held.

Forbidden actions:
- No commit, push, Git LFS, global tmux/font/config change or foreign demo edits.
- No real progress seeding, old-event relabelling, saved-project overwrite or r! workaround.
- No screenshot dependency for saved notes, text grading or row-offset evidence.
- No current source hash may be attached to an older source snapshot's receipt.
```
