import time

from agents.pilot import Pilot
from command_arbitrators.dual_arbitrator import DualArbitrator
from doom.expert_system_copilot import ExpertSystemCopilot

pilot = Pilot(config_file_path = "config.toml") # Primary Agent
copilot = ExpertSystemCopilot(log_file_path = "../Doom/log.txt") # Secondary Agent

arbitrator = DualArbitrator(pilot = pilot, copilot = copilot) # Command Arbitrator

pilot.start() # Start the Pilot
copilot.start() # Start the Copilot

while True:
    time.sleep(1) ## Keep the main thread alive
