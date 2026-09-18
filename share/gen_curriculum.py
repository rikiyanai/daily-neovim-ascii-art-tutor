#!/usr/bin/env python3
"""Generate ~/.local/share/vim-daily/curriculum.json.

Kept as a generator rather than hand-written JSON because the art targets are
full of backslashes and quotes, and hand-escaping them into JSON is exactly the
class of bug that broke drill 2 in the bash version (2026-09-14).
"""
import json, os

CONCEPTS = {
"modes": {
  "title": "Modes: why the editor has more than one rulebook",
  "paradigm": """\
Every other editor you have used runs in one mode. Every key you press inserts
itself, so every COMMAND has to be smuggled in behind a modifier: Ctrl, Cmd,
Alt, or a menu. That single decision is why those editors need a mouse, and why
your hands leave the home row a hundred times an hour.

Vim makes the opposite trade. It splits editing into modes, and each mode is a
small self-contained module with its own rulebook. In Normal mode the entire
alphabet is free, so commands get to be single letters. In Insert mode the
alphabet means letters again. Nothing has to be smuggled.

  Normal   navigate and operate on text          <Esc>
  Insert   type text like a normal editor        i a o I A O
  Visual   select first, then act                v V <C-v>
  Command  talk to the editor in its own line    :

The cost is real: you have to know which mode you are in, and beginners pay for
that in confusion. The payoff is that commands become composable letters instead
of chords, and composable letters can be multiplied together. That multiplication
is the whole reason the rest of these drills exist.

Practical rule: Normal mode is home. You visit Insert mode, you do not live
there. If you find yourself holding a key down, you are in the wrong mode.""",
},

"grammar": {
  "title": "The grammar: vim is a language, not a list of shortcuts",
  "paradigm": """\
The single idea that turns vim from a chore into a tool: commands are sentences.

  [count]  [operator]  [motion or text object]
   adverb     verb          noun

  d        w                 delete one word
  2 d      w                 delete two words
  c        i(                change what is inside the parentheses
  y        ap                yank around this paragraph
  >        }                 indent to the end of the paragraph

You do not memorise commands. You memorise a small vocabulary of verbs and a
small vocabulary of nouns, and the editor multiplies them for you. Ten verbs and
thirty nouns is three hundred edits you were never explicitly taught, and you
can guess every one of them.

This is why nobody has to tell you what `yi(` does once you know `ci(`. It is
also why `d` alone does nothing: a verb with no object is not a sentence. The
editor is waiting for the rest of it.

  verbs   c change   d delete   y yank   > indent   gu lowercase   = format
  nouns   w word   $ end of line   } paragraph   f. up to a dot   i( inside parens

When you catch yourself pressing x fifteen times, stop. That is not a sentence,
that is a stutter. Find the noun that names what you actually want to remove.""",
},

"repeat": {
  "title": "Repetition: fast editing is repeatable editing, not fast typing",
  "paradigm": """\
Watching an expert use vim, the obvious conclusion is that they type quickly.
They do not. What they do is structure each edit so that the editor can perform
it again for them.

Vim gives you three tiers of replay, and they cover almost everything:

  .        repeat the last change, once, wherever the cursor now is
  3a-<Esc> do the insert three times as a single change
  qq ... q record a macro, then @q replays it, 10@q replays it ten times
  :%s///   apply one substitution to every line at once

This has a consequence that is easy to miss: a sloppy edit is a dead end and a
precise edit is an asset. If you fix a line with five improvised keystrokes,
nothing can replay that. If you fix it with `ciw` plus a word, `.` will fix the
next nine occurrences for free. The habit is to make edits small, named, and
repeatable, and then let the editor do the volume.

It is also why `u` (undo) is cheap here. Try a repeatable edit, watch it apply,
undo it if it was wrong. The cost of a wrong guess is one keystroke.""",
},

"motion-precision": {
  "title": "Motions: moving the cursor IS editing",
  "paradigm": """\
In most editors, moving the cursor and changing the text are two different
activities. You arrow over to a spot, then you do a thing. In vim the motion is
an ingredient of the change, so the two collapse into one thought.

  f,     move to the next comma
  df,    delete up to and including the next comma
  ct,    change everything up to but not including the next comma

`df,` is not three keystrokes that happen to be adjacent. It is one intention.
This is why counting keystrokes is the wrong scorecard. The right question is
how many DECISIONS an edit took, and the answer should usually be one.

  f{char}  find the next one on this line      F{char}  find the previous one
  t{char}  stop just before the next one       T{char}  stop just after the previous
  ;        do that find again                  ,        do it backwards
  0 ^ $    start of line, first real char, end of line
  %        bounce between matching brackets    }        next blank line

Precision beats speed. h and l are for adjusting by one cell, not for travelling.
If you are pressing l more than about three times, there was a motion for it.""",
},

"text-objects": {
  "title": "Text objects: address the thing, not the coordinates",
  "paradigm": """\
Motions move from where you are to somewhere else, so they depend on where you
happen to be standing. Text objects do not. They name a STRUCTURE, and they work
from anywhere inside it.

  iw  the word            aw  the word plus its trailing space
  i(  inside the parens   a(  the parens as well
  i"  inside the quotes   a"  the quotes as well
  ip  this paragraph      ap  the paragraph plus its blank line
  it  inside the XML tag  at  the tag as well

`ci(` means "change what is inside these parentheses" and the cursor can be on
the opening bracket, the closing bracket, or anywhere in between. You do not have
to navigate to an edge first. You do not have to count characters.

This is the difference between an edit that is robust and an edit that is a
stunt. Position-based edits break the moment the text shifts by one character.
Structure-based edits do not, which is also why they survive being recorded into
a macro and replayed across forty lines.

i = inner (the contents). a = around (the contents plus the delimiters). That is
the whole mnemonic, and it composes with every verb you already know.""",
},

"lines-and-blocks": {
  "title": "Lines and blocks: the buffer is two-dimensional",
  "paradigm": """\
Most text tooling treats a file as one long string with newlines in it. Vim
treats it as a grid, and gives you operators for both axes.

Along the vertical axis, the line operators:

  dd  delete a line     yy  copy a line      p / P  put it back below / above
  3yy 2p                copy three lines, stamp them down twice
  ddp                   swap this line with the one below it
  :t.  :m0              copy this line to here, move this line to there

Along the horizontal axis, blockwise visual mode:

  <C-v>   select a RECTANGLE, not a run of text
  <C-v>jjI|<Esc>   insert a column down three lines at once
  <C-v>jjd         delete a column
  <C-v>jj$A;<Esc>  append to the end of several lines at once

This is the mode that makes monospaced art tractable. An animation file is a
stack of frames; a frame is a rectangle. Copying a frame, erasing one column
across it, or re-sorting frames into playback order are all one-command
operations here, and they are miserable everywhere else.

Gabriel Santos animates Stone Story RPG in a plain text editor for exactly this
reason: the frames are text, so the text editor is the animation tool.""",
},

"registers-and-ranges": {
  "title": "Ranges and registers: where the editor becomes a small language",
  "paradigm": """\
Press `:` and you are no longer pressing keys at an editor, you are issuing
statements to it. Every statement takes a range, and the range is the powerful
half.

  :t.        copy this line to just after this line
  :5,10m0    move lines 5 to 10 to the top of the file
  :%s/o/0/g  substitute across every line in the buffer
  :'<,'>!sort  pipe the visual selection through an external program
  :g/^$/d    run a command on every line matching a pattern

And the yank you did three edits ago is not gone. Vim has a bank of named
clipboards:

  "ayy   yank this line into register a       "ap   put register a back
  "0p    the last yank, even after a delete overwrote the unnamed register
  qa...q record keystrokes into register a, and @a replays them

The macros and the registers are the same storage. A recorded macro is literally
just text in a register, which means you can paste it out, edit it as text, and
yank it back in. That is the point at which the editor stops being a keyboard
game and starts being programmable.""",
},
}

