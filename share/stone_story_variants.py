"""Real Stone Story RPG animation frames used as changed-art review/transfer art.

VD-29: the "changed-art" review banks were the card's own art with one border
cell swapped for `!`/`+`, and every module transfer's first variant was
byte-identical to the card itself.  This table replaces those surfaces with
frames taken from the Stone Story animation sheets audited in
`share/audits/stone-story-animation-audit/`.

Every row names its source sheet(s) under SOURCE_ROOT.  StoneScript `#`
transparency is already converted to spaces and rows are right-trimmed.
The generator calls `apply(cards)` after each module's cards are assembled;
`share/test_v2.py` then executes every variant in isolated Neovim.

Licence: third-party art.  The operator waived the redistribution gate for
local use (VD-18); the repository is public, so committing/pushing this file
is a publishing decision recorded in VD-29.
"""

SOURCE_ROOT = "~/Downloads/stone-story-consolidated"


def _variant(start, target, expected, recipe, source, method_label,
             prompt, hint, cursor="^"):
    """One changed-art review.  `prompt`/`hint` describe THIS art: the runtime
    otherwise shows the source card's wording for a different subject."""
    return {
        "prompt": prompt,
        "hint": hint,
        "start": start,
        "target": target,
        "expected": expected,
        "recipe": recipe,
        "cursor": cursor,
        "source": source,
        "method_requirement": {"label": method_label, "exact_any_of": [expected]},
    }


# Frames (verified against the raw sheets, 2026-09-28).
DRACULA_WALK_F3 = ["   \\(}_", ".-´  ,'", " ¯-´>\\"]   # official-Pets/Dracula res01 frame 3
DRACULA_WALK_F4 = ["   \\(}_", ".-´  ,'", " ¯-´|\\"]   # frame 4
DRACULA_WALK_F5 = ["   \\(}_", ".-´  ,'", " ¯-´|>"]    # frame 5
SNOWBUNNY_IDLE = ["   (\\(\\", "  ( n.n)", "o(,`_\"_)"]  # official-Pets/SnowBunny res01
SNOWBUNNY_BLINK = ["   (\\(\\", "  ( -.-)", "o(,`_\"_)"]  # res01 + res03 overlay (stateTime%50>=44)
SKULLY_IDLE = ["     ,--.", "    (_o,o)", "      `\"´"]     # official-Pets/Skully res01
SKULLY_BLINK = ["     ,--.", "    (_=,=)", "      `\"´"]    # res01 + res04 overlay
MISSILE_F1 = ["  ____/", "< / / |:.", "  ¯¯¯¯\\"]            # official-Games/TowerDefense res18 frame 1
MISSILE_F2 = ["  ____/", "< / / |:'", "  ¯¯¯¯\\"]            # frame 2
MISSILE_F3 = ["  ____/", "< / / |::'", "  ¯¯¯¯\\"]           # frame 3
MISSILE_F4 = ["  ____/", "< / / |::.", "  ¯¯¯¯\\"]           # frame 4
SKULLY_LOOK = ["     ,--.", "    (_O,o)", "      `\"´"]     # official-Pets/Skully res01 + res02 look overlay
CHICK_PEEP_F3 = ["  __O<", "`{/ ;", "  ^^"]        # official-Pets/Chick res03 frame 3
CHICK_PEEP_F4 = ["  __O-", "`{/ ;", "  ^^"]        # frame 4
FROG_HALF = ["     ,=-", "  (\\/ .-)", "  ´ ·-\\´\\"]         # official-Pets/Frog res01 + res06 overlay
FROG_ONE_OPEN = ["     ,O-", "  (\\/ .-)", "  ´ ·-\\´\\"]     # res01 + res05 overlay


CHICK_EGG_F1 = ["      ,-.", "     :   :", "     '._.'"]  # official-Pets/Chick res01 frame 1
CHICK_EGG_F2 = ["      ,-.", "     : ; :", "     '._.'"]  # frame 2
CHICK_EGG_F3 = ["      ,-.", "     :·; :", "     '._.'"]  # official-Pets/Chick res01 frame 3 (blank row cropped)
CHICK_EGG_F4 = ["      ,-.", "     :·;,:", "     '._.'"]  # frame 4
FROG_OPEN = ["     ,Oo", "  (\\/ .-)", "  ´ ·-\\´\\"]    # official-Pets/Frog res01 (blank rows cropped)
FROG_SHUT = ["     ,--", "  (\\/ .-)", "  ´ ·-\\´\\"]    # res01 + res07 overlay
DRACULA_STAND = ["   \\(}_", "  ,' ¯/", " '-_.'"]          # official-Pets/Dracula res01 frame 1
DRACULA_WALK_F2 = ["   \\(}_", ".-´  ,'", " ¯-´ \\"]       # frame 2
BOO_HOVER_F2 = ["  .-.", "_(   )_", "`.   .´"]      # frame 2: body expands
BOO_HOVER_F3 = ["  .-.", " (   )", "-´   `-"]       # frame 3
BOO_HOVER_F4 = ["  .-.", " (   )", " /   \\"]       # frame 4: skirt folds inward
SNAIL_OPEN = [" _ Oo", "(O)/", "¯¯¯\""]            # official-Pets/Snail idle; @ spiral -> alphabet-safe O
SNAIL_BLINK = [" _ --", "(O)/", "¯¯¯\""]           # res15 blink over idle body
SNAIL_CRAWL_F4 = [" _ Oo", "(O)/", "´¯¯\""]        # res28-res31 crawl composite
SNAIL_CRAWL_IDLE = [" _ Oo", "(O)/", "¯¯¯\""]      # res32-res35 loop-close composite


def _rail(rows, column):
    """Rows padded with spaces and a `|` drawn at 1-based `column`."""
    return [row.ljust(column - 1) + "|" + row[column:] if len(row) < column
            else row[:column - 1] + "|" + row[column:] for row in rows]


def _rail_rows(rows, column, indices):
    return [_rail([row], column)[0] if i in indices else row for i, row in enumerate(rows)]


def _replace_column(rows, column, glyph):
    """Replace one existing 1-based column in each fixed-width art row."""
    return [row[:column - 1] + glyph + row[column:] for row in rows]


SNAKE_BARE = ["         .-.", "        ((`-'", "         \\\\"]       # official-Pets/Snake res01 rows 1-3
SNAKE_TONGUE = ["         .-.", "        ((`-'-", "         \\\\"]    # res01 + res04/res06 tongue layer
SNAKE_FORK = ["         .-.", "        ((`-'-<", "         \\\\"]     # res01 + res05 forked tongue


