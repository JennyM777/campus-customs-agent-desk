# Dashboard Design Notes — Campus Customs Agent Desk

Design rationale for `frontend/`, the operations console a human uses to run and supervise the multi-agent team.

## 1. Overall layout and styling

The dashboard is a three-column "desk," not a single scrolling page: **Ticket Tray** (left), **Live activity** (center, widest), **Decision & Approvals** (right). This mirrors how an actual ops desk is organized — an inbox, a working surface, and an outbox — rather than stacking everything in one default-template column.

Styling choices that move it away from a stock Vite look:
- A custom dark theme (CSS variables in `index.css`) with a subtle radial gradient background (`--bg-grad`) instead of a flat color, giving the page depth without any imagery.
- Cards throughout (`panel`/`panel-raised` surfaces, 10–12px rounded corners, soft 1px borders) instead of plain divs, so every ticket, feed entry, and summary block reads as a distinct physical object on the desk.
- A header bar with a logo glyph, a one-line mission statement under the title, the live cash badge, and a reset control — establishing it as a tool, not a template landing page.
- Deliberate micro-interactions: cards lift slightly on hover, the selected ticket gets an accent-tinted background, and feed entries animate in (`feedIn` keyframe) rather than appearing abruptly.

## 2. How agents are visually distinguished

Every agent gets its own accent color, applied consistently everywhere it appears (the live feed's left border, and implicitly through its labeled card in the summary panel):

| Agent | Color | Where it shows |
|---|---|---|
| Boss | blue (`--accent`) | Feed entry border, delegation list |
| Inventory | purple | Feed entry border |
| Accounting | green (`--ok`) | Feed entry border |
| Facilities | amber (`--warn`) | Feed entry border |
| Customer Service | teal | Feed entry border |

Each feed entry also has a clear, human-readable agent name (not the raw `*_agent` identifier), a timestamp, and its own icon vocabulary for actions — 🔧 for a tool call, ↩ for a tool's return value, 💬 for a text remark, 📝 for its final one-line summary — so the *kind* of thing an agent is doing is scannable at a glance without reading every word.

## 3. Resolved tickets and cash balance

- **Resolved tickets**: each ticket card carries a status pill — amber "Open" or green "Resolved" — in its top row, impossible to miss. A resolved card also dims slightly (`opacity: 0.6`) and its "Run team" button changes to a disabled "Resolved" state, so there's no ambiguity about whether it can be re-run.
- **Cash balance**: pinned in the header, always visible regardless of which ticket is selected or scrolled to. It's styled as its own badge (not just inline text) with a large tabular-numeral dollar figure and an as-of date. When a payment is approved and the balance changes, the badge flashes red (drop) or green (increase) for under a second — a deliberate, brief animation so a balance change is noticed without being distracting or left in a permanently-alarming state.

## 4. Creative choices for operator intuition

- **Streaming the "thinking," not just the result.** Because the backend's run endpoint is a single blocking call, the dashboard polls the audit-trail endpoint *during* that call and reconstructs a live feed from it — so the operator watches the team work (tool calls, tool returns, findings) in near-real time instead of staring at a spinner and receiving a wall of text at the end.
- **An explicit "not called" list is implicit in design, not UI copy.** Rather than listing every agent whether or not it ran, the feed and summary panel only ever show the specialists actually delegated to for that ticket — reinforcing (visually, not just in prose) that the Boss makes targeted calls rather than fanning out to everyone.
- **Payments are a queue, not a popup.** Pending `PaymentRequest`s appear as cards in the same right-hand column as the decision summary, each showing kind, amount, reason, and reference id plus an editable "Approving as" name field — so approval feels like a deliberate desk action (reviewing a slip and signing it) rather than dismissing a modal.
- **The reset button is deliberately understated** — neutral gray by default, only turning red on hover — present for the operator's sandbox workflow, but not something that invites accidental clicks.
