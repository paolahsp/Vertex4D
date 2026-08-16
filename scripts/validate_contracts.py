from __future__ import annotations

import copy
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


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


class ValidationError(Exception):
    pass


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def check_format(value: Any, fmt: str, path: str) -> None:
    if value is None:
        return
    if fmt == "date-time":
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    elif fmt == "date":
        datetime.strptime(value, "%Y-%m-%d")
    else:
        raise ValidationError(f"{path}: unsupported schema format {fmt!r}")


def validate_schema_subset(schema: dict[str, Any], value: Any, path: str = "$") -> None:
    expected_type = schema.get("type")
    if expected_type is not None:
        expected = expected_type if isinstance(expected_type, list) else [expected_type]
        actual = json_type(value)
        if actual == "integer" and "number" in expected:
            actual = "number"
        if actual not in expected:
            raise ValidationError(f"{path}: expected {expected}, got {json_type(value)}")

    if "const" in schema and value != schema["const"]:
        raise ValidationError(f"{path}: expected const {schema['const']!r}, got {value!r}")

    if "enum" in schema and value not in schema["enum"]:
        raise ValidationError(f"{path}: expected one of {schema['enum']!r}, got {value!r}")

    if "pattern" in schema and isinstance(value, str) and re.match(schema["pattern"], value) is None:
        raise ValidationError(f"{path}: value {value!r} does not match {schema['pattern']!r}")

    if "format" in schema and isinstance(value, str):
        check_format(value, schema["format"], path)

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise ValidationError(f"{path}: value {value!r} below minimum {schema['minimum']!r}")
        if "maximum" in schema and value > schema["maximum"]:
            raise ValidationError(f"{path}: value {value!r} above maximum {schema['maximum']!r}")

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                raise ValidationError(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = set(value) - set(properties)
            if extra:
                raise ValidationError(f"{path}: unexpected properties {sorted(extra)!r}")
        for key, child_schema in properties.items():
            if key in value:
                validate_schema_subset(child_schema, value[key], f"{path}.{key}")

    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            validate_schema_subset(schema["items"], item, f"{path}[{index}]")


def walk_values(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_values(child)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def validate_common_contract_fields(artifact_type: str, artifact: dict[str, Any]) -> None:
    require(artifact["schema_version"] == "1.0.0", f"{artifact_type}: unexpected schema_version")
    require(artifact["artifact_type"] == artifact_type, f"{artifact_type}: artifact_type mismatch")
    require(not artifact["validation_errors"], f"{artifact_type}: validation_errors must be empty in golden case")
    approval = artifact["human_approval"]
    require(approval["required"] is True, f"{artifact_type}: human approval must be explicit")
    require(approval["state"] == "approved", f"{artifact_type}: fixture must be approved")
    require(artifact["provenance"]["source_kind"] == "synthetic_fixture", f"{artifact_type}: fixture must be synthetic")
    require(artifact["provenance"]["external_components_used"] == [], f"{artifact_type}: external component use must be empty")


def validate_cross_artifact_rules(fixtures: dict[str, dict[str, Any]]) -> None:
    project_ids = {artifact["project_id"] for artifact in fixtures.values()}
    require(len(project_ids) == 1, "all artifacts must use the same project_id")

    artifacts_by_id = {artifact["artifact_id"]: artifact for artifact in fixtures.values()}
    for artifact_type, artifact in fixtures.items():
        validate_common_contract_fields(artifact_type, artifact)

    project = fixtures["project_record"]
    refs = project["current_artifact_references"]
    require(refs["problem_frame_id"] in artifacts_by_id, "project current problem_frame_id does not resolve")
    require(refs["system_map_id"] in artifacts_by_id, "project current system_map_id does not resolve")
    require(refs["predictive_hypothesis_id"] in artifacts_by_id, "project current predictive_hypothesis_id does not resolve")
    require(refs["financial_scenario_id"] in artifacts_by_id, "project current financial_scenario_id does not resolve")
    require(refs["decision_record_id"] in artifacts_by_id, "project current decision_record_id does not resolve")
    require(project["synthetic_data_declaration"]["is_synthetic"] is True, "project must declare synthetic data")
    require(project["synthetic_data_declaration"]["contains_identifiable_people"] is False, "project must exclude identifiable people")

    problem = fixtures["problem_frame"]
    system = fixtures["system_map"]
    predictive = fixtures["predictive_hypothesis"]
    financial = fixtures["financial_scenario"]
    decision = fixtures["decision_record"]

    require(problem["preceding_artifacts"]["project_record_id"] == project["artifact_id"], "problem frame must link project")
    require(system["preceding_artifacts"]["problem_frame_id"] == problem["artifact_id"], "system map must link problem frame")
    require(predictive["preceding_artifacts"]["system_map_id"] == system["artifact_id"], "predictive hypothesis must link system map")
    require(financial["preceding_artifacts"]["system_map_id"] == system["artifact_id"], "financial scenario must link system map")

    problem_evidence = {item["evidence_id"] for item in problem["evidence_references"]}
    system_evidence = {item["evidence_id"] for item in system["evidence_references"]}
    all_evidence = problem_evidence | system_evidence
    for artifact in [problem, system]:
        for node in walk_values(artifact):
            for evidence_ref in node.get("evidence_refs", []):
                require(evidence_ref in all_evidence, f"evidence reference {evidence_ref!r} does not resolve")

    stakeholder_ids = {item["stakeholder_id"] for item in system["stakeholders"]}
    relationship_ids = {item["relationship_id"] for item in system["relationships"]}
    for relationship in system["relationships"]:
        require(relationship["from_stakeholder_id"] in stakeholder_ids, f"relationship {relationship['relationship_id']} source does not resolve")
        require(relationship["to_stakeholder_id"] in stakeholder_ids, f"relationship {relationship['relationship_id']} target does not resolve")
    require(all(item["is_identifiable_person"] is False for item in system["stakeholders"]), "system map must not include identifiable people")

    approved_predictive = {
        item["assumption_id"]
        for item in system["approved_assumptions"]
        if item["approved_for_predictive_processing"] is True
    }
    approved_financial = {
        item["assumption_id"]
        for item in system["approved_assumptions"]
        if item["approved_for_financial_processing"] is True
    }
    predictive_refs = predictive["approved_input_references"]
    require(set(predictive_refs["stakeholder_ids"]).issubset(stakeholder_ids), "predictive stakeholder references must resolve")
    require(set(predictive_refs["relationship_ids"]).issubset(relationship_ids), "predictive relationship references must resolve")
    require(set(predictive_refs["assumption_ids"]).issubset(approved_predictive), "predictive hypothesis must use only approved predictive assumptions")
    require(set(predictive_refs["evidence_ids"]).issubset(all_evidence), "predictive evidence references must resolve")
    require(predictive["classification"] == "predictive_hypothesis", "predictive artifact must stay classified as predictive_hypothesis")
    require("not direct evidence" in predictive["warning"], "predictive warning must state it is not direct evidence")
    for response in predictive["simulated_stakeholder_responses"]:
        require(response["stakeholder_id"] in stakeholder_ids, "simulated stakeholder response must resolve")
        require(response["classification"] == "hypothesis", "simulated stakeholder responses must stay hypotheses")

    require(set(financial["approved_assumption_references"]).issubset(approved_financial), "financial scenario must use only approved financial assumptions")
    for collection_name in ["pricing_assumptions", "cost_assumptions", "volume_assumptions"]:
        for item in financial[collection_name]:
            require(item["is_fixture_value"] is True, f"{collection_name} must be marked as fixture values")
            require(item["source_assumption_ref"] in approved_financial, f"{collection_name} source assumption must be approved for financial processing")
    for result_name in ["revenue_projection", "cost_projection", "cash_requirement"]:
        require(financial[result_name]["is_fixture_value"] is True, f"{result_name} must be a fixture value")
        require(financial[result_name]["classification"] == "hypothesis", f"{result_name} must not be represented as fact")

    upstream = decision["linked_upstream_artifact_ids"]
    require(upstream["project_record_id"] == project["artifact_id"], "decision must reference project record")
    require(upstream["problem_frame_id"] == problem["artifact_id"], "decision must reference problem frame")
    require(upstream["system_map_id"] == system["artifact_id"], "decision must reference system map")
    require(upstream["predictive_hypothesis_id"] == predictive["artifact_id"], "decision must reference predictive hypothesis")
    require(upstream["financial_scenario_id"] == financial["artifact_id"], "decision must reference financial scenario")
    require(decision["selected_decision"]["decision_type"] == "limited_pilot", "golden case must recommend limited pilot")
    for item in decision["predictive_hypotheses"]:
        require(item["classification"] == "predictive_hypothesis", "decision must not convert predictive hypothesis into evidence")
        require(item["not_evidence"] is True, "decision predictive hypotheses must carry not_evidence=true")
    decision_unknown_text = json.dumps(decision["unknowns"], sort_keys=True)
    for unknown_id in predictive["uncertainty"]["unknowns_preserved"]:
        require(unknown_id in decision_unknown_text, f"unknown {unknown_id!r} must be preserved downstream")


def validate_negative_case(fixtures: dict[str, dict[str, Any]]) -> None:
    invalid = copy.deepcopy(fixtures)
    invalid["decision_record"]["predictive_hypotheses"][0]["classification"] = "fact"
    try:
        validate_cross_artifact_rules(invalid)
    except ValidationError:
        return
    raise ValidationError("negative test failed: predictive hypothesis was accepted as evidence")


def main() -> int:
    schemas = {kind: load_json(SCHEMA_DIR / filename) for kind, filename in SCHEMA_FILES.items()}
    fixtures = {kind: load_json(FIXTURE_DIR / filename) for kind, filename in ARTIFACT_FILES.items()}

    for kind, schema in schemas.items():
        require(schema["$schema"] == "https://json-schema.org/draft/2020-12/schema", f"{kind}: schema must use Draft 2020-12")
        require(schema["additionalProperties"] is False, f"{kind}: top-level additionalProperties must be false")
        validate_schema_subset(schema, fixtures[kind], f"fixtures.{kind}")

    validate_cross_artifact_rules(fixtures)
    validate_negative_case(fixtures)
    print("Validated 6 schemas, 6 fixtures, cross-artifact references, approval gates and negative case.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Contract validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
