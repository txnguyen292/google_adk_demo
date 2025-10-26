from __future__ import annotations

from textwrap import dedent

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.function_tool import FunctionTool

from google_adk_test.settings import OpenAIConfig
from google_adk_test.tools import compute_basic_math


def build_math_agent(config: OpenAIConfig) -> Agent:
    """Factory for the reusable math specialist."""
    llm_kwargs = {"temperature": config.temperature}

    return Agent(
        name="math_agent",
        description=(
            "Solves arithmetic expressions (add, subtract, multiply, divide) "
            "by delegating all computation to a deterministic Python tool."
        ),
        instruction=dedent(
            """
            You are a meticulous math specialist.
            - Carefully rewrite the user request as an arithmetic expression using only +, -, *, /, numbers, and parentheses.
            - You MUST call the tool `compute_basic_math(expression=<expression>)` exactly once for every math request. Do not attempt to answer until the tool returns.
            - After the tool responds, summarize the normalized expression, walk through each item in `steps`, and present the final result with the `operations_count`. Explicitly address the orchestrator so it can continue the workflow. Make it clear that you are not addressing the end user.
            - If the request cannot be satisfied with the supported operations, explain the limitation.
            - When you are done, explicitly say "math agent complete" so the orchestrator knows you have finished.
            """
        ).strip(),
        tools=[FunctionTool(compute_basic_math)],
        model=LiteLlm(model=config.model, **llm_kwargs),
        disallow_transfer_to_parent=False,
        disallow_transfer_to_peers=True,
    )
