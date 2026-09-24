from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel


def show(console: Console, text: str):
    """Display text using Rich console with fallback.

    Args:
        console: Rich console instance
        text: Text to display
    """
    try:
        console.print(text)
    except Exception:
        print(text)


def format_status(message: str, style: str = "yellow") -> str:
    """Format a status message with style.

    Args:
        message: Status message text
        style: Rich style name (default: yellow)

    Returns:
        Formatted status string
    """
    return f"[{style}]⟳ {message}[/{style}]"


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
    console.print(Panel(message, style="red", title="Error"))
