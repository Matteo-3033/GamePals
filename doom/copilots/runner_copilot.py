import math

from doom import Math
from doom.copilots import proximity_factor
from doom.copilots.doom_copilot import DoomCopilot
from game_controllers import ControllerInput, InputType


class RunnerCopilot(DoomCopilot):

    def __init__(self):
        super().__init__()

    def receive_game_state(self, game_state: dict[str, any]) -> None:
        """
        RunnerCopilot checks the closest monster and decides whether to run or not.
        """
        monsters = game_state['MONSTERS']

        if len(monsters) == 0:
            self.notify_inputs(ControllerInput(type=InputType.BTN_X, val=1), 1.0)
            return

        monsters.sort(key=lambda m: proximity_factor(m))  # Sort by proximity factor
        target = monsters[0]
        target_proximity_factor = proximity_factor(target)
        target_distance_screen = math.hypot(target['relativeAngle'], target['relativePitch'])

        if target_distance_screen > 10:
            confidence_level = target_proximity_factor
            self.notify_inputs(ControllerInput(type=InputType.BTN_X, val=1), confidence_level)
        else:
            self.notify_inputs(ControllerInput(type=InputType.BTN_X, val=0), 1.0)

