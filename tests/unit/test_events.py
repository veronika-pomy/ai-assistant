import pytest

from core import orchestrator_runner as runner_module
from core.events import (
    ConfirmRequest,
    QuestionEvent,
    ReportEvent,
    StatusEvent,
    TodoItem,
    TodoUpdate,
    TokenDelta,
)


class _FakeRawEvent:
    type = "raw_response_event"

    def __init__(self, delta_text: str):
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
    def __init__(self, chunks: list[str]):
        self._chunks = chunks

    async def stream_events(self):
        for chunk in self._chunks:
            yield _FakeRawEvent(chunk)


class TestEventModels:

    def test_status_event_defaults_to_info(self):
        assert StatusEvent(text="hi").kind == "info"

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


class TestOrchestratorRunnerStream:
    @pytest.mark.asyncio
    async def test_forwards_text_deltas_in_order(self, monkeypatch):
        def fake_run_streamed(agent, prompt, **kwargs):
            return _FakeStreamedResult(["hello ", "world"])

        monkeypatch.setattr(
            runner_module.Runner, "run_streamed", staticmethod(fake_run_streamed)
        )

        runner = runner_module.OrchestratorRunner()
        events = [e async for e in runner.run("q", session=None)]

        assert [e.text for e in events] == ["hello ", "world"]
        assert all(isinstance(e, TokenDelta) for e in events)
