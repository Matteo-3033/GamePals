import json
import math

from agents.sw_agent_actor import SWAgentActor
from doom.doom_game_state import DoomGameState, MessageType
from doom.utils import polar_to_cartesian, proximity_factor
from sources.controller_inputs import ControllerInput, InputType
from sources.game_state_listener import GameStateListener


class AimerCopilot(SWAgentActor):

    def __init__(self, game_state: GameStateListener):
        super().__init__(game_state)
        self.zero_input_sent = False # Needed to avoid sending zero-value inputs more than once

    def get_controlled_inputs(self) -> list[InputType]:
        return [InputType.STICK_RIGHT_X, InputType.STICK_RIGHT_Y]  # Aim buttons

    def get_arbitrated_inputs(self, input_data: ControllerInput) -> None:
        # Ignore Arbitrated Inputs
        pass

    def game_state_to_inputs(self, game_state: DoomGameState) -> list[tuple[ControllerInput, float]]:
        """ AimerCopilot checks the closest monster and aims at it. """
        if game_state.type != MessageType.GAMESTATE:
            return []

        game_data = json.loads(game_state.json)
        monsters = game_data['MONSTERS']

        if len(monsters) == 0:
            if not self.zero_input_sent:
                self.zero_input_sent = True
                return [
                    (ControllerInput(type=InputType.STICK_RIGHT_X, val=0), 1.0),
                    (ControllerInput(type=InputType.STICK_RIGHT_Y, val=0), 1.0),
                ]
            return []

        self.zero_input_sent = False

        monsters.sort(key=lambda m: proximity_factor(m))  # Sort by proximity factor
        target = monsters[0]
        target_proximity_factor = proximity_factor(target)

        angle = math.atan2(target['relativePitch'], target['relativeAngle'])
        if target_proximity_factor == 0: return []
        (x, y) = polar_to_cartesian(target_proximity_factor, angle)

        # dist_screen1 = math.hypot(monsters[0]['relativeAngle'], monsters[0]['relativePitch'])
        # dist_screen2 = math.hypot(monsters[1]['relativeAngle'], monsters[1]['relativePitch']) if len(monsters) > 1 else 0
        # closest_monsters_diff = dist_screen2 - dist_screen1
        # c2 = Math.linear_mapping(closest_monsters_diff, (0, max(closest_monsters_diff, 50)), (1, 0))
        # confidence_level = min(1.0, c1 * 0.6 + c2 * 0.4)

        confidence_level = 1 - target_proximity_factor  # Confidence is the most when the target is the closest
        return [
            (ControllerInput(type=InputType.STICK_RIGHT_X, val=x), confidence_level),
            (ControllerInput(type=InputType.STICK_RIGHT_Y, val=y), confidence_level),
        ]
