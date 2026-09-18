---
name: Truco Bot
description: Truco argentino 1 vs 1 en la mesa de fórmica de la sede del club, contra bots que muestran cómo deciden.
colors:
  chapa: "#7b1e2c"
  formica: "#8cc7bf"
  formica-ink: "#0f3b35"
  zocalo: "#1e4d3b"
  zocalo-deep: "#153a2c"
  tubo: "#e9eef0"
  aluminio: "#b8bfc2"
  aluminio-dark: "#7d868a"
  naipe: "#fbfbf7"
  tinta: "#1b1f1e"
  oro: "#c8901c"
  copa: "#b3261e"
  espada: "#1f4e8c"
  basto: "#3e7a2e"
typography:
  display:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "2.25rem"
    fontWeight: 900
    lineHeight: 1
    letterSpacing: "0.02em"
    fontVariation: "'wdth' 125"
  score:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "2.25rem"
    fontWeight: 800
    lineHeight: 1
    fontFeature: "'tnum' 1"
    fontVariation: "'wdth' 75"
  headline:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "0.08em"
    fontVariation: "'wdth' 115"
  title:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 800
    lineHeight: 1.2
    fontVariation: "'wdth' 110"
  canto:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 750
    lineHeight: 1.3
    fontVariation: "'wdth' 105"
  body:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.625
    fontFeature: "'tnum' 1"
  label:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.7rem"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "0.14em"
    fontVariation: "'wdth' 125"
  card-index:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 750
    lineHeight: 1
    fontVariation: "'wdth' 80"
rounded:
  sm: "2px"
  md: "6px"
  lg: "8px"
  xl: "12px"
  naipe: "10% / 6%"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  2xl: "32px"
components:
  tanteador:
    backgroundColor: "{colors.chapa}"
    textColor: "{colors.tubo}"
    rounded: "{rounded.xl}"
    padding: "10px 12px 8px"
  button-chapa:
    backgroundColor: "{colors.chapa}"
    textColor: "{colors.tubo}"
    typography: "{typography.title}"
    rounded: "{rounded.lg}"
    padding: "0 24px"
    height: "48px"
  button-canto:
    backgroundColor: "{colors.chapa}"
    textColor: "{colors.tubo}"
    typography: "{typography.canto}"
    rounded: "{rounded.md}"
    padding: "8px 14px"
    height: "44px"
  button-canto-quiet:
    backgroundColor: "transparent"
    textColor: "{colors.tubo}"
    typography: "{typography.canto}"
    rounded: "{rounded.md}"
    padding: "8px 14px"
    height: "44px"
  toggle-zocalo:
    backgroundColor: "transparent"
    textColor: "{colors.zocalo}"
    rounded: "{rounded.md}"
    padding: "6px 10px"
  toggle-zocalo-on:
    backgroundColor: "{colors.zocalo}"
    textColor: "{colors.tubo}"
  formica-mesa:
    backgroundColor: "{colors.formica}"
    textColor: "{colors.formica-ink}"
    rounded: "{rounded.xl}"
    padding: "12px 24px 16px"
  banda-accion:
    backgroundColor: "{colors.zocalo}"
    textColor: "{colors.tubo}"
    rounded: "{rounded.xl}"
    padding: "10px 12px 12px"
  papel:
    backgroundColor: "{colors.naipe}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.lg}"
    padding: "16px"
  panel-analisis:
    backgroundColor: "{colors.zocalo-deep}"
    textColor: "{colors.tubo}"
    rounded: "{rounded.xl}"
    padding: "12px 16px"
  input-semilla:
    backgroundColor: "{colors.tubo}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.md}"
    padding: "10px 12px"
  naipe-mano:
    backgroundColor: "{colors.naipe}"
    rounded: "{rounded.naipe}"
    width: "4.9rem"
  dorso:
    backgroundColor: "{colors.chapa}"
    rounded: "{rounded.naipe}"
    width: "2.25rem"
---

# Design System: Truco Bot

## Overview

**Creative North Star: "Sede del club de barrio"**

La partida se juega en la mesa de fórmica celeste de la sede del club, bajo la luz blanca del tubo, con el tanteador de chapa bordó colgado en la pared. Todo el sistema sale de esos materiales: la pared blanca con zócalo verde inglés, la fórmica moteada con canto de aluminio, la chapa esmaltada con remaches, el naipe blanco y el papel del anotador. No hay superficie que no sea uno de esos objetos.

