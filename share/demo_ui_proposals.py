#!/usr/bin/env python3
"""Demo all UI proposal options in the terminal, anim_B_rainbow.py style.

Self-contained: stdlib only, no repo imports. Widths target ~72 usable
cols (80x24 popup interior). Animations are tty-only and never use
cursor addressing inline (no ESC[H/J, no ESC[nA): frames print
sequentially so pipes/CI stay clean.

Run:  python3 share/demo_ui_proposals.py           # step with any key
      python3 share/demo_ui_proposals.py --auto     # no pauses (CI/smoke)
      python3 share/demo_ui_proposals.py --no-anim  # static fallback only
      VIM_DAILY_ANIM=off python3 share/demo_ui_proposals.py --auto

Ground-truth paths cited here live in two repos:
  tutor:     share/v2_runtime.py, share/animation_lesson_pack.md,
             share/stone_story_variants.py, share/art.json,
             share/gen_curriculum_v2.py, bin/vim-daily-gate
  asciicker: /Users/r/Projects/asciicker-Y9-2/scripts/anim_B_rainbow.py,
             /Users/r/Projects/asciicker-Y9-2/scripts/anim_D_scanline.py,
             /Users/r/Projects/asciicker-Y9-2/scripts/_common.py
  (this repo has NO scripts/ dir; watchdogcannonical.py NOT-FOUND repo-wide)
"""
from __future__ import annotations
import colorsys
import datetime
import json
import os
import shutil
import sys
import textwrap
import time
from pathlib import Path

NO_ANIM = "--no-anim" in sys.argv or os.environ.get("VIM_DAILY_ANIM") == "off"
AUTO = "--auto" in sys.argv or not sys.stdin.isatty()
NO_COLOR = os.environ.get("NO_COLOR") is not None or os.environ.get("TERM") == "dumb"
CI = os.environ.get("CI") is not None
# _common.is_interactive() analogue: tty + not CI + not NO_COLOR.
ANIM_OK = (not NO_ANIM and not NO_COLOR and not CI
           and sys.stdout.isatty() and sys.stdin.isatty()
           and os.environ.get("TERM") != "dumb")
# _common emits 38;2 whenever interactive and not NO_COLOR.
TRUECOLOR = not NO_COLOR and os.environ.get("TERM") != "dumb"


def term_w() -> int:
    return max(20, min(72, shutil.get_terminal_size((80, 24)).columns - 2))


def C(code: str) -> str:
    return "" if NO_COLOR else code


BOLD, DIM, OFF = C("\033[1m"), C("\033[2m"), C("\033[0m")
GREEN, RED, YELLOW, CYAN = (C("\033[32m"), C("\033[31m"),
                            C("\033[33m"), C("\033[36m"))
KEY = C("\033[1;36m")
MAGENTA = C("\033[35m")
BRONZE = "" if NO_COLOR else "\033[38;2;205;127;50m"
GOLD = "" if NO_COLOR else "\033[38;2;255;215;0m"
GEMINI_STOPS = [(0x42, 0x85, 0xF4), (0x7B, 0x6C, 0xF6), (0xB3, 0x6B, 0xE0),
                (0xE2, 0x6D, 0x9A), (0xF2, 0xA6, 0x5A)]
# share/dashboard_theme.py:19-20 pro tier (pink-purple + warm tail);
# upstream: asciicker-Y9-2/scripts/cli_style.py GRADIENT_GEMINI
# #4796E4 -> #847ACE -> #C3677F (gemini-cli theme.ts GradientColors).


def gemini_text(line, phase=0.0):
    """Pink-purple stop sweep, cf. gradient_text_stops (RGB lerp)."""
    if not TRUECOLOR:
        return BOLD + line + OFF
    stops = GEMINI_STOPS
    chars = [ch for ch in line if ch != " "]
    n = max(1, len(chars))
    out, ci = [], 0
    k = len(stops) - 1
    for ch in line:
        if ch == " ":
            out.append(ch)
            continue
        t = (ci / (n - 1) if n > 1 else 0 + phase) % 1.0
        seg = min(int(t * k), k - 1)
        f = t * k - seg
        a, b = stops[seg], stops[seg + 1]
        r = int(a[0] + (b[0] - a[0]) * f)
        g = int(a[1] + (b[1] - a[1]) * f)
        bl = int(a[2] + (b[2] - a[2]) * f)
        out.append("\033[38;2;%d;%d;%dm%s\033[0m" % (r, g, bl, ch))
        ci += 1
    return "".join(out)

AVATARS = [
    ("Lv1 Finger-Rider", [" o", "(_)"]),
    ("Lv2 Row-Walker", ["  o", "->->", " /\\"]),
    ("Lv3 Line-Surgeon", ["  /o ", " / / ", "x-x-x"]),
    ("Lv4 Pose-Builder", ["+-o  ", "|/|  ", "|/\\  "]),
    ("Lv5 Frame-Crafter", ["+---+", "|:x:|", "+---+"]),
    ("Lv6 Tween-Reader", ["~o~~~", "~~o~~", "~~~o~"]),
    ("Lv7 Loop-Director", ["|\\==\\", "|/__/", "  |  "]),
]
TIERS = ("beg", "beg", "bronze", "bronze", "gold", "gold", "gemini")


def tier_color(lv):
    t = TIERS[min(7, max(1, lv)) - 1]
    if t == "bronze":
        return BRONZE or YELLOW
    if t == "gold":
        return GOLD or (YELLOW + BOLD)
    if t == "gemini":
        return ""  # caller uses rainbow_text
    return BOLD


