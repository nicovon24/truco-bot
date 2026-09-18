function Placa({ value }: { value: number }) {
  // La key hace que la placa gire cada vez que cambia el número.
  return (
    <span
      key={value}
      className="anim-placa inline-block min-w-[2ch] text-center"
    >
      {String(value).padStart(2, "0")}
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
          <svg
            key={s}
            viewBox="0 0 20 20"
            className="h-3.5 w-3.5 sm:h-4 sm:w-4"
          >
            {n > 0 && (
              <line
                x1="2"
                y1="2"
                x2="18"
                y2="2"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
              />
            )}
            {n > 1 && (
              <line
                x1="18"
                y1="2"
                x2="18"
                y2="18"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
              />
            )}
            {n > 2 && (
              <line
                x1="18"
                y1="18"
                x2="2"
                y2="18"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
              />
            )}
            {n > 3 && (
              <line
                x1="2"
                y1="18"
                x2="2"
                y2="2"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
              />
            )}
            {n > 4 && (
              <line
                x1="2"
                y1="18"
                x2="18"
                y2="2"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
              />
            )}
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
      aria-label={`Tanteador: vos ${human}, ${botName} ${bot}, a ${target}`}
      className="scoreboard"
    >
      <div className="score-side">
        <div>
          <span className="score-name">Vos</span>
          <span className="score-tally">
            <Palitos value={human} target={target} />
          </span>
        </div>
        <span className="score-number">
          <Placa value={human} />
        </span>
      </div>
      <div className="score-center">
        <strong>A {target} PUNTOS</strong>
        <span>Mano {handNumber + 1}</span>
      </div>
      <div className="score-side">
        <div>
          <span className="score-name">{botName}</span>
          <span className="score-tally">
            <Palitos value={bot} target={target} />
          </span>
        </div>
        <span className="score-number">
          <Placa value={bot} />
        </span>
      </div>
    </section>
  );
}
