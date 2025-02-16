from dataclasses import dataclass
from typing import Callable, Generic, TypeVar
from game_controllers.utils import ControllerInput

# Callback-Based Observer Pattern Implementation of a Generic Input Source

@dataclass
class SourceData:
    pass

@dataclass
class InputData(SourceData):
    input : ControllerInput

@dataclass
class PilotInputData(SourceData):
    input : ControllerInput
    assistance_level : float
    
@dataclass
class CopilotInputData(SourceData):
    input : ControllerInput
    confidence_level : float
    
@dataclass
class MessageData(SourceData):
    message : str


T = TypeVar("T", bound=SourceData)
class InputSource(Generic[T]):
    """
    A generic InputSource class that maintains a list of subscribers.
    Subscribers are callable objects that take an argument of type T and return None. 
    """

    def __init__(self):
        self.subscribers: list[Callable[[T], None]] = [] # Subscribers are methods that take an argument T and return None

    def subscribe(self, observer: Callable[[T], None]) -> None:
        """Adds an observer to the subscriber list."""
        self.subscribers.append(observer)

    def notify_all(self, data : T) -> None:
        """Notifies all subscribers by calling their 'update' method with given arguments."""
        for subscriber in self.subscribers:
            subscriber(data)
    