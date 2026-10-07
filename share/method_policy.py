"""Source-checked taught-command paths for curriculum method grading.

The curriculum's ``exact_any_of`` values are worked examples.  They usually
contain row/column setup, landmarks, authored text, and the command being
practised.  Treating the whole example as one required transcript makes a
correct attempt fail as soon as the learner reorders an exploratory key or
uses a different route to the same target.

This module is deliberately a small, data-only policy boundary.  A value in
``_CARD_PATHS`` is a list of alternative paths; each path is a list of
independent, complete key-string commands whose presence is required.  The
runtime may check those commands in any order and may ignore other captured
keys.  ``[]`` means that this card is not source-checked here and the caller
must use its legacy/fallback policy.

The table is keyed by card id instead of broad deck aliases.  Hidden/review
cards therefore get their own audited entry, and a new card cannot silently
inherit a method requirement from a similarly named grammar family.
"""

from __future__ import annotations

from typing import Any
from functools import lru_cache
import json
from pathlib import Path

try:
    import v2_keys as K
except ImportError:  # Installed gate does not put share/ on sys.path.
    import importlib.util
    _spec = importlib.util.spec_from_file_location(
        "vim_daily_policy_keys", Path(__file__).with_name("v2_keys.py"))
    K = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(K)


# Each value is ``(alternative_path, ...)``.  A path is a tuple of independent
# key-string commands.  Positioning is omitted unless its count names the
# taught scope (for example 10G); counts on operators/motions are retained.
_CARD_PATHS: dict[str, tuple[tuple[str, ...], ...]] = {
    # M0 — fireworks radial loop.
    "M0.L0": (("0",),),
    "M0.F0": (("f*",),),
    "M0.01": (("f*", "ro"),),
    "M0.06": (("f*", "rO", ":s/-/=/g<CR>"),),

    # M11 — fixed-width redraw, whitespace, and undo-tree retrievals.
    "M11.01": (("f_", "R"),),
    "M11.WS": ((
        ":set list<CR>", ":set cursorcolumn<CR>",
        ":set colorcolumn=11<CR>", ":%s/\\s\\+$//e<CR>",
    ),),
    "M11.LS": (
        (":set list<CR>", "x"),
        (":set list<CR>", ":%s/\\s\\+$//e<CR>"),
        (":set list<CR>", ":s/\\s\\+$//e<CR>"),
    ),
    "M11.CUC": ((":set cursorcolumn<CR>", "x"),),
    "M11.CC": ((":set colorcolumn=8<CR>", "x"),),
    "M11.TR": ((":%s/\\s\\+$//e<CR>",),),
    "M11.BR": (("u",),),
    "M11.GM": (("g-",),),
    "M11.GP": (("g+",),),
    "M11.ER": ((":earlier 1<CR>",),),
    "M11.UB": (("u", "r,"),),
    "M11.UG": (("g-", "g+"),),
    "M11.UE": ((":earlier 1<CR>",),),
    "M11.UT": (("g-", "g+"),),
    "M11.04": (("f=", "R", "u", "<C-r>"),),
    "M11.WSH": ((
        ":set list<CR>", ":set cursorcolumn<CR>",
        ":set colorcolumn=7<CR>", ":%s/\\s\\+$//e<CR>",
    ),),
    "M11.UTH": (("g-", "g+"),),
    "M11.06": (("fO", "R"),),
    "M11.08": ((":set virtualedit=all<CR>", "12|", "i"),),

    # M1/M19 — replacement and virtual replacement.
    "M1.06": (("f,", "r:"),),
    "M19.01": (("f?", "gR"),),
    "M19.VRH": (("f-", "gR"),),
    "M19.06": (("6dd",),),
    "M19.08": ((":1,6t$<CR>", "f-", "gR"),),

    # M2 — word deletion.
    "M2.DWH": (("dw",),),
    "M2.DEH": (("de",),),
    "M2.06": (("f=", "rO"),),
    "M2.D2WH": (("d2W",),),

    # M12 — character-find, yank/put, and visual reselect.
    "M12.01": (("t:", "r!"),),
    "M12.02": (("3yy", "p", "T:", "r!"),),
    "M12.04": (("3yy", "p", "f:", ";", "r!"),),
    "M12.JHH": (("<C-v>", "gv", "gvr:"),),
    "M12.06": (("t•", "r-", "T•"),),
    "M12.08": ((":1,3t$<CR>", "t!", "r:", "T:", "r!"),),

    # M14 — named registers, paragraph operations, and put-before.
    "M14.01": (("f*", '"ayl', "fo", "R<C-r>a<Esc>"),),
    "M14.02": (("yap", "p"),),
    "M14.DAP": (("dap",),),
    "M14.04": (("f+", '"ayl', "f*", "R<C-r>a<Esc>"),),
    "M14.DAPH": (("dap",),),
    "M14.PH": (("}", "P"),),
    "M14.06": (("fO", '"ayl', "fo", "R<C-r>a<Esc>"),),
    "M14.08": (("f*", '"byl', "}", "f+", "R<C-r>b<Esc>"),),

    # M10/M5 — unfamiliar replacement and search-landmark retrievals.
    "M10.06": (("f?", "rヽ"),),
    "M5.06": (("f|", "r "),),
    "M5.S6C": (("f/", "r "),),

    # M15 — shiftwidth, blocks, append, and macro replay.
    "M15.01": ((":set shiftwidth=1<CR>", ">>"),),
    "M15.02": (("3yy", "p"),),
    "M15.ZP": (("<C-v>", "zy", "zp"),),
    "M15.04": ((
        ":set shiftwidth=1<CR>", ">>", ":4s/:/./g<CR>",
    ),),
    "M15.APPH": (("a",),),
    "M15.APPAH": (("A",),),
    "M15.ZPH": (("<C-v>", "zy", "zp"),),
    "M15.BAH": (("<C-v>A",),),
    "M15.06": ((":set shiftwidth=1<CR>", ">>"),),
    "M15.08": ((":1,3t$<CR>", "qq", "f:", "r.", "3@q"),),

    # M16 — numeric frame labels.
    "M16.01": (("f0", "<C-a>"),),
    "M16.02": ((":read %<CR>", "f1", "<C-a>"),),
    "M16.04": ((":1,5t$<CR>", "f1", "2<C-a>"),),
    "M16.INCH": (("f0", "2<C-a>"),),
    "M16.06": (("f1", "<C-a>"),),
    "M16.08": ((":1,5t$<CR>", "f2", "2<C-a>"),),

    # M3 — glyph inspection, text objects, marks, registers, and Visual line.
    "M3.GA": (("ga",),),
    "M3.CWH": (("cw",),),
    "M3.CAH": (("ca(",),),
    "M3.04": (("ci(",),),
    "M3.GAH": (("ga",),),
    "M3.Y0H": (("\"0p",),),
    "M3.MARKH": (("ma", "'a"),),
    "M3.VDH": (("Vd",),),
    "M3.06": (("V\"ay", '\"ap', "rO"),),
    "M3.08": (("r<C-k>.M",),),

    # M4 — onion-skin windows, block operations, and diff workflows.
    "M4.WIN": ((":vsplit<CR>", "<C-w>p", ":q<CR>"),),
    "M4.REF": ((":vnew<CR>", ":read #<CR>", ":bwipeout!<CR>"),),
    "M4.DT": ((":diffthis<CR>", ":diffoff!<CR>"),),
    "M4.SIL": ((":silent 0read #<CR>",),),
    "M4.TRIM": (("dd",),),
    "M4.SCB": ((":set scrollbind<CR>",),),
    "M4.BI": (("<C-v>I",),),
    "M4.BC": (("<C-v>c",),),
    "M4.DIFF": ((
        ":vnew<CR>", ":silent 0read #<CR>", ":diffthis<CR>",
        ":set scrollbind<CR>", "<C-w>p", ":diffoff!<CR>",
        ":bwipeout!<CR>",
    ),),
    "M4.GV": (("<C-v>c", "gvr!"),),
    "M4.BDH": (("<C-v>d",),),
    "M4.BIH": (("<C-v>I",),),
    "M4.BCH": (("<C-v>c",),),
    "M4.DIFFH": ((
        ":vnew<CR>", ":silent 0read #<CR>", ":diffthis<CR>",
        ":set scrollbind<CR>", "<C-w>p", ":diffoff!<CR>",
        ":bwipeout!<CR>",
    ),),
    "M4.GVH": (("<C-v>c", "gvr:"),),
    "M4.06": ((":1,3t3<CR>", "r'"),),
    "M4.08": (("3dd",),),

    # M17 — search repeat, named scope, global Normal, and macro.
    "M17.01": (("/x<CR>", "ro", "n", "."),),
    "M17.02": (("3yy", "p"),),
    "M17.04": (("10G", "f^", "r-", "f_", "r-"),),
    "M17.GNH": ((":g/:/normal! 0f.r'<CR>",),),
    "M17.06": (("/\\*<CR>", "r^", "n", "."),),
    "M17.08": (("/\\*<CR>", "qq", "r+", "n", "3@q"),),

    # M13 — WORD/word boundaries and last-nonblank.
    "M13.01": (("W", "r!"),),
    "M13.02": (("3yy", "p", "W", "r.", "r!"),),
    "M13.W": (("w",),),
    "M13.GU": (("g_",),),
    "M13.04": (("3yy", "p", "E", "2W", "2B", "r!", "r."),),
    "M13.WH": (("w",),),
    "M13.GH": (("g_",),),
    "M13.06": (("3W", "B", "r!"),),
    "M13.08": ((":1,3t$<CR>", "W", "r.", "B", "r!"),),

    # M7 — case toggles and Visual characterwise repeat.
    "M7.TCH": (("~",),),
    "M7.04": (("f-", "vr=", "."),),
    "M7.GTCH": (("g~w",),),
    "M7.06": (("fo", "rO", "."),),

    # M6 — joins, line scopes, Ex move, and adjacent swap.
    "M6.JH": (("J",),),
    "M6.04": (("6G", "D"),),
    "M6.06": ((":1,5m$<CR>",),),
    "M6.DDPH": (("dd", "p"),),

    # M18/M8/M9 — change-to-end, open-line, and capstone routes.
    "M18.01": (("C",),),
    "M18.02": (("4yy", "p"),),
    "M18.04": (("C",),),
    "M18.EXPRH": ((":5s/0/\\=getline(1)[-1:]/<CR>",),),
    "M18.06": (("g_", "r."),),
    "M18.08": ((":5,8t$<CR>", ":1,4t$<CR>"),),
    "M8.OH": (("O",),),
    "M8.PADH": (("ft", "O", "."),),
    "M8.04": (("o",),),
    "M8.06": (("f>", "r|"),),
    "M9.06": (("C",),),
}

