"""Explain Vim key strings command by command (VD-13).

The operator could not read `jforO` ("I need to be taught 'f', I don't know what
that means"): recipes were shown as one unbroken string.  `explain(keys)` splits
a recipe into the commands Vim actually executes and gives each a plain-English
meaning, using Vim's grammar:  [count] operator motion/text-object, and for
command-line (Ex) commands  [range] command arguments flags.

`families(keys)` returns the same commands generalised (`f{char}`, `r{char}`,
`:[range]s/old/new/g`), so a lesson that hides its exact keys can still teach
which kinds of command it needs.
"""
import re

_SPECIAL = re.compile(r"<(?:[A-Za-z]-)?[A-Za-z0-9]+>")

KEY_NAMES = {"<CR>": "Enter", "<Esc>": "Esc", "<BS>": "Backspace", "<Space>": "Space",
             "<Tab>": "Tab"}


def tokens(keys):
    out, i = [], 0
    while i < len(keys):
        m = _SPECIAL.match(keys, i) if keys[i] == "<" else None
        if m:
            out.append(m.group(0))
            i = m.end()
        else:
            out.append(keys[i])
            i += 1
    return out


def _show(text):
    """Render typed text so spaces and specials stay visible."""
    return "".join(KEY_NAMES.get(t, t) if t.startswith("<") and len(t) > 1 else t
                   for t in tokens(text)) if text else ""


def _q(text):
    return "'%s'" % text


MOTIONS = {
    "h": "left one column", "j": "down one line", "k": "up one line",
    "l": "right one column", "w": "to the start of the next word",
    "b": "back to the start of the word", "e": "to the end of the word",
    "W": "to the next space-separated WORD", "B": "back one WORD",
    "E": "to the end of the WORD", "0": "to column 1 of the line",
    "^": "to the first non-blank character", "$": "to the end of the line",
    "G": "to the last line", "}": "to the next blank line (end of this frame)",
    "{": "to the previous blank line", ";": "repeat the last f/t find",
    ",": "repeat the last f/t find backwards", "%": "to the matching bracket",
    "n": "to the next search match", "N": "to the previous search match",
    "H": "to the top of the window", "M": "to the middle of the window",
    "L": "to the bottom of the window", "|": "to column 1",
}
FIND = {"f": "jump forward to the next %s on this line",
        "F": "jump back to the previous %s on this line",
        "t": "jump forward to just before the next %s",
        "T": "jump back to just after the previous %s"}
SIMPLE = {
    "x": "delete the character under the cursor",
    "X": "delete the character before the cursor",
    "D": "delete from the cursor to the end of the line",
    "J": "join the next line onto this one",
    "u": "undo the last change", "<C-r>": "redo (undo the undo)",
    ".": "repeat the last change", "p": "put (paste) after the cursor / below this line",
    "P": "put (paste) before the cursor / above this line",
    "~": "toggle the case of the character", "Y": "yank (copy) the whole line",
    "<C-a>": "add 1 to the number under/after the cursor",
    "<C-x>": "subtract 1 from the number under/after the cursor",
    "<Esc>": "back to Normal mode", "<C-d>": "scroll down half a screen",
    "<C-u>": "scroll up half a screen", "*": "search for the word under the cursor",
    "gv": "reselect the last Visual selection",
}
INSERTS = {
    "i": "insert before the cursor", "a": "append after the cursor",
    "I": "insert at the start of the line", "A": "append at the end of the line",
    "o": "open a NEW LINE BELOW and type", "O": "open a new line above and type",
    "s": "delete the character and type", "S": "clear the line and type",
    "C": "change (delete) to the end of the line and type",
}
OPERATORS = {"d": "delete", "c": "change", "y": "yank (copy)",
             ">": "shift right", "<": "shift left", "=": "re-indent"}
DOUBLED = {"dd": "delete the whole line", "cc": "change the whole line",
           "yy": "yank (copy) the whole line", ">>": "shift the line right",
           "<<": "shift the line left", "==": "re-indent the line"}
OBJECTS = {"w": "word", "W": "WORD", "s": "sentence", "p": "paragraph (a whole frame)",
           "(": "( ) pair", ")": "( ) pair", "b": "( ) pair", "[": "[ ] pair",
           "]": "[ ] pair", "{": "{ } pair", "}": "{ } pair", "B": "{ } pair",
           "<": "< > pair", ">": "< > pair", '"': '" " pair', "'": "' ' pair",
           "`": "` ` pair", "t": "tag"}
EX_NAMES = {
    "s": "substitute", "t": "copy lines to", "co": "copy lines to", "copy": "copy lines to",
    "m": "move lines to", "move": "move lines to", "g": "on every matching line run",
    "global": "on every matching line run", "v": "on every NON-matching line run",
    "normal": "run Normal-mode keys", "norm": "run Normal-mode keys",
    "d": "delete lines", "y": "yank lines", "r": "read a file below", "read": "read a file below",
    "set": "change an editor option", "j": "join lines", "undo": "undo",
    "vsplit": "open a vertical split", "diffthis": "join this window to the diff",
    "diffoff": "leave diff mode", "earlier": "visit an older undo-tree state",
    "later": "visit a newer undo-tree state",
    "vnew": "open a new empty window on the left", "new": "open a new empty window above",
    "bwipeout": "remove this buffer (and its window) completely",
    "bw": "remove this buffer (and its window) completely",
}


# VD-42: a recipe line must say what an option or a pattern DOES, not echo it.
OPTION_ALIASES = {"cuc": "cursorcolumn", "cc": "colorcolumn", "ve": "virtualedit",
                  "sw": "shiftwidth", "scb": "scrollbind", "nolist": "list",
                  "nocursorcolumn": "cursorcolumn", "nocuc": "cursorcolumn"}
OPTION_NOTES = {
    "list": lambda _v: ("show invisible characters: a tab, a trailing space and the line end "
                        "become visible marks (display only; turn off with :set nolist)"),
    "cursorcolumn": lambda _v: ("highlight the whole screen column the cursor is in, so you can "
                                "check that cells line up across rows (off: :set nocursorcolumn)"),
    "colorcolumn": lambda v: ("paint screen column %s as a ruler; anything touching or past it "
                              "is outside the frame (off: :set colorcolumn=)" % (v or "N")),
    "virtualedit": lambda v: ("let the cursor stand in empty cells past a row's end "
                              "(%s); off: :set virtualedit=" % (v or "all")),
    "shiftwidth": lambda v: ("make >> and << shift a row by %s cell%s" %
                             (v or "N", "" if v == "1" else "s")),
    "scrollbind": lambda _v: "scroll this window together with every other scrollbind window",
}

_PATTERN_ATOMS = [
    ("\\s", "a space or tab"), ("\\S", "any non-space glyph"), ("\\d", "a digit"),
    ("\\+", "one or more of the previous item"), ("\\=", "zero or one of the previous item"),
    ("\\.", "a literal ."), ("\\*", "a literal *"), ("\\/", "a literal /"),
    ("\\\\", "a literal backslash"), ("*", "zero or more of the previous item"),
    (".", "any one character"), ("^", "the start of the line"), ("$", "the end of the line"),
]


