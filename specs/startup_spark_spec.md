# StartupSpark Spec

## Overview

StartupSpark is a Google ADK agent for early-stage startup idea validation. A founder provides an idea in plain language. The agent returns a Markdown brief with the likely customer, pain point, MVP scope, landing page copy, validation experiments, risks, and a 7-day action plan.

## Goals

- Help a founder move from vague idea to a concrete validation plan.
- Keep the response practical, concise, and action-oriented.
- Produce a complete Markdown document with the required 10 sections.
- Use local skills and local helper functions only.

## Target User

StartupSpark is for early-stage founders, solo builders, and capstone reviewers who want a validation brief before building.

## Non-Goals

- No market-size research.
- No live competitor research.
- No web search.
- No external APIs.
- No frontend or dashboard.
- No multi-agent architecture.
- No database or persistent user accounts.

## User Flow

1. User provides a raw startup idea.
2. Root ADK agent analyzes the idea using the local startup validation skill.
3. Local helper functions may validate or format the Markdown structure.
4. Agent returns one final Markdown validation brief.

## Required Output Sections

The final Markdown response must include these sections in order:

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

## Agent Design

- One root ADK agent.
- Python implementation.
- Local tools/functions only.
- Skill guidance stored under `.agent/skills/`.
- Output contract stored in `specs/output_contract.md`.

## BDD Scenarios

### Clear startup idea

Given a founder provides a clear startup idea with a customer and problem, when the agent responds, then it should generate the full 10-section StartupSpark Markdown report.

### Vague startup idea

Given a founder provides a vague idea such as "I want to build an AI app", when the agent responds, then it should ask 3 to 5 clarifying questions before generating a full report.

### Landing page or MVP request

Given a founder asks specifically for landing page copy or MVP scope, when the agent responds, then it should focus on that request while staying consistent with the StartupSpark output contract and safety rules.

## Local Tool Ideas

These are optional implementation candidates for a later step:

- `normalize_idea_input(raw_idea: str) -> str`
- `build_markdown_outline() -> str`
- `validate_required_sections(markdown: str) -> dict`
- `save_markdown_output(markdown: str, filename: str) -> str`

All tools must remain local and deterministic. They must not call web services or external APIs.

## Safety and Quality Rules

- Do not invent claims that require current market data.
- Do not claim that an idea is guaranteed to work.
- Separate assumptions from recommended validation experiments.
- Prefer specific customer segments over broad audiences.
- Prefer small MVPs that can be validated quickly.
- Use plain language suitable for a non-technical founder.

## Success Criteria

- Output is valid Markdown.
- Output includes all 10 required sections in order.
- Recommendations are specific enough for a founder to act on within 7 days.
- Validation experiments are low-cost and do not require external integrations.
- Risks are concrete and tied to the idea.
- The short pitch is concise and understandable.
