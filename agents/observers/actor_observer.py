from abc import ABC, abstractmethod

from ..datas import ActorData, MessageData


class ActorObserver(ABC):
    """
    The ActorObserver interface represents a class that receives Controller Inputs and messages from an Actor.
    """

    @abstractmethod
    def receive_input_update(self, data: ActorData) -> None:
        """ Receives Controller Inputs and the Confidence Level sent by an Actor """
        pass

    @abstractmethod
    def receive_message_update(self, data: MessageData) -> None:
        """ Receives a message from the Copilot. Messages are usually Metacommands """
        pass
