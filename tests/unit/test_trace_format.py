from agents.items import ToolCallItem
from openai.types.responses.response_function_tool_call import ResponseFunctionToolCall

from core.orchestrator_runner import (
    _format_tool_call,
    _format_tool_output,
    _summarize_args,
)


class _StubAgent:
    name = "stub"


def _call(name: str, arguments: str, call_id: str = "call_1") -> ToolCallItem:
    return ToolCallItem(
        agent=_StubAgent(),
        raw_item=ResponseFunctionToolCall(
            arguments=arguments,
            call_id=call_id,
            name=name,
            type="function_call",
        ),
    )


def test_summarize_args_string():
    assert _summarize_args('{"query": "python 3.13"}') == 'query="python 3.13"'


def test_summarize_args_list_shows_count():
    assert _summarize_args('{"queries": ["a", "b", "c"]}') == "queries=[3 items]"


def test_summarize_args_clips_long_string():
    long = "x" * 100
    out = _summarize_args(f'{{"q": "{long}"}}')
    assert out.endswith("…")
    assert len(out) < 100


def test_format_tool_call_function():
    trace = _format_tool_call(_call("web_search", '{"query": "latest python"}'), pending={})
    assert trace == '→ web_search(query="latest python")'


def test_format_tool_call_records_pending():
    pending: dict[str, str] = {}
    _format_tool_call(_call("run_research", '{"queries": []}', call_id="c1"), pending)
    assert pending == {"c1": "run_research"}


def test_format_tool_output_uses_pending():
    class _FakeOutputItem:
        raw_item = {"type": "function_call_output", "call_id": "c1", "output": "..."}

    trace = _format_tool_output(_FakeOutputItem(), pending={"c1": "run_research"})
    assert trace == "← run_research done"


def test_format_tool_output_falls_back_when_unknown():
    class _FakeOutputItem:
        raw_item = {"type": "function_call_output", "output": "..."}

    assert _format_tool_output(_FakeOutputItem(), pending={}) == "← tool done"
