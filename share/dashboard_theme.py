"""Dashboard look as data (VD-58): tier colours, level avatars, badges, glyphs.

Everything a style guide may change lives here as plain values, so a later
style pass can replace them without touching share/dashboard_tui.py.

All avatar art in this file is original to this repository: small shapes drawn
for the level ladder. Badge TROPHIES reuse Stone Story RPG animation frames
(Gabriel Santos, Martian Rex, Inc.); every one carries that credit on screen.
The operator confirmed publication rights on 2026-09-29 (FAILURE_LOG VD-60).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import importlib.util
from pathlib import Path

try:
    import ui_style as UI
except ImportError:  # the installed gate may load this module by file path
    _style_path = Path(__file__).with_name("ui_style.py")
    _style_spec = importlib.util.spec_from_file_location("vim_daily_ui_style", _style_path)
    if _style_spec is None or _style_spec.loader is None:
        raise
    UI = importlib.util.module_from_spec(_style_spec)
    _style_spec.loader.exec_module(UI)

# Level tiers. A level belongs to the last tier whose `from_level` it reaches.
# `colour` None = the terminal's own foreground (beginner has no colour).
# `gradient` = colour stops swept across the text (the "gemini" pro tier).
TIERS = [
    {"id": "beginner", "name": "Beginner", "from_level": 1, "colour": None},
    {"id": "intermediate", "name": "Intermediate", "from_level": 4, "colour": "#cd7f32"},
    {"id": "advanced", "name": "Advanced", "from_level": 8, "colour": "#ffd700"},
    # The pro tier uses the specified pink-purple Gemini band;
    # this is a reviewable palette choice, not a silent avatar swap.
    {"id": "pro", "name": "Pro", "from_level": 12, "colour": UI.GEMINI_COLORS[0],
     "gradient": list(UI.GEMINI_COLORS)},
]


def tier_for_level(level):
    tier = TIERS[0]
    for row in TIERS:
        if level >= row["from_level"]:
            tier = row
    return tier


# One avatar per level title (v2_runtime._level has 14 titles). Levels past
# the ladder keep the last avatar. Rows are at most 7 cells wide, 3 rows tall.
AVATARS = [
    ["  .  ", " (_) ", " /|\\ "],        # 1 Apprentice: a first dot of ink
    [" [x] ", " (o) ", " /|\\ "],        # 2 Cell Editor: holds one cell
    ["  o/ ", " /|  ", " / > "],         # 3 Pose Builder: strikes a pose
    ["+---+", "|o> |", "+---+"],         # 4 Frame Crafter: a pose in a frame
    ["o  o  o", "|  /  -", "^  ^  ^"],   # 5 Tween Reader: three in-betweens
    [" /\\  *", "/__\\ o", "|[]|/|"],     # 6 Scene Author: house, star, figure
    [" .-. ", "(-+ )", " '-' "],         # 7 Timing Artist: a clock face
    [">>o  ", "  |> ", " / \\ "],         # 8 Motion Editor: speed lines
    ["[o][o]", "[|][/]", "[^][^]"],      # 9 Animator: two film cells
    ["  _o_ ", " / | \\", "[=====]"],     # 10 ASCII Director: on the podium
    [" .->. ", "(  o  )", " '<-' "],      # 11 Loop Designer: a loop
    ["░▒▓█▓▒░", "▒ o o ▒", "░▒▓█▓▒░"],   # 12 Texture Animator: shaded frame
    ["o>o>o>o", " \\|/|\\ ", "o<o<o<o"],  # 13 Motion Systems Artist: chains
    ["╔═════╗", "║ >_█ ║", "╚═════╝"],   # 14 Terminal Animation Director
]


def avatar_for_level(level):
    return AVATARS[max(1, min(level, len(AVATARS))) - 1]


# Semantic colours (Rich style strings).  The first nine roles are the shared
# contract; the remainder are dashboard-only aliases derived from that table.
# Every ✓ and every "+N" uses ``ok``.
STYLE = dict(UI.STYLE)
STYLE.update({
    "here": UI.STYLE["key"],
    "bar_full": UI.STYLE["ok"].replace("bold ", ""),
    "bar_empty": UI.STYLE["meta"],
    "flame": "bold #ff8c1a",
    "flame_glow": ["#ff5a1a", "#ff8c1a", "#ffb31a", "#ffd966", "#ffb31a", "#ff8c1a"],
    "sparkle": ["#fff3b0", "#ffd700", "#ffffff", "#b3e5ff"],
    "strip_on": UI.STYLE["ok"].replace("bold ", ""),
    "strip_off": UI.STYLE["meta"],
})

# Journey states, in the words the learner sees. (glyph, style key, word)
STATE = {
    "mastered": ("✓", "ok", "mastered"),
    "review_pending": ("↻", "warn", "coming back for review"),
    "check_ready": ("◆", "key", "final check ready"),
    "learning": ("◐", "warn", "in progress"),
    "available": ("○", None, "open"),
    "locked": ("▫", "meta", "locked"),
}
CARD_STATE = {
    "done": ("✓", "ok"),
    "revisit": ("↻", "warn"),
    "tried": ("◐", "warn"),
    "open": ("○", None),
    "locked": ("▫", "meta"),
}

# Badges. `rule` names an evaluator in dashboard_tui.BADGE_RULES; `need` is
# its target. `runtime` badges are the eight v2_runtime.project() already
# awards; the rest are dashboard badges built from the same event ledger.
# None can be farmed: each counts distinct passed lessons, distinct days, or
# stage mastery, never repeated attempts.
BADGES = [
    {"id": "first-step", "glyph": "◆", "name": "First step",
     "desc": "pass your first lesson", "rule": "passed", "need": 1, "runtime": True},
    {"id": "transfer", "glyph": "◆", "name": "Transfer",
     "desc": "pass an unseen-art lesson", "rule": "transfer", "need": 1, "runtime": True},
    {"id": "grid-author", "glyph": "★", "name": "Grid author",
     "desc": "master S0", "rule": "stage", "stage": "S0", "runtime": True},
    {"id": "still-artist", "glyph": "★", "name": "Still artist",
     "desc": "master S7", "rule": "stage", "stage": "S7", "runtime": True},
    {"id": "inbetweener", "glyph": "★", "name": "In-betweener",
     "desc": "master A2", "rule": "stage", "stage": "A2", "runtime": True},
    {"id": "timing-editor", "glyph": "★", "name": "Timing editor",
     "desc": "master A4", "rule": "stage", "stage": "A4", "runtime": True},
    {"id": "animator", "glyph": "★", "name": "Animator",
     "desc": "master A7", "rule": "stage", "stage": "A7", "runtime": True},
    {"id": "corpus-reader", "glyph": "★", "name": "Corpus reader",
     "desc": "master the optional P branch", "rule": "stage", "stage": "P", "runtime": True},
    {"id": "streak-keeper-7", "glyph": "▲", "name": "Streak keeper 7",
     "desc": "practise 7 days in a row", "rule": "best_streak", "need": 7},
    {"id": "streak-keeper-14", "glyph": "▲", "name": "Streak keeper 14",
     "desc": "practise 14 days in a row", "rule": "best_streak", "need": 14},
    {"id": "streak-keeper-30", "glyph": "▲", "name": "Streak keeper 30",
     "desc": "practise 30 days in a row", "rule": "best_streak", "need": 30},
    {"id": "commands-10", "glyph": "◆", "name": "+10 commands",
     "desc": "learn 10 different commands", "rule": "commands", "need": 10},
    {"id": "commands-25", "glyph": "◆", "name": "+25 commands",
     "desc": "learn 25 different commands", "rule": "commands", "need": 25},
    {"id": "commands-50", "glyph": "◆", "name": "+50 commands",
     "desc": "learn 50 different commands", "rule": "commands", "need": 50},
    {"id": "safe-ranger", "glyph": "◆", "name": "Safe ranger",
     "desc": "pass 3 lessons that edit a line range with :", "rule": "range", "need": 3},
    {"id": "branch-rescuer", "glyph": "◆", "name": "Branch rescuer",
     "desc": "bring back 3 lessons that were sent back for practice", "rule": "rescued",
     "need": 3},
    {"id": "clean-hands", "glyph": "◆", "name": "Clean hands",
     "desc": "pass 10 lessons on the first try", "rule": "first_try", "need": 10},
    {"id": "review-keeper", "glyph": "↻", "name": "Review keeper",
     "desc": "pass 5 spaced reviews", "rule": "reviews", "need": 5},
    {"id": "full-day", "glyph": "●", "name": "Full day",
     "desc": "reach the daily goal", "rule": "goal_day", "need": 1},
    {"id": "cartographer", "glyph": "✦", "name": "Cartographer",
     "desc": "open every stills stage S0–S7", "rule": "unlocked_stills", "need": 8},
    {"id": "transfer-adept", "glyph": "◆", "name": "Transfer adept",
     "desc": "pass 3 unseen-art lessons", "rule": "transfer", "need": 3},
    {"id": "week-in-motion", "glyph": "◈", "name": "Week in motion",
     "desc": "practise on 7 distinct days", "rule": "distinct_days", "need": 7},
    {"id": "module-mapper", "glyph": "⌘", "name": "Module mapper",
     "desc": "pass 5 different modules", "rule": "modules", "need": 5},
    {"id": "review-pioneer", "glyph": "↟", "name": "Review pioneer",
     "desc": "complete 3 different spaced reviews", "rule": "reviews_distinct", "need": 3},
]

# ``glyph`` remains the dashboard's rendering field for compatibility with
# existing snapshots.  ``icon`` and ``style`` make the descriptor complete for
# static trees and future surfaces without importing dashboard_tui.
_BADGE_STYLES = {
    "first-step": "new", "transfer": "concept", "grid-author": "key",
    "still-artist": "key", "inbetweener": "key", "timing-editor": "key",
    "animator": "key", "corpus-reader": "concept", "clean-hands": "ok",
    "review-keeper": "ok", "review-pioneer": "ok", "full-day": "ok",
    "week-in-motion": "ok", "module-mapper": "concept",
}
_BADGE_ICONS = {
    "first-step": "[.]", "transfer": ">>", "grid-author": "[#]",
    "still-artist": "/\\", "inbetweener": "o-o", "timing-editor": "|:|",
    "animator": "[>]", "corpus-reader": "{?}", "streak-keeper-7": "(*)",
    "streak-keeper-14": "(* *)", "streak-keeper-30": "(*^*)",
    "commands-10": "+|", "commands-25": "++", "commands-50": "+++",
    "safe-ranger": "[..]", "branch-rescuer": "/+/", "clean-hands": "[+]",
    "review-keeper": "<->", "full-day": "(+)", "cartographer": "[/]",
    "transfer-adept": ">>>", "week-in-motion": "o>o", "module-mapper": "[=]",
    "review-pioneer": "<^>",
}
for _badge in BADGES:
    _badge.setdefault("icon", _BADGE_ICONS[_badge["id"]])
    _badge.setdefault("style", _BADGE_STYLES.get(_badge["id"], "warn"))


def _cfg_value(cfg, name, default=None):
    if isinstance(cfg, Mapping):
        return cfg.get(name, default)
    return getattr(cfg, name, default) if cfg is not None else default


def _badge_events(cfg, progress):
    events = _cfg_value(cfg, "events", None)
    if events is None:
        events = progress.get("events", []) if isinstance(progress, Mapping) else []
    # A generator is useful to callers, but badge evaluation needs to inspect
    # the ledger more than once.  Do not consume a caller-owned list in place.
    if not isinstance(events, Iterable) or isinstance(events, (str, bytes)):
        return []
    return [event for event in events if isinstance(event, Mapping)]


def _badge_values(cur, progress, cfg=None):
    """Derive farm-resistant counts from projection data and an event ledger."""
    events = _badge_events(cfg, progress)
    passed = set(progress.get("passed_cards", []))
    cards = {c.get("id"): c for c in cur.get("cards", [])}
    passed_events = [e for e in events
                     if e.get("type") in ("card", "review") and e.get("result") == "pass"]
    days = {str(e.get("at", ""))[:10] for e in passed_events if e.get("at")}
    modules = {cards[cid].get("module_id") for cid in passed if cid in cards}
    review_keys = {e.get("review_key") for e in events
                   if e.get("type") == "review" and e.get("result") == "pass"
                   and e.get("review_key")}
    first_try = {e.get("card_id") for e in events
                 if e.get("type") == "card" and e.get("result") == "pass"
                 and e.get("attempts") == 1 and e.get("card_id")}
    scheduled = set()
    rescued = set()
    for event in events:
        if event.get("type") == "remediation_scheduled" and event.get("card_id"):
            scheduled.add(event["card_id"])
        elif (event.get("type") in ("card", "review")
              and event.get("result") == "pass"
              and event.get("card_id") in scheduled):
            rescued.add(event["card_id"])
            scheduled.discard(event["card_id"])
    values = {
        "passed": len(passed),
        "transfer": sum(1 for cid in passed if str(cid).endswith(".06")),
        "best_streak": progress.get("best_streak", 0),
        "commands": len(progress.get("deck", [])),
        "range": 0,
        "rescued": len(rescued),
        "first_try": len(first_try),
        "reviews": len({(e.get("review_key"), e.get("review_stage")) for e in events
                         if e.get("type") == "review" and e.get("result") == "pass"}),
        "reviews_distinct": len(review_keys),
        "distinct_days": len(days),
        "modules": len({m for m in modules if m}),
        "goal_day": 0,
        "unlocked_stills": sum(1 for sid, stage in progress.get("stages", {}).items()
                                if str(sid).startswith("S") and stage.get("state") != "locked"),
    }
    target = _cfg_value(cfg, "target", 12)
    per_day = {}
    for event in passed_events:
        day = str(event.get("at", ""))[:10]
        per_day[day] = per_day.get(day, 0) + 1
    values["goal_day"] = int(any(n >= target for n in per_day.values()))
    supplied = _cfg_value(cfg, "values", {})
    if isinstance(supplied, Mapping):
        values.update(supplied)
    return values


def badge_status(cur, progress, cfg=None):
    """Return the canonical descriptor/evaluator rows for every badge.

    ``cfg`` is intentionally a plain mapping or small namespace.  It may carry
    ``events``, ``target`` and precomputed values such as the key-family count
    when a caller already owns that domain-specific parser.  The function has
    no Textual/Rich dependency and is therefore safe for static trees, tests,
    and future renderers.
    """

    values = _badge_values(cur, progress, cfg)
    rows = []
    for badge in BADGES:
        if badge["rule"] == "stage":
            cell = progress.get("stages", {}).get(badge["stage"], {})
            have = cell.get("done", 0) + cell.get("reviews_done", 0)
            need = cell.get("total", 0) + cell.get("reviews_total", 0)
            earned = cell.get("state") == "mastered"
        else:
            have = values.get(badge["rule"], 0)
            need = badge.get("need", 1)
            earned = have >= need
        if badge.get("runtime"):
            earned = badge["id"] in progress.get("badges", [])
        rows.append(dict(badge, have=min(have, need), need=need, earned=earned))
    return rows

# Animation timing (seconds). Effects are off under NO_COLOR, TERM=dumb and
# VIM_DAILY_ANIM=off; see dashboard_tui.animations_enabled().
ANIM = {
    "tick": 0.12,          # one frame of every running effect
    "sweep_period": 3.0,   # gradient sweep across the level title
    "pulse_period": 1.2,   # streak flame glow on a personal best
    "sparkle_every": 4,    # sparkle frames per step on the next-badge line
}


# Badge trophies (VD-60): art shown on a badge's page. Stone Story frames are
# imported from share/stone_story_variants.py so there is one copy of each;
# `source` is the sheet in share/audits/STONE_STORY_LOCAL_PROVENANCE.md.
STONE_STORY_CREDIT = "Art: Stone Story RPG by Gabriel Santos (Martian Rex, Inc.)"
TUTOR_CREDIT = "Art: original to this tutor"


def _stone(name):
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "vim_daily_stone_story_variants", Path(__file__).with_name("stone_story_variants.py"))
    SV = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(SV)
    return list(getattr(SV, name))


# Mine Walker boiler flame, flame A (VV). Composite of the MineManager layers
# as audited in share/audits/stone-story-animation-audit/batch-0.md.
MINE_WALKER_FLAME = [
    "   _,—-.___",
    "  _\\     _ \\",
    " | |)   (_) \\",
    " |_/_//______|",
    "  VV//  //",
    "    \\\\  \\\\",
    "    /|\\ /|\\",
]

_TROPHY_SPEC = {
    "first-step": ("stone", "SKULLY_IDLE", "official-Pets/Skully res01"),
    "transfer": ("stone", "FIREWORK_RADIAL_F3", "official-Cosmetics/Fireworks"),
    "transfer-adept": ("stone", "FIREWORK_RADIAL_F4", "official-Cosmetics/Fireworks"),
    "grid-author": ("stone", "SNOWMAN_CHEER_CROP", "official-Pets/Snowman"),
    "still-artist": ("stone", "FIREWORK_CANOPY", "official-Cosmetics/Fireworks"),
    "branch-rescuer": ("stone", "PALLAS_GHOST_LEFT_CALM", "official-Foes/PallasCrown"),
    "streak-keeper-7": ("rows", MINE_WALKER_FLAME, "official-Cosmetics/MineManager"),
    "streak-keeper-14": ("rows", MINE_WALKER_FLAME, "official-Cosmetics/MineManager"),
    "streak-keeper-30": ("rows", MINE_WALKER_FLAME, "official-Cosmetics/MineManager"),
    "animator": ("tutor", ["/--\\", "|oo|", "\\__/'"], "share/animation_lesson_pack.md bell"),
}


def trophy_for(badge_id):
    """{art, credit, source} for a badge, or None when it has no trophy."""
    spec = _TROPHY_SPEC.get(badge_id)
    if not spec:
        return None
    kind, art, source = spec
    if kind == "stone":
        return {"art": _stone(art), "credit": STONE_STORY_CREDIT, "source": source}
    credit = STONE_STORY_CREDIT if kind == "rows" else TUTOR_CREDIT
    return {"art": list(art), "credit": credit, "source": source}