# ---------------------------------------------------------------------------
# kind: "line"   region is a single line, legacy "ART: " prefix, cursor W
# kind: "block"  region is several raw lines, cursor parks at region start
# cursor: a normal-mode command run after jumping to the first region line.
# expected: the keystrokes the recipe asks for, in the gate's own key encoding.
#           The trailing save command is stripped before comparison.
# ---------------------------------------------------------------------------

D = []

def line_drill(**kw):
    kw["kind"] = "line"
    kw["cursor"] = kw.get("cursor", "W")
    kw["start"] = ["ART: TODO"]
    kw["target"] = ["ART: " + kw.pop("art")]
    D.append(kw)

def block_drill(**kw):
    kw["kind"] = "block"
    kw["cursor"] = kw.get("cursor", "^")
    D.append(kw)

line_drill(
  id="change-word", title="stair-step mirror", skill="change a word in place",
  concept="grammar", tier=1, seconds=40,
  art="_.-''-._",
  recipe=[("cw", "change the word under the cursor"),
          ("_.-''-._", "type this (two single quotes, never one double quote)"),
          ("<Esc>", "leave insert mode"),
          (":wq", "save and quit")],
  expected="cw_.-''-._<Esc>:wq<CR>",
  keys=["cw    change to end of word        ciw   change the word, cursor anywhere in it",
        "caw   change word AND its space    C     change to end of line",
        "dw    delete a word                x     delete one character"],
  buys="The verb+noun sentence. Everything else in vim is this shape.")

