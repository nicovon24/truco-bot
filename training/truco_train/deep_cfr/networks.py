"""Redes de ventajas y de estrategia (MLP encode -> 256 -> 256 -> 13).

Durante los recorridos la inferencia se hace con NumPy sobre los pesos exportados (`NumpyMLP`):
una muestra por nodo en PyTorch es mucho más lenta que un producto matricial chico en NumPy.
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
import torch
from torch import nn

FloatArray = npt.NDArray[np.float32]


class MLP(nn.Module):
    def __init__(self, input_size: int, num_actions: int, hidden: int = 256) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, num_actions),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out: torch.Tensor = self.net(x)
        return out


class NumpyMLP:
    """Copia de solo lectura de un `MLP` para inferencia rápida de a una muestra."""

    def __init__(self, model: MLP) -> None:
        layers = [m for m in model.net if isinstance(m, nn.Linear)]
        self.weights = [
            layer.weight.detach().cpu().numpy().T.astype(np.float32) for layer in layers
        ]
        self.biases = [layer.bias.detach().cpu().numpy().astype(np.float32) for layer in layers]

    def __call__(self, x: FloatArray) -> FloatArray:
        h = x
        last = len(self.weights) - 1
        for i, (w, b) in enumerate(zip(self.weights, self.biases, strict=True)):
            h = h @ w + b
            if i < last:
                h = np.maximum(h, 0.0)
        return h


def regret_matching_np(advantages: FloatArray, legal: list[int]) -> list[float]:
    """Estrategia sobre `legal` proporcional a las ventajas positivas; uniforme si no hay."""
    positive = [max(float(advantages[a]), 0.0) for a in legal]
    total = sum(positive)
    if total > 0.0:
        return [p / total for p in positive]
    # Convención de Deep CFR: sin ventajas positivas, la acción de mayor ventaja.
    best = max(range(len(legal)), key=lambda i: float(advantages[legal[i]]))
    return [1.0 if i == best else 0.0 for i in range(len(legal))]


def masked_softmax_np(logits: FloatArray, legal: list[int]) -> list[float]:
    values = np.array([logits[a] for a in legal], dtype=np.float64)
    values -= values.max()
    exp = np.exp(values)
    probs = exp / exp.sum()
    return [float(p) for p in probs]
