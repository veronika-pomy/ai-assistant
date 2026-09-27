"""Shared context for tools invoked during an orchestrator run."""

from dataclasses import dataclass


@dataclass
class AppContext:
    """Handed to Runner.run_streamed via context= and reached by tools
    through RunContextWrapper[AppContext].

    Empty for now; T2.3 will add todo_queue and confirm callback.
    """
    pass
