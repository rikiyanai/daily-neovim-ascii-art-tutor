"""Headed proof for the native popup-to-normal-window route.

This is an isolated uncredited-practice runtime proof, not learner mastery. A disposable
tmux server is created by a real Ghostty process.  The outer pane invokes the
production popup route, which must create a normal window for the proportional
M10 practice card.  The child then drives the real Neovim edit, both native
preview confirmations, and the authored after-question.  Only the isolated
state directory receives the resulting practice attempt artifacts.
"""

from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import secrets
import shlex
import socket
import subprocess
import sys
import tempfile
import time
from io import BytesIO


ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "bin" / "vim-daily-gate"
TEST = Path(__file__).resolve()


def _run(socket_name, *args, check=True):
    return subprocess.run(
        ["tmux", "-L", socket_name, *args],
        check=check,
        text=True,
        capture_output=True,
    )


def _capture(socket_name, pane):
    return _run(socket_name, "capture-pane", "-p", "-t", pane, "-S", "-100").stdout


def _send(socket_name, pane, *keys):
    _run(socket_name, "send-keys", "-t", pane, *keys)


def _send_literal(socket_name, pane, text):
    for char in text:
        _run(socket_name, "send-keys", "-t", pane, "-l", char)
        time.sleep(0.12)


def _wait_screen(socket_name, pane, predicate, label, timeout=45):
    deadline = time.monotonic() + timeout
    latest = ""
    while time.monotonic() < deadline:
        latest = _capture(socket_name, pane)
        if predicate(latest):
            return latest
        time.sleep(0.15)
    raise AssertionError("%s (share/native_window_route.py:41);\n%s" % (label, latest))


def _credit_prompt_ready(text):
    return ("BEFORE CREDIT" in text
            and "Enter = inspected these four native panels" in text.rsplit("BEFORE CREDIT", 1)[-1])


def _window_rows(socket_name):
    output = _run(
        socket_name,
        "list-windows",
        "-F",
        "#{window_id}\t#{window_name}\t#{window_panes}",
    ).stdout
    return [row.split("\t") for row in output.splitlines() if row.strip()]


def _allow_state(socket_name, target, scope):
    if scope == "global":
        args = ("show-options", "-gqv", "allow-passthrough")
    elif scope == "window":
        args = ("show-options", "-wqv", "-t", target, "allow-passthrough")
    elif scope == "pane":
        args = ("show-options", "-pqv", "-t", target, "allow-passthrough")
    else:
        raise ValueError(scope)
    return _run(socket_name, *args).stdout.strip()


def _parent_state(socket_name, window, pane):
    return {
        "global_allow_passthrough": _allow_state(socket_name, window, "global"),
        "window_allow_passthrough": _allow_state(socket_name, window, "window"),
        "pane_allow_passthrough": _allow_state(socket_name, pane, "pane"),
        "window_remain_on_exit": _run(
            socket_name, "show-options", "-wqv", "-t", window, "remain-on-exit"
        ).stdout.strip(),
    }


