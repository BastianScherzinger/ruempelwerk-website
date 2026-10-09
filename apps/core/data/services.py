"""Leistungsseiten als Daten – das Gegenstueck zu ``cities.py`` (A2).

Dieselbe Entscheidung, die ``_CITY_DATA`` fuer 54 Stadtseiten richtig gemacht
hat: **Inhalt als Daten, Darstellung als ein Template.** Acht handgeschriebene
HTML-Dateien waeren acht Orte, an denen ein Schema-Fehler, ein veralteter Preis
oder ein vergessenes ``seo_path`` sitzen kann – und genau diese Fehlerklassen
hat das Projekt schon durch.

**Keine Preiszahl in diesem Modul.** Wo ein Preis im Text steht, steht ein
Platzhalter in geschweiften Klammern (``{haus_ab}``, ``{maler_rate}``), den
``leistung()`` aus ``pricing.py`` fuellt. Damit gilt fuer die Leistungsseiten
dieselbe Regel wie fuer alles andere: ``data/pricing.py`` ist die einzige
Wahrheit. Wer hier eine Zahl eintippt, baut die Doppelung wieder auf, die in F2
aufgeloest wurde.

Wichtig fuer den Text selbst: **geschweifte Klammern sind reserviert.** Ein
literales ``{`` im Fliesstext laesst ``str.format()`` scheitern – das ist
Absicht, ein stiller Ausfall waere schlimmer als ein Fehler beim ersten Aufruf.

Wie ``cities.py`` und ``pricing.py`` importiert dieses Modul **nichts aus
``apps.core``** – sonst entsteht ein Zirkel ueber ``context_processors``.
"""

import functools

from .cities import _CITY_DATA
from .quellen import einsetzen as _quellen_einsetzen
from .zusagen import (ANGEBOT_BEI_BESICHTIGUNG as _ANGEBOT_FRIST,
                      ANTWORT as _REAKTION,
                      RECHNER_DAUER as _RECHNER_DAUER)
from .pricing import (
    _MALER_PER_QM,
    _STANDORT_RABATT_STAEDTE,
    _OBJEKTART_LABELS,
    berechne_preis,
    euro,
    preis_context,
)

__all__ = ['_SERVICE_DATA', 'leistung', 'alle_leistungen', 'beispiel_preise']


# ── Die Leistungen ───────────────────────────────────────────────────────────
#
# Pflichtfelder je Eintrag (das Template erwartet sie):
#   name, h1, h1_em, keyword, objektart, hero_sub, answer, answer_frage,
#   leistungsumfang,
#   abgrenzung, abschnitte, ablauf, faq, related, staedte,
#   seo_title, seo_description, seo_keywords
#
# Optional:
#   vergleich       – Tabelle im Abschnitt 'unterschied'
#   beispiele       – durchgerechnet, siehe unten
#   label           – Beschriftung in Navigation, Footer, Brotkrumen und auf den
#                     'Passt dazu'-Karten. Standard ist ``name``. Noetig, wo der
#                     Seitenname und das Wort im Satz auseinanderfallen:
#                     /entruempelung-kosten/ heisst im Menue 'Entrümpelung
#                     Kosten', im Satz aber 'eine Entrümpelung'.
#   preistabelle    – 'entruempelung' (Standard) oder 'sanierung'. Die
#                     Renovierungsseite rechnet nach ``_MALER_PER_QM`` und
#                     ``_KLEIN_SAN_ITEMS``; die Objektart-Tabelle waere dort
#                     schlicht die falsche Preisliste.
#   modifikatoren   – True blendet die Zuschlagstabelle ein (Fuellgrad,
#                     Stockwerk, Sonderabfall). Nur fuer die Kostenseite.
#
# ``objektart`` verknuepft die Seite mit der Preistabelle und belegt den
# eingebetteten Rechner vor: der Schluessel muss in ``_PER_QM_PREISE``
# existieren. ``None`` ist erlaubt und bedeutet 'keine einzelne Objektart' -
# dann zeigt der Rechner die freie Auswahl und das Schema kein ``offers``.

