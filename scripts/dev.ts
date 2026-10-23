import { resolve } from "node:path";
const root = resolve("public");
const routes: Record<string, string> = {
  "/": "index.html",
  "/privacidad": "privacidad.html",
  "/proyectos/monophone": "monophone.html",
};
Bun.serve({
  hostname: "127.0.0.1",
  port: 4324,
  async fetch(req) {
    if (!["GET", "HEAD"].includes(req.method))
      return new Response("Método no permitido", { status: 405 });
    let path: string;
    try {
      path = decodeURIComponent(new URL(req.url).pathname);
    } catch {
      return new Response("Ruta inválida", { status: 400 });
    }
    if (path.split("/").some((x) => x.startsWith(".")) || path.includes("\0"))
      return new Response("No encontrado", { status: 404 });
    const file = Bun.file(resolve(root, routes[path] || path.slice(1)));
    if (!file.name?.startsWith(root + "/") || !(await file.exists()))
      return new Response("No encontrado", { status: 404 });
    return new Response(req.method === "HEAD" ? null : file, {
      headers: {
        "Content-Type": file.type,
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
      },
    });
  },
});
console.log("Pary Studio · http://127.0.0.1:4324");
