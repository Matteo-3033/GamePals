import logging
from dataclasses import dataclass

from . import PolicyContinuousOR
from ...agents import Actor, ActorID
from ...sources.controller import InputType
from .input_entry import PolicyRole
from .policy import Policy
from ...utils.configuration_handler import ConfigurationHandler


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
            policies_types: dict[InputType, type[Policy]],
            default_policy : type[Policy] = PolicyContinuousOR,
    ) -> None:
        self.policies_map: dict[InputType, PolicyMapEntry] = {}
        self.config_handler: ConfigurationHandler = ConfigurationHandler()

        # Every Input is registered with the specified Policy (or the default one, if none is specified)
        for input_type in InputType:
            specified_policy = policies_types.get(input_type, default_policy)
            self.policies_map[input_type] = PolicyMapEntry(specified_policy, {})

    def register_actor(self, actor: Actor) -> None:
        """
        Registers the given Actor, for the Input Types specified by the
        get_controlled_inputs method of the Actor.
        The Role of the Actor for each of its inputs is determined checking the configuration
        """
        from ...agents.human_actor import HumanActor
        from ...agents.sw_agent_actor import SWAgentActor

        actions = actor.get_controlled_actions()

        # This allows every actor to execute inputs not associated with any action
        inputs = {
            self.config_handler.action_to_game_input(action)
            for action in actions
        }.union(
            {t for t in InputType}.difference(self.config_handler.get_registered_action_inputs())
        )

        for input_type in inputs:
            policy_entry = self.policies_map[input_type]
            actors_number = len(policy_entry.actors)
            action = self.config_handler.game_input_to_action(input_type)

            if isinstance(actor, HumanActor):
                role = self.config_handler.get_human_role(
                    user_idx=actor.get_index(),
                    action=action
                )
            elif isinstance(actor, SWAgentActor):
                role = self.config_handler.get_agent_role(
                    agent_name=actor.get_name(),
                    action=action
                )
            else:
                role = PolicyRole.PILOT

            if policy_entry.policy_type.get_max_actors() > actors_number:
                self.policies_map[input_type].actors[actor.get_id()] = role
            else:
                raise ValueError(
                    f"Only one Actor per Input Type {input_type} is allowed"
                )

    def get_policy(self, input_type: InputType) -> PolicyMapEntry:
        return self.policies_map[input_type]
