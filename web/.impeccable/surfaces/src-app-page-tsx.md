---
version: 1
slug: "src-app-page-tsx"
primary_target: "src/app/page.tsx"
related_targets:
  - "src/app/globals.css"
  - "src/components/Cartelera.tsx"
  - "src/components/Mesa.tsx"
  - "src/components/Naipe.tsx"
  - "src/components/Tanteador.tsx"
  - "src/components/Overlay.tsx"
  - "src/components/Anotador.tsx"
  - "src/components/Analisis.tsx"
  - "src/lib/table.ts"
  - "src/lib/travel.ts"
---

# Inicio y mesa: noche de truco (`/`)

Modo: Operate. Audiencia: jugadores de truco y gente técnica curiosa (PRODUCT.md). Tarea: elegir rival, jugar una partida a 15, leer cada jugada y canto, y consultar las probabilidades del bot a pedido. El front representa la observación y las acciones legales de la API; la secuencia visual no calcula reglas.

## Direction contract

THESIS: Una noche de truco en una cancha de barrio. Una sola baza central y las tres cartas propias abajo, confirmado por el usuario.

OWN-WORLD: Azul noche, paño petróleo, celeste argentino y crema de naipe; Archivo condensada y pesada, botones anchos y cartas españolas propias. Estadio original ilustrado como ambiente continuo. Referencias como esencia, nunca copia. Los tokens y componentes implementados están documentados en DESIGN.md.

STORY: Elegir un bot, jugar a 15, ver las cartas llegar una a una, cantar y volver a repartir. Historial y análisis disponibles bajo demanda. Las reglas y los datos siguen siendo autoridad de la API.

FIRST VIEWPORT: Inicio centrado con el título «TRUCO / DE UNA.», dos naipes ilustrativos y selector compacto de rival. Partida con marcador arriba, rival al fondo, mesa ovalada central con la última baza visible y mano propia en abanico abajo. El estado y los cantos están debajo de la mano. Móvil conserva esa composición y adapta las medidas para mantener controles táctiles amplios. Historial y análisis se abren en diálogos desde el pie.

FORM: Dirección fijada por referencias y aclaración explícita del usuario; seed 3f98d489 subordinado al brief. Implementación desde código según delegación explícita del usuario. La imagen generada es un recurso ambiental, no un mockup aprobado. Interacción firma: entrada secuencial de cartas en una única zona de juego. Este contrato reemplaza la dirección anterior de sede de club con tres columnas de bazas.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Implemented interaction

- La página alterna inicio y mesa según la partida del store. El selector consume `/agents`; el heurístico se preselecciona si está disponible. La semilla opcional se despliega y valida antes de repartir.
- La única baza central corresponde al último cruce con alguna carta revelada. Tres indicadores laterales conservan sus resultados anteriores; las jugadas completas siguen disponibles en Historial.
- La mano propia aparece debajo de la zona de cartas jugadas. Sus botones dependen de las acciones `PLAY_CARD_` y del turno informados por la API. Los cantos muestran exactamente las etiquetas legales del servidor.
- Los eventos de carta de cada respuesta aparecen a los 120ms y luego cada 650ms. Cada viaje dura 520ms. El resultado de baza se oculta hasta que ambas cartas estén reveladas; los controles se bloquean durante solicitudes y mientras queden eventos de carta por revelar.
- El cierre de mano anuncia el resultado y permite «Repartir la siguiente». El cierre de partida permite «Otra partida» o «Cambiar de rival». Salir durante la partida solicita confirmación en un diálogo.
- Historial, Análisis y reglas son diálogos nativos con cierre explícito y Escape. El análisis usa la policy recibida y representa el porcentaje visible con un decimal.
- Movimiento reducido elimina animaciones y transiciones, omite el viaje y revela la secuencia con demora cero. La partida sigue siendo operable con teclado; cartas, turnos, resultados y controles tienen texto accesible.

## Responsive behavior

El punto principal de adaptación es 640px. La mesa se estrecha, los cantos se envuelven y la mano conserva tres cartas operables. Hasta 370px se reduce el título y se omite el pequeño detalle redundante del costado de la mesa. En móvil de hasta 740px de alto se compactan marcador y naipes con una escena de 335px, preservando el espacio entre resultado y mano; en escritorio de hasta 760px de alto también se ajusta la escena. No se agregan columnas laterales permanentes para historial ni análisis.

## Asset and verification evidence

Fondo: `public/images/cancha-noche.webp`, generado originalmente para esta aplicación con image_gen; procedencia en `public/images/cancha-noche.webp.json`. Es decorativo, no un estadio real ni una composición aprobada.

Capturas de la implementación en `.impeccable/review/`: `desktop-lobby-new.png`, `mobile-lobby-new.png`, `desktop-table-new.png`, `desktop-play-new.png`, `desktop.png`, `mobile.png`, `mobile-small.png`, `user-1916.png` y `mobile-analysis.png`. La validación de entrega incluye una partida completa de 12 manos en navegador, los 12 tests del frontend y el build de producción. La revisión final dio veredicto de entrega después de corregir el contraste de oro y la separación entre resultado y mano en pantallas cortas. Las capturas son evidencia de implementación, no una aprobación visual independiente del usuario.
