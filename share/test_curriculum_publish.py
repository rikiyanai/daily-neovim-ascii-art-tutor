"""Read-only live-session exclusion and attempt-identity regression controls."""

import fcntl
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from curriculum_publish import publish
import v2_runtime as runtime


class PublicationTests(unittest.TestCase):
    def test_non_tty_deck_writes_lock_before_curriculum_load(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-deck-launch-") as directory:
            root = Path(directory)
            cfg = SimpleNamespace(state=str(root / "state"), hold_open=lambda: None)
            target = root / "curriculum.json"
            target.write_text("unchanged")
            for argv in (["--deck-miss", "DK.G.01"], ["--quiz", "1"]):
                def session(*args, **kwargs):
                    self.assertIsNotNone(kwargs.get("session_lock"))
                    with self.assertRaisesRegex(RuntimeError, "lesson is active"):
                        publish(target, "replacement", lock_path=runtime._paths(cfg)["lock"])
                    return 0
                with patch.object(runtime, "_run_session", side_effect=session), patch(
                    "sys.stdin.isatty", return_value=False), patch(
                    "sys.stdout.isatty", return_value=False):
                    self.assertEqual(runtime.run(cfg, argv), 0)
                self.assertEqual(target.read_text(), "unchanged")

    def test_missing_configured_lock_refuses_even_with_standard_lock(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-publish-") as directory:
            root = Path(directory)
            target, configured, standard = (root / "curriculum.json",
                                            root / "missing.lock", root / "standard.lock")
            target.write_text("old")
            standard.write_text("existing operator token")
            with patch("curriculum_publish.operator_session_locks",
                       return_value=[configured, standard]):
                with self.assertRaisesRegex(RuntimeError, "No operator session lock"):
                    publish(target, "new")
            self.assertEqual(target.read_text(), "old")
            self.assertFalse(configured.exists())
            self.assertEqual(standard.read_text(), "existing operator token")

    def test_interactive_launch_locks_load_and_catch_up_before_edit(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-launch-lock-") as directory:
            root = Path(directory)
            target = root / "curriculum.json"
            target.write_text("unchanged contract")
            cfg = runtime.RuntimeConfig(
                state=str(root / "state"), share=str(Path(__file__).parent),
                editor="nvim", max_tries=1, target=0, cooldown=0,
                stamp=str(root / "stamp"), run_editor=lambda *args: None,
                decode_keylog=lambda *args: [], hold_open=lambda: None,
                colours=("",) * 6, tokenize=lambda *args: [])
            lock = runtime._paths(cfg)["lock"]
            original_load = runtime.load_curriculum
            observed = []

            def refusal(phase):
                with self.assertRaisesRegex(RuntimeError, "lesson is active"):
                    publish(target, "mid-launch replacement", lock_path=lock)
                self.assertEqual(target.read_text(), "unchanged contract")
                observed.append(phase)

            def load(share):
                refusal("curriculum load")
                return original_load(share)

            with patch.object(runtime, "load_curriculum", side_effect=load), patch.object(
                runtime, "_show_retroactive_module_rewards",
                side_effect=lambda *args: refusal("catch-up playback")), patch(
                "sys.stdin.isatty", return_value=True), patch(
                "sys.stdout.isatty", return_value=True), patch.dict(
                "os.environ", {"VIM_DAILY_SKIP": "", "VIM_DAILY_ACTIVE": "", "NVIM": ""}):
                self.assertEqual(runtime.run(cfg, ["run"]), 0)
            self.assertEqual(observed, ["curriculum load", "catch-up playback"])
            publish(target, "between launches", lock_path=lock)
            self.assertEqual(target.read_text(), "between launches")

    def test_source_history_study_preserves_rejected_operator_files(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-source-history-") as directory:
            root = Path(directory)
            cfg = SimpleNamespace(state=str(root), practice=False)
            project = root / "projects" / "source-project"
            project.mkdir(parents=True)
            old_strip = project / "strip.txt"
            old_strip.write_text("(_!,o)\n")
            old_checkpoint = project / "checkpoints" / "M11.UT-before.txt"
            old_checkpoint.parent.mkdir()
            old_checkpoint.write_text("old rejected take\n")
            card = {"id": "M11.UT", "project_id": "source-project", "start": ["source"],
                    "target": ["source look"], "expected": "rO",
                    "history_source_provenance": {"character": "skully"}}
            path = runtime._artifact_path(cfg, card)
            self.assertNotEqual(path, old_strip)
            runtime._write_new(path, card["start"])
            runtime._checkpoint(cfg, card, path, "before")
            self.assertEqual(old_strip.read_text(), "(_!,o)\n")
            self.assertEqual(old_checkpoint.read_text(), "old rejected take\n")
            self.assertEqual(runtime._artifact_path(cfg, card), path)
            card["target"] = ["different corrected source"]
            self.assertNotEqual(runtime._artifact_path(cfg, card), path)

    def test_nested_source_history_checkpoint_remains_in_gallery(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-source-gallery-") as directory:
            root = Path(directory)
            cfg = SimpleNamespace(state=str(root), practice=False)
            card = {"id": "M11.UT", "module_id": "M11", "project_id": "source-project",
                    "title": "Source history", "kind": "compare_methods",
                    "start": ["  ___", "(_o,o)", " `---"],
                    "target": ["  ___", "(_O,o)", " `---"], "expected": "rO",
                    "history_source_provenance": {"character": "skully"}}
            path = runtime._artifact_path(cfg, card)
            runtime._write_new(path, card["target"])
            runtime._checkpoint(cfg, card, path, "after")
            gallery = runtime.completed_gallery(cfg, {"cards": [card], "modules": []},
                                                {"passed_cards": [card["id"]]})
            self.assertEqual([entry["card_id"] for entry in gallery], [card["id"]])
            self.assertEqual(gallery[0]["view"].frames[-1], card["target"])

    def test_isolated_xdg_cannot_ignore_active_standard_operator(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-publish-") as directory:
            root = Path(directory)
            target, configured, operator = (root / "curriculum.json",
                                           root / "isolated.lock", root / "operator.lock")
            target.write_text("old")
            configured.write_text("isolated")
            operator.write_text("operator")
            with operator.open("rb") as owner:
                fcntl.flock(owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
                with patch("curriculum_publish.operator_session_locks", return_value=[configured, operator]):
                    with self.assertRaisesRegex(RuntimeError, "lesson is active"):
                        publish(target, "new")
                self.assertEqual(target.read_text(), "old")
                self.assertEqual(operator.read_text(), "operator")

    def test_active_session_refuses_without_mutating_json_or_lock(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-publish-") as directory:
            root = Path(directory)
            target, lock = root / "curriculum.json", root / "session.lock"
            target.write_text("old contract\n")
            lock.write_text("learner lock token")
            with lock.open("rb") as owner:
                fcntl.flock(owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
                with self.assertRaisesRegex(RuntimeError, "lesson is active"):
                    publish(target, "new contract\n", lock_path=lock)
                self.assertEqual(target.read_text(), "old contract\n")
                self.assertEqual(lock.read_text(), "learner lock token")
            publish(target, "new contract\n", lock_path=lock)
            self.assertEqual(target.read_text(), "new contract\n")
            self.assertEqual(lock.read_text(), "learner lock token")
            self.assertEqual(list(root.glob(".curriculum-publish-*")), [])

    def test_missing_lock_refuses_without_creating_learner_state(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-publish-") as directory:
            root = Path(directory)
            target = root / "curriculum.json"
            target.write_text("old")
            with self.assertRaisesRegex(RuntimeError, "No operator session lock"):
                publish(target, "new", lock_path=root / "missing.lock")
            self.assertEqual(target.read_text(), "old")
            self.assertFalse((root / "missing.lock").exists())

    def test_failed_attempt_records_pinned_contract(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-revision-") as directory:
            root = Path(directory)
            cfg = SimpleNamespace(state=str(root), stamp=str(root / "stamp"), practice=False)
            original = {"revision": "old", "cards": [{"id": "M11.UT", "target": ["source"]}]}
            runtime._bind_curriculum(cfg, original)
            expected = hashlib.sha256(json.dumps(original, sort_keys=True,
                ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
            # A later live-file replacement cannot change the loaded contract.
            row = runtime.append_event(cfg, {"type": "card", "result": "fail", "card_id": "M11.UT"})
            self.assertEqual(row["curriculum_revision"], "old")
            self.assertEqual(row["curriculum_contract_sha256"], expected)
            self.assertEqual(json.loads((root / "events-v2.jsonl").read_text()), row)

    def test_attempt_retains_exact_task_beside_keylog(self):
        with tempfile.TemporaryDirectory(prefix="vim-daily-contract-") as directory:
            root = Path(directory)
            keylog, artifact = root / "keys-attempt-1.log", root / "strip.txt"
            keylog.write_bytes(b":q!\r")
            card = {"id": "M11.UT", "target": ["source pose"],
                    "prompt": "source task", "cursor": "^"}
            cfg = SimpleNamespace(run_editor=lambda *args: None,
                                  curriculum_revision="pinned",
                                  curriculum_contract_sha256="a" * 64)
            runtime._run_native_editor(cfg, card, artifact, keylog, root / "lesson.txt", ["before"])
            card["target"] = ["later changed target"]
            fields = runtime._keylog_fields(keylog)
            saved = json.loads(Path(fields["attempt_contract"]).read_text())
            self.assertEqual(saved["card"]["target"], ["source pose"])
            self.assertEqual(saved["curriculum_revision"], "pinned")
            self.assertEqual(saved["before"], ["before"])
            self.assertEqual(len(fields["attempt_contract_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
