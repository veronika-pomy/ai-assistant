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
    return console.input("\n[bold cyan]You[/bold cyan] >> ")


def is_exit_command(user_input: str) -> bool:
    """Check if user wants to exit the application.

    Args:
        user_input: The user's input string

    Returns:
        True if input is an exit command
    """
    return user_input.strip().lower() in ('exit', 'quit')
