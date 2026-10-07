#!/usr/bin/env python3
"""Focused regression proofs for completion, receipts, and learner-facing diagnostics."""

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import v2_runtime as R


HERE = Path(__file__).resolve().parent
CUR = json.loads((HERE / "curriculum-v2.json").read_text(encoding="utf-8"))
loader = importlib.machinery.SourceFileLoader("grading_gate", str(HERE.parent / "bin" / "vim-daily-gate"))
spec = importlib.util.spec_from_loader(loader.name, loader)
G = importlib.util.module_from_spec(spec)
loader.exec_module(G)


def cfg_for(root, *, question_answer=None, run_editor=None):
    cfg = R.RuntimeConfig(
        state=str(root), share=str(HERE), editor="nvim", max_tries=1, target=12,
        cooldown=0, stamp=str(Path(root) / "stamp"), run_editor=run_editor,
        decode_keylog=lambda _data: [], hold_open=lambda: None,
        colours=("", "", "", "", "", ""), tokenize=G.tokenize,
        question_answer=question_answer,
    )
    return cfg


def receipt(path, token, *, row, column):
    return {
        "schema": "vim-daily/cursor-receipt@1", "attempt": token,
        "artifact": str(Path(path).resolve()), "buffer_path": str(Path(path).resolve()),
        "buffer_id": 7, "window_id": 9, "cursor": {"row": row, "column": column},
        "display_column": column, "event": "VimLeavePre",
    }


nav_cfg = SimpleNamespace(tokenize=G.tokenize)
nav_cards = {card["id"]: card for card in CUR["cards"]}
for cid in ("M0.L0", "M0.F0"):
    card = nav_cards[cid]
    # Exact keys in a real Normal-mode path pass independently of save/exit.
    assert R._required_method_error(
        nav_cfg, card, {"actual_tokens": G.tokenize(card["expected"] + ":wq<CR>")}) is None
    # R1: command-line argument text and inserted text do not count as Normal-mode keys.
    for fake in (
        ":write !true %s<CR>:q!<CR>" % card["expected"],
        "i%s<Esc>:q!<CR>" % card["expected"],
    ):
        assert R._required_method_error(
            nav_cfg, card, {"actual_tokens": G.tokenize(fake)}), (cid, fake)
    assert R._edit_tokens_without_submit(
        G.tokenize(":write !true %s<CR>:q!<CR>" % card["expected"])) != []
    assert R._cursor_goal_error(card, {"target_matches": True})
    wrong = {"cursor_receipt": receipt("/tmp/art", "x", row=1, column=1)}
    assert R._cursor_goal_error(card, wrong)
    goal = card["cursor_goal"]
    good = {"cursor_receipt": receipt("/tmp/art", "x", row=goal["row"], column=goal["column"])}
    assert R._cursor_goal_error(card, good) is None

# The first-edit and window recipes remain accepted, including their distinct
# semantic modes and Ex command path; only the navigation cards require a cursor receipt.
for cid, recipe in (("M0.01", "j0f*ro"), ("M0.01", "jf*ro"),
                    ("M4.WIN", ":vsplit<CR><C-w>p:q<CR>")):
    card = nav_cards[cid]
    assert R._required_method_error(nav_cfg, card, {"actual_tokens": G.tokenize(recipe)}) is None

# A correct result can use a different positioning path and extra corrections.
# Operator and Visual motions remain method scope, not incidental navigation.
for cid, recipe in (("M0.L0", "jjk0"), ("M0.F0", ":2<CR>0f*"),
                    ("M11.GP", "/o<CR>r!ur-g-g-g+g+"),
                    ("M11.GM", "for!ur-g-g-g-")):
    assert R._required_method_error(nav_cfg, nav_cards[cid],
                                    {"actual_tokens": G.tokenize(recipe)}) is None, cid
for cid, recipe in (("M11.GP", "ig+<Esc>"), ("M11.GM", ":echo 'g-'<CR>")):
    assert R._required_method_error(nav_cfg, nav_cards[cid],
                                    {"actual_tokens": G.tokenize(recipe)}), cid
