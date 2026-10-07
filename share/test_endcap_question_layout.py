"""Actual question renderer preserves both domains in the smallest popup."""
import contextlib
import io
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import v2_runtime as R


class TerminalText(io.StringIO):
    def isatty(self):
        return True


class EndcapQuestionLayoutTests(unittest.TestCase):
    def test_all_twenty_questions_fit_with_full_clipboard_evidence(self):
        curriculum = json.loads(Path(__file__).with_name("curriculum-v2.json").read_text())
        questions = [q for q in curriculum["questions"] if ".REWARD.P" in q["id"]]
        self.assertEqual(len(questions), 20)
        for question in questions:
            with self.subTest(question=question["id"]):
                output = TerminalText()
                snapshots = []
                copied = []
                answers = iter(("y", "abcd"[question["correct_choice"]]))

                def answer(_prompt):
                    snapshots.append(output.getvalue())
                    return next(answers)

                with contextlib.redirect_stdout(output), patch(
                    "shutil.get_terminal_size", return_value=os.terminal_size((68, 20))
                ), patch.object(R, "_copy_text_to_clipboard",
                                side_effect=lambda text: copied.append(text) or True):
                    right, _ = R.ask_question(question, input_fn=answer, shuffle=False)
                self.assertTrue(right)
                rows = snapshots[0].splitlines()
                self.assertLessEqual(len(rows) + 1, 20)
                self.assertLessEqual(max(map(len, rows)), 64)
                self.assertIn("ANIMATION", snapshots[0])
                self.assertIn("NEOVIM", snapshots[0])
                self.assertIn("│", snapshots[0])
                self.assertIn(question["evidence"]["full"], copied[0])
                self.assertIn("FRAME 08", copied[0])


if __name__ == "__main__":
    unittest.main()
