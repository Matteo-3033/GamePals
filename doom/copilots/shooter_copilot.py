from doom import Math
from doom.copilots.doom_copilot import DoomCopilot
from input_sources import ControllerInput, InputType


class ShooterCopilot(DoomCopilot):

    def __init__(self):
        super().__init__()

    def receive_game_state(self, game_state: dict[str, any]) -> None:
        """
        ShooterCopilot checks what the player is aiming at and decides whether to shoot or not.
        """
        aimed_at = game_state['AIMED_AT']
        distance = aimed_at['distance']

        # Confidence is inversely proportional to the distance of the target from the player
        confidence_level = Math.linear_mapping(distance, (0, max(distance, 1000)), (1, 0))

        if aimed_at['entityType'] == 'Monster':
            input = ControllerInput(type=InputType.TRIGGER_RIGHT, val=255)
        else:
            input = ControllerInput(type=InputType.TRIGGER_RIGHT, val=0)

        self.notify_inputs(input, confidence_level)