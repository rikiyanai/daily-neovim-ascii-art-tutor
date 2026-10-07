#!/usr/bin/env python3
"""C34 retrospective reward tests, including a copied-state production gate.

The headed proof copies the operator ledger into a temporary XDG state root,
then drives the real ``bin/vim-daily-gate`` and ``share/viewer.py`` route at
the three supported terminal sizes.  The real learner state is read and
hashed before and after; it is never used as the gate's writable state.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import pty
import select
import shutil
import struct
import subprocess
import sys
import tempfile
import termios
import time
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
GATE = ROOT / "bin" / "vim-daily-gate"
REAL_STATE = Path.home() / ".local" / "state" / "vim-daily"

sys.path.insert(0, str(HERE))
import retro_module_rewards as retro  # noqa: E402
import v2_runtime as runtime  # noqa: E402


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _curriculum():
    return runtime.load_curriculum(str(HERE))


def _operator_progress(cur):
    events = runtime.read_events(type("Cfg", (), {"state": str(REAL_STATE)})())
    return runtime.project(cur, events)


def _set_winsize(fd, columns, rows):
    # rows, columns, xpixel, ypixel
    termios_ioctl = struct.pack("HHHH", rows, columns, 0, 0)
    import fcntl
    fcntl.ioctl(fd, termios.TIOCSWINSZ, termios_ioctl)


def _run_gate_copy(columns, rows, mode="run"):
    """Run the real gate against a temp copy and return its raw PTY output."""

    if not REAL_STATE.joinpath("events-v2.jsonl").is_file():
        raise unittest.SkipTest("operator progress ledger is unavailable")
    before = {
        path: _sha256(path)
        for path in REAL_STATE.rglob("*")
        if path.is_file()
    }
    with tempfile.TemporaryDirectory(prefix="vim-daily-retro-gate-") as tmp:
        root = Path(tmp)
        state_home = root / "state"
        state = state_home / "vim-daily"
        data_home = root / "data"
        data_home.mkdir()
        state.mkdir(parents=True)
        (data_home / "vim-daily").symlink_to(HERE, target_is_directory=True)
        # This is a byte-for-byte copy of the actual append-only progress
        # ledger.  The projection is copied when present, but the runtime is
        # free to rebuild only inside the temporary root.
        for name in ("events-v2.jsonl", "progress-v2.json"):
            source = REAL_STATE / name
            if source.exists():
                shutil.copy2(source, state / name)

        env = dict(os.environ)
        env.update({
            "XDG_STATE_HOME": str(state_home),
            "XDG_DATA_HOME": str(data_home),
            "VIM_DAILY_USE_MANAGED_RUNTIME": "0",
            "VIM_DAILY_TEXTUAL": "0",
            "VIM_DAILY_TARGET": "0",
            "VIM_DAILY_VIEWER": "1",
            "VIM_DAILY_ANIM": "1",
            "TERM": "xterm-256color",
            "NO_COLOR": "1",
        })
        for key in ("VIM_DAILY_SKIP", "VIM_DAILY_ACTIVE", "NVIM"):
            env.pop(key, None)

        master, slave = pty.openpty()
        _set_winsize(slave, columns, rows)
        process = subprocess.Popen(
            [str(GATE), *([] if mode == "run" else [mode])], stdin=slave, stdout=slave, stderr=slave,
            env=env, close_fds=True,
        )
        os.close(slave)
        try:
            output = bytearray()
            deadline = time.monotonic() + 20
            def read_until(needle, *, start=0):
                while process.poll() is None and time.monotonic() < deadline:
                    text = output[start:].decode("utf-8", "replace")
                    if needle in text:
                        return len(output)
                    ready, _, _ = select.select([master], [], [], 0.2)
                    if ready:
                        try:
                            output.extend(os.read(master, 65536))
                        except OSError:
                            break
                raise AssertionError("production viewer did not render %r\n%s" % (
                    needle, output.decode("utf-8", "replace")))

            # Wait for cbreak mode and pause before stepping.  Sending a long
            # key string at process start can be consumed by the PTY's line
            # discipline before the viewer owns the terminal.
            cursor = read_until("pose 01 1/8")
            # No key is sent until automatic playback visibly advances.
            cursor = read_until("pose 02 2/8", start=cursor)
            os.write(master, b" ")
            cursor = read_until("paused", start=cursor)
            for index in range(3, 9):
                os.write(master, b"l")
                cursor = read_until("pose %02d %d/8" % (index, index), start=cursor)
            os.write(master, b"p")
            view_start = cursor
            cursor = read_until("M11", start=view_start)
            if "pose 01 1/8" not in output[view_start:].decode("utf-8", "replace"):
                cursor = read_until("pose 01 1/8", start=view_start)
            for index in range(2, 9):
                os.write(master, b"l")
                cursor = read_until("pose %02d %d/8" % (index, index), start=cursor)
            os.write(master, b"q")
            while process.poll() is None and time.monotonic() < deadline:
                ready, _, _ = select.select([master], [], [], 0.2)
                if ready:
                    try:
                        output.extend(os.read(master, 65536))
                    except OSError:
                        break
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
            while True:
                ready, _, _ = select.select([master], [], [], 0)
                if not ready:
                    break
                try:
                    chunk = os.read(master, 65536)
                except OSError:
                    break
                if not chunk:
                    break
                output.extend(chunk)
            if process.returncode != 0:
                raise AssertionError("production gate failed: %s\n%s" % (
                    process.returncode, output.decode("utf-8", "replace")))
            return output.decode("utf-8", "replace")
        finally:
            os.close(master)
            after = {
                path: _sha256(path)
                for path in REAL_STATE.rglob("*")
                if path.is_file()
            }
            if before != after:
                raise AssertionError("real learner state changed during copied-state gate")


class RetrospectiveRewards(unittest.TestCase):
    def test_prior_study_is_not_mastery_and_uses_all_eight_canonical_frames(self):
        cur = _curriculum()
        progress = _operator_progress(cur)
        rows = retro.retrospective_rewards(cur, progress)
        self.assertEqual([row["module_id"] for row in rows], ["M0", "M11"])
        for row in rows:
            self.assertEqual(row["status"], "prior_study")
            self.assertTrue(row["prior_study"])
            self.assertFalse(row["mastered"])
            self.assertEqual(len(row["animation"]["frames"]), 8)
            self.assertEqual(row["animation"]["source_ref"],
                             ("ascii-art-authoring §§1,9-10; curriculum M0 A1/V0"
                              if row["module_id"] == "M0"
                              else "ascii-art-authoring §§4.4,9h-10; curriculum M11 S0/V11"))

    def test_reward_pass_changes_only_classification(self):
        cur = _curriculum()
        progress = _operator_progress(cur)
        m0 = next(row for row in cur["modules"] if row["id"] == "M0")
        reward_id = (m0.get("module_reward") or {}).get("card_id", "M0.REWARD")
        mastered = dict(progress, passed_cards=list(progress["passed_cards"]) + [reward_id])
        row = next(row for row in retro.retrospective_rewards(cur, mastered)
                   if row["module_id"] == "M0")
        self.assertEqual(row["status"], "mastered")
        self.assertTrue(row["mastered"])
        self.assertFalse(retro.startup_rewards(cur, mastered)[0]["module_id"] == "M0")

    def test_gallery_exposes_read_only_complete_sequences(self):
        cur = _curriculum()
        progress = _operator_progress(cur)
        cfg = type("Cfg", (), {"state": str(REAL_STATE)})()
        gallery = runtime.completed_gallery(cfg, cur, progress)
        retro_rows = [row for row in gallery if row.get("kind") == "module_reward"]
        self.assertEqual([row["module_id"] for row in retro_rows], ["M0", "M11"])
        self.assertEqual([row["frames"] for row in retro_rows], [8, 8])
        self.assertTrue(all(row["status"] == "prior_study" for row in retro_rows))

    def test_real_gate_renderer_at_all_required_sizes(self):
        for columns, rows in ((80, 24), (100, 36), (188, 49)):
            with self.subTest(size=(columns, rows)):
                output = _run_gate_copy(columns, rows)
                self.assertIn("RETROSPECTIVE MODULE REWARDS", output)
                self.assertIn("M0", output)
                self.assertIn("M11", output)
                for index in range(1, 9):
                    self.assertRegex(output, r"pose %02d %d/8" % (index, index))
                self.assertIn("No v2 lesson due", output)
                self.assertIn("module reward · authored original · not learner output", output)
                # Match actual canonical rows, not only changing frame labels.
                for module_id in ("M0", "M11"):
                    for frame in retro._animation_for(module_id)["frames"]:
                        self.assertIn("\r\n".join("    " + row for row in frame), output)

    def test_hourly_popup_entry_reaches_catch_up(self):
        output = _run_gate_copy(80, 24, "--if-due")
        self.assertIn("RETROSPECTIVE MODULE REWARDS", output)
        self.assertIn("pose 08 8/8", output)

    def test_all_passed_module_endcaps_have_canonical_gallery_reward(self):
        cur = _curriculum()
        progress = {"passed_cards": [module["id"] + ".REWARD" for module in cur["modules"]]}
        rewards = retro.gallery_rewards(cur, progress)
        self.assertEqual(len(rewards), len(cur["modules"]))
        self.assertTrue(all(row["mastered"] and len(row["animation"]["frames"]) == 8
                            for row in rewards))


if __name__ == "__main__":
    unittest.main()
