const presets = {
  mexico: { currency: "MXN", taxRate: 0.30, inflationRate: 0.045, wacc: 0.16 },
  usa: { currency: "USD", taxRate: 0.21, inflationRate: 0.03, wacc: 0.12 },
  eu: { currency: "EUR", taxRate: 0.25, inflationRate: 0.025, wacc: 0.11 },
  uk: { currency: "GBP", taxRate: 0.25, inflationRate: 0.025, wacc: 0.11 },
  other: { currency: "USD", taxRate: 0.25, inflationRate: 0.03, wacc: 0.13 },
};

const state = {
  businessType: "physical",
  country: "eu",
  currency: "EUR",
  revenueModel: "usage",
  variableCost: 0.28,
  fixedCostsMonthly: 1500,
  semiVariableCostMonthly: 420,
  semiVariableStepUnits: 1200,
  competitorPrice: 0.55,
  desiredMargin: 0.45,
  minContributionMargin: 0.30,
  pricePosition: "competitive",
  unitsYear1: 1800,
  growthRate: 0.22,
  seasonality: "moderate",
  capex: 6500,
  capexYear: 1,
  usefulLife: 5,
  debt: 0,
  interestRate: 0.10,
  taxRate: 0.25,
  inflationRate: 0.025,
  wacc: 0.11,
  terminalGrowth: 0.025,
  workingCapitalPct: 0.08,
};

const fields = [
  { id: "businessType", block: "Identity", label: "What kind of business are we pricing?", type: "select", options: [["physical", "Physical product"], ["saas", "SaaS"], ["service", "Service"], ["marketplace", "Marketplace"]], help: "This changes how Billie thinks about cost structure." },
  { id: "country", block: "Identity", label: "Where will this model operate first?", type: "select", options: [["mexico", "Mexico"], ["usa", "United States"], ["eu", "European Union"], ["uk", "United Kingdom"], ["other", "Other / custom"]], help: "Billie uses this for currency, tax and inflation presets." },
  { id: "currency", block: "Identity", label: "What currency should Billie show?", type: "text", help: "Examples: MXN, USD, EUR, GBP." },
  { id: "revenueModel", block: "Identity", label: "How do customers pay?", type: "select", options: [["one_time", "One-time purchase"], ["subscription", "Subscription"], ["usage", "Per use"], ["commission", "Marketplace commission"]], help: "The model still projects annual revenue from units, seats or paid uses." },
  { id: "variableCost", block: "Costs", label: "What does one unit/use cost to deliver?", type: "number", step: "0.01", help: "Materials, payment fees, shipping, handling or direct service cost." },
  { id: "fixedCostsMonthly", block: "Costs", label: "What fixed cost do you carry each month?", type: "number", step: "1", help: "Rent, base payroll, software, recurring marketing or minimum operations." },
  { id: "semiVariableCostMonthly", block: "Costs", label: "What cost starts scaling in blocks?", type: "number", step: "1", help: "Example: one extra route, ops person, support pod or server tier." },
  { id: "semiVariableStepUnits", block: "Costs", label: "Every how many units does that step cost appear?", type: "number", step: "1", help: "Set the volume block that triggers semi-variable cost." },
  { id: "competitorPrice", block: "Pricing", label: "What is the closest competitor/reference price?", type: "number", step: "0.01", help: "Use 0 if unknown and Billie will rely on cost-plus pricing." },
  { id: "desiredMargin", block: "Pricing", label: "What gross margin would feel healthy?", type: "percent", step: "0.01", help: "45% means price equals unit cost times 1.45." },
  { id: "minContributionMargin", block: "Pricing", label: "What contribution margin is the floor?", type: "percent", step: "0.01", help: "Billie will not recommend a price below this floor." },
  { id: "pricePosition", block: "Pricing", label: "How do you want to position the offer?", type: "select", options: [["penetration", "Penetration"], ["competitive", "Competitive"], ["premium", "Premium"]], help: "This nudges the market anchor." },
  { id: "unitsYear1", block: "10-year growth", label: "How many units or paid uses in year 1?", type: "number", step: "1", help: "For SaaS, treat this as paid seats or subscriptions." },
  { id: "growthRate", block: "10-year growth", label: "What yearly growth rate should Billie test?", type: "percent", step: "0.01", help: "Use a conservative target, not pitch-deck fantasy." },
  { id: "seasonality", block: "10-year growth", label: "How seasonal is demand?", type: "select", options: [["none", "Not seasonal"], ["moderate", "Moderate"], ["high", "High"]], help: "For now this stays as a risk note; later it can become monthly cash flow." },
  { id: "capex", block: "Capital", label: "How much CAPEX is needed?", type: "number", step: "1", help: "Equipment, technology, setup or one-time operational investment." },
  { id: "capexYear", block: "Capital", label: "In which year does CAPEX happen?", type: "number", step: "1", help: "Use 1 to 10." },
  { id: "usefulLife", block: "Capital", label: "Over how many years is that CAPEX useful?", type: "number", step: "1", help: "Billie uses straight-line depreciation." },
  { id: "debt", block: "Capital", label: "How much debt is financing this?", type: "number", step: "1", help: "Set 0 if there is no debt." },
  { id: "interestRate", block: "Advanced", label: "Debt interest rate, if any", type: "percent", step: "0.01", help: "Affects FCFE; skip if there is no debt." },
  { id: "taxRate", block: "Advanced", label: "Corporate tax rate", type: "percent", step: "0.01", help: "Preset from country, editable if needed." },
  { id: "wacc", block: "Advanced", label: "Discount rate", type: "percent", step: "0.01", help: "Billie hides the jargon; advanced users can adjust it." },
  { id: "terminalGrowth", block: "Advanced", label: "Long-term terminal growth", type: "percent", step: "0.005", help: "Used for terminal value after year 10." },
  { id: "workingCapitalPct", block: "Advanced", label: "Working capital as % of new revenue", type: "percent", step: "0.01", help: "Higher inventory or receivables usually means a higher cash reserve." },
];

