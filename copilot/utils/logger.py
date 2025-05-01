import threading
import time
from typing import TYPE_CHECKING
from ..sources.game import GameStateObserver


if TYPE_CHECKING:
    from ..command_arbitrators.command_arbitrator import CommandArbitrator
    from ..sources.virtual_controller_provider import VirtualControllerProvider
    from ..sources.game import GameStateListener, GameState


class Logger(GameStateObserver):
    """
    Logger is the class that handles writing the state of the copilot architecture on a log file
    """

    def __init__(
            self,
            game_state_listener : 'GameStateListener',
            virtual_controller : 'VirtualControllerProvider',
            arbitrator : 'CommandArbitrator',
            log_file_path: str | None = None
    ) -> None:
        if log_file_path is None:
            log_file_path = "test_log.txt"

        self.game_state_listener = game_state_listener
        self.virtual_controller = virtual_controller
        self.arbitrator = arbitrator
        self.log_file_path: str = log_file_path

        self.running: bool = False
        self._thread: threading.Thread | None = None
        self.game_state : str = ""

        self.game_state_listener.subscribe(self)

    def start(self) -> None:
        if self._thread is None or not self._thread.is_alive():
            self.running = True
            self._thread = threading.Thread(target=self._logging_loop, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self.running = False
        if self._thread:
            self._thread.join()

    def _logging_loop(self):
        idx = 0
        with open(self.log_file_path, "w") as file:

            while self.running:
                file.write(f"Hello {idx}\n")
                file.write(f"GameState:{self.game_state}\n")
                file.write(f"VirtualController:{self.virtual_controller.get_controller_state()}\n")
                file.write(f"Arbitrator:{self.arbitrator.get_state()}\n")
                idx += 1
                time.sleep(1)

    def on_game_state_update(self, game_state: 'GameState') -> None:
        self.game_state = self.game_state_listener.game_state_to_log(game_state)
