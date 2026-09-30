#!/usr/bin/env python3
"""Interactive learner dashboard (VD-58): a Textual app over the v2 projection.

Launched by `vim-daily-gate --dashboard` (and `--tree` in a terminal) through
v2_runtime.open_dashboard, which runs this file with the managed venv python
from install.sh. Progress comes only from v2_runtime (load_curriculum,
read_events, project, _level, _legacy_streak, learned_deck, _revisit_rows);
this file adds presentation and the dashboard-only badges in dashboard_theme.

Keys: j/k move · za/zo/zc/zR/zM fold · Enter open · / search · n/N next match ·
f feedback · ? help · q quit.

Exit code 3 (v2_runtime.DASHBOARD_UNAVAILABLE) = Textual is not importable;
the runtime then prints the static tree instead.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import io
import os
import sys
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import dashboard_theme as TH  # noqa: E402
import v2_runtime as V2  # noqa: E402

UNAVAILABLE = 3


def colour_enabled(env=None):
    env = os.environ if env is None else env
    return "NO_COLOR" not in env and env.get("TERM", "") not in ("", "dumb")


def animations_enabled(env=None):
    env = os.environ if env is None else env
    return colour_enabled(env) and env.get("VIM_DAILY_ANIM", "").lower() != "off"


# --------------------------------------------------------------------- model
# Pure data, no Textual: the tests and the app share it.

def _card_label(card):
    return card.get("title", card["id"]).split(" · ", 1)[-1]


def _rule_values(model):
    """Evaluator inputs for dashboard_theme.BADGES `rule` names."""
    cur, progress, events = model["cur"], model["progress"], model["events"]
    passed = set(progress["passed_cards"])
    cards = {card["id"]: card for card in cur["cards"]}
    K = V2._keys_module()
    ranged = 0
    for cid in passed:
        expected = cards.get(cid, {}).get("expected") or ""
        if expected and any("[range]" in family for family, _m in K.families(expected)):
            ranged += 1
    scheduled, rescued = {}, set()
    first_try = set()
    per_day = {}
    for event in events:
        kind, result, cid = event.get("type"), event.get("result"), event.get("card_id")
        if kind == "remediation_scheduled" and cid:
            scheduled[cid] = True
        key = event.get("review_key") if kind == "review" else cid
        if kind in ("card", "review") and result == "pass":
            if key in scheduled:
                rescued.add(key)
                scheduled.pop(key, None)
            day = str(event.get("at", ""))[:10]
            per_day[day] = per_day.get(day, 0) + 1
        if kind == "card" and result == "pass" and event.get("attempts") == 1:
            first_try.add(cid)
    earned_reviews = {(e.get("review_key"), e.get("review_stage")) for e in events
                      if e.get("type") == "review" and e.get("result") == "pass"}
    stills = [s for s in cur["main_stage_sequence"] if s.startswith("S")]
    return {
        "passed": len(passed),
        "transfer": sum(1 for cid in passed if cid.endswith(".06")),
        "best_streak": model["best"],
        "commands": len(model["deck"]),
        "range": ranged,
        "rescued": len(rescued),
        "first_try": len(first_try),
        "reviews": len(earned_reviews),
        "goal_day": 1 if any(n >= model["target"] for n in per_day.values()) else 0,
        "unlocked_stills": sum(1 for s in stills
                               if progress["stages"][s]["state"] != "locked"),
    }


def _badges(model):
    values = _rule_values(model)
    progress = model["progress"]
    rows = []
    for badge in TH.BADGES:
        if badge["rule"] == "stage":
            cell = progress["stages"][badge["stage"]]
            have = cell["done"] + cell["reviews_done"]
            need = cell["total"] + cell["reviews_total"]
            earned = cell["state"] == "mastered"
        else:
            have, need = values[badge["rule"]], badge["need"]
            earned = have >= need
        if badge.get("runtime"):
            earned = badge["id"] in progress["badges"]
        rows.append(dict(badge, have=min(have, need), need=need, earned=earned))
    return rows


def _card_state(cid, stage_state, progress):
    if cid in progress.get("active_remediations", {}):
        return "revisit"
    if cid in set(progress["passed_cards"]):
        return "done"
    if progress["attempts"].get(cid):
        return "tried"
    return "locked" if stage_state == "locked" else "open"


def build_model(state, share, target=12, now=None):
    now = now or V2._now()
    cfg = SimpleNamespace(state=str(state))
    cur = V2.load_curriculum(str(share))
    events = V2.read_events(cfg)
    progress = V2.project(cur, events)
    level, title, into, needed = V2._level(progress["xp"])
    _nl, next_title, _i, _n = V2._level(progress["xp"] - into + needed)
    streak, best, total = V2._legacy_streak(str(state))
    _counts, active = V2.activity_days(str(state))
    today = now.date()
    strip = [(today - dt.timedelta(days=13 - i),
              (today - dt.timedelta(days=13 - i)) in active) for i in range(14)]
    deck = V2.learned_deck(cur, progress)
    completed = progress.get("completed_at", {})
    new_today = [row for row in deck
                 if str(completed.get(row[3], ""))[:10] == today.isoformat()]
    nxt = V2.next_card(cur, progress)
    cards = {card["id"]: card for card in cur["cards"]}
    stages = []
    for stage in cur["stages"]:
        cell = progress["stages"][stage["id"]]
        modules, order = {}, []
        for cid in stage["card_ids"]:
            card = cards[cid]
            mid = card["module_id"]
            if mid not in modules:
                modules[mid] = []
                order.append(mid)
            modules[mid].append({
                "id": cid, "label": _card_label(card),
                "state": _card_state(cid, cell["state"], progress),
                "next": bool(nxt and nxt["id"] == cid),
            })
        module_rows = []
        for mid in order:
            module = next(m for m in cur["modules"] if m["id"] == mid)
            rows = modules[mid]
            done = sum(1 for r in rows if r["state"] in ("done", "revisit"))
            # A module can span stages; its mark here covers this stage's
            # lessons only, so a finished S0 part is not shown locked by A1.
            if done == len(rows):
                local = "mastered"
            elif done or any(r["state"] == "tried" for r in rows):
                local = "learning"
            else:
                local = "locked" if cell["state"] == "locked" else "available"
            module_rows.append({
                "id": mid, "title": module["title"], "skill": module.get("skill", ""),
                "cards": rows, "done": done, "total": len(rows), "state": local,
                "next": any(r["next"] for r in rows),
            })
        stages.append({
            "id": stage["id"], "title": stage["title"], "state": cell["state"],
            "done": cell["done"], "total": cell["total"], "optional": stage.get("optional", False),
            "current": stage["id"] == progress.get("current_stage"),
            "modules": module_rows,
        })
    model = {
        "cur": cur, "events": events, "progress": progress, "target": target,
        "level": level, "title": title, "into": into, "needed": needed,
        "next_level": level + 1, "next_title": next_title,
        "tier": TH.tier_for_level(level), "avatar": TH.avatar_for_level(level),
        "streak": streak, "best": best, "total": total,
        "personal_best": streak > 0 and streak >= best,
        "strip": strip, "today": V2.done_today(events), "deck": deck, "new_today": new_today,
        "revisit": V2._revisit_rows(cur, progress), "stages": stages,
        "next_card": nxt["id"] if nxt else None,
        "reviews_due": sum(1 for r in progress["reviews"].values() if V2._due(r.get("next_due"))),
    }
    model["badges"] = _badges(model)
    open_badges = [b for b in model["badges"] if not b["earned"] and b["need"]]
    model["next_badge"] = (max(open_badges, key=lambda b: (b["have"] / b["need"], -b["need"]))
                           if open_badges else None)
    return model


# ---------------------------------------------------------------- rendering
# Rich Text builders; `phase` drives the animated effects (0 when static).

def _hex(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _mix(a, b, t):
    ca, cb = _hex(a), _hex(b)
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(ca, cb))


def gradient_colour(stops, t):
    t %= 1.0
    span = t * len(stops)
    index = int(span)
    return _mix(stops[index % len(stops)], stops[(index + 1) % len(stops)], span - index)


def tier_text(text, tier, phase=0.0, animate=False):
    """Level title in its tier colour: gradient for pro, sweep shine for metals."""
    from rich.text import Text
    out = Text()
    stops = tier.get("gradient")
    if not stops and not (animate and tier.get("colour")):
        return Text(text, style="bold " + (tier.get("colour") or ""))
    n = max(1, len(text))
    for i, ch in enumerate(text):
        if stops:
            out.append(ch, style="bold " + gradient_colour(stops, i / n * 0.8 - phase))
        elif tier.get("colour"):
            colour = tier["colour"]
            if animate:
                band = (phase % 1.0) * (n + 8) - 4
                closeness = max(0.0, 1 - abs(i - band) / 3)
                colour = _mix(colour, "#ffffff", 0.7 * closeness)
            out.append(ch, style="bold " + colour)
        else:
            out.append(ch, style="bold")
    return out


def bar(done, total, width=10):
    from rich.text import Text
    filled = 0 if not total else round(width * min(done, total) / total)
    return Text.assemble(("▕", TH.STYLE["meta"]), ("█" * filled, TH.STYLE["bar_full"]),
                         ("░" * (width - filled), TH.STYLE["bar_empty"]), ("▏", TH.STYLE["meta"]))


def _fit(options, width):
    """First Text whose cell width fits; the last option is cropped."""
    for option in options:
        if option.cell_len <= width:
            return option
    last = options[-1].copy()
    last.truncate(max(1, width), overflow="ellipsis")
    return last


def header_lines(model, width, phase=0.0, animate=False):
    """Three header rows beside the avatar: level/XP, streak/today, badge."""
    from rich.text import Text
    S = TH.STYLE
    tier = model["tier"]
    name = "Lv%d %s" % (model["level"], model["title"])
    nxt = "→ Lv%d %s" % (model["next_level"], model["next_title"])
    xp = "%d/%d XP" % (model["into"], model["needed"])
    title = tier_text(name, tier, phase, animate)
    level_opts = [
        Text.assemble(title, "  ", bar(model["into"], model["needed"], 12), " ", xp, "  ",
                      (nxt, S["meta"]), "  ", (tier["name"], S["meta"])),
        Text.assemble(title, "  ", bar(model["into"], model["needed"], 12), " ", xp, "  ",
                      (nxt, S["meta"])),
        Text.assemble(title, " ", bar(model["into"], model["needed"], 8), " ", xp),
        Text.assemble(title, " ", xp),
    ]
    # Streak: 🔥 always beside the number; it glows on a personal best.
    if model["personal_best"] and animate:
        glow = S["flame_glow"][int(phase * len(S["flame_glow"]) * 4) % len(S["flame_glow"])]
        flame_style = "bold " + glow
    else:
        flame_style = S["flame"]
    days = "%d day%s" % (model["streak"], "" if model["streak"] == 1 else "s")
    streak = Text.assemble(("🔥 ", flame_style), (days, flame_style if model["personal_best"]
                                                  else "bold"))
    best = (Text(" ★ best ever", style=S["warn"] + " bold") if model["personal_best"]
            else Text(" · best %d" % model["best"], style=S["meta"]))
    strip = Text()
    for day, on in model["strip"]:
        strip.append("■" if on else "□", style=S["strip_on"] if on else S["strip_off"])
    goal_met = model["today"] >= model["target"]
    today = Text.assemble("today ", (str(model["today"]), "bold"), "/%d" % model["target"],
                          (" ✓", S["ok"]) if goal_met else "")
    plus = (Text("  +%d new" % len(model["new_today"]), style=S["ok"])
            if model["new_today"] else Text(""))
    streak_opts = [
        Text.assemble(streak, best, "  ", strip, "  ", today, plus),
        Text.assemble(streak, best, "  ", strip, "  ", today),
        Text.assemble(streak, best, "  ", today),
        Text.assemble(streak, " ", today),
    ]
    earned = sum(1 for b in model["badges"] if b["earned"])
    nb = model["next_badge"]
    badge = Text.assemble(("badges ", "bold"), ("%d" % earned, S["ok"]),
                          "/%d" % len(model["badges"]))
    if nb:
        sparkle = Text("")
        if animate and nb["have"] / nb["need"] >= 0.6:
            colours = S["sparkle"]
            k = int(phase * 40)
            glyphs = ["✦", "✧", "·", " "]
            sparkle = Text.assemble(
                (" " + glyphs[k % 4], colours[k % len(colours)]),
                (glyphs[(k + 2) % 4], colours[(k + 1) % len(colours)]))
        head = Text.assemble(" · next ", (nb["glyph"] + " " + nb["name"], "bold"))
        tail = Text.assemble(" %d/%d" % (nb["have"], nb["need"]), sparkle)
        badge_opts = [
            Text.assemble(badge, head, " ", bar(nb["have"], nb["need"], 10), tail,
                          ("  " + nb["desc"], S["meta"])),
            Text.assemble(badge, head, " ", bar(nb["have"], nb["need"], 10), tail),
            Text.assemble(badge, head, tail),
        ]
    else:
        badge_opts = [Text.assemble(badge, (" · every badge earned", S["ok"]))]
    return [_fit(level_opts, width), _fit(streak_opts, width), _fit(badge_opts, width)]


def avatar_text(model, phase=0.0, animate=False):
    from rich.text import Text
    tier = model["tier"]
    out = Text()
    for row_no, row in enumerate(model["avatar"]):
        if row_no:
            out.append("\n")
        if tier.get("gradient"):
            for i, ch in enumerate(row):
                out.append(ch, style="bold " + gradient_colour(
                    tier["gradient"], (i + row_no) / 10 - phase))
        elif tier.get("colour"):
            out.append(row, style="bold " + tier["colour"])
        else:
            out.append(row)
    return out


def journey_map(model, width):
    """One-row bird's-eye view: every stage as a coloured state glyph."""
    from rich.text import Text
    S = TH.STYLE
    groups = [("stills", "S"), ("animation", "A"), ("side", "P")]
    wide = width >= 96
    out = Text()
    for name, prefix in groups:
        rows = [s for s in model["stages"] if s["id"].startswith(prefix)]
        out.append(("  " if out.plain else "") + name + " ", style=S["meta"])
        for s in rows:
            glyph, style_key, _w = TH.STATE[s["state"]]
            style = S.get(style_key) if style_key else None
            if s["current"]:
                style = S["here"]
            if wide:
                out.append(s["id"], style=style)
            out.append(glyph + (" " if wide else ""), style=style)
    return _fit([out], width)


