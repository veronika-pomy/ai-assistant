import os
from agents import Agent


SOLVER_INSTRUCTIONS = """
You are a helpful assistant with a knack for solving creative and logical problems.
Answer the user's question directly and concisely.

Provide your response in Rich console markup without code blocks.
Rich markup uses square-bracket tags, e.g. [bold]word[/bold] or [green]word[/green] — never angle-bracket/HTML tags.
Use bold and color only for emphasis on specific words or short phrases — do not style entire sentences or paragraphs.
Body text should remain plain.

Do not ask the user questions or clarification; respond only with the answer.
"""


def create_solver_agent(model: str = None) -> Agent:
    """Factory function to create solver agent for direct problem-solving.

    Args:
        model: Model name override (uses MODEL_NAME env var if not specified)

    Returns:
        Agent instance configured for direct problem-solving

    Example:
        >>> from agents import Runner
        >>> import asyncio
        >>> agent = create_solver_agent()
        >>> result = asyncio.run(Runner.run(agent, "What is 25 * 34?"))
        >>> print(result.final_output)
    """
    return Agent(
        name="Solver",
        instructions=SOLVER_INSTRUCTIONS,
        model=model or os.getenv("MODEL_NAME", "gpt-5.4-mini")
    )
