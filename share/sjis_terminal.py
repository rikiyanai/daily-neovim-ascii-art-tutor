"""Native Saitamaar PNGs in Ghostty's Kitty graphics protocol.

The editable artifact stays text. Raster display never substitutes for byte
transcription, measured registration, or human contour judgement. Only the
validated tutor pane may receive a temporary passthrough override; its exact
prior setting is restored. No global configuration is changed. A missing
graphics acknowledgement denies credit.
"""
from __future__ import annotations

import base64
from contextlib import contextmanager
import hashlib
import os
import re
import secrets
import select
import subprocess
import sys
import termios
import time
import tty

import sjis_authoring as native
from sjis_tutor import TutorPreview


_PASSTHROUGH_VALUES = frozenset(("on", "off", "all"))


def _tmux_target_from_environment():
    """Resolve the exact inherited tmux server and pane, or return ``None``.

    A direct Ghostty terminal has neither tmux variable and needs no tmux
    mutation.  A partial or malformed pair is unsafe: there is no trustworthy
    pane owner to which a temporary override can be bound.
    """
    tmux_value = os.environ.get("TMUX")
    pane_id = os.environ.get("TMUX_PANE")
    if not tmux_value and not pane_id:
        return None
    if not tmux_value or not pane_id:
        raise RuntimeError(
            "Native tmux passthrough requires both TMUX and TMUX_PANE; "
            "precise tutor-pane ownership is unavailable."
        )
    socket_path, separator, metadata = tmux_value.partition(",")
    if not separator or not socket_path or not os.path.isabs(socket_path):
        raise RuntimeError(
            "Native tmux passthrough requires an absolute socket from TMUX; "
            "the default or an arbitrary tmux server will not be touched."
        )
    server_pid, separator, session_token = metadata.partition(",")
    if not separator or not server_pid.isdigit():
        raise RuntimeError(
            "Native tmux passthrough requires the inspected tmux server PID."
        )
    if not re.fullmatch(r"%[0-9]+", pane_id):
        raise RuntimeError(
            "Native tmux passthrough requires a stable TMUX_PANE id; "
            "pane aliases are not accepted."
        )
    return {
        "socket": socket_path,
        "server_pid": server_pid,
        "session_token": session_token,
        "pane_id": pane_id,
    }


def _tmux_call(target, *args):
    """Run one explicitly socket-bound tmux read/write."""
    command = ["tmux", "-S", target["socket"], *args]
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", "") or getattr(exc, "output", "") or str(exc)
        detail = str(detail).strip()
        raise RuntimeError(
            "Unable to inspect the exact tutor tmux pane/server: " + detail
        ) from exc
    return completed.stdout


def _inspect_tmux_pane(target):
    """Validate the pane/server identity inherited by the tutor process."""
    format_string = "\t".join(
        (
            "#{pane_id}",
            "#{session_id}",
            "#{window_id}",
            "#{pane_pid}",
            "#{pid}",
            "#{socket_path}",
            "#{pane_current_command}",
        )
    )
    output = _tmux_call(
        target,
        "display-message",
        "-p",
        "-t",
        target["pane_id"],
        format_string,
    ).rstrip("\n")
    fields = output.split("\t")
    if len(fields) != 7:
        raise RuntimeError(
            "Native tmux passthrough could not inspect the exact tutor pane "
            "identity."
        )
    pane_id, session_id, window_id, pane_pid, server_pid, socket_path, command = fields
    if pane_id != target["pane_id"]:
        raise RuntimeError(
            "Native tmux passthrough resolved a different pane than TMUX_PANE."
        )
    if server_pid != target["server_pid"]:
        raise RuntimeError(
            "Native tmux passthrough resolved a different server than TMUX."
        )
    if os.path.normpath(socket_path) != os.path.normpath(target["socket"]):
        raise RuntimeError(
            "Native tmux passthrough resolved a different tmux socket than TMUX."
        )
    if not session_id.startswith("$") or not window_id.startswith("@") or not pane_pid.isdigit():
        raise RuntimeError("Native tmux passthrough received incomplete pane identity.")
    session_token = target["session_token"]
    if session_token and session_token not in (session_id, session_id.lstrip("$")):
        raise RuntimeError(
            "Native tmux passthrough resolved a different session than TMUX."
        )
    return {
        "pane_id": pane_id,
        "session_id": session_id,
        "window_id": window_id,
        "pane_pid": pane_pid,
        "server_pid": server_pid,
        "socket": socket_path,
        "command": command,
    }


