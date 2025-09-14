
#include "pch.h"
#include "RocketLeagueGameStateParser.h"
#include "Broadcaster.h"
#include "logging.h"
#include "GameTickPacket.h"

BAKKESMOD_PLUGIN(rocket_league_game_state_parser, "Rocket League Game State Parser", "1.0", PERMISSION_ALL)

std::shared_ptr<CVarManagerWrapper> global_cvar_manager;

constexpr int EXHIBITION_PLAYLIST_ID = 8;

const std::vector<Vector> BOOST_PAD_LOCATIONS = {
	{0.0, -4240.0, 70.0},
	{-1792.0, -4184.0, 70.0},
	{1792.0, -4184.0, 70.0},
	{-3072.0, -4096.0, 73.0},
	{3072.0, -4096.0, 73.0},
	{-940.0, -3308.0, 70.0},
	{940.0, -3308.0, 70.0},
	{0.0, -2816.0, 70.0},
	{-3584.0, -2484.0, 70.0},
	{3584.0, -2484.0, 70.0},
	{-1788.0, -2302.0, 70.0},
	{1788.0, -2302.0, 70.0},
	{-2048.0, -1036.0, 70.0},
	{0.0, -1024.0, 70.0},
	{2048.0, -1036.0, 70.0},
	{-3584.0, 0.0, 73.0},
	{-1024.0, 0.0, 70.0},
	{1024.0, 0.0, 70.0},
	{3584.0, 0.0, 73.0},
	{-2048.0, 1036.0, 70.0},
	{0.0, 1024.0, 70.0},
	{2048.0, 1036.0, 70.0},
	{-1788.0, 2302.0, 70.0},
	{1788.0, 2302.0, 70.0},
	{-3584.0, 2484.0, 70.0},
	{3584.0, 2484.0, 70.0},
	{0.0, 2816.0, 70.0},
	{-940.0, 3308.0, 70.0},
	{940.0, 3308.0, 70.0},
	{-3072.0, 4096.0, 73.0},
	{3072.0, 4096.0, 73.0},
	{-1792.0, 4184.0, 70.0},
	{1792.0, 4184.0, 70.0},
	{0.0, 4240.0, 70.0}
};

constexpr double EPSILON = 1e-6;

bool are_equal(const double a, const double b, const double epsilon = EPSILON) {
	return std::fabs(a - b) < epsilon;
}

int get_boost_pad_index(const Vector& boost_pad_location)
{
	const auto it = std::find_if(
		BOOST_PAD_LOCATIONS.cbegin(), 
		BOOST_PAD_LOCATIONS.end(), 
		[&boost_pad_location](const Vector& location) {
			return are_equal(location.X, boost_pad_location.X) &&
				are_equal(location.Y, boost_pad_location.Y);
	});

	if (it == BOOST_PAD_LOCATIONS.cend())
		return -1;

	return std::distance(BOOST_PAD_LOCATIONS.cbegin(), it);
}

rocket_league_game_state_parser::rocket_league_game_state_parser()
	: BakkesModPlugin()
{
}

void rocket_league_game_state_parser::onLoad()
{
	global_cvar_manager = cvarManager;

	LOG("Loading Game State Parser...");

	this->load_hooks();
	broadcaster_.start();

	LOG("Game State Parser loaded.");
}

void rocket_league_game_state_parser::onUnload()
{
	LOG("Unloading Game State Parser...");
	broadcaster_.stop();

	if (game_packet_ != nullptr)
	{
		delete game_packet_;
		game_packet_ = nullptr;
	}

	global_cvar_manager = nullptr;
}

void rocket_league_game_state_parser::load_hooks()
{
	gameWrapper->HookEvent("Function Engine.GameViewportClient.Tick", std::bind(&rocket_league_game_state_parser::on_tick, this, std::placeholders::_1));

	gameWrapper->HookEventWithCaller<ActorWrapper>("Function TAGame.VehiclePickup_TA.OnPickUp", [this](const ActorWrapper& caller, void*, const std::string&) { on_boost_pad_picked_up(caller); });
	gameWrapper->HookEventWithCaller<ActorWrapper>("Function TAGame.VehiclePickup_TA.OnSpawn", [this](const ActorWrapper& caller, void*, const std::string&) { on_boost_pad_respawned(caller); });
}

