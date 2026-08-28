# VERTEX Product + UX + Business Audit System

## Proposito

Este documento convierte la auditoria aplicada al demo institucional de VERTEX en un sistema reutilizable pagina por pagina.

No es una review visual tradicional.

Es una auditoria de producto, negocio, evidencia, pedagogia y venta, disenada para responder:

```text
Esta pagina ayuda a mover al usuario hacia una decision o comportamiento valioso,
y lo hace de una forma que el buyer puede entender, confiar y pagar?
```

Regla central:

```text
Built != useful != effective != commercially valuable.
```

Para VERTEX, la pregunta maestra es:

```text
Que cambio observable deberia producir esta pagina en el razonamiento o comportamiento del usuario,
como queda registrado,
quien utiliza ese cambio despues,
y que evidencia tenemos de que realmente ocurre?
```

Pregunta adicional para todo el sistema:

```text
Esta pantalla hace mas dificil que una suposicion termine disfrazada de hecho?
```

## Como Usar Este Sistema

Usalo antes de redisenar una pantalla, agregar una feature o escribir copy comercial.

Proceso recomendado:

1. Elegir una pagina concreta.
2. Definir usuario, job, decision posterior y artifact.
3. Separar lo construido de lo validado.
4. Auditar UX de decision.
5. Auditar evidencia y riesgo de IA.
6. Auditar contradicciones entre artifacts.
7. Cambiar de lente: founder, facilitator, buyer.
8. Clasificar valor comercial.
9. Hacer substitute test.
10. Auditar claims.
11. Auditar numeros si existen.
12. Priorizar por riesgo.
13. Convertir hallazgos en backlog.

No usar el mismo peso para todas las revisiones.

Usar dos modos:

```text
Quick Audit - para cambios de sprint y QA regular.
Full Audit - para pantallas nuevas, estrategicas o problematicas.
```

El sistema debe ayudar a decidir, no convertirse en burocracia.

## Quick Audit De Sprint

Usar estas 7 preguntas cuando una pantalla ya existe y el cambio es acotado:

| # | Pregunta |
|---|---|
| 1 | Quien es el usuario y cual es su job? |
| 2 | Que debe cambiar al salir? |
| 3 | Cual es el Next Best Action? |
| 4 | Cual es el aha? |
| 5 | Que assumption podria convertirse falsamente en fact? |
| 6 | Que ve despues el facilitator o buyer? |
| 7 | P0, P1, P2 o NOT NOW? |

Usar el Full Audit cuando:

- la pagina es nueva;
- la pagina esta en el buyer demo;
- la pagina alimenta un artifact downstream;
- la pagina contiene IA, scoring, pricing o claims;
- la pagina puede crear confusion entre fact, assumption, inference y unknown;
- el equipo no sabe si la feature debe existir.

## Product Discovery Loop

La auditoria no termina en backlog.

Debe funcionar como loop:

```text
PAGE
-> Expected user change
-> Product hypothesis
-> Implementation
-> User / facilitator / buyer test
-> Observed signal
-> Evidence level changes
-> KEEP / MODIFY / REMOVE
```

Decision rule:

```text
KEEP if it produces a useful signal or protects the evidence chain.
MODIFY if the job is right but the screen does not reveal the right thing fast enough.
REMOVE if no decision, evidence or downstream value becomes weaker without it.
```

This is the product discovery operating system for VERTEX.

## 1. Empezar Por El Job

Antes de mirar colores, botones o layout, contestar:

| Pregunta | Ejemplo VERTEX |
|---|---|
| Quien llega aqui? | Founder |
| Que intenta conseguir? | Entender si el problema esta bien planteado |
| Que decision debe poder tomar despues? | "Este es el problema que voy a investigar" |
| Que artifact debe producir? | `ProblemFrame` |
| Que puede salir mal? | Confundir solucion con problema |

Si no se puede responder en una frase, la pagina no tiene una funcion suficientemente clara.

La pregunta correcta no es:

```text
Que hace esta screen?
```

La pregunta correcta es:

```text
Para que existe dentro de la cadena de decision?
```

## 2. Separar Tres Niveles

### Nivel A - Lo Que Existe

Observar solamente lo construido.

Ejemplo:

```text
Existe dashboard, cohort view, Intervention Queue, Decision Memo y Outcome Report.
El flujo buyer-facing puede recorrerse de punta a punta.
```

Esto significa:

```text
Observed / built
```

No significa:

```text
valuable / validated
```

### Nivel B - Lo Que Afirmamos Que Consigue

