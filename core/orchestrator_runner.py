"""Runs the orchestrator and yields UI events."""

from typing import AsyncIterator

from agents import RunConfig, Runner
from openai.types.responses import ResponseTextDeltaEvent

from config.settings import get_settings
from core.app_context import AppContext
from core.events import Event, TokenDelta
from custom_agents.orchestrator import create_orchestrator_agent


class OrchestratorRunner:
    def __init__(self):
        settings = get_settings()
        self._agent = create_orchestrator_agent()
        self._run_config = RunConfig(workflow_name=settings.trace_workflow_name)

    async def run(self, user_input: str, session) -> AsyncIterator[Event]:
        result = Runner.run_streamed(
            self._agent,
            user_input,
            session=session,
            context=AppContext(),
            max_turns=15,
            run_config=self._run_config,
        )
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                yield TokenDelta(text=event.data.delta)
