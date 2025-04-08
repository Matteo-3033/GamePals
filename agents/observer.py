from abc import ABC, abstractmethod
from dataclasses import dataclass

from .actions import ActionInputWithConfidence
from .actor_id import ActorID


@dataclass
class ActorData:
    """
    The wrapper class of the Input Data sent to an Actor Observer.
    Note that the Actor always sends inputs in the globally-recognized format of the game actions (not actual input_types)
    """

    actor_id: ActorID
    data: ActionInputWithConfidence


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
    def on_input_update(self, actor_data: ActorData) -> None:
        """Receives Controller Inputs and the Confidence Level sent by an Actor"""
        pass

    @abstractmethod
    def on_message_update(self, message_data: MessageData) -> None:
        """Receives a message from the Copilot. Messages are usually Metacommands"""
        pass
