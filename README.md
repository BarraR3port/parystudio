# Pary Studio

Sitio público de Pary Studio: ecommerce y sistemas comerciales para empresas chilenas.

## Desarrollo

```sh
bun install --frozen-lockfile
bun run dev
bun run check
bun run build
```

Vista local: http://127.0.0.1:4324. HTML y CSS, fuentes y recursos alojados localmente. Bun prepara el sitio; Nginx sin privilegios sirve los archivos en producción. Sin base de datos ni credenciales en este repositorio.

## Despliegue en Dokploy

- Dockerfile: `deploy/Dockerfile.public`; contexto: `.`.
- Puerto interno: `8080`; comprobación de salud: `/health`.
- Dominio público: `parystudio.com`.
- El contenedor solo incluye la salida pública de `bun run build`.

## Identidad

`brand-kit/` contiene el isotipo, logotipos Pary y Pary Studio y sus firmas, en SVG trazado y PNG transparente. Incluye versiones a color, inversas y monocromáticas; proporciones y usos en `brand-kit/LEEME.md`.

Para regenerar la familia: Python con fontTools y soporte WOFF2, más ImageMagick; ejecutar `python scripts/brand-family.py`.

## Contenido y recursos

El caso Monophone presenta alcance de desarrollo y una captura pública. No publica código privado, información de clientes ni métricas comerciales internas. Los logotipos de terceros identifican herramientas utilizadas y no implican una relación comercial con sus titulares; fuentes en `docs/LOGOTIPOS-TERCEROS.md`. La tipografía incluye su licencia SIL OFL.

La sección de IA describe apoyo complementario con validación humana. Las revisiones periódicas se acuerdan dentro del plan de continuidad.
