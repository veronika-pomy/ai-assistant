# E4 — MCP Spec

Attach local MCP servers to the orchestrator for page fetching and screenshots. Both run **locally** as stdio subprocesses launched via npx — no remote service involved (this was an open question: confirmed, Playwright MCP drives a local browser).

## T4.1 fetch MCP

**Approach:**
- New `core/mcp.py`:
  ```python
  def build_mcp_servers(settings) -> list[MCPServerStdio]:
      servers = []
      if settings.mcp_fetch_enabled:
          servers.append(MCPServerStdio(
              params={"command": "npx", "args": ["-y", "@modelcontextprotocol/server-fetch"]},
              cache_tools_list=True))
      ...
  ```
  (If the npx package proves flaky, the reference fetch server also ships as Python: `uvx mcp-server-fetch` — pick whichever runs cleanly.)
- `app.py` enters all servers once at startup via `contextlib.AsyncExitStack` wrapped around the REPL loop (MCP stdio servers need `async with` lifecycle; per-query startup would add npx cold-start latency to every turn).
- Pass `mcp_servers=build_mcp_servers(settings)` to the orchestrator `Agent`. Orchestrator instructions: use fetch when the user asks about a specific page/site's current content (the "top book PRH is promoting today" case: search → find URL → fetch → parse).
- Flag: `MCP_FETCH_ENABLED` (default false). App must run fine with it off.

**Test:** flag test (`build_mcp_servers` returns [] when disabled); everything else is manual — add a fetch case to the e2e script.

## T4.2 Playwright MCP with domain blocking

**Approach:**
- In `build_mcp_servers`, when `settings.mcp_playwright_enabled`:
  ```python
  args = ["-y", "@playwright/mcp@latest"]
  if settings.blocked_origins:                 # BLOCKED_ORIGINS=example-corp.com;intranet.local
      args += ["--blocked-origins", settings.blocked_origins]
  ```
  Domain exclusion is thus **config, not custom code** — the server refuses navigation to blocked origins itself. Consider `--isolated` (no persistent browser profile) and `--caps` to trim the tool list to navigation+screenshot if the full toolset distracts the orchestrator.
- Screenshots land as files; orchestrator should report the saved path via a `StatusEvent`/final answer. Set `--output-dir` to a project-local `data/screenshots/`.
- Flag: `MCP_PLAYWRIGHT_ENABLED` (default false). Env: `BLOCKED_ORIGINS`.

**Gotchas:**
- First run downloads a browser (`npx playwright install chromium` may be needed) — document in README/.env.example.
- npx cold start is seconds; `cache_tools_list=True` avoids repeated tool-list round-trips.
- Two MCP servers + agent tools = a big tool menu; keep tool descriptions sharp so routing stays accurate.

**Test:** flag/arg-construction unit test (blocked origins appear in args); manual e2e: screenshot an allowed site, verify a blocked domain is refused.
