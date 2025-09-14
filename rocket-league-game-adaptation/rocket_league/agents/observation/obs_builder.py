from abc import ABC, abstractmethod
from typing import Any

import numpy as np
import numpy.typing as npt

from ...mod import PlayerData, RLGameState


class ObsBuilder(ABC):
    @abstractmethod
    def build_obs(
        self,
        player_state: PlayerData,
        game_state: RLGameState,
        player_input: npt.NDArray[np.float32],
        previous_action: npt.NDArray[np.float32],
    ) -> Any:
        pass
