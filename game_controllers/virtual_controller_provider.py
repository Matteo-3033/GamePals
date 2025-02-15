from game_controllers.utils import ControllerInput, InputType
import vgamepad as vg

class VirtualControllerProvider():
    """
    The VirtualControllerProvider class provides an XBOX 360 Virtual Controller, whose inputs can be requested via the execute and execute_stick methods
    """

    def __init__(self):
        self.gamepad : vg.VX360Gamepad = vg.VX360Gamepad()
    
    def execute(self, input : ControllerInput) -> None:
        """
        Receives Controller Inputs and produces them on a Virtual Controller
        """
        if input.type in self.STICKS: 
            raise ValueError("Use execute_stick method to handle stick inputs")
        
        if input.type in self.BTN_TO_VGBUTTON: # Press-Release Buttons
            if input.val == 1:
                self.gamepad.press_button(self.BTN_TO_VGBUTTON[input.type])
            else:
                self.gamepad.release_button(self.BTN_TO_VGBUTTON[input.type])
                
        elif input.type in self.DPADS: # Direction Pad (values are -1, 0 or 1)
            if input.val != 0:
                self.gamepad.press_button(self.DPAD_TO_VGBUTTON[(input.type, input.val)])
            else:
                self.gamepad.release_button(self.DPAD_TO_VGBUTTON[(input.type, 1)])
                self.gamepad.release_button(self.DPAD_TO_VGBUTTON[(input.type, -1)])
                
        elif input.type in self.TRIGGERS: # Triggers (values are in [0, 255])
            if input.type == InputType.TRIGGER_LEFT:
                self.gamepad.left_trigger(input.val)
            else:
                self.gamepad.right_trigger(input.val)
        
        self.gamepad.update()
                

    def execute_stick(self, input_x : ControllerInput, input_y : ControllerInput) -> None:
        """
        Receives Controller Inputs and produces them on a Virtual Controller
        """
        if input_x.type not in self.STICKS or input_y.type not in self.STICKS: 
            raise ValueError("Use execute method to handle non-stick inputs")
        
        if input_x.type[:-1] != input_y.type[:-1]:
            raise ValueError("The inputs must be on the same stick")
        
        if input_x.type == InputType.STICK_LEFT_X:
            self.gamepad.left_joystick(x_value = int(input_x.val), y_value = int(input_y.val))
        else:
            self.gamepad.right_joystick(x_value = int(input_x.val), y_value = int(input_y.val))
            
        self.gamepad.update()

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

    DPAD_TO_VGBUTTON = {
        (InputType.DIR_PAD_Y, -1): vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
        (InputType.DIR_PAD_Y, 1): vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
        (InputType.DIR_PAD_X, -1): vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
        (InputType.DIR_PAD_X, 1): vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    }

    DPADS = [InputType.DIR_PAD_X, InputType.DIR_PAD_Y]
    TRIGGERS = [InputType.TRIGGER_LEFT, InputType.TRIGGER_RIGHT]
    STICKS = [InputType.STICK_LEFT_X, InputType.STICK_LEFT_Y, InputType.STICK_RIGHT_X, InputType.STICK_RIGHT_Y]
