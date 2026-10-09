# -*- coding: utf-8 -*-
"""Ratgeberartikel unter ``/ratgeber/<slug>/`` - Wissensseiten als Daten (T4-T8).

**Warum es dieses Modul gibt.** Die Messung vom 15.09.2026 fand zwei
Wissensseiten auf siebzig Verkaufsseiten (``SU04``, kritisch; ``SU07``). Die
GEO-Messung vom 27.08.2026 hatte schon gezeigt, woran das liegt: Zitiert werden
Seiten, die **erklaeren**, nicht Seiten, die anbieten - alle drei
Website-Zitate trafen Leistungsseiten mit einem Definitionssatz, keines eine
der 54 Stadtseiten. Dieses Modul liefert die Texte, die nichts verkaufen
muessen.

**Warum als Daten und nicht im CMS.** ``BLOCK-4-AUTORITAET.md`` (T4) sah die
Artikel als CMS-Inhalte vor. Hier stehen sie trotzdem im Repository, aus
demselben Grund wie ``services.py``: Jede Preiszahl und jede Zeitangabe in
diesen Texten laeuft durch dieselben Pruefungen wie der Rest der Website
(Regeln 1 und 24). Ein CMS-Text erreicht ``check_seo`` nie, weil es gegen die
leere lokale Datenbank misst. Die Betriebsberichte bleiben im CMS
(``/aktuelles/``); das ist eine andere Inhaltsklasse.

**Was hier hineingehoert - und was nicht.** Nur Aussagen mit Beleg:

* Preise und Fristen als Platzhalter aus ``pricing.py`` und ``zusagen.py``.
* Ortsangaben wortgleich aus ``city_lokal.py`` - dort mit Quelle und Stand.
* Fachaussagen, die die Website an anderer Stelle bereits macht (§35a EStG,
  „besenrein“, der Ablauf), oder allgemeines Recht mit Fundstelle
  (Paragraf, Urteil). Wo eine Frage vom Einzelfall abhaengt, sagt der Text
  das und verweist auf Steuerberatung bzw. Mietrecht - er beantwortet sie
  nicht.

⚠ **Die fachliche Abnahme durch den Betrieb steht aus** (T6: „Fachliche
Richtigkeit vom Betrieb bestätigt“). Sie ist in ``doku/80-AUFGABEN.md`` unter
„Beim Kunden“ gefuehrt, samt zweier Unstimmigkeiten, die beim Schreiben in den
**bestehenden** Leistungstexten aufgefallen sind (Fahrtkosten und Nachlass bei
§35a).

**Geschweifte Klammern sind reserviert** - wie in ``services.py``. Ein
literales ``{`` laesst ``str.format()`` beim ersten Aufruf scheitern, und das
ist gewollt.

Regel 4: Das Modul importiert nichts aus ``apps.core``, nur Nachbarmodule
unter ``data/``.
"""

import functools
from html import escape as _escape

from .city_lokal import LOKAL as _LOKAL
from .cities import _CITY_DATA
from .ratgeber_wissen import WISSEN as _WISSEN
from .quellen import (QUELLEN as _QUELLEN, aus_schluesseln as _quellen_aus,
                      einsetzen as _quellen_einsetzen, kurzadresse as _kurzadresse)
from .services import _platzhalter as _preis_platzhalter, leistung as _leistung
from .stand import deutsch as _deutsch
from .zusagen import TERMIN_FRUEHESTENS as _BESICHTIGUNG, TERMIN_REGEL as _TERMIN

__all__ = ['_RATGEBER_DATA', 'artikel', 'alle_artikel', 'hub', 'GLOSSAR',
           'KATEGORIEN', 'STAND', 'STAND_ISO', 'lokal_staedte']

#: Rechtsstand der Artikel - wann die Fachaussagen zuletzt geprueft wurden.
#: ISO ist die Quelle, der deutsche Text wird gerechnet (G12).
#: 02.10.2026: alle fuenf Artikel gegen ihre Quellen neu geprueft.
STAND_ISO = '2026-10'
STAND = _deutsch(STAND_ISO)

#: Reihenfolge der Gruppen auf /ratgeber/ - die Gruppierung aus T4.
KATEGORIEN = ('Kosten und Steuern', 'Begriffe und Abgrenzung',
              'Vorbereitung und Übergabe', 'Entsorgung und Schadstoffe',
              'Erbe und Nachlass', 'Miete und Räumung')

#: Die sechs Standortstaedte, deren kommunale Sperrmuellregel der
#: Vergleichsartikel zeigt. Eigene Liste und nicht ``cities.py``: Dort gibt es
#: kein Feld "Standort", nur den Rabatt, und der meint dieselben sechs.
STANDORTE = _STANDORTE = ('halle', 'leipzig', 'magdeburg', 'dresden', 'chemnitz', 'hannover')


# ── Die Quellen ──────────────────────────────────────────────────────────────
#
# GE43 (17.09.2026): Die Belegstellen selbst stehen in ``data/quellen.py``.
# Dort steht auch, warum der Beleg als Fliesstext erscheint und nicht als
# Verweis - und warum die Tabelle ein eigenes Modul bekommen hat: ``services``
# braucht sie fuer ``/entruempelung-kosten/`` und darf nicht aus diesem Modul
# importieren, weil dieses Modul aus ``services`` liest.


# ── Die Artikel ──────────────────────────────────────────────────────────────
#
# Pflichtfelder je Eintrag:
#   kategorie, titel (kurz, fuer Karte und Brotkrumen), h1, h1_em, teaser,
#   answer_frage, answer, abschnitte, faq, leistungen, staedte,
#   seo_title, seo_description, seo_keywords
#
# Ein Abschnitt kennt: id, titel, absaetze, und optional liste, schritte
# (nummerierte Liste), vergleich (eine Tabelle fuer components/rw_vergleich.html)
# und lokal (True blendet die Sperrmuellregeln der Standortstaedte ein).
#
# ``leistungen``: Leistungs-Slugs, auf die der Artikel verweist. Dieselbe
# Liste erzeugt den Rueckverweis auf der Leistungsseite ("Mehr im Ratgeber") -
# eine Kante, zwei Richtungen, eine Quelle.
#
# ``quellen``: je Eintrag ein ``schluessel`` aus ``_QUELLEN``, die ``id`` des
# Abschnitts, an dessen **letzten Absatz** der Beleg tritt, und der ``bezug``,
# der sagt, was die Norm traegt. Der Abschnitt muss mindestens einen Absatz
# haben - eine Checkliste aus reinen ``schritte`` bekaeme sonst einen Absatz,
# den es vorher nicht gab, und das waere eine Aenderung am Aufbau.

