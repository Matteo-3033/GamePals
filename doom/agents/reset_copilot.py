from agents.sw_agent_actor import SWAgentActor
from doom import DoomGameState, MessageType
from sources import ControllerInput, InputType


class ResetCopilot(SWAgentActor):
    """
    ResetCopilot is a Copilot that resets the controller when necessary.
    """

    def get_controlled_inputs(self) -> list[InputType]:
        return []  # No button

    def get_arbitrated_inputs(self, input_data: ControllerInput) -> None:
        # Ignore Arbitrated Inputs
        pass

    def game_state_to_inputs(self, game_state: DoomGameState) -> list[tuple[ControllerInput, float]]:
        """ RunnerCopilots sends a reset message if the Game State is Reset """
        if game_state.type == MessageType.RESET:
            self.notify_message("RESET")
        return []
