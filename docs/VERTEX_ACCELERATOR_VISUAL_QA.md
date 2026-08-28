# VERTEX Accelerator Demo Visual QA

Fecha de revision: 2026-08-26  
Base local validada: `http://127.0.0.1:8000`  
Cohort demo: `cohort_7a1a8ef9e1`  
Alumno usado: `maya.ellis@northstar-demo.example`  
Facilitador usado: `facilitator@northstar-demo.example`

## Veredicto

VERTEX ya puede usarse como demo guiada para aceleradoras.

La pagina comunica una propuesta educativa clara sin convertirse en LMS: el alumno trabaja dentro de un Decision Case real, produce entregables, y el facilitador ve donde intervenir. El buyer puede entender el valor institucional desde Cohort Room, Decision Memo y Outcome Report.

Todavia no la trataria como demo publica self-serve. Para presentacion guiada esta lista; para URL abierta faltan mas direccion contextual, mejor coaching del facilitador, trust docs reales y una ruta de onboarding menos densa.

## Que Se Hizo

1. Se corrio una captura completa del flujo demo con datos seed reales.
2. Se entro como alumno/founder para revisar los modulos del Golden Path.
3. Se entro como facilitator para revisar dashboard, cohort room, Decision Memo y Outcome Report.
4. Se capturaron 15 pantallas en desktop y mobile.
5. Se midio overflow horizontal, presencia del direction layer, texto esperado y clipping.
6. Se encontro overflow mobile en Cohort Room.
7. Se arreglo el responsive del Cohort Room y del header `v4-head`.
8. Se recapturo todo el flujo.

Resultado tecnico final:

```text
15 screens captured
0 horizontal overflow on all captured screens
7/7 student module pages include the direction layer
0 expected-content failures
```

Manifest reproducible:

```text
docs/accelerator_visual_qa_assets/capture_manifest.json
```

Script reproducible:

```powershell
python scripts\capture_accelerator_visual_qa.py
```

## Secuencia Visual De La Demo

```mermaid
flowchart LR
    A[Login alumno] --> B[Decision Case]
    B --> C[Alex / ProblemFrame]
    C --> D[SynapMap / SystemMap]
    D --> E[Approval Gate]
    E --> F[D-Predict + QBI lite]
    F --> G[Billie / FinancialScenario]
    G --> H[DecisionRecord]
    H --> I[Decision Memo]
    I --> J[Facilitator Cohort Room]
    J --> K[Outcome Report]
```

## Flujo Dual Actual

```mermaid
flowchart TB
    subgraph Founder["Alumno / Founder"]
        F1[Decision Case]
        F2[Locked Baseline]
        F3[Golden Path artifacts]
        F4[DecisionRecord]
        F5[Decision Memo]
        F1 --> F2 --> F3 --> F4 --> F5
    end

    subgraph Facilitator["Facilitador / Direccion pedagogica"]
        T1[Cohort dashboard]
        T2[Intervention Radar]
        T3[Case comments]
        T4[Baseline/post rubric]
        T5[Outcome Report]
        T1 --> T2 --> T3 --> T4 --> T5
    end

    F2 -. baseline status .-> T1
    F3 -. artifacts + gaps .-> T2
    T3 -. coaching signal .-> F3
    F4 -. reviewed decision .-> T5
    F5 -. buyer artifact .-> T5
```

## Como Se Ve La Distribucion Grafica

### Alumno

La distribucion del alumno ya tiene una estructura entendible:

```text
Top bar
Golden Path progress
Direction layer
Primary work surface
Supporting panels / readings
```

Esto funciona porque cada modulo muestra:

- que accion sigue;
- por que importa;
- que deberia revelar VERTEX;
- a donde va ese entregable;
- si la puerta es hard gate, soft gate o hypothesis boundary.

La mejor decision visual actual es que el direction layer aparece como orientacion operacional, no como clase teorica. Eso mantiene la identidad de VERTEX como sistema de decision.

Riesgo pendiente: en algunos modulos, especialmente Decision Case, D-Predict y Billie, la pagina es larga y puede sentirse pesada si el buyer espera una experiencia muy pulida. Para demo guiada es aceptable; para self-serve conviene reducir friccion con estado de caso precargado o "guided sample mode".

### Facilitador

El Cohort Room ahora se lee como un espacio operativo real:

```text
Cohort summary
Add case/team controls
Intervention Radar
Case cards
Comments
Rubric scores
Decision Memo links
```

Lo mas fuerte comercialmente es la separacion visual entre:

```text
Decision Intervention
Workflow Attention
```

Eso ayuda a que VERTEX no parezca task management. El buyer puede ver que no todo pendiente tiene el mismo valor pedagogico.

Riesgo pendiente: el Cohort Room muestra muchos controles de edicion. Para una primera demo a aceleradora, conviene entrar directo a Intervention Radar y Outcome Report antes de bajar al detalle de formularios.

### Buyer

Decision Memo y Outcome Report son los artifacts mas demo-ready.

El buyer puede entender:

- que habia una baseline inicial;
- que hubo artefactos intermedios;
- que se registro una decision final;
- que hay cambios observados;
- que falta data donde falta data;
- que VERTEX no esta prometiendo predecir exito.

## Capturas Y Lectura Paso A Paso

### 1. Student workspace: Decision Case

Que hice: entre como alumno y abri `/dashboard/lab/start-golden-path`.

Que paso: la pagina muestra el primer trabajo real del alumno: crear Decision Case y bloquear baseline. La direccion educativa aparece despues del path bar.

![Student Decision Case](accelerator_visual_qa_assets/01-student-decision-case-desktop.png)

### 2. Student workspace: Alex

Que hice: abri `/dashboard/lab/alex`.

Que paso: el modulo conecta el trabajo de problem framing con `ProblemFrame` y con los modulos posteriores. Se entiende que Alex no es contenido separado, sino una lente de decision.

![Student Alex](accelerator_visual_qa_assets/02-student-alex-desktop.png)

### 3. Student workspace: SynapMap

Que hice: abri `/dashboard/lab/synapmap`.

Que paso: la pagina deja claro que el alumno trabaja stakeholder system: payer, approver, blocker y dependencies.

![Student SynapMap](accelerator_visual_qa_assets/03-student-synapmap-desktop.png)

### 4. Student workspace: Approval Gate

Que hice: abri `/dashboard/lab/assumption-approval`.

Que paso: el modulo comunica que las assumptions aprobadas son las que pueden propagarse a D-Predict y Billie.

![Student Approval Gate](accelerator_visual_qa_assets/04-student-approval-gate-desktop.png)

### 5. Student workspace: D-Predict + QBI lite

Que hice: abri `/dashboard/lab/d-predict`.

Que paso: D-Predict muestra `PredictiveHypothesis` y QBI lite como lectura de comportamiento. El lenguaje correcto aparece visible: bounded hypothesis, not proof, not startup prediction.

![Student D-Predict](accelerator_visual_qa_assets/05-student-d-predict-desktop.png)

### 6. Student workspace: Billie

Que hice: abri `/dashboard/lab/billie`.

Que paso: Billie funciona como lente economica. El entregable esperado es `FinancialScenario`, y la pagina conecta precio, margen, costos y runway con DecisionRecord.

![Student Billie](accelerator_visual_qa_assets/06-student-billie-desktop.png)

### 7. Student workspace: DecisionRecord

Que hice: abri `/dashboard/lab/decision-record`.

Que paso: el modulo convierte la cadena en compromiso final. La pagina se entiende como commit gate, no como formulario aislado.

![Student DecisionRecord](accelerator_visual_qa_assets/07-student-decision-record-desktop.png)

### 8. Facilitator dashboard

Que hice: entre como facilitator y abri `/dashboard/facilitator`.

Que paso: el dashboard carga metricas y cohorts. Sirve como entrada institucional, aunque para demo a buyer conviene ir rapido hacia el cohort demo.

![Facilitator dashboard](accelerator_visual_qa_assets/08-facilitator-dashboard-desktop.png)

### 9. Cohort case room

Que hice: abri `/dashboard/facilitator/cohorts/cohort_7a1a8ef9e1`.

Que paso: aparece la cola de intervencion, casos, comentarios abiertos, rubric scores y links a artifacts. Se corrigio overflow mobile detectado aqui.

![Cohort case room](accelerator_visual_qa_assets/09-cohort-case-room-desktop.png)

### 10. Cohort Outcome Report

Que hice: abri `/dashboard/facilitator/cohorts/cohort_7a1a8ef9e1/outcome-report`.

Que paso: el reporte funciona como artifact buyer-facing. Es la pantalla que mejor responde "que cambio en la cohorte".

![Outcome Report](accelerator_visual_qa_assets/10-outcome-report-desktop.png)

### 11. Decision Memo

Que hice: abri `/dashboard/lab/decision-memo?run_id=run_demo_economics_changed`.

Que paso: el Memo conecta baseline, artifacts, decision final y trazabilidad. Es buen artifact para mostrar profundidad sin recorrer cada formulario.

![Decision Memo](accelerator_visual_qa_assets/11-decision-memo-desktop.png)

### 12. Mobile: Decision Case

Que hice: abri el primer paso del alumno en viewport 390x900.

Que paso: no hay overflow horizontal. La pagina es larga pero legible.

![Mobile Decision Case](accelerator_visual_qa_assets/12-student-decision-case-mobile.png)

### 13. Mobile: D-Predict + QBI lite

Que hice: abri D-Predict/QBI en mobile.

Que paso: la pantalla se mantiene legible y conserva el disclaimer de hipotesis acotada.

![Mobile D-Predict](accelerator_visual_qa_assets/13-student-d-predict-mobile.png)

### 14. Mobile: Cohort case room

Que hice: abri Cohort Room en mobile antes y despues del fix responsive.

Que paso: antes tenia 178px de overflow horizontal. Despues del arreglo quedo en 0px. Sigue siendo una pantalla densa, pero ya no rompe layout.

![Mobile Cohort Room](accelerator_visual_qa_assets/14-cohort-case-room-mobile.png)

### 15. Mobile: Outcome Report