_RATGEBER_DATA = {

    # ───────────────────────────────────────────────────────────────────────
    'entruempelung-steuerlich-absetzen': {
        'kategorie': 'Kosten und Steuern',
        'titel': 'Entrümpelung steuerlich absetzen',
        'h1': 'Entrümpelung von der Steuer absetzen',
        'h1_em': '§35a EStG verständlich erklärt',
        'teaser': (
            'Welcher Teil der Rechnung zählt, welcher Höchstbetrag gilt und '
            'warum eine Barzahlung den Steuervorteil kostet.'
        ),
        'seo_title': 'Entrümpelung steuerlich absetzen: §35a EStG | Rümpelwerk',
        'seo_description': (
            'Wann eine Entrümpelung nach §35a EStG zählt und wann nicht: 20 % '
            'der Arbeitskosten, bis 4.000 € im Jahr. Jetzt lesen.'
        ),
        'seo_keywords': ('entrümpelung steuerlich absetzen, haushaltsauflösung '
                         'steuer, 35a estg entrümpelung, haushaltsnahe '
                         'dienstleistung entrümpelung'),

        'answer_frage': 'Kann man eine Entrümpelung von der Steuer absetzen?',
        'answer': (
            'Räumen, Tragen und Sortieren im eigenen, bewohnten Haushalt können '
            'als haushaltsnahe Dienstleistung nach §35a Absatz 2 EStG zählen: '
            '20 % der Arbeitskosten werden von der Einkommensteuer abgezogen, '
            'höchstens 4.000 € im Jahr. Die komplette Haushaltsauflösung führt '
            'das Bundesfinanzministerium dagegen als nicht begünstigt. Nötig sind '
            'eine Rechnung mit getrennt ausgewiesenen Arbeitskosten und eine '
            'Überweisung. Rechtsstand: {stand}.'
        ),

        'quellen': [
            {'schluessel': 'estg-35a', 'abschnitt': 'grundlage',
             'bezug': 'Maßgeblich ist der Gesetzestext selbst'},
            {'schluessel': 'bmf-35a', 'abschnitt': 'was-zaehlt',
             'bezug': 'Haushaltsauflösung und Sperrmüllabfuhr stehen in Anlage 1 '
                      'als nicht begünstigt, Maschinen- und Fahrtkosten als '
                      'Arbeitskosten in Randnummer 39'},
            {'schluessel': 'bmf-35a', 'abschnitt': 'sonderfaelle',
             'bezug': 'Umzug: Randnummer 3, Erben: Randnummer 30'},
        ],

        'abschnitte': [
            {
                'id': 'grundlage',
                'titel': 'Welche Regel gilt: §35a Einkommensteuergesetz',
                'absaetze': [
                    '§35a EStG kennt zwei Töpfe, die sich im selben Jahr '
                    'ergänzen. <strong>Haushaltsnahe Dienstleistungen</strong> '
                    '(Absatz 2) sind Arbeiten, die üblicherweise Mitglieder des '
                    'Haushalts erledigen könnten – Aufräumen, Tragen, Sortieren, '
                    'Entsorgen. Das Anwendungsschreiben des '
                    'Bundesfinanzministeriums nennt die Entrümpelung nicht '
                    'ausdrücklich; die komplette <strong>Haushaltsauflösung</strong> '
                    'und die Sperrmüllabfuhr führt es dagegen als nicht '
                    'begünstigt. Gute Aussichten hat deshalb die Räumung von '
                    'Keller, Dachboden oder Garage in einem Haushalt, den Sie '
                    'weiter bewohnen. '
                    '<strong>Handwerkerleistungen</strong> (Absatz 3) sind '
                    'Renovierung, Erhaltung und Modernisierung, also etwa '
                    'Malerarbeiten nach der Räumung.',
                    'In beiden Töpfen mindern 20 % der Arbeitskosten die '
                    'Steuer. Der Höchstbetrag liegt für haushaltsnahe '
                    'Dienstleistungen bei 4.000 € im Jahr, für '
                    'Handwerkerleistungen bei 1.200 €. Entscheidend ist das Wort '
                    '<em>Steuer</em>: Der Betrag wird von der festgesetzten '
                    'Einkommensteuer abgezogen, nicht vom Einkommen. Von jedem '
                    'Euro Arbeitskosten kommen damit 20 Cent zurück – unabhängig '
                    'vom persönlichen Steuersatz, sofern im Jahr genug '
                    'Einkommensteuer anfällt, von der abgezogen werden kann.',
                    'Wer Räumung und Renovierung im selben Jahr beauftragt, '
                    'kann beide Höchstbeträge nebeneinander nutzen. Das '
                    'funktioniert nur, wenn beide Leistungen auf der Rechnung '
                    'getrennt stehen. Deshalb führen wir sie schon im Angebot '
                    'als eigene Positionen.',
                ],
            },
            {
                'id': 'was-zaehlt',
                'titel': 'Welcher Teil der Rechnung zählt',
                'absaetze': [
                    'Begünstigt sind nur die <strong>Arbeitskosten</strong>. '
                    'Nicht begünstigt sind Materialkosten sowie Entsorgungs- '
                    'und Deponiegebühren – das ist der Posten, der bei einer '
                    'Entrümpelung am stärksten ins Gewicht fällt und der am '
                    'häufigsten zu Unrecht mit angesetzt wird.',
                    'Nach dem Anwendungsschreiben des Bundesfinanzministeriums '
                    'können auch Maschinen- und Fahrtkosten zu den '
                    'Arbeitskosten gehören, wenn sie in der Rechnung '
                    'ausgewiesen sind. Wie das Finanzamt die Aufteilung im '
                    'Einzelfall bewertet, klären Sie mit Ihrer Steuerberatung. '
                    'Fordern Sie bei uns eine Rechnung mit ausgewiesenen '
                    'Arbeitskosten an.',
                ],
                'liste': [
                    '<strong>Zählt:</strong> Lohn für Räumen, Tragen, Sortieren '
                    'und Demontieren, jeweils mit Umsatzsteuer',
                    '<strong>Zählt nicht:</strong> Deponie- und '
                    'Entsorgungsgebühren, Container, Verpackungsmaterial',
                    '<strong>Zählt nicht:</strong> alles, was als '
                    'Betriebsausgabe oder Werbungskosten abgesetzt wird – etwa '
                    'die Räumung einer vermieteten Wohnung durch den Vermieter',
                ],
            },
            {
                'id': 'voraussetzungen',
                'titel': 'Die drei Voraussetzungen, an denen es scheitert',
                'absaetze': [
                    'In der Praxis scheitert der Abzug selten am Gesetz, sondern '
                    'an der Form. Drei Punkte prüft das Finanzamt bei jeder '
                    'Rechnung:',
                ],
                'schritte': [
                    '<strong>Eine ordentliche Rechnung.</strong> Sie nennt '
                    'Leistung, Ort und Datum und weist den Arbeitslohn getrennt '
                    'aus. Ohne diese Aufteilung erkennt das Finanzamt in der '
                    'Regel gar nichts an.',
                    '<strong>Zahlung auf das Konto des Betriebs.</strong> Eine '
                    'Barzahlung ist ausgeschlossen, auch mit Quittung. Heben Sie '
                    'den Kontoauszug zusammen mit der Rechnung auf.',
                    '<strong>Die Leistung im eigenen Haushalt.</strong> Gemeint '
                    'ist der Haushalt, den Sie selbst führen – als Eigentümer '
                    'oder als Mieter, in Deutschland, einem anderen Land der '
                    'EU oder des Europäischen Wirtschaftsraums. Das Räumen und '
                    'Tragen vor Ort gehört dazu.',
                ],
            },
            {
                'id': 'sonderfaelle',
                'titel': 'Nachlass, Umzug ins Heim, vermietete Wohnung',
                'absaetze': [
                    '<strong>Räumung nach einem Todesfall.</strong> Erben '
                    'können §35a nach dem Anwendungsschreiben nur für eine '
                    'geerbte Wohnung nutzen, die zu ihrem eigenen Haushalt '
                    'gehört, in der sie also selbst wohnen. Wird der Haushalt '
                    'eines Verstorbenen aufgelöst, in dem keiner der Erben lebt, '
                    'ist der Abzug deshalb in der Regel ausgeschlossen. Klären '
                    'Sie Ihren Fall mit Ihrer Steuerberatung; die Rechnung '
                    'stellen wir auf den Namen aus, den Sie uns nennen.',
                    '<strong>Auszug aus der eigenen Wohnung.</strong> Wer seinen '
                    'Haushalt selbst auflöst, etwa beim Umzug in eine kleinere '
                    'Wohnung oder in ein Pflegeheim, hat die besten Aussichten: '
                    'Arbeiten in der bisherigen Wohnung, die in engem zeitlichem '
                    'Zusammenhang mit dem Umzug stehen, rechnet das Finanzamt '
                    'noch dem eigenen Haushalt zu. Weil die komplette '
                    'Haushaltsauflösung als nicht begünstigt geführt wird, '
                    'klären Sie die Aufteilung vorher mit Ihrer Steuerberatung.',
                    '<strong>Vermietete Wohnung.</strong> Räumt ein Vermieter '
                    'eine Wohnung nach dem Auszug eines Mieters, sind die Kosten '
                    'Werbungskosten bei den Mieteinkünften. §35a gilt dann '
                    'nicht, der Betrag mindert aber die Einkünfte. Dasselbe gilt '
                    'für Betriebe: Eine '
                    '<a href="/gewerbeentruempelung/">Gewerbeentrümpelung</a> '
                    'ist Betriebsausgabe.',
                ],
            },
            {
                'id': 'rechnung',
                'titel': 'Rechnung und Festpreis',
                'absaetze': [
                    'Für den Steuerabzug brauchen Sie eine Rechnung mit ausgewiesenen '
                    'Arbeitskosten; sprechen Sie uns darauf an, auch wenn der '
                    'Auftrag zum Festpreis vergeben wird. Eine Entrümpelung '
                    'beginnt bei '
                    '{keller_ab} € für einen Keller, eine Wohnungsauflösung bei '
                    '{wohnung_ab} € und eine Haushaltsauflösung bei '
                    '{haus_ab} €. Wie diese Zahlen entstehen, steht auf der '
                    'Seite <a href="/entruempelung-kosten/">Was kostet eine '
                    'Entrümpelung?</a> mit drei durchgerechneten Beispielen.',
                    'Wird zusätzlich renoviert, stehen Räumung und Renovierung '
                    'als getrennte Positionen im Angebot. Malerarbeiten '
                    'rechnen wir mit {maler_rate} € pro m², mindestens '
                    '{maler_min} € – mehr dazu unter '
                    '<a href="/sanierung-renovierung/">Sanierung und '
                    'Renovierung</a>.',
                ],
            },
        ],

        'faq': [
            ('Wie viel Steuer spart man bei einer Entrümpelung?',
             'Wird die Räumung als haushaltsnahe Dienstleistung anerkannt: '
             '20 % der Arbeitskosten, höchstens 4.000 € im Jahr für alle '
             'haushaltsnahen Dienstleistungen zusammen. Der Betrag wird direkt '
             'von der Einkommensteuer abgezogen. Material, Entsorgungs- und '
             'Deponiegebühren zählen nicht mit.'),
            ('Kann ich eine bar bezahlte Entrümpelung absetzen?',
             'Nein. §35a EStG verlangt eine Rechnung und die Zahlung auf das '
             'Konto des Leistenden. Eine Barzahlung wird auch mit Quittung nicht '
             'anerkannt.'),
            ('Gilt der Steuerabzug auch für eine Haushaltsauflösung nach einem '
             'Todesfall?',
             'In der Regel nicht. Das Bundesfinanzministerium führt die '
             'Haushaltsauflösung als nicht begünstigt, und Erben können §35a '
             'nur für eine geerbte Wohnung nutzen, in der sie selbst wohnen. '
             'Klären Sie den Fall mit Ihrer Steuerberatung, bevor Sie ihn in die '
             'Erklärung aufnehmen.'),
            ('Kann ich Räumung und Renovierung im selben Jahr absetzen?',
             'Ja, in zwei getrennten Töpfen, sofern die Räumung als '
             'haushaltsnahe Dienstleistung anerkannt wird: sie bis 4.000 €, die '
             'Renovierung als '
             'Handwerkerleistung bis 1.200 € im Jahr. Dafür müssen beide '
             'Leistungen auf der Rechnung getrennt stehen.'),
        ],

        'leistungen': ['haushaltsaufloesung', 'wohnungsaufloesung',
                       'entruempelung-kosten', 'sanierung-renovierung'],
        'staedte': ['halle', 'leipzig'],
    },

    # ───────────────────────────────────────────────────────────────────────
    'unterschied-entruempelung-haushaltsaufloesung': {
        'kategorie': 'Begriffe und Abgrenzung',
        'titel': 'Entrümpelung oder Haushaltsauflösung?',
        'h1': 'Entrümpelung, Haushaltsauflösung, Wohnungsauflösung',
        'h1_em': 'Worin sich die Begriffe unterscheiden',
        'teaser': (
            'Sechs Begriffe, die oft durcheinandergehen – und woran Sie '
            'erkennen, welcher auf Ihren Fall passt.'
        ),
        # IS06 (24.09.2026): Der Titel nennt einen Nutzen (die Kosten stehen
        # im Artikel, aus pricing.py). Vorher 582 px, jetzt 560 px.
        'seo_title': 'Entrümpelung oder Haushaltsauflösung? Unterschied & Kosten',
        'seo_description': (
            'Entrümpelung, Haushalts-, Wohnungsauflösung, Nachlassräumung: was '
            'die Begriffe bedeuten. Mit Vergleichstabelle. Jetzt lesen.'
        ),
        'seo_keywords': ('unterschied entrümpelung haushaltsauflösung, '
                         'wohnungsauflösung bedeutung, was ist eine '
                         'entrümpelung, nachlassräumung unterschied'),

        'answer_frage': ('Was ist der Unterschied zwischen Entrümpelung und '
                         'Haushaltsauflösung?'),
        'answer': (
            'Eine Entrümpelung ist die Räumung einzelner Räume, deren Bewohner '
            'bleiben; eine Haushaltsauflösung ist die vollständige Auflösung '
            'eines Hausstands, meist nach einem Todesfall oder Umzug ins Heim. '
            'Bei Rümpelwerk Mitteldeutschland beginnt eine Entrümpelung bei '
            '{keller_ab} €, eine Haushaltsauflösung bei {haus_ab} €. '
            'Preisstand: {preisstand}.'
        ),

        'quellen': [
            {'schluessel': 'bgb-1922', 'abschnitt': 'begriffe',
             'bezug': 'Dass im Erbfall der gesamte Hausrat mit dem Todestag '
                      'auf die Erben übergeht, steht im Gesetz'},
        ],

        'abschnitte': [
            {
                'id': 'begriffe',
                'titel': 'Die Begriffe im Einzelnen',
                'absaetze': [
                    'Im Alltag werden die Wörter oft gleichbedeutend benutzt. '
                    'Für die Planung sind sie es nicht: Sie beschreiben, '
                    '<em>wie viel</em> geräumt wird und <em>was danach</em> mit '
                    'dem Objekt geschieht. Davon hängen Aufwand, Termin und '
                    'Preis ab.',
                    'Eine <strong>Entrümpelung</strong> ist die Räumung von '
                    'Gegenständen, die nicht mehr gebraucht werden – aus '
                    'einzelnen Räumen, meist aus Keller, Dachboden, Garage oder '
                    'Abstellkammer. Das Objekt bleibt bewohnt. Die '
                    '<a href="/kellerentruempelung/">Kellerentrümpelung</a> ist '
                    'der häufigste Fall.',
                    'Eine <strong>Haushaltsauflösung</strong> löst einen '
                    'kompletten Hausstand auf: Möbel, Hausrat, Kleidung, '
                    'Elektrogeräte, Keller und Dachboden. Danach wohnt dort '
                    'niemand mehr. Anlass ist meist ein Todesfall, der Umzug in '
                    'ein Pflegeheim oder der Verkauf des Hauses. Mehr unter '
                    '<a href="/haushaltsaufloesung/">Haushaltsauflösung</a>.',
                    'Eine <strong>Wohnungsauflösung</strong> ist dasselbe für '
                    'eine Mietwohnung – mit einem festen Ende: der Übergabe an '
                    'den Vermieter. Deshalb spielen hier das Mietende und der '
                    'Zustand „besenrein“ die Hauptrolle. Mehr unter '
                    '<a href="/wohnungsaufloesung/">Wohnungsauflösung</a>.',
                    'Eine <strong>Nachlassräumung</strong> ist eine '
                    'Haushaltsauflösung im Erbfall. Hinzu kommt die Sichtung: '
                    'Dokumente, Wertgegenstände und Erinnerungsstücke werden '
                    'beiseitegelegt, bevor geräumt wird, und oft müssen sich '
                    'mehrere Erben abstimmen. Mehr unter '
                    '<a href="/nachlassraeumung/">Nachlassräumung</a>.',
                ],
            },
            {
                'id': 'sonderfaelle',
                'titel': 'Zwei Sonderfälle: Messie-Wohnung und Gewerbe',
                'absaetze': [
                    'Bei einer <strong>Messie-Wohnung</strong> ist nicht die '
                    'Fläche das Maß, sondern der Füllgrad. Oft ist der Boden '
                    'nicht mehr zu sehen, dazu kommen Verschmutzung und '
                    'Schädlinge. Die Räumung dauert länger, und nach der '
                    'Räumung folgt häufig eine Grundreinigung. Wir rechnen '
                    'deshalb mit dem Füllgrad-Faktor {fuellgrad_messi} statt '
                    'mit dem Normalsatz – Einzelheiten unter '
                    '<a href="/messie-wohnung-entruempeln/">Messie-Wohnung '
                    'entrümpeln</a>.',
                    'Eine <strong>Gewerbeentrümpelung</strong> räumt Büros, '
                    'Ladenlokale, Lager und Werkstätten. Hier geht es um '
                    'Fristen aus dem Mietvertrag, um Akten, die '
                    'datenschutzgerecht vernichtet werden müssen, und um '
                    'Entsorgungsnachweise für die Buchhaltung. Mehr unter '
                    '<a href="/gewerbeentruempelung/">Gewerbeentrümpelung</a>.',
                ],
            },
            {
                'id': 'vergleich',
                'titel': 'Der Unterschied auf einen Blick',
                'absaetze': [
                    'Die Tabelle ordnet die Begriffe nach drei Fragen, die bei '
                    'jeder Anfrage zuerst kommen: Was wird geräumt, wohnt danach '
                    'noch jemand dort, und an wen geht das Objekt?',
                ],
                'vergleich': {
                    'anker': 'begriffe-tabelle',
                    'titel': 'Entrümpelung, Haushalts-, Wohnungsauflösung und '
                             'Nachlassräumung im Vergleich',
                    'kopf': ['Begriff', 'Was geräumt wird',
                             'Danach bewohnt?', 'Übergabe an'],
                    'zeilen': [
                        ['Entrümpelung', 'einzelne Räume, oft Keller oder '
                         'Dachboden', 'ja', 'die Bewohner selbst'],
                        ['Haushaltsauflösung', 'der ganze Hausstand', 'nein',
                         'Eigentümer, Makler oder Käufer'],
                        ['Wohnungsauflösung', 'eine komplette Mietwohnung',
                         'nein', 'den Vermieter'],
                        ['Nachlassräumung', 'der Hausstand einer verstorbenen '
                         'Person, mit Sichtung', 'nein',
                         'Erben, Vermieter oder Käufer'],
                        ['Messie-Wohnung', 'eine stark überfüllte Wohnung, '
                         'meist mit Reinigung', 'je nach Fall',
                         'Bewohner, Betreuer oder Vermieter'],
                        ['Gewerbeentrümpelung', 'Büro, Laden, Lager oder '
                         'Werkstatt', 'nein', 'Vermieter oder Nachmieter'],
                    ],
                    'fazit_frage': 'Welcher Begriff passt zu meinem Fall?',
                    'fazit': (
                        'Entscheidend ist, ob danach noch jemand dort wohnt. '
                        'Bleibt das Objekt bewohnt, ist es eine Entrümpelung; '
                        'wird der ganze Hausstand aufgelöst, eine '
                        'Haushaltsauflösung, bei einer Mietwohnung eine '
                        'Wohnungsauflösung. Der Ablauf ist in allen Fällen '
                        'derselbe, der Preis richtet sich nach Fläche und '
                        'Füllgrad.'
                    ),
                },
            },
            {
                'id': 'preis',
                'titel': 'Was der Begriff für den Preis bedeutet',
                'absaetze': [
                    'Der Name der Leistung legt den Preis nicht fest – die '
                    'Objektart und die Fläche tun es. Wir rechnen im Keller mit '
                    '{keller_rate} € pro m² bei mindestens {keller_ab} €, in der '
                    'Wohnung mit {wohnung_rate} € bei mindestens {wohnung_ab} € '
                    'und im Haus mit {haus_rate} € bei mindestens {haus_ab} €. '
                    'Darauf wirken der Füllgrad, das Stockwerk ohne Aufzug und '
                    'Sonderabfall wie Farben oder Batterien.',
                    'Den Richtwert für Ihren Fall nennt der '
                    '<a href="/preisangebot/">Preisrechner</a> in '
                    '{rechner_dauer}. Verbindlich wird der Preis nach der '
                    'kostenlosen Besichtigung; das schriftliche Angebot gibt es '
                    '{angebot_frist}.',
                ],
            },
        ],

        'faq': [
            ('Ist eine Haushaltsauflösung teurer als eine Entrümpelung?',
             'Meist ja, weil mehr geräumt wird: Eine Haushaltsauflösung umfasst '
             'den ganzen Hausstand, eine Entrümpelung oft nur einen Keller. Bei '
             'uns beginnt die Entrümpelung bei {keller_ab} €, die '
             'Haushaltsauflösung bei {haus_ab} €.'),
            ('Was ist der Unterschied zwischen Haushaltsauflösung und '
             'Nachlassräumung?',
             'Eine Nachlassräumung ist eine Haushaltsauflösung im Erbfall. Vor '
             'der Räumung werden Dokumente, Wertgegenstände und '
             'Erinnerungsstücke gesichtet und beiseitegelegt, und oft stimmen '
             'sich mehrere Erben über den Termin ab.'),
            ('Ist Sperrmüll dasselbe wie eine Entrümpelung?',
             'Nein. Sperrmüll ist die kommunale Abholung einzelner großer '
             'Stücke, die Sie selbst an die Straße stellen. Eine Entrümpelung '
             'räumt ganze Räume aus, trägt alles aus dem Objekt und entsorgt es '
             'getrennt nach Abfallart.'),
        ],

        'leistungen': ['haushaltsaufloesung', 'wohnungsaufloesung',
                       'kellerentruempelung', 'nachlassraeumung',
                       'messie-wohnung-entruempeln', 'gewerbeentruempelung'],
        'staedte': ['halle', 'leipzig', 'magdeburg'],
    },

    # ───────────────────────────────────────────────────────────────────────
    'sperrmuell-container-oder-entruempelungsfirma': {
        'kategorie': 'Begriffe und Abgrenzung',
        'titel': 'Sperrmüll, Container oder Firma?',
        'h1': 'Sperrmüll, Container oder Entrümpelungsfirma?',
        'h1_em': 'Drei Wege im ehrlichen Vergleich',
        'teaser': (
            'Wann die kommunale Abholung reicht, wann ein Container und wann '
            'eine Firma – mit den Sperrmüllregeln von sechs Städten.'
        ),
        'seo_title': 'Sperrmüll oder Entrümpelungsfirma? Vergleich | Rümpelwerk',
        'seo_description': (
            'Sperrmüll, Container oder Firma? Kosten, Wartezeit und Aufwand im '
            'Vergleich – mit den Regeln von sechs Städten. Jetzt lesen.'
        ),
        'seo_keywords': ('sperrmüll oder entrümpelung, container oder '
                         'entrümpelungsfirma, sperrmüll anmelden halle, '
                         'sperrmüll leipzig, sperrmüll dresden'),

        'answer_frage': 'Sperrmüll, Container oder Entrümpelungsfirma – was '
                        'lohnt sich?',
        'answer': (
            'Sperrmüll lohnt sich für einzelne große Stücke, die Sie selbst an '
            'die Straße tragen können; ein Container für viel Material, wenn '
            'Helfer da sind. Eine Entrümpelungsfirma übernimmt Tragen, Trennen '
            'und Entsorgen komplett und übergibt besenrein. Bei Rümpelwerk '
            'Mitteldeutschland beginnt das bei {keller_ab} € zum Festpreis. '
            'Preisstand: {preisstand}.'
        ),

        'quellen': [
            {'schluessel': 'krwg-17', 'abschnitt': 'sperrmuell',
             'bezug': 'Dass Abfälle aus privaten Haushalten grundsätzlich dem '
                      'öffentlich-rechtlichen Entsorgungsträger zu überlassen '
                      'sind, ist gesetzlich geregelt'},
        ],

        'abschnitte': [
            {
                'id': 'sperrmuell',
                'titel': 'Sperrmüll: günstig, aber mit Wartezeit und Grenzen',
                'absaetze': [
                    'Sperrmüll ist die Abholung großer Haushaltsgegenstände durch '
                    'den kommunalen Entsorger – Sofa, Schrank, Matratze. In '
                    'vielen Städten ist eine bestimmte Menge im Jahr '
                    'gebührenfrei oder kostet wenig. Dafür gelten drei Grenzen: '
                    'Die Menge ist je Haushalt gedeckelt, zwischen Anmeldung und '
                    'Abholung vergehen oft Wochen, und Sie müssen alles selbst '
                    'an die Straße bringen.',
                    'Was nicht mitgenommen wird, ist ebenso wichtig: '
                    'Elektrogeräte, Bauschutt, Farben, Batterien und lose '
                    'Kleinteile gehören nicht in den Sperrmüll. Sie müssen '
                    'getrennt zum Wertstoffhof oder zur Schadstoffannahme. Bei '
                    'einer kompletten Wohnung ist das der größte Teil der '
                    'Arbeit.',
                ],
            },
            {
                'id': 'staedte',
                'titel': 'So regeln sechs Städte den Sperrmüll',
                'absaetze': [
                    'Die Regeln unterscheiden sich stark – bei der Menge, bei den '
                    'Kosten und bei der Wartezeit. Hier die Angaben der '
                    'zuständigen Entsorger in sechs Städten unseres Einsatzgebiets, '
                    'jeweils mit Quelle. Stand der Recherche: {lokal_stand}. '
                    'Gebühren ändern sich; maßgeblich ist die verlinkte Seite '
                    'des Entsorgers.',
                ],
                'lokal': True,
            },
            {
                'id': 'container',
                'titel': 'Container: viel Volumen, aber alles selbst tragen',
                'absaetze': [
                    'Ein Container lohnt sich, wenn viel Material anfällt und '
                    'genug Helfer da sind – etwa bei einem Hausverkauf mit '
                    'Familie. Der Mietpreis hängt von Anbieter, Größe und '
                    'Abfallart ab; gemischte Abfälle sind deutlich teurer als '
                    'sortenreine.',
                    'Drei Punkte werden oft unterschätzt. Erstens: Steht der '
                    'Container auf öffentlichem Grund, braucht es in der Regel '
                    'eine Genehmigung der Stadt. Zweitens: Elektrogeräte und '
                    'Schadstoffe dürfen nicht hinein. Drittens: Tragen, '
                    'Zerlegen und Beladen bleiben bei Ihnen – bei einer '
                    'Altbauwohnung im dritten Stock ohne Aufzug ist das der '
                    'eigentliche Aufwand.',
                ],
            },
            {
                'id': 'firma',
                'titel': 'Entrümpelungsfirma: ein Termin, ein Preis, besenrein',
                'absaetze': [
                    'Eine Entrümpelungsfirma übernimmt alles zwischen Anfrage und '
                    'Übergabe: Demontage, Tragen aus jedem Stockwerk, Trennen '
                    'nach Abfallart, Fahrten zum Wertstoffhof und die '
                    'besenreine Übergabe. Bei uns steht der Preis nach der '
                    'kostenlosen Besichtigung fest, die '
                    '{besichtigung} buchbar ist. Der Termin für die '
                    'Räumung selbst liegt in der Regel in {termin_regel}.',
                    'Günstiger als Sperrmüll ist das fast nie. Es lohnt sich, '
                    'wenn eine ganze Wohnung geräumt werden muss, wenn eine '
                    'Frist drängt – etwa das Mietende – oder wenn niemand '
                    'selbst tragen kann. Wie sich unser Preis zusammensetzt, '
                    'steht unter <a href="/entruempelung-kosten/">Was kostet '
                    'eine Entrümpelung?</a>.',
                ],
            },
            {
                'id': 'vergleich',
                'titel': 'Die drei Wege nebeneinander',
                'absaetze': [
                    'Die Tabelle vergleicht die drei Wege nach den Punkten, die '
                    'bei der Entscheidung am meisten zählen.',
                ],
                'vergleich': {
                    'anker': 'wege-tabelle',
                    'titel': 'Sperrmüll, Container und Entrümpelungsfirma im '
                             'Vergleich',
                    'kopf': ['Weg', 'Kosten', 'Wer trägt?',
                             'Was ist erlaubt?', 'Passt für'],
                    'zeilen': [
                        ['Sperrmüll', 'gering, je nach Stadt teils frei',
                         'Sie selbst, bis zur Straße',
                         'nur große Haushaltsstücke',
                         'einzelne Möbel'],
                        ['Container', 'Miete je nach Größe und Abfallart',
                         'Sie selbst, bis in den Container',
                         'je nach Container, keine Elektrogeräte',
                         'viel Material mit Helfern'],
                        ['Entrümpelungsfirma',
                         'Festpreis nach Besichtigung',
                         'das Team der Firma',
                         'alles, getrennt nach Abfallart',
                         'ganze Wohnungen und Häuser'],
                    ],
                    'fazit_frage': 'Wann ist eine Firma die bessere Wahl?',
                    'fazit': (
                        'Eine Entrümpelungsfirma lohnt sich, sobald mehr als '
                        'einzelne Möbel geräumt werden, eine Frist drängt oder '
                        'niemand selbst tragen kann. Sperrmüll bleibt der '
                        'günstigste Weg für einzelne große Stücke, wenn Zeit '
                        'und Helfer da sind.'
                    ),
                },
            },
        ],

        'faq': [
            ('Was darf nicht in den Sperrmüll?',
             'Elektrogeräte, Bauschutt, Farben, Lacke, Batterien und '
             'Kleinteile in Säcken. Sie gehören zum Wertstoffhof oder zur '
             'Schadstoffannahme des kommunalen Entsorgers.'),
            ('Brauche ich für einen Container eine Genehmigung?',
             'Steht der Container auf öffentlichem Grund, etwa am '
             'Straßenrand, in der Regel ja. Zuständig ist die Stadt; die '
             'Containerfirma weiß meist, wo der Antrag gestellt wird. Auf dem '
             'eigenen Grundstück ist keine Genehmigung nötig.'),
            ('Nimmt eine Entrümpelungsfirma auch Elektrogeräte und Farben mit?',
             'Wir schon: Elektrogeräte bringen wir zur Annahmestelle, '
             'Sonderabfall wie Farben und Lacke rechnen wir als eigene Position '
             '– {sonderabfall_wenige_txt} € für einzelne Posten, '
             '{sonderabfall_viele_txt} € für größere Mengen.'),
        ],

        'leistungen': ['sperrmuell-entsorgung', 'kellerentruempelung',
                       'wohnungsaufloesung', 'entruempelung-kosten'],
        'staedte': list(_STANDORTE),
    },

    # ───────────────────────────────────────────────────────────────────────
    'serioese-entruempelungsfirma-erkennen': {
        'kategorie': 'Vorbereitung und Übergabe',
        'titel': 'Seriöse Entrümpelungsfirma erkennen',
        'h1': 'Woran Sie eine seriöse Entrümpelungsfirma erkennen',
        'h1_em': 'Acht Punkte vor der Unterschrift',
        'teaser': (
            'Festpreis statt Schätzung, Entsorgungsnachweis, Impressum: '
            'eine Checkliste für das Gespräch mit jeder Firma.'
        ),
        'seo_title': 'Seriöse Entrümpelungsfirma erkennen: 8 Punkte | Rümpelwerk',
        'seo_description': (
            'Seriöse Entrümpelungsfirma erkennen: Festpreis, '
            'Entsorgungsnachweis, Impressum und fünf weitere Punkte. '
            'Jetzt prüfen.'
        ),
        'seo_keywords': ('seriöse entrümpelungsfirma, entrümpelungsfirma '
                         'erkennen, entrümpelung abzocke, entrümpelung '
                         'festpreis, entsorgungsnachweis'),

        'answer_frage': 'Woran erkennt man eine seriöse Entrümpelungsfirma?',
        'answer': (
            'Eine seriöse Entrümpelungsfirma besichtigt vor dem Angebot, nennt '
            'einen schriftlichen Festpreis mit Leistungsumfang, weist die '
            'Arbeitskosten getrennt aus und belegt die Entsorgung auf Wunsch mit '
            'einem Nachweis. Rümpelwerk Mitteldeutschland übergibt das Angebot '
            '{angebot_frist}, die Besichtigung selbst ist kostenlos, der '
            'Festpreis beginnt ab {keller_ab} €. Stand: {stand}.'
        ),

        'quellen': [
            {'schluessel': 'krwg-53', 'abschnitt': 'warum',
             'bezug': 'Wer gewerbsmäßig Abfälle sammelt, befördert oder damit '
                      'handelt, muss das bei der zuständigen Behörde anzeigen '
                      '– danach dürfen Sie fragen'},
            {'schluessel': 'ddg-5', 'abschnitt': 'warum',
             'bezug': 'Pflichtangaben im Impressum'},
            {'schluessel': 'krwg-50', 'abschnitt': 'warum',
             'bezug': 'Nachweispflichten gelten für gefährliche Abfälle, nicht '
                      'für private Haushaltungen (Absatz 4)'},
        ],

        'abschnitte': [
            {
                'id': 'warum',
                'titel': 'Warum sich die Prüfung lohnt',
                'absaetze': [
                    'Entrümpelung ist kein geschützter Beruf. Anbieter '
                    'unterscheiden sich deshalb stark – bei der Kalkulation, '
                    'bei der Entsorgung und bei dem, was am Ende auf der '
                    'Rechnung steht. Die häufigsten Ärgernisse sind '
                    'Nachforderungen nach der Räumung und Hausrat, der nicht '
                    'dort ankommt, wo er hingehört.',
                    'Das zweite betrifft Sie auch nach dem Auftrag: Findet eine '
                    'Behörde Ihren Hausrat an einer wilden Müllkippe, führt die '
                    'Spur über Briefe und Adressaufkleber zu Ihnen. Die '
                    'folgenden acht Punkte lassen sich in jedem Gespräch '
                    'abfragen, ohne Fachwissen.',
                ],
            },
            {
                'id': 'checkliste',
                'titel': 'Die Checkliste',
                'absaetze': [],
                'schritte': [
                    '<strong>Besichtigung vor dem Preis.</strong> Wer ohne '
                    'Besichtigung einen verbindlichen Preis nennt, schätzt. '
                    'Fotos reichen für eine erste Einschätzung, nicht für einen '
                    'Festpreis.',
                    '<strong>Schriftliches Angebot mit Leistungsumfang.</strong> '
                    'Im Angebot steht, was enthalten ist und was nicht: '
                    'Demontage, Tragen, Entsorgung, besenreine Übergabe. Ein '
                    'Preis ohne Umfang lässt sich nicht vergleichen.',
                    '<strong>Festpreis statt Stundenlohn.</strong> Bei '
                    'Stundenlohn tragen Sie das Risiko, dass es länger dauert. '
                    'Ein Festpreis verschiebt es zur Firma.',
                    '<strong>Keine Nachforderung für Bekanntes.</strong> Fragen '
                    'Sie, in welchen Fällen sich der Preis noch ändern kann. '
                    'Die ehrliche Antwort lautet: nur wenn etwas auftaucht, das '
                    'bei der Besichtigung nicht zu sehen war.',
                    '<strong>Entsorgungsnachweis auf Wunsch.</strong> Er belegt, '
                    'wo der Hausrat geblieben ist, etwa mit den Belegen der '
                    'Annahmestelle. Für Privathaushalte schreibt das Gesetz '
                    'ihn nicht vor; er schützt Sie aber, falls Hausrat '
                    'illegal abgeladen wird.',
                    '<strong>Betriebshaftpflicht.</strong> Beim Tragen durch '
                    'enge Treppenhäuser entstehen Schäden an Wänden, Türen und '
                    'Geländern. Fragen Sie, ob und wie die Firma versichert ist.',
                    '<strong>Rechnung mit Arbeitskosten.</strong> Ohne getrennt '
                    'ausgewiesenen Lohn entfällt der Steuervorteil nach §35a '
                    'EStG – siehe <a href="/ratgeber/'
                    'entruempelung-steuerlich-absetzen/">Entrümpelung steuerlich '
                    'absetzen</a>.',
                    '<strong>Vollständiges Impressum.</strong> Name, '
                    'Anschrift und E-Mail-Adresse gehören nach §5 '
                    'Digitale-Dienste-Gesetz ins Impressum, dazu – falls '
                    'vorhanden – Handelsregistereintrag und '
                    'Umsatzsteuer-Identifikationsnummer. Eine Firma, die nur '
                    'über eine Mobilnummer ohne '
                    'Adresse erreichbar ist, ist bei einer Reklamation schwer zu '
                    'finden.',
                ],
            },
            {
                'id': 'warnzeichen',
                'titel': 'Warnzeichen im Gespräch',
                'absaetze': [
                    'Einzelne Punkte sind noch kein Beweis, zusammen sollten sie '
                    'Sie vorsichtig machen:',
                ],
                'liste': [
                    'ein auffällig niedriger Preis am Telefon, ohne dass jemand '
                    'das Objekt gesehen hat',
                    'eine hohe Anzahlung in bar vor Beginn der Arbeiten',
                    'ein Angebot, das den Preis mit dem Wert des Hausrats '
                    'verrechnet, ohne dass die Stücke einzeln genannt werden',
                    'keine Rechnung oder eine Rechnung ohne Anschrift',
                    'Druck, sofort zu unterschreiben',
                ],
            },
            {
                'id': 'vergleichen',
                'titel': 'Zwei Angebote richtig vergleichen',
                'absaetze': [
                    'Ein Preisvergleich ist nur fair, wenn beide Angebote '
                    'dasselbe beschreiben. Legen Sie sie nebeneinander und '
                    'prüfen Sie Zeile für Zeile: Sind Demontage und Tragen aus '
                    'dem Stockwerk enthalten? Sind die Entsorgungsgebühren im '
                    'Preis oder kommen sie nach Gewicht dazu? Ist der Keller '
                    'mitgerechnet? Wird besenrein übergeben, und was heißt das '
                    'beim jeweiligen Anbieter?',
                    'Ein Angebot, das deutlich unter den anderen liegt, spart '
                    'oft an einer dieser Stellen – oder rechnet mit einer '
                    'Nachforderung. Fragen Sie in diesem Fall konkret nach, '
                    'welche Positionen fehlen. Seriöse Anbieter nennen außerdem, '
                    'wie sie rechnen. Bei uns sind das ein Quadratmetersatz je '
                    'Objektart und ein Mindestpreis, dazu Zuschläge für '
                    'Füllgrad, Stockwerk ohne Aufzug und Sonderabfall; im Keller '
                    'etwa {keller_rate} € pro m², mindestens {keller_ab} €.',
                    'Nicht vergleichbar sind Angebote, von denen eines mit, das '
                    'andere ohne Besichtigung entstanden ist. Das erste ist ein '
                    'Preis, das zweite eine Schätzung – der Unterschied zeigt '
                    'sich erst am Tag der Räumung.',
                ],
            },
            {
                'id': 'wertanrechnung',
                'titel': 'Wertanrechnung: wann sie fair ist',
                'absaetze': [
                    'Manche Firmen rechnen den Wert verwertbarer Möbel gegen den '
                    'Preis. Das kann fair sein, wenn die Stücke einzeln mit '
                    'Betrag im Angebot stehen. Problematisch wird es, wenn ein '
                    'pauschaler Abzug den Preis drückt und nach der Räumung '
                    'wieder verschwindet, weil die Stücke „doch nichts wert“ '
                    'waren.',
                    'Wir kaufen nichts an und rechnen nichts gegen. Der '
                    'Festpreis steht vor Beginn fest, unabhängig davon, was '
                    'gefunden wird – und was Ihnen gehört, bleibt Ihnen. Wer '
                    'Wertvolles verkaufen möchte, tut das am besten vor der '
                    'Räumung.',
                ],
            },
            {
                'id': 'so-arbeiten-wir',
                'titel': 'So arbeiten wir',
                'absaetze': [
                    'Auf eine Anfrage antworten wir innerhalb von {reaktion}. '
                    'Die Besichtigung ist kostenlos und {besichtigung} '
                    'buchbar; das schriftliche '
                    'Festpreisangebot gibt es {angebot_frist}. Wie sich der Preis '
                    'zusammensetzt, steht '
                    'offen auf der Seite <a href="/entruempelung-kosten/">Was '
                    'kostet eine Entrümpelung?</a>, und wer bei Ihnen klingelt, '
                    'steht auf der <a href="/ueber-uns/">Team-Seite</a>.',
                ],
            },
        ],

        'faq': [
            ('Ist ein Festpreis bei einer Entrümpelung üblich?',
             'Bei seriösen Firmen ja, nach einer Besichtigung. Ohne '
             'Besichtigung ist jede Zahl eine Schätzung. Fragen Sie, in welchen '
             'Fällen sich der Festpreis noch ändern kann.'),
            ('Was ist ein Entsorgungsnachweis?',
             'Ein Beleg darüber, wo die geräumten Gegenstände entsorgt wurden. '
             'Er schützt Sie, falls Hausrat illegal abgeladen wird. Für '
             'Privathaushalte ist er gesetzlich nicht vorgeschrieben; die '
             'Nachweispflichten des Kreislaufwirtschaftsgesetzes gelten nur '
             'für gefährliche Abfälle und ausdrücklich nicht für private '
             'Haushaltungen.'),
            ('Muss ich bei der Entrümpelung dabei sein?',
             'Nein. Nach der Besichtigung und mit klaren Absprachen, was bleibt, '
             'kann das Team allein räumen. Die Übergabe machen wir auf Wunsch '
             'direkt mit Vermieter, Makler oder Hausverwaltung.'),
        ],

        'leistungen': ['haushaltsaufloesung', 'nachlassraeumung',
                       'entruempelung-kosten'],
        'staedte': ['halle', 'leipzig', 'dresden'],
    },

    # ───────────────────────────────────────────────────────────────────────
    'besenrein-wohnungsuebergabe': {
        'kategorie': 'Vorbereitung und Übergabe',
        'titel': 'Besenrein übergeben',
        'h1': 'Wohnung besenrein übergeben',
        'h1_em': 'Was der Begriff verlangt – und was nicht',
        'teaser': (
            'Was „besenrein“ laut Bundesgerichtshof bedeutet, was Sie vor der '
            'Schlüsselübergabe erledigen und was im Protokoll stehen sollte.'
        ),
        'seo_title': 'Besenrein bei der Wohnungsübergabe: Checkliste | Rümpelwerk',
        'seo_description': (
            'Was heißt besenrein? Was der Bundesgerichtshof sagt, was Mieter '
            'schulden – mit Checkliste zur Übergabe. Jetzt lesen.'
        ),
        'seo_keywords': ('besenrein bedeutung, was heißt besenrein, wohnung '
                         'besenrein übergeben, wohnungsübergabe checkliste, '
                         'besenrein bgh'),

        'answer_frage': 'Was bedeutet besenrein bei der Wohnungsübergabe?',
        'answer': (
            'Besenrein bedeutet, dass die Wohnung vollständig geräumt und von '
            'groben Verschmutzungen befreit ist – gefegt, nicht gewischt; so '
            'hat es der Bundesgerichtshof 2006 festgehalten. Fenster putzen oder '
            'streichen gehört nicht dazu. Rümpelwerk Mitteldeutschland übergibt '
            'jede geräumte Wohnung in diesem Zustand, ab {wohnung_ab} €. '
            'Preisstand: {preisstand}.'
        ),

        'quellen': [
            {'schluessel': 'bgb-546', 'abschnitt': 'bedeutung',
             'bezug': 'Die Rückgabepflicht selbst steht im Gesetz; was '
                      '„besenrein“ dabei verlangt, hat erst das genannte '
                      'Urteil bestimmt'},
        ],

        'abschnitte': [
            {
                'id': 'bedeutung',
                'titel': 'Was „besenrein“ rechtlich bedeutet',
                'absaetze': [
                    'Steht im Mietvertrag, die Wohnung sei „besenrein“ '
                    'zurückzugeben, schuldet der Mieter nach dem Urteil des '
                    'Bundesgerichtshofs vom 28. Juni 2006 (Az. VIII ZR 124/05) '
                    'nur die Beseitigung grober Verschmutzungen. Was im '
                    'Einzelnen dazugehört, hat das Gericht offengelassen; '
                    'üblicherweise versteht man darunter eine leere, gefegte '
                    'Wohnung ohne Spinnweben und lose Abfälle.',
                    'Nicht verlangt sind damit eine feuchte Reinigung, geputzte '
                    'Fenster oder eine Grundreinigung von Küche und Bad. Ob Sie '
                    'streichen müssen, regelt nicht das Wort „besenrein“, '
                    'sondern die Klausel zu Schönheitsreparaturen in Ihrem '
                    'Mietvertrag – ob sie wirksam ist, hängt vom Einzelfall ab '
                    'und ist eine Frage für den Mieterverein oder eine '
                    'Rechtsberatung.',
                ],
            },
            {
                'id': 'unser-standard',
                'titel': 'Unser Standard bei der Übergabe',
                'absaetze': [
                    'Bei uns heißt besenrein: Das Objekt ist vollständig '
                    'geräumt, der Boden gefegt, grober Schmutz entfernt. Dübel, '
                    'Nägel und Wandhaken nehmen wir mit heraus. Was besenrein '
                    'nicht heißt: gewischt, Fenster geputzt, Wände gestrichen.',
                    'Wenn der Vermieter oder Käufer mehr erwartet, sagen Sie es '
                    'uns vorher. Endreinigung und Malerarbeiten lassen sich in '
                    'denselben Auftrag legen und stehen dann als eigene '
                    'Position im Angebot – Einzelheiten unter '
                    '<a href="/sanierung-renovierung/">Sanierung und '
                    'Renovierung</a>.',
                ],
            },
            {
                'id': 'checkliste',
                'titel': 'Checkliste vor der Schlüsselübergabe',
                'absaetze': [
                    'Die Übergabe dauert selten lange, wenn diese Punkte vorher '
                    'erledigt sind:',
                ],
                'schritte': [
                    '<strong>Mietvertrag lesen.</strong> Was steht zur Rückgabe, '
                    'zu Schönheitsreparaturen und zu Einbauten? Das legt fest, '
                    'was über „besenrein“ hinaus zu tun ist.',
                    '<strong>Eigene Einbauten klären.</strong> Was Sie selbst '
                    'eingebaut haben – Küche, Regale, Lampen, Teppichboden –, '
                    'bauen Sie grundsätzlich zurück, sofern mit dem Vermieter '
                    'nichts anderes vereinbart ist. Fragen Sie, ob der '
                    'Nachmieter etwas übernehmen möchte.',
                    '<strong>Keller, Dachboden und Stellplatz nicht '
                    'vergessen.</strong> Sind sie mitvermietet, gehören sie zur '
                    'Mietsache und werden genauso übergeben wie die Wohnung.',
                    '<strong>Zählerstände notieren.</strong> Strom, Gas und '
                    'Wasser mit Foto festhalten und den Versorgern melden.',
                    '<strong>Alle Schlüssel sammeln.</strong> Auch Keller-, '
                    'Briefkasten- und nachgemachte Schlüssel. Fehlende Schlüssel '
                    'sind ein häufiger Streitpunkt.',
                    '<strong>Übergabeprotokoll anfertigen.</strong> Zustand '
                    'jedes Raums, Zählerstände und Schlüsselzahl schriftlich '
                    'festhalten und von beiden Seiten unterschreiben lassen, '
                    'dazu Fotos mit Datum.',
                ],
            },
            {
                'id': 'erben',
                'titel': 'Wenn Erben die Wohnung übergeben',
                'absaetze': [
                    'Stirbt ein Mieter, endet der Mietvertrag nicht von selbst. '
                    'Tritt niemand nach §563 BGB in den Vertrag ein – etwa ein '
                    'Ehepartner, der dort mitgewohnt hat –, können Erben und '
                    'Vermieter ihn nach §564 BGB außerordentlich mit der '
                    'gesetzlichen Frist kündigen. Die Erben müssen das innerhalb '
                    'eines Monats tun, nachdem sie vom Tod und davon erfahren '
                    'haben, dass niemand eintritt. Bis zum Ende der Frist läuft '
                    'die Miete weiter; eine frühe Räumung spart deshalb keine '
                    'Miete, verschafft aber Zeit für die Übergabe.',
                    'Für den Zustand der Wohnung gilt dasselbe wie bei jedem '
                    'anderen Auszug: Sie geht so zurück, wie es der Mietvertrag '
                    'verlangt, in der Regel besenrein. Hinzu kommt die Sichtung '
                    'vor der Räumung – Dokumente, Versicherungsunterlagen, '
                    'Wertgegenstände und Erinnerungsstücke. Wie wir dabei '
                    'vorgehen, steht unter '
                    '<a href="/nachlassraeumung/">Nachlassräumung</a>. Wer die '
                    'Fristen im Einzelfall klären muss, wendet sich an einen '
                    'Mieterverein oder eine Rechtsberatung; für Erbschein und '
                    'Ausschlagung ist das Nachlassgericht zuständig.',
                ],
            },
            {
                'id': 'streit',
                'titel': 'Wenn es bei der Übergabe hakt',
                'absaetze': [
                    'Die meisten Konflikte entstehen, weil beide Seiten unter '
                    '„besenrein“ etwas anderes verstehen. Das Protokoll ist '
                    'dann das wichtigste Dokument: Was dort ohne Beanstandung '
                    'steht, ist später schwer zu bestreiten. Unterschreiben Sie '
                    'nichts, was Sie für falsch halten – notieren Sie Ihre '
                    'abweichende Sicht im Protokoll.',
                    'Wer die Räumung beauftragt, muss nicht selbst dabei sein. '
                    'Wir übergeben auf Wunsch direkt an Vermieter, Makler oder '
                    'Hausverwaltung, auf Wunsch mit Entsorgungsnachweis. '
                    'Wie eine komplette '
                    '<a href="/wohnungsaufloesung/">Wohnungsauflösung</a> '
                    'abläuft, steht auf der Leistungsseite.',
                ],
            },
        ],

        'faq': [
            ('Muss ich bei „besenrein“ wischen?',
             'Nein. Nach dem Urteil des Bundesgerichtshofs vom 28. Juni 2006 '
             'verlangt „besenrein“ nur die Beseitigung grober Verschmutzungen. '
             'Üblicherweise heißt das: leer und gefegt; Wischen und '
             'Fensterputzen gehören nicht dazu.'),
            ('Muss ich Dübellöcher schließen?',
             'Das hängt vom Mietvertrag und vom Umfang ab und hat mit '
             '„besenrein“ nichts zu tun. Bei uns gehören das Entfernen von '
             'Dübeln, Nägeln und Wandhaken zur Übergabe; das Verschließen und '
             'Streichen ist eine eigene Position.'),
            ('Wer übergibt die Wohnung nach einem Todesfall?',
             'Die Erben. Tritt niemand in den Mietvertrag ein, können sie ihn '
             'nach §564 BGB innerhalb eines Monats außerordentlich mit der '
             'gesetzlichen Frist kündigen und übergeben die Wohnung dann so, '
             'wie es der Mietvertrag verlangt – in der Regel besenrein.'),
            ('Was passiert, wenn die Wohnung nicht besenrein ist?',
             'Der Vermieter kann verlangen, dass nachgebessert wird, und bei '
             'Weigerung die Kosten für die Reinigung oder Räumung geltend '
             'machen. Ein unterschriebenes Übergabeprotokoll mit Fotos schützt '
             'beide Seiten.'),
        ],

        'leistungen': ['wohnungsaufloesung', 'haushaltsaufloesung',
                       'sanierung-renovierung'],
        'staedte': ['halle', 'leipzig', 'hannover'],
    },
}


