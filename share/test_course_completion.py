#!/usr/bin/env python3
"""Focused regression checks for the §9.5 course-completion handoff.

These checks build the curriculum in memory.  They deliberately do not write
``curriculum-v2.json``; the installed generated artifact and its count/route
fixtures belong to the integration lane.
"""

import importlib.util
import json
import shutil
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


generator = load_module("course_completion_generator", HERE / "gen_curriculum_v2.py")
runtime = load_module("course_completion_runtime", HERE / "v2_runtime.py")
keys = load_module("course_completion_keys", HERE / "v2_keys.py")


class CourseCompletionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.curriculum = generator.build()
        cls.cards = cls.curriculum["cards"]
        cls.by_id = {card["id"]: card for card in cls.cards}
        cls.artifact = json.loads(
            (HERE / "curriculum-v2.json").read_text(encoding="utf-8"))
        cls.artifact_by_id = {card["id"]: card for card in cls.artifact["cards"]}
        cls.questions = {question["id"]: question
                         for question in cls.curriculum["questions"]}
        generator.validate(cls.curriculum)

    def test_one_concept_bridges_and_order(self):
        self.assertEqual(runtime._new_concepts(self.by_id["M4.DIFF"], self.curriculum), [])
        for card_id in ("M4.SIL", "M4.TRIM", "M4.SCB", "M11.GM", "M11.GP"):
            self.assertLessEqual(len(runtime._new_concepts(
                self.by_id[card_id], self.curriculum)), 1, card_id)
        # The counted WORD step is now taught earlier by the required d2W
        # contrast; BE still supplies the W/E/2W performance before hidden B,
        # but it should not be reported as a second NEW concept.
        self.assertEqual([family for family, _ in runtime._new_concepts(
            self.by_id["M13.BE"], self.curriculum)], [])
        self.assertEqual([family for family, _ in runtime._new_concepts(
            self.by_id["M13.BEB"], self.curriculum)], ["B"])
        self.assertEqual([family for family, _ in runtime._new_concepts(
            self.by_id["M16.INC"], self.curriculum)], ["[count]<C-a>"])
        self.assertEqual([family for family, _ in runtime._new_concepts(
            self.by_id["M15.MAC3"], self.curriculum)], ["[count]@{reg}"])
        self.assertEqual([family for family, _ in runtime._new_concepts(
            self.by_id["M15.MACR"], self.curriculum)], ["q{reg}...q"])
        self.assertEqual([family for family, _ in runtime._new_concepts(
            self.by_id["M15.MAC"], self.curriculum)], ["@{reg}"])
        order = {card["id"]: index for index, card in enumerate(self.cards)}
        self.assertLess(order["M16.INC"], order["M16.04"])
        self.assertLess(order["M15.MACR"], order["M15.MAC"])
        self.assertLess(order["M15.MAC"], order["M15.MAC3"])
        self.assertLess(order["M15.MAC3"], order["M15.08"])
        self.assertLess(order["M13.BE"], order["M13.04"])
        self.assertLess(order["M13.BEB"], order["M13.04"])
        self.assertLess(order["M2.TEN"], order["M2.08"])

    def test_authored_hints_contracts_and_placeholders(self):
        self.assertFalse(any("Vim toolbox" in card.get("hint", "")
                             for card in self.cards))
        self.assertFalse(any("qq ... q / 3@q" in repr(card)
                             for card in self.cards))
        self.assertTrue(all(card.get("preserve_trailing_whitespace")
                            for card in self.cards if card["module_id"] == "M10"))
        for card_id in ("M2.TEN", "M4.SIL", "M4.TRIM", "M4.SCB",
                        "M11.GP", "M13.BEB", "M15.MACR"):
            card = self.by_id[card_id]
            self.assertTrue(card.get("source"), card_id)
            question_id = card["paired_question_ids"][0]
            self.assertEqual(self.questions[question_id]["authorship"], "manual")
            self.assertTrue(self.questions[question_id]["source_ref"])
            self.assertEqual(len(self.questions[question_id]["feedback"]), 4)

    def test_split_history_and_range_delete_teaching(self):
        self.assertIn("g-", self.by_id["M11.GM"]["expected"])
        self.assertNotIn("g+", self.by_id["M11.GM"]["expected"])
        self.assertNotIn("g+", self.by_id["M11.GM"]["hint"])
        # GM stops on a real abandoned half-blink source frame. GP owns the
        # separate forward return; neither teaches an invented punctuation eye.
        self.assertTrue(any(",=-" in row for row in self.by_id["M11.GM"]["target"]))
        self.assertIn("half-blink source frame", self.questions["M11.GM.P01"]["prompt"])
        self.assertNotEqual(self.questions["M11.GM.P01"]["prompt"],
                            self.questions["M11.GM.P01"]["compact_prompt"])
        self.assertIn("g+", self.by_id["M11.GP"]["expected"])
        self.assertNotIn("qq ... q / 3@q", repr(self.by_id["M15.08"]))
        self.assertIn(":2,3d", keys.EXAMPLES[":[range]d"])
        self.assertIn("inclusive", keys.FAMILY_TEACH[":[range]d"])

    def test_history_recipe_is_not_an_exact_transcript_requirement(self):
        expected = {
            "M11.BR": ["u"],
            "M11.GM": ["g-"],
            "M11.GP": ["g+"],
            "M11.ER": [":earlier 1<CR>", "g+"],
            "M11.UB": ["u"],
            "M11.UG": ["g-", "g+"],
            "M11.UE": [":earlier 1<CR>", "g+"],
            "M11.UT": ["g-", "g+"],
            "M11.UTH": ["g-", "g+"],
        }
        for cid, commands in expected.items():
            requirement = self.by_id[cid]["method_requirement"]
            self.assertEqual(requirement["all_of"], commands, cid)
            self.assertNotIn("exact_any_of", requirement, cid)
            self.assertNotIn("any_of", requirement, cid)
        self.assertIn("Skully", self.by_id["M11.BR"]["title"])
        self.assertNotIn("Frog", self.by_id["M11.BR"]["title"])
        self.assertIn("Skully", self.by_id["M11.BR"]["source_motion"]["credit"])
        self.assertIn("Skully", self.by_id["M11.UT"]["source_motion"]["credit"])
        self.assertTrue(self.by_id["M11.UTH"]["review_variants"])
        self.assertEqual(self.by_id["M11.UT"]["artifact_mode"], "still-study")
        self.assertEqual(self.by_id["M11.UTH"]["artifact_mode"], "still-study")
        self.assertTrue(all(
            variant["method_requirement"]["all_of"] == expected["M11.UTH"]
            and "exact_any_of" not in variant["method_requirement"]
            for variant in self.by_id["M11.UTH"]["review_variants"]))
        if shutil.which("nvim"):
            card = self.by_id["M11.GP"]
            # A line-search path reaches the same acting eye. Extra history
            # travel is allowed; the chosen state still must match the target.
            ok, _, detail = runtime._safe_typed_effect(
                {"initial_lines": card["start"], "target_lines": card["target"]},
                "1G:s/O/=/g<CR>u1G:s/O/-/g<CR>g-g-g+g+")
            self.assertTrue(ok, detail)
            card = self.by_id["M11.GM"]
            ok, _, detail = runtime._safe_typed_effect(
                {"initial_lines": card["start"], "target_lines": card["target"]},
                card["expected"])
            self.assertTrue(ok, detail)

    def test_two_take_history_comparisons_replay_in_nvim(self):
        """The generated artifact's cumulative cards and reviews replay in Neovim."""
        if not shutil.which("nvim"):
            self.skipTest("Neovim is unavailable for bounded semantic-effect proof")
        samples = []
        for card_id in ("M11.UT", "M11.UTH"):
            card = self.artifact_by_id[card_id]
            samples.append((card_id, card))
            samples.extend(
                ("%s.review%d" % (card_id, index), variant)
                for index, variant in enumerate(card.get("review_variants", []), 1)
            )
        for label, sample in samples:
            from history_source_frames import HISTORY_CARD_CHARACTERS, frame_sequence_matches
            self.assertEqual(len(sample["target"]) % 3, 0, label)
            self.assertGreaterEqual(len(sample["target"]), 6, label)
            frames = [tuple(sample["target"][i:i + 3])
                      for i in range(0, len(sample["target"]), 3)]
            self.assertGreaterEqual(len(set(frames)), 2, label)
            self.assertTrue(frame_sequence_matches(sample["target"],
                            HISTORY_CARD_CHARACTERS[label.split(".review")[0]]), label)
            ok, _evidence, detail = runtime._safe_typed_effect(
                {"initial_lines": sample["start"],
                 "target_lines": sample["target"]}, sample["expected"])
            self.assertTrue(ok, (label, detail))

    def test_authored_box_rows_have_stable_inner_width(self):
        for question_id in ("M11.GM.P01", "M11.ER.P01", "M11.06.P01"):
            question = self.questions[question_id]
            for line in question["prompt"].splitlines():
                if "│" in line:
                    cells = line.split("│")[1::2]
                    self.assertTrue(cells and len(set(map(len, cells))) == 1,
                                    (question_id, line, cells))

    def test_legacy_gap_pairs_are_executable_and_changed_art_required(self):
        pairs = {
            "delete-word": ("M2.DW", "M2.DWH"),
            "delete-to-word-end": ("M2.DE", "M2.DEH"),
            "count-motion": ("M2.D2W", "M2.D2WH"),
            "change-word": ("M3.CW", "M3.CWH"),
            "text-object-paren": ("M3.CA", "M3.CAH"),
            "yank-register-0": ("M3.Y0", "M3.Y0H"),
            "marks": ("M3.MARK", "M3.MARKH"),
            "visual-delete": ("M3.VD", "M3.VDH"),
            "block-erase": ("M4.BD", "M4.BDH"),
            "join": ("M6.J", "M6.JH"),
            "playback-order": ("M6.DDP", "M6.DDPH"),
            "toggle-case": ("M7.GTC", "M7.GTCH"),
            "open-line": ("M8.O", "M8.OH"),
            "pad-frames": ("M8.PAD", "M8.PADH"),
            "append": ("M15.APPA", "M15.APPAH"),
        }
        for legacy_name, (guided_id, hidden_id) in pairs.items():
            guided, hidden = self.by_id[guided_id], self.by_id[hidden_id]
            self.assertNotEqual(guided["start"], guided["target"], legacy_name)
            self.assertNotEqual(hidden["start"], hidden["target"], legacy_name)
            self.assertNotEqual(guided["start"], hidden["start"], legacy_name)
            self.assertEqual(guided["grammar_stage"], "guided", legacy_name)
            self.assertEqual(hidden["grammar_stage"], "hidden", legacy_name)
            self.assertFalse(hidden["show_recipe"], legacy_name)
            self.assertTrue(hidden["required_before_mastery"], legacy_name)
            self.assertEqual(hidden["method_requirement"]["exact_any_of"],
                             [hidden["expected"]], legacy_name)
            self.assertGreaterEqual(len(hidden["review_variants"]), 2, legacy_name)
            for variant in hidden["review_variants"]:
                self.assertNotEqual(variant["start"], variant["target"], legacy_name)
                self.assertEqual(variant["method_requirement"]["exact_any_of"],
                                 [variant["expected"]], legacy_name)
            for card in (guided, hidden):
                question = self.questions[card["paired_question_ids"][0]]
                self.assertEqual(question["authorship"], "manual", legacy_name)
                self.assertTrue(question["source_ref"], legacy_name)
                self.assertEqual(len(question["feedback"]), 4, legacy_name)
                self.assertEqual(len(question["choices"]), 4, legacy_name)

    def test_legacy_gap_effects_and_hidden_changed_retrieval_run_in_nvim(self):
        """Exercise each newly executable family, including both review variants."""
        if not shutil.which("nvim"):
            self.skipTest("Neovim is unavailable for bounded semantic-effect proof")
        pairs = (
            ("M2.DW", "M2.DWH"), ("M2.DE", "M2.DEH"),
            ("M2.D2W", "M2.D2WH"), ("M3.CW", "M3.CWH"),
            ("M3.CA", "M3.CAH"), ("M3.Y0", "M3.Y0H"),
            ("M3.MARK", "M3.MARKH"), ("M3.VD", "M3.VDH"),
            ("M4.BD", "M4.BDH"), ("M6.J", "M6.JH"),
            ("M6.DDP", "M6.DDPH"), ("M7.TC", "M7.TCH"),
            ("M7.GTC", "M7.GTCH"), ("M8.O", "M8.OH"),
            ("M8.PAD", "M8.PADH"), ("M15.APP", "M15.APPH"),
            ("M15.APPA", "M15.APPAH"),
        )
        for guided_id, hidden_id in pairs:
            guided, hidden = self.by_id[guided_id], self.by_id[hidden_id]
            ok, _evidence, detail = runtime._safe_typed_effect(
                {"initial_lines": guided["start"], "target_lines": guided["target"]},
                guided["expected"])
            self.assertTrue(ok, (guided_id, detail))
            ok, _evidence, detail = runtime._safe_typed_effect(
                {"initial_lines": hidden["start"], "target_lines": hidden["target"]},
                hidden["expected"])
            self.assertTrue(ok, (hidden_id, detail))
            for index, variant in enumerate(hidden["review_variants"], 1):
                ok, _evidence, detail = runtime._safe_typed_effect(
                    {"initial_lines": variant["start"],
                     "target_lines": variant["target"]}, variant["expected"])
                self.assertTrue(ok, (hidden_id, index, detail))

    def test_completion_pairs_are_distinct_authored_question_records(self):
        card_ids = (
            "M2.DW", "M2.DE", "M2.D2W", "M3.CW", "M3.CA", "M3.Y0",
            "M3.MARK", "M3.VD", "M4.BD", "M6.J", "M6.DDP", "M7.TC",
            "M7.GTC", "M8.O", "M8.PAD", "M15.APP", "M15.APPA",
            "M2.DWH", "M2.DEH", "M2.D2WH", "M3.CWH", "M3.CAH", "M3.Y0H",
            "M3.MARKH", "M3.VDH", "M4.BDH", "M6.JH", "M6.DDPH", "M7.TCH",
            "M7.GTCH", "M8.OH", "M8.PADH", "M15.APPH", "M15.APPAH",
        )
        questions = [self.questions[self.by_id[card_id]["paired_question_ids"][0]]
                     for card_id in card_ids]
        self.assertEqual(len(questions), len({question["id"] for question in questions}))
        self.assertEqual(len(questions), len({question["prompt"] for question in questions}))
        self.assertTrue(all(question["authorship"] == "manual" for question in questions))

    def test_retained_families_are_explicitly_mapped(self):
        self.assertIn("<C-v>", self.by_id["M4.BI"]["expected"])
        self.assertIn("I", self.by_id["M4.BI"]["expected"])
        self.assertIn("a", self.by_id["M15.APP"]["expected"])
        self.assertIn("A", self.by_id["M15.APPA"]["expected"])
        self.assertIn("J", self.by_id["M6.J"]["expected"])
        self.assertIn("g~", self.by_id["M7.GTC"]["expected"])
        self.assertLess(
            next(i for i, card in enumerate(self.cards) if card["id"] == "M4.BD"),
            next(i for i, card in enumerate(self.cards) if card["id"] == "M4.BC"),
        )

    def test_legacy_parity_map_uses_executable_completion_cards(self):
        expected = {
            "delete-word": "M2.DW", "count-motion": "M2.D2W",
            "change-word": "M3.CW", "text-object-paren": "M3.CA",
            "yank-register-0": "M3.Y0", "marks": "M3.MARK",
            "visual-delete": "M3.VD", "block-insert": "M4.BI",
            "block-erase": "M4.BD", "join": "M6.J",
            "candle-join": "M6.J", "playback-order": "M6.DDP",
            "toggle-case": "M7.TC", "open-line": "M8.O",
            "pad-frames": "M8.PAD", "append": "M15.APP",
        }
        for legacy_id, card_id in expected.items():
            self.assertEqual(generator.LEGACY_CARD_MAP[legacy_id], card_id)
            self.assertEqual(self.by_id[card_id]["grammar_stage"], "guided")


if __name__ == "__main__":
    unittest.main()
