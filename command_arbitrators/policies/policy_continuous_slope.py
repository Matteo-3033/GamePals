from typing import override

from .input_entry import InputEntry
from .policy import ContinuousPolicy


class PolicyContinuousSlope(ContinuousPolicy):
    """
    PolicyContinuousSum is a Continuous Policy that calculates the resulting value
    using a Slope Function for Linear Blending:

            theta_2
              v
              -------
            /
          /
    ------
        ^
       theta_1

    The Slope has the following properties:
    * The x-axis represents the Copilot Confidence.
    * The y-axis represents the alpha parameter, which is then used to weight the Linear Blending.
    * The corners of the function (theta_1 and theta_2) are determined by the Pilot Confidence.

    """

    def __init__(self):
        super().__init__()

    @classmethod
    def get_name(cls) -> str:
        "Returns the name this class should be referred to in the configuration file."
        return "POLICY_CONT_SLOPE"

    @staticmethod
    @override
    def get_max_actors() -> int:
        """Returns the maximum number of actors allowed in the policy."""
        return 2

    @staticmethod
    def merge_input_entries(entries: list[InputEntry]) -> float:
        from .input_entry import PolicyRole

        if len(entries) == 0: return 0.0
        if len(entries) == 1: return entries[0].input_details.val

        pilot = next((e for e in entries if e.actor_role == PolicyRole.PILOT), None)
        copilot = next((e for e in entries if e.actor_role == PolicyRole.COPILOT), None)

        if pilot is None or copilot is None:
            pilot = entries[0]
            copilot = entries[1]

        theta_1 = PolicyContinuousSlope._get_theta_1(pilot.input_details.confidence, p=4)
        theta_2 = PolicyContinuousSlope._get_theta_2(pilot.input_details.confidence, p=4)

        alpha = PolicyContinuousSlope._calc_alpha(
            copilot.input_details.confidence,
            theta_1,
            theta_2
        )

        # Linear Blending
        return pilot.input_details.val * (1 - alpha) + copilot.input_details.val * alpha


    @staticmethod
    def _get_theta_1(c : float, p : float) -> float:
        # c should be the Pilot Confidence
        return c ** p

    @staticmethod
    def _get_theta_2(c : float, p : float) -> float:
        # c should be the Pilot Confidence
        return c ** (1 / p)

    @staticmethod
    def _calc_alpha(c : float, theta_1 : float, theta_2 : float) -> float:
        # c should be the Copilot Confidence

        if c < theta_1: return 0
        if c > theta_2: return 1

        if theta_1 == theta_2:
            return 1 if c > theta_1 else 0

        return 1 / (theta_2 - theta_1) * (c - theta_1)