# ------------------------------------------------------------------ labels

def _clip_plain(text, width):
    from rich.cells import cell_len
    if cell_len(text) <= width:
        return text
    out = ""
    for ch in text:
        if cell_len(out + ch + "…") > width:
            break
        out += ch
    return out + "…"


def node_label(kind, data, width):
    from rich.text import Text
    S = TH.STYLE
    if kind == "stage":
        glyph, style_key, _w = TH.STATE[data["state"]]
        here = "  ← you are here" if data["current"] else ""
        count = " %d/%d" % (data["done"], data["total"])
        fixed = 2 + 3 + 13 + len(count) + len(here)
        pad = max(6, min(30, width - fixed))
        title = _clip_plain(data["title"] + (" (optional)" if data["optional"] else ""), pad)
        return Text.assemble((glyph, S.get(style_key) if style_key else ""), " ",
                             (data["id"].ljust(3), "bold"),
                             title.ljust(pad),
                             " ", bar(data["done"], data["total"], 10), count,
                             (here, S["here"]))
    if kind == "module":
        glyph, style_key, _w = TH.STATE[data["state"]]
        count = " %d/%d" % (data["done"], data["total"])
        fixed = 2 + 9 + len(count) + (7 if data["next"] else 0)
        title = _clip_plain(data["title"], max(6, width - fixed))
        return Text.assemble((glyph, S.get(style_key) if style_key else ""), " ", title, " ",
                             bar(data["done"], data["total"], 6), count,
                             ("  ← now" if data["next"] else "", S["here"]))
    if kind == "card":
        glyph, style_key = TH.CARD_STATE[data["state"]]
        tail = "  ← next" if data["next"] else ""
        title = _clip_plain(data["label"], max(6, width - 2 - len(tail)))
        style = S["meta"] if data["state"] == "locked" else ""
        return Text.assemble((glyph, S.get(style_key) if style_key else ""), " ",
                             (title, style), (tail, S["here"]))
    if kind == "revisit":
        _cid, title, action = data
        return Text.assemble(("↻ ", S["warn"]), _clip_plain("%s — %s" % (title, action),
                                                            max(6, width - 2)))
    if kind == "command":
        family, reminder, times, _first = data
        count = "×%d " % times
        return Text.assemble(("✓ ", S["ok"]), (count, S["meta"]),
                             _clip_plain(reminder, max(6, width - 2 - len(count))))
    if kind == "badge":
        if data["earned"]:
            return Text.assemble((data["glyph"] + " " + data["name"], S["ok"]),
                                 (_clip_plain("  " + data["desc"],
                                              max(4, width - len(data["name"]) - 2)), S["meta"]))
        count = " %d/%d " % (data["have"], data["need"])
        return Text.assemble((data["glyph"] + " " + data["name"], S["meta"]), " ",
                             bar(data["have"], data["need"], 6), count,
                             (_clip_plain(data["desc"], max(4, width - len(data["name"])
                                                        - 12 - len(count))), S["meta"]))
    if kind == "section":
        title, count, extra = data
        return Text.assemble((title, "bold"), " ", (str(count), S["ok"] if count else S["meta"]),
                             (extra, S["ok"]))
    return Text(str(data))


