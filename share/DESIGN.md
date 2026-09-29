# vim-daily design notes

Implementation detail and the reasoning behind it. User-facing docs are in
the top-level README. Updated 2026-09-27 for curriculum v2.

## Layout

    ~/.local/bin/vim-daily-gate              the runner (python3, stdlib only)
    ~/.local/bin/vim-drill                   wrapper: bare = --force, else passthrough
    ~/.local/share/vim-daily/curriculum.json  the content: concepts + drills
    ~/.local/share/vim-daily/gen_curriculum.py  regenerates curriculum.json
    ~/.local/share/vim-daily/test_drills.py     acceptance: every recipe vs nvim
    ~/.local/share/vim-daily/curriculum-v2.json generated modules/cards/questions
    ~/.local/share/vim-daily/gen_curriculum_v2.py v2 content owner + validator
    ~/.local/share/vim-daily/v2_runtime.py        tree/project/review runtime
    ~/.local/share/vim-daily/test_v2.py           graph/state + primary/transfer/compare paths
    ~/.local/share/vim-daily/legacy/          the bash version this replaced
    ~/.local/state/vim-daily/YYYY-MM-DD.log   completion ledger (streak source)
    ~/.local/state/vim-daily/progress.json    per-drill mastery
    ~/.local/state/vim-daily/keys-<id>.log    last attempt's raw keystrokes
    ~/.local/state/vim-daily/events-v2.jsonl  append-only v2 authority
    ~/.local/state/vim-daily/progress-v2.json rebuildable v2 projection
    ~/.local/state/vim-daily/projects/        strips, transfers, manifests, checkpoints

## V2 architecture

The default hourly route is `vim-daily/curriculum@4`: twenty project modules
scheduled through the strict S0-S7 still-art path and then A0-A7 animation path.
P is an optional proportional branch unlocked by S5 and is not a prerequisite
for S6. Cards belong to exactly one progression stage even when a project module
stores work used at more than one point in the journey. The item
bank includes 370 separately authored visual readings, command/output predictions,
diagnoses, method comparisons, transfer decisions, and coherence checks. Every
item has four paired animation-and-Neovim choices with mistake-specific feedback. A module
contains guided edits, answer-hidden concepts, an independent edit, a
method-contrast card, a separate transfer artifact, diagnosis, and a mixed
module check. A stage unlocks only after every owned card and every required
changed-art review reaches review stage 1. Project/module state is a ledger view;
it does not override stage locks.

`events-v2.jsonl` is authoritative. `progress-v2.json` is rewritten atomically
from those events and can be deleted/rebuilt without losing evidence. A card
pass records its curriculum revision, question/artifact identity, and next due
review. A due review requires both a paired conceptual retrieval and an exact
Neovim edit on a changed transfer-art variant; neither half alone awards its
stage. The scheduler serves at most one due changed-variant review after every
four successful sessions, never displacing a ready module check. After all
project cards are complete, due reviews remain runnable without that cadence.
Explicit `--force` means the next project card, not a review. Review stages are
capped at the 4h, 1d, 3d, 7d, and 14d intervals.
The projection awards 10 XP once per unique card and 3 XP once per unique
review key/stage. Badges derive from stage evidence milestones, so duplicate
ledger events cannot farm either XP or unlocks.

Each project card edits the same `strip.txt` as the preceding project card.
M6 and M7 deliberately share `pyramid-build/strip.txt` across the module
boundary. Transfer cards rotate changed-art variants after a failed session and
use `transfer-<card>.txt` plus `transfer-manifest.json`, so they cannot replace
the playable strip's `manifest.json`; compare cards write post-attempt
`compare.txt`. A successful edit writes a SHA-256-bearing manifest and
before/after checkpoints. A failed edit writes a numbered snapshot and restores
the working artifact immediately. Preview reads manifest-owned frame slices,
marks holds with their declared reason, and rejects unequal frame heights.
Every successful module-check artifact automatically plays in manifest order
before the held debrief, which retains a `PLAYBACK VERIFIED` receipt.

