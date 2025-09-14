import math
from enum import Enum
from typing import List

import numpy as np
import numpy.typing as npt
from gamepals.sources.game import GameState

from .. import common_values
from .game_packet import (Focus, GamePacket, Physics, PlayerInfo, Rotator,
                          Vector3)


class PhysicsObject:
    def __init__(
        self,
        position: npt.NDArray[np.float32] | None = None,
        euler_angles: npt.NDArray[np.float32] | None = None,
        linear_velocity: npt.NDArray[np.float32] | None = None,
        angular_velocity: npt.NDArray[np.float32] | None = None,
    ) -> None:
        self.position = position if position else np.zeros(3, dtype=np.float32)

        # ones by default to prevent mathematical errors when converting quat to rot matrix on empty physics state
        self.quaternion = np.ones(4, dtype=np.float32)

        self.linear_velocity = (
            linear_velocity if linear_velocity else np.zeros(3, dtype=np.float32)
        )
        self.angular_velocity = (
            angular_velocity if angular_velocity else np.zeros(3, dtype=np.float32)
        )
        self._euler_angles = (
            euler_angles if euler_angles else np.zeros(3, dtype=np.float32)
        )
        self._rotation_mtx = np.zeros((3, 3), dtype=np.float32)
        self._has_computed_rot_mtx = False

        self._invert_vec = np.asarray([-1, -1, 1])
        self._invert_pyr = np.asarray([0, math.pi, 0], dtype=np.float32)

    def decode_car_data(self, car_data: Physics) -> None:
        self.position = self._vector_to_numpy(car_data.location)
        self._euler_angles = self._rotator_to_numpy(car_data.rotation)
        self.linear_velocity = self._vector_to_numpy(car_data.velocity)
        self.angular_velocity = self._vector_to_numpy(car_data.angular_velocity)

    def decode_ball_data(self, ball_data: Physics) -> None:
        self.position = self._vector_to_numpy(ball_data.location)
        self.linear_velocity = self._vector_to_numpy(ball_data.velocity)
        self.angular_velocity = self._vector_to_numpy(ball_data.angular_velocity)

    def invert(self, other: "PhysicsObject") -> None:
        self.position = other.position * self._invert_vec
        self._euler_angles = other.euler_angles() + self._invert_pyr
        self.linear_velocity = other.linear_velocity * self._invert_vec
        self.angular_velocity = other.angular_velocity * self._invert_vec

    # pitch, yaw, roll
    def euler_angles(self) -> npt.NDArray[np.float32]:
        return self._euler_angles

    def pitch(self) -> np.float32:
        return self._euler_angles[0]

    def yaw(self) -> np.float32:
        return self._euler_angles[1]

    def roll(self) -> np.float32:
        return self._euler_angles[2]

    def rotation_mtx(self) -> npt.NDArray[np.float32]:
        if not self._has_computed_rot_mtx:
            self._rotation_mtx = self._euler_to_rotation(self._euler_angles)
            self._has_computed_rot_mtx = True

        return self._rotation_mtx

    def forward(self) -> npt.NDArray[np.float32]:
        return self.rotation_mtx()[:, 0]

    def right(self) -> npt.NDArray[np.float32]:
        return self.rotation_mtx()[:, 1] * -1

    def left(self) -> npt.NDArray[np.float32]:
        return self.rotation_mtx()[:, 1]

    def up(self) -> npt.NDArray[np.float32]:
        return self.rotation_mtx()[:, 2]

    def _vector_to_numpy(self, vector: Vector3) -> npt.NDArray[np.float32]:
        return np.asarray([vector.x, vector.y, vector.z])

    def _rotator_to_numpy(self, rotator: Rotator) -> npt.NDArray[np.float32]:
        return np.asarray([rotator.pitch, rotator.yaw, rotator.roll])

    def _euler_to_rotation(
        self, pyr: npt.NDArray[np.float32]
    ) -> npt.NDArray[np.float32]:
        CP = math.cos(pyr[0])
        SP = math.sin(pyr[0])
        CY = math.cos(pyr[1])
        SY = math.sin(pyr[1])
        CR = math.cos(pyr[2])
        SR = math.sin(pyr[2])

        theta = np.empty((3, 3))

        # front direction
        theta[0, 0] = CP * CY
        theta[1, 0] = CP * SY
        theta[2, 0] = SP

        # left direction
        theta[0, 1] = CY * SP * SR - CR * SY
        theta[1, 1] = SY * SP * SR + CR * CY
        theta[2, 1] = -CP * SR

        # up direction
        theta[0, 2] = -CR * CY * SP - SR * SY
        theta[1, 2] = -CR * SY * SP + SR * CY
        theta[2, 2] = CP * CR

        return theta


