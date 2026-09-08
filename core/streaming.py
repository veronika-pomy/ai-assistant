from rich.console import Console
from rich.live import Live
from rich.text import Text
from openai.types.responses import ResponseTextDeltaEvent


class StreamingUI:
    """Handles streaming output to Rich console with live updates.

    Provides utilities for displaying status messages, tool calls,
    and streaming agent responses in the terminal.
    """

    def __init__(self, console: Console):
        """Initialize streaming UI.

        Args:
            console: Rich Console instance for output
        """
        self.console = console

    def stream_status(self, message: str, style: str = "yellow"):
        """Display a status update message.

        Args:
            message: Status message to display
            style: Rich style name (default: yellow)
        """
        formatted = f"[{style}]⟳ {message}[/{style}]"
        self.console.print(formatted)

    def stream_tool_call(self, tool_name: str, args: dict = None):
        """Display a tool call notification.

        Args:
            tool_name: Name of the tool being called
            args: Optional tool arguments to display
        """
        msg = f"[cyan]🔧 Calling tool: {tool_name}[/cyan]"
        if args:
            msg += f"\n[dim]  Args: {args}[/dim]"
        self.console.print(msg)

    async def stream_agent_output(self, result):
        """Stream agent output with live updates.

        Args:
            result: RunResult from Runner.run_streamed() with stream_events()

        Yields:
            Each streamed text delta
        """
        buffer = ''
        with Live(Text.from_markup(''), refresh_per_second=20, console=self.console) as live:
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                    buffer += event.data.delta
                    live.update(Text.from_markup(buffer))
                    yield event.data.delta

    def format_final_output(self, text: str, markup: bool = True):
        """Display final formatted output.

        Args:
            text: Text to display
            markup: Whether to interpret Rich markup (default: True)
        """
        if markup:
            self.console.print(Text.from_markup(text))
        else:
            self.console.print(text)

    def show_agent_name(self, name: str = "Nelle"):
        """Display agent name header.

        Args:
            name: Agent name to display (default: Nelle)
        """
        self.console.print(f"\n[bold magenta]{name}[/bold magenta]")

    def show_separator(self):
        """Display a separator line."""
        self.console.print()


def show(console: Console, text: str):
    """Utility to print with Rich console with fallback.

    Args:
        console: Rich console instance
        text: Text to display
    """
    try:
        console.print(text)
    except Exception:
        print(text)
