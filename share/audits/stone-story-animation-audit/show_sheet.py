"""Print a Stone Story sheet's frames with `#` shown as space: show_sheet.py official-Pets/Frog res01 [res02 ...]"""
import sys
from pathlib import Path
root = Path("~/Downloads/stone-story-consolidated").expanduser() / sys.argv[1]
for res in sys.argv[2:]:
    frames = (root / (res + ".txt")).read_text(encoding="utf-8").split("%%\n")
    for i, f in enumerate(frames, 1):
        print("--- %s f%d" % (res, i))
        for line in f.rstrip("\n").split("\n"):
            print(repr(line.replace("#", " ").rstrip()))