def pattern_parts(pattern):
    """Split a search pattern into (piece, meaning) pairs for teaching."""
    parts, i = [], 0
    while i < len(pattern):
        if pattern[i] == "[":
            j = pattern.find("]", i + 1)
            if j > i:
                parts.append((pattern[i:j + 1], "any one of %s" % pattern[i + 1:j]))
                i = j + 1
                continue
        for atom, meaning in _PATTERN_ATOMS:
            if pattern.startswith(atom, i):
                if atom == "^" and i != 0 or atom == "$" and i != len(pattern) - 1:
                    continue
                parts.append((atom, meaning))
                i += len(atom)
                break
        else:
            parts.append((pattern[i], "the literal %s" % pattern[i]))
            i += 1
    return parts


def _pattern_gloss(pattern):
    parts = pattern_parts(pattern)
    if all(meaning.startswith("the literal ") for _p, meaning in parts):
        return _q(pattern)
    return "%s (%s)" % (_q(pattern), ", then ".join(meaning for _p, meaning in parts))


# Concept-overload audit #1/#2/#13: multi-key commands read as one idea.
DIGRAPHS = {".M": "·", "''": "´", "'m": "¯", "'-": "‾", "DG": "°", "Sb": "∙",
            "z*": "ζ", "o!": "ò", "o'": "ó", "!I": "¡"}
WINDOW_KEYS = {"p": "go back to the previous window", "w": "go to the next window",
               "v": "split the window side by side", "s": "split the window top/bottom",
               "c": "close this window", "o": "close every other window",
               "q": "quit this window", "h": "go to the window on the left",
               "l": "go to the window on the right", "j": "go to the window below",
               "k": "go to the window above", "=": "make the windows equal size"}
NOT_LINE_COMMANDS = {"earlier", "later", "diffthis", "diffoff", "vsplit", "vnew", "new",
                     "undo", "read", "r", "set", "silent", "bwipeout", "bw"}


def _range_words(rng):
    if not rng:
        return "on the current line"
    if rng == "%":
        return "on every line"
    if re.fullmatch(r"\d+", rng):
        return "on line %s" % rng
    m = re.fullmatch(r"(\d+),(\d+)", rng)
    if m:
        return "on lines %s-%s" % m.groups()
    if rng == "'<,'>":
        return "on the Visual selection"
    return "on range %s" % rng


def _dest_words(dest):
    dest = dest.strip()
    if dest == "$":
        return "after the last line"
    if dest == "0":
        return "before line 1"
    if dest == ".":
        return "below the current line"
    if re.fullmatch(r"\d+", dest):
        return "after line %s" % dest
    return "to %s" % dest


def _explain_ex(text):
    """Explain one command-line command (without the leading ':' and <CR>)."""
    m = re.match(r"^((?:[%.,$0-9+\-]|'[a-z<>])*)\s*([a-z]+!?)(.*)$", text)
    if not m:
        return "run the command-line command %s" % _q(text), ":" + text
    rng, name, rest = m.groups()
    bang = name.endswith("!")
    name = name.rstrip("!")
    where = _range_words(rng)
    if name == "silent" and rest.strip():
        inner, _fam = _explain_ex(rest.strip())
        return "without messages: " + inner, ":silent"
    if name in ("read", "r") and rest.strip() in ("#", "%"):
        what = ("the file you had open before (# = the alternate file)" if rest.strip() == "#"
                else "a second copy of THIS file (% = the current file here; in :%s it "
                     "means every line)")
        where_ = "above line 1 (0 = before the first line)" if rng == "0" else "below the cursor"
        return "read in %s, placed %s" % (what, where_), ":read " + rest.strip()
    if name == "diffoff":
        return ("leave diff mode" + (" in every window (! = all)" if bang else "")), ":diffoff" + \
            ("!" if bang else "")
    if name in ("bwipeout", "bw"):
        return (EX_NAMES[name] + ("; ! = even with unsaved changes" if bang else "")), \
            ":bwipeout" + ("!" if bang else "")
    fam_rng = "[range]" if rng else ""
    if name == "s" and rest[:1] in "/@#|!":
        sep = rest[0]
        parts = rest[1:].split(sep)
        old = parts[0] if parts else ""
        new = parts[1] if len(parts) > 1 else ""
        flags = parts[2] if len(parts) > 2 else ""
        text_ = "%s, replace %s with %s" % (
            where, _pattern_gloss(old), _q(new) if new else "nothing (delete the match)")
        text_ += ("; g = every match on the line, not just the first" if "g" in flags
                  else "; first match on each line only")
        if "e" in flags:
            text_ += "; e = no error when a line has no match"
        family_flags = "".join(flag for flag in "ge" if flag in flags)
        return text_, ":%ss/old/new/%s" % (fam_rng, family_flags)
    if name in ("t", "co", "copy", "m", "move"):
        verb = "copy" if name in ("t", "co", "copy") else "move"
        return ("%s %s %s" % (verb, where.replace("on ", "", 1), _dest_words(rest)),
                ":%s%s{dest}" % (fam_rng, name))
    if name in ("g", "global", "v"):
        m = re.fullmatch(r"(.)(.*?)\1\s*(normal!?|norm!?)\s+(.*)", rest)
        if m:
            which = "matching" if name != "v" else "NOT matching"
            return ("on every line %s %s, run the Normal-mode keys %s" % (
                which, _pattern_gloss(m.group(2)), _q(m.group(4))), ":%s/pattern/normal" % name)
        return ("%s: %s" % (EX_NAMES[name], _q(rest)), ":%s/pattern/command" % name)
    if name in ("normal", "norm"):
        return ("%s, run the Normal-mode keys %s" % (where, _q(rest.strip())),
                ":%snormal {keys}" % fam_rng)
    if name == "set":
        option = rest.strip()
        base = re.split(r"[=!&?]", option, 1)[0]
        base = OPTION_ALIASES.get(base, base)
        note = OPTION_NOTES.get(base)
        if note is None:
            return "set the editor option %s" % _q(option), ":set %s" % base
        value = option.split("=", 1)[1] if "=" in option else ""
        return note(value), ":set %s" % base
    if name in EX_NAMES:
        if not rng and name in NOT_LINE_COMMANDS:
            return "%s%s" % (EX_NAMES[name], (" " + rest.strip()) if rest.strip() else ""), \
                ":%s" % name
        return "%s, %s%s" % (where, EX_NAMES[name], (" " + rest.strip()) if rest.strip() else ""), \
            ":%s%s" % (fam_rng, name)
    return "run the command-line command %s" % _q(text), ":" + name


def _typed_until_esc(tk, i):
    """Collect insert/replace-mode text up to <Esc>; return (text, next_index)."""
    j = i
    while j < len(tk) and tk[j] != "<Esc>":
        j += 1
    return "".join(tk[i:j]), min(j + 1, len(tk))


