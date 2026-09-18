# vim-daily design notes

Implementation detail and the reasoning behind it. User-facing docs are in
the top-level README. Rewritten 2026-09-18.

## Layout

    ~/.local/bin/vim-daily-gate              the runner (python3, stdlib only)
    ~/.local/bin/vim-drill                   wrapper: bare = --force, else passthrough
    ~/.local/share/vim-daily/curriculum.json  the content: concepts + drills
    ~/.local/share/vim-daily/gen_curriculum.py  regenerates curriculum.json
    ~/.local/share/vim-daily/test_drills.py     acceptance: every recipe vs nvim
    ~/.local/share/vim-daily/legacy/          the bash version this replaced
    ~/.local/state/vim-daily/YYYY-MM-DD.log   completion ledger (streak source)
    ~/.local/state/vim-daily/progress.json    per-drill mastery
    ~/.local/state/vim-daily/keys-<id>.log    last attempt's raw keystrokes

## Triggers

1. `.zshrc` — new interactive shell or tmux pane.
2. `~/.tmux/scripts/vim-drill-popup.sh` — tmux `client-attached` hook.
3. `~/.tmux/scripts/vim-drill-hourly.sh` — launchd `StartInterval 3600`.

1 and 2 are event-driven and can stay silent all day on one long-lived session.
3 is the actual clock. All three defer to the gate, which owns cooldown and cap.

## Why it is data now

The bash version held its drills in a `case` statement, so a drill could only
ever be one line and adding one meant editing the runner. `curriculum.json` is
versioned (`vim-daily/curriculum@1`) and deliberately generic, so an external
curriculum — a Vim Hero lesson tree, a vim-adventures level order, `vimtutor`
chapters — can be imported into the same shape without touching the runner.

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

Two things the decoder must keep doing:

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
    VIM_DAILY_COOLDOWN=3600   seconds between prompts
    VIM_DAILY_MAX_TRIES=3     attempts before the gate lets you through
    VIM_DAILY_SKIP=1          bypass for one shell
    VIM_DAILY_CURRICULUM      path to an alternate curriculum.json

To go back to twice a day: `VIM_DAILY_TARGET=2 VIM_DAILY_COOLDOWN=10800` in
`.zshrc`, and `launchctl unload ~/Library/LaunchAgents/com.vim-daily.hourly.plist`.

## Acceptance

`~/.local/share/vim-daily/test_drills.py` drives every drill through a real nvim, types
exactly the documented recipe, and asserts the buffer reaches the documented
target. 16/16 passed under both `-u NONE` and the real config on 2026-09-18.
A drill whose recipe does not produce its target must not ship.

That test also settled an old suspicion: the 2026-09-15 mangled-line failure was
blamed on mini.pairs, and the blame does not hold. Every drill passes with the
real config loaded. The keystroke table is the diagnostic, not the pair plugin.

## Repo layout vs installed layout

This directory is `share/` in the repo and is symlinked to
`~/.local/share/vim-daily`. `install.sh` links `bin/`, `tmux/` and the launchd
plist into place too, so every path named above is a symlink into the repo.

The practice ledger in `~/.local/state/vim-daily/` is deliberately NOT tracked:
it records when you were at your machine, which does not belong in a public
repository. Losing it resets the streak and nothing else; mastery counts are
rebuilt from the logs, and `progress.json` is rebuilt from them on first run.
