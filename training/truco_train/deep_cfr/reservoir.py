"""Reservoir buffers de ventajas y estrategia.

Guardan (tensor de info, iteración, objetivo) con muestreo reservorio: cuando se llena, cada nueva
muestra reemplaza una existente con probabilidad capacidad / vistas, así el buffer es una muestra
uniforme de todo lo visto. Los tensores se guardan en float16 para ahorrar memoria.
"""

from __future__ import annotations

from random import Random

import numpy as np
import numpy.typing as npt


class ReservoirBuffer:
    def __init__(self, capacity: int, input_size: int, num_actions: int) -> None:
        self.capacity = capacity
        self.inputs = np.zeros((capacity, input_size), dtype=np.float16)
        self.targets = np.zeros((capacity, num_actions), dtype=np.float32)
        self.masks = np.zeros((capacity, num_actions), dtype=np.bool_)
        self.iterations = np.zeros(capacity, dtype=np.float32)
        self.size = 0
        self.seen = 0

    def add(
        self,
        x: npt.NDArray[np.float32],
        target: npt.NDArray[np.float32],
        mask: npt.NDArray[np.bool_],
        iteration: int,
        rng: Random,
    ) -> None:
        self.seen += 1
        if self.size < self.capacity:
            idx = self.size
            self.size += 1
        else:
            idx = rng.randrange(self.seen)
            if idx >= self.capacity:
                return
        self.inputs[idx] = x
        self.targets[idx] = target
        self.masks[idx] = mask
        self.iterations[idx] = iteration

    def arrays(
        self,
    ) -> tuple[
        npt.NDArray[np.float32],
        npt.NDArray[np.float32],
        npt.NDArray[np.bool_],
        npt.NDArray[np.float32],
    ]:
        n = self.size
        return (
            self.inputs[:n].astype(np.float32),
            self.targets[:n],
            self.masks[:n],
            self.iterations[:n],
        )
