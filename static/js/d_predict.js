(function () {
  const storageKey = "vertex_current_run_id";
  const runId = new URLSearchParams(window.location.search).get("run_id") || localStorage.getItem(storageKey);
  const state = { project: null, problem: null, system: null, draft: null };
  const warningText = "This output is a bounded simulation hypothesis. It is not direct evidence, a factual prediction or a conclusion about identifiable people.";

  const $ = (id) => document.getElementById(id);
  const status = $("dp-status");
  const buildButton = $("build-hypothesis");
  const saveButton = $("save-hypothesis");

  function setText(id, value) {
    const node = $(id);
    if (node) node.textContent = value;
  }

  function escapeHtml(value) {
    return String(value || "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
  }

  function pct(value) {
    return `${Math.round(Number(value || 0) * 100)}%`;
  }

  function round2(value) {
    return Math.round(Number(value || 0) * 100) / 100;
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function unique(items) {
    return Array.from(new Set(items.filter(Boolean)));
  }

  function safeId(value, fallback) {
    const raw = String(value || fallback || "id").toLowerCase().replace(/[^a-z0-9_-]+/g, "_").replace(/^_+|_+$/g, "");
    return raw || String(fallback || "id");
  }

  function updateLinks() {
    document.querySelectorAll("[data-run-link]").forEach((link) => {
      if (!runId) return;
      const url = new URL(link.getAttribute("href"), window.location.origin);
      url.searchParams.set("run_id", runId);
      link.setAttribute("href", `${url.pathname}${url.search}`);
    });
  }

  async function loadArtifact(type) {
    const response = await fetch(`/api/vertex/runs/${encodeURIComponent(runId)}/artifacts/${type}`);
    if (!response.ok) throw new Error(`${type} is missing from this run`);
    const result = await response.json();
    return result.artifact || result;
  }

  function approvedPredictiveAssumptions() {
    return (state.system?.approved_assumptions || []).filter((item) => item.approved_for_predictive_processing === true);
  }

  function stakeholderScore(stakeholder, index, assumptions) {
    const influence = { low: 0.08, medium: 0.14, high: 0.2 }[stakeholder.influence] || 0.12;
    const interest = { low: -0.04, medium: 0.02, high: 0.08 }[stakeholder.interest] || 0.02;
    const incentiveText = (stakeholder.incentives || []).join(" ").toLowerCase();
    const frictionWords = ["avoid", "burden", "slow", "risk", "complaint", "uncertain", "limited"];
    const supportWords = ["prove", "reduce", "convenience", "support", "maintain", "predictable", "visible"];
    const friction = frictionWords.some((word) => incentiveText.includes(word)) ? -0.08 : 0;
    const support = supportWords.some((word) => incentiveText.includes(word)) ? 0.08 : 0;
    const assumptionLift = Math.min(0.12, assumptions.length * 0.025);
    const relationLift = Math.min(0.1, relationshipsFor(stakeholder.stakeholder_id).length * 0.025);
    const adoption = clamp(0.42 + influence + interest + support + friction + assumptionLift + relationLift - index * 0.025, 0.18, 0.78);
    const undecided = clamp(0.06 + (stakeholder.influence === "medium" ? 0.04 : 0) + (stakeholder.interest === "medium" ? 0.03 : 0), 0.02, 0.18);
    const resistance = clamp(1 - adoption - undecided, 0.14, 0.78);
    const total = adoption + resistance + undecided;
    return {
      adoption_likelihood: round2(adoption / total),
      resistance_likelihood: round2(resistance / total),
      undecided_likelihood: round2(1 - round2(adoption / total) - round2(resistance / total))
    };
  }

  function relationshipsFor(stakeholderId) {
    return (state.system?.relationships || []).filter((rel) => rel.from_stakeholder_id === stakeholderId || rel.to_stakeholder_id === stakeholderId);
  }

  function stakeholderSentence(stakeholder, score) {
    const label = stakeholder.label || stakeholder.stakeholder_id;
    if (score.adoption_likelihood >= score.resistance_likelihood + 0.12) {
      return `${label} may support the next step if the workflow is visible, low-friction and tied to the incentives already mapped in SynapMap.`;
    }
    if (score.resistance_likelihood >= score.adoption_likelihood + 0.12) {
      return `${label} may resist if the mapped dependencies add work, uncertainty or social friction before value is proven.`;
    }
    return `${label} may remain divided until the team tests the strongest assumption with a small observable experiment.`;
  }

  function collectEvidenceIds(assumptions) {
    const fromAssumptions = assumptions.flatMap((item) => item.evidence_refs || item.evidence_ids || []);
    const fromSystem = (state.system?.evidence_references || []).map((item) => item.evidence_id);
    const fromProblem = (state.problem?.evidence_references || []).map((item) => item.evidence_id);
    return unique([...fromAssumptions, ...fromSystem, ...fromProblem]).slice(0, 8);
  }

  function collectUnknownIds() {
    const unknowns = [
      ...(state.problem?.unknowns || []).map((item) => item.id),
      ...(state.system?.unknowns || []).map((item) => item.id)
    ];
    return unique(unknowns).slice(0, 6);
  }

  function buildQbiReading(stakeholders, relationships, assumptions, responses, signalIds, unknownIds) {
    const runSuffix = safeId(runId || "runless");
    const stakeholderIds = stakeholders.map((item) => item.stakeholder_id);
    const relationshipIds = relationships.map((item) => item.relationship_id);
    const assumptionIds = assumptions.map((item) => item.assumption_id);
    const highestResistance = responses.reduce((current, item) => (
      item.resistance_likelihood > current.resistance_likelihood ? item : current
    ), responses[0]);
    const highestAdoption = responses.reduce((current, item) => (
      item.adoption_likelihood > current.adoption_likelihood ? item : current
    ), responses[0]);
    const adoptionGap = Math.abs(highestAdoption.adoption_likelihood - highestResistance.resistance_likelihood);
    const collapseRisk = unknownIds.length > 2 || adoptionGap < 0.08 ? "high" : adoptionGap < 0.18 ? "medium" : "low";
    const contextSeverity = relationships.length < 2 || assumptions.length < 2 ? "high" : collapseRisk === "high" ? "medium" : "low";
    return {
      qbi_version: "qbi_lite_v0.1",
      model_boundary: "Product-facing QBI reading only; this artifact does not execute the full formal QBI model.",
      interpretation_states: [
        {
          state_id: `qbi_state_adoption_${runSuffix}`,
          statement: `${highestAdoption.stakeholder_id} may read the same venture as a low-friction adoption path if the approved assumptions hold.`,
          stakeholder_ids: [highestAdoption.stakeholder_id],
          assumption_ids: assumptionIds.slice(0, Math.max(1, Math.min(2, assumptionIds.length))),
          classification: "hypothesis"
        },
        {
          state_id: `qbi_state_resistance_${runSuffix}`,
          statement: `${highestResistance.stakeholder_id} may read the same venture as added burden or risk until the context is tested.`,
          stakeholder_ids: [highestResistance.stakeholder_id],
          assumption_ids: assumptionIds.slice(-Math.max(1, Math.min(2, assumptionIds.length))),
          classification: "hypothesis"
        }
      ],
      actor_correlations: [
        {
          correlation_id: `qbi_corr_system_${runSuffix}`,
          statement: "Stakeholder responses are treated as correlated through mapped relationships, so support or resistance can move through the system rather than appearing one actor at a time.",
          stakeholder_ids: stakeholderIds.slice(0, Math.max(1, Math.min(3, stakeholderIds.length))),
          relationship_ids: relationshipIds.slice(0, Math.max(1, Math.min(3, relationshipIds.length))),
          classification: "hypothesis"
        }
      ],
      context_loss_vectors: [
        {
          vector_id: `qbi_context_loss_${runSuffix}`,
          statement: "The scenario can lose coherence if the team commits before observing whether mapped friction, workload or approval constraints appear in context.",
          source_refs: unique([relationshipIds[0], assumptionIds[0], unknownIds[0]]).slice(0, 3),
          severity: contextSeverity,
          classification: "hypothesis"
        }
      ],
      commitment_pressure: {
        statement: "D-Predict keeps adoption, resistance and undecided readings open until a DecisionRecord collapses them into a reviewed next commitment.",
        collapse_risk: collapseRisk,
        decision_trigger_refs: unique([signalIds.adoption, signalIds.resistance, unknownIds[0]]).slice(0, 3),
        classification: "hypothesis"
      }
    };
  }

  function buildDraft() {
    if (!runId) throw new Error("Create a Golden Path run first.");
    if (!state.project || !state.problem || !state.system) throw new Error("D-Predict requires ProjectRecord, ProblemFrame and SystemMap upstream artifacts.");
    const assumptions = approvedPredictiveAssumptions();
    if (!assumptions.length) throw new Error("D-Predict requires at least one SystemMap assumption approved for predictive processing.");
    const stakeholders = (state.system.stakeholders || []).slice(0, 4);
    const relationships = (state.system.relationships || []).slice(0, 6);
    const evidenceIds = collectEvidenceIds(assumptions);
    const unknownIds = collectUnknownIds();
    if (!stakeholders.length) throw new Error("SystemMap must include at least one stakeholder.");
    if (!relationships.length) throw new Error("SystemMap must include at least one relationship.");
    if (!evidenceIds.length) throw new Error("SystemMap or ProblemFrame must include evidence references.");
    if (!unknownIds.length) throw new Error("ProblemFrame or SystemMap must preserve at least one unknown.");

    const now = new Date().toISOString();
    const runSuffix = runId.replaceAll("-", "_");
    const responses = stakeholders.map((stakeholder, index) => {
      const score = stakeholderScore(stakeholder, index, assumptions);
      return {
        stakeholder_id: stakeholder.stakeholder_id,
        simulated_response: stakeholderSentence(stakeholder, score),
        adoption_likelihood: score.adoption_likelihood,
        resistance_likelihood: score.resistance_likelihood,
        classification: "hypothesis",
        undecided_likelihood: score.undecided_likelihood
      };
    });
    const avgAdoption = responses.reduce((sum, item) => sum + item.adoption_likelihood, 0) / responses.length;
    const avgResistance = responses.reduce((sum, item) => sum + item.resistance_likelihood, 0) / responses.length;
    const uncertaintyLevel = assumptions.length < 2 || stakeholders.length < 2 ? "high" : avgAdoption > 0.62 || avgResistance > 0.62 ? "medium" : "high";
    const confidence = clamp(0.34 + assumptions.length * 0.04 + stakeholders.length * 0.035 + relationships.length * 0.02, 0.35, 0.68);
    const stakeholderIds = stakeholders.map((item) => item.stakeholder_id);
    const primaryStakeholderIds = stakeholderIds.slice(0, Math.min(2, stakeholderIds.length));
    const resistanceStakeholderIds = stakeholderIds.slice(-Math.min(2, stakeholderIds.length));
    const assumptionIds = assumptions.map((item) => item.assumption_id);
    const adoptionSignalId = `sig_adoption_${safeId(runSuffix)}`;
    const resistanceSignalId = `sig_resistance_${safeId(runSuffix)}`;

    return {
      schema_version: "1.0.0",
      artifact_type: "predictive_hypothesis",
      artifact_id: `predictive_hypothesis_${runSuffix}`,
      project_id: state.project.project_id,
      created_at: now,
      created_by_role: "d_predict",
      status: "pending_review",
      provenance: {
        source_kind: "system_generated",
        source_label: "D-Predict reduced deterministic scenario",
        ip_owner: state.project?.provenance?.ip_owner || "VERTEX team",
        external_components_used: [],
        notes: "Generated locally from approved SystemMap inputs. No external model, API or adapter was executed."
      },
      human_approval: {
        required: true,
        state: "pending",
        approved_by_role: "founder",
        approved_at: now,
        notes: "Pending facilitator review before DecisionRecord inclusion."
      },
      validation_errors: [],
      preceding_artifacts: {
        project_record_id: state.project.artifact_id,
        problem_frame_id: state.problem.artifact_id,
        system_map_id: state.system.artifact_id
      },
      classification: "predictive_hypothesis",
      warning: warningText,
      scenario_question: `Which stakeholder responses may support or resist adoption of ${state.project.project_name || "this venture"} in the next pilot decision window?`,
      bounded_scenario_type: "stakeholder_adoption_resistance",
      approved_input_references: {
        system_map_id: state.system.artifact_id,
        stakeholder_ids: stakeholderIds,
        relationship_ids: relationships.map((item) => item.relationship_id),
        assumption_ids: assumptionIds,
        evidence_ids: evidenceIds
      },
      assumptions_used: assumptions.map((item) => ({
        assumption_id: item.assumption_id,
        statement: item.statement,
        source_artifact_id: state.system.artifact_id
      })),
      simulated_stakeholder_responses: responses,
      adoption_signals: [{
        signal_id: adoptionSignalId,
        statement: `${primaryStakeholderIds.length} mapped stakeholder group(s) may adopt if the approved assumptions hold in a visible pilot test.`,
        stakeholder_ids: primaryStakeholderIds,
        classification: "hypothesis",
        confidence: round2(confidence)
      }],
      resistance_signals: [{
        signal_id: resistanceSignalId,
        statement: `${resistanceStakeholderIds.length} mapped stakeholder group(s) may resist if the system dependencies increase workload, friction or ambiguity.`,
        stakeholder_ids: resistanceStakeholderIds,
        classification: "hypothesis",
        confidence: round2(clamp(confidence - 0.04, 0.3, 0.64))
      }],
      possible_cascades: [{
        cascade_id: `cas_learning_${safeId(runSuffix)}`,
        statement: "If one high-influence stakeholder group responds positively in a small test, adjacent stakeholders may lower resistance; if friction appears first, resistance may spread faster than adoption.",
        trigger_refs: [adoptionSignalId, resistanceSignalId, assumptionIds[0]],
        classification: "hypothesis",
        confidence: round2(clamp(confidence - 0.08, 0.28, 0.6))
      }],
      qbi_reading: buildQbiReading(stakeholders, relationships, assumptions, responses, { adoption: adoptionSignalId, resistance: resistanceSignalId }, unknownIds),
      uncertainty: {
        level: uncertaintyLevel,
        drivers: unique(["approved assumptions are still hypotheses", "stakeholder behavior has not been observed in a live pilot", "relationship strength comes from current SystemMap evidence", "QBI lite keeps conflicting readings open until human review"]),
        unknowns_preserved: unknownIds
      },
      limitations: [
        "This is a bounded hypothesis, not evidence or a factual prediction.",
        "It uses only approved SystemMap inputs and does not describe identifiable people.",
        "It should feed a DecisionRecord only after human review.",
        "The QBI reading is product-facing and does not execute the full formal QBI model."
      ],
      confidence: round2(confidence),
      run_metadata: {
        run_id: runId,
        engine_name: "d_predict_reduced_deterministic",
        engine_version: "0.1.0",
        is_fixture: false,
        external_api_calls_made: false,
        scenario_count: 1,
        time_horizon: "next pilot decision window"
      },
      revision: 1,
      updated_at: now
    };
  }

  function renderInputs() {
    const assumptions = approvedPredictiveAssumptions();
    const stakeholders = state.system?.stakeholders || [];
    const relationships = state.system?.relationships || [];
    setText("metric-stakeholders", stakeholders.length ? String(stakeholders.length) : "--");
    setText("metric-assumptions", assumptions.length ? String(assumptions.length) : "--");
    setText("input-count", String(assumptions.length + stakeholders.length + relationships.length));
    const warning = $("input-warning");
    if (!state.system) {
      warning.textContent = "Complete SynapMap before generating a scenario.";
      warning.style.display = "block";
    } else if (!assumptions.length) {
      warning.textContent = "No assumptions are approved for D-Predict yet. Open the approval gate first.";
      warning.style.display = "block";
    } else {
      warning.textContent = "Only these approved predictive assumptions will be consumed.";
      warning.style.display = "block";
    }
    $("input-list").innerHTML = assumptions.map((item) => `<div class="signal"><strong>${escapeHtml(item.assumption_id)}</strong><p>${escapeHtml(item.statement)}</p><div class="tagrow"><span class="tag">predictive approved</span><span class="tag">${escapeHtml(item.approval_state || "approved")}</span></div></div>`).join("") || '<div class="signal"><strong>No approved predictive inputs</strong><p>Use the Approval Gate to mark at least one assumption for D-Predict.</p></div>';
  }

  function renderDraft(draft) {
    state.draft = draft;
    const responses = draft.simulated_stakeholder_responses;
    const avgAdoption = responses.reduce((sum, item) => sum + item.adoption_likelihood, 0) / responses.length;
    const avgResistance = responses.reduce((sum, item) => sum + item.resistance_likelihood, 0) / responses.length;
    const avgUndecided = responses.reduce((sum, item) => sum + item.undecided_likelihood, 0) / responses.length;
    setText("metric-confidence", pct(draft.confidence));
    setText("metric-uncertainty", draft.uncertainty.level);
    setText("adoption-avg", pct(avgAdoption));
    setText("resistance-avg", pct(avgResistance));
    setText("undecided-avg", pct(avgUndecided));
    setText("artifact-id", draft.artifact_id);
    $("response-list").innerHTML = responses.map((item) => `<div class="response"><strong>${escapeHtml(item.stakeholder_id)}</strong><p>${escapeHtml(item.simulated_response)}</p><div class="bar"><div class="fill" style="width:${pct(item.adoption_likelihood)}"></div></div><div class="bar"><div class="fill resist" style="width:${pct(item.resistance_likelihood)}"></div></div><div class="bar"><div class="fill wait" style="width:${pct(item.undecided_likelihood)}"></div></div><div class="tagrow"><span class="tag">adopt ${pct(item.adoption_likelihood)}</span><span class="tag">resist ${pct(item.resistance_likelihood)}</span><span class="tag">undecided ${pct(item.undecided_likelihood)}</span></div></div>`).join("");
    $("adoption-list").innerHTML = draft.adoption_signals.map((item) => signalCard(item)).join("");
    $("resistance-list").innerHTML = draft.resistance_signals.map((item) => signalCard(item)).join("");
    $("cascade-list").innerHTML = draft.possible_cascades.map((item) => signalCard(item)).join("");
    $("qbi-list").innerHTML = qbiCards(draft.qbi_reading);
    $("uncertainty-tags").innerHTML = draft.uncertainty.drivers.map((item) => `<span class="tag">${escapeHtml(item)}</span>`).join("") + draft.uncertainty.unknowns_preserved.map((item) => `<span class="tag">${escapeHtml(item)}</span>`).join("");
    $("contract-json").textContent = JSON.stringify(draft, null, 2);
    $("contract-card").classList.add("active");
    $("contract-badge").textContent = "Pending review";
    $("contract-badge").className = "badge";
    $("contract-status").textContent = "Draft created locally. Save it to attach this PredictiveHypothesis to the active Golden Path run.";
    saveButton.disabled = false;
  }

  function signalCard(item) {
    return `<div class="signal"><strong>${escapeHtml(item.signal_id || item.cascade_id)}</strong><p>${escapeHtml(item.statement)}</p><div class="tagrow"><span class="tag">${escapeHtml(item.classification)}</span><span class="tag">confidence ${pct(item.confidence)}</span></div></div>`;
  }

  function qbiCards(reading) {
    if (!reading) return '<div class="signal"><strong>QBI pending</strong><p>Create a PredictiveHypothesis to see the QBI reading.</p></div>';
    const states = (reading.interpretation_states || []).map((item) => (
      `<div class="signal"><strong>${escapeHtml(item.state_id)}</strong><p>${escapeHtml(item.statement)}</p><div class="tagrow"><span class="tag">coexisting reading</span><span class="tag">${escapeHtml(item.classification)}</span></div></div>`
    )).join("");
    const correlations = (reading.actor_correlations || []).map((item) => (
      `<div class="signal"><strong>${escapeHtml(item.correlation_id)}</strong><p>${escapeHtml(item.statement)}</p><div class="tagrow"><span class="tag">actor correlation</span><span class="tag">${escapeHtml(item.classification)}</span></div></div>`
    )).join("");
    const losses = (reading.context_loss_vectors || []).map((item) => (
      `<div class="signal"><strong>${escapeHtml(item.vector_id)}</strong><p>${escapeHtml(item.statement)}</p><div class="tagrow"><span class="tag">context loss ${escapeHtml(item.severity)}</span><span class="tag">${escapeHtml(item.classification)}</span></div></div>`
    )).join("");
    const pressure = reading.commitment_pressure ? `<div class="signal"><strong>commitment pressure</strong><p>${escapeHtml(reading.commitment_pressure.statement)}</p><div class="tagrow"><span class="tag">collapse risk ${escapeHtml(reading.commitment_pressure.collapse_risk)}</span><span class="tag">${escapeHtml(reading.commitment_pressure.classification)}</span></div></div>` : "";
    return `${states}${correlations}${losses}${pressure}`;
  }

  async function createDraft() {
    try {
      const draft = buildDraft();
      const response = await fetch(`/api/vertex/runs/${encodeURIComponent(runId)}/artifacts/predictive_hypothesis/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(draft)
      });
      const result = await response.json();
      if (!response.ok || !result.valid) {
        const message = (result.errors && result.errors[0] && result.errors[0].message) || result.detail || "PredictiveHypothesis did not validate";
        throw new Error(message);
      }
      renderDraft(result.artifact || draft);
      status.textContent = "PredictiveHypothesis created and validated as a bounded hypothesis.";
      status.className = "copy status-ok";
    } catch (error) {
      status.textContent = error.message;
      status.className = "copy status-bad";
      saveButton.disabled = true;
    }
  }

  async function saveDraft() {
    if (!state.draft) return;
    saveButton.disabled = true;
    status.textContent = "Saving PredictiveHypothesis into the Golden Path run...";
    status.className = "copy";
    try {
      const response = await fetch(`/api/vertex/runs/${encodeURIComponent(runId)}/artifacts/predictive_hypothesis/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(state.draft)
      });
      const result = await response.json();
      if (!response.ok || !result.saved) {
        const message = (result.errors && result.errors[0] && result.errors[0].message) || result.detail || "PredictiveHypothesis was not saved";
        throw new Error(message);
      }
      status.textContent = "Saved. D-Predict can now feed Billie and the DecisionRecord.";
      status.className = "copy status-ok";
      $("contract-badge").textContent = "Saved";
      $("contract-badge").className = "badge ok";
      $("contract-status").textContent = "Artifact saved to the active run with contract validation.";
    } catch (error) {
      status.textContent = error.message;
      status.className = "copy status-bad";
      $("contract-badge").textContent = "Rejected";
      $("contract-badge").className = "badge bad";
      saveButton.disabled = false;
    }
  }

  async function init() {
    updateLinks();
    if (!runId) {
      status.textContent = "Create a Golden Path run first.";
      status.className = "copy status-bad";
      buildButton.disabled = true;
      return;
    }
    localStorage.setItem(storageKey, runId);
    try {
      [state.project, state.problem, state.system] = await Promise.all([
        loadArtifact("project_record"),
        loadArtifact("problem_frame"),
        loadArtifact("system_map")
      ]);
      renderInputs();
      status.textContent = "Ready. D-Predict will consume only approved predictive assumptions.";
      status.className = "copy status-ok";
    } catch (error) {
      status.textContent = `${error.message}. Complete Alex, SynapMap and the Approval Gate first.`;
      status.className = "copy status-bad";
      buildButton.disabled = true;
      renderInputs();
    }
  }

  buildButton.addEventListener("click", createDraft);
  saveButton.addEventListener("click", saveDraft);
  init();
}());
