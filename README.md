# practice your neovim and ascii art skills 

Short Neovim and ASCII-animation lessons that interrupt you every 15 minutes, in a
tmux popup, and make you actually use the keys. The default curriculum is a
sixteen-stage main path across twenty project modules: S0-S7 establish still-art
craft, then A0-A7 build animation. Each stage mixes performed edits with
conceptual retrieval and cannot unlock its successor until its required
changed-art review is passed. The original 46 exact-recipe drills remain
available as the legacy practice set.

The ascii art itself is inspired by Standard combo's lecture on ascii art authoring. 
Note: this is for begginers, once I am good enough and feel like it, I'll probably add harder exercises, 
feel free to PR any ones you feel would be useful.

When you get it wrong it shows you what you typed next to what the recipe asked
for, because the keystrokes are recorded.

```
  YOU TYPED                THE RECIPE ASKS FOR
  cw~._.~._                cw~._.~._            ok
                           .                    you skipped this
  <Esc>0                   <Esc>0               ok
  lll                      f.;;                 not this
```

And it keeps a streak.

```
1/12 today  ·  streak 4 days 🔥  ·  best 4  ·  7 drills all time
```

The streak is now secondary to evidence-backed progress:

```
○ S0  Grid and overwrite         0/21 available
· S1  Stroke runs                0/9  locked      requires S0
· A0  Plan and key poses         0/9  locked      requires S7
· P   Proportional Shift_JIS     0/8  locked      optional after S5
next: M0.P0 Spark loop · Vim grammar primer
```

Each module follows the Stone Story authoring order where it applies: establish
the primary pose and extremes, make the middle in-between, test playback, then
polish timing and holds. Later cards teach a second Neovim method for the same
editing intention—such as counted yank/put versus `:t`, or repeated `r` versus a
visual block—and ask when the scaled method is actually safer.

## Why the drills are ASCII art

Because its cool and arguably more fun than having to practice neovim on modfying fizz fuzz foo and hello world strings. Also, the drills will hone your skills in ascii art authoring. Practice is key. Other monospaced text editor is an animation tool, and the operations that
make frame-by-frame art tractable are exactly the vim operations worth owning:
copy a frame, erase one column across it, re-sort frames from authoring order
into playback order, walk one edit down a stack. The tier-3 drills are those
tasks, drawn from the method Gabriel Santos used to animate Stone Story RPG in
a plain text editor.

A drill looks like this. The material is frames 1 and 2 of the Poison Adept
walk cycle, which differ in exactly one row — so the exercise is the real one:
copy the previous frame, then change only the cells that move.

