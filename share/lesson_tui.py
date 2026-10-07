"""Terminal lesson/result screens; no learner-state or grading authority.

Art rows are separate, non-wrapping widgets. Prose scrolls without ellipses.
The existing runtime owns questions, editor, feedback persistence and progress.
"""
from __future__ import annotations

import os
import sys
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class SourceMotionSpec:
    """Authored source poses for an optional, reference-only lesson tab.

    ``frames`` deliberately stores rows verbatim.  The interval is a tutorial
    playback choice supplied by the lesson author; it is never inferred from
    a source file or presented as the original animation rate.
    """

    frames: tuple[tuple[str, ...], ...]
    credit: str
    interval: float

    @property
    def frame_count(self):
        return len(self.frames)


@dataclass(frozen=True)
class ResultRewardSpec:
    """A credited multi-frame source animation shown on a held result.

    This is intentionally a different type from ``SourceMotionSpec``.  The
    lesson tab is an optional reference study; this spec is the result page's
    visible reward.  Both retain authored rows verbatim and neither is learner
    output.
    """

    frames: tuple[tuple[str, ...], ...]
    credit: str
    interval: float
    title: str = "LESSON REWARD · credited source animation · not learner output"

    @property
    def frame_count(self):
        return len(self.frames)


@dataclass(frozen=True)
class ModuleAnimationSpec(SourceMotionSpec):
    """Complete authored module sequence, separate from a source reference."""

    title: str = "MODULE ANIMATION · complete authored sequence · not learner output"


def _frame_rows(frame):
    """Coerce one authored frame to rows without trimming whitespace."""
    if isinstance(frame, str):
        return tuple(frame.splitlines())
    if isinstance(frame, dict):
        frame = frame.get("rows", ())
    return tuple(str(row) for row in (frame or ()))


def _motion_spec(card, spec_type):
    """Build one of the two labelled motion surfaces from card metadata."""
    motion = (card or {}).get(
        "module_reward" if spec_type in (ResultRewardSpec, ModuleAnimationSpec)
        and isinstance((card or {}).get("module_reward"), dict) else "source_motion")
    if not isinstance(motion, dict):
        return None
    frames = tuple(_frame_rows(frame) for frame in motion.get("frames", ()))
    if len(frames) < 2 or len(set(frames)) < 2:
        return None
    try:
        authored_interval = motion.get("interval", 0.35)
        interval = (1 / float(authored_interval["fps"])
                    if isinstance(authored_interval, dict) else float(authored_interval))
    except (TypeError, ValueError, KeyError, ZeroDivisionError):
        interval = 0.35
    if interval <= 0:
        interval = 0.35
    values = {
        "frames": frames,
        "credit": str(motion.get("credit", "source credit not supplied")),
        "interval": interval,
    }
    if spec_type is ResultRewardSpec:
        values["title"] = str(motion.get(
            "reward_title",
            ("MODULE REWARD · %s · complete %d-frame sequence · not learner output"
             % (motion.get("title", "authored animation"), len(frames)))
            if (card or {}).get("module_reward") else
            "LESSON REWARD · credited source animation · not learner output",
        ))
    elif spec_type is ModuleAnimationSpec:
        values["title"] = "MODULE ANIMATION · %s · %d frames · not learner output" % (
            motion.get("title", "complete authored sequence"), len(frames))
    return spec_type(**values)


def source_motion_spec(card):
    """Return an authored source-motion spec, or ``None`` when absent.

    A single pose is not promoted to an animation tab.  This keeps the tab
    truthful when a card has no authored motion and avoids inventing movement
    from a navigation-only study.
    """
    return _motion_spec(card, SourceMotionSpec)


def result_reward_spec(card):
    """Return the result-page reward spec for an eligible card.

    Cards with fewer than two distinct authored poses are intentionally
    ineligible, so a still, cursor overlay, or navigation study cannot be
    presented as moving reward art.
    """
    # Proportional art must use the native Ghostty animation path. Textual
    # terminal cells are not a faithful Saitamaar placement surface.
    if (card or {}).get("medium") == "proportional-sjis":
        return None
    return _motion_spec(card, ResultRewardSpec)


def module_animation_spec(card):
    if not isinstance((card or {}).get("module_reward"), dict):
        return None
    return _motion_spec(card, ModuleAnimationSpec)


reward_motion_spec = result_reward_spec


def _source_motion_fallback(spec):
    """Plain-terminal representation used when Textual is unavailable."""
    lines = [
        "SOURCE MOTION · tutorial reference · not learner output",
        "Playback interval: %.2fs (tutorial setting; not original FPS)" % spec.interval,
        "Frame 1/%d" % spec.frame_count,
        *spec.frames[0],
        "Credit: " + spec.credit,
        "Static reference only: interactive playback requires the Textual surface.",
    ]
    return "\n".join(lines)


