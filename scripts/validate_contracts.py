from __future__ import annotations

import copy
import json
import sys
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "contracts" / "v1"
FIXTURE_DIR = ROOT / "fixtures" / "golden-case" / "v1"
ARTIFACT_FILES = {
    "project_record": "project-record.json",
    "problem_frame": "problem-frame.json",
    "system_map": "system-map.json",
    "predictive_hypothesis": "predictive-hypothesis.json",
    "financial_scenario": "financial-scenario.json",
    "decision_record": "decision-record.json",
}
SCHEMA_FILES = {
    "project_record": "project-record.schema.json",
    "problem_frame": "problem-frame.schema.json",
    "system_map": "system-map.schema.json",
    "predictive_hypothesis": "predictive-hypothesis.schema.json",
    "financial_scenario": "financial-scenario.schema.json",
    "decision_record": "decision-record.schema.json",
}
TOLERANCE = 0.000001


class ContractValidationError(Exception):
    pass


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractValidationError(message)


def iter_objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_objects(child)


def require_unique(items, id_field: str, label: str) -> set[str]:
    ids: set[str] = set()
    for item in items:
        item_id = item[id_field]
        require(item_id not in ids, f"duplicate stable ID in {label}: {item_id}")
        ids.add(item_id)
    return ids


def merge_declared_items(collections, id_field: str, label: str) -> dict[str, dict]:
    registry: dict[str, dict] = {}
    for items in collections:
        local_ids = require_unique(items, id_field, label)
        for item in items:
            item_id = item[id_field]
            if item_id in registry:
                require(registry[item_id] == item, f"duplicate stable ID in {label} has conflicting declarations: {item_id}")
            registry[item_id] = item
    return registry


def build_declared_id_registries(fixtures) -> dict[str, set[str]]:
    project = fixtures["project_record"]
    problem = fixtures["problem_frame"]
    system = fixtures["system_map"]
    predictive = fixtures["predictive_hypothesis"]
    decision = fixtures["decision_record"]
    registries = {
        "artifacts": {artifact["artifact_id"] for artifact in fixtures.values()},
        "evidence": set(merge_declared_items([problem["evidence_references"], system["evidence_references"]], "evidence_id", "evidence")),
        "assumptions": require_unique(problem["assumptions"], "assumption_id", "assumptions"),
        "system_assumptions": require_unique(system["approved_assumptions"], "assumption_id", "system assumptions"),
        "stakeholders": require_unique(system["stakeholders"], "stakeholder_id", "stakeholders"),
        "relationships": require_unique(system["relationships"], "relationship_id", "relationships"),
        "problem_tensions": require_unique(problem["tensions"], "id", "problem tensions"),
        "system_tensions": require_unique(system["tensions"], "id", "system tensions"),
        "dependencies": require_unique(system["dependencies"], "id", "dependencies"),
        "problem_unknowns": require_unique(problem["unknowns"], "id", "problem unknowns"),
        "system_unknowns": require_unique(system["unknowns"], "id", "system unknowns"),
        "adoption_signals": require_unique(predictive["adoption_signals"], "signal_id", "adoption signals"),
        "resistance_signals": require_unique(predictive["resistance_signals"], "signal_id", "resistance signals"),
        "cascades": require_unique(predictive["possible_cascades"], "cascade_id", "cascades"),
        "alternatives": require_unique(decision["alternatives_considered"], "alternative_id", "alternatives"),
        "risks": require_unique(decision["risks"], "id", "decision risks"),
        "decision_unknowns": require_unique(decision["unknowns"], "id", "decision unknowns"),
        "contradictions": require_unique(decision["contradictions"], "id", "decision contradictions"),
        "success_criteria": require_unique(decision["success_criteria"], "criterion_id", "success criteria"),
        "audit_events": require_unique(decision["audit_trail"], "event_id", "audit events"),
        "experiments": {decision["next_experiment"]["experiment_id"]},
        "selected_decisions": {decision["selected_decision"]["decision_id"]},
        "project_ids": {project["project_id"]},
    }
    registries["predictive_signals"] = registries["adoption_signals"] | registries["resistance_signals"]
    registries["unknowns"] = registries["problem_unknowns"] | registries["system_unknowns"] | registries["decision_unknowns"]
    registries["tensions"] = registries["problem_tensions"] | registries["system_tensions"]
    return registries


