# AI Prompts Log — Homework 5

This file records the prompts used while working through each problem in this assignment.

Each problem section follows this format:
1. Problem number and title.
2. At least one prompt typed by the user.
3. A follow-up prompt (if needed), with one sentence explaining what was lacking after the first prompt.

## Problem 1: Set up the AI_prompts.md logging structure

### Prompt 1

For problem 1, please create a file named AI_prompts.md at the root of our project directory. This file will serve as a log where we record the prompts we use for each problem in this assignment as we work through them step-by-step. For now, please initialize the file with a clear title and structure so we can begin logging our prompts for Problem 1 and subsequent problems.

### Follow-up Prompt (if needed)

For the following question, please update our AI_prompts.md file to ensure it strictly follows the formatting requirements for all subsequent problems. Each problem's section in the file must include: 1. The problem number and title. 2. At least one prompt I typed. 3. One follow-up prompt if needed, along with one sentence explaining what was lacking after the first prompt.

**Why the follow-up was needed:** The first pass only had a bare title and an empty "Problem 1 / Prompt 1" heading with no defined structure for subsequent problems, so it needed an explicit per-problem template (prompt + optional follow-up + one-sentence rationale) before it could be used consistently going forward.

## Problem 2: Inspect campus_customs.db and copy to a working database

### Prompt 1

For Problem 2, please examine the campus_customs.db database to inspect every table and its fields, and create a copy named data/campus_customs_new.db to serve as our working database for subsequent operations. Also, please review the three open tickets in the tickets table to understand how they link across the other tables (such as inventory, pricing, vendors, leases, cash_accounts, payments, and invoices). Once you have inspected them, please summarize your findings.

### Follow-up Prompt (if needed)

N/A

**Why the follow-up was needed:** N/A — the initial prompt was specific enough to complete the task in one pass.

### Prompt 2

Please create the output/harness.md file. For every single table in our working database (desk, tickets, inventory, pricing, vendors, leases, cash_accounts, payments, and invoices), please list all of its fields and provide one short line explaining why that specific table matters for our multi-agent team

### Follow-up Prompt (if needed)

N/A

**Why the follow-up was needed:** N/A — the initial prompt was specific enough to complete the task in one pass.

## Problem 3: Build an MCP server with ticket-handling tools

### Prompt 1

For problem 3, please write an MCP server inside an mcp_server/ directory using FastMCP. It should connect and talk to our working database at data/campus_customs_new.db. For now, you do not need to connect or run it, but please implement three specific tools that we will need to handle the tickets in the database (keeping the names clear and strictly querying real data without inventing anything).

### Follow-up Prompt (if needed)

N/A

**Why the follow-up was needed:** N/A — the initial prompt was specific enough to complete the task in one pass.

### Prompt 2

Please update output/harness.md to include a detailed breakdown of each of our three MCP tools. For every tool, explicitly list which database table it reads, which specific ticket it helps unlock (101, 102, or 103), and write one precise sentence explaining why that tool is the right one for that ticket, avoiding any generic descriptions. Additionally, please create a short mcp_server/README.md file that explains what our MCP server is for, which database file it uses, and details its three tools.

### Follow-up Prompt (if needed)

N/A

**Why the follow-up was needed:** N/A — the initial prompt was specific enough to complete the task in one pass.

## Problem 4: Configure the MCP server connection for the vibe coder

### Prompt 1

For Problem 4, please configure our MCP server so that our vibe coder can connect to it and call its tools. Save the connection configuration as a JSON file named .mcp.json at the project root.

### Follow-up Prompt (if needed)

N/A

**Why the follow-up was needed:** N/A — the initial prompt was specific enough to complete the task in one pass.

### Prompt 2

Please test each of our three MCP tools using Claude Code with our connected MCP server. Save the evidence of the testing into a JSON file named output/mcp_smoke.json. For every single tool, please include in the JSON: 1. The exact prompt you asked Claude to run it 2. The exact name of the tool 3. The actual output returned by the tool, ensuring the values precisely match the data in data/campus_customs_new.db

