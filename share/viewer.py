"""Post-completion animation viewer (VD-62).

After a lesson passes, the learner watches what they made: a multi-frame strip
loops in place; a single-frame still plays as a BEFORE -> YOURS flip. Controls:

    space  pause / play        h / l  step back / forward (pauses)
    + / -  faster / slower     o      onion skin (previous frame, dim)
    d      (opt-in) light up the cells that changed from the previous frame
    p      switch between this lesson and the whole project strip
    Enter / q  continue

Outside a terminal (tests, pipes) the viewer prints a static filmstrip once
and returns. VIM_DAILY_VIEWER=off skips it entirely; NO_COLOR / TERM=dumb drop
colour; VIM_DAILY_ANIM=off shows the static filmstrip instead of playback.
Stdlib only: this runs inside the tmux popup next to Neovim.

Unlocks use ``celebrate([{title, art, credit, kind}, ...])``.  Reward art is
UI art and may use the shared Gemini gradient; lesson art remains unstyled by
default.
"""
from __future__ import annotations

import importlib.util
import os
import select
import shutil
import sys
import time
import unicodedata
from pathlib import Path

SPEEDS = [1.0, 0.6, 0.4, 0.25, 0.15, 0.08]   # seconds per frame
DEFAULT_SPEED = 2


def enabled():
    return os.environ.get("VIM_DAILY_VIEWER", "").lower() not in ("off", "0", "no")


def _colour_ok():
    if os.environ.get("NO_COLOR") is not None or os.environ.get("TERM") == "dumb":
        return False
    style = _ui_style()
    enabled_fn = getattr(style, "colour_enabled", None) if style else None
    if callable(enabled_fn):
        try:
            return bool(enabled_fn())
        except Exception:
            pass
    return True


def _anim_ok():
    return os.environ.get("VIM_DAILY_ANIM", "").lower() != "off"


def cell_width(text):
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


_UI_STYLE = None
_UI_STYLE_LOADED = False


