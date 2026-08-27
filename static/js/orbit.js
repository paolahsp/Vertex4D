(function () {
  const STORAGE_KEY = "orbit_evidence_current";

  const defaultSignals = [
    {
      title: "Pilot buyer asked for cohort comparison",
      source: "Facilitator call notes",
      note: "Two accelerator leads compared founders by decision quality, not just pitch polish.",
      confidence: 60,
      risk: "medium",
      project: "VERTEX Quest",
      tag: "Buyer signal",
    },
    {
      title: "Founder artifacts show repeated buyer/user confusion",
      source: "Alex and SynapMap notes",
      note: "Several cases name the end user clearly but leave budget authority unresolved.",
      confidence: 82,
      risk: "high",
      project: "SynapMap",
      tag: "Evidence gap",
    },
    {
      title: "Outcome reporting is the strongest institutional artifact",
      source: "Accelerator demo rehearsal",
      note: "Buyer-facing report made intervention logic easier to explain without claiming final outcomes.",
      confidence: 82,
      risk: "low",
      project: "Brief",
      tag: "Product pattern",
    },
  ];

  const riskWeights = {
    low: 8,
    medium: 18,
    high: 34,
  };

  const elements = {};

  function $(id) {
    return document.getElementById(id);
  }

  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        return { signals: defaultSignals };
      }
      const parsed = JSON.parse(raw);
      if (!parsed || !Array.isArray(parsed.signals)) {
        return { signals: defaultSignals };
      }
      return { signals: parsed.signals };
    } catch (error) {
      return { signals: defaultSignals };
    }
  }

  function saveState(state) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state, null, 2));
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function calculateMetrics(signals) {
    if (!signals.length) {
      return {
        score: 0,
        coverage: 0,
        riskFlags: 0,
        averageConfidence: 0,
      };
    }

    const averageConfidence =
      signals.reduce((total, signal) => total + Number(signal.confidence || 0), 0) / signals.length;
    const riskFlags = signals.filter((signal) => signal.risk === "high").length;
    const averageRisk =
      signals.reduce((total, signal) => total + (riskWeights[signal.risk] || 18), 0) / signals.length;
    const sourceDiversity = new Set(signals.map((signal) => String(signal.source || "").toLowerCase())).size;
    const projectDiversity = new Set(signals.map((signal) => String(signal.project || "").toLowerCase())).size;
    const coverage = clamp(signals.length * 14 + sourceDiversity * 9 + projectDiversity * 7, 0, 100);
    const score = clamp(Math.round(averageConfidence * 0.58 + coverage * 0.34 - averageRisk * 0.28), 0, 100);

    return {
      score,
      coverage,
      riskFlags,
      averageConfidence: Math.round(averageConfidence),
    };
  }

  function confidenceLabel(value) {
    if (value >= 75) return "strong signal";
    if (value >= 50) return "observed signal";
    return "needs support";
  }

  function nodeClass(signal) {
    if (signal.risk === "high") return "signal-risk";
    if (Number(signal.confidence) >= 75) return "signal-high";
    return "";
  }

  function renderOrbit(signals) {
    const layer = elements.nodeLayer;
    layer.innerHTML = "";
    if (!signals.length) {
      layer.innerHTML = '<div class="absolute bottom-5 left-5 rounded-md border border-stone-300 bg-white/90 p-4 text-sm text-stone-600">Add a manual Signal to begin the Evidence Orbit.</div>';
      return;
    }

    const positions = [
      [8, 12],
      [62, 9],
      [77, 36],
      [63, 72],
      [14, 70],
      [5, 41],
      [39, 4],
      [82, 58],
    ];

    signals.slice(0, 8).forEach((signal, index) => {
      const [left, top] = positions[index % positions.length];
      const node = document.createElement("article");
      node.className = `orbit-node ${nodeClass(signal)} rounded-md p-3`;
      node.style.left = `${left}%`;
      node.style.top = `${top}%`;
      node.innerHTML = `
        <p class="font-mono text-[10px] uppercase tracking-wide text-stone-500">${escapeHtml(signal.tag)}</p>
        <h3 class="mt-1 text-sm font-bold leading-tight text-stone-900">${escapeHtml(signal.title)}</h3>
        <p class="mt-2 text-[11px] text-stone-600">${escapeHtml(signal.project || "Unassigned")}</p>
        <div class="mt-2 flex items-center justify-between text-[11px]">
          <span class="text-olive-text">${confidenceLabel(Number(signal.confidence || 0))}</span>
          <span class="font-mono text-coral-text">${Number(signal.confidence || 0)}%</span>
        </div>
      `;
      layer.appendChild(node);
    });
  }

  function renderEvidenceList(signals) {
    if (!signals.length) {
      elements.evidenceList.innerHTML = '<p class="text-sm text-stone-600">No shared evidence in this local draft yet.</p>';
      return;
    }

    elements.evidenceList.innerHTML = signals
      .map(
        (signal) => `
          <article class="rounded-md border border-stone-300 bg-white/80 p-3">
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-sm font-bold text-stone-900">${escapeHtml(signal.title)}</p>
                <p class="mt-1 text-xs text-stone-500">${escapeHtml(signal.source)} / ${escapeHtml(signal.project)}</p>
              </div>
              <span class="rounded-md bg-stone-100 px-2 py-1 font-mono text-[10px] uppercase text-stone-600">${escapeHtml(signal.risk)} risk</span>
            </div>
            <p class="mt-2 text-xs text-stone-600">${escapeHtml(signal.note)}</p>
          </article>
        `
      )
      .join("");
  }

  function renderWeakSignals(signals) {
    const weak = signals.filter((signal) => Number(signal.confidence || 0) < 65 || signal.risk === "high");
    if (!weak.length) {
      elements.weakList.innerHTML = '<p class="text-sm text-stone-600">No weak signals flagged in this local draft.</p>';
      return;
    }

    elements.weakList.innerHTML = weak
      .map(
        (signal) => `
          <article class="rounded-md border border-coral-text/30 bg-white/80 p-3">
            <p class="text-sm font-bold text-stone-900">${escapeHtml(signal.title)}</p>
            <p class="mt-1 text-xs text-stone-600">Needs support: add another source, clarify the evidence note or reduce the claim attached to this signal.</p>
          </article>
        `
      )
      .join("");
  }

  function render(state) {
    const signals = state.signals || [];
    const metrics = calculateMetrics(signals);

    elements.headerSignals.textContent = `${signals.length} signals`;
    elements.headerConfidence.textContent = `${metrics.score}% confidence`;
    elements.signalCount.textContent = String(signals.length);
    elements.coverage.textContent = `${metrics.coverage}%`;
    elements.riskFlags.textContent = String(metrics.riskFlags);
    elements.confidenceScore.textContent = `${metrics.score}%`;
    elements.confidenceBar.style.width = `${metrics.score}%`;
    elements.draftOutput.textContent = JSON.stringify(
      {
        storage_key: STORAGE_KEY,
        local_draft: true,
        confidence_score: metrics.score,
        evidence_coverage: metrics.coverage,
        risk_flags: metrics.riskFlags,
        signals,
      },
      null,
      2
    );

    renderOrbit(signals);
    renderEvidenceList(signals);
    renderWeakSignals(signals);
  }

  function collectFormSignal() {
    return {
      title: $("orbit-signal-title").value.trim(),
      source: $("orbit-signal-source").value.trim(),
      note: $("orbit-signal-note").value.trim(),
      confidence: Number($("orbit-signal-confidence").value),
      risk: $("orbit-signal-risk").value,
      project: $("orbit-signal-project").value.trim() || "Unassigned",
      tag: $("orbit-signal-tag").value,
    };
  }

  document.addEventListener("DOMContentLoaded", () => {
    elements.headerSignals = $("orbit-header-signals");
    elements.headerConfidence = $("orbit-header-confidence");
    elements.signalCount = $("orbit-signal-count");
    elements.coverage = $("orbit-coverage");
    elements.riskFlags = $("orbit-risk-flags");
    elements.confidenceScore = $("orbit-confidence-score");
    elements.confidenceBar = $("orbit-confidence-bar");
    elements.nodeLayer = $("orbit-node-layer");
    elements.evidenceList = $("orbit-evidence-list");
    elements.weakList = $("orbit-weak-list");
    elements.draftOutput = $("orbit-draft-output");

    let state = loadState();
    render(state);

    $("orbit-signal-form").addEventListener("submit", (event) => {
      event.preventDefault();
      const signal = collectFormSignal();
      if (!signal.title || !signal.source || !signal.note) {
        return;
      }
      state = { signals: [signal, ...state.signals].slice(0, 12) };
      saveState(state);
      render(state);
    });

    $("orbit-save-btn").addEventListener("click", () => {
      saveState(state);
      render(state);
    });

    $("orbit-reset-btn").addEventListener("click", () => {
      state = { signals: defaultSignals };
      saveState(state);
      render(state);
    });
  });
})();
