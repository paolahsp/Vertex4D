(() => {
  const root = document.documentElement;
  const allowed = {
    theme: ["dark", "light"],
    motion: ["full", "reduced", "none"],
    focus: ["on", "off"],
  };
  const storageKey = "vertex4d_prefs";
  const systemMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "reduced" : "full";
  const defaults = { theme: "dark", motion: systemMotion, focus: "off" };

  function clean(prefs) {
    const next = { ...defaults };
    if (prefs && typeof prefs === "object") {
      Object.keys(allowed).forEach((key) => {
        if (allowed[key].includes(prefs[key])) next[key] = prefs[key];
      });
    }
    return next;
  }

  function readLocal() {
    try { return clean(JSON.parse(localStorage.getItem(storageKey) || "{}")); }
    catch (_) { return { ...defaults }; }
  }

  function apply(prefs) {
    const next = clean(prefs);
    root.dataset.theme = next.theme;
    root.dataset.motion = next.motion;
    root.dataset.focus = next.focus;
    updateControls(next);
    return next;
  }

  function saveLocal(prefs) {
    try { localStorage.setItem(storageKey, JSON.stringify(clean(prefs))); }
    catch (_) {}
  }

  async function saveRemote(prefs) {
    try {
      await fetch("/api/user/preferences", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(clean(prefs)),
      });
    } catch (_) {}
  }

  function setPref(key, value) {
    if (!allowed[key].includes(value)) return;
    const next = clean({ ...readLocal(), ...root.dataset, [key]: value });
    apply(next);
    saveLocal(next);
    saveRemote(next);
  }

  function button(label, key, value) {
    const el = document.createElement("button");
    el.type = "button";
    el.textContent = label;
    el.dataset.prefKey = key;
    el.dataset.prefValue = value;
    el.setAttribute("aria-label", `${key}: ${value}`);
    el.addEventListener("click", () => setPref(key, value));
    return el;
  }

  function updateControls(prefs) {
    document.querySelectorAll("[data-pref-key]").forEach((el) => {
      el.setAttribute("aria-pressed", String(prefs[el.dataset.prefKey] === el.dataset.prefValue));
    });
  }

  function mountControls() {
    if (document.querySelector(".pref-panel")) return;
    const panel = document.createElement("aside");
    panel.className = "pref-panel";
    panel.setAttribute("aria-label", "Display preferences");
    const focusButton = document.createElement("button");
    focusButton.type = "button";
    focusButton.textContent = "Focus";
    focusButton.dataset.prefKey = "focus";
    focusButton.dataset.prefValue = "on";
    focusButton.setAttribute("aria-label", "toggle focus mode");
    focusButton.addEventListener("click", () => setPref("focus", root.dataset.focus === "on" ? "off" : "on"));
    panel.append(
      button("Dark", "theme", "dark"),
      button("Light", "theme", "light"),
      button("Move", "motion", "full"),
      button("Calm", "motion", "reduced"),
      button("Still", "motion", "none"),
      focusButton
    );
    document.body.append(panel);
    updateControls(clean({ ...readLocal(), ...root.dataset }));
  }

  const initial = clean({ ...readLocal(), ...root.dataset });
  apply(initial);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mountControls);
  else mountControls();
})();
