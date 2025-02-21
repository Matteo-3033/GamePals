import json
from typing import override

from agents import CopilotInputData, MessageData
from agents.copilot import Copilot
from agents.observers.copilot_observer import CopilotObserver
from doom import GameLogMessage, MessageType
from doom.copilots.aimer_copilot import AimerCopilot
from doom.copilots.doom_copilot import DoomCopilot
from doom.copilots.runner_copilot import RunnerCopilot
from doom.copilots.shooter_copilot import ShooterCopilot
from doom.gamestate_listener import GameStateListener
from doom.observers.gamestate_observer import GameStateObserver


class ExpertSystemCopilot(Copilot, CopilotObserver, GameStateObserver):
    """
    The ExpertSystemCopilot class represents the implementation of a Software Agent Copilot for the game Ultimate Doom.
    It represents a Rule-Based System that reads the Game State and notifies its subscribers with some Controller Inputs.
    """

    def __init__(self, log_file_path: str):
        super().__init__()
        self.copilots: list[DoomCopilot] = []
        self.game_state_listener: GameStateListener = GameStateListener(log_file_path)
        self.game_state_listener.subscribe(self)

        # Register Copilots here
        self.register_copilot(RunnerCopilot())
        self.register_copilot(ShooterCopilot())
        self.register_copilot(AimerCopilot())

    def register_copilot(self, copilot: DoomCopilot) -> None:
        """
        Registers a Copilot to inform about the Game State
        """
        self.copilots.append(copilot)
        copilot.subscribe(self)

    @override
    def start(self) -> None:
        """
        Starts listening to the physical controller inputs and notifies its subscribers
        """
        self.game_state_listener.start_listening()

    def input_from_copilot(self, data: CopilotInputData) -> None:
        """
        Receives updates from the DoomCopilots and notifies its subscribers with those inputs
        """
        input = data.input
        confidence_level = data.confidence_level
        return self.notify_inputs(input, confidence_level)

    def update_from_game_state(self, state: GameLogMessage) -> None:
        """
        Receives Game State Updates and notifies its subscribers with Controller Inputs and Confidence Levels
        """
        match state.type:

            case MessageType.RESET:
                # Reset all Controls
                self.notify_metacommand("RESET")

            case MessageType.GAMESTATE:
                game_state = json.loads(state.json)
                for copilot in self.copilots:
                    copilot.receive_game_state(game_state)

    def message_from_copilot(self, data: MessageData) -> None:
        pass
