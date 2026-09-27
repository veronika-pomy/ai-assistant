from pydantic import BaseModel, Field
from agents import Agent, ModelSettings
from tools.web_search import get_web_search_tool

from config.settings import get_model_name


class SearchSummary(BaseModel):
    """Structured result of a single web search.

    Length is enforced by the instructions, not a schema constraint.
    """
    query: str = Field(description="The search query that produced this summary")
    summary: str = Field(
        description="Concise 2-3 paragraph summary of findings (under 300 words)"
    )


SEARCHER_INSTRUCTIONS = """
You are a research assistant performing web searches.

Given a search query, use the web_search tool to find relevant information,
then produce a concise, well-structured summary of your findings.

Your summary should:
- Be 2-3 paragraphs (under 300 words)
- Focus on key facts and insights
- Be objective and informative
- Cite or reference the types of sources when relevant

Return a SearchSummary with:
- query: the original search query you were asked to research
- summary: the summary text only, no preamble or meta-commentary
"""


def create_searcher_agent(model: str = None) -> Agent:
    """Factory function to create searcher agent with web search capability.

    Args:
        model: Model name override (falls back to configured MODEL_NAME).

    Returns:
        Agent instance configured with WebSearchTool and SearchSummary output.
    """
    # Require tool usage - searcher must use web search
    settings = ModelSettings(tool_choice="required")

    return Agent(
        name="Searcher",
        instructions=SEARCHER_INSTRUCTIONS,
        tools=[get_web_search_tool()],
        model=model or get_model_name(),
        model_settings=settings,
        output_type=SearchSummary,
    )
