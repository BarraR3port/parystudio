// Se ejecuta antes del CSS para evitar un destello claro al abrir el tema oscuro.
(() => {
  let saved;
  try {
    saved = localStorage.getItem("pary-theme");
  } catch {
    /* El tema funciona sin almacenamiento. */
  }
  const dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  document.documentElement.dataset.theme =
    saved === "dark" || saved === "light" ? saved : dark ? "dark" : "light";
})();
