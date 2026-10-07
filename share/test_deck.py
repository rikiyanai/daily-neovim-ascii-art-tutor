"""Memory plan 2026-09-29: anatomy diagrams, the authored deck, spacing, warm-up.

Usage: python3 share/test_deck.py [--no-headed]
The headed part drives bin/vim-daily-gate in a detached tmux session at
VIM_DAILY_TEST_COLUMNS x VIM_DAILY_TEST_ROWS (default 80x24) and prints the
captured warm-up and quiz screens.
"""
import copy
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import v2_keys as K  # noqa: E402
import v2_runtime as rt  # noqa: E402
import deck  # noqa: E402

# Keep this test independent of generated curriculum output.  The generator
# attaches card_ids to a fresh copy of the authored source; a stale or partial
# curriculum deck must not make the deck gate appear healthy.
CUR = json.loads((HERE / "curriculum-v2.json").read_text(encoding="utf-8"))
DECK_SOURCE = json.loads((HERE / "deck-v2.json").read_text(encoding="utf-8"))
CUR["deck"] = deck.build_deck(CUR["cards"], CUR["modules"], source=HERE / "deck-v2.json")
CARDS = {card["id"]: card for card in CUR["cards"]}
COLUMNS = int(os.environ.get("VIM_DAILY_TEST_COLUMNS", "80"))
ROWS = int(os.environ.get("VIM_DAILY_TEST_ROWS", "24"))
checks = 0


def check(condition, message):
    global checks
    checks += 1
    if not condition:
        raise AssertionError(message)


# 1. Anatomy snapshots (plan §1): the quiz keys, drawn slot by slot.
SNAPSHOTS = {
    "3yyGp": [
        " 3yyGp",
        " ││ │└ p = put the copy below the cursor line",
        " ││ └ G = the last line of the file (G alone)",
        " │└ yy = yank (copy) whole lines",
        " └ 3 = three lines",
        "In plain words: copy 3 lines starting at the cursor line, then go to the last",
        "  line of the file, then put the copy below the cursor line.",
        "Shape: [count] verb target: 3yy = yank 3 lines · {N}G = line N from the top ·",
        "  G alone = the last line · p = put below · P = Put above"],
    "2G$": [
        " 2G$",
        " ││└ $ = the end of this row",
        " │└ G = go to that line",
        " └ 2 = line 2, counted from the top",
        "In plain words: go to line 2, then go to the end of that row.",
        "Shape: {N}G = line N from the top · G alone = the last line · $ on its own =",
        "  the end of this row"],
    "fo": [
        " fo",
        " │└ o = the glyph to find",
        " └ f = find forward on THIS ROW only",
        "In plain words: move right along THIS ROW to the next 'o'.",
        "Shape: f{char} = this row only · /text<CR> = the whole file"],
    "3G": [
        " 3G",
        " │└ G = go to that line",
        " └ 3 = line 3, counted from the top",
        "In plain words: go to line 3.",
        "Shape: {N}G = line N from the top · G alone = the last line"],
    "G": [
        " G",
        " └ G = the last line of the file (G alone)",
        "In plain words: go to the last line of the file.",
        "Shape: {N}G = line N from the top · G alone = the last line"],
    "yyP": [
        " yyP",
        " │ └ P = put the copy above the cursor line",
        " └ yy = yank (copy) the whole line",
        "In plain words: copy the cursor line, then put the copy above the cursor line.",
        "Shape: [count] verb target: 3yy = yank 3 lines · p = put below · P = Put above"],
    ":%s/\\s\\+$//e<CR>": [
        " :%s/\\s\\+$//e",
        "  ││││ │ │││└ e: no error on lines that have no match",
        "  ││││ │ ││└ divider · empty replacement → delete",
        "  ││││ │ │└ divider",
        "  ││││ │ └ $ = the end of the line",
        "  ││││ └ \\+ = one or more of the previous item",
        "  │││└ \\s = a space or tab",
        "  ││└ divider",
        "  │└ s = substitute",
        "  └ % = every line",
        "In plain words: on every line, find one or more of: a space or tab, at the end",
        "  of the line and delete it (the first match on each line).",
        "Shape: :{where}s/{find}/{replace}/{flags} · no {where} = this line only"],
    "2G:s/,/:/g<CR>": [
        " 2G:s/,/:/g<CR>",
        " ││└ :s/,/:/g<CR> = on the current line: ',' becomes ':' (every match)",
        " │└ G = go to that line",
        " └ 2 = line 2, counted from the top",
        "In plain words: go to line 2, then on the current line, replace ',' with ':';",
        "  g = every match on the line, not just the first.",
        "Shape: {N}G = line N from the top · G alone = the last line ·",
        "  :{where}s/{find}/{replace}/{flags} · no {where} = this line only"],
}
for keys, want in SNAPSHOTS.items():
    got = K.anatomy(keys)
    check(got == want, "anatomy(%r) changed:\n%s" % (keys, "\n".join(got or ["None"])))
