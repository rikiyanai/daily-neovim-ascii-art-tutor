#!/usr/bin/env python3
"""Focused stdlib integration proofs for shared UI and reward decisions."""
import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import v2_runtime as R

HERE = Path(__file__).resolve().parent
cur = json.loads((HERE / "curriculum-v2.json").read_text())
card = next(c for c in cur["cards"] if c["id"] == "M0.01")
V = R._viewer_module()
assert R._notation_bytes("f<r!ur-g-g+:earlier 1<CR>") == b"f<r!ur-g-g+:earlier 1\r"
assert R._notation_bytes("gR> <<Esc>") == b"gR> <\x1b"
batch = [{"title": "reward %d" % i, "art": ["*"], "credit": "credit %d" % i}
         for i in range(25)]
pages = [V.celebration_lines(batch, V.Style(False), tick=tick, max_rows=19)
         for tick in range(4)]
assert all(len(page) <= 19 for page in pages)
assert all("credit %d" % i in "\n".join("\n".join(page) for page in pages)
           for i in range(25)), "compact reward batches must not drop credits"

assert "…" not in R._clip("a long paragraph " * 15, 25)
assert all(len(line) <= 25 for line in R._clip("a long paragraph " * 15, 25).splitlines())
with patch.dict(os.environ, {"NO_COLOR": "1", "TERM": "xterm"}):
    assert R._paint("✓ +10", "ok") == "✓ +10"
with patch("sys.stdout.isatty", return_value=True), patch.dict(
        os.environ, {"TERM": "xterm-256color"}, clear=True):
    actual = R._partial_key_colours("Try `:2s/o/x/g`.", "Try `:2s/o/x/`.")
    assert R._ui_style().ansi("fail") in actual
    assert R._ui_style().ansi("ok") in actual
    assert R._ui_style().ansi("flags") in R._concept_shape()

probe = {"expected": "rx", "method_requirement": {"label": "replace", "any_of": ["rx"]},
         "method_alternatives": [{"label": "change", "keys": "clx<Esc>", "why": "same cell"}]}
cfg_keys = SimpleNamespace(tokenize=lambda text: R._keys_module().tokenize(text))
# The production tokenizer is supplied by the gate; this fixture needs only
# ASCII tokens, and keeps the escape notation atomic.
cfg_keys.tokenize = lambda text: text.replace("<Esc>", "§").split() if " " in text else list(text.replace("<Esc>", "§"))
alternate = {"actual_tokens": list("clx§"), "actual_keys": "clx<Esc>", "method_family": "change"}
assert R._required_method_error(cfg_keys, probe, alternate) is None
assert R._required_method_error(cfg_keys, probe, {"actual_tokens": list("ix§")})
assert R._method_family(cfg_keys, probe, {"actual_tokens": []}) is None

# Authored reminders reach the real brief, but cannot describe a different
# drawing selected for a changed-art review.
first = next(c for c in cur["cards"] if c["id"] == "M0.01")
assert R._brief_key_reminders(first) == first["key_vocabulary"]
dracula_review = R._changed_review_card(cur, {"module_id": "M0", "stage": 1}, "M0.01")
assert dracula_review["expected"] != first["expected"]
assert "key_shape" not in dracula_review and "key_vocabulary" not in dracula_review
assert "jf*ro also works" not in " ".join(R._brief_key_reminders(dracula_review))
R.LAST_FEEDBACK_CONTEXT = None
R.LAST_FEEDBACK_DETAILS = ["complete sentence %d" % n for n in range(35)]
details_output = io.StringIO()
with contextlib.redirect_stdout(details_output), patch("shutil.get_terminal_size", return_value=os.terminal_size((80, 24))):
    R.show_feedback_details(lambda _: "")
