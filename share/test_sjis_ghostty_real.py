"""Actual Ghostty native-PNG acknowledgements; no screenshot/grade injection.

Launch a separate Ghostty window. The child calls the production transmitter
and reports only real four-panel acknowledgements to a nonce-bound loopback
socket. No confirmation is synthesized and no operator acceptance is claimed.
Use --tmux for a disposable tmux server with explicit local passthrough.
"""
import base64
import json
import os
from pathlib import Path
import secrets
import shlex
import socket
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent

if "--popup-launch" in sys.argv:
    # Explicit origin identity is scoped to the popup child, just as the
    # production popup hooks supply it. No server environment is mutated.
    pane = subprocess.check_output(["tmux", "display-message", "-p", "#{pane_id}"], text=True).strip()
    origin = subprocess.check_output(["tmux", "display-message", "-p",
                                      "#{socket_path},#{pid},#{session_id}"], text=True).strip()
    child = [sys.executable, str(Path(__file__).resolve()), "--child", *sys.argv[2:]]
    raise SystemExit(subprocess.run(["tmux", "display-popup", "-E", "-w", "90%", "-h", "85%",
                                    "-e", "TMUX=" + origin, "-e", "TMUX_PANE=" + pane,
                                    shlex.join(child)]).returncode)

if "--child" in sys.argv:
    import sjis_terminal as terminal
    from sjis_tutor import TutorPreview
    port, nonce = int(sys.argv[2]), sys.argv[3]
    card = next(card for card in json.loads((HERE / "curriculum-v2.json").read_text())["cards"]
                if card["id"] == "M10.06")
    result = {"nonce": nonce, "schema": "vim-daily/actual-ghostty-transport@1",
              "operator_visual_acceptance": "unverified",
              "term_program": os.environ.get("TERM_PROGRAM"),
              "term_program_version": os.environ.get("TERM_PROGRAM_VERSION"),
              "transport": "tmux" if os.environ.get("TMUX") else "direct",
              "images": []}
    try:
        if "--isolated-tmux" in sys.argv:
            owned_socket = sys.argv[sys.argv.index("--isolated-tmux") + 1]
            assert owned_socket == "vd-ghostty-proof-" + nonce[:12]
            origin = subprocess.check_output(["tmux", "-L", owned_socket,
                                               "show-environment", "-g", "TERM_PROGRAM"], text=True).strip()
            assert origin == "TERM_PROGRAM=ghostty", ("Not a Ghostty-created tmux server", origin)
            result["parent_term_program"] = "ghostty"
            result["client_termname"] = subprocess.check_output(
                ["tmux", "-L", owned_socket, "display-message", "-p", "#{client_termname}"], text=True).strip()
        else:
            assert os.environ.get("TERM_PROGRAM") == "ghostty", "Not an actual Ghostty terminal"
        with tempfile.TemporaryDirectory(prefix="vim-daily-ghostty-art-") as directory:
            art = Path(directory) / "working.txt"
            art.write_text("\n".join(card["start"]) + "\n")
            preview = TutorPreview(art, card["target"], before_rows=card["start"], open_browser=False)
            payload = preview.refresh()
            result["identity"] = terminal.native._preview_identity(payload)
            result["font_sha256"] = preview.metrics.font_sha256
            with terminal.temporary_tmux_passthrough() as passthrough_before:
                if passthrough_before is not None:
                    result["passthrough_before"] = passthrough_before
                for name in ("before", "yours", "target", "difference"):
                    print("\nACTUAL GHOSTTY · " + name.upper(), flush=True)
                    png = base64.b64decode(payload[name]["png_data_url"].split(",", 1)[1], validate=True)
                    ack = terminal.transmit_png(png, secrets.randbelow(2**30 - 1) + 1)
                    result["images"].append(dict(ack, panel=name))
                    print(flush=True)
            if passthrough_before is not None:
                result["passthrough_after"] = terminal.inspect_tmux_passthrough()
            result["transport_ready"] = True
            print("Four actual native PNGs acknowledged. Human contour approval remains unverified.", flush=True)
    except Exception as exc:
        result["transport_ready"] = False
        result["error"] = str(exc)
    with socket.create_connection(("127.0.0.1", port), timeout=3) as connection:
        connection.sendall(json.dumps(result).encode())
    raise SystemExit(0 if result["transport_ready"] else 1)

with socket.socket() as server:
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    server.settimeout(25)
    nonce = secrets.token_hex(16)
    command = [sys.executable, str(Path(__file__).resolve()), "--child",
               str(server.getsockname()[1]), nonce]
    tmux_socket = "vd-ghostty-proof-" + nonce[:12]
    if "--popup" in sys.argv:
        command[2] = "--popup-launch"
    if "--tmux" in sys.argv or "--popup" in sys.argv:
        command += ["--isolated-tmux", tmux_socket]
        command = ["tmux", "-L", tmux_socket, "-f", "/dev/null", "new-session",
                   "-s", "preview", shlex.join(command)]
    try:
        subprocess.run(["open", "-na", "/Applications/Ghostty.app", "--args", "-e", *command], check=True)
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
        assert result["transport_ready"], result
        assert len(result["images"]) == 4 and all(image["terminal_reply"] == "OK" for image in result["images"])
        if "--tmux" in sys.argv or "--popup" in sys.argv:
            before = result["passthrough_before"]
            after = result["passthrough_after"]
            assert before["pane_explicit"] == ""
            assert before["pane_effective"] == "off"
            assert before["global_default"] == "off"
            assert after["pane_explicit"] == ""
            assert after["pane_effective"] == "off"
            assert after["global_default"] == "off"
        print(json.dumps(result, indent=2))
    finally:
        if "--tmux" in sys.argv or "--popup" in sys.argv:
            subprocess.run(["tmux", "-L", tmux_socket, "kill-server"],
                           check=False, stderr=subprocess.DEVNULL)
