"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Icon } from "@/components/Icon";
import { Naipe, Dorso } from "@/components/Naipe";
import { Rules } from "@/components/Overlay";
import { useGame } from "@/store/game";

function technicalLabel(type: string): string {
  if (type === "random") return "Por dentro: decisiones aleatorias.";
  if (type === "heuristic")
    return "Por dentro: reglas programadas (heurísticas).";
  if (type === "tabular")
    return "Por dentro: CFR tabular entrenado sin envido.";
  if (type === "neural") return "Por dentro: una red neuronal entrenada.";
  return `Por dentro: modelo ${type}.`;
}

export function Cartelera() {
  const {
    agents,
    agentsStatus,
    agentId,
    targetScore,
    busy,
    error,
    loadAgents,
    selectAgent,
    selectTargetScore,
    newGame,
  } = useGame();
  const [seed, setSeed] = useState("");
  const [rules, setRules] = useState(false);
  useEffect(() => {
    if (agentsStatus === "idle") void loadAgents();
  }, [agentsStatus, loadAgents]);
  const seedValue = seed.trim() === "" ? undefined : Number(seed);
  const seedInvalid =
    seedValue !== undefined &&
    (!Number.isSafeInteger(seedValue) || seedValue < 0);
  const selected = agents.find((a) => a.id === agentId);

  return (
    <main className="arena lobby">
      <header className="app-header">
        <Link href="/" className="wordmark" aria-label="Truco Bot, inicio">
          <Icon name="cards" />
          <span>TRUCO BOT</span>
        </Link>
        <button
          type="button"
          className="utility-button"
          onClick={() => setRules(true)}
        >
          <Icon name="book" />
          <span>Cómo se juega</span>
        </button>
      </header>
      <div className="lobby-content">
        <div className="lobby-emblem" aria-hidden="true">
          <span />
          <Icon name="star" />
          <Icon name="star" />
          <Icon name="star" />
          <span />
        </div>
        <h1 className="lobby-title">
          TRUCO<span>DE UNA.</span>
        </h1>
        <p className="lobby-intro">El de siempre. Un rival que no se cansa.</p>
        <div className="lobby-cards" aria-hidden="true">
          <Dorso size="hero" className="hero-back" />
          <Naipe
            size="hero"
            card={{ id: 0, number: 1, suit: "espada", label: "1 de espada" }}
            className="hero-front"
          />
        </div>
        <section className="match-setup" aria-label="Preparar partida">
          <div className="opponent-heading">
            <label htmlFor="rival">Elegí tu rival</label>
            <span>1 vs. 1 · Tres niveles</span>
          </div>
          <div className="opponent-select">
            <Icon name="user" />
            <select
              id="rival"
              value={agentId ?? ""}
              disabled={agentsStatus !== "ready" || busy}
              onChange={(e) => selectAgent(e.target.value)}
            >
              {agentsStatus !== "ready" && (
                <option value="">
                  {agentsStatus === "error"
                    ? "Sin conexión"
                    : "Buscando rivales…"}
                </option>
              )}
              {agentsStatus === "ready" && agents.length === 0 && (
                <option value="">No hay rivales disponibles</option>
              )}
              {agents.map((agent) => (
                <option key={agent.id} value={agent.id}>
                  {agent.name}
                </option>
              ))}
            </select>
            <Icon name="chevron" />
          </div>
          {selected && (
            <div className="opponent-description" aria-live="polite">
              <p>{selected.description}</p>
              <span>{technicalLabel(selected.type)}</span>
            </div>
          )}
          <fieldset className="score-choice">
            <legend>¿A cuántos puntos?</legend>
            <div>
              {([15, 30] as const).map((score) => (
                <label key={score}>
                  <input
                    type="radio"
                    name="target-score"
                    value={score}
                    checked={targetScore === score}
                    onChange={() => selectTargetScore(score)}
                    disabled={busy}
                  />
                  <span>
                    <strong>{score} puntos</strong>
                    <small>{score === 15 ? "Partida rápida" : "Partida completa"}</small>
                  </span>
                </label>
              ))}
            </div>
          </fieldset>
          {error && (
            <div className="error-message" role="alert">
              <p>{error}</p>
              {agentsStatus === "error" && (
                <button type="button" onClick={() => void loadAgents()}>
                  Reintentar conexión
                </button>
              )}
            </div>
          )}
          <button
            type="button"
            className="primary-button play-button"
            disabled={
              !agentId || busy || seedInvalid || agentsStatus !== "ready"
            }
            onClick={() => void newGame(seedValue)}
          >
            <Icon name="cards" />
            {busy ? "Repartiendo…" : `Jugar a ${targetScore}`}
            <Icon name="arrow" />
          </button>
          <details className="seed-settings">
            <summary>
              Personalizar reparto <Icon name="chevron" />
            </summary>
            <div>
              <label htmlFor="semilla">Semilla opcional</label>
              <input
                id="semilla"
                inputMode="numeric"
                placeholder="Al azar"
                value={seed}
                onChange={(e) => setSeed(e.target.value)}
                aria-invalid={seedInvalid}
                aria-describedby="seed-help"
                disabled={busy}
              />
              <p id="seed-help">
                {seedInvalid
                  ? "Usá un número entero mayor o igual a cero."
                  : "Misma semilla y mismo rival para repetir el comienzo."}
              </p>
            </div>
          </details>
        </section>
        <p className="lobby-note">
          Sin registro. Con envido, truco y un poco de farol.
        </p>
      </div>
      <footer className="lobby-footer">
        <span>Hecho para cantar fuerte.</span>
        <span className="argentina-mark">
          <i /> Truco argentino
        </span>
      </footer>
      {rules && <Rules onClose={() => setRules(false)} />}
    </main>
  );
}