Preguntar:

```text
Que estamos diciendo que esta feature hace?
```

Ejemplo:

```text
Intervention Radar le dice al facilitador donde intervenir y por que.
```

Eso sigue siendo una value hypothesis hasta verlo con facilitadores reales.

### Nivel C - Lo Que Esta Demostrado

Preguntar:

```text
Que evidencia tenemos de que realmente produce ese resultado?
```

Evidencia posible:

- funcionamiento tecnico;
- usability test;
- comportamiento real;
- before/after;
- reaccion del buyer;
- willingness to pay;
- pago;
- renovacion.

## 3. Jerarquia De Evidencia

Clasifica cada pagina, feature o claim:

Dividir visualmente product evidence y business evidence.

### Product Evidence

| Nivel | Nombre | Significado |
|---|---|---|
| 0 | Hypothesis | Creemos que deberia funcionar. |
| 1 | Implemented | Existe tecnicamente. |
| 2 | Usable | Usuarios reales consiguen usarlo. |
| 3 | Useful | Usuarios dicen y demuestran que les ayuda. |
| 4 | Behavioral impact | Cambia algo observable en lo que hacen o deciden. |

### Business Evidence

| Nivel | Nombre | Significado |
|---|---|---|
| 5 | Buyer value | El comprador institucional considera ese cambio valioso. |
| 6 | Payment | Paga por obtenerlo. |
| 7 | Repeatability | Renueva, repite o expande. |

Uso recomendado:

```text
No decir "feature validated" si solo significa "feature works".
```

Una feature puede llegar a nivel 4 y aun asi no ser un buen negocio.

Tambien puede existir buyer value para una solucion imperfecta si el dolor institucional es suficientemente fuerte.

### Observed Signal

Ademas de `Success Metric` y `Evidence Level`, registrar que ocurrio realmente en el ultimo test.

Ejemplos:

| Page | Success metric | Observed signal |
|---|---|---|
| SynapMap | Founder identifica actor nuevo | 6/8 founders agregaron al menos 1 stakeholder que no habian considerado |
| Radar | Facilitator prioriza correctamente | 4/5 facilitators eligieron primero el caso con decision intervention |
| Memo | Buyer entiende que cambio | 3/4 buyers explicaron el before -> after sin ayuda |

Sin `Observed signal`, la tabla es una evaluacion.

Con `Observed signal`, se vuelve aprendizaje acumulativo.

## 4. Auditoria UX De Decision

Para cada pagina revisar estas dimensiones:

| Dimension | Pregunta |
|---|---|
| Purpose | Se entiende para que estoy aqui? |
| Next action | Se inmediatamente que hacer? |
| Why now | Entiendo por que importa ahora? |
| Cognitive load | Tengo que pensar demasiado en como usar la herramienta? |
| Evidence discipline | Distingue hecho, supuesto, inferencia y unknown? |
| Artifact | Esta claro que voy a producir? |
| Feedback | VERTEX me revela algo al avanzar? |
| Exit state | Se cuando termine y que sigue? |
| Decision consequence | Que decision posterior mejora gracias a esta pagina? |

Si `Decision consequence` es "ninguna", probablemente es feature administrativa o prescindible.

## 5. Modelo De Cinco Capas

Cada pagina deberia contestar:

```text
What do I do now?
Why does it matter?
What decision-quality dimension is relevant, and should it be visible or only metadata?
What artifact am I producing?
What if I get stuck?
```

Regla de diseno:

```text
No mostrar las cinco capas con el mismo peso visual.
```

Ejemplo de jerarquia:

```text
Principal:
Map the people who can make this decision work or fail.

Secundario:
Why: adoption depends on more than your user.

Progresivo:
Decision skill, expected artifact, stuck prompt.
```

## 6. Buscar El Aha

No basta preguntar:

```text
Puede completar esta pantalla?
```

Hay que preguntar:

```text
Que descubre aqui que no sabia antes?
```

VERTEX necesita microtransformaciones.

| Modulo | Output debil | Aha deseado |
|---|---|---|
| Alex | `ProblemFrame saved` | `Assumption uncovered: you are describing the solution, not the underlying problem.` |
| SynapMap | `SystemMap saved` | `System reveal: the user is not the approver.` |
| Approval Gate | `Approved` | `Evidence gap: 4 of 6 assumptions driving the model are unsupported.` |
| D-Predict | `Prediction generated` | `Resistance found: buyer benefits, approver carries implementation risk.` |
| QBI lite | `Behavioral reading generated` | `Commitment pressure: the actor who must change behavior has the weakest incentive.` |
| Billie | `FinancialScenario saved` | `Economic contradiction: current price does not cover variable cost.` |
| DecisionRecord | `Decision saved` | `Decision shift: initial intuition changed after evidence review.` |