### Follow-up Prompt (if needed)

N/A

**Why the follow-up was needed:** N/A — the initial prompt was specific enough to complete the task in one pass.

## Problem 5: Build the multi-agent team with PydanticAI

### Prompt 1

Move to problem 5, please build the multi-agent team for Campus Customs using PydanticAI. We need five distinct agent roles: Boss, Inventory, Accounting, Facilities, and Customer Service. Please implement the following structure and constraints: 1. Create a backend/models.py file for our data types and schemas. 2. Under backend/prompts/, create a separate, detailed prompt file for each of the five agents (one file per agent). Write each prompt thoroughly in our own words, embedding the relevant shop rules (such as using desk.date_today for overdue checks, vendor lead times, ensuring unpaid invoices block new shipments, requiring human approval for payments, and preventing negative cash balances). 3. Under backend/, implement the agent files and agent loops so that they have full connectivity and can delegate tasks to each other. 4. Strictly configure every agent to use only gpt-6-luna through Portkey (using our PORTKEY_API_KEY). Ensure no other model is used anywhere in the code or runs.

### Follow-up Prompt (if needed)

Please add any additional tools the agents need to our MCP server to handle the open tickets, ensuring all shop facts come directly from our MCP server over data/campus_customs_new.db without any bypassing layer. Additionally, please complete the following documentation and logging updates: 1. Wire our agents to append their execution steps to output/audit_trail.json for auditing purposes (making sure it appends rather than overwriting on each run). 2. Update output/harness.md to list each agent and every MCP tool along with the specific database table each tool uses. Also, add a short safety section detailing the necessary guardrails for agents handling real customers and money, as well as limits to keep token usage in check. 3. Update mcp_server/README.md so the tool list matches our final set of tools.

**Why the follow-up was needed:** The first pass had each agent query `data/campus_customs_new.db` directly through a `backend/db.py` helper, which was a bypassing layer around the MCP server rather than routing every fact through it.

## Problem 6, Panel A: Build the desk plan HTML (tabs per ticket, plus Cash/Reflection stubs)

### Prompt 1

Let's move the problem 6, panel A. Please create an HTML file named output/desk_tickets.html to plan what we expect our multi-agent team to do on each open ticket. Please structure the page with the following tabs: 1. One tab per ticket (101, 102, and 103), containing an "Expected" section that details the expected first call by the Boss, one targeted agent-to-agent handoff, and the necessary MCP tools. Avoid having the Boss call everyone or using generic flows. 2. Stub tabs for "Cash" and "Reflection" (leaving them blank or adding a short "coming later" note for future problems).

### Follow-up Prompt (if needed)

Please update output/desk_tickets.html so that for each of the three ticket tabs (101, 102, and 103), the Expected section explicitly includes: 1. Who the Boss should call first, and why. 2. All expected agent delegations, ensuring we avoid having the Boss call everyone and sticking to targeted handoffs. 3. Which specific MCP tools we expect that run to use. Additionally, please include the stub tabs for Cash and Reflection as required.

**Why the follow-up was needed:** The first pass covered the same content but under looser headings ("Expected first call," "Targeted handoff," "MCP tools needed") rather than explicitly numbered as the three required elements, so the correspondence to the three requirements wasn't unambiguous.

## Problem 7: Build the FastAPI backend for the dashboard

### Prompt 1

For the Problem 7, please create or update our FastAPI backend in backend/main.py to implement the essential API routes required for our frontend dashboard. Specifically, please include routes that: 1. Return the list of the three tickets and whether each is currently open or resolved. 2. Accept a ticket ID and trigger the execution of our multi-agent team on that specific ticket. 3. Return recent agent events (showing what each agent said and the tools they used) so the dashboard can refresh. 4. Handle human-approved payments or purchases (since agents only prepare payments, this route must execute the cash transfer and update the relevant tables). 5. Return the current checking account balance from cash_accounts. 6. Reset the working database back to the original values when a fresh run is requested.

### Follow-up Prompt (if needed)

N/A