# SU07 (02.10.2026): siebzehn belegte Wissensseiten aus ``ratgeber_wissen.py``.
# Eigenes Modul, weil jeder Artikel 10-20 KiB Text mit Fundstellen traegt.
_doppelt = set(_RATGEBER_DATA) & set(_WISSEN)
assert not _doppelt, f'Slug doppelt vergeben: {_doppelt}'
_RATGEBER_DATA.update(_WISSEN)


# ── Glossar fuer /ratgeber/ ──────────────────────────────────────────────────
#
# Kurze Definitionen der Begriffe, die in den Artikeln und auf den
# Leistungsseiten immer wieder vorkommen. Jede Definition beginnt mit dem
# Begriff und einem "ist" - das ist der Satzbau, den Antwortmaschinen
# zitieren (siehe antworten.py). Auf der Seite stehen sie als <dl>, im Schema
# als DefinedTermSet; beides aus dieser einen Liste (Regel 12).
GLOSSAR = [
    ('Besenrein',
     'Besenrein ist der Zustand einer geräumten Wohnung ohne grobe '
     'Verschmutzungen: leer und gefegt, aber nicht gewischt. Mehr dazu im '
     'Artikel zur Wohnungsübergabe.'),
    ('Entrümpelung',
     'Eine Entrümpelung ist die Räumung nicht mehr benötigter Gegenstände aus '
     'einzelnen Räumen, etwa Keller oder Dachboden. Das Objekt bleibt dabei '
     'bewohnt.'),
    ('Haushaltsauflösung',
     'Eine Haushaltsauflösung ist die vollständige Auflösung eines Hausstands '
     'mit Möbeln, Hausrat und Nebenräumen – meist nach einem Todesfall oder '
     'beim Umzug ins Pflegeheim.'),
    ('Wohnungsauflösung',
     'Eine Wohnungsauflösung ist die vollständige Räumung einer Mietwohnung '
     'mit anschließender Übergabe an den Vermieter.'),
    ('Nachlassräumung',
     'Eine Nachlassräumung ist die Haushaltsauflösung im Erbfall, mit Sichtung '
     'von Dokumenten, Wertgegenständen und Erinnerungsstücken vor der '
     'Räumung.'),
    ('Festpreis',
     'Ein Festpreis ist ein Preis, der nach der Besichtigung verbindlich '
     'feststeht und sich nicht nach der tatsächlichen Arbeitszeit richtet.'),
    ('Füllgrad',
     'Der Füllgrad ist das Maß dafür, wie voll ein Raum steht. Wir '
     'unterscheiden leicht, mittel und voll sowie stark verschmutzt und '
     'Messie-Wohnung.'),
    ('Stockwerkzuschlag',
     'Der Stockwerkzuschlag ist der Aufpreis für das Tragen über Treppen ohne '
     'Aufzug. Bei uns liegt er zwischen {stockwerk_min_txt} € und '
     '{stockwerk_max_txt} €; mit Aufzug entfällt er.'),
    ('Sonderabfall',
     'Sonderabfall ist Abfall, der nicht in den Hausmüll darf, etwa Farben, '
     'Lacke, Lösungsmittel oder Batterien. Er wird getrennt abgegeben.'),
    ('Sperrmüll',
     'Sperrmüll ist die kommunale Abholung großer Haushaltsgegenstände wie '
     'Möbel oder Matratzen, die nicht in die Mülltonne passen.'),
    ('Wertstoffhof',
     'Ein Wertstoffhof ist die Annahmestelle des kommunalen Entsorgers für '
     'Sperrmüll, Elektrogeräte, Grünschnitt und andere getrennte Abfälle.'),
    ('Entsorgungsnachweis',
     'Ein Entsorgungsnachweis ist der Beleg darüber, wo geräumte Gegenstände '
     'fachgerecht entsorgt wurden. Für Privathaushalte ist er nicht '
     'vorgeschrieben, schützt aber bei illegal abgeladenem Hausrat.'),
    ('Messie-Wohnung',
     'Eine Messie-Wohnung ist eine Wohnung, die durch jahrelanges Sammeln so '
     'überfüllt ist, dass sie kaum noch nutzbar ist. Ihre Räumung wird nach '
     'dem Füllgrad gerechnet, nicht allein nach der Fläche.'),
    ('Container',
     'Ein Container ist ein gemieteter Abfallbehälter, der gefüllt und '
     'abgeholt wird. Steht er auf öffentlichem Grund, braucht es in der Regel '
     'eine Genehmigung der Stadt.'),
    ('Nachlassgericht',
     'Das Nachlassgericht ist die Abteilung des Amtsgerichts, die Erbscheine '
     'erteilt und die Ausschlagung einer Erbschaft entgegennimmt.'),
    ('Erbschein',
     'Ein Erbschein ist das gerichtliche Zeugnis darüber, wer Erbe ist. '
     'Banken dürfen ihn nicht in jedem Fall verlangen; ein eröffnetes '
     'notarielles Testament genügt meist (BGH, Az. XI ZR 401/12).'),
    ('Mindestpreis',
     'Der Mindestpreis ist der Betrag, den ein Auftrag unabhängig von der '
     'Fläche mindestens kostet, weil Anfahrt, Fahrzeug und Deponie immer '
     'anfallen. Bei uns beginnt er bei {keller_ab} € für einen Keller.'),
    ('Übergabeprotokoll',
     'Ein Übergabeprotokoll ist die schriftliche Aufnahme von Zustand, '
     'Zählerständen und Schlüsseln bei der Rückgabe einer Wohnung, '
     'unterschrieben von beiden Seiten.'),
    ('Schönheitsreparaturen',
     'Schönheitsreparaturen sind Arbeiten wie Streichen und Tapezieren. Ob ein '
     'Mieter sie beim Auszug schuldet, regelt der Mietvertrag, nicht das Wort '
     '„besenrein“.'),
    ('Wertanrechnung',
     'Eine Wertanrechnung ist die Verrechnung verwertbarer Gegenstände mit dem '
     'Preis der Räumung. Wir rechnen nichts gegen; der Festpreis gilt '
     'unabhängig davon, was gefunden wird.'),
    ('Haushaltsnahe Dienstleistung',
     'Eine haushaltsnahe Dienstleistung ist eine Arbeit im eigenen Haushalt, '
     'deren Arbeitskosten nach §35a EStG zu 20 % von der Steuer abgezogen '
     'werden können – etwa das Räumen von Keller oder Dachboden im bewohnten '
     'Haushalt, nicht aber die komplette Haushaltsauflösung.'),
]


