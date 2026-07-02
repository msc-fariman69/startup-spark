# StartupSpark

Turn a startup idea into a Markdown validation brief.

StartupSpark is a Google ADK capstone agent for basic idea validation. It covers customer, pain, MVP scope, landing copy, experiments, risks, a 7-day plan, and a pitch. Local tools only, no web research.

## What It Does

StartupSpark is a Google ADK agent for early-stage founders, solo builders, and capstone reviewers. Give it an idea in plain language, and it returns a Markdown brief for deciding what to validate before building.

It focuses on practical startup validation:

- Clarifies the idea and likely early adopter
- Defines the customer pain and value proposition
- Suggests a focused MVP scope
- Drafts landing page copy
- Recommends quick validation experiments
- Calls out risks and assumptions
- Produces a concrete 7-day action plan
- Ends with a short founder pitch

## Output Format

The final agent response is Markdown with these sections in order:

1. Idea Summary
2. Target Customer
3. Pain Point
4. Value Proposition
5. MVP Scope
6. Landing Page Copy
7. Validation Experiments
8. Risks
9. 7-Day Action Plan
10. Short Pitch

## Project Shape

StartupSpark keeps the core logic inside one root ADK agent. The API and UI are thin local demo wrappers around that agent.

```text
startup-spark/
|-- startup_spark_agent/
|   |-- agent.py
|   |-- .env.example
|   `-- __init__.py
|-- api/
|   |-- main.py
|   |-- requirements.txt
|   `-- __init__.py
|-- ui/
|   |-- index.html
|   |-- package.json
|   |-- vite.config.ts
|   `-- src/
|       |-- App.tsx
|       |-- main.tsx
|       `-- styles.css
|-- specs/
|   |-- startup_spark_spec.md
|   `-- output_contract.md
|-- .agent/
|   `-- skills/
|       |-- clarifying-startup-ideas/
|       |-- designing-mvps/
|       |-- validating-startup-ideas/
|       |-- writing-founder-pitches/
|       `-- writing-landing-pages/
|-- evals/
|   |-- startup_spark_eval_cases.json
|   `-- manual_eval_checklist.md
|-- outputs/
|-- demo_prompt.md
|-- requirements.txt
`-- README.md
```

## Guardrails

StartupSpark is intentionally small and local-first:

- One root Google ADK agent
- Python business logic
- Local deterministic tools/functions only
- No web search or browsing tools
- No live market research claims
- No database or account system
- No sub-agent orchestration
- Markdown output only

## Quick Start

Create a virtual environment and install the ADK dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Configure local ADK credentials in `startup_spark_agent/.env` if your runtime requires them. Do not commit real secrets.

Create the local env file from the template:

```powershell
copy startup_spark_agent\.env.example startup_spark_agent\.env
```

Then edit `startup_spark_agent/.env` and replace placeholder values with your local credentials.

Run the agent from the project root:

```powershell
.\.venv\Scripts\adk.exe run startup_spark_agent
```

You can also open the ADK web UI:

```powershell
.\.venv\Scripts\adk.exe web
```

## Run The Demo API

Install API dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r api\requirements.txt
```

Start the FastAPI wrapper:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8001
```

Endpoint:

```text
POST http://127.0.0.1:8001/api/generate-report
```

Request body:

```json
{
  "idea": "startup idea text",
  "save_as": "optional-file-name"
}
```

Response body:

```json
{
  "report": "markdown report text"
}
```

## Run The Demo UI

In a second terminal:

```powershell
cd ui
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

The Vite dev server proxies `/api` requests to the FastAPI backend on port `8001`.

## Example Idea

```text
I want to build an app that helps remote software teams reduce unnecessary meetings.

The idea is to analyze meeting calendars, identify repeated status meetings,
suggest async updates, and show engineering managers how much focus time they can save.
```

Optional save file name:

```text
remote-team-meeting-reducer
```

If a save file name is provided, the agent may save the Markdown report under `outputs/`.

## Evaluation

Use the files in `evals/` to judge output quality without relying on brittle exact-wording tests. The important checks are whether the agent:

- Produces all 10 required sections in order
- Stays concise and useful
- Avoids unsupported market claims
- Recommends low-cost validation before building
- Gives a specific 7-day action plan

## Tech Stack

- Python
- Google ADK
- FastAPI
- React
- Vite
- TypeScript