line_drill(
  id="end-of-line", title="small arch", skill="operate to end of line",
  concept="grammar", tier=1, seconds=40,
  art=".'-._.-'.",
  recipe=[("C", "change from the cursor to the end of the line"),
          (".'-._.-'.", "type this"),
          ("<Esc>", "leave insert mode"),
          ("ZZ", "save and quit, no colon needed")],
  expected="C.'-._.-'.<Esc>ZZ",
  keys=["C   = c$  change to end of line      D   = d$  delete to end of line",
        "A     append at end of line          I     insert before first non-blank",
        "0     start of line   ^  first non-blank   $  end of line",
        "ZZ    save and quit                  ZQ    quit without saving"],
  buys="The shorthand verbs. C, D, A, I and S are all contractions of a sentence.")

line_drill(
  id="counted-insert", title="slash symmetry", skill="counted insert",
  concept="repeat", tier=1, seconds=60,
  art="/\\__/",
  recipe=[("cw", "change the word under the cursor"),
          ("/\\", "type a slash, then a backslash"),
          ("<Esc>", "leave insert mode"),
          ("2a_<Esc>", "append _ TWICE. The 2 repeats the whole insert, not the key."),
          ("a/<Esc>", "append the closing slash"),
          (":wq", "save and quit")],
  expected="cw/\\<Esc>2a_<Esc>a/<Esc>:wq<CR>",
  keys=["3a-<Esc>   appends ---           5i*<Esc>   inserts *****",
        ".          repeat last change    u   undo       <C-r>  redo",
        "Counts work on nearly everything: 3dd, 2yy, 4j, d3w"],
  buys="A count turns one insert into a run. This is how runs of art get typed.")

line_drill(
  id="counts", title="box fragment", skill="counts instead of key-mashing",
  concept="repeat", tier=1, seconds=45,
  art="+---+",
  recipe=[("cw+<Esc>", "change the word to a single +"),
          ("3a-<Esc>", "append - three times. Do NOT press - three times."),
          ("a+<Esc>", "append the closing +"),
          (":wq", "save and quit")],
  expected="cw+<Esc>3a-<Esc>a+<Esc>:wq<CR>",
  keys=["3a-<Esc>   append --- after cursor     3i-<Esc>   insert --- before cursor",
        "r<char>    replace exactly one char    R          overwrite mode",
        "~          toggle case                 3~         toggle three chars"],
  buys="Saying how many, once, instead of saying it again and again.")

