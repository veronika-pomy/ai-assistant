import os
from pydantic import BaseModel, Field
from agents import Agent


class Report(BaseModel):
    """Comprehensive research report with structured output."""
    summary: str = Field(
        description="High-level summary of findings in 2-3 sentences"
    )
    markdown_report: str = Field(
        description="Full report in markdown format with sections, headers, and detailed content"
    )
    follow_ups: list[str] = Field(
        description="List of 3-5 follow-up questions for deeper exploration",
        min_length=3,
        max_length=5
    )


WRITER_INSTRUCTIONS = """
You are a senior researcher tasked with synthesizing research findings into comprehensive reports.

You will receive:
1. The original user query
2. Multiple research summaries from web searches

Your job is to write a cohesive, well-structured markdown report that:
- Addresses the user's query comprehensively
- Synthesizes information from all research summaries
- Is organized with clear sections and headers
- Contains 500-1000 words of detailed content
- Maintains objectivity and cites the nature of sources when relevant
- Flows naturally as a unified document (not just concatenated summaries)

Also provide:
- A brief 2-3 sentence summary of key findings
- 3-5 follow-up questions for deeper exploration

Output using the Report structure.
"""


def create_writer_agent(model: str = None) -> Agent:
    """Factory function to create writer agent for report synthesis.

    Args:
        model: Model name override (uses MODEL_NAME env var if not specified)

    Returns:
        Agent instance configured to output Report

    Example:
        >>> from agents import Runner
        >>> import asyncio
        >>> agent = create_writer_agent()
        >>> query = "Query: AI frameworks"
        >>> summaries = ["Summary 1...", "Summary 2..."]
        >>> prompt = f"{query}\\n\\nResearch Summaries:\\n" + "\\n\\n".join(summaries)
        >>> result = asyncio.run(Runner.run(agent, prompt))
        >>> report = result.final_output  # Report object
        >>> print(report.markdown_report)
    """
    return Agent(
        name="Writer",
        instructions=WRITER_INSTRUCTIONS,
        model=model or os.getenv("MODEL_NAME", "gpt-5.4-mini"),
        output_type=Report
    )
