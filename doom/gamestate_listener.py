import threading

from doom import GameLogMessage, MessageType
from doom.observers.gamestate_observer import GameStateObserver


class GameStateListener:
    """
    GameStateListener class reads the Ultimate Doom log files and notifies its subscribers with Game State updates.
    It runs in a separate thread.
    """

    LOG_FILE_GAME_STATE_PREFIX = "[GS] "

    def __init__(self, log_file_path: str):
        self.log_file_path: str = log_file_path
        self.subscribers: list[GameStateObserver] = []
        self.running: bool = False
        self.listener_thread: threading.Thread = None

    def subscribe(self, subscriber: GameStateObserver) -> None:
        """
        Adds a subscriber to the list of subscribers
        """
        self.subscribers.append(subscriber)

    def notify_all(self, state: GameLogMessage) -> None:
        """
        Notifies all subscribers of an input
        """
        for subscriber in self.subscribers:
            subscriber.update_from_game_state(state)

    def start_listening(self) -> None:
        """
        Starts listening to the physical controller inputs and notifies its subscribers
        """
        if self.listener_thread is None or not self.listener_thread.is_alive():
            self.running = True
            self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listener_thread.start()

    def stop_listening(self) -> None:
        """
        Stops listening for inputs
        """
        self.running = False
        if self.listener_thread:
            self.listener_thread.join()

    def _listen_loop(self) -> None:
        """
        The loop that listens for game state updates
        """
        with open(self.log_file_path, "r") as file:
            # Move the cursor to the end of the file
            file.seek(0, 2)  # 2 = SEEK_END

            while self.running:
                line = file.readline()
                if line and line.startswith(self.LOG_FILE_GAME_STATE_PREFIX):
                    line = line[len(GameStateListener.LOG_FILE_GAME_STATE_PREFIX):]

                    message_type = line.split(" ")[0]
                    message_data = line[len(message_type) + 1:]

                    if message_type in MessageType:
                        state = GameLogMessage(MessageType(message_type), message_data)
                        self.notify_all(state)
