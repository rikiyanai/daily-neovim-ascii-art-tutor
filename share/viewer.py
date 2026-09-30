"""Post-completion animation viewer (VD-62).

After a lesson passes, the learner watches what they made: a multi-frame strip
loops in place; a single-frame still plays as a BEFORE -> YOURS flip. Controls:

    space  pause / play        h / l  step back / forward (pauses)
    + / -  faster / slower     o      onion skin (previous frame, dim)
    d      light up the cells that changed from the previous frame
    p      switch between this lesson and the whole project strip
    Enter / q  continue

Outside a terminal (tests, pipes) the viewer prints a static filmstrip once
and returns. VIM_DAILY_VIEWER=off skips it entirely; NO_COLOR / TERM=dumb drop
colour; VIM_DAILY_ANIM=off shows the static filmstrip instead of playback.
Stdlib only: this runs inside the tmux popup next to Neovim.
"""
from __future__ import annotations

import os
import select
import shutil
import sys
import time
import unicodedata

SPEEDS = [1.0, 0.6, 0.4, 0.25, 0.15, 0.08]   # seconds per frame
DEFAULT_SPEED = 2


def enabled():
    return os.environ.get("VIM_DAILY_VIEWER", "").lower() not in ("off", "0", "no")


def _colour_ok():
    return os.environ.get("NO_COLOR") is None and os.environ.get("TERM") != "dumb"


def _anim_ok():
    return os.environ.get("VIM_DAILY_ANIM", "").lower() != "off"


def cell_width(text):
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


class View:
    """One playable strip: frames, per-frame labels, a title."""

    def __init__(self, title, frames, labels=None, holds=None, kind="lesson"):
        self.title = title
        self.frames = [list(f) for f in frames]
        self.labels = labels or ["frame %d" % (i + 1) for i in range(len(frames))]
        self.holds = holds or {}
        self.kind = kind

    @property
    def height(self):
        return max(len(f) for f in self.frames)

    @property
    def width(self):
        return max((cell_width(r) for f in self.frames for r in f), default=0)


def split_frames(rows, slices):
    if not slices or sum(slices) != len(rows):
        return None
    frames, offset = [], 0
    for h in slices:
        frames.append(rows[offset:offset + h])
        offset += h
    return frames


def lesson_view(card, rows, before=None):
    """The strip the learner just saved, or BEFORE -> YOURS for a still.

    `before` is the learner's own saved starting file when it exists (the
    lesson's `start` otherwise)."""
    frames = split_frames(rows, card.get("frame_slices"))
    title = "%s · %s" % (card["id"], card.get("title", ""))
    if frames and len(frames) > 1:
        holds = {i: "hold" for i in range(1, len(frames)) if frames[i] == frames[i - 1]}
        return View(title, frames, holds=holds)
    start = [r.rstrip() for r in (before if before else card.get("start", []))]
    if not start or start == [r.rstrip() for r in rows]:
        return View(title, [rows], labels=["yours"])
    return View(title, [start, rows], labels=["before", "yours"], kind="edit")


def _changed(prev, cur):
    """Set of (row, col) character positions in `cur` that differ from `prev`."""
    out = set()
    for r, line in enumerate(cur):
        old = prev[r] if prev and r < len(prev) else ""
        for c, ch in enumerate(line):
            if c >= len(old) or old[c] != ch:
                if ch != " ":
                    out.add((r, c))
        if prev and r < len(prev) and len(old) > len(line):
            if old[len(line):].strip():
                out.add((r, len(line)))
    return out


class Style:
    def __init__(self, colour):
        c = (lambda code: code) if colour else (lambda code: "")
        self.bold, self.dim, self.off = c("\033[1m"), c("\033[2m"), c("\033[0m")
        self.green = c("\033[1;32m")
        self.cyan = c("\033[36m")
        self.yellow = c("\033[33m")
        self.magenta = c("\033[35m")
        self.inverse = c("\033[7m")
        self.colour = colour


def render_frame(frame, prev, st, *, diff=False, onion=False):
    changed = _changed(prev, frame) if (diff and prev is not None) else set()
    lines = []
    height = max(len(frame), len(prev) if (onion and prev) else 0)
    for r in range(height):
        line = frame[r] if r < len(frame) else ""
        ghost = prev[r] if (onion and prev and r < len(prev)) else ""
        out = []
        width = max(len(line), len(ghost))
        for c in range(width):
            ch = line[c] if c < len(line) else " "
            if (r, c) in changed:
                if ch == " ":
                    out.append(st.magenta + "·" + st.off)  # a cell that was cleared
                else:
                    out.append(st.green + ch + st.off)
            elif ch == " " and c < len(ghost) and ghost[c] != " ":
                out.append(st.dim + (ghost[c] if st.colour else "·") + st.off)
            else:
                out.append(ch)
        lines.append("".join(out).rstrip() if not st.colour else "".join(out))
    return lines


def filmstrip(view, current, st, columns):
    """All frames side by side (current one marked), or None when too wide."""
    gap = 3
    widths = [max((cell_width(r) for r in f), default=0) for f in view.frames]
    widths = [max(w, len(view.labels[i]) + 2) for i, w in enumerate(widths)]
    if sum(widths) + gap * (len(widths) - 1) > columns - 2:
        return None
    rows = []
    for r in range(view.height):
        parts = []
        for i, f in enumerate(view.frames):
            cell = f[r] if r < len(f) else ""
            pad = widths[i] - cell_width(cell)
            text = cell + " " * pad
            parts.append((st.bold + text + st.off) if i == current else (st.dim + text + st.off))
        rows.append((" " * gap).join(parts))
    marks = []
    for i, label in enumerate(view.labels):
        mark = ("▲ " if i == current else "  ") + label
        marks.append(((st.cyan if i == current else st.dim) + mark.ljust(widths[i]) + st.off))
    rows.append((" " * gap).join(marks))
    return rows


