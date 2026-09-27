from pydantic import BaseModel, Field, create_model
from agents import Agent

from config.settings import get_model_name, get_settings


class SearchItem(BaseModel):
    """Single search query with reasoning."""
    reason: str = Field(description="Why this search is important for answering the query")
    query: str = Field(description="Search term to use")


class SearchPlan(BaseModel):
    """Research plan consisting of a list of targeted searches.

    The default constraint is a lower bound of 1 and no upper cap; the
    concrete N is enforced dynamically per invocation via
    :func:`build_search_plan_model`.
    """
    searches: list[SearchItem] = Field(
        description="List of search queries to execute",
        min_length=1,
    )


def build_search_plan_model(how_many_searches: int) -> type[BaseModel]:
    """Build a SearchPlan variant that requires exactly N searches."""
    return create_model(
        "SearchPlan",
        __base__=SearchPlan,
        searches=(
            list[SearchItem],
            Field(
                description=f"List of exactly {how_many_searches} search queries to execute",
                min_length=how_many_searches,
                max_length=how_many_searches,
            ),
        ),
    )


PLANNER_INSTRUCTIONS_TEMPLATE = """
You are a research planner helping to answer user questions through web research.

Given a user query, create a strategic plan of web searches that will provide comprehensive information.
Plan exactly {how_many_searches} diverse searches that cover different angles of the query.

Each search should:
- Target a specific aspect or angle
- Use effective search terms
- Have clear reasoning

Output your plan using the SearchPlan structure.
"""


def create_planner_agent(model: str = None, how_many_searches: int | None = None) -> Agent:
    """Factory function to create planner agent for research planning.

    Args:
        model: Model name override (falls back to configured MODEL_NAME).
        how_many_searches: Number of searches the plan must contain
            (falls back to configured HOW_MANY_SEARCHES).

    Returns:
        Agent instance configured to output a SearchPlan of exactly N items.
    """
    n = how_many_searches if how_many_searches is not None else get_settings().how_many_searches
    if n < 1:
        raise ValueError("how_many_searches must be positive")
    return Agent(
        name="Planner",
        instructions=PLANNER_INSTRUCTIONS_TEMPLATE.format(how_many_searches=n),
        model=model or get_model_name(),
        output_type=build_search_plan_model(n),
    )