EXTRA_BADGES = [
    ("method-purist", "pass first try within max_tokens"),
    ("comeback", "fail then pass same card same session"),
    ("review-keeper", "complete due review"),
    ("marathon", "today>=12 same day"),
    ("cartographer", "S0..S7 all unlocked"),
    ("transfer-adept", "3+ distinct transfer cards"),
    ("clean-slate", "pass after 7+ day gap"),
]


SECTIONS = ("lane1", "lane2", "lane2a", "lane2b", "lane2c", "lane3a",
            "lane3b", "lane3c", "lane3-levels", "lane3-badges",
            "trophies", "anima", "animb", "animc", "animd",
            "style", "avatars", "viewer")
TROPHY_SLOTS = ("trophies:01", "trophies:02", "trophies:03",
                "trophies:04a", "trophies:04b", "trophies:05a",
                "trophies:05b", "trophies:06", "trophies:07",
                "trophies:07b", "trophies:08a", "trophies:08b")


def _notes_path():
    args = sys.argv
    if "--notes-file" in args:
        i = args.index("--notes-file")
        if i + 1 < len(args):
            return Path(args[i + 1])
    return Path(__file__).with_name("demo_notes.json")


def _load_notes(path):
    try:
        data = json.loads(path.read_text())
        if isinstance(data, dict) and isinstance(data.get("notes"), dict):
            return data["notes"]
    except FileNotFoundError:
        return {}
    except Exception as e:
        print("demo notes unreadable (%s); continuing" % e, file=sys.stderr)
    return {}


def _save_notes(path, notes):
    path.write_text(json.dumps({"version": 1, "notes": notes}, indent=2) + "\n")


def _clean_note(text):
    t = "".join(ch for ch in text if ch.isprintable() or ch in (" ", "\t"))
    return " ".join(t.strip().split())[:500]


def _print_notes(section):
    if not section:
        return
    notes = _load_notes(_notes_path()).get(section, [])
    if not notes:
        return
    w = term_w()
    print("%s  # %s notes (%d):%s" % (DIM, section, len(notes), OFF))
    for n in notes[-20:]:
        txt = n.get("text", "") if isinstance(n, dict) else str(n)
        for line in textwrap.wrap(txt, width=w - 4) or [""]:
            print("  - " + line)


def _add_note(section, text):
    valid = set(SECTIONS) | set(TROPHY_SLOTS)
    if section not in valid:
        print("unknown section %s" % section, file=sys.stderr)
        print("known: %s" % " ".join(SECTIONS), file=sys.stderr)
        sys.exit(2)
    t = _clean_note(text)
    if not (1 <= len(t) <= 500):
        print("note must be 1..500 chars", file=sys.stderr)
        sys.exit(2)
    path = _notes_path()
    notes = _load_notes(path)
    slot = notes.get(section, [])
    slot.append({"ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "text": t})
    notes[section] = slot[-20:]
    _save_notes(path, notes)
    print("saved %s (%d total)" % (section, len(notes[section])))


def hue_fg(h: float) -> str:
    if not TRUECOLOR:
        return BOLD
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, 0.85, 1.0)
    return f"\033[38;2;{int(r*255)};{int(g*255)};{int(b*255)}m"


def rule(title: str) -> None:
    w = term_w()
    print(f"\n{BOLD}{'=' * w}{OFF}\n{BOLD}{title}{OFF}\n{BOLD}{'=' * w}{OFF}")


def pause(msg: str = "-- key: next | n: note | v: view | q: quit --", section=None) -> None:
    _print_notes(section)
    if AUTO:
        print(f"{DIM}[auto]{OFF}\n")
        return
    try:
        if sys.stdin.isatty():
            try:
                import termios
                import tty
                fd = sys.stdin.fileno()
                old = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    while True:
                        ch = os.read(fd, 1)
                        sys.stdout.write("\r\n")
                        if ch in (b"q", b"Q", b"\x03"):
                            sys.exit(0)
                        if ch in (b"n", b"N") and section:
                            termios.tcsetattr(fd, termios.TCSADRAIN, old)
                            try:
                                t = input("note for %s: " % section)
                                if t.strip():
                                    _add_note(section, t)
                            except (EOFError, KeyboardInterrupt):
                                pass
                            return
                        if ch in (b"v", b"V") and section:
                            _print_notes(section)
                            continue
                        return
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old)
            except Exception:
                pass
        if input(f"{DIM}{msg}{OFF}\n> ").strip().lower() == "q":
            sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(130)
    except EOFError:
        pass


def rainbow_text(line: str, phase: float) -> str:
    """Per-column hue wave, cf. anim_B_rainbow.py hue=(col/w+phase)%1."""
    if not TRUECOLOR:
        return f"{BOLD}{line}{OFF}"
    out = []
    n = max(1, len(line))
    for i, ch in enumerate(line):
        out.append(f"{hue_fg(i / n + phase)}{ch}")
    return "".join(out) + OFF


def scanline_banner(rows: list[str], delay: float = 0.06, hold: float = 0.15) -> None:
    """Traveling brighten band + hue wave, no cursor addressing."""
    if not ANIM_OK:
        for r in rows:
            print(rainbow_text(r, 0.10) if TRUECOLOR else f"{BOLD}{r}{OFF}")
        return
    n = len(rows)
    for cur in range(n):
        print(f"{DIM}--- scan {cur + 1}/{n} ---{OFF}")
        for i, r in enumerate(rows):
            if i < cur:
                print(rainbow_text(r, 0.10))
            elif i == cur:
                print(f"{C(chr(27) + '[1;37m')}{r}{OFF}")
            else:
                print(f"{DIM}{'.' * len(r)}{OFF}")
        sys.stdout.flush()
        time.sleep(delay)
    print(f"{DIM}--- final ---{OFF}")
    for r in rows:
        print(rainbow_text(r, 0.10))
    sys.stdout.flush()
    time.sleep(hold)


