"""Slotberechnung fuer die Terminbuchung (Bauplan §5).

Getrennt von ``views.py`` aus demselben Grund wie ``leads.py``: reine Rechnung
mit Datenbankzugriff, die von der View **und** vom Dashboard-Template
gebraucht wird. Anders als ein Modul unter ``data/`` darf diese Datei Django
und ``apps.core`` benutzen - sie ist kein Stammdatenmodul (Regel 4 gilt nur
fuer ``apps/core/data/``).

**Belegt-Anschein ohne Taeuschung (UWG §5, Bauplan §5):** Ein Slot ist frei,
solange er ab morgen 00:00 liegt, an einem offenen Wochentag,
nicht durch eine ``Terminsperre`` gesperrt und nicht durch einen aktiven
``Besichtigungstermin`` (Status != abgesagt) belegt ist. Gesperrt und gebucht
sehen auf der Seite GLEICH aus ("nicht frei") - es werden nie erfundene
Buchungen angezeigt.
"""

import datetime

from django.utils import timezone

from .data import feiertage

__all__ = [
    'SLOT_ZEITEN_STANDARD', 'SLOT_ZEITEN_SAMSTAG', 'SLOT_DAUER_MINUTEN', 'BUNDESLAND',
    'ANZAHL_OFFENE_TAGE', 'fruehester_termin', 'zeiten_fuer_wochentag',
    'schliessgrund', 'slot_ende_uhrzeit', 'slot_anzeige', 'slot_datetime',
    'slot_frei', 'slot_im_zeitraum', 'slot_normieren', 'wochen_uebersicht', 'naechste_woche_start', 'kalender',
]

#: Fallback, wenn fuer einen Wochentag keine (aktive) Terminvorlage existiert.
SLOT_ZEITEN_STANDARD = ('08:00', '10:00', '12:00', '14:00', '16:00')
#: Samstag schliesst laut Google-Profil um 13 Uhr (``firma.ZEITEN``, 03.10.2026) -
#: der letzte Termin muss davor enden.
SLOT_ZEITEN_SAMSTAG = ('08:00', '10:00', '12:00')
SLOT_DAUER_MINUTEN = 25

#: Der Firmensitz liegt in Sachsen-Anhalt (Cansteinstraße 14, 06110 Halle);
#: das Einsatzgebiet reicht auch nach Sachsen (Leipzig) - fuer die
#: Feiertagsregel zaehlt der Sitz.
BUNDESLAND = 'ST'

#: Wie viele offene Buchungstage der Kalender zeigt (Sonn- und Feiertage
#: werden uebersprungen, nicht mitgezaehlt).
ANZAHL_OFFENE_TAGE = 10
#: Obergrenze in Kalendertagen, damit eine lange Sperrzeit die Schleife nicht
#: endlos laufen laesst.
_MAX_KALENDERTAGE = 28


def fruehester_termin(jetzt=None):
    """Der frueheste Zeitpunkt, den ein Kunde buchen darf: **morgen 00:00** Ortszeit.

    Seit 01.10.2026 (Zusage ``zusagen.TERMIN_FRUEHESTENS`` = "ab morgen",
    im Auftrag des Inhabers): Jeder freie Slot ab dem naechsten
    Kalendertag ist buchbar, unabhaengig von der Uhrzeit der Buchung. Vorher
    wurde ``BESICHTIGUNG_VORLAUF`` ("24-48 Stunden") als 48-Stunden-Sperre
    gelesen und der Kalender begann erst uebermorgen. Sonn- und Feiertage,
    Sperren und Belegung gelten weiter (``slot_frei``).
    """
    jetzt = jetzt or timezone.now()
    morgen = timezone.localtime(jetzt).date() + datetime.timedelta(days=1)
    return slot_datetime(morgen, '00:00')


def _vorlagen():
    """Alle Terminvorlagen in einer Abfrage - fuer die Schleife in ``wochen_uebersicht``."""
    from .models import Terminvorlage
    return {v.wochentag: v for v in Terminvorlage.objects.all()}


def zeiten_fuer_wochentag(wochentag, vorlagen=None):
    """``['08:00', ...]`` fuer einen Wochentag (0=Montag ... 6=Sonntag).

    Sonntag ist IMMER geschlossen, unabhaengig von einer etwaigen
    Datenbankzeile - das steht nicht zur Disposition (Bauplan §5).
    """
    if wochentag == 6:
        return []
    if vorlagen is None:
        vorlagen = _vorlagen()
    vorlage = vorlagen.get(wochentag)
    if vorlage is None:
        return list(SLOT_ZEITEN_SAMSTAG if wochentag == 5 else SLOT_ZEITEN_STANDARD)
    if not vorlage.aktiv:
        return []
    return sorted(vorlage.uhrzeiten)


