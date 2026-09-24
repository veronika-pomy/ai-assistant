from agents import WebSearchTool
from .base import BaseTool


class WebSearch(BaseTool):
    """Web search tool wrapper for easy provider swapping.

    Wraps the OpenAI Agents SDK WebSearchTool and provides a clean
    interface for potential future replacement with other search providers.
    """

    def __init__(self, max_results: int = 5):
        """Initialize web search tool.

        Args:
            max_results: Maximum number of search results to return
        """
        self.max_results = max_results

    def get_tool_instance(self):
        """Return WebSearchTool instance.

        Returns:
            WebSearchTool instance from agents SDK
        """
        return WebSearchTool()

    @property
    def name(self) -> str:
        """Tool name.

        Returns:
            Tool identifier string
        """
        return "web_search"


def get_web_search_tool():
    """Factory function to get web search tool instance.

    Returns:
        WebSearchTool instance ready for use with agents

    Example:
        >>> tool = get_web_search_tool()
        >>> # Use with agent: tools=[tool]
    """
    return WebSearch().get_tool_instance()


# Future: Swap search provider implementation here
# def get_web_search_tool():
#     return TavilySearchTool()  # or DuckDuckGoTool(), etc.