def static_print(view, *, out=None):
    """One-shot text for pipes and tests: a filmstrip or stacked frames."""
    out = out or sys.stdout
    st = Style(False)
    columns = shutil.get_terminal_size((80, 24)).columns
    print("WATCH YOUR WORK  %s" % view.title, file=out)
    strip = filmstrip(view, len(view.frames) - 1, st, columns)
    if strip:
        for row in strip:
            print("  " + row.rstrip(), file=out)
    else:
        for i, frame in enumerate(view.frames):
            print("  -- %s" % view.labels[i], file=out)
            for row in frame:
                print("  " + row, file=out)


def _read_key(timeout):
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if not ready:
        return None
    ch = os.read(sys.stdin.fileno(), 1)
    if ch == b"\x1b":
        # Swallow an escape sequence (arrow keys) if one follows quickly.
        more = b""
        while select.select([sys.stdin], [], [], 0.01)[0]:
            more += os.read(sys.stdin.fileno(), 1)
        return {b"[C": "l", b"[D": "h"}.get(more[:2], "esc")
    try:
        return ch.decode()
    except UnicodeDecodeError:
        return None


def play(views, *, now=time.monotonic):
    """Interactive loop over one or more views (p switches). Returns a summary."""
    views = [v for v in views if v and v.frames]
    if not views:
        return {"shown": False}
    if not (sys.stdin.isatty() and sys.stdout.isatty()) or not _anim_ok():
        static_print(views[0])
        return {"shown": True, "interactive": False}
    import termios
    import tty
    fd = sys.stdin.fileno()
    saved = termios.tcgetattr(fd)
    st = Style(_colour_ok())
    state = {"view": 0, "frame": 0, "paused": False, "speed": DEFAULT_SPEED,
             "onion": False, "diff": True, "loops": 0}
    out = sys.stdout
    try:
        tty.setcbreak(fd)
        out.write("\033[?1049h\033[?25l")
        next_tick = now() + SPEEDS[state["speed"]]
        while True:
            view = views[state["view"]]
            _draw(view, state, st, multi=len(views) > 1)
            timeout = max(0.0, next_tick - now()) if not state["paused"] else None
            key = _read_key(timeout)
            if key is None:
                if not state["paused"] and len(view.frames) > 1:
                    state["frame"] = (state["frame"] + 1) % len(view.frames)
                    if state["frame"] == 0:
                        state["loops"] += 1
                next_tick = now() + SPEEDS[state["speed"]]
                continue
            if key in ("\r", "\n", "q", "esc"):
                break
            if key == " ":
                state["paused"] = not state["paused"]
            elif key in ("l", "h"):
                state["paused"] = True
                step = 1 if key == "l" else -1
                state["frame"] = (state["frame"] + step) % len(view.frames)
            elif key in ("+", "="):
                state["speed"] = min(len(SPEEDS) - 1, state["speed"] + 1)
            elif key in ("-", "_"):
                state["speed"] = max(0, state["speed"] - 1)
            elif key == "o":
                state["onion"] = not state["onion"]
            elif key == "d":
                state["diff"] = not state["diff"]
            elif key == "p" and len(views) > 1:
                state["view"] = (state["view"] + 1) % len(views)
                state["frame"] = 0
            next_tick = now() + SPEEDS[state["speed"]]
    finally:
        out.write("\033[?25h\033[?1049l")
        out.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, saved)
    return {"shown": True, "interactive": True, "loops": state["loops"]}


def _draw(view, state, st, *, multi):
    columns, rows = shutil.get_terminal_size((80, 24))
    i = state["frame"]
    n = len(view.frames)
    prev = view.frames[i - 1] if n > 1 else None
    if view.kind == "edit" and i == 0:
        prev = None
    frame = view.frames[i]
    body = render_frame(frame, prev, st, diff=state["diff"], onion=state["onion"])
    fps = 1.0 / SPEEDS[state["speed"]]
    status = "%s%s%s  %s %d/%d  %s%.1f fps%s%s" % (
        st.cyan, ("❚❚ paused" if state["paused"] else "▶ playing"), st.off,
        "frame" if view.labels[i].startswith("frame") else view.labels[i], i + 1, n,
        st.dim, fps, st.off,
        ("  " + st.yellow + "HOLD" + st.off) if i in view.holds else "")
    lines = ["%sWATCH YOUR WORK%s  %s" % (st.bold, st.off, view.title[:columns - 18]),
             "%s%s%s" % (st.dim, "whole project strip" if view.kind == "project"
                         else ("your edit: before → yours" if view.kind == "edit"
                               else "the frames you just made"), st.off),
             ""]
    lines += ["    " + row for row in body]
    lines.append("")
    strip = filmstrip(view, i, st, columns) if n > 1 else None
    budget = rows - len(lines) - 4
    if strip and len(strip) <= budget:
        lines += ["  " + row for row in strip]
        lines.append("")
    lines.append(status)
    toggles = "%sd%s changes %s · %so%s onion %s" % (
        st.bold, st.off, "on" if state["diff"] else "off",
        st.bold, st.off, "on" if state["onion"] else "off")
    lines.append("%sspace%s pause · %sh/l%s step · %s+/-%s speed%s" % (
        st.bold, st.off, st.bold, st.off, st.bold, st.off,
        (" · %sp%s whole project" % (st.bold, st.off)) if multi else ""))
    lines.append("%s · %sEnter%s continue" % (toggles, st.bold, st.off))
    sys.stdout.write("\033[H\033[2J" + "\n".join(lines[:rows - 1]))
    sys.stdout.flush()
