# Prompt — sistema visual de VERTEX 4D

> Especificación completa: colorimetría, tipografía, iconografía, movimiento y
> componentes. Autocontenida: se puede entregar a otra persona, otro agente o
> llevar a otro producto sin más contexto.
> Todos los ratios de contraste están medidos, no estimados.

---

## 1. Qué tiene que hacer este diseño

VERTEX 4D enseña a founders a leer una idea como sistema, comportamiento y
números antes de comprometer recursos. El recorrido es
`Problema → Sistema → Comportamiento → Números → Decisión`.

Tres consecuencias que mandan sobre todo lo demás:

1. **El color significa, no decora.** Cada tono está atado a un estado real de un
   artefacto. Si un color se usa por gusto, deja de poder leerse como señal.
2. **Se usa durante horas.** Es una herramienta de trabajo en cohortes de un día
   completo, no una landing. La legibilidad sostenida gana sobre el impacto.
3. **Público neurodivergente explícito.** El movimiento y la densidad se diseñan
   para sostener la atención, no para capturarla.

---

## 2. Colorimetría

### Paleta base — invariante entre temas

| Rol | Hex | Uso |
| --- | --- | --- |
| Acción | `#5b13ec` | Botones, rellenos, "ahora" |
| Hipótesis | `#B2A4FF` | Lo que aún no está probado |
| Riesgo | `#FF6B6B` | Lo que puede tumbar el modelo |
| Evidencia | `#66FFB2` | Lo que se sostiene con datos |

**Semántica obligatoria:** evidencia = mint · hipótesis = lavender ·
riesgo = coral · acción y "ahora" = morado. No se reasignan.

### Tema oscuro — el principal

```css
--bg:    #161022    /* fondo */
--bg2:   #0f0a1a    /* fondo de página, por debajo */
--fg:    #E4DFF2    /* texto primario */
--fg2:   #B6ACD2    /* texto secundario */
--fg3:   #958bb4    /* texto terciario */
--act:   #B2A4FF    /* acción como TEXTO */
--actfill: #5b13ec  /* acción como RELLENO, con texto blanco */
--glass:  rgba(178,164,255,.07)   /* superficie */
--glass2: rgba(178,164,255,.11)   /* superficie elevada */
--edge:   rgba(178,164,255,.20)   /* borde */
--edge2:  rgba(178,164,255,.32)   /* borde enfatizado */
--track:  rgba(178,164,255,.14)   /* canal de barra */
```

### Tema claro — de primera clase, no un respaldo

```css
--bg:    #f6f6f8    --fg:  #1A1A1A
--bg2:   #ececf1    --fg2: #55505f
--act:   #5b13ec    --fg3: #6B6B73
--glass:  rgba(255,255,255,.72)
--glass2: rgba(255,255,255,.92)
--edge:   rgba(26,26,26,.10)
--edge2:  rgba(91,19,236,.28)
```

### La regla que no se rompe

**Mint, coral y lavender solo cargan texto sobre fondo oscuro.** Sobre el fondo
claro no llegan ni a la mitad del mínimo:

| Acento sobre `#f6f6f8` | Ratio | Necesita |
| --- | --- | --- |
| mint `#66FFB2` | **1.18** | 4.5 |
| lavender `#B2A4FF` | **2.02** | 4.5 |
| coral `#FF6B6B` | **2.57** | 4.5 |

En tema claro pasan a ser **relleno con tinta oscura encima**:

| Relleno | Tinta | Ratio |
| --- | --- | --- |
| `#66FFB2` evidencia | `#0c3d26` | 9.65 |
| `#B2A4FF` hipótesis | `#241a52` | 7.17 |
| `#FF6B6B` riesgo | `#4d1414` | 5.31 |

Y el morado `#5b13ec` es lo contrario: **2.43 sobre oscuro**, inservible como
texto ahí; es relleno con blanco encima (**7.64**). Sobre claro sí lee como
texto (**7.08**).

### Contraste verificado

**Sobre `#161022`:** fg 14.26 · fg2 8.68 · fg3 5.86 · acción 8.53 · evidencia
14.6 · riesgo `#FF8C8C` 8.29
**Sobre `#f6f6f8`:** fg 16.12 · fg2 7.21 · fg3 4.89 · acción 7.08 · evidencia
`#0a7346` 5.48

