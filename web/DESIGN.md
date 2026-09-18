---
name: Truco Bot
description: Una noche de truco argentino en una cancha de barrio, contra bots que muestran cómo deciden.
colors:
  night: "#0b1d2a"
  sky: "#8ed8ed"
  cream: "#f4eedc"
  muted: "#afc6cd"
  naipe: "#fff9e9"
  tubo: "#edf5f5"
  zocalo-deep: "#102d3a"
  table: "#155462"
  envido: "#efd5a3"
  quiet: "#163544"
  action-ink: "#102936"
  quiet-ink: "#e2edef"
  primary-hover: "#b5ebf7"
  input: "#0b202d"
  oro: "#95681b"
  copa: "#ab3b36"
  espada: "#27678b"
  basto: "#3c7949"
typography:
  display:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(62px, 6.5vw, 92px)"
    fontWeight: 950
    lineHeight: 0.88
    letterSpacing: "-0.04em"
    fontVariation: "'wdth' 75"
  score:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "48px"
    fontWeight: 900
    lineHeight: 1
    fontFeature: "'tnum' 1"
    fontVariation: "'wdth' 75"
  title:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "23px"
    fontWeight: 850
    lineHeight: 1.15
    fontVariation: "'wdth' 85"
  body:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.7
    fontFeature: "'tnum' 1"
  primary-action:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 850
    letterSpacing: "0.025em"
    fontVariation: "'wdth' 75"
  canto:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 800
  label:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "11px"
    fontWeight: 750
    letterSpacing: "0.06em"
  card-index:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "24px"
    fontWeight: 750
    lineHeight: 1
    fontVariation: "'wdth' 80"
rounded:
  field: "6px"
  canto: "7px"
  control: "8px"
  seat: "12px"
  dialog: "16px"
  naipe: "10% / 6%"
  table: "44% / 48%"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
components:
  button-primary:
    backgroundColor: "{colors.sky}"
    textColor: "{colors.night}"
    typography: "{typography.primary-action}"
    rounded: "{rounded.control}"
    padding: "14px 22px"
    width: "100%"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-canto:
    backgroundColor: "{colors.sky}"
    textColor: "{colors.action-ink}"
    typography: "{typography.canto}"
    rounded: "{rounded.canto}"
    padding: "11px 18px"
  button-envido:
    backgroundColor: "{colors.envido}"
    textColor: "{colors.action-ink}"
    typography: "{typography.canto}"
    rounded: "{rounded.canto}"
    padding: "11px 18px"
  button-quiet:
    backgroundColor: "{colors.quiet}"
    textColor: "{colors.quiet-ink}"
    typography: "{typography.canto}"
    rounded: "{rounded.canto}"
    padding: "11px 18px"
  button-utility:
    backgroundColor: "rgb(10 29 42 / 0.82)"
    textColor: "{colors.cream}"
    rounded: "{rounded.control}"
    padding: "9px 14px"
  input-semilla:
    backgroundColor: "{colors.input}"
    textColor: "{colors.cream}"
    rounded: "{rounded.field}"
    padding: "8px 12px"
    height: "44px"
  dialog:
    backgroundColor: "{colors.zocalo-deep}"
    textColor: "{colors.cream}"
    rounded: "{rounded.dialog}"
    width: "min(calc(100% - 32px), 560px)"
  table:
    backgroundColor: "{colors.table}"
    rounded: "{rounded.table}"
  naipe-mano:
    backgroundColor: "{colors.naipe}"
    rounded: "{rounded.naipe}"
    width: "96px"
  result-human:
    backgroundColor: "{colors.sky}"
    textColor: "{colors.night}"
    rounded: "5px"
    padding: "5px 12px"
---

# Design System: Truco Bot

## Overview

**Creative North Star: "Una noche de truco en la cancha de barrio"**

Un estadio de barrio ilustrado, las luces encendidas y el cielo azul noche sitúan la partida en un mundo argentino propio. El celeste y la crema recortan las acciones y las cartas sobre superficies oscuras. El ambiente es continuo entre inicio y partida; la ilustración acompaña sin contener texto, controles ni información de juego.

