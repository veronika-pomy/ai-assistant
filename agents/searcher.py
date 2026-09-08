import os
from agents import Agent, ModelSettings
from tools.web_search import get_web_search_tool


SEARCHER_INSTRUCTIONS = """
You are a research assistant performing web searches.

Given a search query, use the web_search tool to find relevant information,
then produce a concise, well-structured summary of your findings.

Your summary should:
- Be 2-3 paragraphs (under 300 words)
- Focus on key facts and insights
- Be objective and informative
- Cite or reference the types of sources when relevant

Reply only with the summary text - no preamble or meta-commentary.
"""


def create_searcher_agent(model: str = None) -> Agent:
    """Factory function to create searcher agent with web search capability.

    Args:
        model: Model name override (uses MODEL_NAME env var if not specified)

    Returns:
        Agent instance configured with WebSearchTool

    Example:
        >>> from agents import Runner
        >>> import asyncio
        >>> agent = create_searcher_agent()
        >>> result = asyncio.run(Runner.run(agent, "latest AI frameworks"))
        >>> print(result.final_output)  # Summary of search results
    """
    # Require tool usage - searcher must use web search
    settings = ModelSettings(tool_choice="required")

    return Agent(
        name="Searcher",
        instructions=SEARCHER_INSTRUCTIONS,
        tools=[get_web_search_tool()],
        model=model or os.getenv("MODEL_NAME", "gpt-5.4-mini"),
        model_settings=settings
    )
