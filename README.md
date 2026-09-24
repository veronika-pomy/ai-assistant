# Nelle - Agent Assistant

An autonomous agent built with the OpenAI Agents SDK. Nelle breaks down problems into checklists, executes each step, and reports progress with live-streamed styled terminal output.

![Nelle Helpful Assistant](demo.png)

---

**📘 For AI Agents/Assistants**: Please read [CLAUDE.md](CLAUDE.md) for critical virtual environment setup and Python command usage instructions.

## Features

- **Interactive Terminal UI**: Styled ASCII art and Rich live-rendered console output
- **Multi-Agent Orchestration**: Specialized agents (Solver, Planner, Searcher, Writer) execute workflows autonomously
- **Intent-Based Routing**: Keyword analysis automatically routes queries to optimal workflows (research, planning, creative, direct)
- **Parallel Web Search**: Research tasks execute multiple searches concurrently for speed
- **Conversational Memory**: In-memory session persistence maintains context across multiple tasks
- **Live Streaming Output**: Real-time Rich markup rendering as agents work
- **Synthesis & Reporting**: Automated report generation from research results

## Tech Stack

**Core Dependencies:**
- **Python 3.10+**
- **OpenAI Agents SDK** (`openai-agents==0.22.0`) - Agentic framework with built-in tool-calling loop, session management, and streaming
- **OpenAI API** (`openai>=1.0.0`) - Model access
- **Rich** (`rich>=13.0.0`) - Terminal formatting with live rendering
- **python-dotenv** (`python-dotenv>=1.0.0`) - Environment variable management

## Setup

1. **Create a virtual environment:**
   ```sh
   python3 -m venv .venv
   ```

2. **Activate the virtual environment:**
   ```sh
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_api_key_here
   MODEL_NAME=model-name
   ```

5. **Run the application:**
   ```sh
   python app.py
   ```

6. **To deactivate the virtual environment when done:**
   ```sh
   deactivate
   ```

## How to Use

1. Launch the application: `python app.py`
2. Enter a query or task when prompted
3. Nelle automatically detects intent and routes to the appropriate workflow
4. Watch status updates as agents execute and synthesize results
5. Continue with more queries, or type `exit` or `quit` to close

**Example workflows:**
- **Direct Q&A** (auto-routed): `"What is 5 + 5?"`
- **Planning** (keywords: "plan", "how to", "steps to"): `"Plan learning Python in 30 days"`
- **Creative** (keywords: "design", "architect", "create"): `"How would you design a distributed cache?"`
- **Research** (keywords: "research", "find out", "investigate"): `"Research the latest AI frameworks"` ⚠️ (costs API calls)

## Model Configuration

The model is set via the `MODEL_NAME` environment variable in `.env`. Change it to any model supported by your OpenAI API provider.

**Example:**
```
MODEL_NAME=model-name
```

## Architecture

### SDK-Powered Agent Pattern

This project uses the **OpenAI Agents SDK**, which abstracts away the manual tool-calling loop and message management into a high-level framework.

#### Core Flow

```
User Input → Agent (SDK) → Tool Calls → Tool Execution → Streaming Response
                ↑                                              ↓
                └──────────── Session persists ───────────────┘
```

#### Orchestration Flow

Nelle uses an **intent-routed multi-agent workflow**: a deterministic keyword router dispatches
each query to one of four workflows. The research workflow follows a **plan → parallel fan-out →
synthesize** pipeline; the others are single-agent invocations.

```
                ┌──────────────┐
   user  ──►    │  app.py REPL │  ◄── streams status + output
                └──────┬───────┘
                       ▼
                ┌──────────────┐         ┌────────────────────┐
                │ TaskManager  │◄──────► │ SessionManager     │
                └──────┬───────┘         │ (in-memory history)│
                       ▼                 └────────────────────┘
              keyword router
        ┌────────┬────────┬────────┐
        ▼        ▼        ▼        ▼
     DIRECT  CREATIVE PLANNING  RESEARCH
      Solver   Solver  Planner     │
                                   ▼
                             Planner → SearchPlan(5)
                                   │
                         asyncio.gather (fan-out)
                       ┌────┬────┬────┬────┬────┐
                       ▼    ▼    ▼    ▼    ▼
                    Searcher × 5 (web_search tool)
                       └────┴────┴─┬──┴────┴────┘
                                   ▼
                             Writer → Report
```