def module_detail(model, module):
    """Plain-language module page for the Enter screen."""
    from rich.text import Text
    S = TH.STYLE
    K = V2._keys_module()
    cards = {card["id"]: card for card in model["cur"]["cards"]}
    out = Text()
    out.append(module["title"] + "\n", style="bold")
    if module.get("skill"):
        out.append("you practise: ", style=S["meta"])
        out.append(module["skill"] + "\n")
    out.append_text(bar(module["done"], module["total"], 16))
    out.append(" %d/%d lessons\n\n" % (module["done"], module["total"]))
    for row in module["cards"]:
        glyph, style_key = TH.CARD_STATE[row["state"]]
        out.append(glyph + " ", style=S.get(style_key) if style_key else "")
        out.append(row["label"], style="bold" if row["next"] else "")
        if row["next"]:
            out.append("  ← next", style=S["here"])
        out.append("\n")
        expected = cards.get(row["id"], {}).get("expected")
        if row["state"] in ("done", "revisit") and expected:
            keys = [family for family, _m in K.families(expected) if family != "[count]"]
            if keys:
                out.append("    keys: ", style=S["meta"])
                out.append(" · ".join(keys) + "\n", style=S["key"])
    return out


def command_detail(model, row):
    from rich.text import Text
    S = TH.STYLE
    K = V2._keys_module()
    family, reminder, times, first = row
    out = Text()
    out.append("✓ ", style=S["ok"])
    out.append(family + "\n", style=S["key"])
    out.append(reminder + "\n\n")
    example = K.example_for(family)
    if example:
        out.append("e.g. ", style=S["meta"])
        out.append(example + "\n")
    out.append("used in %d lesson%s · first met in %s\n" % (
        times, "" if times == 1 else "s", first), style=S["meta"])
    return out


