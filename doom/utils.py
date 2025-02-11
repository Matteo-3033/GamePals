from dataclasses import dataclass
from enum import StrEnum

class MessageType(StrEnum):
    AIMED_AT = "AIMED_AT" # The Object aimed at by the Player
    MONSTERS = "MONSTERS" # The Monsters on the Screen

@dataclass
class GameStateMessage:
    type : MessageType
    message : str