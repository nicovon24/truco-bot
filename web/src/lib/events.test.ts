import { describe, expect, it } from "vitest";

import type { GameEvent } from "./api";
import { eventLine, lastBotCanto } from "./events";

function ev(partial: Partial<GameEvent>): GameEvent {
  return { seq: 0, hand_number: 0, actor: "system", type: "deal", detail: {}, ...partial };
}

describe("eventLine", () => {
  it("narra cantos citados y cartas", () => {
    expect(eventLine(ev({ actor: "bot", type: "action", label: "Quiero retruco" }), "Heurístico")).toBe(
      "Heurístico: «Quiero retruco».",
    );
    expect(
      eventLine(
        ev({
          actor: "human",
          type: "action",
          card: { id: 0, number: 1, suit: "espada", label: "1 de espada" },
        }),
        "Bot",
      ),
    ).toBe("Tirás el 1 de espada.");
  });

  it("usa voseo al repartir", () => {
    expect(eventLine(ev({ type: "deal", detail: { mano: "human" } }), "Bot")).toBe("Mano 1. Sos mano.");
  });

  it("narra el envido querido con los valores públicos", () => {
    const line = eventLine(
      ev({ type: "envido_result", detail: { accepted: true, winner: "bot", points: 2, values: { human: 25, bot: 31 } } }),
      "Bot",
    );
    expect(line).toBe("Envido: vos 25, Bot 31. Bot suma 2.");
  });
});

describe("lastBotCanto", () => {
  it("devuelve el último canto del bot en la mano y se corta con la respuesta humana", () => {
    const events = [
      ev({ type: "deal" }),
      ev({ seq: 1, actor: "bot", type: "action", label: "Truco" }),
    ];
    expect(lastBotCanto(events, 0)?.label).toBe("Truco");
    events.push(ev({ seq: 2, actor: "human", type: "action", label: "Quiero" }));
    expect(lastBotCanto(events, 0)).toBeNull();
  });
});
