# Fuentes de diseño de VERTEX 4D

Estos archivos son la referencia visual del rediseño v4. Vivían en un directorio
temporal atado a una sesión; están aquí para que sobrevivan.

| Archivo | Qué es |
| --- | --- |
| `maqueta-v4.html` | **Fuente de verdad visual.** Ábrela en el navegador. Lleva el toggle de tema, los tres niveles de movimiento y el modo enfoque funcionando. Es la referencia contra la que se compara cada pantalla. |
| `maqueta-v3.html` | Paso previo, sin la capa de atención. Se conserva porque muestra la decisión de legibilidad para jornada larga. |
| `prompt-rediseno-v4.md` | Brief que produjo la capa de tokens, tipografía y accesibilidad. |
| `prompt-fase-B.md` | Brief de reconstrucción de los cuerpos de pantalla, con las trampas de medición documentadas. |

## Lo que la maqueta fija

- **Paleta**: `#5b13ec` acción · `#B2A4FF` hipótesis · `#FF6B6B` riesgo · `#66FFB2` evidencia
- **Regla de color**: mint, coral y lavender solo cargan texto sobre fondo oscuro.
  Sobre fondo claro son relleno con tinta oscura encima.
- **Tipografía**: Bricolage Grotesque (display) · Manrope (cuerpo) · JetBrains Mono (datos)
- **Movimiento**: de una sola vez, nunca en bucle; nunca la única señal
- **Escala**: título 43px · riel de contadores 218px · cifras 24px · knob 14px · pista 3px

## Cómo verificar contra ella

Los dos scripts de regresión del proyecto cubren contratos y cadena de artefactos,
no diseño. Para lo visual, `prompt-fase-B.md` documenta el método de medición y las
cinco trampas que producen falsos positivos — léelas antes de medir nada.
