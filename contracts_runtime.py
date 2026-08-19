from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_DIR = BASE_DIR / "contracts" / "v1"
ARTIFACT_SCHEMA_FILES = {
    "project_record": "project-record.schema.json",
    "problem_frame": "problem-frame.schema.json",
    "system_map": "system-map.schema.json",
    "predictive_hypothesis": "predictive-hypothesis.schema.json",
    "financial_scenario": "financial-scenario.schema.json",
    "decision_record": "decision-record.schema.json",
}
ARTIFACT_ORDER = list(ARTIFACT_SCHEMA_FILES)
UPSTREAM_REQUIREMENTS = {
    "problem_frame": {"project_record_id": "project_record"},
    "system_map": {"project_record_id": "project_record", "problem_frame_id": "problem_frame"},
    "predictive_hypothesis": {"project_record_id": "project_record", "problem_frame_id": "problem_frame", "system_map_id": "system_map"},
    "financial_scenario": {"project_record_id": "project_record", "problem_frame_id": "problem_frame", "system_map_id": "system_map"},
    "decision_record": {"project_record_id": "project_record", "problem_frame_id": "problem_frame", "system_map_id": "system_map", "predictive_hypothesis_id": "predictive_hypothesis", "financial_scenario_id": "financial_scenario"},
}


def load_schema(artifact_type: str) -> dict[str, Any]:
    if artifact_type not in ARTIFACT_SCHEMA_FILES:
        raise ValueError(f"Unsupported artifact type: {artifact_type}")
    return json.loads((SCHEMA_DIR / ARTIFACT_SCHEMA_FILES[artifact_type]).read_text(encoding="utf-8"))


def schema_errors(artifact_type: str, artifact: dict[str, Any]) -> list[dict[str, str]]:
    schema = load_schema(artifact_type)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = []
    for error in sorted(validator.iter_errors(artifact), key=lambda item: list(item.path)):
        path = ".".join(str(part) for part in error.path) or "root"
        errors.append({"path": path, "message": error.message})
    return errors