assert all("complete sentence %d" % n in details_output.getvalue() for n in range(35))
assert "2/2" in details_output.getvalue()
R.LAST_FEEDBACK_DETAILS = ["\n".join("wrapped sentence %d" % n for n in range(35))]
details_output = io.StringIO()
with contextlib.redirect_stdout(details_output), patch("shutil.get_terminal_size", return_value=os.terminal_size((80, 24))):
    R.show_feedback_details(lambda _: "")
assert all("wrapped sentence %d" % n in details_output.getvalue() for n in range(35))
assert "2/2" in details_output.getvalue(), "pagination must count wrapped rows, not entries"

with tempfile.TemporaryDirectory(prefix="vim-daily-runtime-ui-") as tmp:
    cfg = R.RuntimeConfig(tmp, str(HERE), "nvim", 1, 12, 0, str(Path(tmp) / "stamp"),
                         None, None, lambda: None, ("", "", "", "", "", ""))
    progress = R.project(cur, [])
    brief = R._write_session_lesson(cfg, cur, progress, card).read_text()
    assert brief.startswith("PROGRESS")
    assert brief.index("DO THIS") < brief.index("TARGET") < brief.index("RECIPE")
    assert "── MORE" in brief and "SHAPE" in brief
    hidden = dict(card, show_recipe=False, show_target=False)
    assert R._recipe_shape(hidden) is None
    tree = io.StringIO()
    with contextlib.redirect_stdout(tree):
        R.print_tree(cur, progress, cfg)
    assert all(b["name"] in tree.getvalue() for b in R._dashboard_theme().BADGES)
    # Alternate paths get credit without letting the unpractised taught
    # operation disappear from spaced practice.
    cfg.tokenize = cfg_keys.tokenize
    tiny = dict(cur, deck={"schema": "vim-daily/deck@1", "families": [{
        "id": "R", "family": "r", "parser_families": ["r{char}"],
        "items": [{"id": "R.01"}], "card_ids": [],
    }]})
    probe["id"], probe["module_id"] = "M0.01", "M0"
    R._defer_taught_method(cfg, tiny, probe, progress, alternate)
    marked = [e for e in R.read_events(cfg) if e.get("type") == "deck"]
    assert marked and marked[-1]["source"] == "alternate-method" and marked[-1]["grade"] == "again"
    events_before = len(R.read_events(cfg))
    R._defer_taught_method(cfg, tiny, probe, progress, {"actual_tokens": list("rx"), "method_family": "replace"})
    assert len(R.read_events(cfg)) == events_before

    module = next(m for m in cur["modules"] if m["id"] == "M0")
    old = Path(tmp) / "projects" / "old-fireworks-name"
    old.mkdir(parents=True)
    (old / "manifest.json").write_text(json.dumps({"module_id": "M0", "current_card": card["id"]}))
    (old / "strip.txt").write_text("\n".join(card["target"]) + "\n")
    assert R._project_directory(cfg, module) == old
    with contextlib.redirect_stdout(io.StringIO()):
        assert R.preview_project(cfg, cur, "M0", speed=0) == 0

    seen = []
    before = dict(progress, xp=0)
    after = dict(progress, xp=1000)
    with patch.object(R._viewer_module(), "celebrate", side_effect=lambda rewards, **kw: seen.append((rewards, kw))):
        R._celebrate_progress(cfg, cur, before, after, set())
    assert seen and seen[0][1] == {"duration": 2.0}
    assert all(r["kind"] in ("badge", "level") and r["credit"] for r in seen[0][0])
    cfg.practice = True
    with patch.object(R._viewer_module(), "celebrate", side_effect=AssertionError("practice reward")):
        R._celebrate_progress(cfg, cur, before, after, set())

