"""Focused regression for the M4.BD, M6.DDP, and M8.PAD authored studies."""

import copy
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import gen_curriculum_v2 as generator  # noqa: E402
from test_authored_review_variants import _run_clean_effect  # noqa: E402


TARGETS = ("M4.BD", "M6.DDP", "M8.PAD")


class ChangedArtPrimaryReviewRegressionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.curriculum = generator.build()
        generator.validate(cls.curriculum)
        cls.cards = {card["id"]: card for card in cls.curriculum["cards"]}
        cls.questions = {question["id"]: question
                         for question in cls.curriculum["questions"]}

    def test_review_starts_are_distinct_from_each_primary(self):
        """A changed-art review cannot reuse its card's primary start."""
        for card_id in TARGETS:
            card = self.cards[card_id]
            starts = [tuple(variant["start"])
                      for variant in card["review_variants"]]
            self.assertNotIn(tuple(card["start"]), starts, card_id)
            self.assertEqual(len(starts), len(set(starts)), card_id)

    def test_repeated_builds_do_not_mutate_authored_definitions(self):
        first = generator.build()
        original = copy.deepcopy(first)
        second = generator.build()
        self.assertEqual(first, original)
        self.assertEqual(second, original)
        card = next(row for row in first["cards"] if row["id"] == "M0.06")
        card["variants"][0]["method_requirement"]["label"] = "mutated local fixture"
        self.assertEqual(generator.build(), original)

    def test_validation_rejects_a_primary_review_collision(self):
        """The generator's negative gate catches a future primary reuse."""
        broken = copy.deepcopy(self.curriculum)
        card = next(card for card in broken["cards"] if card["id"] == "M4.BD")
        card["review_variants"][0]["start"] = list(card["start"])
        with self.assertRaises(SystemExit) as raised:
            generator.validate(broken)
        self.assertIn("M4.BD: every authored review start must differ", str(raised.exception))

    def test_primary_and_reviews_execute_their_authored_targets(self):
        """The corrected block scope and the two operation studies remain runnable."""
        for card_id in TARGETS:
            card = self.cards[card_id]
            studies = [{
                "start": card["start"],
                "target": card["target"],
                "expected": card["expected"],
            }, *card["review_variants"]]
            for index, study in enumerate(studies, 1):
                result, detail = _run_clean_effect(study)
                self.assertIsNotNone(result, (card_id, index, detail))
                self.assertEqual(result["lines"], study["target"],
                                 (card_id, index, detail))

    def test_authored_question_choices_use_current_paths(self):
        """Completion questions keep the authored command keys synchronized."""
        expected_question_keys = {
            "M4.BD": "M4.BD.P01",
            "M6.DDP": "M6.DDP.P01",
            "M8.PAD": "M8.PAD.P01",
            "M4.BDH": "M4.BDH.P01",
            "M6.DDPH": "M6.DDPH.P01",
            "M8.PADH": "M8.PADH.P01",
        }
        for card_id, question_id in expected_question_keys.items():
            card = self.cards[card_id]
            question = self.questions[question_id]
            expected = card["expected"]
            self.assertIn(expected, question["choices"][question["correct_choice"]],
                          question_id)
            self.assertIn(expected, question["neovim_answer"], question_id)


if __name__ == "__main__":
    unittest.main()
