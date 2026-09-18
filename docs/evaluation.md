# Evaluación

## Torneos

La comparación principal es un torneo todos contra todos en partidas completas a 15 puntos. Usa una lista fija y publicada de semillas. Cada reparto se juega de manera espejada: los mismos agentes vuelven a jugarlo intercambiando lados, cartas y condición de mano, de modo que la ventaja del reparto no favorezca siempre al mismo bot.

Se reportan partidas y pares espejados, victorias, derrotas, win rate, diferencia media de puntos e intervalo de confianza. Los empates, si el límite operativo permite que existan, se informan por separado y no se descartan silenciosamente.

> ⚠️ A CONFIRMAR: cantidad mínima de partidas o pares espejados por cruce, nivel del intervalo de confianza, método estadístico y eventual límite máximo de manos por partida.

Para comparar iteraciones de entrenamiento se grafica el win rate contra una versión fija del agente heurístico, usando el mismo conjunto de semillas y repartos espejados en todos los puntos de la curva.

## Explotabilidad

En Kuhn Poker la explotabilidad se calcula de manera exacta y debe tender a cero junto con la convergencia al valor `−1/18` para el primer jugador.

En Truco no se afirma explotabilidad exacta. Se entrena un `MaskablePPO` explotador contra la política objetivo congelada y se mide su ventaja con el mismo protocolo reproducible de evaluación. El informe debe llamarla **explotabilidad aproximada**, identificar el presupuesto y configuración del explotador y evitar comparar valores obtenidos con presupuestos distintos como si fueran equivalentes.

## Reproducibilidad

Cada evaluación registra:

- commit y estado del código;
- versión del contrato de acciones y observación;
- IDs, versiones y checksums de los modelos;
- configuración efectiva;
- lista de semillas;
- cantidad de partidas y pares espejados;
- hardware, duración y fecha.

## Reporte

`truco-train eval tournament` genera en `reports/`:

1. una tabla Markdown con una fila por enfrentamiento y métricas agregadas;
2. una matriz o gráfico de win rates;
3. curvas contra el heurístico cuando se evalúan checkpoints;
4. datos estructurados suficientes para regenerar las tablas y gráficos;
5. referencia al registro de experimento correspondiente.

Un resultado no se publica en `metadata.json` si no puede vincularse con su configuración, semillas y artefactos exactos.

