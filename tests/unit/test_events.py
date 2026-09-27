"""Tests for the core event types and TaskManager event stream."""

import pytest

from core import task_manager as tm_module
from core.events import (
    ConfirmRequest,
    QuestionEvent,
    ReportEvent,
    StatusEvent,
    TodoItem,
    TodoUpdate,
    TokenDelta,
)
from core.task_manager import TaskManager


class _FakeResult:
    def __init__(self, final_output):
        self.final_output = final_output


class TestEventModels:
    """Verify each Event subclass round-trips through pydantic."""

    def test_status_event_defaults_to_info(self):
        e = StatusEvent(text="hi")
        assert e.kind == "info"

    def test_status_event_accepts_kind(self):
        assert StatusEvent(text="hi", kind="step").kind == "step"

    def test_token_delta_round_trip(self):
        assert TokenDelta(text="tok").text == "tok"

    def test_report_event_round_trip(self):
        assert ReportEvent(markdown="# hi").markdown == "# hi"

    def test_todo_update_defaults_empty(self):
        assert TodoUpdate().items == []

    def test_todo_update_with_items(self):
        u = TodoUpdate(items=[TodoItem(text="a"), TodoItem(text="b", done=True)])
        assert u.items[0].done is False
        assert u.items[1].done is True

    def test_confirm_request_optional_hint(self):
        assert ConfirmRequest(prompt="?").cost_hint is None

    def test_question_event(self):
        assert QuestionEvent(text="which?").text == "which?"


class TestTaskManagerYieldsEvents:
    """Stub Runner.run and assert TaskManager yields the right event stream."""

    @pytest.fixture(autouse=True)
    def _stub_runner(self, monkeypatch):
        async def fake_run(agent, prompt, session=None):
            return _FakeResult(final_output="stub answer")

        monkeypatch.setattr(tm_module.Runner, "run", staticmethod(fake_run))

    @pytest.mark.asyncio
    async def test_direct_workflow_emits_status_then_report(self):
        manager = TaskManager()
        events = [e async for e in manager.run("what is 2+2", session=None)]

        # trace status ("detected task type"), info status, then final report
        assert isinstance(events[0], StatusEvent) and events[0].kind == "trace"
        assert isinstance(events[1], StatusEvent) and events[1].kind == "info"
        assert isinstance(events[-1], ReportEvent)
        assert events[-1].markdown == "stub answer"

    @pytest.mark.asyncio
    async def test_no_rich_markup_leaks_from_core(self):
        manager = TaskManager()
        events = [e async for e in manager.run("what is 2+2", session=None)]
        for event in events:
            if isinstance(event, StatusEvent):
                assert "[" not in event.text and "]" not in event.text, (
                    f"core emitted Rich markup: {event.text!r}"
                )

    @pytest.mark.asyncio
    async def test_creative_workflow_yields_expected_sequence(self):
        manager = TaskManager()
        events = [e async for e in manager.run("design a cache", session=None)]

        kinds = [type(e).__name__ for e in events]
        assert kinds == ["StatusEvent", "StatusEvent", "ReportEvent"]
