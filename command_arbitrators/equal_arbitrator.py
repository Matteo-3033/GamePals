from agents import ActorData
from agents.input_source import InputSource
from command_arbitrators.command_arbitrator import CommandArbitrator
from input_sources import InputType
from input_sources.controller_inputs_map import ControllerInputsMap


class EqualArbitrator(CommandArbitrator):
    """
    The EqualArbitrator class is an implementation of a very simple CommandArbitrator.

    EqualArbitrator assumes all sources to be equally relevant and produces, on a Virtual Controller,
    an input that is simply the sum of all the inputs from the given sources.
    """

    def __init__(self):
        super().__init__()
        self.sources : list[InputSource[ActorData]] = []
        self.latest_inputs_map : ControllerInputsMap = ControllerInputsMap()

    def receive_input(self, data : ActorData) -> None:
        """ Receives an Input from an Input Source and sends it to the Virtual Controller """
        self.latest_inputs_map.set(data.c_input)
        if type in self.virtual_controller.STICKS:
            is_left_stick = type == InputType.STICK_LEFT_X or type == InputType.STICK_LEFT_Y
            type_x = InputType.STICK_LEFT_X if is_left_stick else InputType.STICK_RIGHT_X
            type_y = InputType.STICK_LEFT_Y if is_left_stick else InputType.STICK_RIGHT_Y

            input_x = self.latest_inputs_map.get(type_x)[0]
            input_y = self.latest_inputs_map.get(type_y)[0]

            self.execute_continuous_command(input_x, input_y)
        else:
            self.execute_binary_command(data.c_input)

    def add_source(self, source: InputSource[ActorData]) -> None:
        """ Adds a new Input Source to the Arbitrator """
        self.sources.append(source)
        source.subscribe(self.receive_input)