```
=== WHERE THIS SHAPE COMES FROM ========================================
  Stone Story RPG ASCII tutorial page plate 02, frames 1 and 2 of the
  Poison Adept walk. They differ in exactly one row. skill §10: preserve
  the glyph pattern between frames wherever the part has not changed.

=== DO THIS ============================================================
  6yy            yank the frame
  G              jump to the last line
  p              put an identical copy below. That copy is now frame 2.
  3j0            drop to the fourth row of the copy, column zero
  5l r,          move to the accent and replace it with a comma
  l r/           next cell: replace the space with a diagonal
  l x            delete the trailing paren, then :wq

=== MAKE THE LINES UNDER THE MARKER LOOK EXACTLY LIKE THIS ==============
  │      ,
  │   ∞_/(_
  │   |{\\
  │   |-´ )
  │   |/__\
  │    `  ´
  │      ,
  │   ∞_/(_
  │   |{\\
  │   |-,/
  │   |/__\
  │    `  ´

>>>>>>>>>>  edit below this line, nothing above it  <<<<<<<<<<
      ,
   ∞_/(_
   |{\\
   |-´ )
   |/__\
    `  ´
```

## What is in it

- **215 project cards** across twenty project modules and sixteen prerequisite-gated
  main stages: 174 recipe-bearing Neovim edits and 61 conceptual/check surfaces
  (module checks contain both, so those counts overlap).
- **20 method-contrast cards** and **70 changed-art review banks**; every primary
  edit path is
  replayed through Neovim by the v2 suite.
- **395 manually authored paired conceptual items** spanning visual reading,
  command/output prediction, diagnosis, method comparison, transfer reasoning,
  and coherence checks. Every item requires both an animation/authoring reading
  and a Neovim edit-scope or command decision. Choices are shuffled and carry
  answer-specific feedback. Module checks prefer unseen stems, and a wrong
  response does not unlock the next node. Each of the twenty second transfer
  variants owns a separately written question that prints that variant's
  actual ASCII evidence; retry art cannot inherit the first variant's prose.
- Persistent `strip.txt`, changed-art `transfer-*.txt` variants with a separate
  transfer manifest, post-attempt `compare.txt`, versioned project manifests,
  before/after/failed checkpoints, an
  append-only event ledger, and spaced review intervals at 4h, 1d, 3d, 7d,
  and 14d. Each due review pairs a conceptual question with a key-hidden Neovim
  edit on changed art; both must pass.
- A legacy-parity teaching brief for every v2 edit: current module/XP/level/
  streak, explicit `DO THIS`, motion intent, authoring principle, observable failure, honest
  lesson benefit, source, notation, and recovery help. Every edit reveals its
  target. Guided cards also reveal the recipe; independent, transfer,
  comparison, review, and module-check cards show an action hint while keeping
  the exact command sequence hidden until evaluation.
- A held debrief followed by a separate progress page. The debrief replays the
  artifact and actual keys, conceptual choice, five module-check outcomes, or
  both halves of a spaced review as appropriate. Successful module checks play
  the verified strip automatically and retain a playback receipt. Failed
  question/transfer/check routes name the next changed remediation. The progress page owns the complete
  S0-S7/A0-A7 stage tree, optional P branch, current module map, level/XP, badges,
  daily/streak totals, new unlocks, and next lesson.
- A visible skill tree, bounded XP (once per unique card/review stage), and
  evidence-backed badges for first progress, transfer, tween, playable strip,
  and capstone completion. Replaying a solved card cannot farm XP.
- **46 legacy drills**, median **6 keystrokes**, longest 14, retained as a
  regression-tested command practice set.
- The original **46-drill legacy track** still exposes the broader vimtutor
  checklist. V2 reports only runtime-enforced method evidence as verified
  coverage; commands that occur only in a displayed recipe are not counted.
- **49 art excerpts** in `share/art.json`: 44 extracted byte-exact from the
  tutorial plates (ten walk-cycle frames, seven pyramid frames, the four style
  renderings, the line-run and anti-aliasing plates, the dithered sphere, and
  the particle and hand layers from the Sacrificial Pit scene), plus 5 from
  user downloads via `share/intake_art.py` (ant, centipede, cheer, candle,
  cicada). Those five legacy downloads now carry explicit author/license/
  permission/status fields; their redistribution status remains `unverified`,
  so they are not represented as rights-cleared assets.

## Install

```sh
git clone https://github.com/rikiyanai/daily-neovim-ascii-art-tutor ~/Projects/daily-neovim-ascii-art-tutor
~/Projects/daily-neovim-ascii-art-tutor/install.sh
```

Then append `shell/zshrc-snippet.zsh` to `~/.zshrc` and `tmux/tmux-snippet.conf`
to `~/.tmux.conf`. Requires nvim (or vim) and python3; no third-party packages.

Everything is symlinked, so editing a drill in the repo changes the installed
system immediately.

The installer also runs `vim-daily-setup-check`, a read-only inspection of
`${XDG_CONFIG_HOME:-~/.config}/nvim`. It reports whether Hardtime, WhichKey,
lualine, a color theme, and relative line numbers are detectable. Missing
items produce a copyable Lazy.nvim example and official links; the installer
never edits the Neovim config or installs plugins on the learner's behalf.

## Use

```
vim-drill                    run a drill now
vim-drill --card M0.01       run a module's first unfinished card (choose an open branch)
vim-drill --list             all 215 project cards and completion marks
vim-drill --tree             stage/module progress and the next action
vim-drill --status           the tree plus reviews, streak, and totals
vim-drill --project M0       print M0's persistent strip
vim-drill --preview M0 0.2   preview at 0.2 seconds per frame
vim-drill --drill hold-frame run a specific legacy drill
vim-drill --legacy-list      all 46 legacy drills
vim-drill --legacy-status    legacy coverage and per-concept counts
vim-drill --concepts         the seven paradigm chapters, standalone
vim-drill --quiz grammar     multiple-choice + key-order questions (also: modes)
vim-drill --streak           one line
vim-drill --export-progress  rebuildable v2 tree/review progress as JSON
```

V2 state lives under `~/.local/state/vim-daily/`: `events-v2.jsonl` is the
append-only authority, `progress-v2.json` is a rebuildable projection, and each
project has its own directory under `projects/`. The old `progress.json` and
dated completion logs are preserved. V2 passes also write the dated ledger so
the existing streak and daily cap continue to work.

Edit cards save a brief under `sessions/<project>/<card>.txt` and open it in a
read-only split above the project in Neovim. Guided targets and recipes stay
visible; evidence-bearing cards explicitly hide them until the attempt is
graded. The active lower buffer and every motion/write address only the
art-only `strip.txt`.

## The three triggers

1. `.zshrc` — a new interactive shell or tmux pane.
2. tmux `client-attached` hook — a popup when you attach.
3. launchd `StartInterval 900` — the actual clock (every 15 minutes).

1 and 2 are event-driven and can both stay silent all day on one long-lived
session, which is why 3 exists. All three defer to the gate, which owns the
cooldown and the daily cap, so they are cheap to fire.

## Tuning

```sh
VIM_DAILY_TARGET=12       drills per day
VIM_DAILY_COOLDOWN=900    seconds between prompts
VIM_DAILY_MAX_TRIES=3     attempts before it lets you through
VIM_DAILY_SKIP=1          bypass for one shell
VIM_DAILY_CURRICULUM      path to an alternate legacy curriculum.json
VIM_DAILY_CURRICULUM_V2   path to an alternate curriculum-v2.json
VIM_DAILY_CLEAN=1           opt into isolated Neovim with fallback tutor UI
VIM_DAILY_USE_USER_CONFIG=0 same isolated fallback route
```

Lesson buffers use your own Neovim configuration by default. That preserves
your theme, lualine, relative numbers, Hardtime, WhichKey, mappings, and other
normal editor behavior. The tutor disables visible whitespace/indent guides in
its two windows, suppresses automatic indentation only in the art buffer, and
restores line 1 after split-preserving UI changes. It does not replace your
statusline, close plugin windows, or install an alternate key coach. Automated
popup readiness is signaled only after lazy.nvim's `User VeryLazy` event and a
short redraw delay.

`VIM_DAILY_CLEAN=1` (or `VIM_DAILY_USE_USER_CONFIG=0`) is the explicit isolated
fallback. Only that route supplies the tutor-owned statusline, F1 cheat sheet,
and repeated-h/j/k/l coach.

Twice a day instead of hourly: `VIM_DAILY_TARGET=2 VIM_DAILY_COOLDOWN=10800`,
and `launchctl unload ~/Library/LaunchAgents/com.vim-daily.hourly.plist`.

## Curriculum sources and writing lessons

`share/gen_curriculum_v2.py` owns stable module, card, question, project, and
review metadata; it generates `share/curriculum-v2.json`. The course follows
Neovim tutor command coverage but uses original ASCII-animation exercises. It
does not copy VimHero lesson prose or reconstruct complete third-party Stone
Story plates. The detailed evidence, rights boundary, progression contract, and
card catalog are in `share/CURRICULUM_V2_SPEC.md` and
`share/CURRICULUM_V2_CARD_CATALOG.md`.

The [legacy curriculum disposition](share/LEGACY_CURRICULUM_DISPOSITION.md)
maps all 46 stable v1 drill IDs to an explicit `adapted`, `partial`, or
`retained-only` status. It is intentionally separate from the broader v2
module map so a nearby card cannot be mistaken for command parity.

The optional M10 branch turns the aggregate evidence in
`share/sjis_corpus_findings.v1.json`: 435 proportional Shift_JIS combinations,
mirrors, stacks, outline/tone strata, and whitespace exceptions measured by
the glyph viewer into a five-pose puff tween: lobe, arch, hatched impact,
impact hold, and settle. Neovim checks exact transcription; it does **not** claim that
a terminal cell view proves proportional alignment. Shape judgment remains a
Saitamaar 16 px true-advance operation.

Run the complete v2 gate after changes:

```sh
share/gen_curriculum_v2.py
share/test_v2.py
share/test_v2.py --real
share/test_tmux_v2.py --show-capture
VIM_DAILY_TEST_COLUMNS=100 VIM_DAILY_TEST_ROWS=36 share/test_tmux_v2.py
VIM_DAILY_TEST_COLUMNS=80 VIM_DAILY_TEST_ROWS=24 share/test_tmux_v2.py
share/test_tmux_v2_routes.py
VIM_DAILY_TEST_COLUMNS=100 VIM_DAILY_TEST_ROWS=36 share/test_tmux_v2_routes.py
VIM_DAILY_TEST_COLUMNS=80 VIM_DAILY_TEST_ROWS=24 share/test_tmux_v2_routes.py
```

The v2 suite validates the S0-S7/A0-A7 stage chain, optional P branch, 215 cards, 395
complete questions, the complete 46-ID disposition table, one representative
legacy-to-v2 surface-job comparison, persistent start→target continuity,
review state, every one of the 174 primary edit recipes, and both executable
paths on all twenty comparison cards in clean Neovim, plus every changed-art
review bank. It also checks all edit briefs for required teaching sections and answer
leakage. Unequal frame heights block
`--preview` with a repair message instead of rendering a misleading animation.
The tmux test attaches a real client so the installed `client-attached` hook
runs its normal `--due-quiet` → `display-popup` → `--if-due` route at 188×49.
It captures the popup itself, scrolls the read-only brief to prove its lower
legacy-parity sections are visible, verifies the held failed artifact/key
replay, advances to the unchanged skill tree, retries, verifies the held
successful replay, then advances to the updated tree, module count, XP/badges,
daily/streak totals, next lesson, and explicit Enter-to-close hold. A direct
`--force` launch or recipe replay is not accepted as automatic-popup proof.
`test_tmux_v2_routes.py` repeats the installed client-attached popup boundary
for conceptual, independent, compare-method, five-question module-check,
spaced-review, and every module-transfer route. It also drives a deterministic
non-identity answer shuffle. Both headed suites prove the page remains visible
before Enter and disappears afterward. They run at 188×49, 100×36, and 80×24;
the smallest viewport uses a reflowed brief, evidence replay, and compact tree.
The learner's own Neovim chrome remains the default: lualine owns
the live mode, WhichKey and Hardtime remain active, and only clean fallback mode
adds the tutor statusline/F1 UI. Retrieval cards show TARGET plus an action
hint while hiding only the exact keys, and results retain the two-column
keystroke ledger. Revision `.38` gives every card one stage owner and makes
stage advancement depend on both card completion and the stage's required
spaced reviews. P unlocks after S5 but never blocks S6. The clean suite passes
215/215 cards and 174/174 primary recipes. The base headed popup path shows the
new stage rendering at 80x24, 100x36, and 188x49; the full post-M2 route matrix
and real-config suite remain separate acceptance evidence.
The stage mechanism is live, but older S-stage content is still being manually
separated into true still studies versus temporal cards; the gate must not be
read as proof that this content migration is finished.

Recipes that need the extended middle-dot glyph teach Neovim's portable
digraph: type `<C-k>.M` where the recipe shows it. For example,
`r<C-k>.M` replaces the current cell with `·`; directly entering `·` is also a
valid path when it produces the exact target.

## Writing legacy drills

Three data files, none of which the runner is hard-coded against:

    share/concepts.json    the seven paradigm chapters
    share/art.json         the art library, with per-entry provenance
    share/curriculum.json  generated: drills that pair a skill with an art entry

The curriculum spine is **vimtutor's lesson sequence** — it ships with vim and
neovim at `$VIMRUNTIME/tutor/en/`, so the spine is verifiable on your own
machine. Each drill names the node it covers in its `tutor` field. No vimtutor
text is copied; only the sequence is followed, and coverage is measurable.

Three rules, all enforced by `test_drills.py`:

- **SOURCED** — every drill names its art provenance and its vimtutor node, and
  every art-library entry records origin, author, license, permission, and an
  explicit redistribution status. The
  first version of this curriculum invented all sixteen shapes (`x_x_x_`,
  `+---+`, `.:*:.`, `[###]`), and two used glyphs outside the alphabet, one of
  them `#`, which is the transparency character, used as ink.
- **SHORT** — at most 16 keystrokes and 75 seconds, at most 8 starting rows.
- **REAL** — the recipe is driven through an actual nvim and must reach the
  target. Targets are *derived* from the art by the operation being taught,
  never retyped, because a retyped target is one no recipe can reach.

Downloaded art goes through `share/intake_art.py`, which splits a text file
into blank-line-delimited blocks, reports glyph violations and signature rows,
and appends a chosen block to `share/art.json`:

```sh
share/intake_art.py ~/Downloads/ant.txt
VIM_DAILY_ART_JSON=/path/to/private-art.json \
share/intake_art.py ~/Downloads/ant.txt --key cheer --block 5 --drop-last 1 \
  --source "user download ~/Downloads/ant.txt (2026-09-21)" \
  --author "unknown; source carried a tre signature" --license unknown \
  --permission "not documented" --redistribution private-only
```

Rights metadata is mandatory. `--redistribution` must be `cleared`,
`private-only`, or `unverified`; the tool records the status and never converts
an unknown download into an implied permission. Seed a private library by
copying `share/art.json` to the path supplied in `VIM_DAILY_ART_JSON`.
Non-cleared art is refused when the destination is the repository library.
`--strip-prefix TAG` removes a signature tag sitting after the art's indent;
`--drop-last N` drops trailing signature rows. Blocks that fail the glyph
alphabet (digits, `*`, stray prose) are refused — excerpt or skip them. Then
add drills in `gen_curriculum.py` and run the gate suite below.

Re-derive the plate library with `share/extract_art.py /path/to/ascii-tutorial-page`.
Re-extraction replaces only derived plate keys and preserves separately ingested
entries. The source page files themselves are not redistributed here; the short
practice excerpts in `art.json` retain explicit, currently unverified rights metadata.

Edit `share/gen_curriculum.py`, not the JSON — the art is full of backslashes,
quotes and non-ASCII glyphs, and hand-escaping that into JSON is the bug class
that broke a drill on 2026-09-14. Then:

```sh
share/gen_curriculum.py && share/test_drills.py --real
```

`test_drills.py` drives every drill through a real nvim, types exactly the
documented recipe, asserts the buffer reaches the target, and then checks the
glyph alphabet, the provenance fields and the length gates. 46/46 pass under
both a clean config and a full one.

It earns its keep. On the run that expanded the set to 42 it caught nine
defects, including one that mattered: a `:g/^/m0` drill, meant to reverse four
frames, reordered **the entire lesson file** — `:g` is whole-buffer, and the
lesson's own instructions sit above the drill region. It now teaches a
range-scoped `:normal` instead. It also caught `d2w` eating half a run (`w`
stops at punctuation, and line art is all punctuation — `W` is what art work
wants), and `dap` swallowing the instruction text above the marker because the
region was contiguous with it.

Implementation notes, including what the keystroke decoder has to get right, are
in [share/DESIGN.md](share/DESIGN.md).

## Your practice log is not in this repo

The completion ledger lives in `~/.local/state/vim-daily/` and is gitignored. It
is a record of when you were sitting at your machine, which does not belong in a
public repository. Back it up somewhere private if you care about the streak.

## Attribution

The drill material is drawn from the ASCII-art tutorial page for **Stone Story
RPG** by Gabriel Santos, Martian Rex, Inc. — `stonestoryrpg.com/ascii_tutorial.html`.
Short excerpts are used here as practice material; the art is the author's, not
mine, and its redistribution permission remains explicitly unverified. The full
source page/plate files are not redistributed in this repo. The authoring method those excerpts illustrate is summarised, with
per-rule citations, in the `ascii-art-authoring` skill.

## Licence

MIT, for the code. See Attribution above for the drill material.