def demo_lane1() -> None:
    rule("LANE 1 — third-party TUI libraries (all 8 rows)")
    for name, fit, anim, cost, verdict in LIBS:
        n = name.replace("\n", " ")
        print(f"  {BOLD}{n}{OFF} -> {verdict}")
        print(f"    fit {fit.splitlines()[0]} | {anim.splitlines()[0]}")
        print(f"    {DIM}{cost.splitlines()[0]}{OFF}")
    print(f"\n{BOLD}Top 3:{OFF}")
    print("  1 Rich-only (winner: keeps nvim handoff)")
    print("  2 keep-stdlib _fit() fix (zero-risk)")
    print("  3 Rich+prompt_toolkit (best UX)")
    print(f"{DIM}out: Textual (event loop), ratatui-py (alpha),{OFF}")
    print(f"{DIM}urwid (LGPL+256c), curses (pain){OFF}")
    _print_notes("lane1")
    pause(section="lane1")


def streak_pulse(line: str) -> None:
    """Single-row pulse 4x90ms when tty; single print otherwise."""
    if not ANIM_OK:
        print(f"{BOLD}{line}{OFF}")
        return
    for _ in range(4):
        sys.stdout.write("\r" + f"{BOLD}{line}{OFF}")
        sys.stdout.flush()
        time.sleep(0.09)
        sys.stdout.write("\r" + f"{DIM}{line}{OFF}")
        sys.stdout.flush()
        time.sleep(0.09)
    print("\r" + f"{BOLD}{line}{OFF}")


# ---------------------------------------------------------------- Lane 1
LIBS: list[tuple[str, str, str, str, str]] = [
    ("Rich\nMIT", "excellent\nConsole(width) inline",
     "Live+Progress\ndirty redraw", "one pip install\nNO_COLOR-safe",
     "ADOPT render"),
    ("keep-stdlib\n(no dep)", "perfect\ncurrent reflow",
     "sleep+clear\npreview ~3771", "zero install\ntextwrap tax #3/#5/#11",
     "KEEP fallback"),
    ("prompt_toolkit\nBSD", "excellent\ninline, no altscreen",
     "none\n+pairs w/ Live", "fixes input()\n:466 :942\n2nd API",
     "ADOPT input"),
    ("blessed\nMIT", "good inline\nno layout eng.", "none",
     "tiny weight\ntiny payoff", "ok cleanup"),
    ("Textual\nMIT", "poor: altscreen\nchrome eats 4-6/24",
     "best-in-class\nfullscreen-only", "owns event loop\nslow popup start",
     "REJECT core"),
    ("ratatui\nRust MIT", "good in Rust\nrect layout", "immediate\n+TestBackend",
     "alpha py binds\nnative FFI bin", "REJECT py"),
    ("urwid\nLGPL-2.1", "medium\n256-color max", "MainLoop\n+alarms",
     "ONLY copyleft\ndated widgets", "REJECT lic"),
    ("curses\nstdlib", "medium\nmacOS+tmux pain", "manual\nnapms",
     "zero dep\nhigh complexity", "REJECT fw"),
]




