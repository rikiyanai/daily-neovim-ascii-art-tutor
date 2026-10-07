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
session="$(tmux display-message -p '#S' 2>/dev/null)"
[ -n "$session" ] || exit 0
popup_pane="$(tmux display-message -p -t "$session" '#{pane_id}' 2>/dev/null)"
popup_tmux="$(tmux display-message -p -t "$session" '#{socket_path},#{pid},#{session_id}' 2>/dev/null)"
[ -n "$popup_pane" ] && [ -n "$popup_tmux" ] || exit 1

# Keep the global option and key tables untouched (VD-31/VD-33). The owner and
# base markers prevent overlapping launchers from restoring each other's
# state. A later attach also repairs an override left by an owner killed with
# SIGKILL before deciding whether a lesson is due.
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
tmux display-popup -e VIM_DAILY_POPUP=1 -e "TMUX=$popup_tmux" -e "TMUX_PANE=$popup_pane" -t "$session" -E -w 90% -h 85% \
  -T " vim drill · drag selects · Cmd-C copies · questions: y copies all " \
  "$gate --if-due"
