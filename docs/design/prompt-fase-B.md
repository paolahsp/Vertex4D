# Prompt — reconstruir los cuerpos de pantalla de VERTEX 4D sobre la maqueta v4

> Copia todo lo que sigue como mensaje inicial de una sesión nueva.
> Adjunta también `vertex_propuesta_v4.html` (la maqueta aprobada).

---

Trabaja en `C:\Apps\Srsly Labs\srsly-labs-app`, rama **`agent/vertex-v4-redesign`**.
Stack: FastAPI + Starlette SessionMiddleware + Jinja2Templates. Arranca con
`python -m uvicorn main:app --host 127.0.0.1 --port 8001`. Sin variables de entorno
obligatorias para desarrollo.

Te adjunto `vertex_propuesta_v4.html`. **Es la fuente de verdad visual.** Ábrela y
úsala para composición, proporciones y vocabulario de componentes.

## Estado actual: qué YA está hecho — no lo rehagas

El sistema visual v4 está construido y verificado. Existe y funciona:

- **Tokens** de tema claro/oscuro vía `data-theme` en `<html>`, en `static/css/vertex4d.css`
- **Tipografía**: Bricolage Grotesque (display), Manrope (cuerpo/UI), JetBrains Mono
  (IDs, cifras, etiquetas cortas). Cargadas con un solo `@import`.
- **Capa de composición v4**: `.v4-bar`, `.v4-brand`, `.v4-tile`, `.v4-runtag`,
  `.v4-head`, `.v4-eyebrow`, `.v4-h1`, `.v4-lede`, `.v4-next`, `.v4-eta`,
  `.v4-tally`, `.v4-t`, `.v4-path`, `.v4-rowcap`, `.v4-track`, `.v4-stations`,
  `.v4-st`, `.v4-knob`
- **Eje del Golden Path** como parcial reutilizable:
  `{% with stage = N %}{% include "lab/_path_bar.html" %}{% endwith %}` (N = 1..6)
- **Iconografía propia**: `templates/_icon_sprite.html`, 39 símbolos, rejilla 24,
  trazo 1.75, `currentColor`. Uso: `<svg class="ic"><use href="#i-billie"/></svg>`.
  Tamaños: `.ic` (1.15em), `.ic-lg`, `.ic-xl`. Cero Material Symbols en la app.
- **Preferencias por usuario**: `static/js/prefs.js` monta el control en el
  encabezado y persiste tema/movimiento/enfoque en BD.
- **Capa de movimiento** (ver más abajo).
- **Versionado de assets**: `?v={{ asset_v }}` — no toques esto, resuelve el caché.

## Qué NO tocar

El pasillo de contratos está terminado y verificado. No modifiques:

- `contracts/v1/*.schema.json`, `contracts_runtime.py`, `artifacts.py`
- La lógica de rutas de `main.py`
- `scripts/validate_contracts.py`, `scripts/smoke_vertex_golden_path.py`

**Al recomponer una pantalla, conserva TODOS los hooks de JS**: `id`, `data-screen`,
`data-run-link`, `name` de formularios. El JS de cada pantalla los busca por selector.
Si renombras uno, la pantalla deja de funcionar sin dar error visible.

Ambos scripts deben pasar al terminar.

---

## El problema a resolver

El rediseño cubre solo el **marco** de cada pantalla. Medido como porcentaje de la
altura total de la página que es composición v4:

| Pantalla | Es maqueta hoy |
|---|---|
| DecisionRecord | 50% |
| D-Predict | 47% |
| Billie | 42% |
| Aprobación | 25% |
| Facilitador | 8% |
| Golden Path | 4% |
| Start Golden Path | 3% |
| 4D Lab, Dashboard, Alex, SynapMap | 0% |

Todo lo que hay debajo de la cabecera sigue siendo la app anterior con colores
nuevos. **Tu trabajo es el cuerpo, no el marco.**

## Los tres componentes de la maqueta que faltan

Constrúyelos en `static/css/vertex4d.css` como capa compartida, con prefijo `v4-`,
y luego aplícalos pantalla por pantalla.

### 1. Panel de registro (columna izquierda de la maqueta)

Lista de entradas donde cada una lleva una **barra de señal de color a la izquierda**
y un **chip de estado a la derecha**. Es el patrón para supuestos, stakeholders,
hipótesis y riesgos.

```
.v4-panel   fondo var(--glass), borde var(--edge), radio 16px, padding 20px,
            backdrop-filter blur(18px) saturate(1.1)
.v4-plabel  mono 10.5px color var(--fg3), margen inferior 15px
.v4-ask     display 20px peso 600, interlineado 1.25
.v4-item    grid 4px | 1fr | auto, gap 13px, align-items center,
            padding 12px 0, borde superior 1px var(--edge)
.v4-sig     ancho 4px, alto 100%, mínimo 30px, radio 3px
.v4-chip    mono 10.5px, padding 5px 9px, radio 7px, white-space nowrap
```

