"""Focused contract tests for the shared semantic style guide."""

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import dashboard_theme as theme  # noqa: E402
import ui_style as style  # noqa: E402
from avatar_options import AVATAR_OPTIONS  # noqa: E402


def main():
    roles = {"heading", "key", "new", "ok", "fail", "warn", "meta", "concept", "flags"}
    assert roles <= set(style.STYLE)
    assert tuple(style.GEMINI_COLORS) == (
        "#FF324F", "#FC255F", "#F61A6F", "#EF1180", "#E60A91", "#DB04A1",
        "#CE01B1", "#C000C0", "#B101CE", "#A104DB", "#910AE6", "#8011EF",
    )
    assert style.colour_enabled({"TERM": "xterm-256color"})
    assert not style.colour_enabled({"TERM": "dumb"})
    assert not style.colour_enabled({"TERM": "xterm-256color", "NO_COLOR": "1"})
    assert style.ansi("ok", enabled=True).startswith("\x1b[")
    assert style.ansi("ok", enabled=False) == ""
    assert style.wrap("ok", "✓", enabled=False) == "✓"
    assert style.wrap("ok", "✓", enabled=True).endswith("✓" + style.RESET)

    # Theme extras remain available, but derive their semantic base from the
    # shared table and use the accepted Gemini band for Pro.
    assert roles <= set(theme.STYLE)
    assert theme.STYLE["bar_full"] == style.STYLE["ok"].replace("bold ", "")
    assert theme.tier_for_level(12)["gradient"] == list(style.GEMINI_COLORS)
    assert all("icon" in badge and "style" in badge for badge in theme.BADGES)

    # The evaluator is pure data: it does not import Textual and can run from
    # a static tree or a test fixture with a tiny projection.
    cur = {"cards": [{"id": "M0.01", "module_id": "M0"}]}
    progress = {
        "passed_cards": ["M0.01"], "badges": ["first-step"],
        "deck": [], "stages": {"S0": {"state": "available", "done": 1,
                                        "total": 1, "reviews_done": 0, "reviews_total": 0}},
    }
    rows = theme.badge_status(cur, progress, {"events": [
        {"type": "card", "result": "pass", "card_id": "M0.01", "at": "2026-09-30"},
    ]})
    first = next(row for row in rows if row["id"] == "first-step")
    assert first["earned"] and first["have"] == 1 and first["style"] == "new"
    assert next(row for row in rows if row["id"] == "week-in-motion")["have"] == 1

    # Every requested review level has three complete original candidates.
    assert set(AVATAR_OPTIONS) == {3, 4, 5, 6, 7}
    for level, options in AVATAR_OPTIONS.items():
        assert len(options) >= 3
        assert all(candidate["art"] and all("\x1b" not in row for row in candidate["art"])
                   for candidate in options)
        assert len({candidate["id"] for candidate in options}) == len(options)

    demo = subprocess.run([sys.executable, str(HERE / "avatar_options.py"), "--level", "3"],
                          capture_output=True, text=True, check=True,
                          env=dict(os.environ, NO_COLOR="1", TERM="dumb"))
    assert "REVIEW ONLY" in demo.stdout and "no avatar was selected" in demo.stdout
    assert demo.stdout.count("Lv3 ·") == 3
    print("test_ui_style: all passed")


if __name__ == "__main__":
    main()
