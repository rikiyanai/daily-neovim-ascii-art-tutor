"""VD-58: the interactive dashboard (share/dashboard_tui.py).

Headless Textual Pilot at 80x24: fold/unfold a stage (za/zo/zc/zR/zM), move
with j/k, open a module with Enter, search with /, send feedback with f, quit
with q; no row wider than the pane. A real pty run proves NO_COLOR emits no
ANSI colour while the default run does. Also checks the gate fallback: a
non-terminal `--tree` / `--dashboard` prints the static text tree.

Needs Textual: when this interpreter lacks it, the test re-runs itself with
the managed venv python from install.sh, or reports SKIP when that is absent.
"""
import asyncio
import datetime as dt
import json
import os
import re
import select
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

try:
    import textual  # noqa: F401
except ImportError:
    import v2_runtime as _v2
    python = _v2.dashboard_python()
    # The venv python is a symlink to the same binary, so compare the flag,
    # not the resolved path.
    if python and not os.environ.get("VIM_DAILY_DASHBOARD_TEST_REEXEC"):
        sys.exit(subprocess.call([python, __file__, *sys.argv[1:]],
                                 env=dict(os.environ, VIM_DAILY_DASHBOARD_TEST_REEXEC="1")))
    print("SKIP test_dashboard_tui: Textual venv missing (run install.sh)")
    sys.exit(0)

import dashboard_tui as D  # noqa: E402
import dashboard_theme as TH  # noqa: E402
import v2_runtime as v2  # noqa: E402

cur = v2.load_curriculum(str(HERE))
S0 = next(s for s in cur["stages"] if s["id"] == "S0")


