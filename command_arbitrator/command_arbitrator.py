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

        self.pilot_inputs_map.set(input)
        
        if (input.type in self.virtual_controller.STICKS): # Input is from a Stick
            
            if input.type == InputType.STICK_LEFT_X or input.type == InputType.STICK_LEFT_Y: # Left Stick
                x_val = self.pilot_inputs_map.get(InputType.STICK_LEFT_X)[0]
                y_val = self.pilot_inputs_map.get(InputType.STICK_LEFT_Y)[0]
            else: # Right Stick
                x_val = self.pilot_inputs_map.get(InputType.STICK_RIGHT_X)[0]
                y_val = self.pilot_inputs_map.get(InputType.STICK_RIGHT_Y)[0]
                
            self.virtual_controller.execute_stick(input_x = x_val, input_y = y_val)
            
        else: # Input is not from a Stick
            self.virtual_controller.execute(input)
            
        
        
    def update_from_copilot(self, input : ControllerInput, confidence_level : float) -> None:
        """
        Receives Controller Inputs
        """
        #print(f"Received input {input.type} with value {input.val} from Copilot")
        
        self.copilot_inputs_map.set(input)
        
        if (input.type in self.virtual_controller.STICKS): # Input is from a Stick
            
            if input.type == InputType.STICK_LEFT_X or input.type == InputType.STICK_LEFT_Y: # Left Stick
                x_val = self.copilot_inputs_map.get(InputType.STICK_LEFT_X)[0]
                y_val = self.copilot_inputs_map.get(InputType.STICK_LEFT_Y)[0]
            else: # Right Stick
                x_val = self.copilot_inputs_map.get(InputType.STICK_RIGHT_X)[0]
                y_val = self.copilot_inputs_map.get(InputType.STICK_RIGHT_Y)[0]
                
            self.virtual_controller.execute_stick(input_x = x_val, input_y = y_val)
            
        else: # Input is not from a Stick
            self.virtual_controller.execute(input)
                
        