Archivo condensada y pesada aporta el carácter deportivo. El volumen está en el borde de la mesa y en los naipes; la interfaz usa controles amplios, rótulos breves y superficies oscuras legibles. La imagen ambiental es original y las cartas se construyen con CSS y SVG propios. Las referencias del usuario fijan la esencia; no se reproducen sus pantallas.

**Key Characteristics:**

- Azul noche, celeste argentino y crema, con paño petróleo y acentos cálidos para envido.
- Una sola familia, Archivo variable, con titulares y cifras condensados.
- Naipes españoles propios, claros y táctiles, con dorsos azul petróleo.
- Ambiente ilustrado continuo y profundidad concentrada en objetos de juego.
- Movimiento breve de reparto, carta, resultado y marcador; alternativa inmediata con movimiento reducido.

## Colors

Los valores normativos están en el frontmatter, extraídos de `src/app/globals.css` y los componentes implementados.

### Primary

**Celeste argentino** (`sky`) identifica acción principal, cantos de truco, foco, cifra y resultado propios. `primary-hover` aclara la acción principal al pasar el puntero.

### Secondary

**Crema de tribuna** (`cream`) recorta títulos, cifra rival y texto sobre oscuro. **Arena de envido** (`envido`) identifica los cantos cuyos nombres incluyen `ENVIDO`, sin modificar su texto ni disponibilidad. **Petróleo de mesa** (`table`) corresponde al paño de la mesa ovalada.

### Neutral

**Azul noche** (`night`) es la base de página, el color del navegador y la tinta sobre celeste. **Azul profundo** (`zocalo-deep`) se usa en diálogos, asiento rival y sello de resultado; su nombre CSS heredado no define un material visual. **Azul silencioso** (`quiet`), **tinta clara** (`quiet-ink`) y **tinta de acción** (`action-ink`) distinguen controles y cantos. **Texto secundario** (`muted`) contextualiza; **blanco de lectura** (`tubo`) aparece en historial y análisis; **crema de naipe** (`naipe`) forma las cartas y **azul de campo** (`input`) el campo de semilla.

Los cuatro colores de palo corresponden al dibujo y marco del naipe. Oro usa su valor final oscurecido para conservar contraste en índices pequeños. Los errores usan salmón sobre fondo oscuro rojizo, como en la implementación.

**The Palo Encerrado Rule.** Los colores de palo identifican cartas; no se convierten en un sistema de estados de la interfaz.

## Typography

**Display Font:** Archivo, con ui-sans-serif, system-ui y sans-serif de respaldo.

**Body Font:** la misma familia, cargada por `next/font` con el eje `wdth` y `display: swap`.

El título del inicio usa mayúsculas, peso 950, ancho 75% y dos líneas. Su escala normal es fluida; pasa a 74px en móvil, 66px hasta 370px, 64px en escritorio corto y 96px desde 1500 × 850px. El marcador usa peso 900, ancho 75% y dos dígitos: 48px en escritorio, 39px en móvil y 32px en móvil corto.

Los títulos de diálogo usan el rol `title` y bajan a 20px en móvil. `body` describe la lectura de reglas; las explicaciones breves usan 12–15px según contexto. Las etiquetas del marcador son mayúsculas. Los índices de mano y de inicio usan `card-index`; las cartas de baza usan 16px y 20px desde 1024px.

**The Una Familia Rule.** Archivo resuelve título, cifra, acción y lectura mediante peso y ancho; no se añade otra familia para crear jerarquía.

**The Cifra Tabular Rule.** El cuerpo usa cifras tabulares para que marcador, semilla y probabilidades mantengan su alineación.

## Layout

La aplicación ocupa al menos `100dvh`, con fondo fijo y contenido centrado entre encabezado y pie. El inicio tiene hasta 440px de ancho; en móvil, hasta 410px con 22px de margen lateral. La partida tiene un contenedor de hasta 1000px y una escena de hasta 860px. Su composición concreta vive en el brief de `/`.