Esto evita que VERTEX se sienta como rellenar modulos.

## 7. Auditoria De Contradicciones

VERTEX no debe auditar cada pagina aislada.

Debe comparar lo que una pagina afirma contra pantallas y artifacts anteriores.

Ejemplos:

```text
Problem page:
Buyer = school.

Stakeholder page:
Approver = municipality.

Pricing page:
Revenue model assumes parents pay.
```

Contradiccion:

```text
Customer, approver and payer are not aligned.
```

Otro ejemplo:

```text
Founder claim:
Customers pay 29/month.

Evidence:
No pricing conversations yet.
```

VERTEX deberia mostrar:

```text
Price assumption - not market evidence.
```

La mejor experiencia de VERTEX no sera solamente generar insights.

Sera detectar cuando las partes del negocio no son coherentes entre si.

## 8. Auditoria De Riesgo De IA

Para cada output generado o asistido por IA:

| Pregunta | Regla VERTEX |
|---|---|
| De donde salio? | Debe tener provenance. |
| Es hecho o inferencia? | Debe estar etiquetado. |
| Puede propagarse? | No debe alimentar pasos posteriores automaticamente si todavia es assumption. |
| Quien lo aprueba? | Founder o facilitator, segun decision. |

Regla reutilizable:

```text
AI may propose.
Evidence may support.
The user authorizes.
VERTEX records.
```

## 9. Tres Lentes De Usuario

Cada pagina requiere tres pasadas.

| Lente | Pregunta |
|---|---|
| Founder | Esto me ayuda a decidir mejor? |
| Facilitator | Esto me dice donde debo intervenir? |
| Buyer | Esto deja evidencia de que algo importante ocurrio? |

La misma cadena de evidencia debe servir a trabajos distintos:

```text
Decision Case -> founder clarity
Intervention Radar -> facilitator prioritization
Cohort Outcome Report -> buyer evidence
```

## 10. Auditoria Comercial

Para cada feature, preguntar:

```text
Esto mueve presupuesto?
```

Clasificacion:

| Categoria | Significado | Ejemplo VERTEX |
|---|---|---|
| Differentiator | Razon potencial para comprar VERTEX. | Decision intervention basada en contradicciones reales. |
| Supporting value | Ayuda a vender, pero no genera compra sola. | Decision Memo PDF. |
| Table stakes | Tiene que existir, pero nadie compra por eso. | Login, responsive, PDF export. |
| Distraction | Consume desarrollo sin aumentar pilot conversion. | Marketplace, community, complex certification, white-label temprano. |

## 11. Competitor Substitution Test

Para cada pagina:

```text
Podria resolver esto razonablemente con ChatGPT + Notion + Excel + mentor?
```

Si la respuesta es si, preguntar:

```text
Que anade VERTEX que seria dificil obtener de esa combinacion?
```

Ventajas prometedoras de VERTEX:

- locked baseline;
- artifact provenance;
- approval gates;
- cross-artifact coherence;
- facilitator intervention;
- cohort-level before/after evidence;
- print-ready buyer artifacts;
- separation of fact, assumption, inference and unknown.

La ventaja no es la IA aislada.

## 12. Artifact Necessity Test

Preguntar:

```text
Si elimino esta pagina, que evidencia o decision deja de existir?
```

Clasificacion:

| Resultado | Interpretacion |
|---|---|
| Nothing | Candidate for removal. |
| Convenience only | Supporting value or table stakes. |
| Evidence chain breaks | Structural product element. |

Ejemplos:

```text
Locked Baseline disappears -> before/after evidence breaks.
```

```text
An explanatory interstitial disappears but SystemMap quality stays the same -> likely screen noise.
```

Este test protege a VERTEX contra scope creep.

## 13. Time To First Meaningful Reveal

Medir por pantalla:

```text
Cuantos minutos pasan antes de que VERTEX revele algo que justifique el esfuerzo?
```

No medir solamente completion.

Medir el primer insight.

Ejemplos:

| Module | Metric |
|---|---|
| Alex | Time-to-problem-reframe |
| SynapMap | Time-to-new-stakeholder |
| Approval Gate | Time-to-evidence-gap |
| D-Predict | Time-to-resistance-signal |
| QBI lite | Time-to-context-loss-signal |
| Billie | Time-to-economic-contradiction |
| Decision Memo | Time-to-before-after-understanding |

