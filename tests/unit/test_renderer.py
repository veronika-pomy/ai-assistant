"""Tests for the UI renderer's handling of model-derived strings.

The renderer interpolates event fields into Rich markup strings. Any field
that can carry model output must be escaped so bracketed content like
citations (`[1]`), regex classes (`[a-z]+`), or unclosed tags do not
mangle output or raise ``MarkupError``.
"""

import io

import pytest
from rich.console import Console

from core.events import (
    ConfirmRequest,
    QuestionEvent,
    StatusEvent,
    TodoItem,
    TodoUpdate,
    TokenDelta,
)
from ui.formatters import show_error
from ui.renderer import Renderer


def _make_renderer() -> tuple[Renderer, Console]:
    console = Console(file=io.StringIO(), force_terminal=False, record=True)
    return Renderer(console), console


class TestTokenDeltaStreaming:
    """Streaming buffer must render arbitrary model text as literal."""

    @pytest.mark.parametrize(
        "chunks",
        [
            ["Studies show X ", "[1]", " and Y ", "[2]"],
            ["arr[0] = list[int]"],
            ["regex: [a-z]+ matches lowercase"],
            ["broken tag ", "[unclos", "ed and more text"],
            ["["],
            ["]"],
            ["[[nested]]"],
        ],
    )
    def test_bracketed_stream_does_not_raise(self, chunks):
        renderer, _ = _make_renderer()
        for chunk in chunks:
            renderer.render(TokenDelta(text=chunk))
        renderer.finish_turn()

    def test_stream_preserves_literal_brackets(self):
        renderer, console = _make_renderer()
        renderer.render(TokenDelta(text="Cite [1] then [2]."))
        renderer.finish_turn()
        output = console.export_text()
        assert "[1]" in output
        assert "[2]" in output


class TestStatusEventEscaping:
    def test_status_with_brackets_does_not_raise(self):
        renderer, console = _make_renderer()
        renderer.render(StatusEvent(text="Searching for: [regex] and [1]"))
        output = console.export_text()
        assert "[regex]" in output
        assert "[1]" in output

    def test_status_with_unclosed_bracket_does_not_raise(self):
        renderer, _ = _make_renderer()
        renderer.render(StatusEvent(text="value is [unclosed"))


class TestTodoEscaping:
    def test_todo_with_brackets_does_not_raise(self):
        renderer, console = _make_renderer()
        renderer.render(
            TodoUpdate(
                items=[
                    TodoItem(text="Read arr[0] docs"),
                    TodoItem(text="Fix [broken tag", done=True),
                ]
            )
        )
        output = console.export_text()
        assert "arr[0]" in output
        assert "[broken tag" in output


class TestConfirmEscaping:
    def test_confirm_with_brackets_does_not_raise(self):
        renderer, console = _make_renderer()
        renderer.render(
            ConfirmRequest(prompt="Proceed with [expensive] research?", cost_hint="~$0.05 [est]")
        )
        output = console.export_text()
        assert "[expensive]" in output
        assert "[est]" in output


class TestQuestionEscaping:
    def test_question_with_brackets_does_not_raise(self):
        renderer, console = _make_renderer()
        renderer.render(QuestionEvent(text="Did you mean [a] or [b]?"))
        output = console.export_text()
        assert "[a]" in output
        assert "[b]" in output


class TestShowErrorEscaping:
    """Error path must survive exception messages containing brackets."""

    def test_show_error_with_brackets_does_not_raise(self):
        console = Console(file=io.StringIO(), force_terminal=False, record=True)
        show_error(console, "KeyError: '[missing]' in config[0]")
        output = console.export_text()
        assert "[missing]" in output
        assert "config[0]" in output

    def test_show_error_with_unclosed_bracket_does_not_raise(self):
        console = Console(file=io.StringIO(), force_terminal=False, record=True)
        show_error(console, "parse error near [unterminated")
