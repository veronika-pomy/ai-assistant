# Nelle Development Backlog

Backlog for the 16 "nice to have" items, grouped into 6 epics. Each ticket has a user story, acceptance criteria, size (S/M/L), and dependencies. Technical detail lives in the per-epic spec files under [specs/](specs/). Deferred work lives in [roadmap.md](roadmap.md). Target architecture is in [architecture.md](architecture.md).

**Personas:**
- **Developer** — the person maintaining and extending this app.
- **User** — the person chatting with Nelle in the terminal.

## Ticket index & build order

| ID | Title | Size | Deps | Spec |
|----|-------|------|------|------|
| T1.4 | Config consolidation | S | — | [E1](specs/E1-foundation.md) |
| T1.1 | Event-based core/UI split | M | — | [E1](specs/E1-foundation.md) |
| T1.2 | Pydantic output app-wide | S | T1.1 | [E1](specs/E1-foundation.md) |
| T1.3 | Token streaming | M | T1.1 | [E1](specs/E1-foundation.md) |
| T2.1 | LLM orchestrator with agents-as-tools | L | T1.1, T1.4 | [E2](specs/E2-orchestrator.md) |
| T2.2 | Turn-by-turn trace display | M | T2.1, T1.3 | [E2](specs/E2-orchestrator.md) |
| T2.3 | Live todo display + confirm gate | M | T2.1 | [E2](specs/E2-orchestrator.md) |
| T2.4 | Clarification questions | S | T2.1 | [E2](specs/E2-orchestrator.md) |
| T3.1 | Tavily search provider flag | M | T2.1 | [E3](specs/E3-providers.md) |
| T3.2 | OpenRouter model provider flag | M | T3.1 | [E3](specs/E3-providers.md) |
| T4.1 | fetch MCP server | S | T2.1 | [E4](specs/E4-mcp.md) |
| T4.2 | Playwright MCP with domain blocking | M | T4.1 | [E4](specs/E4-mcp.md) |
| T5.1 | Persistent sessions + chat IDs | M | T1.1 | [E5](specs/E5-memory.md) |
| T5.2 | Recents menu + chat browser | M | T5.1 | [E5](specs/E5-memory.md) |
| T6.1 | Telegram notification tool | S | T2.1 | [E6](specs/E6-notifications-and-spikes.md) |

**Build order:** T1.4 → T1.1 → T1.2 → T1.3 → T2.1 → T2.2 → T2.3 → T2.4 → T3.1 → T3.2 → T4.1 → T4.2 → T5.1 → T5.2 → T6.1
E5 (memory) has no dependency on E2–E4 beyond T1.1 and can run in parallel with them.

**Mapping from the original nice-to-have list:** #1→T2.4, #2→T2.1, #3→T4.1+T4.2, #4→T2.3 (v1) + roadmap (interactive v2), #5→T1.1+T1.2, #6→T1.3, #7→T5.1+T5.2, #8→T1.1, #9→T2.1, #10→T6.1, #11→T3.1, #12→T3.2, #13→T2.2, #14→T2.1, #15→T2.1

---

## Epic 1 — Foundation

Cleans up the core/UI boundary so every later feature has a place to plug in.

### T1.4 Config consolidation (S)
**As a developer**, I want all model/config reads to go through one place, so that provider switching (E3) has a single seam.
- [ ] `MODEL_NAME` is read in exactly one module; the four per-agent `os.getenv` duplicates are gone.
- [ ] Unused settings (`how_many_searches`, `session_type`) are either wired up or deleted.
- [ ] Existing config tests pass and cover the new helper.

### T1.1 Event-based core/UI split (M)
**As a developer**, I want core orchestration to yield typed events instead of Rich-markup strings, so that UI logic lives only in `ui/` and new displays (todos, traces, streams) are additive.
- [ ] Core modules contain no Rich markup; `app.py` no longer sniffs strings for `##`.
- [ ] A pydantic event vocabulary exists (`StatusEvent`, `TokenDelta`, `ReportEvent`, `TodoUpdate`, `ConfirmRequest`, `QuestionEvent`).
- [ ] A single renderer maps events to console output; app.py shrinks to a thin loop.
- [ ] Unit test asserts event types yielded from a stubbed run (no live API).

### T1.2 Pydantic output app-wide (S)
**As a developer**, I want every agent boundary and core→UI message to be a pydantic model, so that parsing is validated instead of string-matched.
- [ ] Searcher output has a typed summary model; solver keeps free text unless a model adds value.
- [ ] No `str.startswith`/keyword parsing remains between components.

### T1.3 Token streaming (M)
**As a user**, I want answers to appear as they're generated, so that long responses don't sit behind a blank wait.
- [ ] Final answers stream token-by-token via `Runner.run_streamed()`.
- [ ] The dead `core/streaming.py` module is folded into the renderer and deleted.
- [ ] Unit test: fake event stream → deltas rendered in order.

---

## Epic 2 — LLM Orchestrator (centerpiece)

Replaces keyword routing with an LLM agent that owns routing, delegation, and progress reporting.

