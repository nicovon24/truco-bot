# Deploy

## Entornos

| Entorno | Web | API y modelos | Propósito |
|---|---|---|---|
| Local | Next.js o Docker Compose | FastAPI o Docker Compose | Desarrollo y pruebas manuales |
| Preview | Preview de Vercel | Instancia de preview si se configura | Validación de cambios integrados |
| Producción | Vercel | Railway | Piloto público |

Render y Fly.io son alternativas para la API si Railway no satisface los límites operativos.

## Variables de entorno

| Componente | Variable | Uso |
|---|---|---|
| Web | `NEXT_PUBLIC_API_URL` | URL base pública de la API |
| API | `CORS_ORIGINS` | Lista explícita de orígenes permitidos |
| API | `MODEL_CACHE_DIR` | Directorio local para binarios descargados |
| API | `LOG_LEVEL` | Nivel de logs del servicio |
| API | `PORT` | Puerto asignado por la plataforma |

Las URLs y checksums de cada modelo viven en `metadata.json`, no en variables globales. Si el almacenamiento elegido es privado, sus credenciales se agregan como secretos del entorno y nunca se escriben en el repositorio.

> ⚠️ A CONFIRMAR: proveedor de binarios inicial —S3 o GitHub Releases— y si los artefactos serán públicos o privados.

## Publicar un modelo

1. Entrenar desde una configuración y semilla registradas.
2. Ejecutar la evaluación requerida y guardar el reporte.
3. Exportar a msgpack u ONNX; para ONNX, validar paridad con PyTorch.
4. Calcular el checksum del binario.
5. Subir el binario a S3 o GitHub Releases.
6. Crear `models/<nombre>/metadata.json` con tipo, versión, fecha, commit, config, semilla, contrato, URL, checksum y resultados.
7. Desplegar o reiniciar la API para que `agent_registry.py` valide la metadata, descargue el artefacto ausente y verifique el checksum.
8. Confirmar `GET /health` y que `GET /agents` publique la versión esperada.

La API rechaza modelos con checksum inválido o versión incompatible del espacio de acciones o `encode()`.

## Memoria y almacenamiento efímero

Las partidas viven inicialmente en un repositorio en memoria. Si Railway reinicia, reemplaza o escala la instancia, las partidas activas de esa instancia se pierden y los IDs dejan de ser recuperables. El piloto debe comunicar ese comportamiento y el cliente debe permitir iniciar otra partida.

La caché local de modelos también puede ser efímera: al arrancar, el registro vuelve a descargar cualquier binario ausente. El arranque debe fallar de forma visible si un modelo requerido no puede descargarse o validarse.

> ⚠️ A CONFIRMAR: plan concreto de Railway y Vercel. Sin esa elección no se pueden documentar límites numéricos de RAM, disco, tamaño de artefacto, tiempo de arranque ni suspensión.

Si el consumo de modelos supera el plan elegido, las opciones dentro del alcance son reducir o cuantizar artefactos compatibles, cargar solo los agentes habilitados o migrar la API a Render/Fly.io. Persistir partidas en Redis/Postgres queda detrás de la interfaz de repositorio y no forma parte del piloto inicial.