def _child(port, nonce, socket_name, state_home):
    """Run inside the Ghostty-created outer pane."""
    card_id = os.environ.get("VIM_DAILY_TEST_NATIVE_CARD", "M10.01")
    curriculum = json.loads((ROOT / "share" / "curriculum-v2.json").read_text(encoding="utf-8"))
    card = next(row for row in curriculum["cards"] if row["id"] == card_id)
    server_term = _run(socket_name, "show-environment", "-g", "TERM_PROGRAM").stdout.strip()
    if server_term != "TERM_PROGRAM=ghostty":
        raise AssertionError("tmux server was not created by Ghostty (share/test_native_window_route_real.py:107): %s" % server_term)

    parent_row = _run(
        socket_name,
        "display-message",
        "-p",
        "#{window_id}\t#{pane_id}",
    ).stdout.strip().split("\t")
    if len(parent_row) != 2:
        raise AssertionError("Exact parent pane ownership unavailable (share/sjis_terminal.py:40)")
    parent_window, parent_pane = parent_row
    before = _parent_state(socket_name, parent_window, parent_pane)

    # This is the production selection boundary: v2_runtime sees the popup
    # marker and calls native_window_route.open_window, rather than this test
    # creating a window directly.
    ready_signal = os.environ.get("VIM_DAILY_TMUX_READY_SIGNAL")
    if ready_signal:
        _run(socket_name, "wait-for", "-L", ready_signal)
    popup_env = dict(os.environ, VIM_DAILY_POPUP="1")
    selected = subprocess.run(
        [str(GATE), "--practice-card", card_id],
        env=popup_env,
        check=False,
    )
    if selected.returncode != 0:
        raise AssertionError(
            "Production popup selection failed at v2_runtime.py:5266 (exit %d)"
            % selected.returncode
        )

    deadline = time.monotonic() + 20
    native_window = None
    while time.monotonic() < deadline:
        for row in _window_rows(socket_name):
            if row[0] != parent_window and row[1] == "vim-daily JIS":
                native_window = row[0]
                break
        if native_window:
            break
        time.sleep(0.1)
    if not native_window:
        raise AssertionError("Popup did not open a temporary normal window (share/native_window_route.py:38)")
    pane_rows = _run(
        socket_name,
        "list-panes",
        "-t",
        native_window,
        "-F",
        "#{pane_id}",
    ).stdout.splitlines()
    if len(pane_rows) != 1:
        raise AssertionError("Temporary tutor window did not have one owned pane (share/native_window_route.py:38)")
    tutor_pane = pane_rows[0]
    textual = os.environ.get("VIM_DAILY_TEXTUAL") == "1"
    result = {
        "schema": "vim-daily/actual-ghostty-native-window-route@1",
        "nonce": nonce,
        "term_program": os.environ.get("TERM_PROGRAM"),
        "server_term_program": server_term,
        "transport": "ghostty-tmux-normal-window",
        "parent_window": parent_window,
        "parent_pane": parent_pane,
        "native_window": native_window,
        "tutor_pane": tutor_pane,
        "options_before": before,
        "textual_lesson_and_result": textual,
        "card_id": card_id,
    }

    if textual:
        _wait_screen(socket_name, tutor_pane,
                     lambda text: "Lesson" in text and "Continue" in text and "Close" in text,
                     "Native Textual lesson did not mount its controls")
        _send(socket_name, tutor_pane, "Enter")

    # The first four-image display is held by the real TerminalPreview while
    # the pane override is active.  Inspect it before accepting the display.
    _wait_screen(
        socket_name,
        tutor_pane,
        lambda text: "Enter = inspected these four native panels" in text,
        "native BEFORE display did not reach its real confirmation prompt",
    )
    result["native_preview_options"] = {
        "global": _allow_state(socket_name, native_window, "global"),
        "window": _allow_state(socket_name, native_window, "window"),
        "pane": _allow_state(socket_name, tutor_pane, "pane"),
    }
    result["native_window_remain_on_exit"] = _run(
        socket_name, "show-options", "-wqv", "-t", native_window, "remain-on-exit"
    ).stdout.strip()
    if result["native_window_remain_on_exit"] != "off":
        raise AssertionError("Temporary window did not receive remain-on-exit off (share/native_window_route.py:46)")
    _send(socket_name, tutor_pane, "Enter")

    _wait_screen(
        socket_name,
        tutor_pane,
        lambda text: card_id in text and "DO THIS" in text,
        "Neovim did not reach the selected edit surface",
    )
    if ready_signal:
        subprocess.run(["tmux", "-L", socket_name, "wait-for", "-L", ready_signal],
                       check=True, timeout=25, capture_output=True)
        _run(socket_name, "wait-for", "-U", ready_signal)
    # M10.01's authored recipe is $rヽ.  :wq is sent separately so the real
    # nvim scriptout records the edit and its submission boundary.
    _send_literal(socket_name, tutor_pane, card["expected"])
    _send(socket_name, tutor_pane, "Escape")
    time.sleep(1.1)
    _send_literal(socket_name, tutor_pane, ":wq")
    _send(socket_name, tutor_pane, "Enter")

    _wait_screen(
        socket_name,
        tutor_pane,
        # Scrollback still contains the BEFORE EDITING confirmation while
        # the new four panels are transmitting. Sending Enter then lets a
        # graphics acknowledgement read consume it before input() starts.
        _credit_prompt_ready,
        "native BEFORE CREDIT display did not reach its real confirmation prompt",
    )
    _send(socket_name, tutor_pane, "Enter")

    session = Path(state_home) / "vim-daily" / "sessions" / "practice" / card["project_id"] / card_id
    artifact_name = ("animation-%s.txt" % card_id if card.get("artifact") == "animation-study"
                     else "transfer-%s.txt" % card_id if card.get("artifact") == "transfer"
                     else "strip.txt")
    artifact_path = session / artifact_name
    try:
        _wait_screen(
            socket_name, tutor_pane,
            lambda text: "answer (a-d)" in text and "ANIMATION" in text and "NEOVIM" in text,
            "Authored after-question did not appear after the native edit",
        )
    except AssertionError as exc:
        keylog = session / ("keys-%s-attempt-0001.log" % card_id)
        receipt = keylog.with_suffix(".native.json")
        detail = {
            "artifact_rows": artifact_path.read_text().splitlines() if artifact_path.exists() else None,
            "target_equal": artifact_path.exists() and artifact_path.read_text().splitlines() == card["target"],
            "keylog_hex": keylog.read_bytes().hex() if keylog.exists() else None,
            "native_receipt": json.loads(receipt.read_text()) if receipt.exists() else None,
        }
        raise AssertionError(str(exc) + "\nactual attempt: " + json.dumps(detail, ensure_ascii=False)) from exc
    result["options_after_native_restore"] = {
        "global": _allow_state(socket_name, native_window, "global"),
        "window": _allow_state(socket_name, native_window, "window"),
        "pane": _allow_state(socket_name, tutor_pane, "pane"),
    }
    expected_restored = {
        "global": before["global_allow_passthrough"],
        "window": before["window_allow_passthrough"],
        "pane": before["pane_allow_passthrough"],
    }
    if result["options_after_native_restore"] != expected_restored:
        raise AssertionError("Native pane passthrough was not restored before grading: before=%r after=%r" %
                             (expected_restored, result["options_after_native_restore"]))
    _send_literal(socket_name, tutor_pane, "a")
    _send(socket_name, tutor_pane, "Enter")

    # Practice routes deliberately do not append PASS rows to the learner's
    # event ledger.  The actual grade is nevertheless persisted in the
    # isolated attempt receipt and manifest, which is the correct proof here:
    # this run must not manufacture learner progress just to test transport.
    receipt_path = session / ("keys-%s-attempt-0001.native.json" % card_id)
    deadline = time.monotonic() + 35
    native_receipt = {}
    completion_screen = ""
    while time.monotonic() < deadline:
        if receipt_path.is_file():
            native_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        capture_run = _run(socket_name, "capture-pane", "-p", "-t", tutor_pane,
                           "-S", "-100", check=False)
        completion_screen = capture_run.stdout or completion_screen
        if (native_receipt.get("ready") and artifact_path.is_file()
                and "PRACTICE COMPLETE" in completion_screen
                and ("Repeat" in completion_screen if textual else
                     "Enter = skill-tree progress" in completion_screen)):
            break
        time.sleep(0.15)
    if not native_receipt.get("ready") or not artifact_path.is_file():
        state_listing = [str(path.relative_to(state_home)) for path in Path(state_home).rglob("*")]
        raise AssertionError(
            "M10.01 practice grade did not produce a ready native receipt "
            "(share/v2_runtime.py:4308); state=%r screen=%r" %
            (state_listing, completion_screen[-5000:])
        )
    held = "Repeat" in completion_screen if textual else "Enter = skill-tree progress" in completion_screen
    if "PRACTICE COMPLETE" not in completion_screen or not held:
        raise AssertionError("Native receipt is not a passing grade: actual held completion was absent: "
                             + completion_screen[-4000:])
    if artifact_path.read_text(encoding="utf-8").splitlines() != card["target"]:
        raise AssertionError("M10.01 native edit did not produce the authored target (share/v2_runtime.py:4315)")
    keylog_path = session / ("keys-%s-attempt-0001.log" % card_id)
    if not keylog_path.is_file() or not keylog_path.read_bytes():
        raise AssertionError("M10.01 native edit produced no real Neovim keylog (bin/vim-daily-gate:780)")
    if not native_receipt.get("ready"):
        raise AssertionError("M10.01 pass lacked a ready native receipt (share/v2_runtime.py:4308)")
    display = native_receipt.get("display") or {}
    if len(display.get("images", [])) != 4:
        raise AssertionError("Native receipt was not bound to four actual panels (share/sjis_terminal.py:346)")
    result["practice_completion_visible"] = "PRACTICE COMPLETE" in completion_screen
    result["grade"] = "practice-native-target-and-four-panel-receipt"
    result["native_receipt_ready"] = True
    result["native_panel_count"] = len(display["images"])
    result["module_result_reward"] = (
        "authored-by-current-curriculum"
        if card.get("module_reward") else "not-authored-on-M10.01"
    )
    if card.get("module_reward"):
        # Inspect the production result-playback receipt, not a direct helper
        # call or merely the presence of authored metadata on the card.
        import sjis_authoring as native
        from PIL import Image
        reward_path = keylog_path.with_suffix(".reward.json")
        if not reward_path.is_file():
            raise AssertionError("Passing result omitted actual native module playback receipt")
        reward = json.loads(reward_path.read_text(encoding="utf-8"))
        frames = card["module_reward"]["frames"]
        metrics = native.load_font_metrics(
            os.environ.get("VIM_DAILY_SAITAMAAR_FONT") or native.DEFAULT_FONT_PATH)
        if (reward.get("card_id") != card["id"]
                or reward.get("curriculum_revision") != curriculum["revision"]
                or reward.get("keylog_sha256") != hashlib.sha256(keylog_path.read_bytes()).hexdigest()
                or reward.get("font_sha256") != metrics.font_sha256
                or len(reward.get("frames", [])) != len(frames) or len(frames) < 8):
            raise AssertionError("Native result receipt is not bound to this complete authored sequence")
        rasters = [native.render_text("\n".join(frame) + "\n", metrics) for frame in frames]
        extent = [max(raster.width_px for raster in rasters), max(raster.height_px for raster in rasters)]
        if reward.get("canvas_px") != extent or reward.get("origin_px") != [0, 0]:
            raise AssertionError("Native result frames lack a shared registered pixel canvas")
        for index, frame in enumerate(frames):
            raster = rasters[index]
            canvas = Image.new("L", tuple(extent), 0)
            canvas.paste(Image.frombytes("L", (raster.width_px, raster.height_px), raster.pixels), (0, 0))
            encoded = BytesIO()
            canvas.save(encoded, format="PNG", optimize=False, compress_level=9)
            actual = reward["frames"][index]
            if (actual.get("frame_index") != index or actual.get("terminal_reply") != "OK"
                    or actual.get("canonical_text_sha256") != raster.text_sha256
                    or actual.get("png_sha256") != hashlib.sha256(encoded.getvalue()).hexdigest()
                    or actual.get("elapsed_hold_seconds", 0) < actual.get("authored_hold_seconds", 1)):
                raise AssertionError("Actual native result frame/hold mismatch at index %d" % index)
        result["module_result_reward"] = reward
    events = Path(state_home) / "vim-daily/events-v2.jsonl"
    if events.exists() and events.read_text(encoding="utf-8").strip():
        raise AssertionError("Uncredited native practice created a learner event")
    if not textual:
        _send(socket_name, tutor_pane, "Enter")
        _wait_screen(socket_name, tutor_pane,
                     lambda text: "Enter = close" in text, "Native result did not reach held close control")
    _send(socket_name, tutor_pane, "Enter")

    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if all(row[0] != native_window for row in _window_rows(socket_name)):
            break
        time.sleep(0.1)
    if any(row[0] == native_window for row in _window_rows(socket_name)):
        raise AssertionError("Owned native tutor window did not close after the gate exited (share/native_window_route.py:51)")
    result["owned_window_closed"] = True
    after = _parent_state(socket_name, parent_window, parent_pane)
    result["options_after"] = after
    if after != before:
        raise AssertionError("Parent/window/global tmux options changed: before=%r after=%r" % (before, after))
    return result


