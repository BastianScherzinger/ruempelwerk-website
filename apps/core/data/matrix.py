# -*- coding: utf-8 -*-
"""Leistung × Stadt — die Matrixseiten aus A13, Charge 1 und Charge 2.

**Was hier NICHT passieren darf.** Die Versuchung ist 9 Leistungen × 53 Städte
= 477 Seiten. Genau dieser Griff hat dem Projekt schon einmal 131 Landingpages
eingebracht, von denen Google 159 mit „Gefunden – zurzeit nicht indexiert"
quittiert hat. Deshalb ist dieses Modul bewusst klein und wächst nur nach
einer Messung: Charge 1 sind **fünf Seiten für Leipzig**.

**Charge 2 ist seit dem 02.10.2026 gebaut (EIG396)** — die Sperre hing an der
Indexmessung, und die ist erfüllt: Am 29./30.09.2026 waren laut Search Console
91 von 91 Sitemap-URLs indexiert, darunter alle fünf Leipzig-Seiten. Gebaut
wurde trotzdem nicht die volle Charge, sondern nur, wo die Search Console
Nachfrage zeigt: **Haushaltsauflösung in Halle, Magdeburg und Dresden**
(„haushaltsauflösung halle“ 184 Impr., „… halle saale“ 143, „… magdeburg“ 115,
„… dresden preise“ 55). Wohnungsauflösung oder Nachlass in diesen Städten
hatten in ``seo-geo-plan/baseline-queries-2026-08.csv`` je höchstens elf
Impressionen — zu wenig für eine eigene Seite.

**Optionale Felder seit Charge 2:** ``beispiele`` (Eingaben für
``berechne_preis()``, gerechnet mit dem Standortnachlass der Stadt — ersetzt
die allgemeinen Beispiele der Leistung), ``bebauung`` (ersetzt den
Gebäudebestand aus ``city_lokal.py`` auf dieser Seite; ``''`` blendet ihn aus,
wenn er dort nicht belegt ist) und ``quellen`` je Abschnitt (``(Stelle, URL)``,
sichtbar unter dem Abschnitt wie auf den Stadtseiten).

**Die Regel für einen neuen Eintrag:** mindestens vier echte
Unterscheidungsmerkmale, sonst wird die Seite nicht gebaut. Vier davon liefert
``matrix()`` von selbst (Ortsteile, Wertstoffhof, Sperrmüllregelung und
Gebäudebestand aus ``city_lokal.py``, dazu Reaktionszeit und Regionalleiter aus
``cities.py``/``AUTOR_META``). Was hier von Hand dazukommt, ist der Teil, den
keine Datenbank liefert: **warum diese Leistung in dieser Stadt anders läuft.**
Umformulierte Varianten desselben Absatzes zählen nicht — das ist nachgemessen
worden und senkt die Ähnlichkeitszahl nicht.

**Keine Preiszahl in diesem Modul.** Im Text stehen dieselben Platzhalter wie in
``services.py`` (``{haus_ab}``, ``{wohnung_rate}``, ``{preisstand}`` …), gefüllt
aus ``pricing.py``. Ein literales ``{`` im Fließtext lässt ``str.format()``
scheitern — Absicht, ein stiller Ausfall wäre schlimmer.

**Dieses Modul darf nichts aus ``apps.core`` importieren** (Zirkel über
``context_processors``) — dieselbe Regel wie für alle Module unter ``data/``.
"""
import functools

from .cities import _CITY_DATA, leiter_key as _leiter_key
from .city_lokal import lokal, stand as _lokal_stand
from .firma import STRASSE as _FIRMA_STRASSE
from .pricing import berechne_preis as _berechne_preis, euro as _euro
from .services import _fuellen, _platzhalter, leistung
from .stand import deutsch as _stand_deutsch
from .zusagen import ANTWORT as _ANTWORT

# Recherchestand der Quellen, die Charge 2 in den Abschnitten nennt (02.10.2026
# an den Originalseiten nachgelesen). ISO ist die Quelle, der Text wird daraus
# gerechnet - wie in city_lokal.py.
QUELLEN_STAND_ISO = '2026-10'
QUELLEN_STAND = _stand_deutsch(QUELLEN_STAND_ISO)

# Wer die Stadt betreut, steht seit dem 27.08.2026 in cities.py und haengt dort
# am **branch** - damit ist jede der 54 Staedte abgedeckt und nicht nur die
# sechs mit Matrixseite. Hier stand bis dahin eine zweite, slug-basierte Liste
# derselben Zuordnung; bei einer neuen Stadt waeren es zwei Stellen gewesen.