def explain(keys):
    """Return [(chunk, meaning, family)] for a recipe key string."""
    tk, i, out = tokens(keys), 0, []
    visual = False
    while i < len(tk):
        start = i
        count = ""
        while i < len(tk) and tk[i].isdigit() and not (tk[i] == "0" and not count):
            count += tk[i]
            i += 1
        reg = ""
        if i < len(tk) and tk[i] == '"' and i + 1 < len(tk):
            reg = tk[i + 1]
            i += 2
        if i >= len(tk):
            out.append(("".join(tk[start:i]), "count %s" % count, "[count]"))
            break
        c = tk[i]
        n = ("%s times: " % count) if count else ""
        rw = (" (register %s)" % reg) if reg else ""
        fam = "[count]" if count else ""
        fam += ('"{reg}' if reg else "")
        if visual and c in ("d", "c", "y", ">", "<", "=", "r", "I", "A", "J", "~", "p", "P", "x"):
            visual = False
            i += 1
            if c == "r" and i < len(tk):
                ch = tk[i]
                i += 1
                meaning, fam_ = "replace every selected character with %s" % _q(ch), "Visual r{char}"
            elif c in ("I", "A", "c"):
                text, i = _typed_until_esc(tk, i)
                where = {"I": "insert before", "A": "append after", "c": "replace"}[c]
                meaning = "%s the selection on every row: %s, then Esc" % (where, _q(_show(text)))
                fam_ = "Visual %s{text}<Esc>" % c
            else:
                verb = {"d": "delete", "y": "yank (copy)", ">": "shift right", "<": "shift left",
                        "=": "re-indent", "J": "join", "~": "toggle case of", "x": "delete",
                        "p": "replace with the register", "P": "replace with the register"}[c]
                meaning, fam_ = "%s the selection" % verb, "Visual " + c
            out.append(("".join(tk[start:i]), meaning + rw, fam_))
            continue
        if c == ":":
            j = i + 1
            while j < len(tk) and tk[j] != "<CR>":
                j += 1
            text = "".join(tk[i + 1:j])
            meaning, family = _explain_ex(text)
            i = min(j + 1, len(tk))
            if text in ("w", "wq", "q", "q!", "x", "wq!"):
                meaning, family = {"w": "save", "wq": "save and quit (submit)",
                                   "q": "quit", "q!": "quit without saving",
                                   "x": "save and quit", "wq!": "force save and quit"}[text], ":" + text
            out.append(("".join(tk[start:i]), meaning + " (Enter runs it)", family))
            continue
        if c in "/?":
            j = i + 1
            while j < len(tk) and tk[j] != "<CR>":
                j += 1
            pat = "".join(tk[i + 1:j])
            i = min(j + 1, len(tk))
            out.append(("".join(tk[start:i]), "search %s for %s (Enter runs it)" % (
                "forward" if c == "/" else "backward", _q(pat)), c + "pattern"))
            continue
        if c in FIND and i + 1 < len(tk):
            ch = tk[i + 1]
            i += 2
            out.append(("".join(tk[start:i]), n + FIND[c] % _q(ch), fam + c + "{char}"))
            continue
        if c == "r" and i + 3 < len(tk) and tk[i + 1] == "<C-k>":
            pair = tk[i + 2] + tk[i + 3]
            i += 4
            glyph = DIGRAPHS.get(pair)
            out.append(("".join(tk[start:i]), n + "replace the character under the cursor with "
                        "the digraph Ctrl-k %s%s (a glyph you cannot type directly)" % (
                            pair, (" = " + _q(glyph)) if glyph else ""), fam + "r<C-k>{a}{b}"))
            continue
        if c == "r" and i + 1 < len(tk):
            ch = tk[i + 1]
            i += 2
            out.append(("".join(tk[start:i]), n + "replace the character under the cursor with %s"
                        % _q(" " if ch == "<Space>" else ch), fam + "r{char}"))
            continue
        if c == "R":
            text, i = _typed_until_esc(tk, i + 1)
            m = re.fullmatch(r"<C-r>(.)", "".join(text) if isinstance(text, list) else str(text))
            if m:
                out.append(("".join(tk[start:i]),
                            "Replace mode: overwrite with the contents of register %s "
                            "(in Insert/Replace mode Ctrl-r {reg} pastes a register; in Normal "
                            "mode Ctrl-r is redo), then Esc" % _q(m.group(1)), "R<C-r>{reg}<Esc>"))
                continue
            out.append(("".join(tk[start:i]),
                        "Replace mode: type over the existing characters with %s, then Esc"
                        % _q(_show(text)), "R{text}<Esc>"))
            continue
        if c in INSERTS:
            text, i = _typed_until_esc(tk, i + 1)
            out.append(("".join(tk[start:i]), "%s%s %s, then Esc" % (n, INSERTS[c], _q(_show(text))),
                        fam + c + "{text}<Esc>"))
            continue
        if c in ("q",) and i + 1 < len(tk):
            reg = tk[i + 1]
            j = i + 2
            while j < len(tk) and tk[j] != "q":
                j += 1
            body = "".join(tk[i + 2:j])
            i = min(j + 1, len(tk))
            out.append(("".join(tk[start:i]), "record a macro into register %s: %s, then q stops"
                        % (_q(reg), _q(body)), "q{reg}...q"))
            continue
        if c == "@" and i + 1 < len(tk):
            reg = tk[i + 1]
            i += 2
            out.append(("".join(tk[start:i]), n + ("replay the last macro" if reg == "@"
                                                   else "replay macro %s" % _q(reg)), fam + "@{reg}"))
            continue
        if c == "g" and i + 1 < len(tk):
            two = "g" + tk[i + 1]
            i += 2
            if two == "gR":
                text, i = _typed_until_esc(tk, i)
                out.append(("".join(tk[start:i]),
                            "Virtual Replace mode: overwrite screen cells with %s, then Esc"
                            % _q(_show(text)), "gR{text}<Esc>"))
                continue
            meaning = {"gg": "to line %s" % count if count else "to the first line",
                       "gv": SIMPLE["gv"], "gj": "down one screen line",
                       "gk": "up one screen line", "g~": "toggle case over a motion",
                       "gu": "lowercase over a motion", "gU": "uppercase over a motion",
                       "ga": "inspect the character value",
                       "g-": "visit the previous undo-tree state",
                       "g_": "to the last non-blank character of the line",
                       "g+": "visit the next undo-tree state"}.get(two, two)
            out.append(("".join(tk[start:i]), meaning, two))
            if two == "gv":
                visual = True
            continue
        if c == "z" and i + 1 < len(tk) and tk[i + 1] in ("p", "P"):
            two = "z" + tk[i + 1]
            i += 2
            out.append(("".join(tk[start:i]),
                        "paste the block %s without adding trailing spaces" %
                        ("after" if two == "zp" else "before"), two))
            continue
        if c == "<C-w>" and i + 1 < len(tk):
            key = tk[i + 1]
            i += 2
            out.append(("".join(tk[start:i]), "window command: %s" % WINDOW_KEYS.get(
                key, "Ctrl-w then %s" % _q(key)), "<C-w>{x}"))
            continue
        if c == "z" and i + 1 < len(tk) and tk[i + 1] in ("y", "Y"):
            i += 2
            out.append(("".join(tk[start:i]),
                        "yank the selected block WITHOUT the trailing spaces of short rows", "zy"))
            continue
        if c == "G":
            i += 1
            out.append(("".join(tk[start:i]), ("go to line %s" % count) if count else "go to the last line",
                        "[count]G"))
            continue
        if c == "|":
            i += 1
            out.append(("".join(tk[start:i]), "go to column %s" % (count or "1"), "[count]|"))
            continue
        if c in OPERATORS:
            if i + 1 < len(tk) and tk[i + 1] == c:
                if count:
                    i += 2
                    what = {"dd": "delete", "yy": "yank (copy)", "cc": "change",
                            ">>": "shift right", "<<": "shift left", "==": "re-indent"}[c + c]
                    out.append(("".join(tk[start:i]), "%s %s whole lines starting here%s"
                                % (what, count, rw), "[count]" + c + c))
                    continue
                i += 2
                out.append(("".join(tk[start:i]), n + DOUBLED[c + c] + rw, fam + c + c))
                continue
            j = i + 1
            mcount = ""
            while j < len(tk) and tk[j].isdigit():
                mcount += tk[j]
                j += 1
            if j < len(tk) and tk[j] in ("i", "a") and j + 1 < len(tk):
                obj = OBJECTS.get(tk[j + 1], tk[j + 1])
                meaning = "%s %s %s" % (OPERATORS[c], "inside the" if tk[j] == "i" else "around the", obj)
                i = j + 2
                fam_ = c + tk[j] + "{object}"
            elif j < len(tk) and tk[j] in FIND and j + 1 < len(tk):
                meaning = "%s up to %s" % (OPERATORS[c], _q(tk[j + 1]))
                i = j + 2
                fam_ = c + tk[j] + "{char}"
            elif j < len(tk):
                meaning = "%s %s" % (OPERATORS[c], MOTIONS.get(tk[j], "over the motion " + tk[j]))
                i = j + 1
                fam_ = c + "{motion}"
            else:
                i = j
                meaning, fam_ = OPERATORS[c], c
            if mcount:
                meaning = "%s × " % mcount + meaning
            if c == "c":
                text, i = _typed_until_esc(tk, i)
                meaning += ", type %s, then Esc" % _q(_show(text))
            out.append(("".join(tk[start:i]), n + meaning + rw, fam + fam_))
            continue
        if c in ("v", "V", "<C-v>"):
            kind = {"v": "characters", "V": "whole lines", "<C-v>": "a rectangular block"}[c]
            i += 1
            visual = True
            out.append(("".join(tk[start:i]), "start Visual mode selecting %s" % kind, c))
            continue
        if c in SIMPLE:
            i += 1
            out.append(("".join(tk[start:i]), n + SIMPLE[c] + rw, fam + c))
            continue
        if c in MOTIONS:
            i += 1
            out.append(("".join(tk[start:i]), n + MOTIONS[c], fam + c))
            continue
        if c == "<C-k>" and i + 2 < len(tk):
            i += 3
            out.append(("".join(tk[start:i]), "type a digraph character", "<C-k>{a}{b}"))
            continue
        i += 1
        out.append(("".join(tk[start:i]), "press %s" % _show(c), c))
    return out


