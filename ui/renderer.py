"""Renders core events to the terminal via Rich.

All presentation lives here; :mod:`core` yields plain typed events and does
not touch Rich. The Renderer owns the console.
"""

from rich.console import Console

from core.events import (
    ConfirmRequest,
    Event,
    QuestionEvent,
    ReportEvent,
    StatusEvent,
    TodoUpdate,
    TokenDelta,
)
from ui.formatters import format_markdown_report


_STATUS_STYLE = {
    "info": "yellow",
    "step": "green",
    "trace": "dim",
}


class Renderer:
    """Dispatches core events onto a Rich console."""

    def __init__(self, console: Console):
        self.console = console

    def render(self, event: Event) -> None:
        if isinstance(event, StatusEvent):
            self._render_status(event)
        elif isinstance(event, TokenDelta):
            self._render_token_delta(event)
        elif isinstance(event, ReportEvent):
            self._render_report(event)
        elif isinstance(event, TodoUpdate):
            self._render_todo(event)
        elif isinstance(event, ConfirmRequest):
            self._render_confirm(event)
        elif isinstance(event, QuestionEvent):
            self._render_question(event)
        else:
            self.console.print(str(event))

    def _render_status(self, event: StatusEvent) -> None:
        style = _STATUS_STYLE.get(event.kind, "yellow")
        self.console.print(f"[{style}]{event.text}[/{style}]")

    def _render_token_delta(self, event: TokenDelta) -> None:
        # T1.3 will replace this with a Rich Live-driven stream. For now we
        # print each delta so wiring can be smoke-tested end-to-end.
        self.console.print(event.text, end="", soft_wrap=True)

    def _render_report(self, event: ReportEvent) -> None:
        self.console.print(format_markdown_report(event.markdown))

    def _render_todo(self, event: TodoUpdate) -> None:
        for item in event.items:
            mark = "[green]✓[/green]" if item.done else "[dim]•[/dim]"
            self.console.print(f"{mark} {item.text}")

    def _render_confirm(self, event: ConfirmRequest) -> None:
        hint = f" [dim]({event.cost_hint})[/dim]" if event.cost_hint else ""
        self.console.print(f"[bold yellow]? {event.prompt}[/bold yellow]{hint}")

    def _render_question(self, event: QuestionEvent) -> None:
        self.console.print(f"[bold cyan]? {event.text}[/bold cyan]")
