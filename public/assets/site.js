// La navegación y el contacto funcionan sin JavaScript. Solo una pregunta abierta a la vez.
for (const item of document.querySelectorAll(".faq details")) {
  item.addEventListener("toggle", () => {
    if (item.open)
      for (const other of document.querySelectorAll(".faq details"))
        if (other !== item) other.open = false;
  });
}

// Preferencia local; no se envía al servidor ni se utiliza para seguimiento.
(() => {
  const root = document.documentElement;
  const system = window.matchMedia("(prefers-color-scheme: dark)");
  const controls = document.querySelectorAll(".theme-toggle");
  let chosen;
  try {
    chosen = localStorage.getItem("pary-theme");
  } catch {
    /* Navegación privada o almacenamiento deshabilitado. */
  }
  if (chosen !== "light" && chosen !== "dark") chosen = null;
  const apply = (theme) => {
    root.dataset.theme = theme;
    const next = theme === "dark" ? "claro" : "oscuro";
    for (const control of controls) {
      control.setAttribute("aria-label", `Activar modo ${next}`);
      control.title = `Activar modo ${next}`;
      control.querySelector(".theme-label").textContent = theme === "dark" ? "Claro" : "Oscuro";
      control.hidden = false;
    }
    document
      .querySelector('meta[name="theme-color"]')
      ?.setAttribute("content", theme === "dark" ? "#101f1b" : "#146451");
  };
  apply(chosen || (system.matches ? "dark" : "light"));
  for (const control of controls) {
    control.addEventListener("click", () => {
      chosen = root.dataset.theme === "dark" ? "light" : "dark";
      apply(chosen);
      try {
        localStorage.setItem("pary-theme", chosen);
      } catch {
        /* La elección se conserva durante esta página. */
      }
    });
  }
  system.addEventListener("change", () => {
    if (!chosen) apply(system.matches ? "dark" : "light");
  });
  window.addEventListener("storage", (event) => {
    if (event.key !== "pary-theme" && event.key !== null) return;
    chosen = event.newValue === "light" || event.newValue === "dark" ? event.newValue : null;
    apply(chosen || (system.matches ? "dark" : "light"));
  });
})();
