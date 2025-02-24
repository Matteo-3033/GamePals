import tomllib
from dataclasses import dataclass

from agents import MessageData, ActorData
from agents.actor import Actor, ActorID
from agents.observers.actor_observer import ActorObserver
from command_arbitrators.policy_manager import PolicyManager, PolicyRole, BinaryPolicyType, ContinuousPolicyType, \
    PolicyType
from input_sources import ControllerInput, InputType, ControllerInputRecord
from input_sources.controller_inputs_map import ControllerInputsMap
from input_sources.virtual_controller_provider import VirtualControllerProvider


@dataclass
class InputEntry:
    actor_id: ActorID
    actor_role: PolicyRole
    input_details: ControllerInputRecord


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
            self.policy_manager = PolicyManager(config["PolicyTypes"])

    def add_actor(self, actor: Actor, role: PolicyRole) -> None:
        """ Adds an Actor to the Architecture """
        self.actors[actor.get_id()] = actor
        actor.subscribe(self)  # Subscribe the Arbitrator to all the Actors
        self.input_maps[actor.get_id()] = ControllerInputsMap()
        self.policy_manager.register_actor(actor, role)

    def start(self) -> None:
        """ Starts the Actors and the Arbitration Process """
        for _, actor in self.actors.items():
            actor.start()

    def receive_input_update(self, data: ActorData) -> None:
        """ Receives Input and Confidence Level from one of its Actors """
        self.input_maps[data.actor_id].set(data.c_input, data.confidence)

        # Choose Merge Function

        input_type = data.c_input.type
        policy_type = self.policy_manager.get_policy(input_type).policy_type
        if policy_type in ContinuousPolicyType:
            merge_func = self._merge_continuous_inputs
        elif policy_type in BinaryPolicyType:
            merge_func = self._merge_binary_inputs
        else:
            raise ValueError(f"Policy {policy_type} not recognized.")

        # Execute Merge

        if input_type in VirtualControllerProvider.STICKS:  # Input is a Stick (2-Axis required)
            is_left_stick = input_type == InputType.STICK_LEFT_X or input_type == InputType.STICK_LEFT_Y
            input_type_x = InputType.STICK_LEFT_X if is_left_stick else InputType.STICK_RIGHT_X
            input_type_y = InputType.STICK_LEFT_Y if is_left_stick else InputType.STICK_RIGHT_Y

            merge_result_x = merge_func(input_type_x)
            merge_result_y = merge_func(input_type_y)

            self.execute_double_value_command(merge_result_x, merge_result_y)

        else:  # Input is not a Stick (1 Axis/Value is enough)
            merge_result = merge_func(input_type)
            self.execute_single_value_command(merge_result)

    def receive_message_update(self, data: MessageData) -> None:
        """ Receives a Message from one of its Actors """
        print(f"[CommandArbitrator] Received Message: {data}")
        if "RESET" in data.message:
            self.virtual_controller.reset_controls()

    def _merge_binary_inputs(
            self,
            input_type: InputType
    ) -> ControllerInput:
        """ Merges the Input Entries for the given Input Type, based on the specified Policy Type.
         It then returns the resulting ControllerInput """
        policy_info = self.policy_manager.get_policy(input_type)
        policy_type = policy_info.policy_type
        input_entries = [InputEntry(actor_id, actor_role, self.input_maps[actor_id].get(input_type)[1])
                         for actor_id, actor_role in policy_info.actors.items()]

        match policy_type:

            case BinaryPolicyType.POLICY_EXCLUSIVITY:
                val = input_entries[0].input_details.val
                return ControllerInput(input_type, val)

            case BinaryPolicyType.POLICY_AND:
                val = True
                for input_entry in input_entries:
                    curr = input_entry.input_details.val != 0  # False if 0, True otherwise
                    val = val & curr

                return ControllerInput(input_type, input_type.get_max_abs_value() if val else 0)

            case BinaryPolicyType.POLICY_OR:
                val = False
                for input_entry in input_entries:
                    curr = input_entry.input_details.val != 0  # False if 0, True otherwise
                    val = val | curr

                return ControllerInput(input_type, input_type.get_max_abs_value() if val else 0)

            case _:
                raise ValueError(f"Merging for Policy Type {policy_type} currently not implemented")

    def _merge_continuous_inputs(
            self,
            input_type: InputType
    ) -> ControllerInput:
        """ Merges the Input Entries for the given Input Type, based on the specified Policy Type.
         It then returns the resulting ControllerInput """
        policy_info = self.policy_manager.get_policy(input_type)
        policy_type = policy_info.policy_type
        input_entries = [InputEntry(actor_id, actor_role, self.input_maps[actor_id].get(input_type)[1])
                         for actor_id, actor_role in policy_info.actors.items()]

        match policy_type:

            case ContinuousPolicyType.POLICY_EXCLUSIVITY:
                val = input_entries[0].input_details.val
                return ControllerInput(input_type, val)

            case _:
                raise ValueError(f"Merging for Policy Type {policy_type} currently not implemented")

    def execute_single_value_command(self, c_input: ControllerInput) -> None:
        """ Executes a single-value command on the Virtual Controller """
        # print(f"Executing {c_input}")
        self.virtual_controller.execute(c_input)

    def execute_double_value_command(self, input_x: ControllerInput, input_y: ControllerInput) -> None:
        """ Executes a 2-axis command on the Virtual Controller """
        # print(f"Executing {input_x} {input_y} ")
        self.virtual_controller.execute_stick(input_x, input_y)
