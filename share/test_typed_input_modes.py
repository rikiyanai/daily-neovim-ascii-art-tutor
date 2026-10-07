"""Focused mode-bound and receipt-fallback regression tests."""

import importlib.machinery
import importlib.util
import contextlib
import io
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import v2_runtime as R


HERE = Path(__file__).resolve().parent
loader = importlib.machinery.SourceFileLoader(
    "typed_modes_gate", str(HERE.parent / "bin" / "vim-daily-gate"))
spec = importlib.util.spec_from_loader(loader.name, loader)
G = importlib.util.module_from_spec(spec)
loader.exec_module(G)


CFG = SimpleNamespace(
    decode_keylog=staticmethod(G.decode_keylog),
    tokenize=staticmethod(G.tokenize),
    keystroke_table=None,
)


def receipt(*parts, schema="vim-daily/typed-input@1"):
    rows = []
    for text, mode in parts:
        for value in text.encode("utf-8"):
            rows.append({"typed_hex": bytes([value]).hex(), "mode": mode})
    return {"input_schema": schema, "input": rows}


def typed(*parts):
    return R._typed_input_tokens(CFG, receipt(*parts))


def commands(tokens):
    return set(R._method_commands(tokens))


def required(*keys):
    return {"id": "MODE.PROBE", "expected": " ".join(keys),
            "method_requirement": {"all_of": list(keys)}}


def test_state_changing_ex_cannot_promote_insert_text_to_ddp():
    # The Ex command creates the correct target, then the apparent ddp is
    # literal Insert text and is undone.  The real PTY receipt reports i for
    # every payload byte; those bytes must never become Normal commands.
    tokens = typed(
        (":", "n"), ("1m2\r", "c"),
        (":", "n"), ("startinsert\r", "c"),
        ("ddp\x1b", "i"), ("u", "n"),
    )
    assert commands(tokens).isdisjoint({("normal", "dd"), ("normal", "p")})
    assert R._required_method_error(
        CFG, {"id": "M6.DDPH", "expected": "ggddp",
              "method_requirement": {"all_of": ["dd", "p"]}},
        {"actual_tokens": tokens})


def test_genuine_normal_operator_modes_and_replay_are_preserved():
    genuine = typed(("ggd", "n"), ("d", "no"), ("p", "n"))
    assert commands(genuine).issuperset({("normal", "gg"), ("normal", "dd"),
                                         ("normal", "p")})
    assert R._required_method_error(CFG, required("dd", "p"),
                                    {"actual_tokens": genuine}) is None

    # A real extra Normal d is n after the completed dd, so it is not the
    # duplicated no-mode callback that the WhichKey repair removes.
    ddd = typed(("d", "n"), ("d", "no"), ("d", "n"))
    assert list(ddd) == ["d", "d", "d"]
    assert ("normal", "dd") in commands(ddd)
    assert R._required_method_error(CFG, required("dd"),
                                    {"actual_tokens": ddd}) is None

    replay = typed(("d", "n"), ("d", "no"), ("d", "no"), ("p", "n"))
    assert list(replay) == ["d", "d", "p"]


def test_insert_visual_register_ex_search_digraph_replace_and_cancel_are_scoped():
    assert not commands(typed(('"addp', "i")))
    assert not {("normal", "dd"), ("normal", "p")} & commands(
        typed((":", "n"), ("ddp\r", "c")))
    assert not {("normal", "dd"), ("normal", "p")} & commands(
        typed(("/", "n"), ("ddp\r", "c")))

    visual = commands(typed(("v", "n"), ("j", "v"), ("d", "v")))
    assert ("normal", "Visual d") in visual
    assert ("normal", "dd") not in visual

    assert ("normal", '"add') in commands(
        typed(('"a', "n"), ("d", "n"), ("d", "no")))
    assert ("normal", "r<C-k>.M") in commands(
        typed(("r\x0b.M", "n")))
    assert ("normal", "R") in commands(
        typed(("R", "n"), ("abc", "R"), ("\x1b", "R")))
    assert ("normal", "dd") not in commands(
        typed(("d", "n"), ("\x1b", "no"), ("p", "n")))


def test_untyped_mode_transitions_are_not_normal_and_virtual_replace_stays_distinct():
    # No typed colon: command mode still cannot provide Normal dd/p evidence.
    for mode in ("c", "t", "r", "unknown"):
        assert commands(typed(("ddp", mode))).isdisjoint({("normal", "dd"), ("normal", "p")})
    assert ("virtual_replace", "<C-r>a") in commands(
        typed(("gR", "n"), ("\x12a", "Rv")))
    assert ("replace", "<C-r>a") not in commands(
        typed(("gR", "n"), ("\x12a", "Rv")))
    # A pending inferred r must not consume text after an actual Insert transition.
    assert ("normal", "rO") not in commands(typed(("r", "n"), ("O", "i")))
    # Actual on_key receipts report R for a Normal r literal. Prompt-mode r
    # is also accepted only when a witnessed Normal r already owns it.
    assert ("normal", "rO") in commands(typed(("r", "n"), ("O", "r")))
    assert ("normal", "r1") in commands(typed(("r", "n"), ("1", "R")))
    assert ("normal", "r<C-k>.M") in commands(
        typed(("r", "n"), ("\x0b.M", "R")))
    assert not commands(typed(("1ddp", "R")))


