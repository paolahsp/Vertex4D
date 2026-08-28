# VERTEX 4D Contracts v1

These contracts define the first integration foundation for the VERTEX 4D journey. They do not integrate Alex, SynapMap, D-Predict, MiroFish, FinOps or Billie code.

## Validation Model

Contract validation has two layers:

1. Official JSON Schema Draft 2020-12 validation with Python `jsonschema`, `Draft202012Validator.check_schema()`, `Draft202012Validator` and `FormatChecker`.
2. Business-rule validation in `scripts/validate_contracts.py` for cross-artifact references and policy rules JSON Schema cannot fully express.

Checking `$schema` alone does not prove a schema is valid; the official validator checks each schema before validating fixtures.

## Artifact Sequence

1. `ProjectRecord` creates the project container, synthetic-data declaration, revision metadata and current artifact references.
2. `ProblemFrame` represents future Alex output: original challenge, reframed problem, needs, assumptions, tensions, unknowns and Four Dimensions analysis.
3. `SystemMap` represents future SynapMap output: stakeholders, roles, relationships, dependencies, tensions, evidence references, boundaries and approved assumptions.
4. `PredictiveHypothesis` represents a future internal D-Predict scenario result. It is always a bounded simulation hypothesis and now includes a product-facing `qbi_reading`.
5. `FinancialScenario` represents a future FinOps adapter output. It is a contract, not a calculator.
6. `DecisionRecord` is the final VERTEX artifact. It links all upstream artifacts and preserves evidence, assumptions, hypotheses, risks and unknowns.

## Approval Conditions

Every artifact carries `human_approval`. The validator rejects contradictory approval states.

- `status=approved` requires `human_approval.state=approved`, `approved_by_role` and `approved_at`.
- `ProblemFrame` can enter `SystemMap` only when `approval_state=approved_for_system_mapping`.
- `SystemMap` must be approved before predictive or financial processing.
- `PredictiveHypothesis` and `FinancialScenario` must be reviewed before `DecisionRecord` inclusion.
- `DecisionRecord` requires facilitator approval.

## Classification Boundaries

`fact` means a traceable source supports the statement inside its declared context. `inference` is a derived interpretation. `hypothesis` needs testing. `unknown` must be preserved rather than filled.

## Synthetic Evidence

Every evidence object includes `evidence_context: synthetic_fixture`. A synthetic note can be a fact inside the fictional golden case, but it is not real-world evidence. The validator rejects non-synthetic evidence in the golden case.

## Assumption Provenance

Assumptions originate in `ProblemFrame`, are carried into `SystemMap`, and can only be used downstream if approval flags allow it. `SystemMap` cannot introduce new assumptions, silently change assumption statements or escalate unapproved assumptions.

Financial assumptions for service fee, washing cost, setup buffer and pilot volume are separate from operational assumptions such as deposit acceptance, washing capacity and staff training.

## Predictive Semantics

`PredictiveHypothesis` is bounded to `stakeholder_adoption_resistance`. Every simulated response includes adoption, resistance and undecided likelihoods; the validator checks that they sum to 1 within tolerance.

`PredictiveHypothesis` has `classification: predictive_hypothesis` and carries the required not-evidence warning. The `DecisionRecord` may summarize predictive hypotheses, but it must never convert them into evidence or facts.

The `qbi_reading` block is QBI lite, not the full formal model. It captures coexisting interpretation states, actor correlations, context-loss vectors and commitment pressure while preserving the same contract rules: every referenced stakeholder, relationship, assumption, signal, cascade, evidence item or unknown must resolve to the upstream artifact chain, and every QBI statement remains classified as `hypothesis`.

## Structured Success Criteria

Decision success criteria are structured objects with `criterion_id`, `metric`, `operator`, `target_value`, `unit`, `measurement_window`, `data_source` and `classification`.

## Local Setup

```bash
python -m pip install -r requirements-contracts.txt
python scripts/validate_contracts.py
```
