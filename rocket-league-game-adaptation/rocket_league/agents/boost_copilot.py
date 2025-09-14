from itertools import product
from typing import override

import numpy as np
from gamepals.agents import Actor
from gamepals.agents.actions import GameAction

from ..mod import RLGameStateListener
from .base_copilot import BaseCopilot
from .game_action import RLGameAction
from .models import DiscreteModel, NextoModel
from .observation import AdvancedObsBuilder, NextoObsBuilder, ObsBuilder


class BoostCopilot(BaseCopilot):
    def __init__(
        self,
        game_state_listener: RLGameStateListener,
    ):

        model = DiscreteModel(
            "PPO_POLICY_boost", 114, 2, np.asarray(list(product([0, 1], repeat=1)))
        )

        super().__init__(game_state_listener, model)

    @override
    def get_controllable_actions(self) -> list[GameAction]:
        return [RLGameAction.BOOST]

    @override
    def get_obs_builder(self) -> ObsBuilder:
        return AdvancedObsBuilder()


class NextoBoostCopilot(BaseCopilot):
    def __init__(
        self,
        game_state_listener: RLGameStateListener,
    ):
        super().__init__(game_state_listener, NextoModel([6]))

    @override
    def get_controllable_actions(self) -> list[GameAction]:
        return [RLGameAction.BOOST]

    @override
    def get_obs_builder(self) -> ObsBuilder:
        return NextoObsBuilder()
