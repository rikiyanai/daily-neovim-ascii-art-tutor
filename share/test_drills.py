#!/usr/bin/env python3
"""Drive every drill through a real nvim, typing exactly the recipe.

Falsifier: if the documented keystrokes do not produce the documented target,
the drill is unpassable and must not ship.
"""
import importlib.util, os, re, subprocess, sys, tempfile

spec = importlib.util.spec_from_loader(
    "gate", importlib.machinery.SourceFileLoader("gate", os.path.expanduser("~/.local/bin/vim-daily-gate")))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

SPECIAL = {"<Esc>": b"\x1b", "<CR>": b"\r", "<NL>": b"\n", "<Tab>": b"\t", "<BS>": b"\x7f"}

def to_bytes(specstr):
    out = b""
    for t in gate.tokenize(specstr):
        if t in SPECIAL:
            out += SPECIAL[t]
        elif re.fullmatch(r"<C-([A-Za-z])>", t):
            out += bytes([ord(re.fullmatch(r"<C-([A-Za-z])>", t).group(1).lower()) - 0x60])
        else:
            out += t.encode()
    return out

USE_REAL_CONFIG = "--real" in sys.argv
cur = gate.load_curriculum()
fails = []
for d in cur["drills"]:
    tmp = tempfile.mkdtemp()
    lesson = os.path.join(tmp, "lesson.txt")
    start = gate.write_lesson(lesson, d, cur["concepts"][d["concept"]], "Concept: x")
    script = os.path.join(tmp, "in.bin")
    with open(script, "wb") as f:
        f.write(to_bytes(d["expected"]))
    keylog = os.path.join(tmp, "keys.log")
    cmd = ["nvim"]
    if not USE_REAL_CONFIG:
        cmd += ["-u", "NONE", "-i", "NONE"]
    cmd += ["+lua " + gate.NOPAIRS, "+%d" % start, "+normal! " + d.get("cursor", "^"),
            "-s", script, "-w", keylog, lesson]
    subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    env=dict(os.environ, VIM_DAILY_ACTIVE="1"))
    region = gate.read_region(lesson)
    ok = gate.matches(region, d["target"])
    # keylog must also round-trip back to the same tokens
    raw = open(keylog, "rb").read() if os.path.exists(keylog) else b""
    rt = gate.decode_keylog(raw)
    rt_ok = gate.strip_save_tail(rt) == gate.strip_save_tail(gate.tokenize(d["expected"]))
    print("%-4s %-24s keys=%-28s %s%s" % (
        "PASS" if ok else "FAIL", d["title"], d["expected"],
        "" if ok else "  got=%r want=%r" % (region, d["target"]),
        "" if rt_ok else "   [keylog roundtrip differs: %r]" % (rt,)))
    if not ok:
        fails.append(d["id"])
print("\n%d/%d drills passable (config=%s)" % (
    len(cur["drills"]) - len(fails), len(cur["drills"]), "real" if USE_REAL_CONFIG else "none"))
sys.exit(1 if fails else 0)
