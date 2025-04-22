import logging
from collections import defaultdict

from copilot.sources.controller import ControllerInput, InputType
from copilot.utils.configuration_handler import ConfigurationHandler

from .abstract_conversion_delegate import ActionConversionDelegate
from .action_input import ActionInput
from .default_action_to_input_delegate import DefaultActionToInputDelegate
from .game_action import GameAction

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

        _action_and_user_to_delegate_map: dict[
            tuple[GameAction, int], ActionConversionDelegate
        ] = {
            (action, delegate.get_user_idx()): delegate
            for delegate in conversion_delegates
            for action in delegate.get_actions()
        }

        self._action_to_delegate_map: dict[GameAction, ActionConversionDelegate] = {
            action: delegate
            for delegate in conversion_delegates
            for action in delegate.get_actions()
        }

        self.config_handler = ConfigurationHandler()

        self._input_to_delegate_map: dict[
            int, dict[InputType, ActionConversionDelegate]
        ] = defaultdict(dict)

        humans_count = self.config_handler.get_humans_count()
        game_action_enum = self.config_handler.get_game_action_type()
        for user_idx in range(humans_count):
            for action in game_action_enum:

                if (action, user_idx) in _action_and_user_to_delegate_map:
                    delegate = _action_and_user_to_delegate_map[(action, user_idx)]
                else:
                    delegate = DefaultActionToInputDelegate(user_idx, [action])

                user_inputs = self.config_handler.action_to_user_input(user_idx, action)
                if not user_inputs:
                    continue
                for user_input in user_inputs:
                    self._input_to_delegate_map[user_idx][user_input] = delegate

                if action not in self._action_to_delegate_map:
                    self._action_to_delegate_map[action] = delegate


    def input_to_actions(
        self, user_idx: int, c_input: ControllerInput | None
    ) -> list[ActionInput]:
        """
        Registers the new User Input into the Delegates (if c_input is not None),
        then collects ready Action Inputs from all Delegates of the specified user_idx.
        """

        if c_input:
            # Register the new input in the corresponding Delegate
            if c_input.type in self._input_to_delegate_map[user_idx]:
                delegate = self._input_to_delegate_map[user_idx][c_input.type]
                delegate.register_input(c_input)

        # Ask all Delegates for any Action ready to be executed
        actions: list[ActionInput] = list()

        for delegate in self._input_to_delegate_map[user_idx].values():
            actions.extend(delegate.get_ready_actions())

        return actions

    def action_to_inputs(self, action_input: ActionInput) -> list[ControllerInput]:
        """Maps the Game Action into a list of Controller Input Types to activate."""

        return self._action_to_delegate_map[action_input.action].convert_to_inputs(
            action_input
        )