check(K.anatomy("2G0f;lr!ur,") is None, "more than 10 slots must fall back to None")
check(K.anatomy("3yyGp", 40) is None, "a tree row wider than the width must fall back")
check(K.anatomy("") is None, "empty keys draw nothing")
drawn = 0
for card in CUR["cards"]:
    if not card.get("show_recipe") or not card.get("expected"):
        continue
    rows = K.anatomy(card["expected"])
    if rows is None:
        continue
    drawn += 1
    for row in rows:
        check(len(row) <= 78, "%s: anatomy row wider than 78 cells: %r" % (card["id"], row))
        check("…" not in row, "%s: anatomy clipped with an ellipsis" % card["id"])
check(drawn >= 40, "expected most guided recipes to get a diagram, got %d" % drawn)

# 2. The authored deck ships only through the generator gate.
errors = deck.validate_deck(CUR, typed_check=rt._safe_typed_effect)
check(not errors, "deck validation failed:\n" + "\n".join(errors))
source_families = {fam for family in DECK_SOURCE["families"]
                   for fam in family.get("parser_families", [])}
used_families = {fam for module in CUR["modules"] if module["id"] in deck.COVERAGE_MODULES
                 for cid in module["card_ids"]
                 for fam, _meaning in K.families(CARDS[cid].get("expected") or "")}
check(not (used_families - source_families - deck.COVERAGE_EXEMPT),
      "authored source misses course families: %s" %
      sorted(used_families - source_families - deck.COVERAGE_EXEMPT))
check(all(family.get("card_ids") for family in CUR["deck"]["families"]),
      "build_deck must attach at least one lesson to every authored family")
index = deck.item_index(CUR)
for required in deck.REQUIRED_ITEMS:
    check(required in index, "missing misconception item %s" % required)
families = deck.family_map(CUR)
for left, right in (("DK.F", "DK.SEARCH"), ("DK.G", "DK.J"), ("DK.G", "DK.GG"),
                    ("DK.S", "DK.RANGE"), ("DK.GFLAG", "DK.RANGE"), ("DK.XR", "DK.R"),
                    ("DK.U", "DK.GMINUS")):
    check(right in families[left]["contrasts"] or left in families[right]["contrasts"],
          "contrast pair %s / %s is not linked" % (left, right))
bad = copy.deepcopy(CUR)
bad["deck"]["families"][0]["items"][0]["prompt"] = "Use the Ex address on this card."
bad["deck"]["families"][1]["items"] = []
bad_errors = deck.validate_deck(bad, run_typed=False)
check(any("internal word" in e for e in bad_errors), "banned learner words must fail")
check(any("no items" in e for e in bad_errors), "an empty family must fail")
bad = copy.deepcopy(CUR)
bad["deck"]["families"] = [f for f in bad["deck"]["families"] if f["id"] != "DK.ZERO"]
check(any("has no deck family" in e for e in deck.validate_deck(bad, run_typed=False)),
      "a reached command without a deck family must fail")

# 3. Screens fit an 80x24 popup: no clipped prose, no overflow.
for item_id, (family, item) in index.items():
    screen = deck.item_lines(family, item, "DECK QUIZ 1/5 · " + family["family"], 78)
    check(len(screen) + 1 <= 22, "%s: question screen has %d lines" % (item_id, len(screen)))
    for line in screen:
        check(len(line) <= 78 and "…" not in line, "%s: bad line %r" % (item_id, line))
    whys = item.get("why") or [t["why"] for t in item["trap_answers"]]
    for why in whys:
        page = deck.result_lines(family, item, False, why, 78, 22,
                                 answer_line="YOUR ANSWER: " + (item.get("choices") or ["x"])[0],
                                 right_line="RIGHT ANSWER: " + (item.get("choices") or ["x"])[-1])
        check(len(page) <= 22, "%s: result page has %d lines" % (item_id, len(page)))
        check(all(len(line) <= 78 and "…" not in line for line in page),
              "%s: result page line too wide or clipped" % item_id)
        check(any(line.startswith("  COMMON MIX-UP") for line in page),
              "%s: a wrong answer must name the mix-up" % item_id)

