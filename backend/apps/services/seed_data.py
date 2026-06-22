"""Structured seed catalog for ``seed_prices`` (see ADR 0001).

Derived from the repo-root reference files ``prices_joao.py`` (depilação laser)
and ``prices_tiz.py`` (unhas + estética). Those files are human reference only;
this module is the in-container source the seed command consumes, after which the
**DB is the source of truth**. Prices in EUR; durations in minutes.

``price = None`` + ``is_quote_only = True`` models the ``-1`` "contactar" sentinel
from the reference files (never stored as -1 — see business-rules.md).

Laser durations are not in the reference file; a conservative 15-minute default
is used and meant to be tuned per service in the BO.
"""

# Staff identities (provided by the studio owner). Edited later in the BO.
STAFF = {
    "joao": {
        "first_name": "João",
        "last_name": "Veloso",
        "msisdn": "+351910028444",
        "email": "",
    },
    "tiz": {
        "first_name": "Beatriz",
        "last_name": "Veloso",
        "msisdn": "+351913999420",
        "email": "beautystudio.bv.2026@gmail.com",
    },
}

CATEGORIES = [
    {"slug": "unhas", "name": "Unhas", "display_order": 1},
    {"slug": "estetica", "name": "Estética", "display_order": 2},
    {"slug": "depilacao-laser", "name": "Depilação Laser", "display_order": 3},
]

_LASER_DEFAULT_MINUTES = 15

# (category_slug, staff_key, name, price | None, duration_minutes, is_quote_only, is_nail_service)
SERVICES = [
    # --- Unhas (Beatriz) ---
    ("unhas", "tiz", "Reparação de unha", None, 15, True, True),
    ("unhas", "tiz", "Remoção de unha", 5, 30, False, True),
    ("unhas", "tiz", "Verniz gel mãos", 15, 75, False, True),
    ("unhas", "tiz", "Verniz gel pés", 10, 30, False, True),
    ("unhas", "tiz", "Primeira aplicação com extensão (< 2cm)", 25, 150, False, True),
    ("unhas", "tiz", "Primeira aplicação com extensão (> 2cm)", None, 150, True, True),
    ("unhas", "tiz", "Primeira aplicação sobre unha natural", 20, 90, False, True),
    ("unhas", "tiz", "Manutenção de gel", "17.50", 90, False, True),
    ("unhas", "tiz", "Manutenção de gel com Nail Art simples", None, 105, True, True),
    ("unhas", "tiz", "Manutenção de gel com Nail Art complexa", None, 120, True, True),
    # --- Estética (Beatriz) ---
    ("estetica", "tiz", "Buço à linha", 4, 15, False, False),
    ("estetica", "tiz", "Sobrancelha à linha", 6, 15, False, False),
    ("estetica", "tiz", "Sobrancelha e buço à linha", 10, 15, False, False),
    ("estetica", "tiz", "Limpeza de pele", 30, 75, False, False),
    ("estetica", "tiz", "Lifting de pestanas", 23, 90, False, False),
    ("estetica", "tiz", "Brow lamination", 18, 60, False, False),
    # --- Depilação Laser (João) — rosto ---
    ("depilacao-laser", "joao", "Orelhas", 5, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Buço", 10, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Queixo", 10, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Patilhas", 10, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Maçãs do rosto", 5, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Nariz", 5, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Linha da nuca", 15, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Linha do pescoço", 15, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Entre sobrancelhas", 5, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Barba", 25, 30, False, False),
    # --- Depilação Laser (João) — corpo ---
    ("depilacao-laser", "joao", "Mãos", 8, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Pés", 8, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Ombros", 10, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Axilas", 15, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Antebraços", 15, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Braços completos", 25, 30, False, False),
    ("depilacao-laser", "joao", "Seios", 5, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Linha do peito", 5, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Linha alba", 5, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Abdómen e tórax", 15, 30, False, False),
    ("depilacao-laser", "joao", "Peito", 25, 30, False, False),
    ("depilacao-laser", "joao", "Costas", 25, 30, False, False),
    ("depilacao-laser", "joao", "Lombar", 10, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Glúteos", 10, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Joelhos", 10, _LASER_DEFAULT_MINUTES, False, False),
    ("depilacao-laser", "joao", "Virilhas", 20, 30, False, False),
    ("depilacao-laser", "joao", "Perna sem virilha", 30, 45, False, False),
    ("depilacao-laser", "joao", "Meia perna superior", 20, 30, False, False),
    ("depilacao-laser", "joao", "Meia perna inferior", 15, 30, False, False),
]
