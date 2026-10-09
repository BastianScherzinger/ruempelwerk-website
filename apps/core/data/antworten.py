# -*- coding: utf-8 -*-
"""Antwort-zuerst-Bloecke (G2) - **eine** Quelle je Antwort.

**Warum es dieses Modul gibt.** Generative Systeme zitieren Textpassagen, nicht
Seiten. Eine Passage, die die Frage in zwei Saetzen vollstaendig beantwortet,
ist zitierbar; ein Absatz, der mit "Seit vielen Jahren stehen wir fuer
Qualitaet..." beginnt, ist es nicht. Dasselbe Format gewinnt nebenbei Featured
Snippets in der klassischen Suche - eine Massnahme, zwei Kanaele.

**Was hier NICHT steht: die Antworten der Leistungs- und Matrixseiten.** Die
liegen seit jeher als ``answer`` in ``services.py`` und ``matrix.py`` und
speisen von dort ``/llms.txt`` und ``/llms-full.txt``. Sie hier noch einmal
aufzuschreiben waere die zweite Textquelle, gegen die Regel 12 geschrieben ist.
Dieses Modul liefert nur, was es noch nicht gab: den Antworttext der **54
Stadtseiten**, der beiden Hubs und der Startseite.

**Die sechs Regeln aus BLOCK-3-GEO.md, Abschnitt G2:**

1. 40-60 Woerter. Kuerzer ist zu duenn, laenger wird nicht am Stueck zitiert.
2. Der **erste Satz** beantwortet die Frage vollstaendig - kein Aufbau.
3. Mindestens eine konkrete Zahl.
4. Firmenname im Satz, sonst wird die Antwort ohne Nennung uebernommen.
5. Datum dabei (Preisstand).
6. Direkt unter der H1.

**Regel 2 heisst nicht "der erste Satz nennt den Preis".** Genau das stand hier
bis zum 01.09.2026, und es hat nicht funktioniert: Die GEO-Messung Nr. 1
(27.08.2026) brachte drei Website-Zitate - alle drei auf **Leistungs**seiten,
keines auf einer der 54 Stadtseiten. Der Unterschied steht im ersten Satz.

    zitiert       "Eine Kellerentruempelung **ist** die Teilraeumung eines
                  Kellers, Dachbodens oder Nebengelasses ..."
    nicht zitiert "Eine Entruempelung in Halle (Saale) **kostet** bei
                  Ruempelwerk Mitteldeutschland **ab 300 EUR** ..."

Das eine ist ein Faktum, das andere ein Angebot. Eine Antwortmaschine zitiert
Fakten; was Perplexity aus ``/nachlassraeumung/`` uebernommen hat, waren
Ablaufschritte und Abgrenzungen ("Dokumente sichern", "besenreine Uebergabe"),
die Preise erst danach. **Der Preis bleibt deshalb im Block - aber im zweiten
Satz.**

**Die Falle, die dieses Modul teuer machen koennte.** 54 Bloecke mit demselben
Satzbau erhoehen die Aehnlichkeit der Stadtseiten - und genau die war der
Grund, aus dem Google 38 von 54 nicht indexiert hat. Der Jaccard-Median stand
am 27.08.2026 bei **0,782**, das Ziel aus P1b bei unter 0,80.

**Vier Satzbauten waren dagegen zu wenig, und zwar messbar an der falschen
Stelle.** Am 01.09.2026 nachgemessen (``P1-halle.md``, Befund 2): Nach Ersetzen
der Eigennamen erzeugten die vier Bauten auf **54 von 54** Seiten **genau eine**
Schablone im ersten Satz - sie unterschieden erst den **dritten**. Der erste ist
der, der zitiert wird. Seitdem waehlen **zwei unabhaengige Merkmale** den Text:

* den **Eroeffnungssatz** die Objektarten, fuer die ``city_lokal.py`` dieser
  Stadt Rechenbeispiele fuehrt (fuenf Bauten). Sie sind aus dem recherchierten
  Gebaeudebestand abgeleitet, nicht gepflegt - und sie schneiden **quer zur
  Geografie**: Zwei Nachbarstaedte, die sich sonst am aehnlichsten sind,
  bekommen verschiedene erste Saetze.
* den **Schlusssatz** wie bisher die Lage (Standort / schnelle Stadt /
  Regelstadt / Randgebiet).

Gefuellt werden beide mit dem einzigen Vokabular, das eine Stadtseite mit keiner
anderen teilt: Ortsteilnamen aus ``city_lokal.py``, Entfernung zum Standort,
``response``. **Die Ortsteile stehen im ersten Satz**, nicht in einem Nachsatz -
sie sind das, was diese Antwort von 53 anderen unterscheidet.

Nach jeder Aenderung an den Satzbauten gehoert ``jaccard_staedte.py`` gelaufen
und die Zahl ins Logbuch.

**Jede Zahl kommt aus ``pricing.py`` (Regel 1), jede Zeitangabe aus
``zusagen.py`` bzw. ``cities.py`` (Regel 24).** ``check_seo`` prueft beides,
sobald der Block sichtbar ist.

Das Modul importiert nichts aus ``apps.core`` (Regel 4).
"""