# 4. Leitner steps reuse review_intervals_hours.
now = dt.datetime(2026, 9, 29, 12, 0, tzinfo=dt.timezone.utc)
hours = CUR["review_intervals_hours"]
state = deck.schedule(CUR, {}, "good", now)
check(state["box"] == 1 and state["next_due"] == (now + dt.timedelta(hours=hours[0])).isoformat(),
      "good from a new item goes to box 1")
state = deck.schedule(CUR, state, "good", now)
check(state["box"] == 2, "good promotes")
state = deck.schedule(CUR, state, "hard", now)
check(state["box"] == 2 and state["next_due"] == (now + dt.timedelta(hours=hours[1])).isoformat(),
      "hard keeps the box")
state = deck.schedule(CUR, state, "again", now)
check(state["box"] == 0 and state["lapses"] == 1 and state["next_due"] == now.isoformat(),
      "again drops to box 0 and is due now")
top = {"box": len(hours), "lapses": 0}
check(deck.schedule(CUR, top, "good", now)["box"] == len(hours), "the top box is capped")


# 5. Fold, resurfacing, XP and scheduling order.
def ev(**row):
    row.setdefault("at", "2026-09-20T12:00:00-04:00")
    return row


passes = [ev(type="card", result="pass", card_id=cid, module_id=cid.split(".")[0],
             next_due="2099-01-01T00:00:00-05:00")
          for cid in ("M0.P0", "M0.01", "M0.YP", "M0.O")]
base = rt.project(CUR, passes)
deck_rows = [ev(type="deck", item_id="DK.G.01", family_id="DK.G", grade="again",
                result="wrong", box=0, next_due="2026-09-20T12:00:00-04:00"),
             ev(type="deck", item_id="DK.F.01", family_id="DK.F", grade="good",
                result="right", box=1, next_due="2099-01-01T00:00:00-05:00")]
with_deck = rt.project(CUR, passes + deck_rows)
check(with_deck["xp"] == base["xp"], "deck answers must not add XP")
check(with_deck["passed_cards"] == base["passed_cards"], "deck answers pass no lesson")
check(with_deck["deck"]["weak"] == ["DK.G.01"] and with_deck["deck"]["weak_families"] == ["DK.G"],
      "an again grade makes the item weak")
check(with_deck["deck"]["items"]["DK.F.01"]["box"] == 1, "box folds from the event")
failed = rt.project(CUR, passes + [ev(type="question", result="fail", card_id="M0.SL",
                                      question_id="Q-x", at="2026-09-21T09:00:00-04:00")])
for item in families["DK.S"]["items"]:
    state = failed["deck"]["items"].get(item["id"], {})
    check(state.get("resurfaced") and state.get("next_due") == "2026-09-21T09:00:00-04:00",
          "a failed paired question makes its family due: %s" % item["id"])
remedied = rt.project(CUR, passes + [ev(type="remediation_scheduled", result="scheduled",
                                        card_id="M0.YP", remediation_id="Q-M0.YP")])
check(all(i["id"] in remedied["deck"]["items"] for i in families["DK.YY"]["items"]),
      "a scheduled remediation makes its family due")
later = dt.datetime(2026, 9, 25, tzinfo=dt.timezone.utc)
picked = deck.pick(CUR, with_deck, 4, now=later)
check(picked[0] == "DK.G.01", "weak items come first: %r" % picked)
check("DK.F.01" not in picked, "an item not yet due is not drilled")
check(all(deck.item_index(CUR)[i][0]["id"] in deck.eligible_families(CUR, with_deck)
          or i == "DK.G.01" for i in picked), "new items come only from met families")
check(deck.pick(CUR, rt.project(CUR, []), 5, now=later) == [],
      "a learner with no passed lesson has nothing to drill")
nearby = deck.warmup_families(CUR, "M11.02")
check({"DK.GG", "DK.YY", "DK.G", "DK.P"} <= nearby, "warm-up uses the upcoming lesson's families")
check("DK.J" in nearby, "warm-up adds contrast partners")
check(deck.warmup_due(CUR, passes, later), "no lesson or warm-up today: warm-up is due")
check(not deck.warmup_due(CUR, passes + [ev(type="deck_warmup", result="skipped",
                                              at=later.isoformat())], later),
      "one warm-up per day")


# 6. Interactive item, feedback key, warm-up skip and --deck-miss, headless.
class Cfg:
    practice = False

    def __init__(self, state):
        self.state = state
        self.stamp = str(Path(state) / "last-prompt")


