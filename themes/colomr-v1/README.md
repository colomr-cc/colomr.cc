# colomr-v1

Tema Hugo para [colomr.pm](https://colomr.pm). Material Design 3, modo claro/oscuro nativo, sistema de bloques tipo Notion para páginas interiores.

---

## Requisitos

- Hugo Extended `>= 0.120.0`
- Fuentes externas: Google Fonts (Plus Jakarta Sans + Inter + Material Symbols)

---

## Dónde se gestiona cada cosa

| Pregunta | Respuesta | Fichero(s) |
|----------|-----------|------------|
| Datos globales del sitio (título, autor, analytics, social links) | `config.toml` → `[params]` | `config.toml` |
| Datos de una página concreta (título, bloques, cover) | Front matter del `index.md` | `content/*/index.md` |
| Texto narrativo libre | Body del markdown (debajo del front matter) | `content/*/index.md` |
| Datos estructurados reutilizables (badges, categorías) | Data files | `data/*.json` |
| Assets globales (logos, favicons, avatar) | Carpeta static | `static/images/` |
| Assets de una página concreta | Page Bundle (junto al `index.md`) | `content/*/` |
| Estilos visuales y layout | Tema | `themes/colomr-v1/` |
| Overrides de layout específicos del sitio | Root layouts | `layouts/` |

---

## Estructura del proyecto

```
colomr.pm/
├── config.toml                    # Solo configuración global del sitio
├── content/
│   ├── _index.md                  # Home — datos del hero, learning, context
│   ├── quien/
│   │   └── index.md               # Page Bundle — front matter con bloques
│   ├── donde/
│   │   └── index.md               # Page Bundle
│   ├── que/
│   │   └── index.md               # Page Bundle
│   └── badges/
│       └── index.md               # Page Bundle — type: badges
├── data/
│   ├── badges.json                # Badges de Google Cloud Skills Boost
│   └── categorias.json            # Categorías con icono y color
├── static/images/                 # Assets globales (avatar, logos, favicons)
├── layouts/                       # Overrides raíz (se eliminarán al completar el tema)
│   ├── badges/single.html         # Entry point → partial badges.html
│   └── partials/
│       ├── badges.html            # Grid de badges con filtros y paginación
│       ├── header.html            # Nav, drawer móvil, bottom nav
│       └── footer.html            # Footer con social links
└── themes/colomr-v1/              # EL TEMA
    ├── assets/
    │   ├── scss/
    │   │   ├── main.scss          # Entry point — importa el resto
    │   │   ├── _tokens.scss       # Design tokens MD3 (colores, tipografía, spacing)
    │   │   ├── _components.scss   # Header, footer, nav, botones, chips
    │   │   ├── _home.scss         # Estilos del Home
    │   │   └── _page.scss         # Estilos de páginas interiores
    │   └── js/
    │       ├── main.js            # Toggle dark/light + drawer móvil
    │       └── badges.js          # Filtros, paginación y scroll-to-top de badges
    ├── layouts/
    │   ├── index.html             # Home — lee de content/_index.md front matter
    │   ├── _default/
    │   │   ├── baseof.html        # Plantilla base (head, header, main, footer)
    │   │   ├── page.html          # Páginas interiores — lee bloques del front matter
    │   │   └── single.html        # Fallback genérico — renderiza .Content
    │   └── partials/
    │       ├── header.html        # Nav + drawer móvil + bottom nav
    │       ├── footer.html        # Footer con créditos
    │       ├── scripts.html       # JS compilado con fingerprint
    │       ├── icons/
    │       │   ├── google-cloud.html
    │       │   └── anthropic.html
    │       └── head/
    │           ├── meta.html      # SEO, favicons
    │           ├── fonts.html     # Google Fonts
    │           ├── styles.html    # SCSS compilado con fingerprint
    │           └── analytics.html # GA4 (solo en producción)
    └── theme.toml
```

---

## Convención Hugo que seguimos

```
config.toml      →  configuración global, [params], [menus], taxonomías
front matter     →  datos de cada página (bloques, cover, icon, subtitle...)
body markdown    →  contenido narrativo (renderizado con {{ .Content }})
data/*.json      →  datos estructurados reutilizables
Page Bundles     →  cada página es una carpeta con index.md (content/*/index.md)
partials         →  trozos reutilizables de layout
assets/          →  SCSS y JS procesados por Hugo Pipes (minify + fingerprint)
static/          →  solo assets globales (logos, favicons)
```

---

## Páginas interiores — sistema de bloques

Las páginas interiores usan `layout: "page"` y definen su contenido en el **front matter YAML** del `index.md`, no en `config.toml`.

### Crear una página nueva

**1. Crear el Page Bundle:**

```bash
mkdir content/mi-pagina
```

**2. Crear `content/mi-pagina/index.md`:**

```yaml
---
title: "Mi Página"
description: "Descripción para SEO"
url: "/mi-pagina/"
layout: "page"

cover: "/images/mi-cover.jpg"
icon: "🚀"
pageTitle: "Título visible en la página"
subtitle: "Una línea descriptiva"

tags_list:
  - label: "Tag 1"
  - label: "Tag 2"

blocks:
  - type: "text"
    heading: "Sección de texto"
    body: "Contenido del párrafo."

  - type: "cards"
    heading: "Tarjetas"
    items:
      - icon: "architecture"
        title: "Card 1"
        body: "Descripción"

  - type: "timeline"
    heading: "Trayectoria"
    items:
      - role: "Cargo"
        company: "Empresa"
        period: "2021 – presente"

  - type: "contact"
    heading: "Contacto"
    items:
      - label: "LinkedIn"
        url: "https://linkedin.com/in/..."
        icon: "fa fa-linkedin"
---
```

**3. (Opcional) Colocar assets junto al `index.md`:**

```
content/mi-pagina/
├── index.md
├── cover.jpg      # asset local del Page Bundle
└── diagram.png
```

Accesibles en el template con `{{ .Resources.GetMatch "cover.*" }}`.

---

### Tipos de bloque disponibles

#### `text` — Párrafo de texto

```yaml
- type: "text"
  heading: "Sobre mí"       # opcional
  body: "Texto del párrafo"
```

#### `cards` — Tarjetas en grid (1–3 columnas según pantalla)

```yaml
- type: "cards"
  heading: "En qué destaco"  # opcional
  items:
    - icon: "architecture"    # nombre de Material Symbol
      title: "Título"
      body: "Descripción breve"
```

#### `timeline` — Línea de tiempo

```yaml
- type: "timeline"
  heading: "Trayectoria"
  items:
    - role: "Cargo o título"
      company: "Empresa"
      period: "2021 – presente"
```

#### `contact` — Links de contacto

```yaml
- type: "contact"
  heading: "Encuéntrame en"
  items:
    - label: "LinkedIn"
      url: "https://linkedin.com/in/..."
      icon: "fa fa-linkedin"
```

### Añadir un nuevo tipo de bloque

1. Añadir `{{ else if eq .type "nuevo" }}` en `themes/colomr-v1/layouts/_default/page.html`
2. Añadir estilos en `themes/colomr-v1/assets/scss/_page.scss`
3. Documentar el schema YAML en este README

---

## Home page

El contenido del home se gestiona desde `content/_index.md`. El front matter define tres secciones:

```yaml
hero:
  chips: ["GOOGLE CLOUD", "ANTHROPIC"]
  title: "Texto antes del "
  titleHighlight: "gradiente"
  subtitle: "Subtítulo"
  subtitleEmphasis: "texto en cursiva"
  subtitleEmoji: "🤖"
  ctas:
    - label: "CTA primario"
      url: "/quien/"
      style: "primary"
    - label: "CTA secundario"
      url: "/donde/"
      style: "ghost"

learning:
  title: "Aprendizaje Continuo"
  subtitle: "Subtítulo"
  cards:
    - name: "Google"
      desc: "Descripción"
      url: "/que/"
      icon: "google-cloud"        # partial en partials/icons/
      cssModifier: ""
    - name: "Anthropic"
      desc: "Descripción"
      url: "/que/"
      icon: "anthropic"
      cssModifier: "learning-card--anthropic"

context:
  heading: "Título"
  body: "Texto"
  icon: "architecture"            # Material Symbol
  stat: "20+"
  statLabel: "LABEL"
```

Los SVG de las learning cards se gestionan como **partials** en `themes/colomr-v1/layouts/partials/icons/`. Para añadir uno nuevo, crear el fichero `.html` con el SVG y referenciarlo por nombre en el campo `icon`.

---

## Badges

La página de badges (`content/badges/index.md`) usa `type: "badges"` y se alimenta de:

- `data/badges.json` — array de badges (título, imagen, fecha, URL, descripción, categoría)
- `data/categorias.json` — definiciones de categoría (id, nombre, icono, color)
- Front matter — `pageTitle`, `profileUrl`, `profileLinkText`

El JS de filtros y paginación está en `themes/colomr-v1/assets/js/badges.js`, cargado via Hugo Pipes con minificación y fingerprint.

---

## Diseño y tokens

Los design tokens están en `assets/scss/_tokens.scss` como custom properties CSS:

```scss
var(--color-primary)                // #0058bd
var(--color-surface-container-low)  // fondo de secciones
var(--color-on-surface)             // texto principal
var(--font-display)                 // Plus Jakarta Sans
var(--font-body)                    // Inter
var(--space-6)                      // 1.5rem
var(--radius-xl)                    // 1.5rem
```

El modo oscuro se activa por preferencia del sistema (`prefers-color-scheme`) o manualmente con `data-theme="dark"/"light"` en `<html>`. El toggle llama a `window.__toggleTheme()`.

---

## Iconos

| Sistema | Uso | Sintaxis |
|---------|-----|----------|
| **Material Symbols Outlined** | UI (nav, bloques, cards) | `<span class="material-symbols-outlined">home</span>` |
| **Font Awesome 4** | Social links, contacto | `<i class="fa fa-github"></i>` |

---

## Comandos

```bash
hugo server                  # desarrollo local con live reload
hugo --cleanDestinationDir   # build de producción
```

---

*Tema diseñado con [Stitch](https://stitch.withgoogle.com) e implementado con Claude.*
