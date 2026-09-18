#!/usr/bin/env python3
"""Generate curriculum.json.

Kept as a generator rather than hand-written JSON because the art is full of
backslashes, quotes and non-ASCII glyphs, and hand-escaping that into JSON is
the bug class that broke a drill on 2026-09-14.

SOURCING RULE (added 2026-09-18 after an audit)
-----------------------------------------------
Every drill's material must come from a named source: either a plate from the
Stone Story RPG ASCII tutorial page, or a numbered rule in the ascii-art-authoring
skill. Inventing a shape "that looks arty" is what the first version did, and it
produced sixteen drills of fragments -- `x_x_x_`, `+---+`, `.:*:.`, `[###]` --
none of which came from anywhere, two of which used glyphs outside the alphabet
(`*`), and one of which used `#`, the transparency character, as ink.

Excerpts are short (<= 6 rows) and are practice material, attributed in README.

Plate excerpts below were extracted byte-exact from:
  articles/2026-09-07-stone-story-video-transcripts-media/o5v-NS9o4yc/
    ascii-tutorial-page/{02-poison-adept-walk-cycle,06-animation-subtractive,
                         03-styles-fonts-alphabet,04-lines-materials-antialiasing}.txt
"""
import json, os

# --- byte-exact plate excerpts -------------------------------------------

WALK_F1 = ["      ,", "   \u221e_/(_", "   |{\\\\", "   |-\u00b4 )", "   |/__\\", "    `  \u00b4"]
WALK_F2 = ["      ,", "   \u221e_/(_", "   |{\\\\", "   |-,/",   "   |/__\\", "    `  \u00b4"]
PYR_APEX = ["          ./\\", "         ____", "       .\u2500\u2500\u2500\u2500\u2500.", "      ________"]
PYR_BASE = ["  \\\u00b4\\/_|__|__|__|_\\", "   \\/|__|__|__|__|_\\"]
EXT_ALPHABET = "\u00b4 \u203e \u00a1 \u00b7"

PLATE = "Stone Story RPG ASCII tutorial page (stonestoryrpg.com/ascii_tutorial.html)"

CONCEPTS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       "concepts.json"), encoding="utf-8"))

D = []
def drill(**kw):
    kw.setdefault("cursor", "^")
    kw.setdefault("kind", "block")
    D.append(kw)

# ===== TIER 1 : line runs, ASCII only, typed by hand =====================

drill(id="change-word", title="stair-step run", skill="change a word in place",
  concept="modes", tier=1, seconds=40,
  start=["TODO"], target=["_.--._"],
  source="skill \u00a74.7 drills 1-2: type the stair-step run, then type it mirrored. "
         "Plated as `_.-\u00b4` in " + PLATE + " \u00a76.",
  recipe=[("cw", "change the word under the cursor"),
          ("_.--._", "type the run, then the same run mirrored"),
          ("<Esc>", "leave insert mode"),
          (":wq", "save and quit")],
  expected="cw_.--._<Esc>:wq<CR>",
  keys=["cw    change to end of word        ciw   change the word, cursor anywhere in it",
        "caw   change word AND its space    C     change to end of line",
        "The plate writes the rise as _ . - \u00b4 . The last glyph is an acute accent,",
        "not an apostrophe. The `symbol table` drill teaches how to get it."],
  buys="The verb+noun sentence, on the one run you will type more than any other.")

drill(id="end-of-line", title="shallowest gradient", skill="operate to end of line",
  concept="grammar", tier=1, seconds=40,
  start=["TODO"], target=[",.,.,.,."],
  source="skill \u00a74.4: `,` and `.` runs are the shallowest gradient available.",
  recipe=[("C", "change from the cursor to the end of the line"),
          (",.,.,.,.", "alternate comma and period"),
          ("<Esc>", "leave insert mode"),
          ("ZZ", "save and quit, no colon needed")],
  expected="C,.,.,.,.<Esc>ZZ",
  keys=["C   = c$  change to end of line      D   = d$  delete to end of line",
        "A     append at end of line          I     insert before first non-blank",
        "0     start of line   ^  first non-blank   $  end of line",
        "ZZ    save and quit                  ZQ    quit without saving"],
  buys="The shorthand verbs. C, D, A and I are each a contraction of a sentence.")