from .cities import REGIONEN as _REGIONEN, entfernung_zum_standort as _entfernung
from .firma import FIRMA as _FIRMA, INHABER as _INHABER, ORT as _ORT
from .pricing import _MALER_PER_QM, _PER_QM_PREISE, _PREISSTAND, euro as _euro
from .zusagen import (ANGEBOT_BEI_BESICHTIGUNG as _ANGEBOT, ANTWORT as _ANTWORT,
                      TERMIN_FRUEHESTENS as _BESICHTIGUNG,
                      RECHNER_DAUER as _RECHNER, TERMIN_REGEL as _TERMIN_REGEL,
                      TERMIN_SCHNELL as _TERMIN_SCHNELL,
                      TERMIN_SCHNELL_ORTE as _SCHNELL_ORTE)

__all__ = ['stadt_antwort', 'hub_antwort', 'start_antwort', 'seiten_antwort',
           'job_antwort', 'rechner_antwort', 'wortzahl']

# Die Zahlen, die in jeder Antwort vorkommen - aus pricing.py, nie getippt.
_AB_KELLER = _euro(_PER_QM_PREISE['keller']['min_preis'])
_AB_HAUS = _euro(_PER_QM_PREISE['haus']['min_preis'])
_AB_MALER = _euro(_MALER_PER_QM['min_preis'])
_RATE_WOHNUNG = _PER_QM_PREISE['wohnung']['rate']
_RATE_HAUS = _PER_QM_PREISE['haus']['rate']
_RATE_KELLER = _PER_QM_PREISE['keller']['rate']
_RATE_GEWERBE = _PER_QM_PREISE['gewerbe']['rate']
_RATE_SCHEUNE = _PER_QM_PREISE['scheune']['rate']
_RATE_GARTEN = _PER_QM_PREISE['garten']['rate']


def wortzahl(text):
    """Woerter eines Antworttextes - das Mass, an dem G2 haengt (40-60)."""
    return len([w for w in text.split() if any(z.isalnum() for z in w)])


def _ortsteile(lokal, anzahl=3):
    """Die ersten Ortsteile einer Stadt, als Aufzaehlung mit 'und'.

    Ortsteilnamen sind das einzige Vokabular, das eine Stadtseite mit keiner
    anderen teilt (siehe city_lokal.py). Sie sind hier der wichtigste Beitrag
    gegen die Aehnlichkeit - und zugleich echte Suchanfragen
    ("Entruempelung Leipzig Plagwitz").
    """
    namen = list((lokal or {}).get('ortsteile') or [])[:anzahl]
    if not namen:
        return ''
    if len(namen) == 1:
        return namen[0]
    return '%s und %s' % (', '.join(namen[:-1]), namen[-1])


