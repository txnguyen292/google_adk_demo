"""Run a sample ADK agent and emit a graphviz DOT trace of the workflow."""

from __future__ import annotations

import asyncio
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from graphviz import Digraph

from google.adk.apps.app import App
from google.adk.artifacts.in_memory_artifact_service import (
    InMemoryArtifactService,
)
from google.adk.cli import agent_graph
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import (
    InMemorySessionService,
)
from google.adk.utils.context_utils import Aclosing
from google.genai import types

from google_adk_test import OpenAIConfig, build_math_orchestrator

# Load env vars (.env in repo root if present).
load_dotenv(find_dotenv())

TRACE_DIR = Path("traces")
TRACE_DIR.mkdir(exist_ok=True)


async def build_and_run(prompt: str) -> tuple[list, str, str, str]:
    """Run the math orchestrator once and return events + ids + dot path."""
    config = OpenAIConfig.from_env()
    config.apply()

    root_agent = build_math_orchestrator(config)
    # Use app_name="agents" to align with the default agent package name.
    app = App(name="agents", root_agent=root_agent)

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
    content = types.Content(role="user", parts=[types.Part(text=prompt)])

    events = []
    async with Aclosing(
        runner.run_async(
            user_id=session.user_id, session_id=session.id, new_message=content
        )
    ) as agen:
        async for event in agen:
            events.append(event)

    # Build highlight edges from the last event (tool calls/responses).
    highlights = []
    if events:
        last = events[-1]
        for fc in last.get_function_calls():
            highlights.append((last.author, fc.name))
        for fr in last.get_function_responses():
            highlights.append((fr.name, last.author))

    dot_src = ""
    dot_graph = await agent_graph.get_agent_graph(
        root_agent=root_agent, highlights_pairs=highlights
    )
    if dot_graph and isinstance(dot_graph, Digraph):
        dot_src = dot_graph.source

    dot_path = TRACE_DIR / "capital_trace.dot"
    dot_path.write_text(dot_src or "", encoding="utf-8")

    return events, session.id, events[-1].id if events else "", str(dot_path)


def main() -> None:
    prompt = "What is (12 + 4) / 2? Please also give a short poem."
    events, session_id, last_event_id, dot_path = asyncio.run(build_and_run(prompt))

    print(f"Session id: {session_id}")
    print(f"Last event id: {last_event_id}")
    print(f"Events generated: {len(events)}")
    print(f"DOT written to: {dot_path}")
    if dot_path:
        print("Render with: dot -Tpng -o traces/capital_trace.png", dot_path)
    print("Highlights in DOT correspond to edges from the final event's tool calls.")


if __name__ == "__main__":
    main()
