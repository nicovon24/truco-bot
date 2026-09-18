"use client";

import { useEffect, useLayoutEffect, useMemo, useRef } from "react";

import { Analisis } from "@/components/Analisis";
import { Anotador } from "@/components/Anotador";
import { Dorso, Naipe } from "@/components/Naipe";
import { Tanteador } from "@/components/Tanteador";
import type { Card, Game, LegalAction } from "@/lib/api";
import { lastBotCanto } from "@/lib/events";
import { markOrigin, travelFrom } from "@/lib/travel";
import { useGame } from "@/store/game";

const PLAY_PREFIX = "PLAY_CARD_";

function Resultado({ result }: { result: "human" | "bot" | "parda" | null | undefined }) {
  if (!result) return null;
  const text = result === "parda" ? "Parda" : result === "human" ? "Tuya" : "Del rival";
  return (
    <span
      className={`anim-globo mt-1 rounded-sm px-1.5 py-0.5 text-[0.65rem] font-[800] uppercase tracking-[0.12em] ${
        result === "human"
          ? "bg-zocalo text-tubo"
          : result === "bot"
            ? "bg-chapa text-tubo"
            : "border border-dashed border-formica-ink text-formica-ink"
      }`}
    >
      {text}
    </span>
  );
}

/** Carta en la baza: si recién se jugó, viaja desde la mano (o desde los dorsos del rival). */
function Viajera({ card, fresh, from }: { card: Card; fresh: boolean; from: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    if (fresh && ref.current) travelFrom(ref.current, card.id, from);
    // Solo al montar: una carta viaja una vez.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return (
    <div ref={ref}>
      <Naipe card={card} />
    </div>
  );
}

const HUECO =
  "block aspect-[5/8] w-[3.3rem] rounded-[10%/6%] border-2 border-dashed border-formica-ink/30 sm:w-16 lg:w-[4.6rem]";

function Bazas({ game, freshSeqs }: { game: Game; freshSeqs: Set<number> }) {
  const bazas = game.observation.bazas;
  const freshCards = new Set(
    game.events.filter((e) => freshSeqs.has(e.seq) && e.card).map((e) => e.card?.id),
  );
  return (
    <ol className="grid grid-cols-3 gap-2 sm:gap-3" aria-label="Bazas">
      {[0, 1, 2].map((i) => {
        const baza = bazas[i];
        return (
          <li key={i} className="flex flex-col items-center gap-1.5">
            <span className="text-[0.7rem] font-[800] uppercase tracking-[0.14em] text-formica-ink">
              {i + 1}ª baza
            </span>
            {baza?.bot ? (
              <Viajera key={baza.bot.id} card={baza.bot} fresh={freshCards.has(baza.bot.id)} from="rival-mano" />
            ) : (
              <span className={HUECO} />
            )}
            {baza?.human ? (
              <Viajera key={baza.human.id} card={baza.human} fresh={freshCards.has(baza.human.id)} from="mi-mano" />
            ) : (
              <span className={HUECO} />
            )}
            <Resultado result={baza?.result} />
          </li>
        );
      })}
    </ol>
  );
}

function Cantos({ actions, disabled, onPlay }: { actions: LegalAction[]; disabled: boolean; onPlay: (id: number) => void }) {
  if (actions.length === 0) return null;
  return (
    <div className="flex flex-wrap justify-center gap-2" role="group" aria-label="Cantos">
      {actions.map((a) => {
        const quiet = a.name === "FOLD";
        return (
          <button
            key={a.id}
            type="button"
            disabled={disabled}
            onClick={() => onPlay(a.id)}
            className={`min-h-11 rounded-md px-3.5 py-2 text-[0.95rem] font-[750] [font-stretch:105%] transition-[transform,filter] duration-150 active:translate-y-px disabled:opacity-50 ${
              quiet
                ? "text-tubo ring-1 ring-tubo/55 enabled:hover:bg-tubo/10"
                : "chapa enabled:hover:brightness-110"
            }`}
          >
            «{a.label}»
          </button>
        );
      })}
    </div>
  );
}