La densidad es de mesa, no de tablero: una columna central (tanteador, dorsos del rival, fórmica con tres bazas, banda verde con cantos y la mano propia) y, en escritorio, el anotador de papel a la izquierda y el panel de análisis a la derecha. La tipografía es una sola familia, Archivo, que cambia de ancho según el objeto: expandida y negra para los rótulos pintados de chapa, condensada para los números del tanteador y de los naipes, normal para el texto.

El sistema rechaza el paño verde de casino y la botonera de formulario: los cantos son chapitas esmaltadas con la frase entre comillas, y la acción principal es tocar una carta.

**Key Characteristics:**
- Materiales con nombre propio: pared (tubo + zócalo), fórmica, chapa, aluminio, naipe, tinta.
- Una sola familia tipográfica variable en ancho (Archivo, `wdth` 75 a 125).
- Bordó de chapa como único color de acción; verde zócalo como banda de turno y estado.
- Naipes y palos dibujados en SVG propio, con los cuatro colores de palo reservados al naipe.
- Movimiento físico y corto: la carta viaja a su baza, los números giran como placas.

## Colors

Paleta de sede de club: blancos fríos de tubo, un celeste agua de fórmica, verde inglés de zócalo y un único bordó de chapa, con los cuatro colores de palo encerrados en el naipe.

### Primary
- **Bordó chapa** (chapa): el tanteador, los dorsos, los botones de canto y toda acción principal ("Repartir", "Repartir la siguiente", "Otra partida"). También el anillo de foco, la selección de texto, el anillo del rival elegido y los mensajes de error.

### Secondary
- **Verde zócalo** (zocalo): la franja inferior de la pared, la banda de turno donde viven los cantos y la mano propia, el sello "Tuya" de la baza, el toggle de análisis prendido y los textos de enlace ("Levantarse"). También es el `theme-color` del navegador.
- **Verde zócalo hondo** (zocalo-deep): fondo del panel "Cómo decide", el único panel oscuro.

### Tertiary
- **Celeste fórmica** (formica): la superficie de la mesa y la barra de la acción elegida en el análisis.
- **Tinta de fórmica** (formica-ink): todo texto y trazo apoyado sobre la fórmica (rótulos de baza, línea de estado, huecos punteados, sello "Parda").

### Neutral
- **Blanco tubo** (tubo): fondo de la pared y del cuerpo; texto sobre chapa y zócalo.
- **Aluminio** (aluminio): el canto de la fórmica y los remaches de la chapa.
- **Aluminio oscuro** (aluminio-dark): la arista inferior del canto y el color de la barra de scroll.
- **Blanco naipe** (naipe): naipes, globo de canto del rival, tarjetas de rival y el papel del anotador.
- **Tinta** (tinta): texto base y la línea que separa pared de zócalo.

### Colores de palo
- **Oro** (oro), **Copa** (copa), **Espada** (espada), **Basto** (basto): solamente dentro del naipe (marco, números, dibujo del palo) y en la fila de palos de la cartelera.

### Named Rules
**The Una Chapa Rule.** El bordó es el color de lo que se toca o se canta. Si algo es bordó y no es tanteador, dorso, acción o error, sobra.

**The Palo Encerrado Rule.** Oro, copa, espada y basto no salen del naipe: no se usan para estados, gráficos ni interfaz.

## Typography

**Display Font:** Archivo (con ui-sans-serif, system-ui, sans-serif)
**Body Font:** Archivo (misma familia)

**Character:** Una grotesca argentina (Omnibus-Type) usada como letrista de club: ancha y negra para lo pintado, angosta para los números, neutra para leer. El eje `wdth` hace el trabajo que en otro sistema haría una segunda familia.

### Hierarchy
- **Display** (900, 2.25rem, 1, ancho 125%, mayúsculas): el nombre "Truco Bot" pintado en la chapa de la cartelera.
- **Score** (800, 2.25rem en móvil y 3rem desde `sm`, 1, ancho 75%, cifras tabulares): los números del tanteador.
- **Headline** (800, 1.125rem, tracking 0.08em, ancho 115%, mayúsculas): encabezados de sección de pantalla ("¿Contra quién jugás?").
- **Title** (800, 1.25rem, ancho 110%): nombre de cada rival. Los botones de acción principal usan este peso en 1.125 a 1.25rem, mayúsculas, tracking 0.06em y ancho 115%.
- **Canto** (750, 0.95rem, ancho 105%): la frase de cada canto, siempre entre comillas angulares.
- **Body** (400 a 500, 0.875rem a 1rem, interlineado 1.625): descripciones, anotador, mensajes.
- **Label** (800, 0.7rem, tracking 0.14 a 0.18em, ancho 125%, mayúsculas): rótulos pintados del tanteador ("Nosotros", nombre del bot), rótulos de baza y títulos de panel ("Anotador", "Cómo decide").
- **Card index** (750, 1.5rem en la mano y 1rem a 1.25rem en la baza, ancho 80%): el número del naipe, en el color de su palo.