def check_schema_strictness(schema, path="$") -> None:
    if isinstance(schema, dict):
        if schema.get("type") == "object":
            require("properties" in schema, f"{path}: object missing properties")
            require("required" in schema, f"{path}: object missing required")
            require(schema.get("additionalProperties") is False, f"{path}: object must set additionalProperties=false")
        if schema.get("type") == "array":
            require("items" in schema, f"{path}: array missing items")
        for key, value in schema.items():
            check_schema_strictness(value, f"{path}.{key}")
    elif isinstance(schema, list):
        for index, item in enumerate(schema):
            check_schema_strictness(item, f"{path}[{index}]")


def validate_official_schemas(schemas, fixtures) -> None:
    checker = FormatChecker()
    for kind, schema in schemas.items():
        Draft202012Validator.check_schema(schema)
        check_schema_strictness(schema)
        validator = Draft202012Validator(schema, format_checker=checker)
        errors = sorted(validator.iter_errors(fixtures[kind]), key=lambda error: list(error.path))
        if errors:
            first = errors[0]
            raise ContractValidationError(f"{kind}: schema validation failed at {list(first.path)}: {first.message}")


def validate_common(kind: str, artifact: dict) -> None:
    require(artifact["schema_version"] == "1.0.0", f"{kind}: schema_version mismatch")
    require(artifact["artifact_type"] == kind, f"{kind}: artifact_type mismatch")
    require(isinstance(artifact["revision"], int) and artifact["revision"] > 0, f"{kind}: revision must be positive")
    created = datetime.fromisoformat(artifact["created_at"].replace("Z", "+00:00"))
    updated = datetime.fromisoformat(artifact["updated_at"].replace("Z", "+00:00"))
    require(updated >= created, f"{kind}: updated_at cannot be earlier than created_at")
    require(artifact["provenance"]["source_kind"] == "synthetic_fixture", f"{kind}: must be synthetic fixture")
    require(artifact["provenance"]["ip_owner"] == "Paola Hintze", f"{kind}: IP owner must remain Paola Hintze")
    require(artifact["provenance"]["external_components_used"] == [], f"{kind}: must not integrate external components")
    approval = artifact["human_approval"]
    if artifact["status"] == "approved":
        require(approval["state"] == "approved", f"{kind}: approved status requires approved human_approval")
        require(approval["approved_by_role"] is not None, f"{kind}: approved artifact requires approver role")
        require(approval["approved_at"] is not None, f"{kind}: approved artifact requires approved_at")
    if artifact["status"] in {"pending_review", "rejected"}:
        require(approval["state"] != "approved", f"{kind}: pending/rejected cannot carry approved gate")