The upper Neovim split is a scrollable teaching surface, not a terse launch
banner. It preserves the legacy lesson jobs (`WHY`, concrete benefit, source,
recipe, retained keys, notation, and stuck/quit guidance) and adds the current
module count, XP, daily count, and streak before the attempt. The module record
owns the motion intent, authoring principle, observable defect, local method,
scaling method, and source reference. A card owns its concrete benefit and
recipe. Guided cards reveal target/recipe. Independent, transfer, comparison,
and module-check cards replace exact commands with an explicit retrieval
boundary until evaluation. Both the edit and conceptual routes use the same
teaching contract.

Each comparison card owns two named `{label, keys, why}` methods. Both commands
are executed from the same start buffer and must reach the same target in the
real-Neovim suite. Generic module-level claims are not accepted as alternatives.
The runtime reveals them only after a verified artifact. It records the
demonstrated method family (or `other-valid-exact-target`); an exact file with no
captured edit keys cannot earn comparison credit.

Module checks honor their declared ten-item bank and select the five least-seen
stems first. Their artifact prompt remains answer-hidden. A mastery event binds
the final checkpoint hash to the preceding unseen-transfer artifact/hash.
Animation decisions such as extremes, midpoint tween, hold reason, contact,
pivot, and timing live in structured card/manifest metadata.

The original `curriculum.json`/`progress.json` path is preserved as legacy.
`--drill` and `--legacy-*` still enter it, and v2 completions add compatible
dated-log rows so streak and daily-cap history continue without granting false
legacy mastery.

## Triggers

1. `.zshrc` — new interactive shell or tmux pane.
2. `~/.tmux/scripts/vim-drill-popup.sh` — tmux `client-attached` hook.
3. `~/.tmux/scripts/vim-drill-hourly.sh` — launchd `StartInterval 3600`.

1 and 2 are event-driven and can stay silent all day on one long-lived session.
3 is the actual clock. All three defer to the gate, which owns cooldown and cap.

## Why it is data now

The bash version held its drills in a `case` statement, so a drill could only
ever be one line and adding one meant editing the runner. Legacy
`curriculum.json` is now `vim-daily/curriculum@3`. V2 content is separately
generated as `vim-daily/curriculum@4`; importing outside curricula requires an
exact-file license/provenance review rather than copying course prose by default.

### Drill schema

    id        stable key, used in the log and in progress.json
    title     short name shown in the header
    skill     the one named thing the drill teaches
    concept   key into `concepts`; supplies the paradigm-level WHY text
    tier      1..3; unlocked by lifetime completions (see `tiers`)
    seconds   rough cost, for pacing
    kind      "line" (one line, legacy ART: prefix) or "block" (several lines)
    start     the buffer lines the drill begins with
    target    the buffer lines that count as passing
    cursor    normal-mode command run after jumping to the first editable line
    recipe    [[keys, explanation], ...] — printed in the buffer
    expected  the recipe as one key string, for the typed-vs-recipe table
    keys      related keys worth keeping
    buys      one line: what this skill actually buys you

### Concept schema

    title     chapter heading
    paradigm  prose. Broad, memory-level framing first, mechanics second.

Seven chapters: modes, grammar, repeat, motion-precision, text-objects,
lines-and-blocks, registers-and-ranges. Read them with `vim-daily-gate --concepts`.

Edit drills in `gen_curriculum.py`, not in `curriculum.json`. The art targets
are full of backslashes and quotes, and hand-escaping them into JSON is exactly
the bug class that broke drill 2 on 2026-09-14. Regenerate, then re-run
`test_drills.py --real`.

## Data layout

    concepts.json    seven paradigm chapters (prose)
    art.json         49 art excerpts, each with provenance
    curriculum.json  GENERATED legacy set: 46 drills
    curriculum-v2.json GENERATED project course: 20 modules / 210 cards / 370 questions

`extract_art.py` re-derives plate entries in art.json and merges them with
separately ingested entries instead of replacing the whole library. User
downloads require structured origin, author, license, permission, and
redistribution status. Unknown rights remain explicitly `unverified`; source
page files are not redistributed, while art.json holds short practice excerpts.

The spine is vimtutor's lesson sequence (`$VIMRUNTIME/tutor/en/`), which ships
with the editor and is therefore verifiable rather than asserted. Each drill's
`tutor` field names the node it covers: 24 distinct nodes across 46 legacy drills.

