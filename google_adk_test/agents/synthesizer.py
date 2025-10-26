from __future__ import annotations

from textwrap import dedent

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

from google_adk_test.settings import OpenAIConfig


def build_synthesizer_agent(config: OpenAIConfig) -> Agent:
    """Produces a final user-facing answer using math + poetry context."""
    llm_kwargs = {"temperature": config.temperature}

    return Agent(
        name="synthesizer_agent",
        description="Aggregates outputs from other agents and produces the final human-friendly response.",
        instruction=dedent(
            """
            You are the final narrator.
            - Review the latest replies from math_agent and poetry_agent (if present).
            - Provide a clear numeric summary of the math result, mentioning the number of operations when available.
            - If a poem was provided, quote or paraphrase it in a friendly way; otherwise simply mention that no poem was requested.
            - Close with actionable or encouraging language so the user has a complete answer in one message.
            """
        ).strip(),
        model=LiteLlm(model=config.model, **llm_kwargs),
        disallow_transfer_to_parent=False,
        disallow_transfer_to_peers=True,
    )
