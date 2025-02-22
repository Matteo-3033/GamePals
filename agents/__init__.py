from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import agents.actor
    import input_sources


@dataclass
class SourceData:
    pass


@dataclass
class InputData(SourceData):
    c_input: "input_sources.ControllerInput"


@dataclass
class ActorData(SourceData):
    actor_id: "agents.actor.ActorID"
    c_input: "input_sources.ControllerInput"
    confidence: float


@dataclass
class MessageData(SourceData):
    actor_id: "agents.actor.ActorID"
    message: str


@dataclass
class ArbitratorData(SourceData):
    pass