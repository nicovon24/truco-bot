"""Export de redes a ONNX con test de paridad PyTorch vs ONNX Runtime."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch
from torch import nn

from truco_engine.agents.neural_agent import INPUT_NAME, OUTPUT_NAME

PARITY_ATOL = 1e-4


def export_mlp(model: nn.Module, input_size: int, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    model.eval()
    dummy = torch.zeros(1, input_size, dtype=torch.float32)
    torch.onnx.export(
        model,
        (dummy,),
        str(path),
        input_names=[INPUT_NAME],
        output_names=[OUTPUT_NAME],
        dynamic_axes={INPUT_NAME: {0: "batch"}, OUTPUT_NAME: {0: "batch"}},
        opset_version=17,
        dynamo=False,
    )


def parity_error(
    model: nn.Module, path: Path, input_size: int, samples: int = 256, seed: int = 0
) -> float:
    """Máximo error absoluto entre PyTorch y ONNX Runtime sobre entradas aleatorias en [0, 1]."""
    rng = np.random.default_rng(seed)
    x = rng.random((samples, input_size), dtype=np.float32)
    model.eval()
    with torch.no_grad():
        expected = model(torch.from_numpy(x)).numpy()
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    got = session.run([OUTPUT_NAME], {INPUT_NAME: x})[0]
    return float(np.max(np.abs(expected - got)))


def export_with_parity(model: nn.Module, input_size: int, path: Path) -> float:
    export_mlp(model, input_size, path)
    err = parity_error(model, path, input_size)
    if err > PARITY_ATOL:
        raise RuntimeError(f"paridad ONNX fallida: error máximo {err:.2e} > {PARITY_ATOL:.0e}")
    return err
