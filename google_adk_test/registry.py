from __future__ import annotations

from textwrap import dedent

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

from google_adk_test.agents import (
    build_math_agent,
    build_orchestrator,
    build_poetry_agent,
    build_synthesizer_agent,
    build_math_tool_agent,
    build_poetry_tool_agent,
)
from google_adk_test.settings import OpenAIConfig


def _build_specialists(config: OpenAIConfig) -> tuple[Agent, Agent, Agent]:
    math_agent = build_math_agent(config)
    poetry_agent = build_poetry_agent(config)
    synth_agent = build_synthesizer_agent(config)
    return math_agent, poetry_agent, synth_agent


def build_math_orchestrator(config: OpenAIConfig) -> Agent:
    """Deterministic math → poetry → synthesizer pipeline."""
    config.apply()
    math_agent, poetry_agent, synth_agent = _build_specialists(config)
    return build_orchestrator(
        config,
        sub_agents=[math_agent, poetry_agent, synth_agent],
    )


def build_reasoning_tool_orchestrator(config: OpenAIConfig) -> Agent:
    """LLM orchestrator that invokes math/poetry as tools and synthesizer as a sub-agent."""
    config.apply()

    math_tool = build_math_tool_agent(config)
    poetry_tool = build_poetry_tool_agent(config)
    synth_agent = build_synthesizer_agent(config)

    return Agent(
        name="reasoning_tool_orchestrator",
        description="Uses math/poetry tools and delegates final messaging to the synthesizer agent.",
        instruction=dedent(
            """
            You must solve requests by calling tools and delegating the final answer to the synthesizer agent.
            - `math_agent` tool: send the arithmetic expression and wait for its JSON result.
            - `poetry_agent` tool: call ONLY after math succeeds and only if the user wants creativity.
            - `synthesizer_agent`: transfer to this agent LAST so it can merge the math (and optional poem) into the final user response.

            Workflow:
              1. Determine if the user needs math. If not, respond directly.
              2. For math, call `math_agent` with the full expression and capture the result.
              3. Optionally call `poetry_agent` for creative output.
              4. Transfer to `synthesizer_agent`, providing the original prompt plus the math/poetry context. Do NOT craft the final answer yourself.
            """
        ).strip(),
        tools=[math_tool, poetry_tool],
        sub_agents=[synth_agent],
        model=LiteLlm(model=config.model, temperature=config.temperature),
        disallow_transfer_to_parent=True,
    )