def _tmux_option(target, *args):
    value = _tmux_call(target, "show-options", *args, "allow-passthrough").strip()
    if value and value not in _PASSTHROUGH_VALUES:
        raise RuntimeError(
            "Native tmux passthrough received an unknown allow-passthrough value: "
            + value
        )
    return value


def inspect_tmux_passthrough():
    """Return exact pane/inherited passthrough state for the current tutor."""
    target = _tmux_target_from_environment()
    if target is None:
        return None
    identity = _inspect_tmux_pane(target)
    pane_explicit = _tmux_option(target, "-p", "-qv", "-t", target["pane_id"])
    pane_effective = _tmux_option(target, "-p", "-Aqv", "-t", target["pane_id"])
    window_explicit = _tmux_option(target, "-w", "-qv", "-t", target["pane_id"])
    window_effective = _tmux_option(target, "-w", "-Aqv", "-t", target["pane_id"])
    global_default = _tmux_option(target, "-gwqv")
    if pane_effective not in _PASSTHROUGH_VALUES:
        raise RuntimeError(
            "Native tmux passthrough could not inspect the effective pane setting."
        )
    if window_effective not in _PASSTHROUGH_VALUES or global_default not in _PASSTHROUGH_VALUES:
        raise RuntimeError(
            "Native tmux passthrough could not inspect the inherited setting."
        )
    return {
        "target": target,
        "identity": identity,
        "pane_explicit": pane_explicit,
        "pane_effective": pane_effective,
        "window_explicit": window_explicit,
        "window_effective": window_effective,
        "global_default": global_default,
    }


def _restore_tmux_pane_option(target, value):
    if value:
        _tmux_call(
            target,
            "set-option",
            "-p",
            "-t",
            target["pane_id"],
            "allow-passthrough",
            value,
        )
    else:
        _tmux_call(
            target,
            "set-option",
            "-pu",
            "-t",
            target["pane_id"],
            "allow-passthrough",
        )


@contextmanager
def temporary_tmux_passthrough():
    """Temporarily allow Kitty passthrough on only the exact tutor pane.

    The inherited pane/window/global values are read before mutation.  A
    missing explicit pane value is restored by unsetting only that pane value;
    an explicit value is restored verbatim.  No ``-g`` mutation is performed.
    """
    target = _tmux_target_from_environment()
    if target is None:
        yield None
        return

    before = inspect_tmux_passthrough()
    if before["target"] != target:
        raise RuntimeError("Native tmux passthrough target changed during inspection.")
    needs_override = before["pane_effective"] not in ("on", "all")
    try:
        if needs_override:
            _tmux_call(
                target,
                "set-option",
                "-p",
                "-t",
                target["pane_id"],
                "allow-passthrough",
                "on",
            )
        yield before
    finally:
        restore_error = None
        try:
            current_explicit = _tmux_option(
                target, "-p", "-qv", "-t", target["pane_id"]
            )
            if needs_override or current_explicit != before["pane_explicit"]:
                _restore_tmux_pane_option(target, before["pane_explicit"])
            after = inspect_tmux_passthrough()
            expected_keys = (
                "pane_explicit",
                "pane_effective",
                "window_explicit",
                "window_effective",
                "global_default",
            )
            mismatches = [
                f"{key} before={before[key]!r} after={after[key]!r}"
                for key in expected_keys
                if before[key] != after[key]
            ]
            if mismatches:
                raise RuntimeError(
                    "Native tmux passthrough restoration mismatch: "
                    + "; ".join(mismatches)
                )
        except Exception as exc:
            restore_error = exc
        if restore_error is not None:
            raise RuntimeError(
                "Native tmux passthrough could not restore the exact tutor-pane "
                "state: " + str(restore_error)
            ) from restore_error


def graphics_chunks(png, image_id, *, tmux=False):
    """Direct PNG transfer, bounded base64 chunks, no shared filesystem."""
    payload = base64.b64encode(png)
    for offset in range(0, len(payload), 4096):
        chunk = payload[offset:offset + 4096]
        more = int(offset + 4096 < len(payload))
        control = f"a=T,f=100,t=d,i={image_id},m={more}" if offset == 0 else f"m={more}"
        packet = b"\x1b_G" + control.encode("ascii") + b";" + chunk + b"\x1b\\"
        if tmux:
            packet = b"\x1bPtmux;" + packet.replace(b"\x1b", b"\x1b\x1b") + b"\x1b\\"
        yield packet


