import math

from doom import Math
from doom.copilots import proximity_factor
from doom.copilots.doom_copilot import DoomCopilot
from input_sources import ControllerInput, InputType


class AimerCopilot(DoomCopilot):

    def __init__(self):
        super().__init__()

    def receive_game_state(self, game_state: dict[str, any]) -> None:
        """
        AimerCopilot checks the closest monster and aims at it.
        """
        monsters = game_state['MONSTERS']

        if len(monsters) == 0:
            self.notify_inputs(ControllerInput(type=InputType.STICK_RIGHT_X, val=0), 0.0)
            self.notify_inputs(ControllerInput(type=InputType.STICK_RIGHT_Y, val=0), 0.0)
            return

        monsters.sort(key=lambda m: proximity_factor(m))  # Sort by proximity factor
        target = monsters[0]
        target_proximity_factor = proximity_factor(target)

        angle = math.atan2(target['relativePitch'], target['relativeAngle'])
        intensity = int(target_proximity_factor * 32767)
        if intensity == 0: return
        (x, y) = Math.polar_to_cartesian(intensity, angle)

        # dist_screen1 = math.hypot(monsters[0]['relativeAngle'], monsters[0]['relativePitch'])
        # dist_screen2 = math.hypot(monsters[1]['relativeAngle'], monsters[1]['relativePitch']) if len(monsters) > 1 else 0
        # closest_monsters_diff = dist_screen2 - dist_screen1
        # c2 = Math.linear_mapping(closest_monsters_diff, (0, max(closest_monsters_diff, 50)), (1, 0))
        # confidence_level = min(1.0, c1 * 0.6 + c2 * 0.4)

        confidence_level = 1 - target_proximity_factor  # Confidence is the most when the target is the closest
        self.notify_inputs(ControllerInput(type=InputType.STICK_RIGHT_X, val=int(x)), confidence_level)
        self.notify_inputs(ControllerInput(type=InputType.STICK_RIGHT_Y, val=int(y)), confidence_level)