**El texto primario no es blanco puro.** Blanco sobre `#161022` da 18.6:1 y
produce halación: el texto vibra y cansa en jornadas largas. `#E4DFF2` da 14.26,
se lee igual de bien y descansa. Para uso prolongado, menos contraste es mejor
mientras no baje del mínimo.

**Objetivo del sistema:** cero pares por debajo de AA en ambos temas. La
implementación actual mide 30/30 rutas limpias, peor par 4.89:1.

---

## 3. Tipografía

| Rol | Familia | Dónde |
| --- | --- | --- |
| Display | **Bricolage Grotesque** 500–800 | h1–h3, cifras grandes |
| Cuerpo | **Manrope** 400–800 | Todo el texto de interfaz |
| Datos | **JetBrains Mono** 500–700 | IDs, cifras, etiquetas de 1–2 palabras |

Bricolage Grotesque es una grotesca variable con carácter — la elección busca
personalidad sin parecer chiste, y explícitamente **no** las fuentes por defecto
de todo mockup generado.

### Escala

```
título de página   clamp(28px, 3.4vw, 43px)   peso 800, tracking -1.3px
encabezado sección 16–20px                     peso 600
cuerpo             13.5–14.5px                 interlineado 1.6–1.68
etiqueta mono      10.5–11px
cifra grande       clamp(38px, 4.4vw, 60px)    peso 800, tracking -2.6px
```

### Reglas de legibilidad

- **Nada por debajo de 10px.** Ni siquiera etiquetas.
- **Sin mayúsculas ni tracking abierto en texto de más de dos palabras.** Eso se
  lee bien en un cartel y agota en una jornada.
- **El mono solo donde gana**: identificadores, cifras, etiquetas cortas. Nunca
  párrafos.
- El interlineado del cuerpo no baja de 1.6.

---

## 4. Espacio, radio y elevación

```css
--radius:      16px   /* paneles */
--radius-ui:   11px   /* botones, inputs */
--radius-chip:  8px   /* chips */
/* los círculos siguen siendo círculos: 999px */
```

Tres radios, no uno: un valor plano para todo aplana la jerarquía.

```css
--shadow: 0 24px 80px rgba(0,0,0,.32), inset 0 1px 0 rgba(255,255,255,.04);
```

Superficies de vidrio: `backdrop-filter: blur(18px) saturate(1.06)` sobre
`--glass`, con borde `--edge`.

---

## 5. Iconografía

Set propio de 39 símbolos. Rejilla 24, trazo **1.75**, extremos y uniones
redondeados, sin relleno, `currentColor`. Sprite inline por página, no externo,
para que `currentColor` y el dimensionado en CSS funcionen sin depender del
soporte de `<use>` entre documentos.

**El principio de dibujo: cada icono representa lo que la cosa hace, no una
metáfora prestada.**

| Icono | Qué dibuja |
| --- | --- |
| Marca | El vértice: dos líneas que se encuentran en un punto |
| Alex | Dos corchetes cerrándose sobre el problema real |
| SynapMap | Un núcleo y sus relaciones, deliberadamente asimétrico |
| Aprobación | Una compuerta: solo pasa lo que sostienes |
| D-Predict | Una trayectoria que se abre en adopción, duda y resistencia |
| Billie | La curva cruzando el punto de equilibrio |
| DecisionRecord | La cadena sellada |

Tamaños en `em` para que acompañen a la tipografía: `1.15em` base, `1.5em`,
`2em`. Los iconos decorativos llevan `aria-hidden="true"`; los que son el único
contenido de un control necesitan nombre accesible.

---

## 6. Movimiento

Tres niveles vía `data-motion` en `<html>`: `full` · `reduced` · `none`.
`prefers-reduced-motion` manda en la primera carga; el control en pantalla puede
sobrescribirlo, porque casi nadie encuentra el ajuste del sistema. La preferencia
se guarda **por usuario**, no por sesión.

### Qué hay

- **Entrada escalonada** en orden de lectura: barra 0ms → cabecera 60ms → eje
  115ms → contenido 130/175/215ms, 300ms cada bloque. En una app de recargas
  completas es el movimiento de mayor valor: avisa de que la vista cambió y guía
  el ojo a dónde empezar a leer.