def schliessgrund(datum, vorlagen=None):
    """``None``, wenn ``datum`` ein Buchungstag ist - sonst der Anzeigetext."""
    if datum.weekday() == 6:
        return 'Sonntag'
    name = feiertage.feiertag_name(datum, BUNDESLAND)
    if name:
        return name
    if not zeiten_fuer_wochentag(datum.weekday(), vorlagen):
        return 'Geschlossen'
    return None


def slot_ende_uhrzeit(zeit_str):
    """``'08:00'`` -> ``'08:25'`` (Ende = Beginn + ``SLOT_DAUER_MINUTEN``)."""
    h, m = (int(x) for x in zeit_str.split(':'))
    basis = datetime.datetime(2000, 1, 1, h, m)
    ende = basis + datetime.timedelta(minutes=SLOT_DAUER_MINUTEN)
    return ende.strftime('%H:%M')


def slot_anzeige(zeit_str):
    """``'08:00'`` -> ``'08:00–08:25 Uhr'`` - der Wortlaut aus ``f.html``."""
    return f'{zeit_str}–{slot_ende_uhrzeit(zeit_str)} Uhr'


def slot_datetime(datum, zeit_str):
    """``(date, '08:00')`` -> zeitzonenbewusstes ``datetime`` (Ortszeit)."""
    h, m = (int(x) for x in zeit_str.split(':'))
    naiv = datetime.datetime.combine(datum, datetime.time(h, m))
    return timezone.make_aware(naiv)


def _belegung(von, bis):
    """Gesperrte Tage/Zeiten und belegte Slots im Zeitraum - drei Abfragen statt drei je Slot."""
    from .models import Besichtigungstermin, Terminsperre
    ganze_tage, zeiten = set(), set()
    for sperre in Terminsperre.objects.filter(datum__gte=von, datum__lte=bis):
        if sperre.uhrzeit is None:
            ganze_tage.add(sperre.datum)
        else:
            zeiten.add((sperre.datum, sperre.uhrzeit.replace(second=0, microsecond=0)))
    belegt = set(Besichtigungstermin.objects
                 .exclude(status='abgesagt')
                 .filter(beginn__date__gte=von - datetime.timedelta(days=1),
                         beginn__date__lte=bis + datetime.timedelta(days=1))
                 .values_list('beginn', flat=True))
    return ganze_tage, zeiten, belegt


def slot_im_zeitraum(beginn_dt, jetzt=None):
    """True, wenn ``beginn_dt`` zwischen morgen 00:00 und dem Ende des Kalenderfensters liegt."""
    erster = fruehester_termin(jetzt)
    if beginn_dt < erster:
        return False
    letzter = timezone.localtime(erster).date() + datetime.timedelta(days=_MAX_KALENDERTAGE)
    return timezone.localtime(beginn_dt).date() < letzter


def slot_normieren(beginn_dt):
    """Ortszeit-``datetime`` auf volle Minute (Sekunden/Mikrosekunden weg), zeitzonenbewusst."""
    lokal = timezone.localtime(beginn_dt)
    return slot_datetime(lokal.date(), lokal.strftime('%H:%M'))


def slot_frei(beginn_dt, jetzt=None, _vorab=None):
    """True, wenn der Slot ab morgen liegt, offen, ungesperrt und unbebucht ist.

    Der Zeitstempel muss **exakt** eine Slotzeit des Wochentags treffen (keine
    Sekunden, keine Uhrzeit ausserhalb der Terminvorlage) - sonst liesse sich
    ein Termin um 03:17 oder eine Sekunde neben einem belegten Slot buchen.

    ``_vorab``: das Ergebnis von ``_belegung`` und die Vorlagen, wenn
    ``wochen_uebersicht`` viele Slots in einem Zug prueft (gleiche Regel,
    weniger Abfragen).
    """
    from .models import Besichtigungstermin, Terminsperre

    if beginn_dt < fruehester_termin(jetzt):
        return False
    lokal = timezone.localtime(beginn_dt)
    if lokal.second or lokal.microsecond:
        return False
    datum = lokal.date()
    zeit = lokal.time().replace(second=0, microsecond=0)
    vorlagen_vorab = _vorab[1] if _vorab is not None else None
    if lokal.strftime('%H:%M') not in zeiten_fuer_wochentag(datum.weekday(), vorlagen_vorab):
        return False
    if _vorab is not None:
        (ganze_tage, zeiten, belegt), vorlagen = _vorab
        if schliessgrund(datum, vorlagen):
            return False
        return (datum not in ganze_tage and (datum, zeit) not in zeiten
                and beginn_dt not in belegt)
    if schliessgrund(datum):
        return False
    if Terminsperre.objects.filter(datum=datum, uhrzeit__isnull=True).exists():
        return False
    if Terminsperre.objects.filter(datum=datum, uhrzeit=zeit).exists():
        return False
    if Besichtigungstermin.objects.filter(beginn=beginn_dt).exclude(status='abgesagt').exists():
        return False
    return True


