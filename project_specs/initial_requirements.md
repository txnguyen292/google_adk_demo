## Google ADK Math Orchestration – Implementation Guidelines

### 1. Project Vision
- Build a minimal, demonstrable agentic workflow on top of the **Google Agentic Development Kit (ADK)**.
- Use OpenAI LLMs for reasoning while exercising ADK’s orchestration, state, and tool abstractions.
- Showcase a practical two-agent pattern (router + specialist) that can be extended later to additional skills.

### 2. Scope & Assumptions
- **In scope**
  - One “orchestrator” agent that receives user prompts, classifies intent, and delegates.
  - One “math specialist” agent that executes deterministic arithmetic (add, subtract, multiply, divide) via an ADK Python tool.
  - CLI entry point (or script) that wires agents, tools, and LLM configuration through google-adk APIs.
  - Configurable OpenAI model & credentials (via env vars or config file).
- **Out of scope (for now)**
  - Google Workspace/Vertex AI connectors.
  - Persistence beyond ADK’s default memory store.
  - Advanced routing, planning, or monitoring.

### 3. Functional Requirements
1. **Agent Composition**
   - Define agents using `google_adk.core` primitives (e.g., `Agent`, `Orchestrator`, `Tool` abstractions).
   - Orchestrator must inspect incoming text, decide if it’s a supported math query, and either delegate to the math agent or respond with a reminder of capabilities.
2. **Math Specialist**
   - Implement a Python callable exposed as an ADK tool, capable of performing the four basic operations with input validation and error handling (e.g., division by zero).
   - Provide reasoning/step trace: expression evaluated + final numeric output.
3. **LLM Configuration**
   - Use OpenAI models via ADK’s model adapters (`google_adk.integrations.openai`).
   - Allow overriding model name, API base, temperature through environment variables.
4. **Runner**
   - Provide a script or CLI (e.g., `python main.py "2 + 2"`) that initializes the ADK runtime, registers agents/tools, and streams the conversation result to stdout.
   - Include helpful logs (e.g., which agent handled the request, tool invocations, errors).
5. **Fallback Behaviour**
   - Non-math prompts must lead to a graceful message describing supported operations.
   - Surface validation errors back to the user in plain language.

### 4. Non-Functional Requirements
- Clean, modular code with docstrings and minimal but clear comments.
- Leverage ADK’s built-in logging/monitoring hooks where straightforward.
- Ensure the project remains runnable via `uv run` (created by `uv add google-adk`).

### 5. Environment & Tooling
- Dependency management: `uv` (already initialized; `google-adk` added as default dependency).
- Recommended env vars (document in README later):
  - `OPENAI_API_KEY` (required)
  - `OPENAI_MODEL` (default: `gpt-4o-mini` or similar)
  - `OPENAI_TEMPERATURE` (default: `0.2`)
- Optional: support `.env` loading via `python-dotenv` if convenient.

### 6. Deliverables
- Implementation aligned with requirements above.
- Updated documentation (README or dedicated file) describing setup, configuration, and usage.
- Example prompts demonstrating math success and fallback behaviour.

### 7. Acceptance Criteria
- Running the entry script with a math prompt returns correct computation (verified manually).
- Non-math prompt returns capability reminder.
- No unhandled exceptions during normal usage.
- Code passes linting/format expectations (if tooling available) or at minimum `python -m compileall` sanity check.

Use this document as the authoritative checklist while implementing the google-adk based workflow.
