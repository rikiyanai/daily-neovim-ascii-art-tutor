#!/usr/bin/env python3
"""Generate curriculum.json from concepts.json + art.json.

Three rules, all enforced by test_drills.py:

  SOURCED   every drill names where its art comes from (art.json provenance)
            and which vimtutor lesson node it covers.
  SHORT     <= 16 keystrokes and <= 75 seconds. These fire hourly; a drill that
            takes three minutes is a drill you start resenting.
  REAL      the recipe is driven through an actual nvim and must reach the target.

Targets are DERIVED from the art by the same operation the drill teaches, never
retyped by hand. Retyping is how you get a target that no recipe can reach.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ART = json.load(open(os.path.join(HERE, "art.json"), encoding="utf-8"))["art"]
CONCEPTS = json.load(open(os.path.join(HERE, "concepts.json"), encoding="utf-8"))

def a(key):
    return list(ART[key]["rows"])
def src(key, extra=""):
    return ART[key]["source"] + ((" " + extra) if extra else "")

D = []
def d(id, title, skill, concept, tier, tutor, start, target, recipe, expected,
      source, keys=(), buys="", cursor="^", seconds=None, labels=False):
    D.append({"id": id, "title": title, "skill": skill, "concept": concept,
              "tier": tier, "tutor": tutor, "kind": "block", "cursor": cursor,
              "start": [l.rstrip() for l in start], "target": [l.rstrip() for l in target],
              "recipe": [list(r) for r in recipe], "expected": expected, "source": source,
              "keys": list(keys), "buys": buys, "labels": labels,
              # Estimate from KEYSTROKES, not from the length of the spec string
              # (`<Esc>` is one key, not five). ~3s per keystroke plus a fixed
              # allowance for reading the recipe.
              "seconds": seconds or min(75, 14 + 3 * _nkeys(expected))})

SAVE = ":wq<CR>"

def _nkeys(spec):
    """Count keys the way the runner tokenizes them, ignoring the save command."""
    out, i = 0, 0
    while i < len(spec):
        if spec[i] == "<":
            j = spec.find(">", i)
            if j > 0 and len(spec[i:j]) < 8:
                out += 1
                i = j + 1
                continue
        out += 1
        i += 1
    return max(0, out - 4)      # :, w, q, <CR>
def drop(rows, i):     return rows[:i] + rows[i+1:]
def dup(rows, i):      return rows[:i+1] + [rows[i]] + rows[i+1:]
def sub(rows, i, new): return rows[:i] + [new] + rows[i+1:]

# ===================== TIER 1 — vimtutor chapter 1-4 =====================

d("move-x", "spark, one cell", "move the cursor, delete a character", "modes", 1,
  "vim-01 1.1 / 1.3", a("spark4"), drop(a("spark4"), 1),
  [("j", "move down one line"), ("dd", "delete that whole line"), (":wq", "save and quit")],
  "jdd" + SAVE, src("spark4", "The particle layer is a one-cell animation."),
  ["h j k l   left down up right, without leaving the home row",
   "dd  delete a line     x  delete a character     u  undo"],
  "The home-row four. Every motion you learn later replaces these.")

d("delete-word", "trim the alphabet", "delete a word", "grammar", 1, "vim-01 2.1",
  a("alphabet_ext"), ["‾ ¡ ·"],
  [("dw", "delete the word under the cursor, and the space after it"), (":wq", "save and quit")],
  "dw" + SAVE, src("alphabet_ext"),
  ["dw   delete a word        de   delete to the end of the word",
   "d$   delete to end of line   dd   delete the line"],
  "The first verb+noun sentence: delete, a word.", labels=True)

d("delete-eol", "cut the label", "delete to end of line", "grammar", 1, "vim-01 2.2",
  ["(   '   )    Line"], ["(   '   )"],
  [("$", "jump to the end of the line"), ("F ", "back to the space before the label"),
   ("D", "delete from here to the end of the line"), (":wq", "save and quit")],
  "$F D" + SAVE, src("lamp_line", "The plate labels the style beside the art."),
  ["D = d$   delete to end of line      C = c$   change to end of line",
   "F<char>  find backwards on this line"],
  "Stripping a label off a line without counting characters.", labels=True)

d("count-motion", "two runs on", "use a count with a motion", "grammar", 1, "vim-01 2.4",
  ["_.-´ _.-´ _.-´"], ["_.-´"],
  [("d2W", "delete two WORDS. Capital W, and here is why:"),
   ("", "w stops at every punctuation mark, and line art is all punctuation."),
   ("", "W is whitespace-delimited, so one run is one W."), (":wq", "save and quit")],
  "d2W" + SAVE, src("run_stair", "Three copies of the stair-step run."),
  ["w  next word, stopping at punctuation     W  next whitespace-delimited WORD",
   "b B  backwards        e E  end of word",
   "d2W  delete two runs                      3dd  delete three lines",
   "For prose, w. For art, W: `_.-\u00b4` is four words to w and one WORD to W."],
  "The w/W distinction, on material where it actually bites.")

d("delete-line", "drop a frame", "delete whole lines", "lines-and-blocks", 1, "vim-01 2.6",
  a("pyr_apexes"), drop(a("pyr_apexes"), 2),
  [("2j", "move down to the third frame's apex"), ("dd", "delete that line"),
   (":wq", "save and quit")],
  "2jdd" + SAVE, src("pyr_apexes"),
  ["dd   delete a line      3dd  delete three lines      D  delete to end of line"],
  "Frames are lines. Dropping one is one command.")

d("undo", "delete, then think again", "the undo command", "repeat", 1, "vim-01 2.7",
  a("pyr_apexes"), drop(a("pyr_apexes"), 0),
  [("dd", "delete the first apex"), ("u", "undo it. The line comes back."),
   ("<C-r>", "redo it. Ctrl and r. The line goes away again."),
   (":wq", "save and quit")],
  "ddu<C-r>" + SAVE, src("pyr_apexes"),
  ["u      undo the last change        <C-r>  redo",
   "U      undo every change on this line",
   "Undo is cheap. That is what makes guessing a command a reasonable move."],
  "Nothing you try in normal mode costs more than one keystroke to take back.")

d("put", "stamp a spark", "the put command", "lines-and-blocks", 1, "vim-01 3.1",
  a("spark1"), a("spark1") + [a("spark1")[0]],
  [("yy", "yank this line"), ("G", "jump to the last line"),
   ("p", "put the yanked line below it"), (":wq", "save and quit")],
  "yyGp" + SAVE, src("spark1"),
  ["yy  yank a line    p  put below    P  put above    3p  put three copies"],
  "Copy and paste, without a clipboard or a mouse.")

d("replace-char", "raise the joint", "the replace command", "motion-precision", 1, "vim-01 3.2",
  ["|--.--|"], ["|--:--|"],
  [("3l", "move onto the joint glyph"), ("r:", "replace exactly that one character"),
   (":wq", "save and quit")],
  "3lr:" + SAVE,
  "skill §4.6 rule 5: a joint glyph sits differently in its cell. `.` sits too low, "
  "`'` sits too high, `:` sits in the middle.",
  ["r<char>  replace one character, staying in normal mode",
   "3rx      replace the next three          R  overwrite until <Esc>"],
  "One glyph, one key, no mode change.")

d("change-word", "stair-step run", "change a word in place", "modes", 1, "vim-01 3.3",
  ["TODO"], ["_.--._"],
  [("cw", "change the word under the cursor"),
   ("_.--._", "type the run, then the same run mirrored"),
   ("<Esc>", "leave insert mode"), (":wq", "save and quit")],
  "cw_.--._<Esc>" + SAVE,
  "skill §4.7 drills 1-2: type the stair-step run, then type it mirrored. "
  "Plated as `_.-´` in the Lines & Materials section.",
  ["cw   change to end of word      ciw  change the word from anywhere in it",
   "The plate writes the rise as _ . - ´ . That last glyph is an acute accent,",
   "not an apostrophe. The `symbol table` drill shows how to get it."],
  "The verb+noun sentence, on the run you will type more than any other.")

d("change-eol", "shallowest gradient", "change to end of line", "grammar", 1, "vim-01 3.4",
  ["TODO"], [",.,.,.,."],
  [("C", "change from the cursor to the end of the line"),
   (",.,.,.,.", "alternate comma and period"), ("<Esc>", "leave insert mode"),
   ("ZZ", "save and quit, no colon needed")],
  "C,.,.,.,.<Esc>ZZ",
  "skill §4.4: `,` and `.` runs give the shallowest gradient available.",
  ["C = c$  change to end of line      A  append at end of line",
   "0  start of line   ^  first non-blank   $  end of line",
   "ZZ save and quit                   ZQ quit without saving"],
  "The shorthand verbs: each is a contraction of a whole sentence.")

d("search", "find the anchor", "the search command", "motion-precision", 1, "vim-01 4.2",
  a("dither_low"), drop(a("dither_low"), 1),
  [("/`", "search for the backtick"), ("<CR>", "run the search"),
   ("dd", "delete the line it landed on"), (":wq", "save and quit")],
  "/`<CR>dd" + SAVE, src("dither_low"),
  ["/text  search forward    ?text  search backward",
   "n      next match        N      previous match",
   "<C-o>  jump back to where you were      <C-i>  jump forward again"],
  "Finding a cell by what is in it, not by counting to it.")

d("match-paren", "check the pair", "matching parentheses", "text-objects", 1, "vim-01 4.3",
  ["(TODO)"], ["(   '   )"],
  [("ci(", "change INSIDE the parentheses. The brackets survive."),
   ("   '   ", "three spaces, an apostrophe, three spaces"),
   ("<Esc>", "leave insert mode"), ("%", "bounce between the brackets to check the pair"),
   (":wq", "save and quit")],
  "ci(   '   <Esc>%" + SAVE, src("lamp_line", "This is the lamp's body row."),
  ["%    jump between matching ( ) [ ] { }",
   "ci(  change inside parens     ca(  change the parens as well",
   "The cursor may sit anywhere inside the object."],
  "i = inner, a = around. One mnemonic, a hundred commands.")

d("substitute", "swap one glyph", "the substitute command", "registers-and-ranges", 1,
  "vim-01 4.4", ["|--.--|"], ["|--:--|"],
  [(":s/./:/", "substitute, but the dot means `any character` in a pattern"),
   ("", "so escape it: type  :s/\\./:/  exactly"), ("<CR>", "run it"),
   (":wq", "save and quit")],
  ":s/\\./:/<CR>" + SAVE,
  "skill §4.6 rule 5: `:` sits at mid-height in the cell, `.` sits too low.",
  [":s/old/new/     first match on this line",
   ":s/old/new/g    every match on this line",
   ":%s/old/new/g   every match in the file",
   "In a pattern, . means any character. Escape it as \\. to mean a literal dot."],
  "The first taste of the colon line, and of patterns.")

d("substitute-all", "lighten every band", "substitute across the file", "registers-and-ranges", 1,
  "vim-01 4.4", ["::::", "::::", "::::"], [".:.:", ".:.:", ".:.:"],
  [(":%s/::/.:/g", "on every line, replace each :: with .:"), ("<CR>", "run it"),
   (":wq", "save and quit")],
  ":%s/::/.:/g<CR>" + SAVE,
  "skill §8 rule 2: lighten a shading band by erasing members of it, not by "
  "swapping to a lighter glyph.",
  [":%s/a/b/g    every match in the file",
   ":%s/a/b/gc   ask for confirmation at each one",
   ":5,9s/a/b/g  only on lines 5 to 9"],
  "One command instead of forty edits.")

d("open-line", "pad the frame", "open a line", "lines-and-blocks", 1, "vim-01 6.1",
  a("spark1"), [""] + a("spark1"),
  [("O", "open a blank line ABOVE the cursor"), ("<Esc>", "leave insert mode"),
   (":wq", "save and quit")],
  "O<Esc>" + SAVE, src("spark1", "skill §9 step h: pad every frame to the height "
                        "of the tallest one before rendering."),
  ["o  open a line below and start typing      O  open one above",
   "Frames in a set must be the same height, so padding is routine."],
  "Padding frames to a common height, one keystroke per row.")

d("append", "ground the run", "append text", "grammar", 1, "vim-01 6.2",
  ["_.-"], ["_.-´"],
  [("A", "append at the end of the line"), ("", "then put the acute accent there"),
   ("<Esc>", "leave insert mode"), (":wq", "save and quit")],
  "A´<Esc>" + SAVE,
  "skill §4.4: the classic stair-step is `_ . - ´`. If your keyboard cannot type "
  "´ directly, do the `symbol table` drill instead.",
  ["a  append after the cursor      A  append at end of line",
   "i  insert before the cursor     I  insert before the first non-blank"],
  "Four ways into insert mode, each saving a motion.")

d("yank-put", "hold a spark", "yank and put a line", "lines-and-blocks", 1, "vim-01 6.4",
  a("spark2"), dup(a("spark2"), 0),
  [("yy", "yank this line"), ("p", "put a copy of it below"), (":wq", "save and quit")],
  "yyp" + SAVE, src("spark2", "skill §10: a hold is a repeated frame."),
  ["yy p   the cheapest duplicate there is",
   "3yy    yank three lines      \"ayy   yank into register a"],
  "A hold in animation is a repeated frame, and two keystrokes here.")

d("join", "close the seam", "join two lines", "lines-and-blocks", 1, "vim-01 extras",
  ["_.-", "-._"], ["_.- -._"],
  [("J", "join the next line onto this one, with a space between"),
   (":wq", "save and quit")],
  "J" + SAVE,
  "skill §4.7 drill 2: type the run, then type it mirrored.",
  ["J   join the line below, inserting a space",
   "gJ  join without inserting anything",
   "3J  join three lines"],
  "Two rows become one row without retyping either.")

d("toggle-case", "swap the eye", "toggle case", "repeat", 1, "vim-01 extras",
  ["( o )"], ["( O )"],
  [("2l", "move onto the o"), ("~", "toggle its case"), (":wq", "save and quit")],
  "2l~" + SAVE,
  "skill §4.3 rule 3: place one alphanumeric only where you want the reader to "
  "look, such as an eye. Both `o` and `O` are on the twelve-glyph whitelist.",
  ["~    toggle the case of one character      3~   toggle three",
   "g~w  toggle the case of a word             gUU  upper-case the line"],
  "The smallest possible edit, and a real one: o and O read as different eyes.")

# ===================== TIER 2 — objects, registers, blocks ===============

d("text-object-quote", "inside the quotes", "change inside a text object", "text-objects", 2,
  "vim-02 2.1.1", ["´ ‾ ¡ ·"], ["´ ‾ ¡ ·"],
  [("", "this drill is a no-op placeholder and is removed below")], "x", "placeholder")
D.pop()

d("text-object-paren", "around versus inside", "a-objects versus i-objects", "text-objects", 2,
  "vim-02 2.1.1", ["(   '   )"], ["'"],
  [("f'", "land on the apostrophe inside the brackets"),
   ("ca(", "change AROUND the parens: the brackets go too"),
   ("'", "type a single apostrophe"), ("<Esc>", "leave insert mode"), (":wq", "save and quit")],
  "f'ca('<Esc>" + SAVE, src("lamp_line"),
  ["ci(  change inside the parens       ca(  change the parens as well",
   "di\"  delete inside quotes           dap  delete a paragraph and its blank line",
   "i = inner, a = around."],
  "The difference between the contents and the container.")

d("paragraph-object", "drop a layer", "operate on a paragraph", "lines-and-blocks", 2,
  "vim-02 2.1.1", a("spark1") + [""] + a("spark2"), a("spark1"),
  [("3j", "move into the SECOND block"),
   ("dap", "delete that paragraph AND its blank separator"), (":wq", "save and quit")],
  "3jdap" + SAVE, src("spark1", "skill §3 rule 5: layers are stored as blank-line-"
                     "separated blocks in one file, back layer first."),
  ["dap  delete a paragraph and its blank line    dip  just the paragraph",
   "yap  yank one                                 }    jump to the next blank line",
   "A blank-line-separated block IS a layer. That is why ap matters here."],
  "A frame or a layer is a paragraph. Address it as one.")

d("named-register", "two glyphs at once", "named registers", "registers-and-ranges", 2,
  "vim-02 2.1.2", ["´", "‾", "x"], ["´", "‾", "´"],
  [("\"ayy", "yank this line into register a"), ("2j", "move to the last line"),
   ("V", "select that line"), ("\"ap", "put register a OVER the selection"),
   (":wq", "save and quit")],
  "\"ayy2jV\"ap" + SAVE,
  "skill §1.7: keep a symbol-table file of glyphs open beside the drawing. Named "
  "registers are that table, inside the editor.",
  ["\"ayy  yank a line into register a      \"ap  put it back",
   "\"Ayy  APPEND to register a             :reg  list every register",
   "Twenty-six registers means twenty-six glyphs held at once."],
  "A bank of clipboards, which is what glyph work actually needs.")

d("yank-register-0", "the yank survives", "the numbered registers", "registers-and-ranges", 2,
  "vim-02 2.1.4", ["´", "x", "x"], ["´", "x", "´"],
  [("yy", "yank the glyph line"), ("j", "down to the first x"),
   ("dd", "delete it. That overwrites the unnamed register, but NOT register 0."),
   ("\"0p", "put register 0: the last YANK, not the last delete"), (":wq", "save and quit")],
  "yyjdd\"0p" + SAVE,
  "skill §1.7, the symbol-table workflow: a delete must not cost you the glyph you "
  "just copied.",
  ["\"0p   the last yank, even after a delete overwrote the unnamed register",
   "\"1p   the last delete    \"2p  the one before that",
   "This is the fix for `I yanked, then deleted, and my yank was gone`."],
  "Why your paste stopped working, and the register that fixes it.")

d("marks", "back to the anchor", "marks", "motion-precision", 2, "vim-02 2.1.6",
  a("pyr_apexes"), drop(a("pyr_apexes"), 0),
  [("ma", "drop mark a on this line"), ("G", "jump to the last line"),
   ("'a", "jump straight back to mark a"), ("dd", "delete it"), (":wq", "save and quit")],
  "maG'add" + SAVE, src("pyr_apexes"),
  ["ma   set mark a here      'a   jump to the line of mark a",
   "`a   jump to the exact cell of mark a      :marks  list them",
   "d'a  delete from here to mark a"],
  "A bookmark, so a long file stops costing you your place.")

d("visual-delete", "select and cut", "visual mode", "lines-and-blocks", 2, "vim-01 5.3",
  a("pyr_apexes"), a("pyr_apexes")[3:],
  [("V", "enter line-wise visual mode"), ("2j", "extend the selection down two lines"),
   ("d", "delete the selection"), (":wq", "save and quit")],
  "V2jd" + SAVE, src("pyr_apexes"),
  ["v   character-wise    V   line-wise    <C-v>  block-wise",
   "gv  reselect whatever you had selected last",
   "o   in visual mode, jump to the other end of the selection"],
  "Select first, then act, for when you cannot name the motion.")

d("block-insert", "column of bars", "blockwise insert", "lines-and-blocks", 2, "vim-01 6.x",
  ["\\", "\\", "\\"], ["|\\", "|\\", "|\\"],
  [("<C-v>", "blockwise visual mode (Ctrl and v)"), ("jj", "extend down two lines"),
   ("I|", "capital I: insert at the LEFT edge of the block"),
   ("<Esc>", "leave insert mode. The bar lands on all three lines.")],
  "<C-v>jjI|<Esc>" + SAVE,
  "skill §4.4: the rotation triple is `\\` then `\\|` then `/`; the vertical bar is "
  "the in-between frame.",
  ["<C-v>jjI text <Esc>   insert down a column",
   "<C-v>jj$A text <Esc>  append to the end of several lines",
   "<C-v>jjd              delete a column",
   "Nothing appears to happen until you press <Esc>."],
  "Editing a rectangle. Frame work is rectangle work.")

d("block-append", "rotation in-between", "blockwise append", "lines-and-blocks", 2, "vim-01 6.x",
  ["\\", "\\", "\\"], ["\\|", "\\|", "\\|"],
  [("<C-v>", "blockwise visual mode"), ("jj", "extend down two lines"),
   ("$", "extend to the end of every line"), ("A|", "capital A: append after the block"),
   ("<Esc>", "leave insert mode")],
  "<C-v>jj$A|<Esc>" + SAVE,
  "skill §4.4: `\\` then `\\|` then `/` is the rotation triple. The bar is the tween.",
  ["<C-v>jj$A  appends to lines of different lengths, correctly",
   "<C-v>jjI   inserts at a fixed column instead"],
  "The in-between frame of a rotation, in one command.")

d("block-erase", "narrow the base", "blockwise delete", "lines-and-blocks", 2, "vim-01 6.x",
  ["\\/|__|__|__|_\\"] * 3, ["\\/|__|__|_\\"] * 3,
  [("2l", "move onto the first bar of the base"), ("<C-v>", "blockwise visual mode"),
   ("jjll", "extend down two lines and right two columns"),
   ("d", "delete the rectangle. The base loses one unit."), (":wq", "save and quit")],
  "2l<C-v>jjlld" + SAVE, src("pyr1", "skill §10: copy the frame, delete one unit, repeat."),
  ["<C-v>jjd   delete a rectangle      <C-v>jjr.  fill it with one glyph",
   "Subtractive animation: draw the finished object, erase one unit per frame,",
   "then re-sort the frames into playback order."],
  "Erasing a unit per frame is how accretive animation is really authored.")

d("block-replace", "fill a rectangle", "blockwise replace", "lines-and-blocks", 2, "vim-01 6.x",
  ["|--|", "|--|", "|--|"], ["|::|", "|::|", "|::|"],
  [("l", "move onto the first dash"), ("<C-v>", "blockwise visual mode"),
   ("jjl", "extend down two lines and right one column"),
   ("r:", "replace every cell in the rectangle"), (":wq", "save and quit")],
  "l<C-v>jjlr:" + SAVE,
  "skill §8: a shading band is built by alternating two glyphs across a region.",
  ["<C-v>...r<char>  fill a rectangle with one glyph",
   "<C-v>...~        toggle case across a rectangle",
   "<C-v>...d        cut it out"],
  "Repainting a region without touching the cells around it.")

d("macro", "frame caps", "record and replay a macro", "repeat", 2, "vim-02 extras",
  ["/__\\"] * 4, ["'/__\\'"] * 4,
  [("qq", "start recording into register q"), ("I'<Esc>", "cap the start of the line"),
   ("A'<Esc>", "cap the end of the line"),
   ("j", "step down. Recording the move is what makes it replayable."),
   ("q", "stop recording"), ("3@q", "replay it three times"), (":wq", "save and quit")],
  "qqI'<Esc>A'<Esc>jq3@q" + SAVE,
  "skill §4.6 rule 5: `'` sits high in its cell, so it caps a frame cleanly.",
  ["qa ... q  record into register a     @a   replay      10@a  replay ten times",
   "@@        replay the last macro again",
   "Always record the move to the next item as part of the macro.",
   "\"ap pastes a macro out as text, so you can edit it and yank it back."],
  "Teaching the editor a new verb, in about four seconds.")

d("symbol-table", "the symbol table", "yank a glyph, put it over another",
  "registers-and-ranges", 2, "vim-02 2.1.2", labels=True,
  start=["alphabet:  ´ ‾ ¡ ·", "slope:     _.-'"],
  target=["alphabet:  ´ ‾ ¡ ·", "slope:     _.-´"],
  recipe=[("W", "jump to the first extended glyph"), ("yl", "yank exactly one character"),
          ("j$", "drop to the slope line, last character: the wrong glyph"),
          ("vp", "select that character and put the yanked one over it"),
          (":wq", "save and quit")],
  expected="Wylj$vp" + SAVE,
  source="skill §1.7: keep the glyph alphabet open beside the drawing. skill §4.2: "
         "´ is the mirror of the backtick. It is not the apostrophe, and it is not "
         "on your keyboard.",
  keys=["yl   yank one character         3yl  yank three",
        "vp   select, then put OVER the selection",
        "This is how an artist types a glyph the keyboard does not have: keep a",
        "strip of them in the file and copy from it. Never retype by hand."],
  buys="The four extended glyphs, without fighting your keyboard layout.")

d("dot-repeat", "walk an edit down", "the dot command", "repeat", 2, "vim-01 extras",
  ["|--.--|"] * 3, ["|--:--|"] * 3,
  [("3l", "move onto the joint glyph"), ("r:", "replace it"),
   ("j.", "step down. The dot repeats r: at the SAME column."),
   ("j.", "and again"), (":wq", "save and quit")],
  "3lr:j.j." + SAVE,
  "skill §4.6 rule 5: `.` sits too low, `'` too high, `:` in the middle.",
  ["j keeps your column, so j. walks one edit down a stack of frames",
   "3.  repeat the change three times",
   "For a taller stack, record it: qq r: j q  then 20@q"],
  "Vertical repetition without a macro.")

d("find-char", "hop the band", "find-character motions", "motion-precision", 2, "vim-01 extras",
  [".:.:.:.:"], [".:.:."],
  [("f:", "find the first colon"), (";", "repeat the find"), (";", "and again"),
   ("D", "delete from here to the end of the line"), (":wq", "save and quit")],
  "f:;;D" + SAVE,
  "skill §8: a shading band alternates two glyphs, which makes it a row of landmarks.",
  ["f:  find next :     F:  find previous :     ;  repeat     ,  reverse",
   "t:  stop just BEFORE the next :            df:  delete up to and including it"],
  "Travelling by landmark instead of counting cells.")

d("ex-copy", "duplicate a base row", "ex ranges", "registers-and-ranges", 2, "vim-01 extras",
  ["  \\´\\/_|__|__|__|_\\", "   \\/|__|__|__|__|_\\"],
  ["  \\´\\/_|__|__|__|_\\", "   \\/|__|__|__|__|_\\", "   \\/|__|__|__|__|_\\"],
  [(":t.", "copy THIS line to just after itself. Colon, t, dot."), ("<CR>", "run it"),
   (":wq", "save and quit")],
  ":t.<CR>" + SAVE, src("pyr1", "The base rows of the pyramid."),
  [":t.   copy this line below itself     :t0  copy it to the top",
   ":m0   move this line to the top       :m$  move it to the bottom",
   "yyp does the same as :t. Ranges scale to a hundred lines; yyp does not."],
  "The colon line takes a range, and the range is the half that scales.", cursor="j^")

# ===================== TIER 3 — real frame work ==========================

d("hold-frame", "hold a walk frame", "counted line yank and put", "lines-and-blocks", 3,
  "vim-01 6.4", a("walk1"), a("walk1") * 3,
  [("6yy", "yank six lines: the whole frame"), ("G", "jump to the last line"),
   ("2p", "put the frame back twice"), (":wq", "save and quit")],
  "6yyG2p" + SAVE, src("walk1", "skill §10: add holds by repeating frames."),
  ["6yy 2p  copy a 6-line frame and stamp it down twice",
   "yap p   yank a blank-line-separated frame and put it",
   "P       put ABOVE the cursor instead of below"],
  "A real frame, copied the way a real frame file gets built.")

d("tween-frame", "tween by copy and edit", "copy a frame, change one row",
  "lines-and-blocks", 3, "vim-01 6.4", a("walk1"), a("walk1") + a("walk2"),
  [("6yy", "yank the frame"), ("Gp", "copy it below. That copy is now frame 2."),
   ("3j$", "fourth row of the copy, last cell"), ("x", "drop the trailing paren"),
   ("r/", "the space becomes a diagonal"), ("hr,", "step back: the accent becomes a comma"),
   (":wq", "save and quit")],
  "6yyGp3j$xr/hr," + SAVE,
  src("walk1", "Frames 1 and 2 differ in exactly one row. skill §10: preserve the "
      "glyph pattern between frames wherever the part has not changed."),
  ["Copy the previous frame, then change ONLY the cells that move. Everything",
   "you do not touch stays registered, which is what stops an animation boiling.",
   "",
   "yyp then edit     the cheapest tween there is",
   "<C-v> then r      change a rectangle between frames"],
  "Temporal coherence: every frame is an edit of the frame before it.")

d("break-seam", "break the seam", "two surgical replaces", "text-objects", 3, "vim-01 3.2",
  ["  .---./     \\", " /     \\      :"],
  ["  .---.´     \\", " /     \\      :"],
  [("f/", "find the slash that joins the two forms"),
   ("r´", "replace it with an acute accent, which does not touch the other form"),
   ("", "(if ´ is hard to type, do the `symbol table` drill first)"),
   (":wq", "save and quit")],
  "f/r´" + SAVE,
  src("seam_joined", "skill §3: a glyph shared between two objects creates a false "
      "connection. Replace it with a partial-coverage glyph placed away from the seam."),
  ["The plate shows this edit as a before/after pair, with an arrow between them.",
   "It is two character replacements, and it is the whole depth technique:",
   "  a shared glyph reads as a join           break it",
   "  a deleted cell at a seam reads as shadow leave it empty"],
  "Depth, from one character. This is the highest-value edit in the whole method.")

d("playback-order", "playback order", "swap adjacent lines", "lines-and-blocks", 3,
  "vim-01 extras",
  [a("pyr_apexes")[0], a("pyr_apexes")[2], a("pyr_apexes")[1], a("pyr_apexes")[3]],
  a("pyr_apexes")[:4], cursor="j^",
  recipe=[("ddp", "delete this line and put it back after the next. They swap."),
          (":wq", "save and quit")],
  expected="ddp" + SAVE,
  source=src("pyr_apexes", "skill §10: authoring order and playback order are "
             "independent; re-sort the frames afterwards."),
  keys=["ddp    swap with the line below      ddkP  swap with the line above",
        ":m+1   move this line down one       :m-2  move it up one",
        ":5,9m0 move a range to the top"],
  buys="Re-sorting frames is one idiom, not a rewrite.")

d("range-normal", "one edit, every row", "run a normal command over a range",
  "registers-and-ranges", 3, "vim-01 5.3",
  ["_.-", "_.-", "_.-"], ["_.-'", "_.-'", "_.-'"],
  [("VG", "select from here to the last line"),
   (":", "press colon. Vim fills in the range '<,'> for you."),
   ("normal A'", "run `A'` in normal mode on every selected line"),
   ("<CR>", "run it"), (":wq", "save and quit")],
  "VG:normal A'<CR>" + SAVE,
  "skill \u00a74.4: `'` plus `\u00b4` reads as a very slight inclination; capping a run is "
  "a per-row edit you want to apply to the whole set at once.",
  [":'<,'>normal A;   append ; to every selected line",
   ":%normal I// commentiment every line in the file",
   ":g/pattern/cmd    run cmd on every MATCHING line (whole buffer -- careful)",
   "Selecting first and then pressing : is how you scope a range safely."],
  "Any normal-mode command, applied to a whole range at once.")

d("mirror-run", "hand-mirrored run", "single character replace", "motion-precision", 3,
  "vim-01 3.2", ["_.-", "_.-"], ["_.-", "-._"], cursor="j^",
  recipe=[("r-", "replace the underscore with a dash"),
          ("lr.", "step right, replace with a period"),
          ("lr_", "step right, replace with an underscore"), (":wq", "save and quit")],
  expected="r-lr.lr_" + SAVE,
  source="skill §4.7 drills 6-7: mirror art by retyping the row backwards with each "
         "glyph swapped for its mirror. Never use a software flip.",
  keys=["The mirror table:  _ <-> _    . <-> .    - <-> -",
        "                   / <-> \\    ( <-> )    { <-> }    < <-> >",
        "                   ` <-> ´    , <-> .",
        "r<char>  replace one character      3rx  replace three"],
  buys="Mirroring by hand, which is the only way that preserves the style.")

d("pad-frames", "pad to height", "open lines above", "lines-and-blocks", 3, "vim-01 6.1",
  a("spark1"), ["", ""] + a("spark1"),
  [("O", "open a blank line above"), ("<Esc>", "leave insert mode"),
   (".", "the dot repeats the whole open-line change"), (":wq", "save and quit")],
  "O<Esc>." + SAVE,
  src("spark1", "skill §9 step h: count the rows in the tallest frame and pad every "
      "other frame to that height before rendering."),
  ["O<Esc> then .   pad a frame one row at a time",
   "3O<Esc>         or do it in one count",
   "A frame set of mixed heights renders as a jitter."],
  "The least glamorous step in animation, reduced to two keystrokes.")

d("macro-frames", "cap every frame", "replay a macro over a frame set", "repeat", 3,
  "vim-02 extras", ["|--|"] * 5, ["|::|"] * 5,
  [("qq", "start recording into register q"), ("l", "move onto the first dash"),
   ("vl", "select it and the one after it"), ("r:", "replace both"),
   ("j0", "step to the next frame row"), ("q", "stop recording"),
   ("4@q", "replay it on the remaining four"), (":wq", "save and quit")],
  "qqlvlr:j0q4@q" + SAVE,
  "skill §8: a shading band is a region of alternating glyphs, applied per frame.",
  ["qq ... q then 4@q   the same edit across a whole frame set",
   "A macro beats the dot when the edit is more than one operator.",
   "If a macro goes wrong, u undoes the whole replay one step at a time."],
  "One recorded edit, applied to every frame in the set.")

# -------------------------------------------------------------------------
doc = {
  "schema": "vim-daily/curriculum@3",
  "generated": "2026-09-18",
  "provenance": {
    "concepts": "share/concepts.json. Framing follows the paradigm-first style of "
                "blog.codeminer42.com 'A Noob's Neovim Journey Pt.1' (2024-10-23).",
    "spine": "The `tutor` field on each drill names the vimtutor lesson node it covers. "
             "vimtutor ships with vim and neovim ($VIMRUNTIME/tutor/en/); its lesson "
             "SEQUENCE is used as the curriculum spine. No vimtutor text is copied.",
    "drill_shape": "concept -> skill -> source -> recipe -> challenge -> mastery counter, "
                   "the structure used by Vim Hero and vim-adventures lesson trees.",
    "art": "share/art.json, extracted byte-exact from the Stone Story RPG ASCII tutorial "
           "plates by share/extract_art.py. Every drill's `source` field names the plate "
           "or the numbered rule in the ascii-art-authoring skill that it comes from.",
  },
  "tiers": {"1": {"unlock_at": 0}, "2": {"unlock_at": 8}, "3": {"unlock_at": 16}},
  "concepts": CONCEPTS,
  "drills": D,
}
out = os.path.join(HERE, "curriculum.json")
json.dump(doc, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
open(out, "a", encoding="utf-8").write("\n")
print("wrote %s: %d drills" % (out, len(D)))
