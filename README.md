# colomr.cc

Sitio web personal construido con [Hugo](https://gohugo.io/) y desplegado en [Firebase Hosting](https://firebase.google.com/).

Tema propio [colomr-v1](https://github.com/colomr-dev/colomr-v1-theme) basado en Material Design 3.

## Tecnologias

- **Hugo** (Extended) — generador de sitios estáticos
- **Firebase Hosting** — despliegue y CDN
- **colomr-v1** — tema propio MD3 (submódulo git)
- **GitHub Actions** — sincronizacion automática de badges
- **Gemini API** — generación de descripciones de badges

## Estructura

```
colomr.cc/
├── hugo.toml                    # Configuración del sitio
├── content/
│   ├── _index.md                # Home
│   ├── quien/index.md           # /sobre-mi/ (layout: blocks)
│   ├── que/index.md             # /formacion/ (layout: providers)
│   └── donde/index.md           # /vision/ (layout: blocks)
├── data/
│   ├── badges.json              # 6 últimos badges Google Cloud
│   └── anthropic_badges.json    # Badges Anthropic Academy (manual)
├── layouts/                     # Overrides personales
│   └── partials/
│       ├── footer.html
│       └── icons/               # Logos Gemini y Claude
├── scripts/
│   ├── sync_badges.py           # Sync automático Google badges
│   └── MANUAL_BADGES.md         # Procedimiento manual Anthropic
├── static/images/               # Avatar, logos, favicons, badges
├── themes/colomr-v1/            # Submódulo → colomr-v1-theme
└── .github/workflows/
    ├── sync-badges.yml          # Sync semanal de badges Google
    └── sync-theme.yml           # Sync tema al repo público
```

## Desarrollo local

```bash
# Clonar con submódulos
git clone --recurse-submodules https://github.com/colomr-dev/colomr.cc.git

# Servidor local
hugo server

# Build producción
hugo --cleanDestinationDir

# Deploy
firebase deploy --only hosting
```

## Badges

### Google Cloud (automático)
Cada lunes a las 8:00 UTC, GitHub Actions sincroniza los 6 badges más recientes del perfil de Google Cloud Skills Boost. Genera descripciones en español via Gemini API.

Secrets necesarios en GitHub:

| Secret | Descripción |
|---|---|
| `GEMINI_API_KEY` | API key de Google AI Studio |
| `FIREBASE_SERVICE_ACCOUNT` | Service account de Firebase |

### Anthropic Academy (manual)
Procedimiento documentado en [scripts/MANUAL_BADGES.md](scripts/MANUAL_BADGES.md).

## Licencia

El código de este sitio está bajo [MIT License](LICENSE).
El contenido (textos, imágenes, datos personales) es propiedad del autor.
El tema colomr-v1 está bajo [GPL-3.0](https://github.com/colomr-dev/colomr-v1-theme/blob/main/LICENSE).

## Autor

**Francisco Colomer** — [colomr.cc](https://colomr.cc)
