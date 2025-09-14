import time
from dataclasses import dataclass

from . import ControllerInputWithConfidence
from .controller_inputs import ControllerInput, InputType


@dataclass
class ControllerInputRecord:
    """ControllerInputRecord stores the value of an input, the associated confidence level and the timestamp of acquisition"""

    val: float
    confidence: float
    timestamp: float


class ControllerInputsMap:
    """
    ControllerInputsMap is a class that stores for each Input a corresponding ControllerInputRecord
    """

    def __init__(self) -> None:
        self.inputs_map = {i: ControllerInputRecord(0, 0, 0) for i in InputType}

    def set(
        self,
        c_input: ControllerInputWithConfidence,
        timestamp: float | None = None,
    ) -> None:
        """
        Updates the entry of the value for an input_type.

        If timestamp is not specified, it uses current time.
        """
        if timestamp is None:
            timestamp = time.time()

        self.inputs_map[c_input.type] = ControllerInputRecord(
            val=c_input.val, confidence=c_input.confidence, timestamp=timestamp
        )

    def get(self, c_input: InputType) -> tuple[ControllerInput, ControllerInputRecord]:
        """Returns the ControllerInput and the ControllerInputRecord associated with the input."""
        record = self.inputs_map[c_input]
        return ControllerInput(type=c_input, val=record.val), record
