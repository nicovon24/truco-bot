import { describe, expect, it } from "vitest";
import type { Card, Game, GameEvent } from "./api";
import { tableFrame } from "./table";

const a: Card = { id: 0, number: 1, suit: "espada", label: "1 de espada" };
const b: Card = { id: 1, number: 2, suit: "espada", label: "2 de espada" };
const c: Card = { id: 2, number: 3, suit: "espada", label: "3 de espada" };
const game = {
  observation: {
    bazas: [
      { human: a, bot: b, result: "human" },
      { human: null, bot: c, result: null },
      { human: null, bot: null, result: null },
    ],
  },
} as Game;
const incoming: GameEvent[] = [
  { seq: 1, hand_number: 0, actor: "human", type: "action", card: a },
  { seq: 2, hand_number: 0, actor: "bot", type: "action", card: b },
  { seq: 3, hand_number: 0, actor: "bot", type: "action", card: c },
];

describe("central table playback", () => {
  it("does not reveal a bot card or result before its event", () => {
    const frame = tableFrame(game, incoming, 1);
    expect(frame.current).toBe(0);
    expect(frame.bazas[0]).toEqual({ human: a, bot: null, result: null });
    expect(frame.bazas[1]?.bot).toBeNull();
  });
  it("keeps the completed trick visible before the next card arrives", () => {
    const frame = tableFrame(game, incoming, 2);
    expect(frame.current).toBe(0);
    expect(frame.bazas[0]?.result).toBe("human");
  });
  it("switches the center to the next trick without losing history", () => {
    const frame = tableFrame(game, incoming, 3);
    expect(frame.current).toBe(1);
    expect(frame.bazas[1]?.bot).toEqual(c);
    expect(frame.bazas[0]?.human).toEqual(a);
    expect(game.observation.bazas[0]?.result).toBe("human");
  });
  it("shows the latest played trick when there are no new card events", () => {
    expect(tableFrame(game, [], 0).current).toBe(1);
    const empty = {
      observation: { bazas: [{ human: null, bot: null, result: null }] },
    } as Game;
    expect(tableFrame(empty, [], 0).current).toBe(0);
  });
});