loader = importlib.machinery.SourceFileLoader("ui_test_gate", str(HERE.parent / "bin" / "vim-daily-gate"))
spec = importlib.util.spec_from_loader(loader.name, loader)
gate = importlib.util.module_from_spec(spec)
loader.exec_module(gate)
lua = ("vim.api.nvim_buf_set_lines(0,0,-1,false,{'PROGRESS','DO THIS','── MORE','WHY'});"
       "vim.wo.foldmethod='manual';vim.cmd('2,3fold');"
       "vim.g.vim_daily_brief_win=vim.api.nvim_get_current_win();" + gate.BRIEF_HIGHLIGHT_LUA +
       ";assert(vim.fn.foldclosed(3)==3);assert(vim.fn.foldclosed(2)==-1);")
run = subprocess.run(["nvim", "--headless", "--clean", "+lua " + lua, "+qa!"],
                     capture_output=True, text=True)
assert run.returncode == 0 and "Error" not in run.stderr, run.stderr

# Both a fresh edit and a recovered exact artifact use the same declared-path
# credit policy. Editor/keystroke capture are fixtures here, not headed proof.
for recovered in (False, True):
    with tempfile.TemporaryDirectory(prefix="vim-daily-method-tier-") as tmp:
        trial = dict(card, start=["o"], target=["x"], expected="rx",
                     recipe=[["rx", "replace one cell"]], paired_question_ids=[],
                     method_requirement={"label": "replace", "any_of": ["rx"]},
                     method_alternatives=[{"label": "replace", "keys": "rx", "why": "taught path"},
                                          {"label": "change", "keys": "clx<Esc>",
                                           "why": "same one-cell result"}])
        cfg = R.RuntimeConfig(tmp, str(HERE), "nvim", 1, 12, 0,
                              str(Path(tmp) / "stamp"), None, None,
                              lambda: None, ("", "", "", "", "", ""))
        cfg.tokenize = gate.tokenize
        cfg.decode_keylog = lambda _data: gate.tokenize("clx<Esc>")
        def finish(path, _line, _cursor, keylog, *_rest):
            Path(path).write_text("x\n")
            Path(keylog).write_bytes(b"captured alternate fixture")
        cfg.run_editor = finish
        if recovered:
            path = Path(tmp) / "projects" / trial["project_id"] / "strip.txt"
            path.parent.mkdir(parents=True)
            path.write_text("x\n")
            (path.parent / ("keys-%s-attempt-0001.log" % trial["id"])).write_bytes(b"recovered fixture")
        with contextlib.redirect_stdout(io.StringIO()), patch.object(R, "watch_your_work"), patch.object(R, "_celebrate_progress"):
            assert R.run_edit(cfg, cur, R.project(cur, []), trial) == 0
        events = R.read_events(cfg)
        passed = next(e for e in events if e.get("type") == "card" and e.get("result") == "pass")
        assert passed["method_tier"] == "declared" and passed["method_family"] == "change"
        assert bool(passed.get("recovered")) == recovered
        assert any(e.get("source") == "alternate-method" and e.get("grade") == "again"
                   for e in events)
# An unchanged-art workflow still needs a real fresh editor invocation.
with tempfile.TemporaryDirectory(prefix="vim-daily-window-workflow-") as tmp:
    trial = dict(card, start=["o"], target=["o"], expected=":vsplit<CR>:q<CR>",
                 recipe=[[":vsplit<CR>:q<CR>", "inspect and close a second view"]],
                 paired_question_ids=[],
                 method_requirement={"label": "window workflow", "exact_any_of": [":vsplit<CR>:q<CR>"]})
    cfg = R.RuntimeConfig(tmp, str(HERE), "nvim", 1, 12, 0,
                          str(Path(tmp) / "stamp"), None, None,
                          lambda: None, ("", "", "", "", "", ""))
    cfg.tokenize = gate.tokenize
    cfg.decode_keylog = lambda _data: gate.tokenize(trial["expected"])
    editor_calls = []
    def unchanged_workflow(path, _line, _cursor, keylog, *_rest):
        editor_calls.append(path)
        Path(keylog).write_bytes(b"captured window workflow fixture")
    cfg.run_editor = unchanged_workflow
    with contextlib.redirect_stdout(io.StringIO()), patch.object(R, "watch_your_work"), patch.object(R, "_celebrate_progress"):
        assert R.run_edit(cfg, cur, R.project(cur, []), trial) == 0
    assert len(editor_calls) == 1
    assert any(e.get("result") == "pass" and not e.get("recovered") for e in R.read_events(cfg))