### Named Rules
**The Un Eje Rule.** No se agrega otra familia. La jerarquía se arma con peso y ancho de Archivo: expandido para rótulos, condensado para números.

**The Cifra Tabular Rule.** Todo número va en cifras tabulares (`font-variant-numeric: tabular-nums` en el cuerpo), para que tanteador, porcentajes y semilla no bailen.

## Layout

Mobile first en una columna. La pantalla completa es la pared: fondo blanco tubo con el zócalo verde de 4.5rem anclado al pie, separado por una línea de tinta de 3px.

- **Cartelera** (sin partida): columna centrada de ancho máximo 28rem (`max-w-md`), con la chapa del título arriba, la lista de rivales y el papel de semilla con el botón "Repartir".
- **Mesa**: contenedor de hasta 88rem con márgenes de 12px en móvil y 20px desde `sm`. En `lg` pasa a tres columnas (17rem, flexible, 19rem) con 24px de separación: anotador a la izquierda, mesa al centro, análisis a la derecha. En móvil el orden es mesa, análisis (solo si está prendido) y anotador.
- La columna central apila tanteador, dorsos con globo de canto, fórmica con tres bazas en grilla de tres columnas y la banda verde de turno, con 12px entre bloques (10px en `lg`).
- El ritmo usa pasos de 4px: 4, 8, 12, 16, 24 y 32px.
- Los objetivos táctiles de canto miden 44px de alto como mínimo; los de acción principal, 48px.

## Elevation & Depth

La profundidad es física y de objeto: cada material proyecta la sombra que tendría bajo el tubo, y la sombra siempre es suave y hacia abajo. No hay capas flotantes ni desenfoques de vidrio. La fórmica suma un bisel (brillo interior y arista de aluminio oscuro) porque es la única superficie con canto.

### Shadow Vocabulary
- **Caída de chapa** (`box-shadow: 0 4px 8px -3px rgb(0 0 0 / 0.4)`): tanteador, chapa del título, cantos y botones de acción.
- **Canto de fórmica** (`box-shadow: inset 0 0 0 1px rgb(255 255 255 / 0.35), 0 1px 0 1px #7d868a, 0 16px 26px -14px rgb(21 58 44 / 0.6)`): la mesa.
- **Naipe apoyado** (`box-shadow: 0 2px 0 rgb(0 0 0 / 0.08), 0 8px 14px -8px rgb(15 59 53 / 0.7)`): naipes boca arriba.
- **Papel** (`box-shadow: 0 10px 20px -14px rgb(0 0 0 / 0.8)`): anotador, papel de semilla, panel de análisis y tarjetas de rival (variante `0 6px 14px -10px`).
- **Globo** (`box-shadow: 0 6px 12px -8px rgb(0 0 0 / 0.7)`): el globo del canto del rival y los dorsos.

### Named Rules
**The Sombra de Tubo Rule.** Toda sombra cae recta hacia abajo con desenfoque y dispersión negativa. Nunca una sombra dura desplazada ni un resplandor de color.

## Shapes

Esquinas de objeto real, no de interfaz: 12px para las superficies grandes (fórmica, tanteador, anotador, banda de turno), 8px para tarjetas y botones de acción, 6px para cantos y campos, 2px para los sellos de resultado. El naipe tiene su propia curva elíptica (10% / 6%) y proporción 5:8, que se repite en los huecos punteados de las bazas vacías. Los remaches son círculos de 6px en las esquinas de la chapa. El globo del rival es un bocadillo de 16px con la esquina inferior izquierda recortada a 2px, apuntando a los dorsos.

## Components

### Buttons
Chapitas esmaltadas: planas, pintadas, con sombra de caída.
- **Shape:** 8px en acciones principales, 6px en cantos.
- **Primary (chapa):** fondo bordó, texto tubo, mayúsculas expandidas, alto mínimo 48px, ancho completo en la cartelera.
- **Canto:** chapa con la frase de la API entre comillas angulares («Truco»), alto mínimo 44px, en fila que se envuelve y centra.
- **Canto silencioso:** "Me voy al mazo" va sin relleno, texto tubo y anillo tubo al 55%; se distingue del resto sin volverse invisible.
- **Hover / Focus / Active:** hover sube el brillo al 110%; active baja 1px; disabled a 50 a 55% de opacidad. El foco es siempre el contorno bordó de 3px con 3px de separación.
- **Enlace:** "Levantarse" y "Cambiar de rival" son texto subrayado (verde zócalo sobre la pared, tubo sobre la banda) que pasa a bordó en hover.

