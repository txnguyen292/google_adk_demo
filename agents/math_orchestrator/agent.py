from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from google.adk.apps.app import App

from google_adk_test import OpenAIConfig, build_math_orchestrator  # noqa: E402


def _build_root_agent():
    config = OpenAIConfig.from_env()
    logger.info(f"Loading math orchestrator for ADK web UI with {config.model}")
    return build_math_orchestrator(config)


root_agent = _build_root_agent()
app = App(name="math_orchestrator", root_agent=root_agent)
