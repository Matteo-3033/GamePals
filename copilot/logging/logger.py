import os
from datetime import datetime
import threading
import time
from pathlib import Path
from typing import List
import logging

from copilot.logging.loggable import Loggable

logger = logging.getLogger(__name__)


class Logger:
    """
    Logger is the class that handles writing the state of the copilot architecture on a log file
    """

    def __init__(
            self,
            loggables : List[Loggable],
            log_file_path: str | None = None
    ) -> None:
        # If file already exists, fall back to default path to avoid accidental override
        if log_file_path:
            if os.path.exists(log_file_path):
                logger.warning(f"File '{log_file_path}' already exists. Using default '{self._get_default_log_file_path()}' instead.")
                log_file_path = self._get_default_log_file_path()
        else:
            log_file_path = self._get_default_log_file_path()

        self.loggables = loggables
        self.log_file_path: str = log_file_path
        self.running: bool = False
        self._thread: threading.Thread | None = None
        self._start_time: float = 0.0

        # Eventually create the log folder
        log_path = Path(self.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _get_default_log_file_path() -> str:
        return datetime.now().strftime("log/%Y-%m-%d_%H-%M-%S.log")

    def start(self) -> None:
        if self._thread is None or not self._thread.is_alive():
            self.running = True
            self._start_time = time.time()
            self._thread = threading.Thread(target=self._logging_loop, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self.running = False
        if self._thread:
            self._thread.join()

    def _logging_loop(self):
        idx = 0
        with (open(self.log_file_path, "w") as file):
            while self.running:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                time_since_start = time.time() - self._start_time

                file.write(f"--- Log #{idx} | {now} ({time.time()}) | {time_since_start:.2f}s since start ---\n")
                for loggable in self.loggables:
                    file.write(f"{loggable.get_tag()}: \n\t{loggable.get_log().replace("\n", "\n\t")}\n")
                file.write("\n")

                idx += 1
                time.sleep(1)