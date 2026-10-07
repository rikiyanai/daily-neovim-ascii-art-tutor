"""Actual Ghostty playback proof for the canonical M10 animation.

This is a transport proof, not a screenshot fixture or a learner-grade path.
The child imports ``animation_for`` directly, calls the production native
playback helper, binds each actual Kitty acknowledgement to the canonical
frame and rendered PNG hash, and reports only through a nonce-bound loopback
socket.  ``--tmux`` uses a disposable tmux server created by Ghostty; the
production pane-scoped passthrough context must leave pane and global state
unchanged after all eight frames.
"""
import hashlib
import json
import os
from pathlib import Path
import secrets
import shlex
import socket
import subprocess
import sys
import time
from io import BytesIO
from PIL import Image

import sjis_authoring as native
from module_animations import animation_for


def _font_metrics(native):
    return native.load_font_metrics(
        os.environ.get("VIM_DAILY_SAITAMAAR_FONT") or native.DEFAULT_FONT_PATH
    )


def _canonical_frame_hash(frame):
    return hashlib.sha256(("\n".join(frame) + "\n").encode("utf-8")).hexdigest()


def _canonical_png(native, metrics, frame):
    motion = animation_for("M10")
    rasters = [native.render_text("\n".join(rows) + "\n", metrics) for rows in motion["frames"]]
    raster = native.render_text("\n".join(frame) + "\n", metrics)
    canvas = Image.new("L", (max(row.width_px for row in rasters),
                             max(row.height_px for row in rasters)), 0)
    canvas.paste(Image.frombytes("L", (raster.width_px, raster.height_px), raster.pixels), (0, 0))
    encoded = BytesIO()
    canvas.save(encoded, format="PNG", optimize=False, compress_level=9)
    return encoded.getvalue()


if "--child" in sys.argv:
    import module_native_playback as playback
    import sjis_terminal as terminal

    port, nonce = int(sys.argv[2]), sys.argv[3]
    motion = animation_for("M10")
    result = {
        "nonce": nonce,
        "schema": "vim-daily/actual-ghostty-module-playback@1",
        "module_id": motion["module_id"],
        "frame_count": motion["frame_count"],
        "operator_visual_acceptance": "unverified",
        "term_program": os.environ.get("TERM_PROGRAM"),
        "term_program_version": os.environ.get("TERM_PROGRAM_VERSION"),
        "transport": "tmux" if os.environ.get("TMUX") else "direct",
        "actual_frames": [],
        "wait_intervals": [],
    }
    try:
        if "--isolated-tmux" in sys.argv:
            owned_socket = sys.argv[sys.argv.index("--isolated-tmux") + 1]
            assert owned_socket == "vdt-module-proof-" + nonce[:12]
            origin = subprocess.check_output(
                ["tmux", "-L", owned_socket, "show-environment", "-g", "TERM_PROGRAM"],
                text=True,
            ).strip()
            assert origin == "TERM_PROGRAM=ghostty", (
                "Not a Ghostty-created tmux server",
                origin,
            )
            result["parent_term_program"] = "ghostty"
            result["client_termname"] = subprocess.check_output(
                [
                    "tmux",
                    "-L",
                    owned_socket,
                    "display-message",
                    "-p",
                    "#{client_termname}",
                ],
                text=True,
            ).strip()
        else:
            assert os.environ.get("TERM_PROGRAM") == "ghostty", (
                "Not an actual Ghostty terminal",
                os.environ.get("TERM_PROGRAM"),
            )

        metrics = _font_metrics(native)
        result["canonical_font_sha256"] = metrics.font_sha256
        result["interval_fps"] = motion["interval"]["fps"]
        before = terminal.inspect_tmux_passthrough()
        if before is not None:
            result["passthrough_before"] = before

        def sender(png, image_id):
            index = len(result["actual_frames"])
            frame = motion["frames"][index]
            expected_png = _canonical_png(native, metrics, frame)
            expected_png_sha256 = hashlib.sha256(expected_png).hexdigest()
            expected_text_sha256 = _canonical_frame_hash(frame)
            if png != expected_png:
                raise AssertionError(
                    "Production playback raster does not match canonical M10 frame "
                    + str(index)
                )
            ack = terminal.transmit_png(png, image_id)
            if ack.get("terminal_reply") != "OK":
                raise AssertionError("Ghostty did not positively acknowledge frame %d" % index)
            if ack.get("png_sha256") != expected_png_sha256:
                raise AssertionError("ACK PNG hash does not bind frame %d" % index)
            result["actual_frames"].append(
                {
                    "frame_index": index,
                    "image_id": image_id,
                    "terminal_reply": ack["terminal_reply"],
                    "png_sha256": ack["png_sha256"],
                    "canonical_frame_sha256": expected_text_sha256,
                    "font_sha256": metrics.font_sha256,
                }
            )
            return ack

        def wait(interval):
            started = time.monotonic()
            time.sleep(interval)
            result["wait_intervals"].append(interval)
            result.setdefault("elapsed_holds", []).append(time.monotonic() - started)

        with terminal.temporary_tmux_passthrough() as context_before:
            if context_before is not None:
                result["context_before"] = context_before
            playback_result = playback.play(
                motion,
                sender=sender,
                wait=wait,
            )
        result["playback"] = playback_result
        after = terminal.inspect_tmux_passthrough()
        if after is not None:
            result["passthrough_after"] = after
        result["transport_ready"] = True
        print(
            "Eight actual canonical M10 native PNGs acknowledged. "
            "Human contour acceptance remains unverified.",
            flush=True,
        )
    except Exception as exc:
        result["transport_ready"] = False
        result["error"] = str(exc)

    with socket.create_connection(("127.0.0.1", port), timeout=3) as connection:
        connection.sendall(json.dumps(result).encode("utf-8"))
    raise SystemExit(0 if result["transport_ready"] else 1)