**Why the follow-up was needed:** N/A — the initial prompt was specific enough to complete the task in one pass.

### Prompt 2

Please update our output/harness.md file to list every FastAPI route we created in backend/main.py, providing a concise one-line description for each route detailing its URL and what it does. Also, please ensure our backend server can be started properly with uvicorn main:app --reload --port 8000 from the backend/ directory.

### Follow-up Prompt (if needed)

N/A

**Why the follow-up was needed:** N/A — the initial prompt was specific enough to complete the task in one pass.

## Problem 8: Build the React/Vite/TypeScript frontend dashboard

### Prompt 1

Please build the frontend dashboard in a frontend/ directory using React, Vite, and TypeScript. The interface should call the API routes we built in Problem 7 and serve as our interactive agent operations desk. At a minimum, the dashboard should: 1. List all three tickets clearly on a board. 2. Allow a user to pick any single ticket and trigger the execution of our multi-agent team on it. 3. Show live updates of each agent and what they are saying or doing while the ticket runs. 4. Mark a ticket as resolved when the run finishes. 5. Display a short summary of what each agent did on that ticket. 6. Provide a way for a human to approve a pay or purchase request when prompted. 7. Show the current checking account balance, reflecting drops when payments are approved. Please make the dashboard look polished, creative, and thoughtfully styled like a real desk setup rather than a default Vite template.

### Follow-up Prompt (if needed)

N/A

**Why the follow-up was needed:** N/A — the initial prompt was specific enough to complete the task in one pass.

### Prompt 2

