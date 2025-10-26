from __future__ import annotations

from google.adk import Agent
from google.adk.tools.agent_tool import AgentTool

from google_adk_test.agents.math import build_math_agent
from google_adk_test.agents.poetry import build_poetry_agent
from google_adk_test.settings import OpenAIConfig


def build_math_tool_agent(config: OpenAIConfig) -> AgentTool:
    """Wrap math agent as a tool for orchestration."""
    return AgentTool(build_math_agent(config), skip_summarization=False)


def build_poetry_tool_agent(config: OpenAIConfig) -> AgentTool:
    """Wrap poetry agent as a tool."""
    return AgentTool(build_poetry_agent(config), skip_summarization=False)

