---
name: comment-style
description: Comment and docstring style for this repo — short, human, only when the code alone isn't enough
---

# Comment style

Write comments and docstrings like a person left a note, not a compliance document.

## Principles

1. **Assume the dev will read the code.** Don't try to save them from it. A comment's job is to add the piece the code can't show, not to summarise what the code plainly says.
2. **Default: no comment.** Add one only when removing it would confuse a reader who's looking at the code cold.
3. **Say why, not what.** The code shows the what. Comments earn their space by explaining a non-obvious constraint, gotcha, or reason.
4. **Short.** One line where possible. If a docstring needs a paragraph, the function probably needs a rethink.

## Rules

- **No historical narration.** Don't write "replaces X", "was previously", "we used to". That belongs in `git log` and the commit message.
- **Future narration is OK, but must be cleaned up.** Writing "T2.2 will map trace events" is fine while T2.2 is a real upcoming ticket. When you start work on TX.Y, grep the repo for `TX.Y` (or the phrase) and delete/update any stale references before you commit. If you can't commit to that cleanup, don't write the future note.
- **Don't restate the signature.** Type hints already document types. Skip `Args:` / `Returns:` blocks when they'd only repeat what the signature already shows. Keep them when they say something extra (e.g. "falls back to MODEL_NAME env").
- **Module docstrings: one line, or omit.** The filename and its exports usually tell the story.
- **Skip narration between statements.** `# Load settings` above `settings = get_settings()` is noise.

## When to comment

- A hidden constraint or invariant a reader can't see (`# session-less on purpose — concurrent SQLiteSession writes race`).
- A subtle workaround or bug fix that would look wrong without context.
- Behavior that would genuinely surprise someone reading it cold.
- A parameter's behavior that isn't captured in its type (env fallback, side-effect trigger, etc.).

## Examples

**Bad — verbose, references history, restates the code:**

```python
"""Streams the orchestrator's run as typed :class:`core.events.Event`s.

Thin wrapper around ``Runner.run_streamed``: only text deltas are
surfaced right now. T2.2 will map tool-call and agent-switch events onto
``StatusEvent(kind="trace")`` for the trace display.
"""
```

**Good — one line for the module, keep the future note only if you'll clean it up:**

```python
"""Runs the orchestrator and yields UI events."""
# T2.2 will add trace events here.  ← only if you'll delete this line during T2.2
```

**Bad — factory boilerplate that restates the name:**

```python
def create_solver_agent(model: str = None) -> Agent:
    """Factory function to create solver agent for direct problem-solving.

    Args:
        model: Model name override (uses MODEL_NAME env var if not specified)

    Returns:
        Agent instance configured for direct problem-solving
    """
```

**Good — kill the restated name, keep the env-fallback fact because it isn't in the signature:**

```python
def create_solver_agent(model: str | None = None) -> Agent:
    """Direct-answer agent. Model falls back to MODEL_NAME env."""
```

**Bad — comment restates the code:**

```python
# Initialize task manager with settings.
self.settings = get_settings()
```

**Good — delete it:**

```python
self.settings = get_settings()
```

**Good — comment earns its space:**

```python
# session-less on purpose: concurrent SQLiteSession writes race.
summaries = await asyncio.gather(*(Runner.run(searcher, q) for q in queries))
```

## Apply when

- Writing new code in this repo.
- Editing a file: clean up the comments/docstrings you touch as you go.
- Starting work on a ticket: grep for the ticket ID across the repo and prune stale future-narration references.
- Reviewing: flag anything that violates the rules above.
