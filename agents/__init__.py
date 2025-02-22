from dataclasses import dataclass

from agents.actor import ActorID
from input_sources import ControllerInput

@dataclass
class SourceData:
    pass

@dataclass
class InputData(SourceData):
    c_input : ControllerInput

@dataclass
class ActorData(SourceData):
    actor_id : ActorID
    c_input : ControllerInput
    confidence : float


@dataclass
class MessageData(SourceData):
    actor_id : ActorID
    message: str