### T2.1 LLM orchestrator with agents-as-tools (L)
**As a user**, I want Nelle to decide for itself whether my question needs a quick answer, a single search, or full research, so that I don't have to phrase queries with magic keywords.
**As a developer**, I want agents wired via `agent.as_tool()`, so that nesting and delegation come from the SDK instead of hand-written pipelines.
- [ ] Keyword classification (`_analyze_task_type`) is removed; an orchestrator agent routes via tool selection.
- [ ] Planner, solver, and a `run_research` pipeline tool are exposed as tools; a direct web-search tool covers simple lookups (no full research pipeline).
- [ ] Parallel 5-site research still runs concurrently (session-less sub-runs).
- [ ] Simple question → no research tools called; "research X" → full pipeline; verified manually with the e2e script.

### T2.2 Turn-by-turn trace display (M)
**As a user**, I want to see which agent/tool the orchestrator is invoking each turn, so that I can follow what it's doing.
- [ ] Tool-call and agent-switch stream events render as an indented trace ("→ calling plan_research(...)").
- [ ] Traces are visually distinct from the final answer.

### T2.3 Live todo display + confirm gate (M)
**As a user**, I want a running todo list during complex tasks and a yes/no confirmation before expensive research starts, so that I can see progress and veto costly work.
- [ ] Orchestrator maintains todos via `set_todos`/`mark_done` tools; renderer shows a live-updating panel for multi-step tasks only.
- [ ] Research (5-site) asks for confirmation before running; declining cancels cleanly with a message.
- [ ] No mid-run pause/edit — that is [roadmap](roadmap.md) scope.

### T2.4 Clarification questions (S)
**As a user**, I want Nelle to ask me a clarifying question when my request is ambiguous, so that I get relevant answers instead of guesses.
- [ ] The "never ask questions" instruction is removed; agents are told to ask one question when genuinely ambiguous.
- [ ] Answering the question in the next REPL turn continues the task (session history carries context).

---

## Epic 3 — Provider flags

### T3.1 Tavily search provider flag (M)
**As a developer**, I want `SEARCH_PROVIDER=openai|tavily` to switch the search backend, so that search survives moving off OpenAI-hosted tools. **Prerequisite for T3.2.**
- [ ] A `get_search_tool(settings)` factory returns the hosted tool or a Tavily function tool based on env.
- [ ] `max_results` actually takes effect (currently a dead parameter).
- [ ] Unit test: factory returns the right tool per env value.

### T3.2 OpenRouter model provider flag (M)
**As a developer**, I want `MODEL_PROVIDER=openai|openrouter` to switch the LLM backend, so that I can experiment with non-OpenAI models.
- [ ] OpenRouter mode configures the SDK client at startup (base_url, chat-completions API, tracing off).
- [ ] Startup fails fast with a clear error if OpenRouter is selected while `SEARCH_PROVIDER=openai` (hosted search only works on OpenAI).
- [ ] Known caveat documented: some OpenRouter models lack `json_schema` support for pydantic outputs.

---

## Epic 4 — MCP

### T4.1 fetch MCP server (S)
**As a user**, I want Nelle to fetch and parse live web pages (e.g. "what's the top book PRH is promoting today?"), so that answers can use page content, not just search snippets.
- [ ] fetch MCP server (local, stdio via npx) is attached to the orchestrator behind `MCP_FETCH_ENABLED` (default off).
- [ ] Server lifecycle is managed for the whole REPL session (started once, cleaned up on exit).

### T4.2 Playwright MCP with domain blocking (M)
**As a user**, I want Nelle to take screenshots of websites, except blocked domains, so that I can capture pages while respecting off-limits sites.
- [ ] Playwright MCP runs locally (npx, local browser — confirmed: no remote service) behind `MCP_PLAYWRIGHT_ENABLED`.
- [ ] `BLOCKED_ORIGINS` env setting is passed via `--blocked-origins`; a blocked domain request fails visibly.

---

## Epic 5 — Persistent memory

### T5.1 Persistent sessions + chat IDs (M)
**As a user**, I want conversations saved across restarts under chat IDs, so that I can pick up where I left off.
- [ ] Sessions persist to a SQLite file (replacing the hardcoded `:memory:`); each chat has an id, title, and updated-at.
- [ ] `SessionManager.clear()` works.
- [ ] Unit test: tmp-path DB round-trip of chat metadata.

### T5.2 Recents menu + chat browser (M)
**As a user**, I want a startup menu with my 5 most recent chats and a way to browse all of them, so that I can jump back into any conversation.
- [ ] Startup offers: new chat / 5 recents / browse all (paginated console list).
- [ ] A `/chats` command switches chats mid-session.

---

## Epic 6 — Bottom of backlog

### T6.1 Telegram notification tool (S)
**As a user**, I want Nelle to send me a Telegram message when a search/research finishes — but only when I explicitly ask, so that I'm not spammed.
- [ ] A `notify_telegram` tool posts to the Bot API; instructions restrict it to explicit user requests.
- [ ] Missing `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` produces a clear error, not a crash.
