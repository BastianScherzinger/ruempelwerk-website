# -*- coding: utf-8 -*-
"""Zeitzusagen: **eine** Quelle je Versprechen (Befund K2).

**Warum es dieses Modul gibt.** ``pricing.py`` ist die Quelle jeder Preiszahl,
``reviews.py`` die jeder Bewertungszahl, ``stand.py`` die jedes Datums. Für
Zeitversprechen gab es bis zum 25.08.2026 **gar keine Quelle** — und ohne
Quelle liefen zwei verschiedene Zusagen unter demselben Wort.

**Die Korrektur vom 26.08.2026, bestätigt vom Inhaber — es sind ZWEI Zusagen:**

====================  ==========================  ==============================
                      **Antwort auf die Anfrage**  **Termin vor Ort**
====================  ==========================  ==============================
Wie lange             ``ANTWORT`` = 2 Stunden      ``c['response']``, je Stadt
Wo                    **überall gleich**           von 1–2 Stunden bis 1–2 Werktage
Wann                  rund um die Uhr, jeden Tag   Anfahrt und Auslastung
====================  ==========================  ==============================

**Antworten heißt nicht hinfahren.** Genau diese Verwechslung steckte in den
Vorlagen: ``city.html`` schrieb „Rückmeldung in {{ city.response }}", und
``response`` steht für die allermeisten Städte auf ``1 Werktag``, für einige
auf ``1–2 Werktage`` und nur für wenige auf Stunden. Die genaue Verteilung
liefert ``response_verteilung()`` aus ``cities.py`` — sie steht bewusst
**nicht** als Zahl in diesem Text: Hier stand bis zum 02.10.2026 „45 der 54
Städte“, während die Seite längst 57 Stadtseiten hatte (EIG399; davor „51
Städte auf 2–5 Werktage“, EIG147). Als Antwortzeit gelesen ist das zu
langsam — als Termin vor Ort ist es richtig. Am 25.08.2026 ist
daraufhin die *richtige* Zusage („Antwort in 2 Stunden") von sechs Stellen
entfernt worden, weil sie an der *falschen* Zahl gemessen wurde.

**Die Lehre steht in** ``docs/fallen.md``: Eine Prüfung kann nur feststellen,
ob eine Zahl zu ihrer Quelle passt — **nicht, ob es die richtige Quelle ist.**
Bevor eine Zusage entfernt wird, ist die Frage nicht „steht die Zahl irgendwo?",
sondern „wovon redet der Satz überhaupt?".

Was hier steht, ist deshalb entweder vom Inhaber **bestätigt** (Gruppe C), aus
``cities.py`` *hergeleitet* (Gruppe A) oder als ungedeckt *ausgewiesen*
(Gruppe B).

**Gruppe A — hergeleitet.** Diese Werte rechnet das Modul beim Import aus
``cities.py`` aus. Wer eine Stadt schneller oder langsamer einstuft, ändert
damit automatisch den Satz auf der Startseite. Eine zweite Zahl, die davon
abweichen könnte, gibt es nicht mehr.

**Gruppe B — ungedeckt. Zurzeit leer.** Hier standen bis zum 26.08.2026
``ANGEBOT_NACH_BESICHTIGUNG`` und ``BESICHTIGUNG_VORLAUF`` als offene
Rückfragen (``BESICHTIGUNG_VORLAUF`` seit 01.10.2026 durch ``TERMIN_FRUEHESTENS`` ersetzt). **Der Inhaber hat beide am 26.08.2026 bestätigt**; sie sind nach
Gruppe C gewandert; seit 01.10.2026 gehören dort auch ``TERMIN_FRUEHESTENS`` und
``ANGEBOT_NACH_VIDEO`` dazu (im Auftrag des Inhabers). Wer künftig eine Zusage ohne Quelle braucht, legt sie hier
an — nicht bei den bestätigten — und setzt sie im Zweifel auf ``''``, dann
verschwindet sie aus allen Vorlagen zugleich.

``check_seo`` prüft **jede** sichtbare Zeitzusage gegen dieses Modul, so wie es
jede Bewertungszahl gegen ``reviews.stand()`` prüft.

Das Modul kennt Django nicht und importiert nichts aus ``apps.core`` — sonst
entsteht ein Zirkel über ``context_processors`` (Regel 4).
"""

import re

from .cities import _CITY_DATA