Please configure our FastAPI backend to allow requests from the Vite frontend origin (specifically http://localhost:5173) using CORS so that the browser can successfully communicate with our API routes at http://localhost:8000. Additionally, please create a file named output/design.md detailing the design choices we made for our dashboard. Include: 1. The overall layout and styling choices that make it look polished and creative rather than a default Vite template. 2. How different agents are visually distinguished. 3. How resolved tickets and current cash balances are prominently displayed. 4. The creative design choices that make the desk feel special and intuitive for human operators. Finally, please verify how to start the development server using `npm run dev` in the frontend directory.

**Why the follow-up was needed:** The first pass had left CORS wide open (`allow_origins=["*"]`) and the Vite dev server pinned to port 5174 (to dodge a conflict with an unrelated project's dev server during testing), which no longer matched the port 5173 this request specifically named.

## Problem 9: Run all three tickets through the real multi-agent team

### Prompt 1

Let's move to Problem 9. Please reset our working database data/campus_customs_new.db back to its original clean state from data/campus_customs.db, and note the starting checking account balance. Then, run all three open tickets (101, 102, and 103) through our multi-agent team until every single ticket is fully resolved. Finally, update output/desk_tickets.html so that for each ticket tab, the Actual section is completely filled out with the real execution details from this run—specifying which agents worked, what tasks they delegated to each other, and which MCP tools were used, while keeping the Expected section for comparison.

### Follow-up Prompt (if needed)

This is my API Key: [redacted — PORTKEY_API_KEY provided in chat, not stored in this log]

**Why the follow-up was needed:** PORTKEY_API_KEY wasn't set anywhere in the environment, so the first attempt to run the real team against gpt-6-luna couldn't authenticate; I asked the user to supply it. A second blocker also surfaced once the key was in place: Portkey/Azure rejected function-tool calls on gpt-6-luna whenever a reasoning_effort was implicitly set, which required pinning `openai_reasoning_effort="none"` in `backend/config.py` before any ticket would actually run.

### Prompt 2

Please complete the remaining requirements for Problem 9, specifically focusing on financial tracking, final documentation, and output artifacts: 1. On the Cash tab of output/desk_tickets.html, please itemize the cash flow: starting checking balance (immediately following the database reset), for each ticket (101, 102, and 103) document how the cash changed upon resolution detailing the exact pay or purchase action and the dollar amount, and the ending checking balance, ensuring it matches cash_accounts in the working database precisely. 2. Create output/resolved_tickets.json containing the final status, short outcome, contributions of each agent, and any human approvals for each ticket. 3. Create output/resolved_board.html featuring screenshots of your React board for each resolved ticket (101, 102, and 103). 4. Append the execution audit trail to output/audit_trail.json. 5. Finalize output/harness.md so that it comprehensively covers the tables, MCP tools, the five agent definitions, FastAPI routes, the frontend dashboard, and all necessary safety rules.

### Follow-up Prompt (if needed)

Approve both now — I asked the user whether to approve the two pending payments (invoice 501 and rent) so the Cash tab could show real before/after deltas, since our system's guardrails require an explicit human decision before any money moves; the user chose to approve both.

**Why the follow-up was needed:** The real run had only drafted both `PaymentRequest`s, not executed them (that's the whole point of the human-approval guardrail), so the cash-flow itemization this prompt asked for couldn't show real deltas without that explicit approval decision. While building the screenshots for `resolved_board.html` I also found and fixed a real gap: `POST /api/payments/approve` had no duplicate-approval guard, which could have double-paid the same invoice/rent — added a check that rejects (409) a second approval for the same `kind`+`ref_id`.

## Problem 10: Fill out the Reflection tab

### Prompt 1

Move to the Problem 10. Please fill out the Reflection tab in output/desk_tickets.html thoroughly and in detail. Please ensure you cover: 1. How we evaluate the performance of the agents on each ticket (101, 102, and 103) and why. 2. For each ticket, how the Actual execution compared to the Expected plan we wrote earlier (including human approvals and delegation differences). 3. An analysis of what would have been simpler as a single agent with tools, and why. 4. Descriptions of three new problems Campus Customs might face that this multi-agent team could solve with the tools we built. 5. Descriptions of three new problems Campus Customs might face that this team could not solve with our current tools, along with the new tools and agents required to solve them.

### Follow-up Prompt (if needed)

N/A

**Why the follow-up was needed:** N/A — the initial prompt was specific enough to complete the task in one pass. While writing the Actual-vs-Expected comparison, I caught and fixed an inconsistency in ticket 102's own Actual section from the prior turn: it had claimed the delegation targets "matched the plan exactly," but the plan's own "Not delegated to" list had explicitly predicted no Customer Service call, and the real run did delegate to Customer Service — corrected before writing the Reflection so the two sections wouldn't contradict each other.

### Prompt 2

Please complete the remaining reflections and analysis on the Reflection tab of output/desk_tickets.html, ensuring everything is strictly tied to our Campus Customs app, database, and actual ticket runs (101, 102, and 103). Specifically, please include: 1. Detailed descriptions of three new problems Campus Customs might face that this multi-agent team could solve using our existing toolset. 2. Detailed descriptions of three new problems Campus Customs might face that our current team and tools could not solve, along with the precise new tools and agent roles required to handle them.

### Follow-up Prompt (if needed)

N/A

**Why the follow-up was needed:** N/A — the initial prompt was specific enough to complete the task in one pass.

## Problem 11: Prepare the repository for final submission

### Prompt 1

For Problem 11, please prepare our repository for final submission by completing the following: 1. Initialize a git repository (if not already done), ensure our real .env file is excluded via .gitignore (while keeping .env.example), and verify that both database files under data/ (campus_customs.db and campus_customs_new.db) are included. 2. Push our code to a new public GitHub repository. 3. Save the public repository URL into output/github_url.txt so we can easily submit it to Canvas. 4. Double-check that our file structure matches the expected layout, including AI_prompts.md, requirements.txt, .env.example, .gitignore, .mcp.json, README.md, the mcp_server/ directory, frontend/, backend/, and all required output files.

### Follow-up Prompt (if needed)

N/A

**Why the follow-up was needed:** N/A — the initial prompt was specific enough to complete the task in one pass. While assembling the repo I found `mcp_server/requirements.txt` was missing (an earlier turn had apparently written "fastmcp" to the project root instead, due to a cwd mix-up across turns) and recreated it; also added a root-level `requirements.txt`, `.env`/`.env.example`, `.gitignore`, and `README.md`, none of which existed yet.
