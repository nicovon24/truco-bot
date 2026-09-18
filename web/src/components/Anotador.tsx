"use client";

import { useEffect, useRef } from "react";

import type { GameEvent } from "@/lib/api";
import { eventLine } from "@/lib/events";

/** Anotador de la mesa: el log de cantos y jugadas, mano por mano. */
export function Anotador({ events, botName }: { events: GameEvent[]; botName: string }) {
  const endRef = useRef<HTMLLIElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "nearest" });
  }, [events.length]);

  return (
    <section
      aria-labelledby="anotador"
      className="rounded-xl bg-naipe shadow-[0_10px_20px_-14px_rgb(0_0_0/0.8)] ring-1 ring-black/10"
    >
      <h2
        id="anotador"
        className="border-b-2 border-chapa/80 px-4 pb-2 pt-3 text-sm font-[850] uppercase tracking-[0.14em] [font-stretch:120%]"
      >
        Anotador
      </h2>
      <ol className="max-h-[22rem] overflow-y-auto px-4 py-2 text-sm leading-relaxed lg:max-h-[calc(100dvh-8rem)]">
        {events.map((ev) => {
          const line = eventLine(ev, botName);
          if (!line) return null;
          const strong = ev.type === "hand_end" || ev.type === "game_end" || ev.type === "envido_result";
          return (
            <li
              key={ev.seq}
              className={`border-b border-dotted border-tinta/15 py-1 ${
                ev.type === "deal" ? "mt-2 text-xs font-[750] uppercase tracking-[0.1em] text-zocalo" : ""
              } ${strong ? "font-[700] text-chapa" : ""}`}
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
