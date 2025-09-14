#pragma once

#include "bakkesmod/plugin/bakkesmodplugin.h"
#include "Broadcaster.h"
#include "GameTickPacket.h"

#pragma comment(lib, "pluginsdk.lib")

class rocket_league_game_state_parser final : public BakkesMod::Plugin::BakkesModPlugin
{
public:
	rocket_league_game_state_parser();

	void onLoad() override;
	void onUnload() override;

private:
	void load_hooks();

	void on_tick(const std::string& event_name);
	void on_boost_pad_picked_up(ActorWrapper caller);
	void on_boost_pad_respawned(ActorWrapper caller);

	void init_game_packet();
	void update_game_state() const;
	void update_player_state(CarWrapper car, PlayerInfo& out) const;
	static void update_ball_state(BallWrapper ball, BallInfo& out);

	broadcaster broadcaster_;
	GameTickPacket* game_packet_ = nullptr;
};
