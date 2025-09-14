import numpy as np
import numpy.typing as npt
import torch

from .discrete_policy import DiscretePolicy
from .model import DEFAULT_DEVICE, POLICY_LAYER_SIZES, Model
from .policy import Policy


class DiscreteModel(Model):
    def __init__(
        self,
        policy_name: str,
        obs_size: int,
        action_space_size: int,
        lookup_table: npt.NDArray[np.float32],
    ):
        super().__init__(policy_name, obs_size, action_space_size)

        self.__lookup_table = lookup_table

    def _get_policy(
        self,
        obs_size: int,
        action_space_size: int,
        policy_layer_sizes: list[int] = POLICY_LAYER_SIZES,
        device: torch.device = DEFAULT_DEVICE,
    ) -> Policy:

        return DiscretePolicy(
            obs_size,
            action_space_size,
            policy_layer_sizes,
            device,
        ).to(device)

    def _parse_action(
        self, action: npt.NDArray[np.float32], weight: npt.NDArray[np.float32]
    ) -> tuple[npt.NDArray[np.float32], float]:
        action, weight = super()._parse_action(action, weight)

        return self.__lookup_table[action], weight
