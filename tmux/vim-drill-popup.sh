#!/usr/bin/env bash
# Offer the daily vim drill in a tmux popup when a client attaches.
#
# This is the second of two triggers (2026-09-14). The other lives in .zshrc and
# fires in a new window/pane. Attaching usually drops you into work already in
# progress, so this one overlays a popup instead of hijacking a pane.
#
# The gate itself decides whether anything is due (daily cap + cooldown), so
# this hook is cheap and safe to fire on every attach.
set -uo pipefail

gate="$HOME/.local/bin/vim-daily-gate"
[ -x "$gate" ] || exit 0

"$gate" --due-quiet || exit 0

# Never change global tmux options or key tables here (VD-31). A popup whose
# lesson process hangs, is killed, or overlaps another launcher would leave
# every normal pane with the changed setting. Copying inside the popup uses
# the tutor's `c` key or the terminal's own Shift-drag selection.
tmux display-popup -e VIM_DAILY_POPUP=1 -E -w 90% -h 85% \
  -T " vim drill · c copies a question · Shift-drag selects · Cmd-V pastes " \
  "$gate --if-due"
