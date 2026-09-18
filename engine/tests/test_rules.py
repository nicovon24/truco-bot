from __future__ import annotations

from random import Random

import pytest

from truco_engine.actions import Action
from truco_engine.config import RulesConfig
from truco_engine.rules import IllegalActionError, apply, legal_actions, new_game, next_hand
from truco_engine.state import PARDA, Phase
from truco_engine.testing import B, C, E, O, build, play, slot_of

# Asiento 0 (mano): envido 33. Slots: 4E, 6O, 7O.
H0 = [(7, O), (6, O), (4, E)]
# Asiento 1: envido 3. Slots: 12B, 3C, 1E.
H1 = [(1, E), (3, C), (12, B)]

A = Action


def test_initial_legal_actions_for_mano() -> None:
    s = build(H0, H1)
    assert s.hand.current_player == 0
    assert legal_actions(s) == [
        A.PLAY_CARD_0,
        A.PLAY_CARD_1,
        A.PLAY_CARD_2,
        A.ENVIDO,
        A.REAL_ENVIDO,
        A.FALTA_ENVIDO,
        A.TRUCO,
        A.FOLD,
    ]


def test_illegal_action_raises() -> None:
    s = build(H0, H1)
    with pytest.raises(IllegalActionError):
        apply(s, A.QUIERO)
    with pytest.raises(IllegalActionError):
        apply(s, A.FLOR_RESERVED)


def test_apply_is_pure() -> None:
    s = build(H0, H1)
    before = repr(s)
    s2 = apply(s, A.TRUCO)
    assert repr(s) == before
    assert apply(s, A.TRUCO) == s2


# ---------------------------------------------------------------------------
# Truco
# ---------------------------------------------------------------------------


def test_truco_no_quiero_gives_one() -> None:
    s = play(build(H0, H1), A.TRUCO, A.NO_QUIERO)
    assert s.hand.finished
    assert s.hand.winner == 0
    assert s.scores == (1, 0)
    assert s.phase is Phase.HAND_OVER


def test_truco_quiero_then_retruco_no_quiero_gives_two() -> None:
    s = play(build(H0, H1), A.TRUCO, A.QUIERO)
    assert s.hand.truco.level == 2
    assert s.hand.current_player == 0
    # Quien hizo el último canto no puede subir.
    assert A.RETRUCO not in legal_actions(s)
    s = play(s, A.PLAY_CARD_0)
    assert A.RETRUCO in legal_actions(s)
    s = play(s, A.RETRUCO, A.NO_QUIERO)
    assert s.hand.winner == 1
    assert s.scores == (0, 2)


def test_raise_while_pending_accepts_previous() -> None:
    s = play(build(H0, H1), A.TRUCO, A.RETRUCO)
    assert s.hand.truco.level == 2
    assert s.hand.truco.pending
    assert s.hand.current_player == 0
    assert A.VALE_CUATRO in legal_actions(s)
    assert play(s, A.NO_QUIERO).scores == (0, 2)
    s = play(s, A.VALE_CUATRO)
    assert A.TRUCO not in legal_actions(s)
    assert A.RETRUCO not in legal_actions(s)
    assert A.VALE_CUATRO not in legal_actions(s)
    assert play(s, A.NO_QUIERO).scores == (3, 0)
    s = play(s, A.QUIERO)
    assert s.hand.truco.level == 4
    assert not any(a in legal_actions(s) for a in (A.TRUCO, A.RETRUCO, A.VALE_CUATRO))


def test_truco_value_awarded_to_hand_winner() -> None:
    s = play(build(H0, H1), A.TRUCO, A.QUIERO)
    # P0 tira 7 de oro contra 1 de espada, pierde; luego P1 gana con 3 contra 6.
    s = play(s, A.PLAY_CARD_2, A.PLAY_CARD_2, A.PLAY_CARD_1, A.PLAY_CARD_1)
    assert s.hand.winner == 1
    assert s.scores == (0, 2)


# ---------------------------------------------------------------------------
# Bazas y pardas
# ---------------------------------------------------------------------------


def test_first_parda_then_second_decides() -> None:
    s = build([(5, C), (4, E), (12, E)], [(5, O), (6, B), (11, C)], mano=0)
    s = play(s, slot_of(s, 0, 5, C), slot_of(s, 1, 5, O))
    assert s.hand.results == (PARDA,)
    assert s.hand.current_player == 0
    s = play(s, slot_of(s, 0, 4, E), slot_of(s, 1, 6, B))
    assert s.hand.winner == 1
    assert s.scores == (0, 1)