# ── Satz 1: was eine Entruempelung in DIESER Stadt ueberhaupt umfasst ───────
#
# **Woher die fuenf Bauten kommen - und warum gerade daher.** Gesucht war ein
# Merkmal, das (a) je Stadt recherchiert ist, (b) niemand zusaetzlich pflegen
# muss und (c) **quer zur Geografie schneidet**: Zwei Nachbarstaedte sind sich
# ohnehin am aehnlichsten (Merseburg ist mit 0,804 die Halle-aehnlichste von 53
# Seiten), sie duerfen also nicht auch noch denselben Satzbau bekommen.
#
# Das Merkmal ist die Menge der ``objektart``-Werte in ``beispiele`` von
# ``city_lokal.py``. Diese Beispiele sind aus dem recherchierten
# ``bebauung``-Text abgeleitet - eine Stadt mit Scheunen bekommt ein
# Scheunen-Beispiel, eine mit Gewerbebrachen ein Gewerbe-Beispiel. Gemessen am
# 01.09.2026: **acht verschiedene Signaturen** ueber die 54 Staedte, und sie
# folgen dem Gebaeudebestand, nicht der Entfernung.
#
# **Die Reihenfolge ist eine Rangfolge, kein Zufall.** Eine Stadt kann mehrere
# Merkmale tragen; genannt wird das **seltenere**, weil es mehr ueber sie sagt.
# 'keller' steht deshalb hinten: Keller hat fast jede Stadt.
_SATZBAU_ORDNUNG = ('gewerbe', 'scheune', 'garten', 'keller')

#: Der Eroeffnungssatz je Bau. **Kein Preis, kein Firmenname** - beides steht im
#: zweiten Satz. Und die Ortsteile stehen *im* Satz, nicht dahinter.
_EROEFFNUNG = {
    'gewerbe':
        'Eine Entrümpelung in %(name)s betrifft Wohnungen und Häuser ebenso '
        'wie Büros, Lager und Ladenlokale – von %(orte)s bis in die '
        'Gewerbelagen.',
    'scheune':
        'Eine Entrümpelung in %(name)s umfasst neben Wohnung und Haus '
        'regelmäßig auch Scheune, Stall und Nebengebäude – in %(orte)s wie in '
        'den Ortslagen ringsum.',
    'garten':
        'Eine Entrümpelung in %(name)s reicht von der Wohnung über das Haus '
        'bis zum Gartengrundstück mit Laube und Schuppen – in %(orte)s und im '
        'Umland.',
    'keller':
        'Eine Entrümpelung in %(name)s reicht vom Kellerabteil bis zur '
        'kompletten Räumung von Wohnung oder Haus – in %(orte)s wie in den '
        'übrigen Ortsteilen.',
    'wohnraum':
        'Eine Entrümpelung in %(name)s ist die vollständige Räumung von '
        'Wohnung oder Haus samt Möbeln, Hausrat und Elektrogeräten – in '
        '%(orte)s wie im übrigen Stadtgebiet.',
}

