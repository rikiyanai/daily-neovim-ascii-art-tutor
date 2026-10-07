"""Tutor integration for strict bytes and displayed native-font previews.

The byte codec, raster, and token-protected surface belong to sjis_authoring.
This adapter owns the editor-file lifecycle and the actual display requirement.
Automated display evidence never implies a human has accepted artistic joins.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import webbrowser

import sjis_authoring as native


def art_text(rows):
    """Match the tutor's UTF-8 LF artifact, retaining every row-space."""
    return "\n".join(rows) + "\n"


def target_registration_contract(target, metrics):
    """Pin visible glyph starts to the authored target's advance lattice.

    This measures registration, not inferred artist intent or whether a contour
    should be continuous. The browser presents the raster for that human review.
    A terminal-column match is insufficient for these native positions.
    """
    raster = native.render_text(target, metrics)
    anchors = [native.JoinAnchor(
        name=f"target-glyph-{p.row}-{p.column}", row=p.row, column=p.column,
        expected_x_units=p.x_units, expected_y_px=p.y_px, require_ink=True,
    ) for p in raster.placements if p.ink_bbox is not None]
    return native.make_join_contract(target, metrics, anchors)


def write_receipt(path, receipt):
    """Write only to the caller's declared attempt evidence path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=path.parent, delete=False) as output:
            name = output.name
            json.dump(receipt, output, ensure_ascii=False, indent=2)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(name, path)
        name = None
    finally:
        if name is not None:
            Path(name).unlink(missing_ok=True)


class TutorPreview:
    """One editor attempt; disk updates invalidate prior display receipts."""

    def __init__(self, path, target_rows, *, before_rows=None, source=None,
                 font_path=None, open_browser=True, target_text=None):
        self.path = Path(path)
        self.source = source or native.artifact_from_text(
            art_text(before_rows) if before_rows is not None
            else native.import_artifact(self.path, encoding="utf-8").text,
            encoding="utf-8")
        self.target = art_text(target_rows) if target_text is None else target_text
        selected_font = (font_path or os.environ.get("VIM_DAILY_SAITAMAAR_FONT")
                         or native.DEFAULT_FONT_PATH)
        self.metrics = native.load_font_metrics(selected_font)
        self.contract = target_registration_contract(self.target, self.metrics)
        self.open_browser = open_browser
        self.server = None
        self.payload = None
        self.error = None
        self._byte_hash = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._thread = None

    def refresh(self):
        """Strictly decode the working UTF-8 file; never trim or repair it."""
        with self._lock:
            if native._sha256(Path(self.metrics.font_path).read_bytes()) != self.metrics.font_sha256:
                self.error = "Measured font changed; restart the preview with the current font."
                raise native.FontUnavailableError(self.error)
            raw = self.path.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            if digest == self._byte_hash and self.error is None:
                return self.payload
            try:
                yours = native.TextArtifact.from_bytes(raw, encoding="utf-8").text
                payload = native.build_preview_payload(
                    self.source, yours, self.target, self.metrics,
                    join_contract=self.contract)
                if self.server:
                    self.server.update(payload)
                self.payload = payload
                self._byte_hash = digest
                self.error = None
                return payload
            except (native.AuthoringError, OSError) as exc:
                self.error = str(exc)
                self._byte_hash = None
                raise

    def _watch(self):
        while not self._stop.wait(0.2):
            try:
                self.refresh()
            except (native.AuthoringError, OSError):
                # A partially written editor file may be temporarily invalid.
                # It cannot receive credit; final_receipt rechecks actual bytes.
                pass

    def start(self):
        self.refresh()
        self.server = native.serve_preview(self.payload)
        self._thread = threading.Thread(target=self._watch,
                                        name="tutor-native-preview", daemon=True)
        self._thread.start()
        if self.open_browser:
            webbrowser.open(self.server.url)
        return self

    @property
    def url(self):
        return self.server.url if self.server else None

    def final_receipt(self, *, display_timeout=5):
        """Grade current bytes and require the browser to display those bytes."""
        self.refresh()
        deadline = time.monotonic() + max(0, display_timeout)
        displayed = None
        while self.server:
            displayed = self.server.displayed_receipt()
            if displayed or time.monotonic() >= deadline:
                break
            time.sleep(0.1)
            self.refresh()
        # A disk edit during the wait must invalidate an earlier browser ACK.
        self.refresh()
        displayed = self.server.displayed_receipt() if self.server else None
        payload = self.payload
        gate = payload["gate"]
        reasons = list(gate["reasons"])
        if not displayed:
            reasons.append("Open the native preview and wait for the current four images and font to load before submitting.")
        ready = bool(displayed and gate["fresh_receipt"]
                     and gate["transcription_ready"] and gate["visual_equal"]
                     and gate["join_contract_passed"])
        final_hash = hashlib.sha256(self.path.read_bytes()).hexdigest()
        if final_hash != self._byte_hash:
            ready = False
            reasons.append("Artifact changed after its final preview; display the new version before submitting.")
        return {
            "schema": "vim-daily/proportional-attempt@1",
            "ready": ready, "reasons": reasons,
            "artifact_sha256": final_hash,
            "receipt": payload["receipt"], "gate": gate,
            "display": displayed,
            "join_registration": payload["join_evaluation"],
            "operator_visual_acceptance": "required",
            "acceptance_basis": "transcription, native raster, measured target registration, browser display",
        }

    def close(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
        if self.server:
            self.server.close()

    def __enter__(self):
        return self.start()

    def __exit__(self, *exc):
        self.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Strict proportional-art import, export, and native preview")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("import", "export"):
        action = commands.add_parser(name)
        action.add_argument("--source", required=True, type=Path)
        action.add_argument("--source-encoding", required=True, choices=native.SUPPORTED_ENCODINGS)
        action.add_argument("--output", required=True, type=Path)
        action.add_argument("--output-encoding", required=True, choices=native.SUPPORTED_ENCODINGS)
        action.add_argument("--overwrite", action="store_true")
    preview = commands.add_parser("preview")
    preview.add_argument("--source", required=True, type=Path)
    preview.add_argument("--source-encoding", required=True, choices=native.SUPPORTED_ENCODINGS)
    preview.add_argument("--yours", required=True, type=Path, help="Working UTF-8 editor file")
    preview.add_argument("--target", required=True, type=Path)
    preview.add_argument("--target-encoding", required=True, choices=native.SUPPORTED_ENCODINGS)
    preview.add_argument("--font", type=Path)
    preview.add_argument("--receipt", required=True, type=Path)
    preview.add_argument("--surface", choices=("terminal", "browser"), default="terminal")
    args = parser.parse_args(argv)
    try:
        source = native.import_artifact(args.source, encoding=args.source_encoding)
        if args.command in ("import", "export"):
            receipt = native.export_artifact(source, args.output,
                encoding=args.output_encoding, overwrite=args.overwrite)
            print(json.dumps(asdict(receipt), ensure_ascii=False, indent=2))
            return 0
        target = native.import_artifact(args.target, encoding=args.target_encoding)
        # Explicit preview files preserve their final newline through rows.
        target_rows = target.text.removesuffix("\n").split("\n")
        if args.surface == "terminal":
            from sjis_terminal import TerminalPreview
            factory = TerminalPreview
        else:
            factory = TutorPreview
        with factory(args.yours, target_rows, source=source,
                          font_path=args.font, target_text=target.text) as session:
            print("Native proportional preview: " + session.url)
            input("Inspect BEFORE / YOURS / TARGET and native differences. Press Enter to check submission: ")
            receipt = session.final_receipt()
            write_receipt(args.receipt, receipt)
            print(json.dumps(receipt, ensure_ascii=False, indent=2))
            return 0 if receipt["ready"] else 1
    except (native.AuthoringError, OSError, RuntimeError, EOFError) as exc:
        print("Proportional authoring refused: " + str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
