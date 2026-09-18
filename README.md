# vim-daily

Short vim drills that interrupt you once an hour, in a tmux popup, and make you
actually type the keys. Forty-two drills across three tiers, each one opening with
a paradigm-level explanation of *why* the mechanic exists rather than a list of
keystrokes to memorise.

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

## Why the drills are ASCII art

Because a monospaced text editor is an animation tool, and the operations that
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

- **42 drills**, median **6 keystrokes**, longest 14. 36 of them estimate under
  45 seconds. They fire hourly, so a drill you dread is a drill you skip.
- **24 vimtutor lesson nodes** covered, from `1.1 MOVING THE CURSOR` through
  registers, marks and ranges.
- **44 art excerpts** in `share/art.json`, extracted byte-exact from the tutorial
  plates: ten walk-cycle frames, seven pyramid frames, the four style renderings,
  the line-run and anti-aliasing plates, the dithered sphere, and the particle
  and hand layers from the Sacrificial Pit scene.

## Install

```sh
git clone https://github.com/rikiyanai/vim-daily ~/Projects/vim-daily
~/Projects/vim-daily/install.sh
```

Then append `shell/zshrc-snippet.zsh` to `~/.zshrc` and `tmux/tmux-snippet.conf`
to `~/.tmux.conf`. Requires nvim (or vim) and python3; no third-party packages.

Everything is symlinked, so editing a drill in the repo changes the installed
system immediately.

## Use

```
vim-drill                    run a drill now
vim-drill --drill hold-frames  run a specific one
vim-drill --list             all 16 drills, tier, and how many times you passed
vim-drill --status           streak, cadence, per-skill mastery, last 14 days
vim-drill --concepts         the seven paradigm chapters, standalone
vim-drill --streak           one line
vim-drill --export-progress  JSON
```

## The three triggers

1. `.zshrc` — a new interactive shell or tmux pane.
2. tmux `client-attached` hook — a popup when you attach.
3. launchd `StartInterval 3600` — the actual clock.

1 and 2 are event-driven and can both stay silent all day on one long-lived
session, which is why 3 exists. All three defer to the gate, which owns the
cooldown and the daily cap, so they are cheap to fire.

## Tuning

```sh
VIM_DAILY_TARGET=12       drills per day
VIM_DAILY_COOLDOWN=3600   seconds between prompts
VIM_DAILY_MAX_TRIES=3     attempts before it lets you through
VIM_DAILY_SKIP=1          bypass for one shell
VIM_DAILY_CURRICULUM      path to an alternate curriculum.json
```

Twice a day instead of hourly: `VIM_DAILY_TARGET=2 VIM_DAILY_COOLDOWN=10800`,
and `launchctl unload ~/Library/LaunchAgents/com.vim-daily.hourly.plist`.

## Writing your own drills

Three data files, none of which the runner is hard-coded against:

    share/concepts.json    the seven paradigm chapters
    share/art.json         the art library, with per-entry provenance
    share/curriculum.json  generated: drills that pair a skill with an art entry

The curriculum spine is **vimtutor's lesson sequence** — it ships with vim and
neovim at `$VIMRUNTIME/tutor/en/`, so the spine is verifiable on your own
machine. Each drill names the node it covers in its `tutor` field. No vimtutor
text is copied; only the sequence is followed, and coverage is measurable.

Three rules, all enforced by `test_drills.py`:

- **SOURCED** — every drill names its art provenance and its vimtutor node. The
  first version of this curriculum invented all sixteen shapes (`x_x_x_`,
  `+---+`, `.:*:.`, `[###]`), and two used glyphs outside the alphabet, one of
  them `#`, which is the transparency character, used as ink.
- **SHORT** — at most 16 keystrokes and 75 seconds, at most 8 starting rows.
- **REAL** — the recipe is driven through an actual nvim and must reach the
  target. Targets are *derived* from the art by the operation being taught,
  never retyped, because a retyped target is one no recipe can reach.

Re-derive the art library with `share/extract_art.py /path/to/ascii-tutorial-page`.
The plates themselves are not redistributed here.

Edit `share/gen_curriculum.py`, not the JSON — the art is full of backslashes,
quotes and non-ASCII glyphs, and hand-escaping that into JSON is the bug class
that broke a drill on 2026-09-14. Then:

```sh
share/gen_curriculum.py && share/test_drills.py --real
```

`test_drills.py` drives every drill through a real nvim, types exactly the
documented recipe, asserts the buffer reaches the target, and then checks the
glyph alphabet, the provenance fields and the length gates. 42/42 pass under
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
Excerpts are at most six rows and are used here as practice material; the art is
the author's, not mine. The tutorial plates themselves are not redistributed in
this repo. The authoring method those excerpts illustrate is summarised, with
per-rule citations, in the `ascii-art-authoring` skill.

## Licence

MIT, for the code. See Attribution above for the drill material.
