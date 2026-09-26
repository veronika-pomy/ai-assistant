# E3 — Provider Flags Spec

Two env-driven switches: search backend and model backend. **Order matters: T3.1 before T3.2** — the hosted `WebSearchTool` executes on OpenAI's servers (Responses API) and hard-fails on any other provider.

## T3.1 Tavily search provider flag

**Approach:**
- New `tools/tavily_search.py` implementing the existing `BaseTool` ABC (`tools/base.py:5` — the seam already exists, with a swap hint comment at `web_search.py:51`):
  ```python
  @function_tool
  async def tavily_search(query: str) -> str:
      # tavily-python AsyncTavilyClient.search(query, max_results=settings.max_results)
      # return concatenated title+content snippets
  ```
- New factory `tools/__init__.py::get_search_tool(settings)` switching on `settings.search_provider` (`SEARCH_PROVIDER=openai|tavily`, default `openai`). Searcher (`custom_agents/searcher.py:44`) and the orchestrator take the tool from this factory only.
- Fix the dead `max_results` param in `tools/web_search.py` (accepted but never passed to `WebSearchTool`) — pass it through or drop it; Tavily honors it either way.
- New env: `SEARCH_PROVIDER`, `TAVILY_API_KEY`. New dep: `tavily-python`.

**Note:** `tool_choice="required"` on the searcher works the same with a function tool as with the hosted tool.

**Test:** factory returns the correct tool class per env value; Tavily call itself mocked (no live key in tests).

## T3.2 OpenRouter model provider flag

**Approach:**
- Settings additions: `model_provider` (`MODEL_PROVIDER=openai|openrouter`), `openrouter_api_key`.
- At startup in `app.py` (before any agent is built), if provider is openrouter:
  ```python
  set_default_openai_client(AsyncOpenAI(
      base_url="https://openrouter.ai/api/v1",
      api_key=settings.openrouter_api_key))
  set_default_openai_api("chat_completions")   # OpenRouter has no Responses API
  set_tracing_disabled(True)                   # traces need an OpenAI key
  ```
- **Guard (fail fast):** if `MODEL_PROVIDER=openrouter` and `SEARCH_PROVIDER=openai`, exit with: "Hosted OpenAI web search is unavailable on OpenRouter — set SEARCH_PROVIDER=tavily."
- `MODEL_NAME` then takes OpenRouter model ids (e.g. `anthropic/claude-sonnet-5`); document in `.env.example`.

**Caveats to document:**
- Some OpenRouter models don't support `json_schema` structured outputs → planner/writer `output_type` may fail; note per-model.
- Hosted tools of any kind (web search, code interpreter) are unavailable off-OpenAI.

**Test:** settings-validation unit test (guard triggers on the bad combo); no live calls.