#: Satz 2 - hier steht der Preis, und hier steht der Firmenname (Regel 4 der
#: sechs G2-Regeln). Genannt wird der **Richtwert der Objektarten, die diese
#: Stadt wirklich hat**: Ein Ort mit Scheunen erfaehrt den Scheunensatz, kein
#: Ort erfaehrt eine Zahl, die auf ihn nicht passt. Jede Zahl aus pricing.py
#: (Regel 1); die Mindestpauschale ``_AB_KELLER`` gilt objektartunabhaengig und
#: steht deshalb ueberall.
_PREISSATZ = {
    'gewerbe':
        'Rümpelwerk Mitteldeutschland übernimmt sie zum Festpreis ab %s €, '
        'Richtwert %s €/m² (Wohnung) und %s €/m² (Gewerbe).'
        % (_AB_KELLER, _RATE_WOHNUNG, _RATE_GEWERBE),
    'scheune':
        'Rümpelwerk Mitteldeutschland übernimmt sie zum Festpreis ab %s €, '
        'Richtwert %s €/m² (Nebengebäude) und %s €/m² (Haus).'
        % (_AB_KELLER, _RATE_SCHEUNE, _RATE_HAUS),
    'garten':
        'Rümpelwerk Mitteldeutschland übernimmt sie zum Festpreis ab %s €, '
        'Richtwert %s €/m² (Grundstück) und %s €/m² (Wohnung).'
        % (_AB_KELLER, _RATE_GARTEN, _RATE_WOHNUNG),
    'keller':
        'Rümpelwerk Mitteldeutschland übernimmt sie zum Festpreis ab %s €, '
        'Richtwert %s €/m² (Keller) und %s €/m² (Wohnung).'
        % (_AB_KELLER, _RATE_KELLER, _RATE_WOHNUNG),
    'wohnraum':
        'Rümpelwerk Mitteldeutschland übernimmt sie zum Festpreis ab %s €, '
        'Richtwert %s €/m² (Wohnung) und %s €/m² (Haus).'
        % (_AB_KELLER, _RATE_WOHNUNG, _RATE_HAUS),
}


def _objektarten(lokal):
    """Die ``objektart``-Werte der Rechenbeispiele dieser Stadt.

    Leere Menge, wenn eine Stadt keine Beispiele hat - dann greift der
    Grundbau. Das ist heute (01.09.2026) auf keiner der 54 Seiten der Fall,
    aber ein fehlendes Feld darf hier nie eine Ausnahme werfen: Dieses Modul
    wird beim Rendern **jeder** Stadtseite aufgerufen.
    """
    return {(b.get('args') or {}).get('objektart')
            for b in ((lokal or {}).get('beispiele') or ())}


def _satzbau(lokal):
    """Welcher Eroeffnungssatz greift - abgeleitet, nicht gepflegt."""
    arten = _objektarten(lokal)
    for art in _SATZBAU_ORDNUNG:
        if art in arten:
            return art
    return 'wohnraum'


