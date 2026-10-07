"""Actual gate + Textual + Neovim PTY routes in isolated learner state.

Mount records come from after-refresh callbacks, never screenshots or injected
grade/receipt data. This is terminal-app proof, not a Ghostty graphics claim.
"""
import fcntl
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import pty
import select
import struct
import subprocess
import sys
import tempfile
import termios
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PYTHON = Path.home() / ".local/share/vim-daily-venv/bin/python"


def write_json(path, value):
    """Publish a complete read-only observation inside the isolated fixture."""
    path = Path(path)
    staging = path.with_suffix(path.suffix + ".pending")
    staging.write_text(json.dumps(value, default=vars), encoding="utf-8")
    staging.replace(path)

if "--dashboard-child" in sys.argv:
    spec = importlib.util.spec_from_file_location("observed_dashboard", HERE / "dashboard_tui.py")
    dashboard = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = dashboard
    spec.loader.exec_module(dashboard)
    original_make = dashboard.make_app
    def observed_make(*args, **kwargs):
        app = original_make(*args, **kwargs)
        original_mount = type(app).on_mount
        def on_mount(self):
            original_mount(self)
            self.call_after_refresh(lambda: write_json(os.environ["VIM_DAILY_TEST_DASHBOARD"],
                {"columns": self.size.width, "rows": self.size.height}))
        type(app).on_mount = on_mount
        return app
    dashboard.make_app = observed_make
    raise SystemExit(dashboard.main(sys.argv[2:]))

if "--child" in sys.argv:
    loader = importlib.machinery.SourceFileLoader("textual_route_gate", str(ROOT / "bin/vim-daily-gate"))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    gate = importlib.util.module_from_spec(spec)
    loader.exec_module(gate)
    runtime = gate.load_v2_runtime()
    gate.load_v2_runtime = lambda: runtime
    original_call = runtime.subprocess.call
    def observed_call(argv, *args, **kwargs):
        if len(argv) > 1 and Path(argv[1]).name == "dashboard_tui.py":
            # Only add an after-refresh observer to the actual dashboard app.
            # Model, widgets, keys and subprocess boundary remain unchanged.
            argv = [argv[0], __file__, "--dashboard-child", *argv[2:]]
        return original_call(argv, *args, **kwargs)
    runtime.subprocess.call = observed_call
    surface = runtime._lesson_tui()
    original_show = surface.show
    original_make_app = surface.make_app
    frame_path = Path(os.environ["VIM_DAILY_TEST_FRAMES"])
    observed_frames = []
    def observed_make_app(*args, **kwargs):
        app = original_make_app(*args, **kwargs)
        original_mount = getattr(type(app), "on_mount", None)
        def observe_frame():
            try:
                panel = app.query_one("#result-reward-panel")
                rows = [panel.query_one("#reward-row-%d" % n).content.plain
                        for n in range(len(panel.frame_rows))]
                observed = {"index": panel.frame_index, "rows": rows}
                if not observed_frames or observed_frames[-1] != observed:
                    observed_frames.append(observed)
                    write_json(frame_path, observed_frames)
            except Exception:
                pass  # Lesson/reference pages have no reward widget.
        def on_mount(self):
            if original_mount:
                original_mount(self)
            self.set_interval(0.05, lambda: self.call_after_refresh(observe_frame))
        type(app).on_mount = on_mount
        return app
    surface.make_app = observed_make_app
    evidence = Path(os.environ["VIM_DAILY_TEST_MOUNTS"])
    mounts = []
    def observed_show(pages, *, result=False, mounted=None):
        reward = getattr(pages, "reward", None)
        observed_page = {"result": result, "pages": pages}
        if reward:
            # This is the spec produced by the actual result route.  Keep it
            # beside the list-compatible page evidence so the assertions can
            # compare raw PTY art to the mounted panel after its timer ticks.
            observed_page["reward"] = {
                "title": reward.title,
                "credit": reward.credit,
                "interval": reward.interval,
                "frames": [list(frame) for frame in reward.frames],
            }
        def painted():
            mounts.append(observed_page)
            write_json(evidence, mounts)
            if mounted:
                mounted()
        route = original_show(pages, result=result, mounted=painted)
        mounts[-1]["route"] = route
        write_json(evidence, mounts)
        return route
    surface.show = observed_show
    questions_rendered = []
    def question_rendered(question, order):
        questions_rendered.append(question["id"])
        write_json(os.environ["VIM_DAILY_TEST_QUESTION"], {
            "answer": "abcd"[order.index(question["correct_choice"])],
            "id": question["id"],
            "count": len(questions_rendered),
        })
    gate.signal_question_rendered = question_rendered
    raise SystemExit(gate.main(["--force"]))

