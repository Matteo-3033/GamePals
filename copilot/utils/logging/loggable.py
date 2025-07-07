from abc import abstractmethod
from typing import Any


class Loggable:
    """Loggable is the interface for every class that wants to be logged"""

    @classmethod
    def get_tag(cls) -> str:
        """The tag associated with the class"""
        return cls.__name__

    @abstractmethod
    def get_json(self) -> dict[str, Any] | list[Any]:
        """The json to log"""
        pass

