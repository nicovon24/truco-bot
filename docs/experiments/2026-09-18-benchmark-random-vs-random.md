# Experimento: benchmark del motor random vs random

## Identidad

- Fecha: 2026-09-18
- Commit: ver el commit que agrega este registro (fases 2–4)
- Autor: nicovon24 (con Claude Code)
- Objetivo: medir manos/segundo del motor puro antes de optimizar.

## Configuración

- Comando: `uv run python engine/benchmarks/random_vs_random.py --games 2000 --seed 0`
- Reglas: `RulesConfig()` (a 15, bonus de mazo activado)
- Semillas: 0..1999 (reparto `Random(seed)`, agentes `Random("agents:{seed}")`)
- Contrato: v1

## Entorno

- AMD Ryzen 5 5600, Windows 11, Python 3.12.2

## Resultados

- 2000 partidas, 14.595 manos, 54.176 decisiones en 4,00 s.
- **3.646 manos/s**, 13.534 decisiones/s.

## Observaciones

Perfil (`cProfile`, 500 partidas): el mayor costo es `dataclasses.replace` (~35% del tiempo), seguido por `legal_actions` (se llama también dentro de `apply` para validar) y `observe`. No se optimizó nada: el SPEC pide hacerlo solo cuando el entrenamiento lo justifique.

## Próximos pasos

Si MCCFR (fase 6–7) queda limitado por el motor: evitar la doble llamada a `legal_actions` en recorridos internos y reducir `replace` anidados.
