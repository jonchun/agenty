# Agenty

A Pythonic framework for building AI agents and LLM pipelines, powered by [pydantic-ai](https://github.com/pydantic/pydantic-ai). The framework emphasizes simplicity and maintainability without sacrificing power, making it an ideal choice for rapid prototyping.

📚 **[Documentation](https://agenty.readthedocs.io/)**

> [!Caution]
> Agenty is under active development. Expect frequent breaking changes until we reach a stable release.

Agenty provides a clean, type-safe interface for creating:

-   Conversational AI agents with structured inputs and outputs
-   LLM pipelines
-   Complex agent interactions with minimal boilerplate

## Key Features

-   Built on pydantic-ai for type validation
-   Automatic conversation history management
-   Intuitive Pythonic interfaces

The framework is currently only officially tested with the OpenAI API (through a proxy such as [LiteLLM](https://docs.litellm.ai/docs/simple_proxy)/[OpenRouter](https://openrouter.ai/docs/quick-start)) although theoretically it supports all the models supported by pydantic-ai.

> [!TIP]
> Looking for a more mature alternative? Check out [atomic-agents](https://github.com/BrainBlend-AI/atomic-agents), which heavily inspired this project.

## Installation

```bash
pip install agenty
```

Or with uv:

```bash
uv add agenty
```

## Quick Preview

Here's a simple example to get started:

```python
import asyncio
from agenty import Agent
from agenty.models import OpenAIModel

async def main():
    agent = Agent(
        model=OpenAIModel(
            "gpt-4o",
            api_key="your-api-key"
        ),
        system_prompt="You are a helpful and friendly AI assistant."
    )

    response = await agent.run("Hello, how are you?")
    print(response)

asyncio.run(main())
```

In most cases, to build a custom AI agent, you'll want to create your own class that inherits from `Agent.` The below is functionally equivalent to the above code (and is the recommended way to use this framework)

```python
import asyncio
from agenty import Agent
from agenty.models import OpenAIModel

class Assistant(Agent):
    model = OpenAIModel("gpt-4o", api_key="your-api-key")
    system_prompt = "You are a helpful and friendly AI assistant."

async def main():
    agent = Assistant()
    response = await agent.run("Hello, how are you?")
    print(response)

asyncio.run(main())
```

---

### Tools

Add capabilities to your agents with simple decorators:

```python
class WeatherAgent(Agent):
    system_prompt = "You help users check the weather."

    def __init__(self, location: str):
        super().__init__()
        self.location = location
        self.temperature = 72  # Simulated temperature

    @tool
    def get_temperature(self) -> float:
        """Get the current temperature."""
        return self.temperature

    @tool
    def get_location(self) -> str:
        """Get the configured location."""
        return self.location
```

---

### Structured I/O

Define type-safe inputs and outputs for predictable behavior:

```python
from agenty import Agent
from agenty.types import BaseIO

class User(BaseIO):
    name: str
    age: int
    hobbies: List[str]

class UserExtractor(Agent[str, User]):
    input_schema = str
    output_schema = User
    system_prompt = "Extract user information from the text"
```

---

### Agent Pipelines

Chain multiple agents together for complex workflows:

```python
class TextCleaner(Agent[str, str]):
    model = OpenAIModel("gpt-4o-mini", api_key="your-api-key")
    system_prompt = "Clean and format the input text"

class SentimentAnalyzer(Agent[str, str]):
    model = OpenAIModel("gpt-4o-mini", api_key="your-api-key")
    system_prompt = "Analyze the sentiment of the text"

# Create and use the pipeline
pipeline = TextCleaner() | SentimentAnalyzer()
result = await pipeline.run("This is my input text!")
```

---

### Templates

Create dynamic prompts with Jinja templates:

```python
class DynamicGreeter(Agent):
    system_prompt = """
    You are a greeter who:
    - Speaks in a {{TONE}} tone
    - Gives {{LENGTH}} responses
    """
    TONE: str = "friendly"
    LENGTH: str = "concise"
```

---

### Hooks

Transform inputs and outputs with hooks:

```python
class MyAgent(Agent[str, str]):
    @hook.input
    def add_prefix(self, input: str) -> str:
        return f"prefix_{input}"

    @hook.output
    def add_suffix(self, output: str) -> str:
        return f"{output}_suffix"
```

### 📚 Like what you see? **[Read the Documentation](https://agenty.readthedocs.io/)** to learn more!

---

## Requirements

-   Python >= 3.12

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Jonathan Chun ([@jonchun](https://github.com/jonchun))
