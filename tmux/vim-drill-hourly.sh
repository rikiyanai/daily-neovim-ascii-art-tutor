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

command -v tmux >/dev/null 2>&1 || exit 0
session="$(tmux list-clients -F '#{client_session}' 2>/dev/null | head -1)"
[ -n "$session" ] || exit 0

# See vim-drill-popup.sh: serialize ownership and heal a killed prior owner
# before the due check, so an orphaned override cannot persist on quiet hours.
owner="$(tmux show-options -qv -t "$session" @vim_daily_mouse_owner 2>/dev/null)"
if [ -n "$owner" ]; then
  case "$owner" in
    *[!0-9]*|'') owner_command='' ;;
    *) owner_command="$(ps -p "$owner" -o command= 2>/dev/null)" ;;
  esac
  case "$owner_command" in
    *vim-drill-popup.sh*|*vim-drill-popup-force.sh*|*vim-drill-hourly.sh*) exit 0 ;;
  esac
  stale_base="$(tmux show-options -qv -t "$session" @vim_daily_mouse_base 2>/dev/null)"
  if [ "$stale_base" = inherit ]; then
    tmux set-option -qu -t "$session" mouse
  elif [ "${stale_base#local:}" != "$stale_base" ]; then
    tmux set-option -q -t "$session" mouse "${stale_base#local:}"
  fi
  tmux set-option -qu -t "$session" @vim_daily_mouse_owner
  tmux set-option -qu -t "$session" @vim_daily_mouse_base
fi

"$gate" --due-quiet || exit 0

mouse_line="$(tmux show-options -q -t "$session" mouse 2>/dev/null)"
restore_mouse() {
  current_owner="$(tmux show-options -qv -t "$session" @vim_daily_mouse_owner 2>/dev/null)"
  [ "$current_owner" = "$$" ] || return 0
  if [ -n "$mouse_line" ]; then
    tmux set-option -q -t "$session" mouse "${mouse_line#mouse }"
  else
    tmux set-option -qu -t "$session" mouse
  fi
  tmux set-option -qu -t "$session" @vim_daily_mouse_owner
  tmux set-option -qu -t "$session" @vim_daily_mouse_base
}
trap restore_mouse EXIT
trap 'restore_mouse; exit 130' HUP INT TERM
if [ -n "$mouse_line" ]; then
  tmux set-option -q -t "$session" @vim_daily_mouse_base "local:${mouse_line#mouse }"
else
  tmux set-option -q -t "$session" @vim_daily_mouse_base inherit
fi
tmux set-option -q -t "$session" @vim_daily_mouse_owner "$$"
tmux set-option -q -t "$session" mouse off
popup_pane="$(tmux display-message -p -t "$session" '#{pane_id}' 2>/dev/null)"
popup_tmux="$(tmux display-message -p -t "$session" '#{socket_path},#{pid},#{session_id}' 2>/dev/null)"
[ -n "$popup_pane" ] && [ -n "$popup_tmux" ] || exit 1
tmux display-popup -e VIM_DAILY_POPUP=1 -e "TMUX=$popup_tmux" -e "TMUX_PANE=$popup_pane" -t "$session" -E -w 90% -h 85% \
  -T " vim drill · drag selects · Cmd-C copies · questions: y copies all " \
  "$gate --if-due"
