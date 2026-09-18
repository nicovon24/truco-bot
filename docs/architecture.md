# Arquitectura

## Componentes del monorepo

```mermaid
flowchart LR
    Human[Jugador] --> Web[web<br/>Next.js]
    Web -->|HTTP + tipos OpenAPI| API[api<br/>FastAPI]
    API --> Engine[engine<br/>reglas puras]
    API --> Registry[agent_registry]
    Registry --> Agents[agentes del engine]
    Registry --> Metadata[models/*/metadata.json]
    Registry --> Storage[(S3 o GitHub Releases)]
    Training[training<br/>self-play y evaluación] --> Engine
    Training -->|msgpack / ONNX| Storage
    Training --> Metadata
    API --> Repo[repositorio de partidas<br/>memoria]
```

`engine/` es el núcleo compartido. No conoce HTTP, interfaces web ni frameworks de ML. `training/` consume el motor mediante adaptadores y exporta artefactos que `api/` puede servir sin PyTorch. `web/` trata a la API como única autoridad sobre el estado y las acciones legales.

## Secuencia de una jugada

```mermaid
sequenceDiagram
    actor H as Humano
    participant W as Web
    participant A as API
    participant E as Engine
    participant B as Bot
    participant R as GameRepository

    H->>W: elige una acción legal
    W->>A: POST /games/{id}/actions
    A->>R: carga la partida
    A->>E: legal_actions(state)
    E-->>A: acciones legales
    A->>E: apply(state, human_action)
    E-->>A: nuevo estado inmutable
    loop hasta que vuelva el turno humano o termine la mano
        A->>E: observación parcial + acciones legales
        A->>B: policy(obs, legal)
        B-->>A: probabilidades explícitas
        A->>B: act(obs, legal, seeded_rng)
        B-->>A: acción muestreada
        A->>E: apply(state, bot_action)
        E-->>A: nuevo estado inmutable
    end
    A->>R: guarda la partida
    A-->>W: estado público, legales y eventos con policies
    W-->>H: actualiza mesa y log
```

Una acción fuera de la lista legal produce HTTP 422. El front no valida reglas por su cuenta.

## Entrenamiento, exportación y serving

```mermaid
flowchart LR
    Config[config YAML<br/>+ semilla] --> Train[entrenamiento<br/>self-play]
    Engine[engine / Game API] --> Train
    Train --> Checkpoint[checkpoints]
    Checkpoint --> Eval[evaluación]
    Eval --> Report[reports/]
    Checkpoint --> Export[exportación]
    Export -->|tabular| Msgpack[.msgpack]
    Export -->|neural| ONNX[.onnx]
    ONNX --> Parity[test de paridad]
    Msgpack --> Artifact[(S3 o GitHub Releases)]
    Parity --> Artifact
    Report --> Metadata[metadata.json]
    Artifact --> Metadata
    Metadata --> Registry[agent_registry]
    Registry -->|checksum + contrato compatibles| Runtime[API: NumPy + ONNX Runtime]
```

El metadata registra procedencia, versión del contrato, checksum y resultados. La API rechaza un artefacto cuyo contrato no coincida con el motor desplegado.

## Deploy

```mermaid
flowchart TB
    Browser[Navegador] -->|HTTPS| Vercel[Vercel<br/>web]
    Vercel -->|HTTPS + CORS permitido| Railway[Railway<br/>API]
    Railway --> Memory[(partidas en memoria)]
    Railway --> Models[(cache local de modelos)]
    Railway --> Remote[(S3 o GitHub Releases)]
    Remote -->|descarga al arrancar| Models
    CI[GitHub Actions] --> Vercel
    CI --> Railway
```

La web recibe la URL pública de la API por variable de entorno. La API configura los orígenes CORS permitidos por variable de entorno. El repositorio de partidas en memoria se pierde al reiniciar o reemplazar la instancia.