def _ui_style():
    """Load the shared style module even when the gate imports us by path."""
    global _UI_STYLE, _UI_STYLE_LOADED
    if _UI_STYLE_LOADED:
        return _UI_STYLE
    _UI_STYLE_LOADED = True
    path = Path(__file__).with_name("ui_style.py")
    try:
        spec = importlib.util.spec_from_file_location("vim_daily_ui_style", path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            _UI_STYLE = module
    except (OSError, ImportError, SyntaxError):
        _UI_STYLE = None
    return _UI_STYLE


GEMINI_COLORS = (
    "#FF324F", "#FC255F", "#F61A6F", "#EF1180", "#E60A91", "#DB04A1",
    "#CE01B1", "#C000C0", "#B101CE", "#A104DB", "#910AE6", "#8011EF",
)


def _hex_ansi(value):
    if isinstance(value, (tuple, list)) and len(value) >= 3:
        try:
            red, green, blue = (int(value[i]) for i in range(3))
            return "\033[38;2;%d;%d;%dm" % (red, green, blue)
        except (TypeError, ValueError):
            return ""
    value = str(value)
    if value.startswith("\033["):
        return value
    if value.startswith("#") and len(value) == 7:
        try:
            red, green, blue = (int(value[i:i + 2], 16) for i in (1, 3, 5))
            return "\033[38;2;%d;%d;%dm" % (red, green, blue)
        except ValueError:
            return ""
    return ""


def _shared_ansi(role, fallback, colour):
    if not colour:
        return ""
    style = _ui_style()
    ansi_fn = getattr(style, "ansi", None) if style else None
    if callable(ansi_fn):
        try:
            value = ansi_fn(role, enabled=True)
            if isinstance(value, str) and value:
                return value
        except Exception:
            pass
    return fallback


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
    rows = list(rows)
    frames = split_frames(rows, card.get("frame_slices"))
    title = "%s · %s" % (card["id"], card.get("title", ""))
    if frames and len(frames) > 1:
        holds = {i: "hold" for i in range(1, len(frames)) if frames[i] == frames[i - 1]}
        return View(title, frames, holds=holds)
    # A proportional/JIS card can make trailing half/full spaces part of the
    # authored text.  Keep the raw rows for that explicit contract; legacy
    # cards retain the historical right-trimmed comparison.
    preserve = bool(card.get("preserve_trailing_whitespace"))
    source = before if before is not None else card.get("start", [])
    start = list(source) if preserve else [r.rstrip() for r in source]
    current = rows if preserve else [r.rstrip() for r in rows]
    if not start or start == current:
        return View(title, [rows], labels=["yours"])
    return View(title, [start, rows], labels=["before", "yours"], kind="edit")


def _changed(prev, cur):
    """Return every changed codepoint position across both frame extents.

    Missing characters are compared as an empty cell.  This intentionally
    includes ordinary and full-width whitespace: a diagnostic diff must not
    erase a meaningful tail merely because it has no visible ink.
    """
    out = set()
    previous = list(prev or [])
    current = list(cur or [])
    for r in range(max(len(previous), len(current))):
        old = previous[r] if r < len(previous) else ""
        line = current[r] if r < len(current) else ""
        for c in range(max(len(old), len(line))):
            old_ch = old[c] if c < len(old) else ""
            new_ch = line[c] if c < len(line) else ""
            if old_ch != new_ch:
                out.add((r, c))
    return out


class Style:
    def __init__(self, colour):
        self.colour = bool(colour)
        self.bold = _shared_ansi("heading", "\033[1m", self.colour)
        self.dim = _shared_ansi("meta", "\033[2m", self.colour)
        self.off = "\033[0m" if self.colour else ""
        self.ok = _shared_ansi("ok", "\033[1;32m", self.colour)
        self.green = self.ok  # explicit diff uses the same semantic palette
        self.cyan = _shared_ansi("concept", "\033[36m", self.colour)
        self.yellow = _shared_ansi("warn", "\033[33m", self.colour)
        self.magenta = _shared_ansi("flags", "\033[35m", self.colour)
        self.inverse = _shared_ansi("key", "\033[7m", self.colour)
        style = _ui_style()
        stops = getattr(style, "GEMINI_COLORS", None) if style else None
        self.gemini = tuple(stops or GEMINI_COLORS)

    def gradient(self, index, phase=0):
        if not self.colour or not self.gemini:
            return ""
        return _hex_ansi(self.gemini[(int(index) + int(phase)) % len(self.gemini)])


def render_frame(frame, prev, st, *, diff=False, onion=False):
    changed = _changed(prev, frame) if (diff and prev is not None) else set()
    lines = []
    height = max(len(frame), len(prev) if ((diff or onion) and prev is not None) else 0)
    for r in range(height):
        line = frame[r] if r < len(frame) else ""
        previous = prev[r] if (prev is not None and r < len(prev)) else ""
        ghost = previous if onion else ""
        out = []
        width = max(len(line), len(previous) if (diff or onion) else 0)
        for c in range(width):
            ch = line[c] if c < len(line) else " "
            if (r, c) in changed:
                # Show a marker for every cleared/whitespace cell.  Match the
                # deleted full-width character's display width so the marker
                # remains at the same visual extent as the source glyph.
                if not ch or ch.isspace():
                    source = previous[c] if c < len(previous) else ch
                    marker = "·" * max(1, cell_width(source))
                    out.append(st.magenta + marker + st.off)
                else:
                    out.append(st.green + ch + st.off)
            elif ch.isspace() and c < len(ghost) and not ghost[c].isspace():
                marker = "·" * max(1, cell_width(ch))
                out.append(st.dim + (ghost[c] if st.colour else marker) + st.off)
            else:
                out.append(ch)
        # Do not right-trim canonical frame rows.  Trailing U+0020 and U+3000
        # are meaningful for cards that opt into whitespace preservation.
        lines.append("".join(out))
    return lines


def filmstrip(view, current, st, columns):
    """All frames side by side (current one marked), or None when too wide."""
    gap = 3
    widths = [max((cell_width(r) for r in f), default=0) for f in view.frames]
    widths = [max(w, cell_width(view.labels[i]) + 2) for i, w in enumerate(widths)]
    if sum(widths) + gap * (len(widths) - 1) > columns - 2:
        return None
    rows = []
    for r in range(view.height):
        parts = []
        for i, f in enumerate(view.frames):
            cell = f[r] if r < len(f) else ""
            pad = widths[i] - cell_width(cell)
            text = cell + " " * pad
            # Art rows remain raw.  Labels below carry the current-frame style.
            parts.append(text)
        rows.append((" " * gap).join(parts))
    marks = []
    for i, label in enumerate(view.labels):
        mark = ("▲ " if i == current else "  ") + label
        marks.append((st.cyan if i == current else st.dim) + mark
                     + " " * max(0, widths[i] - cell_width(mark)) + st.off)
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
            print("  " + row, file=out)
    else:
        for i, frame in enumerate(view.frames):
            print("  -- %s" % view.labels[i], file=out)
            for row in frame:
                print("  " + row, file=out)


def _read_key(timeout, stream=None):
    stream = stream or sys.stdin
    ready, _, _ = select.select([stream], [], [], timeout)
    if not ready:
        return None
    ch = os.read(stream.fileno(), 1)
    if ch == b"\x1b":
        # Swallow an escape sequence (arrow keys) if one follows quickly.
        more = b""
        while select.select([stream], [], [], 0.01)[0]:
            more += os.read(stream.fileno(), 1)
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
             "onion": False, "diff": False, "loops": 0}
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