# ---------------------------------------------------------------- Lane 2
def demo_lane2() -> None:
    rule("LANE 2 — color roles (one theme.py, art never colored)")
    print(f"  heading {BOLD}bold{OFF} · key {KEY}:set cc{OFF}")
    print(f"  new {YELLOW}{BOLD}★ NEW{OFF} · ok {GREEN}{BOLD}✓{OFF} · "
          f"fail {RED}{BOLD}✗{OFF} · meta {DIM}dim{OFF}")
    print(f"  {DIM}NO_COLOR/dumb -> blank; art never styled{OFF}")
    _print_notes("lane2")
    pause(section="lane2")

    rule("LANE 2A — minimal-stdlib lesson (zero dep)")
    print(f"M11.CUC M11 |{GREEN}██████{OFF}{DIM}░░░░{OFF}| 7/21")
    print("  Lv3 40/80 · streak 4 days")
    print(f"{YELLOW}{BOLD}★ NEW 1:{OFF} cursorcolumn is one ruler col")
    print("  MORE below has the rest")
    print(f"{BOLD}RECIPE{OFF}  {KEY}:set cursorcolumn=11{OFF}")
    print(f"{DIM}── MORE · 6 closed · za opens · / finds ── [CLOSED]{OFF}")
    print(f"{DIM}Enter close · r repeat · n next · t tree · f feedback{OFF}")
    print(f"\n{DIM}[OPEN adds: SKILL M11 · WHY prose · BUYS · KEYS ·{OFF}")
    print(f"{DIM}SOURCES · HELP · COPY/PASTE — all folded shut]{OFF}")
    print(f"{DIM}fix: lines<38 off shorten() onto :1035 wrap;{OFF}")
    print(f"{DIM}… prose NEVER, art rows only{OFF}")
    _print_notes("lane2a")
    pause(section="lane2a")

    rule("LANE 2B — Rich dashboard (stdout pages only)")
    print(f"{BOLD}PROGRESS AWARDED  M11.CUC{OFF}  {GREEN}{BOLD}+10 XP{OFF}")
    print(f"{YELLOW}{BOLD}+1 command  :set cursorcolumn{OFF}")
    print(f"Lv4 Frame Crafter {GREEN}{'█' * 6}{DIM}{'░' * 4}{OFF} 50/80")
    print("streak 4 days · best 9 · all-time 42")
    print(f"next: grid-author S0 {YELLOW}{'█' * 6}{DIM}{'░' * 3}{OFF} 15/27")
    print(f"{GREEN}▾{OFF} S0 Grid+overwrite 15/27  ← you are here")
    print(f"{DIM}▸ S1-S7 stills   ▸ A1 Extremes 6/7   ▸ P ShiftJIS 0/8{OFF}")
    print(f"{DIM}brief stays stdlib — Rich never in nvim/keylog;{OFF}")
    print(f"{DIM}plain fallback if import fails{OFF}")
    _print_notes("lane2b")
    pause(section="lane2b")

    rule("LANE 2C — playful ASCII-frame wrong-answer (zero dep)")
    w = term_w()
    inner = w - 6
    MAG = MAGENTA
    rows = [
        "%sM11.CUC - Missile redraw - no progress awarded%s" % (BOLD, OFF),
        "%sYOUR ANSWER%s  VIM: %s:%s%s...%s%ss%s/%s-%s/%s=%s/%sg%s" % (BOLD, OFF, GREEN, OFF, RED, OFF, GREEN, DIM, GREEN, DIM, GREEN, DIM, GREEN, OFF),
        "%skeys:%s %s: ok%s | %s4,6 MISSING%s | %ss/-/-/g ok%s" % (DIM, OFF, GREEN, OFF, RED, OFF, GREEN, OFF),
        "%sWHY%s  no range = this line only; tower needs 4-6" % (DIM, OFF),
        "%sCORRECT%s  VIM: %s:%s%s4,6%s%ss%s/%s-%s/%s=%s/%sg%s" % (BOLD, OFF, GREEN, OFF, YELLOW, OFF, GREEN, DIM, GREEN, DIM, GREEN, DIM, GREEN, OFF),
        BOLD + "CONCEPT" + OFF + "  " + DIM + ":" + OFF + YELLOW + "{where}" + OFF + GREEN + "s" + OFF + DIM + "/" + OFF + CYAN + "{find}" + OFF + DIM + "/" + OFF + GREEN + "{replace}" + OFF + DIM + "/" + OFF + MAG + "{flags}" + OFF,
        "  range %s4,6%s  find %s-%s  repl %s=%s  flag %sg%s" % (YELLOW, OFF, CYAN, OFF, GREEN, OFF, MAG, OFF),
        "%s%sX%s 4  YOUR %s--%sx  TARGET %s==%sx" % (RED, BOLD, OFF, RED, OFF, GREEN, OFF),
        "  3  %s(unchanged row 3, dim)%s" % (DIM, OFF),
        "DO THIS  compare YOURS with TARGET (X = row differs)",
        "DO THIS  compare YOURS with TARGET (X = row differs)",
        f"YOUR ANSWER  VIM: {RED}:s/-/=/g{OFF}",
        "WHY IT MISSES  no range = this line only; tower needs 4-6",
        f"CORRECT ANSWER  VIM: {GREEN}:4,6s/-/=/g{OFF}",
        "CONCEPT  :{where}s/{find}/{replace}/{flags}; range picks lines",
    ]
    print("." + "-" * (inner + 2) + ".")
    for r in rows:
        print(f"| {r[:inner].ljust(inner)} |")
    print("'" + "-" * (inner + 2) + "'")
    print(f"{DIM}resize: 80x24 stacked+minimal+MORE closed{OFF}")
    print(f"{DIM}100x36 side-by-side · 188x49 full+WHY open{OFF}")
    print(f"{DIM}>=120 cols: vertical nvim split{OFF}")
    _print_notes("lane2c")
    pause(section="lane2c")


