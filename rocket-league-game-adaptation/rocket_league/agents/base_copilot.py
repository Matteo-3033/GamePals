from abc import ABC, abstractmethod
from enum import Enum

import numpy as np
import numpy.typing as npt
from gamepals.agents import SWAgentActor
from gamepals.agents.actions import ActionInputWithConfidence, GameAction
from gamepals.agents.observer import ActorData, MessageData
from gamepals.sources.controller import ControllerInput
from gamepals.sources.game import GameState

from ..mod import GameStateType, RLGameState, RLGameStateListener
from .game_action import RLGameAction
from .models import AbstractModel
from .observation import ObsBuilder


class ModelAction(Enum):
    THROTTLE = 0
    STEER = 1
    YAW = 2
    PITCH = 3
    ROLL = 4
    JUMP = 5
    BOOST = 6
    HANDBRAKE = 7


GAME_ACTION_TO_MODEL_ACTIONS: dict[GameAction, list[ModelAction]] = {
    RLGameAction.THROTTLE: [ModelAction.THROTTLE],
    RLGameAction.STEER_YAW: [ModelAction.STEER, ModelAction.YAW],
    RLGameAction.PITCH: [ModelAction.PITCH],
    RLGameAction.ROLL: [ModelAction.ROLL],
    RLGameAction.JUMP: [ModelAction.JUMP],
    RLGameAction.BOOST: [ModelAction.BOOST],
    RLGameAction.HANDBRAKE: [ModelAction.HANDBRAKE],
}

MODEL_ACTION_TO_GAME_ACTION_ON_GROUND: dict[ModelAction, GameAction] = {
    ModelAction.THROTTLE: RLGameAction.THROTTLE,
    ModelAction.STEER: RLGameAction.STEER_YAW,
    ModelAction.JUMP: RLGameAction.JUMP,
    ModelAction.BOOST: RLGameAction.BOOST,
    ModelAction.HANDBRAKE: RLGameAction.HANDBRAKE,
}

MODEL_ACTION_TO_GAME_ACTION_IN_AIR: dict[ModelAction, GameAction] = {
    ModelAction.THROTTLE: RLGameAction.THROTTLE,
    ModelAction.YAW: RLGameAction.STEER_YAW,
    ModelAction.PITCH: RLGameAction.PITCH,
    ModelAction.ROLL: RLGameAction.ROLL,
    ModelAction.JUMP: RLGameAction.JUMP,
    ModelAction.BOOST: RLGameAction.BOOST,
    ModelAction.HANDBRAKE: RLGameAction.HANDBRAKE,
}


class BaseCopilot(SWAgentActor, ABC):
    def __init__(
        self, game_state_listener: RLGameStateListener, model: AbstractModel, **kwargs
    ):
        super().__init__(game_state_listener, **kwargs)
        self.model = model
        self.rl_game_state_listener = game_state_listener

        self.managed_actions = list()
        for game_action in self.get_controlled_actions():
            model_action = GAME_ACTION_TO_MODEL_ACTIONS.get(game_action, None)
            if model_action is not None:
                self.managed_actions.extend(model_action)

        self.managed_actions: list[ModelAction] = list(set(self.managed_actions))
        self.managed_actions.sort(key=lambda x: x.value)
        self.managed_actions_indexes = [a.value for a in self.managed_actions]

        non_managed_actions_set = set(ModelAction) - set(self.managed_actions)
        self.non_managed_actions = list(non_managed_actions_set)
        self.non_managed_actions.sort(key=lambda x: x.value)
        self.non_managed_actions_indexes = [a.value for a in self.non_managed_actions]

        self.default_actions: list[ActionInputWithConfidence] = list()
        for game_action in self.get_controlled_actions():
            self.default_actions.append(
                ActionInputWithConfidence(action=game_action, val=0.0, confidence=1.0)
            )

        self.state_handlers = {
            GameStateType.PAUSE: self._on_pause,
            GameStateType.RESET: self._on_reset,
            GameStateType.IN_GAME: self._on_game_state,
        }

        self.obs_builder: ObsBuilder
        self.previous_action: npt.NDArray[np.float64]
        self.current_action: npt.NDArray[np.float64]

        self._init_state()

    def _init_state(self) -> None:
        """Initialize state components that should be resetted at the beginning of each match."""
        self.obs_builder = self.get_obs_builder()

        self.previous_action = np.zeros(len(ModelAction))
        self.current_action = np.zeros(len(ModelAction))

    @abstractmethod
    def get_obs_builder(self) -> ObsBuilder:
        pass

    @property
    def rl_game_state(self) -> RLGameState:
        return self.rl_game_state_listener.game_state

    def __parse_model_action(self, model_action: ModelAction) -> GameAction | None:
        map = MODEL_ACTION_TO_GAME_ACTION_ON_GROUND

        if (
            self.rl_game_state.local_player_index >= 0
            and not self.rl_game_state.local_player.on_ground
        ):
            map = MODEL_ACTION_TO_GAME_ACTION_IN_AIR

        input = map.get(model_action, None)
        return input

    def on_arbitrated_inputs(self, input_data: ControllerInput) -> None:
        """Receives the final Inputs produced by the Command Arbitrator and sent to the Game"""

        if self.rl_game_state.type != GameStateType.IN_GAME:
            return

        game_action = self.config_handler.game_input_to_action(input_data.type)
        if game_action is None:
            return

        model_action = GAME_ACTION_TO_MODEL_ACTIONS.get(game_action, None)
        if model_action is None:
            return

        indexes = [a.value for a in model_action]

        # Actions are rounded due to how the agents were trained
        self.previous_action[indexes] = self.current_action[indexes]
        self.current_action[indexes] = int(input_data.val)

    def compute_actions(self, game_state: GameState) -> list[ActionInputWithConfidence]:
        """Produces a list of action inputs given a Game State. Inputs are executed one after another, with no delay"""

        handler = self.state_handlers.get(self.rl_game_state.type, None)
        if handler is not None:
            return handler()

        return list()

    def _on_pause(self) -> list[ActionInputWithConfidence]:
        return self.default_actions

    def _on_reset(self) -> list[ActionInputWithConfidence]:
        self._init_state()
        return list()

    def _on_game_state(self) -> list[ActionInputWithConfidence]:
        obs = self.obs_builder.build_obs(
            self.rl_game_state.local_player,
            self.rl_game_state,
            self.current_action[self.non_managed_actions_indexes],
            self.previous_action,
        )

        action, weight = self.model.act(obs)

        for action_index, action_type in enumerate(self.managed_actions):
            if action_type.value < 5:  # Movement actions
                action[action_index] = action[action_index].clip(-1, 1)
            else:  # Binary actions
                action[action_index] = action[action_index] > 0

        return self.__parse_inferred_actions(action, weight)

    def __parse_inferred_actions(
        self,
        action: npt.NDArray[np.float32],
        weight: float,
    ) -> list[ActionInputWithConfidence]:
        parsed_actions: list[ActionInputWithConfidence] = list()

        for action_index, model_action in enumerate(self.managed_actions):
            value = action[action_index]

            parsed_action = self.__parse_model_action(model_action)
            if parsed_action is None:
                continue

            parsed_actions.append(
                ActionInputWithConfidence(
                    action=parsed_action, val=value, confidence=weight
                )
            )

        return parsed_actions

    def on_input_update(self, actor_data: ActorData) -> None:
        """Receives Controller Inputs and the Confidence Level sent by an Actor"""
        pass

    def on_message_update(self, message_data: MessageData) -> None:
        """Receives a message from the Copilot. Messages are usually Metacommands"""
        pass
