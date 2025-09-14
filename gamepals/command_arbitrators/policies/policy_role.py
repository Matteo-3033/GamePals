
from enum import StrEnum


class PolicyRole(StrEnum):
    """
    Enumerator for the Policy Roles. An Actor can register for an input specifying its Role.
    The Role is supposed to be used to allow for more complex Policies to be produced.
    """

    PILOT = "Pilot"
    COPILOT = "Copilot"