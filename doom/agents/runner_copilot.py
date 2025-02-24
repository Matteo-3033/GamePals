import json
import math

from agents import MessageData, ActorData
from agents.sw_agent_actor import SWAgentActor
from doom import Math, DoomGameState, MessageType
from doom.agents import proximity_factor
from sources import ControllerInput, InputType, GameState


class RunnerCopilot(SWAgentActor):

    def get_controlled_inputs(self) -> list[InputType]:
        return [InputType.BTN_X]  # Run button

    def receive_input_update(self, data: ActorData) -> None:
        # Ignore other Actors inputs
        pass

    def receive_message_update(self, data: MessageData) -> None:
        # Ignore other Actors messages
        pass

    def game_state_to_inputs(self, game_state: DoomGameState) -> list[tuple[ControllerInput, float]]:
        """ RunnerCopilots checks whether a monster is close to the player. If not, it decides to run """
        if game_state.type != MessageType.GAMESTATE:
            return []

        game_data = json.loads(game_state.json)
        monsters = game_data['MONSTERS']

        if len(monsters) == 0:
            return [(ControllerInput(type=InputType.BTN_X, val=1), 1.0)]

        monsters.sort(key=lambda m: proximity_factor(m))  # Sort by proximity factor
        target = monsters[0]
        target_proximity_factor = proximity_factor(target)
        target_distance_screen = math.hypot(target['relativeAngle'], target['relativePitch'])

        if target_distance_screen > 10:
            confidence_level = target_proximity_factor
            return [(ControllerInput(type=InputType.BTN_X, val=1), confidence_level)]

        return [(ControllerInput(type=InputType.BTN_X, val=0), 1.0)]
