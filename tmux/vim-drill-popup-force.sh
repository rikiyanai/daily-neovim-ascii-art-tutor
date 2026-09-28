#!/usr/bin/env bash
# Prefix+V: run a vim drill on demand in a popup, ignoring cap and cooldown.
set -uo pipefail
gate="$HOME/.local/bin/vim-daily-gate"
[ -x "$gate" ] || exit 0
if command -v pbcopy >/dev/null 2>&1; then
  tmux set-option -g mouse on
  tmux set-option -g set-clipboard on
  tmux bind-key -T copy-mode-vi y send-keys -X copy-pipe-and-cancel 'pbcopy'
  tmux bind-key -T copy-mode-vi Enter send-keys -X copy-pipe-and-cancel 'pbcopy'
  tmux bind-key -T copy-mode-vi MouseDragEnd1Pane send-keys -X copy-pipe-and-cancel 'pbcopy'
fi
tmux display-popup -e VIM_DAILY_POPUP=1 -E -w 90% -h 85% -T " vim drill · drag copies · Cmd-V pastes · :wq submits " "$gate --force"
