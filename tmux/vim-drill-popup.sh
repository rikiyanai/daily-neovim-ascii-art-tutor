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

mouse_before="$(tmux show-options -gv mouse 2>/dev/null || printf 'off')"
restore_mouse() {
  tmux set-option -g mouse "$mouse_before" >/dev/null 2>&1 || true
}
trap restore_mouse EXIT
tmux set-option -g mouse off

if command -v pbcopy >/dev/null 2>&1; then
  # Let Terminal/iTerm receive the drag so native selection and Cmd-C work.
  # The original tmux mouse preference is restored when the popup closes.
  tmux set-option -g set-clipboard on
  tmux bind-key -T copy-mode-vi y send-keys -X copy-pipe-and-cancel 'pbcopy'
  tmux bind-key -T copy-mode-vi Enter send-keys -X copy-pipe-and-cancel 'pbcopy'
  tmux bind-key -T copy-mode-vi MouseDragEnd1Pane send-keys -X copy-pipe-and-cancel 'pbcopy'
fi

tmux display-popup -e VIM_DAILY_POPUP=1 -E -w 90% -h 85% \
  -T " vim drill · drag selects · Cmd-C copies · Cmd-V pastes " \
  "$gate --if-due"
