from typing import Any

from copilot.sources.controller import InputType
from copilot.sources.game import GameAction


class ConfigurationHandler:

    _instance : 'ConfigurationHandler' = None

    def __new__(
            cls,
            game_config : dict[str, Any] = dict(),
            agents_config : dict[str, Any] = dict(),
            assistance_config : dict[str, Any] = dict(),
    ) -> 'ConfigurationHandler':
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
            game_config : dict[str, Any],
            agents_config : dict[str, Any],
            assistance_config : dict[str, Any],
    ) -> None:
        self.game_config = game_config
        self.agents_config = agents_config
        self.assistance_config = assistance_config

    def user_input_to_action(
            self,
            user_id : int,
            input_type : InputType,
    ) -> GameAction :
        # TODO: check in the assistance_config for the line that looks like
        # { id = user_id, ..., control = input_type } and return the action
        pass

    def action_to_user_input(
            self,
            user_id : int,
            action : GameAction,
    ) -> InputType :
        # TODO: the opposite
        pass

    def action_to_game_input(
            self,
            action : GameAction,
    ) -> InputType :
        # TODO: check file1
        pass

    def game_input_to_action(
            self,
            input_type : InputType
    ) -> GameAction :
        # TODO: check file1 and file3
        pass


"""
Class handles configuration. It's a singleton

What it needs to do:
- Translate from User Input to Game Action (by different Human) and viceversa
- Translate from Game Action to Game Input and viceversa
- Returns the list of Copilots or something like that

"""