for cid, recipe in (("M11.GP", "gg+"), ("M11.GM", "gg-"),
                    ("M0.F0", "j0fXr*")):
    assert R._required_method_error(nav_cfg, nav_cards[cid],
                                    {"actual_tokens": G.tokenize(recipe)}), (cid, recipe)
position_probe = {"method_requirement": {"exact_any_of": ["j0dw"]}}
assert R._required_method_error(nav_cfg, position_probe,
    {"actual_tokens": G.tokenize(":2<CR>^dw")}) is None
assert R._required_method_error(nav_cfg, position_probe,
    {"actual_tokens": G.tokenize("j0de")})
scope_probe = {"method_requirement": {"exact_any_of": ["dj"]}}
assert R._required_method_error(nav_cfg, scope_probe,
    {"actual_tokens": G.tokenize("dk")})
assert R._method_operation_tokens(G.tokenize("Vjjd")) != R._method_operation_tokens(G.tokenize("Vjd"))
count_probe = {"method_requirement": {"exact_any_of": ["10G"]}}
assert R._required_method_error(nav_cfg, count_probe, {"actual_tokens": G.tokenize("1G")})
assert R._required_method_error(nav_cfg, count_probe, {"actual_tokens": G.tokenize("10G")}) is None
comparison_probe = {"method_alternatives": [{"label": "word deletion", "keys": "j0dw"}]}
assert R._method_family(nav_cfg, comparison_probe,
                        {"actual_tokens": G.tokenize(":2<CR>^dw")}) == "word deletion"

# C31 treats a recipe as a set of atomic operations, not a timeline or quota.
unordered_probe = {"method_requirement": {"exact_any_of": ["dwurO"]}}
for keys in ("rOudw", "udwrO", "rOrOudw", "rO:echo 'explore'<CR>udw"):
    assert R._required_method_error(nav_cfg, unordered_probe,
                                    {"actual_tokens": G.tokenize(keys)}) is None, keys
for keys in ("irOudw<Esc>", ":echo 'rOudw'<CR>", "d<Esc>wrOu"):
    assert R._required_method_error(nav_cfg, unordered_probe,
                                    {"actual_tokens": G.tokenize(keys)}), keys
for required, actual in (("dd", "dwdb"), ("g+", "gg+"),
                         ("f*", "fXr*"), ("10G", "1G0")):
    probe = {"method_requirement": {"all_of": [required]}}
    assert R._required_method_error(nav_cfg, probe,
                                    {"actual_tokens": G.tokenize(actual)}), (required, actual)
quota_probe = {"method_requirement": {"all_of": ["rO"], "max_tokens": 2}}
assert R._required_method_error(nav_cfg, quota_probe,
    {"actual_tokens": G.tokenize("jjk0rOu<C-r>:wq<CR>")}) is None
assert R._mode_text_matches(G.tokenize("Rchanged<Esc>"), "R", "example")
assert not R._mode_text_matches(G.tokenize("iRexample<Esc>"), "R", "example")
for keys in ("vvrO", "VdrO", "<C-v>r-rO"):
    assert ("normal", "rO") in R._method_commands(G.tokenize(keys)), keys
assert ("normal", "g+") not in R._method_commands(G.tokenize("Vcg+<Esc>"))
assert ("normal", "u") not in R._method_commands(G.tokenize("vu"))
assert ("ex", "earlier 1") not in R._method_commands(G.tokenize("v:earlier 1<CR>"))
assert ("ex", "earlier 1") in R._method_commands(G.tokenize("v<Esc>:earlier 1<CR>"))
assert ("normal", '"ayl') in R._method_commands(G.tokenize('"ayl'))
assert ("normal", '"ayl') not in R._method_commands(G.tokenize('"aly l'))
assert ("normal", '"0p') in R._method_commands(G.tokenize('"0p'))
assert ("normal", '"0p') not in R._method_commands(G.tokenize('"0lp'))
assert ("normal", "r<C-k>.M") in R._method_commands(G.tokenize("r<C-k>.M"))
assert ("normal", "r<C-k>.M") not in R._method_commands(G.tokenize("r<C-k>!I.M"))
assert ("replace", "<C-r>a") in R._method_commands(G.tokenize("R<C-r>a<Esc>"))
assert ("insert", "<C-r>a") not in R._method_commands(G.tokenize("R<C-r>a<Esc>"))
assert ("insert", "<C-r>a") not in R._method_commands(G.tokenize("Rliteral a<Esc>"))