_MATRIX_DATA = {
    # ══════════════════════════════════════════════════════════════════════
    # LEIPZIG — Charge 1
    # ══════════════════════════════════════════════════════════════════════
    'haushaltsaufloesung': {
        'leipzig': {
            'h1_em': 'Festpreis, auch im Altbau ohne Aufzug',
            'hero_sub': (
                'Kompletter Hausstand in Leipzig — vom Gründerzeitaltbau in '
                'Schleußig bis zur Plattenbauwohnung in Grünau. Wir kennen die '
                'Treppenhäuser und rechnen sie nicht nachträglich drauf. '
                'Festpreis ab {haus_ab} €.'),
            'answer': (
                'Eine Haushaltsauflösung in Leipzig kostet bei Rümpelwerk '
                'Mitteldeutschland ab {haus_ab} € und wird darüber nach Wohnfläche '
                'berechnet ({haus_rate} € je m²). Der Zuschlag für einen Altbau ohne '
                'Aufzug wird bei der Besichtigung besprochen und im Festpreisangebot '
                'verbindlich genannt. Termin vor Ort in {response}. '
                'Preisstand: {preisstand}.'),
            'abschnitte': [
                {
                    'id': 'altbau',
                    'titel': 'Warum eine Leipziger Altbauwohnung mehr Volumen hat, als der Grundriss sagt',
                    'absaetze': [
                        'Leipzig hat den größten zusammenhängenden Gründerzeitbestand '
                        'Deutschlands. In Schleußig, Gohlis, Plagwitz und Connewitz sind '
                        'Deckenhöhen um 3,50 m die Regel. Für eine Haushaltsauflösung '
                        'heißt das: Dieselben 90 m² Wohnfläche enthalten rund ein Drittel '
                        'mehr Luftraum als ein Neubau — und dieser Raum ist meist genutzt. '
                        'Deckenhohe Schränke, Vertikos, Bücherwände bis zur Stuckleiste.',

                        'Wir rechnen trotzdem nach Quadratmetern und nicht nach '
                        'Kubikmetern. Das ist für Sie die ehrlichere Zahl, weil Sie sie '
                        'vorher nachprüfen können — die Wohnfläche steht im Mietvertrag, '
                        'der Rauminhalt nirgends. Was die Höhe wirklich kostet, steckt im '
                        'Füllgrad, den Sie im Rechner selbst einstellen.',

                        'Der zweite Punkt ist das Treppenhaus. Ein Leipziger Altbau der '
                        'Jahrhundertwende hat selten einen Aufzug, dafür oft vier '
                        'Vollgeschosse und ein ausgebautes Dachgeschoss. Der Zuschlag je '
                        'Stockwerk steht offen in der Preistabelle und entfällt, sobald ein '
                        'Aufzug da ist. Auf einen nachträglichen „Erschwerniszuschlag", den '
                        'niemand vorher beziffern kann, verzichten wir.',
                    ],
                },
                {
                    'id': 'entsorgung',
                    'titel': 'Wohin der Hausrat in Leipzig geht',
                    'absaetze': [
                        'Zuständig ist die Stadtreinigung Leipzig. Was verwertbar ist, geht '
                        'in die Wiederverwendung; der Rest wird getrennt und über zugelassene '
                        'Betriebe entsorgt. Sie bekommen die Entsorgungsnachweise auf Wunsch '
                        'zur Wohnungsübergabe mit — bei einer Auflösung im Auftrag einer '
                        'Erbengemeinschaft ist das regelmäßig gefragt.',

                        'Die Wertstoffhöfe der Stadt nehmen Privatanlieferungen nur gegen '
                        'Nachweis an, dass Sie in Leipzig gemeldet sind. Wer die Wohnung '
                        'eines verstorbenen Angehörigen auflöst und selbst auswärts wohnt, '
                        'steht damit vor einem praktischen Problem. Für uns ist es keines: '
                        'Wir entsorgen gewerblich und brauchen Ihre Meldebescheinigung nicht.',
                    ],
                },
                {
                    'id': 'anfahrt',
                    'titel': 'Halteverbot, Hof und Anfahrt',
                    'absaetze': [
                        'In den dicht bebauten Vierteln — Südvorstadt, Waldstraßenviertel, '
                        'Schleußig — ist der Stellplatz vor dem Haus das eigentliche '
                        'Nadelöhr. Wo nötig, beantragen wir die Halteverbotszone und '
                        'stellen die Schilder mit dem gesetzlichen Vorlauf auf. Das '
                        'besprechen wir bei der Besichtigung und nennen es im Festpreisangebot.',

                        'In Grünau, Paunsdorf und Mockau ist die Lage umgekehrt: Aufzug '
                        'vorhanden, dafür enge Flure und Aufzugskabinen, in die ein '
                        'Dreisitzer nicht hineingeht. Das kostet Zeit statt Stockwerke — '
                        'auch das nennen wir im Festpreisangebot.',
                    ],
                },
            ],
            'faq': [
                ['Was kostet eine Haushaltsauflösung in Leipzig?',
                 'Ab {haus_ab} €, darüber {haus_rate} € je m² Wohnfläche. Ein typisches '
                 'Reihenhaus mit {haus_qm} m² liegt bei {haus_beispiel}. Zuschläge für '
                 'Stockwerk, Füllgrad und Sonderabfall stehen offen in der Tabelle; den '
                 'genauen Betrag rechnet Ihnen der Rechner auf dieser Seite aus. '
                 'Preisstand {preisstand}.'],
                ['Gibt es einen Aufschlag für Altbau ohne Aufzug?',
                 'Ja, aber er ist beziffert und steht vorher fest: Der Zuschlag hängt am '
                 'Stockwerk und entfällt, sobald ein Aufzug vorhanden ist. Er gilt für '
                 'Wohnungen und Keller. Einen unbezifferten „Altbauzuschlag" gibt es bei '
                 'uns nicht.'],
                ['Wie schnell sind Sie in Leipzig vor Ort?',
                 'Termin vor Ort in {response}. Leipzig gehört zu unserem Einsatzgebiet, '
                 'die Anfahrt ist kurz, und für '
                 'Servicegebietsstädte ziehen wir {rabatt} % vom Preis ab.'],
                ['Kaufen Sie Möbel oder Hausrat an?',
                 'Nein. Wir kaufen nichts an und rechnen auch nichts gegen. Der Grund ist '
                 'Ihre Sicherheit: Ein Betrieb, der Wertanrechnung verspricht, hat ein '
                 'Interesse daran, den Wert niedrig anzusetzen. Was in der Wohnung '
                 'gefunden wird, gehört Ihnen — Sie behalten alles, '
                 'was Sie behalten wollen.'],
                ['Bekomme ich Nachweise für die Wohnungsübergabe?',
                 'Ja. Auf Wunsch bekommen Sie die Entsorgungsnachweise und eine '
                 'Bestätigung der besenreinen Übergabe. Bei Erbengemeinschaften und '
                 'Nachlassverfahren ist das der Punkt, an dem es sonst hakt.'],
            ],
            'seo_title': 'Haushaltsauflösung Leipzig ab {haus_ab} € | Rümpelwerk',
            'seo_description': (
                'Haushaltsauflösung in Leipzig zum Festpreis ab {haus_ab} €. Altbau ohne '
                'Aufzug, Halteverbot, Nachweis. Termin vor Ort in {response}.'),
            'seo_keywords': (
                'Haushaltsauflösung Leipzig, Haushaltsauflösung Leipzig Kosten, '
                'Haushalt auflösen Leipzig, Haushaltsauflösung Firma Leipzig'),
        },

        # ══════════════════════════════════════════════════════════════════
        # HALLE (SAALE) — Charge 2 (02.10.2026, EIG396)
        # Suchabsicht: "haushaltsauflösung halle (saale)" - nicht "entrümpelung
        # halle" (Startseite/Stadtseite). Eigenes Vokabular: Firmensitz,
        # Saale vs. Westfalen, was die HWS-Abfuhr NICHT nimmt, Team Sperrungen.
        # Quellen (02.10.2026 nachgelesen):
        #   https://halle.de/leben-in-halle/klimaschutz-und-umwelt/abfall-und-abwasser/abfall-abc/sperrmuell
        #   https://hws-halle.de/produkte-dienstleistungen/entsorgung/sperrmuell-elektrogeraete
        #   https://halle.de/serviceportal/dienstleistungen/leistung/strassensperrung-wegen-umzug-beantragen/391549757
        # Firmensitz aus firma.py (Platzhalter firma_strasse; die PLZ bleibt weg,
        # check_seo prueft PLZ+Ort als Adressschreibweise).
        # ══════════════════════════════════════════════════════════════════
        'halle': {
            'h1_em': 'Festpreis vom Betrieb aus Halle',
            'hero_sub': (
                'Den ganzen Hausstand auflösen — vom Altbau im Paulusviertel bis '
                'zur Wohnung in Neustadt. Unser Firmensitz liegt in der Stadt, die '
                'Besichtigung ist kostenlos. Festpreis ab {haus_ab} €.'),
            'answer': (
                'Eine Haushaltsauflösung in Halle (Saale) kostet bei Rümpelwerk '
                'Mitteldeutschland ab {haus_ab} € für ein Haus ({haus_rate} € je m²) '
                'und ab {wohnung_ab} € für eine Wohnung. Weil Halle im Servicegebiet '
                'liegt, ziehen wir {rabatt} % ab. Der Betrieb sitzt in der '
                '{firma_strasse}; Termin vor Ort in {response}. '
                'Preisstand: {preisstand}.'),
            'abschnitte': [
                {
                    'id': 'sitz',
                    'titel': 'Ein Betrieb mit Sitz in Halle',
                    'absaetze': [
                        'Rümpelwerk Mitteldeutschland hat seinen Sitz in der '
                        '{firma_strasse} in Halle. Für eine '
                        'Haushaltsauflösung in der Stadt heißt das vor allem: kurze '
                        'Wege zur Besichtigung. Termin vor Ort in {response}; den '
                        'Festpreis nennen wir bei diesem Termin, nicht am Telefon.',

                        'Gemeint ist Halle an der Saale. Der Nachlass von {rabatt} %, '
                        'den wir für Orte im Servicegebiet abziehen, gilt hier — für '
                        'Halle in Westfalen nicht. Der Preisrechner auf dieser Seite '
                        'unterscheidet die beiden Orte, wenn Sie die Adresse eintragen.',
                    ],
                },
                {
                    'id': 'hws',
                    'titel': 'Was die HWS kostenlos abholt — und was bei einer Auflösung übrig bleibt',
                    'absaetze': [
                        'Die Hallesche Wasser und Stadtwirtschaft (HWS) holt einmal im '
                        'Jahr Sperrmüll gebührenfrei ab, bis zu zwei Kubikmeter je '
                        'Person, die im Haushalt lebt. Bei einem Einpersonenhaushalt '
                        'sind das zwei Kubikmeter. Eine Haushaltsauflösung räumt '
                        'dagegen alles: Möbel, Hausrat, Keller und Dachboden.',

                        'Wichtiger als die Menge ist, was die Abfuhr gar nicht '
                        'mitnimmt. Laut Stadt gehören Elektroaltgeräte, Linoleum und '
                        'in Säcken, Kartons oder anderen Behältnissen verpackte '
                        'Kleinteile nicht zum Sperrmüll. Genau das füllt bei einer '
                        'Auflösung Schränke und Schubladen: Geschirr, Bücher, '
                        'Kleidung, Papiere.',

                        'Große Elektrogeräte wie Kühlschrank und Waschmaschine holt die '
                        'HWS aus Privathaushalten kostenfrei ab, aber auf eigenen '
                        'Antrag. Teile über 2,20 × 1,50 × 0,75 m oder über 70 kg nimmt '
                        'sie nur auf schriftlichen Antrag gegen Gebühr. Bei uns ist das '
                        'ein Räumtag: Elektrogeräte, Schadstoffe und Sperriges werden '
                        'vor Ort getrennt und getrennt entsorgt.',
                    ],
                    'quellen': [
                        ('Stadt Halle, Sperrmüll',
                         'https://halle.de/leben-in-halle/klimaschutz-und-umwelt/abfall-und-abwasser/abfall-abc/sperrmuell'),
                        ('HWS, Sperrmüll und Elektrogeräte',
                         'https://hws-halle.de/produkte-dienstleistungen/entsorgung/sperrmuell-elektrogeraete'),
                    ],
                },
                {
                    'id': 'halteverbot',
                    'titel': 'Halteverbot in Halle: 14 Tage Vorlauf beim Team Sperrungen',
                    'absaetze': [
                        'Wo vor dem Haus kein Platz für den Wagen ist, braucht es ein '
                        'Halteverbot. Zuständig ist in Halle das Team Sperrungen der '
                        'Stadt, Am Stadion 5. Der Antrag muss mindestens 14 Tage vorher '
                        'dort sein, die Schilder müssen drei volle Tage vor dem Räumtag '
                        'stehen — der Tag des Aufstellens zählt nicht mit.',

                        'Zum Antrag gehört ein Verkehrszeichenplan im Maßstab 1:500, '
                        'den eine Verkehrssicherungsfirma erstellt. Stellen darf ihn '
                        'auch eine beauftragte Fachfirma mit Ihrer Vollmacht. Wenn die '
                        'Straße es verlangt, übernehmen wir das und nennen die Kosten im '
                        'Festpreisangebot — Sie müssen dafür nicht selbst zur Stadt.',
                    ],
                    'quellen': [
                        ('Stadt Halle, Straßensperrung wegen Umzug',
                         'https://halle.de/serviceportal/dienstleistungen/leistung/strassensperrung-wegen-umzug-beantragen/391549757'),
                    ],
                },
            ],
            # Eingaben fuer berechne_preis(), gerechnet MIT stadtort - der
            # Standortnachlass erscheint als eigener Schritt im Rechenweg.
            'beispiele': [
                {
                    'titel': 'Zweiraumwohnung in Halle-Neustadt, 48 m², 4. OG mit Aufzug',
                    'beschreibung': 'Ein voller Hausstand auf kleiner Fläche. Mit '
                                    'Aufzug entfällt der Stockwerkzuschlag.',
                    'args': {'objektart': 'wohnung', 'qm': 48, 'stockwerk': '4og',
                             'aufzug': True, 'fuellgrad': 'voll'},
                },
                {
                    'titel': 'Altbauwohnung im Paulusviertel, 85 m², 2. OG ohne Aufzug',
                    'beschreibung': 'Normal möbliert, im Keller ein paar Farbeimer '
                                    'und Batterien.',
                    'args': {'objektart': 'wohnung', 'qm': 85, 'stockwerk': '2og',
                             'fuellgrad': 'mittel', 'sonderabfall': 'wenige'},
                },
                {
                    'titel': 'Doppelhaushälfte in Dölau, 110 m², mittel',
                    'beschreibung': 'Wohnräume, Keller, Dachboden und Garage in '
                                    'einem Auftrag.',
                    'args': {'objektart': 'haus', 'qm': 110, 'fuellgrad': 'mittel'},
                },
            ],
            'faq': [
                ['Was kostet eine Haushaltsauflösung in Halle (Saale)?',
                 'Ein Haus ab {haus_ab} €, darüber {haus_rate} € je m² Wohnfläche; eine '
                 'Wohnung ab {wohnung_ab} €, darüber {wohnung_rate} € je m². Etage ohne '
                 'Aufzug, Füllgrad und Sonderabfall kommen als bezifferte Zuschläge '
                 'dazu, und für Halle ziehen wir {rabatt} % ab. Die drei Beispiele auf '
                 'dieser Seite sind damit gerechnet. Preisstand {preisstand}.'],
                ['Reicht nicht die kostenlose Sperrmüllabfuhr der HWS?',
                 'Für einzelne Möbel ja — einmal im Jahr bis zu zwei Kubikmeter je '
                 'Person im Haushalt, gebührenfrei. Für einen ganzen Haushalt nicht, '
                 'weil verpackte Kleinteile und Elektroaltgeräte nicht zum Sperrmüll '
                 'gehören. Dafür brauchen Sie dann Wertstoffmarkt, Elektroabholung und '
                 'Restmülltonne zusätzlich.'],
                ['Wer beantragt das Halteverbot?',
                 'Das sprechen wir bei der Besichtigung ab. In Halle geht der Antrag mindestens 14 Tage '
                 'vorher an das Team Sperrungen der Stadt; die Schilder stehen drei '
                 'volle Tage vor dem Räumtag.'],
                ['Wo sitzt Rümpelwerk in Halle?',
                 'In der {firma_strasse} in Halle. Gemeint ist Halle an der '
                 'Saale — für Halle in Westfalen gilt der Standortnachlass nicht.'],
                ['Nehmen Sie Kühlschrank und Waschmaschine mit?',
                 'Ja. Elektrogroßgeräte gehören zur Haushaltsauflösung und werden '
                 'getrennt entsorgt. Die HWS holt sie ebenfalls kostenfrei ab, aber auf '
                 'eigenen Antrag und zu einem eigenen Termin — bei uns ist es derselbe '
                 'Räumtag.'],
            ],
            'seo_title': 'Haushaltsauflösung Halle (Saale) ab {haus_ab} € | Rümpelwerk',
            'seo_description': (
                'Haushaltsauflösung in Halle (Saale) zum Festpreis ab {haus_ab} €, Betrieb '
                'mit Sitz in Halle. HWS-Regeln, Halteverbot, Termin vor Ort in {response}.'),
            'seo_keywords': (
                'Haushaltsauflösung Halle, Haushaltsauflösung Halle Saale, '
                'Haushalt auflösen Halle, Haushaltsauflösungen Halle (Saale)'),
        },

        # ══════════════════════════════════════════════════════════════════
        # MAGDEBURG — Charge 2 (02.10.2026, EIG396)
        # Eigenes Vokabular: SAB-Kontingent mit Elektrogeraeten, was stehen
        # bleibt, 1-m3-Grenze der Hoefe, Herkunftsnachweis, gemeinnuetzige
        # Abnehmer, Strassenverkehrsbehoerde An der Steinkuhle.
        # Quellen (02.10.2026 nachgelesen):
        #   https://www.magdeburg.de/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Recycling-und-Entsorgung/Sperrm%C3%BCll/
        #   https://www.magdeburg.de/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Recycling-und-Entsorgung/Wertstoffh%C3%B6fe/
        #   https://www.magdeburg.de/index.php?object=tx,698.8844&ModID=10&FID=37.809.1
        # 'bebauung' bewusst leer: Der Text in city_lokal.py ("1945 fast
        # vollstaendig zerstoert", "wenige Gruenderzeitinseln") ist ohne Quelle
        # und fuer Stadtfeld Ost zweifelhaft - auf dieser Seite nicht zeigen.
        # ══════════════════════════════════════════════════════════════════
        'magdeburg': {
            'h1_em': 'Festpreis, Termin nach Absprache',
            'hero_sub': (
                'Den ganzen Hausstand in Magdeburg auflösen — von Stadtfeld bis '
                'Ottersleben, mit Möbeln, Elektrogeräten und dem Inhalt jeder '
                'Schublade. Besichtigung kostenlos, Festpreis ab {haus_ab} €.'),
            'answer': (
                'Eine Haushaltsauflösung in Magdeburg kostet bei Rümpelwerk '
                'Mitteldeutschland ab {haus_ab} € für ein Haus ({haus_rate} € je m²) '
                'und ab {wohnung_ab} € für eine Wohnung. Magdeburg liegt im '
                'Servicegebiet, wir ziehen {rabatt} % ab. Den verbindlichen Festpreis '
                'nennen wir bei der kostenlosen Besichtigung; Termin vor Ort in '
                '{response}. Preisstand: {preisstand}.'),
            'abschnitte': [
                {
                    'id': 'sab',
                    'titel': 'Was die Sperrmüllabfuhr in Magdeburg mitnimmt — und was stehen bleibt',
                    'absaetze': [
                        'Der Städtische Abfallwirtschaftsbetrieb (SAB) holt für jeden '
                        'Magdeburger Haushalt zweimal im Jahr bis zu zwei Kubikmeter '
                        'Sperrmüll gebührenfrei ab, alternativ einmal bis zu vier. '
                        'Anders als etwa in Halle nimmt die Abfuhr Elektroaltgeräte und '
                        'Schrott in haushaltsüblicher Menge gleich mit.',

                        'Stehen bleibt laut Stadt, was bei einer Auflösung in Schränken '
                        'und Kellern steckt: verpackte Kleinteile, Geschirr, '
                        'Pappkartons, Hausmüll und Tapetenreste, dazu Farbeimer, '
                        'Schadstoffe, Sanitärkeramik und Bauabfälle wie Türen, Laminat '
                        'oder Heizkörper. Den Abholtermin legt der SAB fest und schickt '
                        'ihn per Postkarte; wer einen eigenen Termin will, zahlt 50 € '
                        'Servicegebühr.',
                    ],
                    'quellen': [
                        ('Stadt Magdeburg, Sperrmüll',
                         'https://www.magdeburg.de/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Recycling-und-Entsorgung/Sperrm%C3%BCll/'),
                    ],
                },
                {
                    'id': 'hoefe',
                    'titel': 'Selbst zum Wertstoffhof: die Grenze von einem Kubikmeter',
                    'absaetze': [
                        'Bis zu einem Kubikmeter Sperrmüll nehmen die Höfe Hängelsberge, '
                        'Cracauer Anger und Silberbergweg gebührenfrei an — allerdings '
                        'nur von Haushalten, die an die Magdeburger Abfallentsorgung '
                        'angeschlossen sind. Mehr auf einmal nimmt nur Hängelsberge in '
                        'der Königstraße, und dann gegen Gebühr. Wer anliefert, muss im '
                        'Zweifel die Herkunft des Abfalls nachweisen, notfalls mit dem '
                        'Ausweis.',

                        'Für Erben, die selbst nicht in Magdeburg wohnen, ist das der '
                        'Haken: Jede Fahrt bringt gebührenfrei höchstens einen '
                        'Kubikmeter weg. Wir entsorgen gewerblich und in einem Zug; die '
                        'Mengengrenze der Höfe betrifft Sie dann nicht.',

                        'Brauchbares muss nicht auf den Hof. Die Stadt verweist selbst '
                        'auf gemeinnützige Stellen wie AQB, Help 2007 e.V. und Soziale '
                        'Mitte e.V., die Möbel bis hin zum Hausrat annehmen und an '
                        'Bedürftige weitergeben. Was davon in Frage kommt, besprechen '
                        'wir bei der Besichtigung.',
                    ],
                    'quellen': [
                        ('Stadt Magdeburg, Wertstoffhöfe',
                         'https://www.magdeburg.de/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Recycling-und-Entsorgung/Wertstoffh%C3%B6fe/'),
                        ('Stadt Magdeburg, Sperrmüll',
                         'https://www.magdeburg.de/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Recycling-und-Entsorgung/Sperrm%C3%BCll/'),
                    ],
                },
                {
                    'id': 'halteverbot',
                    'titel': 'Halteverbot in Magdeburg: Antrag bei der Straßenverkehrsbehörde',
                    'absaetze': [
                        'Für Schilder vor dem Haus ist in Magdeburg die '
                        'Straßenverkehrsbehörde zuständig, An der Steinkuhle 6. '
                        'Beantragt wird mindestens 14 Tage vorher, mit einem '
                        'Verkehrszeichenplan und den Angaben zu Ort, Zeitraum und Datum. '
                        'Die Schilder müssen mindestens drei Tage vor dem Räumtag '
                        'stehen, und aufstellen darf sie nur eine beauftragte '
                        'Absperrfirma.',

                        'Ein Halteverbot lässt sich in Magdeburg also nicht in letzter '
                        'Minute organisieren. Braucht die Straße eines, sagen wir es bei '
                        'der Besichtigung und sprechen ab, wer Antrag und Absperrfirma '
                        'übernimmt.',
                    ],
                    'quellen': [
                        ('Stadt Magdeburg, Verkehrszeichen für Möbelumzug',
                         'https://www.magdeburg.de/index.php?object=tx,698.8844&ModID=10&FID=37.809.1'),
                    ],
                },
            ],
            'bebauung': '',
            'beispiele': [
                {
                    'titel': 'Dreiraumwohnung in Sudenburg, 70 m², 3. OG ohne Aufzug, voll',
                    'beschreibung': 'Jedes Möbelstück geht über das Treppenhaus, die '
                                    'Schränke sind voll.',
                    'args': {'objektart': 'wohnung', 'qm': 70, 'stockwerk': '3og',
                             'fuellgrad': 'voll'},
                },
                {
                    'titel': 'Einraumwohnung in Buckau, 38 m², Erdgeschoss, leicht',
                    'beschreibung': 'Wenig Hausrat im Erdgeschoss: kein '
                                    'Stockwerkzuschlag, kein Füllgradaufschlag.',
                    'args': {'objektart': 'wohnung', 'qm': 38, 'fuellgrad': 'leicht'},
                },
                {
                    'titel': 'Reihenhaus in Reform, 105 m², mittel',
                    'beschreibung': 'Wohnräume, Keller und Dachboden, dazu einzelne '
                                    'Farbreste in der Garage.',
                    'args': {'objektart': 'haus', 'qm': 105, 'fuellgrad': 'mittel',
                             'sonderabfall': 'wenige'},
                },
            ],
            'faq': [
                ['Was kostet eine Haushaltsauflösung in Magdeburg?',
                 'Ein Haus ab {haus_ab} € ({haus_rate} € je m²), eine Wohnung ab '
                 '{wohnung_ab} € ({wohnung_rate} € je m²). Füllgrad, Etage ohne Aufzug '
                 'und Sonderabfall sind bezifferte Zuschläge; für Magdeburg ziehen wir '
                 '{rabatt} % ab. Preisstand {preisstand}.'],
                ['Holt der SAB nicht alles kostenlos ab?',
                 'Nur Sperrmüll, und nur im Kontingent: zweimal zwei oder einmal vier '
                 'Kubikmeter im Jahr je Haushalt, Elektroaltgeräte und Schrott '
                 'inklusive. Verpackte Kleinteile, Geschirr, Kartons, Farbeimer und '
                 'Bauabfälle nimmt die Abfuhr nicht mit. Bei einer kompletten '
                 'Auflösung bleibt deshalb ein Rest, den jemand anders wegbringen muss.'],
                ['Kann ich selbst zum Wertstoffhof fahren?',
                 'Ja, bis zu einem Kubikmeter Sperrmüll gebührenfrei, wenn der Haushalt '
                 'an die Magdeburger Abfallentsorgung angeschlossen ist. Größere Mengen '
                 'nimmt nur Hängelsberge gegen Gebühr. Für einzelne Stücke ist das die '
                 'günstigere Lösung.'],
                ['Wie lange vorher muss das Halteverbot beantragt werden?',
                 'Mindestens 14 Tage vor dem Räumtag, bei der Straßenverkehrsbehörde der '
                 'Stadt. Die Schilder stellt eine Absperrfirma mindestens drei Tage '
                 'vorher auf. Darum kümmern wir uns, wenn die Straße es verlangt.'],
                ['Was passiert mit gut erhaltenen Möbeln?',
                 'Was noch brauchbar ist, muss nicht entsorgt werden. Die Stadt '
                 'Magdeburg nennt dafür gemeinnützige Stellen wie AQB, Help 2007 e.V. '
                 'und Soziale Mitte e.V. Angekauft oder gegengerechnet wird bei uns '
                 'nichts.'],
            ],
            'seo_title': 'Haushaltsauflösung Magdeburg ab {haus_ab} € | Rümpelwerk',
            'seo_description': (
                'Haushaltsauflösung in Magdeburg zum Festpreis ab {haus_ab} €: was der SAB '
                'nicht mitnimmt, Halteverbot, Elektrogeräte. Termin vor Ort in {response}.'),
            'seo_keywords': (
                'Haushaltsauflösung Magdeburg, Haushalt auflösen Magdeburg, '
                'Haushaltsauflösung Magdeburg Kosten, Wohnungsauflösung Magdeburg'),
        },

        # ══════════════════════════════════════════════════════════════════
        # DRESDEN — Charge 2 (02.10.2026, EIG396)
        # Suchabsicht: "haushaltsauflösung dresden preise/kosten/termine".
        # Deshalb steht hier der Preisaufbau (alle Zahlen als Platzhalter aus
        # pricing.py) und der ehrliche Vergleich mit der Stadtreinigung.
        # Quellen (02.10.2026 nachgelesen):
        #   https://www.srdresden.de/ueber-uns/wertstoffhoefe/
        #   https://www.srdresden.de/aktuelles/detail/ohne-abzocke-sperrmuell-von-zu-hause-entsorgen-lassen
        #   https://www.dresden.de/de/stadtraum/planen/stadtentwicklung/stadterneuerung/stadtteile/gorbitz.php
        #   https://www.dresden.de/de/stadtraum/planen/stadtentwicklung/stadterneuerung/stadtteile/prohlis.php
        #   https://www.dresden.de/de/rathaus/dienstleistungen/umzug-moebeltransport.php
        # 'bebauung' bewusst leer: Der Text in city_lokal.py nennt Striesen
        # "weitgehend erhalten" - ohne Quelle; der belegte Teil (Gorbitz,
        # Prohlis) steht stattdessen im Abschnitt 'viertel'.
        # ══════════════════════════════════════════════════════════════════
        'dresden': {
            'h1_em': 'Preise offen, Zuschläge vorher beziffert',
            'hero_sub': (
                'Was eine Haushaltsauflösung in Dresden kostet, steht hier vor dem '
                'ersten Anruf: Grundpreis je m², jeder Zuschlag und drei '
                'durchgerechnete Beispiele aus Gorbitz, der Neustadt und Klotzsche. '
                'Festpreis ab {haus_ab} €.'),
            'answer': (
                'Eine Haushaltsauflösung in Dresden kostet bei Rümpelwerk '
                'Mitteldeutschland ab {haus_ab} € für ein Haus und ab {wohnung_ab} € '
                'für eine Wohnung. Gerechnet wird nach Wohnfläche — {haus_rate} € '
                'beziehungsweise {wohnung_rate} € je m² —, dazu kommen bezifferte '
                'Zuschläge; für Dresden ziehen wir {rabatt} % ab. Termin vor Ort in '
                '{response}. Preisstand: {preisstand}.'),
            'abschnitte': [
                {
                    'id': 'preis',
                    'titel': 'Woraus sich der Preis in Dresden zusammensetzt',
                    'absaetze': [
                        'Der Grundpreis hängt an der Wohnfläche: {haus_rate} € je m² '
                        'für ein Haus, mindestens {haus_ab} €, und {wohnung_rate} € je '
                        'm² für eine Wohnung, mindestens {wohnung_ab} €. Darauf wirkt '
                        'der Füllgrad als Faktor — von {fuellgrad_leicht} für einen '
                        'leichten bis {fuellgrad_voll} für einen vollen Haushalt.',

                        'Dazu kommen zwei Zuschläge, beide beziffert: für eine Etage '
                        'ohne Aufzug {stockwerk_min_txt} € bis {stockwerk_max_txt} € '
                        '(nur bei Wohnungen und Kellern) und für Sonderabfälle wie '
                        'Farben, Lacke oder Batterien {sonderabfall_wenige_txt} € oder '
                        '{sonderabfall_viele_txt} €. Weil Dresden zu unserem '
                        'Servicegebiet gehört, ziehen wir am Ende {rabatt} % ab, nie '
                        'unter den Mindestpreis. Die drei Beispiele auf dieser Seite '
                        'sind genau so gerechnet.',

                        'Verbindlich wird der Preis bei der kostenlosen Besichtigung: '
                        'Dann steht er als Festpreis im Angebot, ein Halteverbot '
                        'eingeschlossen, wenn die Straße eines braucht.',
                    ],
                },
                {
                    'id': 'srd',
                    'titel': 'Stadtreinigung oder Firma: der ehrliche Vergleich',
                    'absaetze': [
                        'Die Stadtreinigung Dresden (SRD) holt Sperrmüll bis vier '
                        'Kubikmeter für 29,37 € vor dem Haus ab, in der Regel innerhalb '
                        'von vier Wochen; als Expressabholung kostet es 88,12 €. Auf den '
                        'fünf Wertstoffhöfen kann jeder Haushalt pro Halbjahr vier '
                        'Kubikmeter kostenlos abgeben, Schadstoffe bis höchstens 25 '
                        'Liter. Wer für Angehörige anliefert, nimmt die Vollmacht der '
                        'Stadt mit.',

                        'Wer nur ein paar Möbel loswerden will und sie selbst an die '
                        'Straße tragen kann, fährt mit der SRD günstiger als mit uns. '
                        'Eine Haushaltsauflösung ist etwas anderes: Ausräumen, Tragen, '
                        'Trennen und der Inhalt aller Schränke, der kein Sperrmüll ist.',

                        'Die SRD warnt selbst vor Dienstleistern, die mit günstigen '
                        'Festpreisen werben und vor Ort teure Zuschläge aufschlagen. '
                        'Deshalb stehen unsere Zuschläge oben offen, bevor jemand zur '
                        'Besichtigung kommt.',
                    ],
                    'quellen': [
                        ('Stadtreinigung Dresden, Wertstoffhöfe',
                         'https://www.srdresden.de/ueber-uns/wertstoffhoefe/'),
                        ('SRD, Sperrmüll von zu Hause',
                         'https://www.srdresden.de/aktuelles/detail/ohne-abzocke-sperrmuell-von-zu-hause-entsorgen-lassen'),
                    ],
                },
                {
                    'id': 'viertel',
                    'titel': 'Gorbitz, Prohlis, Neustadt: warum derselbe Quadratmeter unterschiedlich viel kostet',
                    'absaetze': [
                        'Gorbitz entstand ab 1981 und ist das größte Plattenbaugebiet '
                        'Dresdens; Prohlis wuchs in den 1970er-Jahren auf über 10.000 '
                        'Wohnungen, das Wohngebiet Am Koitschgraben kam in den 1980ern '
                        'dazu. Ob ein Block dort einen Aufzug hat, ist von Haus zu Haus '
                        'verschieden — und genau daran hängt der Stockwerkzuschlag: Mit '
                        'Aufzug entfällt er ganz.',

                        'In einem Altbau ohne Aufzug, etwa in der Äußeren Neustadt, ist '
                        'es umgekehrt: Jede Etage geht über das Treppenhaus, der '
                        'Zuschlag steht vorher fest. Bei einem Einfamilienhaus in '
                        'Klotzsche fällt er gar nicht an; dort gehören Keller, '
                        'Dachboden und Garage zum Auftrag.',
                    ],
                    'quellen': [
                        ('Stadt Dresden, Gorbitz',
                         'https://www.dresden.de/de/stadtraum/planen/stadtentwicklung/stadterneuerung/stadtteile/gorbitz.php'),
                        ('Stadt Dresden, Prohlis',
                         'https://www.dresden.de/de/stadtraum/planen/stadtentwicklung/stadterneuerung/stadtteile/prohlis.php'),
                    ],
                },
                {
                    'id': 'halteverbot',
                    'titel': 'Halteverbot in Dresden: mindestens vier Tage vorher aufgestellt',
                    'absaetze': [
                        'Ein Halteverbot vor dem Haus genehmigt in Dresden das Straßen- '
                        'und Tiefbauamt. Der Antrag soll nach Möglichkeit 14 Tage vor dem '
                        'Termin dort sein; nach der Genehmigung müssen die Schilder '
                        'mindestens vier Tage vorher stehen. Für die Genehmigung kommt '
                        'ein Kostenbescheid, für einen Möbellift zusätzlich eine '
                        'Sondernutzungsgebühr.',

                        'Beantragen dürfen Privatleute und Unternehmen. Braucht Ihre '
                        'Straße ein Halteverbot, sprechen wir bei der Besichtigung ab, '
                        'wer Antrag und Schilder übernimmt.',
                    ],
                    'quellen': [
                        ('Stadt Dresden, Umzug und Möbeltransport',
                         'https://www.dresden.de/de/rathaus/dienstleistungen/umzug-moebeltransport.php'),
                    ],
                },
            ],
            'bebauung': '',
            'beispiele': [
                {
                    'titel': 'Wohnung in Gorbitz, 60 m², 4. OG mit Aufzug, mittel',
                    'beschreibung': 'Normal möbliert. Mit Aufzug entfällt der '
                                    'Stockwerkzuschlag.',
                    'args': {'objektart': 'wohnung', 'qm': 60, 'stockwerk': '4og',
                             'aufzug': True, 'fuellgrad': 'mittel'},
                },
                {
                    'titel': 'Altbauwohnung in der Äußeren Neustadt, 80 m², 3. OG ohne Aufzug, voll',
                    'beschreibung': 'Volle Schränke, im Keller Farben und Lacke.',
                    'args': {'objektart': 'wohnung', 'qm': 80, 'stockwerk': '3og',
                             'fuellgrad': 'voll', 'sonderabfall': 'wenige'},
                },
                {
                    'titel': 'Einfamilienhaus in Klotzsche, 140 m², voll',
                    'beschreibung': 'Wohnräume, Keller, Dachboden und Garage in '
                                    'einem Auftrag.',
                    'args': {'objektart': 'haus', 'qm': 140, 'fuellgrad': 'voll'},
                },
            ],
            'faq': [
                ['Was kostet eine Haushaltsauflösung in Dresden?',
                 'Ein Haus ab {haus_ab} € ({haus_rate} € je m²), eine Wohnung ab '
                 '{wohnung_ab} € ({wohnung_rate} € je m²). Dazu kommen Füllgrad, Etage '
                 'ohne Aufzug und Sonderabfall als bezifferte Zuschläge, und für '
                 'Dresden {rabatt} % Nachlass. Preisstand {preisstand}.'],
                ['Warum ist die Sperrmüllabholung der Stadtreinigung so viel günstiger?',
                 'Weil sie etwas anderes ist: Die SRD holt bis vier Kubikmeter Sperrmüll '
                 'ab, den Sie selbst an die Straße stellen. Ausräumen, Tragen, Trennen '
                 'und alles, was kein Sperrmüll ist, gehören nicht dazu. Für einzelne '
                 'Möbel ist sie die bessere Wahl.'],
                ['Kommen nach der Besichtigung noch Zuschläge dazu?',
                 'Nein. Alle Zuschläge stehen vorher auf dieser Seite und im Rechner, '
                 'und bei der Besichtigung wird daraus ein Festpreis. Einen '
                 'nachträglichen Aufschlag vor Ort gibt es nicht.'],
                ['Wann bekomme ich in Dresden einen Termin?',
                 'Termin vor Ort in {response}. Den Räumtag legen wir bei der '
                 'Besichtigung fest; braucht die Straße ein Halteverbot, planen wir den '
                 'Vorlauf des Straßen- und Tiefbauamts mit ein.'],
                ['Kann ich Hausrat selbst zum Wertstoffhof bringen?',
                 'Sperrmüll ja: Jeder Haushalt darf pro Halbjahr vier Kubikmeter '
                 'kostenlos auf den Höfen der Stadtreinigung abgeben. Wer für '
                 'Angehörige anliefert, nimmt die Vollmacht der Stadt mit.'],
            ],
            'seo_title': 'Haushaltsauflösung Dresden: Preise ab {haus_ab} € | Rümpelwerk',
            'seo_description': (
                'Haushaltsauflösung in Dresden: Preise ab {haus_ab} €, alle Zuschläge '
                'offen, drei Beispiele durchgerechnet. Kostenlos Angebot anfordern.'),
            'seo_keywords': (
                'Haushaltsauflösung Dresden, Haushaltsauflösung Dresden Preise, '
                'Haushaltsauflösung Dresden Kosten, Haushaltsauflösung Dresden Termine'),
        },
    },

    'wohnungsaufloesung': {
        'leipzig': {
            'h1_em': 'besenrein zur Übergabe',
            'hero_sub': (
                'Mietwohnung in Leipzig auflösen — besenrein übergeben, der Räumtermin '
                'richtet sich nach Ihrem Übergabetermin. Mit Halteverbot, wo die Straße keines hergibt. '
                'Festpreis ab {wohnung_ab} €.'),
            'answer': (
                'Eine Wohnungsauflösung in Leipzig kostet bei Rümpelwerk '
                'Mitteldeutschland ab {wohnung_ab} €, darüber {wohnung_rate} € je m². '
                'Der Termin richtet sich nach Ihrer Wohnungsübergabe: Wir räumen so, '
                'dass die Wohnung am vereinbarten Tag besenrein ist — mit '
                'Entsorgungsnachweis, wenn der Vermieter danach fragt. Termin vor Ort '
                'in {response}. Preisstand: {preisstand}.'),
            'abschnitte': [
                {
                    'id': 'uebergabe',
                    'titel': 'Der Übergabetermin ist die eigentliche Frist',
                    'absaetze': [
                        'Bei einer Mietwohnung zählt nicht, wann geräumt wird, sondern dass '
                        'die Wohnung am Übergabetag leer und besenrein ist. Wer den Termin '
                        'reißt, zahlt in Leipzig schnell eine weitere Monatsmiete — auf dem '
                        'hiesigen Markt vermietet die Verwaltung sofort weiter und hält den '
                        'Nachmieter nicht auf.',

                        'Deshalb legen wir den Räumtag bewusst nicht auf den Übergabetag, '
                        'sondern davor. Bleibt etwas offen — eine vergessene Kellerbox, ein '
                        'Schaden, der erst unter dem Schrank sichtbar wird —, ist noch Zeit, '
                        'es zu erledigen. Ob und was das kostet, besprechen wir bei der Besichtigung '
                        'und nennen es im Festpreisangebot.',
                    ],
                },
                {
                    'id': 'kellerbox',
                    'titel': 'Kellerverschlag, Dachboden und Fahrradkeller',
                    'absaetze': [
                        'In Leipziger Mehrfamilienhäusern gehören zur Wohnung fast immer ein '
                        'Kellerverschlag und oft ein Bodenabteil. Beides steht nicht im '
                        'Grundriss, gehört aber zur Mietsache — und wird bei der Übergabe '
                        'kontrolliert. Wir räumen sie mit und rechnen sie nicht als eigenen '
                        'Auftrag ab.',

                        'Was wir dabei regelmäßig finden: Farbeimer, Autobatterien, alte '
                        'Leuchtstoffröhren. Das sind Sonderabfälle, die nicht in den '
                        'Hausmüll dürfen. Im Rechner stellen Sie ein, ob wenige oder viele '
                        'davon dabei sind; der Zuschlag ist beziffert und steht vorher fest.',
                    ],
                },
                {
                    'id': 'strasse',
                    'titel': 'Wo der Wagen steht',
                    'absaetze': [
                        'Karl-Liebknecht-Straße, Bornaische, Georg-Schwarz-Straße: In den '
                        'Leipziger Hauptstraßen gibt es tagsüber keinen freien Stellplatz, '
                        'und Halten in zweiter Reihe blockiert die Straßenbahn. Wo es nötig '
                        'ist, beantragen wir die Halteverbotszone rechtzeitig — die Schilder '
                        'müssen mit Vorlauf stehen, sonst greift das Verbot nicht.',

                        'In den Seitenstraßen von Plagwitz und Lindenau geht es oft über den '
                        'Hof. Das ist meist die bessere Lösung, verlängert aber den Laufweg. '
                        'Beides sehen wir bei der Besichtigung und beziffern es vorher.',
                    ],
                },
            ],
            'faq': [
                ['Was kostet eine Wohnungsauflösung in Leipzig?',
                 'Ab {wohnung_ab} €, darüber {wohnung_rate} € je m². Eine typische Wohnung mit '
                 '{wohnung_qm} m² liegt bei {wohnung_beispiel}. Stockwerk, Füllgrad und '
                 'Sonderabfall kommen als bezifferte Zuschläge dazu. Preisstand {preisstand}.'],
                ['Räumen Sie auch Keller und Dachboden mit?',
                 'Ja, beides gehört zur Wohnung und wird im Festpreisangebot mit genannt. Die Fläche des '
                 'Kellerverschlags rechnen wir nicht zusätzlich als Kellerentrümpelung ab.'],
                ['Kümmern Sie sich um die Halteverbotszone?',
                 'Ja, wo sie nötig ist. Wir beantragen sie und stellen die Schilder mit dem '
                 'vorgeschriebenen Vorlauf auf. Das ist Teil des Angebots.'],
                ['Was ist, wenn der Vermieter Nachweise verlangt?',
                 'Die bekommen Sie. Auf Wunsch stellen wir die Entsorgungsnachweise und '
                 'eine Bestätigung der besenreinen Übergabe aus.'],
            ],
            'seo_title': 'Wohnungsauflösung Leipzig ab {wohnung_ab} € | Rümpelwerk',
            'seo_description': (
                'Wohnungsauflösung in Leipzig zum Festpreis ab {wohnung_ab} €: besenrein '
                'zum Übergabetermin, Keller inklusive. Jetzt Angebot anfordern.'),
            'seo_keywords': (
                'Wohnungsauflösung Leipzig, Wohnung auflösen Leipzig, '
                'Wohnungsauflösung Leipzig Kosten, Wohnungsentrümpelung Leipzig'),
        },
    },

    'kellerentruempelung': {
        'leipzig': {
            'h1_em': 'auch im feuchten Gewölbekeller',
            'hero_sub': (
                'Kellerverschlag, Gewölbekeller, Waschküche: In Leipziger Altbauten '
                'steht seit Jahrzehnten Zeug, das niemand mehr vermisst. Wir holen es '
                'raus — auch wenn es feucht ist. Festpreis ab {keller_ab} €.'),
            'answer': (
                'Eine Kellerentrümpelung in Leipzig kostet bei Rümpelwerk '
                'Mitteldeutschland ab {keller_ab} €, darüber {keller_rate} € je m². Das '
                'ist die günstigste Objektart, weil die Flächen klein sind — der Aufwand '
                'steckt hier nicht in der Menge, sondern im Weg nach oben. Enthalten '
                'sind Transport und Entsorgung, die Übergabe erfolgt besenrein. '
                'Preisstand: {preisstand}.'),
            'abschnitte': [
                {
                    'id': 'gewoelbe',
                    'titel': 'Was einen Leipziger Altbaukeller besonders macht',
                    'absaetze': [
                        'Die Gründerzeithäuser in Plagwitz, Lindenau und Connewitz haben '
                        'Keller mit Ziegelgewölbe, niedriger Scheitelhöhe und schmalen '
                        'Zugängen. Sacktransport statt Rollwagen, gebückt statt aufrecht. '
                        'Das ist der Grund, warum ein 12-m²-Keller mehr Zeit kostet als '
                        '12 m² Wohnzimmer — und warum der Mindestpreis hier greift.',

                        'Dazu kommt die Feuchte. Große Teile der Leipziger Altbaukeller '
                        'liegen nah am Grundwasser; Pappkartons, Spanplatten und Textilien '
                        'sind nach Jahren im Keller nicht mehr trocken. Verschimmelte Sachen '
                        'gehören nicht in den Restmüll und nicht in Ihr Auto. Wir nehmen sie '
                        'geschlossen mit.',
                    ],
                },
                {
                    'id': 'sonderabfall',
                    'titel': 'Was im Keller regelmäßig auftaucht',
                    'absaetze': [
                        'Farb- und Lackreste, Verdünner, Autobatterien, Leuchtstoffröhren, '
                        'alte Ölradiatoren: Der Keller ist der Ort, an dem Sonderabfälle '
                        'jahrzehntelang stehen bleiben. Sie gehören weder in den Hausmüll '
                        'noch auf den normalen Container.',

                        'Im Rechner geben Sie an, ob wenige oder viele davon dabei sind. Der '
                        'Zuschlag ist beziffert und steht vor dem Termin fest — wir schätzen '
                        'ihn nicht hinterher.',
                    ],
                },
                {
                    'id': 'selbst',
                    'titel': 'Wann sich der Wertstoffhof mehr lohnt als wir',
                    'absaetze': [
                        'Wenn Sie in Leipzig gemeldet sind, wenig zu entsorgen haben und ein '
                        'Auto mit Anhängerkupplung: Fahren Sie selbst. Die Stadtreinigung '
                        'Leipzig nimmt Privatanlieferungen an ihren Wertstoffhöfen '
                        'kostenlos an, unter anderem in der Lößniger Straße 7 in Connewitz '
                        'und in der Döllingstraße 29 in Paunsdorf — gegen Nachweis, dass Sie '
                        'in Leipzig gemeldet sind.',

                        'Es lohnt sich nicht mehr, sobald der Keller voll ist, Sperriges '
                        'dabei ist oder Sonderabfall. Dann brauchen Sie mehrere Fahrten, '
                        'einen Anhänger und jemanden, der mit trägt — und der Nachmittag ist '
                        'weg. Wir sagen Ihnen das offen, weil ein Auftrag, den Sie günstiger '
                        'selbst erledigen können, kein guter Auftrag ist.',
                    ],
                },
            ],
            'faq': [
                ['Was kostet eine Kellerentrümpelung in Leipzig?',
                 'Ab {keller_ab} €, darüber {keller_rate} € je m². Ein typischer Keller mit '
                 '{keller_qm} m² liegt bei {keller_beispiel}. Preisstand {preisstand}.'],
                ['Nehmen Sie auch verschimmelte Sachen mit?',
                 'Ja. In feuchten Leipziger Altbaukellern ist das eher die Regel als die '
                 'Ausnahme. Wir transportieren geschlossen ab, damit nichts durchs '
                 'Treppenhaus staubt.'],
                ['Kann ich das nicht selbst zum Wertstoffhof bringen?',
                 'Bei kleinen Mengen ja, und dann ist das die günstigere Lösung — die '
                 'Wertstoffhöfe der Stadtreinigung Leipzig nehmen kostenlos an, wenn Sie in '
                 'Leipzig gemeldet sind. Ab einem vollen Keller, bei Sperrigem oder bei '
                 'Sonderabfall rechnet es sich nicht mehr.'],
                ['Gilt der Stockwerkzuschlag auch nach unten?',
                 'Der Zuschlag hängt am Geschoss der Wohnung, nicht am Keller. Für einen '
                 'reinen Kellerauftrag im Erdgeschosszugang fällt er nicht an.'],
            ],
            'seo_title': 'Kellerentrümpelung Leipzig ab {keller_ab} € | Rümpelwerk',
            'seo_description': (
                'Kellerentrümpelung in Leipzig ab {keller_ab} € zum Festpreis. Gewölbekeller, '
                'Feuchte, Sonderabfall — mit Nachweis. Angebot anfordern.'),
            'seo_keywords': (
                'Kellerentrümpelung Leipzig, Keller entrümpeln Leipzig, '
                'Kellerentrümpelung Leipzig Kosten, Keller ausräumen Leipzig'),
        },
    },

    'nachlassraeumung': {
        'leipzig': {
            'h1_em': 'für Erben, die nicht in Leipzig wohnen',
            'hero_sub': (
                'Nachlass in Leipzig räumen — mit Rücksicht auf das, was bleiben soll, '
                'und mit den Nachweisen, die eine Erbengemeinschaft braucht. '
                'Festpreis ab {wohnung_ab} € für eine Wohnung.'),
            'answer': (
                'Eine Nachlassräumung in Leipzig kostet bei Rümpelwerk '
                'Mitteldeutschland ab {wohnung_ab} € für eine Wohnung und ab {haus_ab} € '
                'für ein Haus. Wir räumen erst, wenn Sie durchgesehen haben — und legen '
                'alles beiseite, was Sie behalten wollen. Was gefunden wird, gehört '
                'Ihnen. Preisstand: {preisstand}.'),
            'abschnitte': [
                {
                    'id': 'entfernung',
                    'titel': 'Wenn die Erben nicht in Leipzig wohnen',
                    'absaetze': [
                        'Das ist der häufigste Fall. Die Wohnung ist in Leipzig, die Erben '
                        'sind es nicht — und jede Fahrt kostet einen Tag. Wir arbeiten '
                        'deshalb so, dass Sie nicht dabei sein müssen: Besichtigung nach '
                        'Absprache mit Hausverwaltung oder Nachbarn, Fotos von allem, was '
                        'persönlich wirkt, Rücksprache vor dem Räumtag.',

                        'Praktisch relevant ist dabei ein Leipziger Detail: Die '
                        'Wertstoffhöfe der Stadt nehmen Privatanlieferungen nur an, wenn '
                        'Sie in Leipzig gemeldet sind. Als auswärtiger Erbe können Sie '
                        'selbst also nicht einmal die Kleinigkeiten wegbringen. Wir '
                        'entsorgen gewerblich; die Frage stellt sich für Sie nicht.',
                    ],
                },
                {
                    'id': 'erbengemeinschaft',
                    'titel': 'Erbengemeinschaft: was schriftlich sein sollte',
                    'absaetze': [
                        'Räumen darf, wer verfügungsbefugt ist. Bei mehreren Erben heißt das '
                        'in der Regel: gemeinsam. Wir brauchen keinen Erbschein, aber eine '
                        'klare Ansage, wer beauftragt — sonst steht am Ende die Frage im '
                        'Raum, wer den Auftrag eigentlich erteilt hat.',

                        'Was Sie von uns bekommen, ist die Gegenseite davon: '
                        'Entsorgungsnachweise, eine Bestätigung der besenreinen Übergabe und '
                        'auf Wunsch Fotos vom Zustand vor und nach der Räumung. Innerhalb '
                        'einer Erbengemeinschaft ist das oft wichtiger als der Preis.',
                    ],
                },
                {
                    'id': 'persoenliches',
                    'titel': 'Unterlagen, Fotos, Schmuck',
                    'absaetze': [
                        'Wir werfen nichts weg, was persönlich sein könnte. Dokumente, '
                        'Fotoalben, Briefe, Schmuck und Bargeld werden aussortiert und '
                        'übergeben — auch dann, wenn Sie nichts davon erwartet haben. Das '
                        'ist bei uns kein Sonderwunsch, sondern Teil des Auftrags.',

                        'Was wir nicht tun: ankaufen oder gegenrechnen. Wir sind ein '
                        'Räumbetrieb und kein Händler. Das Festpreisangebot kommt vor dem Räumen, und '
                        'was gefunden wird, gehört Ihnen — genau das ist der Grund, warum '
                        'wir das Ankaufsgeschäft bewusst nicht machen.',
                    ],
                },
            ],
            'faq': [
                ['Was kostet eine Nachlassräumung in Leipzig?',
                 'Für eine Wohnung ab {wohnung_ab} € ({wohnung_rate} € je m²), für ein Haus ab '
                 '{haus_ab} € ({haus_rate} € je m²). Preisstand {preisstand}.'],
                ['Muss ich als Erbe bei der Räumung dabei sein?',
                 'Nein. Viele unserer Auftraggeber wohnen nicht in Leipzig. Wir stimmen '
                 'Besichtigung und Zugang mit Hausverwaltung oder Nachbarn ab und '
                 'sprechen vor dem Räumtag durch, was bleibt.'],
                ['Was passiert mit Unterlagen und persönlichen Dingen?',
                 'Sie werden aussortiert und Ihnen übergeben — Dokumente, Fotos, Schmuck, '
                 'Bargeld. Wir kaufen nichts an und rechnen nichts gegen.'],
                ['Bekomme ich Nachweise für das Nachlassgericht oder die Miterben?',
                 'Ja: Entsorgungsnachweise, Übergabebestätigung und auf Wunsch Fotos vom '
                 'Zustand vorher und nachher.'],
                ['Wie schnell können Sie in Leipzig anfangen?',
                 'Termin vor Ort in {response}. Der Räumtermin '
                 'richtet sich danach, wann Sie durchgesehen haben — dabei drängen wir nicht.'],
            ],
            'seo_title': 'Nachlassräumung Leipzig ab {wohnung_ab} € | Rümpelwerk',
            'seo_description': (
                'Nachlassräumung in Leipzig zum Festpreis ab {wohnung_ab} €. Für auswärtige '
                'Erben, mit Entsorgungsnachweis. Jetzt Angebot anfordern.'),
            'seo_keywords': (
                'Nachlassräumung Leipzig, Nachlass auflösen Leipzig, '
                'Entrümpelung Erbe Leipzig, Haushaltsauflösung Todesfall Leipzig'),
        },
    },

    'gewerbeentruempelung': {
        'leipzig': {
            'h1_em': 'Ladenlokal, Büro, Halle',
            'hero_sub': (
                'Gewerbeflächen in Leipzig räumen — vom Ladenlokal an der '
                'Karl-Liebknecht-Straße bis zur Hallenfläche im Leipziger Westen. '
                'Festpreis ab {gewerbe_ab} €. Nach Absprache auch außerhalb der '
                'Öffnungszeiten.'),
            'answer': (
                'Eine Gewerbeentrümpelung in Leipzig kostet bei Rümpelwerk '
                'Mitteldeutschland ab {gewerbe_ab} €, darüber {gewerbe_rate} € je m² — '
                'der günstigste Quadratmeterpreis, weil Gewerbeflächen offen und gut '
                'befahrbar sind. Nach Absprache räumen wir außerhalb der '
                'Öffnungszeiten, damit der Betrieb weiterläuft. Termin vor Ort in {response}. '
                'Preisstand: {preisstand}.'),
            'abschnitte': [
                {
                    'id': 'flaechen',
                    'titel': 'Leipziger Gewerbeflächen sind sehr unterschiedlich',
                    'absaetze': [
                        'Ein Ladenlokal in der Südvorstadt, ein Büro in der Innenstadt und '
                        'eine Halle in Plagwitz oder Lindenau sind drei verschiedene '
                        'Aufträge. Das Ladenlokal hat Ladeneinbauten, die zurückgebaut '
                        'werden müssen; das Büro hat Aktenbestände; die Halle hat Volumen, '
                        'aber eine Rampe.',

                        'Der Quadratmeterpreis ist bei Gewerbe deshalb niedriger als bei '
                        'Wohnraum — offene Flächen, kurze Wege, meist ebenerdig oder mit '
                        'Lastenaufzug. Was den Preis bewegt, ist nicht die Fläche, sondern '
                        'der Rückbau: Ladenbau, Trennwände, verschraubte Regalanlagen.',
                    ],
                },
                {
                    'id': 'akten',
                    'titel': 'Akten und Datenträger',
                    'absaetze': [
                        'Geschäftsunterlagen dürfen nicht im Container landen. Für Akten und '
                        'Datenträger brauchen Sie eine Vernichtung nach Schutzklasse, nicht '
                        'eine Entsorgung. Sagen Sie uns vorher Bescheid, wenn Aktenbestände '
                        'dabei sind — wir trennen sie ab und lassen sie gesondert behandeln.',

                        'Ebenso wichtig sind die Aufbewahrungsfristen: Handels- und '
                        'Steuerunterlagen müssen sechs beziehungsweise zehn Jahre '
                        'aufbewahrt werden. Was noch in der Frist ist, wird nicht vernichtet, '
                        'sondern eingelagert oder übergeben. Diese Entscheidung treffen Sie, '
                        'nicht wir.',
                    ],
                },
                {
                    'id': 'termin',
                    'titel': 'Wann geräumt wird',
                    'absaetze': [
                        'Bei laufendem Betrieb räumen wir nach Absprache außerhalb der Öffnungszeiten. In '
                        'der Leipziger Innenstadt ist das ohnehin oft die einzige Möglichkeit '
                        '— die Fußgängerzonen sind nur in festen Zeitfenstern befahrbar, und '
                        'für die Anlieferung gelten eigene Regeln.',

                        'Bei einer Geschäftsaufgabe zählt dagegen meist das Datum der '
                        'Schlüsselübergabe an den Vermieter. Wir legen den Räumtag davor, '
                        'damit für Nacharbeiten Luft bleibt — dieselbe Vorkehrung wie bei '
                        'einer Wohnungsübergabe, aus demselben Grund.',
                    ],
                },
            ],
            'faq': [
                ['Was kostet eine Gewerbeentrümpelung in Leipzig?',
                 'Ab {gewerbe_ab} €, darüber {gewerbe_rate} € je m². Eine typische Fläche mit '
                 '{gewerbe_qm} m² liegt bei {gewerbe_beispiel}. Preisstand {preisstand}.'],
                ['Können Sie außerhalb der Öffnungszeiten räumen?',
                 'Ja, nach Absprache. In der Leipziger Innenstadt ist das wegen '
                 'der Befahrbarkeit der Fußgängerzonen häufig ohnehin nötig.'],
                ['Was passiert mit Akten und Datenträgern?',
                 'Die werden abgetrennt und gesondert behandelt, das weitere Vorgehen '
                 'stimmen wir mit Ihnen ab. Was noch in der Aufbewahrungsfrist ist, '
                 'wird nicht vernichtet; das entscheiden Sie.'],
                ['Bekomme ich Entsorgungsnachweise für die Buchhaltung?',
                 'Ja. Gewerbliche Abfälle sind nachweispflichtig; Sie bekommen die '
                 'Nachweise und eine Rechnung mit ausgewiesener Umsatzsteuer.'],
            ],
            'seo_title': 'Gewerbeentrümpelung Leipzig ab {gewerbe_ab} € | Rümpelwerk',
            'seo_description': (
                'Gewerbeentrümpelung in Leipzig ab {gewerbe_ab} €: Ladenlokal, Büro, Halle. '
                'Auch außerhalb der Öffnungszeiten nach Absprache. Angebot anfordern.'),
            'seo_keywords': (
                'Gewerbeentrümpelung Leipzig, Büroauflösung Leipzig, '
                'Ladenlokal räumen Leipzig, Geschäftsauflösung Leipzig'),
        },
    },
}


