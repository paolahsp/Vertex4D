# Golden Case v1

The golden case is a fully synthetic VERTEX 4D journey for `ReCircle Kitchens`, a fictional women-led impact venture exploring reusable food containers for independent cafes in Berlin.

## Scenario Boundary

The scenario is limited to stakeholder adoption and resistance during a five-cafe pilot. It does not represent a full launch, real market research, real financial forecasting or conclusions about identifiable people.

## Fixture Files

The fixtures live in `fixtures/golden-case/v1/`:

- `project-record.json`
- `problem-frame.json`
- `system-map.json`
- `predictive-hypothesis.json`
- `financial-scenario.json`
- `decision-record.json`

The final decision recommends a limited pilot, not a full launch. The next experiment measures first-time uptake, repeat returns, staff explanation time and container loss over six weeks.

## Local Validation

Run:

```bash
python scripts/validate_contracts.py
```

The validator checks:

- all schemas are JSON Schema Draft 2020-12 documents
- all six fixtures validate against their schemas
- all artifacts use the same `project_id`
- referenced artifacts exist
- evidence references resolve
- stakeholder and relationship references resolve
- `PredictiveHypothesis` uses only approved `SystemMap` inputs
- `FinancialScenario` uses only approved financial assumptions
- `DecisionRecord` references all preceding artifacts
- predictive hypotheses remain labelled as hypotheses
- unknowns and limitations are preserved downstream
- an invalid in-memory fixture fails predictably

No external API calls, LLM calls, database reads or external component imports are required.