__all__ = [
    'ANTWORT', 'ANTWORT_KURZ',
    'TERMIN_REGEL', 'TERMIN_SCHNELL', 'TERMIN_SCHNELL_STAEDTE',
    'TERMIN_KURZ', 'ZUSAGE_SATZ', 'TERMIN_SCHNELL_ORTE',
    'ANGEBOT_BEI_BESICHTIGUNG', 'BESICHTIGUNG_VORLAUF', 'RECHNER_DAUER',
    'BESICHTIGUNG_DAUER', 'TERMIN_FRUEHESTENS', 'ANGEBOT_NACH_VIDEO',
    'response_dativ', 'response_verteilung', 'ANTWORT_GILT',
    'erlaubte_zeitangaben', 'zusagen_context',
    'einheiten_muster', 'kanonische_einheit', 'zahlwort_muster',
]

# ── Die Schreibweisen einer Zeiteinheit ─────────────────────────────────────
#
# **Warum diese Tabelle hier steht und nicht in check_seo.py.** Sie ist der
# einzige Ort, an dem eine neue Schreibweise nachgetragen werden muss - direkt
# neben der Quelle der Zusagen selbst. ``check_seo`` baut sein Suchmuster
# daraus; zwei Listen, die auseinanderlaufen koennen, gibt es nicht mehr.
#
# **Warum sie eine Aufzaehlung ist und keine Herleitung.** Das ist am
# 25.08.2026 gemessen worden, nachdem die Pruefung dreimal hintereinander eine
# Schreibweise uebersehen hatte (``2h``, ``1 Werktag``, ``Std.``). Drei
# Umkehrungen wurden durchgerechnet - ueber alle 85 Seiten:
#
#   * **"Zahl + irgendein Wort"**: 189 verschiedene Folgewoerter, 3.353
#     Vorkommen, **99 davon einmalig**. Die Freigabeliste bestuende ueberwiegend
#     aus Inhaltswoertern ("Halle", "Termin", "Fotos") und muesste bei jeder
#     Textaenderung nachgezogen werden.
#   * **"Zahl + Wort, das ein abgekuerzter Zeitstamm sein koennte"**
#     (Teilfolge-Vergleich): 19 Token, davon **4 falsch** - ``Abs.`` aus den
#     Rechtstexten, die Wochentage ``Mo``/``Mi`` und das Wort ``mit``. Und weil
#     dieses Projekt Abschnitte als "1 Anfrage", "2 Besichtigung" nummeriert,
#     trifft die Regel jede kuenftige Ueberschrift, die mit einem W-Wort
#     beginnt.
#   * **"Zahl + Wort im Umfeld eines Zusage-Wortes"**: ueber 40 Token, in der
#     Mehrzahl Abschnittsnummern, Telefonnummern und Paragrafenverweise.
#
# Alle drei verlangen eine Freigabeliste, die **mit dem Inhalt waechst** - und
# eine Pruefung, die man bei jeder Textaenderung nachziehen muss, wird nicht
# nachgezogen. Die Aufzaehlung waechst dagegen nur, wenn jemand eine **neue
# Abkuerzung** einfuehrt, und das ist selten und sichtbar.
#
# **Der Preis dafuer steht in check_seo._pruefe_zeitzusagen als erster Punkt
# der Liste "Was diese Pruefung nicht finden kann".** Wer eine Zusage in einer
# neuen Schreibweise setzt, traegt sie hier nach.
_EINHEITEN = {
    'Stunde': ('Stunden', 'Stunde', 'Stdn.', 'Stdn', 'Std.', 'Std', 'h'),
    'Werktag': ('Werktagen', 'Werktage', 'Werktag',
                'Arbeitstagen', 'Arbeitstage', 'Arbeitstag', 'AT'),
    'Minute': ('Minuten', 'Minute', 'Min.', 'Min'),
    # Kein blosses 's': Mit re.I traefe es jedes 'S' hinter einer Zahl.
    'Sekunde': ('Sekunden', 'Sekunde', 'Sek.', 'Sek'),
}

#: Kanonische Einheit je Schreibweise, klein geschrieben und ohne Punkt.
_EINHEIT_NACH_WORT = {
    form.lower().rstrip('.'): kanon
    for kanon, formen in _EINHEITEN.items() for form in formen
}


