from dataclasses import dataclass

from game_controllers import ControllerInput


@dataclass
class SourceData:
    pass


@dataclass
class InputData(SourceData):
    input: ControllerInput


@dataclass
class PilotInputData(SourceData):
    input: ControllerInput
    assistance_level: float


@dataclass
class CopilotInputData(SourceData):
    input: ControllerInput
    confidence_level: float


@dataclass
class MessageData(SourceData):
    message: str