# Actual completion sinks automatically open the reward viewer.  Neither
# path requires a viewer command or dashboard interaction.  Deck quizzes
# grant neither XP nor these achievements, so they do not invent rewards.
with tempfile.TemporaryDirectory(prefix="vim-daily-auto-rewards-") as tmp:
    cfg = R.RuntimeConfig(tmp, str(HERE), "nvim", 1, 12, 0,
                          str(Path(tmp) / "stamp"), None, None,
                          lambda: None, ("", "", "", "", "", ""))
    seen = []
    with contextlib.redirect_stdout(io.StringIO()), \
            patch.object(R, "_post_lesson"), \
            patch.object(V, "celebrate", side_effect=lambda rewards, **kw: seen.append((rewards, kw))):
        assert R._complete(cfg, cur, card) == 0
    assert len(seen) == 1 and seen[0][1] == {"duration": 2.0}
    assert any(r["title"] == "First step" for r in seen[0][0]), seen
    # Existing achievements are not replayed on another pass.
    with contextlib.redirect_stdout(io.StringIO()), \
            patch.object(R, "_post_lesson"), patch.object(V, "celebrate") as celebrate:
        assert R._complete(cfg, cur, card) == 0
    celebrate.assert_not_called()

for prior_reviews, completed in ((3, True), (4, True), (3, False)):
    with tempfile.TemporaryDirectory(prefix="vim-daily-review-rewards-") as tmp:
        cfg = R.RuntimeConfig(tmp, str(HERE), "nvim", 1, 12, 0,
                              str(Path(tmp) / "stamp"), None, None,
                              lambda: None, ("", "", "", "", "", ""))
        seed = [c for c in cur["cards"] if c["kind"] != "module_check"][:7]
        for source in seed:
            R.append_event(cfg, {"type": "card", "result": "pass",
                                 "card_id": source["id"], "module_id": source["module_id"]})
        # Independent thresholds: 79 -> 82 XP levels up; a fifth distinct
        # successful review earns Review keeper.  Prior events are fixtures.
        sources = [c for c in cur["cards"]
                   if c["id"] != card["id"] and R._review_variants(c)][:prior_reviews]
        for source in sources:
            R.append_event(cfg, {"type": "review", "result": "pass",
                                 "review_key": source["id"], "module_id": source["module_id"],
                                 "review_stage": 1})
        before = R.project(cur, R.read_events(cfg))
        assert before["xp"] == 70 + 3 * prior_reviews
        artifact = Path(tmp) / "review.txt"
        artifact.write_text("saved review fixture\n")
        seen = []
        with contextlib.redirect_stdout(io.StringIO()), \
                patch.object(R, "ask_question", return_value=(completed, 0)), \
                patch.object(R, "_run_review_edit", return_value=(True, card, artifact, {})), \
                patch.object(R, "_post_lesson"), \
                patch.object(V, "celebrate", side_effect=lambda rewards, **kw: seen.append((rewards, kw))):
            status = R.run_review(cfg, cur, before, card["id"], {"module_id": "M0", "stage": 0})
        assert status == (0 if completed else 1)
        if completed:
            assert len(seen) == 1 and seen[0][1] == {"duration": 2.0}
            if prior_reviews == 3:
                assert any(r["kind"] == "level" and r["title"].startswith("Level 2")
                           for r in seen[0][0]), seen
            else:
                assert any(r["title"] == "Review keeper" for r in seen[0][0]), seen
        else:
            assert not seen

print("PASS runtime UI: wrapping, partial credit, method alternatives, fresh unchanged-art workflow, folds, shared badges, renamed projects, automatic viewer-only lesson/review rewards")