## Targets are derived, never retyped

`gen_curriculum.py` builds each target by applying the taught operation to the
art (`drop(rows, i)`, `dup(rows, i)`, `rows * 3`). Retyping a target by hand
produces a target no recipe can reach, and the failure looks like a broken
recipe rather than a broken target.

## The three gates

| gate | rule |
|---|---|
| SOURCED | `source` names a plate or numbered skill rule; `tutor` names a lesson node; every art entry has structured rights/status metadata |
| SHORT | <= 16 keystrokes, <= 75 estimated seconds, <= 8 starting rows |
| REAL | the recipe is driven through a real nvim and must reach the target |

Current distribution: median 6 keystrokes, max 14; median 32s, max 56s.

## What the gates caught

Expanding 17 -> 42 drills, the harness rejected nine. Three were worth the whole
apparatus:

- **`:g/^/m0` reordered the entire lesson file.** The drill meant to reverse four
  pyramid frames. `:g` is whole-buffer, and the lesson's instructions sit above
  the drill region, so it moved those too. Replaced with a range-scoped
  `:normal`. A drill that damages its own lesson file is the worst possible
  failure mode here, and only an executed run could have found it.
- **`d2w` ate half a run.** `w` stops at every punctuation mark and line art is
  entirely punctuation, so `_.-´` is four words to `w` and one to `W`. The drill
  now teaches that distinction on material where it actually bites.
- **`dap` swallowed the instructions.** The drill region is contiguous with the
  marker line above it, so the first paragraph extended upward into the lesson
  text. The drill now operates on the second, blank-line-bounded block.

## The sourcing rule

Added 2026-09-18 after an audit of schema v1. Every drill carries a `source`
field naming where its shape comes from: a plate from the Stone Story tutorial
page, or a numbered rule in the ascii-art-authoring skill. The lesson prints it.

v1 failed this completely. All sixteen drills were invented fragments, and the
audit found three distinct problems:

| problem | drills | detail |
|---|---|---|
| unsourced | 16 of 16 | no drill's shape came from anywhere |
| glyph outside the alphabet | `subtractive erase` | `*` is in no row of the alphabet |
| transparency char used as ink | `playback order` | `#` is the transparency glyph (skill §7.6) |
| alphanumeric scatter | `shadow pattern`, `ringed frames`, `spine joint` | skill §4.3 rules 3-4: one alphanumeric, placed where you want the reader to look |

Two things v1 got right and v2 keeps: `+` and `=` ARE in the basic alphabet row,
so `+---+` was legal, just unsourced; and `'` is a legal glyph, it is simply not
the same glyph as `´`.

`test_drills.py` now enforces both gates: a drill with no `source`, or with a
glyph outside `BASIC | EXTENDED | ALNUM | BOXDRAW | PLATE_OBS`, fails the suite.

