"""Real pre-mapping input receipts; isolated files, no learner progress."""
import fcntl
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
from types import SimpleNamespace

import v2_runtime as R

HERE = Path(__file__).resolve().parent
loader = importlib.machinery.SourceFileLoader("typed_input_gate", str(HERE.parent / "bin/vim-daily-gate"))
spec = importlib.util.spec_from_loader(loader.name, loader)
G = importlib.util.module_from_spec(spec)
loader.exec_module(G)
card = next(c for c in json.loads((HERE / "curriculum-v2.json").read_text())["cards"]
            if c["id"] == "M6.DDPH")
for clean in (True, False):
    with tempfile.TemporaryDirectory(prefix="vim-daily-typed-input-") as directory:
        root = Path(directory)
        art, keys, brief = root / "art.txt", root / "keys.log", root / "brief.txt"
        art.write_text("\n".join(card["start"]) + "\n")
        brief.write_text("PROGRESS M6.DDPH\nDO THIS\nTARGET\n── MORE\n")
        master, slave = pty.openpty()
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
        with R._CursorReceiptEnv(art, keys, 1) as owner:
            env = dict(os.environ, TERM="xterm-256color",
                       VIM_DAILY_CLEAN="1" if clean else "0",
                       VIM_DAILY_USE_USER_CONFIG="0" if clean else "1")
            for name in list(env):
                if name == "TMUX" or name.startswith("VIM_DAILY_TMUX_"):
                    env.pop(name)
            child = subprocess.Popen([sys.executable, str(HERE / "test_cursor_real.py"),
                                      "--child", str(art), str(keys), str(brief)],
                                     stdin=slave, stdout=slave, stderr=slave, env=env)
            raw = bytearray()
            try:
                deadline = time.monotonic() + 12
                while b"SWITCHES PANE" not in raw and time.monotonic() < deadline:
                    if select.select([master], [], [], .1)[0]:
                        raw.extend(os.read(master, 65536))
                assert b"SWITCHES PANE" in raw, raw[-1000:]
                select.select([], [], [], 1.5)
                for value in b"ggddpZZ":
                    os.write(master, bytes([value]))
                    select.select([], [], [], .12)
                while child.poll() is None and time.monotonic() < deadline:
                    if select.select([master], [], [], .1)[0]:
                        raw.extend(os.read(master, 65536))
                assert child.poll() == 0, raw[-1500:]
                receipt = R._read_cursor_receipt(owner.receipt, owner.token, art)
                assert receipt and receipt.get("input_schema") == "vim-daily/typed-input@1", (
                    owner.receipt.read_bytes() if owner.receipt.exists() else "missing",
                    keys.read_bytes().hex(), art.read_text(), raw[-2000:])
                tokens = R._typed_input_tokens(SimpleNamespace(decode_keylog=G.decode_keylog), receipt)
                assert ("normal", "dd") in R._method_commands(tokens), tokens
                assert ("normal", "p") in R._method_commands(tokens), tokens
                assert art.read_text().splitlines() == card["target"]
                print(json.dumps({"clean": clean, "scriptout": keys.read_bytes().hex(),
                                  "input": receipt["input"], "target_matches":
                                  art.read_text().splitlines() == card["target"]}), flush=True)
            finally:
                if child.poll() is None:
                    child.terminate()
                    child.wait(timeout=3)
                os.close(master)
                os.close(slave)
