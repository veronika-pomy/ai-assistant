import asyncio
from enum import Enum
from typing import AsyncIterator

# OpenAI Agents SDK imports
from agents import Runner

# Local imports
from config.settings import get_settings
from custom_agents.solver import create_solver_agent
from custom_agents.planner import create_planner_agent, SearchPlan
from custom_agents.searcher import create_searcher_agent
from custom_agents.writer import create_writer_agent, Report


class TaskType(Enum):
    """Types of tasks the manager can handle."""
    RESEARCH = "research"
    PLANNING = "planning"
    DIRECT = "direct"
    CREATIVE = "creative"


class TaskManager:
    """Orchestrates agent execution based on task type.

    This manager analyzes incoming queries, determines the appropriate
    workflow, and coordinates agent execution with status updates.
    """

    def __init__(self):
        """Initialize task manager with settings."""
        self.settings = get_settings()

    async def run(self, query: str, session) -> AsyncIterator[str]:
        """Main entry point - analyzes query and runs appropriate workflow.

        Args:
            query: User's query or task
            session: Session instance for conversation history

        Yields:
            Status updates and final output as strings

        Example:
            >>> manager = TaskManager()
            >>> async for update in manager.run("What is 5+5?", session):
            ...     print(update)
        """
        # Analyze what type of task this is
        task_type = await self._analyze_task_type(query)

        yield f"[dim]Detected task type: {task_type.value}[/dim]"

        # Route to appropriate workflow
        if task_type == TaskType.RESEARCH:
            async for update in self._run_research_workflow(query, session):
                yield update
        elif task_type == TaskType.PLANNING:
            async for update in self._run_planning_workflow(query, session):
                yield update
        elif task_type == TaskType.CREATIVE:
            async for update in self._run_creative_workflow(query, session):
                yield update
        else:  # DIRECT
            async for update in self._run_direct_workflow(query, session):
                yield update

    async def _analyze_task_type(self, query: str) -> TaskType:
        """Determine task type from query keywords.

        Args:
            query: User's query

        Returns:
            TaskType enum value
        """
        query_lower = query.lower()

        # Research indicators
        research_keywords = ['research', 'find out about', 'learn about', 'investigate',
                            'search for', 'look up', 'what are the latest', 'trends in']
        if any(keyword in query_lower for keyword in research_keywords):
            return TaskType.RESEARCH

        # Planning indicators
        planning_keywords = ['plan', 'steps to', 'how to', 'roadmap', 'strategy',
                           'break down', 'organize', 'outline']
        if any(keyword in query_lower for keyword in planning_keywords):
            return TaskType.PLANNING

        # Creative indicators (design, architecture, complex reasoning)
        creative_keywords = ['design', 'architect', 'create', 'build', 'develop',
                           'system for', 'approach to', 'solution for']
        if any(keyword in query_lower for keyword in creative_keywords):
            return TaskType.CREATIVE

        # Default to direct for simple questions
        return TaskType.DIRECT

    async def _run_direct_workflow(self, query: str, session) -> AsyncIterator[str]:
        """Direct Q&A workflow - just use solver agent.

        Args:
            query: User's query
            session: Session instance

        Yields:
            Status updates and final answer
        """
        yield "[yellow]Solving directly...[/yellow]"

        agent = create_solver_agent(self.settings.model_name)
        result = await Runner.run(agent, query, session=session)

        yield result.final_output

    async def _run_planning_workflow(self, query: str, session) -> AsyncIterator[str]:
        """Planning workflow - break down task into steps.

        Args:
            query: User's query
            session: Session instance

        Yields:
            Status updates and plan
        """
        yield "[yellow]Creating plan...[/yellow]"

        # Use planner to break down the task
        agent = create_planner_agent(self.settings.model_name)
        result = await Runner.run(agent, query, session=session)

        plan = result.final_output

        # Format the plan output
        if isinstance(plan, SearchPlan):
            output = "## Plan\n\n"
            for i, item in enumerate(plan.searches, 1):
                output += f"{i}. **{item.query}**\n   *{item.reason}*\n\n"
            yield output
        else:
            yield str(plan)

    async def _run_creative_workflow(self, query: str, session) -> AsyncIterator[str]:
        """Creative workflow - use solver with full reasoning.

        Args:
            query: User's query
            session: Session instance

        Yields:
            Status updates and creative solution
        """
        yield "[yellow]Thinking creatively...[/yellow]"

        agent = create_solver_agent(self.settings.model_name)
        result = await Runner.run(agent, query, session=session)

        yield result.final_output

    async def _run_research_workflow(self, query: str, session) -> AsyncIterator[str]:
        """Research workflow: plan → search → write.

        Args:
            query: User's research query
            session: Session instance

        Yields:
            Status updates and final research report
        """
        # Step 1: Create search plan
        yield "[yellow]Planning research...[/yellow]"
        plan = await self._run_planner(query, session)

        yield f"[green]Created plan with {len(plan.searches)} searches[/green]"

        # Step 2: Execute searches in parallel
        yield "[yellow]Searching the web...[/yellow]"
        search_results = await self._run_searches(plan, session)

        yield f"[green]Completed {len(search_results)} searches[/green]"

        # Step 3: Write comprehensive report
        yield "[yellow]Writing report...[/yellow]"
        report = await self._run_writer(query, search_results, session)

        # Format final output
        output = f"## Summary\n\n{report.summary}\n\n"
        output += f"{report.markdown_report}\n\n"
        output += "## Follow-up Questions\n\n"
        for i, question in enumerate(report.follow_ups, 1):
            output += f"{i}. {question}\n"

        yield output

    async def _run_planner(self, query: str, session) -> SearchPlan:
        """Execute planner agent to create search plan.

        Args:
            query: Research query
            session: Session instance

        Returns:
            SearchPlan with list of searches
        """
        agent = create_planner_agent(self.settings.model_name)
        result = await Runner.run(agent, query, session=session)
        return result.final_output

    async def _run_searches(self, plan: SearchPlan, session) -> list[str]:
        """Execute search agent for each query in parallel.

        Args:
            plan: SearchPlan with queries
            session: Session instance

        Returns:
            List of search result summaries
        """
        async def search_single(search_item):
            """Run a single search."""
            agent = create_searcher_agent(self.settings.model_name)
            result = await Runner.run(agent, search_item.query, session=session)
            return result.final_output

        # Execute all searches in parallel
        tasks = [search_single(item) for item in plan.searches]
        results = await asyncio.gather(*tasks)

        return results

    async def _run_writer(self, query: str, search_results: list[str], session) -> Report:
        """Execute writer agent to synthesize research.

        Args:
            query: Original research query
            search_results: List of search summaries
            session: Session instance

        Returns:
            Report object with synthesis
        """
        # Format input for writer
        context = f"Original Query: {query}\n\n"
        context += "Research Summaries:\n\n"
        for i, result in enumerate(search_results, 1):
            context += f"### Source {i}\n{result}\n\n"

        agent = create_writer_agent(self.settings.model_name)
        result = await Runner.run(agent, context, session=session)

        return result.final_output
