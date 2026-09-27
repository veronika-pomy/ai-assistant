---
name: backlog-hygiene
description: Where to put new work in docs/ai/ — completed epics stay frozen; everything new goes in future slots
---

# Backlog hygiene

The backlog is a historical record as much as a plan. Once a ticket or epic is marked done, don't backfill into it — that rewrites history and makes "was this shipped?" impossible to answer at a glance.

## Rules

1. **Never modify a completed ticket or epic.** If a ticket has `✅` or every checkbox is ticked, the epic it lives in is frozen. Don't add new acceptance criteria, checklist items, or scope creep to it — even for "small follow-ups."
2. **New work goes in a future slot.** New scope, new ticket, new spec — always in a section that isn't yet complete.
3. **Bugs and regressions found in later work get their own home.** They go into the `## Bugs` section at the bottom of `docs/ai/backlog.md` with their own `B1`, `B2`, … IDs. They do not go into the epic where the buggy code originally shipped.
4. **Corrections vs. additions.** Small factual corrections to an old ticket (e.g. a fixed typo, a broken link) are fine. New scope disguised as a correction is not — if in doubt, file it as a new ticket.
5. **Specs follow tickets.** A ticket in a completed epic doesn't get new spec content. A new ticket (in a future epic slot or in `## Bugs`) either extends its epic's spec file or, for bugs, keeps its detail inline in the backlog entry — no need to spin up a spec-per-bug.

## Where to add things

| Kind of work | Where |
|---|---|
| New feature in an unstarted epic | Existing ticket in that epic, or a new one within it |
| New feature that doesn't fit any current epic | New epic at the end of the backlog table |
| Deferred nice-to-have (not currently planned) | `docs/ai/roadmap.md` |
| Bug in shipped code, discovered during later work | `## Bugs` section at the bottom of `docs/ai/backlog.md` with a `BN` ID |
| Design note about future architecture | `docs/ai/architecture.md` if load-bearing; otherwise inline in the relevant epic spec |

## Apply when

- Filing a follow-up ticket from a smoke test or code review.
- Discovering a bug that traces back to older, shipped code.
- Any time you find yourself adding a `- [ ]` under a ticket that's already `✅`.

## Anti-pattern to avoid

```
### T1.3 Token streaming (M) ✅
- [x] Final answers stream token-by-token
- [x] Delete dead streaming module
- [x] Unit test: fake event stream → deltas
- [ ] Fix line duplication  ← WRONG. T1.3 is done. File as a Bug or new ticket.
```