let currentQuestion = 0;
let currentFinancialScenarioDraft = null;
let currentFinancialScenarioIsValid = false;
const vertexRun = {
  runId: new URLSearchParams(window.location.search).get("run_id") || localStorage.getItem("vertex_current_run_id") || null,
  upstream: {},
};
if (vertexRun.runId) localStorage.setItem("vertex_current_run_id", vertexRun.runId);

async function loadRunArtifactForBillie(artifactType) {
  if (!vertexRun.runId) return null;
  const response = await fetch(`/api/vertex/runs/${encodeURIComponent(vertexRun.runId)}/artifacts/${artifactType}`);
  if (!response.ok) return null;
  const result = await response.json();
  return result.artifact || null;
}

async function loadVertexRunContextForBillie() {
  if (!vertexRun.runId) return;
  const entries = await Promise.all(["project_record", "problem_frame", "system_map"].map(async (artifactType) => [artifactType, await loadRunArtifactForBillie(artifactType)]));
  entries.forEach(([artifactType, artifact]) => {
    if (artifact) vertexRun.upstream[artifactType] = artifact;
  });
  setText("artifact-id", vertexRun.upstream.system_map ? `Billie output - ${vertexRun.runId} - upstream linked` : `Billie output - ${vertexRun.runId} - waiting for upstream artifacts`);
}

function money(value, currency = state.currency) {
  if (!Number.isFinite(value)) return "n/a";
  const digits = Math.abs(value) < 100 ? 2 : 0;
  return `${value.toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits })} ${currency}`;
}