def make_state(root):
    """Synthetic learner: 12 S0 lessons passed today, one sent back, 3-day streak."""
    now = v2._now()
    rows = []
    for cid in S0["card_ids"][:12]:
        rows.append({"type": "card", "result": "pass", "card_id": cid,
                     "at": now.isoformat(), "attempts": 1})
    rows.append({"type": "card", "result": "fail", "card_id": S0["card_ids"][12],
                 "at": now.isoformat()})
    rows.append({"type": "remediation_scheduled", "card_id": S0["card_ids"][1],
                 "changed_variant": "edit", "at": now.isoformat()})
    Path(root, "events-v2.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    for back in range(3):
        day = (now.date() - dt.timedelta(days=back)).isoformat()
        Path(root, day + ".log").write_text("drill\n", encoding="utf-8")


def node_kind(node):
    return node.data[0] if node is not None and node.data else None


async def pilot_run(state):
    model = D.build_model(state, HERE, target=12)
    app = D.make_app(model, state=state, animate=False, colour=True)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        tree = app.query_one("#tree")
        # Opens on the current stage with the current module under the cursor.
        stage_nodes = list(tree.root.children)[:len(cur["stages"])]
        s0 = stage_nodes[0]
        assert s0.data[1]["id"] == "S0" and s0.is_expanded
        assert all(not n.is_expanded for n in stage_nodes[1:])
        assert node_kind(tree.cursor_node) == "module", tree.cursor_node

        # j / k move.
        line = tree.cursor_line
        await pilot.press("j")
        assert tree.cursor_line == line + 1
        await pilot.press("k")
        assert tree.cursor_line == line

        # zc on a module closes its parent stage fold only when it is a leaf;
        # on the stage row za toggles.
        tree.move_cursor(s0)
        await pilot.pause()
        await pilot.press("z", "a")
        assert not s0.is_expanded
        await pilot.press("z", "o")
        assert s0.is_expanded
        await pilot.press("z", "c")
        assert not s0.is_expanded
        await pilot.press("z", "R")
        assert all(n.is_expanded for n in stage_nodes)
        await pilot.press("z", "M")
        assert all(not n.is_expanded for n in tree.root.children)
        # "z" alone followed by an unrelated key does not fold anything.
        await pilot.press("z", "x")
        assert not s0.is_expanded

        # Enter on a stage toggles it; Enter on a module opens its page.
        tree.move_cursor(s0)
        await pilot.pause()
        await pilot.press("enter")
        assert s0.is_expanded
        await pilot.press("j")
        assert node_kind(tree.cursor_node) == "module"
        await pilot.press("enter")
        await pilot.pause()
        page = app.screen
        assert type(page).__name__ == "Page", page
        body = page.query("Static").first().render()
        assert "lessons" in str(body)
        await pilot.press("escape")
        await pilot.pause()
        assert app.screen is not page

        # 80x24: nothing is wider than the pane.
        await pilot.press("z", "R")
        await pilot.pause()
        assert tree.virtual_size.width <= tree.size.width, (tree.virtual_size, tree.size)
        for widget_id in ("line1", "line2", "line3", "map", "keys"):
            widget = app.query_one("#" + widget_id)
            rendered = widget.render()
            width = getattr(rendered, "cell_len", None)
            if width is None:
                width = len(str(rendered))
            assert widget.region.right <= 80 and width <= widget.size.width, widget_id

        # / search moves to the match and opens its parents.
        await pilot.press("z", "M", "slash")
        for ch in "stroke runs":
            await pilot.press("space" if ch == " " else ch)
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()
        assert node_kind(tree.cursor_node) == "stage"
        assert tree.cursor_node.data[1]["id"] == "S1", tree.cursor_node.data

        # ? help, closed with q (q on a page closes the page, not the app).
        await pilot.press("question_mark")
        await pilot.pause()
        assert type(app.screen).__name__ == "Page"
        await pilot.press("q")
        await pilot.pause()
        assert type(app.screen).__name__ != "Page"

        # f feedback writes the shared feedback store with screen=dashboard.
        await pilot.press("f")
        await pilot.pause()
        for ch in "tree ok":
            await pilot.press("space" if ch == " " else ch)
        await pilot.press("enter")
        await pilot.pause()
        rows = [json.loads(x) for x in
                v2.feedback_path(state).read_text(encoding="utf-8").splitlines()]
        assert rows[-1]["message"] == "tree ok" and rows[-1]["screen"] == "dashboard", rows

        # q quits.
        await pilot.press("q")
        await pilot.pause()
    assert app.return_code in (0, None) and not app.is_running
    return model


def pty_capture(state, env_extra, seconds=3.0):
    """Run the app in a real 80x24 pty; return every byte it wrote."""
    import fcntl
    import pty
    import struct
    import termios
    env = dict(os.environ)
    env.pop("NO_COLOR", None)
    env.update({"TERM": "xterm-256color", "COLUMNS": "80", "LINES": "24"}, **env_extra)
    pid, fd = pty.fork()
    if pid == 0:
        os.execve(sys.executable, [sys.executable, str(HERE / "dashboard_tui.py"),
                                   "--state", state, "--share", str(HERE)], env)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
    out = b""
    deadline = time.time() + seconds
    sent_q = False
    while True:
        if time.time() > deadline and not sent_q:
            os.write(fd, b"q")
            sent_q = True
            deadline = time.time() + 3
        elif time.time() > deadline:
            break
        ready, _w, _x = select.select([fd], [], [], 0.1)
        if ready:
            try:
                chunk = os.read(fd, 65536)
            except OSError:
                break
            if not chunk:
                break
            out += chunk
    try:
        os.kill(pid, 9)
    except ProcessLookupError:
        pass
    os.waitpid(pid, 0)
    os.close(fd)
    return out.decode("utf-8", "replace")


COLOUR_SGR = re.compile(r"\x1b\[([0-9;]*)m")


def colour_params(text):
    found = set()
    for params in COLOUR_SGR.findall(text):
        parts = params.split(";")
        i = 0
        while i < len(parts):
            p = parts[i]
            if p in ("38", "48"):
                found.add(";".join(parts[i:i + 5]))
                break
            if p.isdigit() and (30 <= int(p) <= 37 or 40 <= int(p) <= 47
                                or 90 <= int(p) <= 97 or 100 <= int(p) <= 107):
                found.add(p)
            i += 1
    return found


def main():
    with tempfile.TemporaryDirectory() as root:
        state = str(Path(root, "vim-daily"))
        os.makedirs(state)
        make_state(state)
        model = D.build_model(state, HERE, target=12)
        # Model: same projection as print_tree, plus dashboard badges.
        assert model["progress"] == v2.project(cur, v2.read_events(
            type("C", (), {"state": state})()))
        assert len(model["strip"]) == 14 and model["strip"][-1][1]
        assert model["streak"] == 3 and model["personal_best"]
        assert model["today"] == 12
        ids = {b["id"] for b in model["badges"] if b["earned"]}
        assert {"first-step", "full-day"} <= ids, ids
        assert "streak-keeper-7" not in ids and len(model["badges"]) >= 20
        assert model["next_badge"] and not model["next_badge"]["earned"]
        assert model["tier"]["id"] == "beginner" and model["avatar"]
        assert D.TH.tier_for_level(4)["id"] == "intermediate"
        assert D.TH.tier_for_level(8)["id"] == "advanced"
        assert D.TH.tier_for_level(12)["gradient"]
        # Animations: off under NO_COLOR, TERM=dumb, VIM_DAILY_ANIM=off.
        assert not D.animations_enabled({"TERM": "xterm", "NO_COLOR": "1"})
        assert not D.animations_enabled({"TERM": "dumb"})
        assert not D.animations_enabled({"TERM": "xterm", "VIM_DAILY_ANIM": "off"})
        assert D.animations_enabled({"TERM": "xterm-256color"})
        # Every ✓ and "+N" is the ok (green) style in labels and header.
        label = D.node_label("command", ("x", "delete", 2, "M0.01"), 60)
        assert any(span.style == D.TH.STYLE["ok"] and label.plain[span.start:span.end] == "✓ "
                   for span in label.spans)

        asyncio.run(pilot_run(state))
        print("ok pilot 80x24: j/k, za/zo/zc/zR/zM, Enter page, / search, ? help, f, q")

        coloured = pty_capture(state, {})
        plain = pty_capture(state, {"NO_COLOR": "1"})
        def text_of(raw):
            return re.sub(r"\x1b\[[0-9;?<>=$]*[A-Za-z~]|\x1b\][^\x07]*\x07", "", raw)
        assert "Lv2 Cell Editor" in text_of(coloured), text_of(coloured)[:400]
        assert colour_params(coloured), "control run showed no colour"
        assert "Lv2 Cell Editor" in text_of(plain), text_of(plain)[:400]
        leaked = colour_params(plain)
        assert not leaked, "NO_COLOR run emitted colour SGR: %s" % sorted(leaked)[:10]
        print("ok NO_COLOR pty: no colour SGR (control run had %d)" % len(colour_params(coloured)))

        # Gate route: non-terminal --tree and --dashboard keep the static text.
        env = dict(os.environ, XDG_STATE_HOME=root, VIM_DAILY_SKIP="1")
        for args in (["--tree"], ["--dashboard"], ["--tree", "--static"]):
            out = subprocess.run([sys.executable, str(REPO / "bin" / "vim-daily-gate"), *args],
                                 capture_output=True, text=True, env=env, timeout=60,
                                 stdin=subprocess.DEVNULL)
            assert out.returncode == 0, out.stderr
            assert "YOUR JOURNEY" in out.stdout, (args, out.stdout[:300])
        print("ok non-tty --tree / --dashboard / --tree --static print the static tree")
    # VD-60: every trophy page shows its art and names who made it.
    for badge in TH.BADGES:
        trophy = TH.trophy_for(badge["id"])
        if not trophy:
            continue
        for earned in (True, False):
            row = dict(badge, have=0, need=badge.get("need", 1), earned=earned)
            page = D.badge_detail(None, row).plain
            assert trophy["art"][0].rstrip() in page, badge["id"]
            assert trophy["credit"] in page, badge["id"]
        if trophy["source"].startswith("official-"):
            assert "Stone Story RPG" in trophy["credit"] and "Gabriel Santos" in trophy["credit"]
    print("ok trophy pages show art and credit")
    print("test_dashboard_tui: all passed")


if __name__ == "__main__":
    main()