# ── Die Uebersichtsseite ─────────────────────────────────────────────────────

_HUB = {
    'seo_title': 'Ratgeber Entrümpelung: Kosten, Begriffe | Rümpelwerk',
    'seo_description': (
        'Steuer, Sperrmüll, Asbest, Elektrogeräte, Erbe, Pflegeheim und '
        'besenreine Übergabe: der Ratgeber zur Entrümpelung mit Fundstellen. '
        'Jetzt lesen.'
    ),
    'answer_frage': 'Was sollte man vor einer Entrümpelung wissen?',
    'answer': (
        'Vor einer Entrümpelung sollte man drei Dinge wissen: was genau geräumt '
        'wird, wie sich der Preis zusammensetzt und in welchem Zustand das '
        'Objekt übergeben werden muss. Die Artikel von Rümpelwerk '
        'Mitteldeutschland beantworten diese Fragen mit echten Preisen ab '
        '{keller_ab} € und Fundstellen. Preisstand: {preisstand}.'
    ),
    # Die Einleitung: worauf sich die Artikel stuetzen. Das ist die Aussage,
    # an der ein Leser - und eine Antwortmaschine - die Texte messen kann.
    'einleitung_titel': 'Worauf sich diese Artikel stützen',
    'einleitung': [
        'Die Artikel beantworten die Fragen, die uns bei Anfragen am häufigsten '
        'gestellt werden: Was kostet die Räumung, was davon lässt sich von der '
        'Steuer absetzen, welcher Begriff passt zum eigenen Fall, und in welchem '
        'Zustand muss eine Wohnung übergeben werden? Sie verkaufen nichts; wer '
        'danach einen Preis braucht, findet ihn im Preisrechner.',
        'Jede Preisangabe stammt aus derselben Preisliste, mit der wir Angebote '
        'rechnen – Preisstand {preisstand}. Wo ein Gesetz oder ein Urteil die '
        'Antwort gibt, steht die Fundstelle im Text, etwa §35a '
        'Einkommensteuergesetz oder das Urteil des Bundesgerichtshofs zur '
        'besenreinen Rückgabe. Die Sperrmüllregeln der Städte stammen von den '
        'Websites der zuständigen Entsorger und sind dort verlinkt.',
        'Wo die Antwort vom Einzelfall abhängt – bei der Steuer nach einem '
        'Todesfall oder bei Schönheitsreparaturen im Mietvertrag –, sagen die '
        'Artikel das offen und verweisen auf Steuerberatung, Mieterverein oder '
        'Rechtsberatung. Eine Einzelfallberatung ersetzen sie nicht.',
        'Die Artikel sind in sechs Gruppen geordnet: Kosten und Steuern, '
        'Begriffe, Vorbereitung und Übergabe, Entsorgung und Schadstoffe, '
        'Erbe und Nachlass sowie Miete und Räumung. Die Artikel der letzten '
        'drei Gruppen stützen sich auf Gesetzestexte und amtliche Seiten; '
        'jeder Abschnitt nennt seine Quelle samt Abrufdatum. Unter den Gruppen '
        'steht ein Glossar mit den Wörtern, die in Angeboten und '
        'Mietverträgen immer wieder auftauchen.',
    ],
    # GE43: dieselben Quellen wie in den Artikeln, hier gesammelt. Aus dieser
    # einen Liste entsteht der Satz in der Einleitung **und** der
    # ``citation``-Eintrag des ``CollectionPage``-Knotens (Regel 12).
    'quellen': ['estg-35a', 'bgb-546', 'bgb-1922', 'krwg-17', 'krwg-53'],
}