function pct(value) {
  return Number.isFinite(value) ? `${(value * 100).toFixed(1)}%` : "n/a";
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function applyCountryPreset(country) {
  const preset = presets[country] || presets.other;
  state.currency = preset.currency;
  state.taxRate = preset.taxRate;
  state.inflationRate = preset.inflationRate;
  state.wacc = preset.wacc;
}

function calculateModel() {
  const unitsYear1 = Math.max(Number(state.unitsYear1), 1);
  const variableCost = Math.max(Number(state.variableCost), 0);
  const fixedAnnual = Math.max(Number(state.fixedCostsMonthly), 0) * 12;
  const stepUnits = Math.max(Number(state.semiVariableStepUnits), 1);
  const semiAnnualYear1 = Math.ceil(unitsYear1 / stepUnits) * Math.max(Number(state.semiVariableCostMonthly), 0) * 12;
  const fullUnitCost = variableCost + ((fixedAnnual + semiAnnualYear1) / unitsYear1);
  const costPlus = fullUnitCost * (1 + Math.max(Number(state.desiredMargin), 0));
  const marginFloor = clamp(Number(state.minContributionMargin), 0.01, 0.95);
  const minViable = variableCost / (1 - marginFloor);
  const competitor = Math.max(Number(state.competitorPrice), 0);
  const factor = state.pricePosition === "premium" ? 1.15 : state.pricePosition === "penetration" ? 0.90 : 1;
  const marketAnchor = competitor > 0 ? competitor * factor : costPlus;
  const suggestedPrice = Math.max(minViable, competitor > 0 ? ((costPlus + marketAnchor) / 2) : costPlus);
  const competitivePrice = Math.max(minViable, competitor > 0 ? competitor : costPlus);
  const premiumPrice = Math.max(competitivePrice * 1.15, costPlus * 1.10);
  const contributionMargin = suggestedPrice > 0 ? (suggestedPrice - variableCost) / suggestedPrice : 0;
  const breakevenUnits = suggestedPrice > variableCost ? (fixedAnnual + semiAnnualYear1) / (suggestedPrice - variableCost) : Infinity;
  const breakevenRevenue = breakevenUnits * suggestedPrice;
  const projection = buildProjection(suggestedPrice, variableCost, fixedAnnual, stepUnits);
  const wacc = Math.max(Number(state.wacc), 0.001);
  const terminalGrowth = Math.min(Number(state.terminalGrowth), wacc - 0.001);
  const fcf10 = projection[9].fcff;
  const terminalValue = fcf10 > 0 ? (fcf10 * (1 + terminalGrowth)) / (wacc - terminalGrowth) : 0;
  const npv = projection.reduce((sum, row) => sum + row.fcff / Math.pow(1 + wacc, row.year), 0) + terminalValue / Math.pow(1 + wacc, 10);
  const cashflows = [Number(state.capexYear) === 1 ? -Math.max(Number(state.capex), 0) : 0, ...projection.map((row) => row.fcff)];
  const irrValue = irr(cashflows);
  const payback = projection.find((row) => row.accumulated >= 0 && row.year >= Number(state.capexYear));
  return { fullUnitCost, minViable, competitivePrice, premiumPrice, suggestedPrice, contributionMargin, breakevenUnits, breakevenRevenue, projection, terminalValue, npv, irr: irrValue, paybackYear: payback ? payback.year : null };
}

function buildProjection(suggestedPrice, variableCost, fixedAnnual, stepUnits) {
  const rows = [];
  let previousRevenue = 0;
  let accumulated = 0;
  const taxRate = clamp(Number(state.taxRate), 0, 0.6);
  const inflation = clamp(Number(state.inflationRate), -0.05, 0.25);
  const growth = clamp(Number(state.growthRate), -0.8, 2);
  const capexYear = clamp(Math.round(Number(state.capexYear)), 1, 10);
  const usefulLife = Math.max(Math.round(Number(state.usefulLife)), 1);
  const capex = Math.max(Number(state.capex), 0);
  const debt = Math.max(Number(state.debt), 0);
  const interestRate = Math.max(Number(state.interestRate), 0);
  const annualPrincipal = debt > 0 ? debt / 5 : 0;
  for (let year = 1; year <= 10; year += 1) {
    const units = Number(state.unitsYear1) * Math.pow(1 + growth, year - 1);
    const inflationFactor = Math.pow(1 + inflation, year - 1);
    const price = suggestedPrice * inflationFactor;
    const revenue = units * price;
    const cogs = units * variableCost * inflationFactor;
    const semiVariable = Math.ceil(units / stepUnits) * Number(state.semiVariableCostMonthly) * 12 * inflationFactor;
    const opex = fixedAnnual * inflationFactor + semiVariable;
    const ebitda = revenue - cogs - opex;
    const depreciation = year >= capexYear && year < capexYear + usefulLife ? capex / usefulLife : 0;
    const ebit = ebitda - depreciation;
    const taxes = Math.max(0, ebit * taxRate);
    const capexOutflow = year === capexYear ? capex : 0;
    const deltaWorkingCapital = Math.max(0, revenue - previousRevenue) * clamp(Number(state.workingCapitalPct), 0, 0.6);
    const fcff = ebit * (1 - taxRate) + depreciation - capexOutflow - deltaWorkingCapital;
    const outstandingDebt = Math.max(0, debt - annualPrincipal * Math.max(0, year - 1));
    const interest = outstandingDebt * interestRate;
    const principal = debt > 0 && year <= 5 ? annualPrincipal : 0;
    const newDebt = debt > 0 && year === 1 ? debt : 0;
    const fcfe = fcff - interest * (1 - taxRate) - principal + newDebt;
    accumulated += fcff;
    rows.push({ year, units, price, revenue, cogs, opex, ebitda, depreciation, ebit, taxes, capexOutflow, deltaWorkingCapital, fcff, fcfe, accumulated });
    previousRevenue = revenue;
  }
  return rows;
}

function npvAt(rate, cashflows) {
  return cashflows.reduce((sum, cashflow, index) => sum + cashflow / Math.pow(1 + rate, index), 0);
}

function irr(cashflows) {
  if (!cashflows.some((v) => v > 0) || !cashflows.some((v) => v < 0)) return NaN;
  let low = -0.95;
  let high = 2.5;
  let lowValue = npvAt(low, cashflows);
  if (lowValue * npvAt(high, cashflows) > 0) return NaN;
  for (let i = 0; i < 80; i += 1) {
    const mid = (low + high) / 2;
    const midValue = npvAt(mid, cashflows);
    if (Math.abs(midValue) < 0.0001) return mid;
    if (lowValue * midValue < 0) high = mid;
    else {
      low = mid;
      lowValue = midValue;
    }
  }
  return (low + high) / 2;
}

function valueLabel(field) {
  const value = state[field.id];
  if (field.type === "percent") return pct(Number(value));
  if (field.type === "select") return (field.options.find((item) => item[0] === value) || [null, value])[1];
  if (["variableCost", "fixedCostsMonthly", "semiVariableCostMonthly", "competitorPrice", "capex", "debt"].includes(field.id)) return money(Number(value));
  return String(value);
}

function renderQuestion() {
  const field = fields[currentQuestion];
  document.getElementById("question-block").textContent = field.block;
  document.getElementById("question-count").textContent = `${String(currentQuestion + 1).padStart(2, "0")} / ${fields.length}`;
  document.getElementById("question-title").textContent = field.label;
  document.getElementById("question-help").textContent = field.help;
  document.getElementById("progress-fill").style.width = `${((currentQuestion + 1) / fields.length) * 100}%`;
  const wrap = document.getElementById("question-input");
  if (field.type === "select") {
    wrap.innerHTML = `<select id="active-input">${field.options.map((item) => `<option value="${item[0]}">${item[1]}</option>`).join("")}</select>`;
  } else {
    const type = field.type === "text" ? "text" : "number";
    const value = field.type === "percent" ? Number(state[field.id]) * 100 : state[field.id];
    wrap.innerHTML = `<input id="active-input" type="${type}" step="${field.step || "1"}" value="${value}">`;
  }
  const input = document.getElementById("active-input");
  input.value = field.type === "percent" ? Number(state[field.id]) * 100 : state[field.id];
  input.addEventListener("input", () => {
    state[field.id] = field.type === "percent" ? Number(input.value) / 100 : field.type === "number" ? Number(input.value) : input.value;
    if (field.id === "country") applyCountryPreset(input.value);
    renderFieldList();
    updateAll();
  });
  renderFieldList();
  updateAll();
}

function renderFieldList() {
  document.getElementById("field-list").innerHTML = fields.map((field, index) => `
    <button class="field-pill ${index === currentQuestion ? "active" : ""}" type="button" data-field-index="${index}">
      <strong>${field.label}</strong><span>${valueLabel(field)}</span>
    </button>`).join("");
  document.querySelectorAll(".field-pill").forEach((button) => button.addEventListener("click", () => {
    currentQuestion = Number(button.dataset.fieldIndex);
    renderQuestion();
  }));
}

function updateAll() {
  const model = calculateModel();
  setText("hero-price", money(model.suggestedPrice));
  setText("hero-margin", pct(model.contributionMargin));
  setText("hero-npv", money(model.npv));
  setText("hero-irr", Number.isFinite(model.irr) ? pct(model.irr) : "n/a");
  setText("artifact-id", `Billie draft - ${state.businessType} - ${state.currency} - FinancialScenario`);
  setText("suggested-price", money(model.suggestedPrice));
  setText("breakeven-units", Number.isFinite(model.breakevenUnits) ? Math.ceil(model.breakevenUnits).toLocaleString() : "n/a");
  setText("contribution-margin", pct(model.contributionMargin));
  setText("price-min", money(model.minViable));
  setText("price-market", money(model.competitivePrice));
  setText("price-premium", money(model.premiumPrice));
  setText("npv-value", money(model.npv));
  setText("irr-value", Number.isFinite(model.irr) ? pct(model.irr) : "n/a");
  setText("terminal-value", money(model.terminalValue));
  document.getElementById("result-notes").innerHTML = [row("Unit cost", `${money(model.fullUnitCost)} including allocated fixed and step costs.`), row("Break-even revenue", `${money(model.breakevenRevenue)} at the suggested price.`), row("Positioning", `${state.pricePosition} strategy with ${state.seasonality} seasonality risk.`)].join("");
  document.getElementById("projection-notes").innerHTML = [row("Payback", model.paybackYear ? `Cumulative FCFF turns positive in year ${model.paybackYear}.` : "Cumulative FCFF does not turn positive in the 10-year window."), row("Advanced defaults", `Discount ${pct(state.wacc)}, tax ${pct(state.taxRate)}, terminal growth ${pct(state.terminalGrowth)}.`)].join("");
  renderProjectionTable(model.projection);
  drawBreakevenChart(model);
  drawCashflowChart(model.projection);
}

function buildFinancialScenarioDraft() {
  const model = calculateModel();
  const now = new Date().toISOString();
  const revenueYear1 = Math.round(model.projection[0].revenue);
  const costYear1 = Math.round(model.projection[0].cogs + model.projection[0].opex + model.projection[0].capexOutflow);
  const cashGap = Math.max(0, costYear1 - revenueYear1);
  const upstream = vertexRun.upstream || {};
  const projectRecord = upstream.project_record || null;
  const problemFrame = upstream.problem_frame || null;
  const systemMap = upstream.system_map || null;
  const runSuffix = vertexRun.runId ? vertexRun.runId.replaceAll("-", "_") : "runless";
  if (!vertexRun.runId) {
    throw new Error("Billie requires an active Golden Path run before creating a FinancialScenario.");
  }
  if (!projectRecord || !problemFrame || !systemMap) {
    throw new Error("Billie requires ProjectRecord, ProblemFrame and SystemMap upstream artifacts before creating a FinancialScenario.");
  }
  const financialAssumptions = (systemMap.approved_assumptions || []).filter((item) => item.approved_for_financial_processing === true);
  if (!financialAssumptions.length) {
    throw new Error("Billie requires at least one SystemMap assumption approved for financial processing. Open Assumption Approval before creating a FinancialScenario.");
  }
  const priceRef = pickFinancialRef(financialAssumptions, 0, ["fee", "price", "deposit", "revenue"]);
  const variableCostRef = pickFinancialRef(financialAssumptions, 1, ["cost", "washing", "handling"]);
  const fixedCostRef = pickFinancialRef(financialAssumptions, 2, ["capacity", "staff", "setup", "buffer"]);
  const unitsRef = pickFinancialRef(financialAssumptions, 3, ["volume", "uses", "customers"]);
  const growthRef = pickFinancialRef(financialAssumptions, 4, ["adoption", "acceptance", "growth"]);
  const capexRef = pickFinancialRef(financialAssumptions, 5, ["setup", "buffer", "capex"]);
  const refs = unique([priceRef, variableCostRef, fixedCostRef, unitsRef, growthRef, capexRef]);
  return {
    schema_version: "1.0.0",
    artifact_type: "financial_scenario",
    artifact_id: `financial_scenario_${runSuffix}`,
    project_id: projectRecord?.project_id || `project_${runSuffix}`,
    created_at: now,
    created_by_role: "finops",
    status: "draft",
    provenance: {
      source_kind: "user_supplied",
      source_label: "Billie pricing and 10-year projection wizard",
      ip_owner: "Billie user",
      external_components_used: [],
      notes: "Generated by Billie from founder-facing inputs. Values are calculated in the local FinOps prototype and require founder review."
    },
    human_approval: {
      required: true,
      state: "pending",
      approved_by_role: "founder",
      approved_at: now,
      notes: "Pending founder review before this FinancialScenario can feed a DecisionRecord."
    },
    validation_errors: [],
    preceding_artifacts: {
      project_record_id: projectRecord.artifact_id,
      problem_frame_id: problemFrame.artifact_id,
      system_map_id: systemMap.artifact_id
    },
    approved_assumption_references: refs,
    currency: state.currency,
    scenario_name: `Billie ${state.businessType} ${state.pricePosition} pricing scenario`,
    time_horizon: "10 years",
    pricing_assumptions: [
      assumption("fin_price_suggested", "Suggested price", round2(model.suggestedPrice), `${state.currency} per unit/use`, priceRef),
      assumption("fin_price_min_viable", "Minimum viable price", round2(model.minViable), `${state.currency} per unit/use`, priceRef),
      assumption("fin_price_premium", "Premium price", round2(model.premiumPrice), `${state.currency} per unit/use`, priceRef)
    ],
    cost_assumptions: [
      assumption("fin_variable_cost", "Variable cost per unit/use", round2(state.variableCost), `${state.currency} per unit/use`, variableCostRef),
      assumption("fin_fixed_costs_monthly", "Fixed costs per month", Math.round(state.fixedCostsMonthly), `${state.currency} per month`, fixedCostRef),
      assumption("fin_capex", "Initial or expansion CAPEX", Math.round(state.capex), state.currency, capexRef)
    ],
    volume_assumptions: [
      assumption("fin_year_1_units", "Year 1 units or paid uses", Math.round(state.unitsYear1), "units", unitsRef),
      assumption("fin_growth_rate", "Annual growth rate percentage", Math.round(state.growthRate * 100), "percent", growthRef)
    ],
    revenue_projection: {
      value: revenueYear1,
      unit: state.currency,
      is_fixture_value: false,
      classification: "hypothesis",
      calculation_note: `Year 1 revenue = units (${Math.round(state.unitsYear1)}) x suggested price (${round2(model.suggestedPrice)}).`
    },
    cost_projection: {
      value: costYear1,
      unit: state.currency,
      is_fixture_value: false,
      classification: "hypothesis",
      calculation_note: "Year 1 cost includes COGS, fixed opex, semi-variable opex and CAPEX if scheduled in year 1."
    },
    cash_requirement: {
      value: cashGap,
      unit: state.currency,
      is_fixture_value: false,
      classification: "hypothesis",
      calculation_note: "Positive gap between first-year total cost and revenue; excludes financing strategy beyond declared debt input."
    },
    sustainability_indicators: [{
      indicator_id: "sus_financial_learning",
      statement: "Billie turns pricing, cost and runway assumptions into explicit decision learning before scale-up.",
      classification: "inference",
      confidence: 0.7
    }],
    sensitivity_notes: [
      {
        note_id: "sens_break_even",
        statement: `Break-even requires ${Number.isFinite(model.breakevenUnits) ? Math.ceil(model.breakevenUnits).toLocaleString() : "unresolved"} units at the suggested price.`,
        classification: "hypothesis"
      },
      {
        note_id: "sens_valuation",
        statement: `10-year NPV is ${money(model.npv)} and IRR is ${Number.isFinite(model.irr) ? pct(model.irr) : "not available"} under current assumptions.`,
        classification: "hypothesis"
      }
    ],
    uncertainty: {
      level: uncertaintyLevel(model),
      drivers: ["founder-supplied assumptions", "unvalidated demand forecast", "country tax and discount-rate presets"],
      unknowns_preserved: ["unk_actual_customer_willingness_to_pay", "unk_actual_growth_rate"]
    },
    approval_state: "pending_financial_review",
    revision: 1,
    updated_at: now
  };
}

function unique(values) {
  return Array.from(new Set(values.filter(Boolean)));
}

function pickFinancialRef(financialAssumptions, fallbackIndex, keywords) {
  const match = financialAssumptions.find((item) => {
    const text = `${item.assumption_id || ""} ${item.statement || ""}`.toLowerCase();
    return keywords.some((keyword) => text.includes(keyword));
  });
  const fallback = financialAssumptions[fallbackIndex % financialAssumptions.length];
  return (match || fallback).assumption_id;
}

function assumption(assumptionId, label, value, unit, sourceRef) {
  return { assumption_id: assumptionId, label, value, unit, is_fixture_value: false, source_assumption_ref: sourceRef };
}

function round2(value) {
  return Math.round(Number(value) * 100) / 100;
}

function uncertaintyLevel(model) {
  if (!Number.isFinite(model.irr) || state.seasonality === "high" || Number(state.growthRate) > 0.5) return "high";
  if (Number(state.growthRate) > 0.25 || Number(state.capex) > model.projection[0].revenue) return "medium";
  return "low";
}

async function createFinancialScenarioPreview() {
  const preview = document.getElementById("contract-preview");
  const status = document.getElementById("contract-status");
  const badge = document.getElementById("contract-badge");
  const output = document.getElementById("contract-json");
  let draft;
  try {
    draft = buildFinancialScenarioDraft();
  } catch (error) {
    preview.classList.add("active");
    status.textContent = error.message;
    status.className = "copy status-bad";
    badge.textContent = "Missing run";
    badge.className = "contract-badge bad";
    output.textContent = JSON.stringify({ error: error.message }, null, 2);
    preview.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }
  preview.classList.add("active");
  currentFinancialScenarioDraft = draft;
  currentFinancialScenarioIsValid = false;
  const saveButton = document.getElementById("save-scenario");
  if (saveButton) saveButton.disabled = true;
  renderContractReview(draft);
  status.textContent = "Checking the FinancialScenario contract...";
  status.className = "copy";
  badge.textContent = "Checking";
  badge.className = "contract-badge";
  output.textContent = JSON.stringify(draft, null, 2);
  try {
    const validationUrl = `/api/vertex/runs/${encodeURIComponent(vertexRun.runId)}/artifacts/financial_scenario/validate`;
    const response = await fetch(validationUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(draft)
    });
    const result = await response.json();
    if (result.valid) {
      status.textContent = "Schema valid. Billie translated the model into a FinancialScenario draft ready for founder review.";
      status.className = "copy status-ok";
      badge.textContent = "Schema valid";
      badge.className = "contract-badge ok";
      currentFinancialScenarioIsValid = true;
      if (saveButton) saveButton.disabled = false;
    } else {
      status.textContent = `Needs attention before review: ${result.errors.length} schema issue(s).`;
      status.className = "copy status-bad";
      badge.textContent = "Needs fix";
      badge.className = "contract-badge bad";
      currentFinancialScenarioIsValid = false;
      if (saveButton) saveButton.disabled = true;
      output.textContent = JSON.stringify({ errors: result.errors, artifact: draft }, null, 2);
    }
  } catch (error) {
    status.textContent = `Validation failed: ${error.message}`;
    status.className = "copy status-bad";
    badge.textContent = "Offline";
    badge.className = "contract-badge bad";
  }
  preview.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderContractReview(draft) {
  setText("contract-price", money(draft.pricing_assumptions[0].value, draft.currency));
  setText("contract-revenue", money(draft.revenue_projection.value, draft.currency));
  setText("contract-cash", money(draft.cash_requirement.value, draft.currency));
  setText("contract-uncertainty", draft.uncertainty.level);
  document.getElementById("contract-pricing").innerHTML = draft.pricing_assumptions.map((item) => contractItem(item.label, `${money(item.value, draft.currency)} - ${item.unit}`)).join("");
  document.getElementById("contract-assumptions").innerHTML = [
    ...draft.cost_assumptions.map((item) => contractItem(item.label, `${money(item.value, draft.currency)} - ${item.unit}`)),
    ...draft.volume_assumptions.map((item) => contractItem(item.label, `${item.value.toLocaleString()} ${item.unit}`))
  ].join("");
  document.getElementById("contract-signals").innerHTML = [
    contractItem("Revenue hypothesis", draft.revenue_projection.calculation_note),
    contractItem("Cash requirement", draft.cash_requirement.calculation_note),
    ...draft.sensitivity_notes.map((item) => contractItem(item.note_id.replaceAll("_", " "), item.statement))
  ].join("");
}

function contractItem(title, body) {
  return `<div class="contract-item"><strong>${title}</strong><p>${body}</p></div>`;
}

async function saveFinancialScenarioDraft() {
  const status = document.getElementById("contract-status");
  const badge = document.getElementById("contract-badge");
  if (!currentFinancialScenarioDraft || !currentFinancialScenarioIsValid) {
    status.textContent = "Create a schema-valid FinancialScenario before saving.";
    status.className = "copy status-bad";
    return;
  }
  status.textContent = "Saving FinancialScenario draft...";
  status.className = "copy";
  try {
    const saveUrl = `/api/vertex/runs/${encodeURIComponent(vertexRun.runId)}/artifacts/financial_scenario/save`;
    const response = await fetch(saveUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(currentFinancialScenarioDraft)
    });
    const result = await response.json();
    if (!response.ok || !result.saved) {
      status.textContent = `Could not save draft: ${(result.errors || [{ message: response.statusText }])[0].message}`;
      status.className = "copy status-bad";
      badge.textContent = "Save failed";
      badge.className = "contract-badge bad";
      return;
    }
    status.textContent = "Draft saved to the active Golden Path run. Billie can now feed DecisionRecord with a real FinancialScenario artifact.";
    status.className = "copy status-ok";
    badge.textContent = "Saved draft";
    badge.className = "contract-badge ok";
    await loadSavedFinancialScenarios();
  } catch (error) {
    status.textContent = `Could not save draft: ${error.message}`;
    status.className = "copy status-bad";
    badge.textContent = "Save failed";
    badge.className = "contract-badge bad";
  }
}