def _result_reward_fallback(spec):
    """Show all authored reward poses when Textual is unavailable."""
    lines = [spec.title,
             "Playback interval: %.2fs (tutorial setting; not original FPS)"
             % spec.interval]
    for index, frame in enumerate(spec.frames, 1):
        lines += ["Frame %d/%d" % (index, spec.frame_count), *frame]
    lines += ["Credit: " + spec.credit,
              "Static fallback: interactive playback requires the Textual surface."]
    return "\n".join(lines)


def _cell_width(value):
    """Return terminal-cell width without normalising the source text."""
    return sum(2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
               for char in str(value))


def enabled():
    if (os.environ.get("VIM_DAILY_TEXTUAL", "1") == "0"
            or not sys.stdin.isatty() or not sys.stdout.isatty()):
        return False
    try:
        import textual  # noqa: F401
    except ImportError:
        return False
    return True


def _navigation_overlay(rows, position, marker="▲"):
    """Return an opt-in cursor overlay while leaving ``rows`` untouched.

    The overlay is deliberately a separate diagnostic line.  It is not an
    animation frame and never becomes part of the saved artifact.  ``row``
    and ``column`` are the one-based display coordinates used by the runtime's
    cursor receipt.
    """
    rows = [str(row) for row in rows]
    position = position or {}
    row_number = max(1, int(position.get("row", 1)))
    column = max(1, int(position.get("column", 1)))
    overlay = ["" for _ in rows]
    if row_number <= len(rows):
        prefix = " " * max(0, column - 1)
        overlay[row_number - 1] = prefix + marker
    return rows, overlay


def navigation_study(card):
    """Build a truthful cursor-travel study for an unchanged-art lesson.

    Navigation cards have one canonical frame, so showing them as an
    animation would be misleading.  This page repeats the exact rows under a
    labelled start/goal overlay and keeps the two overlays separate from the
    canonical artwork.
    """
    if not card or not card.get("navigation_only"):
        return None
    rows = [str(row) for row in card.get("start", [])]
    first = rows[0] if rows else ""
    prefix = first[:len(first) - len(first.lstrip())]
    start = {"row": 1, "column": _cell_width(prefix) + 1}
    goal = card.get("cursor_goal") or start
    labels = (
        "NAVIGATION STUDY · unchanged artwork · not animation",
        "START CURSOR · initial editor position",
        "AFTER %s · cursor-receipt goal" % (card.get("expected") or "recipe"),
    )
    start_rows, start_overlay = _navigation_overlay(rows, start)
    _goal_rows, goal_overlay = _navigation_overlay(rows, goal)
    lines = [labels[0], "", labels[1]]
    for row, caret in zip(start_rows, start_overlay):
        lines.append(row)
        if caret:
            lines.append(caret)
    lines += ["", labels[2]]
    for row, caret in zip(rows, goal_overlay):
        lines.append(row)
        if caret:
            lines.append(caret)
    lines += ["", "The caret is a UI overlay; the artwork above remains byte-for-byte unchanged."]
    return "\n".join(lines)


def lesson_pages(content, *, card=None):
    """Return lesson tabs with optional navigation and source studies."""
    pages = [("Lesson", content)]
    study = navigation_study(card)
    if study:
        pages.append(("Navigation study", study))
    motion = source_motion_spec(card)
    if motion:
        pages[0] = ("Lesson", "SOURCE MOTION AVAILABLE · press m to play the source poses; the study artifact stays separate.\n\n" + str(content))
        pages.append(("Source motion", motion))
    module = module_animation_spec(card)
    if module and (card or {}).get("medium") != "proportional-sjis":
        pages[0] = ("Lesson", "FULL MODULE ANIMATION · press a to play all %d frames; the editable study stays separate.\n\n%s" % (
            module.frame_count, pages[0][1]))
        pages.append(("Module animation", module))
    return pages


class _ResultPages(list):
    """List-compatible result pages with optional non-prose reward metadata."""

    def __init__(self, feedback, progress, reward=None):
        super().__init__([("Feedback", feedback), ("Progress", progress)])
        self.reward = reward


def _coerce_result_reward(reward):
    if reward is None or isinstance(reward, ResultRewardSpec):
        return reward
    if isinstance(reward, SourceMotionSpec):
        return ResultRewardSpec(reward.frames, reward.credit, reward.interval)
    if isinstance(reward, dict):
        if "source_motion" in reward:
            return result_reward_spec(reward)
        if "frames" in reward:
            return _motion_spec({"source_motion": reward}, ResultRewardSpec)
    return None


