import tomllib

from agents import InputData, MessageData, ActorData
from agents.actor import Actor
from agents.observers.controller_observer import ControllerObserver
from sources import InputType, ControllerInput
from sources.physical_controller_listener import PhysicalControllerListener


class HumanActor(Actor, ControllerObserver):
    """
    HumanActor is a particular type of Actor that represents a Human Player.

    The inputs it produces are read from a Physical Controller.
    """

    def __init__(self, physical_controller: PhysicalControllerListener, config_file_path: str):
        super().__init__()
        self.controller = physical_controller
        self.confidence_levels: dict[InputType, float] = {}

        self.controller.subscribe(self)

        with open(config_file_path, 'rb') as config_file:
            config = tomllib.load(config_file)
            # Confidence is the complement of Assistance
            self.confidence_levels = {t: 1 - v for t, v in config["AssistanceLevels"].items()}

    def start(self) -> None:
        """
        Starts listening to the Physical Controller.
        Before doing so, it informs its subscribers of the confidence levels specified (this is needed to apply a
        correct Arbitration from the start)
        """

        # Notify all subscribers of the Confidence Levels (using zero-value inputs)
        for key, value in self.confidence_levels.items():
            zero_input = ControllerInput(type=key, val=0)
            self.notify_input(zero_input, value)

        self.controller.start_listening()

    def get_controlled_inputs(self) -> list[InputType]:
        """ Returns the list of Input Types that the Actor is controlling.  """

        # Considers as controlled all inputs which have a Confidence > 0.0 (Assistance < 1.0 in the config file)
        return [t for t, conf in self.confidence_levels.items() if conf > 0.0]

    def receive_controller_input(self, data: InputData) -> None:
        """ Receives an Input from the Controller and notifies it with the associated confidence level """
        confidence = self.confidence_levels[data.c_input.type]
        self.notify_input(data.c_input, confidence)

    def receive_input_update(self, data: ActorData) -> None:
        """ Receives Inputs from other Actors """
        pass

    def receive_message_update(self, data: MessageData) -> None:
        """
        Receives Messages from other Actors
        TODO: add a game overlay or some form of voice/visual notification for the Human Actor
        """
        pass

    def get_arbitrated_inputs(self, input_data: ControllerInput) -> None:
        # Ignore Arbitrated Inputs at the moment
        pass