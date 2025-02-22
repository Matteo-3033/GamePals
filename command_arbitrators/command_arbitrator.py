from agents import MessageData, ActorData
from agents.actor import Actor, ActorID
from agents.observers.actor_observer import ActorObserver
from command_arbitrators.policy_manager import PolicyManager, PolicyRole, PolicyType
from input_sources import ControllerInput, InputType
from input_sources.controller_inputs_map import ControllerInputsMap
from input_sources.virtual_controller_provider import VirtualControllerProvider


class CommandArbitrator(ActorObserver):
    """
     The CommandArbitrator class is an abstract Arbitrator.

     It arbitrates between inputs from different Actors and sends the final command to a Virtual Controller.

     The Arbitrator can communicate to its Actors via their get_arbitrator_updates method.
     """

    def __init__(self) -> None:
        self.virtual_controller: VirtualControllerProvider = VirtualControllerProvider()
        self.actors: dict[ActorID, Actor] = {}
        self.input_maps : dict[ActorID, ControllerInputsMap] = {}
        self.policy_manager = PolicyManager()

    def add_actor(self, actor: Actor, role : PolicyRole) -> None:
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

        input_type = data.c_input.type
        if input_type in self.virtual_controller.STICKS:
            self._merge_continuous_input(input_type)
        else:
            self._merge_binary_input(input_type)

    def receive_message_update(self, data: MessageData) -> None:
        """ Receives a Message from one of its Actors """
        print(f"[CommandArbitrator] Received Message: {data}")

    def _merge_binary_input(self, input_type : InputType) -> None:
        """ Merges Binary Inputs and sends the final Input to the Virtual Controller """

        policy = self.policy_manager.get_policy(input_type)
        input_values = [self.input_maps[actor_id].get(input_type) for actor_id in policy.actors.keys()]

        match policy.policy_type:

            case PolicyType.POLICY_EXCLUSIVITY:
                c_input = input_values[0][0]
                self.execute_single_value_command(c_input)

            case _:
                raise ValueError(f"Merging for Policy Type {policy.policy_type} currently not implemented")

    def _merge_continuous_input(self, input_type : InputType) -> None:
        """ Merges Continuous Inputs and sends the final Input to the Virtual Controller """

        # Currently assuming complementary controls
        is_left_stick = input_type == InputType.STICK_LEFT_X or input_type == InputType.STICK_LEFT_Y
        input_type_x = InputType.STICK_LEFT_X if is_left_stick else InputType.STICK_RIGHT_X
        input_type_y = InputType.STICK_LEFT_Y if is_left_stick else InputType.STICK_RIGHT_Y

        policy_x = self.policy_manager.get_policy(input_type_x)
        input_values_x = [self.input_maps[actor_id].get(input_type_x) for actor_id in policy_x.actors.keys()]

        policy_y = self.policy_manager.get_policy(input_type_y)
        input_values_y = [self.input_maps[actor_id].get(input_type_y) for actor_id in policy_y.actors.keys()]

        match (policy_x.policy_type, policy_y.policy_type):

            case (PolicyType.POLICY_EXCLUSIVITY, PolicyType.POLICY_EXCLUSIVITY):
                c_input_x = input_values_x[0][0]
                c_input_y = input_values_y[0][0]
                self.execute_double_value_command(c_input_x, c_input_y)

            case _:
                raise ValueError(f"Merging for Policy Type {policy_x.policy_type} {policy_y.policy_type} currently not implemented")

    def execute_single_value_command(self, c_input: ControllerInput) -> None:
        """ Executes a single-value command on the Virtual Controller """
        print(f"Executing {c_input}")
        self.virtual_controller.execute(c_input)

    def execute_double_value_command(self, input_x: ControllerInput, input_y: ControllerInput) -> None:
        """ Executes a 2-axis command on the Virtual Controller """
        print(f"Executing {input_x} {input_y} ")
        self.virtual_controller.execute_stick(input_x, input_y)
