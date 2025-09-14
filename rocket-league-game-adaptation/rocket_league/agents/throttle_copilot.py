from enum import StrEnum
from itertools import product
from typing import override

import numpy as np
from gamepals.agents import Actor, SWAgentPressToToggle
from gamepals.agents.actions import ActionInput, ActionInputWithConfidence, GameAction
from gamepals.agents.observer import ActorData
from gamepals.sources import VirtualControllerProvider
from gamepals.sources.game import GameState

from ..mod import RLGameStateListener
from .base_copilot import BaseCopilot
from .game_action import RLGameAction
from .models import ContinuousModel, DiscreteModel, NextoModel
from .observation import AdvancedObsBuilder, NextoObsBuilder, ObsBuilder


class Control(StrEnum):
    ACCELERATION = "acceleration"
    DEACCELERATION = "deacceleration"
    BOTH = "both"


class ThrottleCopilot(SWAgentPressToToggle, BaseCopilot):
    def __init__(
        self,
        game_state_listener: RLGameStateListener,
        control: str = "both",
        pilot: Actor | None = None,
    ):
        model = DiscreteModel(
            "PPO_POLICY_throttle",
            114,
            3,
            np.asarray(list(product([-1, 0, 1], repeat=1))),
        )
        # model = ContinuousModel("PPO_POLICY_throttle", 114, 1)

        self.control = Control(control)
        super().__init__(
            game_state_listener, pilot=pilot, model=model, start_pressed=True
        )

    @override
    def get_controllable_actions(self) -> list[GameAction]:
        return [RLGameAction.THROTTLE]

    @override
    def get_obs_builder(self) -> ObsBuilder:
        return AdvancedObsBuilder()

    def _filter_input(self, action_input: ActionInput) -> bool:
        if self.control == Control.ACCELERATION and action_input.val < 0:
            return False

        if self.control == Control.DEACCELERATION and action_input.val > 0:
            return False

        return True

    def _should_toggle(self, actor_data: ActorData) -> bool:
        if self.control == Control.ACCELERATION:
            return actor_data.data.val > VirtualControllerProvider.INPUT_THRESHOLD
        if self.control == Control.DEACCELERATION:
            return actor_data.data.val < -VirtualControllerProvider.INPUT_THRESHOLD
        return super()._should_toggle(actor_data)

    def compute_actions(self, game_state: GameState) -> list[ActionInputWithConfidence]:
        return BaseCopilot.compute_actions(self, game_state)


class NextoThrottleCopilot(SWAgentPressToToggle, BaseCopilot):
    def __init__(
        self,
        game_state_listener: RLGameStateListener,
        control: str = "both",
        pilot: Actor | None = None,
    ):
        super().__init__(
            game_state_listener, pilot=pilot, model=NextoModel([0]), start_pressed=True
        )

        self.control = Control(control)

    @override
    def get_controllable_actions(self) -> list[GameAction]:
        return [RLGameAction.THROTTLE]

    @override
    def get_obs_builder(self) -> ObsBuilder:
        return NextoObsBuilder()

    def _filter_input(self, action_input: ActionInput) -> bool:
        if self.control == Control.ACCELERATION and action_input.val < 0:
            return False

        if self.control == Control.DEACCELERATION and action_input.val > 0:
            return False

        return True

    def _should_toggle(self, actor_data: ActorData) -> bool:
        if self.control == Control.ACCELERATION:
            return actor_data.data.val > VirtualControllerProvider.INPUT_THRESHOLD
        if self.control == Control.DEACCELERATION:
            return actor_data.data.val < -VirtualControllerProvider.INPUT_THRESHOLD
        return super()._should_toggle(actor_data)

    def compute_actions(self, game_state: GameState) -> list[ActionInputWithConfidence]:
        return BaseCopilot.compute_actions(self, game_state)
