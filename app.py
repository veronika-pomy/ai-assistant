import asyncio
from rich.console import Console

from config.settings import get_settings
from core.session import SessionManager
from core.task_manager import TaskManager
from ui.banner import show_welcome
from ui.prompts import prompt_user, is_exit_command
from ui.renderer import Renderer
from ui.formatters import show_error


console = Console()


async def main():
    """Main REPL loop for Nelle assistant. Handles user input and task execution."""
    settings = get_settings()
    show_welcome(console)

    session = SessionManager(settings.session_name, ":memory:")
    manager = TaskManager()
    renderer = Renderer(console)

    first = True

    while True:
        user_input = prompt_user(console, first=first)
        first = False

        if not user_input.strip():
            console.print("[yellow]Empty input - try again![/yellow]")
            continue

        if is_exit_command(user_input):
            console.print("[green]Thanks! Have a great day![/green]")
            break

        try:
            console.print("\n[bold magenta]Nelle[/bold magenta]")

            async for event in manager.run(user_input, session.get_session()):
                renderer.render(event)

        except Exception as e:
            show_error(console, f"Error: {str(e)}")
            console.print("\n[dim]Hint: Check your .env configuration and API key.[/dim]")
        finally:
            # Rich Live and input() collide; always close any live stream
            # before next prompt.
            renderer.finish_turn()


if __name__ == "__main__":
    asyncio.run(main())
