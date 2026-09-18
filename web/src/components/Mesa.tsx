"use client";

import {
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
} from "react";
import { Analisis } from "@/components/Analisis";
import { Anotador } from "@/components/Anotador";
import { Icon } from "@/components/Icon";
import { Dorso, Naipe } from "@/components/Naipe";
import { Overlay, Rules } from "@/components/Overlay";
import { Tanteador } from "@/components/Tanteador";
import type { Card, Game, LegalAction } from "@/lib/api";
import { lastBotCanto } from "@/lib/events";
import { tableFrame } from "@/lib/table";
import { markOrigin, travelFrom } from "@/lib/travel";
import { useGame } from "@/store/game";

function Viajera({ card, from }: { card: Card; from: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    if (ref.current) travelFrom(ref.current, card.id, from);
  }, [card.id, from]);
  return (
    <div ref={ref}>
      <Naipe card={card} size="baza" />
    </div>
  );
}

function Cantos({
  actions,
  disabled,
  onPlay,
}: {
  actions: LegalAction[];
  disabled: boolean;
  onPlay: (id: number) => void;
}) {
  return (
    <div className="cantos" role="group" aria-label="Cantos disponibles">
      {actions.map((a) => (
        <button
          key={a.id}
          type="button"
          disabled={disabled}
          onClick={() => onPlay(a.id)}
          className={`canto-button ${a.name === "FOLD" || a.name.includes("REJECT") ? "canto-quiet" : a.name.includes("ENVIDO") ? "canto-envido" : ""}`}
        >
          {a.label}
        </button>
      ))}
    </div>
  );
}

