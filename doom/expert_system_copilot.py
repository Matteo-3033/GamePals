from agents.copilot import Copilot
from doom.observers import GameStateObserver
from doom.utils import GameStateMessage, Math, MessageType
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
        messageData = json.loads(message)
        distance = messageData['distance']
        # Confidence is inversely proportional to the distance of the target from the player
        confidence_level = Math.linear_mapping(distance, (0, max(distance, 1000)), (1, 0)) 
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
        monsters = json.loads(message)
        
        # Filter for monsters only in the FOV (optional)
        #monsters = [m for m in monsters if m['inFOV']]
        
        if len(monsters) == 0:
            inputs.append(ControllerInput(type=InputType.STICK_RIGHT_X, val = 0))
            inputs.append(ControllerInput(type=InputType.STICK_RIGHT_Y, val = 0))
            if inputs:      
                for input in inputs:
                    self.notify_all(input, 0.0)
            return
        
        
        monsters.sort(key = lambda m: math.hypot(m['relativeAngle'], m['relativePitch'])) # Closest to the crosshair, not to the player
        closest = monsters[0]
        distance = math.hypot(closest['relativeAngle'], closest['relativePitch'])
        
        intensity = ExpertSystemCopilot.aim_pull_intensity(distance, closest['distance'])
        if intensity == 0:
            return
        
        angle = math.atan2(closest['relativePitch'], closest['relativeAngle'])
        (x, y) = Math.polar_to_cartesian(intensity, angle)
        inputs.append(ControllerInput(type=InputType.STICK_RIGHT_X, val = x))
        inputs.append(ControllerInput(type=InputType.STICK_RIGHT_Y, val = y))
            
        dist_screen1 = math.hypot(monsters[0]['relativeAngle'], monsters[0]['relativePitch'])
        dist_screen2 = math.hypot(monsters[1]['relativeAngle'], monsters[1]['relativePitch']) if len(monsters) > 1 else 0
        closest_monsters_diff = dist_screen2 - dist_screen1
        
        c1 = 1 - intensity / 32767 # Inverse of the intensity
        c2 = Math.linear_mapping(closest_monsters_diff, (0, max(closest_monsters_diff, 50)), (1, 0))
        confidence_level = min(1.0, c1 * 0.6 + c2 * 0.4)
        
        print(intensity, confidence_level)
        
        if inputs:      
            for input in inputs:
                self.notify_all(input, confidence_level)
                
        
    def aim_pull_intensity(distance_on_screen : float, distance_3d : float) -> int:
        """
        Returns the intensity of the pull towards the enemy, based on the distance on the screen and the 3D distance.
        Intensity is the most when the enemy is the furthest (on the screen or in 3D).
        """
        p1 = Math.exponential_mapping(distance_on_screen, (0, max(distance_on_screen, 60)), (0, 1), p = 0.25)
        p2 = Math.exponential_mapping(distance_3d, (0, max(distance_3d, 1000)), (0, 1), p = 0.25)
        p = min(p1, p2)
        i = int(p * 32767)
        return i
        