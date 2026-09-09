import asyncio
from rich.console import Console

from config.settings import get_settings
from core.session import SessionManager
from core.task_manager import TaskManager
from ui.banner import show_welcome
from ui.prompts import prompt_user, is_exit_command
from ui.formatters import format_markdown_report, show_error


console = Console()


async def main():
    """Main REPL loop for Nelle assistant."""
    # Initialize
    settings = get_settings()
    show_welcome(console)

    session = SessionManager(settings.session_name, ":memory:")
    manager = TaskManager()

    first = True

    # REPL loop
    while True:
        user_input = prompt_user(console, first=first)
        first = False

        # Handle empty input
        if not user_input.strip():
            console.print("[yellow]Empty input - try again![/yellow]")
            continue

        # Handle exit commands
        if is_exit_command(user_input):
            console.print("[green]Thanks! Have a great day![/green]")
            break

        # Run task and stream updates
        try:
            console.print("\n[bold magenta]Nelle[/bold magenta]")

            async for update in manager.run(user_input, session.get_session()):
                # Check if this is a markdown report (starts with ##)
                if update.strip().startswith("##"):
                    console.print(format_markdown_report(update))
                else:
                    # Print status updates directly with Rich markup
                    console.print(update)

        except Exception as e:
            show_error(console, f"Error: {str(e)}")
            console.print("\n[dim]Hint: Check your .env configuration and API key.[/dim]")


if __name__ == "__main__":
    asyncio.run(main())