def einheiten_muster():
    """Die Alternative fuer den regulaeren Ausdruck in ``check_seo``.

    Laengste Form zuerst - sonst frisst ``Std`` das ``n`` von ``Stdn`` nicht
    mit und ``Werktag`` nicht das ``en`` von ``Werktagen``. Der Punkt wird
    maskiert, damit er nicht als "beliebiges Zeichen" gilt.
    """
    formen = sorted(_EINHEIT_NACH_WORT, key=len, reverse=True)
    return '|'.join(re.escape(f) + r'\.?' for f in formen)


#: Ausgeschriebene Zahlwoerter. **Geschlossene Menge** - anders als die
#: Schreibweisen einer Einheit waechst diese Liste nicht mit dem Inhalt, und
#: hoehere Zahlen schreibt niemand aus. Gebraucht, weil "in zwei Minuten" am
#: 25.08.2026 die **sechste** Schreibweise derselben Aussage war und weder vom
#: Ziffernmuster noch von RE_ZEITWORT gesehen wurde.
_ZAHLWOERTER = (
    'einer', 'einem', 'eine', 'ein', 'zwei', 'drei', 'vier', 'fünf', 'sechs',
    'sieben', 'acht', 'neun', 'zehn', 'elf', 'zwölf', 'zwanzig', 'dreißig',
    'vierzig', 'fünfzig', 'sechzig', 'anderthalb',
)


def zahlwort_muster():
    """Die Alternative der ausgeschriebenen Zahlen, laengste Form zuerst."""
    return '|'.join(re.escape(w) for w in
                    sorted(_ZAHLWOERTER, key=len, reverse=True))


def kanonische_einheit(wort):
    """``'Std.'`` -> ``'Stunde'``; ``None``, wenn es keine Zeiteinheit ist."""
    return _EINHEIT_NACH_WORT.get((wort or '').lower().rstrip('.'))


# **Aus derselben Tabelle wie das Suchmuster.** Hier stand bis zum 25.08.2026
# eine eigene, kürzere Liste (``Stunde|Werktag|Tag|Woche``) — und genau das ist
# die Konstruktion, gegen die dieses Modul geschrieben wurde: Als „Sekunde" in
# die Einheitentabelle kam, kannte das Suchmuster in ``check_seo`` die Einheit,
# ``_spanne()`` aber nicht — und die Prüfung meldete ihre eigene Zusage
# „60 Sekunden" 345-mal als quellenlos.
_RE_SPANNE = re.compile(r'(\d+)(?:\s*[–-]\s*(\d+))?\s*(' + einheiten_muster() + r')',
                        re.I)


def _spanne(text):
    """``'2–4 Stunden'`` -> ``(2, 4, 'Stunde')``; ``None``, wenn nichts passt.

    Die Einheit kommt kanonisch zurück (``'Std.'`` -> ``'Stunde'``), damit
    zwei Schreibweisen derselben Einheit nicht als zwei Einheiten zählen.
    """
    m = _RE_SPANNE.search(text or '')
    if not m:
        return None
    von = int(m.group(1))
    bis = int(m.group(2)) if m.group(2) else von
    return von, bis, kanonische_einheit(m.group(3))


def _plural(n, einheit, dativ=False):
    """``(2, 'Werktag')`` -> ``'Werktage'``; mit ``dativ`` -> ``'Werktagen'``.

    Die Dativform wird gebraucht, weil jede Verwendung im Satz auf „in …"
    folgt: „in 1–2 Werktagen", nicht „in 1–2 Werktage". Ohne sie steht auf
    der Startseite ein Grammatikfehler — und den korrigiert dann jemand von
    Hand im Template, womit die Zahl wieder zwei Quellen hätte.
    """
    if n == 1:
        return einheit
    if einheit == 'Werktag':
        return 'Werktagen' if dativ else 'Werktage'
    return einheit + 'n'


def _text(von, bis, einheit, dativ=False):
    if von == bis:
        return '%d %s' % (von, _plural(von, einheit, dativ))
    return '%d–%d %s' % (von, bis, _plural(bis, einheit, dativ))


def response_dativ(text):
    """``'1–2 Werktage'`` -> ``'1–2 Werktagen'`` - für „Termin vor Ort in …".

    ``c['response']`` steht im Nominativ in ``cities.py``; jede Verwendung im
    Satz folgt aber auf „in …". Live stand deshalb „Termin vor Ort in 1–2
    Werktage" (EIG153). Was sich nicht zerlegen lässt, kommt unverändert
    zurück - lieber ein Kasusfehler als eine verschwundene Zusage.
    """
    s = _spanne(text)
    if not s:
        return text or ''
    return _text(*s, dativ=True)


