# Nelle - Agent Loop

A demo of an autonomous agent loop using OpenAI's function calling API. Nelle is a task assistant that breaks down problems into checklists, executes each step, and reports progress with styled terminal output.

![Nelle Demo](demo.png)

## Features

- **Interactive Terminal UI**: Styled ASCII art and Rich console formatting
- **Autonomous Task Planning**: Agent creates and manages checklists autonomously
- **Tool-based Architecture**: Agent uses function calling to create checklists and mark items complete
- **Step-by-Step Execution**: Visual progress tracking with strikethrough formatting for completed items

## Tech Stack

**Core Dependencies:**
- **Python 3.10+**
- **OpenAI API** (`openai`) - GPT model access and function calling
- **Rich** (`rich`) - Terminal formatting and styled output
- **python-dotenv** (`python-dotenv`) - Environment variable management

## Setup

1. **Activate the virtual environment:**
   ```sh
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

4. **Run the application:**
   ```sh
   python agent_loop.py
   ```

5. **To deactivate the virtual environment when done:**
   ```sh
   deactivate
   ```

## How to Use

1. Launch the application
2. Enter a task or problem when prompted
3. Watch Nelle break it down into steps and work through them
4. Choose whether to work on another task or exit

**Example prompts:**
- "Plan a dinner party for 8 people with a $200 budget"
- "Create a shopping list for making pasta carbonara"

## Model Configuration

**Current Model:** `gpt-5.5`

The model is defined as a constant near the top of `agent_loop.py` (line 16). You can swap to any OpenAI model.

### Using OpenAI-Compatible APIs

The OpenAI SDK can work with many providers that offer **OpenAI-compatible endpoints** by setting a custom `base_url`. Simply update the client initialization in `agent_loop.py`:

**Major Providers:**

```python
# Anthropic (Claude)
openai = OpenAI(
    api_key="your_anthropic_key",
    base_url="https://api.anthropic.com/v1"
)

# DeepSeek
openai = OpenAI(
    api_key="your_deepseek_key",
    base_url="https://api.deepseek.com/v1"
)

# Google Gemini
openai = OpenAI(
    api_key="your_google_key",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Groq (Fast inference)
openai = OpenAI(
    api_key="your_groq_key",
    base_url="https://api.groq.com/openai/v1"
)

# xAI (Grok)
openai = OpenAI(
    api_key="your_grok_key",
    base_url="https://api.x.ai/v1"
)

# OpenRouter (Multi-model aggregator)
openai = OpenAI(
    api_key="your_openrouter_key",
    base_url="https://openrouter.ai/api/v1"
)

# Azure OpenAI
openai = OpenAI(
    api_key="your_azure_key",
    base_url="https://your-resource.openai.azure.com/",
    default_headers={"api-version": "2024-02-01"}
)

# Local Models (Ollama, LM Studio)
openai = OpenAI(
    api_key="ollama",  # Can be any string for local
    base_url="http://localhost:11434/v1"
)
```

**Note:** When using these providers, make sure to:
1. Update the `MODEL` constant to use a model name supported by that provider
2. Verify that the provider supports function calling (most modern ones do)
3. Check provider-specific documentation if additional help

## Architecture

### The Agent Loop Pattern

This project demonstrates a **tool-calling agent loop**, a common pattern for building autonomous AI agents that can take actions and respond to results iteratively.

#### Core Loop Flow

```
User Input → Agent Planning → Tool Calls → Tool Execution → Results → Agent Response
                ↑                                                            ↓
                └────────────────── Loop continues ─────────────────────────┘
```

#### Key Components

**1. Message History (`messages` array)**
- Maintains conversation context between user, assistant, and tool results
- Each message has a `role` field: `user`, `assistant`, or `tool`
- Grows with each iteration, providing full context to the model

**2. Tool Definitions**
- JSON schemas describe available functions (`create_checklist`, `mark_complete`)
- Sent to the OpenAI API so the model knows what actions it can take
- Include parameter types, descriptions, and requirements

**3. Tool Execution Handler**
- Receives tool calls from the API response
- Dynamically dispatches to Python functions using `globals().get()`
- Returns results formatted as tool messages with matching `tool_call_id`

**4. Loop Control**
- Continues while `finish_reason == "tool_calls"`
- Exits when agent decides it's done (no more tools needed)
- Final response shown to user

#### Design Principles

**Autonomy**: The agent decides when and how to use tools without hard-coded logic. It can adapt its approach based on the task.

**Extensibility**: Adding new tools only requires:
- Defining the function
- Adding its JSON schema to the `tools` array
- No changes to the loop logic

**Transparency**: Each tool call is visible in the console, showing the agent's "thought process" as it works through the checklist.

**Stateful Execution**: The `checklist` and `completed` arrays maintain state across tool calls, allowing the agent to track progress over multiple steps.

#### The Two Loops

**Outer Loop (Agent Iterations)**
```python
while response.finish_reason == "tool_calls":
    # Agent wants to call tools
    # Execute them and continue
```

**Inner Loop (Batch Tool Calls)**
```python
for tool_call in tool_calls:
    # Execute each tool call
    # Collect all results
```

The agent can request multiple tools in a single response (e.g., "create checklist AND mark first item complete"), which the inner loop handles in parallel before continuing the outer conversation loop.

## Project Structure

```
agent_loop.py
├── Imports & Setup
├── Helper Functions (show)
├── Checklist State (checklist, completed arrays)
├── Checklist Functions (create_checklist, mark_complete, get_checklist_report)
├── Tool JSON Schemas
├── Tool Execution (handle_tool_calls)
├── Agent Loop (loop function)
├── User Interface (get_user_task, main)
└── Entry Point (__name__ == "__main__")
```

## Learning Notes

This demo illustrates several important patterns:

- **Function calling vs. prompting**: Instead of asking the agent to output JSON we parse, we use structured function calls with guaranteed schema adherence
- **State management**: Global state (`checklist`, `completed`) persists across tool calls within a single task
- **Dynamic dispatch**: `globals().get(tool_name)` allows runtime function lookup without switch statements
- **Message role separation**: OpenAI uses `role` to understand context—`user` inputs, `assistant` responses, `tool` results
- **Progressive enhancement**: The Rich library gracefully falls back to plain text if rendering fails

## Future Enhancements

- Add persistent storage (save/load checklists)
- Support for sub-tasks and nested checklists
- Multi-agent collaboration (delegate subtasks to specialized agents)
- Streaming responses for real-time progress updates
- Tool result validation and error recovery

---

Built as a demonstration of modern AI agent patterns and autonomous task execution.
