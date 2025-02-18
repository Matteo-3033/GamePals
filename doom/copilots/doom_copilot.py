from abc import ABC, abstractmethod

from agents.copilot import Copilot


class DoomCopilot(Copilot, ABC):
    """
    The DoomCopilot class represents a Software Agent Copilot dedicated to a specific action for the game Ultimate Doom.
    """

    @abstractmethod
    def receive_game_state(self, game_state: dict[str, any]) -> None:
        """
        Receives the updated Game State, on which the Copilot will decide and notify the action to take.
        """
        pass