from typing import Any, TYPE_CHECKING
from collections import defaultdict

if TYPE_CHECKING:
    from ..command_arbitrators.policies import PolicyName
    from ..sources.controller.controller_inputs import InputType
    from ..sources.game.game_action import GameAction



class ConfigurationHandler:
    """


    TODO: implement default values for the config
    TODO: eventually split x and y axis into up and down
    TODO: configuring meta-commands
    """
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

        #TODO: Configuration Validation should go here

        self.confidence_levels: dict[int, dict['InputType', float]] = defaultdict()
        self.user_actions: dict[int, list['GameAction']] = defaultdict()
        self.policy_types: dict['InputType', 'PolicyName'] = defaultdict()

        self.user_input_to_action_map: dict[int, dict['InputType', 'GameAction']] = defaultdict()
        self.action_to_user_input_map: dict[int, dict['GameAction', 'InputType']] = defaultdict()
        self.game_input_to_action_map: dict['InputType', 'GameAction'] = defaultdict()
        self.action_to_game_input_map: dict['GameAction', 'InputType'] = defaultdict()


        for action in assistance_config.get("action", []):
            for human in action.get("humans", []):

                self.user_actions[human["id"]].append(action["name"])
                controls = human.get("controls", [])

                for control in controls:
                    self.confidence_levels[human["id"]][control] = human["confidence"]
                    self.user_input_to_action_map[human["id"]][control] = action["name"]

                if len(controls) > 0:
                    # Knowing one input for each action is enough
                    self.action_to_user_input_map[human["id"]][action["name"]] = controls[0]

            if action["name"] in game_config.get("actions", {}):
                for game_input in game_config["actions"][action["name"]]:
                    self.policy_types[game_input] = action["policy"]

        for action, inputs in game_config.get("actions", {}).items():

            self.action_to_game_input_map[action] = inputs[0]  # Knowing one input for each action is enough

            for game_input in inputs:
                self.game_input_to_action_map[game_input] = action

    def get_policy_types(
            self
    ) -> dict['InputType', 'PolicyName']:
        return self.policy_types

    def get_confidence_levels(
            self,
            user_id: int
    ) -> dict['InputType', float]:
        return self.confidence_levels.get(user_id, {})

    def get_controlled_actions(
            self,
            user_id: int
    ) -> list['GameAction']:
        return self.user_actions.get(user_id, [])

    def user_input_to_action(
            self,
            user_id: int,
            input_type: 'InputType',
    ) -> 'GameAction':
        return self.user_input_to_action_map.get(user_id, {}).get(input_type, None)

    def action_to_user_input(
            self,
            user_id: int,
            action: 'GameAction',
    ) -> 'InputType':
        return self.action_to_user_input_map.get(user_id, {}).get(action, None)

    def game_input_to_action(
            self,
            input_type: 'InputType'
    ) -> 'GameAction':
        return self.game_input_to_action_map.get(input_type, None)

    def action_to_game_input(
            self,
            action: 'GameAction',
    ) -> 'InputType':
        return self.action_to_game_input_map.get(action, None)

    def game_input_to_user_input(
            self,
            user_id: int,
            input_type: 'InputType',
    ) -> 'InputType':
        return self.action_to_user_input(user_id, self.game_input_to_action(input_type))

    def user_input_to_game_input(
            self,
            user_id: int,
            input_type: 'InputType',
    ) -> 'InputType':
        return self.action_to_game_input(self.user_input_to_action(user_id, input_type))

    def get_humans_count(self) -> int:
        return len(self.user_actions)