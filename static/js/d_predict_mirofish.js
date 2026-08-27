(function () {
  const storageKey = "dpredict_mirofish_current";
  const $ = (id) => document.getElementById(id);
  const status = $("dp-status");

  function textLines(value) {
    return String(value || "")
      .split(/\r?\n|,/)
      .map((item) => item.trim())
      .filter(Boolean)
      .slice(0, 8);
  }

  function hashSeed(value) {
    const raw = String(value || "42");
    let seed = 2166136261;
    for (let i = 0; i < raw.length; i += 1) {
      seed ^= raw.charCodeAt(i);
      seed = Math.imul(seed, 16777619);
    }
    return seed >>> 0;
  }

  function mulberry32(seed) {
    let t = seed >>> 0;
    return function () {
      t += 0x6D2B79F5;
      let r = Math.imul(t ^ (t >>> 15), 1 | t);
      r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
      return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
    };
  }

  function pct(value) {
    return `${Math.round(Number(value || 0) * 100)}%`;
  }

  function round(value, places) {
    const factor = 10 ** (places || 2);
    return Math.round(Number(value || 0) * factor) / factor;
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function escapeHtml(value) {
    return String(value || "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
  }

  function readInputs() {
    const read = (id) => ($(id) ? $(id).value : "");
    return {
      scenarioTitle: read("scenario-title"),
      scenarioQuestion: read("scenario-question"),
      timeHorizon: read("time-horizon"),
      interpretations: textLines(read("interpretations")),
      actors: textLines(read("actors")),
      evidenceNotes: read("evidence-notes"),
      frictions: textLines(read("frictions")),
      seed: Number(read("seed") || 42),
      rounds: clamp(Number(read("rounds") || 18), 6, 48),
      measurementPressure: Number(read("measurement-pressure") || 0) / 100,
      alignmentField: Number(read("alignment-field") || 0) / 100,
      trustDensity: Number(read("trust-density") || 0) / 100,
      contextFriction: Number(read("context-friction") || 0) / 100
    };
  }

  function normalize(weights) {
    const sum = weights.reduce((total, item) => total + item, 0) || 1;
    return weights.map((item) => item / sum);
  }

  function entropy(weights) {
    const h = weights.reduce((total, item) => (item > 0 ? total - item * Math.log2(item) : total), 0);
    return h / Math.log2(Math.max(2, weights.length));
  }

  function buildScenario(inputs) {
    const interpretations = inputs.interpretations.length ? inputs.interpretations : ["adoption path", "resistance path", "wait for evidence"];
    const actors = inputs.actors.length ? inputs.actors : ["buyer", "founder", "facilitator"];
    const rng = mulberry32(hashSeed(`${inputs.seed}:${inputs.scenarioTitle}:${inputs.scenarioQuestion}`));
    let weights = normalize(interpretations.map((_, index) => 0.7 + rng() * 0.6 + (index === 0 ? inputs.trustDensity * 0.35 : 0)));
    const trace = [];
    for (let roundIndex = 0; roundIndex < inputs.rounds; roundIndex += 1) {
      const pressure = inputs.measurementPressure * (roundIndex + 1) / inputs.rounds;
      const friction = inputs.contextFriction * (0.75 + rng() * 0.5);
      weights = normalize(weights.map((weight, index) => {
        const alignment = inputs.alignmentField * (index === 0 ? 0.18 : -0.06);
        const noise = (rng() - 0.5) * 0.11;
        const measurement = pressure * (weight - 1 / weights.length) * 0.18;
        return clamp(weight + alignment + noise - friction * 0.035 + measurement, 0.03, 0.92);
      }));
      trace.push(weights.slice());
    }
    const h = entropy(weights);
    const maxWeight = Math.max(...weights);
    const minWeight = Math.min(...weights);
    const coherence = clamp((1 - inputs.contextFriction) * 0.44 + inputs.alignmentField * 0.34 + inputs.trustDensity * 0.22, 0, 1);
    const superposition = clamp(h * (1 - Math.abs(maxWeight - (1 / weights.length)) * 0.35), 0, 1);
    const bornFloor = clamp(1 / Math.max(actors.length, 2), 0.04, 0.5);
    const commitmentPressure = clamp(inputs.measurementPressure * 0.48 + maxWeight * 0.38 + (1 - h) * 0.18, 0, 1);
    const distribution = interpretations.map((label, index) => ({
      label,
      weight: round(weights[index], 3),
      support: actors.filter((_, actorIndex) => ((actorIndex + index + Math.floor(inputs.seed)) % interpretations.length) === index % interpretations.length).slice(0, 3)
    })).sort((a, b) => b.weight - a.weight);
    return {
      ...inputs,
      actors,
      interpretations,
      trace,
      distribution,
      observables: {
        coherence: round(coherence, 3),
        superposition: round(superposition, 3),
        bornFloor: round(bornFloor, 3),
        commitmentPressure: round(commitmentPressure, 3),
        entropy: round(h, 3),
        spread: round(maxWeight - minWeight, 3)
      },
      generatedAt: new Date().toISOString()
    };
  }

  function renderMap(result) {
    const svg = $("scenario-map");
    if (!svg) return;
    const width = 720;
    const height = 430;
    const centerX = width / 2;
    const centerY = height / 2;
    const maxWeight = Math.max(...result.distribution.map((item) => item.weight));
    const actors = result.actors.map((actor, index) => {
      const angle = (Math.PI * 2 * index) / Math.max(1, result.actors.length) - Math.PI / 2;
      return {
        actor,
        x: centerX + Math.cos(angle) * 178,
        y: centerY + Math.sin(angle) * 142
      };
    });
    const nodes = result.distribution.map((item, index) => {
      const angle = (Math.PI * 2 * index) / Math.max(1, result.distribution.length) + Math.PI / 7;
      return {
        ...item,
        x: centerX + Math.cos(angle) * (54 + (1 - item.weight) * 72),
        y: centerY + Math.sin(angle) * (42 + (1 - item.weight) * 58),
        r: 28 + (item.weight / maxWeight) * 28
      };
    });
    const actorMarkup = actors.map((item) => (
      `<g class="dp-map-node"><circle cx="${item.x}" cy="${item.y}" r="12" fill="#ffffff" stroke="#5b13ec" stroke-width="2"></circle><text class="dp-map-label" x="${item.x + 16}" y="${item.y + 4}">${escapeHtml(item.actor)}</text></g>`
    )).join("");
    const edgeMarkup = actors.flatMap((actor, actorIndex) => nodes.map((node, nodeIndex) => {
      const opacity = 0.12 + (((actorIndex + nodeIndex + result.seed) % 4) / 10);
      return `<line x1="${actor.x}" y1="${actor.y}" x2="${node.x}" y2="${node.y}" stroke="#5b13ec" stroke-width="1.4" opacity="${opacity}"></line>`;
    })).join("");
    const nodeMarkup = nodes.map((item, index) => {
      const colors = ["#5b13ec", "#00A86B", "#FF6B6B", "#B2A4FF", "#161022"];
      return `<g class="dp-map-node"><circle cx="${item.x}" cy="${item.y}" r="${item.r}" fill="${colors[index % colors.length]}" opacity="0.88"></circle><text class="dp-map-label" x="${item.x}" y="${item.y + 4}" text-anchor="middle">${escapeHtml(item.label)}</text><text class="dp-map-label" x="${item.x}" y="${item.y + item.r + 20}" text-anchor="middle">${pct(item.weight)}</text></g>`;
    }).join("");
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.innerHTML = `<rect x="0" y="0" width="${width}" height="${height}" fill="transparent"></rect>${edgeMarkup}${actorMarkup}${nodeMarkup}`;
  }

  function list(items) {
    return items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  }

  function renderResult(result) {
    $("metric-coherence").textContent = pct(result.observables.coherence);
    $("metric-superposition").textContent = pct(result.observables.superposition);
    $("metric-born-floor").textContent = pct(result.observables.bornFloor);
    $("metric-collapse").textContent = pct(result.observables.commitmentPressure);
    $("distribution-list").innerHTML = result.distribution.map((item) => (
      `<div class="dp-output-card"><h3>${escapeHtml(item.label)}</h3><p><strong>${pct(item.weight)}</strong> scenario weight. Support signals: ${escapeHtml(item.support.join(", ") || "not enough actors mapped")}.</p></div>`
    )).join("");
    const leader = result.distribution[0];
    const runnerUp = result.distribution[1] || result.distribution[0];
    const safeClaims = [
      `${result.scenarioTitle || "This scenario"} has ${result.distribution.length} competing readings visible in the current notes.`,
      `${leader.label} is the strongest current reading in this local in-silico rehearsal.`,
      `The output is deterministic under seed ${result.seed} and changes when assumptions or frictions change.`
    ];
    const unsafeClaims = [
      "Do not say D-Predict/MiroFish predicts buyer behavior or startup success.",
      "Do not say this run proves adoption, demand or institutional readiness.",
      `Do not erase the competing reading "${runnerUp.label}" until evidence makes the tradeoff clearer.`
    ];
    const nextEvidence = [
      "Collect one buyer or facilitator reaction that can distinguish the top two readings.",
      "Run the same scenario with a lower and higher context friction setting.",
      "Document which assumption would change the distribution most if it turned out false."
    ];
    $("safe-claims").innerHTML = list(safeClaims);
    $("unsafe-claims").innerHTML = list(unsafeClaims);
    $("next-evidence").innerHTML = list(nextEvidence);
    renderMap(result);
    status.textContent = "Local stress test complete. Evidence needed is explicit.";
    status.className = "dp-status is-ok text-sm font-bold";
  }

  function saveCurrent(result) {
    localStorage.setItem(storageKey, JSON.stringify(result));
    status.textContent = "Saved locally in this browser.";
    status.className = "dp-status is-ok text-sm font-bold";
  }

  function updateSliderLabels() {
    const pairs = [
      ["measurement-pressure", "measurement-value"],
      ["alignment-field", "alignment-value"],
      ["trust-density", "trust-value"],
      ["context-friction", "friction-value"]
    ];
    pairs.forEach(([inputId, labelId]) => {
      const input = $(inputId);
      const label = $(labelId);
      if (input && label) label.textContent = round(Number(input.value) / 100, 2).toFixed(2);
    });
  }

  function run() {
    try {
      updateSliderLabels();
      const result = buildScenario(readInputs());
      renderResult(result);
      saveCurrent(result);
    } catch (error) {
      status.textContent = error.message || "The local scenario could not run.";
      status.className = "dp-status is-error text-sm font-bold";
    }
  }

  function loadSaved() {
    updateSliderLabels();
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey) || "null");
      if (saved && saved.distribution) {
        renderResult(saved);
        status.textContent = "Loaded local D-Predict/MiroFish draft.";
        status.className = "dp-status is-ok text-sm font-bold";
      } else {
        run();
      }
    } catch (_) {
      run();
    }
  }

  function reset() {
    localStorage.removeItem(storageKey);
    window.location.reload();
  }

  document.querySelectorAll("input[type='range']").forEach((input) => {
    input.addEventListener("input", updateSliderLabels);
  });
  $("run-scenario").addEventListener("click", run);
  $("save-scenario").addEventListener("click", () => saveCurrent(buildScenario(readInputs())));
  $("clear-scenario").addEventListener("click", reset);
  loadSaved();
}());
