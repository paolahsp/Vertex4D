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

## Hardened v1 Semantics

- `ProjectRecord` has `revision` and `updated_at` so current artifact references represent the final fixture snapshot.
- Evidence objects declare `evidence_context: synthetic_fixture`.
- Financial assumptions trace from `ProblemFrame` to `SystemMap` to `FinancialScenario`: EUR 0.45 service fee, EUR 0.28 washing and handling cost, EUR 900 setup buffer and 1,800 pilot uses.
- Predictive responses include adoption, resistance and undecided likelihoods that sum to 1.
- `DecisionRecord` has a resolving `selected_alternative_id` and structured success criteria.

## Local Validation

```bash
python -m pip install -r requirements-contracts.txt
python scripts/validate_contracts.py
python -m compileall main.py database.py scripts
```

The validator checks official schema validity, fixture validation, cross-artifact references, approval gates, synthetic evidence semantics, assumption provenance, probability semantics, downstream unknown preservation and deterministic negative cases.

No external API calls, LLM calls, database reads or external component imports are required.