Semántica de color, **respétala**: mint = evidencia · lavender = hipótesis ·
coral = riesgo · morado = acción. En tema claro los acentos son **relleno con tinta
oscura encima** (`#0c3d26`, `#241a52`, `#4d1414`), nunca texto.

### 2. Panel de lectura (columna derecha)

```
.v4-num     display clamp(38px,4.4vw,60px), peso 800, letter-spacing -2.6px
.v4-num u   15px, color var(--fg3), sin subrayado  (la unidad)
.v4-shift   inline-flex, fondo var(--glass2), borde var(--edge),
            padding 7px 11px, radio 9px  ("Tu intuición decía X")
.v4-meters  grid, gap 12px
.v4-meter   etiqueta arriba (12px var(--fg2)) + valor a la derecha (mono 11px)
.v4-mt      alto 7px, radio 6px, fondo var(--track), overflow hidden
.v4-mt i    alto 100%, radio 6px, color según semántica
```

### 3. Bloque de veredicto

```
.v4-verdict  grid 196px | 1fr, borde var(--edge2), radio 16px,
             fondo var(--glass2), backdrop-filter blur(18px), overflow hidden
.v4-vl       padding 19px, fondo var(--actfill), color #fff
             (kicker mono 10px + h2 display 28px peso 800)
.v4-vr       padding 19px 20px, grid 3 columnas, gap 16px
             cada columna: h4 mono 10px + p 12.5px var(--fg2)
             "por qué sí" mint · "pero" coral · "qué medir" lavender
.v4-foot     grid-column 1/-1, borde superior, mono 10px var(--fg3)
```

---

## Fase B — Cuerpos, en el orden del recorrido de cohorte

Este es el orden elegido: es lo que un participante recorre de principio a fin en
noviembre. Haz **un commit por pantalla** para poder revertir una sin perder las demás.

### B1. Start Golden Path — `templates/lab/start_golden_path.html` (hoy 3%)
Es la puerta de entrada: lo primero que ve cualquiera. Hoy es un formulario largo
sin jerarquía. Objetivo: cabecera v4 con título y una sola acción siguiente clara,
el formulario de baseline dentro de `.v4-panel` agrupado en secciones legibles
(proyecto · privacidad · baseline de métricas), y el riel de contadores a la derecha.
Incluye el eje con `stage = 1`.
**Conserva** los `name` de todos los campos: el POST a `/api/vertex/runs` depende de
`baseline_problem_statement`, `baseline_stakeholders`, `baseline_intuition_price`,
`baseline_price_currency`, y de los campos de privacidad.

### B2. Alex — `templates/lab/alex.html` (hoy 0%)
Página Tailwind con chat + tarjeta de persona. Objetivo: barra v4, cabecera con
etapa 1, chat dentro de `.v4-panel`, y la tarjeta de persona convertida en panel de
registro con barra de señal. **Conserva** el responsive actual: por debajo de `lg`
apila en una columna y hace scroll; por encima mantiene 4/8 sin scroll de página.
Conserva `#chat-log`, `#start-session-btn`, `#display-role` y el modal de configuración.

### B3. SynapMap — `templates/lab/synapmap.html` (hoy 0%)
Igual que Alex: barra, cabecera etapa 2, paneles. El panel derecho de análisis está
vacío hasta que corre el mapa — dale un **estado vacío real** con texto, no un panel
en blanco. Conserva la rejilla 3/6/3 en escritorio y el `min-h-[420px]` del mapa en
móvil. Conserva `#system-map-svg`, `#chat-container` y el D3.

### B4. Aprobación — `templates/lab/assumption_approval.html` (hoy 25%)
Ya tiene el eje. Falta la cabecera v4 y, sobre todo, **el panel de registro**: es
literalmente la pantalla donde el founder marca qué supuestos sostiene. Cada supuesto
como `.v4-item` con barra de señal y chip. Conserva el POST a
`/api/vertex/runs/{run_id}/assumption-approvals` y los nombres de campo.

### B5. D-Predict — `templates/lab/d_predict.html` (hoy 47%)
Falta el par de paneles: registro de stakeholders a la izquierda, lectura a la
derecha. Conserva `#build-hypothesis`, `#save-hypothesis`, `#dp-status` y los cuatro
`#metric-*`.

### B6. Billie — `templates/lab/billie.html` (hoy 42%)
Falta el par de paneles y los tres medidores. El asistente de 24 preguntas va dentro
de `.v4-panel`; el mapa de entradas a la derecha como panel de lectura. Conserva
`#create-scenario`, los `data-screen` de las pestañas, los cuatro `#hero-*`,
`#question-title`, `#question-input`, `#field-list`, `#progress-fill`.

### B7. DecisionRecord — `templates/lab/decision_record.html` (hoy 50%)
Falta **el bloque de veredicto**, que es el remate de todo el método: franja morada
con la decisión y a la derecha *por qué sí / pero / qué medir*. Conserva
`#build-decision`, `#save-decision`, `#dr-status`, los `#metric-*` y el panel de
feedback de piloto (`#pilot-feedback-card`, `#would-pay`, `#would-recommend`,
`#send-feedback`).

