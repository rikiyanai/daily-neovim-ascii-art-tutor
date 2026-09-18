#!/usr/bin/env bash
# Prefix+V: run a vim drill on demand in a popup, ignoring cap and cooldown.
set -uo pipefail
gate="$HOME/.local/bin/vim-daily-gate"
[ -x "$gate" ] || exit 0
tmux display-popup -e VIM_DAILY_POPUP=1 -E -w 90% -h 85% -T " vim drill - :q! then n to close " "$gate --force"
