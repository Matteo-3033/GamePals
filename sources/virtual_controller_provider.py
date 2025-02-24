import time

import vgamepad as vg

from sources import ControllerInput, InputType


class VirtualControllerProvider:
    """
    The VirtualControllerProvider class provides an XBOX 360 Virtual Controller, whose inputs can be requested via the execute and execute_stick methods
    """

    def __init__(self):
        self.gamepad: vg.VX360Gamepad = vg.VX360Gamepad()

    def execute(self, c_input: ControllerInput) -> None:
        """
        Receives Controller Inputs and produces them on a Virtual Controller.

        Valid for any single-value Input Type.
        """
        if c_input.type in self.STICKS:
            raise ValueError("Use execute_stick method to handle stick inputs")

        if c_input.type in self.BTN_TO_VGBUTTON:  # Press-Release Buttons
            if c_input.val == 1:
                self.gamepad.press_button(self.BTN_TO_VGBUTTON[c_input.type])
            else:
                self.gamepad.release_button(self.BTN_TO_VGBUTTON[c_input.type])

        elif c_input.type in self.DPADS:  # Direction Pad (values are -1, 0 or 1)
            if c_input.val != 0:
                self.gamepad.press_button(self.DPAD_TO_VGBUTTON[(c_input.type, c_input.val)])
            else:
                self.gamepad.release_button(self.DPAD_TO_VGBUTTON[(c_input.type, 1)])
                self.gamepad.release_button(self.DPAD_TO_VGBUTTON[(c_input.type, -1)])

        elif c_input.type in self.TRIGGERS:  # Triggers (values are in [0, 255])
            if c_input.type == InputType.TRIGGER_LEFT:
                self.gamepad.left_trigger(c_input.val)
            else:
                self.gamepad.right_trigger(c_input.val)

        self.gamepad.update()

    def execute_stick(self, c_input_x: ControllerInput, c_input_y: ControllerInput) -> None:
        """
        Receives Controller Inputs and produces them on a Virtual Controller.

        Valid for any 2-axis Input Type.
        """
        if c_input_x.type not in self.STICKS or c_input_y.type not in self.STICKS:
            raise ValueError("Use execute method to handle non-stick inputs")

        if c_input_x.type[:-1] != c_input_y.type[:-1]:
            raise ValueError("The inputs must be on the same stick")

        if c_input_x.type == InputType.STICK_LEFT_X:
            self.gamepad.left_joystick(x_value=int(c_input_x.val), y_value=int(c_input_y.val))
        else:
            self.gamepad.right_joystick(x_value=int(c_input_x.val), y_value=int(c_input_y.val))

        self.gamepad.update()

    def reset_controls(self):
        """ Releases all buttons (except sticks) of the Virtual Controller """
        time.sleep(0.5)  # This looks unnecessary, but it's needed for it to work even when the level is reset
        for btn in self.BTN_TO_VGBUTTON.values():
            self.gamepad.release_button(btn)

        for btn in self.DPAD_TO_VGBUTTON.values():
            self.gamepad.release_button(btn)

        self.gamepad.left_trigger(0)
        self.gamepad.right_trigger(0)

        self.gamepad.update()
        print("Gamepad was reset")
        time.sleep(0.1)

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
        InputType.BTN_START: vg.XUSB_BUTTON.XUSB_GAMEPAD_START
    }

    # Map of conversions between the InputType enum and the vg.XUSB_BUTTON used by the package vgamepad
    DPAD_TO_VGBUTTON = {
        (InputType.DIR_PAD_Y, -1): vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
        (InputType.DIR_PAD_Y, 1): vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
        (InputType.DIR_PAD_X, -1): vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
        (InputType.DIR_PAD_X, 1): vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    }

    # Arrays of InputTypes that can be used to check the category of the Input Type
    DPADS = [InputType.DIR_PAD_X, InputType.DIR_PAD_Y]
    TRIGGERS = [InputType.TRIGGER_LEFT, InputType.TRIGGER_RIGHT]
    STICKS = [InputType.STICK_LEFT_X, InputType.STICK_LEFT_Y, InputType.STICK_RIGHT_X, InputType.STICK_RIGHT_Y]
