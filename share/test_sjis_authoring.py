"""Strict, native-metric tests for :mod:`sjis_authoring`.

These tests use only the authored M10 strings already present in the tutor's
curriculum.  They do not open corpus records or perform corpus admission.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
import tempfile
import unittest
from urllib.request import urlopen
from urllib.error import HTTPError

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import sjis_authoring as sjis  # noqa: E402


M10_LOBE = "\u3000\u3000⌒ヽ\n\u3000（\u3000\u3000）\n\u3000\u3000ヽ_ノ"


class StrictEncodingTests(unittest.TestCase):
    def test_cp932_duplicate_byte_spelling_is_not_canonicalized(self):
        raw = bytes.fromhex("8790")
        self.assertNotEqual(raw.decode("cp932").encode("cp932"), raw)
        artifact = sjis.TextArtifact.from_bytes(raw, encoding="cp932")
        self.assertEqual(artifact.encode("cp932"), raw)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "exact.cp932"
            sjis.export_artifact(artifact, path, encoding="cp932")
            self.assertEqual(path.read_bytes(), raw)

    def test_round_trip_preserves_bytes_and_every_whitespace_codepoint(self) -> None:
        text = "\u3000ヽ_ノ\r\n  \t\n"
        for encoding in sjis.SUPPORTED_ENCODINGS:
            with self.subTest(encoding=encoding):
                artifact = sjis.artifact_from_text(text, encoding=encoding)
                self.assertEqual(artifact.text, text)
                self.assertEqual(artifact.source_bytes, text.encode(encoding))
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / f"source-{encoding}.txt"
                    receipt = sjis.export_artifact(
                        artifact, path, encoding=encoding
                    )
                    self.assertEqual(path.read_bytes(), artifact.source_bytes)
                    restored = sjis.import_artifact(path, encoding=encoding)
                    self.assertEqual(restored.text, text)
                    self.assertEqual(restored.byte_sha256, artifact.byte_sha256)
                    self.assertEqual(receipt.output_byte_sha256, artifact.byte_sha256)

    def test_encoding_is_required_and_unsupported_glyph_is_rejected(self) -> None:
        with self.assertRaises(sjis.EncodingPolicyError):
            sjis.artifact_from_text("ヽ", encoding="auto")
        with self.assertRaises(sjis.UnsupportedGlyphError) as raised:
            sjis.artifact_from_text("火🔥", encoding="shift_jis")
        self.assertIn("U+1F525", str(raised.exception))

    def test_export_never_overwrites_without_explicit_flag(self) -> None:
        artifact = sjis.artifact_from_text("ヽ", encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "art.txt"
            path.write_bytes(b"owner")
            with self.assertRaises(sjis.ExportExistsError):
                sjis.export_artifact(artifact, path, encoding="utf-8")
            self.assertEqual(path.read_bytes(), b"owner")
            sjis.export_artifact(artifact, path, encoding="utf-8", overwrite=True)
            self.assertEqual(path.read_bytes(), "ヽ".encode("utf-8"))
            self.assertEqual(list(Path(directory).glob(".art.txt.sjis-*")), [])


class FontAndRasterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.metrics = sjis.load_font_metrics()

    def test_native_font_identity_and_known_advances(self) -> None:
        self.assertEqual(self.metrics.units_per_em, 1280)
        self.assertEqual(self.metrics.font_size_px, 16)
        self.assertEqual(self.metrics.line_pitch_px, 17)
        self.assertEqual(self.metrics.glyph_metric("⌒").advance_units, 1280)
        self.assertEqual(self.metrics.glyph_metric("　").advance_units, 880)
        self.assertEqual(self.metrics.glyph_metric(" ").advance_units, 400)
        self.assertEqual(
            hashlib.sha256(Path(self.metrics.font_path).read_bytes()).hexdigest(),
            self.metrics.font_sha256,
        )
        with self.assertRaises(sjis.FontUnavailableError):
            sjis.load_font_metrics("/definitely/missing/Saitamaar.ttf")

    def test_missing_metrics_dependency_does_not_fallback(self) -> None:
        original = sjis.TTFont
        sjis.TTFont = None
        try:
            with self.assertRaises(sjis.DependencyMissingError):
                sjis.load_font_metrics()
        finally:
            sjis.TTFont = original

    def test_missing_raster_dependency_does_not_fallback(self) -> None:
        original = (sjis.Image, sjis.ImageDraw, sjis.ImageFont)
        sjis.Image = sjis.ImageDraw = sjis.ImageFont = None
        try:
            with self.assertRaises(sjis.DependencyMissingError):
                sjis.render_text("ヽ", self.metrics)
        finally:
            sjis.Image, sjis.ImageDraw, sjis.ImageFont = original

    def test_same_and_different_true_advance_rasters(self) -> None:
        same = sjis.compare_text_art(M10_LOBE, M10_LOBE, M10_LOBE, self.metrics)
        self.assertTrue(same.text_equal)
        self.assertTrue(same.yours_vs_target.visual_equal)
        self.assertEqual(same.yours_vs_target.changed_pixel_count, 0)
        # Full space and two half spaces occupy the same common terminal width,
        # but the native advances are 880 versus 800 units.  The bar moves.
        target = "　|"
        yours = "  |"
        changed = sjis.compare_text_art(target, yours, target, self.metrics)
        self.assertFalse(changed.text_equal)
        self.assertFalse(changed.yours_vs_target.visual_equal)
        self.assertGreater(changed.yours_vs_target.changed_pixel_count, 0)
        self.assertIsNotNone(changed.yours_vs_target.changed_bbox)

    def test_deletion_tail_is_visible_in_union_diff_extent(self) -> None:
        before = sjis.render_text("⌒ヽ", self.metrics)
        after = sjis.render_text("⌒", self.metrics)
        diff = sjis.compare_rasters(before, after)
        self.assertFalse(diff.visual_equal)
        self.assertGreater(diff.changed_pixel_count, 0)
        self.assertIsNotNone(diff.changed_bbox)

    def test_unsupported_font_glyph_is_rejected_before_render(self) -> None:
        with self.assertRaises(sjis.UnsupportedGlyphError):
            sjis.render_text("🔥", self.metrics)


class JoinAndReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.metrics = sjis.load_font_metrics()

    def _anchor_for(self, text: str, row: int, column: int) -> sjis.JoinAnchor:
        raster = sjis.render_text(text, self.metrics)
        placement = raster.placement(row, column)
        return sjis.JoinAnchor(
            name="bar-start",
            row=row,
            column=column,
            expected_x_units=placement.x_units,
            expected_y_px=placement.y_px,
            require_ink=True,
        )

    def test_join_anchor_rejects_native_misregistration_with_equal_terminal_width(self) -> None:
        target = "　|"
        anchor = self._anchor_for(target, 0, 1)
        contract = sjis.make_join_contract(target, self.metrics, [anchor])
        # U+4E8C and U+3000 both occupy two terminal columns, but their
        # Saitamaar advances are 1280 and 880 native units respectively.
        evaluation = sjis.evaluate_join_contract("二|", target, self.metrics, contract)
        self.assertFalse(evaluation.passed)
        self.assertEqual(evaluation.measurements[0].delta_x_units, 400)
        self.assertIn("native join delta", evaluation.failures[0])

    def test_stale_and_no_preview_receipts_are_not_creditable(self) -> None:
        target = "　|"
        source = sjis.artifact_from_text(target, encoding="utf-8")
        anchor = self._anchor_for(target, 0, 1)
        contract = sjis.make_join_contract(target, self.metrics, [anchor])
        comparison = sjis.compare_text_art(target, target, target, self.metrics)
        receipt = sjis.build_preview_receipt(
            source, target, target, self.metrics, comparison,
            sjis.evaluate_join_contract(target, target, self.metrics, contract),
        )
        fresh = sjis.gate_submission(receipt, source, target, target, self.metrics)
        self.assertTrue(fresh.fresh_receipt)
        self.assertTrue(fresh.transcription_ready)
        changed_source = sjis.artifact_from_text(target, encoding="cp932")
        stale = sjis.gate_submission(receipt, changed_source, target, target, self.metrics)
        self.assertFalse(stale.fresh_receipt)
        self.assertFalse(stale.transcription_ready)
        self.assertTrue(any("stale" in reason for reason in stale.reasons))
        no_preview = sjis.build_preview_receipt(
            source, target, target, self.metrics, comparison, preview_rendered=False
        )
        blocked = sjis.gate_submission(no_preview, source, target, target, self.metrics)
        self.assertFalse(blocked.preview_present)
        self.assertFalse(blocked.transcription_ready)

    def test_text_and_visual_evidence_are_independent(self) -> None:
        target = "　|"
        yours = "  |"
        source = sjis.artifact_from_text(yours, encoding="utf-8")
        comparison = sjis.compare_text_art(yours, yours, target, self.metrics)
        receipt = sjis.build_preview_receipt(
            source, yours, target, self.metrics, comparison
        )
        self.assertFalse(receipt.text_equal)
        self.assertFalse(receipt.visual_equal)
        self.assertGreater(receipt.changed_pixel_count, 0)
        trailing_space = sjis.compare_text_art("ヽ", "ヽ ", "ヽ", self.metrics)
        self.assertFalse(trailing_space.text_equal)
        self.assertTrue(trailing_space.yours_vs_target.visual_equal)
        self.assertEqual(trailing_space.yours_vs_target.changed_pixel_count, 0)

    def test_browser_payload_keeps_raw_selectable_text_and_hashes(self) -> None:
        source = sjis.artifact_from_text("\u3000| ", encoding="utf-8")
        payload = sjis.build_preview_payload(
            source, source.text, source.text, self.metrics
        )
        self.assertEqual(payload["before"]["text"], "　| ")
        self.assertEqual(payload["yours"]["text"], "　| ")
        self.assertEqual(payload["target"]["text"], "　| ")
        self.assertEqual(payload["source"]["byte_sha256"], source.byte_sha256)
        self.assertEqual(payload["font"]["font_sha256"], self.metrics.font_sha256)
        self.assertEqual(payload["receipt"]["target_text_sha256"], source.text_sha256)
        self.assertEqual(payload["difference"]["changed_pixel_count"], 0)
        self.assertEqual(payload["gate"]["operator_visual_acceptance"], "required")


class PreviewServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.metrics = sjis.load_font_metrics()

    def test_loopback_server_is_token_protected_and_local(self) -> None:
        source = sjis.artifact_from_text("ヽ", encoding="utf-8")
        payload = sjis.build_preview_payload(source, source.text, source.text, self.metrics)
        server = sjis.serve_preview(payload)
        try:
            self.assertTrue(server.url.startswith("http://127.0.0.1:"))
            try:
                urlopen(
                    f"http://127.0.0.1:{server._server.server_address[1]}"
                    "/api/preview?token=wrong",
                    timeout=2,
                )
            except HTTPError as forbidden:
                try:
                    self.assertEqual(forbidden.code, 403)
                finally:
                    forbidden.close()
            else:
                self.fail("wrong preview token unexpectedly succeeded")
            with urlopen(server.url, timeout=2) as response:
                html = response.read().decode("utf-8")
            self.assertIn("BEFORE", html)
            with urlopen(
                f"http://127.0.0.1:{server._server.server_address[1]}"
                f"/api/preview?token={server.token}",
                timeout=2,
            ) as response:
                body = response.read().decode("utf-8")
            self.assertIn("sjis-authoring-preview/v1", body)
            updated = dict(payload)
            updated["source"] = dict(payload["source"])
            updated["source"]["byte_sha256"] = "updated"
            server.update(updated)
            with urlopen(
                f"http://127.0.0.1:{server._server.server_address[1]}"
                f"/api/preview?token={server.token}",
                timeout=2,
            ) as response:
                self.assertIn("updated", response.read().decode("utf-8"))
        finally:
            server.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
