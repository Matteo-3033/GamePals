import json

from agents import MessageData, ActorData
from agents.sw_agent_actor import SWAgentActor
from doom import Math, DoomGameState, MessageType
from sources import ControllerInput, InputType, GameState


class ShooterCopilot(SWAgentActor):

    def get_controlled_inputs(self) -> list[InputType]:
        return [InputType.TRIGGER_RIGHT]  # Shoot button

    def receive_input_update(self, data: ActorData) -> None:
        # Ignore other Actors inputs
        pass

    def receive_message_update(self, data: MessageData) -> None:
        # Ignore other Actors messages
        pass

    def game_state_to_inputs(self, game_state: DoomGameState) -> list[tuple[ControllerInput, float]]:
        """ ShooterCopilot checks what the player is aiming at and decides whether to shoot or not. """
        if game_state.type != MessageType.GAMESTATE:
            return []

        game_data = json.loads(game_state.json)
        aimed_at = game_data['AIMED_AT']
        distance = aimed_at['distance']

        # Confidence is inversely proportional to the distance of the target from the player
        confidence_level = Math.linear_mapping(distance, (0, max(distance, 1000)), (1, 0))

        if aimed_at['entityType'] == 'Monster':
            c_input = ControllerInput(type=InputType.TRIGGER_RIGHT, val=255)
        else:
            c_input = ControllerInput(type=InputType.TRIGGER_RIGHT, val=0)

        return [(c_input, confidence_level)]
