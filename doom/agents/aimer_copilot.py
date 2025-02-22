import json
import math

from agents import ActorData, MessageData
from agents.sw_agent_actor import SWAgentActor
from doom import Math, DoomGameState, MessageType
from doom.agents import proximity_factor
from input_sources import ControllerInput, InputType


class AimerCopilot(SWAgentActor):

    def get_controlled_inputs(self) -> list[InputType]:
        return [InputType.STICK_RIGHT_X, InputType.STICK_RIGHT_Y]  # Aim buttons

    def receive_input_update(self, data: ActorData) -> None:
        # Ignore other Actors inputs
        pass

    def receive_message_update(self, data: MessageData) -> None:
        # Ignore other Actors messages
        pass

    def game_state_to_inputs(self, game_state: DoomGameState) -> list[tuple[ControllerInput, float]]:
        """ AimerCopilot checks the closest monster and aims at it. """
        if game_state.type != MessageType.GAMESTATE:
            return []

        game_data = json.loads(game_state.json)
        monsters = game_data['MONSTERS']

        if len(monsters) == 0:
            return [
                (ControllerInput(type=InputType.STICK_RIGHT_X, val=0), 0.0),
                (ControllerInput(type=InputType.STICK_RIGHT_Y, val=0), 0.0),
            ]

        monsters.sort(key=lambda m: proximity_factor(m))  # Sort by proximity factor
        target = monsters[0]
        target_proximity_factor = proximity_factor(target)

        angle = math.atan2(target['relativePitch'], target['relativeAngle'])
        intensity = int(target_proximity_factor * 32767)
        if intensity == 0: return []
        (x, y) = Math.polar_to_cartesian(intensity, angle)

        # dist_screen1 = math.hypot(monsters[0]['relativeAngle'], monsters[0]['relativePitch'])
        # dist_screen2 = math.hypot(monsters[1]['relativeAngle'], monsters[1]['relativePitch']) if len(monsters) > 1 else 0
        # closest_monsters_diff = dist_screen2 - dist_screen1
        # c2 = Math.linear_mapping(closest_monsters_diff, (0, max(closest_monsters_diff, 50)), (1, 0))
        # confidence_level = min(1.0, c1 * 0.6 + c2 * 0.4)

        confidence_level = 1 - target_proximity_factor  # Confidence is the most when the target is the closest
        return [
            (ControllerInput(type=InputType.STICK_RIGHT_X, val=int(x)), confidence_level),
            (ControllerInput(type=InputType.STICK_RIGHT_Y, val=int(y)), confidence_level),
        ]
