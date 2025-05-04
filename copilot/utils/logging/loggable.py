from abc import abstractmethod


class Loggable:
    """Loggable is the interface for every class that wants to be logged"""

    @classmethod
    def get_tag(cls) -> str:
        """The tag associated with the class"""
        return cls.__name__

    @abstractmethod
    def get_log(self) -> str:
        """The log of the class"""
        pass

