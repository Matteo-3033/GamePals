from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # Avoid Circular Imports
    import agents.actor
    import sources


@dataclass
class InputData:
    """ The wrapper class of the Data sent to a Controller Observer """
    c_input: "sources.ControllerInput"


@dataclass
class ActorData:
    """ The wrapper class of the Input Data sent to an Actor Observer """
    actor_id: "agents.actor.ActorID"
    c_input: "sources.ControllerInput"
    confidence: float


@dataclass
class MessageData:
    """ The wrapper class of the String Data sent to an Actor Observer """
    actor_id: "agents.actor.ActorID"
    message: str


@dataclass
class ArbitratorData:
    """ The wrapper class of the Data sent to an Arbitrator Observer [WIP] """
    pass
