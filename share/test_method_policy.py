"""Pure coverage and regression tests for :mod:`method_policy`."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from types import SimpleNamespace
import v2_keys as K
import v2_runtime as R

try:
    from method_policy import explicit_card_ids, taught_paths
except ImportError:  # pragma: no cover - supports ``python share/test_...py``.
    from share.method_policy import explicit_card_ids, taught_paths


ROOT = Path(__file__).resolve().parent
CURRICULUM = json.loads((ROOT / "curriculum-v2.json").read_text(encoding="utf-8"))
CARDS = {card["id"]: card for card in CURRICULUM["cards"]}


def _presence_matches(actual: list[str], path: list[str]) -> bool:
    """Model C31's order-independent, complete-command presence check."""
    return set(path).issubset(set(actual))


class MethodPolicyTests(unittest.TestCase):
    def test_every_declared_rule_has_an_explicit_source_checked_path(self):
        ruled = {
            card["id"]
            for card in CURRICULUM["cards"]
            if card.get("method_requirement")
        }
        # New endcaps explicitly opt into complete atomic all_of commands.
        # They must not inherit a table policy through a grammar-family alias.
        atomic = {card["id"] for card in CURRICULUM["cards"]
                  if card.get("method_requirement", {}).get("all_of")}
        self.assertEqual(ruled, set(explicit_card_ids()) | atomic)
        for card_id in sorted(ruled):
            paths = taught_paths(CARDS[card_id], CARDS[card_id]["method_requirement"])
            self.assertTrue(paths, card_id)
            self.assertTrue(all(path for path in paths), card_id)
            self.assertTrue(all(all(isinstance(command, str) and command for command in path)
                                for path in paths), card_id)

    def test_focal_routes_are_minimal_and_do_not_use_family_aliases(self):
        self.assertEqual(
            taught_paths(CARDS["M0.01"], CARDS["M0.01"]["method_requirement"]),
            [["f*", "ro"]],
        )
        self.assertEqual(
            taught_paths(CARDS["M2.DWH"], CARDS["M2.DWH"]["method_requirement"]),
            [["dw"]],
        )
        self.assertEqual(
            taught_paths(CARDS["M2.DEH"], CARDS["M2.DEH"]["method_requirement"]),
            [["de"]],
        )
        self.assertEqual(
            taught_paths(CARDS["M11.GP"], CARDS["M11.GP"]["method_requirement"]),
            [["g+"]],
        )
        self.assertEqual(
            taught_paths(CARDS["M11.UT"], CARDS["M11.UT"]["method_requirement"]),
            [["g-", "g+"]],
        )
        self.assertEqual(
            taught_paths(CARDS["M0.L0"], CARDS["M0.L0"]["method_requirement"]),
            [["0"]],
        )
        self.assertNotEqual(
            taught_paths(CARDS["M2.DWH"], CARDS["M2.DWH"]["method_requirement"]),
            taught_paths(CARDS["M2.DEH"], CARDS["M2.DEH"]["method_requirement"]),
        )

    def test_reordered_and_exploratory_input_preserves_credit(self):
        path = taught_paths(CARDS["M0.01"], CARDS["M0.01"]["method_requirement"])[0]
        actual = ["gg", "f*", "j", "ro", "u", "fo"]
        self.assertTrue(_presence_matches(actual, path))

        path = taught_paths(CARDS["M11.UT"], CARDS["M11.UT"]["method_requirement"])[0]
        actual = ["g+", "j", "u", ":earlier 1<CR>", "gg", "g-"]
        self.assertTrue(_presence_matches(actual, path))

    def test_named_scopes_and_operator_counts_remain_atomic(self):
        self.assertIn("10G", taught_paths(CARDS["M17.04"], None)[0])
        self.assertNotIn("1G", taught_paths(CARDS["M17.04"], None)[0])
        self.assertEqual(taught_paths(CARDS["M19.06"], None), [["6dd"]])
        self.assertEqual(taught_paths(CARDS["M4.08"], None), [["3dd"]])
        self.assertEqual(taught_paths(CARDS["M2.D2WH"], None), [["d2W"]])
        self.assertEqual(taught_paths(CARDS["M16.INCH"], None), [["f0", "2<C-a>"]])

    def test_true_alternatives_and_multi_operation_lessons_are_not_flattened(self):
        whitespace = taught_paths(CARDS["M11.WS"], None)
        self.assertEqual(len(whitespace), 1)
        self.assertEqual(len(whitespace[0]), 4)
        self.assertEqual(len(taught_paths(CARDS["M11.LS"], None)), 3)
        self.assertEqual(
            taught_paths(CARDS["M11.LS"], None)[0],
            [":set list<CR>", "x"],
        )
        self.assertEqual(
            taught_paths(CARDS["M18.08"], None),
            [[":5,8t$<CR>", ":1,4t$<CR>"]],
        )

    def test_unknown_card_does_not_inherit_a_grammar_family_alias(self):
        unknown = {
            "id": "M2.NEW",
            "grammar_families": ["word-delete"],
            "title": "Retrieve dw on another card",
        }
        self.assertEqual(
            taught_paths(unknown, {"exact_any_of": ["ggfodw"]}),
            [],
        )

    def test_every_primary_variant_and_review_accepts_its_actual_commands(self):
        cfg = SimpleNamespace(tokenize=K.tokens)
        checked = 0
        for source in CURRICULUM["cards"]:
            if not source.get("method_requirement"):
                continue
            for bank, variants in (("primary", [{}]),
                                   ("variants", source.get("variants", [])),
                                   ("review_variants", source.get("review_variants", []))):
                for index, variant in enumerate(variants):
                    card = dict(source, **variant)
                    if bank == "review_variants":
                        card["id"] = "REVIEW"
                        card["review_source_card_id"] = source["id"]
                    keys = card["expected"]
                    self.assertIsNone(R._required_method_error(
                        cfg, card, {"actual_tokens": K.tokens(keys)}),
                        (source["id"], bank, index, keys, taught_paths(card, card["method_requirement"])))
                    checked += 1
        self.assertGreater(checked, 280)

    def test_positioning_is_not_a_second_method_requirement(self):
        cfg = SimpleNamespace(tokenize=K.tokens)
        for card_id, keys in (("M2.DWH", "1Gfodw"),
                              ("M3.CWH", ":1<CR>focwchanged<Esc>"),
                              ("M4.BI", "1G0<C-v>jjI!<Esc>"),
                              ("M14.02", "1Gyapp")):
            self.assertIsNone(R._required_method_error(
                cfg, CARDS[card_id], {"actual_tokens": K.tokens(keys)}), card_id)

    def test_visual_case_is_not_normal_history_evidence(self):
        cfg = SimpleNamespace(tokenize=K.tokens)
        self.assertIsNotNone(R._required_method_error(
            cfg, CARDS["M11.BR"], {"actual_tokens": K.tokens("2G0for!rO0vu")}))
        self.assertIsNotNone(R._required_method_error(
            cfg, CARDS["M11.ER"], {"actual_tokens": K.tokens("jf.r!ur'0v:earlier 1<CR>g+")}))

    def test_named_register_and_paste_are_actual_bound_commands(self):
        cfg = SimpleNamespace(tokenize=K.tokens)
        card = CARDS["M14.01"]
        self.assertIsNone(R._required_method_error(cfg, card, {
            "actual_tokens": K.tokens(card["expected"])}))
        # Choosing register a for an unrelated motion does not name the later
        # default-register yank. Literal replacement text is not Ctrl-r paste.
        for keys in ('f*"aly lfoR<C-r>a<Esc>', 'f*"aylfoR*<Esc>'):
            self.assertIsNotNone(R._required_method_error(cfg, card, {
                "actual_tokens": K.tokens(keys)}), keys)
        # An abandoned Replace entry cannot turn a later Insert paste into
        # a Replace-mode register paste, even though all literal keys occur.
        self.assertIsNotNone(R._required_method_error(cfg, card, {
            "actual_tokens": K.tokens('f*"aylR<Esc>i<C-r>a<Esc>uj0for*')}))

    def test_comparison_positioning_and_c31_mode_presence(self):
        cfg = SimpleNamespace(tokenize=K.tokens)
        self.assertEqual(R._method_family(cfg, CARDS["M18.05"], {
            "actual_tokens": K.tokens(":4<CR>$r1:8<CR>$r1")}),
            "manual verification markers")
        # C31 explicitly allows an actual taught mode entry even when a
        # later command writes the final target; no payload quota applies.
        self.assertTrue(R._mode_text_matches(K.tokens("gR<Esc>"), "gR", "> <"))


if __name__ == "__main__":
    unittest.main()