async function loadSavedFinancialScenarios() {
  const container = document.getElementById("saved-scenarios");
  if (!container) return;
  try {
    const response = await fetch("/api/billie/financial-scenarios");
    const result = await response.json();
    const scenarios = result.scenarios || [];
    if (!scenarios.length) {
      container.innerHTML = '<div class="contract-item"><strong>No drafts yet</strong><p>Create and save a FinancialScenario to see it here.</p></div>';
      return;
    }
    container.innerHTML = scenarios.map((scenario) => contractItem(
      scenario.scenario_name || scenario.artifact_id,
      `${scenario.currency} ? ${scenario.time_horizon} ? revenue ${scenario.revenue_projection?.toLocaleString?.() || scenario.revenue_projection || 0} ? cash gap ${scenario.cash_requirement?.toLocaleString?.() || scenario.cash_requirement || 0} ? ${scenario.approval_state}`
    )).join("");
  } catch (error) {
    container.innerHTML = contractItem("Could not load drafts", error.message);
  }
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function row(title, body) {
  return `<div class="row"><strong>${title}</strong><p>${body}</p></div>`;
}

function renderProjectionTable(rows) {
  const metrics = [["Units", "units"], ["Price", "price"], ["Revenue", "revenue"], ["COGS", "cogs"], ["Opex", "opex"], ["EBITDA", "ebitda"], ["D&A", "depreciation"], ["EBIT", "ebit"], ["Taxes", "taxes"], ["CAPEX", "capexOutflow"], ["Delta WC", "deltaWorkingCapital"], ["FCFF", "fcff"], ["FCFE", "fcfe"], ["Cumulative FCFF", "accumulated"]];
  document.getElementById("projection-table").innerHTML = `<thead><tr><th>Metric</th>${rows.map((r) => `<th>Y${r.year}</th>`).join("")}</tr></thead><tbody>${metrics.map(([label, key]) => `<tr><td>${label}</td>${rows.map((r) => `<td>${key === "units" ? Math.round(r[key]).toLocaleString() : money(r[key])}</td>`).join("")}</tr>`).join("")}</tbody>`;
}

function drawBreakevenChart(model) {
  const maxUnits = Math.max(Number(state.unitsYear1) * 1.4, model.breakevenUnits * 1.25, 10);
  const fixedAnnual = Number(state.fixedCostsMonthly) * 12;
  const maxY = Math.max(maxUnits * model.suggestedPrice, fixedAnnual + maxUnits * Number(state.variableCost)) * 1.12;
  drawChart("breakeven-chart", [
    { label: "Revenue", color: "#1946D1", points: Array.from({ length: 24 }, (_, i) => { const u = maxUnits * i / 23; return [u / maxUnits, (u * model.suggestedPrice) / maxY]; }) },
    { label: "Total cost", color: "#E74530", points: Array.from({ length: 24 }, (_, i) => { const u = maxUnits * i / 23; return [u / maxUnits, (fixedAnnual + u * Number(state.variableCost)) / maxY]; }) },
  ]);
}

function drawCashflowChart(rows) {
  const values = rows.map((r) => r.accumulated);
  const min = Math.min(0, ...values);
  const span = Math.max(1, Math.max(...values) - min);
  drawChart("cashflow-chart", [{ label: "Cumulative FCFF", color: "#1946D1", points: rows.map((r, i) => [i / (rows.length - 1), (r.accumulated - min) / span]) }]);
}

function drawChart(id, series) {
  const canvas = document.getElementById(id);
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  ctx.clearRect(0, 0, width, height);
  ctx.strokeStyle = "rgba(24,24,16,0.18)";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(54, 22);
  ctx.lineTo(54, height - 38);
  ctx.lineTo(width - 22, height - 38);
  ctx.stroke();
  series.forEach((item, index) => {
    ctx.strokeStyle = item.color;
    ctx.lineWidth = 4;
    ctx.beginPath();
    item.points.forEach(([x, y], i) => {
      const px = 54 + x * (width - 78);
      const py = 22 + (1 - y) * (height - 60);
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    });
    ctx.stroke();
    ctx.fillStyle = item.color;
    ctx.fillRect(70 + index * 170, 16, 18, 10);
    ctx.fillStyle = "#181810";
    ctx.font = "bold 13px Arial";
    ctx.fillText(item.label, 96 + index * 170, 26);
  });
}

function setScreen(name) {
  document.querySelectorAll(".screen").forEach((screen) => screen.classList.toggle("active", screen.id === `screen-${name}`));
  document.querySelectorAll(".tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.screen === name));
  updateAll();
}

document.querySelectorAll(".tab").forEach((tab) => tab.addEventListener("click", () => setScreen(tab.dataset.screen)));
document.querySelectorAll("[data-screen-jump]").forEach((button) => button.addEventListener("click", () => setScreen(button.dataset.screenJump)));
document.getElementById("prev-question").addEventListener("click", () => { currentQuestion = Math.max(0, currentQuestion - 1); renderQuestion(); });
document.getElementById("next-question").addEventListener("click", () => { currentQuestion = Math.min(fields.length - 1, currentQuestion + 1); renderQuestion(); });
document.getElementById("create-scenario").addEventListener("click", createFinancialScenarioPreview);
document.getElementById("save-scenario").addEventListener("click", saveFinancialScenarioDraft);
document.getElementById("refresh-scenarios").addEventListener("click", loadSavedFinancialScenarios);

fetch("/api/vertex/golden-case")
  .then((response) => response.ok ? response.json() : null)
  .then((data) => {
    if (data && data.financial) {
      const financial = data.financial;
      state.currency = financial.currency || state.currency;
      if (financial.pricing_assumptions && financial.pricing_assumptions[0]) state.competitorPrice = Number(financial.pricing_assumptions[0].value) || state.competitorPrice;
      if (financial.cost_assumptions && financial.cost_assumptions[0]) state.variableCost = Number(financial.cost_assumptions[0].value) || state.variableCost;
      if (financial.volume_assumptions && financial.volume_assumptions[0]) state.unitsYear1 = Number(financial.volume_assumptions[0].value) || state.unitsYear1;
    }
    renderQuestion();
  })
  .catch(() => renderQuestion());

renderQuestion();
