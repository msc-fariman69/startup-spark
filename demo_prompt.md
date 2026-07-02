# StartupSpark Demo Prompt

Use this prompt to test the agent in ADK CLI or ADK Web.

## Demo Scenario

A founder has a startup idea but needs help turning it into a clear validation plan, MVP scope, landing page copy, and short pitch.

## Prompt

```text
I want to build an app that helps remote software teams reduce unnecessary meetings.

The idea is to analyze meeting calendars, identify repeated status meetings, suggest async updates, and show engineering managers how much focus time they can save.

Please create a StartupSpark report and save it as remote-team-meeting-reducer.
```

## Expected Behavior

The agent should generate a Markdown report with these sections:

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

## Expected Tool Usage

The agent may use:

- `load_skill`
- `score_startup_idea`
- `create_validation_experiments`
- `save_startup_report`

## Expected Output File

If saving works correctly, the agent should create:

```text
outputs/remote-team-meeting-reducer.md
```
