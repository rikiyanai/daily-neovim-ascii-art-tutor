"""Flashcard deck, Leitner spacing and the daily warm-up (memory plan 2026-09-29).

The operator asked for "a flashcard deck", "memory anchors" and "spaced
repetition across sessions" (feedback 13:33), and the chat quiz of 2026-09-29
showed eight misconceptions that lessons alone had not fixed (`3G` read as
"three blocks", `fo` as a whole-file search, `3yyGp` as only "yank three
lines", ...).  This module owns all of it so v2_runtime keeps thin hooks:

* ``share/deck-v2.json`` is authored by hand.  ``build_deck`` attaches the
  lesson ids that use each family; ``validate_deck`` is the generator gate.
* Deck answers are ``deck`` events in the same events-v2.jsonl ledger.
  ``fold`` turns them into ``progress["deck"]``: a Leitner box, a due time and
  a lapse count per item, plus a weak set.  A failed paired question or a
  scheduled remediation makes that lesson's families due again.  Deck events
  never count toward XP, lessons done today or mastery.
* ``run_quiz`` (``--quiz [N]``), ``browse`` (``--deck``), ``record_misses``
  (``--deck-miss``) and ``maybe_warmup`` (before the first lesson of the day)
  are the learner-facing routes.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import random
import re
import shutil
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECK_SOURCE = HERE / "deck-v2.json"

# Plan §3: the quiz misconceptions every deck must keep.
REQUIRED_ITEMS = ("DK.G.01", "DK.F.01", "DK.YP.01", "DK.S.01", "DK.S.02", "DK.S.03",
                  "DK.U.01", "DK.D.01", "DK.D.02")
# Every command family the course uses must have a deck family.  The deck is a
# course-wide reference, rather than a primer-only aid: later modules revisit
# the same grammar with new art and also introduce registers, Visual mode,
# macros, windows and Ex commands.
COVERAGE_MODULES = tuple("M%d" % number for number in range(20))
# These are pure cursor-navigation controls.  They are deliberately the only
# omissions: word motions, counts, operators, display commands and command-line
# forms all carry a learner-facing explanation in the authored source.
COVERAGE_EXEMPT = {"h", "k", "l", "[count]h", "[count]k", "[count]l"}
ITEM_KINDS = ("predict", "decode", "typed_keys")
GRADES = ("again", "hard", "good")
WARMUP_ITEMS = 3
QUIZ_DEFAULT = 5

# Learner-facing text must not carry authoring vocabulary (VD-28, VD-48).
BANNED_LEARNER = re.compile(
    r"\bEx\b|\baddress(?:es)?\b|\bfamily id\b|\bDK\.|\bparser\b|"
    r"\b(?:card|module|curriculum|misconception)\b|\bM\d+(?:\.[A-Z0-9]+)+\b",
    re.IGNORECASE)
TEMPLATE_PHRASES = (
    "makes only its named change", "named defect", "accepts the module's",
    "stated scope stays", "This visible failure occurs", "performs the bounded edit",
    "registration contract", "hidden recipe", "method evidence",
)

_KEYS = None


def keys_module():
    global _KEYS
    if _KEYS is None:
        spec = importlib.util.spec_from_file_location("vim_daily_deck_keys",
                                                      HERE / "v2_keys.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _KEYS = module
    return _KEYS


# --------------------------------------------------------------- build/validate

def build_deck(cards, modules, source=DECK_SOURCE):
    """Load the authored deck and attach, per family, the lessons that use it."""
    deck = json.loads(Path(source).read_text(encoding="utf-8"))
    K = keys_module()
    order = [cid for module in modules for cid in module["card_ids"]]
    card_map = {card["id"]: card for card in cards}
    used = {}
    for cid in order:
        expected = card_map.get(cid, {}).get("expected") or ""
        used[cid] = {family for family, _m in K.families(expected)}
    for family in deck["families"]:
        wanted = set(family.get("parser_families", []))
        family["card_ids"] = [cid for cid in order if used.get(cid, set()) & wanted]
    return deck


def learner_texts(family):
    """(where, text) for every string a learner can read in one family."""
    yield family["id"] + ".family", family.get("family", "")
    for field in ("front", "back", "anchor", "shape"):
        yield "%s.%s" % (family["id"], field), family.get(field, "")
    for item in family.get("items", []):
        yield item["id"] + ".prompt", item.get("prompt", "")
        yield item["id"] + ".misconception", item.get("misconception", "")
        for index, text in enumerate(item.get("choices", [])):
            yield "%s.choice%d" % (item["id"], index), text
        for index, text in enumerate(item.get("why", [])):
            yield "%s.why%d" % (item["id"], index), text
        for index, trap in enumerate(item.get("trap_answers", [])):
            yield "%s.trap%d" % (item["id"], index), trap.get("why", "")


def validate_deck(cur, *, run_typed=True, typed_check=None):
    """Return a list of errors; empty means the deck may ship."""
    errors = []
    deck = cur.get("deck")
    if not isinstance(deck, dict) or deck.get("schema") != "vim-daily/deck@1":
        return ["deck: missing or wrong schema (want vim-daily/deck@1)"]
    families = deck.get("families", [])
    if not families:
        return ["deck: no families"]
    family_ids = [family.get("id") for family in families]
    if len(set(family_ids)) != len(family_ids):
        errors.append("deck: duplicate family ids")
    item_ids = [item.get("id") for family in families for item in family.get("items", [])]
    if len(set(item_ids)) != len(item_ids):
        errors.append("deck: duplicate item ids")
    for required in REQUIRED_ITEMS:
        if required not in item_ids:
            errors.append("deck: required misconception item %s is missing" % required)
    K = keys_module()
    covered = set()
    why_seen = {}
    for family in families:
        fid = family.get("id", "?")
        for field in ("family", "front", "back", "anchor", "shape", "example_keys"):
            if not str(family.get(field, "")).strip():
                errors.append("%s: empty %s" % (fid, field))
        if not family.get("parser_families"):
            errors.append("%s: no parser_families" % fid)
        covered.update(family.get("parser_families", []))
        if not family.get("card_ids"):
            errors.append("%s: no lesson uses %s" % (fid, family.get("parser_families")))
        for other in family.get("contrasts", []):
            if other == fid or other not in family_ids:
                errors.append("%s: contrast %r does not resolve" % (fid, other))
        if not family.get("items"):
            errors.append("%s: family has no items" % fid)
        for item in family.get("items", []):
            iid = item.get("id", "?")
            if not iid.startswith(fid.split(".")[0] + "."):
                errors.append("%s: item id must start with DK." % iid)
            kind = item.get("kind")
            if kind not in ITEM_KINDS:
                errors.append("%s: kind %r" % (iid, kind))
            if not str(item.get("misconception", "")).strip():
                errors.append("%s: no named misconception" % iid)
            if not item.get("keys"):
                errors.append("%s: no keys to draw" % iid)
            for row in item.get("rows", []):
                if len(row) > 60:
                    errors.append("%s: art row wider than 60 cells" % iid)
            if kind in ("predict", "decode"):
                choices, why = item.get("choices", []), item.get("why", [])
                if not 3 <= len(choices) <= 4:
                    errors.append("%s: needs 3-4 choices" % iid)
                if len(set(choices)) != len(choices):
                    errors.append("%s: duplicate choices" % iid)
                if not isinstance(item.get("answer"), int) or not \
                        0 <= item["answer"] < len(choices):
                    errors.append("%s: answer index out of range" % iid)
                if len(why) != len(choices) or not all(str(w).strip() for w in why):
                    errors.append("%s: every choice needs its own why" % iid)
                for text in why:
                    if text in why_seen:
                        errors.append("%s: why reused verbatim from %s" % (iid, why_seen[text]))
                    why_seen.setdefault(text, iid)
            elif kind == "typed_keys":
                contract = item.get("contract", {})
                if not contract.get("initial_lines") or not contract.get("target_lines"):
                    errors.append("%s: typed contract needs initial and target lines" % iid)
                if not item.get("sample_answer"):
                    errors.append("%s: typed item needs a sample answer" % iid)
                traps = item.get("trap_answers", [])
                if not traps or not all(t.get("keys") and t.get("why") for t in traps):
                    errors.append("%s: typed item needs trap answers with a why" % iid)
                if run_typed and typed_check and item.get("sample_answer"):
                    setup = contract.get("setup_keys", "")
                    right, _e, _m = typed_check(contract, setup + item["sample_answer"])
                    if not right:
                        errors.append("%s: sample answer does not reach the target" % iid)
                    for trap in traps:
                        wrong, _e, _m = typed_check(contract, setup + trap["keys"])
                        if wrong:
                            errors.append("%s: trap %r reaches the target" % (iid, trap["keys"]))
        for where, text in learner_texts(family):
            match = BANNED_LEARNER.search(text)
            if match:
                errors.append("%s: internal word %r in learner text" % (where, match.group(0)))
            if "…" in text:
                errors.append("%s: ellipsis in learner text" % where)
            for phrase in TEMPLATE_PHRASES:
                if phrase.casefold() in text.casefold():
                    errors.append("%s: template phrase %r" % (where, phrase))
    cards = {card["id"]: card for card in cur.get("cards", [])}
    for module in cur.get("modules", []):
        if module["id"] not in COVERAGE_MODULES:
            continue
        for cid in module["card_ids"]:
            for fam, _m in K.families(cards.get(cid, {}).get("expected") or ""):
                if fam not in covered and fam not in COVERAGE_EXEMPT:
                    errors.append("deck: %s (used by %s) has no deck family" % (fam, cid))
                    covered.add(fam)
    return errors


# ------------------------------------------------------------------- schedule

def _parse(iso):
    try:
        return dt.datetime.fromisoformat(iso)
    except (TypeError, ValueError):
        return None


def item_index(cur):
    """item id -> (family, item)."""
    out = {}
    for family in cur.get("deck", {}).get("families", []):
        for item in family.get("items", []):
            out[item["id"]] = (family, item)
    return out


def family_map(cur):
    return {family["id"]: family for family in cur.get("deck", {}).get("families", [])}


def schedule(cur, state, grade, now):
    """Leitner step reusing review_intervals_hours; returns the new state."""
    intervals = cur["review_intervals_hours"]
    box = int((state or {}).get("box", 0))
    lapses = int((state or {}).get("lapses", 0))
    if grade == "again":
        box, lapses, due = 0, lapses + 1, now
    elif grade == "hard":
        box = max(1, min(box, len(intervals)))
        due = now + dt.timedelta(hours=intervals[box - 1])
    else:
        box = min(box + 1, len(intervals))
        due = now + dt.timedelta(hours=intervals[box - 1])
    return {"box": box, "next_due": due.isoformat(), "lapses": lapses}


def fold(cur, events):
    """Project deck events (and lesson failures) into progress["deck"]."""
    index = item_index(cur)
    by_card = {}
    for family in cur.get("deck", {}).get("families", []):
        for cid in family.get("card_ids", []):
            by_card.setdefault(cid, []).append(family)
    items = {}
    for event in events:
        kind = event.get("type")
        if kind == "deck" and event.get("item_id") in index:
            state = items.setdefault(event["item_id"], {"box": 0, "lapses": 0, "seen": 0})
            grade = event.get("grade")
            if grade == "again":
                state["lapses"] += 1
            state["box"] = int(event.get("box", 0))
            state["next_due"] = event.get("next_due")
            state["last_grade"] = grade
            state["seen"] += 1
            state.pop("resurfaced", None)
            continue
        failed = ((kind in ("question", "review") and event.get("result") == "fail")
                  or kind == "remediation_scheduled")
        if not failed:
            continue
        card_id = event.get("card_id") or event.get("review_key")
        for family in by_card.get(card_id, []):
            for item in family.get("items", []):
                state = items.setdefault(item["id"], {"box": 0, "lapses": 0, "seen": 0})
                state["next_due"] = event.get("at")
                state["resurfaced"] = True
    weak = sorted(iid for iid, state in items.items()
                  if state.get("last_grade") == "again"
                  or (state["lapses"] >= 2 and state["box"] <= 1))
    weak_families = sorted({index[iid][0]["id"] for iid in weak})
    return {"items": items, "weak": weak, "weak_families": weak_families}


def _is_due(state, now):
    when = _parse((state or {}).get("next_due"))
    return when is not None and when <= now


def eligible_families(cur, progress):
    """Families met in a passed lesson, plus their contrast partners."""
    passed = set(progress.get("passed_cards", []))
    families = family_map(cur)
    met = {fid for fid, family in families.items() if passed & set(family.get("card_ids", []))}
    out = set(met)
    for fid in met:
        out.update(families[fid].get("contrasts", []))
    return out


def pick(cur, progress, n, *, now, only_families=None):
    """Weak first, then due, then never-seen items of eligible families."""
    deck_state = progress.get("deck", {"items": {}, "weak": []})
    states = deck_state.get("items", {})
    index = item_index(cur)
    allowed = (lambda fid: True) if only_families is None else \
        (lambda fid: fid in only_families)
    chosen = []

    def take(iid):
        if iid in index and iid not in chosen and allowed(index[iid][0]["id"]) \
                and len(chosen) < n:
            chosen.append(iid)

    for iid in sorted(deck_state.get("weak", []),
                      key=lambda i: (-states.get(i, {}).get("lapses", 0), i)):
        take(iid)
    due = [(states[iid].get("next_due"), iid) for iid in states if _is_due(states[iid], now)]
    for _when, iid in sorted(due):
        take(iid)
    eligible = eligible_families(cur, progress)
    for family in cur.get("deck", {}).get("families", []):
        if family["id"] not in eligible:
            continue
        for item in family.get("items", []):
            if item["id"] not in states:
                take(item["id"])
    return chosen


def warmup_families(cur, card_id):
    families = family_map(cur)
    out = set()
    for fid, family in families.items():
        if card_id in family.get("card_ids", []):
            out.add(fid)
            out.update(family.get("contrasts", []))
    return out


# ------------------------------------------------------------------- rendering

def _width():
    return max(40, min(78, shutil.get_terminal_size((80, 24)).columns - 2))


def _rows():
    return shutil.get_terminal_size((80, 24)).lines


def wrap(text, width, indent="  ", hang="    "):
    return textwrap.wrap(text, width=width, initial_indent=indent,
                         subsequent_indent=hang, break_on_hyphens=False) or [indent]


def _letters(item):
    return "abcd"[:len(item.get("choices", []))]


def item_lines(family, item, header, width, order=None):
    """The question screen for one item, already wrapped to width."""
    lines = wrap(header, width, "", "  ")
    lines += wrap(item["prompt"], width, "  ", "  ")
    rows = item.get("rows") or []
    if rows:
        lines.append("")
        cursor_line = (item.get("cursor") or [None])[0]
        for number, row in enumerate(rows, 1):
            mark = "▶" if number == cursor_line else " "
            lines.append("  %s%2d │%s" % (mark, number, row))
    if item["kind"] == "typed_keys":
        contract = item["contract"]
        before, after = contract["initial_lines"], contract["target_lines"]
        lines.append("")
        lines.append("  START%sTARGET" % (" " * 22))
        for index in range(max(len(before), len(after))):
            left = before[index] if index < len(before) else ""
            right = after[index] if index < len(after) else ""
            lines.append("  │%-25s │%s" % (left, right))
        lines.append("  The cursor starts on line 1, column 1.")
    else:
        lines.append("")
        order = order or list(range(len(item["choices"])))
        for shown, original in enumerate(order):
            lines += wrap("%s) %s" % ("abcd"[shown], item["choices"][original]), width,
                          "  ", "     ")
    return lines


def anatomy_lines(keys, width):
    K = keys_module()
    rows = K.anatomy(keys, width)
    return rows or []


def result_lines(family, item, right, why, width, budget, *, answer_line=None,
                 right_line=None):
    """Result page: essentials always; the diagram only when it fits unclipped."""
    head = ["✓ RIGHT" if right else "✗ NOT QUITE"]
    if answer_line:
        head += wrap(answer_line, width, "  ", "    ")
    if right_line:
        head += wrap(right_line, width, "  ", "    ")
    head += wrap("WHY: " + why, width, "  ", "    ")
    if not right:
        head += wrap("COMMON MIX-UP: " + item["misconception"], width, "  ", "    ")
    anchor = wrap("REMEMBER: " + family["anchor"], width, "  ", "    ")
    shape = wrap("SHAPE: " + family["shape"], width, "  ", "    ")
    diagram = anatomy_lines(item["keys"], width) if not right else []
    lines = list(head)
    for block in (anchor, [""] + diagram if diagram else [], shape if not diagram else []):
        if block and len(lines) + len(block) <= budget:
            lines += block
    return lines


def family_lines(family, width, state_line=None):
    lines = ["%s · %s" % (family["family"], family["anchor"])][:1]
    lines = wrap(lines[0], width, "", "  ")
    lines += wrap("Q: " + family["front"], width, "  ", "     ")
    lines += wrap("A: " + family["back"], width, "  ", "     ")
    lines += wrap("SHAPE: " + family["shape"], width, "  ", "     ")
    if state_line:
        lines += wrap(state_line, width, "  ", "     ")
    return lines


# ------------------------------------------------------------------ recording

def record(rt, cfg, cur, progress, item_id, grade, source, now=None):
    """Append one deck event; the projection folds it later."""
    now = now or rt._now()
    index = item_index(cur)
    family, _item = index[item_id]
    state = progress.get("deck", {}).get("items", {}).get(item_id, {})
    new = schedule(cur, state, grade, now)
    row = rt.append_event(cfg, {
        "type": "deck", "item_id": item_id, "family_id": family["id"], "grade": grade,
        "result": "wrong" if grade == "again" else "right", "source": source,
        "box": new["box"], "next_due": new["next_due"],
    })
    progress.setdefault("deck", {"items": {}, "weak": [], "weak_families": []})
    items = progress["deck"].setdefault("items", {})
    merged = dict(items.get(item_id, {"lapses": 0, "seen": 0}))
    merged.update(new)
    merged["last_grade"] = grade
    merged["seen"] = merged.get("seen", 0) + 1
    items[item_id] = merged
    return row


def record_misses(rt, cfg, cur, progress, ids):
    """`--deck-miss ITEM…`: an outside miss (a chat quiz) makes items weak now."""
    index = item_index(cur)
    families = family_map(cur)
    wanted = []
    for value in ids:
        if value in index:
            wanted.append(value)
        elif value in families:
            wanted += [item["id"] for item in families[value]["items"]]
        else:
            print("no deck item or family: %s" % value)
            return 1
    if not wanted:
        print("usage: vim-daily-gate --deck-miss ITEM [ITEM ...]  (e.g. DK.G.01)")
        return 1
    for item_id in wanted:
        record(rt, cfg, cur, progress, item_id, "again", "external")
        print("marked for review: %s · %s" % (item_id, index[item_id][0]["family"]))
    return 0


# ---------------------------------------------------------------- interaction

class _Skip(Exception):
    pass


class _Quit(Exception):
    pass


def _input(input_fn, prompt):
    try:
        return input_fn(prompt)
    except (EOFError, KeyboardInterrupt, StopIteration):
        print()
        raise _Quit()


def _order(item):
    order = list(range(len(item.get("choices", []))))
    if os.environ.get("VIM_DAILY_TEST_ORDERED_CHOICES") != "1":
        random.shuffle(order)
    return order


def _clear():
    import sys
    if sys.stdout.isatty():
        print("\033[2J\033[H", end="")


def _feedback(rt, input_fn, item, screen):
    rt.note_feedback_context(question_id=item["id"], screen=screen,
                             question_prompt=item["prompt"][:160])
    rt.collect_feedback(input_fn, screen=screen)


def ask_item(rt, cfg, cur, progress, item_id, header, *, source, input_fn=input,
             skip_word=None):
    """Ask one item, show why, record the grade; return the grade."""
    family, item = item_index(cur)[item_id]
    width = _width()
    order = _order(item) if item["kind"] != "typed_keys" else None
    _clear()
    for line in item_lines(family, item, header, width, order):
        print(line)
    extra = (" · s %s" % skip_word) if skip_word else ""
    if item["kind"] == "typed_keys":
        prompt = "  keys (<Esc>, <CR> as written) · f feedback%s: " % extra
    else:
        prompt = "  answer (a-%s) · f feedback%s: " % (_letters(item)[-1], extra)
    rt.note_feedback_context(question_id=item_id, screen=source, answer=None,
                             answer_correct=None, card_id=None)
    while True:
        raw = _input(input_fn, prompt)
        answer = raw.rstrip("\r\n") if item["kind"] == "typed_keys" else raw.strip().lower()
        if answer.strip() == "f":
            _feedback(rt, input_fn, item, source)
            continue
        if skip_word and answer.strip() == "s":
            raise _Skip()
        if item["kind"] == "typed_keys" and answer.strip():
            break
        if item["kind"] != "typed_keys" and answer in _letters(item) and len(answer) == 1:
            break
        print("  that did not count; answer %s" % (
            "with Vim keys" if item["kind"] == "typed_keys" else
            "with " + ", ".join(_letters(item))))
    budget = _rows() - 2
    if item["kind"] == "typed_keys":
        contract = item["contract"]
        right, _evidence, _message = rt._safe_typed_effect(
            contract, contract.get("setup_keys", "") + answer)
        trap = next((t for t in item["trap_answers"] if t["keys"] == answer), None)
        why = ("Your keys reach TARGET." if right else
               trap["why"] if trap else "The result does not match TARGET yet.")
        lines = result_lines(family, item, right, why, width, budget,
                             answer_line="YOUR KEYS: %s" % answer,
                             right_line=None if right else
                             "ONE WAY: %s" % item["sample_answer"])
    else:
        chosen = order[_letters(item).index(answer)]
        right = chosen == item["answer"]
        lines = result_lines(
            family, item, right, item["why"][chosen], width, budget,
            answer_line=None if right else "YOUR ANSWER: %s" % item["choices"][chosen],
            right_line=None if right else "RIGHT ANSWER: %s" % item["choices"][item["answer"]])
    _clear()
    for line in lines:
        if line.startswith("✓"):
            line = rt._paint(line, "ok")
        elif line.startswith("✗"):
            line = rt._paint(line, "fail")
        elif item["kind"] == "typed_keys" and line.strip().startswith("YOUR KEYS:"):
            shown = line.split(":", 1)[1].lstrip()
            good = item["sample_answer"]
            line = line[:line.index(":") + 1] + " " + rt._partial_key_colours(
                "`" + shown + "`", "`" + good + "`")
        print(line)
    rt.note_feedback_context(question_id=item_id, answer_correct=bool(right),
                             screen=source + "-result")
    grade = "good" if right else "again"
    hold = ("  Enter = next · h = that was hard · f feedback: " if right
            else "  Enter = next · f feedback: ")
    while True:
        choice = _input(input_fn, hold).strip().lower()
        if choice == "f":
            _feedback(rt, input_fn, item, source + "-result")
            continue
        if right and choice == "h":
            grade = "hard"
        break
    record(rt, cfg, cur, progress, item_id, grade, source)
    return grade


def run_quiz(rt, cfg, cur, progress, count=QUIZ_DEFAULT, *, input_fn=input):
    """`--quiz [N]`: a short drill, weak items first, then due, then new."""
    ids = pick(cur, progress, count, now=rt._now())
    if not ids:
        print("Nothing to drill yet: the deck opens as you pass lessons.")
        return 0
    tally = {"good": 0, "hard": 0, "again": 0}
    try:
        for number, item_id in enumerate(ids, 1):
            family = item_index(cur)[item_id][0]
            header = "DECK QUIZ %d/%d · %s" % (number, len(ids), family["family"])
            grade = ask_item(rt, cfg, cur, progress, item_id, header, source="quiz",
                             input_fn=input_fn, skip_word="stops")
            tally[grade] += 1
    except (_Skip, _Quit):
        pass
    _clear()
    print("DECK QUIZ DONE · %d right · %d hard · %d to see again soon" % (
        tally["good"], tally["hard"], tally["again"]))
    print("Deck answers never change lesson progress or XP.")
    return 0


def warmup_due(cur, events, now):
    """True before the first lesson of the day, once per day."""
    today = now.date().isoformat()
    for event in events:
        if not str(event.get("at", "")).startswith(today):
            continue
        if event.get("type") == "deck_warmup":
            return False
        if event.get("type") in ("card", "review") and event.get("result") == "pass":
            return False
    return True


def maybe_warmup(rt, cfg, cur, progress, events, card_id, *, input_fn=input):
    """Up to three items from the upcoming lesson's families; s skips."""
    if os.environ.get("VIM_DAILY_NO_WARMUP") == "1" or not card_id:
        return False
    now = rt._now()
    if not warmup_due(cur, events, now):
        return False
    nearby = warmup_families(cur, card_id)
    only = nearby & (eligible_families(cur, progress)
                     | set(progress.get("deck", {}).get("weak_families", [])))
    ids = pick(cur, progress, WARMUP_ITEMS, now=now, only_families=only)
    if not ids:
        return False
    outcome = "done"
    try:
        for number, item_id in enumerate(ids, 1):
            family = item_index(cur)[item_id][0]
            header = "WARM-UP %d/%d before today's lesson · %s" % (
                number, len(ids), family["family"])
            ask_item(rt, cfg, cur, progress, item_id, header, source="warmup",
                     input_fn=input_fn, skip_word="skips the warm-up")
    except _Skip:
        outcome = "skipped"
    except _Quit:
        outcome = "skipped"
    rt.append_event(cfg, {"type": "deck_warmup", "result": outcome, "items": ids})
    _clear()
    return True