def validate_business_rules(fixtures) -> None:
    for kind, artifact in fixtures.items():
        validate_common(kind, artifact)
    require(len({artifact["project_id"] for artifact in fixtures.values()}) == 1, "all artifacts must use one project_id")
    project = fixtures["project_record"]
    problem = fixtures["problem_frame"]
    system = fixtures["system_map"]
    predictive = fixtures["predictive_hypothesis"]
    financial = fixtures["financial_scenario"]
    decision = fixtures["decision_record"]
    artifacts = {artifact["artifact_id"]: artifact for artifact in fixtures.values()}
    registries = build_declared_id_registries(fixtures)
    expected_project_refs = {
        "problem_frame_id": problem["artifact_id"],
        "system_map_id": system["artifact_id"],
        "predictive_hypothesis_id": predictive["artifact_id"],
        "financial_scenario_id": financial["artifact_id"],
        "decision_record_id": decision["artifact_id"],
    }
    for field, expected in expected_project_refs.items():
        actual = project["current_artifact_references"][field]
        require(actual == expected, f"ProjectRecord.{field} must reference expected artifact {expected}, got {actual}")
    require(project["revision"] >= 2, "project final snapshot must be revisioned")
    require(problem["approval_state"] == "approved_for_system_mapping", "ProblemFrame must be approved_for_system_mapping")
    require(system["status"] == "approved", "SystemMap must be approved before processing")
    require(predictive["human_approval"]["state"] == "approved", "PredictiveHypothesis must be reviewed")
    require(financial["human_approval"]["state"] == "approved", "FinancialScenario must be reviewed")
    require(decision["facilitator_approval"]["state"] == "approved", "DecisionRecord requires facilitator approval")
    require(problem["preceding_artifacts"]["project_record_id"] == project["artifact_id"], "ProblemFrame.project_record_id must link ProjectRecord")
    require(system["preceding_artifacts"]["project_record_id"] == project["artifact_id"], "SystemMap.project_record_id must link ProjectRecord")
    require(system["preceding_artifacts"]["problem_frame_id"] == problem["artifact_id"], "SystemMap.problem_frame_id must link ProblemFrame")
    require(predictive["preceding_artifacts"]["project_record_id"] == project["artifact_id"], "PredictiveHypothesis.project_record_id must link ProjectRecord")
    require(predictive["preceding_artifacts"]["problem_frame_id"] == problem["artifact_id"], "PredictiveHypothesis.problem_frame_id must link ProblemFrame")
    require(predictive["preceding_artifacts"]["system_map_id"] == system["artifact_id"], "PredictiveHypothesis.system_map_id must link SystemMap")
    require(financial["preceding_artifacts"]["project_record_id"] == project["artifact_id"], "FinancialScenario.project_record_id must link ProjectRecord")
    require(financial["preceding_artifacts"]["problem_frame_id"] == problem["artifact_id"], "FinancialScenario.problem_frame_id must link ProblemFrame")
    require(financial["preceding_artifacts"]["system_map_id"] == system["artifact_id"], "FinancialScenario.system_map_id must link SystemMap")
    problem_evidence = {item["evidence_id"]: item for item in problem["evidence_references"]}
    system_evidence = {item["evidence_id"]: item for item in system["evidence_references"]}
    all_evidence = problem_evidence | system_evidence
    for evidence in all_evidence.values():
        require(evidence["evidence_context"] == "synthetic_fixture", f"non-synthetic evidence found: {evidence['evidence_id']}")
        require(evidence["contains_personal_data"] is False, f"evidence contains personal data: {evidence['evidence_id']}")
    for artifact in [problem, system]:
        for obj in iter_objects(artifact):
            for ref in obj.get("evidence_refs", []):
                require(ref in all_evidence, f"unresolved evidence reference: {ref}")
    problem_assumptions = {item["assumption_id"]: item for item in problem["assumptions"]}
    system_assumptions = {item["assumption_id"]: item for item in system["approved_assumptions"]}
    for assumption_id, system_assumption in system_assumptions.items():
        require(assumption_id in problem_assumptions, f"SystemMap introduced absent assumption: {assumption_id}")
        problem_assumption = problem_assumptions[assumption_id]
        require(system_assumption["source_artifact_id"] == problem["artifact_id"], f"SystemMap assumption source_artifact_id must equal ProblemFrame for {assumption_id}")
        require(system_assumption["statement"] == problem_assumption["statement"], f"SystemMap changed assumption statement: {assumption_id}")
        require(problem_assumption["approval_state"] == "approved", f"SystemMap escalated unapproved assumption: {assumption_id}")
        require(
            not (system_assumption["approved_for_predictive_processing"] is True and problem_assumption["approved_for_predictive_processing"] is False),
            f"SystemMap escalated predictive approval: {assumption_id}",
        )
        require(
            not (system_assumption["approved_for_financial_processing"] is True and problem_assumption["approved_for_financial_processing"] is False),
            f"SystemMap escalated financial approval: {assumption_id}",
        )
    stakeholder_ids = {item["stakeholder_id"] for item in system["stakeholders"]}
    relationship_ids = {item["relationship_id"] for item in system["relationships"]}
    require(all(item["is_identifiable_person"] is False for item in system["stakeholders"]), "SystemMap contains identifiable person")
    for relationship in system["relationships"]:
        require(relationship["from_stakeholder_id"] in stakeholder_ids, f"unresolved relationship source: {relationship['relationship_id']}")
        require(relationship["to_stakeholder_id"] in stakeholder_ids, f"unresolved relationship target: {relationship['relationship_id']}")
    approved_predictive = {key for key, item in system_assumptions.items() if item["approved_for_predictive_processing"] is True}
    approved_financial = {key for key, item in system_assumptions.items() if item["approved_for_financial_processing"] is True}
    refs = predictive["approved_input_references"]
    require(predictive["classification"] == "predictive_hypothesis", "PredictiveHypothesis classification cannot change")
    require("not direct evidence" in predictive["warning"], "PredictiveHypothesis warning cannot change")
    require(predictive["bounded_scenario_type"] == "stakeholder_adoption_resistance", "PredictiveHypothesis scenario must remain bounded")
    require(set(refs["stakeholder_ids"]).issubset(stakeholder_ids), "PredictiveHypothesis has unresolved stakeholder reference")
    require(set(refs["relationship_ids"]).issubset(relationship_ids), "PredictiveHypothesis has unresolved relationship reference")
    require(set(refs["evidence_ids"]).issubset(all_evidence), "PredictiveHypothesis has unresolved evidence reference")
    require(set(refs["assumption_ids"]).issubset(approved_predictive), "PredictiveHypothesis uses unapproved predictive assumption")
    used_ids = {item["assumption_id"] for item in predictive["assumptions_used"]}
    require(used_ids == set(refs["assumption_ids"]), "assumptions_used must exactly match approved_input_references")
    for item in predictive["assumptions_used"]:
        require(item["statement"] == system_assumptions[item["assumption_id"]]["statement"], f"PredictiveHypothesis copied changed assumption: {item['assumption_id']}")
    for response in predictive["simulated_stakeholder_responses"]:
        require(response["stakeholder_id"] in stakeholder_ids, "PredictiveHypothesis response stakeholder does not resolve")
        require(response["classification"] == "hypothesis", "simulated stakeholder responses must remain hypotheses")
        total = response["adoption_likelihood"] + response["resistance_likelihood"] + response["undecided_likelihood"]
        require(abs(total - 1.0) <= TOLERANCE, f"probabilities must sum to 1 for {response['stakeholder_id']}")
    for signal in predictive["adoption_signals"] + predictive["resistance_signals"]:
        require(signal["classification"] == "hypothesis", f"predictive signal must remain hypothesis: {signal['signal_id']}")
        require(set(signal["stakeholder_ids"]).issubset(stakeholder_ids), f"predictive signal stakeholder reference unresolved: {signal['signal_id']}")
    for cascade in predictive["possible_cascades"]:
        require(cascade["classification"] == "hypothesis", f"cascade must remain hypothesis: {cascade['cascade_id']}")
    require(set(financial["approved_assumption_references"]).issubset(approved_financial), "FinancialScenario uses unapproved financial assumption")
    used_financial_assumption_refs: set[str] = set()
    for collection_name in ["pricing_assumptions", "cost_assumptions", "volume_assumptions"]:
        for item in financial[collection_name]:
            require(item["is_fixture_value"] is True, f"{collection_name} must use fixture values")
            used_financial_assumption_refs.add(item["source_assumption_ref"])
            require(item["source_assumption_ref"] in approved_financial, f"{collection_name} source assumption not approved for financial processing")
    require(
        used_financial_assumption_refs == set(financial["approved_assumption_references"]),
        "FinancialScenario used source_assumption_ref set must equal approved_assumption_references",
    )
    for result_name in ["revenue_projection", "cost_projection", "cash_requirement"]:
        require(financial[result_name]["classification"] == "hypothesis", f"{result_name} must remain hypothesis")
        require(financial[result_name]["is_fixture_value"] is True, f"{result_name} must remain fixture value")
    expected_decision_refs = {
        "project_record_id": project["artifact_id"],
        "problem_frame_id": problem["artifact_id"],
        "system_map_id": system["artifact_id"],
        "predictive_hypothesis_id": predictive["artifact_id"],
        "financial_scenario_id": financial["artifact_id"],
    }
    for field, expected in expected_decision_refs.items():
        actual = decision["linked_upstream_artifact_ids"][field]
        require(actual == expected, f"DecisionRecord {field} must reference expected artifact {expected}, got {actual}")
    alternative_ids = {item["alternative_id"] for item in decision["alternatives_considered"]}
    rejected_ids = {item["alternative_id"] for item in decision["rejected_alternatives"]}
    require(decision["selected_alternative_id"] in alternative_ids, "selected_alternative_id does not resolve")
    require(decision["selected_alternative_id"] not in rejected_ids, "selected alternative cannot be rejected")
    require(rejected_ids.issubset(alternative_ids), "rejected alternative does not resolve")
    require(decision["selected_decision"]["decision_type"] == "limited_pilot", "final recommendation must remain limited pilot")
    for item in decision["evidence_summary"]:
        require(item["evidence_id"] in all_evidence, f"DecisionRecord evidence summary unresolved: {item['evidence_id']}")
        require(item["classification"] == "fact", "DecisionRecord evidence summary can only reference evidence facts")
        require(item["evidence_context"] == "synthetic_fixture", "DecisionRecord evidence summary must preserve synthetic context")
    for item in decision["predictive_hypotheses"]:
        require(item["classification"] == "predictive_hypothesis", "DecisionRecord converted predictive hypothesis")
        require(item["not_evidence"] is True, "DecisionRecord predictive hypothesis must carry not_evidence=true")
    for item in decision["financial_scenarios"]:
        require(item["classification"] == "hypothesis", "fixture financial scenario must remain hypothesis")
        require(item["uses_fixture_values"] is True, "financial summary must preserve fixture flag")
    allowed_decision_source_refs = (
        registries["artifacts"]
        | registries["evidence"]
        | registries["assumptions"]
        | registries["system_assumptions"]
        | registries["stakeholders"]
        | registries["relationships"]
        | registries["tensions"]
        | registries["dependencies"]
        | registries["unknowns"]
        | registries["predictive_signals"]
        | registries["cascades"]
        | registries["alternatives"]
        | registries["risks"]
        | registries["contradictions"]
        | registries["experiments"]
        | registries["success_criteria"]
        | registries["audit_events"]
        | registries["selected_decisions"]
    )
    for collection_name in ["risks", "unknowns", "contradictions"]:
        for item in decision[collection_name]:
            for ref in item["source_refs"]:
                require(ref in allowed_decision_source_refs, f"{collection_name} source_ref does not resolve: {ref}")
    unknown_text = json.dumps(decision["unknowns"], sort_keys=True)
    for unknown_id in predictive["uncertainty"]["unknowns_preserved"] + financial["uncertainty"]["unknowns_preserved"]:
        require(unknown_id in unknown_text, f"unknown dropped from DecisionRecord: {unknown_id}")


