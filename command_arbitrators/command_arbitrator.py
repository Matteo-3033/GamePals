import logging
from typing import Type

from ..agents import ActionConversionDelegate, ActionInput, Actor, ActorID
from ..agents.actor_observer import ActorData, ActorObserver, MessageData
from ..sources import VirtualControllerProvider
from ..sources.controller import ControllerInput
from ..sources.game import GameAction
from ..sources.game.game_actions_map import GameActionsMap
from ..utils.configuration_handler import ConfigurationHandler
from .policies import InputEntry, Policy, PolicyManager

logger = logging.getLogger(__name__)


class CommandArbitrator(ActorObserver):
    """
    The CommandArbitrator class is an abstract Arbitrator.

    It arbitrates between inputs from different Actors and sends the final command to a Virtual Controller.

    The Arbitrator can communicate to its Actors the computed inputs via their get_arbitrator_updates method.
    """

    def __init__(
        self,
        policies: dict[GameAction, Type[Policy]],
        conversion_delegates: list[ActionConversionDelegate] | None = None,
    ) -> None:
        if conversion_delegates is None:
            conversion_delegates = list()

        self.config_handler: ConfigurationHandler = ConfigurationHandler()
        self.virtual_controller: VirtualControllerProvider = VirtualControllerProvider()
        self.actors: dict[ActorID, Actor] = {}
        self.action_maps: dict[ActorID, GameActionsMap] = {}
        self.conversion_delegates: dict[GameAction, ActionConversionDelegate] = {
            delegate.get_action(): delegate for delegate in conversion_delegates
        }

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
        for _, actor in self.actors.items():
            actor.start()

    def receive_input_update(self, actor_data: ActorData) -> None:
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

        if merge_result is not None:
            self.execute_command(merge_result)

    def receive_message_update(self, data: MessageData) -> None:
        """Receives a Message from one of its Actors"""
        logger.info("Received Message: %s", data)
        if "RESET" in data.message:
            self.virtual_controller.reset_controls()

    def _merge_by_action(self, action: GameAction) -> ControllerInput | None:
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
        c_input = self.action_to_input(action_input)

        logger.debug("Policy is %s and Entries are %s", policy.__name__, input_entries)

        return c_input

    def execute_command(self, c_input: ControllerInput) -> None:
        """Executes a command on the Virtual Controller"""
        logger.debug("Executing %s", c_input)
        self.virtual_controller.execute(c_input)
        self.notify_arbitrated_input(c_input)

    def notify_arbitrated_input(self, input_data: ControllerInput) -> None:
        """Notifies all Actors of the Arbitrated Input"""
        for actor in self.actors.values():
            actor.on_arbitrated_inputs(input_data)

    def action_to_input(self, action_input: ActionInput) -> ControllerInput | None:
        """Maps the Game Action into the Controller Input Type. Return None to ignore the input (i.e. unrecognized)"""

        inputs = self.config_handler.action_to_game_input(action_input.action)

        if not inputs:
            logger.warning(
                "The game action %s is not mapped to any input. Ignored",
                action_input.action,
            )
            return None

        if len(inputs) > 1:
            if action_input.action not in self.conversion_delegates:
                logger.warning(
                    "Game actions mapped to multiple inputs must be handled by a Delegate. Ignored",
                    action_input.action,
                )
                return None

        if action_input.action in self.conversion_delegates:
            # Check if the Action is handled by a Delegate
            # This is useful for Actions that are mapped to multiple inputs (eg: both triggers)
            return self.conversion_delegates[action_input.action].convert_to_input(
                action_input
            )

        return ControllerInput(type=inputs[0], val=action_input.val)
