from typing import override

import numpy as np
from gamepals.agents.actions import GameAction

from ..mod import RLGameStateListener
from .base_copilot import BaseCopilot
from .game_action import RLGameAction
from .models import ContinuousModel, DiscreteModel, NextoModel
from .observation import AdvancedObsBuilder, NextoObsBuilder, ObsBuilder


def remove_duplicates(lst: list[list[float]]) -> list[list[float]]:
    out: list[list[float]] = list()
    seen = set()

    for item in lst:
        item_tuple = tuple(item)
        if item_tuple in seen:
            continue

        seen.add(item_tuple)
        out.append(item)

    return out


class MovementCopilot(BaseCopilot):
    def __init__(
        self,
        game_state_listener: RLGameStateListener,
    ):
        lookup_table: list[list[float]] = list()

        # Ground
        for steer in (-1, 0, 1):
            lookup_table.append([steer, 0, steer])
        # Aerial
        for pitch in (-1, 0, 1):
            for yaw in (-1, 0, 1):
                lookup_table.append([yaw, pitch, yaw])

        lookup_table_np = np.asarray(remove_duplicates(lookup_table))

        model = DiscreteModel(
            "PPO_POLICY_movement", 112, len(lookup_table_np), lookup_table_np
        )
        # model = ContinuousModel("PPO_POLICY_movement", 112, 3)

        super().__init__(game_state_listener, model)

    @override
    def get_controllable_actions(self) -> list[GameAction]:
        return [RLGameAction.STEER_YAW, RLGameAction.PITCH]

    @override
    def get_obs_builder(self) -> ObsBuilder:
        return AdvancedObsBuilder()


class NextoMovementCopilot(BaseCopilot):
    def __init__(
        self,
        game_state_listener: RLGameStateListener,
    ):
        super().__init__(game_state_listener, NextoModel([1, 2, 3]))

    @override
    def get_controllable_actions(self) -> list[GameAction]:
        return [RLGameAction.STEER_YAW, RLGameAction.PITCH]

    @override
    def get_obs_builder(self) -> ObsBuilder:
        return NextoObsBuilder()
