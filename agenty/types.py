from typing import Union, Tuple, Sequence, Any, Type, get_origin, get_args, List

from typing_extensions import TypeVar

from pydantic import BaseModel
from rich.json import JSON

__all__ = [
    "BaseIO",
    "AgentIO",
    "AgentIOBase",
    "AgentInputT",
    "AgentOutputT",
]


class BaseIO(BaseModel):
    """Base class for all agent input/output models.

    This class extends Pydantic's BaseModel to represent basic IO between agents. All structured
    input/output models should inherit from this class.
    """

    def __str__(self) -> str:
        """Convert the model to a JSON string.

        Returns:
            str: JSON string representation of the model
        """
        return self.model_dump_json()

    def __rich__(self) -> JSON:
        """Create a rich console representation of the model.

        Returns:
            JSON: Rich-formatted JSON representation
        """
        json_str = self.model_dump_json()
        return JSON(json_str)


AgentIOBase = Union[
    bool,
    int,
    float,
    str,
    BaseIO,
]
"""Union type for basic agent I/O types.

This type represents the allowed primitive types and BaseIO models that can be
used for agent inputs and outputs.
"""

AgentIO = Union[AgentIOBase, Sequence[AgentIOBase]]
"""All supported data types for agent communication.

Extends the core types (AgentIOBase) to also support sequences/lists of those types.
"""

AgentInputT = TypeVar(
    "AgentInputT",
    bound=AgentIO,
    default=str,
)
"""Type variable for agent input types.

This type variable is used for generic agent implementations to specify their input schema
"""

AgentOutputT = TypeVar(
    "AgentOutputT",
    bound=AgentIO,
    default=str,
)
"""Type variable for agent output types.

This type variable is used for generic agent implementations to specify their output schema
"""

PipelineOutputT = TypeVar(
    "PipelineOutputT",
    bound=AgentIO,
    default=str,
)


class NOT_GIVEN:
    """Sentinel class used to distinguish between unset and None values."""

    ...


NOT_GIVEN_ = NOT_GIVEN()


def normalize_type(type_: Any) -> Tuple[Type, Tuple[Any]]:
    """Normalize a type annotation to a standard form."""
    # If there's no origin, return the type itself
    origin = get_origin(type_) or type_
    args = get_args(type_)
    return (origin, args)
