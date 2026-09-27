import sys

# Prefer GNU readline via the gnureadline package on macOS
try:
    import gnureadline

    sys.modules["readline"] = gnureadline
except ImportError:
    import readline  # noqa: F401 — enables arrow-key editing and history

from rich.console import Console


def prompt_user(console: Console, first: bool = False) -> str:
    """Prompt user for input.

    Args:
        console: Rich console instance
        first: Whether this is the first prompt in the session

    Returns:
        User input string
    """
    if first:
        console.print("[bold yellow]→ What can I help you with today?[/bold yellow]")
    # Split the prompt: Rich prints the styled "You" (invisible to
    # readline), and ">> " is handed to input() as a plain-text prompt
    # so readline enforces it as an immovable left-edit boundary.
    console.print("\n[bold cyan]You[/bold cyan] ", end="")
    return input(">> ")


def is_exit_command(user_input: str) -> bool:
    """Check if user wants to exit the application.

    Args:
        user_input: The user's input string

    Returns:
        True if input is an exit command
    """
    return user_input.strip().lower() in ('exit', 'quit')
