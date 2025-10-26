from __future__ import annotations

import asyncio
import sys
from typing import Iterable

import typer
from google.adk import Runner
from google.adk.artifacts.in_memory_artifact_service import (
    InMemoryArtifactService,
)
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.sessions.in_memory_session_service import (
    InMemorySessionService,
)
from google.genai import types
from loguru import logger
from rich.console import Console

from google_adk_test import OpenAIConfig, build_math_orchestrator


app = typer.Typer(help="Google ADK math orchestration demo.")
console = Console()


def iter_text_parts(content: types.Content | None) -> Iterable[str]:
    """Yield text fragments from an event content."""
    if not content or not content.parts:
        return
    for part in content.parts:
        if part.text:
            yield part.text


def print_event(event) -> None:
    """Display an ADK event with Rich styling."""
    text_segments = [
        segment.strip() for segment in iter_text_parts(event.content) if segment
    ]
    if text_segments:
        console.print(f"[bold]{event.author}[/] {' '.join(text_segments)}")

    for function_call in event.get_function_calls():
        console.print(
            "[cyan][tool-call][/cyan] "
            f"{function_call.name}({function_call.args})"
        )

    for function_response in event.get_function_responses():
        console.print(
            "[green][tool-response][/green] "
            f"{function_response.name}: {function_response.response}"
        )


def configure_logging(debug: bool) -> None:
    """Set up loguru sinks."""
    logger.remove()
    level = "DEBUG" if debug else "INFO"
    logger.add(sys.stderr, level=level)
    logger.debug("Logger initialized with level {}", level)


@app.command()
def run(
    prompt: str = typer.Argument(
        ...,
        help="User request, e.g. 'What is 12 / 3 + 4?'",
    ),
    session: str = typer.Option(
        "demo-session",
        "--session",
        "-s",
        help="Session identifier for ADK runner.",
    ),
    user: str = typer.Option(
        "demo-user",
        "--user",
        "-u",
        help="User identifier injected into the session.",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable verbose logging.",
    ),
) -> None:
    """Execute the orchestrator for a single user prompt."""
    configure_logging(debug)

    config = OpenAIConfig.from_env()
    logger.info("Using OpenAI model {}", config.model)

    orchestrator = build_math_orchestrator(config)

    session_service = InMemorySessionService()
    asyncio.run(
        session_service.create_session(
            app_name="agents",
            user_id=user,
            session_id=session,
        )
    )
    logger.debug("Session created for user='%s', session='%s'", user, session)

    runner = Runner(
        app_name="agents",
        agent=orchestrator,
        session_service=session_service,
        artifact_service=InMemoryArtifactService(),
        memory_service=InMemoryMemoryService(),
    )
    logger.debug("Runner initialized with session '{}'", session)

    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    events = runner.run(
        user_id=user,
        session_id=session,
        new_message=message,
    )

    for event in events:
        if event.author == "user":
            continue
        print_event(event)


if __name__ == "__main__":
    app()
