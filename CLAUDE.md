# CLAUDE.md — Contexto del proyecto colomr.cc

## Qué es este proyecto
Sitio web personal generado con **Hugo** y desplegado en **Firebase Hosting**.
Muestra badges/certificaciones de Google Cloud Skills Boost y Anthropic Academy.
Rama principal: **`main`**. Tema colomr-v1 en producción.

## Estructura clave
- `hugo.toml` — configuración Hugo
- `data/badges.json` — 6 últimos badges Google Cloud Skills Boost
- `data/anthropic_badges.json` — badges Anthropic Academy (manual)
- `scripts/sync_badges.py` — sincronización automática de badges Google
- `scripts/MANUAL_BADGES.md` — procedimiento manual para badges Anthropic
- `.github/workflows/sync-badges.yml` — sync semanal (lunes 8:00 UTC)
- `.github/workflows/sync-theme.yml` — sincroniza tema al repo público (pendiente PAT)
- `themes/colomr-v1/` — submódulo git → https://github.com/colomr-dev/colomr-v1-theme
- `layouts/` — overrides personales (footer, iconos gemini/claude)
- `content/*/index.md` — Page Bundles, contenido en front matter YAML

## Tema colomr-v1
Tema propio Material Design 3, diseñado con Google Stitch 2. Licencia GPL-3.0.
Es un submódulo git — los cambios al tema se hacen dentro del submódulo y se sincronizan al repo público.

### Páginas
| URL | Archivo | Layout | Estado |
|-----|---------|--------|--------|
| `/` | `content/_index.md` | `index.html` | ✅ Completa |
| `/sobre-mi/` | `content/quien/index.md` | `blocks.html` | ✅ Completa |
| `/formacion/` | `content/que/index.md` | `providers.html` | ✅ Completa |
| `/vision/` | `content/donde/index.md` | `blocks.html` | ✅ Completa |

### Estructura del tema
```
themes/colomr-v1/              (submódulo → colomr-v1-theme)
├── assets/
│   ├── scss/
│   │   ├── main.scss          — importa todo
│   │   ├── _tokens.scss       — variables MD3 (colores, fuentes, spacing)
│   │   ├── _components.scss   — header, nav, botones, chips
│   │   ├── _home.scss         — hero + secciones home + efectos cover
│   │   ├── _page.scss         — páginas interiores (bloques)
│   │   └── _formacion.scss    — tabs pill + badge grid
│   └── js/main.js             — dark/light toggle, tabs, hamburger
├── layouts/
│   ├── _default/
│   │   ├── baseof.html        — base (head, header, footer, GitHub corner)
│   │   ├── blocks.html        — sistema de bloques Notion-style
│   │   ├── providers.html     — tabs de providers + badges
│   │   └── single.html        — fallback genérico
│   ├── index.html             — home page
│   └── partials/
│       ├── head/              — meta, fonts, styles, analytics
│       ├── header.html        — nav desktop + drawer + bottom nav
│       ├── footer.html        — social links + credits
│       └── scripts.html       — JS loader
├── exampleSite/               — contenido demo para galería Hugo Themes
├── images/                    — screenshot.png y tn.png
├── LICENSE                    — GPL-3.0
├── README.md                  — documentación completa del tema
└── theme.toml
```

### Overrides personales (en raíz, fuera del tema)
```
layouts/
├── partials/
│   ├── footer.html            — footer con enlace a colomr-v1
│   └── icons/
│       ├── gemini.html        — logo Gemini (learning cards)
│       └── claude.html        — logo Claude (learning cards)
```

### Sistema de bloques (blocks.html)
```yaml
blocks:
  - type: "text"
    heading: "Título"
    body: "Texto..."
  - type: "cards"
    heading: "Título"
    items:
      - icon: "cloud"          # Material Symbol
        title: "Título card"
        body: "Texto"
  - type: "timeline"
    heading: "Título"
    items:
      - role: "Rol"
        company: "Empresa"
        period: "Fecha"
  - type: "contact"
    heading: "Título"
    body: "Texto introductorio"
    items:
      - icon: "fa fa-linkedin"  # Font Awesome 4.7
        label: "Texto"
        url: "https://..."
```

