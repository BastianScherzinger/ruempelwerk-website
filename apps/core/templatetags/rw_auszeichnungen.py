"""``{% rw_nachweise %}`` - externe Nachweise (§6).

Inclusion-Tag, isolierter Context wie bei ``rw_termin`` - hier ohne
``firma.context()``, weil das Template keine Stammdaten braucht.
Der fruehere Tag ``rw_siegel`` (nur das Abzeichen) war nirgends eingebunden und
ist am 01.10.2026 samt ``components/rw_siegel.html`` entfernt (PJ09).
"""

from django import template

from ..data import auszeichnungen

register = template.Library()


@register.inclusion_tag('components/rw_nachweise.html')
def rw_nachweise():
    """Trustlocal-Karte + WKDB-Zeile - nie die Google-Zahl (siehe Template)."""
    return {'trustlocal': auszeichnungen.TRUSTLOCAL, 'wkdb': auszeichnungen.WKDB}
