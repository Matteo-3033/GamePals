import time

from input_sources import ControllerInputRecord, InputType, ControllerInput


class ControllerInputsMap:
    """
    ControllerInputsMap is a class that stores for each Input a corresponding ControllerInputRecord
    """

    def __init__(self):
        self.inputs_map = {input: ControllerInputRecord(0, 0, 0) for input in InputType}

    def set(self, input: ControllerInput, level: float = 1.0, timestamp: float | None = None) -> None:
        """
        Updates the value of an input
        """
        if timestamp is None:
            timestamp = time.time()

        self.inputs_map[input.type] = ControllerInputRecord(val=input.val, level=level, timestamp=timestamp)

    def get(self, input: InputType) -> tuple[ControllerInput, ControllerInputRecord]:
        """
        Returns the ControllerInput and the ControllerInputRecord associated with the input
        """
        record = self.inputs_map[input]
        return ControllerInput(type=input, val=record.val), record

