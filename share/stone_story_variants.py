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


def _rail(rows, column):
    """Rows padded with spaces and a `|` drawn at 1-based `column`."""
    return [row.ljust(column - 1) + "|" + row[column:] if len(row) < column
            else row[:column - 1] + "|" + row[column:] for row in rows]


def _rail_rows(rows, column, indices):
    return [_rail([row], column)[0] if i in indices else row for i, row in enumerate(rows)]


SNAKE_BARE = ["         .-.", "        ((`-'", "         \\\\"]       # official-Pets/Snake res01 rows 1-3
SNAKE_TONGUE = ["         .-.", "        ((`-'-", "         \\\\"]    # res01 + res04/res06 tongue layer
SNAKE_FORK = ["         .-.", "        ((`-'-<", "         \\\\"]     # res01 + res05 forked tongue


# card id -> {"review_variants": [...]}
# Transfer `variants` are NOT replaced yet: run_edit asks the card's paired
# question after each transfer attempt, and that question shows the card's own
# art.  A Stone Story variant there would contradict its question (VD-29).
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