El ancho de 640px activa la adaptación móvil. La escena pasa de `clamp(410px, 53dvh, 530px)` a `clamp(365px, 51dvh, 455px)`; hasta 740px de alto en móvil se compacta a 335px. Escritorios de hasta 760px de alto usan 390px. Desde 1500 × 850px usa 520px.

Los controles auxiliares miden al menos 44px; los cantos, 46px en escritorio y 44px en móvil. La acción primaria tiene un mínimo de 56px, ampliado a 60px al iniciar; las acciones de continuación usan 48px. Los cantos se envuelven y distribuyen el ancho disponible. La semilla avanzada se despliega a pedido. Historial, análisis y reglas usan diálogos de hasta 560px, con márgenes móviles de 16px y altura máxima de `min(85dvh, 760px)`.

El espaciado documentado recoge valores reutilizados; los objetos de juego conservan medidas específicas para su composición.

## Elevation & Depth

La profundidad combina estadio pintado, capa oscura de legibilidad y objetos con sombra. La mesa tiene borde grueso, filete interior y canto inferior; los naipes tienen arista de papel y sombra. Los diálogos se separan mediante borde y sombra sobre un backdrop oscuro al 80%.

### Shadow Vocabulary

- **Naipe:** `0 3px 0 #b6ad95, 0 10px 22px rgb(0 0 0 / 0.28)`.
- **Acción primaria:** `0 6px 18px rgb(0 0 0 / 0.2)`.
- **Mesa:** `inset 0 0 0 2px #8a967e, inset 0 -18px 50px rgb(3 30 40 / 0.3), 0 8px 0 #112b35, 0 24px 50px rgb(0 0 0 / 0.4)`.
- **Diálogo:** `0 24px 90px rgb(0 0 0 / 0.5)`.

**The Objeto Legible Rule.** La profundidad sitúa cartas, mesa y diálogo; no debe competir con sus textos ni con la lectura de una jugada.

## Shapes

Acciones y controles auxiliares usan esquinas de 8px, cantos de 7px y campos de 6px. El asiento rival usa 12px y el diálogo 16px. La mesa es ovalada (`44% / 48%`), pasa a `42% / 32%` en móvil y reduce el borde de 9px a 6px.

El naipe conserva proporción 5:8 y radio `10% / 6%`. El dorso tiene campo petróleo, filete crema y marca propia. Indicadores de baza y avatar son circulares. El bocadillo del rival tiene fondo crema y una esquina inferior de 2px.

## Components

### Buttons

La acción primaria es celeste y ancha, con texto oscuro en mayúsculas; sube 2px y aclara en hover, y baja 1px al presionarla. Los cantos usan el texto legal de la API sin comillas añadidas: celeste para el resto de acciones, arena para envido y azul con borde para `FOLD` o nombres que incluyen `REJECT`. El bocadillo y el historial sí pueden citar cantos entre comillas angulares.

Los controles auxiliares usan fondo azul translúcido, texto crema e iconos SVG; en el pie su fondo de reposo es transparente. Se deshabilitan las acciones durante solicitudes y mientras falten cartas por revelar. El foco general es un contorno celeste de 3px separado 5px.

### Inputs / Fields

El rival se elige con un `select` nativo de al menos 50px sobre fondo oscuro con borde e iconos; sus opciones, nombre de dificultad y descripción provienen de la API. Debajo se muestra la técnica real del bot. La duración se selecciona con dos radios segmentados, 15 puntos como partida rápida y 30 como partida completa. La semilla vive en un `details`: campo de 44px, texto de 16px, explicación del error de entero inválido, `aria-invalid` y borde salmón.

### Navigation and dialogs

El inicio presenta marca y reglas. En partida, `Salir` abre una confirmación con `Seguir jugando` como acción principal. Historial y análisis están en el pie. Los diálogos usan `<dialog>.showModal()`, nombre accesible, cierre explícito, Escape y clic en el fondo exterior; su contenido puede desplazarse verticalmente.

