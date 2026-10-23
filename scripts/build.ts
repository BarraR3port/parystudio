import { cp, mkdir, rm, readdir, readFile } from "node:fs/promises";
import { join } from "node:path";
await rm("dist", { recursive: true, force: true });
await mkdir("dist/public", { recursive: true });
await cp("public", "dist/public", { recursive: true });
await rm("dist/public/assets/admin.css", { force: true });
async function check(dir: string) {
  for (const f of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, f.name);
    if (f.isDirectory()) await check(p);
    else if (/\.(html|css|js|json|txt|xml|svg)$/.test(p)) {
      const text = await readFile(p, "utf8");
      if (
        /gmail_id|SENT verificado|content_sha256|ADMIN_PASSWORD_HASH|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY/.test(
          text,
        )
      )
        throw Error("Contenido privado en build: " + p);
    }
  }
}
await check("dist/public");
console.log("Build público generado y verificado; solo recursos públicos.");