def test_second_parda_goes_to_first_winner() -> None:
    s = build([(2, E), (6, C), (4, E)], [(12, O), (6, O), (5, B)], mano=0)
    s = play(s, slot_of(s, 0, 2, E), slot_of(s, 1, 12, O))
    assert s.hand.results == (0,)
    s = play(s, slot_of(s, 0, 6, C), slot_of(s, 1, 6, O))
    assert s.hand.winner == 0


def test_three_pardas_go_to_mano() -> None:
    s = build([(3, E), (6, C), (4, E)], [(3, O), (6, O), (4, B)], mano=1)
    for number, s0, s1 in ((3, E, O), (6, C, O), (4, E, B)):
        s = play(s, slot_of(s, 1, number, s1), slot_of(s, 0, number, s0))
    assert s.hand.results == (PARDA, PARDA, PARDA)
    assert s.hand.winner == 1


def test_parda_leader_is_mano() -> None:
    s = build([(3, E), (6, C), (4, E)], [(3, O), (7, O), (5, B)], mano=1)
    s = play(s, slot_of(s, 1, 3, O), slot_of(s, 0, 3, E))
    assert s.hand.results == (PARDA,)
    assert s.hand.current_player == 1


def test_one_each_and_third_parda_goes_to_first_winner() -> None:
    s = build([(1, E), (4, C), (6, E)], [(12, O), (7, O), (6, B)], mano=0)
    s = play(s, slot_of(s, 0, 1, E), slot_of(s, 1, 12, O))
    s = play(s, slot_of(s, 0, 4, C), slot_of(s, 1, 7, O))
    assert s.hand.results == (0, 1)
    s = play(s, slot_of(s, 1, 6, B), slot_of(s, 0, 6, E))
    assert s.hand.results == (0, 1, PARDA)
    assert s.hand.winner == 0


def test_slots_are_stable_and_used_slot_is_illegal() -> None:
    s = play(build(H0, H1), A.PLAY_CARD_0, A.PLAY_CARD_2)
    # P1 ganó con 1 de espada y abre la segunda baza.
    assert s.hand.current_player == 1
    s = play(s, A.PLAY_CARD_0)
    legal = legal_actions(s)
    assert A.PLAY_CARD_0 not in legal
    assert A.PLAY_CARD_1 in legal
    assert A.PLAY_CARD_2 in legal


# ---------------------------------------------------------------------------
# Envido
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("chain", "response", "scores"),
    [
        ((A.ENVIDO,), A.QUIERO, (2, 0)),
        ((A.ENVIDO,), A.NO_QUIERO, (1, 0)),
        ((A.ENVIDO, A.ENVIDO), A.NO_QUIERO, (0, 2)),
        ((A.ENVIDO, A.ENVIDO), A.QUIERO, (4, 0)),
        ((A.REAL_ENVIDO,), A.NO_QUIERO, (1, 0)),
        ((A.ENVIDO, A.REAL_ENVIDO), A.QUIERO, (5, 0)),
        ((A.ENVIDO, A.ENVIDO, A.REAL_ENVIDO), A.QUIERO, (7, 0)),
        ((A.ENVIDO, A.ENVIDO, A.REAL_ENVIDO), A.NO_QUIERO, (4, 0)),
        ((A.ENVIDO, A.FALTA_ENVIDO), A.NO_QUIERO, (0, 2)),
        ((A.FALTA_ENVIDO,), A.QUIERO, (15, 0)),
    ],
)
def test_envido_chains(
    chain: tuple[Action, ...], response: Action, scores: tuple[int, int]
) -> None:
    s = play(build(H0, H1), *chain, response)
    assert s.scores == scores
    assert not s.hand.envido.pending
    assert s.hand.envido.resolved


def test_falta_envido_uses_leader_score() -> None:
    s = play(build(H0, H1, scores=(3, 10)), A.FALTA_ENVIDO, A.QUIERO)
    assert s.scores == (8, 10)


def test_envido_chain_limits() -> None:
    s = play(build(H0, H1), A.ENVIDO, A.ENVIDO)
    assert A.ENVIDO not in legal_actions(s)
    assert A.REAL_ENVIDO in legal_actions(s)
    s = play(s, A.REAL_ENVIDO)
    assert A.REAL_ENVIDO not in legal_actions(s)
    assert A.FALTA_ENVIDO in legal_actions(s)
    s = play(s, A.FALTA_ENVIDO)
    assert not any(a in legal_actions(s) for a in (A.ENVIDO, A.REAL_ENVIDO, A.FALTA_ENVIDO))
    s = play(build(H0, H1), A.REAL_ENVIDO)
    assert A.ENVIDO not in legal_actions(s)


