# E6 — Notifications & Spikes Spec

Bottom of the backlog: cheap, optional, or exploratory.

## T6.1 Telegram notification tool

**Approach:**
- New `tools/telegram_notify.py` (implements `BaseTool`):
  ```python
  @function_tool
  async def notify_telegram(message: str) -> str:
      # httpx.post(f"https://api.telegram.org/bot{token}/sendMessage",
      #            json={"chat_id": chat_id, "text": message})
  ```
- Registered on the orchestrator **only when** `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set (absent config = tool not offered, so the model can't try it).
- Instruction line: "Use notify_telegram ONLY when the user explicitly asks to be notified (e.g. 'ping me on Telegram when the research is done'). Never send unprompted."
- Typical flow: user asks for research + notification → orchestrator runs `run_research`, then calls `notify_telegram` with a one-line summary.
- New dep: `httpx`. Setup (create bot via @BotFather, get chat id) documented in `.env.example`.

**Test:** mock httpx — payload shape; tool absent from orchestrator when unconfigured.
