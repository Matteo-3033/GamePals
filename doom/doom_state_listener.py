import threading

from doom import MessageType, DoomGameState
from input_sources.game_state_listener import GameStateListener


class DoomStateListener(GameStateListener):
    """
    DoomStateListener is aGameStateListener implementation that reads the Ultimate Doom log files and notifies its subscribers with Game State updates.
    It runs in a separate thread.
    """

    LOG_FILE_GAME_STATE_PREFIX = "[GS] "

    def __init__(self, log_file_path: str):
        super().__init__()
        self.log_file_path: str = log_file_path
        self.running: bool = False
        self.listener_thread: threading.Thread = None

    def start_listening(self):
        if self.listener_thread is None or not self.listener_thread.is_alive():
            self.running = True
            self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listener_thread.start()

    def stop_listening(self) -> None:
        """ Stops listening for inputs """
        self.running = False
        if self.listener_thread:
            self.listener_thread.join()

    def _listen_loop(self) -> None:
        """ The loop that listens for game state updates """
        with open(self.log_file_path, "r") as file:
            # Move the cursor to the end of the file
            file.seek(0, 2)  # 2 = SEEK_END

            while self.running:
                line = file.readline()
                if line and line.startswith(self.LOG_FILE_GAME_STATE_PREFIX):
                    line = line[len(self.LOG_FILE_GAME_STATE_PREFIX):]

                    message_type = line.split(" ")[0].strip()
                    message_data = line[len(message_type) + 1:]

                    if message_type in MessageType:
                        state = DoomGameState(MessageType(message_type), message_data)
                        self.notify_all(state)
                    else:
                        print("Unrecognized message type: " + message_type)