def badge_detail(model, row):
    """Badge page: what it asks for, progress, and its trophy art with credit."""
    from rich.text import Text
    S = TH.STYLE
    out = Text()
    out.append(row["glyph"] + " " + row["name"] + "\n", style=S["ok"] if row["earned"] else "bold")
    out.append(row["desc"] + "\n", style=S["meta"])
    if row["earned"]:
        out.append("✓ earned\n", style=S["ok"])
    else:
        out.append("%d/%d so far\n" % (row["have"], row["need"]))
    trophy = TH.trophy_for(row["id"])
    if trophy:
        out.append("\n")
        style = "" if row["earned"] else S["meta"]
        for line in trophy["art"]:
            out.append("  " + line + "\n", style=style)
        if not row["earned"]:
            out.append("  (full colour once earned)\n", style=S["meta"])
        out.append("\n" + trophy["credit"] + "\n", style=S["meta"])
    return out


HELP = """KEYS
  j / k        move down / up          g / G   top / bottom
  za           open or close a fold    zo / zc open / close
  zR / zM      open all / close all
  Enter        open a module, command, or badge
  /            search · n / N next / previous match
  f            send feedback about this screen
  ?            this help · q quit (Esc closes a page)

MARKS
  ✓ done  ◐ in progress  ◆ final check  ↻ coming back  ○ open  ▫ locked
  🔥 streak (glows on a personal best) · ■ a day you practised"""


