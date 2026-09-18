import type { Game, GameEvent } from "@/lib/api";

/** Presentation only: conceal cards until their server event has been played back. */
export function tableFrame(
  game: Game,
  incoming: GameEvent[],
  revealed: number,
) {
  const hidden = new Set(
    incoming
      .slice(revealed)
      .flatMap((event) => (event.card ? [event.card.id] : [])),
  );
  const bazas = game.observation.bazas.map((baza) => {
    const human = baza.human && !hidden.has(baza.human.id) ? baza.human : null;
    const bot = baza.bot && !hidden.has(baza.bot.id) ? baza.bot : null;
    return { human, bot, result: human && bot ? baza.result : null };
  });
  let current = 0;
  bazas.forEach((baza, index) => {
    if (baza.human || baza.bot) current = index;
  });
  return { bazas, current };
}
