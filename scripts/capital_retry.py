"""Example: enforce ALL-CAPS capital names with retries using ADK LlmAgent."""

from __future__ import annotations

import argparse
import asyncio
from typing import Optional

from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from pydantic import BaseModel, Field, field_validator

from google.genai import types

from google.adk import Agent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.apps.app import App
from google.adk.artifacts.in_memory_artifact_service import (
    InMemoryArtifactService,
)
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import (
    InMemorySessionService,
)
from google.adk.utils.context_utils import Aclosing
from google.adk.models.llm_request import LlmRequest

from google_adk_test import OpenAIConfig

# Load environment variables from the repo .env explicitly, then fall back to search.
REPO_ENV = Path("/Users/gt132601/Desktop/gainwell/google_adk_demo/.env")
if REPO_ENV.exists():
    load_dotenv(REPO_ENV)
else:
    load_dotenv(find_dotenv())


class CapitalOut(BaseModel):
    """Simple schema enforcing ALL-CAPS capital city names."""

    capital: str = Field(description="Return the capital when given a country")

    @field_validator("capital", mode="after")
    def must_be_all_caps(cls, v: str) -> str:
        if v != v.upper():
            raise ValueError("Capital string should be all caps")
        return v


async def uppercase_via_llm(callback_context, llm_response):
    """Validate via CapitalOut; on failure, re-ask using the original prompt plus the error."""
    if not llm_response or not llm_response.content:
        return llm_response

    text = "".join(part.text or "" for part in (llm_response.content.parts or []))
    try:
        # If it validates, keep as-is.
        CapitalOut(capital=text)
        print("callback: validation succeeded without rewrite")
        return llm_response
    except Exception as e:
        error_msg = str(e)

    # Pull original user prompt from the callback context.
    user_parts = []
    if callback_context.user_content and callback_context.user_content.parts:
        for part in callback_context.user_content.parts:
            if part.text:
                user_parts.append(part.text)
    original_prompt = "\n".join(user_parts) if user_parts else ""

    print("callback: validation failed, rewriting via LLM with error + original prompt")
    rewrite_prompt = (
        f"The previous answer failed validation: {error_msg}\n"
        f"User question: {original_prompt}\n"
        f"Previous answer: {text}\n"
        "Fix the mistakes"
    )
    print(f"Current rewrite prompt: {rewrite_prompt}")
    model_obj = callback_context._invocation_context.agent.model
    req = LlmRequest(
        model=model_obj.model,
        contents=[types.Content(role="user", parts=[types.Part(text=rewrite_prompt)])],
    )

    rewritten = None
    async for resp in model_obj.generate_content_async(req, stream=False):
        rewritten = resp

    # Return the rewritten response if present; otherwise fall back to original.
    return rewritten or llm_response


def build_agent(config: OpenAIConfig) -> LlmAgent:
    """Construct a minimal LlmAgent with LiteLlm backend and a logging callback."""
    config.apply()
    return LlmAgent(
        name="capital_agent",
        description="Returns capital cities",
        instruction="Answer with the capital city name only, in lowercase.",
        model=LiteLlm(model=config.model, temperature=config.temperature),
        after_model_callback=uppercase_via_llm,
    )


async def run_once(agent: Agent, country: str) -> str:
    """Run the agent once and return the raw text response."""
    app = App(name="capital_caps_agent", root_agent=agent)
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()
    artifact_service = InMemoryArtifactService()
    runner = Runner(
        app=app,
        session_service=session_service,
        memory_service=memory_service,
        artifact_service=artifact_service,
    )

    session = await session_service.create_session(
        app_name=app.name, user_id="demo", session_id="demo-session"
    )
    prompt = (
        f"What is the capital of {country}? "
        "Return only the city name in ALL CAPS."
    )
    content = types.Content(role="user", parts=[types.Part(text=prompt)])

    text = ""
    async with Aclosing(
        runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        )
    ) as agen:
        async for event in agen:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        text += part.text
    return text.strip()


async def run_with_validation(
    country: str, max_retries: int = 3, model: Optional[str] = None
) -> CapitalOut:
    """Retry until the capital passes validation or retries are exhausted."""
    config = OpenAIConfig.from_env()
    if model:
        config.model = model
    agent = build_agent(config)
    reminder = (
        " Reminder: respond ONLY with the capital city name in ALL CAPS."
    )
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt}")
        raw = await run_once(agent, country)
        print("LLM raw output:", raw)
        try:
            return CapitalOut(capital=raw)
        except ValueError as e:
            last_error = e
            print("Validation failed:", e)
            # Reinforce instruction for the next attempt.
            agent.instruction = agent.instruction + reminder
    raise last_error or RuntimeError("Validation failed")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Get a capital city in ALL CAPS with validation + retries."
    )
    parser.add_argument("country", help="Country name, e.g., France")
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Max retries on validation failure (default: 3)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Optional model override (defaults to OPENAI_MODEL or project default).",
    )
    args = parser.parse_args()

    result = asyncio.run(
        run_with_validation(
            country=args.country,
            max_retries=args.retries,
            model=args.model,
        )
    )
    print("Validated capital:", result.capital)


if __name__ == "__main__":
    main()