def result_pages(feedback, progress, *, reward=None):
    """Return held result tabs plus an optional visible playing reward.

    The list shape stays backward-compatible for route evidence and fallback
    callers.  ``reward`` is side metadata consumed only by ``make_app``; it is
    not confused with feedback prose or learner output.
    """
    return _ResultPages(feedback, progress, _coerce_result_reward(reward))


def make_app(pages, *, result=False, mounted=None):
    from rich.text import Text
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import HorizontalScroll, VerticalScroll
    from textual.widget import Widget
    from textual.widgets import Footer, Static, TabbedContent, TabPane
    reward = getattr(pages, "reward", None)

    class SourceMotionPanel(Widget):
        """Reference playback with exact, independently scrollable art rows."""

        def __init__(self, spec):
            super().__init__(id=("module-animation-panel" if isinstance(spec, ModuleAnimationSpec)
                                 else "source-motion-panel"))
            self.spec = spec
            self.frame_index = 0
            self.paused = False

        @property
        def frame_rows(self):
            return self.spec.frames[self.frame_index]

        def compose(self) -> ComposeResult:
            yield Static(
                spec_title if (spec_title := getattr(self.spec, "title", None)) else
                "SOURCE MOTION · tutorial reference · not learner output",
                id="motion-heading", markup=False,
            )
            yield Static(
                "Playback interval: %.2fs (tutorial setting; not original FPS)"
                % self.spec.interval,
                id="motion-speed", markup=False,
            )
            yield Static("", id="motion-frame", markup=False)
            for index in range(max(map(len, self.spec.frames))):
                with HorizontalScroll():
                    yield Static(
                        "", id="motion-row-%d" % index,
                        classes="art motion-row", markup=False,
                    )
            yield Static("Credit: " + self.spec.credit, id="motion-credit", markup=False)
            yield Static(
                "Controls: space pause/play · h/l step · Enter closes this screen",
                id="motion-controls", markup=False,
            )

        def on_mount(self):
            self.render_frame()
            self.set_interval(self.spec.interval, self.advance)

        def render_frame(self):
            self.query_one("#motion-frame", Static).update(
                "Frame %d/%d" % (self.frame_index + 1, self.spec.frame_count)
            )
            for index in range(max(map(len, self.spec.frames))):
                row = self.frame_rows[index] if index < len(self.frame_rows) else ""
                self.query_one("#motion-row-%d" % index, Static).update(
                    Text.from_ansi(row)
                )

        def advance(self):
            if self.paused:
                return
            self.frame_index = (self.frame_index + 1) % self.spec.frame_count
            self.render_frame()

        def toggle_pause(self):
            self.paused = not self.paused

        def step(self, amount):
            self.paused = True
            self.frame_index = (self.frame_index + amount) % self.spec.frame_count
            self.render_frame()

    class ResultRewardPanel(Widget):
        """Visible result reward playback using credited source poses."""

        def __init__(self, spec):
            super().__init__(id="result-reward-panel")
            self.spec = spec
            self.frame_index = 0
            self.paused = False

        @property
        def frame_rows(self):
            return self.spec.frames[self.frame_index]

        def compose(self) -> ComposeResult:
            yield Static(self.spec.title, id="reward-heading", markup=False)
            yield Static(
                "Playback interval: %.2fs (tutorial setting; not original FPS)"
                % self.spec.interval,
                id="reward-speed", markup=False,
            )
            yield Static("", id="reward-frame", markup=False)
            for index in range(max(map(len, self.spec.frames))):
                with HorizontalScroll():
                    yield Static(
                        "", id="reward-row-%d" % index,
                        classes="art reward-art", markup=False,
                    )
            yield Static("Credit: " + self.spec.credit, id="reward-credit", markup=False)
            yield Static(
                "Reward controls: space pause/play · h/l step · Enter closes this screen",
                id="reward-controls", markup=False,
            )

        def on_mount(self):
            self.render_frame()
            self.set_interval(self.spec.interval, self.advance)

        def render_frame(self):
            self.query_one("#reward-frame", Static).update(
                "Frame %d/%d" % (self.frame_index + 1, self.spec.frame_count)
            )
            for index in range(max(map(len, self.spec.frames))):
                row = self.frame_rows[index] if index < len(self.frame_rows) else ""
                self.query_one("#reward-row-%d" % index, Static).update(
                    Text.from_ansi(row)
                )

        def advance(self):
            if self.paused:
                return
            self.frame_index = (self.frame_index + 1) % self.spec.frame_count
            self.render_frame()

        def toggle_pause(self):
            self.paused = not self.paused

        def step(self, amount):
            self.paused = True
            self.frame_index = (self.frame_index + amount) % self.spec.frame_count
            self.render_frame()

    class LessonApp(App):
        CSS = """
        Screen { background: #101018; color: #e4e4e4; }
        TabbedContent { height: 1fr; }
        VerticalScroll { height: 1fr; padding: 0 1; }
        Static { height: auto; }
        HorizontalScroll { height: auto; max-height: 3; }
        .art { width: auto; height: 1; text-wrap: nowrap; }
        SourceMotionPanel { height: auto; }
        ResultRewardPanel { height: auto; margin-bottom: 1; }
        Footer { height: auto; }
        """
        BINDINGS = [Binding("enter", "continue", "Continue"),
                    Binding("q", "close", "Close"),
                    Binding("j", "down", "Down", show=False),
                    Binding("k", "up", "Up", show=False),
                    Binding("space", "motion_pause", "Pause", show=False),
                    Binding("h", "motion_step_back", "Step back", show=False),
                    Binding("l", "motion_step_forward", "Step forward", show=False)] + (
            [Binding("r", "route('repeat')", "Repeat"),
             Binding("n", "route('next')", "Next"),
             Binding("f", "route('feedback')", "Feedback"),
             Binding("d", "route('dashboard')", "Dashboard"),
             Binding("v,w", "route('watch')", "Watch")] if result else [])
        if any(isinstance(body, SourceMotionSpec) for _title, body in pages):
            BINDINGS.append(Binding("m", "source_motion", "Source motion"))
        if any(isinstance(body, ModuleAnimationSpec) for _title, body in pages):
            BINDINGS.append(Binding("a", "module_animation", "Module animation"))

        def compose(self) -> ComposeResult:
            with TabbedContent():
                for index, (title, content) in enumerate(pages):
                    with TabPane(title, id=f"page-{index}"):
                        with VerticalScroll():
                            # Keep the credited reward first on Feedback so it
                            # is visible and playing by default, rather than
                            # hidden in the optional source-reference tab or
                            # below a long prose body.
                            if result and index == 0 and reward:
                                yield ResultRewardPanel(reward)
                            if isinstance(content, SourceMotionSpec):
                                yield SourceMotionPanel(content)
                                continue
                            # splitlines preserves leading/trailing spaces in
                            # each canonical art row.  It only removes the
                            # transport newline between rows.
                            for row in str(content).splitlines():
                                text = Text.from_ansi(row)
                                # The canonical art never enters prose wrapping.
                                if "│" in text.plain or "┃" in text.plain:
                                    with HorizontalScroll():
                                        yield Static(text, classes="art", markup=False)
                                else:
                                    yield Static(text, markup=False)
            yield Footer()

        def on_mount(self):
            if mounted:
                # Signal only after the layout is actually painted.
                self.call_after_refresh(mounted)

        def action_continue(self):
            self.exit("close" if result else "edit")

        def action_close(self):
            self.exit("close")

        def action_route(self, route):
            self.exit(route)

        def action_down(self):
            self.query_one(TabbedContent).active_pane.query_one(VerticalScroll).scroll_down()

        def action_up(self):
            self.query_one(TabbedContent).active_pane.query_one(VerticalScroll).scroll_up()

        def _active_motion(self):
            pane = self.query_one(TabbedContent).active_pane
            for panel_type in (SourceMotionPanel, ResultRewardPanel):
                try:
                    return pane.query_one(panel_type)
                except Exception:
                    continue
            return None

        def action_motion_pause(self):
            panel = self._active_motion()
            if panel:
                panel.toggle_pause()

        def action_source_motion(self):
            for index, (_title, body) in enumerate(pages):
                if isinstance(body, SourceMotionSpec) and not isinstance(body, ModuleAnimationSpec):
                    self.query_one(TabbedContent).active = "page-%d" % index
                    return

        def action_module_animation(self):
            for index, (_title, body) in enumerate(pages):
                if isinstance(body, ModuleAnimationSpec):
                    self.query_one(TabbedContent).active = "page-%d" % index
                    return

        def action_motion_step_back(self):
            panel = self._active_motion()
            if panel:
                panel.step(-1)

        def action_motion_step_forward(self):
            panel = self._active_motion()
            if panel:
                panel.step(1)

    return LessonApp()


def show(pages, *, result=False, mounted=None):
    try:
        return make_app(pages, result=result, mounted=mounted).run()
    except ImportError:
        # The runtime supplies a stdlib fallback when the managed Textual
        # environment is absent.  This branch is intentionally plain and does
        # not mutate learner state or claim that a screen was painted.
        reward = getattr(pages, "reward", None)
        if result and reward:
            print("\nReward")
            rendered_reward = _result_reward_fallback(reward)
            print(rendered_reward, end="" if rendered_reward.endswith("\n") else "\n")
        for title, content in pages:
            print("\n%s" % title)
            rendered = (_source_motion_fallback(content)
                        if isinstance(content, SourceMotionSpec) else str(content))
            print(rendered, end="" if rendered.endswith("\n") else "\n")
        return "close" if result else "edit"