def scripted(values):
    values = iter(values)
    return lambda _prompt="": next(values)


os.environ["VIM_DAILY_TEST_ORDERED_CHOICES"] = "1"
with tempfile.TemporaryDirectory() as tmp:
    cfg = Cfg(tmp)
    rt.FEEDBACK["path"] = rt.feedback_path(tmp)
    rt.FEEDBACK["context"].clear()
    progress = rt.project(CUR, passes)
    grade = deck.ask_item(rt, cfg, CUR, progress, "DK.G.01", "T", source="quiz",
                          input_fn=scripted(["f", "why line 3?", "a", "h"]))
    check(grade == "hard", "right answer then h grades hard")
    grade = deck.ask_item(rt, cfg, CUR, progress, "DK.D.01", "T", source="quiz",
                          input_fn=scripted(["b", ""]))
    check(grade == "again", "a wrong answer grades again")
    grade = deck.ask_item(rt, cfg, CUR, progress, "DK.G.02", "T", source="quiz",
                          input_fn=scripted(["3jr#", ""]))
    check(grade == "again", "the trap keys are graded by effect and miss")
    grade = deck.ask_item(rt, cfg, CUR, progress, "DK.G.02", "T", source="quiz",
                          input_fn=scripted(["3Gr#", ""]))
    check(grade == "good", "the taught keys reach the target")
    rows = [json.loads(line) for line in Path(tmp, "events-v2.jsonl").read_text().splitlines()]
    check([r["grade"] for r in rows] == ["hard", "again", "again", "good"],
          "each graded item appends one deck event")
    check(not Path(cfg.stamp).exists(), "deck events do not touch the lesson stamp")
    feedback = [json.loads(line) for line in rt.feedback_path(tmp).read_text().splitlines()]
    check(feedback[0]["question_id"] == "DK.G.01" and feedback[0]["screen"] == "quiz",
          "f on a quiz screen saves feedback with the item context")
    progress = rt.project(CUR, passes + rows)
    check(progress["deck"]["weak"] == ["DK.D.01"],
          "missed items stay weak until answered right: %r" % progress["deck"]["weak"])
    events = passes + rows
    shown = deck.maybe_warmup(rt, cfg, CUR, progress, events, "M11.02",
                              input_fn=scripted(["s"]))
    check(shown, "the warm-up runs before the first lesson of the day")
    rows = [json.loads(line) for line in Path(tmp, "events-v2.jsonl").read_text().splitlines()]
    check(rows[-1]["type"] == "deck_warmup" and rows[-1]["result"] == "skipped",
          "s skips the warm-up with one key and records it")
    check(not deck.maybe_warmup(rt, cfg, CUR, progress, passes + rows, "M11.02",
                                input_fn=scripted([])),
          "the warm-up does not come back the same day")
    check(deck.record_misses(rt, cfg, CUR, progress, ["DK.U.01", "DK.GMINUS"]) == 0,
          "--deck-miss accepts item and family ids")
    check(deck.record_misses(rt, cfg, CUR, progress, ["nope"]) == 1, "unknown ids are refused")
    rows = [json.loads(line) for line in Path(tmp, "events-v2.jsonl").read_text().splitlines()]
    check({r["item_id"] for r in rows if r.get("source") == "external"} ==
          {"DK.U.01", "DK.GMINUS.01"}, "external misses are recorded per item")
    weak_card = CARDS["M0.YP"]
    rt.DECK_WEAK.clear()
    rt.DECK_WEAK.add("DK.YY")
    alert = rt._new_concept_alert(weak_card, CUR, width=66)
    rt.DECK_WEAK.clear()
    check(any("REMEMBER (missed in your deck)" in line for line in alert),
          "a weak family shows a REMEMBER line in the next lesson that uses it")

print("PASS deck: %d checks (anatomy snapshots, deck gate, 80x24 screens, spacing, "
      "fold, warm-up, feedback)" % checks)


# 7. Headed: the real gate in tmux at COLUMNS x ROWS.
def tmux(sock, *args, capture=False):
    return subprocess.run(["tmux", "-L", sock, *args], check=True, text=True,
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.DEVNULL)


def screen(sock):
    return tmux(sock, "capture-pane", "-p", "-t", "t", capture=True).stdout


def wait_for(sock, text, timeout=25):
    deadline = time.time() + timeout
    while time.time() < deadline:
        shot = screen(sock)
        if text in shot:
            return shot
        time.sleep(0.2)
    raise AssertionError("timed out waiting for %r; screen:\n%s" % (text, screen(sock)))


