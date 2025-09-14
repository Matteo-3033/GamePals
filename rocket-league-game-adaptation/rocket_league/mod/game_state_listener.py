import json
import logging
import socket
import struct
import threading as th
import time
from typing import Any

from gamepals.sources.game import GameStateListener

from .game_packet import Focus, GamePacket
from .game_state import RLGameState

logger = logging.getLogger(__name__)


class RLGameStateListener(GameStateListener):
    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = 3000
    DEFAULT_TARGET_FPS = 120
    DEFAULT_TICK_SKIP = 8
    MAX_ATTEMPTS = 20
    RETRAY_DELAY = 10

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        target_fps: int = DEFAULT_TARGET_FPS,
        tick_skip: int = DEFAULT_TICK_SKIP,
        max_attempts: int = MAX_ATTEMPTS,
        retry_delay: int = RETRAY_DELAY,
    ) -> None:
        super().__init__()

        self.host = host
        self.port = port

        self.max_attempts = max_attempts
        self.retry_delay = retry_delay

        self.target_fps = target_fps
        self.tick_skip = tick_skip

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.receive_thread: th.Thread | None = None
        self.game_state = RLGameState()
        self.__prev_time = 0.0
        self.__ticks = 0
        self._running = False
        self.__lock = th.RLock()

    def start_listening(self) -> None:
        if self._running:
            return

        with self.__lock:
            if self._running:
                return
            self._running = True

        self.game_state = RLGameState()
        self.__prev_time = 0.0
        self.__ticks = 0

        for attemp in range(self.max_attempts):
            try:
                logger.info(
                    f"Connecting to game at {self.host}:{self.port} with target FPS {self.target_fps} and tick skip {self.tick_skip}..."
                )
                self.client_socket.connect((self.host, self.port))
                logger.info(f"Connected to game.")

                self.receive_thread = th.Thread(
                    target=self.__listen_to_messages, daemon=True
                )
                self.receive_thread.start()
                break

            except socket.error as e:
                if attemp < self.max_attempts:
                    time.sleep(self.retry_delay)

        else:
            logger.error(
                f"Failed to connect to game after {self.max_attempts} attempts. Exiting."
            )
            self.stop_listening()

    def stop_listening(self) -> None:
        if not self._running:
            return
        with self.__lock:
            if not self._running:
                return
            self._running = False

        logger.info("Stopping listening to game state updates")
        self.client_socket.close()

        if self.receive_thread is not None:
            self.receive_thread.join()
            self.receive_thread = None

    def __listen_to_messages(self) -> None:
        try:
            while self._running:
                packet = self.__read_packet()
                if packet is None:
                    continue

                if (
                    packet.focus == Focus.GAME
                ):  # GAME packets are transmitted every tick_skip ticks
                    cur_time = packet.game_info.seconds_elapsed
                    delta = cur_time - self.__prev_time
                    self.__prev_time = cur_time
                    ticks_elapsed = round(delta * self.target_fps)
                    self.__ticks += ticks_elapsed

                    self.game_state.decode(packet, ticks_elapsed)
                else:
                    self.game_state.decode(packet, 0)
                    self.__ticks = (
                        self.tick_skip
                    )  # Non-GAME packets are immediately transmitted

                if self.__ticks < self.tick_skip:
                    continue
                self.__ticks = 0

                self.notify_all(self.game_state)

        except socket.error as e:
            logger.error(f"Error reading game state: {e}")
        finally:
            self.stop_listening()

    def __read_packet(self) -> GamePacket | None:
        data_length_bytes = self.client_socket.recv(4)
        if not data_length_bytes:
            return None

        data_length = struct.unpack("!I", data_length_bytes)[0]

        msg_bytes_buffer = b""
        while len(msg_bytes_buffer) < data_length:
            packet = self.client_socket.recv(data_length - len(msg_bytes_buffer))
            if not packet:
                return None
            msg_bytes_buffer += packet

        msg = msg_bytes_buffer.decode("utf-8")

        try:
            return GamePacket.from_json(json.loads(msg))
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding game state packet: {e}")
            return None

    def get_json(self) -> dict[str, Any]:
        # TODO: Aggiungere:
        # - Se la macchina è in area
        # - Distanza dalla palla
        # - Velocità della palla
        # - Velocità della macchina
        # - Distanza dalla porta avversaria
        # - Distanza dalla propria porta
        # - Distanza dall'altro giocatore

        return {
            "focus": self.game_state.focus.value,
            "blue_score": int(self.game_state.blue_score),
            "orange_score": int(self.game_state.orange_score),
            "local_player_team": int(self.game_state.local_player.team_num),
        }
