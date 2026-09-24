from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Base interface for all tools.

    This abstract class defines the contract that all tool wrappers
    must implement, enabling easy swapping of tool implementations.
    """

    @abstractmethod
    def get_tool_instance(self) -> Any:
        """Return the actual tool instance.

        Returns:
            Tool instance compatible with agents SDK
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name identifier.

        Returns:
            String name of the tool
        """
        pass
