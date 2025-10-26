## Google ADK Math Demo

This repository demonstrates how to orchestrate a lightweight, multi-agent workflow using the [Google Agentic Development Kit (ADK)](https://github.com/google/adk-python) with OpenAI models.

- **Orchestrator agent** – inspects each user request, decides when to involve specialists, and stitches the final response together.
- **Math agent** – calls a deterministic Python tool (`compute_basic_math`) to solve full arithmetic expressions (with multiple operations and parentheses).
- **Poetry agent** – turns the math journey into a short poem that references the number of operations performed.
- **Synthesizer agent** – reads the math/poetry outputs and crafts the final human-friendly response.

### Quick start

```bash
uv run python main.py "What is 12 / 3 + 4?"
```

> **Note:** If you run into OpenAI authentication errors, export `OPENAI_API_KEY` (and optionally `OPENAI_MODEL`) in your shell first.

Set the following environment variables before running:

| Variable | Purpose | Default |
| --- | --- | --- |
| `OPENAI_API_KEY` | Authenticates calls made through ADK’s LiteLLM integration. | – |
| `OPENAI_MODEL` | Model identifier passed to LiteLLM. | `gpt-4o-mini` |
| `OPENAI_TEMPERATURE` | Optional generation temperature for both agents. | `0.2` |

### Project layout

| Path | Description |
| --- | --- |
| `google_adk_test/agents/` | Individual agent factories (math, poetry, orchestrator). |
| `google_adk_test/registry.py` | Assembles the orchestrator with its specialists. |
| `google_adk_test/tools.py` | Deterministic arithmetic tool exposed to the LLM. |
| `google_adk_test/settings.py` | Reads OpenAI configuration from the environment. |
| `main.py` | CLI runner that spins up the ADK `Runner` and streams responses. |
| `project_specs/initial_requirements.md` | Implementation guidelines for the demo. |

### Example

```
$ uv run python main.py "Compute (5 + 7) * 3 / 2"
[orchestrator] I’ll ask our math specialist to evaluate: (5 + 7) * 3 / 2
[tool-call] compute_basic_math({'expression': '(5 + 7) * 3 / 2'})
[tool-response] compute_basic_math: {'expression': '(5 + 7) * 3 / 2', 'result': 18.0, 'operations_count': 3, 'steps': ['5 = 5.0', '7 = 7.0', '5 + 7 = 12.0', '3 = 3.0', '(5 + 7) * 3 = 36.0', '2 = 2.0', '((5 + 7) * 3) ÷ 2 = 18.0']}
[math_agent] Expression: (5 + 7) * 3 / 2  
 - Step 1: 5 + 7 = 12.0  
 - Step 2: 12.0 × 3 = 36.0  
 - Step 3: 36.0 ÷ 2 = 18.0  
Result: 18.0 (3 operations)  
[poetry_agent] In three swift turns the numbers spun,  
Twelve embraced three—now eighteen won.  
Steps entwined like rhythmic art,  
Math’s small waltz now warms the heart.
[orchestrator] Summary: the calculation evaluates to 18.0 using 3 operations. Enjoy the poem above!
```

For non-math questions:

```
$ uv run python main.py "Write me a poem"
[orchestrator] I can only help with addition, subtraction, multiplication, or division problems.
```

### ADK Web UI

Once your environment variables are in place, you can explore the same agents through the built-in web experience:

```bash
uv run adk web agents/math_orchestrator          # deterministic math → poetry pipeline
uv run adk web agents/reasoning_tool_orchestrator # LLM orchestrator that calls specialists as tools
```

Open the provided URL in a browser to interact with the orchestrator visually.

### Available workflows

| App | Description | When to use |
| --- | --- | --- |
| `math_orchestrator` | Sequential pipeline: math → poetry → synthesizer (poetry politely declines if not requested, synthesizer always produces the final response). | Deterministic demos or regression tests. |
| `reasoning_tool_orchestrator` | LLM orchestrator that uses math/poetry as tools and always transfers to the synthesizer agent for the final user-facing response. | Showcases dynamic routing and tool use. |

Feel free to extend the toolset or add more specialist agents (percentages, unit conversion, etc.) by following the pattern in `google_adk_test/agents.py`.