# These authored variants deliberately change the operation, not merely a
# glyph operand. They need their own minimal source-checked path. The source
# bank/index identifies the version; no recipe-order matching is performed.
_CHANGED_PATHS = {
    ("M11.06", "variants", 1): (("r¯",),),
    ("M1.06", "variants", 1): (("r:",),),
    ("M19.06", "variants", 1): ((":1,5d<CR>",),),
    ("M4.06", "variants", 1): ((":1,3t3<CR>", "R"),),
    ("M17.06", "variants", 1): (("/==<CR>", "R", "n", "."),),
    ("M17.08", "review_variants", 0): (("/!<CR>", "qq", "r:", "n", "3@q"),),
    ("M17.08", "review_variants", 1): (("/o<CR>", "qq", "r*", "n", "3@q"),),
    ("M13.06", "variants", 1): (("E", "2E", "r!"),),
    ("M7.04", "review_variants", 0): (("vr=", "."),),
    ("M7.04", "review_variants", 1): (("vr~", "."),),
    ("M7.06", "variants", 1): (("r-", "."),),
    ("M18.06", "variants", 1): (("C",),),
    ("M8.06", "variants", 1): (("r>",),),
    ("M9.06", "variants", 1): (("r ", "x", "R"),),
}


@lru_cache(maxsize=1)
def _source_cards() -> dict[str, dict[str, Any]]:
    return {card["id"]: card for card in json.loads(
        (Path(__file__).parent / "curriculum-v2.json").read_text(encoding="utf-8"))["cards"]}


