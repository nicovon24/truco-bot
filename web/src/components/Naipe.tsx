import type { Card } from "@/lib/api";

type Suit = Card["suit"];

const SUIT_COLOR: Record<Suit, string> = {
  espada: "var(--color-espada)",
  basto: "var(--color-basto)",
  oro: "var(--color-oro)",
  copa: "var(--color-copa)",
};

/** Palos del naipe español dibujados a mano, en un viewBox de 40×40. */
export function Palo({ suit, className }: { suit: Suit; className?: string }) {
  const color = SUIT_COLOR[suit];
  return (
    <svg viewBox="0 0 40 40" className={className} aria-hidden="true" focusable="false">
      {suit === "oro" && (
        <g>
          <circle cx="20" cy="20" r="15" fill={color} />
          <circle cx="20" cy="20" r="11.5" fill="none" stroke="#fff6d8" strokeWidth="1.4" />
          <circle cx="20" cy="20" r="5" fill="#fff6d8" opacity="0.85" />
          {Array.from({ length: 8 }, (_, i) => {
            const a = (i * Math.PI) / 4;
            return (
              <circle
                key={i}
                cx={20 + Math.cos(a) * 8.3}
                cy={20 + Math.sin(a) * 8.3}
                r="1.1"
                fill="#fff6d8"
              />
            );
          })}
        </g>
      )}
      {suit === "copa" && (
        <g fill={color}>
          <path d="M9 7h22c0 8.5-4.6 14.3-9.3 15.6V29h4.6v2.6H13.7V29h4.6v-6.4C13.6 21.3 9 15.5 9 7Z" />
          <rect x="11.5" y="32.6" width="17" height="2.6" rx="1.3" />
          <path d="M12.4 10h15.2c-.6 4.4-3.3 8-7.6 8.4-4.3-.4-7-4-7.6-8.4Z" fill="#ffd9d4" opacity="0.55" />
        </g>
      )}
      {suit === "espada" && (
        <g fill={color}>
          <path d="M20 3.5 22.4 8v17.5h-4.8V8Z" />
          <rect x="12" y="25.2" width="16" height="3" rx="1.5" />
          <rect x="18.4" y="28" width="3.2" height="6.4" rx="1" />
          <circle cx="20" cy="36" r="2.2" />
          <path d="M20 8.5v15.5" stroke="#dbe7f7" strokeWidth="0.9" />
        </g>
      )}
      {suit === "basto" && (
        <g>
          <path
            d="M14.4 35.5 11.7 33c3.8-7 8.2-15 12.2-24.4 1.4-3.2 6.3-3.7 7.7-.3 1.2 2.9-.4 5.3-2.6 6.3C24 21.8 19.7 28.6 14.4 35.5Z"
            fill={color}
          />
          <circle cx="25.4" cy="14.4" r="1.6" fill="#d9ecc9" />
          <circle cx="21.3" cy="21.2" r="1.3" fill="#d9ecc9" />
          <circle cx="17.4" cy="27.6" r="1.1" fill="#d9ecc9" />
          <path d="M26.8 7.6c1.6-.3 2.8.4 3.2 1.6" stroke="#d9ecc9" strokeWidth="1" fill="none" />
        </g>
      )}
    </svg>
  );
}

const SIZES = {
  mano: "w-[4.9rem] sm:w-24",
  baza: "w-[3.3rem] sm:w-16 lg:w-[4.6rem]",
  dorso: "w-9 sm:w-11",
} as const;

/** Cortes de la pinta: interrupciones del marco que dicen el palo (oro 0, copa 1, espada 2, basto 3). */
const CORTES: Record<Suit, number> = { oro: 0, copa: 1, espada: 2, basto: 3 };

function Marco({ suit }: { suit: Suit }) {
  const n = CORTES[suit];
  const gaps = Array.from({ length: n }, (_, i) => 50 + (i - (n - 1) / 2) * 13);
  return (
    <span className="pointer-events-none absolute inset-[7%] rounded-[6%/4%] border" style={{ borderColor: SUIT_COLOR[suit] }} aria-hidden="true">
      {gaps.map((left) => (
        <span key={`t${left}`} className="absolute -top-px h-[3px] w-[8%] -translate-x-1/2 bg-naipe" style={{ left: `${left}%` }} />
      ))}
      {gaps.map((left) => (
        <span key={`b${left}`} className="absolute -bottom-px h-[3px] w-[8%] -translate-x-1/2 bg-naipe" style={{ left: `${left}%` }} />
      ))}
    </span>
  );
}

export function Naipe({
  card,
  size = "baza",
  className = "",
}: {
  card: Card;
  size?: keyof typeof SIZES;
  className?: string;
}) {
  const big = size === "mano";
  return (
    <div
      className={`${SIZES[size]} relative aspect-[5/8] select-none rounded-[10%/6%] bg-naipe shadow-[0_2px_0_rgb(0_0_0/0.08),0_8px_14px_-8px_rgb(15_59_53/0.7)] ring-1 ring-black/10 ${className}`}
      role="img"
      aria-label={card.label}
    >
      <Marco suit={card.suit} />
      <span
        className={`absolute left-[12%] top-[9%] bg-naipe px-px font-[750] leading-none [font-stretch:80%] ${big ? "text-2xl" : "text-base lg:text-xl"}`}
        style={{ color: SUIT_COLOR[card.suit] }}
        aria-hidden="true"
      >
        {card.number}
      </span>
      <Palo suit={card.suit} className="absolute inset-x-[18%] top-1/2 -translate-y-1/2" />
      <span
        className={`absolute bottom-[9%] right-[12%] bg-naipe px-px font-[750] leading-none [font-stretch:80%] ${big ? "text-2xl" : "text-base lg:text-xl"}`}
        style={{ color: SUIT_COLOR[card.suit] }}
        aria-hidden="true"
      >
        {card.number}
      </span>
    </div>
  );
}

export function Dorso({ size = "baza", className = "" }: { size?: keyof typeof SIZES; className?: string }) {
  return (
    <div
      className={`${SIZES[size]} aspect-[5/8] rounded-[10%/6%] bg-chapa p-[7%] shadow-[0_6px_12px_-8px_rgb(0_0_0/0.8)] ring-1 ring-black/20 ${className}`}
      aria-hidden="true"
    >
      <div
        className="h-full w-full rounded-[8%/5%] border border-tubo/50"
        style={{
          backgroundImage:
            "repeating-linear-gradient(45deg, rgb(233 238 240 / 0.16) 0 2px, transparent 2px 7px), repeating-linear-gradient(-45deg, rgb(233 238 240 / 0.16) 0 2px, transparent 2px 7px)",
        }}
      />
    </div>
  );
}
