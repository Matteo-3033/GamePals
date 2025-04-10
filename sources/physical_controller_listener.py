import logging
import threading

from inputs import devices

from .controller import ControllerInput, ControllerObserver, InputData, InputType

logger = logging.getLogger(__name__)


class PhysicalControllerListener:
    """
    The PhysicalControllerListener class listens to the inputs of a Physical Controller and
    notifies its subscribers with Controller Inputs.

    It runs in a separate thread.
    """

    def __init__(self, gamepad_number: int):
        # gamepad_number is the index of the device in the inputs.devices.gamepads list
        self.gamepad_number = gamepad_number
        self.subscribers: list[ControllerObserver] = []
        self.running: bool = False
        self.listener_thread: threading.Thread | None = None
        try:
            self.gamepad = devices.gamepads[gamepad_number]
        except IndexError:
            logger.error("Gamepad %d not found", gamepad_number)
            raise Exception(f"Gamepad {gamepad_number} not found")

    def subscribe(self, subscriber: ControllerObserver) -> None:
        """Adds a subscriber to the list of subscribers"""
        self.subscribers.append(subscriber)

    def notify_all(self, c_input: ControllerInput) -> None:
        """Notifies all subscribers of an input, wrapped in an InputData object"""
        data = InputData(c_input)
        logger.info("Sending data %s", data)
        for subscriber in self.subscribers:
            subscriber.receive_controller_input(data)

    def start_listening(self) -> None:
        """Starts listening to the physical controller inputs and notifying its subscribers"""
        if self.listener_thread is None or not self.listener_thread.is_alive():
            self.running = True
            self.listener_thread = threading.Thread(
                target=self._listen_loop, daemon=True
            )
            self.listener_thread.start()

    def stop_listening(self) -> None:
        """Stops listening for inputs"""
        self.running = False
        if self.listener_thread:
            self.listener_thread.join()

    def _listen_loop(self) -> None:
        """The loop that listens for controller inputs"""
        while self.running:
            try:
                events = self.gamepad.read()
            except Exception as e:
                logger.error("Error while getting gamepad events: %s", e)
                return

            for event in events:
                if event.ev_type == "Sync":
                    continue

                observed = self.event_to_input(event)
                if observed:
                    self.notify_all(observed)

    def event_to_input(self, event) -> ControllerInput | None:
        """Converts an event from the physical controller to a Controller Input"""
        if event.code not in self.INPUT_TYPES_MAP:
            return None  # Ignore unmapped inputs

        input_types = self.INPUT_TYPES_MAP[event.code]

        if len(input_types) == 1:
            idx = 1
        else: # It's a stick, with split axis
            idx = 0 if event.state >= 0 else 1

        input_value = self.normalize(input_types[idx], event.state)
        return ControllerInput(input_types[idx], input_value)

    @staticmethod
    def normalize(input_type: InputType, val: int) -> float:
        """Normalizes the value of the input into relative values between -1 and 1 (or 0 and 1)"""
        match input_type:
            case InputType.TRIGGER_RIGHT | InputType.TRIGGER_LEFT:
                return val / 255
            case (
                InputType.STICK_LEFT_X_POS
                | InputType.STICK_LEFT_X_NEG
                | InputType.STICK_LEFT_Y_POS
                | InputType.STICK_LEFT_Y_NEG
                | InputType.STICK_RIGHT_X_POS
                | InputType.STICK_RIGHT_X_NEG
                | InputType.STICK_RIGHT_Y_POS
                | InputType.STICK_RIGHT_Y_NEG
            ):
                return val / 32767
            case _:
                return val

    def get_index(self) -> int:
        return self.gamepad_number

    # Map of conversions between "inputs" (the package) identifiers and the InputType enum.
    INPUT_TYPES_MAP = {
        "BTN_SOUTH": [InputType.BTN_A],
        "BTN_EAST": [InputType.BTN_B],
        "BTN_NORTH": [InputType.BTN_Y],
        "BTN_WEST": [InputType.BTN_X],
        "BTN_TR": [InputType.BUMPER_RIGHT],
        "BTN_TL": [InputType.BUMPER_LEFT],
        "BTN_THUMBR": [InputType.THUMB_RIGHT],
        "BTN_THUMBL": [InputType.THUMB_LEFT],
        "ABS_HAT0X": [InputType.DIR_PAD_X],
        "ABS_HAT0Y": [InputType.DIR_PAD_Y],
        "ABS_RZ": [InputType.TRIGGER_RIGHT],
        "ABS_Z": [InputType.TRIGGER_LEFT],
        "ABS_RX": [InputType.STICK_RIGHT_X_POS, InputType.STICK_RIGHT_X_NEG],
        "ABS_RY": [InputType.STICK_RIGHT_Y_POS, InputType.STICK_RIGHT_Y_NEG],
        "ABS_X": [InputType.STICK_LEFT_X_POS, InputType.STICK_LEFT_X_NEG],
        "ABS_Y": [InputType.STICK_LEFT_Y_POS, InputType.STICK_LEFT_Y_NEG],
        "BTN_START": [InputType.BTN_BACK],
        "BTN_SELECT": [InputType.BTN_START],
    }
