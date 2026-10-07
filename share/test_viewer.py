"""VD-62: post-completion animation viewer."""
import io
import json
import os
import pty
import re
import select
import signal
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
assert V._changed(["ab  x"], ["ab"]) == {(0, 2), (0, 3), (0, 4)}
assert V._changed(["abc"], ["a c"]) == {(0, 1)}
assert V._changed(["a", "b"], ["a"]) == {(1, 0)}
assert V._changed(["ヽ\u3000"], ["ヽ"]) == {(0, 1)}
plain = V.Style(False)
assert V.render_frame(["-—o—-"], ["-—*—-"], plain, diff=True) == ["-—o—-"]
assert V.render_frame(["ab"], ["abcd"], plain, diff=True) == ["ab··"], "every deleted tail glyph is marked"
assert V.render_frame(["a"], ["a", "gone"], plain, diff=True) == ["a", "····"], "deleted rows are rendered"
assert V.render_frame(["ヽ"], ["ヽ\u3000"], plain, diff=True) == ["ヽ··"], "full-width whitespace is significant"
assert V.render_frame(["a  "], None, plain) == ["a  "], "canonical rows keep trailing spaces"
onion = V.render_frame(["a  "], ["a b"], plain, onion=True)
assert onion == ["a ·"], onion  # previous frame shows through, no colour
colour = V.Style(True)
assert colour.ok + "o" in V.render_frame(["-—o—-"], ["-—*—-"], colour, diff=True)[0]

# Whitespace-preserving cards keep exact before/yours rows and do not collapse
# a whitespace-only edit to one frame.  Legacy cards still trim for comparison.
probe = {"id": "probe", "start": ["ヽ_ノ\u3000 "],
         "preserve_trailing_whitespace": True}
preserved = V.lesson_view(probe, ["ヽ_ノ"])
assert preserved.labels == ["before", "yours"]
assert preserved.frames[0] == ["ヽ_ノ\u3000 "] and preserved.frames[1] == ["ヽ_ノ"]
legacy = V.lesson_view({"id": "legacy", "start": ["ヽ_ノ\u3000 "]}, ["ヽ_ノ"])
assert legacy.labels == ["yours"]

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
# Lesson art stays raw even when UI labels have colour.  The explicit diff and
# onion overlays remain opt-in diagnostics; a normal filmstrip does not bold
# or dim its glyph rows.
colour_strip = V.filmstrip(V.View("t", [["ab"], ["cd"]]), 1, V.Style(True), 80)
assert "\033[1mab" not in colour_strip[0] and "\033[2mab" not in colour_strip[0]

# Celebration rewards are a UI-only art path.  Static fallbacks retain every
# source credit, never emit SGR, and do not enter an alternate screen.
rewards = [
    {"title": "First step", "art": [" /\\ ", "/__\\"],
     "credit": "Art: original to this tutor", "kind": "badge"},
    {"title": "Level up", "art": ["<+>"],
     "credit": "Art: Stone Story RPG by Gabriel Santos (Martian Rex, Inc.)",
     "kind": "level"},
]
saved_env = {key: os.environ.get(key) for key in ("NO_COLOR", "TERM", "VIM_DAILY_ANIM", "VIM_DAILY_VIEWER")}
try:
    os.environ.pop("NO_COLOR", None)
    os.environ["TERM"] = "xterm-256color"
    os.environ["VIM_DAILY_ANIM"] = "off"
    buf = io.StringIO()
    static_result = V.celebrate(rewards, duration=2.0, out=buf)
    static_text = buf.getvalue()
    assert static_result["shown"] and not static_result["interactive"]
    assert "First step" in static_text and "Level up" in static_text
    assert rewards[0]["credit"] in static_text and rewards[1]["credit"] in static_text
    assert "\033" not in static_text and "?1049h" not in static_text
    for blocked in ("NO_COLOR", "TERM"):
        os.environ["VIM_DAILY_ANIM"] = "on"
        os.environ.pop("NO_COLOR", None)
        os.environ["TERM"] = "xterm-256color"
        if blocked == "NO_COLOR":
            os.environ["NO_COLOR"] = "1"
        else:
            os.environ["TERM"] = "dumb"
        blocked_buf = io.StringIO()
        blocked_result = V.celebrate(rewards, out=blocked_buf)
        assert blocked_result["shown"] and not blocked_result["interactive"]
        assert rewards[1]["credit"] in blocked_buf.getvalue()
        assert "\033" not in blocked_buf.getvalue()
