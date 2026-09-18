"use client";

import { useEffect, useState } from "react";

import { Palo } from "@/components/Naipe";
import { useGame } from "@/store/game";

/** Pantalla de entrada: la cartelera de la sede con los rivales disponibles. */
export function Cartelera() {
  const { agents, agentsStatus, agentId, busy, error, loadAgents, selectAgent, newGame } = useGame();
  const [seed, setSeed] = useState("");

  useEffect(() => {
    if (agentsStatus === "idle") void loadAgents();
  }, [agentsStatus, loadAgents]);

  const seedValue = seed.trim() === "" ? undefined : Number(seed);
  const seedInvalid = seedValue !== undefined && (!Number.isInteger(seedValue) || seedValue < 0);

  return (
    <main className="pared flex min-h-dvh flex-col items-center px-4 pb-10 pt-8">
      <header className="w-full max-w-md">
        <div className="chapa relative rounded-xl px-5 py-4 text-center">
          <span className="remache absolute left-2 top-2" />
          <span className="remache absolute right-2 top-2" />
          <h1 className="text-4xl font-[900] uppercase leading-none tracking-[0.02em] [font-stretch:125%]">
            Truco Bot
          </h1>
          <p className="mt-2 text-sm font-[500] text-tubo/85">
            Sentate a la mesa. Uno contra uno, a 15.
          </p>
        </div>
        <div className="mt-3 flex justify-center gap-3" aria-hidden="true">
          {(["espada", "basto", "oro", "copa"] as const).map((s) => (
            <Palo key={s} suit={s} className="h-6 w-6" />
          ))}
        </div>
      </header>

      <section aria-labelledby="rivales" className="mt-8 w-full max-w-md">
        <h2 id="rivales" className="text-lg font-[800] uppercase tracking-[0.08em] [font-stretch:115%]">
          ¿Contra quién jugás?
        </h2>

        {agentsStatus === "loading" && <p className="mt-3 text-sm">Buscando rivales en la sede…</p>}

        {agentsStatus === "error" && (
          <div className="mt-3 rounded-lg border-2 border-chapa bg-naipe p-4 text-sm" role="alert">
            <p>{error}</p>
            <button
              type="button"
              onClick={() => void loadAgents()}
              className="mt-3 rounded-md bg-chapa px-4 py-2 font-[700] text-tubo"
            >
              Reintentar
            </button>
          </div>
        )}

        {agentsStatus === "ready" && (
          <ul className="mt-3 space-y-3" role="radiogroup" aria-labelledby="rivales">
            {agents.map((agent, i) => {
              const checked = agent.id === agentId;
              return (
                <li key={agent.id}>
                  <button
                    type="button"
                    role="radio"
                    aria-checked={checked}
                    onClick={() => selectAgent(agent.id)}
                    className={`w-full rounded-lg bg-naipe px-4 py-3 text-left shadow-[0_6px_14px_-10px_rgb(0_0_0/0.8)] transition-transform duration-200 ease-out ${
                      checked ? "ring-[3px] ring-chapa" : "ring-1 ring-black/10 hover:-translate-y-0.5"
                    }`}
                    style={{ rotate: `${i % 2 === 0 ? -0.6 : 0.5}deg` }}
                  >
                    <span className="flex items-baseline justify-between gap-3">
                      <span className="text-xl font-[800] [font-stretch:110%]">{agent.name}</span>
                      <span className="text-xs font-[600] uppercase tracking-[0.12em] text-zocalo">
                        {checked ? "Elegido" : agent.type}
                      </span>
                    </span>
                    <span className="mt-1 block text-sm leading-snug text-tinta/80">{agent.description}</span>
                    {agent.model_version && (
                      <span className="mt-1 block text-xs text-tinta/60">Modelo v{agent.model_version}</span>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </section>

      <section className="mt-8 w-full max-w-md rounded-lg bg-naipe p-4 shadow-[0_10px_20px_-14px_rgb(0_0_0/0.8)] ring-1 ring-black/10">
        <label htmlFor="semilla" className="block text-sm font-[650] text-tinta">
          Semilla (opcional, para repetir un reparto)
        </label>
        <input
          id="semilla"
          inputMode="numeric"
          value={seed}
          onChange={(e) => setSeed(e.target.value)}
          placeholder="Al azar"
          aria-invalid={seedInvalid}
          className="mt-1 w-full rounded-md bg-tubo px-3 py-2.5 text-base text-tinta ring-1 ring-black/15 placeholder:text-tinta/45"
        />
        {seedInvalid && <p className="mt-1 text-sm font-[650] text-chapa">La semilla tiene que ser un entero positivo.</p>}

        {error && agentsStatus === "ready" && (
          <p className="mt-3 rounded-md bg-naipe p-3 text-sm text-chapa" role="alert">
            {error}
          </p>
        )}

        <button
          type="button"
          disabled={!agentId || busy || seedInvalid}
          onClick={() => void newGame(seedValue)}
          className="chapa mt-4 w-full rounded-lg py-4 text-xl font-[800] uppercase tracking-[0.06em] [font-stretch:115%] transition-[filter,transform] duration-150 active:translate-y-px disabled:opacity-55 enabled:hover:brightness-110"
        >
          {busy ? "Repartiendo…" : "Repartir"}
        </button>
      </section>
    </main>
  );
}