def runtime_errors(artifact_type: str, artifact: dict[str, Any], upstream: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    errors = []
    actual_type = artifact.get("artifact_type")
    if actual_type != artifact_type:
        errors.append({"path": "artifact_type", "message": f"artifact_type must be {artifact_type}, got {actual_type}"})
    artifact_id = artifact.get("artifact_id")
    if not is_safe_artifact_id(artifact_id):
        errors.append({"path": "artifact_id", "message": "artifact_id is not safe for local storage"})
    requirements = UPSTREAM_REQUIREMENTS.get(artifact_type, {})
    refs = artifact.get("linked_upstream_artifact_ids") if artifact_type == "decision_record" else artifact.get("preceding_artifacts")
    refs = refs or {}
    for field, upstream_type in requirements.items():
        upstream_artifact = upstream.get(upstream_type)
        if upstream_artifact is None:
            errors.append({"path": f"preceding_artifacts.{field}", "message": f"Missing upstream {upstream_type}; do not invent {field}"})
            continue
        expected = upstream_artifact.get("artifact_id")
        actual = refs.get(field)
        if actual != expected:
            location = "linked_upstream_artifact_ids" if artifact_type == "decision_record" else "preceding_artifacts"
            errors.append({"path": f"{location}.{field}", "message": f"Expected {expected} from {upstream_type}, got {actual}"})
    return errors



def privacy_gate_errors(artifact_type: str, artifact: dict[str, Any]) -> list[dict[str, str]]:
    if artifact_type != "project_record":
        return []
    declaration = artifact.get("synthetic_data_declaration") or {}
    if declaration.get("contains_identifiable_people") is not True:
        return []
    errors: list[dict[str, str]] = []
    consent = declaration.get("privacy_consent")
    if not isinstance(consent, dict):
        errors.append({
            "path": "synthetic_data_declaration.privacy_consent",
            "message": "ProjectRecord identifiable people require privacy_consent",
        })
    if declaration.get("approved_for_predictive_processing") is True:
        allows_predictive = isinstance(consent, dict) and consent.get("allows_predictive_processing") is True
        if not allows_predictive:
            errors.append({
                "path": "synthetic_data_declaration.approved_for_predictive_processing",
                "message": "ProjectRecord identifiable people cannot be approved for predictive processing without explicit predictive consent",
            })
    return errors


def current_reference_errors(artifact_type: str, artifact: dict[str, Any], upstream: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    if artifact_type != "project_record":
        return []
    errors: list[dict[str, str]] = []
    refs = artifact.get("current_artifact_references") or {}
    field_to_type = {
        "problem_frame_id": "problem_frame",
        "system_map_id": "system_map",
        "predictive_hypothesis_id": "predictive_hypothesis",
        "financial_scenario_id": "financial_scenario",
        "decision_record_id": "decision_record",
    }
    for field, downstream_type in field_to_type.items():
        downstream_artifact = upstream.get(downstream_type)
        if downstream_artifact is None:
            continue
        expected = downstream_artifact.get("artifact_id")
        actual = refs.get(field)
        if actual != expected:
            errors.append({"path": f"current_artifact_references.{field}", "message": f"Expected {expected} from {downstream_type}, got {actual}"})
    return errors


def indexed(items: list[dict[str, Any]], id_field: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in items or []:
        item_id = item.get(id_field)
        if isinstance(item_id, str):
            result[item_id] = item
    return result


def system_registries(upstream: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any] | set[str]]:
    problem = upstream.get("problem_frame") or {}
    system = upstream.get("system_map") or {}
    problem_evidence = indexed(problem.get("evidence_references", []), "evidence_id")
    system_evidence = indexed(system.get("evidence_references", []), "evidence_id")
    evidence = problem_evidence | system_evidence
    approved_assumptions = indexed(system.get("approved_assumptions", []), "assumption_id")
    stakeholders = indexed(system.get("stakeholders", []), "stakeholder_id")
    relationships = indexed(system.get("relationships", []), "relationship_id")
    return {
        "evidence": evidence,
        "approved_assumptions": approved_assumptions,
        "approved_predictive": {key for key, item in approved_assumptions.items() if item.get("approved_for_predictive_processing") is True},
        "approved_financial": {key for key, item in approved_assumptions.items() if item.get("approved_for_financial_processing") is True},
        "stakeholders": set(stakeholders),
        "relationships": set(relationships),
    }


def predictive_rule_errors(artifact: dict[str, Any], upstream: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    if "system_map" not in upstream:
        return []
    errors: list[dict[str, str]] = []
    registries = system_registries(upstream)
    refs = artifact.get("approved_input_references") or {}
    if refs.get("system_map_id") != upstream["system_map"].get("artifact_id"):
        errors.append({"path": "approved_input_references.system_map_id", "message": "PredictiveHypothesis system_map_id must reference upstream SystemMap"})
    for field, registry_name, message in [
        ("stakeholder_ids", "stakeholders", "PredictiveHypothesis has unresolved stakeholder reference"),
        ("relationship_ids", "relationships", "PredictiveHypothesis has unresolved relationship reference"),
        ("evidence_ids", "evidence", "PredictiveHypothesis has unresolved evidence reference"),
    ]:
        allowed = registries[registry_name]
        missing = sorted(set(refs.get(field, [])) - set(allowed))
        if missing:
            errors.append({"path": f"approved_input_references.{field}", "message": f"{message}: {', '.join(missing)}"})
    assumption_ids = set(refs.get("assumption_ids", []))
    unapproved = sorted(assumption_ids - registries["approved_predictive"])
    if unapproved:
        errors.append({"path": "approved_input_references.assumption_ids", "message": f"PredictiveHypothesis uses unapproved predictive assumption: {', '.join(unapproved)}"})
    used_ids = {item.get("assumption_id") for item in artifact.get("assumptions_used", [])}
    if used_ids != assumption_ids:
        errors.append({"path": "assumptions_used", "message": "assumptions_used must exactly match approved_input_references.assumption_ids"})
    approved_assumptions = registries["approved_assumptions"]
    for item in artifact.get("assumptions_used", []):
        assumption_id = item.get("assumption_id")
        source = approved_assumptions.get(assumption_id) if isinstance(approved_assumptions, dict) else None
        if source and item.get("statement") != source.get("statement"):
            errors.append({"path": "assumptions_used", "message": f"PredictiveHypothesis copied changed assumption: {assumption_id}"})
    for index, response in enumerate(artifact.get("simulated_stakeholder_responses", [])):
        if response.get("stakeholder_id") not in registries["stakeholders"]:
            errors.append({"path": f"simulated_stakeholder_responses.{index}.stakeholder_id", "message": "PredictiveHypothesis response stakeholder does not resolve"})
        total = sum(float(response.get(field, 0)) for field in ["adoption_likelihood", "resistance_likelihood", "undecided_likelihood"])
        if abs(total - 1.0) > 0.000001:
            errors.append({"path": f"simulated_stakeholder_responses.{index}", "message": f"probabilities must sum to 1 for {response.get('stakeholder_id')}"})
        if response.get("classification") != "hypothesis":
            errors.append({"path": f"simulated_stakeholder_responses.{index}.classification", "message": "simulated stakeholder responses must remain hypotheses"})
    for collection_name in ["adoption_signals", "resistance_signals"]:
        for index, signal in enumerate(artifact.get(collection_name, [])):
            if signal.get("classification") != "hypothesis":
                errors.append({"path": f"{collection_name}.{index}.classification", "message": f"predictive signal must remain hypothesis: {signal.get('signal_id')}"})
            missing = sorted(set(signal.get("stakeholder_ids", [])) - registries["stakeholders"])
            if missing:
                errors.append({"path": f"{collection_name}.{index}.stakeholder_ids", "message": f"predictive signal stakeholder reference unresolved: {signal.get('signal_id')}"})
    for index, cascade in enumerate(artifact.get("possible_cascades", [])):
        if cascade.get("classification") != "hypothesis":
            errors.append({"path": f"possible_cascades.{index}.classification", "message": f"cascade must remain hypothesis: {cascade.get('cascade_id')}"})
    return errors


def financial_rule_errors(artifact: dict[str, Any], upstream: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    if "system_map" not in upstream:
        return []
    errors: list[dict[str, str]] = []
    registries = system_registries(upstream)
    approved_refs = set(artifact.get("approved_assumption_references", []))
    unapproved = sorted(approved_refs - registries["approved_financial"])
    if unapproved:
        errors.append({"path": "approved_assumption_references", "message": f"FinancialScenario uses unapproved financial assumption: {', '.join(unapproved)}"})
    used_refs: set[str] = set()
    for collection_name in ["pricing_assumptions", "cost_assumptions", "volume_assumptions"]:
        for index, item in enumerate(artifact.get(collection_name, [])):
            ref = item.get("source_assumption_ref")
            if isinstance(ref, str):
                used_refs.add(ref)
            if ref not in registries["approved_financial"]:
                errors.append({"path": f"{collection_name}.{index}.source_assumption_ref", "message": f"{collection_name} source assumption not approved for financial processing: {ref}"})
    if used_refs != approved_refs:
        errors.append({"path": "approved_assumption_references", "message": "FinancialScenario used source_assumption_ref set must equal approved_assumption_references"})
    return errors


def decision_rule_errors(artifact: dict[str, Any], upstream: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    required = {"problem_frame", "system_map", "predictive_hypothesis", "financial_scenario"}
    if not required.issubset(upstream):
        return []
    errors: list[dict[str, str]] = []
    registries = system_registries(upstream)
    evidence = registries["evidence"]
    for index, item in enumerate(artifact.get("evidence_summary", [])):
        evidence_id = item.get("evidence_id")
        if evidence_id not in evidence:
            errors.append({"path": f"evidence_summary.{index}.evidence_id", "message": f"DecisionRecord evidence summary unresolved: {evidence_id}"})
        if item.get("classification") != "fact":
            errors.append({"path": f"evidence_summary.{index}.classification", "message": "DecisionRecord evidence summary can only reference evidence facts"})
    for index, item in enumerate(artifact.get("predictive_hypotheses", [])):
        if item.get("classification") != "predictive_hypothesis":
            errors.append({"path": f"predictive_hypotheses.{index}.classification", "message": "DecisionRecord converted predictive hypothesis"})
        if item.get("not_evidence") is not True:
            errors.append({"path": f"predictive_hypotheses.{index}.not_evidence", "message": "DecisionRecord predictive hypothesis must carry not_evidence=true"})
    approval = artifact.get("facilitator_approval") or {}
    if approval.get("state") != "approved" or approval.get("approved_by_role") != "facilitator" or not approval.get("approved_at"):
        errors.append({"path": "facilitator_approval", "message": "DecisionRecord requires facilitator approval"})
    return errors


def business_rule_errors(artifact_type: str, artifact: dict[str, Any], upstream: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    if artifact_type == "predictive_hypothesis":
        return predictive_rule_errors(artifact, upstream)
    if artifact_type == "financial_scenario":
        return financial_rule_errors(artifact, upstream)
    if artifact_type == "decision_record":
        return decision_rule_errors(artifact, upstream)
    return []


def validate_artifact(artifact_type: str, artifact: dict[str, Any], upstream: dict[str, dict[str, Any]] | None = None) -> list[dict[str, str]]:
    upstream = upstream or {}
    return schema_errors(artifact_type, artifact) + runtime_errors(artifact_type, artifact, upstream) + current_reference_errors(artifact_type, artifact, upstream) + privacy_gate_errors(artifact_type, artifact) + business_rule_errors(artifact_type, artifact, upstream)


def is_safe_artifact_id(value: Any) -> bool:
    return isinstance(value, str) and bool(value) and value[0].isalnum() and all(ch.isalnum() or ch in {"_", "-"} for ch in value)
