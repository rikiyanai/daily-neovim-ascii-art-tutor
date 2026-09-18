#!/usr/bin/env python3
"""Extract the art library from the Stone Story ASCII tutorial plates.

Run this only when re-deriving art.json. The plates are NOT redistributed in
this repo; art.json holds short excerpts (attributed in README) and is what the
curriculum generator actually reads, so the repo stays self-contained.

Usage: extract_art.py /path/to/ascii-tutorial-page
"""
import json, os, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/Downloads/asciicker-Y9-2/articles/2026-09-07-stone-story-video-transcripts-media/"
    "o5v-NS9o4yc/ascii-tutorial-page")

def lines(path):
    return [l.replace("\t", "") for l in open(os.path.join(SRC, path), encoding="utf-8").read().split("\n")]

def grab(path, a, b, dedent=True):
    rows = [l.rstrip() for l in lines(path)[a-1:b]]
    if dedent:
        pad = min((len(r) - len(r.lstrip(" ")) for r in rows if r.strip()), default=0)
        rows = [r[pad:] for r in rows]
    return rows

P2, P6, P3, P4, P5, P1 = ("02-poison-adept-walk-cycle.txt", "06-animation-subtractive.txt",
                          "03-styles-fonts-alphabet.txt", "04-lines-materials-antialiasing.txt",
                          "05-depth-dithering-shadows.txt", "01-sacrificial-pit-layers.txt")
PLATE = "Stone Story RPG ASCII tutorial page (stonestoryrpg.com/ascii_tutorial.html)"
art = {}
def add(key, rows, src):
    art[key] = {"rows": rows, "source": src}

# --- plate 02: Poison Adept walk cycle, 10 frames of 6 rows ---------------
for i in range(10):
    add("walk%d" % (i + 1), grab(P2, 4 + i * 6, 9 + i * 6, dedent=False),
        PLATE + " plate 02, Poison Adept walk cycle, frame %d of 10" % (i + 1))

# --- plate 06: subtractive pyramid, 7 frames ------------------------------
PYR = [(27, 34), (37, 44), (47, 53), (56, 62), (65, 70), (73, 78), (81, 85)]
for i, (a, b) in enumerate(PYR):
    add("pyr%d" % (i + 1), grab(P6, a, b),
        PLATE + " plate 06 section 13, subtractive-animation pyramid, frame %d of 7" % (i + 1))
add("pyr_apexes", [grab(P6, a, a, dedent=False)[0] for a, _ in PYR[:5]],
    PLATE + " plate 06, apex rows of pyramid frames 1 to 5")

# --- plate 03: the same lamp in four styles -------------------------------
add("lamp_block",  grab(P3, 3, 6),  PLATE + " plate 03, Block style")
add("lamp_filled", grab(P3, 8, 12), PLATE + " plate 03, Filled style")
add("lamp_line",   [r.replace("    Line", "") .rstrip() for r in grab(P3, 13, 16)],
    PLATE + " plate 03, Line style")
add("lamp_box",    grab(P3, 17, 21), PLATE + " plate 03, Box Drawing style")
add("alphabet_ext", ["´ ‾ ¡ ·"], PLATE + " plate 03 section 5, the four extended glyphs")

# --- plate 04: line runs and anti-aliasing --------------------------------
add("run_steep",   grab(P4, 3, 5),   PLATE + " plate 04 section 6, the steep diagonal run")
add("run_shallow", grab(P4, 6, 8),   PLATE + " plate 04 section 6, a shallower run using ,´")
add("run_period",  grab(P4, 9, 11),  PLATE + " plate 04 section 6, the .´ run")
add("run_under",   grab(P4, 12, 14), PLATE + " plate 04 section 6, the _/ run")
add("run_stair",   grab(P4, 15, 16), PLATE + " plate 04 section 6, the classic _.-´ stair-step")
add("run_long",    grab(P4, 17, 18), PLATE + " plate 04 section 6, a long shallow run")
add("run_flat",    grab(P4, 19, 20), PLATE + " plate 04 section 6, the flattest run")
add("aa_ramp",     grab(P4, 32, 36), PLATE + " plate 04 section 7, anti-aliasing of near-vertical lines")

# --- plate 05: depth, dithering, shadows ----------------------------------
add("seam_joined", grab(P5, 3, 8)[:6], PLATE + " plate 05 section 9, two forms sharing a seam glyph")
add("dither_top",  grab(P5, 30, 34),   PLATE + " plate 05 section 10, the dithered sphere, upper band")
add("dither_low",  grab(P5, 43, 45),   PLATE + " plate 05 section 10, the dithered sphere, lower band")
add("shadow_gnd",  grab(P5, 62, 67),   PLATE + " plate 05 section 11, hatched ground under a figure")

# --- plate 01: small sprites and particle frames --------------------------
blocks, cur = [], []
for l in lines(P1):
    t = l.rstrip()
    if t.strip():
        cur.append(t)
    else:
        if cur:
            blocks.append(cur)
        cur = []
if cur:
    blocks.append(cur)

def dedent(rows):
    pad = min((len(r) - len(r.lstrip(" ")) for r in rows if r.strip()), default=0)
    return [r[pad:].rstrip() for r in rows]

hands, sparks = [], []
for b in blocks:
    if not (2 <= len(b) <= 6):
        continue
    d = dedent(b)
    if max((len(x) for x in d), default=99) > 14:
        continue
    if any("(" in x or ")" in x for x in d) and len(d) == 4:
        hands.append(d)
    elif all(len(x) <= 2 for x in d):
        sparks.append(d)
for i, h in enumerate(hands[:5]):
    add("hand%d" % (i + 1), h, PLATE + " plate 01, hand/arm layer frame %d" % (i + 1))
for i, s in enumerate(sparks[:6]):
    add("spark%d" % (i + 1), s, PLATE + " plate 01, particle layer frame %d" % (i + 1))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "art.json")
json.dump({"schema": "vim-daily/art@1",
           "attribution": "Excerpts from the Stone Story RPG ASCII tutorial page by "
                          "Gabriel Santos, Martian Rex, Inc. Used as practice material.",
           "art": art}, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("wrote %s: %d entries" % (out, len(art)))
for k in sorted(art):
    print("  %-14s %d rows" % (k, len(art[k]["rows"])))
