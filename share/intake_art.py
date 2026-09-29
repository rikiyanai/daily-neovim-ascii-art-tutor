#!/usr/bin/env python3
"""Intake downloaded ASCII art into share/art.json.

A download file (e.g. ~/Downloads/ant.txt) usually holds several pictures
separated by blank lines, plus author signature tags. This tool lists the
blocks with a glyph report, then appends a chosen block as an art entry.

Usage:
  intake_art.py FILE
      list blank-line-delimited blocks: rows, width, glyph violations,
      alphanumeric-only lines (usually signature tags to trim).
  intake_art.py FILE --key KEY --block N --source "..." --author "..."
      --license "..." --permission "..." --redistribution STATUS
      [--strip-prefix STR] [--drop-last N]
      append block N as art.json entry KEY. --strip-prefix removes STR from
      the start of every row that has it (signature tags sit after the art's
      own indent, so matching skips leading whitespace). --drop-last drops N
      trailing rows (trailing signature lines).
Glyph alphabet is owned by share/test_drills.py; the sets below mirror it.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ART_JSON = os.path.join(HERE, "art.json")
ART_JSON = os.environ.get("VIM_DAILY_ART_JSON", DEFAULT_ART_JSON)

BASIC = set("`~!^()-_+=;:'\",.\\/|<>[]{}")
EXTENDED = set("´‾¡·")
ALNUM = set("oOvVTL7UcCxX")
BOXDRAW = set("─│┌┐└┘┬┴├┤┼"
              "═╕╒╛╘╤╥╧")
PLATE_OBS = set("∞¯•")
ALLOWED = BASIC | EXTENDED | ALNUM | BOXDRAW | PLATE_OBS | {" "}


def blocks(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read().split("\n")
    out, cur = [], []
    for line in raw + [""]:
        if line.strip():
            cur.append(line.rstrip("\n"))
        elif cur:
            out.append(cur)
            cur = []
    return out


def report(rows):
    bad = sorted({ch for line in rows for ch in line if ch not in ALLOWED})
    siggy = [i for i, line in enumerate(rows)
             if line.strip() and all(ch not in ALLOWED or ch in ALNUM or ch == " "
                                     for ch in line.strip()) and any(ch.isalpha() for ch in line)]
    width = max((len(l) for l in rows), default=0)
    return bad, siggy, width


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    path = argv[1]
    blks = blocks(path)
    rest = argv[2:]
    if "--key" not in rest:
        for i, b in enumerate(blks):
            bad, siggy, width = report(b)
            print("block %d: %d rows, width %d" % (i, len(b), width))
            for r in b:
                print("    |" + r)
            if bad:
                print("    GLYPH violations: %r" % (bad,))
            if siggy:
                print("    ALNUM-only lines (signature?): %s" % (siggy,))
        print("\n%d blocks. Append one with: --key KEY --block N --source \"...\"" % len(blks))
        return 0
    key = rest[rest.index("--key") + 1]
    blk = int(rest[rest.index("--block") + 1])
    required = ("--source", "--author", "--license", "--permission", "--redistribution")
    missing = [flag for flag in required if flag not in rest]
    if missing:
        print("refusing: rights metadata is required: %s" % ", ".join(missing))
        return 1
    source = rest[rest.index("--source") + 1]
    author = rest[rest.index("--author") + 1]
    license_name = rest[rest.index("--license") + 1]
    permission = rest[rest.index("--permission") + 1]
    redistribution = rest[rest.index("--redistribution") + 1]
    if redistribution not in ("cleared", "private-only", "unverified"):
        print("refusing: --redistribution must be cleared, private-only, or unverified")
        return 1
    if redistribution != "cleared" and os.path.abspath(ART_JSON) == os.path.abspath(DEFAULT_ART_JSON):
        print("refusing: %s art cannot be added to the repository library; "
              "set VIM_DAILY_ART_JSON to a private library path" % redistribution)
        return 1
    prefix = rest[rest.index("--strip-prefix") + 1] if "--strip-prefix" in rest else ""
    drop_last = int(rest[rest.index("--drop-last") + 1]) if "--drop-last" in rest else 0
    rows = list(blks[blk])
    if drop_last:
        rows = rows[:-drop_last]
    if prefix:
        # Signature tags sit after the art's own indent ("   jgs      \_!_/"),
        # so match past leading whitespace and keep the indent.
        stripped = []
        for r in rows:
            s = r.lstrip()
            if s.startswith(prefix):
                stripped.append(r[:len(r) - len(s)] + s[len(prefix):])
            else:
                stripped.append(r)
        rows = stripped
    bad, siggy, _ = report(rows)
    if bad:
        print("refusing: glyph violations %r (trim the block first)" % (bad,))
        return 1
    if len(rows) > 8:
        print("refusing: %d rows (drill start rows max 8; excerpt a piece)" % len(rows))
        return 1
    art = json.load(open(ART_JSON, encoding="utf-8"))
    if key in art["art"] and "--force" not in rest:
        print("refusing: key %r exists (pass --force to overwrite)" % key)
        return 1
    art["schema"] = "vim-daily/art@2"
    art["art"][key] = {
        "rows": rows,
        "source": source,
        "origin": {"kind": "user_download", "path": os.path.abspath(os.path.expanduser(path))},
        "author": author,
        "license": license_name,
        "permission": permission,
        "redistribution": redistribution,
    }
    with open(ART_JSON, "w", encoding="utf-8") as f:
        json.dump(art, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print("added %s: %d rows (siggy lines: %s)" % (key, len(rows), siggy or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
