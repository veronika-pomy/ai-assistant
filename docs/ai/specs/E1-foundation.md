# E1 — Foundation Spec

Cleans the core/UI boundary. Everything in E2+ assumes these seams exist.

## T1.4 Config consolidation

**Problem:** each agent file duplicates `os.getenv("MODEL_NAME", "gpt-5.4-mini")`; `settings.how_many_searches` and `settings.session_type` are defined but never read.

**Approach:**
- Add a `get_model_name()` helper (in `config/settings.py` or a tiny `custom_agents/model.py`) that all agent factories use.
- Wire `how_many_searches` into the planner's instructions/schema (currently hardcoded to exactly 5 in the `SearchPlan` pydantic model) — or delete it. Prefer wiring; the confirm gate (T2.3) wants to say "run N-site research?".
- `session_type` gets consumed by T5.1; leave a TODO pointing there or delete and reintroduce.

**Files:** `config/settings.py`, `custom_agents/{planner,searcher,solver,writer}.py`.
**Test:** extend `tests/unit/test_config.py`.

## T1.1 Event-based core/UI split

**Problem:** `core/task_manager.py` yields Rich-markup strings (`"[yellow]Searching...[/yellow]"`); `app.py:47` decides rendering by sniffing for a leading `##`. Presentation is baked into orchestration.

**Approach:**
- New `core/events.py` with pydantic models:
  ```python
  StatusEvent(text: str, kind: Literal["info", "step", "trace"] = "info")
  TokenDelta(text: str)
  ReportEvent(markdown: str)
  TodoUpdate(items: list[TodoItem])        # TodoItem: text, done
  ConfirmRequest(prompt: str, cost_hint: str | None)
  QuestionEvent(text: str)
  ```
- Core generators yield these events (union type `Event`). All Rich markup deleted from `core/`.
- New `ui/renderer.py`: `class Renderer` with `render(event)` dispatching on type. It owns the console and (after T1.3) the Rich `Live` lifecycle. `app.py` becomes: prompt → `async for event in runner.run(...)` → `renderer.render(event)`.

**Files:** new `core/events.py`, new `ui/renderer.py`; edit `core/task_manager.py` (until T2.1 replaces it), `app.py`, `ui/formatters.py`.
**Test:** stub the workflow (no `Runner` call), assert the yielded event types/sequence.

## T1.2 Pydantic app-wide

- Searcher gets `output_type=SearchSummary` (e.g. `query`, `summary: str` capped ~300 words via instructions) — this also mitigates orchestrator context bloat later (E2 risk #2).
- Solver stays free-text (it *is* the answer); events from T1.1 already cover core→UI parsing.

**Files:** `custom_agents/searcher.py`, `core/task_manager.py` (consume the model).
**Test:** model round-trip; searcher factory smoke test.

## T1.3 Token streaming

**Problem:** final answers arrive via blocking `Runner.run()`. `core/streaming.py` (`StreamingUI`) already implements delta filtering + Rich `Live` but is dead code.

**Approach:**
- In workflows, replace terminal `Runner.run(...)` with `Runner.run_streamed(...)`; iterate `result.stream_events()`, map `raw_response_event` / `ResponseTextDeltaEvent` → `TokenDelta`.
- Move the Live-display logic from `core/streaming.py` into `ui/renderer.py` (`TokenDelta` handling: start Live on first delta, stop on next non-delta event). Delete `core/streaming.py` and its import test.
- Structured-output runs (planner/writer) don't stream usefully; keep those blocking, emit `StatusEvent`s around them.

**Gotcha:** the renderer must stop any active `Live` before the REPL prompts for input (or a confirm gate) — Rich `Live` and `input()` collide.

**Files:** `core/task_manager.py` (then `core/orchestrator_runner.py` after T2.1), `ui/renderer.py`, delete `core/streaming.py`.
**Test:** feed a fake event stream, assert `TokenDelta`s forwarded in order.
