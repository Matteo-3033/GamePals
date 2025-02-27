import time

from agents.human_actor import HumanActor
from command_arbitrators.command_arbitrator import CommandArbitrator
from command_arbitrators.policy_manager import PolicyRole
from doom.agents.aimer_copilot import AimerCopilot
from doom.agents.interact_copilot import InteractCopilot
from doom.agents.reset_copilot import ResetCopilot
from doom.agents.run_toggler import RunToggler
from doom.agents.runner_copilot import RunnerCopilot
from doom.agents.shooter_copilot import ShooterCopilot
from doom.doom_state_listener import DoomStateListener
from sources.physical_controller_listener import PhysicalControllerListener

# Listeners
controller_listener = PhysicalControllerListener(gamepad_number=0)
game_state_listener = DoomStateListener(log_file_path="../Doom/log.txt")

# Agents
pilot = HumanActor(controller_listener, config_file_path="config.toml")

copilot_1 = ShooterCopilot(game_state_listener)
copilot_2 = RunnerCopilot(game_state_listener)
copilot_3 = AimerCopilot(game_state_listener)
copilot_4 = ResetCopilot(game_state_listener)
copilot_5 = RunToggler(game_state_listener, pilot = pilot)
copilot_6 = InteractCopilot(game_state_listener)

# Arbitrator
arbitrator = CommandArbitrator(config_file_path="config.toml")
arbitrator.add_actor(pilot, PolicyRole.PILOT)
# arbitrator.add_actor(copilot_1, PolicyRole.COPILOT)
# arbitrator.add_actor(copilot_2, PolicyRole.COPILOT)
# arbitrator.add_actor(copilot_3, PolicyRole.COPILOT)
# arbitrator.add_actor(copilot_4, PolicyRole.PILOT)
# arbitrator.add_actor(copilot_5, PolicyRole.PILOT)
arbitrator.add_actor(copilot_6, PolicyRole.PILOT)

arbitrator.start()

while True:
    time.sleep(1)  # Keep the main thread alive
