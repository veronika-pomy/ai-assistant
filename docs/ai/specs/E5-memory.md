# E5 — Persistent Memory Spec

Sessions already use the SDK's `SQLiteSession`; persistence is off only because `app.py:21` hardcodes `":memory:"`. This epic makes it a real file DB with chat metadata and a picker UI. Independent of E2–E4 (only needs T1.1's event/prompt structure).

## T5.1 Persistent sessions + chat IDs

**Approach:**
- `core/session.py`: `SQLiteSession(chat_id, settings.session_db_path)` with `SESSION_DB_PATH` defaulting to `data/sessions.db` (add `data/` to `.gitignore`). The unused `SESSION_TYPE` setting either drives `:memory:` vs file (useful for tests) or gets deleted in favor of the path setting.
- Chat metadata: a `chats` table (`id TEXT PK, title TEXT, updated_at TEXT`) in the same DB, managed with plain `sqlite3` in `SessionManager` — the SDK owns its own message tables; we only add ours alongside.
  - `create_chat()` → uuid id; title = first user message truncated ~60 chars; `touch(chat_id)` on every turn.
  - `list_chats(limit, offset)`, `delete_chat(id)` (removes metadata + calls session clear).
- Implement the existing `clear()` stub via the SDK session's clear.

**Gotcha:** unchanged invariant from E2 — only the top-level orchestrator run gets `session=`; parallel searcher runs stay session-less (concurrent SQLite writes would interleave history).

**Test:** tmp-path DB — create/list/touch/delete round-trip; ordering by `updated_at`.

## T5.2 Recents menu + chat browser

**Approach:**
- Startup menu in `ui/prompts.py` (before the REPL):
  ```
  [n] New chat
  [1-5] <5 most recent chats: title — relative time>
  [a] Browse all chats
  ```
  "Browse all" = paginated console list (10/page, next/prev/select). This is the "tool or skill to pull up all of them in the console and click through" — plain numbered selection, no mouse.
- `/chats` command handled in the REPL loop (alongside exit commands) to reopen the menu mid-session; switching chats swaps the `SQLiteSession` instance.
- Selecting an existing chat should print the last few messages as context (the SDK session exposes `get_items`); keep it to ~3 exchanges.

**Files:** `ui/prompts.py`, `app.py`, `core/session.py`.
**Test:** menu logic unit-tested with a fake chat list (selection → chat_id mapping); rendering itself manual.
