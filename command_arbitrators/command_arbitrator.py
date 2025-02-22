from agents import MessageData, ActorData
from agents.actor import Actor
from agents.observers.actor_observer import ActorObserver
from input_sources import ControllerInput
from input_sources.virtual_controller_provider import VirtualControllerProvider


class CommandArbitrator(ActorObserver):
    """
    The CommandArbitrator class is an abstract Arbitrator.

    It arbitrates between inputs from different sources and sends the final command to a Virtual Controller.
    """

    def __init__(self) -> None:
        self.virtual_controller: VirtualControllerProvider = VirtualControllerProvider()
        self.actors: list[Actor] = []

    def add_actor(self, actor: Actor) -> None:
        """ Adds an Actor to the Architecture """
        self.actors.append(actor)
        actor.subscribe(self)  # Subscribe the Arbitrator to all the Actors

    def start(self) -> None:
        """ Starts the Actors and the Arbitration Process """
        for actor in self.actors:
            actor.start()

    def receive_input_update(self, data: ActorData) -> None:
        """ Receives Input and Confidence Level from one of its Actors """
        pass

    def receive_message_update(self, data: MessageData) -> None:
        """ Receives a Message from one of its Actors """
        pass

    def execute_binary_command(self, input: ControllerInput) -> None:
        """
        Executes a single-value command on the Virtual Controller
        """
        print(f"Executing {input}")
        self.virtual_controller.execute(input)

    def execute_continuous_command(self, input_x: ControllerInput, input_y: ControllerInput) -> None:
        """
        Executes a 2-axis command on the Virtual Controller
        """
        print(f"Executing {input_x} {input_y} ")
        self.virtual_controller.execute_stick(input_x, input_y)