### Chips
- **Toggle de análisis:** anillo verde zócalo al 50% y texto zócalo apagado; prendido pasa a fondo zócalo con texto tubo. El texto dice el estado ("Análisis prendido").
- **Sello de baza:** mayúsculas de 0.65rem sobre 2px de radio; "Tuya" en zócalo, "Del rival" en chapa, "Parda" con borde punteado en tinta de fórmica.

### Cards / Containers
- **Fórmica:** la mesa. Celeste moteado con ruido fractal (dos capas SVG), reflejo diagonal del tubo, canto de aluminio de 3px y 12px de radio. Todo lo que se apoya encima usa tinta de fórmica.
- **Banda de turno:** verde zócalo, 12px, aloja el estado ("Te toca."), los cantos y la mano propia.
- **Papel:** blanco naipe, 8 a 12px, anillo negro al 10% y sombra de papel. Anotador, semilla y tarjetas de rival.
- **Panel de análisis:** zócalo hondo, texto tubo, filas de probabilidad con barra de 10px: la acción elegida en celeste fórmica, el resto en tubo al 45%, porcentaje con un decimal.

### Inputs / Fields
- **Style:** fondo blanco tubo sobre papel, 6px de radio, anillo negro al 15%, 10px por 12px de relleno, texto de 1rem.
- **Focus:** el contorno bordó global.
- **Error:** mensaje en bordó, peso 650, debajo del campo; `aria-invalid` en el campo.

### Tanteador
La chapa bordó de la pared, a todo el ancho de la columna, con cuatro remaches de aluminio. Dos columnas (Nosotros | rival) con rótulo expandido, número condensado y los palitos del tanteo de mesa (cuadrados de cinco con diagonal) dibujados en SVG; al centro "a 15" y el número de mano, separados por un filete de tubo al 40%. Cada vez que un número cambia, gira como una placa (`rotateX` a 90° y vuelta, 520ms).

### Naipe
Blanco naipe en proporción 5:8 con marco fino del color del palo; las interrupciones del marco dicen el palo (oro 0, copa 1, espada 2, basto 3). Número arriba a la izquierda y abajo a la derecha en ancho 80%, palo dibujado al centro. Tres tamaños: mano (4.9rem, 6rem desde `sm`), baza (3.3rem a 4.6rem) y dorso (2.25rem a 2.75rem). El dorso es chapa bordó con guarda de rombos en tubo al 16%. La mano propia se abre en abanico (−4°, 0°, 4°) y la carta jugable sube 8px en hover o foco.

### Viaje de la carta
La carta jugada viaja desde la mano (o desde los dorsos del rival) hasta su baza con FLIP: sale girada −7°, se pasa a 1.5° y 102% al 82% del recorrido y se asienta, en 520ms con `cubic-bezier(0.16, 1, 0.3, 1)`. El globo del canto y los sellos de baza entran en 260ms subiendo 6px. Con `prefers-reduced-motion` no hay viaje, ni placa, ni globo.

## Do's and Don'ts

### Do:
- **Do** nombrar cada superficie por su material (pared, fórmica, chapa, papel, naipe) y usar solo los colores de ese material.
- **Do** reservar el bordó chapa para tanteador, dorsos, cantos, acciones principales, foco y error.
- **Do** escribir los cantos con el texto que manda la API, entre comillas angulares («»).
- **Do** usar Archivo con el eje de ancho: 125% en rótulos pintados, 75 a 80% en números, normal en texto.
- **Do** mantener 44px de alto mínimo en cantos y 48px en acciones principales.
- **Do** dibujar palos, palitos y remaches en SVG o CSS propio.
- **Do** apagar viaje, placa y globo con `prefers-reduced-motion`.

### Don't:
- **Don't** usar paño verde de casino ni texturas de fieltro para la mesa: la mesa es fórmica celeste.
- **Don't** armar la botonera como un formulario de botones grises; cada canto es una chapita, y el único canto sin relleno es el silencioso ("Me voy al mazo").
- **Don't** usar los colores de palo fuera del naipe.
- **Don't** agregar una segunda familia tipográfica.
- **Don't** usar sombras duras desplazadas ni resplandores de color; la luz es la del tubo, de arriba.
- **Don't** usar imágenes de terceros para cartas o palos.