_SERVICE_DATA = {

    # ───────────────────────────────────────────────────────────────────────
    'haushaltsaufloesung': {
        'name': 'Haushaltsauflösung',
        'h1': 'Haushaltsauflösung',
        # Kurz halten: Der Hero setzt die H1 mit bis zu 4rem. Die erste Fassung
        # („zum Festpreis, besenrein übergeben“) lief über vier Zeilen und
        # drückte CTA und Vertrauenszeile unter die Falz.
        'h1_em': 'Festpreis. Besenrein.',
        'keyword': 'haushaltsauflösung',
        'objektart': 'haus',

        'hero_sub': (
            'Kompletter Hausstand statt einzelner Räume: Möbel, Hausrat, '
            'Elektrogeräte, Keller und Dachboden. Wir räumen in Sachsen-Anhalt, '
            'Sachsen und Niedersachsen – mit Festpreis ab '
            '{haus_ab} € nach kostenloser Besichtigung.'
        ),

        # Antwort zuerst (G2): 40–60 Wörter, beantwortet die Suchanfrage direkt.
        # Generative Suchmaschinen ziehen bevorzugt den ersten zusammenhängenden
        # Absatz, der die Frage ohne Vorrede beantwortet.
        #
        # ``answer_frage`` ist die Überschrift darüber und seit dem 27.08.2026
        # sichtbar: G2 verlangt, dass die <h2> die Suchanfrage in der Form
        # stellt, in der Menschen sie tippen. Die Matrixseiten leiten ihre
        # Frage daraus ab (matrix.py) – kein zweiter Satz, der abweichen kann.
        'answer_frage': 'Was kostet eine Haushaltsauflösung?',
        'answer': (
            'Eine Haushaltsauflösung ist die vollständige Räumung eines Hauses '
            'oder einer Wohnung samt Möbeln, Hausrat, Elektrogeräten, Keller und '
            'Dachboden. Rümpelwerk Mitteldeutschland übernimmt sie zum Festpreis '
            'ab {haus_ab} € – besenrein übergeben, auf Wunsch mit '
            'Entsorgungsnachweis. Der Preis steht nach der kostenlosen '
            'Besichtigung als Festpreis im verbindlichen Angebot. '
            'Preisstand: {preisstand}.'
        ),

        'leistungsumfang': [
            'Alle Wohnräume, Küche, Bad, Flur – einschließlich Einbaumöbeln',
            'Keller, Dachboden, Garage, Gartenhaus und Nebengelass',
            'Möbel, Hausrat, Kleidung, Geschirr, Bücher, Teppiche',
            'Elektrogroßgeräte und Elektroschrott, fachgerecht getrennt',
            'Abbau von Küchen, Schränken, Lampen und Gardinenschienen',
            'Transport, Entsorgungsgebühren und Arbeitslohn im Festpreis',
            'Besenreine Übergabe an Eigentümer, Erben, Makler oder Vermieter',
            'Entsorgungsnachweis auf Wunsch – für Nachlass und Buchhaltung',
        ],

        # Was NICHT enthalten ist. Steht bewusst gleich neben dem Umfang: Eine
        # Leistungsseite, die nur aufzählt, was alles geht, liest sich wie jede
        # andere. Die Grenze ist das, was Vertrauen erzeugt – und sie verhindert
        # Nachverhandlungen auf der Baustelle.
        'abgrenzung': [
            'Umzugstransporte: Was Sie behalten wollen, stellen wir beiseite und '
            'übergeben es Ihnen. Der Transport an eine neue Adresse ist kein '
            'Bestandteil der Haushaltsauflösung.',
            'Schadstoffsanierung: Asbest, künstliche Mineralfasern und ähnliche '
            'Stoffe gehören in die Hand eines dafür zugelassenen Fachbetriebs. '
            'Wir sagen Ihnen bei der Besichtigung, wenn wir so etwas sehen.',
            'Wertermittlung: Wir sind kein Auktionshaus und erstellen keine '
            'Gutachten über Antiquitäten, Schmuck oder Sammlungen.',
            'Renovierung: Malerarbeiten, Böden und Kleinreparaturen sind eine '
            'eigene Leistung mit eigenem Preis – ab {maler_rate} €/m², '
            'mindestens {maler_min} €. Auf Wunsch im selben Auftrag.',
        ],

        # Der Fließtext. Jeder Abschnitt wird als <h2> + Absätze gerendert;
        # 'liste' ist optional.
        'abschnitte': [
            {
                'id': 'unterschied',
                'titel': 'Haushaltsauflösung oder Entrümpelung – was ist der Unterschied?',
                'absaetze': [
                    'Die beiden Begriffe werden im Alltag synonym benutzt, meinen '
                    'aber zwei verschiedene Aufträge. Eine <strong>Entrümpelung</strong> '
                    'ist eine Teilräumung: Der Keller wird leer, der Dachboden, ein '
                    'einzelnes Zimmer. Das Objekt bleibt bewohnt, der Haushalt bleibt '
                    'bestehen. Eine <strong>Haushaltsauflösung</strong> löst den '
                    'gesamten Hausstand auf. Danach ist das Objekt leer und wird '
                    'übergeben, verkauft oder neu vermietet.',
                    'Der Unterschied ist nicht nur sprachlich, er ändert die '
                    'Kalkulation: Bei der Teilräumung zählt der geräumte Raum, bei '
                    'der Auflösung die gesamte Wohnfläche. Deshalb beginnt eine '
                    'Kellerentrümpelung bei {keller_ab} €, eine Haushaltsauflösung '
                    'dagegen bei {haus_ab} €.',
                    'Für Mietwohnungen gibt es einen dritten Fall: die '
                    '<strong>Wohnungsauflösung</strong>. Dort bestimmt nicht der '
                    'Eigentümer den Zeitplan, sondern der Mietvertrag – Kündigungs'
                    'frist, Übergabetermin und Wohnungsübergabeprotokoll.',
                ],
            },
            {
                'id': 'anlaesse',
                'titel': 'Wann eine Haushaltsauflösung ansteht',
                'absaetze': [
                    'Vier Anlässe machen den größten Teil unserer Aufträge aus. Sie '
                    'unterscheiden sich weniger in der Arbeit als im Zeitdruck und '
                    'darin, wer entscheidet.',
                ],
                'liste': [
                    '<strong>Todesfall.</strong> Angehörige stehen zwischen Trauer, '
                    'Fristen und einer Wohnung voller Erinnerungen. Wir gehen dabei '
                    'anders vor als bei einem Umzug – wie genau, steht auf der Seite '
                    'zur Nachlassräumung.',
                    '<strong>Umzug ins Pflegeheim.</strong> Meist eilig, oft '
                    'entscheidet eine bevollmächtigte Person. Ein kleiner Teil des '
                    'Hausrats zieht mit um; wir stellen ihn beiseite, statt ihn '
                    'mitzuräumen.',
                    '<strong>Verkleinerung.</strong> Aus dem Haus wird eine Wohnung. '
                    'Hier ist die Frage nicht, was weg soll, sondern was bleibt – '
                    'dafür brauchen Sie Zeit, und die planen wir ein.',
                    '<strong>Immobilienverkauf.</strong> Käufer und Makler erwarten '
                    'ein leeres, besenreines Objekt zum Notartermin. Der Termin steht '
                    'fest, bevor die Räumung beginnt – deshalb ist er bei uns Teil '
                    'des Angebots und keine Absichtserklärung.',
                ],
            },
            {
                'id': 'wertgegenstaende',
                'titel': 'Wertgegenstände, Dokumente und Erinnerungsstücke',
                'absaetze': [
                    'Bei einer Haushaltsauflösung kommt regelmäßig etwas zum '
                    'Vorschein, das niemand mehr auf dem Schirm hatte: Sparbücher, '
                    'Versicherungspolicen, Schmuck, Bargeld in Büchern, alte Fotos, '
                    'Briefe. Wir sammeln solche Funde getrennt und übergeben sie '
                    'Ihnen – das ist bei uns Teil des Auftrags, nicht eine Geste.',
                    'Was wir <strong>nicht</strong> tun: Hausrat ankaufen oder einen '
                    '„Wertausgleich“ gegen den Preis rechnen. Der Festpreis steht vor '
                    'Beginn und hängt nicht davon ab, was wir finden. Wenn Sie '
                    'Möbel oder Sammlungen verkaufen möchten, tun Sie das vor dem '
                    'Räumungstermin – was dann noch da ist, räumen wir.',
                    'Sagen Sie uns bei der Besichtigung, worauf wir achten sollen. '
                    'Ein Satz wie „in der Kommode im Schlafzimmer müssten noch Papiere '
                    'liegen“ erspart hinterher die Suche im Container.',
                ],
            },
            {
                'id': 'entsorgung',
                'titel': 'Was mit dem Hausrat passiert',
                'absaetze': [
                    'Ein aufgelöster Haushalt ist kein Müllberg, sondern ein Gemisch '
                    'aus Wertstoffen, Gebrauchtem und Restmüll. Wir trennen von Hand, '
                    'bevor etwas auf den Wagen geht: Metall, Holz, Elektrogeräte, '
                    'Papier, Textilien und Restabfall gehen getrennte Wege. Was noch '
                    'brauchbar ist, geben wir an Secondhand-Stellen und soziale '
                    'Einrichtungen weiter.',
                    'Auf Wunsch bekommen Sie einen <strong>Entsorgungsnachweis</strong>. '
                    'Bei einem Nachlass ist er die Grundlage gegenüber der '
                    'Erbengemeinschaft, bei vermieteten Objekten gegenüber der '
                    'Hausverwaltung.',
                    'Elektrogeräte dürfen nicht in den Restmüll: Das Elektro- und '
                    'Elektronikgerätegesetz verlangt, dass Altgeräte getrennt vom '
                    'unsortierten Siedlungsabfall erfasst werden, und Batterien und '
                    'herausnehmbare Lampen vorher entnommen sind. Farben, Lacke und '
                    'Batterien gehen in die Schadstoffsammlung. Wenn Sie vorab selbst '
                    'etwas zum Wertstoffhof bringen, lassen Sie diese Dinge also '
                    'nicht in einem Sack mit dem Rest.',
                ],
            },
            {
                'id': 'besenrein',
                'titel': 'Was „besenrein“ tatsächlich bedeutet',
                'absaetze': [
                    'Besenrein heißt: Das Objekt ist vollständig geräumt, der Boden '
                    'gefegt, grober Schmutz entfernt. Dübel, Nägel und Wandhaken '
                    'nehmen wir mit heraus. Was besenrein <em>nicht</em> heißt: '
                    'gewischt, Fenster geputzt, Wände gestrichen.',
                    'Das ist keine Wortklauberei, sondern der Punkt, an dem es bei '
                    'einer Wohnungsübergabe regelmäßig hakt. Wenn der Vermieter oder '
                    'Käufer mehr erwartet, sagen Sie es uns vorher – Endreinigung und '
                    'Malerarbeiten lassen sich in denselben Auftrag legen und stehen '
                    'dann mit im Festpreis.',
                ],
            },
            {
                'id': 'steuer',
                'titel': 'Ist eine Haushaltsauflösung steuerlich absetzbar?',
                'absaetze': [
                    'Oft liest man, eine Haushaltsauflösung sei nach §35a EStG '
                    'absetzbar. Die Finanzverwaltung sieht das anders: Ihre '
                    'Beispielliste zu §35a führt die <strong>Haushaltsauflösung</strong> '
                    'ausdrücklich als <strong>nicht begünstigt</strong>, ebenso die '
                    'Entsorgung, wenn sie die Hauptleistung ist. Planen Sie den '
                    'Steuerabzug deshalb nicht fest ein.',
                    'Begünstigt sein können Arbeiten, die zu Ihrem eigenen Umzug '
                    'gehören – etwa Malerarbeiten in der Wohnung, aus der Sie '
                    'ausziehen. Wann das gilt und was Sie dafür brauchen, steht auf '
                    '<a href="/entruempelung-kosten/#steuer">Entrümpelung Kosten</a>. '
                    'Ob Ihr Fall dazugehört, klärt Ihr Steuerberater.',
                ],
            },
        ],

        'quellen': [
            {'schluessel': 'bmf-35a-anlage1', 'abschnitt': 'steuer',
             'bezug': 'Die Haushaltsauflösung steht dort in der Spalte „nicht '
                      'begünstigt“'},
        ],

        # Vergleichstabelle. Echte <table> statt Prosa: Für Nutzer ist die
        # Zuordnung damit eindeutig, und generative Suchmaschinen zitieren
        # Tabellen deutlich häufiger als denselben Inhalt im Fließtext.
        'vergleich': {
            'titel': 'Entrümpelung, Haushaltsauflösung, Wohnungsauflösung im Vergleich',
            'eigene_spalte': 3,
            'fazit_frage': 'Was ist der Unterschied zwischen Entrümpelung, Haushaltsauflösung und Wohnungsauflösung?',
            'fazit': ('Der Unterschied liegt im Umfang, nicht im Verfahren. Eine Entrümpelung leert einzelne Räume, das Objekt wird weiter bewohnt – ab {keller_ab} €. Eine Haushaltsauflösung löst den gesamten Hausstand auf, meist nach Todesfall oder Umzug ins Pflegeheim – ab {haus_ab} €. Eine Wohnungsauflösung ist die Räumung einer Mietwohnung bis zur besenreinen Rückgabe – ab {wohnung_ab} €. Wer nur den Keller leeren will, braucht keine Haushaltsauflösung. Preisstand: {preisstand}.'),
            'kopf': ['', 'Entrümpelung', 'Haushaltsauflösung', 'Wohnungsauflösung'],
            'zeilen': [
                ['Umfang', 'einzelne Räume', 'kompletter Hausstand',
                 'komplette Mietwohnung'],
                ['Typischer Anlass', 'Platz schaffen, Keller, Dachboden',
                 'Todesfall, Pflegeheim, Verkauf', 'Auszug, Mietende, Nachlass'],
                ['Objekt danach', 'weiter bewohnt', 'leer, wird übergeben',
                 'leer, Rückgabe an Vermieter'],
                ['Wer beauftragt', 'Bewohner, Eigentümer', 'Eigentümer, Erben',
                 'Mieter, Erben, Hausverwaltung'],
                ['Termin bestimmt', 'Sie selbst', 'Notar- oder Übergabetermin',
                 'Mietvertrag und Kündigungsfrist'],
                ['Preis ab', '{keller_ab} €', '{haus_ab} €', '{wohnung_ab} €'],
            ],
        },

        # Durchgerechnete Beispiele. Die Zahlen entstehen NICHT hier, sondern in
        # beispiel_preise() über berechne_preis() – also über denselben Code, den
        # auch der Rechner und die Bestätigungsmail benutzen.
        'beispiele': [
            {
                'titel': 'Reihenhaus, 100 m², normal möbliert',
                'beschreibung': 'Erdgeschoss bis Dachboden, keine Sonderabfälle, '
                                'Füllgrad mittel.',
                'args': {'objektart': 'haus', 'qm': 100, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Einfamilienhaus, 140 m², voll',
                'beschreibung': 'Vier Jahrzehnte Hausrat inklusive Keller und '
                                'Garage, dazu einzelne Sonderabfälle wie Farben '
                                'und Lacke.',
                'args': {'objektart': 'haus', 'qm': 140, 'fuellgrad': 'voll',
                         'sonderabfall': 'wenige'},
            },
            {
                'titel': '3-Zimmer-Wohnung, 75 m², 2. OG ohne Aufzug',
                'beschreibung': 'Kompletter Hausstand einer Wohnung – gerechnet '
                                'als Wohnungsauflösung mit Stockwerkzuschlag.',
                'args': {'objektart': 'wohnung', 'qm': 75, 'stockwerk': '2og',
                         'fuellgrad': 'mittel'},
            },
        ],

        'ablauf': [
            {'titel': 'Anfrage',
             'text': 'Per WhatsApp, Formular oder Telefon. Ein paar Fotos aus jedem '
                     'Raum reichen für eine erste Einschätzung; wir melden uns in '
                     '{reaktion}.'},
            {'titel': 'Kostenlose Besichtigung',
             'text': 'Wir sehen uns das Objekt vor Ort an: Wohnfläche, Menge, Zugang, '
                     'Treppenhaus, Parksituation. Ohne diesen Termin gibt es keinen '
                     'Festpreis, sondern nur eine Schätzung.'},
            {'titel': 'Festpreisangebot',
             'text': 'Schriftlich, {angebot_frist}, mit Termin. '
                     'Auf Anfrage mit ausgewiesenen Arbeitskosten für die Steuer.'},
            {'titel': 'Räumung',
             'text': 'Unser Team räumt, trennt und verlädt. Wertgegenstände und '
                     'Dokumente legen wir beiseite, Behaltenes stellen wir zusammen. '
                     'Sie müssen nicht dabei sein.'},
            {'titel': 'Übergabe',
             'text': 'Besenreine Abnahme gemeinsam mit Ihnen oder direkt mit '
                     'Vermieter, Makler oder Hausverwaltung. Entsorgungsnachweis auf '
                     'Wunsch, Schlüsselübergabe nach Absprache.'},
        ],

        'faq': [
            ('Was kostet eine Haushaltsauflösung?',
             'Eine Haushaltsauflösung beginnt bei {haus_ab} € und wird darüber nach '
             'Wohnfläche gerechnet – Richtwert {haus_rate} € pro m². Für eine '
             'Wohnung gilt {wohnung_rate} € pro m² ab {wohnung_ab} €. Auf diesen '
             'Grundpreis wirken Füllgrad, Stockwerk ohne Aufzug und Sonderabfall. '
             'Der Preisrechner nennt in {rechner_dauer} einen konkreten Wert, '
             'verbindlich wird er nach der kostenlosen Besichtigung. '
             'Preisstand: {preisstand}.'),
            ('Wie lange dauert eine Haushaltsauflösung?',
             'Das hängt an Menge und Zugang, nicht allein an der Quadratmeterzahl: '
             'Ein zweiter Stock ohne Aufzug kostet mehr Zeit als ein doppelt so '
             'großes Erdgeschoss. Den Zeitbedarf schätzen wir bei der Besichtigung '
             'und schreiben ihn ins Angebot.'),
            ('Muss ich bei der Haushaltsauflösung anwesend sein?',
             'Zur Besichtigung ja – Sie oder eine bevollmächtigte Person, denn dort '
             'wird der Umfang festgelegt. Bei der Räumung selbst nicht. Viele '
             'Auftraggeber wohnen weit weg; Schlüsselübergabe und Abnahme regeln wir '
             'dann direkt mit Vermieter, Makler oder Hausverwaltung.'),
            ('Was passiert mit Wertgegenständen und Dokumenten?',
             'Wir sammeln Papiere, Fotos, Schmuck und Bargeld getrennt und übergeben '
             'sie Ihnen. Angekauft wird nichts, und es wird auch nichts gegen den '
             'Preis gerechnet: Der Festpreis steht vor Beginn fest, unabhängig davon, '
             'was gefunden wird. Sagen Sie uns vorher, worauf wir besonders achten '
             'sollen.'),
            ('Ist eine Haushaltsauflösung steuerlich absetzbar?',
             'In der Regel nicht. Die Beispielliste des Bundesfinanzministeriums '
             'zu §35a EStG führt die Haushaltsauflösung als nicht begünstigt. '
             'Begünstigt sein können Arbeiten im Zusammenhang mit Ihrem eigenen '
             'Umzug, etwa Malerarbeiten in der bisherigen Wohnung. Dafür brauchen '
             'Sie eine Rechnung mit ausgewiesenen Arbeitskosten – sprechen Sie '
             'uns darauf an – und eine Überweisung statt Barzahlung. Ob Ihr Fall '
             'dazugehört, klärt Ihr Steuerberater.'),
            ('Was heißt besenrein?',
             'Vollständig geräumt, Boden gefegt, grober Schmutz entfernt, Dübel und '
             'Nägel heraus. Nicht enthalten sind Wischen, Fensterreinigung und '
             'Malerarbeiten. Wenn bei der Übergabe mehr verlangt wird, sagen Sie es '
             'vorher – Endreinigung und Renovierung lassen sich in denselben Auftrag '
             'legen.'),
            ('Wie schnell bekomme ich einen Termin?',
             'In unserem Kerngebiet in Sachsen-Anhalt und Sachsen melden wir uns in '
             '{reaktion} zurück und stimmen die Besichtigung mit Ihnen ab. '
             'Bei festen Übergabe- oder Notarterminen sagen wir Ihnen '
             'ehrlich, ob wir es schaffen – lieber eine Absage als ein gerissener '
             'Termin.'),
            ('Übernehmen Sie auch Renovierung und Malerarbeiten danach?',
             'Ja. Malerarbeiten rechnen wir mit {maler_rate} € pro m² ab, mindestens '
             '{maler_min} €; dazu kommen Kleinreparaturen wie Sockelleisten, '
             'Wandlöcher oder Fliesen als Einzelpositionen. Im selben Auftrag ist das '
             'meist günstiger und immer schneller, weil das Objekt schon leer ist.'),
            ('Haushalt auflösen, Beräumung, Wohnungsräumung – ist das '
             'dasselbe?',
             'Weitgehend ja. „Haushaltsauflösung", „Haushalt auflösen", '
              '„Beräumung", „Wohnungsräumung", „räumen lassen" und '
              '„Entrümpelung" meinen im Alltag dieselbe Arbeit; „Beräumung" '
              'ist der Begriff, den Behörden und Hausverwaltungen benutzen. '
              'Ein echter Unterschied besteht nur im Umfang: Bei einer '
              'Haushaltsauflösung geht der komplette Hausstand raus, bei '
              'einer Entrümpelung nur ein Teil. Auf den Preis wirkt das Wort '
              'nicht – gerechnet wird nach Fläche, Füllgrad und Zugang. Der '
              'Rechner nennt für beides denselben Wert.'),
            ('Arbeiten Sie in ganz Sachsen-Anhalt und Sachsen?',
             'Ja. Unser Einsatzgebiet umfasst {staedte_anzahl} Städte in Sachsen-Anhalt, '
              'Sachsen und Niedersachsen – von '
              'Stendal bis Plauen, von Görlitz bis Wernigerode. Für jede '
              'dieser Städte gibt es eine eigene Seite mit den örtlichen '
              'Entsorgungsregeln, dem zuständigen Träger und durchgerechneten '
              'Beispielen.'),
        ],

        'related': ['wohnungsaufloesung', 'nachlassraeumung',
                    'sanierung-renovierung', 'entruempelung-kosten'],

        # Städte, in denen die Leistung ausdrücklich beworben wird. Slugs aus
        # _CITY_DATA – die View löst sie zu Namen und Links auf, damit hier kein
        # Ortsname doppelt gepflegt wird.
        'staedte': ['leipzig', 'halle', 'magdeburg', 'dresden', 'chemnitz',
                    'hannover', 'merseburg', 'dessau', 'bitterfeld',
                    'weissenfels', 'zwickau', 'stendal'],

        'seo_title': 'Haushaltsauflösung ab {haus_ab} € – Festpreis | Rümpelwerk',
        'seo_description': (
            'Haushaltsauflösung ab {haus_ab} € zum Festpreis: Möbel, Hausrat, '
            'Keller und Dachboden. Besenrein, auf Wunsch mit Nachweis. '
            'Angebot anfordern.'
        ),
        'seo_keywords': (
            'Haushaltsauflösung, Haushaltsauflösung Kosten, Haushalt auflösen, '
            'Haushaltsauflösung Firma, Haushaltsauflösung Sachsen-Anhalt, '
            'Haushaltsauflösung Festpreis, Entrümpelung Haushalt, '
            'Haushaltsauflösung besenrein'
        ),
    },

    # ───────────────────────────────────────────────────────────────────────
    # A5 — /wohnungsaufloesung/
    #
    # Die Abgrenzung zu A4 ist hier keine Feinheit, sondern der Existenzgrund
    # der Seite: A4 ist der Hausstand (Eigentum, Nachlass), A5 das
    # Mietverhältnis. Ohne diese Trennung im Text kannibalisieren sich beide.
    #
    # Die Synonyme stammen aus dem GSC-Export: „Wohnungsräumung",
    # „Wohnungsberäumung", „Beräumung" und „Wohnungsentrümpelung" bringen
    # Impressionen auf Position 1–8, ohne dass es je eine Seite dafür gab.
    # „Beräumung" ist dabei kein Fülltext, sondern der in Sachsen und
    # Sachsen-Anhalt gebräuchliche Ausdruck.
    'wohnungsaufloesung': {
        'name': 'Wohnungsauflösung',
        'h1': 'Wohnungsauflösung',
        'h1_em': 'Termingerecht. Besenrein.',
        'keyword': 'wohnungsauflösung',
        'objektart': 'wohnung',

        'hero_sub': (
            'Mietwohnung komplett räumen lassen – rechtzeitig vor dem '
            'Übergabetermin, besenrein und mit Protokoll. Wir arbeiten in '
            'Sachsen-Anhalt, Sachsen und Niedersachsen zum Festpreis ab '
            '{wohnung_ab} € nach kostenloser Besichtigung.'
        ),

        'answer_frage': 'Was kostet eine Wohnungsauflösung?',
        'answer': (
            'Eine Wohnungsauflösung ist die vollständige Räumung einer Mietwohnung '
            'samt Keller- und Bodenabteil vor der Rückgabe an den Vermieter. '
            'Rümpelwerk Mitteldeutschland übernimmt sie zum Festpreis ab '
            '{wohnung_ab} € – Richtwert {wohnung_rate} € pro m², besenrein und zum '
            'vereinbarten Übergabetermin. Der Preis steht nach der kostenlosen '
            'Besichtigung als Festpreis im verbindlichen Angebot. '
            'Preisstand: {preisstand}.'
        ),

        'leistungsumfang': [
            'Alle Wohnräume, Küche, Bad, Flur, Balkon und Abstellkammer',
            'Keller- und Bodenabteil, Garage und Stellplatz, wenn mitvermietet',
            'Abbau von Einbauküche, Schränken, Lampen und Gardinenschienen',
            'Möbel, Hausrat, Textilien, Elektrogeräte und Elektroschrott',
            'Teppichboden und Laminat aufnehmen, wenn der Vermieter das verlangt',
            'Dübel, Nägel und Haken entfernen, Bohrlöcher auf Wunsch verspachtelt',
            'Besenreine Übergabe – auf Wunsch direkt an Vermieter oder Hausverwaltung',
            'Entsorgungsnachweis, wenn Hausverwaltung oder Gericht ihn braucht',
        ],

        'abgrenzung': [
            'Umzug: Was mitkommt, stellen wir beiseite und übergeben es Ihnen. Der '
            'Transport an die neue Adresse ist eine Umzugsleistung und nicht '
            'Bestandteil der Wohnungsauflösung.',
            'Rechtsberatung: Ob eine Klausel zu Schönheitsreparaturen in Ihrem '
            'Mietvertrag wirksam ist, sagt Ihnen ein Mieterverein oder ein Anwalt. '
            'Wir beschreiben, was uns in der Praxis begegnet – mehr nicht.',
            'Zwangsräumungen ordnen wir nicht an. Als ausführender Dienstleister im '
            'Auftrag eines Gerichtsvollziehers oder einer Hausverwaltung arbeiten '
            'wir mit; die Anordnung selbst kommt nie von uns.',
            'Renovierung ist eine eigene Leistung mit eigenem Preis: Malerarbeiten '
            'ab {maler_rate} €/m², mindestens {maler_min} €. Im selben Auftrag '
            'möglich und meist günstiger, weil die Wohnung dann schon leer ist.',
        ],

        'abschnitte': [
            {
                'id': 'unterschied',
                'titel': 'Wohnungsauflösung, Haushaltsauflösung oder Entrümpelung?',
                'absaetze': [
                    'Die drei Begriffe beschreiben ähnliche Arbeit in drei '
                    'verschiedenen Rechtslagen – und genau die entscheidet über '
                    'Zeitplan und Aufwand. Bei einer <strong>Entrümpelung</strong> '
                    'wird ein Teil geräumt, die Wohnung bleibt bewohnt. Bei einer '
                    '<a href="/haushaltsaufloesung/">Haushaltsauflösung</a> löst sich '
                    'ein kompletter Hausstand auf, meist im Eigentum und ohne fremden '
                    'Termindruck.',
                    'Die <strong>Wohnungsauflösung</strong> ist der Mietfall. Hier '
                    'bestimmt nicht der Auftraggeber den Zeitpunkt, sondern der '
                    'Mietvertrag: Kündigungsfrist, Rückgabetermin, Übergabeprotokoll. '
                    'Wer einen Tag zu spät fertig wird, zahlt unter Umständen eine '
                    'weitere Monatsmiete – deshalb steht bei uns der Übergabetermin '
                    'im Angebot und nicht nur die Leistung.',
                    'Regional heißen dieselben Aufträge auch '
                    '<strong>Wohnungsräumung</strong>, '
                    '<strong>Wohnungsberäumung</strong> oder schlicht '
                    '<strong>Beräumung</strong>. Gemeint ist jedes Mal dasselbe: Die '
                    'Wohnung ist danach leer und wird zurückgegeben.',
                ],
            },
            {
                'id': 'fristen',
                'titel': 'Fristen, Übergabetermin und die Rechnung ohne Kalender',
                'absaetze': [
                    'Die gesetzliche Kündigungsfrist für Mieter beträgt knapp drei '
                    'Monate. Das klingt reichlich – ist es aber nicht, wenn die '
                    'Wohnung 200 Kilometer entfernt liegt, der Mieter ins Pflegeheim '
                    'gezogen ist oder eine Erbengemeinschaft sich erst einigen muss. '
                    'Bis alle Beteiligten entschieden haben, was bleibt, ist von der '
                    'Frist oft nur noch ein kleiner Teil übrig.',
                    'Legen Sie den Räumungstermin deshalb <strong>vor</strong> den '
                    'Übergabetermin, nicht auf denselben Tag. Zwei bis drei Werktage '
                    'dazwischen sind der Puffer für Endreinigung, kleine Reparaturen '
                    'und für den Fall, dass der Vermieter bei der Vorabnahme etwas '
                    'anmerkt.',
                    'Stirbt ein Mieter, endet das Mietverhältnis nicht automatisch. '
                    'Tritt niemand aus dem Haushalt in den Vertrag ein, geht er auf '
                    'die Erben über; Erbe und Vermieter können dann <strong>innerhalb '
                    'eines Monats</strong> außerordentlich mit der gesetzlichen Frist '
                    'kündigen. Der Monat läuft, sobald beide vom Tod wissen und '
                    'davon, dass niemand eintritt. Wer ihn '
                    'verstreichen lässt, ist an die normale Kündigung gebunden – '
                    'wie es danach mit der Räumung weitergeht, steht auf der Seite '
                    'zur <a href="/nachlassraeumung/">Nachlassräumung</a>.',
                ],
            },
            {
                'id': 'uebergabe',
                'titel': 'Wohnungsübergabe: was der Vermieter verlangen darf',
                'absaetze': [
                    'Bei der Rückgabe zählen zwei Dinge: Die Wohnung muss geräumt und '
                    '<strong>besenrein</strong> sein. Besenrein heißt vollständig '
                    'leer, Boden gefegt, grober Schmutz entfernt, Dübel und Nägel '
                    'heraus. Es heißt <em>nicht</em> gewischt, Fenster geputzt oder '
                    'frisch gestrichen.',
                    'Ob darüber hinaus Schönheitsreparaturen fällig sind, hängt am '
                    'Mietvertrag – und viele ältere Klauseln dazu sind von Gerichten '
                    'gekippt worden. Klären Sie das <em>vor</em> der Räumung, nicht '
                    'mittendrin. Wenn gestrichen werden muss, ist der beste Zeitpunkt '
                    'der Tag nach der Räumung: Die Wohnung ist leer, und der Maler '
                    'kommt ohne Möbelrücken aus.',
                    'Gehen Sie mit einem <strong>Übergabeprotokoll</strong> in den '
                    'Termin. Ohne Protokoll steht später Aussage gegen Aussage, und '
                    'die Kaution bleibt einbehalten, bis das geklärt ist. Auf Wunsch '
                    'sind wir beim Termin dabei und übergeben direkt.',
                ],
                'liste': [
                    '<strong>Zählerstände</strong> für Strom, Gas und Wasser – am '
                    'besten zusätzlich als Foto.',
                    '<strong>Schlüssel</strong> vollständig, inklusive Keller-, '
                    'Brief- und Garagenschlüssel. Fehlt einer, kann der Vermieter die '
                    'Schließanlage in Rechnung stellen.',
                    '<strong>Mängel</strong>, die schon beim Einzug vorhanden waren – '
                    'am besten mit dem Einzugsprotokoll daneben.',
                    '<strong>Datum und Unterschrift</strong> beider Seiten. Ein '
                    'Protokoll, das nur einer unterschreibt, hilft niemandem.',
                ],
            },
            {
                'id': 'kosten',
                'titel': 'Was eine Wohnungsauflösung kostet – und was den Preis bewegt',
                'absaetze': [
                    'Der Grundpreis richtet sich nach der Wohnfläche: '
                    '{wohnung_rate} € pro m², mindestens {wohnung_ab} €. Eine typische '
                    'Wohnung von {wohnung_qm} m² liegt damit bei etwa '
                    '{wohnung_beispiel}. Auf diesen Grundwert wirken drei Dinge – und '
                    'alle drei kann man vorher wissen.',
                    'Der <strong>Füllgrad</strong> ist der größte Hebel: leicht '
                    'möbliert rechnet mit Faktor {fuellgrad_leicht}, voll mit {fuellgrad_voll}. Das '
                    '<strong>Stockwerk ohne Aufzug</strong> kostet zwischen {stockwerk_min_txt} € im '
                    'ersten und {stockwerk_max_txt} € im vierten Obergeschoss – mit Aufzug entfällt '
                    'der Zuschlag vollständig. <strong>Sonderabfälle</strong> wie '
                    'Farben, Lacke oder Altöl schlagen mit {sonderabfall_wenige_txt} € bei wenigen und '
                    '{sonderabfall_viele_txt} € bei vielen zu Buche, weil sie getrennt angeliefert werden '
                    'müssen.',
                    'Im Servicegebiet ziehen wir {rabatt} % ab. Wie sich die Zahlen im '
                    'Einzelfall zusammensetzen, steht mit sichtbarem Rechenweg auf '
                    '<a href="/entruempelung-kosten/">Entrümpelung Kosten</a>.',
                ],
            },
            {
                'id': 'hausverwaltung',
                'titel': 'Für Vermieter, Hausverwaltungen und Makler',
                'absaetze': [
                    'Ein erheblicher Teil unserer Wohnungsauflösungen kommt nicht vom '
                    'Mieter, sondern von der anderen Seite: Hausverwaltungen, die eine '
                    'zurückgelassene Wohnung wieder vermietbar brauchen, Makler vor '
                    'dem Besichtigungstermin, Eigentümer nach einer Räumung.',
                    'Für diese Aufträge zählt anderes als beim Privatkunden: ein '
                    'fester Termin, eine Rechnung mit ausgewiesener Umsatzsteuer, ein '
                    'Entsorgungsnachweis für die Akte und ein Ansprechpartner, der '
                    'auch am Tag danach erreichbar ist. Bei mehreren Objekten im Jahr '
                    'lohnt eine feste Absprache – dafür gibt es die Seite für '
                    '<a href="/kooperationspartner/">Kooperationspartner</a>.',
                    'Bei einer <strong>Räumung nach Titel</strong> arbeiten wir als '
                    'ausführender Dienstleister mit dem Gerichtsvollzieher zusammen. '
                    'Bei der regulären Räumung entsorgt er die beweglichen Sachen des '
                    'Mieters nicht: Er übergibt sie oder bringt sie in Verwahrung, '
                    'vernichtet wird nur, woran offensichtlich kein Interesse besteht. '
                    'Fordert der Mieter sie nicht binnen eines Monats an, verkauft der '
                    'Gerichtsvollzieher sie und hinterlegt den Erlös. Was zu welchem '
                    'Weg gehört, entscheidet der '
                    'Gerichtsvollzieher, nicht wir.',
                ],
            },
            {
                'id': 'steuer',
                'titel': 'Beim eigenen Auszug: was steuerlich zählt',
                'absaetze': [
                    'Ziehen Sie selbst aus, gilt die alte Wohnung für §35a EStG noch '
                    'als Ihr Haushalt – bis zu dem Tag, auf den gekündigt ist. Arbeiten, '
                    'die die Abnutzung aus Ihrer Wohnzeit beseitigen, rechnet die '
                    'Finanzverwaltung noch dem Haushalt zu, wenn sie in engem '
                    'zeitlichem Zusammenhang mit dem Umzug stehen. Ihr Beispiel dafür '
                    'sind <strong>Renovierungsarbeiten eines ausziehenden Mieters</strong>: '
                    'Handwerkerleistung, 20 % der Arbeitskosten, höchstens 1.200 € im '
                    'Jahr.',
                    'Die Räumung selbst ist unsicherer. Die Haushaltsauflösung führt die '
                    'Finanzverwaltung als nicht begünstigt, Umzugsdienstleistungen '
                    'prüft sie im Einzelfall. Deshalb stehen Räumung und Malerarbeiten '
                    'bei uns getrennt im Angebot. Abziehbar sind nur Arbeits- und '
                    'Fahrtkosten, und nur mit Rechnung und Überweisung – sprechen Sie '
                    'uns auf ausgewiesene Arbeitskosten an.',
                ],
            },
        ],

        'quellen': [
            {'schluessel': 'bgb-564', 'abschnitt': 'fristen',
             'bezug': 'Fortsetzung mit dem Erben und Kündigung binnen eines Monats'},
            {'schluessel': 'zpo-885', 'abschnitt': 'hausverwaltung',
             'bezug': 'Verwahrung und Verwertung bei der Räumung'},
            {'schluessel': 'bmf-35a-2016', 'abschnitt': 'steuer',
             'bezug': 'Umzug und ausziehender Mieter: Rdnr. 3, Arbeitskosten: '
                      'Rdnr. 39'},
        ],

        'vergleich': {
            'titel': 'Wohnungsauflösung, Haushaltsauflösung und Entrümpelung im Vergleich',
            'eigene_spalte': 2,
            'fazit_frage': 'Wohnungsauflösung oder Haushaltsauflösung – was brauche ich?',
            'fazit': ('Entscheidend ist, wer das Objekt danach bekommt. Geht eine Mietwohnung besenrein an den Vermieter zurück, ist es eine Wohnungsauflösung – ab {wohnung_ab} €, Termin bestimmt die Kündigungsfrist. Wird ein ganzer Hausstand aufgelöst, etwa nach einem Todesfall oder vor einem Verkauf, ist es eine Haushaltsauflösung – ab {haus_ab} €. Der Ablauf ist derselbe, die Menge nicht. Preisstand: {preisstand}.'),
            'kopf': ['', 'Wohnungsauflösung', 'Haushaltsauflösung', 'Entrümpelung'],
            'zeilen': [
                ['Rechtslage', 'Mietverhältnis', 'meist Eigentum oder Nachlass',
                 'egal – Objekt bleibt bewohnt'],
                ['Termin bestimmt', 'Mietvertrag und Rückgabetermin',
                 'Notar-, Verkaufs- oder Erbtermin', 'Sie selbst'],
                ['Umfang', 'komplette Wohnung samt Keller', 'kompletter Hausstand',
                 'einzelne Räume'],
                ['Danach', 'Rückgabe an den Vermieter', 'Verkauf, Vermietung, Übergabe',
                 'weiter bewohnt'],
                ['Typischer Auftraggeber', 'Mieter, Erben, Hausverwaltung',
                 'Eigentümer, Erben', 'Bewohner'],
                ['Preis ab', '{wohnung_ab} €', '{haus_ab} €', '{keller_ab} €'],
            ],
        },

        'beispiele': [
            {
                'titel': '2-Zimmer-Wohnung, 55 m², Erdgeschoss',
                'beschreibung': 'Normal möbliert, keine Sonderabfälle – der '
                                'häufigste Fall bei einem regulären Auszug.',
                'args': {'objektart': 'wohnung', 'qm': 55, 'fuellgrad': 'mittel'},
            },
            {
                'titel': '3-Zimmer-Wohnung, 75 m², 3. OG ohne Aufzug',
                'beschreibung': 'Voll möbliert, Kellerabteil inklusive, einzelne '
                                'Farbreste im Abstellraum.',
                'args': {'objektart': 'wohnung', 'qm': 75, 'stockwerk': '3og',
                         'fuellgrad': 'voll', 'sonderabfall': 'wenige'},
            },
            {
                'titel': '4-Zimmer-Wohnung, 95 m², 1. OG mit Aufzug',
                'beschreibung': 'Aufzug vorhanden – der Stockwerkzuschlag '
                                'entfällt dadurch vollständig.',
                'args': {'objektart': 'wohnung', 'qm': 95, 'stockwerk': '1og',
                         'aufzug': True, 'fuellgrad': 'mittel'},
            },
        ],

        'ablauf': [
            {'titel': 'Anfrage mit Termin',
             'text': 'Nennen Sie uns gleich den Übergabetermin. Danach richtet sich '
                     'alles Weitere – und wir sagen Ihnen ehrlich, ob er zu halten ist.'},
            {'titel': 'Kostenlose Besichtigung',
             'text': 'Wohnfläche, Menge, Stockwerk, Aufzug, Parksituation vor der '
                     'Tür. Ein kurzer Termin, der den Unterschied zwischen Festpreis '
                     'und Schätzung ausmacht.'},
            {'titel': 'Festpreisangebot mit Datum',
             'text': 'Schriftlich, {angebot_frist} – mit '
                     'Räumungstermin; auf Anfrage mit ausgewiesenen Arbeitskosten '
                     'für die Steuer.'},
            {'titel': 'Räumung',
             'text': 'Wir räumen, bauen ab, trennen und verladen. Behaltenes stellen '
                     'wir zusammen, Dokumente und Wertsachen legen wir beiseite. Sie '
                     'müssen nicht dabei sein.'},
            {'titel': 'Übergabe an den Vermieter',
             'text': 'Besenreine Abnahme, auf Wunsch gemeinsam beim Übergabetermin. '
                     'Zählerstände, Schlüssel, Protokoll – und der '
                     'Entsorgungsnachweis, falls die Verwaltung ihn braucht.'},
        ],

        'faq': [
            ('Was kostet eine Wohnungsauflösung?',
             'Sie beginnt bei {wohnung_ab} € und rechnet darüber mit '
             '{wohnung_rate} € pro m² Wohnfläche. Eine Wohnung von {wohnung_qm} m² '
             'liegt damit bei etwa {wohnung_beispiel}. Dazu kommen Füllgrad, '
             'Stockwerk ohne Aufzug und Sonderabfälle; im Servicegebiet ziehen wir '
             '{rabatt} % ab. Der Preisrechner nennt in {rechner_dauer} einen konkreten '
             'Wert, verbindlich wird er nach der kostenlosen Besichtigung. '
             'Preisstand: {preisstand}.'),
            ('Wie lange dauert die Räumung einer Wohnung?',
             'Entscheidend ist weniger die Fläche als der Weg nach draußen: '
             'Ein dritter Stock ohne '
             'Aufzug oder eine enge Altbautreppe kostet mehr Zeit als zwanzig '
             'Quadratmeter zusätzlich. Den Zeitbedarf schätzen wir bei der '
             'Besichtigung und schreiben ihn ins Angebot.'),
            ('Was ist der Unterschied zwischen Wohnungsauflösung und Haushaltsauflösung?',
             'Die Wohnungsauflösung betrifft eine Mietwohnung: Sie endet mit der '
             'Rückgabe an den Vermieter, und der Zeitplan kommt aus dem Mietvertrag. '
             'Die Haushaltsauflösung löst einen kompletten Hausstand auf, meist im '
             'Eigentum oder im Nachlass, und richtet sich nach Verkaufs- oder '
             'Notarterminen. Die Arbeit ist ähnlich, der Rahmen nicht.'),
            ('Muss die Wohnung bei der Übergabe renoviert sein?',
             'Räumen und besenrein hinterlassen müssen Sie in jedem Fall. Ob darüber '
             'hinaus Schönheitsreparaturen fällig sind, steht im Mietvertrag – viele '
             'ältere Klauseln dazu sind allerdings unwirksam. Klären Sie das vor der '
             'Räumung. Wird gestrichen, ist der Tag nach der Räumung der beste '
             'Zeitpunkt: Wir rechnen Malerarbeiten mit {maler_rate} € pro m² ab, '
             'mindestens {maler_min} €.'),
            ('Wer zahlt die Wohnungsauflösung nach einem Todesfall?',
             'Grundsätzlich der Nachlass, also die Erben. Reicht der Nachlass nicht, '
             'gibt es Wege, die Haftung zu begrenzen – das ist eine Frage an einen '
             'Anwalt oder das Nachlassgericht, nicht an uns. Praktisch wichtig: Das '
             'Mietverhältnis endet nicht mit dem Tod. Erben können innerhalb eines '
             'Monats außerordentlich mit der gesetzlichen Frist kündigen (§ 564 '
             'BGB); danach gilt die normale Kündigungsfrist.'),
            ('Räumen Sie auch Keller und Dachboden mit?',
             'Ja – und beides gehört ausdrücklich in die Besichtigung. Keller- und '
             'Bodenabteile werden regelmäßig vergessen und tauchen dann am '
             'Räumungstag als Überraschung auf. Wenn sie im Angebot stehen, sind sie '
             'im Festpreis enthalten, auch wenn mehr darin steht als gedacht.'),
            ('Können Sie die Wohnung direkt an den Vermieter übergeben?',
             'Ja. Viele Auftraggeber wohnen weit weg oder sind gesundheitlich nicht '
             'in der Lage, beim Termin dabei zu sein. Wir übergeben dann besenrein '
             'direkt an Vermieter, Hausverwaltung oder Makler, notieren Zählerstände '
             'und Schlüsselzahl und schicken Ihnen das Protokoll.'),
            ('Wie schnell meldet sich Rümpelwerk bei einer Wohnungsauflösung?',
             'In Halle, Leipzig, Magdeburg, Dresden und Chemnitz melden wir uns in '
             '{reaktion} zurück und stimmen die Besichtigung mit Ihnen ab. '
             'Wenn ein Übergabetermin drückt, schreiben Sie das gleich '
             'in die erste Nachricht. Wir sagen Ihnen dann ehrlich, ob wir es '
             'schaffen – eine Absage ist besser als ein gerissener Termin.'),
            ('Wohnungsräumung, Wohnung auflösen, Beräumung – welches Wort ist '
             'richtig?',
             'Alle drei. „Wohnungsräumung" und „Beräumung" sind die '
              'amtlicheren Begriffe, „Wohnung auflösen" und „räumen lassen" '
              'die alltäglichen – gemeint ist dieselbe Leistung: Die Wohnung '
              'wird vollständig geleert und besenrein übergeben. Nur die '
              'Zwangsräumung ist etwas anderes: Sie setzt einen gerichtlichen '
              'Titel voraus und wird vom Gerichtsvollzieher durchgeführt; wir '
              'arbeiten dabei höchstens als ausführender Dienstleister mit.'),
        ],

        'related': ['haushaltsaufloesung', 'messie-wohnung-entruempeln',
                    'sanierung-renovierung', 'entruempelung-kosten'],

        'staedte': ['halle', 'leipzig', 'magdeburg', 'dresden', 'chemnitz',
                    'merseburg', 'dessau', 'hannover', 'zwickau', 'naumburg',
                    'bitterfeld', 'weissenfels'],

        'seo_title': 'Wohnungsauflösung ab {wohnung_ab} € – Festpreis | Rümpelwerk',
        'seo_description': (
            'Wohnungsauflösung ab {wohnung_ab} €: Festpreis direkt bei der '
            'kostenlosen Besichtigung, besenrein zum Übergabetermin. '
            'Jetzt Preis berechnen.'
        ),
        'seo_keywords': (
            'Wohnungsauflösung, Wohnungsauflösung Kosten, Wohnungsräumung, '
            'Wohnungsberäumung, Wohnung entrümpeln, Wohnungsentrümpelung, '
            'Beräumung, Wohnungsauflösung Halle, Wohnungsauflösung Leipzig'
        ),
    },

    # ───────────────────────────────────────────────────────────────────────
    # A6 — /kellerentruempelung/
    #
    # Günstigster Einstieg des Portfolios ({keller_ab} €) und damit die Seite
    # für den Erstkontakt. Der GSC-Export zeigt „kellerentrümpelung" auf
    # Position 3,5 ohne eigene Seite – dazu Kellerabfragen aus Städten weit
    # außerhalb des Gebiets. Die Seite muss deshalb sagen, wo gearbeitet wird.
    'kellerentruempelung': {
        'name': 'Kellerentrümpelung',
        'h1': 'Kellerentrümpelung',
        'h1_em': 'Ab {keller_ab} €. Besenrein.',
        'keyword': 'kellerentrümpelung',
        'objektart': 'keller',

        'hero_sub': (
            'Keller, Dachboden, Garage oder Speicher leer räumen lassen – '
            'sortiert entsorgt und besenrein hinterlassen. '
            'Festpreis ab {keller_ab} € nach kostenloser Besichtigung, auf '
            'Wunsch mit Entsorgungsnachweis.'
        ),

        'answer_frage': 'Was kostet eine Kellerentrümpelung?',
        'answer': (
            'Eine Kellerentrümpelung ist die Teilräumung eines Kellers, Dachbodens '
            'oder Nebengelasses – die Wohnung darüber bleibt bewohnt. Rümpelwerk '
            'Mitteldeutschland übernimmt sie ab {keller_ab} € zum Festpreis, '
            'Richtwert {keller_rate} € pro m². Ein normales Kellerabteil räumen wir '
            'leer, entsorgen es sortiert und fegen besenrein. '
            'Preisstand: {preisstand}.'
        ),

        'leistungsumfang': [
            'Kellerräume, einzelne Kellerabteile und ganze Kellergeschosse',
            'Dachboden, Speicher, Abstellkammer und Trockenboden',
            'Garage, Carport, Schuppen, Gartenhaus und Nebengelass',
            'Möbel, Kartons, Einweckgläser, Reifen, Fahrräder, Regale',
            'Elektrogeräte und Elektroschrott, getrennt gesammelt',
            'Abbau fest verbauter Regale, Werkbänke und Einbauschränke',
            'Fegen und besenreine Übergabe, Türen und Zugänge sauber hinterlassen',
            'Entsorgungsnachweis für Hausverwaltung oder Eigentümergemeinschaft',
        ],

        'abgrenzung': [
            'Schadstoffsanierung: Asbestplatten, künstliche Mineralfasern und '
            'ähnliche Stoffe gehören in die Hand eines zugelassenen Fachbetriebs. '
            'Wir sagen Ihnen bei der Besichtigung, wenn wir so etwas sehen – und '
            'räumen den Rest.',
            'Schimmelsanierung: Oberflächlichen Schimmel an geräumten Wänden können '
            'wir behandeln, die Ursachensuche an feuchten Kellerwänden ist Sache '
            'eines Bausachverständigen.',
            'Heizöltanks entleeren und stilllegen ist eine Fachleistung mit eigener '
            'Zulassung. Wir räumen den Raum drum herum.',
            'Wertermittlung: Wir kaufen nichts an und schätzen nichts. Was Ihnen '
            'wertvoll erscheint, stellen wir beiseite, statt es zu bewerten.',
        ],

        'abschnitte': [
            {
                'id': 'unterschied',
                'titel': 'Kellerentrümpelung, Sperrmüll oder Container – was ist richtig?',
                'absaetze': [
                    'Beim Keller entscheidet die Treppe über den Weg. Der '
                    '<strong>kommunale Sperrmüll</strong> holt ab dem Gehweg ab – '
                    'in Halle, Magdeburg und Chemnitz in festen Mengen ohne Gebühr, in '
                    'Leipzig und Dresden gegen Gebühr. Jedes Stück muss vorher aus dem '
                    'Keller nach oben, und Schadstoffe wie Farbreste nimmt keine '
                    'Sperrmüllabfuhr mit.',
                    'Ein <strong>Container</strong> spart den Termin, nicht das Tragen: '
                    'Er steht vor dem Haus, der Keller liegt darunter. Für ein '
                    'einzelnes Abteil ist er meist überdimensioniert, und auf '
                    'öffentlichem Grund braucht er eine Genehmigung.',
                    'Wir tragen selbst, auch über enge Kellertreppen, und trennen '
                    'dabei Metall, Holz, Elektro und Restabfall. Die Regel Ihrer Stadt '
                    'samt Gebühr und Vorlauf steht auf der jeweiligen Stadtseite, der '
                    'Vergleich aller Wege auf '
                    '<a href="/sperrmuell-entsorgung/">Sperrmüll entsorgen</a>.',
                ],
            },
            {
                'id': 'zugang',
                'titel': 'Warum der Zugang mehr kostet als die Menge',
                'absaetze': [
                    'Bei einer Kellerentrümpelung entscheidet selten die Kubikmeterzahl '
                    'über den Aufwand, sondern der Weg nach draußen. Eine steile '
                    'Kellertreppe mit Wendung, ein Lichtschacht statt eines Fensters, '
                    'ein Hinterhof ohne Zufahrt: Das kostet mehr Zeit als der Inhalt '
                    'selbst.',
                    'Deshalb fragen wir bei der Besichtigung nach Dingen, die auf den '
                    'ersten Blick nebensächlich wirken – Türbreite, Deckenhöhe, '
                    'Stellplatz für den Wagen, Entfernung zur Ladefläche, ob ein '
                    'Halteverbot nötig ist. Wer diese Punkte vorher klärt, bekommt '
                    'einen Festpreis, der auch hält.',
                    'Umgekehrt gilt: Ein ebenerdiger Garagenzugang mit Auffahrt macht '
                    'dieselbe Menge deutlich günstiger. Sagen Sie uns solche Vorteile '
                    'ruhig gleich – sie fließen in die Kalkulation ein.',
                ],
                'liste': [
                    '<strong>Treppe.</strong> Gerade oder gewendelt, Stufenhöhe, '
                    'Geländer – bei Altbauten oft der begrenzende Faktor.',
                    '<strong>Türbreite.</strong> Alte Kellertüren sind schmaler als '
                    'moderne Schränke. Manches muss vor Ort zerlegt werden.',
                    '<strong>Licht und Strom.</strong> Wo keine funktionierende '
                    'Beleuchtung ist, arbeiten wir mit eigenen Strahlern.',
                    '<strong>Stellfläche.</strong> Je näher der Wagen an den Ausgang '
                    'kommt, desto kürzer der Weg – und desto günstiger die Stunde.',
                ],
            },
            {
                'id': 'feuchtigkeit',
                'titel': 'Feuchte Keller, Schimmel und was danach sinnvoll ist',
                'absaetze': [
                    'In vielen Altbaukellern in Halle, Leipzig oder Magdeburg steht '
                    'seit Jahrzehnten Kartonware direkt an der Außenwand. Das Ergebnis '
                    'sehen wir regelmäßig: durchgeweichte Pappe, stockige Textilien, '
                    'weißer Belag an der Wand. Für die Räumung ist das eine Frage der '
                    'Schutzausrüstung, nicht des Preises.',
                    'Wichtiger ist, was danach passiert. Ein leerer Keller trocknet '
                    'nur, wenn er richtig gelüftet wird – im Sommer <em>nicht</em> '
                    'tagsüber, sondern in den kühlen Morgenstunden, weil warme '
                    'Außenluft an kalten Kellerwänden kondensiert. Wer den frisch '
                    'geräumten Keller sofort wieder vollstellt, hat das Problem in '
                    'zwei Jahren erneut.',
                    'Oberflächlichen Schimmel an geräumten Wänden können wir '
                    'behandeln; das ist eine der Kleinreparaturen aus unserem '
                    '<a href="/sanierung-renovierung/">Sanierungsangebot</a>. Ist die '
                    'Ursache bauseitig – aufsteigende Feuchte, defekte Abdichtung –, '
                    'gehört ein Sachverständiger dazu und nicht ein Entrümpler.',
                ],
            },
            {
                'id': 'hausverwaltung',
                'titel': 'Mehrfamilienhaus: Kellergänge, verwaiste Abteile, Brandschutz',
                'absaetze': [
                    'Für Hausverwaltungen und Eigentümergemeinschaften ist der Keller '
                    'ein wiederkehrendes Thema – meist dann, wenn der Brandschutz '
                    'geprüft wird. Vollgestellte Kellergänge und Fluchtwege sind ein '
                    'Mangel, der abgestellt werden muss, und verwaiste Abteile nach '
                    'Auszügen sind der häufigste Grund dafür.',
                    'Wir räumen solche Objekte abteilweise oder komplett, arbeiten '
                    'nach Aushangfrist und dokumentieren, was aus welchem Abteil kam. '
                    'Eine Rechnung mit ausgewiesener Umsatzsteuer und ein '
                    'Entsorgungsnachweis gehören dazu, weil beides in die Abrechnung '
                    'der Gemeinschaft muss.',
                    'Bei mehreren Objekten im Jahr ist eine feste Absprache günstiger '
                    'als jede Einzelbeauftragung – wie das aussieht, steht auf der '
                    'Seite für <a href="/kooperationspartner/">Kooperationspartner</a>.',
                ],
            },
            {
                'id': 'kosten',
                'titel': 'Was eine Kellerentrümpelung kostet',
                'absaetze': [
                    'Der Einstieg liegt bei {keller_ab} € – das ist zugleich der '
                    'niedrigste Preis im gesamten Portfolio. Darüber rechnen wir mit '
                    '{keller_rate} € pro m² Grundfläche. Ein typisches Kellerabteil von '
                    '{keller_qm} m² liegt damit bei etwa {keller_beispiel}.',
                    'Auf diesen Grundwert wirken zwei Dinge: der Füllgrad (leicht {fuellgrad_leicht} '
                    'bis messiartig {fuellgrad_messi}) und Sonderabfälle wie alte Farbeimer, Lacke, '
                    'Verdünner oder Autobatterien – {sonderabfall_wenige_txt} € bei wenigen, {sonderabfall_viele_txt} € bei '
                    'vielen. Beides sehen wir bei der Besichtigung, und beides steht '
                    'danach fest.',
                    'Im Servicegebiet ziehen wir {rabatt} % ab. Wenn Sie den Keller '
                    'ohnehin im Zuge einer '
                    '<a href="/wohnungsaufloesung/">Wohnungsauflösung</a> räumen '
                    'lassen, ist er dort bereits enthalten – dann fällt kein zweiter '
                    'Mindestpreis an.',
                ],
            },
        ],

        'vergleich': {
            'titel': 'Keller leeren: Sperrmüll, Container oder Firma',
            'eigene_spalte': 4,
            'fazit_frage': 'Keller leeren – lohnt sich Sperrmüll, Container oder eine Firma?',
            'fazit': ('Wer selbst tragen kann und Zeit hat, kommt mit dem kommunalen Sperrmüll am günstigsten weg – in Halle, Magdeburg und Chemnitz holt die Stadt feste Mengen gebührenfrei ab, in Leipzig und Dresden kostet die Abholung eine Gebühr. Ein Container lohnt, wenn Sie ohnehin selbst räumen und Stellfläche haben. Eine Firma kostet ab {keller_ab} €, trägt aber selbst aus dem Keller und liefert auf Wunsch einen Entsorgungsnachweis für die Hausverwaltung. Preisstand: {preisstand}.'),
            'kopf': ['', 'Kommunaler Sperrmüll', 'Container mieten', 'Firma beauftragen'],
            'zeilen': [
                ['Ihre Arbeit', 'alles selbst hochtragen', 'alles selbst hochtragen',
                 'keine'],
                ['Vorlauf', 'Wochen bis Monate', 'wenige Tage', 'meist wenige Tage'],
                ['Elektrogeräte', 'je nach Stadt eigene Anmeldung', 'nicht erlaubt',
                 'enthalten'],
                ['Schadstoffe', 'nein', 'nein', 'gegen Aufpreis'],
                ['Stellfläche nötig', 'Gehweg am Abholtag', 'ja, ggf. mit Genehmigung',
                 'nein'],
                ['Besenrein danach', 'nein', 'nein', 'ja'],
                ['Kosten', 'je nach Stadt frei oder Gebühr', 'Miete plus Gewicht',
                 'ab {keller_ab} € Festpreis'],
            ],
        },

        'beispiele': [
            {
                'titel': 'Kellerabteil, 12 m², normal gefüllt',
                'beschreibung': 'Kartons, Regale, altes Kinderspielzeug – der '
                                'Standardfall im Mehrfamilienhaus.',
                'args': {'objektart': 'keller', 'qm': 12, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Dachboden, 30 m², voll',
                'beschreibung': 'Vier Jahrzehnte Aufbewahrung unter der Schräge, '
                                'schmale Bodentreppe.',
                'args': {'objektart': 'keller', 'qm': 30, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Garage, 20 m², mit Altlasten',
                'beschreibung': 'Werkbank, Reifen, dazu Farbreste, Verdünner und '
                                'eine Autobatterie als Sonderabfall.',
                'args': {'objektart': 'keller', 'qm': 20, 'fuellgrad': 'voll',
                         'sonderabfall': 'wenige'},
            },
        ],

        'ablauf': [
            {'titel': 'Fotos schicken',
             'text': 'Für einen Keller reichen drei, vier Fotos vom Handy plus die '
                     'ungefähre Grundfläche. Damit können wir die Größenordnung nennen, '
                     'sobald wir uns melden – in {reaktion}.'},
            {'titel': 'Kostenlose Besichtigung',
             'text': 'Wir sehen uns Zugang, Treppe, Türbreite und Stellfläche an. Bei '
                     'kleinen Kellern machen wir das auf Wunsch direkt am Räumungstag '
                     'vorab – dann sparen Sie einen Termin.'},
            {'titel': 'Festpreis',
             'text': 'Schriftlich, mit Termin. Was im Angebot steht, wird berechnet – '
                     'auch wenn hinter der letzten Regalwand mehr steht als gedacht.'},
            {'titel': 'Räumen und trennen',
             'text': 'Wir tragen heraus und trennen dabei: Metall, Holz, Elektro, '
                     'Papier, Restabfall. Brauchbares geht an Secondhand-Stellen '
                     'statt in den Container.'},
            {'titel': 'Besenrein übergeben',
             'text': 'Boden gefegt, Regalanker heraus, Tür zu. Auf Wunsch mit '
                     'Entsorgungsnachweis für die Hausverwaltung.'},
        ],

        'faq': [
            ('Was kostet eine Kellerentrümpelung?',
             'Sie beginnt bei {keller_ab} € und rechnet darüber mit {keller_rate} € '
             'pro m² Grundfläche. Ein Kellerabteil von {keller_qm} m² liegt damit bei '
             'etwa {keller_beispiel}. Dazu kommen der Füllgrad und – falls vorhanden – '
             'Sonderabfälle wie Farben oder Altöl. Im Servicegebiet ziehen wir '
             '{rabatt} % ab. Preisstand: {preisstand}.'),
            ('Wie lange dauert eine Kellerentrümpelung?',
             'Die Dauer hängt von der Menge ab – ein einzelnes Kellerabteil ist '
             'schneller geleert als ein ganzes Kellergeschoss oder ein voller Dachboden. Den '
             'Ausschlag gibt der Weg nach draußen: Eine gewendelte Altbautreppe kostet '
             'mehr Zeit als die doppelte Menge im ebenerdigen Garagenzugang.'),
            ('Lohnt sich eine Firma oder ist der Sperrmüll günstiger?',
             'Rein nach Geld ist der kommunale Sperrmüll günstiger – in Halle, '
             'Magdeburg und Chemnitz holt die Stadt feste Mengen gebührenfrei ab, '
             'in Leipzig und Dresden zahlen Sie eine Gebühr. Er setzt aber voraus, dass '
             'Sie selbst hochtragen, an die Straße stellen und auf den Termin warten, '
             'und Schadstoffe nimmt er nicht mit. Wenn Sie nicht tragen '
             'können, keine Zeit haben oder ein Termin drückt, ist die Firma der '
             'sinnvollere Weg. Wir sagen Ihnen das auch dann, wenn es gegen uns '
             'spricht.'),
            ('Nehmen Sie auch Farben, Lacke und Altöl mit?',
             'Ja, als Sonderabfall. Diese Stoffe dürfen nicht in den Restmüll und '
             'müssen getrennt angeliefert werden – deshalb stehen sie mit {sonderabfall_wenige_txt} € bei '
             'wenigen und {sonderabfall_viele_txt} € bei vielen im Angebot. Was genau darunter fällt, sehen '
             'wir bei der Besichtigung. Asbest und künstliche Mineralfasern gehören '
             'dagegen in die Hand eines zugelassenen Fachbetriebs.'),
            ('Räumen Sie auch einzelne Kellerabteile im Mehrfamilienhaus?',
             'Ja, das ist einer der häufigsten Aufträge – meist nach einem Auszug oder '
             'wenn der Brandschutz vollgestellte Kellergänge beanstandet hat. Wir '
             'arbeiten abteilweise, halten die Aushangfrist der Verwaltung ein und '
             'dokumentieren, was aus welchem Abteil kam.'),
            ('Was passiert mit noch brauchbaren Sachen aus dem Keller?',
             'Was noch verwendbar ist, geben wir an Secondhand-Stellen und soziale '
             'Einrichtungen weiter, statt es zu entsorgen. Angekauft wird nichts, und '
             'es wird auch nichts gegen den Preis gerechnet: Der Festpreis steht vor '
             'Beginn fest, unabhängig davon, was im Keller steht.'),
            ('Ist der Keller danach besenrein?',
             'Ja. Besenrein heißt: vollständig geräumt, Boden gefegt, grober Schmutz '
             'entfernt, Regalanker und Dübel heraus. Gewischt oder gestrichen wird '
             'nicht – das ist eine eigene Leistung, die sich aber in denselben Auftrag '
             'legen lässt.'),
            ('Muss ich beim Termin dabei sein?',
             'Zur Besichtigung ja, weil dort der Umfang festgelegt wird. Bei der '
             'Räumung selbst nicht. Schlüsselübergabe regeln wir mit Ihnen, der '
             'Hausverwaltung oder einem Nachbarn – das ist bei Kellern der Normalfall.'),
            ('Keller ausräumen lassen, Kellerberäumung, Kellerentrümpelung – '
             'ein Unterschied?',
             'Nein, das ist dieselbe Arbeit. Gerechnet wird nach Grundfläche '
              'des Kellers, nicht nach der Zahl der Verschläge: {keller_rate} '
              '€ pro m², mindestens {keller_ab} €. Ein durchschnittlicher '
              'Kellerverschlag von {keller_qm} m² liegt bei '
              '{keller_beispiel}. Dachboden und Garage rechnen wir genauso.'),
        ],

        'related': ['sperrmuell-entsorgung', 'gewerbeentruempelung',
                    'haushaltsaufloesung', 'entruempelung-kosten'],

        'staedte': ['halle', 'leipzig', 'magdeburg', 'dresden', 'chemnitz',
                    'merseburg', 'delitzsch', 'bitterfeld', 'dessau',
                    'sangerhausen', 'querfurt', 'naumburg'],

        'seo_title': 'Kellerentrümpelung ab {keller_ab} € – Festpreis | Rümpelwerk',
        'seo_description': (
            'Kellerentrümpelung ab {keller_ab} €: Keller, Dachboden, Garage '
            'räumen, besenrein. Festpreis bei kostenloser Besichtigung. '
            'Jetzt Termin buchen.'
        ),
        'seo_keywords': (
            'Kellerentrümpelung, Keller entrümpeln, Kellerentrümpelung Kosten, '
            'Dachboden entrümpeln, Garage entrümpeln, Speicher räumen, '
            'Kellerentrümpelung Halle, Kellerentrümpelung Leipzig'
        ),
    },

    # ───────────────────────────────────────────────────────────────────────
    # A7 — /nachlassraeumung/
    #
    # Höchste Priorität der Marge-Gruppe: geringe Konkurrenz, hohe
    # Auftragswerte, und die Suchintention ist emotional statt preisgetrieben.
    # Der GSC-Export zeigt „nachlassauflösung dresden" mit 10 Impressionen auf
    # Position 68 – die Nachfrage ist da, die Seite fehlte.
    #
    # Ton: sachlich und respektvoll. Kein Preisdruck-Marketing, keine
    # Superlative, keine Rabattsprache. Der Preis steht auf dieser Seite
    # bewusst weiter unten als auf allen anderen.
    'nachlassraeumung': {
        'name': 'Nachlassräumung',
        'h1': 'Nachlassräumung',
        'h1_em': 'Ruhig. Vollständig. Dokumentiert.',
        'keyword': 'nachlassräumung',
        'objektart': 'haus',

        'hero_sub': (
            'Wohnung oder Haus nach einem Todesfall räumen lassen – sorgfältig, '
            'diskret und mit gesicherten Dokumenten. Wir arbeiten mit Erben, '
            'Bevollmächtigten und Nachlassverwaltern in Sachsen-Anhalt, Sachsen '
            'und Niedersachsen. Festpreis ab {wohnung_ab} € für eine Wohnung.'
        ),

        'answer_frage': 'Was kostet eine Nachlassräumung?',
        'answer': (
            'Eine Nachlassräumung ist die vollständige Räumung einer Wohnung oder '
            'eines Hauses nach einem Todesfall – einschließlich der Sicherung von '
            'Dokumenten, Fotos und persönlichen Gegenständen, die an die Erben '
            'übergeben werden. Rümpelwerk Mitteldeutschland übernimmt sie zum '
            'Festpreis ab {haus_ab} € für ein Haus und ab {wohnung_ab} € für eine '
            'Wohnung, besenrein und auf Wunsch mit Entsorgungsnachweis für die '
            'Erbengemeinschaft. Preisstand: {preisstand}.'
        ),

        'leistungsumfang': [
            'Vollständige Räumung von Wohnung, Haus, Keller und Dachboden',
            'Getrenntes Sichern von Dokumenten, Verträgen, Fotos und Briefen',
            'Persönliche Erinnerungsstücke werden beiseitegelegt, nicht entsorgt',
            'Fundstücke werden auf Wunsch fotografisch dokumentiert',
            'Abstimmung mit Vermieter, Hausverwaltung, Makler oder Nachlassgericht',
            'Terminliche Abstimmung auf Kündigungsfristen und Übergabetermine',
            'Besenreine Übergabe, Schlüsselrückgabe nach Absprache',
            'Entsorgungsnachweis für die Erbengemeinschaft und die Nachlassakte',
        ],

        'abgrenzung': [
            'Wir bewerten keinen Nachlass. Antiquitäten, Schmuck und Sammlungen '
            'schätzt ein Gutachter oder ein Auktionshaus – wir stellen solche Funde '
            'beiseite und übergeben sie, statt sie zu beziffern.',
            'Wir kaufen nichts an. Der Festpreis steht vor Beginn fest und hängt '
            'nicht davon ab, was gefunden wird. Wer den Preis vom '
            'Fundwert abhängig macht, hat ein Interesse an einer niedrigen Bewertung.',
            'Rechtsfragen zu Erbschaft, Ausschlagung und Haftung beantworten ein '
            'Notar, ein Anwalt oder das Nachlassgericht. Wir sagen Ihnen, was uns '
            'in der Praxis begegnet, und wo Sie fragen müssen.',
            'Ohne Auftrag einer verfügungsberechtigten Person räumen wir nicht. Bei '
            'mehreren Erben brauchen wir die Zustimmung der Erbengemeinschaft oder '
            'eine Vollmacht – das schützt Sie und uns.',
        ],

        'abschnitte': [
            {
                'id': 'unterschied',
                'titel': 'Was eine Nachlassräumung von einer normalen Räumung unterscheidet',
                'absaetze': [
                    'Technisch ist die Arbeit dieselbe wie bei einer '
                    '<a href="/haushaltsaufloesung/">Haushaltsauflösung</a>: Möbel, '
                    'Hausrat, Keller, Dachboden. Der Unterschied liegt in der '
                    'Sorgfalt, mit der getrennt wird, und darin, dass niemand die '
                    'Wohnung so hinterlassen hat, wie sie ist, weil er ausziehen '
                    'wollte.',
                    'Praktisch heißt das: Wir arbeiten langsamer durch Schubladen, '
                    'Kommoden, Aktenordner und Bücher, statt sie im Ganzen '
                    'abzutragen. Papiere, Fotos, Schmuck, Bargeld, Schlüssel und '
                    'Datenträger landen in getrennten Behältern, nicht im Container. '
                    'Was Sie behalten möchten, stellen wir zusammen, bevor der erste '
                    'Wagen belädt.',
                    'Und wir gehen davon aus, dass Sie nicht die ganze Zeit dabei '
                    'sein wollen oder können. Viele Angehörige beauftragen uns aus '
                    'einem anderen Bundesland; Schlüsselübergabe, Abnahme und '
                    'Rückgabe an die Hausverwaltung regeln wir dann direkt.',
                ],
            },
            {
                'id': 'dokumente',
                'titel': 'Dokumente, Wertsachen und die Frage, was verloren gehen kann',
                'absaetze': [
                    'Die häufigste Sorge, die uns Angehörige nennen, ist nicht der '
                    'Preis, sondern der Gedanke, dass etwas Wichtiges im Container '
                    'landet. Deshalb ist das Sichern kein Zusatz, sondern Teil des '
                    'Auftrags – und es steht so im Angebot.',
                    'Wir sammeln getrennt: amtliche Dokumente, Versicherungs- und '
                    'Bankunterlagen, Sparbücher, Testamente, Fotoalben, Briefe, '
                    'Schmuck, Uhren, Münzen, Bargeld, Schlüssel, Ausweise und '
                    'Datenträger. Auf Wunsch fotografieren wir die Fundstücke und '
                    'schicken die Aufnahmen, bevor wir übergeben – das ist besonders '
                    'dann hilfreich, wenn mehrere Erben beteiligt sind und niemand '
                    'vor Ort war.',
                    'Sagen Sie uns vorher, worauf wir besonders achten sollen. Ein '
                    'Satz wie „im Sekretär im Wohnzimmer müssten noch Papiere liegen" '
                    'oder „es gibt einen zweiten Schlüsselbund" erspart die Suche im '
                    'Nachhinein.',
                ],
                'liste': [
                    '<strong>Amtliches und Verträge:</strong> Personalausweis, '
                    'Rentenbescheide, Versicherungen, Mietvertrag, Grundbuchauszüge.',
                    '<strong>Finanzielles:</strong> Sparbücher, Kontoauszüge, '
                    'Depotunterlagen, Bargeld – oft in Büchern und Kleidung.',
                    '<strong>Persönliches:</strong> Fotoalben, Briefe, Tagebücher, '
                    'Urkunden, Erinnerungsstücke ohne Marktwert.',
                    '<strong>Digitales:</strong> Handys, Laptops, Festplatten, '
                    'USB-Sticks, Speicherkarten – enthalten oft die einzigen '
                    'Fotos der letzten Jahre.',
                ],
            },
            {
                'id': 'erbengemeinschaft',
                'titel': 'Erbengemeinschaft, Vollmacht und wer beauftragen darf',
                'absaetze': [
                    'Mehrere Erben bilden eine Erbengemeinschaft, und über einen '
                    'Nachlassgegenstand können sie nur gemeinschaftlich verfügen. '
                    'Wer Möbel und Hausrat entsorgen lässt, verfügt darüber – deshalb '
                    'brauchen wir einen Auftrag, der gedeckt ist: durch alle Miterben, '
                    'durch eine Vollmacht, durch einen Erbschein oder durch einen '
                    'bestellten Nachlassverwalter oder Testamentsvollstrecker.',
                    'Das klingt formal, hat aber einen praktischen Grund. Wir haben '
                    'Fälle erlebt, in denen ein Miterbe im Alleingang räumen ließ und '
                    'sich anschließend gegenüber den anderen erklären musste. Mit '
                    'einer kurzen schriftlichen Zustimmung aller Beteiligten ist das '
                    'vom Tisch – ein formloser Text per E-Mail genügt uns.',
                    'Wer das Erbe <strong>ausschlagen</strong> will, sollte vor der '
                    'Räumung mit dem Nachlassgericht sprechen und nicht danach: Wer '
                    'über Nachlassgegenstände verfügt, kann damit die Annahme des '
                    'Erbes erklären. Die Ausschlagung ist zudem an eine Frist von '
                    '<strong>sechs Wochen</strong> gebunden, die mit der Kenntnis vom '
                    'Erbfall beginnt. Eine Räumung kann deshalb warten, bis diese '
                    'Frage entschieden ist – die Kündigungsfrist der Wohnung meist '
                    'nicht.',
                ],
            },
            {
                'id': 'fristen',
                'titel': 'Fristen bei einer Mietwohnung',
                'absaetze': [
                    'Stirbt ein Mieter, läuft das Mietverhältnis weiter – und mit ihm '
                    'die Miete. Tritt niemand aus dem Haushalt in den Vertrag ein, '
                    'können Erbe und Vermieter innerhalb eines Monats außerordentlich '
                    'mit der gesetzlichen Frist kündigen. Wer den Monat verstreichen '
                    'lässt, ist an die normale Kündigungsfrist gebunden und zahlt so '
                    'lange für eine leere Wohnung.',
                    'Das ist der Grund, warum eine Nachlassräumung oft schneller '
                    'stattfinden muss, als es sich richtig anfühlt. Wir können den '
                    'zeitlichen Druck nicht wegnehmen, aber wir können ihn planbar '
                    'machen: Termin bei der Besichtigung festlegen, Angebot mit Datum, '
                    'Übergabe am vereinbarten Tag. Wie eine Wohnungsübergabe im '
                    'Detail abläuft, steht auf der Seite zur '
                    '<a href="/wohnungsaufloesung/">Wohnungsauflösung</a>.',
                    'Wenn es zeitlich nicht reicht, sagen wir das. Eine ehrliche '
                    'Absage ist in dieser Situation mehr wert als ein Termin, der '
                    'nicht hält.',
                ],
            },
            {
                'id': 'zusammenarbeit',
                'titel': 'Zusammenarbeit mit Bestattern, Betreuern und Verwaltern',
                'absaetze': [
                    'Nach einem Todesfall sind oft schon Bestattungshäuser, '
                    'Nachlassverwalter, rechtliche Betreuer oder Hausverwaltungen '
                    'beteiligt. Sie brauchen anderes als Angehörige: einen festen '
                    'Ansprechpartner, verlässliche Termine, eine Rechnung mit '
                    'ausgewiesener Umsatzsteuer und einen Entsorgungsnachweis für die '
                    'Akte.',
                    'Für Angehörige heißt das im Zweifel: Wenn ein Bestatter oder '
                    'Betreuer bereits eingeschaltet ist, kann er die Räumung '
                    'koordinieren, ohne dass Sie zwischen mehreren Stellen vermitteln '
                    'müssen. Wir stimmen uns direkt ab, wenn Sie das so möchten – die '
                    'Rahmenbedingungen dafür stehen auf der Seite für '
                    '<a href="/kooperationspartner/">Kooperationspartner</a>.',
                ],
            },
            {
                'id': 'kosten',
                'titel': 'Kosten und wer sie trägt',
                'absaetze': [
                    'Eine Nachlassräumung wird gerechnet wie jede andere Räumung: '
                    'nach Fläche und Menge. Für ein Haus beginnt sie bei {haus_ab} € '
                    '(Richtwert {haus_rate} € pro m²), für eine Wohnung bei '
                    '{wohnung_ab} € (Richtwert {wohnung_rate} € pro m²). Die '
                    'sorgfältige Trennung von Dokumenten und Erinnerungsstücken '
                    'kostet nichts extra – sie gehört dazu. Konkrete Zahlen für Ihren '
                    'Fall nennt der Preisrechner in etwa {rechner_dauer}; jede '
                    'Rechengröße ist auf '
                    '<a href="/entruempelung-kosten/">Entrümpelung Kosten</a> '
                    'aufgeschlüsselt.',
                    'Getragen werden die Kosten grundsätzlich vom Nachlass, also von '
                    'den Erben. Reicht der Nachlass nicht aus, gibt es Wege, die '
                    'Haftung zu begrenzen; das ist eine Frage an einen Anwalt oder '
                    'das Nachlassgericht. Wir stellen die Rechnung an den '
                    'Auftraggeber.',
                    'Mit einem Steuerabzug nach §35a EStG sollten Erben nicht '
                    'rechnen: Die Haushaltsauflösung führt die Finanzverwaltung als '
                    'nicht begünstigt, und begünstigt sind ohnehin nur Leistungen im '
                    'eigenen Haushalt – die Wohnung des Verstorbenen ist das für '
                    'Erben, die dort nicht gewohnt haben, nicht.',
                ],
            },
        ],

        'quellen': [
            {'schluessel': 'bgb-2040', 'abschnitt': 'erbengemeinschaft',
             'bezug': 'Gemeinschaftliche Verfügung der Erben'},
            {'schluessel': 'nachlass-bgb-1944', 'abschnitt': 'erbengemeinschaft',
             'bezug': 'Sechs Wochen ab Kenntnis'},
            {'schluessel': 'bgb-564', 'abschnitt': 'fristen',
             'bezug': 'Kündigung durch Erbe oder Vermieter binnen eines Monats'},
            {'schluessel': 'bmf-35a-anlage1', 'abschnitt': 'kosten',
             'bezug': 'Haushaltsauflösung „nicht begünstigt“'},
        ],

        'beispiele': [
            {
                'titel': '2-Zimmer-Wohnung, 60 m², normal möbliert',
                'beschreibung': 'Der häufigste Fall: langjährig bewohnte '
                                'Mietwohnung im Erdgeschoss, Kellerabteil dabei.',
                'args': {'objektart': 'wohnung', 'qm': 60, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Einfamilienhaus, 130 m², voll',
                'beschreibung': 'Jahrzehntelang bewohnt, Keller und Dachboden '
                                'gefüllt, einzelne Farben und Lacke in der Garage.',
                'args': {'objektart': 'haus', 'qm': 130, 'fuellgrad': 'voll',
                         'sonderabfall': 'wenige'},
            },
            {
                'titel': '3-Zimmer-Wohnung, 78 m², 2. OG ohne Aufzug',
                'beschreibung': 'Altbau ohne Aufzug – der Stockwerkzuschlag ist '
                                'hier der zweitgrößte Posten nach der Fläche.',
                'args': {'objektart': 'wohnung', 'qm': 78, 'stockwerk': '2og',
                         'fuellgrad': 'mittel'},
            },
        ],

        'ablauf': [
            {'titel': 'Erste Nachricht',
             'text': 'Per Formular, WhatsApp oder Telefon. Sie müssen dabei nichts '
                     'erklären, was Sie nicht erklären wollen – Adresse, ungefähre '
                     'Größe und der zeitliche Rahmen genügen.'},
            {'titel': 'Besichtigung vor Ort',
             'text': 'Wir sehen uns das Objekt in Ruhe an und besprechen, was '
                     'gesichert werden soll und wer über den Nachlass verfügen darf. '
                     'Der Termin ist kostenlos und unverbindlich.'},
            {'titel': 'Festpreisangebot',
             'text': 'Schriftlich, {angebot_frist}, mit Termin; auf Anfrage mit '
                     'ausgewiesenen Arbeitskosten. Sie können es in Ruhe mit '
                     'der Erbengemeinschaft abstimmen.'},
            {'titel': 'Räumung mit Sicherung',
             'text': 'Dokumente, Fotos und Wertsachen werden getrennt gesammelt und '
                     'auf Wunsch fotografiert. Alles Übrige wird sortiert entsorgt '
                     'oder an soziale Einrichtungen weitergegeben.'},
            {'titel': 'Übergabe und Nachweis',
             'text': 'Besenreine Abnahme mit Ihnen oder direkt mit Vermieter, Makler '
                     'oder Verwaltung. Fundstücke werden übergeben, der '
                     'Entsorgungsnachweis geht auf Wunsch an die Erbengemeinschaft.'},
        ],

        'faq': [
            ('Was kostet eine Nachlassräumung?',
             'Sie wird gerechnet wie jede Räumung: nach Fläche und Menge. Ein Haus '
             'beginnt bei {haus_ab} €, Richtwert {haus_rate} € pro m²; eine Wohnung '
             'bei {wohnung_ab} €, Richtwert {wohnung_rate} € pro m². Füllgrad, '
             'Stockwerk ohne Aufzug und Sonderabfälle kommen hinzu, im Servicegebiet '
             'ziehen wir {rabatt} % ab. Das Sichern von Dokumenten und '
             'Erinnerungsstücken kostet nichts extra. Preisstand: {preisstand}.'),
            ('Wer darf eine Nachlassräumung beauftragen?',
             'Jede Person, die über den Nachlass verfügen darf: alle Miterben '
             'gemeinsam, ein Bevollmächtigter, der Inhaber eines Erbscheins oder ein '
             'bestellter Nachlassverwalter beziehungsweise Testamentsvollstrecker. '
             'Bei einer Erbengemeinschaft genügt uns eine formlose schriftliche '
             'Zustimmung aller Beteiligten. Ohne diese Deckung räumen wir nicht – das '
             'schützt Sie ebenso wie uns.'),
            ('Was passiert mit Dokumenten, Fotos und Wertsachen?',
             'Sie werden getrennt gesammelt und Ihnen übergeben – Papiere, '
             'Versicherungsunterlagen, Sparbücher, Fotoalben, Briefe, Schmuck, '
             'Bargeld, Schlüssel und Datenträger. Auf Wunsch fotografieren wir die '
             'Fundstücke und schicken die Aufnahmen vorab, was besonders dann hilft, '
             'wenn mehrere Erben beteiligt sind und niemand vor Ort war.'),
            ('Kaufen Sie Möbel oder Antiquitäten aus dem Nachlass an?',
             'Nein. Wir bewerten und kaufen nichts, und wir rechnen auch keinen '
             '„Wertausgleich" gegen den Preis. Der Festpreis steht vor Beginn fest, '
             'unabhängig davon, was gefunden wird. Diese Trennung ist Absicht: Wer '
             'den Preis vom Fundwert abhängig macht, hat ein Interesse daran, dass '
             'die Bewertung niedrig ausfällt – und Sie können sie nicht überprüfen. '
             'Für eine echte Bewertung ist ein Gutachter oder ein Auktionshaus '
             'zuständig.'),
            ('Wie schnell muss eine Mietwohnung nach einem Todesfall geräumt sein?',
             'Das Mietverhältnis endet nicht mit dem Tod. Tritt niemand aus dem '
             'Haushalt in den Vertrag ein, können die Erben innerhalb eines Monats '
             'außerordentlich mit der gesetzlichen Frist kündigen; danach läuft die '
             'normale Kündigungsfrist. Praktisch heißt das: '
             'Klären Sie zuerst die Kündigung, dann den Übergabetermin, und legen Sie '
             'die Räumung zwei bis drei Werktage davor.'),
            ('Kann ich das Erbe noch ausschlagen, wenn die Wohnung geräumt ist?',
             'Sprechen Sie darüber mit dem Nachlassgericht oder einem Anwalt, '
             'bevor geräumt wird – nicht danach. Wer über Nachlassgegenstände '
             'verfügt, kann damit unter Umständen die Annahme des Erbes erklären. '
             'Wir haben Anfragen aus genau diesem Grund schon gebremst; die '
             'Reihenfolge ist hier wichtiger als das Tempo.'),
            ('Muss ich bei der Räumung dabei sein?',
             'Nein. Zur Besichtigung sollten Sie oder eine bevollmächtigte Person '
             'kommen, weil dort der Umfang festgelegt wird. Bei der Räumung selbst '
             'nicht – viele Angehörige wohnen weit entfernt. Schlüsselübergabe, '
             'Abnahme und Rückgabe an die Hausverwaltung regeln wir dann direkt und '
             'melden uns danach bei Ihnen.'),
            ('Arbeiten Sie mit Bestattern und Nachlassverwaltern zusammen?',
             'Ja, wenn Sie das möchten. Wenn bereits ein Bestattungshaus, ein rechtlicher '
             'Betreuer oder ein Nachlassverwalter eingeschaltet ist, stimmen wir uns '
             'direkt mit dieser Stelle ab, damit Sie nicht zwischen mehreren '
             'Beteiligten vermitteln müssen. Rechnung mit ausgewiesener '
             'Umsatzsteuer und Entsorgungsnachweis gehören in diesen Fällen '
             'standardmäßig dazu.'),
            ('Ist eine Nachlassräumung steuerlich absetzbar?',
             'Nach §35a EStG meist nicht. Die Beispielliste des '
             'Bundesfinanzministeriums führt die Haushaltsauflösung als nicht '
             'begünstigt, und begünstigt sind nur Leistungen im eigenen Haushalt. '
             'Ob die Kosten an anderer Stelle eine Rolle spielen, etwa bei der '
             'Erbschaftsteuer, ist eine Frage an Ihren Steuerberater. Eine Rechnung '
             'mit ausgewiesenen Arbeitskosten bekommen Sie auf Anfrage.'),
            ('Nachlassauflösung, Nachlassräumung, Haushaltsauflösung im '
             'Todesfall – wo ist der Unterschied?',
             'Im Sprachgebrauch keiner – „Nachlassauflösung" und '
              '„Nachlassräumung" meinen dasselbe, und wer nach '
              '„Haushaltsauflösung im Todesfall" sucht, meint es auch. Der '
              'Unterschied zur gewöhnlichen Haushaltsauflösung liegt nicht in '
              'der Arbeit, sondern im Umgang: Dokumente, Fotos und '
              'persönliche Papiere werden gesichtet und übergeben, statt '
              'entsorgt zu werden.'),
        ],

        'related': ['haushaltsaufloesung', 'wohnungsaufloesung',
                    'messie-wohnung-entruempeln', 'sanierung-renovierung'],

        'staedte': ['halle', 'leipzig', 'dresden', 'magdeburg', 'chemnitz',
                    'hannover', 'dessau', 'merseburg', 'naumburg', 'zwickau',
                    'stendal', 'wernigerode'],

        'seo_title': 'Nachlassräumung Halle & Leipzig – ab {wohnung_ab} € | Rümpelwerk',
        'seo_description': (
            'Nachlassräumung Halle und Leipzig ab {wohnung_ab} €: Dokumente '
            'gesichert, besenrein übergeben. Festpreis bei Besichtigung. '
            'Jetzt Termin buchen.'
        ),
        'seo_keywords': (
            'Nachlassräumung, Nachlassauflösung, Entrümpelung nach Todesfall, '
            'Wohnung auflösen nach Todesfall, Erbschaftsräumung, '
            'Nachlassräumung Kosten, Haushaltsauflösung Todesfall'
        ),
    },

    # ───────────────────────────────────────────────────────────────────────
    # A8 — /gewerbeentruempelung/
    #
    # B2B: andere Entscheider, andere Argumente. Der GSC-Export nennt
    # „gewerbe entrümpelung" (Position 1,0), „firmenauflösung halle" (4,3) und
    # „betriebsauflösung halle" (16,0) – alle drei ohne eigene Seite. Die
    # Synonyme Firmenauflösung und Betriebsauflösung stehen deshalb im Text
    # und in den Keywords, nicht nur im Titel.
    'gewerbeentruempelung': {
        'name': 'Gewerbeentrümpelung',
        'h1': 'Gewerbeentrümpelung',
        'h1_em': 'Zum Stichtag geräumt.',
        'keyword': 'gewerbeentrümpelung',
        'objektart': 'gewerbe',

        'hero_sub': (
            'Büro, Lager, Werkstatt, Praxis oder Gastronomie räumen lassen – '
            'zum vereinbarten Stichtag, mit Entsorgungsnachweis und Rechnung '
            'mit ausgewiesener Umsatzsteuer. Festpreis ab {gewerbe_ab} €. Nach '
            'Absprache auch außerhalb der Geschäftszeiten, damit der Betrieb '
            'weiterläuft.'
        ),

        'answer_frage': 'Was kostet eine Gewerbeentrümpelung?',
        # EIG397 (02.10.2026): "gewerbe entrümpelung kosten" traf diese Seite
        # auf Position 54,5 - die Antwort nannte den Preis, aber nicht, wie er
        # entsteht. Jetzt: Satz, Mindestpreis, gerechnetes Beispiel und was erst
        # die Besichtigung klaert. Die "datenschutzkonforme Aktenvernichtung"
        # als feste Zusage ist raus (dieselbe Begruendung wie EIG271).
        'answer': (
            'Eine Gewerbeentrümpelung kostet bei Rümpelwerk Mitteldeutschland '
            '{gewerbe_rate} € pro m² Gewerbefläche, mindestens {gewerbe_ab} €. Eine '
            'normal ausgestattete Fläche von {gewerbe_qm} m² liegt damit bei '
            '{gewerbe_beispiel}. Füllgrad und Sonderabfall verändern den Preis; '
            'Rückbau, Akten und Datenträger klären wir bei der kostenlosen '
            'Besichtigung und weisen sie im Festpreisangebot einzeln aus. '
            'Preisstand: {preisstand}.'
        ),

        'leistungsumfang': [
            'Büroflächen: Schreibtische, Rollcontainer, Regale, Trennwände, Stühle',
            'Lager und Werkstatt: Palettenregale, Werkbänke, Maschinen, Restbestände',
            'Ladenlokale: Verkaufstresen, Ladenbau, Warenträger, Beschilderung',
            'Gastronomie: Küchentechnik, Kühlung, Mobiliar, Theke, Zapfanlage',
            'Praxen und Kanzleien: Einrichtung, Wartebereich, Aktenschränke',
            'IT und Elektroschrott: Rechner, Monitore, Serverschränke, Verkabelung',
            'Rückbau von Einbauten und besenreine Übergabe an den Vermieter',
        ],

        'abgrenzung': [
            'Kernsanierung und statische Eingriffe sind Bauleistungen und brauchen '
            'einen Bauunternehmer. Wir übernehmen Rückbau von Einbauten, keine '
            'Eingriffe in die Gebäudestruktur.',
            'Schadstoffsanierung – Asbest, künstliche Mineralfasern, kontaminierte '
            'Böden – gehört zu einem zugelassenen Fachbetrieb. Wir benennen den '
            'Verdacht bei der Besichtigung, statt ihn zu übergehen.',
            'Maschinen mit Restwert verwerten wir nicht. Wenn Anlagen einen Erlös '
            'bringen können, gehören sie zu einem Industrieauktionator – wir räumen, '
            'was danach übrig bleibt.',
            'Gefahrstoffe aus Produktion und Labor brauchen eine eigene '
            'Entsorgungskette. Sagen Sie uns vorher, was im Objekt lagert; danach '
            'sagen wir Ihnen, was wir übernehmen können.',
        ],

        'abschnitte': [
            {
                'id': 'unterschied',
                'titel': 'Betriebsauflösung, Firmenauflösung, Büroräumung – was gemeint ist',
                'absaetze': [
                    'Im Sprachgebrauch laufen mehrere Begriffe nebeneinander, die '
                    'unterschiedliche Anlässe meinen. Eine <strong>Büroräumung</strong> '
                    'ist der Umzug oder die Verkleinerung einer Fläche – der Betrieb '
                    'läuft weiter. Eine <strong>Betriebsauflösung</strong> oder '
                    '<strong>Firmenauflösung</strong> beendet den Geschäftsbetrieb an '
                    'diesem Standort: Ausstattung, Lager und Akten müssen weg, und '
                    'meist steht ein Stichtag im Mietvertrag oder im '
                    'Übergabeprotokoll.',
                    'Der dritte Fall ist die <strong>Insolvenz</strong>. Auftraggeber '
                    'ist dann in der Regel der Insolvenzverwalter, und die Anforderung '
                    'ist eine andere: nachvollziehbare Dokumentation, klare Trennung '
                    'zwischen verwertbarem und zu entsorgendem Bestand, prüfbare '
                    'Nachweise.',
                    'Für die Kalkulation ist der Unterschied gering – gerechnet wird '
                    'nach Fläche. Für den Ablauf ist er groß, weil bei einer '
                    'Auflösung fast immer ein fester Termin dahintersteht.',
                ],
            },
            {
                'id': 'kosten',
                'titel': 'Was kostet eine Gewerbeentrümpelung? Der Rechenweg',
                'absaetze': [
                    'Der Grundpreis ist Fläche mal Satz: {gewerbe_rate} € pro m², '
                    'mindestens {gewerbe_ab} €. Bis {gewerbe_grenze_qm} m² gilt also '
                    'der Mindestpreis – Anfahrt, Fahrzeug und Entsorgung kosten bei '
                    'einem kleinen Büro dasselbe wie bei einem größeren. Der Satz '
                    'liegt unter dem für Wohnraum, weil Gewerbeflächen meist weniger '
                    'dicht bestückt und besser zugänglich sind: Eine Halle mit '
                    'Rolltor räumt sich schneller als ein Büro im dritten Stock.',
                    'Auf den Grundpreis wirken zwei bezifferte Größen. Der '
                    '<strong>Füllgrad</strong> multipliziert ihn – von Faktor '
                    '{fuellgrad_leicht} für eine fast leere Fläche bis {fuellgrad_voll} '
                    'für ein volles Lager. <strong>Sonderabfall</strong> wie Altöl, '
                    'Farben oder Lösemittel kommt fest dazu: '
                    '{sonderabfall_wenige_txt} € für einzelne Posten, '
                    '{sonderabfall_viele_txt} € für viele. Liegt der Betrieb in '
                    'unserem Servicegebiet, ziehen wir {rabatt} % ab, höchstens bis '
                    'zum Mindestpreis. Mit genau diesen Größen rechnet der '
                    'Preisrechner auf dieser Seite.',
                    'Was der Rechner nicht kennt, klären wir bei der Besichtigung: '
                    'Etage und Aufzug (der Stockwerkzuschlag aus der '
                    'Wohnungsrechnung gilt für Gewerbe nicht), Ladezone und '
                    'Halteverbot, den Rückbau von Trennwänden oder Ladenbau, Kühl- '
                    'und Klimageräte, Akten und Datenträger sowie Arbeit außerhalb '
                    'der Geschäftszeiten. Für diese Posten gibt es keine Pauschale; '
                    'sie stehen nach der Besichtigung als eigene Position im Angebot.',
                    'Die Rechnung weist die Umsatzsteuer aus, die Kosten sind '
                    'Betriebsausgabe – §35a EStG gilt nur für Aufwendungen, die keine '
                    'Betriebsausgaben sind, und spielt für Betriebe deshalb keine '
                    'Rolle. In ein belastbares Festpreisangebot gehören:',
                ],
                'liste': [
                    '<strong>der Endbetrag als Festpreis</strong>, mit '
                    'ausgewiesener Umsatzsteuer;',
                    '<strong>die Positionen einzeln</strong>: Räumung nach Fläche, '
                    'Sonderabfall, Rückbau, Akten und Datenträger;',
                    '<strong>der Räumungstermin mit Datum</strong>, abgestimmt auf '
                    'Ihren Übergabetermin;',
                    '<strong>was nicht enthalten ist</strong> – etwa '
                    'Schadstoffsanierung oder Gefahrstoffe aus Produktion und Labor;',
                    '<strong>welche Nachweise</strong> Sie über die Entsorgung '
                    'bekommen.',
                ],
            },
            {
                'id': 'nachweise',
                'titel': 'Entsorgungsnachweise: was die Gewerbeabfallverordnung verlangt',
                'absaetze': [
                    'Für Betriebe gilt beim Abfall eine eigene Verordnung. Die '
                    'Gewerbeabfallverordnung verpflichtet Erzeuger und Besitzer '
                    'gewerblicher Siedlungsabfälle, Papier, Glas, Kunststoffe, Metalle, '
                    'Holz, Textilien und Bioabfälle getrennt zu sammeln und dem '
                    'Recycling zuzuführen – und das zu dokumentieren, etwa mit '
                    'Lageplänen, Fotos und Liefer- oder Wiegescheinen. Die Behörde '
                    'kann diese Dokumentation verlangen.',
                    'Bei einer Räumung heißt das: Klären Sie vor dem Auftrag, welche '
                    'Belege über den Verbleib Sie bekommen, und legen Sie sie zur '
                    'Rechnung. Wir trennen beim Verladen nach Fraktionen; welcher '
                    'Nachweis in Ihre Dokumentation passt, legen wir bei der '
                    'Besichtigung fest und schreiben ihn ins Angebot.',
                ],
            },
            {
                'id': 'dsgvo',
                'titel': 'Aktenvernichtung nach DSGVO – der Punkt, an dem es teuer wird',
                'absaetze': [
                    'Personenbezogene Unterlagen dürfen bei einer Räumung nicht im '
                    'Container landen. Das betrifft mehr, als die meisten auf dem '
                    'Schirm haben: Personalakten, Bewerbungsunterlagen, '
                    'Kundenkarteien, Rechnungen mit Namen, Lieferscheine, '
                    'Patientenunterlagen, Notizbücher – und die Datenträger dazu.',
                    'Nach der Datenschutz-Grundverordnung haftet der Verantwortliche '
                    'für die Vernichtung, nicht der Entrümpler. Genau deshalb ist ein '
                    'schriftlicher <strong>Vernichtungsnachweis</strong> kein '
                    'Papierkram, sondern Ihr Beleg. Datenschutzrelevantes Material '
                    'trennen wir deshalb vom übrigen Räumgut ab; wie es vernichtet '
                    'und nachgewiesen wird, stimmen wir vor dem Auftrag mit Ihnen ab.',
                    'Für IT gilt dasselbe eine Stufe schärfer: Festplatten, SSDs, '
                    'Kopierer mit Speicher, Smartphones und Backup-Bänder enthalten '
                    'Daten, die ein einfaches Löschen nicht entfernt. Sagen Sie uns '
                    'bei der Besichtigung, welche Geräte betroffen sind – dann werden '
                    'sie getrennt erfasst und mit eigenem Nachweis vernichtet.',
                ],
                # EIG271 (SEO-Audit 25.09.2026): Verschlossene Behaelter,
                # Vernichtung nach Schutzklasse und ein Nachweis mit Datum,
                # Menge und Verfahren sind unbestaetigte Zusagen ("Beim
                # Kunden" Nr. 35). Die Liste sagt jetzt, worauf der Kunde
                # achten muss - nicht, was der Betrieb zusagt.
                'liste': [
                    '<strong>Getrennt vom Räumgut</strong> – nicht offen auf dem '
                    'Wagen zwischen Möbeln und Sperrmüll.',
                    '<strong>Schutzbedarf vorher klären</strong> – Personalakten '
                    'und Patientendaten verlangen mehr als Werbepost.',
                    '<strong>Nachweis vereinbaren</strong>, damit er in Ihre '
                    'Datenschutzdokumentation passt.',
                    '<strong>Datenträger separat</strong>: Festplatten und Kopierer '
                    'werden nicht wie Elektroschrott behandelt.',
                ],
            },
            {
                'id': 'termine',
                'titel': 'Stichtag, Wunschzeiten und laufender Betrieb',
                'absaetze': [
                    'Bei gewerblichen Aufträgen ist der Termin fast immer der '
                    'kritische Punkt, nicht der Preis. Ein Mietvertrag endet zum '
                    'Monatsletzten, ein Nachmieter zieht am Ersten ein, eine '
                    'Ladenfläche muss vor dem Umbau leer sein. Wir setzen den Termin '
                    'deshalb ins Angebot – mit Datum, nicht als Absichtserklärung.',
                    'Wenn der Betrieb weiterläuft, arbeiten wir nach Absprache '
                    'außerhalb der Geschäftszeiten oder etagenweise, damit '
                    'die verbleibenden Bereiche nutzbar bleiben. Das kostet mehr '
                    'Koordination und wird vorher besprochen, nicht hinterher '
                    'berechnet.',
                    'In Innenstadtlagen kommt die Logistik dazu: Halteverbotszone '
                    'beantragen, Ladezone abstimmen, Aufzug reservieren, '
                    'Gebäudemanagement informieren. Wir sagen Ihnen bei der '
                    'Besichtigung, was davon nötig ist und wer es beantragt.',
                ],
            },
            {
                'id': 'branchen',
                'titel': 'Was in den einzelnen Branchen anders ist',
                'absaetze': [
                    'Die Fläche ist bei allen dieselbe Rechengröße – der Aufwand '
                    'nicht. Vier Fälle begegnen uns am häufigsten.',
                ],
                'liste': [
                    '<strong>Büro und Kanzlei.</strong> Viel Papier, viel IT, wenig '
                    'Gewicht. Der Schwerpunkt liegt auf Datenschutz und darauf, dass '
                    'am Montag niemand vor einem halb geräumten Flur steht.',
                    '<strong>Lager und Werkstatt.</strong> Hohes Gewicht, '
                    'Palettenregale, Restbestände, oft Altöl und Chemie. Hier '
                    'entscheidet die Trennung über den Entsorgungspreis.',
                    '<strong>Gastronomie.</strong> Kühltechnik enthält Kältemittel '
                    'und muss fachgerecht entsorgt werden; Fettabscheider und '
                    'Zapfanlagen sind eigene Positionen. Ladenbau ist meist fest '
                    'verbaut und wird zurückgebaut.',
                    '<strong>Praxis.</strong> Patientenunterlagen und medizinische '
                    'Geräte haben eigene Vorschriften. Was unter die '
                    'Aufbewahrungspflicht fällt, wird nicht vernichtet, sondern '
                    'übergeben.',
                ],
            },
        ],

        'quellen': [
            {'schluessel': 'gewabfv-3', 'abschnitt': 'nachweise',
             'bezug': 'Getrennte Sammlung und Dokumentation'},
        ],

        # EIG397: Die Tabelle trennt, was der Rechner kennt, von dem, was erst
        # die Besichtigung festlegt. Fuer die zweite Gruppe gibt pricing.py
        # keinen Satz her - deshalb steht dort keine Zahl, sondern der Ort,
        # an dem sie entsteht (offene Frage an Oliver, siehe Bericht).
        'vergleich': {
            'titel': 'Gewerbeentrümpelung: was den Preis bestimmt und wann er feststeht',
            'fazit_frage': 'Wovon hängen die Kosten einer Gewerbeentrümpelung ab?',
            'fazit': ('Von Fläche, Füllgrad und Sonderabfall – diese drei rechnet '
                      'der Preisrechner: {gewerbe_rate} € pro m², mindestens '
                      '{gewerbe_ab} €, der Füllgrad als Faktor, Sonderabfall als '
                      'fester Aufschlag. Rückbau, Akten, Datenträger, Kühltechnik und '
                      'Arbeit außerhalb der Geschäftszeiten haben keinen '
                      'Pauschalpreis; sie stehen nach der kostenlosen Besichtigung '
                      'als eigene Position im Festpreisangebot. '
                      'Preisstand: {preisstand}.'),
            'kopf': ['Kostenfaktor', 'Wie er wirkt', 'Steht fest'],
            'zeilen': [
                ['Fläche', '{gewerbe_rate} € pro m², mindestens {gewerbe_ab} €',
                 'im Preisrechner'],
                ['Füllgrad', 'Faktor {fuellgrad_leicht} bis {fuellgrad_messi} auf '
                 'den Grundpreis', 'im Preisrechner, bestätigt bei der Besichtigung'],
                ['Sonderabfall', 'plus {sonderabfall_wenige_txt} € bei einzelnen '
                 'Posten, plus {sonderabfall_viele_txt} € bei vielen',
                 'im Preisrechner'],
                ['Standort im Servicegebiet', 'minus {rabatt} %, höchstens bis zum '
                 'Mindestpreis', 'im Preisrechner'],
                ['Etage, Aufzug, Ladezone', 'kein Pauschalsatz',
                 'bei der Besichtigung'],
                ['Rückbau von Einbauten', 'eigene Position', 'bei der Besichtigung'],
                ['Akten und Datenträger', 'eigene Position, Nachweis nach Absprache',
                 'bei der Besichtigung'],
                ['Arbeit außerhalb der Geschäftszeiten', 'nach Absprache',
                 'bei der Besichtigung'],
            ],
        },

        'beispiele': [
            {
                'titel': 'Büroetage, 180 m², normal ausgestattet',
                'beschreibung': 'Schreibtische, Rollcontainer, Aktenschränke, IT – '
                                'gerechnet ohne Aktenvernichtung, die als eigene '
                                'Position dazukommt.',
                'args': {'objektart': 'gewerbe', 'qm': 180, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Lagerhalle, 400 m², voll',
                'beschreibung': 'Palettenregale, Restbestände und Werkstattbereich, '
                                'dazu Altöl und Farbreste als Sonderabfall.',
                'args': {'objektart': 'gewerbe', 'qm': 400, 'fuellgrad': 'voll',
                         'sonderabfall': 'wenige'},
            },
            {
                'titel': 'Ladenlokal, 90 m², leicht möbliert',
                'beschreibung': 'Verkaufstresen, Warenträger und Beschilderung nach '
                                'einer Geschäftsaufgabe.',
                'args': {'objektart': 'gewerbe', 'qm': 90, 'fuellgrad': 'leicht'},
            },
        ],

        'ablauf': [
            {'titel': 'Anfrage mit Stichtag',
             'text': 'Nennen Sie Fläche, Nutzung und den Termin, zu dem übergeben '
                     'werden muss. Wir melden uns in {reaktion} mit einer '
                     'Einschätzung, ob der Termin trägt.'},
            {'titel': 'Begehung',
             'text': 'Vor Ort klären wir Zugang, Aufzug, Ladezone, Restbestände, '
                     'Datenschutzmaterial und was zurückgebaut werden muss. Bei '
                     'mehreren Standorten machen wir das gebündelt.'},
            {'titel': 'Angebot mit Terminplan',
             'text': 'Festpreis mit ausgewiesener Umsatzsteuer, Positionen für '
                     'Aktenvernichtung und Nachweise, dazu ein Ablaufplan mit '
                     'Datum – abgestimmt auf Ihren laufenden Betrieb.'},
            {'titel': 'Räumung',
             'text': 'Auf Wunsch außerhalb der Geschäftszeiten oder etagenweise. '
                     'Datenschutzrelevantes Material bleibt getrennt vom Rest.'},
            {'titel': 'Übergabe und Nachweise',
             'text': 'Besenreine Abnahme mit Vermieter oder Verwaltung, dazu '
                     'Entsorgungsnachweis für die Buchhaltung; wie Akten und '
                     'Datenträger nachgewiesen werden, steht im Angebot.'},
        ],

        'faq': [
            ('Was kostet eine Gewerbeentrümpelung?',
             'Gewerbeflächen rechnen wir mit {gewerbe_rate} € pro m², mindestens '
             '{gewerbe_ab} € – bis {gewerbe_grenze_qm} m² gilt also der Mindestpreis. '
             'Eine normal ausgestattete Fläche von {gewerbe_qm} m² liegt bei '
             '{gewerbe_beispiel}. Der Füllgrad multipliziert den Grundpreis, '
             'Sonderabfall kommt fest dazu. Rückbau, Akten, Datenträger und Arbeit '
             'außerhalb der Geschäftszeiten stehen nach der Besichtigung als eigene '
             'Positionen im Festpreisangebot, mit ausgewiesener Umsatzsteuer. '
             'Preisstand: {preisstand}.'),
            ('Wie werden Akten und Datenträger vernichtet?',
             'Datenschutzrelevantes Material trennen wir vom übrigen Räumgut ab. '
             'Welcher Schutzbedarf besteht und wie die Vernichtung nachgewiesen '
             'wird, klären wir bei der Besichtigung und halten es im Angebot fest. '
             'Festplatten, SSDs, Kopierer mit '
             'Speicher und Backup-Medien werden dabei separat erfasst – einfaches '
             'Löschen genügt bei ihnen nicht.'),
            ('Können Sie außerhalb der Geschäftszeiten räumen?',
             # EIG272 (SEO-Audit 25.09.2026): "der Normalfall" war eine
             # unbestaetigte Zusage ("Beim Kunden" Nr. 11) - jetzt "auf Wunsch".
             'Nach Absprache ja – außerhalb der Geschäftszeiten oder '
             'etagenweise, wenn der Betrieb weiterläuft. Welche Zeiten möglich sind, klären wir bei der '
             'Besichtigung; der Mehraufwand steht vorher im Angebot.'),
            ('Arbeiten Sie auch für Insolvenzverwalter?',
             'Ja. Dabei ist die Dokumentation wichtiger als das Tempo: klare Trennung '
             'zwischen verwertbarem und zu entsorgendem Bestand, nachvollziehbare '
             'Mengen, prüfbare Entsorgungsnachweise. Anlagen mit Restwert räumen wir '
             'nicht ab, sondern stellen sie bereit – deren Verwertung gehört zu einem '
             'Industrieauktionator.'),
            ('Übernehmen Sie auch den Rückbau von Einbauten?',
             'Ja, soweit es sich um nichttragende Einbauten handelt: Trennwände, '
             'Ladenbau, Theken, Kabeltrassen, Bodenbeläge, Beschilderung. Eingriffe '
             'in die Gebäudestruktur und Kernsanierung sind Bauleistungen und '
             'gehören zu einem Bauunternehmen.'),
            ('Was passiert mit Kühltechnik aus der Gastronomie?',
             'Kühl- und Klimageräte enthalten Kältemittel und müssen fachgerecht '
             'entsorgt werden – sie dürfen weder geöffnet noch mit dem übrigen '
             'Metallschrott vermischt werden. Wir erfassen sie getrennt und weisen '
             'sie im Angebot als eigene Position aus.'),
            ('Bekomme ich einen Entsorgungsnachweis?',
             'Ja, auf Wunsch. Für Betriebe ist er mehr als eine Formalität: Die '
             'Gewerbeabfallverordnung verlangt, die getrennte Sammlung zu '
             'dokumentieren, und die Behörde kann die Belege anfordern. Welche '
             'Angaben Ihre Dokumentation braucht, klären wir bei der Besichtigung; '
             'der Nachweis steht dann im Angebot.'),
            ('Räumen Sie auch mehrere Standorte gleichzeitig?',
             'Ja. Bei Filialnetzen und mehreren Objekten bündeln wir Begehung und '
             'Angebot und legen einen gemeinsamen Terminplan an. Für wiederkehrende '
             'Aufträge gibt es feste Absprachen – die Rahmenbedingungen dafür stehen '
             'auf der Seite für Kooperationspartner.'),
            ('Betriebsauflösung, Büroauflösung, Hallenräumung – machen Sie '
             'das auch?',
             'Ja, das sind alles Gewerberäumungen und werden gleich '
              'gerechnet: nach Grundfläche, {gewerbe_rate} € pro m² ab '
              '{gewerbe_ab} €. Ob Büro, Lager, Werkstatt, Ladenlokal oder '
              'Praxis, ändert am Preis nichts – am Ablauf schon: Akten und '
              'Datenträger werden getrennt behandelt, Metall und Holz gehen '
              'getrennt in die Verwertung.'),
        ],

        'related': ['sperrmuell-entsorgung', 'kellerentruempelung',
                    'sanierung-renovierung', 'entruempelung-kosten'],

        'staedte': ['halle', 'leipzig', 'magdeburg', 'dresden', 'chemnitz',
                    'hannover', 'braunschweig', 'merseburg', 'dessau', 'zwickau',
                    'bitterfeld', 'stendal'],

        # Kein "&" im Titel: check_seo zaehlt das ausgelieferte HTML, dort
        # steht "&amp;" - vier Zeichen statt einem, und der Titel lag mit
        # 63 sichtbaren Zeichen bei gemessenen 67 (erlaubt 30-65).
        'seo_title': 'Gewerbeentrümpelung Kosten ab {gewerbe_ab} € | Rümpelwerk',
        'seo_description': (
            'Was kostet eine Gewerbeentrümpelung? {gewerbe_rate} € pro m², ab '
            '{gewerbe_ab} €: Rechenweg, Nachweise nach GewAbfV, '
            'Festpreis-Angebot nach Besichtigung.'
        ),
        'seo_keywords': (
            'Gewerbeentrümpelung, Gewerbeentrümpelung Kosten, Gewerbe '
            'Entrümpelung Kosten pro qm, Betriebsauflösung, Firmenauflösung, '
            'Büroräumung Kosten, Lagerräumung, Geschäftsauflösung, '
            'Entsorgungsnachweis Gewerbe'
        ),
    },

    # ───────────────────────────────────────────────────────────────────────
    # A9 — /messie-wohnung-entruempeln/
    #
    # ⚠️ Die Aufgabenbeschreibung nennt „neutrale Fahrzeuge", „Desinfektion"
    # und „Kostenübernahme durch das Sozialamt" als Schwerpunkte. Für keinen
    # der drei Punkte gibt es im Betrieb eine Grundlage, die hier belegbar
    # wäre – also stehen sie NICHT als Zusage auf der Seite.
    #
    # Was belegbar ist: Der Preisrechner kennt die Füllgrade „verschmutzt"
    # (1,55) und „messi" (1,75). Der Betrieb kalkuliert diese Fälle also und
    # nimmt sie an. Alles Weitere ist als Frage formuliert, die vor dem
    # Auftrag geklärt wird – das ist ehrlicher und in dieser Zielgruppe auch
    # glaubwürdiger als ein Versprechen.
    #
    # Wenn Oliver bestätigt, dass unbeschriftete Fahrzeuge oder eine
    # Desinfektion angeboten werden, gehören die Abschnitte umgeschrieben.
    'messie-wohnung-entruempeln': {
        'name': 'Messie-Wohnung entrümpeln',
        'h1': 'Messie-Wohnung',
        'h1_em': 'Ohne Vorwurf geräumt.',
        'keyword': 'messie wohnung entrümpeln',
        'objektart': 'wohnung',

        'hero_sub': (
            'Stark vermüllte Wohnungen und Häuser räumen wir vollständig, '
            'sortiert und ohne Kommentar. Sie müssen vorher nicht aufräumen, '
            'nichts erklären und nicht dabei sein. Festpreis ab {wohnung_ab} € '
            'nach kostenloser Besichtigung.'
        ),

        'answer_frage': 'Was kostet es, eine Messie-Wohnung entrümpeln zu lassen?',
        'answer': (
            'Eine Messie-Wohnung zu entrümpeln bedeutet, eine stark vermüllte '
            'Wohnung vollständig zu räumen, den Inhalt zu trennen und persönliche '
            'Unterlagen zu sichern. Rümpelwerk Mitteldeutschland übernimmt solche '
            'Räumungen ab {wohnung_ab} €; der erhöhte Aufwand steckt im Füllgrad, '
            'der den Grundpreis um bis zu {fuellgrad_messi_prozent} % erhöht. Sie müssen vorher nichts '
            'aufräumen und nicht anwesend sein. Preisstand: {preisstand}.'
        ),

        'leistungsumfang': [
            'Vollständige Räumung stark vermüllter Wohnungen und Häuser',
            'Keller, Dachboden, Balkon, Nebenräume und Außenbereich',
            'Sortenreine Trennung, auch wenn dafür jede Schicht einzeln durchgeht',
            'Sichern von Ausweisen, Verträgen, Fotos, Bargeld und Datenträgern',
            'Entsorgung verdorbener Lebensmittel und stark verschmutzter Textilien',
            'Grobreinigung der geräumten Flächen, Boden gefegt',
            'Auf Wunsch Abstimmung mit Betreuung, Angehörigen oder Hausverwaltung',
            'Anschließende Renovierung im selben Auftrag möglich',
        ],

        'abgrenzung': [
            'Wir sind keine Schädlingsbekämpfer. Bei Befall mit Ratten, Schaben '
            'oder Bettwanzen muss ein Fachbetrieb ran – sinnvollerweise vor der '
            'Räumung, sonst wandert das Problem mit. Wir sagen Ihnen, was wir '
            'sehen, und benennen es klar.',
            'Wir sind kein Reinigungsunternehmen für Extremfälle. Grobreinigung '
            'nach der Räumung machen wir; eine Desinfektion nach Infektionsschutz '
            'gehört zu einer dafür zugelassenen Fachfirma.',
            'Diskretion sagen wir zu, soweit sie in unserer Hand liegt: Wir '
            'sprechen mit niemandem im Haus über den Auftrag. Unsere Fahrzeuge '
            'sind allerdings beschriftet. Wenn das ein Problem ist, sagen Sie es '
            'vorher – über Ladestelle und Ablauf lässt sich reden.',
            'Wir übernehmen keine Betreuung und keine Beratung. Wenn hinter der '
            'Wohnung eine Erkrankung steht, hilft eine Beratungsstelle oder eine '
            'Betreuung weiter – wir räumen nur die Wohnung.',
        ],

        'abschnitte': [
            {
                'id': 'unterschied',
                'titel': 'Was bei einer Messie-Wohnung anders ist',
                'absaetze': [
                    'Der Unterschied zu einer normalen '
                    '<a href="/wohnungsaufloesung/">Wohnungsauflösung</a> ist nicht '
                    'die Menge allein, sondern dass nichts mehr sortiert ist. Es gibt '
                    'keine Schränke, in denen die Papiere liegen, und keine Kartons, '
                    'die man stapeln kann. Alles liegt in Schichten, und in jeder '
                    'Schicht kann etwas Wichtiges stecken.',
                    'Deshalb arbeiten wir langsamer und in kleineren Abschnitten. '
                    'Statt Räume auszuräumen, tragen wir Schichten ab und sehen dabei '
                    'durch: Ausweise, Verträge, Fotos, Bargeld, Schlüssel und '
                    'Datenträger werden getrennt gesammelt und übergeben. Genau das '
                    'ist der Grund, warum solche Aufträge mehr Zeit brauchen als eine '
                    'Räumung derselben Fläche im Normalzustand.',
                    'Hinzu kommen Dinge, die es sonst nicht gibt: verdorbene '
                    'Lebensmittel, durchnässte Textilien, Gerüche, gelegentlich '
                    'Ungeziefer. Damit rechnen wir, und wir bringen die passende '
                    'Ausrüstung mit. Sie müssen nichts davon vorbereiten.',
                ],
            },
            {
                'id': 'scham',
                'titel': 'Sie müssen sich nicht erklären',
                'absaetze': [
                    'Fast alle Anfragen zu diesem Thema beginnen mit einer '
                    'Entschuldigung. Das ist verständlich und unnötig. Wir haben '
                    'diese Wohnungen oft gesehen, und wir bewerten sie nicht – weder '
                    'bei der Besichtigung noch im Team, noch gegenüber Nachbarn.',
                    'Praktisch heißt das: Sie müssen vorher nichts aufräumen. Der '
                    'häufigste Grund, warum eine Räumung monatelang verschoben wird, '
                    'ist der Versuch, vorher selbst „einen Anfang zu machen". Das '
                    'führt fast immer dazu, dass gar nichts passiert. Rufen Sie an, '
                    'wie es ist.',
                    'Sie müssen auch nicht dabei sein. Viele Auftraggeber übergeben '
                    'den Schlüssel und kommen erst zur Abnahme wieder. Wenn Sie das '
                    'so möchten, sagen Sie es – wir schicken Ihnen Fotos vom '
                    'Ergebnis, statt Sie durch die Wohnung zu führen.',
                ],
            },
            {
                'id': 'angehoerige',
                'titel': 'Für Angehörige, Betreuer und Hausverwaltungen',
                'absaetze': [
                    'Ein großer Teil dieser Aufträge kommt nicht von der Person '
                    'selbst, sondern von Angehörigen, rechtlichen Betreuern oder der '
                    'Hausverwaltung – oft, wenn eine Kündigung im Raum steht oder das '
                    'Gesundheitsamt eingeschaltet wurde.',
                    'Dabei gilt eine Grenze, die wir nicht verschieben: Wir räumen '
                    'nur mit dem Einverständnis der verfügungsberechtigten Person '
                    'oder auf Grundlage einer entsprechenden Befugnis. Eine Wohnung '
                    'gegen den Willen der Bewohnerin oder des Bewohners zu räumen, '
                    'ist keine Dienstleistung, die man bestellen kann – dafür braucht '
                    'es einen Titel und den zuständigen Gerichtsvollzieher.',
                    'Wenn eine Betreuung besteht, klären Sie die Kostenfrage vorab mit '
                    'der Betreuung und gegebenenfalls dem Sozialamt. Ob Kosten '
                    'übernommen werden, entscheidet immer die zuständige Stelle und '
                    'nie wir; wir stellen aber ein schriftliches Angebot, das Sie dort '
                    'einreichen können.',
                ],
            },
            {
                'id': 'ablauf-praxis',
                'titel': 'Wie so eine Räumung praktisch abläuft',
                'absaetze': [
                    'Die Besichtigung dauert länger als sonst. Wir sehen uns '
                    'jeden Raum an, schätzen die Menge, prüfen '
                    'Zugang und Treppenhaus und fragen nach dem, worauf wir achten '
                    'sollen. Danach folgt das verbindliche Festpreisangebot.',
                ],
                'liste': [
                    '<strong>Wir bringen alles mit</strong> – Schutzausrüstung, '
                    'Handschuhe, Atemschutz, Beleuchtung, Behälter. Sie müssen nichts '
                    'stellen.',
                    '<strong>Schichtweise statt raumweise.</strong> Jede Lage wird '
                    'durchgesehen, bevor sie auf den Wagen geht.',
                    '<strong>Getrennt gesammelt:</strong> Dokumente, Schlüssel, '
                    'Ausweise, Bargeld, Fotos, Datenträger – in eigenen Behältern.',
                    '<strong>Mehrere Tage sind normal.</strong> Bei starkem Füllgrad '
                    'planen wir von vornherein mit Folgetagen statt mit Überstunden.',
                    '<strong>Grobreinigung zum Schluss:</strong> Boden gefegt, grober '
                    'Schmutz entfernt, Fenster geöffnet.',
                ],
            },
            {
                'id': 'danach',
                'titel': 'Was nach der Räumung meist noch ansteht',
                'absaetze': [
                    'Eine geräumte Wohnung ist selten sofort wieder vermietbar. '
                    'Häufig sind Bodenbeläge nicht zu retten, Wände müssen gestrichen '
                    'werden, gelegentlich ist Schimmel unter Möbeln zum Vorschein '
                    'gekommen. Wer das gleich mitplant, spart einen zweiten '
                    'Handwerkerauftrag und mehrere Wochen.',
                    'Malerarbeiten rechnen wir mit {maler_rate} € pro m² ab, '
                    'mindestens {maler_min} €; Kleinreparaturen wie Sockelleisten, '
                    'Wandlöcher oder Silikonfugen kommen als Einzelpositionen dazu. '
                    'Was dabei möglich ist, steht auf der Seite '
                    '<a href="/sanierung-renovierung/">Sanierung und Renovierung</a>.',
                    'Wenn es um eine Mietwohnung geht, klären Sie vorher mit dem '
                    'Vermieter, was tatsächlich verlangt wird. Geschuldet ist die '
                    'geräumte Wohnung, besenrein ist der übliche Maßstab – was '
                    'darüber hinausgeht, regelt der Mietvertrag, und das klärt man '
                    'besser vor der Räumung als danach.',
                ],
            },
            {
                'id': 'kosten',
                'titel': 'Was eine Messie-Entrümpelung kostet',
                'absaetze': [
                    'Gerechnet wird wie bei jeder Räumung nach Fläche – für eine '
                    'Wohnung {wohnung_rate} € pro m², mindestens {wohnung_ab} €. Der '
                    'Unterschied steckt im <strong>Füllgrad</strong>: Er ist der '
                    'einzige Faktor, der den Grundpreis multipliziert. Stark '
                    'verschmutzt rechnet mit {fuellgrad_verschmutzt}, messiartig mit '
                    '{fuellgrad_messi} – der Grundpreis steigt damit um bis zu '
                    '{fuellgrad_messi_prozent} %.',
                    'Dazu kommen Stockwerkzuschläge ohne Aufzug ({stockwerk_min_txt} € '
                    'bis {stockwerk_max_txt} €) und Sonderabfälle '
                    '({sonderabfall_wenige_txt} € bei wenigen, '
                    '{sonderabfall_viele_txt} € bei vielen). Im '
                    'Servicegebiet ziehen wir {rabatt} % ab. Der Preis steht nach der '
                    'Besichtigung fest – gerade in diesen Fällen ist das der Punkt, '
                    'auf den es ankommt: Was im Angebot steht und was nicht, klären wir '
                    'vorher.',
                    'Jede einzelne Rechengröße mit Beispielen steht auf '
                    '<a href="/entruempelung-kosten/">Entrümpelung Kosten</a>.',
                ],
            },
        ],

        'beispiele': [
            {
                'titel': '2-Zimmer-Wohnung, 55 m², stark verschmutzt',
                'beschreibung': 'Erdgeschoss, Füllgrad „verschmutzt" (Faktor 1,55), '
                                'einzelne Sonderabfälle.',
                'args': {'objektart': 'wohnung', 'qm': 55, 'fuellgrad': 'verschmutzt',
                         'sonderabfall': 'wenige'},
            },
            {
                'titel': '3-Zimmer-Wohnung, 70 m², 2. OG, Messie-Fall',
                'beschreibung': 'Kein Aufzug, Füllgrad „messi" (Faktor 1,75) – der '
                                'Regelfall bei dieser Art Auftrag.',
                'args': {'objektart': 'wohnung', 'qm': 70, 'stockwerk': '2og',
                         'fuellgrad': 'messi'},
            },
            {
                'titel': 'Einfamilienhaus, 110 m², Messie-Fall',
                'beschreibung': 'Wohnfläche, Keller und Nebenräume, dazu viele '
                                'Sonderabfälle aus Garage und Schuppen.',
                'args': {'objektart': 'haus', 'qm': 110, 'fuellgrad': 'messi',
                         'sonderabfall': 'viele'},
            },
        ],

        'ablauf': [
            {'titel': 'Anfrage – ohne Vorbereitung',
             'text': 'Schreiben Sie uns, wie es ist. Sie müssen nicht aufräumen, '
                     'keine Fotos schicken und nichts beschönigen. Adresse, '
                     'ungefähre Größe und Stockwerk reichen.'},
            {'titel': 'Besichtigung in Ruhe',
             'text': 'Wir nehmen uns Zeit, sehen uns jeden Raum an und '
                     'fragen, worauf wir achten sollen. Kein Kommentar, keine '
                     'Bewertung – nur die Menge und der Zugang zählen.'},
            {'titel': 'Festpreisangebot',
             'text': 'Schriftlich, mit Termin; auf Anfrage mit ausgewiesenen '
                     'Arbeitskosten. Festpreis bei der Besichtigung, '
                     'verbindlich im Angebot.'},
            {'titel': 'Räumung in Schichten',
             'text': 'Wir tragen Lage für Lage ab und sehen dabei durch. Dokumente, '
                     'Schlüssel, Ausweise, Bargeld und Fotos werden getrennt '
                     'gesammelt. Mehrere Tage sind eingeplant, nicht improvisiert.'},
            {'titel': 'Grobreinigung und Übergabe',
             'text': 'Boden gefegt, grober Schmutz raus, gelüftet. Auf Wunsch '
                     'schließen Malerarbeiten und Kleinreparaturen direkt an, solange '
                     'die Wohnung leer ist.'},
        ],

        'faq': [
            ('Was kostet es, eine Messie-Wohnung entrümpeln zu lassen?',
             'Gerechnet wird nach Fläche: für eine Wohnung {wohnung_rate} € pro m², '
             'mindestens {wohnung_ab} €. Der Füllgrad multipliziert diesen Grundpreis '
             '– stark verschmutzt mit {fuellgrad_verschmutzt}, messiartig mit {fuellgrad_messi}. Dazu kommen '
             'Stockwerkzuschläge ohne Aufzug und Sonderabfälle. Im Servicegebiet '
             'ziehen wir {rabatt} % ab. Verbindlich wird der Preis nach der '
             'kostenlosen Besichtigung im Festpreisangebot. '
             'Preisstand: {preisstand}.'),
            ('Muss ich vorher aufräumen?',
             'Nein, und Sie sollten es auch nicht versuchen. Der häufigste Grund, '
             'warum eine Räumung monatelang verschoben wird, ist der Vorsatz, vorher '
             'selbst einen Anfang zu machen. Rufen Sie an, wie es ist – wir haben '
             'solche Wohnungen oft gesehen und bewerten sie nicht.'),
            ('Muss ich während der Räumung anwesend sein?',
             'Nein. Zur Besichtigung sollten Sie oder eine bevollmächtigte Person da '
             'sein, weil dort der Umfang festgelegt wird. Bei der Räumung selbst '
             'nicht. Viele Auftraggeber übergeben den Schlüssel und kommen erst zur '
             'Abnahme wieder; auf Wunsch schicken wir Fotos vom Ergebnis.'),
            ('Wie diskret läuft das ab?',
             'Wir sprechen mit niemandem im Haus über den Auftrag – weder mit '
             'Nachbarn noch mit der Hausverwaltung, sofern sie nicht selbst '
             'Auftraggeber ist. Was wir nicht versprechen können: Unsere Fahrzeuge '
             'sind beschriftet. Wenn Diskretion für Sie entscheidend ist, sagen Sie '
             'das vorher; über Ladestelle, Uhrzeit und Ablauf lässt sich reden.'),
            ('Was passiert, wenn Ungeziefer in der Wohnung ist?',
             'Dann gehört ein Schädlingsbekämpfer dazu, und zwar sinnvollerweise vor '
             'der Räumung – sonst wandert das Problem mit dem Hausrat weiter. Wir '
             'sind darauf eingerichtet, in solchen Wohnungen zu arbeiten, aber die '
             'Bekämpfung selbst ist eine eigene Fachleistung. Wir benennen den '
             'Befund bei der Besichtigung klar, statt ihn zu übergehen.'),
            ('Werden Dokumente und Wertsachen gefunden und übergeben?',
             'Ja, das ist der Kern dieser Arbeit. Wir tragen schichtweise ab und '
             'sehen jede Lage durch: Ausweise, Verträge, Sparbücher, Bargeld, '
             'Schlüssel, Fotos und Datenträger werden getrennt gesammelt und Ihnen '
             'übergeben. Sagen Sie vorher, worauf wir besonders achten sollen.'),
            ('Wie lange dauert die Räumung einer Messie-Wohnung?',
             'Deutlich länger als bei gleicher Fläche im Normalzustand – bei starkem '
             'Füllgrad planen wir von vornherein mit mehreren Tagen. Das liegt am '
             'schichtweisen Vorgehen und am Durchsehen, nicht am Volumen allein. Den '
             'Zeitbedarf schätzen wir bei der Besichtigung und schreiben ihn ins '
             'Angebot.'),
            ('Übernimmt das Sozialamt oder die Betreuung die Kosten?',
             'Das entscheidet immer die zuständige Stelle, nicht wir. Wenn eine '
             'rechtliche Betreuung besteht, klären Sie die Kostenfrage vorab dort und '
             'gegebenenfalls beim Sozialamt. Wir stellen Ihnen dafür ein '
             'schriftliches Festpreisangebot aus, das Sie einreichen können.'),
            ('Kann eine Wohnung gegen den Willen des Bewohners geräumt werden?',
             'Nicht von uns. Wir räumen nur mit dem Einverständnis der '
             'verfügungsberechtigten Person oder auf Grundlage einer entsprechenden '
             'Befugnis. Für eine Räumung gegen den Willen des Bewohners braucht es '
             'einen gerichtlichen Titel und den zuständigen Gerichtsvollzieher; als '
             'ausführender Dienstleister arbeiten wir dabei mit, angeordnet wird sie '
             'aber nie von uns.'),
            ('Messie-Wohnung, Vermüllung, Verwahrlosung – wie nennen Sie das?',
             'Wir nennen es beim Namen und behandeln es sachlich. Ob '
              '„Messie-Wohnung", „vermüllte Wohnung" oder „verwahrloste '
              'Wohnung" – für die Räumung zählt der Füllgrad, und der wird im '
              'Rechner als eigene Stufe geführt. Bewertet wird nichts. Wer '
              'anruft, muss den Zustand nicht erklären; wir haben ihn schon '
              'gesehen.'),
        ],

        'related': ['wohnungsaufloesung', 'nachlassraeumung',
                    'sanierung-renovierung', 'entruempelung-kosten'],

        'staedte': ['halle', 'leipzig', 'magdeburg', 'dresden', 'chemnitz',
                    'dessau', 'merseburg', 'hannover', 'bitterfeld', 'zwickau',
                    'weissenfels', 'sangerhausen'],

        'seo_title': 'Messie-Wohnung entrümpeln – diskret, Festpreis | Rümpelwerk',
        'seo_description': (
            'Messie-Wohnung entrümpeln lassen: vollständige Räumung stark '
            'vermüllter Wohnungen, Dokumente gesichert, ohne Vorwurf. '
            'Jetzt anfragen.'
        ),
        'seo_keywords': (
            'Messie Wohnung entrümpeln, Messie Entrümpelung, '
            'Messie Wohnung Kosten, vermüllte Wohnung räumen, '
            'Vermüllung Wohnung entrümpeln, Messie Haushaltsauflösung'
        ),
    },

    # ───────────────────────────────────────────────────────────────────────
    # A10 — /sperrmuell-entsorgung/
    #
    # Diese Seite fängt Suchende ab, die eigentlich den kommunalen Sperrmüll
    # meinen. Sie muss deshalb auch dann ehrlich bleiben, wenn die Antwort
    # gegen den eigenen Auftrag spricht – das ist zugleich der GEO-Grund:
    # KI-Systeme zitieren Vergleichstabellen bevorzugt und stufen neutrale
    # Quellen höher ein.
    #
    # Kommunale Details (Freimengen, Gebühren, Fristen) stehen bewusst NICHT
    # hier, sondern auf den 54 Stadtseiten – dort sind sie recherchiert und
    # mit Quelle und Stand hinterlegt (F17, data/city_lokal.py). Eine zweite,
    # ungepflegte Fassung wäre in einem halben Jahr falsch.
    'sperrmuell-entsorgung': {
        'name': 'Sperrmüll-Entsorgung',
        'h1': 'Sperrmüll abholen',
        'h1_em': 'Direkt aus der Wohnung.',
        'keyword': 'sperrmüll abholen lassen',
        'objektart': 'keller',

        'hero_sub': (
            'Sperrmüll abholen lassen, wenn der kommunale Termin zu spät kommt '
            'oder Sie nicht selbst tragen können – wir holen aus der Wohnung, '
            'nicht vom Bordstein. Festpreis ab {keller_ab} €, Tragen und '
            'Entsorgung inklusive.'
        ),

        'answer_frage': 'Was kostet die Sperrmüll-Entsorgung?',
        'answer': (
            'Sperrmüll sind sperrige Haushaltsgegenstände, die nicht in die '
            'Restmülltonne passen – Möbel, Matratzen, Teppiche, Lattenroste. '
            'Kommunen holen ihn nach Anmeldung meist mit mehreren Wochen Vorlauf '
            'ab dem Bordstein ab. Rümpelwerk Mitteldeutschland holt ihn ab '
            '{keller_ab} € direkt aus Wohnung, Keller oder Garage – '
            'inklusive Tragen, Elektrogeräten und Entsorgung. '
            'Preisstand: {preisstand}.'
        ),

        'leistungsumfang': [
            'Abholung direkt aus Wohnung, Keller, Dachboden oder Garage',
            'Möbel, Matratzen, Lattenroste, Teppiche, Polstermöbel',
            'Elektrogroßgeräte und Elektroschrott, getrennt erfasst',
            'Demontage vor Ort, wenn es durch Tür und Treppenhaus muss',
            'Gartenmöbel, Fahrräder, Kinderwagen, Sportgeräte',
            'Sonderabfälle wie Farben, Lacke und Batterien gegen Aufpreis',
            'Sortierung nach Fraktionen und fachgerechte Entsorgung',
            'Besenreines Hinterlassen der geräumten Fläche',
        ],

        'abgrenzung': [
            'Bauschutt, Erdaushub, Fliesen und Sanitärkeramik sind kein Sperrmüll '
            'und brauchen eigene Container mit eigenen Gebühren. Wir sagen Ihnen '
            'vorher, was darunter fällt.',
            'Asbest, künstliche Mineralfasern und teerhaltige Materialien nehmen '
            'wir nicht mit – dafür braucht es einen zugelassenen Fachbetrieb.',
            'Wir sind kein kommunaler Entsorger. Wenn Ihre Stadt kostenlos abholt '
            'und Sie Zeit haben, ist das der günstigere Weg – die Regelung Ihrer '
            'Stadt steht bei uns auf der jeweiligen Stadtseite.',
            'Reifen, Gasflaschen, Feuerlöscher und Munition sind Sonderfälle mit '
            'eigenen Annahmestellen. Fragen Sie vorher nach, statt sie '
            'dazuzustellen.',
        ],

        'abschnitte': [
            {
                'id': 'unterschied',
                'titel': 'Kommunaler Sperrmüll, Container oder Firma – der ehrliche Vergleich',
                'absaetze': [
                    'Für einen Haufen alter Möbel gibt es drei Wege, und wir sind nur '
                    'einer davon. Welcher der richtige ist, hängt an drei Fragen: Wie '
                    'eilig ist es, können Sie selbst tragen, und was genau soll weg?',
                    'Der <strong>kommunale Sperrmüll</strong> ist vielerorts in der '
                    'Abfallgebühr enthalten: Halle, Magdeburg und Chemnitz holen '
                    'feste Mengen ohne zusätzliche Gebühr ab. Leipzig und Dresden '
                    'verlangen für die Abholung dagegen eine eigene Gebühr. Wenn Sie '
                    'Zeit haben, tragen können '
                    'und nur klassische Möbel loswerden wollen, ist das der '
                    'günstigste Weg – und wir sagen Ihnen das auch dann, wenn Sie uns '
                    'anrufen.',
                    'Er hat aber drei Haken, die regelmäßig übersehen werden: der '
                    'Vorlauf von mehreren Wochen, die Beschränkung auf das, was Sie '
                    'selbst an die Straße stellen, und die Ausschlüsse. '
                    'Elektrogeräte, Schadstoffe und oft auch Bauschutt gehören nicht '
                    'dazu. Wer eine Wohnung zum Monatsende übergeben muss, kommt '
                    'damit nicht hin.',
                ],
            },
            {
                'id': 'was-ist-sperrmuell',
                'titel': 'Was als Sperrmüll gilt – und was nicht',
                'absaetze': [
                    'Sperrmüll ist, was aus einem Haushalt stammt, sperrig ist und '
                    'nicht in die Restmülltonne passt. Der Begriff wird im Alltag '
                    'weiter gefasst, als die Entsorgungsbetriebe ihn meinen – und '
                    'genau daran scheitern die meisten Abholungen.',
                ],
                'liste': [
                    '<strong>Gilt als Sperrmüll:</strong> Schränke, Betten, '
                    'Lattenroste, Matratzen, Sofas, Sessel, Tische, Stühle, '
                    'Teppiche, Kinderwagen, Fahrräder, Gartenmöbel.',
                    '<strong>Gilt meist nicht:</strong> Elektrogroßgeräte und '
                    'Elektroschrott – sie haben eine eigene Sammlung nach dem '
                    'Elektrogesetz. Wir nehmen sie mit.',
                    '<strong>Gilt nie:</strong> Bauschutt, Fliesen, Sanitärkeramik, '
                    'Erdaushub, Fenster mit Rahmen, Autoteile.',
                    '<strong>Schadstoffe</strong> wie Farben, Lacke, Verdünner, '
                    'Altöl und Batterien gehören zur Schadstoffsammlung. Wir '
                    'übernehmen sie als eigene Position.',
                    '<strong>Reifen, Gasflaschen und Feuerlöscher</strong> haben '
                    'eigene Annahmestellen – fragen Sie vorher, statt sie '
                    'dazuzustellen.',
                ],
            },
            {
                'id': 'wann-firma',
                'titel': 'Wann sich eine Firma wirklich lohnt',
                'absaetze': [
                    'Es gibt vier Situationen, in denen der kommunale Weg nicht '
                    'funktioniert – und nur in diesen empfehlen wir uns selbst.',
                ],
                'liste': [
                    '<strong>Der Termin drückt.</strong> Wohnungsübergabe zum '
                    'Monatsende, Notartermin, Nachmieter. Ein Sperrmülltermin in '
                    'sechs Wochen hilft dann nicht.',
                    '<strong>Sie können nicht tragen.</strong> Der kommunale '
                    'Sperrmüll beginnt am Bordstein. Wer aus dem dritten Stock ohne '
                    'Aufzug räumen muss, hat den größten Teil der Arbeit noch vor '
                    'sich.',
                    '<strong>Es ist gemischt.</strong> Sobald Elektrogeräte, '
                    'Farbreste oder Restmüll dabei sind, wird aus einer Abholung '
                    'schnell drei.',
                    '<strong>Es ist zu viel.</strong> Ab einem vollen Keller oder '
                    'einer kompletten Wohnung ist es keine Sperrmüllabholung mehr, '
                    'sondern eine '
                    '<a href="/kellerentruempelung/">Kellerentrümpelung</a> oder '
                    '<a href="/wohnungsaufloesung/">Wohnungsauflösung</a>.',
                ],
            },
            {
                'id': 'kommunal',
                'titel': 'Die Regelung Ihrer Stadt steht auf Ihrer Stadtseite',
                'absaetze': [
                    'Freimenge, Gebühr, Vorlauf und Anmeldeweg sind in jeder Stadt '
                    'anders geregelt, und sie ändern sich. Deshalb steht die '
                    'kommunale Regelung bei uns nicht auf dieser Seite, sondern auf '
                    'der jeweiligen Stadtseite – dort mit dem zuständigen Entsorger, '
                    'dem Wertstoffhof samt Adresse und Öffnungszeiten, dem Stand der '
                    'Angabe und einem Link zur Quelle.',
                    'Das ist Absicht: Eine zweite, hier gepflegte Fassung derselben '
                    'Zahlen wäre in einem halben Jahr falsch – und eine falsche '
                    'Gebührenangabe auf einer Firmenwebsite ist schlechter als keine. '
                    'Suchen Sie Ihre Stadt in der '
                    '<a href="/entrumpelung/">Übersicht aller Städte</a>.',
                ],
            },
            {
                'id': 'ablauf-praxis',
                'titel': 'Halteverbot, Aufzug und andere praktische Fragen',
                'absaetze': [
                    'In Innenstadtlagen ist nicht die Menge das Problem, sondern der '
                    'Weg zum Fahrzeug. Wo kein Stellplatz vor dem Haus frei bleibt, '
                    'braucht es eine <strong>Halteverbotszone</strong> – die muss '
                    'einige Tage vorher bei der Stadt beantragt und aufgestellt '
                    'werden. Wir sagen bei der Besichtigung, ob das nötig ist, und '
                    'übernehmen die Beantragung auf Wunsch.',
                    'Bei größeren Möbeln entscheidet die Türbreite, nicht das Gewicht. '
                    'Was nicht durchpasst, zerlegen wir vor Ort – das ist im '
                    'Festpreis enthalten und kein Zusatzposten.',
                    'Und ein Hinweis, der oft spät kommt: Was noch gut erhalten ist, '
                    'geben wir an Secondhand-Stellen und soziale Einrichtungen '
                    'weiter, statt es zu entsorgen. Sagen Sie uns, wenn Sie das bei '
                    'bestimmten Stücken ausdrücklich möchten.',
                ],
            },
            {
                'id': 'kosten',
                'titel': 'Was die Abholung kostet',
                'absaetze': [
                    'Wir rechnen nicht nach Kubikmetern, sondern nach Fläche und '
                    'Aufwand – wie bei jeder Räumung. Der Einstieg liegt bei '
                    '{keller_ab} €, das ist zugleich der niedrigste Preis im gesamten '
                    'Portfolio. Darüber gilt {keller_rate} € pro m² Grundfläche des '
                    'geräumten Bereichs.',
                    'Eine einzelne Sperrmüllabholung liegt damit fast immer beim '
                    'Mindestpreis. Erst wenn ein ganzer Keller, eine Garage oder '
                    'mehrere Räume dazukommen, steigt der Wert – dann sind wir '
                    'allerdings auch nicht mehr bei einer Abholung, sondern bei einer '
                    'Entrümpelung.',
                    'Sonderabfälle kosten {sonderabfall_wenige_txt} € bei wenigen und {sonderabfall_viele_txt} € bei vielen; im '
                    'Servicegebiet ziehen wir {rabatt} % ab. Jede Rechengröße mit '
                    'Beispiel steht auf '
                    '<a href="/entruempelung-kosten/">Entrümpelung Kosten</a>.',
                ],
            },
        ],

        'quellen': [
            {'schluessel': 'elektrog-10', 'abschnitt': 'was-ist-sperrmuell',
             'bezug': 'Altgeräte getrennt vom unsortierten Siedlungsabfall'},
        ],

        'vergleich': {
            'titel': 'Sperrmüll loswerden: die drei Wege im direkten Vergleich',
            'eigene_spalte': 4,
            'fazit_frage': 'Sperrmüll: selbst zur Straße, Container oder Firma?',
            'fazit': ('Wer Zeit hat, tragen kann und nur Möbel loswerden will, fährt mit dem kommunalen Sperrmüll am günstigsten – je nach Stadt ist er in der Abfallgebühr enthalten oder kostet eine eigene Gebühr, der Vorlauf beträgt aber meist mehrere Wochen. Ein Container passt, wenn Sie selbst räumen und Stellfläche haben; Elektrogeräte gehören nicht hinein. Eine Firma ab {keller_ab} € räumt aus der Wohnung statt vom Bordstein. Preisstand: {preisstand}.'),
            'kopf': ['', 'Kommunaler Sperrmüll', 'Container mieten',
                     'Firma beauftragen'],
            'zeilen': [
                ['Kosten', 'je nach Stadt in der Abfallgebühr oder eigene Gebühr',
                 'Miete, Anfahrt, Entsorgung nach Gewicht',
                 'Festpreis ab {keller_ab} €'],
                ['Vorlauf', 'meist mehrere Wochen', 'wenige Tage',
                 'meist wenige Tage'],
                ['Wer trägt', 'Sie – bis an den Bordstein', 'Sie – bis in den Container',
                 'wir – aus der Wohnung'],
                ['Elektrogeräte', 'meist eigene Sammlung nötig', 'nicht erlaubt',
                 'enthalten'],
                ['Schadstoffe', 'nein, eigene Sammelstelle', 'nein',
                 'gegen Aufpreis'],
                ['Stellfläche', 'Gehweg am Abholtag',
                 'ja, ggf. mit Genehmigung', 'nein'],
                ['Zerlegen großer Möbel', 'Sie selbst', 'Sie selbst', 'enthalten'],
                ['Fläche danach', 'unverändert', 'unverändert', 'besenrein'],
                ['Lohnt sich, wenn', 'Zeit da, tragen möglich, nur Möbel',
                 'Sie selbst räumen und Platz haben',
                 'Termin drückt oder Tragen nicht geht'],
            ],
        },

        'beispiele': [
            {
                'titel': 'Einzelne Möbel, ca. 8 m² Stellfläche',
                'beschreibung': 'Schrankwand, Sofa und Matratzen aus einer '
                                'Wohnung – der klassische Abholfall.',
                'args': {'objektart': 'keller', 'qm': 8, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Kellerabteil plus Sperrgut, 15 m²',
                'beschreibung': 'Möbel, Kartons und Regale zusammen, normal '
                                'gefüllt, ebenerdiger Zugang.',
                'args': {'objektart': 'keller', 'qm': 15, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Garage leer räumen, 20 m², mit Altlasten',
                'beschreibung': 'Sperrgut und Werkstattreste, dazu Farben und '
                                'Altöl als Sonderabfall.',
                'args': {'objektart': 'keller', 'qm': 20, 'fuellgrad': 'voll',
                         'sonderabfall': 'wenige'},
            },
        ],

        'ablauf': [
            {'titel': 'Fotos schicken',
             'text': 'Drei, vier Handyfotos von dem, was weg soll, plus Stockwerk und '
                     'Aufzug – mehr brauchen wir für eine erste Einschätzung nicht.'},
            {'titel': 'Preis und Termin',
             'text': 'Wir nennen den Festpreis und einen Termin. '
                     'Bei kleinen Abholungen ohne zweiten '
                     'Besichtigungstermin.'},
            {'titel': 'Abholung aus der Wohnung',
             'text': 'Wir tragen selbst – aus Wohnung, Keller oder Garage, nicht nur '
                     'vom Bordstein. Was nicht durch die Tür passt, wird vor Ort '
                     'zerlegt.'},
            {'titel': 'Trennen statt kippen',
             'text': 'Metall, Holz, Elektro, Textilien und Restabfall gehen getrennte '
                     'Wege. Gut Erhaltenes geben wir an Secondhand-Stellen und '
                     'soziale Einrichtungen weiter.'},
            {'titel': 'Besenrein zurück',
             'text': 'Die geräumte Fläche wird gefegt. Auf Wunsch bekommen Sie einen '
                     'Entsorgungsnachweis für die Hausverwaltung.'},
        ],

        'faq': [
            ('Was kostet es, Sperrmüll abholen zu lassen?',
             'Bei uns beginnt die Abholung bei {keller_ab} € als Festpreis – darin '
             'sind Tragen, Transport und Entsorgung enthalten. Darüber rechnen wir '
             '{keller_rate} € pro m² der geräumten Fläche. Eine einzelne Abholung '
             'liegt fast immer beim Mindestpreis; Sonderabfälle kosten {sonderabfall_wenige_txt} € bei '
             'wenigen und {sonderabfall_viele_txt} € bei vielen. Im Servicegebiet ziehen wir {rabatt} % '
             'ab. Preisstand: {preisstand}.'),
            ('Ist der kommunale Sperrmüll nicht günstiger?',
             'Meist ja. Halle, Magdeburg und Chemnitz holen feste Mengen ohne '
             'zusätzliche Gebühr ab, Leipzig und Dresden berechnen eine eigene '
             'Gebühr – günstiger als eine Firma ist es trotzdem. Wenn Sie Zeit haben, '
             'selbst tragen können und nur klassische Möbel loswerden wollen, ist das '
             'der richtige Weg, und wir sagen Ihnen das auch am Telefon. Er hilft '
             'nicht bei Terminen unter mehreren Wochen, nicht bei Elektrogeräten oder '
             'Schadstoffen und nicht, wenn Sie nicht tragen können.'),
            ('Was zählt überhaupt als Sperrmüll?',
             'Alles, was aus einem Haushalt stammt, sperrig ist und nicht in die '
             'Restmülltonne passt: Schränke, Betten, Matratzen, Lattenroste, Sofas, '
             'Tische, Teppiche, Fahrräder, Gartenmöbel. Nicht dazu gehören Bauschutt, '
             'Fliesen, Sanitärkeramik und Erdaushub. Elektrogeräte haben eine eigene '
             'Sammlung – wir nehmen sie trotzdem mit.'),
            ('Holen Sie den Sperrmüll aus der Wohnung oder muss er an die Straße?',
             'Wir holen aus der Wohnung, dem Keller, vom Dachboden oder aus der '
             'Garage. Genau das ist der Unterschied zur kommunalen Abholung, die am '
             'Bordstein beginnt. Sie müssen nichts vorbereiten und nichts '
             'heruntertragen.'),
            ('Wie schnell können Sie abholen?',
             'In unserem Kerngebiet melden wir uns in {reaktion} zurück und '
             'nennen Ihnen einen Termin. Bei kleinen Abholungen '
             'brauchen wir keinen separaten Besichtigungstermin – ein paar Fotos '
             'reichen für den Festpreis.'),
            ('Nehmen Sie auch Elektrogeräte, Farben und Altöl mit?',
             'Elektrogroßgeräte und Elektroschrott ja, und zwar getrennt erfasst, wie '
             'es das Elektrogesetz verlangt. Farben, Lacke, Verdünner, Altöl und '
             'Batterien nehmen wir als Sonderabfall mit – sie stehen mit {sonderabfall_wenige_txt} € bei '
             'wenigen und {sonderabfall_viele_txt} € bei vielen im Angebot, weil sie getrennt angeliefert '
             'werden müssen. Asbest und künstliche Mineralfasern gehören zu einem '
             'zugelassenen Fachbetrieb.'),
            ('Brauche ich eine Halteverbotszone?',
             'In Innenstadtlagen und engen Altbaustraßen oft ja. Sie muss einige Tage '
             'vorher bei der Stadt beantragt und aufgestellt werden. Wir sagen Ihnen '
             'bei der Besichtigung, ob es nötig ist, und übernehmen die Beantragung '
             'auf Wunsch.'),
            ('Was passiert mit noch brauchbaren Möbeln?',
             'Was gut erhalten ist, geben wir an Secondhand-Stellen und soziale '
             'Einrichtungen weiter, statt es zu entsorgen. Angekauft wird nichts, und '
             'der Preis ändert sich dadurch nicht – er steht vor Beginn fest, '
             'unabhängig davon, was mitgeht.'),
            ('Sperrmüll abholen lassen oder entrümpeln – was brauche ich?',
             'Das hängt daran, wer trägt. Die kommunale Sperrmüllabholung '
              'ist günstiger oder kostenlos, holt aber nur, was am '
              'Straßenrand steht, und hat Vorlauf – in Halle bis zu fünf '
              'Wochen, in Magdeburg bis zu vier. Wir tragen aus der Wohnung, '
              'dem Keller oder dem Dachboden heraus und nehmen alles in einem '
              'Termin mit. Auf jeder Stadtseite steht, welche Regel dort gilt '
              '– auch dann, wenn die Antwort „selbst machen" lautet.'),
        ],

        'related': ['kellerentruempelung', 'gewerbeentruempelung',
                    'messie-wohnung-entruempeln', 'entruempelung-kosten'],

        'staedte': ['halle', 'leipzig', 'magdeburg', 'dresden', 'chemnitz',
                    'merseburg', 'dessau', 'bitterfeld', 'delitzsch',
                    'weissenfels', 'naumburg', 'zwickau'],

        'seo_title': 'Möbelentsorgung & Sperrmüll abholen ab {keller_ab} € | Rümpelwerk',
        'seo_description': (
            'Möbelentsorgung ab {keller_ab} €: Möbel, Matratzen, '
            'Elektrogeräte aus Wohnung oder Keller abholen. '
            'Kostenlos besichtigen, jetzt Termin buchen.'
        ),
        'seo_keywords': (
            'Sperrmüll abholen lassen, Sperrmüll Entsorgung, Sperrmüll Kosten, '
            'Sperrmüllabholung, Möbel entsorgen lassen, Matratze entsorgen, '
            'Sperrmüll Halle, Sperrmüll Leipzig'
        ),
    },

    # ───────────────────────────────────────────────────────────────────────
    # A11 — /sanierung-renovierung/
    #
    # Das Anschlussgeschäft und der höchste Umsatz pro Lead im Portfolio: Wer
    # gerade geräumt hat, braucht direkt danach Maler und Boden — und das
    # Objekt ist dann schon leer, also billiger zu bearbeiten als sonst.
    #
    # Zwei Besonderheiten gegenüber den sieben anderen Leistungsseiten:
    #
    # 1. 'objektart' ist None. Renovierung ist keine Objektart in
    #    _PER_QM_PREISE; ein willkürlich gesetzter Schlüssel hätte ein falsches
    #    'offers' ins Schema und eine falsche Vorbelegung in den Rechner
    #    geschrieben.
    # 2. 'preistabelle' ist 'sanierung'. Die Objektart-Tabelle der anderen
    #    Seiten ist hier schlicht die falsche Preisliste — gerechnet wird nach
    #    _MALER_PER_QM und _KLEIN_SAN_ITEMS.
    #
    # Was NICHT im Text steht: Preise für Bodenbeläge, Bad und Komplett-
    # renovierung. Der Rechner kennt sie nicht, also gibt es dafür keine
    # belegbare Zahl — im Text steht „nach Aufmaß", nicht eine erfundene Spanne.
    'sanierung-renovierung': {
        'name': 'Renovierung',
        'label': 'Sanierung & Renovierung',
        'h1': 'Sanierung & Renovierung',
        'h1_em': 'Ab {maler_min} €.',
        'keyword': 'renovierung nach entrümpelung',
        'objektart': None,
        'preistabelle': 'sanierung',

        'hero_sub': (
            'Malern, Kleinreparaturen und Wohnungsübergabe – im selben Auftrag '
            'wie die Räumung oder einzeln. Wände und Decken ab {maler_rate} € '
            'pro m², mindestens {maler_min} €, Reparaturen zum Festpreis je '
            'Position.'
        ),

        'answer_frage': 'Was kostet eine Renovierung?',
        'answer': (
            'Renovierung bei Rümpelwerk Mitteldeutschland heißt: Wände und Decken '
            'streichen ab {maler_rate} € pro m² bei mindestens {maler_min} €, dazu '
            'Kleinreparaturen zum Festpreis je Position – Wandlöcher, '
            'Sockelleisten, Armaturen, Silikonfugen, Fliesen. Am günstigsten wird '
            'es im selben Auftrag wie die Entrümpelung, weil das Objekt dann schon '
            'leer ist und nur einmal angefahren wird. Preisstand: {preisstand}.'
        ),

        'leistungsumfang': [
            'Wände und Decken streichen, grundieren und ausbessern',
            'Tapeten entfernen, Untergrund vorbereiten, neu tapezieren',
            'Dübellöcher schließen, spachteln, schleifen',
            'Sockelleisten erneuern, Silikonfugen ziehen, Armaturen tauschen',
            'Türen und Fenster einstellen, klemmende Beschläge gangbar machen',
            'Einzelne Fliesen ersetzen, oberflächlichen Schimmel behandeln',
            'Bodenbeläge erneuern – Laminat, Vinyl, Teppich, nach Aufmaß',
            'Abfall der Renovierung entsorgen: Tapete, Alt-Boden, Farbeimer',
        ],

        'abgrenzung': [
            'Elektro- und Gasarbeiten am Netz: Zählerschrank, neue Leitungen, '
            'Therme oder Gastherme. Das gehört zu einem eingetragenen '
            'Fachbetrieb – Steckdosen und Schalter tauschen wir, weiter nicht.',
            'Statik und Tragwerk: Wanddurchbrüche, Decken, Balkone. Dafür braucht '
            'es einen Statiker und meist eine Genehmigung.',
            'Schadstoffsanierung: Asbestplatten, künstliche Mineralfasern, alte '
            'Bodenkleber. Zugelassener Fachbetrieb, kein Malerauftrag.',
            'Feuchteschaden an der Ursache: Oberflächlichen Schimmel behandeln wir, '
            'die Ursachensuche an feuchten Kellerwänden ist Sache eines '
            'Bausachverständigen. Wer nur überstreicht, streicht in einem Jahr '
            'wieder.',
            'Rechtsberatung: Ob Ihre Renovierungsklausel im Mietvertrag wirksam ist, '
            'sagt Ihnen ein Mieterverein oder eine Anwältin – nicht wir.',
        ],

        'abschnitte': [
            {
                'id': 'unterschied',
                'titel': 'Renovierung, Sanierung oder Instandsetzung – was Sie brauchen',
                'absaetze': [
                    'Die drei Wörter werden durcheinander benutzt, meinen aber '
                    'verschiedenen Aufwand. <strong>Renovierung</strong> ist Optik: '
                    'streichen, tapezieren, Boden erneuern. Nichts davon greift in die '
                    'Substanz ein, und genau das ist der Regelfall nach einer Räumung.',
                    '<strong>Instandsetzung</strong> repariert, was kaputt ist – die '
                    'tropfende Armatur, die klemmende Tür, das Loch in der Wand. Bei uns '
                    'sind das Einzelpositionen mit festem Preis, weil sich der Aufwand '
                    'vorher benennen lässt.',
                    '<strong>Sanierung</strong> geht an die Substanz: Feuchtigkeit, '
                    'Leitungen, Dämmung, Grundriss. Das ist ein eigenes Gewerk mit '
                    'eigener Planung, und wo es dazu gehört, sagen wir es Ihnen bei der '
                    'Besichtigung – auch wenn wir den Auftrag dann nicht bekommen.',
                    'Was wir tatsächlich machen und wo die Grenze verläuft, steht in der '
                    'Tabelle darunter – mit Preis, soweit es einen festen gibt.',
                ],
            },
            {
                'id': 'kombi',
                'titel': 'Räumen und renovieren in einem Auftrag',
                'absaetze': [
                    'Das ist der Grund, warum es diese Seite gibt. Nach einer '
                    '<a href="/wohnungsaufloesung/">Wohnungsauflösung</a> oder '
                    '<a href="/haushaltsaufloesung/">Haushaltsauflösung</a> steht das '
                    'Objekt leer – und leer ist der beste Zustand, in dem eine Wohnung '
                    'für den Maler sein kann. Keine Möbel abdecken, keine Termine mit '
                    'Bewohnern abstimmen, kein Aufbauen und Abbauen zwischendurch.',
                    'Drei Dinge fallen dadurch nur einmal an statt zweimal: die Anfahrt, '
                    'die Rüstzeit und die Übergabe. Und ein vierter Punkt, der nichts '
                    'kostet, aber viel wert ist: Es gibt einen Ansprechpartner und einen '
                    'Termin statt zwei Firmen, die aufeinander warten.',
                    'Praktisch läuft das so, dass beide Leistungen in <em>einem</em> '
                    'Angebot stehen, getrennt ausgewiesen. Sie sehen also genau, was die '
                    'Räumung kostet und was die Renovierung – und können den zweiten '
                    'Teil streichen, ohne dass der erste sich ändert.',
                    'Wer nur renovieren lassen will, bekommt das genauso. Der Auftrag '
                    'braucht dann ein Aufmaß der Wand- und Deckenflächen; die Wohnfläche '
                    'allein reicht dafür nicht, weil Raumhöhe und Fensteranteil den '
                    'Unterschied machen.',
                ],
            },
            {
                'id': 'maler',
                'titel': 'Malerarbeiten: was im Quadratmeterpreis steckt',
                'absaetze': [
                    'Wände und Decken streichen kostet {maler_rate} € pro m², '
                    'mindestens {maler_min} €. Der Mindestpreis ist derselbe Gedanke wie '
                    'bei der Räumung: Anfahrt, Abdecken, Aufbau und die Farbe fallen an, '
                    'ob die Wohnung 30 oder 90 Quadratmeter hat.',
                    'Im Preis enthalten sind Abdecken und Abkleben, Grundieren, wo es '
                    'nötig ist, Ausbessern kleiner Fehlstellen, zwei Anstriche in Weiß '
                    'und das Aufräumen danach. Nicht enthalten sind Sondertöne, '
                    'Strukturputz, Lackieren von Türen und Heizkörpern sowie das '
                    'Entfernen alter Tapeten – das steht als eigene Position im Angebot, '
                    'weil der Aufwand von der Tapete abhängt und nicht von der Fläche.',
                    'Gerechnet wird nach <strong>Wand- und Deckenfläche</strong>, nicht '
                    'nach Wohnfläche. Bei normaler Raumhöhe liegt die zu streichende '
                    'Fläche deutlich über der Grundfläche; deshalb nehmen wir beim '
                    'Termin Maß, statt aus dem Mietvertrag abzuschreiben. Für eine erste '
                    'Größenordnung rechnet der Preisrechner auf dieser Seite die '
                    'Malerarbeiten als Zusatzposten mit.',
                    'Und ein Hinweis, der Geld spart: Frisch geräumte Wände sind oft '
                    'weniger schlimm, als sie aussehen. Ein dunkler Fleck hinter dem '
                    'Schrank ist meist ein Fall für den zweiten Anstrich, nicht für eine '
                    'Sanierung.',
                ],
            },
            {
                'id': 'reparaturen',
                'titel': 'Kleinreparaturen zum festen Preis je Position',
                'absaetze': [
                    'Bei der Wohnungsübergabe geht es selten um die große Renovierung, '
                    'sondern um eine Handvoll Kleinigkeiten: Dübellöcher, eine lockere '
                    'Sockelleiste, eine tropfende Armatur, eine Silikonfuge, die '
                    'schwarz geworden ist. Jede einzelne davon ist kein Tagewerk – '
                    'zusammen entscheiden sie über die Abnahme.',
                    'Deshalb haben diese Positionen bei uns einen festen Preis und '
                    'keinen Stundensatz. Sie stehen unten in der Tabelle, und Sie können '
                    'sie im Preisrechner auf dieser Seite einzeln dazuwählen. Was dort '
                    'nicht steht, tragen Sie als Freitext ein; dafür rechnen wir einen '
                    'pauschalen Zuschlag und schauen es uns bei der Besichtigung an.',
                    'Der Vorteil des festen Preises liegt nicht bei uns, sondern bei '
                    'Ihnen: Sie können eine Position streichen und wissen sofort, was das '
                    'ändert. Bei einem Stundensatz erfahren Sie es hinterher.',
                ],
            },
            {
                'id': 'uebergabe',
                'titel': 'Wohnungsübergabe: was tatsächlich verlangt werden darf',
                'absaetze': [
                    'Der häufigste Anlass für einen Renovierungsauftrag ist ein '
                    'Übergabetermin, bei dem der Vermieter „renoviert" im Mietvertrag '
                    'stehen hat. Zwei Dinge sind dabei nützlich zu wissen – beides ohne '
                    'Anspruch auf Rechtsberatung.',
                    'Erstens: <strong>Besenrein und renoviert sind nicht dasselbe.</strong> '
                    'Besenrein heißt geräumt und gefegt; das ist der Standard, den unsere '
                    'Räumungen liefern. Streichen ist eine eigene Leistung mit eigenem '
                    'Preis, und ob sie geschuldet ist, steht im Mietvertrag – nicht im '
                    'Übergabeprotokoll.',
                    'Zweitens: <strong>Nicht jede Renovierungsklausel ist wirksam.</strong> '
                    'Starre Fristenpläne und Klauseln, die auch bei unrenoviert '
                    'übernommenen Wohnungen greifen sollen, hat die Rechtsprechung '
                    'wiederholt kassiert. Ob das auf Ihren Vertrag zutrifft, sagt Ihnen '
                    'ein Mieterverein oder eine Anwältin. Wir sagen Ihnen nur, was die '
                    'Arbeit kostet, wenn Sie sie machen lassen wollen.',
                    'Praktisch bewährt hat sich diese Reihenfolge: erst räumen, dann '
                    'gemeinsam durch die leere Wohnung gehen, dann entscheiden, was '
                    'wirklich gestrichen werden muss. In einer vollen Wohnung sieht das '
                    'jeder falsch ein – in beide Richtungen.',
                ],
            },
            {
                'id': 'boden-bad',
                'titel': 'Bodenbeläge, Bad und größere Vorhaben',
                'absaetze': [
                    'Bodenbeläge erneuern wir mit: Laminat, Vinyl und Teppich '
                    'herausnehmen, Untergrund prüfen, neu verlegen, Sockelleisten setzen. '
                    'Dafür gibt es keinen Quadratmeterpreis auf dieser Seite, und das ist '
                    'Absicht – der Preis hängt am Material, das Sie wählen, und am '
                    'Untergrund, den wir erst sehen, wenn der alte Belag draußen ist. Sie '
                    'bekommen nach dem Aufmaß einen Festpreis, Material getrennt '
                    'ausgewiesen.',
                    'Im <strong>Bad</strong> machen wir Armaturen, Silikonfugen, einzelne '
                    'Fliesen und oberflächlichen Schimmel. Eine komplette Badsanierung '
                    'mit neuen Leitungen, Estrich und Abdichtung ist ein anderes Vorhaben '
                    'für einen Sanitärfachbetrieb – das sagen wir Ihnen bei der '
                    'Besichtigung, bevor ein Angebot entsteht.',
                    'Für eine <strong>Komplettrenovierung</strong> vor Verkauf oder '
                    'Neuvermietung gilt dasselbe Prinzip wie überall bei uns: Erst '
                    'Besichtigung und Aufmaß, dann ein schriftlicher Festpreis mit '
                    'getrennten Positionen, dann der Termin. Was wir nicht selbst machen, '
                    'steht als solches im Angebot und nicht kleingedruckt darunter.',
                ],
            },
            {
                'id': 'steuer',
                'titel': 'Handwerkerleistungen: 20 % der Arbeitskosten, bis 1.200 € im Jahr',
                'absaetze': [
                    'Renovierungs- und Reparaturarbeiten in einem selbst genutzten oder '
                    'gemieteten Haushalt fallen unter §35a Absatz 3 EStG: '
                    '<strong>20 % der Arbeitskosten</strong>, höchstens <strong>1.200 € '
                    'pro Jahr</strong>, direkt von der Steuerschuld.',
                    'Das gilt auch beim Auszug. Die Finanzverwaltung rechnet Arbeiten, '
                    'die die Abnutzung aus der bisherigen Wohnzeit beseitigen, noch dem '
                    'alten Haushalt zu, wenn sie in engem zeitlichem Zusammenhang mit '
                    'dem Umzug stehen – ihr Beispiel sind ausdrücklich '
                    'Renovierungsarbeiten eines ausziehenden Mieters. Für die Räumung '
                    'davor gilt das nicht automatisch: Die Haushaltsauflösung führt sie '
                    'als nicht begünstigt. Deshalb stehen Räumung und Renovierung bei uns '
                    'getrennt im Angebot.',
                    'Abziehbar sind die Arbeitskosten samt berechneter Fahrtkosten, '
                    'Material nicht. Sie brauchen eine Rechnung mit ausgewiesenen '
                    'Arbeitskosten – sprechen Sie uns darauf an – und eine Überweisung '
                    'auf das Konto des Betriebs; eine Barzahlung erkennt das Finanzamt '
                    'auch mit Quittung nicht an.',
                ],
            },
        ],

        'quellen': [
            {'schluessel': 'estg-35a', 'abschnitt': 'steuer',
             'bezug': 'Höchstbetrag und Arbeitskosten'},
            {'schluessel': 'bmf-35a-2016', 'abschnitt': 'steuer',
             'bezug': 'Ausziehender Mieter: Rdnr. 3, Fahrtkosten: Rdnr. 39'},
        ],

        'vergleich': {
            'titel': 'Was wir machen – und wo ein anderer Fachbetrieb hingehört',
            'fazit_frage': 'Welche Arbeiten übernehmen wir nach der Räumung – und welche nicht?',
            'fazit': ('Nach der Räumung übernehmen wir Malerarbeiten ab {maler_min} € ({maler_rate} € pro m²), das Entfernen von Bodenbelägen und Tapeten sowie kleinere Reparaturen. Alles, was in Statik, Elektrik, Gas oder Wasser eingreift, gehört zu einem zugelassenen Fachbetrieb – auch dann, wenn wir es könnten. Wir sagen das vor dem Angebot, nicht danach. Preisstand: {preisstand}.'),
            'kopf': ['Leistung', 'Preis', 'Typischer Anlass'],
            'zeilen': [
                ['Wände und Decken streichen',
                 '{maler_rate} € pro m², mindestens {maler_min} €',
                 'Wohnungsübergabe, Verkaufsvorbereitung, Neuvermietung'],
                ['Kleinreparaturen',
                 'Festpreis je Position, siehe Tabelle',
                 'Dübellöcher, Sockelleisten, Armaturen, Silikonfugen'],
                ['Tapeten entfernen und neu tapezieren',
                 'eigene Position nach Aufwand',
                 'Raufaser über Jahrzehnte, gemusterte Alttapete'],
                ['Bodenbeläge erneuern',
                 'nach Aufmaß, Material getrennt ausgewiesen',
                 'Laminat, Vinyl oder Teppich nach der Räumung'],
                ['Bad: Armaturen, Fugen, einzelne Fliesen',
                 'Festpreis je Position',
                 'Übergabe, tropfende Armatur, schwarze Fuge'],
                ['Elektro und Gas am Netz, Statik, Schadstoffe',
                 'machen wir nicht',
                 'Zählerschrank, Therme, Wanddurchbruch, Asbest'],
            ],
        },

        'beispiele': [
            {
                'titel': 'Wohnung 65 m² räumen und streichen',
                'beschreibung': 'Normal möblierte Wohnung im Erdgeschoss, komplett '
                                'geräumt, anschließend Wände und Decken gestrichen.',
                'args': {'objektart': 'wohnung', 'qm': 65, 'fuellgrad': 'mittel',
                         'with_maler': True},
            },
            {
                'titel': 'Übergabe-Paket, 70 m², 1. OG',
                'beschreibung': 'Räumung, Malerarbeiten und drei Reparaturen: '
                                'Wandlöcher schließen, Sockelleisten erneuern, '
                                'Dusche neu abdichten.',
                'args': {'objektart': 'wohnung', 'qm': 70, 'stockwerk': '1og',
                         'fuellgrad': 'mittel', 'with_maler': True,
                         'klein_items': ['wand_loch', 'sockelleisten', 'dichtungen']},
            },
            {
                'titel': 'Einfamilienhaus 120 m² für den Verkauf',
                'beschreibung': 'Haushaltsauflösung, danach alle Wände und Decken '
                                'gestrichen und die Fliesen im Bad ausgebessert.',
                'args': {'objektart': 'haus', 'qm': 120, 'fuellgrad': 'mittel',
                         'with_maler': True, 'klein_items': ['fliesen']},
            },
        ],

        'ablauf': [
            {'titel': 'Anfrage mit Fotos',
             'text': 'Bilder von jedem Raum, gern auch von den Stellen, um die es '
                     'geht. Sagen Sie dazu, ob nur renoviert oder auch geräumt '
                     'werden soll – das ändert Termin und Reihenfolge.'},
            {'titel': 'Besichtigung und Aufmaß',
             'text': 'Kostenlos. Wand- und Deckenflächen werden gemessen, nicht '
                     'geschätzt: Raumhöhe und Fensteranteil verschieben die Fläche '
                     'gegenüber der Wohnfläche deutlich.'},
            {'titel': 'Festpreisangebot mit getrennten Positionen',
             'text': 'Räumung, Malerarbeiten, Reparaturen und Boden stehen einzeln '
                     'im Angebot. So können Sie einen Teil streichen, ohne dass '
                     'sich der Rest ändert. Für §35a EStG sprechen Sie uns auf '
                     'ausgewiesene Arbeitskosten an.'},
            {'titel': 'Räumen, dann renovieren',
             'text': 'In dieser Reihenfolge, weil in der leeren Wohnung erst '
                     'sichtbar wird, was wirklich gemacht werden muss. Wo nur '
                     'renoviert wird, entfällt der Schritt.'},
            {'titel': 'Abnahme',
             'text': 'Gemeinsam vor Ort oder direkt mit Vermieter, Makler oder '
                     'Hausverwaltung. Was nicht passt, wird nachgearbeitet – der '
                     'Preis ändert sich dadurch nicht.'},
        ],

        'faq': [
            ('Was kostet eine Renovierung nach der Entrümpelung?',
             'Wände und Decken streichen kostet {maler_rate} € pro m², mindestens '
             '{maler_min} €. Kleinreparaturen haben einen festen Preis je Position, '
             'Bodenbeläge und Bad rechnen wir nach Aufmaß. Im selben Auftrag wie '
             'die Räumung ist es günstiger, weil Anfahrt und Rüstzeit nur einmal '
             'anfallen. Preisstand: {preisstand}.'),
            ('Was kostet Streichen pro Quadratmeter?',
             '{maler_rate} € pro m² Wand- und Deckenfläche, mindestens {maler_min} €. '
             'Enthalten sind Abdecken, Grundieren, Ausbessern kleiner Fehlstellen und '
             'zwei Anstriche in Weiß. Sondertöne, Lackarbeiten und das Entfernen alter '
             'Tapeten stehen als eigene Positionen im Angebot.'),
            ('Rechnen Sie nach Wohnfläche oder nach Wandfläche?',
             'Nach Wand- und Deckenfläche. Bei normaler Raumhöhe liegt die zu '
             'streichende Fläche deutlich über der Wohnfläche, deshalb nehmen wir beim '
             'Besichtigungstermin Maß. Der Preisrechner auf dieser Seite rechnet für '
             'eine erste Größenordnung mit der Wohnfläche – verbindlich wird der Preis '
             'nach dem Aufmaß.'),
            ('Machen Sie Räumung und Renovierung gemeinsam?',
             'Ja, und das ist der Regelfall. Beide Leistungen stehen getrennt '
             'ausgewiesen in einem Angebot, es gibt einen Ansprechpartner und einen '
             'Terminplan. Sie können den Renovierungsteil jederzeit streichen, ohne '
             'dass sich der Preis der Räumung ändert.'),
            ('Übernehmen Sie auch Bodenbeläge und Badsanierung?',
             'Bodenbeläge ja – alten Belag heraus, Untergrund prüfen, neu verlegen, '
             'Sockelleisten setzen, Preis nach Aufmaß mit getrennt ausgewiesenem '
             'Material. Im Bad machen wir Armaturen, Silikonfugen, einzelne Fliesen und '
             'oberflächlichen Schimmel. Eine Komplettsanierung mit Leitungen, Estrich '
             'und Abdichtung ist ein anderes Gewerk.'),
            ('Was gehört nicht zu Ihren Leistungen?',
             'Elektro- und Gasarbeiten am Netz, Statik und Wanddurchbrüche sowie '
             'Schadstoffsanierung. Steckdosen und Schalter tauschen wir, den '
             'Zählerschrank nicht. Was wir bei der Besichtigung sehen und nicht machen, '
             'sagen wir Ihnen vor dem Angebot – auch wenn wir den Auftrag dadurch '
             'verlieren.'),
            ('Muss ich als Mieter beim Auszug renovieren?',
             'Das steht in Ihrem Mietvertrag, und nicht jede Renovierungsklausel ist '
             'wirksam: Starre Fristenpläne und Klauseln für unrenoviert übernommene '
             'Wohnungen hat die Rechtsprechung wiederholt gekippt. Ob das auf Ihren '
             'Vertrag zutrifft, sagt Ihnen ein Mieterverein oder eine Anwältin – wir '
             'nennen Ihnen nur den Preis der Arbeit.'),
            ('Ist die Renovierung steuerlich absetzbar?',
             'Ja, als Handwerkerleistung nach §35a Absatz 3 EStG: 20 % der '
             'Arbeitskosten, höchstens 1.200 € pro Jahr – auch für die Wohnung, aus '
             'der Sie gerade ausziehen, wenn die Arbeiten eng mit dem Umzug '
             'zusammenhängen. Für die Räumung davor gilt das nicht automatisch. Sie '
             'brauchen eine Rechnung mit ausgewiesenen Arbeitskosten – sprechen Sie '
             'uns darauf an –, und die Rechnung muss überwiesen werden.'),
            ('Wie schnell nach der Räumung kann gestrichen werden?',
             'In der Regel direkt im Anschluss – wann genau, planen wir gemeinsam '
             'im Angebot. Länger dauert es nur, wenn die '
             'Wände erst trocknen müssen, etwa nach dem Entfernen alter Tapeten oder '
             'nach einer Feuchtebehandlung.'),
            ('Entkernung, Rückbau, Renovierung – was gehört wozu?',
             'Rückbau und Entkernung heißen: Bodenbeläge, Tapeten und '
              'Einbauten kommen raus, bei der Entkernung bis auf den Rohbau. '
              'Renovierung ist das Gegenteil – streichen, spachteln, '
              'wiederherrichten. Wir bauen Bodenbeläge, Tapeten und '
              'nichttragende Einbauten zurück und renovieren danach; Leitungen, '
              'Sanitäranschlüsse und alles Tragende gehören zu einem '
              'Fachbetrieb. Malerarbeiten rechnen wir mit {maler_rate} € '
              'pro m² ab {maler_min} €.'),
        ],

        'related': ['wohnungsaufloesung', 'nachlassraeumung',
                    'messie-wohnung-entruempeln', 'entruempelung-kosten'],

        'staedte': ['leipzig', 'halle', 'magdeburg', 'dresden', 'chemnitz',
                    'hannover', 'merseburg', 'dessau', 'bitterfeld',
                    'weissenfels', 'zwickau', 'stendal'],

        'seo_title': 'Renovierung nach Entrümpelung ab {maler_rate} €/m² | Rümpelwerk',
        'seo_description': (
            'Malerarbeiten ab {maler_rate} € pro m², mindestens {maler_min} €, dazu '
            'Kleinreparaturen zum Festpreis. Räumen und renovieren: '
            'Angebot anfordern.'
        ),
        'seo_keywords': (
            'Renovierung nach Entrümpelung, Malerarbeiten Wohnungsübergabe, '
            'Malerarbeiten Kosten pro qm, Wohnung streichen lassen, '
            'Kleinreparaturen Festpreis, Renovierung Wohnungsauflösung, '
            'Sanierung Sachsen-Anhalt, Renovierung Leipzig Halle'
        ),
    },

    # ───────────────────────────────────────────────────────────────────────
    # A12 — /entruempelung-kosten/
    #
    # Die Money-Seite. Belegt durch den GSC-Export vom August 2026: vier
    # Kosten-Anfragen mit zusammen 55 Impressionen stehen auf Position 65–85
    # und haben null Klicks („haushaltsauflösung dresden preise" 14/66,5 ·
    # „… dresden kosten" 14/68,3 · „entrümpelung dresden kosten" 14/69,4 ·
    # „preise haushaltsauflösung leipzig" 13/84,3). Sichtbar, aber unbrauchbar
    # — weil es keine Seite gibt, die die Frage beantwortet. /preisangebot/
    # rechnet zwar, erklärt aber nichts: dort steht ein Wizard, kein Text.
    #
    # Zugleich die wichtigste GEO-Seite der Website. „Was kostet X" ist der
    # Fragetyp, den AI Overviews und ChatGPT am häufigsten beantworten, und sie
    # zitieren Quellen mit konkreten, datierten Zahlen. Deshalb steht hier jede
    # Zahl mit Preisstand — und keine einzige davon ist getippt.
    #
    # 'name' ist „Entrümpelung", nicht „Entrümpelung Kosten": Das Template baut
    # daraus Sätze („So läuft eine … ab", „Was kostet eine …?"). Fürs Menü und
    # die Brotkrumen steht das Seitenwort in 'label'.
    'entruempelung-kosten': {
        'name': 'Entrümpelung',
        'label': 'Entrümpelung Kosten',
        # EIG398 (02.10.2026): Die Suchabsicht "Entrümpelung Kosten berechnen /
        # Kostenrechner" verteilte sich auf /anfrage/, /preisangebot/ und diese
        # Seite. Gebuendelt wird sie hier: Nur diese Seite hat den Rechner UND
        # erklaert jede Zahl, mit der er rechnet - und sie ist Zielseite der
        # ChatGPT-Anzeigen (Regel 23). /preisangebot/ heisst seitdem
        # "Preisangebot anfordern", /anfrage/ "Entrümpelung anfragen".
        # Die Frage "Was kostet eine Entrümpelung?" bleibt als answer_frage
        # ueber dem Antwortblock stehen.
        'h1': 'Entrümpelung Kosten berechnen',
        'h1_em': 'Rechner und alle Preise offen.',
        'rechner_titel': 'Entrümpelungskosten berechnen',
        'keyword': 'entrümpelung kosten',
        # Keine einzelne Objektart: Die Seite beantwortet die Frage für alle
        # sechs. Damit zeigt der eingebettete Rechner die freie Auswahl, und das
        # Service-Schema trägt kein 'offers' mit einem willkürlichen Mindestpreis.
        'objektart': None,
        'preistabelle': 'entruempelung',
        'modifikatoren': True,

        'hero_sub': (
            'Der Kostenrechner auf dieser Seite rechnet Ihren Fall mit denselben '
            'Zahlen, die hier offen stehen: Quadratmetersätze, Mindestpreise, '
            'jeder Zuschlag und drei komplett durchgerechnete Beispiele. '
            'Stand {preisstand}.'
        ),

        # GE43 (17.09.2026): Die Kostenseite ist der Ratgeber unter einem
        # Leistungs-Slug (RATGEBER_SEITEN) - und der einzige, der hier steht
        # statt in ratgeber.py. Aufbau und Begruendung: data/quellen.py.
        'quellen': [
            {'schluessel': 'estg-35a', 'abschnitt': 'steuer',
             'bezug': 'Maßgeblich ist der Gesetzestext selbst'},
            {'schluessel': 'bmf-35a-anlage1', 'abschnitt': 'steuer',
             'bezug': 'Haushaltsauflösung und Entsorgung als Hauptleistung: '
                      'nicht begünstigt'},
            {'schluessel': 'bmf-35a-2016', 'abschnitt': 'steuer',
             'bezug': 'Ausziehender Mieter: Rdnr. 3, Fahrtkosten: Rdnr. 39'},
        ],

        'answer_frage': 'Was kostet eine Entrümpelung?',
        'answer': (
            'Eine Entrümpelung kostet bei Rümpelwerk Mitteldeutschland ab '
            '{keller_ab} € für einen Keller, ab {wohnung_ab} € für eine Wohnung '
            'und ab {haus_ab} € für ein Haus. Gerechnet wird Fläche mal Satz: '
            '{keller_rate} € pro m² im Keller, {wohnung_rate} € in der Wohnung, '
            '{haus_rate} € im Haus, {gewerbe_rate} € im Gewerbe; darauf wirken '
            'Füllgrad, Stockwerk ohne Aufzug und Sonderabfall. Ihren Betrag '
            'berechnet der Kostenrechner auf dieser Seite in {rechner_dauer}, '
            'verbindlich wird er nach der kostenlosen Besichtigung. '
            'Preisstand: {preisstand}.'
        ),

        'leistungsumfang': [
            'Arbeitslohn des gesamten Teams – keine Stundenabrechnung',
            'An- und Abfahrt, Fahrzeuge, Werkzeug und Verpackungsmaterial',
            'Alle Entsorgungsgebühren, getrennt nach Abfallart',
            'Demontage von Küchen, Schränken, Lampen und Regalen',
            'Tragen aus jedem Stockwerk, auch ohne Aufzug',
            'Besenreine Übergabe: gefegt, grober Schmutz weg, Dübel heraus',
            'Entsorgungsnachweis auf Wunsch – für Nachlass, Vermieter und Buchhaltung',
            'Rechnung mit getrennt ausgewiesenen Arbeitskosten auf Wunsch',
        ],

        'abgrenzung': [
            'Umzugstransporte: Was Sie behalten wollen, stellen wir beiseite. Der '
            'Transport an eine neue Adresse ist eine eigene Leistung.',
            'Schadstoffsanierung: Asbest, künstliche Mineralfasern, Heizöltanks. '
            'Das gehört zu einem zugelassenen Fachbetrieb – und was wir bei der '
            'Besichtigung sehen, sagen wir Ihnen vor dem Angebot.',
            'Endreinigung: Besenrein heißt gefegt, nicht gewischt. Wischen, '
            'Fenster und Sanitärreinigung sind zubuchbar und stehen dann als '
            'eigene Position im Angebot.',
            'Renovierung: Malerarbeiten kosten {maler_rate} € pro m², mindestens '
            '{maler_min} €; Kleinreparaturen sind Einzelpositionen. Alles auf '
            '<a href="/sanierung-renovierung/">Sanierung und Renovierung</a>.',
            'Wertanrechnung: Wir kaufen nichts an und rechnen nichts gegen. Der '
            'Festpreis steht vor Beginn fest – unabhängig davon, was gefunden wird.',
        ],

        'abschnitte': [
            {
                'id': 'kostenrechner',
                'titel': 'So rechnet der Kostenrechner',
                'absaetze': [
                    'Der <a href="#rechner">Kostenrechner</a> fragt ab, was den '
                    'Preis bestimmt: Objektart, Fläche in Quadratmetern, Stockwerk '
                    'und Aufzug, Füllgrad und Sonderabfall. Dazu kommt der Ort – '
                    'liegt er im Servicegebiet, zieht der Rechner {rabatt} % ab –, '
                    'und auf Wunsch Malerarbeiten und Kleinreparaturen. Gerechnet '
                    'wird mit genau den Sätzen und Zuschlägen, die auf dieser Seite '
                    'stehen, nicht mit einer zweiten Preisliste.',
                    'Den Richtpreis zeigt der Rechner nach Angabe von Name und '
                    'E-Mail. Verbindlich wird er erst als Festpreis nach der '
                    'kostenlosen Besichtigung, weil Zugang, Treppenhaus und '
                    'tatsächliche Menge nur sieht, wer vor Ort war. Wer seine Zahl '
                    'ohne Kontaktdaten überschlagen will, findet jeden Baustein '
                    'dafür in den Tabellen weiter unten und in drei durchgerechneten '
                    'Beispielen.',
                ],
            },
            {
                'id': 'preisbildung',
                'titel': 'Wie sich der Preis zusammensetzt',
                'absaetze': [
                    'Der Preis einer Entrümpelung entsteht aus zwei Zahlen und drei '
                    'Zuschlägen. Die beiden Zahlen sind der Quadratmetersatz '
                    'der Objektart und ihr <strong>Mindestpreis</strong>. Gerechnet '
                    'wird Fläche mal Satz; liegt das Ergebnis unter dem Mindestpreis, '
                    'gilt der Mindestpreis. Ein Kellerabteil von sechs Quadratmetern '
                    'kostet deshalb nicht ein Viertel eines Kellers von 24 – Anfahrt, '
                    'Fahrzeug und Deponiegebühr fallen genauso an.',
                    'Die Sätze unterscheiden sich nach Objektart, weil sich die Arbeit '
                    'unterscheidet. Im Keller rechnen wir {keller_rate} € '
                    'pro m² bei mindestens {keller_ab} €, in der Wohnung '
                    '{wohnung_rate} € bei mindestens {wohnung_ab} €, im '
                    'Haus {haus_rate} € bei mindestens {haus_ab} €. '
                    'Ein Haus ist pro Quadratmeter teurer als eine Wohnung, obwohl es '
                    'größer ist: Dachboden, Keller, Garage und Garten hängen mit dran, '
                    'und die Wege sind länger.',
                    'Günstiger wird es dort, wo weniger pro Fläche steht. '
                    'Gewerbeflächen rechnen wir mit {gewerbe_rate} € '
                    'pro m² ab {gewerbe_ab} €, weil eine Lagerhalle auf 400 m² oft '
                    'weniger enthält als eine 60-m²-Wohnung. Eine '
                    'Gartenräumung kostet {garten_rate} € pro m² ab '
                    '{garten_ab} €, eine Scheune {scheune_rate} € pro '
                    'm² ab {scheune_ab} €.',
                    'Alles Weitere sind Zuschläge auf diesen Grundpreis – und alle drei '
                    'stehen weiter unten mit ihrem Betrag in einer Tabelle. Was dort '
                    'nicht steht, kommt auch nicht auf die Rechnung.',
                ],
            },
            {
                'id': 'unterschied',
                'titel': 'Selbst räumen, Container mieten oder Firma beauftragen?',
                'absaetze': [
                    'Die Frage „was kostet eine Entrümpelung" hat drei Antworten, weil '
                    'es drei Wege gibt. Der billigste auf dem Papier ist selten der '
                    'billigste am Ende – die Rechnung geht nur auf, wenn die eigene '
                    'Arbeitszeit mitgerechnet wird.',
                    'Der kommunale Sperrmüll ist in Halle, Magdeburg und Chemnitz in '
                    'festen Mengen ohne zusätzliche Gebühr zu haben, in Leipzig und '
                    'Dresden gegen eine eigene Gebühr. Dafür müssen Sie selbst räumen, '
                    'tragen und zum Termin bereitstellen; Bauschutt und Schadstoffe '
                    'nimmt er nicht mit. Welche Regelung in Ihrer Stadt gilt, steht auf '
                    'der jeweiligen Stadtseite – Freimenge, Kosten und Vorlauf sind je '
                    'Kommune verschieden und ändern sich.',
                    'Ein Container lohnt sich, wenn Sie selbst räumen '
                    'wollen und eine Stellfläche haben. Sie zahlen Miete, Anfahrt und '
                    'Entsorgung nach Gewicht; für den öffentlichen Straßenraum brauchen '
                    'Sie eine Genehmigung. Die Arbeit bleibt bei Ihnen, und Mischabfall '
                    'ist die teuerste Fraktion überhaupt.',
                    'Die <strong>Firma zum Festpreis</strong> ist der teuerste Weg pro '
                    'Kubikmeter und der günstigste pro Stunde Ihrer Zeit. Sie nennen '
                    'den Termin, wir tragen, trennen, fahren und fegen. Der Vergleich '
                    'mit Zahlen steht auf '
                    '<a href="/sperrmuell-entsorgung/">Sperrmüll entsorgen</a>.',
                ],
            },
            {
                'id': 'zuschlaege',
                'titel': 'Was den Preis nach oben treibt – und um wie viel',
                'absaetze': [
                    'Drei Größen verändern den Grundpreis, und alle drei sind bezifferbar. '
                    'Sie stehen mit ihrem Betrag in der '
                    '<a href="#zuschlagstabelle">Zuschlagstabelle</a> weiter unten; hier '
                    'steht, warum es sie gibt.',
                    'Der Füllgrad ist der stärkste Hebel, weil er '
                    'multiplikativ wirkt: Eine kaum möblierte Wohnung ist der Grundpreis, '
                    'eine normal möblierte liegt darüber, ein Messie-Fall bei fast dem '
                    'Doppelten. Das ist keine Bewertung, sondern eine Mengenangabe – '
                    'dieselbe Fläche kann fünf oder fünfzig Kubikmeter enthalten.',
                    'Das Stockwerk ohne Aufzug kostet Zeit, und Zeit ist '
                    'in einem Festpreis der einzige Posten, den wir nicht nachreichen '
                    'können. Der Zuschlag gilt für Wohnungen und Keller und entfällt '
                    'vollständig, wenn ein benutzbarer Aufzug da ist. Ein zweiter Stock '
                    'ohne Aufzug kostet regelmäßig mehr Zeit als ein doppelt so großes '
                    'Erdgeschoss.',
                    'Sonderabfall ist alles, was nicht in den normalen '
                    'Sperrmüll darf: Farben, Lacke, Lösemittel, Batterien, '
                    'Leuchtstoffröhren, Altöl. Er wird getrennt gesammelt, getrennt '
                    'gefahren und getrennt bezahlt. Deshalb fragen wir bei der '
                    'Besichtigung danach – und deshalb ist ein Angebot ohne diese Frage '
                    'keines.',
                    'Nicht bepreist, aber wichtig: der Zugang. Enge '
                    'Altstadtgassen, fehlende Halteverbotszone, ein Hinterhof ohne '
                    'Zufahrt – das sehen wir bei der Besichtigung und rechnen es in den '
                    'Festpreis ein. Wer eine Halteverbotszone selbst beantragt, spart '
                    'genau diesen Aufwand.',
                ],
            },
            {
                'id': 'senken',
                'titel': 'Was den Preis senkt',
                'absaetze': [
                    'Drei Dinge machen eine Entrümpelung günstiger, und keines davon '
                    'kostet Sie etwas außer Absprache.',
                    'Standort im Servicegebiet: Liegt das Objekt in '
                    'einer der Städte, in denen wir ohnehin fahren, ziehen wir '
                    '{rabatt} % ab. Das ist keine Rabattaktion, sondern eine ersparte '
                    'Anfahrt, die wir weitergeben. Der Kostenrechner erkennt das '
                    'automatisch, sobald Sie den Ort eintragen.',
                    'Eigenleistung: Was vor unserem Termin schon draußen '
                    'ist, zahlen Sie nicht. Kleidersammlung, Bücher an die Bücherei, '
                    'Elektrogeräte zum Wertstoffhof – das senkt Menge und Füllgrad und '
                    'damit den Faktor, der multiplikativ wirkt. Sagen Sie uns vorher, was '
                    'Sie selbst schaffen, dann rechnen wir damit.',
                    'Bündeln: Keller, Wohnung und Garage in einem Auftrag '
                    'sind günstiger als drei Einsätze, weil Anfahrt und Rüstzeit einmal '
                    'anfallen. Dasselbe gilt für die Renovierung im Anschluss – das '
                    'Objekt ist dann schon leer.',
                    'Was den Preis <em>nicht</em> senkt: der Wert des Hausrats. Wir kaufen '
                    'nichts an und rechnen nichts gegen. Das ist bewusst so – ein Preis, '
                    'der von einer Schätzung abhängt, ist kein Festpreis, und was Ihnen '
                    'gehört, soll Ihnen gehören.',
                ],
            },
            {
                'id': 'steuer',
                'titel': 'Ist eine Entrümpelung steuerlich absetzbar?',
                'absaetze': [
                    'Nicht pauschal. §35a EStG kennt zwei Töpfe: haushaltsnahe '
                    'Dienstleistungen mit 20 % der Arbeitskosten, höchstens 4.000 € im '
                    'Jahr, und Handwerkerleistungen mit 20 %, höchstens 1.200 €. Abgezogen '
                    'wird von der Steuerschuld, nicht vom Einkommen.',
                    'Die Finanzverwaltung zieht für Räumungen aber eine Grenze: In der '
                    'Anlage 1 zum BMF-Schreiben steht die Haushaltsauflösung ausdrücklich '
                    'unter „nicht begünstigt“, ebenso eine Entsorgung, die selbst die '
                    'Hauptleistung ist. Eine Entrümpelung, bei der es nur ums Leeren '
                    'geht, ist deshalb meist nicht absetzbar – auch wenn das an vielen '
                    'Stellen anders zu lesen ist.',
                    'Anders liegt es, wenn die Arbeit Teil einer Leistung im Haushalt ist, '
                    'etwa beim Renovieren vor dem eigenen Auszug: Auch Arbeiten in der '
                    'alten Wohnung zählen dann noch zum Haushalt. Anrechenbar sind immer '
                    'nur Arbeits- und Fahrtkosten, nicht Material und Entsorgungsgebühren, '
                    'und nur mit Rechnung und Überweisung – Barzahlung zählt nicht. Ob Ihr '
                    'Fall darunter fällt, entscheidet das Finanzamt; auf Wunsch weisen '
                    'wir die Arbeitskosten in der Rechnung getrennt aus.',
                ],
            },
            {
                'id': 'seriositaet',
                'titel': 'Woran Sie ein belastbares Angebot erkennen',
                'absaetze': [
                    'Preise im Internet sind schwer vergleichbar, weil sie '
                    'unterschiedliche Dinge messen. Manche Anbieter rechnen pro '
                    'Kubikmeter, andere pro Quadratmeter, '
                    'wieder andere pro Stunde und Mann. Ein '
                    'Kubikmeterpreis klingt niedrig und ist es auch – bis jemand die '
                    'Kubikmeter zählt, und das tut er erst beim Verladen.',
                    'Wir rechnen nach Quadratmetern, weil Sie die Zahl kennen, bevor jemand '
                    'da war. Sie steht in Ihrem Mietvertrag oder im Exposé. Damit können '
                    'Sie ein Angebot prüfen, statt es zu glauben.',
                    'Drei Dinge sollten in jedem Angebot stehen, egal von wem: der '
                    '<strong>Gesamtpreis als Festpreis</strong>, die '
                    'Arbeitskosten getrennt ausgewiesen und die Angabe, '
                    'was nicht enthalten ist. Fehlt der dritte Punkt, '
                    'steht der Nachschlag schon fest, nur das Datum noch nicht.',
                    'Und ein Angebot ohne Besichtigung ist eine Schätzung, keine Zusage. '
                    'Wir nennen auf Fotos gern eine Größenordnung, damit Sie planen können '
                    '– verbindlich wird der Preis, wenn wir das Objekt gesehen haben und '
                    'das Festpreisangebot vorliegt.',
                ],
            },
            {
                'id': 'regional',
                'titel': 'Kostet eine Entrümpelung in Leipzig mehr als in Halle?',
                'absaetze': [
                    'Nein. Unsere Sätze sind in ganz Mitteldeutschland dieselben – in '
                    'Leipzig, Halle, Magdeburg, Dresden, Chemnitz und Hannover gilt '
                    'dieselbe Tabelle. Was sich unterscheidet, ist nicht der Preis, '
                    'sondern das, was vor Ort dazukommt.',
                    'Drei Dinge sind örtlich verschieden: die Gebühren des '
                    'zuständigen Entsorgers, die kommunale '
                    'Sperrmüllregelung mit ihrer Freimenge und der '
                    'Gebäudebestand. Ein Leipziger Gründerzeitbau mit '
                    'vierter Etage ohne Aufzug ist ein anderer Auftrag als ein '
                    'Plattenbau mit Lastenaufzug – nicht weil die Stadt eine andere ist, '
                    'sondern weil die Treppe eine andere ist.',
                    'Deshalb steht auf jeder Stadtseite, welcher Entsorger zuständig ist, '
                    'wo der Wertstoffhof liegt und wie die Sperrmüllregelung dort '
                    'aussieht – mit Stand und Quelle. Im Servicegebiet ziehen wir '
                    '{rabatt} % ab; das ist der einzige regionale Unterschied im Preis '
                    'selbst.',
                ],
            },
        ],

        'vergleich': {
            'titel': 'Drei Wege, ein Objekt zu leeren – was sie wirklich kosten',
            'fazit_frage': 'Firma, Container oder selbst räumen – was kostet wirklich weniger?',
            'fazit': ('Selbst räumen ist günstiger, solange Ihre Arbeitszeit nichts kostet und Sie tragen können: Beim kommunalen Sperrmüll zahlen Sie wenig oder nichts extra, stellen aber alles selbst an den Bordstein. Ein Container kostet Miete, Anfahrt und Entsorgung nach Gewicht – die Beladung bleibt Ihre Arbeit. Eine Firma zum Festpreis beginnt bei {keller_ab} € für den Keller und {wohnung_ab} € für die Wohnung. Preisstand: {preisstand}.'),
            'kopf': ['Weg', 'Was Sie zahlen', 'Was Sie selbst tun', 'Zeit'],
            'zeilen': [
                ['Kommunaler Sperrmüll',
                 'je nach Stadt in der Abfallgebühr enthalten oder eigene Gebühr',
                 'räumen, tragen, sortieren, bereitstellen',
                 'Vorlauf bis zum Termin, je nach Kommune Wochen'],
                ['Container mieten',
                 'Miete + Anfahrt + Entsorgung nach Gewicht, ggf. Stellgenehmigung',
                 'komplett selbst räumen und beladen',
                 'Stellzeit plus Ihre eigenen Arbeitstage'],
                ['Firma zum Festpreis',
                 'ab {keller_ab} € Keller · ab {wohnung_ab} € Wohnung · ab {haus_ab} € Haus',
                 'nichts – Sie nennen den Termin',
                 'nach Absprache, Angebot {angebot_frist}'],
            ],
        },

        # G11, Vergleich 4: die Abrechnungsmodelle der Branche.
        #
        # Hier steht **keine fremde Zahl**, und das ist Absicht. Ein
        # Stundensatz oder ein Kubikmeterpreis "der Branche" haette weder eine
        # Quelle in pricing.py noch eine belegte Fremdquelle mit Datum und
        # Link - und die Preispruefung in check_seo faende ihn nicht: Sie
        # meldet falsche Zahlen, nicht quellenlose. Verglichen wird deshalb,
        # was die Modelle strukturell leisten.
        #
        # Die Zeile "Wo es teuer wird" nennt auch den Nachteil des eigenen
        # Modells. Einseitige Vergleiche werden als Werbung eingestuft und
        # nicht zitiert - und der Kunde merkt es ohnehin.
        'vergleich_2': {
            'titel': 'Festpreis, Stundenlohn und Kubikmeterpreis im Vergleich',
            'eigene_spalte': 2,
            'fazit_frage': 'Festpreis, Stundenlohn oder Kubikmeterpreis – '
                           'was ist für mich sicherer?',
            'fazit': ('Beim Festpreis wird der Betrag bei der Besichtigung genannt '
                      'und ist im Angebot verbindlich. '
                      'Dafür kalkuliert er einen Puffer ein – bei einer wirklich '
                      'kleinen, klar begrenzten Arbeit kann ein Stundensatz '
                      'günstiger sein. Der Kubikmeterpreis ist eine Schätzgröße, '
                      'kein Angebot. Wir arbeiten zum Festpreis ab {keller_ab} €. '
                      'Preisstand: {preisstand}.'),
            'kopf': ['', 'Festpreis', 'Stundenlohn', 'Kubikmeterpreis'],
            'zeilen': [
                ['Was vorher feststeht', 'der Endbetrag', 'der Stundensatz',
                 'der Preis je Kubikmeter'],
                ['Wann der Preis feststeht', 'bei der Besichtigung', 'nach Aufwand',
                 'nach Schätzung der Menge'],
                ['Voraussetzung', 'Besichtigung vor Ort',
                 'keine – nach Aufwand', 'Schätzung der Menge'],
                ['Nachträgliche Erhöhung', 'Festpreis, verbindlich im Angebot',
                 'bei jeder zusätzlichen Stunde', 'bei mehr Volumen als geschätzt'],
                ['Wo es teuer wird', 'wenn die Menge überschätzt wurde',
                 'wenn die Wohnung voller ist als gedacht',
                 'wenn sperrige Möbel viel Volumen bei wenig Gewicht machen'],
                ['Gut geeignet für', 'Räumungen mit festem Übergabetermin',
                 'kleine, klar begrenzte Arbeiten', 'eine grobe Vorabschätzung'],
                ['Bei uns', 'ja, ab {keller_ab} €', 'nein',
                 'nur als Schätzung im Preisrechner'],
            ],
        },

        'beispiele': [
            {
                'titel': 'Kellerabteil, 15 m², voll',
                'beschreibung': 'Jahrzehnte Einweckgläser, Reifen und Kartons, dazu '
                                'einzelne Farbdosen als Sonderabfall.',
                'args': {'objektart': 'keller', 'qm': 15, 'fuellgrad': 'voll',
                         'sonderabfall': 'wenige'},
            },
            {
                'titel': '3-Zimmer-Wohnung, 70 m², 2. OG ohne Aufzug',
                'beschreibung': 'Normal möbliert, komplette Räumung, besenreine '
                                'Übergabe an den Vermieter.',
                'args': {'objektart': 'wohnung', 'qm': 70, 'stockwerk': '2og',
                         'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Einfamilienhaus, 140 m², voll, mit Malerarbeiten',
                'beschreibung': 'Kompletter Hausstand inklusive Keller und Garage, '
                                'einzelne Sonderabfälle, anschließend Wände streichen.',
                'args': {'objektart': 'haus', 'qm': 140, 'fuellgrad': 'voll',
                         'sonderabfall': 'wenige', 'with_maler': True},
            },
        ],

        'ablauf': [
            {'titel': 'Größenordnung selbst rechnen',
             'text': 'Der Kostenrechner auf dieser Seite fragt Objektart, Fläche, '
                     'Stockwerk, Füllgrad und Sonderabfall ab und nennt in etwa '
                     '{rechner_dauer} einen konkreten Wert. Er rechnet mit denselben '
                     'Zahlen wie diese Seite.'},
            {'titel': 'Anfrage mit Fotos',
             'text': 'Ein paar Bilder aus jedem Raum reichen für eine belastbare '
                     'Einschätzung. Per WhatsApp, Formular oder Telefon – wir '
                     'melden uns in {reaktion} zurück.'},
            {'titel': 'Kostenlose Besichtigung',
             'text': 'Wir sehen uns Fläche, Menge, Zugang, Treppenhaus und '
                     'Parksituation an. Ohne diesen Termin gibt es keinen '
                     'Festpreis, sondern nur eine Schätzung – und das sagen wir '
                     'auch so.'},
            {'titel': 'Festpreisangebot',
             'text': 'Schriftlich, {angebot_frist}, mit Termin. Auf Wunsch '
                     'mit getrennt ausgewiesenen Arbeitskosten.'},
            {'titel': 'Räumung und Übergabe',
             'text': 'Wir räumen, trennen, verladen und fegen. Besenreine Abnahme '
                     'mit Ihnen oder direkt mit Vermieter, Makler oder '
                     'Hausverwaltung, Entsorgungsnachweis auf Wunsch.'},
        ],

        'faq': [
            ('Was kostet eine Entrümpelung?',
             'Eine Entrümpelung kostet ab {keller_ab} € für einen Keller, ab '
             '{wohnung_ab} € für eine Wohnung und ab {haus_ab} € für ein Haus. '
             'Über den Mindestpreis hinaus wird nach Fläche gerechnet: '
             '{keller_rate} € pro m² im Keller, {wohnung_rate} € in der Wohnung, '
             '{haus_rate} € im Haus. Füllgrad, Stockwerk ohne Aufzug und '
             'Sonderabfall kommen als Zuschläge dazu. Preisstand: {preisstand}.'),
            ('Was kostet eine Entrümpelung pro Quadratmeter?',
             'Der Richtwert hängt an der Objektart: Keller {keller_rate} € pro m², '
             'Wohnung {wohnung_rate} €, Haus {haus_rate} €, Gewerbe '
             '{gewerbe_rate} €, Garten {garten_rate} €, Scheune {scheune_rate} €. '
             'Unter dem jeweiligen Mindestpreis wird nicht gerechnet, weil '
             'Anfahrt, Fahrzeug und Entsorgungsgebühr unabhängig von der Fläche '
             'anfallen.'),
            ('Was kostet eine Haushaltsauflösung?',
             'Eine komplette Haushaltsauflösung beginnt bei {haus_ab} € und wird '
             'darüber mit {haus_rate} € pro m² gerechnet. Ein Einfamilienhaus von '
             '{haus_qm} m² liegt normal möbliert bei {haus_beispiel}. Alles '
             'Weitere steht auf '
             '<a href="/haushaltsaufloesung/">Haushaltsauflösung</a>.'),
            ('Was kostet eine Wohnungsauflösung?',
             'Eine Wohnungsauflösung beginnt bei {wohnung_ab} €, Richtwert '
             '{wohnung_rate} € pro m². Eine normal möblierte Wohnung von '
             '{wohnung_qm} m² im Erdgeschoss liegt bei {wohnung_beispiel}; ohne '
             'Aufzug kommt der Stockwerkzuschlag dazu. Details auf '
             '<a href="/wohnungsaufloesung/">Wohnungsauflösung</a>.'),
            ('Was kostet eine Kellerentrümpelung?',
             'Eine Kellerentrümpelung kostet ab {keller_ab} €, Richtwert '
             '{keller_rate} € pro m². Ein normales Kellerabteil von {keller_qm} m² '
             'liegt bei {keller_beispiel}. Das ist zugleich der günstigste '
             'Einstieg unseres Portfolios – mehr auf '
             '<a href="/kellerentruempelung/">Kellerentrümpelung</a>.'),
            ('Was kostet eine Entrümpelung in Dresden oder Leipzig?',
             'Dasselbe wie überall in unserem Gebiet: Die Sätze sind in Leipzig, '
             'Halle, Magdeburg, Dresden, Chemnitz und Hannover identisch. Im '
             'Servicegebiet ziehen wir {rabatt} % ab. Örtlich verschieden sind '
             'nur die Gebühren des zuständigen Entsorgers und die kommunale '
             'Sperrmüllregelung – beides steht auf der jeweiligen Stadtseite.'),
            ('Gibt es versteckte Kosten oder Nachschläge?',
             'Der Festpreis steht bei der Besichtigung im Angebot und ist dort '
             'verbindlich. Was nicht enthalten ist, steht ebenfalls im Angebot: Umzugstransporte, '
             'Schadstoffsanierung, Endreinigung über besenrein hinaus und '
             'Renovierung. Ein Angebot, das nur den Preis nennt und nicht die '
             'Grenze, ist unvollständig.'),
            ('Ist eine Entrümpelung steuerlich absetzbar?',
             'Meist nicht. Die Finanzverwaltung führt die Haushaltsauflösung und '
             'eine Entsorgung als Hauptleistung als nicht begünstigt nach §35a '
             'EStG. Absetzbar sind Arbeitskosten nur, wenn die Arbeit Teil einer '
             'Leistung im Haushalt ist, etwa einer Renovierung vor dem eigenen '
             'Auszug – dann 20 %, höchstens 4.000 € (haushaltsnahe Dienstleistung) '
             'oder 1.200 € (Handwerkerleistung) im Jahr, nur mit Rechnung und '
             'Überweisung. Ob Ihr Fall dazugehört, entscheidet das Finanzamt.'),
            ('Wird mir der Wert der Möbel angerechnet?',
             'Nein. Wir kaufen nichts an und rechnen nichts gegen den Preis. Das '
             'ist bewusst so: Ein Preis, der von einer Schätzung abhängt, ist kein '
             'Festpreis. Wertgegenstände, Dokumente und Fotos sammeln wir getrennt '
             'und übergeben sie Ihnen – sagen Sie uns vorher, worauf wir besonders '
             'achten sollen.'),
            ('Wird es günstiger, wenn ich selbst mithelfe?',
             'Ja, wenn Sie vor dem Termin Menge herausnehmen. Kleidersammlung, '
             'Bücher, Elektrogeräte zum Wertstoffhof: Das senkt Menge und Füllgrad, '
             'und der Füllgrad wirkt multiplikativ auf den Grundpreis. Sagen Sie '
             'uns vor der Besichtigung, was Sie selbst schaffen, dann steht es im '
             'Angebot. Am Räumungstag mitzuhelfen ändert dagegen nichts mehr – der '
             'Preis ist dann bereits fest.'),
            ('Warum rechnen Sie nach Quadratmetern und nicht nach Kubikmetern?',
             'Weil Sie die Quadratmeter kennen, bevor jemand da war – sie stehen im '
             'Mietvertrag oder im Exposé. Kubikmeter kennt niemand vorher; sie '
             'werden beim Verladen gezählt, also nachdem der Auftrag vergeben ist. '
             'Ein Kubikmeterpreis klingt deshalb günstiger, als er sich am Ende '
             'rechnet.'),
            ('Was kostet eine Beräumung, eine Wohnungsräumung oder „räumen '
             'lassen"?',
             'Dasselbe wie eine Entrümpelung – die Begriffe meinen dieselbe '
              'Arbeit. Der Preis hängt nicht am Wort, sondern an vier Dingen: '
              'Fläche in m², Füllgrad, Stockwerk ohne Aufzug und '
              'Sonderabfall. Eine Kellerberäumung beginnt bei {keller_ab} €, '
              'eine Wohnungsräumung bei {wohnung_ab} €, eine komplette '
              'Hausauflösung bei {haus_ab} €. Preisstand: {preisstand}.'),
            ('Was kostet eine professionelle Entrümpelung in Sachsen-Anhalt?',
             'Dieselben Sätze wie überall in unserem Gebiet – wir rechnen '
              'nicht nach Bundesland. Liegt das Objekt in einer der {rabatt_anzahl} '
              'Städte, in denen wir ohnehin fahren, ziehen wir {rabatt} % ab '
              '– höchstens bis zum Mindestpreis. In Sachsen-Anhalt '
              'sind das unter anderem Halle, Magdeburg, Merseburg, Dessau, '
              'Köthen, Stendal und Halberstadt. Was Ihr Objekt kostet, '
              'rechnen Sie unten in {rechner_dauer} selbst aus.'),
        ],

        'related': ['haushaltsaufloesung', 'kellerentruempelung',
                    'gewerbeentruempelung', 'sperrmuell-entsorgung'],

        'staedte': ['leipzig', 'halle', 'magdeburg', 'dresden', 'chemnitz',
                    'hannover', 'merseburg', 'dessau', 'bitterfeld',
                    'weissenfels', 'zwickau', 'stendal'],

        'seo_title': 'Entrümpelung Kosten berechnen – ab {keller_ab} € | Rümpelwerk',
        'seo_description': (
            'Entrümpelung Kosten berechnen: Keller ab {keller_ab} €, Wohnung '
            'ab {wohnung_ab} €, Haus ab {haus_ab} €, jeder Zuschlag offen. '
            'Besichtigung kostenlos.'
        ),
        'seo_keywords': (
            'Entrümpelung Kosten berechnen, Entrümpelung Kostenrechner, '
            'Entrümpelung Kosten, was kostet eine Entrümpelung, Entrümpelung '
            'Preis pro qm, Haushaltsauflösung Preise, Haushaltsauflösung Kosten, '
            'Wohnungsauflösung Kosten, Kellerentrümpelung Preis, Entrümpelung '
            'Preisliste, Entrümpelung Festpreis, Entrümpelung absetzbar'
        ),
    },
}


# ── Zugriff ──────────────────────────────────────────────────────────────────

def _komma(x):
    """0.05 -> '0,05'. Deutscher Fliesstext braucht das Dezimalkomma.

    In JSON-LD gilt das Gegenteil (dort ist der Punkt Pflicht) - diese Werte
    stehen aber im Antworttext, nicht als Zahlenwert.
    """
    return f'{x:.2f}'.replace('.', ',')


def _platzhalter():
    """Die Werte, die in den Texten oben eingesetzt werden – alle aus pricing.py."""
    pk = preis_context()
    mods = pk['PREIS_MODIFIKATOREN']
    werte = {
        'preisstand': pk['PREISSTAND'],
        # Zeitzusagen aus data/zusagen.py, nicht getippt (Befund K2).
        'angebot_frist': _ANGEBOT_FRIST,
        'reaktion': _REAKTION,
        'rechner_dauer': _RECHNER_DAUER,
        # Wie viele Stadtseiten es gibt - stand bis zum 02.10.2026 als "54"
        # getippt im Text, waehrend _CITY_DATA laengst 57 Eintraege hatte.
        'staedte_anzahl': len(_CITY_DATA),
        'maler_rate': _MALER_PER_QM['rate'],
        'maler_min': _MALER_PER_QM['min_preis'],
        'rabatt': mods['rabatt_prozent'],
        # Wie viele Orte den Nachlass bekommen - stand als „25“ getippt.
        'rabatt_anzahl': len(_STANDORT_RABATT_STAEDTE),
        # Die Modifikatoren, damit auch sie im Fliesstext nicht getippt werden.
        # Sie standen bis zum 25.08.2026 in /messie-wohnung-entruempeln/ als
        # "150 € bis 590 €" und "1,55 / 1,75" von Hand im Absatz - richtig, aber
        # ohne Verbindung zur Quelle. Die neue Preispruefung in check_seo haette
        # sie nicht gefunden: Sie meldet falsche Zahlen, nicht getippte.
        'stockwerk_min_txt': euro(min(v for v in mods['stockwerk'].values() if v)),
        'stockwerk_max_txt': euro(max(mods['stockwerk'].values())),
        'sonderabfall_wenige_txt': euro(mods['sonderabfall']['wenige']),
        'sonderabfall_viele_txt': euro(mods['sonderabfall']['viele']),
        'fuellgrad_leicht': _komma(mods['fuellgrad']['leicht']),
        'fuellgrad_voll': _komma(mods['fuellgrad']['voll']),
        'fuellgrad_verschmutzt': _komma(mods['fuellgrad']['verschmutzt']),
        'fuellgrad_messi': _komma(mods['fuellgrad']['messi']),
        'fuellgrad_messi_prozent': int(round((mods['fuellgrad']['messi'] - 1) * 100)),
    }
    for key, zeile in pk['PREISE'].items():
        werte[f'{key}_ab'] = zeile['min_txt']
        werte[f'{key}_rate'] = zeile['rate']
        werte[f'{key}_qm'] = zeile['qm_typisch']
        werte[f'{key}_beispiel'] = zeile['beispiel_txt']
        # Bis zu welcher Flaeche der Mindestpreis den Grundpreis bildet -
        # gerechnet, damit der Satz "bis etwa 30 m²" beim naechsten
        # Satzwechsel nicht stehen bleibt.
        werte[f'{key}_grenze_qm'] = -(-zeile['min'] // zeile['rate'])
    return werte


def _fuellen(wert, werte):
    """Setzt die Platzhalter rekursiv ein und kopiert dabei die Struktur."""
    if isinstance(wert, str):
        return wert.format(**werte)
    if isinstance(wert, dict):
        return {k: _fuellen(v, werte) for k, v in wert.items()}
    if isinstance(wert, (list, tuple)):
        return [_fuellen(v, werte) for v in wert]
    return wert


# ── Welche dieser Seiten ein Ratgeber ist (GE15, 10.09.2026) ────────────────
#
# Neun Adressen liegen unter einem Leistungs-Slug, aber nur eine davon ist ein
# **Text**: ``/entruempelung-kosten/`` erklaert, wie ein Preis entsteht, und
# man kann sie nicht beauftragen. Das steht in diesem Modul schon zweimal
# schwarz auf weiss - ``_HUB_UMFANG`` nennt sie "Preisuebersicht, keine
# Leistung", und ``hub_vergleich()`` laesst sie aus der Vergleichstabelle
# heraus, "sonst stuende in der Preisspalte eine Zahl fuer etwas, das man
# nicht beauftragen kann".
#
# Der ``Article``-Knoten (``schema.article_schema``) haengt an dieser Liste
# und nicht an einer Abfrage in der View. Wer eine weitere Ratgeberseite
# anlegt, traegt sie hier ein **und** ihr belegtes Erscheinungsdatum in
# ``data/lastmod.py::VEROEFFENTLICHT`` - ohne das zweite bleibt der Knoten
# aus, statt ein Datum zu erfinden.
#
# **Die uebrigen acht bleiben bewusst draussen.** Eine Leistungsseite ist ein
# Angebot, kein Aufsatz; sie als ``Article`` auszuzeichnen waere formal
# gueltig und inhaltlich falsch - dieselbe Zurueckhaltung wie bei ``sameAs``
# (G5) und beim ``author`` in ``webpage_schema``.
RATGEBER_SEITEN = ('entruempelung-kosten',)


# ── Orientierungstabelle des Hubs (G11, 27.08.2026) ─────────────────────────
# Der Anlass ist das einzige Feld, das hier von Hand steht: Er laesst sich aus
# keinem vorhandenen Feld ableiten, und geraten waere er wertlos. Umfang und
# Preis kommen aus den Leistungsdaten bzw. pricing.py.
#
# Bewusst **nicht** die Dreier-Tabelle von /haushaltsaufloesung/: Dieselbe
# Tabelle auf drei Seiten waere Duplikat und triebe die Aehnlichkeit hoch.
_HUB_ANLASS = {
    'haushaltsaufloesung':       'Todesfall, Pflegeheim, Hausverkauf',
    'wohnungsaufloesung':        'Auszug, Mietende, Nachlass',
    'kellerentruempelung':       'Platz schaffen, Keller- oder Dachbodenabteil',
    'nachlassraeumung':          'Erbfall, Erbengemeinschaft',
    'gewerbeentruempelung':      'Betriebsaufgabe, Umzug, Insolvenz',
    'messie-wohnung-entruempeln': 'Verwahrlosung, Räumungsklage, Gesundheitsamt',
    'sperrmuell-entsorgung':     'einzelne Möbel, kein Transporter da',
    'sanierung-renovierung':     'nach der Räumung, vor der Übergabe',
    'entruempelung-kosten':      'Sie wollen zuerst wissen, was es kostet',
}

# Umfang in drei Worten - laenger passt in einer Tabellenzelle nicht.
_HUB_UMFANG = {
    'haushaltsaufloesung':       'kompletter Hausstand',
    'wohnungsaufloesung':        'komplette Mietwohnung',
    'kellerentruempelung':       'einzelne Räume',
    'nachlassraeumung':          'kompletter Hausstand, mit Wertsichtung',
    'gewerbeentruempelung':      'Ladenlokal, Büro, Halle',
    'messie-wohnung-entruempeln': 'komplett, mit Grobreinigung',
    'sperrmuell-entsorgung':     'einzelne Stücke',
    'sanierung-renovierung':     'Wände, Böden, Kleinreparaturen',
    'entruempelung-kosten':      'Preisübersicht, keine Leistung',
}


# Wo der Einstiegspreis der Leistung nicht an ihrer Objektart haengt.
_HUB_PREIS_ART = {
    'nachlassraeumung': 'wohnung',
}


def hub_vergleich():
    """Die Orientierungstabelle fuer /dienstleistungen/ - Anlass, Umfang, Preis.

    Der Preis kommt aus ``preis_context()``, also aus derselben Quelle wie der
    Rechner. ``entruempelung-kosten`` ist eine Uebersichtsseite und keine
    Leistung - sie steht deshalb **nicht** in der Tabelle, sonst stuende in der
    Preisspalte eine Zahl fuer etwas, das man nicht beauftragen kann.
    """
    pk = preis_context()
    zeilen = []
    for slug, roh in _SERVICE_DATA.items():
        if slug == 'entruempelung-kosten':
            continue
        # 02.10.2026: Die Nachlassseite rechnet mit dem Haus, beginnt aber bei
        # der Wohnung (seo_title "ab {wohnung_ab}") - die Tabelle nannte den
        # Hauspreis und damit einen hoeheren Einstieg als die Seite selbst.
        art = _HUB_PREIS_ART.get(slug, roh.get('objektart'))
        preis = pk['PREISE'][art]['min_txt'] + ' €' if art in pk['PREISE'] else '–'
        zeilen.append([roh['name'], _HUB_ANLASS.get(slug, ''),
                       _HUB_UMFANG.get(slug, ''), preis])
    return {
        'titel': 'Welche Leistung passt zu welchem Anlass?',
        'anker': 'vergleich',
        'fazit_frage': 'Entrümpelung, Haushaltsauflösung oder Wohnungsauflösung – '
                       'welche Leistung brauche ich?',
        'fazit': ('Entscheidend ist der Umfang, nicht der Name. Werden einzelne '
                  'Räume geleert und das Objekt weiter bewohnt, ist es eine '
                  'Entrümpelung – ab %s €. Wird ein ganzer Hausstand aufgelöst, '
                  'etwa nach einem Todesfall, ist es eine Haushaltsauflösung – '
                  'ab %s €. Geht eine Mietwohnung besenrein an den Vermieter '
                  'zurück, ist es eine Wohnungsauflösung – ab %s €. '
                  'Der Ablauf ist in allen drei Fällen derselbe. Preisstand: %s.'
                  % (pk['PREISE']['keller']['min_txt'],
                     pk['PREISE']['haus']['min_txt'],
                     pk['PREISE']['wohnung']['min_txt'],
                     pk['PREISSTAND'])),
        'kopf': ['Leistung', 'Typischer Anlass', 'Umfang', 'Preis ab'],
        'zeilen': zeilen,
    }


@functools.lru_cache(maxsize=None)
def leistung(slug):
    """Eine Leistung mit eingesetzten Preisen – oder ``None``.

    Gecacht wie ``preis_context()``: Die Daten sind Konstanten, die Views lesen
    sie nur. ``args``-Dicts der Beispiele bleiben unangetastet, sie enthalten
    keine Texte.
    """
    roh = _SERVICE_DATA.get(slug)
    if not roh:
        return None
    werte = _platzhalter()
    daten = {k: (v if k == 'beispiele' else _fuellen(v, werte))
             for k, v in roh.items()}
    # Beispiele: nur die Texte füllen, 'args' bleibt ein Dict für berechne_preis.
    daten['beispiele'] = [
        {**b, 'titel': b['titel'].format(**werte),
         'beschreibung': b['beschreibung'].format(**werte)}
        for b in roh.get('beispiele', [])
    ]
    daten['slug'] = slug
    daten['url'] = f'/{slug}/'
    # GE43: Der Beleg tritt an den letzten Absatz seines Abschnitts; zurueck
    # kommt die Liste, aus der das Schema seinen 'citation'-Eintrag baut.
    # Sieben der neun Leistungen tragen keine Quelle - sie erklaeren kein Recht.
    daten['quellen'] = _quellen_einsetzen(daten)
    daten['objektart_label'] = _OBJEKTART_LABELS.get(roh['objektart'], '')
    # Standardwerte, damit Template und View nie auf ein fehlendes Feld
    # pruefen muessen - sieben der acht Leistungen setzen keines davon.
    daten['label'] = daten.get('label') or daten['name']
    daten['preistabelle'] = daten.get('preistabelle') or 'entruempelung'
    daten['modifikatoren'] = bool(roh.get('modifikatoren'))
    # G11: Das Template rendert eine **Liste** von Vergleichen, weil
    # /entruempelung-kosten/ zwei traegt. Das alte Einzelfeld 'vergleich'
    # bleibt gueltig und wird hier eingereiht - sonst muesste jede der sechs
    # Leistungen, die schon einen hat, gleichzeitig umgeschrieben werden.
    daten['vergleiche'] = _vergleiche(daten)
    return daten


def _vergleiche(daten):
    """Vergleiche einer Leistung als Liste, mit Anker je Tabelle.

    Der Anker wird aus der Reihenfolge gebildet (``vergleich``,
    ``vergleich-2``, …) und landet als ``id`` am Fazit-Block. Zwei Bloecke mit
    derselben ``id`` waeren ein doppeltes Sprungziel (Regel 10); ``check_seo``
    faengt das ab, aber erst nach dem Deploy waere es sichtbar.
    """
    roh = daten.get('vergleiche') or daten.get('vergleich')
    if not roh:
        return []
    liste = list(roh) if isinstance(roh, (list, tuple)) else [roh]
    # Ein zweiter Vergleich auf derselben Seite (/entruempelung-kosten/).
    # Bewusst ein eigenes Feld statt einer Liste im Datensatz: So bleiben die
    # sechs vorhandenen Vergleiche unveraendert, und wer einen dritten
    # ergaenzen will, sieht sofort, dass hier nachzuziehen ist.
    if daten.get('vergleich_2'):
        liste.append(daten['vergleich_2'])
    aus = []
    for i, v in enumerate(liste):
        v = dict(v)
        v['anker'] = 'vergleich' if i == 0 else 'vergleich-%d' % (i + 1)
        aus.append(v)
    return aus


def alle_leistungen():
    """Alle Leistungsseiten in Reihenfolge – für Navigation, Sitemap, llms.txt."""
    return [leistung(slug) for slug in _SERVICE_DATA]


def beispiel_preise(slug):
    """Die durchgerechneten Beispiele einer Leistung.

    Der Preis kommt aus ``berechne_preis()`` – demselben Code, den der Wizard
    spiegelt und der Server beim Versand noch einmal rechnet. Eine von Hand
    geschätzte Beispielzahl wäre die vierte Preisquelle im Projekt und würde
    beim nächsten Satzwechsel als Erstes falsch.
    """
    daten = leistung(slug)
    if not daten:
        return []
    aus = []
    for b in daten.get('beispiele', []):
        preis, details = berechne_preis(**b['args'])
        aus.append({
            'titel': b['titel'],
            'beschreibung': b['beschreibung'],
            'preis': preis,
            'preis_txt': f'{euro(preis)} €',
            # Der sichtbare Rechenweg (A12). Er entsteht in berechne_preis()
            # waehrend der Rechnung, ist hier also zwangsläufig derselbe Weg,
            # der zu genau diesem Preis gefuehrt hat.
            'schritte': details['schritte'],
        })
    return aus
