#!/usr/bin/env python3
"""Negative mode/receipt controls for the actual course runtime."""
import contextlib
import importlib.machinery
import importlib.util
import io
import json
import tempfile
import unittest
import urllib.request
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import sjis_authoring as N
import sjis_tutor as S
import v2_runtime as R

HERE = Path(__file__).resolve().parent
loader = importlib.machinery.SourceFileLoader("adversarial_gate", str(HERE.parent / "bin/vim-daily-gate"))
spec = importlib.util.spec_from_loader(loader.name, loader)
G = importlib.util.module_from_spec(spec)
loader.exec_module(G)


class MethodProof(unittest.TestCase):
    def test_saved_feedback_box_rows_keep_both_borders_registered(self):
        cur = json.loads((HERE / "curriculum-v2.json").read_text())
        questions = {q["id"]: q for q in cur["questions"]}
        for qid in ("M11.TR.P01", "M11.LS.P01", "M11.GM.P01", "M11.ER.P01", "M11.06.P01"):
            prompt = questions[qid]["prompt"]
            rows = [line.split("│") for line in R._align_question_art(prompt).splitlines() if line.count("│") >= 4]
            self.assertGreater(len(rows), 1, qid)
            for border in (1, 2, 3):
                self.assertEqual(len({R._cell_width("│".join(parts[:border])) for parts in rows}), 1, (qid, border))
        # This is the compensating-gap shape that the old renderer offsets.
        raw = "  │a│     │x│\n  │abc│   │y│"
        aligned = R._align_question_art(raw).splitlines()
        self.assertEqual(aligned[0].rfind("│"), aligned[1].rfind("│"))

    def test_ex_case_and_pattern_spaces_are_not_discarded(self):
        self.assertFalse(R._method_path_matches(G.tokenize(":normal J<CR>"), G.tokenize(":normal j<CR>"), {}))
        self.assertFalse(R._method_path_matches(G.tokenize(":s//x/<CR>"), G.tokenize(":s/ /x/<CR>"), {}))

    def test_literal_motion_arguments_do_not_enter_insert(self):
        actual = R._semantic_tokens(G.tokenize("rOj0"))
        self.assertIn(("argument", "O"), actual)
        self.assertIn(("normal", "j"), actual)
        self.assertFalse(R._method_path_matches(G.tokenize("rj0"), G.tokenize("j0"), {"navigation_only": True}))
        self.assertFalse(R._method_path_matches(G.tokenize('"j0'), G.tokenize("j0"), {"navigation_only": True}))

    def test_change_payload_does_not_prove_navigation(self):
        for payload in ("clj0<Esc>", "ci(j0<Esc>", "cf)j0<Esc>"):
            self.assertFalse(R._method_path_matches(G.tokenize(payload), G.tokenize("j0"), {"navigation_only": True}), payload)

    def test_alternative_yank_and_copy_cannot_hide_in_payload(self):
        method = {"evidence": {"kind": "linewise_yank_put", "rows": 3}}
        copy = {"evidence": {"kind": "ex_copy", "start": 1, "end": 3, "destination": "3"}}
        self.assertFalse(R._method_evidence_matches(method, G.tokenize(":echo '3yyp'<CR>"), []))
        self.assertFalse(R._method_evidence_matches(copy, G.tokenize("i:1,3t3<CR><Esc>"), []))
        self.assertTrue(R._method_evidence_matches(method, G.tokenize("3yyp"), []))
        self.assertTrue(R._method_evidence_matches(copy, G.tokenize(":1,3t3<CR>"), []))

    def test_attempt_nonce_changes_for_same_path_and_number(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-nonce-") as directory:
            p = Path(directory)
            with R._CursorReceiptEnv(p / "art.txt", p / "keys.log", 1) as one:
                first = one.token
            with R._CursorReceiptEnv(p / "art.txt", p / "keys.log", 1) as two:
                self.assertNotEqual(first, two.token)


class NativeRuntime(unittest.TestCase):
    def test_m10_requires_current_display_not_only_transcription(self):
        cur = json.loads((HERE / "curriculum-v2.json").read_text())
        card = next(c for c in cur["cards"] if c["id"] == "M10.01")
        for acknowledged, suffix, wanted in ((False, "", False), (True, "", True), (True, "　 ", False)):
            with self.subTest(acknowledged=acknowledged, suffix=suffix), tempfile.TemporaryDirectory(prefix="vim-daily-native-runtime-") as directory:
                class ProtocolFixture(S.TutorPreview):
                    def __init__(self, *args, **kwargs):
                        super().__init__(*args, open_browser=False, **kwargs)

                    def final_receipt(self):
                        self.refresh()
                        if acknowledged:
                            # Protocol fixture, not a claim of operator inspection.
                            body = json.dumps(N._preview_identity(self.payload)).encode()
                            req = urllib.request.Request(self.url.replace("/?", "/api/seen?"), data=body, headers={"Content-Type": "application/json"})
                            with urllib.request.urlopen(req) as response:
                                self.assert_status = response.status
                        return super().final_receipt(display_timeout=0)

                def edit(path, _line, _cursor, keylog, *_rest):
                    Path(path).write_text(S.art_text([row + suffix for row in card["target"]]), encoding="utf-8")
                    Path(keylog).write_bytes(b"fixture")

                cfg = R.RuntimeConfig(state=directory, share=str(HERE), editor="nvim", max_tries=1,
                    target=12, cooldown=0, stamp=str(Path(directory) / "stamp"), run_editor=edit,
                    decode_keylog=lambda _: G.tokenize(card["expected"]), hold_open=lambda: None,
                    colours=("",) * 6, tokenize=G.tokenize, native_preview_factory=ProtocolFixture)
                with contextlib.redirect_stdout(io.StringIO()), patch.object(R, "run_paired_questions", return_value=(True, None)), \
                        patch.object(R, "watch_your_work"), patch.object(R, "_post_lesson"), patch.object(R, "_celebrate_progress"):
                    R.run_edit(cfg, cur, R.project(cur, []), card)
                passes = [e for e in R.read_events(cfg) if e.get("type") == "card" and e.get("result") == "pass"]
                events = [e for e in R.read_events(cfg) if e.get("type") == "card"]
                self.assertEqual(bool(passes), wanted, events)
                if passes:
                    self.assertTrue(passes[0]["native_preview"]["ready"])
                    self.assertTrue(passes[0]["native_preview"]["display"])
                elif suffix:
                    failures = [e for e in R.read_events(cfg) if e.get("native_preview")]
                    self.assertTrue(failures)
                    self.assertIn("gate", failures[-1]["native_preview"], failures[-1])
                    gate = failures[-1]["native_preview"]["gate"]
                    self.assertFalse(gate["transcription_ready"])
                    # Adding blank tails changes transcription but not ink.
                    # Native pixel equality alone must not award this card.
                    self.assertTrue(gate["visual_equal"])


if __name__ == "__main__":
    unittest.main()
