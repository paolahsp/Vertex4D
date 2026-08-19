from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import contracts_runtime

BASE_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = Path(os.getenv("VERTEX4D_RUNTIME_DIR", BASE_DIR / ".vertex_runtime" / "runs"))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def create_run_id() -> str:
    return f"run_{uuid.uuid4().hex[:12]}"


def safe_artifact_type(artifact_type: str) -> str:
    if artifact_type not in contracts_runtime.ARTIFACT_SCHEMA_FILES:
        raise ValueError(f"Unsupported artifact type: {artifact_type}")
    return artifact_type


def run_dir(run_id: str) -> Path:
    if not contracts_runtime.is_safe_artifact_id(run_id):
        raise ValueError("run_id is not safe for local storage")
    return RUNTIME_DIR / run_id


def artifact_path(run_id: str, artifact_type: str) -> Path:
    return run_dir(run_id) / f"{safe_artifact_type(artifact_type)}.json"


def load_artifact(run_id: str, artifact_type: str) -> dict[str, Any] | None:
    path = artifact_path(run_id, artifact_type)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_upstream(run_id: str, artifact_type: str) -> dict[str, dict[str, Any]]:
    if artifact_type == "project_record":
        candidate_types = contracts_runtime.ARTIFACT_ORDER[1:]
    else:
        index = contracts_runtime.ARTIFACT_ORDER.index(artifact_type)
        candidate_types = contracts_runtime.ARTIFACT_ORDER[:index]
    upstream = {}
    for upstream_type in candidate_types:
        artifact = load_artifact(run_id, upstream_type)
        if artifact is not None:
            upstream[upstream_type] = artifact
    return upstream


def save_artifact(run_id: str, artifact_type: str, artifact: dict[str, Any]) -> Path:
    path = artifact_path(run_id, artifact_type)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def artifact_summary(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_type": artifact.get("artifact_type"),
        "artifact_id": artifact.get("artifact_id"),
        "project_id": artifact.get("project_id"),
        "status": artifact.get("status"),
        "approval_state": artifact.get("approval_state"),
        "updated_at": artifact.get("updated_at"),
    }


def build_project_record(run_id: str, team: dict[str, Any], title: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    metadata = metadata or {}
    now = utc_now()
    safe_run = run_id.replace("-", "_")
    project_id = f"project_{safe_run}"
    challenge = str(metadata.get("challenge_statement") or team.get("challenge_desc") or title).strip()
    venture_stage = metadata.get("venture_stage") if metadata.get("venture_stage") in {"idea", "discovery", "prototype", "pilot", "launched"} else "idea"
    operating_scope = metadata.get("operating_scope") if metadata.get("operating_scope") in {"local", "regional", "national", "international"} else "local"
    impact_area = metadata.get("impact_area")
    if isinstance(impact_area, str):
        impact_area = [item.strip() for item in impact_area.split(",") if item.strip()]
    if not isinstance(impact_area, list) or not impact_area:
        impact_area = ["entrepreneurship"]
    is_synthetic = bool(metadata.get("is_synthetic", False))
    predictive_ok = bool(metadata.get("approved_for_predictive_processing", True))
    contains_identifiable_people = bool(metadata.get("contains_identifiable_people", False))
    privacy_consent = metadata.get("privacy_consent")
    consent_record_ref = str(metadata.get("consent_record_ref") or "").strip()
    if contains_identifiable_people and not isinstance(privacy_consent, dict) and consent_record_ref:
        privacy_consent = {
            "consent_basis": metadata.get("consent_basis", "explicit_consent"),
            "consent_record_ref": consent_record_ref,
            "granted_by_role": metadata.get("granted_by_role", "founder"),
            "granted_at": metadata.get("granted_at") or now,
            "allows_predictive_processing": bool(metadata.get("allows_predictive_processing", False)),
        }
    approval_state = metadata.get("approval_state") if metadata.get("approval_state") in {"pending", "approved", "rejected"} else "pending"
    approved_by_role = metadata.get("approved_by_role") if approval_state == "approved" else None
    approved_at = now if approval_state == "approved" else None
    synthetic_data_declaration = {
        "is_synthetic": is_synthetic,
        "contains_identifiable_people": contains_identifiable_people,
        "approved_for_predictive_processing": predictive_ok,
        "statement": "Synthetic golden-case data for a VERTEX pilot run." if is_synthetic else "Founder-supplied project data for a real VERTEX Golden Path run."
    }
    if privacy_consent is not None:
        synthetic_data_declaration["privacy_consent"] = privacy_consent
    return {
        "schema_version": "1.1.0",
        "artifact_type": "project_record",
        "artifact_id": f"project_record_{safe_run}",
        "project_id": project_id,
        "created_at": now,
        "created_by_role": "founder",
        "status": "draft",
        "provenance": {
            "source_kind": "user_supplied",
            "source_label": "VERTEX Golden Path run creation",
            "ip_owner": team.get("team_name") or "VERTEX team",
            "external_components_used": [],
            "notes": "Draft project record created when the team starts a Golden Path run."
        },
        "human_approval": {
            "required": True,
            "state": approval_state,
            "approved_by_role": approved_by_role,
            "approved_at": approved_at,
            "notes": "Pending founder/facilitator review." if approval_state == "pending" else "Approved during Golden Path run creation."
        },
        "validation_errors": [],
        "project_name": title,
        "venture_description": challenge,
        "challenge_statement": challenge,
        "venture_stage": venture_stage,
        "geography": {
            "primary_city": str(metadata.get("primary_city") or "Unknown").strip() or "Unknown",
            "country": str(metadata.get("country") or "Unknown").strip() or "Unknown",
            "operating_scope": operating_scope
        },
        "impact_area": impact_area,
        "cohort_program_context": {
            "program_name": "VERTEX 4D",
            "cohort_name": "pilot",
            "facilitator_role": "facilitator",
            "notes": "Created from the app run flow."
        },
        "synthetic_data_declaration": synthetic_data_declaration,
        "current_artifact_references": {
            "problem_frame_id": f"problem_frame_{safe_run}",
            "system_map_id": f"system_map_{safe_run}",
            "predictive_hypothesis_id": f"predictive_hypothesis_{safe_run}",
            "financial_scenario_id": f"financial_scenario_{safe_run}",
            "decision_record_id": f"decision_record_{safe_run}"
        },
        "revision": 1,
        "updated_at": now
    }