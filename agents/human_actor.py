import logging

from ..sources import PhysicalControllerListener
from ..sources.controller import ControllerInput, ControllerObserver, InputData
from .actions import ActionConversionDelegate, ActionInput, GameAction
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
        conversion_delegates: list[ActionConversionDelegate] | None = None,
    ) -> None:
        super().__init__()
        if conversion_delegates is None:
            conversion_delegates = list()

        self.controller = physical_controller
        self.confidence_levels: dict[GameAction, float] = (
            self.config_handler.get_confidence_levels(self.controller.get_index())
        )

        self.conversion_delegates: dict[GameAction, ActionConversionDelegate] = {
            delegate.get_action(): delegate for delegate in conversion_delegates
        }

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

    def on_controller_input(self, data: InputData) -> None:
        """Receives an Input from the Controller and notifies it with the associated confidence level"""

        # Before sending, it converts the user input into the game input
        action_input = self.input_to_action(data.c_input)

        if action_input is None:
            return

        confidence = self.confidence_levels[action_input.action]
        self.notify_input(action_input, confidence)

    def input_to_action(self, c_input: ControllerInput) -> ActionInput | None:
        """Maps the User Input Type into the Game Action. Return None to ignore the input (i.e. unrecognized)"""
        action = self.config_handler.user_input_to_action(
            self.get_index(), c_input.type
        )

        if action is None:
            return None

        if action in self.conversion_delegates:
            # Check if the Action is handled by a Delegate
            # This is useful for Actions that are mapped to multiple inputs (eg: both triggers)
            return self.conversion_delegates[action].convert_from_input(
                self.get_index(), c_input
            )

        return ActionInput(action=action, val=c_input.val)

    def on_arbitrated_inputs(self, input_data: ControllerInput) -> None:
        # Ignore Arbitrated Inputs at the moment
        pass
