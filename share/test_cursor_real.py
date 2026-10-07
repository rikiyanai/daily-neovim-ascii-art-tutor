"""Actual clean Neovim PTY receipt controls; no real learner state."""
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import pty
import select
import struct
import subprocess
import sys
import tempfile
import termios
import time
import fcntl

import v2_runtime as R

HERE = Path(__file__).resolve().parent
loader = importlib.machinery.SourceFileLoader("cursor_real_gate", str(HERE.parent / "bin/vim-daily-gate"))
spec = importlib.util.spec_from_loader(loader.name, loader)
G = importlib.util.module_from_spec(spec)
loader.exec_module(G)

if "--child" in sys.argv:
    art, keylog, brief = sys.argv[2:5]
    G.run_editor(art, 1, "^", keylog, brief, "isolated cursor receipt control", "follow the fixture")
    raise SystemExit(0)

cur = json.loads((HERE / "curriculum-v2.json").read_text())
cards = {c["id"]: c for c in cur["cards"]}
cases = [("M0.L0", b"j0:qa!\r", True),
         ("M0.L0", b"j0:wq\r", True),
         ("M0.L0", b":write !true j0\r:q!\r", False),
         ("M0.L0", b"jjk0:wq\r", True),
         # Leave the art window, return and move again: the final snapshot
         # must supersede the prior correct position instead of self-crediting.
         ("M0.L0", b"j0\x17w\x17wl:qa!\r", False),
         ("M0.F0", b"j0f*:wq\r", True),
         # Exact cursor/art cannot launder fX plus r* into a fictitious f*.
         ("M0.F0", b"j0fX5lr*:wq\r", False),
         # Virtual cursor offset must survive :wq; byte position alone is
         # not display column 12 on this nine-character ragged row.
         ("M11.COL", b":set virtualedit=all\r2G12|:wq\r", True),
         ("M11.COL", b"2G$:wq\r", False),
         ("M11.COL", b":set virtualedit=all\r2G011l:wq\r", False)]
if "--direct" in sys.argv:
    cases = cases[:1]
if "--wide" in sys.argv:
    wide = dict(cards["M0.L0"], start=["  /", "　⌒ヽ"], target=["  /", "　⌒ヽ"],
                expected="j0fヽ", cursor_goal={"row": 2, "column": 5},
                method_requirement={"exact_any_of": ["j0fヽ"]})
    cards["WIDE"] = wide
    cases = [("WIDE", "j0fヽ".encode() + b"\x17w:qa!\r", True)]
for cid, keys, wanted in cases:
    with tempfile.TemporaryDirectory(prefix="vim-daily-cursor-real-") as directory:
        root = Path(directory)
        art, keylog, brief = root / "art.txt", root / "keys.log", root / "brief.txt"
        card = cards[cid]
        art.write_text("\n".join(card["start"]) + "\n", encoding="utf-8")
        brief.write_text("PROGRESS\nDO THIS\nTARGET\n── MORE\n", encoding="utf-8")
        master, slave = pty.openpty()
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 36, 100, 0, 0))
        try:
            with R._CursorReceiptEnv(art, keylog, 1) as owner:
                env = dict(os.environ, TERM="xterm-256color", VIM_DAILY_CLEAN="1", VIM_DAILY_USE_USER_CONFIG="0")
                for name in list(env):
                    if name == "TMUX" or name.startswith("VIM_DAILY_TMUX_"):
                        env.pop(name)
                child = subprocess.Popen([sys.executable, __file__, "--child", str(art), str(keylog), str(brief)], stdin=slave, stdout=slave, stderr=slave, env=env)
                seen = bytearray()
                deadline = time.monotonic() + 8
                while b"SWITCHES PANE" not in seen and time.monotonic() < deadline:
                    if select.select([master], [], [], 0.1)[0]:
                        seen.extend(os.read(master, 65536))
                assert b"SWITCHES PANE" in seen, seen[-1500:]
                # Wait for the editor's bounded late placement, not a job poll.
                select.select([], [], [], 0.4)
                os.write(master, keys)
                deadline = time.monotonic() + 8
                while child.poll() is None and time.monotonic() < deadline:
                    if select.select([master], [], [], 0.1)[0]:
                        seen.extend(os.read(master, 65536))
                assert child.poll() == 0, seen[-1500:]
                receipt = R._read_cursor_receipt(owner.receipt, owner.token, art)
                assert receipt and receipt["event"] == "VimLeavePre", (owner.receipt.exists(), owner.receipt.read_text() if owner.receipt.exists() else "missing receipt", seen[-500:])
                decoded = G.decode_keylog(keylog.read_bytes())
                replay = {"actual_tokens": R._without_brief_navigation(decoded), "cursor_receipt": receipt}
                passed = not R._required_method_error(type("Cfg", (), {"tokenize": staticmethod(G.tokenize)})(), card, replay) and not R._cursor_goal_error(card, replay)
                assert passed == wanted, (cid, decoded, receipt, wanted)
                assert art.read_text() == "\n".join(card["target"]) + "\n"
                print("PASS actual Neovim cursor", cid, "credit" if passed else "denied", receipt["cursor"], receipt["display_column"])
        finally:
            if "child" in locals() and child.poll() is None:
                child.terminate()
                child.wait(timeout=3)
            os.close(slave)
            os.close(master)