### Imágenes de cabecera (cover)
- Tamaño recomendado: **1920x1080 (16:9)**, formato WebP, calidad 80%
- Parámetros configurables en front matter:
  - `cover` — URL de la imagen
  - `cover_position` — CSS background-position (default: `center center`)
  - `cover_opacity` — opacidad del overlay 0-1 (default: 0.5 interiores, 0.65 home)
  - `cover_ratio` — aspect ratio del contenedor (default: `3 / 1`, opciones: `16 / 9`, `4 / 1`)
  - `cover_effect` — solo home: `glass` | `vignette` | `shadow` | `highlight`
- Overlay adaptativo: negro en dark mode, blanco en light mode

### Providers de Formación (providers.html)
```yaml
providers:
  - id: "google"
    name: "Google Cloud Skills Boost"
    profile_url: "https://..."    # omitir para ocultar botón
    profile_label: "Ver mi perfil"
    data: "badges"                # → data/badges.json
  - id: "anthropic"
    name: "Anthropic Academy"
    data: "anthropic_badges"      # → data/anthropic_badges.json
```
Muestra los **6 badges más recientes** de cada provider. Tabs estilo pill con logos.

### Navegación
- Configurada en `hugo.toml` → `[[params.nav_links]]`
- Iconos de Material Symbols, configurables con `nav_icon`
- Se renderiza en desktop nav, drawer móvil y bottom nav

### GitHub Corner
- Activo por defecto apuntando al repo del tema
- Desactivar con `github_corner = "false"` en `hugo.toml`

## Workflow de sincronización de badges
Se ejecuta cada lunes (cron `0 8 * * 1`) o manualmente:
1. Scrapa los 6 badges más recientes del perfil Google Skills
2. Detecta nuevos comparando por URL con `data/badges.json`
3. Genera descripción en español via Gemini API
4. Si hay cambios: build Hugo + deploy Firebase + commit al repo

### Gemini API
```python
models_to_try = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash-lite"]
```
Fallback automático si un modelo tiene cuota agotada.

### Badges Anthropic (manual)
Procedimiento documentado en `scripts/MANUAL_BADGES.md`.
Mantener solo 6 badges. Imágenes locales optimizadas en `static/images/`.

## Comandos útiles
```bash
hugo server                          # desarrollo local (puerto 1313)
hugo --cleanDestinationDir           # build producción
firebase deploy --only hosting       # deploy a Firebase
python scripts/sync_badges.py        # sync manual (requiere GOOGLE_API_KEY)
git -c commit.gpgsign=false commit   # commit sin GPG

# ExampleSite del tema
hugo server --source themes/colomr-v1/exampleSite --themesDir ../..
```

## Versionado (SemVer)
Usamos **Semantic Versioning** (`MAJOR.MINOR.PATCH`):
- **MAJOR** — breaking changes, reescrituras (v1→v2)
- **MINOR** — nuevas funcionalidades compatibles (nuevo bloque, efecto, etc.)
- **PATCH** — bug fixes, ajustes visuales

Versión actual: **v2.0.0** (tema colomr-v1, MD3, deploy automático).
Se marca con `git tag` + GitHub Release en cada versión.

## Preferencias de workflow con Claude
- Siempre trabajar en **feature branches** con **PRs** contra main. Nunca push directo a main.
- Push a main dispara deploy automático (no hace falta `hugo` ni `firebase deploy` en local)
- Avisar antes de hacer commit con una frase breve
- Imágenes: el usuario las elige y pasa la URL — Claude no las busca solo
- Paso a paso con aprobación del usuario para cambios estructurales

## Tareas pendientes
1. ⏳ Optimizar imágenes de cover a local (WebP 1920x1080, `static/images/covers/`)
2. ⏳ Imágenes definitivas con "alma" para las páginas
3. ⏳ PR #693 Hugo Themes — esperando revisión, configurar PAT y flujo sync cuando aprueben
