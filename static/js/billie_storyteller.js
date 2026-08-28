(function () {
  const STORAGE_KEY = "billie_storyteller_current";
  const EMPTY_TEXT = "No draft yet.";

  const fields = [
    "projectName",
    "audience",
    "problem",
    "founderInsight",
    "availableEvidence",
    "tone",
    "channel",
    "communicationGoal",
    "cannotClaim"
  ];

  const outputTargets = {
    positioning_statement: "out-positioning",
    one_liner: "out-one-liner",
    founder_story: "out-founder-story",
    buyer_program_narrative: "out-buyer-narrative",
    pitch_opening: "out-pitch-opening",
    content_angles: "out-content-angles",
    safe_claims: "out-safe-claims",
    unsafe_claims: "out-unsafe-claims",
    next_evidence_needed: "out-next-evidence"
  };

  let currentDraft = null;

  function byId(id) {
    return document.getElementById(id);
  }

  function setStatus(message, type) {
    const status = byId("billie-status");
    if (!status) return;
    status.textContent = message;
    status.classList.remove("is-error", "is-ok");
    if (type) status.classList.add(type === "error" ? "is-error" : "is-ok");
  }

  function collectInputs() {
    const form = byId("billie-form");
    const data = {};
    fields.forEach((name) => {
      const el = form?.elements[name];
      data[name] = (el?.value || "").trim();
    });
    return data;
  }

  function hydrateInputs(data) {
    const form = byId("billie-form");
    if (!form || !data) return;
    fields.forEach((name) => {
      if (form.elements[name] && data[name] !== undefined) {
        form.elements[name].value = data[name];
      }
    });
  }

  function asArray(value) {
    if (Array.isArray(value)) return value.filter(Boolean).map(String);
    if (typeof value === "string" && value.trim()) return [value.trim()];
    return [];
  }

  function renderList(id, items, fallback) {
    const target = byId(id);
    if (!target) return;
    const safeItems = asArray(items);
    if (!safeItems.length) {
      target.innerHTML = `<li>${fallback}</li>`;
      return;
    }
    target.innerHTML = safeItems.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  }

  function renderText(id, value) {
    const target = byId(id);
    if (!target) return;
    target.textContent = String(value || EMPTY_TEXT);
  }

  function renderDraft(draft) {
    currentDraft = draft || null;
    renderText(outputTargets.positioning_statement, draft?.positioning_statement);
    renderText(outputTargets.one_liner, draft?.one_liner);
    renderText(outputTargets.founder_story, draft?.founder_story);
    renderText(outputTargets.buyer_program_narrative, draft?.buyer_program_narrative);
    renderText(outputTargets.pitch_opening, draft?.pitch_opening);
    renderList(outputTargets.content_angles, draft?.content_angles, "No content angles drafted yet.");
    renderList(outputTargets.safe_claims, draft?.safe_claims, "No claims drafted yet.");
    renderList(outputTargets.unsafe_claims, draft?.unsafe_claims, "No claims flagged yet.");
    renderList(outputTargets.next_evidence_needed, draft?.next_evidence_needed, "No evidence gaps listed yet.");
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function stripCodeFence(value) {
    return String(value || "")
      .replace(/^```json\s*/i, "")
      .replace(/^```\s*/i, "")
      .replace(/\s*```$/i, "")
      .trim();
  }

  function parseModelJson(raw) {
    const clean = stripCodeFence(raw);
    try {
      return JSON.parse(clean);
    } catch (error) {
      throw new Error("Billie returned a draft that was not valid JSON. Try again with shorter evidence notes.");
    }
  }

  function buildPrompt(inputs) {
    return `Create Billie Storyteller v1 output as strict JSON.

Billie is a Srsly Labs Lab storyteller for narrative, brand, positioning, content and pitch language.
Billie converts founder judgment, technical context and evidence available into clear language.

Boundaries:
- Do not invent evidence.
- Do not create a deck.
- Do not calculate finance, price, runway or forecast.
- Do not decide for the founder.
- Use careful language such as "Evidence available", "Observed signal", "Claim supported by current notes", "Claim needs more evidence" and "Do not say yet".
- Avoid certainty language that implies outcomes are already established.
- Do not use terms such as "proved", "validated", "guaranteed" or "confirmed outcome".

Inputs:
${JSON.stringify(inputs, null, 2)}

Return only JSON with this shape:
{
  "positioning_statement": "string",
  "one_liner": "string",
  "founder_story": "string",
  "buyer_program_narrative": "string",
  "pitch_opening": "string",
  "content_angles": ["string"],
  "safe_claims": ["string"],
  "unsafe_claims": ["string"],
  "next_evidence_needed": ["string"]
}`;
  }

  async function generateStory() {
    const inputs = collectInputs();
    if (!inputs.projectName || !inputs.problem || !inputs.founderInsight) {
      setStatus("Add project name, problem and founder insight first.", "error");
      return;
    }

    setStatus("Billie is shaping the narrative...", "ok");
    try {
      const response = await fetch("/api/openai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify({
          model: "gpt-4o",
          response_format: { type: "json_object" },
          messages: [
            {
              role: "system",
              content: "You are Billie Storyteller for Srsly Labs Lab. Return concise, honest JSON only."
            },
            { role: "user", content: buildPrompt(inputs) }
          ],
          temperature: 0.65
        })
      });

      if (!response.ok) {
        throw new Error(`Billie could not generate a draft (${response.status}).`);
      }

      const data = await response.json();
      const raw = data?.choices?.[0]?.message?.content;
      const draft = parseModelJson(raw);
      renderDraft(draft);
      saveDraft(false);
      setStatus("Draft narrative ready", "ok");
    } catch (error) {
      console.error(error);
      setStatus(error.message || "Billie could not generate a draft.", "error");
    }
  }

  function saveDraft(showStatus = true) {
    const payload = {
      inputs: collectInputs(),
      draft: currentDraft,
      savedAt: new Date().toISOString()
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    if (showStatus) setStatus("Draft saved locally", "ok");
  }

  function loadDraft() {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    try {
      const payload = JSON.parse(raw);
      hydrateInputs(payload.inputs);
      if (payload.draft) renderDraft(payload.draft);
      setStatus("Local draft loaded", "ok");
    } catch (error) {
      console.warn("Could not load Billie draft", error);
    }
  }

  function clearDraft() {
    localStorage.removeItem(STORAGE_KEY);
    const form = byId("billie-form");
    if (form) form.reset();
    renderDraft(null);
    setStatus("Draft cleared", "ok");
  }

  async function copyOutput() {
    if (!currentDraft) {
      setStatus("Generate a draft before copying.", "error");
      return;
    }
    const text = [
      `Positioning Statement\n${currentDraft.positioning_statement || ""}`,
      `One-Liner\n${currentDraft.one_liner || ""}`,
      `Founder Story\n${currentDraft.founder_story || ""}`,
      `Buyer / Program Narrative\n${currentDraft.buyer_program_narrative || ""}`,
      `Pitch Opening\n${currentDraft.pitch_opening || ""}`,
      `Content Angles\n${asArray(currentDraft.content_angles).map((item) => `- ${item}`).join("\n")}`,
      `Safe Claims\n${asArray(currentDraft.safe_claims).map((item) => `- ${item}`).join("\n")}`,
      `Unsafe Claims\n${asArray(currentDraft.unsafe_claims).map((item) => `- ${item}`).join("\n")}`,
      `Next Evidence Needed\n${asArray(currentDraft.next_evidence_needed).map((item) => `- ${item}`).join("\n")}`
    ].join("\n\n");

    try {
      await navigator.clipboard.writeText(text);
      setStatus("Output copied", "ok");
    } catch (error) {
      setStatus("Could not copy automatically. Select the text manually.", "error");
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    byId("generate-story")?.addEventListener("click", generateStory);
    byId("save-story")?.addEventListener("click", () => saveDraft(true));
    byId("clear-story")?.addEventListener("click", clearDraft);
    byId("copy-story")?.addEventListener("click", copyOutput);
    loadDraft();
  });
})();
