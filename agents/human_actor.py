from ..sources import PhysicalControllerListener
from ..sources.controller import (
    ControllerInput,
    ControllerObserver,
    InputData,
    InputType,
)
from .actor import Actor
from ..sources.game import GameAction

ConfidenceLevels = dict[InputType, float]

InputToActionMap = dict[InputType, GameAction]

ActionToInputMap = dict[GameAction, InputType]


class HumanActor(Actor, ControllerObserver):
    """
    HumanActor is a particular type of Actor that represents a Human Player.

    The inputs it produces are read from a Physical Controller.
    """

    def __init__(
            self,
            physical_controller: PhysicalControllerListener,
            confidence_levels: ConfidenceLevels,
            human_input_to_action: InputToActionMap, # Converts the User Input into the desired Game Action
            action_to_game_input: ActionToInputMap, # Converts the Game Action into the corresponding expected Input
    ):
        super().__init__()
        self.controller = physical_controller
        self.confidence_levels = confidence_levels
        self.input_to_action = human_input_to_action
        self.action_to_game_input = action_to_game_input

        self.controller.subscribe(self)

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

    def get_controlled_actions(self) -> list[GameAction]:
        """Returns the list of Game Actions that the Actor is controlling."""

        # The Human controls all actions whose inputs have a specified confidence
        return [self.input_to_action[inp] for inp in self.input_to_action.keys()]

    def map_input(self, input_type: InputType) -> InputType:
        """Maps the User Input Type into the Game Input Type"""

        #TODO: check existence
        return self.action_to_game_input[self.input_to_action[input_type]]

    def receive_controller_input(self, data: InputData) -> None:
        """Receives an Input from the Controller and notifies it with the associated confidence level"""
        confidence = self.confidence_levels[data.c_input.type]
        self.notify_input(data.c_input, confidence)

    def get_arbitrated_inputs(self, input_data: ControllerInput) -> None:
        # Ignore Arbitrated Inputs at the moment
        pass