def matrix_ablauf(daten):
    """Der Ablauf einer Leistung **in dieser Stadt** - fuer Text und Schema (G8).

    **Warum es diese Funktion gibt.** Die fuenf Matrixseiten hatten ein
    ``FAQPage``, aber kein ``HowTo`` - als einzige Seitenklasse des Projekts.
    Die Leistungsseiten haben es seit A3, die 54 Stadtseiten seit dem 21.08.2026.
    Ein ``HowTo`` ist die Form, in der Google und die Antwortmaschinen einen
    Ablauf ueberhaupt als Ablauf erkennen.

    **Regel 12 gilt.** Diese Liste speist den sichtbaren Abschnitt *und* das
    Schema. Ein ``HowTo``, dessen Schritte von den sichtbaren abweichen, ist ein
    Verstoss gegen Googles Regeln zu strukturierten Daten - genau daran ist die
    FAQ der Stadtseiten schon einmal auseinandergelaufen (6 im Schema,
    5 sichtbar).

    **Warum aus ``leistung['ablauf']`` und nicht aus ``stadt_ablauf()``.**
    Der Ablauf einer Kellerentruempelung unterscheidet sich von dem einer
    Gewerbeentruempelung; der Ablauf in Leipzig unterscheidet sich von dem in
    Halle kaum. Die Leistung ist also die Achse, an der sich der Ablauf wirklich
    aendert - und sie haelt die fuenf Seiten untereinander unterschiedlich.
    ``stadt_ablauf()`` waere auf allen fuenf Leipzig-Seiten wortgleich gewesen
    und haette die Aehnlichkeit hochgetrieben, die A13 muehsam unter 0,80
    gedrueckt hat.

    Stadtspezifisch sind genau **zwei** Saetze: die Reaktionszeit im ersten
    Schritt und der zustaendige Entsorger im letzten. Beide Angaben stehen
    ohnehin schon auf der Seite (Regionalleiter-Notiz und Ortsangaben), bringen
    also kaum neues Vokabular mit - nachgemessen mit ``jaccard_matrix.py``.
    """
    l, stadt = daten['leistung'], daten['stadt']
    schritte = [dict(s) for s in l.get('ablauf', ())]
    if not schritte:
        return []

    if stadt.get('randgebiet'):
        zusatz = (f"Für {stadt['name']} stimmen wir Termin und Anfahrt "
                  f"vorher persönlich ab.")
    else:
        # Antworten ist nicht Hinfahren (Regel 24, EIG79): Der Satz redet von
        # der Rückmeldung, also ANTWORT - nicht vom Termin vor Ort ('response').
        zusatz = (f"In {stadt['name']} melden wir uns in "
                  f"{_ANTWORT} zurück.")
    schritte[0]['text'] = '%s %s' % (schritte[0]['text'], zusatz)

    ort = daten.get('lokal') or {}
    traeger = (ort.get('traeger') or '').strip()
    if traeger:
        schritte[-1]['text'] = (
            '%s Entsorgt wird über zugelassene Wege; zuständiger '
            'Entsorger in %s ist %s.' % (schritte[-1]['text'], stadt['name'],
                                         traeger))
    return schritte


