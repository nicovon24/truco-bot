# ADR 0009 — Entrenamiento local o Colab y serving en la nube

- Estado: Aceptada
- Fecha: 2026-09-18

## Contexto

El entrenamiento puede requerir GPU y procesos largos, mientras el producto necesita una web y una API livianas y disponibles. No hace falta entrenar dentro de producción.

## Decisión

Ejecutar entrenamiento de forma local o en Colab, registrar cada experimento y publicar sus artefactos. Desplegar la web en Vercel y la API con modelos en Railway; Render y Fly.io quedan como alternativas.

## Alternativas consideradas

- Entrenamiento dentro de Railway: mezcla cargas, encarece el servicio y complica despliegues reproducibles.
- Servir todo desde un único proveedor o proceso: acopla ciclos de despliegue y requisitos de recursos distintos.

## Consecuencias

- Entrenamiento y serving escalan y se actualizan por separado.
- La transferencia se realiza mediante artefactos versionados y metadata.
- Cada entorno de entrenamiento debe registrar hardware, dependencias, semilla y commit.
- El deploy depende de límites y comportamiento operativo de Vercel y Railway.

