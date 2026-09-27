from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text


def format_markdown_report(markdown: str) -> Markdown:
    """Convert markdown string to Rich Markdown renderable.

    Args:
        markdown: Markdown text

    Returns:
        Rich Markdown object for rendering
    """
    return Markdown(markdown)


def show_error(console: Console, message: str):
    """Display error message in a styled panel.

    Args:
        console: Rich console instance
        message: Error message text
    """
    console.print(Panel(Text(message), style="red", title="Error"))
