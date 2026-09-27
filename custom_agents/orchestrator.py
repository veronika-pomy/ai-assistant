"""Routing orchestrator: picks a tool per user turn."""

import asyncio

from agents import Agent, RunContextWrapper, Runner, function_tool

from config.settings import get_model_name, get_orchestrator_model_name
from core.app_context import AppContext
from custom_agents.searcher import SearchSummary, create_searcher_agent
from custom_agents.solver import create_solver_agent
from custom_agents.writer import Report, create_writer_agent
from tools.web_search import get_web_search_tool


ORCHESTRATOR_INSTRUCTIONS = """
You are Nelle, a helpful assistant. Route each user turn by picking the
right approach:

- Conversational, opinion, math, or reasoning questions you can handle
  yourself: answer directly with your own words.
- Longer direct answers that need focused reasoning: call the `answer`
  tool.
- A single factual lookup that needs the web: call `web_search`.
- A genuinely deep question that benefits from multiple angles synthesised
  into a report: call `run_research` with 3–5 diverse search queries.

Never call `run_research` for a single-fact question. Never call
`web_search` when the user is asking you to reason about text they
already provided. When in doubt, prefer the cheaper option.

If the request is genuinely ambiguous, ask ONE clarifying question
instead of guessing.

Respond in plain text or Rich console markup — square-bracket tags only,
never angle-bracket/HTML. Use bold and colour for emphasis only; keep
body text plain.
"""


async def _run_research_pipeline(queries: list[str]) -> str:
    model = get_model_name()

    async def _search_one(query: str) -> SearchSummary:
        searcher = create_searcher_agent(model)
        result = await Runner.run(searcher, query)
        return result.final_output

    # session-less sub-runs: concurrent SQLiteSession writes would race.
    summaries: list[SearchSummary] = await asyncio.gather(
        *(_search_one(q) for q in queries)
    )

    context = "Research summaries:\n\n"
    for i, s in enumerate(summaries, 1):
        context += f"### Source {i} — query: {s.query}\n{s.summary}\n\n"

    writer = create_writer_agent(model)
    result = await Runner.run(writer, context)
    report: Report = result.final_output

    output = f"## Summary\n\n{report.summary}\n\n{report.markdown_report}\n\n"
    output += "## Follow-up Questions\n\n"
    for i, q in enumerate(report.follow_ups, 1):
        output += f"{i}. {q}\n"
    return output


@function_tool
async def run_research(
    ctx: RunContextWrapper[AppContext],
    queries: list[str],
) -> str:
    """Parallel web searches synthesised into a markdown report.

    Args:
        queries: 3–5 diverse search queries covering different angles.
    """
    # T2.3 will await ctx.context.confirm(...) here.
    return await _run_research_pipeline(queries)


def create_orchestrator_agent(model: str | None = None) -> Agent:
    """Routing agent. Model falls back to ORCHESTRATOR_MODEL env."""
    solver = create_solver_agent()
    return Agent(
        name="Orchestrator",
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        model=model or get_orchestrator_model_name(),
        tools=[
            solver.as_tool(
                tool_name="answer",
                tool_description=(
                    "Answer the user's question directly with focused "
                    "reasoning. Use for longer explanations that don't "
                    "need the web."
                ),
            ),
            get_web_search_tool(),
            run_research,
        ],
    )