def families(keys):
    """De-duplicated generalised command forms used by a key string."""
    seen = []
    for _chunk, meaning, family in explain(keys):
        if family not in [f for f, _m in seen]:
            seen.append((family, meaning))
    return seen


FAMILY_TEACH = {
    "r<C-k>{a}{b}": "r Ctrl-k {a}{b}  replace one cell with a digraph glyph you cannot type (Ctrl-k .M = ·)",
    "<C-w>{x}": "Ctrl-w {x}  window commands: p previous window, w next, v side-by-side split, c close",
    "zy": "zy  yank a Visual block without the trailing spaces of its shorter rows",
    "g_": "g_  jump to the last non-blank character of the line ($ goes past trailing spaces)",
    "R<C-r>{reg}<Esc>": "R Ctrl-r {reg}  in Replace mode, Ctrl-r a types the contents of register a over the text",
    ":g/pattern/normal": ":g/pattern/normal! {keys}  run the same Normal keys on every line the pattern matches",
    ":set list": ":set list  show invisible whitespace as marks (display only; :set nolist hides them)",
    ":set cursorcolumn": ":set cursorcolumn  highlight the cursor's column top to bottom (off: :set nocursorcolumn)",
    ":set colorcolumn": ":set colorcolumn={N}  paint column N as a ruler for the frame's right edge (off: :set colorcolumn=)",
    ":set virtualedit": ":set virtualedit=all  let the cursor stand past a row's end",
    ":set shiftwidth": ":set shiftwidth={N}  choose how far >> and << shift a row",
    ":[range]s/old/new/e": ":{range}s/pattern//e  delete what the pattern matches (/ separates the parts; \\ starts a special piece like \\s); e = no error on lines with no match",
    ":[range]s/old/new/ge": ":{range}s/pattern/new/ge  every match on each line; e = no error when a line has none",
    "j": "j k h l  move down / up / left / right one cell",
    "k": "j k h l  move down / up / left / right one cell",
    "h": "j k h l  move down / up / left / right one cell",
    "l": "j k h l  move down / up / left / right one cell",
    "[count]G": "{N}G  jump to line N  (G alone = last line, gg = first line)",
    "gg": "gg  jump to the first line  ({N}gg = line N)",
    "0": "0 ^ $  jump to column 1 / first glyph / end of line",
    "^": "0 ^ $  jump to column 1 / first glyph / end of line",
    "$": "0 ^ $  jump to column 1 / first glyph / end of line",
    "f{char}": "f{char}  jump to the next {char} on this line  (fo = next 'o'; ; repeats)",
    "t{char}": "t{char}  jump to just before the next {char} on this line",
    "F{char}": "F{char}  jump back to the previous {char} on this line",
    "r{char}": "r{char}  replace the ONE character under the cursor  (rO = make it 'O')",
    "R{text}<Esc>": "R  Replace mode: type over characters without shifting the row; Esc ends",
    "gR{text}<Esc>": "gR  Virtual Replace mode: overwrite screen cells, preserving width across tabs or wide glyphs",
    "ga": "ga  inspect the glyph under the cursor (character plus decimal/hex/octal value)",
    "yy": "yy  yank (copy) the whole line; {N}yy copies N lines",
    "[count]yy": "{N}yy  yank (copy) N whole lines starting at the cursor",
    "dd": "dd  delete the whole line; {N}dd deletes N lines",
    "[count]dd": "{N}dd  delete N whole lines",
    "p": "p  put (paste): whole lines go BELOW this line, characters after the cursor",
    "P": "P  put (paste) above this line / before the cursor",
    "zp": "zp  paste a block after the cursor without manufacturing trailing spaces",
    "zP": "zP  paste a block before the cursor without manufacturing trailing spaces",
    "o{text}<Esc>": "o  open a NEW LINE BELOW and start typing; Esc ends",
    "O{text}<Esc>": "O  open a new line above and start typing; Esc ends",
    "x": "x  delete the character under the cursor (shifts the row left!)",
    "u": "u  undo;  Ctrl-r  redo",
    "<C-r>": "u  undo;  Ctrl-r  redo",
    "g-": "g-  visit the previous state in the undo tree (including another branch)",
    "g+": "g+  visit the next state in the undo tree",
    ".": ".  repeat your last change here",
    ":s/old/new/": ":s/old/new/  substitute on THIS line; add g to replace every match",
    ":s/old/new/g": ":s/old/new/g  substitute every 'old' with 'new' on THIS line",
    ":[range]s/old/new/": ":{range}s/old/new/  substitute on those lines (8 = line 8, 7,9 = lines 7-9, % = all)",
    ":[range]s/old/new/g": ":{range}s/old/new/g  on lines {range}, substitute EVERY 'old' with 'new'",
    ":[range]t{dest}": ":{from},{to}t{dest}  copy whole lines, e.g. :7,9t$ copies lines 7-9 after the last line",
    ":t{dest}": ":t{dest}  copy this line to after line {dest}",
    ":[range]m{dest}": ":{from},{to}m{dest}  move whole lines, e.g. :6,10m0 moves lines 6-10 to the top",
    "V": "V  select whole lines (then y d > etc. act on them)",
    "v": "v  select characters",
    "<C-v>": "Ctrl-v  select a rectangular column block",
    "gv": "gv  reselect the exact previous Visual area in the same character/line/block mode",
    "q{reg}...q": "q{reg} ... q  record a macro;  @{reg} replays it; {N}@{reg} N times",
    "@{reg}": "@{reg}  replay a recorded macro",
    "ci{object}": "ci( / ciw  change INSIDE a pair or word: delete it and type the new text",
    "ca{object}": "ca( / caw  change AROUND a pair or word, including the brackets/space",
    "di{object}": "di( / diw  delete inside a pair or word",
    "da{object}": "dap / daw  delete around a paragraph (frame) or word",
    "yi{object}": "yi( / yiw  yank inside a pair or word",
    "ya{object}": "yap  yank a whole paragraph = one blank-line-separated frame",
    "}": "} {  jump to the next / previous blank line (frame boundary)",
    "{": "} {  jump to the next / previous blank line (frame boundary)",
    "Visual r{char}": "(selection) r{char}  replace every selected character",
    "Visual I{text}<Esc>": "(block) I  type in front of the block on every row; Esc applies",
    "Visual A{text}<Esc>": "(block) $A  type after the end of every selected row; Esc applies",
    "Visual y": "(selection) y  yank (copy) what is selected",
    "Visual d": "(selection) d  delete what is selected",
    "Visual >": "(selection) >  shift the selected lines right by 'shiftwidth'",
    "D": "D  delete from the cursor to the end of the line",
    "C{text}<Esc>": "C  change from the cursor to the end of the line; Esc ends",
    "A{text}<Esc>": "A  append at the end of the line; Esc ends",
    "I{text}<Esc>": "I  insert at the start of the line; Esc ends",
    "i{text}<Esc>": "i  insert before the cursor; Esc ends",
    "a{text}<Esc>": "a  append after the cursor; Esc ends",
    "[count]|": "{N}|  jump to column N of the line",
    ";": ";  repeat the last f/t find (, goes back)",
    ",": ";  repeat the last f/t find (, goes back)",
    "w": "w b e  jump by words (punctuation runs count as words)",
    "b": "w b e  jump by words (punctuation runs count as words)",
    "e": "w b e  jump by words (punctuation runs count as words)",
    "W": "W B E  jump by space-separated WORDS (clusters)",
    "B": "W B E  jump by space-separated WORDS (clusters)",
    "E": "W B E  jump by space-separated WORDS (clusters)",
    "/pattern": "/text Enter  search forward; n = next match, N = previous",
    "n": "/text Enter  search forward; n = next match, N = previous",
    "<C-a>": "Ctrl-a / Ctrl-x  add / subtract 1 from the number on the line",
    ":set {option}": ":set {option}  change an editor setting for this session",
    ":vsplit": ":vsplit  show another window beside this one; Ctrl-w w moves between windows",
    ":diffthis": ":diffthis  include the current window in a side-by-side diff",
    ":diffoff": ":diffoff  leave diff mode in the current window",
    ":earlier": ":earlier {N}  visit an older undo-tree state",
    ":later": ":later {N}  visit a newer undo-tree state",
    ":/pattern/command": ":g/pattern/command  run a command on every line matching pattern",
    ":g/pattern/command": ":g/pattern/command  run a command on every line matching pattern",
    ":[range]normal {keys}": ":{range}normal {keys}  type Normal-mode keys on each line of the range",
    ">>": ">> <<  shift the line right / left by 'shiftwidth'",
    "J": "J  join the next line onto this one",
    "~": "~  toggle case of the character",
    "<C-k>{a}{b}": "Ctrl-k {a}{b}  type a digraph (e.g. Ctrl-k .M = ·)",
    "%": "%  jump to the matching bracket",
    "M": "H M L  jump to the top / middle / bottom of the window",
    "T{char}": "T{char}  jump back to just after the previous {char} on this line",
    "y{motion}": "y{motion}  yank (copy) over a motion, e.g. yl = one character, y$ = to line end",
    ":read": ":read {file}  read a file in below the cursor (:read % = this file's saved copy)",
    "Visual c{text}<Esc>": "(block) c  replace the selected block on every row; Esc applies",
}

