"""legal_actions(state) y apply(state, action) -> state. Funciones puras.

El reparto es el único punto con azar y recibe un `random.Random` explícito (`new_game`,
`next_hand`). Una mano terminada deja la partida en `Phase.HAND_OVER` hasta que se reparte la
siguiente con `next_hand`.
"""

from __future__ import annotations

from dataclasses import replace
from random import Random

from truco_engine.actions import (
    LEVEL_TRUCO_ACTION,
    PLAY_ACTIONS,
    TRUCO_ACTION_LEVEL,
    Action,
)
from truco_engine.cards import DECK, compare_cards, envido_points, sort_slots
from truco_engine.config import RulesConfig
from truco_engine.scoring import (
    envido_accepted_points,
    envido_rejected_points,
    envido_winner,
    falta_envido_value,
    hand_winner,
)
from truco_engine.state import (
    NO_CARD,
    PARDA,
    GameState,
    HandState,
    Phase,
    PublicEvent,
)


class IllegalActionError(ValueError):
    pass


# ---------------------------------------------------------------------------
# Reparto
# ---------------------------------------------------------------------------


def deal_hand(mano: int, rng: Random) -> HandState:
    cards = rng.sample(DECK, 6)
    h0 = sort_slots(cards[:3])
    h1 = sort_slots(cards[3:])
    hands = ((h0[0], h0[1], h0[2]), (h1[0], h1[1], h1[2]))
    return HandState(
        mano=mano,
        hands=hands,
        envido_values=(envido_points(h0), envido_points(h1)),
        play_turn=mano,
    )


def new_game(config: RulesConfig, rng: Random, first_mano: int | None = None) -> GameState:
    mano = rng.randrange(2) if first_mano is None else first_mano
    return GameState(config=config, scores=(0, 0), hand_number=0, hand=deal_hand(mano, rng))


def next_hand(state: GameState, rng: Random) -> GameState:
    if state.phase is not Phase.HAND_OVER:
        raise IllegalActionError("solo se reparte cuando terminó la mano y no la partida")
    return replace(
        state,
        hand_number=state.hand_number + 1,
        hand=deal_hand(1 - state.hand.mano, rng),
    )


# ---------------------------------------------------------------------------
# Acciones legales
# ---------------------------------------------------------------------------


def _envido_open_for(hand: HandState, player: int) -> bool:
    """Se puede iniciar el envido: primera baza, antes de tirar la propia carta, sin cantos previos
    de envido y sin truco querido."""
    return (
        hand.baza == 0
        and not hand.has_played_in_baza(player, 0)
        and not hand.envido.calls
        and hand.truco.level == 1
    )


def _envido_raises(calls: tuple[Action, ...]) -> list[Action]:
    out: list[Action] = []
    if calls in ((), (Action.ENVIDO,)):
        out.append(Action.ENVIDO)
    if Action.REAL_ENVIDO not in calls and Action.FALTA_ENVIDO not in calls:
        out.append(Action.REAL_ENVIDO)
    if Action.FALTA_ENVIDO not in calls:
        out.append(Action.FALTA_ENVIDO)
    return out


def legal_actions(state: GameState) -> list[Action]:
    if state.phase is not Phase.PLAYING:
        return []
    hand = state.hand
    p = hand.current_player
    actions: list[Action] = []

    if hand.envido.pending:
        actions += [Action.QUIERO, Action.NO_QUIERO]
        actions += _envido_raises(hand.envido.calls)
    elif hand.truco.pending:
        actions += [Action.QUIERO, Action.NO_QUIERO]
        proposed = hand.truco.level + 1
        if proposed < 4:
            actions.append(LEVEL_TRUCO_ACTION[proposed + 1])
        if _envido_open_for(hand, p):
            actions += _envido_raises(())
    else:
        actions += [a for a in PLAY_ACTIONS if not hand.slot_used(p, int(a))]
        if _envido_open_for(hand, p):
            actions += _envido_raises(())
        if hand.truco.last_caller != p and hand.truco.level < 4:
            actions.append(LEVEL_TRUCO_ACTION[hand.truco.level + 1])
    actions.append(Action.FOLD)
    return sorted(actions)


# ---------------------------------------------------------------------------
# Transiciones
# ---------------------------------------------------------------------------


def _add_points(state: GameState, player: int, points: int) -> GameState:
    scores = list(state.scores)
    scores[player] += points
    hand_points = list(state.hand.points)
    hand_points[player] += points
    return replace(
        state,
        scores=(scores[0], scores[1]),
        hand=replace(state.hand, points=(hand_points[0], hand_points[1])),
    )


