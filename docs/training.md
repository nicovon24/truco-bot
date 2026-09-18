# Entrenamiento

## Juego de entrenamiento

Los algoritmos consumen solamente el protocolo genérico de `games/game_api.py`: `current_player`, `legal_actions`, `apply`, `is_terminal`, `returns`, `info_key(player)`, `info_tensor(player)` y `sample_chance(rng)`. Los nodos pueden pertenecer al jugador 0, al jugador 1 o a `CHANCE`. La aleatoriedad entra por un generador con semilla registrada.

`truco_hand` representa una única mano como juego de suma cero. El payoff es `puntos ganados - puntos perdidos`; quién es mano se sortea en el nodo de azar y forma parte del information set. La variante `sin_envido` se implementa primero y `completo` agrega el envido después. El adaptador ignora el marcador de una partida: Falta Envido usa un valor fijo configurable. Por eso una política óptima para `truco_hand` no necesariamente es óptima en cada marcador de una partida a 15.

## Validación con Kuhn Poker

Kuhn Poker valida la implementación de MCCFR antes de usarla con Truco. El valor esperado para el primer jugador debe converger a `−1/18` y la explotabilidad debe tender a cero. Mientras esas condiciones no se cumplan con una corrida reproducible, no se habilita el entrenamiento tabular de Truco.

## MCCFR tabular

La implementación usa external sampling. En los nodos del jugador recorrido evalúa todas las acciones legales y actualiza regrets; en los nodos del rival muestrea la estrategia actual y acumula la estrategia promedio; en los nodos de azar muestrea mediante el RNG de la corrida. Regret matching+ y el promedio lineal son opciones configurables.

Las tablas usan `dict[info_key, np.ndarray]`. La corrida guarda checkpoints periódicos, cantidad de information sets, memoria utilizada y métricas de convergencia. La salida servible es la estrategia promedio exportada a msgpack. `TabularAgent` usa el heurístico cuando encuentra una clave desconocida y contabiliza esos fallbacks.

## Deep CFR

Deep CFR mantiene una red de ventajas por jugador con arquitectura `encode → 256 → 256 → 13`. La máscara elimina acciones ilegales y regret matching transforma las ventajas predichas en una estrategia. Cada iteración realiza `K` recorridos con external sampling y guarda ejemplos ponderados por iteración en reservoirs separados para ventajas y estrategia.

Cada red de ventajas se reentrena desde cero en cada iteración con pérdida MSE ponderada. Al finalizar, una red de estrategia se entrena sobre el reservoir acumulado y se convierte en el bot servible. Los checkpoints de PyTorch pertenecen al entorno de entrenamiento; la API recibe solamente la exportación ONNX validada.

## MaskablePPO

PPO es un experimento comparativo implementado con `MaskablePPO` de `sb3-contrib`. El entorno Gymnasium representa una mano, expone `action_masks()` y normaliza el payoff como recompensa. No se implementa un PPO propio.

El rival se elige mediante pesos configurables entre checkpoints anteriores, el heurístico y el agente random. Se agrega un checkpoint propio al pool cada cantidad configurable de updates. Los experimentos deben registrar señales de ciclado estratégico y si el pool logra mitigarlo.

## Configuración y ejecución

Cada corrida parte de un YAML versionado en `training/configs/`. Como mínimo debe registrar algoritmo, variante del juego, semilla, presupuesto de entrenamiento, frecuencia de checkpoint, evaluación periódica y opciones específicas del algoritmo. Los valores efectivos, incluido cualquier override de CLI, se guardan junto al resultado.

El contrato previsto de la CLI es:

```bash
uv run truco-train train --config training/configs/<config>.yaml
uv run truco-train eval tournament --config training/configs/<config>.yaml
uv run truco-train export --config training/configs/<config>.yaml
```

> ⚠️ A CONFIRMAR: nombres finales de los subcomandos y formato de overrides cuando se implemente `cli.py`.

## Checkpoints y reanudación

Cada checkpoint debe guardar el estado suficiente para reanudar la corrida de forma determinista cuando la biblioteca lo permita: iteración o update, estado del optimizador, parámetros, tablas o reservoirs aplicables, configuración efectiva y estados de los generadores aleatorios. También registra commit, fecha y versión de los contratos.

La frecuencia y la política de retención se definen en el YAML; no hay un valor global asumido. Reanudar genera un evento en el registro del experimento y conserva la procedencia del checkpoint original.

## Exportación

La estrategia promedio tabular se exporta a msgpack. Las redes se exportan a ONNX y deben superar una prueba de paridad numérica contra PyTorch con entradas representativas y máscaras legales. El exportador produce o completa `models/<nombre>/metadata.json` con tipo, versión, fecha, commit, config, semilla, versión del contrato, URL, checksum y evaluación.

Los binarios se publican en S3 o GitHub Releases y nunca se agregan a Git. La tolerancia numérica de la prueba de paridad queda pendiente de definir durante la fase de exportación.

