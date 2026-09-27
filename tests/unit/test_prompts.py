"""Tests for the REPL prompt module.

The ``ui.prompts`` module imports :mod:`readline` for its side effect —
hooking line editing (arrow keys, in-session history, ctrl-a/e/w/u)
into Python's built-in ``input()``.
"""

import io
import sys

import pytest
from rich.console import Console

from ui.prompts import is_exit_command, prompt_user


class TestReadlineHooked:
    def test_readline_is_loaded_after_importing_prompts(self):
        """Importing ui.prompts must leave readline in sys.modules."""
        assert "readline" in sys.modules

    def test_readline_is_gnu_on_darwin(self):
        """On macOS, gnureadline must have replaced libedit so that
        input() enforces the prompt as a left-edit boundary."""
        if sys.platform != "darwin":
            pytest.skip("Only relevant on macOS.")
        import readline

        doc = readline.__doc__ or ""
        assert "libedit" not in doc, (
            "readline is using libedit; install gnureadline "
            "(in requirements.txt) so input() enforces the prompt boundary."
        )


class TestIsExitCommand:
    def test_exit_returns_true(self):
        assert is_exit_command("exit") is True

    def test_quit_returns_true(self):
        assert is_exit_command("quit") is True

    def test_case_insensitive(self):
        assert is_exit_command("EXIT") is True
        assert is_exit_command("Quit") is True

    def test_whitespace_trimmed(self):
        assert is_exit_command("  exit  ") is True

    def test_non_exit_returns_false(self):
        assert is_exit_command("hello") is False
        assert is_exit_command("") is False


class TestPromptBoundary:
    """The prompt handed to input() must be plain ASCII so readline
    treats it as an immovable left-edit boundary. Rich handles the
    styled portion via a separate print so its ANSI escape bytes never
    reach readline's cursor bookkeeping."""

    def test_input_called_with_plain_ascii_prompt(self, monkeypatch):
        captured: dict = {}

        def fake_input(*args, **kwargs):
            captured["args"] = args
            captured["kwargs"] = kwargs
            return "hi"

        monkeypatch.setattr("builtins.input", fake_input)
        console = Console(file=io.StringIO(), force_terminal=False, record=True)

        result = prompt_user(console)

        assert result == "hi"
        assert captured["args"] == (">> ",)
        assert captured["kwargs"] == {}
        # No ANSI escape bytes in the prompt readline sees.
        assert "\x1b" not in captured["args"][0]

    def test_prompt_is_printed_before_input(self, monkeypatch):
        events: list[str] = []

        def fake_input(*args, **kwargs):
            events.append("input")
            return ""

        monkeypatch.setattr("builtins.input", fake_input)

        class RecordingConsole(Console):
            def print(self_inner, *args, **kwargs):
                events.append("print")

        console = RecordingConsole(file=io.StringIO(), force_terminal=False)
        prompt_user(console, first=True)

        assert events.index("input") == len(events) - 1
        assert "print" in events[: events.index("input")]