Transversal metric:

```text
Time to first meaningful reveal
```

This may matter more than completion rate for founder UX.

## 14. Claims Audit

Cada frase comercial debe etiquetarse:

| Etiqueta | Uso |
|---|---|
| FACT | Existe evidencia directa. |
| SUPPORTED INFERENCE | La evidencia permite concluirlo razonablemente. |
| HYPOTHESIS | Hay que probarlo. |
| OVERCLAIM | La frase va mas alla de la evidencia. |

Ejemplo:

```text
OVERCLAIM:
VERTEX improves founder decision quality.

Mejor:
VERTEX is designed to make changes in founder reasoning visible and measurable.

Pilot framing:
The pilot tests whether those changes actually occur.
```

## 15. Auditoria De Numeros

Para paginas con negocio, pricing o metricas, revisar por separado:

- calculos;
- denominadores;
- cohort sizes;
- conversion assumptions;
- ARR;
- CAC;
- gross margin;
- retention;
- runway;
- pricing logic;
- si la metrica es observada, modelada o hipotetica.

Regla:

```text
Audita la matematica y audita por separado la interpretacion de la matematica.
```

## 16. Priorizacion Por Riesgo

Priorizar por riesgo de comprension, confianza y venta.

| Prioridad | Significado |
|---|---|
| P0 | Bloquea comprension, confianza o venta. Arreglar ya. |
| P1 | Aumenta considerablemente el valor del pilot. |
| P2 | Optimizacion. Puede esperar. |
| NOT NOW | No construir hasta que comportamiento real lo justifique. |

Formato de recomendacion:

```text
Problem -> Change -> Why -> Evidence needed
```

Ejemplo:

```text
Problem:
Radar mezcla workflow issues y decision issues.

Change:
Separar Decision Intervention y Workflow Attention.

Why:
Si no, el differentiator parece task management.

Evidence needed:
Facilitadores priorizan correctamente los casos y califican las intervenciones como utiles.
```

## Template Pagina Por Pagina

Usar este template para cualquier screen nueva o existente:

```text
PAGE:
USER:
JOB:

1. PURPOSE
Why does this page exist?

2. ENTRY STATE
What does the user know/believe when entering?

3. DESIRED EXIT STATE
What should be different when leaving?

4. NEXT BEST ACTION
What should they do immediately?

5. WHY IT MATTERS
Why is this step necessary?

6. DECISION SKILL
What capability is being exercised?

7. ARTIFACT
What structured output should exist?

8. AHA MOMENT
What might VERTEX reveal?

9. EVIDENCE
What is fact / inference / assumption / unknown?

10. AI BOUNDARY
What can AI propose?
What must the user approve?
What must AI never decide?

11. CROSS-ARTIFACT CHECK
What previous claims should this page challenge?

12. FAILURE STATES
How can the founder misunderstand this?

13. IF STUCK
What is the smallest useful next action?

14. FACILITATOR VIEW
What would make this case worth intervention?

15. BUYER EVIDENCE
What signal should survive into the Outcome Report?

16. SUBSTITUTE TEST
Could ChatGPT/Notion/Excel do this?
If yes, what does VERTEX uniquely add?

17. SUCCESS METRIC
How will we know this page helped?

18. EVIDENCE LEVEL
Hypothesis / implemented / usable / useful / behavioral impact / paid / repeated

19. PRIORITY
P0 / P1 / P2 / NOT NOW

20. ARTIFACT NECESSITY
If this page disappeared, what would become impossible?

21. TIME TO FIRST MEANINGFUL REVEAL
How long before the user sees something worth the effort?

22. OBSERVED SIGNAL
What actually happened in the latest test?

23. NEXT EXPERIMENT
What should we test next?

24. KEEP / MODIFY / REMOVE
What should happen to this page after the evidence update?
```

## Primera Aplicacion A VERTEX Actual

Esta tabla no es una sentencia final. Es una primera lectura del estado actual despues del demo readiness.