## Fase C — Contadores vacíos

D-Predict muestra 4 contadores en `--` y DecisionRecord 3. No se lee como "aún no hay
dato", se lee como roto. Dales un estado vacío con texto real ("sin calcular",
"requiere run activo") o esconde la tarjeta hasta que haya valor.

## Fase D — Superficie de pitch

Portada, Dashboard y 4D Lab, hoy al 0%. Fuera del recorrido de cohorte, así que va al
final salvo que haya un pitch antes.

---

## Movimiento — ya está construido, respeta sus reglas

`data-motion` en `<html>` con tres niveles: `full` | `reduced` | `none`.
`prefers-reduced-motion` manda en la primera carga; el control en pantalla lo
sobrescribe.

Lo que existe: entrada escalonada (barra 0ms → cabecera 60ms → eje 115ms →
contenido 130/175/215ms, 300ms cada una), el eje creciendo desde cero en CSS,
respuesta al pulsar, destello único al guardar, y la estación activa respirando
exactamente 3 veces con 420ms de retraso.

**Reglas que no se rompen:**
- Movimiento **de una sola vez**, nunca en bucle. Ninguna animación con
  `iteration-count: infinite`.
- **El movimiento nunca es la única señal**: con `data-motion="none"` todo debe
  seguir entendiéndose por color, posición, peso y texto.
- Nada de parallax, autoplay, brillos que laten, ni cifras contando hasta su valor
  (retrasan la lectura del dato y desvían la atención al movimiento).
- El llenado del eje va en **CSS, no en JS**: `requestAnimationFrame` no dispara si
  la pestaña carga en segundo plano.

Si añades movimiento nuevo a un cuerpo de pantalla, que sea feedback de una acción
del usuario, no decoración ambiental.

---

## Verificación — y las trampas de medición

Corre siempre al terminar cada pantalla:

```powershell
python scripts\validate_contracts.py          # 25 negativos
python scripts\smoke_vertex_golden_path.py    # cadena completa
```

Y verifica en navegador. **Objetivos**: cero desbordes horizontales, recortes,
solapamientos, texto fuera de pantalla o tipografía bajo 10px, en 1440 / 1024 / 390 px;
y cero fallos de contraste AA en ambos temas.

**Cinco trampas que me costaron horas. Léelas antes de medir nada:**

1. **`color-mix()` computa a `color(srgb 0.96 0.96 0.97)` con valores 0–1**, no 0–255.
   Un parser que asuma 0–255 los lee como casi negro y produce decenas de falsos
   fallos de contraste. Detecta el prefijo `color(` y multiplica por 255.

2. **Contextos de apilamiento.** Un modal `position:fixed` con `z-index` alto tapa la
   página de debajo a propósito. Si comparas cajas sin considerar la capa, lo
   reportarás como solapamiento. Sube por los ancestros buscando el primer
   `fixed/absolute` con `z-index >= 5` y solo compara elementos de la misma capa.

3. **Las transiciones y animaciones se congelan si el panel no compone fotogramas.**
   Verás `playState: "running"` con `currentTime: 0` para siempre, y medirás el
   fotograma cero. Antes de medir: `document.getAnimations().forEach(a => a.finish())`,
   o pon `data-motion="none"` — mata las transiciones con `!important` y el valor
   final es inmediato. Esto también aplica al cambiar de tema: mide después de que
   asiente, o desactiva el movimiento primero.

4. **El `<style>` inline de cada plantilla se carga DESPUÉS de la hoja enlazada**, así
   que una regla de una sola clase en la plantilla (`.hero`, `.mini`, `.snap`) gana a
   la tuya en `vertex4d.css`. Solución sin `!important`: duplica la clase en el
   selector (`.v4-head.v4-head`) para subir especificidad.

5. **Un riel de navegación estrecho de alto completo es intencional**, no un panel
   vacío. Excluye elementos de menos de ~110px de ancho de cualquier detector de
   "espacio desaprovechado".

Además: **abre siempre con Ctrl+Shift+R la primera vez**. Los assets van versionados
por mtime, pero si tocas algo fuera de `static/` el navegador puede seguir cacheando.

---

## Criterio de "terminado" por pantalla

Una pantalla está lista cuando:

1. La composición corresponde a la maqueta: barra, cabecera, eje, y el cuerpo usando
   `.v4-panel` / `.v4-item` / `.v4-num` / `.v4-verdict` según toque
2. Todos los hooks de JS siguen funcionando (pruébalo, no lo asumas)
3. Cero fallos de layout en 1440 / 1024 / 390
4. Cero fallos de contraste en tema oscuro y claro
5. Con `data-motion="none"` la pantalla sigue siendo comprensible
6. Los dos scripts de regresión pasan

Trabaja pantalla por pantalla y haz commit al terminar cada una. No avances a la
siguiente con la anterior a medias.
