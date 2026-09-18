# ADR 0006 — Inferencia con ONNX Runtime en la API

- Estado: Aceptada
- Fecha: 2026-09-18

## Contexto

PyTorch es necesario para entrenar, pero aumenta el tamaño y consumo de memoria de la imagen de serving. La API solo necesita inferencia.

## Decisión

Exportar redes a ONNX y ejecutar inferencia con ONNX Runtime y NumPy. PyTorch queda excluido de las dependencias de `api/`.

## Alternativas consideradas

- Servir directamente con PyTorch: simplifica la exportación, pero aumenta imagen, memoria y superficie de dependencias.
- Reimplementar las capas con NumPy: agrega mantenimiento y riesgo de divergencia numérica.

## Consecuencias

- La imagen de API es más acotada y separa entrenamiento de serving.
- Cada exportación debe superar un test de paridad PyTorch–ONNX Runtime.
- Operaciones no soportadas por ONNX condicionan futuras arquitecturas.

