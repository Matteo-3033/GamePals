import os
from abc import ABC, abstractmethod
from typing import Any

import numpy as np
import numpy.typing as npt
import torch

from .policy import Policy

POLICY_LAYER_SIZES = [2048, 2048, 1024, 1024]
DEFAULT_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class AbstractModel(ABC):
    @abstractmethod
    def act(self, state: Any) -> tuple[npt.NDArray[np.float32], float]:
        pass


class Model(AbstractModel):
    def __init__(
        self,
        policy_name: str,
        obs_size: int,
        action_space_size: int,
    ):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        device = DEFAULT_DEVICE

        self.policy_name = policy_name

        with open(os.path.join(cur_dir, f"policies/{policy_name}.pt"), "rb") as f:
            policy = torch.load(f, map_location=device)

        self.policy = self._get_policy(
            obs_size, action_space_size, POLICY_LAYER_SIZES, device
        )
        self.policy.load_state_dict(policy)

        torch.set_num_threads(1)

    @abstractmethod
    def _get_policy(
        self,
        obs_size: int,
        action_space_size: int,
        policy_layer_sizes: list[int] = POLICY_LAYER_SIZES,
        device: torch.device = DEFAULT_DEVICE,
    ) -> Policy:
        pass

    def act(self, state: Any) -> tuple[npt.NDArray[np.float32], float]:
        with torch.no_grad():
            action, weight = self.policy.get_action(state, deterministic=True)

        return self._parse_action(action, weight)

    def _parse_action(
        self, action: npt.NDArray[np.float32], weight: npt.NDArray[np.float32]
    ) -> tuple[npt.NDArray[np.float32], float]:
        if len(action.shape) > 1:
            if action.shape[0] == 1:
                action = action[0]

        return action, weight
