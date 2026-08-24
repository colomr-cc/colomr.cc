# CLAUDE.md — Contexto del proyecto colomr.cc

## Qué es este proyecto
Sitio web personal generado con **Hugo** y desplegado en **Firebase Hosting**.
Muestra badges/certificaciones de Google Cloud Skills Boost y Anthropic Academy.
Rama principal: **`main`**. Tema colomr-v1 en producción.

## 🚦 Flujo E2E obligatorio (MANDATORY)

**Todo cambio en este repo sigue este flujo, sin excepciones.** Leer y aplicar desde el inicio de cada sesión.

```
💡 Idea (sin Specs/ADR — excepción consciente: proyecto personal, bajo riesgo)
   → rama feature (nunca push directo a main)
   → cambio atómico (+ UT solo si se toca lógica; hoy solo hay lógica en scripts/sync_badges.py)
   → Claude verifica los checks en local, commitea (avisando antes), hace push y CREA EL PR
   → Claude pasa la URL del PR al owner — y AHÍ SE DETIENE
       ├─ CI · ci.yml         → ci-hugo.yml (build) + ci-python.yml (ruff/pytest) + badges schema + sonar-scan.yml (CI-based Quality Gate)
       ├─ CI · deploy.yml     → build Hugo (smoke test) + preview Firebase (URL en el PR)
       ├─ Org ruleset         → no-ai-attribution.yml (required workflow, org-wide, no vive en este ci.yml)
       └─ 🚦 Branch protection: todos los checks en verde son obligatorios
   → HITL: el usuario revisa la preview de Firebase + checks → aprueba
   → merge (la rama feature se borra automáticamente)
   → main → deploy automático a producción (CD via deploy.yml)
```

Reglas derivadas:
- **UT solo donde hay lógica.** Si se modifica `scripts/sync_badges.py`, actualizar/añadir tests en `tests/`. Contenido, SCSS y plantillas no llevan tests: los cubren el build de Hugo, los schemas y Sonar.
- **Schemas JSON.** Si cambia la estructura de `data/*.json`, actualizar `schemas/badges.schema.json` en el mismo PR.
- **Regla Gatekeeper:** rige la regla 6 del contrato global (`~/.claude/CLAUDE.md`, repo `claude-sync`).
  Concreción en este repo: lo que el owner revisa antes de aprobar es la preview de Firebase + el diff + los checks.
- **Nunca mergear con checks en rojo** ni pedir saltarse la branch protection.

## Estructura clave
- `hugo.toml` — configuración Hugo
- `data/badges.json` — 6 últimos badges Google Cloud Skills Boost
- `data/anthropic_badges.json` — badges Anthropic Academy (manual)
- `scripts/sync_badges.py` — sincronización automática de badges Google
- `scripts/MANUAL_BADGES.md` — procedimiento manual para badges Anthropic
- `.github/workflows/sync-badges.yml` — sync semanal (lunes 8:00 UTC)
- `themes/colomr-v1/` — submódulo git → https://github.com/colomr-cc/colomr-v1-theme
  El tema tiene su propio repo, CI y branch protection: los cambios se hacen allí por PR
  y aquí solo se actualiza el puntero del submódulo (también por PR).
- `layouts/` — overrides personales (footer, iconos gemini/claude)
- `content/*/index.md` — Page Bundles, contenido en front matter YAML

## Tema colomr-v1
Tema propio Material Design 3, diseñado con Google Stitch 2. Licencia GPL-3.0.
Es un submódulo git con repo propio, CI y branch protection: los cambios se hacen allí por PR y
aquí solo se actualiza el puntero del submódulo, también por PR.

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
      - icon: "fa-brands fa-linkedin-in"  # Font Awesome 7
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
3. Genera descripciones (español e inglés) via Gemini API
4. Si hay cambios: crea una rama y **abre un PR** con revisión solicitada al owner
5. El owner revisa las descripciones en la preview y mergea → `deploy.yml` publica

Usa el token de la GitHub App `colomr-cc-automation` (variable `APP_CLIENT_ID` y secret
`AUTOMATION_APP_PRIVATE_KEY`): caduca en 1 hora y, a diferencia de `GITHUB_TOKEN`, sí
dispara los checks obligatorios sobre el PR.

### Gemini API
`select_models()` consulta a la API qué modelos ofrece la clave y los ordena por familia
(flash-lite primero, luego flash; versión más reciente antes). No hay lista fija: jubilar
un modelo no rompe el script. Si todos fallan, el error incluye los modelos probados y el
mensaje literal de Google.

### Badges Anthropic (manual)
Procedimiento documentado en `scripts/MANUAL_BADGES.md`.
Mantener solo 6 badges. Imágenes locales optimizadas en `static/images/`.

## Comandos útiles
```bash
# Hugo local y CI van a la misma versión (0.164.0). Al subirla en deploy.yml, subir también aquí:
#   curl -sL https://github.com/gohugoio/hugo/releases/download/v0.164.0/hugo_extended_0.164.0_linux-amd64.deb -o /tmp/hugo.deb && sudo apt install -y /tmp/hugo.deb

hugo server                          # desarrollo local (puerto 1313)
hugo --cleanDestinationDir           # build producción
firebase deploy --only hosting       # deploy a Firebase
python scripts/sync_badges.py        # sync manual (requiere GOOGLE_API_KEY)
git -c commit.gpgsign=false commit   # commit sin GPG

# Regenerar lock de dependencias CI (tras cambiar requirements-dev.txt o scripts/requirements.txt)
uv pip compile --generate-hashes --python-version 3.12 requirements-dev.txt scripts/requirements.txt -o requirements-ci.lock

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

### Autoría y estilo de commits/PRs
La autoría y la prohibición de atribución de IA las fija la regla 5 del contrato global
(`~/.claude/CLAUDE.md`, repo `claude-sync`); el idioma del contenido público, la regla 8.
Aquí solo lo específico de este repo:

- **Enforcement de máquina**: `no-ai-attribution.yml`, required workflow a nivel de org (`maiwei-app`, ruleset "Protect default branch"), falla el PR si detecta cualquier cuño de IA en autores, mensajes de commit, título o cuerpo del PR. No vive como step local en el `ci.yml` de este repo.
- **Mensaje de commit**: [Conventional Commits](https://www.conventionalcommits.org/) — `type: subject`, una sola línea, en minúsculas, **en inglés**, descriptiva y concisa. Sin body salvo que aporte algo imprescindible. `type` es uno de `feat|fix|docs|perf|refactor|chore|style|test|ci` (ver `changelog-sections` en `.release-please-config.json`). Enforcement de máquina: job `commitlint` de `ci-python.yml`. Ejemplos: `feat: add dev.to link to the footer`, `chore: upgrade font awesome to 7 across the site`.
- **Cuerpo del PR**: breve — una o dos frases, en inglés. No incluir plan de prueba manual; la URL de preview de Firebase llega automáticamente al PR y sirve para revisar.
- **Qué NO se traduce**: el contenido del sitio es bilingüe es/en por diseño (`content/*/index.es.md` y `.en.md`), y este `CLAUDE.md` y las sesiones siguen en español. El inglés aplica a lo que se publica en GitHub.

## Tareas pendientes
1. ⏳ Optimizar imágenes de cover a local (WebP 1920x1080, `static/images/covers/`)
2. ⏳ Imágenes definitivas con "alma" para las páginas
3. ⏳ PR #693 Hugo Themes — esperando revisión
