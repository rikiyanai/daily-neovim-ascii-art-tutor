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
ln -sfn "$repo/share"              "$share"
for f in vim-drill-popup.sh vim-drill-popup-force.sh vim-drill-hourly.sh; do
  ln -sfn "$repo/tmux/$f" "$tmuxdir/$f"
done
echo "linked: $bin/vim-daily-gate, $bin/vim-drill, $share, $tmuxdir/vim-drill-*.sh"

# macOS: the hourly trigger. The two tmux triggers are event-driven and can stay
# silent all day on one long-lived session; this one is the actual clock.
if [ "$(uname -s)" = "Darwin" ]; then
  agents="$HOME/Library/LaunchAgents"
  mkdir -p "$agents"
  cp "$repo/launchd/com.vim-daily.hourly.plist" "$agents/"
  launchctl unload "$agents/com.vim-daily.hourly.plist" 2>/dev/null || true
  launchctl load   "$agents/com.vim-daily.hourly.plist"
  echo "loaded: com.vim-daily.hourly (every 3600s)"
else
  echo "not macOS: run tmux/vim-drill-hourly.sh from cron for the hourly trigger"
fi

cat <<'MSG'

Two manual steps remain, because they append to files you own:

  1. shell/zshrc-snippet.zsh   -> append to ~/.zshrc
  2. tmux/tmux-snippet.conf    -> append to ~/.tmux.conf

Then: vim-drill --status
MSG