def _finish_hand(state: GameState, winner: int, truco_points: int) -> GameState:
    state = replace(state, hand=replace(state.hand, finished=True, winner=winner))
    return _add_points(state, winner, truco_points)


def _falta(state: GameState) -> int:
    return falta_envido_value(
        state.scores, state.config.target_score, state.config.falta_envido_fixed
    )


def _play_card(state: GameState, player: int, slot: int) -> GameState:
    hand = state.hand
    card = hand.hands[player][slot]
    baza = hand.baza
    current = list(hand.played[baza])
    current[player] = card
    played = (*hand.played[:baza], (current[0], current[1]))
    history = (*hand.history, PublicEvent(player, Action(slot), card))

    if current[1 - player] == NO_CARD:
        hand = replace(hand, played=played, history=history, play_turn=1 - player)
        return replace(state, hand=hand)

    cmp = compare_cards(current[0], current[1])
    result = PARDA if cmp == 0 else (0 if cmp > 0 else 1)
    results = (*hand.results, result)
    hand = replace(hand, played=played, history=history, results=results)
    winner = hand_winner(results, hand.mano)
    if winner is not None:
        return _finish_hand(replace(state, hand=hand), winner, hand.truco.level)
    leader = hand.mano if result == PARDA else result
    hand = replace(hand, played=(*played, (NO_CARD, NO_CARD)), play_turn=leader)
    return replace(state, hand=hand)


def _resolve_envido(state: GameState, accepted: bool) -> GameState:
    hand = state.hand
    env = hand.envido
    assert env.caller is not None
    falta = _falta(state)
    if accepted:
        winner = envido_winner(hand.envido_values, hand.mano)
        points = envido_accepted_points(env.calls, falta)
        values: tuple[int, int] | None = hand.envido_values
    else:
        winner = env.caller
        points = envido_rejected_points(env.calls, falta)
        values = None
    new_env = replace(
        env,
        pending=False,
        resolved=True,
        accepted=accepted,
        values=values,
        winner=winner,
        points=points,
    )
    state = replace(state, hand=replace(hand, envido=new_env))
    return _add_points(state, winner, points)


def apply(state: GameState, action: Action) -> GameState:
    """Aplica una acción legal del jugador de turno y devuelve el nuevo estado."""
    if action not in legal_actions(state):
        raise IllegalActionError(f"acción ilegal: {action!r}")
    action = Action(action)
    hand = state.hand
    p = hand.current_player

    if action in PLAY_ACTIONS:
        return _play_card(state, p, int(action))

    hand = replace(hand, history=(*hand.history, PublicEvent(p, action)))
    state = replace(state, hand=hand)

    if action in (Action.ENVIDO, Action.REAL_ENVIDO, Action.FALTA_ENVIDO):
        env = replace(hand.envido, calls=(*hand.envido.calls, action), caller=p, pending=True)
        return replace(state, hand=replace(hand, envido=env))

    if action in TRUCO_ACTION_LEVEL:
        truco = hand.truco
        # Subir estando pendiente implica querer el canto anterior.
        level = truco.level + 1 if truco.pending else truco.level
        new_truco = replace(truco, level=level, pending=True, last_caller=p)
        return replace(state, hand=replace(hand, truco=new_truco))

    if action is Action.QUIERO:
        if hand.envido.pending:
            return _resolve_envido(state, accepted=True)
        truco = replace(hand.truco, level=hand.truco.level + 1, pending=False)
        return replace(state, hand=replace(hand, truco=truco))

    if action is Action.NO_QUIERO:
        if hand.envido.pending:
            return _resolve_envido(state, accepted=False)
        caller = hand.truco.last_caller
        assert caller is not None
        return _finish_hand(state, caller, hand.truco.level)

    if action is Action.FOLD:
        rival = 1 - p
        if hand.envido.pending:
            state = _resolve_envido(state, accepted=False)
            if state.is_terminal:
                return state
            hand = state.hand
        if (
            state.config.fold_envido_bonus
            and hand.baza == 0
            and not hand.envido.calls
            and hand.truco.level == 1
        ):
            state = _add_points(state, rival, 1)
            if state.is_terminal:
                return state
        state = replace(state, hand=replace(state.hand, folded_by=p))
        return _finish_hand(state, rival, state.hand.truco.level)

    raise IllegalActionError(f"acción no soportada: {action!r}")