`PLATE_OBS` holds two glyphs the author demonstrably typed that the skill's
alphabet table does not list: `∞` (the Poison Adept's staff) and `¯` U+00AF,
which he used where the alphabet specifies `‾` U+203E. The plate is the evidence
of what was actually typed, so the validator admits both.

## Typing versus operating

Extended glyphs (`´ ‾ ¡ ·`) are never typed in a drill. They are not on a US
keyboard, and demanding Option-e mid-drill would be pointless. Drills either
use ASCII-only runs, or they OPERATE on art that already contains the glyph —
yank it, copy the row, move the block, delete the column. The `symbol table`
drill teaches the real workaround: keep a strip of the alphabet in the file and
yank from it, which is the authoring method's own rule (skill §1.7).

## Vendorable pieces

Three sections of the runner are self-contained and can be lifted out:

- **keys** — `decode_keylog`, `tokenize`, `strip_save_tail`, `keystroke_table`.
  Takes nvim's `-w` scriptout, returns readable key tokens, and diffs them
  against a recipe with `difflib`. No dependency on the rest of the file.
- **progress** — `day_counts`, `streaks`, `load_progress`, `pick_drill`.
  Streak is derived from the log filenames, so it survives losing progress.json.
  `pick_drill` is weakest-skill-first (fewest passes, then least recent), which
  replaced the old `day-of-year % 7` that served the same two drills every day.
- **lesson** — `write_lesson`, `read_region`, `matches`, `show_diff`.

`--export-progress` emits `vim-daily/export@1` JSON for anything downstream.

## Keystroke recording

`nvim -w <file>` appends every typed key to a scriptout. Cost is nil. On a
failed attempt the gate decodes it and prints what you typed beside what the
recipe asked for, aligned with `difflib.SequenceMatcher`.

Keys used only to enter, scroll, and leave the read-only teaching split are
removed from the v2 edit comparison. Reading the lesson is not an editing
error.

The v2 post-attempt surface is deliberately paged. Feedback page one shows the
artifact before/after on success or wanted/yours plus the first differing
column on failure. It also shows the actual-versus-taught keys, `WHY`, concrete
benefit, `DO / AVOID`, and source. An explicit Enter replaces that page with a
progress page containing the complete S0-S7/A0-A7 stage tree, optional P branch,
module ledger, reviews, XP, badges,
streak, best streak, all-time completions, next card, and daily count. A second
Enter closes a successful popup; failed edits instead offer checkpoint restore
and retry from the progress page. Concept cards retain the chosen/correct answer
and explanation. Module checks retain all five outcomes through the artifact
subpart. Spaced reviews use the same held feedback and progress pages instead of
printing a transient line; their page includes both the concept replay and the
changed-art artifact/key replay. Failed Q/T/K routes append a named remediation
with the exact changed stem, transfer variant, or checkpoint recovery due next.

At 80×24, the same contract is reflowed: the initial brief keeps `DO THIS`, an
action hint, and the target above the editable art while withholding only the
exact keys on retrieval cards. The default editing surface is the learner's
own Neovim configuration: their theme, lualine mode indicator, relative
numbers, Hardtime, WhichKey, and mappings remain owned by that config. The
tutor disables only visible whitespace/indent guides in its windows and
suppresses automatic indentation only in the art buffer, then restores line 1
after split-preserving UI changes. It waits for lazy.nvim's
`User VeryLazy` event before signaling headed-test readiness. It does not reset
the statusline or close plugin windows. `VIM_DAILY_CLEAN=1` is the explicit
fallback route; only that isolated route supplies the tutor statusline, F1
cheat sheet, and repeated-motion coach. The compact feedback page retains a
literal `YOU TYPED │ THE RECIPE ASKS FOR` row rather than collapsing it to an
actual/taught sentence; the progress page compresses the stage path into compact
rows. Larger viewports may also show the project/module ledger.

Two things the decoder must keep doing:

- Decode UTF-8 multibyte glyphs as ONE key. The art uses `´ ‾ ¡ ·`, so `r´` logs
  `72 C2 B4` and must read as `r´`, not as `r` plus two replacement characters.
  Verified live 2026-09-18: `f/r´:wq<CR>` round-trips exactly. `0x80` is
  K_SPECIAL and is never a UTF-8 lead byte, so the two cases cannot collide.
- Drop `0x80` K_SPECIAL triples. nvim injects them itself during `f`, `r` and
  `.` handling — verified 2026-09-18: `f.;` logs `66 2e 80 fd 35 3b`. They are
  not keys a human pressed.
- Strip the trailing save command from both sides before diffing, so `ZZ`
  against `:wq` is never reported as a mistake.
- Decode `0x80 0xfc <mask>` as a MODIFIER applied to the next key, not as noise.
  nvim folds Esc-immediately-followed-by-a-key into Meta, so a fast `<Esc>0`
  arrives as `80 fc 08 30` = `<M-0>` (verified live 2026-09-18). Dropping the
  prefix printed a bare `0` and made a real failure look inexplicable, which is
  the exact situation the table exists to prevent.

## Tuning

    VIM_DAILY_TARGET=12       drills per day
    VIM_DAILY_COOLDOWN=900    seconds between prompts
    VIM_DAILY_MAX_TRIES=3     attempts before the gate lets you through
    VIM_DAILY_SKIP=1          bypass for one shell
    VIM_DAILY_CURRICULUM      path to an alternate legacy curriculum.json
    VIM_DAILY_CURRICULUM_V2   path to an alternate curriculum-v2.json

To go back to twice a day: `VIM_DAILY_TARGET=2 VIM_DAILY_COOLDOWN=10800` in
`.zshrc`, and `launchctl unload ~/Library/LaunchAgents/com.vim-daily.hourly.plist`.

## Acceptance

`~/.local/share/vim-daily/test_drills.py` drives every legacy drill through a
real nvim, types exactly the documented recipe, and asserts the buffer reaches
the documented target. All 46/46 passed under both `-u NONE` and the real config
on 2026-09-27. A drill whose recipe does not produce its target must not ship.

`test_v2.py` validates the strict stage graph, exact 210/370 counts, matching
choice/feedback completeness, minimum visual substance, generated-artifact equality,
glyph vocabulary, project continuity, review cadence,
frame-boundary preview behavior, every executable recipe, runtime method contracts,
nonduplicated loop seams for M4/M5, the attached bottom-up M6 build, and the complete
46-ID disposition table in `LEGACY_CURRICULUM_DISPOSITION.md`. A separate
representative surface test checks that the v2 brief preserves the legacy
lesson's teaching jobs and their content; it does not claim command parity from
matching headings. The suite renders every edit brief to enforce the
guided/hidden boundary and executes all 169 primary recipe-bearing paths.
Revision `.35` passes 169/169 primary paths in clean Neovim; headed real-config
acceptance for the new stage rendering is a separate gate. Its automatic failure/retry/debrief
test additionally enters Visual mode, toggles F1 help, and triggers the
repeated-motion coach before checking the compact two-column ledger.

`test_tmux_v2.py` validates the automatic presentation boundary. A real client
attachment fires the installed hook, which must pass the silent due check and
render `--if-due` inside `display-popup`. An outer 188×49 tmux terminal captures
that popup. The test captures and scrolls the teaching brief, captures an
intentional failed artifact/key replay, advances to unchanged progression,
retries inside the same popup, captures the successful artifact/key replay,
advances to the updated stage tree, module count, XP/badges,
daily/streak totals and next lesson, then proves the progress page remains open
until Enter. Direct `--force` execution is not evidence for this boundary.

`test_tmux_v2_routes.py` exercises the other presentation routes through that
same installed client-attached hook and real `display-popup`: conceptual check,
independent retrieval, method comparison, five-question module check plus
artifact, and spaced review. It checks held route-specific evidence and the
level/tree/card-map/streak page at 188×49.
The same suite runs with `VIM_DAILY_TEST_COLUMNS=100` and
`VIM_DAILY_TEST_ROWS=36`. Below 38 terminal rows, feedback collapses duplicate
WHY/benefit prose already retained in the pre-attempt brief but preserves the
two-column keystroke ledger. An all-correct five-question check is summarized in
one line so the completion heading remains on screen. Artifact evidence,
module-check score, playback, do/avoid, source, completion heading, and
progression remain mandatory.

Executable recipes enter the extended middle dot through Neovim's `.M`
digraph (`<C-k>.M`) instead of assuming an operating-system Unicode input
method. The target remains `·`, so direct Unicode input remains valid.

That test also settled an old suspicion: the 2026-09-15 mangled-line failure was
blamed on mini.pairs, and the blame does not hold. Every drill passes with the
real config loaded. The keystroke table is the diagnostic, not the pair plugin.

## Repo layout vs installed layout

This directory is `share/` in the repo and is symlinked to
`~/.local/share/vim-daily`. `install.sh` links `bin/`, `tmux/` and the launchd
plist into place too, so every path named above is a symlink into the repo.
It then runs `bin/vim-daily-setup-check`, which reads the user's Neovim config
and reports found/missing/verify states for Hardtime, WhichKey, lualine, a
theme, and relative numbers. The check prints recommendations and source links
only; it never writes to the user's config or invokes a plugin manager.

The practice ledger in `~/.local/state/vim-daily/` is deliberately NOT tracked:
it records when you were at your machine, which does not belong in a public
repository. Legacy mastery can seed from dated logs. V2 mastery rebuilds from
`events-v2.jsonl`; `progress-v2.json` is only its disposable projection.
