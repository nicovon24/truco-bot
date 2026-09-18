"""NeuralAgent: carga .onnx (extra opcional [neural]).

La red recibe `encode(obs)` (entrada `obs`, float32 [N, ENCODE_SIZE]) y devuelve logits sobre las
13 acciones (salida `logits`). La policy es un softmax restringido a las acciones legales; el
agente muestrea de ella (nunca argmax). Inferencia con ONNX Runtime y NumPy, sin PyTorch.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from truco_engine.actions import NUM_ACTIONS, Action
from truco_engine.agents.base import Policy, PolicyAgent
from truco_engine.observation import ENCODE_SIZE, Observation, encode

INPUT_NAME = "obs"
OUTPUT_NAME = "logits"


class NeuralAgent(PolicyAgent):
    name = "neural"

    def __init__(self, session: Any, name: str | None = None) -> None:
        self.session = session
        if name is not None:
            self.name = name

    @classmethod
    def load(cls, path: Path, name: str | None = None) -> NeuralAgent:
        import onnxruntime as ort

        options = ort.SessionOptions()
        options.intra_op_num_threads = 1
        session = ort.InferenceSession(
            str(path), sess_options=options, providers=["CPUExecutionProvider"]
        )
        inputs = session.get_inputs()
        if inputs[0].name != INPUT_NAME or inputs[0].shape[-1] != ENCODE_SIZE:
            raise ValueError(f"modelo incompatible: entrada {inputs[0].name} {inputs[0].shape}")
        return cls(session, name=name)

    def logits(self, obs: Observation) -> np.ndarray[Any, np.dtype[np.float32]]:
        x = encode(obs)[None, :]
        out = self.session.run([OUTPUT_NAME], {INPUT_NAME: x})[0]
        logits: np.ndarray[Any, np.dtype[np.float32]] = np.asarray(out, dtype=np.float32)[0]
        if logits.shape != (NUM_ACTIONS,):
            raise ValueError(f"salida inesperada: {logits.shape}")
        return logits

    def policy(self, obs: Observation, legal: list[Action]) -> Policy:
        logits = self.logits(obs)
        values = np.array([logits[int(a)] for a in legal], dtype=np.float64)
        values -= values.max()
        exp = np.exp(values)
        probs = exp / exp.sum()
        return {a: float(p) for a, p in zip(legal, probs, strict=True)}