# **Jede Stadt bekommt ihre Dativform als ``response_dativ``** (EIG153,
# 24.09.2026). Ergänzt hier und nicht in ``cities.py``, weil die Form aus
# ``_plural`` kommen muss - eine zweite, getippte Spalte liefe auseinander.
# ``setdefault``: Trägt ``cities.py`` den Wert später selbst, gilt der.
# ``city_page``/``matrix_page`` kopieren das Städte-Dict erst nach dem Import
# dieses Moduls (``views.py`` importiert es auf Modulebene), der Schlüssel ist
# also in jeder Kopie.
for _c in _CITY_DATA.values():
    _c.setdefault('response_dativ', response_dativ(_c.get('response')))


def _kerngebiet():
    """Die Städte, für die überhaupt eine Zusage gilt.

    ``randgebiet``-Städte sind ausgenommen: Für sie sagt jede Seite ohnehin
    „Termin nach Absprache" — sie in eine pauschale Zusage einzurechnen würde
    sie unnötig verschlechtern.
    """
    return [c for c in _CITY_DATA.values() if not c.get('randgebiet')]


def _herleitung():
    stunden, werktage = [], []
    schnelle_staedte = []
    for c in _kerngebiet():
        s = _spanne(c.get('response'))
        if not s:
            continue
        if s[2] == 'Stunde':
            stunden.append(s)
            schnelle_staedte.append(c['name'])
        else:
            werktage.append(s)

    schnell = (_text(min(v for v, _, _ in stunden), max(b for _, b, _ in stunden),
                     'Stunde', dativ=True) if stunden else None)
    # Die **langsamste** Zusage des Kerngebiets, nicht die häufigste. Eine
    # pauschale Zusage ist nur dann wahr, wenn sie für die langsamste Stadt
    # gilt — genau daran ist „2 Stunden" gescheitert.
    regel = (_text(min(v for v, _, _ in werktage), max(b for _, b, _ in werktage),
                   'Werktag', dativ=True) if werktage else None)
    return schnell, sorted(schnelle_staedte), regel


# ── Gruppe C: vom Inhaber bestätigt ─────────────────────────────────────────
#: **Wie schnell auf eine Anfrage geantwortet wird. Gilt überall gleich.**
#:
#: Bestätigt vom Inhaber am 26.08.2026: „Das Versprechen, dass wir in 2 Stunden
#: antworten, ist echt, wir sind immer erreichbar — das heißt nicht, dass wir da
#: direkt hinfahren."
#:
#: **Deshalb hat diese Zusage keine Herleitung aus** ``cities.py``: Sie hängt
#: nicht am Ort, sondern an der Erreichbarkeit. Die ortsabhängige Zahl ist eine
#: andere — ``c['response']``, der Termin vor Ort. Wer die beiden verwechselt,
#: verspricht entweder zu viel (2 Stunden bis vor die Tür in Bremerhaven) oder
#: zu wenig (5 Werktage bis zur ersten Antwort). Beides ist hier schon passiert.
ANTWORT = '2 Stunden'

#: **Wann die Antwortzusage gilt: jederzeit.** Entscheidung (im Auftrag
#: des Inhabers) am 02.10.2026, EIG394: Die Antwort in ``ANTWORT`` gilt rund um
#: die Uhr, auch abends, am Wochenende und an Feiertagen. Die Geschäftszeiten in
#: ``firma.ZEITEN_ANZEIGE`` (seit 03.10.2026 wie das Google-Profil: Mo–Fr 8–19, Sa 8–13, So 9–12 Uhr) gelten für **Telefon und
#: Besichtigung**, nicht für die Antwort auf eine Anfrage. Vorher begründete
#: dieses Modul die Zusage mit „erreichbar Mo–Sa 8–18 Uhr“, und eine Anfrage am
#: Samstagabend ließ offen, ob die zwei Stunden gelten.
ANTWORT_GILT = 'rund um die Uhr'

#: Die kurze Form für Trustbar, Kacheln und Aufzählungen.
ANTWORT_KURZ = 'Antwort in %s' % ANTWORT

TERMIN_SCHNELL, TERMIN_SCHNELL_STAEDTE, TERMIN_REGEL = _herleitung()

