# StartupSpark Agent Guidance

## Project Goal

StartupSpark is a simple Google ADK capstone agent that helps startup founders validate a raw startup idea and produce a structured Markdown validation brief.

## Constraints

- Keep the project simple and readable.
- Use Python and Google ADK.
- Use one root ADK agent.
- Use local tools/functions only.
- Do not add web search, browsing tools, external APIs, databases, or extra agent orchestration.
- Keep the existing local `api/` and `ui/` as thin demo wrappers only.
- Do not move core business logic out of the ADK agent.
- Keep specs under `specs/`.
- Keep local skills under `.agent/skills/`.
- Keep generated outputs under `outputs/`.
- Final agent output must be Markdown.
- Do not modify ADK-generated files unless the change is required and approved.
- Do not modify `startup_spark_agent/agent.py` until the implementation step is approved.

## Expected Output Sections

The agent should generate these sections in order:

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

## Implementation Notes

- Prefer explicit prompts and small local helper functions over complex orchestration.
- Keep tools deterministic and local, such as formatting, validation, or section checks.
- Do not create sub-agents.
- Do not expand the UI beyond a thin local demo wrapper.
- Use eval files in `evals/` to judge output quality instead of brittle tests that assert exact LLM wording.