line_drill(
  id="find-char", title="wave", skill="find-character motions",
  concept="motion-precision", tier=1, seconds=60,
  art="~._.~._.",
  recipe=[("cw", "change the word under the cursor"),
          ("~._.~._.", "type this"),
          ("<Esc>", "leave insert mode"),
          ("0", "jump to the start of the line"),
          ("f.", "jump to the first dot, then press ; ; to hop the rest"),
          (":wq", "save and quit")],
  expected="cw~._.~._.<Esc>0f.;;:wq<CR>",
  keys=["f.    find next . on this line      F.    find previous .",
        "t.    stop just BEFORE the next .   ;     repeat the find forward",
        ",     repeat the find backward      df.   delete up to and including next ."],
  buys="Travelling by landmark instead of by counting cells.")

line_drill(
  id="dot", title="shadow pattern", skill="the dot command",
  concept="repeat", tier=1, seconds=50,
  art="x_x_x_",
  recipe=[("cw", "change the word under the cursor"),
          ("x_", "type this"),
          ("<Esc>", "leave insert mode"),
          ("ax_<Esc>", "append x_   <- the dot key will repeat THIS edit"),
          (".", "press the dot key. It repeats that edit."),
          (":wq", "save and quit")],
  expected="cwx_<Esc>ax_<Esc>.:wq<CR>",
  keys=[".     repeat the last change        3.    repeat it three times",
        "u     undo                          <C-r>  redo",
        "The dot repeats the last INSERT or OPERATOR, not motions and not : commands.",
        "Habit: keep edits small and repeatable, and let dot do the volume."],
  buys="The single highest-leverage key on the board.")

line_drill(
  id="pairs", title="nested shape", skill="matching pairs and text objects",
  concept="text-objects", tier=1, seconds=60,
  art="<{[()]}>",
  recipe=[("cw", "change the word under the cursor"),
          ("<{[()]}>", "type this"),
          ("<Esc>", "leave insert mode"),
          ("0 then f{", "jump to the opening brace"),
          ("%", "bounce to its matching closing brace"),
          (":wq", "save and quit")],
  expected="cw<{[()]}><Esc>0f{%:wq<CR>",
  keys=["%      jump between matching ( ) [ ] { }",
        "ci(    change inside parens       ci\"   change inside quotes",
        "di[    delete inside brackets     ya{   yank around braces",
        "vi(    visually select inside parens"],
  buys="Structure-aware movement. % is the cheapest way to check a nesting.")

# ---- tier 2 -------------------------------------------------------------

block_drill(
  id="inner-parens", title="glyph swap", skill="change inside a text object",
  concept="text-objects", tier=2, seconds=45,
  start=["(___)"],
  target=["(~~~)"],
  cursor="^",
  recipe=[("ci(", "change INSIDE the parentheses. The brackets survive."),
          ("~~~", "type three tildes"),
          ("<Esc>", "leave insert mode"),
          (":wq", "save and quit")],
  expected="ci(~~~<Esc>:wq<CR>",
  keys=["ci(    change inside ( )          ca(    change ( ) as well",
        "di\"    delete inside quotes       yi[    yank inside brackets",
        "The cursor may sit anywhere inside the object. No navigation needed."],
  buys="i = inner, a = around. One mnemonic, one hundred commands.")

block_drill(
  id="block-insert", title="rain column", skill="blockwise insert",
  concept="lines-and-blocks", tier=2, seconds=70,
  start=["~", "~", "~"],
  target=["|~", "|~", "|~"],
  cursor="^",
  recipe=[("<C-v>", "enter blockwise visual mode (Ctrl and v together)"),
          ("jj", "extend the block down two lines"),
          ("I", "capital I: insert at the LEFT edge of the block"),
          ("|", "type one pipe"),
          ("<Esc>", "leave insert mode. The pipe now appears on all three lines.")],
  expected="<C-v>jjI|<Esc>:wq<CR>",
  keys=["<C-v>jjI text <Esc>   insert down a column",
        "<C-v>jj$A text <Esc>  append to the end of several lines",
        "<C-v>jjd             delete a column",
        "The edit looks like it only happened on one line until you press <Esc>."],
  buys="Editing a rectangle. This is the operation art files are made of.")