Que hice: abri Outcome Report en mobile.

Que paso: no hay overflow horizontal y el reporte conserva lectura institucional.

![Mobile Outcome Report](accelerator_visual_qa_assets/15-outcome-report-mobile.png)

## Estado Frente Al Roadmap

### Meses 0-2: Pilot hardening

Estado actual: mayormente completo para demo guiada.

Hecho:

- Journey completo estable.
- Baseline y post-assessment sembrados en demo.
- Evidence Gate presente.
- Decision Memo.
- Dashboard facilitador basico.
- Outcome Report inicial.
- Demo seed/reset.
- Direction layer visible en modulos del alumno.
- QA visual desktop/mobile con capturas.

Pendiente:

- Responsive mobile mas pulido para todas las rutas reales, no solo capturas clave.
- Analytics de eventos como producto visible, no solo eventos internos.
- Evidence Gate mas contextual segun estado de caso.

### Meses 2-4: Alpha/Beta pilots

Estado actual: parcialmente iniciado.

Hecho o casi hecho:

- 5 equipos demo sinteticos.
- Rubric pre/post funcional en cohort.
- Intervention queue funcional.
- Comments de facilitador funcionales.

Falta:

- Probar con 8-12 founders reales.
- Pasar de demo seed a cohort piloto real.
- Validar si facilitadores entienden y usan Decision Intervention vs Workflow Attention.
- Pricing experiments reales.
- Mejorar coaching de facilitator: reason, recommended move, artifact link.

### Meses 4-6: Commercial V1

Estado actual: fundamentos presentes, no completo.

Hecho o casi hecho:

- Outcome reports existen.
- Better export parcial: print routes ya existen para Memo y Outcome Report.
- Cohort setup basico.

Falta:

- Cohort setup mejorado.
- Roles y permisos mas robustos.
- Exports mas pulidos.
- Onboarding institucional.
- 3-5 pilotos pagados.
- Trust docs reales.

### Meses 6-12

Estado actual: no conviene construir todavia.

No priorizar aun:

- SSO/SAML.
- White-label.
- API/export avanzado.
- LMS integrations.
- Self-service paid.
- Benchmarking de cohortes.

La prioridad ahora no es escalar infraestructura. Es validar que aceleradoras pagan por decision traceability, intervention usefulness y outcome reports.

## Que Funciona Hoy

Tools/modulos del alumno:

- Decision Case.
- Locked Baseline.
- Alex / `ProblemFrame`.
- SynapMap / `SystemMap`.
- Approval Gate.
- D-Predict / `PredictiveHypothesis`.
- QBI lite reading dentro de D-Predict.
- Billie / `FinancialScenario`.
- DecisionRecord.
- Decision Memo.

Facilitador/institucion:

- Facilitator dashboard.
- Cohort case room.
- Intervention Radar.
- Decision Intervention vs Workflow Attention.
- Comments.
- Rubric baseline/post.
- Outcome Report.
- Print routes para artifacts.

## Que Hace Falta Antes De Presentar A Aceleradoras

### Must Have Para Demo Guiada

1. Preparar un run-of-show de 8-12 minutos usando estas capturas.
2. Entrar directo a Cohort Room y Outcome Report, no empezar llenando formularios.
3. Tener una historia concreta de 2 casos:
   - uno con cambio de decision;
   - uno con intervention need.
4. Mostrar D-Predict/QBI solo como lente de comportamiento, no como prediccion.
5. Cerrar con pilot ask: 4-6 semanas, 8-12 equipos, decision-quality evidence.

### Should Have Antes De URL Publica

1. Sample mode precargado para alumno.
2. Next Best Action contextual por contradiccion real.
3. Facilitator coaching cards.
4. Trust pack real.
5. Un dashboard demo menos editable para buyer.
6. Export visual mas consistente para PDF.

### Not Yet

1. No claim de skill acquisition probado.
2. No claim de startup validation.
3. No self-serve sin onboarding.
4. No integraciones LMS/SSO hasta que una venta lo exija.

## Decision Sobre URL

URL funcionando debe ser el ultimo paso de esta fase, no el primero.

Orden recomendado:

```text
1. Cerrar QA visual y mobile
2. Ajustar run-of-show buyer
3. Preparar sample mode / demo state
4. Generar trust/demo docs minimos
5. Publicar URL semi-privada
6. Ensayar con 1-2 personas externas
7. Presentar a aceleradoras
```

Motivo: si se publica antes de cerrar narrativa y estado precargado, el producto puede parecer mas pesado de lo que realmente es. Guiado, VERTEX se entiende como sistema de decision. Self-serve, todavia puede sentirse como muchas herramientas juntas.

## Recomendacion Final

Siguiente paso recomendado:

```text
Crear un Accelerator Demo Mode semi-guiado.
```

Debe hacer tres cosas:

1. Llevar al facilitator directo a `cohort_7a1a8ef9e1`.
2. Resaltar dos casos demo con nombres comerciales claros.
3. Abrir Outcome Report y Decision Memo como artifacts principales.

Despues de eso, la URL publica/semi-privada si tiene sentido.
