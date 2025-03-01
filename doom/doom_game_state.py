from enum import StrEnum

from sources.game_state import GameState


class MessageType(StrEnum):
    """ The Type of Game State Message """
    GAMESTATE = "GAMESTATE"  # The State of the Game, in the form of an unparsed JSON
    RESET = "RESET"  # Notifies that the Player has either spawned, respawned, unpaused or any other event that resets the controls


class DoomGameState(GameState):
    """ The Game State class for The Ultimate Doom """

    def __init__(self, msg_type: MessageType, json: str):
        super().__init__()
        self.type: MessageType = msg_type
        self.json: str = json