drill(id="counted-insert", title="fence pattern", skill="counted insert",
  concept="repeat", tier=1, seconds=55,
  start=["TODO"], target=["xxxxxx"],
  source="skill \u00a74.3 rule 8: use `x` for patterns such as a fence or a grater, "
         "never for lines. It is one of the twelve whitelisted alphanumerics.",
  recipe=[("cwx<Esc>", "change the word to a single x"),
          ("5ax<Esc>", "append x five more times. The 5 repeats the whole insert."),
          (":wq", "save and quit")],
  expected="cwx<Esc>5ax<Esc>:wq<CR>",
  keys=["3a-<Esc>   appends ---           5i*<Esc>   inserts *****",
        ".          repeat last change    u   undo       <C-r>  redo",
        "Counts work on nearly everything: 3dd, 2yy, 4j, d3w",
        "Alphanumerics are gaze anchors. Use them for texture, or for an eye."],
  buys="A count turns one insert into a run. This is how texture gets typed.")

drill(id="counts", title="trough", skill="counts instead of key-mashing",
  concept="grammar", tier=1, seconds=50,
  start=["TODO"], target=["\\______/"],
  source="skill \u00a74.4: `/` and `\\` runs are the natural 60\u00b0 diagonal, and a `_` run "
         "is the floor between them.",
  recipe=[("cw\\<Esc>", "change the word to a single backslash"),
          ("6a_<Esc>", "append the floor six times. Do NOT press _ six times."),
          ("a/<Esc>", "append the closing diagonal"),
          (":wq", "save and quit")],
  expected="cw\\<Esc>6a_<Esc>a/<Esc>:wq<CR>",
  keys=["3a-<Esc>   append --- after cursor     3i-<Esc>   insert --- before cursor",
        "r<char>    replace exactly one char    R          overwrite mode",
        "One angle has several material renderings. Choose by material, not angle."],
  buys="Saying how many, once, instead of saying it again and again.")

drill(id="find-char", title="dither band", skill="find-character motions",
  concept="motion-precision", tier=1, seconds=60,
  start=["TODO"], target=[".:.:.:.:"],
  source="skill \u00a78: build a shading band by alternating two glyphs.",
  recipe=[("cw", "change the word under the cursor"),
          (".:.:.:.:", "alternate the two glyphs of the band"),
          ("<Esc>", "leave insert mode"),
          ("0", "jump to the start of the line"),
          ("f:", "jump to the first colon, then press ; ; to hop the rest"),
          (":wq", "save and quit")],
  expected="cw.:.:.:.:<Esc>0f:;;:wq<CR>",
  keys=["f:    find next : on this line     F:    find previous :",
        "t:    stop just BEFORE the next :  ;     repeat the find forward",
        ",     repeat the find backward     df:   delete up to and including next :"],
  buys="Travelling by landmark instead of by counting cells.")

drill(id="dot", title="lighten the band", skill="the dot command",
  concept="repeat", tier=1, seconds=60,
  start=["::::::::"], target=[".:.:.:.:"],
  source="skill \u00a78 rule 2: lighten a band by ERASING members of it, not by swapping "
         "to a lighter glyph.",
  recipe=[("r.", "replace this colon with a period"),
          ("2l", "skip one cell"),
          (".", "the dot key repeats r. at the new cursor"),
          ("2l .", "and again"),
          ("2l .", "and once more, then :wq")],
  expected="r.2l.2l.2l.:wq<CR>",
  keys=[".     repeat the last change        3.    repeat it three times",
        "u     undo                          <C-r>  redo",
        "The dot repeats the last INSERT or OPERATOR, not motions and not : commands.",
        "Habit: keep edits small and repeatable, and let dot do the volume."],
  buys="The single highest-leverage key on the board.")

drill(id="pairs", title="line-style lamp", skill="matching pairs and text objects",
  concept="text-objects", tier=1, seconds=55,
  start=["(TODO)"], target=["(   '   )"],
  source=PLATE + " \u00a73, the Line style plate. This is the lamp's body row, "
         "under `(   '   )`.",
  recipe=[("ci(", "change INSIDE the parentheses. The brackets survive."),
          ("   '   ", "three spaces, an apostrophe, three spaces"),
          ("<Esc>", "leave insert mode"),
          ("%", "bounce between the matching brackets to check the pair"),
          (":wq", "save and quit")],
  expected="ci(   '   <Esc>%:wq<CR>",
  keys=["ci(    change inside ( )          ca(    change ( ) as well",
        "di\"    delete inside quotes       yi[    yank inside brackets",
        "%      jump between matching ( ) [ ] { }",
        "The cursor may sit anywhere inside the object. No navigation needed."],
  buys="i = inner, a = around. One mnemonic, one hundred commands.")

