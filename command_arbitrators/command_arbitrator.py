from abc import ABC

from game_controllers import ControllerInput
from game_controllers.virtual_controller_provider import VirtualControllerProvider


class CommandArbitrator(ABC):
    """
    The CommandArbitrator class is an abstract Arbitrator.

    It arbitrates between inputs from different sources and sends the final command to a Virtual Controller.
    """

    def __init__(self) -> None:
        self.virtual_controller: VirtualControllerProvider = VirtualControllerProvider()

    def execute_binary_command(self, input: ControllerInput) -> None:
        """
        Executes a single-value command on the Virtual Controller
        """
        print(f"Executing {input}")
        self.virtual_controller.execute(input)

    def execute_continuous_command(self, input_x: ControllerInput, input_y: ControllerInput) -> None:
        """
        Executes a 2-axis command on the Virtual Controller
        """
        print(f"Executing {input_x} {input_y} ")
        self.virtual_controller.execute_stick(input_x, input_y)