def expect_negative(name: str, mutator, expected_fragment: str, schemas, fixtures, results: list[str]) -> None:
    invalid = copy.deepcopy(fixtures)
    mutator(invalid)
    try:
        validate_official_schemas(schemas, invalid)
        validate_business_rules(invalid)
    except ContractValidationError as exc:
        message = str(exc)
        require(
            expected_fragment in message,
            f"negative test {name!r} failed for wrong reason. Expected fragment {expected_fragment!r}; got {message!r}",
        )
        results.append(name)
        print(f"NEGATIVE PASS: {name} -> {expected_fragment}")
        return
    raise ContractValidationError(f"negative test did not fail: {name}")


def run_negative_tests(schemas, fixtures) -> list[str]:
    tests = [
        (
            "malformed nested object",
            lambda f: f["project_record"].__setitem__("geography", "Berlin"),
            "schema validation failed",
        ),
        (
            "unexpected nested property",
            lambda f: f["system_map"]["stakeholders"][0].__setitem__("secret_note", "nope"),
            "schema validation failed",
        ),
        (
            "wrong array item type",
            lambda f: f["problem_frame"]["needs"].append("bad item"),
            "schema validation failed",
        ),
        (
            "unresolved artifact reference",
            lambda f: f["decision_record"]["linked_upstream_artifact_ids"].__setitem__("system_map_id", "missing"),
            "DecisionRecord system_map_id must reference expected artifact",
        ),
        (
            "unresolved evidence reference",
            lambda f: f["system_map"]["dependencies"][0]["evidence_refs"].append("ev_missing"),
            "unresolved evidence reference: ev_missing",
        ),
        (
            "unresolved stakeholder reference",
            lambda f: f["predictive_hypothesis"]["approved_input_references"]["stakeholder_ids"].append("stk_missing"),
            "PredictiveHypothesis has unresolved stakeholder reference",
        ),
        (
            "unapproved predictive assumption",
            lambda f: f["predictive_hypothesis"]["approved_input_references"]["assumption_ids"].append("asm_service_fee_per_use"),
            "PredictiveHypothesis uses unapproved predictive assumption",
        ),
        (
            "unapproved financial assumption",
            lambda f: f["financial_scenario"]["approved_assumption_references"].append("asm_staff_training"),
            "FinancialScenario uses unapproved financial assumption",
        ),
        (
            "changed assumption statement",
            lambda f: f["system_map"]["approved_assumptions"][0].__setitem__("statement", "changed"),
            "SystemMap changed assumption statement",
        ),
        (
            "approval-state contradiction",
            lambda f: f["problem_frame"]["human_approval"].__setitem__("state", "pending"),
            "schema validation failed",
        ),
        (
            "predictive classification changed to fact",
            lambda f: f["predictive_hypothesis"].__setitem__("classification", "fact"),
            "schema validation failed",
        ),
        (
            "predictive hypothesis inserted as evidence",
            lambda f: f["decision_record"]["predictive_hypotheses"][0].__setitem__("classification", "fact"),
            "DecisionRecord converted predictive hypothesis",
        ),
        (
            "probabilities not summing to 1",
            lambda f: f["predictive_hypothesis"]["simulated_stakeholder_responses"][0].__setitem__("undecided_likelihood", 0.5),
            "probabilities must sum to 1",
        ),
        (
            "selected alternative not resolving",
            lambda f: f["decision_record"].__setitem__("selected_alternative_id", "alt_missing"),
            "selected_alternative_id does not resolve",
        ),
        (
            "unknown dropped from DecisionRecord",
            lambda f: f["decision_record"].__setitem__("unknowns", []),
            "schema validation failed",
        ),
        (
            "non-synthetic evidence in golden case",
            lambda f: f["problem_frame"]["evidence_references"][0].__setitem__("evidence_context", "real_world"),
            "schema validation failed",
        ),
        (
            "unresolved DecisionRecord source_ref",
            lambda f: f["decision_record"]["risks"][0].__setitem__("source_refs", ["invented_ref"]),
            "risks source_ref does not resolve: invented_ref",
        ),
        (
            "existing artifact ID used in wrong typed upstream field",
            lambda f: f["decision_record"]["linked_upstream_artifact_ids"].__setitem__("system_map_id", f["project_record"]["artifact_id"]),
            "DecisionRecord system_map_id must reference expected artifact",
        ),
        (
            "SystemMap predictive approval escalation",
            lambda f: next(item for item in f["system_map"]["approved_assumptions"] if item["assumption_id"] == "asm_service_fee_per_use").__setitem__("approved_for_predictive_processing", True),
            "SystemMap escalated predictive approval: asm_service_fee_per_use",
        ),
        (
            "SystemMap financial approval escalation",
            lambda f: next(item for item in f["system_map"]["approved_assumptions"] if item["assumption_id"] == "asm_staff_training").__setitem__("approved_for_financial_processing", True),
            "SystemMap escalated financial approval: asm_staff_training",
        ),
        (
            "duplicate stable ID",
            lambda f: f["system_map"]["stakeholders"][1].__setitem__("stakeholder_id", f["system_map"]["stakeholders"][0]["stakeholder_id"]),
            "duplicate stable ID in stakeholders",
        ),
        (
            "financial assumption used but absent from approved_assumption_references",
            lambda f: f["financial_scenario"].__setitem__("approved_assumption_references", [ref for ref in f["financial_scenario"]["approved_assumption_references"] if ref != "asm_setup_buffer"]),
            "FinancialScenario used source_assumption_ref set must equal approved_assumption_references",
        ),
    ]
    results: list[str] = []
    for name, mutator, expected_fragment in tests:
        expect_negative(name, mutator, expected_fragment, schemas, fixtures, results)

    try:
        expect_negative(
            "unexpected runtime exception is not counted as negative pass",
            lambda f: (_ for _ in ()).throw(RuntimeError("boom from test mutator")),
            "boom from test mutator",
            schemas,
            fixtures,
            results,
        )
    except RuntimeError as exc:
        require("boom from test mutator" in str(exc), "unexpected runtime exception guard failed for wrong reason")
        results.append("unexpected runtime exception is not counted as negative pass")
        print("NEGATIVE HARNESS PASS: unexpected runtime exception is not counted as a negative pass -> boom from test mutator")
    return results

def main() -> int:
    schemas = {kind: load_json(SCHEMA_DIR / filename) for kind, filename in SCHEMA_FILES.items()}
    fixtures = {kind: load_json(FIXTURE_DIR / filename) for kind, filename in ARTIFACT_FILES.items()}
    validate_official_schemas(schemas, fixtures)
    print("Official schema validation passed for 6 schemas and 6 fixtures.")
    validate_business_rules(fixtures)
    print("Cross-artifact business validation passed.")
    results = run_negative_tests(schemas, fixtures)
    print(f"Negative tests passed: {len(results)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Contract validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