finally:
    for key, value in saved_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

# Viewer-disabled celebrations are silent, matching the existing playback
# gate and avoiding accidental unlock output in quiet/headless routes.
saved_viewer = os.environ.get("VIM_DAILY_VIEWER")
os.environ["VIM_DAILY_VIEWER"] = "off"
buf = io.StringIO()
disabled_result = V.celebrate(rewards, out=buf)
assert not disabled_result["shown"] and buf.getvalue() == ""
if saved_viewer is None:
    os.environ.pop("VIM_DAILY_VIEWER", None)
else:
    os.environ["VIM_DAILY_VIEWER"] = saved_viewer

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
    env.pop("NO_COLOR", None)
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


def finish_child(child, seconds=5):
    """Drain the pty and bound a failed interaction instead of hanging."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        exited, _status = os.waitpid(child, os.WNOHANG)
        if exited:
            return
        pump(0.10)
    os.kill(child, signal.SIGKILL)
    os.waitpid(child, 0)
    raise AssertionError("viewer child did not finish:\n" + out.decode("utf-8", "replace")[-4000:])


pump(1.2)                     # plays at least one frame change
os.write(fd, b" ")            # pause
pump(0.3)
os.write(fd, b"l")            # step
pump(0.3)
os.write(fd, b"o")            # onion on
pump(0.3)
os.write(fd, b"\r")           # continue
pump(1.0)
finish_child(pid)
screen = out.decode("utf-8", "replace")
for needle in ("WATCH YOUR WORK", "▶ playing", "❚❚ paused", "o\x1b[0m onion on",
               "HOLD", "Enter\x1b[0m continue", "\x1b[?1049h", "\x1b[?1049l"):
    assert needle in screen, (needle, screen[-800:])
result = json.loads(re.search(r"RESULT (\{.*\})", screen).group(1))
assert result["shown"] and result["interactive"], result
print("ok viewer pty: plays, pauses, steps, onion toggle, Enter returns, screen restored")

# A celebration shares one <=2s budget across rewards.  Any key skips it and
# the alternate screen/cbreak state is restored even on that early exit.
celebrate_script = r'''
import json, sys
sys.path.insert(0, %r)
import viewer as V
rewards = [{"title": "Badge", "art": ["[*]"], "credit": "credit", "kind": "badge"},
           {"title": "Level", "art": ["<+>"], "credit": "credit2", "kind": "level"}]
print("RESULT", json.dumps(V.celebrate(rewards, duration=2.0)))
''' % str(HERE)
pid, fd = pty.fork()
if pid == 0:
    env = dict(os.environ, TERM="xterm-256color", COLUMNS="80", LINES="24")
    env.pop("NO_COLOR", None)
    os.execvpe(sys.executable, [sys.executable, "-c", celebrate_script], env)
out = b""
pump(0.30)
os.write(fd, b"x")
pump(0.80)
finish_child(pid)
celebrate_screen = out.decode("utf-8", "replace")
assert "CELEBRATION" in celebrate_screen
assert "\x1b[?1049h" in celebrate_screen and "\x1b[?1049l" in celebrate_screen
celebrate_result = json.loads(re.search(r"RESULT (\{.*\})", celebrate_screen).group(1))
assert celebrate_result["shown"] and celebrate_result["interactive"]
assert celebrate_result["skipped"] and celebrate_result["elapsed"] < 1.5, celebrate_result
print("ok celebration pty: combined reward display, key skip, bounded timing, screen restored")

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
