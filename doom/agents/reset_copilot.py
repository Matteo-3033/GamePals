from agents import MessageData, ActorData
from agents.sw_agent_actor import SWAgentActor
from doom import DoomGameState, MessageType
from sources import ControllerInput, InputType


class ResetCopilot(SWAgentActor):
    """
    ResetCopilot is a Copilot that resets the controller when necessary.
    """

    def get_controlled_inputs(self) -> list[InputType]:
        return []  # No button

    def receive_input_update(self, data: ActorData) -> None:
        # Ignore other Actors inputs
        pass

    def receive_message_update(self, data: MessageData) -> None:
        # Ignore other Actors messages
        pass

    def game_state_to_inputs(self, game_state: DoomGameState) -> list[tuple[ControllerInput, float]]:
        """ RunnerCopilots sends a reset message if the Game State is Reset """
        if game_state.type == MessageType.RESET:
            self.notify_message("RESET")
        return []
