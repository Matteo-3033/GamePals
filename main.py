import time

from agents.human_actor import HumanActor
from command_arbitrators.command_arbitrator import CommandArbitrator
from command_arbitrators.policy_manager import PolicyRole
from doom.agents.aimer_copilot import AimerCopilot
from doom.agents.runner_copilot import RunnerCopilot
from doom.agents.shooter_copilot import ShooterCopilot
from doom.doom_state_listener import DoomStateListener
from input_sources.physical_controller_listener import PhysicalControllerListener

controller_listener = PhysicalControllerListener()
game_state_listener = DoomStateListener(log_file_path="../Doom/log.txt")

pilot = HumanActor(controller_listener, config_file_path="config.toml")  # Primary Agent

copilot_1 = ShooterCopilot(game_state_listener)  # Secondary Agent 1
copilot_2 = RunnerCopilot(game_state_listener)  # Secondary Agent 2
copilot_3 = AimerCopilot(game_state_listener)  # Secondary Agent 3

arbitrator = CommandArbitrator(config_file_path="config.toml")
arbitrator.add_actor(pilot, PolicyRole.PILOT)
arbitrator.add_actor(copilot_1, PolicyRole.COPILOT)
arbitrator.add_actor(copilot_2, PolicyRole.COPILOT)
arbitrator.add_actor(copilot_3, PolicyRole.COPILOT)

arbitrator.start()

while True:
    time.sleep(1)  # Keep the main thread alive

