import logging

from copilot.sources import PhysicalControllerListener
from copilot.sources.controller import ControllerInput, ControllerObserver, InputData

from .actions import ActionConversionManager, ActionInput, GameAction
from .actor import Actor

logger = logging.getLogger(__file__)


class HumanActor(Actor, ControllerObserver):
    """
    HumanActor is a particular type of Actor that represents a Human Player.

    The inputs it produces are read from a Physical Controller and mapped into Game Actions for global understanding.
    """

    def __init__(
        self,
        physical_controller: PhysicalControllerListener,
        conversion_manager: ActionConversionManager,
    ) -> None:
        super().__init__()

        self.controller = physical_controller
        self.confidence_levels: dict[GameAction, float] = (
            self.config_handler.get_confidence_levels(self.controller.get_index())
        )

        self.conversion_manager : ActionConversionManager = conversion_manager

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

    def on_controller_update(self, data: InputData | None) -> None:
        """Receives an Input from the Controller and notifies it with the associated confidence level"""

        update_data = data.c_input if data else None
        
        # Before sending, it converts the user input into the game inputs
        action_inputs = self.conversion_manager.input_to_actions(
            self.get_index(), update_data
        )

        for action_input in action_inputs:
            confidence = self.confidence_levels[action_input.action]
            self.notify_input(action_input, confidence)

    def on_arbitrated_inputs(self, input_data: ControllerInput) -> None:
        # Ignore Arbitrated Inputs at the moment
        pass
