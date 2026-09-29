# Curriculum v2 implementation plan

Status: P1-P6 runtime/content work and the automated portions of P7 are
implemented, 2026-09-27. This file records the executed dependency order for
[CURRICULUM_V2_SPEC.md](CURRICULUM_V2_SPEC.md). A complete human M0→M18 journey,
long-gap observation in wall-clock use, and private-state migration rehearsal
remain product acceptance; they are not automated-test claims.
The concrete card sequence to author is
[CURRICULUM_V2_CARD_CATALOG.md](CURRICULUM_V2_CARD_CATALOG.md).
The current 46 drills and private progress files must continue to work until a
tested migration exists. All pre-existing uncommitted changes are user-owned.

Implementation receipt: `share/test_drills.py` passes 46/46 under a clean config;
`share/test_v2.py` validates 19 modules, 152 cards, 190 questions, graph/state
transitions, and passes 114/114 executable v2 recipes under both clean and
real-config Neovim, plus all 38 changed-art transfer variants and all 38 named
comparison paths. Revision `.18` passes the automatic-popup and full conceptual,
remediation, edit, check, review, and M0-M18 transfer route matrices at 188×49,
100×36, and 80×24.
`bin/vim-daily-gate --tree` and `--export-progress` pass against an
isolated fresh XDG state root. Runtime state is append-only `events-v2.jsonl`
plus a rebuildable projection; project strips, manifests, transfer files, and
checkpoints live outside Git under the user's XDG state directory.

## Sequencing and release boundary

Work in dependency order. Ship M0-M2 behind an explicit opt-in before switching
the automatic hourly route. Keep the v1 command (`--drill`) and its 46/46
passability suite as a regression path until v2 passes migration and real-user
acceptance. Do not regenerate or overwrite `share/curriculum.json` with a new
schema as the first move.

| Phase | Work and concrete files | Exit proof |
|---|---|---|
| P0 — freeze evidence and rights | Record current 46 IDs, tier/quiz/progress behavior, source art inventory, and `share/test_drills.py` clean/real results. Review the README/extractor tension in spec E11: all ten walk and seven pyramid frames are already present as separate entries. Make an import ledger for any third-party curriculum candidate: URL, commit, exact path, license, notice, intended transformation. No copying by default. | Baseline fixture and source/rights ledger are reviewable; no user state modified. |
| P1 — v2 content schema | Add a versioned generated schema for modules, DAG nodes, card kinds, question items, projects, variants, source provenance, and method families. Keep authoring data separate from generated JSON, as legacy `share/gen_curriculum.py:27-37,595-619` does. Add validation for unique IDs, prerequisite cycles, all refs, four-choice items, feedback, source/license, and lesson-to-tutor coverage. | Invalid DAG/question/project fixtures fail with actionable errors; v1 loads unchanged. |
| P2 — event state and migration | Implement append-only `events-v2.jsonl` and rebuildable `progress-v2.json`. Preserve `progress.json`, every dated log, and all 46 stable legacy IDs behind `--drill`/`--legacy-*`; do not translate a legacy recipe pass into false v2 module mastery. V2 completion rows remain compatible with streak/cap counting but are ignored by legacy mastery because their IDs are unknown there (`bin/vim-daily-gate:296-313`). Add active-session lock and atomic projection writes. | Rebuild is idempotent; old streak/counts and legacy detail stay readable; two concurrent interactive triggers yield one v2 session; no private art enters Git. |
| P3 — project and preview | Add persistent `strip.txt`/manifest/checkpoints; a strict frame parser; terminal playback at chosen rates; equal-height warning; answer-hidden prompt/transfer/comparison text files. Separate ephemeral instructions from editable project state (legacy `bin/vim-daily-gate:499-546,723-750` combines them). | Two hourly sessions edit the same strip; interruption/restart resumes; wrong edit can restore a checkpoint without losing earlier frames; playback is inspectable. |
| P4 — cards, grading, and quizzes | Route guided edit, independent edit, four-choice, predicted-output, choose-method, and compare-method cards through one session runner. Move v2 questions out of legacy `QUESTIONS` at `bin/vim-daily-gate:390-427`. Grade resulting buffer plus concept/method constraints, not equality to one key sequence. Keep canonical recipe replay as a test oracle and optional hint. | Answers are not visible before checks; alternate valid methods pass; wrong answers have targeted feedback; item-level attempts persist; module check can pass/fail deterministically. |
| P5 — scheduler and tree | Replace lifetime-threshold `unlocked` and failure-biased `pick_drill` (`bin/vim-daily-gate:325-355`) with DAG eligibility, project continuation, and distinct spaced review variants. Add `--tree`, next-card/banner, module completion, badges, and bounded XP. Keep streak as secondary. | Repeating an easy card never unlocks advanced modules; failed static card does not immediately resurface unchanged; due review cannot displace consecutive project sessions; tree advances immediately after check. |
| P6 — content batches | Author M0-M9 in the original animation spine; add M10 proportional SJIS, M11 fixed-width redraw, M12 joint timing, M13 WORD texture timing, M14 S5 palette variants, M15 S7 texture ground, M16 A0 planning, M17 A3 coherence, and M18 A6 full hand-mirrored reverse reuse. Continue remaining command breadth such as marks, joins, case operators, block insert/erase, onion-skin comparison, and the dedicated S1/S4 slope and off-vertical anti-alias drills. Each card cites Neovim help/tutor and art/animation evidence. | Each implemented batch has real-Neovim golden paths, alternate compare paths, changed-art transfer variants, and source-linked reviews. Current totals are 152 cards/190 questions; all 190 use four choices, distinct authored stems, local distractors, and mistake-specific feedback. |
| P7 — release and docs | Run clean and real Neovim suites, module journeys, long-gap scheduler simulation, crash/concurrency tests, and private-state migration against copies. Reconcile `README.md` and stale `share/DESIGN.md` counts/schema (`DESIGN.md:31-37,67-76,198-203`). Roll out opt-in, inspect a complete M0-M2 journey, then change the hourly default. | Every acceptance item in spec §9 is demonstrated; opt-out retains v1; no lost ledger rows; no unsupported completion claim. |

