#!/usr/bin/env python3
"""
Sincroniza los 6 badges más recientes desde el perfil público de Google Cloud Skills Boost.

Detecta badges nuevos comparando con data/badges.json,
genera una descripción en español via Gemini API,
y guarda solo los 6 más recientes.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from google import genai

PROFILE_URL = "https://www.skills.google/public_profiles/36fdb0e1-891c-4dc5-aef1-d89aecc3dd45"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BADGES_JSON = PROJECT_ROOT / "data" / "badges.json"
MAX_BADGES = 6


def fetch_profile_badges() -> list[dict]:
    """Scrape badges from the public Google Skills profile."""
    resp = requests.get(PROFILE_URL, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    badges = []

    for badge_div in soup.select("div.profile-badge"):
        link = badge_div.select_one("a.badge-image")
        img = badge_div.select_one("a.badge-image img")
        title_span = badge_div.select_one("span.ql-title-medium")
        date_span = badge_div.select_one("span.ql-body-medium")

        if link is None or img is None or title_span is None or date_span is None:
            continue

        url = link["href"]
        img_src = img["src"]
        titulo = title_span.get_text(strip=True)
        date_text = date_span.get_text(strip=True)

        fecha = parse_date(date_text)
        if fecha is None:
            continue

        badges.append({
            "titulo": titulo,
            "img": img_src,
            "fecha": fecha,
            "url": url,
        })

    if len(badges) == 0:
        raise RuntimeError(
            f"Scraping devolvió 0 badges desde {PROFILE_URL}. "
            "Probablemente Google cambió el HTML del perfil — revisar selectores CSS."
        )

    return badges


def parse_date(text: str) -> str | None:
    """Parse 'Earned Feb 13, 2026 EST' to '2026-02-13'."""
    match = re.match(r"Earned\s+([A-Za-z]{3}\s+\d{1,2},\s+\d{4})\s+\S+$", text)
    if not match:
        return None
    cleaned = " ".join(match.group(1).split())
    try:
        dt = datetime.strptime(cleaned, "%b %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None


def load_existing_badges() -> list[dict]:
    """Load current badges.json."""
    if not BADGES_JSON.exists():
        return []
    with open(BADGES_JSON, encoding="utf-8") as f:
        return json.load(f)


def find_new_badges(profile_badges: list[dict], existing_badges: list[dict]) -> list[dict]:
    """Find badges from profile not already in badges.json (matched by URL)."""
    existing_urls = {b["url"] for b in existing_badges}
    return [b for b in profile_badges if b["url"] not in existing_urls]


def _call_gemini(prompt: str) -> str:
    """Call Gemini API with automatic model fallback. Returns raw response text."""
    client = genai.Client()
    models_to_try = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash-lite"]
    response = None
    for model in models_to_try:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            break
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "503" in str(e) or "UNAVAILABLE" in str(e):
                print(f"  -> Model {model} unavailable, trying next...")
                continue
            raise
    if response is None:
        raise RuntimeError("All Gemini models exhausted their quota.")

    response_text = response.text.strip()
    if response_text.startswith("```"):
        response_text = response_text.removeprefix("```json").removeprefix("```").strip()
        response_text = response_text.removesuffix("```").strip()
    return response_text


def generate_descriptions(badges: list[dict]) -> list[dict]:
    """Use Gemini API to generate Spanish and English descriptions for new badges."""
    badges_list = "\n".join(f'{i+1}. "{b["titulo"]}"' for i, b in enumerate(badges))

    prompt = f"""Para cada badge/certificación de Google Cloud, genera una descripción
en español y otra en inglés (1-2 frases cada una) sobre qué se aprende. Estilo profesional y conciso.

Badges:
{badges_list}

Responde SOLO con un JSON array de objetos (sin markdown), cada objeto con "desc" (español) y "desc_en" (inglés), en el mismo orden."""

    response_text = _call_gemini(prompt)
    return json.loads(response_text)


def merge_badges(latest_badges: list[dict], existing_badges: list[dict], new_badges: list[dict]) -> list[dict]:
    """Build the final list: keep existing entries (with descriptions) and fill gaps with new badges."""
    existing_by_url = {b["url"]: b for b in existing_badges}
    new_by_url = {b["url"]: b for b in new_badges}
    final_badges = []
    for badge in latest_badges:
        merged = existing_by_url.get(badge["url"]) or new_by_url.get(badge["url"])
        if merged is not None:
            final_badges.append(merged)
    return final_badges


def write_github_output(new_badges: list[dict]) -> None:
    """Expose results to GitHub Actions via GITHUB_OUTPUT, or print locally."""
    names = ", ".join(b["titulo"] for b in new_badges)
    output_file = os.environ.get("GITHUB_OUTPUT")
    if not output_file:
        print(f"\nNew badges: {names}")
        return
    with open(output_file, "a") as f:
        f.write("new_badges=true\n")
        f.write(f"badge_count={len(new_badges)}\n")
        if len(new_badges) == 1:
            f.write(f"commit_msg=añadido nuevo badge {new_badges[0]['titulo']}\n")
        else:
            f.write(f"commit_msg=añadidos {len(new_badges)} nuevos badges: {names}\n")


def save_badges(badges: list[dict]) -> None:
    """Save badges to badges.json."""
    with open(BADGES_JSON, "w", encoding="utf-8") as f:
        json.dump(badges, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    print("Fetching profile badges...")
    profile_badges = fetch_profile_badges()
    print(f"Found {len(profile_badges)} badges on profile.")

    # Sort by date (newest first) and take only the 6 most recent
    profile_badges.sort(key=lambda b: b["fecha"], reverse=True)
    latest_badges = profile_badges[:MAX_BADGES]
    print(f"Keeping {len(latest_badges)} most recent badges.")

    existing_badges = load_existing_badges()
    print(f"Existing badges in JSON: {len(existing_badges)}")

    new_badges = find_new_badges(latest_badges, existing_badges)

    if not new_badges:
        print("No new badges in the top 6. Nothing to do.")
        sys.exit(0)

    print(f"Found {len(new_badges)} new badge(s):")
    for b in new_badges:
        print(f"  - {b['titulo']} ({b['fecha']})")

    # Generate descriptions for new badges
    print(f"Generating descriptions for {len(new_badges)} badge(s)...")
    descriptions = generate_descriptions(new_badges)

    for badge, desc_pair in zip(new_badges, descriptions, strict=True):
        badge["desc"] = desc_pair["desc"]
        badge["desc_en"] = desc_pair["desc_en"]

    final_badges = merge_badges(latest_badges, existing_badges, new_badges)
    save_badges(final_badges)
    print(f"Saved {len(final_badges)} badges to badges.json.")

    write_github_output(new_badges)


if __name__ == "__main__":
    main()