def _hub_quellenorte(quellen):
    """Die Fundorte der Quellen: ``[(Host, Startadresse), ...]``, nach Host sortiert.

    Der Link zeigt auf die Startadresse des Herausgebers (Schema und Host der
    ersten Quelle dieses Hosts) - nicht auf eine einzelne Norm: Die Uebersicht
    zitiert keine Norm selbst, sie sagt, wo die Artikel nachzulesen sind.
    """
    orte = {}
    for q in quellen:
        host = _kurzadresse(q['url']).split('/')[0]
        schema = q['url'].split('://', 1)[0]
        orte.setdefault(host, f'{schema}://{q["url"].split("://", 1)[1].split("/")[0]}/')
    return sorted(orte.items())


def _hub_quellensatz_text(quellen):
    """Der Beleg der Uebersichtsseite als reiner Text - ohne jedes HTML.

    Die Uebersicht zitiert nichts selbst; sie sagt, worauf ihre Artikel sich
    stuetzen und wo das nachzulesen ist. Herausgeber und Adresse kommen aus
    ``_QUELLEN``, damit eine neue Quelle den Satz mitzieht.
    """
    herausgeber = sorted({q['herausgeber'] for q in quellen})
    orte = [host for host, _ in _hub_quellenorte(quellen)]
    return ('Die zitierten Vorschriften stehen im Volltext unter '
            f"{', '.join(orte)} ({' und '.join(herausgeber)}); welche Norm "
            'einen Abschnitt trägt, steht am Ende des Abschnitts.')


