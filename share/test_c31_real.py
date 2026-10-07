"""C31 actual Neovim/gate grade controls in isolated learner state.

The parent sends actual keys over the PTY. The gate owns artifact creation,
cursor receipt, keylog decoding, questions, grading and event publication.
No correct target, keylog, cursor receipt or passing event is injected.
"""
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

import v2_runtime as R

HERE = Path(__file__).resolve().parent
CUR = json.loads((HERE / "curriculum-v2.json").read_text())
CARDS = {card["id"]: card for card in CUR["cards"]}
loader = importlib.machinery.SourceFileLoader("c31_real_gate", str(HERE.parent / "bin/vim-daily-gate"))
spec = importlib.util.spec_from_loader(loader.name, loader)
G = importlib.util.module_from_spec(spec)
loader.exec_module(G)

if "--child" in sys.argv:
    state, card_id = sys.argv[2:4]
    cfg = R.RuntimeConfig(
        state=state, share=str(HERE), editor="nvim", max_tries=1,
        target=12, cooldown=0, stamp=str(Path(state) / "stamp"),
        run_editor=G.run_editor, decode_keylog=G.decode_keylog,
        hold_open=lambda: None, colours=("", "", "", "", "", ""),
        tokenize=G.tokenize,
        question_answer=lambda question: "abcd"[question["correct_choice"]],
    )
    progress = R.project(CUR, [])
    result = R.run_edit(cfg, CUR, progress, CARDS[card_id])
    print("C31 ACTUAL RESULT", result, flush=True)
    raise SystemExit(0)

cases = [
    ("M6.DDPH", b"ggddp", True, True),
    # Exact target via Ex cannot turn literal Insert text into Normal dd/p.
    ("M6.DDPH", b":1m2\r:startinsert\rddp\x1bu", False, True),
    ("M11.GP", b"g+0fOr-", True, True),
    ("M11.GP", b"0fOr-", False, True),
    ("M11.GP", b"ig+\x1bu0fOr-", False, True),
    ("M11.GP", b"1G:s/O/=/g\ru1G:s/O/-/g\rVg+\x1b", False, True),
    ("M3.06", b'ggV5j"ayG"ap9G0forO', True, True),
    ("M15.ZP", b"gg0\x162j9|zy4G2|zp", True, True),
    ("M2.DWH", b"1Gfodw", True, True),
    ("M18.05", b"4G$r1G$r1", True, True),
    ("M18.05", b":4\r$r1:8\r$r1", True, True),
    ("M14.01", b'f*"aylR\x1bi\x12a\x1buj0for*', False, True),
    ("M11.BR", b"2G:s/=/o/g\r2G0forO0vu", False, True),
    ("M11.ER", b"2G:s/:/::/g\r0v:earlier 1\rg+", False, True),
]
for card_id, keys, wanted_pass, wanted_target in cases:
    with tempfile.TemporaryDirectory(prefix="vim-daily-c31-real-") as directory:
        state = Path(directory)
        env = dict(os.environ, TERM="xterm-256color", VIM_DAILY_CLEAN="1",
                   VIM_DAILY_USE_USER_CONFIG="0", VIM_DAILY_TEXTUAL="0",
                   VIM_DAILY_VIEWER="off")
        for name in list(env):
            if name == "TMUX" or name.startswith("VIM_DAILY_TMUX_"):
                env.pop(name)
        master, slave = pty.openpty()
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 36, 100, 0, 0))
        child = subprocess.Popen([sys.executable, __file__, "--child", str(state), card_id],
                                 stdin=slave, stdout=slave, stderr=slave, env=env)
        raw = bytearray()
        def receive_until(predicate, label):
            deadline = time.monotonic() + 12
            while time.monotonic() < deadline:
                if select.select([master], [], [], 0.05)[0]:
                    raw.extend(os.read(master, 65536))
                if predicate():
                    return
                if child.poll() is not None:
                    break
            raise AssertionError((card_id, label, child.poll(), bytes(raw[-2500:])))
        try:
            receive_until(lambda: b"SWITCHES PANE" in raw, "actual editor mount")
            select.select([], [], [], 0.4)
            os.write(master, keys + b":wq\r")
            receive_until(lambda: b"C31 ACTUAL RESULT" in raw, "actual gate result")
            child.wait(timeout=3)
            events = R.read_events(type("State", (), {"state": str(state)})())
            attempts = [event for event in events if event.get("type") == "card"
                        and event.get("card_id") == card_id]
            receipt = (json.loads(Path(attempts[-1]["input_receipt"]).read_text())
                       if attempts and attempts[-1].get("input_receipt") else {})
            assert attempts and (attempts[-1]["result"] == "pass") == wanted_pass, (
                card_id, attempts, receipt.get("input"), raw[-1500:])
            assert attempts[-1]["curriculum_revision"] == CUR["revision"], attempts[-1]
            assert len(attempts[-1]["curriculum_contract_sha256"]) == 64, attempts[-1]
            contract = json.loads(Path(attempts[-1]["attempt_contract"]).read_text())
            assert contract["curriculum_revision"] == CUR["revision"]
            assert contract["card"]["target"] == CARDS[card_id]["target"]
            recovered = R._recovery_input_receipt(
                attempts[-1]["keylog"], Path(attempts[-1]["artifact"]),
                contract["card"], contract["before"])
            assert recovered is not None, contract
            assert recovered["attempt"] == receipt["attempt"]
            if not wanted_pass and wanted_target:
                failed = next(state.glob("projects/**/checkpoints/*-failed-1.txt"))
                assert failed.read_text().splitlines() == CARDS[card_id]["target"]
                assert b"TARGET CORRECT" in raw and b"instant retry" in raw
                assert b"saved project did not match" not in raw
                assert attempts[-1]["reason"] == "missing-method-evidence"
            if wanted_pass:
                artifact = Path(attempts[-1]["artifact"])
                assert artifact.read_text().splitlines() == CARDS[card_id]["target"]
            print("PASS actual C31 grade", card_id, "pass" if wanted_pass else "target-correct/method-missing", keys)
        finally:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=3)
            os.close(slave)
            os.close(master)
