import logging

from .action_input import ActionInput
from ..sources import PhysicalControllerListener
from ..sources.controller import (
    ControllerInput,
    ControllerObserver,
    InputData,
    InputType,
)
from .actor import Actor
from ..sources.game import GameAction

ConfidenceLevels = dict[GameAction, float]

logger = logging.getLogger(__file__)

class HumanActor(Actor, ControllerObserver):
    """
    HumanActor is a particular type of Actor that represents a Human Player.

    The inputs it produces are read from a Physical Controller and mapped into Game Actions for global understanding.
    """

    def __init__(
            self,
            physical_controller: PhysicalControllerListener
    ) -> None:
        super().__init__()
        self.controller = physical_controller
        self.confidence_levels : ConfidenceLevels = self.config_handler.get_confidence_levels(self.controller.get_index())

        self.controller.subscribe(self)

    def get_index(self) -> int:
        """Returns the index with which the HumanActor is identified in the configuration"""
        return self.controller.get_index()

    def start(self) -> None:
        """
        Starts listening to the Physical Controller.
        Before doing so, it informs its subscribers of the confidence levels specified (this is needed to apply a
        correct Arbitration from the start)
        """

        # Notify all subscribers of the Confidence Levels (using zero-value inputs) <-- Needed for correct arbitration
        for key, value in self.confidence_levels.items():
            zero_input = ActionInput(action=key, val=0)
            self.notify_input(zero_input, value)

        self.controller.start_listening()

    def get_controlled_actions(self) -> list[GameAction]:
        """Returns the list of Game Actions that the Actor is controlling."""
        return self.config_handler.get_controlled_actions(self.controller.get_index())

    def receive_controller_input(self, data: InputData) -> None:
        """Receives an Input from the Controller and notifies it with the associated confidence level"""

        # Before sending, it converts the user input into the game input
        action = self.input_to_action(data.c_input.type)

        if action is None:
            logger.warning("The input %s is not recognized as a game action. Ignored", data.c_input.type)
            return

        game_input_data = ActionInput(
            action,
            data.c_input.val,
        )

        confidence = self.confidence_levels[action]
        self.notify_input(game_input_data, confidence)

    def input_to_action(self, input_type: InputType) -> GameAction:
        """Maps the User Input Type into the Game Action"""
        return self.config_handler.user_input_to_action(self.get_index(), input_type)

    def get_arbitrated_inputs(self, input_data: ControllerInput) -> None:
        # Ignore Arbitrated Inputs at the moment
        pass