# ---------------------------------------------------------------- Lane 3
def demo_lane3() -> None:
    rule("LANE 3A — skill tree, --tree (current stage expanded)")
    print(f"{BOLD}LEVEL 4 Frame Crafter  40/80 (xp//80+1){OFF}")
    print("streak 4 days · best 9 · all-time 42")
    print(f"next: grid-author S0 {YELLOW}{'█' * 6}{DIM}{'░' * 3}{OFF} 15/27")
    print(f"{GREEN}▾ S0 Grid and overwrite 15/27{OFF}  <- here")
    print("    ✓ M0.01  ✓ M0.02  ◐ M0.04  ○ M0.09")
    print(f"{DIM}▸ S1 Stroke runs ▸ S2 Hand mirror ▸ S3 Block still{OFF}")
    print(f"{DIM}▸ A0-A7 anim ▸ P Shift_JIS opt (needs S5){OFF}")
    print(f"{DIM}flags: --tree · --tree --all · --tree S3{OFF}")
    _print_notes("lane3a")
    pause(section="lane3a")

    rule("LANE 3B — skill tree in Neovim (folds = Vim practice)")
    print(f"{DIM}\" read-only tree — zo/zc/za/zR/zM · /S4 finds · q closes{OFF}")
    print(f"{GREEN}+ S0 Grid and overwrite [open] 15/27{OFF}")
    print("      M0.01  M0.02  M0.04  M0.09")
    print(f"{DIM}+ S1 [closed] + S2 [closed] + S3 [closed]{OFF}")
    print(f"{DIM}+ A0-A7 [closed] + P [closed] · manual folds{OFF}")
    print(f"{DIM}slower than --all on purpose · ~120 lines{OFF}")
    _print_notes("lane3b")
    pause(section="lane3b")

    rule("LANE 3C — viewer comparison (do A, then B, never C)")
    print("  A flags: zero dep, best 80x24 -> DO FIRST")
    print("  B folds: HIGHEST practice -> DO SECOND")
    print("  C TUI lib: NEGATIVE practice -> DO NOT DO")
    _print_notes("lane3c")
    pause(section="lane3c")

    rule("LANE 3 — levels: RUNTIME truth (xp//80+1, no gates)")
    for t in ["Apprentice", "Cell Editor", "Pose Builder", "Frame Crafter",
              "Tween Reader", "Scene Author", "Timing Artist", "Motion Editor"]:
        print(f"  {t}")
    print(f"  {DIM}… Animator, ASCII Director … (v2_runtime.py:3546 _level){OFF}")
    print(f"\n{BOLD}PROPOSAL ladder (renames + stage gates, not yet shipped):{OFF}")
    for lv, title, gate in [
        ("Lv1", "Finger-Rider", "-"), ("Lv2", "Row-Walker", "S0 learning"),
        ("Lv3", "Line-Surgeon", "S0 mastered"), ("Lv4", "Pose-Builder", "S3 mastered"),
        ("Lv5", "Frame-Crafter", "S7 still-artist"), ("Lv6", "Tween-Reader", "A2 inbetweener"),
        ("Lv7", "Loop-Director", "A7 animator"),
    ]:
        print(f"  {lv} {title:14} gate: {gate}")
    _print_notes("lane3-levels")
    pause(section="lane3-levels")

    rule("LANE 3 — badges: 8 SHIPPED + 5 proposed")
    print(f"{BOLD}shipped (v2_runtime.py:project):{OFF}")
    print("  first-step · transfer (*.06) · grid-author (S0)")
    print("  still-artist (S7) · inbetweener (A2) · timing-editor")
    print("  (A4) · animator (A7) · corpus-reader (P)")
    print(f"{BOLD}proposed (no farmables):{OFF}")
    print("  +1-command · streak-keeper 7/14/30 · branch-rescuer")
    print("  safe-ranger (:range) · midpoint-weaver (A2+review)")
    print("  %smore: method-purist comeback review-keeper marathon%s" % (DIM, OFF))
    print("  %scartographer transfer-adept clean-slate%s" % (DIM, OFF))
    print("  %seach level gets a color ASCII avatar (see STYLE)%s" % (DIM, OFF))
    _print_notes("lane3-badges")
    pause(section="lane3-badges")


# ---------------------------------------------------------------- Trophies
TROPHIES: list[tuple[str, str, list[str], str]] = [
    ("1. Bell — TROPHY (CLEARED, ship it · A7 animator)",
     "animation_lesson_pack.md:156 · pure ASCII 3x5",
     ["/--\\", "|oo|", "\\__/'"],
     "sibling signal 4x6: <++> / |  | x2 / __||__ (+anchor col)"),
    ("2. Firework radial F3 — LEVEL-UP (local-only · LEVEL :1665)",
     "FIREWORK_RADIAL_F3 · note: ¡ U+00A1, — U+2014 ambiguous",
     ["    \\¡/", "   -—*—-", "    /!\\"],
     "color: * yellow core, rays cyan, ¡/! magenta"),
    ("3. Willow canopy — CAPSTONE BURST (local-only · still-artist S7)",
     "stone_story_variants.py FIREWORK_CANOPY · pure ASCII 5x10",
     [" .''.'.''.", "  .,,*,,.", "'  .'.'. '", " ,  .  ,", "  '  .  '"],
     "color: * yellow core, , embers orange outward"),
    ("4a. Boiler flame VV — STREAK frame A (local-only · streak>=3 :1664)",
     "audit batch-0.md:480 VV frame · pure ASCII (feet \\v/ cropped)",
     [" |_/_//______|", "  VV//  //", "    \\\\  \\\\", "    /|\\ /|\\"],
     "flicker A->B is 6G3|Rvv, 2 cells"),
    ("4b. Boiler flame vv — STREAK frame B (the loop IS the lesson)",
     "audit batch-0.md:466 frame-B · alternate popups for flicker",
     [" |_/_//______|", "  vv//  //", "    \\\\  \\\\", "    /|\\ /|\\"],
     "color: VV bright orange/red, vv dim red"),
    ("5a. Pallas calm ghost — BRANCH-RESCUE (local-only · M11.UT g-/g+)",
     "PALLAS_GHOST_LEFT_CALM · note: ‾ U+203E, ´ U+00B4",
     ["    .-.", "   (- -)", "   \\ ‾ `-´", "    ) /", "    |/", "    '"],
     "rescued branch = rescued spirit"),
    ("5b. Pallas strain ghost — expression swap (local-only)",
     "stone_story_variants.py PALLAS_GHOST_LEFT_STRAIN",
     ["    .-.", "   (> <)", "   \\ ‾ `-´", "    \\ /", "    '/", "    !"],
     "flash strain first, resolve to calm"),
    ("6. Skully idle — FRAME-COPY (local-only · M11.02 gg3yyGp)",
     "stone_story_variants.py SKULLY_IDLE :45/:317 · pure ASCII 3x10",
     ["     ,--.", "    (_o,o)", "      `\"´"],
     "color: o,o yellow, skull white-bold"),
    ("7. Cheer — FIRST-PASS (DO-NOT-USE, rights unverified)",
     "art.json cheer:860 · author/license unknown, tre sig dropped",
     [' \\(")/', " -( )-", " /(_)\\"],
     "3x6 smallest banner · needs rights research"),
    ("7b. Candle — ALT (DO-NOT-USE, same class as cheer)",
     "art.json candle · ~/Downloads/ant.txt, license unknown",
     ["        \\O/", "       '-O-'", "        /o\\", "         ^"],
     "4x12 streak-flame alternative"),
    ("8a. Snowman cheer — MASTERY (local-only · new_unlocks :2915)",
     "stone_story_variants.py SNOWMAN_CHEER_CROP · pure ASCII 3x11",
     ["    __", "  _|__|_", ". ( ^,^) ,."],
     "first-pass (#7) vs mastery (#8) pairing"),
    ("8b. Snowman blink — frame swap (local-only)",
     "stone_story_variants.py SNOWMAN_BLINK_CROP · ^,^ -> -,-",
     ["    __", "  _|__|_", ". ( -,-) ,."],
     "2-cell swap = frame-copy lesson"),
]


