import asyncio
from typing import Generic, Type, Optional, Union, List, Callable, cast, Any, Dict
import logging

from pydantic import TypeAdapter, ValidationError
import pydantic_ai as pai
from pydantic_ai.agent import EndStrategy

from agenty.models import infer_model, KnownModelName, Model, ModelSettings
from agenty.types import (
    AgentInputT,
    AgentOutputT,
    PipelineOutputT,
    AgentIO,
    NOT_GIVEN,
    NotGiven,
)
from agenty.template import apply_template
from agenty.protocol import AgentIOProtocol
from agenty.pipeline import Pipeline

import agenty.exceptions as exc

from .meta import AgentMeta
from .chat_history import ChatHistory, ChatMessage

__all__ = ["Agent", "EndStrategy"]

logger = logging.getLogger(__name__)


class Agent(Generic[AgentInputT, AgentOutputT], metaclass=AgentMeta):
    # agenty
    name: str = ""
    system_prompt: str = ""
    input_schema: Type[AgentIO] = str
    output_schema: Type[AgentIO] = str
    chat_history: ChatHistory

    # pydantic-ai
    model: Optional[Model] = None
    model_settings: Optional[ModelSettings] = None
    retries: int = 1
    result_retries: Optional[int] = None
    end_strategy: EndStrategy = "early"

    _pai_agent: Optional[pai.Agent["Agent[AgentInputT, AgentOutputT]", AgentIO]]
    _input_hooks: List[
        Callable[["Agent[AgentInputT, AgentOutputT]", AgentInputT], AgentInputT]
    ]
    _output_hooks: List[
        Callable[["Agent[AgentInputT, AgentOutputT]", AgentOutputT], AgentOutputT]
    ]

    def __init__(
        self,
        model: Union[KnownModelName, Model, NotGiven, None] = NOT_GIVEN,
        model_settings: Union[Optional[ModelSettings], NotGiven] = NOT_GIVEN,
        name: Union[str, NotGiven] = NOT_GIVEN,
        system_prompt: Union[str, NotGiven] = NOT_GIVEN,
        input_schema: Union[Type[AgentIO], NotGiven] = NOT_GIVEN,
        output_schema: Union[Type[AgentIO], NotGiven] = NOT_GIVEN,
        retries: Union[int, NotGiven] = NOT_GIVEN,
        result_retries: Union[Optional[int], NotGiven] = NOT_GIVEN,
        end_strategy: Union[EndStrategy, NotGiven] = NOT_GIVEN,
        chat_history: Union[ChatHistory, NotGiven] = NOT_GIVEN,
        # usage: Optional[AgentUsage] = None,
        # usage_limits: Optional[AgentUsageLimits] = None,
    ) -> None:
        _create_pai_agent = False
        # infer model so that we always have a Model instance or None
        if not isinstance(model, NotGiven):
            if model is None:
                self.model = None
            else:
                self.model = infer_model(model)
                _create_pai_agent = True

        if not isinstance(name, NotGiven):
            self.name = name
        if not isinstance(system_prompt, NotGiven):
            self.system_prompt = system_prompt
        if not isinstance(input_schema, NotGiven):
            self.input_schema = input_schema
        if isinstance(chat_history, NotGiven):
            self.chat_history = ChatHistory()
        else:
            self.chat_history = chat_history
        # self.usage = usage or AgentUsage()
        # self.usage_limits = usage_limits or AgentUsageLimits()

        # If any of these attributes are not NOT_GIVEN, set them and create an object-specific pydantic-ai agent
        create_pai_agent_attributes = {
            "model_settings": model_settings,
            "output_schema": output_schema,
            "retries": retries,
            "result_retries": result_retries,
            "end_strategy": end_strategy,
        }
        for attr, val in create_pai_agent_attributes.items():
            if val is not None and not isinstance(val, NotGiven):
                setattr(self, attr, val)
                _create_pai_agent = True

        if _create_pai_agent and self.model is not None:
            logger.debug("Creating object-specific pydantic-ai agent")
            self._pai_agent = None
            if model is not None:
                self._pai_agent = pai.Agent(
                    self.model,
                    result_type=self.output_schema,
                    deps_type=self.__class__,
                    model_settings=self.model_settings,
                    retries=self.retries,
                    result_retries=self.result_retries,
                    end_strategy=self.end_strategy,
                )

    async def run(
        self,
        input_data: Optional[AgentInputT],
        name: Optional[str] = None,
    ) -> AgentOutputT:
        """Run the agent with the provided input.

        Args:
            input_data: The input data for the agent to process

        Returns:
            The processed output data
        """

        _chat_history = self.chat_history.to_pydantic_ai(ctx=self.template_context())
        _input_data: Any = input_data
        if _input_data is not None:
            for input_hook in self._input_hooks:
                _type: Any = type(_input_data)
                _input_data = input_hook(self, _input_data)
                if not isinstance(_input_data, _type):
                    raise exc.AgentyValueError(
                        f"Input hook {input_hook.__name__} returned invalid type"
                    )
            try:
                TypeAdapter(self.input_schema).validate_python(input_data)
            except ValidationError as e:
                raise exc.AgentyTypeError(e)
            self.chat_history.add("user", _input_data, name=name)

        system_prompt = ChatMessage(
            role="system", content=self.system_prompt
        ).to_pydantic_ai(ctx=self.template_context())

        try:
            output = await self.pai_agent.run(
                str(_input_data),
                message_history=[system_prompt] + _chat_history,
                deps=self,
            )
        except pai.exceptions.UnexpectedModelBehavior as e:
            raise exc.InvalidResponse(e)

        _output_data: Any = output.data
        for output_hook in self._output_hooks:
            _type = type(_output_data)
            _output_data = output_hook(self, _output_data)
            if not isinstance(_output_data, _type):
                raise exc.AgentyValueError(
                    f"Output hook {output_hook.__name__} returned invalid type"
                )

        self.chat_history.add("assistant", _output_data, name=name)
        return cast(AgentOutputT, _output_data)

    def run_sync(
        self,
        input_data: Optional[AgentInputT],
        name: Optional[str] = None,
    ) -> AgentOutputT:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop:
            return loop.run_until_complete(
                asyncio.create_task(self.run(input_data, name))
            )
        else:
            return asyncio.run(self.run(input_data, name))

    @property
    def model_name(self) -> str:
        """Get the name of the current model.

        Returns:
            str: The model name

        Raises:
            ValueError: If no model is set
        """
        if self.model is None:
            return ""

        return self.model.name()

    @property
    def pai_agent(self) -> pai.Agent["Agent[AgentInputT, AgentOutputT]", AgentIO]:
        """Get the underlying pydantic-ai agent instance.

        Returns:
            pai.Agent: The pydantic-ai agent instance
        """
        if self.model is None:
            raise exc.AgentyAttributeError("Model is not set")
        if self._pai_agent is None:
            raise exc.AgentyAttributeError("Pydantic AI agent does not exist")
        return self._pai_agent

    @property
    def system_prompt_rendered(self) -> str:
        """Render the system prompt with the current template context.

        Returns:
            str: The rendered system prompt
        """
        return apply_template(self.system_prompt, self.template_context())

    def template_context(self) -> Dict[str, Any]:
        """Get a dictionary of instance variables for use in templates. By default, this includes all variables that start with an uppercase letter.

        Returns:
            Dict[str, Any]: Dictionary of variables
        """
        return {key: getattr(self, key) for key in dir(self) if key[0].isupper()}

    def reset(self) -> None:
        """Reset the agent to its initial state."""
        self.chat_history.clear()

    def __or__(
        self, other: AgentIOProtocol[AgentOutputT, PipelineOutputT]
    ) -> AgentIOProtocol[AgentInputT, PipelineOutputT]:
        """Chain this agent with another using the | operator.

        Args:
            other: Another agent to chain with. Its input schema must match this agent's output schema.

        Returns:
            A new Pipeline instance containing both agents, preserving type information.
        """
        return Pipeline[AgentInputT, PipelineOutputT](
            agents=[self, other],
            input_schema=self.input_schema,
            output_schema=other.output_schema,
        )
