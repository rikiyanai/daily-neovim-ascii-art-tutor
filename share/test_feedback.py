"""VD-35: `f` sends learner feedback from question and result screens."""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import v2_runtime as v2  # noqa: E402

cur = json.loads((HERE / "curriculum-v2.json").read_text(encoding="utf-8"))
question = next(q for q in cur["questions"] if q.get("form") == "multiple_choice")
card = next(c for c in cur["cards"] if c["id"] == question["card_id"])

with tempfile.TemporaryDirectory() as tmp:
    v2.FEEDBACK["path"] = v2.feedback_path(tmp)
    v2.FEEDBACK["context"].clear()
    v2.note_feedback_context(revision=cur["revision"], card_id=card["id"],
                             card_title=card["title"], screen="lesson")
    letter = "abcd"[question["correct_choice"]]
    answers = iter(["f", "the second choice is unclear", "f", "", letter])
    right, chosen = v2.ask_question(question, input_fn=lambda _prompt: next(answers),
                                    shuffle=False)
    # Feedback never counts as an answer; the real answer still grades.
    assert right is True and chosen == question["correct_choice"]
    rows = [json.loads(line) for line in
            v2.feedback_path(tmp).read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1, rows  # the empty message was cancelled
    row = rows[0]
    assert row["message"] == "the second choice is unclear"
    assert row["screen"] == "question"
    assert row["card_id"] == card["id"] and row["question_id"] == question["id"]
    assert row["revision"] == cur["revision"] and row["at"]

    # A result page records the answer context captured after grading.
    v2.collect_feedback(lambda _prompt: "result page note", screen="lesson-end")
    rows = [json.loads(line) for line in
            v2.feedback_path(tmp).read_text(encoding="utf-8").splitlines()]
    assert rows[-1]["screen"] == "lesson-end" and rows[-1]["answer_correct"] is True

print("PASS feedback: question and result screens record context; empty message cancels")
