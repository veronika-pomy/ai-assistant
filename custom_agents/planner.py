import os
from pydantic import BaseModel, Field
from agents import Agent


class SearchItem(BaseModel):
    """Single search query with reasoning."""
    reason: str = Field(description="Why this search is important for answering the query")
    query: str = Field(description="Search term to use")


class SearchPlan(BaseModel):
    """Research plan consisting of exactly 5 targeted searches."""
    searches: list[SearchItem] = Field(
        description="List of exactly 5 search queries to execute",
        min_length=5,
        max_length=5
    )


PLANNER_INSTRUCTIONS = """
You are a research planner helping to answer user questions through web research.

Given a user query, create a strategic plan of web searches that will provide comprehensive information.
Plan exactly 5 diverse searches that cover different angles of the query.

Each search should:
- Target a specific aspect or angle
- Use effective search terms
- Have clear reasoning

Output your plan using the SearchPlan structure.
"""


def create_planner_agent(model: str = None) -> Agent:
    """Factory function to create planner agent for research planning.

    Args:
        model: Model name override (uses MODEL_NAME env var if not specified)

    Returns:
        Agent instance configured to output SearchPlan

    Example:
        >>> from agents import Runner
        >>> import asyncio
        >>> agent = create_planner_agent()
        >>> result = asyncio.run(Runner.run(agent, "Research AI frameworks"))
        >>> plan = result.final_output  # SearchPlan object
        >>> for item in plan.searches:
        ...     print(f"{item.query}: {item.reason}")
    """
    return Agent(
        name="Planner",
        instructions=PLANNER_INSTRUCTIONS,
        model=model or os.getenv("MODEL_NAME", "gpt-5.4-mini"),
        output_type=SearchPlan
    )
