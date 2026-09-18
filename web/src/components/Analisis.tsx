"use client";

import type { GameEvent } from "@/lib/api";

/** Modo análisis: cada decisión del bot como un instrumento, con la probabilidad de cada acción. */
export function Analisis({
  events,
  botName,
  enabled,
  onToggle,
}: {
  events: GameEvent[];
  botName: string;
  enabled: boolean;
  onToggle: () => void;
}) {
  const decisions = events
    .filter((e) => e.actor === "bot" && e.type === "action" && e.policy)
    .reverse();

  return (
    <section aria-labelledby="analisis" className="text-tubo">
      <div className="flex items-center justify-between gap-2 border-b border-tubo/15 px-4 pb-2 pt-3">
        <h2
          id="analisis"
          className="text-sm font-[850] uppercase tracking-[0.14em] [font-stretch:120%]"
        >
          Cómo decide {botName}
        </h2>
        <button
          type="button"
          onClick={onToggle}
          aria-pressed={enabled}
          className="min-h-11 rounded px-3 py-2 text-xs font-[700] ring-1 ring-tubo/40 hover:bg-tubo/10"
        >
          {enabled ? "Ocultar" : "Mostrar"}
        </button>
      </div>

      {!enabled ? (
        <p className="px-4 py-4 text-sm leading-relaxed text-tubo/80">
          Prendé el análisis para ver las probabilidades que usó el bot en cada
          decisión. Elige sorteando con esas probabilidades, no siempre la más
          alta.
        </p>
      ) : decisions.length === 0 ? (
        <p className="px-4 py-4 text-sm text-tubo/80">
          Todavía no decidió nada en esta partida.
        </p>
      ) : (
        <ol className="max-h-[55dvh] space-y-4 overflow-y-auto py-3">
          {decisions.map((ev) => {
            const entries = ev.policy ?? [];
            return (
              <li key={ev.seq}>
                <p className="text-xs font-[650] text-tubo/70">
                  Mano {ev.hand_number + 1} · eligió{" "}
                  <span className="font-[800] text-tubo">
                    {ev.card ? ev.card.label : `«${ev.label ?? ""}»`}
                  </span>
                </p>
                <ul className="mt-1.5 space-y-1">
                  {entries.map(({ name, label, probability: p }) => {
                    const chosen = name === ev.action_name;
                    const pct = Math.round(p * 1000) / 10;
                    return (
                      <li
                        key={name}
                        className="grid grid-cols-[minmax(0,1fr)_minmax(25px,1fr)_3rem] items-center gap-2 text-xs"
                      >
                        <span
                          className={chosen ? "font-[800]" : "text-tubo/85"}
                        >
                          {chosen && <span className="sr-only">Elegida: </span>}
                          {label}
                        </span>
                        <span
                          className="relative h-2.5 overflow-hidden rounded-sm bg-tubo/10"
                          aria-hidden="true"
                        >
                          <span
                            className={`absolute inset-y-0 left-0 rounded-sm ${chosen ? "bg-formica" : "bg-tubo/45"}`}
                            style={{
                              width: `${Math.max(p * 100, p > 0 ? 1.5 : 0)}%`,
                            }}
                          />
                        </span>
                        <span
                          className={`text-right tabular-nums ${chosen ? "font-[800] text-formica" : "text-tubo/85"}`}
                        >
                          {pct}%
                        </span>
                      </li>
                    );
                  })}
                </ul>
              </li>
            );
          })}
        </ol>
      )}
    </section>
  );
}
