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


class _FakeDelta:
    """Duck-types openai.types.responses.ResponseTextDeltaEvent."""

    def __init__(self, delta: str):
        self.delta = delta


class _FakeRawEvent:
    """Duck-types the SDK's raw_response_event."""
    type = "raw_response_event"

    def __init__(self, delta_text: str):
        # Must be a real ResponseTextDeltaEvent instance so isinstance passes.
        from openai.types.responses import ResponseTextDeltaEvent
        self.data = ResponseTextDeltaEvent(
            content_index=0,
            delta=delta_text,
            item_id="item_1",
            logprobs=[],
            output_index=0,
            sequence_number=0,
            type="response.output_text.delta",
        )


class _FakeStreamedResult:
    """Duck-types Runner.run_streamed's return value."""

    def __init__(self, chunks: list[str]):
        self._chunks = chunks

    async def stream_events(self):
        for chunk in self._chunks:
            yield _FakeRawEvent(chunk)


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
    """Stub Runner and assert TaskManager yields the right event stream."""

    @pytest.fixture(autouse=True)
    def _stub_runner(self, monkeypatch):
        async def fake_run(agent, prompt, session=None):
            return _FakeResult(final_output="stub answer")

        def fake_run_streamed(agent, prompt, session=None):
            return _FakeStreamedResult(["hello ", "world"])

        monkeypatch.setattr(tm_module.Runner, "run", staticmethod(fake_run))
        monkeypatch.setattr(
            tm_module.Runner, "run_streamed", staticmethod(fake_run_streamed)
        )

    @pytest.mark.asyncio
    async def test_direct_workflow_streams_token_deltas(self):
        manager = TaskManager()
        events = [e async for e in manager.run("what is 2+2", session=None)]

        # trace status, info status, then token deltas from the streamed run.
        assert isinstance(events[0], StatusEvent) and events[0].kind == "trace"
        assert isinstance(events[1], StatusEvent) and events[1].kind == "info"
        deltas = [e for e in events if isinstance(e, TokenDelta)]
        assert [d.text for d in deltas] == ["hello ", "world"]

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
    async def test_creative_workflow_yields_status_then_deltas(self):
        manager = TaskManager()
        events = [e async for e in manager.run("design a cache", session=None)]

        kinds = [type(e).__name__ for e in events]
        assert kinds[:2] == ["StatusEvent", "StatusEvent"]
        assert all(k == "TokenDelta" for k in kinds[2:])
        assert len(kinds) >= 3  # at least one delta forwarded


class TestTokenDeltaForwarding:
    """Directly poke _stream_agent with a fake stream and check order."""

    @pytest.mark.asyncio
    async def test_stream_agent_forwards_deltas_in_order(self, monkeypatch):
        def fake_run_streamed(agent, prompt, session=None):
            return _FakeStreamedResult(["a", "b", "c", "d"])

        monkeypatch.setattr(
            tm_module.Runner, "run_streamed", staticmethod(fake_run_streamed)
        )

        manager = TaskManager()
        deltas = [
            d async for d in manager._stream_agent(agent=None, prompt="p", session=None)
        ]
        assert [d.text for d in deltas] == ["a", "b", "c", "d"]
        assert all(isinstance(d, TokenDelta) for d in deltas)
