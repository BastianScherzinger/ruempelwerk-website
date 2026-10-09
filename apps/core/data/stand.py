# -*- coding: utf-8 -*-
"""Stand-Angaben: **eine** Quelle je Datum, maschinenlesbar und deutsch (G12).

**Warum es dieses Modul gibt.** Das Projekt macht zwei datierte Zusagen - den
Preisstand (``pricing.py``) und den Stand der recherchierten Ortsangaben
(``city_lokal.py``). Beide standen als getippter deutscher Text da
(``'August 2026'``), und beide brauchen fuer ``<time datetime="…">`` zusaetzlich
die ISO-Form. Zwei Schreibweisen desselben Datums nebeneinander sind genau die
Konstruktion, an der dieses Projekt schon zweimal verloren hat: die Preise
("ab 180 €" im Text, 300 € im Rechner) und die Bewertungszahlen.

Deshalb ist die **ISO-Form die Quelle** und der deutsche Text wird daraus
gerechnet. Wer den Stand hochzieht, aendert eine Zeile.

**Warum ein eigenes Modul:** ``pricing.py`` und ``city_lokal.py`` brauchen
dieselbe Funktion, und kein Modul unter ``data/`` darf etwas aus ``apps.core``
importieren - sonst entsteht ein Zirkel ueber ``context_processors``.
"""

_MONATE = ('Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli',
           'August', 'September', 'Oktober', 'November', 'Dezember')


def deutsch(iso):
    """``'2026-08'`` -> ``'August 2026'``.

    Wirft absichtlich, wenn die Eingabe kein ``JJJJ-MM`` ist: Ein stiller
    Rueckfall auf den Rohtext wuerde ein kaputtes ``datetime``-Attribut
    ueberleben lassen, und genau das soll hier nicht passieren.
    """
    jahr, monat = iso.split('-')[:2]
    return '%s %s' % (_MONATE[int(monat) - 1], jahr)