def _selected_command(command: str, primary: str, selected: str) -> str:
    """Adapt only an audited command's literal operand to changed source art.

    Match the exact parser family and occurrence in the primary recipe. Never
    use broad deck-family aliases, and never require the surrounding recipe.
    Replace-mode payloads and macro bodies stay outside primitive templates.
    """
    if primary == selected:
        return command
    before = K.explain(primary)
    after = K.explain(selected)
    out = []
    for part, _meaning, family in K.explain(command):
        candidates = [(i, chunk) for i, (chunk, _m, fam) in enumerate(before)
                      if fam == family and (chunk == part or chunk.startswith(part))]
        if not candidates:
            out.append(part)
            continue
        index, original = candidates[0]
        occurrence = sum(fam == family for _c, _m, fam in before[:index])
        matches = [chunk for chunk, _m, fam in after if fam == family]
        replacement = matches[occurrence] if occurrence < len(matches) else part
        if original != part:
            # 'R' means enter the mode, not reproduce an authored payload.
            # 'qq' means start recording, not replay the whole macro recipe.
            replacement = "".join(K.tokens(replacement)[:len(K.tokens(part))])
        out.append(replacement)
    return "".join(out)


def taught_paths(card: dict[str, Any], rule: dict[str, Any] | None = None) -> list[list[str]]:
    """Return explicit alternative taught-command paths for ``card``.

    The result is a list of alternatives.  Each alternative is a list of
    complete command strings, and all strings in one alternative must be
    observed (in any order) for method credit.  An empty list intentionally
    means "no policy here"; callers should then use their documented fallback
    atomizer.  No grammar-family alias is used as an implicit fallback.

    ``rule`` is accepted to make the call site explicit and to support safe
    handling of an atomic ``all_of`` rule for a future card.  We do not
    atomize an unknown ``exact_any_of`` recipe because that would silently
    turn incidental recipe keys into new lesson requirements.
    """
    if rule and rule.get("all_of"):
        return [list(rule["all_of"])]
    card_id = str(card.get("id", ""))
    if card_id not in _CARD_PATHS:
        card_id = str(card.get("review_source_card_id", ""))
    paths = _CARD_PATHS.get(card_id)
    if paths is None:
        return []
    source = _source_cards().get(card_id, {})
    primary = source.get("expected", "")
    selected = card.get("expected", primary)
    known = {primary} | {variant.get("expected", "")
                        for bank in ("variants", "review_variants")
                        for variant in source.get(bank, [])}
    if selected not in known:
        # A synthetic/new version with an old id is not an audited source.
        return []
    for bank in ("variants", "review_variants"):
        for index, variant in enumerate(source.get(bank, [])):
            if variant.get("expected") == selected:
                changed = _CHANGED_PATHS.get((card_id, bank, index))
                if changed is not None:
                    return [list(path) for path in changed]
    return [[_selected_command(command, primary, selected) for command in path]
            for path in paths]


def explicit_card_ids() -> frozenset[str]:
    """Return the ids covered by the source-checked table."""
    return frozenset(_CARD_PATHS)


__all__ = ["explicit_card_ids", "taught_paths"]
