import time

from sources import ControllerInputRecord, InputType, ControllerInput


class ControllerInputsMap:
    """
    ControllerInputsMap is a class that stores for each Input a corresponding ControllerInputRecord
    """

    def __init__(self):
        self.inputs_map = {i: ControllerInputRecord(0, 0, 0) for i in InputType}

    def set(self, c_input: ControllerInput, level: float = 1.0, timestamp: float | None = None) -> None:
        """
        Updates the entry of the value for an input_type.

        If timestamp is not specified, it uses current time.
        """
        if timestamp is None:
            timestamp = time.time()

        self.inputs_map[c_input.type] = ControllerInputRecord(val=c_input.val, level=level, timestamp=timestamp)

    def get(self, c_input: InputType) -> tuple[ControllerInput, ControllerInputRecord]:
        """ Returns the ControllerInput and the ControllerInputRecord associated with the input. """
        record = self.inputs_map[c_input]
        return ControllerInput(type=c_input, val=record.val), record