def fake_editor(path, _line, _cursor, keylog, *_rest):
    Path(keylog).write_bytes(b"captured")
    # Deliberately no receipt: an unchanged target must not self-credit.


nav = nav_cards["M0.L0"]
with tempfile.TemporaryDirectory(prefix="vim-daily-grading-negative-") as tmp:
    cfg = cfg_for(tmp, run_editor=fake_editor,
                  question_answer=lambda q: "abcd"[q["correct_choice"]])
    with patch.object(R, "watch_your_work"), patch.object(R, "_post_lesson"), \
            patch.object(R, "_celebrate_progress"):
        assert R.run_edit(cfg, CUR, R.project(CUR, []), nav) == 1
    assert any(event.get("result") == "fail" for event in R.read_events(cfg))


# Positive unchanged-art completion binds the receipt to the same attempt and buffer.
def receipt_editor(path, _line, _cursor, keylog, *_rest):
    Path(keylog).write_bytes(b"captured")
    receipt_path = Path(os.environ["VIM_DAILY_CURSOR_RECEIPT"])
    receipt_path.write_text(json.dumps(receipt(
        path, os.environ["VIM_DAILY_CURSOR_ATTEMPT"], row=2, column=1)), encoding="utf-8")


with tempfile.TemporaryDirectory(prefix="vim-daily-grading-positive-") as tmp:
    cfg = cfg_for(tmp, run_editor=receipt_editor,
                  question_answer=lambda q: "abcd"[q["correct_choice"]])
    cfg.decode_keylog = lambda _data: G.tokenize(nav["expected"])
    with patch.object(R, "watch_your_work"), patch.object(R, "_post_lesson"), \
            patch.object(R, "_celebrate_progress"):
        assert R.run_edit(cfg, CUR, R.project(CUR, []), nav) == 0
    passed = [event for event in R.read_events(cfg) if event.get("result") == "pass"]
    assert passed and passed[-1]["cursor_receipt"]["event"] == "VimLeavePre"


# Width diagnostics report terminal display columns while retaining the source
# character index for a learner inspecting a wide-glyph row.
wide = R._artifact_replay({"target": ["　⌒ヽ"], "got": ["　⌒ノ"]}, False)
assert "first difference at column 4 (character 3)" in "\n".join(wide)

# Question art is a display copy: line breaks survive, borders are aligned, and
# the authored prompt remains byte-for-byte unchanged.
raw_prompt = "ANIMATION\n\n  │ short│ → │ x│\n  │ longer│ → │ y│\n\nNEOVIM"
before = raw_prompt
rendered_prompt = R._compact_question_text(raw_prompt)
assert "\n  │ short " in rendered_prompt and "\n  │ longer" in rendered_prompt
assert raw_prompt == before

# A method miss remains conspicuous even when the saved artifact is exact, and
# the shared keystroke table keeps correct captures green and wrong captures red.
with patch("sys.stdout.isatty", return_value=True), patch.dict(
        os.environ, {"TERM": "xterm-256color"}, clear=True):
    partial = R._partial_key_colours("Try `:2s/o/x/g`.", "Try `:2s/o/x/`.")
    assert R._ui_style().ansi("ok", enabled=True) in partial
    assert R._ui_style().ansi("fail", enabled=True) in partial
method_replay = {
    "type": "edit", "target_matches": True,
    "method_evidence_error": "wrong method", "actual_tokens": G.tokenize("j0f*"),
    "actual_keys": "j0f*", "taught_keys": "j0f*ro",
    "table": G.keystroke_table(G.tokenize("j0f*"), G.tokenize("j0f*ro")),
    "before": nav["start"], "got": nav["target"], "target": nav["target"],
}
with tempfile.TemporaryDirectory(prefix="vim-daily-grading-render-") as tmp:
    cfg = cfg_for(tmp)
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        R._post_feedback(cfg, CUR, nav, method_replay, completed=False)
    text = output.getvalue()
    assert "RESULT ✓ · METHOD ✗" in text and "KEYSTROKE LEDGER" in text
    assert "THE RECIPE ASKS FOR" in text
    assert "TARGET CORRECT" in text and "instant retry: r" in text