export function Mesa({ game }: { game: Game }) {
  const { agents, busy, error, fresh, analysis, play, nextHand, newGame, leave, toggleAnalysis, clearError } =
    useGame();
  const obs = game.observation;
  const botName = agents.find((a) => a.id === game.agent_id)?.name ?? "Bot";
  const freshSeqs = useMemo(() => new Set(fresh.map((e) => e.seq)), [fresh]);

  const plays = new Map<number, LegalAction>();
  const cantos: LegalAction[] = [];
  for (const a of game.legal_actions) {
    if (a.name.startsWith(PLAY_PREFIX)) plays.set(Number(a.name.slice(PLAY_PREFIX.length)), a);
    else cantos.push(a);
  }

  const bubble = lastBotCanto(game.events, obs.hand_number);
  const myTurn = obs.turn === "human" && game.status === "playing";
  const statusRef = useRef<HTMLParagraphElement>(null);

  useEffect(() => {
    if (game.status !== "playing") statusRef.current?.focus();
  }, [game.status]);

  return (
    <div className="pared min-h-dvh">
      <div className="mx-auto grid max-w-[88rem] gap-4 px-3 pb-6 pt-3 sm:px-5 lg:grid-cols-[17rem_minmax(0,1fr)_19rem] lg:gap-6 lg:pt-4">
        <aside className="order-3 lg:order-1">
          <Anotador events={game.events} botName={botName} />
        </aside>

        <main className="order-1 flex flex-col gap-3 lg:order-2 lg:gap-2.5">
          <div className="flex items-center justify-between gap-2">
            <button
              type="button"
              onClick={leave}
              className="rounded-md px-2 py-1.5 text-sm font-[650] text-zocalo underline decoration-2 underline-offset-4 hover:text-chapa"
            >
              Levantarse
            </button>
            <span className="text-xs font-[600] text-tinta/80">Semilla {game.seed}</span>
            <button
              type="button"
              aria-pressed={analysis}
              onClick={toggleAnalysis}
              className={`rounded-md px-2.5 py-1.5 text-sm font-[700] ring-1 transition-colors ${
                analysis ? "bg-zocalo text-tubo ring-zocalo" : "text-zocalo ring-zocalo/50 hover:bg-zocalo/10"
              }`}
            >
              Análisis {analysis ? "prendido" : "apagado"}
            </button>
          </div>

          <Tanteador
            human={game.scores.human ?? 0}
            bot={game.scores.bot ?? 0}
            target={game.target_score}
            botName={botName}
            handNumber={obs.hand_number}
          />

          {/* Rival: dorsos chicos y su último canto al lado */}
          <section
            aria-label={`${botName}: ${obs.bot_cards_in_hand} cartas en la mano`}
            className="flex min-h-12 items-center justify-center gap-3"
          >
            <div id="rival-mano" className="flex shrink-0 -space-x-3">
              {Array.from({ length: obs.bot_cards_in_hand }, (_, i) => (
                <Dorso key={i} size="dorso" className={i === 0 ? "-rotate-6" : i === 2 ? "rotate-6" : ""} />
              ))}
            </div>
            <div aria-live="polite">
              {bubble ? (
                <p
                  key={bubble.seq}
                  className="anim-globo rounded-2xl rounded-bl-sm bg-naipe px-3.5 py-1.5 text-base font-[750] shadow-[0_6px_12px_-8px_rgb(0_0_0/0.7)] ring-1 ring-black/10"
                >
                  «{bubble.label}»
                </p>
              ) : obs.turn === "bot" ? (
                <p className="text-sm font-[600] text-tinta/80">{botName} está pensando…</p>
              ) : null}
            </div>
          </section>

          {/* Fórmica */}
          <section className="formica px-3 py-3 sm:px-6 sm:py-4" aria-label="Mesa">
            <Bazas game={game} freshSeqs={freshSeqs} />
            <div className="mt-3 flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-xs font-[650] text-formica-ink">
              <span>
                {obs.mano === "human" ? "Sos mano" : `Es mano ${botName}`}
              </span>
              <span aria-hidden="true">·</span>
              <span>
                Truco: {obs.truco.level === 1 ? "sin cantar" : `vale ${obs.truco.level}`}
                {obs.truco.pending ? " (pendiente)" : ""}
              </span>
              <span aria-hidden="true">·</span>
              <span>Tu envido: {obs.envido.human_value}</span>
              {obs.envido.bot_value != null && (
                <>
                  <span aria-hidden="true">·</span>
                  <span>
                    {botName}: {obs.envido.bot_value}
                  </span>
                </>
              )}
            </div>
          </section>

          {/* Estado y acciones */}
          <section aria-label="Tu turno" className="flex flex-col items-center gap-2.5 rounded-xl bg-zocalo px-3 pb-3 pt-2.5">
            <p
              ref={statusRef}
              tabIndex={-1}
              className="text-center text-base font-[750] text-tubo outline-none"
              aria-live="polite"
            >
              {game.status === "game_over"
                ? game.winner === "human"
                  ? "¡Ganaste la partida!"
                  : `${botName} ganó la partida.`
                : game.status === "hand_over"
                  ? obs.hand_winner === "human"
                    ? `Mano tuya: +${obs.hand_points.human ?? 0}.`
                    : `Mano de ${botName}: +${obs.hand_points.bot ?? 0}.`
                  : myTurn
                    ? "Te toca."
                    : `Juega ${botName}…`}
            </p>

            {game.status === "playing" && <Cantos actions={cantos} disabled={busy || !myTurn} onPlay={(id) => void play(id)} />}

            {game.status === "hand_over" && (
              <button
                type="button"
                disabled={busy}
                onClick={() => void nextHand()}
                className="chapa min-h-12 rounded-lg px-6 text-lg font-[800] uppercase tracking-[0.06em] [font-stretch:115%] enabled:hover:brightness-110 disabled:opacity-55"
              >
                Repartir la siguiente
              </button>
            )}

            {game.status === "game_over" && (
              <div className="flex flex-wrap justify-center gap-2">
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => void newGame()}
                  className="chapa min-h-12 rounded-lg px-6 text-lg font-[800] uppercase tracking-[0.06em] [font-stretch:115%] enabled:hover:brightness-110"
                >
                  Otra partida
                </button>
                <button type="button" onClick={leave} className="min-h-12 rounded-lg px-4 font-[700] text-tubo underline underline-offset-4">
                  Cambiar de rival
                </button>
              </div>
            )}

            {/* Mano propia */}
            <div id="mi-mano" className="flex items-end justify-center gap-2 pt-1 sm:gap-3" role="group" aria-label="Tus cartas">
              {obs.my_cards.map(({ slot, card }) => {
                if (!card) {
                  return <span key={slot} className="block aspect-[5/8] w-[4.9rem] sm:w-24" aria-hidden="true" />;
                }
                const action = plays.get(slot);
                const playable = Boolean(action) && myTurn && !busy;
                return (
                  <button
                    key={slot}
                    type="button"
                    disabled={!playable}
                    onClick={(e) => {
                      if (!action) return;
                      markOrigin(card.id, e.currentTarget);
                      void play(action.id);
                    }}
                    aria-label={action ? action.label : card.label}
                    className={`rounded-[10%/6%] transition-transform duration-200 ease-out ${
                      playable ? "hover:-translate-y-2 focus-visible:-translate-y-2" : "cursor-default"
                    }`}
                    style={{ rotate: `${(slot - 1) * 4}deg` }}
                  >
                    <Naipe card={card} size="mano" className={playable ? "" : "opacity-95"} />
                  </button>
                );
              })}
            </div>
          </section>

          {error && (
            <div className="flex items-start justify-between gap-3 rounded-lg bg-naipe p-3 text-sm text-chapa ring-2 ring-chapa" role="alert">
              <p>{error}</p>
              <button type="button" onClick={clearError} className="font-[700] underline">
                Cerrar
              </button>
            </div>
          )}
        </main>

        <aside className={`order-2 lg:order-3 ${analysis ? "" : "hidden lg:block"}`}>
          <Analisis events={game.events} botName={botName} enabled={analysis} onToggle={toggleAnalysis} />
        </aside>
      </div>
    </div>
  );
}