def _parent():
    with tempfile.TemporaryDirectory(prefix="vim-daily-native-window-") as directory:
        root = Path(directory)
        state_home = root / "state"
        data_home = root / "data"
        state_home.mkdir()
        data_home.mkdir()
        (data_home / "vim-daily").symlink_to(ROOT / "share", target_is_directory=True)
        if "--textual" in sys.argv:
            (data_home / "vim-daily-venv").symlink_to(
                Path.home() / ".local/share/vim-daily-venv", target_is_directory=True)

        nonce = secrets.token_hex(16)
        socket_name = "vdt-native-window-" + nonce[:12]
        with socket.socket() as server:
            server.bind(("127.0.0.1", 0))
            server.listen(1)
            server.settimeout(110)
            child = [
                sys.executable,
                str(TEST),
                "--child",
                str(server.getsockname()[1]),
                nonce,
                socket_name,
                str(state_home),
            ]
            command = [
                "tmux",
                "-L",
                socket_name,
                "-f",
                "/dev/null",
                "new-session",
                "-s",
                "preview",
                "-x",
                os.environ.get("VIM_DAILY_TEST_COLUMNS", "180"),
                "-y",
                os.environ.get("VIM_DAILY_TEST_ROWS", "58"),
                shlex.join(child),
            ]
            launch_env = dict(os.environ)
            launch_env.update({
                "XDG_STATE_HOME": str(state_home),
                "XDG_DATA_HOME": str(data_home),
                "EDITOR": "nvim",
                "TERM": "xterm-256color",
                "VIM_DAILY_CLEAN": "1",
                "VIM_DAILY_USE_USER_CONFIG": "0",
                "VIM_DAILY_USE_MANAGED_RUNTIME": "1" if "--textual" in sys.argv else "0",
                "VIM_DAILY_TEXTUAL": "1" if "--textual" in sys.argv else "0",
                "VIM_DAILY_NO_WARMUP": "1",
                "VIM_DAILY_VIEWER": "off",
                "VIM_DAILY_MAX_TRIES": "1",
                "VIM_DAILY_COOLDOWN": "0",
                "VIM_DAILY_TEST_CHOICE_ORDER": "0123",
                "VIM_DAILY_TMUX_QUESTION_SIGNAL": "vdt-question-" + nonce[:12],
                "VIM_DAILY_TMUX_READY_SIGNAL": "vdt-ready-" + nonce[:12],
                "VIM_DAILY_TMUX_FEEDBACK_SIGNAL": "vdt-feedback-" + nonce[:12],
                "VIM_DAILY_TMUX_POST_SIGNAL": "vdt-post-" + nonce[:12],
                "VIM_DAILY_TMUX_FINISHED_SIGNAL": "vdt-finished-" + nonce[:12],
            })
            if "--endcap" in sys.argv:
                launch_env.update({"VIM_DAILY_TEST_NATIVE_CARD": "M10.REWARD",
                                   "VIM_DAILY_CLEAN": "0",
                                   "VIM_DAILY_USE_USER_CONFIG": "1"})
            chosen_card = next((arg.split("=", 1)[1] for arg in sys.argv
                                if arg.startswith("--card=")), None)
            if chosen_card:
                launch_env["VIM_DAILY_TEST_NATIVE_CARD"] = chosen_card
            subprocess.run(
                ["open", "-na", "/Applications/Ghostty.app", "--args", "-e", *command],
                env=launch_env,
                check=True,
            )
            try:
                connection, _address = server.accept()
                with connection:
                    connection.settimeout(5)
                    data = bytearray()
                    while True:
                        chunk = connection.recv(65536)
                        if not chunk:
                            break
                        data.extend(chunk)
                result = json.loads(data)
            finally:
                subprocess.run(
                    ["tmux", "-L", socket_name, "kill-server"],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        if result.pop("nonce") != nonce:
            raise AssertionError("Nonce-bound Ghostty result did not match this run")
        if result.get("error"):
            raise AssertionError(result["error"])
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if "--child" in sys.argv:
        try:
            value = _child(int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5])
        except Exception as exc:
            # Preserve failed-stage evidence; never create a learner event.
            value = {"nonce": sys.argv[3], "error": str(exc)}
            with socket.create_connection(("127.0.0.1", int(sys.argv[2])), timeout=5) as connection:
                connection.sendall(json.dumps(value).encode("utf-8"))
            raise
        with socket.create_connection(("127.0.0.1", int(sys.argv[2])), timeout=5) as connection:
            connection.sendall(json.dumps(value).encode("utf-8"))
        raise SystemExit(0)
    _parent()
