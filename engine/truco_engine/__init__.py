"""Motor de reglas de Truco argentino 1 vs 1. Sin dependencias web ni de ML."""

from truco_engine.actions import CONTRACT_VERSION, NUM_ACTIONS, Action
from truco_engine.config import RulesConfig
from truco_engine.game import play_game
from truco_engine.observation import ENCODE_SIZE, Observation, encode, info_key, observe
from truco_engine.rules import IllegalActionError, apply, legal_actions, new_game, next_hand
from truco_engine.state import GameState, HandState, Phase

__all__ = [
    "CONTRACT_VERSION",
    "ENCODE_SIZE",
    "NUM_ACTIONS",
    "Action",
    "GameState",
    "HandState",
    "IllegalActionError",
    "Observation",
    "Phase",
    "RulesConfig",
    "apply",
    "encode",
    "info_key",
    "legal_actions",
    "new_game",
    "next_hand",
    "observe",
    "play_game",
]
