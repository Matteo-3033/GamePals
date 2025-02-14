import math
from game_controllers.utils import ControllerInput, InputType
from doom.utils import DoomCopilot, Math

class AimerCopilot(DoomCopilot):
    
    def __init__(self):
        super().__init__()
        
    def receive_game_state(self, game_state : dict[str, any]) -> None:
        """
        AimerCopilot checks the closest monster and aims at it.
        """
        monsters = game_state['MONSTERS']
        
        if len(monsters) == 0:
            self.notify_all(ControllerInput(type=InputType.STICK_RIGHT_X, val = 0.0), 0.0)
            self.notify_all(ControllerInput(type=InputType.STICK_RIGHT_Y, val = 0.0), 0.0)
            return
        
        monsters.sort(key = lambda m: AimerCopilot.proximity_factor(m)) # Sort by proximity factor
        target = monsters[0]
        target_proximity_factor = AimerCopilot.proximity_factor(target)
     
        angle = math.atan2(target['relativePitch'], target['relativeAngle'])
        intensity = int(target_proximity_factor * 32767)
        if intensity == 0: return
        (x, y) = Math.polar_to_cartesian(intensity, angle)

        # dist_screen1 = math.hypot(monsters[0]['relativeAngle'], monsters[0]['relativePitch'])
        # dist_screen2 = math.hypot(monsters[1]['relativeAngle'], monsters[1]['relativePitch']) if len(monsters) > 1 else 0
        # closest_monsters_diff = dist_screen2 - dist_screen1
        # c2 = Math.linear_mapping(closest_monsters_diff, (0, max(closest_monsters_diff, 50)), (1, 0))
        # confidence_level = min(1.0, c1 * 0.6 + c2 * 0.4)
        
        confidence_level = 1 - target_proximity_factor # Confidence is the most when the target is the closest
        self.notify_all(ControllerInput(type=InputType.STICK_RIGHT_X, val = x), confidence_level)
        self.notify_all(ControllerInput(type=InputType.STICK_RIGHT_Y, val = y), confidence_level)
    
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