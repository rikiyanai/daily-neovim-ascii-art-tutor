#!/usr/bin/env bash
# Symlink vim-daily into place. Idempotent; safe to re-run after a git pull.
#
# Everything is symlinked rather than copied, so editing a drill in this repo
# changes the installed system immediately and `git status` sees your edits.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bin="$HOME/.local/bin"
share="${XDG_DATA_HOME:-$HOME/.local/share}/vim-daily"
tmuxdir="$HOME/.tmux/scripts"

mkdir -p "$bin" "$tmuxdir" "$(dirname "$share")"

ln -sfn "$repo/bin/vim-daily-gate" "$bin/vim-daily-gate"
ln -sfn "$repo/bin/vim-drill"      "$bin/vim-drill"
ln -sfn "$repo/bin/vim-daily-setup-check" "$bin/vim-daily-setup-check"
ln -sfn "$repo/share"              "$share"
for f in vim-drill-popup.sh vim-drill-popup-force.sh vim-drill-hourly.sh; do
  ln -sfn "$repo/tmux/$f" "$tmuxdir/$f"
done
echo "linked: $bin/vim-daily-gate, $bin/vim-drill, $share, $tmuxdir/vim-drill-*.sh"

# VD-58: the interactive dashboard (vim-daily-gate --dashboard / --tree) runs
# Textual from a managed venv; Homebrew python is PEP-668 managed. Idempotent:
# uv reuses the venv and only installs what the pinned file changes. Without
# uv or the venv the gate falls back to the static text tree.
venv="${XDG_DATA_HOME:-$HOME/.local/share}/vim-daily-venv"
if command -v uv >/dev/null 2>&1; then
  [ -x "$venv/bin/python" ] || uv venv --quiet "$venv"
  uv pip install --quiet --python "$venv/bin/python" -r "$repo/share/requirements-dashboard.txt"
  echo "dashboard venv: $venv"
else
  echo "uv not found: skipped the dashboard venv (static --tree still works)"
fi

# macOS: the hourly trigger. The two tmux triggers are event-driven and can stay
# silent all day on one long-lived session; this one is the actual clock.
if [ "$(uname -s)" = "Darwin" ] && [ "${VIM_DAILY_INSTALL_NO_LAUNCHD:-0}" != "1" ]; then
  agents="$HOME/Library/LaunchAgents"
  mkdir -p "$agents"
  cp "$repo/launchd/com.vim-daily.hourly.plist" "$agents/"
  launchctl unload "$agents/com.vim-daily.hourly.plist" 2>/dev/null || true
  launchctl load   "$agents/com.vim-daily.hourly.plist"
  echo "loaded: com.vim-daily.hourly (every 900s)"
elif [ "$(uname -s)" != "Darwin" ]; then
  echo "not macOS: run tmux/vim-drill-hourly.sh from cron for the hourly trigger"
else
  echo "skipped launchd setup (VIM_DAILY_INSTALL_NO_LAUNCHD=1)"
fi

cat <<'MSG'

Two manual steps remain, because they append to files you own:

  1. shell/zshrc-snippet.zsh   -> append to ~/.zshrc
  2. tmux/tmux-snippet.conf    -> append to ~/.tmux.conf

Then: vim-drill --status
MSG

# Inspect only. Never write into, bootstrap, or otherwise take ownership of the
# user's Neovim configuration. Missing learning aids are recommendations, not
# installation failures.
"$repo/bin/vim-daily-setup-check"
