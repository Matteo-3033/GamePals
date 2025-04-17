import uuid
from abc import ABC, abstractmethod

from copilot.sources.controller import ControllerInput
from copilot.utils.configuration_handler import ConfigurationHandler

from .actions import ActionInput, ActionInputWithConfidence, GameAction
from .actor_id import ActorID
from .observer import ActorData, ActorObserver, MessageData


class Actor(ABC):
    """
    Actor represents a generic subject of the Architecture.

    It's a source of Inputs and Messages, but also reads Inputs and Messages of other Actors.

    An Actor is uniquely identified by its actor ActorID.
    """

    def __init__(self):

        self.id = ActorID(str(uuid.uuid4()))
        self.subscribers: list[ActorObserver] = []
        self.config_handler = ConfigurationHandler()

    def get_id(self) -> ActorID:
        """Returns the identifier for self"""
        return self.id

    def subscribe(self, subscriber: ActorObserver) -> None:
        """Adds a new subscriber to the list"""
        self.subscribers.append(subscriber)

    def notify_input(self, actor_data: ActionInput, confidence: float) -> None:
        """Notifies all the subscribers with an ActionInputWithConfidence object"""
        data = ActorData(
            self.id,
            ActionInputWithConfidence(actor_data.action, actor_data.val, confidence),
        )
        for subscriber in self.subscribers:
            subscriber.on_input_update(data)

    def notify_message(self, message: str) -> None:
        """Notifies all subscribers with a MessageData object"""
        data = MessageData(self.id, message)
        for subscriber in self.subscribers:
            subscriber.on_message_update(data)

    @abstractmethod
    def start(self) -> None:
        """Starts the Actor. Called when the Arbitrator is started"""
        pass

    @abstractmethod
    def get_controlled_actions(self) -> list[GameAction]:
        """Returns the list of Game Actions that the Actor is able to control"""
        pass

    @abstractmethod
    def on_arbitrated_inputs(self, input_data: ControllerInput) -> None:
        """Receives the final Inputs produced by the Command Arbitrator and sent to the Game"""
        pass
