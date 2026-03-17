#!/usr/bin/env python3
"""
Sincroniza badges desde el perfil público de Google Cloud Skills Boost.

Detecta nuevos badges por fecha, genera descripción y categoría via Gemini API,
y actualiza data/badges.json.
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
CATEGORIAS_JSON = PROJECT_ROOT / "data" / "categorias.json"


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

        if not all([link, img, title_span, date_span]):
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

    return badges


def parse_date(text: str) -> str | None:
    """Parse 'Earned Feb 13, 2026 EST' to '2026-02-13'."""
    match = re.match(r"Earned\s+(.+?)\s+\w{3,4}$", text)
    if not match:
        return None
    try:
        dt = datetime.strptime(match.group(1).strip(), "%b %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        # Handle dates with extra spaces like "Feb  3, 2026"
        cleaned = re.sub(r"\s+", " ", match.group(1).strip())
        try:
            dt = datetime.strptime(cleaned, "%b %d, %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None


def load_existing_badges() -> list[dict]:
    """Load current badges.json."""
    with open(BADGES_JSON, encoding="utf-8") as f:
        return json.load(f)


def load_categorias() -> list[dict]:
    """Load categorias.json."""
    with open(CATEGORIAS_JSON, encoding="utf-8") as f:
        return json.load(f)


def find_new_badges(profile_badges: list[dict], existing_badges: list[dict]) -> list[dict]:
    """Find badges from profile that are newer than the most recent in badges.json."""
    if not existing_badges:
        return profile_badges

    latest_date = existing_badges[0]["fecha"]
    return [b for b in profile_badges if b["fecha"] > latest_date]


def generate_desc_and_category_batch(badges: list[dict], categorias: list[dict], existing_badges: list[dict]) -> list[dict]:
    """Use Gemini API to generate description and category for multiple badges in a single call."""
    client = genai.Client()

    cat_list = "\n".join(f'- {c["id"]}: {c["nombre"]}' for c in categorias)

    # Pick examples from existing badges (up to 6, diverse categories)
    seen_cats = set()
    examples = []
    for b in existing_badges:
        if b["categoria"] not in seen_cats and len(examples) < 6:
            seen_cats.add(b["categoria"])
            examples.append(b)

    examples_text = json.dumps(examples, ensure_ascii=False, indent=2)
    badges_list = "\n".join(f'{i+1}. "{b["titulo"]}"' for i, b in enumerate(badges))

    prompt = f"""Eres un asistente que clasifica y describe badges/certificaciones de Google Cloud.

Para cada badge de la lista, genera un objeto JSON con:
1. "desc": Descripción en español de 1-2 frases sobre qué se aprende. Estilo profesional y conciso.
2. "categoria": Una de estas categorías existentes:
{cat_list}

Si ninguna categoría existente encaja, puedes crear una nueva añadiendo:
3. "nueva_categoria": objeto con campos:
   - "id": identificador en minúsculas con guiones (ej: "seguridad-cloud")
   - "nombre": nombre visible (ej: "Seguridad Cloud")
   - "icono": icono de Font Awesome 6 (ej: "fa-shield-halved")
   - "color": color hexadecimal que no repita los existentes

Solo incluye "nueva_categoria" si realmente no encaja en ninguna existente.

Ejemplos de badges existentes para referencia de estilo:
{examples_text}

Badges a clasificar:
{badges_list}

Responde SOLO con un JSON array válido (sin markdown), un objeto por badge, en el mismo orden."""

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
                print(f"  -> Model {model} unavailable (quota/capacity), trying next model...")
                continue
            raise
    if response is None:
        raise RuntimeError("All Gemini models exhausted their quota.")

    response_text = response.text.strip()
    response_text = re.sub(r"^```(?:json)?\s*", "", response_text)
    response_text = re.sub(r"\s*```$", "", response_text)

    return json.loads(response_text)


def save_badges(badges: list[dict]) -> None:
    """Save badges to badges.json with consistent formatting."""
    with open(BADGES_JSON, "w", encoding="utf-8") as f:
        json.dump(badges, f, ensure_ascii=False, indent=2)
        f.write("\n")


def save_categorias(categorias: list[dict]) -> None:
    """Save categorias to categorias.json with consistent formatting."""
    with open(CATEGORIAS_JSON, "w", encoding="utf-8") as f:
        json.dump(categorias, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    print("Fetching profile badges...")
    profile_badges = fetch_profile_badges()
    print(f"Found {len(profile_badges)} badges on profile.")

    existing_badges = load_existing_badges()
    print(f"Existing badges in JSON: {len(existing_badges)}")

    new_badges = find_new_badges(profile_badges, existing_badges)

    if not new_badges:
        print("No new badges found. Nothing to do.")
        sys.exit(0)

    print(f"Found {len(new_badges)} new badge(s):")
    for b in new_badges:
        print(f"  - {b['titulo']} ({b['fecha']})")

    categorias = load_categorias()
    categorias_updated = False

    # Generate description and category for all new badges in a single API call
    print(f"Generating desc/category for {len(new_badges)} badge(s) in one batch call...")
    results = generate_desc_and_category_batch(new_badges, categorias, existing_badges)

    completed_badges = []
    for badge, result in zip(new_badges, results):
        badge["desc"] = result["desc"]
        badge["categoria"] = result["categoria"]

        # Handle new category creation
        if "nueva_categoria" in result:
            new_cat = result["nueva_categoria"]
            cat_ids = {c["id"] for c in categorias}
            if new_cat["id"] not in cat_ids:
                categorias.append(new_cat)
                categorias_updated = True
                print(f"  -> NEW category created: {new_cat['id']} ({new_cat['nombre']})")

        completed_badges.append(badge)
        print(f"  -> {badge['titulo']}: {badge['categoria']}")

    # Insert new badges at the beginning (sorted by date, newest first)
    completed_badges.sort(key=lambda b: b["fecha"], reverse=True)
    updated_badges = completed_badges + existing_badges

    save_badges(updated_badges)
    if categorias_updated:
        save_categorias(categorias)
        print("Updated categorias.json with new category(ies).")
    print(f"Updated badges.json with {len(completed_badges)} new badge(s).")

    # Write badge names for use in commit message
    names = ", ".join(b["titulo"] for b in completed_badges)
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"new_badges=true\n")
            f.write(f"badge_count={len(completed_badges)}\n")
            if len(completed_badges) == 1:
                f.write(f"commit_msg=añadido nuevo badge {completed_badges[0]['titulo']}\n")
            else:
                f.write(f"commit_msg=añadidos {len(completed_badges)} nuevos badges: {names}\n")
    else:
        # Local execution
        print(f"\nBadges added: {names}")


if __name__ == "__main__":
    main()
