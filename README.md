## Google ADK Demo Agents

This project showcases a small fleet of [Google Agentic Development Kit (ADK)](https://github.com/google/adk-python) agents powered by OpenAI via LiteLLM:

- **Math specialist** – rewrites arithmetic into a deterministic Python tool call and walks through the computation.
- **Poetry specialist** – celebrates the math result in verse when creativity is requested.
- **Synthesizer** – assembles the final human-facing answer.
- **Reasoning orchestrator** – decides which specialists or tools to involve.
- **OCR transcriber** – extracts text from uploaded images and formats a clean transcription.

These agents are available both as a CLI demo and in the ADK web UI.

---

## Prerequisites

- macOS (tested) with `zsh`
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management
- OpenAI API key with access to GPT-4 family models (the defaults target `gpt-4o-mini`)

If you operate behind an TLS-intercepting proxy, export the relevant CA bundle (or set `litellm.ssl_verify = False` only if required in controlled environments).

---

## Installation

Clone the repo and install dependencies using uv:

```bash
git clone https://github.com/txnguyen292/google_adk_demo.git
cd google_adk_demo
uv sync
```

The project installs as an editable package (`google-adk-test==0.1.0`). The `uv sync` command also prepares a `.venv` in the repository root; activate it when running commands manually:

```bash
source .venv/bin/activate
```

---

## Configuration

Set these environment variables before calling any agents (either export them in your shell or place them in a `.env` file; the repo uses `python-dotenv` in notebooks and agents for convenience):

| Variable | Purpose | Default |
| --- | --- | --- |
| `OPENAI_API_KEY` | API key passed to LiteLLM/OpenAI | required |
| `OPENAI_MODEL` | Model name for all agents | `gpt-4o-mini` |
| `OPENAI_TEMPERATURE` | Base sampling temperature | `0.2` |

Example (macOS/zsh):

```bash
export OPENAI_API_KEY="sk-your-key"
export OPENAI_MODEL="gpt-4o-mini"
```

Or create a `.env` in the project root:

```
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.2
```

The ADK apps and notebooks load `.env` automatically if present.

The demo also sets `litellm.ssl_verify = False` during configuration so requests succeed in restrictive corporate networks. If you import the proxy’s root CA instead, remove that override in `google_adk_test/settings.py` for better security.

---

## Command-Line Demo

Run the orchestrator on a single prompt:

```bash
uv run python main.py "What is (12 + 4) / 2?"
```

You will see streamed events from each agent, including tool calls and final summaries. Non-math requests are gracefully declined.

---

## ADK Web Apps

Launch the built-in ADK UI and choose the desired app from the dropdown:

```bash
uv run adk web agents
```

The following app names are registered:

| App | What it does |
| --- | --- |
| `math_orchestrator` | Deterministic math → poetry → synthesizer pipeline. |
| `reasoning_tool_orchestrator` | LLM-controlled reasoning flow that invokes math/poetry as tools and hands off to the synthesizer. |
| `ocr_transcriber` | OCR agent that reuses the latest uploaded image and returns the detected text + notes. |

**OCR tips:** Upload an image (PNG/JPEG) and optionally add textual instructions in the same turn. The agent stores the most recent image in session state, so follow-up messages can reference it without re-uploading.

---

## Notebook Usage

`notebooks/test.ipynb` demonstrates direct OpenAI calls with custom TLS settings and LiteLLM usage (`litellm.ssl_verify = False`). Run it inside the project’s virtualenv to reuse installed dependencies.

---

## Project Layout

| Path | Description |
| --- | --- |
| `main.py` | Minimal CLI entry point for the orchestrator demo. |
| `google_adk_test/settings.py` | Loads OpenAI configuration and toggles LiteLLM TLS handling. |
| `google_adk_test/agents/` | Specialist factories (math, poetry, synthesizer, OCR). |
| `google_adk_test/agents/tool_wrappers.py` | Wraps agents as tools for orchestrators. |
| `google_adk_test/registry.py` | Builds orchestrators and exposes the OCR agent builder. |
| `agents/*/agent.py` | Web-app entry points loaded by `adk web agents`. |
| `project_specs/initial_requirements.md` | Original requirements used to scope the demo. |

---

## Extending the Demo

- Add new specialists by following the pattern in `google_adk_test/agents/` and register them in `google_adk_test/registry.py`.
- Attach tools via `google_adk_test/agents/tool_wrappers.py` to expose existing agents as callable functions.
- Update `agents/<app>/agent.py` (or create new folders) to surface additional workflows in the ADK web UI.

Feel free to experiment—the ADK stack makes it straightforward to sequence or orchestrate new agent behaviors around LiteLLM-compatible models.
