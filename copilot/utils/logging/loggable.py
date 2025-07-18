from abc import abstractmethod
from typing import Any


class Loggable:
    """Loggable is the interface for every class that wants to be logged"""

    @classmethod
    def get_tag(cls) -> str:
        """Returns the tag associated with the class"""
        return cls.__name__

    @abstractmethod
    def get_json(self) -> dict[str, Any] | list[Any]:
        """Returns the json to log"""
        pass