# **Beide Hälften dürfen leer sein, und das darf nichts umbringen.**
# ``_herleitung()`` liefert ``None``, wenn keine Kerngebietsstadt Stunden nennt
# (oder keine Werktage). Dieses Modul steht auf Modulebene und wird von
# ``views.py``, ``emails.py``, ``services.py`` und ``context_processors.py``
# importiert — ein ``IndexError`` beim Import wäre ein **500 auf jeder Seite**,
# und der Fall tritt schon ein, wenn jemand die vier Stundenstädte auf
# ``randgebiet`` setzt. Nachgespielt am 25.08.2026. Fehlt die Werktage-Hälfte,
# entstünde ohne den Rückfall außerdem still der Text „Rückmeldung in None".
if not TERMIN_REGEL:                                       # pragma: no cover
    # Der ehrliche Rückfall ist die **langsamste** Angabe, die es im Kerngebiet
    # noch gibt — notfalls die Stundenzusage. Gibt es gar keine, wird gar nichts
    # versprochen; die Vorlagen blenden dann eine leere Zusage aus.
    # '' und nicht None: Django rendert ``{{ x }}`` fuer None als den Text
    # "None", und f-Strings in emails.py taeten dasselbe. Ein leerer String
    # laesst den Satz still verschwinden - was hier das Richtige ist.
    TERMIN_REGEL = TERMIN_SCHNELL or ''


def _und(namen):
    """``['A', 'B', 'C']`` -> ``'A, B und C'``; ``[]`` -> ``''``.

    Der leere Fall ist kein Schönheitsfehler: Ohne ihn wirft ``namen[-1]``
    einen ``IndexError`` beim **Import** des Moduls (S4).
    """
    namen = list(namen)
    if not namen:
        return ''
    if len(namen) == 1:
        return namen[0]
    return ', '.join(namen[:-1]) + ' und ' + namen[-1]


#: Die kurze Form für Badges und Aufzählungen. Immer die **pauschal wahre**.
#: Bis zum 26.08.2026 stand hier „Rückmeldung in …" — das war der Fehler selbst:
#: Dieselbe Zahl beschreibt den **Termin vor Ort**, nicht die Antwortzeit.
TERMIN_KURZ = ('Termin vor Ort in %s' % TERMIN_REGEL) if TERMIN_REGEL else ''

#: Die schnellen Städte als fertiger Aufzählungstext. **Einzige Quelle** —
#: ``home.html`` nannte zwei statt vier Städte und ``anfrage.html`` schrieb
#: „Halle" statt „Halle (Saale)", beide von Hand nachgezogen (S5).
TERMIN_SCHNELL_ORTE = _und(TERMIN_SCHNELL_STAEDTE)

#: Der vollständige Satz: erst die Zusage, die überall gilt, dann die
#: schnellere für die Städte, die sie halten. Beide Hälften kommen aus
#: ``cities.py`` — eine neue Stadt mit Stundenzusage taucht hier von selbst auf.
#: Fehlt eine Hälfte, bleibt der Satz trotzdem ein Satz.
if TERMIN_KURZ and TERMIN_SCHNELL and TERMIN_SCHNELL_ORTE:
    ZUSAGE_SATZ = '%s. %s – in %s in %s.' % (
        ANTWORT_KURZ, TERMIN_KURZ, TERMIN_SCHNELL_ORTE, TERMIN_SCHNELL)
elif TERMIN_KURZ:                                            # pragma: no cover
    ZUSAGE_SATZ = '%s. %s.' % (ANTWORT_KURZ, TERMIN_KURZ)
else:                                                        # pragma: no cover
    ZUSAGE_SATZ = '%s.' % ANTWORT_KURZ


def _zahl_und_einheit(text, kurz=False):
    """``'1–2 Werktagen'`` -> ``(2, 'Werktage')``; ``'24 Stunden'`` -> ``(24, 'h')``.

    Für das Zahlenband der Startseite, das **eine** Zahl hochzählt. Genommen
    wird die **Obergrenze** — eine Zusage ist nur dann wahr, wenn ihr
    ungünstigster Wert stimmt. ``kurz`` liefert „h" statt „Stunden", weil in
    einer Kachel kein Platz für das Wort ist.

    Bis zum 25.08.2026 stand dort ``data-rw-countup="2"`` mit dem Suffix „h" —
    das 2-Stunden-Versprechen ein fünftes Mal, nur animiert statt getippt, und
    deshalb weder von einem Grep noch von der ersten Fassung der Zeitprüfung zu
    finden.
    """
    s = _spanne(text)
    if not s:                                                # pragma: no cover
        return None, ''
    _, bis, einheit = s
    if einheit == 'Stunde':
        return bis, 'h' if kurz else _plural(bis, 'Stunde')
    return bis, _plural(bis, einheit)

