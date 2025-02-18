from agents import PilotInputData, CopilotInputData, MessageData
from agents.copilot import Copilot
from agents.observers.copilot_observer import CopilotObserver
from agents.observers.pilot_observer import PilotObserver
from agents.pilot import Pilot
from command_arbitrators.command_arbitrator import CommandArbitrator
from game_controllers import InputType, ControllerInput
from game_controllers.controller_inputs_map import ControllerInputsMap

class DualArbitrator(CommandArbitrator, PilotObserver, CopilotObserver):
    """
    The DualArbitrator class is an implementation of a CommandArbitrator.

    It arbitrates between the inputs from a Pilot and a Copilot.
    """

    def __init__(self, pilot: Pilot, copilot: Copilot):
        super().__init__()
        self.pilot: Pilot = pilot
        self.copilot: Copilot = copilot

        # Latest Inputs from the Pilot and Copilot
        self.pilot_inputs_map: ControllerInputsMap = ControllerInputsMap()
        self.copilot_inputs_map: ControllerInputsMap = ControllerInputsMap()

        # Receive Updates from the Pilot and Copilot
        self.pilot.subscribe(self)
        self.copilot.subscribe(self)
        
        # Connect Pilot and Copilot
        self.pilot.subscribe(self.copilot)
        self.copilot.subscribe(self.pilot)

    def input_from_pilot(self, data: PilotInputData) -> None:
        """
        Receives Pilot Inputs as ControllerInput and Assistance Level.
        It then merges the inputs from the Pilot and Copilot and executes an action.
        """
        # print(f"Received input {input.type} with value {input.val} from Pilot")
        input = data.input
        assistance_level = data.assistance_level

        self.pilot_inputs_map.set(input, assistance_level)
        self.merge_inputs(input.type)

    def input_from_copilot(self, data: CopilotInputData) -> None:
        """
        Receives Copilot Inputs as ControllerInput and Confidence Level.
        It then merges the inputs from the Pilot and Copilot and executes an action.
        """
        #print(f"Received input {data.input.type} with value {data.input.val} from Copilot")
        input = data.input
        confidence_level = data.confidence_level

        # Avoid sending a zero-input twice
        last_input = self.copilot_inputs_map.get(input.type)
        if input.val == 0 and last_input[0].val == input.val:
            if input.type not in self.virtual_controller.STICKS:
                self.copilot_inputs_map.set(input, confidence_level)
            return

        self.copilot_inputs_map.set(input, confidence_level)
        self.merge_inputs(input.type)

    def merge_inputs(self, type: InputType) -> None:
        """
        Merges the inputs from the Pilot and Copilot
        """
        if type in self.virtual_controller.STICKS:
            self.merge_continuous_inputs(type)
        else:
            self.merge_binary_inputs(type)

    def merge_binary_inputs(self, type: InputType) -> None:
        """
        Merges the binary inputs from the Pilot and Copilot
        """
        (pilot_input, pilot_input_details) = self.pilot_inputs_map.get(type)
        (copilot_input, copilot_input_details) = self.copilot_inputs_map.get(type)

        I = copilot_input_details.level > 1 - pilot_input_details.level  # Indicator Function I{c > 1 - b}

        if I:
            self.execute_binary_command(copilot_input)
        else:
            self.execute_binary_command(pilot_input)

    def merge_continuous_inputs(self, type: InputType) -> None:
        """
        Merges the continuous inputs from the Pilot and Copilot
        """
        is_left_stick = type == InputType.STICK_LEFT_X or type == InputType.STICK_LEFT_Y
        type_x = InputType.STICK_LEFT_X if is_left_stick else InputType.STICK_RIGHT_X
        type_y = InputType.STICK_LEFT_Y if is_left_stick else InputType.STICK_RIGHT_Y

        (pilot_input_x, pilot_input_x_details) = self.pilot_inputs_map.get(type_x)
        (pilot_input_y, pilot_input_y_details) = self.pilot_inputs_map.get(type_y)
        (copilot_input_x, copilot_input_x_details) = self.copilot_inputs_map.get(type_x)
        (copilot_input_y, copilot_input_y_details) = self.copilot_inputs_map.get(type_y)

        # Send the most recent input atm
        most_recent_pilot = max(pilot_input_x_details.timestamp, pilot_input_y_details.timestamp)
        most_recent_copilot = max(copilot_input_x_details.timestamp, copilot_input_y_details.timestamp)

        # print(f"Pilot: {pilot_input_x} - Copilot: {copilot_input_x}")

        if most_recent_pilot - most_recent_copilot > 1:
            self.execute_continuous_command(input_x=pilot_input_x, input_y=pilot_input_y)
        else:
            alpha_x = self.alpha(pilot_input_x_details.level, copilot_input_x_details.level)
            alpha_y = self.alpha(pilot_input_y_details.level, copilot_input_y_details.level)
            combined_x = (1 - alpha_x) * pilot_input_x.val + (alpha_x) * copilot_input_x.val
            combined_y = (1 - alpha_y) * pilot_input_y.val + (alpha_y) * copilot_input_y.val
            self.execute_continuous_command(
                input_x=ControllerInput(type=pilot_input_x.type, val=int(combined_x)),
                input_y=ControllerInput(type=pilot_input_y.type, val=int(combined_y))
            )

    def alpha(self, beta: float, c: float) -> float:
        """
        Returns the value of the Blending Factor Alpha given Assistance Level Beta and Confidence Level C
        """
        return 1.0
        # return beta * c

    def message_from_pilot(self, data: MessageData) -> None:
        pass

    def message_from_copilot(self, data: MessageData) -> None:
        pass