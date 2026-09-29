#!/usr/bin/env bash
# Prefix+V: run a vim drill on demand in a popup, ignoring cap and cooldown.
set -uo pipefail
gate="$HOME/.local/bin/vim-daily-gate"
[ -x "$gate" ] || exit 0
# Never change global tmux options or key tables here (VD-31). A popup whose
# lesson process hangs, is killed, or overlaps another launcher would leave
# every normal pane with the changed setting. Copying inside the popup uses
# the tutor's `c` key or the terminal's own Shift-drag selection.
tmux display-popup -e VIM_DAILY_POPUP=1 -E -w 90% -h 85% -T " vim drill · c copies a question · Shift-drag selects · Cmd-V pastes " "$gate --force"