def _hub_quellensatz(quellen):
    """Derselbe Beleg als HTML-Satz: jeder Fundort ist ein Link (GE43).

    Nach dem Muster von ``quellen.satz()``: ``rel="noopener"`` (fremde
    Adresse, kein ``target``), jeder Wert maskiert, der sichtbare Text
    derselbe wie in :func:`_hub_quellensatz_text`.
    """
    herausgeber = sorted({q['herausgeber'] for q in quellen})
    links = ', '.join(
        f'<a href="{_escape(url, quote=True)}" rel="noopener">{_escape(host)}</a>'
        for host, url in _hub_quellenorte(quellen))
    return ('Die zitierten Vorschriften stehen im Volltext unter '
            f"{links} ({_escape(' und '.join(herausgeber))}); welche Norm "
            'einen Abschnitt trägt, steht am Ende des Abschnitts.')


# ── Zugriff ──────────────────────────────────────────────────────────────────

def _werte():
    """Alle Platzhalter: Preise aus ``services``, dazu Fristen und Staende."""
    from .city_lokal import STAND as _LOKAL_STAND
    werte = dict(_preis_platzhalter())
    werte.update({
        'besichtigung': _BESICHTIGUNG,
        'termin_regel': _TERMIN,
        'stand': STAND,
        'lokal_stand': _LOKAL_STAND,
    })
    return werte