def stadt_antwort(city, lokal=None):
    """(Frage, Antworttext) fuer eine Stadtseite.

    **Zwei Achsen, nicht eine** - siehe Modul-Docstring. Bis zum 01.09.2026
    entschied allein die Lage, und sie entschied erst ueber den *dritten* Satz;
    der erste war auf allen 54 Seiten derselbe. Jetzt gilt:

    * **Satz 1** waehlt ``_satzbau()`` nach den Objektarten der Stadt
      (``gewerbe`` / ``scheune`` / ``garten`` / ``keller`` / ``wohnraum``).
      Er **definiert**, statt anzubieten, und traegt die Ortsteile.
    * **Satz 2** nennt Firma und Preis, mit den Richtwerten der Objektarten,
      die diese Stadt hat.
    * **Satz 3** waehlt die Lage, wie bisher:

      - **Randgebiet** (Raum Hannover): kein Tempoversprechen. Diese Staedte
        werden nur bei groesseren Auftraegen angefahren; eine kurze Zusage
        erzeugte dort Anfragen, die abgesagt werden muessen.
      - **Standort** (``entfernung_zum_standort`` ist None): Team vor Ort.
      - **schnelle Stadt** (``response`` in Stunden): darf mit Tempo werben.
      - **Regelstadt**: Entfernung und Termin nuechtern nennen.

    ``response`` ist der **Termin vor Ort**, nicht die Antwortzeit - die beiden
    sind am 25.08.2026 schon einmal verwechselt worden (Regel 24). Deshalb
    steht hier nie "Antwort in", sondern immer "Termin vor Ort".

    **Die Laenge ist das Nadeloehr.** 40-60 Woerter, und dabei zaehlt der
    Stadtname je nach Ort ein oder zwei Woerter ("Halle (Saale)") und ein
    Ortsteilname ebenso ("Stadtfeld Ost"). Gemessen am 01.09.2026 ueber alle
    54 Seiten: **53-59 Woerter**, engste Reserve **einer**. Wer einen der Bauten
    verlaengert, misst mit ``wortzahl()`` aus diesem Modul nach - eine Pruefung,
    die das Band automatisch haelt, gibt es nicht.
    """
    name = city['name']
    frage = 'Was kostet eine Entrümpelung in %s?' % name
    orte = _ortsteile(lokal)
    km = _entfernung(city)
    # Dativ ("in 1–2 Werktagen") aus zusagen.response_dativ (EIG153); der
    # Stunden-Test unten liest dieselbe Form.
    termin = city.get('response_dativ') or city.get('response') or ''
    branch = city.get('branch') or ''
    bau = _satzbau(lokal)

    if orte:
        kopf = _EROEFFNUNG[bau] % {'name': name, 'orte': orte}
    else:
        # Ohne Ortsteile faellt der Satz auf die Region zurueck - er soll nicht
        # "in  und im ganzen Stadtgebiet" lauten. Heute betrifft das keine
        # Stadt; das Feld kann aber jederzeit fehlen (city_lokal.py laesst
        # Felder bewusst leer, statt sie zu raten).
        kopf = (_EROEFFNUNG[bau] % {'name': name,
                                    'orte': city.get('region') or city['state']})

    preis = _PREISSATZ[bau]

    if city.get('randgebiet'):
        schluss = ('%s liegt im erweiterten Einsatzgebiet: Termin nach '
                   'Absprache, Festpreisangebot %s.'
                   % (name, _ANGEBOT))
    elif km is None:
        # 02.10.2026: kein "Team sitzt in X" - belegt ist nur die Betriebsstaette
        # in Halle (firma.py); die uebrigen Kernstaedte sind Einsatzgebiet.
        schluss = ('%s liegt im Kerngebiet – Termin vor Ort in %s.'
                   % (name, termin))
    else:
        schluss = ('Entfernung zu %s: %d km, Termin vor Ort in %s.'
                   % (branch, km, termin))

    text = '%s %s %s Preisstand: %s.' % (kopf, preis, schluss, _PREISSTAND)
    return frage, text


# ── Die beiden Hubs ─────────────────────────────────────────────────────────
#
# /entrumpelung/ und /dienstleistungen/ standen bis zum 27.08.2026 ohne
# Antwortblock da - beides Seiten mit echtem Erklaerbedarf, auf die G9 mangels
# Alternative den Hero-Lead als 'speakable' gesetzt hat.
_HUBS = {
    'entrumpelung': (
        'Was kostet eine Entrümpelung?',
        'Eine Entrümpelung kostet bei Rümpelwerk Mitteldeutschland ab {ab} € '
        'zum Festpreis; der Richtwert liegt bei {wohnung} €/m² für Wohnungen '
        'und {haus} €/m² für Häuser. Enthalten sind Transport, '
        'Entsorgungsgebühren und Arbeitslohn, die Übergabe erfolgt besenrein. '
        'Die Besichtigung ist kostenlos, das Festpreisangebot gibt es '
        '{angebot}. Preisstand: {stand}.'
    ),
    'dienstleistungen': (
        'Welche Leistungen bietet Rümpelwerk Mitteldeutschland an?',
        'Rümpelwerk Mitteldeutschland übernimmt Entrümpelung, '
        'Haushaltsauflösung, Wohnungsauflösung, Kellerentrümpelung, '
        'Nachlassräumung, Gewerbeentrümpelung, Messie-Wohnungen, '
        'Sperrmüllentsorgung sowie Sanierung und Renovierung – in Sachsen, '
        'Sachsen-Anhalt und Niedersachsen. Die Räumungen gibt es zum '
        'Festpreis ab {ab} €, Malerarbeiten ab {maler_min} €, besenrein '
        'übergeben. Den Festpreis nennen wir '
        'nach der kostenlosen Besichtigung, verbindlich im Angebot. '
        'Preisstand: {stand}.'
    ),
}


