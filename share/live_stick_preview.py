"""Live terminal preview for Shallot's editable 8-view stick-figure draft.

This previews the authored text cells, not the game's proportional-font render.
Run in a tmux pane: python3 share/live_stick_preview.py PATH
Save the file in Neovim to reload it. Nothing here writes to the source file.
"""

from __future__ import annotations

import argparse
import os
import re
import select
import shutil
import sys
import termios
import time
import tty
import unicodedata
from pathlib import Path

VIEWS = tuple(range(0, 360, 45))
POSES = ("idle", "walk_00", "walk_01", "walk_02", "walk_03")
W, H = 10, 8
SPEEDS = (0.5, 0.33, 0.25, 0.17, 0.1)
HEADER = re.compile(r"^# (idle|walk_0[0-3]) view=(\d+)deg(?:\s|$)")


def parse_sheet(source: str) -> dict[tuple[int, str], tuple[str, ...]]:
    """Read fixed-size blocks; fail visibly rather than playing broken edits."""
    lines = source.splitlines()
    frames: dict[tuple[int, str], tuple[str, ...]] = {}
    for i, line in enumerate(lines):
        match = HEADER.match(line)
        if not match:
            continue
        pose, view_text = match.groups()
        view = int(view_text)
        if view not in VIEWS:
            raise ValueError(f"line {i + 1}: view must be 0,45,...,315deg")
        key = (view, pose)
        if key in frames:
            raise ValueError(f"line {i + 1}: duplicate {pose} view={view}deg")
        rows = lines[i + 1:i + 1 + H]
        if len(rows) != H or any(len(row) != W for row in rows):
            raise ValueError(f"line {i + 1}: {pose} view={view}deg needs {H} rows of {W} characters")
        frames[key] = tuple(row.replace(".", " ") for row in rows)
    missing = [(view, pose) for view in VIEWS for pose in POSES if (view, pose) not in frames]
    if missing:
        view, pose = missing[0]
        raise ValueError(f"missing {pose} view={view}deg ({len(missing)} missing frames)")
    return frames


def cell_width(value: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in value)


def filmstrip(frames: dict[tuple[int, str], tuple[str, ...]], view: int) -> list[str]:
    labels = POSES[1:]
    result = ["   ".join(label.center(12) for label in labels)]
    for y in range(H):
        result.append("   ".join(frames[(view, label)][y] + " " * max(0, 12 - cell_width(frames[(view, label)][y])) for label in labels))
    return result


def screen(frames: dict[tuple[int, str], tuple[str, ...]] | None, *, path: Path,
           view: int, step: int, paused: bool, idle: bool, speed: int,
           error: str | None, reloads: int) -> str:
    size = shutil.get_terminal_size((80, 24))
    pose = "idle" if idle else POSES[step + 1]
    title = f"LIVE ASCII WALK   {W}x{H} cells   view {view:03d}deg   {pose}   {'PAUSED' if paused else f'{1 / SPEEDS[speed]:.1f} fps'}"
    rows = [title, f"Watching: {path.name}   saved reloads: {reloads}",
            "Save in Neovim (:w) to update.  This is TXT cells, not the game renderer.",
            "[ ] or h/l: view   0-7: view   space: pause   ,/.: step   i: idle   +/-: speed   q: quit", ""]
    if error:
        rows.extend([f"FILE ERROR: {error}", "Showing last valid save until the file is corrected.", ""])
    if frames is None:
        rows.append("Waiting for a valid sheet...")
    else:
        wide_rows = sum(cell_width(row) != W for frame in frames.values() for row in frame)
        if wide_rows:
            rows.append(f"WIDTH WARNING: {wide_rows} art rows occupy more than {W} terminal columns (e.g. full-width glyphs).")
        rows.extend(["CURRENT FRAME (dots are transparent spaces)", "   +" + "-" * W + "+",
                     *["   |" + line + "|" for line in frames[(view, pose)]],
                     "   +" + "-" * W + "+", "", "WALK KEY FRAMES — current view", *filmstrip(frames, view)])
        rows.append("     " + "   ".join("^".center(12) if not idle and step == i else " ".center(12) for i in range(4)))
    return "\n".join(row[:size.columns] for row in rows[:size.lines - 1]) + "\n"


def run(path: Path) -> int:
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        print("Live preview needs an interactive tmux/terminal pane.", file=sys.stderr)
        return 2
    fd = sys.stdin.fileno()
    saved = termios.tcgetattr(fd)
    frames: dict[tuple[int, str], tuple[str, ...]] | None = None
    signature: tuple[int, int, int] | None = None
    error: str | None = None
    view_index = step = reloads = 0
    paused = idle = False
    speed = 2
    next_tick = time.monotonic() + SPEEDS[speed]
    dirty = True
    out = sys.stdout
    try:
        tty.setcbreak(fd)
        out.write("\033[?1049h\033[?25l")
        out.flush()
        while True:
            try:
                stat = path.stat()
                now_signature = (stat.st_ino, stat.st_size, stat.st_mtime_ns)
                if now_signature != signature:
                    signature = now_signature
                    frames = parse_sheet(path.read_text(encoding="utf-8"))
                    reloads += 1
                    error = None
                    dirty = True
            except (OSError, UnicodeError, ValueError) as exc:
                message = str(exc)
                if message != error:
                    error = message
                    dirty = True
            now = time.monotonic()
            if not paused and not idle and now >= next_tick:
                step = (step + 1) % 4
                next_tick = now + SPEEDS[speed]
                dirty = True
            if dirty:
                out.write("\033[H\033[2J" + screen(frames, path=path, view=VIEWS[view_index], step=step,
                                                     paused=paused, idle=idle, speed=speed,
                                                     error=error, reloads=reloads))
                out.flush()
                dirty = False
            ready, _, _ = select.select([fd], [], [], 0.08)
            if not ready:
                continue
            key = os.read(fd, 1)
            if key in (b"q", b"Q", b"\x03"):
                break
            if key in (b"[", b"h"):
                view_index = (view_index - 1) % 8
            elif key in (b"]", b"l"):
                view_index = (view_index + 1) % 8
            elif key in (b"0", b"1", b"2", b"3", b"4", b"5", b"6", b"7"):
                view_index = int(key)
            elif key == b" ":
                paused = not paused
            elif key in (b",", b"p"):
                step = (step - 1) % 4
                paused = True
                idle = False
            elif key in (b".", b"n"):
                step = (step + 1) % 4
                paused = True
                idle = False
            elif key == b"i":
                idle = not idle
            elif key in (b"+", b"="):
                speed = min(speed + 1, len(SPEEDS) - 1)
            elif key in (b"-", b"_"):
                speed = max(speed - 1, 0)
            else:
                continue
            next_tick = time.monotonic() + SPEEDS[speed]
            dirty = True
    finally:
        out.write("\033[?25h\033[?1049l")
        out.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, saved)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="editable play-8dir-draft.txt")
    args = parser.parse_args()
    return run(args.source.expanduser().resolve())


if __name__ == "__main__":
    raise SystemExit(main())
