# Manual procedure: add Anthropic Academy badge

> **Spanish version:** [MANUAL_BADGES_ES.md](MANUAL_BADGES_ES.md)

## When
Every time you complete a course in Anthropic Academy.

## Steps

### 1. Get badge data
- Course title (exact as it appears in Anthropic Academy)
- Verification URL (e.g., `https://verify.skilljar.com/c/...`)
- Obtained date (format YYYY-MM-DD)

### 2. Prepare the image
- Download the certificate/badge image
- Optimize with sharp or Gimp:
  - Size: 600px wide
  - Format: JPG, quality 80%
  - Name: `anthropic-{course-name}-opt.jpg` (lowercase, hyphens)
- Save in `static/images/`

### 3. Add entry to JSON
Edit `data/anthropic_badges.json` and add at the **start** of the array:

```json
{
  "titulo": "Course Name",
  "img": "/images/anthropic-course-name-opt.jpg",
  "fecha": "2026-04-01",
  "url": "https://verify.skilljar.com/c/XXXXX",
  "desc": "Short 1-2 line description of what you learn in the course.",
  "desc_en": "Short 1-2 line description of what the course teaches."
}
```

> **Important (bilingual site es/en):** the `desc_en` field is mandatory.
> The site renders `desc_en` in the English version and falls back to `desc` if missing,
> so without it the English site would show Spanish text.
> The `categoria` field that may appear in old entries is optional and not
> rendered — it can be omitted.

### 4. Verify and deploy
```bash
hugo server              # check at localhost
hugo --cleanDestinationDir
firebase deploy --only hosting
```

### 5. Commit
```bash
git add data/anthropic_badges.json static/images/anthropic-*
git commit -m "add anthropic badge: Course Name"
git push
```

## Notes
- Keep only the 6 most recent badges in the JSON
- If there are more than 6, delete the oldest ones from the end of the array
- The `desc` (Spanish) and `desc_en` (English) fields are own summaries, not AI-generated
- Local images go in `static/images/`, not external URLs