def hub_antwort(schluessel):
    """(Frage, Antworttext) fuer /entrumpelung/ oder /dienstleistungen/."""
    eintrag = _HUBS.get(schluessel)
    if not eintrag:
        return None, None
    frage, muster = eintrag
    return frage, muster.format(
        ab=_AB_KELLER, maler_min=_AB_MALER, wohnung=_RATE_WOHNUNG,
        haus=_RATE_HAUS, angebot=_ANGEBOT, stand=_PREISSTAND)


def start_antwort():
    """(Frage, Antworttext) der Startseite.

    Die Suchanfrage mit den meisten Impressionen ist die nach dem Preis - und
    die Startseite faengt sie heute ab, statt die Stadtseite ranken zu lassen
    (MESSUNG-2026-08-21.md, Befund zu Halle). Also beantwortet sie sie auch.
    """
    return (
        'Was kostet eine Entrümpelung oder Haushaltsauflösung?',
        'Eine Entrümpelung kostet bei Rümpelwerk Mitteldeutschland ab %s € '
        'zum Festpreis, eine komplette Haushaltsauflösung ab %s €. Der '
        'Richtwert liegt bei %s €/m² für Wohnungen und %s €/m² für Häuser, '
        'inklusive Transport, Entsorgung und besenreiner Übergabe. Die '
        'Besichtigung ist kostenlos, das verbindliche Angebot gibt es '
        '%s. Preisstand: %s.'
        % (_AB_KELLER, _AB_HAUS, _RATE_WOHNUNG, _RATE_HAUS,
           _ANGEBOT, _PREISSTAND)
    )


# ── Die Seiten ohne Leistung (16.09.2026) ───────────────────────────────────
#
# Die Messung vom 15.09.2026 (GE23, kritisch) fand zehn Seiten, deren
# erste drei Absaetze weder eine Zahl noch eine Festlegung tragen: Standorte,
# Ueber uns, Aktuelles, Galerie, Jobs, Kooperation, die Stellenanzeigen und
# der Preisrechner. Es sind Seiten ohne eigene Leistung - aber jede beantwortet
# eine Frage, die jemand stellt ("Wo seid ihr?", "Wer seid ihr?"), und genau
# diese Antwort steht jetzt oben.
#
# Dieselben sechs Regeln wie oben. Keine Aussage hier, die nicht schon an
# anderer Stelle der Website belegt steht: Regionen aus cities.py, Firmendaten
# aus firma.py, Zusagen aus zusagen.py, Preise aus pricing.py, Gehaelter aus
# jobs.py. **Nichts davon ist neu behauptet** - neu ist nur, dass es oben steht.

def _liste(namen):
    """'a, b und c' - fuer die Aufzaehlung der Regionen und Stellen."""
    namen = list(namen)
    if len(namen) < 2:
        return ''.join(namen)
    return '%s und %s' % (', '.join(namen[:-1]), namen[-1])


