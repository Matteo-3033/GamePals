from typing import Any, TYPE_CHECKING, Type
from collections import defaultdict
import logging

from .utils import get_all_concrete_subclasses

if TYPE_CHECKING:
    from ..command_arbitrators.policies import Policy, PolicyRole
    from ..sources.controller.controller_inputs import InputType
    from ..sources.game.game_action import GameAction
    from ..agents.sw_agent_actor import SWAgentActor

logger = logging.getLogger(__name__)


class ConfigurationHandler:
    """
    ConfigurationHandler class handles the configuration files for the architecture.

    The configuration is composed of 3 toml dictionaries:
    * game_config, containing general information about the game and the game inputs.
    * agents_config, containing information about which software agents are available for the specified game.
    * assistance_config, containing all information about the actors involved in the architecture, which actions
     they control and which inputs they use

    It implements a Singleton pattern.

    TODO: eventually split x and y axis into positive and negative
    TODO: configure meta-commands
    """
    _instance: 'ConfigurationHandler' = None

    def __new__(
            cls,
            game_config: dict[str, Any] | None = None,
            agents_config: dict[str, Any] | None = None,
            assistance_config: dict[str, Any] | None = None,
    ) -> 'ConfigurationHandler':
        """Returns the singleton instance. If it's the first time calling this, config dicts should be passed"""

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
        """
        Loads the configuration from config into more specific dictionaries.
        """
        from ..command_arbitrators.policies import PolicyName

        # TODO: Configuration Validation should go here

        self.confidence_levels: dict[int, dict['GameAction', float]] = defaultdict(lambda: defaultdict(lambda: 1.0))
        self.user_actions: dict[int, list['GameAction']] = defaultdict(list)
        self.policy_types: dict['GameAction', Type['Policy']] = defaultdict()
        self.registered_inputs: set['InputType'] = set()
        self.required_agents: set[str] = set()
        self.agents_params: dict[str, dict[str, Any]] = defaultdict(lambda: defaultdict())
        self.user_policy_roles: dict[tuple['GameAction', int], PolicyRole] = defaultdict()
        self.agent_policy_roles: dict[tuple['GameAction', str], PolicyRole] = defaultdict()

        self.user_input_to_action_map: dict[int, dict['InputType', 'GameAction']] = defaultdict(dict)
        self.action_to_user_input_map: dict[int, dict['GameAction', 'InputType']] = defaultdict(dict)
        self.game_input_to_action_map: dict['InputType', 'GameAction'] = defaultdict()
        self.action_to_game_input_map: dict['GameAction', 'InputType'] = defaultdict()

        for action in assistance_config.get("action", []):
            for human in action.get("humans", []):
                human_idx = human.get("idx", self.DEFAULTS["HUMAN_IDX"])
                human_role = human.get("role", self.DEFAULTS["HUMAN_ROLE"])

                self.user_actions[human_idx].append(action["name"])
                self.user_policy_roles[(action["name"], human_idx)] = human_role
                controls = human.get("controls", [])

                self.confidence_levels[human_idx][action["name"]] = human["confidence"]

                for control in controls:
                    self.user_input_to_action_map[human_idx][control] = action["name"]

                if len(controls) > 0:
                    # Knowing one input for each action is enough
                    self.action_to_user_input_map[human_idx][action["name"]] = controls[0]

            for agent in action.get("agents", []):
                agent_role = agent.get("role", self.DEFAULTS["AGENT_ROLE"])
                self.required_agents.add(agent["name"])
                self.agent_policy_roles[(action["name"], agent["name"])] = agent_role

            if action["name"] in game_config.get("actions", {}):
                self.policy_types[action["name"]] = PolicyName[action.get("policy", "POLICY_EXCLUSIVITY")]

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
    ) -> dict['GameAction', Type['Policy']]:
        """Returns the Policy associated with every Input Type"""
        return self.policy_types

    def get_confidence_levels(
            self,
            user_idx: int
    ) -> dict['GameAction', float]:
        """Returns the confidence level associated with every GameAction, for a specific HumanActor"""
        return self.confidence_levels.get(user_idx, {})

    def get_controlled_actions(
            self,
            user_idx: int
    ) -> list['GameAction']:
        """Returns the list of game actions that a certain HumanActor is responsible for"""
        return self.user_actions.get(user_idx, [])

    def get_registered_action_inputs(
            self
    ) -> set['InputType']:
        """
        Returns all the action inputs for which there is a designated actor.
        This allows to know which inputs are not part of the config (i.e., a button that is only used in the menu)
        """
        return self.registered_inputs

    def user_input_to_action(
            self,
            user_idx: int,
            input_type: 'InputType',
    ) -> 'GameAction':
        """Returns the GameAction that the user user_idx intends to do when pressing the given input_type"""
        return self.user_input_to_action_map.get(user_idx, {}).get(input_type, None)

    def action_to_user_input(
            self,
            user_idx: int,
            action: 'GameAction',
    ) -> 'InputType':
        """Returns the InputType that the user user_idx needs to press to perform the given action"""
        return self.action_to_user_input_map.get(user_idx, {}).get(action, None)

    def game_input_to_action(
            self,
            input_type: 'InputType'
    ) -> 'GameAction':
        """Returns the GameAction that the game associates with the given input_type"""
        return self.game_input_to_action_map.get(input_type, None)

    def action_to_game_input(
            self,
            action: 'GameAction',
    ) -> 'InputType':
        """Returns the InputType that the game associates with the given action"""
        return self.action_to_game_input_map.get(action, None)

    def game_input_to_user_input(
            self,
            user_idx: int,
            input_type: 'InputType',
    ) -> 'InputType':
        """Returns the game InputType corresponding to the user InputType (matches the inputs based on the action)"""
        found = self.action_to_user_input(user_idx, self.game_input_to_action(input_type))
        return found if found else input_type

    def user_input_to_game_input(
            self,
            user_idx: int,
            input_type: 'InputType',
    ) -> 'InputType':
        """Returns the user InputType corresponding to the game InputType (matches the inputs based on the action)"""
        found = self.action_to_game_input(self.user_input_to_action(user_idx, input_type))
        return found if found else input_type

    def get_humans_count(self) -> int:
        """Returns the number of Human Actors specified in the config"""
        return len(self.user_actions)

    def get_necessary_agents(self) -> set[Type['SWAgentActor']]:
        """Returns the list of SWAgentActors that are required by the config"""
        from ..agents.sw_agent_actor import SWAgentActor

        agent_classes = get_all_concrete_subclasses(cls=SWAgentActor)
        required_agent_classes = {
            cls
            for cls in agent_classes
            if cls.get_name() in self.required_agents
        }
        return required_agent_classes

    def get_params_for_agent(self, agent_name: str) -> dict[str, Any]:
        """Returns the map of constructor parameters associated to the specified agent"""
        return self.agents_params[agent_name]

    def get_agent_role(
            self,
            agent_name: str,
            action : 'GameAction'
    ) -> 'PolicyRole':
        """Returns the Role that agent_name covers for the specified action"""
        found = self.agent_policy_roles[(action, agent_name)]
        return found if found else self.DEFAULTS["AGENT_ROLE"]

    def get_human_role(
            self,
            user_idx: int,
            action : 'GameAction'
    ) -> 'PolicyRole':
        """Returns the Role that user_idx covers for the specified action"""
        found = self.user_policy_roles[(action, user_idx)]
        return found if found else self.DEFAULTS["HUMAN_ROLE"]


    DEFAULTS : dict[str, Any] = {
        "HUMAN_IDX": 0,
        "HUMAN_ROLE": "Pilot",
        "AGENT_ROLE": "Copilot",
    }