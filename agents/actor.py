import uuid
from abc import ABC, abstractmethod
from typing import NewType

from agents.datas import MessageData, ActorData
from agents.observers.actor_observer import ActorObserver
from sources.controller_inputs import ControllerInput, InputType

ActorID = NewType("ActorID", str)


class Actor(ABC):
    """
    Actor represents a generic subject of the Architecture.

    It's a source of Inputs and Messages, but also reads Inputs and Messages of other Actors.

    An Actor is uniquely identified by its actor ID.
    """

    def __init__(self):
        self.id = ActorID(str(uuid.uuid4()))
        self.subscribers: list[ActorObserver] = []

    def get_id(self) -> ActorID:
        """ Returns the identifier for self """
        return self.id

    def subscribe(self, subscriber: ActorObserver) -> None:
        """ Adds a new subscriber to the list """
        self.subscribers.append(subscriber)

    def notify_input(self, input_data: ControllerInput, confidence: float) -> None:
        """ Notifies all the subscribers with an InputData object """
        data = ActorData(self.id, input_data, confidence)
        for subscriber in self.subscribers:
            subscriber.receive_input_update(data)

    def notify_message(self, message: str) -> None:
        """ Notifies all subscribers with a MessageData object """
        data = MessageData(self.id, message)
        for subscriber in self.subscribers:
            subscriber.receive_message_update(data)

    @abstractmethod
    def start(self) -> None:
        """ Starts the Actor. Called when the Arbitrator is started """
        pass

    @abstractmethod
    def get_controlled_inputs(self) -> list[InputType]:
        """ Returns the list of Input Types that the Actor is controlling. """
        pass

    @abstractmethod
    def get_arbitrated_inputs(self, input_data : ControllerInput) -> None:
        """ Receives the final Inputs produced by the Command Arbitrator and sent to the Game """
        pass


