# ADR 0012 — Contrato v1 de acciones, `info_key` y `encode`

- Estado: Aceptada
- Fecha: 2026-09-18

## Contexto

`docs/action-space.md` dejaba abiertos el orden canónico de cartas, la estabilidad de slots, el formato de `info_key` y el layout de `encode`.

## Decisión

- Versión del contrato: `"1"`.
- Orden canónico: palo (espada, basto, oro, copa) y número (1–7, 10–12); índice = palo·10 + posición.
- Slots estables toda la mano, ordenados por escalón y desempatados por índice canónico.
- `info_key` y `encode` (317 posiciones) con el formato documentado en `docs/action-space.md`.
- En `info_key` las cartas jugadas se abstraen a su escalón de truco.

## Alternativas consideradas

- Compactar slots tras cada jugada: cambia el significado de un índice dentro de la mano y complica máscaras.
- Codificar cartas jugadas por escalón en `encode`: pierde el palo, que la red puede usar para inferir envido.

## Consecuencias

- Todo modelo entrenado declara `contract.version = "1"`, `num_actions = 13` y `encode_size = 317`; la API rechaza otros valores.
- Cualquier cambio de layout requiere versión 2.