def test_fresh_neovim_receipt_fails_closed_but_legacy_fallback_survives():
    card = dict(required("dd"), target=["x"])
    with tempfile.TemporaryDirectory(prefix="vim-daily-typed-contract-") as directory:
        root = Path(directory)
        art, keylog, receipt_path = root / "art.txt", root / "keys.log", root / "keys.cursor.json"
        art.write_text("x\n", encoding="utf-8")
        keylog.write_bytes(b"dd")
        base = {
            "schema": "vim-daily/cursor-receipt@1", "attempt": "nonce",
            "event": "VimLeavePre", "artifact": str(art),
            "buffer_path": str(art), "cursor": {"row": 1, "column": 1},
            "display_column": 1,
        }
        malformed = dict(base, input_schema="wrong", input=[{"typed_hex": "64", "mode": "i"}])
        receipt_path.write_text(json.dumps(malformed), encoding="utf-8")
        fresh = R._read_cursor_receipt(receipt_path, "nonce", art)
        assert fresh is not None
        nvim_cfg = SimpleNamespace(editor="nvim", decode_keylog=G.decode_keylog,
                                   tokenize=G.tokenize, keystroke_table=None)
        replay = R._attempt_replay(nvim_cfg, card, keylog, ["x"], ["x"], fresh,
                                    require_typed_input=True)
        assert replay["input_source"] == "typed-input-receipt-invalid"
        assert replay["actual_tokens"] == []
        assert R._required_method_error(nvim_cfg, card, replay)

        missing = R._attempt_replay(nvim_cfg, card, keylog, ["x"], ["x"], None,
                                    require_typed_input=True)
        assert missing["input_source"] == "typed-input-missing"
        assert missing["actual_tokens"] == []

        strict_old = R._attempt_replay(nvim_cfg, card, keylog, ["x"], ["x"], base,
                                       require_typed_input=True)
        assert strict_old["input_source"] == "typed-input-missing"
        assert strict_old["actual_tokens"] == []

        legacy_cfg = SimpleNamespace(editor="vim", decode_keylog=G.decode_keylog,
                                     tokenize=G.tokenize, keystroke_table=None)
        legacy = R._attempt_replay(legacy_cfg, card, keylog, ["x"], ["x"], None)
        assert legacy["input_source"] == "scriptout-legacy"
        assert legacy["actual_tokens"] == ["d", "d"]

        old_receipt = R._attempt_replay(nvim_cfg, card, keylog, ["x"], ["x"], base)
        assert old_receipt["input_source"] == "scriptout-legacy"
        assert old_receipt["actual_tokens"] == ["d", "d"]


def test_visual_prefix_and_register_scope_survives_actual_modes():
    for key in ("g+", "g-", "gR", "gu", "gU"):
        actual = typed(("V", "n"), (key, "V"), ("\x1b", "V"))
        assert ("normal", key) not in commands(actual)
    genuine = typed(("ggV", "n"), ('5j"ay', "V"), ('G"ap', "n"))
    assert commands(genuine).issuperset({("normal", '"aVisual y'), ("normal", '"ap')})
    assert R._method_path_matches(genuine, G.tokenize('ggV5j"ayG"ap'), {})
    block = typed(("\x16", "n"), ("2j9|zy", "\x16"), ("4G2|zp", "n"))
    assert ("normal", "Visual zy") in commands(block)
    assert ("normal", "zp") in commands(block)
    rule = {"id": "M15.ZP", "expected": "gg0<C-v>2j9|zy4G2|zp",
            "method_requirement": {"all_of": ["<C-v>", "zy", "zp"]}}
    assert R._required_method_error(CFG, rule, {"actual_tokens": block}) is None
    wrong = typed(("\x16\x1bzyzp", "n"))
    assert R._required_method_error(CFG, rule, {"actual_tokens": wrong})


def test_cursor_receipt_shape_and_exact_positive_integer_coordinates():
    with tempfile.TemporaryDirectory(prefix="vim-daily-cursor-types-") as directory:
        root = Path(directory)
        art, output = root / "art.txt", root / "receipt.json"
        base = {"schema": "vim-daily/cursor-receipt@1", "attempt": "nonce",
                "event": "VimLeavePre", "artifact": str(art), "buffer_path": str(art),
                "cursor": {"row": 1, "column": 1}, "display_column": 1}
        output.write_text(json.dumps(base), encoding="utf-8")
        assert R._read_cursor_receipt(output, "nonce", art) is not None
        for value in ([], None, True, "receipt"):
            output.write_text(json.dumps(value), encoding="utf-8")
            assert R._read_cursor_receipt(output, "nonce", art) is None
        for field in ("row", "column", "display_column"):
            for value in (True, False, 0, -1, 1.0, "1"):
                changed = dict(base, cursor=dict(base["cursor"]))
                if field == "display_column":
                    changed[field] = value
                else:
                    changed["cursor"][field] = value
                output.write_text(json.dumps(changed), encoding="utf-8")
                assert R._read_cursor_receipt(output, "nonce", art) is None