| Page / Artifact | Primary user | Job | Artifact | Current evidence level | Commercial role | Priority |
|---|---|---|---|---|---|---|
| Login | Founder / facilitator | Entrar con rol correcto | Session | 1 - Implemented | Table stakes | P2 |
| Founder dashboard / start | Founder | Saber que decision trabajar | Decision Case | 1 - Implemented | Supporting value | P1 |
| Decision Case | Founder | Capturar la decision que importa | Run + case metadata | 1 - Implemented | Differentiator if tied to baseline | P1 |
| Locked Baseline | Founder / buyer | Preservar intuicion inicial | Baseline snapshot | 1 - Implemented | Differentiator | P0 maintained |
| Alex / ProblemFrame | Founder | Separar problema de solucion | `ProblemFrame` | 1 - Implemented | Supporting value | P1 |
| SynapMap / SystemMap | Founder / facilitator | Ver actores de adopcion | `SystemMap` | 1 - Implemented | Differentiator if contradictions surface | P1 |
| Approval Gate | Founder / facilitator | Autorizar assumptions antes de propagarlas | Approval state | 1 - Implemented | Differentiator | P0 maintained |
| D-Predict + QBI lite | Founder / facilitator | Leer resistencia, actor behavior and decision risk | `PredictiveHypothesis` | 1 - Implemented | Differentiator if bounded correctly | P1 |
| Billie / FinancialScenario | Founder | Ver coherencia economica | `FinancialScenario` | 1 - Implemented | Differentiator if contradictions surface | P1 |
| DecisionRecord | Founder / facilitator | Guardar decision revisada | `DecisionRecord` | 1 - Implemented | Differentiator | P0 maintained |
| Decision Memo | Founder / buyer | Mostrar que cambio y por que | Memo / PDF | 1 - Implemented | Supporting value / buyer proof | P0 maintained |
| Facilitator dashboard | Facilitator | Saber donde mirar | Cohort overview | 1 - Implemented | Supporting value | P1 |
| Cohort case room | Facilitator | Comparar casos y estado | Case list | 1 - Implemented | Supporting value | P1 |
| Intervention Radar | Facilitator | Priorizar intervenciones de decision | Intervention queue | 1 - Implemented | Differentiator | P0/P1 |
| Comments + resolution | Facilitator / founder | Dejar intervencion trazable | Case comments | 1 - Implemented | Supporting value | P1 |
| Rubric baseline/post | Facilitator / buyer | Medir movimiento observado en la rubrica | Quality scores | 1 - Implemented | Potential differentiator if reliable, interpretable and useful to buyers | P1 |
| Cohort Outcome Report | Buyer | Conservar evidencia de cambio de cohorte | Outcome report / PDF | 1 - Implemented | Primary buyer artifact | P0 maintained |
| Trust Pack | Buyer / procurement | Reducir riesgo de compra piloto | Procurement docs | 0 - Requirement identified / checklist specified | Table stakes for paid pilot | P0 before sale |

## Hallazgos Iniciales

### P0 - Mantener Antes De Buyer Calls

1. Decision Memo debe seguir abriendo con `What changed?`, no con una lista de features.
2. Outcome Report debe seguir abriendo con metrics buyer-readable, no con tablas internas.
3. Todos los outputs generados/asistidos deben separar fact, assumption, inference y unknown.
4. Approval Gate no debe permitir que assumptions no aprobadas alimenten DecisionRecord como evidencia.
5. Claims comerciales deben evitar "AI validates", "predicts success", "proves decision quality" y "below tender threshold".
6. Demo seed/reset debe seguir evitando deletes amplios y debe borrar solo datos marcados como demo.

### P1 - Siguiente Iteracion De Producto

1. Agregar un `Next Best Action` persistente por rol, basado en evidencia, contradiccion o riesgo de decision.
2. Convertir los Aha moments en copy contextual dentro de cada modulo.
3. Separar visualmente `Decision Intervention` de `Workflow Attention` en radar/cohort.
4. Agregar contradiction cards entre artifacts:
   - payer mismatch;
   - approver mismatch;
   - price unsupported by evidence;
   - user/buyer split;
   - cost/price contradiction;
   - evidence not strong enough for selected decision.
5. Registrar en Outcome Report que intervenciones fueron sustantivas vs administrativas.
6. Crear un `decision_skill` tag por comentario, score y intervention reason.
7. Medir si facilitadores entienden y usan la prioridad del radar sin explicacion externa.
8. Medir `time to first meaningful reveal` por modulo.
9. Registrar `observed signal` despues de cada founder/facilitator/buyer test.

### P2 - Optimizacion

1. Mejorar empty states y stuck prompts.
2. Afinar responsive mobile despues de pruebas con usuarios.
3. Mejorar PDF export visual y paginacion.
4. Agregar tooltips ligeros para provenance.
5. Reducir carga cognitiva en tablas densas con filtros y agrupaciones.

