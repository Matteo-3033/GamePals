from typing import Any

from ..command_arbitrators.policies import PolicyName
from ..sources.controller import InputType
from ..sources.game import GameAction


class ConfigurationHandler:
    _instance: 'ConfigurationHandler' = None

    def __new__(
            cls,
            game_config: dict[str, Any] | None = None,
            agents_config: dict[str, Any] | None = None,
            assistance_config: dict[str, Any] | None = None,
    ) -> 'ConfigurationHandler':

        if game_config is None: game_config = {}
        if agents_config is None: agents_config = {}
        if assistance_config is None: assistance_config = {}

        if cls._instance is None:
            cls._instance = super(ConfigurationHandler, cls).__new__(cls)
            cls._instance._load_config_from_dicts(
                game_config,
                agents_config,
                assistance_config,
            )
        return cls._instance

    def _load_config_from_dicts(
            self,
            game_config: dict[str, Any],
            agents_config: dict[str, Any],
            assistance_config: dict[str, Any],
    ) -> None:
        self.game_config = game_config
        self.agents_config = agents_config
        self.assistance_config = assistance_config

    def get_policy_types(
            self
    ) -> dict[InputType, PolicyName]:
        pass

    def get_confidence_levels(
            self,
            user_id: int
    ) -> dict[InputType, float]:
        pass

    def get_controlled_actions(
            self,
            user_id: int
    ) -> list[GameAction]:
        pass

    def user_input_to_action(
            self,
            user_id: int,
            input_type: InputType,
    ) -> GameAction:
        # TODO: check in the assistance_config for the line that looks like
        # { id = user_id, ..., control = input_type } and return the action
        pass

    def action_to_user_input(
            self,
            user_id: int,
            action: GameAction,
    ) -> InputType:
        # TODO: the opposite
        pass

    def game_input_to_action(
            self,
            input_type: InputType
    ) -> GameAction:
        # TODO: check file1 and file3
        pass

    def action_to_game_input(
            self,
            action: GameAction,
    ) -> InputType:
        # TODO: check file1
        pass

    def game_input_to_user_input(
            self,
            user_id: int,
            input_type: InputType,
    ) -> InputType:
        return self.action_to_user_input(user_id, self.game_input_to_action(input_type))

    def user_input_to_game_input(
            self,
            user_id: int,
            input_type: InputType,
    ) -> InputType:
        return self.action_to_game_input(self.user_input_to_action(user_id, input_type))



"""
Class handles configuration. It's a singleton

What it needs to do:
- Translate from User Input to Game Action (by different Human) and viceversa
- Translate from Game Action to Game Input and viceversa
- Returns the list of Copilots or something like that

"""
