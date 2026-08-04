"""Tests unitarios de la lógica pura de scripts/sync_badges.py (sin red ni APIs)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from sync_badges import find_new_badges, parse_date


def _badge(url: str, titulo: str = "Badge", fecha: str = "2026-01-01") -> dict:
    return {"titulo": titulo, "img": "https://cdn.example/x.png", "fecha": fecha, "url": url}


def test_parse_date_formato_valido():
    assert parse_date("Earned Feb 13, 2026 EST") == "2026-02-13"
    assert parse_date("Earned Jun  6, 2026 CEST") == "2026-06-06"


def test_parse_date_formato_invalido_devuelve_none():
    assert parse_date("Completed Feb 13, 2026") is None
    assert parse_date("Earned mañana EST") is None
    assert parse_date("") is None


def test_find_new_badges_detecta_solo_los_nuevos_por_url():
    existentes = [_badge("https://a"), _badge("https://b")]
    perfil = [_badge("https://b"), _badge("https://c", titulo="Nuevo")]

    nuevos = find_new_badges(perfil, existentes)

    assert [b["url"] for b in nuevos] == ["https://c"]


def test_find_new_badges_sin_existentes_devuelve_todos():
    perfil = [_badge("https://a"), _badge("https://b")]
    assert find_new_badges(perfil, []) == perfil
