#!/usr/bin/env python3
"""Proof for the 26 manually authored, operation-specific review banks."""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


authored = _load("authored_review_variants", HERE / "authored_review_variants.py")
runtime = _load("authored_review_runtime", HERE / "v2_runtime.py")


def _art_difference(left, right):
    """Count changed glyph positions, including row-width changes."""
    total = 0
    for index in range(max(len(left), len(right))):
        before = left[index] if index < len(left) else ""
        after = right[index] if index < len(right) else ""
        total += sum(a != b for a, b in zip(before, after))
        total += abs(len(before) - len(after))
    return total


def _run_clean_effect(variant):
    """Run exactly the authored recipe in clean, isolated Neovim."""
    with tempfile.TemporaryDirectory(prefix="vim-daily-authored-review-") as tmp:
        root = Path(tmp)
        artifact = root / "scratch.txt"
        key_script = root / "keys.bin"
        result_path = root / "result.json"
        artifact.write_text("\n".join(variant["start"]) + "\n", encoding="utf-8")
        result_lua = (
            "lua local r={lines=vim.api.nvim_buf_get_lines(0,0,-1,true),"
            "cursor=vim.api.nvim_win_get_cursor(0),display_column=vim.fn.virtcol('.'),"
            "wins=#vim.api.nvim_list_wins(),tabs=#vim.api.nvim_list_tabpages(),"
            "scrollbind=vim.o.scrollbind};"
            "vim.fn.writefile({vim.json.encode(r)},%s)"
            % json.dumps(str(result_path))
        )
        key_script.write_bytes(
            b":set noautoindent nosmartindent nocindent indentexpr=\r"
            + runtime._notation_bytes(variant.get("prelude", ""))
            + runtime._notation_bytes("gg^")
            + runtime._notation_bytes(variant["expected"])
            + b"\x1b:"
            + result_lua.encode("utf-8")
            + b"\r:qa!\r"
        )
        isolated_xdg = root / "xdg"
        isolated_xdg.mkdir()
        environment = dict(os.environ)
        environment.update({
            "XDG_CONFIG_HOME": str(isolated_xdg / "config"),
            "XDG_DATA_HOME": str(isolated_xdg / "data"),
            "XDG_STATE_HOME": str(isolated_xdg / "state"),
            "XDG_CACHE_HOME": str(isolated_xdg / "cache"),
        })
        completed = subprocess.run(
            [shutil.which("nvim"), "--headless", "-u", "NONE", "-i", "NONE",
             "-n", "-s", str(key_script), str(artifact)],
            env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=10, check=False,
        )
        if completed.returncode != 0 or not result_path.exists():
            detail = completed.stderr.decode("utf-8", "replace")[-500:]
            return None, "nvim failed (%s): %s" % (completed.returncode, detail)
        return json.loads(result_path.read_text(encoding="utf-8")), ""


class AuthoredReviewVariantTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("nvim"):
            raise unittest.SkipTest("Neovim is unavailable")
        with (HERE / "curriculum-v2.json").open(encoding="utf-8") as handle:
            curriculum = json.load(handle)
        cls.cards = {card["id"]: card for card in curriculum["cards"]}
        cls.variants = authored.REVIEW_VARIANTS

    def test_exact_card_coverage_and_substantive_pairing(self):
        expected = {
            "M11.AT", "M11.COL", "M11.INS", "M2.DW", "M2.DE", "M2.D2W", "M2.TEN",
            "M15.APP", "M15.APPA", "M15.MACR", "M3.CW", "M3.CA", "M3.Y0", "M3.MARK",
            "M3.VD", "M4.SIL", "M4.TRIM", "M4.SCB", "M4.BD", "M13.BEB", "M7.TC",
            "M7.GTC", "M6.J", "M6.DDP", "M8.O", "M8.PAD",
        }
        self.assertEqual(set(self.variants), expected)
        self.assertEqual(sum(len(rows) for rows in self.variants.values()), 52)
        no_text_mutation = {"M11.COL", "M2.TEN", "M4.SIL", "M4.SCB"}
        for card_id, rows in self.variants.items():
            self.assertIn(card_id, self.cards)
            self.assertEqual(len(rows), 2, card_id)
            card = self.cards[card_id]
            self.assertTrue(all(row["expected"] == card["expected"] for row in rows), card_id)
            self.assertGreaterEqual(
                _art_difference(rows[0]["start"], rows[1]["start"]), 4, card_id)
            self.assertGreaterEqual(
                _art_difference(rows[0]["target"], rows[1]["target"]), 4, card_id)
            for row in rows:
                for field in ("start", "target", "expected", "recipe", "cursor", "source_ref"):
                    self.assertTrue(row.get(field), (card_id, field))
                self.assertIn("ascii-art-authoring", row["source_ref"])
                if card_id not in no_text_mutation:
                    self.assertNotEqual(row["start"], row["target"], card_id)

    def test_all_52_recipes_match_exact_targets(self):
        for card_id, rows in self.variants.items():
            for index, variant in enumerate(rows, 1):
                result, detail = _run_clean_effect(variant)
                self.assertIsNotNone(result, (card_id, index, detail))
                self.assertEqual(result["lines"], variant["target"],
                                 (card_id, index, result["lines"], variant["target"]))
                self.assertEqual(result["wins"], 1, (card_id, index))
                self.assertEqual(result["tabs"], 1, (card_id, index))
                if "cursor_after" in variant:
                    self.assertEqual(result["cursor"], variant["cursor_after"],
                                     (card_id, index, result["cursor"]))
                if card_id == "M11.COL":
                    self.assertEqual(result["display_column"], 12)
                if card_id == "M11.INS":
                    self.assertEqual(len(result["lines"][1]), 12)
                    self.assertEqual(result["lines"][1][:len(variant["start"][1])], variant["start"][1])
                if "option_after" in variant:
                    self.assertTrue(result["scrollbind"], (card_id, index))


if __name__ == "__main__":
    unittest.main()
