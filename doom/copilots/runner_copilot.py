import math
from game_controllers.utils import ControllerInput, InputType
from doom.utils import DoomCopilot, Math

class RunnerCopilot(DoomCopilot):
    
    def __init__(self):
        super().__init__()
        
    def receive_game_state(self, game_state : dict[str, any]) -> None:
        """
        RunnerCopilot checks the closest monster and decides whether to run or not.
        """
        monsters = game_state['MONSTERS']
        
        if len(monsters) == 0:
            self.notify_all(ControllerInput(type=InputType.BTN_X, val = 1), 1.0)
            return
        
        monsters.sort(key = lambda m: RunnerCopilot.proximity_factor(m)) # Sort by proximity factor
        target = monsters[0]
        target_proximity_factor = RunnerCopilot.proximity_factor(target)
        target_distance_screen = math.hypot(target['relativeAngle'], target['relativePitch'])
        

        if (target_distance_screen > 10):
            confidence_level = target_proximity_factor
            self.notify_all(ControllerInput(type=InputType.BTN_X, val = 1), confidence_level)
        else:
            self.notify_all(ControllerInput(type=InputType.BTN_X, val = 0), 1.0) 
        
    @staticmethod
    def proximity_factor(monster : dict[str, any]) -> float:
        """
        Returns the proximity factor of a Monster, based on their distance on the screen (from the crosshair)
        and their 3D distance (from the player).
        The factor is the most when the enemy is the furthest, either on the screen or in 3D.
        """
        distance_on_screen = math.hypot(monster['relativeAngle'], monster['relativePitch'])
        distance_3d = monster['distance']
        p1 = Math.exponential_mapping(distance_on_screen, (0, max(distance_on_screen, 60)), (0, 1), p = 0.25)
        p2 = Math.exponential_mapping(distance_3d, (0, max(distance_3d, 1000)), (0, 1), p = 0.25)
        p = min(p1, p2)
        return p