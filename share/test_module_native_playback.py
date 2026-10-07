"""Native animation ACK/cleanup fixtures, not actual Ghostty acceptance."""
import hashlib
import io
import unittest
from PIL import Image

import module_native_playback as playback


class NativePlayback(unittest.TestCase):
    def motion(self):
        return {"frames": [["　" * n + "⌒ヽ"] for n in range(8)],
                "title": "ACK protocol fixture", "credit": "Original fixture",
                "interval": 0.2}

    def test_every_frame_is_native_and_acknowledged(self):
        emitted = []
        def sender(png, image_id):
            emitted.append(png)
            return {"image_id": image_id, "terminal_reply": "OK",
                    "png_sha256": hashlib.sha256(png).hexdigest()}
        output = io.StringIO()
        receipt = playback.play(self.motion(), sender=sender, output=output, wait=lambda _: None)
        self.assertEqual(len(receipt["frames"]), 8)
        self.assertEqual(len(set(emitted)), 8)
        self.assertEqual({Image.open(io.BytesIO(png)).size for png in emitted},
                         {tuple(receipt["canvas_px"])})
        self.assertEqual(receipt["origin_px"], [0, 0])
        self.assertEqual(receipt["operator_visual_acceptance"], "unverified")
        for index, item in enumerate(receipt["frames"]):
            text = "\n".join(self.motion()["frames"][index]) + "\n"
            self.assertEqual(item["canonical_text_sha256"], hashlib.sha256(text.encode()).hexdigest())
            self.assertEqual(item["authored_hold_seconds"], 0.2)
            self.assertGreaterEqual(item["elapsed_hold_seconds"], 0)
        self.assertIn("not learner output", output.getvalue())
        self.assertEqual(output.getvalue().count("a=d,d=i"), 9)
        self.assertTrue(output.getvalue().endswith("\x1b[u\n"))

    def test_unbound_ack_fails_and_clears_image(self):
        output = io.StringIO()
        with self.assertRaisesRegex(RuntimeError, "does not bind"):
            playback.play(self.motion(), sender=lambda *_: {}, output=output, wait=lambda _: None)
        self.assertEqual(output.getvalue().count("a=d,d=i"), 2)
        self.assertTrue(output.getvalue().endswith("\x1b[u\n"))

    def test_authored_fps_is_not_replaced_with_default(self):
        motion = dict(self.motion(), interval={"fps": 8, "duration_seconds": 1})
        waits = []
        def sender(png, image_id):
            return {"image_id": image_id, "terminal_reply": "OK",
                    "png_sha256": hashlib.sha256(png).hexdigest()}
        playback.play(motion, sender=sender, output=io.StringIO(), wait=waits.append)
        self.assertEqual(waits, [0.125] * 8)


if __name__ == "__main__":
    unittest.main()
