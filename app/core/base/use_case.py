from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

OutputType = TypeVar("OutputType")

class BaseUseCase(ABC, Generic[OutputType]):
    """Abstract base class for all use cases (commands and queries)."""

    @abstractmethod
    def execute(self) -> OutputType:
        """Execute the use case logic and return the result."""
        raise NotImplementedError


class BaseCommand(BaseUseCase[OutputType]):
    """Base class for commands (write operations that mutate state)."""
    pass


class BaseQuery(BaseUseCase[OutputType]):
    """Base class for queries (read operations that don't mutate state)."""
    pass