def browse(cur, progress, wanted=None):
    """`--deck [FAMILY]`: the authored deck, met families first."""
    width = _width()
    states = progress.get("deck", {}).get("items", {})
    weak = set(progress.get("deck", {}).get("weak_families", []))
    eligible = eligible_families(cur, progress)
    families = cur.get("deck", {}).get("families", [])
    if wanted:
        match = [f for f in families if f["id"] == wanted or f["family"] == wanted
                 or wanted in f.get("parser_families", [])]
        if not match:
            print("no deck family: %s" % wanted)
            return 1
        family = match[0]
        for line in family_lines(family, width):
            print(line)
        rows = anatomy_lines(family["example_keys"], width)
        if rows:
            print("")
            print("HOW TO READ %s" % family["example_keys"])
            for line in rows:
                print(line)
        return 0
    met = [f for f in families if f["id"] in eligible]
    rest = [f for f in families if f["id"] not in eligible]
    now = dt.datetime.now().astimezone()
    print("YOUR DECK · %d of %d families open · ! = missed lately" % (len(met), len(families)))
    print("vim-daily-gate --quiz drills them · --deck NAME shows one with its diagram")
    for family in met:
        items = family["items"]
        known = sum(1 for i in items if states.get(i["id"], {}).get("box", 0) >= 3)
        due = sum(1 for i in items if _is_due(states.get(i["id"]), now)
                  or i["id"] not in states)
        mark = "!" if family["id"] in weak else " "
        print("")
        lines = family_lines(family, width - 2, "%d item%s · %d known well · %d to drill now" % (
            len(items), "" if len(items) == 1 else "s", known, due))
        print(mark + " " + lines[0])
        for line in lines[1:]:
            print("  " + line)
    if rest:
        print("")
        for line in wrap("OPENS LATER: " + ", ".join(f["family"] for f in rest), width,
                         "", "  "):
            print(line)
    return 0


def remember_lines(card, cur, weak_families, wrap_fn):
    """A REMEMBER block for families the learner missed in the deck lately."""
    if not weak_families:
        return []
    lines = []
    for family in cur.get("deck", {}).get("families", []):
        if family["id"] in weak_families and card.get("id") in family.get("card_ids", []):
            lines += wrap_fn("REMEMBER (missed in your deck) · %s · %s" % (
                family["family"], family["anchor"]), "  ")
            lines += wrap_fn("shape: " + family["shape"], "     ")
    return lines
