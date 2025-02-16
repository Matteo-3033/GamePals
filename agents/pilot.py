from agents.input_source import CopilotInputData, InputData, InputSource, MessageData, PilotInputData
from game_controllers.physical_controller_listener import PhysicalControllerListener
from agents.observers import CopilotObserver, InputObserver, PilotObserver
from game_controllers.utils import ControllerInput, InputType
import tomllib

class Pilot(InputObserver, CopilotObserver):
    """
    The Pilot class represents the Pilot in the Shared Control System.
    
    The Pilot:
    - listens to a Physical Controller
    - notifies its subscribers with Inputs from the Controller, together with the Assistance Level
    - notifies its subscribers with Metacommands (messages)
    
    It also receives messages (and inputs) from the Copilot.
    """
    
    def __init__(self, config_file_path : str):
        self.pilot_inputs_source : InputSource[PilotInputData] = InputSource[PilotInputData]() # Pilot inputs and assistance levels
        self.pilot_metacommands_source : InputSource[str] = InputSource[str]() # Metacommands are messages that are not inputs
        self.controller_listener : PhysicalControllerListener = PhysicalControllerListener()
        self.assistance_levels : dict[InputType, float] = {}
        
        self.controller_listener.subscribe(self)
        
        with open(config_file_path, 'rb') as config_file:
            config = tomllib.load(config_file)
            self.assistance_levels = config["AssistanceLevels"]
            
    def subscribe(self, observer : PilotObserver) -> None:
        """ 
        Subscribe an Observer to the Pilot 
        """
        observer.subscribe_to_pilot(self)
        
    def notify_inputs(self, input : ControllerInput, assistance_level : float) -> None:
        """ 
        Notify all subscribers with the input and the assistance level 
        """
        self.pilot_inputs_source.notify_all(PilotInputData(input, assistance_level))
        
    def notify_metacommand(self, message : str) -> None:
        """ 
        Notify all subscribers with a message 
        """
        self.pilot_metacommands_source.notify_all(message)
            
    def start(self) -> None:
        """ 
        Starts listening to the physical controller inputs and notifies its subscribers 
        """
        
        # Notify all subscribers of the Assistance Levels (using zero-value inputs)
        for key, value in self.assistance_levels.items():
            zero_input = ControllerInput(type=InputType[key], val=0)
            self.notify_inputs(zero_input, value)
        
        self.controller_listener.start_listening()
        
    def input_from_source(self, data : InputData) -> None:
        """ 
        Receives Controller Inputs from the Physical Controller and notifies its subscribers with the Assistance Level 
        """
        assistance_level = self.assistance_levels[data.input.type]
        self.notify_inputs(data.input, assistance_level)

    def input_from_copilot(self, data : CopilotInputData) -> None:
        """ 
        Receives Controller Inputs and the Assistance Level sent by the Copilot 
        """
        pass
    
    def message_from_copilot(self, data: MessageData) -> None:
        """ Receives a message from the Copilot. Messages are usually Metacommands """
        print(f"Pilot received a message from Copilot: {data.message}")