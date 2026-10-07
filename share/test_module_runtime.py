"""Module reward routing fixtures; actual transport is proved separately."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import v2_runtime as runtime


class ModuleRewardRouting(unittest.TestCase):
    def test_held_feedback_names_practice_without_learner_credit(self):
        cur = json.loads((Path(runtime.__file__).parent / "curriculum-v2.json").read_text())
        card = next(card for card in cur["cards"] if card["id"] == "M10.01")
        cfg = SimpleNamespace(practice=True, colours=("",) * 6)
        with contextlib.redirect_stdout(io.StringIO()) as output:
            runtime._post_feedback(cfg, cur, card, completed=True)
        self.assertIn("PRACTICE COMPLETE", output.getvalue())
        self.assertNotIn("LESSON COMPLETE", output.getvalue())

    def test_compact_sequence_target_retains_every_plate(self):
        frames = [[" /\\ ", "(o )", " \\/ "] for _ in range(8)]
        card = {"kind": "module_reward", "target": sum(frames, []),
                "frame_slices": [3] * 8}
        shown = runtime._compact_target_lines(card, width=30)
        self.assertEqual(len(shown), 32)
        for index in range(8):
            self.assertEqual(shown[4 * index], "FRAME %02d" % (index + 1))
            self.assertEqual(shown[4 * index + 1:4 * index + 4],
                             ["  │" + row for row in frames[index]])

    def test_sequence_study_preserves_main_project_and_manifest(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-sequence-path-") as directory:
            cfg = SimpleNamespace(state=directory, practice=False)
            card = {"id": "M0.REWARD", "project_id": "spark", "module_id": "M0",
                    "artifact": "animation-study", "source_ref": "original test"}
            path = runtime._artifact_path(cfg, card)
            path.parent.mkdir(parents=True)
            main = path.parent / "strip.txt"
            manifest = path.parent / "manifest.json"
            main.write_text("old project\n")
            manifest.write_text('{"current_card":"M0.07"}')
            path.write_text("new complete sequence\n")
            runtime._update_manifest({"revision": "fixture"}, card, path)
            self.assertEqual(main.read_text(), "old project\n")
            self.assertEqual(json.loads(manifest.read_text())["current_card"], "M0.07")
            own = json.loads((path.parent / "animation-M0.REWARD-manifest.json").read_text())
            self.assertEqual(own["artifact"], path.name)

    def test_completed_native_reward_uses_scoped_transport(self):
        motion = {"frames": [["⌒ヽ"]] * 8}
        transport = Mock()
        transport.temporary_tmux_passthrough.return_value = contextlib.nullcontext()
        playback = Mock()
        def module(name):
            return {"sjis_terminal": transport, "module_native_playback": playback}[name]
        card = {"medium": "proportional-sjis", "module_reward": motion}
        with patch.object(runtime, "_native_module", side_effect=module), patch.object(
                runtime, "_textual_enabled", return_value=False):
            self.assertFalse(runtime._show_result_screen(None, None, card, None, None, True))
            playback.play.assert_called_once_with(motion)
            transport.temporary_tmux_passthrough.assert_called_once_with()
            playback.reset_mock()
            runtime._show_result_screen(None, None, card, None, None, False)
            playback.play.assert_not_called()

    def test_transport_failure_does_not_regrade(self):
        with patch.object(runtime, "_native_module", side_effect=RuntimeError("fixture denial")), \
                patch.object(runtime, "_textual_enabled", return_value=False), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            runtime._show_result_screen(None, None, {
                "medium": "proportional-sjis", "module_reward": {"frames": []}}, None, None, True)
        self.assertIn("Your grade is unchanged", output.getvalue())

    def test_actual_post_lesson_plays_native_reward_without_textual(self):
        motion = {"frames": [["⌒ヽ"]] * 8}
        transport = Mock()
        transport.temporary_tmux_passthrough.return_value = contextlib.nullcontext()
        playback = Mock()
        cfg = SimpleNamespace(feedback_rendered=Mock(), post_page_break=Mock())
        card = {"id": "M10.REWARD", "medium": "proportional-sjis",
                "module_reward": motion}
        def module(name):
            return {"sjis_terminal": transport, "module_native_playback": playback}[name]
        with patch.object(runtime, "_native_module", side_effect=module), \
                patch.object(runtime, "_textual_enabled", return_value=False), \
                patch.object(runtime, "_post_feedback") as feedback, \
                patch.object(runtime, "_post_progress") as progress, \
                patch.object(runtime, "_legacy_attempt") as attempt:
            runtime._post_lesson(cfg, None, card, None, completed=True)
            playback.play.assert_called_once_with(motion)
            feedback.assert_called_once()
            progress.assert_called_once()
            cfg.feedback_rendered.assert_called_once()
            cfg.post_page_break.assert_called_once()
            playback.reset_mock()
            runtime._post_lesson(cfg, None, card, None, completed=False)
            playback.play.assert_not_called()
            attempt.assert_called_once_with(cfg, "M10.REWARD")

    def test_native_reward_receipt_binds_actual_attempt_without_credit(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-reward-receipt-") as directory:
            keylog = Path(directory) / "keys-M10.01-attempt-0001.log"
            keylog.write_bytes(b"$r")
            transport = Mock()
            transport.temporary_tmux_passthrough.return_value = contextlib.nullcontext()
            playback = Mock()
            playback.play.return_value = {"frames": [{"terminal_reply": "OK"}],
                                          "operator_visual_acceptance": "unverified"}
            def module(name):
                return {"sjis_terminal": transport, "module_native_playback": playback}[name]
            with patch.object(runtime, "_native_module", side_effect=module), \
                    patch.object(runtime, "_textual_enabled", return_value=False):
                runtime._show_result_screen(None, {"revision": "fixture"}, {
                    "id": "M10.01", "medium": "proportional-sjis", "module_reward": {}},
                    None, {"keylog": str(keylog)}, True)
                self.assertFalse(keylog.with_suffix(".reward.json").exists())
                runtime._show_result_screen(None, {"revision": "fixture"}, {
                    "id": "M10.01", "medium": "proportional-sjis", "module_reward": {"frames": []}},
                    None, {"keylog": str(keylog)}, True)
            record = json.loads(keylog.with_suffix(".reward.json").read_text())
            self.assertEqual(record["card_id"], "M10.01")
            self.assertEqual(record["keylog_sha256"], runtime._hash_file(keylog))
            self.assertEqual(record["curriculum_revision"], "fixture")
            self.assertEqual(record["operator_visual_acceptance"], "unverified")
            self.assertFalse((Path(directory) / "events-v2.jsonl").exists())

    def test_reward_receipt_write_failure_keeps_result_surface(self):
        transport = Mock()
        transport.temporary_tmux_passthrough.return_value = contextlib.nullcontext()
        playback = Mock()
        playback.play.return_value = {"frames": []}
        cfg = SimpleNamespace(feedback_rendered=None, post_page_break=None)
        def module(name):
            return {"sjis_terminal": transport, "module_native_playback": playback}[name]
        with patch.object(runtime, "_native_module", side_effect=module), \
                patch.object(runtime, "_textual_enabled", return_value=False), \
                patch.object(runtime, "_hash_file", return_value="fixture"), \
                patch.object(runtime, "_write_lines_atomic", side_effect=OSError("fixture full disk")), \
                patch.object(runtime, "_post_feedback") as feedback, \
                patch.object(runtime, "_post_progress") as progress, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            runtime._post_lesson(cfg, {"revision": "fixture"}, {
                "id": "M10.01", "medium": "proportional-sjis", "module_reward": {"frames": []}},
                None, {"keylog": "/fixture/attempt.log"}, completed=True)
        self.assertIn("Your grade is unchanged", output.getvalue())
        feedback.assert_called_once()
        progress.assert_called_once()


if __name__ == "__main__":
    unittest.main()
