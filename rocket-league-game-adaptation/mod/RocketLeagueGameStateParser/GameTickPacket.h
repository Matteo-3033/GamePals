#pragma once

#define _USE_MATH_DEFINES

#include <nlohmann/json.hpp>
#include <vector>
#include <math.h>

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(
	Vector,
	X,
	Y,
	Z
);

struct Rotation
{
	double Pitch = 0.0F;
	double Yaw = 0.0F;
	double Roll = 0.0F;

	static Rotation from_rotator(const Rotator& rotator)
	{
		constexpr double scaling_factor = M_PI / max_angle;

		return {
			normalize_angle(rotator.Pitch * scaling_factor),
			normalize_angle(rotator.Yaw * scaling_factor),
			normalize_angle(rotator.Roll * scaling_factor)
		};
	}

private:
	static constexpr int max_angle = 32768;

	static double normalize_angle(double radians)
	{
		radians = fmod(radians, 2 * M_PI);

		if (radians < -M_PI)
			radians += 2 * M_PI;
		else if (radians > M_PI)
			radians -= 2 * M_PI;

		return radians;
	}
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(
	Rotation,
	Pitch,
	Yaw,
	Roll
);

struct Physics
{
	Vector location;
	Rotation rotation;
	Vector velocity;
	Vector angular_velocity;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(
	Physics,
	location,
	rotation,
	velocity,
	angular_velocity
);

struct PlayerInfo
{
	Physics physics;
	int team = 0;
	bool is_demolished = false;
	bool has_wheel_contact = true;
	bool jumped = false;
	bool double_jumped = false;
	int boost = 0;
	bool is_bot = true;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(
	PlayerInfo,
	physics,
	team,
	is_demolished,
	has_wheel_contact,
	jumped,
	double_jumped,
	boost,
	is_bot
);

struct BallInfo
{
	Physics physics;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(
	BallInfo,
	physics
);

struct BoostPadState
{
	bool is_active = false;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(
	BoostPadState,
	is_active
);

struct TeamInfo
{
	int team_index = 0;
	int score = 0;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(
	TeamInfo,
	team_index,
	score
);

struct GameInfo
{
	float seconds_elapsed = 0.0F;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(
	GameInfo,
	seconds_elapsed
);

enum FocusedWindow : uint8_t
{
	GAME,
	PAUSE,
	OTHER,
};

NLOHMANN_JSON_SERIALIZE_ENUM(FocusedWindow, {
	{GAME, "game"},
	{PAUSE, "pause"},
	{OTHER, "other"},
});

struct GameTickPacket
{
	GameTickPacket(int num_cars, int num_teams, int num_boost);

	FocusedWindow focus;

	int num_cars;
	int local_car_index;
	std::vector<PlayerInfo> game_cars;

	BallInfo game_ball;

	int num_boost;
	std::vector<BoostPadState> game_boosts;

	int num_teams;
	std::vector<TeamInfo> teams;

	GameInfo game_info;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(
	GameTickPacket,
	focus,
	num_cars,
	local_car_index,
	game_cars,
	game_ball,
	num_boost,
	game_boosts,
	num_teams,
	teams,
	game_info
);
