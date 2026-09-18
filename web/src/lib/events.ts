import type { GameEvent } from "./api";

/** Texto de presentación: no deduce reglas, solo narra los eventos que manda la API. */

type Detail = Record<string, unknown>;

function who(actor: unknown, botName: string): string {
  return actor === "human" ? "Vos" : botName;
}

function num(v: unknown): number {
  return typeof v === "number" ? v : 0;
}

export function eventLine(ev: GameEvent, botName: string): string | null {
  const d = (ev.detail ?? {}) as Detail;
  switch (ev.type) {
    case "deal":
      return d.mano === "human"
        ? `Mano ${ev.hand_number + 1}. Sos mano.`
        : `Mano ${ev.hand_number + 1}. Es mano ${botName}.`;
    case "action":
      if (ev.card) {
        return ev.actor === "human" ? `Tirás el ${ev.card.label}.` : `${botName} tira el ${ev.card.label}.`;
      }
      return `${who(ev.actor, botName)}: «${ev.label ?? ev.action_name ?? ""}».`;
    case "envido_result": {
      const values = d.values as { human?: number; bot?: number } | undefined;
      const suma = d.winner === "human" ? `Sumás ${num(d.points)}` : `${botName} suma ${num(d.points)}`;
      if (d.accepted && values) {
        return `Envido: vos ${values.human ?? "?"}, ${botName} ${values.bot ?? "?"}. ${suma}.`;
      }
      return `Envido no querido. ${suma}.`;
    }
    case "hand_end": {
      const points = d.points as { human?: number; bot?: number } | undefined;
      const gana = d.winner === "human" ? "Ganás la mano" : `${botName} gana la mano`;
      const folded =
        d.folded_by === "human" ? " (te fuiste al mazo)" : d.folded_by ? ` (${botName} se fue al mazo)` : "";
      return `${gana}${folded}. Vos +${points?.human ?? 0}, ${botName} +${points?.bot ?? 0}.`;
    }
    case "game_end":
      return d.winner === "human" ? "¡Ganaste la partida!" : `${botName} ganó la partida.`;
    default:
      return null;
  }
}

/** Último canto (no carta) del bot en la mano en curso, para el globo sobre sus cartas. */
export function lastBotCanto(events: GameEvent[], handNumber: number): GameEvent | null {
  for (let i = events.length - 1; i >= 0; i--) {
    const ev = events[i];
    if (!ev || ev.hand_number !== handNumber) break;
    if (ev.actor === "bot" && ev.type === "action" && !ev.card) return ev;
    if (ev.actor === "human" && ev.type === "action" && !ev.card) return null;
  }
  return null;
}