def matrix_beispiele(daten):
    """Die durchgerechneten Ortsbeispiele einer Matrixseite - oder ``[]``.

    Baugleich zu ``city_lokal.beispiele()``: In ``_MATRIX_DATA`` stehen nur die
    *Eingaben*, Preis und Rechenweg liefert ``berechne_preis()``. Gerechnet
    wird mit ``stadtort`` - der Standortnachlass erscheint damit als eigener
    Schritt, genau wie im Rechner, wenn der Besucher die Stadt eintraegt.
    ``[]`` heisst: Die Seite zeigt die allgemeinen Beispiele der Leistung.
    """
    aus = []
    for b in daten.get('beispiele') or ():
        preis, details = _berechne_preis(stadtort=daten['stadt']['name'],
                                         **b['args'])
        aus.append({
            'titel': b['titel'],
            'beschreibung': b['beschreibung'],
            'preis': preis,
            'preis_txt': f'{_euro(preis)} €',
            'schritte': details['schritte'],
        })
    return aus


def matrix_kombinationen():
    """Alle gebauten (leistung, stadt)-Paare in stabiler Reihenfolge."""
    return [(l_slug, s_slug)
            for l_slug, staedte in _MATRIX_DATA.items()
            for s_slug in staedte]


@functools.lru_cache(maxsize=None)
def matrix(leistung_slug, stadt_slug):
    """Eine Matrixseite mit eingesetzten Preisen – oder ``None``.

    Führt drei Quellen zusammen, ohne eine davon zu kopieren: die Leistung aus
    ``services.py``, die Stadt aus ``cities.py`` und die recherchierten
    Ortsangaben aus ``city_lokal.py``. Genau diese Zusammenführung ist der
    Unterschied zu den entfernten Landingpages – die hatten nur eine Quelle und
    waren untereinander zu 99 % identisch.
    """
    roh = _MATRIX_DATA.get(leistung_slug, {}).get(stadt_slug)
    if not roh:
        return None
    l = leistung(leistung_slug)
    stadt = _CITY_DATA.get(stadt_slug)
    if not l or not stadt:
        return None

    # response gehoert zu den Platzhaltern, damit "{response}" im Text steht
    # und nicht die Zeitangabe abgetippt wird.
    werte = dict(_platzhalter())
    werte['stadt'] = stadt['name']
    werte['response'] = stadt['response']
    # Firmensitz aus firma.py (Regel 25) - Halle nennt ihn im Text.
    werte['firma_strasse'] = _FIRMA_STRASSE

    daten = _fuellen(roh, werte)
    daten['leistung'] = l
    daten['stadt'] = stadt
    daten['stadt_slug'] = stadt_slug
    daten['leistung_slug'] = leistung_slug
    daten['lokal'] = lokal(stadt_slug)
    # Gebaeudebestand: eigener Text der Matrixseite, wenn gesetzt ('' blendet
    # ihn aus), sonst der aus city_lokal.py - siehe Modulkopf.
    if 'bebauung' not in roh:
        daten['bebauung'] = (daten['lokal'] or {}).get('bebauung', '')
    daten['quellen_stand'] = QUELLEN_STAND
    daten['quellen_stand_iso'] = QUELLEN_STAND_ISO
    # Stand je Stadt (city_lokal.stand), nicht der Modulstandard: Die
    # Eintraege von Leipzig, Halle, Magdeburg und Dresden sind im Oktober 2026
    # nachrecherchiert und sollen nicht "August" behaupten.
    daten['lokal_stand_iso'], daten['lokal_stand'] = _lokal_stand(stadt_slug)
    daten['leiter_key'] = _leiter_key(stadt)
    daten['url'] = f'/{leistung_slug}/{stadt_slug}/'
    daten['h1'] = f"{l['name']} {stadt['name']}"
    # Die Frage ueber dem Antwortblock (G2). Abgeleitet statt gepflegt: Die
    # Leistung bringt ihre Frageform schon mit ("Was kostet die
    # Sperrmuell-Entsorgung?"), hier kommt nur der Ort dazu. Ein eigenes Feld
    # je Kombination waere der zweite Satz, der von seiner Quelle abweichen
    # kann - genau das, wogegen Regel 12 geschrieben ist.
    _frage = l.get('answer_frage') or ''
    daten['answer_frage'] = (
        _frage.rstrip('?') + f" in {stadt['name']}?" if _frage else '')
    # Der Brotkrumen ist dreistufig: Dienstleistungen > Leistung > Stadt.
    daten['breadcrumb_name'] = stadt['name']
    # Speist den sichtbaren Ablauf UND das HowTo-Schema (G8, Regel 12).
    # Muss NACH 'leistung'/'stadt'/'lokal' stehen - matrix_ablauf() liest sie.
    daten['ablauf'] = matrix_ablauf(daten)
    return daten
