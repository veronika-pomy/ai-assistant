import asyncio
from enum import Enum
from typing import AsyncIterator

# OpenAI Agents SDK imports
from agents import Runner
from openai.types.responses import ResponseTextDeltaEvent

# Local imports
from config.settings import get_settings
from core.events import Event, ReportEvent, StatusEvent, TokenDelta
from custom_agents.solver import create_solver_agent
from custom_agents.planner import create_planner_agent, SearchPlan
from custom_agents.searcher import create_searcher_agent, SearchSummary
from custom_agents.writer import create_writer_agent, Report


class TaskType(Enum):
    """Types of tasks the manager can handle."""
    RESEARCH = "research"
    PLANNING = "planning"
    DIRECT = "direct"
    CREATIVE = "creative"


class TaskManager:
    """Orchestrates agent execution based on task type.

    Yields typed :class:`core.events.Event` values; the UI decides how to
    render them.
    """

    def __init__(self):
        """Initialize task manager with settings."""
        self.settings = get_settings()

    async def run(self, query: str, session) -> AsyncIterator[Event]:
        """Analyze the query and drive the appropriate workflow.

        Args:
            query: User's query or task
            session: Session instance for conversation history

        Yields:
            Typed events describing progress and results.
        """
        task_type = await self._analyze_task_type(query)

        yield StatusEvent(text=f"Detected task type: {task_type.value}", kind="trace")

        if task_type == TaskType.RESEARCH:
            async for event in self._run_research_workflow(query, session):
                yield event
        elif task_type == TaskType.PLANNING:
            async for event in self._run_planning_workflow(query, session):
                yield event
        elif task_type == TaskType.CREATIVE:
            async for event in self._run_creative_workflow(query, session):
                yield event
        else:  # DIRECT
            async for event in self._run_direct_workflow(query, session):
                yield event

    async def _analyze_task_type(self, query: str) -> TaskType:
        """Determine task type from query keywords."""
        query_lower = query.lower()

        research_keywords = ['research', 'find out about', 'learn about', 'investigate',
                            'search for', 'look up', 'what are the latest', 'trends in']
        if any(keyword in query_lower for keyword in research_keywords):
            return TaskType.RESEARCH

        planning_keywords = ['plan', 'steps to', 'how to', 'roadmap', 'strategy',
                           'break down', 'organize', 'outline']
        if any(keyword in query_lower for keyword in planning_keywords):
            return TaskType.PLANNING

        creative_keywords = ['design', 'architect', 'create', 'build', 'develop',
                           'system for', 'approach to', 'solution for']
        if any(keyword in query_lower for keyword in creative_keywords):
            return TaskType.CREATIVE

        return TaskType.DIRECT

    async def _run_direct_workflow(self, query: str, session) -> AsyncIterator[Event]:
        """Direct Q&A workflow - just use solver agent, streamed."""
        yield StatusEvent(text="Solving directly...", kind="info")

        agent = create_solver_agent(self.settings.model_name)
        async for delta in self._stream_agent(agent, query, session):
            yield delta

    async def _run_planning_workflow(self, query: str, session) -> AsyncIterator[Event]:
        """Planning workflow - break down task into steps."""
        yield StatusEvent(text="Creating plan...", kind="info")

        agent = create_planner_agent(
            self.settings.model_name,
            how_many_searches=self.settings.how_many_searches,
        )
        result = await Runner.run(agent, query, session=session)

        plan = result.final_output

        if isinstance(plan, SearchPlan):
            output = "## Plan\n\n"
            for i, item in enumerate(plan.searches, 1):
                output += f"{i}. **{item.query}**\n   *{item.reason}*\n\n"
            yield ReportEvent(markdown=output)
        else:
            yield ReportEvent(markdown=str(plan))

    async def _run_creative_workflow(self, query: str, session) -> AsyncIterator[Event]:
        """Creative workflow - use solver with full reasoning, streamed."""
        yield StatusEvent(text="Thinking creatively...", kind="info")

        agent = create_solver_agent(self.settings.model_name)
        async for delta in self._stream_agent(agent, query, session):
            yield delta

    async def _run_research_workflow(self, query: str, session) -> AsyncIterator[Event]:
        """Research workflow: plan → search → write."""
        yield StatusEvent(text="Planning research...", kind="info")
        plan = await self._run_planner(query, session)

        yield StatusEvent(
            text=f"Created plan with {len(plan.searches)} searches",
            kind="step",
        )

        yield StatusEvent(text="Searching the web...", kind="info")
        search_results = await self._run_searches(plan, session)

        yield StatusEvent(
            text=f"Completed {len(search_results)} searches",
            kind="step",
        )

        yield StatusEvent(text="Writing report...", kind="info")
        report = await self._run_writer(query, search_results, session)

        output = f"## Summary\n\n{report.summary}\n\n"
        output += f"{report.markdown_report}\n\n"
        output += "## Follow-up Questions\n\n"
        for i, question in enumerate(report.follow_ups, 1):
            output += f"{i}. {question}\n"

        yield ReportEvent(markdown=output)

    async def _run_planner(self, query: str, session) -> SearchPlan:
        """Execute planner agent to create search plan."""
        agent = create_planner_agent(
            self.settings.model_name,
            how_many_searches=self.settings.how_many_searches,
        )
        result = await Runner.run(agent, query, session=session)
        return result.final_output

    async def _run_searches(self, plan: SearchPlan, session) -> list[SearchSummary]:
        """Execute search agent for each query in parallel."""
        async def search_single(search_item) -> SearchSummary:
            agent = create_searcher_agent(self.settings.model_name)
            result = await Runner.run(agent, search_item.query, session=session)
            return result.final_output

        tasks = [search_single(item) for item in plan.searches]
        results = await asyncio.gather(*tasks)

        return results

    async def _run_writer(
        self, query: str, search_results: list[SearchSummary], session
    ) -> Report:
        """Execute writer agent to synthesize research."""
        context = f"Original Query: {query}\n\n"
        context += "Research Summaries:\n\n"
        for i, result in enumerate(search_results, 1):
            context += f"### Source {i} — query: {result.query}\n{result.summary}\n\n"

        agent = create_writer_agent(self.settings.model_name)
        result = await Runner.run(agent, context, session=session)

        return result.final_output

    async def _stream_agent(self, agent, prompt: str, session) -> AsyncIterator[TokenDelta]:
        """Run an agent with streaming and yield TokenDelta events.

        Only text deltas are surfaced; other stream events (tool calls,
        agent handoffs, etc.) are ignored — this workflow is for
        single-agent free-text output where tokens are the useful signal.
        """
        result = Runner.run_streamed(agent, prompt, session=session)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                yield TokenDelta(text=event.data.delta)
