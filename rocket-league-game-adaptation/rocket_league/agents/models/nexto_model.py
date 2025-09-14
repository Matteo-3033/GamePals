import os
from typing import Any

import numpy as np
import numpy.typing as npt
import torch
import torch.nn.functional as F

from .model import AbstractModel


class NextoModel(AbstractModel):
    def __init__(self, managed_actions: list[int] | None = None) -> None:
        cur_dir = os.path.dirname(os.path.realpath(__file__))

        with open(os.path.join(cur_dir, "policies/nexto-model.pt"), "rb") as f:
            self.actor = torch.jit.load(f)

        torch.set_num_threads(1)
        self._lookup_table = self.make_lookup_table()
        self.state = None

        if managed_actions is not None:
            self.managed_actions = managed_actions
        else:
            self.managed_actions = list(range(8))

    @staticmethod
    def make_lookup_table():
        actions = []
        # Ground
        for throttle in (-1, 0, 1):
            for steer in (-1, 0, 1):
                for boost in (0, 1):
                    for handbrake in (0, 1):
                        if boost == 1 and throttle != 1:
                            continue
                        actions.append(
                            [throttle or boost, steer, 0, steer, 0, 0, boost, handbrake]
                        )
        # Aerial
        for pitch in (-1, 0, 1):
            for yaw in (-1, 0, 1):
                for roll in (-1, 0, 1):
                    for jump in (0, 1):
                        for boost in (0, 1):
                            if jump == 1 and yaw != 0:  # Only need roll for sideflip
                                continue
                            if pitch == roll == jump == 0:  # Duplicate with ground
                                continue
                            # Enable handbrake for potential wavedashes
                            handbrake = jump == 1 and (
                                pitch != 0 or yaw != 0 or roll != 0
                            )
                            actions.append(
                                [boost, yaw, pitch, yaw, roll, jump, boost, handbrake]
                            )
        return np.array(actions)

    def act(self, state: Any) -> tuple[npt.NDArray[np.float32], float]:
        self.state = state
        state = tuple(torch.from_numpy(s).float() for s in state)

        with torch.no_grad():
            out, weights = self.actor(state)

        out = (out,)
        weights = (weights,)

        max_shape = max(o.shape[-1] for o in out)
        logits = torch.stack(
            [
                (
                    l
                    if l.shape[-1] == max_shape
                    else F.pad(l, pad=(0, max_shape - l.shape[-1]), value=float("-inf"))
                )
                for l in out
            ],
            dim=1,
        )

        actions = np.argmax(logits, axis=-1)
        parsed = self._lookup_table[actions.numpy().item()]

        return parsed[self.managed_actions], 1.0
