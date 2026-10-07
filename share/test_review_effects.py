#!/usr/bin/env python3
"""Run every generated changed-art review bank in clean headless Neovim.

This is intentionally separate from the broad curriculum gate: it protects the
operation-specific source/target construction of the 148 two-variant review
banks (128 hidden-review banks plus 20 transfer/compare banks) against marker,
register, row-order, and frame-padding drift.
"""

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


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


generator = load_module("review_effect_generator", HERE / "gen_curriculum_v2.py")
runtime = load_module("review_effect_runtime", HERE / "v2_runtime.py")


def run_clean_effect(variant):
    """Apply one exact recipe in an isolated, plugin-free Neovim process."""
    with tempfile.TemporaryDirectory(prefix="vim-daily-review-effect-") as tmp:
        root = Path(tmp)
        artifact = root / "scratch.txt"
        key_script = root / "keys.bin"
        result_path = root / "result.json"
        artifact.write_text("\n".join(variant["start"]) + "\n", encoding="utf-8")
        result_lua = (
            "lua local p=%s; local r={lines=vim.api.nvim_buf_get_lines(0,0,-1,true),"
            "cursor=vim.api.nvim_win_get_cursor(0),wins=#vim.api.nvim_list_wins(),"
            "tabs=#vim.api.nvim_list_tabpages()}; vim.fn.writefile({vim.json.encode(r)},p)"
            % json.dumps(str(result_path))
        )
        key_script.write_bytes(
            b":set noautoindent nosmartindent nocindent indentexpr=\rgg^"
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
            return False, None, "nvim failed (%s): %s" % (completed.returncode, detail)
        result = json.loads(result_path.read_text(encoding="utf-8"))
        right = (
            result.get("lines") == variant["target"]
            and result.get("wins") == 1
            and result.get("tabs") == 1
        )
        return right, result, "The scratch art matches TARGET exactly."


class ReviewEffectTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("nvim"):
            raise unittest.SkipTest("Neovim is unavailable")
        with (HERE / "curriculum-v2.json").open(encoding="utf-8") as handle:
            cls.curriculum = json.load(handle)
        runtime.validate_curriculum(cls.curriculum)
        cls.cards = cls.curriculum["cards"]

    def test_generated_artifact_matches_source_and_has_148_review_banks(self):
        self.assertEqual(generator.build(), self.curriculum)
        review_cards = [card for card in self.cards if card.get("review_variants")]
        transfer_cards = [card for card in self.cards if card.get("variants")]
        self.assertEqual(len(review_cards), 128)
        self.assertEqual(len(transfer_cards), 20)
        self.assertEqual(len(review_cards) + len(transfer_cards), 148)
        self.assertTrue(all(len(card["review_variants"]) == 2 for card in review_cards))
        self.assertTrue(all(len(card["variants"]) == 2 for card in transfer_cards))

    def test_all_review_variants_match_their_operation_targets(self):
        entries = []
        for card in self.cards:
            for field in ("review_variants", "variants"):
                entries.extend(
                    (card["id"], field, index, variant)
                    for index, variant in enumerate(card.get(field, []), 1)
                )
        self.assertEqual(len(entries), 296)
        for card_id, field, index, variant in entries:
            ok, result, detail = run_clean_effect(variant)
            self.assertTrue(
                ok,
                (card_id, field, index, variant["expected"],
                 result.get("lines") if result else None, variant["target"], detail),
            )


if __name__ == "__main__":
    unittest.main()
