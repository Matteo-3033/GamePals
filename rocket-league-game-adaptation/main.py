import logging
import sys
import time

from gamepals.agents import HumanActor
from gamepals.agents.actions import (
    ActionConversionDelegate,
    ActionConversionManager,
    ActionToAxisDelegate,
    ActionToBinaryInputsDelegate,
)
from gamepals.command_arbitrators import CommandArbitrator
from gamepals.sources import PhysicalControllerListener
from gamepals.utils import ArgParser
from gamepals.utils.logging import Logger

from rocket_league.agents import *
from rocket_league.mod import RLGameStateListener


def main(arg_parser: ArgParser) -> None:
    # Logger
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logger = logging.getLogger(__name__)

    # (Globally) init Configuration Handler
    config_handler = arg_parser.init_config_handler()

    delegates: list[ActionConversionDelegate] = [
        ActionToBinaryInputsDelegate(0, RLGameAction.THROTTLE),
        ActionToAxisDelegate(0, RLGameAction.STEER_YAW),
        ActionToBinaryInputsDelegate(1, RLGameAction.THROTTLE),
        ActionToAxisDelegate(1, RLGameAction.STEER_YAW),
        ActionToBinaryInputsDelegate(2, RLGameAction.THROTTLE),
        ActionToAxisDelegate(2, RLGameAction.STEER_YAW),
    ]
    conversion_manager = ActionConversionManager(delegates)

    arbitrator = CommandArbitrator(
        config_handler.get_policy_types(), conversion_manager
    )

    # Human Pilots
    pilots: list[HumanActor] = list()
    controller_listeners: list[PhysicalControllerListener] = list()

    for gamepad_index in range(config_handler.get_humans_count()):
        # Register Human Actor
        controller_listener = PhysicalControllerListener(
            gamepad_number=gamepad_index, late_init=True
        )
        pilot = HumanActor(controller_listener, conversion_manager)
        arbitrator.add_actor(pilot)
        # Track Pilots and Listeners
        pilots.append(pilot)
        controller_listeners.append(controller_listener)

        logger.info(
            f"Registered human actor for gamepad {gamepad_index} with ID {pilot.get_id()}."
        )

    # AI Agents
    game_state_listener = RLGameStateListener()

    for agent in config_handler.get_necessary_agents():
        agent_params = config_handler.get_params_for_agent(agent.get_name())
        if "pilot_idx" in agent_params:
            pilot_idx = agent_params.pop("pilot_idx", -1)
            if 0 <= pilot_idx < len(pilots):
                agent_params["pilot"] = pilots[pilot_idx]
            else:
                logger.warning(
                    "No pilot or invalid pilot specified for agent %s", agent.get_name()
                )

        agent_instance = agent(game_state_listener, **agent_params)

        arbitrator.add_actor(agent_instance)

        logger.info(
            f"Registered agent {agent.get_name()} with ID {agent_instance.get_id()}."
        )

    system_logger = Logger(
        loggables=[
            game_state_listener,
            arbitrator,
            arbitrator.get_virtual_controller(),
        ],
        log_file_path=arg_parser.get_output_file(),
    )

    arbitrator.start()
    game_state_listener.start_listening()
    system_logger.start()

    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        pass
    finally:
        system_logger.stop()
        game_state_listener.stop_listening()
        for controller_listener in controller_listeners:
            controller_listener.stop_listening()  # Known issue: this only really stops after you press an input on the controller


if __name__ == "__main__":
    parser = ArgParser()
    main(parser)