def _fuellen(wert, werte):
    if isinstance(wert, str):
        return wert.format(**werte)
    if isinstance(wert, dict):
        return {k: _fuellen(v, werte) for k, v in wert.items()}
    if isinstance(wert, (list, tuple)):
        return [_fuellen(v, werte) for v in wert]
    return wert


@functools.lru_cache(maxsize=None)
def artikel(slug):
    """Ein Artikel mit eingesetzten Werten - oder ``None``."""
    roh = _RATGEBER_DATA.get(slug)
    if not roh:
        return None
    werte = _werte()
    # Der Rechtsstand eines Artikels kann vom Stand der aelteren abweichen
    # (SU07: die Wissensseiten vom 02.10.2026 tragen 'stand_iso').
    stand_iso = roh.get('stand_iso', STAND_ISO)
    if stand_iso != STAND_ISO:
        werte['stand'] = _deutsch(stand_iso)
    daten = _fuellen(roh, werte)
    daten['quellen'] = _quellen_einsetzen(daten)
    # rw_vergleich.html erwartet eine Liste - je Abschnitt hoechstens eine.
    for abschnitt in daten['abschnitte']:
        abschnitt['vergleiche'] = ([abschnitt['vergleich']]
                                   if abschnitt.get('vergleich') else [])
    daten['slug'] = slug
    daten['url'] = f'/ratgeber/{slug}/'
    daten['stand'] = _deutsch(stand_iso)
    daten['stand_iso'] = stand_iso
    return daten


