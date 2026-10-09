# -*- coding: utf-8 -*-
"""Feiertage Sachsen-Anhalt und Sachsen, 2026/2027 - fuer die Terminbuchung (§5).

**Warum es dieses Modul gibt.** Die Terminbuchung zeigt Mo-Sa 08/10/12/14/16
Uhr als moegliche Slots und schliesst Sonn- und Feiertage. Ein erfundener
oder falscher Feiertag waere entweder ein Slot, den niemand buchen kann
(Tag fehlt), oder ein offener Tag an einem echten Feiertag (Tag fehlt in der
Liste). Beides ist ohne Quelle nicht zu unterscheiden - deshalb steht die
Berechnung hier, einmal, nicht an der Stelle, die die Slots rendert.

**Warum berechnet und nicht eingetippt.** Die beweglichen Feiertage (Ostern
und alles, was daran haengt) haben in zwei Jahren zwei verschiedene Datumswerte
- eine getippte Liste ist beim naechsten Jahreswechsel automatisch falsch,
ohne dass es auffaellt (dieselbe Fehlerklasse wie ``date.today()`` in Regel 22).
Der Ostersonntag kommt aus dem anerkannten Gauss'schen Verfahren
(Meeus/Jones/Butcher-Algorithmus), alles andere ist ein fester Versatz dazu.

Das Modul kennt Django nicht und importiert nichts aus ``apps.core`` - wie
jedes Modul unter ``data/`` (Regel 4).
"""

import datetime

__all__ = [
    'BUNDESLAENDER', 'ostersonntag', 'feiertage_fuer_jahr', 'ist_feiertag',
    'feiertag_name',
]

BUNDESLAENDER = ('ST', 'SN')  # Sachsen-Anhalt, Sachsen - die beiden Einsatzländer.


def ostersonntag(jahr):
    """Ostersonntag nach dem Gauss'schen Verfahren (Meeus/Jones/Butcher).

    Geprueft gegen die amtlich bekannten Termine: 2026-04-05, 2027-03-28.
    """
    a = jahr % 19
    b = jahr // 100
    c = jahr % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    monat = (h + l - 7 * m + 114) // 31
    tag = ((h + l - 7 * m + 114) % 31) + 1
    return datetime.date(jahr, monat, tag)


def _tag(datum, versatz):
    return datum + datetime.timedelta(days=versatz)


def feiertage_fuer_jahr(jahr, bundesland='ST'):
    """``{datum: name}`` aller Feiertage eines Jahres in ``ST`` oder ``SN``.

    Gemeinsam in beiden Ländern: Neujahr, Karfreitag, Ostermontag, 1. Mai,
    Christi Himmelfahrt, Pfingstmontag, Tag der Deutschen Einheit,
    Reformationstag (seit 2018 in beiden Ländern ein permanenter Feiertag),
    1. und 2. Weihnachtsfeiertag.

    Nur Sachsen-Anhalt: Heilige Drei Könige (6. Januar).
    Nur Sachsen: Buß- und Bettag (Mittwoch vor dem 23. November).
    """
    if bundesland not in BUNDESLAENDER:
        raise ValueError(f'unbekanntes Bundesland: {bundesland!r}')

    ostern = ostersonntag(jahr)
    tage = {
        datetime.date(jahr, 1, 1): 'Neujahr',
        _tag(ostern, -2): 'Karfreitag',
        _tag(ostern, 1): 'Ostermontag',
        datetime.date(jahr, 5, 1): 'Tag der Arbeit',
        _tag(ostern, 39): 'Christi Himmelfahrt',
        _tag(ostern, 50): 'Pfingstmontag',
        datetime.date(jahr, 10, 3): 'Tag der Deutschen Einheit',
        datetime.date(jahr, 10, 31): 'Reformationstag',
        datetime.date(jahr, 12, 25): '1. Weihnachtsfeiertag',
        datetime.date(jahr, 12, 26): '2. Weihnachtsfeiertag',
    }
    if bundesland == 'ST':
        tage[datetime.date(jahr, 1, 6)] = 'Heilige Drei Könige'
    if bundesland == 'SN':
        # Buß- und Bettag: der Mittwoch vor dem 23. November (immer der
        # letzte Mittwoch vor diesem Datum, auch wenn der 23. selbst ein
        # Mittwoch ist - dann ist es der vorletzte).
        stichtag = datetime.date(jahr, 11, 23)
        versatz = (stichtag.weekday() - 2) % 7
        if versatz == 0:
            versatz = 7
        tage[stichtag - datetime.timedelta(days=versatz)] = 'Buß- und Bettag'
    return tage


def feiertag_name(datum, bundesland='ST'):
    """Der Name des Feiertags an ``datum`` in ``bundesland`` - oder ``None``."""
    return feiertage_fuer_jahr(datum.year, bundesland).get(datum)


def ist_feiertag(datum, bundesland='ST'):
    """True, wenn ``datum`` in ``bundesland`` ein gesetzlicher Feiertag ist."""
    return feiertag_name(datum, bundesland) is not None
