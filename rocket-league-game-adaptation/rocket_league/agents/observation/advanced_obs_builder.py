import math
from typing import Any, List

import numpy as np
import numpy.typing as npt

from ... import common_values
from ...mod import PhysicsObject, PlayerData, RLGameState
from .obs_builder import ObsBuilder


class AdvancedObsBuilder(ObsBuilder):
    POS_STD = (
        2300  # If you read this and wonder why, ping Rangler in the dead of night.
    )
    ANG_STD = math.pi

    def build_obs(
        self,
        player_state: PlayerData,
        game_state: RLGameState,
        non_managed_inputs: npt.NDArray[np.float32],
        previous_action: npt.NDArray[np.float32],
    ) -> Any:

        if player_state.team_num == common_values.ORANGE_TEAM:
            inverted = True
            ball = game_state.inverted_ball
            pads = game_state.inverted_boost_pads
        else:
            inverted = False
            ball = game_state.ball
            pads = game_state.boost_pads

        obs = [
            ball.position / self.POS_STD,
            ball.linear_velocity / self.POS_STD,
            ball.angular_velocity / self.ANG_STD,
            previous_action,
            pads,
        ]

        player_car = self._add_player_to_obs(obs, player_state, ball, inverted)

        allies = []
        enemies = []

        for other in game_state.players:
            if other.car_id == player_state.car_id:
                continue

            if other.team_num == player_state.team_num:
                team_obs = allies
            else:
                team_obs = enemies

            other_car = self._add_player_to_obs(team_obs, other, ball, inverted)

            # Extra info
            team_obs.extend(
                [
                    (other_car.position - player_car.position) / self.POS_STD,
                    (other_car.linear_velocity - player_car.linear_velocity)
                    / self.POS_STD,
                ]
            )

        obs.extend(allies)
        obs.extend(enemies)
        obs.append(non_managed_inputs)

        return np.concatenate(obs)

    def _add_player_to_obs(
        self, obs: List, player: PlayerData, ball: PhysicsObject, inverted: bool
    ):
        if inverted:
            player_car = player.inverted_car_data
        else:
            player_car = player.car_data

        rel_pos = ball.position - player_car.position
        rel_vel = ball.linear_velocity - player_car.linear_velocity

        obs.extend(
            [
                rel_pos / self.POS_STD,
                rel_vel / self.POS_STD,
                player_car.position / self.POS_STD,
                player_car.forward(),
                player_car.up(),
                player_car.linear_velocity / self.POS_STD,
                player_car.angular_velocity / self.ANG_STD,
                [
                    player.boost_amount,
                    int(player.on_ground),
                    int(player.has_flip),
                    int(player.is_demoed),
                ],
            ]
        )

        return player_car
