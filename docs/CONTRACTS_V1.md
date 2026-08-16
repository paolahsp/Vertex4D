# VERTEX 4D Contracts v1

These contracts define the first integration foundation for the VERTEX 4D journey. They do not integrate Alex, SynapMap, D-Predict, MiroFish, FinOps or Billie code.

## Artifact Sequence

1. `ProjectRecord` creates the project container, synthetic-data declaration and current artifact references.
2. `ProblemFrame` represents future Alex output: original challenge, reframed problem, needs, assumptions, tensions, unknowns and Four Dimensions analysis.
3. `SystemMap` represents future SynapMap output: stakeholders, roles, relationships, dependencies, tensions, evidence references, boundaries and approved assumptions.
4. `PredictiveHypothesis` represents a future internal D-Predict scenario result. It is always a bounded simulation hypothesis.
5. `FinancialScenario` represents a future FinOps adapter output. It is a contract, not a calculator.
6. `DecisionRecord` is the final VERTEX artifact. It links all upstream artifacts and preserves evidence, assumptions, hypotheses, risks and unknowns.

## Approval Gates

Human approval is explicit in every artifact through `human_approval`.

- `ProblemFrame` must be approved before system mapping.
- `SystemMap` must be approved before predictive or financial processing.
- `PredictiveHypothesis` must be reviewed as a hypothesis before it can be summarized in a decision record.
- `FinancialScenario` must be approved as fixture or calculated output before it can be summarized in a decision record.
- `DecisionRecord` requires facilitator approval.

## Classification Boundaries

`fact` means a traceable source supports the statement.

`inference` means VERTEX or a human reviewer derived a reasonable interpretation from facts.

`hypothesis` means the statement needs testing. Assumptions, simulations and fixture financial values remain hypotheses.

`unknown` means VERTEX must preserve uncertainty rather than filling the gap.

## PredictiveHypothesis Is Not Evidence

`PredictiveHypothesis` has `classification: predictive_hypothesis` and carries this required warning:

> This output is a bounded simulation hypothesis. It is not direct evidence, a factual prediction or a conclusion about identifiable people.

The `DecisionRecord` may summarize predictive hypotheses, but it must not convert them into evidence or facts.

## Future Adapters

Future adapters should connect existing components through these contracts:

- Alex writes `ProblemFrame`.
- SynapMap reads approved `ProblemFrame` material and writes `SystemMap`.
- D-Predict reads approved `SystemMap` inputs and writes `PredictiveHypothesis`.
- FinOps reads approved assumptions through a future adapter and writes `FinancialScenario`.
- VERTEX assembles `DecisionRecord`.

Adapters must not pass secrets, credentials, identifiable-person records or unapproved inputs into predictive processing.

