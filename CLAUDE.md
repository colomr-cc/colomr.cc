# CLAUDE.md — Contexto del proyecto colomr.pm

## Qué es este proyecto
Sitio web personal generado con **Hugo** y desplegado en **Firebase Hosting**.
Muestra badges/certificaciones de Google Cloud Skills Boost y Anthropic Academy.
Rama activa de desarrollo: **`feature/colomr-v1`** (NO mergear a main hasta terminar).

## Estructura clave
- `hugo.toml` — configuración Hugo (convención moderna)
- `data/badges.json` — badges Google Cloud Skills Boost
- `data/anthropic_badges.json` — badges Anthropic Academy (manual por ahora)
- `data/categorias.json` — categorías de badges con icono y color
- `scripts/sync_badges.py` — script de sincronización automática (solo Google por ahora)
- `.github/workflows/sync-badges.yml` — workflow GitHub Actions (pendiente adaptar para Anthropic)
- `themes/colomr-v1/` — tema propio Material Design 3 (EN DESARROLLO)
- `content/*/index.md` — Page Bundles, todo el contenido en front matter YAML

## Tema colomr-v1 — Estado actual
Nuevo tema construido desde cero con Material Design 3. Reemplaza `hugo-coder`.

### Páginas implementadas
| URL | Archivo | Layout | Estado |
|-----|---------|--------|--------|
| `/` | `content/_index.md` | `home.html` | ✅ Completa |
| `/sobre-mi/` | `content/quien/index.md` | `page.html` | ✅ Completa |
| `/formacion/` | `content/que/index.md` | `formacion.html` | ✅ Completa |
| `/vision/` | `content/donde/index.md` | `page.html` | ⏳ Pendiente contenido |

### Estructura del tema
```
themes/colomr-v1/
├── assets/
│   ├── scss/
│   │   ├── main.scss        — importa todo
│   │   ├── _tokens.scss     — variables MD3 (light + dark)
│   │   ├── _components.scss — header, nav, botones, chips
│   │   ├── _home.scss       — página home
│   │   ├── _page.scss       — páginas interiores (ipage-*)
│   │   └── _formacion.scss  — tabs + badge grid
│   └── js/main.js           — hamburger, tabs, dark/light toggle
└── layouts/
    ├── _default/
    │   ├── baseof.html
    │   ├── home.html
    │   ├── page.html        — sistema de bloques Notion-style
    │   └── formacion.html   — tabs de providers + badges
    └── partials/
        ├── head/            — meta, fonts, styles, analytics
        ├── header.html
        ├── footer.html
        └── scripts.html
```

### Sistema de bloques (page.html)
Las páginas interiores usan bloques YAML en front matter:
```yaml
blocks:
  - type: "text"
    heading: "Título"
    body: "Texto..."
  - type: "cards"
    heading: "Título"
    items:
      - icon: "material_symbol"
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
    items:
      - icon: "fa-linkedin"   # Font Awesome 4.7
        label: "Texto"
        url: "https://..."
```

### Imágenes de cabecera (cover)
- Usar imágenes **landscape / 16:9 o más anchas** para que `background-size: cover` funcione bien
- Default `background-position: top center` (CSS var `--cover-pos`)
- Override por página: `cover_position: "right center"` en front matter
- Las imágenes portrait se cortan (comportamiento CSS estándar, no es un bug)

### Providers de Formación
```yaml
providers:
  - id: "google"
    name: "Google Cloud Skills Boost"
    profile_url: "https://www.skills.google/public_profiles/..."
    profile_label: "Ver mi perfil en Google Skills Boost"
    data: "badges"           # → data/badges.json
  - id: "anthropic"
    name: "Anthropic Academy"
    profile_url: "https://verify.skilljar.com/c/46ocuxdgxcvz"
    profile_label: "Ver mi perfil en Anthropic Academy"
    data: "anthropic_badges" # → data/anthropic_badges.json
```
Badge grid: `auto-fill, minmax(280px, 1fr)` — 2 columnas desktop/tablet, 1 móvil.

## Decisiones de diseño tomadas
- **No hay página de listado de badges** — cada provider muestra los 5 últimos + enlace a perfil oficial
- **Imágenes de badges Anthropic**: guardadas local en `static/images/` optimizadas con sharp (node)
  - Original: `anthropic-claude101.jpg` (3300×2550, backup)
  - Optimizada: `anthropic-claude101-opt.jpg` (600×463, 14KB, en uso)
- **Logos Google/Anthropic**: SVG inline en `content/_index.md` con `currentColor` para dark/light
- **Font Awesome 4.7** para iconos de contacto/social; **Material Symbols Outlined** para UI
- **GPG signing desactivado** para commits: `git -c commit.gpgsign=false commit`
- **Imágenes Unsplash**: provisionales, pendiente elegir definitivas con "alma"
  - Formación: `photo-1650735310389-df969edf5e77` (libros, `cover_position: right center`)
  - Sobre mí: pendiente — necesita imagen landscape
  - Visión: pendiente contenido y imagen

## Tareas pendientes (por orden)
1. ⏳ Imagen landscape para `/sobre-mi/` (la actual es portrait, se corta mal)
2. ⏳ Contenido de `/vision/` (bloques YAML)
3. ⏳ Imágenes definitivas con "alma" para las 3 páginas
4. ⏳ Merge `feature/colomr-v1` → `main`
5. ⏳ Adaptar GitHub Actions para sincronizar Anthropic Academy además de Google
6. ⏳ Toggle `enabled: false` para bloques en page.html (aplazado)

## Workflow de sincronización automática (Sync Badges)
El workflow se ejecuta cada 2 días (cron `0 8 */2 * *`) o manualmente:
1. Scrapa el perfil público de Google Skills
2. Detecta badges nuevos por fecha comparando con `data/badges.json`
3. Genera descripción en español y categoría via Gemini API
4. Si hay cambios: build Hugo + deploy Firebase + commit al repo

### Gemini API — modelos y cuota
La API key se pasa como `GOOGLE_API_KEY` (secret `GEMINI_API_KEY` en GitHub Actions).
```python
models_to_try = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash-lite"]
```
- `gemini-2.0-flash` tiene cuota free tier a 0 (error 429)
- `gemini-2.0-flash-lite` es el que funciona actualmente como fallback

## Comandos útiles
```bash
hugo server                          # desarrollo local (puerto 1313)
hugo --cleanDestinationDir           # build producción
python scripts/sync_badges.py        # sync manual (requiere GOOGLE_API_KEY)
git -c commit.gpgsign=false commit   # commit sin GPG (no hay TTY interactiva)
```

## Preferencias de workflow con Claude
- Puede hacer commit y push directamente, pero avisar antes con una frase breve
- No reinventar la rueda: si algo funciona en el tema anterior, copiarlo directamente
- Imágenes: el usuario las elige en Unsplash y pasa la URL — Claude no las busca solo