block_drill(
  id="macro", title="ringed frames", skill="record and replay a macro",
  concept="repeat", tier=2, seconds=100,
  start=["o", "o", "o", "o"],
  target=["(o)", "(o)", "(o)", "(o)"],
  cursor="^",
  recipe=[("qq", "start recording into register q"),
          ("I(<Esc>", "insert an opening paren at the start of the line"),
          ("A)<Esc>", "append a closing paren at the end of the line"),
          ("j", "step down one line. Recording the move is what makes it replayable."),
          ("q", "stop recording"),
          ("3@q", "replay the macro three times"),
          (":wq", "save and quit")],
  expected="qqI(<Esc>A)<Esc>jq3@q:wq<CR>",
  keys=["qa ... q   record into register a       @a    replay it",
        "@@         replay the last macro again   10@a  replay it ten times",
        "Always record the cursor move to the next item as part of the macro.",
        "\"ap pastes the macro out as plain text, so you can edit and re-yank it."],
  buys="Teaching the editor a new verb, on the spot, in about four seconds.")

# ---- tier 3: monospaced-art frame work ----------------------------------

block_drill(
  id="hold-frames", title="hold frames", skill="counted line yank and put",
  concept="lines-and-blocks", tier=3, seconds=60,
  start=[" _ ", "( )", " - "],
  target=[" _ ", "( )", " - ", " _ ", "( )", " - ", " _ ", "( )", " - "],
  cursor="^",
  recipe=[("3yy", "yank three lines: the whole frame"),
          ("G", "jump to the last line. p puts AFTER the cursor, so this matters."),
          ("2p", "put the frame back twice. Two more frames, a 3-frame hold."),
          (":wq", "save and quit")],
  expected="3yyG2p:wq<CR>",
  keys=["3yy 2p    copy a 3-line frame and stamp it down twice",
        "yap p     yank a paragraph (blank-line-separated frame) and put it",
        "P         put ABOVE the cursor instead of below"],
  buys="A hold in animation is a repeated frame. In vim a hold is two keystrokes.")

block_drill(
  id="playback-order", title="playback order", skill="swap adjacent lines",
  concept="lines-and-blocks", tier=3, seconds=50,
  start=["[   ]", "[## ]", "[#  ]", "[###]"],
  target=["[   ]", "[#  ]", "[## ]", "[###]"],
  cursor="j^",
  recipe=[("ddp", "delete this line and put it back after the next one. They swap."),
          (":wq", "save and quit")],
  expected="ddp:wq<CR>",
  keys=["ddp    swap this line with the one below     ddkP   swap with the one above",
        ":m+1   move this line down one              :m-2   move it up one",
        ":5,9m0 move a range of lines to the top of the file"],
  buys="Authoring order and playback order are independent. Re-sorting is one idiom.")

block_drill(
  id="block-erase", title="subtractive erase", skill="blockwise delete",
  concept="lines-and-blocks", tier=3, seconds=80,
  start=[".:*:.", ".:*:.", ".:*:."],
  target=[".:.", ".:.", ".:."],
  cursor="^",
  recipe=[("f*", "find the star on this line"),
          ("<C-v>", "enter blockwise visual mode"),
          ("jjl", "extend the block down two lines and right one column"),
          ("d", "delete the rectangle"),
          (":wq", "save and quit")],
  expected="f*<C-v>jjld:wq<CR>",
  keys=["<C-v>jjd      delete a rectangle       <C-v>jjr.   fill it with one glyph",
        "<C-v>jj~      toggle case in a column",
        "Subtractive animation: draw the finished object, then erase one layer per frame."],
  buys="Erasing a layer per frame is how accretive animations are actually authored.")

block_drill(
  id="ex-copy", title="duplicate a frame line", skill="ex ranges",
  concept="registers-and-ranges", tier=3, seconds=55,
  start=[" . ", "/|\\"],
  target=[" . ", "/|\\", "/|\\"],
  cursor="j^",
  recipe=[(":t.", "copy THIS line (.) to just after THIS line. Type colon, t, dot."),
          ("<CR>", "run it"),
          (":wq", "save and quit")],
  expected=":t.<CR>:wq<CR>",
  keys=[":t.     copy this line below itself      :t0    copy it to the top of the file",
        ":m0     move this line to the top        :m$    move it to the bottom",
        ":%s/o/0/g   substitute on every line",
        "yyp does the same as :t. Ranges scale to a hundred lines; yyp does not."],
  buys="The colon line takes a range. That range is the half that scales.")

