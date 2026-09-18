"""HeuristicAgent: reglas documentadas con umbrales en config.

Reglas (en orden de prioridad):

1. Envido pendiente de respuesta: sube si su envido alcanza `envido_raise_threshold` (falta si
   alcanza `falta_envido_threshold`); si no, quiere cuando alcanza `envido_accept_threshold`
   más 2 por cada canto extra de la cadena (+3 si hay falta). Si no, no quiere.
2. Truco pendiente de respuesta: canta envido primero si puede y tiene `envido_call_threshold`;
   si no, sube con fuerza >= `truco_raise_strength`, quiere con fuerza >= `truco_accept_strength`
   y en otro caso no quiere.
3. Turno propio: canta envido si puede y alcanza `envido_call_threshold` (real/falta según sus
   umbrales); si no, canta truco/subida con fuerza >= `truco_call_strength`; si no, tira carta.
4. Carta: si el rival ya tiró en la baza, la menor carta que le gana (o la menor si ninguna gana);
   si abre, la menor en la primera baza y la mayor en las siguientes.

Farol: con probabilidad `bluff_probability` elige un canto de truco (o querer) sin fuerza. La
policy devuelve estas probabilidades de forma explícita. Nunca se va al mazo.
"""

from __future__ import annotations

from dataclasses import dataclass

from truco_engine.actions import LEVEL_TRUCO_ACTION, TRUCO_ACTIONS, Action
from truco_engine.agents.base import Policy, PolicyAgent, normalize
from truco_engine.cards import NUM_TRUCO_RANKS, TRUCO_RANK
from truco_engine.observation import Observation
from truco_engine.state import NO_CARD, PARDA


@dataclass(frozen=True, slots=True)
class HeuristicConfig:
    envido_call_threshold: int = 27
    real_envido_threshold: int = 30
    falta_envido_threshold: int = 33
    envido_accept_threshold: int = 26
    envido_raise_threshold: int = 31
    truco_call_strength: float = 0.70
    truco_accept_strength: float = 0.45
    truco_raise_strength: float = 0.80
    bluff_probability: float = 0.05


def hand_strength(obs: Observation) -> float:
    """Fuerza en [0, 1]: promedio de escalones restantes ajustado por bazas ganadas/perdidas."""
    remaining = obs.my_remaining
    if remaining:
        base = sum(TRUCO_RANK[c] for c in remaining) / (len(remaining) * NUM_TRUCO_RANKS)
    else:
        base = 0.0
    for result in obs.results:
        if result == PARDA:
            continue
        base += 0.25 if result == obs.player else -0.25
    rival_card = _rival_card_on_table(obs)
    if rival_card != NO_CARD and any(TRUCO_RANK[c] > TRUCO_RANK[rival_card] for c in remaining):
        base += 0.1
    return min(1.0, max(0.0, base))


def _rival_card_on_table(obs: Observation) -> int:
    if obs.baza >= len(obs.played):
        return NO_CARD
    pair = obs.played[obs.baza]
    if pair[obs.player] != NO_CARD:
        return NO_CARD
    return pair[obs.rival]


class HeuristicAgent(PolicyAgent):
    name = "heuristic"

    def __init__(self, config: HeuristicConfig | None = None) -> None:
        self.config = config or HeuristicConfig()

    def policy(self, obs: Observation, legal: list[Action]) -> Policy:
        primary = self._primary(obs, legal)
        bluffs = self._bluffs(obs, legal, primary)
        if not bluffs:
            return normalize({primary: 1.0}, legal)
        eps = self.config.bluff_probability
        weights = {primary: 1.0 - eps}
        for a in bluffs:
            weights[a] = weights.get(a, 0.0) + eps / len(bluffs)
        return normalize(weights, legal)

    # -- decisión principal ------------------------------------------------

    def _primary(self, obs: Observation, legal: list[Action]) -> Action:
        cfg = self.config
        envido = obs.my_envido
        strength = hand_strength(obs)
        truco_raise = next((a for a in TRUCO_ACTIONS if a in legal), None)

        if obs.envido_pending:
            if envido >= cfg.falta_envido_threshold and Action.FALTA_ENVIDO in legal:
                return Action.FALTA_ENVIDO
            if envido >= cfg.envido_raise_threshold:
                for raise_ in (Action.REAL_ENVIDO, Action.ENVIDO):
                    if raise_ in legal:
                        return raise_
            need = cfg.envido_accept_threshold + 2 * (len(obs.envido_calls) - 1)
            if Action.FALTA_ENVIDO in obs.envido_calls:
                need += 3
            return Action.QUIERO if envido >= need else Action.NO_QUIERO

        envido_call = self._envido_call(envido, legal)

        if obs.truco_pending:
            if envido_call is not None:
                return envido_call
            if truco_raise is not None and strength >= cfg.truco_raise_strength:
                return truco_raise
            return Action.QUIERO if strength >= cfg.truco_accept_strength else Action.NO_QUIERO

        if envido_call is not None:
            return envido_call
        if truco_raise is not None and strength >= cfg.truco_call_strength:
            return truco_raise
        return self._card(obs, legal)

    def _envido_call(self, envido: int, legal: list[Action]) -> Action | None:
        cfg = self.config
        if Action.ENVIDO not in legal:
            return None
        if envido >= cfg.falta_envido_threshold:
            return Action.FALTA_ENVIDO
        if envido >= cfg.real_envido_threshold:
            return Action.REAL_ENVIDO
        if envido >= cfg.envido_call_threshold:
            return Action.ENVIDO
        return None

    def _card(self, obs: Observation, legal: list[Action]) -> Action:
        slots = [
            (TRUCO_RANK[c], i)
            for i, c in enumerate(obs.my_slots)
            if c != NO_CARD and Action(i) in legal
        ]
        slots.sort()
        rival_card = _rival_card_on_table(obs)
        if rival_card != NO_CARD:
            winners = [s for s in slots if s[0] > TRUCO_RANK[rival_card]]
            return Action((winners or slots)[0][1])
        if obs.baza == 0:
            return Action(slots[0][1])
        return Action(slots[-1][1])

    # -- faroles -----------------------------------------------------------

    def _bluffs(self, obs: Observation, legal: list[Action], primary: Action) -> list[Action]:
        if self.config.bluff_probability <= 0.0:
            return []
        if obs.envido_pending:
            return []
        if obs.truco_pending:
            if primary is Action.NO_QUIERO:
                return [Action.QUIERO]
            return []
        next_level = obs.truco_level + 1
        if next_level <= 4:
            call = LEVEL_TRUCO_ACTION[next_level]
            if call in legal and call is not primary:
                return [call]
        return []