# ===== TIER 2 : rectangles, macros, the symbol table =====================

drill(id="block-append", title="rotation in-between", skill="blockwise append",
  concept="lines-and-blocks", tier=2, seconds=70,
  start=["\\", "\\", "\\"], target=["\\|", "\\|", "\\|"],
  source="skill \u00a74.4: the rotation triple is `\\` then `\\|` then `/`. The vertical "
         "bar is the in-between frame.",
  recipe=[("<C-v>", "enter blockwise visual mode (Ctrl and v together)"),
          ("jj", "extend the block down two lines"),
          ("$", "extend it to the end of every line"),
          ("A|", "capital A: append after the block. Type one bar."),
          ("<Esc>", "leave insert mode. It lands on all three lines.")],
  expected="<C-v>jj$A|<Esc>:wq<CR>",
  keys=["<C-v>jj$A text <Esc>  append to the end of several lines",
        "<C-v>jjI  text <Esc>  insert down a column instead",
        "<C-v>jjd             delete a column",
        "The edit looks like it only happened on one line until you press <Esc>."],
  buys="Editing a rectangle. A rotation in-between is a rectangle edit.")

drill(id="block-erase", title="narrow the base", skill="blockwise delete",
  concept="lines-and-blocks", tier=2, seconds=85,
  start=["\\/|__|__|__|_\\"] * 3, target=["\\/|__|__|_\\"] * 3,
  source=PLATE + " \u00a713, the subtractive-animation pyramid. skill \u00a710: copy the "
         "frame, delete one unit, repeat.",
  recipe=[("2l", "move onto the first bar of the base"),
          ("<C-v>", "enter blockwise visual mode"),
          ("jjll", "extend down two lines and right two columns"),
          ("d", "delete the rectangle. The base loses one unit."),
          (":wq", "save and quit")],
  expected="2l<C-v>jjlld:wq<CR>",
  keys=["<C-v>jjd      delete a rectangle       <C-v>jjr.   fill it with one glyph",
        "<C-v>jj~      toggle case in a column",
        "Subtractive animation: draw the finished object, then erase one unit per",
        "frame, then re-sort the frames into playback order."],
  buys="Erasing a unit per frame is how accretive animations are actually authored.")

drill(id="macro", title="frame caps", skill="record and replay a macro",
  concept="repeat", tier=2, seconds=100,
  start=["/__\\"] * 4, target=["'/__\\'"] * 4,
  source="skill \u00a74.6 rule 5: `'` sits high in the cell, `.` sits too low, `:` sits in "
         "the middle. Here `'` caps each frame cell.",
  recipe=[("qq", "start recording into register q"),
          ("I'<Esc>", "insert a cap at the start of the line"),
          ("A'<Esc>", "append a cap at the end of the line"),
          ("j", "step down. Recording the move is what makes it replayable."),
          ("q", "stop recording"),
          ("3@q", "replay the macro three times"),
          (":wq", "save and quit")],
  expected="qqI'<Esc>A'<Esc>jq3@q:wq<CR>",
  keys=["qa ... q   record into register a       @a    replay it",
        "@@         replay the last macro again   10@a  replay it ten times",
        "Always record the cursor move to the next item as part of the macro.",
        "\"ap pastes the macro out as plain text, so you can edit it and yank it back."],
  buys="Teaching the editor a new verb, on the spot, in about four seconds.")

