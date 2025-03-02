import tomllib
import logging
from dataclasses import dataclass

from ..agents.datas import MessageData, ActorData
from ..agents.actor import Actor, ActorID
from ..agents.observers.actor_observer import ActorObserver
from .policies.policy import Policy
from .policy_manager import PolicyManager, PolicyRole
from ..sources.controller_inputs import ControllerInput, InputType
from ..sources.controller_inputs_map import ControllerInputsMap, ControllerInputRecord
from ..sources.virtual_controller_provider import VirtualControllerProvider

logger = logging.getLogger(__name__)

@dataclass
class InputEntry:
    """
    InputEntry contains all the information needed from an Actor to perform a merge.

    In particular, a Merging Method should be created based on a PolicyType and a list of InputEntry.
    """
    actor_id: ActorID
    actor_role: PolicyRole
    input_details: ControllerInputRecord  # Contains Value, Confidence Level and a Timestamp of last acquisition


class CommandArbitrator(ActorObserver):
    """
     The CommandArbitrator class is an abstract Arbitrator.

     It arbitrates between inputs from different Actors and sends the final command to a Virtual Controller.

     The Arbitrator can communicate to its Actors via their get_arbitrator_updates method.
     """

    def __init__(self, config_file_path: str) -> None:
        self.virtual_controller: VirtualControllerProvider = VirtualControllerProvider()
        self.actors: dict[ActorID, Actor] = {}
        self.input_maps: dict[ActorID, ControllerInputsMap] = {}

        with open(config_file_path, 'rb') as config_file:
            config = tomllib.load(config_file)
            policies_types = {
                in_type: Policy.policy_name_to_policy(name)
                for in_type, name in config["PolicyTypes"].items()
            }
            self.policy_manager = PolicyManager(policies_types)

    def add_actor(self, actor: Actor, role: PolicyRole) -> None:
        """ Adds an Actor to the Architecture """
        self.actors[actor.get_id()] = actor
        self.input_maps[actor.get_id()] = ControllerInputsMap()
        self.policy_manager.register_actor(actor, role)
        actor.subscribe(self)  # Subscribe the Arbitrator to all the Actors

    def start(self) -> None:
        """ Starts the Actors and the Arbitration Process """
        for _, actor in self.actors.items():
            actor.start()

    def receive_input_update(self, data: ActorData) -> None:
        """ Receives Input and Confidence Level from one of its Actors """
        self.input_maps[data.actor_id].set(data.c_input, data.confidence)

        input_type = data.c_input.type

        if input_type in VirtualControllerProvider.STICKS:  # Input is a Stick (2-Axis required)
            is_left_stick = input_type == InputType.STICK_LEFT_X or input_type == InputType.STICK_LEFT_Y
            input_type_x = InputType.STICK_LEFT_X if is_left_stick else InputType.STICK_RIGHT_X
            input_type_y = InputType.STICK_LEFT_Y if is_left_stick else InputType.STICK_RIGHT_Y

            merge_result_x = self._merge_by_input_type(input_type_x)
            merge_result_y = self._merge_by_input_type(input_type_y)

            self.execute_double_value_command(merge_result_x, merge_result_y)

        else:  # Input is not a Stick (1 Axis/Value is enough)
            merge_result = self._merge_by_input_type(input_type)
            self.execute_single_value_command(merge_result)

    def receive_message_update(self, data: MessageData) -> None:
        """ Receives a Message from one of its Actors """
        logger.info("Received Message: %s", data)
        if "RESET" in data.message:
            self.virtual_controller.reset_controls()


    def _merge_by_input_type(self, input_type: InputType) -> ControllerInput:
        """
        Merges the Input Entries for the given Input Type, based on the specified Policy Type.
        It then returns the resulting ControllerInput
        """
        policy_info = self.policy_manager.get_policy(input_type)
        policy = policy_info.policy_type
        input_entries = [InputEntry(actor_id, actor_role, self.input_maps[actor_id].get(input_type)[1])
                         for actor_id, actor_role in policy_info.actors.items()]

        value = policy.merge_input_entries(input_entries)
        return ControllerInput(input_type, value)

    def execute_single_value_command(self, c_input: ControllerInput) -> None:
        """ Executes a single-value command on the Virtual Controller """
        logger.info("Executing %s", c_input)
        self.virtual_controller.execute(c_input)
        self.notify_arbitrated_input(c_input)

    def execute_double_value_command(self, input_x: ControllerInput, input_y: ControllerInput) -> None:
        """ Executes a 2-axis command on the Virtual Controller """
        logger.info("Executing %s %s", input_x, input_y)
        self.virtual_controller.execute_stick(input_x, input_y)
        self.notify_arbitrated_input(input_x)
        self.notify_arbitrated_input(input_y)

    def notify_arbitrated_input(self, input_data : ControllerInput) -> None:
        """ Notifies all Actors of the Arbitrated Input"""
        for actor in self.actors.values():
            actor.get_arbitrated_inputs(input_data)
