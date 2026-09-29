#!/usr/bin/env bash
# Hourly vim drill, trigger 3 of 3 (added 2026-09-18).
#
# The other two triggers are event-driven: .zshrc fires on a new interactive
# shell/pane, and vim-drill-popup.sh fires on tmux client-attached. Neither is
# a clock, so on a machine that stays attached to one session all day they can
# both go quiet for hours. This one is launchd-driven and actually hourly.
#
# The gate still owns the decision (cooldown + daily cap), so this is cheap and
# safe to fire every hour. It does nothing when no tmux client is attached.
set -uo pipefail
export PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin"

gate="$HOME/.local/bin/vim-daily-gate"
[ -x "$gate" ] || exit 0
"$gate" --due-quiet || exit 0

command -v tmux >/dev/null 2>&1 || exit 0
session="$(tmux list-clients -F '#{client_session}' 2>/dev/null | head -1)"
[ -n "$session" ] || exit 0

mouse_before="$(tmux show-options -gv mouse 2>/dev/null || printf 'off')"
restore_mouse() {
  tmux set-option -g mouse "$mouse_before" >/dev/null 2>&1 || true
}
trap restore_mouse EXIT
tmux set-option -g mouse off
if command -v pbcopy >/dev/null 2>&1; then
  tmux set-option -g set-clipboard on
  tmux bind-key -T copy-mode-vi y send-keys -X copy-pipe-and-cancel 'pbcopy'
  tmux bind-key -T copy-mode-vi Enter send-keys -X copy-pipe-and-cancel 'pbcopy'
  tmux bind-key -T copy-mode-vi MouseDragEnd1Pane send-keys -X copy-pipe-and-cancel 'pbcopy'
fi

tmux display-popup -e VIM_DAILY_POPUP=1 -t "$session" -E -w 90% -h 85% \
  -T " vim drill · drag selects · Cmd-C copies · Cmd-V pastes " \
  "$gate --if-due"
