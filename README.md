# colomr.cc

> **Spanish version:** [README_ES.md](README_ES.md)

Personal website built with [Hugo](https://gohugo.io/) and deployed on [Firebase Hosting](https://firebase.google.com/).

Custom theme [colomr-v1](https://github.com/colomr-cc/colomr-v1-theme) based on Material Design 3.

## Technologies

- **Hugo** (Extended) — static site generator
- **Firebase Hosting** — deployment and CDN
- **colomr-v1** — custom MD3 theme (git submodule)
- **GitHub Actions** — automatic badge synchronization
- **Gemini API** — badge description generation

## Structure

```
colomr.cc/
├── hugo.toml                    # Site configuration
├── content/
│   ├── _index.md                # Home
│   ├── quien/index.md           # /about-me/ (layout: blocks)
│   ├── que/index.md             # /experience/ (layout: providers)
│   └── donde/index.md           # /vision/ (layout: blocks)
├── data/
│   ├── badges.json              # 6 latest Google Cloud badges
│   └── anthropic_badges.json    # Anthropic Academy badges (manual)
├── layouts/                     # Custom overrides
│   └── partials/
│       ├── footer.html
│       └── icons/               # Gemini and Claude logos
├── scripts/
│   ├── sync_badges.py           # Automatic Google badges sync
│   └── MANUAL_BADGES.md         # Anthropic manual procedure
├── static/images/               # Avatar, logos, favicons, badges
├── themes/colomr-v1/            # Submodule → colomr-v1-theme
└── .github/workflows/
    ├── sync-badges.yml          # Weekly Google badges sync
    └── sync-theme.yml           # Theme sync to public repo
```

## Local Development

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/colomr-cc/colomr.cc.git

# Local server
hugo server

# Production build
hugo --cleanDestinationDir

# Deploy
firebase deploy --only hosting
```

## Badges

### Google Cloud (automatic)
Every Monday at 8:00 UTC, GitHub Actions syncs the 6 latest badges from Google Cloud Skills Boost profile. Generates descriptions in Spanish via Gemini API.

Required secrets on GitHub:

| Secret | Description |
|---|---|
| `GEMINI_API_KEY` | Google AI Studio API key |
| `FIREBASE_SERVICE_ACCOUNT` | Firebase service account |

### Anthropic Academy (manual)
Procedure documented in [scripts/MANUAL_BADGES.md](scripts/MANUAL_BADGES.md).

## License

The code of this site is under [MIT License](LICENSE).
The content (texts, images, personal data) is property of the author.
The colomr-v1 theme is under [GPL-3.0](https://github.com/colomr-cc/colomr-v1-theme/blob/main/LICENSE).

## Author

**Francisco Colomer** — [colomr.cc](https://colomr.cc)
