import threading
import inputs

from agents import InputData
from agents.input_source import InputSource
from agents.observers.input_observer import InputObserver
from game_controllers import ControllerInput, InputType


class PhysicalControllerListener:
    """
    The PhysicalControllerListener class is a particular Input Source for InputData.

    It listens to the inputs of a Physical Controller and notifies its subscribers with Controller Inputs.

    It runs in a separate thread.
    """

    def __init__(self):
        self.input_source : InputSource[InputData] = InputSource[InputData]()
        self.running : bool = False
        self.listener_thread : threading.Thread = None

    def subscribe(self, subscriber : InputObserver) -> None:
        """ Adds a subscriber to the list of subscribers """
        subscriber.subscribe_to_input_source(self.input_source)

    def notify_all(self, input : ControllerInput) -> None:
        """ Notifies all subscribers of an input, wrapped in an InputData object """
        self.input_source.notify_all(InputData(input))

    def start_listening(self) -> None:
        """  Starts listening to the physical controller inputs and notifies its subscribers """
        if self.listener_thread is None or not self.listener_thread.is_alive():
            self.running = True
            self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listener_thread.start()

    def stop_listening(self) -> None:
        """ Stops listening for inputs """
        self.running = False
        if self.listener_thread:
            self.listener_thread.join()

    def _listen_loop(self) -> None:
        """ The loop that listens for controller inputs """
        while self.running:
            try:
                events = inputs.get_gamepad()
            except Exception as e:
                print(f"Error while getting gamepad events: {e}")
                return

            for event in events:
                if event.ev_type == "Sync":
                    continue

                observed = self.event_to_input(event)
                if observed:
                    self.notify_all(observed)

    def event_to_input(self, event) -> ControllerInput:
        """ Converts an event from the physical controller to a Controller Input """
        if event.code not in self.INPUT_TYPES_MAP:
            return None  # Ignore unmapped inputs

        input_type = self.INPUT_TYPES_MAP[event.code]
        input_value = event.state
        return ControllerInput(input_type, input_value)


    INPUT_TYPES_MAP = {
        "BTN_SOUTH" :InputType.BTN_A,
        "BTN_EAST": InputType.BTN_B,
        "BTN_NORTH": InputType.BTN_Y,
        "BTN_WEST": InputType.BTN_X,
        "BTN_TR": InputType.BUMPER_RIGHT,
        "BTN_TL": InputType.BUMPER_LEFT,
        "BTN_THUMBR": InputType.THUMB_RIGHT,
        "BTN_THUMBL": InputType.THUMB_LEFT,
        "ABS_HAT0X": InputType.DIR_PAD_X,
        "ABS_HAT0Y": InputType.DIR_PAD_Y,
        "ABS_RZ": InputType.TRIGGER_RIGHT,
        "ABS_Z": InputType.TRIGGER_LEFT,
        "ABS_RX": InputType.STICK_RIGHT_X,
        "ABS_RY": InputType.STICK_RIGHT_Y,
        "ABS_X": InputType.STICK_LEFT_X,
        "ABS_Y": InputType.STICK_LEFT_Y,
        "BTN_START": InputType.BTN_BACK,
        "BTN_SELECT": InputType.BTN_START,
    }