drill(id="symbol-table", title="the symbol table", skill="yank a glyph, put it over another",
  concept="registers-and-ranges", tier=2, seconds=90, labels=True,
  start=["alphabet:  " + EXT_ALPHABET, "slope:     _.-'"],
  target=["alphabet:  " + EXT_ALPHABET, "slope:     _.-\u00b4"],
  source="skill \u00a71.7: keep the glyph alphabet and a personal symbol-table file open "
         "beside the drawing. skill \u00a74.2: \u00b4 is the mirror of the backtick. It is NOT "
         "the apostrophe, and it is not on your keyboard.",
  recipe=[("W", "jump to the first extended glyph on the alphabet line"),
          ("yl", "yank exactly one character into the unnamed register"),
          ("j$", "drop to the slope line, last character: the wrong glyph"),
          ("vp", "select that one character and put the yanked glyph over it"),
          (":wq", "save and quit")],
  expected="Wylj$vp:wq<CR>",
  keys=["yl    yank one character        3yl   yank three",
        "vp    select, then put OVER the selection",
        "\"ayl  yank into register a      \"ap   put register a back",
        "This is how an artist types a glyph that is not on the keyboard: keep a",
        "strip of them in the file and copy from it. Never retype by hand."],
  buys="The four extended glyphs, without fighting your keyboard layout.")

# ===== TIER 3 : real multi-frame plates ==================================

drill(id="hold-frames", title="hold a walk frame", skill="counted line yank and put",
  concept="lines-and-blocks", tier=3, seconds=70,
  start=list(WALK_F1), target=WALK_F1 * 3,
  source=PLATE + " plate 02, Poison Adept walk cycle, frame 1. skill \u00a710: add holds "
         "by repeating frames.",
  recipe=[("6yy", "yank six lines: the whole frame"),
          ("G", "jump to the last line. p puts AFTER the cursor, so this matters."),
          ("2p", "put the frame back twice. A three-frame hold."),
          (":wq", "save and quit")],
  expected="6yyG2p:wq<CR>",
  keys=["6yy 2p    copy a 6-line frame and stamp it down twice",
        "yap p     yank a blank-line-separated frame and put it",
        "P         put ABOVE the cursor instead of below",
        "A hold in animation is a repeated frame. Here it is two keystrokes."],
  buys="A real frame, copied the way a real frame file gets built.")

drill(id="tween-frame", title="tween by copy and edit", skill="copy a frame, change one row",
  concept="lines-and-blocks", tier=3, seconds=150,
  start=list(WALK_F1), target=WALK_F1 + WALK_F2,
  source=PLATE + " plate 02, frames 1 and 2 of the Poison Adept walk. They differ in "
         "exactly one row. skill \u00a710: preserve the glyph pattern between frames "
         "wherever the part has not changed.",
  recipe=[("6yy", "yank the frame"),
          ("G", "jump to the last line"),
          ("p", "put an identical copy below. That copy is now frame 2."),
          ("3j0", "drop to the fourth row of the copy, column zero"),
          ("5l r,", "move to the accent and replace it with a comma"),
          ("l r/", "next cell: replace the space with a diagonal"),
          ("l x", "delete the trailing paren, then :wq")],
  expected="6yyGp3j05lr,lr/lx:wq<CR>",
  keys=["This is the whole craft in one exercise: copy the previous frame, then",
        "change ONLY the cells that move. Everything you do not touch stays",
        "registered, which is what stops an animation from boiling.",
        "",
        "yyp then edit    the cheapest tween there is",
        "<C-v> then r     change a rectangle between frames",
        "qq ... q then @q when the same change repeats across many frames"],
  buys="Temporal coherence: the frames that follow are edits of the frame before.")

drill(id="playback-order", title="playback order", skill="swap adjacent lines",
  concept="lines-and-blocks", tier=3, seconds=55,
  start=[PYR_APEX[0], PYR_APEX[2], PYR_APEX[1], PYR_APEX[3]],
  target=list(PYR_APEX),
  source=PLATE + " \u00a713, the subtractive pyramid: apex rows of frames 1 to 4. "
         "skill \u00a710: authoring order and playback order are independent; re-sort "
         "the frames afterwards.",
  cursor="j^",
  recipe=[("ddp", "delete this line and put it back after the next one. They swap."),
          (":wq", "save and quit")],
  expected="ddp:wq<CR>",
  keys=["ddp    swap this line with the one below     ddkP   swap with the one above",
        ":m+1   move this line down one              :m-2   move it up one",
        ":5,9m0 move a range of lines to the top of the file"],
  buys="Re-sorting frames is one idiom, not a rewrite.")