def test_recovery_keeps_owned_modes_and_refuses_unbound_legacy_evidence():
    card = dict(required("dd", "p"), target=["target"])
    before = ["source"]
    with tempfile.TemporaryDirectory(prefix="vim-daily-recovery-modes-") as directory:
        root = Path(directory)
        art, keylog = root / "art.txt", root / "keys.log"
        contract_path = keylog.with_suffix(".contract.json")
        output = keylog.with_suffix(".cursor.json")
        base = dict(receipt(("ddp", "i")), schema="vim-daily/cursor-receipt@1",
                    attempt="nonce", event="VimLeavePre", artifact=str(art),
                    buffer_path=str(art), cursor={"row": 1, "column": 1}, display_column=1)
        output.write_text(json.dumps(base), encoding="utf-8")
        keylog.write_bytes(b"ddp")
        assert R._recovery_input_receipt(keylog, art, card, before) is None
        contract = {"schema": "vim-daily/attempt-contract@1", "cursor_attempt": "nonce",
                    "card": card, "before": before}
        contract_path.write_text(json.dumps(contract), encoding="utf-8")
        recovered = R._recovery_input_receipt(keylog, art, card, before)
        assert recovered is not None
        replay = R._attempt_replay(CFG, card, keylog, before, ["target"], recovered,
                                   require_typed_input=True)
        assert R._required_method_error(CFG, card, replay)
        assert R._recovery_input_receipt(keylog, art, dict(card, id="other"), before) is None
        assert R._recovery_input_receipt(keylog, art, card, ["other"]) is None
        contract["cursor_attempt"] = "stale"
        contract_path.write_text(json.dumps(contract), encoding="utf-8")
        assert R._recovery_input_receipt(keylog, art, card, before) is None


def test_production_cold_recovery_uses_owned_modes_not_scriptout():
    cur = json.loads((HERE / "curriculum-v2.json").read_text())
    card = next(c for c in cur["cards"] if c["id"] == "M6.DDPH")
    # Integration fixture supplies a completed artifact, not a real learner
    # attempt. The actual gate callback identity selects the production
    # recovery policy; no editor, questions or successful events are injected.
    for mode, bound, wanted_pass in (("n", True, True), ("i", True, False), ("n", False, False)):
        with tempfile.TemporaryDirectory(prefix="vim-daily-cold-recovery-") as directory:
            cfg = R.RuntimeConfig(state=directory, share=str(HERE), editor="nvim",
                target=12, cooldown=0, max_tries=1, stamp=str(Path(directory) / "stamp"),
                run_editor=G.run_editor, decode_keylog=G.decode_keylog, tokenize=G.tokenize,
                hold_open=lambda: None, colours=("",) * 6)
            assert R._typed_input_required(cfg)
            art = R._artifact_path(cfg, card)
            art.parent.mkdir(parents=True, exist_ok=True)
            R._write_lines_atomic(art, card["target"])
            R._checkpoint(cfg, card, art, "before")
            R._write_lines_atomic(art.parent / "checkpoints" / (card["id"] + "-before.txt"), card["start"])
            keylog = R._next_attempt_keylog(art.parent, "keys-" + card["id"])
            keylog.write_bytes(b"ggddp")
            payload = dict(receipt(("ggddp", mode)), schema="vim-daily/cursor-receipt@1",
                attempt="nonce", event="VimLeavePre", artifact=str(art), buffer_path=str(art),
                cursor={"row": 1, "column": 1}, display_column=1)
            keylog.with_suffix(".cursor.json").write_text(json.dumps(payload), encoding="utf-8")
            if bound:
                keylog.with_suffix(".contract.json").write_text(json.dumps({
                    "schema": "vim-daily/attempt-contract@1", "cursor_attempt": "nonce",
                    "card": card, "before": card["start"]}), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), \
                    patch.object(R, "run_paired_questions", return_value=(True, None)), \
                    patch.object(R, "watch_your_work"), patch.object(R, "_post_lesson"), \
                    patch.object(R, "_celebrate_progress"):
                result = R.run_edit(cfg, cur, R.project(cur, []), card)
            events = [e for e in R.read_events(cfg) if e.get("type") == "card"]
            assert bool([e for e in events if e["result"] == "pass"]) == wanted_pass
            assert result == (0 if wanted_pass else 1)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
