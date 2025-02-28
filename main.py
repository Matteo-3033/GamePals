import time
from csv import excel

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

shooter_copilot = ShooterCopilot(game_state_listener)
runner_copilot = RunnerCopilot(game_state_listener)
aimer_copilot = AimerCopilot(game_state_listener)
reset_copilot = ResetCopilot(game_state_listener)
run_toggler = RunToggler(game_state_listener, pilot = pilot) # Some Copilots want to listen directly to player inputs
interact_copilot = InteractCopilot(game_state_listener, pilot = pilot)

# Arbitrator
arbitrator = CommandArbitrator(config_file_path="config.toml")
arbitrator.add_actor(pilot, PolicyRole.PILOT)
arbitrator.add_actor(shooter_copilot, PolicyRole.COPILOT)
arbitrator.add_actor(runner_copilot, PolicyRole.COPILOT)
arbitrator.add_actor(aimer_copilot, PolicyRole.COPILOT)
arbitrator.add_actor(reset_copilot, PolicyRole.PILOT)
arbitrator.add_actor(run_toggler, PolicyRole.PILOT)
arbitrator.add_actor(interact_copilot, PolicyRole.PILOT)

arbitrator.start()

try:
    while True:
        time.sleep(1)  # Keep the main thread alive
except KeyboardInterrupt:
    pass
finally:
    game_state_listener.stop_listening()
    controller_listener.stop_listening()