GRAMMAR = ("VIM GRAMMAR  [count] verb target: 3yy = 3 x yank line · d$ = delete to end · "
           "fo = find 'o' · rO = replace with 'O'.  Colon commands: :[lines]command/args/flags, "
           "e.g. :3s/a/b/g = on line 3 substitute every a with b (g = all on the line); Enter runs it.")


def teach_lines(keys):
    """One line per command family a recipe needs, without revealing the recipe."""
    lines = []
    for family, meaning in families(keys):
        base = family.replace('"{reg}', "")
        text = FAMILY_TEACH.get(base) or FAMILY_TEACH.get(base.replace("[count]", ""))
        if text is None:
            continue
        if text not in lines:
            lines.append(text)
    return lines


def explain_lines(keys, width=None):
    """`chunk  = meaning` lines for a full recipe."""
    rows = explain(keys)
    pad = max((len(chunk) for chunk, _m, _f in rows), default=0)
    pad = min(pad, 18)
    return ["%-*s = %s" % (pad, chunk, meaning) for chunk, meaning, _f in rows]


# VD-13: a worked example on neutral text for each command family, shown the
# first time a hidden-recipe lesson needs a family that no earlier lesson showed.
EXAMPLES = {
    "r<C-k>{a}{b}": "on `a:c` with the cursor on ':', r Ctrl-k .M makes it `a·c`",
    "<C-w>{x}": "with two windows open, Ctrl-w p jumps back to the one you were just in",
    "zy": "on rows `ab` and `abcd` in a 4-wide block: zy copies `ab` without two padding spaces",
    "g_": "on `ab   ` (3 trailing spaces): g_ lands on b; $ lands on the last space",
    "R<C-r>{reg}<Esc>": "after \"ayl on `*`: R Ctrl-r a Esc overwrites one cell with `*`",
    ":g/pattern/normal": ":g/o/normal! 0rO turns the first cell of every line containing o into O",
    ":set list": "after :set list, `ab   ` shows as `ab···$`: three trailing spaces you could not see before",
    ":set cursorcolumn": "with the cursor on column 7, :set cursorcolumn lights column 7 on every row, so a glyph one cell off stands out",
    ":set colorcolumn": ":set colorcolumn=11 paints column 11; a 10-cell frame must end before the painted stripe",
    ":set virtualedit": "on a 3-cell row, :set virtualedit=all then 9| puts the cursor in empty column 9",
    ":set shiftwidth": ":set shiftwidth=1 then >> moves a row right by exactly one cell",
    ":[range]s/old/new/e": "on `ab   ` and `cd`: :%s/\\s\\+$//e makes `ab` and leaves `cd` (no error for it)",
    ":[range]s/old/new/ge": ":%s/-/=/ge changes every - in the file and stays quiet on lines without one",
    "f{char}": "on `ab-cd-ef` with the cursor on a: f- lands on the first '-'; ; lands on the next '-'",
    "t{char}": "on `ab-cd` with the cursor on a: t- stops on 'b', just before the '-'",
    "F{char}": "on `ab-cd` with the cursor on d: F- jumps back onto the '-'",
    "r{char}": "on `a.c` with the cursor on '.': rO makes it `aOc` (row width unchanged)",
    "R{text}<Esc>": "on `-----` at column 1: R==<Esc> makes it `==---` (overwrites, never inserts)",
    "gR{text}<Esc>": "on `漢..`, gR==<Esc> makes `==..`: two screen cells replace the wide glyph without pulling the dots left",
    "ga": "on `·`, ga reports the glyph and its numeric value without changing the buffer",
    ":s/old/new/": "on `a-b-c`: :s/-/=/ makes `a=b-c` (first match only)",
    ":s/old/new/g": "on `a-b-c`: :s/-/=/g makes `a=b=c` (g = every match on the line)",
    ":[range]s/old/new/": "lines 2-3 only: :2,3s/o/O/ changes the first 'o' on each of those lines",
    ":[range]s/old/new/g": "line 4 only: :4s/-/=/g turns `-- x --` on line 4 into `== x ==`",
    ":[range]t{dest}": "on a 6-line file: :1,3t$ copies lines 1-3 to after line 6 (lines 7-9)",
    ":[range]m{dest}": "on a 6-line file: :4,6m0 moves lines 4-6 to the top",
    ";": "on `a-b-c-d` after f-: ; jumps to the next '-', ; again to the one after",
    ",": "after f- and ; on `a-b-c`: , goes back to the previous '-'",
    "}": "in frames separated by blank lines: } jumps to the blank line after this frame",
    "{": "{ jumps to the blank line before this frame",
    "P": "after yy on line 2 with the cursor on line 5: P puts the copy ABOVE line 5",
    "zp": "after a block yank: zp pastes after the cursor but does not pad shorter rows with trailing spaces",
    "zP": "after a block yank: zP pastes before the cursor but does not pad shorter rows with trailing spaces",
    "p": "after 3yy on lines 1-3 with the cursor on the last line: p puts the 3 lines below it",
    "yy": "3yy on line 4 copies lines 4, 5 and 6 (whole lines)",
    "v": "v then 2l selects 3 characters; r= then turns all 3 into '='",
    "V": "V then 2j selects 3 whole lines; y copies them",
    "<C-v>": "Ctrl-v then 2j selects one column across 3 rows",
    "gv": "after a Visual operator ends the selection: gv reselects the same cells in the same Visual mode",
    "Visual A{text}<Esc>": "Ctrl-v 2j $ A|<Esc> adds '|' after the end of each of the 3 rows",
    "Visual I{text}<Esc>": "Ctrl-v 2j I|<Esc> adds '|' before the block on each of the 3 rows",
    "Visual r{char}": "v2l r= turns the 3 selected characters into '==='",
    ".": "after rO on one line: j . does the same rO on the next line",
    "o{text}<Esc>": "o--<Esc> opens a new line below and types '--'",
    "O{text}<Esc>": "O--<Esc> opens a new line above and types '--'",
    "ya{object}": "yap on a frame copies the whole frame plus its blank line",
    "ci{object}": "on `(o)` with the cursor inside: ci(O<Esc> makes `(O)`",
    "q{reg}...q": "qqr=jq records 'replace with =, go down' into q; 3@q repeats it 3 times",
    "@{reg}": "3@q replays macro q three times",
    "x": "on `abc` at b: x makes `ac` (the row gets shorter!)",
    "D": "on `abc---` at the first '-': D makes `abc`",
    "u": "u undoes the last change; Ctrl-r redoes it",
    "g-": "after exploring two edits: g- visits the older state without discarding the undo branch",
    "g+": "after g-: g+ returns to the newer state",
    "[count]G": "5G jumps to line 5; G alone jumps to the last line",
    "gg": "gg jumps to line 1",
    "[count]|": "12| jumps to column 12",
    "W": "on `ab cd ef`: W jumps from a to c (space-separated WORD)",
    "B": "on `ab cd ef` at e: B jumps back to c",
    "E": "on `ab cd` at a: E jumps to b (end of WORD)",
    "<C-a>": "on `frame 3`: Ctrl-a makes `frame 4`",
    "/pattern": "/\\* then Enter jumps to the next '*'; n repeats",
    "n": "after /x Enter: n jumps to the next 'x'",
    ":vsplit": ":vsplit opens a second view beside the art; :set scrollbind in both keeps frame rows aligned",
    ":diffthis": "run :diffthis in each split to highlight cells that differ between two buffers",
    ":earlier": ":earlier 1 visits the prior undo-tree state; :later 1 comes forward again",
}