#### Key Components

**1. Task Manager (`core/task_manager.py`)**
- Analyzes incoming queries using keyword detection
- Routes to appropriate workflow: research, planning, creative, or direct
- Coordinates agent execution with status updates via async generators
- Implements plan → parallel execute → synthesize pipeline for research

**2. Custom Agents (`custom_agents/`)**
- **Solver**: Direct Q&A and creative problem-solving
- **Planner**: Creates structured search plans (5-search strategy)
- **Searcher**: Executes web searches with the `WebSearchTool`
- **Writer**: Synthesizes search results into comprehensive reports
- All agents use Pydantic `output_type` for structured outputs (SearchPlan, Report)

**3. Session Management (`core/session.py`)**
- Wraps OpenAI Agents SDK's SQLiteSession
- In-memory session maintains conversation history automatically
- Conversation context persists across multiple tasks within one run

**4. Streaming & Output (`core/streaming.py`, `ui/`)**
- `StreamingUI` handles live-rendered status updates
- Rich markup for formatted console output
- Markdown report rendering for final outputs
- Status messages stream as agents execute

**5. Agent & Runner (OpenAI Agents SDK)**
- `Agent` defines agent's name, instructions, tools, and model
- `Runner.run` handles tool-calling loop and streaming internally
- Yields streaming events and final output
- No manual agentic loop needed

#### Design Principles

**SDK Abstraction**: The OpenAI Agents SDK eliminates boilerplate — no manual loop control, message formatting, or tool dispatch logic.

**Declarative Tools**: Decorate a function with `@function_tool` and it becomes available to the agent. The SDK handles schema generation and invocation.

**Conversational Continuity**: `SQLiteSession` tracks history automatically. The agent remembers prior tasks within the session without manual state management.

**Scoped Task State**: Checklist state rides in a per-run `context` object (`RunContextWrapper[ChecklistState]`) rather than shared globals, so it can't bleed between unrelated tasks while conversational history still persists in the session.

**Streaming UX**: Live-rendered output provides real-time feedback as the agent processes each step.

## Project Structure

```
ai-assistant/
├── app.py                          # Main REPL entry point (69 lines)
├── config/
│   └── settings.py                 # Configuration & environment loading
├── core/
│   ├── task_manager.py             # Orchestration & workflow routing
│   ├── session.py                  # Session management wrapper
│   └── streaming.py                # Live streaming UI utilities
├── custom_agents/
│   ├── solver.py                   # Direct problem-solving agent
│   ├── planner.py                  # Search planning agent
│   ├── searcher.py                 # Web search agent
│   └── writer.py                   # Report synthesis agent
├── ui/
│   ├── banner.py                   # Welcome banner
│   ├── prompts.py                  # User input handling
│   └── formatters.py               # Output formatting
├── tools/
│   ├── base.py                     # Tool base abstractions
│   └── web_search.py               # Web search tool wrapper
└── tests/
    ├── test_config.py              # Config tests
    ├── test_imports.py             # Module structure tests
    ├── test_session.py             # Session management tests
    └── test_task_manager.py        # Orchestration & routing tests (16 tests)
```

## Testing

Run the comprehensive test suite:

```bash
# Run all unit and integration tests (63 tests)
pytest tests/ -v

# Run end-to-end testing of safe workflows
python test_phase8.py
```

**Test Coverage:**
- **Imports & Structure** (26 tests): Validates all modules load correctly
- **Task Routing** (16 tests): Tests keyword-based intent detection for all task types
- **Config** (6 tests): Settings loading and environment handling
- **Session** (9 tests): Session management and persistence

All tests pass without requiring API calls or external services.

## Observability

View agent traces on OpenAI platform:

<https://platform.openai.com/traces>

## Future Enhancements

- **Persistent storage**: Swap in-memory session for file-based SQLite
- **Agent specialization**: Add domain-specific agents (code, math, design, etc.)
- **Tool library expansion**: Add more tools beyond web search (calculator, code execution, etc.)
- **Agent-to-agent collaboration**: Implement sub-task delegation
- **Interactive refinement**: Allow users to refine or re-route mid-workflow
- **Performance optimization**: Caching, token counting, and message trimming
- **Error recovery**: Automatic retry with backoff and fallback strategies
- **Observability**: OpenAI traces integration, metrics, and audit logs

---

Built as a demonstration of SDK-powered agentic workflows with live streaming output.