class PlayerData(object):
    def __init__(self) -> None:
        self.car_id: int = -1
        self.team_num: int = -1
        self.is_demoed: bool = False
        self.on_ground: bool = False
        self.ball_touched: bool = False
        self.has_jump: bool = False
        self.has_flip: bool = False
        self.boost_amount: float = -1
        self.car_data: PhysicsObject = PhysicsObject()
        self.inverted_car_data: PhysicsObject = PhysicsObject()


class GameStateType(Enum):
    WAIT_TO_START = 0
    IN_GAME = 1
    PAUSE = 2
    RESET = 3

    @staticmethod
    def from_focus(focus: Focus) -> "GameStateType":
        return focus_to_state[focus]


focus_to_state = {
    Focus.GAME: GameStateType.IN_GAME,
    Focus.PAUSE: GameStateType.PAUSE,
    Focus.OTHER: GameStateType.WAIT_TO_START,
}


class RLGameState(GameState):
    def __init__(self) -> None:
        self.type = GameStateType.WAIT_TO_START
        self.blue_score = 0
        self.orange_score = 0
        self.players: List[PlayerData] = list()
        self._on_ground_ticks = np.zeros(64)

        self.ball: PhysicsObject = PhysicsObject()
        self.inverted_ball: PhysicsObject = PhysicsObject()

        # List of "booleans" (1 or 0)
        self.boost_pads = np.zeros(len(common_values.BOOST_LOCATIONS), dtype=np.float32)
        self.inverted_boost_pads: npt.NDArray[np.float32] = np.zeros_like(
            self.boost_pads, dtype=np.float32
        )

        self.local_player_index = -1
        self.focus = Focus.OTHER

    @property
    def local_player(self) -> PlayerData:
        return (
            0 <= self.local_player_index < len(self.players)
            and self.players[self.local_player_index]
        ) or PlayerData()

    def decode(self, packet: GamePacket, ticks_elapsed: int = 1) -> None:
        if self.focus != Focus.OTHER and packet.focus == Focus.OTHER:
            self.type = GameStateType.RESET
        else:
            self.type = GameStateType.from_focus(packet.focus)

        self.focus = packet.focus

        self.blue_score = packet.teams[0].score
        self.orange_score = packet.teams[1].score

        self.local_player_index = packet.local_car_index

        for i in range(packet.num_boost):
            self.boost_pads[i] = packet.game_boosts[i].is_active
        self.inverted_boost_pads[:] = self.boost_pads[::-1]

        self.ball.decode_ball_data(packet.game_ball.physics)
        self.inverted_ball.invert(self.ball)

        self.players = []
        for i in range(packet.num_cars):
            player = self._decode_player(packet.game_cars[i], i, ticks_elapsed)
            self.players.append(player)

            if player.ball_touched:
                self.last_touch = player.car_id

    def _decode_player(
        self, player_info: PlayerInfo, index: int, ticks_elapsed: int
    ) -> PlayerData:
        player_data = PlayerData()

        player_data.car_data.decode_car_data(player_info.physics)
        player_data.inverted_car_data.invert(player_data.car_data)

        if player_info.has_wheel_contact:
            self._on_ground_ticks[index] = 0
        else:
            self._on_ground_ticks[index] += ticks_elapsed

        player_data.car_id = index
        player_data.team_num = player_info.team
        player_data.is_demoed = player_info.is_demolished
        player_data.on_ground = (
            player_info.has_wheel_contact or self._on_ground_ticks[index] <= 6
        )
        player_data.ball_touched = False
        player_data.has_jump = not player_info.jumped
        player_data.has_flip = not player_info.double_jumped
        player_data.boost_amount = player_info.boost / 100

        return player_data
