from gamepals.agents.actions import GameAction


class RLGameAction(GameAction):
    """The Enum class for Rocket League Game Actions"""

    STEER_YAW = "steer_yaw"
    PITCH = "pitch"
    BOOST = "boost"
    HANDBRAKE = "handbrake"
    THROTTLE = "throttle"
    JUMP = "jump"
    ROLL = "roll"
    FOCUS_BALL = "focus_ball"
    PAUSE = "pause"