P1/P2 can be developed against fixtures independently, but P3-P5 need their
contracts before any full-hourly switch. P6 content can be authored while P3-P5
are built, provided its schema is frozen. P7 is not satisfied by 152 parseable
JSON records alone: the whole timed journey must be exercised.

## Decisions to resolve at P0/P1

1. **Curriculum source:** default to original cards mapped to installed Neovim
   tutor nodes. If a specific MIT-licensed OpenVim/VIM Master file is worth
   importing, record a pinned commit and keep its notice. Do not import a
   course merely to inflate card count.
2. **Art publication boundary:** preserve existing short, attributed Stone
   Story entries pending the E11 content review; the full ten-frame walk and
   seven-frame pyramid are already reconstructible from separate entries, so
   do not assume “plates not redistributed” resolves the question. Do not
   bundle a new full plate or transcript. Choose an original or user-local
   scaffold for the complete multi-hour strip where publication rights are
   uncertain. The five already-tracked downloads are marked `unverified`; that
   status is not permission. Do not add another local download to distributable
   content unless the user explicitly clears it for repo inclusion.
3. **Session budget:** guided hourly cards aim for the existing short window;
   optional capstone/preview can be launched manually or split across hours.
   No implicit extension of the prompt cap or cooldown.
4. **Method identity:** clarify which cards require demonstrating a particular
   command family versus merely obtaining the valid result. Store both in the
   schema and surface the distinction before editing.
5. **Cross-exercise text:** v2 interprets this as linked `strip.txt`, unseen
   `transfer.txt`, and post-attempt `compare.txt`. If the intended meaning is
   different, revise the format before implementation; the learning contract
   (transfer beyond the same exact art) stays.

## Test matrix to build before release

- Schema: duplicate IDs, dangling refs, DAG cycles, invalid frame metadata,
  missing source/license, wrong quiz answer index, repeated variants.
- Neovim execution: all guided golden recipes, all claimed alternate methods,
  linewise/characterwise/blockwise edge cases, newline/trailing-space behavior,
  real user config and clean config. The legacy suite at
  `share/test_drills.py:58-105` is the seed; `share/test_v2.py` adds v2 graph,
  state, preview, and 84 primary executable-path checks.
- State: fresh user, user with v1 logs, malformed progress projection,
  renamed legacy drill, midnight/daylight-saving changes, duplicate event,
  crash during checkpoint, concurrent shell+launchd trigger, manual forced
  drill, skip, let-through, and interrupted quiz.
- Scheduler: never-tried skill, due review, multiple due reviews, failed
  review, all nodes mastered, curriculum revision, missed week, cap reached,
  cooldown not reached, no art variant available.
- Pedagogy: first-time M0-M2 path, project continuity, concept-before-answer,
  check unlock, exact-repeat suppression, two valid Neovim paths to one edit,
  transfer to different art, preview of declared holds, and enforcement of
  equal frame bounds during subtractive authoring.

## Release review questions

- Can the learner say what their current animation communicates, not merely
  reproduce a target buffer?
- After a popup succeeds, does it name the changed tree node, next project
  step, and review timing without requiring `--status`?
- When a learner is stuck, is the remedy a smaller decision/new variant rather
  than another immediate copy of the same recipe?
- Is the visible project still plain text, editable outside the tutor, and
  recoverable from a checkpoint?
- Do source notices and the private/public art boundary survive install,
  export, and a fresh clone?

If any answer is no, the phase is not complete even if recipe tests pass.
