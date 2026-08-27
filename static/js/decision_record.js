(function () {
  const storageKey = "vertex_current_run_id";
  const runId = new URLSearchParams(window.location.search).get("run_id") || localStorage.getItem(storageKey);
  const userRole = document.body.dataset.userRole || "founder";
  const state = { project: null, problem: null, system: null, predictive: null, financial: null, draft: null };
  const artifactTypes = ["project_record", "problem_frame", "system_map", "predictive_hypothesis", "financial_scenario"];

  const $ = (id) => document.getElementById(id);
  const status = $("dr-status");
  const buildButton = $("build-decision");
  const saveButton = $("save-decision");

  function setText(id, value) {
    const node = $(id);
    if (node) node.textContent = value;
  }

  function escapeHtml(value) {
    return String(value || "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
  }

  function safeId(value, fallback) {
    const raw = String(value || fallback || "id").toLowerCase().replace(/[^a-z0-9_-]+/g, "_").replace(/^_+|_+$/g, "");
    return raw || String(fallback || "id");
  }

  function money(value, currency) {
    const amount = Number(value || 0);
    return `${currency || "USD"} ${Math.round(amount).toLocaleString()}`;
  }

  function addDays(date, days) {
    const next = new Date(date.getTime());
    next.setUTCDate(next.getUTCDate() + days);
    return next.toISOString().slice(0, 10);
  }

  function unique(items) {
    return Array.from(new Set(items.filter(Boolean)));
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

  function evidenceSummary() {
    const problemEvidence = (state.problem?.evidence_references || []).map((item) => ({ ...item, source_artifact_id: state.problem.artifact_id }));
    const systemEvidence = (state.system?.evidence_references || []).map((item) => ({ ...item, source_artifact_id: state.system.artifact_id }));
    return [...problemEvidence, ...systemEvidence]
      .filter((item, index, all) => item.evidence_id && all.findIndex((other) => other.evidence_id === item.evidence_id) === index)
      .slice(0, 4)
      .map((item) => ({
        evidence_id: item.evidence_id,
        summary: `${item.label || item.evidence_id} is preserved as factual upstream evidence for the decision.`,
        classification: "fact",
        source_artifact_id: item.source_artifact_id,
        evidence_context: "synthetic_fixture"
      }));
  }

  function approvedAssumptions() {
    return (state.system?.approved_assumptions || []).filter((item) => item.approval_state === "approved" || item.approved_for_predictive_processing || item.approved_for_financial_processing);
  }

  function assumptionSummary() {
    return approvedAssumptions().slice(0, 6).map((item) => ({
      assumption_id: item.assumption_id,
      summary: item.statement || item.assumption_id,
      classification: "hypothesis",
      approval_state: item.approval_state || "approved"
    }));
  }

  function predictionSummary() {
    const response = (state.predictive?.simulated_stakeholder_responses || []).slice().sort((a, b) => (b.resistance_likelihood || 0) - (a.resistance_likelihood || 0))[0];
    const summary = response ? response.simulated_response : state.predictive?.scenario_question || "Ripple produced a bounded stakeholder adoption/resistance hypothesis.";
    return [{
      hypothesis_id: state.predictive.artifact_id,
      summary,
      classification: "predictive_hypothesis",
      not_evidence: true
    }];
  }

  function financialSummary() {
    const currency = state.financial?.currency || "USD";
    const revenue = state.financial?.revenue_projection?.value;
    const cash = state.financial?.cash_requirement?.value;
    return [{
      financial_scenario_id: state.financial.artifact_id,
      summary: `Ledger estimates ${money(revenue, currency)} revenue and ${money(cash, currency)} cash requirement under current assumptions.`,
      classification: "hypothesis",
      uses_fixture_values: Boolean(state.financial?.run_metadata?.is_fixture || (state.financial?.pricing_assumptions || []).some((item) => item.is_fixture_value))
    }];
  }

  function sourceUnknownIds() {
    return unique([
      ...(state.predictive?.uncertainty?.unknowns_preserved || []),
      ...(state.financial?.uncertainty?.unknowns_preserved || []),
      ...(state.problem?.unknowns || []).map((item) => item.id),
      ...(state.system?.unknowns || []).map((item) => item.id)
    ]).slice(0, 6);
  }

  function firstSignalId(collectionName) {
    const collection = state.predictive?.[collectionName] || [];
    return collection[0]?.signal_id;
  }

  function firstTensionId() {
    return (state.problem?.tensions || [])[0]?.id || (state.system?.tensions || [])[0]?.id;
  }

  function buildDecisionRecord() {
    if (!runId) throw new Error("Create a Quest run first from Spark.");
    for (const type of artifactTypes) {
      if (!state[typeToState(type)]) throw new Error(`${type} is required before Stamp.`);
    }
    const now = new Date();
    const nowIso = now.toISOString();
    const runSuffix = runId.replaceAll("-", "_");
    const evidence = evidenceSummary();
    const assumptions = assumptionSummary();
    const unknownRefs = sourceUnknownIds();
    if (!evidence.length) throw new Error("Stamp requires factual evidence summaries.");
    if (!assumptions.length) throw new Error("Stamp requires approved assumptions.");
    if (!unknownRefs.length) throw new Error("Stamp must preserve upstream unknowns.");

    const alternatives = [
      { alternative_id: "alt_full_launch", statement: "Move directly to a broad launch.", classification: "hypothesis" },
      { alternative_id: "alt_limited_pilot", statement: "Run a limited pilot focused on adoption, resistance and financial learning.", classification: "inference" },
      { alternative_id: "alt_continue_discovery", statement: "Continue discovery without an operating pilot.", classification: "inference" }
    ];
    const selectedAlternativeId = "alt_limited_pilot";
    const adoption = avg(state.predictive.simulated_stakeholder_responses || [], "adoption_likelihood");
    const resistance = avg(state.predictive.simulated_stakeholder_responses || [], "resistance_likelihood");
    const reviewDate = addDays(now, 42);
    const decisionId = `dec_limited_pilot_${safeId(runSuffix)}`;
    const experimentId = `exp_pilot_${safeId(runSuffix)}`;
    const criteria = successCriteria(runSuffix);
    const auditCreated = `audit_decision_created_${safeId(runSuffix)}`;
    const auditApproved = `audit_facilitator_approved_${safeId(runSuffix)}`;

    return {
      schema_version: "1.0.0",
      artifact_type: "decision_record",
      artifact_id: `decision_record_${runSuffix}`,
      project_id: state.project.project_id,
      created_at: nowIso,
      created_by_role: "facilitator",
      status: "approved",
      provenance: {
        source_kind: "system_generated",
        source_label: "VERTEX Stamp DecisionRecord",
        ip_owner: state.project?.provenance?.ip_owner || "VERTEX team",
        external_components_used: [],
        notes: "Assembled locally from the active VERTEX Quest chain."
      },
      human_approval: {
        required: true,
        state: "approved",
        approved_by_role: "facilitator",
        approved_at: nowIso,
        notes: "Approved as the final Stamp for this VERTEX run."
      },
      validation_errors: [],
      linked_upstream_artifact_ids: {
        project_record_id: state.project.artifact_id,
        problem_frame_id: state.problem.artifact_id,
        system_map_id: state.system.artifact_id,
        predictive_hypothesis_id: state.predictive.artifact_id,
        financial_scenario_id: state.financial.artifact_id
      },
      decision_question: `Should ${state.project.project_name || "this venture"} move forward now, continue discovery, pause, or run a bounded pilot first?`,
      alternatives_considered: alternatives,
      evidence_summary: evidence,
      assumptions,
      predictive_hypotheses: predictionSummary(),
      financial_scenarios: financialSummary(),
      risks: [{
        id: `risk_adoption_resistance_${safeId(runSuffix)}`,
        statement: `Stakeholder resistance may still outweigh adoption in the first pilot if the strongest friction is not tested directly. Current average adoption is ${Math.round(adoption * 100)}% and resistance is ${Math.round(resistance * 100)}%.`,
        classification: "hypothesis",
        source_refs: [state.predictive.artifact_id]
      }, {
        id: `risk_financial_learning_${safeId(runSuffix)}`,
        statement: "Financial viability may depend on assumptions that Ledger has modelled but the team has not yet observed in market.",
        classification: "hypothesis",
        source_refs: [state.financial.artifact_id]
      }],
      unknowns: [{
        id: `unk_decision_${safeId(runSuffix)}`,
        statement: `The decision preserves these unresolved unknowns: ${unknownRefs.join(", ")}.`,
        classification: "unknown",
        source_refs: unknownRefs
      }],
      contradictions: [{
        id: `ctr_learning_before_scale_${safeId(runSuffix)}`,
        statement: "The opportunity may look strategically attractive while adoption and financial assumptions remain too uncertain for a full launch.",
        classification: "inference",
        source_refs: unique([firstTensionId(), firstSignalId("resistance_signals"), state.financial.artifact_id]).slice(0, 3)
      }],
      selected_decision: {
        decision_id: decisionId,
        statement: "Run a limited pilot before committing to a broader launch.",
        decision_type: "limited_pilot"
      },
      rationale: "The upstream evidence, approved assumptions, Ripple hypothesis and Ledger financial scenario support a bounded learning commitment. They do not yet justify full launch or indefinite desk research.",
      rejected_alternatives: [{
        alternative_id: "alt_full_launch",
        reason: "Ripple and Ledger still preserve enough uncertainty to make broad launch premature."
      }, {
        alternative_id: "alt_continue_discovery",
        reason: "The next important unknowns require observed behavior and financial learning in a real pilot window."
      }],
      next_experiment: {
        experiment_id: experimentId,
        statement: "Run a focused pilot that measures stakeholder adoption, resistance points, pricing behavior and operational friction before scale-up.",
        owner_role: "founder",
        measurement_window: "six weeks"
      },
      success_criteria: criteria,
      owner_role: "founder",
      review_date: reviewDate,
      facilitator_approval: {
        state: "approved",
        approved_by_role: "facilitator",
        approved_at: nowIso,
        notes: "Facilitator approval required; server will normalize this role from the authenticated session."
      },
      audit_trail: [{
        event_id: auditCreated,
        timestamp: nowIso,
        actor_role: "system",
        action: "assembled_reduced_decision_record",
        artifact_refs: [state.project.artifact_id, state.problem.artifact_id, state.system.artifact_id, state.predictive.artifact_id, state.financial.artifact_id]
      }, {
        event_id: auditApproved,
        timestamp: nowIso,
        actor_role: "facilitator",
        action: "approved_reduced_decision_record",
        artifact_refs: [`decision_record_${runSuffix}`]
      }],
      revision: 1,
      updated_at: nowIso,
      selected_alternative_id: selectedAlternativeId
    };
  }

  function typeToState(type) {
    return {
      project_record: "project",
      problem_frame: "problem",
      system_map: "system",
      predictive_hypothesis: "predictive",
      financial_scenario: "financial"
    }[type];
  }

  function avg(items, field) {
    if (!items.length) return 0;
    return items.reduce((sum, item) => sum + Number(item[field] || 0), 0) / items.length;
  }

  function successCriteria(runSuffix) {
    return [{
      criterion_id: `crit_adoption_${safeId(runSuffix)}`,
      metric: "target stakeholder segment shows observable adoption behavior",
      operator: ">=",
      target_value: 25,
      unit: "percent",
      measurement_window: "six-week pilot",
      data_source: "pilot observation log",
      classification: "hypothesis"
    }, {
      criterion_id: `crit_resistance_${safeId(runSuffix)}`,
      metric: "critical resistance events remain below threshold",
      operator: "<=",
      target_value: 20,
      unit: "percent",
      measurement_window: "six-week pilot",
      data_source: "pilot issue log",
      classification: "hypothesis"
    }, {
      criterion_id: `crit_cash_${safeId(runSuffix)}`,
      metric: "cash requirement stays within planned pilot buffer",
      operator: "<=",
      target_value: Math.max(1, Math.round(Number(state.financial?.cash_requirement?.value || 1000))),
      unit: state.financial?.currency || "currency units",
      measurement_window: "pilot close",
      data_source: "Ledger scenario and actual spend log",
      classification: "hypothesis"
    }];
  }

  function renderChain() {
    const loaded = artifactTypes.map((type) => state[typeToState(type)]).filter(Boolean).length;
    setText("metric-artifacts", `${loaded}/5`);
    setText("metric-role", userRole);
    setText("prediction-state", state.predictive?.status || "missing");
    setText("finance-state", state.financial?.status || "missing");
    const warning = $("chain-warning");
    if (loaded === 5) {
      warning.textContent = userRole === "facilitator" ? "Ready for facilitator close-out." : "Stamp can be drafted, but final save requires a facilitator session.";
    } else {
      warning.textContent = "Complete Ripple and Ledger before creating the final record.";
    }
    $("chain-list").innerHTML = artifactTypes.map((type) => {
      const artifact = state[typeToState(type)];
      return `<div class="item"><strong>${escapeHtml(type)}</strong><p>${escapeHtml(artifact?.artifact_id || "missing")}</p><div class="tagrow"><span class="tag">${escapeHtml(artifact?.status || "not ready")}</span></div></div>`;
    }).join("");
  }

  function renderDraft(draft) {
    state.draft = draft;
    setText("artifact-id", draft.artifact_id);
    setText("metric-risks", String(draft.risks.length));
    setText("metric-criteria", String(draft.success_criteria.length));
    setText("decision-type", draft.selected_decision.decision_type);
    setText("review-date", draft.review_date);
    setText("verdict-title", draft.selected_decision.statement);
    setText("verdict-yes", draft.rationale);
    setText("verdict-but", (draft.risks[0] && draft.risks[0].statement) || "Keep the strongest risk visible before scale-up.");
    setText("verdict-measure", (draft.success_criteria[0] && `${draft.success_criteria[0].metric} ${draft.success_criteria[0].operator} ${draft.success_criteria[0].target_value} ${draft.success_criteria[0].unit}`) || "Define one observable success criterion.");
    setText("verdict-chain", `${draft.linked_upstream_artifact_ids ? Object.keys(draft.linked_upstream_artifact_ids).length : 0} upstream artifacts linked`);
    setText("verdict-owner", `Owner: ${draft.owner_role} - review ${draft.review_date}`);
    $("decision-list").innerHTML = `<div class="item decision"><strong>${escapeHtml(draft.selected_decision.statement)}</strong><p>${escapeHtml(draft.rationale)}</p><div class="tagrow"><span class="tag">${escapeHtml(draft.selected_alternative_id)}</span><span class="tag">facilitator approval required</span></div></div>`;
    $("risk-list").innerHTML = [...draft.risks, ...draft.unknowns, ...draft.contradictions].map(card).join("");
    $("criteria-list").innerHTML = draft.success_criteria.map((item) => `<div class="item"><strong>${escapeHtml(item.metric)}</strong><p>${escapeHtml(item.operator)} ${escapeHtml(item.target_value)} ${escapeHtml(item.unit)} / ${escapeHtml(item.measurement_window)}</p><div class="tagrow"><span class="tag">${escapeHtml(item.criterion_id)}</span></div></div>`).join("");
    $("contract-json").textContent = JSON.stringify(draft, null, 2);
    $("contract-card").classList.add("active");
    $("contract-badge").textContent = "Approved draft";
    $("contract-badge").className = "badge";
    $("contract-status").textContent = userRole === "facilitator" ? "Draft created. Save to persist the final record." : "Draft created, but save will be rejected unless the authenticated session is facilitator.";
    saveButton.disabled = false;
  }

  function card(item) {
    return `<div class="item"><strong>${escapeHtml(item.id)}</strong><p>${escapeHtml(item.statement)}</p><div class="tagrow"><span class="tag">${escapeHtml(item.classification)}</span>${(item.source_refs || []).map((ref) => `<span class="tag">${escapeHtml(ref)}</span>`).join("")}</div></div>`;
  }

  async function createDraft() {
    try {
      const draft = buildDecisionRecord();
      const response = await fetch(`/api/vertex/runs/${encodeURIComponent(runId)}/artifacts/decision_record/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(draft)
      });
      const result = await response.json();
      if (!response.ok || !result.valid) {
        const message = (result.errors && result.errors[0] && result.errors[0].message) || result.detail || "Stamp did not validate";
        throw new Error(message);
      }
      renderDraft(result.artifact || draft);
      status.textContent = "Stamp created and validated.";
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
    status.textContent = "Saving final Stamp...";
    status.className = "copy";
    try {
      const response = await fetch(`/api/vertex/runs/${encodeURIComponent(runId)}/artifacts/decision_record/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(state.draft)
      });
      const result = await response.json();
      if (!response.ok || !result.saved) {
        const message = (result.errors && result.errors[0] && result.errors[0].message) || result.detail || "Stamp was not saved";
        throw new Error(message);
      }
      status.textContent = "Saved. The VERTEX Quest now has a complete traceable decision chain.";
      status.className = "copy status-ok";
      $("contract-badge").textContent = "Saved";
      $("contract-badge").className = "badge ok";
      $("contract-status").textContent = "Final record saved with facilitator approval normalized by the server.";
      showPilotFeedback();
    } catch (error) {
      status.textContent = error.message;
      status.className = "copy status-bad";
      $("contract-badge").textContent = "Rejected";
      $("contract-badge").className = "badge bad";
      saveButton.disabled = false;
    }
  }

  function showPilotFeedback() {
    const card = $("pilot-feedback-card");
    if (card) card.hidden = false;
  }

  async function revealPilotFeedbackIfRecordExists() {
    // decision_record is not part of artifactTypes (those are the upstream five),
    // so ask for it directly. A missing record is the normal case, not an error.
    try {
      const response = await fetch(`/api/vertex/runs/${encodeURIComponent(runId)}/artifacts/decision_record`);
      if (response.ok) showPilotFeedback();
    } catch (error) {
      /* the panel simply stays closed */
    }
  }

  async function sendPilotFeedback() {
    const button = $("send-feedback");
    const note = $("feedback-status");
    const wouldPay = $("would-pay").value;
    const wouldRecommend = $("would-recommend").value;
    if (!wouldPay || !wouldRecommend) {
      note.textContent = "Answer both questions before sending.";
      note.className = "copy status-bad";
      return;
    }
    button.disabled = true;
    note.textContent = "Sending...";
    note.className = "copy";
    try {
      const response = await fetch(`/api/vertex/runs/${encodeURIComponent(runId)}/pilot-feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          would_pay: wouldPay,
          would_recommend: wouldRecommend,
          note: $("feedback-note").value
        })
      });
      const result = await response.json();
      if (!response.ok || !result.saved) {
        throw new Error(result.detail || "Feedback was not recorded");
      }
      note.textContent = "Recorded. Thank you — this is what tells the program whether the method worked.";
      note.className = "copy status-ok";
    } catch (error) {
      note.textContent = error.message;
      note.className = "copy status-bad";
      button.disabled = false;
    }
  }

  async function init() {
    updateLinks();
    setText("metric-role", userRole);
    if (!runId) {
      status.textContent = "Create a Quest run first from Spark.";
      status.className = "copy status-bad";
      buildButton.disabled = true;
      return;
    }
    localStorage.setItem(storageKey, runId);
    try {
      const loaded = await Promise.all(artifactTypes.map((type) => loadArtifact(type)));
      artifactTypes.forEach((type, index) => { state[typeToState(type)] = loaded[index]; });
      renderChain();
      await revealPilotFeedbackIfRecordExists();
      status.textContent = userRole === "facilitator" ? "Ready. Facilitator session can close Stamp." : "Ready to preview. Final save requires facilitator role.";
      status.className = "copy status-ok";
    } catch (error) {
      renderChain();
      status.textContent = `${error.message}. Complete the Quest chain first.`;
      status.className = "copy status-bad";
      buildButton.disabled = true;
    }
  }

  buildButton.addEventListener("click", createDraft);
  saveButton.addEventListener("click", saveDraft);
  $("send-feedback").addEventListener("click", sendPilotFeedback);
  init();
}());
