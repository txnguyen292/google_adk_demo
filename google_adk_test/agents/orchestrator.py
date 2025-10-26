from __future__ import annotations

from google.adk import Agent
from google.adk.agents.sequential_agent import SequentialAgent

from google_adk_test.settings import OpenAIConfig


def build_orchestrator(config: OpenAIConfig, *, sub_agents: list[Agent]) -> SequentialAgent:
    """Run the math specialist first, then (optionally) the poetry specialist."""
    return SequentialAgent(
        name="math_poetry_pipeline",
        description=(
            "Sequential pipeline that always executes the math agent before the poetry agent. "
            "If the user does not request creativity, the poetry agent should acknowledge that and exit quickly."
        ),
        sub_agents=sub_agents,
    )
