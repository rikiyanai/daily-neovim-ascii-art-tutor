"""Terminal PNG protocol fixtures, not operator visual-acceptance receipts."""
import base64
import contextlib
import hashlib
import io
import os
from pathlib import Path
import pty
import re
import secrets
import shutil
import subprocess
import tempfile
import termios
import threading
import unittest
from unittest.mock import patch

import sjis_terminal as T
import sjis_tutor as S


@contextlib.contextmanager
def isolated_tmux_environment():
    """Yield a real, disposable tmux pane bound into TMUX/TMUX_PANE."""
    if not shutil.which("tmux"):
        raise unittest.SkipTest("tmux is required for pane restoration controls")
    socket_name = "sjis-terminal-" + secrets.token_hex(8)
    command = ["tmux", "-L", socket_name, "-f", "/dev/null", "new-session", "-d", "-s", "tutor"]
    subprocess.run(command, check=True, capture_output=True, text=True)

    def tmux(*args):
        completed = subprocess.run(
            ["tmux", "-L", socket_name, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    try:
        pane = tmux("list-panes", "-t", "tutor", "-F", "#{pane_id}")
        socket_path = tmux("display-message", "-p", "#{socket_path}")
        server_pid = tmux("display-message", "-p", "#{pid}")
        session_id = tmux("display-message", "-p", "#{session_id}").lstrip("$")
        tmux_value = f"{socket_path},{server_pid},{session_id}"
        with patch.dict(
            os.environ,
            {"TMUX": tmux_value, "TMUX_PANE": pane},
            clear=False,
        ):
            yield socket_name, pane, tmux
    finally:
        subprocess.run(
            ["tmux", "-L", socket_name, "kill-server"],
            check=False,
            capture_output=True,
            text=True,
        )


class TerminalProtocol(unittest.TestCase):
    def test_tmux_override_restores_inherited_off_without_global_mutation(self):
        with isolated_tmux_environment() as (_socket, pane, tmux):
            self.assertEqual(tmux("show-options", "-gwqv", "allow-passthrough"), "off")
            before = T.inspect_tmux_passthrough()
            self.assertEqual(before["pane_explicit"], "")
            self.assertEqual(before["pane_effective"], "off")
            with T.temporary_tmux_passthrough() as snapshot:
                self.assertEqual(snapshot["pane_explicit"], "")
                self.assertEqual(tmux("show-options", "-p", "-qv", "-t", pane,
                                      "allow-passthrough"), "on")
                self.assertEqual(tmux("show-options", "-p", "-Aqv", "-t", pane,
                                      "allow-passthrough"), "on")
                self.assertEqual(tmux("show-options", "-gwqv", "allow-passthrough"), "off")
            after = T.inspect_tmux_passthrough()
            self.assertEqual(after["pane_explicit"], "")
            self.assertEqual(after["pane_effective"], "off")
            self.assertEqual(after["global_default"], "off")

    def test_tmux_override_leaves_inherited_on_untouched(self):
        with isolated_tmux_environment() as (_socket, pane, tmux):
            tmux("set-option", "-w", "-t", pane, "allow-passthrough", "all")
            before = T.inspect_tmux_passthrough()
            self.assertEqual(before["pane_explicit"], "")
            self.assertEqual(before["pane_effective"], "all")
            self.assertEqual(before["window_explicit"], "all")
            with T.temporary_tmux_passthrough() as snapshot:
                self.assertEqual(snapshot["pane_effective"], "all")
                self.assertEqual(tmux("show-options", "-p", "-qv", "-t", pane,
                                      "allow-passthrough"), "")
            after = T.inspect_tmux_passthrough()
            self.assertEqual(after["pane_explicit"], "")
            self.assertEqual(after["pane_effective"], "all")
            self.assertEqual(after["window_explicit"], "all")
            self.assertEqual(after["global_default"], "off")

    def test_tmux_override_restores_explicit_pane_on_cancellation(self):
        with isolated_tmux_environment() as (_socket, pane, tmux):
            tmux("set-option", "-p", "-t", pane, "allow-passthrough", "off")
            with self.assertRaisesRegex(RuntimeError, "cancelled"):
                with T.temporary_tmux_passthrough():
                    self.assertEqual(tmux("show-options", "-p", "-qv", "-t", pane,
                                          "allow-passthrough"), "on")
                    raise RuntimeError("preview cancelled")
            after = T.inspect_tmux_passthrough()
            self.assertEqual(after["pane_explicit"], "off")
            self.assertEqual(after["pane_effective"], "off")
            self.assertEqual(after["global_default"], "off")

    def test_tmux_override_rejects_unowned_or_partial_identity(self):
        with patch.dict(os.environ, {"TMUX": "", "TMUX_PANE": "%0"}, clear=False):
            with self.assertRaisesRegex(RuntimeError, "both TMUX and TMUX_PANE"):
                with T.temporary_tmux_passthrough():
                    pass
        with patch.dict(
            os.environ,
            {"TMUX": "/private/tmp/sjis-terminal-no-such-server,999999,0", "TMUX_PANE": "%0"},
            clear=False,
        ):
            with self.assertRaisesRegex(RuntimeError, "exact tutor tmux pane/server"):
                with T.temporary_tmux_passthrough():
                    pass

    def test_four_panel_rejection_restores_pane_override(self):
        rows = ["　⌒ヽ", "　ヽ_ノ"]
        with isolated_tmux_environment():
            with tempfile.TemporaryDirectory(prefix="vim-daily-terminal-tmux-") as directory:
                path = Path(directory) / "art.txt"
                path.write_text(S.art_text(rows), encoding="utf-8")
                calls = []

                def sender(png, image_id):
                    calls.append(png)
                    if len(calls) == 2:
                        raise RuntimeError("terminal rejected native image")
                    return {
                        "image_id": image_id,
                        "png_sha256": hashlib.sha256(png).hexdigest(),
                        "terminal_reply": "OK",
                    }

                with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(
                    RuntimeError, "rejected native image"
                ):
                    T.TerminalPreview(path, rows, sender=sender, confirm=lambda _: "").start()
            after = T.inspect_tmux_passthrough()
            self.assertEqual(len(calls), 2)
            self.assertEqual(after["pane_explicit"], "")
            self.assertEqual(after["pane_effective"], "off")
            self.assertEqual(after["global_default"], "off")

    def test_actual_pty_ack_parser_and_terminal_mode_restoration(self):
        for matching in (True, False):
            master, slave = pty.openpty()
            previous = termios.tcgetattr(slave)
            incoming = os.fdopen(os.dup(slave), "r")
            outgoing = io.TextIOWrapper(os.fdopen(os.dup(slave), "wb"), write_through=True)
            def emulate():
                data = bytearray()
                while b"\x1b\\" not in data:
                    data.extend(os.read(master, 4096))
                os.write(master, b"\x1b_Gi=" + (b"31" if matching else b"32") + b";OK\x1b\\")
            worker = threading.Thread(target=emulate, daemon=True)
            worker.start()
            try:
                with patch("sys.stdin", incoming), patch("sys.stdout", outgoing):
                    if matching:
                        self.assertEqual(T.transmit_png(b"fixture", 31, timeout=0.1)["terminal_reply"], "OK")
                    else:
                        with self.assertRaisesRegex(RuntimeError, "No graphics acknowledgement"):
                            T.transmit_png(b"fixture", 31, timeout=0.1)
                restored = termios.tcgetattr(slave)
                # macOS may set the kernel's pending-input bookkeeping bit
                # while restoring cooked mode. It is not an application mode.
                restored[3] &= ~getattr(termios, "PENDIN", 0)
                previous[3] &= ~getattr(termios, "PENDIN", 0)
                self.assertEqual(restored, previous)
            finally:
                worker.join(timeout=1)
                incoming.close()
                outgoing.close()
                os.close(slave)
                os.close(master)

    def test_png_chunks_and_tmux_transport_are_byte_exact(self):
        png = bytes(range(256)) * 40
        for tmux in (False, True):
            chunks = list(T.graphics_chunks(png, 31, tmux=tmux))
            self.assertGreater(len(chunks), 1)
            data = []
            for index, packet in enumerate(chunks):
                if tmux:
                    self.assertTrue(packet.startswith(b"\x1bPtmux;"))
                    packet = packet[8:-2].replace(b"\x1b\x1b", b"\x1b")
                self.assertTrue(packet.startswith(b"\x1b_G"))
                control, encoded = packet[3:-2].split(b";", 1)
                self.assertLessEqual(len(encoded), 4096)
                self.assertIn(b"m=" + str(int(index < len(chunks) - 1)).encode(), control)
                data.append(encoded)
            self.assertEqual(base64.b64decode(b"".join(data)), png)

    def test_terminal_receipt_needs_all_current_panels(self):
        rows = ["　⌒ヽ", "　ヽ_ノ"]
        emitted = []
        def sender(png, image_id):
            emitted.append(png)
            return {"image_id": image_id, "png_sha256": hashlib.sha256(png).hexdigest(), "terminal_reply": "OK"}
        with tempfile.TemporaryDirectory(prefix="vim-daily-terminal-native-") as directory:
            path = Path(directory) / "art.txt"
            path.write_text(S.art_text(rows), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                with T.TerminalPreview(path, rows, sender=sender, confirm=lambda _: "") as preview:
                    final = preview.final_receipt()
                    self.assertTrue(final["ready"])
                    self.assertEqual(len(final["display"]["images"]), 4)
                    self.assertEqual(len(emitted), 8)
                    path.write_text(S.art_text([row + "　 " for row in rows]), encoding="utf-8")
                    self.assertFalse(preview.final_receipt()["ready"])

    def test_cancel_and_unbound_terminal_ack_deny_credit(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-terminal-negative-") as directory:
            path = Path(directory) / "art.txt"
            path.write_text("　ヽ\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(RuntimeError, "does not bind"):
                T.TerminalPreview(path, ["　ヽ"], sender=lambda *_: {}, confirm=lambda _: "").start()
            def sender(png, image_id):
                return {"image_id": image_id, "png_sha256": hashlib.sha256(png).hexdigest(), "terminal_reply": "OK"}
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(RuntimeError, "cancelled"):
                T.TerminalPreview(path, ["　ヽ"], sender=sender, confirm=lambda _: "q").start()


if __name__ == "__main__":
    unittest.main()
