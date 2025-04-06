from enum import StrEnum


class GameAction(StrEnum):
    """
    GameAction is the Enum Superclass of any Game Action that can be supported by the SW Agents.

    Implementing the architecture for a specific game requires all Game Actions to be specified in a subclass of this class.
    """
    pass