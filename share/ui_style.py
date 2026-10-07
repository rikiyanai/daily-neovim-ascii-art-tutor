"""The shared semantic style guide for every vim-daily surface.

The lesson renderer, viewer, and dashboard are intentionally different
presentations, but they should agree on the meaning of a colour.  This module
keeps that small contract dependency-free so the stdlib lesson path can use it
without importing Rich or Textual.

``STYLE`` contains Rich-compatible style strings for consumers that already
render Rich ``Text`` objects.  ``ansi`` is the tiny terminal counterpart for
plain-text surfaces.  Art is never a role: callers should leave lesson art
untouched and style only labels, controls, icons, avatars, or trophy UI.
"""

from __future__ import annotations

import os
from typing import Mapping


RESET = "\x1b[0m"

# The pink-to-purple band from the Y9-2 Rainbowifier.  Keep these as strings so
# Rich, ANSI helpers, demos, and future renderers share exactly the same stops.
GEMINI_COLORS = (
    "#FF324F",
    "#FC255F",
    "#F61A6F",
    "#EF1180",
    "#E60A91",
    "#DB04A1",
    "#CE01B1",
    "#C000C0",
    "#B101CE",
    "#A104DB",
    "#910AE6",
    "#8011EF",
)

# Semantic roles are deliberately small.  Keep the names stable: callers use
# them as meaning, not as a particular colour choice.
STYLE = {
    "heading": "bold",
    "key": "bold #5fd7ff",
    "new": "bold #f0c040",
    "ok": "bold #3fd46b",
    "fail": "bold #ff5f5f",
    "warn": "#f0c040",
    "meta": "#8a8f98",
    "concept": "bold #d49cff",
    "flags": "#9ed9ff",
}

# Derive ANSI from the same role table without importing Rich. Changing a
# semantic colour therefore cannot leave the plain-terminal palette behind.
def _ansi_style(value):
    codes = ["1"] if "bold" in value.split() else []
    colour = next((word for word in value.split() if word.startswith("#")), None)
    if colour:
        rgb = [int(colour[i:i + 2], 16) for i in (1, 3, 5)]
        codes += ["38", "2", *map(str, rgb)]
    return "\x1b[" + ";".join(codes) + "m" if codes else ""


_ANSI = {role: _ansi_style(value) for role, value in STYLE.items()}


def colour_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Return whether colour and animation may be emitted for ``env``.

    ``NO_COLOR`` follows the community convention: presence is enough, even
    when its value is empty.  A dumb or missing terminal is treated as plain
    output so redirected lesson runs never receive escape sequences.
    """

    values = os.environ if env is None else env
    return "NO_COLOR" not in values and values.get("TERM", "") not in ("", "dumb")


def ansi(role: str, enabled: bool | None = None) -> str:
    """Return the ANSI prefix for a semantic role, or ``""`` when disabled.

    Unknown roles are rejected early.  A misspelled role should not silently
    make a success or failure look like ordinary text.
    """

    if role not in STYLE:
        raise KeyError("unknown UI style role: %s" % role)
    if enabled is None:
        enabled = colour_enabled()
    return _ANSI[role] if enabled else ""


def wrap(role: str, value: str, enabled: bool | None = None) -> str:
    """Convenience helper for plain terminal labels using :func:`ansi`."""

    prefix = ansi(role, enabled)
    return prefix + value + (RESET if prefix else "")


__all__ = ["GEMINI_COLORS", "RESET", "STYLE", "ansi", "colour_enabled", "wrap"]