- **La barra de progreso crece desde cero** hasta el valor real, 720ms. En CSS,
  no en JS: `requestAnimationFrame` no dispara si la pestaña carga en segundo
  plano y la barra se quedaría vacía.
- **Cue de llegada**: el punto de la etapa activa respira **exactamente 3 veces**
  y se detiene.
- **Feedback de acción** al pulsar, y un destello único al guardar.

### Reglas

- **De una sola vez, nunca en bucle.** Una señal que no para es una señal que hay
  que ignorar activamente, y eso consume justo el recurso que se quiere proteger.
- **El movimiento nunca es la única señal.** Con `none` todo debe entenderse por
  color, posición, peso y texto.
- En `reduced`, solo opacidad: nada viaja por el campo visual (trastornos
  vestibulares).
- **Prohibido**: parallax, autoplay, brillos que laten, transiciones entre
  pantallas, y **cifras contando hasta su valor** — retrasan la lectura del dato
  y desvían la atención al movimiento.

### Modo enfoque

Atenúa lo que no es la tarea actual al 34% con `saturate(.45)`, y la enmarca con
contorno. **Atenúa, no oculta**, para que nadie pierda el hilo de dónde está. Es
el apoyo de atención más fuerte del sistema, y no es una animación.

---

## 7. Componentes

**Barra** — marca a la izquierda, identificador del run al centro, controles de
tema/movimiento/enfoque a la derecha. Se ancla al encabezado; nunca flota sobre
el contenido.

**Cabecera** — grid `1fr | 218px`: a la izquierda eyebrow de etapa, título,
entradilla y **una sola acción siguiente** con estimación de tiempo al lado. A la
derecha, riel de contadores. La estimación de tiempo no es adorno: la ceguera
temporal estorba más que la navegación.

**Eje del Golden Path** — pista de 3px con knobs de 14px en seis estaciones. La
actual marcada `aquí estás`. Es el ancla de "dónde estoy", idéntica y en el mismo
sitio en todas las pantallas.

**Panel de registro** — lista donde cada entrada lleva **barra de señal de color
a la izquierda** (4px) y **chip de estado a la derecha**. Es el patrón para
supuestos, stakeholders, hipótesis y riesgos.

**Panel de lectura** — cifra grande, la comparación contra la intuición previa, y
medidores de 7px.

**Bloque de veredicto** — franja morada con la decisión, y a la derecha tres
columnas: *por qué sí* (mint) · *pero* (coral) · *qué medir* (lavender).

---

## 8. Lo que este sistema deliberadamente no tiene

Estas ausencias son decisiones, no omisiones:

- **Degradados en texto**, blobs de glow radial y retículas de tarjetas iguales.
  Son los tics que hacen que una interfaz se lea como generada de fábrica.
- **Blanco puro como texto** sobre fondo oscuro.
- **Movimiento ambiental** de cualquier tipo.
- **Un solo radio** para todo.
- **Iconos de biblioteca.** El set es propio porque los símbolos de etapa tienen
  que representar un método que no existe fuera de este producto.

---

## 9. Cómo verificar

Contraste y layout son medibles; el gusto no. Mide siempre sobre pares
renderizados, no sobre tokens sueltos.

**Objetivos:** cero pares bajo AA en ambos temas · cero desbordes horizontales,
recortes, solapamientos o texto fuera de pantalla a 1440 / 1024 / 390 px · nada
bajo 10px · ninguna animación infinita.

**Cinco trampas que producen falsos positivos:**

1. `color-mix()` computa a `color(srgb 0.96 …)` con valores **0–1**, no 0–255.
2. Un modal `fixed` con z-index alto tapa la página a propósito: compara solo
   elementos de la misma capa de apilamiento.
3. Las animaciones y transiciones **se congelan si la página no compone
   fotogramas**. Antes de medir: `document.getAnimations().forEach(a=>a.finish())`
   o pon `data-motion="none"`.
4. Un `<style>` inline en la plantilla se carga **después** de la hoja enlazada y
   gana a igual especificidad. Duplica la clase en el selector antes de recurrir
   a `!important`.
5. Un riel de navegación estrecho de alto completo es intencional, no un panel
   vacío.
