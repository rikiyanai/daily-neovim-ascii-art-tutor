"""Connected strict-byte and browser-display protocol controls.

HTTP acknowledgements below are protocol fixtures, not operator acceptance.
The real page sends its ACK only after font and all native images load.
"""
import json
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import sjis_authoring as native
import sjis_tutor as tutor


def acknowledge(session, identity=None):
    identity = identity or native._preview_identity(session.payload)
    request = Request(session.url.replace("/?", "/api/seen?"),
                      data=json.dumps(identity).encode(), method="POST",
                      headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=2) as response:
        return json.load(response)


class TutorNativeTests(unittest.TestCase):
    def test_no_display_get_only_stale_and_fresh_controls(self):
        rows = ["　⌒ヽ ", "　ヽ_ノ"]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "art.txt"
            path.write_text(tutor.art_text(rows), encoding="utf-8")
            with tutor.TutorPreview(path, rows, open_browser=False) as session:
                first = session.final_receipt(display_timeout=0)
                self.assertFalse(first["ready"])
                with urlopen(session.url, timeout=2) as response:
                    self.assertIn(b"BEFORE", response.read())
                self.assertFalse(session.final_receipt(display_timeout=0)["ready"])
                self.assertEqual(acknowledge(session), {"displayed": True})
                final = session.final_receipt(display_timeout=0)
                self.assertTrue(final["ready"])
                self.assertEqual(final["operator_visual_acceptance"], "required")
                self.assertEqual(final["display"]["basis"], "browser-font-and-four-native-images-loaded")
                old_identity = native._preview_identity(session.payload)
                path.write_text(tutor.art_text([rows[0] + "　", rows[1]]), encoding="utf-8")
                session.refresh()
                self.assertFalse(session.final_receipt(display_timeout=0)["ready"])
                with self.assertRaises(HTTPError) as stale:
                    acknowledge(session, old_identity)
                self.assertEqual(stale.exception.code, 409)
                stale.exception.close()
                acknowledge(session)
                self.assertFalse(session.final_receipt(display_timeout=0)["ready"])
                path.write_text(tutor.art_text(rows), encoding="utf-8")
                session.refresh()
                # Returning to the same codepoints still needs the current display.
                self.assertIsNone(session.server.displayed_receipt())
                acknowledge(session)
                self.assertTrue(session.final_receipt(display_timeout=0)["ready"])

    def test_font_token_and_browser_assets(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "art.txt"
            path.write_text("　ヽ\n", encoding="utf-8")
            with tutor.TutorPreview(path, ["　ヽ"], open_browser=False) as session:
                with urlopen(session.url.replace("/?", "/font.ttf?"), timeout=2) as response:
                    self.assertEqual(native._sha256(response.read()), session.metrics.font_sha256)
                with self.assertRaises(HTTPError) as unauthorized:
                    urlopen(session.url.replace("/?", "/font.ttf?").replace(session.server.token, "wrong"), timeout=2)
                self.assertEqual(unauthorized.exception.code, 403)
                unauthorized.exception.close()
        js = Path(__file__).with_name("sjis_preview.js").read_text()
        css = Path(__file__).with_name("sjis_preview.css").read_text()
        self.assertIn("Promise.all(images)", js)
        self.assertIn("nativeFont.load()", js)
        self.assertIn("/api/seen?token=", js)
        self.assertIn("white-space: pre", css)
        self.assertIn("font-size: 16px; line-height: 17px", css)

    def test_mixed_font_metrics_rejected(self):
        from dataclasses import replace
        metrics = native.load_font_metrics()
        larger = replace(metrics, font_size_px=17)
        source = native.artifact_from_text("　ヽ", encoding="utf-8")
        comparison = native.compare_text_art(source.text, source.text, source.text, larger)
        with self.assertRaises(native.ReceiptError):
            native.build_preview_receipt(source, source.text, source.text, metrics, comparison)
        contract = tutor.target_registration_contract(source.text, metrics)
        with self.assertRaises(native.JoinContractError):
            native.evaluate_join_contract(source.text, source.text, larger, contract)

    def test_changed_font_refuses_cached_preview(self):
        with tempfile.TemporaryDirectory() as folder:
            font = Path(folder) / "Saitamaar.ttf"
            font.write_bytes(native.DEFAULT_FONT_PATH.read_bytes())
            path = Path(folder) / "art.txt"
            path.write_text("　ヽ\n", encoding="utf-8")
            with tutor.TutorPreview(path, ["　ヽ"], font_path=font, open_browser=False) as session:
                acknowledge(session)
                font.write_bytes(font.read_bytes() + b"\0")
                with self.assertRaises(native.FontUnavailableError):
                    session.final_receipt(display_timeout=0)

    def test_cli_strict_import_export_round_trip_and_no_overwrite(self):
        text = "　⌒ヽ　 \r\n　ヽ_ノ"
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "original.sjis"
            editable = Path(folder) / "editable.txt"
            exported = Path(folder) / "final.sjis"
            raw = text.encode("shift_jis")
            source.write_bytes(raw)
            self.assertEqual(tutor.main(["import", "--source", str(source), "--source-encoding", "shift_jis",
                "--output", str(editable), "--output-encoding", "utf-8"]), 0)
            self.assertEqual(editable.read_bytes(), text.encode("utf-8"))
            self.assertEqual(tutor.main(["export", "--source", str(editable), "--source-encoding", "utf-8",
                "--output", str(exported), "--output-encoding", "shift_jis"]), 0)
            self.assertEqual(exported.read_bytes(), raw)
            self.assertEqual(tutor.main(["export", "--source", str(editable), "--source-encoding", "utf-8",
                "--output", str(exported), "--output-encoding", "shift_jis"]), 1)
            self.assertEqual(source.read_bytes(), raw)
            self.assertEqual(exported.read_bytes(), raw)


if __name__ == "__main__":
    unittest.main(verbosity=2)
