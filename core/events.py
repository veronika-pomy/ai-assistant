"""Event types yielded by core workflows to the UI layer.

Core code yields these typed events; the
:class:`ui.renderer.Renderer` decides how to render them for the terminal.
"""

from typing import Literal, Union
from pydantic import BaseModel, Field


class StatusEvent(BaseModel):
    """Progress / status update for the user."""
    text: str
    kind: Literal["info", "step", "trace"] = "info"


class TokenDelta(BaseModel):
    """Incremental token streamed from a running agent."""
    text: str


class ReportEvent(BaseModel):
    """A finished markdown document to be rendered as markdown."""
    markdown: str


class TodoItem(BaseModel):
    """One item in a TodoUpdate list."""
    text: str
    done: bool = False


class TodoUpdate(BaseModel):
    """Snapshot of the current TODO list state."""
    items: list[TodoItem] = Field(default_factory=list)


class ConfirmRequest(BaseModel):
    """Ask the user to confirm an action before proceeding."""
    prompt: str
    cost_hint: str | None = None


class QuestionEvent(BaseModel):
    """Free-form question posed to the user."""
    text: str


Event = Union[
    StatusEvent,
    TokenDelta,
    ReportEvent,
    TodoUpdate,
    ConfirmRequest,
    QuestionEvent,
]
