# ADR 0015 — Dependencias de ML como extra con PyTorch CPU

- Estado: Aceptada
- Fecha: 2026-09-18

## Contexto

Deep CFR y PPO necesitan PyTorch, Gymnasium y sb3-contrib; la API no debe depender de PyTorch. En Linux el wheel de PyPI de torch arrastra CUDA (varios GB).

## Decisión

- `truco-train[ml]` agrupa torch, onnx, onnxruntime, gymnasium, sb3-contrib, tensorboard y matplotlib. torch se resuelve desde el índice CPU de PyTorch (`[[tool.uv.index]] pytorch-cpu`, explícito).
- El grupo dev del workspace instala `truco-train[ml]`: la CI corre los tests de Deep CFR, paridad ONNX y PPO.
- La API usa `truco-engine[neural]` (solo onnxruntime + NumPy). La imagen Docker de la API no instala torch.

## Consecuencias

- `uv sync --all-groups` descarga ~200 MB extra la primera vez.
- Entrenar en GPU requiere cambiar el índice de torch en una config local, fuera del alcance actual.