def naechste_woche_start(jetzt=None):
    """Der Kalendertag, an dem der Kalender beginnt: **morgen** (Ortszeit)."""
    return timezone.localtime(fruehester_termin(jetzt)).date()


def wochen_uebersicht(start_datum=None, tage=ANZAHL_OFFENE_TAGE, jetzt=None):
    """Die naechsten ``tage`` **offenen** Tage als Liste von ``{'datum', 'geschlossen', 'slots': [...]}``.

    Sonntage, Feiertage und deaktivierte Wochentage werden uebersprungen (nicht
    als graue Spalte gezeigt - ``kalender()`` nennt sie in einer Zeile); es
    werden hoechstens ``_MAX_KALENDERTAGE`` Kalendertage durchsucht. Jeder Tag
    traegt ``'geschlossen': None`` und ``'frei_anzahl'``.

    Jeder Slot: ``{'zeit', 'anzeige', 'beginn' (aware datetime), 'wert'
    (String fuers Formular), 'frei'}``. Gebuchte und gesperrte Slots erscheinen
    ununterscheidbar als ``frei=False`` - das ist Absicht, nicht eine Luecke.
    """
    start = start_datum or naechste_woche_start(jetzt)
    vorlagen = _vorlagen()
    vorab = (_belegung(start, start + datetime.timedelta(days=_MAX_KALENDERTAGE)), vorlagen)
    tage_liste = []
    for i in range(_MAX_KALENDERTAGE):
        if len(tage_liste) >= tage:
            break
        datum = start + datetime.timedelta(days=i)
        if schliessgrund(datum, vorlagen):
            continue
        slots = []
        for zeit in zeiten_fuer_wochentag(datum.weekday(), vorlagen):
            beginn = slot_datetime(datum, zeit)
            slots.append({
                'zeit': zeit,
                'anzeige': slot_anzeige(zeit),
                'beginn': beginn,
                'wert': beginn.isoformat(),
                'frei': slot_frei(beginn, jetzt, _vorab=vorab),
            })
        tage_liste.append({
            'datum': datum, 'geschlossen': None, 'slots': slots,
            'frei_anzahl': sum(1 for sl in slots if sl['frei']),
        })
    return tage_liste


def kalender(jetzt=None, tage=ANZAHL_OFFENE_TAGE):
    """Alles, was die Komponente fuer Schritt 1 braucht, in einem Aufruf.

    ``{'tage': [...offene Tage...], 'erster_frei': Index des ersten Tags mit
    freiem Slot (0, wenn keiner), 'geschlossen': [{'datum', 'grund'}, ...]}``;
    ``geschlossen`` nennt die uebersprungenen **Feiertage** im Zeitraum (Sonntage
    stehen in der festen Legende, nicht in der Liste).
    """
    start = naechste_woche_start(jetzt)
    offen = wochen_uebersicht(start_datum=start, tage=tage, jetzt=jetzt)
    erster = next((i for i, t in enumerate(offen) if t['frei_anzahl']), 0)
    geschlossen = []
    if offen:
        vorlagen = _vorlagen()
        tag = start
        while tag <= offen[-1]['datum']:
            grund = schliessgrund(tag, vorlagen)
            if grund and grund != 'Sonntag':
                geschlossen.append({'datum': tag, 'grund': grund})
            tag += datetime.timedelta(days=1)
    return {'tage': offen, 'erster_frei': erster, 'geschlossen': geschlossen}


def slot_aus_wert(wert):
    """Das Formularfeld (ISO-Zeitstempel) zurueck in ein aware ``datetime``.

    ``None`` bei jedem Wert, der sich nicht parsen laesst - eine manipulierte
    Eingabe darf nie eine Ausnahme werfen, die eine 500-Seite zeigt.
    """
    if not wert:
        return None
    try:
        dt = datetime.datetime.fromisoformat(wert)
    except (ValueError, TypeError):
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    return dt
