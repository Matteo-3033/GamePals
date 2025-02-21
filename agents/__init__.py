from dataclasses import dataclass

from game_controllers import ControllerInput

@dataclass
class SourceData:
    pass

@dataclass
class InputData(SourceData):
    c_input : ControllerInput

@dataclass
class ActorData(SourceData):
    c_input : ControllerInput
    confidence : float


@dataclass
class MessageData(SourceData):
    message: str

@dataclass
class GameState:
    pass