# ----------------------------------------------------------------- the app

def make_app(model, *, state, animate=None, colour=None):
    """Build the Textual app. Imported lazily so the model works without it."""
    from rich.text import Text
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical, VerticalScroll
    from textual.screen import ModalScreen
    from textual.widgets import Input, Static, Tree

    animate = animations_enabled() if animate is None else animate
    colour = colour_enabled() if colour is None else colour

    class Page(ModalScreen):
        AUTO_FOCUS = "VerticalScroll"
        BINDINGS = [Binding("escape,q,enter", "dismiss_page", "close"),
                    Binding("j", "scroll_down", show=False),
                    Binding("k", "scroll_up", show=False)]
        DEFAULT_CSS = """
        Page { align: center middle; }
        Page > VerticalScroll { width: 90%; max-width: 100; height: 90%; border: round $accent;
                                padding: 0 1; background: $surface; }
        """

        def __init__(self, body):
            super().__init__()
            self.body = body

        def compose(self) -> ComposeResult:
            with VerticalScroll():
                yield Static(self.body, classes="page-body")
                yield Static(Text("Esc / q / Enter closes", style=TH.STYLE["meta"]))

        def action_dismiss_page(self):
            self.dismiss(None)

        def action_scroll_down(self):
            self.query_one(VerticalScroll).scroll_down()

        def action_scroll_up(self):
            self.query_one(VerticalScroll).scroll_up()

    class FeedbackPage(ModalScreen):
        AUTO_FOCUS = "#feedback-input"
        BINDINGS = [Binding("escape", "cancel", "cancel")]
        DEFAULT_CSS = """
        FeedbackPage { align: center middle; }
        FeedbackPage > Vertical { width: 90%; height: auto; border: round $accent;
                                  padding: 0 1; background: $surface; }
        """

        def compose(self) -> ComposeResult:
            with Vertical():
                yield Static("FEEDBACK · what is wrong or confusing here?\n"
                             "Enter sends · Esc cancels")
                yield Input(placeholder="type your message", id="feedback-input")

        def on_input_submitted(self, event):
            self.dismiss(event.value)

        def action_cancel(self):
            self.dismiss(None)

    class JourneyTree(Tree):
        BINDINGS = [Binding("j", "cursor_down", show=False),
                    Binding("k", "cursor_up", show=False),
                    Binding("g", "scroll_home", show=False),
                    Binding("G", "scroll_end", show=False)]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.z_pending = False

        def on_key(self, event):
            if self.z_pending:
                self.z_pending = False
                if event.character in ("a", "o", "c", "R", "M"):
                    event.stop()
                    event.prevent_default()
                    self.app.fold(event.character)
                    return
            if event.character == "z":
                self.z_pending = True
                event.stop()
                event.prevent_default()

        def on_resize(self, _event):
            self.app.relabel()

    class Dashboard(App):
        TITLE = "vim-daily journey"
        AUTO_FOCUS = "#tree"
        CSS = """
        Screen { layout: vertical; }
        #top { height: 3; }
        #avatar { width: 9; height: 3; padding: 0 1 0 0; }
        #head { height: 3; width: 1fr; }
        #map { height: 1; }
        #main { height: 1fr; }
        #tree { width: 1fr; overflow-x: hidden; }
        #side { width: 42%; display: none; border-left: tall $panel; padding: 0 1; }
        #search { dock: bottom; display: none; }
        #keys { height: 1; }
        Static { text-wrap: nowrap; }
        #side, .page-body { text-wrap: wrap; }
        """
        BINDINGS = [Binding("q", "quit", "quit"),
                    Binding("question_mark", "help", "help"),
                    Binding("f", "feedback", "feedback"),
                    Binding("slash", "search", "search"),
                    Binding("n", "next_match", show=False),
                    Binding("N", "previous_match", show=False)]

        def __init__(self):
            super().__init__(ansi_color=True if not colour else None)
            self.model = model
            self.phase = 0.0
            self.matches = []
            self.match_index = -1
            self.labelled_width = None

        # --- layout
        def compose(self) -> ComposeResult:
            with Horizontal(id="top"):
                yield Static(id="avatar")
                with Vertical(id="head"):
                    yield Static(id="line1")
                    yield Static(id="line2")
                    yield Static(id="line3")
            yield Static(id="map")
            with Horizontal(id="main"):
                tree = JourneyTree("journey", id="tree")
                tree.show_root = False
                tree.auto_expand = False
                tree.guide_depth = 3
                yield tree
                yield Static(id="side")
            yield Input(placeholder="search: stage, module, lesson, command", id="search")
            yield Static(id="keys")

        def on_mount(self):
            self.build_tree()
            self.query_one(JourneyTree).focus()
            self.paint()
            if animate:
                self.set_interval(TH.ANIM["tick"], self.tick)

        def on_resize(self, _event):
            self.paint()

        # --- content
        def build_tree(self):
            tree = self.query_one(JourneyTree)
            tree.clear()
            m = self.model
            cursor = None
            for stage in m["stages"]:
                snode = tree.root.add("", data=("stage", stage), expand=stage["current"])
                if stage["current"]:
                    cursor = cursor or snode
                for module in stage["modules"]:
                    # Current stage open, its modules closed: the whole
                    # journey stays in view at 80x24; zo shows the lessons.
                    mnode = snode.add("", data=("module", module), expand=False)
                    if module["next"] and stage["current"]:
                        cursor = mnode
                    for card in module["cards"]:
                        mnode.add_leaf("", data=("card", card))
            section = tree.root.add("", data=("section", ("TO REVISIT", len(m["revisit"]), "")))
            for row in m["revisit"]:
                section.add_leaf("", data=("revisit", row))
            plus = " +%d today" % len(m["new_today"]) if m["new_today"] else ""
            section = tree.root.add("", data=("section", ("COMMANDS LEARNED", len(m["deck"]),
                                                          plus)))
            for row in m["deck"]:
                section.add_leaf("", data=("command", row))
            earned = sum(1 for b in m["badges"] if b["earned"])
            section = tree.root.add("", data=("section", ("BADGES", earned,
                                                          "/%d" % len(m["badges"]))))
            for row in sorted(m["badges"], key=lambda b: (not b["earned"], -b["have"] / b["need"])):
                section.add_leaf("", data=("badge", row))
            self.labelled_width = None
            self.relabel()
            if cursor is not None:
                self.call_after_refresh(self.move_to, cursor)

        def label_width(self):
            tree = self.query_one(JourneyTree)
            # Leave room for the vertical scrollbar so no row is cropped.
            width = tree.size.width or self.size.width
            return max(24, width - 3)

        def relabel(self):
            width = self.label_width()
            if width == self.labelled_width:
                return
            self.labelled_width = width
            tree = self.query_one(JourneyTree)

            def walk(node, depth):
                for child in node.children:
                    kind, data = child.data
                    # Tree indents each level by guide_depth plus the fold icon.
                    child.set_label(node_label(kind, data, width - depth * 3 - 2))
                    walk(child, depth + 1)
            walk(tree.root, 0)

        def paint(self):
            width = self.size.width
            side = self.query_one("#side", Static)
            side.display = width >= 110
            avatar = self.query_one("#avatar", Static)
            avatar.update(avatar_text(self.model, self.phase, animate))
            lines = header_lines(self.model, max(20, width - 10), self.phase, animate)
            for index, line in enumerate(lines, 1):
                self.query_one("#line%d" % index, Static).update(line)
            self.query_one("#map", Static).update(journey_map(self.model, width))
            keys = [("j/k", "move"), ("za", "fold"), ("Enter", "open"), ("/", "search"),
                    ("f", "feedback"), ("?", "help"), ("q", "quit")]
            text = Text()
            for key, word in keys:
                if text.cell_len + len(key) + len(word) + 3 > width:
                    break
                text.append(key, style=TH.STYLE["key"])
                text.append(" " + word + "  ", style=TH.STYLE["meta"])
            self.query_one("#keys", Static).update(text)
            if side.display:
                self.update_side()

        def tick(self):
            self.phase = (self.phase + TH.ANIM["tick"] / TH.ANIM["sweep_period"]) % 1.0
            width = self.size.width
            lines = header_lines(self.model, max(20, width - 10), self.phase, True)
            for index, line in enumerate(lines, 1):
                self.query_one("#line%d" % index, Static).update(line)
            if self.model["tier"].get("gradient"):
                self.query_one("#avatar", Static).update(
                    avatar_text(self.model, self.phase, True))

        def update_side(self):
            node = self.query_one(JourneyTree).cursor_node
            side = self.query_one("#side", Static)
            if node is None or node.data is None:
                side.update("")
                return
            kind, data = node.data
            if kind == "module":
                side.update(module_detail(self.model, data))
            elif kind == "card":
                module = node.parent.data[1]
                side.update(module_detail(self.model, module))
            elif kind == "command":
                side.update(command_detail(self.model, data))
            elif kind == "stage":
                body = Text()
                body.append("%s %s\n" % (data["id"], data["title"]), style="bold")
                body.append(TH.STATE[data["state"]][2] + "\n\n", style=TH.STYLE["meta"])
                for module in data["modules"]:
                    body.append_text(node_label("module", module, 40))
                    body.append("\n")
                side.update(body)
            else:
                side.update(node_label(kind, data, 40))

        def on_tree_node_highlighted(self, _event):
            if self.query_one("#side", Static).display:
                self.update_side()

        def on_tree_node_selected(self, event):
            node = event.node
            if node.data is None:
                return
            kind, data = node.data
            if kind in ("stage", "section"):
                node.toggle()
            elif kind == "module":
                self.push_screen(Page(module_detail(self.model, data)))
            elif kind == "card":
                self.push_screen(Page(module_detail(self.model, node.parent.data[1])))
            elif kind == "command":
                self.push_screen(Page(command_detail(self.model, data)))
            elif kind == "badge":
                self.push_screen(Page(badge_detail(self.model, data)))
            else:
                self.push_screen(Page(node_label(kind, data, 200)))

        # --- navigation
        def move_to(self, node):
            tree = self.query_one(JourneyTree)
            parent = node.parent
            while parent is not None:
                parent.expand()
                parent = parent.parent
            self.call_after_refresh(lambda: (tree.move_cursor(node), tree.scroll_to_node(node)))

        def fold(self, key):
            tree = self.query_one(JourneyTree)
            node = tree.cursor_node
            if node is None:
                return
            if key == "R":
                for child in tree.root.children:
                    child.expand_all()
                return
            if key == "M":
                top = node
                while top.parent is not None and top.parent is not tree.root:
                    top = top.parent
                for child in tree.root.children:
                    child.collapse_all()
                self.call_after_refresh(tree.move_cursor, top)
                return
            target = node if node.allow_expand and node.children else node.parent
            if target is None or target is tree.root:
                return
            if key == "a":
                target.toggle()
            elif key == "o":
                target.expand()
            elif key == "c":
                target.collapse()
            if target is not node and not target.is_expanded:
                self.call_after_refresh(tree.move_cursor, target)

        def all_nodes(self):
            out = []

            def walk(node):
                for child in node.children:
                    out.append(child)
                    walk(child)
            walk(self.query_one(JourneyTree).root)
            return out

        def action_search(self):
            box = self.query_one("#search", Input)
            box.display = True
            box.value = ""
            box.focus()

        def on_input_submitted(self, event):
            if event.input.id != "search":
                return
            needle = event.value.strip().lower()
            event.input.display = False
            self.query_one(JourneyTree).focus()
            if not needle:
                return
            self.matches = [n for n in self.all_nodes()
                            if needle in node_label(*n.data, 400).plain.lower()]
            self.match_index = -1
            if not self.matches:
                self.notify("no match for %r" % needle, severity="warning")
                return
            self.action_next_match()

        def on_key(self, event):
            box = self.query_one("#search", Input)
            if event.key == "escape" and box.display:
                box.display = False
                self.query_one(JourneyTree).focus()
                event.stop()

        def action_next_match(self, step=1):
            if not self.matches:
                return
            self.match_index = (self.match_index + step) % len(self.matches)
            self.move_to(self.matches[self.match_index])
            self.notify("match %d/%d" % (self.match_index + 1, len(self.matches)), timeout=1.5)

        def action_previous_match(self):
            self.action_next_match(-1)

        # --- pages
        def action_help(self):
            self.push_screen(Page(Text(HELP)))

        def action_feedback(self):
            node = self.query_one(JourneyTree).cursor_node
            context = {"screen": "dashboard", "card_id": None, "module_id": None}
            if node is not None and node.data:
                kind, data = node.data
                if kind == "card":
                    context["card_id"] = data["id"]
                elif kind == "module":
                    context["module_id"] = data["id"]
                elif kind == "revisit":
                    context["card_id"] = data[0]

            def done(message):
                if not message or not message.strip():
                    self.notify("feedback cancelled", timeout=2)
                    return
                V2.FEEDBACK["path"] = V2.feedback_path(state)
                V2.note_feedback_context(revision=self.model["cur"].get("revision"), **context)
                with contextlib.redirect_stdout(io.StringIO()):
                    saved = V2.collect_feedback(lambda _prompt: message, screen="dashboard")
                self.notify("✓ feedback saved — thank you" if saved else "feedback not saved",
                            timeout=3)

            self.push_screen(FeedbackPage(), done)

    return Dashboard()


