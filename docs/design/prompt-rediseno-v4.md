# Prompt — aplicar el rediseño v4 a VERTEX 4D

> Copia todo lo que sigue como mensaje inicial de una sesión nueva.

---

Trabaja en `C:\Apps\Srsly Labs\srsly-labs-app` (FastAPI + Starlette SessionMiddleware +
Jinja2Templates, arranca con `python -m uvicorn main:app --port 8001`).

Quiero aplicar un rediseño visual completo. La maqueta de referencia, ya aprobada, está en
`vertex_propuesta_v4.html` (te la paso aparte o búscala en el scratchpad de la sesión anterior).
Ábrela y úsala como fuente de verdad para tokens, tipografía, componentes y comportamiento.

## Qué NO tocar

El pasillo de contratos ya está terminado y verificado. No modifiques:

- `contracts/v1/*.schema.json`, `contracts_runtime.py`, `artifacts.py`
- las rutas ni la lógica de `main.py` (solo su HTML/plantillas si hace falta)
- `scripts/validate_contracts.py` ni `scripts/smoke_vertex_golden_path.py`

Ambos scripts deben seguir pasando al terminar. Son la red de seguridad.

## 1. Reemplazar la paleta

Hoy la app usa un sistema crema/tinta (`--v4d-paper`, `--v4d-ink`, `--v4d-cobalt`…) en
`static/css/vertex4d.css`. **Conserva el mecanismo de tokens, cambia los valores** y añade
tema claro/oscuro real con `data-theme` en `<html>`.

```css
:root{
  --primary:#5b13ec; --lav:#B2A4FF; --coral:#FF6B6B; --mint:#66FFB2;
}
[data-theme="dark"]{
  --bg:#161022; --bg2:#0f0a1a;
  --glass:rgba(178,164,255,.07); --glass2:rgba(178,164,255,.11);
  --edge:rgba(178,164,255,.20);  --edge2:rgba(178,164,255,.32);
  --fg:#E4DFF2; --fg2:#A79CC4; --fg3:#8A80A6;
  --act:#B2A4FF; --actfill:#5b13ec; --acttext:#fff;
  --track:rgba(178,164,255,.14); --ok:#66FFB2;
}
[data-theme="light"]{
  --bg:#f6f6f8; --bg2:#ececf1;
  --glass:rgba(255,255,255,.72); --glass2:rgba(255,255,255,.92);
  --edge:rgba(26,26,26,.10);     --edge2:rgba(91,19,236,.28);
  --fg:#1A1A1A; --fg2:#55505f; --fg3:#6B6B73;
  --act:#5b13ec; --actfill:#5b13ec; --acttext:#fff;
  --track:rgba(26,26,26,.09); --ok:#0a7346;
}
```

**Regla de color que no se rompe:** mint, coral y lavender **solo pueden cargar texto sobre
fondo oscuro**. Sobre el fondo claro dan 1,2 / 2,6 / 2,0 a 1 y reprueban. En tema claro pasan
a ser relleno de chip con texto oscuro encima (`#0c3d26`, `#4d1414`, `#241a52`), y quien lee
es `--fg` o el morado `#5b13ec` (7,1:1).

`#5b13ec` sobre oscuro da 2,43:1: nunca como texto ahí. Es color de acción — botones y
rellenos, siempre con texto blanco encima (7,6:1).

**El color significa algo, no decora:** mint = evidencia · lavender = hipótesis ·
coral = riesgo · morado = acción y "ahora". Respeta esa semántica en toda la app; ya coincide
con los estados reales de los artefactos.

## 2. Tipografía

Sustituye la pareja actual (Source Serif 4 + Inter) por:

- **Bricolage Grotesque** — display: `h1`–`h3`, cifras grandes
- **Manrope** — cuerpo e interfaz
- **JetBrains Mono** — solo IDs, cifras y etiquetas de una o dos palabras

Carga las tres con un solo `@import` en `vertex4d.css`, que es la hoja que enlazan todas las
páginas. Elimina cualquier otro `<link>` a Google Fonts salvo Material Symbols.