void rocket_league_game_state_parser::on_boost_pad_picked_up(ActorWrapper caller)
{
	const int boost_pad_index = get_boost_pad_index(caller.GetLocation());

	if (boost_pad_index < 0)
	{
		DEBUGLOG("Boost pad not found! {},{},{}", caller.GetLocation().X, caller.GetLocation().Y, caller.GetLocation().Z);
		return;
	}

	if (game_packet_ == nullptr)
		init_game_packet();

	DEBUGLOG("Boost pad picked up! {}", boost_pad_index);
	game_packet_->game_boosts[boost_pad_index].is_active = false;
}

void rocket_league_game_state_parser::on_boost_pad_respawned(ActorWrapper caller)
{
	const int boost_pad_index = get_boost_pad_index(caller.GetLocation());

	if (boost_pad_index < 0)
	{
		DEBUGLOG("Boost pad not found! {},{},{}", caller.GetLocation().X, caller.GetLocation().Y, caller.GetLocation().Z);
		return;
	}

	if (game_packet_ == nullptr)
		init_game_packet();

	game_packet_->game_boosts[boost_pad_index].is_active = true;
}

void rocket_league_game_state_parser::on_tick(const std::string& event_name)
{
	if (game_packet_ == nullptr)
		init_game_packet();

	if (!gameWrapper->IsInGame() && !gameWrapper->IsInCustomTraining() && !gameWrapper->IsInOnlineGame() && !gameWrapper->IsInFreeplay())
	{
		game_packet_->focus = OTHER;
	}
	else if (gameWrapper->IsPaused() || gameWrapper->IsInReplay())
	{
		game_packet_->focus = PAUSE;
	}
	else
	{
		game_packet_->focus = GAME;
		update_game_state();
	}

	if (game_packet_ != nullptr)
		broadcaster_.broadcast(*game_packet_);
}

void rocket_league_game_state_parser::update_game_state() const
{
	auto new_state = gameWrapper->GetCurrentGameState();
	if (new_state.IsNull())
		return;

	if (new_state.GetPlaylist().GetPlaylistId() != EXHIBITION_PLAYLIST_ID || new_state.GetbMatchEnded() == 1)
	{
		game_packet_->focus = OTHER;
		return;
	}

	game_packet_->game_info.seconds_elapsed = new_state.GetSecondsElapsed();
	update_ball_state(new_state.GetBall(), game_packet_->game_ball);

	auto teams = new_state.GetTeams();

	for (int i = 0; i < game_packet_->num_teams; i++)
		game_packet_->teams[i].score = teams.Get(i).GetScore();
	
	auto cars = new_state.GetCars();

	for (int i = 0; i < cars.Count(); i++)
	{
		update_player_state(
			cars.Get(i),
			game_packet_->game_cars[i]
		);

		if (!game_packet_->game_cars[i].is_bot)
			game_packet_->local_car_index = i;
	}
}

void rocket_league_game_state_parser::update_ball_state(BallWrapper ball, BallInfo& out)
{
	if (ball.IsNull())
		return;

	out.physics.location = ball.GetLocation();
	out.physics.velocity = ball.GetVelocity();
	out.physics.angular_velocity = ball.GetAngularVelocity();
	out.physics.rotation = Rotation::from_rotator(ball.GetRotation());
}

void rocket_league_game_state_parser::update_player_state(CarWrapper car, PlayerInfo& out) const
{
	out.team = car.GetLoadoutTeamIndex();
	out.is_bot = gameWrapper->GetLocalCar().memory_address != car.memory_address;
	out.is_demolished = car.IsNull();

	if (out.is_demolished)
	{
		out.boost = 0;
		out.jumped = false;
		out.double_jumped = false;
		out.has_wheel_contact = false;

		out.physics.location = Vector();
		out.physics.velocity = Vector();
		out.physics.angular_velocity = Vector();
		out.physics.rotation = Rotation();
	}
	else
	{
		auto boost_component = car.GetBoostComponent();
		out.boost = boost_component.IsNull() ? 0 : static_cast<int>(boost_component.GetCurrentBoostAmount() * 100);
		out.jumped = car.GetbJumped() != 0;
		out.double_jumped = car.GetbDoubleJumped() != 0;
		out.has_wheel_contact = car.AnyWheelTouchingGround();

		out.physics.location = car.GetLocation();
		out.physics.velocity = car.GetVelocity();
		out.physics.angular_velocity = car.GetAngularVelocity();
		out.physics.rotation = Rotation::from_rotator(car.GetRotation());
	}
}

void rocket_league_game_state_parser::init_game_packet()
{
	LOG("Initializing game state...");

	game_packet_ = new GameTickPacket(
		2, // state.GetPlayers().Count(),
		2, // state.GetTeams().Count(),
		BOOST_PAD_LOCATIONS.size()
	);
}