with socket.socket() as server:
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    server.settimeout(35)
    nonce = secrets.token_hex(16)
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--child",
        str(server.getsockname()[1]),
        nonce,
    ]
    tmux_socket = "vdt-module-proof-" + nonce[:12]
    if "--tmux" in sys.argv:
        command += ["--isolated-tmux", tmux_socket]
        command = [
            "tmux",
            "-L",
            tmux_socket,
            "-f",
            "/dev/null",
            "new-session",
            "-s",
            "preview",
            shlex.join(command),
        ]
    try:
        subprocess.run(
            ["open", "-na", "/Applications/Ghostty.app", "--args", "-e", *command],
            check=True,
        )
        connection, _address = server.accept()
        with connection:
            connection.settimeout(3)
            data = bytearray()
            while True:
                chunk = connection.recv(65536)
                if not chunk:
                    break
                data.extend(chunk)
        result = json.loads(data)
        assert result.pop("nonce") == nonce
        assert result["module_id"] == "M10"
        motion = animation_for("M10")
        assert result["frame_count"] == len(motion["frames"]) == 8
        assert result["transport_ready"], result
        actual = result["actual_frames"]
        assert len(actual) == 8
        assert [item["frame_index"] for item in actual] == list(range(8))
        assert all(item["terminal_reply"] == "OK" for item in actual)
        playback_frames = result["playback"]["frames"]
        assert len(playback_frames) == 8
        assert [item["frame_index"] for item in playback_frames] == list(range(8))
        assert all(item["terminal_reply"] == "OK" for item in playback_frames)
        assert result["playback"]["font_sha256"] == result["canonical_font_sha256"]
        assert result["operator_visual_acceptance"] == "unverified"
        metrics = _font_metrics(native)
        assert result["canonical_font_sha256"] == metrics.font_sha256
        assert len(result["wait_intervals"]) == 8
        assert all(abs(interval - (1 / motion["interval"]["fps"])) < 1e-9
                   for interval in result["wait_intervals"])
        assert len(result["elapsed_holds"]) == 8
        assert all(elapsed >= interval for elapsed, interval in zip(
            result["elapsed_holds"], result["wait_intervals"]))
        for index, item in enumerate(actual):
            frame = motion["frames"][index]
            expected_text_sha256 = _canonical_frame_hash(frame)
            expected_png_sha256 = hashlib.sha256(
                _canonical_png(native, metrics, frame)
            ).hexdigest()
            assert item["canonical_frame_sha256"] == expected_text_sha256
            assert item["png_sha256"] == expected_png_sha256
            assert item["font_sha256"] == metrics.font_sha256
            assert playback_frames[index]["frame_index"] == item["frame_index"]
            assert playback_frames[index]["image_id"] == item["image_id"]
            assert playback_frames[index]["png_sha256"] == item["png_sha256"]
        if "--tmux" in sys.argv:
            before = result["passthrough_before"]
            after = result["passthrough_after"]
            for state in (before, after):
                assert state["pane_explicit"] == ""
                assert state["pane_effective"] == "off"
                assert state["window_effective"] == "off"
                assert state["global_default"] == "off"
            assert before["target"] == after["target"]
        print(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        if "--tmux" in sys.argv:
            subprocess.run(
                ["tmux", "-L", tmux_socket, "kill-server"],
                check=False,
                stderr=subprocess.DEVNULL,
            )
