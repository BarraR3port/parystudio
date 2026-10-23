// La navegación y el contacto funcionan sin JavaScript. Solo una pregunta abierta a la vez.
for (const item of document.querySelectorAll(".faq details")) {
  item.addEventListener("toggle", () => {
    if (item.open)
      for (const other of document.querySelectorAll(".faq details"))
        if (other !== item) other.open = false;
  });
}