# ── Gruppe C, zweiter Teil: vom Inhaber bestätigt (26.08.2026, Angebot am
# 28.09.2026 korrigiert) ─────────────────────────────────────────────────────
#
# **Der Ablauf, den diese Werte beschreiben** — Grundlage 26.08.2026: „Wir geben
# ein Richtangebot direkt, richtiges Angebot 24 Stunden und Besichtigung
# 24–48 Stunden passt." **Punkt 4 hat der Inhaber am 28.09.2026 korrigiert:**
# Es gibt kein schriftliches Angebot erst 24 Stunden nach der Besichtigung —
# das Festpreisangebot liegt bereits **bei** der Besichtigung vor Ort vor.
#
#   1. **sofort**                    Richtpreis über den Preisrechner
#                                     (``RECHNER_DAUER``)
#   2. **2 Stunden**                 Antwort auf die Anfrage (``ANTWORT``)
#   3. **ab morgen**                 Besichtigungstermin buchbar
#                                     (``TERMIN_FRUEHESTENS``; der frühere
#                                     ``BESICHTIGUNG_VORLAUF`` ist ersetzt)
#   4. **direkt bei der Besichtigung**  Festpreisangebot vor Ort
#                                     (``ANGEBOT_BEI_BESICHTIGUNG``)
#
# Der **Termin vor Ort für die Räumung** ist davon getrennt und steht je Stadt
# in ``cities.py`` (``TERMIN_*``) — er reicht bis 1–2 Werktage (EIG147). Wer eine dieser
# Zahlen ändert, prüft, ob die Reihenfolge noch stimmt: Ein Angebot kann nicht
# vor der Besichtigung liegen, auf die es sich bezieht.

#: Wann das schriftliche Festpreisangebot vorliegt: **bei** der Besichtigung,
#: nicht erst danach. Bewusst ein Text, keine Zahl-Einheit-Spanne — es ist
#: kein Zeitraum, sondern ein Zeitpunkt. Bestätigt vom Inhaber am 28.09.2026;
#: ersetzt die bis dahin geltende 24-Stunden-Frist vom 26.08.2026, die dieselbe
#: Konstante unter dem Namen ``ANGEBOT_NACH_BESICHTIGUNG`` trug. Weil der Text
#: keine Zeitspanne ist, taucht er in ``erlaubte_zeitangaben()`` nicht auf und
#: bleibt von ``_spanne()`` unberührt — richtig so, ``check_seo`` prüft nur
#: Zahl-Einheit-Zusagen gegen dieses Modul.
ANGEBOT_BEI_BESICHTIGUNG = 'direkt bei der Besichtigung'
#: ALTZUSAGE (Vorlauf bis zum Besichtigungstermin, bestätigt am 26.08.2026) —
#: ersetzt durch TERMIN_FRUEHESTENS am 01.10.2026. Steht nur noch als
#: Dokumentation hier: weder in ``erlaubte_zeitangaben()`` noch im Context.
BESICHTIGUNG_VORLAUF = '24–48 Stunden'

#: Wie lange der Preisrechner dauert. **Keine Zusage an einen Kunden**, sondern
#: eine Aussage über die eigene Oberfläche — sie steht hier trotzdem, weil sie
#: dieselbe Krankheit hatte: Am 25.08.2026 nannte die Website für **denselben**
#: Rechner **drei** Dauern nebeneinander — „60 Sekunden" an 14 Stellen,
#: „2 Minuten" in den Beschreibungen der 54 Stadtseiten und „zwei Minuten" in
#: einer FAQ-Antwort. Gefunden hat das die Zeitprüfung, nachdem „Minute" und
#: „Sekunde" in die Einheitentabelle aufgenommen wurden.
#:
#: Gewählt ist die **häufigste** Form, nicht die schnellste: Sie stand an 14 von
#: 16 Stellen, das ist die kleinste Änderung an der sichtbaren Seite.
RECHNER_DAUER = '60 Sekunden'

