"""
File: continuous_policy.py
Author: Matthew Allen

Description:
    An implementation of a policy for the continuous action space. For N actions the policy will output N*2 values in
    the range [-1, 1]. A linear transform is applied to the latter half of the policy's output to map it onto the range
    [var_min, var_max]. A mutli-variate Gaussian distribution with a diagonal covariance matrix is then constructed
    using the former half of the policy's output as the mean and the transformed latter half as the diagonal of the
    covariance matrix.

"""

import functools
from typing import Any

import numpy as np
import torch
import torch.nn as nn
from torch.distributions import Normal

from .policy import Policy


class MapContinuousToAction(nn.Module):
    """
    A class for policies using the continuous action space. Continuous policies output N*2 values for N actions where
    each value is in the range [-1, 1]. Half of these values will be used as the mean of a multi-variate normal distribution
    and the other half will be used as the diagonal of the covariance matrix for that distribution. Since variance must
    be positive, this class will map the range [-1, 1] for those values to the desired range (defaults to [0.1, 1]) using
    a simple linear transform.
    """

    def __init__(self, range_min=0.1, range_max=1):
        super().__init__()

        tanh_range = [-1, 1]
        self.m = (range_max - range_min) / (tanh_range[1] - tanh_range[0])
        self.b = range_min - tanh_range[0] * self.m

    def forward(self, x):
        n = x.shape[-1] // 2
        # map the right half of x from [-1, 1] to [range_min, range_max].
        return x[..., :n], x[..., n:] * self.m + self.b


class ContinuousPolicy(Policy):
    def __init__(
        self, input_shape, output_shape, layer_sizes, device, var_min=0.1, var_max=1.0
    ):
        super().__init__()
        self.device = device
        self.affine_map = MapContinuousToAction(range_min=var_min, range_max=var_max)

        # Build the neural network.
        assert (
            len(layer_sizes) != 0
        ), "AT LEAST ONE LAYER MUST BE SPECIFIED TO BUILD THE NEURAL NETWORK!"
        layers = [nn.Linear(input_shape, layer_sizes[0]), nn.ReLU()]

        prev_size = layer_sizes[0]
        for size in layer_sizes[1:]:
            layers.append(nn.Linear(prev_size, size))
            layers.append(nn.ReLU())
            prev_size = size

        layers.append(nn.Linear(layer_sizes[-1], output_shape))
        layers.append(nn.Tanh())
        self.model = nn.Sequential(*layers).to(self.device)

    @functools.lru_cache()
    def logpdf(self, x, mean, std):
        """
        Function to compute the log of the pdf of our distribution parameterized by (mean, std) evaluated at x. PyTorch
        can do this natively but I don't trust their method.
        :param x: value to compute the logpdf for.
        :param mean: Mean of the distribution to evaluate.
        :param std: Diagonal of the covariance matrix of the distribution to evaluate.
        :return: ln(pdf(x)).
        """

        msq = mean * mean
        ssq = std * std
        xsq = x * x

        term1 = -torch.divide(msq, (2 * ssq))
        term2 = torch.divide(mean * x, ssq)
        term3 = -torch.divide(xsq, (2 * ssq))
        term4 = torch.log(1 / torch.sqrt(2 * np.pi * ssq))

        return term1 + term2 + term3 + term4

    def get_output(self, obs):
        if type(obs) != torch.Tensor:
            if type(obs) != np.array:
                obs = np.asarray(obs)
            obs = torch.as_tensor(obs, dtype=torch.float32, device=self.device)

        policy_output = self.model(obs)
        return self.affine_map(policy_output)

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
        mean, std = self.get_output(obs)
        if deterministic:
            log_prob = self.logpdf(mean, mean, std)

            if summed_probs:
                log_prob = log_prob.sum(dim=-1) if log_prob.ndim > 1 else log_prob.sum()

            return mean.cpu(), log_prob.cpu()

        distribution = Normal(loc=mean, scale=std)
        action = distribution.sample().clamp(min=-1, max=1)
        log_prob = self.logpdf(action, mean, std)

        shape = log_prob.shape
        if summed_probs:
            if len(shape) > 1:
                log_prob = log_prob.sum(dim=-1)
            else:
                log_prob = log_prob.sum()

        return action.cpu(), log_prob.cpu()

    def get_backprop_data(self, obs, acts, summed_probs=True):
        """
        Function to compute the data necessary for backpropagation.
        :param obs: Observations to pass through the policy.
        :param acts: Actions taken by the policy.
        :param summed_probs: Whether the log probs should be summed along the final dimension. Default True.
        :return: Action log probs & entropy.
        """

        mean, std = self.get_output(obs)
        distribution = Normal(loc=mean, scale=std)

        prob = self.logpdf(acts, mean, std)
        if summed_probs:
            log_probs = prob.sum(dim=1).to(self.device)
        else:
            log_probs = prob.to(self.device)

        entropy = distribution.entropy()
        entropy = entropy.mean().to(self.device)

        return log_probs, entropy