block_drill(
  id="mirror-run", title="hand-mirrored run", skill="single character replace",
  concept="motion-precision", tier=3, seconds=70,
  start=["_.-'", "_.-'"],
  target=["_.-'", "'-._"],
  cursor="j^",
  recipe=[("r'", "replace the character under the cursor with a single quote"),
          ("l r-", "step right, replace with a dash"),
          ("l r.", "step right, replace with a dot"),
          ("l r_", "step right, replace with an underscore"),
          (":wq", "save and quit")],
  expected="r'lr-lr.lr_:wq<CR>",
  keys=["r<char>   replace exactly one character, staying in normal mode",
        "3rx       replace the next three characters with x",
        "R         overwrite mode, until <Esc>",
        "Mirror art by retyping the row backwards with each glyph swapped for its",
        "mirror. Never use a software flip: _ . - ' mirror to ' - . _"],
  buys="r is the surgical tool. One glyph, one key, no mode change.")

block_drill(
  id="dot-column", title="spine joint", skill="the dot command across lines",
  concept="repeat", tier=3, seconds=70,
  start=["o---o", "o---o", "o---o"],
  target=["o-+-o", "o-+-o", "o-+-o"],
  cursor="^",
  recipe=[("2l", "move two columns right, onto the middle dash"),
          ("r+", "replace it with a plus"),
          ("j.", "step down. The dot repeats r+ at the SAME column."),
          ("j.", "and again"),
          (":wq", "save and quit")],
  expected="2lr+j.j.:wq<CR>",
  keys=["j keeps your column, so j. walks an edit down a stack of frames",
        "3.        repeat the change three times in place",
        "For a taller stack, record it instead: qq r+ j q then 20@q"],
  buys="Vertical repetition without a macro. The cheapest way to edit a stack.")

# Trailing whitespace in art renders as a visible glyph under a `listchars`
# trail setting (the real config shows ` _ ` as ` _-`, which reads as a dash in
# the art). Verified live 2026-09-18. matches() rstrips anyway, so strip here.
for _d in D:
    _d["start"] = [l.rstrip() for l in _d["start"]]
    _d["target"] = [l.rstrip() for l in _d["target"]]

doc = {
  "schema": "vim-daily/curriculum@1",
  "generated": "2026-09-18",
  "provenance": {
    "concepts": "Written for this repo. Framing follows the paradigm-first style of "
                "blog.codeminer42.com 'A Noob's Neovim Journey Pt.1' (2024-10-23).",
    "drill_shape": "concept -> skill -> recipe -> challenge -> mastery counter, the "
                   "structure used by Vim Hero and vim-adventures lesson trees. The "
                   "fields below are deliberately generic so an external curriculum "
                   "can be imported into this same shape without touching the runner.",
    "frame_drills": "Tier 3 tasks are the monospaced-art operations described in the "
                    "ascii-art-authoring skill (Stone Story RPG method): holds as "
                    "repeated frames, authoring order vs playback order, subtractive "
                    "erasure per frame, and hand-mirrored runs."
  },
  # Unlocks are in lifetime completions. Tuned for the hourly cadence adopted
  # 2026-09-18: at ~12/day tier 2 arrives within a day and tier 3 the day after.
  # Any drill can be run now regardless, with `vim-drill --drill <id>`.
  "tiers": {"1": {"unlock_at": 0}, "2": {"unlock_at": 8}, "3": {"unlock_at": 14}},
  "concepts": CONCEPTS,
  "drills": D,
}

out = os.path.expanduser("~/.local/share/vim-daily/curriculum.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    json.dump(doc, f, indent=1, ensure_ascii=True)
    f.write("\n")
print("wrote", out, len(D), "drills", len(CONCEPTS), "concepts")
