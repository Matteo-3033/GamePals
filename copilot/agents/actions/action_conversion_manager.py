import logging
from collections import defaultdict

from copilot.sources.controller import ControllerInput, InputType
from copilot.utils.configuration_handler import ConfigurationHandler

from .abstract_conversion_delegate import ActionConversionDelegate
from .action_input import ActionInput
from .game_action import GameAction
from .one_to_one_delegate import OneToOneDelegate

logger = logging.getLogger(__name__)


class ActionConversionManager:
    """
    This class is responsible for converting Game Actions to Controller Input Types and vice versa.

    By default, it maps each action to the first Input Type listed in the game configuration file, and each input to its corresponding actions.

    The class constructor accepts a list of ActionConversionDelegate instances that can be used to specify how the conversion should be handled for specific actions.
    This is useful, for example, in the case of a continuous action with values ranging from -1 to 1 that needs to be mapped to two buttons: in such cases, a BinaryConversionDelegate might be used.
    """

    def __init__(
        self,
        conversion_delegates: list[ActionConversionDelegate] | None = None,
    ) -> None:

        if conversion_delegates is None:
            conversion_delegates = list()

        self._action_to_delegate_map: dict[GameAction, ActionConversionDelegate] = {
            delegate.get_action(): delegate for delegate in conversion_delegates
        }

        self.config_handler = ConfigurationHandler()
        game_action = self.config_handler.get_game_action_type()
        for action in game_action:
            inputs = self.config_handler.action_to_game_input(action)

            if (
                inputs
                and len(inputs) > 1
                and action not in self._action_to_delegate_map
            ):
                logger.warning(
                    f"{action} action: Game actions mapped to multiple inputs should be handled by a Delegate; otherwise, only the first input will be used."
                )

            if action not in self._action_to_delegate_map:
                self._action_to_delegate_map[action] = OneToOneDelegate(action)

        self._input_to_delegate_map: dict[
            int, dict[InputType, ActionConversionDelegate]
        ] = defaultdict(dict)

        humans_count = self.config_handler.get_humans_count()
        for delegate in self._action_to_delegate_map.values():
            action = delegate.get_action()

            for user_idx in range(humans_count):

                user_inputs = self.config_handler.action_to_user_input(user_idx, action)
                if not user_inputs:
                    continue

                for user_input in user_inputs:
                    self._input_to_delegate_map[user_idx][user_input] = delegate

    def input_to_actions(
        self, user_idx: int, c_input: ControllerInput
    ) -> list[ActionInput]:
        """Maps the User Input Type into the corresponding Game Actions."""
        if c_input.type not in self._input_to_delegate_map[user_idx]:
            return list()

        return self._input_to_delegate_map[user_idx][c_input.type].convert_from_input(
            user_idx, c_input
        )

    def action_to_inputs(self, action_input: ActionInput) -> list[ControllerInput]:
        """Maps the Game Action into a list of Controller Input Types to activate."""

        return self._action_to_delegate_map[action_input.action].convert_to_inputs(
            action_input
        )