cur = json.loads((HERE / "curriculum-v2.json").read_text())
for columns, rows in ((80, 24), (100, 36), (188, 49)):
    with tempfile.TemporaryDirectory(prefix="vim-daily-textual-routes-") as directory:
        root = Path(directory)
        state = root / "state/vim-daily"
        state.mkdir(parents=True)
        if "--first-reward" not in sys.argv:
            state.joinpath("events-v2.jsonl").write_text(json.dumps({
                "type": "card", "result": "pass", "card_id": "M0.P0", "module_id": "M0",
                "at": "2026-09-28T00:00:00-04:00",
            }) + "\n")
        mounts, question = root / "mounts.json", root / "question.json"
        dashboard_mount = root / "dashboard-mount.json"
        frame_observations = root / "frames.json"
        env = dict(os.environ, TERM="xterm-256color", XDG_STATE_HOME=str(root / "state"),
                   VIM_DAILY_TEST_MOUNTS=str(mounts), VIM_DAILY_TEST_QUESTION=str(question),
                   VIM_DAILY_TEST_DASHBOARD=str(dashboard_mount),
                   VIM_DAILY_TEST_FRAMES=str(frame_observations),
                   VIM_DAILY_CLEAN="1", VIM_DAILY_TEXTUAL="1", VIM_DAILY_POPUP="1",
                   VIM_DAILY_VIEWER="off", VIM_DAILY_NO_WARMUP="1",
                   VIM_DAILY_USE_MANAGED_RUNTIME="0", VIM_DAILY_MAX_TRIES="3")
        for name in list(env):
            if name == "TMUX" or name.startswith("VIM_DAILY_TMUX_"):
                env.pop(name)
        master, slave = pty.openpty()
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", rows, columns, 0, 0))
        child = subprocess.Popen([str(PYTHON), __file__, "--child"], env=env,
                                 stdin=slave, stdout=slave, stderr=slave)
        raw = bytearray()
        def wait_for(predicate, label):
            deadline = time.monotonic() + 12
            while time.monotonic() < deadline:
                if select.select([master], [], [], 0.05)[0]:
                    raw.extend(os.read(master, 65536))
                if predicate():
                    return
                if child.poll() is not None:
                    break
            routes = [(row["result"], row.get("route")) for row in json.loads(mounts.read_text())] if mounts.exists() else []
            raise AssertionError((columns, rows, label, child.poll(), routes, bytes(raw[-2000:])))
        def mount_count():
            return len(json.loads(mounts.read_text())) if mounts.exists() else 0
        def send(value):
            # Match ordinary human input pacing across apps whose drivers
            # hand the same PTY back to one another after their painted mount.
            select.select([], [], [], 0.2)
            os.write(master, value)
        def edit(keys):
            offset = len(raw)
            send(b"\r")
            wait_for(lambda: b"SWITCHES PANE" in raw[offset:], "actual Neovim mount")
            select.select([], [], [], 0.4)
            send(keys + b":wq\r")
        try:
            wait_for(lambda: mount_count() == 1, "first lesson")
            first = json.loads(mounts.read_text())[-1]
            if "--first-reward" in sys.argv:
                # No successful progress is seeded: the learner reaches the
                # first reward by answering the actual initial lesson.
                assert "M0.P0" in first["pages"][0][1]
                send(b"\r")
                wait_for(question.exists, "first actual conceptual question")
                result_offset = len(raw)
                send(json.loads(question.read_text())["answer"].encode() + b"\r")
                wait_for(lambda: mount_count() == 2, "first reached reward result")
                reached = json.loads(mounts.read_text())[-1]
                assert reached["result"] and reached.get("reward")
                frames = reached["reward"]["frames"]
                first_card = next(card for card in cur["cards"] if card["id"] == "M0.P0")
                assert frames == first_card["module_reward"]["frames"]
                assert len(frames) >= 8 and len({tuple(frame) for frame in frames}) >= 6
                offset = len(raw)
                def complete_cycle():
                    if not frame_observations.exists():
                        return False
                    seen = json.loads(frame_observations.read_text())
                    return {row["index"] for row in seen} >= set(range(len(frames)))
                wait_for(complete_cycle, "every authored frame on actual first result page")
                seen = json.loads(frame_observations.read_text())
                assert all(row["rows"] == frames[row["index"]] for row in seen)
                assert len({tuple(row["rows"]) for row in seen}) >= 2
                assert any(row.strip().encode("utf-8") in raw[result_offset:]
                           for frame in frames for row in frame if row.strip())
                assert b"REWARD" in raw[result_offset:]
                events = [json.loads(line) for line in state.joinpath("events-v2.jsonl").read_text().splitlines()]
                assert any(e.get("type") == "card" and e.get("card_id") == "M0.P0"
                           and e.get("result") == "pass" for e in events)
                send(b"q")
                wait_for(lambda: child.poll() is not None, "close first reward")
                assert child.returncode == 0
                print(f"PASS actual first reward M0.P0 from empty state: question/grade/result/all {len(frames)} frames {columns}x{rows}", flush=True)
                continue
            assert "M0.L0" in first["pages"][0][1]
            assert first["pages"][1][0] == "Navigation study"
            offset = len(raw)
            send(b"m")
            wait_for(lambda: b"SOURCE MOTION" in raw[offset:], "actual source-motion tab")
            edit(b"j")  # Wrong method/cursor; unchanged art cannot pass.
            wait_for(lambda: mount_count() == 2, "failed result")
            failed = json.loads(mounts.read_text())[-1]
            assert failed["result"] and failed["pages"][0][0] == "Feedback"
            assert "METHOD" in failed["pages"][0][1]
            send(b"r")
            wait_for(lambda: mount_count() == 3, "Repeat bypasses plain retry prompt")
            assert "M0.L0" in json.loads(mounts.read_text())[-1]["pages"][0][1]
            edit(b"j0")
            wait_for(question.exists, "paired question")
            result_offset = len(raw)
            send(json.loads(question.read_text())["answer"].encode() + b"\r")
            wait_for(lambda: mount_count() == 4, "successful result")
            successful = json.loads(mounts.read_text())[-1]
            reward = successful.get("reward")
            assert reward and "REWARD" in reward["title"]
            assert reward["interval"] > 0
            frames = reward["frames"]
            assert len(frames) > 1 and len({tuple(frame) for frame in frames}) > 1
            # The reward is the default-visible result panel.  Wait past its
            # real .35s Textual timer and require a distinct authored art row
            # to reach the PTY; earlier lesson-reference playback is excluded
            # by starting at this already-mounted result offset.
            offset = len(raw)
            previous = tuple(frames[0])
            changed_rows = [
                row for frame in frames[1:]
                for row in frame
                if row.strip() and row not in previous
            ]
            assert changed_rows, (columns, rows, frames)
            wait_for(lambda: changed_rows[0].encode("utf-8") in raw[offset:],
                     "result reward frame timer")
            wait_for(lambda: frame_observations.exists() and len({
                row["index"] for row in json.loads(frame_observations.read_text())}) >= 2,
                "two actual rendered reward frames")
            assert b"REWARD" in raw[result_offset:]
            send(b"f")
            wait_for(lambda: b"FEEDBACK" in raw[-1500:], "feedback input")
            send(b"isolated Textual route note\r")
            wait_for(lambda: mount_count() == 5, "result after saved feedback")
            feedback = [json.loads(line) for line in state.joinpath("feedback.jsonl").read_text().splitlines()]
            assert feedback[-1]["message"] == "isolated Textual route note"
            before = state.joinpath("events-v2.jsonl").read_text()
            offset = len(raw)
            send(b"w")
            wait_for(lambda: b"cursor start" in raw[offset:], "explicit Watch with auto-play off")
            send(b"\r")
            wait_for(lambda: mount_count() == 6, "result after Watch")
            offset = len(raw)
            send(b"d")
            wait_for(dashboard_mount.exists, "actual dashboard after-refresh")
            assert json.loads(dashboard_mount.read_text()) == {"columns": columns, "rows": rows}
            send(b"q")
            wait_for(lambda: mount_count() == 7, "result after dashboard")
            send(b"r")
            wait_for(lambda: mount_count() == 8, "credited lesson repeat")
            assert "M0.L0" in json.loads(mounts.read_text())[-1]["pages"][0][1]
            edit(b"jjk0")  # Extra movement is not a failed method.
            wait_for(lambda: mount_count() == 9, "practice result")
            # Already-passed paired questions are not repeated or awarded.
            assert json.loads(question.read_text())["count"] == 1
            assert "METHOD ✗" not in json.loads(mounts.read_text())[-1]["pages"][0][1]
            assert state.joinpath("events-v2.jsonl").read_text() == before
            send(b"n")
            wait_for(lambda: mount_count() == 10, "Next leaves completed practice")
            assert "M0.F0" in json.loads(mounts.read_text())[-1]["pages"][0][1]
            # Closing the next lesson cannot invent another pass.
            send(b"q")
            wait_for(lambda: child.poll() is not None, "close practice")
            assert state.joinpath("events-v2.jsonl").read_text() == before
            assert child.returncode == 0
            print(f"PASS actual Textual lesson/source-motion/result-reward-timer/failed Repeat/credited practice/Next/Watch/dashboard/feedback/close {columns}x{rows}")
        finally:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=3)
            os.close(slave)
            os.close(master)