def _reward_rows(reward):
    art = reward.get("art") or []
    if isinstance(art, str):
        return art.splitlines() or [""]
    if isinstance(art, (tuple, list)):
        # Be forgiving of a one-frame wrapper while keeping the documented
        # shape (a list of rows) intact.
        if art and isinstance(art[0], (tuple, list)):
            art = art[0]
        return [str(row) for row in art]
    return [str(art)]


def _normalise_rewards(rewards):
    if isinstance(rewards, dict):
        rewards = [rewards]
    out = []
    for reward in rewards or []:
        if not isinstance(reward, dict):
            continue
        row = dict(reward)
        row["title"] = str(row.get("title") or row.get("kind") or "Reward")
        row["kind"] = str(row.get("kind") or "reward")
        row["credit"] = str(row.get("credit") or "")
        row["art"] = _reward_rows(row)
        out.append(row)
    return out


def _gradient_art(row, st, phase):
    """Colour reward/icon art only; lesson frames never enter this path."""
    if not st.colour:
        return row
    pieces = []
    visible = 0
    for char in row:
        if char.isspace():
            pieces.append(char)
            continue
        pieces.append(st.gradient(visible, phase) + char + st.off)
        visible += 1
    return "".join(pieces)


def celebration_lines(rewards, st, *, tick=0, max_rows=None):
    """Render a celebration, retaining each reward's visible source credit."""
    rewards = _normalise_rewards(rewards)
    pulse = (tick // 2) % 2 == 1
    sparkle = ("✦" if tick % 4 in (0, 1) else "·") if st.colour else "*"
    heading = "  %s%s CELEBRATION %s" % (st.bold if pulse else "", sparkle,
                                         st.off if pulse else "")
    lines = [heading]
    for index, reward in enumerate(rewards):
        marker = "↑" if reward["kind"].lower() in ("level", "level-up", "levelup") else "★"
        if st.colour and tick % 4 in (0, 1):
            marker = sparkle
        title = "%s%s%s %s" % (st.bold if pulse else "", marker, st.off if pulse else "",
                                reward["title"])
        lines.append("  " + title)
        for row in reward["art"]:
            lines.append("    " + _gradient_art(row, st, tick + index))
        if reward["credit"]:
            lines.append("    %s%s%s" % (st.dim, reward["credit"], st.off))
        if index != len(rewards) - 1:
            lines.append("")
    lines.append("")
    lines.append("  any key skips · Enter continues")
    if max_rows and len(lines) > max_rows:
        # Rotate compact batches instead of truncating later rewards/credits.
        # The shared two-second clock still bounds the whole celebration.
        compact = [heading]
        per_page = max(1, (max_rows - 3) // 2)
        batches = [rewards[i:i + per_page] for i in range(0, len(rewards), per_page)]
        for reward in batches[tick % len(batches)]:
            marker = "↑" if reward["kind"].lower() in ("level", "level-up", "levelup") else "★"
            compact.append("  %s %s" % (marker, reward["title"]))
            if reward["credit"]:
                compact.append("    %s" % reward["credit"])
        compact.extend(("", "  any key skips · Enter continues"))
        lines = compact
    return lines


def _static_celebrate(rewards, out):
    st = Style(False)
    for line in celebration_lines(rewards, st):
        print(line, file=out)
    out.flush()


def celebrate(rewards, *, duration=2.0, out=None, inp=None, input_stream=None,
              output_stream=None, now=time.monotonic):
    """Show one bounded unlock celebration for badges and/or a level-up.

    ``rewards`` is a list of dictionaries with ``title``, ``art``, ``credit``
    and ``kind`` fields.  ``art`` is a list of rows and ``credit`` is printed
    for every reward, including static/no-colour fallback output.  All rewards
    share one animation budget (capped at two seconds), and any key skips it.
    A disabled viewer, non-terminal, dumb terminal, no-colour mode, or
    ``VIM_DAILY_ANIM=off`` uses a safe one-shot static display; no terminal
    modes are changed on that path.
    """
    rewards = _normalise_rewards(rewards)
    result = {"shown": False, "interactive": False, "skipped": False,
              "rewards": len(rewards), "elapsed": 0.0}
    if not rewards or not enabled():
        return result
    out = output_stream or out or sys.stdout
    inp = input_stream or inp or sys.stdin
    try:
        budget = min(2.0, max(0.0, float(duration)))
    except (TypeError, ValueError):
        budget = 2.0
    is_tty = lambda stream: bool(getattr(stream, "isatty", lambda: False)())
    interactive = (budget > 0 and _anim_ok() and _colour_ok() and
                   is_tty(inp) and is_tty(out))
    if not interactive:
        _static_celebrate(rewards, out)
        result.update(shown=True)
        return result
    try:
        import termios
        import tty
        fd = inp.fileno()
        saved = termios.tcgetattr(fd)
    except (ImportError, OSError, AttributeError):
        _static_celebrate(rewards, out)
        result.update(shown=True)
        return result
    st = Style(True)
    started = now()
    skipped = False
    tick = 0
    entered_alt = False
    try:
        tty.setcbreak(fd)
        out.write("\033[?1049h\033[?25l")
        entered_alt = True
        while True:
            elapsed = now() - started
            if elapsed >= budget:
                break
            columns, rows = shutil.get_terminal_size((80, 24))
            del columns  # The shared renderer remains width-safe through rows.
            lines = celebration_lines(rewards, st, tick=tick, max_rows=max(3, rows - 1))
            out.write("\033[H\033[2J" + "\n".join(lines[:max(1, rows - 1)]))
            out.flush()
            key = _read_key(min(0.08, max(0.0, budget - elapsed)), inp)
            if key is not None:
                skipped = True
                break
            tick += 1
    finally:
        if entered_alt:
            out.write("\033[?25h\033[?1049l")
            out.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, saved)
    result.update(shown=True, interactive=True, skipped=skipped,
                  elapsed=min(budget, max(0.0, now() - started)))
    return result


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
                         else "module reward · authored original · not learner output" if view.kind == "module_reward"
                         else ("cursor travel · artwork unchanged" if view.kind == "navigation"
                               else "still study · not animation" if view.kind == "still"
                               else "your edit: before → yours" if view.kind == "edit"
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
