function Placa({ value }: { value: number }) {
  // La key hace que la placa gire cada vez que cambia el número.
  return (
    <span key={value} className="anim-placa inline-block min-w-[2ch] text-center">
      {value}
    </span>
  );
}

/** Palitos: el tanteo de mesa en cuadrados de cinco (cuatro lados y la diagonal). */
function Palitos({ value, target }: { value: number; target: number }) {
  // Solo se dibujan los trazos que hay: el palito se anota sobre la nada, no en casillas.
  const squares = Math.ceil(Math.min(value, target) / 5);
  return (
    <span className="flex h-3.5 gap-1.5 sm:h-4" aria-hidden="true">
      {Array.from({ length: squares }, (_, s) => {
        const n = Math.max(0, Math.min(5, value - s * 5));
        return (
          <svg key={s} viewBox="0 0 20 20" className="h-3.5 w-3.5 sm:h-4 sm:w-4">
            {n > 0 && <line x1="2" y1="2" x2="18" y2="2" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />}
            {n > 1 && <line x1="18" y1="2" x2="18" y2="18" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />}
            {n > 2 && <line x1="18" y1="18" x2="2" y2="18" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />}
            {n > 3 && <line x1="2" y1="18" x2="2" y2="2" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />}
            {n > 4 && <line x1="2" y1="18" x2="18" y2="2" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />}
          </svg>
        );
      })}
    </span>
  );
}

export function Tanteador({
  human,
  bot,
  target,
  botName,
  handNumber,
}: {
  human: number;
  bot: number;
  target: number;
  botName: string;
  handNumber: number;
}) {
  return (
    <section
      aria-label={`Tanteador: nosotros ${human}, ${botName} ${bot}, a ${target}`}
      className="chapa relative flex items-stretch rounded-xl px-3 pb-2 pt-2.5"
    >
      <span className="remache absolute left-2 top-2" />
      <span className="remache absolute right-2 top-2" />
      <span className="remache absolute bottom-2 left-2" />
      <span className="remache absolute bottom-2 right-2" />
      <div className="flex flex-1 flex-col items-center">
        <span className="text-[0.7rem] font-[800] uppercase tracking-[0.18em] [font-stretch:125%]">Nosotros</span>
        <span className="text-4xl font-[800] leading-none [font-stretch:75%] sm:text-5xl">
          <Placa value={human} />
        </span>
        <span className="mt-1">
          <Palitos value={human} target={target} />
        </span>
      </div>
      <div className="flex flex-col items-center justify-center px-2 text-center">
        <span className="text-[0.7rem] font-[700] uppercase tracking-[0.14em]">a {target}</span>
        <span className="mt-1 h-8 w-px bg-tubo/40" aria-hidden="true" />
        <span className="mt-1 text-[0.7rem] font-[600]">mano {handNumber + 1}</span>
      </div>
      <div className="flex flex-1 flex-col items-center">
        <span className="max-w-full truncate text-[0.7rem] font-[800] uppercase tracking-[0.18em] [font-stretch:125%]">
          {botName}
        </span>
        <span className="text-4xl font-[800] leading-none [font-stretch:75%] sm:text-5xl">
          <Placa value={bot} />
        </span>
        <span className="mt-1">
          <Palitos value={bot} target={target} />
        </span>
      </div>
    </section>
  );
}
