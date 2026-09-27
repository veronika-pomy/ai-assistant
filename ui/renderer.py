"""Renders core events to the terminal via Rich.

All presentation lives here; :mod:`core` yields plain typed events. 
The Renderer owns the console and the Rich ``Live``
lifecycle used for :class:`~core.events.TokenDelta` streams.
"""

from rich.console import Console
from rich.live import Live
from rich.text import Text

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
    """Dispatches core events onto a Rich console.

    Token streams are batched into a single ``rich.live.Live`` block: the
    first ``TokenDelta`` starts a Live, subsequent deltas update it, and
    the next non-delta event (or ``finish_turn``) tears it down. This is
    critical — a Live must be stopped before ``input()`` runs, or Rich
    and the REPL prompt collide.
    """

    def __init__(self, console: Console):
        self.console = console
        self._live: Live | None = None
        self._live_buffer: str = ""

    def render(self, event: Event) -> None:
        if isinstance(event, TokenDelta):
            self._render_token_delta(event)
            return

        # Any non-delta event ends an in-flight stream first.
        self._stop_live()

        if isinstance(event, StatusEvent):
            self._render_status(event)
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

    def finish_turn(self) -> None:
        """Close any in-flight Live before the REPL prompts for input."""
        self._stop_live()

    def _render_status(self, event: StatusEvent) -> None:
        style = _STATUS_STYLE.get(event.kind, "yellow")
        self.console.print(f"[{style}]{event.text}[/{style}]")

    def _render_token_delta(self, event: TokenDelta) -> None:
        if self._live is None:
            self._live_buffer = ""
            self._live = Live(
                Text.from_markup(""),
                console=self.console,
                refresh_per_second=20,
            )
            self._live.start()
        self._live_buffer += event.text
        self._live.update(Text(self._live_buffer))

    def _stop_live(self) -> None:
        if self._live is not None:
            self._live.stop()
            self._live = None
            self._live_buffer = ""

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
