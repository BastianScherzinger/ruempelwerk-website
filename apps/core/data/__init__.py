"""Stammdaten des Projekts, getrennt von den Views.

Angelegt in F2 (seo-geo-plan) mit dem Preis-Teil. Städte und Jobs sind in F6
nachgezogen, die Leistungsseiten in A2 (Block 2) nach demselben Muster.

**Die Einfuhren unten sind Re-Exporte, keine vergessenen Zeilen.**
``_CITY_DATA``, ``_EXTRA_LANDING_CITIES`` und ``_JOB_DATA`` werden hier nicht
benutzt, sondern weitergereicht: ``views.py``, ``sitemaps.py`` und ``schema.py``
holen sie als ``from .data import …``. Wer sie entfernt, bricht diese Importe -
und zwar erst beim Aufruf der betroffenen Seite, nicht beim Start.
"""

from .cities import _CITY_DATA, _EXTRA_LANDING_CITIES  # noqa: F401
from .jobs import _JOB_DATA  # noqa: F401
from .pricing import *  # noqa: F401,F403
from .services import (  # noqa: F401
    _SERVICE_DATA, alle_leistungen, beispiel_preise, leistung,
)
