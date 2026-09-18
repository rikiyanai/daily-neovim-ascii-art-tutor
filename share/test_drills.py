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

# The glyph alphabet, from the ascii-art-authoring skill sections 4.1 and 4.2 and
# the Stone Story tutorial plate 03. A drill whose art uses a glyph outside this
# set is a sourcing bug: schema v1 shipped `*` (not in any row) and `#`, which is
# the TRANSPARENCY character, used as ink.
BASIC     = set("`~!^()-_+=;:'\",.\\/|<>[]{}")
EXTENDED  = set("\u00b4\u203e\u00a1\u00b7")
ALNUM     = set("oOvVTL7UcCxX")
BOXDRAW   = set("\u2500\u2502\u250c\u2510\u2514\u2518\u252c\u2534\u251c\u2524\u253c"
                "\u2550\u2555\u2552\u255b\u2558\u2564\u2565\u2568")
PLATE_OBS = set("\u221e\u00af\u2022")  # observed in the plates: the adept's staff, the
                                   # macron typed where the alphabet specifies \u203e,
                                   # and the bullet used in the particle layer
ALLOWED = BASIC | EXTENDED | ALNUM | BOXDRAW | PLATE_OBS | {" "}


def glyph_violations(d):
    if d.get("labels"):          # buffer carries deliberate prose labels
        return []
    bad = []
    for line in d["start"] + d["target"]:
        # TODO is the edit placeholder the drill replaces; it is never art, and
        # it can sit inside a shape (drill `pairs` starts as "(TODO)").
        for ch in line.replace("TODO", ""):
            if ch not in ALLOWED:
                bad.append(ch)
    return sorted(set(bad))


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
    bad = glyph_violations(d)
    problems = []
    if bad:
        problems.append("GLYPH %r not in the alphabet" % (bad,))
    if not d.get("source"):
        problems.append("no source field")
    if not d.get("tutor"):
        problems.append("no tutor node")
    # SHORT gate: these fire hourly. A drill you dread is a drill you skip.
    nkeys = len(gate.strip_save_tail(gate.tokenize(d["expected"])))
    if nkeys > 16:
        problems.append("TOO LONG: %d keystrokes (max 16)" % nkeys)
    if d.get("seconds", 0) > 75:
        problems.append("TOO SLOW: %ds (max 75)" % d["seconds"])
    if len(d["start"]) > 8 or len(d["target"]) > 20:
        problems.append("TOO BIG: %d start rows, %d target rows" % (len(d["start"]), len(d["target"])))
    for pr in problems:
        print("     %s: %s" % (d["id"], pr))
    if not ok or problems:
        fails.append(d["id"])
print("\n%d/%d drills passable (config=%s)" % (
    len(cur["drills"]) - len(fails), len(cur["drills"]), "real" if USE_REAL_CONFIG else "none"))
sys.exit(1 if fails else 0)
