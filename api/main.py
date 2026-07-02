from __future__ import annotations

import os
import re
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.adk.runners import InMemoryRunner
from google.genai import types
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENT_ENV_PATH = PROJECT_ROOT / "startup_spark_agent" / ".env"
APP_NAME = "startup_spark_agent"
REQUIRED_REPORT_SECTIONS = (
    "Idea Summary",
    "Target Customer",
    "Pain Point",
    "Value Proposition",
    "MVP Scope",
    "Landing Page Copy",
    "Validation Experiments",
    "Risks",
    "7-Day Action Plan",
    "Short Pitch",
)


class ReportContractError(RuntimeError):
    pass


def _load_local_env(env_path: Path) -> None:
    """Load simple KEY=VALUE pairs from the local agent .env without overriding env vars."""
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


_load_local_env(AGENT_ENV_PATH)

from startup_spark_agent.agent import root_agent  # noqa: E402


class GenerateReportRequest(BaseModel):
    idea: Annotated[
        str,
        Field(
            min_length=10,
            max_length=5000,
            description="Raw startup idea text supplied by the founder.",
        ),
    ]
    save_as: Annotated[
        str | None,
        Field(
            max_length=80,
            description="Optional output filename hint for the agent's save tool.",
        ),
    ] = None


class GenerateReportResponse(BaseModel):
    report: str


app = FastAPI(
    title="StartupSpark API",
    description="Local FastAPI wrapper around the existing StartupSpark ADK agent.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def _build_prompt(idea: str, save_as: str | None) -> str:
    prompt = (
        "Create a StartupSpark report for this startup idea.\n\n"
        f"{idea.strip()}\n\n"
        "Return the final answer as Markdown using the required 10 sections."
    )

    if save_as:
        prompt += (
            "\n\nAlso save the report using the save_startup_report tool "
            f"with this startup_name: {save_as.strip()}"
        )

    return prompt


def _normalize_section_title(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^\s{0,3}#{1,6}\s+", "", value)
    value = re.sub(r"\s*#+\s*$", "", value)
    value = value.strip("*_ ")
    value = re.sub(r"^\d+\.\s*", "", value)
    value = value.rstrip(":").strip()
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _missing_report_sections(markdown: str) -> list[str]:
    found_sections = {
        _normalize_section_title(line)
        for line in markdown.splitlines()
        if _normalize_section_title(line)
    }

    return [
        section
        for section in REQUIRED_REPORT_SECTIONS
        if _normalize_section_title(section) not in found_sections
    ]


async def _run_startup_spark_agent(prompt: str) -> str:
    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
    user_id = "ui-user"
    session_id = f"ui-{uuid.uuid4().hex}"

    await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)],
    )

    final_responses: list[str] = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            text_parts = [
                part.text
                for part in event.content.parts
                if getattr(part, "text", None)
            ]
            response_text = "\n".join(text_parts).strip()
            if response_text and response_text not in final_responses:
                final_responses.append(response_text)

    final_text = "\n\n".join(final_responses).strip()

    if not final_text:
        raise RuntimeError("The ADK agent did not return a final text response.")

    missing_sections = _missing_report_sections(final_text)
    if missing_sections:
        raise ReportContractError(
            "The ADK agent returned an incomplete report. Missing sections: "
            + ", ".join(missing_sections)
        )

    return final_text


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/generate-report", response_model=GenerateReportResponse)
async def generate_report(request: GenerateReportRequest) -> GenerateReportResponse:
    try:
        report = await _run_startup_spark_agent(
            _build_prompt(request.idea, request.save_as)
        )
    except ReportContractError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "StartupSpark could not generate a report. Check that your local "
                "ADK credentials and model configuration are available."
            ),
        ) from exc

    return GenerateReportResponse(report=report)
