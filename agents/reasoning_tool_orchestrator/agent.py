from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from google.adk.apps.app import App

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from google_adk_test import OpenAIConfig, build_reasoning_tool_orchestrator  # noqa: E402


def _build_root_agent():
    config = OpenAIConfig.from_env()
    logger.info("Loading reasoning tool orchestrator with %s", config.model)
    return build_reasoning_tool_orchestrator(config)


root_agent = _build_root_agent()
app = App(name="reasoning_tool_orchestrator", root_agent=root_agent)