def seiten_antwort(schluessel, staedte=None):
    """(Frage, Antworttext) fuer eine der Seiten ohne Leistung.

    ``staedte`` braucht nur ``standorte``: die Zahl der Orte, die die Seite
    darunter auflistet. Sie kommt aus der View, weil sie dort ohnehin gezaehlt
    wird - eine zweite Zaehlung hier koennte von der sichtbaren Liste abweichen.
    """
    regionen = len(_REGIONEN)
    if schluessel == 'standorte':
        return (
            'Wo ist Rümpelwerk Mitteldeutschland im Einsatz?',
            'Das Einsatzgebiet von %s umfasst %s Orte in Sachsen, '
            'Sachsen-Anhalt und Niedersachsen, betreut aus %s Regionen mit je '
            'einem festen Ansprechpartner: %s. Anfragen beantworten wir überall binnen %s; '
            'ein Termin vor Ort ist in der Regel in %s möglich, in %s schon in '
            '%s. Die Besichtigung ist kostenlos.'
            % (_FIRMA, staedte, regionen, _liste(_REGIONEN), _ANTWORT,
               _TERMIN_REGEL, _SCHNELL_ORTE, _TERMIN_SCHNELL)
        )
    if schluessel == 'ueber_uns':
        return (
            'Wer steht hinter Rümpelwerk Mitteldeutschland?',
            '%s ist ein inhabergeführter Entrümpelungsbetrieb von %s mit Sitz '
            'in %s. Das Team übernimmt Entrümpelungen, Haushaltsauflösungen '
            'und Sanierungen in %s Regionen, jede mit einem festen '
            'Ansprechpartner (in Leipzig und Halle der Inhaber selbst). Gearbeitet wird zum Festpreis ab %s\u00a0€ inkl. MwSt. nach '
            'kostenloser Besichtigung und mit Antwort auf '
            'jede Anfrage binnen %s. Preisstand: %s.'
            % (_FIRMA, _INHABER, _ORT, regionen, _AB_KELLER, _ANTWORT,
               _PREISSTAND)
        )
    if schluessel == 'aktuelles':
        return (
            'Was steht unter „Aktuelles“?',
            'Aktuelles ist das Einsatztagebuch von %s: kurze Berichte aus '
            'abgeschlossenen Entrümpelungen, Haushaltsauflösungen und '
            'Sanierungen, jeweils mit Datum und, wo vorhanden, Fotos vor und '
            'nach der Räumung. Wer selbst räumen lassen möchte: Eine '
            'Entrümpelung kostet ab %s € zum Festpreis, das Angebot gibt es '
            '%s. Preisstand: %s.'
            % (_FIRMA, _AB_KELLER, _ANGEBOT, _PREISSTAND)
        )
    if schluessel == 'galerie':
        return (
            'Was zeigt die Galerie?',
            'Die Galerie zeigt Vorher-Nachher-Fotos aus echten Aufträgen von '
            '%s: Entrümpelungen, Haushaltsauflösungen und Sanierungen, jedes '
            'Bild mit dem Bericht, aus dem es stammt. Die Räume werden '
            'besenrein übergeben, Transport und Entsorgung sind im Festpreis '
            'enthalten. Eine Entrümpelung kostet ab %s\u00a0€ inkl. MwSt., der Richtwert für '
            'Wohnungen liegt bei %s\u00a0€/m². Preisstand: %s.'
            % (_FIRMA, _AB_KELLER, _RATE_WOHNUNG, _PREISSTAND)
        )
    if schluessel == 'kooperation':
        return (
            'Für wen lohnt eine Kooperation mit Rümpelwerk Mitteldeutschland?',
            'Eine Kooperation mit %s lohnt sich für Hausverwaltungen, Makler, '
            'Nachlassverwalter und Handwerksbetriebe, die regelmäßig Objekte '
            'geräumt übergeben müssen. Sie bekommen einen festen '
            'Ansprechpartner, eine Antwort innerhalb von %s, eine Besichtigung, '
            'die %s buchbar ist, '
            'ein Festpreisangebot %s und eine besenreine, '
            'dokumentierte Übergabe. Für vermittelte Aufträge gibt es eine '
            'Tippgeber-Provision.'
            % (_FIRMA, _ANTWORT, _BESICHTIGUNG, _ANGEBOT)
        )
    return None, None


