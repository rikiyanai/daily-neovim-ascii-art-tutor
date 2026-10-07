#!/usr/bin/env python3
"""Drive Prefix+Q through a client-attached, isolated tmux server."""
import json
import os
import shlex
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
cols = int(os.environ.get("VIM_DAILY_TEST_COLUMNS", "80"))
rows = int(os.environ.get("VIM_DAILY_TEST_ROWS", "24"))
tag = uuid.uuid4().hex[:8]
inner, outer = "vdquiz-i-" + tag, "vdquiz-o-" + tag

def tmux(sock, *args):
    return subprocess.run(["tmux", "-L", sock, *args], check=True,
                          capture_output=True, text=True).stdout

with tempfile.TemporaryDirectory(prefix="vim-daily-quiz-popup-") as tmp:
    state = Path(tmp) / "vim-daily"
    state.mkdir()
    (state / "events-v2.jsonl").write_text(json.dumps({
        "type": "card", "result": "pass", "card_id": "M0.01", "module_id": "M0",
        "at": "2026-09-20T12:00:00-04:00", "next_due": "2099-01-01T00:00:00-04:00",
    }) + "\n")
    try:
        tmux(inner, "-f", "/dev/null", "new-session", "-d", "-s", "quiz",
             "-x", str(cols), "-y", str(rows), "/bin/zsh", "-f")
        for key, value in {"XDG_STATE_HOME": tmp, "TERM": "xterm-256color",
                           "VIM_DAILY_NO_WARMUP": "1"}.items():
            tmux(inner, "set-environment", "-t", "quiz", key, value)
        # Only this sandbox server receives the binding. No user tmux setting
        # or installed launcher is changed to make the test pass.
        launcher = "bash " + shlex.quote(str(ROOT / "tmux" / "vim-drill-quiz.sh"))
        tmux(inner, "bind-key", "Q", "run-shell", "-b", launcher)
        tmux(inner, "set-option", "-g", "mouse", "on")
        local_mouse = os.environ.get("VIM_DAILY_TEST_LOCAL_MOUSE", "")
        if local_mouse:
            assert local_mouse in ("on", "off")
            tmux(inner, "set-option", "-t", "quiz", "mouse", local_mouse)
        baseline = tmux(inner, "show-options", "-g")
        attach = "env -u TMUX tmux -L %s attach-session -t quiz" % shlex.quote(inner)
        tmux(outer, "-f", "/dev/null", "new-session", "-d", "-s", "terminal",
             "-x", str(cols), "-y", str(rows), attach)
        # Synchronize on the attached shell before sending the real prefix.
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if tmux(inner, "list-clients").strip():
                break
            time.sleep(0.05)
        tmux(outer, "send-keys", "-t", "terminal", "C-b", "Q")
        deadline = time.monotonic() + 8
        shot = ""
        while time.monotonic() < deadline:
            shot = tmux(outer, "capture-pane", "-p", "-t", "terminal")
            if "DECK QUIZ 1/" in shot:
                break
            time.sleep(0.05)
        assert "DECK QUIZ 1/" in shot and "vim quiz" in shot, shot
        assert baseline == tmux(inner, "show-options", "-g"), "launcher changed global options"
        assert tmux(inner, "show-options", "-v", "-t", "quiz", "mouse").strip() == "off"
        print("--- Prefix+Q popup %dx%d ---\n%s" % (cols, rows, shot.rstrip()))
        tmux(outer, "send-keys", "-t", "terminal", "s", "Enter")
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if tmux(inner, "show-options", "-qv", "-t", "quiz", "mouse").strip() == local_mouse and not tmux(inner, "show-options", "-qv", "-t", "quiz", "@vim_daily_mouse_owner").strip():
                break
            time.sleep(0.05)
        assert tmux(inner, "show-options", "-qv", "-t", "quiz", "mouse").strip() == local_mouse, tmux(outer, "capture-pane", "-p", "-t", "terminal")
        assert tmux(inner, "show-options", "-gv", "mouse").strip() == "on"
        assert not tmux(inner, "show-options", "-qv", "-t", "quiz", "@vim_daily_mouse_owner").strip()
        assert baseline == tmux(inner, "show-options", "-g")
        print("PASS Prefix+Q opens the real quiz popup without changing global tmux options")
    finally:
        for sock in (outer, inner):
            subprocess.run(["tmux", "-L", sock, "kill-server"], capture_output=True)
        subprocess.run(["pkill", "-9", "-f", tmp], capture_output=True)
