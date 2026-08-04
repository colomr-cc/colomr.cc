"""Tests unitarios de la lógica pura de scripts/sync_badges.py (sin red ni APIs)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from bs4 import BeautifulSoup

from sync_badges import (
    extract_badge,
    find_new_badges,
    merge_badges,
    parse_date,
    write_github_output,
)

HTML_BADGE = """
<div class="profile-badge">
  <a class="badge-image" href="https://skills/badges/1"><img src="https://cdn/img.png"></a>
  <span class="ql-title-medium">Un Badge</span>
  <span class="ql-body-medium">Earned Feb 13, 2026 EST</span>
</div>
"""


def _div(html: str):
    return BeautifulSoup(html, "html.parser").select_one("div.profile-badge")


def _badge(url: str, titulo: str = "Badge", fecha: str = "2026-01-01") -> dict:
    return {"titulo": titulo, "img": "https://cdn.example/x.png", "fecha": fecha, "url": url}


def test_extract_badge_completo():
    badge = extract_badge(_div(HTML_BADGE))

    assert badge == {
        "titulo": "Un Badge",
        "img": "https://cdn/img.png",
        "fecha": "2026-02-13",
        "url": "https://skills/badges/1",
    }


def test_extract_badge_devuelve_none_si_falta_el_enlace():
    html = HTML_BADGE.replace('class="badge-image"', 'class="otra-cosa"')
    assert extract_badge(_div(html)) is None


def test_extract_badge_devuelve_none_si_falta_el_titulo():
    html = HTML_BADGE.replace('class="ql-title-medium"', 'class="otra-cosa"')
    assert extract_badge(_div(html)) is None


def test_extract_badge_devuelve_none_si_la_fecha_no_es_valida():
    html = HTML_BADGE.replace("Earned Feb 13, 2026 EST", "Completado ayer")
    assert extract_badge(_div(html)) is None


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


def test_merge_badges_prefiere_existentes_y_completa_con_nuevos():
    existente = _badge("https://a") | {"desc": "descripción guardada"}
    nuevo = _badge("https://b") | {"desc": "descripción nueva"}
    latest = [_badge("https://b"), _badge("https://a")]

    final = merge_badges(latest, [existente], [nuevo])

    assert [b["url"] for b in final] == ["https://b", "https://a"]
    assert final[1]["desc"] == "descripción guardada"
    assert final[0]["desc"] == "descripción nueva"


def test_merge_badges_descarta_badges_sin_origen():
    latest = [_badge("https://desconocido")]
    assert merge_badges(latest, [], []) == []


def test_write_github_output_un_badge(tmp_path, monkeypatch):
    out = tmp_path / "output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))

    write_github_output([_badge("https://a", titulo="Nuevo Badge")])

    contenido = out.read_text(encoding="utf-8")
    assert "new_badges=true" in contenido
    assert "badge_count=1" in contenido
    assert "commit_msg=añadido nuevo badge Nuevo Badge" in contenido


def test_write_github_output_varios_badges(tmp_path, monkeypatch):
    out = tmp_path / "output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))

    write_github_output([_badge("https://a", titulo="Uno"), _badge("https://b", titulo="Dos")])

    contenido = out.read_text(encoding="utf-8")
    assert "badge_count=2" in contenido
    assert "commit_msg=añadidos 2 nuevos badges: Uno, Dos" in contenido