def demo_trophies() -> None:
    rule("ARCHIVED ASCII — unlock banners (80x24-safe)")
    for title, prov, art, note in TROPHIES:
        print(f"\n{BOLD}{title}{OFF}\n{DIM}{prov}{OFF}")
        for r in art:
            print(f"  {r}")
        print(f"  {DIM}{note}{OFF}")
    print(f"\n{DIM}rights: #1 CLEARED shippable · locals preview-only{OFF}")
    print(f"{DIM}Stone Story: no push · art.json DO-NOT-USE{OFF}")
    _print_notes("trophies")
    pause(section="trophies")




# ------------------------------------------------- STYLE + viewer
def demo_style():
    rule("STYLE — tiers + 3 avatar options per level (PICK=ship)")
    print("  roles: heading BOLD key 1;36 new YELLOW ok GREEN")
    print("  fail RED tokens only CONCEPT CYAN flags MAGENTA")
    print("  mine: art.json walk/hands/seam/sparks (motifs only,")
    print("  shapes stay invented = rights-cleared like bell)")
    for lv, tier, options in AVATAR_OPTIONS:
        print("  %s%s [%s]%s" % (BOLD, lv, tier, OFF))
        for name, art in options:
            c = {"bronze": BRONZE or YELLOW, "gold": GOLD or YELLOW}.get(tier, "")
            tag = " <== PICK" if "PICK" in name else ""
            print("    %s%s%s%s" % (DIM, name, tag, OFF))
            for r in art:
                line = "      " + r
                if tier == "gemini":
                    print("      " + gemini_text(line.strip(), 0.10))
                else:
                    print("    %s%s%s" % (c, line, OFF))
    print("  Lv1-2 kept (pebble/strider, beg, no color)")
    print("  %schecks green / +1 green / fire streak>=3 [hot]%s" % (GREEN, OFF))
    print("  high score: BOLD+pulse glow, fallback NEW BEST tag")
    _print_notes("style")
    pause(section="style")


AVATAR_OPTIONS = [
    ("Lv3 Line-Surgeon", "bronze", [
        ("3A scissors", [" o   ", "8<---", " o   "]),
        ("3B needle+suture PICK", ["  /o ", " / / ", "x-x-x"]),
        ("3C sampler", [".-.-.", "|x+x|", "'-+-'"])]),
    ("Lv4 Pose-Builder", "bronze", [
        ("4A set-square PICK", ["+-o  ", "|/|  ", "|/\\  "]),
        ("4B before/after", ["o o  ", "|\\|/ ", "/\\/\\ "]),
        ("4C mannequin", ["  o  ", " .|. ", "./.\\ "])]),
    ("Lv5 Frame-Crafter", "gold", [
        ("5A weave PICK", ["+---+", "|:x:|", "+---+"]),
        ("5B loom warp", ["|-|-|", "o-+-o", "|-|-|"]),
        ("5C bevel", ["/---\\", "| o |", "\\---/"])]),
    ("Lv6 Tween-Reader", "gold", [
        ("6A wave-rider PICK", ["~o~~~", "~~o~~", "~~~o~"]),
        ("6B lens", [" __  ", "/o\\~~", "\\_/~~"]),
        ("6C onion-skin", ["o . o", " .o. ", "o . o"])]),
    ("Lv7 Loop-Director", "gemini", [
        ("7A clapper PICK", ["|\\==\\", "|/__/", "  |  "]),
        ("7B knot loop", [" (o) ", "/(+)\\", " \\_/ "]),
        ("7C megaphone", ["  _   ", "o|_\\  ", " |__/ "])]),
]


def demo_avatars():
    rule("AVATARS — 3 options per level (Lv1-2 kept, pick marked)")
    for lv, tier, options in AVATAR_OPTIONS:
        print("  %s%s [%s]%s" % (BOLD, lv, tier, OFF))
        for name, art in options:
            c = {"bronze": BRONZE or YELLOW, "gold": GOLD or YELLOW}.get(tier, "")
            print("    %s%s%s" % (DIM, name, OFF))
            for r in art:
                line = "      " + r
                print("      " + (gemini_text(line, 0.10) if tier == "gemini" else "%s%s%s" % (c, line.strip(), OFF)))
    _print_notes("avatars")
    pause(section="avatars")


def fx_combo(name):
    combos = {
        "mastery": [fx_ember, fx_confetti, fx_sparkle],
        "miss": [fx_border, lambda: fx_shake()],
        "award": [fx_bar_sweep, fx_sparkle],
        "levelup": [lambda: scanline_banner(["  LEVEL UP"]), fx_flicker],
    }
    for fn in combos.get(name, [fx_sparkle]):
        fn()
        if ANIM_OK:
            time.sleep(0.05)