# Additional audited animation material. These are hand-transcribed crops,
# not generated stand-ins: `#` transparency becomes spaces, rows are trimmed,
# and ambiguous-width bars use the audit's documented ASCII-safe substitute.
DRILL_TREAD = [" - - - - - -", "\\ _ _ _ _ _ /"]
CAVE_LAVA_A = ["   o", "  /|\\", "    ~ ~ ~ ~ ~ ~ ~"]
CAVE_LAVA_B = ["   o", "  /|\\", "   ~ ~ ~ ~ ~ ~ ~"]
DRILL_TREAD_SCENE = ["'  |---------|~~.", DRILL_TREAD[0], DRILL_TREAD[1]]
FACE_SHOCK = [
    " .' ._. `.",
    "/ --. .-- \\",
    "  (o) (o)",
    "    ___",
    "\\  /___\\  /",
    " `._   _.'",
]
FACE_SHOCK_WOUND = [
    FACE_SHOCK[0],
    FACE_SHOCK[1],
    FACE_SHOCK[2],
    "    ___.",
    "\\  /___\\` /",
    FACE_SHOCK[5],
]
FACE_NEUTRAL = [
    " .'     `.",
    "/ __   __ \\",
    "  <o) (o>",
    "",
    "\\   ---   /",
    " `._   _.'",
]
TANK_IDLE = [
    "          o",
    " /-\\     /|\\_",
    "'  |---------|~~.",
    "   |: |-|   :|=-~\\",
    "   |:  -    :|~~-/",
    "  /-----------\\-'",
    "  \\___________/",
]
FLOWER_HEAD = ["   ( )", "    ζ", "    |", "  . | ,", "   \\|/"]
FIREWORK_SHELL = ["    .'.", "    ,*,", "    '.'", "", ""]
FIREWORK_CANOPY = [" .''.'.''.", "  .,,*,,.", "'  .'.'. '", " ,  .  ,", "  '  .  '"]
FIREWORK_WILLOW_NODES = [" ' .'.'. '", "  ·  .  ·", "  '  .  '"]
FIREWORK_RADIAL_NODES = ["   . : .", "   .\\¡/. ", "  •-—*—-•"]
PAD_1 = ["    _", " ,'   `.", "/    1  \\", "\\       /", " \\/|..-'"]
PAD_2 = ["    _", " ,'   `.", "/    2  \\", "\\       /", " \\/|..-'"]
PAD_3 = ["    _", " ,'   `.", "/    3  \\", "\\       /", " \\/|..-'"]
SKULLY_EQ_PALETTE = [" ,--. [=]", "(_o,o)", "  `\"´"]
SKULLY_O_PALETTE = [" ,--. [O]", "(_o,o)", "  `\"´"]
SKULLY_O_PALETTE_LOOK = [" ,--. [O]", "(_O,o)", "  `\"´"]
SKULLY_OE_PALETTE = [" ,--. [o=]", "(_o,o)", "  `\"´"]
SNOWBUNNY_FACE_PALETTE = ["   (\\(\\ [n-]", "  ( n.n)", "o(,`_\"_)"]
SNOWBUNNY_FACE_PALETTE_BLINK = ["   (\\(\\ [n-]", "  ( -.-)", "o(,`_\"_)"]
SNOWMAN_OPEN_CROP = ["    __", "  _|__|_", ". ( •,•) ,."]
SNOWMAN_BLINK_CROP = ["    __", "  _|__|_", ". ( -,-) ,."]
SNOWMAN_CHEER_CROP = ["    __", "  _|__|_", ". ( ^,^) ,."]


