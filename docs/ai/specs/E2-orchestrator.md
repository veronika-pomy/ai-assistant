# E2 — LLM Orchestrator Spec

Replaces keyword routing (`task_manager.py:_analyze_task_type`, pure keyword lists) with an LLM agent that routes by choosing tools. Delivers nested agent calling, LLM orchestration, turn traces, simple-vs-complex search, todo display, confirm gate, and clarification questions.

## T2.1 Orchestrator agent

**Approach:**
- New `custom_agents/orchestrator.py`:
  ```python
  orchestrator = Agent(
      name="orchestrator",
      instructions=ROUTING_POLICY,   # answer directly | one search | plan | full research
      tools=[
          solver.as_tool(tool_name="answer", tool_description="..."),
          planner.as_tool(tool_name="plan_research", tool_description="..."),
          get_search_tool(),          # ONE web search — the "simple search" path
          run_research,               # @function_tool — the full pipeline
          set_todos, mark_done,       # T2.3
      ],
      mcp_servers=mcp_servers,        # E4
  )
  ```
- `run_research(ctx, queries: list[str])` is a `@function_tool` (not agent-as-tool) so we keep control:
  1. await the confirm gate (T2.3),
  2. `asyncio.gather` **session-less** `Runner.run(searcher, q)` calls — preserves today's parallelism, which a naive as-tool loop would serialize, and avoids concurrent SQLiteSession writes,
  3. run writer over the summaries, return the report markdown.
- New `core/orchestrator_runner.py` replacing `TaskManager`: `run(user_input, session) -> AsyncIterator[Event]` wrapping `Runner.run_streamed(orchestrator, user_input, session=session, max_turns=15)`. Only this top-level run gets `session=`.
- Delete `core/task_manager.py` and its keyword-classification tests; the routing policy now lives in instructions, exercised manually via `python app.py`.

**Routing policy sketch (instructions):** answer simple/conversational queries yourself or via `answer`; use `web_search` for a single factual lookup; use `plan_research` when the user wants a plan; use `run_research` only for genuinely deep questions — and set todos first for any multi-step task.

**Model choice:** orchestrator should use the strongest configured model (routing quality matters); sub-agents keep `MODEL_NAME`. Per-agent model tuning is roadmap scope.

**Risks:**
- *Context bloat:* 5 search summaries + report flow through the orchestrator's context — capped by `SearchSummary` (T1.2) length limits.
- *`tool_choice="required"` on searcher:* SDK auto-resets tool_choice after the first call; also pass `max_turns` to nested runs.
- *as_tool sub-runs don't stream:* accepted for v1; see roadmap.

**Test:** assert tool wiring (`[t.name for t in orchestrator.tools]`); monkeypatch `Runner.run_streamed` with canned events and assert `orchestrator_runner` yields expected event types. Manual smoke via `python app.py`: one simple query, one research query.

## T2.2 Turn-by-turn trace display

Map SDK stream events in `orchestrator_runner`:
- `run_item_stream_event` with `tool_call_item` → `StatusEvent("→ plan_research({...})", kind="trace")`
- `tool_call_output_item` → `StatusEvent("← plan_research done", kind="trace")`
- `agent_updated_stream_event` → `StatusEvent("agent: searcher", kind="trace")`

Renderer prints `kind="trace"` dim/indented. This is the "task manager turn printed in traces" feature — every orchestrator decision becomes visible.

**Test:** canned stream → expected StatusEvents.

## T2.3 Live todo panel + confirm gate

**Todos:** `@function_tool set_todos(ctx: RunContextWrapper[AppContext], items: list[str])` and `mark_done(ctx, index: int)`. `AppContext` (a small dataclass passed as `Runner.run_streamed(..., context=app_ctx)`) holds an `asyncio.Queue[Event]`; the tools push `TodoUpdate` onto it. `orchestrator_runner` merges the queue with the SDK stream (e.g. `asyncio.wait` on both) so todo updates interleave with run events. Renderer redraws a Rich todo panel on each `TodoUpdate`.

**Confirm gate:** `AppContext.confirm: Callable[[str], Awaitable[bool]]`, injected by app.py. `run_research` awaits `ctx.context.confirm(f"Run {n}-site research?")` before doing anything. Implementation: the runner yields `ConfirmRequest` and awaits an `asyncio.Future`; the renderer/REPL prompts y/n (stopping any Live display first) and resolves the future. Declining → `run_research` returns "cancelled by user" so the orchestrator can respond gracefully.

**Why a callback, not generator `asend()`:** async-generator two-way communication is fragile; a Future bridge keeps the runner a plain one-way event stream.

**Test:** fake context — assert queue receives `TodoUpdate`s; assert declining confirm short-circuits `run_research`.

## T2.4 Clarification questions

- Delete the prohibition in `custom_agents/solver.py:14`; add to solver + orchestrator instructions: "If the request is genuinely ambiguous, ask ONE clarifying question instead of guessing."
- No new mechanics: a final output that is a question just ends the turn; because the orchestrator run carries `session=`, the user's next REPL input continues with full context.
- Optionally yield `QuestionEvent` when the final output ends with `?` (heuristic is fine at this maturity) so the renderer can style it.

**Test:** none beyond an instructions snapshot; verify manually ("compare them" with no antecedent → expect a question).