def demo_viewer():
    rule("VIEWER — post-exercise animation (pass -> YOURS -> party)")
    print("  flow: pass -> YOURS static -> combo -> progress -> latch")
    print("  YOURS -- M11.CUC tower (3 frames x 5 rows, verbatim)")
    print("  combo full only: border 240 + scan 330 + sparkle 320")
    print("  + confetti iff unlock 320 + flicker iff streak>=3 360")
    print("  + typewriter next 300: typical 1190 worst 1870<=2000")
    print("  gates: off|static|full MS=2000 any-key skip")
    print("  fail/concept/review: NO viewer · seam play_art(rows)")
    print("  test: static golden YOURS + final rows before latch")
    fx_combo("levelup")
    _print_notes("viewer")
    pause(section="viewer")


# ------------------------------------------------- ANIM catalog D-O
def _frames_or_static(frames, static):
    if not ANIM_OK:
        for r in static:
            print(r)
        return False
    return True


def fx_sparkle(line="grid-author: master S0"):
    """ANIM badge sparkle: * particles pop then fade (5x80ms=400ms)."""
    if not _frames_or_static(None, ["[NEW] " + line]):
        return
    for i in range(5):
        stars = "*" * (3 - abs(2 - i)) + "·" * abs(2 - i)
        print("  %s %s" % (line, stars))
        time.sleep(0.08)


def fx_bar_sweep(label="Lv4 Frame Crafter", have=5, total=8):
    """ANIM progress sweep L->R over track (6x60ms=360ms)."""
    full = ["  %s %s%s %d/%d" % (label, "█" * (have + 1 if have + 1 <= total else total),
                                 "░" * (total - have - 1 if have + 1 <= total else 0), have + 1, 80)]
    if not ANIM_OK:
        print(full[0])
        return
    for f in range(6):
        n = min(total, max(0, have - 2 + f))
        print("  %s %s%s" % (label, "█" * n, "░" * (total - n)))
        time.sleep(0.06)
    print(full[0])


def fx_flicker():
    """ANIM boiler VV/vv 2-frame swap (4x90ms=360ms). IS the loop lesson."""
    a = [" |_/_//______|", "  VV//  //"]
    b = [" |_/_//______|", "  vv//  //"]
    if not ANIM_OK:
        print("  %s (flicker VV/vv static)" % a[1].strip())
        return
    for i in range(4):
        for r in (a if i % 2 == 0 else b):
            print("  " + r)
        time.sleep(0.09)


def fx_blink():
    """ANIM frame-copy blink ^,^ <-> -,- (2x150ms+200ms=500ms)."""
    a, b = ". ( ^,^) ,.", ". ( -,-) ,."
    if not ANIM_OK:
        print("  " + a + " (blink static)")
        return
    print("  " + a)
    time.sleep(0.15)
    print("  " + b)
    time.sleep(0.20)


def fx_ghost():
    """ANIM branch-rescue: strain DIM -> calm BOLD (2x100+300=500ms)."""
    if not ANIM_OK:
        print("  (ghost calm static)")
        return
    print("%s   (> <) strain — abandoned take%s" % (DIM, OFF))
    time.sleep(0.10)
    print("   (- -) calm — rescued via g-/g+")
    time.sleep(0.30)


def fx_confetti():
    """ANIM victory fall: particles lean 1 col/row (6x80ms=480ms)."""
    if not ANIM_OK:
        print("  *** VICTORY ***")
        return
    for f in range(4):
        pad = " " * f
        print("  %s. * ' . *'" % pad)
        time.sleep(0.08)
    print("  *** VICTORY ***")


def fx_ember():
    """ANIM mastery rise: , embers rise from * core (6x80ms=480ms)."""
    rows = ["  .,,*,,.", "  .,,*,,.", "   , * ,"]
    if not ANIM_OK:
        for r in rows[:1]:
            print(r)
        return
    for i in range(3):
        print(rows[i % len(rows)] + " rise %d" % i)
        time.sleep(0.08)


def fx_typewriter(line="RECIPE  :set cursorcolumn=11"):
    """ANIM typewriter chunked 8 chars/frame (8x60ms=480ms)."""
    if not ANIM_OK:
        print("  " + line)
        return
    for i in range(8, len(line) + 8, 8):
        print("\r  " + line[:i])
        time.sleep(0.06)
    print("  " + line)


def fx_border():
    """ANIM border-draw: top, sides, bottom (4x80ms=320ms)."""
    w = min(40, term_w() - 4)
    if not ANIM_OK:
        print("  ." + "-" * w + ".")
        print("  | miss: no range |")
        print("  '" + "-" * w + "'")
        return
    print("  ." + "-" * w + ".")
    time.sleep(0.08)
    print("  | YOUR :s/-/=/g | CORRECT :4,6s |")
    time.sleep(0.08)
    print("  '" + "-" * w + "'")
    time.sleep(0.08)


def fx_wipe():
    """ANIM wipe: rows appear top->bottom (5x60+150=450ms)."""
    rows = ["  S0 done", "  S1 done", "  S3 learning", "  A0 locked"]
    if not ANIM_OK:
        for r in rows:
            print(r)
        return
    for i in range(len(rows)):
        for j, r in enumerate(rows):
            print(r if j <= i else "%s%s%s" % (DIM, "." * len(r), OFF))
        time.sleep(0.06)
    time.sleep(0.15)


def fx_hint():
    """ANIM hint fade BOLD->DIM->BOLD (4x80ms=320ms)."""
    line = "  -- MORE closed: za opens, / finds --"
    if not ANIM_OK:
        print(line)
        return
    for i in range(4):
        print("%s%s%s" % (BOLD if i % 2 == 0 else DIM, line, OFF))
        time.sleep(0.08)


