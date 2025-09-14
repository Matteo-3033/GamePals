#include "pch.h"

#include "GameTickPacket.h"
#include <vector>

GameTickPacket::GameTickPacket(const int num_cars, const int num_teams, const int num_boost)
	: focus(GAME), num_cars(num_cars), local_car_index(0), game_cars(num_cars), num_boost(num_boost),
	  game_boosts(num_boost), num_teams(num_teams), teams(num_teams)
{
	for (int i = 0; i < num_teams; i++)
		teams[i].team_index = 0;
}
