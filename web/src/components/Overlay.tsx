"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { Icon } from "@/components/Icon";

export function Overlay({
  title,
  onClose,
  children,
}: {
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const dialog = ref.current;
    dialog?.showModal();
    return () => dialog?.close();
  }, []);
  return (
    <dialog
      ref={ref}
      className="game-dialog"
      aria-label={title}
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="dialog-inner">
        <header className="dialog-heading">
          <h2>{title}</h2>
          <button
            type="button"
            className="icon-button"
            onClick={onClose}
            aria-label="Cerrar"
          >
            <Icon name="close" />
          </button>
        </header>
        {children}
      </div>
    </dialog>
  );
}

export function Rules({ onClose }: { onClose: () => void }) {
  return (
    <Overlay title="Un ratito para las reglas" onClose={onClose}>
      <div className="rules-copy">
        <p>
          Truco argentino, uno contra uno. Antes de repartir elegís si la
          partida termina a <strong>15 o 30 puntos</strong>.
        </p>
        <h3>Tres cartas. Mucha picardía.</h3>
        <p>
          Tocá una carta para jugarla. Cada mano tiene hasta tres bazas; la
          carta más fuerte gana cada cruce. Si hay empate, la primera baza y
          quién es mano definen el resultado.
        </p>
        <h3>De mayor a menor</h3>
        <p>
          1 de espada · 1 de basto · 7 de espada · 7 de oro · todos los 3 ·
          todos los 2 · 1 de oro y copa · 12 · 11 · 10 · 7 de copa y basto · 6 ·
          5 · 4.
        </p>
        <h3>El canto también juega</h3>
        <p>
          El truco sube el valor de la mano. El envido compara tus puntos: dos
          cartas del mismo palo suman 20 más sus valores; 10, 11 y 12 valen cero
          para el envido. La mesa te muestra tu tanto y los cantos disponibles.
        </p>
        <h3>Conocé a tu rival</h3>
        <p>
          Abrí <strong>Análisis</strong> durante la partida para ver las
          probabilidades que usó el bot. En <strong>Historial</strong> podés
          repasar las cartas y los cantos.
        </p>
      </div>
      <button type="button" className="primary-button" onClick={onClose}>
        Listo, a la mesa <Icon name="arrow" />
      </button>
    </Overlay>
  );
}
