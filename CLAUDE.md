# AI Assistant Instructions for Claude and Other AI Agents

## Critical: Virtual Environment Setup

**⚠️ IMPORTANT**: This project uses a local virtual environment. **ALWAYS** activate it before running any Python commands.

### Virtual Environment Location
```
.venv/
```

### Activation Commands

**Before running ANY Python command**, activate the virtual environment:

```bash
# Activate venv (REQUIRED before any Python commands)
source .venv/bin/activate

# Verify you're in the venv (should show .venv path)
which python
```

### Python Command Usage

Once activated, use:
- `python` (NOT `python3`) - venv Python
- `pip` (NOT `pip3`) - venv pip

### Common Tasks

**Install dependencies:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

**Run tests:**
```bash
source .venv/bin/activate
python test_phase6.py
```

**Run the app:**
```bash
source .venv/bin/activate
python app.py
```

**Check imports:**
```bash
source .venv/bin/activate
python -c "from core.task_manager import TaskManager; print('OK')"
```

**Deactivate when done:**
```bash
deactivate
```

### What NOT to Do

❌ **DO NOT** use `python3` or `pip3` directly - these use global Python  
❌ **DO NOT** install packages globally (`pip3 install`)  
❌ **DO NOT** run Python commands without activating venv first  

### Verification

To verify venv is active:
```bash
which python
# Should output: /Users/vpomyate/projects/ai-assistant/.venv/bin/python
# NOT: /Library/Frameworks/Python.framework/...
```

## Project Structure

```
ai-assistant/
├── .venv/                      # Virtual environment (ACTIVATE THIS)
├── custom_agents/              # Custom agent definitions
│   ├── planner.py
│   ├── searcher.py
│   ├── solver.py
│   └── writer.py
├── core/                       # Core orchestration
│   ├── task_manager.py
│   ├── session.py
│   └── streaming.py
├── tools/                      # Tool abstractions
│   ├── base.py
│   └── web_search.py
├── ui/                         # Terminal UI
│   ├── banner.py
│   ├── prompts.py
│   └── formatters.py
├── config/                     # Configuration
│   └── settings.py
├── app.py                      # Main entry point
├── requirements.txt            # Dependencies
└── .env                        # API keys (not in git)
```

## Important Notes

1. **Package Naming**: We use `custom_agents/` instead of `agents/` to avoid conflicts with the `openai-agents` SDK which also imports as `agents`.

2. **SDK Imports**: OpenAI Agents SDK components (Agent, Runner, etc.) are imported from the global `agents` package:
   ```python
   from agents import Runner, Agent  # SDK
   from custom_agents.solver import create_solver_agent  # Our code
   ```

3. **Testing**: Some tests are expensive (WebSearchTool costs money). Only run research workflows when explicitly requested.

4. **Environment Variables**: Ensure `.env` exists with `OPENAI_API_KEY` and `MODEL_NAME`.

## For AI Agents Running Commands

When you need to execute Python commands:

1. **FIRST**: Check if venv exists: `ls -la .venv/`
2. **ALWAYS**: Activate it: `source .venv/bin/activate`
3. **THEN**: Run your command: `python <script>.py`
4. **USE**: `python` not `python3`, `pip` not `pip3`

## Initial Setup (If .venv doesn't exist)

```bash
# Create venv
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify
python -c "import agents; print('SDK installed')"
```

---

**Summary**: Always activate `.venv/` first, use `python`/`pip` (not `python3`/`pip3`), keep global Python clean.
