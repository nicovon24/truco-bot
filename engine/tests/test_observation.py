from __future__ import annotations

from dataclasses import replace
from random import Random

import numpy as np

from truco_engine.actions import Action
from truco_engine.cards import DECK
from truco_engine.config import RulesConfig
from truco_engine.observation import ENCODE_SIZE, encode, info_key, observe
from truco_engine.rules import apply, legal_actions, new_game, next_hand
from truco_engine.state import NO_CARD, GameState, Phase
from truco_engine.testing import B, C, E, O, build, play

H0 = [(7, O), (6, O), (4, E)]
H1 = [(1, E), (3, C), (12, B)]


def _random_states(seed: int, max_steps: int = 400) -> list[GameState]:
    rng = Random(seed)
    state = new_game(RulesConfig(), rng)
    states = [state]
    for _ in range(max_steps):
        if state.phase is Phase.GAME_OVER:
            break
        if state.phase is Phase.HAND_OVER:
            state = next_hand(state, rng)
        else:
            state = apply(state, rng.choice(legal_actions(state)))
        states.append(state)
    return states


def _swap_hidden_rival_cards(state: GameState, player: int, rng: Random) -> GameState:
    """Reemplaza las cartas no jugadas del rival por otras cartas no visibles para `player`."""
    hand = state.hand
    rival = 1 - player
    played = {c for pair in hand.played for c in pair if c != NO_CARD}
    visible = set(hand.hands[player]) | played
    hidden_slots = [i for i in range(3) if not hand.slot_used(rival, i)]
    pool = [c for c in DECK if c not in visible]
    new_cards = rng.sample(pool, len(hidden_slots))
    rival_hand = list(hand.hands[rival])
    for slot, card in zip(hidden_slots, new_cards, strict=True):
        rival_hand[slot] = card
    hands = list(hand.hands)
    hands[rival] = (rival_hand[0], rival_hand[1], rival_hand[2])
    values = list(hand.envido_values)
    values[rival] = 0 if hand.envido.values is None else values[rival]
    return replace(
        state,
        hand=replace(
            hand,
            hands=(hands[0], hands[1]),
            envido_values=(values[0], values[1]),
        ),
    )


def test_observation_never_contains_hidden_rival_cards() -> None:
    for seed in range(40):
        for state in _random_states(seed):
            for player in (0, 1):
                obs = observe(state, player)
                rival = 1 - player
                hidden = {
                    c
                    for i, c in enumerate(state.hand.hands[rival])
                    if not state.hand.slot_used(rival, i)
                }
                assert not hidden & set(obs.my_slots)
                assert not hidden & {c for pair in obs.played for c in pair}
                if not (state.hand.envido.resolved and state.hand.envido.accepted):
                    assert obs.envido_values is None


def test_encode_and_info_key_do_not_depend_on_hidden_cards() -> None:
    rng = Random(99)
    for seed in range(30):
        for state in _random_states(seed, max_steps=60):
            for player in (0, 1):
                other = _swap_hidden_rival_cards(state, player, rng)
                a, b = observe(state, player), observe(other, player)
                assert info_key(a) == info_key(b)
                assert np.array_equal(encode(a), encode(b))


def test_encode_shape_is_constant() -> None:
    for seed in range(20):
        for state in _random_states(seed):
            for player in (0, 1):
                x = encode(observe(state, player))
                assert x.shape == (ENCODE_SIZE,)
                assert x.dtype == np.float32
                assert np.all(np.isfinite(x))
                assert np.all((x >= 0.0) & (x <= 1.0))


def test_encode_size_is_documented_value() -> None:
    assert ENCODE_SIZE == 317


def test_info_key_format() -> None:
    s = build(H0, H1)
    assert info_key(observe(s, 0)) == "c=1.3.11|e=33|m=1|s=0-0|v=-|h="
    assert info_key(observe(s, 1)) == "c=7.10.14|e=3|m=0|s=0-0|v=-|h="
    s = play(s, Action.ENVIDO, Action.QUIERO, Action.PLAY_CARD_2)
    assert info_key(observe(s, 1)) == "c=7.10.14|e=-|m=0|s=0-2|v=3-33|h=bE,aQ,b11"


def test_envido_values_become_public() -> None:
    s = play(build(H0, H1), Action.ENVIDO, Action.QUIERO)
    obs = observe(s, 1)
    assert obs.envido_values == (33, 3)
