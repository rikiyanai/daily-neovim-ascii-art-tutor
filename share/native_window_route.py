"""Move a selected native lesson out of tmux's non-graphics popup parser.

The existing tutor gate still owns scheduling, the session lock and grading.
This adapter changes only its new window's exit policy and supplies no
successful learner events. Existing panes and global options stay unchanged.
"""
import json
import os
from pathlib import Path
import shlex
import socket
import subprocess
import tempfile
import uuid

import sjis_terminal


CHILD_ACK_TIMEOUT = 10.0


def _wait_for_child_ack(server, nonce):
    """Wait for the nonce-bound child load acknowledgement."""
    server.settimeout(CHILD_ACK_TIMEOUT)
    try:
        connection, _address = server.accept()
    except socket.timeout as exc:
        raise RuntimeError("Native tutor child did not acknowledge session load before timeout.") from exc
    with connection:
        connection.settimeout(2.0)
        chunks = []
        remaining = 4096
        while remaining:
            chunk = connection.recv(min(1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
            if b"\n" in chunk:
                break
        payload = b"".join(chunks).decode("utf-8")
    try:
        ack = json.loads(payload)
    except (TypeError, ValueError, UnicodeError) as exc:
        raise RuntimeError("Native tutor child sent an invalid session acknowledgement.") from exc
    if not isinstance(ack, dict) or ack.get("nonce") != nonce:
        raise RuntimeError("Native tutor child sent a stale session acknowledgement.")
    if ack.get("phase") != "curriculum-loaded" or not isinstance(ack.get("pid"), int):
        raise RuntimeError("Native tutor child did not acknowledge a loaded session.")
    return ack


def open_window(cfg, argv):
    state = sjis_terminal.inspect_tmux_passthrough()
    if state is None:
        raise RuntimeError("Native popup routing needs verified tmux pane ownership.")
    gate = Path(cfg.share).resolve().parent / "bin" / "vim-daily-gate"
    if not gate.is_file():
        raise RuntimeError("The native-window tutor gate is missing: %s" % gate)
    target = state["target"]
    # The new pane receives its own TMUX/TMUX_PANE from tmux. Never carry the
    # popup's pane id into that pane or enable a global graphics option.
    env = ["env", "-u", "VIM_DAILY_POPUP", "-u", "VIM_DAILY_ACTIVE",
           "XDG_STATE_HOME=" + str(Path(cfg.state).parent), "VIM_DAILY_NATIVE_WINDOW=1"]
    for key in ("VIM_DAILY_CLEAN", "VIM_DAILY_USE_USER_CONFIG",
                "VIM_DAILY_TEXTUAL", "VIM_DAILY_VIEWER", "VIM_DAILY_NO_WARMUP",
                "VIM_DAILY_SAITAMAAR_FONT", "VIM_DAILY_MAX_TRIES",
                "VIM_DAILY_CURRICULUM_V2", "VIM_DAILY_USE_MANAGED_RUNTIME",
                "VIM_DAILY_TARGET", "VIM_DAILY_COOLDOWN", "EDITOR",
                "XDG_DATA_HOME", "NO_COLOR", "TERM",
                "VIM_DAILY_TMUX_READY_SIGNAL", "VIM_DAILY_TEST_CHOICE_ORDER",
                "VIM_DAILY_TMUX_FINISHED_SIGNAL", "VIM_DAILY_TMUX_FEEDBACK_SIGNAL",
                "VIM_DAILY_TMUX_POST_SIGNAL", "VIM_DAILY_TMUX_QUESTION_SIGNAL"):
        if key in os.environ:
            env.append(key + "=" + os.environ[key])
    route = list(argv)
    tmux = ["tmux", "-S", target["socket"]]
    nonce = uuid.uuid4().hex
    channel = "vim-daily-native-start-" + nonce
    ack_dir = tempfile.TemporaryDirectory(prefix="vim-daily-native-ack-")
    ack_server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    ack_path = Path(ack_dir.name) / "a"
    window = None
    activated = False
    channel_released = False
    def checked(args, message):
        result = subprocess.run([*tmux, *args], text=True, capture_output=True, timeout=5)
        if result.returncode:
            raise RuntimeError(message + ": " + result.stderr.strip())
        return result
    try:
        ack_server.bind(str(ack_path))
        ack_server.listen(1)
        env += ["VIM_DAILY_NATIVE_ACK_SOCKET=" + str(ack_path),
                "VIM_DAILY_NATIVE_ACK_NONCE=" + nonce]
        # Hold the child behind a private server lock until its owned exit
        # policy is set. A failed setup must not race a real lesson attempt.
        checked(["wait-for", "-L", channel], "Native tutor start lock unavailable")
        command = " && ".join([
            shlex.join([*tmux, "wait-for", "-L", channel]),
            shlex.join([*tmux, "wait-for", "-U", channel]),
            "exec " + shlex.join([*env, str(gate), *route]),
        ])
        result = checked([
            "new-window", "-P", "-F", "#{window_id}", "-t",
            "$" + target["session_token"], "-n", "vim-daily JIS", command,
        ], "Native tutor window was not created")
        identity = result.stdout.strip()
        if not identity.startswith("@") or not identity[1:].isdigit():
            raise RuntimeError("Native tutor window returned an invalid identity.")
        window = identity
        # Existing parent/window/global options remain unchanged.
        checked(["set-option", "-w", "-t", window, "remain-on-exit", "off"],
                "Native tutor window exit policy was not established")
        checked(["wait-for", "-U", channel], "Native tutor child was not released")
        channel_released = True
        _wait_for_child_ack(ack_server, nonce)
        activated = True
        return window
    finally:
        ack_server.close()
        ack_dir.cleanup()
        if not activated:
            if window:
                subprocess.run([*tmux, "kill-window", "-t", window],
                               text=True, capture_output=True, timeout=5)
            if not channel_released:
                subprocess.run([*tmux, "wait-for", "-U", channel],
                               text=True, capture_output=True, timeout=5)
