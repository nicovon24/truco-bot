---
version: 1
slug: "src-app-page-tsx"
primary_target: "src/app/page.tsx"
related_targets: []
---

# Mesa de juego (`/`)

Modo: Operate. Audiencia: jugadores de truco y gente técnica curiosa (PRODUCT.md). Tarea: elegir rival, jugar una partida a 15, leer cada canto del bot y, si se quiere, sus probabilidades. Restricción dura: el front renderiza solo la observación y las acciones legales de la API.

## Direction contract

THESIS: La partida se juega en la mesa de fórmica de la sede del club, bajo el tubo, con el tanteador de chapa en la pared. Rechaza el paño verde de casino y la botonera de formulario.

OWN-WORLD: Fórmica celeste agua (#8cc7bf) moteada, con canto de aluminio en bordes. Pared: zócalo verde inglés (#1e4d3b) abajo y blanco tubo (#e9eef0) arriba. Tanteador de chapa bordó (#7b1e2c) con números pintados en blanco. Naipes blancos con palo en SVG propio y dorso bordó con guarda. Cantos como chapitas esmaltadas con la frase entre comillas. Tipografía Archivo (Omnibus-Type, Buenos Aires): expandida y negra para rótulos, normal para el resto.

STORY: El jugador elige rival en la cartelera, se sienta, ve su mano abajo, canta o tira. El bot responde con frases citadas. Al cerrar la mano el tanteador suma y se pide la siguiente. En modo análisis ve la barra de probabilidades de cada decisión del bot.

FIRST VIEWPORT: En móvil (390), arriba el tanteador de chapa NOSOTROS | ELLOS a todo el ancho con números grandes. Debajo, los dorsos del rival y su último canto citado. Al centro la fórmica con las tres bazas en columnas, con resultado sellado. Abajo, las chapitas de cantos legales y tus tres cartas grandes: la acción principal es tocar una carta. En escritorio suma el anotador a la izquierda y el análisis a la derecha.

FORM: Sede del club de barrio, candidato 7 de 7 de la lista propia, seed c3ca7f9f. Interacción firma: la carta viaja de la mano a su baza y se asienta; los números del tanteador giran como placas de chapa al sumar.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