export function Mesa({ game }: { game: Game }) {
  const {
    agents,
    busy,
    error,
    fresh,
    analysis,
    play,
    nextHand,
    newGame,
    leave,
    toggleAnalysis,
    clearError,
  } = useGame();
  const [panel, setPanel] = useState<"history" | "rules" | "leave" | null>(
    null,
  );
  const obs = game.observation;
  const botName = agents.find((a) => a.id === game.agent_id)?.name ?? "Bot";
  const incoming = useMemo(
    () => fresh.filter((e) => e.card && e.hand_number === obs.hand_number),
    [fresh, obs.hand_number],
  );
  const sequenceKey = `${game.id}:${obs.hand_number}:${incoming.map((e) => e.seq).join(",")}`;
  const [playback, setPlayback] = useState({ key: "", revealed: 0 });
  const revealed = playback.key === sequenceKey ? playback.revealed : 0;
  const animating = revealed < incoming.length;

  useEffect(() => {
    if (!incoming.length) return;
    const reduced = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;
    const timers = incoming.map((_, index) =>
      window.setTimeout(
        () => setPlayback({ key: sequenceKey, revealed: index + 1 }),
        reduced ? 0 : 120 + index * 650,
      ),
    );
    return () => timers.forEach(window.clearTimeout);
  }, [sequenceKey, incoming]);

  const { bazas, current } = tableFrame(game, incoming, revealed);
  const baza = bazas[current];
  const plays = new Map<number, LegalAction>();
  const cantos: LegalAction[] = [];
  game.legal_actions.forEach((a) => {
    if (a.name.startsWith("PLAY_CARD_")) plays.set(Number(a.name.slice(10)), a);
    else cantos.push(a);
  });
  const bubble = lastBotCanto(game.events, obs.hand_number);
  const myTurn = obs.turn === "human" && game.status === "playing";
  const locked = busy || animating;
  const statusRef = useRef<HTMLParagraphElement>(null);
  useEffect(() => {
    if (game.status !== "playing" && !animating) statusRef.current?.focus();
  }, [game.status, animating]);
  const resultText =
    baza?.result === "human"
      ? "La baza es tuya"
      : baza?.result === "bot"
        ? "Baza del rival"
        : baza?.result === "parda"
          ? "Parda"
          : "";
  const status = animating
    ? "Cartas sobre la mesa…"
    : busy
      ? "Un segundo…"
      : game.status === "game_over"
        ? game.winner === "human"
          ? "¡La partida es tuya!"
          : `Ganó ${botName}`
        : game.status === "hand_over"
          ? obs.hand_winner === "human"
            ? `¡Mano tuya! +${obs.hand_points.human ?? 0}`
            : `Mano del rival. +${obs.hand_points.bot ?? 0}`
          : myTurn
            ? obs.truco.pending || obs.envido.pending
              ? "Hay un canto. ¿Qué decís?"
              : "Te toca. Jugá tu carta."
            : `Juega ${botName}…`;

  return (
    <div className="arena game-arena">
      <header className="app-header game-header">
        <button
          type="button"
          className="utility-button"
          onClick={() => setPanel("leave")}
        >
          <Icon name="back" />
          <span>Salir</span>
        </button>
        <span className="wordmark">
          <Icon name="cards" />
          <span>TRUCO BOT</span>
        </span>
        <button
          type="button"
          className="icon-button"
          onClick={() => setPanel("rules")}
          aria-label="Cómo se juega"
        >
          <Icon name="book" />
        </button>
      </header>
      <main className="game-layout">
        <Tanteador
          human={game.scores.human ?? 0}
          bot={game.scores.bot ?? 0}
          target={game.target_score}
          botName={botName}
          handNumber={obs.hand_number}
        />
        <section className="table-scene" aria-label="Mesa de truco">
          <div className="table-surface" aria-hidden="true">
            <div className="table-mark">
              TRUCO BOT<span>ARGENTINO DE LEY</span>
            </div>
          </div>
          <div className="opponent-seat">
            <div className="avatar">
              <Icon name="user" />
            </div>
            <span className="player-name">
              {botName}
              <small>{obs.mano === "bot" ? "Es mano" : "Tu rival"}</small>
            </span>
            <div
              id="rival-mano"
              className="opponent-hand"
              aria-label={`${obs.bot_cards_in_hand} cartas del rival`}
            >
              {Array.from({ length: obs.bot_cards_in_hand }, (_, i) => (
                <Dorso
                  key={i}
                  size="dorso"
                  className={`opponent-card opponent-card-${i}`}
                />
              ))}
            </div>
            {bubble && (
              <p key={bubble.seq} className="speech-bubble anim-globo">
                «{bubble.label}»
              </p>
            )}
          </div>
          <div className="baza-tracker" aria-label="Resultado de las bazas">
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className={`baza-dot ${i === current ? "is-current" : ""} ${bazas[i]?.result ? `won-${bazas[i].result}` : ""}`}
                aria-label={`Baza ${i + 1}: ${bazas[i]?.result === "human" ? "tuya" : bazas[i]?.result === "bot" ? "del rival" : bazas[i]?.result === "parda" ? "parda" : "sin resolver"}`}
              >
                {bazas[i]?.result === "human" ? <Icon name="check" /> : i + 1}
              </span>
            ))}
          </div>
          <div
            className="central-baza"
            aria-label={`Baza actual: ${current + 1}`}
          >
            {baza?.bot || baza?.human ? (
              <>
                <div className="played-card played-bot">
                  {baza.bot && (
                    <Viajera
                      key={`${obs.hand_number}-${baza.bot.id}`}
                      card={baza.bot}
                      from="rival-mano"
                    />
                  )}
                </div>
                <div className="played-card played-human">
                  {baza.human && (
                    <Viajera
                      key={`${obs.hand_number}-${baza.human.id}`}
                      card={baza.human}
                      from="mi-mano"
                    />
                  )}
                </div>
              </>
            ) : (
              <p className="table-invitation">
                La mesa está servida.
                <span>
                  {obs.mano === "human"
                    ? "Vos abrís la mano."
                    : "A ver qué trae el rival."}
                </span>
              </p>
            )}
            {resultText && (
              <span
                key={`${current}-${resultText}`}
                className={`baza-result anim-globo ${baza?.result === "human" ? "is-yours" : ""}`}
              >
                {resultText}
              </span>
            )}
          </div>
          <div className="table-details">
            <span>Mano {obs.hand_number + 1}</span>
            <span>
              {obs.truco.level === 1 ? "Sin truco" : `Vale ${obs.truco.level}`}
              {obs.truco.pending ? " · a responder" : ""}
            </span>
          </div>
          <div className="player-seat">
            <div className="hand-meta">
              <span>VOS {obs.mano === "human" && <small>MANO</small>}</span>
              <span>
                Envido <strong>{obs.envido.human_value}</strong>
                {obs.envido.bot_value != null && (
                  <small> · Rival {obs.envido.bot_value}</small>
                )}
              </span>
            </div>
            <div
              id="mi-mano"
              className="player-hand"
              role="group"
              aria-label="Tus cartas"
            >
              {obs.my_cards.map(
                ({ slot, card }) =>
                  card && (
                    <button
                      key={`${obs.hand_number}-${slot}`}
                      type="button"
                      disabled={!plays.has(slot) || !myTurn || locked}
                      aria-label={plays.get(slot)?.label ?? card.label}
                      onClick={(e) => {
                        const action = plays.get(slot);
                        if (!action) return;
                        markOrigin(card.id, e.currentTarget);
                        void play(action.id);
                      }}
                      className="hand-card"
                      style={
                        {
                          "--card-angle": `${(slot - 1) * 9}deg`,
                          "--deal-delay": `${slot * 90}ms`,
                        } as CSSProperties
                      }
                    >
                      <Naipe card={card} size="mano" />
                    </button>
                  ),
              )}
            </div>
          </div>
        </section>
        <section className="action-dock" aria-label="Tu turno">
          <p
            ref={statusRef}
            tabIndex={-1}
            className={`turn-status ${myTurn && !locked ? "your-turn" : ""}`}
            aria-live="polite"
          >
            <span aria-hidden="true" />
            {status}
          </p>
          {game.status === "playing" && (
            <Cantos
              actions={cantos}
              disabled={locked || !myTurn}
              onPlay={(id) => void play(id)}
            />
          )}
          {game.status === "hand_over" && (
            <button
              type="button"
              className="primary-button next-button"
              disabled={locked}
              onClick={() => void nextHand()}
            >
              Repartir la siguiente <Icon name="arrow" />
            </button>
          )}
          {game.status === "game_over" && (
            <div className="end-actions">
              <button
                type="button"
                className="primary-button next-button"
                disabled={locked}
                onClick={() => void newGame()}
              >
                Otra partida <Icon name="arrow" />
              </button>
              <button type="button" className="utility-button" onClick={leave}>
                Cambiar de rival
              </button>
            </div>
          )}
          {error && (
            <div role="alert" className="error-message">
              <p>{error}</p>
              <button type="button" onClick={clearError}>
                Cerrar
              </button>
            </div>
          )}
        </section>
      </main>
      <footer className="game-footer">
        <span className="game-seed">Semilla {game.seed}</span>
        <div>
          <button
            type="button"
            className="utility-button"
            onClick={() => setPanel("history")}
          >
            <Icon name="history" />
            <span>Historial</span>
          </button>
          <button
            type="button"
            className="utility-button"
            aria-pressed={analysis}
            onClick={toggleAnalysis}
          >
            <Icon name="chart" />
            <span>Análisis</span>
          </button>
        </div>
        <span className="argentina-mark">
          <i /> A {game.target_score} puntos
        </span>
      </footer>
      {panel === "history" && (
        <Overlay title="Así viene la partida" onClose={() => setPanel(null)}>
          <Anotador events={game.events} botName={botName} />
        </Overlay>
      )}
      {analysis && (
        <Overlay title="Dentro de la cabeza del bot" onClose={toggleAnalysis}>
          <Analisis
            events={game.events}
            botName={botName}
            enabled={analysis}
            onToggle={toggleAnalysis}
          />
        </Overlay>
      )}
      {panel === "rules" && <Rules onClose={() => setPanel(null)} />}
      {panel === "leave" && (
        <Overlay
          title="¿Te levantás de la mesa?"
          onClose={() => setPanel(null)}
        >
          <p className="leave-copy">
            Vas a volver al inicio. Esta partida no se podrá retomar desde la
            mesa.
          </p>
          <div className="leave-actions">
            <button
              type="button"
              className="primary-button"
              onClick={() => setPanel(null)}
            >
              Seguir jugando
            </button>
            <button type="button" className="utility-button" onClick={leave}>
              Salir de la partida
            </button>
          </div>
        </Overlay>
      )}
    </div>
  );
}