with patch("sys.stdout.isatty", return_value=True), patch.dict(
        os.environ, {"TERM": "xterm-256color"}, clear=True):
    probe = {"expected": "dwurO", "method_requirement": {"all_of": ["dw", "u", "rO"]}}
    ledger = "\n".join(R._result_key_ledger(probe, {
        "target_matches": True, "actual_tokens": G.tokenize("rOu")
    }))
    assert R._paint("rO", "ok") in ledger and R._paint("u", "ok") in ledger
    assert R._paint("dw", "fail") in ledger
    assert "not this" not in ledger and "you skipped" not in ledger

# Generic authored toolbox reminders are scoped to the actual recipe instead
# of leaking an unrelated search/landmark command into a different lesson.
scoped = R._scoped_hint({
    "expected": "j0", "hint": "Vim toolbox. /pattern<CR> searches. f* finds. Use 0 here."
})
assert "/pattern<CR>" not in scoped and "f*" not in scoped and "Use 0 here" in scoped

# Whitespace-preserving playback is carried through project, watch, and gallery
# reads without relying on viewer.lesson_view's legacy rstrip path.
nav_view = R._lesson_view_preserving_whitespace(nav, nav["target"])
assert nav_view.kind == "navigation" and len(nav_view.frames) == 2
assert "not animation" in nav_view.title
assert nav_view.frames[0][::2] == nav["start"] == nav_view.frames[1][::2]
still_card = {"id": "STILL", "start": ["left", "right"],
              "artifact_mode": "still-study", "frame_slices": [1, 1]}
still_view = R._lesson_view_preserving_whitespace(still_card, still_card["start"])
assert still_view.kind == "still" and len(still_view.frames) == 1
edit_view = R._lesson_view_preserving_whitespace(still_card, ["leaf", "right"])
assert edit_view.kind == "edit" and edit_view.labels == ["before", "yours"]
with tempfile.TemporaryDirectory(prefix="vim-daily-grading-whitespace-") as tmp:
    tmp = Path(tmp)
    card = {
        "id": "M10.TEST", "module_id": "M10", "project_id": "jis-test",
        "title": "JIS", "frame_slices": [1, 1],
        "start": ["ヽ_ノ\u3000 "], "preserve_trailing_whitespace": True,
    }
    module = {"id": "M10", "title": "JIS", "project_id": "jis-test"}
    cur = {"cards": [card], "modules": [module]}
    project = tmp / "projects" / "jis-test"
    (project / "checkpoints").mkdir(parents=True)
    rows = ["ヽ_ノ\u3000 ", "ヽ_ノ\u3000 "]
    (project / "strip.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (project / "manifest.json").write_text(json.dumps({
        "module_id": "M10", "current_card": "M10.TEST",
    }), encoding="utf-8")
    after = project / "checkpoints" / "M10.TEST-after.txt"
    before_path = project / "checkpoints" / "M10.TEST-before.txt"
    after.write_text("ヽ_ノ\u3000 \nヽ_ノ\u3000 \n", encoding="utf-8")
    before_path.write_text("ヽ_ノ\u3000\n", encoding="utf-8")
    cfg = cfg_for(tmp)
    progress = {"passed_cards": ["M10.TEST"]}
    view = R.project_view(cfg, cur, "M10")
    assert view.frames[0][0].endswith("\u3000 ")
    with patch.dict(os.environ, {"VIM_DAILY_VIEWER": "1"}), patch.object(R._viewer_module(), "play"):
        R.watch_your_work(cfg, cur, card, project / "strip.txt")
    with patch.dict(os.environ, {"VIM_DAILY_VIEWER": "off"}), patch.object(R._viewer_module(), "play") as playback:
        R.LAST_VIEW["views"] = None
        R.watch_your_work(cfg, cur, card, project / "strip.txt")
        playback.assert_not_called()
        assert R.LAST_VIEW["views"]
        R.replay_last_view()
        playback.assert_called_once()
    gallery = R.completed_gallery(cfg, cur, progress)
    assert gallery and gallery[0]["view"].frames[0][0].endswith("\u3000 ")

print("PASS grading completion: receipts, semantic negative controls, scoped diagnostics, question rows, whitespace playback")
