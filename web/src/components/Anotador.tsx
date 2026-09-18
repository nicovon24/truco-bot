"use client";

import { useEffect, useRef } from "react";

import type { GameEvent } from "@/lib/api";
import { eventLine } from "@/lib/events";

/** Anotador de la mesa: el log de cantos y jugadas, mano por mano. */
export function Anotador({
  events,
  botName,
}: {
  events: GameEvent[];
  botName: string;
}) {
  const endRef = useRef<HTMLLIElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "nearest" });
  }, [events.length]);

  return (
    <section aria-labelledby="anotador" className="history-panel">
      <h2
        id="anotador"
        className="border-b border-tubo/20 pb-3 text-sm font-bold"
      >
        Anotador
      </h2>
      <ol className="max-h-[55dvh] overflow-y-auto py-2 text-sm leading-relaxed">
        {events.map((ev) => {
          const line = eventLine(ev, botName);
          if (!line) return null;
          const strong =
            ev.type === "hand_end" ||
            ev.type === "game_end" ||
            ev.type === "envido_result";
          return (
            <li
              key={ev.seq}
              className={`border-b border-tubo/10 py-2 ${
                ev.type === "deal"
                  ? "mt-3 text-xs font-bold uppercase tracking-wide text-sky"
                  : ""
              } ${strong ? "font-bold text-cream" : "text-tubo/85"}`}
            >
              {line}
            </li>
          );
        })}
        <li ref={endRef} aria-hidden="true" />
      </ol>
    </section>
  );
}
