from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from google.adk.agents import Agent


BASE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = BASE_DIR / ".agent" / "skills"
OUTPUTS_DIR = BASE_DIR / "outputs"


def _path_is_relative_to(path: Path, base: Path) -> bool:
    """Return True when path resolves inside base."""
    try:
        path.resolve().relative_to(base.resolve())
    except ValueError:
        return False
    return True


def _safe_slug(value: str) -> str:
    """Create a safe filename slug from user-provided text."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value[:60] or "startup-spark-report"


def list_available_skills() -> dict[str, Any]:
    """
    List local StartupSpark skill folder names from .agent/skills.

    Returns:
        A dictionary with status and a list of available skill folder names.
    """
    if not SKILLS_DIR.exists():
        return {
            "status": "error",
            "message": f"Skills directory not found: {SKILLS_DIR}",
            "skills": [],
        }

    skills = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            skills.append(skill_dir.name)

    return {
        "status": "success",
        "skills": skills,
    }


def load_skill(skill_name: str) -> dict[str, Any]:
    """
    Load a local StartupSpark SKILL.md file by skill folder name.

    Args:
        skill_name: The folder name under .agent/skills to load.

    Returns:
        A dictionary with status and the skill Markdown content when found.
    """
    skill_file = SKILLS_DIR / skill_name / "SKILL.md"

    if not _path_is_relative_to(skill_file, SKILLS_DIR):
        return {
            "status": "error",
            "message": "Skill name must refer to a folder under .agent/skills.",
        }

    if not skill_file.exists():
        return {
            "status": "error",
            "message": f"Skill not found: {skill_name}",
            "available_skills": list_available_skills().get("skills", []),
        }

    return {
        "status": "success",
        "skill_name": skill_name,
        "content": skill_file.read_text(encoding="utf-8"),
    }


def score_startup_idea(
    clarity: int,
    pain_level: int,
    reachability: int,
    mvp_simplicity: int,
    willingness_to_pay: int,
) -> dict[str, Any]:
    """
    Score a startup idea using simple founder-friendly criteria.

    Each input must be from 1 to 5:
    - clarity: how clear the idea is
    - pain_level: how painful the problem is
    - reachability: how easy it is to reach target users
    - mvp_simplicity: how simple the first MVP is
    - willingness_to_pay: how likely users are to pay
    """
    values = {
        "clarity": clarity,
        "pain_level": pain_level,
        "reachability": reachability,
        "mvp_simplicity": mvp_simplicity,
        "willingness_to_pay": willingness_to_pay,
    }

    for key, value in values.items():
        if value < 1 or value > 5:
            return {
                "status": "error",
                "message": f"{key} must be between 1 and 5.",
            }

    total = sum(values.values())
    percentage = int((total / 25) * 100)

    if percentage >= 80:
        label = "Strong idea to validate"
    elif percentage >= 60:
        label = "Promising but needs sharper validation"
    elif percentage >= 40:
        label = "Unclear or risky; validate before building"
    else:
        label = "Too vague or too risky right now"

    return {
        "status": "success",
        "score": percentage,
        "label": label,
        "criteria": values,
    }


def create_validation_experiments(
    target_customer: str,
    startup_idea: str,
    budget_level: str = "low",
) -> dict[str, Any]:
    """
    Create three practical validation experiments for a startup idea.

    budget_level can be: low, medium, or high.

    Args:
        target_customer: The narrow customer segment to validate with.
        startup_idea: The startup idea being tested.
        budget_level: The expected budget level, such as low, medium, or high.

    Returns:
        A dictionary with status and a list of practical validation experiments.
    """
    experiments = [
        {
            "name": "Customer interview sprint",
            "goal": "Check whether the problem is painful and frequent.",
            "action": f"Interview 10 {target_customer} about the problem behind: {startup_idea}",
            "success_signal": "At least 6 out of 10 mention the pain without being pushed.",
            "time_box": "3 days",
            "budget": "low",
        },
        {
            "name": "Landing page smoke test",
            "goal": "Check whether people understand the value proposition.",
            "action": "Create a simple landing page with one CTA: Join waitlist or Book a demo.",
            "success_signal": "At least 5% visitor-to-signup conversion from relevant traffic.",
            "time_box": "7 days",
            "budget": budget_level,
        },
        {
            "name": "Manual concierge test",
            "goal": "Check whether the solution creates real value before building software.",
            "action": "Deliver the promised outcome manually for 3 potential users.",
            "success_signal": "At least 2 users ask to continue or ask about pricing.",
            "time_box": "7 days",
            "budget": "low",
        },
    ]

    return {
        "status": "success",
        "experiments": experiments,
    }


def save_startup_report(startup_name: str, markdown_report: str) -> dict[str, Any]:
    """
    Save the StartupSpark report as a Markdown file in the outputs folder.

    Args:
        startup_name: The startup or project name used to create a safe filename.
        markdown_report: The final Markdown report content to save.

    Returns:
        A dictionary with status and the saved file path.
    """
    OUTPUTS_DIR.mkdir(exist_ok=True)

    slug = _safe_slug(startup_name)
    output_path = OUTPUTS_DIR / f"{slug}.md"

    if not _path_is_relative_to(output_path, OUTPUTS_DIR):
        return {
            "status": "error",
            "message": "Output path must stay inside the outputs folder.",
        }

    output_path.write_text(markdown_report, encoding="utf-8")

    return {
        "status": "success",
        "path": str(output_path),
        "message": f"Report saved to {output_path}",
    }


STARTUP_SPARK_INSTRUCTION = """
You are StartupSpark, an AI startup validation agent.

Your job:
Help early-stage founders turn raw startup ideas into clear validation plans, MVP scope, landing page copy, and short founder pitches.

You are not a generic chatbot.
You are practical, honest, and founder-friendly.

Core behavior:
1. Read the user's startup idea carefully.
2. If the idea is too vague, ask 3 to 5 follow-up questions first.
3. If the idea is clear enough, generate a full StartupSpark Report.
4. Use the local skill files by folder name when helpful:
   - clarifying-startup-ideas
   - validating-startup-ideas
   - designing-mvps
   - writing-landing-pages
   - writing-founder-pitches
5. Use tools when useful:
   - list_available_skills
   - load_skill
   - score_startup_idea
   - create_validation_experiments
   - save_startup_report
6. Do not invent market statistics.
7. Do not promise startup success.
8. Do not give investment, legal, or financial advice.
9. Prefer validation before building.
10. Keep MVP suggestions small and realistic.

When producing the final answer, use this Markdown format:

# StartupSpark Report

## 1. Idea Summary

## 2. Target Customer

## 3. Pain Point

## 4. Value Proposition

## 5. MVP Scope

## 6. Landing Page Copy

### Headline

### Subheadline

### Benefits

### Call To Action

## 7. Validation Experiments

## 8. Risks

## 9. 7-Day Action Plan

## 10. Short Pitch

Do not add extra top-level sections beyond the 10 required sections.
Within the existing sections, include the biggest assumption the founder must validate first.

Important:
If the user asks to save the report, call save_startup_report.
"""


root_agent = Agent(
    model="gemini-2.5-flash",
    name="startup_spark_agent",
    description="Helps founders validate startup ideas and create MVP, landing page, validation, and pitch outputs.",
    instruction=STARTUP_SPARK_INSTRUCTION,
    tools=[
        list_available_skills,
        load_skill,
        score_startup_idea,
        create_validation_experiments,
        save_startup_report,
    ],
)
