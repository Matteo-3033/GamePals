from typing import Any, TYPE_CHECKING, Type
from collections import defaultdict
import logging

if TYPE_CHECKING:
    from ..command_arbitrators.policies import PolicyName, Policy
    from ..sources.controller.controller_inputs import InputType
    from ..sources.game.game_action import GameAction
    from ..agents.sw_agent_actor import SWAgentActor

logger = logging.getLogger(__name__)


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
        from ..command_arbitrators.policies import PolicyName

        # TODO: Configuration Validation should go here

        self.confidence_levels: dict[int, dict['InputType', float]] = defaultdict(lambda: defaultdict(lambda: 1.0))
        self.user_actions: dict[int, list['GameAction']] = defaultdict(list)
        self.policy_types: dict['InputType', Type['Policy']] = defaultdict()
        self.registered_inputs: set['InputType'] = set()
        self.required_agents: set[str] = set()
        self.agents_params: dict[str, dict[str, Any]] = defaultdict(lambda: defaultdict())

        self.user_input_to_action_map: dict[int, dict['InputType', 'GameAction']] = defaultdict(dict)
        self.action_to_user_input_map: dict[int, dict['GameAction', 'InputType']] = defaultdict(dict)
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

            for agent in action.get("agents", []):
                self.required_agents.add(agent["name"])

            if action["name"] in game_config.get("actions", {}):
                for game_input in game_config["actions"][action["name"]]:
                    self.policy_types[game_input] = PolicyName[action.get("policy", "POLICY_EXCLUSIVITY")]

        for action, inputs in game_config.get("actions", {}).items():

            self.action_to_game_input_map[action] = inputs[0]  # Knowing one input for each action is enough

            for game_input in inputs:
                self.game_input_to_action_map[game_input] = action
                self.registered_inputs.add(game_input)

        for agent in assistance_config.get("agent", []):
            if agent["name"] not in self.required_agents and agent.get("active", False):
                self.required_agents.add(agent["name"])

            self.agents_params[agent["name"]] = agent["params"]

    def get_policy_types(
            self
    ) -> dict['InputType', Type['Policy']]:
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

    def get_registered_action_inputs(
            self
    ) -> set['InputType']:
        return self.registered_inputs

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
        found = self.action_to_user_input(user_id, self.game_input_to_action(input_type))
        return found if found else input_type

    def user_input_to_game_input(
            self,
            user_id: int,
            input_type: 'InputType',
    ) -> 'InputType':
        found = self.action_to_game_input(self.user_input_to_action(user_id, input_type))
        return found if found else input_type

    def get_humans_count(self) -> int:
        return len(self.user_actions)

    def get_necessary_agents(self) -> set[Type['SWAgentActor']]:
        from ..agents.sw_agent_actor import SWAgentActor

        agent_classes = self.get_agent_classes(cls=SWAgentActor)
        logger.info("Required agents are %s", self.required_agents)
        logger.info("Found %d agent implementations: %s", len(agent_classes), agent_classes )
        required_agent_classes = {
            cls
            for cls in agent_classes
            if cls.get_name() in self.required_agents
        }
        return required_agent_classes

    def get_agent_classes(self, cls: Type) -> set[Type['SWAgentActor']]:
        subclasses = set(cls.__subclasses__())  # Find direct subclasses
        all_subclasses = set(subclasses)

        for subclass in subclasses.copy():  # Find nested subclasses
            all_subclasses.update(self.get_agent_classes(subclass))

        # Filter out abstract classes, checking the __abstractmethods__ attribute
        all_subclasses = {
            subclass
            for subclass in all_subclasses
            if not hasattr(subclass, "__abstractmethods__")  # Doesn't have
               or not subclass.__abstractmethods__  # Has but it's empty
        }

        return all_subclasses

    def get_params_for_agent(self, agent_name : str) -> dict[str, Any]:
        return self.agents_params[agent_name]