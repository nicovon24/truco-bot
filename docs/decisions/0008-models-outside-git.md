# ADR 0008 — Modelos fuera de Git referenciados por metadata

- Estado: Aceptada
- Fecha: 2026-09-18

## Contexto

Los checkpoints y modelos exportados pueden ser grandes, cambian con frecuencia y no ofrecen diffs útiles en Git. El serving necesita verificar origen y compatibilidad.

## Decisión

Guardar binarios en S3 o GitHub Releases. En Git, `models/<nombre>/` contiene solamente `metadata.json` con URL, checksum, procedencia, contrato y resultados de evaluación.

## Alternativas consideradas

- Commit de binarios: aumenta el repositorio y no preserva revisiones legibles.
- Git LFS: agrega operación y cuotas sin resolver por sí solo la validación contractual.
- Descargar una URL sin metadata versionada: pierde trazabilidad y compatibilidad verificable.

## Consecuencias

- El historial de Git permanece liviano.
- La API necesita red al descargar un artefacto ausente y una caché local.
- La disponibilidad del proveedor de artefactos afecta el arranque en frío.
- Checksum y contrato deben verificarse antes de habilitar un agente.