# card id -> {"review_variants": [...]}
# Transfer variants are migrated only after their paired questions are manually
# rewritten around the exact new START/TARGET. M3 and M4 now do this in the
# generator; the remaining module transfers still retain tutor-authored art.
REPLACEMENTS = {
    # M0.01 teaches j0f.ro (find the visible core, replace it in place).
    "M0.01": {"review_variants": [
        _variant(DRACULA_WALK_F3, DRACULA_WALK_F4, "2j0f>r|",
                 [["2j0f>", "go to the cape-hem row and find the trailing foot"],
                  ["r|", "plant the foot: the next walk frame"]],
                 "official-Pets/Dracula res01 walk frame 3 -> 4",
                 "find the changed foot, then replace it in place",
                 "Stone Story Dracula walk: plant the trailing foot on the hem row so frame 3 becomes frame 4. Cape and head stay put.",
                 "Find the foot glyph on the bottom row, then replace that one cell."),
        _variant(DRACULA_WALK_F4, DRACULA_WALK_F5, "2j0f\\r>",
                 [["2j0f\\", "go to the hem row and find the back foot"],
                  ["r>", "kick it forward: the last walk frame"]],
                 "official-Pets/Dracula res01 walk frame 4 -> 5",
                 "find the changed foot, then replace it in place",
                 "Stone Story Dracula walk: kick the back foot forward so frame 4 becomes frame 5. Nothing else moves.",
                 "Find the back-foot glyph on the bottom row, then replace that one cell."),
    ]},
    # M0.SL teaches a line-scoped substitute with the g flag.
    "M0.SL": {"review_variants": [
        _variant(SNOWBUNNY_IDLE, SNOWBUNNY_BLINK, "2G:s/n/-/g<CR>",
                 [["2G", "go to the face row"],
                  [":s/n/-/g<CR>", "close both eyes on this row only"]],
                 "official-Pets/SnowBunny res01 idle -> res03 blink overlay",
                 "blink with one line-scoped substitute",
                 "Stone Story snow bunny blink: close both eyes (n -> -) with one substitute on the face row only.",
                 "Go to the face row; one :s with the g flag changes both eyes."),
        _variant(SKULLY_IDLE, SKULLY_BLINK, "2G:s/o/=/g<CR>",
                 [["2G", "go to the eye row"],
                  [":s/o/=/g<CR>", "narrow both eyes on this row only"]],
                 "official-Pets/Skully res01 idle -> res04 blink overlay",
                 "blink with one line-scoped substitute",
                 "Stone Story Skully blink: narrow both eye sockets (o -> =) with one substitute on the eye row only.",
                 "Go to the eye row; one :s with the g flag changes both eyes."),
    ]},
    # M11.02 teaches gg3yyGp: copy the complete 3-row key pose as a working frame.
    "M11.02": {"review_variants": [
        _variant(MISSILE_F1, MISSILE_F1 + MISSILE_F1, "gg3yyGp",
                 [["gg3yy", "copy all three rows of the missile"],
                  ["Gp", "put the working copy below"]],
                 "official-Games/TowerDefense res18 missile frame 1 (copied)",
                 "copy the complete three-row pose with a counted linewise yank",
                 "Stone Story missile: copy the complete three-row missile as the working frame for its next exhaust puff.",
                 "A count on yy copies whole rows; put the copy after the last line."),
        _variant(CHICK_EGG_F4, CHICK_EGG_F4 + CHICK_EGG_F4, "gg3yyGp",
                 [["gg3yy", "copy all three rows of the cracked egg"],
                  ["Gp", "put the working copy below"]],
                 "official-Pets/Chick res01 hatch frame 4 (copied)",
                 "copy the complete three-row pose with a counted linewise yank",
                 "Stone Story chick egg: copy the complete three-row cracked egg before the hatch frames change it.",
                 "A count on yy copies whole rows; put the copy after the last line."),
    ]},
    # M11.UR teaches replace, undo, redo on one fixed cell.
    "M11.UR": {"review_variants": [
        _variant(CHICK_EGG_F3, CHICK_EGG_F4, "2G0f;lr,u<C-r>",
                 [["2G0f;l", "go to the cell right of the first crack"],
                  ["r,", "add the next crack glyph"],
                  ["u<C-r>", "scrub back one frame and forward again"]],
                 "official-Pets/Chick res01 hatch frame 3 -> 4",
                 "replace one cell, then undo and redo it",
                 "Stone Story egg hatch: add the next crack cell, undo to compare, then redo so frame 4 remains.",
                 "Find the existing crack, step one cell right, replace; u then CTRL-R."),
        _variant(SKULLY_IDLE, SKULLY_LOOK, "2G0forOu<C-r>",
                 [["2G0fo", "go to the eye row and find the left eye"],
                  ["rO", "widen it: Skully looks left"],
                  ["u<C-r>", "scrub back one frame and forward again"]],
                 "official-Pets/Skully res01 -> res02 look overlay",
                 "replace one cell, then undo and redo it",
                 "Stone Story Skully: widen the left eye so it looks left, undo to compare, then redo so the look remains.",
                 "Find the eye on the middle row, replace it; u then CTRL-R."),
    ]},
    # M11.04 teaches Replace mode over two cells, then undo/redo.
    "M11.04": {"review_variants": [
        _variant(SNOWBUNNY_IDLE, SNOWBUNNY_BLINK, "2G0fnR-.-<Esc>u<C-r>",
                 [["2G0fn", "go to the first eye"],
                  ["R-.-<Esc>", "overwrite eye, nose, eye without shifting the row"],
                  ["u<C-r>", "compare, then keep the blink"]],
                 "official-Pets/SnowBunny res01 -> res03 blink overlay",
                 "overwrite cells in Replace mode, then undo and redo",
                 "Stone Story snow bunny: overwrite the n.n face with the -.- blink in Replace mode; undo, then redo.",
                 "Replace mode overwrites; it never pushes the rest of the row."),
        _variant(FROG_OPEN, FROG_SHUT, "0f,lR--<Esc>u<C-r>",
                 [["0f,l", "go to the first eye"],
                  ["R--<Esc>", "overwrite both eyes shut"],
                  ["u<C-r>", "compare, then keep the blink"]],
                 "official-Pets/Frog res01 -> res07 blink overlay",
                 "overwrite two cells in Replace mode, then undo and redo",
                 "Stone Story frog blink: overwrite both eyes shut in Replace mode; undo, then redo.",
                 "Find the comma before the eyes; Replace mode keeps the row width."),
    ]},
    # M11.05 teaches a line-scoped substitute on one frame of a strip.
    "M11.05": {"review_variants": [
        _variant(MISSILE_F3, MISSILE_F4, "2G:s/'/./<CR>",
                 [["2G", "go to the exhaust row"],
                  [":s/'/./<CR>", "drop the last exhaust puff on this row"]],
                 "official-Games/TowerDefense res18 missile frame 3 -> 4",
                 "change one row with a line-scoped substitute",
                 "Stone Story missile: drop the trailing exhaust puff ' to . with one substitute on the exhaust row.",
                 "A substitute without a range acts only on the cursor's line."),
        _variant(FROG_OPEN, FROG_HALF, "1G:s/Oo/=-/<CR>",
                 [["1G", "go to the eye row"],
                  [":s/Oo/=-/<CR>", "half-close both eyes on this row"]],
                 "official-Pets/Frog res01 -> res06 blink overlay",
                 "change one row with a line-scoped substitute",
                 "Stone Story frog blink: half-close the eyes Oo into =- with one substitute on the eye row.",
                 "A substitute without a range acts only on the cursor's line."),
    ]},
    # M11.VE teaches virtualedit to draw past the end of short rows.
    "M11.VE": {"review_variants": [
        _variant(CHICK_PEEP_F4, _rail(CHICK_PEEP_F4, 9), ":set virtualedit=all<CR>gg9|i|<Esc>2G9|i|<Esc>3G9|i|<Esc>",
                 [[":set virtualedit=all<CR>", "let the cursor stand in empty cells"],
                  ["gg9|i|<Esc>2G9|i|<Esc>3G9|i|<Esc>", "draw a fence post at column 9 on all three rows"]],
                 "official-Pets/Chick res03 frame 4 + drawn fence post",
                 "draw past the end of short rows with virtualedit",
                 "Stone Story chick: draw a fence post at column 9 beside all three rows, though the rows end earlier.",
                 "virtualedit=all lets a column motion land past the end of a row."),
        _variant(DRACULA_STAND, _rail(DRACULA_STAND, 9), ":set virtualedit=all<CR>gg9|i|<Esc>2G9|i|<Esc>3G9|i|<Esc>",
                 [[":set virtualedit=all<CR>", "let the cursor stand in empty cells"],
                  ["gg9|i|<Esc>2G9|i|<Esc>3G9|i|<Esc>", "draw a doorway edge at column 9 on all three rows"]],
                 "official-Pets/Dracula res01 stand + drawn doorway edge",
                 "draw past the end of short rows with virtualedit",
                 "Stone Story Dracula: draw a doorway edge at column 9 beside all three rows, though the rows end earlier.",
                 "virtualedit=all lets a column motion land past the end of a row."),
    ]},
    # M11.08 teaches virtualedit on the same row of two frames.
    "M11.08": {"review_variants": [
        _variant(CHICK_PEEP_F3 + CHICK_PEEP_F4, _rail_rows(CHICK_PEEP_F3 + CHICK_PEEP_F4, 13, {1, 4}),
                 ":set virtualedit=all<CR>2G13|i|<Esc>3j13|i|<Esc>",
                 [[":set virtualedit=all<CR>", "let the cursor stand in empty cells"],
                  ["2G13|i|<Esc>3j13|i|<Esc>", "mark the body row of both frames at column 13"]],
                 "official-Pets/Chick res03 peep frames 3-4 + drawn marks",
                 "mark the same row of two frames past the end of the line",
                 "Stone Story chick peep: mark the body row of both frames at column 13 so their registration can be compared.",
                 "The same row of the next frame is three lines down."),
        _variant(DRACULA_WALK_F2 + DRACULA_WALK_F3, _rail_rows(DRACULA_WALK_F2 + DRACULA_WALK_F3, 13, {1, 4}),
                 ":set virtualedit=all<CR>2G13|i|<Esc>3j13|i|<Esc>",
                 [[":set virtualedit=all<CR>", "let the cursor stand in empty cells"],
                  ["2G13|i|<Esc>3j13|i|<Esc>", "mark the cape row of both frames at column 13"]],
                 "official-Pets/Dracula res01 walk frames 2-3 + drawn marks",
                 "mark the same row of two frames past the end of the line",
                 "Stone Story Dracula walk: mark the cape row of both frames at column 13 so their registration can be compared.",
                 "The same row of the next frame is three lines down."),
    ]},
    # M1.DD teaches deleting one complete redundant frame (count + dd).
    "M1.DD": {"review_variants": [
        _variant(MISSILE_F1 + MISSILE_F1 + MISSILE_F2, MISSILE_F1 + MISSILE_F2, "4G3dd",
                 [["4G", "go to the first row of the accidental duplicate"],
                  ["3dd", "delete its three rows as one frame"]],
                 "official-Games/TowerDefense res18 missile frames 1,1,2 (duplicate removed)",
                 "delete one complete frame with a counted dd",
                 "Stone Story missile strip: frame 2 is an accidental copy of frame 1. Delete that whole frame so the exhaust animates.",
                 "Start on the duplicate's first row; a count on dd removes whole rows."),
        _variant(DRACULA_WALK_F2 + DRACULA_WALK_F3 + DRACULA_WALK_F3, DRACULA_WALK_F2 + DRACULA_WALK_F3, "7G3dd",
                 [["7G", "go to the first row of the repeated frame"],
                  ["3dd", "delete its three rows as one frame"]],
                 "official-Pets/Dracula res01 walk frames 2,3,3 (duplicate removed)",
                 "delete one complete frame with a counted dd",
                 "Stone Story Dracula walk: the last frame repeats frame 3 with no timing purpose. Delete that whole frame.",
                 "Start on the duplicate's first row; a count on dd removes whole rows."),
    ]},
    # M3.CI teaches ci( : change everything inside a parenthesised object.
    "M3.CI": {"review_variants": [
        _variant(SNOWBUNNY_IDLE, SNOWBUNNY_BLINK, "2G0f(ci( -.-<Esc>",
                 [["2G0f(", "go to the face row and find its opening paren"],
                  ["ci( -.-<Esc>", "replace the whole face inside the parens"]],
                 "official-Pets/SnowBunny res01 -> res03 blink overlay",
                 "change inside the face's parentheses",
                 "Stone Story snow bunny: swap the whole face inside ( ) for the blink face ' -.-'; both parens stay.",
                 "ci( replaces what is between the parens and keeps the parens."),
        _variant(SKULLY_IDLE, SKULLY_BLINK, "2G0f(ci(_=,=<Esc>",
                 [["2G0f(", "go to the eye row and find its opening paren"],
                  ["ci(_=,=<Esc>", "replace everything inside the parens with the blink"]],
                 "official-Pets/Skully res01 -> res04 blink overlay",
                 "change inside the skull's parentheses",
                 "Stone Story Skully: swap everything inside ( ) for the blink '_=,='; both parens stay.",
                 "ci( replaces what is between the parens and keeps the parens."),
    ]},
    # M3.REG teaches a named-register copy of a whole pose, then one acting change.
    "M3.REG": {"review_variants": [
        _variant(SKULLY_IDLE, SKULLY_IDLE + SKULLY_LOOK, 'ggV2j"ayG"ap5G0forO',
                 [['ggV2j"ay', "yank the three-row skull into register a"],
                  ['G"ap', "put the copy below as the next frame"],
                  ["5G0forO", "widen the copy's left eye: it looks left"]],
                 "official-Pets/Skully res01 -> res01 + res02 look overlay",
                 "copy the pose through register a, then change the copy",
                 "Stone Story Skully: copy the idle skull through register a, then make only the copy look left.",
                 "Yank the three rows into a named register, put it at the end, then edit the copy's eye row."),
        _variant(FROG_OPEN, FROG_OPEN + FROG_ONE_OPEN, 'ggV2j"ayG"ap4G0for-',
                 [['ggV2j"ay', "yank the three-row frog into register a"],
                  ['G"ap', "put the copy below as the next frame"],
                  ["4G0for-", "close the copy's right eye"]],
                 "official-Pets/Frog res01 -> res01 + res05 blink overlay",
                 "copy the pose through register a, then change the copy",
                 "Stone Story frog: copy the frog through register a, then close only the copy's right eye.",
                 "Yank the three rows into a named register, put it at the end, then edit the copy's eye row."),
    ]},
    # M6.MOVE / M16.MOVE teach :{range}m$ to fix playback order without copying.
    "M6.MOVE": {"review_variants": [
        _variant(DRACULA_WALK_F3 + DRACULA_WALK_F2, DRACULA_WALK_F2 + DRACULA_WALK_F3, ":1,3m$<CR>",
                 [[":1,3m$<CR>", "move the first three-row frame after the second"]],
                 "official-Pets/Dracula res01 walk frames 3,2 -> 2,3",
                 "reorder two frames with an addressed move",
                 "Stone Story Dracula walk: the frames play out of order (3 before 2). Move the first frame after the second; copy nothing.",
                 "An Ex move takes a line range and a destination line."),
        _variant(CHICK_EGG_F2 + CHICK_EGG_F1, CHICK_EGG_F1 + CHICK_EGG_F2, ":1,3m$<CR>",
                 [[":1,3m$<CR>", "move the cracked egg after the whole egg"]],
                 "official-Pets/Chick res01 hatch frames 2,1 -> 1,2",
                 "reorder two frames with an addressed move",
                 "Stone Story egg hatch: the cracked egg plays before the whole egg. Move the first frame after the second; copy nothing.",
                 "An Ex move takes a line range and a destination line."),
    ]},
    "M16.MOVE": {"review_variants": [
        _variant(MISSILE_F2 + MISSILE_F1, MISSILE_F1 + MISSILE_F2, ":1,3m$<CR>",
                 [[":1,3m$<CR>", "move the first three-row frame after the second"]],
                 "official-Games/TowerDefense res18 missile frames 2,1 -> 1,2",
                 "reorder two planned frames with an addressed move",
                 "Stone Story missile plan: frame 2 is filed before frame 1. Move the first block after the second; copy nothing.",
                 "An Ex move takes a line range and a destination line."),
        _variant(SKULLY_BLINK + SKULLY_IDLE, SKULLY_IDLE + SKULLY_BLINK, ":1,3m$<CR>",
                 [[":1,3m$<CR>", "move the blink after the open-eyed key"]],
                 "official-Pets/Skully res04,res01 -> res01,res04",
                 "reorder two planned frames with an addressed move",
                 "Stone Story Skully plan: the blink is filed before the open-eyed key pose. Move the first block after the second.",
                 "An Ex move takes a line range and a destination line."),
    ]},
    # M7.GLOBAL teaches :g/pattern/normal! to repeat one edit on every matching row.
    "M7.GLOBAL": {"review_variants": [
        _variant(SKULLY_IDLE + SKULLY_IDLE, SKULLY_LOOK + SKULLY_LOOK, ":g/o/normal! 0forO<CR>",
                 [[":g/o/", "select every row that contains an eye"],
                  ["normal! 0forO<CR>", "on each, widen the first eye"]],
                 "official-Pets/Skully res01 x2 -> res02 look overlay x2",
                 "repeat one Normal edit on every matching row with :g",
                 "Stone Story Skully held for two frames: make both copies look left with one :g command.",
                 ":g runs the same Normal keys on every row that matches."),
        _variant(FROG_OPEN + FROG_OPEN, FROG_ONE_OPEN + FROG_ONE_OPEN, ":g/o/normal! 0for-<CR>",
                 [[":g/o/", "select every row that contains the open eye"],
                  ["normal! 0for-<CR>", "on each, close that eye"]],
                 "official-Pets/Frog res01 x2 -> res05 blink overlay x2",
                 "repeat one Normal edit on every matching row with :g",
                 "Stone Story frog held for two frames: close the right eye in both copies with one :g command.",
                 ":g runs the same Normal keys on every row that matches."),
    ]},
    # M7.DOT teaches one change followed by dot repeat on homologous rows.
    "M7.DOT": {"review_variants": [
        _variant(FROG_OPEN * 3, FROG_ONE_OPEN * 3, "gg0for-3j.3j.",
                 [["gg0for-", "close the right eye in the first held frame"],
                  ["3j.3j.", "repeat that change on the same row of the next two frames"]],
                 "official-Pets/Frog res01 x3 -> res05 blink overlay x3",
                 "make one change, then dot-repeat it on the matching rows",
                 "Stone Story frog held for three frames: close the right eye in the first, then repeat the change on the other two with dot.",
                 "The eye row of each frame is three lines below the last; . repeats the whole r change."),
        _variant(SKULLY_IDLE * 3, SKULLY_LOOK * 3, "2G0forO3j.3j.",
                 [["2G0forO", "widen the left eye in the first held frame"],
                  ["3j.3j.", "repeat that change on the same row of the next two frames"]],
                 "official-Pets/Skully res01 x3 -> res02 look overlay x3",
                 "make one change, then dot-repeat it on the matching rows",
                 "Stone Story Skully held for three frames: make the first look left, then repeat the change on the other two with dot.",
                 "The eye row of each frame is three lines below the last; . repeats the whole r change."),
    ]},
    # M6.D teaches D: delete from the cursor to the end of the row, keeping the anchor.
    "M6.D": {"review_variants": [
        _variant(SNAKE_TONGUE, SNAKE_BARE, "2G0f'lD",
                 [["2G0f'l", "go to the first tongue cell after the mouth"],
                  ["D", "delete the tongue to the end of the row"]],
                 "official-Pets/Snake res01 + res06 tongue -> bare head",
                 "delete to the end of the row after a landmark",
                 "Stone Story snake: retract the tongue. Delete from the first tongue cell to the end of the row; the head stays.",
                 "Find the mouth corner, step right once, then delete to the end of the row."),
        _variant(SNAKE_FORK, SNAKE_TONGUE, "2G0f'2lD",
                 [["2G0f'2l", "go to the fork tip"],
                  ["D", "delete the fork to the end of the row"]],
                 "official-Pets/Snake res01 + res05 fork -> res06 tongue",
                 "delete to the end of the row after a landmark",
                 "Stone Story snake: pull the forked tip back in. Delete only the fork; the tongue stays out.",
                 "Find the mouth corner, step to the fork, then delete to the end of the row."),
    ]},
    # M15.GLOBAL teaches :g/pattern/normal! on the rows a pattern selects.
    "M15.GLOBAL": {"review_variants": [
        _variant(MISSILE_F1 + MISSILE_F1, MISSILE_F2 + MISSILE_F2, ":g/:/normal! 0f.r'<CR>",
                 [[":g/:/", "select every exhaust row (the rows that contain :)"],
                  ["normal! 0f.r'<CR>", "on each, flick the last puff upward"]],
                 "official-Games/TowerDefense res18 missile frame 1 x2 -> frame 2 x2",
                 "edit only the rows a global pattern selects",
                 "Stone Story missile, two held frames: advance the exhaust in both with one :g command; hull rows stay.",
                 "Only the exhaust rows contain ':' so :g picks exactly those."),
        _variant(CHICK_EGG_F3 + CHICK_EGG_F3, CHICK_EGG_F4 + CHICK_EGG_F4, ":g/;/normal! 0f;lr,<CR>",
                 [[":g/;/", "select every cracked row (the rows that contain ;)"],
                  ["normal! 0f;lr,<CR>", "on each, add the next crack cell"]],
                 "official-Pets/Chick res01 hatch frame 3 x2 -> frame 4 x2",
                 "edit only the rows a global pattern selects",
                 "Stone Story egg, two held frames: grow the crack in both with one :g command; shell top and base stay.",
                 "Only the cracked rows contain ';' so :g picks exactly those."),
    ]},
    # M15.MAC teaches recording one find-and-replace, then replaying it.
    "M15.MAC": {"review_variants": [
        _variant(SKULLY_IDLE, SKULLY_BLINK, "2G0qqfor=q0@q",
                 [["2G0", "go to the start of the eye row"],
                  ["qqfor=q", "record: find the next eye, narrow it"],
                  ["0@q", "replay from the row start for the second eye"]],
                 "official-Pets/Skully res01 -> res04 blink overlay",
                 "record one find-and-replace, then replay it",
                 "Stone Story Skully blink: record narrowing one eye as macro q, then replay it for the other eye.",
                 "After the first eye becomes =, the same f o lands on the second eye."),
        _variant(SNOWBUNNY_IDLE, SNOWBUNNY_BLINK, "2G0qqfnr-q0@q",
                 [["2G0", "go to the start of the face row"],
                  ["qqfnr-q", "record: find the next open eye, close it"],
                  ["0@q", "replay from the row start for the second eye"]],
                 "official-Pets/SnowBunny res01 -> res03 blink overlay",
                 "record one find-and-replace, then replay it",
                 "Stone Story snow bunny blink: record closing one eye as macro q, then replay it for the other eye.",
                 "After the first eye becomes -, the same f n lands on the second eye."),
    ]},
    # M12.FIND teaches f plus ; and , on repeated landmarks. These are real
    # moving material rows, not the old box with a changed border glyph.
    "M12.FIND": {"review_variants": [
        _variant(CAVE_LAVA_A, [CAVE_LAVA_A[0], CAVE_LAVA_A[1], "    ! ! ~ ~ ~ ~ ~"],
                 "3G0f~;r!,r!",
                 [["3G0f~", "find the first lava crest on the acting row"],
                  [";r!", "repeat the find forward and mark the second crest"],
                  [",r!", "reverse the same find and mark the first crest"]],
                 "official-Cosmetics/CaveParty res06 lava frame 1",
                 "find, repeat, and reverse across one animated lava row",
                 "Cave Party lava: mark the first two crests as the leading pulse; do not touch the offset row below.",
                 "Find one ~, repeat that find forward, then reverse the same find."),
        _variant(DRILL_TREAD_SCENE,
                 [DRILL_TREAD_SCENE[0], " ! ! - - - -", DRILL_TREAD_SCENE[2]],
                 "2G0f-;r!,r!",
                 [["2G0f-", "find the first bright tread cell"],
                  [";r!", "repeat forward to the second tread cell"],
                  [",r!", "return to the first tread cell"]],
                 "official-Cosmetics/Drill res26 tread shimmer layer",
                 "find, repeat, and reverse across a moving tread pattern",
                 "Stone Story drill tread: mark the first two moving tread cells; the lower track remains registered.",
                 "Use ; to repeat the dash find and , to reverse it."),
    ]},
    # M13.BE teaches WORD starts/ends on the separated cells of a real lava
    # texture. The two frames differ in their authored one-column phase.
    "M13.BE": {"review_variants": [
        _variant(CAVE_LAVA_A,
                 [CAVE_LAVA_A[0], CAVE_LAVA_A[1], "    ~ ! + ? ~ ~ ~"],
                 "3G0WEr!2Wr?Br+",
                 [["3G0WE", "reach the end of the next lava cell"],
                  ["r!2Wr?", "mark it, then count two WORD starts to the next mark"],
                  ["Br+", "move back one WORD start for the middle mark"]],
                 "official-Cosmetics/CaveParty res06 lava frame 1",
                 "retouch bounded lava cells with W, E, and B",
                 "Cave Party lava: retouch three internal crest cells while the first crest and the lower phase stay fixed.",
                 "Spaces make each ~ a WORD; use the starts and ends rather than counting columns."),
        _variant(CAVE_LAVA_B,
                 [CAVE_LAVA_B[0], CAVE_LAVA_B[1], "   ~ ! + ? ~ ~ ~"],
                 "3G0WEr!2Wr?Br+",
                 [["3G0WE", "reach the end of the next crest cell"],
                  ["r!2Wr?", "mark it and count forward by WORD starts"],
                  ["Br+", "return one WORD start for the middle mark"]],
                 "official-Cosmetics/CaveParty res06 lava frame 2",
                 "retouch bounded cells in the shifted lava phase",
                 "Cave Party lava, shifted phase: retouch the same three internal cells without moving either row.",
                 "Treat each separated ~ as one WORD-shaped texture cell."),
    ]},
    # M14 is the variant palette module. The palette is written beside real
    # Skully/SnowBunny poses so the register has a visible, meaningful source.
    "M14.01": {"review_variants": [
        _variant(SKULLY_EQ_PALETTE,
                 [SKULLY_EQ_PALETTE[0], "(_=,o)", SKULLY_EQ_PALETTE[2]],
                 "ggf=\"aylj0foR<C-r>a<Esc>",
                 [["ggf=\"ayl", "store the blink material in register a"],
                  ["j0foR<C-r>a<Esc>", "retrieve it over the left eye without shifting the skull"]],
                 "official-Hats/Skully res01 + res06 eye material",
                 "retrieve a real Skully eye material through register a",
                 "Skully palette: store = from the visible palette, then apply it to only the left eye.",
                 "Yank the palette cell into register a; Replace mode can insert that register without changing width."),
        _variant(SKULLY_O_PALETTE,
                 [SKULLY_O_PALETTE[0], "(_O,o)", SKULLY_O_PALETTE[2]],
                 "ggfO\"aylj0foR<C-r>a<Esc>",
                 [["ggfO\"ayl", "store the wide look material in register a"],
                  ["j0foR<C-r>a<Esc>", "retrieve it over the left eye"]],
                 "official-Hats/Skully res01 + res04 look material",
                 "retrieve the alternate Skully eye material through register a",
                 "Skully look: store O from the visible palette, then widen only the left eye.",
                 "The palette is on the top row; the acting eye is one row below."),
    ]},
    "M14.04": {"review_variants": [
        _variant(SKULLY_EQ_PALETTE + [""] + SKULLY_EQ_PALETTE,
                 SKULLY_EQ_PALETTE + [""] +
                 [SKULLY_EQ_PALETTE[0], "(_=,o)", SKULLY_EQ_PALETTE[2]],
                 "5Gf=\"aylj0foR<C-r>a<Esc>",
                 [["5Gf=\"ayl", "store = from the copied pose's palette"],
                  ["j0foR<C-r>a<Esc>", "blink only the copied left eye"]],
                 "official-Hats/Skully res01 + res06 eye material",
                 "change only the copied Skully pose through register a",
                 "Two Skully frames: leave the first open-eyed; apply the blink material only to the copy.",
                 "Start on the copied palette row, then replace one eye in the row below."),
        _variant(SKULLY_O_PALETTE + [""] + SKULLY_O_PALETTE,
                 SKULLY_O_PALETTE + [""] +
                 [SKULLY_O_PALETTE[0], "(_O,o)", SKULLY_O_PALETTE[2]],
                 "5GfO\"aylj0foR<C-r>a<Esc>",
                 [["5GfO\"ayl", "store O from the copied pose's palette"],
                  ["j0foR<C-r>a<Esc>", "make only the copy look left"]],
                 "official-Hats/Skully res01 + res04 look material",
                 "change only the copied Skully look through register a",
                 "Two Skully frames: the first holds; widen only the copied frame's left eye.",
                 "Use the palette belonging to the second paragraph frame."),
    ]},
    "M14.08": {"review_variants": [
        _variant(SKULLY_OE_PALETTE + [""] +
                 [SKULLY_OE_PALETTE[0], "(_=,=)", SKULLY_OE_PALETTE[2]] + [""] +
                 [SKULLY_OE_PALETTE[0], "(_=,=)", SKULLY_OE_PALETTE[2]],
                 SKULLY_OE_PALETTE + [""] +
                 [SKULLY_OE_PALETTE[0], "(_=,=)", SKULLY_OE_PALETTE[2]] + [""] +
                 [SKULLY_OE_PALETTE[0], "(_o,=)", SKULLY_OE_PALETTE[2]],
                 "ggfo\"bylgg}}jj0f=R<C-r>b<Esc>",
                 [["ggfo\"byl", "store the first frame's open-eye material in register b"],
                  ["gg}}jj", "cross two blank-line-separated frame objects"],
                  ["0f=R<C-r>b<Esc>", "restore the third frame's left eye"]],
                 "official-Hats/Skully res01 + res06 blink material",
                 "carry an eye material across three paragraph frames",
                 "Skully sequence: open, blink, blink. Restore the left eye only in frame 3 from frame 1's palette.",
                 "Two } motions cross the two frame boundaries; then edit the eye row."),
        _variant(SNOWBUNNY_FACE_PALETTE + [""] +
                 [SNOWBUNNY_FACE_PALETTE[0], "  ( -.-)", SNOWBUNNY_FACE_PALETTE[2]] + [""] +
                 [SNOWBUNNY_FACE_PALETTE[0], "  ( -.-)", SNOWBUNNY_FACE_PALETTE[2]],
                 SNOWBUNNY_FACE_PALETTE + [""] +
                 [SNOWBUNNY_FACE_PALETTE[0], "  ( -.-)", SNOWBUNNY_FACE_PALETTE[2]] + [""] +
                 [SNOWBUNNY_FACE_PALETTE[0], "  ( n.-)", SNOWBUNNY_FACE_PALETTE[2]],
                 "ggfn\"bylgg}}jj0f-R<C-r>b<Esc>",
                 [["ggfn\"byl", "store the open-eye material in register b"],
                  ["gg}}jj", "cross two complete bunny frame objects"],
                  ["0f-R<C-r>b<Esc>", "reopen the third frame's left eye"]],
                 "official-Pets/SnowBunny res01 + res03 blink overlay",
                 "carry a SnowBunny eye material across three frames",
                 "Snow bunny sequence: open, blink, blink. Reopen only the left eye of frame 3.",
                 "Use paragraph motion for frames; use the saved material only after reaching frame 3."),
    ]},
    # Real tread/lava rows replace the fake brick-border permutations.
    "M15.01": {"review_variants": [
        _variant(DRILL_TREAD_SCENE,
                 [DRILL_TREAD_SCENE[0], DRILL_TREAD_SCENE[1], " " + DRILL_TREAD_SCENE[2]],
                 "2j:set shiftwidth=1<CR>>>",
                 [["2j", "select the lower moving tread row"],
                  [":set shiftwidth=1<CR>", "make one indent step one fixed-grid cell"],
                  [">>", "offset only that tread row"]],
                 "official-Cosmetics/Drill res26 tread shimmer layer",
                 "offset one real tread row by exactly one cell",
                 "Drill tread shimmer: offset only the lower track by one cell; the upper phase stays fixed.",
                 "Set the width of one indent step before shifting the acting row."),
        _variant(CAVE_LAVA_A,
                 [CAVE_LAVA_A[0], CAVE_LAVA_A[1], " " + CAVE_LAVA_A[2]],
                 "2j:set shiftwidth=1<CR>>>",
                 [["2j", "select the lava-material row"],
                  [":set shiftwidth=1<CR>>>", "offset that row by one cell"]],
                 "official-Cosmetics/CaveParty res06 lava frame 1",
                 "offset one lava phase row by exactly one cell",
                 "Cave Party lava: shift the upper phase one cell right; leave the staggered lower phase registered.",
                 "The two figure rows are stable; 2j lands on the acting texture row."),
    ]},
    # The frame numbers are part of the original FrogBog pad sequence.
    "M16.01": {"review_variants": [
        _variant(PAD_1, PAD_2, "3G0f1<C-a>",
                 [["3G0f1", "find the written frame number on the pad"],
                  ["<C-a>", "increment 1 to 2 without retyping the pose"]],
                 "official-Games/FrogBog res05 -> res06 lily-pad frames",
                 "increment a real animation frame label in place",
                 "FrogBog lily pad: advance the written frame label from 1 to 2; the pad silhouette stays identical.",
                 "CTRL-A increments the number under the cursor and preserves the surrounding art."),
        _variant(PAD_2, PAD_3, "3G0f2<C-a>",
                 [["3G0f2", "find the second written frame number"],
                  ["<C-a>", "increment 2 to 3"]],
                 "official-Games/FrogBog res06 -> res07 lily-pad frames",
                 "increment the next FrogBog frame label in place",
                 "FrogBog lily pad: advance label 2 to label 3 without redrawing the pad.",
                 "Find the digit first; CTRL-A changes only the number."),
    ]},
    # FaceHUD and the flower/egg sequences replace copied stick figures.
    "M3.04": {"review_variants": [
        _variant(FACE_SHOCK + FACE_SHOCK,
                 FACE_SHOCK + [FACE_SHOCK[0], FACE_SHOCK[1], "  (O) (o)"] + FACE_SHOCK[3:],
                 "9G0f(ci(O<Esc>",
                 [["9G0f(", "reach the copied pose's first parenthesised eye"],
                  ["ci(O<Esc>", "widen only the eye inside its parentheses"]],
                 "official-UI/FaceHUD res08 shock pose (copied)",
                 "change one acting feature inside the copied FaceHUD pose",
                 "FaceHUD shock: the first six-row pose holds; widen only the copied pose's left eye.",
                 "ci( keeps the eye's enclosing parentheses, so the head does not shift."),
        _variant(FACE_SHOCK_WOUND + FACE_SHOCK_WOUND,
                 FACE_SHOCK_WOUND +
                 [FACE_SHOCK_WOUND[0], FACE_SHOCK_WOUND[1], "  (o) (O)"] + FACE_SHOCK_WOUND[3:],
                 "9G0f(;ci(O<Esc>",
                 [["9G0f(;", "reach the copied pose's second parenthesised eye"],
                  ["ci(O<Esc>", "widen only that eye inside its parentheses"]],
                 "official-UI/FaceHUD res08 shock pose + res10 wound overlay (copied, right eye)",
                 "change the other acting feature inside a copied FaceHUD pose",
                 "FaceHUD shock: the first six-row pose holds; widen only the copied pose's right eye.",
                 "Repeat the parenthesis find once, then ci( keeps the enclosing eye shape fixed."),
    ]},
    "M3.DI": {"review_variants": [
        _variant(FROG_OPEN, ["     ,·o", FROG_OPEN[1], FROG_OPEN[2]],
                 "gg0fOr<C-k>.M",
                 [["gg0fO", "find the frog's left eye"],
                  ["r<C-k>.M", "replace it with the middle-dot digraph"]],
                 "official-Pets/Frog res01 open-eye pose",
                 "enter a middle-dot in-between marker with a digraph",
                 "Stone Story frog: mark the left eye with a centred middle-dot as an in-between guide; the head width stays fixed.",
                 "Use replace plus the .M digraph; insertion would shift the other eye."),
        _variant(CHICK_EGG_F2, CHICK_EGG_F3, "2G0f;hr<C-k>.M",
                 [["2G0f;h", "land on the blank cell immediately before the crack"],
                  ["r<C-k>.M", "place the next crack speck with the middle-dot digraph"]],
                 "official-Pets/Chick res01 hatch frame 2 -> 3",
                 "enter the egg's next crack speck with a digraph",
                 "Chick hatch: add the middle-dot crack speck before the semicolon; shell width stays fixed.",
                 "Find the existing crack, step left onto its blank cell, then replace that cell."),
    ]},
    "M3.08": {"review_variants": [
        _variant(FACE_SHOCK * 3,
                 FACE_SHOCK * 2 + [FACE_SHOCK[0], FACE_SHOCK[1], "  (·) (o)"] + FACE_SHOCK[3:],
                 "15G0for<C-k>.M",
                 [["15G0fo", "go to the final complete FaceHUD pose's left eye"],
                  ["r<C-k>.M", "give only that pose the middle-dot guide"]],
                 "official-UI/FaceHUD res08 shock pose x3",
                 "accent only the final complete six-row face pose",
                 "Three held shock poses: change only the final pose's left eye to a middle-dot in-between guide.",
                 "Each complete pose is six rows; the final eye row is row 15."),
        _variant(FACE_NEUTRAL * 3,
                 FACE_NEUTRAL * 2 + [FACE_NEUTRAL[0], FACE_NEUTRAL[1], "  <·) (o>"] + FACE_NEUTRAL[3:],
                 "15G0for<C-k>.M",
                 [["15G0fo", "go to the final neutral pose's left pupil"],
                  ["r<C-k>.M", "replace only that pupil with the middle-dot guide"]],
                 "official-UI/FaceHUD res02 neutral pose x3",
                 "accent only the final complete neutral face pose",
                 "Three held neutral faces: change only the final left pupil to the middle-dot guide.",
                 "The final complete face starts on row 13; its eye row is row 15."),
    ]},
    "M7.VIS": {"review_variants": [
        _variant(TANK_IDLE[1:4],
                 [TANK_IDLE[1], "'  |===------|~~.", TANK_IDLE[3]],
                 "2G0f-v2lr=",
                 [["2G0f-", "find the first hull-band cell"],
                  ["v2l", "select exactly three material cells"],
                  ["r=", "replace that band in place"]],
                 "official-Cosmetics/Drill res04 tank body (ASCII-safe crop)",
                 "replace a bounded hull band without shifting the tank",
                 "Drill tank: brighten only the first three cells of the long upper hull band; every rail stays registered.",
                 "Characterwise Visual mode should cover three dashes, no more."),
        _variant([FACE_NEUTRAL[2], FACE_NEUTRAL[4], FACE_NEUTRAL[5]],
                 [FACE_NEUTRAL[2], "\\   ===   /", FACE_NEUTRAL[5]],
                 "2G0f-v2lr=",
                 [["2G0f-", "find the start of the neutral mouth band"],
                  ["v2lr=", "select its three cells and replace them together"]],
                 "official-UI/FaceHUD res02 neutral face (ASCII-safe crop)",
                 "replace the complete FaceHUD mouth band characterwise",
                 "FaceHUD: change only the three-cell mouth band from --- to ===; cheeks and eyes do not move.",
                 "Select the exact three-cell band before replacing it."),
    ]},
    "M6.04": {"review_variants": [
        _variant(FLOWER_HEAD + FLOWER_HEAD,
                 FLOWER_HEAD + ["", FLOWER_HEAD[1], FLOWER_HEAD[2], FLOWER_HEAD[3], FLOWER_HEAD[4]],
                 "6G0D",
                 [["6G0D", "clear the copied flower-head row without deleting the row"]],
                 "official-Games/GrowPlants res03 flower frame 5 crop (copied)",
                 "clear only the copied flower apex while preserving frame height",
                 "GrowPlants flower: remove the copied ( ) head for the subtractive in-between; keep its blank row above the stem.",
                 "D clears from column 1 through the row but leaves the row itself in the frame."),
        _variant(FIREWORK_CANOPY + FIREWORK_CANOPY,
                 FIREWORK_CANOPY + ["", FIREWORK_CANOPY[1], FIREWORK_CANOPY[2], FIREWORK_CANOPY[3], FIREWORK_CANOPY[4]],
                 "6G0D",
                 [["6G0D", "clear the copied shell's top row without deleting it"]],
                 "official-Cosmetics/Fireworks res03 willow frame 5 (copied)",
                 "clear the copied firework apex for a subtractive fade",
                 "Willow firework: blank only the copied frame's top shell row; the star row and five-row registration remain.",
                 "Clear the row's contents with D; dd would collapse the frame."),
    ]},
    # Expression replacement remains validation metadata; it never generates
    # or mirrors the adjacent source art.
    "M18.EXPR": {"review_variants": [
        _variant(["CHECK 1"] + PAD_1[:4] + ["CHECK 0"],
                 ["CHECK 1"] + PAD_1[:4] + ["CHECK 1"],
                 ":6s/0/\\=getline(1)[-1:]/<CR>",
                 [[":6s/0/", "replace the stale digit on CHECK row 6"],
                  ["\\=getline(1)[-1:]", "evaluate the digit from CHECK row 1"],
                  ["<CR>", "update metadata without touching the pad art"]],
                 "official-Games/FrogBog res05 lily-pad frame + validation rows",
                 "derive a check digit beside a real pose without generating art",
                 "FrogBog pad: copy CHECK 1's digit into the stale final CHECK row; the five art rows stay untouched.",
                 "The expression reads metadata from line 1; it must not calculate any art cell."),
        _variant(["CHECK 2"] + FIREWORK_CANOPY[:4] + ["CHECK 0"],
                 ["CHECK 2"] + FIREWORK_CANOPY[:4] + ["CHECK 2"],
                 ":6s/0/\\=getline(1)[-1:]/<CR>",
                 [[":6s/0/", "replace the stale final check digit"],
                  ["\\=getline(1)[-1:]", "copy the leading metadata digit by expression"],
                  ["<CR>", "leave all five firework rows literal"]],
                 "official-Cosmetics/Fireworks res03 willow frame 5 + validation rows",
                 "derive validation metadata beside a firework frame",
                 "Willow firework: update CHECK 0 to CHECK 2 from line 1; do not generate or mirror any shell glyph.",
                 "Use the expression only on the final metadata row."),
    ]},
    # The last generic-border reviews: paragraph objects, block append,
    # blockwise pivots, and macros now operate on actual source animation.
    "M14.PARA": {"review_variants": [
        _variant(SKULLY_IDLE + [""] + SKULLY_BLINK + [""],
                 SKULLY_IDLE + [""] + SKULLY_IDLE + [""] + SKULLY_BLINK + [""],
                 "ggyapgg}jP",
                 [["ggyap", "yank the complete open-eyed Skully paragraph"],
                  ["gg}", "cross its blank-line frame boundary"],
                  ["jP", "put the saved frame above the blink frame"]],
                 "official-Pets/Skully res01 + res04 blink overlay",
                 "copy one complete Skully paragraph frame with yap and P",
                 "Skully strip: copy the complete open-eyed frame and place it before the blink frame as an anticipation hold.",
                 "The blank line is part of the paragraph boundary; yank the object, not three counted rows."),
        _variant(SNOWBUNNY_IDLE + [""] + SNOWBUNNY_BLINK + [""],
                 SNOWBUNNY_IDLE + [""] + SNOWBUNNY_IDLE + [""] + SNOWBUNNY_BLINK + [""],
                 "ggyapgg}jP",
                 [["ggyap", "yank the complete open-eyed bunny paragraph"],
                  ["gg}jP", "cross the boundary and put it above the blink"]],
                 "official-Pets/SnowBunny res01 + res03 blink overlay",
                 "copy one complete SnowBunny paragraph frame with yap and P",
                 "Snow bunny strip: insert one complete open-eyed hold before the blink without reconstructing the pose.",
                 "Use the paragraph object so ears, face, body, and separator travel together."),
    ]},
    "M15.BA": {"review_variants": [
        _variant(MISSILE_F1 + MISSILE_F2,
                 MISSILE_F1 + [row + "|" for row in MISSILE_F2],
                 "4G0<C-v>2j$A|<Esc>",
                 [["4G0<C-v>2j", "select the complete second missile as a three-row block"],
                  ["$A|<Esc>", "append a registration edge at each selected row end"]],
                 "official-Games/TowerDefense res18 missile frames 1 -> 2",
                 "append an edge to every row of one complete missile frame",
                 "TowerDefense missile: add the right registration edge only to frame 2; its three uneven rows keep their contents.",
                 "Blockwise $A appends at each selected row's true end, not one shared column."),
        _variant(SKULLY_IDLE + SKULLY_BLINK,
                 SKULLY_IDLE + [row + "|" for row in SKULLY_BLINK],
                 "4G0<C-v>2j$A|<Esc>",
                 [["4G0<C-v>2j", "select all three rows of the blink frame"],
                  ["$A|<Esc>", "append its comparison edge at each row end"]],
                 "official-Pets/Skully res01 -> res04 blink overlay",
                 "append an edge to every row of the Skully blink frame",
                 "Skully comparison: append one right edge to all three rows of the blink frame; leave the open frame unchanged.",
                 "Use blockwise append so short and long rows each receive exactly one edge."),
    ]},
    "M4.VB": {"review_variants": [
        _variant(FIREWORK_SHELL[:3], _replace_column(FIREWORK_SHELL[:3], 5, "|"),
                 "gg04l<C-v>2jr|",
                 [["gg04l", "land on column 5 of the shell's top row"],
                  ["<C-v>2j", "select the same pivot column through all three rows"],
                  ["r|", "replace the column in place"]],
                 "official-Cosmetics/Fireworks res03 willow frame 2 crop",
                 "replace one aligned firework pivot column blockwise",
                 "Willow firework: turn column 5 into a vertical tween guide across the three-row shell; neighbouring sparks stay fixed.",
                 "The pivot is a column, so select vertically before replacing."),
        _variant(MISSILE_F1, _replace_column(MISSILE_F1, 3, "|"),
                 "gg02l<C-v>2jr|",
                 [["gg02l", "land on column 3 of the missile"],
                  ["<C-v>2jr|", "replace that registered column through all rows"]],
                 "official-Games/TowerDefense res18 missile frame 1",
                 "replace one aligned missile registration column blockwise",
                 "TowerDefense missile: mark column 3 through hull, exhaust, and lower contour as the tween registration guide.",
                 "A vertical block preserves every cell to the left and right of the guide."),
    ]},
    "M7.MAC": {"review_variants": [
        _variant([MISSILE_F1[1], MISSILE_F2[1], MISSILE_F3[1], MISSILE_F4[1]],
                 [row.replace(":", ".", 1)
                  for row in (MISSILE_F1[1], MISSILE_F2[1], MISSILE_F3[1], MISSILE_F4[1])],
                 "ggqaf:r.qj0@aj0@aj0@a",
                 [["ggqa", "start macro a on the first exhaust row"],
                  ["f:r.", "find and soften one exhaust landmark"],
                  ["qj0@aj0@aj0@a", "replay on the other three frame rows"]],
                 "official-Games/TowerDefense res18 missile frames 1-4 exhaust rows",
                 "record one exhaust edit and replay it across four frames",
                 "Missile exhaust strip: change the first : to . in every frame row with one recorded edit plus three replays.",
                 "Reset to column 1 before each replay so f: finds the homologous exhaust landmark."),
        _variant([MISSILE_F4[1], MISSILE_F3[1], MISSILE_F2[1], MISSILE_F1[1]],
                 [row.replace(":", ".", 1)
                  for row in (MISSILE_F4[1], MISSILE_F3[1], MISSILE_F2[1], MISSILE_F1[1])],
                 "ggqaf:r.qj0@aj0@aj0@a",
                 [["ggqa", "record from the first row of the reversed exhaust strip"],
                  ["f:r.", "soften its first exhaust landmark"],
                  ["qj0@aj0@aj0@a", "replay on each following frame row"]],
                 "official-Games/TowerDefense res18 missile frames 4-1 exhaust rows",
                 "replay the same macro over the reversed exhaust timing",
                 "Missile return strip: apply the same first-puff edit to all four reversed frame rows.",
                 "The art order changed; the row-local macro remains valid because it starts from column 1."),
    ]},
}


def cell_difference(a, b):
    """Fraction of non-space cells that differ between two row lists."""
    width = max([len(row) for row in a + b] or [0])
    rows = max(len(a), len(b))
    pad = lambda rows_, n: [r.ljust(width) for r in rows_] + [" " * width] * (n - len(rows_))
    a, b = pad(a, rows), pad(b, rows)
    cells = [(x, y) for ra, rb in zip(a, b) for x, y in zip(ra, rb) if x != " " or y != " "]
    if not cells:
        return 0.0
    return sum(1 for x, y in cells if x != y) / len(cells)


def apply(cards):
    """Replace listed cards' review/transfer variants in place."""
    by_id = {card["id"]: card for card in cards}
    for card_id, fields in REPLACEMENTS.items():
        card = by_id.get(card_id)
        if card is None:
            continue
        for field, rows in fields.items():
            if field not in ("review_variants", "variants"):
                raise ValueError("%s: unsupported replacement field %s" % (card_id, field))
            for row in rows:
                if cell_difference(row["start"], card["start"]) < 0.5:
                    raise ValueError(
                        "%s: replacement art is not different art from the card" % card_id)
            card[field] = [dict(row) for row in rows]
    return cards
