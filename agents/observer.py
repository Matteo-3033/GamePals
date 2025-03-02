from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..sources.controller import ControllerInput
from .actor_id import ActorID


@dataclass
class ActorData:
    """The wrapper class of the Input Data sent to an Actor Observer"""

    actor_id: ActorID
    c_input: ControllerInput
    confidence: float


@dataclass
class MessageData:
    """The wrapper class of the String Data sent to an Actor Observer"""

    actor_id: ActorID
    message: str


class ActorObserver(ABC):
    """
    The ActorObserver interface represents a class that receives Controller Inputs and messages from an Actor.
    """

    @abstractmethod
    def receive_input_update(self, data: ActorData) -> None:
        """Receives Controller Inputs and the Confidence Level sent by an Actor"""
        pass

    @abstractmethod
    def receive_message_update(self, data: MessageData) -> None:
        """Receives a message from the Copilot. Messages are usually Metacommands"""
        pass
