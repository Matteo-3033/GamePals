from dataclasses import dataclass
from enum import StrEnum
from typing import Any

# This file contains the dataclasses that represent the game state as it is sent by the game mod through the socket.


@dataclass
class Vector3:
    """
    Note that in Rocket League, the x-axis is backwards from what you might expect.
    The orange goal is in the positive y direction. To the left of the orange goal
    is the positive x direction (yes really). Be careful with trig functions!
    """

    x: float
    y: float
    z: float


@dataclass
class Rotator:
    """
    Values are in radians.
    """

    pitch: float
    yaw: float
    roll: float


@dataclass
class Physics:
    location: Vector3
    rotation: Rotator
    velocity: Vector3
    angular_velocity: Vector3

    @staticmethod
    def from_json(json_dict: dict[str, Any]) -> "Physics":
        return Physics(
            location=Vector3(
                json_dict["location"]["X"],
                json_dict["location"]["Y"],
                json_dict["location"]["Z"],
            ),
            rotation=Rotator(
                json_dict["rotation"]["Pitch"],
                json_dict["rotation"]["Yaw"],
                json_dict["rotation"]["Roll"],
            ),
            velocity=Vector3(
                json_dict["velocity"]["X"],
                json_dict["velocity"]["Y"],
                json_dict["velocity"]["Z"],
            ),
            angular_velocity=Vector3(
                json_dict["angular_velocity"]["X"],
                json_dict["angular_velocity"]["Y"],
                json_dict["angular_velocity"]["Z"],
            ),
        )


@dataclass
class PlayerInfo:
    physics: Physics
    is_demolished: bool
    has_wheel_contact: bool
    is_bot: bool
    jumped: bool
    double_jumped: bool
    team: int
    boost: int

    @staticmethod
    def from_json(json_dict: dict[str, Any]) -> "PlayerInfo":
        return PlayerInfo(
            physics=Physics.from_json(json_dict["physics"]),
            is_demolished=json_dict["is_demolished"],
            has_wheel_contact=json_dict["has_wheel_contact"],
            is_bot=json_dict["is_bot"],
            jumped=json_dict["jumped"],
            double_jumped=json_dict["double_jumped"],
            team=json_dict["team"],
            boost=json_dict["boost"],
        )


@dataclass
class BallInfo:
    physics: Physics

    @staticmethod
    def from_json(json_dict: dict[str, Any]) -> "BallInfo":
        return BallInfo(physics=Physics.from_json(json_dict["physics"]))


@dataclass
class BoostPadState:
    is_active: bool

    @staticmethod
    def from_json(json_dict: dict[str, Any]) -> "BoostPadState":
        return BoostPadState(is_active=json_dict["is_active"])


@dataclass
class TeamInfo:
    team_index: int
    score: int

    @staticmethod
    def from_json(json_dict: dict[str, Any]) -> "TeamInfo":
        return TeamInfo(team_index=json_dict["team_index"], score=json_dict["score"])


@dataclass
class GameInfo:
    seconds_elapsed: float

    @staticmethod
    def from_json(json_dict: dict[str, Any]) -> "GameInfo":
        return GameInfo(seconds_elapsed=json_dict["seconds_elapsed"])


class Focus(StrEnum):
    GAME = "game"
    PAUSE = "pause"
    OTHER = "other"


@dataclass
class GamePacket:
    focus: Focus
    game_cars: list[PlayerInfo]
    num_cars: int
    local_car_index: int
    game_boosts: list[BoostPadState]
    num_boost: int
    game_ball: BallInfo
    teams: list[TeamInfo]
    num_teams: int
    game_info: GameInfo

    @staticmethod
    def from_json(json_dict: dict[str, Any]) -> "GamePacket":
        return GamePacket(
            focus=Focus(json_dict["focus"]),
            local_car_index=json_dict["local_car_index"],
            num_cars=json_dict["num_cars"],
            num_boost=json_dict["num_boost"],
            num_teams=json_dict["num_teams"],
            game_cars=[PlayerInfo.from_json(car) for car in json_dict["game_cars"]],
            game_boosts=[
                BoostPadState.from_json(boost) for boost in json_dict["game_boosts"]
            ],
            game_ball=BallInfo.from_json(json_dict["game_ball"]),
            teams=[TeamInfo.from_json(team) for team in json_dict["teams"]],
            game_info=GameInfo.from_json(json_dict["game_info"]),
        )
