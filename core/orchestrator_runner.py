"""Runs the orchestrator and yields UI events."""

import json
from typing import AsyncIterator

from agents import RunConfig, Runner
from agents.items import ToolCallItem, ToolCallOutputItem
from openai.types.responses import ResponseTextDeltaEvent
from openai.types.responses.response_function_tool_call import ResponseFunctionToolCall
from openai.types.responses.response_function_web_search import ResponseFunctionWebSearch

from config.settings import get_settings
from core.app_context import AppContext
from core.events import Event, StatusEvent, TokenDelta
from custom_agents.orchestrator import create_orchestrator_agent


_MAX_ARG_CHARS = 60


class OrchestratorRunner:
    def __init__(self):
        settings = get_settings()
        self._agent = create_orchestrator_agent()
        self._run_config = RunConfig(workflow_name=settings.trace_workflow_name)

    async def run(self, user_input: str, session) -> AsyncIterator[Event]:
        # call_id → tool name, so tool outputs can echo the name they resolve.
        pending: dict[str, str] = {}

        result = Runner.run_streamed(
            self._agent,
            user_input,
            session=session,
            context=AppContext(),
            max_turns=15,
            run_config=self._run_config,
        )
        async for event in result.stream_events():
            if event.type == "raw_response_event":
                if isinstance(event.data, ResponseTextDeltaEvent):
                    yield TokenDelta(text=event.data.delta)
                continue

            if event.type == "run_item_stream_event":
                trace = _trace_for_run_item(event.item, pending)
                if trace:
                    yield StatusEvent(text=trace, kind="trace")
                continue

            if event.type == "agent_updated_stream_event":
                yield StatusEvent(
                    text=f"agent: {event.new_agent.name}", kind="trace"
                )


def _trace_for_run_item(item, pending: dict[str, str]) -> str | None:
    if isinstance(item, ToolCallItem):
        return _format_tool_call(item, pending)
    if isinstance(item, ToolCallOutputItem):
        return _format_tool_output(item, pending)
    return None


def _format_tool_call(item: ToolCallItem, pending: dict[str, str]) -> str:
    raw = item.raw_item
    if isinstance(raw, ResponseFunctionToolCall):
        pending[raw.call_id] = raw.name
        return f"→ {raw.name}({_summarize_args(raw.arguments)})"
    if isinstance(raw, ResponseFunctionWebSearch):
        query = getattr(raw.action, "query", None)
        if query:
            return f'→ web_search("{_clip(query)}")'
        return "→ web_search"
    name = item._resolved_tool_name or type(raw).__name__
    return f"→ {name}"


def _format_tool_output(item: ToolCallOutputItem, pending: dict[str, str]) -> str:
    raw = item.raw_item
    call_id = raw.get("call_id") if isinstance(raw, dict) else getattr(raw, "call_id", None)
    name = pending.pop(call_id, None) if call_id else None
    if not name and isinstance(raw, dict):
        name = raw.get("name")
    return f"← {name} done" if name else "← tool done"


def _summarize_args(raw_args: str) -> str:
    try:
        parsed = json.loads(raw_args)
    except (ValueError, TypeError):
        return _clip(raw_args)
    if not isinstance(parsed, dict):
        return _clip(str(parsed))
    parts = []
    for k, v in parsed.items():
        if isinstance(v, list):
            parts.append(f"{k}=[{len(v)} items]")
        elif isinstance(v, str):
            parts.append(f'{k}="{_clip(v)}"')
        else:
            parts.append(f"{k}={_clip(str(v))}")
    return _clip(", ".join(parts))


def _clip(s: str) -> str:
    return s if len(s) <= _MAX_ARG_CHARS else s[:_MAX_ARG_CHARS] + "…"