def main(argv=None):
    parser = argparse.ArgumentParser(description="vim-daily interactive dashboard")
    parser.add_argument("--state", default=os.path.join(
        os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state")), "vim-daily"))
    parser.add_argument("--share", default=str(HERE))
    parser.add_argument("--target", type=int, default=int(os.environ.get("VIM_DAILY_TARGET",
                                                                         "12")))
    parser.add_argument("--screenshot", help="save an SVG of the first screen and exit")
    parser.add_argument("--size", default="80x24", help="screenshot size, COLSxROWS")
    parser.add_argument("--preview-level", type=int,
                        help="show this level's title, tier colour and avatar (display only)")
    args = parser.parse_args(argv)
    try:
        import textual  # noqa: F401
    except ImportError:
        print("dashboard: Textual is not installed for %s" % sys.executable, file=sys.stderr)
        return UNAVAILABLE
    model = build_model(args.state, args.share, args.target)
    if args.preview_level:
        level, title, _into, _needed = V2._level((args.preview_level - 1) * 80)
        model.update(level=level, title=title, next_level=level + 1,
                     next_title=V2._level(level * 80)[1],
                     tier=TH.tier_for_level(level), avatar=TH.avatar_for_level(level))
    if args.screenshot:
        import asyncio
        cols, rows = (int(v) for v in args.size.lower().split("x"))
        app = make_app(model, state=args.state, animate=False)

        async def shoot():
            async with app.run_test(size=(cols, rows)) as pilot:
                await pilot.pause()
                path = Path(args.screenshot).resolve()
                app.save_screenshot(filename=path.name, path=str(path.parent))
        asyncio.run(shoot())
        print(args.screenshot)
        return 0
    make_app(model, state=args.state).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
