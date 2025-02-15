## Getting Started

This guide will help you create your first AI agent using agenty.

### Basic Usage

Here's a simple example to get started:

```python
import asyncio
from agenty import Agent
from agenty.models import OpenAIModel

async def main():
    agent = Agent(
        model=OpenAIModel(
            "gpt-4",
            api_key="your-api-key"
        ),
        system_prompt="You are a helpful and friendly AI assistant."
    )

    response = await agent.run("Hello, how are you?")
    print(response)

asyncio.run(main())
```

### Creating a Custom Agent

For most use cases, you'll want to create your own class that inherits from `Agent`. This is the recommended way to use the framework:

```python
import asyncio
from agenty import Agent
from agenty.models import OpenAIModel

class Assistant(Agent):
    model = OpenAIModel("gpt-4", api_key="your-api-key")
    system_prompt = "You are a helpful and friendly AI assistant."

async def main():
    agent = Assistant()
    response = await agent.run("Hello, how are you?")
    print(response)

asyncio.run(main())
```

### Adding Tools

You can enhance your agent with tools using a simple decorator pattern:

```python
import asyncio
import random
from agenty import Agent, tool
from agenty.models import OpenAIModel

class GameAgent(Agent):
    model = OpenAIModel("gpt-4", api_key="your-api-key")
    system_prompt = "You're a dice game. Use the roll_die tool when asked to roll."

    def __init__(self, num_sides: int = 6, **kwargs):
        super().__init__(**kwargs)
        self.num_sides = num_sides

    @tool
    def roll_die(self) -> int:
        """Roll a die and return the result."""
        return random.randint(1, self.num_sides)

async def main():
    agent = GameAgent()
    response = await agent.run("Please roll the die!")
    print(response)

asyncio.run(main())
```

### Environment Variables

It's recommended to use environment variables for API keys:

```python
import os
from agenty import Agent
from agenty.models import OpenAIModel

class Assistant(Agent):
    model = OpenAIModel(
        "gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    system_prompt = "You are a helpful AI assistant."
```

### Next Steps

-   Learn about [Agent Configuration](../documentation/agent_configuration.md)
-   Explore [Tools](../documentation/tools.md) and learn more
-   Ensure type safety with [Structured I/O](../documentation/structured_io.md)
-   Read about [Pipelines](../documentation/pipelines.md) for complex workflows
