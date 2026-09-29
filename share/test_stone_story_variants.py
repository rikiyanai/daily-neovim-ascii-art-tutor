"""VD-29: replay every stone_story_variants row in isolated Neovim (same command as test_v2).

Usage: python3 share/test_stone_story_variants.py
Prints one line per variant and exits non-zero on any mismatch.
"""
import subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stone_story_variants as ssv
from v2_runtime import _notation_bytes

bad = 0
for card_id, fields in ssv.REPLACEMENTS.items():
    for field, rows in fields.items():
        for i, v in enumerate(rows, 1):
            with tempfile.TemporaryDirectory() as tmp:
                art = Path(tmp) / "a.txt"; art.write_text("\n".join(v["start"]) + "\n", encoding="utf-8")
                script = Path(tmp) / "k.bin"; script.write_bytes(_notation_bytes(v["expected"] + ":wq<CR>"))
                subprocess.run(["nvim", "-u", "NONE", "-i", "NONE",
                                "+set noautoindent nosmartindent nocindent indentexpr=", "+1",
                                "+normal! " + v.get("cursor", "^"), "-s", str(script), str(art)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
                got = [l.rstrip() for l in art.read_text(encoding="utf-8").splitlines()]
            ok = got == [l.rstrip() for l in v["target"]]
            bad += not ok
            print("%s %s.%s[%d] %-18s %s" % ("PASS" if ok else "FAIL", card_id, field, i, v["expected"], v["source"]))
            if not ok:
                print("   got:", got)
import json, re
root = Path(ssv.SOURCE_ROOT).expanduser()
if root.is_dir():
    for card_id, fields in ssv.REPLACEMENTS.items():
        for rows in fields.values():
            for v in rows:
                sheet = re.match(r"(official-[A-Za-z]+/[A-Za-z]+) (res\d+)", v["source"])
                if not sheet or not (root / sheet.group(1) / (sheet.group(2) + ".txt")).is_file():
                    bad += 1
                    print("FAIL source sheet missing:", card_id, v["source"])
cur = json.loads((HERE / "curriculum-v2.json").read_text(encoding="utf-8"))
for card in cur["cards"]:
    for v in card.get("review_variants", []):
        if card["id"] in ssv.REPLACEMENTS and "source" not in v:
            bad += 1
            print("FAIL %s: curriculum-v2.json not regenerated with the replacement" % card["id"])
remaining = sum(1 for c in cur["cards"] for v in c.get("review_variants", [])
                if "source" not in v and len(v["start"]) == len(c["start"])
                and all(a[1:] == b[1:] for a, b in zip(c["start"], v["start"])))
print("remaining border-swap review variants (VD-29, not yet replaced):", remaining)
sys.exit(1 if bad else 0)