### NOT NOW

1. Marketplace.
2. Community.
3. White-label profundo.
4. Complex certification.
5. LMS integration antes de demanda pagada.
6. SSO/SAML antes de que procurement lo exija.
7. AI autonomous grading.

## Como Se Conecta Con El Roadmap

### Meses 0-2 - Pilot Hardening

Estado actual:

- Journey completo: implemented.
- Baseline y post-assessment: implemented.
- Evidence Gate: implemented.
- Decision Memo: implemented.
- Intervention queue: implemented.
- Outcome Report: implemented.
- Analytics/event traces: partially implemented.
- Responsive/mobile: needs fuller QA.
- Facilitator dashboard: basic implemented.

Lectura:

```text
VERTEX esta al final de Pilot Hardening.
```

### Meses 2-4 - Alpha / Beta Pilots

Lo que falta probar:

- 8-12 founders iniciales reales;
- 20-40 equipos posteriores;
- si el rubric pre/post funciona con facilitadores reales;
- si la intervention queue cambia preparacion de sesiones;
- si comments ayudan al founder o solo al facilitator;
- si buyers quieren pagar por el Outcome Report;
- pricing experiments;
- willingness to run another cohort.

Lectura:

```text
VERTEX esta listo para entrar en Alpha/Beta pilots condicionados,
pero no para venderse como plataforma probada.
```

### Meses 4-6 - Commercial V1

No declarar completo hasta tener:

- 3-5 pilotos pagados;
- cohort setup mejorado;
- roles/permisos mas finos;
- export mas robusto;
- onboarding institucional;
- trust pack convertido en documentos reales;
- evidence from buyer reactions and payment.

### Meses 6-12

No priorizar todavia salvo que ventas lo pidan:

- SSO/SAML;
- LMS integrations;
- white-label;
- API/export avanzado;
- benchmarking;
- self-service paid;
- annual licenses.

## Cadencia De Auditoria

### Antes De Cada Sprint

Elegir 3 paginas maximo y completar Quick Audit.

Usar Full Audit solo para pantallas nuevas, estrategicas o problematicas.

### Durante QA

Verificar:

- no overlap visual;
- CTA visible;
- artifact esperado claro;
- labels de evidence type visibles;
- no claims peligrosos;
- no propagation de assumptions sin approval.

### Despues De User Tests

Actualizar evidencia level:

```text
1 Implemented -> 2 Usable -> 3 Useful -> 4 Behavioral impact
```

No subir a nivel 5 sin buyer reaction.

No subir a nivel 6 sin pago.

No subir a nivel 7 sin repeticion, renovacion o expansion.

## Artifact Recomendado

Crear una tabla viva de auditoria por pagina:

| Page | User | Job | Desired change | Aha | Artifact | Evidence risk | Cross-check | Facilitator signal | Buyer signal | Substitute | Time-to-insight | Evidence level | Commercial role | Priority | Observed signal | Next experiment |
|---|---|---|---|---|---|---|---|---|---|---|---:|---|---|---|---|---|

Esa tabla deberia vivir junto al roadmap de producto y actualizarse despues de cada rehearsal o pilot.

## Reveal / Challenge / Authorize / Commit

Every VERTEX screen must earn its existence through at least one of four things:

| Function | Meaning |
|---|---|
| Reveal | Descubre algo que el user no veia. |
| Challenge | Cuestiona una assumption, contradiction o decision risk. |
| Authorize | Decide que puede propagarse downstream. |
| Commit | Convierte analisis en una decision registrada. |

Si una pantalla no hace ninguna de estas cuatro cosas, probablemente es navegacion, administracion o contenido auxiliar.

## Definicion De Una Buena Pagina VERTEX

Una pagina de VERTEX es buena cuando:

1. El usuario sabe que hacer ahora.
2. La pagina revela, desafia, autoriza o compromete algo sobre la decision.
3. El artifact resultante tiene provenance.
4. Las assumptions no se disfrazan de facts.
5. El facilitator puede decidir si intervenir.
6. El buyer puede ver que cambio sin escuchar una explicacion larga.
7. Hay un observed signal o una hipotesis explicita de que la pagina ayuda.
8. El claim comercial queda dentro de la evidencia disponible.

Si una pagina solo se ve bien y contiene informacion util, todavia es una interfaz.

Si produce un cambio observable, lo registra, lo conecta con otros artifacts y permite una decision posterior mejor, entonces es producto VERTEX.
