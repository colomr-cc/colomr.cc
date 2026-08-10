#!/usr/bin/env python3
"""
Syncs the 6 most recent badges from the public Google Cloud Skills Boost profile.

Detects new badges by comparing against data/badges.json,
generates their descriptions via the Gemini API,
and keeps only the 6 most recent ones.
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
MAX_MODELS_TO_TRY = 4  # techo para no encadenar decenas de intentos si la API lista muchos


def extract_badge(badge_div) -> dict | None:
    """Extract a badge from the profile HTML, or None if any field is missing.

    Each element is checked right before it is used: the access sits next to its
    guard, with no compound conditions that would obscure the guarantee.
    """
    link = badge_div.select_one("a.badge-image")
    if link is None:
        return None

    img = badge_div.select_one("a.badge-image img")
    if img is None:
        return None

    title_span = badge_div.select_one("span.ql-title-medium")
    if title_span is None:
        return None

    date_span = badge_div.select_one("span.ql-body-medium")
    if date_span is None:
        return None

    fecha = parse_date(date_span.get_text(strip=True))
    if fecha is None:
        return None

    return {
        "titulo": title_span.get_text(strip=True),
        "img": img["src"],
        "fecha": fecha,
        "url": link["href"],
    }


def fetch_profile_badges() -> list[dict]:
    """Scrape badges from the public Google Skills profile."""
    resp = requests.get(PROFILE_URL, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    badges = []

    for badge_div in soup.select("div.profile-badge"):
        badge = extract_badge(badge_div)
        if badge is not None:
            badges.append(badge)

    if len(badges) == 0:
        raise RuntimeError(
            f"Scraping returned 0 badges from {PROFILE_URL}. "
            "Google probably changed the profile HTML — check the CSS selectors."
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


def select_models(available: list[str]) -> list[str]:
    """Sort the available models by preference for this task.

    Writing two sentences about a badge needs no advanced reasoning: the cheapest and
    fastest family (flash-lite) comes first, then flash. Families that do not apply and
    unstable variants are discarded. The preference is by FAMILY, not by a specific
    version, so retiring a model does not break the script.
    """
    descartadas = ("embedding", "vision", "image", "audio", "tts", "preview", "exp")
    candidatos = [m for m in available if not any(d in m for d in descartadas)]

    elegidos: list[str] = []
    for familia in ("flash-lite", "flash"):
        # Descending order: among versions of the same family, the most recent first
        for modelo in sorted(candidatos, reverse=True):
            if familia in modelo and modelo not in elegidos:
                elegidos.append(modelo)
    return elegidos[:MAX_MODELS_TO_TRY]


def clean_json_response(text: str) -> str:
    """Quita los fences de markdown con los que el modelo a veces envuelve el JSON."""
    limpio = text.strip()
    if limpio.startswith("```"):
        limpio = limpio.removeprefix("```json").removeprefix("```").strip()
        limpio = limpio.removesuffix("```").strip()
    return limpio


def _available_models(client) -> list[str]:
    """Modelos que la API ofrece a esta clave y sirven para generar contenido."""
    nombres = []
    for modelo in client.models.list():
        acciones = modelo.supported_actions or []
        if "generateContent" in acciones:
            nombres.append(modelo.name.removeprefix("models/"))
    return nombres


def _call_gemini(prompt: str) -> str:
    """Llama a Gemini probando los modelos disponibles por orden de preferencia."""
    client = genai.Client()

    disponibles = _available_models(client)
    modelos = select_models(disponibles)
    if not modelos:
        raise RuntimeError(
            "No compatible model for this key. "
            f"The API offered: {', '.join(disponibles) or '(none)'}"
        )
    print(f"  Models to try: {', '.join(modelos)}")

    ultimo_error = None
    for modelo in modelos:
        try:
            response = client.models.generate_content(model=modelo, contents=prompt)
        except Exception as e:  # noqa: BLE001 — it is logged and the next one is tried
            ultimo_error = e
            print(f"  -> {modelo} failed: {e}")
            continue
        print(f"  -> description generated with {modelo}")
        return clean_json_response(response.text)

    raise RuntimeError(
        f"No model responded. Tried: {', '.join(modelos)}. Last error: {ultimo_error}"
    )


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
            f.write(f"commit_msg=add new badge {new_badges[0]['titulo']}\n")
        else:
            f.write(f"commit_msg=add {len(new_badges)} new badges: {names}\n")


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
