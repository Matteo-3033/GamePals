from game_controllers.virtual_controller_provider import VirtualControllerProvider
from game_controllers.utils import ControllerInput, ControllerInputsMap, InputType
from agents.observers import CopilotInputsObserver, PilotInputsObserver
from agents.copilot import Copilot
from agents.pilot import Pilot

class CommandArbitrator(PilotInputsObserver, CopilotInputsObserver):
    """
    The CommandArbitrator class arbitrates between the inputs from the Pilot and the Copilot, then it sends the final command to a Virtual Controller.
    """
    
    def __init__(self, pilot : Pilot, copilot : Copilot):
        self.pilot : Pilot = pilot
        self.copilot : Copilot = copilot
        self.virtual_controller : VirtualControllerProvider = VirtualControllerProvider()
        
        # Latest Inputs from the Pilot and Copilot
        self.pilot_inputs_map : ControllerInputsMap = ControllerInputsMap()
        self.copilot_inputs_map : ControllerInputsMap = ControllerInputsMap()
        
        # Receive Updates from the Pilot and Copilot
        self.pilot.subscribe(self)
        self.copilot.subscribe(self)
    
    def update_from_pilot(self, input : ControllerInput, assistance_level : float) -> None:
        """
        Receives Controller Inputs
        """
        #print(f"Received input {input.type} with value {input.val} from Pilot")
        self.pilot_inputs_map.set(input, assistance_level)
        self.merge_inputs(input.type)
            
        
    def update_from_copilot(self, input : ControllerInput, confidence_level : float) -> None:
        """
        Receives Controller Inputs
        """
        #print(f"Received input {input.type} with value {input.val} from Copilot")        
        last_input = self.copilot_inputs_map.get(input.type)
        if input.val == 0 and last_input[0].val == input.val:
            return # Avoid sending a zero-input twice
        
        self.copilot_inputs_map.set(input, confidence_level)
        self.merge_inputs(input.type)
        
            
    def merge_inputs(self, type : InputType) -> None:
        """
        Merges the inputs from the Pilot and Copilot
        """
        if (type in self.virtual_controller.STICKS): 
            self.merge_continuous_inputs(type)
        else:
            self.merge_binary_inputs(type)
            
            
    def merge_binary_inputs(self, type : InputType) -> None:
        """
        Merges the binary inputs from the Pilot and Copilot
        """
        (pilot_input, pilot_input_details) = self.pilot_inputs_map.get(type)
        (copilot_input, copilot_input_details) = self.copilot_inputs_map.get(type)
        
        I = pilot_input_details.level > 1 - copilot_input_details.level # Indicator Function I{c > 1 - b}
        if I:
            self.virtual_controller.execute(copilot_input)
        else:
            self.virtual_controller.execute(pilot_input)

    
    def merge_continuous_inputs(self, type : InputType) -> None:
        """
        Merges the continuous inputs from the Pilot and Copilot
        """
        if type == InputType.STICK_LEFT_X or type == InputType.STICK_LEFT_Y: # Left Stick
            (pilot_input_x, pilot_input_x_details) = self.pilot_inputs_map.get(InputType.STICK_LEFT_X)
            (pilot_input_y, pilot_input_y_details) = self.pilot_inputs_map.get(InputType.STICK_LEFT_Y)
            (copilot_input_x, copilot_input_x_details) = self.copilot_inputs_map.get(InputType.STICK_LEFT_X)
            (copilot_input_y, copilot_input_y_details) = self.copilot_inputs_map.get(InputType.STICK_LEFT_Y)
        else: # Right Stick
            (pilot_input_x, pilot_input_x_details) = self.pilot_inputs_map.get(InputType.STICK_RIGHT_X)
            (pilot_input_y, pilot_input_y_details) = self.pilot_inputs_map.get(InputType.STICK_RIGHT_Y)
            (copilot_input_x, copilot_input_x_details) = self.copilot_inputs_map.get(InputType.STICK_RIGHT_X)
            (copilot_input_y, copilot_input_y_details) = self.copilot_inputs_map.get(InputType.STICK_RIGHT_Y)
                
        # Send the most recent input atm
        most_recent_pilot = max(pilot_input_x_details.timestamp, pilot_input_y_details.timestamp)
        most_recent_copilot = max(copilot_input_x_details.timestamp, copilot_input_y_details.timestamp)
        
        if most_recent_pilot > most_recent_copilot:
            self.virtual_controller.execute_stick(input_x = pilot_input_x, input_y = pilot_input_y)
        else:
            self.virtual_controller.execute_stick(input_x = copilot_input_x, input_y = copilot_input_y)
            
            
        