def headed(label, argv, seed_ids, steps):
    sock = "vdk-" + uuid.uuid4().hex[:8]
    with tempfile.TemporaryDirectory(prefix="vim-daily-deck-") as tmp:
        state = Path(tmp) / "state" / "vim-daily"
        state.mkdir(parents=True)
        rows = [ev(type="card", result="pass", card_id=cid, module_id=cid.split(".")[0],
                   next_due="2099-01-01T00:00:00-05:00") for cid in seed_ids]
        (state / "events-v2.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        env = ("env -u TMUX -u NVIM -u VIM_DAILY_NO_WARMUP XDG_STATE_HOME=%s XDG_DATA_HOME=%s "
               "VIM_DAILY_TEST_ORDERED_CHOICES=1 TERM=xterm-256color EDITOR=nvim " %
               (Path(tmp) / "state", Path(tmp) / "data"))
        command = env + " ".join([str(ROOT / "bin" / "vim-daily-gate"), *argv])
        try:
            subprocess.run(["tmux", "-L", sock, "-f", "/dev/null", "new-session", "-d", "-s", "t",
                            "-x", str(COLUMNS), "-y", str(ROWS), command + "; sleep 30"],
                           check=True)
            shots = []
            for wait_text, keys in steps:
                if wait_text.startswith("!"):
                    deadline = time.time() + 25
                    while time.time() < deadline:
                        shot = screen(sock)
                        if wait_text[1:] not in shot and shot.strip():
                            break
                        time.sleep(0.2)
                    check(wait_text[1:] not in shot and shot.strip(),
                          "%s: %r stayed or the screen went blank" % (label, wait_text))
                    shots.append(shot)
                    continue
                shot = wait_for(sock, wait_text)
                shots.append(shot)
                for line in shot.splitlines():
                    check(len(line) <= COLUMNS, "%s: line wider than the pane" % label)
                check("…" not in shot, "%s: prose clipped with an ellipsis:\n%s" % (label, shot))
                if keys is not None:
                    tmux(sock, "send-keys", "-t", "t", *keys)
            return shots, (state / "events-v2.jsonl").read_text()
        finally:
            subprocess.run(["tmux", "-L", sock, "kill-server"], stderr=subprocess.DEVNULL)
            # VD-31: kill-server can orphan the lesson's `nvim --embed`; reap
            # only processes whose command line names this test's temp dir.
            subprocess.run(["pkill", "-9", "-f", tmp], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)


if "--no-headed" not in sys.argv and shutil.which("tmux"):
    s0 = next(s for s in CUR["stages"] if s["id"] == "S0")["card_ids"]
    seed = s0[:s0.index("M11.02")]
    shots, ledger = headed("warm-up", ["--force"], seed, [
        ("WARM-UP 1/", ["s", "Enter"]),
        ("!WARM-UP", None)])
    warm = shots[0]
    check("s skips the warm-up" in warm, "the warm-up names its one-key skip")
    skipped = [json.loads(line) for line in ledger.splitlines() if "deck_warmup" in line]
    check(skipped and skipped[-1]["result"] == "skipped", "the skip is recorded: %r" % skipped)
    print("--- headed %dx%d: warm-up screen ---" % (COLUMNS, ROWS))
    print(warm.rstrip())
    print("--- headed %dx%d: after s (the lesson starts) ---" % (COLUMNS, ROWS))
    print("\n".join(shots[1].rstrip().splitlines()[:8]))
    shots, ledger = headed("quiz", ["--quiz", "2"], seed, [
        ("DECK QUIZ 1/2", ["b", "Enter"]),
        ("NOT QUITE", ["Enter"]),
        ("DECK QUIZ 2/2", ["3Gr#", "Enter"]),
        ("RIGHT", ["Enter"]),
        ("DECK QUIZ DONE", None)])
    check("✗ NOT QUITE" in shots[1] and "COMMON MIX-UP" in shots[1],
          "the wrong answer names the mix-up")
    check("✓ RIGHT" in shots[3], "the typed keys are graded right")
    grades = [json.loads(line).get("grade") for line in ledger.splitlines()
              if '"deck"' in line]
    check(grades == ["again", "good"], "the headed quiz recorded %r" % grades)
    for title, shot in (("quiz question", shots[0]), ("quiz wrong", shots[1]),
                        ("quiz typed question", shots[2]), ("quiz right", shots[3])):
        print("--- headed %dx%d: %s ---" % (COLUMNS, ROWS, title))
        print(shot.rstrip())
    print("PASS deck headed at %dx%d" % (COLUMNS, ROWS))
