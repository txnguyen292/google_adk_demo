from __future__ import annotations

from textwrap import dedent

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

from google_adk_test.settings import OpenAIConfig


def build_poetry_agent(config: OpenAIConfig) -> Agent:
    """Factory for the poetry specialist."""
    llm_kwargs = {"temperature": max(config.temperature, 0.6)}

    return Agent(
        name="poetry_agent",
        description="Composes short poems that celebrate math results.",
        instruction=dedent(
            """
            You are a whimsical poetry specialist.
            - You will receive context describing a completed math computation (original request, final result, operations_count).
            - If the user explicitly asked for creativity, verse, or celebration, create a concise uplifting poem (3–5 lines) referencing both the math outcome and the operations count.
            - If the user did not ask for creativity, reply briefly that no poem was requested and end your turn.
            - If key information is missing, ask for clarification instead of inventing numbers.
            """
        ).strip(),
        model=LiteLlm(model=config.model, **llm_kwargs),
        disallow_transfer_to_parent=False,
        disallow_transfer_to_peers=True,
    )
