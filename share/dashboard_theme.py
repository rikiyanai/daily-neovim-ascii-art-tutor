"""Dashboard look as data (VD-58): tier colours, level avatars, badges, glyphs.

Everything a style guide may change lives here as plain values, so a later
style pass can replace them without touching share/dashboard_tui.py.

All avatar art in this file is original to this repository (the repository is
public): small shapes drawn for the level ladder, no third-party art.
"""

# Level tiers. A level belongs to the last tier whose `from_level` it reaches.
# `colour` None = the terminal's own foreground (beginner has no colour).
# `gradient` = colour stops swept across the text (the "gemini" pro tier).
TIERS = [
    {"id": "beginner", "name": "Beginner", "from_level": 1, "colour": None},
    {"id": "intermediate", "name": "Intermediate", "from_level": 4, "colour": "#cd7f32"},
    {"id": "advanced", "name": "Advanced", "from_level": 8, "colour": "#ffd700"},
    {"id": "pro", "name": "Pro", "from_level": 12, "colour": "#8e7cf0",
     "gradient": ["#4285f4", "#7b6cf6", "#b36be0", "#e26d9a", "#f2a65a"]},
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


# Semantic colours (Rich style strings). Every ✓ and every "+N" is `ok`.
STYLE = {
    "ok": "bold #3fd46b",
    "warn": "#f0c040",
    "fail": "bold #ff5f5f",
    "meta": "#8a8f98",
    "key": "bold #5fd7ff",
    "heading": "bold",
    "here": "bold #5fd7ff",
    "bar_full": "#3fd46b",
    "bar_empty": "#4a4f58",
    "flame": "bold #ff8c1a",
    "flame_glow": ["#ff5a1a", "#ff8c1a", "#ffb31a", "#ffd966", "#ffb31a", "#ff8c1a"],
    "sparkle": ["#fff3b0", "#ffd700", "#ffffff", "#b3e5ff"],
    "strip_on": "#3fd46b",
    "strip_off": "#4a4f58",
}

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
]

# Animation timing (seconds). Effects are off under NO_COLOR, TERM=dumb and
# VIM_DAILY_ANIM=off; see dashboard_tui.animations_enabled().
ANIM = {
    "tick": 0.12,          # one frame of every running effect
    "sweep_period": 3.0,   # gradient sweep across the level title
    "pulse_period": 1.2,   # streak flame glow on a personal best
    "sparkle_every": 4,    # sparkle frames per step on the next-badge line
}