drill(id="ex-copy", title="duplicate a base row", skill="ex ranges",
  concept="registers-and-ranges", tier=3, seconds=60,
  start=list(PYR_BASE), target=PYR_BASE + [PYR_BASE[1]],
  source=PLATE + " \u00a713, the subtractive pyramid base rows.",
  cursor="j^",
  recipe=[(":t.", "copy THIS line (.) to just after THIS line. Colon, t, dot."),
          ("<CR>", "run it"),
          (":wq", "save and quit")],
  expected=":t.<CR>:wq<CR>",
  keys=[":t.     copy this line below itself      :t0    copy it to the top",
        ":m0     move this line to the top        :m$    move it to the bottom",
        ":%s/o/0/g   substitute on every line",
        "yyp does the same as :t. Ranges scale to a hundred lines; yyp does not."],
  buys="The colon line takes a range, and the range is the half that scales.")

drill(id="mirror-run", title="hand-mirrored run", skill="single character replace",
  concept="motion-precision", tier=3, seconds=60,
  start=["_.-", "_.-"], target=["_.-", "-._"],
  source="skill \u00a74.7 drills 6-7: mirror art by retyping the row backwards with each "
         "glyph swapped for its mirror. Never use a software flip.",
  cursor="j^",
  recipe=[("r-", "replace the underscore with a dash"),
          ("l r.", "step right, replace the period with a period"),
          ("l r_", "step right, replace the dash with an underscore"),
          (":wq", "save and quit")],
  expected="r-lr.lr_:wq<CR>",
  keys=["r<char>   replace exactly one character, staying in normal mode",
        "3rx       replace the next three characters with x",
        "The mirror table: _ <-> _   . <-> .   - <-> -   / <-> \\   ( <-> )",
        "                  ` <-> \u00b4   , <-> .   { <-> }   < <-> >"],
  buys="r is the surgical tool: one glyph, one key, no mode change.")

drill(id="dot-column", title="joint glyph", skill="the dot command across lines",
  concept="repeat", tier=3, seconds=70,
  start=["|--.--|"] * 3, target=["|--:--|"] * 3,
  source="skill \u00a74.6 rule 5: test a joint glyph three ways. `.` sits too low, `'` sits "
         "too high, `:` sits in the middle. Rule 6: `:` preserves a corner, `-` turns "
         "it into a curve.",
  recipe=[("3l", "move onto the joint glyph"),
          ("r:", "replace it with the middle-height glyph"),
          ("j.", "step down. The dot repeats r: at the SAME column."),
          ("j.", "and again, then :wq")],
  expected="3lr:j.j.:wq<CR>",
  keys=["j keeps your column, so j. walks one edit down a stack of frames",
        "3.        repeat the change three times in place",
        "For a taller stack, record it instead: qq r: j q then 20@q"],
  buys="Vertical repetition without a macro: the cheapest way to edit a stack.")

# -------------------------------------------------------------------------
for _d in D:
    _d["start"] = [l.rstrip() for l in _d["start"]]
    _d["target"] = [l.rstrip() for l in _d["target"]]

doc = {
  "schema": "vim-daily/curriculum@2",
  "generated": "2026-09-18",
  "provenance": {
    "concepts": "Framing follows the paradigm-first style of blog.codeminer42.com "
                "'A Noob's Neovim Journey Pt.1' (2024-10-23).",
    "drill_shape": "concept -> skill -> source -> recipe -> challenge -> mastery counter, "
                   "the structure used by Vim Hero and vim-adventures lesson trees. The "
                   "fields are deliberately generic so an external curriculum can be "
                   "imported into this shape without touching the runner.",
    "art": "Every drill cites a source in its `source` field: a plate from the Stone "
           "Story RPG ASCII tutorial page by Gabriel Santos (Martian Rex, Inc.), or a "
           "numbered rule in the ascii-art-authoring skill. Plate excerpts are at most "
           "six rows and are used as practice material. Schema v1 invented all sixteen "
           "shapes and is retained in git history as a counter-example.",
  },
  "tiers": {"1": {"unlock_at": 0}, "2": {"unlock_at": 8}, "3": {"unlock_at": 10}},
  "concepts": CONCEPTS,
  "drills": D,
}

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "curriculum.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1, ensure_ascii=False)
    f.write("\n")
print("wrote %s: %d drills, %d concepts" % (out, len(D), len(CONCEPTS)))
