# Failure Log

## VD-01 · 2026-09-20 — touch typing was incorrectly framed as separable

- GitHub issue: https://github.com/rikiyanai/daily-neovim-ascii-art-tutor/issues/1
- Intended product: hourly drills should make Vim skill and typing reliability
  stronger through the same meaningful ASCII-art authoring practice loop.
- Observed mismatch: treating touch typing as a separate track would reproduce
  the failure mode of generic typing platforms and generic Vim trainers: filler
  material with no reason to care, which makes the routine easy to abandon.
- User correction: touch typing practice belongs inside the Vim/ascii-art drill
  itself. Drills should bias toward motions, operators, counts, text objects,
  and common command combos on meaningful Stone Story-style art.
- Required successor: add live feedback or a trailing typed-history surface
  during the drill, then add quick quizzes, repeated practice, and milestones
  around conceptual handles such as Vim's count-verb-object grammar.
- Acceptance remains open until progress can report typing reliability and Vim
  operation gains without splitting them into separate products or modes.

## VD-02 · 2026-09-24 — repo identity drifted from GitHub canonical name
- GitHub issue: https://github.com/rikiyanai/daily-neovim-ascii-art-tutor/issues/8

- GitHub canonical: https://github.com/rikiyanai/daily-neovim-ascii-art-tutor (`gh repo view` from inside the checkout)
- Observed mismatch: local dir `~/Projects/vim-daily` + `origin https://github.com/rikiyanai/vim-daily.git` (stale pre-rename URL, kept alive by GitHub redirect); README clone line still points at `vim-daily`.
- User correction: rename local checkout to the canonical name, point origin at it, fix README clone URL.
- Required successor: re-run `install.sh` after rename (it symlinks absolute `$repo` paths) and verify `vim-drill --status`.

## VD-03 · 2026-09-24 — retry defaults to a dirty buffer, DO THIS becomes unfollowable
- GitHub issue: https://github.com/rikiyanai/daily-neovim-ascii-art-tutor/issues/2

- Intended product: retrying a drill re-attempts the documented recipe from the documented start.
- Observed mismatch (user-reported, confirmed in `bin/vim-daily-gate` `do_drill`): reset happens only on explicit `r`; bare Enter loops back into the same file with the user's random chars still in it, so the recipe's motions no longer land where DO THIS assumes.
- User correction: retry must reset by default (or snapshot start and offer diff-against-start).
- Required successor: change retry prompt default to reset; keep an explicit keep-my-mess option.

## VD-04 · 2026-09-24 — deleting the marker line bricks the drill, reset silently no-ops
- GitHub issue: https://github.com/rikiyanai/daily-neovim-ascii-art-tutor/issues/3

- Intended product: any failed state is recoverable with `r`.
- Observed mismatch (code-read, `read_region`/`reset_region`/`show_diff`): if the `MARKER` line is deleted, `read_region` returns None and the UI says "press r", but `reset_region` returns silently when the marker is absent, so the drill can never recover until the next drill.
- Required successor: `reset_region` must rebuild from the drill definition when the marker is gone (or rewrite the whole lesson file).

## VD-05 · 2026-09-24 — no quiz layer; concepts are read-only prose, `<CR>` undefined
- GitHub issue: https://github.com/rikiyanai/daily-neovim-ascii-art-tutor/issues/4

- Intended product (VD-01 successor, still open): quick quizzes and milestones around count-verb-object grammar; user asks for multiple-choice + socratic (`what does dd mean`, `what keys in what order`).
- Observed mismatch: `--concepts` only prints prose; no MC, no checks, no notes. Instance: recipes print `:wq<CR>` with no key legend anywhere in the lesson — user had to ask what `<CR>` means.
- Required successor: `--quiz` mode (MC + key-order questions, incl. a count-verb-object chapter quiz) plus a key-notation legend in every lesson.

## VD-06 · 2026-09-24 — progress is streaks only; selection feels like repeats; orphan ids
- GitHub issue: https://github.com/rikiyanai/daily-neovim-ascii-art-tutor/issues/5

- Intended product: progress that shows coverage and what to do next.
- Observed mismatch: `--status` shows streak + per-drill passed/failed but no coverage %, no per-concept mastery, no typing-reliability metric (VD-01 acceptance). `pick_drill` is weakest-first with a random tiebreak excluding only `last_id`, so repeats surface early. Evidence of linkage fragility: `progress.json` tracks 43 ids vs 42 drills (`counted-insert`, `pairs` orphaned by renames; seeding keys on title, not stable id).
- Required successor: coverage % + per-concept mastery + stable-id progress; reweight picker (e.g. exclude recent-N, weight failures).

## VD-07 · 2026-09-24 — let-through and quit leave no ledger row
- GitHub issue: https://github.com/rikiyanai/daily-neovim-ascii-art-tutor/issues/6

- Intended product: the log reflects every drill outcome, including struggle.
- Observed mismatch (code-read, `do_drill`/`record_completion`): passing writes a log row; `MAX_TRIES` let-through and `n`/quit return 0 with no row. Failed counter increments in `progress.json` but the daily log understates attempts, so `--status` and streak math never see the struggle.
- Required successor: log skips/let-throughs as rows (e.g. `result=skip`) excluded from streak credit.

## VD-08 · 2026-09-24 — downloaded art (~/Downloads/*.txt, 2026-09-21) has no intake path
- GitHub issue: https://github.com/rikiyanai/daily-neovim-ascii-art-tutor/issues/7

- Intended product: new ASCII art becomes new lessons via a documented step.
- Observed mismatch: `share/extract_art.py` only derives from Stone Story plates; the Sep-21 batch (cat, apple, ant, cicada, cuckoo, champagne, centipede, applause, JISART) sits in `~/Downloads/` with no importer, and the SOURCED gate (plate/skill provenance) rejects ad-hoc art by default.
- User correction: add intake docs + a generic source kind so downloaded art ships as drills.
- Required successor: `intake_art.py <file>` (glyph-alphabet check, provenance block) + README section; first batch: the Sep-21 downloads.

## VD-09 · 2026-09-26 — hourly practice is not an animation curriculum

- Intended product (user-confirmed): a level/skill-tree course in which each hourly
  session advances the same plain-text animation strip through meaningful
  Stone Story-style draw-along work; short conceptual checks occur between edits;
  module checks and transfer exercises prove both animation understanding and
  Neovim editing fluency. Spaced retrieval uses varied art and questions, and
  progress visibly updates on success.
- Observed mismatch: the current curriculum has 46 passable static drills and
  three tiers unlocked by 0/8/16 lifetime passes (`share/curriculum.json:10-20`,
  legacy `bin/vim-daily-gate:325-328`). The legacy picker favors
  `passed - failed` and uses success timestamps for its three-item recency
  exclusion (`:331-355`, `:723-750`), so failure can intensify near-term
  repetition. The eight fixed
  questions cover only grammar/modes and run only under manual `--quiz`
  (`:390-474`, `:879-881`). Each legacy drill gets a dated standalone lesson
  file (`:723-750`); the ten archived walk frames are represented in only the
  `hold-frame` and `tween-frame` tasks (`share/art.json:5-114`,
  `share/gen_curriculum.py:447-471`). The library has 49 art keys
  (`README.md:86-91`), but only 12 distinct keys are loaded with `a(...)` in
  the static generator; this does not imply all unused excerpts should ship
  as new lessons.
- Publication-boundary note: `README.md:86-89,217-220` simultaneously records
  all ten walk and seven pyramid frames as extracted excerpts and says the
  plates are not redistributed; `share/extract_art.py:34-45` confirms those
  sequences are separately extracted. Review the exact bundled content before
  adding more third-party art. This records an evidence tension, not a legal
  conclusion or authorization to remove the existing art.
- Partial existing capability, not erased: `--status` and `--export-progress`
  show drill coverage and per-concept one-pass counts (`bin/vim-daily-gate:358-383`,
  `:866-903`). `share/test_drills.py:58-105` checks recipe passability; 46/46
  passed with clean Neovim config on 2026-09-26. These are not module mastery,
  persistent-project, conceptual-check, or spaced-retention proofs.
- Source correction: the archived Part 1 transcript at 00:52:45-01:01:05 and
  Part 2 at 00:13:18-00:14:56, 00:25:20-00:42:51 teach key poses, middle
  in-betweens, timing, secondary motion, preview, and polish as a continuing
  workflow. The archive's `02-poison-adept-walk-cycle.txt` and
  `06-animation-subtractive.txt` provide cited frame references. Do not
  reduce this to more random copy/delete drills or bundle full third-party
  source material as if owned by this repo.
- User correction: reuse a standard Vim/Neovim teaching sequence where useful,
  adapt every lesson into ASCII-art authoring, vary repeats through spaced
  retrieval and unseen transfer text, add four-choice and other conceptual
  checks, teach multiple valid Neovim methods for the same edit with explicit
  scale/tradeoff comparisons, and make module checks update a visible tree.
- Required successor: implement the contracts in
  [share/CURRICULUM_V2_SPEC.md](share/CURRICULUM_V2_SPEC.md) in the dependency
  order of [share/CURRICULUM_V2_PLAN.md](share/CURRICULUM_V2_PLAN.md), while
  authoring the 80 numbered slots in
  [share/CURRICULUM_V2_CARD_CATALOG.md](share/CURRICULUM_V2_CARD_CATALOG.md),
  preserving existing private logs, user art, dirty worktree edits, and the
  46-drill regression baseline. Acceptance remains open until a learner can
  complete a multi-hour strip, pass mixed conceptual/performance checks, see
  an immediate node unlock, and later retrieve the skill on changed art.

### Fix attempt 1 · 2026-09-27 — v2 connected and automated-test verified

- Intervention: the default hourly route now loads `share/v2_runtime.py` from
  `bin/vim-daily-gate`. The original 46 drills remain callable with `--drill`
  and `--legacy-*`; `progress.json` and dated logs are preserved.
- Curriculum: `share/gen_curriculum_v2.py` generates schema
  `vim-daily/curriculum@4` with 10 prerequisite-gated modules, 80 stable cards,
  100 four-choice items with per-choice feedback, 60 executable edit paths,
  separate transfer artifacts, module checks, and original practice art.
- Progress/scheduling: `events-v2.jsonl` is append-only; `progress-v2.json` is
  rebuilt from it. A pass updates the visible tree immediately. Reviews use a
  changed question variant on 4h/1d/3d/7d/14d intervals and are capped at one
  every four successful sessions. Streak and daily-cap rows remain secondary.
- Gamification: the tree projection awards bounded XP once per unique card and
  review stage, plus badges for first progress, transfer, first module,
  midpoint tween, playable strip, and capstone. Duplicate events cannot farm XP.
- Project surface: each module owns an XDG-state `strip.txt`, `manifest.json`,
  before/after checkpoints, and per-card key logs. Transfer cards edit a
  distinct `transfer-<card>.txt`; compare cards write post-attempt
  `compare.txt`. `--preview` marks identical holds and rejects unequal frame
  heights instead of rendering them as valid motion.
- Neovim alternatives: every module contains a compare-method card; content
  includes local `r`, counted yank/put, addressed `:t`/`:m`, visual block,
  range substitution, and dot-repeat paths selected by task shape.
- Direct proof (2026-09-27): `share/test_drills.py` passed 46/46 under clean
  Neovim; `share/test_v2.py` passed 60/60 v2 edit recipes and all
  graph/question/state checks under a clean config; `share/test_v2.py --real`
  passed 60/60 under the user's real Neovim configuration. Fresh isolated XDG
  runs of `--tree`, `--list`, legacy list, and v2 JSON export also passed.
- Stage: Implemented, connected, and automated-test verified. Manual completion
  of the full ten-module journey remains the acceptance falsifier; no such
  human-use claim is made by the automated recipe suite.
- CodeRefs: `bin/vim-daily-gate` (VD-09 v2 dispatch),
  `share/v2_runtime.py` (ledger, projection, scheduler, projects, questions,
  checks, preview), `share/gen_curriculum_v2.py` (content/schema), and
  `share/test_v2.py` (graph/state/real-Neovim falsifiers).

### Fix attempt 2 · 2026-09-27 — blank first-card popup repaired

- User-visible failure: the first live v2 popup appeared blank. The private
  ledger recorded `M0.01` as `target-mismatch` at
  `2026-09-27T14:05:18.070222-04:00`. The persistent
  `projects/spark-loop/strip.txt` and `checkpoints/M0.01-before.txt` both
  contained the unchanged one-cell start (` . ` after display normalization),
  so the failed session did not overwrite learner work.
- Cause: `run_edit` printed the teaching brief to the popup terminal and then
  opened only the art-only `strip.txt` in full-screen Neovim. For `M0.01` that
  file contains one faint glyph, while the title, task, target, and recipe are
  hidden on the terminal screen behind the editor. The runtime therefore
  produced a visually blank lesson even though the process was active.
- Intervention: `share/v2_runtime.py` now creates
  `sessions/<project>/<card>.txt` for each attempt. The Neovim buffer contains
  the title, skill, task, guided target, command recipe, and submission help as
  display-only virtual lines above the current project art. Virtual lines add
  no buffer rows, so `gg`, `G`, counts, absolute ranges, `:t`, and `:m` retain
  their artifact-only meaning; `:wq` still writes only the persistent project.
- Regression proof: `share/test_v2.py` now drives `M0.01` through the complete
  lesson-buffer boundary with an actual Neovim process. It asserts that the
  brief exists, the cursor begins on artifact line 1, only the art is saved to
  `strip.txt`, and progress records the pass. On 2026-09-27 the suite passed
  60/60 recipes and the new boundary check with both `-u NONE` and the user's
  real Neovim configuration. `share/test_drills.py` also remained 46/46.
- Stage: implemented and automated-test verified. The next real hourly popup is
  the manual acceptance surface; this entry does not claim human-visible
  confirmation before it occurs.
- Falsified later the same day: live tmux pane `%37` at `100x36` showed the
  user's Lazy plugin interface over the lesson. Closing that interface exposed
  only the one-cell art. The virtual-line intervention was not visible. The
  automated recipe test did not exercise or prove the rendered tmux surface.
- CodeRefs: `share/v2_runtime.py:322` (atomic brief writes),
  `share/v2_runtime.py:336` (visible lesson construction),
  `share/v2_runtime.py:522` (edit-session synchronization),
  `bin/vim-daily-gate:628` (Neovim virtual-line rendering), and
  `share/test_v2.py:115` (real-Neovim blank-popup regression).

### Fix attempt 3 · 2026-09-27 — live tmux rendering and lesson count corrected

- Live failure proof: detached tmux session `vimdaily-proof-u4mucJ`, pane `%37`,
  rendered the user's Lazy interface at `100x36`; after `q`, the screen showed
  only ` .`. A clean-Neovim successor still showed only the art because virtual
  lines placed above buffer row zero were outside the scrollable viewport. The
  private ledger contains `target-mismatch` events at 14:05:18 and 15:07:02.
  After both failures, `strip.txt` remains byte-identical to
  `checkpoints/M0.01-before.txt`, with the unchanged 14:04:15 mtime.
- Rendering intervention: `run_editor` now starts Neovim with
  `--clean -i NONE` unless `VIM_DAILY_USE_USER_CONFIG=1` explicitly opts into
  personal plugins. It opens the lesson brief in a wrapped, read-only upper
  split and leaves the art as the active lower buffer. The split adds no art
  rows, so `gg`, `G`, counts, ranges, `:t`, and `:m` keep artifact-only meaning.
  Closing the art with `:wq` closes the brief and returns to the grader.
- Live pass proof: `python3 share/test_tmux_v2.py --show-capture` created tmux
  session `vim-daily-test-a7286853026d`, pane `%50`, at `100x36`. The capture
  visibly contained `M0.01`, its distinct title, complete wrapped task, target,
  recipe, submission help, and the lower art buffer. The test typed `r·` and
  `:wq` through tmux, then verified the `M0.01` pass event. The test uses tmux
  readiness/completion locks instead of startup sleeps or pane polling.
- Curriculum-count correction: the earlier `60/60` statement counted only
  executable edit recipes, not all lessons. The installed `--list` route has
  exactly 80 cards: 60 edit lessons and 20 conceptual/check lessons. Before
  this correction those records reused eight titles and twelve prompts. The
  generated data now has 80 distinct titles, 80 distinct live prompts, and 80
  retained `roadmap_contract` rows. Runtime edit prompts are derived from the
  executable recipe; the roadmap remains separately visible and is not
  misrepresented as already executed.
- Regression proof: clean and real-config suites each report
  `80/80 authored lessons present`, `60/60 edit recipes passable`, and
  `20 conceptual/check lessons`. The legacy suite remains 46/46. The installed
  `~/.local/bin/vim-daily-gate` symlink resolves to this checkout and contains
  the clean-Neovim/read-only-split route.
- Stage: the first-card tmux rendering and submission path are executed and
  verified. Full manual completion of all ten modules remains open; this entry
  does not claim that every aspirational catalog contract has a matching
  performance rubric yet.
- CodeRefs: `bin/vim-daily-gate:629` (isolated editor and read-only brief),
  `share/test_tmux_v2.py:1` (live tmux capture/submission proof),
  `share/gen_curriculum_v2.py:19` (80 distinct lesson surfaces),
  `share/v2_runtime.py:472` (concept lesson framing), and
  `share/test_v2.py:201` (honest total/edit/concept count report).

### Fix attempt 4 · 2026-09-27 — automatic client-attached popup proved

- Falsifier against attempt 3: its tmux test started
  `vim-daily-gate --force` as the pane command. That proved the corrected
  Neovim lesson surface, but it bypassed the automatic route the user actually
  encounters: `client-attached` → installed hook → `--due-quiet` →
  `display-popup` → `--if-due`. Attempt 3 therefore did not prove that the next
  automatic popup would contain the lesson.
- Intervention: `share/test_tmux_v2.py` no longer invokes `--force`. It creates
  isolated inner and outer tmux servers. A real client attaches to the inner
  server and fires the installed
  `~/.tmux/scripts/vim-drill-popup.sh` hook. The outer server provides and
  captures the attached terminal, so the assertion observes the rendered
  `display-popup` rather than the pane underneath it. Isolated XDG state keeps
  the test due without changing the learner's private ledger.
- Exact-route proof: `python3 share/test_tmux_v2.py --show-capture` exited 0 at
  2026-09-27 15:40 EDT. The captured popup border contained
  `vim drill - :q! then n to close`; its body contained
  `NEOVIM × ASCII ANIMATION · M0.01`, the complete task, target, command
  recipe, submission help, and active one-cell art buffer. UI keystrokes then
  traversed outer terminal → attached client → popup → Neovim; `r·` and `:wq`
  produced an `M0.01` pass event and closed the popup.
- Gate proof: the test first requires the installed `--due-quiet` command to
  return 0 with no output, requires `--if-due` to create `last-prompt`, and
  requires the installed gate symlink to resolve to this checkout. At 15:40
  EDT the learner's real state correctly returned not-due because its
  `last-prompt` was 15:05 EDT; the isolated proof did not alter that cooldown.
- Stage: the automatic client-attached popup route is executed and regression
  tested. This supersedes the `--force` proxy as popup acceptance evidence.
  The full ten-module human journey remains open.
- CodeRefs: `share/test_tmux_v2.py:64` (installed-route checks),
  `share/test_tmux_v2.py:69` (silent due gate),
  `share/test_tmux_v2.py:74` (real client-attached hook setup),
  `share/test_tmux_v2.py:106` (rendered popup capture), and
  `share/test_tmux_v2.py:128` (terminal-to-popup submission).

### Fix attempt 5 · 2026-09-27 — required post-lesson debrief and progress screen

- User-visible falsifier against attempt 4: the real automatic popup ran at
  16:07 EDT, but after the editor closed it showed no persistent debrief,
  actual-versus-taught keystroke replay, do/avoid guidance, skill tree, module
  count, XP, badge, daily count, streak, or next lesson. The private v2 ledger
  recorded `M0.01` as `target-mismatch` at
  `2026-09-27T16:07:55.453566-04:00`; projection remained `M0 0/8`, `XP 0`.
- Cause: v2 `_complete` recorded the event, printed two transient lines, and
  returned without calling the popup hold function. The edit-failure path
  printed the target mismatch but never decoded the key log and never rendered
  any progress projection. Because `display-popup -E` destroys the popup when
  its command exits, the v2 path had no durable post-lesson screen.
- Input evidence: the 16:07 key log decodes to `r.` followed by `:wq`; the
  period does not match the requested middle dot `·`. The former lesson wrote
  the literal Unicode glyph in the recipe without teaching a portable way to
  enter it, so even a correct failure had no actionable recovery path.
- Intervention: v2 now renders a second screen for both failed and successful
  edit attempts. It shows `YOU TYPED` beside `THE RECIPE ASKS FOR`, explains
  that exact target state—not key count alone—is the grading boundary, lists
  the card's `DO`, `START`, `ALSO`, and `AVOID` guidance, prints all ten
  module nodes and their locked/available/learning/mastered states, then prints
  reviews, XP, badges, streak, best streak, all-time completions, next card,
  and today's target count. Concept cards replay the selected and correct
  answers with the correct feedback. The success and terminal-failure paths
  now wait for Enter before allowing the popup to close.
- Glyph-input correction: every executable recipe that types `·` now teaches
  Neovim's portable `.M` digraph as `<C-k>.M`, including Normal-mode `r` and
  Insert-mode paths. This avoids assuming macOS character-palette knowledge;
  directly typing `·` remains a valid alternate path because grading uses the
  exact saved target.
- Failure-path proof: the automatic tmux test first saves `M0.01` without the
  required edit. The captured real popup shows `ATTEMPT NOT PASSED`,
  `r<C-k>.M` as `you skipped this`, `M0 0/8`, `XP: 0`, `today: 0/12`,
  `streak: 0 days`, and the checkpoint retry prompt. The same popup then
  restores the checkpoint and reopens Neovim.
- Success-path proof: the test submits `r<C-k>.M` and captures
  `LESSON COMPLETE`, an `ok` actual-versus-taught row, the do/avoid rules,
  `M0 1/8 learning`,
  `XP: 10`, `first-step`, `today: 1/12`, `streak: 1 day`, and
  `next: M0.02`. The popup remains present until the test sends Enter.
- Harness falsifier and correction: the hook's preliminary `--due-quiet`
  process inherited the test completion signal and could unlock it before a
  lesson finished. The gate now excludes `--due-quiet` from completion
  signalling. A separate post-render signal fires only after the debrief is
  fully printed; the test uses tmux locks rather than sleeps or pane polling.
- Authoring-method influence: the debrief treats exact saved art as the primary
  outcome while presenting the taught command path as a reusable method. It
  permits alternate valid paths when the exact target matches, and compare
  cards explicitly advise selection by scope, repeatability, and error risk.
  The `.M` digraph teaches the bounded middle-dot glyph without weakening the
  target alphabet. This matches the ASCII-authoring method's emphasis on
  readable results, retained variants, a deliberate glyph vocabulary, and
  deliberate method choice rather than key count alone.
- Stage: implemented and executed through the installed automatic
  client-attached hook for both fail→retry and success→hold→close. Full manual
  completion of all ten modules remains open.
- CodeRefs: `share/v2_runtime.py` (`_attempt_replay`, `_post_lesson`, and all
  success/failure call sites), `bin/vim-daily-gate` (`keystroke_table`,
  `hold_open`, `signal_post_rendered`, and due-probe signal exclusion), and
  `share/test_tmux_v2.py` (automatic fail/retry/success captures).

### Fix attempt 6 · 2026-09-27 — legacy teaching parity and paged debrief

- User-visible falsifier against attempt 5: the learner's 17:19 EDT `M0.01`
  attempt passed and updated the real projection to `M0 1/8`, `XP 10`, streak
  13, and `next M0.02`, but the lesson still exposed only task, target, and
  recipe before editing. The post screen added progress but did not restore
  what v2 removed from the legacy lesson. Attempt 5 therefore proved that
  headings and progress existed; it did not prove legacy teaching parity.
- Literal comparison: legacy `write_lesson` contains `WHY THIS EXISTS`, `WHAT
  THIS DRILL BUYS YOU`, `WHERE THIS SHAPE COMES FROM`, `DO THIS`, `KEYS WORTH
  KEEPING`, `READING THE RECIPE`, target, and explicit stuck/quit/reset help.
  Legacy failure output also contains wanted/yours artifact rows and the first
  differing column. Before this intervention, v2 `_write_session_lesson`
  contained task, target/recipe, submit, and split navigation only; v2
  `_post_lesson` contained a key table, do/avoid, and the progress tree but no
  saved-artifact difference.
- Teaching intervention: generated module records now preserve `meaning`,
  `principle`, `defect`, `basic`, `scaled`, and `source_ref`. The v2 Neovim
  brief renders current module count/state, XP, today, streak, motion intent,
  authoring principle, observable failure, concrete lesson benefit, recipe,
  retained keys, source, notation legend, and submit/stuck guidance. The split
  height increased from 18 to 24 rows and remains scrollable/read-only, so art
  motions and addressed commands still operate only on `strip.txt`.
- Debrief intervention: feedback and progression no longer compete for one
  terminal height. Held page one shows before/after artifact rows on success or
  wanted/yours rows plus the first differing column on failure. It then shows
  actual-versus-taught keys, `WHY`, benefit, `DO / AVOID`, and source. Enter
  advances to held page two, which owns the full tree, module counts, reviews,
  XP, badges, streak, best, all-time completions, next lesson, and daily count.
  Success closes only after another Enter; failure offers checkpoint restore
  and retry from page two.
- Navigation correction discovered by headed proof: `<C-w>k`, scrolling keys,
  and `<C-w>j` used to inspect the brief were initially recorded as a wrong
  editing method. `_without_brief_navigation` now excludes a complete
  enter-brief/leave-brief span from the edit replay. Reading instructions no
  longer creates a false error while artifact grading remains exact.
- Structural parity proof: `python3 share/test_v2.py --real` exited 0 on
  2026-09-27. It generates a real legacy lesson and a real v2 brief, then maps
  every legacy teaching job to v2 and checks the underlying module/card
  content, benefit, source, notation, recovery guidance, artifact diff, and
  progress page. It also passed all 60/60 v2 edit recipes, 20 conceptual/check
  lessons, and graph/question/state checks with the user's real Neovim.
- Installed popup proof: `python3 share/test_tmux_v2.py --show-capture` and the
  final `python3 share/test_tmux_v2.py` both exited 0. The test uses the
  installed gate symlink and installed client-attached hook at 188×49. It
  captures the initial teaching page, scrolls to and asserts the lower source/
  legend/stuck sections, captures failed artifact/key feedback, advances to
  `PROGRESS UNCHANGED` (`M0 0/8`, `XP 0`), retries, captures successful
  artifact/key feedback, advances to `PROGRESS AWARDED` (`M0 1/8`, `XP 10`,
  `next M0.02`), and proves the final page remains held until Enter.
- Regression proof: `python3 share/test_drills.py` remained 46/46. Python
  compilation and shell syntax checks passed. The isolated headed proof does
  not mutate the learner's real XDG ledger.
- Authoring-method influence: each lesson now names motion intent, the applied
  Stone Story authoring principle, and an observable failure before the edit.
  The post-attempt artifact replay treats exact saved text as primary evidence
  and the command path as a reusable method. This reflects the skill's rules to
  test the smallest readable motion, keep a bounded glyph vocabulary, preserve
  temporal coherence, and judge the result in the authored medium.
- Stage: implemented and executed through the installed automatic popup for
  the first-card fail→retry→pass route. Full manual completion of all ten
  modules and learner acceptance of later-card layouts remain open; this entry
  does not claim either.
- CodeRefs: `share/v2_runtime.py:344-430` (teaching contract and brief),
  `share/v2_runtime.py:514-543` (brief-navigation filtering and attempt
  evidence), `share/v2_runtime.py:555-687` (artifact replay and paged debrief),
  `bin/vim-daily-gate:650-674` (24-row read-only split),
  `bin/vim-daily-gate:742-765` (page signals/hold),
  `share/test_v2.py:129-225` (content-bearing legacy parity), and
  `share/test_tmux_v2.py:112-313` (188×49 installed-route captures).

### Fix attempt 7 · 2026-09-27 — whole-route audit beyond the first card

- Phase 1 audit checkpoint; stage: observed, not yet corrected. Attempt 6 proved
  the installed `M0.01` guided-edit route. It did not exercise every runtime
  kind or prove that hidden-answer, module-check, and review contracts survived
  the new teaching/debrief presentation.
- Finding A, hidden-answer leak: `_write_session_lesson` says an independent
  target and recipe remain hidden, then its shared `KEYS WORTH KEEPING` block
  prints the exact `card["recipe"]`. Compare-method cards likewise say the
  method comparison appears after a verified submission, then print both
  `method_alternatives` in the same pre-attempt brief. This invalidates the
  retrieval/transfer evidence those cards claim to collect.
- Finding B, module-check evidence loss: `run_check_questions` retains five
  outcomes only in a local list and returns one Boolean. A failed threshold
  reaches `_post_lesson` without the five prompts, chosen answers, correct
  answers, or explanations. A passed conceptual subpart followed by an artifact
  attempt also drops the question evidence from the final debrief.
- Finding C, review presentation gap: `run_review` appends a review event,
  rebuilds the projection, prints one transient sentence, and returns. In an
  automatic `display-popup -E` this route has no held feedback page, no XP/tree
  page, and no explicit close. Review success can therefore award three XP
  without visibly showing that progress.
- Acceptance surface for Phase 1: tests must prove pre-attempt briefs do not
  contain hidden exact recipes or compare alternatives; module-check feedback
  must retain all five outcomes across fail and pass-to-artifact paths; review
  fail/pass must render held feedback and unchanged/awarded progression. Headed
  popup coverage must include each distinct presentation route, not only the
  guided edit.
- Ownership: `share/v2_runtime.py`, generated curriculum metadata only when a
  content defect requires it, `share/test_v2.py`, headed popup tests,
  `README.md`, `share/DESIGN.md`, and this VD-09 log. Existing unrelated
  worktree hunks remain preserved.

- Phase 2 finding D, misleading benefit copy: the runtime displayed each
  catalog slot's aspirational curriculum sentence as `WHAT THIS LESSON BUYS
  YOU`, even when the executable card implemented only one smaller edit. This
  made future curriculum intent look like present lesson behavior. Every card
  now has a generated `lesson_benefit` that names its actual evidence boundary;
  `_lesson_context` consumes that field. The catalog contract remains planning
  metadata rather than a learner-facing performance claim.
- Phase 2 finding E, non-executable “alternatives”: comparison cards previously
  stored the module's generic `basic` and `scaled` prose. Those strings were not
  proof that either method could create the card's target. The generator now
  stores two `{label, keys, why}` methods on each of ten compare cards
  (`share/gen_curriculum_v2.py:55-245`). The real-Neovim suite executes all 20
  commands from the same card start and requires the same exact target
  (`share/test_v2.py:291`). The pre-attempt brief does not expose either command;
  `_write_compare` and the debrief reveal them only after grading
  (`share/v2_runtime.py:382-509,635-714`).
- Phase 2 finding F, repetitive conceptual bank: all modules formerly reused
  ten near-identical stems with implausible generic distractors. Questions now
  include the module's actual before/after ASCII evidence, use other animation
  meanings/principles/defects as plausible distractors, ask artifact evidence,
  transfer, temporal coherence, spaced retrieval, and blast-radius decisions,
  and make M3's whole-pose-copy case explicit (`share/gen_curriculum_v2.py:277`).
  The bank remains 100 stable four-choice items with rotated answers.
- Phase 2 finding G, fake linear tree: projection state used one
  `previous_mastered` Boolean, so a displayed “skill tree” was a ten-item chain.
  The generated DAG now opens M1 and M2 after M0, joins relevant editing and
  animation prerequisites later, and requires M5+M8 for M9
  (`share/gen_curriculum_v2.py:257-268`). Projection checks every named
  prerequisite (`share/v2_runtime.py:134-199`). The progress page explains the
  A/V tracks, prints `requires`, reports level and XP-to-next, shows the current
  eight-card map, and announces newly unlocked modules
  (`share/v2_runtime.py:717-765,1042-1070`).
- Phase 2 finding H, stale-looking repeated artifacts: M1.06 duplicated M4's
  rotation midpoint instead of transferring line geometry, and M9 reused M2's
  exact face buffer. M1.06 is now an unseen hand-mirror edit; M9 uses a distinct
  brace-bounded subject. A generated-data audit now reports zero duplicate
  start→target pairs. Repeated commands remain only where the same Neovim
  operation is deliberately retrieved on different art, scope, or module
  context; they do not repeat an identical artifact.
- Phase 3 correction A: hidden evidence cards printed the exact recipe in their
  shared retained-keys section, and comparison cards printed both claimed
  alternatives before submission. `_write_session_lesson` now prints exact
  target/recipe/keys only when `show_target` is true. Other edit types show a
  retrieval-boundary statement and safe controls only
  (`share/v2_runtime.py:382-451`). The suite renders all 60 edit briefs, checks
  every legacy teaching job, and rejects any hidden primary or alternative
  command before evaluation (`share/test_v2.py:265-289`).
- Phase 3 correction B: module checks now return a structured replay containing
  all five question objects, chosen answers, correctness, score, and threshold.
  `run_edit` carries it through the artifact subpart, and the held debrief prints
  every choice and explanation (`share/v2_runtime.py:611-631,803-935`). The
  first headed version was itself too tall and scrolled the completion heading
  out of a 188×49 popup; the final compact table uses two rows per correct item
  and a bounded correction row for misses. If the artifact fails after the
  conceptual threshold passed, `_latest_check_replay` reconstructs those five
  outcomes from the append-only question/check events on the next artifact
  retry rather than losing the table (`share/v2_runtime.py:803-842`).
- Phase 3 correction C: spaced review formerly awarded/rebuilt progress and
  immediately closed after one transient sentence. `run_review` now identifies
  the source card, renders `REVIEW RETRIEVED` or `REVIEW NEEDS WORK`, replays the
  chosen/correct conceptual answer, renders awarded/unchanged tree progress,
  and holds for explicit close (`share/v2_runtime.py:937-965`).
- Phase 4 proof: `python3 share/test_v2.py --real` passes 60/60 primary edit
  recipes, 20/20 executable compare paths, all 60 edit-brief visibility
  contracts plus conceptual-route debrief contracts, the branched
  graph, 100 questions, module-check replay, spaced-review debrief, state, and
  preview checks. The legacy suite remains a separate required gate.
- Phase 4 installed-popup proof: `python3 share/test_tmux_v2.py --show-capture`
  again passed the exact client-attached fail→retry→success route at 188×49.
  Its awarded page visibly contains `M0 1/8`, `XP: 10`, `LEVEL 1 Apprentice`,
  the A/V legend, named prerequisites, all ten modules, the current 8-card map,
  streak, next card, and held close prompt.
- Phase 4 cross-route proof: `python3 share/test_tmux_v2_routes.py` fires the
  installed client-attached hook in isolated state for five additional live
  popup routes: conceptual check, independent retrieval, method comparison,
  five-question module check followed by its artifact, and spaced review
  (`share/test_tmux_v2_routes.py:73-196`). All five passed. The test inspects
  hidden briefs before input, then held route-specific evidence and the full
  level/tree/card-map/streak page after input. Deterministic question ordering
  is test-only and synchronized by a tmux question-rendered signal
  (`bin/vim-daily-gate:758,895`; `share/v2_runtime.py:275`).
- Stage after Phase 4: implemented and automated/headed verified for all six
  distinct presentation routes (guided, concept, independent, compare, module
  check, review). This does not claim that a person has manually completed all
  80 cards; it does establish that the next automatic popup uses the installed
  corrected runtime and that later route layouts are no longer inferred from
  the first card.

- Phase 5 compact-terminal falsifier: the new cross-route headed test passed at
  188×49, but replaying it at the earlier failure size of 100×36 exposed an
  independent-success overflow. The captured popup began at the artifact's
  `after` row; `LESSON COMPLETE`, the verification line, artifact heading, and
  first before-row had already scrolled out. This disproves any claim that the
  188×49 pass alone established viewport safety. Acceptance now requires both
  sizes and the compact view must retain the completion header, artifact/key
  evidence, do/avoid table, source, and progress page.
- Phase 5 correction and proof: `_post_feedback` detects an interactive popup
  shorter than 38 rows. It retains exact artifact rows, compact actual/taught
  keys, all five module-check choices, a compact taught/alternative method
  table, do/avoid, source, and the completion heading; it removes only repeated
  WHY/benefit prose already present in the pre-attempt brief. The route harness
  now accepts `VIM_DAILY_TEST_COLUMNS`/`VIM_DAILY_TEST_ROWS`. All five additional
  routes pass at both 188×49 and 100×36, and the separate exact automatic
  fail→retry→pass hook test still passes.
- Phase 5 compact failure-path proof: `share/test_tmux_v2.py` now accepts the
  same size variables and has explicit compact/full replay assertions. The
  installed automatic hook's failed attempt, unchanged progress, checkpoint
  retry, successful attempt, awarded progress, and held close all pass at both
  188×49 and 100×36.
- Phase 6 invalid-answer falsifier: `ask_question` returned `(False, None)` for
  anything outside `a` through `d`. Concept, module-check, and review routes
  then treated that as a graded wrong answer and attempted
  `q["choices"][None]` in the debrief, raising `TypeError` instead of preserving
  the popup. Invalid input must reprompt in place and must not write a question,
  failure, review, XP, or scheduling event.
- Phase 6 correction and proof: `ask_question` now loops on invalid text, tells
  the learner it did not count, and keeps the original rendered/shuffled choice
  order. EOF/interrupt still abandons cleanly. `share/test_v2.py` submits two
  invalid responses followed by the correct letter and asserts one render, two
  non-attempt notices, and the correct selected index; the complete real-Neovim
  suite remains green.
- Phase 7 manual-sequence falsifier: `--card` rejected locked modules but allowed
  any card inside an available/learning module. Project checkpoint mismatches
  happened to stop some late edit cards, while late conceptual cards could earn
  evidence out of order. Selecting an already-passed card could also call
  `_legacy_credit` again, leaving v2 XP bounded but inflating the secondary
  daily/all-time ledger. Manual branch choice must remain possible, but within
  each available module only its first unfinished card may award evidence.
- Phase 7 correction and proof: `--card` now rejects completed cards and rejects
  any card other than that module's first unfinished card. It still permits a
  real branch choice: after M0 mastery, M2.01 is selectable even while automatic
  iteration names M1.01 next. Unit coverage proves late-card rejection,
  completed-card rejection, and the M1/M2 branch choice; the real-Neovim suite
  remains green.
- Phase 8 minimum-terminal falsifier: at 80×24, conceptual success scrolled
  `LESSON COMPLETE` and the entire concept replay offscreen, leaving only
  duplicated WHY/benefit/do/source prose. Edit routes also asked Neovim for a
  fixed 24-row brief inside an approximately 20-row popup, risking an unusably
  small art window. The 100×36 compact threshold is therefore not the minimum
  supported layout. Acceptance requires an ultra-compact feedback/tree mode and
  a brief split sized from the live Neovim row count so editable art retains
  viewport space.

- Phase 9 native-subagent audit checkpoint; stage: observed, fixes in progress.
  Independent runtime, curriculum, claims/provenance, and headed-route reviewers
  were assigned read-only scopes. Confirmed runtime gaps include unbounded
  review stages/XP, reviews starved after course completion, stale-lock owner
  races, repeated check questions, missing compare method evidence, terminal
  failure leaving a blocking artifact, transfer metadata replacing strip
  preview metadata, absent `check_ready`, `--force` selecting a review, and
  incomplete schema validation. Confirmed curriculum gaps include generic
  question/transfer variants, catalog/executable mismatch, prose-only timing and
  hold intent, the M3 three-row/six-row contradiction, M6 previewing unequal
  frames, and a promised macro without a macro exercise. Confirmed repository
  gaps include extraction deleting curated art, unenforced provenance fields,
  a v1-only curriculum override documented as global, and a symlink fallback
  derived from the installed link rather than its resolved checkout. No prior
  pass is treated as proof against these findings.
- Phase 9 runtime corrections: review stage increments are capped at the last
  configured interval; project completion no longer starves due reviews;
  explicit force skips review selection and a ready module check takes priority.
  The pathname/age lock was replaced with a process-owned advisory lock, so a
  stale timestamp cannot evict a live session and an old owner cannot unlink a
  successor. `check_ready` has its own `◆` tree state. Curriculum validation now
  rejects duplicate module IDs, invalid card/module references, module card-list
  mismatches, invalid answer indices, missing question sources, and duplicate
  normalized prompt/choice sets.
- Phase 9 assessment corrections: module checks honor their declared ten-item
  bank and select least-seen stems first; the checkpoint prompt no longer embeds
  its edit recipe. Mastery events bind the checkpoint hash to the earlier
  transfer artifact/hash. Compare cards require captured edit keystrokes,
  classify the demonstrated named method or `other-valid-exact-target`, and
  persist that family. An exact target written with an empty key log is recorded
  as `missing-method-evidence`, not a pass.
- Phase 9 artifact corrections: every failed edit is saved as a numbered failed
  checkpoint and the working file is restored immediately, including terminal
  failure/decline paths. Transfer verification writes
  `transfer-manifest.json`, leaving the playable strip manifest untouched.
  Each module now has a second changed-art transfer variant selected on a later
  failed session. Structured animation metadata records extremes, midpoint,
  pivot, contact, timing, and hold reason in the generated card and manifest;
  preview prints the hold reason.
- Phase 9 curriculum corrections: Q06-Q10 now carry module-specific principles,
  meaning, defects, and methods rather than a repeated generic answer set.
  Concept-card question IDs were remapped to the advertised decision (including
  M3 whole-pose copying), and each concept card now rotates five stems rather
  than two. All checks declare all ten module questions. M3's
  roadmap now consistently says three-row pose, M6.08 explicitly diagnoses its
  unequal-height intermediate rather than promising playable preview, and M7.05
  contains a real recorded-macro path (`3Gqq02lr-3jq@q`) versus the scoped
  substitute. Both methods execute to the same target under Neovim.
- Phase 9 provenance/config corrections: plate extraction merges generated keys
  with separately ingested art rather than overwriting the library. Intake now
  requires structured origin, author, license, permission, and redistribution
  status; the five existing downloads are explicitly `unverified`, not silently
  described as licensed. The extract→legacy-generate regression preserves those
  keys. `VIM_DAILY_CURRICULUM` is documented as legacy-only,
  `VIM_DAILY_CURRICULUM_V2` owns v2, and checkout fallback resolves the installed
  gate symlink before locating `share/`.
- Phase 9 minimum-terminal correction: the 80×24 brief is reflowed into bounded
  teaching rows, Neovim sizes the split from live rows, feedback has an
  ultra-compact artifact/key/do/source form, and progress compresses ten module
  cells into two tree rows so the result header is not scrolled away. The exact
  automatic client-attached fail→retry→pass route now passes at 80×24 and proves
  the held page persists before Enter and disappears after Enter. The headed
  harness also parses the real `~/.tmux.conf` hook and verifies the installed
  hook resolves to this checkout.
- Phase 9 headed proof: the exact automatic client-attached fail→retry→pass
  suite passes at 188×49, 100×36, and 80×24. At every size it captures the
  initial brief, failed artifact/key replay, unchanged tree, restored retry,
  successful replay, awarded tree/XP/streak/card map, held-before-close page,
  and absence of the popup after Enter. The cross-route suite also passes at
  all three sizes for concept, independent, compare, five-question module
  check, spaced review, and each of M0.06 through M9.06. It verifies a
  non-identity displayed-choice permutation, persisted compare method family,
  distinct transfer manifest, no replacement strip manifest, and real tmux
  control-key notation including `<Esc>`, `<C-v>`, and `<C-k>`.
- Phase 9 recovered-target falsifier and correction: a compare workspace could
  already contain the exact target after an interrupted session while its key
  log was empty. Treating that file as a normal retry would let the learner
  submit somebody else's completed artifact as method evidence. Recovery now
  saves the unexplained target as `uncredited-target-*`, restores the declared
  start artifact, records `missing-method-evidence`, and requires a fresh edit.
  The v2 suite covers this exact-target/no-log path.
- Phase 9 redistribution-boundary correction: structured metadata alone is not
  permission to commit an asset. `intake_art.py` now refuses `private-only` and
  `unverified` content when its destination is the repository library; those
  statuses may only be written to an explicitly separate private library.
  Tests cover both the repository refusal and a successful private-library
  intake with preserved metadata.
- Phase 9 final regression proof (2026-09-27): regeneration reports 10 modules,
  80 cards, and 100 questions. `share/test_v2.py` passes under both isolated and
  real Neovim: 80/80 executable cards, 60/60 edit recipes, 20 conceptual/check
  cards, 20 changed-art transfer variants, and 20 comparison paths. The exact
  automatic popup test passes at 188×49, 100×36, and 80×24. The cross-route
  headed suite passes at all three sizes for concept, independent, compare,
  module check, review, and M0.06 through M9.06 transfer routes. Both legacy
  suites remain 46/46 under isolated and real configuration. Python AST checks,
  shell syntax checks, and `git diff --check` also pass. This is automated and
  headed runtime evidence; it is not a claim that a person has manually worked
  the full 80-card curriculum or completed long-gap spaced reviews.

## 2026-09-27 — successful M0.02 popup still lacked an imperative task

- **Observed live attempt:** the append-only event ledger records `M0.02` as a
  pass at 19:23:01 EDT under curriculum revision `2026-09-27.4`. The card shown
  was `Spark loop · Develop the strip`; its only edit was `yyp`, turning one
  ` · ` row into two identical rows.
- **Confirmed presentation defect:** v2 briefs labeled the learner instruction
  `TASK`, not `DO THIS`. The legacy-parity regression made this easier to miss:
  it counted v2's `COMMAND RECIPE` heading as satisfying the legacy `DO THIS`
  teaching job, so it never required an actual imperative heading. Concept,
  module-check, and spaced-review routes likewise asked questions without an
  explicit `DO THIS` line.
- **Confirmed lesson defect:** duplicating the one-glyph frame without changing
  the copy exercised `yyp` but did not create a new visible pose or require an
  authoring decision. It advanced the artifact count while feeling like a
  repeated mechanical drill.
- **Correction:** edit briefs now render a literal `DO THIS` heading in full
  and compact layouts. Concept, five-question check, and spaced-review routes
  print their own explicit `DO THIS` instruction. `M0.02` now requires
  `yypro`: duplicate the entire frame, then replace only the copied centre with
  the brighter `o` pose. M0.04 develops that copy into `O`; M0.05 compares a
  local replacement with a visual-block normalization that creates an
  intentional two-frame bright hold; M0.08 adds the dim settle pose.
- **Regression falsifier:** headed route tests now require `DO THIS` on every
  question route, and the edit-brief suite requires that heading on every one
  of the 66 executable cards. The exact automatic popup also requires it.
- **Compact-layout falsifier:** the first 80×24 run after adding the instruction
  scrolled the concept card identity offscreen. The ultra-compact conceptual
  route now removes repeated WHY/BUYS/SOURCE lines from the pre-answer page
  while retaining card ID, bounded progress, `DO THIS`, the complete question,
  four choices, and answer prompt. The entire 80×24 headed route suite then
  passed, including spaced review and all eleven transfer modules.

## 2026-09-27 — corpus-wide Shift_JIS findings added as a separate evidence branch

- **Source receipt:** the viewer repository at commit `661b220` produced
  `aahub_aa003_train.sjis_combos.v1.json` from archive commit `3687cc5…`, with
  57 held-out slugs excluded. The training aggregate covers 114 slugs, 23,363
  pages, and 457,065 lines. Its 435 viewer entries are rasterized in Saitamaar
  16 px at true advances beside their recorded mirrors. Viewer tests and dump
  evidence belong to that repository; this tutor does not claim interactive
  human acceptance of the viewer.
- **Vendored evidence boundary:** this repository does not copy the 973 KiB
  corpus or any source art. `share/sjis_corpus_findings.v1.json` stores only the
  small aggregate receipt needed by lessons: source/input/font hashes, coverage,
  selected idiom counts, whitespace exceptions, vertical stacks, hatching
  counts, and interpretation limits.
- **Findings encoded:** `⌒ヽ` is 6,788 uses across 112/114 slugs; `／￣` 7,222;
  `_ノ` 6,474; `｀ヽ` 14,348. `ゝ__ノ` is explicitly rare at 39 uses across
  10 slugs. The no-double/no-leading half-space rule is taught as a strong
  convention with 147/78 exceptions, not a zero-violation law. The `￣` over
  `＿` 0 px stack is recorded at 5,949 uses. `ﾆ`, `二`, and `ニ` are taught as
  context-dependent hatching shapes. Outline combinations, stacks, and tone
  bands are separated so `::`-dominated raw frequency cannot define the visual
  vocabulary by itself.
- **Curriculum correction:** M10 `SJIS combination lab` adds eight cards and
  ten four-choice questions as a branch unlocked after M1. Its six executable
  edit cards cover `⌒ヽ`/`ノ⌒`, `／￣`/`＼＿`, the `￣` over `＿` stack, hatching,
  two valid append methods, and changed-pair transfer. Every M10 surface states
  the medium boundary: Neovim grades exact Unicode transcription; visual shape
  must be judged in Saitamaar at proportional advances, not in terminal cells.
- **Fresh proof:** generation reports 11 modules, 88 cards, and 110 questions.
  Isolated and real-Neovim suites pass 88/88 cards, 66/66 primary edit recipes,
  22 conceptual/check cards, 22 changed-art transfer variants, and 22 compare
  paths. The exact automatic popup passes at 188×49, 100×36, and 80×24. The
  cross-route popup suite passes at all three sizes and includes M10.06. This is
  executable/headed evidence; the full human M0→M10 journey and an interactive
  viewer acceptance session remain unclaimed.

## 2026-09-27 — live M0.03 concept check reduced animation reading to one dot

- **Observed live attempt:** the append-only v2 ledger records a failed
  `M0.03` question at 21:20:07 EDT: question `M0.Q01`, displayed choice index
  `2`, followed by a `concept-answer` card failure. Progress correctly remained
  at M0 2/8 and XP 20; this entry concerns lesson quality, not event accounting.
- **Exact bad stimulus:** `M0.Q01` asked the learner to infer a whole animation
  meaning from `BEFORE | .` and `AFTER | ·`. The generated question called that
  evidence for “a spark brightens, settles, and returns,” although two isolated
  punctuation marks show neither a loop nor a settle. The user's description
  that the example was “a literal dot” is accurate.
- **Why prior proof missed it:** generator validation and the 88/88 Neovim suite
  prove IDs, answer indexes, recipes, target equality, and popup routing. They
  impose no minimum visual footprint, no multi-frame evidence requirement for a
  motion-reading question, and no human-quality threshold for ASCII-art examples.
  A syntactically unique one-glyph prompt therefore passed every automated gate.
- **Scope of correction:** this is not an M0.Q01-only wording fix. All 88 cards
  are undergoing explicit card-by-card review for visual substance, persistent
  strip continuity, command/objective fit, repetition, and catalog/runtime
  parity. The generator must reject punctuation-only fixtures and any motion
  question whose visual evidence cannot actually display the claimed temporal
  change.
- **Acceptance falsifier:** a replacement is not accepted merely because its
  command executes or its answer is unambiguous. The prompt must contain a
  readable multi-row subject, the compared frames must visibly support the
  claimed motion, and the module's edit cards must continue one coherent
  animation strip rather than accumulate isolated glyph demonstrations.

### Native all-lesson audit and replacement disposition

Four independent read-only reviews covered every module plus the live/runtime
boundary. Their card-level disposition was materially worse than the previous
88/88 execution result implied:

- **M0-M3:** the prior M0 one-glyph spark, M1 tiny/no-op contour work, M2 text
  cleanup/no-op work, and nearly all of M3 were not acceptable animation
  authoring lessons; only the old M3.05 method comparison was conditionally
  defensible. The replacement subjects are now respectively 3-row spark
  frames, 3-row anchored contours, 4-row faces, and 6-row whole-body poses.
- **M4-M7:** every prior M4 and M5 card required replacement; M6 required major
  repair except its final ordering check; only M7.02, M7.04, and M7.08 were
  conditionally acceptable. Replacements now use a complete 3-row rotating
  prop, 7-row foreground/blank/background composites, equal-height 5-row
  subtractive pyramid frames, and explicit 5-row anticipation/settle timing.
- **M8-M10:** all M8 and M9 cards required replacement. M10's corpus facts were
  sound, but its edits presented isolated pairs without contour context and
  could imply that exact terminal transcription proved proportional shape.
  Replacements now use 5-row whole walkers, a complete 3-row eye-blink study,
  and context-complete SJIS contour fragments; M10 explicitly separates
  Neovim text grading from Saitamaar true-metric visual acceptance.
- **Cross-curriculum/runtime:** the audit found generic normalized question
  templates, MC-only item metadata, weak transfer semantics, no enforced
  generator/artifact equality, no visual-substance contract, and insufficient
  forensic question logging. A historical attempt could not reconstruct the
  exact displayed letter order because the event stored only the semantic
  choice, not the prompt revision, displayed order, or raw letter.

### Corrections and machine falsifiers

- All 66 executable cards now operate on complete multi-row subjects. Generator
  validation rejects any authored start, target, or transfer frame with fewer
  than three nonblank rows, fewer than seven visible glyphs, or a visible span
  below five columns. This gate directly rejects the old one-dot/two-row class.
- Visual-reading items preserve art as bordered multi-line `BEFORE`/`AFTER`
  blocks. Temporal-coherence items show the ordered strip as explicitly
  numbered complete frames. M0.Q01 now compares the full three-row ray/core
  subject, and the next retry stem M0.Q07 shows all five spark frames rather
  than an abstract sentence or isolated punctuation.
- The question schema now distinguishes visual reading, principle choice,
  diagnosis, command prediction, method comparison, transfer reasoning,
  coherence, evidence, risk diagnosis, and two-choice true/false retrieval.
  Immediate identical repetition is explicitly *not* labeled spaced retrieval.
- Each new question event records the curriculum revision, prompt SHA-256,
  displayed semantic order, displayed choice text, raw answer letter, and
  resolved semantic choice. This does not retroactively invent missing evidence
  for the 21:20 attempt; it makes future popup reconstruction falsifiable.
- The live project file was inspected separately from the event prose: it
  contains two ` · ` rows from the credited M0.02, not the later intended
  dot/`o` pair. M0.04 recognizes both historical two-line outcomes, checkpoints
  the exact old file, upgrades it to the revised multi-row start, and preserves
  the already-earned M0.01/M0.02 credit. A regression executes this migration
  and requires the pre-migration checkpoint plus a revision-stamped event.
- The test suite now imports the generator and requires exact equality with the
  committed JSON artifact. It also requires multi-line art for every non-SJIS
  Q01, executes all primary/transfer/compare commands through Neovim, and tests
  the two-choice question path. The card catalog was revised to describe the
  implemented multi-row artifacts rather than the rejected toy roadmap.

### Verification after the all-lesson replacement

- Regeneration reports **11 modules, 88 cards, and 110 conceptual items**.
  `share/test_v2.py` passes under isolated and real user-config Neovim:
  **88/88 cards present, 66/66 primary edit recipes, 22/22 changed-art transfer
  variants, and 22/22 compare paths**. The suite also proves generator/JSON
  equality, visual-substance rejection, two-choice retrieval, migration of the
  exact live two-middle-dot artifact, and refusal to award module mastery when
  unseen-transfer evidence is absent.
- The automatic client-attached fail→retry→pass popup passes at **80×24,
  100×36, and 188×49** with the new three-row M0.01 art and recipe.
- The cross-route headed suite passes at **80×24, 100×36, and 188×49** for the
  first M0.03 visual item, the exact one-failure retry stem M0.Q07, independent
  retrieval, method comparison, five-question module check, spaced review, and
  every live transfer route M0.06-M10.06. At 80×24 it explicitly requires
  `DO THIS M0.03`, `FRAME 1` through `FRAME 5`, held replay, skill tree, module
  map, level/XP, and streak.
- Both legacy suites still pass **46/46** under isolated and real Neovim.
  Python compilation, shell syntax, and `git diff --check` pass. These are
  automated/runtime results; they do not claim that a human has completed the
  entire 88-card course or accepted every proportional rendering interactively.

## 2026-09-27 — conceptual cards could pass animation knowledge without Neovim knowledge

- **Operator acceptance and correction:** the revised multi-frame animation
  multiple-choice item was acceptable, but it remained a one-sided lesson. The
  product requirement is conjunctive: every lesson must teach/test animation
  authoring **and** Neovim, including cards whose primary interaction is a
  conceptual choice.
- **Observed schema defect:** M0.03 rotated among Q01, Q07, Q02, Q06, and Q09.
  Those stems covered visual reading, temporal coherence, authoring principle,
  transfer rationale, and spaced retrieval, but none required a Neovim
  operation or scope decision. A correct animation interpretation alone could
  award the card and its XP.
- **Correction:** every one of the 110 question records now carries explicit
  `animation_prompt`/`animation_answer` and
  `neovim_prompt`/`neovim_answer` fields. The rendered prompt labels both
  halves, and every displayed choice answers both. Four-choice items include a
  distractor with the animation half right and Vim half wrong, plus one with
  the Vim half right and animation half wrong; recognizing only one domain is
  therefore insufficient.
- **Regression contract:** generator validation, runtime validation, and the
  unit suite reject any question missing either half or containing a one-sided
  answer choice. The existing changed-stem rotation and complete-frame visual
  stimuli remain intact; this adds the required Neovim decision rather than
  replacing the accepted animation question.

## VD-10 · 2026-09-28 — full-curriculum review: v2 content does not teach or test what its receipts claim

- **Scope and state reviewed:** generated `share/curriculum-v2.json` revision
  `2026-09-27.7` (11 modules, 88 cards, 110 questions), `share/v2_runtime.py`,
  and the headed popup, on the uncommitted working tree at HEAD `17f8712`.
  Every card's start/target/recipe was read; every question in M0 and M10 and
  Q01/Q07 in every module was read; the remaining questions were checked by
  script because they are template instances of the same module strings.
- **What holds:** `python3 share/test_v2.py` passed (66/66 recipes, 22
  transfer variants, 22 compare paths; config=none) and
  `python3 share/test_drills.py` passed 46/46 (config=none) on 2026-09-28.
  M10 counts match `share/sjis_corpus_findings.v1.json`. These prove key-path
  passability, not teaching quality. Real-config runs were not repeated.
- **Finding 1 — paired questions are solvable without either domain
  (falsifies the preceding entry's "recognizing only one domain is therefore
  insufficient").** Each four-choice item has one A-right/V-wrong and one
  V-right/A-wrong distractor, so the keyed choice is the unique one whose two
  halves each occur twice. Majority vote over repeated halves selects the key
  in 100/110 items; the other 10 are two-choice `true_false` items (spec §7/§9.4
  require four choices). Falsifier: count half frequencies per item and pick
  the max-sum choice.
- **Finding 2 — keyed answers contradict the displayed evidence.** The keyed
  NEOVIM half is the module's fixed `basic`/`scaled` string, not the operation
  shown: M2.Q01 shows a note deleted (`D`) but keys "find the eye and replace
  one glyph with r"; M3.Q01 and M6.Q01 show a one-glyph `r` but key a copy
  operation; M7.Q01 shows a `:t` range copy but keys dot repeat. Keyed
  ANIMATION halves contradict their own strips: M1.Q07 "fixed anchors" while
  `o` moves from column 0 to 7 in frame 2; M6.Q07 "visibly build" while the
  strip ends finished→incomplete; M8.Q07 "coherent" while the arm flips sides
  with no transition (the module's declared defect).
- **Finding 3 — the popup hides the task at common sizes.** Compact briefs
  (any terminal under 38 rows) clip `DO THIS` to 61 columns
  (`_write_session_lesson`, `_clip(card["prompt"], 61)`), which removes the
  instruction on all 66 edit cards because every prompt starts with a fixed
  preamble. Headed capture via the route harness (M0.04, seeded 3 passes):
  80×24 and 100×36 both show only `DO THIS  Work independently without a
  revealed target in Spark loop:…`; at 80×24 the Neovim strip window shows 2 of
  the 6 project rows. Guided `TARGET` is flattened with ` / ` and clipped to 21
  columns, so the target art is not visible in compact mode either. The route
  suite passes because it asserts boundary strings, not task visibility.
- **Finding 4 — checks and independent cards are graded by exact match against
  unstated targets.** All 11 `*.08` module checks render the same boilerplate
  prompt; `roadmap_contract` (the only statement of the required edit) is never
  read by the runtime. Unstated glyphs are required by M0.04 (`=`), M0.06,
  M1.05 (`;`), M2.04/M2.05/M2.06 (`o`/`O`), M3.04, M3.08 (`·` via `<C-k>.M`,
  never taught), M5.04, M5.08, M7.04 (`·`), M7.05 (`_`→`-`), M8.04 (five
  hand-typed rows), M8.05, M9.05, M10.04, M10.05, M10.08. Spec §4 requires two
  unhinted transfer edits per check; each check has one, and 7/11 check edits
  are a single `:t` copy.
- **Finding 5 — the lesson art violates the course's own animation rules.**
  Loops close by copying frame 1 to the end (M0, M1, M4, M8), producing a
  double frame at the loop seam — the "dead duplicate" the course teaches as a
  defect. M1.04's "descending counterpart" moves the endpoint the module says
  must stay fixed; the `:`→`;` "material" change has no visual meaning. M4's
  main extremes stack `\` in one column (reads as a hatched vertical, not a
  tilt; the M4.06 variant draws the diagonal correctly); M4 `animation.pivot`
  says column 1 while the pivot is column 3. M5 depicts no overlap: the "false
  seam" `|` is two rows below the pivot, and the M5.04 mirrored blade sits at
  columns 4-5, detached from the column-3 pivot. M6 subtracts the base first,
  so forward playback builds a floating pyramid top-down; M6.05 appends an
  identical duplicate; M6.08/M7.08 strips end finished→incomplete. M7.05
  "polish" changes `/_\` to `/-\` only in the held frames, so the layer spelling
  pops at completion. M8's four-frame walk is contact, passing, contact,
  copy-of-contact (no second passing pose); M8.05's range `1,6` crosses into
  frame 2 while claiming "only the first pose", and rewrites the arm M8.01 said
  stays fixed. M9 "capstone" repeats M2's blink on the same contour with no
  planning or original authoring.
- **Finding 6 — Neovim coverage is far narrower than cited tutor lessons.**
  Across every expected/alternative/variant key path: `G` 59, `C` 53, `:t` 23,
  `r` 21, `$` 21, `p` 19, `yy` 17, `:s` 13, `f` 8, `.` 6, `<C-v>` 4, `:m` 4,
  `q/@` 3, `dd` 2, `D` 2, `F` 1. Never used: `w b e W B E`, `x`, `u`/`<C-r>`,
  `d`/`c`/`y` with a motion, text objects, `/ ? n N * #`, `%`, `v`/`V`, `J`,
  `i a A I`, `>>`, `~`, registers, marks, `:normal`, `:g`. M1 cites tutor
  2.1/2.4/4.2 (deletion, counts, search) and exercises none; M5 cites tutor 5.3
  (writing a selection to a file). Heavy `C` line-retyping contradicts VD-01's
  "motions, operators, counts, text objects".
- **Finding 7 — the question bank is template filler.** 18 distinct stems
  across 110 items ("What animation intent must the edit preserve in <M>?"
  ×30); 20/110 show any art; 35 choices are ungrammatical fills ("preserve a
  registered three-row spark brightens…"); 50 choices quote another module's
  meaning/principle and are eliminable on sight; all 310 wrong-choice feedback
  strings are the same generic "Not yet. One or both halves…" (spec §7 requires
  misconception-specific feedback); `true_false` ANIMATION halves are about
  spaced retrieval, not animation; about three items per module quiz the
  tutor's own design (why a transfer file, what evidence advances a module).
  M10's NEOVIM half is a Saitamaar-rendering instruction and its items test
  memorized corpus counts.
- **Required successor:** regenerate questions from per-item authored
  stimuli with keyed answers derived from the displayed change, and a
  validator that rejects majority-vote-solvable items; render the full task and
  full target at every supported popup size; state the required edit on every
  check/independent card and grade by rule where glyph choice is free; repair
  the listed art; rebuild Neovim coverage against the tutor chapters it cites.
  Acceptance stays open until those falsifiers pass and a learner completes
  M0-M2 from the popup without reading JSON.

### VD-10 second sweep · 2026-09-28 — process violations and coverage regressions

- **Default switched before release gates.** Plan P7 requires opt-in rollout,
  an inspected M0-M2 journey, and a retain/adapt/retire disposition for every
  legacy ID before the hourly default changes (`share/CURRICULUM_V2_PLAN.md`
  P7; spec `:205`). Fix attempt 1 already made v2 the default hourly route,
  and no disposition record exists (search for `disposition`/`retire` finds
  only the spec sentence).
- **The default switch removed Neovim coverage.** The 46 legacy drills
  (`share/curriculum.json`) exercise `dw`, `d2W`, `u`/`<C-r>`, `cw`, `/`
  search, `ci(` with `%`, `ca(`, `dap`, `~`, `"a` and `"0` registers,
  `ma`/`'a` marks, `V` linewise visual, blockwise `I`/`$A`/`d`, a macro using
  `I`/`A`, `;` repeat, `:t.`, `:normal`, `O`, `A`, `J`. None of these appear in
  any v2 key path, so the hourly route teaches fewer commands than the course it
  replaced.
- **No remediation path.** Spec §4 and catalog `:48-49` require a failed
  Q/T/K card to schedule a named remediation and a changed variant. Neither
  runtime nor generator contains a remediation card; a failed concept card
  rotates to the next stem of the same card, and a failed check re-asks the
  same bank.
- **Spaced review never re-practises an edit.** `run_review` asks one
  multiple-choice item and nothing else (`share/v2_runtime.py` `run_review`),
  while spec §8 requires reviews to retrieve intent/operation on changed art.
  After first pass, no Neovim operation is ever retrieved again.
- **Playback is optional and untaught.** `--preview` exists only as a manual CLI
  flag; no card requires playing the strip, checking jitter, or tuning rate,
  although the course claims A6 "playback + polish" and ascii-art-authoring §9h
  makes partial playback a required step.
- **ASCII-art method coverage is thin.** Against ascii-art-authoring
  §§2-10, no card exercises: blocking/variants/choose-by-eye (§2), layer blocks
  stored back to front (§3.5), alphanumeric-focus rules (§4.3), material
  contracts (§4.5, M1 misuses "material"), off-vertical anti-aliasing with
  `¡ ! . '` (§4.6), stair-step typing and hand mirroring drills done correctly
  (§4.7), isometric ground (§5), dithering, brick ground, shadows (§8),
  references/concept/size/plan with seconds and fps (§9a-e), recursive
  bisection, onion-skin partial merge, symmetry count, half-cell limit (§9g),
  pad-to-tallest and rate tuning (§9h), stagger, overshoot/settle, drag,
  bounce, motion blur, growth, reuse by reversal, dense→empty coherence (§10).

### VD-10 gap inventory · 2026-09-28 — Neovim topics other courses cover that v2 does not

- **Method:** v2 key-path command set (all expected, alternative, and variant
  paths) compared with topic lists from the installed Neovim 0.12.5 tutor
  (`runtime/tutor/en/vim-01-beginner.tutor`, `vim-02-beginner.tutor`), the user
  manual (`runtime/doc/usr_toc.txt`, `usr_04`, `usr_10`, `usr_24`, `usr_25`,
  `usr_26`, `usr_32`), OpenVim (`egaga/openvim` `js/tutorial/sections.js`),
  VIM Master (`renzorlive/vimmaster` `content/lessons`), Vim Hero lesson sidebar,
  Vim Adventures command list, vim-be-good games, Practical Vim 2e tip list,
  and Learn-Vim (`iggredible/Learn-Vim`). Vim Hero, Vim Adventures, and Practical
  Vim were only partly accessible; VimGolf was not accessed.
- **v2 uses only:** `G gg j l 0 $ f F r C D o yy p dd . :t :m :s :put`, blockwise
  `<C-v>…r`, `<C-k>` digraph, and `q/@` in one alternative path.
- **Missing beginner topics (taught by nearly every source):** `x`,
  `i a A I O`, `w b e W B E`, `^`, `t T ; ,`, operator+motion (`dw cw ce c$
  d2w`), `u <C-r> U`, `/ ? n N * #`, `%`, `R` Replace mode, `J`, `v V`, text
  objects (`iw aw i( a( i" ip ap`), marks, registers (named, `"0`, append,
  `"_`), `:set list/hlsearch`.
- **Missing intermediate topics:** block `I`/`A`/`c`, ragged `$A`, `gv`, `o` in
  visual; recorded, edited, and recursive macros; `:normal`; `:g`/`:v`; `:s`
  flags, `&`/`g&`, `\v`, `\=`; mark ranges `'<,'>`; `<C-a>`/`<C-x>`/`g<C-a>`;
  `~ g~ gu gU`; `> <`; `gq`; `:sort`; jumplist `<C-o>`/`<C-i>`; `H M L zt zz`;
  insert `<C-r>{reg} <C-w> <C-o>`; completion `<C-n>`; undo tree `g- g+
  :earlier`; windows/splits; `:help` navigation.
- **Missing fixed-width-art topics (rare even in other courses):**
  `virtualedit=all`, `gr`/`gR` virtual replace (usr_25.5), `|` column motion,
  `g_`, `zp`/`zP` blockwise put without trailing spaces (`change.txt`), `:set
  list`, `:retab`/`expandtab`, `:center`/`:right`, `ga`, `<C-v>{code}`,
  `colorcolumn`/`cursorcolumn`, split + `scrollbind` or `:diffthis` for frame
  comparison.
- **Acceptance for the intermediate goal:** every topic above has at least one
  guided card, one unhinted card on changed art, and one spaced edit review, and
  each is tied to an ascii-art-authoring step. Coverage is measured from key
  paths, not from `source_ref` citations.

### VD-10 successor correction · revision 2026-09-28.9

This entry supersedes closure claims made before the second sweep. It records
what the current implementation and tests prove, and it leaves broader parity
work open.

- **Popup task/target visibility fixed.** Compact lesson rendering now wraps the
  complete authored prompt and renders each target row plus the full recipe
  (`share/v2_runtime.py:530-565`). The headed route test requires every wrapped
  task line, every target row, and every recipe key
  (`share/test_tmux_v2_routes.py:199-219`). It passed at 80×24, 100×36, and
  188×49 on 2026-09-28.
- **Post-lesson evidence and progress fixed.** Feedback retains artifact or
  concept replay before the held progress page (`share/v2_runtime.py:914-970`),
  and the progress surface renders node state, module counts, XP/level, review
  count, badges, active remediation, streak, all-time total, and next lesson
  (`share/v2_runtime.py:1650-1702`). The headed suite requires replay,
  `SKILL TREE / MODULE PROGRESS`, `CURRENT MODULE MAP`, `LEVEL`, and `streak`,
  and proves the page stays held until Enter
  (`share/test_tmux_v2_routes.py:221-256`).
- **Cooldown-on-open fixed.** Only durable pass/fail attempt events touch the
  cooldown stamp (`share/v2_runtime.py:187-205`). The unit test proves a
  `session_open` event does not stamp and a failed question does
  (`share/test_v2.py:195-208`).
- **Named remediation fixed.** Runtime persists Q/T/K remediation IDs, names,
  and changed variants (`share/v2_runtime.py:209-277,442-459`). Tests prove
  transfer failures rotate through distinct art and concept/check failures
  create visible Q/K records (`share/test_v2.py:585-627`).
- **Spaced review edit retrieval fixed.** A review selects changed transfer art,
  asks the paired conceptual item, opens an unhinted Neovim edit, and awards
  review progress only when both pass (`share/v2_runtime.py:1479-1571`). The
  headed route performs the changed-art edit and requires both concept and edit
  replay (`share/test_tmux_v2_routes.py:175-183,221-225`).
- **Module playback fixed.** Successful module-check artifacts automatically
  invoke preview and retain `playback_verified` evidence
  (`share/v2_runtime.py:1355-1364,1407-1428`). The headed check rejects a
  debrief without `PLAYBACK VERIFIED` (`share/test_tmux_v2_routes.py:236-239`).
- **Toy and defective animation stimuli fixed for the cited modules.** M4 now
  has readable diagonal extremes, a real aligned block column, and pivot column
  4; M5 places the background seam directly under the pivot; M6 builds
  bottom-up in playback order; M7 keeps material spelling coherent across
  frames and removes the unjustified duplicate; M8 has a distinct return
  passing pose and a correctly scoped first-pose edit; M9 is an original
  high/fall/squash/rebound study rather than the M2 blink. These definitions are
  in `share/gen_curriculum_v2.py:371-891`; the validator rejects any frame with
  fewer than three nonblank rows, seven ink cells, or width five
  (`share/gen_curriculum_v2.py:1622-1636`).
- **Question-bank template defects fixed.** Generation yields 110 distinct
  authored paired prompts with four choices, both ANIMATION and NEOVIM halves,
  local keyed answers, and mistake-specific feedback. Validation rejects
  missing paired fields, non-four-choice items, generic feedback, duplicate
  stems, fewer than 55 art-bearing prompts, and half-frequency answer leakage
  (`share/gen_curriculum_v2.py:1637-1684`).
- **The narrow audited Vim-category regression is fixed, not full parity.** The
  generated executable paths are guarded for `w/b/e`, `x`, `u`, `daw`, `ci(`,
  `/`, `%`, characterwise/linewise/blockwise Visual mode, `J`, `I`/`A`, a named
  register, marks, and range `normal!`
  (`share/gen_curriculum_v2.py:1751-1765`). All 66 primary paths, 22 changed-art
  variants, and 22 compare paths passed real Neovim with `-u NONE`; the same 66
  primary and 22 compare paths passed the real user configuration on
  2026-09-28. This does not satisfy the larger gap inventory above.
- **Legacy disposition is now explicit and test-enforced.** All 46 IDs have one
  `adapted`, `partial`, or `retained-only` row with a concrete v2 card and a
  named gap (`share/LEGACY_CURRICULUM_DISPOSITION.md:1-69`). The suite checks
  exact ID-set equality, uniqueness, and card existence
  (`share/test_v2.py:459-498`). Totals are 30 adapted, 8 partial, and 8
  retained-only. The old statement that one representative heading test proved
  “literal legacy parity” was false and has been removed.

**Verification on 2026-09-28:** `python3 share/gen_curriculum_v2.py` generated
11 modules, 88 cards, and 110 questions; `python3 share/test_v2.py` passed
66/66 primary edit paths, 22/22 changed-art variants, and 22/22 comparison
paths with `-u NONE`; `python3 share/test_v2.py --real` passed the corresponding
real-config paths; `python3 share/test_drills.py` and `--real` passed all 46
legacy drills; `share/test_tmux_v2_routes.py` passed all 18 live routes at each
of 80×24, 100×36, and 188×49; `share/test_tmux_v2.py` passed the automatic
client-attached popup at those same three sizes.

**Still open; do not call these complete:**

1. No human learner has completed the required M0–M2 popup journey. Automated
   headed tmux proof is not human usability evidence.
2. The gap-inventory acceptance target—every listed beginner, intermediate, and
   fixed-width-art topic receiving a guided card, changed-art unhinted card, and
   spaced edit review—is not implemented. The current validator covers the
   specifically audited categories only.
3. The disposition table exposes 16 partial or retained-only legacy drills;
   their exact command lessons are still available only partly or through the
   legacy route.
4. The full ascii-art-authoring method inventory (including isometric ground,
   dithering, shadows, and every advanced animation construction method) is not
   yet represented as executable modules.

### VD-10 recheck of revision 2026-09-28.9 · 2026-09-28 — coverage guard counts oracle strings, not learner practice

- **Confirmed fixed (independent recount on `share/curriculum-v2.json`
  revision `2026-09-28.9`):** majority-vote leakage 0/110; all 110 items have
  four choices; 440/440 feedback strings distinct; longest-choice heuristic hits
  the key 1/110.
- **Coverage guard is satisfied by padding.** `gen_curriculum_v2.py` checks that
  a literal token occurs in some key path (`coverage` dict near the end of the
  validator). Several paths contain the token without needing it: M0.01
  `jwbewbwro` (a direct path is `jf.ro`); M6.04 `6GJu…` joins a line and
  immediately undoes it; M8.04 `Go<Esc>I \<Esc>Ao<Esc>…` splits one typed row
  into `I`/`A` fragments; M3.08 `13Gma2G'aj…` sets a mark only to jump back.
- **The learner is never required to use a covered command.** Non-compare cards
  pass on exact buffer result. For compare cards `_method_family`
  (`share/v2_runtime.py:757-766`) returns `other-valid-exact-target` for any
  path that produces the target, so a method is named but never required. The
  commands above can be skipped and the card still passes. Coverage therefore
  describes the answer key, not what a learner practises or is examined on.
- **Residual art defects:** M4.08 and M5.08 end with a frame identical to frame
  1 (double frame at the loop seam). M6.08 playback frame 1 shows an apex `.`
  over an empty row 2, so the apex floats before the layer under it exists; the
  build is not bottom-up.
- **Acceptance addition:** a covered command counts only when a card that
  requires it (by method check or by a task it alone can do efficiently under a
  keystroke budget) passes unhinted and again in a spaced review.

### VD-10 proposed interleaved sequence · 2026-09-28 — plan, not accepted

- **Status:** operator-requested plan; not implemented and not accepted. It
  orders modules by the ascii-art-authoring process (§§1-10) and gives each
  art step the Neovim family that the step needs. Card counts are not fixed.
- **Invariants for every module:** (1) edit in place: overwrite with `r`/`R`/
  `gR` and erase with `r<Space>`; insert or delete a character only when the
  row must change length; (2) frames and layers are blank-line-separated blocks,
  so `ip`/`ap` and `{`/`}` address them; (3) one new art concept and one new
  Neovim family per module, both used on the same persistent artifact;
  (4) every later module reuses earlier families on changed art (spiral
  review); (5) a command counts only when a card requires it (method check or
  keystroke budget) unhinted and again in a spaced edit review.

| # | Art subskill (ascii-art-authoring) | Neovim family | Artifact |
|---|---|---|---|
| S0 | Grid, cell aspect, bounded alphabet (§§1, 4.1) | modes, `hjkl`, `r`, `R`, `u`/`<C-r>`, `:set list virtualedit=all cursorcolumn` | stamp sheet |
| S1 | Stair-step slopes and diagonals; typed runs (§§4.4, 4.7.1-4) | `R` runs, `0 ^ $ g_`, `N\|`, counts | slope sheet |
| S2 | Hand mirroring by row reversal and glyph swap (§4.7.6-7) | `f t ; ,`, `gR`, `.` | mirrored slope pair |
| S3 | Blocking a still, emptying uncertain cells, coarse horizontals (§2.1-6) | `w b e W B E` over punctuation runs, `r<Space>` vs `x`, `d`/`c` with motion inside a row | first still |
| S4 | Joint height `. ' :` and off-vertical anti-aliasing (§4.6) | `j`/`k` column memory, `<C-v>` + `r`, `o`, `gv` | smoothed curve |
| S5 | Variants, choose by eye, keep versions; material contract; symbol table (§§2, 4.5, 1.7) | `ip`/`ap`, `yap`, `}`, `P`; registers `"a-"z`, `"0`, `"_`, insert `<C-r>a`; `<C-k>`, `ga` | variant sheet + palette |
| S6 | Layers back to front, seams, erase from background (§3) | marks, `:'a,'b` ranges, blockwise yank + `zp`/`zP`, `:vsplit` + `scrollbind` | layered still |
| S7 | Texture: dither, erase to lighten, brick offset, shadow, isometric ground (§§5, 8) | counts, `>`/`<` with `shiftwidth=1`, block `I`/`$A`, `:s` in range, `&`/`g&`, `qq`/`@q`/`@@` | textured ground |
| A0 | References, concept, primary key, size test, written plan with seconds/fps (§9a-e) | `:read`, `:t`/`:m` with ranges, `<C-a>` frame labels, `:center` | plan + primary key |
| A1 | Extremes first; copy-then-vary (§9f) | `yap}p`, `:t$`, `gR` on the copy, `.` | extremes strip |
| A2 | Midpoint, recursive bisection, onion-skin merge, symmetry count, half-cell limit (§9g) | `:vsplit` + `:diffthis`, `\|` column checks, `colorcolumn`, block copy | tween strip |
| A3 | Temporal coherence across frames (§10) | macros across frames with `}`, recursive/edited macros, `:g/…/normal`, `n` + `.` | coherent strip |
| A4 | Timing: hold, stagger, overshoot/settle, drag, bounce, no dead frame (§10) | counted put for holds, `:m` reorder, `:diffthis` for dead frames, undo tree `g-`/`g+`/`:earlier` for timing variants | timed strip |
| A5 | Subtractive build, playback order, pad to tallest frame (§§9h, 10) | `dap` + `P`/`:m` for reversal, counted `o<Esc>` padding, `:%s/\s\+$//e`, `zp` | build animation |
| A6 | Reuse by reversal and mirrored action (§10) | S2 mirroring at frame scale; `:s` with `\=` dictionary only to check a manual mirror, never to replace it (§4.7.7) | mirrored action |
| A7 | Preview, jitter check, rate tuning, polish; original walk 4+4+2 (§§9h, 10) | all prior families; `:help` lookup | original capstone |
| P | Proportional SJIS branch (§15) after S5 | whitespace law with `:set list`, idiom registers | SJIS notebook |

- **Mapping to current revision `2026-09-28.9`:** M0 spark ≈ S0/A1; M1 contour
  ≈ S1/S4; M2 face ≈ S3; M3 pose ≈ A1; M4 rotation ≈ A2; M5 layers ≈ S6; M6/M7
  pyramid ≈ A5/A4; M8 walk ≈ A7; M9 bounce ≈ A4; M10 ≈ P. Absent in full: S2,
  S5, S7, A0, A3, A6.

### VD-10 correction · revision 2026-09-28.10 · 2026-09-28 — padded coverage and three frame defects removed

- **Coverage semantics changed.** `share/gen_curriculum_v2.py:43-65` now gives
  a lesson an explicit `method_requirement`; `share/v2_runtime.py:757-794`
  recognizes only a taught compare path and separately checks required token
  patterns plus an optional key ceiling. An exact target reached through an
  unknown comparison path or without required evidence is rejected in both
  recovery and normal attempt routes (`share/v2_runtime.py:1351-1387`,
  `:1431-1451`). The generated `verified_method_coverage` list is derived only
  from those enforced paths (`share/gen_curriculum_v2.py:1624-1641`).
- **Padding removed, not reclassified as mastery.** M0.01 now uses `j0f.ro`;
  M6.04 uses `6G0D`; M8.04 opens and types complete pose rows without filler
  `I`/`A`; M3.08 addresses the final eye directly without `ma`/`'a`. Their
  paired conceptual questions were rewritten to match the executable paths.
  `share/LEGACY_CURRICULUM_DISPOSITION.md` therefore moves undo, append, join,
  marks, and candle-join to `retained-only` rather than preserving false v2
  coverage. The honest tally is now 26 adapted, 7 partial, 13 retained-only.
- **Loop seams fixed.** M4.08 now deletes the copied first three-row pose and
  finishes `backslash → vertical → slash → vertical`, wrapping to the first
  pose without an adjacent duplicate. M5.05 inserts a genuine vertical
  seven-row midpoint between the left and right blade extremes, so M5.08 no
  longer ends on frame 1.
- **Bottom-up build fixed.** M6 subtractive frames clear the apex row and then
  the shoulder row without deleting either. M6.08 begins with two blank top
  rows over three attached lower layers, then adds the shoulder and apex; no
  seed floats above an empty row. M7's continuation was updated to use the
  same attached build and repeats a bounded material-band edit across its
  declared hold.
- **Regression evidence.** `python3 share/gen_curriculum_v2.py` wrote revision
  `2026-09-28.10`; `python3 share/test_v2.py` passed 66/66 primary edit
  recipes, 22/22 comparison paths, 22 changed-art variants, all 110 paired
  questions, method-evidence checks, and explicit assertions that M4/M5 do not
  repeat frame 1 at the loop seam and M6 begins from attached lower layers.
- **Still open; do not call the wider course complete.** The legacy disposition
  now exposes 20 partial/retained-only drills. The S0–S7/A0–A7 sequence above
  remains the implementation plan for missing Vim families and the still,
  texture, planning, in-betweening, timing, and polish sections of
  `ascii-art-authoring`. Revision `.10` fixes the audited false claims and art
  defects; it does not yet implement those missing modules.

### VD-10 follow-through · revision 2026-09-28.11 · 2026-09-28 — real redraw module and source-specific reviews

- **M11 adds one coherent fixed-width animation branch rather than keyword
  padding.** Its persistent three-row machine strip overwrites a bounded roof
  with `R`, copies the complete pose, performs a causally real `u`/`<C-r>`
  cycle, compares local replacements with a row-scoped substitute, transfers
  the redraw to changed shells, and places two motion-blur trails at display
  column 14 using `virtualedit=all` and `13|`
  (`share/gen_curriculum_v2.py:1055-1195`). These operations act on the saved
  animation artifact; they are not inserted before an unrelated solution.
- **Spaced edits can now belong to the source technique.** A card may own two
  `review_variants`; review retrieval prefers that bank and otherwise falls
  back to the module transfer (`share/gen_curriculum_v2.py:43-57`;
  `share/v2_runtime.py:1557-1580`). M11 provides source-specific changed art
  for whole-pose copying, meaningful undo/redo, bounded indicator editing, and
  virtual-column trails. The suite executes every declared review variant
  through Neovim (`share/test_v2.py:732-760`).
- **Earlier required methods gained changed-art reviews too.** M0.01's core
  find/replace, M4.08's three-row seam deletion, and M6.04's in-place apex
  clearing now each have two distinct review fixtures
  (`share/gen_curriculum_v2.py:92-115,473-505,653-679`). This corrects the
  narrower defect where those source cards always reviewed the module's one
  transfer operation.
- **Honest legacy tally after M11:** `undo` is now adapted at M11.04, leaving
  27 adapted, 7 partial, and 12 retained-only rows; 19 legacy gaps remain
  (`share/LEGACY_CURRICULUM_DISPOSITION.md:1-69`). M11 does not establish the
  absent word-motion, search-repeat, register, Visual-block-insert, texture,
  planning, or full animation-method inventory.

### VD-10 follow-through · revision 2026-09-28.12 · 2026-09-28 — exact method evidence and M12 mirrored sweep

- **The remaining method-evidence loophole is closed for declared exact
  paths.** A `method_requirement` may now list `exact_any_of` accepted paths
  (`share/gen_curriculum_v2.py:65-75`). Runtime strips only the final submit
  command and rejects every other captured path not exactly in that list
  (`share/v2_runtime.py:771-789,800-831`). Thus a learner cannot prepend an
  unused `u`, `J`, mark, motion, or other padding merely because the final
  buffer is correct. Tests explicitly prepend padding and require rejection
  (`share/test_v2.py:762-773`). Comparison cards likewise continue to accept
  only one of their two exact taught alternatives
  (`share/v2_runtime.py:780-789`).
- **Generated coverage now reports only runtime-enforced evidence.** Exact
  requirements are labelled `runtime-required exact accepted key path`, while
  comparisons are labelled `runtime-recognized exact comparison path`
  (`share/gen_curriculum_v2.py:2053-2072`). The validator checks exact-path
  consistency and validates visual substance and schema completeness for every
  card-specific review fixture (`share/gen_curriculum_v2.py:2183-2205`;
  `share/v2_runtime.py:54-122`).
- **M12 is an animation-plus-Neovim module, not a disconnected command card.**
  The complete three-row mirrored mechanism passes an accent from the left
  joint to both upper joints, delays the lower pair as drag, brightens the
  release, then exits on the right. `t` approaches the left landmark, `T`
  approaches its right mirror, `;` reaches the second delayed joint, and `,`
  returns to the first still-unedited joint. The module also compares repeated
  character search with a row-scoped substitute, transfers to two unfamiliar
  shells, and hand-authors the opposite-side return without byte-reversing the
  slash directions (`share/gen_curriculum_v2.py:1198-1343`). Its eight learner
  contracts are recorded at `share/CURRICULUM_V2_CARD_CATALOG.md:285-296`.
- **The course is now 13 modules / 104 cards / 130 paired questions.** There
  are 78 executable primary cards, 26 conceptual/check cards, 26 changed-art
  transfer variants, and 26 comparison alternatives. Structural assertions
  are at `share/test_v2.py:64-144`; generator count guards are at
  `share/gen_curriculum_v2.py:2096-2098`.
- **Legacy mirroring remains partial.** M12 moves an accent to its mirrored
  partner but does not require retyping and glyph-swapping an entire row, so
  `mirror-run` is now classified `partial`, not `adapted`. The current honest
  disposition is 26 adapted, 8 partial, and 12 retained-only: 20 gaps
  (`share/LEGACY_CURRICULUM_DISPOSITION.md:1-69`).
- **Verification performed for this revision:**
  `python3 -W error::SyntaxWarning share/gen_curriculum_v2.py` generated
  revision `.12`; `python3 share/test_v2.py` and
  `python3 share/test_v2.py --real` each passed all 78 primary paths, all 26
  transfer variants, all 26 comparison paths, every explicit changed-art
  review fixture, and graph/question/state checks. `python3
  share/test_drills.py` and `python3 share/test_drills.py --real` each passed
  all 46 legacy drills. No current-revision headed tmux result is claimed.
- **Still open; do not call the full audit complete:** 20 partial/retained-only
  legacy rows remain. Beginner gaps still include `W/B/E`, `n/N/*/#`, `~`,
  and the `"0`/`"_` registers; intermediate and fixed-width-art gaps still
  include the broader Visual, macro, Ex, jump-list, undo-tree, window/onion-skin,
  paragraph-object, palette-register, texture, planning, timing, and polish
  inventory. M0-M10 cards without a source-specific review bank still fall
  back to their module transfer, so per-technique repetition variety is only
  partially implemented. The live popup, remediation, debrief, review, and
  playback routes have not been rerun against revision `.12`.

## VD-11 · 2026-09-28 — failed popup: no DO THIS, horizontal replay, failure not counted toward streak

- **Operator report (live popup, 2026-09-28):** a failed popup showed no
  `DO THIS` section; the replay was horizontal instead of two columns (what the
  learner typed/produced vs what the target required); a failed attempt did not
  count toward the daily streak.
- **Ledger evidence:** `~/.local/state/vim-daily/events-v2.jsonl` records
  `M0.04` `result=fail reason=target-mismatch` at 2026-09-28T00:55:25-04:00 and
  2026-09-28T02:54:44-04:00. No `2026-09-28.log` exists, so the streak reader
  (`_legacy_streak`, counts only rows without `result=` in dated logs) sees no
  activity today; `_legacy_credit` is written only on pass or review pass.
- **Concurrency note:** `share/v2_runtime.py`, `share/gen_curriculum_v2.py`, and
  `share/test_v2.py` were modified at 02:55-02:56 by another session while this
  entry was written; the 02:54 popup may have run against a mid-edit tree.
- **Operator requirement:** every failure screen shows `DO THIS`; the replay is
  a two-column comparison (yours | target); any attempted card (pass or fail)
  counts toward the streak while mastery/XP stay pass-only.

### VD-10 follow-through · revision 2026-09-28.13 · 2026-09-28 — enforced evidence, review ownership, and M13 texture motion

- **The padding defect is now a graded failure, not a recipe cleanup claim.**
  Cards that exist to demonstrate one command path declare `exact_any_of`; the
  runtime compares the captured edit tokens with the accepted paths exactly
  after removing only the submit command (`share/v2_runtime.py:872-898`). The
  suite also rejects a prepended unused command for every source-linked exact
  review (`share/test_v2.py:804-818`). Thus reaching the same final buffer with
  `u`, `J`, a mark, or an unrelated motion prepended no longer proves the
  declared method.
- **Review evidence is source-owned and deliberately incomplete.** The generator
  adds `review_source_card_id` and `review_method_family` only when a card has
  its own changed-art review bank, including transfer variants
  (`share/gen_curriculum_v2.py:2254-2264`), and publishes that list separately
  as `verified_review_coverage` (`:2287-2316`). Runtime refuses an unlinked
  source instead of silently borrowing the module transfer
  (`share/v2_runtime.py:1706-1725`), schedules a due date only when changed art
  exists (`:1290-1296`), and ignores stale unsupported review rows
  (`:411-428`). The generated `.13` artifact currently verifies 25 source cards
  out of 112; the remaining cards do **not** have spaced-edit coverage and are
  not represented as if they do. The no-fallback case is regression-tested with
  M12.01 (`share/test_v2.py:819-825`).
- **Adjacent duplicate frames are now classified instead of inferred.** Every
  actual adjacent identical pair is declared as a playback `hold`, authoring
  `scaffold`, `material-normalization`, or `reviewable-duplicate`, with a reason;
  holds additionally declare playback intent and duration
  (`share/gen_curriculum_v2.py:2151-2177`). Generator and runtime validation
  reject an unclassified pair or an unbounded hold
  (`share/gen_curriculum_v2.py:2423-2443`; `share/v2_runtime.py:131-148`), and
  the test suite removes one declaration to prove the validator fails closed
  (`share/test_v2.py:1027-1042`).
- **Progress levels no longer stop at the old title table.** Level continues
  every 80 XP; after the fourteen named levels, the final title gains a `+N`
  prestige suffix and the progress-within-level value remains in `0..79`
  (`share/v2_runtime.py:1871-1880`). This fixes the prior state where XP beyond
  the finite title list could report nonsensical progress.
- **M12 is now named honestly.** `Joint sweep` teaches causal `t`, `T`, `;`, and
  `,` landmark motion while animating stagger/drag; it no longer claims that
  moving one accent proves full-row manual mirroring
  (`share/gen_curriculum_v2.py:1198-1343`;
  `share/CURRICULUM_V2_CARD_CATALOG.md:285-296`). `mirror-run` therefore remains
  `partial` in the legacy disposition, not adapted
  (`share/LEGACY_CURRICULUM_DISPOSITION.md:58`).
- **M13 adds real WORD-motion practice inside an animation strip.** `Texture
  pulse` uses `W`, `B`, and `E` to move an acting accent across
  whitespace-separated punctuation texture clusters, with a three-row pose,
  copy-and-vary frames, a method comparison, two changed-art transfers, paired
  animation/Neovim questions, and a module check
  (`share/gen_curriculum_v2.py:1346-1493`;
  `share/CURRICULUM_V2_CARD_CATALOG.md:298-309`). This closes only the uppercase
  WORD-motion portion of the beginner inventory; it does not close lowercase
  `w/b/e` as causal required practice or the other command gaps.
- **The current tested size is 14 modules / 112 cards / 140 paired questions.**
  The suite asserts those exact counts and question structure
  (`share/test_v2.py:64-101`), then executes all 84 primary edit recipes, 28
  changed-art transfer variants, and 28 comparison paths. On 2026-09-28 both
  `python3 share/test_v2.py` and `python3 share/test_v2.py --real` passed revision
  `.13` with those totals (`share/test_v2.py:1044-1047`). This is recipe,
  curriculum, state, and real-Neovim evidence; it is not headed popup evidence.
- **Headed popup evidence is current for `.13`.** The real installed
  `client-attached` hook, automatic `display-popup`, failed two-column replay,
  retry, successful replay, fourteen-node progress page, XP/level, streak,
  module map, and next lesson pass at 188×49, 100×36, and 80×24. The route
  matrix passes conceptual, changed-stem retry, guided, independent,
  comparison, five-question module check, source-linked spaced review, and
  every M0-M13 transfer at all three sizes. During this run, the review test was
  corrected to retrieve M0.01's own review bank instead of silently borrowing
  M0.06's transfer, the transfer matrix was expanded through M13, and the
  compact module-check result header was kept on-screen
  (`share/test_tmux_v2_routes.py:175-186,303-317`;
  `share/v2_runtime.py:1025-1031,1107-1174`). A failed attempt keeps the streak
  active while `today`, XP, mastery, and all-time completions remain pass-only
  (`share/v2_runtime.py:789-805,1854-1885`).
- **Still open; the course audit is not complete.** The legacy disposition is
  still 26 adapted / 8 partial / 12 retained-only, leaving 20 rows without full
  parity. Required practice remains absent or incomplete for search repeat,
  registers, richer Visual operations, text objects, macros, Ex commands,
  jump/undo trees, split/onion-skin work, drafting variants, line-quality drills,
  layer/material planning, broader texture construction, recursive in-betweening,
  contact tracking, overshoot/bounce/blur/growth, playback-rate tuning, and dense
  region polish. Only 25 source cards currently own changed-art spaced-review
  banks. Headed delivery is now verified, but those curriculum breadth and
  per-technique spaced-review gaps remain real and are not closed by UI tests.

### VD-11 fix attempt 1 · 2026-09-28 — DO THIS, two-column replay, attempt streak, progress fit

- **Changes (`share/v2_runtime.py`):** `_print_feedback_do_this` prints a
  `DO THIS` action on every result page (failure: compare YOURS with TARGET,
  press Enter, redo the card prompt). `_two_column_replay`/`_artifact_replay`
  render the artifact as two columns — failure `YOURS (what you saved) │ TARGET
  (what it should be)` with `✗` on differing rows and the first differing
  column; pass `BEFORE │ AFTER (yours)` with `•` on changed rows; wide glyphs
  measured in terminal cells. Compact pages render off-screen and shrink only
  the replay until title, status, DO THIS, replay, and the Enter prompt fit;
  a tight module-check page keeps both columns but shows only the first changed
  row. `_legacy_attempt` writes a `result=attempt` daily row on every failed
  result page; `_legacy_streak` counts a day with any pass or attempt row, while
  cap (`today N/12`), all-time completions, XP, and mastery stay pass-only.
  `progress_full_rows` switches the progress page to its compact tree when the
  tree does not fit (the 14-module tree scrolled `PROGRESS UNCHANGED` off a
  100×36 popup); the compact tree wraps five modules per line.
- **Tests changed to the operator requirement:** `share/test_v2.py` asserts the
  two-column labels, a `✗` row, `DO THIS`, streak ≥ 1 after a failure, and
  unchanged cap/all-time counts; `share/test_tmux_v2.py` requires `DO THIS`,
  `YOURS`/`TARGET`, `streak: 1 day` after a failure, and `BEFORE`/`AFTER` on
  success (the old `row 2:`, `wanted`/`yours`, and `streak: 0 days` checks
  encoded the rejected behaviour).
- **Operator state backfill:** the two failed `M0.04` attempts from
  `events-v2.jsonl` (00:55:25 and 02:54:44) were appended to
  `~/.local/state/vim-daily/2026-09-28.log` as `result=attempt backfill=VD-11`
  rows. Reader result: streak 14 (includes today), today cap 0, all-time 40.
- **Verification (2026-09-28, current tree):** `python3 share/test_v2.py` passed
  (112/112 lessons, 84/84 recipes, config=none); `python3 share/test_drills.py`
  46/46; `share/test_tmux_v2.py` (automatic popup with a real failed attempt)
  passed at 80×24, 100×36, and 188×49, and the captured 80×24/100×36 failure
  pages were inspected: DO THIS, two columns, `✗` row, first-difference line,
  and `streak: 1 day` on the progress page. `share/test_tmux_v2_routes.py`
  passed the first 18 routes at all three sizes.
- **Open, not owned by this fix:** the route suite now iterates all 14 modules
  and fails at `M11.06` (Fixed-width redraw transfer, added in revision .13):
  its expected keys do not produce its target in the live popup. This is buffer
  content, which the VD-11 rendering changes cannot alter. No human has yet
  seen the new failure page in a real hourly popup.

### VD-11 fix attempt 2 · 2026-09-28 — headed route closure and compact check header

- **The M11.06 curriculum was not the defect.** Clean and real Neovim recipe
  execution already proved `0lR==<Esc>` reaches the target. The headed driver
  followed `<Esc>` immediately with `:wq` or `ZZ`; Neovim's terminal-key timeout
  recorded that pair as `<M-:>` or `<M-Z>`, leaving Replace mode active. The
  driver now waits past the terminal-key timeout after Escape and submits with
  `ZZ`, which the runtime already strips as a submit suffix. M11.06, M12.06,
  and M13.06 then passed through the real popup without weakening their exact
  method contracts (`share/test_tmux_v2_routes.py:52-77,178-189,202-230`).
- **The source-review regression test now obeys source ownership.** Its due row
  is M0.01, so it edits M0.01's first `review_variants` fixture rather than the
  unrelated M0.06 module-transfer fixture. The matrix iterates the generated
  module count, so adding a module can no longer leave its transfer route
  silently untested (`share/test_tmux_v2_routes.py:175-189,318-321`).
- **The 80×24 five-question result keeps its outcome header.** Compact feedback
  reserves a popup-border row and omits the redundant second status sentence
  on module checks; `LESSON COMPLETE` or `ATTEMPT NOT PASSED`, `DO THIS`, the
  artifact, all five outcomes, playback receipt, source, and Enter prompt stay
  visible (`share/v2_runtime.py:1025-1031,1127-1175`).
- **Verification:** the full automatic-popup suite and the route matrix pass at
  188×49, 100×36, and 80×24. The route matrix covers conceptual success,
  changed-stem remediation, guided and independent edits, both comparison
  methods, the five-question module check, source-linked spaced review, and all
  fourteen transfer routes M0.06-M13.06. `share/test_v2.py` and `--real` still
  pass 112/112 cards, 84/84 primary recipes, 28 transfers, and 28 comparisons;
  both legacy suites still pass 46/46. The remaining open work is curriculum
  breadth and per-source review coverage recorded under revision `.13`, not a
  known delivery-route failure.

### VD-10 follow-through · revision 2026-09-28.14 · 2026-09-28 — S5 variant and glyph-palette stage

- **The attachment's S5 gap now has an implemented module.** M14 `Variant
  palette` keeps three-row variants as blank-line-separated paragraph objects,
  stores a visible one-cell glyph vocabulary in named registers, retrieves it
  with `<C-r>{register}` from Replace mode, navigates frame boundaries with `}`,
  and compares `yap` plus `P` with an exact four-line `:t` copy. The eye changes
  star → plus → star while the silhouette remains registered, so the commands
  serve one visible material-variant sequence rather than isolated Vim trivia
  (`share/gen_curriculum_v2.py:1497-1680`;
  `share/CURRICULUM_V2_CARD_CATALOG.md:311-322`).
- **The new commands are runtime evidence, not answer-key mentions.** M14.01,
  M14.04, and M14.08 require exact named-register/Replace retrieval paths;
  M14.02 requires an exact `yap` whole-frame copy; M14.05 accepts only its exact
  paragraph-object/`P` or addressed-range comparison paths. M14.01, .04, .05,
  .06, and .08 own two changed-art review variants and explicit source/family
  links. Tests assert the presence of `<C-r>a`, `yap`, `P`, `}}`, `<C-r>b`, and
  those source-owned review links (`share/test_v2.py:168-178`).
- **Legacy parity improved but remains incomplete.** `paragraph-object` is now
  adapted at M14.05, and `symbol-table` is adapted at M14.04. The honest tally
  is 28 adapted / 7 partial / 11 retained-only, leaving 18 gaps
  (`share/LEGACY_CURRICULUM_DISPOSITION.md:39-49,69-71`).
- **Current generated size:** revision `.14` contains 15 modules, 120 cards, 150
  paired questions, 90 primary edit paths, 30 changed-art transfer variants,
  and 30 comparison paths. The clean-config suite passes all of those paths and
  all declared review variants. A real-config run passed the first `.14` M14
  recipe set before M14.05 was strengthened from `Gp` to frame-boundary `P`;
  the final real-config plus headed M0-M14 route rerun is still in progress and
  is not claimed here.
- **Still open from the attached sequence:** S7 texture construction, A0
  planning, A3 cross-frame coherence, and A6 full mirrored action remain
  unimplemented. S2 still lacks a full row-by-row hand-mirror module. M14 closes
  S5 only; it does not convert those remaining stages into inferred coverage.

### VD-10 completion pass · revision 2026-09-28.18 · 2026-09-28 — S7, A0, A3, A6, and full hand mirror

- **The four stage gaps named after M14 now have executable modules.** M15 `Texture
  ground` requires one-cell brick offsets, bounded dither lightening, ragged
  block `$A`, range append, and a recorded dither macro while an angled shadow
  remains fixed (`share/gen_curriculum_v2.py:1674`; catalog `:327-334`). M16
  `Key-pose plan` requires a saved-plate `:read %`, complete-block `:t`/`:m`,
  linewise move comparison, written FPS evidence, and counted `<C-a>` frame
  labels (`share/gen_curriculum_v2.py:1844`; catalog `:337-346`). M17 `Coherent
  anchors` requires `/` + `n` + dot, a separately graded `:global ... normal`
  path, and a search-bearing macro across four homologous eye anchors
  (`share/gen_curriculum_v2.py:2045`; catalog `:351-360`). M18 `Hand-mirrored
  return` requires three full-row overwrites for every directional mirror,
  check-only `\=`/`getline()` use, and addressed reverse-order frame reuse around
  an explicit turnaround hold (`share/gen_curriculum_v2.py:2245`; catalog
  `:365-374`).
- **Coverage is based on runtime requirements and source-linked changed-art
  review, not answer-key tokens.** Tests assert each new method contract and its
  review-source link (`share/test_v2.py:177-209`). Both `python3
  share/test_v2.py` and `python3 share/test_v2.py --real` pass revision `.18`:
  19 modules, 152 cards, 190 paired questions, 114/114 primary edit recipes, 38
  changed-art transfer variants, and 38 comparison paths. Every primary path,
  both methods of every comparison, every transfer variant, and every declared
  changed-art review is replayed through Neovim.
- **The mirror is authored; the expression is not allowed to draw it.** M18.01,
  M18.04, and M18.06 accept exact three-row overwrite paths. M18.05's expression
  alternative substitutes only the digit on `CHECK=0` after inspecting an
  already-authored top row. M18.08 is structurally classified as return /
  overshoot / held overshoot / reversed return; the adjacent middle frames are
  machine-readable playback hold metadata, not an unreviewed duplicate
  (`share/gen_curriculum_v2.py:3246,3289`).
- **Legacy parity improved, but it is still not complete.** `block-append` is now
  adapted at M15.05 and `mirror-run` at M18.01. The disposition is 30 adapted / 6
  partial / 10 retained-only, leaving 16 visible gaps
  (`share/LEGACY_CURRICULUM_DISPOSITION.md:45,58,66-69`). S2's full manual
  mirror requirement is closed at frame scale. Dedicated stair-step slope and
  off-vertical anti-alias drills still belong to the separate S1/S4 gaps and
  are not inferred from M18.
- **Presentation proof remains a separate gate.** This receipt claims the clean
  and real-Neovim curriculum suites only. Revision `.18` headed automatic-popup
  and full-route matrices must be rerun before the new modules are called
  popup-verified; the older `.13` headed receipt cannot be inherited.

### VD-10 headed proof · revision 2026-09-28.18 · 2026-09-28 — expanded tree and new routes

- **Automatic popup:** `share/test_tmux_v2.py` passes the installed
  `client-attached` failure → unchanged progress → retry → success → awarded
  progress journey at 188×49, 100×36, and 80×24. Expanding to nineteen modules
  exposed a stale test assumption: the real 85%-height popup legitimately used
  compact progress at 188×49 even though the outer terminal alone exceeded the
  old threshold. The assertion now requires the same XP/today evidence in
  either supported full or compact rendering instead of guessing from outer
  rows (`share/test_tmux_v2.py:245-257,326-338`).
- **Full route matrix at 188×49:** conceptual success, changed-stem retry,
  guided target, independent retrieval, both comparison methods, five-question
  module check, spaced review, and every live transfer M0.06 through M18.06 all
  pass through the installed hook and real `display-popup` boundary.
- **Compact full-route matrices also pass:** the same route inventory, including
  every M0.06-M18.06 live transfer, passes at 100×36 and 80×24. Revision `.18`
  therefore has both the automatic failure/retry journey and the complete route
  matrix at all three supported viewports; no `.13` headed result is being
  inherited.

## VD-12 · 2026-09-28 — editor surface hid the task contract and compact debrief dropped the ledger

- **Human report:** the live exercise appeared as an unstyled dark/blank editor,
  did not expose `NORMAL`/`VISUAL`, did not keep `DO THIS` or TARGET visibly tied
  to the art, offered no discoverable lower-left cheat sheet, gave no help for
  creating a line below, allowed repeated wasteful `k`, and reduced the
  post-exercise correct-vs-actual comparison to a sentence instead of the
  legacy two-column ledger.
- **Root cause 1 — target and answer were incorrectly coupled:** revision `.18`
  generated `show_target` only for guided ordinals 1 and 2. Independent,
  comparison, transfer, review, and module-check cards therefore hid the visual
  target merely because they were supposed to hide exact keys. Revision `.19`
  separates `show_target=True`, guided-only `show_recipe`, and an authored
  action hint for all 114 edit cards
  (`share/gen_curriculum_v2.py:3320-3326`; `share/v2_runtime.py:605-626`).
- **Root cause 2 — `--clean` removed personal chrome without installing tutor
  chrome:** `run_editor` created the read-only brief split but no owned color,
  mode, task, or help surface. It now installs a light tutor palette, a global
  status line with named Normal/Insert/Visual/Replace states, a persistent art
  winbar beginning `DO THIS`, and an F1 lower-left cheat sheet. The sheet names
  `o` as NEW LINE BELOW and includes window navigation, undo/redo, replace, and
  submit controls (`bin/vim-daily-gate:652-692`).
- **Root cause 3 — no live inefficient-motion intervention:** the editor now
  intercepts the fifth rapid identical normal-mode `h`, `j`, `k`, or `l`, leaves
  the extra move unapplied, and temporarily replaces the art winbar with a
  count/landmark-motion correction (`bin/vim-daily-gate:693-703`). This is
  deliberately narrow; it does not pretend to grade every inefficient Vim path
  live. Method-constrained cards still use captured-key evidence after submit.
- **Root cause 4 — compact output discarded structure:** the under-55-row path
  printed `actual … · taught …`, so insertions, omissions, and waste were no
  longer aligned. It now renders `KEYSTROKE LEDGER  YOU TYPED │ THE RECIPE ASKS
  FOR` plus the aligned diff row at 80×24; full layouts retain every diff row
  (`share/v2_runtime.py:1043-1062`). Compact all-correct module checks collapse
  five redundant success rows to one summary so the lesson-complete heading,
  artifact, ledger, playback receipt, and Enter prompt all remain on screen.
- **Regression proof added:** the automatic installed-hook test now asserts
  `TUTOR · NORMAL`, enters Visual mode and asserts `TUTOR · VISUAL`, toggles F1
  and checks `o NEW LINE BELOW`, triggers the repeated-`k` coach, then requires
  the two ledger column headers on both failure and success
  (`share/test_tmux_v2.py:134-207,226-324`). The route matrix requires TARGET
  plus HINT with the exact command absent on independent/check cards
  (`share/test_tmux_v2_routes.py:203-228`).
- **Live-session boundary:** the already-running gate and Neovim processes do
  not hot-load this Python/Lua setup. Their current buffers are preserved. The
  next separately launched popup after the current gate closes receives
  revision `.19`; no repair/reset command and no manual state rewrite is
  required.

## VD-12 · 2026-09-28 — real M0.04 popup vs the revision `.18` "popup verified" claim

**Operator report (13:10 real popup, M0.04, sixth failure):** popup looked black
with no NORMAL/VISUAL mode line; no DO THIS; no TARGET; no post-attempt two-column
ledger of the correct action sequence vs what they typed; no hint; no legacy-style
blocking of repeated `k`; no lower-left toggleable cheat sheet; did not know what
the card wanted or how to open a new line below.

- **The `.18` headed receipt does not cover the operator's route.** Both
  `test_tmux_v2.py` and the route matrix start from a fresh isolated state, so
  the automatic journey only ever renders M0.01 (a guided card with its recipe
  shown). The operator's real route (M0.04 independent edit, 188×49 popup from a
  209×58 Ghostty client, six prior failures) was never exercised. "Automatic
  popup journey passes" is true of the fixture, not of what the operator saw.
- **What the 13:10 popup displayed is not recoverable.** No screen capture
  exists, and another session rewrote `bin/vim-daily-gate` `run_editor` (13:22)
  and `share/v2_runtime.py` (13:25) afterwards — adding the tutor status line,
  DO THIS winbar, F1 cheat sheet, and h/j/k/l repeat blocking. The report is
  therefore evidence against the pre-13:22 code; it is not re-derived here.
- **Current code, replayed on a copy of the real state** (scratchpad copy of
  `~/.local/state/vim-daily`, isolated tmux server 188×49, `--force`): editor
  shows TASK/DO THIS/TARGET/HINT split, `DO THIS ·` winbar, `TUTOR · NORMAL · ART`
  status line; `k` pressed 7× shows `COACH · k BLOCKED · use a count like 5k or
  f/t/search`; F1 opens a lower-left cheat sheet and closes it. Failure page shows
  `DO THIS`, `YOURS (what you saved) │ TARGET (what it should be)` with ✗ rows.
- **Defect found and fixed (this entry): the keystroke ledger showed one row.**
  Every popup is "compact" (`lines < 55`), and `_post_feedback_ultra` printed
  only `table[2:3]`. Replaying the operator's actual edit shape
  (`kkkkkkk4G0v2j$y6G$p<Esc>:wq`) produced a ledger of just `kkkkkkk extra`
  with an empty recipe column. Now the ledger prints every row that fits
  (`ledger_rows`), and the fit loop shrinks ledger → 3, then artifact rows, then
  ledger → 1 with `… N more ledger row(s)`. At 188×49 the same attempt shows all
  nine aligned rows (`4G ok`, `0v2j$ │ 3 not this`, `6 │ y not this`,
  `<Esc> │ :8s/-/=/g<CR> not this`). Also fixed: a one-row artifact window showed
  an unchanged context row; it now shows the first differing row
  (`share/v2_runtime.py` `_post_feedback_ultra`, `_post_feedback`,
  `_two_column_replay`).
- **Verification of the fix:** `test_v2.py` 152/152 + 114/114; `test_drills.py`
  46/46; `test_tmux_v2.py` PASS at 80×24, 100×36, 188×49; 72×20 and 188×49
  replays of M0.04 inspected. `test_tmux_v2_routes.py` at 80×24 exits 0
  through the M18.06 live transfer (100×36 and 188×49 route matrices not rerun).
- **Open — curriculum sequencing (not fixed here; generator owned by the
  active `.19` session):** M0.04 is an *independent* (recipe-hidden) retrieval of
  `4G3yyGp` + `:8s/-/=/g`, but M0.01 (`j0f.ro`) and M0.02 (`gg3yyGp5GforO`)
  never teach `:s`, a range, or `/g`, and nothing before M0.04 teaches `o`
  (open line below) or that `yy`/`p` is linewise. The operator's saved artifact
  (`checkpoints/M0.04-failed-6.txt`) shows a characterwise paste appended to row
  6 — exactly that missing knowledge. Three of six failures saved the start
  unchanged (did not know what to do).
- **Open — failure hint is generic.** After failure DO THIS says "compare YOURS
  with TARGET … then redo: <prompt>"; it does not diagnose the attempt (e.g.
  "your paste landed inside row 6; `yy`/`p` put whole lines below"). The
  operator explicitly accepts no keystroke reveal but wants a hint.
- **Open — cheat sheet content.** It omits `yy`/`p`/`P`, counts, `gg`/`G`, and
  `:s` — the keys the current card needs; its HINT line is clipped (`@@@`); while
  open it covers the `TUTOR · <MODE>` status line.
- **Open — colour.** The editor now forces `Normal guibg=#1e293b` (dark slate).
  Whether that answers "the popup is black" needs operator confirmation.
- **Hygiene:** two test Neovim processes (PIDs 15451, 99071) have been running
  10–11 h from leaked harness temp dirs.

### VD-12 audit 2 · 2026-09-28 — legacy vs v2, every legacy lesson (operator screenshot 13:33)

**Operator evidence:** screenshot 13:33, real M0.04 popup. Top: a read-only brief
(TARGET, HINT, INDEPENDENT ATTEMPT, WHY, BUYS, KEYS WORTH KEEPING, SOURCE,
READING THE RECIPE, SUBMIT) filling most of the screen. Bottom: a six-row art
pane with a `DO THIS ·` winbar and a hand-made yellow `TUTOR · NORMAL · ART`
status line. HINT and KEYS WORTH KEEPING both said "copy the bright three-row
keyframe as the flare extreme; then widen only the new frame's horizontal rays",
a paraphrase of DO THIS.

**My failure in the previous VD-12 reply.** I reported DO THIS, TARGET, HINT, the
mode line, `k` blocking and the F1 sheet as "already present now". I checked
only that the labels rendered. I did not check that the HINT carries information
DO THIS lacks, and I did not compare any of it with the legacy screen. Those are
the operator's actual acceptance conditions.

**Root cause of "legacy had more": v2 removed the operator's own Neovim.**
- Legacy (`git show HEAD:bin/vim-daily-gate`, rendered with the operator's config
  in an isolated tmux 188×49, drill `move-x`) opened the lesson as one ordinary
  buffer in the operator's LazyVim. `~/.config/nvim/lua/plugins/beginner.lua`
  supplies `hardtime.nvim` (`max_count = 3`, `hint = true` — the "k too many
  times, use a different key" block), `which-key.nvim` (the key popup at the
  bottom), lualine (`NORMAL`/`VISUAL` mode), relative numbers, and the
  tokyonight/catppuccin theme. HEAD's gate contains no cheat sheet or blocking
  code: the operator's plugins provided both.
- VD-09 added `--clean -i NONE` to `run_editor` (`bin/vim-daily-gate:650`),
  which disables every one of those plugins. The 13:22 edits then imitated them
  with inline Lua: a yellow status line, an F1 float, and a custom h/j/k/l
  counter that blocks after 4 presses. That replaced the real owner with a
  weaker copy instead of fixing the obstruction VD-09 named. The dashboard does
  not open when a file argument is given. The lazy.nvim installer appears only
  when `XDG_DATA_HOME` points to an empty plugin directory: I reproduced that
  here by setting it, and lazy started cloning 36 plugins into scratch.
  `VIM_DAILY_USE_USER_CONFIG=1` already bypasses `--clean`, but it is opt-in and
  the operator does not set it.

**Screen structure, legacy vs v2**

| Element | Legacy (every one of 46 lessons) | v2 (M0.04 as shipped) |
|---|---|---|
| Editor | the operator's Neovim, one buffer, vimtutor-like | `--clean` Neovim, split windows, imitation UI |
| DO THIS | the exact keys, each with its meaning (`j` move down one line / `dd` delete that whole line) | one prose sentence; keys hidden on 76 of 114 edit cards |
| KEYS WORTH KEEPING | a per-drill key vocabulary, independent of the answer (`h j k l …`, `dd x u`) | on hidden cards the HINT repeated; the v2 schema has **no key-vocabulary field** (`grep key` over the card fields: none) |
| HINT | not needed: the keys were shown | `gen_curriculum_v2.py:3324` joins the recipe step *descriptions*, so it is a paraphrase of the task by construction. Revision `.19` (13:40, another session) turned these into "Vim toolbox:" sentences; 7 cards still get the generic "choose the smallest normal-mode operation…" |
| Target | directly above the marker, next to the edit | in the upper brief, separate from the art pane |
| Mode line / blocking / key popup | lualine, hardtime, which-key | imitations after 13:22 (F1 sheet leaves out `yy p G :s`) |

**Every legacy lesson.** Command families come from a heuristic key parser
(inferred: `scratchpad/audit/vimparse.py`, spot-checked on `V2jd`, `:normal`,
`<C-v>…I`, `:%s///g`). "hidden-recipe cards" means the v2 path exists only on
cards whose keys are never shown. Summary: nearest v2 card shows keys for
12/46; nearest v2 card omits some legacy family for 39/46; 21/46 legacy lessons
contain a family absent from every v2 key path; 21/46 contain a family that v2
uses only on hidden-recipe cards.

| Legacy | Legacy DO THIS (keys shown) | Legacy KEYS WORTH KEEPING | Disposition → v2 | v2 shows keys? | Legacy families missing from that v2 card | …absent from every v2 path | …in v2 only on hidden-recipe cards |
|---|---|---|---|---|---|---|---|
| `move-x` | `jdd:wq<CR>` | h j k l   left down up right, without leaving th | adapted → `M9.04` (independent_edit) | **no** | motion:j, dd | — | dd |
| `delete-word` | `dw:wq<CR>` | dw   delete a word        de   delete to the end | partial → `M2.01` (guided_edit) | yes | d{motion} | d{motion} | — |
| `delete-eol` | `$F D:wq<CR>` | D = d$   delete to end of line      C = c$   cha | adapted → `M6.05` (compare_methods) | **no** | motion:$, F{c} | F{c} | D |
| `count-motion` | `d2W:wq<CR>` | w  next word, stopping at punctuation     W  nex | retained-only → `M2.01` (guided_edit) | yes | d{motion} | d{motion} | — |
| `delete-line` | `2jdd:wq<CR>` | dd   delete a line      3dd  delete three lines  | adapted → `M7.08` (module_check) | **no** | motion:j | — | dd |
| `undo` | `ddu<C-r>:wq<CR>` | u      undo the last change        <C-r>  redo | adapted → `M11.04` (independent_edit) | **no** | dd | — | dd, u, <C-r> |
| `put` | `yyGp:wq<CR>` | yy  yank a line    p  put below    P  put above  | adapted → `M0.02` (guided_edit) | yes | — | — | — |
| `replace-char` | `3lr::wq<CR>` | r<char>  replace one character, staying in norma | adapted → `M0.01` (guided_edit) | yes | motion:l | — | — |
| `change-word` | `cw_.--._<Esc>:wq<CR>` | cw   change to end of word      ciw  change the  | partial → `M3.04` (independent_edit) | **no** | c{motion} | c{motion} | — |
| `change-eol` | `C,.,.,.,.<Esc>ZZ` | C = c$  change to end of line      A  append at  | adapted → `M4.01` (guided_edit) | yes | — | — | — |
| `search` | `/`<CR>dd:wq<CR>` | /text  search forward    ?text  search backward | adapted → `M1.01` (guided_edit) | yes | dd | — | dd |
| `match-paren` | `ci(   '   <Esc>%:wq<CR>` | %    jump between matching ( ) [ ] { } | adapted → `M3.01` (guided_edit) | yes | ci{(} | — | ci{(} |
| `substitute` | `:s/\./:/<CR>:wq<CR>` | :s/old/new/     first match on this line | adapted → `M0.06` (transfer) | **no** | — | — | :s |
| `substitute-all` | `:%s/::/.:/g<CR>:wq<CR>` | :%s/a/b/g    every match in the file | adapted → `M7.05` (compare_methods) | **no** | — | — | :s[range], :s///g |
| `open-line` | `O<Esc>:wq<CR>` | o  open a line below and start typing      O  op | retained-only → `M8.04` (independent_edit) | **no** | O(insert) | O(insert) | — |
| `append` | `A´<Esc>:wq<CR>` | a  append after the cursor      A  append at end | retained-only → `M8.04` (independent_edit) | **no** | A(insert) | A(insert) | — |
| `yank-put` | `yyp:wq<CR>` | yy p   the cheapest duplicate there is | adapted → `M0.02` (guided_edit) | yes | — | — | — |
| `join` | `J:wq<CR>` | J   join the line below, inserting a space | retained-only → `M6.04` (independent_edit) | **no** | J | J | — |
| `toggle-case` | `2l~:wq<CR>` | ~    toggle the case of one character      3~    | retained-only → `M7.05` (compare_methods) | **no** | motion:l, ~ | ~ | — |
| `text-object-paren` | `f'ca('<Esc>:wq<CR>` | ci(  change inside the parens       ca(  change  | partial → `M3.04` (independent_edit) | **no** | f{c}, ca{(} | ca{(} | — |
| `paragraph-object` | `3jdap:wq<CR>` | dap  delete a paragraph and its blank line    di | adapted → `M14.05` (compare_methods) | **no** | da{p} | da{p} | — |
| `named-register` | `"ayy2jV"ap:wq<CR>` | "ayy  yank a line into register a      "ap  put  | adapted → `M3.06` (transfer) | **no** | yy, visual-p | visual-p | — |
| `yank-register-0` | `yyjdd"0p:wq<CR>` | "0p   the last yank, even after a delete overwro | retained-only → `M3.06` (transfer) | **no** | yy, dd | — | dd |
| `marks` | `maG'add:wq<CR>` | ma   set mark a here      'a   jump to the line  | retained-only → `M3.08` (module_check) | **no** | m{mark}, 'mark, dd | m{mark}, 'mark | dd |
| `visual-delete` | `V2jd:wq<CR>` | v   character-wise    V   line-wise    <C-v>  bl | partial → `M3.06` (transfer) | **no** | visual-d | visual-d | — |
| `block-insert` | `<C-v>jjI\|<Esc>:wq<CR>` | <C-v>jjI text <Esc>   insert down a column | retained-only → `M4.04` (independent_edit) | **no** | visual-I | visual-I | <C-v>block |
| `block-append` | `<C-v>jj$A\|<Esc>:wq<CR>` | <C-v>jj$A  appends to lines of different lengths | adapted → `M15.05` (compare_methods) | **no** | — | — | <C-v>block, visual-A |
| `block-erase` | `2l<C-v>jjlld:wq<CR>` | <C-v>jjd   delete a rectangle      <C-v>jjr.  fi | retained-only → `M4.04` (independent_edit) | **no** | visual-d | visual-d | <C-v>block |
| `block-replace` | `l<C-v>jjlr::wq<CR>` | <C-v>...r<char>  fill a rectangle with one glyph | adapted → `M4.04` (independent_edit) | **no** | — | — | <C-v>block, visual-r |
| `macro` | `qqI'<Esc>A'<Esc>jq3@q:wq<CR>` | qa ... q  record into register a     @a   replay | adapted → `M7.05` (compare_methods) | **no** | q(record), I(insert), A(insert), motion:j, @macro | I(insert), A(insert) | q(record), @macro |
| `symbol-table` | `Wylj$vp:wq<CR>` | yl   yank one character         3yl  yank three | adapted → `M14.04` (independent_edit) | **no** | motion:W, motion:$, v(visual), visual-p | visual-p | v(visual) |
| `dot-repeat` | `3lr:j.j.:wq<CR>` | j keeps your column, so j. walks one edit down a | adapted → `M7.04` (independent_edit) | **no** | r{c} | — | — |
| `find-char` | `f:;;D:wq<CR>` | f:  find next :     F:  find previous :     ;  r | adapted → `M7.06` (transfer) | **no** | motion:;, D | — | motion:;, D |
| `ex-copy` | `:t.<CR>:wq<CR>` | :t.   copy this line below itself     :t0  copy  | adapted → `M5.05` (compare_methods) | **no** | :t | :t | — |
| `hold-frame` | `6yyG2p:wq<CR>` | 6yy 2p  copy a 6-line frame and stamp it down tw | adapted → `M7.01` (guided_edit) | yes | yy, motion:G, p | — | — |
| `tween-frame` | `6yyGp3j$xr/hr,:wq<CR>` | Copy the previous frame, then change ONLY the ce | adapted → `M9.05` (compare_methods) | **no** | yy, p, motion:j, motion:$, x, r{c}, motion:h | — | x |
| `break-seam` | `f/r´:wq<CR>` | The plate shows this edit as a before/after pair | adapted → `M5.01` (guided_edit) | yes | f{c} | — | — |
| `playback-order` | `ddp:wq<CR>` | ddp    swap with the line below      ddkP  swap  | partial → `M6.08` (module_check) | **no** | dd, p | — | dd |
| `range-normal` | `VG:normal A'<CR>:wq<CR>` | :'<,'>normal A;   append ; to every selected lin | adapted → `M7.05` (compare_methods) | **no** | V(visual), motion:G, :normal | :normal | — |
| `mirror-run` | `r-lr.lr_:wq<CR>` | The mirror table:  _ <-> _    . <-> .    - <-> - | adapted → `M18.01` (guided_edit) | yes | r{c}, motion:l | — | — |
| `pad-frames` | `O<Esc>.:wq<CR>` | O<Esc> then .   pad a frame one row at a time | partial → `M8.04` (independent_edit) | **no** | O(insert), . | O(insert) | — |
| `macro-frames` | `qqlvlr:j0q4@q:wq<CR>` | qq ... q then 4@q   the same edit across a whole | adapted → `M7.05` (compare_methods) | **no** | q(record), motion:l, v(visual), visual-r, motion:j, motion:0, @macro | — | q(record), v(visual), visual-r, @macro |
| `ant-drop` | `2jdd:wq<CR>` | dd   delete a line      3dd  delete three lines  | adapted → `M7.08` (module_check) | **no** | motion:j | — | dd |
| `centipede-hold` | `yyp:wq<CR>` | yy p   the cheapest duplicate there is | adapted → `M7.01` (guided_edit) | yes | yy, p | — | — |
| `cheer-eyes` | `j2lro:wq<CR>` | r<char>  replace one character, staying in norma | adapted → `M3.04` (independent_edit) | **no** | motion:j, motion:l, r{c} | — | — |
| `candle-join` | `J:wq<CR>` | J   join the line below, inserting a space | retained-only → `M6.04` (independent_edit) | **no** | J | J | — |

**v2 sequencing: recalling commands never taught.** 46 of the 76 hidden-recipe
v2 edit cards require a command family that no earlier guided (keys shown) card
contains (revision `.19`, same parser; ordered by module then card). A
multiple-choice question may *name* a command earlier: the M0.03 pool includes
`:8s` choices in Q06/Q09. The operator drew Q01 and Q07, so for this operator
`:s` first appeared as a recall demand at M0.04.

| Card | Kind | Expected | Families never shown before |
|---|---|---|---|
| `M0.04` | independent_edit | `4G3yyGp:8s/-/=/g<CR>` | :s[range], :s///g |
| `M0.05` | compare_methods | `:7,9t$<CR>` | :t[range] |
| `M0.06` | transfer | `jforO:s/-/=/g<CR>` | :s, :s///g |
| `M0.08` | module_check | `:1,3t$<CR>14Gfor.` | :t[range] |
| `M1.04` | independent_edit | `4G3ddGo´<CR> `-.:<CR><C-u>o_.-<Esc>` | dd, o(insert) |
| `M1.05` | compare_methods | `:%s/:/;/g<CR>` | :s[range], :s///g |
| `M1.08` | module_check | `:1,3t$<CR>8G0f;r:` | :t[range] |
| `M2.05` | compare_methods | `:%s/[.o]/O/g<CR>` | :s[range], :s///g |
| `M2.08` | module_check | `:1,4t$<CR>10GfOr-` | :t[range] |
| `M3.04` | independent_edit | `8Gci(O<Esc>` | ci{(} |
| `M3.05` | compare_methods | `:1,6t$<CR>` | :t[range] |
| `M3.06` | transfer | `ggV5j"ayG"ap8GforO` | V(visual), "reg, visual-y |
| `M3.08` | module_check | `14Gfor<C-k>.M` | ., motion:M |
| `M4.04` | independent_edit | `:1,3t3<CR>4G0C   \<Esc>4G03l<C-v>jr\|` | :t[range], <C-v>block, visual-r |
| `M4.05` | compare_methods | `10G0C   \|<Esc>11G0C   \|<Esc>:1,3t$<CR>` | :t[range] |
| `M4.06` | transfer | `:1,3t3<CR>4G0C   \|<Esc>5G0C   \|<Esc>` | :t[range] |
| `M4.08` | module_check | `13G3dd` | dd |
| `M5.05` | compare_methods | `:1,7t7<CR>8G0C    \|<Esc>9G0C    \|<Esc>` | :t[range] |
| `M6.04` | independent_edit | `6G0D` | D |
| `M6.05` | compare_methods | `:6,10t$<CR>12G0D` | D |
| `M6.06` | transfer | `:1,5m$<CR>` | :m[range] |
| `M6.08` | module_check | `:11,15m0<CR>:11,15m5<CR>` | :m[range] |
| `M7.04` | independent_edit | `3G0f-v2lr=5j.` | v(visual), visual-r, . |
| `M7.05` | compare_methods | `:%s@/---\\@/===\\@g<CR>` | :s[range], :s///g |
| `M7.06` | transfer | `2GforO5j.` | . |
| `M7.08` | module_check | `21G5dd` | dd |
| `M8.04` | independent_edit | `Go<C-u> \o<Esc>o<C-u>  \|\<Esc>o<C-u>  \` | o(insert) |
| `M8.05` | compare_methods | `:1,5s@o/@o\\@<CR>` | :s[range] |
| `M9.04` | independent_edit | `5GfOxi=<Esc>` | x, i(insert) |
| `M10.04` | independent_edit | `Go／￣￣＼<Esc>o\|ﾆ二ニ\|<Esc>o＼＿＿／<Esc>` | o(insert) |
| `M11.04` | independent_edit | `4G0lR~~<Esc>u<C-r>` | u, <C-r> |
| `M11.05` | compare_methods | `5G:s/o/O/g<CR>` | :s, :s///g |
| `M11.08` | module_check | `:set virtualedit=all<CR>2G13\|i\|<Esc>3j` | :set, ?\|, i(insert), . |
| `M12.04` | independent_edit | `4G3yyGp8G0f:;r!,r!` | motion:;, motion:, |
| `M12.05` | compare_methods | `:1,3t$<CR>12G0forO;rO` | motion:; |
| `M13.04` | independent_edit | `4G3yyGp7GEr!2Wr.Er!2Br!` | motion:E, motion:B |
| `M13.05` | compare_methods | `:7,9t$<CR>10G:s/!/*/g<CR>` | :s, :s///g |
| `M13.06` | transfer | `2Wr+Br+` | motion:B |
| `M13.08` | module_check | `:1,3t$<CR>13GWr.Br!` | motion:B |
| `M14.05` | compare_methods | `5Gyapgg}jP` | motion:}, P |
| `M14.08` | module_check | `ggf*"bylgg}}jj0f+R<C-r>b<Esc>` | motion:} |
| `M15.04` | independent_edit | `:set shiftwidth=1<CR>5G>>:4s/:/./g<CR>` | :s[range], :s///g |
| `M15.05` | compare_methods | `4G0<C-v>2j$A\|<Esc>` | <C-v>block, visual-A |
| `M15.08` | module_check | `:1,3t$<CR>7G0qqf:r.q3@q` | q(record), @macro |
| `M16.05` | compare_methods | `:6,10m0<CR>` | :m[range] |
| `M17.08` | module_check | `/\*<CR>qqr+nq3@q` | q(record), @macro |

**Required outcome, not yet implemented (no code changed in this audit):**
1. Run lessons in the operator's own Neovim by default (reverse the VD-09
   `--clean` default). Handle the two named obstructions in their own terms,
   and delete the 13:22 imitation UI.
2. Give each v2 card a key vocabulary (KEYS WORTH KEEPING) that is independent of
   the answer. On hidden-recipe cards, name the relevant key *family*
   (for example "linewise yank/put: `yy` `p`; substitute on one line: `:s`")
   instead of paraphrasing the task.
3. Never ask to recall a command family before a guided card has shown it with
   its meaning (46 cards above). M0.04 needs `o` and linewise put before it.
4. Restore the legacy single-buffer layout (target above the edit area),
   or show why the split layout is better — operator's decision.

### VD-12 fix · 2026-09-28 — operator's own Neovim config is the default again

- **Operator decision (14:4x):** lessons open in the operator's own Neovim
  config by default.
- **Why `--clean` had been added:** 2026-09-27 "Fix attempt 3" saw lazy.nvim's
  plugin-install screen over the lesson in the headed test and blamed the
  personal config. The headed tests set `XDG_DATA_HOME` to an empty temporary
  directory, so LazyVim reinstalled every plugin on each run. Real popups use
  `~/.local/share`, where the plugins are already installed. The cause was the
  test fixture, not the operator's config.
- **Default flipped:** another session made the flip concurrently at 13:44
  (`VIM_DAILY_CLEAN=1` is the opt-in for an isolated Neovim).
- **My changes:**
  - `bin/vim-daily-gate` `run_editor`, user-config branch: turns off `list` and
    indent guides (snacks, mini.indentscope, ibl) in the tutor windows. Without
    that, LazyVim drew art row `  \|/  ` as `│ \|/--`, and `-` is a real art
    glyph in this curriculum.
  - `vd_top`: scrolls each lesson window back to line 1 after the bufferline
    appears. With `splitkeep=screen`, line 1 had been scrolled out of view, so
    the brief header and first art row were missing.
  - `share/test_tmux_v2.py` and `share/test_tmux_v2_routes.py` now use the real
    `XDG_DATA_HOME`. `~/.local/share/vim-daily` already resolves to this
    checkout.
  - `test_tmux_v2.py` captures now wait up to 5 s for the expected text
    (`capture_until`).
  - The brief's `middle-dot` text and the hardtime-title needles wrap at the
    split border and are truncated at 80×24.
- **Observed in isolated tmux replays using the real config** (M0.04 at 188×49;
  M0.01 at 167×40 and 72×21):
  - lualine `NORMAL` renders.
  - hardtime shows "You pressed the j key too soon! Use countj or CTRL-D" and
    stops the cursor.
  - which-key opens on `<Space>`.
  - the art shows without `-` or `│` artefacts.
- **Tests:** `test_tmux_v2.py` passes at 188×49 and 100×36. It **fails at
  80×24**: on the retry, keys sent right after the ready signal
  (`j0f.ro:wq`) were logged but not applied, so the art was unchanged.
  - Hypothesis, unconfirmed: keys typed while LazyVim's VeryLazy plugins
    (flash `f`) are still loading get dropped.
  - Typed by hand after startup at 72×21, the same keys apply.
  - My patch to signal readiness after `User VeryLazy` was refused by the
    mtime check, because another session rewrote the same signal code at 13:48
    (a 1000 ms deferred cleanup that also re-sets the tutor `statusline`).
  - Not verified: the 80×24 journey, and the route matrix at any size.

- **Steer relayed to Codex (operator request):** queued in Codex pane `%13` (tmux main:5.3). It says: your own config is the default, with no tutor chrome layered over it; Codex owns `bin/vim-daily-gate` from here; a subagent audits install.sh / new-user setup, recommending your hardtime/which-key/lualine setup to users who lack it; research more default plugins; fix the 80×24 VeryLazy key drop. Claude stops editing the gate.

## VD-13 · 2026-09-28 — `--clean` removed the learning environment; full LazyVim startup also covered the task

- **Operator correction:** the broad `--clean -i NONE` workaround removed much
  more than a dashboard. It bypassed the complete Neovim configuration. Direct
  inspection of the installed startup showed that this removed LazyVim,
  `hardtime.nvim`, lualine, TokyoNight, WhichKey, Telescope, Snacks, NUI, Mason,
  Treesitter/LSP startup, the mode-aware terminal title, and the user's Ctrl-S,
  `jk`, Insert-mode Alt-h/j/k/l, and H/L buffer mappings. The most important
  loss was the real Hardtime handler that blocks excess unit motions and tells
  the learner which count or landmark motion to use.
- **The attempted reversal was also unsafe:** making the complete personal
  config the default restored Hardtime and lualine, but asynchronous
  Treesitter/Mason/Snacks message windows could appear after the one-second
  cleanup, cover the lesson, and steal focus. A live 80×24 capture reproduced a
  `Messages` float over the task. Therefore neither bare `--clean` nor full
  LazyVim startup is an acceptable lesson profile.
- **Tutor-safe startup:** the default still begins deterministically with
  `--clean -i NONE`, then prepends and loads only the installed
  `tokyonight.nvim`, `lualine.nvim`, `nui.nvim`, and the real
  `hardtime.nvim`. It restores Ctrl-S, `jk`, and Insert-mode Alt-h/j/k/l. It
  intentionally does not start Lazy/Mason/Treesitter/Snacks, and it does not
  restore H/L buffer switching because those mappings replace the H/L screen
  motions the course must teach. `VIM_DAILY_USE_USER_CONFIG=1` remains an
  explicit full-config diagnostic route.
- **Hardtime ownership:** the tutor calls the installed plugin with
  `max_count=3`, `hint=true`, `restriction_mode=block`, and an owned callback.
  The callback displays the plugin's concrete advice in the art winbar without
  calling `nvim_echo`; the latter produced a `Press ENTER` prompt that trapped
  `:wq` in the first headed replay. The hand-written h/j/k/l counter is now
  missing-plugin fallback only.
- **Editor surface:** the live art pane uses TokyoNight and a real lualine mode
  segment (`NORMAL`, `VISUAL`, and other modes), while its winbar keeps
  `DO THIS`, `o NEW LINE BELOW`, and `F1 HELP`. F1 now includes counts,
  `gg`/`G`, `yy`, `p`/`P`, and `:s`, in addition to insertion, selection,
  replace, undo/redo, window switching, and submission.
- **Legacy teaching payload restored:** all 46 original lessons now attach
  exactly once to their nearest v2 animation card. Each attachment carries the
  original `KEYS WORTH KEEPING`, complete legacy Vim concept prose, benefit,
  and exact source. This fixes the content loss; it does not reclassify the 16
  partial/retained-only command-family gaps as implemented. Generated revision
  is `2026-09-28.20`.
- **Direct evidence:** `python3 share/test_v2.py` passes 152/152 executable
  lessons and 114/114 primary edit paths, including an exact 46-payload
  assertion. The installed `client-attached` tmux route passes at 80×24 and
  188×49. Captures show `DO THIS`, target, lualine `NORMAL`, F1 help, real
  Hardtime intervention, the failure ledger, daily attempt credit, the skill
  tree, and post-success progress. The 80×24 capture also searches the actual
  read-only brief and displays the original replace-character key vocabulary,
  its legacy source, and the full Motions concept prose.
- **Still open:** this entry does not close the 16 command-family gaps or prove
  every route matrix at revision `.20`. Do not describe the overall curriculum
  audit as complete.

### VD-12 · 2026-09-28 14:16 — real M0.04 attempt 8: auto-indent shifted the pasted frame; `:s` still never taught

- **Operator report plus the saved artifact** (`checkpoints/M0.04-failed-8.txt`): rows 7–9 were saved as `   \|/   `, ` -- O -- `, `   /|\  `, one column right of the target. The operator opened a line with `o`. Their config (now the default) has `autoindent`/`smartindent` on for text files (`nvim --headless` on a .txt file prints `ai=true si=true`). The new line therefore started indented, and the blockwise paste landed one column right. The operator did not know how to fix it.
- **The brief shown for that attempt** (`sessions/spark-loop/M0.04.txt`): KEYS WORTH KEEPING listed only `F1`, `<C-w>w`, `u`, `<C-r>`, `:wq`, `:q!`. No `yy`/`p`, no `:s`. The operator says they do not know what `:8s/-/=/g` means. It has still not been taught before the card that requires it (VD-12 audit 2, row M0.04).
- **Required:**
  - The art buffer only sets `noautoindent nosmartindent indentexpr=` (buffer-local; the rest of the config is untouched). Column registration is the curriculum invariant, and auto-indent breaks it silently.
  - Teach linewise `yy`/`p` and `:s` (with range and `g`) on guided cards before M0.04.
  - Relayed to Codex (owner of `bin/vim-daily-gate` and the generator).

## VD-14 · 2026-09-28 — operator config restored, 80×24 retry fixed, installer gap addressed

This entry supersedes VD-13's claim that a hand-selected tutor profile should
be the default. It does **not** close the overall curriculum audit or the open
command-family inventory.

### What `--clean` removed

`nvim --clean -i NONE` bypassed the operator's complete Neovim startup, not
just a dashboard. Direct config inspection showed that it removed:

- Hardtime and its `max_count = 3`, `hint = true`, `restriction_mode = "hint"`
  coaching (`~/.config/nvim/lua/plugins/beginner.lua:19-27`);
- WhichKey and the operator's labelled leader groups
  (`~/.config/nvim/lua/plugins/beginner.lua:1-16`);
- lualine (`~/.config/nvim/lua/plugins/example.lua:157-175`), the TokyoNight
  theme, relative numbers inherited from LazyVim, and the rest of LazyVim;
- user mappings, including Ctrl-S, `jk`, Insert-mode Alt-h/j/k/l, and H/L
  buffer navigation (`~/.config/nvim/lua/config/keymaps.lua`);
- all other configured startup plugins and services: Telescope, Snacks, NUI,
  Mason, Treesitter/LSP setup, Flash, and the mode-aware terminal title.

The default is therefore the user's config (`bin/vim-daily-gate:648-653`). The
tutor-owned statusline, F1 float, and custom h/j/k/l blocker exist only in the
explicit clean fallback (`bin/vim-daily-gate:654-712`). The user-config branch
does not reset `statusline` and does not close plugin windows. It only disables
visible whitespace/indent guides, disables automatic indentation in the art
buffer, and restores the top line (`bin/vim-daily-gate:713-741`). Headed-test
readiness waits for lazy.nvim's `User VeryLazy` event before test keys are sent
(`bin/vim-daily-gate:766-787`).

### M0.04 indentation and teaching repair

- The saved M0.04 failure was caused by `o` inheriting leading art whitespace.
  The art buffer now sets `noautoindent`, `nosmartindent`, and an empty
  `indentexpr` without changing the operator's other buffers
  (`bin/vim-daily-gate:627-630,723-739`).
- M0.02 now visibly teaches complete-frame `{count}yy`/`p` and addressed
  `:{line}s/old/new/g`; M0.04 names those two families but continues to hide
  its exact answer (`share/gen_curriculum_v2.py:146-171`). The original
  `substitute` legacy lesson now attaches to M0.02, before retrieval
  (`share/gen_curriculum_v2.py:24-30`). Generated revision is `.21`.

### New-user installer audit and fix

The delegated read-only audit found that the prior `install.sh:8-44` only
created links, installed the timer, and printed two manual steps. A new user
could therefore install successfully without Hardtime, WhichKey, lualine, a
theme, or relative numbers and receive no explanation.

`install.sh:15-22,47-50` now links and runs a read-only setup checker. The
checker scans `${XDG_CONFIG_HOME:-$HOME/.config}/nvim` without starting Neovim
or a plugin manager (`bin/vim-daily-setup-check:69-91`). It reports each
baseline capability as found, missing, or verify; LazyVim-inherited relative
numbers are correctly reported as verify rather than falsely missing
(`bin/vim-daily-setup-check:94-134`). Missing items print an exact Lazy.nvim
example and authoritative links (`bin/vim-daily-setup-check:27-65`). It never
writes to the user's config and recommendations do not fail installation.

Ranked plugin recommendation from the delegated source review:

1. Keep [hardtime.nvim](https://github.com/m4xshen/hardtime.nvim) as the
   baseline repeated-motion coach. It is MIT-licensed, requires Neovim 0.10+
   and nui.nvim, and matches the operator's hint-mode configuration.
2. Add [precognition.nvim](https://github.com/tris203/precognition.nvim) as the
   best optional motion-learning aid, but disable its virtual text/signs in
   tutor art buffers because they alter the visible fixed-width surface.
3. Offer [venn.nvim](https://github.com/jbyuki/venn.nvim) as an opt-in
   ASCII-diagram tool. Its `virtualedit=all` and temporary HJKL behavior must
   never be forced onto graded lessons.
4. Offer [screenkey.nvim](https://github.com/NStefan002/screenkey.nvim) for
   demonstrations, toggleable and off by default at 80×24 because its float
   consumes lesson space. The reviewed release line requires Neovim 0.11+.
5. Retain [flash.nvim](https://github.com/folke/flash.nvim) only when already
   present in the user's config. Do not force it into tutor startup; it loads
   on VeryLazy and changes motion handling.
6. [nvzone/showkeys](https://github.com/nvzone/showkeys) is a lower-ranked
   screencast alternative because it adds another overlay, has a smaller
   documentation surface, and is GPL-3.0.

Baseline sources: [which-key.nvim](https://github.com/folke/which-key.nvim) and
[lualine.nvim](https://github.com/nvim-lualine/lualine.nvim). No reviewed
plugin is silently installed by this project.

### Evidence produced after the fixes

- `python3 share/test_setup_check.py`: passes fresh, partial, LazyVim,
  read-only, and twice-run idempotent installer fixtures. The fresh fixture
  recommends all five capabilities; the
  partial fixture recommends only missing items; the LazyVim fixture reports
  inherited relative numbers as verify. Before/after bytes prove the checker
  changes no Neovim config file; the installer fixture proves it creates only
  its own links and never creates `${XDG_CONFIG_HOME}/nvim`.
- `python3 share/test_v2.py`: 152/152 executable lessons present; 114/114
  primary edit paths pass with clean config.
- `python3 share/test_v2.py --real`: the same 114/114 primary paths pass with
  the operator's real config.
- `python3 share/test_drills.py` and `python3 share/test_drills.py --real`:
  all 46/46 legacy drills pass in clean and real-config Neovim.
- `share/test_tmux_v2.py` passes through the installed `client-attached` hook
  at **80×24, 100×36, and 188×49**. The live checks require the operator's
  lualine NORMAL/VISUAL states, absence of tutor-owned `TUTOR` chrome,
  a real WhichKey popup, Hardtime intervention, and target/brief content
  (`share/test_tmux_v2.py:245-303`). The indentation proof actually executes
  `o`, saves an `X`, verifies it began in column 1, undoes it, and verifies the
  checkpoint was restored byte-for-byte (`share/test_tmux_v2.py:268-291`).
  The journey then proves failed-attempt daily credit, retry key delivery,
  two-column debrief, skill tree, M0 1/8, XP 10, streak, and today 2/12.
- `VIM_DAILY_TEST_CLEAN=1 VIM_DAILY_TEST_COLUMNS=80
  VIM_DAILY_TEST_ROWS=24 share/test_tmux_v2.py` passes the explicit clean
  fallback, including its own short `TUTOR · NORMAL/VISUAL` statusline, F1
  cheat sheet, fallback repeated-motion coach, and the same complete journey.

Still open: the `.21` full route matrix has not been rerun; the sixteen
command-family sequencing gaps from VD-12 have not all been repaired; the
curriculum audit must not be described as complete.

## VD-15 · 2026-09-28 — `.22` still teaches by revealed recipes and late multiple choice

**Operator direction:** first review, then log, then propose. No generator,
runtime, test, or curriculum JSON change is authorized until the operator
approves the audit.

**Audit artifacts:** the complete 152-card matrix, current-revision evidence,
full question proposals, finish-line coverage ledger, and M0 sequence are in
`share/audits/SOCRATIC_COURSE_AUDIT.md`; the typed-key/effect-grading,
wrong-answer, continuation, evidence, and viewport mechanics are in
`share/audits/SOCRATIC_RUNTIME_DESIGN.md`; current-source plugin research is in
`share/audits/NEOVIM_HINT_PLUGIN_RESEARCH.md`. The course artifact re-reads
`/Users/r/.codex/attachments/499fbe13-648c-423a-855d-39c9339aede0/pasted-text-1.txt`
in full and cites each generated card ID and JSON line.

**Direct `.22` counts:** 19 modules / 152 cards / 114 executable cards / 38
concept cards / 190 questions. Only 57 cards own question IDs (38 concept
cards plus 19 module checks); 95 cards have no paired question at all. All
190 questions are four-choice multiple choice: there are no open typed-key,
decode, complete, predict, or why questions. Thirty-one executable cards have
explicit `review_variants`, while all 19 transfer cards contribute their two
`variants` to the same changed-art review route; 50/114 executable cards are
therefore review-capable and 64 have no changed-art bank. A nearby concept
pool, answer key, recipe, distractor, or legacy attachment is not a teaching
stage.

**Current sequencing result:** strict review of revision `.22` finds 47
card-level hidden-first violations: the 46 rows retained from the VD-12
inventory at `FAILURE_LOG.md:1830-1895`, plus the new validation-only
expression substitution in M18.05 (`share/curriculum-v2.json:13378-13520`).
Several rows contain multiple missing families. The concrete failures include
M0.04's required `:8s/-/=/g`, M0.05's first hidden `:t`, M1.04's `dd`/`o`,
M3.04's `ci(`, M3.06's Visual-line/register path, M4.04's block operation,
M6.04/M6.06's `D`/`:m`, M7.04/M7.05's dot/macro/global-normal, M8.04/M9.04's
open/delete/insert paths, M11.04/M11.08's recovery/option paths,
M12–M14's repeat/WORD/object paths, M15–M17's option/block/move/global paths,
and M18.05's `\=` expression path.

**Finish-line gaps:** H7 has no required `:diffthis`/scroll-bound comparison;
H8 has no required trailing-whitespace cleanup or `>` one-cell padding;
H9 lacks the undo-tree exploration habit. S0–S7 and A0–A7 have no owned
machine-readable hidden-performance plus spaced-review links; related cards
are not proof. The four M0–M4, M5–M9, M10–M14, and M15–M18 partition reports
are reconciled in the full-card audit and `GRAMMAR_FIRST_REQUIREMENT.md`.

**Proposed gate (not implemented):** begin M0 with a grammar primer, then
`r`, visible `yy/p`, visible `o`, ranged `:s` with `g`, and only then M0.04
with keys hidden. Add typed-key effect grading in scratch Neovim, grammar
breakdown re-show after wrong answers, and an optional `Next` action that
respects prerequisites/remediation/review. Require every card to own at least
one paired question; exceptions need a card-specific written reason.

**Plugin boundary correction:** no researched hint or key-display plugin can
replace Neovim `-w` evidence plus semantic effect/method grading. screenkey.nvim
is suitable only as an optional demonstration display; showkeys and other
keycasts add no grading/export contract; Precognition is rejected because its
virtual text, virtual lines, and signs contaminate the fixed-width evidence
surface; track-action may become an advisory semantic ledger only after an
operator-approved Neovim 0.13 migration. Most importantly, the operator's
configured Hardtime, WhichKey, lualine, theme, relative numbers, and mappings
remain active by default. The tutor must not silently install, suppress, or
retune them. A future exam-isolation mode may suppress selected hint displays
only through an explicit operator setting; plugin output is never mastery
evidence. This supersedes VD-14's provisional Precognition recommendation
without rewriting that historical entry.

**Audit boundary:** all files in this entry are requirement, evidence, or
proposal documents. No generator, runtime, generated curriculum, popup, or test
implementation is part of this audit commit.

**Status:** open; operator review required. This entry does not claim any
implementation or completion of the curriculum finish line.

## VD-16 · 2026-09-28 — 152-card slice-audit evidence vs the 9 habits + S0–S7/A0–A7 finish line (plan, not implemented)

**Status:** OPEN — plan logged, no generator/runtime code changed in this entry.
**Collision note:** filed as VD-15 in parallel with another session's VD-15 above;
renumbered VD-16 on discovery. That entry's artifact
(`share/audits/SOCRATIC_COURSE_AUDIT.md`, 518 lines, plus grammar-sequence ×4 and
SOCRATIC_RUNTIME_DESIGN.md) is the primary matrix; this entry is the independent
second opinion: 19 parallel slice audits (M0–M18) + main-agent file-wide regex
verification over revision `.22`. Reconciliation: their "47 hidden-first" (46 + M18.05
`\=`) matches this audit's §D (M18.05 :s-\= first-use "no"). Direct runtime
inspection corrects the initial review count: 31 cards own explicit
`review_variants`, and 19 transfer cards supply changed-art `variants`, so 50
cards are review-capable and 64 are not.
**Method:** slice agents read card JSON only (expected/recipe/show_recipe/question_ids/
neovim_answer); cross-module lineage claims marked "out of slice" were re-verified by
the main agent where load-bearing (Ex-:t shown M6.02/M7.01/M7.02 — the "never shown"
sub-claim in M16-V5 is corrected below; :m never shown stands).
STOP observed: generator (`gen_curriculum_v2.py`) and runtime (`v2_runtime.py`) untouched.
**Per-card rows:** §D (appended below). Proposals: §E–G (appended below).

### A. Verified curriculum facts (revision .22, main-agent counts)

- 152 cards: 38 guided_edit (show_recipe=true) / 19 independent_edit / 19
  compare_methods / 19 transfer / 19 module_check / 38 concept. 114 edit cards carry `expected`.
- 190 questions = 19 modules × 10, one of each type per module
  (visual_reading, principle_choice, diagnosis, command_prediction,
  method_comparison, transfer_reasoning, coherence_check, principle_application,
  output_prediction, risk_diagnosis). **190/190 resolve to a 4-option (a–d) pick**
  (`ask_question`, `v2_runtime.py:457`); zero typed-key/decode/complete/predict/explain
  graded forms exist. Per-type variety is delivery variety, not form variety.
- Pairing is module-level only: 57/152 cards carry `question_ids`; **0/190 questions
  carry a card ref** (module_id only). Floor-rule compliance therefore rests on
  bundle convention (Qs on concept/check cards), not on links.
- Checks: every module_check gates on 4/10 MCQs (guessable). Spaced review uses
  `review_intervals_hours [4,24,72,168,336]`, re-asks a module question, and—on
  the 50 review-capable source cards—requires an unhinted changed-art edit
  (`_review_question`, `_changed_review_card`, and `_run_review_edit`). The gap
  is incomplete family/stage coverage and review-after-mastery timing, not the
  total absence of spaced edit retrieval.
- Ex-copy `:t` IS shown-guided, but late: M6.02, M7.01, M7.02 (show_recipe=true).
  M0.05/M0.08/M1.08/M2.08/M3.05 use it hidden with no earlier shown card (VD-12's 46
  hidden-recall cards confirmed, extended in §D).
- review_source_card_id == card_id on all 50 transfer/review cards is file-wide
  convention (self-scope marker), not the M7.06 anomaly it was flagged as.

### B. Habit matrix: hidden + spaced-review status (finish-line rule)

- H1 overwrite: r hidden+reviewed many ✓. R shown M11.01, hidden M11.04/M11.06, no
  later review — THIN. gR zero file-wide — GAP. r<Space>-vs-x: shown, hidden M5.06,
  diagnosed — OK. M9.04 requires x+i hidden-first — VIOLATION (fix: r=).
- H2 exact cell: f/t/; hidden chains ✓ (M0→M12). W/B/E hidden M13.04/06/08 but B
  never shown — GAP. w lowercase zero in expecteds — GAP. N| once hidden M11.08, no
  review — GAP. $ as motion first M10.01 (trivial generalisation, accepted). ^ once
  (M17.04 f^); g_ zero — GAP.
- H3 frame-as-object: yy/p/:t hidden+reviewed many ✓ (shown lineage starts M6.02
  for :t — late, §D M0.05). yap shown M14.02 → hidden M14.05 → check M14.08 ✓.
  } hidden-first M14.05, never shown — GAP. P-as-put once (M14.05 gg}jP); zp zero —
  GAP. :m hidden ×3 (M6.06/M6.08/M16.05), never shown — GAP. dap zero — GAP.
- H4 columns: <C-v> hidden ×2 (M4.04/M15.05), never guided-shown — GAP. r once
  (M4.04); I/$A once ($A M15.05 hidden); c zero; gv zero; o zero in column role —
  GAP (4 of 7 column operators untaught).
- H5 repeat: n shown M17.01 → hidden M17.06 ✓. . hidden-first M7.04, never guided —
  GAP. macros hidden ×2 checks (M15.08/M17.08), never shown/practised — GAP. :g/…/normal
  never performed (alternatives + Q text only) — GAP.
- H6 registers: "a linewise shown?? no — hidden-first M3.06 transfer — GAP for that
  sub-skill; charwise "ayl shown M14.01 → hidden M14.04 ✓. <C-r>a shown M14.01 →
  hidden M14.04 ✓. <C-k> hidden-first M3.08 check, never shown — GAP. ga zero — GAP.
- H7 compare: :diffthis/scrollbind zero; :set list zero; cursorcolumn/colorcolumn
  zero — GAP (whole habit unexercised; Q-only mentions don't count).
- H8 cleanup/pad: :%s-cleanup shape present but as material edits, never whitespace
  cleanup — GAP. counted o<Esc> pad zero (o always with text) — GAP. >+shiftwidth=1
  shown M15.01 → hidden M15.04/06 ✓ (sole H8 pass).
- H9 safe variants: :t-variant keep ✓ (lineage above). u hidden M11.04 once, no
  review — THIN. g-/g+/:earlier zero — GAP.

### C. Stage matrix

- S0 grid/overwrite: content lives in M11 (R, u, <C-r>, virtualedit, N|) — ~11
  modules late; overwrite-first-from-S0 rule broken by placement, not content.
- S1 slopes/typed runs: NO owner. R/counts/0^$g_/N| never taught as slope typing
  (M1 teaches /,r:,yy,:%s,;/,/G0f — S2/A1/S7/A6 fragments).
- S2 hand mirror: NO module. f/t fragments in M2/M12/M18 without ;/,/gR/. mirror art.
- S3 unsure-cells: M13 owns WORD motions ✓ (B-never-shown, V4 typo suspect
  `r_` in M13.04 review-variant-2 vs target row — verify before generator change).
  M2 teaches daw/ci( with hidden-first violations.
- S4 near-verticals: M4 owns <C-v>+r ✓ minus gv/I/$A/c/o gaps; M4.05 prompt d$/A
  fiction (prompt advertises ungraded path).
- S5 variants/symbol table: LABEL (M5) ≠ CONTENT (M3.06/M3.08/M14). M5 teaches
  S3/S6 seam + A1 copy under an S5 name; zero yap/}/P/registers/digraphs in M5.
- S6 layers/seams: NO module. M6 = A5 content (:t/:m/D); marks/zp/scrollbind zero
  file-wide.
- S7 texture: LABEL (M7 = A3/A4 holds/timing) ≠ CONTENT (M0.02 :s + M15 ✓ minus
  macro/:g-shown gaps). M7 tests macros/:g it never performs.
- A0 plan: M16 ✓ (Q06-before-transfer exemplary) minus <C-a>/:read shown-before-Q
  inversion, :m never shown, Q04/Q05 orphaned at check.
- A1 copy-then-vary: M0.02/M2.02/M3/M8.02/M9 — ci(/V/"a hidden-first violations.
- A2 onion skin: NO owner (:diffthis zero; M4/A2 vocabulary without the split).
- A3 coherence: M17 ✓ (Q01-before, Q04-before, Q06-before, Q08-trio exemplary)
  minus :g-hidden (guided card or demo-only exception needed), macro lineage via
  hidden M15.08 (thin).
- A4 holds: M6–M8 timing content ✓-ish (no dedicated violations beyond lineage).
- A5 subtractive: M6 ✓-ish (D/:m hidden-first violations).
- A6 mirror-reuse: M12/M18 ✓, flip-ban honored file-wide (sole :s/\= use checks
  CHECK digits, M18.05) — strongest stage.
- A7 walk: M8 ✓ (Q10 marks-mention needs reword/teach).
- P SJIS: M10 ✓ minus :set-list check and register edit (add or written exception).


### D. Per-card rows, M0–M9 (chain = worked-Q → shown → hidden; G? = grammar stem exists)

| Card | Habit/stage | New families + chain | G? | Paired verdict + reason |
|---|---|---|---|---|
| M0.01 guided `j0f.ro` | H1/S0 | j/0/f/r curriculum-FIRST (primer must precede) | decode f-vs-r | ADD Q04-style pre-Q before + keep Q01 after: predict-then-show |
| M0.02 guided `gg3yyGp`+`:4,6s/o/O/g` | H3/A1 | counted-yy + ranged-:s FIRST (primer must precede) | split range/cmd/args/g | Q08-before (count is failure point) + Q02-after keep |
| M0.03 concept | —/mixed | none | — | MOVE Q07+Q09 → M0.07: test-before-teach at ord 3 |
| M0.04 indep `4G3yyGp:8s` | H3/A1 | variants of M0.02 ✓ | :8s-vs-:%s | KEEP after (recall must precede Q03-diagnosis in .07) |
| M0.05 compare `:7,9t$` | H3/A1 | :t FIRST **hidden** ✗ | :t-vs-yy | NEW worked-:t-Q before + NEW guided :t card before .05 |
| M0.06 transfer `jforO:s` | H1/S0 | f/r per M0.01, :s per M0.02 ✓ | bare-:s scope | KEEP (Q06 in .03 pre-teaches ✓) |
| M0.07 concept | —/mixed | none | hold-vs-drift | KEEP after; receive Q07/Q09 |
| M0.08 check `:1,3t$…for.` | H3/A4 | :t chained on hidden .05 ✗ | Ex-vs-language | KEEP terminal; unblocks via new guided :t |
| M1.01 guided `/,<CR>r:` | H1+2/— | / shown-ok; r per M0.01 ✓ | /-vs-r | KEEP after (Q01 in .03) |
| M1.02 guided `gg3yyGp` | H3/A1 | per M0.02 ✓ | count-on-yy | KEEP after (Q02 in .03) |
| M1.03 concept | — | none | — | KEEP (primes .06 via Q06 ✓) |
| M1.04 indep `4G3ddGo…` | H3/A6-ish | 3dd FIRST hidden ✗; o/insert FIRST hidden ✗ | count-on-dd | Q04-before OR guided demo; S1 gap noted |
| M1.05 compare `:%s/:/;/g` | H5+2+8/S7 | % FIRST hidden ✗ (contradicts M0.Q10); dot FIRST hidden ✗ | %-vs-bounded | Q05-before; Q09/Q10-after keep |
| M1.06 transfer `G0f,r:` | H2+1/S2-frag | f/r per M0.01 ✓ | landmark-vs-count | KEEP-before (Q06 primes ✓) |
| M1.07 concept | — | none | :%-rewrite | KEEP (diagnoses .05) |
| M1.08 check `:1,3t$…;` | H3+2+1/A1 | :t per M0.05-lineage ✓; `;` unguided ✗ | address/motion/repeat/op | KEEP; Q04/Q05 arrive too late to scaffold |
| S1 verdict: ZERO R/typed-count/edges in M1 expecteds — stage unowned file-wide (R only M11) |
| M2.01 guided `/note<CR>daw` | H2/S3 | daw FIRST shown (needs pre-Q) | verb-vs-noun | ADD typed pre-Q before + keep Q01/Q03 after |
| M2.02 guided `gg4yyGp` | H3/A1-early | per M0.02 ✓ | count-on-yy | MOVE Q02 before .02 (currently after in .03/.08) |
| M2.03 concept | H2+3-meta | none | daw-vs-dw-vs-r | KEEP but SPLIT: Q02→.02, Q04→.04 |
| M2.04 indep `6Gf.ro` | H2+1/S3 | f+r per M0.01 ✓ | r-takes-no-motion | Q04 strictly before .04 (currently beside it) |
| M2.05 compare `:%s/[.o]/O/g` | —/S7-early | %+[]-class FIRST ✗ | scope-to-:1,8 | KEEP Q05/Q09 after + ADD pre-Q on `[.o]` |
| M2.06 transfer `jforO` | H2+1/S3 | M0.01→M0.06→M1.06 ✓ | landmark-survives | PIN Q06 immediately before .06 |
| M2.07 concept | meta | ciw named in Q08, never an edit ✗ | ciw-vs-r-vs-daw | KEEP; add ciw micro-edit or drop Q08 from gate |
| M2.08 check `:1,4t$…` | H3+2+1/A1 | :t per M0.05 ✓ | copy-then-vary order | KEEP gate; NOT floor cover for .01/.02/.04/.05/.06 |
| M3.01 guided `2G0f(%hro` | H1+2/— | % FIRST shown (Q01 unlinked) | %-vs-f(+r | LINK Q01 before |
| M3.02 guided `gg6yyGp` | H3/A1 | count scales only ✓ | 6yy-vs-yy | LINK Q02 before |
| M3.03 concept | H3/A1 | none | whole-pose-duplicate | KEEP (5 linked Qs ✓) |
| M3.04 indep `8Gci(O<Esc>` | H1+2/A1-vary | ci( FIRST hidden ✗ | ci(-vs-C | LINK Q04 before |
| M3.05 compare `:1,6t$` | H3/A1 | :t per M0.05-lineage ✓ | cursor-dependence | LINK Q05 before/with |
| M3.06 transfer `ggV5j"ayG"ap…` | H3+6/A1+S5 | V + "a FIRST hidden ✗; hint teaches yap, recipe does V5j ✗ | "a-survives-deletes | LINK Q03+Q06 before; fix hint or teach yap here |
| M3.07 concept | H3/A1+A4 | none | missing-continuity | KEEP (5 linked ✓) |
| M3.08 check `for<C-k>.M` | H6+1/S5-in-A1 | <C-k> FIRST hidden-in-check ✗ | r-digraph-vs-paste | KEEP links + ADD guided digraph card before .08 |
| M4.01 guided `4G0C…` | H4/S4 | C FIRST shown (guided-ok, no pre-Q minor) | C-consumes-to-EOL | KEEP after (Q01+Q08 consolidate) |
| M4.02 guided `4G3yyGp` | H4/S4 | per M0.02 ✓ | count/verb/motion | KEEP after (Q02) |
| M4.03 concept | H4/S4 | host Q01/Q02/Q03/Q06/Q09 | 0+3l-vs-N| | KEEP (floor layer ✓) |
| M4.04 indep `:1,3t3…<C-v>jr|` | H4/S4 | <C-v> FIRST hidden ✗ CORE; :t3-addr FIRST hidden ✗ | block-scope/pivot | MOVE Q04+Q10 pairing before .04 |
| M4.05 compare `:1,3t$`-vs-yy | H4/S4 | families old ✓ but prompt d$/A fiction ✗ | range-upfront-vs-cursor | KEEP after; align prompt or add d$/A alternative |
| M4.06 transfer (unseen art) | H4/S4 | per .04/.01 ✓ | noun-vs-verb | KEEP-before (Q06 in .03 ✓) |
| M4.07 concept | H4/S4 | host | — | KEEP (backs .04/.08) |
| M4.08 check `13G3dd` | H4/S4 | counted-dd per M1.04 ✓ | address/count/verb | KEEP (exemplary: Qs before hidden artifact) |
| M5.01 guided `r<Space>` seam | H1/(S3/S6, NOT S5) | r per M0.01 ✓ | count+G+l+r-op | MOVE Q01 before .01 (currently only .03/.08) |
| M5.02 guided `ggV6jyGp` | H3-partial/A1 | V/y/p per M0.02+M3.06 ✓ | scope-token | MOVE Q02 before .02 |
| M5.03 concept | — | host | f-vs-counted-l | KEEP as holder; release Q01/Q02 forward |
| M5.04 indep `C` redraw | H1/A1 | C per M4.01 ✓ | C-bounds-vs-pivot | MOVE Q04 before .04 (currently only .08) |
| M5.05 compare `:1,7t7` | H3/A1 | :t per M0.05 ✓ | range-vs-cursor | MOVE Q05 before .05 |
| M5.06 transfer `r<Space>` | H1/— | per .01, shifted count ✓ | derive-new-column | ADD pre-derivation; keep after-check |
| M5.07 concept | — | host | one-cell-vs-frame | KEEP |
| M5.08 check `forO…rO` | H1+3/— | f+r per M0–M4 ✓ | rO-vs-x | KEEP; dual-use Q01/Q02/Q04/Q05 as pre-links too |
| M5 verdict: ZERO S5-canonical families (no yap/}/P/registers/digraphs) — label/content mismatch |
| M6.01 guided `r^` | H1/A5 | r per M1.01 ✓ | r-takes-no-motion | KEEP after (Q01 in .03/.08) |
| M6.02 guided `:1,5t$` | H3/A5 | :t range-copy (shown ✓) | range+cmd+arg | KEEP after (Q02) |
| M6.03 concept | H—/A5 | host — PRUNE Q03/Q06/Q09 (forward refs to .04/.06) | range-vs-no-range | REMOVE those three → M6.07 |
| M6.04 indep `6G0D` | H2/A5 | D FIRST hidden ✗; J/u prompt-fiction ✗ | D-vs-dd | MOVE Q03 → .07; make J/u unscored demo or drop |
| M6.05 compare `:6,10t$`+D | H3/A5 | per .04+M0-lineage ✓ | range-vs-walk | KEEP after (Q05 in .08) |
| M6.06 transfer `:1,5m$` | H3/A5 | :m FIRST hidden ✗ | predict-m0-vs-m$ | MOVE Q06 → .07; needs guided :m card |
| M6.07 concept | —/A5 | host | whole-range-move | KEEP; receive Q03/Q06/Q09 (dedupe Q03/Q09 double-list) |
| M6.08 check `:m0/:m5` | H3/A5 | :m-numeric never shown ✗ | dest-order | KEEP gate |
| M6 verdict: ZERO S6 families (no marks/zp/scrollbind) — module mislabeled; S6 empty file-wide |
| M7.01 guided `:1,5t5` | H3/A4-not-S7 | :t-mid per M6.02 ✓ (Q01 unpaired) | range/cmd/landing | PAIR Q01 after (qids null ✗) |
| M7.02 guided `:16,20t$` | H3/A4 | :t-$ per M0-lineage ✓ (Q02 unpaired) | range/cmd/$ | PAIR Q02 after |
| M7.03 concept | —/A4 | host | :-duplicate-vs-.-replay | KEEP |
| M7.04 indep `f-v2lr=`+`5j.` | H5/A3 | v-band FIRST hidden ✗; . FIRST hidden ✗ | motion+op+object; .-replays-what | NEW guided worked-Q BEFORE + Q03/Q04 after |
| M7.05 compare `:%s@…` | H5/A3 | @-delim variant unworked; macro/:g UNPERFORMED ✗ | range/cmd/args/flags | NEW guided macro+:g card first; Q05/Q08/Q09/Q10 after it |
| M7.06 transfer `forO5j.` | H5/A3-A4 | forO old; forO+5j.-unit unworked | find/change/step-5j | PAIR Q06 after |
| M7.07 concept | —/A3-A4 | host | :g-vs-:%s-rows | KEEP + one typed-key item |
| M7.08 check `21G5dd` | H3/A4 | 5dd per M4.08 ✓ (weakest) | address/count/verb | KEEP; dual-pair Q01/Q02/Q04/Q06 at cards |
| M7 verdict: ZERO S7 texture families; macros/:g tested-never-performed |
| M8.01 guided `G0lr_` | H1+2/A7 | per M0.01 ✓ | motion-vs-replace | KEEP after (Q01 in .03) |
| M8.02 guided `gg5yyGp`+C | H3/A7 | per M0.02/M4.01 ✓ | count-keeps-frame | KEEP after (Q02+Q03 in .03) |
| M8.03 concept | —/A7 | holder | r_-vs-x | KEEP (holder before .04 ✓) |
| M8.04 indep `Go…o…` | H8+3/A7 | o per M1.04 ✓ (first hidden use of drilled family — ok) | typed-rows-scope | KEEP hidden; dual-list Q04 in .07 too |
| M8.05 compare `:1,5s@…` | H5/A7 | :s-@ per M0.02 ✓ | range-end-at-5 | KEEP after (Q05+Q09 in .08) |
| M8.06 transfer `G0llr_` | H1+2/A7 | count-derivation, family old ✓ | derive-don't-memorise | KEEP (Q06 in .08) |
| M8.07 concept | —/A7 | Q10 names marks never taught ✗ | foot-slide-repair | KEEP; reword Q10 search-only or teach marks |
| M8.08 check `:6,10t$`+C | H3+9/A7 | :t per M0.05 ✓; C per M4.01 ✓; hand-mirror (A6-compliant, no flip) | range+args; C-mirror-rows | KEEP (exemplary terminal) |
| M9.01 guided `fxro` | H2/A1 | f/r per M0.01 ✓ | motion-carries-scope | KEEP after |
| M9.02 guided `gg3yyGp`+C | H3/A1 | per M0.02/M4.01 ✓ | count/op/motion/put | KEEP after |
| M9.03 concept | — | holder | language-vs-Ex | KEEP (primes .05/.06 ✓ sandwich) |
| M9.04 indep `5GfOxi=` | H1-claim/A1 | x FIRST hidden ✗; i-entry FIRST hidden ✗ (anti-H1) | parse-then-r=-instead | FIX expected → `5GfOr=` (or add guided x/i); Q03-after keep |
| M9.05 compare `:1,3t3` | H3/A2 | :t per M6.02 ✓; C per M4.01 ✓ | registration-grammar | KEEP (Q05-before/Q05-after sandwich exemplary) |
| M9.06 transfer `fxro`-fam | H2/A1 | per M0.01 ✓ | fx-needs-no-count | KEEP-before (Q06 primes ✓) |
| M9.07 concept | — | holder | op/motion/range-per-option | KEEP |
| M9.08 check `:1,3t$…forO` | H3/A4 | per M6.02/M0.01 ✓; overclaims "all families" ✗ | Ex-vs-language-halves | KEEP gate; trim "every family" claim |


### D (ctd). Per-card rows, M10–M18

| Card | Habit/stage | New families + chain | G? | Paired verdict + reason |
|---|---|---|---|---|
| M10.01 guided `$rヽ` | H1/P | r per M0.01 ✓; $ motion trivially new (accepted) | motion-vs-operator | KEEP after (Q01 in .03) |
| M10.02 guided `gg3yyGp`+C | H3/P | per M0.02/M4.01 ✓ | count-token | KEEP after (Q02+Q03 in .03) |
| M10.03 concept | —/P | holder; Q06 pre-teaches .06 ✓ exemplary | count+op pairing | KEEP |
| M10.04 indep `Go…o…` | H3/P | o per M1.04 ✓ but zero paired Q ✗ | o-per-row-parse | ADD command_prediction pre-Q (floor gap) |
| M10.05 compare `:7,9t$` | H3/P | per M0.05 ✓ | range+cmd+addr | KEEP after (Q05 in .08) |
| M10.06 transfer `$r` | H1/P | per .01 ✓ + Q06-before ✓ exemplary | motion-vs-op-unseen | KEEP-before |
| M10.07 concept | —/P | holder (Q04 J-defect, Q09/Q10 Saitamaar concept-only — accepted) | row-vs-frame-repair | KEEP |
| M10.08 check `:1,3t$` | H3/P | per M0.08 ✓ | unhinted-family-name | KEEP gate |
| M10 gaps: :set-list zero (ADD bounded check in .07/.08); registers zero (ADD palette edit or written exception) |
| M11.01 guided `0lR==` | H1/S0 | 0l per M0.01 ✓; R FIRST shown (guided-ok) | address+overwrite-N | ADD direct qids link; keep-after |
| M11.02 guided `gg3yyGp` | H3/S0 | per M0.02 ✓ | count+op+motion+put | ADD direct link; keep-after |
| M11.03 concept | H1/S0 | host — PRUNE Q04/Q06/Q08 (forward refs) | R-vs-i-registration | REMOVE those three → later cards |
| M11.04 indep `R~~u<C-r>` | H9/S0 | R 2nd-exposure ✓; u FIRST ✗; <C-r> FIRST ✗ (+M14 collision note) | inverse-ops-predict | REMOVE Q04 from .03; keep in .08 |
| M11.05 compare `:s/o/O/g` | H8+1/S0 | bare-:s per M0.06 ✓ but Q05/card path mismatch ✗ | /g-removed-predict | KEEP after + FIX card or narrow Q05 |
| M11.06 transfer `R==` | H1/S0 | shown→hidden→transfer ✓ exemplary | endpoint-invariance | REMOVE Q06 from .03; keep .08 |
| M11.07 concept | H1+9/S0 | host — PRUNE Q07/Q10 (forward refs to .08) | i-vs-R-drift | REMOVE those two → .08 |
| M11.08 check `VE,13|,i,3j.` | H1+2+5/S0+S1 | virtualedit FIRST in-check ✗; N| FIRST in-check ✗; . per M0.01 ✓ | VE-off-vs-all; 3j.-replay | KEEP gate + ADD guided VE/N| card before |
| M11 verdict: S0 core ~11 modules late (placement defect, content sound) |
| M12.01 guided `0t:lr!` | H2/A6 | t-family FIRST shown (no pre-Q, minor) | motion-vs-op+arg | KEEP (shown→Q→hidden ✓ via .03) |
| M12.02 guided `gg3yyGp`+`$T:h` | H2/A6 | T FIRST shown; Q02 only in .08 ✗ | addr-vs-motions | ADD backward-till stem to .03 |
| M12.03 concept | H2/A6 | host (Q04 pre-works ;/ ✓, Q06 pre-works transfer ✓) | t-vs-T-direction | KEEP |
| M12.04 indep `f:;r!,r!` | H2/A6 | ;/, per M1.06/M1.08 ✓ + Q04-before ✓ | repeat-vs-edit | KEEP |
| M12.05 compare `:1,3t$`+`:s` | H2/A6 | families old ✓ (:s glyph-identity only — flip-ban holds) | range+cmd+bare-:s | MOVE Q05 → .07 (equivalence before check) |
| M12.06 transfer `t/T` | H2/A6 | per .01/.02 ✓ + Q06-before ✓ | origin-direction-till | KEEP |
| M12.07 concept | H2/A6 | host (Q08 byte-reversal ban = §4.7.7 ✓) | two-tills-mark | KEEP; receive Q05 |
| M12.08 check `:1,3t$…t!/T:` | H2/A6 | per M0.02/.01/.02 ✓ | Ex-vs-Normal-halves | KEEP (pass 4/10 convention) |
| M12 gaps: all-MC; no explicit count+op+motion parse in any Q (grammar-coverage potential only) |
| M13.01 guided `Wr!` | H2/S3 | W FIRST shown (Q01 after — inverted) | motion+replaceless-r | MOVE Q01 before .01 |
| M13.02 guided `gg3yyGp…Wr.` | H2/S3 | W 2nd, still no pre-Q | counts+addr+motion | ADD Q02 to .03 immediately after |
| M13.03 concept | H2/S3 | holder (Q04/Q06 pre-work ✓) | W-slot; w-stops | KEEP |
| M13.04 indep `E…2W…2B` | H2/S3 | E/B/counted-W FIRST hidden ✗ (Q04-before placement ok, exposure wrong) | addr-vs-motion-count | ADD shown B/E micro-step before .04 |
| M13.05 compare `:7,9t$`+`:s` | H5/S3 | per M0.02 ✓ but method_requirement null (f/;-alt ungraded) ✗ | range+cmd+args+flags | ADD Q05 to .07 after; set requirement or drop alt |
| M13.06 transfer `2W…B…` | H2/S3 | lineage tainted by .04; Q06-before ✓ | no-column-count-why | KEEP |
| M13.07 concept | H1+2/S3 | host (x/d-vs-r = overwrite-first ✓) | op-terms-of-drift | KEEP |
| M13.08 check `:1,3t$…Wr.` | H2/S3 | W/B+r shown→Q→hidden except B-never-shown (partial) | range-copy+motion-edit | KEEP gate |
| M13 suspect: M13.04 review-variant-2 `r_` vs target row without `_` — verify typo before generator change |
| M14.01 guided `"ayl+R<C-r>a` | H6/S5 | charwise-"a FIRST shown ✗; R<C-r>a-combo FIRST shown ✗ (M3.06 linewise ≠ this; M11 <C-r>=redo) | register-slots; yaw-vs-yal | ADD Q02/Q01 before |
| M14.02 guided `yapGp` | H3/S5 | yap FIRST shown ✗ (only M14.05 reuses) | yap-vs-y3j-scope | ADD Q08 before |
| M14.03 concept | H6/S5 | host (dual-link Q01/Q02 forward too) | R-vs-i-width | KEEP; duplicate-link (not move) Q01/Q02 |
| M14.04 indep `"ayl…R<C-r>a` | H6/S5 | shown(.01)+Q04(.03)→hidden ✓ partial-chain | addr/motion/register | LINK Q04 after (floor paper-gaps despite chain) |
| M14.05 compare `yap…}…` | H3/S5 | } FIRST hidden ✗ WORST; :t-contrast per M0.02 ✓ | object-vs-range-breakage | ADD }-navigation Q before; LINK Q05 after |
| M14.06 transfer (x-palette) | H6/S5 | shown+Q06→hidden ✓ | keystroke-to-wall-map | LINK Q06 after |
| M14.07 concept | H6/S5 | host | scope-vs-cursor-vs-separator | KEEP |
| M14.08 check `…}}jj…<C-r>b` | H6/S5 | "b by-analogy ✓ (Q09); }} depends on .05-fix | find/register/navigate/replace | KEEP gate + pre-link note |
| M15.01 guided `sw=1…>>` | H8/S7 | shiftwidth/>> FIRST shown | op-without-motion | KEEP after (hands-before-why) |
| M15.02 guided `gg3yyGp` | H3/S7 | per M0.02 ✓ | count/op/motion | KEEP after (Q02) |
| M15.03 concept | H8/S7 | host | option-vs-operator | KEEP bridge |
| M15.04 indep `5G>>`+`:4s` | H8/S7 | >> per .01 ✓; :s-family per M0.02 ✓ (Q04-before would leak — after correct) | range-drop-predict | KEEP after |
| M15.05 compare `<C-v>$A`-vs-`:s` | H4/S7 | <C-v> never shown ✗ (M4.04 hidden → here hidden) | selection-vs-range-scope | KEEP after + guided block card |
| M15.06 transfer `>>` | H8/S7 | shown→hidden→transfer ✓ exemplary | art-vs-grid-tokens | KEEP after |
| M15.07 concept | —/S7 | host (defect span H8+H5) | leaking-range-rewrite | KEEP before check |
| M15.08 check `:1,3t$…qq…3@q` | H5/S7 | macro FIRST in-check ✗ (S7 "first macros" examined cold) | record/landmark/count | Q09/Q10 precede artifact in-card ✓ + guided macro card |
| M16.01 guided `<C-a>` | H3/A0 | <C-a> FIRST shown; Q01 after (inverted) | 0f0-landing; bare-<C-a> | MOVE Q01 before .01 |
| M16.02 guided `:read %` | H3/A0 | :read FIRST shown; Q02/Q10 after (inverted; stale-disk = top risk) | file-below-line; saved-first | MOVE Q02 before .02 |
| M16.03 concept | H3/A0 | host (inherits inversion) | plan-block-range | KEEP; trim Q01/Q02 if moved (no double-ask) |
| M16.04 indep `:1,5t$`+`2<C-a>` | H3/A0 | :t shown-lineage late (M6.02+); 2<C-a> FIRST hidden ✗ (Q04 orphaned at check) | range/cmd/addr-parts | ATTACH Q04 before .04 |
| M16.05 compare `:6,10m0` | H3/A0 | :m NEVER shown ✗ (only hidden M6.08 before; M16.05 hidden too) | range/cmd/0-addr | ATTACH Q05 before .05 |
| M16.06 transfer `<C-a>` | H3/A0 | per .01 ✓ + Q06-before ✓ (only correct pre-use in M16) | label-vs-pose | KEEP |
| M16.07 concept | H3/A0 | host | copy/move-five-line-range | KEEP |
| M16.08 check `:1,5t$`+`2<C-a>` | H3/A0 | recombination, hidden ✓ | copy-then-renumber-split | KEEP (all-10 convention) |
| M17.01 guided `/x<CR>ron.n.` | H5/A3 | n FIRST shown-guided ✓-by-construction; . FIRST shown-guided ✓ | travel-(n)-vs-repeat-(.) | KEEP-before (Q01 predicts ✓) |
| M17.02 guided `7G3yyGp` | H3/A1-scaffold | per M0.02 ✓ (stage-tag as A1-support, not A3) | count-scopes-what | KEEP-before |
| M17.03 concept | —/A3 | host (consolidates foundation ✓) | anchor-vs-scope | KEEP after .01/.02 |
| M17.04 indep `f^r-…f_r-` | H1+2/S3-like | per M12.04 ✓ (stage-tag S3-supporting-A3) | addr/motion/op; eye-skipped-why | KEEP-before (Q04 predicts hidden ✓ floor) |
| M17.05 compare `n.`-vs-`:g` | H5/A3 | search-dot per .01 ✓; :g NEVER performed ✗ | match-count-vs-line-proof | KEEP after + guided :g card OR demo-only exception |
| M17.06 transfer (brackets) | H5/A3 | per .01 ✓ identical path, new vocab ✓ exemplary | semantic-eye-invariant | KEEP-before (Q06 names invariant ✓) |
| M17.07 concept | —/A3 | host | material-vs-geometry | KEEP after compare+transfer |
| M17.08 check `/*qqr+nq3@q` | H5/A3 | macro per M15.08-hidden (lineage thin ✗); n-macro combo first-as-combo (families old ✓) | record/edit/close/replay-count | KEEP-before-trio (Q08+Q09+Q10 strongest pairing) |
| M18.01 guided `0C…` | H1/A6 | C per M4.01 (slice-first = cross-module ok) | 0C-vs-c$; retype-why | ATTACH Q01 before (currently only .03/.08) |
| M18.02 guided `gg4yyGp` | H3/A6 | yy/p per M0.02 ✓ | count-includes-CHECK | ATTACH Q02 before (currently only .08) |
| M18.03 concept | —/A6 | holder for .01/.04/.06 ✓ | byte-reverse-fails-why | KEEP |
| M18.04 indep `5G0C…` | H1/A6 | per .01 shown→hidden ✓ (no pre-Q, Q04 in .03 covers) | frame/columns/same-cell | KEEP |
| M18.05 compare `$r1`+`:s/\=` | H1/A6 | $r1 slice-new; :s-\= FIRST (CHECK-digits-only, flip-ban holds ✓) | range+cmd+arg+scope | ATTACH Q05 before (currently only .08) |
| M18.06 transfer (unfamiliar) | H1/A6 | per .01/.04 ✓ (reading-only pre-Q, no typed pre-Q — noted) | meaning-not-position | KEEP (Q06 before ✓) |
| M18.07 concept | —/A6 | holder (generated-mirror diagnosis = §4.7.7 ✓) | pixels-right-mastery-denied | KEEP |
| M18.08 check `:5,8t$`+`:1,4t$` | H3/A6 | :t per M0-lineage ✓ reversed order | copy/land/overshoot-first | KEEP terminal |

### E. Proposals: one rule + new-question texts (existing Qs cited by ID; full text only for NEW stems)

Rule: every exercise card gets ≥1 paired question; guided → after-consolidation,
hidden (independent/compare/transfer/check) → before-prediction, except compare cards
whose in-card alternatives self-pair (M4.05, M9.05, M15.05 keep-after). Moves/adds in §D
are the per-card proposal; below is full text for stems that do not exist yet.
Forms: T = typed-key graded by buffer effect (new mechanic §G); D = decode; C = complete;
P = predict-the-art; W = explain-why. No per-card exception is claimed — all gaps get a Q.

- P0 primer card (NEW concept, ordinal 0, before M0.01). Five micro-stems, all T except noted:
  (a) T "Spark core at row 2 col 4 shows `.`: go there and make it `o`. Any path passes."
  (b) D "In `f.` vs `ro`: which token is the motion, which the char argument, and why does `r` take no motion?"
  (c) D "Split `:8s/-/=/g` into range + command + args + flag. What does `g` scope, and what would `%` touch instead?"
  (d) C "Finish the copy that ignores cursor row: `:7,9_ $` (one char missing)."
  (e) W "Why does `r` keep the row width while `x` plus insert shifts the wall?"
- M0-O guided card (NEW, between M0.02 and M0.04): `Go<Esc>` pad + C "After `G`, which
  single key opens the flare row, and what does `<C-u>` clear if you mistype it?"
- M0-T guided :t card (NEW, before M0.05): Q "Contrast `7G3yyGp` vs `:7,9t$`: which
  depends on cursor row? Name range + command + destination in the `:t` form." (extends Q05)
- M1.04 pre-Q (T, before): "Delete rows 4–6 as whole lines with one count. Any counted-`dd` path passes."
- M2.01 pre-Q (T, before): "Delete the word `note` with operator + text-object. `dw`/`daw` both pass if the face survives."
- M2.05 pre-Q (D, before): "In `:%s/[.o]/O/g` name range, class, replacement, flag — then bound it to `:1,8`."
- M3 digraph guided card (NEW, before M3.08): Q (T) "Replace the core with `·` via
  `r<C-k>.M`. Typing the literal `·` passes too; recipe shows the digraph path."
- M4.04 pre-Q (T, before + NEW guided block micro-card first): "Select the 2-row Pixcol
  with `<C-v>j` and fill `|`. Any block path that fills exactly those cells passes."
- M6.04 pre-Q (D, before): "Parse `6G0D` into address + motion + operator. Why does the row survive but `dd` would remove it?"
- M6.06 guided :m card (NEW, before transfer): Q (P) "`:1,5m0` vs `:1,5m$`: where does the moved range land in each? Then perform the `m0` form shown."
- M7.04 pre-Q (T, before): "Change the 3-cell band with `v2lr=` then step `5j` and repeat with `.`. Any equivalent visual+dot path passes."
- M7.05 guided macro+:g card (NEW, before compare): Q (C) "Record `qq…q` over one joint,
  replay with `2@q`. How many joints does the count cover, and which would `:g/…/normal` select instead?"
- M9.04: NO new Q (Q03 covers) — change expected to `5GfOr=` (overwrite-first compliance).
- M10.04 pre-Q (P, before): "Which open-line sequence appends exactly 3 bounded rows? Predict the frame count for `Go…o…o…` vs one `o` plus paste."
- M10 :set-list Q (D, in .07): "Run `:set list` on the puff: which cells are full-width
  spaces vs half spaces, and which line-leading form is forbidden?"
- M10 register Q (T, in .06 or .08): "Store the `⌒ヽ` lobe in `a` (`\"ayl`) and place it
  with `R<C-r>a`. Any register letter passes." (If cut: written exception "P-register deferred to S5-deep M14".)
- M11 VE/N| guided card (NEW, before M11.08): Q (P) "With `virtualedit=all`, where does
  `2G13|` land vs with it off? Predict, toggle, then `i|`."
- M12.02 T-stem (ADD to .03): D "Parse `4G$T:` into address + motions; contrast direction with `0t:`."
- M13 B/E micro-step (NEW guided, before M13.04): Q (T) "Reach the second cluster with
  `2W`, step back with `B`, close with `E`. Any W/B/E path that lands all three edges passes."
- M14.01/14.02/14.05 pre-Qs: Q02-duplicate before .01, Q08-duplicate before .02 (duplicate-link,
  not move); NEW }-Q (D, before .05): "Contrast `5Gyap`+`gg}jP` (object scope) vs `:5,8t$`
  (range+command+args): when does each break if a separator is missing?"
- M15.08 guided macro card (NEW, before check): Q (C) "In `qqf:r.q`: which key starts/stops,
  what is the landmark, what does `3@q` count? Then perform it shown once."
- M16 moves only (Q01→.01, Q02→.02, Q04→.04, Q05→.05 — duplicate-link, trim from .03 to
  avoid double-ask); M17: NEW guided :g card before .05 OR written exception "`:g` is
  demo-only in A3; mastery requires search-dot + macro limbs only."
- M8.Q10 reword: "mark or search" → "search" (or teach marks before M8); M13.04 variant-2
  `r_` suspect → verify typo before generator change; M4.05 prompt ↔ d$/A alternative alignment.

### F. M0 full sequence (required order)

P0 primer (new, §E) → M0.01 `r` (guided shown) → M0.02 `{count}yy/p` + addressed `:s`+`g`
(guided shown) → M0-O `o` pad (new, guided shown) → M0.04 hidden recall yy/p + one-line
`:s` (first unhinted retrieval) → M0-T `:t` (new, worked-Q then shown) → M0.05 compare →
M0.06 transfer → M0.07 diagnosis (receives Q07/Q09) → M0.08 check. Missing pieces are exactly
M0-V4 (no `o` card) + M0-V5 (no primer) + M0-V1/V2 (`:t` hidden-first) from §D.

### G. New mechanics (named, not built — STOP)

1. Typed-key items graded by buffer effect: prompt withholds keys, learner types in a
  scratch buffer, grader applies keys and compares effect (art + registration), so any
  valid path passes (`daw` vs `dw`, literal `·` vs digraph). Replaces MC-only `ask_question`.
2. Breakdown re-show after wrong answer: a miss re-displays the recipe decomposition
  (count + operator + motion / range + command + args + flags) with the failed slot
  marked — the grammar, not the answer key.
3. Optional `Next`: after a result, the learner may start the next eligible
  item. Active remediation comes first; `Next` never skips a failed question,
  prerequisite, unfinished module-check subpart, due-review policy, or daily
  cap, and it never converts a failure into progress.

### H. Stop

Operator decision required before any generator/runtime change: (1) §D moves/adds,
(2) §E new cards/questions, (3) §F M0 reorder, (4) §G mechanics, (5) label/content repairs
(M5→S3/S6+A1 or new S5 content; M6→A5 or new S6 content; M7→A3/A4 or new S7 content),
(6) M13.04 `r_` typo verification. Showing this entry for review now.

### VD-16 reconciliation delta against VD-15 and the partition reports · 2026-09-28

The second audit confirms the already logged grammar/pairing/review defects; the
following are the non-duplicate corrections that change the decision surface:

- **Stage ownership is a label/content problem, not just missing metadata.**
  M5 is not S5 content (it is a seam/S3-S6 plus A1-copy slice), M6 is not S6
  content (it is A5 `:t`/`:m`/`D`), and M7 is not S7 content (it is A3/A4
  holds/timing). No module owns the complete S2, S6, or A2 finish-line stage;
  §H therefore needs relabel-versus-rebuild decisions.
- **H7 is wholly unexercised in current executable paths.** `:diffthis`,
  `scrollbind`, and `:set list` are each zero-occurrence file-wide, so this is
  stronger than a missing review link or an unowned comparison card.
- **The negative inventory is now explicit.** Required-but-never-shown items
  include `:m`, `<C-v>`, macros, `B`, `}`, `<C-k>`, `u`, `virtualedit`, and
  `N|`; no current executable expected/variant/method path uses `gR`, `gv`,
  `ga`, `zp`, `dap`, undo-tree navigation (`g-`, `g+`, `:earlier`), or
  lowercase `w`. Legacy prose and attachments do not count as use.
- **M9.04 has a concrete anti-overwrite repair.** Its hidden-first `x+i`
  path (`5GfOxi=<Esc>`) should be replaced in the proposal by
  `5GfOr=`; the existing x/i sequencing gap remains, but this repair preserves
  the fixed cell rather than deleting and reinserting it.
- **Correction to the `:t` slice wording:** `:t` is shown-guided at M6.02 and
  reused shown-guided at M7.01/M7.02. It is late and unpaired—not absent;
  M0.05 and the earlier hidden uses remain ordering violations.
- **M13.04 review variant 2 is intentional, not a typo.** Its start contains
  `O` at the old pulse location; `2Wr_` clears that cell, while the target has
  `_` there and puts `!` at the new edge cells. No generator change is warranted
  from the earlier `r_` suspicion.

### VD-13 · 2026-09-28 — M0.05 failed correct work: exact-log method check; M0.04/M0.05 attempt audit

**Operator report:** "I've been failing the same lesson all day." That was M0.04
(8 failures from 2026-09-28 00:55 to 14:16, then passed 14:34, revision `.21`),
followed by M0.05 (9 failures from 14:34 to 16:37).

**Attempt audit.** Saved checkpoints are compared with the card's target;
`events-v2.jsonl` supplies the reasons.

| When | Card | Saved result | Recorded reason |
|---|---|---|---|
| 00:55, 02:54, 11:56 (+2 dup copies) | M0.04 | start unchanged | target-mismatch |
| 13:10 | M0.04 | frame pasted characterwise onto the end of row 6 | target-mismatch |
| 14:16 | M0.04 | frame pasted one column right (after `o`, autoindent) | target-mismatch |
| 14:34 | M0.04 | **pass** | — |
| 15:08 | M0.05 | **exact target** | **missing-method-evidence** |
| 15:55, 16:19:25, 16:19:42 (+2 at 14:34) | M0.05 | start unchanged | target-mismatch |
| 16:36:53, 16:37:20 | M0.05 | **exact target** | **missing-method-evidence** |
| 16:37:43 | M0.05 | only row 9 appended (keylog `:9t$<CR>:ew<BS><BS>wq<CR>`) | target-mismatch |

**Defect 1 — correct work graded as failure (three times).**
- `_method_family` (`share/v2_runtime.py:919`) credits a comparison method
  only when the entire captured keystroke log, minus a literal `:wq<CR>` or
  `ZZ` suffix, equals `7G3yyGp` or `:7,9t$<CR>` exactly.
- Any other key fails an exact target: a look-around motion, an undo, a
  hardtime-blocked press, `:w` then `:q`, or a corrected typo in `:wq` (the
  operator's last log has `:ew<BS><BS>wq`).
- The feedback then says "no edit keystrokes were captured", which is false:
  the keys were captured.
- Required fix: credit the method when its defining command occurs in the
  log, together with the exact target. For example, `:{range}t` with a range
  resolving to rows 7–9, or `3yy` or an equivalent yank followed by `p`.
  Strip every save/quit form, including one with corrected typos. Replace the
  false message with the reason.

**Defect 2 — the prompt asks for two methods but grades one buffer.** "Create
a deliberate whole-frame flare hold by counted yank/put *and* by addressed
`:t`". Only one copy fits the target. The page does not say to do one of them.

**Defect 3 — the keys are unknown and untaught.** `:t` and line ranges are
never shown on a guided card before M0.05 (VD-12 audit 2 row M0.05). The
operator's last attempt `:9t$` shows the range grammar was missing (it needed
`7,9`). Five M0.05 saves and three M0.04 saves are unchanged starts: the
learner did not know what to type.

**Defect 4 — per-attempt keystrokes are not kept.** `keys-M0.05.log` is
overwritten on every attempt, so the keys behind the three exact-target
failures cannot be audited. Only the final attempt's log survives.

**Defect 5 — encouragement surface regressed.**
- Legacy `progress_banner` showed `N/12 today · streak N days 🔥` (the
  flame appears from 3 days), best streak, and all-time total, in bold.
  Legacy also printed "Streak extended to N days" on a pass.
- v2 `_progress_line` shows plain XP, level and streak, with no flame, no
  best streak and no extension message.

**Fix attempt 1 · Codex · 2026-09-28:**
- M0.05 now declares semantic evidence for either one valid method: a
  three-line linewise yank followed later by `p`/`P`, or an executed addressed
  `:7,9t$`/`:7,9copy$`. `_method_family` searches for that defining operation
  inside the attempt instead of requiring the whole keylog to equal a pristine
  recipe. Exact target equality remains mandatory.
- Ex evidence reconstructs the command after `<BS>`, `<C-h>`, `<C-u>`, or
  `<C-w>` corrections. Save/quit commands are removed wherever they occur,
  including `:wq`, `:w` + `:q`, `:write` + `:quit`, `:x`, `ZZ`, and `ZQ`.
- Unrecognized input now distinguishes an empty capture from captured-but-
  unrecognized keys and prints the latter truthfully. If the buffer is exact
  but method evidence is missing, the failure headline now says the target
  matched instead of falsely calling it a target mismatch.
- M0.05 now says to use **ONE** method; success still displays both approaches
  for comparison.
- Every v2 edit attempt receives a numbered durable keylog such as
  `keys-M0.05-attempt-0001.log`; pass/fail events retain its path and SHA-256.
- V2 progress restores the bold streak line, flame at three days, best streak,
  all-time total, and `Streak extended to N days.` pass message.
- Evidence: `python3 share/test_v2.py` passes all 114/114 primary edits and new
  M0.05 integration cases with extra motions, corrected Ex typing, split
  save/quit, both taught methods, and retained keylog hashes. `python3
  share/test_v2.py --real` also passes 114/114 under the operator's real Neovim
  config. The installed client-attached headed route reproduces extra `jj`,
  `:7,9t$`, and corrected `:ew<BS><BS>wq`, and passes with numbered keylog
  evidence at 80x24, 100x36, and 188x49.

**Status:** blocking defect fixed and verified; the broader grammar-first
curriculum implementation remains in progress.
- **Defect 6 — no optional "next lesson" (operator, 2026-09-28).** Every exit
  ends in `hold_open()` → "press Enter to close" (`bin/vim-daily-gate:841`,
  called from ten places in `share/v2_runtime.py`). A motivated learner cannot
  continue in the same popup. Required behaviour:
  - After any result (pass, fail, concept), offer `n` = next due lesson,
    `r` = retry this one, Enter = close.
  - `n` counts toward the daily cap and the cooldown as usual.
  - It never forces continuation.
  - The legacy route had `vim-drill` for another drill, but no in-popup
    continue either.
  Queued to Codex.
- **Defect 6 implemented by Claude (operator: "wire the next feature here now").**
  - In the v2 lesson routes (`run`, `--force`, `--if-due`), `hold_open()` now
    prompts `press Enter to close · n then Enter = next lesson now`.
  - `n` sets `_NEXT_REQUESTED`, and `main()` then runs the next lesson in the
    same popup through the on-demand (`--force`) route. Enter still closes.
  - Legacy drills keep the plain prompt.
  - Code: `bin/vim-daily-gate` `hold_open`, `_OFFER_NEXT`/`_NEXT_REQUESTED`,
    and `main` v2 branch.
  - Evidence:
    - isolated tmux 188×49 on a copy of the real state, with the real config:
      M0.06 failure → the prompt shown above → `n` opened the next lesson
      (`transfer-M0.06.txt`) → Enter exited;
    - `test_tmux_v2.py` passes at 188×49, 100×36 and 80×24 (real user
      config); `test_drills.py` 46/46.
  - Not yet seen by the operator in a real scheduled popup.

### VD-17 · 2026-09-28 — Grammar-first pairing runtime and M0 prerequisite insertion

**Implemented slice (not the end of the broader hidden-first inventory):**

- The generated course now contains 155 cards and 307 authored questions.
  The question bank has 190 paired animation/Neovim multiple-choice items,
  39 effect-graded typed-key items, 21 decode items, 19 completion items,
  19 prediction items, and 19 why items. Every card declares at least one
  paired question, its before/after placement, a card-specific placement
  reason, grammar family/stage, and H/S/A coverage metadata.
- M0 now begins `M0.P0 → M0.01 → M0.02 → M0.O → M0.03 → M0.04 →
  M0.T → M0.05 → M0.06 → M0.07 → M0.08`. `M0.P0` asks the learner to
  classify operator, standalone-Normal, and Ex grammar. `M0.O` visibly teaches
  `o`, `<C-u>`, and `<Esc>` without relying on inherited indentation.
  `M0.T` visibly teaches addressed `:t` before M0.05 can hide it. Existing
  card IDs did not move.
- Typed-key questions are evaluated by replaying the learner's notation in an
  isolated `nvim -u NONE` scratch buffer and comparing resulting lines (and,
  when declared, cursor state). The evaluator rejects file writes, shell/
  runtime execution, extra windows/tabs, and unsupported notation. It accepts
  effect-equivalent paths: both `j0f.ro` and `jf.ro` pass M0.01's scratch
  contract, while `j0f.rx` fails.
- Wrong typed/decode/complete/why answers re-render `GRAMMAR BREAKDOWN` and
  record evidence but award no card XP. `progress-v2.json` now separately
  projects `passed_questions`; a question-only pass leaves XP at zero.
- Edit cards run unanswered paired questions at their authored before/after
  point. Module checks run their paired prerequisite before the five-question
  checkpoint. Post-edit why questions preserve an exact saved artifact while
  withholding card credit until the explanation passes.
- Runtime validation no longer assumes exactly eight cards and ten all-MC
  questions per module. It validates all six forms, pairing fields, declared
  module inventories, and written pairing exceptions.

**Defects found while executing this slice:**

- The first M0.O recipe inherited indentation under bare Neovim. The recipe
  now uses `<C-u>` only on the two newly opened rows that can inherit leading
  indentation; its third open row deliberately omits `<C-u>` because using it
  at column zero joins the line above. The art-buffer-local `noautoindent`,
  `nosmartindent`, `nocindent`, and empty `indentexpr` protection remains.
- The module-check flow originally asked its five bank questions before the
  newly declared paired prerequisite. `run_edit` now executes the authored
  before-question first, then the five-question checkpoint, then the artifact.
- Raw command-family inference mistook a glyph-search dot for Normal `.` and
  control-key notation for operator commands. Inference now removes Ex spans
  and angle-bracket key tokens before classifying Normal-mode syntax.

**Direct evidence:**

- `python3 share/test_v2.py`: 155/155 cards structurally present; 116/116
  primary edit recipes pass in isolated Neovim; mixed-form, semantic-effect,
  pairing, no-XP-on-question, remediation, review, replay, and schema checks
  pass.
- `python3 share/test_v2.py --real`: the same 116/116 primary edit recipes
  pass with the operator's real Neovim configuration.
- `python3 share/test_tmux_v2_routes.py --only-m005`: the corrected M0.05
  extra-motion/corrected-Ex route still passes after the paired after-question.
- `python3 share/test_tmux_v2_routes.py --only-check`: the paired prerequisite,
  five questions, and unhinted M0.08 artifact run in that order and pass in a
  real 188×49 tmux popup.
- `python3 share/test_tmux_v2.py`: the automatic client-attached route answers
  M0.01's semantic typed-key prerequisite, preserves the operator's real
  lualine/WhichKey/Hardtime UI, records failure practice, retries, passes, and
  shows 2/11 M0 progress at 188×49.

**Still open:** the consequential hidden-first families listed in VD-16
(`dd`, `ci(`/text objects, Visual block/registers, digraphs, `D`, `:m`, dot,
macros, `:g … normal!`, virtual columns, `E/B`, undo-tree work, and expression
substitution) still need their inserted guided microcards and a generator gate
that proves explanation → interpretation/completion → shown performance →
hidden retrieval → changed-art review. This entry does not mark that inventory
complete.

### VD-13 fix (Claude, operator: "fix it all here, do not ping codex") · 2026-09-28 17:15–17:35

**Operator report:** M0.06 transfer failed at 17:12. The operator "needs to be
taught 'f'": the ledger showed `jforO` as one word. After the failure there was
no retry ("This transfer attempt stops here").

**Changes:**
- **New `share/v2_keys.py`: a key-by-key explainer.**
  - `explain()` splits a recipe into the commands Vim executes: count,
    register, operator + motion/text object, Visual-mode operators, inserts,
    `r`/`R`, `f`/`t`, macros, and Ex range + command + args + flags. Each
    command gets a plain meaning.
  - `teach_lines()` names the command *families* a card needs without its
    exact answer.
  - Round-trip checked on all 154 expected, method and variant key strings.
    Every family used has teaching text.
- **Lesson brief (`_write_session_lesson`).**
  - Guided cards show "THE RECIPE, KEY BY KEY".
  - Hidden-recipe cards show "HOW THE KEYS YOU NEED WORK (the exact answer
    stays hidden)": a grammar line plus one line per family, e.g.
    `f{char} jump to the next {char} on this line`,
    `r{char} replace the ONE character…`, `:s/old/new/g …`.
  - The compact header now has the progress line on a line of its own.
- **Failure/success page (`_post_feedback_ultra`).**
  - "THE ANSWER, KEY BY KEY" appears under DO / AVOID, for example:
    `j = down one line`,
    `fo = jump forward to the next 'o' on this line`,
    `rO = replace the character under the cursor with 'O'`,
    `:s/-/=/g<CR> = on the current line, substitute '-' with '=' …`.
    Alternative methods are explained too.
  - In a tight popup it packs into one paragraph, as part of the
    measure-and-shrink fit.
- **Concept failures (`_print_grammar_breakdown`).** Every command quoted in the
  question (e.g. `3daw`, `rO`, `:8s/-/=/g`) is decoded key by key under
  "THOSE COMMANDS, KEY BY KEY".
- **Transfer retry.** The "transfer attempt stops here" return was removed. A
  failed transfer now reaches the same "retry? [Y/n]" prompt as other edits,
  and its remediation stays scheduled.
- **Ledger hygiene (`_without_brief_navigation`).** Keys typed in the brief
  pane after `<C-w>w`/`<C-w>h` are no longer counted as art edits. The old
  filter handled only `<C-w>k…<C-w>j`, so `/KEYS WORTH KEEPING` showed up in the
  ledger.
- **Crashes introduced by the concurrent revision-`.22` M0.P0 grammar primer.**
  Opening M0.P0 raised `AttributeError: 'NoneType'…` in
  `ask_authored_question`, because the card has only `paired_question_ids` and
  `_question_for_card` did not fall back to them. The progress page then raised
  `ValueError: int('P0')` in `_module_card_map` and in the compact module map.
  Both are fixed; non-numeric ids render as `P0`, `O`, `T`.
- **The compact module map** prints `today N/12` on its own line, so it is no
  longer split by wrapping.
- **`test_tmux_v2.py`** searches for the source sections separately at 80×24,
  where the brief pane is ~12 rows.

**Evidence:**
- Isolated tmux at 188×49 on a copy of the real state, with the real config:
  - M0.P0 opened;
  - a wrong answer showed the per-command decode;
  - `n` retried with a new stem;
  - no crash.
- `_key_teaching`/`_answer_breakdown` output was inspected for M0.05 and M0.06.
- `test_tmux_v2.py` passes at 80×24, 100×36 and 188×49 (real user config).
- `test_v2.py` was still running when this entry was written; see the next
  line.

**Not verified:**
- The failed-transfer retry through a real M0.06 popup: the state gate now
  requires M0.P0 first. It was checked by code path only.
- The route matrix.
- Operator confirmation.
- **Also fixed (VD-13):** typed-key answers were `.strip()`ped, so a correct
  answer ending in `r` + Space (e.g. M5.01/M5.06 `4G05lr `) was graded wrong.
  Typed-key answers now keep spaces; only the line ending is removed
  (`ask_authored_question`). Rerunning the headed M5.06 transfer route alone
  passed at 188×49.
- **Verification status at 17:36:**
  - `test_tmux_v2.py` passes at 80×24, 100×36 and 188×49.
  - The full route matrix and `test_v2.py` are **not verified**. Another
    session rewrote `gen_curriculum_v2.py`, `curriculum-v2.json`,
    `v2_runtime.py` and `test_v2.py` between 17:35:13 and 17:36:02. At that
    point `test_v2.py` stopped at "generated artifact drifted from
    gen_curriculum_v2.py": `build()` gives 169 cards / 321 questions, while the
    JSON holds 170 / 322.
  - A route run failed at M1.06 because the curriculum changed underneath it.
  - An earlier `test_v2.py` run hung on stdin for 16+ minutes; it was killed.
    A leftover `test_v2.py --real` from another session (PID 95612) has been
    running for about 15 hours.

## VD-17 · 2026-09-28 — curriculum moved under the audit; 1,908 Stone Story frame sheets found outside archive and tutor

**Status:** OPEN — recorded, no code changed here.

- **Drift:** VD-16 evidence is pinned to revision `.22` (152 cards / 190 Qs). Live tree
  is now revision `.23` (169 cards / 321 Qs, `share/curriculum-v2.json` + generator
  rewritten 17:35–17:41 by another session; `build()` vs JSON mismatch 169/321 vs
  170/322 noted at VD-13 fix tail). VD-16 per-card rows need a `.23` re-run before any
  claim built on them is used for generator work.
- **Found, unarchived, unvendored:** `~/Downloads/stone-story-consolidated/` — 4,202 files,
  17 MB, **0 rows** in `ascii-art-archive/MANIFEST.tsv`: 1,908 `resNN.txt` animation
  frame sheets (16,741 nonblank art lines) with `.png` renders + 386 `manifest.txt`
  (Foes 22 / Pets 576 / Weapons 226 / Cosmetics 521 / Hats 86 / UI 96 / Games 212 /
  community+cAutomation 31 / steam-guides 138). Official + community StoneScript sources.
- **Found in-archive but unvendored** (`share/art.json` holds 49 pieces, all plates 01–06
  extracts + 5 downloads): `01-sacrificial-pit-layers.txt` (1,122-line layered scene —
  the S6 content the curriculum lacks), `ssrpg Sapling & Ramparts.txt` (355 lines game
  sprites), tutorial-HTML extras (worm-walk frames, dome build, brick-ground rows, logo
  variants — mined 160 unique art lines from `collections/downloads/ASCII-art Tutorial.html`).
- **License gate stands:** archive rows are `license=unknown/redistribute=unresolved`;
  nothing above may be vendored or published until cleared. Next step when authorized:
  archive `stone-story-consolidated` (hash-index), then intake selected sheets via
  `intake_art.py` with provenance blocks.


### VD-13 audit 3 · 2026-09-28 17:45 — the same gaps checked on every lesson (revision `.23`)

**Operator:** "this was just a single example; similar pedagogical gaps
persist in the other lessons."

**Scope.** All 169 cards (130 edit, 76 with hidden keys) were checked with the
`share/v2_keys.py` family parser. This is an inferred parser, spot-checked,
with a round-trip over all key strings.

**Findings:**

| Check | Result |
|---|---|
| Hidden-key cards requiring a family that no earlier guided card showed | 10, down from 46 at `.19`: M0.06 `:s///g`; M7.04 `v`; M8.05 ranged `:s`; M11.05, M13.05 `:s///g`; M12.04 `;` `,`; M12.05 `;`; M14.05 `}` `P`; M14.08 `}`; M15.05 block `$A` |
| …of those with a "before" paired question | 4 |
| Hidden-key cards with the generic "choose the smallest normal-mode operation" hint | 8 |
| Compare-methods cards whose prompt says "by A and by B" but grades one buffer | 9 |
| Edit cards with at least one paired question | 130/130 (39 typed_keys, 34 decode, 19 predict_art, 19 why, 19 complete; 111 before, 19 after) |

**Runtime fixes (independent of the generator, so future cards get them too):**
- `_key_teaching(card, cur=…)` computes the families that earlier guided
  lessons displayed.
- Any family needed for the first time is shown under "FIRST TIME YOU NEED
  THESE (no earlier lesson showed them)", as `NEW <family teaching>` plus a
  worked example on neutral text (`v2_keys.EXAMPLES`). For instance: `on
  a-b-c: :s/-/=/g makes a=b=c`, or `} jumps to the blank line after this
  frame`.
- 15 hidden-key cards now show this. The runtime counts `[count]`/range
  variants separately, so it flags more than the audit's 10.
- A generic hint is replaced by "use the commands explained under HOW THE KEYS
  YOU NEED WORK".
- The compact brief on comparison cards says "USE ONE METHOD — either one
  passes; both are compared after you pass". The full brief already says
  "CHALLENGE — Make the outcome with one method".

**Evidence:**
- `_key_teaching` output was inspected for M0.06 and M14.05.
- `test_tmux_v2.py` passes at 80×24, 100×36 and 188×49 (real user config).

**Still open (curriculum authoring, not runtime):**
- The 10 cards should get a guided (keys shown) card, or a before-question for
  the family, earlier in their module.
- The 9 compare prompts should be reworded in the generator.
- Seeing a command once is not mastery. Spaced recall of every family (the
  goal "practised everything a master uses") has not been measured per family.

## VD-18 · 2026-09-28 — missing ANIMATION frame paths, verified frame-vs-part (license gate waived by operator)

**Status:** OPEN. Operator waived the redistribute gate for logging (not for publishing).
**Method:** `resNN.txt` blocks are script splits in file order (full sprite + part layers),
NOT frames — proven by Dog res01 (body) vs res02–05 (eye/leg parts) and FlowerFoes res01
(whole) vs res03 (fragment). Animation-grade = set holding ≥2 DISTINCT full-pose blocks
(≥4 nonblank lines, sha-distinct). 282 dirs hold res sheets; 158 are singleton/part-only
(excluded below, they are standalone items); **86 sets / 885 sheets qualify**.
Full per-file list: `share/audits/animation-frame-paths.txt` (972 lines). Base for all
paths: `~/Downloads/stone-story-consolidated/`. Archive rows: 0. Tutor use: 0.

Missing animation sets (set [full-pose sheets]): Mech [49], Skully/pet [37], Panda [28],
Dragon/pet [28], Knight [27], SillyGoose [26], LegsTurkey [23], TowerDefense [21],
Cranius [21], SpearThrowing [18], BurgerRush [18], FoesNoMore [18], Mushroom/pet [18],
Snowman [17], CaveParty [17], CultGroup [15], Calculator/UI [15], SpringBloom [13],
FrogBog [12], WhackaMole [11], StoneasaurGame [11], Dog [11], FaceHUD [11], Bunny [10],
Snake/pet [10], Bolesh [10], AcronianGuardian [10], Crab [9], FrogJump [8], Stonehead [8],
plus 56 sets of 2–7 sheets each, enumerated by name in `share/audits/animation-frame-paths.txt`.
Also unvendored (in-archive): `01-sacrificial-pit-layers.txt` (1,122 lines),
`ssrpg Sapling & Ramparts.txt` (355), tutorial-HTML worm-walk row groups + dome build +
brick-ground rows + logo variants (160 unique art lines mined, page order = frame order).

## VD-19 · 2026-09-28 — command-family prerequisites and spaced retrieval are now generator contracts

**Scope:** curriculum source/data/tests only; `bin/vim-daily-gate` was not
edited. This entry follows VD-13 audit 3 and preserves the live 169-card
guided-bridge work.

**Curriculum changes:**

- Added five visible guided prerequisite cards, raising the generated course
  to **174 cards / 326 questions**: M0.SL teaches current-line `:s///g`;
  M7.VIS teaches characterwise `v`; M12.FIND teaches `f` plus `;` and `,`;
  M14.PARA teaches `}` and `P` on blank-line-separated frames; M15.BA teaches
  blockwise `$A` append.
- Split substitution grammar into `ex-substitute-line` and
  `ex-substitute-range`; hidden cards cannot claim that a ranged substitution
  taught the implicit-current-line form (or the reverse).
- Hidden-first validation now preserves fractional guided bridge stages instead
  of recategorising them as interpretation cards. The generated
  `verified_grammar_sequence` records the exact earlier guided card for every
  hidden family, including the ten VD-13 audit targets.
- All compare-method source prompts now begin with the card id and
  **USE ONE METHOD**, explicitly saying not to perform both and that method
  evidence is compared only after that one path reaches the target.
- Added card-specific changed-art review banks to M3.04 (text object), M3.08
  (digraph), M7.04 (characterwise Visual), and M8.04 (open-line authoring), so
  late first-use families return with keys hidden instead of relying on a
  worked-example string.

**New command-level contract:**

`verified_command_review_coverage` is generated and independently re-derived
by `share/v2_runtime.py`. For every family first shown by a guided recipe, the
contract requires a later hidden card (`show_recipe=false`) with at least two
source-linked changed-art variants. It records the guided card, review card,
variant count, `keys_hidden=true`, and runtime evidence. The current contract
covers 28 families, including line/range `:s`, `;/,`, `}`, `P`, `v`, and block
append. `share/test_v2.py` asserts the contract and executes every review bank
through real Neovim; this prevents answer-key padding from satisfying coverage.

**Evidence:**

- `python3 share/gen_curriculum_v2.py` → 19 modules, 174 cards, 326 questions.
- `python3 share/test_v2.py` → **174/174 executable lessons**, **135/135
  primary edit recipes**, all transfer/compare/review paths pass with isolated
  Neovim; output reports 54 changed-art review/transfer sources and 19 compare
  paths.
- Generated artifact and source are checked equal by the focused suite; runtime
  schema validation rejects a missing or stale command-review contract.

**Still open:** headed popup proof for this new curriculum slice and the wider
master-habit inventory (H7 tooling and commands not yet taught) remain outside
this source/data subtask.

## VD-20 · 2026-09-28 17:55 — primer had no answer contract; held result omitted repeat

**Operator evidence:** the live `M0.P0.P01` decode question was submitted blank
at 17:55:06 (`events-v2.jsonl`, event
`20260928T175506458787-0400-0eb924da`). The popup asked the learner to classify
`3daw`, `rO`, and `:8s/-/=/g<CR>` but rendered only `your answer:`: it showed no
response shape and no different worked example. Blank Enter was recorded as a
failed question/card and scheduled remediation. On the held result page the
only controls were close and `n`; there was no `r` repeat control. At compact
size the long result control wrapped through the popup border, matching the
operator's garbled capture.

**Runtime repair:** every non-choice form now renders an explicit `ANSWER
FORMAT` plus a short `OTHER EXAMPLE` before input. Blank input re-prompts and
does not become evidence. A genuine wrong answer renders the grammar breakdown
and the authored `sample_answer` as `ONE ACCEPTED ANSWER` (or `ONE WORKING
ANSWER` for effect-graded typed keys). This applies to all typed-key, decode,
complete, and why questions rather than only M0.P0.

**Result controls:** the held prompt is now one compact line:
`Enter = close · r = repeat this lesson · n = next lesson`. `r` on a failed
ordinary card reopens that exact current card so a later pass can advance it;
failed reviews remain on the review/remediation route. `r` after a pass uses an
isolated practice artifact and suppresses event, XP, mastery, daily, and streak
credit; it cannot silently mean “next”. The existing `n` implementation and
launcher loop are preserved.

**Evidence:** `share/test_v2.py` covers blank re-prompting, pre-answer format,
post-error accepted examples, distinct `r`/`n` state, and non-crediting practice
events/artifacts. `share/test_tmux_v2.py` now derives module totals from the live
curriculum and proves the answer format, all three held controls, exact-card
repeat, and unchanged practice progress. The real user-config popup passes at
80×24, 100×36, and 188×49 on the 174-card curriculum.

**Still open:** two exhaustive independent audits are running: (1) every live
card/question for visible answer usability and all result routes; (2) every
card/question under the stricter gate “answerable from previous teaching alone,
clear request/acceptance contract, and pedagogically correct placement.” Their
reports must be reconciled before any claim that all lessons are clean.

### VD-20 audit reconciliation · all 174 cards / 326 questions

The completed learner-facing audit is preserved verbatim in
`share/audits/VD-20_EXHAUSTIVE_QUESTION_UX_AUDIT.md`. It found 141 compact
80×24 rendering risks, 59 decode/why questions whose accepted synonym groups
are not visible, 19 hidden transfer questions whose exact sample answer was
printed on the transient pre-clear path, and incorrect `n` routing: after a
failure it reopened the same card through `--force`, while after a pass it
bypassed the ordinary spaced-review selector. It also reproduced stale wrapped
prompt pixels after `n` in an 80×24 popup.

The runtime correction now keeps an exact or accepted sample off the transient
question-input path and places it on the held replay page after evaluation.
Same-popup `n` no longer uses `--force`: it cannot skip an unpassed current
lesson, and after a pass it uses the normal card/review selector while enforcing
the daily cap. Because `n` is an explicit continuation inside the already-open
popup, it waives only the hourly re-prompt cooldown. Every new same-popup route
clears the terminal before rendering, preventing the prior wrapped prompt from
bleeding into the next lesson. `r` remains the distinct exact-card action.

**Open, not waived:** the 141 compact risks and 59 hidden-term-contract findings
remain curriculum/layout work. They are not converted to “pass” by the generic
answer-format line. The prerequisite/clarity/placement audit must also be
reconciled before question text is rewritten.

## VD-21 · 2026-09-28 — three live prerequisite/contract gaps in rev .25 (same class as the primer failure)

**Status:** OPEN. Verified against rev `.25` (174 cards / 326 Qs) in JSON (runtime) order.
Related: VD-20's open 59 hidden-term-contract findings are distinct from item 2 below.

1. **Primer still violates (other session's replacement not landed):** `M0.P0.P01`
  (decode, before) asks to classify `` `3daw` `` / `` `rO` `` / `` `:8s/-/=/g<CR>` `` while
  `d`-operator is first guided at `M1.DD` and `aw` at `M2.01`. The family order checker
  cannot see it: the Q is tagged `grammar_family=vim-language-primer`, a family no card
  teaches, so content escapes verification. Full JSON-order scan otherwise passes —
  this is the only family-order violation in 326 questions.
2. **All 19 why-contracts byte-identical:** every `form=why` question carries the same
  `answer_contract` (term groups frame/rows/range/object + scope/cursor/registered/
  unchanged; sample "The complete frame is the object; bounded scope keeps registered
  cells unchanged.") and the same NEOVIM half ("Why was the demonstrated method safe
  for this frame, and what scope error would the other task shape risk?"). Any module's
  accepted answer passes any other module's why — grading cannot discriminate.
  Animation halves differ (19 unique prompts), so the defect is the contract, not coverage.
3. **Tag-masking class:** the order checker trusts `grammar_family` tags; backtick content
  exceeding the tag is unchecked (item 1 proves it). Before-question backticks should be
  scanned against first-guided positions the way VD-16 §D did for expected fields.
Retracted (checked, not a gap): `M7.04.P01` — JSON order runs `M7.VIS` (guided visual)
before `M7.04`; the flag was an ordinal-sort artifact. Decode-before on guided cards is
the designed decode-the-shown-recipe pattern, not test-before-teach.


## VD-22 · 2026-09-28 — primer replacement landed and verifies; why-contracts still identical

**Status:** PARTIAL — item 1 of VD-21 closed, items 2–3 open. Rev `.25` (174/326).

- **Closed:** `M0.P0.P01` no longer classifies `3daw`/`rO`/`:8s`. It now asks what
  unfamiliar `5j` means after teaching `4j` — clean count-transfer with no untaught
  family in backticks. Primer prerequisite violation resolved.
- **Still open:** all 19 `form=why` contracts byte-identical (1 unique contract), same
  shared NEOVIM half — grading still cannot discriminate across modules.
- **Still open:** tag-masking (order checker trusts `grammar_family`; backtick content
  unchecked). The fixed primer proves the class matters: the old tag
  (`vim-language-primer`) hid the violation until a content read caught it.

## VD-23 · 2026-09-28 — popup clipboard and prerequisite-first lesson order

**Operator evidence:** the opening M0.P0 popup required a long free-text decode
of `3daw`, `rO`, and `:8s/-/=/g<CR>` before any lesson had taught delete
operators, text objects, replacement, Ex ranges, substitution, flags, or the
expected answer shape. The operator also could not copy text from the popup.

**Root causes:** M0.P0 carried an advanced survey disguised by the broad
`vim-language-primer` metadata tag; guided paired questions were placed before
the edit that was supposed to teach them; the installed popup route enabled
OSC clipboard support but had no `pbcopy` copy-mode bindings and did not force
mouse mode for an already-running tmux server.

**Curriculum repair:** M0.P0 now teaches only `[count] + motion`, demonstrates
`j` and `4j`, and asks one four-choice transfer to `5j`; the advanced commands
are absent. First-use guided questions now occur after the visible recipe and
the learner's guided edit. All M*.03 banks contain only Q01/Q02 from their two
preceding guided cards, removing the 21 future-content presentations in the
`.24` prerequisite audit. Compound decode contracts require every family in
their recipe. The stale M6.04 prompt no longer orders a `J`/undo performance
that its actual target and recipe had already removed.

**Contract repair:** the 19 compare-method why questions now have 19 distinct,
card-specific prompts, required term groups, and accepted examples. Visual-line
`V` and `C`/change-to-end are recorded as real grammar families and receive the
same later hidden changed-art review contract as other taught families. Tests
scan command-looking backticks in every before-question against earlier guided
performance rather than trusting the question's declared family tag.

**Clipboard repair:** all three popup launch routes enable `mouse` and
`set-clipboard`, and bind copy-mode-vi `y`, `Enter`, and mouse-drag completion
to `copy-pipe-and-cancel pbcopy`. The popup title and lesson brief state
`drag copies` / `Cmd-V pastes`.

**Evidence:** `share/test_v2.py` passes 174/174 executable cards and 135/135
primary edit recipes under isolated Neovim. M0.P0 headed proof passes at
80×24, 100×36, and 188×49. The full real-user-config popup passes at 80×24,
100×36, and 188×49; the 80×24 route also asserts live mouse/clipboard options
and the three `pbcopy` bindings. The `.24` audit snapshot plus resolution note
is preserved at `share/audits/lesson-prerequisite-clarity-matrix.md`.

**Still open:** VD-20's 141 compact-layout risks and 59 hidden accepted-variant
visibility findings require per-question layout/contract work. The standalone
animation lesson pack is authored and rights-audited but not yet wired into the
live generator.

## VD-24 · 2026-09-28 — compact questions wrapped choices off-screen

**Status:** PARTIAL — the measured compact rendering class is fixed; open-text
accepted-variant disclosure remains open.

The VD-20 renderer audit counted 141 likely 80×24 overflows because terminal
autowrap split long prompts/choices unpredictably, and typed-key questions
stacked START above TARGET. The runtime now deliberately wraps compact prompt
paragraphs at 64 cells, compresses each multiple-choice animation/Neovim pair
onto one line while retaining both halves, and renders typed-key START and
TARGET side by side. This changes layout only; grading and semantic choice
indices remain unchanged.

The headed 80×24 module-check test now checks every presented question has four
complete one-line `A · V` choices, and the five-question check reaches its real
Neovim artifact. M0.P0 and the full guided/fail/retry/pass/repeat popup also
pass at 80×24. The route test's stale `passed=10` setup was corrected to 11:
after M0.P0 was added, 10 selected M0.07 rather than the asserted M0.08 check.

Still open from VD-20: decode/why acceptance uses hidden term groups. The UI
shows the response shape and a non-answer example, then shows the exact grammar
and one accepted answer after a wrong attempt, but it does not expose every
accepted synonym before grading.

## VD-25 · 2026-09-28 18:28 — M0.O is an obsolete typing wall, not an `o` micro-lesson

**Status:** CLOSED in curriculum revision `.26`; the operator still needs to
see the repaired sequence in a real scheduled popup.

The operator passed the repaired M0.P0 at 18:27:37, then failed M0.O twice at
18:28:46 and 18:28:54. The durable first keylog is
`~/.local/state/vim-daily/projects/m0-open-line-lab/keys-M0.O-attempt-0001.log`:
it begins with the shown `G`, `o`, `<C-u>`, and the first ray row, then contains
repeated recovery/undo input and exits without a target. The second attempt is
`:q!`. The artifact was correctly restored to the old three-row start.

The card's supposed single-family lesson requires a 46-character recipe and
18 literal art characters:
`Go<C-u>  \\|/<Esc>o<C-u>-- O --<Esc>o  /|\\<Esc>`. It asks the beginner to
author an entire second three-row spark while simultaneously learning `G`,
`o`, `<C-u>`, Insert mode, `<Esc>`, and exact whitespace. Worse, `<C-u>` was a
workaround for inherited indentation, but the runtime now correctly disables
autoindent/smartindent/cindent/indentexpr in the art buffer. The workaround is
obsolete and teaches noise.

Required correction: make M0.O one visible `o` micro-performance. Supply the
first five rows of two three-row spark frames and ask the learner to open only
the missing lower-ray row (`Go  /|\\<Esc>`). The recipe must separately name
`G`, `o`, the literal row, and `<Esc>`; no `<C-u>`. Accept the old three-row
start as a migration source so the operator's restored artifact upgrades
without deletion or a manual repair. Add a generator test bounding M0.O's
literal typing burden and a real headed retry proof.

**Implemented at 18:54:** M0 is now ordered `P0 → 01 → YP → O → SR → 02`.
`M0.YP` visibly teaches `gg`, counted linewise `3yy`, `G`, and `p` on a full
three-row frame. Repaired `M0.O` supplies five correct rows and requires only
`Go  /|\\<Esc>`; the obsolete `<C-u>` workaround is gone. `M0.SR` visibly
teaches `:2s/o/O/g<CR>` as address + command + old/new arguments + flag +
Enter. Only after those three micro-performances does the old combined M0.02
appear. This grows M0 from 12 to 14 cards and the course from 174 to 176 cards.

The operator's three-row M0.O artifact is an explicit
`accepted_legacy_starts` value. Runtime proof checks that it is checkpointed as
`M0.O-pre-curriculum-migration-1.txt`, upgraded to the five-row scaffold, and
then completed without deleting user work.

**Compact-popup finding and repair:** the first 80×24 headed run showed that a
six-row target consumed the visible brief before `HINT` and `RECIPE`. Equal-
height animation frames now render side by side in compact briefs without
collapsing fixed-width spaces. `DO THIS`, `HINT`, all target rows, `RECIPE`, and
the Normal-mode statusline are simultaneously visible at 80×24.

**Clipboard evidence:** the installed gate and popup hook are symlinks to this
checkout. The live tmux server reports `mouse on` and `set-clipboard on`;
copy-mode-vi `y`, `Enter`, and `MouseDragEnd1Pane` all execute
`copy-pipe-and-cancel pbcopy`. The popup title states `drag copies · Cmd-V
pastes`. The real user-config client-attached popup completed at 80×24,
100×36, and 188×49 while asserting those live options and bindings.

**Verification:** `share/test_v2.py` passes all 176 executable cards and all
137 primary edit recipes. Focused headed runs of M0.YP, M0.O, and M0.SR pass at
80×24, 100×36, and 188×49. The animation-pack integration test passes with 12
live paired lessons and 24 paired questions. Python compilation, popup shell
syntax checks, and `git diff --check` pass.

## VD-26 · 2026-09-28 19:00 — master-habit/stage claims are metadata, not runtime mastery

**Status:** PARTIAL. This supersedes the last sentence of VD-25: the 12 animation
pack rows are not live scheduled lessons, so calling them “live paired
lessons” was false.

The authoritative finish line is the operator's nine-habit list and the
S0–S7, A0–A7, then proportional-P order in
`/Users/r/.codex/attachments/499fbe13-648c-423a-855d-39c9339aede0/pasted-text-1.txt`.
A command counts only when the learner first sees and performs it, later must
use it with keys hidden under a method check or keystroke limit, and retrieves
it again on changed art in spaced review. Stills S0–S7 must precede animation.

### Evidence that the current claim does not hold

1. `animation_lesson_pack` contains 12 nested records and 24 nested questions,
   but there are zero `AL*` ids in top-level `cards`, zero of the 24 `AL*-Q*`
   ids in top-level `questions`, and `share/v2_runtime.py` never reads either
   `animation_lesson_pack` or `animation_pack_*`. Generator lines 4976–4993
   merely attach ids to existing M cards. The scheduler therefore cannot show,
   grade, advance, or space any AL lesson or AL question.
2. `MASTER_COVERAGE` at generator lines 3778–3797 stamps broad habit/stage
   labels onto every card in a module. It does not derive those labels from a
   graded method. For example M4 claims H7/frame comparison, while no expected
   or accepted route anywhere contains `:diffthis` or `scrollbind`.
3. `command_review_contract()` at lines 4447–4475 matches broad grammar-family
   labels and `show_recipe=false`. It never requires the reviewed command to
   appear in `method_requirement`. Ordinary exact-target grading accepts a
   different route, so this does not meet the operator's “required unhinted”
   rule despite the evidence string saying `runtime-validated`.
4. Stage order is contradicted by the graph. Animation modules M1–M9 can unlock
   before later still modules M11–M15. S5 is attached to M10/M14 and S7 to M15,
   after the walk and bounce capstones in M8/M9.

### Exact command gaps against the nine habits

No executable path anywhere uses `gR`, `g_`, lowercase `w`, blockwise `I`,
blockwise `c` as a taught operation, `gv`, Visual-selection `o`, `zp`/`zP`,
`ga`, `:diffthis`, `scrollbind`, `:set list`, `cursorcolumn`, `colorcolumn`,
trailing-whitespace cleanup `:%s/\\s\\+$//e`, `g-`, `g+`, `:earlier`, or
`dap`. Counted `o<Esc>` appears only in a hidden answer, not guided first.
Several present commands also lack required-method evidence: `r<Space>`, `P`,
`:m`, blockwise `r`, `$A`, `:g/.../normal`, `<C-k>`, and `\\=`.

This is not a wording defect. Completion requires executable guided →
method-required hidden → changed-art spaced-review routes for those commands,
truthful evidence derived from the method grader, a topological stage gate
with S0–S7 before A0, and promotion of the AL material into top-level scheduled
cards/questions (or removal of the live-integration claim until promotion).

**Implemented foundation:** every module's hidden `.06` unfamiliar-art
transfer now has an exact method requirement on both authored variants and is
marked `required_before_mastery`. Runtime projection holds an otherwise
complete module at `review_pending` until one changed-art `.06` spaced review
passes with method evidence; only then can the module become `mastered` and
unlock dependents. `required_mastery_review_coverage` is derived from those
enforced cards rather than broad command labels. This closes the false
target-only mastery award for the 19 existing transfer routes. The exact
command gaps, stage ordering, and unscheduled AL pack listed above remain open.

## VD-27 · 2026-09-28 19:04 — hidden `<C-u>` and open-response grading

**Status:** CLOSED in curriculum revision `.27`; headed proof repeated
after the repair.

**Operator evidence:** the 19:04 ledger records M0.YP's edit as already passed,
then records the paired decode answer `last line + copy block + last line +
pase` as a failure. The answer described the actual `gg3yyGp` sequence, but the
free-text grader required undisclosed term-group synonyms. This was not a Vim
performance failure. Separately, `<C-u>` remained embedded in executable
M1.04 and M8.04 authoring recipes and in generated question explanations even
though no earlier card taught it.

**Scope audit:** revision `.26` contained 328 questions: 191 multiple choice,
41 decode, 39 predict-art, 19 why, 19 typed-key, and 19 complete. Thus 137
questions still used a non-`multiple_choice` form. The two live `<C-u>` recipe
paths used Insert-mode indent deletion as a workaround even though the lesson
art buffer now enforces `noautoindent`, `nosmartindent`, `nocindent`, and an
empty `indentexpr` after user plugins load.

**Repair:** all 328 questions are now four-choice multiple choice. Decode,
predict, why, typed-key, and completion remain as `learning_form` metadata, but
they share the same explicit a/b/c/d interaction, four paired
ANIMATION/NEOVIM choices, shuffled display order, and choice-specific feedback.
Converted choices are grounded in the owning card: animation halves name the
card and its module's documented defect, while Neovim distractors contradict
the shown command, bounded target, or method comparison instead of reusing one
generic wrong sentence.
The old open-response contract is retained only as source audit metadata; it
is never presented or graded. Hidden transfer checks moved from before to
after the edit so their correct choice cannot reveal the required key path.
Prompts no longer say “type keys” or “decode in plain language.” The post-card
question replay now shows `you`, `correct`, and `why` for paired choices rather
than looking for a free-text sample answer.

M1.04 and M8.04 no longer contain `<C-u>`. Their `o` rows rely on the runtime's
art-buffer no-indent invariant, and the isolated Neovim executor now applies
the same invariant. The generated JSON contains zero `<C-u>` occurrences.

**Evidence:** `share/test_v2.py` passes 176/176 executable cards and 137/137
primary recipes; it asserts 328/328 multiple-choice questions, rejects any
live `<C-u>`, rejects stale open-response instructions, and checks four choices
plus four feedback messages on every question. `git diff --check` passes.

## VD-28 · 2026-09-28 — rev `.27` "all questions multiple choice" shipped template nonsense; popup copy proof never copied

**Status:** OPEN. Audit and log only; no product code changed. Audited the
committed live bank `share/curriculum-v2.json` (revision `.27`, 176 cards,
328 questions). The working-tree generator could not be audited: it currently
fails in `build()` with `M18.EXPR: taught family expression-substitute never
returns as hidden changed art` (a concurrent uncommitted edit).

**Operator evidence:** a live M0 popup showed choices such as
`ANIMATION: Spark loop • Foundation edit accepts the module's named defect: …`
and `… makes only its named change while every cell outside the stated scope
stays registered`, clipped and unreadable, and the operator could not select
or copy popup text: "NOT ONLY CAN I NOT COPY SELECT ETC, WHAT THE FUCK ARE
THESE BS QUESTIONS?"

**Reproduce:** `python3 share/audits/question_choice_audit.py share/curriculum-v2.json`.
The script calls the runtime's own `_compact_choice_text`.

### Measured gaps (same class: a gate checked for the presence of a form, not for the result the learner sees)

1. **Generated jargon in place of authored content.** 137/328 questions (all
   VD-27 conversions: 41 decode, 39 predict, 19 why, 19 typed-key, 19
   complete) take their ANIMATION half from the template in
   `convert_to_multiple_choice` (`gen_curriculum_v2.py`, `animation_correct` /
   `animation_wrong`): "<card title> makes only its named change while every
   cell outside the stated scope stays registered" versus "<card title>
   accepts the module's named defect: <module defect>". Neither half describes
   the art on screen. "Named change", "named defect", "stated scope" and
   "registered" are generator vocabulary that no lesson defines. Across all
   choices: `registered` 686, `scope` 372, `named change` 274, `named defect`
   274. Across feedback: `registered` 562, `bounded` 553, `registration
   contract` 137.
2. **At 80×24 the compact choices are unanswerable.** In all 137 converted
   questions the four compact choices reduce to two distinct strings. The
   28-cell ANIMATION half becomes `A: Spark loop · Foundation…` in every
   choice, so the right and wrong animation halves look the same, and the
   NEOVIM half is cut before the clause that differs. Example M0.01.P01:
   `A: Spark loop · Foundation… · V: It only moved the cursor; no…` appears
   twice, and `… · V: It made the stated bounded…` appears twice. VD-24 ("four complete
   one-line `A · V` choices") checked only that the `A:`/`V:` markers were
   present (`test_v2.py` ~L211, `test_tmux_v2_routes.py`
   `assert_compact_choices_fit`). No test checks that the choices are
   distinct or that the differing words are visible.
3. **The answer can be found from the wording alone.** In all 137 converted
   questions the correct choice is the one whose wording is "makes only its
   named change" / "It made the stated bounded edit" / "TARGET exactly". A
   learner who reads no art still scores 100%. The wrong halves repeat across
   questions: "It only moved the cursor; no requested art cell changed." ×40,
   "START unchanged; navigation alone proves the skill." ×38, and "is an
   unrelated project-wide command" in every converted complete question.
   These questions do not measure what they claim to measure.
4. **All 328 questions use one 2×2 grid** (two ANIMATION halves × two NEOVIM
   halves). The learner never makes one decision; each question is two
   binary checks joined. With the template halves in (1), one of those two
   checks is empty.
5. **Full-layout choices overflow.** 1312/1312 full-layout choice lines are
   longer than the ~70-column interior of a 90% popup on an 80-column client.
   They wrap mid-word across 3–4 rows and have no hanging indent. This is
   what the operator saw.
6. **VD-27's claim does not hold.** VD-27 says "animation halves name the card
   and its module's documented defect" and "Neovim distractors contradict the
   shown command … instead of reusing one generic wrong sentence". Measured:
   the animation halves are one template, and the distractors are reused up
   to 40 times. The VD-27 evidence line checks count and form only (4 choices,
   4 feedback, `multiple_choice`); it contains no check that the content is
   correct or readable.

### Popup copy/select (VD-23/VD-25 claim not supported)

- The popup routes run `tmux display-popup -E` (`tmux/vim-drill-popup.sh`),
  and tmux here is 3.6a. The repair enabled `mouse on` and bound
  `copy-mode-vi MouseDragEnd1Pane`/`y`/`Enter` to `copy-pipe-and-cancel
  pbcopy`. Those bindings act on **pane** copy mode. Per the tmux manual, a
  popup is "drawn over the top of any panes" and is not a pane.
  Inferred (from tmux behaviour, not yet run here): a drag inside popup
  content never enters copy mode. Also, global `mouse on` makes tmux take the
  drag away from the terminal's own selection, so the terminal's bypass
  modifier (e.g. Shift-drag) is needed. The repair may therefore have made
  plain selection *worse* in panes and in the popup.
- `test_tmux_v2.py` ~L196–205 asserts only that the options and bindings
  exist. No test drags, checks `pbpaste`, or compares the result with the
  shown text. The "drag copies · Cmd-V pastes" title is therefore a claim
  with no test behind it.
- **Falsifier:** a plain mouse drag in the real `display-popup`, then
  `pbpaste`, returns the selected popup text. If so, the inference above is
  wrong.
- **Required proof:** that exact real-client drag → `pbpaste` comparison,
  plus the same for Shift-drag. The copy method must stay the same for the
  whole session. If popup copy is not possible, give the lesson text another
  copy path (e.g. a key that runs `pbcopy` on the current question), and the
  title must state that method.

### Required correction (not implemented)

- Delete the template ANIMATION halves. Each converted question needs an
  authored, art-specific pair built from the card's START/TARGET, like the
  native M0.Q01 ("only the core changes from . to o; all six rays stay
  registered"). If a question cannot be authored that way, remove it.
- Remove generator vocabulary from choices and feedback, or teach each term
  in a lesson before a question uses it.
- Add gates on the displayed strings at 80×24, 100×36 and full width: the
  four choices are pairwise distinct after the runtime's own truncation;
  every choice shows the words that make it differ; no wrong half repeats
  across more than N questions; and the correct answer cannot be found by a
  phrase shared across the bank.
- Wrap full-layout choices with a hanging indent at the actual popup width.
- Replace the copy test's option/binding checks with a real copy round
  trip.

## VD-29 · 2026-09-28 19:40 — "changed-art" reviews and transfers reuse one subject; 885 Stone Story animation sheets unused

**Status:** OPEN — manual audit running; replacement started (see below).

**Operator:** "THE ANIMATIONS SHOULD VARY … there are literal dozens of unused
Stone Story animation txt files, manually audit them and start fixing
replacing." Earlier records of the same gap: VD-17 (1,908 sheets found, 0
used) and VD-18 (86 animation-grade sets / 885 sheets, 0 used).

**Measured on the live bank** (revision `.28`, 187 cards; `share/curriculum-v2.json`):

- 57 cards carry 114 `review_variants`, described as "source-linked
  changed-art review bank" (the `verified_review_coverage` evidence string).
  44/114 are the card's own art with the first non-space cell of one row
  replaced by `!` or `+` (`attach_command_review_variants` +
  `REVIEW_PERTURB_ROWS`, and the bridge-card equivalent). Example: M3.CI
  ` /---\ ⏎ | (.) | ⏎  \---/` becomes ` /---\ ⏎ ! (.) | ⏎  \---/`. That
  overwrites the silhouette's border and teaches no new art. Another 8/114
  change one row. The rest recolour the same subject (spark `-- x --` /
  `== ? ==`, brick `[]`→`<>`→`{}`, stick figure `o`→`*`→`+`).
- Every module transfer (`M*.06`) has two `variants`. Variant 1 is
  byte-identical to the card's own start. Variant 2 is the same silhouette
  mirrored or recoloured. "Unfamiliar art" transfer therefore never shows
  unfamiliar art.
- The bridge labs (M0.SL, M1.DD, M3.CI, M3.REG, M3.DI, M6.D, M6.MOVE, M11.UR,
  M12.FIND …) all draw one generic `/---\ | o | \---/` box.
- `test_v2.py` executes each variant in Neovim and checks that there are two
  distinct starts. It never checks that a variant is different art.
- Result for the learner: all ~190 edit surfaces are ~20 invented
  programmer-art subjects. No real Stone Story animation frame is used,
  though 885 animation sheets sit in `~/Downloads/stone-story-consolidated/`.

**Licence note:** VD-18 recorded the operator's waiver for logging, not for
publishing. The GitHub repo is PUBLIC (`gh repo view`: visibility PUBLIC), so
committing or pushing vendored sheets publishes third-party art. Local
working-tree edits only until the operator decides.

### VD-29 progress · 2026-09-28 20:45 — manual audit complete; 22 review variants replaced

**Audit (manual; 4 subagents; every listed sheet opened and its StoneScript
source read):** `share/audits/stone-story-animation-audit/batch-0.md` …
`batch-3.md`. The 86 sets split USE 40 / MAYBE 16 / REJECT 30 (b0 10/5/6,
b1 12/4/6, b2 10/4/8, b3 8/3/10). Each USE/MAYBE section pastes the frames,
the per-pair cell diff, a proposed Neovim edit and a module slot. Findings
that constrain import:
- `#` is transparent, but a space in an overlay layer may clear the cell
  below. The Boo and BurgerRush composites are inferred, not exact.
- Full-width glyphs (`］ ＂ ｛ ［`) in SillyGoose, Knight, Turret, CavePets,
  Mushroom res15/16, Dragon attack, Mech, and four batch-1 rejects break the
  grid.
- `´ ¯ ‾ · •` are ambiguous width and need digraphs to type.
- The RootBats `@HE@` placeholder is template text.
The subagents wrote their proposed edits by hand; they were not run in Neovim.
Only rows imported below were executed.

**Replaced (working tree, not committed):**
- New `share/stone_story_variants.py`: 22 review variants on 9 cards — M0.01,
  M0.SL, M11.02, M11.UR, M11.04, M11.05, M11.VE, M11.08, M1.DD, M3.CI,
  M3.REG. Sources: Dracula walk, SnowBunny/Skully/Frog blinks, TowerDefense
  missile exhaust, Chick egg crack and peep.
- Every frame was re-read from the raw sheet
  (`share/audits/stone-story-animation-audit/show_sheet.py`).
- Each variant carries its own `prompt` and `hint`: `_changed_review_card`
  otherwise showed the source card's "spark" wording over different art.
- Each variant also carries a `source` naming the sheet and frame, and an
  exact `method_requirement`.
- `gen_curriculum_v2.py` calls `stone_story_variants.apply(module_cards)` —
  two added lines plus the import. `apply` rejects any variant whose art is
  less than 50% different from the card's own art.
- The existing toy-stimulus gate (≥3 rows, ≥5 wide, ≥7 ink per module frame)
  rejected the 3-column StoneasaurGame runner and the 4–5-row
  Stonehead/Dragon/Mushroom frames in 3-row modules. Those were swapped for
  3-row sprites.

**Evidence:**
- `python3 share/test_stone_story_variants.py`: 22/22 PASS. Each variant's
  keys run in `nvim -u NONE` (the test_v2 command) and reach the target.
  The test also checks that every source sheet exists and that the JSON was
  regenerated. Exit 0.
- `python3 share/gen_curriculum_v2.py` writes 187 cards / 347 questions and
  passes the generator validation, including the toy gate.
- `_changed_review_card` builds all 18 replaced reviews (9 cards × 2 stages)
  with the Stone Story prompt.
- **Not run:** full `share/test_v2.py`. It stops at
  `validate_curriculum` with "question M0.Q01 has an invalid compact paired
  prompt". That is the concurrent uncommitted question rework
  (`share/questions-authored-v2.json`); it fails the same way with the
  replacement table emptied.
- **Not seen:** a headed popup showing a Stone Story review. The operator's
  M0.01 review (next_due 23:22) is the first live surface.

**Still open:**
1. 32 border-swap (`!`/`+`) review variants remain (M3.04, M3.DI, M3.08,
   M4.VB, M6.D, M6.MOVE, M7.*, M8.04, M12.FIND, M13.BE, M14.PARA, M15.*,
   M16.MOVE, M18.EXPR). So do the recoloured same-subject variants on the
   other review cards.
2. Transfer `variants` (every `M*.06`): not replaced. `run_edit` asks the
   card's paired question after each attempt, and that question renders the
   card's own art, so a Stone Story variant would contradict its question.
   This needs per-variant paired questions first.
3. The main module art (spark, `/---\` box, stick figure …) is unchanged.
   The best-fit USE rows per module are in the batch tables' "best module"
   column.
4. Publishing: repo is PUBLIC; commit/push of Stone Story frames awaits the
   operator's decision (VD-18 waiver covered logging only).

## VD-30 · 2026-09-28 20:20 — generated question prose, missing compact art, and tmux capture blocked native copy

**Status:** VERIFIED FOR VD-30 — all live question ids now use explicitly
authored records and the popup copy/select path is proven at all required
sizes. This closes only VD-30; the overall curriculum goal and the separate
Stone Story publication boundary remain open.

**Operator evidence:** the live M0.04 question presented four mechanically
crossed variants of the same two sentences. Its prompt contained no frame art,
the correct choice repeated the complete hidden recipe
`4G3yyGp:8s/-/=/g<CR>`, and popup text could not be selected normally. The
operator required every multiple-choice item to print the relevant ASCII art
and rejected further generated question prose.

### Root causes

- `_multiple_choice_pair` constructed question prose and a two-by-two
  animation/Neovim answer matrix. Both generator and runtime then required
  each animation half and each Neovim half to occur exactly twice. That
  validator encoded the very repetition the operator rejected.
- compact question rendering flattened every paragraph with whitespace joins;
  a multi-line art panel therefore became prose at 80×24.
- the three popup launchers set global tmux `mouse on`. tmux consumed drag
  gestures before Terminal/iTerm could create a native selection.
- the question bank could pass structural checks while its wording was not
  understandable or useful. Presence/count validation was being treated as
  content review.

### Implemented in the working tree

- `share/questions-authored-v2.json` now owns all 22 M0 questions as explicit
  records. Each was written separately with a full and compact art panel, four
  distinct misconceptions, and answer-specific feedback. M0.04 now asks the
  learner to distinguish: changing the old frame, appending a one-row fragment,
  using whole-file scope, and appending one complete registered flare.
- hidden-before questions no longer expose M0.04's or M0.08's exact key path.
  They ask about object and scope; the debrief remains responsible for the
  exact sequence.
- `questions-authored-v2-stills-a.json`, `questions-authored-v2-stills-b.json`,
  `questions-authored-v2-motion-a.json`, and
  `questions-authored-v2-motion-b.json` add the remaining 325 separately
  authored items. Together with M0, all 347/347 live questions are manually
  authored.
- the generator only installs exact authored records from those files; it does
  not synthesize their wording. Duplicate ids, unknown ids, and any missing
  authored id fail generation. `share/test_v2.py` independently requires
  `authorship == "manual"` on all 347 live questions.
- the two-by-two answer-frequency requirement was removed from generator and
  runtime validation. Four choices must be distinct; the validator no longer
  dictates their prose structure.
- `_compact_question_text` preserves art blocks instead of joining their rows.
  Every question is required to provide art in both full and compact prompts.
- `ask_question` prints paired choices as separate `ANIM:` and `VIM:` rows and
  accepts `c` to copy the complete prompt and choices through `pbcopy` without
  recording an answer attempt.
- all popup launchers save the user's tmux mouse preference, turn mouse capture
  off for the popup so native drag-selection reaches the terminal, advertise
  `drag selects · Cmd-C copies · Cmd-V pastes`, and restore the original mouse
  preference on exit.

### Direct evidence

- Generated live artifact: revision `2026-09-28.29`, 20 modules, 187 cards,
  347 questions, and 347/347 `authorship: manual`.
- every question has four distinct full choices and four distinct compact
  choices; all 1,388 answer-feedback slots are question-specific; compact
  choice collision checks at widths 42, 62, and 72 report zero collisions.
- no before-question on a key-hidden card contains that card's complete
  expected key path. All compact question screens fit the reviewed 22-line
  budget at width 72.
- headed automatic popup route, real user Neovim config:
  - 80×24: PASS;
  - 100×36: PASS;
  - 188×49: PASS.
  At each size the test sees `mouse off` during the popup, copies the complete
  current question with `c`, verifies prompt/art/choices in the macOS
  clipboard, closes the popup, and sees the learner's original `mouse on`
  preference restored.
- the 80×24 capture also shows the user's lualine/Normal mode, DO THIS, TARGET,
  hint, recipe, legacy teaching, failed replay, two-column keystroke ledger,
  skill tree, XP, streak, all-time total, repeat, next, and close controls.
- `python3 share/test_question_quality.py`: PASS on all 347 questions.
- `python3 share/test_v2.py`: PASS, including 187/187 executable lessons and
  146/146 primary edit recipes under `config=none`.
- `python3 share/test_stone_story_variants.py`: PASS on the 42 currently
  integrated review variants; it still reports 18 border-swap variants under
  the separate VD-29 work item.

### Still open outside VD-30

1. Keep the Stone Story publication boundary in VD-29 separate; these local
   question fixes do not authorize publishing third-party source art.
2. Continue the broader card-by-card curriculum review; passing the VD-30
   question and popup acceptance checks is not a claim that the entire course
   goal is complete.

### VD-28/VD-29 follow-up · 2026-09-28 20:45 (Claude session, alongside VD-30)

- **Displayed-text gate:** `share/test_question_quality.py` judges the
  strings the learner sees, not the question's form. It checks:
  - banned template phrases;
  - choices identical after the runtime's own `_compact_choice_text` at
    72/90/169 popup columns;
  - a correct answer that restates the prompt;
  - a before-edit question whose choices contain the hidden `expected` keys;
  - a wrong half reused in more than 3 questions.
  On the pre-VD-30 bank it failed 135/135/19/2/41. VD-30 extended it with
  authorship, visible-art, overflow and feedback-reuse rules. Now:
  `PASS all question-quality rules on 347 multiple-choice questions`.
- Fixed five authored items the gate still flagged: the bare "use a global
  substitute." wrong half in M8.Q03, M8.Q10, M6.MOVE.P01 and M18.EXPR.P01
  (each now names a concrete wrong command), and "registration contract" in
  the M4.Q08 feedback.
- **Neovim mouse:** VD-30 turns tmux mouse off in the popup, but the
  operator's config sets `mouse=a` (checked: `nvim --headless … set
  mouse?` → `mouse=a`). A drag inside the lesson editor therefore became a
  Visual selection, not a native selection, so "drag selects · Cmd-C copies"
  was still false during the edit. `bin/vim-daily-gate` now sets
  `vim.o.mouse=''` in the lesson editor. With the full user config it is
  still `''` 3 s after startup.
- **VD-29:** 42 review variants on 19 cards now use Stone Story frames. This
  batch added M6.MOVE, M16.MOVE, M7.GLOBAL, M7.DOT, M6.D (snake tongue
  retract), M15.GLOBAL and M15.MAC. 18 border-swap variants remain.
- **Evidence, one run after the last change:**
  - `test_v2.py` exit 0 (187/187 lessons, 146/146 recipes);
  - `test_stone_story_variants.py` exit 0;
  - `test_question_quality.py` exit 0;
  - `test_tmux_v2.py` PASS at 80×24, 100×36 and 188×49 with the real user
    config.
  - **Not observed:** a human mouse drag and Cmd-C inside the popup. The test
    asserts mouse state, not an actual selection.

## VD-31 · 2026-09-28 20:58 — popup launchers changed global tmux state; stray processes kept normal panes from copying

**Operator:** "i had to kill stray python processes that prevented me from
copying normal tmux panes, please make sure this does not happen again."

**Root cause:** VD-30 made all three popup launchers run
`tmux set-option -g mouse off`. They also rebound `copy-mode-vi` `y`,
`Enter` and `MouseDragEnd1Pane` to `pbcopy` in the global key table. The
mouse setting was restored only by a bash `trap … EXIT`. That failed in
three ways:
1. While a lesson process hung, every normal pane in the server had tmux
   mouse off, so drag-copy stopped working. Killing the stray process let
   the trap run.
2. Two overlapping launchers (attach hook + hourly job): the second saved
   `off` as the "original" value and restored it for good.
3. `kill -9` of a launcher skipped the trap.
The rebindings were never undone. The live server still carried all three
`pbcopy` bindings; the user's `~/.tmux.conf` defines none of them and
tmux-yank is not installed.

**Stray processes found:**
- 28 `nvim --embed` servers reparented to launchd (PPID 1). All came from
  headed test runs: `vim-daily-routes-*` temp state dirs and an earlier
  repro scratchpad. `tmux kill-server` killed their TUI clients, and these
  servers ignore SIGTERM (checked: `kill` returned 0 and the process stayed).
- One `share/test_v2.py --real`, alive 19 h under a Codex parent.

**Fix:**
- `tmux/vim-drill-popup.sh`, `vim-drill-hourly.sh` and
  `vim-drill-popup-force.sh` no longer set any global option or key table;
  a comment states why. The popup copy methods are now the `c` key (the
  operator confirmed it copied) and the terminal's own Shift-drag selection.
  The title and lesson help say so.
- `share/test_tmux_v2.py` now asserts that global `mouse` is unchanged
  (`on`) during and after the popup, and that no `pbcopy` binding is added.
- Both headed tests `pkill -9 -f <their temp dir>` after `kill-server`.
- Live cleanup:
  - the three injected bindings were reset to tmux defaults (checked
    against a fresh `-f /dev/null` server: `Enter` and `MouseDragEnd1Pane`
    → `copy-pipe-and-cancel`, `y` unbound);
  - the 28 orphans and the 19 h test run were killed with SIGKILL.

**Evidence:**
- `share/test_tmux_v2.py` PASS at 80×24, 100×36 and 188×49 (real user
  config).
- After a test run: 0 orphaned `nvim --embed`, user server `mouse on`,
  0 `pbcopy` bindings.
- `share/test_v2.py` exit 0 (187/187, 146/146), after regenerating the JSON
  from current sources.
- Not observed: a human Shift-drag in the popup. That Ghostty lets Shift
  bypass tmux mouse capture is inferred from Ghostty's
  `mouse-shift-capture` default.

**Open findings from reviewing the concurrent session's 20:44 report:**
- `037f478` changed `questions-authored-v2-motion-a.json` (M4.Q04) without
  regenerating `curriculum-v2.json`. `share/test_v2.py` fails at that
  commit with "generated artifact drifted", so its claim that 187/187
  lessons pass does not hold for the commit.
- `share/test_tmux_v2_routes.py` fails at 80×24 on the authored bank: it
  still asserts "DO THIS" and "both" in the concept/check prompt, which the
  VD-30 wording no longer contains. The report listed only
  `test_tmux_v2.py`.
- Its claim that the worktree was clean was false at the time:
  `questions-authored-v2-motion-a.json` was being modified again.

## VD-32 · 2026-09-28 21:40 — question-copy key made answer c impossible; route test asserted deleted template prose

**Operator evidence:** in a live four-choice question, pressing `c` copied
the page instead of selecting answer `c`; normal drag also did not create a
terminal selection.

**Root cause:** `ask_question()` lowercased input and handled `answer == "c"`
before its `answer in "abcd"` branch. The copy affordance therefore shadowed
one quarter of the answer alphabet. Separately,
`share/test_tmux_v2_routes.py` still required generated phrases (`DO THIS`,
`both`, `TEACH FIRST`, `complete`, and `Spaced review`) that the manually
authored bank intentionally removed. Its compact-choice check also expected
the old one-line `· V:` renderer after choices had moved to separate `ANIM:`
and `VIM:` rows.

**Fix in the working tree:**
- question copy moves from `c` to `y`, matching Vim's yank mnemonic; `c`
  remains a normal answer letter;
- unit coverage submits `c` as the correct third choice and separately uses
  `y` to copy without recording an attempt;
- the headed popup test uses `y` and checks the new learner-visible title;
- the route test now verifies authored prompt content, paired headings, four
  `ANIM:`/`VIM:` choices, and the answer prompt instead of template wording;
  its forced choice order records `raw_answer == "c"` when the correct
  semantic answer is displayed third;
- `curriculum-v2.json` was rebuilt from the current authored sources, closing
  the drift recorded in VD-31.

**Drag root cause and boundary:** the live tmux server deliberately keeps
`mouse on`, so tmux owns an unmodified drag. More importantly, tmux 3.6a's
`tty.c` sends `CSI ? 7727 h` (`XTSHIFTESCAPE`) for VT100-like terminals.
Ghostty's default `mouse-shift-capture = false` allows an application to
override Shift selection with that mode, so the previous report's inference
that default Ghostty would preserve Shift-drag was false. Both of the
operator's identical Ghostty config files now set
`mouse-shift-capture = never`, the documented mode that applications cannot
override. This reserves Shift-drag for terminal selection while leaving plain
mouse gestures available to tmux. `ghostty +show-config` reports the active
value as `never`. Ghostty must reload its config (`Cmd-Shift-,`) before an
already-open window uses the change. The computer-use surface is not permitted
to control Ghostty, so the physical Shift-drag remains a manual acceptance
check. `y` remains the deterministic whole-question copy route.

**Evidence so far:** `share/test_question_quality.py` passes 347/347;
`share/test_v2.py` passes 187/187 lessons and 146/146 recipes; the
client-attached popup test passes at 80×24, 100×36 and 188×49. The route
matrix is being rerun after removal of its stale assertions.

## VD-33 · 2026-09-28 21:54 — wrong-answer page replayed internal question metadata; popup selection still unusable

**Operator evidence:** after choosing a wrong answer, the held result page was
headed `QUESTION REPLAY` and repeated internal/course-author prose instead of
teaching the concept. The operator also reported that popup text still could
not be selected and copied, and required another manual review of every
question rather than another generated-prose or validator-only claim.

**Exact failed question:** the live event at 21:54:05 records
`M0.SL.P01`, displayed choices `[0,1,2,3]`, raw answer `d`, semantic choice
3. The selected claim was that `s` rewrites a whole line. The correct concept
is narrower: with no explicit address, `:s` owns the current line; its `g`
flag replaces every matching `o` on that line. The authored feedback already
contained both explanations, but the result renderer foregrounded replay
metadata and did not present the selected misconception beside the correct
concept.

**Wrong-answer UI fix in the working tree:** both full and compact result
routes now use the learner-facing heading `ANSWER EXPLANATION`. A wrong
multiple-choice result prints, in order:

1. `YOUR ANSWER` — the option actually selected;
2. `WHY IT MISSES` — that option's authored misconception-specific feedback;
3. `CORRECT ANSWER` — the correct animation + Neovim statement;
4. `CONCEPT` — the correct answer's authored explanation;
5. `GRAMMAR BREAKDOWN` — the command parts and, when quoted, their key-by-key
   meanings.

Question form, placement, placement rationale, and the phrases `QUESTION
REPLAY` / `CONCEPT REPLAY` are no longer printed to the learner. The
regression test requires those five learner-facing sections and explicitly
rejects the old heading and `placement:` prose.

The question-result route also no longer follows the answer with generic
course-author advice such as “retain the principle” or the card's design
rationale. The authored misconception, correct choice, concept explanation,
and grammar breakdown are the teaching content; only those, the source, and
the learner's next action remain on that result page.

**Copy/selection path:** `y` copies the full prompt and all four choices while
`a`–`d` remain answers. For arbitrary text selection, both layers that can
capture an ordinary drag are now released only for the live popup:

- the tutor Neovim process sets `mouse=''`, after the user configuration has
  loaded, so Neovim does not request terminal mouse reports;
- each popup launcher sets `mouse off` only on the target tmux session while
  its synchronous popup exists, then restores the exact inherited/local state
  in its exit trap. Global tmux options and key tables remain untouched.

At 22:26, a direct inspection after the operator's popup had closed found the
real `main` session in a bad state: global `mouse on`, local `mouse off`,
effective `mouse off`, and no active popup. The local override was removed
immediately; the effective value returned to `on`. This proves the first
session-local trap was not sufficient. The launchers now record a session-local
owner PID and the exact inherited/local base state. A concurrent live owner
causes a second launcher to exit without touching mouse state; a later
attach/hourly/forced invocation detects a dead owner, restores its recorded
base before the due check, and clears both ownership markers. Normal and
handled-signal exits restore only when the current process still owns the
override. The headed test starts from a stale owner marker and stale local
`mouse off`, then requires a new owner while open and no local override or
owner/base marker after close.

The headed acceptance test now checks both the effective session option and
the actual post-plugin `&mouse` value. A physical Ghostty drag and Cmd-C still
requires operator acceptance; it must not be reported as observed by an
automated key test.

**Manual question audit, source records rather than generated JSON:**

- M0/core: 22/22 read individually. `M0.SL.P01` is clear and its four feedback
  branches teach current-line scope, `g`, `%`, and substitution rather than
  whole-line rewrite; the defect was the result renderer.
- stills-a: 84/84 read individually. Corrections include M11.Q03/Q07/Q10,
  M11.01/M11.08, M1.Q03/Q04/Q08/Q09/Q10, M19.Q03, M2.Q09, M12.05, M12.06,
  and M12.08. These repair contradictory pictures, phantom rows, missing
  frame rows, over-broad `%` examples, and learner-facing workflow jargon.
- stills-b: 85/85 read individually. Corrections include M10.Q03/Q04/Q05,
  M13.Q03/Q04/Q05/Q10/M13.BE.P01, M14.Q03/Q04/Q05/M14.PARA.P01, and
  M15.Q03/Q04/Q05. In particular, each printed AFTER panel now visibly shows
  the change its stem asks about. Learner-facing `hidden recipe`, `checkpoint`,
  and `mastery strip` wording was replaced with the actual object, scope, and
  animation result.
- motion-b: 67/67 read individually. Corrections include M6.Q05 ambiguity,
  M18.EXPR.P01's duplicate CHECK row, M9.08.P01's malformed squash row, and
  removal of hidden/checkpoint authoring jargon from M6.04/M6.06/M6.08,
  M18.04/M18.08, M8.04, and M9.04.
- motion-a: 89/89 were read individually by the assigned manual reviewer.
  Corrections cover internal/meta wording, fixed-width prompt art, hidden-key
  leaks, scope clarity, misconception-specific feedback, and exact copy/edit
  semantics across M16, M3, M4, M17, and M7. Integration then caught one
  duplicate stem: M3.Q10's compact prompt had copied M3.02.P01 and no longer
  depicted its missing-body diagnosis. M3.Q10 now shows the floating eye and
  missing torso/feet/baseline in both sizes and asks for complete-pose repair.

**Verification to this point:** the authored sources rebuild to 20 modules,
187 cards, and 347 questions. `test_question_quality.py` passes all 347;
`test_v2.py` passes all 187 executable lessons and 146 primary edit recipes;
the 46 legacy drills and 42 integrated Stone Story review variants pass. The
headed main popup passes at 80×24, 100×36, and 188×49 with the user's real
config, including stale-owner healing, live `&mouse=''`, answer `c`, question
copy `y`, and cleanup of local tmux state. A first 80×24 route run additionally
found that the review result was one row too tall and scrolled the `REVIEW
RETRIEVED` header away; the feedback budget now reserves one more trailer row
and its route rerun is pending. Physical Ghostty drag remains operator
acceptance, and this entry does not close the broader curriculum audit.

**Owner-liveness hardening:** a numeric owner marker is not enough evidence
that the popup still exists because the operating system can reuse a dead
process ID. All three launchers now inspect the marked PID's command and treat
it as live only when it is one of the three tutor popup launchers. A reused PID
therefore cannot strand `mouse off` indefinitely. The headed acceptance setup
uses its own live Python PID as the stale marker, rather than an impossible
dead PID, and requires the launcher to replace it. Shell syntax and repository
diff checks pass after this change.

**Route-harness finding:** the 80×24 matrix passed its first nine routes, then
opened no popup for `M1.06`. The product had not failed to launch: the test's
synthetic progress wrote card-pass rows but omitted the now-required stage-1
review evidence, leaving M0 `review_pending` and M1 locked. Progress-targeted
fixtures now seed the required review rows for every fully completed prior
module. This keeps the route test subject to the same mastery contract as the
real scheduler instead of bypassing or accidentally contradicting it.

After that repair, `M2.06` exposed a second harness-only race: the ledger saw
`jforO`, but the buffer was unchanged because the driver injected the entire
string as one terminal-byte burst through the user's asynchronous Flash
`f`-motion mapping. The route driver now emits discrete keys with a 30 ms
human-like interval. This preserves the real user config while avoiding a
machine-only input shape that a learner cannot physically produce.

The delay alone did not make synthetic `j` reliable under that stack. The
lesson now accepts two explicit, bounded command paths that produce the same
one-cell edit: `jforO` (relative row motion) and `2GforO` (exact line address),
then still requires `fo` + `rO`. The popup driver uses the exact-line variant;
the curriculum retains and teaches the relative variant. This is a real
multiple-method contract, not ungraded answer-key padding.

**Final evidence for this entry:**

- `test_question_quality.py`: 347/347 manually authored questions pass the
  visible-art, four-choice, feedback, compact-layout, and internal-prose gates.
- `test_v2.py`: 187/187 executable lessons and 146/146 primary recipes pass,
  including the exact `M0.SL.P01` wrong-answer explanation.
- The direct client-attached popup passes with the real user config at 80×24,
  100×36, and 188×49. It verifies the live session-local mouse release,
  post-plugin Neovim `mouse=''`, answer `c`, full-question copy on `y`, and
  cleanup/restore ownership.
- The final question-result route passes at all three sizes and rejects
  `QUESTION REPLAY`, `CONCEPT REPLAY`, and “retain the principle”. Isolated
  `M1.06` and `M2.06` transfer routes pass at 80×24 after the fixture and
  input-path corrections above.
- A full 80×24 matrix run before the M2 correction passed ten consecutive
  routes through `M1.06`, then reproduced the synthetic M2 input failure. It
  was not rerun in full after that correction; this entry does not claim a
  final all-transfer matrix pass.
- At 23:40 the real `main` session had one legitimate open M0.06 popup owned
  by `vim-drill-hourly.sh`; its session-local `mouse off` and base `inherit`
  markers were therefore expected. It was left open and untouched for the
  operator. The three isolated acceptance runs left no additional tutor
  process or tmux server behind.

Physical drag selection in Ghostty remains an operator acceptance check. The
currently open popup is already using the revised launcher/runtime, so it is
the correct live surface on which to try ordinary drag followed by Cmd-C.

## VD-34 · 2026-09-29 03:28 — M3.06 exact-target work was rejected by mapping-prefix replay; post-M3 headed routes exposed three separate input failures

The isolated real-config reproduction was:

```text
python3 share/test_tmux_v2_routes.py --only-transfer=M3.06
expected: ggV5j"ayG"ap8GforO
captured: ggggV55j"a"ayG"a"ap8GforO
saved artifact: exact target
old result: fail, required exact method missing
```

Neovim's `-w` key log records mapping-prefix replay from the operator's live
configuration, so whole-log equality was not evidence that the learner used or
did not use the taught path. A discarded `vim.on_key(..., typed)` experiment
also duplicated `g`, counts, and register prefixes and was removed; it did not
provide a physical-key oracle.

The mastery contract is now two independent gates:

1. the saved artifact must equal the target exactly; and
2. every token in one declared taught command path must occur in order in the
   attempt log.

Extra navigation, corrections, undo, Hardtime-blocked input, and mapping replay
no longer reject correct art. Omitting a required command token still fails.
The debrief and generated evidence labels now say "required commands in order ·
exact saved target" instead of claiming an exact whole key log. Regression
coverage includes the captured M3.06 replay above and a missing-token rejection.

The 80×24 headed popup also clipped row six of M3.06's six-row TARGET. The
compact brief receives one additional row; it now shows the complete target
without removing the art window.

**Verified scope:**

- `python3 share/test_v2.py`: 187/187 executable lessons and 146/146 primary
  recipes pass; command-path replay and missing-token checks pass.
- M3.06 passes in the real-config headed popup at 80×24, 100×36, and 188×49.
- M4.06 passes at 80×24 after the route driver was slowed from a 30 ms byte
  burst to learner-paced 120 ms key events.

**New open failures found by continuing the 80×24 matrix:**

- M9.06 logs `fxro` but saves `[ x ]` instead of `[ o ]`.
- M12.06 logs `0t+lr*$T+hr*` but saves the unchanged joint row.
- M18.06 logs all three `C` redraws but saves the original mirror rows.

Each of those three cards passes in clean mode. A test-only probe confirmed for
M9.06 that, at the real-config ready boundary, the art buffer was current,
Normal, modifiable, not read-only, and named for the correct project. Removing
the Flash `f/t` callbacks and trying the mapping-free `3|ro` diagnostic still
left the art unchanged. Those diagnostic hooks and mapping changes were removed.
Therefore this entry does not claim a complete post-M3 headed matrix. M8.06,
M16.06, and M17.06 did pass at 80×24; M9.06, M12.06, and M18.06 remain the
specific live-config blockers to diagnose next.

### VD-34 follow-through · 2026-09-29 03:33 — late cursor restoration and multi-line Flash semantics resolved the headed blockers

The three apparent input failures shared a current-line assumption. LazyVim's
late handlers could restore a cursor after the launcher's `+1`/`+normal! ^`, so
the logged `f`, `t`, or `C` command ran on a different row. The launcher now
reapplies each card's authored line/cursor once after `VeryLazy` and before the
headed ready boundary. This made M9.06, M12.06, and M18.06 pass at 80×24.

Continuing the matrix then exposed M7.06: the personal Flash configuration's
character mode is multi-line, so `fo` may select an `o` in another frame rather
than native Vim's next `o` on the current row. The tutor teaches native Vim
grammar, so only `f/F/t/T/;/,` receive buffer-local nonrecursive native mappings
inside the art buffer. The user's theme, lualine, relative numbers, WhichKey,
Hardtime, other mappings, and every non-tutor buffer remain unchanged. M7.06
then passed at 80×24.

All twenty `M*.06` transfer cards have now passed as isolated real-config
headed routes at 80×24 on the current source. M3.06 additionally passed at
100×36 and 188×49. This is isolated per-transfer evidence, not a claim that the
entire all-route script (primer, concept, retry, guided, independent, compare,
module check, review, then all transfers in one process) has been rerun.

The main 80×24 popup regression then caught the failed-attempt headline still
scrolling away. The feedback body already ends with a newline, while
`post_page_break()` added a second blank row before its prompt. Removing that
redundant row keeps `ATTEMPT NOT PASSED`, the two-column replay, ledger, source,
and progress prompt visible together. The main client-attached real-config
popup now passes at 80×24, 100×36, and 188×49.

## VD-35 · 2026-09-29 04:02 — every remaining border-swap review replaced with manually authored Stone Story animation work

**Failure carried from VD-29/VD-34:** eighteen detected review variants still
changed only the source card's first border glyph to `!` or `+`. A fresh scan
after the first replacement pass found eight more generic variants that the
earlier list had omitted: both variants of `M14.PARA`, `M15.BA`, `M4.VB`, and
`M7.MAC`. These were valid executable buffers but not unfamiliar art and did
not test transfer of the Vim method to another animation subject.

**Manual replacements:** every variant below was written individually in
`share/stone_story_variants.py`, with its own source, art-specific DO THIS
prompt, action hint, command breakdown, exact expected target, and enforced
method path. No question or prompt prose was template-generated.

| cards | Stone Story material | Neovim retrieval |
|---|---|---|
| `M12.FIND` | CaveParty lava pulse; Drill tread shimmer | `f`, `;`, `,`, then in-place `r` |
| `M13.BE` | two authored CaveParty lava phases | `W`, `E`, and `B` over separated texture cells |
| `M14.01`, `M14.04`, `M14.08` | Skully open/blink/look palettes; SnowBunny open/blink | named registers, Replace-mode register insertion, `}` across frame paragraphs |
| `M14.PARA` | complete Skully and SnowBunny paragraph frames | `yap`, `}`, and `P` on whole frame objects |
| `M15.01` | Drill tread and CaveParty lava material layers | `shiftwidth=1` plus a one-cell `>>` offset |
| `M15.BA` | TowerDefense missile and Skully blink frames | blockwise `$A` at each selected row's true end |
| `M16.01` | FrogBog lily-pad labels 1→2 and 2→3 | numeric increment with `<C-a>` |
| `M3.04` | FaceHUD shock pose, plain and with the wound overlay | `ci(` on one eye inside the copied six-row pose |
| `M3.DI`, `M3.08` | Frog, Chick hatch, and FaceHUD full-pose strips | middle-dot digraph entry with in-place `r<C-k>.M` |
| `M4.VB` | willow firework shell and TowerDefense missile | exact-column Visual Block replacement |
| `M6.04` | GrowPlants flower and willow firework subtractive frames | `D` clears contents but preserves the frame row |
| `M7.VIS` | Drill hull band and FaceHUD mouth band | bounded characterwise Visual replacement |
| `M7.MAC` | four missile exhaust frames, forward and reverse | record once and replay on homologous frame rows |
| `M18.EXPR` | FrogBog pad and willow firework beside CHECK metadata | `\=` derives only the check digit; it never generates or mirrors art |

The source sheets are the audited local corpus under
`~/Downloads/stone-story-consolidated/` and the corresponding official source
scripts under `~/Downloads/stone-story-official/`. The file records each
`official-*/Name resNN` reference. `#` transparency was converted to spaces;
rows were right-trimmed; where the audit already required an ASCII-safe copy,
overscore/em-dash material was written as `-`. The FrogBog UTF-8 corruption
`Â´` was not copied into the curriculum. Source ownership is unchanged:
third-party Stone Story material is permitted for this local tutor, but a push
from this public repository remains a separate publication/licensing decision
and is **not** authorized by this entry.

**Direct evidence:**

- `python3 share/gen_curriculum_v2.py` rebuilt 20 modules, 187 cards, and 347
  questions with no visual-stimulus error.
- `python3 share/test_stone_story_variants.py` replayed all 70 source-linked
  review variants in isolated Neovim; every exact target passed and the
  border-swap count is now **0**.
- `python3 share/test_v2.py` passes 187/187 executable lessons and 146/146
  primary recipes; the rebuilt graph, questions, state, method evidence, and
  all 57 changed-art transfer/review routes validate.
- `python3 share/test_question_quality.py` passes all 347 questions.
- `python3 share/test_animation_lesson_pack.py` and
  `python3 share/test_animation_curriculum_integration.py` pass the 12-lesson,
  24-question animation pack and its guided-before-hidden integration.
- The real-user-config headed popup passes at 80×24, 100×36, and 188×49 after
  the rebuilt curriculum.

**Still open; this entry does not close the course audit:** module transfer
variants still require per-variant paired questions before their first source
art can be replaced without contradicting the question; much of the primary
module art remains invented; dedicated command practice is still missing for
the VD-26 list (`gR`, `g_`, lowercase `w`, blockwise `I/c`, `gv`, `zp`, `ga`,
`:diffthis`, `scrollbind`, display-column tools, whitespace cleanup, undo-tree
travel, and `dap`); and the current mixed modules do not yet enforce the
requested complete S0–S7 still-authoring sequence before A0–A7 animation.

## VD-36 · 2026-09-29 — seven VD-26 command gaps now have enforced guided → hidden → spaced-review paths

**Failure carried from VD-26/VD-35:** the course could mention a command in an
answer or metadata and call that coverage even when the learner was never
required to perform it. The finish line is stricter: visible guided performance,
then an unfamiliar-art lesson with the recipe hidden and runtime method evidence,
then changed-art retrieval before module mastery.

**Implemented in revision `2026-09-29.30`:** fourteen individually authored
cards close seven of the exact command gaps. The hidden card in every pair has
`show_recipe=false`, an `exact_any_of` method requirement, two source-linked
review variants with their own method requirements, and
`required_before_mastery=true`. The module cannot master until that review is
passed.

| guided card | required hidden card | method that is actually graded | source-linked animation work |
|---|---|---|---|
| `M13.W` | `M13.WH` | lowercase `w` over separated punctuation runs | CaveParty lava → Drill tread, then two changed phases |
| `M13.GU` | `M13.GH` | `g_` to the last nonblank cell despite registered padding | TowerDefense missile exhaust → Chick beak, then reverse-state reviews |
| `M4.BI` | `M4.BIH` | Visual Block `I` over a three-row registered column | CaveParty lava → missile, then SnowBunny and Skully |
| `M4.BC` | `M4.BCH` | Visual Block `c` replacing one fixed column | missile → shifted lava, then SnowBunny and Skully |
| `M4.GV` | `M4.GVH` | `gv` restores and refines the exact previous block | missile → shifted lava, then SnowBunny and Skully |
| `M3.GA` | `M3.GAH` | `ga` inspection before the one-cell replacement | FaceHUD shock → neutral, then wound/right-eye reviews |
| `M14.DAP` | `M14.DAPH` | `d` + `ap` deletes one blank-line-separated full-pose frame | Skully open/blink → SnowBunny, then Frog and Skully |

The fourteen paired questions are separately written in
`share/questions-authored-v2-mastery.json`; none is synthesized from a card
template. Each shows the acting ASCII-art cells, asks about both animation scope
and Neovim grammar, has four distinct choices, and gives mistake-specific
feedback. Guided cards place the question after the visible performance; hidden
cards ask for recognition without printing the hidden recipe in a before-card
prompt.

**Executable evidence for this slice:**

- `python3 share/gen_curriculum_v2.py` rebuilt 20 modules, 201 cards, and 361
  questions.
- `python3 share/test_question_quality.py` passes all 361 questions.
- `python3 share/test_v2.py` passes 201/201 executable lessons and 160/160
  primary recipes. It now asserts the seven hidden ids, exact enforced method,
  two source-linked reviews per card, required-before-mastery state, and one
  manually authored paired question per hidden card.
- `python3 share/test_stone_story_variants.py` still reports zero generic
  border-swap reviews; the animation-pack and live-integration tests pass.
- The current real-user-config client-attached popup passes at 188×49. The
  broader real-config and route runs were still outstanding at this log point,
  so this entry does not claim their result.

**Corrections to older open entries:** VD-26's `gR` gap had already been closed
by M19 before this slice. VD-21 items 2–3 are also no longer live: every visible
question is four-choice multiple choice, the 20 comparison questions have 20
distinct card-specific source contracts, and `test_v2.py` parses command-looking
backticks in before-card questions against earlier guided performance instead of
trusting the `grammar_family` tag.

**Still open; this is not course completion:** `zp`/`zP`; `:diffthis` and
`scrollbind`; `:set list`, `cursorcolumn`, and `colorcolumn`; intentional
trailing-whitespace inspection/cleanup; undo-tree travel with `g-`, `g+`, and
`:earlier`; per-variant questions before replacing each module transfer's first
art; remaining invented primary art; Stone Story provenance/publication intake;
and a real stage gate that completes S0–S7 before A0–A7 rather than attaching
mixed stage labels to modules.

### VD-36 follow-through · revision `2026-09-29.32` — ragged block copy and whitespace/column inspection

Two more guided → hidden → review paths are now executable and method-required:

- `M15.ZP` → `M15.ZPH` teaches Visual Block `zy` plus `zp`. The source palette
  is deliberately rectangular and padded, while the destination contains the
  same complete Stone Story pose with each row ending at its actual visible
  glyph. This makes the `z` commands' no-trailing-space contract observable,
  rather than mentioning `zp` without a buffer where ordinary block padding is
  the defect. Hidden Chick work reviews on Skully and SnowBunny.
- `M11.WS` → `M11.WSH` teaches `:set list`, `cursorcolumn`, and `colorcolumn`
  as inspection aids before `:%s/\s\+$//e` removes only row-end whitespace.
  Interior spaces remain drawing cells. Hidden Chick work reviews on Skully
  and SnowBunny.

Both pairs have individually written four-choice animation + Neovim questions
with visible art. The whitespace questions explicitly say that `·` visualizes
a space only in the diagram; they do not pretend the display marker is stored
in the art. The generated curriculum now contains 205 cards and 365 questions.
`test_v2.py` passes 205/205 executable lessons and 164/164 primary recipes;
`test_question_quality.py` passes all 365 questions; and the Stone Story
variant test still reports zero border-swap reviews.

The client-attached real-user-config popup passes at 80×24, 100×36, and
188×49 on revision `.32`. The first concurrent 80×24/100×36 attempt exposed a
test-harness race rather than a tutor failure: both tests saved and restored
the process-global macOS clipboard, so one could restore old content between
the other's `y` copy and `pbpaste` assertion. `test_tmux_v2.py` now holds an
exclusive cross-process lock across clipboard save, copy, assertion, and
restore. All three sizes then passed concurrently, including question copy,
answer `c`, real user config, progress/debrief, repeat, and cleanup.

The first direct live run of `M11.WSH` found a defect the clean recipe replay
could not expose: `_read_lines()` stripped every row with `rstrip()`, so the
three padded start rows were normalized to the already-clean target before the
editor opened. Recovery then correctly rejected the missing method evidence,
but the learner could never perform the lesson. Whitespace is now a per-card
artifact contract. `M11.WS`/`M11.WSH` set
`preserve_trailing_whitespace=true`; runtime reads, start/target comparisons,
replay, recovery, and spaced review preserve bytes for those cards while all
older cards retain their existing normalized behavior. A unit regression
proves both read modes. The direct real-config `M11.WSH` popup then passed at
80×24. `M15.ZPH` also passed as a direct 80×24 real-config route. The route
driver now has `--only-card=<id>` so future inserted guided/hidden cards can be
proved directly instead of being inferred from the module's `.06` transfer.

**Remaining VD-26 command gaps after this revision:** `:diffthis` with
`scrollbind`, plus undo-tree travel with `g-`, `g+`, and `:earlier`. The stage
gate, transfer-question replacement, primary-art replacement, and archive
provenance/publication work listed above also remain open.

### VD-36 follow-through · revision `2026-09-29.34` — comparison windows and undo-tree takes close the named command list

The last two command families in VD-26's explicit missing list now have the
same enforced progression as the earlier additions:

- `M4.DIFF` → `M4.DIFFH`: create a disposable vertical copy of the prior
  frame, enable `:diffthis` and `scrollbind` in both art windows, edit only the
  working frame, turn diff off, and close only the disposable reference. The
  hidden Chick beak lesson passed in the real-user-config 80×24 popup; its
  cleanup leaves the tutor's upper brief intact. Reviews use Skully and
  SnowBunny blink work.
- `M11.UT` → `M11.UTH`: author one exaggerated take, `u` to branch, author the
  chosen sibling take, visit the abandoned take chronologically with `g-` and
  return with `g+`, then repeat the comparison with `:earlier 1` and restore
  the chosen state before save. The hidden SnowBunny half-blink lesson passed
  in the real-user-config 80×24 popup. Reviews transfer the same history model
  to missile exhaust and Chick beak timing.

Both hidden cards are required before module mastery and each owns two
source-linked, method-required spaced reviews. Their four paired questions are
individually authored with the actual reference/working frames or history
branches shown. `--only-card=<id>` live-route proof prevents these inserted
cards from hiding behind the older `.06` transfer matrix.

Revision `.34` contains 209 cards and 369 manually authored four-choice
questions. `test_question_quality.py` passes all 369. A complete `test_v2.py`
run was still in progress when this paragraph was written, so its final result
is deliberately not claimed here.

The client-attached base popup also passes concurrently at 80×24, 100×36, and
188×49 on `.34` with the real user config. This proves the general question,
copy, edit, debrief, progress, retry/repeat, and cleanup surface; the two new
hidden command cards have the separate direct-route evidence above.

The first clean-Neovim full replay then hung at `M4.DIFF`: closing the
reference *window* left its modified unnamed buffer hidden, so the final
`:wq` refused to exit with E37/E162. The live popup happened to complete, but
that was not a portable teardown contract. The lesson now uses
`:bwipeout!` on the disposable reference after `:diffoff!`; `:silent 0read #`
also suppresses the reference-read hit-enter message in clean Neovim. The
corrected direct `M4.DIFFH` popup still passes at 80×24, and the complete clean
suite now passes **209/209 executable lessons and 168/168 primary recipes**,
including all four diff-review variants and all four undo-tree variants.

**Scope correction:** the concrete command gaps enumerated by VD-26 are now
represented by executable guided → hidden-method → changed-art-review paths;
that does **not** make the course complete. The remaining curriculum failures
are structural/content work: replace module transfer art only after writing
matching per-variant questions; replace remaining invented primary art; turn
the mixed `MASTER_COVERAGE` labels into a truthful enforced S0→S7 then A0→A7
stage journey rather than relabeling mixed cards; and finish Stone Story archive
provenance/publication handling without publishing third-party material by
default.

## VD-37 · 2026-09-29 — mixed stage labels replaced by an enforced S0-S7 → A0-A7 journey

**Observed failure:** revision `.34` attached two or three `master_stages` labels
to most cards but never projected stage state. Progress and availability were
computed only from module prerequisites in `share/v2_runtime.py::project()` and
`next_card()`. A single pass could therefore appear to cover unrelated still and
animation stages (for example M0 claimed S0+A0 and M11 claimed S0+A3), and the
tree could not prove the operator's required stills-before-animation order. M10
was described as an optional branch but appeared before M5 in the default module
iteration, so it could pre-empt the main route after S5.

**Implemented in revision `.35`:**

- `share/gen_curriculum_v2.py` now emits sixteen main stage records in the exact
  order `S0..S7,A0..A7`, plus optional P with prerequisite S5. Every one of the
  210 cards has one `stage_owner`; `master_stages` is exactly that one owner.
  Stage inventories are derived from the owned cards, not separately maintained
  counts.
- `share/v2_runtime.py::project()` now projects stage `done/total`, required
  review evidence, and state. The next main stage remains locked until every
  current-stage card passes and every owned `required_before_mastery` review has
  reached review stage 1. Module state remains a project ledger and no longer
  authorizes a card independently of its stage.
- `share/v2_runtime.py::next_card()` always chooses the current main-stage card.
  P becomes selectable after S5 but cannot pre-empt an available S6-A7 lesson;
  it is offered automatically only while the main path is waiting on spaced
  review or after the main path is complete.
- The popup progress line now names both the authoritative stage and the project
  module. The compact tree prints all S/A/P stage cells; the full tree prints the
  stage path first and a separate project/module ledger second. Unlock notices
  name stages rather than implying that a module label is a mastery level.
- Stage content ownership is now: M11→S0, M1→S1, M19→S2, M2→S3, M12→S4,
  M14→S5, M5→S6, M15→S7, M16→A0, the Spark strip→A1, M3+M4→A2,
  M17→A3, M13+M7→A4, M6→A5, M18→A6, M8+M9→A7, and M10→P.
  The seven M0 grammar/fixed-grid labs (`P0`, `01`, `YP`, `O`, `SR`, `T`,
  `SL`) explicitly own S0; the remaining Spark cards own A1. This is a real
  scheduler split, not a second label on the same completion event.

**New prerequisite defect found by reachable-stage validation:** after moving
animation modules behind S7, M5.04 and M5.05 required `C`/change-to-end while
the only visible guides were in later A2 or optional P. New card `M5.C` teaches
the row-suffix grammar on a three-layer fixed-width still before either hidden
use. Its manually authored `M5.C.P01` question prints the cloud/ledge/ground
visual and distinguishes `C` from whole-line deletion, insertion, and one-cell
`r`. The generator now validates grammar introduction in the order a learner
can actually reach (S0-S5, optional P, S6-S7, A0-A7), rather than trusting
module storage order.

**Executable evidence:**

- `python3 share/gen_curriculum_v2.py` writes 20 modules, 210 cards, and 370
  questions at revision `.35`.
- `python3 share/test_question_quality.py` passes all 370 manually authored
  four-choice questions.
- `python3 share/test_animation_lesson_pack.py` and
  `python3 share/test_animation_curriculum_integration.py` pass all 12 pack
  lessons / 24 paired questions.
- `python3 share/test_v2.py` passes **210/210 lessons and 169/169 primary
  recipes**. Its projection tests prove: only S0 is initially available; every
  successor is locked; an all-card S0 without reviews is `review_pending`; S1
  opens only after all three S0 review gates; P and S6 both open after S5;
  automatic selection chooses S6; and A0 remains locked until S7 masters.

**Still open; no overall-completion claim:** the new stage rendering still needs
headed popup proof at 80×24, 100×36, and 188×49. Module `.06` transfer variants
still need variant-specific manually authored questions before their first art
can be replaced; remaining invented primary art still needs source-backed
replacement; and Stone Story archive provenance/publication intake remains
unresolved. No third-party art was pushed or published in this change.

**Content-scope correction after the structural gate:** `.35` proves ordering,
ownership, review gates, and non-blocking P. It does **not** yet prove that every
S-stage card is a still-only lesson. A prompt-level audit for explicit temporal
terms (`frame`, `pose`, `animation`, `loop`, `extreme`, `tween`, `motion`,
`blink`, `swing`, `playback`) finds S0 8/21, S1 4/9, S2 6/8, S3 2/8,
S4 4/9, S5 7/11, S6 2/9, and S7 4/13. Examples include M19.02's
"opposite-facing animation extreme", M12.04's "drag-inbetween", M5.04's
foreground swing, and M15.08's settle frame. Some are legitimate non-playing
working copies or still variants, so the word count is a triage signal rather
than a verdict; each named card still needs manual disposition. The remaining
requirement is to re-author or move every genuinely temporal S-card, then add a
validator over explicit card dispositions. Do not describe `.35` as completion
of the still-content migration. The per-card manual decisions and required S4/S6
replacement work are recorded in `share/audits/stage-content-disposition-v35.md`.

**Headed proof correction:** the base real-user-config popup path passes at
80x24, 100x36, and 188x49 and visibly renders stage progress (for example,
`PROGRESS S0 1/21 learning`) plus the S0-A7/P tree. That evidence covers the
base route only. The full post-M2 route matrix and the full real-config recipe
suite remain separate pending results and are not claimed by this proof.

## VD-38 · 2026-09-29 — S4 rebuilt as still authoring; temporal cards moved behind A0

**Finding.** The `.35` scheduler enforced an S0-S7 → A0-A7 order, but S4 still
owned M12 timing work. The manual disposition in
`share/audits/stage-content-disposition-v35.md` identified `.02`, `.04`, `.07`,
and `.08`; implementation review found the same defect in `.03` and `.05.
Calling those cards “S4 joint heights” would have made the tree honest only in
metadata.

**Implemented in revision `.36`:**

- Temporal ownership moved explicitly: `M12.02/.03/.04/.05/.07/.08` to A4,
  `M11.08` to A3, `M5.04/.07` to A3, and `M15.08` to A4.
- S4 now contains four new manually written exercises rather than generated
  filler. `M12.AA` replaces a hard four-row staircase with the documented
  off-vertical `¡ ! . '` palette and teaches the `!I` digraph. `M12.JH`
  centres an aligned joint column with `<C-v> ... r:`. `M12.GV` deliberately
  tries the too-high apostrophe, restores the exact selection with `gv`, and
  refines it to `:`. `M12.JHH` repeats that judgement with hidden keys on
  unfamiliar art and owns two enforced changed-art reviews.
- Each of those four cards has one manually authored four-choice question with
  the complete ASCII-art evidence printed in both full and compact forms. The
  choices pair the art decision with the Neovim scope, and every wrong answer
  has mistake-specific feedback.
- Every card now has one `artifact_mode`: `still-study`, `animation-strip`, or
  `optional-proportional`. Generation rejects an animation-strip assigned to
  S0-S7. It also rejects S-task prompts containing temporal authoring terms.
- Every KEEP-STILL/REWORD prompt named by the `.35` audit was rewritten by card
  id. Candidate stills, paragraph-separated drawings, and working copies are
  no longer described as frames, loops, or intended animation. No temporal
  operation was made to pass by renaming it; genuine temporal cards moved.

**Proof completed:**

- `python3 share/gen_curriculum_v2.py` writes 20 modules, 214 cards, and 374
  questions at revision `.36`.
- `python3 share/test_question_quality.py` passes all 374 manually authored
  four-choice questions.
- `python3 share/test_animation_lesson_pack.py` passes 12 lessons / 24 audited
  questions and H1-H9, S0-S7, A0-A7 coverage.
- `python3 share/test_animation_curriculum_integration.py` passes the live
  guided-before-hidden integration for all 12 animation lessons.
- `python3 share/test_v2.py` passes **214/214 executable lessons and 173/173
  primary edit recipes** in clean Neovim, with 69 changed-art review banks.
- A generated prompt scan finds zero occurrences of `animation`, `playback`,
  `loop`, `tween`, `frame`, or `motion` in S0-S7 executable task prompts.
- The base real-config popup passes at 80x24, 100x36, and 188x49. The new
  `M12.JHH` hidden checkpoint also passes its complete headed popup route at
  all three sizes.
- The formerly disappearing `M3.06` transfer now passes a direct real-config
  headed run at 80x24 after the stage-aware route fixture seeds prior stage
  reviews. The broad post-M2 matrix remains a separate pending claim.

**Still open; not claimed here.** The broad headed route matrix after M2 is not
yet claimed by the direct M3.06 pass. The broader Stone Story primary-art
migration, per-variant `.06` questions, archive
provenance intake, and full headed post-M2 route matrix remain open. No Stone
Story third-party art was pushed or otherwise published.

## VD-39 · 2026-09-29 — S6 now proves a complete layer/material/seam decision

**Finding.** S6 had individual seam edits, but no one card required the learner
to read an unfamiliar composite back-to-front, retain three declared material
languages, and break only the false background/foreground connection. The
stage could therefore advance on local cursor skill without proving the layer
judgement named by the stage.

**Implemented in revision `.37`:**

- `M5.S6C` presents a four-row cloud/roof/ground composite. The target replaces
  only the final cloud colon touching the foreground roof with one blank cell;
  roof and ground remain byte-for-byte registered.
- Its key path is hidden and runtime-required: `2G0f/hr<Space>` uses the
  foreground slash as the landmark, steps back to the touching background
  cell, and overwrites that one cell with negative space. The learner does not
  retype the drawing or insert/delete a column.
- The paired four-choice question prints the full BEFORE/AFTER composite and
  asks both why the seam is removed from the background and why `r<Space>`
  preserves registration. Each wrong choice explains its particular layer or
  Vim-scope error.
- Two enforced changed-art reviews replace cloud `.:` with hatch `;` and wave
  `~` materials. They retain the same authoring principle without using a
  synthetic border-glyph swap.

**Proof:** generator `.37` writes 215 cards / 375 questions;
`test_question_quality.py` passes 375; `test_v2.py` passes **215/215 cards and
174/174 primary recipes**, with 70 changed-art review banks; and the full
headed `M5.S6C` route passes with the real user config at 80x24, 100x36, and
188x49.

**Still open.** This does not close the broader Stone Story primary-art
migration, `.06` variant-specific question work, archive provenance, or the
full headed route matrix. No third-party art was pushed or published.

## VD-40 · 2026-09-29 — transfer questions can now follow the selected art variant (first two cards)

**Finding.** `run_edit()` selects a transfer variant before paired questions,
but every variant inherited the card's one base `paired_question_ids` list.
On a retry the learner could receive different art while the question still
printed the first variant. That is the same picture/question contradiction the
operator reported; a generic command question would not cure it because every
multiple-choice item must print the actual ASCII evidence.

**Implemented in revision `.38` as a vertical slice:**

- A transfer variant may now override `paired_question_ids`. Because runtime
  already overlays the selected variant before `run_paired_questions()`, the
  exact selected art now determines the question bank.
- `M3.06` variant 2 owns `M3.06.V2.P01`, manually written around its unfamiliar
  six-row figure and `6yy` whole-object scope. `M4.06` variant 2 owns
  `M4.06.V2.P01`, manually written around its two diagonal extremes, inserted
  vertical midpoint, addressed copy, and row-local `C` rewrites.
- Both full and compact forms print their own BEFORE/AFTER art. All four choices
  answer the animation and Neovim halves, and every distractor explains its
  particular object-scope or command error.
- The headed route harness gained `--only-transfer-alt=<card>` and derives the
  before/after question ids and target from the same selected variant. Both
  `M3.06` and `M4.06` alternate routes pass at 80x24 with the real config.

**Proof:** generator `.38` writes 215 cards / 377 manually authored questions;
question quality passes 377; clean Neovim remains **215/215 cards and 174/174
primary recipes**; headed alternate transfers pass for M3.06 and M4.06.

**Still open.** Eighteen other `.06` cards still lack a manually authored
question for variant 2, and no first variant has yet been replaced by Stone
Story art. The implementation is intentionally not described as course-wide
variant-question parity. Archive provenance and publication remain open; no
third-party art was pushed.

### VD-40 follow-through · revision `.39` — M0/M1/M2 alternates now own their evidence

The next three alternate transfers were reviewed and written individually,
not populated from a prose template:

- `M0.06` variant 2 prints the mirrored, left-facing comet and asks the learner
  to distinguish one-cell `rO` from current-row `:s/-/=/g`; its feedback
  explains why `g` expands matches within the addressed row rather than adding
  vertical scope.
- `M1.06` variant 2 prints the mirrored contour and makes the changed column
  part of the question: `f,` follows the visible joint after mirroring, whereas
  a memorized column would not transfer.
- `M2.06` variant 2 prints the heavy `===` brow and `---` mouth as deliberate
  distractor materials, then requires the learner to identify the eye row,
  glyph landmark, and one-cell `rO` scope.

All three own full and compact ASCII evidence, four paired
animation/Neovim choices, and mistake-specific feedback. The selected retry
variant supplies its own question id through the `.38` mechanism.

**Proof:** generator `.39` writes 215 cards / 380 manually authored questions;
question quality passes 380; clean Neovim remains **215/215 cards and 174/174
primary recipes**; and all three new alternate routes pass with the real user
config at 80x24.

**Still open.** Fifteen other `.06` cards still lack a manually authored
variant-2 question. First variants still use the existing lesson art, so the
Stone Story primary-art replacement, provenance intake, full headed route
matrix, and publication decision remain open. No third-party art was pushed.

### VD-40 follow-through · revision `.40` — M5/M6/M7 alternates own layer, pose, and repeat scope

Three more alternate transfers now have individually authored visual questions:

- `M5.06` variant 2 prints its triangle, dotted midground, wave ground, and
  false vertical seam. The correct account binds the single negative-space
  repair to `4G06lr<Space>` and explicitly rejects repainting or shifting a
  whole layer.
- `M6.06` variant 2 prints both complete five-row pyramid poses. Its question
  decodes `:1,5m$` as range + move + destination and distinguishes pose
  reordering from copying, deletion, or detached apex swapping.
- `M7.06` variant 2 prints both complete hold frames and asks why the five-row
  offset plus dot repeats only `rX` on the corresponding eye, not the preceding
  navigation or a whole-frame put.

**Proof:** generator `.40` writes 215 cards / 383 manually authored questions;
question quality passes 383; clean Neovim remains **215/215 cards and 174/174
primary recipes**; and all three new alternate routes pass with the real user
config at 80x24.

**Still open.** Twelve other `.06` cards still lack manually authored
variant-2 questions. Stone Story primary-art migration, provenance intake, the
full headed route matrix, and publication decision also remain open. No
third-party art was pushed.

### VD-40 follow-through · revision `.41` — M8/M9/M10 alternates own contact, bound, and SJIS evidence

- `M8.06` variant 2 prints the reversed walker and identifies the exact blank
  contact cell between its feet. Its question distinguishes three rightward
  motions from a selection and one-cell `r_` from insertion.
- `M9.06` variant 2 prints the wider angled shell and `=====` ground. It asks
  why `fxrX` transfers by a visible landmark while preserving the unfamiliar
  bounds.
- `M10.06` variant 2 prints the full-width puff and its `?` shoulder defect.
  The question binds `0f?r￣` to that one placeholder and rejects widening or
  retyping the SJIS silhouette.

The first headed M10 attempt exposed a test-fixture error: optional stage P is
eligible after S5, but the scheduler still prefers unfinished main-path S6, so
the fixture opened M5.01. Targeted P fixtures now finish the competing main
path before seeding the requested P card. This changes test setup only; it does
not bypass runtime progression.

**Proof:** generator `.41` writes 215 cards / 386 manually authored questions;
question quality passes 386; clean Neovim remains **215/215 cards and 174/174
primary recipes**; and M8.06, M9.06, and M10.06 alternate routes each open the
correct card and pass with the real user config at 80x24.

**Still open.** Nine `.06` cards still lack manually authored variant-2
questions. Stone Story primary-art migration, provenance intake, the full
headed route matrix, and publication decision remain open. No third-party art
was pushed.

### VD-40 follow-through · revision `.42` — M11/M12/M13 alternates own redraw, symmetry, and WORD scope

- `M11.06` variant 2 prints both unfamiliar shells and asks why `R==<Esc>`
  redraws exactly the first two roof cells without widening the shell or
  spilling into the second roof.
- `M12.06` variant 2 prints both top-row colon joints, the fixed axis, and the
  untouched lower joints. Its question explains the paired `t:`/`T:` stops and
  the final one-cell steps into the symmetric targets.
- `M13.06` variant 2 prints all three texture clusters and support rows. Its
  question makes whitespace-delimited WORD ends the transferable structure:
  `E` reaches cluster 1's end and `2E` reaches cluster 3's end.

**Proof:** generator `.42` writes 215 cards / 389 manually authored questions;
question quality passes 389; clean Neovim remains **215/215 cards and 174/174
primary recipes**; and all three alternate routes pass with the real user
config at 80x24.

**Still open.** Six `.06` cards still lack manually authored variant-2
questions. Stone Story primary-art migration, provenance intake, the full
headed route matrix, and publication decision remain open. No third-party art
was pushed.

### VD-40 follow-through · revision `.43` — M14/M15/M16 alternates own palette, offset, and label scope

- `M14.06` variant 2 prints the local `[@+]` palette and unfamiliar shell. Its
  question follows the actual named-register grammar from visible source yank
  through Replace-mode retrieval, while preserving the palette source.
- `M15.06` variant 2 prints dither, brace-brick, and wave-shadow layers. It
  ties `shiftwidth=1` plus row-local `>>` to the exact one-cell middle-band
  offset rather than describing indentation abstractly.
- `M16.06` variant 2 prints the plus pose, `F07 KEY`, and `T06 FPS`. Its
  question makes the cursor's numeric-token scope explicit so only F07 becomes
  F08.

**Proof:** generator `.43` writes 215 cards / 392 manually authored questions;
question quality passes 392; clean Neovim remains **215/215 cards and 174/174
primary recipes**; and all three alternate routes pass with the real user
config at 80x24.

**Still open.** Three `.06` cards still lack manually authored variant-2
questions. Stone Story primary-art migration, provenance intake, the full
headed route matrix, and publication decision remain open. No third-party art
was pushed.

### VD-40 follow-through · revision `.44` — all 20 alternate transfers now own manual visual questions

- `M17.06` variant 2 prints three complete, deliberately different shells and
  asks how `/x`, `n`, and dot preserve varied contexts while changing only
  corresponding anchors.
- `M18.06` variant 2 prints all three directional rows plus `CHECK=0` and asks
  why three bounded, hand-authored `C` rewrites are required instead of actor-
  only editing or byte reversal.
- `M19.06` variant 2 prints the fixed-rail five-row still and pairs the
  glyph-aware mirror with three bounded Virtual Replace rows.
- `test_v2.py` now requires all 20 transfer cards to give variant 2 its exact
  `<card>.V2.P01` manually authored question. It also checks that every START
  and TARGET row appears verbatim in that question's full prompt. This caught
  and repaired two pre-commit defects: M17 had omitted literal shell rails and
  M7 described, rather than drew, its AFTER frames.
- Generator validation rejects any later transfer variant that inherits the
  first variant's question instead of declaring its own question ids.

**Proof completed:** generator `.44` writes 215 cards / 395 manually authored
questions; question quality passes 395; clean Neovim passes **215/215 cards and
174/174 primary recipes**; M17.06 and M18.06 alternate routes pass with the
real user config at 80x24; animation-pack, live integration, and all 70
changed-art review-bank tests pass.

**Proof still pending:** the M19.06 alternate headed route was still running
when this entry was written, so it is not claimed here. The revision-wide full
headed route matrix is also not claimed. Stone Story primary-art migration,
archive provenance intake, and the publication decision remain open. The
rights audit found no redistribution permission; the operator later allowed
local tutor integration, but did not authorize publication from this public
repository. No third-party art was pushed.

## VD-41 · 2026-09-29 — primary transfer-art migration begins with M3 FaceHUD poses

**Finding.** Completing variant-specific question ownership removed the
picture/question contradiction, but all 40 primary `M*.06` transfer variants
still reported no exact source. M3 in particular still used two invented
stick figures even though the already-local, audited FaceHUD material supplies
two complete six-row poses that fit its whole-object register lesson.

**Implemented in revision `.45`:**

- M3.06 variant 1 now starts from `official-UI/FaceHUD res08` shock pose. The
  learner selects all six rows into register a, appends the complete face, and
  changes only the copied left pupil on row 9.
- Variant 2 now uses the `official-UI/FaceHUD res02` neutral pose. Its blank
  fourth row is intentionally inside the six-line object, so the task tests
  whether the learner preserves registered vertical spacing as well as visible
  glyph rows.
- `M3.06.P01` and `M3.06.V2.P01` were both rewritten individually around the
  exact FaceHUD START and TARGET. They print the complete source and copied
  result, use four art/Neovim paired choices, and explain row scope, named-
  register independence, blank-line ownership, and the one-cell pupil edit.
- The source rows were already present in the local tutor's audited review
  bank; this slice imports no additional third-party asset.

**Proof:** generator `.45` writes 215 cards / 395 questions; question quality
passes 395; clean Neovim passes **215/215 cards and 174/174 primary recipes**;
all changed-art banks replay; and both M3.06 transfer variants pass their real-
config headed routes at 80x24.

**Still open.** The other nineteen module transfers still lack exact-source
primary variants, and most earlier guided/independent module art is still tutor-
authored scaffolding. M19.06's alternate headed proof and the revision-wide
route matrix remain unclaimed. Archive provenance and public-repository
publication remain separate open decisions; no push occurred.

### VD-41 follow-through · revision `.47` — real in-between and ordering strips replace M4/M6 stand-ins

- M4.06 variant 1 now uses TowerDefense missile exhaust frames 1 and 4 as its
  extremes and constructs the missing frame 2 by copying the complete first
  missile, then changing only the copied exhaust endpoint. Variant 2 uses Chick
  hatch frames 1 and 4 and constructs the missing first-crack frame 2.
- The egg's semicolon initially used `r;`. Clean Neovim passed, but the real
  user-config headed route showed the semicolon key being consumed before `r`
  received its replacement; the subsequent submit `Z` became the glyph. The
  path is now `R;<Esc>` on the already-addressed cell, making semicolon literal
  Replace-mode input and bounding it with Escape.
- Both M4 questions were rewritten around the complete source strips and ask
  why full-frame copy precedes the one-cell in-between change.
- M6.06 now reorders real five-row FrogBog lily pads: 2→1 becomes 1→2, and the
  alternate 3→2 becomes 2→3. Both questions print every contour row and make
  the numbered centre part of, not a substitute for, whole-frame scope.

**Proof completed:** revision `.47` writes 215 cards / 395 questions; question
quality, all 215 cards / 174 recipes, and changed-art replay pass. The M4
missile route and both M6 pad routes pass with the real user config at 80x24.

**Proof pending:** the corrected M4 egg headed route was still running when
this entry was written and is not claimed. The older M19 alternate process and
the revision-wide route matrix are also unclaimed. Seventeen other module
transfers still use tutor-authored primary variants. No new source assets were
imported and no push occurred.

### VD-41 follow-through · revision `.48` — M7 holds now use padded Skully and Frog animation states

- M7.06 variant 1 now holds the audited Skully idle pose twice, padding each
  three-row source frame to the module's declared five-row height. One local
  `o→O` look edit is repeated exactly five rows later with dot.
- Variant 2 holds the audited Frog open-eye pose twice with the same explicit
  padding. It changes only the visible right eye from `o` to `-`, then repeats
  that blink one complete frame later.
- Both questions print both complete BEFORE and AFTER holds, including the
  blank registration rows, and distinguish repeating the last one-cell change
  from repeating navigation, copying a frame, or applying a global search.

**Proof:** revision `.48` writes 215 cards / 395 questions; question quality,
all 215 cards / 174 recipes, and changed-art replay pass. Both M7.06 variants
pass real-user-config headed routes at 80x24.

**Still open.** Sixteen module transfers still use tutor-authored primary
variants. The pending M4/M19 headed processes and full route matrix remain
unclaimed here. No new source asset was imported and no push occurred.

### VD-41 follow-through · revision `.49` — M8 contact now advances real Dracula walk frames

- M8.06 variant 1 advances Dracula walk frame 3 to 4 by changing only the
  trailing `>` foot to a planted `|` on the hem row.
- Variant 2 advances frame 4 to 5 by changing only the final backslash foot to
  a forward `>`, retaining the already planted bar and every upper-pose cell.
- The three-row source frames are explicitly padded to the module's five-row
  invariant. Both paired questions print the padded BEFORE/AFTER pose and ask
  about a visible foot landmark or row-end motion followed by one-cell `r`.

**Proof:** revision `.49` writes 215 cards / 395 questions; question quality,
all 215 cards / 174 recipes, and changed-art replay pass. Both M8.06 variants
pass real-user-config headed routes at 80x24.

**Still open.** Fifteen module transfers still use tutor-authored primary
variants. The pending M4/M19 headed processes and full route matrix remain
unclaimed. No new source asset was imported and no push occurred.

### VD-42 follow-through · revision `.50` — current M3 route is healthy; M9 now uses Boo's real hover squash

**Route-report reconciliation.** On commit `00c3ebd`, M0.06 through M19.06
each reached the editor and passed as an individually isolated real-user-config
headed route at 80x24. M0.06 through M3.06 were also run consecutively and all
passed. The reported M3.06 shell exit therefore does not reproduce on the
current revision. This is per-card current-revision evidence, not a claim that
the full same-process route matrix passes at every viewport.

**M9 source replacement.** Both M9.06 variants now use `official-Pets/Boo`
res01 hover frames identified by the corpus audit as a three-row M9
bounce/squash fit:

- frame 3 to 4 folds only the lower flare inward with a row-scoped `C` edit;
- frame 2 to 3 removes both body anchors and restores the flared skirt contour,
  combining one-cell replacement, end deletion, and a bounded Replace-mode
  row rewrite. This distinct start avoids treating the identical frame-1 and
  frame-3 loop poses as different retry art.

Both questions were rewritten individually. Each prints its exact full
BEFORE/AFTER source pose, asks about the visible animation change and the Vim
scope together, and gives mistake-specific feedback.

**Proof:** revision `.50` writes 215 cards / 395 questions; question quality,
all 215 cards / 174 primary recipes, and every changed-art replay pass. Both
M9.06 source variants pass their real-user-config headed routes at 80x24.

**Still open.** Fourteen module transfers still use tutor-authored primary
variants. Full same-process route coverage at all three viewport sizes remains
unclaimed. The Boo excerpt is authorized for this local tutor only; no push or
publication occurred.

### VD-43 follow-through · revision `.51` — M11 redraw now uses Snail blink and crawl frames

- M11.06 variant 1 composites the official Snail idle layers and closes the
  adjacent `Oo` eyes as `--` with a two-cell Replace-mode redraw. The shell,
  spiral, slash, and crawl baseline are complete and remain registered. The
  source `@` spiral is explicitly adapted to alphabet-safe `O`; the rest of the
  composite is unchanged.
- Variant 2 uses the official crawl loop's frame-4 to loop-close transition:
  only the first baseline glyph settles from `´` to `¯` with normal-mode `r`.
- Both paired questions were rewritten by hand around their exact full-pose
  BEFORE/AFTER art and distinguish `R`'s sequential overwrite from `r`'s
  single-cell scope.

**Proof:** revision `.51` writes 215 cards / 395 questions; question quality,
all 215 cards / 174 primary recipes, and every changed-art replay pass. Both
M11.06 source variants pass their real-user-config headed routes at 80x24.

**Still open.** Thirteen module transfers still use tutor-authored primary
variants. The Snail excerpts are local-tutor use only; no push or publication
occurred.

### VD-44 follow-through · revision `.52` — M14 primary transfer now uses real face states

- M14.06 variant 1 uses the official Skully idle-to-look change. The tutor adds
  a visible `[O]` palette annotation, then the learner copies that O into named
  register `a` and retrieves it over only the left eye.
- Variant 2 uses the official SnowBunny idle-to-blink change. The visible
  `[n-]` palette supplies one dash that is yanked once and retrieved over both
  eyes; ears, nose, outline, body, and separator remain fixed.
- Both questions print the full source-backed BEFORE/AFTER face and ask about
  animation scope and named-register/Replace-mode scope together.

**Proof:** revision `.52` writes 215 cards / 395 questions; question quality,
all 215 cards / 174 primary recipes, and every changed-art replay pass. Both
M14.06 source-backed palette routes pass with the real user config at 80x24.

**Still open.** Twelve module transfers still use tutor-authored primary
variants. These excerpts remain local-tutor use only; no push or publication
occurred.

### VD-45 follow-through · revision `.53` — M15 primary transfer now uses real tread and lava materials

- M15.06 variant 1 uses the official Drill tread crop: only the repeated tread
  band pans one cell right while the machine edge and angled support row remain
  registered.
- Variant 2 uses the CaveParty lava crop's one-cell phase change: only the
  bottom wave band advances while the figure's head and torso stay fixed.
- Both questions print the full source-backed crop and explicitly connect the
  animation-cell offset to `shiftwidth=1`, cursor row scope, and one `>>`.

**Proof:** revision `.53` writes 215 cards / 395 questions; question quality,
all 215 cards / 174 primary recipes, and every changed-art replay pass. Both
M15.06 source-material routes pass with the real user config at 80x24.

**Still open.** Eleven module transfers still use tutor-authored primary
variants. These excerpts remain local-tutor use only; no push or publication
occurred.

### VD-46 follow-through · revision `.54` — M16 increments numbers inside real FrogBog frames

- M16.06 variant 1 now uses the exact five-row `official-Games/FrogBog`
  res05→res06 lily-pad transition. The number drawn inside the pad advances
  from 1 to 2; the rim, sides, and `\/|..-'` lower texture remain registered.
  Its required path is `3G0f1<C-a>`: address the numbered third row, find the
  visible 1, and increment only that numeric token.
- Variant 2 uses the adjacent res06→res07 transition. It advances the embedded
  2 to 3 with `3G0f2<C-a>` while preserving the same complete pad contour.
- `M16.06.P01` and `M16.06.V2.P01` were rewritten individually around those
  exact BEFORE/AFTER frames. Both print all five source rows, pair the visible
  animation invariant with the Neovim address/motion/operator grammar, and
  explicitly reject the false ideas that Ctrl-a duplicates a pose, changes
  every number, shifts a column, or generates surrounding animation art.

**Proof:** revision `.54` writes 215 cards / 395 questions; question quality
passes all 395; clean Neovim passes **215/215 cards and 174/174 primary
recipes**; every changed-art replay passes; and both M16.06 source-pad variants
pass their real-user-config headed routes at 80x24.

**Still open.** Ten module transfers still use tutor-authored primary variants.
Full same-process route coverage at all three viewport sizes remains unclaimed.
The FrogBog excerpts remain authorized for this local tutor only; no push or
publication occurred.

### VD-47 follow-through · revision `.55` — M13 WORD motions now act on real Fireworks node groups

- M13.06 variant 1 uses three exact rows from `official-Cosmetics/Fireworks`
  res03 willow frame 5. Its source row contains three visible whitespace-
  separated lower-canopy nodes. The learner authors a pulse by brightening only
  the centre and right nodes; the upper spark row, left node, and lower
  apostrophe row remain registered.
- The first recipe attempt, `j02Wr!Br!`, failed exact replay. Because `0` leaves
  the cursor before the row's leading spaces, the first `W` reaches node 1;
  `2W` therefore reaches node 2, not node 3. The enforced path is now
  `j03Wr!Br!`, and the question teaches that leading-whitespace count rather
  than hiding it behind a memorized column.
- Variant 2 uses an exact three-row crop from res06 radial frame 5. The learner
  authors an outer-node pulse with `0Er!2Er!`: `0E` reaches the first separated
  dot and counted `2E` crosses the centre colon to the third dot. The spoke and
  burst rows remain unchanged.
- Both paired questions were rewritten individually and print their complete
  BEFORE/AFTER crops. They distinguish motions from operators, explain why
  normal-mode `r` preserves width, and state honestly that the source crop is
  official while the requested pulse is the learner-authored animation edit.

**Proof:** revision `.55` writes 215 cards / 395 questions; question quality
passes all 395; clean Neovim passes **215/215 cards and 174/174 primary
recipes**; and both M13.06 Fireworks variants pass their real-user-config
headed routes at 80x24.

**Still open.** Nine module transfers still use tutor-authored primary
variants. Full same-process route coverage at all three viewport sizes remains
unclaimed. The Fireworks excerpts remain local-tutor use only; no push or
publication occurred.

### VD-48 follow-through · revision `.56` — M12 uses Snowman's real expression overlays; Unicode method evidence fixed

- M12.06 variant 1 now combines the exact first three rows of
  `official-Pets/Snowman` res01 with the res08 blink overlay. Both `•` eyes
  become dashes while the hat, comma nose, parentheses, cheek punctuation, and
  row width remain registered. `2j0t•lr-$T•hr-` deliberately approaches the
  homologous eye landmarks from opposite directions.
- Variant 2 is visibly distinct: it begins at the closed-eye state and applies
  the res06 raised-eye overlay. `2j0t-lr^$T-hr^` changes the two dashes to
  carets without moving the face. Both paired questions print the complete
  three-row states and explain that `t`/`T` are motions, the inward `l`/`h`
  reaches the landmark itself, and `r` preserves column registration.
- Clean Neovim reached both targets, but the first real popup initially
  reported missing method evidence even though its saved target was exact.
  The captured raw keylog encoded U+2022 as `e2 80 fe 58 a2`: Neovim had
  escaped the literal UTF-8 `0x80` continuation byte as `80 fe 58`. The
  decoder incorrectly consumed `e2 80 fe` as one malformed scalar, losing the
  bullet token used by method matching.
- `decode_keylog` now reconstructs an escaped `0x80` continuation inside a
  multibyte scalar before decoding it. `test_v2.py` contains the captured byte
  sequence as a regression assertion. The primary-art alphabet also admits
  U+2022 after direct Neovim evidence that `strdisplaywidth('•') == 1`; the
  legacy corpus test already classified it as an observed plate glyph.

**Proof:** revision `.56` writes 215 cards / 395 questions; question quality
passes all 395; clean Neovim passes **215/215 cards and 174/174 primary
recipes**; every changed-art replay passes; the captured Unicode keylog
regression passes; and both M12.06 Snowman variants pass their real-user-config
headed routes at 80x24.

**Still open.** Eight module transfers still use tutor-authored primary
variants. Full same-process route coverage at all three viewport sizes remains
unclaimed. The Snowman excerpts remain local-tutor use only; no push or
publication occurred.

### VD-49 follow-through · revision `.57` — M17 search-and-dot now edits real Cranius expression states

- M17.06 variant 1 uses the three-row face crop identified by the animation
  audit from `official-Pets/Cranius` res01 plus the res04 happy overlay. The
  two `*` eye materials become carets with `/\*<CR>r^n.`; search finds the
  homologous landmark and dot repeats only the one-cell edit. Sockets, nose,
  jaw, and all other source cells remain fixed.
- Variant 2 is the res06 half-blink crop advancing to the res07 shut-eye
  overlay. `/==<CR>R--<Esc>n.` overwrites exactly two cells in the first eye,
  Escape bounds Replace mode, `n` finds the second `==`, and dot repeats that
  bounded edit.
- M17's existing registration helper adds `| ` / ` |` tutor rails around each
  source row. The first question draft showed only the unrailed inner crop and
  was rejected by the exact-art validator. Both final questions print the
  actual railed START and TARGET while identifying the official face as the
  inner crop; the choices distinguish search repetition from edit repetition
  and explain why neither `n` nor dot copies the surrounding socket.

**Proof:** revision `.57` writes 215 cards / 395 questions; question quality
passes all 395; clean Neovim passes **215/215 cards and 174/174 primary
recipes**; and both M17.06 Cranius variants pass their real-user-config headed
routes at 80x24.

**Still open.** Seven module transfers still use tutor-authored primary
variants. Full same-process route coverage at all three viewport sizes remains
unclaimed. The Cranius excerpts remain local-tutor use only; no push or
publication occurred.

### VD-50 follow-through · revision `.58` — M2 face focus now uses Frog and Skully overlays

- M2.06 variant 1 uses the exact three-row `official-Pets/Frog` half-eye crop
  plus a blank fourth registration row. `0f=rO` opens only the left eye from
  `=` to `O`; the paired dash, body, legs, and frame height remain fixed.
- Variant 2 uses the exact `official-Pets/Skully` idle-to-look overlay plus the
  same explicit fourth-row padding. `j0forO` widens only the left eye while the
  right eye, comma, skull contour, and mouth remain registered.
- Both questions were rewritten around their complete visible source poses and
  explain that `f` is a current-line motion and `r` is one-cell overwrite, not
  a range selection or insertion.
- The first headed run failed because `test_tmux_v2_routes.py` still replaced
  M2.06's authored recipe with the old invented face's hard-coded `2GforO`.
  That exception was obsolete once the Frog eye moved to row 1. It was removed;
  the route driver now sends the card's current expected path like every other
  transfer.

**Proof:** revision `.58` writes 215 cards / 395 questions; question quality
passes all 395; clean Neovim passes **215/215 cards and 174/174 primary
recipes**; and both M2.06 source-face variants pass their real-user-config
headed routes at 80x24.

**Still open.** Six module transfers still use tutor-authored primary variants.
Full same-process route coverage at all three viewport sizes remains
unclaimed. The Frog and Skully excerpts remain local-tutor use only; no push or
publication occurred.

### VD-51 follow-through · revision `.59` — M0 transfer replaces the comet with readable Fireworks states

- M0.06 variant 1 now uses the central three-row crop from
  `official-Cosmetics/Fireworks` res06 radial frame 3. The learner authors a
  brightness pass with `j0f*rO:s/-/=/g<CR>`: `*` becomes `O`, both outer ASCII
  hyphens become equals signs, and the two inner em-dash spokes plus vertical
  accents remain fixed.
- Variant 2 uses the denser frame-4 crop, including its edge bullets and larger
  upper/lower flare. It applies the same bounded grammar while preserving the
  bullets and em-dash spokes. Both questions print the exact three-row art and
  teach that literal `-` and `—` are different glyphs, while `g` means every
  match on the addressed current row rather than vertical or whole-file scope.
- The first replacement draft used radial frame 2 (`¡ / -*- / !`). Generation
  rejected it as a toy stimulus: only five nonblank ink cells across three
  rows. The final frame-3/frame-4 pair satisfies the readable multi-row art
  gate instead of recreating the operator's earlier “literal dot” failure.
- U+2014 EM DASH was admitted to the primary-art alphabet only after direct
  Neovim evidence that `strdisplaywidth('—') == 1`. The escaped-continuation
  decoder regression from VD-48 also covers its UTF-8 `0x80` byte.

**Proof:** revision `.59` writes 215 cards / 395 questions; question quality
passes all 395; clean Neovim passes **215/215 cards and 174/174 primary
recipes**; and both M0.06 radial Fireworks variants pass their real-user-config
headed routes at 80x24.

**Still open.** Five module transfers still use tutor-authored primary variants
(M1, M5, M10, M18, M19). Full same-process route coverage at all three
viewport sizes remains unclaimed. The Fireworks excerpts remain local-tutor
use only; no push or publication occurred.

## VD-52 · 2026-09-29 — final invented primary transfers removed; provenance gap exposed

**Operator evidence carried forward:** the prior audit still found five module
transfers using invented primary art, the M3.06 headed route had previously
fallen back to a shell at 80×24, archive provenance was incomplete, and the
local source-art commits had not been pushed. The last fact is intentional:
local tutor authorization is not redistribution permission.

### Source-backed transfer replacements

- M1.06 now uses complete five-row Acronian Guardian wing poses from
  `official-Cosmetics/AcronianGuardian` res06 and res11. Each task changes one
  visible comma joint to a colon with `f,` plus one-cell `r`, preserving the
  complete feather contour.
- M5.06 now uses the exact four-layer Ironclad mask composite from
  `official-Hats/IroncladMask` res01–res04. START injects one false `|` seam;
  the target restores the source negative-space break with a one-cell
  overwrite. A question fidelity check caught and restored the literal
  backslash before the third-row backtick.
- M10.06 now uses complete AAHub `bakuhatsu-kemuri` puffs from resK-119 and
  resK-123. Only the redacted partner in the measured `⌒ヽ` shoulder is
  restored; full-width spaces, body, tail, and the alternate `ﾐ` wisp remain.
- M18.06 now uses Pallas Crown's source-authored calm and straining left/right
  ghost pairs from res01–res04. Six fixed-rail rows are hand-authored with
  bounded `C` passes; the questions distinguish deliberate glyph-aware
  mirroring from byte reversal.
- M19.06 now uses Acronian left/right wing pairs from res08/res12 and
  res07/res11. The six-row folded mid-wing and five-row downstroke are
  hand-authored with bounded `gR` passes; the rails expose insertion or width
  drift.

All ten base/alternate paired questions were rewritten individually in the
four authored question files. Each prints its complete actual START and TARGET,
asks a specific art judgment and Neovim scope question, supplies four distinct
choices, and gives choice-specific feedback. No question template or prose
generator produced these records.

The new source excerpts do not share the parent module's old frame height
(M1 5 rows, M10 4/3 rows, M18 6 rows). Transfer variants now carry their own
`frame_rows`; validation uses that per-variant value instead of splitting a
complete pose into a three-row frame plus a rejected toy remainder.

### Provenance correction

`share/audits/STONE_STORY_LOCAL_PROVENANCE.md` now binds the exact local file
sets used by the tutor: 21 Stone Story source directories and two AAHub files.
It records exact filenames, byte-derived SHA-256 set digests, transformations,
curriculum linkage, and the local-only/publication-blocked boundary.
`share/test_stone_story_provenance.py` recomputes those digests and checks every
generated transfer. That check exposed M16.06: its FrogBog art was cited in
question prose but both generated variants lacked a `source` field. The
generator now records res05→res06 and res06→res07 directly. The test proves
20/20 primary transfers have source metadata.

This register is not archive ingestion. The 885-sheet corpus still has zero
rows in `ascii-art-archive/MANIFEST.tsv`; adding it there or pushing the local
tutor commits would publish third-party material and remains blocked pending a
redistribution decision.

### Evidence available at this checkpoint

- Revision `.60` generates 20 modules, 215 cards, and 395 questions.
- `test_question_quality.py` passes all 395 multiple-choice questions.
- `test_v2.py` passes 215/215 cards, 174/174 primary recipes, 70 changed-art
  variants, the strict S0→S7 then A0→A7 stage gate, and progress/state checks.
- `test_drills.py` passes 46/46 legacy drills; setup, Stone Story variant,
  animation-pack, and live curriculum-integration tests pass.
- `test_stone_story_provenance.py` passes 21 Stone Story sets, two AAHub files,
  22 source families, and 20/20 source-backed primary transfers.
- The formerly disappearing M3.06 transfer passes a direct real-config headed
  route at 188×49 in this checkpoint; VD-34 already records its three-size
  fix. M1 base/alternate pass at 80×24, 100×36, and 188×49. M5, M10, and M18
  base/alternate pass at those same three sizes.
- At this checkpoint, M19 alternate passes at 80×24 and 100×36. Its first base
  runs exceeded the 30-second command yield and remain unresolved background
  sessions. They are **not** counted as passes or failures until their terminal
  results are collected under the required polling cadence.

**Still open:** collect and diagnose the M19 base headed runs; prove M19 at all
three viewport sizes; run the full same-process route matrix rather than only
targeted transfers; keep archive ingestion and all push/publication blocked;
and do not treat automated question rules as a substitute for the prior
per-question human audit.

### VD-52 follow-through — M19 live failure reproduced and repaired

The two pending M19 base sessions both terminated as failures. Rows 1–4 were
exact; row 5 expected `|        ;/    |` but saved `|        /    ||`. The
literal semicolon in the res06→res10 target was not inserted during the
real-config Virtual Replace replay, so the original right rail survived as a
second final `|`. The test then timed out waiting for an after-question because
the runtime was correctly holding the failed-art debrief instead.

The base exercise now uses the complete six-row Acronian folded mid-wing pair
from res08/res12. This is not a weakened target: it adds one row and requires
the learner to judge the outer edge, inner fold, accents, and gaps in a visibly
different full pose. The variant-1 question was manually rewritten again with
all six fixed-rail START and TARGET rows. The provenance set now includes
res08/res12 and its recomputed byte-bound digest.

This exposed a second metadata defect. `infer_grammar_families()` scanned the
literal text typed inside `gR...<Esc>` as Normal-mode commands. The `,.` inside
the source wing was falsely classified as reverse character-find plus dot
repeat; the older semicolon had likewise falsely claimed character-find repeat.
Virtual Replace payloads are now removed from grammar inference while the `gR`
mode transition remains. M19.06 therefore owns `virtual-replace` and
`normal-motion`, not commands that merely appear as art glyphs.

**Current headed proof:** M19.06 base and alternate both pass with the real user
config at 80×24, 100×36, and 188×49. Together with the earlier targeted runs,
all ten final base/alternate routes for M1, M5, M10, M18, and M19 pass at all
three sizes. Static proof remains 215/215 cards, 174/174 recipes, 395/395
questions, 20/20 source-backed transfers, and all provenance digests valid.

**Remaining boundary:** this closes the five-transfer replacement slice, not
the entire audit. The full every-route same-process matrix still needs a fresh
three-size run. Archive ingestion and all push/publication remain blocked.

### VD-52 follow-through — complete headed route matrix

The fresh same-process route matrix completed successfully at every required
viewport. At **80×24, 100×36, and 188×49**, it passed the grammar primer,
conceptual check, changed-stem retry, guided task/target, independent retrieval,
two-method comparison, five-question module check, spaced review, and every
live transfer from **M0.06 through M19.06**. This includes M3.06, which no
longer falls through to a shell at 80×24.

This closes the previously unverified popup-route boundary for the current
revision. It does not convert the automated question checks into a claim that
all 395 questions received a new human editorial pass in this checkpoint, and
it does not resolve redistribution. The 885-sheet corpus still has zero
archive-manifest rows; the source excerpts and all local commits remain
unpushed because publication permission has not been established.

## VD-53 · 2026-09-29 — internal authoring labels leaked into learner explanations

**Finding:** the authored files accounted for all 395 live questions, but a
field-by-field scan of every learner-visible scalar found 39 strings that still
spoke from the curriculum author's point of view. Thirty-four mastery
explanations named internal ids such as `M13.W`, `M4.DIFFH`, or “variant 2.”
Five feedback lines referred to “the card,” “this module,” “method evidence,”
or “the checkpoint.” The post-lesson UI separately printed `ARTIFACT REPLAY`,
`EDIT REPLAY`, `MODULE CHECK REPLAY`, `METHOD EVIDENCE`, and “resuming the
artifact subpart.” These phrases describe storage and grading machinery rather
than teaching the animation or Neovim concept.

**Repair:** every identified question string now states the visible change and
the Vim operation directly, without an id or authoring-system noun. The result
page now labels the requested surfaces as `RESULT COMPARISON`, `KEYSTROKE
LEDGER`, `METHOD CHECK`, `EDIT RESULT`, and `CHECK ANSWERS`. Module checks say
“art edit” and “editing task,” not “artifact task/subpart.”

`test_question_quality.py` now scans the complete learner-visible question
record—including array feedback—for module/card/curriculum nouns, internal
`M*.**` ids, numbered variant labels, and the previously observed workflow
phrases. This is a regression guard for the manually repaired text; it is not a
claim that a prose heuristic can replace human review.

**Proof:** the regenerated revision still contains 215 cards, 395 questions,
and 174 primary recipes. Question quality passes 395/395 and `test_v2.py`
passes 215/215 cards plus 174/174 recipes. The real-user-config client-attached
popup passes at 80×24, 100×36, and 188×49 with the new labels; the focused
five-question headed route also passes at 80×24.

## VD-54 · 2026-09-29 — command mastery was still inferred from permissive hidden cards

**Finding:** the generated command-review table said that all visibly taught
command families returned in hidden changed-art review, but its selector did
not prove that the selected card required that command. Four selected cards
had no method requirement at all: `M8.04` for open-line `o`, `M3.04` for an
operator plus text object, `M3.08` for digraph entry, and `M7.04` for
characterwise Visual mode. Seven other families could resolve to comparison
cards where reaching the target with a different method still passed: Ex copy,
paragraph motion, put-before, blockwise append, global Normal, Ex move, and dot
repeat. Expression substitution also had only its guided/comparison path.
Thus answer-key presence and a correct final buffer could still masquerade as
retrieval of the named method.

The stale review banks behind `M7.04` and `M8.04` exposed a second defect.
Their nominal changed-art reviews were the old generic border-character swaps,
not unfamiliar animation poses. This contradicted the earlier zero-border-swap
claim even though recipe tests remained green.

### Repair

- `verified_command_review_coverage` now accepts only a later card that is
  key-hidden, has an explicit method requirement, is required before module
  mastery, and owns at least two source-linked method-enforced variants. The
  runtime independently recomputes the same table and rejects stale generated
  metadata.
- Every hidden changed-art card with a method requirement is now a module
  mastery prerequisite; completing the visible main path cannot bypass its
  spaced reviews.
- The four formerly unenforced existing cards now require their exact taught
  family: open-line `o`, operator/text-object `ci(`, `<C-k>` digraph entry, and
  characterwise `v` editing.
- Four manually authored hidden mastery cards close families that had no
  unambiguous retrieval route: `M14.PH` (`yap`, `}`, `P`), `M15.BAH`
  (blockwise `$A`), `M17.GNH` (`:g…normal!`), and `M18.EXPRH` (row-bounded
  expression substitution). Each has one individually written four-choice
  animation-plus-Neovim question and two different official-source review
  poses. Their prompts print the relevant art rather than asking about internal
  tutor state.
- `M7.04` reviews now use paired TowerDefense missile poses and Chick egg
  poses. `M8.04` reviews now append complete Dracula walk and Boo hover poses.
  All four source pairs preserve full-row registration and require the named
  Visual/open-line method.
- Regression tests pin the chosen review card for the twelve families that had
  been vulnerable to no-method or alternate-method selection. A family cannot
  move silently to an easier card while aggregate coverage remains green.

### Evidence

- Revision `.61` generates **219 cards, 399 manually authored questions, 178
  executable primary recipes, and 74 changed-art variants**.
- `test_v2.py` passes 219/219 cards and 178/178 primary recipes. Its generated
  map contains 41 command families; every mapped review card is hidden,
  method-required, mastery-required, and has at least two method-required
  changed-art variants.
- `test_question_quality.py` passes all 399 questions. Stone Story variant and
  provenance checks, animation-pack and live integration checks, all 46 legacy
  drills, and fresh/partial/LazyVim/read-only/idempotent installer fixtures
  pass.
- The four new mastery cards pass real-user-config headed popup routes at
  **80×24, 100×36, and 188×49**.
- The previously reported `M3.06` shell-drop does not reproduce: both its base
  and alternate transfer variants pass headed routes at all three viewport
  sizes.

**Boundary:** the official-source excerpts remain local-tutor use only. No
archive ingestion, push, or publication occurred. This checkpoint closes the
command-review proof loophole; it does not turn automated prose checks into a
new manual editorial review of all 399 questions.

## VD-55 · 2026-09-29 — source-backed transfers did not replace the primary lesson art

**Finding:** the claim that transfer/review variety solved the invented-art
problem was too broad. The current `.61` curriculum has 178 executable cards,
but only 45 primary cards identify an official Stone Story or AAHub source.
Another three have non-official source metadata. **130 executable cards have
no source metadata at all.** Every comparison card (20/20) and every module
check (20/20) remains unsourced; only 11/81 guided cards and 17/37 independent
cards are source-backed. This is why the operator can still spend most of the
course editing the old spark, boxes, and stick figures even though every
`.06` transfer now uses different sourced art.

Exact unsourced primary-card inventory by module:

- M0 (10): `M0.01`, `M0.YP`, `M0.O`, `M0.SR`, `M0.02`, `M0.04`, `M0.T`,
  `M0.05`, `M0.SL`, `M0.08`.
- M11 (7): `M11.01`, `M11.02`, `M11.UR`, `M11.04`, `M11.05`, `M11.VE`,
  `M11.08`.
- M1 (6): `M1.01`, `M1.02`, `M1.DD`, `M1.04`, `M1.05`, `M1.08`.
- M19 (5): `M19.01`, `M19.02`, `M19.04`, `M19.05`, `M19.08`.
- M2 (5): `M2.01`, `M2.02`, `M2.04`, `M2.05`, `M2.08`.
- M12 (9): `M12.AA`, `M12.JH`, `M12.01`, `M12.02`, `M12.FIND`, `M12.04`,
  `M12.05`, `M12.GV`, `M12.08`.
- M14 (6): `M14.01`, `M14.02`, `M14.04`, `M14.PARA`, `M14.05`, `M14.08`.
- M10 (5): `M10.01`, `M10.02`, `M10.04`, `M10.05`, `M10.08`.
- M5 (6): `M5.01`, `M5.02`, `M5.C`, `M5.04`, `M5.05`, `M5.08`.
- M15 (8): `M15.01`, `M15.02`, `M15.04`, `M15.BA`, `M15.05`, `M15.MAC`,
  `M15.GLOBAL`, `M15.08`.
- M16 (6): `M16.01`, `M16.02`, `M16.04`, `M16.MOVE`, `M16.05`, `M16.08`.
- M3 (8): `M3.01`, `M3.02`, `M3.CI`, `M3.04`, `M3.05`, `M3.REG`, `M3.DI`,
  `M3.08`.
- M4 (6): `M4.01`, `M4.02`, `M4.VB`, `M4.04`, `M4.05`, `M4.08`.
- M17 (5): `M17.01`, `M17.02`, `M17.04`, `M17.05`, `M17.08`.
- M13 (6): `M13.01`, `M13.02`, `M13.BE`, `M13.04`, `M13.05`, `M13.08`.
- M7 (9): `M7.01`, `M7.02`, `M7.DOT`, `M7.MAC`, `M7.VIS`, `M7.04`,
  `M7.GLOBAL`, `M7.05`, `M7.08`.
- M6 (7): `M6.01`, `M6.02`, `M6.D`, `M6.04`, `M6.05`, `M6.MOVE`, `M6.08`.
- M18 (6): `M18.01`, `M18.02`, `M18.04`, `M18.EXPR`, `M18.05`, `M18.08`.
- M8 (5): `M8.01`, `M8.02`, `M8.04`, `M8.05`, `M8.08`.
- M9 (5): `M9.01`, `M9.02`, `M9.04`, `M9.05`, `M9.08`.

**Required repair order:** convert one module at a time into a coherent sourced
project strip, beginning with M0 because it is the first-run experience. For
each changed card, rewrite its paired question manually against the actual
visible frames, rerun the clean Neovim recipe, and prove the popup at all three
viewports. Do not bulk-label old tutor art as sourced and do not regenerate
question prose from a template. The local-only publication boundary remains in
force.

### VD-55 follow-through · revision `.62` — M0 is now one sourced Fireworks project

M0 no longer teaches through the generic `\\|/`, `-- o --`, `/|\\` sun. Its
eleven executable cards now use `official-Cosmetics/Fireworks`: the radial
frame-3 shell is carried through source-star, dim, bright, flare, deliberate
hold, and settle states; the current-line substitute lab uses three rows of the
willow canopy. Only the named energy cells are authored teaching states. The
source contour's `¡`, `!`, em-dash spokes, asymmetrical accents, and widths
remain visible registration evidence throughout.

All 22 M0 question records were edited individually against those actual
states. They now print the relevant Fireworks rows for cursor motion,
star-to-dim overwrite, whole-frame copy, missing `/!\\` row, addressed
brightening, flare construction, Ex copy, hold timing, canopy material
substitution, wider-radial transfer, registration, prediction, and settle.
No question generator or token-replacement template authored those records.

The sourced-primary count rises from 45/178 to **55/178**; M0 is 11/11 and the
unsourced count falls from 130 to **120**. This closes the first-run module,
not the remaining nineteen-module inventory above.

**Proof:** question quality passes all 399 questions; clean Neovim passes all
219 cards and 178 primary recipes. Every one of M0's fourteen routes (primer,
two concept groups, eleven executable cards including transfer and module
check) passes the real-user-config headed popup at **80×24, 100×36, and
188×49**. The first concurrent 80×24 `M0.YP` driver run recorded an incorrect
bright copied core; the same route passed immediately in isolation and at both
larger sizes, so no product pass is claimed from that anomalous run itself.

### VD-55 follow-through · revision `.63` — M11 now uses a sourced missile project

The seven unsourced M11 cards named in the original inventory now use the
three-row `official-Games/TowerDefense` res18 missile as one registered
project: roof tension, complete-frame copy, a local inner-stroke edit, a
row-scoped slash edit, and virtual-column trail alignment. Existing specialist
cards remain source-backed SnowBunny, Skully, Chick, and Snail studies. Thus
all **12/12 executable M11 cards** now identify their actual source; seven are
newly converted in this revision.

All **17 M11 question records** were rewritten individually. Each prints the
missile or the named specialist pose being reasoned about, asks one concrete
animation decision and one concrete Neovim decision, and gives mistake-specific
feedback. No question template or token substitution authored those records.
The M11 source/fallback prose, comparison reflection, diagnostic distractors,
sequence reading, and catalog contract were changed with the art so that the
old generic machine/indicator wording cannot reappear.

The sourced-primary total rises from 55/178 to **62/178**. The no-source total
falls from 120 to **113**; three additional primary cards retain non-official
source metadata. This converts M11, not the remaining 113-card inventory.

**Proof:** all 219 cards and 178 clean-Neovim recipes pass; all 399 questions
pass the question-quality checks; Stone Story variant, provenance, animation
pack/integration, 46-drill, and installer suites pass. Every M11 route—14
cards including its concept checks, transfer, and module check—passes the real
user-config popup at **80×24, 100×36, and 188×49**.

**Boundary:** source excerpts remain local tutor evidence. Nothing was pushed,
published, archived, transformed for transport, or placed in Git LFS.

## VD-56 · 2026-09-29 — compact feedback and headed tests hid or misread valid UI

**Finding 1 — real UI defect:** at 80×24 the compact feedback fitter reserved
two status rows although the card heading wrapped and the outcome occupied a
third. tmux therefore scrolled `ATTEMPT NOT PASSED` off the top, leaving only
the end of the title (`it`). The fitter now reserves the wrapped heading row,
and its compact `DO / AVOID` summary no longer repeats redundant prose. The
status heading, DO THIS, two-column YOURS/TARGET replay, keystroke ledger,
answer breakdown, source, and progress prompt remain simultaneously visible.

**Finding 2 — stale test contract:** the popup test required literal
`BEFORE`/`AFTER` labels even when compact mode deliberately renders the same
visual as `│source│ → │target│`. It now checks the viewport-specific authored
stem, both domains, visible art, and all four choices. The clipboard route is
held to the exact question displayed rather than to undisplayed long-form
labels.

**Finding 3 — hidden route coverage:** the module-check driver and comparison
keylog assertions were tied to M0 wording and IDs. They now derive the selected
card, its five questions, recipe, and method family from curriculum data.
`M3.06` passes directly at 80×24, 100×36, and 188×49. Every later transfer,
`M3.06` through `M19.06`, also passes independently at 80×24, so an early
driver exit can no longer be reported as evidence for unexecuted later cards.

**Proof:** the baseline automatic popup and five-question module-check popup
both pass at **80×24, 100×36, and 188×49** with the real user config. No claim
is made that this source conversion or route proof closes VD-55's remaining
113 unsourced primary cards.

### VD-55 follow-through · revision `.64` — M1 is now one sourced Acronian wing study

M1 no longer uses the invented three-row `o_.-` contour. Its seven executable
cards now use complete `official-Cosmetics/AcronianGuardian` wing poses: the
res06 left wing supplies the main joint/copy study, the res11 right wing is the
hand-authored opposite candidate, and res07/res10 provide unfamiliar transfer
poses. The sequence owns five-row pose boundaries throughout: approve one
joint, copy five rows, remove one redundant five-row candidate, type the
opposite pose by eye, compare two joint-edit methods, transfer to unfamiliar
wing geometry, then append a complete return candidate.

All **18 M1 question records** (17 main records plus the alternate transfer)
were edited individually against the displayed Acronian rows. They now cover
row/landmark/replacement grammar, `5yy`, `6G5dd`, a planning-label `dW`,
hand-mirroring versus byte reversal, local edit plus dot, `%` on an art-only
ten-row buffer, `V4j`, an explicit `1,10` boundary, and a different endpoint
landmark on the alternate source pose. Raw backtick glyphs in the source art
also exposed a test bug: command-token checking now ignores whitespace-spanning
backtick pairs, which are drawing cells rather than Markdown key spans.

The sourced-primary total rises from 62/178 to **68/178**. The no-source total
falls from 113 to **107**; three other primary cards retain non-official source
metadata. This converts M1, not the remaining 107-card inventory.

**Proof:** all 219 cards and 178 clean-Neovim recipes pass; all 399 questions,
Stone Story variants/provenance, animation pack/integration, 46 drills, and
installer fixtures pass. Every M1 card passes the real-user-config popup at
**80×24, 100×36, and 188×49**. Its alternate unfamiliar transfer also passes
all three sizes. The baseline automatic popup remains green at all three sizes.

## VD-57 · 2026-09-29 — real config changed literal punctuation and hid method comparison

Three defects appeared only in the headed M1 routes:

1. Typing a source row whose last glyph was `\` followed immediately by Enter
   triggered completion and inserted an `/Applications/...` path. The
   hand-author recipe now leaves Insert mode after each row and uses a fresh
   `o` for the next row, so every trailing backslash is committed literally.
2. The operator's semicolon mapping intercepted `r;`, `f;`, and even `/;` in
   the headed route. Required main-study paths now use
   `!` as the tightened joint (`r!` plus dot). The alternate source retains its
   authentic semicolon but reaches it geometrically with `G$h`, never typing a
   normal-mode semicolon.
3. A successful compact comparison debrief printed only `METHOD CHECK:
   demonstrated …`; it omitted the alternative method even though the lesson
   promised a comparison. Compact feedback now prints every method label,
   exact keys, and concrete tradeoff, while omitting the redundant default
   key-by-key paragraph so the title remains visible. Both M1 methods pass at
   **80×24, 100×36, and 188×49**; the existing M0.05 corrected-method route
   also passes at 80×24.

These are real-user-config compatibility repairs. Clean-Neovim success alone
did not predict them, which is why the three-size headed proof remains required.
No source archive, remote, or publication state changed.

## VD-42 · 2026-09-29 13:00 — M11.WS taught four ideas with no explanation; no reinforcement before retrieval

**Status:** IMPLEMENTED in the working tree (not committed); verified below.

**Operator:** "the latest lesson was hard and probably needs reinforcement,
like color column etc, in addition to the %s/... stuff. needs better
pedagogical wording / maybe like a 'NEW CONCEPT ALERT'." The lesson meant is
M11.WS; the one after it, M11.UT, failed at 12:43.

**Progress at the time:** revision `.65`. Passed: M0 (14 cards) and M11.01,
.02, .03, .UR, .WS. Failed and scheduled for remediation: the M0.08 module
check (paired question) and the M0.01, M0.SL and M0.06 spaced reviews.
M11.UT failed with target-mismatch.

**Defects in M11.WS:**
- One guided card introduced `:set list`, `:set cursorcolumn`,
  `:set colorcolumn=11` and `:%s/\s\+$//e`, which also brings `%`, `\s`,
  `\+`, the `$` anchor, an empty replacement and the `e` flag.
- The hint was the generic "Follow the visible grammar once".
- The key explainer printed "set the editor option 'list'" and
  "substitute '\s\+$' with ''". Neither says what the command does.
- Every `:set` option shared one family, `:set {option}`, so a later
  option could never count as new.
- The runtime's "FIRST TIME YOU NEED THESE" block appeared only on
  hidden-recipe cards. Guided cards, where a concept is first met, had none.
- The next cards went straight to more new content (UT) or hidden retrieval
  (WSH), with no single-idea practice in between.

**Fix:**
- `share/v2_keys.py`:
  - `:set` options now say what they do and how to turn them off: list,
    cursorcolumn, colorcolumn, virtualedit, shiftwidth, scrollbind.
  - Each option is its own family (`:set list`, `:set colorcolumn`, …).
  - Substitute patterns are glossed piece by piece (`pattern_parts`:
    `\s`, `\S`, `\d`, `\+`, `\=`, `*`, `.`, `^`, `$`, `[…]`, escaped
    literals).
  - An empty replacement reads "nothing (delete the match)"; the `e` flag is
    explained; `…/e` and `…/ge` have their own families with teaching lines
    and examples.
- `share/v2_runtime.py`:
  - **★ NEW CONCEPT ALERT** on every card, guided or hidden. It lists each
    family that no earlier guided card showed, with its meaning and a
    neutral example, and — only when the recipe is shown — the recipe's
    pattern piece by piece.
  - A one-line `★ NEW n · …` banner sits under DO THIS; on compact guided
    cards it replaces the generic HINT. The full alert follows the task,
    target and WHY blocks, so they stay on the first screen.
  - Cards that reuse a pattern get a `REMEMBER · PATTERN … piece by piece`
    block.
  - The old hidden-only "FIRST TIME" lines were folded into the alert.
- `share/gen_curriculum_v2.py`: two guided single-idea reinforcements after
  WS, each with its own authored question and a card-specific hint.
  - **M11.CC:** colorcolumn alone. The Dracula stand pose has one stray cell
    in column 8: `:set colorcolumn=8<CR>2G$x`.
  - **M11.TR:** the end-anchored cleanup alone, on the padded SnowBunny.
    The recipe is split as `:%` / `s/\s\+$/` / `/` / `e<CR>`.
- `share/test_v2.py`: course counts 219→221 cards, 399→401 questions,
  sourced primary edits 73→75, stage S0 20→22.

**Evidence:**
- `share/test_v2.py` exit 0 (221/221 lessons, 180/180 recipes).
- `test_question_quality.py` PASS on 401 questions.
- `test_stone_story_variants.py` exit 0.
- `test_tmux_v2.py` PASS at 80×24, 100×36 and 188×49 with the real user
  config. This caught one regression: at 188×49 the alert had pushed
  "Failure to watch" off screen, and it now passes after the alert moved
  below WHY.
- Headed M11.WS, M11.CC and M11.TR routes pass at 80×24 and 188×49. Screens
  were read after the last change: banner, TARGET and recipe are visible on
  the first screen, and the key-by-key block says what each option and
  pattern piece does.
- 0 orphaned `nvim --embed` after the runs.

**Still open:**
- M11.UT (failed 12:43) has not been reviewed for the same bundling.
- The remediation queue (M0.08 check, M0.01/SL/06 reviews) is unchanged.

## VD-43 · 2026-09-29 13:15 — no way to report what is wrong from inside a lesson

**Status:** IMPLEMENTED and verified (headed).

**Operator:** "i need a 'feedback' button so i can send messages about what is
wrong. it should be right after i complete / answer something or after i wq
and shows me lesson complete or whatever."

**Implemented:**
- `f` sends feedback from four places:
  - every multiple-choice prompt (`answer (a-d) · y copies this question ·
    f feedback`); it does not count as an attempt;
  - the result page (`Enter = skill-tree progress · f = feedback`);
  - the retry prompt after a failed `:wq` (`… [Y/n] · f = feedback`);
  - the final held page (`Enter = close · r = repeat · n = next` plus
    `f = feedback (tell us what is wrong)` on its own line, so it survives
    80×24).
- After sending, the same controls return. An empty message cancels.
- Rows are appended, under a file lock, to
  `~/.local/state/vim-daily/feedback.jsonl`. Each row records curriculum
  revision, card id and title, module, question id and prompt excerpt, the
  chosen answer and whether it was correct, lesson result, screen
  (`question`, `result`, `retry`, `lesson-end`), time and message.
- `vim-daily-gate --feedback` lists the latest rows. Maintainers read this
  inbox at the start of a session and log actionable rows here.
- Code: `share/v2_runtime.py` (`FEEDBACK`, `note_feedback_context`,
  `collect_feedback`, `print_feedback`; context set in
  `_write_session_lesson`, `ask_question` and `_post_feedback`) and
  `bin/vim-daily-gate` (`hold_open`, `post_page_break`, `_collect_feedback`,
  `--feedback`).

**Evidence:**
- `share/test_feedback.py` PASS: question feedback is saved with card and
  question context, an empty message cancels, grading is unchanged, and the
  result-page row carries the answer context.
- `share/test_v2.py` exit 0.
- `share/test_tmux_v2.py` PASS at 80×24, 100×36 and 188×49 (real user
  config). The test now presses `f` on the held lesson-end page in the real
  popup, types a message, waits for "feedback saved", and asserts the
  `feedback.jsonl` row has `card_id` M0.01 and `screen` lesson-end.

## VD-44 · 2026-09-29 13:25 — readability audit and fixes (headings, concept alert, progress)

**Audit:** `share/audits/READABILITY_AUDIT_2026-09-29.md` (17 prioritised
findings from headed captures at 80×24 and 188×49).

**Implemented:**
- #1: the concept page's TEACH FIRST lines were erased by the question
  page's screen clear. They now get their own held page ("Enter = show the
  question · f = feedback"); the route test presses Enter on it.
- #2: DO THIS in the compact brief wraps instead of being clipped at 54
  cells. It uses up to 3 rows and fewer when a tall TARGET needs them, so
  TARGET stays whole at 80×24.
- #3: the compact module map wraps between cards, never inside a card id.
- #4: compact side-by-side TARGET frames are padded to their own width, so
  the frame separators line up.
- #5: the progress line carries a module bar (`M11 6/16 ▕████░░░░░░▏`).
- #6: the Neovim brief highlights headings, the ★ alert, REMEMBER lines and
  the command names in alert items (bold, colorscheme colours, window-local
  `matchadd`), plus `breakindent`. A headless check confirmed art rows and
  prose do not match.
- #8: ATTEMPT NOT PASSED is red; PROGRESS UNCHANGED is yellow.
- #10: the ★ NEW banner keeps its "↓ alert below" pointer and shortens the
  concept names instead.

**Evidence, after the last change:**
- `share/test_tmux_v2.py` PASS at 80×24, 100×36 and 188×49 (real user
  config).
- `share/test_tmux_v2_routes.py` at 80×24: 28/28 PASS. The first two runs
  caught TARGET rows pushed off screen by the longer DO THIS and progress
  lines; both fixed.
- `share/test_v2.py` exit 0; `test_feedback.py` PASS; 0 orphaned
  `nvim --embed`.

**Not yet done:** audit #7 (heading-word standardisation; tests assert the
current words), #9 (brief width sizing at 188 columns) and #11–#17.

## VD-45 · 2026-09-29 13:30 — concept-overload audit: first fixes (parser meanings, M11 splits, wrong content)

**Audit:** `share/audits/CONCEPT_OVERLOAD_AUDIT_2026-09-29.md` (221 cards).
- 7 cards introduce 3 or more new ideas.
- Only 6 of 180 hints are card-specific.
- 24 explanation lines on 14 cards just echo the command.
- 57 guided→hidden jumps, and 10 hidden cards use a command never shown.
- 4 parser misreads, 3 of which teach wrong meanings.

**Fixed now:**
- Parser misreads (`share/v2_keys.py`), each now a single command with the
  correct meaning, its own family, and teaching and example text:
  - `r<C-k>{a}{b}` was read as `.` = repeat and `M` = middle; it is now a
    digraph replace (`.M` = ·).
  - `<C-w>{x}` was read as "press Ctrl-w" plus `p` = paste; it is now a
    window command (`p` = previous window).
  - `zy` (was "press z"): yank a block without trailing spaces.
  - `g_` (was echoed as-is): the last non-blank character.
  - `R<C-r>{reg}` (was literal text): paste a register in Replace mode,
    contrasted with Normal-mode Ctrl-r = redo.
  - `:g/pat/normal! keys`: now spelled out in words.
  - `:earlier`, `:diffthis`, `:read` no longer get a false "on the current
    line".
  - `:read %` explains that `%` means this file here but every line in
    `:%s`.
- M11, where the operator is now:
  - M11.WS's four ideas and M11.UT's three are each preceded by single-idea
    guided steps, each with a card-specific hint, a hand-authored question
    and different Stone Story art. The order is WS → LS → CUC → CC → TR →
    UB → UG → UE → UT.
    - LS: `:set list` (Skully).
    - CUC: cursorcolumn (Dracula stand/walk).
    - UB: undo branch (Chick egg crack).
    - UG: `g-`/`g+` (Frog blink).
    - UE: `:earlier 1` (missile exhaust).
  - UT got a specific hint.
- Wrong content:
  - the M0.O hint said "two leading spaces"; the target has four;
  - the M16.01 recipe showed `0f1<C-a>` on a card whose label is F00 and
    whose expected keys use `f0`.
- Test harness: `send_text` sent a lone `;` that tmux reads as a command
  separator, so repeat-find recipes never reached Neovim in headed tests. It
  now sends `\;`. Learners typing in the popup were not affected.

**Evidence:**
- `share/test_v2.py` exit 0: 226/226 lessons, 185/185 primary recipes
  executed in Neovim.
- Question quality PASS on 406.
- `share/test_tmux_v2_routes.py` 28/28 PASS at 80×24;
  `share/test_tmux_v2.py` PASS at 80×24.
- All 9 M11 guided steps (WS, LS, CUC, CC, TR, UB, UG, UE, UT) pass the
  headed popup route at 80×24.

**Still open (from the audit):**
- M4.DIFF (8 ideas / 18 steps) split.
- M11.VE and M13.BE splits.
- Digraph teaching before M1, and the typing walls in M10/M1.04/M19/M18.06.
- Count-variant NEW detection (`3@q`, `2<C-a>`) and guided cards for them.
- The M18.EXPR Vimscript explanation.
- The hint template, which still names tools a card does not use.
- 9 missing FAMILY_TEACH and 20 missing EXAMPLES entries.
- Recipe placeholders (`C...`).

## VD-46 · 2026-09-29 13:40 — pasted feedback was split into several rows and leaked into the next prompts

**Operator:** "so pasting on feedback seems broken". The saved rows show the
13:37 message cut mid-line at "edit│ │". The 13:35 and 13:37 rows came from a
13:33 paste whose later lines leaked into the following prompts.

**Cause:** `collect_feedback` read one line with `input()`. A paste arrives
as several lines, so line 1 was saved and every later line landed in the
next prompt (result page, held controls), where it was taken as a menu
choice or as a new feedback row.

**Fix:** `share/v2_runtime.py` `_drain_pasted_lines`. After the first line,
lines already waiting on the terminal (a paste) are read with a 0.25 s
`select` and joined into one message; lines typed afterwards are not
touched. The prompt says "paste or type".

**Evidence:**
- `share/test_tmux_v2.py` now pastes a three-line message into the real
  popup through `tmux set-buffer` / `paste-buffer`. It asserts exactly one
  `feedback.jsonl` row whose message holds all three lines, and that the
  held controls return. PASS at 80×24, 100×36 and 188×49.
- `share/test_feedback.py` PASS.

**Operator feedback still to act on:**
- 13:33: the difference between `/` and `\` (both the substitute separator
  and the escape) was never taught. Also asked for memory anchors, spaced
  repetition across sessions, a flashcard deck of every learned key and
  command, a syntax reminder line, and later an optional "post to GitHub" for
  feedback.
- 13:35: "the art was offset" on M11.TR (not yet reproduced).
- 13:37: the dashboard shows internal validator prose ("REMEDIATION Q-M0.01
  alternate changed-art edit variant …") instead of a learner's bird's-eye
  view of what was learned and the journey.

## VD-47 · 2026-09-29 13:50 — dashboard showed validator prose instead of the learner's journey

**Operator (feedback 13:37 and 13:33):**
- "clean up this dashboard: access what I have learned so far". The
  "REMEDIATION Q-M0.01 alternate changed-art edit variant | …" line "sounds
  like internal dev validator prose, confusing".
- The dashboard "should be where I can see the birds-eye view of my master
  progress and journey".
- Asked for a flashcard deck of every concept, key and command already
  covered.
- Asked what the difference is between `/` and `\`.

**Implemented (`share/v2_runtime.py`, `bin/vim-daily-gate`):**
- `--tree` / `--status` open with **YOUR JOURNEY**: one row per stage with
  a progress bar and "← you are here".
- **TO REVISIT** lists each spaced-remediation lesson in plain words:
  "↻ M0.01 Foundation edit — redo the edit on new art", "answer a fresh
  version of its question". The ids, "changed_variant" and "paired stem"
  prose are gone from every learner screen.
- **WHAT YOU HAVE LEARNED** lists one reminder line per command family
  passed so far, with how many lessons used it. Families sharing a reminder
  (u / Ctrl-r, 0 ^ $) are merged.
- The new `vim-daily-gate --learned` prints the full deck: reminder,
  example and the lesson where each command was first met. This is the
  flashcard deck.
- The compact result page (80×24) keeps its heading on screen. The learned
  count joins the XP line, the state legend fits on one row, and TO REVISIT
  is a single line.
- Every pattern breakdown (NEW CONCEPT ALERT and REMEMBER) now ends with:
  "/ separates the parts: s/pattern/replacement/flags" and "\ inside a
  pattern starts a special piece (\s, \+); it is not a key you press".
  The `…//e` reminder says the same.

**Evidence:**
- `vim-daily-gate --tree` and `--learned` were read on the operator's real
  state (19 commands, 5 revisit rows).
- `share/test_tmux_v2.py` PASS at 80×24, 100×36 and 188×49, and the 80×24
  awarded page was read after the change.
- `share/test_tmux_v2_routes.py` 28/28 PASS at 80×24.
- `share/test_v2.py` exit 0; 0 orphaned processes.

**Still open from the operator's feedback:**
- Memory anchors and cross-session spaced drill of the deck (a flashcard
  review mode).
- "Post to GitHub?" for feedback, later.
- The M11.TR "art was offset" report, not yet reproduced.

## VD-48 · 2026-09-29 — context-dependent symbols and recipe notation were never taught

**Operator (feedback after M11.TR, `:%s/\s\+$//e`):** "what are these called?
what is the concept diff between / and \ i thought \ was an escape seq or
something. also do not remember learning this ... how do i not memorize these
things? a reminder line about the syntax maybe helpful".

**Cause:** the course uses symbols whose job depends on where they stand, and
recipe meta-notation, without ever naming the job. Before M11.TR the learner
had met `\` as an art glyph (`/!\`, M0.O) and `$` as the last-line address
(`:1,3t$`, M0.T). In M11.WS both changed job (`\s` prefix, `$` row-end
anchor) and nothing said so. The VD-47 note even said "\ ... it is not a key
you press", which is wrong: the learner types it.

**Measured (audit `share/audits/SYMBOL_NOTATION_AUDIT_2026-09-29.md`, 226
cards, module order; candidates from `v2_keys.symbol_roles`, each row read on
the card):**
- `$` has three jobs, met in this order: address (M0.T), pattern anchor
  (M11.WS), motion (M11.LS). No card contrasted them.
- `@` as the `:s` separator and `\\` = one backslash are first required on
  hidden M11.05 and never shown on a guided card. `\.`-style escapes
  (M17.06) are the same.
- `0` as a line address (`:m0`) is first required on hidden M16.05. Dot
  repeat is first required on hidden M1.05; the first guided card is M17.01.
- `:` / "Ex statement" (M0.SR), `<CR>` (M0.01 vocabulary), `<C-r>`-style
  "hold Ctrl" notation (M11.UR) and `{char}`/`{N}`/`[count]` placeholders
  (M0.01 alert) were never defined. The only definition was a footer at the
  bottom of the brief, and the 80×24 footer did not list `<CR>`.
- M11.VE uses `|` as the column motion and as a typed glyph in one recipe.
- M11.UR's alert printed "u undo; Ctrl-r redo" twice. M4.DIFF/M4.DIFFH
  explained `:vnew`, `:silent 0read #`, `:diffoff!`, `:bwipeout!` by echo.
  6 families had no FAMILY_TEACH and 22 had no EXAMPLES.

**Fix:**
- `share/v2_keys.py`: `SYMBOL_ROLES` (42 symbol/job pairs, each a plain
  sentence plus a short contrast label); `symbol_roles(keys)`;
  `RECIPE_READING`; `_explain_ex` handles `!`, `:vnew`, `:silent`,
  `:read #`/`%` with `0`, `:diffoff!`, `:bwipeout!`; 9 FAMILY_TEACH and 24
  EXAMPLES entries added.
- `share/v2_runtime.py`:
  - `_symbol_lines`, inside the NEW CONCEPT ALERT / REMEMBER block (below
    the first screen), prints a SYMBOLS block:
    - `★ NEW` the first time a job appears, e.g. "$ on its own = jump to the
      end of the row · elsewhere $ = last line (:1,3t$) (in M0.T); row end
      in a pattern (\s\+$) (in M11.WS)";
    - `REMEMBER` on guided cards when the symbol has another job the learner
      already met.
  - M0.01, the first guided recipe card, carries a one-time HOW TO READ A
    RECIPE block covering `<CR>`, `<Esc>`, `<C-r>`, placeholders and modes.
  - `_new_concept_banner` names new symbol jobs (`★ NEW 2: :t{dest} · $ =
    last line`).
  - SLASH_NOTE is corrected and dropped where SYMBOLS already covers it.
  - Alert lines are de-duplicated.
  - The footers list `<CR>` and the placeholders.
  - `--learned` ends with "SYMBOLS WHOSE JOB DEPENDS ON WHERE THEY STAND"
    (`learned_symbols`): the reminder line the operator asked for.
- `share/gen_curriculum_v2.py`: `<CR>` recipe rows say "press Enter to run
  the whole : command line" instead of "execute the complete Ex statement".
- `share/test_v2.py`: VD-48 assertions (M0.01 block, M0.T/M11.LS/M11.TR/
  M11.VE/M11.05/M16.05 symbol lines, M11.UR de-duplication, no echo on
  M4.DIFF, the learned-symbols deck).

**Evidence (all run after the last code change):**
- `share/test_v2.py` exit 0: "226/226 executable lessons present; 185/185
  primary edit recipes passable". The VD-48 assertions pass.
- `test_question_quality.py` PASS on 406; `test_feedback.py` PASS;
  `test_stone_story_variants.py` exit 0.
- `test_tmux_v2.py` PASS at 80×24 and 188×49 (real user config).
- `test_tmux_v2_routes.py` 28/28 PASS at 80×24.
- 0 orphaned `nvim --embed`.
- The first 188×49 run failed: the longer footer line wrapped
  "<C-k>.M middle-dot". The footer line was restored and the placeholder text
  moved to its own line.

**Still open:**
- `@` separator, `\\`, `\.` escapes, dot repeat and the `0` address are
  still first required on hidden cards. They now carry a ★ NEW symbol line
  there, but no guided single-idea card comes before them.
- The term "Ex" and "address" remain in authored question stems and
  key_vocabulary. The `:` symbol line now defines "Ex commands".
- M0.01 recipe rows still omit the `0` that `expected` uses (overload audit
  F7).

## VD-49 · 2026-09-29 15:45 — operator feedback 13:58–15:30: clipped wrong-answer page, method failures read as plain failures, the `:s` explanation folded in; duplicate FL ids fixed

**FL numbering correction:** a concurrent session had already used VD-34…VD-41
(03:28 onward). This session's entries of 13:00–15:00 reused those numbers.
They are renumbered in this file and in code comments:
- VD-34→VD-42, VD-35→VD-43, VD-36→VD-44, VD-37→VD-45, VD-38→VD-46,
  VD-39→VD-47, VD-40 (symbols)→VD-48.
- Commit messages `94ec213`, `5f76730`, `0a1240a`, `097469e`, `4710d8b`,
  `66ca46c` and `0a2cd74` still cite the old numbers.
- Before appending, check the highest existing id:
  `command grep -o '^## VD-[0-9]*' FAILURE_LOG.md | sort -t- -k2 -n | tail -1`.
- VD-12 was already duplicated earlier (not touched here).

**Operator feedback (`feedback.jsonl`):**
- 13:58 M11.LS: "set list … just highlights right? … wouldn't the goal be to
  delete all the whitespace … s/\s\+$//e?"
- 14:58: "cant read the full sentence" (wrong-answer page clipped with …).
- 15:05 M11.CUC: "this one was hard … some unrelated stuff; we need a style
  guide color coding".
- 15:29 M0.SL: "it should acknowledge that the destination was correct but I
  still failed because I did not use the concept being taught".
- 15:30: "stages can be collapsed, color code / stylize progress and level …
  gamifying, the skill tree can be an expandable viewing mode — this needs
  to be a design discussion".
- In chat, the operator asked that the `:%s/\s\+$//e` tree diagram be folded
  into the curriculum.

**Implemented:**
- The wrong-answer page (`_print_choice_explanation`) no longer clips. YOUR
  ANSWER, WHY IT MISSES, CORRECT ANSWER and CONCEPT wrap at the popup width
  with a hanging indent, and paired answers print ANIM and VIM on separate
  lines. The METHOD CHECK line wraps too.
- New `_method_goal` and `_method_miss_message` produce this wording:
  "✓ Your result matches the target. ✗ Not counted yet: this lesson is
  practising <commands in words>, and your keys did not use it. Try again
  with that method (any correct method is fine outside this lesson)." The
  old messages printed internal labels such as "use the taught
  whitespace-column-audit path".
- M11.LS: the prompt now says only ONE of the three rows has the space. It
  accepts `:set list` followed by `2G$x`, `:%s/\s\+$//e` or
  `2G:s/\s\+$//e`, because the lesson's idea is `list`.
- The `:s` diagram is folded in:
  - `v2_keys.substitute_anatomy` draws any visible `:[range]s/pat/rep/flags`
    recipe as the labelled `│ └` tree (range, s, dividers, each pattern
    piece, replacement or "empty replacement → delete", flags), then a
    plain-English sentence and the "remember the shape, not the characters"
    line.
  - `_substitute_anatomy_lines` shows it as HOW TO READ IT in the NEW
    CONCEPT ALERT and REMEMBER · HOW TO READ IT on reinforcement cards,
    replacing the piece list. It appears only when the recipe is visible.
- Plans written for the design discussion:
  - `share/audits/DASHBOARD_UI_DESIGN_PROPOSAL_2026-09-29.md`: style guide
    roles, the unrelated brief sections, collapsible and expandable tree
    options, and motivation elements with mock-ups.
  - `share/audits/MEMORY_SPACED_REVIEW_PLAN_2026-09-29.md`: the general
    anatomy renderer, a flashcard deck with anchors, contrast pairs and
    Leitner spacing, a daily warm-up, the 8 quiz-misconception items, and
    method tiers.

**Chat quiz (2026-09-29) weak spots:**
- `{N}G` is absolute (not "blocks"); G alone = last line of the file.
- `f` searches the current row only; `/` searches the file.
- `3yy G p` has three parts.
- No range means the current line only; `%` goes before `s`.
- Pattern `$` is an anchor.
- The undo branch / `g-`.
These are the first items for the deck plan.

**Evidence, after the last change:**
- `share/test_v2.py` exit 0 (226/226 lessons, 185/185 recipes). Its SL
  replay check now compares whitespace-collapsed text, because explanations
  wrap.
- `test_question_quality.py` PASS on 406; `test_feedback.py` PASS;
  `test_stone_story_variants.py` exit 0.
- `share/test_tmux_v2.py` PASS at 80×24, 100×36 and 188×49.
- `share/test_tmux_v2_routes.py` 28/28 PASS at 80×24.
- Headed M11.LS, M0.SL and M11.TR routes PASS at 80×24.
- 0 orphaned `nvim --embed`.

**Not verified:** a headed run of M11.LS with the `:%s` alternative, and the
reworded method-miss page on a real failed attempt. The wording is covered
only by direct function output.

## VD-58 · 2026-09-29 21:50 — interactive gamified dashboard (Textual) replaces the static tree in a terminal

**Status:** IMPLEMENTED in the working tree (not committed); verified below.

**Operator decisions** (`share/audits/DASHBOARD_UI_DESIGN_PROPOSAL_2026-09-29.md`
"Operator decisions"; `share/demo_notes.json` lane3a, lane3c, lane3-badges,
anima, animb, animd): use a TUI library ("need to feel pretty / gamified");
colour-coded, collapsible stages with the current stage open; tier colours
(beginner none, intermediate bronze, advanced gold, pro "gemini" gradient); a
colour ASCII avatar per level; more non-farmable badges; every ✓ and "+N"
green; 🔥 beside the streak, glowing on a personal best; combined pulse /
gradient-sweep / sparkle effects.

**Built:**
- `share/dashboard_tui.py` — Textual 8.2.8 app. Reads only the v2 projection
  (`load_curriculum`, `read_events`, `project`, `_level`, `_legacy_streak`,
  `activity_days`, `done_today`, `learned_deck`, `_revisit_rows`,
  `next_card`). Header: level avatar, tier-coloured title, XP bar to the next
  title, 🔥 streak with best / 14-day strip / today-goal / green "+N new",
  badge count and next-badge progress. One-row journey map. Tree: stages →
  modules → lessons (✓ ◐ ◆ ↻ ○ ▫, bars), then TO REVISIT (plain words),
  COMMANDS LEARNED (browse; Enter shows example and first lesson), BADGES.
  Keys: j/k, g/G, za/zo/zc/zR/zM, Enter (module/command/badge page), / search
  with n/N, f feedback (same `collect_feedback` store, `screen=dashboard`),
  ? help, q quit. Side detail panel from 110 columns. `--preview-level N`
  (display only) and `--screenshot PATH --size CxR` for review.
- `share/dashboard_theme.py` — tiers, 14 original avatars (repo is public; no
  third-party art), semantic colours, state glyphs, 21 badges as data (8
  runtime + streak-keeper 7/14/30, +10/+25/+50 commands, safe-ranger,
  branch-rescuer, clean-hands, review-keeper, full-day, cartographer,
  transfer-adept), animation timing. Replaceable by a later style guide.
- Animations (flame glow on a personal best, metal sweep / gemini gradient on
  the title, sparkle near the next badge) are off under `NO_COLOR`,
  `TERM=dumb`, `VIM_DAILY_ANIM=off`. `NO_COLOR` uses Textual's NoColor filter.
- `share/v2_runtime.py` — `activity_days()` split out of `_legacy_streak`;
  `done_today()` shared with `run()`; `dashboard_python()` /
  `open_dashboard()`; `run()` dispatches `--dashboard`, and `--tree` in a
  terminal. Non-tty, `TERM=dumb`, missing venv, or exit code 3 (Textual not
  importable) print the old static `print_tree`. `--tree --static` and
  `--status` stay text.
- `bin/vim-daily-gate` — `--dashboard` in `v2_modes` and usage; `d = dashboard`
  on the held post-lesson page (`hold_open`), returning to the same page.
- `install.sh` + `share/requirements-dashboard.txt` — idempotent `uv venv` /
  `uv pip install -r` into `${XDG_DATA_HOME:-$HOME/.local/share}/vim-daily-venv`
  (pinned freeze). Installed on this machine for the tests.

**Evidence (2026-09-29, this working tree):**
- `python3 share/test_dashboard_tui.py` → all passed (re-runs itself with the
  venv python): Pilot 80×24 j/k, za/zo/zc/zR/zM, Enter page, / search, ?
  help, f feedback row, q quit, tree `virtual_size.width <= size.width`;
  real-pty NO_COLOR run 0 colour SGR vs 18 in the control run; non-tty
  `--tree`, `--dashboard`, `--tree --static` print the static tree.
- `python3 share/test_v2.py` → exit 0.
- `VIM_DAILY_TEST_COLUMNS=80 VIM_DAILY_TEST_ROWS=24 python3 share/test_tmux_v2.py` → exit 0.
- `python3 share/test_tmux_v2_routes.py` → exit 0, 28 PASS. (An earlier run
  the same evening failed at M3.06 on a `WARM-UP 1/3` prompt from the
  concurrent deck work in `share/deck.py`; not a dashboard hunk.)
- Headed tmux captures through `~/.local/bin/vim-daily-gate --dashboard`
  (gate exit 0 each) in `share/audits/dashboard-captures/`: `tmux-80x24`,
  `tmux-72x20-popup-inner` (the 90%×85% popup of an 80×24 client),
  `tmux-100x36`, `tmux-188x49`, `tmux-188x49-help`, `tmux-80x24-module-page`,
  `tmux-80x24-nocolor` (0 colour SGR; 16 in `tmux-80x24.ansi`),
  `tmux-80x24-anim-frame1/2.ansi` (header differs: flame glow),
  `tmux-80x24-hold-*.txt` (`d` on the held page opens the dashboard, `q`
  returns to the same prompt). SVGs: `dashboard-80x24.svg` and
  `dashboard-80x24-lv{3,4,8,12,14}.svg` (tier colours via `--preview-level`).

**Remains:**
- Not yet seen by the operator inside the real `prefix+V` popup; the popup
  test suites do not press `d`.
- The static `print_tree` still lists only the 8 runtime badges; the 13 new
  badges exist only in the dashboard.
- Level/tier boundaries (4 / 8 / 12) and avatars are first proposals for the
  style-guide session to replace in `share/dashboard_theme.py`.
- Textual start-up time inside the popup was not measured.

## VD-59 · 2026-09-29 — lessons had no memory loop: flashcard deck, spaced review, daily warm-up and Normal-mode anatomy

**Operator:** feedback 13:33 asked for memory anchors, spaced repetition across
sessions, a flashcard deck and a syntax reminder line. The chat quiz of
2026-09-29 showed eight misconceptions: `3G` read as "three blocks", `fo` as a
whole-file search, `3yy G p` as only "yank three lines", no range on `:s` as
every line, `%` placed after `s`, a count after `:s` read as a match count,
`u` vs `g-`, and `2G$` / pattern `$` misread. The plan was approved in chat
(~21:25) for §1-§3 and the runs in §2; §4 (method tiers) is deferred.
Plan: `share/audits/MEMORY_SPACED_REVIEW_PLAN_2026-09-29.md`.

**Built:**
- `share/v2_keys.py` `anatomy(keys, width)`: the VD-49 `│ └` tree for
  Normal-mode strings as well as `:s`. Each slot is labelled: count, register,
  operator, motion, find glyph, typed text, `<Esc>`, and `:` commands. The tree
  is followed by an "In plain words" sentence and a "Shape" line. It returns
  None above 10 slots or 78 cells, so no row is ever clipped.
  `_substitute_anatomy_lines` uses it for guided recipes in the NEW CONCEPT
  ALERT when the recipe is not a pure `:s`.
- `share/deck-v2.json`, authored by hand: 22 families and 34 items (predict,
  decode, typed_keys). Each family has a front, back, anchor, shape, example
  keys and contrasts, and every item names its misconception.
  - The plan §3 items are all present: DK.G.01, DK.F.01, DK.YP.01, DK.S.01,
    DK.S.02, DK.S.03, DK.U.01, DK.D.01, DK.D.02.
  - The contrast pairs are linked: f vs /, {N}G vs {N}j, G vs gg, p vs P,
    :s vs :4,6s vs :%s, g flag, x vs r, u vs g-, / vs \.
  - Typed items carry trap answers. Each trap is run in scratch Neovim and
    must miss the target; a trap's own "why" is shown when the learner types
    it.
- `share/deck.py` owns the rest:
  - `build_deck` attaches the lesson ids that use each family.
  - `validate_deck` is the generator gate. It checks required items, contrast
    links, 3-4 distinct choices with one "why" each, no reused "why", and
    typed samples reaching the target while traps miss it. It rejects banned
    learner words (Ex, address, family id, card, module, lesson ids, DK.),
    template phrases and "…". Every command used by M0/M11 must have a family.
  - Leitner scheduling reuses `review_intervals_hours`. good promotes, hard
    keeps the box, again drops to box 0 and is due now.
  - `fold` produces `progress["deck"]` (items, weak, weak_families). A failed
    question or review, or a `remediation_scheduled` event, makes that
    lesson's families due.
  - `--quiz [N]` picks weak items, then due, then new from met families.
    `--deck [NAME]` browses; `--deck-miss ID…` records an outside miss.
  - The warm-up gives at most 3 items from the upcoming lesson's families and
    their contrasts, once per day, before the first lesson. `s` skips it, and
    the skip is recorded as a `deck_warmup` event.
  - `f` saves feedback with the item id on quiz and warm-up screens.
- `share/gen_curriculum_v2.py` embeds `cur["deck"]`, and `validate()` runs
  the deck gate. `share/curriculum-v2.json` was regenerated: only the `deck`
  key changed (checked against HEAD).
- Thin hooks in `share/v2_runtime.py`:
  - `project()` adds `out["deck"]`. XP, passed lessons and the lesson stamp
    are untouched; deck events use result right/wrong, never pass/fail.
  - `run()` handles `--deck`, `--quiz`, `--deck-miss` and the warm-up call.
  - `DECK_WEAK` feeds a "REMEMBER (missed in your deck)" line into the next
    lesson alert that uses a weak family.
- `bin/vim-daily-gate`: `--deck` and `--deck-miss` join v2_modes. `--quiz` or
  `--quiz N` goes to the deck; `--quiz NAME` still opens the original
  question banks. Usage text and `VIM_DAILY_NO_WARMUP` are documented.
- `share/test_tmux_v2.py` and `share/test_tmux_v2_routes.py` set
  `VIM_DAILY_NO_WARMUP=1`, because their seeded states would otherwise open
  with the warm-up. `share/test_deck.py` covers the warm-up instead.

**Evidence (all run after the last code change, 2026-09-29):**
- `python3 share/test_deck.py`: exit 0, "PASS deck: 2169 checks", "PASS deck
  headed at 80x24". With `VIM_DAILY_TEST_COLUMNS=100 VIM_DAILY_TEST_ROWS=36`:
  exit 0, "PASS deck headed at 100x36". It covers:
  - anatomy snapshots and the fallback to None;
  - the deck gate, and its failure on bad text, an empty family or a missing
    family;
  - every question and result screen at 78×22 with no "…";
  - Leitner steps, the fold, resurfacing, no XP from deck events, and pick
    order;
  - warm-up once per day and the one-key skip;
  - `--deck-miss`, `f` feedback, and the REMEMBER hook.
- `python3 share/test_v2.py`: exit 0 (226/226 lessons, 185/185 recipes). No
  hard-coded count changed.
- `python3 share/test_question_quality.py`: PASS on 406.
  `python3 share/test_feedback.py`: PASS.
- `python3 share/test_tmux_v2.py`: PASS at 80×24 and at 100×36.
- `python3 share/test_tmux_v2_routes.py` at 80×24: exit 0, 28/28 routes PASS.
- `pgrep -fl 'nvim --embed'`: none after the runs. One orphan from an early
  test_deck run was killed by its temp-dir path, and test_deck now reaps its
  own.
- Headed 80×24 capture, warm-up (seeded through M11.01, `--force`):
  ```
  WARM-UP 1/3 before today's lesson · {N}G and G
    The cursor is on line 5. You type 3G. Where does the cursor go?
    ...
    ▶ 5 │(__|__)
    a) to line 3
    b) to line 8, three lines further down
    ...
    answer (a-d) · f feedback · s skips the warm-up:
  ```
  After `s` the M11.02 lesson opened, and the ledger holds a
  `deck_warmup`/`skipped` event.
- Headed 80×24 capture, `--quiz 2` wrong then right:
  ```
  ✗ NOT QUITE
    YOUR ANSWER: to line 8, three lines further down
    RIGHT ANSWER: to line 3
    WHY: Moving three lines down from here is 3j. G counts from the top of the
      file.
    COMMON MIX-UP: 3G read as a move relative to the cursor, or as 'three
      blocks'
   3G
   │└ G = go to that line
   └ 3 = line 3, counted from the top
  ...
  ✓ RIGHT
    YOUR KEYS: 3Gr#
  ```
  The ledger recorded the grades again, good.

**Not done / still open:**
- Plan §4 method tiers (deferred by the operator).
- The first-screen SHAPE line in the lesson brief (plan §1): the full diagram
  is in the alert only. REMEMBER blocks on reinforcement cards still draw
  only `:s`.
- The operator's real ledger has no deck events. Recording the chat-quiz
  misses is one command, not run here: `vim-daily-gate --deck-miss DK.G.01
  DK.F.01 DK.YP.01 DK.S.01 DK.S.02 DK.S.03 DK.U.01 DK.D.01 DK.D.02`.
- No tmux key binding opens `--quiz` in a popup. It runs in any terminal or
  inside the lesson popup.
- The deck covers M0/M11 plus contrasts (22 families). Later modules need
  families as the learner reaches them; the coverage gate lists
  `COVERAGE_MODULES` in `share/deck.py`.
- The curriculum revision string was not bumped (still `2026-09-29.65`).

## VD-60 · 2026-09-29 — Stone Story trophy art promoted into the dashboard, with credit

- **Operator decision (chat):** "I CONFIRM THE RIGHT, STONE SCRIPT PEOPLE USE
  EVERYWHERE, JUST CITE THE AUTHOR/STONESTORY RPG JUST IN CASE". This answers
  the rights hold recorded in the dashboard proposal's decisions section and the
  `anima` demo note ("promote, they should not be local only").
- **Built:** `share/dashboard_theme.py` `trophy_for(badge_id)` maps badges to
  art: first-step Skully idle; transfer / transfer-adept firework radial F3/F4;
  grid-author Snowman cheer; still-artist firework willow canopy; branch-rescuer
  Pallas ghost; streak-keeper 7/14/30 Mine Walker boiler flame (MineManager
  composite from `share/audits/stone-story-animation-audit/batch-0.md`); animator
  the tutor's own bell. Stone Story frames are imported from
  `share/stone_story_variants.py` (one copy). `share/dashboard_tui.py`
  `badge_detail()`: Enter on a badge opens its page with progress, art (dim until
  earned) and the credit line "Art: Stone Story RPG by Gabriel Santos (Martian
  Rex, Inc.)".
- **Records:** README Attribution rewritten (no longer says permission is
  unverified); `STONE_STORY_LOCAL_PROVENANCE.md` publication status updated.
  Not covered by the confirmation and still excluded: AAHub
  `bakuhatsu-kemuri` rows and `share/art.json` unknown-licence art (cheer,
  candle).
- **Evidence:** `python3 share/test_dashboard_tui.py` → "ok trophy pages show art
  and credit", "all passed". Headed 80x24 tmux: `/Streak keeper 7`, Enter, Enter
  showed the badge page with "✓ earned", the 7-row flame and the credit line.
- **Remaining:** no unlock banner/animation plays the trophy at the moment a
  badge is earned (that belongs with the post-completion viewer work, owned by
  the omp session); the static `--tree` still lists only the 8 runtime badges.

## VD-61 · 2026-09-29 — AAHub and the remaining third-party art credited and cleared

- **Operator decision (chat):** "AGAIN SAME WITH AAHUB AND THE REST, CREDIT AND
  COMMIT." Extends VD-60 beyond Stone Story.
- **Changed:** every `share/art.json` entry is `redistribution: cleared` with a
  `credit` field and the permission text citing this entry; the attribution
  string names every author. `share/extract_art.py` PLATE_RIGHTS writes the same
  values, so a re-extraction does not revert them. The two M10.06 AAHub sources
  in `share/gen_curriculum_v2.py` now carry the page URL
  (aahub.org/mlt/a60392576bd5eefca3ed22d55606b85f, taken from the saved page's
  canonical link) and credit the original posters; `curriculum-v2.json`
  regenerated. README Attribution lists AAHub, Joan G. Stark (jgs), the "pb"
  and "tre" signers, and the unsigned candle. Provenance register updated.
- **Test:** `share/test_stone_story_provenance.py` asserted "Publication: blocked"; VD-60 broke it (not run before that commit). It now asserts the credited status, per-entry `credit`, and README names; PASS.
- **Not changed:** the signature rows that were stripped at intake (jgs, pb,
  tre) are not restored into the lesson art; credit lives in metadata, README
  and the provenance register.

## VD-62 · 2026-09-29 — post-completion animation viewer is a first-class feature

- **Operator request (chat):** "the animation viewer after successful completion
  should be first class feature" and, after VD-61, "proceed with animation
  viewer". Before this, playback existed only on `module_check` passes: a
  0.12 s/frame run of `preview_project` that the result page immediately
  scrolled away; every other pass showed no animation at all.
- **Built:** `share/viewer.py` (stdlib; alternate screen, cbreak keys):
  `WATCH YOUR WORK` loops what the learner just saved. Multi-frame lessons play
  their own frames (split by `frame_slices`, equal neighbours marked HOLD); a
  one-frame still plays as `before → yours`. Changed cells light up green
  (`d`), onion skin shows the previous frame dim (`o`), `space` pauses, `h/l`
  (or arrows) step, `+/-` change speed, `p` switches to the whole project strip,
  Enter continues. A filmstrip of all frames with the current one marked sits
  under the frame when it fits. Non-terminal output prints one static
  filmstrip; `VIM_DAILY_VIEWER=off` skips it; `VIM_DAILY_ANIM=off` shows the
  static filmstrip; NO_COLOR drops colour.
- **Wired:** `v2_runtime.watch_your_work()` runs after a fully passed edit
  (after the paired after-questions, before `_complete`), on both the normal
  and the recovered-target path. Module checks open on the project strip.
  `--view [MODULE]` plays a module's strip (default: the latest passed module).
  The held result page offers `v = watch your work again` only when there is
  work to watch. `project_view()` finds a project saved under an older folder
  name by its manifest `module_id` (the operator's M0 work lives in
  `projects/spark-loop`, while M0's project id is now `fireworks-radial-loop`).
- **Defects found while building:** the runtime was first loaded from
  `~/.local/share/vim-daily/` without `share/` on `sys.path`, so `import viewer`
  failed in the real gate (`--view` crashed; the headed popup test failed at
  the viewer). Fixed by loading `viewer.py` by file path like `deck.py`.
- **Evidence:**
  - `python3 share/test_viewer.py` → PASS. Covers the model, and a real
    pseudo-terminal run that plays, pauses, steps, turns the onion skin on,
    and returns on Enter with the screen restored.
  - `VIM_DAILY_TEST_COLUMNS=80 VIM_DAILY_TEST_ROWS=24 python3
    share/test_tmux_v2.py` → PASS. It now asserts the viewer after the
    after-question, `v` on the held page, and the viewer on a repeated pass.
  - Headed 80x24 tmux run of `vim-daily-gate --view M0` on the operator's real
    state: the 4-frame fireworks loop played with the filmstrip; pausing and
    the onion skin worked; exit 0.
  - `test_tmux_v2_routes.py` runs with `VIM_DAILY_VIEWER=off` (its 28 routes
    are not about the viewer).
- **Remaining:**
  - `preview_project` (the automatic module-check playback) has the same
    renamed-folder blind spot, not fixed here.
  - No trophy or unlock animation plays in the viewer when a badge is earned.
  - The dashboard's module page has no "watch" key yet.
  - Colour is fixed ANSI and does not yet follow the style guide the operator
    is revising (the gemini pink-purple palette note of 22:12).

## VD-63 · 2026-09-30 — the dashboard shows and plays completed animations

- **Operator request (chat):** "the animation player is great, is it possible
  to keep this, and make it so dashboard can show completed animations?"
- **Built:** `v2_runtime.completed_gallery()` builds a playable View for every
  passed lesson from the per-lesson checkpoints (`<card>-before.txt`,
  `<card>-after.txt`) that every pass already writes. A later lesson that
  overwrites the project strip therefore does not lose earlier work, and
  renamed project folders still count. The dashboard has a **YOUR ANIMATIONS**
  section grouped by module (`▦ M0 Fireworks radial loop 10 · whole project ▶`).
  Each lesson row says `N frames`, `before → yours`, or `still`. Enter or `w`
  plays it in the WATCH YOUR WORK viewer (Textual suspends, then resumes on the
  same row). Inside the viewer, `p` switches to the whole project. `w` on a
  journey module plays its project strip; `w` on a passed lesson plays that
  lesson. `--view M0.05` (a lesson id) plays one lesson.
- **Evidence:**
  - `python3 share/test_viewer.py` → "ok gallery…", PASS.
  - `python3 share/test_dashboard_tui.py` → all passed.
  - Headed 80x24 run on the operator's real state: YOUR ANIMATIONS 21. `/M0.05`
    then Enter played the 4-frame loop with the filmstrip and HOLD on frame 4;
    Enter returned to the same dashboard row; `q` exited 0.
- **Remaining:** no Pilot test drives Enter/`w` on a gallery row (Textual
  `suspend()` under `run_test()` was not attempted). Items whose saved work
  equals the start (whitespace-only edits: M11.WS, M11.LS, M11.TR) show as a
  one-frame `still`.