Cuerpo a 13,5–14,5 px con `line-height` 1,6. **Nada de mayúsculas ni `letter-spacing` abierto
en texto de más de dos palabras** — eso es lo que provocó la queja de fatiga visual.

## 3. Capa de accesibilidad atencional

Es requisito, no adorno. Añade `static/js/prefs.js` y dos atributos en `<html>`:
`data-motion="full|reduced|none"` y `data-focus="on|off"`.

- `prefers-reduced-motion` **manda en la primera carga**; el control en pantalla puede
  sobrescribirlo, porque casi nadie encuentra el ajuste del sistema.
- Movimiento **de una sola vez al cambiar de estado. Cero bucles.** La señal de llegada de la
  etapa activa respira exactamente 3 veces y se detiene (`animation: breathe 1.6s ... 3`).
  Una señal que nunca para hay que ignorarla activamente, y eso cansa más de lo que ayuda.
- **El movimiento nunca es la única señal.** Con `data-motion="none"` todo debe seguir
  entendiéndose por color, posición, peso y texto ("aquí estás").
- **Modo enfoque:** `[data-focus="on"] .dim { opacity:.34; filter:saturate(.45) }`. Atenúa,
  no oculta, para que nadie pierda el hilo. La tarea actual lleva `.focusable` con contorno.
- Prohibido: parallax, autoplay, brillos que laten, contadores que suben solos, transiciones
  entre pantallas, y cualquier cosa que se mueva mientras se lee.

**Persiste las preferencias por usuario**, no por sesión: guarda `theme`, `motion` y `focus`
en `team_members` (o una tabla `user_prefs`) y aplícalas al renderizar. Alguien que necesita
movimiento cero no debe pedirlo cada vez que entra.

## 4. Unificar el CSS disperso

Hoy hay ~36 KB de CSS inline contra 24 KB compartido, y `billie.html`, `golden_path.html`,
`how_vertex_thinks.html`, `start_golden_path.html`, `d_predict.html`, `decision_record.html`,
`assumption_approval.html` y `facilitator.html` redeclaran cada uno un `:root` privado con el
hex de marca escrito a mano como fallback.

Extrae a `vertex4d.css` un juego único de tokens y componentes compartidos —`.panel`, `.btn`,
`.chip`, `.item`, `.track`, `.meter`— y borra los prefijos privados (`.sgp-`, `.think-`,
`.gp-`, `--c`, `--m`). Las páginas Tailwind deben leer los mismos tokens.

## 5. Aplicar por pantalla

Prioridad, de mayor a menor valor:

1. `templates/lab/start_golden_path.html` — es la puerta de entrada
2. `templates/lab/billie.html` + `static/js/billie.js` — el momento "wow"
3. `templates/lab/d_predict.html`, `decision_record.html`, `assumption_approval.html`
4. `templates/lab/alex.html`, `synapmap.html` — **conserva su responsive actual**: por debajo
   de `lg` apilan en una columna y hacen scroll; por encima mantienen 4/8 y 3/6/3 sin scroll
5. `templates/facilitator.html`, `dashboard/*`, `index.html`, `auth/*`

## Verificación

1. `python scripts\validate_contracts.py` — 25 negativos en verde
2. `python scripts\smoke_vertex_golden_path.py` — cadena completa
3. Las 21 rutas devuelven 200
4. **Contraste medido en el navegador, en los dos temas**, recorriendo cada par real de
   texto/fondo y componiendo las capas translúcidas. Objetivo: cero fallos AA.
   Referencia de la maqueta: oscuro mínimo 4,54:1 · claro mínimo 4,89:1.
5. Con `data-motion="none"`, toda la información sigue siendo comprensible
6. La animación de etapa activa tiene `animation-iteration-count: 3`, nunca `infinite`
7. A 375 px, Alex y SynapMap sin desbordamiento horizontal; a 1280 px sin scroll de página

**Advertencia de medición:** las transiciones y el cambio de tema no se resuelven al instante.
Si mides `getComputedStyle` justo después de un clic vas a leer valores a medio camino. Espera
a que terminen, o desactiva la transición antes de leer el estado final.

Trabaja en una rama nueva y haz commits por fase (tokens → tipografía → accesibilidad →
unificación → pantallas), para poder revertir una sin perder las demás.
