# Target Architecture

One page. The goal: **very simple, but modularized and extendable via abstractions** — swap points are env flags + factories, not frameworks.

## Shape after the backlog lands

```
┌─────────────────────────── app.py (thin REPL) ───────────────────────────┐
│  startup: settings → provider setup → MCP servers (ExitStack) → chat menu│
│  loop:    prompt → orchestrator_runner.run() → renderer(event)           │
└───────────────────────────────────────────────────────────────────────────┘
                 │ yields typed events                ▲ ConfirmRequest bridge
                 ▼                                    │
┌──────────────────────────── core/ ────────────────────────────────────────┐
│ events.py            pydantic event vocabulary (core→UI contract)        │
│ orchestrator_runner  wraps Runner.run_streamed(orchestrator, session=…)  │
│ session.py           SQLiteSession(chat_id, data/sessions.db) + chats DB │
│ mcp.py               MCPServerStdio builders (fetch, playwright)         │
└───────────────────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────── custom_agents/ ───────────────────────────────────┐
│ orchestrator.py — Agent with tools:                                       │
│   solver.as_tool()      quick answers                                    │
│   planner.as_tool()     produce a SearchPlan                             │
│   get_search_tool()     ONE web search (simple path, no pipeline)        │
│   run_research()        @function_tool: gate → parallel searchers → writer│
│   set_todos()/mark_done()  progress reporting                            │
│   + mcp_servers=[fetch, playwright]                                       │
└───────────────────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌── tools/ ────────────────────────────┐  ┌── ui/ ─────────────────────────┐
│ base.py     BaseTool ABC (seam)      │  │ renderer.py  event → console   │
│ web_search  hosted WebSearchTool     │  │ prompts.py   input, chat menu  │
│ tavily      Tavily function tool     │  │ banner, formatters             │
│ __init__    get_search_tool(settings)│  └────────────────────────────────┘
│ telegram    notify tool              │
└──────────────────────────────────────┘
```

## Key principles

1. **Events are the only core→UI contract.** Core never emits Rich markup; UI never parses strings. Adding a display (trace, todo panel) = new event type + renderer case.
2. **LLM does the routing.** No keyword classification. The orchestrator picks tools; "simple vs complex search" is just "call `web_search` vs `run_research`". Nesting comes from `agent.as_tool()`, traces come from the SDK's stream events.
3. **Provider switching is env + factory.** `SEARCH_PROVIDER` (openai|tavily) via `get_search_tool()`; `MODEL_PROVIDER` (openai|openrouter) via startup client config. Hard rule: OpenRouter requires Tavily (hosted search runs on OpenAI servers only).
4. **Feature flags for optional integrations.** MCP servers and Telegram are off by default (`MCP_FETCH_ENABLED`, `MCP_PLAYWRIGHT_ENABLED`, token presence). The app must run with none of them configured.
5. **Sessions: one writer.** Only the orchestrator run gets `session=`. Parallel sub-runs (searchers) are session-less to avoid interleaved history in SQLite.
6. **Minimal testing (discovery level).** Unit tests for pure logic (event yielding, factories, chat metadata CRUD) with `Runner` stubbed. Live-API testing is manual (`python app.py`). No mocking pyramid.

## Invariants to protect

- `app.py` stays under ~80 lines: wiring only.
- Adding a new agent = new factory in `custom_agents/` + one `as_tool()` line in the orchestrator.
- Adding a new tool provider = subclass `BaseTool` + one branch in its factory.
- Nothing in `core/` or `custom_agents/` imports from `ui/`.
