import logging
from typing import Type

from copilot.agents import Actor, ActorID
from copilot.agents.actions import ActionConversionManager, ActionInput, GameAction
from copilot.agents.observer import ActorData, ActorObserver, MessageData
from copilot.sources import VirtualControllerProvider
from copilot.sources.controller import ControllerInput
from copilot.utils.configuration_handler import ConfigurationHandler

from .game_actions_map import GameActionsMap
from .policies import InputEntry, Policy, PolicyManager
from ..logging.loggable import Loggable

logger = logging.getLogger(__name__)


class CommandArbitrator(ActorObserver, Loggable):
    """
    The CommandArbitrator class is an abstract Arbitrator.

    It arbitrates between inputs from different Actors and sends the final command to a Virtual Controller.

    The Arbitrator can communicate to its Actors the computed inputs via their get_arbitrator_updates method.
    """

    def __init__(
        self,
        policies: dict[GameAction, Type[Policy]],
        conversion_manager: ActionConversionManager,
    ) -> None:
        self.config_handler = ConfigurationHandler()
        self.virtual_controller = VirtualControllerProvider()
        self.actors: dict[ActorID, Actor] = dict()
        self.action_maps: dict[ActorID, GameActionsMap] = dict()
        self.conversion_manager = conversion_manager

        policy_types = policies.copy()
        self.policy_manager = PolicyManager(policy_types)

    def add_actor(self, actor: Actor) -> None:
        """Adds an Actor to the Architecture"""
        self.actors[actor.get_id()] = actor
        self.action_maps[actor.get_id()] = GameActionsMap()
        self.policy_manager.register_actor(actor)
        actor.subscribe(self)  # Subscribe the Arbitrator to all the Actors

    def start(self) -> None:
        """Starts the Actors and the Arbitration Process"""

        self.virtual_controller.start()

        for _, actor in self.actors.items():
            actor.start()

    def on_input_update(self, actor_data: ActorData) -> None:
        """Receives Input and Confidence Level from one of its Actors"""
        executed_action = actor_data.data.action

        if (
            executed_action
            not in self.actors[actor_data.actor_id].get_controlled_actions()
        ):
            logger.warning(
                "Actor %s is not registered to execute action %s",
                self.actors[actor_data.actor_id].__class__.__name__,
                executed_action,
            )
            return

        self.action_maps[actor_data.actor_id].set(actor_data.data)
        merge_result = self._merge_by_action(executed_action)

        for merged_input in merge_result:
            self.execute_command(merged_input)

    def on_message_update(self, data: MessageData) -> None:
        """Receives a Message from one of its Actors"""
        logger.info("Received Message: %s", data)
        if "RESET" in data.message:
            self.virtual_controller.reset_controls()

    def _merge_by_action(self, action: GameAction) -> list[ControllerInput]:
        """
        Merges the Input Entries for the given Input Type, based on the specified Policy Type.
        It then returns the resulting ControllerInput
        """

        policy_info = self.policy_manager.get_policy(action)
        policy = policy_info.policy_type

        input_entries = [
            InputEntry(actor_id, actor_role, self.action_maps[actor_id].get(action)[1])
            for actor_id, actor_role in policy_info.actors.items()
        ]

        value = policy.merge_input_entries(input_entries)
        action_input = ActionInput(action=action, val=value)
        c_inputs = self.conversion_manager.action_to_inputs(action_input)

        return c_inputs

    def execute_command(self, c_input: ControllerInput) -> None:
        """Executes a command on the Virtual Controller"""
        logger.debug("Executing %s", c_input)
        self.virtual_controller.execute(c_input)
        self.notify_arbitrated_input(c_input)

    def notify_arbitrated_input(self, input_data: ControllerInput) -> None:
        """Notifies all Actors of the Arbitrated Input"""
        for actor in self.actors.values():
            actor.on_arbitrated_inputs(input_data)

    def get_virtual_controller(self):
        return self.virtual_controller

    def get_log(self) -> str:
        return str(self.action_maps)
