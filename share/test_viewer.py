"""VD-62: post-completion animation viewer."""
import io
import json
import os
import pty
import re
import select
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import viewer as V  # noqa: E402

cur = json.loads((HERE / "curriculum-v2.json").read_text(encoding="utf-8"))
cards = {c["id"]: c for c in cur["cards"]}

# A multi-frame lesson plays its own frames, split by frame_slices.
multi = next(c for c in cur["cards"] if len(c.get("frame_slices") or []) > 2)
view = V.lesson_view(multi, multi["target"])
assert len(view.frames) == len(multi["frame_slices"]), multi["id"]
assert view.kind == "lesson" and view.labels[0] == "frame 1"
# Equal neighbours are marked as holds.
held = V.View("t", [["ab"], ["ab"], ["ac"]])
assert V.lesson_view({"id": "X", "frame_slices": [1, 1, 1]}, ["ab", "ab", "ac"]).holds == {1: "hold"}
del held

# A one-frame still plays as a BEFORE -> YOURS flip.
still = cards["M0.01"]
view = V.lesson_view(still, still["target"])
assert view.kind == "edit" and view.labels == ["before", "yours"], view.labels
assert view.frames[0] == [r.rstrip() for r in still["start"]]

# Changed cells: only the edited glyph lights up; a cleared cell is marked.
assert V._changed(["-—*—-"], ["-—o—-"]) == {(0, 2)}
assert V._changed(["ab  x"], ["ab"]) == {(0, 2)}
plain = V.Style(False)
assert V.render_frame(["-—o—-"], ["-—*—-"], plain, diff=True) == ["-—o—-"]
onion = V.render_frame(["a  "], ["a b"], plain, onion=True)
assert onion == ["a ·"], onion  # previous frame shows through, no colour
colour = V.Style(True)
assert "\033[1;32mo" in V.render_frame(["-—o—-"], ["-—*—-"], colour, diff=True)[0]

# Filmstrip: all frames side by side, current marked; None when too wide.
strip = V.filmstrip(V.View("t", [["ab"], ["cd"]]), 1, plain, 80)
assert strip[-1].split() == ["frame", "1", "▲", "frame", "2"], strip
assert V.filmstrip(V.View("t", [["x" * 50], ["y" * 50]]), 0, plain, 80) is None
# Wide (East Asian) glyphs count as two cells.
assert V.cell_width("ヽア") == 4

# Static output for pipes: one filmstrip, no escape codes.
buf = io.StringIO()
V.static_print(V.lesson_view(still, still["target"]), out=buf)
text = buf.getvalue()
assert text.startswith("WATCH YOUR WORK  M0.01") and "\033" not in text, text
assert "▲ yours" in text

# Off switch.
os.environ["VIM_DAILY_VIEWER"] = "off"
assert not V.enabled()
del os.environ["VIM_DAILY_VIEWER"]
assert V.enabled()
print("ok viewer model: frames, holds, before->yours, changed cells, onion, filmstrip")

# Interactive run in a real pseudo-terminal: it draws, pauses, steps, toggles
# onion skin, and Enter returns with the terminal restored.
script = r'''
import sys, json
sys.path.insert(0, %r)
import viewer as V
view = V.View("M12.04 · test", [["\\..!..", " \\.:.."], ["\\..!..", " \\.!.."], ["\\..!..", " \\.!.."]],
              holds={2: "hold"})
print("RESULT", json.dumps(V.play([view])))
''' % str(HERE)
pid, fd = pty.fork()
if pid == 0:
    env = dict(os.environ, TERM="xterm-256color", COLUMNS="80", LINES="24")
    os.execvpe(sys.executable, [sys.executable, "-c", script], env)
out = b""


def pump(seconds):
    global out
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        ready, _, _ = select.select([fd], [], [], 0.05)
        if ready:
            try:
                out += os.read(fd, 65536)
            except OSError:
                return


pump(1.2)                     # plays at least one frame change
os.write(fd, b" ")            # pause
pump(0.3)
os.write(fd, b"l")            # step
pump(0.3)
os.write(fd, b"o")            # onion on
pump(0.3)
os.write(fd, b"\r")           # continue
pump(1.0)
os.waitpid(pid, 0)
screen = out.decode("utf-8", "replace")
for needle in ("WATCH YOUR WORK", "▶ playing", "❚❚ paused", "o\x1b[0m onion on",
               "HOLD", "Enter\x1b[0m continue", "\x1b[?1049h", "\x1b[?1049l"):
    assert needle in screen, (needle, screen[-800:])
result = json.loads(re.search(r"RESULT (\{.*\})", screen).group(1))
assert result["shown"] and result["interactive"], result
print("ok viewer pty: plays, pauses, steps, onion toggle, Enter returns, screen restored")

# Gate: --view on an empty state explains itself instead of crashing.
import tempfile  # noqa: E402
with tempfile.TemporaryDirectory() as root:
    env = dict(os.environ, XDG_STATE_HOME=root, VIM_DAILY_SKIP="1")
    run = subprocess.run([sys.executable, str(HERE.parent / "bin" / "vim-daily-gate"), "--view"],
                         capture_output=True, text=True, env=env, timeout=60,
                         stdin=subprocess.DEVNULL)
    assert "nothing to watch yet" in run.stdout, (run.stdout, run.stderr)
# VD-63: the gallery replays every passed lesson from its own checkpoints,
# even after later lessons overwrote the project strip.
sys.path.insert(0, str(HERE))
import v2_runtime as v2  # noqa: E402
from types import SimpleNamespace  # noqa: E402
with tempfile.TemporaryDirectory() as root:
    cfg = SimpleNamespace(state=root)
    card = cards["M0.05"]
    ck = Path(root) / "projects" / "old-folder-name" / "checkpoints"
    ck.mkdir(parents=True)
    (ck / "M0.05-before.txt").write_text("\n".join(card["start"]) + "\n", encoding="utf-8")
    (ck / "M0.05-after.txt").write_text("\n".join(card["target"]) + "\n", encoding="utf-8")
    (ck / "M0.99-after.txt").write_text("x\n", encoding="utf-8")  # unknown lesson: ignored
    progress = {"passed_cards": ["M0.05"]}
    gallery = v2.completed_gallery(cfg, cur, progress)
    assert [g["card_id"] for g in gallery] == ["M0.05"], gallery
    assert gallery[0]["frames"] == len(card["frame_slices"]) and gallery[0]["kind"] == "lesson"
    assert v2.completed_gallery(cfg, cur, {"passed_cards": []}) == []  # not passed: hidden
print("ok gallery: passed lessons from checkpoints; unknown or unpassed lessons hidden")
print("PASS viewer")