### Marcador and result indicators

El marcador muestra `Vos`, nombre del bot, objetivo, número de mano y palitos en SVG. Las cifras tienen dos dígitos; la propia es celeste y la rival crema. Cada cambio entra desde 5px arriba con opacidad creciente durante 350ms; no gira en tres dimensiones.

Tres indicadores conservan resultados: celeste con check para el humano, arena para el bot y petróleo para parda. Tienen nombres accesibles. El resultado central incluye una etiqueta escrita.

### Naipe

Palos propios en SVG y marco con interrupciones tradicionales: cero para oro, una para copa, dos para espada y tres para basto. El as tiene un palo grande; del 2 al 7 se repite la cantidad de palos; sota, caballo y rey llevan inicial y nombre. Los índices de esquinas opuestas están invertidos.

Anchos normales: mano 96px, baza 84px, dorso rival 34px e inicio 92px. En móvil: 78, 65, 29 y 79px. Móvil corto: mano 66px y baza 57px; escritorio corto: 83 y 70px. Cada carta anuncia número y palo; el botón jugable anuncia la acción de la API. El abanico usa −9°, 0° y 9°; hover y foco elevan 16px, y la pulsación eleva 22px con escala 1.04.

### Motion and presentation timing

El reparto entra desde 24px abajo en 450ms, con 90ms de separación por slot. La carta viaja desde su origen registrado o la mano correspondiente hasta la baza en 520ms, con `cubic-bezier(0.16, 1, 0.3, 1)`. Sale a −7°, se asienta desde 1.5° y escala 1.02, y termina en su lugar. Bocadillos y resultados entran en 250ms.

La presentación revela únicamente eventos recibidos: primera carta a los 120ms y cada siguiente 650ms después. Hasta que ambas estén reveladas no muestra el resultado de esa baza. Los controles se bloquean mientras queden cartas por revelar. Esa demora organiza la lectura sin calcular reglas ni fabricar jugadas.

Con `prefers-reduced-motion: reduce` se desactivan animaciones y transiciones CSS, se omite el viaje y todos los eventos se revelan con demora cero. La información y las acciones se conservan.

### History and analysis

El historial representa eventos del servidor y resalta reparto y resultados. El análisis ordena las decisiones desde la última, con acción elegida y probabilidades recibidas. El porcentaje visible se redondea a un decimal; las barras usan la probabilidad original con un mínimo visual de 1.5% para valores positivos. La adaptación gráfica no cambia la policy.

### Environmental illustration

`public/images/cancha-noche.webp` es la ilustración original generada para el proyecto: 1536 × 1024, WebP de aproximadamente 141 KB. Se aplica con `cover`, centrada al 57% vertical, como fondo decorativo. Prompt y procedencia están en `public/images/cancha-noche.webp.json`. No representa un estadio real ni un mockup aprobado por el usuario.

## Do's and Don'ts

### Do:

- **Do** mantener la paleta azul noche, celeste y crema sobre el ambiente ilustrado original.
- **Do** usar Archivo y cifras tabulares para toda la jerarquía.
- **Do** conservar objetivos táctiles amplios y foco celeste visible.
- **Do** dibujar naipes e iconos con CSS y SVG propios.
- **Do** renderizar acciones, puntos y resultados desde la API, con nombres accesibles y texto de estado.
- **Do** respetar el movimiento reducido sin demorar la revelación de cartas.
- **Do** conservar la procedencia de cada recurso raster que se publique.

### Don't:

- **Don't** copiar las pantallas, los naipes ni los recursos de las referencias del usuario.
- **Don't** volver a la identidad anterior de pared clara, fórmica y chapa bordó.
- **Don't** trasladar los colores de palo a estados ajenos a las cartas.
- **Don't** sustituir resultados o probabilidades del servidor por estimaciones de la interfaz.
- **Don't** presentar el ambiente generado como una fotografía o un lugar real.
