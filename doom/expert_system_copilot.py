from agents.copilot import Copilot
from doom.observers import GameStateObserver
from doom.utils import GameStateMessage, MessageType
from game_controllers.utils import ControllerInput, InputType
from doom.game_state_listener import GameStateListener
import json
import math

class ExpertSystemCopilot(Copilot, GameStateObserver):
    """
    The ExpertSystemCopilot class represents the implementation of a Software Agent Copilot for the game Ultimate Doom.
    It represents a Rule-Based System that reads the Game State and notifies its subscribers with some Controller Inputs.
    """
    
    def __init__(self, log_file_path : str):
        super().__init__()
        self.game_state_listener = GameStateListener(log_file_path)
        self.game_state_listener.subscribe(self)
        
    def start(self) -> None:
        """
        Starts listening to the physical controller inputs and notifies its subscribers
        """
        self.game_state_listener.start_listening()
        
    def update_from_game_state(self, state: GameStateMessage) -> None:
        """
        Receives Game State Updates and notifies its subscribers with Controller Inputs and Confidence Levels
        """
        match state.type:
            case MessageType.AIMED_AT:
                self.process_aimed_at_message(state.message)
            case MessageType.MONSTERS:
                self.process_monsters_message(state.message)
                              
    def process_aimed_at_message(self, message : str) -> None:
        """
        Processes the AIMED_AT message and notifies subscribers
        """
        inputs = []
        confidence_level = 1.0 # This will be replaced by the actual value
        messageData = json.loads(message)
        if messageData['entityType'] == 'Monster':
            inputs.append(ControllerInput(type=InputType.TRIGGER_RIGHT, val = 255))
        else:
            inputs.append(ControllerInput(type=InputType.TRIGGER_RIGHT, val = 0))
            
        if inputs:      
            for input in inputs:
                self.notify_all(input, confidence_level)
            
    def process_monsters_message(self, message : str) -> None:
        """
        Processes the MONSTERS message and notifies subscribers
        """
        inputs = []
        confidence_level = 1.0 # This will be replaced by the actual value
        monsters = json.loads(message)
        
        # Filter for monsters only in the FOV (optional)
        #monsters = [m for m in monsters if m['inFOV']]
        
        if len(monsters) == 0:
            inputs.append(ControllerInput(type=InputType.STICK_RIGHT_X, val = 0))
            inputs.append(ControllerInput(type=InputType.STICK_RIGHT_Y, val = 0))
            if inputs:      
                for input in inputs:
                    self.notify_all(input, confidence_level)
            return
        
        
        closest = min(monsters, key = lambda m: math.hypot(m['relativeAngle'], m['relativePitch'])) # Closest to the crosshair, not to the player
        distance = math.hypot(closest['relativeAngle'], closest['relativePitch'])
        
        intensity = ExpertSystemCopilot.aim_pull_intensity(distance, closest['distance'])
        if intensity == 0:
            return
        
        angle = math.atan2(closest['relativePitch'], closest['relativeAngle'])
        (x, y) = ExpertSystemCopilot.polar_to_cartesian(intensity, angle)
        inputs.append(ControllerInput(type=InputType.STICK_RIGHT_X, val = x))
        inputs.append(ControllerInput(type=InputType.STICK_RIGHT_Y, val = y))
            
        if inputs:      
            for input in inputs:
                self.notify_all(input, confidence_level)
                
    
    def polar_to_cartesian(rho : float, theta : float) -> tuple[float, float]:
        return (rho * math.cos(theta), rho * math.sin(theta))
    
    def aim_pull_intensity(distance_on_screen : float, distance_3d : float) -> int:
        """
        Returns the intensity of the pull towards the enemy, based on the distance on the screen and the 3D distance
        """
        if distance_on_screen > 10000: # The current limit to activate aim lock
            return 0
        p = 10 - 0.008 * distance_3d
        i = int((distance_on_screen / max(distance_on_screen, p)) * 32767)
        return i
        