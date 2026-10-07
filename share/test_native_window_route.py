"""Routing fixtures and isolated tmux housekeeping, not Ghostty grade proof."""
import os
import contextlib
import io
import json
import shutil
import socket
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import native_window_route as route
import v2_runtime as runtime


class NativeWindowRoute(unittest.TestCase):
    def test_child_missing_ack_listener_stops_before_attempt(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-native-missing-ack-") as directory:
            path = str(Path(directory) / "missing")
            with patch.dict(os.environ, {
                "VIM_DAILY_NATIVE_WINDOW": "1", "VIM_DAILY_NATIVE_ACK_SOCKET": path,
                "VIM_DAILY_NATIVE_ACK_NONCE": "current"}):
                with self.assertRaisesRegex(RuntimeError, "no lesson was attempted"):
                    runtime._native_handoff_ack({"revision": "fixture"})
                self.assertNotIn("VIM_DAILY_NATIVE_ACK_SOCKET", os.environ)

    def test_native_confirmation_cannot_match_previous_prompt_in_scrollback(self):
        from test_native_window_route_real import _credit_prompt_ready
        previous = "BEFORE EDITING\nEnter = inspected these four native panels · q = cancel\n"
        loading = previous + "BEFORE CREDIT\nBEFORE\nYOURS\nTARGET\nCHANGED PIXELS\n"
        self.assertFalse(_credit_prompt_ready(previous))
        self.assertFalse(_credit_prompt_ready(loading))
        self.assertTrue(_credit_prompt_ready(loading + "Enter = inspected these four native panels · q = cancel"))

    def test_managed_runtime_alias_does_not_reexec_forever(self):
        installed = Path("/Users/r/.local/share/vim-daily-venv")
        if not (installed / "bin/python").is_file():
            self.skipTest("managed tutor runtime unavailable")
        with tempfile.TemporaryDirectory(prefix="vim-daily-managed-alias-") as directory:
            root = Path(directory)
            data = root / "data"
            data.mkdir()
            (data / "vim-daily-venv").symlink_to(installed, target_is_directory=True)
            (data / "vim-daily").symlink_to(Path(__file__).parent, target_is_directory=True)
            environment = dict(os.environ, XDG_DATA_HOME=str(data),
                               XDG_STATE_HOME=str(root / "state"),
                               VIM_DAILY_USE_MANAGED_RUNTIME="1", VIM_DAILY_TARGET="0")
            gate = Path(__file__).parent.parent / "bin/vim-daily-gate"
            result = subprocess.run([str(gate), "--due-quiet"], env=environment,
                                    capture_output=True, text=True, timeout=5)
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertFalse((root / "state/vim-daily/events-v2.jsonl").exists())

    @unittest.skipUnless(shutil.which("tmux"), "tmux required for isolated server control")
    def test_real_owned_window_closes_with_parent_remain_on_exit_enabled(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-native-route-") as directory:
            socket = str(Path(directory) / "tmux.sock")
            command = ["tmux", "-S", socket]
            def tmux(*args):
                return subprocess.run([*command, *args], text=True, capture_output=True,
                                      check=True, timeout=5).stdout.strip()
            try:
                session = tmux("new-session", "-d", "-P", "-F", "#{session_id}",
                               "-s", "owned", "tail -f /dev/null")
                parent = tmux("display-message", "-p", "-t", session, "#{window_id}")
                tmux("set-option", "-w", "-t", parent, "remain-on-exit", "on")
                before = tmux("show-options", "-w", "-v", "-t", parent, "remain-on-exit")
                global_before = tmux("show-options", "-gw", "-v", "remain-on-exit")
                cfg = SimpleNamespace(share=str(Path(__file__).parent),
                                      state=str(Path(directory) / "state/vim-daily"))
                context = {"target": {"socket": socket, "session_token": session[1:]}}
                with patch.object(route.sjis_terminal, "inspect_tmux_passthrough", return_value=context), \
                        patch.dict(os.environ, {"VIM_DAILY_TARGET": "0"}):
                    window = route.open_window(cfg, ["--due-quiet"])
                deadline = time.monotonic() + 5
                while window in tmux("list-windows", "-t", session, "-F", "#{window_id}").splitlines():
                    self.assertLess(time.monotonic(), deadline, "temporary window remained after gate exit")
                    time.sleep(0.05)
                self.assertEqual(tmux("show-options", "-w", "-v", "-t", parent, "remain-on-exit"), before)
                self.assertEqual(tmux("show-options", "-gw", "-v", "remain-on-exit"), global_before)
                self.assertFalse(Path(cfg.state, "events-v2.jsonl").exists())
            finally:
                subprocess.run([*command, "kill-server"], text=True, capture_output=True, timeout=5)

    def test_exact_server_new_pane_and_same_gate_route(self):
        cfg = SimpleNamespace(share=str(Path(__file__).parent), state="/tmp/test/vim-daily")
        context = {"target": {"socket": "/tmp/owned-socket", "session_token": "3"}}
        result = SimpleNamespace(returncode=0, stdout="@9\n", stderr="")
        with patch.object(route.sjis_terminal, "inspect_tmux_passthrough", return_value=context), \
                patch.object(route.subprocess, "run", return_value=result) as run, \
                patch.object(route, "_wait_for_child_ack", return_value={
                    "nonce": "fixture", "phase": "curriculum-loaded", "pid": 1}), \
                patch.dict(os.environ, {"VIM_DAILY_POPUP": "1", "TMUX_PANE": "%8",
                                        "VIM_DAILY_TEXTUAL": "1"}, clear=True):
            self.assertEqual(route.open_window(cfg, ["--card", "M10.01"]), "@9")
        args = run.call_args_list[1].args[0]
        self.assertEqual(args[:5], ["tmux", "-S", "/tmp/owned-socket", "new-window", "-P"])
        self.assertIn("$3", args)
        self.assertIn("--card M10.01", args[-1])
        self.assertIn("-u VIM_DAILY_POPUP", args[-1])
        self.assertNotIn("TMUX_PANE=", args[-1])
        self.assertEqual(run.call_args_list[2].args[0], [
            "tmux", "-S", "/tmp/owned-socket", "set-option", "-w", "-t", "@9",
            "remain-on-exit", "off"])

    def test_continuation_keeps_scheduler_cap_and_practice_stays_uncredited(self):
        cfg = SimpleNamespace(share=str(Path(__file__).parent), state="/tmp/test/vim-daily")
        context = {"target": {"socket": "/tmp/owned-socket", "session_token": "3"}}
        result = SimpleNamespace(returncode=0, stdout="@9\n", stderr="")
        for argv in (["--continue"], ["--practice-card", "M10.01"],
                     ["--practice-review", "M10.01"]):
            with patch.object(route.sjis_terminal, "inspect_tmux_passthrough", return_value=context), \
                    patch.object(route.subprocess, "run", return_value=result) as run, \
                    patch.object(route, "_wait_for_child_ack", return_value={
                        "nonce": "fixture", "phase": "curriculum-loaded", "pid": 1}):
                route.open_window(cfg, argv)
            command = run.call_args_list[1].args[0][-1]
            self.assertTrue(command.endswith(" ".join(argv)), command)
            self.assertNotIn("--force", command)

    def test_exit_policy_denial_kills_only_owned_window_before_child_release(self):
        cfg = SimpleNamespace(share=str(Path(__file__).parent), state="/tmp/test/vim-daily")
        context = {"target": {"socket": "/tmp/owned-socket", "session_token": "3"}}
        ok = SimpleNamespace(returncode=0, stdout="", stderr="")
        created = SimpleNamespace(returncode=0, stdout="@9\n", stderr="")
        denied = SimpleNamespace(returncode=1, stdout="", stderr="fixture policy denial")
        with patch.object(route.sjis_terminal, "inspect_tmux_passthrough", return_value=context), \
                patch.object(route.subprocess, "run", side_effect=[ok, created, denied, ok, ok]) as run:
            with self.assertRaisesRegex(RuntimeError, "fixture policy denial"):
                route.open_window(cfg, ["--force"])
        calls = [row.args[0] for row in run.call_args_list]
        self.assertEqual(calls[0][3:5], ["wait-for", "-L"])
        self.assertIn("wait-for -L", calls[1][-1])
        self.assertEqual(calls[3], ["tmux", "-S", "/tmp/owned-socket", "kill-window", "-t", "@9"])
        self.assertEqual(calls[4][3:5], ["wait-for", "-U"])

    def test_child_ack_timeout_kills_only_owned_window_after_release(self):
        cfg = SimpleNamespace(share=str(Path(__file__).parent), state="/tmp/test/vim-daily")
        context = {"target": {"socket": "/tmp/owned-socket", "session_token": "3"}}
        ok = SimpleNamespace(returncode=0, stdout="", stderr="")
        created = SimpleNamespace(returncode=0, stdout="@9\n", stderr="")
        with patch.object(route.sjis_terminal, "inspect_tmux_passthrough", return_value=context), \
                patch.object(route.subprocess, "run", side_effect=[ok, created, ok, ok, ok]) as run, \
                patch.object(route, "_wait_for_child_ack", side_effect=RuntimeError("ack timeout")):
            with self.assertRaisesRegex(RuntimeError, "ack timeout"):
                route.open_window(cfg, ["--due-quiet"])
        calls = [row.args[0] for row in run.call_args_list]
        self.assertEqual(calls[0][3:5], ["wait-for", "-L"])
        self.assertEqual(calls[1][3:5], ["new-window", "-P"])
        self.assertEqual(calls[2], ["tmux", "-S", "/tmp/owned-socket", "set-option", "-w", "-t", "@9",
                                    "remain-on-exit", "off"])
        self.assertEqual(calls[3][3:5], ["wait-for", "-U"])
        # The channel was already released before acknowledgement; cleanup
        # must kill this window only and must not unlock the channel twice.
        self.assertEqual(calls[4], ["tmux", "-S", "/tmp/owned-socket", "kill-window", "-t", "@9"])
        self.assertEqual(len(calls), 5)

    def test_runtime_ack_is_nonce_bound_and_one_shot(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-native-ack-test-") as directory:
            path = str(Path(directory) / "ack")
            server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                server.bind(path)
                server.listen(1)
                with patch.dict(os.environ, {"VIM_DAILY_NATIVE_WINDOW": "1",
                                             "VIM_DAILY_NATIVE_ACK_SOCKET": path,
                                             "VIM_DAILY_NATIVE_ACK_NONCE": "nonce-1"}, clear=True):
                    runtime._native_handoff_ack({"revision": "fixture-rev"})
                    self.assertNotIn("VIM_DAILY_NATIVE_ACK_SOCKET", os.environ)
                    self.assertNotIn("VIM_DAILY_NATIVE_ACK_NONCE", os.environ)
                    server.settimeout(2)
                    connection, _ = server.accept()
                    with connection:
                        payload = connection.recv(4096).decode("utf-8")
                ack = json.loads(payload)
                self.assertEqual(ack["nonce"], "nonce-1")
                self.assertEqual(ack["phase"], "curriculum-loaded")
                self.assertEqual(ack["revision"], "fixture-rev")
                self.assertIsInstance(ack["pid"], int)
            finally:
                server.close()

    def test_route_rejects_stale_child_ack_nonce(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-native-stale-ack-") as directory:
            server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            path = str(Path(directory) / "ack")
            server.bind(path)
            server.listen(1)

            def send_stale_ack():
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                    client.connect(path)
                    client.sendall((json.dumps({"nonce": "stale", "phase": "curriculum-loaded",
                                                "pid": 1}) + "\n").encode("utf-8"))

            sender = threading.Thread(target=send_stale_ack)
            sender.start()
            try:
                with self.assertRaisesRegex(RuntimeError, "stale session acknowledgement"):
                    route._wait_for_child_ack(server, "current")
            finally:
                sender.join(timeout=2)
                server.close()
            self.assertFalse(sender.is_alive())

    def test_missing_identity_does_not_launch(self):
        with patch.object(route.sjis_terminal, "inspect_tmux_passthrough", return_value=None), \
                patch.object(route.subprocess, "run") as run:
            with self.assertRaises(RuntimeError):
                route.open_window(None, [])
            run.assert_not_called()

    def test_launch_error_is_not_a_success(self):
        cfg = SimpleNamespace(share=str(Path(__file__).parent), state="/tmp/test/vim-daily")
        context = {"target": {"socket": "/tmp/owned-socket", "session_token": "3"}}
        with patch.object(route.sjis_terminal, "inspect_tmux_passthrough", return_value=context), \
                patch.object(route.subprocess, "run", return_value=SimpleNamespace(
                    returncode=1, stdout="", stderr="fixture launch denial")):
            with self.assertRaisesRegex(RuntimeError, "fixture launch denial"):
                route.open_window(cfg, ["--force"])

    def test_selected_native_popup_releases_launch_lock_before_child_and_creates_no_attempt(self):
        card = {"id": "M10.01", "medium": "proportional-sjis"}
        cfg = SimpleNamespace(state="/tmp/native-fixture/vim-daily", share="unused")
        for unavailable in (False, True):
            helper = SimpleNamespace(open_window=Mock(
                return_value="@9", side_effect=RuntimeError("fixture denial") if unavailable else None))
            output = io.StringIO()
            with contextlib.redirect_stdout(output), \
                    patch.object(output, "isatty", return_value=True), \
                    patch.object(__import__("sys").stdin, "isatty", return_value=True), \
                    patch.dict(os.environ, {"VIM_DAILY_POPUP": "1", "TMUX": "owned"}), \
                    patch.object(runtime, "load_curriculum", return_value={"revision": "fixture", "cards": [card]}), \
                    patch.object(runtime, "read_events", return_value=[]), \
                    patch.object(runtime, "project", return_value={}), \
                    patch.object(runtime, "save_projection"), \
                    patch.object(runtime, "due_review", return_value=None), \
                    patch.object(runtime, "next_card", return_value=card), \
                    patch.object(runtime, "should_run_review", return_value=False), \
                    patch.object(runtime, "_native_module", return_value=helper), \
                    patch.object(runtime, "SessionLock") as lock, \
                    patch.object(runtime, "append_event") as event:
                def launch_child(*_args):
                    lock.return_value.__exit__.assert_called_once()
                    if unavailable:
                        raise RuntimeError("fixture denial")
                    return "@9"
                helper.open_window.side_effect = launch_child
                self.assertEqual(runtime.run(cfg, ["--force"]), int(unavailable))
                lock.assert_called_once()
                lock.return_value.__enter__.assert_called_once()
                event.assert_not_called()
                helper.open_window.assert_called_once_with(cfg, ["--force"])
            self.assertIn("No lesson was attempted" if unavailable else "temporary tmux window @9",
                          output.getvalue())


if __name__ == "__main__":
    unittest.main()