def example_for(family):
    base = family.replace('"{reg}', "")
    return EXAMPLES.get(base) or EXAMPLES.get(base.replace("[count]", ""))


# VD-48: the same glyph does different jobs.  `$` is a line address in
# :1,3t$, the end-of-row motion in 2G$ and an end anchor in :%s/\s\+$//e;
# `\` is a glyph in `/!\`, a special-piece prefix in \s.  The learner asked
# "what is the concept diff between / and \ ... i thought \ was an escape
# seq".  Each (symbol, role) gets a plain meaning and a short contrast label.
SYMBOL_ROLES = {
    ("<CR>", "key"): ("<CR> = press Enter (do not type the letters < C R >)", "Enter"),
    ("<Esc>", "key"): ("<Esc> = press the Escape key: it ends Insert/Replace mode and "
                       "returns to Normal mode", "Escape"),
    ("<C-x>", "key"): ("<C-r>, <C-v>, <C-w>, <C-a> … = hold Ctrl and press the letter "
                       "(<C-r> = Ctrl+r)", "Ctrl+letter"),
    ("<Space>", "key"): ("<Space> = press the space bar", "space bar"),
    ("<BS>", "key"): ("<BS> = press Backspace", "Backspace"),
    (":", "cmdline"): (": in Normal mode opens the command line at the bottom of the screen "
                       "(Vim calls these Ex commands); type the command there, <CR> runs it, "
                       "<Esc> cancels", "command line"),
    ("$", "motion"): ("$ on its own = jump to the end of the row (a motion)", "end of row (2G$)"),
    ("$", "address"): ("$ in a line address = the last line of the file "
                       "(:1,3t$ = copy after the last line)", "last line (:1,3t$)"),
    ("$", "anchor"): ("$ at the end of a pattern = match only at the end of the row",
                      "row end in a pattern (\\s\\+$)"),
    ("%", "range"): ("% before a : command = every line of the file (:%s = on all lines)",
                     "every line (:%s)"),
    ("%", "file"): ("% after :read = this file's own name", "this file (:read %)"),
    ("%", "motion"): ("% on its own = jump to the matching bracket", "matching bracket"),
    (".", "dot"): (". in Normal mode = repeat your last change", "repeat last change"),
    (".", "any"): (". inside a pattern = any one character (\\. = a real dot)",
                   "any character in a pattern"),
    (".", "address"): (". in a line address = the current line", "current line"),
    (".", "glyph"): (". after f, t, r or in typed text = just a dot glyph", "a dot glyph (f.)"),
    ("^", "motion"): ("^ on its own = jump to the first glyph of the row", "first glyph"),
    ("^", "anchor"): ("^ at the start of a pattern = match only at the start of the row",
                      "row start in a pattern"),
    ("^", "glyph"): ("^ after f, r or in typed text = just a caret glyph", "a caret glyph"),
    ("|", "column"): ("{N}| = jump to column N (12| = column 12; a motion)", "column jump (12|)"),
    ("|", "glyph"): ("| after i, a, r, f or in a pattern = just a bar glyph in the art",
                     "a bar glyph"),
    ("0", "motion"): ("0 on its own = jump to column 1", "column 1 (0)"),
    ("0", "count"): ("0 after another digit = part of the number (10G = line ten, "
                     "not 1 then 0)", "part of a number (10G)"),
    ("0", "address"): ("0 as a line address = before line 1 (:m0 = move to the top)",
                       "before line 1 (:m0)"),
    (",", "range"): ("a,b in a line address = lines a through b (:4,6 = lines 4-6)",
                     "from,to lines (:4,6)"),
    (",", "motion"): (", on its own = repeat the last f/t find backwards", "find backwards"),
    ("/", "search"): ("/ in Normal mode = search: type the text, <CR> jumps to it",
                      "search (/text)"),
    ("/", "separator"): ("/ inside :s or :g = the divider: s/pattern/replacement/flags",
                         "divider in :s/old/new/"),
    ("/", "glyph"): ("/ after f, r, in typed text or in a pattern = just a slash glyph",
                     "a slash glyph"),
    ("@", "separator"): ("@ right after :s or :g = the divider instead of /, so a / in "
                         "the art needs no escape", "divider in :s@old@new@"),
    ("@", "macro"): ("@ + a register letter = replay that macro (@q)", "replay macro (@q)"),
    ("\\", "special"): ("\\ inside a pattern = the next letter is special (\\s = space or tab, "
                        "\\+ = one or more); you type the backslash yourself, it is not Esc",
                        "special piece (\\s, \\+)"),
    ("\\", "escape"): ("\\ before . * / in a pattern = take that glyph literally "
                       "(\\. = a real dot)", "literal marker (\\.)"),
    ("\\", "literal"): ("\\\\ (two backslashes) in a pattern or replacement = one real "
                        "backslash glyph", "one backslash (\\\\)"),
    ("\\", "glyph"): ("\\ after r or in typed text = just a backslash glyph in the art",
                      "a backslash glyph (/!\\)"),
    ("*", "searchword"): ("* in Normal mode = search for the word under the cursor",
                          "search word"),
    ("*", "repeat"): ("* inside a pattern = zero or more of the previous item",
                      "zero or more in a pattern"),
    ("*", "glyph"): ("* after f, r or in typed text = just a star glyph", "a star glyph (f*)"),
    ('"', "register"): ('"a before y, d or p = use register a, a named clipboard slot '
                        '("ayl copies one cell into a)', 'register ("a)'),
    ("#", "altfile"): ("# after :read = the file you had open before (the alternate file)",
                       "previous file"),
    ("<C-r>", "redo"): ("<C-r> in Normal mode = redo (undo the undo)", "redo"),
    ("<C-r>", "paste"): ("<C-r> {reg} in Insert or Replace mode = type out register {reg}",
                         "paste a register while typing"),
}
_GLYPH_SYMBOLS = set(".^|/\\*$%")