#: Wie lange die Besichtigung vor Ort dauert (Bauplan §5, Terminbuchung).
#: **Keine Zusage an einen Kunden**, dieselbe Kategorie wie ``RECHNER_DAUER`` -
#: eine Aussage über die eigene Oberfläche, kein Versprechen über den Betrieb.
#: Die Zahl ist an ``apps/core/termine.py::SLOT_DAUER_MINUTEN`` gebunden (ein
#: Modul unter ``data/`` darf ``apps.core`` nicht importieren, Regel 4 - die
#: Übereinstimmung hält deshalb ein Test in ``test_termine.py``, kein Import).
BESICHTIGUNG_DAUER = '25 Minuten'

# ── Gruppe C, dritter Teil: vom Inhaber beauftragt (01.10.2026) ─────────────

#: Ab wann ein Besichtigungstermin gebucht werden kann: **ab morgen**, also jeder
#: freie Slot ab dem nächsten Kalendertag 00:00 (Europe/Berlin), Montag bis Samstag,
#: ohne Sonn- und Feiertage. Im Auftrag des Inhabers, 01.10.2026. Das ist
#: die **Buchbarkeit im Kalender**, kein Versprechen, dass Oliver am Folgetag
#: kommt: ob ein Tag frei ist, zeigt der Kalender selbst. ``termine.py`` rechnet
#: danach (``fruehester_termin``) - ``BESICHTIGUNG_VORLAUF`` steuert den Kalender
#: seitdem nicht mehr. Ein Text, keine Zahl-Einheit-Spanne: taucht deshalb nicht
#: in ``erlaubte_zeitangaben()`` auf.
TERMIN_FRUEHESTENS = 'ab morgen'

#: Wann das Festpreisangebot bei einer **Video-Besichtigung** (WhatsApp-Videoanruf)
#: vorliegt. Im Auftrag des Inhabers, 01.10.2026. Gilt nur unter der
#: Bedingung, dass alle Räume im Videoanruf gezeigt wurden - die Bedingung steht
#: im sichtbaren Satz neben dieser Konstante, nicht in ihr (der Wortlaut hier ist
#: der Zeitpunkt). Gegenstück zu ``ANGEBOT_BEI_BESICHTIGUNG`` (vor Ort).
ANGEBOT_NACH_VIDEO = 'direkt im Anschluss an den Videoanruf'


def response_verteilung():
    """Wie viele Stadtseiten welche Terminzusage (``c['response']``) tragen.

    ``{'1 Werktag': 48, '1–2 Werktage': 5, …}`` — gezählt über **alle** Städte
    in ``cities.py``, also über genau die Seiten, die es gibt. Ersetzt die
    getippten Zahlen im Modulkopf (EIG399): Wer eine Zahl braucht, ruft das
    hier auf, statt sie abzuschreiben.
    """
    aus = {}
    for c in _CITY_DATA.values():
        r = c.get('response')
        if r:
            aus[r] = aus.get(r, 0) + 1
    return dict(sorted(aus.items(), key=lambda kv: (-kv[1], kv[0])))


def erlaubte_zeitangaben():
    """Jede Zeitangabe, die im sichtbaren Text einer Zusage stehen darf.

    Normalisiert auf ``'<von>-<bis> <Einheit>'``, damit ``2–4 Stunden`` und
    ``2-4 Stunden`` (Bindestrich statt Halbgeviertstrich) denselben Eintrag
    treffen. Speist die Prüfung in ``check_seo``.

    **Enthält auch die Zusagen der einzelnen Städte** — eine Stadtseite darf
    ihre eigene, engere Zusage nennen, und die Matrixseiten reichen sie durch.
    """
    aus = set()

    def merke(text, zerlegt=False):
        s = _spanne(text)
        if not s:
            return
        _, bis, einheit = s
        aus.add('%d-%d %s' % s)
        # ``zerlegt`` nur fuer die beiden Werte, die dieses Modul auch
        # **zerlegt ausliefert**: Das Zahlenband der Startseite zeigt aus
        # "1-2 Werktagen" die Zahl 2 mit der Einheit daneben (siehe
        # ``_zahl_und_einheit``). Ohne diese Zeile meldete die Pruefung ihre
        # eigene Ausgabe als quellenlos.
        #
        # **Und nur fuer die beiden.** Wuerde jede Stadtzusage zerlegt, waere
        # aus Tauchas "1-2 Stunden" auch "2 Stunden" allein erlaubt - und
        # damit genau das Versprechen wieder offen, wegen dem dieses Modul
        # existiert. Nachgemessen: Mit der breiten Variante lief die
        # Gegenprobe "Rueckmeldung in 2h" durch.
        if zerlegt:
            aus.add('%d-%d %s' % (bis, bis, einheit))

    merke(ANTWORT)
    merke(TERMIN_SCHNELL)
    # BESICHTIGUNG_VORLAUF ist seit 01.10.2026 bewusst kein ``merke(...)`` mehr:
    # ersetzt durch TERMIN_FRUEHESTENS. So meldet check_seo ein eingeschlepptes
    # "24–48 Stunden" als quellenlose Zeitzusage.
    merke(RECHNER_DAUER)
    merke(BESICHTIGUNG_DAUER)
    merke(TERMIN_REGEL, zerlegt=True)
    # ANGEBOT_BEI_BESICHTIGUNG ist bewusst kein ``merke(...)`` mehr: Seit
    # 28.09.2026 ist die Zusage ein Zeitpunkt ("direkt bei der Besichtigung"),
    # keine Zahl-Einheit-Spanne mehr - ``_spanne()`` faende darin ohnehin
    # nichts. Die alte Zeile mit ``ANGEBOT_NACH_BESICHTIGUNG`` ist deshalb
    # ersatzlos entfernt, nicht auf die neue Konstante umgestellt.
    for c in _CITY_DATA.values():
        merke(c.get('response'))
    return aus


