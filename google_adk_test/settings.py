from __future__ import annotations

import os
from dataclasses import dataclass

import litellm

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.2

@dataclass(slots=True)
class OpenAIConfig:
    """Runtime configuration for using OpenAI models via google-adk."""

    api_key: str
    model: str = DEFAULT_MODEL
    temperature: float = DEFAULT_TEMPERATURE

    @classmethod
    def from_env(cls) -> "OpenAIConfig":
        """Build configuration from environment variables."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY not found in the environment. "
                "Set it before running the demo."
            )

        model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
        temperature_raw = os.getenv("OPENAI_TEMPERATURE", str(DEFAULT_TEMPERATURE))
        try:
            temperature = float(temperature_raw)
        except ValueError as exc:  # pragma: no cover - defensive guard
            raise ValueError(
                f"OPENAI_TEMPERATURE must be numeric, got '{temperature_raw}'."
            ) from exc

        return cls(api_key=api_key, model=model, temperature=temperature)

    def apply(self) -> None:
        """Ensure downstream libraries see the OpenAI credentials."""
        os.environ.setdefault("OPENAI_API_KEY", self.api_key)
        os.environ.setdefault("OPENAI_MODEL", self.model)
        # Disable TLS verification for LiteLLM to match local notebook usage.
        litellm.ssl_verify = False
