# smolagents Integration

The [smolagents](https://github.com/huggingface/smolagents) integration allows you to use `CodeAgent` from smolagents as part of your agenty workflow. This integration provides a powerful way to create agents that can execute Python code, perform web searches, and handle complex computational tasks.

## CodeAgent

The `CodeAgent` is a wrapper around `smolagents.CodeAgent` that integrates seamlessly with agenty. It works out of the box and can be configured with any smolagents tools.

For a complete working example, see [examples/smol/code_agent.py](https://github.com/jonchun/agenty/blob/main/examples/smol/code_agent.py).

### Configuration

The `CodeAgent` accepts the following parameters:

-   `model`: An instance of a language model (Same as any other `agenty` agent)
-   `input_schema`: The type for input validation (Same as any other `agenty` agent -- recommended to use `str`)
-   `output_schema`: The type for output validation (Same as any other `agenty` agent -- recommended to use `str`)
-   `smol_tools`: A list of smol tools to make available to the agent (e.g., `PythonInterpreterTool`, `DuckDuckGoSearchTool`)
-   `smol_verbosity_level`: Integer controlling the verbosity of smol output (0 for minimal, 2 for detailed)
-   `smol_grammar`: Optional dictionary of grammar rules for code generation
-   `smol_additional_authorized_imports`: Optional list of additional Python imports to allow
-   `smol_planning_interval`: Optional integer for planning steps interval
-   `smol_use_e2b_executor`: Boolean flag to use e2b code executor (default: False)
-   `smol_max_print_outputs_length`: Optional integer for maximum length of print outputs

### Example Usage

Here's a basic example of using `CodeAgent` with OpenAI:

```python
import asyncio
import os
from agenty.models import OpenAIModel
from agenty.integrations.smol import CodeAgent
from agenty.integrations.smol.tools import DuckDuckGoSearchTool, PythonInterpreterTool

async def main() -> None:
    code_agent: CodeAgent[str, float] = CodeAgent(
        model=OpenAIModel(
            "gpt-4",
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key"),
            base_url=os.getenv("OPENAI_API_URL", "https://api.openai.com/v1"),
        ),
        smol_tools=[DuckDuckGoSearchTool(), PythonInterpreterTool()],
        smol_verbosity_level=1,  # 0 for minimal output, 2 for detailed
        input_schema=str,
        output_schema=float,
        # Optional advanced configuration
        smol_grammar=None,  # Custom grammar rules for code generation
        smol_additional_authorized_imports=None,  # Additional allowed Python imports
        smol_planning_interval=None,  # Interval for planning steps
        smol_use_e2b_executor=False,  # Whether to use e2b code executor
        smol_max_print_outputs_length=None,  # Max length of print outputs
    )

    query = ('How many seconds would it take for a leopard at full speed '
            'to run through Pont des Arts?')
    result = await code_agent.run(query)
    print(f"Response: {result}, Type: {type(result)}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Supported Models

The `CodeAgent` supports the following model providers:

-   OpenAI: Using `OpenAIModel` with custom base URL and organization support
-   Anthropic: Using `AnthropicModel` (via LiteLLM)
-   Groq: Using `GroqModel` (via LiteLLM)
-   Cohere: Using `CohereModel` (via LiteLLM, requires COHERE_API_KEY environment variable)
-   Mistral: Using `MistralModel` (via LiteLLM)
