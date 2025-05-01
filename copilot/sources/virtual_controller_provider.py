import logging
import time

import vgamepad as vg

from .controller import (
    ControllerInput,
    InputType,
    ControllerInputsMap,
    ControllerInputWithConfidence,
)

logger = logging.getLogger(__name__)


class VirtualControllerProvider:
    """
    The VirtualControllerProvider class provides an XBOX 360 Virtual Controller, whose inputs can be requested via the execute and execute_stick methods
    """

    INPUT_THRESHOLD: float = (
        0.7  # The float value after which the input is interpreted as a 1
    )

    def __init__(self):
        self.gamepad: vg.VX360Gamepad | None = None
        self.gamepad_state: ControllerInputsMap = ControllerInputsMap()
        self.left_stick_values: tuple[float, float] = (0, 0)  # (X, Y)
        self.right_stick_values: tuple[float, float] = (0, 0)  # (X, Y)

    def start(self) -> None:
        self.gamepad = vg.VX360Gamepad()

    def execute(self, c_input: ControllerInput) -> None:
        """
        Receives Controller Inputs and produces them on a Virtual Controller.

        Valid for any single-value Input Type.
        """

        assert self.gamepad is not None, "Gamepad not initialized. Call start() first."

        logger.debug("Received input %s", c_input)
        self.gamepad_state.set(
            ControllerInputWithConfidence(
                type=c_input.type, val=c_input.val, confidence=1.0
            )
        )

        if c_input.type in self.STICKS:
            if c_input.val > 0 and c_input.type in self.NEGATIVE_AXIS:
                c_input.val = -c_input.val
            if c_input.type in self.RIGHT_STICK:  # Right Stick
                if c_input.type in self.RIGHT_STICK_Y:
                    self.right_stick_values = (self.right_stick_values[0], c_input.val)
                else:
                    self.right_stick_values = (c_input.val, self.right_stick_values[1])
                self.gamepad.right_joystick_float(
                    x_value_float=self.right_stick_values[0],
                    y_value_float=self.right_stick_values[1],
                )
            elif c_input.type in self.LEFT_STICK:  # Left Stick
                if c_input.type in self.LEFT_STICK_Y:
                    self.left_stick_values = (self.left_stick_values[0], c_input.val)
                else:
                    self.left_stick_values = (c_input.val, self.left_stick_values[1])
                self.gamepad.left_joystick_float(
                    x_value_float=self.left_stick_values[0],
                    y_value_float=self.left_stick_values[1],
                )

        if c_input.type in self.BTN_TO_VGBUTTON:  # Press-Release Buttons
            if abs(c_input.val) > self.INPUT_THRESHOLD:
                self.gamepad.press_button(self.BTN_TO_VGBUTTON[c_input.type])
            else:
                self.gamepad.release_button(self.BTN_TO_VGBUTTON[c_input.type])

        elif c_input.type in self.DPADS:  # Direction Pad (values are -1, 0 or 1)
            if c_input.val != 0:
                self.gamepad.press_button(
                    self.DPAD_TO_VGBUTTON[(c_input.type, c_input.val)]
                )
            else:
                self.gamepad.release_button(self.DPAD_TO_VGBUTTON[(c_input.type, 1)])
                self.gamepad.release_button(self.DPAD_TO_VGBUTTON[(c_input.type, -1)])

        elif c_input.type in self.TRIGGERS:  # Triggers (values are in [0, 1])
            if c_input.type == InputType.TRIGGER_LEFT:
                self.gamepad.left_trigger_float(c_input.val)
            else:
                self.gamepad.right_trigger_float(c_input.val)

        self.gamepad.update()

    def reset_controls(self):
        """Releases all buttons of the Virtual Controller"""

        assert self.gamepad is not None, "Gamepad not initialized. Call start() first."

        time.sleep(
            0.5
        )  # This looks unnecessary, but it's needed for it to work even when the level is reset
        self.gamepad.reset()
        self.gamepad.update()
        logger.info("Gamepad was reset")
        time.sleep(0.1)

    def get_controller_state(self) -> str:
        return str(self.gamepad_state.inputs_map)

    # Map of conversions between the InputType enum and the vg.XUSB_BUTTON used by the package vgamepad
    BTN_TO_VGBUTTON = {
        InputType.BTN_A: vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
        InputType.BTN_B: vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
        InputType.BTN_Y: vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
        InputType.BTN_X: vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
        InputType.BUMPER_RIGHT: vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
        InputType.BUMPER_LEFT: vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
        InputType.THUMB_RIGHT: vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
        InputType.THUMB_LEFT: vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
        InputType.BTN_BACK: vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        InputType.BTN_START: vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
    }

    # Map of conversions between the InputType enum and the vg.XUSB_BUTTON used by the package vgamepad
    DPAD_TO_VGBUTTON = {
        (InputType.DIR_PAD_Y, -1.0): vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
        (InputType.DIR_PAD_Y, 1.0): vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
        (InputType.DIR_PAD_X, -1.0): vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
        (InputType.DIR_PAD_X, 1.0): vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    }

    # Arrays of InputTypes that can be used to check the category of the Input Type
    DPADS = [InputType.DIR_PAD_X, InputType.DIR_PAD_Y]
    TRIGGERS = [InputType.TRIGGER_LEFT, InputType.TRIGGER_RIGHT]
    LEFT_STICK_X = [InputType.STICK_LEFT_X_POS, InputType.STICK_LEFT_X_NEG]
    LEFT_STICK_Y = [InputType.STICK_LEFT_Y_POS, InputType.STICK_LEFT_Y_NEG]
    RIGHT_STICK_X = [InputType.STICK_RIGHT_X_POS, InputType.STICK_RIGHT_X_NEG]
    RIGHT_STICK_Y = [InputType.STICK_RIGHT_Y_POS, InputType.STICK_RIGHT_Y_NEG]
    LEFT_STICK = LEFT_STICK_X + LEFT_STICK_Y
    RIGHT_STICK = RIGHT_STICK_X + RIGHT_STICK_Y
    STICKS = LEFT_STICK + RIGHT_STICK

    AXIS_INPUTS = STICKS + TRIGGERS

    NEGATIVE_AXIS = [
        InputType.STICK_LEFT_X_NEG,
        InputType.STICK_LEFT_Y_NEG,
        InputType.STICK_RIGHT_X_NEG,
        InputType.STICK_RIGHT_Y_NEG,
    ]