RECIPE_READING = [
    "HOW TO READ A RECIPE (once; it holds for every lesson)",
    "  Press the keys left to right exactly as shown; letters are keys, not words.",
    "  <CR> = press Enter · <Esc> = press Escape · <C-r> = hold Ctrl, press r.",
    "  In reminders {char} = any glyph you choose, {N} = any number, {reg} = a",
    "  register letter, [count] = an optional number. You never type the braces.",
    "  Normal mode (start here): keys are commands. Insert mode (after i a o):",
    "  keys type text until <Esc>. : opens the command line at the bottom.",
]


def _split_sep(rest):
    """Split `/a/b/g` (any separator) into parts, keeping escaped separators."""
    sep, parts, cur, i = rest[0], [], "", 1
    while i < len(rest):
        if rest[i] == "\\" and i + 1 < len(rest):
            cur += rest[i:i + 2]
            i += 2
            continue
        if rest[i] == sep:
            parts.append(cur)
            cur = ""
        else:
            cur += rest[i]
        i += 1
    parts.append(cur)
    return sep, parts


def _pattern_roles(pattern, add):
    for piece, meaning in pattern_parts(pattern):
        if piece in ("\\s", "\\S", "\\d", "\\+", "\\="):
            add("\\", "special")
        elif piece in ("\\.", "\\*", "\\/"):
            add("\\", "escape")
        elif piece == "\\\\":
            add("\\", "literal")
        elif piece == ".":
            add(".", "any")
        elif piece == "*":
            add("*", "repeat")
        elif piece == "^":
            add("^", "anchor")
        elif piece == "$":
            add("$", "anchor")
        elif piece in _GLYPH_SYMBOLS:
            add(piece, "glyph")


_ROLE_CACHE = {}


def symbol_roles(keys):
    """Ordered (symbol, role) pairs a key string uses (VD-48)."""
    if keys in _ROLE_CACHE:
        return list(_ROLE_CACHE[keys])
    out = []

    def add(symbol, role):
        if (symbol, role) in SYMBOL_ROLES and (symbol, role) not in out:
            out.append((symbol, role))

    for token in tokens(keys):
        if token in ("<CR>", "<Esc>", "<Space>", "<BS>"):
            add(token, "key")
        elif token.startswith("<C-"):
            add("<C-x>", "key")
    for chunk, _meaning, family in explain(keys):
        count = re.match(r"[1-9]\d*", chunk)
        if count and "0" in count.group(0):
            add("0", "count")
        if chunk.startswith(":"):
            add(":", "cmdline")
            _ex_roles(chunk[1:].replace("<CR>", ""), add)
            continue
        if family in ("/pattern", "?pattern"):
            add("/", "search")
            _pattern_roles(chunk[1:].replace("<CR>", ""), add)
            continue
        base = family.replace("[count]", "").replace('"{reg}', "")
        if '"{reg}' in family:
            add('"', "register")
        if base.endswith("{char}") and chunk[-1:] in _GLYPH_SYMBOLS:
            add(chunk[-1], "glyph")
        elif base.endswith("{text}<Esc>"):
            for ch in set(chunk[1:]) & _GLYPH_SYMBOLS:
                add(ch, "glyph")
        elif base == "R<C-r>{reg}<Esc>":
            add("<C-r>", "paste")
        elif base == "<C-r>":
            add("<C-r>", "redo")
        elif base in ("$", "0", "^", "%"):
            add(base, "motion")
        elif base == ".":
            add(".", "dot")
        elif base == ",":
            add(",", "motion")
        elif base == "[count]|" or family == "[count]|":
            add("|", "column")
        elif base == "*":
            add("*", "searchword")
        elif base == "@{reg}":
            add("@", "macro")
        elif base.endswith("{motion}") and chunk[-1:] in ("$", "0", "^", "%"):
            add(chunk[-1], "motion")
    _ROLE_CACHE[keys] = tuple(out)
    return out