def job_antwort(job, anzahl=None):
    """(Frage, Antworttext) fuer /jobs/ (``job=None``) oder eine Anzeige.

    Die Gehaltszahlen sind die Zeilen aus ``jobs.py``, woertlich - ``check_seo``
    kennt dieses Modul als Quelle (Ausnahmeliste der Preispruefung).
    """
    from .jobs import _JOB_DATA
    if job is None:
        stellen = list(_JOB_DATA.values())
        helfer = _JOB_DATA['entruempelungshelfer']['verdienst'][0]
        leitung = _JOB_DATA['teamleiter']['verdienst'][0]
        return (
            'Welche Stellen bietet Rümpelwerk Mitteldeutschland an?',
            '%s hat derzeit %s Stellen offen: %s. Entrümpelungshelfer: %s. '
            'Das Gehalt als Teamleiter beträgt %s. Vorkenntnisse sind für den '
            'Einstieg nicht nötig, Fahrzeuge und Ausrüstung werden gestellt. '
            'Die Kurzbewerbung weiter unten braucht nur Name, Telefon und '
            'E-Mail.'
            % (_FIRMA, len(stellen), _liste(s['title'] for s in stellen),
               helfer, leitung)
        )
    return (
        'Was bietet die Stelle „%s“?' % job['title'],
        '%s ist eine Stelle bei %s (%s) mit Einsatz in %s. %s. '
        'Aufgaben unter anderem: %s; %s. Voraussetzung: %s.'
        % (job['title'], _FIRMA, job['badge'].replace(' | ', ', '),
           job['orte'].replace(' · ', ', '), job['verdienst'][0],
           job['aufgaben'][0], job['aufgaben'][1],
           job['voraussetzungen'][0].rstrip('.'))
    )


def rechner_antwort():
    """Der Hero-Satz des Preisrechners - dort, nicht als eigener Block.

    Auf /preisangebot/ steht der Rechner direkt unter dem Hero; ein Block
    dazwischen schoebe das Werkzeug, fuer das die Seite da ist, nach unten.
    Deshalb traegt hier der Hero-Absatz die Antwort.
    """
    return (
        'Der Preisrechner von %s zeigt in %s einen Richtpreis für Ihre '
        'Entrümpelung, Haushaltsauflösung oder Sanierung – kostenlos, nach '
        'Angabe von Name und E-Mail. Eine Entrümpelung kostet ab %s\u00a0€, Wohnungen rund %s\u00a0€/m². '
        'Den verbindlichen Festpreis bekommen Sie nach der kostenlosen '
        'Besichtigung. Preisstand: %s.'
        % (_FIRMA, _RECHNER, _AB_KELLER, _RATE_WOHNUNG, _PREISSTAND)
    )


def anfrage_faq():
    """GE17 (19.09.2026): Frage und Antwort ueber dem Ablauf auf /anfrage/.

    Die Frage ist die Ueberschrift des Abschnitts ``#nach-der-anfrage``, die
    Antwort der Satz direkt darunter. Die Ueberschrift steht im Template
    ``anfrage.html`` (wegen ihres ``<em>``), der Satz wird seit dem 01.10.2026
    aus diesem Wert gerendert (``{{ nach_anfrage_antwort }}`` aus
    ``views._anfrage_ctx``, EIG368). ``AntwortblockFaqTests`` und
    ``AnfrageAblaufAusEinerQuelleTests`` halten die Wortlaute gegen den
    sichtbaren Text.
    """
    return (
        'Wie geht es nach Ihrer Anfrage weiter?',
        'Vier Schritte, keine Vorkasse – und bis zum schriftlichen Angebot '
        'bleibt alles unverbindlich.',
    )


def rechner_faq():
    """GE17 (19.09.2026): Die Frage des ersten Rechnerschritts auf /preisangebot/.

    Ueberschrift und Satz stehen in ``components/rw_rechner.html`` (Schritt 1).
    Die Komponente ist auf 69 Seiten eingebunden, deshalb bleibt ihr Text dort;
    ausgezeichnet wird das Paar nur auf /preisangebot/ - die uebrigen Seiten
    haben eine eigene FAQPage. ``AntwortblockFaqTests`` haelt den Wortlaut
    gegen den sichtbaren Text.
    """
    return (
        'Um welche Objektart handelt es sich?',
        'Wählen Sie die Art des Objekts, das entrümpelt oder geräumt werden soll.',
    )


#: Pfad -> Paar fuer die Seiten ohne Antwortblock, aber mit sichtbarer Frage.
#: Gelesen von ``templatetags/rw_schema.py::rw_head_schema`` (GE17).
FORMULAR_FAQ = {
    '/anfrage/': anfrage_faq,
    '/preisangebot/': rechner_faq,
}
