"""Textual screen fixtures at all required terminal sizes."""
import asyncio
import os
from pathlib import Path
import sys

try:
    import textual
except ImportError:
    managed = Path.home() / ".local/share/vim-daily-venv/bin/python"
    if managed.is_file() and str(managed) != sys.executable:
        os.execv(str(managed), [str(managed), __file__])
    raise

import lesson_tui as L
from textual.widgets import Static


async def main():
    # Literal brackets, full-width/trailing spaces and long prose are not
    # interpreted as markup, collapsed, clipped or wrapped as artwork.
    art = "  │　[O]　 │"
    prose = "An operation-specific explanation. " * 16
    for size in ((80, 24), (100, 36), (188, 49)):
        mounted = []
        app = L.make_app([("Lesson", prose + "\n" + art)], mounted=lambda: mounted.append(True))
        async with app.run_test(size=size) as pilot:
            await pilot.pause()
            widgets = list(app.query(".art"))
            assert len(widgets) == 1
            assert widgets[0].content.plain == art, (size, widgets[0].content)
            assert all("…" not in str(widget.content)
                       for widget in app.query(Static)), size
            assert mounted
            await pilot.press("enter")
            assert app.return_value == "edit"
        app = L.make_app([("Result", "RESULT ✓ · METHOD ✗\n" + art), ("Progress", prose)], result=True)
        async with app.run_test(size=size) as pilot:
            await pilot.press("r")
            assert app.return_value == "repeat"
    nav = {
        "id": "M0.L0", "navigation_only": True,
        "start": ["  abc", "  def"], "expected": "j0",
        "cursor_goal": {"row": 2, "column": 1},
    }
    study = L.navigation_study(nav)
    assert "NAVIGATION STUDY" in study and "not animation" in study
    assert "  abc" in study and "  def" in study
    assert "The caret is a UI overlay" in study
    assert L.lesson_pages("  │raw  ", card=nav)[1][0] == "Navigation study"
    assert L.result_pages("RESULT ✓", "PROGRESS +10") == [
        ("Feedback", "RESULT ✓"), ("Progress", "PROGRESS +10")]
    motion_card = {
        "id": "M11.GP",
        "source_motion": {
            "frames": [
                ["  │　/\\  ", "尾  "],
                ["  │　\\/  ", "尾　 "],
                ["  │　—  ", "尾  "],
            ],
            "credit": "Original source: lesson-author/reference-01",
            "interval": 0.2,
        },
    }
    motion_pages = L.lesson_pages("  │raw  ", card=motion_card)
    assert motion_pages[-1][0] == "Source motion"
    spec = motion_pages[-1][1]
    assert isinstance(spec, L.SourceMotionSpec)
    assert spec.frame_count == 3 and spec.interval == 0.2
    assert spec.credit == motion_card["source_motion"]["credit"]
    assert spec.frames[0][0] == "  │　/\\  "
    assert L.source_motion_spec({"source_motion": {"frames": [["same"], ["same"]]}}) is None
    reward = L.result_reward_spec(motion_card)
    assert isinstance(reward, L.ResultRewardSpec)
    assert reward is not spec
    assert reward.frame_count == spec.frame_count
    assert reward.interval == spec.interval
    assert reward.frames == spec.frames
    assert "LESSON REWARD" in reward.title
    reward_pages = L.result_pages("RESULT ✓", "PROGRESS +10", reward=reward)
    assert reward_pages[:2] == [("Feedback", "RESULT ✓"), ("Progress", "PROGRESS +10")]
    assert reward_pages.reward is reward
    module_card = dict(motion_card, module_reward={
        "frames": [["|" + "." * n + "o" + "." * (7 - n) + "|"] for n in range(8)],
        "title": "UI protocol fixture, not authored course content",
        "credit": "Original UI test fixture",
        "interval": 0.2,
    })
    module_pages = L.lesson_pages("Module study", card=module_card)
    assert module_pages[-1][0] == "Module animation"
    assert isinstance(module_pages[-1][1], L.ModuleAnimationSpec)
    assert L.source_motion_spec(module_card).frame_count == 3
    assert L.result_reward_spec(module_card).frame_count == 8
    assert "MODULE REWARD" in L.result_reward_spec(module_card).title
    assert L.result_reward_spec(dict(module_card, medium="proportional-sjis")) is None
    assert L.result_pages("R", "P", reward=motion_card).reward.frames == spec.frames
    for size in ((80, 24), (100, 36), (188, 49)):
        app = L.make_app(module_pages)
        async with app.run_test(size=size) as pilot:
            await pilot.press("a")
            await pilot.pause()
            assert app.query_one("TabbedContent").active == "page-2"
            panel = app.query_one("#module-animation-panel")
            await pilot.press("space")
            assert panel.paused
            frozen = panel.frame_index
            await pilot.press("l")
            assert panel.frame_index == (frozen + 1) % 8
            row = panel.query_one("#motion-row-0", Static).content.plain
            assert row == module_pages[-1][1].frames[panel.frame_index][0]
            await pilot.press("m")
            assert app.query_one("TabbedContent").active == "page-1"
    # The authored frame timer, pause control, and manual h/l steps are real
    # mounted behavior at each supported terminal size.  The row assertion
    # also proves full-width/trailing whitespace survives Textual rendering.
    for size in ((80, 24), (100, 36), (188, 49)):
        app = L.make_app(motion_pages)
        async with app.run_test(size=size) as pilot:
            await pilot.press("m")
            await pilot.pause()
            assert app.query_one("TabbedContent").active == "page-1"
            panel = app.query_one("#source-motion-panel")
            initial = panel.frame_index
            # Observe an actual tick instead of sampling after a whole loop.
            for _ in range(8):
                await pilot.pause(0.1)
                if panel.frame_index != initial:
                    break
            assert panel.frame_index != initial, (size, initial, panel.frame_index)
            await pilot.press("space")
            assert panel.paused
            frozen = panel.frame_index
            await pilot.pause(0.5)
            assert panel.frame_index == frozen
            await pilot.press("l")
            assert panel.frame_index == (frozen + 1) % spec.frame_count
            row = panel.query_one("#motion-row-0", Static).content.plain
            assert row == spec.frames[panel.frame_index][0], (size, repr(row))
            await pilot.press("h")
            assert panel.frame_index == frozen
            assert panel.paused
    # The result reward is a separate, default-visible playing panel.  It uses
    # the same credited source rows but is not the optional reference tab and
    # never gets cursor overlays or learner output.
    for size in ((80, 24), (100, 36), (188, 49)):
        app = L.make_app(reward_pages, result=True)
        async with app.run_test(size=size) as pilot:
            panel = app.query_one("#result-reward-panel")
            # An after-mount timer may already tick under a loaded machine.
            # Inspect the actual current frame, not a timing-dependent zero.
            initial = panel.frame_index
            assert str(app.query_one("#reward-heading", Static).content).startswith(
                "LESSON REWARD")
            first = panel.query_one("#reward-row-0", Static).content.plain
            assert first == reward.frames[initial][0], (size, repr(first))
            # Poll within the active Pilot test for the first observable tick;
            # do not sleep an entire loop then compare modulo frame counts.
            for _ in range(8):
                await pilot.pause(0.1)
                if panel.frame_index != initial:
                    break
            assert panel.frame_index != initial, (size, panel.frame_index)
            current = panel.query_one(
                "#reward-row-0", Static).content.plain
            assert current == reward.frames[panel.frame_index][0], (size, repr(current))
            await pilot.press("space")
            frozen = panel.frame_index
            await pilot.pause(0.5)
            assert panel.frame_index == frozen
            await pilot.press("l")
            assert panel.frame_index == (frozen + 1) % reward.frame_count
            await pilot.press("h")
            assert panel.frame_index == frozen
            assert panel.paused
    # Result actions are mounted on the real app, not only declared as an
    # unused shell binding.  Tab reaches the held progress page; both w and v
    # are accepted aliases for the existing watch owner.
    app = L.make_app(L.result_pages("RESULT ✓", "PROGRESS +10"), result=True)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.press("right")
        await pilot.pause()
        assert app.query_one("TabbedContent").active == "page-1"
        await pilot.press("w")
        assert app.return_value == "watch"
if __name__ == "__main__":
    asyncio.run(main())
    print("PASS Textual lesson/result model: three sizes, canonical rows, long prose, mounted signal, source-motion and default-visible result-reward playback/pause/step, result actions")
