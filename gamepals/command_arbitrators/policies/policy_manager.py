import logging
from dataclasses import dataclass

from gamepals.agents import Actor, ActorID, HumanActor, SWAgentActor
from gamepals.agents.actions import GameAction
from gamepals.utils.configuration_handler import ConfigurationHandler

from .input_entry import PolicyRole
from .policy import Policy
from .policy_continuous_or import PolicyContinuousOR


@dataclass
class PolicyMapEntry:
    """An Entry in the Policies Map for a given Input Type. It contains the PolicyType and the involved Actors."""

    policy_type: type[Policy]
    actors: dict[ActorID, PolicyRole]


logger = logging.getLogger(__file__)


class PolicyManager:
    """
    PolicyManager manages the Arbitration Policies for a Command Arbitrator.

    A Policy is defined for every Input Type.
    """

    def __init__(
        self,
        policies_types: dict[GameAction, type[Policy]],
        default_policy: type[Policy] = PolicyContinuousOR,
    ) -> None:
        self.policies_map: dict[GameAction, PolicyMapEntry] = dict()
        self.config_handler = ConfigurationHandler()
        self.default_policy = default_policy

        # Every Input is registered with the specified Policy (or the default one, if none is specified)
        for action, policy_type in policies_types.items():
            self.policies_map[action] = PolicyMapEntry(policy_type, dict())

    def register_actor(self, actor: Actor) -> None:
        """
        Registers the given Actor, for the Input Types specified by the
        get_controlled_inputs method of the Actor.
        The Role of the Actor for each of its inputs is determined checking the configuration
        """

        actions = actor.get_controlled_actions()

        for action in actions:
            policy_entry = self.policies_map.get(action)
            if policy_entry is None:
                self.policies_map[action] = PolicyMapEntry(self.default_policy, {})
                policy_entry = self.policies_map[action]

            actors_number = len(policy_entry.actors)

            # Finds the Role of the Actor in the Config, for that specific action. It's over-complicated because we
            # currently don't have a unique way to identify actors in the config.example (for humans we use index, for agents we use name)
            if isinstance(actor, HumanActor):
                role = self.config_handler.get_human_role(
                    user_idx=actor.get_index(), action=action
                )
            elif isinstance(actor, SWAgentActor):
                role = self.config_handler.get_agent_role(
                    agent_name=actor.get_name(), action=action
                )

            max_actors = policy_entry.policy_type.get_max_actors()
            if max_actors > actors_number:
                self.policies_map[action].actors[actor.get_id()] = PolicyRole(role)
            else:
                raise ValueError(f"Action {action} allows maximum {max_actors} actors")

    def get_policy(self, action: GameAction) -> PolicyMapEntry:
        found = self.policies_map.get(action)
        if found is None:
            self.policies_map[action] = PolicyMapEntry(self.default_policy, {})
            return self.policies_map[action]
        return found