def _ex_roles(text, add):
    m = re.match(r"^((?:[%.,$0-9+\-]|'[a-z<>])*)\s*([a-z]+!?)(.*)$", text)
    if not m:
        return
    rng, name, rest = m.groups()
    if "%" in rng:
        add("%", "range")
    if "$" in rng:
        add("$", "address")
    if "." in rng:
        add(".", "address")
    if "," in rng:
        add(",", "range")
    dest = rest.strip()
    if name in ("t", "co", "copy", "m", "move"):
        add({"$": "$", "0": "0", ".": "."}.get(dest, ""), "address")
    if name == "silent":
        _ex_roles(dest, add)
        return
    if name in ("read", "r"):
        if rng == "0":
            add("0", "address")
        if dest == "%":
            add("%", "file")
        if dest == "#":
            add("#", "altfile")
    if name in ("s", "g", "global", "v") and rest[:1] and not rest[:1].isalnum() \
            and rest[:1] not in " \"":
        sep, parts = _split_sep(rest)
        add(sep if sep in ("/", "@") else "", "separator")
        _pattern_roles(parts[0], add)
        if name == "s" and len(parts) > 1 and "\\\\" in parts[1]:
            add("\\", "literal")
        if name != "s" and len(parts) > 1:
            normal = re.match(r"\s*norm(?:al)?!?\s+(.*)", parts[1])
            if normal:
                for pair in symbol_roles(normal.group(1)):
                    add(*pair)


# VD-48 / concept-overload audit F17: families that had no teaching line or no
# worked example, so the NEW CONCEPT ALERT echoed the command instead.
FAMILY_TEACH.update({
    ":read %": ":read %  read a second copy of this file below the cursor (% = this file here)",
    ":read #": ":read #  read in the file you had open before (# = the alternate file)",
    ":vnew": ":vnew  open a new, empty window on the left (a scratch space)",
    ":silent": ":silent {command}  run the command without printing a message",
    ":set scrollbind": ":set scrollbind  scroll this window together with the other bound window",
    ":diffoff!": ":diffoff!  leave diff mode in every window (! = all windows)",
    ":diffoff": ":diffoff  leave diff mode in the current window",
    ":bwipeout!": ":bwipeout!  remove this buffer and its window (! = even if unsaved)",
    ":bwipeout": ":bwipeout  remove this buffer and its window",
})
EXAMPLES.update({
    "0": "on `  ab` with the cursor on b: 0 lands on the first space (column 1)",
    "$": "on `ab  ` (2 trailing spaces): $ lands on the last space; x there deletes it",
    "^": "on `  ab`: ^ lands on a, the first glyph after the spaces",
    "<C-r>": "after rO then u (the O is gone): Ctrl-r brings the O back",
    "i{text}<Esc>": "on `ac` with the cursor on c: ib<Esc> makes `abc`",
    "[count]dd": "on 5 rows with the cursor on row 2: 2dd removes rows 2 and 3",
    "dd": "on 3 rows, 2G then dd removes row 2; the rows below move up",
    "da{object}": "dap on a frame deletes the frame and the blank line after it",
    "T{char}": "on `ab-cd` with the cursor on d: T- stops on c, just after the '-'",
    "y{motion}": "on `*ab` with the cursor on *: yl copies just the `*`",
    "C{text}<Esc>": "on `ab---` at the first '-': C==<Esc> makes `ab==`",
    "Visual y": "v2l then y copies the 3 selected characters",
    "Visual d": "V2j then d deletes the 3 selected rows",
    "Visual c{text}<Esc>": "Ctrl-v 2j c=<Esc> replaces one column on 3 rows with '='",
    ">>": ":set shiftwidth=1 then >> moves the row right by one cell; << moves it back",
    "%": "on `(ab)` with the cursor on (: % jumps to the matching )",
    "w": "on `ab-cd` at a: w jumps to '-' (a punctuation run is its own word)",
    ":read %": ":read % under a 3-row frame adds a second copy of those 3 rows",
    ":read #": ":vnew then :read # shows the file you were editing in the new window",
    ":vnew": ":vnew opens an empty window on the left; :q closes it again",
    ":silent": ":silent 0read # reads the previous file in without a '3 lines' message",
    ":set scrollbind": "with two windows side by side, :set scrollbind in both keeps rows level",
    ":diffoff!": "after :diffthis in two windows, :diffoff! clears the diff colours in both",
    ":bwipeout!": "in the scratch window, :bwipeout! closes it and throws its text away",
})



# VD-49: the operator asked for this chat explanation to become curriculum:
# draw any :s command as a labelled tree, then say it in plain English.
_SUB_RE = re.compile(r":([%.,$0-9']*)s/((?:\\/|[^/])*)/((?:\\/|[^/])*)/([a-z]*)")
_FLAG_WORDS = {"g": "g: every match on the line, not just the first",
               "e": "e: no error on lines that have no match",
               "c": "c: ask before each change", "i": "i: ignore upper/lower case"}


def substitute_anatomy(keys):
    """Return (diagram_rows, plain_english) for the first :s command in keys."""
    m = _SUB_RE.search(keys)
    if not m:
        return None
    rng, pattern, replacement, flags = m.groups()
    text = ":" + rng + "s/" + pattern + "/" + replacement + "/" + flags
    labels = []  # (column, text)
    col = 1
    if rng:
        where = _range_words(rng).replace("on ", "", 1)
        labels.append((col, "%s = %s" % (rng, where)))
        col += len(rng)
    labels.append((col, "s = substitute (no range before it = this line only)"
                   if not rng else "s = substitute"))
    col += 1
    labels.append((col, "divider"))
    col += 1
    for piece, meaning in pattern_parts(pattern):
        labels.append((col, "%s = %s" % (piece, meaning)))
        col += len(piece)
    labels.append((col, "divider"))
    col += 1
    if replacement:
        labels.append((col, "replacement: %s" % _q(replacement)))
        col += len(replacement)
        labels.append((col, "divider"))
    else:
        labels.append((col, "divider · empty replacement → delete"))
    col += 1
    for flag in flags:
        labels.append((col, _FLAG_WORDS.get(flag, "%s: flag" % flag)))
        col += 1
    rows = [" " + text]
    columns = [c for c, _t in labels]
    for index in range(len(labels) - 1, -1, -1):
        c, label = labels[index]
        line = [" "] * (c + 1)
        for other in columns[:index]:
            line[other] = "│"
        line[c] = "└"
        rows.append(" " + "".join(line).rstrip("│ ").ljust(c) + "└ " + label
                    if False else " " + "".join(line[:c]) + "└ " + label)
    parts = pattern_parts(pattern)
    words = []
    index = 0
    while index < len(parts):
        piece, meaning = parts[index]
        if index + 1 < len(parts) and parts[index + 1][0] == "\\+":
            words.append("one or more of: %s" % meaning)
            index += 2
            continue
        words.append("at the end of the line" if piece == "$" else
                     "at the start of the line" if piece == "^" else meaning)
        index += 1
    finds = ", ".join(words)
    where = _range_words(rng)
    what = ('replace it with %s' % _q(replacement)) if replacement else "delete it"
    how_many = "every match on each line" if "g" in flags else "the first match on each line"
    english = "In plain English: %s, find %s and %s (%s)." % (where, finds, what, how_many)
    return rows, english