def alle_artikel():
    """Alle Artikel in Reihenfolge - fuer Hub, Sitemap, Feed und llms.txt."""
    return [artikel(slug) for slug in _RATGEBER_DATA]


def artikel_zu_stadt(stadt_slug):
    """Die Artikel, die eine Stadt nennen - fuer den Hinweis auf der Stadtseite."""
    return [a for a in alle_artikel() if stadt_slug in a['staedte']]


def artikel_zu_leistung(leistung_slug):
    """Die Artikel, die auf eine Leistungsseite verweisen - fuer den Rueckweg."""
    return [a for a in alle_artikel() if leistung_slug in a['leistungen']]


@functools.lru_cache(maxsize=None)
def hub():
    """Texte der Uebersichtsseite, Glossar eingesetzt, Artikel nach Gruppe.

    Die Kostenseite ``/entruempelung-kosten/`` ist ein Ratgeber unter einem
    Leistungs-Slug (``services.RATGEBER_SEITEN``) und steht deshalb in der
    ersten Gruppe mit - sonst fehlte auf der Uebersicht der meistgelesene
    Wissenstext der Website.
    """
    werte = _werte()
    kosten = _leistung('entruempelung-kosten')
    gruppen = []
    for kategorie in KATEGORIEN:
        eintraege = [
            {'titel': a['titel'], 'url': a['url'], 'teaser': a['teaser']}
            for a in alle_artikel() if a['kategorie'] == kategorie
        ]
        if kategorie == KATEGORIEN[0] and kosten:
            eintraege.insert(0, {
                'titel': kosten['h1'], 'url': kosten['url'],
                'teaser': ('Quadratmetersätze, Mindestpreise und jeder '
                           'Zuschlag – mit drei durchgerechneten Beispielen.'),
            })
        gruppen.append({'titel': kategorie, 'eintraege': eintraege})
    daten = _fuellen(_HUB, werte)
    quellen = _quellen_aus(daten.pop('quellen'))
    # GE43: Der Beleg tritt an den Absatz, der ohnehin von Fundstellen
    # handelt - angehaengt, nicht als eigener Absatz (siehe _QUELLEN).
    # Die Absaetze laufen im Template durch ``|safe`` (der Satz traegt Links):
    # darum wird der uebrige Text hier maskiert, nicht erst dort.
    daten['einleitung'] = [_escape(p) for p in daten['einleitung']]
    daten['einleitung'][1] += ' ' + _hub_quellensatz(quellen)
    return {
        **daten,
        'gruppen': gruppen,
        'glossar': glossar(werte),
        'quellen': quellen,
        'stand': STAND,
        'stand_iso': STAND_ISO,
    }


_UMSCHRIFT = str.maketrans({'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss'})


def glossar_anker(begriff):
    """``'Füllgrad'`` -> ``'begriff-fuellgrad'`` - Sprungziel und Schema-URL."""
    wort = begriff.lower().translate(_UMSCHRIFT)
    return 'begriff-' + '-'.join(''.join(z if z.isalnum() else ' '
                                         for z in wort).split())


def glossar(werte=None):
    """Das Glossar mit eingesetzten Werten und Anker - fuer Seite und Schema."""
    werte = werte or _werte()
    return [{'begriff': b, 'text': t.format(**werte), 'anker': glossar_anker(b)}
            for b, t in GLOSSAR]


def lokal_staedte():
    """Die Sperrmuellregeln der Standortstaedte, **wortgleich** aus city_lokal.

    Wortgleich ist Absicht: ``check_seo`` erkennt eine Zeitangabe ohne Ziffer
    ("bis zu fünf Wochen") nur dann als kommunale Auskunft, wenn der Satz so
    in ``city_lokal.py`` steht. Umformuliert waere er eine Zusage des
    Betriebs ohne Quelle.
    """
    aus = []
    for slug in _STANDORTE:
        stadt, lokal = _CITY_DATA.get(slug), _LOKAL.get(slug) or {}
        if not stadt or not lokal.get('sperrmuell'):
            continue
        aus.append({
            'name': stadt['name'], 'slug': slug,
            'url': f'/entrumpelung/{slug}/',
            'traeger': lokal.get('traeger', ''),
            'sperrmuell': lokal['sperrmuell'],
            # 02.10.2026: Die Sperrmuell-Karte hat ihre eigene Quelle
            # (``sperrmuell_quelle``, siehe Kopf von city_lokal.py). Bis dahin
            # verlinkte der Artikel fuer Chemnitz, Magdeburg und Hannover die
            # Wertstoffhof-Seite, die den Sperrmuell-Satz nicht traegt.
            'quelle': lokal.get('sperrmuell_quelle') or lokal.get('quelle', ''),
        })
    return aus
