"""Regret matching y regret matching+."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]


def regret_matching(regrets: FloatArray, legal_mask: npt.NDArray[np.bool_]) -> FloatArray:
    """Estrategia proporcional a los regrets positivos; uniforme sobre legales si no hay."""
    positive: FloatArray = np.where(legal_mask, np.maximum(regrets, 0.0), 0.0)
    total = float(positive.sum())
    if total > 0.0:
        out: FloatArray = positive / total
        return out
    n = int(legal_mask.sum())
    return np.where(legal_mask, 1.0 / n, 0.0)


def normalize_average(strategy_sum: FloatArray, legal_mask: npt.NDArray[np.bool_]) -> FloatArray:
    total = float(strategy_sum[legal_mask].sum())
    if total > 0.0:
        avg: FloatArray = np.where(legal_mask, strategy_sum / total, 0.0)
        return avg
    n = int(legal_mask.sum())
    return np.where(legal_mask, 1.0 / n, 0.0)