def fx_shake(line="  X row 3 differs: no range = this line only"):
    """ANIM shake: 0/1-space nudge reprints (4x70ms=280ms)."""
    if not ANIM_OK:
        print(line)
        return
    for i in range(4):
        print((" " if i % 2 else "") + line)
        time.sleep(0.07)


def fx_twinkle():
    """ANIM +1-command twinkle: star BOLD/DIM (4x90ms=360ms)."""
    line = "  * NEW +1 command  :set cursorcolumn"
    if not ANIM_OK:
        print(line)
        return
    for i in range(4):
        print("%s%s%s" % (BOLD if i % 2 == 0 else DIM, line, OFF))
        time.sleep(0.09)


def fx_throbber():
    """ANIM loading throbber: braille cycle (6x80ms=480ms)."""
    glyphs = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴"]
    if not ANIM_OK:
        print("  ... loading")
        return
    for g in glyphs:
        print("\r  %s starting up" % g, end="")
        time.sleep(0.08)
    print("\r  done          ")


def demo_anims2():
    rule("ANIM D-O — 14-effect catalog (each <=1s, <=5 rows)")
    for title, fn in [
        ("D badge sparkle (:2915 unlock)", fx_sparkle),
        ("E progress sweep (:1666 PROGRESS)", fx_bar_sweep),
        ("F boiler flicker (streak>=3 :1664)", fx_flicker),
        ("G frame-copy blink (M11.02 gg3yyGp)", fx_blink),
        ("H ghost-fade rescue (M11.UT g-/g+)", fx_ghost),
        ("I victory confetti (stage unlock)", fx_confetti),
        ("J mastery ember-rise (S7 still-artist)", fx_ember),
        ("K typewriter recipe reveal", lambda: fx_typewriter()),
        ("L border-draw wrong-answer frame", fx_border),
        ("M wipe section transition", fx_wipe),
        ("N hint fade (MORE closed)", fx_hint),
        ("O shake miss nudge", lambda: fx_shake()),
        ("P +1-command twinkle", fx_twinkle),
        ("Q loading throbber (real waits only)", fx_throbber),
    ]:
        print("\n%s%s%s" % (BOLD, title, OFF))
        fn()
    _print_notes("animd")
    pause(section="animd")


# ---------------------------------------------------------------- Anim
def demo_anim() -> None:
    rule("ANIM A — rainbow scanline level-up (~330ms, stdlib only)")
    print(f"{DIM}hue=(col/w+phase)%1 (rainbow:60) + white lead t=0.40{OFF}")
    print(f"{DIM}(scanline:33); sequential here, no cursor addressing{OFF}")
    scanline_banner(["  LEVEL UP  Lv4 Frame Crafter",
                     "  /--\\  |oo|  \\__/'",
                     "  +1 command  :set cursorcolumn"])
    _print_notes("anima")
    pause(section="anima")

    rule("ANIM B — streak pulse (~360ms, one row, scale_v analogue)")
    streak_pulse("streak 4 days · best 9 · all-time 42")
    _print_notes("animb")
    pause(section="animb")

    rule("ANIM C — static-gradient fallback (zero ticks)")
    print(f"{DIM}forced by --no-anim/NO_COLOR/dumb/CI/non-tty;{OFF}")
    print(f"{DIM}gate vim-daily-gate:78 must learn NO_COLOR too{OFF}")
    print(rainbow_text("  LEVEL UP  Lv4 Frame Crafter (frozen phase)", 0.10))


def main() -> None:
    args = sys.argv
    if "--help" in args:
        print("usage: demo_ui_proposals.py [--auto] [--no-anim]")
        print("  --notes             list all stored notes")
        print("  --note ID \"text\"    add note to section ID")
        print("  --notes-file PATH   redirect note store")
        print("slots: " + " ".join(SECTIONS))
        print("trophy: " + " ".join(TROPHY_SLOTS))
        print("keys: any=next n=note v=view q=quit")
        return
    if "--note" in args:
        i = args.index("--note")
        if i + 2 >= len(args):
            print('usage: --note ID "text"', file=sys.stderr)
            sys.exit(2)
        _add_note(args[i + 1], args[i + 2])
        return
    if "--notes" in args:
        notes = _load_notes(_notes_path())
        empty = True
        for sid in list(SECTIONS) + list(TROPHY_SLOTS):
            for n in notes.get(sid, []):
                empty = False
                print("%s: %s" % (sid, n.get("text", "")))
        if empty:
            print("no notes yet")
        return
    w = term_w()
    print(f"{BOLD}UI proposal demo — {w} cols, "
          f"{'static (pipe/CI/NO_COLOR/no-anim)' if not ANIM_OK else 'animated'}{OFF}")
    print(f"{DIM}watchdogcannonical.py: NOT-FOUND (searched asciicker-Y9-2){OFF}")
    print(f"{DIM}analogues: anim_B_rainbow.py + anim_D_scanline.py{OFF}")
    print(f"{DIM}on _common.py (hue wave, white blend, 40ms ticks){OFF}")
    try:
        demo_lane1()
        demo_lane2()
        demo_lane3()
        demo_trophies()
        demo_anim()
        demo_style()
        demo_avatars()
        demo_anims2()
        demo_viewer()
    except KeyboardInterrupt:
        sys.exit(130)
    rule("END — A(stdlib+flags+bell) -> C-frames -> B-folds -> Rich")


if __name__ == "__main__":
    main()