def zusagen_context():
    """Was der Context-Processor in jede Vorlage legt."""
    # Das Zahlenband der Startseite zeigt die **Antwortzeit** — sie ist die
    # Zusage, die überall gilt. Bis zum 25.08. zählte es auf 2 h hoch, was
    # richtig war; am 25.08. wurde es auf die Termin-Spanne umgestellt, was
    # falsch war. Jetzt wieder die Antwortzeit, aber aus einer Quelle.
    antwort_zahl, antwort_einheit = _zahl_und_einheit(ANTWORT, kurz=True)
    return {
        # **Die Zusage, die überall gilt** — sie steht in Trustbar, Kacheln
        # und Hero. Bis zum 26.08. lag hier die Termin-Spanne, und damit sagte
        # die Startseite „Rückmeldung in 1–2 Werktagen", obwohl binnen zwei
        # Stunden geantwortet wird.
        'ZUSAGE_ANTWORT': ANTWORT_KURZ,
        # Die blanke Spanne fuer Saetze, die ihr eigenes „in …" mitbringen:
        # „Wir melden uns in {{ ZUSAGE_ANTWORT_SPANNE }} zurueck."
        'ZUSAGE_ANTWORT_SPANNE': ANTWORT,
        # Wann sie gilt (EIG394, 02.10.2026): rund um die Uhr, nicht nur in
        # den Geschaeftszeiten.
        'ZUSAGE_ANTWORT_GILT': ANTWORT_GILT,
        'ZUSAGE_REAKTION': ANTWORT_KURZ,
        'ZUSAGE_REAKTION_SATZ': ZUSAGE_SATZ,
        # Der **Termin vor Ort**, hergeleitet aus cities.py.
        'ZUSAGE_TERMIN': TERMIN_KURZ,
        'ZUSAGE_REAKTION_SPANNE': TERMIN_REGEL or '',
        'ZUSAGE_REAKTION_SCHNELL': TERMIN_SCHNELL or '',
        # Die vier Städte mit Stundenzusage als fertiger Text (S5).
        'ZUSAGE_SCHNELL_ORTE': TERMIN_SCHNELL_ORTE,
        # Seit 28.09.2026 ein Zeitpunkt ("direkt bei der Besichtigung"),
        # keine Frist mehr - deshalb kein ZUSAGE_ANGEBOT_ZAHL/_EINHEIT mehr:
        # Es gibt keine Zahl mehr, die ein Zahlenband hochzaehlen koennte.
        'ZUSAGE_ANGEBOT': ANGEBOT_BEI_BESICHTIGUNG,
        'ZUSAGE_RECHNER': RECHNER_DAUER,
        'ZUSAGE_BESICHTIGUNG_DAUER': BESICHTIGUNG_DAUER,
        'ZUSAGE_TERMIN_FRUEHESTENS': TERMIN_FRUEHESTENS,
        'ZUSAGE_ANGEBOT_VIDEO': ANGEBOT_NACH_VIDEO,
        # Zerlegt für das Zahlenband der Startseite, das hochzählt.
        'ZUSAGE_REAKTION_ZAHL': antwort_zahl,
        'ZUSAGE_REAKTION_EINHEIT': antwort_einheit,
    }
