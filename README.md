# vim-daily

Short vim drills that interrupt you once an hour, in a tmux popup, and make you
actually type the keys. Sixteen drills across three tiers, each one opening with
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

A drill looks like this:

```
=== DO THIS ============================================================
  3yy            yank three lines: the whole frame
  G              jump to the last line. p puts AFTER the cursor, so this matters.
  2p             put the frame back twice. Two more frames, a 3-frame hold.

=== MAKE THE LINES UNDER THE MARKER LOOK EXACTLY LIKE THIS ==============
  │ _
  │( )
  │ -
  │ _
  │( )
  │ -
  │ _
  │( )
  │ -

>>>>>>>>>>  edit below this line, nothing above it  <<<<<<<<<<
 _
( )
 -
```

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

Drills are data, in `share/curriculum.json`, under a versioned schema
(`vim-daily/curriculum@1`) kept deliberately generic so an external curriculum
can be imported into the same shape without touching the runner.

Edit `share/gen_curriculum.py`, not the JSON — the art targets are full of
backslashes and quotes, and hand-escaping them into JSON is the bug class that
broke a drill on 2026-09-14. Then:

```sh
share/gen_curriculum.py && share/test_drills.py --real
```

`test_drills.py` drives every drill through a real nvim, types exactly the
documented recipe, and asserts the buffer reaches the documented target. A drill
whose recipe does not produce its target must not ship. It caught one on the
first run: `3yy` then `2p` interleaves the frames, because `p` pastes after the
cursor and not after the yanked block.

Implementation notes, including what the keystroke decoder has to get right, are
in [share/DESIGN.md](share/DESIGN.md).

## Your practice log is not in this repo

The completion ledger lives in `~/.local/state/vim-daily/` and is gitignored. It
is a record of when you were sitting at your machine, which does not belong in a
public repository. Back it up somewhere private if you care about the streak.

## Licence

MIT.
