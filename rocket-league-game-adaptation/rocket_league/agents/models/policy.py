from abc import ABC, abstractmethod
from typing import Any

import torch.nn as nn


class Policy(ABC, nn.Module):
    @abstractmethod
    def get_action(
        self, obs: Any, summed_probs: bool = True, deterministic: bool = False
    ):
        """
        Function to get an action and the log of its probability from the policy given an observation.
        :param obs: Observation to get an action for.
        :param summed_probs: Whether the resulting log probabilities should be summed along the final axis. Defaults to true.
        :param deterministic: Whether an action should be sampled or the mean should be returned instead.
        :return: An action and its probability.
        """
        pass
