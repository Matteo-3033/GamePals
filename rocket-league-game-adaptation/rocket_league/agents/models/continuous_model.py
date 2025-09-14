import numpy as np
import numpy.typing as npt
import torch

from .continuous_policy import ContinuousPolicy
from .model import DEFAULT_DEVICE, POLICY_LAYER_SIZES, Model
from .policy import Policy


class ContinuousModel(Model):
    def _get_policy(
        self,
        obs_size: int,
        action_space_size: int,
        policy_layer_sizes: list[int] = POLICY_LAYER_SIZES,
        device: torch.device = DEFAULT_DEVICE,
    ) -> Policy:

        return ContinuousPolicy(
            obs_size,
            action_space_size * 2,
            policy_layer_sizes,
            device,
            var_min=0.1,
            var_max=1.0,
        ).to(device)

    def _parse_action(
        self, action: npt.NDArray[np.float32], weight: npt.NDArray[np.float32]
    ) -> tuple[npt.NDArray[np.float32], float]:
        action, weight = super()._parse_action(action, weight)

        return action.cpu().numpy(), weight