def test_envido_values_public_only_when_accepted() -> None:
    s = play(build(H0, H1), A.ENVIDO, A.QUIERO)
    assert s.hand.envido.values == (33, 3)
    s = play(build(H0, H1), A.ENVIDO, A.NO_QUIERO)
    assert s.hand.envido.values is None


def test_envido_tie_goes_to_mano() -> None:
    s = build([(7, E), (6, E), (4, C)], [(7, C), (6, C), (4, B)], mano=1)
    s = play(s, A.ENVIDO, A.QUIERO)
    assert s.scores == (0, 2)


def test_envido_returns_turn_to_player_who_had_to_play() -> None:
    s = play(build(H0, H1), A.PLAY_CARD_0, A.ENVIDO)
    assert s.hand.current_player == 0
    s = play(s, A.QUIERO)
    assert s.hand.current_player == 1
    assert A.ENVIDO not in legal_actions(s)


def test_envido_only_before_own_first_card() -> None:
    s = play(build(H0, H1), A.PLAY_CARD_0)
    assert A.ENVIDO in legal_actions(s)
    s = play(s, A.PLAY_CARD_2)
    # Segunda baza: nadie puede cantar envido.
    assert A.ENVIDO not in legal_actions(s)


def test_envido_not_after_truco_accepted() -> None:
    s = play(build(H0, H1), A.TRUCO, A.QUIERO)
    assert A.ENVIDO not in legal_actions(s)


def test_envido_esta_primero() -> None:
    s = play(build(H0, H1), A.TRUCO)
    assert A.ENVIDO in legal_actions(s)
    s = play(s, A.ENVIDO)
    assert s.hand.current_player == 0
    assert A.TRUCO not in legal_actions(s)
    assert A.RETRUCO not in legal_actions(s)
    s = play(s, A.QUIERO)
    assert s.scores == (2, 0)
    # Resuelto el envido, el truco sigue pendiente para el que respondía.
    assert s.hand.truco.pending
    assert s.hand.current_player == 1
    assert legal_actions(s) == [A.RETRUCO, A.QUIERO, A.NO_QUIERO, A.FOLD]
    s = play(s, A.QUIERO)
    assert s.hand.truco.level == 2
    assert s.hand.current_player == 0


def test_envido_can_end_the_game_mid_hand() -> None:
    s = play(build(H0, H1, scores=(14, 0)), A.ENVIDO, A.QUIERO)
    assert s.phase is Phase.GAME_OVER
    assert s.winner == 0
    assert legal_actions(s) == []


# ---------------------------------------------------------------------------
# Irse al mazo
# ---------------------------------------------------------------------------


def test_fold_first_baza_without_envido_gives_bonus() -> None:
    s = play(build(H0, H1), A.FOLD)
    assert s.hand.winner == 1
    assert s.hand.folded_by == 0
    assert s.scores == (0, 2)


def test_fold_bonus_can_be_disabled() -> None:
    s = play(build(H0, H1, config=RulesConfig(fold_envido_bonus=False)), A.FOLD)
    assert s.scores == (0, 1)


def test_fold_after_envido_sung_has_no_bonus() -> None:
    s = play(build(H0, H1), A.ENVIDO, A.NO_QUIERO, A.FOLD)
    assert s.scores == (1, 1)


def test_fold_with_envido_pending_counts_as_no_quiero() -> None:
    s = play(build(H0, H1), A.ENVIDO, A.FOLD)
    assert s.scores == (2, 0)


def test_fold_with_truco_pending_counts_as_no_quiero() -> None:
    s = play(build(H0, H1), A.PLAY_CARD_0, A.PLAY_CARD_2, A.TRUCO, A.FOLD)
    assert s.scores == (0, 1)
    s = play(build(H0, H1), A.TRUCO, A.QUIERO, A.PLAY_CARD_0, A.RETRUCO, A.FOLD)
    assert s.scores == (0, 2)


def test_fold_with_truco_accepted_gives_level() -> None:
    s = play(build(H0, H1), A.TRUCO, A.QUIERO, A.FOLD)
    assert s.scores == (0, 2)


# ---------------------------------------------------------------------------
# Manos y partida
# ---------------------------------------------------------------------------


def test_next_hand_alternates_mano() -> None:
    rng = Random(7)
    s = new_game(RulesConfig(), rng, first_mano=0)
    with pytest.raises(IllegalActionError):
        next_hand(s, rng)
    s = play(s, A.FOLD)
    s = next_hand(s, rng)
    assert s.hand_number == 1
    assert s.hand.mano == 1
    assert s.hand.current_player == 1
    assert s.phase is Phase.PLAYING


def test_same_seed_same_deal() -> None:
    a = new_game(RulesConfig(), Random(123))
    b = new_game(RulesConfig(), Random(123))
    assert a == b
