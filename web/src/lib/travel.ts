/**
 * Viaje de la carta (FLIP): la mano registra de dónde sale cada carta y la baza la anima
 * desde ahí hasta su lugar. Las cartas del bot salen de sus dorsos (`#rival-mano`).
 */
const origins = new Map<number, DOMRect>();

export function markOrigin(cardId: number, el: Element): void {
  origins.set(cardId, el.getBoundingClientRect());
}

export function travelFrom(el: HTMLElement, cardId: number, fallbackId: string): void {
  if (typeof window === "undefined") return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const origin = origins.get(cardId) ?? document.getElementById(fallbackId)?.getBoundingClientRect();
  origins.delete(cardId);
  if (!origin) return;
  const target = el.getBoundingClientRect();
  const dx = origin.left + origin.width / 2 - (target.left + target.width / 2);
  const dy = origin.top + origin.height / 2 - (target.top + target.height / 2);
  const scale = origin.width / Math.max(target.width, 1);
  el.animate(
    [
      { transform: `translate(${dx}px, ${dy}px) rotate(-7deg) scale(${scale})` },
      { transform: "translate(0, 0) rotate(1.5deg) scale(1.02)", offset: 0.82 },
      { transform: "none" },
    ],
    { duration: 520, easing: "cubic-bezier(0.16, 1, 0.3, 1)" },
  );
}
