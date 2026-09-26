# Future Roadmap

Items deliberately **not** in the current backlog. Kept here so they stay on the map.

## Interactive task control (todo v2)

The current backlog ships todo **display** + a **confirm-before-research gate** (T2.3). The full Claude-Code-style experience — pause a running task, edit/reorder todos mid-run, per-action allow/deny prompts — is deferred because a plain-terminal REPL can't cleanly handle keyboard input while agents are running. Revisit when the app gets a proper UI, one of:

- a full-screen TUI (e.g. Textual) with an input widget alongside a live task panel, or
- a local web UI over the same event stream (the T1.1 event contract is designed to survive this move unchanged).

Scope when picked up: pause/resume orchestrator runs, todo editing, allow/deny gates per tool call (generalizing the T2.3 confirm callback into a permission layer).

## Per-sub-agent token streaming

`agent.as_tool()` sub-runs don't stream through the parent run, so v1 traces (T2.2) show orchestrator-level tool calls only. Streaming tokens from nested searcher/writer runs would need custom function tools that run `Runner.run_streamed` internally and forward deltas onto the event queue. Nice depth-of-visibility win; not worth the plumbing until the trace display proves useful.

## Other parked ideas

- Cost/token usage display per run (SDK exposes usage on run results).
- Exposing `run_research` / web search as an MCP server so other clients can use Nelle's research pipeline (inverse of E4).
- Model-per-agent tuning (cheap model for searchers, strong model for orchestrator/writer) once OpenRouter (T3.2) makes model experimentation cheap.
