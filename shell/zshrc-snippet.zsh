# Append to ~/.zshrc. Trigger 1 of 3: fires in a new interactive shell,
# which includes every new tmux window or pane.

# Daily vim drill, trigger 1 of 3: fires in a new interactive shell, which means
# a new tmux window or pane as well as a login shell.
#
# The `-z "$TMUX"` condition was removed 2026-09-14. With the tmux auto-attach
# below and a machine that is rarely rebooted, that condition meant the drill
# fired roughly once per reboot -- the state dir held zero completions.
#
# Frequency is the script's job, not this block's:
#   VIM_DAILY_TARGET=12       drills per day (default 12, was 2 until 2026-09-18)
#   VIM_DAILY_COOLDOWN=3600   seconds between prompts (default hourly, was 3h)
#   VIM_DAILY_SKIP=1          bypass for one shell
# Trigger 2 is a tmux popup on client-attached; see ~/.tmux/scripts/vim-drill-popup.sh.
# Trigger 3 is launchd every 3600s; see ~/.tmux/scripts/vim-drill-hourly.sh and
# ~/Library/LaunchAgents/com.vim-daily.hourly.plist. Triggers 1 and 2 are
# event-driven and can stay silent all day on a long-lived session; 3 is the clock.
# On demand: `vim-drill`, `vim-drill --list`, `vim-daily-gate --drill 4`, or Prefix+V.
# Progress: `vim-daily-gate --status` (streak, mastery), `--concepts` (the why),
# `--streak` (one line), `--export-progress` (JSON).
if [[ -o interactive && -z "${VIM_DAILY_SKIP:-}" && -z "${VIM_DAILY_ACTIVE:-}" && -z "${NVIM:-}" && "$TERM" != "dumb" && -t 0 && -t 1 ]]; then
  if [[ -x "$HOME/.local/bin/vim-daily-gate" ]]; then
    "$HOME/.local/bin/vim-daily-gate" --if-due || true
  fi
fi
