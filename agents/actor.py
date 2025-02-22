from abc import ABC, abstractmethod

from agents import MessageData, ActorData
from agents.observers.actor_observer import ActorObserver
from input_sources import ControllerInput, InputType


class Actor(ActorObserver, ABC):
    """
    Actor represents a generic subject of the Architecture.

    It's a source of Inputs and Messages, but also reads Inputs and Messages of other Actors.
    """

    def __init__(self):
        self.subscribers: list[ActorObserver] = []

    def subscribe(self, subscriber: ActorObserver) -> None:
        """ Adds a new subscriber to the list """
        self.subscribers.append(subscriber)

    def notify_input(self, input_data : ControllerInput, confidence : float) -> None:
        """ Notifies all the subscribers with an InputData """
        data = ActorData(input_data, confidence)
        for subscriber in self.subscribers:
            subscriber.receive_input_update(data)

    def notify_message(self, message : str) -> None:
        """ Notifies all subscribers with a MessageData """
        data = MessageData(message)
        for subscriber in self.subscribers:
            subscriber.receive_message_update(data)

    @abstractmethod
    def start(self) -> None:
        """ Starts the Actor (if needed). """
        pass

    @abstractmethod
    def get_controlled_inputs(self) -> list[InputType]:
        """ Returns the list of Input Types that the Actor is controlling. """
        pass