def transmit_png(png, image_id, *, timeout=2):
    """Require an exact positive response from the terminal for this image."""
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise RuntimeError("Native terminal preview requires an interactive terminal.")
    fd = sys.stdin.fileno()
    previous = termios.tcgetattr(fd)
    response = bytearray()
    try:
        tty.setraw(fd)
        for packet in graphics_chunks(png, image_id, tmux=bool(os.environ.get("TMUX"))):
            sys.stdout.buffer.write(packet)
        sys.stdout.buffer.flush()
        deadline = time.monotonic() + timeout
        pattern = re.compile(rb"\x1b_G(?:[^;]*,)?i=" + str(image_id).encode() + rb"(?:,[^;]*)?;([^\x1b]+)\x1b\\")
        while time.monotonic() < deadline:
            if not select.select([fd], [], [], max(0, deadline - time.monotonic()))[0]:
                break
            response.extend(os.read(fd, 4096))
            match = pattern.search(response)
            if match:
                if match.group(1) != b"OK":
                    raise RuntimeError("Terminal rejected native image: " + match.group(1).decode("ascii", "replace"))
                return {"image_id": image_id, "png_sha256": hashlib.sha256(png).hexdigest(), "terminal_reply": "OK"}
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, previous)
    raise RuntimeError("No graphics acknowledgement. Ghostty must receive Kitty graphics; a tmux path must permit passthrough. No configuration was changed.")


class TerminalPreview(TutorPreview):
    """Before-edit and before-credit terminal display; never opens a browser."""
    def __init__(self, *args, sender=None, confirm=None, **kwargs):
        kwargs.pop("open_browser", None)
        super().__init__(*args, open_browser=False, **kwargs)
        self.sender = sender or transmit_png
        self.confirm = confirm or input
        self.display = None

    def start(self):
        self.refresh()
        self.show_current("BEFORE EDITING · inspect the native target")
        return self

    @property
    def url(self):
        return "Ghostty · native terminal graphics"

    def show_current(self, heading):
        self.refresh()
        identity = native._preview_identity(self.payload)
        print("\n" + heading + " · Saitamaar 16 px / 17 px pitch")
        panels = [(name, self.payload[name.lower()]["png_data_url"])
                  for name in ("BEFORE", "YOURS", "TARGET")]
        panels.append(("CHANGED PIXELS", self.payload["difference"]["png_data_url"]))
        receipts = []
        with temporary_tmux_passthrough():
            for name, data_url in panels:
                print("\n" + name, flush=True)
                png = base64.b64decode(data_url.split(",", 1)[1], validate=True)
                image_id = secrets.randbelow(2**30 - 1) + 1
                receipt = self.sender(png, image_id)
                if (receipt.get("image_id") != image_id or receipt.get("terminal_reply") != "OK"
                        or receipt.get("png_sha256") != hashlib.sha256(png).hexdigest()):
                    raise RuntimeError("Terminal acknowledgement does not bind this native PNG.")
                receipts.append(receipt)
                print()
            answer = self.confirm("Enter = inspected these four native panels · q = cancel ")
        self.refresh()
        if answer.strip() or native._preview_identity(self.payload) != identity:
            self.display = None
            raise RuntimeError("Native display cancelled or artifact changed; inspect the current version.")
        self.display = {"identity": identity, "basis": "terminal-four-native-png-acknowledgements-and-confirmation", "images": receipts}
        return self.display

    def final_receipt(self, **_kwargs):
        self.show_current("BEFORE CREDIT · inspect your saved work and the native diff")
        gate = self.payload["gate"]
        final_hash = hashlib.sha256(self.path.read_bytes()).hexdigest()
        ready = bool(self.display and gate["fresh_receipt"] and gate["transcription_ready"]
                     and gate["visual_equal"] and gate["join_contract_passed"] and final_hash == self._byte_hash)
        reasons = list(gate["reasons"])
        if final_hash != self._byte_hash:
            reasons.append("Artifact changed after its final native display; inspect the current version.")
        return {"schema": "vim-daily/proportional-attempt@1", "ready": ready,
                "reasons": reasons, "artifact_sha256": final_hash,
                "receipt": self.payload["receipt"], "gate": gate, "display": self.display,
                "join_registration": self.payload["join_evaluation"],
                "operator_visual_acceptance": "required",
                "acceptance_basis": "transcription, native raster, measured target registration, terminal display"}
