# -*- coding: utf-8 -*-
"""Recherchierte Ortsangaben je Stadt - der Inhalt, der die Stadtseiten
unterscheidbar macht (F17).

**Warum es diese Datei gibt.** Die Stadtseiten waren (Stand der Messung im August 2026, damals
53 Seiten; heute sind es 57) zu 95 % wortgleich (Jaccard-Median 0,951), und Google hat davon nur 16
indexiert. Die aktuelle Zahl steht in ``cities._CITY_DATA``, nicht hier. Der Versuch,
das mit berechneten Werten zu loesen (Luftlinie zum Standort), hat die
Aehnlichkeit sogar erhoeht: Bei rund 900 Woertern je Seite, von denen 432 auf
allen Seiten identisch sind, verschwindet ein einzelner Satz spurlos.
Gerechnet braucht jede Seite rund 108 nur ihr eigene Woerter.

**Was hier hineingehoert.** Nachpruefbare Angaben, die es nur fuer diese eine
Stadt gibt: der zustaendige Entsorger, die Adresse des Wertstoffhofs, die
Sperrmuellregelung mit Menge, Kosten und Vorlauf, der ortstypische
Gebaeudebestand. Alles am 14.08.2026 recherchiert, ``quelle`` nennt die Stelle,
an der es steht.

**Was hier nicht hineingehoert.** Umformulierter Fuelltext. 41 Varianten
desselben Absatzes senken die Aehnlichkeitszahl und aendern nichts - Google
bewertet den Informationsgehalt, nicht die Wortvielfalt. Lieber ein Feld leer
lassen: Das Template blendet weg, was fehlt.

**Pflege.** Gebuehren und Oeffnungszeiten aendern sich. Die Seite nennt
deshalb sichtbar den Stand und verlinkt die Quelle. Wer aktualisiert, zieht
``STAND`` mit hoch.
"""

# ISO ist die Quelle, der deutsche Text wird daraus gerechnet (G12) -
# damit <time datetime="…"> und der sichtbare Text nie auseinanderlaufen.
from .stand import deutsch as _stand_deutsch

STAND_ISO = '2026-08'
STAND = _stand_deutsch(STAND_ISO)

# Nur Felder, die belegt sind. Ein fehlendes Feld ist kein Fehler - es fehlt
# dann auf der Seite, statt geraten zu werden.
#
#   ortsteile   Die echten Orts- und Stadtteilnamen (Liste)
#   traeger     Wer die Entsorgung macht (Firma/Betrieb, wie sie sich nennt)
#   quelle      URL, unter der die Angaben stehen
#   hof         Wertstoffhof: Adresse, wenn moeglich mit Oeffnungszeiten
#   sperrmuell  Wie die Abholung laeuft: Menge, Kosten, Vorlauf, Anmeldung
#   bebauung    Ortstypischer Gebaeudebestand - was er fuer eine Raeumung heisst
#               (nur noch in zwoelf aelteren Eintraegen (Halle bis Bautzen); seit B7/B8 bei
#               keiner weiteren Stadt, weil unbelegt)
#
# Optionale Felder (IS21/IS22, 01.10.2026):
#
#   lokal_text         Liste aus zwei bis sieben Absaetzen (alle 57 Stadtseiten
#                      haben sie seit 01.10.2026), je ``{'text': ..., 'quellen':
#                      [(Stelle, URL), ...]}``. Nur belegte Fakten ueber den Ort,
#                      **keine Aussage ueber die Firma** (kein "wir"/"unser").
#                      city.html zeigt sie im Lokal-Kasten, jeder Absatz mit
#                      seinen Quellen und dem Stand. ``test_ortsinhalte_2026_10_01.py``
#                      prueft https, Quellen und die Firmenaussage.
#   faq_zusatz         Ein Satz, den ``schema.city_faq_paare`` an die Antwort
#                      "Wohin kommt das Geraeumte" haengt - sichtbar und im
#                      FAQ-Schema aus derselben Liste (Regel 12).
#   hof_quelle         eigene Quelle der Hof-Karte (sonst ``quelle``)
#   sperrmuell_quelle  eigene Quelle der Sperrmuell-Karte (sonst ``quelle``) -
#                      noetig, wenn Hof und Abholung verschiedene Stellen sind
#                      (Bautzen: Veolia und Landkreis)
#   parken_stand_iso   Stand der Parken-Karte, wenn er vom Stand des Eintrags
#                      abweicht (Leipzig: Angaben der Stadt von 09.2024)
#
# Betraege kommunaler Gebuehren stehen im Text als "29,37 €" mit Traeger und
# Stand (Quelle und Stand zeigt die Seite je Karte bzw. je Absatz). Mit "€"
# geschrieben (nie "Euro" ausgeschrieben): Steht das Zeichen im Quelltext dieser
# Datei, sammelt ``check_seo`` den Betrag als belegte Fremdzahl ein (Regel 1) und
# listet ihn sichtbar auf - hier muss also nichts eingetragen werden, nie in
# ``pricing.py``.
#
# ``ortsteile`` hat den Zielwert erst erreichbar gemacht. Nachgemessen fehlten
# jeder Seite rund zehn eigene Woerter; Ortsteilnamen sind das einzige
# Vokabular, das eine Stadtseite mit keiner anderen teilt - und sie treffen
# echte Suchanfragen ("Entruempelung Leipzig Plagwitz"). Nachgeschlagen, nicht
# geraten: ein erfundener Ortsteil ist so falsch wie eine erfundene Gebuehr.
from .pricing import berechne_preis as _berechne_preis, euro as _euro

LOKAL = {

    # ══ Sachsen-Anhalt, Raum Halle ═══════════════════════════════════════
    'halle': {
        'ortsteile': ['Paulusviertel', 'Giebichenstein', 'Kröllwitz',
                      'Trotha', 'Neustadt', 'Silberhöhe', 'Ammendorf',
                      'Nietleben', 'Dölau', 'Büschdorf', 'Diemitz'],
        'traeger': 'Hallesche Wasser und Stadtwirtschaft (HWS)',
        'quelle': 'https://hws-halle.de/produkte-dienstleistungen/entsorgung',
        'hof': 'Drei Wertstoffmärkte: Äußere Hordorfer Straße 12, Äußere '
               'Radeweller Straße 15 und Schieferstraße 2. Geöffnet Mo–Fr '
               '6:00–20:30 Uhr, Sa 7:00–12:00 Uhr.',
        'sperrmuell': ('Einmal im Jahr holt die HWS bis zu 2 m³ je Person im Haushalt '
                       'gebührenfrei ab. Anmeldung über das Online-Formular der HWS '
                       '(Kundenservice 0345 581-4100); ohne Wunschtermin wird der '
                       'Sperrmüll innerhalb von fünf Wochen abgeholt.'),
        # 02.10.2026: bis dahin ein unbelegter Satz ("drei Bauwelten ...").
        # Jetzt die Zensuszahlen des Statistischen Landesamts (Stichtag
        # 15.05.2022), Quelle sichtbar ueber ``bebauung_quellen``.
        'bebauung': ('Fast die Hälfte der Wohnungen in Halle (44,2 %) stammt aus den '
                     'Jahren 1960 bis 1989, gut jede fünfte (22,5 %) aus der Zeit vor '
                     '1919. Am häufigsten liegt eine Wohnung in einem Haus mit 7 bis '
                     '12 Wohnungen (46,3 %), nur jede zehnte in einem Haus mit einer '
                     'einzigen Wohnung (Zensus 2022). Daraus folgen die Rechenbeispiele '
                     'oben: Keller und Wohnung im Altbau ohne Aufzug, Wohnung im '
                     'Block mit Aufzug, Einfamilienhaus mit Keller und Dachboden.'),
        'bebauung_quellen': [
            ('Statistisches Landesamt Sachsen-Anhalt, Zensus 2022, Gebäude und Wohnungen',
             'https://statistik.sachsen-anhalt.de/fileadmin/Bibliothek/Landesaemter/StaLa/startseite/Zensus_2022/Tabellen/15_ST_Regionaltabelle_Geb%C3%A4ude_Wohnungen_Z22.xlsx'),
        ],
        # Die drei Bauwelten aus 'bebauung', durchgerechnet. Hier stehen nur
        # die EINGABEN - den Preis rechnet berechne_preis(), dieselbe Funktion,
        # die der Wizard spiegelt und der Server beim Versand noch einmal
        # ausfuehrt. Eine getippte Beispielzahl waere die naechste Preisquelle.
        'beispiele': [
            {
                'titel': 'Hochkeller im Altbau, 18 m²',
                'beschreibung': 'Der typische Einstieg in der Südlichen Innenstadt oder der'
                ' Südstadt: ein voller Kellerverschlag, Zugang '
                                'über die enge Treppe im Hof.',
                'args': {'objektart': 'keller', 'qm': 18, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Altbauwohnung im Paulusviertel, 68 m², 3. OG ohne Aufzug',
                'beschreibung': 'Normal möbliert. Jedes Möbelstück geht über '
                                'das Treppenhaus – deshalb der Stockwerkzuschlag.',
                'args': {'objektart': 'wohnung', 'qm': 68, 'stockwerk': '3og',
                         'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Plattenbauwohnung in Halle-Neustadt, 62 m², 4. OG mit Aufzug',
                'beschreibung': 'Höher gelegen als die Altbauwohnung und '
                                'trotzdem günstiger: Mit Aufzug entfällt der '
                                'Stockwerkzuschlag vollständig.',
                'args': {'objektart': 'wohnung', 'qm': 62, 'stockwerk': '4og',
                         'aufzug': True, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Einfamilienhaus in Kröllwitz, 130 m², voll',
                'beschreibung': 'Erdgeschoss bis Dachboden samt Keller, dazu '
                                'einzelne Sonderabfälle wie Farben und Lacke.',
                'args': {'objektart': 'haus', 'qm': 130, 'fuellgrad': 'voll',
                         'sonderabfall': 'wenige'},
            },
        ],
        'stand_iso': '2026-10',
        'lokal_text': [
            {'text': ('Alle drei Wertstoffmärkte sind sonn- und feiertags '
                      'geschlossen. Der Markt Äußere Hordorfer Straße 12 '
                      'öffnet von März bis Oktober zusätzlich samstags von 12:30 '
                      'bis 20:30 Uhr und sonntags von 9:00 bis 17:00 Uhr für '
                      'Grünschnitt. Bei Selbstanlieferung von Sperrmüll bleibt der '
                      'erste Kubikmeter gebührenfrei.'),
             'quellen': [('HWS, Wertstoffmärkte',
                          'https://hws-halle.de/produkte-dienstleistungen/wertstoffmarkt/standorte-oeffnungszeiten'),
                         ('Stadt Halle, Sperrmüll',
                          'https://halle.de/leben-in-halle/klimaschutz-und-umwelt/abfall-und-abwasser/abfall-abc/sperrmuell')]},
            {'text': ('Der Termin der Sperrmüllabholung wird mindestens drei Tage '
                      'vorher angekündigt; ein Wunschtermin kostet 20 €. '
                      'Bereitgestellt wird bis 6:00 Uhr am Abholtag, nicht an Sonn- '
                      'und Feiertagen. Teile über 2,20 × 1,50 × 0,75 m oder 70 kg '
                      'werden nur gegen Gebühr auf schriftlichen Antrag abgeholt. Der'
                      ' Kundenservice der HWS ist montags bis donnerstags von 7 bis '
                      '18 Uhr, freitags bis 16 Uhr erreichbar.'),
             'quellen': [('HWS, Sperrmüll bestellen',
                          'https://hws-halle.de/produkte-dienstleistungen/entsorgung/sperrmuell/sperrmuellabholung-beantragen'),
                         ('HWS, Kundenservice',
                          'https://hws-halle.de/produkte-dienstleistungen/kundenservice/kontakt')]},
            {'text': ('Amtlich ordnet halle.de die Stadt in fünf Stadtbezirke (Mitte,'
                      ' Nord, Ost, Süd, West) mit 34 Stadtteilen, darunter '
                      'Giebichenstein, Kröllwitz, Silberhöhe und Büschdorf. Trotha, '
                      'Ammendorf, Neustadt und Lettin sind zusätzlich in zwölf '
                      'Stadtviertel unterteilt. Glaucha ist kein eigener Stadtteil, '
                      'sondern eine ehemalige Vorstadt innerhalb der Südlichen '
                      'Innenstadt.'),
             'quellen': [('Stadt Halle, Stadtteile und Stadtviertel',
                          'https://halle.de/leben-in-halle/stadtentwicklung/stadtteile-und-stadtviertel')]},
            {'text': ('Schadstoffe und Elektroaltgeräte haben in Halle feste Wege: '
                      'Die Schadstoffannahme am Wertstoffmarkt Äußere Hordorfer '
                      'Straße steht zu den regulären Öffnungszeiten offen. '
                      'Große oder schwere Elektroaltgeräte, also Kühl- und '
                      'Haushaltsgroßgeräte sowie Bildschirme, holt die HWS aus '
                      'privaten Haushalten kostenfrei ab; beantragt wird online. '
                      'Mit der Sperrmüllabholung gehen sie nicht mit: Elektroaltgeräte '
                      'zählen in Halle nicht zum Sperrmüll.'),
             'quellen': [('HWS Halle, Standorte und Öffnungszeiten',
                          'https://hws-halle.de/produkte-dienstleistungen/wertstoffmarkt/standorte-oeffnungszeiten'),
                         ('HWS Halle, Sperrmüll und Elektrogeräte',
                          'https://hws-halle.de/produkte-dienstleistungen/entsorgung/sperrmuell-elektrogeraete'),
                         ('Stadt Halle, Sperrmüll',
                          'https://halle.de/leben-in-halle/klimaschutz-und-umwelt/abfall-und-abwasser/abfall-abc/sperrmuell')]},
            {'text': ('Wer Geschirr, Kleinmöbel, Spielzeug oder Fahrräder noch in '
                      'gutem Zustand hat, kann sie in Halle in die „Fundgrube“ '
                      'geben, den begehbaren Second-Hand-Container im '
                      'Einfahrtsbereich des Wertstoffmarkts Äußere Hordorfer Straße '
                      '12, montags bis freitags 15-18 Uhr. Auch auf den Märkten in '
                      'Radewell und in der Schieferstraße wird abgegeben. Die Dinge '
                      'müssen sauber, vollständig und funktionsfähig sein; verkauft '
                      'wird zu niedrigen Preisen ohne Gewinnabsicht.'),
             'quellen': [('HWS Halle, Standorte und Öffnungszeiten',
                          'https://hws-halle.de/produkte-dienstleistungen/wertstoffmarkt/standorte-oeffnungszeiten')]},
        ],
        'faq_zusatz': ('In Halle nehmen die drei Wertstoffmärkte der HWS '
                       'Selbstanlieferungen an; der erste Kubikmeter Sperrmüll ist '
                       'dabei gebührenfrei.'),
    },
    'merseburg': {
        'ortsteile': ['Altenburg', 'Neumarkt', 'Freiimfelde', 'Kötzschen',
                      'Meuschau', 'Geusa', 'Trebnitz', 'Beuna', 'Blösien',
                      'Atzendorf', 'Zscherben'],
        'traeger': 'EGS Saalekreis mbH',
        'quelle': 'https://www.egsaalekreis.de/',
        'hof': 'Annahmestelle (Kleinanlieferbereich) der EGS Saalekreis in '
               'Beuna, Großkaynaer Str. 1. Geöffnet Mo–Fr 7:30–18:00 Uhr, Sa '
               '9:00–12:00 Uhr.',
        'sperrmuell': 'Angeschlossene Haushalte und Gewerbe im Saalekreis '
                      'können einmal im Jahr eine Sperrmüllentsorgung in '
                      'Anspruch nehmen; bis insgesamt 5 m³ im Jahr sind '
                      'kostenfrei. Angemeldet wird über das Sperrmüllformular im '
                      'EntsorgungsPortal der EGS, mindestens 6 Wochen vor dem '
                      'Wunschtermin.',
        'beispiele': [
            {
                'titel': 'Einfamilienhaus, 95 m², voll',
                'args': {'objektart': 'haus', 'qm': 95, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 62 m², 3. OG ohne Aufzug',
                'beschreibung': 'Ohne Aufzug: Der Stockwerkzuschlag macht den '
                                'Unterschied zur Erdgeschosswohnung.',
                'args': {'objektart': 'wohnung', 'qm': 62, 'stockwerk': '3og',
                         'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Wohnung, 80 m², 1. OG',
                'args': {'objektart': 'wohnung', 'qm': 80, 'stockwerk': '1og',
                         'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'lokal_text': [
            {'text': ('Für die Abfallwirtschaft im Saalekreis ist die EGS mit Sitz in '
                      'Merseburg-Beuna zuständig (Großkaynaer Str. 1, Telefon 03461 '
                      '440-0). Der Kleinanlieferbereich ist werktags von 7:30 bis '
                      '18:00 Uhr und samstags von 9:00 bis 12:00 Uhr geöffnet. Weitere '
                      'Standorte mit denselben Zeiten gibt es in Querfurt (Am '
                      'Stadtwege 9), Landsberg-Oppin (Lilienthalstr. 3) und '
                      'Teutschenthal-Bahnhof (Dömikenweg 1); der Bauhof Merbitz nimmt '
                      'dienstags und donnerstags von 14:00 bis 17:00 Uhr nur '
                      'Grünschnitt und Sperrmüll an.'),
             'quellen': [('EGS Saalekreis, Standorte und Öffnungszeiten',
                          'https://www.egsaalekreis.de/')]},
            {'text': ('Angeschlossene Haushalte und Gewerbe dürfen einmal im Jahr '
                      'Sperrmüll abholen lassen; Mengen bis insgesamt 5 m³ im Jahr, '
                      'sogenannte haushaltsübliche Mengen, sind kostenfrei, weitere '
                      'Mengen kostenpflichtig. Gemeldet wird über das '
                      'Sperrmüllformular im EntsorgungsPortal der EGS, mindestens '
                      'sechs Wochen vor dem gewünschten Termin. Schrott sowie '
                      'Elektro- und Elektronikschrott laufen über ein eigenes '
                      'Formular, einzelne Schrottteile dürfen höchstens 2 m lang '
                      'sein.'),
             'quellen': [('EGS Saalekreis, Leistungen',
                          'https://www.egsaalekreis.de/'),
                         ('EGS-EntsorgungsPortal',
                          'https://portal.muellabfuhr-deutschland.de/saalekreis')]},
            {'text': ('Laut merseburg.de gehören zur Stadt die Ortsteile Beuna (seit '
                      '2009), Geusa (seit 2010), Meuschau (seit 1994), Trebnitz (seit '
                      '2003) und Kötzschen. Geusa ist mit 1404 Einwohnern der größte '
                      'Ortsteil; zu ihm zählen Blösien, Atzendorf und Zscherben. '
                      'Altenburg und Neumarkt nennt Wikipedia als 1832 eingemeindete '
                      'Vorstädte, Freiimfelde als Ortsteil im Stadtgebiet.'),
             'quellen': [('Stadt Merseburg, Ortsteile',
                          'https://www.merseburg.de/de/ortsteile.html'),
                         ('Wikipedia, Merseburg (Sekundärquelle)',
                          'https://de.wikipedia.org/wiki/Merseburg')]},
            {'text': ('Pedelecs, Batterien und Farbreste zählt der Landkreis zu den '
                      'Schadstoffen. Eingesammelt werden sie einmal im Jahr vom '
                      'Schadstoffmobil an zentralen Stellen jeder Ortschaft; '
                      'außerhalb der Tour geht es zu den Wertstoffhöfen. Schrott '
                      'und Elektronikschrott holt der Entsorger einmal jährlich am '
                      'Grundstück ab, angemeldet mindestens sechs Wochen vorher; '
                      'Schrottteile dürfen höchstens zwei Meter lang sein, '
                      'Kühlgeräte müssen dicht bereitstehen.'),
             'quellen': [('Landkreis Saalekreis, Abfall entsorgen',
                          'https://www.saalekreis.de/de/leistungsausgabe/leistung/530/abfall_entsorgen.html'),
                         ('Landkreis Saalekreis, Schrott-, Elektro- und Elektronikschrottabfuhr',
                          'https://www.saalekreis.de/de/leistungsausgabe/leistung/703/schrott-_elektro-_und_elektronikschrottabfuhr.html'),
                         ('EGS Saalekreis, Startseite',
                          'https://www.egsaalekreis.de/')]},
            {'text': ('Wird ein Haushalt nach einem Todesfall aufgelöst, liegt die '
                      'Nachlasssache beim Amtsgericht Merseburg in der Geusaer '
                      'Straße 88. Die Wertstoffhöfe in Beuna, Querfurt, '
                      'Teutschenthal-Bahnhof und Oppin nehmen im Bringsystem '
                      'Abfälle an. Für das Räumen selbst hat die EGS getrennte '
                      'Formulare: eines für Sperrmüll, bis insgesamt 5 m³ im Jahr '
                      'kostenfrei, ein eigenes für Schrott und Elektronikschrott.'),
             'quellen': [('Justizportal des Bundes und der Länder, Orts- und Gerichtsverzeichnis (PLZ 06217)',
                          'https://www.justizadressen.nrw.de/de/justiz/gericht?ang=nachlass&plz=06217&ort='),
                         ('EGS Saalekreis, Startseite',
                          'https://www.egsaalekreis.de/')]},
        ],
        'faq_zusatz': ('Das Geräumte lässt sich in Merseburg am Kleinanlieferbereich '
                       'der EGS in Beuna abgeben oder über die Sperrmüllabholung der '
                       'EGS (Anmeldung im EntsorgungsPortal) entsorgen.'),
    },
    'querfurt': {
        'ortsteile': ['Gatterstädt', 'Grockstädt', 'Leimbach', 'Lodersleben',
                      'Ober- und Niederschmon', 'Vitzenburg',
                      'Weißenschirmbach', 'Ziegelroda'],
        'traeger': 'EGS Saalekreis mbH',
        'quelle': 'https://www.saalekreis.de/de/abfall-entsorgung.html',
        'hof': ('Wertstoffhof Querfurt (EGS), Am Stadtwege 9, 06268 Querfurt, '
                'Telefon 03461 440-0: Mo–Fr 7:30–18:00 Uhr, Sa 9–12 Uhr. '
                'Kostenfrei sind unter anderem bis zu 5 m³ Sperrmüll im Jahr sowie '
                'Schrott, Elektroschrott und Strauchschnitt; Bauschutt, Dachpappe, '
                'Bau- und Abbruchholz, Reifen und Mineralwolle kosten extra.'),
        'sperrmuell': ('Alternativ holt die EGS einmal im Jahr bis zu 5 m³ gebührenfrei '
                       'ab: Sperrmüllkarte aus dem Umweltkalender oder Anmeldung im '
                       'EntsorgungsPortal der EGS, mindestens 6 Wochen vor dem '
                       'Wunschtermin.'),
        'beispiele': [
            {
                'titel': 'Scheune, 120 m², voll',
                'args': {'objektart': 'scheune', 'qm': 120, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus, 110 m², voll',
                'args': {'objektart': 'haus', 'qm': 110, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 65 m², 1. OG, mittel',
                'args': {'objektart': 'wohnung', 'qm': 65, 'stockwerk': '1og', 'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.saalekreis.de/de/wertstoffhoefe-detail/adr/1171828,1002,1/wertstoffhof_querfurt.html?con=1171828,1002,de,1',
        'sperrmuell_quelle': 'https://www.saalekreis.de/de/leistungsausgabe/leistung/702/sperrmuell_entsorgen.html',
        'lokal_text': [
            {'text': ('Am Stadtwege 9 steht der Wertstoffhof der '
                      'Entsorgungsgesellschaft Saalekreis (EGS), montags bis '
                      'freitags von 7:30 bis 18:00 Uhr und samstags von 9:00 bis '
                      '12:00 Uhr offen. Nach Angaben des Landkreises sind Sperrmüll '
                      'bis 5 m³ im Jahr, Schrott, Elektroschrott, Papier und Baum- '
                      'und Strauchschnitt dort kostenfrei. Ab dem sechsten '
                      'Kubikmeter Sperrmüll sowie für Bauschutt, Dachpappe, Reifen '
                      'und Mineralwolle wird ein Entgelt verlangt.'),
             'quellen': [('Landkreis Saalekreis, Wertstoffhof Querfurt',
                          'https://www.saalekreis.de/de/wertstoffhoefe-detail/adr/1171828,1002,1/wertstoffhof_querfurt.html?con=1171828,1002,de,1')]},
            {'text': ('Wer den Sperrmüll lieber abholen lässt, hat dazu einmal im '
                      'Jahr bis 5 m³ gebührenfrei Gelegenheit. Bestellt wird mit '
                      'der Sperrmüllkarte aus dem Umweltkalender oder im '
                      'EntsorgungsPortal der EGS, mindestens sechs Wochen vor dem '
                      'Wunschtermin; der genaue Tag kommt spätestens drei Tage '
                      'vorher. Einzelstücke dürfen 1 m³, 2 m Länge oder 50 kg nicht '
                      'überschreiten, Fenster, Türen und Zäune bleiben '
                      'ausgeschlossen.'),
             'quellen': [('Landkreis Saalekreis, Sperrmüll entsorgen',
                          'https://www.saalekreis.de/de/leistungsausgabe/leistung/702/sperrmuell_entsorgen.html'),
                         ('EGS Saalekreis, Startseite',
                          'https://www.egsaalekreis.de/')]},
            {'text': ('Schadstoffe fährt das Umweltmobil des Landkreises einmal '
                      'jährlich an zentrale Standplätze. Als Alternative nehmen die '
                      'Höfe in Beuna, Querfurt und Oppin bis 100 kg kostenfrei an, '
                      'allerdings nur nach Anmeldung beim Umweltamt unter 03461 '
                      '40-1419 oder 40-1447. Kühlgeräte, Waschmaschinen und '
                      'Fernseher gelten als Elektroschrott und können am Hof '
                      'abgegeben oder per EGS-Formular zur Abholung angemeldet '
                      'werden.'),
             'quellen': [('Landkreis Saalekreis, Abfallarten',
                          'https://www.saalekreis.de/de/abfallarten.html'),
                         ('EGS Saalekreis, Startseite',
                          'https://www.egsaalekreis.de/')]},
            {'text': ('Das Stadtgebiet besteht aus acht Ortschaften: Gatterstädt, '
                      'Grockstädt mit Kleineichstädt und Spielberg, Leimbach, '
                      'Lodersleben, Ober- und Niederschmon, Vitzenburg mit '
                      'Liederstädt, Pretitz und Zingst, Weißenschirmbach sowie '
                      'Ziegelroda mit Landgrafroda. Nachlasssachen gehören nach '
                      'Wikipedia (Sekundärquelle) zum Amtsgericht Merseburg, '
                      'Geusaer Straße 88, 06217 Merseburg, dessen Anschrift das '
                      'Justizportal Sachsen-Anhalt führt.'),
             'quellen': [('Stadt Querfurt, Ortschaften',
                          'https://www.querfurt.de/seite/761104/ortschaften-ortsteile.html'),
                         ('Justizportal Sachsen-Anhalt, Anschriftenverzeichnis',
                          'https://justiz.sachsen-anhalt.de/themen/anschriftenverzeichnis'),
                         ('Wikipedia, Amtsgericht Merseburg (Sekundärquelle)',
                          'https://de.wikipedia.org/wiki/Amtsgericht_Merseburg')]},
        ],
        'faq_zusatz': ('Das Geräumte geht in Querfurt an den EGS-Wertstoffhof Am '
                       'Stadtwege 9 (Sperrmüll bis 5 m³ im Jahr kostenfrei) oder über die '
                       'jährliche Sperrmüllabholung des Landkreises.'),
    },
    'weissenfels': {
        'ortsteile': ['Burgwerben', 'Markwerben', 'Langendorf', 'Leißling',
                      'Tagewerben', 'Uichteritz', 'Reichardtswerben',
                      'Großkorbetha', 'Borau', 'Wengelsdorf', 'Schkortleben',
                      'Storkau'],
        'traeger': 'AW SAS – AöR (Abfallwirtschaft Sachsen-Anhalt Süd)',
        'quelle': 'https://www.awsas.de/wertstoffhoefe.html',
        'hof': ('Wertstoffhof Weißenfels, Straße am Wehr, 06667 Weißenfels, '
                'Telefon 03443 279037: Mo und Mi–Fr 10–17:30 Uhr, Sa 9–15 Uhr, '
                'dienstags geschlossen. Über 30 Abfallarten werden angenommen; '
                'Sperrmüll aus Haushalten bleibt bis 2 m³ pro Tag gebührenfrei.'),
        'sperrmuell': ('Abholung online oder telefonisch (034445 223-41, Di und Do): bis '
                       '2 m³ pro Person und Jahr je Haushalt gebührenfrei, höchstens zwei '
                       'Abholungen im Jahr; Bereitstellung bis 6:00 Uhr, frühestens am '
                       'Vorabend. Haushaltsauflösungen sind gebührenpflichtig. Am Hof '
                       'kostet Sperrmüll ab 2 m³ am Tag 50,00 € je m³ (AW SAS, Stand '
                       '10/2026).'),
        'beispiele': [
            {
                'titel': 'Wohnung, 72 m², 2. OG, mittel',
                'args': {'objektart': 'wohnung', 'qm': 72, 'stockwerk': '2og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Gewerbefläche, 300 m², voll, einzelne Schadstoffe',
                'beschreibung': ('Gewerbe wird nach der Grundfläche berechnet. Einzelne '
                                 'Schadstoffe werden mit einem Aufschlag berechnet.'),
                'args': {'objektart': 'gewerbe', 'qm': 300, 'fuellgrad': 'voll', 'sonderabfall': 'wenige'},
            },
            {
                'titel': 'Einfamilienhaus, 115 m², voll',
                'args': {'objektart': 'haus', 'qm': 115, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.awsas.de/wertstoffhoefe.html',
        'sperrmuell_quelle': 'https://www.awsas.de/sperrmuell-auf-abruf.html',
        'lokal_text': [
            {'text': ('Auf dem Wertstoffhof an der Straße am Wehr nimmt die AW SAS '
                      'über 30 Abfallarten an; geöffnet ist er montags sowie '
                      'mittwochs bis freitags von 10:00 bis 17:30 Uhr und samstags '
                      'von 9:00 bis 15:00 Uhr, dienstags bleibt er zu. Sperrmüll '
                      'aus Haushalten bleibt bis 2 m³ pro Tag gebührenfrei. Wer '
                      'Möbel im Auftrag eines Haushalts anliefert, braucht laut '
                      'Benutzungsordnung Vollmacht und Ausweiskopie des '
                      'Eigentümers.'),
             'quellen': [('AW SAS, Wertstoffhöfe',
                          'https://www.awsas.de/wertstoffhoefe.html'),
                         ('AW SAS, Benutzungsordnung der Wertstoffhöfe',
                          'https://www.awsas.de/satzungen/benutzungsordnung-wertstoffhoefe.html')]},
            {'text': ('Ab 2 m³ am Tag werden auf dem Hof 50,00 € je Kubikmeter '
                      'fällig (AW SAS, Stand 10/2026). Die Abholung am Wohnort ist '
                      'mit bis zu 2 m³ pro Person und Jahr gebührenfrei, höchstens '
                      'zweimal jährlich; angemeldet wird online oder dienstags und '
                      'donnerstags unter 034445 223-41. Bereitgestellt wird bis '
                      '6:00 Uhr an der Tonnenstellfläche, Elektrogeräte und '
                      'Altmetall getrennt. Haushaltsauflösungen sind ausdrücklich '
                      'gebührenpflichtig.'),
             'quellen': [('AW SAS, Gebühren bei Selbstanlieferung',
                          'https://www.awsas.de/gebuehren-bei-selbstanlieferung.html'),
                         ('AW SAS, Sperrmüll auf Abruf',
                          'https://www.awsas.de/sperrmuell-auf-abruf.html')]},
            {'text': ('Farben, Lacke und Batterien nimmt der Hof in '
                      'haushaltsüblichen Mengen kostenfrei an; außerhalb der '
                      'Kernstädte fährt zusätzlich das Schadstoffmobil, zweimal im '
                      'Jahr und mit höchstens 10 kg bzw. 10 l je Haushalt. '
                      'Elektroaltgeräte kommen gebührenfrei in die Container der '
                      'Höfe, Datenträger werden dort nicht gelöscht. Altmetall darf '
                      'pro Teil höchstens 1 m lang und 40 kg schwer sein.'),
             'quellen': [('AW SAS, Schadstoffmobil',
                          'https://www.awsas.de/schadstoffmobil.html'),
                         ('AW SAS, Was kommt wohin',
                          'https://www.awsas.de/was-kommt-wo-hin.html')]},
            {'text': ('Brauchbare Kleidung, Schuhe, Bettwäsche und Gardinen gehören '
                      'sauber und trocken in Altkleidercontainer, etwa von DRK, AWO '
                      'oder Malteser, oder auf einen der drei Höfe; verschmutzte '
                      'Stücke zählen zum Restabfall.'),
             'quellen': [('AW SAS, Was kommt wohin',
                          'https://www.awsas.de/was-kommt-wo-hin.html')]},
            {'text': ('Zwölf Ortschaften gehören zur Stadt: Borau, Burgwerben, '
                      'Großkorbetha, Langendorf, Leißling, Markwerben, '
                      'Reichardtswerben, Schkortleben, Storkau, Tagewerben, '
                      'Uichteritz und Wengelsdorf. Nachlassgericht ist das '
                      'Amtsgericht Weißenfels, Friedrichsstraße 18, wo die '
                      'Nachlassabteilung nur nach telefonischer Vereinbarung (03443 '
                      '3840) empfängt.'),
             'quellen': [('Stadt Weißenfels, Ortschaften',
                          'https://www.weissenfels.de/Stadt-Ortschaften/Ortschaften/'),
                         ('Justizportal Sachsen-Anhalt, Anschriftenverzeichnis',
                          'https://justiz.sachsen-anhalt.de/themen/anschriftenverzeichnis'),
                         ('Amtsgericht Weißenfels, Nachlass',
                          'https://www.ag-wsf.sachsen-anhalt.de/service/nachlass')]},
        ],
        'faq_zusatz': ('Das Geräumte geht in Weißenfels auf den AW-SAS-Wertstoffhof '
                       'Straße am Wehr (Sperrmüll bis 2 m³ am Tag kostenfrei) oder über '
                       'die angemeldete Sperrmüllabholung des Burgenlandkreises.'),
    },
    'zeitz': {
        'ortsteile': ['Zangenberg', 'Theißen', 'Luckenau', 'Nonnewitz',
                      'Kayna', 'Würchwitz', 'Geußnitz', 'Pirkau'],
        'traeger': 'AW SAS – AöR (Abfallwirtschaft Sachsen-Anhalt Süd)',
        'quelle': 'https://www.awsas.de/wertstoffhoefe.html',
        'hof': ('Wertstoffhof Zeitz, Friedrich-Degelow-Straße, 06712 Zeitz, '
                'Telefon 03441 2044010: Mo–Mi und Fr 10–17:30 Uhr, Sa 9–15 Uhr, '
                'donnerstags geschlossen. Sperrmüll aus Haushalten bleibt bis 2 m³ '
                'pro Tag gebührenfrei, darüber 50,00 € je m³ (AW SAS, Stand '
                '10/2026).'),
        'sperrmuell': ('Abholung online oder telefonisch (034445 223-41): bis 2 m³ pro '
                       'Person und Jahr je Haushalt gebührenfrei, höchstens zwei '
                       'Abholungen im Jahr. Der Sperrmüll muss bis 6:00 Uhr im '
                       'öffentlichen Raum stehen, nicht auf dem Privatgrundstück. '
                       'Haushaltsauflösungen sind gebührenpflichtig.'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus, 170 m², voll',
                'args': {'objektart': 'haus', 'qm': 170, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 80 m², 3. OG, voll',
                'args': {'objektart': 'wohnung', 'qm': 80, 'stockwerk': '3og', 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Keller, 20 m², voll',
                'args': {'objektart': 'keller', 'qm': 20, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.awsas.de/wertstoffhoefe.html',
        'sperrmuell_quelle': 'https://www.awsas.de/sperrmuell-auf-abruf.html',
        'lokal_text': [
            {'text': ('Die Friedrich-Degelow-Straße führt zum Zeitzer Wertstoffhof '
                      'der AW SAS (Telefon 03441 2044010). Geöffnet ist montags bis '
                      'mittwochs sowie freitags von 10:00 bis 17:30 Uhr, samstags '
                      'von 9:00 bis 15:00 Uhr; donnerstags bleibt das Tor zu. '
                      'Haushaltssperrmüll bis 2 m³ je Tag kostet nichts, darüber '
                      'werden 50,00 € je Kubikmeter berechnet (AW SAS, Stand '
                      '10/2026).'),
             'quellen': [('AW SAS, Wertstoffhöfe',
                          'https://www.awsas.de/wertstoffhoefe.html'),
                         ('AW SAS, Gebühren bei Selbstanlieferung',
                          'https://www.awsas.de/gebuehren-bei-selbstanlieferung.html')]},
            {'text': ('Soll der Sperrmüll abgeholt werden, meldet ihn der Haushalt '
                      'beim Burgenlandkreis-Entsorger online an oder telefonisch '
                      'unter 034445 223-41. Gebührenfrei sind bis zu 2 m³ pro '
                      'Person und Jahr in höchstens zwei Abholungen. Die Möbel '
                      'stehen spätestens um 6:00 Uhr im öffentlichen Bereich, nie '
                      'auf dem Privatgrundstück; Elektrogeräte und Altmetall werden '
                      'getrennt hingestellt.'),
             'quellen': [('AW SAS, Sperrmüll auf Abruf',
                          'https://www.awsas.de/sperrmuell-auf-abruf.html')]},
            {'text': ('Wegen der Gebühren lohnt ein Blick in die Benutzungsordnung: '
                      'Gewerbliche Anlieferung von Sperrmüll durch '
                      'Entrümpelungsfirmen ist nicht kostenfrei, und für '
                      'Haushaltsauflösungen nennt die AW SAS ausdrücklich Gebühren. '
                      'Gefährliche Abfälle in Haushaltsmengen, Elektroaltgeräte und '
                      'Altmetall nimmt der Hof dagegen für Privathaushalte '
                      'gebührenfrei an.'),
             'quellen': [('AW SAS, Benutzungsordnung der Wertstoffhöfe',
                          'https://www.awsas.de/satzungen/benutzungsordnung-wertstoffhoefe.html'),
                         ('AW SAS, Sperrmüll auf Abruf',
                          'https://www.awsas.de/sperrmuell-auf-abruf.html'),
                         ('AW SAS, Was kommt wohin',
                          'https://www.awsas.de/was-kommt-wo-hin.html')]},
            {'text': ('Noch brauchbares Mobiliar kann die CJD Möbelbörse & '
                      'Sozialboutique in der Freiligrathstraße 41a nehmen. Die '
                      'gemeinnützige Einrichtung sammelt Möbel und Kleidung von '
                      'Privatpersonen und Unternehmen und gibt sie an Bedürftige '
                      'ab; laut CJD-Seite ist dienstags und donnerstags von 8:00 '
                      'bis 12:30 Uhr geöffnet.'),
             'quellen': [('CJD, Möbelbörse & Sozialboutique Zeitz',
                          'https://www.cjd.de/de/cjd-moebelboerse-sozialboutique-zeitz')]},
            {'text': ('Zur Stadt gehören die Ortschaften Geußnitz, Kayna, Luckenau, '
                      'Nonnewitz, Pirkau, Theißen, Würchwitz und Zangenberg. Für '
                      'Nachlässe ist das Amtsgericht Zeitz am Herzog-Moritz-Platz 1 '
                      'zuständig (Sekundärquelle Wikipedia für den Bezirk); Anträge '
                      'auf einen Erbschein nimmt dort die Serviceeinheit für '
                      'Nachlasssachen nach Terminvereinbarung auf.'),
             'quellen': [('Stadt Zeitz, Ortschaften',
                          'https://www.zeitz.de/Zeitz-Die-Kleinstadt-/Ortschaften/'),
                         ('Justizportal Sachsen-Anhalt, Anschriftenverzeichnis',
                          'https://justiz.sachsen-anhalt.de/themen/anschriftenverzeichnis'),
                         ('Amtsgericht Zeitz, Nachlass',
                          'https://www.ag-zz.sachsen-anhalt.de/service/nachlass'),
                         ('Wikipedia, Amtsgericht Zeitz (Sekundärquelle)',
                          'https://de.wikipedia.org/wiki/Amtsgericht_Zeitz')]},
        ],
        'faq_zusatz': ('Das Geräumte geht in Zeitz auf den AW-SAS-Wertstoffhof '
                       'Friedrich-Degelow-Straße, über die angemeldete Sperrmüllabholung '
                       'oder – wenn gut erhalten – an die CJD Möbelbörse in der '
                       'Freiligrathstraße 41a.'),
    },
    'naumburg': {
        'ortsteile': ['Bad Kösen', 'Großjena', 'Kleinjena', 'Flemmingen',
                      'Eulau', 'Schulpforte', 'Roßbach', 'Saaleck'],
        'traeger': 'AW SAS – AöR (Abfallwirtschaft Sachsen-Anhalt Süd)',
        'quelle': 'https://www.awsas.de/wertstoffhoefe.html',
        'hof': ('Wertstoffhof Naumburg (Saale), Hallesche Straße 60, 06618 '
                'Naumburg (Saale), Telefon 03445 777783: Mo, Di, Do, Fr 10–17:30 '
                'Uhr, Sa 9–15 Uhr, mittwochs geschlossen.'),
        'sperrmuell': ('Abholung nach Anmeldung (online jederzeit): bis 2 m³ pro Person '
                       'und Jahr je Haushalt gebührenfrei, höchstens zwei Abholungen im '
                       'Jahr; Bereitstellung bis 6:00 Uhr. Haushaltsauflösungen sind '
                       'gebührenpflichtig.'),
        'beispiele': [
            {
                'titel': 'Wohnung, 72 m², 3. OG, mittel',
                'args': {'objektart': 'wohnung', 'qm': 72, 'stockwerk': '3og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Einfamilienhaus in Bad Kösen, 125 m², voll',
                'args': {'objektart': 'haus', 'qm': 125, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Keller, 18 m², voll',
                'args': {'objektart': 'keller', 'qm': 18, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.awsas.de/wertstoffhoefe.html',
        'sperrmuell_quelle': 'https://www.awsas.de/sperrmuell-auf-abruf.html',
        'lokal_text': [
            {'text': ('Hallesche Straße 60 ist die Adresse des Naumburger '
                      'Wertstoffhofs der AW SAS (Telefon 03445 777783). Annahme '
                      'montags, dienstags, donnerstags und freitags von 10:00 bis '
                      '17:30 Uhr, samstags von 9:00 bis 15:00 Uhr, mittwochs ist '
                      'geschlossen. Für Haushalte kostet Sperrmüll bis 2 m³ pro Tag '
                      'nichts; bei Bauabfällen und gemischtem Siedlungsabfall '
                      'werden 55,00 € je Kubikmeter berechnet (AW SAS, Stand '
                      '10/2026).'),
             'quellen': [('AW SAS, Wertstoffhöfe',
                          'https://www.awsas.de/wertstoffhoefe.html'),
                         ('AW SAS, Gebühren bei Selbstanlieferung',
                          'https://www.awsas.de/gebuehren-bei-selbstanlieferung.html')]},
            {'text': ('Für Wohnungsauflösungen gelten diese Mengen: Bis 2 m³ je Tag '
                      'und Haushalt sind am Hof kostenfrei, darüber 50,00 € je '
                      'Kubikmeter. Abgeholt wird nach Anmeldung bis 2 m³ pro Person '
                      'und Jahr; Haushaltsauflösungen führt die AW SAS ausdrücklich '
                      'als gebührenpflichtig. Entrümpelungsfirmen liefern laut '
                      'Benutzungsordnung nicht kostenfrei an.'),
             'quellen': [('AW SAS, Gebühren bei Selbstanlieferung',
                          'https://www.awsas.de/gebuehren-bei-selbstanlieferung.html'),
                         ('AW SAS, Sperrmüll auf Abruf',
                          'https://www.awsas.de/sperrmuell-auf-abruf.html'),
                         ('AW SAS, Benutzungsordnung der Wertstoffhöfe',
                          'https://www.awsas.de/satzungen/benutzungsordnung-wertstoffhoefe.html')]},
            {'text': ('Schadstoffe, die in keine Tonne gehören, nehmen die Höfe in '
                      'haushaltsüblichen Mengen kostenfrei an. Das Schadstoffmobil '
                      'bedient dagegen nur Haushalte außerhalb der Kernstädte '
                      'Naumburg, Weißenfels und Zeitz. Waschmaschinen, Kühlschränke '
                      'und andere Elektroaltgeräte gehören in die gekennzeichneten '
                      'Container des Hofs; eine Datenlöschung übernimmt dort '
                      'niemand.'),
             'quellen': [('AW SAS, Schadstoffmobil',
                          'https://www.awsas.de/schadstoffmobil.html'),
                         ('AW SAS, Was kommt wohin',
                          'https://www.awsas.de/was-kommt-wo-hin.html')]},
            {'text': ('Gut erhaltene Textilien, Schuhe und Heimtextilien dürfen '
                      'sauber und trocken in die Altkleidercontainer, die auch '
                      'gemeinnützige Organisationen wie DRK, AWO und Malteser '
                      'aufstellen, oder direkt auf den Hof; nasse oder zerrissene '
                      'Ware zählt zum Restabfall.'),
             'quellen': [('AW SAS, Was kommt wohin',
                          'https://www.awsas.de/was-kommt-wo-hin.html')]},
            {'text': ('Außer der Kernstadt kennt die Stadtseite 31 Ortsteile, von '
                      'Bad Kösen mit Schulpforte und Saaleck bis Wettaburg und '
                      'Tultewitz; Bad Kösen betreut dabei zehn Ortsteile in einer '
                      'gemeinsamen Verwaltung. Nachlassgericht ist das Amtsgericht '
                      'Naumburg am Markt 7 (Bezirk nach Wikipedia, Sekundärquelle).'),
             'quellen': [('Stadt Naumburg, Einwohner und Ortsteile',
                          'https://www.naumburg.de/de/einwohner.html'),
                         ('Stadt Naumburg, Ortsteile N–Z',
                          'https://www.naumburg.de/de/ortsteile-n-z.html'),
                         ('Justizportal Sachsen-Anhalt, Anschriftenverzeichnis',
                          'https://justiz.sachsen-anhalt.de/themen/anschriftenverzeichnis'),
                         ('Amtsgericht Naumburg, Nachlass',
                          'https://www.ag-nmb.sachsen-anhalt.de/service/nachlass-informationen-und-formulare'),
                         ('Wikipedia, Amtsgericht Naumburg (Saale) (Sekundärquelle)',
                          'https://de.wikipedia.org/wiki/Amtsgericht_Naumburg_(Saale)')]},
        ],
        'faq_zusatz': ('Das Geräumte geht in Naumburg auf den AW-SAS-Wertstoffhof '
                       'Hallesche Straße 60 (Sperrmüll bis 2 m³ am Tag kostenfrei) oder '
                       'über die angemeldete Sperrmüllabholung des Burgenlandkreises.'),
    },
    'sangerhausen': {
        'ortsteile': ['Oberröblingen', 'Riestedt', 'Lengefeld', 'Gonna',
                      'Grillenberg', 'Großleinungen', 'Morungen',
                      'Obersdorf', 'Wettelrode', 'Wippra', 'Wolfsberg',
                      'Breitenbach', 'Horla', 'Rotha'],
        'traeger': 'Eigenbetrieb Abfallwirtschaft Mansfeld-Südharz',
        'quelle': 'https://www.abfallwirtschaft-msh.de/',
        'hof': 'Wertstoffhof Sangerhausen, Oststraße 5, Telefon 03464 2609136. '
               'Geöffnet Mo, Di, Do, Fr 9:00–12:00 und 12:30–16:30 Uhr, Mi und '
               'Sa 9:00–12:00 Uhr. Jedem Haushalt im Landkreis Mansfeld-Südharz '
               'stehen laut Eigenbetrieb je Kalenderjahr zwei gebührenfreie '
               'Anlieferungen zu; Sperrmüll und Grünschnitt werden nur aus dem '
               'Landkreis angenommen.',
        'sperrmuell': 'Gebührenfrei abgeholt werden bis zu 4 m³ im Jahr, verteilt '
                      'auf höchstens zwei Termine (zweimal 2 m³ oder einmal 4 m³). '
                      'Anmeldung im Online-Formular oder mit den '
                      'Sperrmüllabrufkarten aus dem Service-Heft, mindestens drei '
                      'Wochen vor dem Wunschtermin. Einzelstücke dürfen höchstens '
                      '2 × 1 × 0,75 m messen und nicht schwerer als 70 kg sein.',
        'beispiele': [
            {
                'titel': 'Einfamilienhaus, 85 m², voll',
                'beschreibung': 'Wohnräume, Keller und Nebengelass in einem '
                                'Auftrag; der Hauspreis schließt sie ein.',
                'args': {'objektart': 'haus', 'qm': 85, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Keller und Nebengelass, 20 m², voll',
                'args': {'objektart': 'keller', 'qm': 20, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 60 m², 2. OG',
                'beschreibung': 'Normal möbliert, im 2. Obergeschoss ohne '
                                'Aufzug: Der Stockwerkzuschlag ist der '
                                'Unterschied zur Erdgeschosswohnung.',
                'args': {'objektart': 'wohnung', 'qm': 60,
                         'stockwerk': '2og', 'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.abfallwirtschaft-msh.de/index.php/wehoe-lk-msh/wertstoffhof-sangerhausen',
        'sperrmuell_quelle': 'https://www.abfallwirtschaft-msh.de/index.php/entsorgung-sas-lkmsh-hm/sperr-sas-hm',
        'lokal_text': [
            {'text': ('Der Eigenbetrieb Abfallwirtschaft Mansfeld-Südharz betreibt '
                      'den Wertstoffhof Sangerhausen, Oststraße 5 (Telefon 03464 '
                      '2609136): montags, dienstags, donnerstags und freitags von '
                      '9:00 bis 12:00 und von 12:30 bis 16:30 Uhr, mittwochs und '
                      'samstags von 9:00 bis 12:00 Uhr. Weitere Höfe des '
                      'Eigenbetriebs liegen in Hettstedt (Ritteröder Straße) und '
                      'Unterrißdorf (Kreismülldeponie). Sperrmüll und Grünschnitt '
                      'nehmen die Höfe laut Eigenbetrieb nur an, wenn sie aus dem '
                      'Landkreis Mansfeld-Südharz stammen.'),
             'quellen': [('Eigenbetrieb Abfallwirtschaft, Wertstoffhof Sangerhausen',
                          'https://www.abfallwirtschaft-msh.de/index.php/wehoe-lk-msh/wertstoffhof-sangerhausen'),
                         ('Wertstoffhöfe des Eigenbetriebs',
                          'https://www.abfallwirtschaft-msh.de/index.php/wehoe-lk-msh'),
                         ('Eigenbetrieb Abfallwirtschaft, Hinweise zur Anlieferung',
                          'https://www.abfallwirtschaft-msh.de/index.php/anlief-spm-gruen-ph')]},
            {'text': ('Jeder Haushalt hat je Kalenderjahr zwei gebührenfreie '
                      'Anlieferungen, je höchstens 2 m³ Sperrmüll oder 3 m³ '
                      'Grünschnitt; Teil-Anlieferungen sind nicht möglich. Am Hof '
                      'sind die ausgefüllte Sperrmüllkarte des laufenden Jahres, ein '
                      'Wohnsitznachweis wie der Personalausweis und die '
                      'unterschriebene Erklärung zum Freikontingent vorzulegen. '
                      'Ohne Freikontingent kostet Sperrmüll 173,00 € je Tonne '
                      '(Annahmegebühren 2026).'),
             'quellen': [('Eigenbetrieb Abfallwirtschaft, Anlieferung von Sperrmüll und Grünschnitt',
                          'https://www.abfallwirtschaft-msh.de/index.php/anlief-spm-gruen-ph'),
                         ('Abfallgebühren 2026',
                          'https://www.abfallwirtschaft-msh.de/index.php/abfallrecht-lkmsh/abfallgebuehren-uebersicht-2026')]},
            {'text': ('Bei der Abholung sind bis zu 4 m³ im Jahr gebührenfrei, auf '
                      'höchstens zwei Termine verteilt. Angemeldet wird im '
                      'Online-Formular oder mit den Abrufkarten aus dem Service-Heft, '
                      'mindestens drei Wochen vor dem Wunschtermin; üblich sind drei '
                      'bis vier Wochen bis zur Abholung, der Termin kommt spätestens '
                      'drei Tage vorher per E-Mail. Einzelstücke dürfen 2 × 1 × 0,75 m '
                      'und 70 kg nicht überschreiten, ausdrücklich genannt ist ein '
                      'Ecksofa. Die Expressabholung binnen drei Werktagen kostet 75 € '
                      'Vorkasse. Bereitgestellt wird nur das Angemeldete, am Abholtag '
                      'bis 6 Uhr morgens; Fenster, Türen oder Laminat gelten nicht als '
                      'Sperrmüll.'),
             'quellen': [('Eigenbetrieb Abfallwirtschaft, Sperrmüllabholung',
                          'https://www.abfallwirtschaft-msh.de/index.php/entsorgung-sas-lkmsh-hm/sperr-sas-hm')]},
            {'text': ('Gefährliche Haushaltsabfälle werden nur im Bringsystem '
                      'entsorgt: Das Schadstoffmobil fährt zweimal im Jahr seine '
                      'Touren und steht zusätzlich an ausgewählten Samstagen; die '
                      'Annahme ist für Haushalte gebührenfrei. Ungezündetes '
                      'Feuerwerk, Munition und Sprengstoff nimmt es nicht. Bei '
                      'Elektrogeräten zählt der Eigenbetrieb auch einen elektrisch '
                      'höhenverstellbaren Schreibtisch dazu; vier Großgeräte je '
                      'Haushalt und Jahr holt er kostenfrei ab, in höchstens zwei '
                      'Terminen.'),
             'quellen': [('Abfallwirtschaft Mansfeld-Südharz, Gefährliche Abfälle',
                          'https://www.abfallwirtschaft-msh.de/index.php/entsorgung-sas-lkmsh-hm/gefaehrliche-sas-hm'),
                         ('Abfallwirtschaft Mansfeld-Südharz, Elektro-/Elektronikaltgeräte',
                          'https://www.abfallwirtschaft-msh.de/index.php/entsorgung-sas-lkmsh-hm/ealt-sas-hm')]},
            {'text': ('Noch gut erhaltene Möbel nimmt die Möbelbörse der Arbeits- '
                      'und Bildungs-Initiative (ABI) in der Lengefelder Straße 15 '
                      'entgegen, Telefon 03464 5439475; sie gibt die Waren gegen '
                      'ein geringes Entgelt an Menschen mit wenig Einkommen ab; '
                      'gespendet wird direkt beim Projekt, der Träger ist unter '
                      '03464 515197 in der Riestedter Straße 2 zu erreichen. Ein '
                      'Nachlass wird beim Amtsgericht Sangerhausen am Markt 3 '
                      'abgewickelt.'),
             'quellen': [('Abfallwirtschaft Mansfeld-Südharz, Sperrmüll',
                          'https://www.abfallwirtschaft-msh.de/index.php/entsorgung-sas-lkmsh-hm/sperr-sas-hm'),
                         ('Justizportal des Bundes und der Länder, Orts- und Gerichtsverzeichnis (PLZ 06526)',
                          'https://www.justizadressen.nrw.de/de/justiz/gericht?ang=nachlass&plz=06526&ort=')]},
        ],
        'faq_zusatz': ('Das Geräumte nimmt der Wertstoffhof Sangerhausen (Oststraße 5) '
                       'an, sofern es aus dem Landkreis stammt, oder es läuft über '
                       'die Sperrmüllabholung des Eigenbetriebs.'),
    },

    # ══ Sachsen-Anhalt, Raum Magdeburg / Anhalt / Harz ═══════════════════
    'magdeburg': {
        'ortsteile': ['Stadtfeld Ost', 'Stadtfeld West', 'Sudenburg',
                      'Buckau', 'Alte Neustadt', 'Neue Neustadt',
                      'Ottersleben', 'Reform', 'Rothensee', 'Salbke',
                      'Westerhüsen', 'Diesdorf', 'Kannenstieg',
                      'Neu Olvenstedt'],
        'traeger': 'Städtischer Abfallwirtschaftsbetrieb (SAB) Magdeburg',
        'quelle': ('https://www.magdeburg.de/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Recycling-und-Entsorgung/Wertstoffh%C3%B6fe/'),
        # 02.10.2026 an magdeburg.de nachgelesen: Bis 1 m³ Sperrmuell ist an
        # allen drei Hoefen gebuehrenfrei, mehr nur am Hof Haengelsberge gegen
        # Gebuehr - das fehlte und widersprach scheinbar der 0,2-m³-Regel, die
        # fuer die uebrigen Abfallarten gilt.
        'hof': ('Drei Wertstoffhöfe der Stadt: Hängelsberge (Königstraße 96), '
                'Cracauer Anger (An der Lake 3, Berliner Chaussee) und '
                'Silberbergweg 26, alle mit Schadstoffsammelstelle. Bis 1 m³ '
                'Sperrmüll nehmen alle drei gebührenfrei an, mehr nur der Hof '
                'Hängelsberge gegen Gebühr. Das gilt nur für Haushalte, die an '
                'die Magdeburger Abfallentsorgung angeschlossen sind.'),
        'sperrmuell': ('Kostenfrei sind zweimal jährlich je 2 m³ oder einmal 4 m³. '
                       'Anmeldung online, per Postkarte, unter 0391 540-4688 oder '
                       'persönlich in der Sternstraße 13; von der Anmeldung bis '
                       'zur Abholung plant die Stadt bis zu 4 Wochen ein. '
                       'Elektroaltgeräte und Schrott nimmt die Sperrmüllabfuhr in '
                       'Magdeburg mit. Ist das Kontingent aufgebraucht, holt der '
                       'Abfallwirtschaftsbetrieb per Lkw gegen Gebühr ab: 15,40 € je '
                       'angefangenen halben Kubikmeter und 13 € je Elektroaltgerät.'),
        # Bis 02.10.2026: "1945 fast vollstaendig zerstoert ... ueberwiegend
        # Nachkriegszeit ... wenige Gruenderzeitinseln" - unbelegt und laut
        # Zensus schief (39 % der Wohnungen sind aelter als 1950).
        'bebauung': ('Gut jede dritte Magdeburger Wohnung (35,4 %) stammt aus den '
                     'Jahren 1960 bis 1989, fast ebenso viele (39,0 %) aus der Zeit '
                     'vor 1950. Drei von zehn Wohnungen liegen in Häusern mit 13 '
                     'und mehr Wohnungen (29,2 %), weitere 35,7 % in Häusern mit 7 '
                     'bis 12 (Zensus 2022). Entsprechend stehen oben der Block mit '
                     'Aufzug, die Altbauwohnung ohne Aufzug und das Haus am '
                     'Stadtrand nebeneinander.'),
        'bebauung_quellen': [
            ('Statistisches Landesamt Sachsen-Anhalt, Zensus 2022, Gebäude und Wohnungen',
             'https://statistik.sachsen-anhalt.de/fileadmin/Bibliothek/Landesaemter/StaLa/startseite/Zensus_2022/Tabellen/15_ST_Regionaltabelle_Geb%C3%A4ude_Wohnungen_Z22.xlsx'),
        ],
        'beispiele': [
            {
                'titel': 'Wohnung in Neu-Olvenstedt, 62 m², 4. OG mit Aufzug',
                'beschreibung': 'Der Aufzug spart den Stockwerkzuschlag; '
                                'getragen wird trotzdem, vom Aufzug bis zum '
                                'Fahrzeug.',
                'args': {'objektart': 'wohnung', 'qm': 62,
                         'stockwerk': '4og', 'aufzug': True,
                         'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Gründerzeitwohnung in Stadtfeld Ost, 90 m², 3. OG, '
                         'voll',
                'beschreibung': 'Große Altbauwohnung ohne Aufzug, voll '
                                'möbliert – Fläche, Stockwerk und Füllgrad '
                                'wirken zusammen.',
                'args': {'objektart': 'wohnung', 'qm': 90,
                         'stockwerk': '3og', 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus in Ottersleben, 130 m², mittel',
                'beschreibung': 'Am Stadtrand mit Grundstück und Zufahrt. '
                                'Keller, Dachboden und Garage sind im '
                                'Hauspreis enthalten.',
                'args': {'objektart': 'haus', 'qm': 130,
                         'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.magdeburg.de/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Recycling-und-Entsorgung/Wertstoffh%C3%B6fe/',
        'sperrmuell_quelle': 'https://www.magdeburg.de/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Recycling-und-Entsorgung/Sperrm%C3%BCll/',
        'lokal_text': [
            {'text': ('Die Stadt Magdeburg betreibt drei Wertstoffhöfe: Hängelsberge '
                      '(Königstraße 96), Cracauer Anger (An der Lake 3, Berliner '
                      'Chaussee) und Silberbergweg 26. Geöffnet ist montags bis '
                      'freitags ab 7:00 Uhr (Hängelsberge) beziehungsweise 9:30 Uhr, '
                      'mittwochs bis 16:00 Uhr, samstags von 8:00 bis 13:00 Uhr; '
                      'Cracauer Anger und Silberbergweg schließen montags bis '
                      'freitags von 12:00 bis 13:00 Uhr und sonst um 17:00 Uhr. Am '
                      'Hängelsberge gibt es keine Mengenbegrenzung, an den beiden '
                      'anderen höchstens 1 m³ je Anlieferung, Gartenabfälle bis 2 m³.'),
             'quellen': [('Stadt Magdeburg, Wertstoffhöfe',
                          'https://www.magdeburg.de/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Recycling-und-Entsorgung/Wertstoffh%C3%B6fe/'),
                         ('Kontakte und Öffnungszeiten',
                          'https://www.magdeburg.de/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Kontakte-und-%C3%96ffnungszeiten/')]},
            {'text': ('Bei der städtischen Sperrmüllabholung wird zum bestätigten '
                      'Termin bis 7:00 Uhr bereitgestellt, frühestens am Vorabend. '
                      'Ein selbst bestimmter Termin kostet 50 € Servicegebühr. '
                      'Bauabfälle, Schadstoffe, Farbeimer, Sanitäreinrichtungen, '
                      'Verpackungen und Autoteile bleiben ausgeschlossen, ebenso '
                      'Teile über 2,20 × 1,50 × 0,75 m oder 75 kg.'),
             'quellen': [('Stadt Magdeburg, Sperrmüll',
                          'https://www.magdeburg.de/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Recycling-und-Entsorgung/Sperrm%C3%BCll/')]},
            {'text': ('Magdeburg gliedert sich in 40 Stadtteile und 180 statistische '
                      'Bezirke, darunter Neu Olvenstedt, Kannenstieg, Stadtfeld Ost, '
                      'Sudenburg, Cracau und Brückfeld. Für die meisten Abfallarten '
                      'gilt an den Höfen je Tag und Haushalt eine gebührenfreie Menge '
                      'von 0,2 m³; Sperrmüll ist bis 1 m³ frei, zwischen 1 und 2 m³ '
                      'kostet er 10 €, größere Mengen werden gewogen.'),
             'quellen': [('Stadt Magdeburg, Stadtteile',
                          'https://www.magdeburg.de/index.php?La=1&ffsn=false&ffsm=1&object=tx%2C698.8798.1&kat=&kuo=2&sub=0'),
                         ('Wertstoffhöfe',
                          'https://www.magdeburg.de/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Recycling-und-Entsorgung/Wertstoffh%C3%B6fe/')]},
            {'text': ('Auf den drei Magdeburger Wertstoffhöfen lässt sich mehr '
                      'abgeben als Sperrmüll: Elektrogroßgeräte wie Waschmaschinen, '
                      'Herde, Kühlgeräte und Fernseher, kleine Geräte wie Toaster, '
                      'Föhn oder Mobiltelefone, außerdem Textilien, Altglas und '
                      'Speiseöl. Wer nicht an die städtische Abfallentsorgung '
                      'angeschlossen ist, zahlt laut Stadt für jede Abgabe, nur '
                      'Elektroaltgeräte sind davon ausgenommen.'),
             'quellen': [('Stadt Magdeburg, Wertstoffhöfe',
                          'https://www.magdeburg.de/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Recycling-und-Entsorgung/Wertstoffh%C3%B6fe/')]},
            {'text': ('Brauchbares muss in Magdeburg nicht im Container enden. Das '
                      'Sozialkaufhaus der BVIK gGmbH im Bruno-Taut-Ring 119 nimmt '
                      'Gebrauchtes kostenlos an und holt Möbel und Großgeräte '
                      'kostenfrei ab. Help 2007 sammelt gebrauchsfähige Möbel und '
                      'Elektrogroßgeräte ebenfalls ohne Abholkosten und verkauft '
                      'ohne Armutsnachweis. Der Möbel- und Hausratservice der AQB '
                      'in der Karl-Schmidt-Straße 9-11 verkauft nur gegen '
                      'Bedürftigkeitsnachweis.'),
             'quellen': [('Sozialkaufhaus Magdeburg (BVIK gGmbH)',
                          'https://bvik-sozialkaufhaus.de/'),
                         ('Help 2007 Magdeburg',
                          'https://help2007.de/'),
                         ('AQB gGmbH, Möbel- und Hausratservice',
                          'https://aqb-md.de/moebel-und-hausratservice/')]},
        ],
        'faq_zusatz': ('In Magdeburg nehmen die drei städtischen Wertstoffhöfe '
                       'Hängelsberge, Cracauer Anger und Silberbergweg '
                       'Sperrmüll bis 1 m³ gebührenfrei an, größere Mengen nur '
                       'Hängelsberge gegen Gebühr; Sperrmüll holt die Stadt nach '
                       'Anmeldung ab.'),
    },
    'dessau': {
        'ortsteile': ['Ziebigk', 'Törten', 'Mildensee', 'Waldersee',
                      'Alten', 'Kochstedt', 'Mosigkau', 'Großkühnau',
                      'Kleinkühnau', 'Haideburg', 'Roßlau', 'Meinsdorf',
                      'Zoberberg', 'Kleutsch', 'Sollnitz', 'Brambach',
                      'Rodleben', 'Mühlstedt'],
        'traeger': 'Eigenbetrieb Stadtpflege Dessau-Roßlau',
        'quelle': ('https://stadtpflege.dessau-rosslau.de/entsorgung/abfall-abc/entsorgungswege/'),
        'hof': ('Abfallentsorgungsanlage Polysiusstraße 2, Selbstanlieferung '
                'Mo–Fr 7:15–15:45 Uhr, Sa 7:00–12:30 Uhr; Schadstoffannahme nur'
                ' am 1. und 3. Samstag 7–12 Uhr.'),
        'sperrmuell': ('Abholung auf Abruf, nur schriftlich per Sperrmüllkarte '
                       '(Wasserwerkstraße 13 oder online) oder über das '
                       'Onlineformular. Je Einwohner und Jahr sind 1,0 m³ aus privaten'
                       ' Haushalten in der Abfallgrundpauschale enthalten '
                       '(Abfallgebührensatzung ab 01.01.2025), darüber gilt der '
                       'Gebührentarif.'),
        'bebauung': 'Dessau ist Bauhausstadt – die Siedlung Dessau-Törten und '
                    'die Laubenganghäuser stehen unter Denkmalschutz, mit '
                    'entsprechend kleinen Räumen und schmalen Zugängen. '
                    'Daneben große Plattenbaugebiete in Zoberberg und Alten, '
                    'und in Roßlau viel Einfamilienhaus mit Garten.',
        'beispiele': [
            {
                'titel': 'Reihenhaus in Dessau-Törten, 75 m², mittel',
                'beschreibung': 'Die Bauhaus-Siedlung steht unter '
                                'Denkmalschutz: kleine Räume, schmale '
                                'Zugänge.',
                'args': {'objektart': 'haus', 'qm': 75, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Plattenbauwohnung in Alten, 58 m², 4. OG mit Aufzug',
                'beschreibung': 'In den großen Wohngebieten gibt es Aufzüge – '
                                'damit entfällt der Stockwerkzuschlag, egal '
                                'wie hoch die Wohnung liegt.',
                'args': {'objektart': 'wohnung', 'qm': 58,
                         'stockwerk': '4og', 'aufzug': True,
                         'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Gartengrundstück in Roßlau, 180 m²',
                'beschreibung': 'In Roßlau steht viel Einfamilienhaus mit '
                                'Garten. Laube, Zaun und Grünschnitt rechnen '
                                'wir als Gartenfläche, nicht als Wohnfläche.',
                'args': {'objektart': 'garten', 'qm': 180,
                         'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'sperrmuell_quelle': 'https://stadtpflege.dessau-rosslau.de/entsorgung/entsorgung-kontakt/',
        'lokal_text': [
            {'text': ('Die Abfallentsorgungsanlage der Stadtpflege liegt im Südwesten'
                      ' der Stadt, auf der früheren Deponie „Scherbelberg“. Sie ist '
                      'an Sonn- und Feiertagen, am Ostersonnabend, an Heiligabend und'
                      ' an Silvester geschlossen; Sperrmüll ist bei Selbstanlieferung'
                      ' kostenpflichtig. Schadstoffe aus Haushalten nimmt sie bis 20 '
                      'kg beziehungsweise 20 Liter je Anlieferung an, nicht in Wochen'
                      ' mit mobiler Schadstoffsammlung. Auskunft: 0340 204 1178 oder '
                      '0340 204 1278.'),
             'quellen': [('Stadtpflege Dessau-Roßlau, Entsorgungswege',
                          'https://stadtpflege.dessau-rosslau.de/entsorgung/abfall-abc/entsorgungswege/')]},
            {'text': ('Nach der Abfallgebührensatzung ab 1. Januar 2025 sind 1,0 m³ '
                      'Sperrmüll je Einwohner und Jahr aus privaten Haushalten in der'
                      ' Abfallgrundpauschale enthalten, gemessen im zusammengelegten '
                      'Zustand (§ 5 Abs. 3). Ein Elektro-Großgerät je Einwohner und '
                      'Jahr wird kostenfrei abgeholt, Kleingeräte unbegrenzt; '
                      'Anmeldung per Anruf unter 0340 2041572 oder per Formular.'),
             'quellen': [('Abfallgebührensatzung ab 01.01.2025 (PDF)',
                          'https://stadtpflege.dessau-rosslau.de/cms/wp-content/uploads/2024/12/Abfallgebuehrensatzung-ab-01.01.2025.pdf'),
                         ('Kontakt Entsorgung',
                          'https://stadtpflege.dessau-rosslau.de/entsorgung/entsorgung-kontakt/')]},
            {'text': ('Dessau-Roßlau gliedert sich statistisch in zwei Stadtteile, '
                      'Dessau und Roßlau, mit zusammen 25 Stadtbezirken und 14 '
                      'Ortschaften. Zu den Stadtbezirken zählen unter anderem '
                      'Ziebigk, Törten, Mildensee, Waldersee, Alten und Zoberberg.'),
             'quellen': [('Stadt Dessau-Roßlau, Stadtgebiet',
                          'https://verwaltung.dessau-rosslau.de/stadt-buerger/wahlen-und-statistik/statistik/stadtgebiet.html'),
                         ('Wikipedia, Dessau-Roßlau (Sekundärquelle)',
                          'https://de.wikipedia.org/wiki/Dessau-Ro%C3%9Flau')]},
            {'text': ('Am Werner-Seelenbinder-Ring 2 sammelt das Sozialkaufhaus '
                      'Dessau Sachspenden direkt zur Weitergabe an bedürftige '
                      'Menschen der Region. Gesucht werden unter anderem Möbel und '
                      'Fahrräder, Garten- und Küchengeräte, Waschmaschinen, Herde, '
                      'Kühlschränke, Werkzeuge, Bürogeräte, Bücher und Hilfsmittel '
                      'für ältere und behinderte Menschen. Abgeholt wird kostenlos; '
                      'offen ist mittwochs von 9:00 bis 16:30 Uhr, weitere Zeiten '
                      'nach telefonischer Vereinbarung.'),
             'quellen': [('Sozialkaufhaus Dessau',
                          'https://sozialkaufhaus-dessau.de/')]},
            {'text': ('Zuständig für Nachlässe aus Dessau-Roßlau ist das '
                      'Amtsgericht in der Willy-Lohmann-Straße 33; es führt '
                      'zugleich Betreuungs- und Nachlasssachen. Auf der '
                      'Gerichtsseite liegen Vordrucke für Testamentseröffnung, '
                      'Testamentsverwahrung, den Termin zur Erbausschlagung, den '
                      'Termin zum Erbschein und einen Wertermittlungsbogen bereit.'),
             'quellen': [('Amtsgericht Dessau-Roßlau, Themen',
                          'https://ag-de.sachsen-anhalt.de/themen'),
                         ('Amtsgericht Dessau-Roßlau, Lokaler Service',
                          'https://ag-de.sachsen-anhalt.de/service/lokaler-service-des-gerichts')]},
        ],
        'faq_zusatz': ('In Dessau-Roßlau nimmt die Abfallentsorgungsanlage der '
                       'Stadtpflege in der Polysiusstraße 2 Selbstanlieferungen an; '
                       'Sperrmüll holt die Stadtpflege auf Abruf ab.'),
    },
    'bitterfeld': {
        'ortsteile': ['Bitterfeld', 'Wolfen', 'Greppin', 'Holzweißig',
                      'Thalheim', 'Bobbau', 'Reuden', 'Rödgen'],
        'traeger': 'Anhalt-Bitterfelder Kreiswerke (ABIKW)',
        'quelle': 'https://www.abikw.de/sammelsysteme/',
        'hof': ('Abfallanlieferung der ABIKW: Salegaster Chaussee 10, Ortsteil '
                'Greppin, Telefon 03494 79999-0, geöffnet Mo, Mi, Do 8:00–16:00, '
                'Di 8:00–18:00, Fr 8:00–13:00 Uhr. Die ABIKW verlinkt auf ihrer '
                'Seite außerdem die Wolfener Recycling GmbH (privater Betreiber), '
                'Hugo-Preuß-Straße 1 (Mo–Fr 6:30–16:00 Uhr, Sa 8:00–12:00 Uhr, '
                'laut deren Website).'),
        'sperrmuell': ('Anmeldung über das Online-Anmeldeformular der ABIKW. Je '
                       'Anmeldung und Einwohner werden 2 m³ abgeholt, höchstens '
                       'zweimal im Jahr. Ausschließlich der angemeldete Sperrmüll darf'
                       ' am mitgeteilten Termin bis 6 Uhr morgens bereitgestellt '
                       'werden.'),
        'bebauung': ('Bitterfeld-Wolfen ist aus zwei Industriestädten '
                     'zusammengewachsen. Der Rückbau nach 1990 hat viele Wohnblöcke '
                     'verschwinden lassen; geblieben sind sanierte Bestände und die '
                     'Werkssiedlungen in Wolfen-Nord. Gewerbeflächen im Chemiepark '
                     'sind ein eigenes Thema.'),
        'beispiele': [
            {
                'titel': 'Wohnung in der Werkssiedlung Wolfen-Nord, 56 m², 1. OG',
                'beschreibung': 'Sanierter Bestand, normale Möblierung – der '
                                'häufigste Fall bei einem regulären Auszug.',
                'args': {'objektart': 'wohnung', 'qm': 56, 'stockwerk': '1og',
                         'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Gewerbefläche im Chemiepark, 220 m²',
                'beschreibung': 'Gerechnet wird nach Grundfläche; Sonderabfall wird '
                'getrennt erfasst und nachgewiesen.',
                'args': {'objektart': 'gewerbe', 'qm': 220,
                         'fuellgrad': 'mittel', 'sonderabfall': 'viele'},
            },
            {
                'titel': 'Einfamilienhaus, 110 m², voll',
                'beschreibung': 'Kompletter Hausstand inklusive Keller und '
                                'Dachboden.',
                'args': {'objektart': 'haus', 'qm': 110, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.abikw.de/anfallanlieferung/',
        'sperrmuell_quelle': 'https://www.abikw.de/sammelsysteme/sperrmuell-richtig-entsorgen-gekuerzt/',
        'lokal_text': [
            {'text': ('Für Bitterfeld-Wolfen ist die Anhalt-Bitterfelder Kreiswerke '
                      'GmbH (ABIKW) zuständig. Ihr Kundenbüro in Greppin für '
                      'Privatkunden erreichen Sie unter 03494 79999-35. Die ABIKW '
                      'verlinkt auf ihrer Seite außerdem die Wolfener Recycling '
                      'GmbH, einen privaten Betreiber; Adresse und '
                      'Öffnungszeiten stehen auf wolfener-recycling.de.'),
             'quellen': [('ABIKW, Anlieferung',
                          'https://www.abikw.de/anfallanlieferung/'),
                         ('Anlage zur Bauschuttsortierung',
                          'https://www.abikw.de/anfallanlieferung/anlage-zur-bauschuttsortierung/')]},
            {'text': ('Sperrmüll wird nur auf Anmeldung abgeholt, über das '
                      'Online-Formular der ABIKW. Je Anmeldung und Einwohner sind es '
                      '2 m³, höchstens zweimal im Jahr, also 4 m³ pro Jahr. Am '
                      'mitgeteilten Termin darf ausschließlich der angemeldete '
                      'Sperrmüll vor das Grundstück oder an den Behälterstandplatz, '
                      'geordnet und bis 6 Uhr morgens.'),
             'quellen': [('ABIKW, Sperrmüll richtig entsorgen',
                          'https://www.abikw.de/sammelsysteme/sperrmuell-richtig-entsorgen-gekuerzt/'),
                         ('Sperrmüll anmelden',
                          'https://www.abikw.de/sperrmuellanmelden/')]},
            {'text': ('Bitterfeld-Wolfen entstand am 1. Juli 2007 aus dem '
                      'Zusammenschluss der Städte Bitterfeld und Wolfen mit weiteren '
                      'Gemeinden. Heute gliedert sich die Stadt in acht Ortschaften: '
                      'Bitterfeld, Wolfen, Greppin, Holzweißig, Thalheim, Bobbau (mit'
                      ' Siebenhausen), Reuden an der Fuhne und Rödgen (mit '
                      'Zschepkau).'),
             'quellen': [('Wikipedia, Bitterfeld-Wolfen (Sekundärquelle)',
                          'https://de.wikipedia.org/wiki/Bitterfeld-Wolfen')]},
            {'text': ('Elektroaltgeräte sind im Landkreis Anhalt-Bitterfeld ein '
                      'Sonderweg: Die ABIKW holt sie auf Antrag mehrmals im Jahr '
                      'und ohne Begrenzung der Jahresmenge entgeltfrei vor dem '
                      'Grundstück ab, bis 6 Uhr geordnet bereitgestellt. Aus '
                      'Kleingartenanlagen nimmt sie keine Geräte mit. Wer selbst '
                      'fährt, kann die meisten Annahmestellen im Landkreis nutzen.'),
             'quellen': [('ABIKW, Elektroaltgeräte richtig entsorgen',
                          'https://www.abikw.de/sammelsysteme/xelektroaltgeraete-richtig-entsorgen/')]},
            {'text': ('Das Amtsgericht Bitterfeld-Wolfen in der Lindenstraße 9 '
                      'deckt nicht nur die Doppelstadt ab, sondern auch '
                      'Muldestausee, Raguhn-Jeßnitz, Sandersdorf-Brehna und Zörbig. '
                      'Für Nachlassangelegenheiten nennt das Gericht die Rufnummern '
                      '03493 364-302 und 364-304. Maßgeblich ist der letzte '
                      'Wohnsitz des Verstorbenen.'),
             'quellen': [('Amtsgericht Bitterfeld-Wolfen, Zuständigkeiten',
                          'https://ag-btf.sachsen-anhalt.de/themenzustaendigkeiten')]},
        ],
        'faq_zusatz': ('In Bitterfeld-Wolfen holt die ABIKW Sperrmüll nach '
                       'Anmeldung über das Online-Formular ab.'),
    },
    'koethen': {
        'ortsteile': ['Arensdorf', 'Baasdorf', 'Dohndorf',
                      'Löbnitz an der Linde', 'Merzien', 'Wülknitz',
                      'Gahrendorf', 'Hohsdorf', 'Zehringen', 'Großwülknitz',
                      'Kleinwülknitz', 'Elsdorf', 'Porst'],
        'traeger': 'Anhalt-Bitterfelder Kreiswerke (ABIKW)',
        'quelle': 'https://www.abikw.de/anfallanlieferung/anliefern-in-koethen/',
        'hof': ('Annahmestellen der PreZero Service Köthen GmbH (Anlieferung für '
                'die ABIKW), Elsdorfer Weg 25 und Maxdorfer Straße 40: Mo–Fr 8–12 '
                'und 12:30–17 Uhr, samstags 8–12 Uhr im Wechsel. Gefährliche '
                'Abfälle nimmt die ABIKW ganzjährig an stationären Stellen an, '
                'darunter in Köthen.'),
        'sperrmuell': ('Zweimal im Jahr auf Antrag, je Anmeldung und Einwohner 2 m³ (4 m³ '
                       'im Jahr); Anmeldung online, Bereitstellung bis 6 Uhr vor dem '
                       'Grundstück. Haushaltsauflösungen laufen über einen '
                       'kostenpflichtigen Containerdienst.'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus, 140 m², voll',
                'args': {'objektart': 'haus', 'qm': 140, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 70 m², 2. OG, mittel',
                'args': {'objektart': 'wohnung', 'qm': 70, 'stockwerk': '2og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Keller, 22 m², voll',
                'args': {'objektart': 'keller', 'qm': 22, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.abikw.de/anfallanlieferung/anliefern-in-koethen/',
        'sperrmuell_quelle': 'https://www.abikw.de/sammelsysteme/sperrmuell-richtig-entsorgen-gekuerzt/',
        'lokal_text': [
            {'text': ('In Köthen liefert man bei den Annahmestellen der PreZero '
                      'Service Köthen GmbH an: Elsdorfer Weg 25 und Maxdorfer '
                      'Straße 40. Beide öffnen werktags von 8 bis 12 und von 12:30 '
                      'bis 17 Uhr; samstags von 8 bis 12 Uhr ist im Wechsel einmal '
                      'die eine (gerade Kalenderwochen), einmal die andere Stelle '
                      '(ungerade Wochen) offen.'),
             'quellen': [('ABIKW, Abfälle anliefern in Köthen',
                          'https://www.abikw.de/anfallanlieferung/anliefern-in-koethen/')]},
            {'text': ('Sperrmüll holt die ABIKW zweimal im Jahr auf Antrag ab, je '
                      'Anmeldung und Einwohner 2 m³, also höchstens 4 m³ im Jahr; '
                      'bereitzustellen ist er bis 6 Uhr vor dem Grundstück. '
                      'Angemeldet wird online. Wer eine ganze Wohnung räumt, muss '
                      'laut ABIKW einen kostenpflichtigen Containerdienst seiner '
                      'Wahl beauftragen.'),
             'quellen': [('ABIKW, Sperrmüll richtig entsorgen',
                          'https://www.abikw.de/sammelsysteme/sperrmuell-richtig-entsorgen-gekuerzt/'),
                         ('ABIKW, Sperrmüll: neues Anmeldeverfahren',
                          'https://www.abikw.de/sammelsysteme/sperrmuell-richtig-entsorgen-gekuerzt/neues_anmeldeverfahren/')]},
            {'text': ('Gefährliche Haushaltsabfälle nimmt die ABIKW ganzjährig an '
                      'stationären Stellen in Greppin, Zerbst und Köthen an, in '
                      'Gebinden bis 25 Liter und in der Originalverpackung; '
                      'entgeltfrei, nur Kfz-Altöle kosten. Elektroaltgeräte werden '
                      'mehrmals im Jahr entgeltfrei auf Antrag abgeholt oder selbst '
                      'angeliefert; das Schadstoffmobil kommt zweimal jährlich.'),
             'quellen': [('ABIKW, Gefährliche Abfälle sicher entsorgen',
                          'https://www.abikw.de/sammelsysteme/xgefaehrliche-abfaelle-sicher-entsorgen/'),
                         ('ABIKW, Elektroaltgeräte richtig entsorgen',
                          'https://www.abikw.de/sammelsysteme/xelektroaltgeraete-richtig-entsorgen/')]},
            {'text': ('Bei noch brauchbarem Sperrmüll verweist die ABIKW auf das '
                      'Sozialkaufhaus der Region. In Köthen betreibt die KÖSAG '
                      'gGmbH das Soziale Kaufhaus in der Langenfelder Straße 2 am '
                      'Wattrelos-Ring, montags bis donnerstags von 9 bis 15:30 und '
                      'freitags bis 15 Uhr; einkaufen dürfen Berechtigte mit '
                      'Leistungsbescheid oder GEZ-Befreiung. Daneben gibt es die '
                      'DRK-Kleiderkammer in der Siebenbrünnenpromenade 4/5.'),
             'quellen': [('ABIKW, Sperrmüll: neues Anmeldeverfahren',
                          'https://www.abikw.de/sammelsysteme/sperrmuell-richtig-entsorgen-gekuerzt/neues_anmeldeverfahren/'),
                         ('ABIKW, Sozialkaufhäuser und Kleiderkammern 2026 (PDF)',
                          'https://www.abikw.de/wp-content/uploads/2026/01/LK-ABI_Sozialkaufhaeuser_Kleiderkammern_2026.pdf')]},
            {'text': ('Das Amtsgericht Köthen in der Friedhofstraße 48 ist laut '
                      'Justizportal Nachlassgericht; mittwochs findet dort kein '
                      'Sprechtag in Nachlasssachen statt. Zur Stadt mit 23.257 '
                      'Einwohnern (31.12.2025) gehören die Ortschaften Arensdorf, '
                      'Baasdorf, Dohndorf, Löbnitz an der Linde, Merzien und '
                      'Wülknitz mit ihren Ortsteilen. Die Fläche beträgt 78,42 km².'),
             'quellen': [('Justizportal, Orts- und Gerichtsverzeichnis (Nachlasssachen, PLZ 06366)',
                          'https://www.justizadressen.nrw.de/de/justiz/gericht?ang=nachlass&plzort=06366+Köthen'),
                         ('Amtsgericht Köthen, Nachlassangelegenheiten',
                          'https://www.ag-koet.sachsen-anhalt.de/themen/nachlassangelegenheiten'),
                         ('Stadt Köthen (Anhalt), Über die Stadt',
                          'https://www.koethen-anhalt.de/de/ueber-die-stadt.html')]},
        ],
        'faq_zusatz': ('Geräumtes aus Köthen geht an die Annahmestellen in Elsdorfer Weg '
                       'und Maxdorfer Straße, per Antrag in die Sperrmüllabholung der '
                       'ABIKW oder, wenn es taugt, ins Soziale Kaufhaus der KÖSAG.'),
    },
    'bernburg': {
        'ortsteile': ['Dröbel', 'Roschwitz', 'Strenzfeld', 'Waldau',
                      'Neuborna', 'Aderstedt', 'Baalberge', 'Biendorf',
                      'Gröna', 'Peißen', 'Poley', 'Preußlitz', 'Wohlsdorf'],
        'traeger': 'Kreiswirtschaftsbetrieb Salzlandkreis',
        'quelle': 'https://www.awb-salzlandkreis.de/wertstoffhoefe.html',
        'hof': 'Wertstoffhof Bernburg, Dessauer Straße 121, Telefon '
               '03471 684-4527. Geöffnet Mo–Fr 7:00–17:00, Sa 8:00–12:00 Uhr.',
        'sperrmuell': ('Antrag über das Online-Formular des Kreiswirtschaftsbetriebs '
                       '(Rückfragen: Disposition Bernburg, 03471 684-4526). Bis zu '
                       '2 m³ je Abholung und Haushalt sind gebührenfrei; angestrebt '
                       'ist die Abholung binnen fünf Wochen, der Termin kommt '
                       'spätestens drei Werktage vorher per E-Mail.'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus, 100 m², mittel',
                'beschreibung': 'Keller und Dachboden sind im Hauspreis '
                                'enthalten.',
                'args': {'objektart': 'haus', 'qm': 100,
                         'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Wohnung, 58 m², 3. OG ohne Aufzug',
                'beschreibung': 'Ohne Aufzug im 3. Obergeschoss: Daher fällt '
                                'der Stockwerkzuschlag an.',
                'args': {'objektart': 'wohnung', 'qm': 58,
                         'stockwerk': '3og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Keller, 15 m², voll',
                'args': {'objektart': 'keller', 'qm': 15, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.awb-salzlandkreis.de/wertstoffhoefe.html',
        'sperrmuell_quelle': 'https://www.awb-salzlandkreis.de/sperrmuellabholung.html',
        'lokal_text': [
            {'text': ('Der Wertstoffhof Bernburg in der Dessauer Straße 121 gehört '
                      'zum Kreiswirtschaftsbetrieb Salzlandkreis und ist werktags '
                      'von 7:00 bis 17:00 Uhr, samstags von 8:00 bis 12:00 Uhr '
                      'geöffnet (Telefon 03471 684-4527). Er nimmt Abfälle, Grüngut, '
                      'Verpackungen sowie Elektro- und Elektronikgeräte an. Wer '
                      'Sperrmüll selbst bringt, gibt bis zu 1 m³ je Anlieferung '
                      'gebührenfrei ab; größere Mengen kosten eine Gebühr.'),
             'quellen': [('Kreiswirtschaftsbetrieb Salzlandkreis, Wertstoffhöfe',
                          'https://www.awb-salzlandkreis.de/wertstoffhoefe.html'),
                         ('Ansprechpartner',
                          'https://www.awb-salzlandkreis.de/ansprechpartner.html'),
                         ('Sperrmüllabholung',
                          'https://www.awb-salzlandkreis.de/sperrmuellabholung.html')]},
            {'text': ('Für die Abholung wird der Antrag im Online-Formular des '
                      'Kreiswirtschaftsbetriebs gestellt. Je Abholung nimmt der '
                      'Betrieb bis zu 2 m³ je Haushalt gebührenfrei mit, was zu '
                      'mehreren Terminen führen kann. Einzelstücke dürfen höchstens '
                      '75 kg wiegen und 2,00 × 1,50 × 0,75 m messen. Angestrebt ist '
                      'die Abholung binnen fünf Wochen; den Termin teilt der Betrieb '
                      'spätestens drei Werktage vorher per E-Mail mit. Rückfragen '
                      'beantwortet die Disposition Bernburg unter 03471 684-4526.'),
             'quellen': [('Kreiswirtschaftsbetrieb Salzlandkreis, Sperrmüllabholung',
                          'https://www.awb-salzlandkreis.de/sperrmuellabholung.html'),
                         ('Ansprechpartner',
                          'https://www.awb-salzlandkreis.de/ansprechpartner.html')]},
            {'text': ('Herausgestellt wird frühestens ab 16:00 Uhr am Vortag und '
                      'spätestens bis 6:30 Uhr am Abholtag, getrennt nach Holz, '
                      'Polstern und Altmetall oder Elektronik. Ausgeschlossen sind '
                      'unter anderem Restabfall, Schadstoffe, Bauschutt, Laminat, '
                      'Fenster und Türen. Für große Mengen gibt es '
                      'gebührenpflichtige Sperrmüllcontainer bis 7 m³. Zur Stadt '
                      'gehören laut bernburg.de acht Ortschaften von Aderstedt bis '
                      'Wohlsdorf; Dröbel, Roschwitz, Strenzfeld, Waldau und Neuborna '
                      'führt Wikipedia als Stadtteile.'),
             'quellen': [('Kreiswirtschaftsbetrieb Salzlandkreis, Sperrmüllabholung',
                          'https://www.awb-salzlandkreis.de/sperrmuellabholung.html'),
                         ('Was gehört zum Sperrmüll, was nicht?',
                          'https://www.awb-salzlandkreis.de/was-gehoert-zum-sperrmuell,-was-nicht-.html'),
                         ('Stadt Bernburg, Ortschaften',
                          'https://www.bernburg.de/de/ortschaften.html'),
                         ('Wikipedia, Bernburg (Saale) (Sekundärquelle)',
                          'https://de.wikipedia.org/wiki/Bernburg_(Saale)')]},
            {'text': ('Das Schadstoffmobil des Kreiswirtschaftsbetriebs übernimmt '
                      'Gefahrstoffe ausschließlich aus Privathaushalten und '
                      'kostenlos: Gebinde bis 60 Liter, auf zwei Behälter zu je 30 '
                      'Liter verteilt, oder bis 60 Kilogramm. Das Fachpersonal '
                      'kippt nichts aus und füllt nicht um; abgestellt werden darf '
                      'nie. Leere Spraydosen, Farbeimer und Kanister mit Grünem '
                      'Punkt gehören in die gelbe Tonne.'),
             'quellen': [('Kreiswirtschaftsbetrieb Salzlandkreis, Schadstoffentsorgung',
                          'https://www.kwb-slk.de/schadstoffentsorgung.html')]},
            {'text': ('Elektroaltgeräte nehmen die Wertstoffhöfe des '
                      'Salzlandkreises kostenlos an, Batterien und Akkus werden '
                      'vorher getrennt; Teile auszubauen ist ausdrücklich '
                      'untersagt. Bei der Abholung teilt der Betrieb den Tag '
                      'spätestens drei Werktage vorher mit. Nachlassangelegenheiten '
                      'aus Bernburg liegen beim Amtsgericht Bernburg in der '
                      'Liebknechtstraße 2.'),
             'quellen': [('Kreiswirtschaftsbetrieb Salzlandkreis, Elektro- und Elektronikaltgeräte',
                          'https://www.kwb-slk.de/elektro--und-elektronikaltgeraete.html'),
                         ('Justizportal des Bundes und der Länder, Orts- und Gerichtsverzeichnis (PLZ 06406)',
                          'https://www.justizadressen.nrw.de/de/justiz/gericht?ang=nachlass&plz=06406&ort=')]},
        ],
        'faq_zusatz': ('Das Geräumte geht in Bernburg an den Wertstoffhof in der '
                       'Dessauer Straße 121 oder, bei Antrag über den '
                       'Kreiswirtschaftsbetrieb, in die Sperrmüllabholung des '
                       'Salzlandkreises.'),
    },
    'aschersleben': {
        'ortsteile': ['Drohndorf', 'Freckleben', 'Groß Schierstedt',
                      'Klein Schierstedt', 'Mehringen', 'Schackenthal',
                      'Schackstedt', 'Westdorf', 'Wilsleben',
                      'Winningen', 'Neu Königsaue'],
        'traeger': 'Kreiswirtschaftsbetrieb Salzlandkreis',
        'quelle': ('https://www.kwb-slk.de/wertstoffhoefe.html'),
        'hof': 'Wertstoffhof Aschersleben, Wilslebener Chaussee, Telefon '
               '03471 684-4525. Geöffnet Mo–Fr 7:00–17:00, Sa 8:00–12:00 Uhr.',
        'sperrmuell': ('Zweimal im Jahr holt der Kreiswirtschaftsbetrieb je Haushalt '
                       'bis 2 m³ Sperrmüll gebührenfrei ab. Anmeldung online oder per '
                       'Abrufkarte, Disposition Aschersleben unter 03471 684-4524; '
                       'Ziel für die Abholung sind fünf Wochen.'),
        'beispiele': [
            {
                'titel': 'Altbauhaus im alten Kern, 110 m², voll',
                'beschreibung': 'Ein volles Haus heißt hier: Wohnetagen, '
                                'Dachboden und Keller in einem Auftrag. Große '
                                'Stücke werden im Zimmer zerlegt, bevor sie '
                                'nach unten gehen.',
                'args': {'objektart': 'haus', 'qm': 110, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung in Westdorf, 65 m², 2. OG',
                'beschreibung': 'Normal möbliert, Zugang über das '
                                'Treppenhaus. Der Stockwerkzuschlag ist der '
                                'einzige Unterschied zur gleich großen '
                                'Erdgeschosswohnung.',
                'args': {'objektart': 'wohnung', 'qm': 65,
                         'stockwerk': '2og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Keller und Nebengelass, 20 m², voll',
                'beschreibung': 'Ein Keller samt Nebengelass – meist im Zuge einer '
                'Haushaltsauflösung, manchmal auch allein.',
                'args': {'objektart': 'keller', 'qm': 20, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'sperrmuell_quelle': 'https://www.kwb-slk.de/sperrmuellabholung.html',
        'lokal_text': [
            {'text': ('Der Kreiswirtschaftsbetrieb kündigt den Termin der '
                      'Sperrmüllabholung per E-Mail bis spätestens drei Werktage '
                      'vorher an. Bereitgestellt wird frühestens am Vortag ab 16 Uhr,'
                      ' spätestens bis 6:30 Uhr. Einzelteile dürfen höchstens 75 kg '
                      'wiegen und 2,00 × 1,50 × 0,75 m groß sein.'),
             'quellen': [('Kreiswirtschaftsbetrieb Salzlandkreis, Sperrmüllabholung',
                          'https://www.kwb-slk.de/sperrmuellabholung.html'),
                         ('Sperrmüll-, Schrott- und Altholzentsorgung',
                          'https://www.kwb-slk.de/sperrmuell-,-schrott--und-altholzentsorgung.html')]},
            {'text': ('Am Wertstoffhof Aschersleben ist Sperrmüll bis 1 m³ je '
                      'Anlieferung gebührenfrei. Die Disposition Aschersleben unter '
                      '03471 684-4524 nimmt Anmeldungen für Sperrmüll und Container '
                      'entgegen und kümmert sich um die Tonnenentleerung; der Hof '
                      'selbst ist unter 03471 684-4525 zu erreichen.'),
             'quellen': [('Kreiswirtschaftsbetrieb Salzlandkreis, Ansprechpartner',
                          'https://www.kwb-slk.de/ansprechpartner.html'),
                         ('Wertstoffhöfe',
                          'https://www.kwb-slk.de/wertstoffhoefe.html')]},
            {'text': ('Zur Stadt Aschersleben gehören neben der Kernstadt elf '
                      'Ortschaften, die die Hauptsatzung in der Reihenfolge der '
                      'Eingemeindung nennt: Winningen, Klein Schierstedt, Wilsleben, '
                      'Mehringen, Drohndorf, Freckleben, Groß Schierstedt, '
                      'Schackenthal, Westdorf, Neu Königsaue und Schackstedt. '
                      'Ortschaftsräte gibt es unter anderem in Mehringen, Freckleben,'
                      ' Schackenthal, Westdorf und Neu Königsaue.'),
             'quellen': [('Stadt Aschersleben, Hauptsatzung (PDF)',
                          'https://www.aschersleben.de/output/download.php?fid=3666.38.1.PDF')]},
            {'text': ('Der Kreiswirtschaftsbetrieb sammelt Schadstoffe nur aus '
                      'privaten Haushalten und nimmt sie am Schadstoffmobil '
                      'kostenlos an; Gebinde dürfen bis 60 Liter oder 60 Kilogramm '
                      'fassen, geteilt in je zwei Hälften. Die Mitarbeiter müssen '
                      'die Stoffe persönlich übernehmen, einfach abstellen geht '
                      'nicht. Elektroaltgeräte kosten an den Wertstoffhöfen des '
                      'Salzlandkreises nichts und kommen in eigene Sammelbehälter.'),
             'quellen': [('Kreiswirtschaftsbetrieb Salzlandkreis, Schadstoffentsorgung',
                          'https://www.kwb-slk.de/schadstoffentsorgung.html'),
                         ('Kreiswirtschaftsbetrieb Salzlandkreis, Elektro- und Elektronikaltgeräte',
                          'https://www.kwb-slk.de/elektro--und-elektronikaltgeraete.html')]},
            {'text': ('Das Amtsgericht Aschersleben im Theodor-Römer-Weg 3 ist das '
                      'Nachlassgericht für Verstorbene mit letztem Wohnsitz in '
                      'seinem Bezirk. Seine Seite beschreibt Testamentseröffnung, '
                      'Erbscheinsverfahren und Erbausschlagung; wer ein Testament '
                      'abgeben, zurückholen oder einen Erbscheinsantrag stellen '
                      'will, spricht dort nach telefonischer Vereinbarung vor.'),
             'quellen': [('Amtsgericht Aschersleben, Nachlassgericht',
                          'https://ag-asl.sachsen-anhalt.de/service/nachlassgericht')]},
        ],
        'faq_zusatz': ('In Aschersleben nimmt der Wertstoffhof an der Wilslebener '
                       'Chaussee Sperrmüll bis 1 m³ je Anlieferung gebührenfrei an.'),
    },
    'halberstadt': {
        'ortsteile': ['Aspenstedt', 'Athenstedt', 'Emersleben',
                      'Klein Quenstedt', 'Langenstein', 'Sargstedt',
                      'Schachdorf Ströbeck'],
        'traeger': 'Entsorgungswirtschaft des Landkreises Harz (enwi)',
        'quelle': 'https://www.enwi-hz.de/entsorgung/wertstoffhoefe/wertstoffhoefe.html',
        'hof': 'Wertstoffhof Halberstadt, Am Sülzegraben 15a (Gewerbegebiet „Am '
               'Sülzegraben“), Telefon 03941 41 92 77 19. Geöffnet Mo–Fr '
               '7:00–18:00 Uhr, Sa 8:00–14:00 Uhr.',
        'sperrmuell': 'Abholung kostenlos über die Abfallwirtschaft Nordharz '
                      '(Telefon 03943 56 07 38, Karte aus dem Entsorgungskalender '
                      'oder Online-Formular der enwi), höchstens 10 m³ lose je '
                      'Anmeldung, Abfuhr innerhalb von drei Wochen. Selbstanlieferung '
                      'am Hof bis 2 m³ je Anlieferung und Tag kostenlos.',
        'beispiele': [
            {
                'titel': 'Einfamilienhaus, 90 m², voll',
                'args': {'objektart': 'haus', 'qm': 90, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 60 m², 4. OG mit Aufzug',
                'beschreibung': 'Mit Aufzug entfällt der Stockwerkzuschlag.',
                'args': {'objektart': 'wohnung', 'qm': 60,
                         'stockwerk': '4og', 'aufzug': True,
                         'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Kellerabteil, 16 m², voll',
                'beschreibung': 'Einzelauftrag ohne Wohnung: Für kleine '
                                'Flächen greift die Mindestpauschale, nicht '
                                'der Quadratmeterpreis.',
                'args': {'objektart': 'keller', 'qm': 16, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.enwi-hz.de/entsorgung/wertstoffhoefe/halberstadt/index.html',
        'sperrmuell_quelle': 'https://www.enwi-hz.de/entsorgung/was-wie-wohin/sperrmuell/index.html',
        'lokal_text': [
            {'text': ('Am Sülzegraben 15a, im gleichnamigen Gewerbegebiet, liegt der '
                      'Wertstoffhof Halberstadt des Landkreises Harz. Angenommen wird '
                      'montags bis freitags zwischen 7:00 und 18:00 Uhr, samstags von '
                      '8:00 bis 14:00 Uhr; eine abweichende Winterzeit nennt die enwi '
                      'für diesen Hof nicht. Kostenlos in Kleinmengen gehen unter '
                      'anderem Altmetall, Behälterglas, Elektrogeräte, Papier und '
                      'Pappe an, Sperrmüll bis 2 m³ je Anlieferung und Tag, nur lose '
                      'und ohne Hausmüll oder Kleinteile in Säcken. Bauschutt und '
                      'Baumischabfälle sind gebührenpflichtig, je höchstens 1 m³.'),
             'quellen': [('enwi, Wertstoffhof Halberstadt',
                          'https://www.enwi-hz.de/entsorgung/wertstoffhoefe/halberstadt/index.html')]},
            {'text': ('Wer nicht selbst fährt, meldet Sperrmüll bei der '
                      'Abfallwirtschaft Nordharz an, die die enwi mit Abholung und '
                      'Anmeldung beauftragt hat: per Karte aus dem Entsorgungskalender, '
                      'im Online-Formular der enwi oder unter 03943 56 07 38. Die '
                      'Abholung ist kostenlos und auf 10 m³ lose je Anmeldung '
                      'begrenzt; sie erfolgt innerhalb von drei Wochen nach Eingang, '
                      'der Termin kommt per Antwortkarte.'),
             'quellen': [('enwi, Sperrmüll',
                          'https://www.enwi-hz.de/entsorgung/was-wie-wohin/sperrmuell/index.html'),
                         ('enwi, Sperrmüllanmeldung',
                          'https://www.enwi-hz.de/service/formularservice/sperrmuellanmeldung.html')]},
            {'text': ('Außerhalb des Kerns führt die Stadt laut halberstadt.de sieben '
                      'Ortsteile: Aspenstedt am Huy, Athenstedt am Huy, Emersleben, '
                      'Klein Quenstedt, Langenstein, Sargstedt am Huy und Schachdorf '
                      'Ströbeck. Die Verwaltung der enwi sitzt in der Braunschweiger '
                      'Straße 87/88 in Halberstadt (Telefon 03941 6880-0).'),
             'quellen': [('Stadt Halberstadt, Ortsteile',
                          'https://www.halberstadt.de/de/ortsteile.html'),
                         ('enwi, Kontakt',
                          'https://www.enwi-hz.de/kontakt/index.html')]},
            {'text': ('Zum Schadstoffmobil der enwi bringt man Farben, Lacke, '
                      'Lösungsmittel, Säuren, Batterien und Leuchtstoffröhren '
                      'kostenlos, in haushaltsüblicher Menge: etwa 20 Kilogramm je '
                      'Anlieferer, Gebinde bis 30 Liter. Auch Elektrokleingeräte '
                      'bis 25 Zentimeter Kantenlänge werden dort genommen. Größere '
                      'Altgeräte gibt man am Wertstoffhof Am Sülzegraben 15a '
                      'kostenlos ab; wer abholen lässt, zahlt 8,27 € je Gerät '
                      '(Stand 10/2026, enwi).'),
             'quellen': [('enwi, Schadstoffe',
                          'https://www.enwi-hz.de/entsorgung/was-wie-wohin/schadstoffe/index.html'),
                         ('enwi, Elektrische Haushaltsgeräte',
                          'https://www.enwi-hz.de/entsorgung/was-wie-wohin/elektrische-haushaltsgeraete/index.html')]},
            {'text': ('Möbel in gutem Zustand sind im Gebrauchtmöbelhaus '
                      'Burchardikloster, Am Kloster 1, besser aufgehoben als im '
                      'Container: Die AWZ prüft sie beim Spender und holt sie '
                      'kostenlos ab, verkauft wird montags bis freitags von 10 bis '
                      '15 Uhr ohne Bedürftigkeitsnachweis. Die enwi nennt das Haus '
                      'unter den Abgabemöglichkeiten für Möbel. Nachlasssachen '
                      'gehören vor das Amtsgericht Halberstadt, '
                      'Richard-Wagner-Straße 52.'),
             'quellen': [('AWZ, Gebrauchtmöbelhaus',
                          'https://www.awz.net/gebrauchtmoebelhaus/'),
                         ('Burchardikloster, Gebrauchtmöbel-Haus',
                          'https://burchardikloster.de/gebrauchtmoebel-haus/'),
                         ('enwi, Möbel (gebrauchsfähig)',
                          'https://www.enwi-hz.de/entsorgung/was-wie-wohin/moebel-gebrauchsfaehig/moebel-gebrauchsfaehig.html'),
                         ('Justizportal des Bundes und der Länder, Orts- und Gerichtsverzeichnis (PLZ 38820)',
                          'https://www.justizadressen.nrw.de/de/justiz/gericht?ang=nachlass&plz=38820&ort=')]},
        ],
        'faq_zusatz': ('Geräumtes geht je nach Art zum Wertstoffhof Am Sülzegraben 15a '
                       'oder in die kostenlose, bei der Abfallwirtschaft Nordharz '
                       'angemeldete Sperrmüllabfuhr des Landkreises Harz.'),
    },
    'wernigerode': {
        'ortsteile': ['Hasserode', 'Nöschenrode', 'Benzingerode',
                      'Minsleben', 'Silstedt', 'Schierke', 'Reddeber'],
        'traeger': 'Entsorgungswirtschaft des Landkreises Harz (enwi)',
        'quelle': 'https://www.enwi-hz.de/entsorgung/wertstoffhoefe/wertstoffhoefe.html',
        'hof': 'Wertstoffhof Wernigerode, Am Köhlerteich 9. Geöffnet Mo–Fr '
               '9:00–18:00 Uhr (Dezember bis Februar 10:00–17:00), Sa '
               '9:00–13:00 Uhr.',
        'sperrmuell': 'Abholung kostenlos über die Abfallwirtschaft Nordharz, '
                      'Telefon 03943 56 07 38 (höchstens 10 m³ lose je Anmeldung, '
                      'innerhalb von drei Wochen). Am Hof ist Sperrmüll bis 2 m³ je '
                      'Anlieferung und Tag kostenlos.',
        'beispiele': [
            {
                'titel': 'Einfamilienhaus, 95 m², voll',
                'args': {'objektart': 'haus', 'qm': 95, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 55 m², 2. OG',
                'beschreibung': 'Normal möbliert, im 2. Obergeschoss ohne '
                                'Aufzug: Der Stockwerkzuschlag fällt an.',
                'args': {'objektart': 'wohnung', 'qm': 55,
                         'stockwerk': '2og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Keller in Hasserode, 15 m², voll',
                'beschreibung': 'Der Preis hängt hier am Volumen des '
                                'Kellers.',
                'args': {'objektart': 'keller', 'qm': 15, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.enwi-hz.de/entsorgung/wertstoffhoefe/wernigerode/index.html',
        'sperrmuell_quelle': 'https://www.enwi-hz.de/entsorgung/was-wie-wohin/sperrmuell/index.html',
        'lokal_text': [
            {'text': ('Der Wertstoffhof Am Köhlerteich 9 ist der Bauhof der Stadt '
                      '(Rückfragen unter 03943 65 46 80). '
                      'Sperrmüll ist dort bis 2 m³ je Anlieferung und Tag kostenlos, '
                      'ebenso Altmetall, Elektrogeräte, Glas, Papier und Alttextilien '
                      'in Kleinmengen. Bauschutt und Baumischabfall kosten Gebühr, '
                      'je Sorte bis 1 m³.'),
             'quellen': [('enwi, Wertstoffhof Wernigerode',
                          'https://www.enwi-hz.de/entsorgung/wertstoffhoefe/wernigerode/index.html')]},
            {'text': ('Abgeholt wird nicht vom Hof, sondern von einem Unternehmen, '
                      'das die enwi beauftragt hat: der Abfallwirtschaft Nordharz im '
                      'Ortsteil Reddeber, Brockenblick 1. Angemeldet wird mit der '
                      'Karte aus dem Kalender, im Formular der enwi oder unter '
                      '03943 56 07 38; kostenlos sind bis zu 10 m³ lose je Anmeldung, '
                      'gefahren wird innerhalb von drei Wochen. Wer es eilig hat, '
                      'bucht telefonisch die Expressabfuhr: zwei Werktage, 104,17 € '
                      'in bar.'),
             'quellen': [('enwi, Sperrmüll',
                          'https://www.enwi-hz.de/entsorgung/was-wie-wohin/sperrmuell/index.html'),
                         ('enwi, Sperrmüllanmeldung',
                          'https://www.enwi-hz.de/service/formularservice/sperrmuellanmeldung.html')]},
            {'text': ('Neben dem Kern führt wernigerode.de fünf Ortschaften auf: '
                      'Benzingerode, Minsleben, Reddeber, Schierke und Silstedt; '
                      'Hasserode und Nöschenrode, vor 1994 eingemeindet, nennt '
                      'Wikipedia zusätzlich. Aus dem Sperrmüll ausgenommen sind laut '
                      'enwi Altmetall, Bauabfälle wie Türen und Fliesen, '
                      'Elektrogeräte, Fahrzeugteile samt Reifen, Hausmüll und '
                      'Schadstoffe.'),
             'quellen': [('Stadt Wernigerode, Ortschaften',
                          'https://www.wernigerode.de/Stadt-Leben/Ortschaften/'),
                         ('Wikipedia, Wernigerode (Sekundärquelle)',
                          'https://de.wikipedia.org/wiki/Wernigerode'),
                         ('enwi, Sperrmüll',
                          'https://www.enwi-hz.de/entsorgung/was-wie-wohin/sperrmuell/index.html')]},
            {'text': ('Der Bauhof am Köhlerteich 9 nimmt Elektrogeräte gebührenfrei '
                      'an. Schadstoffe wie nicht ausgehärtete Farben, Lösungsmittel und '
                      'Säuren sammelt dagegen das Schadstoffmobil der enwi, '
                      'kostenlos bis etwa 20 Kilogramm je Anlieferer. Eine Abholung '
                      'am Grundstück kostet 8,27 € je Elektrogerät (Stand 10/2026, '
                      'enwi).'),
             'quellen': [('enwi, Elektrische Haushaltsgeräte',
                          'https://www.enwi-hz.de/entsorgung/was-wie-wohin/elektrische-haushaltsgeraete/index.html'),
                         ('enwi, Schadstoffe',
                          'https://www.enwi-hz.de/entsorgung/was-wie-wohin/schadstoffe/index.html')]},
            {'text': ('Für gebrauchsfähige Möbel nennt die enwi als '
                      'Abgabemöglichkeit unter den karitativen Trägern das '
                      'Gebraucht-Möbelhaus Burchardikloster in Halberstadt, Am '
                      'Kloster 1 (Telefon 03941 58337419); das Haus verkauft '
                      'montags bis freitags von 10 bis 15 Uhr und holt Möbel nach '
                      'Prüfung beim Spender kostenlos ab. Für Nachlasssachen aus '
                      'Wernigerode ist laut Orts- und Gerichtsverzeichnis das '
                      'Amtsgericht Wernigerode in der Rudolf-Breitscheid-Straße 8 '
                      'zuständig.'),
             'quellen': [('enwi, Möbel (gebrauchsfähig)',
                          'https://www.enwi-hz.de/entsorgung/was-wie-wohin/moebel-gebrauchsfaehig/moebel-gebrauchsfaehig.html'),
                         ('Justizportal des Bundes und der Länder, Orts- und Gerichtsverzeichnis (PLZ 38855)',
                          'https://www.justizadressen.nrw.de/de/justiz/gericht?ang=nachlass&plz=38855&ort=')]},
        ],
        'faq_zusatz': ('Geräumtes nimmt der Wertstoffhof Am Köhlerteich 9 an oder die '
                       'kostenlose, über die Abfallwirtschaft Nordharz angemeldete '
                       'Sperrmüllabfuhr des Landkreises Harz.'),
    },
    'quedlinburg': {
        'ortsteile': ['Gernrode', 'Bad Suderode', 'Quarmbeck', 'Münchenhof',
                      'Morgenrot', 'Gersdorfer Burg'],
        'traeger': 'Entsorgungswirtschaft des Landkreises Harz (enwi)',
        'quelle': 'https://www.enwi-hz.de/entsorgung/wertstoffhoefe/quedlinburg/index.html',
        'hof': 'Wertstoffhof Quedlinburg, Groß Orden 27 (Gewerbegebiet '
               '„Magdeburger Straße“), Telefon 03946 99 99 006. Geöffnet Mo–Fr '
               '8:00–18:00 Uhr (Dezember bis Februar 9:00–17:00), Sa 8:00–14:00 '
               'Uhr.',
        'sperrmuell': 'Anmeldung bei der Abfallwirtschaft Nordharz (Telefon '
                      '03943 56 07 38) oder über das Online-Formular der enwi; die '
                      'Abholung ist gebührenfrei, je Anmeldung werden bis zu 10 m³ '
                      'lose mitgenommen. Wer selbst bringt, gibt am Hof bis 2 m³ je '
                      'Anlieferung und Tag kostenlos ab.',
        'beispiele': [
            {
                'titel': 'Einfamilienhaus, 100 m², voll',
                'args': {'objektart': 'haus', 'qm': 100, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 60 m², 2. OG',
                'args': {'objektart': 'wohnung', 'qm': 60,
                         'stockwerk': '2og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Keller, 16 m², voll',
                'beschreibung': 'Ein volles Kellerabteil als Einzelauftrag, '
                                'ohne Wohnung.',
                'args': {'objektart': 'keller', 'qm': 16, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.enwi-hz.de/entsorgung/wertstoffhoefe/quedlinburg/index.html',
        'sperrmuell_quelle': 'https://www.enwi-hz.de/entsorgung/was-wie-wohin/sperrmuell/index.html',
        'lokal_text': [
            {'text': ('Am Wertstoffhof der Welterbestadt Quedlinburg in Groß Orden 27 '
                      'bleibt Sperrmüll bis 2 m³ je Anlieferung und Tag '
                      'gebührenfrei, in Kleinmengen auch Altmetall, Glas und '
                      'Papier; für Bauschutt wird eine Gebühr fällig, je Sorte bis '
                      '1 m³.'),
             'quellen': [('enwi, Wertstoffhof Quedlinburg',
                          'https://www.enwi-hz.de/entsorgung/wertstoffhoefe/quedlinburg/index.html')]},
            {'text': ('Die Abfallwirtschaft Nordharz fährt im Auftrag der enwi '
                      'und holt Sperrmüll gebührenfrei ab. Zur Anmeldung dienen das '
                      'enwi-Formular, die Postkarte aus dem Kalender oder die '
                      'Rufnummer 03943 56 07 38. Nach Eingang vergehen höchstens drei '
                      'Wochen, ehe der Wagen kommt, und eine Antwortkarte nennt den '
                      'Tag. Wer schneller will, zahlt für die Expressabfuhr binnen '
                      'zwei Werktagen 104,17 € bar; Container stellt die enwi dabei '
                      'nicht.'),
             'quellen': [('enwi, Sperrmüll',
                          'https://www.enwi-hz.de/entsorgung/was-wie-wohin/sperrmuell/index.html'),
                         ('enwi, Sperrmüllanmeldung',
                          'https://www.enwi-hz.de/service/formularservice/sperrmuellanmeldung.html')]},
            {'text': ('Zum Sperrmüll zählen laut enwi unter anderem Möbel, '
                      'Matratzen, Teppiche und Auslegware; nicht dazu gehören '
                      'Fahrzeugteile, Türen und Fenster, Elektrogeräte, Hausmüll und '
                      'Schadstoffe. Verwaltungsmäßig besteht die Stadt aus der '
                      'Kernstadt, den Ortschaften Gernrode und Bad Suderode sowie den '
                      'Ortsteilen Quarmbeck, Münchenhof, Morgenrot und Gersdorfer '
                      'Burg.'),
             'quellen': [('enwi, Sperrmüll',
                          'https://www.enwi-hz.de/entsorgung/was-wie-wohin/sperrmuell/index.html'),
                         ('Stadt Quedlinburg, Ortsteile',
                          'https://www.quedlinburg.de/Unsere-Stadt/Ortschaften-und-Ortsteile/Ortsteile/')]},
            {'text': ('Elektrogeräte nimmt die enwi gebührenfrei an, in Quedlinburg '
                      'am Hof Groß Orden 27. Ein weiterer '
                      'Hof liegt auf der ehemaligen Deponie Westerhausen an der '
                      'Ortsverbindungsstraße nach Warnstedt, werktags 9 bis 17 Uhr. '
                      'Schadstoffe gehören zum Schadstoffmobil der enwi, kostenlos '
                      'bis etwa 20 Kilogramm je Anlieferer.'),
             'quellen': [('enwi, Elektrische Haushaltsgeräte',
                          'https://www.enwi-hz.de/entsorgung/was-wie-wohin/elektrische-haushaltsgeraete/index.html'),
                         ('enwi, Schadstoffe',
                          'https://www.enwi-hz.de/entsorgung/was-wie-wohin/schadstoffe/index.html')]},
            {'text': ('Brauchbare Schränke und Sofas muss niemand zerlegen: Das '
                      'Gebrauchtmöbelhaus Burchardikloster der AWZ in Halberstadt '
                      '(Telefon 03941 58337419) holt gut erhaltene Möbel nach '
                      'Besichtigung beim Spender kostenlos ab und liefert verkaufte '
                      'Stücke bei Bedarf nach Hause; die enwi nennt das Haus unter '
                      'den Abgabemöglichkeiten für gebrauchsfähige Möbel. Für '
                      'Nachlassangelegenheiten ist das Amtsgericht Quedlinburg in '
                      'der Adelheidstraße 2 zuständig.'),
             'quellen': [('AWZ, Gebrauchtmöbelhaus',
                          'https://www.awz.net/gebrauchtmoebelhaus/'),
                         ('Justizportal des Bundes und der Länder, Orts- und Gerichtsverzeichnis (PLZ 06484)',
                          'https://www.justizadressen.nrw.de/de/justiz/gericht?ang=nachlass&plz=06484&ort=')]},
        ],
        'faq_zusatz': ('Aussortiertes landet im Wertstoffhof Groß Orden 27 oder in der '
                       'kostenlosen, bei der Abfallwirtschaft Nordharz angemeldeten '
                       'Sperrmüllabfuhr des Landkreises Harz.'),
    },
    'lutherstadt-wittenberg': {
        'ortsteile': ['Altstadt', 'Piesteritz', 'Kleinwittenberg', 'Reinsdorf',
                      'Apollensdorf', 'Pratau', 'Griebo', 'Nudersdorf',
                      'Dobien', 'Euper', 'Kropstädt', 'Straach'],
        'traeger': 'Landkreis Wittenberg, Fachdienst Umwelt und Abfallwirtschaft, '
                   'Abteilung Abfallwirtschaft',
        'quelle': 'https://www.landkreis-wittenberg.de/landkreis-wittenberg-entdecken/abfallwirtschaft/fragen-beantworten/entsorgungsunternehmen/',
        'hof': 'Annahmestelle Lindenstraße 23, Ortsteil Reinsdorf (Betriebshof '
               'Zegarek): Sommer (1. März bis 31. Oktober) Mo–Do 8:00–17:00, Fr '
               '7:00–19:00 Uhr; Winter (1. November bis 28. Februar) Mo–Fr '
               '8:00–17:00 Uhr; jeden 1. und 3. Samstag 9:00–12:00 Uhr. Annahme '
               'nur aus privaten Haushalten, ohne zusätzliche Gebühr.',
        'sperrmuell': 'Abholung auf Abruf mit der Abrufkarte aus der Abfallfibel '
                      'oder im Online-Formular, direkt beim zuständigen Entsorger '
                      '(nicht beim Landkreis); in der Regel binnen 14 Tagen, '
                      'Bereitstellung am Abfuhrtag bis 07:05 Uhr an öffentlichen '
                      'Straßen. Die Anlieferung aus privaten Haushalten an den '
                      'Annahmestellen kostet keine zusätzliche Gebühr.',
        'beispiele': [
            {
                'titel': 'Wohnung, 68 m², 1. OG',
                'args': {'objektart': 'wohnung', 'qm': 68,
                         'stockwerk': '1og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Wohnung, 58 m², 4. OG mit Aufzug',
                'args': {'objektart': 'wohnung', 'qm': 58,
                         'stockwerk': '4og', 'aufzug': True,
                         'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Einfamilienhaus, 120 m², voll',
                'args': {'objektart': 'haus', 'qm': 120, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.landkreis-wittenberg.de/landkreis-wittenberg-entdecken/abfallwirtschaft/fragen-beantworten/entsorgungsunternehmen/',
        'sperrmuell_quelle': 'https://www.landkreis-wittenberg.de/landkreis-wittenberg-entdecken/abfallwirtschaft/abfallarten-trennen/sperrmuell/',
        'lokal_text': [
            {'text': ('In Lutherstadt Wittenberg liegt die Annahmestelle des '
                      'Landkreises im Ortsteil Reinsdorf, Lindenstraße 23 (Betriebshof '
                      'Zegarek). Im Sommer ist dort montags bis donnerstags von 8 bis '
                      '17 Uhr und freitags von 7 bis 19 Uhr geöffnet, im Winter '
                      'montags bis freitags von 8 bis 17 Uhr; samstags jeden ersten '
                      'und dritten des Monats von 9 bis 12 Uhr. Angenommen werden '
                      'Sperrmüll, Grünschnitt, Elektrogeräte, Altmetall und Pappe '
                      'aus Privathaushalten, ohne zusätzliche Gebühr. Seit dem '
                      '1. Juli 2026 gibt es im Landkreis fünf Annahmestellen.'),
             'quellen': [('Landkreis Wittenberg, Entsorgungsunternehmen',
                          'https://www.landkreis-wittenberg.de/landkreis-wittenberg-entdecken/abfallwirtschaft/fragen-beantworten/entsorgungsunternehmen/'),
                         ('Landkreis Wittenberg, Änderungen ab 1. Juli 2026',
                          'https://www.landkreis-wittenberg.de/aenderungen-bei-der-abfallentsorgung-ab-1-juli-2026-im-landkreis-wittenberg/')]},
            {'text': ('Sperrmüll aus bewohnten Privatgrundstücken wird im Holsystem '
                      'abgeholt. Die Abrufkarte aus der Abfallfibel oder das '
                      'Online-Formular geht direkt an den zuständigen Entsorger, '
                      'nicht an den Landkreis; die Abholung folgt in der Regel '
                      'binnen 14 Tagen. Bereitgestellt wird am Abfuhrtag bis 7:05 Uhr '
                      'an öffentlicher Straße. Ausgeschlossen sind Bauabfälle, '
                      'Altfenster, Türen, Reifen, Batterien und Kfz-Teile. Sperrmüll '
                      'von unbewohnten Grundstücken und Wochenendgrundstücken geht '
                      'nicht ins Holsystem, sondern zur ALBA Sachsen GmbH, Rackither '
                      'Gewerbepark 1 in Kemberg, gegen Gebühr nach der '
                      'Abfallgebührensatzung.'),
             'quellen': [('Landkreis Wittenberg, Sperrmüll',
                          'https://www.landkreis-wittenberg.de/landkreis-wittenberg-entdecken/abfallwirtschaft/abfallarten-trennen/sperrmuell/')]},
            {'text': ('Amtlich gliedert sich die Stadt in zwölf Ortschaften, darunter '
                      'Apollensdorf, Griebo, Kropstädt, Nudersdorf, Pratau, Reinsdorf '
                      'und Straach. Zu Reinsdorf gehören Braunsdorf und Dobien, zu '
                      'Abtsdorf Euper und Karlsfeld. Für den Kernort mit Altstadt, '
                      'Kleinwittenberg und Piesteritz nennt Wikipedia weitere '
                      'Ortsteile.'),
             'quellen': [('Stadt Wittenberg, Ortschaften',
                          'https://www.wittenberg.de/portal/seiten/ortschaften-900000088-36670.html'),
                         ('Wikipedia, Lutherstadt Wittenberg (Sekundärquelle)',
                          'https://de.wikipedia.org/wiki/Lutherstadt_Wittenberg')]},
            {'text': ('Problemabfälle aus dem Haushalt nimmt der Landkreis '
                      'kostenlos an: am Schadstoffmobil bis zu 30 Kilogramm oder 30 '
                      'Liter, größere Mengen nur an der Annahmestelle für '
                      'Problemabfälle und Asbest in Kemberg-Rackith. Altgeräte '
                      'gehen an die Betriebshöfe der Entsorger, in der Stadt ist es '
                      'Zegarek in Reinsdorf; Nachtspeicheröfen werden bislang nur '
                      'dort angenommen und sollten vorab telefonisch angemeldet '
                      'werden. Über die Restmülltonne dürfen Elektrogeräte nie '
                      'entsorgt werden.'),
             'quellen': [('Landkreis Wittenberg, Schadstoffe',
                          'https://www.landkreis-wittenberg.de/landkreis-wittenberg-entdecken/abfallwirtschaft/abfallarten-trennen/schadstoffe/'),
                         ('Landkreis Wittenberg, Elektro- und Elektronikgeräte',
                          'https://www.landkreis-wittenberg.de/landkreis-wittenberg-entdecken/abfallwirtschaft/abfallarten-trennen/elektro-und-elektronikgeraete/')]},
            {'text': ('Gut erhaltenes Mobiliar findet im Sozialen Kaufhaus der '
                      'Diakonie in der Juristenstraße neue Abnehmer: Angenommen '
                      'werden gebrauchte Möbel, Haushalts- und Elektrogeräte, '
                      'Kleidung, Spielzeug und Bücher; große, schwere Stücke holt '
                      'das Kaufhaus ab, die Waren werden gegen Spende abgegeben, '
                      'eingekauft wird mit Berechtigungsschein. Nachlasssachen '
                      'führt das Amtsgericht Wittenberg in der Dessauer Straße 291.'),
             'quellen': [('Diakonie Wittenberg, Soziales Kaufhaus mit Kleiderkammer',
                          'https://beratungsstelle-wittenberg.de/hilfe/soziales-kaufhaus-mit-kleiderkammer/'),
                         ('Justizportal des Bundes und der Länder, Orts- und Gerichtsverzeichnis (PLZ 06886)',
                          'https://www.justizadressen.nrw.de/de/justiz/gericht?ang=nachlass&plz=06886&ort=')]},
        ],
        'faq_zusatz': ('Das Geräumte geht aus Privathaushalten an die Annahmestelle '
                       'Reinsdorf, Lindenstraße 23 (ohne zusätzliche Gebühr), oder '
                       'per Abrufkarte oder Online-Formular in die Sperrmüllabholung '
                       'des zuständigen Entsorgers.'),
    },
    'stendal': {
        'ortsteile': ['Bindfelde', 'Borstel', 'Buchholz', 'Dahlen',
                      'Döbbelin-Tornau', 'Groß Schwechten', 'Heeren', 'Insel',
                      'Jarchau', 'Möringen', 'Nahrstedt', 'Staats',
                      'Staffelde', 'Uchtspringe', 'Uenglingen', 'Vinzelberg',
                      'Volgfelde', 'Wahrburg', 'Wittenmoor'],
        'traeger': 'ALS Dienstleistungsgesellschaft mbH, Osterburg',
        'quelle': 'https://www.landkreis-stendal.de/de/abfallwirtschaft.html',
        'hof': ('Abfallannahme und Umladestation (AUS) Stendal, Osterburger Straße '
                '64a: Mo–Fr 7:30–17 Uhr, Sa 7:30–12 Uhr; gefährliche Abfälle Mo–Fr '
                '8–15 Uhr, Sa 8–11 Uhr. Auskunft beim Umweltamt des Landkreises, '
                'Hospitalstraße 1–2, Telefon 03931 60-7305.'),
        'sperrmuell': ('Abholung auf Abruf per Abholkarte aus dem Abfallkalender: einmal '
                       'jährlich kostenlos bis 3 m³, der Termin kommt binnen vier Wochen '
                       'schriftlich. Abfälle aus Haushaltsauflösungen und Renovierungen '
                       'gehören nicht in diese Abfuhr.'),
        'beispiele': [
            {
                'titel': 'Wohnung, 60 m², 4. OG mit Aufzug, mittel',
                'args': {'objektart': 'wohnung', 'qm': 60, 'stockwerk': '4og', 'aufzug': True, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Einfamilienhaus, 130 m², voll',
                'args': {'objektart': 'haus', 'qm': 130, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Scheune, 100 m², voll',
                'args': {'objektart': 'scheune', 'qm': 100, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://als-stendal.de/standort/aus-stendal/',
        'sperrmuell_quelle': 'https://als-stendal.de/abfaelle/hufige-fragen/',
        'lokal_text': [
            {'text': ('Die Abfallannahme und Umladestation der ALS liegt an der '
                      'Osterburger Straße 64a. Montags bis freitags von 7:30 bis 17 '
                      'Uhr und samstags von 7:30 bis 12 Uhr nimmt sie Hausmüll, '
                      'Sperrabfall, Grünabfälle, Elektroaltgeräte, Batterien, '
                      'Schrott, Altkleider, Altholz und Altreifen an; gefährliche '
                      'Abfälle werden werktags von 8 bis 15 Uhr und samstags von 8 '
                      'bis 11 Uhr entgegengenommen. Auskunft: 03931 212056.'),
             'quellen': [('ALS Stendal, AUS Stendal',
                          'https://als-stendal.de/standort/aus-stendal/'),
                         ('ALS Stendal, Öffnungszeiten',
                          'https://als-stendal.de/als/oeffnungszeiten/')]},
            {'text': ('Privathaushalte können einmal im Jahr bis zu 3 m³ '
                      'Sperrabfall kostenlos abholen lassen, per Abholkarte aus dem '
                      'Abfallkalender; der Termin kommt binnen vier Wochen '
                      'schriftlich. Holzartiges und sonstiges Material wird '
                      'getrennt bereitgestellt, weil für jede Sammlung ein eigenes '
                      'Fahrzeug fährt. Einzelstücke dürfen 70 kg wiegen. Abfälle '
                      'aus Haushaltsauflösungen gehören nicht in diese Abfuhr.'),
             'quellen': [('ALS Stendal, Häufige Fragen',
                          'https://als-stendal.de/abfaelle/hufige-fragen/'),
                         ('ALS Stendal, Sperrabfall, Tipps und Tricks',
                          'https://als-stendal.de/abfaelle/sperrabfall/tipps-tricks/')]},
            {'text': ('Elektroaltgeräte holt die ALS einmal im Kalenderjahr '
                      'kostenfrei per Abrufkarte ab, an der Umladestation Stendal '
                      'sind alle sechs Gerätegruppen gebührenfrei abzugeben. '
                      'Schadstoffe nimmt dieselbe Station an (bis 20 kg je '
                      'Anlieferung im Privathaushalt), daneben tourt das '
                      'Schadstoffmobil einmal im Jahr durch den Landkreis, mit '
                      'Behältern bis 10 kg oder 10 Litern.'),
             'quellen': [('ALS Stendal, Elektroaltgeräte',
                          'https://als-stendal.de/abfaelle/elektroaltgeraete/'),
                         ('ALS Stendal, Gefährliche Abfälle',
                          'https://als-stendal.de/abfaelle/gefaehrliche-abfaelle/')]},
            {'text': ('Die ALS Dienstleistungsgesellschaft in Osterburg gründeten '
                      '1992 der Landkreis Stendal sowie die Städte Stendal, '
                      'Tangerhütte und Tangermünde. Zur Hansestadt Stendal gehören '
                      'neunzehn Ortschaften mit eigenem Ortschaftsbüro, von '
                      'Bindfelde über Uchtspringe und Uenglingen bis Wittenmoor.'),
             'quellen': [('ALS Stendal, Über die ALS',
                          'https://als-stendal.de/als/wir-ueber-uns/'),
                         ('Stadt Stendal, Ortschaften',
                          'https://www.stendal.de/de/ortschaften.html')]},
            {'text': ('Zuständig für Nachlässe in Stendal ist laut Justizportal das '
                      'Amtsgericht Stendal, Scharnhorststraße 40. Wer eine '
                      'Haushaltsauflösung vorbereitet, bekommt von der ALS den '
                      'Hinweis, dass dafür private Containerdienste zu beauftragen '
                      'sind.'),
             'quellen': [('Justizportal, Orts- und Gerichtsverzeichnis (Nachlasssachen, PLZ 39576)',
                          'https://www.justizadressen.nrw.de/de/justiz/gericht?ang=nachlass&plzort=39576+Stendal'),
                         ('ALS Stendal, Sperrabfall, Tipps und Tricks',
                          'https://als-stendal.de/abfaelle/sperrabfall/tipps-tricks/')]},
        ],
        'faq_zusatz': ('Geräumtes aus Stendal geht an die ALS-Umladestation in der '
                       'Osterburger Straße 64a; die kostenlose Sperrabfallabholung des '
                       'Landkreises schließt Haushaltsauflösungen aus.'),
    },

    # ══ Sachsen, Raum Leipzig ════════════════════════════════════════════
    'leipzig': {
        'stand_iso': '2026-10',
        'ortsteile': ['Plagwitz', 'Connewitz', 'Gohlis', 'Schleußig',
                      'Lindenau', 'Reudnitz', 'Stötteritz', 'Möckern',
                      'Mockau', 'Paunsdorf', 'Volkmarsdorf',
                      'Kleinzschocher', 'Lößnig', 'Probstheida', 'Grünau'],
        'traeger': 'Stadtreinigung Leipzig',
        'quelle': 'https://stadtreinigung-leipzig.de/sie-kommen-zu-uns/wertstoffhoefe',
        'sperrmuell_quelle': 'https://stadtreinigung-leipzig.de/wir-kommen-zu-ihnen/sperrmuell-und-elektroschrott/sperrmuell',
        # Nachgezogen am 24.09.2026 (Leipzig auf Halle-Tiefe): alle 15 Hoefe
        # stehen in der Standortliste der Stadtreinigung; genannt sind die
        # drei mit den laengsten Zeiten. Sperrmuell: "je Haushalt" war falsch,
        # die Stadtreinigung sagt "pro Auftrag".
        'hof': ('Die Stadtreinigung betreibt 15 Wertstoffhöfe. Ohne '
                'Mittagspause geöffnet sind unter anderem Lößniger Straße 7 '
                '(mit Schadstoffannahme), Augustinerstraße 8 und '
                'Max-Liebermann-Straße 97: Mo–Mi und Fr 10–18 Uhr, Do bis 19 '
                'Uhr, Sa 8:30–14 Uhr. Stoßzeiten sind 10–12 und 16–17 Uhr, '
                'dienstags und donnerstags ist weniger los. Die Abgabe ist '
                'kostenlos, aber nur mit Nachweis, dass Sie in der Stadt gemeldet'
                ' sind – Ausweis oder Meldebescheinigung mitnehmen.'),
        'sperrmuell': ('Die Abholung kostet eine Wertmarke: 25 € vor dem '
                       'Grundstück, 50 €, wenn der Sperrmüll vom Grundstück oder '
                       'aus der Wohnung getragen wird, jeweils bis 4 m³ pro Auftrag. '
                       'Den Termin vereinbaren Sie online oder unter 0341 6571-111 – '
                       'die Stadtreinigung rät zu mindestens fünf Wochen Vorlauf.'),
        # Halteverbot fuer den Raeumtag: amtliche Angaben der Stadt Leipzig
        # (Serviceportal und Antragsformular, Stand 09.2024). Eigene Quelle,
        # weil nicht die Stadtreinigung, sondern das Mobilitaets- und
        # Tiefbauamt zustaendig ist. Nur Fakten der Behoerde - ob und wie der
        # Betrieb die Zone beantragt, ist eine offene Rueckfrage (STAND.md).
        'parken': 'Eine Halteverbotszone genehmigt das Mobilitäts- und '
                  'Tiefbauamt; der Antrag muss spätestens 14 behördliche '
                  'Arbeitstage vorher eingehen, die Gebühr beginnt bei '
                  '32 €. Die Schilder müssen mindestens vier Tage vor dem '
                  'Termin stehen – aufstellen muss sie der Antragsteller oder '
                  'eine beauftragte Firma, nicht die Stadt.',
        'parken_stelle': 'Stadt Leipzig, Mobilitäts- und Tiefbauamt',
        'parken_quelle': 'https://www.leipzig.de/service-portal/dienstleistung/antrag-fuer-eine-haltverbotszone-bei-umzug-598ad33d5cc1a',
        # 02.10.2026: "groesster zusammenhaengender Gruenderzeitbestand
        # Deutschlands" und "3,50 m Deckenhoehe die Regel" waren unbelegt.
        # Jetzt die Zensuszahlen des Statistischen Landesamts Sachsen.
        'bebauung': ('Mehr als die Hälfte der Leipziger Wohnungen (51,6 %) liegt in '
                     'Häusern, die bis 1949 gebaut wurden; 19,1 % stammen aus den '
                     'Jahren 1970 bis 1989. Typisch ist das Mietshaus: 44,5 % der '
                     'Wohnungen liegen in Häusern mit 7 bis 12 Wohnungen, und nur '
                     '13,3 % der bewohnten Wohnungen nutzen ihre Eigentümer selbst '
                     '(Zensus 2022). Für eine Räumung heißt das meist: Treppenhaus, '
                     'Kellerabteil, Hof – die Beispiele oben rechnen genau diese Fälle.'),
        'bebauung_quellen': [
            ('Statistisches Landesamt Sachsen, Zensus 2022, Datenblatt Leipzig',
             'https://zensus.sachsen.de/05_03_Datenblatt_Gemeinden/statistik-sachsen_zensus_gwz_gemeinde_leipzig-stadt.pdf'),
        ],
        'beispiele': [
            {
                'titel': 'Altbauwohnung in Schleußig, 85 m², 3. OG ohne Aufzug',
                'beschreibung': 'Hohe Räume, hohe Schränke, Regale bis unter '
                                'die Decke – deshalb Füllgrad voll, und alles '
                                'geht über das Treppenhaus.',
                'args': {'objektart': 'wohnung', 'qm': 85, 'stockwerk': '3og',
                         'fuellgrad': 'voll'},
            },
            {
                'titel': 'Plattenbauwohnung in Grünau, 60 m², 4. OG mit Aufzug',
                'beschreibung': 'Mit Aufzug fällt der Stockwerkzuschlag weg.',
                'args': {'objektart': 'wohnung', 'qm': 60, 'stockwerk': '4og',
                         'aufzug': True, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Kellerabteil im Gründerzeithaus, 15 m²',
                'beschreibung': 'Der häufigste Einzelauftrag in den '
                                'Altbauvierteln: ein volles Abteil im '
                                'Gewölbekeller.',
                'args': {'objektart': 'keller', 'qm': 15, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Nachlasswohnung in Gohlis, 75 m², 2. OG ohne Aufzug',
                'beschreibung': 'Jahrzehnte bewohnt, entsprechend voll – dazu '
                                'ein Kellerabteil. Eine Halteverbotszone '
                                'braucht Vorlauf.',
                'args': {'objektart': 'wohnung', 'qm': 75, 'stockwerk': '2og',
                         'fuellgrad': 'voll'},
            },
        ],
        'parken_stand_iso': '2024-09',
        'lokal_text': [
            {'text': ('Fünf der 15 Wertstoffhöfe haben keine Mittagspause: '
                      'Augustinerstraße 8, Gärtnerstraße 36, Geithainer Straße 13, '
                      'Lößniger Straße 7 und Max-Liebermann-Straße 97. Der Hof '
                      'Ludwig-Hupfeld-Straße 9 legt dagegen von 13:15 bis 14:00 Uhr '
                      'eine Pause ein. Genutzt werden dürfen die Höfe nur mit '
                      'amtlicher Meldeadresse in der Stadt; Personalausweis oder '
                      'Meldeschein gehören ins Gepäck.'),
             'quellen': [('Stadtreinigung Leipzig, Wertstoffhöfe',
                          'https://stadtreinigung-leipzig.de/sie-kommen-zu-uns/wertstoffhoefe'),
                         ('Standortliste der Stadtreinigung (ArcGIS-Dienst)',
                          'https://services2.arcgis.com/MRKb3GTGdZqdYx9o/ArcGIS/rest/services/Wertstoffhoefe/FeatureServer/0/query')]},
            {'text': ('Sperrmüll holt die Stadtreinigung auf Bestellung ab, je '
                      'Auftrag bis zu 4 m³. Der Termin sollte mindestens fünf Wochen '
                      'vorher bestellt werden; auf dem Gehweg bleibt eine '
                      'Durchgangsbreite von 1,30 m für Passanten frei. Das '
                      'ServiceTeam erreichen Sie unter 0341 6571-111.'),
             'quellen': [('Stadtreinigung Leipzig, Sperrmüll',
                          'https://stadtreinigung-leipzig.de/wir-kommen-zu-ihnen/sperrmuell-und-elektroschrott/sperrmuell'),
                         ('Gebührenübersicht',
                          'https://stadtreinigung-leipzig.de/wir-fuer-eine-schoene-stadt/wir-sind-fuer-sie-da/uebersicht-gebuehren')]},
            {'text': ('Amtlich gliedert sich Leipzig in zehn Stadtbezirke mit 63 '
                      'Ortsteilen. Was im Alltag „Gohlis“ heißt, sind Gohlis-Süd, '
                      'Gohlis-Mitte und Gohlis-Nord; „Mockau“ besteht aus Mockau-Süd '
                      'und Mockau-Nord, Reudnitz gehört zu Reudnitz-Thonberg. Grünau '
                      'umfasst fünf eigene Ortsteile im Stadtbezirk West.'),
             'quellen': [('Stadt Leipzig, Ortsteilkatalog (zehn Stadtbezirke, 63 Ortsteile)',
                          'https://www.leipzig.de/newsarchiv/news/ortsteilkatalog-mit-aktuellen-angaben'),
                         ('Stadt Leipzig, Ortsteilprofil Gohlis-Süd',
                          'https://statistik.leipzig.de/statdist/table_area.aspx?dist=90')]},
            {'text': ('Die Stadtreinigung Leipzig betreibt in der Lößniger Straße 7 '
                      'eine stationäre Schadstoffsammelstelle. Farbreste und '
                      'Dachanstriche nimmt sie bis 30 Liter je Person an. '
                      'Fahrzeugbatterien werden nicht auf den Wertstoffhöfen, '
                      'sondern nur an den Schadstoffsammelstellen angenommen. '
                      'Elektrogeräte vom Fernseher bis zur Waschmaschine lassen '
                      'sich kostenfrei an einem Wertstoffhof abgeben; die Abholung '
                      'kostet eine Gebühr.'),
             'quellen': [('Stadtreinigung Leipzig, Schadstoffe und Elektroschrott',
                          'https://stadtreinigung-leipzig.de/sie-kommen-zu-uns/schadstoffe')]},
            {'text': ('Gut Erhaltenes lässt sich vor Ort tauschen oder '
                      'verschenken: im Laden „täglich rausgeputzt“ in der '
                      'Markgrafenstraße 5, im Foyer des Technischen Rathauses '
                      '(Prager Straße 118-136) und im Online-Verschenkemarkt der '
                      'Stadtreinigung. Angenommen wird, was man allein tragen kann, '
                      'außer Elektrogeräten und Alttextilien. Möbel und '
                      'Haushaltsgeräte nimmt das Sozialwarenhaus (Eisenbahnstraße '
                      '171) an seiner Spendenannahme in der Bülowstraße 35 an und '
                      'holt gebrauchsfähige Spenden nach Absprache kostenfrei ab.'),
             'quellen': [('Stadtreinigung Leipzig, Tauschmarkt',
                          'https://stadtreinigung-leipzig.de/wir-fuer-eine-schoene-stadt/wir-sind-fuer-sie-da/abfallvermeidung/tauschmarkt'),
                         ('Sozialwarenhaus Leipzig, Spenden',
                          'https://sozialwarenhaus.com/spende.html'),
                         ('Sozialwarenhaus Leipzig, Kontakt',
                          'https://sozialwarenhaus.com/kontakt.html')]},
        ],
        'faq_zusatz': ('In Leipzig nehmen 15 Wertstoffhöfe der Stadtreinigung '
                       'Selbstanlieferungen an – allerdings nur mit Leipziger '
                       'Meldeadresse.'),
    },
    'schkeuditz': {
        'ortsteile': ['Dölzig', 'Freiroda', 'Gerbisdorf', 'Glesien', 'Hayna',
                      'Kleinliebenau', 'Kursdorf', 'Radefeld', 'Wolteritz'],
        'traeger': 'Kreiswerke Delitzsch GmbH / ASG mbH des Landkreises Nordsachsen',
        'quelle': 'https://www.kwdz.de/entsorgung/wertstoffh%C3%B6fe.html',
        'hof': ('Wertstoffhof Schkeuditz/Radefeld im Entsorgungszentrum Radefeld, '
                'Seilerweg 2, 04158 Leipzig (Güterverkehrszentrum). Öffnungszeiten '
                'führt die AbfallApp des Landkreises.'),
        'sperrmuell': ('Sperrmüll aus Haushalten des Landkreises Nordsachsen in '
                       'haushaltsüblichen Mengen kostenfrei am Wertstoffhof, mit Ausweis '
                       'oder Gebührenbescheid; Gewerbe zahlt. Abgaben aus kompletten '
                       'Haushaltsauflösungen zählen laut ASG-Flyer nicht als kostenfreier '
                       'Sperrmüll.'),
        'beispiele': [
            {
                'titel': 'Gewerbefläche, 500 m², mittel',
                'args': {'objektart': 'gewerbe', 'qm': 500, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Einfamilienhaus in Dölzig, 120 m², mittel',
                'args': {'objektart': 'haus', 'qm': 120, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Wohnung, 68 m², 1. OG, mittel',
                'args': {'objektart': 'wohnung', 'qm': 68, 'stockwerk': '1og', 'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.kwdz.de/entsorgung/wertstoffh%C3%B6fe.html',
        'sperrmuell_quelle': 'https://www.kwdz.de/entsorgung/sperrm%C3%BCllanmeldung.html',
        'lokal_text': [
            {'text': ('Für Haushalte aus dem Landkreis Nordsachsen nimmt der '
                      'Wertstoffhof Schkeuditz/Radefeld Sperrmüll, Grünschnitt, '
                      'Rasen, Laub sowie Elektro- und Elektronikschrott kostenfrei '
                      'an. Er liegt als Entsorgungszentrum Radefeld im '
                      'Güterverkehrszentrum Leipzig, Seilerweg 2. Ausweis oder '
                      'Gebührenbescheid gehören ins Gepäck, denn das Personal prüft '
                      'die Herkunft. Gewerbebetriebe zahlen. Die Öffnungszeiten '
                      'führt die AbfallApp des Landkreises unter „Standorte“.'),
             'quellen': [('Kreiswerke Delitzsch, Wertstoffhöfe',
                          'https://www.kwdz.de/entsorgung/wertstoffh%C3%B6fe.html')]},
            {'text': ('Wer nicht selbst fahren möchte, meldet Sperrmüll, '
                      'Elektroaltgeräte oder Metallschrott zur Abholung an, '
                      'höchstens zweimal im Jahr und bis 4 m³. Gültig wird die '
                      'Anmeldung erst mit der Terminbestätigung per E-Mail; am '
                      'Abholtag steht das Material bis 6:00 Uhr am Gehweg. '
                      'Komplette Haushaltsauflösungen zählen laut ASG-Flyer nicht '
                      'zum kostenfreien Sperrmüll.'),
             'quellen': [('Kreiswerke Delitzsch, Sperrmüllanmeldung',
                          'https://www.kwdz.de/entsorgung/sperrm%C3%BCllanmeldung.html'),
                         ('ASG Nordsachsen, Flyer Wertstoffhof Taucha (Stand 01.01.2024)',
                          'https://asg-nordsachsen.de/images/unternehmen/Prospekt%20Wertstoffhof%20Taucha%202024.pdf')]},
            {'text': ('Farben, Lösemittel und Pflanzenschutzmittel nimmt der '
                      'Landkreis nur in den sechs Schadstoffwochen des Jahres auf '
                      'den Höfen an, je Anlieferer und Woche etwa 5 Liter '
                      'Lösemittel oder 5 Liter gefährliche Farben, 10 kg Pestizide. '
                      'Lithium-Ionen-Akkus gehen ausschließlich nach Spröda, Torgau '
                      'oder Oschatz; Leuchtstoffröhren dagegen auf jeden Hof.'),
             'quellen': [('Kreiswerke Delitzsch, Schadstoffsammlung 2026 (PDF)',
                          'https://www.kwdz.de/images/service/schadstoffsammlung_2026.pdf')]},
            {'text': ('Brauchbares muss nicht auf den Hof: Der Tausch- und '
                      'Verschenkemarkt des Landkreises Nordsachsen vermittelt '
                      'Möbel, Hausrat, Büromöbel und Haushaltsgeräte kostenlos von '
                      'Haushalt zu Haushalt. Inserate lassen sich mit bis zu fünf '
                      'Fotos einstellen und werden nach einer Prüfung '
                      'freigeschaltet.'),
             'quellen': [('Tausch- und Verschenkemarkt des Landkreises Nordsachsen',
                          'https://www.verschenkemarkt-lk-nordsachsen.de/')]},
            {'text': ('Nach einem Todesfall ist für Schkeuditzer Einwohner das '
                      'Amtsgericht Eilenburg als Nachlassgericht zuständig '
                      '(Walther-Rathenau-Straße 9); Erbausschlagung und Erbschein '
                      'beginnen dort mit einem Formular und einem Termin. Die Stadt '
                      'hat neben der Kernstadt neun Ortsteile von Dölzig bis '
                      'Wolteritz und zählt 19.022 Einwohner (31.12.2025).'),
             'quellen': [('Amtsgericht Eilenburg, Nachlassgericht',
                          'https://www.justiz.sachsen.de/ageb/nachlassgericht-4331.html'),
                         ('Stadt Schkeuditz, Zahlen und Fakten',
                          'https://www.schkeuditz.de/wirtschaft-bauen/wirtschaftsstandort/zahlen-und-fakten/')]},
        ],
        'faq_zusatz': ('Geräumtes geht in Schkeuditz auf den Wertstoffhof Radefeld, in '
                       'die angemeldete Sperrmüllabholung des Landkreises oder, wenn es '
                       'noch brauchbar ist, über den Verschenkemarkt Nordsachsen weiter.'),
    },
    'taucha': {
        'ortsteile': ['Cradefeld', 'Dewitz', 'Graßdorf', 'Merkwitz', 'Plösitz',
                      'Pönitz', 'Seegeritz', 'Sehlis'],
        'traeger': 'Kreiswerke Delitzsch (KWD) für den Landkreis Nordsachsen',
        'quelle': 'https://www.kwdz.de/entsorgung/wertstoffh%C3%B6fe.html',
        'hof': ('Wertstoffhof Taucha, Jubischstraße 9, 04425 Taucha (Wertstoffhof '
                'des Landkreises); Öffnungszeiten führt die AbfallApp des '
                'Landkreises.'),
        'sperrmuell': ('Sperrmüll aus Haushalten des Landkreises Nordsachsen kostenfrei '
                       'am Hof, höchstens 4 m³ je Anlieferung, mit Ausweis oder '
                       'Gebührenbescheid. Haushaltsauflösungen und Scheunenentrümpelungen '
                       'zählen laut ASG-Flyer nicht als kostenfreier Sperrmüll.'),
        'beispiele': [
            {
                'titel': 'Keller, 18 m², voll',
                'args': {'objektart': 'keller', 'qm': 18, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus, 140 m², voll',
                'args': {'objektart': 'haus', 'qm': 140, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 70 m², 2. OG, mittel',
                'args': {'objektart': 'wohnung', 'qm': 70, 'stockwerk': '2og', 'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.kwdz.de/entsorgung/wertstoffh%C3%B6fe.html',
        'sperrmuell_quelle': 'https://asg-nordsachsen.de/images/unternehmen/Prospekt%20Wertstoffhof%20Taucha%202024.pdf',
        'lokal_text': [
            {'text': ('In der Jubischstraße 9 steht der Wertstoffhof Taucha, der '
                      'den früheren Platz seit dem 9. Januar 2024 ersetzt. '
                      'Haushalte aus dem Landkreis geben dort Sperrmüll, '
                      'Grünschnitt, Rasen, Laub und Elektroschrott kostenfrei ab, '
                      'Sperrmüll bis 4 m³ je Anlieferung, Grünschnitt bis 2 m³. Die '
                      'Stadt Taucha verweist für die aktuellen Zeiten auf die '
                      'AbfallApp des Landkreises.'),
             'quellen': [('Kreiswerke Delitzsch, Wertstoffhöfe',
                          'https://www.kwdz.de/entsorgung/wertstoffh%C3%B6fe.html'),
                         ('Stadt Taucha, Müllentsorgung',
                          'https://www.taucha.de/service/buergerservice/muellentsorgung/'),
                         ('ASG Nordsachsen, Flyer Wertstoffhof Taucha (Stand 01.01.2024)',
                          'https://asg-nordsachsen.de/images/unternehmen/Prospekt%20Wertstoffhof%20Taucha%202024.pdf')]},
            {'text': ('Was in die Mülltonne passt oder im Sack kommt, gilt nicht '
                      'als Sperrmüll; Möbel, Matratzen, Teppiche, Auslegware und '
                      'Gartenmöbel schon. Ausdrücklich kein kostenfreier Sperrmüll '
                      'sind Renovierungs- und Bauabfälle, Kfz-Teile, Altreifen '
                      'sowie Abfälle aus kompletten Haushaltsauflösungen oder '
                      'Werkstatt- und Scheunenentrümpelung.'),
             'quellen': [('ASG Nordsachsen, Flyer Wertstoffhof Taucha (Stand 01.01.2024)',
                          'https://asg-nordsachsen.de/images/unternehmen/Prospekt%20Wertstoffhof%20Taucha%202024.pdf')]},
            {'text': ('Haushaltsschadstoffe nimmt der Landkreis nur in sechs '
                      'Sammelwochen jährlich auf den Wertstoffhöfen an; die Termine '
                      'je Hof stehen in der AbfallApp. Je Woche und Anlieferer '
                      'gelten Höchstmengen, etwa 5,0 Liter Lösemittel, 1,0 Liter '
                      'Säuren oder 30 Batterien. Elektroschrott dagegen bleibt '
                      'jederzeit kostenfrei, Leuchtstoffröhren gehen auf jeden Hof.'),
             'quellen': [('Kreiswerke Delitzsch, Schadstoffsammlung 2026 (PDF)',
                          'https://www.kwdz.de/images/service/schadstoffsammlung_2026.pdf'),
                         ('ASG Nordsachsen, Flyer Wertstoffhof Taucha (Stand 01.01.2024)',
                          'https://asg-nordsachsen.de/images/unternehmen/Prospekt%20Wertstoffhof%20Taucha%202024.pdf')]},
            {'text': ('Im Tausch- und Verschenkemarkt des Landkreises Nordsachsen '
                      'können Tauchaer Haushalte Möbel, Hausrat, Kinderzubehör oder '
                      'Werkzeug kostenlos anbieten; bis zu fünf Fotos pro Inserat '
                      'sind erlaubt, die Freischaltung folgt nach einer Prüfung '
                      'spätestens am nächsten Tag. Die Stadt Taucha zählt 16.071 '
                      'Einwohner (Stand 06/2025).'),
             'quellen': [('Tausch- und Verschenkemarkt des Landkreises Nordsachsen',
                          'https://www.verschenkemarkt-lk-nordsachsen.de/'),
                         ('Stadt Taucha, Taucha in Zahlen',
                          'https://www.taucha.de/wirtschaft/standort/taucha-in-zahlen/')]},
            {'text': ('Nachlassgericht für Taucha ist das Amtsgericht Eilenburg. '
                      'Telefonisch erreicht man die Nachlassabteilung unter 03423 '
                      '654321, 654322 oder 654459, Unterlagen lassen sich auch im '
                      'Nachtbriefkasten abgeben. Zur Stadt gehören acht Ortsteile, '
                      'von Cradefeld und Dewitz (mit Döbitz) über Merkwitz und '
                      'Plösitz bis Seegeritz und Sehlis.'),
             'quellen': [('Amtsgericht Eilenburg, Nachlassgericht',
                          'https://www.justiz.sachsen.de/ageb/nachlassgericht-4331.html'),
                         ('Wikipedia, Taucha (Sekundärquelle)',
                          'https://de.wikipedia.org/wiki/Taucha')]},
        ],
        'faq_zusatz': ('Geräumtes aus Taucha geht auf den Wertstoffhof Jubischstraße 9, '
                       'in die angemeldete Sperrmüllabholung des Landkreises oder über '
                       'den Verschenkemarkt Nordsachsen weiter.'),
    },
    'delitzsch': {
        'ortsteile': ['Beerendorf', 'Brodau', 'Döbernitz', 'Selben',
                      'Zschepen', 'Benndorf', 'Laue', 'Schenkenberg', 'Rödgen',
                      'Storkwitz', 'Spröda', 'Poßdorf'],
        'traeger': 'Kreiswerke Delitzsch (KWD)',
        'quelle': 'https://www.kwdz.de/entsorgung/wertstoffh%C3%B6fe.html',
        'hof': ('Wertstoffhof Spröda an der B 183a, 04509 Delitzsch OT Spröda '
                '(Entsorgungsanlagen der Kreiswerke Delitzsch).'),
        'sperrmuell': ('Sperrmüll aus Haushalten des Landkreises in haushaltsüblichen '
                       'Mengen am Hof kostenfrei, gegen Herkunftsnachweis. Komplette '
                       'Haushaltsauflösungen zählen laut ASG nicht als kostenfreier '
                       'Sperrmüll.'),
        'beispiele': [
            {
                'titel': 'Wohnung, 72 m², 2. OG, mittel',
                'args': {'objektart': 'wohnung', 'qm': 72, 'stockwerk': '2og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Einfamilienhaus in Schenkenberg, 125 m², voll',
                'args': {'objektart': 'haus', 'qm': 125, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Keller, 14 m², voll',
                'args': {'objektart': 'keller', 'qm': 14, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.kwdz.de/entsorgung/wertstoffh%C3%B6fe.html',
        'sperrmuell_quelle': 'https://www.kwdz.de/entsorgung/sperrm%C3%BCllanmeldung.html',
        'lokal_text': [
            {'text': ('Delitzscher Haushalte fahren zum Wertstoffhof Spröda an der '
                      'B 183a. Die Kreiswerke Delitzsch nehmen dort Sperrmüll, '
                      'Grünschnitt, Rasen, Laub und Elektroschrott in '
                      'haushaltsüblichen Mengen kostenfrei an; Gewerbe- und '
                      'Baustellenmischabfälle sind kostenpflichtig. Betonschotter '
                      'und Kompost werden hier auch verkauft. Wer die Herkunft '
                      'belegen muss, bringt Ausweis oder Gebührenbescheid mit.'),
             'quellen': [('Kreiswerke Delitzsch, Wertstoffhöfe',
                          'https://www.kwdz.de/entsorgung/wertstoffh%C3%B6fe.html')]},
            {'text': ('Statt Selbstanlieferung kann der Sperrmüll abgeholt werden: '
                      'Anmeldung per Online-Verfahren der KWD bzw. der ASG, '
                      'höchstens zweimal im Jahr und bis 4 m³, zusammen mit '
                      'Elektroaltgeräten und Metallschrott. Ein Abholtermin ist '
                      'erst mit der Bestätigungsmail gültig. Ganze '
                      'Haushaltsauflösungen und Werkstattentrümpelungen zählen laut '
                      'ASG nicht zum kostenfreien Sperrmüll.'),
             'quellen': [('Kreiswerke Delitzsch, Sperrmüllanmeldung',
                          'https://www.kwdz.de/entsorgung/sperrm%C3%BCllanmeldung.html'),
                         ('ASG Nordsachsen, Flyer Wertstoffhof Taucha (Stand 01.01.2024)',
                          'https://asg-nordsachsen.de/images/unternehmen/Prospekt%20Wertstoffhof%20Taucha%202024.pdf')]},
            {'text': ('Der Hof Spröda ist einer von drei Standorten im Landkreis, '
                      'die Lithium-Ionen-Akkus annehmen, die anderen beiden liegen '
                      'in Torgau und Oschatz. Sonstige Schadstoffe kommen in den '
                      'sechs Sammelwochen des Jahres an, in Mengen von zum Beispiel '
                      'höchstens 5 Liter Lösemittel oder 10 kg Pestizide.'),
             'quellen': [('Kreiswerke Delitzsch, Schadstoffsammlung 2026 (PDF)',
                          'https://www.kwdz.de/images/service/schadstoffsammlung_2026.pdf')]},
            {'text': ('Noch brauchbare Möbel, Lampen oder Haushaltsgeräte können '
                      'über den Tausch- und Verschenkemarkt des Landkreises '
                      'Nordsachsen weiterwandern. Der Markt ist kommunal, werbefrei '
                      'und ohne eigenes Benutzerkonto nutzbar; Kontaktdaten der '
                      'Interessenten bleiben unveröffentlicht und gehen direkt an '
                      'den Anbieter.'),
             'quellen': [('Tausch- und Verschenkemarkt des Landkreises Nordsachsen',
                          'https://www.verschenkemarkt-lk-nordsachsen.de/')]},
            {'text': ('Das zuständige Nachlassgericht ist das Amtsgericht '
                      'Eilenburg, Walther-Rathenau-Straße 9. Zur Stadt gehören '
                      'zwölf Ortsteile, vom Ortsteilverbund Beerendorf, Brodau, '
                      'Döbernitz, Selben und Zschepen (2.837 Einwohner, 10/2023) '
                      'bis zu Spröda und Poßdorf. Ein Wahrzeichen ist das im 17. '
                      'Jahrhundert als Damenschloss errichtete Barockschloss.'),
             'quellen': [('Amtsgericht Eilenburg, Nachlassgericht',
                          'https://www.justiz.sachsen.de/ageb/nachlassgericht-4331.html'),
                         ('Stadt Delitzsch, Ortsteile',
                          'https://www.delitzsch.de/mein-delitzsch/ortsteile/'),
                         ('Stadt Delitzsch, Barockschloss',
                          'https://www.delitzsch.de/entdecken/stadtbummel/barockschloss/')]},
        ],
        'faq_zusatz': ('Geräumtes aus Delitzsch geht auf den Wertstoffhof Spröda, in die '
                       'angemeldete Sperrmüllabholung oder über den Verschenkemarkt '
                       'Nordsachsen weiter.'),
    },
    'eilenburg': {
        'ortsteile': ['Eilenburg-Berg', 'Eilenburg-Mitte', 'Eilenburg-Ost',
                      'Hainichen', 'Wedelwitz', 'Behlitz', 'Pressen',
                      'Zschettgau', 'Kospa'],
        'traeger': ('Stadt Eilenburg, Abfallwirtschaft; Wertstoffhof der REMONDIS '
                    'Eilenburg GmbH'),
        'quelle': 'https://www.eilenburg.de/rathaus/buergerservice/abfallwirtschaft/',
        'hof': ('Wertstoffhof der REMONDIS Eilenburg GmbH, Wurzener Landstraße 9, '
                '04838 Eilenburg: im Sommer (1.4.–31.10.) Mo–Fr 8–12 und 13–17 '
                'Uhr, Di bis 18 Uhr, Sa 8–12 Uhr. Sperrmüll, Grünschnitt und '
                'Elektro werden kostenlos angenommen.'),
        'sperrmuell': ('Kostenlos auf dem REMONDIS-Gelände zu den Geschäftszeiten: Möbel, '
                       'Matratzen, Teppiche. Nicht dazu zählen Abfälle aus Haus-, Hof- '
                       'und Stallentrümpelungen, Bauschutt, Kfz-Teile und Schrott; Stücke '
                       'über 75 kg oder über 1 m × 2 m sind ausgenommen. Für '
                       'Sperrmüllcontainer gibt es bei der Stadt ein Antragsformular.'),
        'beispiele': [
            {
                'titel': 'Keller, 20 m², voll, einzelne Schadstoffe',
                'beschreibung': ('Einzelauftrag ohne Wohnung: Für kleine Flächen greift die '
                                 'Mindestpauschale. Einzelne Schadstoffe werden mit einem '
                                 'Aufschlag berechnet.'),
                'args': {'objektart': 'keller', 'qm': 20, 'fuellgrad': 'voll', 'sonderabfall': 'wenige'},
            },
            {
                'titel': 'Einfamilienhaus in Eilenburg-Ost, 110 m², mittel',
                'args': {'objektart': 'haus', 'qm': 110, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Wohnung in Eilenburg-Mitte, 65 m², 2. OG, mittel',
                'args': {'objektart': 'wohnung', 'qm': 65, 'stockwerk': '2og', 'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.eilenburg.de/rathaus/buergerservice/abfallwirtschaft/',
        'sperrmuell_quelle': 'https://www.eilenburg.de/rathaus/buergerservice/abfallwirtschaft/',
        'lokal_text': [
            {'text': ('Die Stadt ist beim Landkreis-Angebot die Ausnahme: Die '
                      'städtische Abfallwirtschaft arbeitet mit dem Wertstoffhof '
                      'der REMONDIS Eilenburg GmbH an der Wurzener Landstraße 9 '
                      'zusammen. Dort werden Sperrmüll, Grünschnitt und '
                      'Elektroabfälle kostenlos angenommen; von April bis Oktober '
                      'ist montags bis freitags von 8 bis 12 und 13 bis 17 Uhr '
                      'geöffnet (dienstags bis 18 Uhr), samstags von 8 bis 12 Uhr.'),
             'quellen': [('Stadt Eilenburg, Abfallwirtschaft',
                          'https://www.eilenburg.de/rathaus/buergerservice/abfallwirtschaft/')]},
            {'text': ('Als Sperrmüll zählen Möbel, Matratzen, Teppiche, Koffer und '
                      'Federbetten. Abfälle aus Haus-, Hof- und Stallentrümpelungen '
                      'sind laut Stadt davon ausgenommen, ebenso Bauschutt, '
                      'Kfz-Teile, Schrott wie Fahrräder und Waschmaschinen sowie '
                      'Stücke über 75 kg oder über 1 m × 2 m. Für größere Mengen '
                      'hält die Stadt ein Antragsformular für Sperrmüllcontainer '
                      'bereit.'),
             'quellen': [('Stadt Eilenburg, Abfallwirtschaft',
                          'https://www.eilenburg.de/rathaus/buergerservice/abfallwirtschaft/')]},
            {'text': ('Schadstoffe aus Haushalten, etwa Farb- und Lackreste, '
                      'Lösungsmittel, Pflanzenschutzmittel und Altmedikamente, '
                      'nimmt das Schadstoffmobil auf dem REMONDIS-Hof an. Kostenlos '
                      'geht das nur für Eilenburger und die zugehörigen Dörfer, '
                      'Auswärtige zahlen; der Personalausweis wird kontrolliert. '
                      'Gefäße über 30 Liter oder 20 kg, Gasflaschen und Altöl nimmt '
                      'die Sammlung nicht.'),
             'quellen': [('Stadt Eilenburg, Abfallwirtschaft',
                          'https://www.eilenburg.de/rathaus/buergerservice/abfallwirtschaft/')]},
            {'text': ('Gut Erhaltenes kann im Tausch- und Verschenkemarkt des '
                      'Landkreises Nordsachsen weitergegeben werden, der allen '
                      'Einwohnern des Landkreises offensteht. Zur Auswahl stehen '
                      'unter anderem die Rubriken Möbel, Hausrat und '
                      'Haushaltsgeräte.'),
             'quellen': [('Tausch- und Verschenkemarkt des Landkreises Nordsachsen',
                          'https://www.verschenkemarkt-lk-nordsachsen.de/')]},
            {'text': ('In der Stadt selbst sitzt das Nachlassgericht: das '
                      'Amtsgericht in der Walther-Rathenau-Straße 9. Die Stadt '
                      'gliedert sich in die Stadtteile Berg, Mitte und Ost sowie '
                      'die Ortsteile Behlitz, Hainichen, Kospa, Pressen, Wedelwitz '
                      'und Zschettgau. Beim Muldehochwasser 2002 stand das Wasser '
                      'auf dem Marktplatz über einen Meter hoch.'),
             'quellen': [('Amtsgericht Eilenburg, Nachlassgericht',
                          'https://www.justiz.sachsen.de/ageb/nachlassgericht-4331.html'),
                         ('Stadt Eilenburg, Ortsteile',
                          'https://www.eilenburg.de/leben/ortsteile/'),
                         ('Stadt Eilenburg, Hochwasser 2002',
                          'https://www.eilenburg.de/leben/eilenburg-und-die-mulde/hochwasser-2002/')]},
        ],
        'faq_zusatz': ('Geräumtes von hier geht auf den REMONDIS-Wertstoffhof '
                       'Wurzener Landstraße 9, in einen beantragten Sperrmüllcontainer '
                       'oder über den Verschenkemarkt Nordsachsen weiter.'),
    },
    'torgau': {
        'ortsteile': ['Beckwitz', 'Bennewitz', 'Graditz', 'Kranichau',
                      'Kunzwerda', 'Loßwig', 'Mehderitzsch', 'Melpitz',
                      'Staupitz', 'Welsau', 'Weßnig', 'Zinna'],
        'traeger': 'Abfallwirtschaft Torgau-Oschatz (A.TO)',
        'quelle': 'https://ato-online.de/betriebshoefe',
        'hof': ('Betriebshof Torgau der A.TO, Gewerbering 51, 04860 Torgau, '
                'Telefon 03421 77300-0: Nov.–Feb. Mo–Fr 8–16 Uhr, März–Okt. Mo–Fr '
                '8–17 Uhr (März–Sept. Do bis 18 Uhr), Sa 8–12 Uhr.'),
        'sperrmuell': ('Gebührenfrei auf den Betriebshöfen in haushaltsüblichen Mengen, '
                       'mit Personalausweis. Abholung zweimal jährlich per Abrufkarte aus '
                       'dem Abfallkalender oder Onlineanmeldung; je Stück höchstens 2 m '
                       'Länge und 50 kg. Abfälle aus kompletten Haushaltsauflösungen '
                       'zählen nicht als Sperrmüll.'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus, 120 m², voll',
                'args': {'objektart': 'haus', 'qm': 120, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 72 m², 2. OG, mittel',
                'args': {'objektart': 'wohnung', 'qm': 72, 'stockwerk': '2og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Keller, 16 m², voll',
                'args': {'objektart': 'keller', 'qm': 16, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://ato-online.de/betriebshoefe',
        'sperrmuell_quelle': 'https://ato-online.de/abfallarten/sperrmuell',
        'lokal_text': [
            {'text': ('Am Gewerbering 51 liegt der Betriebshof Torgau der A.TO, '
                      'zugleich Wertstoffhof, Kompostieranlage, Sammelstelle für '
                      'Elektroaltgeräte und Annahme für Haushaltsschadstoffe. Von '
                      'November bis Februar ist montags bis freitags von 8 bis 16 '
                      'Uhr geöffnet, von März bis Oktober bis 17 Uhr, donnerstags '
                      'bis September sogar bis 18 Uhr; samstags gilt 8 bis 12 Uhr. '
                      'Der Personalausweis gehört zum Pflichtgepäck.'),
             'quellen': [('A.TO, Betriebshöfe',
                          'https://ato-online.de/betriebshoefe')]},
            {'text': ('Sperrmüll aus Nordsachsener Haushalten bleibt auf den '
                      'Betriebshöfen gebührenfrei, in haushaltsüblicher Menge. '
                      'Abgeholt wird zweimal jährlich nach Abrufkarte oder '
                      'Onlineanmeldung, jedes Stück höchstens 2 Meter lang und 50 '
                      'Kilogramm schwer, bereitgestellt zwischen 16:00 Uhr am '
                      'Vortag und 6:00 Uhr am Abholtag. Komplette '
                      'Haushaltsauflösungen sowie Scheunen- und '
                      'Werkstattentrümpelungen nennt die A.TO ausdrücklich nicht '
                      'als Sperrmüll.'),
             'quellen': [('A.TO, Sperrmüll',
                          'https://ato-online.de/abfallarten/sperrmuell'),
                         ('A.TO, Voraussetzungen zur Anmeldung',
                          'https://ato-online.de/entsorgung/voraussetzungen-zur-anmeldung')]},
            {'text': ('Schadstoffe nimmt der Betriebshof nur zu festen Terminen an, '
                      'kostenfrei und in haushaltsüblichen Mengen, am besten in '
                      'Originalgebinden, gut verschlossen und kippsicher. '
                      'Lithium-Akkus aus Powerbanks oder Akkuwerkzeug gehen nach '
                      'Torgau, Oschatz oder Spröda. Elektro- und '
                      'Elektronikaltgeräte vom Kühlschrank bis zum Laptop nimmt der '
                      'Hof ohne gesonderte Gebühr an.'),
             'quellen': [('A.TO, Schadstoffentsorgung',
                          'https://ato-online.de/abfallarten/schadstoffentsorgung'),
                         ('Kreiswerke Delitzsch, Schadstoffsammlung 2026 (PDF)',
                          'https://www.kwdz.de/images/service/schadstoffsammlung_2026.pdf')]},
            {'text': ('Was noch gut ist, lässt sich über den Tausch- und '
                      'Verschenkemarkt des Landkreises Nordsachsen verschenken, '
                      'etwa Schränke, Bürostühle oder Haushaltsgeräte. Kompost aus '
                      'Hecken- und Baumschnitt gibt der Betriebshof dagegen mit '
                      'RAL-Gütezeichen ab; die Tonne kostet 15,00 € netto (Stand '
                      '10/2026).'),
             'quellen': [('Tausch- und Verschenkemarkt des Landkreises Nordsachsen',
                          'https://www.verschenkemarkt-lk-nordsachsen.de/'),
                         ('A.TO, Betriebshöfe',
                          'https://ato-online.de/betriebshoefe')]},
            {'text': ('Das Nachlassgericht für den Altkreis Torgau sitzt im '
                      'Amtsgericht am Rosa-Luxemburg-Platz 14; für den Altkreis '
                      'Oschatz gibt es die Zweigstelle in der Brüderstraße 5. '
                      'Torgau hat neben der Kernstadt zwölf Ortsteile, von Beckwitz '
                      'und Graditz bis Weßnig und Zinna.'),
             'quellen': [('Amtsgericht Torgau, Nachlassabteilung',
                          'https://www.justiz.sachsen.de/agto/nachlassabteilung-4501.html'),
                         ('Wikipedia, Torgau (Sekundärquelle)',
                          'https://de.wikipedia.org/wiki/Torgau')]},
        ],
        'faq_zusatz': ('Geräumtes aus Torgau geht zum A.TO-Betriebshof Gewerbering 51, in '
                       'die angemeldete Sperrmüllabholung oder über den Verschenkemarkt '
                       'Nordsachsen weiter.'),
    },
    'markranstaedt': {
        'ortsteile': ['Albersdorf', 'Altranstädt', 'Döhlen', 'Frankenheim',
                      'Gärnitz', 'Göhrenz', 'Großlehna', 'Kulkwitz',
                      'Lindennaundorf', 'Meyhen', 'Priesteblich', 'Quesitz',
                      'Räpitz', 'Schkeitbar', 'Schkölen', 'Seebenisch',
                      'Thronitz'],
        'traeger': 'KELL Kommunalentsorgung Landkreis Leipzig',
        'quelle': 'https://kell-gmbh.de/wertstoffhof-finder/',
        'hof': ('Wertstoffhof Markranstädt im Ortsteil Großlehna, Am Gläschen 9, '
                '04420 Markranstädt: Di 9–12 Uhr, Do 14–18 Uhr, Fr 14–17 Uhr und '
                'jeden 1. Samstag im Monat 8–13 Uhr.'),
        'sperrmuell': ('Am Hof geben Haushalte bis 2 m³ je Anlieferung kostenfrei ab, '
                       'darüber 35,00 € je Anlieferung (KELL, Stand 10/2026), höchstens 5 '
                       'm³; eine Sperrmüllkarte ist dafür seit 2019 nicht mehr nötig. '
                       'Abholung nur für Haushalte per Sperrmüllkarte, Auskunft unter '
                       '034299 7060 10.'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus in Großlehna, 130 m², voll',
                'args': {'objektart': 'haus', 'qm': 130, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Gartengrundstück in Kulkwitz, 200 m², mittel',
                'args': {'objektart': 'garten', 'qm': 200, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Keller, 18 m², voll',
                'args': {'objektart': 'keller', 'qm': 18, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://kell-gmbh.de/wertstoffhof-finder/',
        'sperrmuell_quelle': 'https://kell-gmbh.de/entsorgungswege/',
        'lokal_text': [
            {'text': ('Im Ortsteil Großlehna, Am Gläschen 9, betreibt die KELL den '
                      'Wertstoffhof für Markranstädt. Er ist dienstags von 9 bis '
                      '12, donnerstags von 14 bis 18 und freitags von 14 bis 17 Uhr '
                      'offen, dazu am ersten Samstag im Monat von 8 bis 13 Uhr. An '
                      'Heiligabend, Silvester und Feiertagen bleibt er zu.'),
             'quellen': [('KELL, Wertstoffhof-Finder',
                          'https://kell-gmbh.de/wertstoffhof-finder/')]},
            {'text': ('Haushalte geben bis zu 2 m³ Sperrmüll je Anlieferung '
                      'kostenfrei ab; ab 2 m³ verlangt die KELL 35,00 € (Stand '
                      '10/2026), bei höchstens 5 m³. Eine Sperrmüllkarte braucht es '
                      'dafür seit 2019 nicht mehr. Für die Abholung vor der Tür '
                      'gilt eine Karte; die lose Abholung kostet ab 59,00 € '
                      'Transportgebühr, ein 7-m³-Container 250,00 €.'),
             'quellen': [('KELL, Entsorgungswege',
                          'https://kell-gmbh.de/entsorgungswege/')]},
            {'text': ('Elektroaltgeräte vom Kühlschrank bis zum Toaster sowie '
                      'Geräteakkus und Powerbanks nehmen die Höfe kostenfrei an; '
                      'Akkus sollen vorher aus den Geräten, die Pole abgeklebt '
                      'werden. Schadstoffe wie Farbreste und Lösemittel (bis 30 '
                      'Liter je Anlieferung) gibt es nur samstags in Borna, Grimma, '
                      'Wurzen und Störmthal, nicht in Großlehna.'),
             'quellen': [('KELL, Wertstoffhof-Finder',
                          'https://kell-gmbh.de/wertstoffhof-finder/'),
                         ('KELL, Entsorgungswege',
                          'https://kell-gmbh.de/entsorgungswege/')]},
            {'text': ('Gut Erhaltenes lässt sich im Tausch- und Verschenkmarkt des '
                      'Landkreises Leipzig weitergeben; dort stehen Möbel, '
                      'Haushaltsgeräte und Hausrat zur Auswahl.'),
             'quellen': [('Tausch- und Verschenkmarkt Landkreis Leipzig',
                          'https://www.verschenkmarkt-lk-leipzig.de/'),
                         ('KELL, Entsorgungswege',
                          'https://kell-gmbh.de/entsorgungswege/')]},
            {'text': ('Sterbefälle aus Markranstädt gehören zum Nachlassgericht '
                      'beim Amtsgericht Borna, Leipziger Straße 67a; dort werden '
                      'Erbscheine erteilt und Testamente eröffnet. Die Stadt '
                      'gliedert sich in 17 Ortsteile von Albersdorf bis Thronitz, '
                      'darunter Großlehna, Kulkwitz und Räpitz, und liegt am '
                      'Kulkwitzer See, einem Tagebau-Restloch der 1970er Jahre.'),
             'quellen': [('Amtsgericht Borna, Nachlasssachen',
                          'https://www.justiz.sachsen.de/agbrn/abteilungen-4180.html'),
                         ('Stadt Markranstädt, Zahlen und Fakten',
                          'https://www.markranstaedt.de/de/fakten/fakten.html')]},
        ],
        'faq_zusatz': ('Geräumtes aus Markranstädt geht zum Wertstoffhof Großlehna (Am '
                       'Gläschen 9), in die Sperrmüllabholung der KELL oder, wenn es noch '
                       'gut ist, in den Verschenkmarkt des Landkreises Leipzig.'),
    },
    'borna': {
        'ortsteile': ['Eula', 'Gestewitz', 'Haubitz', 'Kesselshain',
                      'Zedtlitz', 'Neukirchen', 'Wyhra', 'Thräna'],
        'traeger': 'KELL Kommunalentsorgung Landkreis Leipzig',
        'quelle': 'https://kell-gmbh.de/wertstoffhof-finder/',
        'hof': ('Wertstoffhof Borna, Deutzener Straße 73, 04552 Borna: Di 10–18:30 '
                'Uhr, Mi–Fr 9–17 Uhr und jeden 4. Samstag im Monat 8–13 Uhr; '
                'montags geschlossen. Nur hier wird Gipskarton angenommen.'),
        'sperrmuell': ('Am Hof geben Haushalte bis 2 m³ je Anlieferung kostenfrei ab, '
                       'darüber 35,00 € (KELL, Stand 10/2026), höchstens 5 m³; eine '
                       'Sperrmüllkarte ist seit 2019 nicht mehr nötig. Abholung nur für '
                       'Haushalte, Rückfragen unter 034299 7060 10.'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus, 95 m², voll',
                'args': {'objektart': 'haus', 'qm': 95, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Scheune in Eula, 60 m², voll',
                'args': {'objektart': 'scheune', 'qm': 60, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 62 m², 1. OG, mittel',
                'args': {'objektart': 'wohnung', 'qm': 62, 'stockwerk': '1og', 'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://kell-gmbh.de/wertstoffhof-finder/',
        'sperrmuell_quelle': 'https://kell-gmbh.de/entsorgungswege/',
        'lokal_text': [
            {'text': ('Der Wertstoffhof Borna an der Deutzener Straße 73 ist '
                      'montags zu, dienstags von 10 bis 18:30 Uhr und mittwochs bis '
                      'freitags von 9 bis 17 Uhr geöffnet. Zusätzlich gilt der '
                      'vierte Samstag im Monat von 8 bis 13 Uhr, und dann werden '
                      'dort auch Schadstoffe angenommen. Nur in Borna wird '
                      'Gipskarton angenommen: 16,00 € je Anlieferung nach Aushang '
                      'der KELL (Stand 10/2026).'),
             'quellen': [('KELL, Wertstoffhof-Finder',
                          'https://kell-gmbh.de/wertstoffhof-finder/')]},
            {'text': ('Bis 2 m³ je Anlieferung nehmen die Kreishöfe '
                      'Haushalts-Sperrmüll kostenfrei, danach kostet es 35,00 € '
                      '(Stand 10/2026); mehr als 5 m³ gehen nicht in einem Zug. Ein '
                      'Gewerbe zahlt schon ab dem ersten Kubikmeter 22,00 €. Wer '
                      'abholen lässt, beauftragt per Karte oder per Mail an '
                      'entsorgung@kell-gmbh.de; der Termin liegt innerhalb von vier '
                      'Wochen.'),
             'quellen': [('KELL, Entsorgungswege',
                          'https://kell-gmbh.de/entsorgungswege/')]},
            {'text': ('Schadstoffe aus dem Haushalt nehmen Borna, Grimma, Wurzen '
                      'und Störmthal nur an ihren Samstagszeiten an, höchstens 30 '
                      'Liter je Anlieferung, darunter Farbreste, Lacke und '
                      'Lösemittel. Elektroaltgeräte, Geräteakkus und Metallschrott '
                      'bleiben auf dem Hof kostenfrei, Kfz- und Industriebatterien '
                      'nimmt er nicht.'),
             'quellen': [('KELL, Wertstoffhof-Finder',
                          'https://kell-gmbh.de/wertstoffhof-finder/'),
                         ('KELL, Entsorgungswege',
                          'https://kell-gmbh.de/entsorgungswege/')]},
            {'text': ('Das Sozialkaufhaus des Vereins Soziales Borna e.V. in der '
                      'Deutzener Straße 14 holt bei Haushaltsauflösungen Möbel, '
                      'Kühlschränke, Waschmaschinen, Fernseher und Bettwäsche '
                      'kostenlos ab und bereitet sie für Menschen mit geringem '
                      'Einkommen auf. Geöffnet ist montags bis mittwochs 9 bis 16, '
                      'donnerstags 11 bis 18 und freitags 9 bis 14 Uhr; der Verein '
                      'bietet außerdem Beräumung gegen Kostenvoranschlag an.'),
             'quellen': [('Soziales Borna e. V., Sozialkaufhaus',
                          'https://soziales-borna.de/index.php/sozialkaufhaus')]},
            {'text': ('Zuständig für Nachlässe von Bornaer Einwohnern ist das '
                      'Amtsgericht Borna in der Leipziger Straße 67a, wo Erbscheine '
                      'erteilt und Erbausschlagungen beurkundet werden. Zur Stadt '
                      'gehören neben dem Zentrum acht Ortsteile: Eula, Gestewitz, '
                      'Haubitz und Kesselshain im Norden, Zedtlitz, Neukirchen, '
                      'Wyhra und Thräna im Süden.'),
             'quellen': [('Amtsgericht Borna, Nachlasssachen',
                          'https://www.justiz.sachsen.de/agbrn/abteilungen-4180.html'),
                         ('Stadt Borna, Ortsteile',
                          'https://www.borna.de/Stadtverwaltung-und-Buergerservice/Ortsteile.htm')]},
        ],
        'faq_zusatz': ('Geräumtes aus Borna kommt zum Wertstoffhof Deutzener Straße 73, '
                       'in die Sperrmüllabholung der KELL oder, wenn es noch brauchbar '
                       'ist, zum Sozialkaufhaus Soziales Borna e.V. in der Deutzener '
                       'Straße 14.'),
    },
    'grimma': {
        'ortsteile': ['Nerchau', 'Mutzschen', 'Großbothen', 'Großbardau',
                      'Höfgen', 'Döben', 'Dürrweitzschen', 'Beiersdorf',
                      'Leipnitz'],
        'traeger': 'KELL Kommunalentsorgung Landkreis Leipzig',
        'quelle': 'https://kell-gmbh.de/wertstoffhof-finder/',
        'hof': ('Wertstoffhof Grimma, Bahnhofstraße 5, 04668 Grimma: Di 10–18:30 '
                'Uhr, Mi–Fr 9–17 Uhr und jeden 3. Samstag im Monat 8–13 Uhr; '
                'montags geschlossen. Der Landkreis Leipzig betreibt zehn '
                'Wertstoffhöfe.'),
        'sperrmuell': ('Am Hof geben Haushalte bis 2 m³ je Anlieferung kostenfrei ab, '
                       'darüber 35,00 € (KELL, Stand 10/2026), höchstens 5 m³; eine '
                       'Sperrmüllkarte ist seit 2019 nicht mehr nötig. Abholung nur für '
                       'Haushalte.'),
        'beispiele': [
            {
                'titel': 'Keller, 45 m², voll',
                'args': {'objektart': 'keller', 'qm': 45, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus, 120 m², mittel',
                'args': {'objektart': 'haus', 'qm': 120, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Wohnung, 70 m², 1. OG, mittel',
                'args': {'objektart': 'wohnung', 'qm': 70, 'stockwerk': '1og', 'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://kell-gmbh.de/wertstoffhof-finder/',
        'sperrmuell_quelle': 'https://kell-gmbh.de/entsorgungswege/',
        'lokal_text': [
            {'text': ('Der KELL-Wertstoffhof Grimma liegt an der Bahnhofstraße 5 '
                      'und ist dienstags von 10 bis 18:30 Uhr sowie mittwochs bis '
                      'freitags von 9 bis 17 Uhr offen, montags nicht. Dazu kommt '
                      'der dritte Samstag im Monat von 8 bis 13 Uhr; an diesem Tag '
                      'werden dort auch Schadstoffe angenommen. Der Landkreis '
                      'betreibt insgesamt zehn solcher Höfe.'),
             'quellen': [('KELL, Wertstoffhof-Finder',
                          'https://kell-gmbh.de/wertstoffhof-finder/'),
                         ('KELL, Entsorgungswege',
                          'https://kell-gmbh.de/entsorgungswege/')]},
            {'text': ('Wer selbst anliefert, gibt bis 2 m³ Haushalts-Sperrmüll '
                      'kostenfrei ab; ab 2 m³ werden 35,00 € je Anlieferung fällig, '
                      'höchstens 5 m³ pro Fahrt (Stand 10/2026). Die Sperrmüllkarte '
                      'entfällt dafür seit 2019. Eine Abholung nur für Haushalte '
                      'beginnt mit der Karte aus der Abfallbroschüre; lose Abholung '
                      'ab 59,00 € Transportgebühr, innerhalb von vier Wochen.'),
             'quellen': [('KELL, Entsorgungswege',
                          'https://kell-gmbh.de/entsorgungswege/')]},
            {'text': ('In Grimma gibt es Schadstoffe, etwa Farbreste, Lösemittel '
                      'oder Pflanzenschutzmittel, bis 30 Liter je Anlieferung, am '
                      'dritten Samstag des Monats von 8 bis 13 Uhr. '
                      'Elektroaltgeräte, Akkus und Metallschrott aus Haushalten '
                      'bleiben kostenfrei, Akkus sollen vorher aus den Geräten '
                      'genommen werden.'),
             'quellen': [('KELL, Wertstoffhof-Finder',
                          'https://kell-gmbh.de/wertstoffhof-finder/'),
                         ('KELL, Entsorgungswege',
                          'https://kell-gmbh.de/entsorgungswege/')]},
            {'text': ('Der Möbelfundus des Bildungs- und Sozialwerks Muldental am '
                      'Prophetenberg 7 verkauft auf rund 600 m² Polstermöbel, '
                      'Sitzgruppen, Schränke und Lampen, dazu Kleidung aus der '
                      'angeschlossenen Kleiderkammer, und liefert und baut auf. '
                      'Zusätzlich vermittelt der Verschenkmarkt des Landkreises '
                      'Leipzig Gebrauchtes kostenlos.'),
             'quellen': [('Bildungs- und Sozialwerk Muldental, Möbelfundus und Kleiderkammer',
                          'https://www.bsw-muldental.de/projekte/mobelfundus-kleiderkammer'),
                         ('Tausch- und Verschenkmarkt Landkreis Leipzig',
                          'https://www.verschenkmarkt-lk-leipzig.de/')]},
            {'text': ('Nachlasssachen aus Grimma bearbeitet das Amtsgericht Grimma, '
                      'Klosterstraße 9, im Schloss Grimma; das Schloss stand im '
                      'Juni 2013 etwa 80 Zentimeter unter Wasser und liegt heute '
                      'hinter der 2019 eingeweihten, über 2 Kilometer langen '
                      'Hochwasserschutzanlage. Die Stadt umfasst 64 Ortsteile auf '
                      '21.825 Hektar, darunter Nerchau, Großbothen und Mutzschen.'),
             'quellen': [('Amtsgericht Grimma, Historisches',
                          'https://www.justiz.sachsen.de/aggrm/historisches-4257.html'),
                         ('Stadt Grimma, Über die Stadt',
                          'https://www.grimma.de/leben-in-grimma/ueber-die-stadt/')]},
        ],
        'faq_zusatz': ('Geräumtes aus Grimma geht zum Wertstoffhof Bahnhofstraße 5, in '
                       'die Sperrmüllabholung der KELL oder, wenn es noch gut ist, zum '
                       'Möbelfundus am Prophetenberg 7.'),
    },

    # ── Leipziger Umland, recherchiert am 24.09.2026 ────────────────────
    # Alle drei im Landkreis Leipzig, Entsorger KELL. Quellen: KELL
    # Wertstoffhof-Finder (Stand 29.05.2026) und "Entsorgungswege",
    # Ortsteile und Ortsbild aus den Wikipedia-Artikeln der Staedte.
    # Die Sperrmuellregeln des Landkreises gelten fuer alle drei; jede Seite
    # nennt davon den Teil, der fuer den Ort zaehlt, statt denselben Absatz
    # dreimal zu tragen (IS21, Beinahe-Duplikate).
    'markkleeberg': {
        'ortsteile': ['Auenhain', 'Gaschwitz', 'Großstädteln', 'Wachau'],
        'traeger': 'KELL Kommunalentsorgung Landkreis Leipzig',
        'quelle': 'https://kell-gmbh.de/wertstoffhof-finder/',
        'hof': ('Wertstoffhof Markkleeberg, Hauptstraße 321: Di 10–18:30 Uhr, '
                'Mi–Fr 9–17 Uhr, dazu am ersten Samstag im Monat 8–13 Uhr. '
                'Montags, an Heiligabend, an Silvester und an Feiertagen '
                'geschlossen.'),
        'sperrmuell': ('Selbst angeliefert sind bis 2 m³ kostenfrei, darüber kostet es '
                       '35,00 € je Anlieferung, höchstens 5 m³ auf einmal. Zur Abholung '
                       'schicken Sie die Sperrmüllkarte per Post oder E-Mail an die KELL; '
                       'abgeholt wird binnen vier Wochen.'),
        'beispiele': [
            {
                'titel': 'Wohnung, 80 m², 2. OG, mittel',
                'args': {'objektart': 'wohnung', 'qm': 80, 'stockwerk': '2og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Einfamilienhaus, 140 m², voll',
                'args': {'objektart': 'haus', 'qm': 140, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Keller, 12 m², voll',
                'args': {'objektart': 'keller', 'qm': 12, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://kell-gmbh.de/wertstoffhof-finder/',
        'sperrmuell_quelle': 'https://kell-gmbh.de/wp-content/uploads/2026/02/Sperrmuellkarte-fuer-Abholung.pdf',
        'lokal_text': [
            {'text': ('Der KELL-Wertstoffhof an der Hauptstraße 321 öffnet '
                      'dienstags von 10 bis 18:30 Uhr und mittwochs bis freitags '
                      'von 9 bis 17 Uhr; hinzu kommt der erste Samstag im Monat von '
                      '8 bis 13 Uhr. Montags, an Heiligabend, an Silvester und an '
                      'Feiertagen bleibt er zu. Private Haushalte geben Sperrmüll '
                      'bis 2 m³ kostenfrei ab, darüber fallen 35,00 € je '
                      'Anlieferung an, höchstens 5 m³ auf einmal (KELL, Stand '
                      '10/2026). Gezahlt wird bar.'),
             'quellen': [('KELL, Wertstoffhof-Finder',
                          'https://kell-gmbh.de/wertstoffhof-finder/')]},
            {'text': ('Wer den Sperrmüll abholen lässt, schickt die Sperrmüllkarte '
                      'der KELL per Post oder an entsorgung@kell-gmbh.de; den '
                      'Termin teilt die Gesellschaft binnen vier Wochen mit. Lose '
                      'Abholung kostet 59,00 € Transportgebühr bis 500 kg, oberhalb '
                      'von 200 kg kommen 0,20 € je Kilogramm Mehrmenge dazu (KELL, '
                      'Stand 10/2026). Für größere Mengen gibt es Container mit 7 '
                      'oder 10 m³ zu 250,00 €; im öffentlichen Raum verlangt die '
                      'Stadt dafür eine Stellplatzgenehmigung. Das Verfahren steht '
                      'nur privaten Haushalten offen.'),
             'quellen': [('KELL, Sperrmüllkarte für Abholung (PDF)',
                          'https://kell-gmbh.de/wp-content/uploads/2026/02/Sperrmuellkarte-fuer-Abholung.pdf'),
                         ('KELL, Abfallwegweiser Landkreis Leipzig 2025/2026 (PDF), S. 17',
                          'https://kell-gmbh.de/wp-content/uploads/2026/02/Abfallwegweiser-Landkreis-Leipzig-2025-2026.pdf')]},
            {'text': ('Elektroaltgeräte, Batterien und Akkus nehmen die KELL-Höfe '
                      'kostenfrei an; lithiumhaltige Akkus kommen mit abgeklebten '
                      'Polen. Schadstoffe gehen dagegen nicht an jedem Hof über den '
                      'Tisch: Angenommen werden sie samstags von 8 bis 13 Uhr in '
                      'Störmthal (1. Samstag), Wurzen (2.), Grimma (3.) und Borna '
                      '(4. Samstag im Monat), höchstens 30 Liter je Anlieferung. Im '
                      'Frühjahr und Herbst fährt zusätzlich das Schadstoffmobil.'),
             'quellen': [('KELL, Wertstoffhof-Finder',
                          'https://kell-gmbh.de/wertstoffhof-finder/')]},
            {'text': ('Brauchbares muss nicht in den Container: Der Tausch- und '
                      'Verschenkmarkt der KELL vermittelt Möbel und Geräte online, '
                      'und der DRK-Sozialmarkt in Gaschwitz, Neue Straße 2, nimmt '
                      'Elektrogeräte, Hausrat und Kleidung zu seinen Öffnungszeiten '
                      'an. Möbelspenden laufen über den Sozialmarkt Zwenkau, der '
                      'sie nach Terminabsprache kostenfrei abholt.'),
             'quellen': [('Tausch- und Verschenkmarkt Landkreis Leipzig',
                          'https://www.verschenkmarkt-lk-leipzig.de/'),
                         ('DRK Leipzig-Land, Sozialmarkt Markkleeberg',
                          'https://www.drk-leipzig-land.de/angebote/sozialmarkt-markkleeberg.html'),
                         ('DRK Leipzig-Land, Sozialmärkte',
                          'https://www.drk-leipzig-land.de/sozialmaerkte.html')]},
            {'text': ('Für Nachlässe Markkleeberger Einwohner ist laut Justizportal '
                      'das Amtsgericht Borna in der Leipziger Straße 67a zuständig. '
                      'Amtliche Ortsteile sind Auenhain, Gaschwitz, Großstädteln '
                      'und Wachau; Gautzsch, Oetzsch, Raschwitz und Zöbigker gelten '
                      'als Wohnviertel. 679 Kulturdenkmale zählt die Stadt, vom '
                      'Villenviertel Raschwitz mit dem „Weißen Haus“ im agra-Park '
                      'bis zu Gründerzeitzeilen. Einwohner: 25.359 (30.06.2024).'),
             'quellen': [('Justizportal, Orts- und Gerichtsverzeichnis (Nachlasssachen, PLZ 04416)',
                          'https://www.justizadressen.nrw.de/de/justiz/gericht?ang=nachlass&plzort=04416+Markkleeberg'),
                         ('Stadt Markkleeberg, Zahlen und Daten',
                          'https://www.markkleeberg.de/stadt-politik/markkleeberg/zahlen-daten'),
                         ('Stadt Markkleeberg, Wohnviertel',
                          'https://www.markkleeberg.de/wohnen-und-leben/wohnen-in-markkleeberg/wohnviertel')]},
        ],
        'faq_zusatz': ('Geräumtes geht in Markkleeberg an den KELL-Wertstoffhof '
                       '(Hauptstraße 321), per Sperrmüllkarte in die Abholung oder, wenn '
                       'es noch taugt, in den Verschenkmarkt und den DRK-Sozialmarkt '
                       'Gaschwitz.'),
    },
    'wurzen': {
        'ortsteile': ['Dehnitz', 'Nemt', 'Roitzsch', 'Kühren', 'Burkartshain',
                      'Birkenhof', 'Kornhain', 'Mühlbach', 'Nitzschka',
                      'Oelschütz', 'Pyrna', 'Sachsendorf', 'Streuben',
                      'Trebelshain', 'Wäldgen'],
        'traeger': 'KELL Kommunalentsorgung Landkreis Leipzig',
        'quelle': 'https://kell-gmbh.de/wertstoffhof-finder/',
        'hof': ('Wertstoffhof Wurzen, Bäßlerstraße 9 im Gewerbegebiet Nord: Di '
                '10–18:30 Uhr, Mi–Fr 9–17 Uhr. Am zweiten Samstag im Monat 8–13 '
                'Uhr, dann auch mit Schadstoffannahme – Schadstoffe nur an diesem '
                'Samstag, höchstens 30 Liter je Anlieferung.'),
        'sperrmuell': ('Die Abholung läuft über die Sperrmüllkarte der KELL. Lose '
                       'bereitgestellt bis 200 kg fällt nur die Transportgebühr von 59 € '
                       'an, ab 200 kg kommen 20 Cent je Kilogramm dazu; ab 500 kg rät die '
                       'KELL zum Container.'),
        'beispiele': [
            {
                'titel': 'Wohnung, 65 m², 2. OG, mittel',
                'args': {'objektart': 'wohnung', 'qm': 65, 'stockwerk': '2og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Scheune, 60 m², voll',
                'args': {'objektart': 'scheune', 'qm': 60, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus, 120 m², voll, einzelne Schadstoffe',
                'beschreibung': ('Keller, Dachboden und Garage sind im Hauspreis enthalten. '
                                 'Einzelne Schadstoffe werden mit einem Aufschlag '
                                 'berechnet.'),
                'args': {'objektart': 'haus', 'qm': 120, 'fuellgrad': 'voll', 'sonderabfall': 'wenige'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://kell-gmbh.de/wertstoffhof-finder/',
        'sperrmuell_quelle': 'https://kell-gmbh.de/wp-content/uploads/2026/02/Sperrmuellkarte-fuer-Abholung.pdf',
        'lokal_text': [
            {'text': ('Im Gewerbegebiet Nord, Bäßlerstraße 9, betreibt die KELL den '
                      'Wertstoffhof Wurzen. Er ist dienstags von 10 bis 18:30 Uhr '
                      'und mittwochs bis freitags von 9 bis 17 Uhr offen, am '
                      'zweiten Samstag im Monat von 8 bis 13 Uhr; montags und an '
                      'den Feiertagen steht das Tor zu. Privathaushalte bringen '
                      'Sperrmüll bis 2 m³ gebührenfrei, darüber werden 35,00 € je '
                      'Anlieferung fällig (KELL, Stand 10/2026).'),
             'quellen': [('KELL, Wertstoffhof-Finder',
                          'https://kell-gmbh.de/wertstoffhof-finder/')]},
            {'text': ('Elektroaltgeräte, Batterien und Akkus bleiben an den '
                      'KELL-Höfen kostenfrei. Eine Besonderheit hat Wurzen bei '
                      'Schadstoffen: Sie werden nur am zweiten Samstag im Monat '
                      'zwischen 8 und 13 Uhr angenommen, höchstens 30 Liter je '
                      'Anlieferung. Wer an einem anderen Samstag fahren muss, '
                      'findet die Termine in Störmthal, Grimma und Borna.'),
             'quellen': [('KELL, Wertstoffhof-Finder',
                          'https://kell-gmbh.de/wertstoffhof-finder/')]},
            {'text': ('Statt selbst zu fahren, lässt sich Sperrmüll mit der '
                      'KELL-Sperrmüllkarte abholen, nur für private Haushalte und '
                      'binnen vier Wochen nach Beantragung. Die lose Abholung '
                      'kostet 59,00 € Transportgebühr bis 500 kg; über 200 kg '
                      'werden 0,20 € je Kilogramm zusätzlich berechnet (KELL, Stand '
                      '10/2026). Ab 500 kg beantragt man einen Container, 7 oder 10 '
                      'm³ groß, für 250,00 €.'),
             'quellen': [('KELL, Sperrmüllkarte für Abholung (PDF)',
                          'https://kell-gmbh.de/wp-content/uploads/2026/02/Sperrmuellkarte-fuer-Abholung.pdf')]},
            {'text': ('Was noch heil ist, darf über den Tausch- und Verschenkmarkt '
                      'der KELL weiterziehen; dort stehen Anzeigen aus Wurzen neben '
                      'denen aus dem übrigen Landkreis Leipzig. Gebrauchte Möbel '
                      'nimmt zudem der DRK-Sozialmarkt Zwenkau (Schulstraße 19) '
                      'entgegen und holt sie nach Absprache kostenfrei ab.'),
             'quellen': [('Tausch- und Verschenkmarkt Landkreis Leipzig',
                          'https://www.verschenkmarkt-lk-leipzig.de/'),
                         ('DRK Leipzig-Land, Sozialmärkte',
                          'https://www.drk-leipzig-land.de/sozialmaerkte.html')]},
            {'text': ('Nachlassgericht für Wurzen ist laut Justizportal das '
                      'Amtsgericht Grimma, Klosterstraße 9. Zur Stadt gehören neben '
                      'der Kernstadt fünfzehn Ortsteile von Birkenhof bis Wäldgen; '
                      'insgesamt leben dort 16.209 Menschen (Stand 12/2019, '
                      'Stadtangabe). Zu den Wahrzeichen zählen der 1114 geweihte '
                      'romanische Dom St. Marien, das Bischofsschloss am Amtshof '
                      'und der Bismarckturm auf dem Wachtelberg in Dehnitz.'),
             'quellen': [('Justizportal, Orts- und Gerichtsverzeichnis (Nachlasssachen, PLZ 04808)',
                          'https://www.justizadressen.nrw.de/de/justiz/gericht?ang=nachlass&plzort=04808+Wurzen'),
                         ('Tourismus Wurzen, Wurzen im Überblick',
                          'https://www.tourismus-wurzen.de/portal/seiten/wurzen-die-stadt-im-ueberblick-901000368-22901.html'),
                         ('Tourismus Wurzen, Sehenswürdigkeiten',
                          'https://www.tourismus-wurzen.de/sehenswertes-kunst-kultur/sehenswuerdigkeiten/')]},
        ],
        'faq_zusatz': ('Aus Wurzen geht Geräumtes an den KELL-Wertstoffhof in der '
                       'Bäßlerstraße, per Sperrmüllkarte in die Abholung oder in den '
                       'Tausch- und Verschenkmarkt.'),
    },
    'zwenkau': {
        'ortsteile': ['Löbschütz', 'Großdalzig', 'Kleindalzig', 'Tellschütz',
                      'Zitzschen', 'Rüssen-Kleinstorkwitz'],
        'traeger': 'KELL Kommunalentsorgung Landkreis Leipzig',
        'quelle': 'https://kell-gmbh.de/wertstoffhof-finder/',
        'hof': ('Zwenkau hat keinen eigenen Wertstoffhof. Höfe der KELL in der '
                'Umgebung: Markkleeberg, Hauptstraße 321, und Markranstädt im '
                'Ortsteil Großlehna, Am Gläschen 9 – beide am ersten Samstag im '
                'Monat 8–13 Uhr, werktags mit eigenen Zeiten.'),
        'sperrmuell': ('Wer abholen lässt, meldet den Sperrmüll mit der Karte der KELL '
                       'an. Für große Mengen gibt es Container mit 7 oder 10 m³ für je '
                       '250,00 €; auf öffentlichem Grund braucht der Stellplatz eine '
                       'Genehmigung der Stadt.'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus, 130 m², mittel',
                'args': {'objektart': 'haus', 'qm': 130, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Gartengrundstück, 250 m², mittel',
                'args': {'objektart': 'garten', 'qm': 250, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Keller, 20 m², voll',
                'args': {'objektart': 'keller', 'qm': 20, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://kell-gmbh.de/wertstoffhof-finder/',
        'sperrmuell_quelle': 'https://kell-gmbh.de/wp-content/uploads/2026/02/Abfallwegweiser-Landkreis-Leipzig-2025-2026.pdf',
        'lokal_text': [
            {'text': ('Einen eigenen Wertstoffhof gibt es in Zwenkau nicht; die '
                      'nächstgelegenen KELL-Höfe stehen in Markranstädt OT '
                      'Großlehna, Am Gläschen 9, und in Markkleeberg, Hauptstraße '
                      '321. Großlehna öffnet dienstags von 9 bis 12 Uhr, '
                      'donnerstags von 14 bis 18 Uhr und freitags von 14 bis 17 '
                      'Uhr, dazu am ersten Samstag im Monat von 8 bis 13 Uhr. '
                      'Sperrmüll bis 2 m³ ist für Privathaushalte frei (KELL, Stand '
                      '10/2026).'),
             'quellen': [('KELL, Wertstoffhof-Finder',
                          'https://kell-gmbh.de/wertstoffhof-finder/')]},
            {'text': ('Die Alternative zum Selbstfahren ist die Sperrmüllkarte der '
                      'KELL. Sie bringt binnen vier Wochen einen Termin; größere '
                      'Mengen kommen in einen Container mit 7 oder 10 m³, der '
                      '250,00 € kostet (KELL, Stand 10/2026). Steht er im '
                      'öffentlichen Verkehrsraum, braucht es die '
                      'Stellplatzgenehmigung der Stadt, auf dem Grundstück sollte '
                      'die Durchfahrt mindestens 3 m breit sein.'),
             'quellen': [('KELL, Abfallwegweiser Landkreis Leipzig 2025/2026 (PDF), S. 17',
                          'https://kell-gmbh.de/wp-content/uploads/2026/02/Abfallwegweiser-Landkreis-Leipzig-2025-2026.pdf'),
                         ('KELL, Sperrmüllkarte für Abholung (PDF)',
                          'https://kell-gmbh.de/wp-content/uploads/2026/02/Sperrmuellkarte-fuer-Abholung.pdf')]},
            {'text': ('Schadstoffe werden von der KELL nicht in Zwenkau angenommen, '
                      'sondern samstags von 8 bis 13 Uhr in Störmthal, Wurzen, '
                      'Grimma oder Borna, höchstens 30 Liter je Anlieferung. '
                      'Elektroaltgeräte, Batterien und Akkus sind an allen '
                      'KELL-Höfen kostenfrei.'),
             'quellen': [('KELL, Wertstoffhof-Finder',
                          'https://kell-gmbh.de/wertstoffhof-finder/')]},
            {'text': ('Zwenkau besitzt selbst einen Abnehmer für Brauchbares: den '
                      'DRK-Sozialmarkt in der Schulstraße 19 mit über 700 '
                      'Quadratmetern, der Möbel, Elektrogeräte, Spielzeug, Bücher '
                      'und Geschirr führt. Möbelspenden holt das DRK nach '
                      'Terminabsprache kostenfrei ab; Telefon 034203/32439. Online '
                      'vermittelt zudem der Verschenkmarkt der KELL.'),
             'quellen': [('DRK Leipzig-Land, Sozialmarkt Zwenkau',
                          'https://www.drk-leipzig-land.de/angebote/sozialmarkt-zwenkau.html'),
                         ('DRK Leipzig-Land, Sozialmärkte',
                          'https://www.drk-leipzig-land.de/sozialmaerkte.html'),
                         ('Tausch- und Verschenkmarkt Landkreis Leipzig',
                          'https://www.verschenkmarkt-lk-leipzig.de/')]},
            {'text': ('Das Nachlassgericht für Zwenkau ist laut Justizportal das '
                      'Amtsgericht Borna. Zur Stadt gehören die Ortsteile Löbschütz '
                      '(seit 1974), Großdalzig, Kleindalzig, Tellschütz, Zitzschen '
                      'und Rüssen-Kleinstorkwitz. Prägend ist der Tagebau: Der '
                      'Abbauschein stammt von 1921, die Kohleförderung endete am '
                      '30.09.1999, die Flutung des Zwenkauer Sees begann 2007.'),
             'quellen': [('Justizportal, Orts- und Gerichtsverzeichnis (Nachlasssachen, PLZ 04442)',
                          'https://www.justizadressen.nrw.de/de/justiz/gericht?ang=nachlass&plzort=04442+Zwenkau'),
                         ('Stadt Zwenkau, Zahlen und Fakten',
                          'https://www.zwenkau.de/stadt-wirtschaft/standortinformation/zahlen-und-fakten/'),
                         ('Stadt Zwenkau, Tagebaugeschichte',
                          'https://www.zwenkau.de/stadt-wirtschaft/historisches/tagebaugeschichte/')]},
        ],
        'faq_zusatz': ('Geräumtes aus Zwenkau geht an die KELL-Höfe Großlehna oder '
                       'Markkleeberg, per Sperrmüllkarte in die Abholung oder in den '
                       'DRK-Sozialmarkt in der Schulstraße.'),
    },

    # ══ Sachsen, Raum Dresden / Elbtal ═══════════════════════════════════
    'dresden': {
        'ortsteile': ['Neustadt', 'Striesen', 'Blasewitz', 'Pieschen',
                      'Löbtau', 'Cotta', 'Gorbitz', 'Prohlis', 'Klotzsche',
                      'Strehlen', 'Gruna', 'Laubegast', 'Leuben', 'Trachau',
                      'Kaditz', 'Tolkewitz'],
        'traeger': 'Stadtreinigung Dresden (SRD)',
        'quelle': ('https://www.srdresden.de/ueber-uns/wertstoffhoefe/'),
        'hof': ('Fünf Wertstoffhöfe der Stadtreinigung: Friedrichstadt '
                '(Altonaer Straße 15), Reick (Georg-Mehrtens-Straße 1), '
                'Hammerweg 23, Johannstadt (Hertelstraße 3) und Kaditz '
                '(Scharfenberger Straße 146). Jeder Haushalt darf pro Halbjahr '
                '4 m³ Sperrmüll kostenlos auf den Wertstoffhöfen abgeben. '
                'Geöffnet Mo–Fr 7:00–19:00 Uhr (Johannstadt und Kaditz erst ab '
                '12:00 Uhr), Sa 8:00–14:00 Uhr.'),
        # EIG397 (02.10.2026): gegen dresden.de/sperrmuell geprueft (Seite vom
        # 22.04.2026). Neu: Elektro-Altgeraete nicht bei der Sperrmuellabholung,
        # Heraustragen als Zusatzleistung, Express nur online, Dresden-Pass.
        # Die fuer 2027 geplanten Gebuehren (PM 043/2026) stehen bewusst nicht
        # hier: Der Stadtrat entscheidet erst am 29.10.2026.
        'sperrmuell': ('Bis 4 m³ holt die Stadtreinigung im Auftrag der Stadt für '
                       '29,37 € vor dem Grundstück ab, in der Regel innerhalb von '
                       'vier Wochen; die Expressabholung binnen drei Werktagen kostet '
                       '88,12 € und ist nur online bestellbar. Elektro-Altgeräte wie '
                       'Kühlschrank, Waschmaschine oder Fernseher nimmt die '
                       'Sperrmüllabholung nicht mit, sie werden getrennt beauftragt. '
                       'Das Heraustragen aus Wohnung oder Keller ist eine '
                       'kostenpflichtige Zusatzleistung des Entsorgers und muss bei der '
                       'Anmeldung angegeben werden. Wer einen Dresden-Pass hat, kann '
                       'einmal im Jahr gebührenfrei abholen lassen.'),
        # Bis 02.10.2026 ein unbelegter Satz ("Dresden ist zweigeteilt ...").
        # Jetzt die Zahlen der Kommunalen Statistikstelle (Stand 2024), Quelle
        # sichtbar ueber ``bebauung_quellen``.
        'bebauung': ('Gut jede vierte Dresdner Wohnung (26,4 %) steht in einem Haus, '
                     'das vor 1919 gebaut wurde; im Stadtbezirk Neustadt stammen '
                     '1.556 der 2.725 Mehrfamilienhäuser aus dieser Zeit. In den '
                     'großen Wohnhäusern mit mehr als 20 Wohnungen liegt dagegen die '
                     'Hälfte der Wohnungen (50,5 %) in Bauten von 1970 bis 1990. '
                     'Dazu kommen 34.128 Eigenheime, fast 40 % davon nach 1990 '
                     'gebaut (Zahlen der Kommunalen Statistikstelle, Stand 2024). '
                     'Daraus folgen die drei Rechenbeispiele oben: Altbau ohne '
                     'Aufzug, Wohnblock mit Aufzug, Haus mit Keller und Dachboden.'),
        'bebauung_quellen': [
            ('Kommunale Statistikstelle Dresden, Wohnungen nach Baujahresgruppen 2024',
             'https://www.dresden.de/media/pdf/statistik/Statistik_3206_Wohnungen-Baujahr-15.pdf'),
            ('Kommunale Statistikstelle Dresden, Eigenheime und Mehrfamilienhäuser 2024',
             'https://www.dresden.de/media/pdf/statistik/Statistik_3204_Eigenheime.pdf'),
        ],
        'beispiele': [
            {
                'titel': 'Gründerzeitwohnung in der Äußeren Neustadt, 78 m², 2. OG',
                'beschreibung': 'Kein Aufzug – jedes Möbelstück geht über das Treppenhaus.',
                'args': {'objektart': 'wohnung', 'qm': 78, 'stockwerk': '2og',
                         'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Plattenbauwohnung in Gorbitz, 58 m², 4. OG mit Aufzug',
                'beschreibung': 'Höher gelegen als die Altbauwohnung und '
                                'trotzdem günstiger: Mit Aufzug entfällt der '
                                'Stockwerkzuschlag vollständig.',
                'args': {'objektart': 'wohnung', 'qm': 58, 'stockwerk': '4og',
                         'aufzug': True, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Haus am Elbhang, 160 m², voll',
                'beschreibung': 'Erdgeschoss bis Dachboden samt Keller, dazu '
                                'einzelne Sonderabfälle wie Farben und Lacke.',
                'args': {'objektart': 'haus', 'qm': 160, 'fuellgrad': 'voll',
                         'sonderabfall': 'wenige'},
            },
        ],
        'stand_iso': '2026-10',
        'sperrmuell_quelle': 'https://www.dresden.de/de/stadtraum/umwelt/abfall-stadtreinigung/entsorgung/sperrmuell.php',
        # EIG397 (02.10.2026): jeder Absatz am Original nachgelesen. Der fruehere
        # zweite Absatz wiederholte die Sperrmuell-Karte fast woertlich und ist
        # durch die Regel fuer Mengen ueber 4 m³ ersetzt; die Gliederung kommt
        # jetzt von dresden.de statt aus Wikipedia ("64 statistische
        # Stadtteile" stand auf keiner Stadtseite und ist entfallen); die
        # Gebrauchtwaren-Annahme gilt laut Stadt (Seite vom 01.10.2026) auf
        # vier Hoefen, nicht mehr auf drei.
        'lokal_text': [
            {'text': ('Die fünf Wertstoffhöfe der Stadtreinigung Dresden – '
                      'Friedrichstadt, Hammerweg, Johannstadt, Kaditz und Reick – '
                      'sind unter einer Nummer erreichbar: 0351 44 55-118. Sperrmüll '
                      'und Altholz nehmen sie bis 4 m³ an, Elektrogeräte auf allen '
                      'Höfen; Schadstoffe sind je Haushalt und Halbjahr bis höchstens '
                      '25 Liter möglich, berechnet über die Verpackungsgrößen.'),
             'quellen': [('Stadtreinigung Dresden, Wertstoffhöfe',
                          'https://www.srdresden.de/ueber-uns/wertstoffhoefe/')]},
            {'text': ('Was über 4 m³ hinausgeht, nimmt die Veolia Umweltservice Ost '
                      'GmbH Am Lugaer Graben 20 an: Die Menge wird verwogen und gegen '
                      'Entgelt entsorgt (Mo–Fr 7–18 Uhr, Sa 7–13 Uhr). Einen Container '
                      'stellt die Stadt bei der Sperrmüllabholung nicht; für '
                      'Haushaltsauflösungen verweist sie auf private Firmen. Ein '
                      'Container im öffentlichen Straßenraum braucht eine '
                      'Sondergenehmigung des Straßen- und Tiefbauamts.'),
             'quellen': [('Stadt Dresden, Sperrmüll',
                          'https://www.dresden.de/de/stadtraum/umwelt/abfall-stadtreinigung/entsorgung/sperrmuell.php')]},
            {'text': ('Dresden gliedert sich in zehn Stadtbezirke – Altstadt, '
                      'Blasewitz, Cotta, Klotzsche, Leuben, Loschwitz, Neustadt, '
                      'Pieschen, Plauen und Prohlis – und neun Ortschaften, darunter '
                      'Cossebaude, Langebrück, Schönfeld-Weißig und Weixdorf.'),
             'quellen': [('Stadt Dresden, Stadtbezirke',
                          'https://www.dresden.de/de/rathaus/stadtbezirke.php'),
                         ('Stadt Dresden, Ortschaften',
                          'https://www.dresden.de/de/rathaus/ortschaften.php')]},
            {'text': ('Noch brauchbare Möbel nimmt in Dresden der Soziale '
                      'Möbeldienst des SUFW in der Industriestraße 17 entgegen; '
                      'nach Rücksprache holt er Möbel, Haushaltsgroßgeräte und '
                      'Kühlschränke ab. Saubere, funktionsfähige Gebrauchsgüter '
                      'nehmen außerdem die Höfe Friedrichstadt, Hammerweg, Kaditz '
                      'und Reick an – die Stadt nennt diesen Weg aber nur die '
                      'zweitbeste Lösung.'),
             'quellen': [('Stadt Dresden, Sozialer Möbeldienst des SUFW',
                          'https://www.dresden.de/de/stadtraum/umwelt/abfall-stadtreinigung/entsorgung/gebrauchtwaren/SUFW.php'),
                         ('Stadt Dresden, Gebrauchtwaren an den Wertstoffhöfen',
                          'https://www.dresden.de/de/stadtraum/umwelt/abfall-stadtreinigung/entsorgung/gebrauchtwaren/wsh_gebraucht.php')]},
            {'text': ('Zuständig ist das Amtsgericht Dresden, Roßbachstraße 6, '
                      'immer dann, wenn der Verstorbene zuletzt in der Stadt '
                      'Dresden wohnte. Persönliche Vorsprache gibt es nur nach '
                      'Terminabsprache, der Erbscheinsantrag geht per Post ein.'),
             'quellen': [('Amtsgericht Dresden, Nachlassabteilung',
                          'https://www.justiz.sachsen.de/agdd/nachlassabteilung-4373.html')]},
        ],
        'faq_zusatz': ('Selbst abgeben können Sie Sperrmüll in Dresden an den fünf '
                       'Wertstoffhöfen der Stadtreinigung; je Haushalt und Halbjahr '
                       'sind bis zu 4 m³ kostenfrei. Größere Mengen nimmt die Veolia '
                       'Am Lugaer Graben 20 gegen Entgelt an.'),
    },
    'pirna': {
        'ortsteile': ['Copitz', 'Posta', 'Neundorf', 'Rottwerndorf',
                      'Zuschendorf', 'Jessen', 'Obervogelgesang',
                      'Niedervogelgesang'],
        'traeger': 'Zweckverband Abfallwirtschaft Oberes Elbtal (ZAOE)',
        'quelle': 'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/',
        'hof': ('Wertstoffhof Pirna-Copitz, Nordstraße 5 – einer von zwölf '
                'ZAOE-Höfen. Geöffnet Mo 9–14, Mi 13–18, Fr 9–14 und Sa 8–12 '
                'Uhr, dienstags und donnerstags geschlossen. Bisher der einzige'
                ' ZAOE-Hof mit digitalem Self-Service (MAEX-App, Pilotprojekt '
                'seit 3. März 2025).'),
        'sperrmuell': ('Der ZAOE holt Sperrmüll zweimal im Jahr je Haushalt bis zu 3 '
                       'm³ gebührenfrei am Grundstück ab – Bestellung per Karte aus '
                       'dem Abfallkalender oder online, Abholung innerhalb von vier '
                       'Wochen. Dieselbe Freimenge gilt bei Anlieferung am Hof gegen '
                       'ein ausgedrucktes Formular.'),
        'bebauung': 'Pirnas Altstadt ist fast vollständig erhalten und steht '
                    'unter Denkmalschutz – enge Gassen, Innenhöfe, kaum '
                    'Stellflächen. Am Elbufer kommt das Hochwasserthema dazu: '
                    'Keller in der Unterstadt sind seit 2002 vielfach '
                    'ausgeräumt und trockengelegt.',
        'beispiele': [
            {
                'titel': 'Altstadtwohnung, 68 m², 2. OG',
                'beschreibung': 'Normal möbliert, Zugang über den Hof. Der Tragweg vom Fahrzeug bis zur Haustür bestimmt den '
                'Aufwand.',
                'args': {'objektart': 'wohnung', 'qm': 68,
                         'stockwerk': '2og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Keller in der Unterstadt, 18 m², voll',
                'beschreibung': 'Am Elbufer sind die Keller seit 2002 '
                                'vielfach ausgeräumt und trockengelegt worden '
                                '– geräumt wird trotzdem regelmäßig nach.',
                'args': {'objektart': 'keller', 'qm': 18, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus in Copitz, 120 m², voll',
                'beschreibung': 'Auf der rechten Elbseite ist die Zufahrt '
                                'frei. Keller, Dachboden und Garage sind im '
                                'Hauspreis enthalten.',
                'args': {'objektart': 'haus', 'qm': 120, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/',
        'sperrmuell_quelle': 'https://www.zaoe.de/entsorgung/vor-dem-grundstueck/abholung-sperrmuell-und-elektroaltgeraete/',
        'lokal_text': [
            {'text': ('Der Zweckverband Abfallwirtschaft Oberes Elbtal (ZAOE) '
                      'betreibt insgesamt zwölf Wertstoffhöfe, und jeder Einwohner '
                      'des Verbandsgebiets darf jeden davon nutzen, unabhängig vom '
                      'Wohnsitz. Am Hof in Pirna-Copitz lassen sich als Pilotprojekt '
                      'Zeitfenster über die MAEX-App buchen, montags bis freitags von'
                      ' 8 bis 18 Uhr und samstags von 8 bis 12 Uhr.'),
             'quellen': [('ZAOE, Wertstoffhöfe',
                          'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/'),
                         ('Self-Service Pirna-Copitz',
                          'https://www.zaoe.de/entsorgung/am-wertstoffhof/entsorgungsnachweise/self-service-wertstatthof-pirna-copitz/')]},
            {'text': ('Wer Sperrmüll vom ZAOE abholen lässt, stellt ihn spätestens um'
                      ' 6:00 Uhr am Abholtag bereit, frühestens am Vorabend; einzelne'
                      ' Möbelteile dürfen höchstens 70 Kilogramm wiegen. Lassen Sie '
                      'Möbel aus Wohnung oder Keller tragen, fällt eine Servicegebühr'
                      ' je angefangener Viertelstunde an, am Grundstück ist die '
                      'Abholung gebührenfrei. Wer am Hof abgibt, bringt ein '
                      'ausgedrucktes Formular mit; was in einen Sack oder Karton '
                      'passt, gilt nicht als Sperrmüll, Bauschutt und Autoteile sind '
                      'ausgeschlossen.'),
             'quellen': [('ZAOE, Abholung Sperrmüll',
                          'https://www.zaoe.de/entsorgung/vor-dem-grundstueck/abholung-sperrmuell-und-elektroaltgeraete/'),
                         ('Formular Sperrmüllabgabe',
                          'https://www.zaoe.de/entsorgung/am-wertstoffhof/formular-sperrmuellabgabe/')]},
            {'text': ('Das Stadtportal führt die Pirnaer Altstadt und die übrigen '
                      'Stadt- und Ortsteile einzeln auf, darunter Copitz, '
                      'Sonnenstein, Graupa, Zehista, Jessen, Liebethal, Birkwitz und '
                      'Pratzschwitz; eine Gesamtzahl nennt es nicht.'),
             'quellen': [('Stadt Pirna, Stadt- und Ortsteile',
                          'https://www.pirna.de/stadtinfo/stadtportraet/stadt-und-ortsteile/')]},
            {'text': ('Gefährliche Haushaltsreste sammelt der ZAOE mit dem '
                      'Schadstoffmobil regelmäßig und gebührenfrei, in '
                      'haushaltsüblichen Mengen von höchstens 25 Kilogramm oder 30 '
                      'Litern je Gebinde. Größere Mengen bis 60 Liter nimmt er zu '
                      'den Sammelterminen auf den Wertstoffhöfen an; außerhalb '
                      'dieser Termine gibt es keine Annahme. Reste wasserlöslicher '
                      'Farben gelten nicht als Schadstoff.'),
             'quellen': [('ZAOE, Schadstoffhaltige Abfälle',
                          'https://www.zaoe.de/abfall-infos/abfallarten/schadstoffe/')]},
            {'text': ('Das Diakonie-Kaufhaus in der Rottwerndorfer Straße nimmt '
                      'Möbel, Küchen, Haushaltswaren, Elektrogeräte, Spielzeug und '
                      'Fahrräder als Schenkung an. Möbel und Küchen baut das Haus '
                      'kostenlos ab und holt sie ab, sofern vorab Fotos per E-Mail '
                      'oder WhatsApp vorliegen und die Möbel aufgebaut sind. Die '
                      'Warenannahme ist montags bis donnerstags von 9 bis 15 Uhr; '
                      'Spendenquittungen gibt es für Schenkungen nicht.'),
             'quellen': [('Diakonie Pirna, Diakonie-Kaufhaus',
                          'https://www.diakonie-pirna.de/diakonie-kaufhaus/')]},
        ],
        'faq_zusatz': ('In Pirna nimmt der ZAOE Sperrmüll am Wertstoffhof Copitz '
                       '(Nordstraße 5) an; bis zu 3 m³ sind zweimal im Jahr '
                       'gebührenfrei.'),
    },
    'heidenau': {
        'ortsteile': ['Heidenau-Süd', 'Gommern', 'Großsedlitz',
                      'Kleinsedlitz', 'Mügeln', 'Wölkau'],
        'traeger': 'Zweckverband Abfallwirtschaft Oberes Elbtal (ZAOE)',
        'quelle': 'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/',
        'hof': ('In Heidenau gibt es keinen der 12 ZAOE-Höfe; nutzbar sind alle, '
                'zum Beispiel Pirna-Copitz, Nordstraße 5 (Mo und Fr 9–14, Mi '
                '13–18, Sa 8–12 Uhr) und Kleincotta, Cotta B 40 in Dohma (im '
                'Sommer Mo–Mi und Fr 8–17, Do 8–18, Sa 8–12 Uhr).'),
        'sperrmuell': ('Abholung am Grundstück zweimal jährlich bis 3 m³ '
                       'gebührenfrei, Bestellung per Karte aus dem Abfallkalender '
                       'oder Onlineformular; Anlieferung am Hof ebenfalls bis 3 m³ '
                       'gegen ausgedrucktes Formular.'),
        'beispiele': [
            {
                'titel': 'Wohnung, 52 m², 3. OG',
                'beschreibung': 'Weniger Fläche heißt weniger Grundpreis; das '
                                'Stockwerk ohne Aufzug bleibt der Aufschlag.',
                'args': {'objektart': 'wohnung', 'qm': 52,
                         'stockwerk': '3og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Kellerabteil in Großsedlitz, 12 m², voll',
                'args': {'objektart': 'keller', 'qm': 12, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus in Mügeln, 95 m², voll',
                'args': {'objektart': 'haus', 'qm': 95, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/',
        'sperrmuell_quelle': 'https://www.zaoe.de/entsorgung/vor-dem-grundstueck/abholung-sperrmuell-und-elektroaltgeraete/',
        'lokal_text': [
            {'text': ('Heidenau liegt mit rund 16.500 Einwohnern und etwa 11 km² im '
                      'oberen Elbtal und ist nach Pirna und Freital die drittgrößte '
                      'Stadt im Landkreis Sächsische Schweiz-Osterzgebirge. Als '
                      'touristische Attraktion nennt die Stadt den Barockgarten '
                      'Großsedlitz. Laut Wikipedia gliedert sie sich in sechs '
                      'Stadtteile: Gommern, Großsedlitz, Heidenau-Süd, Kleinsedlitz, '
                      'Mügeln und Wölkau.'),
             'quellen': [('Stadt Heidenau, Stadtportrait',
                          'https://www.heidenau.de/Stadt-Rathaus/Stadt/Stadtportrait/'),
                         ('Wikipedia, Heidenau (Sekundärquelle)',
                          'https://de.wikipedia.org/wiki/Heidenau_(Sachsen)')]},
            {'text': ('Der Zweckverband Abfallwirtschaft Oberes Elbtal betreibt '
                      'zwölf Höfe, keiner davon liegt in Heidenau; jeder Einwohner '
                      'darf aber jeden nutzen. Pirna-Copitz, Nordstraße 5, nimmt '
                      'montags und freitags von 9 bis 14 Uhr, mittwochs von 13 bis '
                      '18 Uhr und samstags von 8 bis 12 Uhr an, Kleincotta (Cotta B '
                      '40, Dohma) donnerstags bis 18 Uhr und samstags von 8 bis 12 '
                      'Uhr. Auf beiden Höfen ist Zahlung mit EC-Karte möglich.'),
             'quellen': [('ZAOE, Adressen und Öffnungszeiten',
                          'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/')]},
            {'text': ('Sperrmüll nimmt der Hof nur mit dem ausgedruckten, '
                      'unterschriebenen Formular an: zweimal im Jahr bis zu 3 m³, '
                      'gebührenfrei. Bauabfälle und Autoteile zählen nicht dazu. '
                      'Für die Abholung vor dem Grundstück gelten dieselben zwei '
                      'Termine mit je höchstens 3 m³; bestellt wird per Karte aus '
                      'dem Abfallkalender oder online.'),
             'quellen': [('ZAOE, Abgabe von Sperrmüll am Wertstoffhof',
                          'https://www.zaoe.de/entsorgung/am-wertstoffhof/formular-sperrmuellabgabe/'),
                         ('ZAOE, Abholung von Sperrmüll und Elektroaltgeräten',
                          'https://www.zaoe.de/entsorgung/vor-dem-grundstueck/abholung-sperrmuell-und-elektroaltgeraete/')]},
            {'text': ('Altgeräte und Gefahrstoffe laufen in Heidenau über getrennte '
                      'Wege. Elektroaltgeräte nimmt der ZAOE gebührenfrei auf '
                      'seinen Höfen an, vollständig und ohne Batterien. Schadstoffe '
                      'wie Altöl, Lackreste oder Quecksilberthermometer gehören ans '
                      'Schadstoffmobil; Munition, Asbest und radioaktive Abfälle '
                      'werden dort nicht genommen. Als haushaltsüblich gelten '
                      'höchstens 25 Kilogramm oder 30 Liter je Gebinde.'),
             'quellen': [('ZAOE, Elektroaltgeräte',
                          'https://www.zaoe.de/abfall-infos/abfallarten/elektroaltgeraete/'),
                         ('ZAOE, Schadstoffhaltige Abfälle',
                          'https://www.zaoe.de/abfall-infos/abfallarten/schadstoffe/')]},
            {'text': ('Brauchbares muss nicht entsorgt werden: Das '
                      'Diakonie-Kaufhaus DIKA in Pirna, Rottwerndorfer Straße, '
                      'nimmt Möbel, Küchen, Elektrogeräte und Haushaltswaren als '
                      'Schenkung an, montags bis donnerstags von 9 bis 15 Uhr; '
                      'Möbel und Küchen werden nach Vorab-Fotos kostenlos abgeholt. '
                      'Zuständig für Nachlässe aus Heidenau ist das Amtsgericht '
                      'Pirna im Schloßhof 7.'),
             'quellen': [('Diakonie Pirna, Diakonie-Kaufhaus',
                          'https://www.diakonie-pirna.de/diakonie-kaufhaus/'),
                         ('Amtsgericht Pirna, Nachlassgericht',
                          'https://www.justiz.sachsen.de/agpir/nachlassgericht-4542.html'),
                         ('Justizportal des Bundes und der Länder, Orts- und Gerichtsverzeichnis (PLZ 01809)',
                          'https://www.justizadressen.nrw.de/de/justiz/gericht?ang=nachlass&plz=01809&ort=')]},
        ],
        'faq_zusatz': ('Das Geräumte geht aus Heidenau entweder in die '
                       'ZAOE-Sperrmüllabholung (zweimal jährlich bis 3 m³, '
                       'Bestellkarte oder Onlineformular) oder mit Formular zu einem '
                       'ZAOE-Hof, etwa Pirna-Copitz oder Kleincotta.'),
    },
    'freital': {
        'ortsteile': ['Deuben', 'Potschappel', 'Döhlen', 'Hainsberg',
                      'Burgk', 'Birkigt', 'Zauckerode', 'Niederhäslich',
                      'Pesterwitz', 'Somsdorf', 'Wurgwitz', 'Weißig',
                      'Kleinnaundorf', 'Saalhausen', 'Schweinsdorf'],
        'traeger': 'Zweckverband Abfallwirtschaft Oberes Elbtal (ZAOE)',
        'quelle': 'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/',
        'hof': ('Wertstoffhof Saugrund, Schachtstraße 107 (Betreiber ZAOE). '
                'Geöffnet vom 1. März bis 15. November Mo, Di, Do, Fr '
                '8:00–17:00, Mi 8:00–18:00, Sa 8:00–12:00 Uhr.'),
        'sperrmuell': ('Zweimal im Jahr holt der ZAOE je Haushalt bis zu 3 m³ '
                       'Sperrmüll und Elektroaltgeräte kostenlos ab. Bestellung per '
                       'Abholkarte aus dem Abfallkalender oder online, Abholung '
                       'innerhalb von vier Wochen. Alternativ Anlieferung am Saugrund.'),
        'bebauung': ('Freital ist 1921 aus Deuben, Döhlen und Potschappel '
                     'zusammengelegt worden und zieht sich schmal durchs '
                     'Weißeritztal. Später kamen weitere Orte dazu, zuletzt 1999 '
                     'Pesterwitz.'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus in Burgk, 105 m², voll',
                'beschreibung': 'Erdgeschoss bis Dachboden samt Keller. Der Preis hängt am '
                'Volumen.',
                'args': {'objektart': 'haus', 'qm': 105, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung in Deuben, 62 m², 2. OG',
                'beschreibung': 'Normal möbliert, Zugang über das Treppenhaus.',
                'args': {'objektart': 'wohnung', 'qm': 62,
                         'stockwerk': '2og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Gartengrundstück in Somsdorf, 250 m²',
                'beschreibung': 'Laube, Bewuchs und Altlasten auf der Fläche '
                                '– gerechnet wird nach Grundstücksfläche, '
                                'nicht nach Wohnfläche.',
                'args': {'objektart': 'garten', 'qm': 250,
                         'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'sperrmuell_quelle': 'https://www.zaoe.de/entsorgung/vor-dem-grundstueck/abholung-sperrmuell-und-elektroaltgeraete/',
        'lokal_text': [
            {'text': ('Freital entstand am 1. Oktober 1921 durch den Zusammenschluss '
                      'von Deuben, Döhlen und Potschappel. Heute führt die Stadt 15 '
                      'Stadtteile: neben diesen dreien Niederhäslich, Schweinsdorf, '
                      'Zauckerode, Birkigt, Burgk, Hainsberg, Saalhausen, Wurgwitz, '
                      'Kleinnaundorf, Weißig, Somsdorf und Pesterwitz, das 1999 als '
                      'letzter dazukam.'),
             'quellen': [('Stadt Freital, Stadtteile',
                          'https://www.freital.de/stadtteile')]},
            {'text': ('Zuständig für die Abfallwirtschaft ist der Zweckverband '
                      'Abfallwirtschaft Oberes Elbtal (ZAOE). Der Termin der Abholung'
                      ' wird spätestens eine Woche vorher gemeldet, bereitgestellt '
                      'wird bis 6 Uhr, Möbelteile dürfen höchstens 70 Kilogramm '
                      'wiegen. Abholung aus Wohnung oder Keller ist '
                      'gebührenpflichtiger Vollservice, abgerechnet je angefangener '
                      'Viertelstunde.'),
             'quellen': [('ZAOE, Abholung Sperrmüll',
                          'https://www.zaoe.de/entsorgung/vor-dem-grundstueck/abholung-sperrmuell-und-elektroaltgeraete/')]},
            {'text': ('Sperrmüll bis 3 m³ nehmen die Höfe des ZAOE mit ausgefülltem '
                      'Abgabeformular entgegen. Saugrund gehört neben Gröbern und '
                      'Kleincotta zu den drei Höfen, die zusätzlich Asbest, größere '
                      'Baustoffmengen, Wurzelstöcke und Dämmstoffe annehmen; samstags'
                      ' wird in Saugrund kein Asbest angenommen.'),
             'quellen': [('ZAOE, Annahme von Abfällen',
                          'https://www.zaoe.de/entsorgung/am-wertstoffhof/annahme-von-abfaellen/'),
                         ('Alle Wertstoffhöfe',
                          'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/')]},
            {'text': ('Elektroaltgeräte holt der ZAOE in Freital am Grundstück '
                      'gebührenfrei ab, gemeinsam mit bis zu drei Kubikmetern '
                      'Sperrmüll, zweimal im Jahr. Die Geräte müssen getrennt vom '
                      'Sperrmüll stehen, weil ein anderes Fahrzeug kommt; jedes '
                      'darf höchstens 1,5 Kubikmeter groß sein und nicht zerlegt '
                      'werden. Elektrokleingeräte werden nur zusammen mit '
                      'Großgeräten mitgenommen.'),
             'quellen': [('ZAOE, Abholung von Sperrmüll und Elektroaltgeräten',
                          'https://www.zaoe.de/entsorgung/vor-dem-grundstueck/abholung-sperrmuell-und-elektroaltgeraete/')]},
            {'text': ('Das Gebrauchtwarenhaus des DRK Freital an der Dresdner '
                      'Straße 303 verkauft Möbel, Textilien, Elektrokleingeräte, '
                      'Geschirr, Bücher und Spielzeug aus Spenden und '
                      'Haushaltsauflösungen. Angenommen werden gut erhaltene, '
                      'zeitgemäße Möbel und funktionstüchtige Haushaltsgeräte; bei '
                      'Abholung oder Lieferung hilft das Haus auf Anfrage. Geöffnet '
                      'ist montags, mittwochs und freitags von 9 bis 13 Uhr, '
                      'dienstags und donnerstags von 11 bis 17 Uhr.'),
             'quellen': [('DRK Kreisverband Freital, Gebrauchtwarenhaus und Möbelhalle',
                          'https://www.drkfreital.de/angebote/alltagshilfe/gebrauchtwarenhaus-und-moebelhalle.html')]},
        ],
        'faq_zusatz': ('In Freital nimmt der Wertstoffhof Saugrund an der '
                       'Schachtstraße 107 Sperrmüll bis 3 m³ mit Abgabeformular an; '
                       'der ZAOE holt ihn zweimal im Jahr kostenlos ab.'),
    },
    'meissen': {
        'ortsteile': ['Altstadt', 'Cölln', 'Triebischtal', 'Zscheila',
                      'Bohnitzsch', 'Niederfähre', 'Obermeisa',
                      'Niedermeisa', 'Oberspaar', 'Niederspaar', 'Korbitz',
                      'Proschwitz', 'Siebeneichen'],
        'traeger': 'Zweckverband Abfallwirtschaft Oberes Elbtal (ZAOE)',
        'quelle': 'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/',
        'hof': ('Wertstoffhof Meißen, Am Wall 7, 01662 Meißen: Mo, Mi, Fr '
                '13–18 Uhr, Sa 8–12 Uhr, Di und Do geschlossen. Mehr als 3 m³ '
                'Sperrmüll nimmt der ZAOE in Gröbern an (Radeburger Straße 65, '
                'Niederau).'),
        'sperrmuell': ('Abholung am Grundstück zweimal jährlich bis 3 m³ '
                       'gebührenfrei, bestellt per Bestellkarte aus dem '
                       'Abfallkalender oder im Onlineformular des ZAOE; die '
                       'Abholung erfolgt innerhalb von vier Wochen nach Eingang '
                       'der Bestellung. Abgabe am Hof mit ausgedrucktem '
                       'Formular.'),
        'beispiele': [
            {
                'titel': 'Wohnung in der Altstadt, 75 m², 2. OG, voll',
                'beschreibung': 'Ohne Aufzug im 2. Obergeschoss, voll gefüllt: '
                                'Stockwerkzuschlag und Füllgrad gehen in die '
                                'Rechnung ein.',
                'args': {'objektart': 'wohnung', 'qm': 75,
                         'stockwerk': '2og', 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus, 120 m², mittel',
                'args': {'objektart': 'haus', 'qm': 120,
                         'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Keller, 15 m², voll',
                'args': {'objektart': 'keller', 'qm': 15, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/',
        'sperrmuell_quelle': 'https://www.zaoe.de/entsorgung/vor-dem-grundstueck/abholung-sperrmuell-und-elektroaltgeraete/',
        'lokal_text': [
            {'text': ('Am Wall 7 liegt der Meißner Wertstoffhof des ZAOE: montags, '
                      'mittwochs und freitags von 13 bis 18 Uhr, samstags von 8 bis '
                      '12 Uhr; dienstags und donnerstags bleibt er geschlossen. '
                      'Genutzt werden darf jeder der zwölf ZAOE-Höfe, unabhängig vom '
                      'Wohnsitz. Mehr als 3 m³ Sperrmüll nehmen nur Gröbern, '
                      'Kleincotta und Saugrund an; Gröbern in Niederau öffnet im '
                      'Sommer montags, mittwochs, donnerstags und freitags von 8 bis '
                      '17 Uhr, dienstags bis 18 Uhr und samstags von 8 bis 12 Uhr.'),
             'quellen': [('ZAOE, Adressen und Öffnungszeiten',
                          'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/'),
                         ('ZAOE, Annahme von Abfällen',
                          'https://www.zaoe.de/entsorgung/am-wertstoffhof/annahme-von-abfaellen/')]},
            {'text': ('Beim Sperrmüll vor dem Grundstück zählt die Bereitstellung: '
                      'frühestens am Vorabend, spätestens bis 6:00 Uhr am Termin, '
                      'gut sichtbar außerhalb des Grundstücks an der Stelle, wo auch '
                      'die Abfallbehälter geleert werden. Große Möbel sind in Stücke '
                      'bis 70 Kilogramm und 1,5 Kubikmeter zu zerlegen, '
                      'Elektroaltgeräte separat bereitzustellen, weil ein anderes '
                      'Fahrzeug sie holt. Nicht mitgenommen werden Restabfall, '
                      'Schadstoffe, Reifen, Gartenabfälle und Renovierungsabfälle '
                      'wie Fenster, Türen oder Bauschutt. Der Termin liegt innerhalb '
                      'von vier Wochen nach der Bestellung und wird spätestens eine '
                      'Woche vorher mitgeteilt.'),
             'quellen': [('ZAOE, Abholung von Sperrmüll und Elektroaltgeräten',
                          'https://www.zaoe.de/entsorgung/vor-dem-grundstueck/abholung-sperrmuell-und-elektroaltgeraete/')]},
            {'text': ('Brauchbares muss nicht in den Container: Der ZAOE führt für '
                      'Meißen den Allerhand-Gebrauchtwarenladen der '
                      'Produktionsschule Moritzburg, Niederfährer Straße 31 '
                      '(Telefon 03521/406509), als Abgabestelle auf, ohne Anspruch '
                      'auf Vollständigkeit. Zur Stadtgliederung nennt Wikipedia '
                      'unter anderem Altstadt, Cölln, Triebischtal, Zscheila, Korbitz '
                      'und Siebeneichen.'),
             'quellen': [('ZAOE, Sperrmüll',
                          'https://www.zaoe.de/abfall-infos/abfallarten/sperrmuell/'),
                         ('Wikipedia, Meißen (Sekundärquelle)',
                          'https://de.wikipedia.org/wiki/Mei%C3%9Fen')]},
            {'text': ('Farbreste, Altöl oder Energiesparlampen gehören nicht in den '
                      'Container, sondern ans Schadstoffmobil des ZAOE. Dort gilt '
                      'die haushaltsübliche Menge: höchstens 25 Kilogramm oder 30 '
                      'Liter je Gebinde, kostenfrei; bis 60 Liter nehmen die '
                      'Wertstoffhöfe nur zu den Sammelterminen an. Asbest, '
                      'Feuerwerk und Munition sind ausgeschlossen. Elektroaltgeräte '
                      'kommen gebührenfrei auf die Höfe des Verbands, vollständig '
                      'und ohne eingebaute Batterien.'),
             'quellen': [('ZAOE, Schadstoffhaltige Abfälle',
                          'https://www.zaoe.de/abfall-infos/abfallarten/schadstoffe/'),
                         ('ZAOE, Elektroaltgeräte',
                          'https://www.zaoe.de/abfall-infos/abfallarten/elektroaltgeraete/')]},
            {'text': ('Brauchbares Mobiliar nimmt unter anderem der Möbeldienst des '
                      'Diakonischen Werks Meißen in der Auenstraße 15 in Großenhain '
                      '(Telefon 03522 5233941) auf der ZAOE-Abgabeliste entgegen. '
                      'Für Nachlasssachen ist das Amtsgericht Meißen zuständig, '
                      'dessen Nachlassgericht im Haus Neumarkt 19 sitzt; maßgeblich '
                      'ist der letzte gewöhnliche Aufenthalt der verstorbenen '
                      'Person. Anträge gehen nicht per E-Mail, eine per E-Mail '
                      'eingereichte Erbausschlagung ist unwirksam.'),
             'quellen': [('ZAOE, Sperrmüll mit Abgabeliste',
                          'https://www.zaoe.de/abfall-infos/abfallarten/sperrmuell/'),
                         ('Amtsgericht Meißen, Abteilungen',
                          'https://www.justiz.sachsen.de/agmei/abteilungen-aussenstellen-4049.html'),
                         ('Amtsgericht Meißen, Nachlassabteilung (PDF)',
                          'https://www.justiz.sachsen.de/agmei/download/Nachlassabteilung.pdf')]},
        ],
        'faq_zusatz': ('Das Geräumte lässt sich in Meißen am Wertstoffhof Am Wall 7 '
                       'abgeben oder über die ZAOE-Sperrmüllabholung anmelden, die '
                       'zweimal jährlich bis 3 m³ gebührenfrei ist.'),
    },
    'radebeul': {
        'ortsteile': ['Alt-Radebeul', 'Kötzschenbroda', 'Oberlößnitz',
                      'Niederlößnitz', 'Serkowitz', 'Wahnsdorf', 'Naundorf',
                      'Lindenau', 'Zitzschewig', 'Fürstenhain'],
        'traeger': 'Zweckverband Abfallwirtschaft Oberes Elbtal (ZAOE)',
        'quelle': 'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/',
        'hof': ('Der ZAOE hat seine Geschäftsstelle in Radebeul, Meißner Straße '
                '151 a, betreibt hier aber keinen Wertstoffhof. Höfe im '
                'Landkreis Meißen sind unter anderem Meißen (Am Wall 7) und '
                'Gröbern (Radeburger Straße 65, Niederau).'),
        'sperrmuell': ('Bestellung per Bestellkarte oder Onlineformular des ZAOE; '
                       'zweimal jährlich bis 3 m³ gebührenfrei. Aus Wohnung oder '
                       'Keller holt der Entsorger gegen eine Servicegebühr je '
                       'angefangener Zeiteinheit.'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus, 180 m², voll',
                'beschreibung': 'Erdgeschoss bis Dachboden samt Keller: Der '
                                'Hauspreis schließt alle Geschosse ein.',
                'args': {'objektart': 'haus', 'qm': 180, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Grundstück mit Nebengebäuden, 300 m²',
                'beschreibung': 'Beispielrechnung für ein Grundstück; '
                                'Grundlage ist die Fläche, nicht die Raumzahl.',
                'args': {'objektart': 'garten', 'qm': 300,
                         'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Wohnung in Kötzschenbroda, 80 m², 2. OG',
                'args': {'objektart': 'wohnung', 'qm': 80,
                         'stockwerk': '2og', 'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/',
        'sperrmuell_quelle': 'https://www.zaoe.de/entsorgung/vor-dem-grundstueck/abholung-sperrmuell-und-elektroaltgeraete/',
        'lokal_text': [
            {'text': ('Einen eigenen Wertstoffhof hat Radebeul nicht, dafür sitzt '
                      'der Zweckverband selbst in der Meißner Straße 151 a. Die '
                      'Geschäftsstelle ist montags, mittwochs und freitags von 9 bis '
                      '12 Uhr sowie dienstags und donnerstags von 9 bis 12 und von '
                      '14 bis 18 Uhr zu sprechen, telefonisch unter 0351 40404-0. '
                      'Die zwölf Wertstoffhöfe des Verbands stehen jedem Einwohner '
                      'des Verbandsgebiets offen, auch den Radebeulern.'),
             'quellen': [('ZAOE, Der ZAOE',
                          'https://www.zaoe.de/verband/der-zaoe/'),
                         ('ZAOE, Adressen und Öffnungszeiten',
                          'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/')]},
            {'text': ('Wer Sperrmüll am Hof abgibt, bringt das ausgedruckte, '
                      'unterschriebene Abgabeformular des ZAOE mit: Zweimal im Jahr '
                      'sind bis zu 3 m³ gebührenfrei. Was in einen Sack oder Karton '
                      'passt, gilt nicht als Sperrmüll. Wird vor dem Grundstück '
                      'abgeholt, ist auf Wunsch auch die Abholung aus Wohnung oder '
                      'Keller möglich; dafür berechnet der Entsorger eine '
                      'Servicegebühr je angefangener Zeiteinheit ab Eintreffen des '
                      'Fahrzeugs, die Höhe steht in der Gebührensatzung.'),
             'quellen': [('ZAOE, Abgabe von Sperrmüll am Wertstoffhof',
                          'https://www.zaoe.de/entsorgung/am-wertstoffhof/formular-sperrmuellabgabe/'),
                         ('ZAOE, Abholung von Sperrmüll und Elektroaltgeräten',
                          'https://www.zaoe.de/entsorgung/vor-dem-grundstueck/abholung-sperrmuell-und-elektroaltgeraete/')]},
            {'text': ('Radebeul entstand 1935 durch den Zusammenschluss von Radebeul '
                      'und Kötzschenbroda; die Stadtteile gehen auf zehn frühere '
                      'Gemeinden zurück (Angaben laut Wikipedia): '
                      'Alt-Radebeul, Serkowitz, Oberlößnitz, Wahnsdorf, '
                      'Kötzschenbroda, Fürstenhain, Lindenau, Naundorf, '
                      'Niederlößnitz und Zitzschewig. Für Wiederverwendbares führt '
                      'der ZAOE den Allerhand-Gebrauchtwarenladen der '
                      'Produktionsschule Moritzburg an der Wasastraße 17 '
                      '(Telefon 0351/8382878) in seiner Abgabeliste.'),
             'quellen': [('Wikipedia, Radebeul (Sekundärquelle)',
                          'https://de.wikipedia.org/wiki/Radebeul'),
                         ('ZAOE, Sperrmüll',
                          'https://www.zaoe.de/abfall-infos/abfallarten/sperrmuell/')]},
            {'text': ('Wohin mit Altöl, Fotochemikalien oder '
                      'Quecksilberthermometern? Der ZAOE verweist auf das '
                      'Schadstoffmobil: kostenfrei, haushaltsübliche Mengen bis 25 '
                      'Kilogramm oder 30 Liter je Gebinde. Flüssigkeiten kommen '
                      'getrennt in dichten, gekennzeichneten Behältern, Reste nie '
                      'gemischt. Elektroaltgeräte nehmen die Verbandshöfe '
                      'gebührenfrei, solange sie vollständig sind. Größere Mengen '
                      'bis 60 Liter nehmen die Höfe nur zu den Sammelterminen an.'),
             'quellen': [('ZAOE, Schadstoffhaltige Abfälle',
                          'https://www.zaoe.de/abfall-infos/abfallarten/schadstoffe/'),
                         ('ZAOE, Elektroaltgeräte',
                          'https://www.zaoe.de/abfall-infos/abfallarten/elektroaltgeraete/')]},
            {'text': ('Bei Erbfällen aus Radebeul entscheidet das Amtsgericht '
                      'Meißen; die Nachlassabteilung sitzt im Haus Neumarkt 19 und '
                      'nimmt Testamente in Verwahrung. Anträge lassen sich nicht '
                      'per E-Mail stellen, und eine per E-Mail eingereichte '
                      'Erbausschlagung ist unwirksam. Für Termin- und allgemeine '
                      'Anfragen nimmt das Gericht E-Mails an, mit Namen, letztem '
                      'Wohnort und Sterbedatum der verstorbenen Person.'),
             'quellen': [('Amtsgericht Meißen, Nachlassabteilung (PDF)',
                          'https://www.justiz.sachsen.de/agmei/download/Nachlassabteilung.pdf'),
                         ('Amtsgericht Meißen, Abteilungen',
                          'https://www.justiz.sachsen.de/agmei/abteilungen-aussenstellen-4049.html')]},
        ],
        'faq_zusatz': ('Das Geräumte geht in Radebeul über die ZAOE-Sperrmüllabholung '
                       'oder zu einem Wertstoffhof des Landkreises, etwa nach Meißen, '
                       'Am Wall 7.'),
    },
    'coswig': {
        'ortsteile': ['Kötitz', 'Neucoswig', 'Brockwitz', 'Sörnewitz',
                      'Neusörnewitz'],
        'traeger': 'Zweckverband Abfallwirtschaft Oberes Elbtal (ZAOE)',
        'quelle': 'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/',
        'hof': ('Kein ZAOE-Wertstoffhof in Coswig; nutzbar sind alle Höfe des '
                'Verbands, zum Beispiel Meißen (Am Wall 7: Mo, Mi, Fr 13–18 Uhr, '
                'Sa 8–12 Uhr) und Gröbern (Radeburger Straße 65, Niederau).'),
        'sperrmuell': ('Abholung am Grundstück per Bestellkarte oder '
                       'ZAOE-Onlineformular, zweimal jährlich bis 3 m³ '
                       'gebührenfrei.'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus in Kötitz, 115 m², voll',
                'args': {'objektart': 'haus', 'qm': 115, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Gewerbeeinheit, 180 m², mittel',
                'beschreibung': 'Gewerbe wird nach der Grundfläche berechnet, '
                                'nicht nach der Raumzahl.',
                'args': {'objektart': 'gewerbe', 'qm': 180,
                         'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Wohnung in Neucoswig, 68 m², 1. OG',
                'args': {'objektart': 'wohnung', 'qm': 68,
                         'stockwerk': '1og', 'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/',
        'sperrmuell_quelle': 'https://www.zaoe.de/entsorgung/vor-dem-grundstueck/abholung-sperrmuell-und-elektroaltgeraete/',
        'lokal_text': [
            {'text': ('Amtlich nennt coswig.de fünf Ortsteile: Brockwitz und '
                      'Sörnewitz, beide 1950 eingemeindet, dazu Neusörnewitz sowie '
                      'die früheren Dörfer Neucoswig (seit 1920) und Kötitz (seit '
                      '1935). Kötitz ist durch das Kammermusikzentrum Villa Teresa '
                      'bekannt, Sörnewitz durch den Boselfelsen, Brockwitz durch '
                      'seine Barockkirche. Neusörnewitz hat ausgedehnte '
                      'Gewerbegebiete im Wechsel mit Wohnsiedlungen, Neucoswig ist '
                      'eine Weinbergsgemeinde am Friedewald.'),
             'quellen': [('Stadt Coswig, Ortsteile',
                          'https://www.coswig.de/de/ortsteile.html')]},
            {'text': ('Derzeit hat Coswig keinen eigenen ZAOE-Hof. Da jeder Bewohner '
                      'des Verbandsgebiets jeden der zwölf Höfe nutzen darf, kommen '
                      'etwa Meißen (Am Wall 7; montags, mittwochs und freitags 13 bis '
                      '18 Uhr, samstags 8 bis 12 Uhr) oder Gröbern in Niederau in '
                      'Betracht. Gröbern öffnet im Sommer von 8 bis 17 Uhr, '
                      'dienstags bis 18 Uhr, und nimmt auch Sperrmüll über 3 m³ an.'),
             'quellen': [('ZAOE, Adressen und Öffnungszeiten',
                          'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/'),
                         ('ZAOE, Annahme von Abfällen',
                          'https://www.zaoe.de/entsorgung/am-wertstoffhof/annahme-von-abfaellen/')]},
            {'text': ('Wer selbst fährt, druckt das Abgabeformular des ZAOE aus und '
                      'unterschreibt es; zweimal im Jahr sind bis zu 3 m³ Sperrmüll '
                      'gebührenfrei. Alles, was in einen Sack oder Karton passt, '
                      'gilt nicht als Sperrmüll. Für die Abholung am Grundstück '
                      'genügt die Bestellkarte aus dem Abfallkalender oder das '
                      'Onlineformular; die Abholung folgt innerhalb von vier Wochen '
                      'nach Eingang der Bestellung.'),
             'quellen': [('ZAOE, Abgabe von Sperrmüll am Wertstoffhof',
                          'https://www.zaoe.de/entsorgung/am-wertstoffhof/formular-sperrmuellabgabe/'),
                         ('ZAOE, Abholung von Sperrmüll und Elektroaltgeräten',
                          'https://www.zaoe.de/entsorgung/vor-dem-grundstueck/abholung-sperrmuell-und-elektroaltgeraete/')]},
            {'text': ('Schadstoffe übergibt man dem Annahmepersonal am '
                      'Schadstoffmobil des ZAOE: kostenlos, haushaltsüblich und '
                      'höchstens 25 Kilogramm oder 30 Liter je Gebinde; außerhalb '
                      'der Termine erfolgt keine Annahme. Mitgenommen werden etwa '
                      'Spraydosen mit Restinhalt, Leim, Pflanzenschutzmittel und '
                      'Haushaltsreiniger. Elektroaltgeräte nehmen die Höfe des '
                      'Verbands gebührenfrei, aber nur vollständig; Einzelteile '
                      'sind ausgeschlossen.'),
             'quellen': [('ZAOE, Schadstoffhaltige Abfälle',
                          'https://www.zaoe.de/abfall-infos/abfallarten/schadstoffe/'),
                         ('ZAOE, Elektroaltgeräte',
                          'https://www.zaoe.de/abfall-infos/abfallarten/elektroaltgeraete/')]},
            {'text': ('Wiederverwendbares nimmt der Allerhand-Gebrauchtwarenladen '
                      'der Produktionsschule Moritzburg an, den die Abgabeliste des '
                      'ZAOE in Radebeul (Wasastraße 17) und in Meißen (Niederfährer '
                      'Straße 31) nennt. Nachlasssachen aus Coswig bearbeitet das '
                      'Amtsgericht Meißen; die Nachlassabteilung sitzt im Haus '
                      'Neumarkt 19 und verwahrt auch Testamente; Anträge lassen '
                      'sich nicht per E-Mail stellen, nur Termin- und allgemeine '
                      'Anfragen.'),
             'quellen': [('ZAOE, Sperrmüll mit Abgabeliste',
                          'https://www.zaoe.de/abfall-infos/abfallarten/sperrmuell/'),
                         ('Amtsgericht Meißen, Nachlassabteilung (PDF)',
                          'https://www.justiz.sachsen.de/agmei/download/Nachlassabteilung.pdf'),
                         ('Amtsgericht Meißen, Abteilungen',
                          'https://www.justiz.sachsen.de/agmei/abteilungen-aussenstellen-4049.html')]},
        ],
        'faq_zusatz': ('Das Geräumte aus Coswig kommt über die ZAOE-Sperrmüllabholung '
                       '(bis 3 m³, zweimal jährlich gebührenfrei) oder an einen '
                       'ZAOE-Wertstoffhof im Landkreis, etwa in Meißen.'),
    },
    'riesa': {
        'ortsteile': ['Gröba', 'Weida', 'Merzdorf', 'Pausitz', 'Poppitz',
                      'Mergendorf', 'Göhlis', 'Canitz', 'Nickritz',
                      'Leutewitz', 'Jahnishausen', 'Oelsitz', 'Mautitz'],
        'traeger': 'Zweckverband Abfallwirtschaft Oberes Elbtal (ZAOE)',
        'quelle': 'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/',
        'hof': ('In Riesa gibt es keinen der 12 ZAOE-Höfe; nutzbar ist unter '
                'anderem Groptitz, Altweidaer Straße 2, 01594 Stauchitz (Mo, Mi, '
                'Fr 13–18 Uhr, Sa 8–12 Uhr).'),
        'sperrmuell': ('Abholung am Grundstück zweimal jährlich bis 3 m³ '
                       'gebührenfrei; Bestellung per Karte aus dem Abfallkalender '
                       'oder Onlineformular, Abholung binnen vier Wochen, '
                       'Bereitstellung bis 6:00 Uhr. Terminabsprachen mit REMONDIS '
                       'Elbe-Röder, Telefon 03524 883 647.'),
        'beispiele': [
            {
                'titel': 'Gewerbefläche, 400 m², mittel',
                'args': {'objektart': 'gewerbe', 'qm': 400,
                         'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Wohnung in Weida, 58 m², 4. OG mit Aufzug',
                'args': {'objektart': 'wohnung', 'qm': 58,
                         'stockwerk': '4og', 'aufzug': True,
                         'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Einfamilienhaus in Gröba, 100 m², voll',
                'beschreibung': 'Keller, Schuppen und Garage sind im '
                                'Hauspreis enthalten.',
                'args': {'objektart': 'haus', 'qm': 100, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/',
        'sperrmuell_quelle': 'https://www.zaoe.de/entsorgung/vor-dem-grundstueck/abholung-sperrmuell-und-elektroaltgeraete/',
        'lokal_text': [
            {'text': ('Für die Region Riesa-Großenhain nennt der ZAOE als '
                      'Ansprechpartner für Abholort und Termin die REMONDIS '
                      'Elbe-Röder GmbH (Telefon 03524 883 647). Gebührenfrei sind '
                      'zwei Abholungen im Jahr mit höchstens 3 m³ je Haushalt; '
                      'bestellt wird per Karte oder Onlineformular, ausgeführt wird '
                      'binnen vier Wochen. Aus Wohnung oder Keller holt der '
                      'Vollservice gegen eine Zeitgebühr je angefangener Zeiteinheit.'),
             'quellen': [('ZAOE, Abholung von Sperrmüll und Elektroaltgeräten',
                          'https://www.zaoe.de/entsorgung/vor-dem-grundstueck/abholung-sperrmuell-und-elektroaltgeraete/')]},
            {'text': ('Zwölf Höfe betreibt der ZAOE, keiner steht in Riesa. Zur Wahl '
                      'steht etwa Groptitz in Stauchitz, Altweidaer Straße 2: '
                      'montags, mittwochs und freitags von 13 bis 18 Uhr, samstags '
                      'von 8 bis 12 Uhr, Zahlung mit EC-Karte möglich. Sperrmüll '
                      'nimmt ein Hof bis 3 m³ an; größere Mengen gehen nur in '
                      'Gröbern, Kleincotta und Saugrund an.'),
             'quellen': [('ZAOE, Adressen und Öffnungszeiten',
                          'https://www.zaoe.de/entsorgung/am-wertstoffhof/alle-wertstoffhoefe/'),
                         ('ZAOE, Annahme von Abfällen',
                          'https://www.zaoe.de/entsorgung/am-wertstoffhof/annahme-von-abfaellen/')]},
            {'text': ('Brauchbare Möbel nehmen in Riesa die Möbelbörse '
                      '(Spinnereistr. 3) und die Secondhand Halle (Merzdorfer Str. 5) '
                      'entgegen; beide stehen auf der Abgabeliste des ZAOE, ohne '
                      'Anspruch auf Vollständigkeit. Die Stadt führt Canitz, '
                      'Jahnishausen, Leutewitz, Mautitz, Nickritz und Oelsitz als '
                      'Ortschaften mit eigenem Ortschaftsrat; Gröba und Weida wurden '
                      '1923 eingemeindet.'),
             'quellen': [('ZAOE, Sperrmüll',
                          'https://www.zaoe.de/abfall-infos/abfallarten/sperrmuell/'),
                         ('Stadt Riesa, Ortschaftsrat',
                          'https://www.riesa.de/rathaus/politik/ortschaftsrat'),
                         ('Stadt Riesa, Stadtportrait',
                          'https://www.riesa.de/stadtportrait')]},
            {'text': ('In Riesa gilt die ZAOE-Regel für Gefahrstoffe: Sie werden am '
                      'Schadstoffmobil kostenlos angenommen, nur haushaltsüblich '
                      'und höchstens 25 Kilogramm oder 30 Liter je Gebinde. Reste '
                      'wasserlöslicher Farben gelten laut Verband nicht als '
                      'Schadstoff: offen aushärten lassen, dann in den Restabfall; '
                      'der leere Eimer kommt in die Gelbe Tonne. Elektroaltgeräte '
                      'nehmen die ZAOE-Höfe gebührenfrei an, vollständig und ohne '
                      'Batterien.'),
             'quellen': [('ZAOE, Schadstoffhaltige Abfälle',
                          'https://www.zaoe.de/abfall-infos/abfallarten/schadstoffe/'),
                         ('ZAOE, Elektroaltgeräte',
                          'https://www.zaoe.de/abfall-infos/abfallarten/elektroaltgeraete/')]},
            {'text': ('Nachlasssachen aus Riesa führt das Amtsgericht Riesa in der '
                      'Lauchhammerstraße 10; die Nachlassabteilung hat mittwochs '
                      'und freitags geschlossen und bittet in Nachlasssachen stets '
                      'um einen Termin. Auf der ZAOE-Abgabeliste stehen die '
                      'Möbelbörse (Spinnereistraße 3) und die Secondhand Halle '
                      '(Merzdorfer Straße 5).'),
             'quellen': [('Amtsgericht Riesa, Kontakt',
                          'https://www.justiz.sachsen.de/agrie/kontakt-anreise-datenschutz-3916.html'),
                         ('ZAOE, Sperrmüll mit Abgabeliste',
                          'https://www.zaoe.de/abfall-infos/abfallarten/sperrmuell/')]},
        ],
        'faq_zusatz': ('Das Geräumte wird in Riesa über die ZAOE-Sperrmüllabholung '
                       '(zweimal jährlich bis 3 m³ gebührenfrei) oder am Hof Groptitz '
                       'in Stauchitz entsorgt; brauchbare Möbel nehmen die '
                       'Möbelbörse und die Secondhand Halle an.'),
    },

    # ══ Sachsen, Südwesten und Oberlausitz ═══════════════════════════════
    'chemnitz': {
        'ortsteile': ['Kaßberg', 'Sonnenberg', 'Schloßchemnitz',
                      'Altchemnitz', 'Bernsdorf', 'Gablenz', 'Hilbersdorf',
                      'Lutherviertel', 'Yorckgebiet', 'Adelsberg',
                      'Rabenstein', 'Reichenbrand', 'Siegmar', 'Rottluff',
                      'Grüna'],
        'traeger': 'Abfallentsorgungs- und Stadtreinigungsbetrieb (ASR) Chemnitz',
        'quelle': 'https://www.asr-chemnitz.de/leistungen/abfallentsorgung/wertstoffhoefe',
        'hof': ('Fünf Wertstoffhöfe: Blankenburgstraße 62, Weißer Weg, '
                'Jägerschlößchenstraße 15a, Straße Usti nad Labem 30 und '
                'Kalkstraße 47. Für die vier zuletzt genannten gilt: Mo, Di, '
                'Do, Fr 8:00–18:00, Mi 10:00–19:00, Sa 7:00–15:00 Uhr. Die Höfe'
                ' stehen nur Chemnitzer Abfallgebührenzahlern offen; bei '
                'fremdem Kennzeichen sind Ausweis, Mietvertrag oder '
                'Abfallbescheid vorzulegen.'),
        'sperrmuell': ('Einmal im Jahr holt der ASR haushaltstypischen Sperrabfall '
                       'gebührenfrei ab, bis zu 20 m³ je Haushalt und Jahr. Bestellt '
                       'wird schriftlich per Sperrabfallkarte oder online auf der '
                       'ASR-Website, Rückfragen beantwortet der Kundenservice unter '
                       '0371 4095-777; der Termin liegt in der Regel '
                       'innerhalb von vier Wochen, Abholung Mo–Fr, Bereitstellung bis '
                       '6 Uhr. Waschmaschine, Kühlschrank oder Fernseher nimmt die '
                       'Sperrabfallabholung in Chemnitz mit.'),
        # 02.10.2026: der fruehere Satz ("verlor 1945 fast die gesamte
        # Innenstadt ... hohe Decken") war unbelegt. Jetzt Zensus 2022.
        'bebauung': ('41,0 % der Chemnitzer Wohnungen liegen in Häusern, die bis '
                     '1949 gebaut wurden, ein Viertel (24,7 %) in Bauten von 1970 '
                     'bis 1989. Elf von hundert Wohnungen standen am Zensusstichtag '
                     'leer (11,0 %), so viele wie in keiner der beiden anderen '
                     'sächsischen Großstädte (Zensus 2022). Die Rechenbeispiele '
                     'oben folgen diesem Bestand: Altbau ohne Aufzug, Wohnblock mit '
                     'Aufzug, Haus am Stadtrand.'),
        'bebauung_quellen': [
            ('Statistisches Landesamt Sachsen, Zensus 2022, Datenblatt Chemnitz',
             'https://zensus.sachsen.de/05_03_Datenblatt_Gemeinden/statistik-sachsen_zensus_gwz_gemeinde_chemnitz-stadt.pdf'),
            ('Statistisches Landesamt Sachsen, Zensus 2022, Datenblatt Dresden',
             'https://zensus.sachsen.de/05_03_Datenblatt_Gemeinden/statistik-sachsen_zensus_gwz_gemeinde_dresden-stadt.pdf'),
            ('Statistisches Landesamt Sachsen, Zensus 2022, Datenblatt Leipzig',
             'https://zensus.sachsen.de/05_03_Datenblatt_Gemeinden/statistik-sachsen_zensus_gwz_gemeinde_leipzig-stadt.pdf'),
        ],
        'beispiele': [
            {
                'titel': 'Gründerzeitwohnung auf dem Kaßberg, 95 m², 3. OG '
                         'ohne Aufzug, voll',
                'beschreibung': 'Der aufwendigste Wohnungstyp der Stadt: viel '
                                'Volumen auf einer Etage, und jedes Teil muss '
                                'die Stufen hinunter. Fläche und Stockwerk '
                                'wirken zusammen.',
                'args': {'objektart': 'wohnung', 'qm': 95,
                         'stockwerk': '3og', 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung im Yorckgebiet, 60 m², 4. OG mit Aufzug',
                'beschreibung': 'Höher gelegen als die Kaßberg-Wohnung und '
                                'trotzdem deutlich günstiger: Mit Aufzug '
                                'entfällt der Stockwerkzuschlag vollständig.',
                'args': {'objektart': 'wohnung', 'qm': 60,
                         'stockwerk': '4og', 'aufzug': True,
                         'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Einfamilienhaus in Rabenstein, 130 m², mittel',
                'beschreibung': 'Am Stadtrand mit Zufahrt bis zur Tür. Keller '
                                'und Dachboden gehören beim Hauspreis dazu, '
                                'sie werden nicht extra gerechnet.',
                'args': {'objektart': 'haus', 'qm': 130,
                         'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.asr-chemnitz.de/leistungen/abfallentsorgung/wertstoffhoefe',
        'sperrmuell_quelle': 'https://www.asr-chemnitz.de/leistungen/abfallentsorgung/sperrabfall',
        'lokal_text': [
            {'text': ('Chemnitz gliedert sich in 39 Stadtteile; acht davon sind '
                      'zugleich Ortschaften mit eigenem Ortschaftsrat: Einsiedel, '
                      'Euba, Grüna, Klaffenbach, Kleinolbersdorf-Altenhain, '
                      'Mittelbach, Röhrsdorf und Wittgensdorf.'),
             'quellen': [('Stadt Chemnitz, Statistische Information Stadtteile 2021',
                          'https://d2vw8mc5mcb3gm.cloudfront.net/fileadmin/chemnitz/media/aktuell/publikationen/downloads/stadtteile_2021.pdf'),
                         ('Stadt Chemnitz, Ortschaften',
                          'https://www.chemnitz.de/de/unsere-stadt/ortschaften')]},
            {'text': ('Die Sperrabfallkarte gibt es auf den Wertstoffhöfen, im '
                      'ASR-Kundenservice und in den Bürgerservicestellen; bestellt '
                      'werden kann auch online. Bereitgestellt wird zwischen 18 Uhr '
                      'am Vortag und 6 Uhr am Abholtag. Nicht zum Sperrabfall zählen '
                      'Bauschutt, Kfz-Teile, Textilien, Bioabfälle, Farben und Lacke '
                      'sowie Produktionsabfall. Für Gewerbe liegt die Grenze bei 10 '
                      'm³ je Jahr.'),
             'quellen': [('ASR Chemnitz, Sperrabfall',
                          'https://www.asr-chemnitz.de/leistungen/abfallentsorgung/sperrabfall')]},
            {'text': ('Gegen Gebühr bietet der ASR zusätzlich die Abholung aus der '
                      'Wohnung (nach Zeitaufwand je Sechs-Minuten-Einheit), die '
                      'Komplettberäumung und Terminabholungen mit mindestens zehn '
                      'Tagen Vorlauf an. Die Wertstoffhöfe stehen ausschließlich '
                      'Chemnitzer Abfallgebührenzahlern offen und nehmen Sperrabfall '
                      'bis 2 m³ je Anlieferung und Tag an. Bringt ein beauftragtes '
                      'Transportunternehmen die Abfälle, muss der Transport beim ASR '
                      'angemeldet sein oder ein Haushaltsmitglied mitfahren.'),
             'quellen': [('ASR Chemnitz, Sperrabfall',
                          'https://www.asr-chemnitz.de/leistungen/abfallentsorgung/sperrabfall'),
                         ('Wertstoffhöfe',
                          'https://www.asr-chemnitz.de/leistungen/abfallentsorgung/wertstoffhoefe')]},
            {'text': ('Der ASR nimmt Problemabfälle gebührenfrei am Schadstoffmobil '
                      'an, das samstags reihum die Höfe anfährt: erster Samstag '
                      'Straße Usti nad Labem 30, zweiter Blankenburgstraße 62, '
                      'dritter Jägerschlößchenstraße 15 a, vierter Kalkstraße 47, '
                      'fünfter Weißer Weg. Erlaubt sind bis zu 5 Kilogramm, bei '
                      'Altfarben bis zu 25 Kilogramm je Anlieferung. Große '
                      'Elektroaltgeräte nehmen alle fünf Höfe kostenfrei an.'),
             'quellen': [('ASR Chemnitz, Problemabfall',
                          'https://www.asr-chemnitz.de/leistungen/abfallentsorgung/private-haushalte/problemabfall'),
                         ('ASR Chemnitz, Elektro(nik)geräte',
                          'https://www.asr-chemnitz.de/leistungen/abfallentsorgung/elektronikgeraete')]},
            {'text': ('Das Sozialkaufhaus MöbelWert des Netzwerks Mittweida, '
                      'Altchemnitzer Straße 15-17, arbeitet Spenden in eigenen '
                      'Werkstätten auf und verkauft sie an jedermann. Mobiliar, '
                      'Elektrogeräte, Hausrat, Teppiche, Sportgeräte und Bücher '
                      'holt es kostenfrei ab, nachdem es sie auf Fotos oder vor Ort '
                      'angesehen hat. Geöffnet ist montags bis freitags von 9 bis '
                      '18 Uhr.'),
             'quellen': [('Netzwerk Mittweida, MöbelWert',
                          'https://www.netzwerk-mittweida.de/angebote-fuer-firmen-privatkunden/sozialkaufhaeuser-moebelwert.html')]},
        ],
        'faq_zusatz': ('In Chemnitz nehmen fünf Wertstoffhöfe des ASR '
                       'Selbstanlieferungen an, allerdings nur von Chemnitzer '
                       'Abfallgebührenzahlern.'),
    },
    'zwickau': {
        'ortsteile': ['Innenstadt', 'Pölbitz', 'Marienthal',
                      'Eckersbach', 'Neuplanitz', 'Oberplanitz',
                      'Niederplanitz', 'Bockwa', 'Oberhohndorf',
                      'Weißenborn', 'Crossen', 'Mosel', 'Cainsdorf'],
        'traeger': ('Amt für Abfallwirtschaft des Landkreises Zwickau'),
        'quelle': ('https://www.landkreis-zwickau.de/annahmestellen'),
        'hof': ('Im Stadtgebiet nimmt Veolia an der Flurstraße (abseits) '
                'Elektrogeräte, Batterien, Textilien und Schrott an (Mo–Fr '
                '7:00–18:00, Sa 9:00–13:00 Uhr). Die KECL GmbH in Glauchau, '
                'Ringstraße 36, ist ebenfalls Annahmestelle des Landkreises. '
                'Die Entsorgungsanlage Lipprandis (Schönberger Straße 44, '
                'Glauchau) betreibt der Zweckverband Abfallwirtschaft '
                'Südwestsachsen.'),
        'sperrmuell': ('Im Landkreis Zwickau gibt es einmal im Jahr eine Abholung je '
                       'Haushalt, enthalten in der Grundgebühr. Der Antrag läuft '
                       'online über „Entsorgung auf Abruf“ oder per Entsorgungskarte, '
                       'die Wartezeit beträgt höchstens einen Monat. Bereitgestellt '
                       'wird an der Grundstücksgrenze bis 7:00 Uhr am Abholtag, '
                       'frühestens am Vortag.'),
        'bebauung': 'Zwickau ist Automobilstandort seit Audi und Trabant; '
                    'neben Werkssiedlungen prägen Gründerzeit im Bahnhofsviertel '
                    'und Plattenbau in Eckersbach das Bild. Der Bergbau hat '
                    'Senkungsgebiete hinterlassen, in denen Keller feucht sind '
                    '– dort ist Durchnässtes oft Sondermüll statt Sperrmüll.',
        'beispiele': [
            {
                'titel': 'Feuchter Keller im Senkungsgebiet, 18 m², voll, mit '
                         'belasteten Teilen',
                'beschreibung': 'Durchnässtes Holz und verschimmelte '
                                'Polstermöbel gehören nicht in den normalen '
                                'Container – daher der Aufschlag für die '
                                'getrennte Entsorgung.',
                'args': {'objektart': 'keller', 'qm': 18,
                         'fuellgrad': 'voll', 'sonderabfall': 'wenige'},
            },
            {
                'titel': 'Gründerzeitwohnung im Bahnhofsviertel, 88 m², 3. '
                         'OG, voll',
                'beschreibung': 'Große Altbauwohnung ohne Aufzug: Fläche und '
                                'Stockwerk treiben den Preis gemeinsam.',
                'args': {'objektart': 'wohnung', 'qm': 88,
                         'stockwerk': '3og', 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Werkssiedlungshaus in Marienthal, 110 m², voll',
                'beschreibung': 'Zwickau ist Automobilstandort seit Audi und '
                                'Trabant; die Werkssiedlungen haben Keller, '
                                'Schuppen und Garten.',
                'args': {'objektart': 'haus', 'qm': 110, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'sperrmuell_quelle': 'https://www.landkreis-zwickau.de/detail?type=VB&id=551',
        'lokal_text': [
            {'text': ('Träger der Abfallentsorgung ist im Landkreis das Amt für '
                      'Abfallwirtschaft in der Stauffenbergstraße 2, Telefon 0375 '
                      '4402-26600. Die erste Sperrmüllabholung eines Jahres kostet je'
                      ' Haushalt nichts zusätzlich, sie ist in der Sockelgebühr '
                      'enthalten. Ausgeschlossen sind Bauschutt, Elektroschrott, '
                      'Metallschrott und Schadstoffe.'),
             'quellen': [('Landkreis Zwickau, Amt für Abfallwirtschaft',
                          'https://www.landkreis-zwickau.de/detail?type=BHW&id=33'),
                         ('Sperrmüll',
                          'https://www.landkreis-zwickau.de/detail?type=VB&id=551')]},
            {'text': ('Elektrogeräte, Batterien, saubere Alttextilien und Schrott '
                      'lassen sich kostenfrei bei Annahmestellen des Landkreises '
                      'abgeben. In Zwickau ist das der Betrieb von Veolia an der '
                      'Flurstraße, Telefon 0375 27732-0. Die KECL in Glauchau, '
                      'Ringstraße 36, nimmt montags von 13 bis 16 Uhr sowie dienstags'
                      ' und donnerstags von 9 bis 12 und von 13 bis 18 Uhr an.'),
             'quellen': [('Landkreis Zwickau, Annahmestellen',
                          'https://www.landkreis-zwickau.de/annahmestellen'),
                         ('Annahmestellen (PDF)',
                          'https://www.landkreis-zwickau.de/download/abfall/Annahmestellen.pdf')]},
            {'text': ('Zwickau zählt fünf Stadtbezirke mit 35 Stadtteilen. Als '
                      'Ortschaften mit eigenem Ortschaftsrat gelten Rottmannsdorf, '
                      'Cainsdorf, Mosel, Oberrothenbach, Schlunzig und Crossen mit '
                      'Schneppendorf.'),
             'quellen': [('Wikipedia, Zwickau (Sekundärquelle)',
                          'https://de.wikipedia.org/wiki/Zwickau')]},
            {'text': ('Schadstoffe aus Zwickauer Haushalten nimmt das '
                      'Schadstoffmobil des Amts für Abfallwirtschaft an: am zweiten '
                      'Samstag jedes Monats von 9 bis 12 Uhr in der Reichenbacher '
                      'Straße 142, auf dem Gelände der Firma WZL. Zusätzlich fährt '
                      'es jedes Frühjahr und jeden Herbst durch die Gemeinden des '
                      'Landkreises. Die Stellplätze und Zeiten lassen sich auf der '
                      'Seite des Landkreises per Umkreissuche finden.'),
             'quellen': [('Landkreis Zwickau, Standorte des Schadstoffmobils',
                          'https://www.landkreis-zwickau.de/standorte-schadstoffmobil')]},
            {'text': ('Nachlassgericht ist das Amtsgericht Zwickau in der '
                      'Humboldtstraße 1, wenn der Erblasser zuletzt im '
                      'Gerichtsbezirk lebte. Wer eine Erbschaft ausschlagen will, '
                      'kann das beim Gericht des letzten Aufenthalts des '
                      'Verstorbenen oder an seinem eigenen Wohnsitz erklären; die '
                      'Frist beträgt sechs Wochen ab Kenntnis, bei Aufenthalt im '
                      'Ausland sechs Monate.'),
             'quellen': [('Amtsgericht Zwickau, Nachlassabteilung',
                          'https://www.justiz.sachsen.de/agz/nachlassabteilung-4448.html')]},
        ],
        'faq_zusatz': ('In Zwickau nimmt Veolia an der Flurstraße Elektrogeräte, '
                       'Batterien, Textilien und Schrott an; Sperrmüll holt der '
                       'Landkreis einmal im Jahr je Haushalt ab.'),
    },
    'glauchau': {
        'ortsteile': ['Gesau', 'Jerisau', 'Niederlungwitz', 'Reinholdshain',
                      'Wernsdorf', 'Höckendorf', 'Albertsthal', 'Rothenbach',
                      'Lipprandis', 'Schönbörnchen'],
        'traeger': 'KECL Kommunalentsorgung Chemnitzer Land GmbH',
        'quelle': 'https://www.kecl.de/',
        'hof': ('Annahmestelle für Elektroaltgeräte der KECL, Ringstraße 36 im '
                'Ortsteil Reinholdshain: Mo 13–16 Uhr, Di und Do 9–12 und 13–18 '
                'Uhr. Dort sitzt auch die Gesellschaft selbst (Ringstraße 36 B).'),
        'sperrmuell': ('Einmal jährlich je Haushalt im Rahmen der Sockelgebühr; der '
                       'Termin folgt auf eine schriftliche Bestellung bei der KECL, '
                       'bereitzustellen ist am Grundstück am Abholtag bis 7 Uhr.'),
        'beispiele': [
            {
                'titel': 'Gewerbefläche, 300 m², mittel',
                'args': {'objektart': 'gewerbe', 'qm': 300, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Wohnung, 85 m², 3. OG, voll',
                'args': {'objektart': 'wohnung', 'qm': 85, 'stockwerk': '3og', 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus in Niederlungwitz, 120 m², mittel',
                'args': {'objektart': 'haus', 'qm': 120, 'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.kecl.de/annahmestelle-elektroaltgeraete',
        'sperrmuell_quelle': 'https://www.kecl.de/abfallarten',
        'lokal_text': [
            {'text': ('Elektroaltgeräte aus Glauchau nimmt die KECL an der '
                      'Ringstraße 36 im Ortsteil Reinholdshain an, montags von 13 '
                      'bis 16 Uhr sowie dienstags und donnerstags von 9 bis 12 und '
                      'von 13 bis 18 Uhr. Dort sitzt auch die Gesellschaft selbst '
                      '(Ringstraße 36 B). Gartenabfälle und Elektrogeräte zählen '
                      'dagegen nicht zum Sperrmüll der Abholung.'),
             'quellen': [('KECL, Annahmestelle Elektroaltgeräte',
                          'https://www.kecl.de/annahmestelle-elektroaltgeraete'),
                         ('KECL, Impressum',
                          'https://www.kecl.de/impressum'),
                         ('KECL, Abfallarten',
                          'https://www.kecl.de/abfallarten')]},
            {'text': ('Sperrige Abfälle holt die KECL einmal pro Haushalt und Jahr '
                      'im Rahmen der Sockelgebühr ab; der Termin folgt auf eine '
                      'schriftliche Bestellung, bereitzustellen ist am Abholtag bis '
                      '7 Uhr am Grundstück. Sperrige Kunststoffe werden separat '
                      'gesammelt.'),
             'quellen': [('KECL, Abfallarten',
                          'https://www.kecl.de/abfallarten')]},
            {'text': ('Das Schadstoffmobil fährt zweimal im Jahr Sammelpunkte an. '
                      'Wer früher entsorgen muss, kann jeden zweiten Samstag im '
                      'Monat von 9 bis 12 Uhr zum Standplatz bei der WZL GmbH, '
                      'Reichenbacher Straße 142 in Zwickau.'),
             'quellen': [('KECL, Abfallarten',
                          'https://www.kecl.de/abfallarten'),
                         ('KECL, Schadstoffsammlung',
                          'https://www.kecl.de/schadstoffsammlung')]},
            {'text': ('Noch gebrauchsfähige Möbel und Hausrat nimmt die gGAB '
                      'Glauchau in der Schlachthofstraße 33 als Spende: Mobiliar, '
                      'Elektrogeräte, Hausrat, Lampen und Teppiche in der '
                      'Sozialbörse, dazu gibt es eine Kleider- und '
                      'Kinderartikelbörse. Dort ist auch die Glauchauer Tafel '
                      'angesiedelt.'),
             'quellen': [('gGAB, Standort Glauchau',
                          'https://www.gab-sozial.de/glauchau/')]},
            {'text': ('Nachlässe aus Glauchau bearbeitet laut Justizportal das '
                      'Amtsgericht Hohenstein-Ernstthal, Conrad-Clauß-Straße 11; '
                      'Anträge werden nur nach Terminvereinbarung aufgenommen. Die '
                      'Stadt gliedert sich in den Stadtgebietskern und sechs '
                      'Ortschaften, darunter Niederlungwitz, Wernsdorf und '
                      'Reinholdshain; 21.745 Menschen leben hier (Melderegister, '
                      'Dezember 2025).'),
             'quellen': [('Justizportal, Orts- und Gerichtsverzeichnis (Nachlasssachen, PLZ 08371)',
                          'https://www.justizadressen.nrw.de/de/justiz/gericht?ang=nachlass&plzort=08371+Glauchau'),
                         ('Justiz Sachsen, Amtsgericht Hohenstein-Ernstthal, Nachlassabteilung',
                          'https://www.justiz.sachsen.de/aghot/nachlassabteilung-4499.html'),
                         ('Stadt Glauchau, Zahlen und Fakten',
                          'https://www.glauchau.de/de/zahlen-fakten.html'),
                         ('Stadt Glauchau, Ortschaften',
                          'https://www.glauchau.de/de/ortschaften.html')]},
        ],
        'faq_zusatz': ('Geräumtes aus Glauchau geht an die KECL-Annahmestelle Ringstraße '
                       '36, per schriftlich bestellter Sperrmüllabholung oder, wenn es '
                       'taugt, an die gGAB-Sozialbörse in der Schlachthofstraße.'),
    },
    'freiberg': {
        'ortsteile': ['Zug', 'Kleinwaltersdorf', 'Halsbach'],
        'traeger': 'EKM Entsorgungsdienste Kreis Mittelsachsen',
        'quelle': 'https://www.ekm-mittelsachsen.de/abfallentsorgung/sperrige-abfaelle',
        'hof': ('Wertstoffhof Freiberg (EKM), Frauensteiner Straße 95: Mo–Fr 8–18 '
                'Uhr, Sa 8–12 Uhr. Sperrige Abfälle bis 3 m³ je Anlieferung nimmt '
                'er kostenfrei an; Asbest, Dachpappe, Mineralwolle und '
                'Photovoltaikmodule bleiben ausgeschlossen.'),
        'sperrmuell': ('Gebührenfrei sind 6 m³ je Haushalt und Jahr, aufgeteilt in '
                       'zweimal 3 m³. Abgeholt wird vom 1. März bis 30. November; '
                       'Anmeldung per Doppelkarte aus dem Abfallkalender oder online, den '
                       'Termin bekommen Sie binnen vier Wochen, spätestens eine Woche '
                       'vorher. Abfälle aus Haushaltsauflösungen sind von dieser Abholung '
                       'ausgeschlossen.'),
        'beispiele': [
            {
                'titel': 'Keller, 25 m², voll',
                'args': {'objektart': 'keller', 'qm': 25, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 80 m², 3. OG, voll',
                'args': {'objektart': 'wohnung', 'qm': 80, 'stockwerk': '3og', 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus in Kleinwaltersdorf, 130 m², mittel',
                'args': {'objektart': 'haus', 'qm': 130, 'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.ekm-mittelsachsen.de/abfallentsorgung/wertstoffhoefe',
        'sperrmuell_quelle': 'https://www.ekm-mittelsachsen.de/abfallentsorgung/sperrige-abfaelle',
        'lokal_text': [
            {'text': ('Der EKM-Wertstoffhof Freiberg, Frauensteiner Straße 95, ist '
                      'montags bis freitags von 8 bis 18 Uhr und samstags von 8 bis '
                      '12 Uhr geöffnet. Sperrige Abfälle bis 3 m³ je Anlieferung '
                      'nimmt er kostenfrei an, und die Zahl der Anlieferungen ist '
                      'nicht begrenzt; ebenso frei sind Elektro- und '
                      'Elektronikaltgeräte sowie Kühlgeräte. Asbest, Dachpappe, '
                      'Mineralwolle und Photovoltaikmodule bleiben ausgeschlossen '
                      '(EKM, Stand 10/2026).'),
             'quellen': [('EKM Mittelsachsen, Wertstoffhöfe',
                          'https://www.ekm-mittelsachsen.de/abfallentsorgung/wertstoffhoefe')]},
            {'text': ('Die Abholung läuft vom 1. März bis 30. November; '
                      'Anmeldeschluss ist der 31. Oktober, per Doppelkarte aus dem '
                      'Abfallkalender oder online. Den Termin erhält man binnen '
                      'vier Wochen, spätestens eine Woche vorher. Bereitgestellt '
                      'wird ab 18 Uhr am Vortag bis 5 Uhr am Abholtag; kostenfrei '
                      'sind 6 m³ je Haushalt und Jahr, jede weitere Menge kostet '
                      '47,45 € je m³ (EKM, Stand 10/2026). Einzelteile dürfen 70 kg '
                      'und 2 m nicht überschreiten.'),
             'quellen': [('EKM Mittelsachsen, Sperrige Abfälle',
                          'https://www.ekm-mittelsachsen.de/abfallentsorgung/sperrige-abfaelle')]},
            {'text': ('Abfälle aus Renovierungen und Haushaltsauflösungen zählen '
                      'nach den EKM-Regeln nicht zu den sperrigen Abfällen der '
                      'Abholung. Schadstoffe nimmt das FNE-Zwischenlager am '
                      'Schachtweg 6 in Freiberg ganzjährig an, bis 60 Liter oder '
                      'Kilogramm je Haushalt kostenfrei, werktags nachmittags sowie '
                      'am 1. und 3. Samstag im Monat von 9 bis 12 Uhr. Das '
                      'Schadstoffmobil kommt zweimal jährlich.'),
             'quellen': [('EKM Mittelsachsen, Sperrige Abfälle',
                          'https://www.ekm-mittelsachsen.de/abfallentsorgung/sperrige-abfaelle'),
                         ('EKM Mittelsachsen, Schadstoffe',
                          'https://www.ekm-mittelsachsen.de/abfallentsorgung/schadstoffe')]},
            {'text': ('Für Brauchbares verweist die EKM auf die MöbelWert-Filiale '
                      'in der Dammstraße 46 Ecke Silberhofstraße. Sie nimmt '
                      'Mobiliar, Elektrogeräte und Hausrat als Spende an; abgeholt '
                      'wird nach Ansicht auf Bildern oder vor Ort kostenfrei. Das '
                      'Gebrauchtwarenhaus gehört zum Netzwerk Mittweida.'),
             'quellen': [('EKM Mittelsachsen, Sperrige Abfälle',
                          'https://www.ekm-mittelsachsen.de/abfallentsorgung/sperrige-abfaelle'),
                         ('Netzwerk Mittweida, Sozialkaufhäuser MöbelWert',
                          'https://www.netzwerk-mittweida.de/angebote-fuer-firmen-privatkunden/sozialkaufhaeuser-moebelwert.html')]},
            {'text': ('Nachlassgericht ist laut Justizportal das Amtsgericht '
                      'Freiberg; die Abteilung für Betreuung, Grundbuch und '
                      'Nachlass sitzt in der Chemnitzer Straße 40, Seiteneingang '
                      'Brückenstraße (Di 9–12 und 13–15:30 Uhr, Do und Fr 9–12 '
                      'Uhr). Ortschaftsräte besitzen die Stadtteile Zug, '
                      'Kleinwaltersdorf und Halsbach. Die Stadt zählte 41.213 '
                      'Einwohner (31.12.2023, Landesamt).'),
             'quellen': [('Justizportal, Orts- und Gerichtsverzeichnis (Nachlasssachen, PLZ 09599)',
                          'https://www.justizadressen.nrw.de/de/justiz/gericht?ang=nachlass&plzort=09599+Freiberg'),
                         ('Justiz Sachsen, Amtsgericht Freiberg, Außenstelle',
                          'https://www.justiz.sachsen.de/agfg/amtsgericht-aussenstelle-4099.html'),
                         ('Stadt Freiberg, Stadtteile',
                          'https://www.freiberg.de/stadt-und-buerger/stadt/portrait/stadtteile'),
                         ('Stadt Freiberg, Amtliche Einwohnerzahlen 31.12.2023 (PDF)',
                          'https://www.freiberg.de/fileadmin/documents/Statistik/Zensus_2025/Homepage_2023_1982_Amtliche_EW_31_12.pdf')]},
        ],
        'faq_zusatz': ('Geräumtes aus Freiberg geht an den EKM-Wertstoffhof in der '
                       'Frauensteiner Straße, Brauchbares in die MöbelWert-Filiale in der '
                       'Dammstraße; Haushaltsauflösungen sind von der Sperrmüllabholung '
                       'ausgeschlossen.'),
    },
    'plauen': {
        'ortsteile': ['Altstadt', 'Bahnhofsvorstadt', 'Neustadt',
                      'Haselbrunn', 'Chrieschwitz', 'Reusa', 'Südvorstadt',
                      'Ostvorstadt', 'Oberlosa', 'Unterlosa', 'Straßberg',
                      'Neundorf', 'Jößnitz', 'Kauschwitz'],
        'traeger': ('Vogtlandkreis (Sperrmüll) und Kreisentsorgung Vogtland '
                    '(Wertstoffhof)'),
        'quelle': 'https://www.kreisentsorgung.de/Wertstoffh%C3%B6fe/Wertstoffhof-Plauen/',
        'hof': ('Wertstoffhof Plauen, Klopstockstraße 15 (Kreisentsorgung '
                'Vogtland), Telefon 037421 123 335. Von April bis Oktober Mo–Mi'
                ' und Fr 7:30–17:00 Uhr, Do 7:30–18:00 Uhr, Sa 8:00–12:00 Uhr; '
                'einen gültigen Personalausweis mitbringen.'),
        'sperrmuell': ('Eine Abholung bis 9 m³ kostet 10,00 € je Antrag und kann '
                       'grundsätzlich bis zu sechs Wochen dauern. Für die '
                       'Expressabholung (ebenfalls bis 9 m³) kommen 56,88 € zur '
                       'normalen Gebühr hinzu. Den Antrag können Eigentümer oder '
                       'Besitzer der Abfälle stellen. Gebührensätze laut Landkreis '
                       'gültig ab 2022.'),
        'bebauung': ('Plauen war Zentrum der Spitzenherstellung und ist bis heute '
                     'von Fabrikantenvillen und Gründerzeitquartieren geprägt, dazu '
                     'Hanglage über der Weißen Elster.'),
        'beispiele': [
            {
                'titel': 'Gründerzeithaus vor dem Verkauf, 160 m², voll',
                'beschreibung': 'Ein ganzes Haus zu räumen heißt: Dachboden, Keller und '
                'alle Etagen in einem Auftrag.',
                'args': {'objektart': 'haus', 'qm': 160, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung in der Bahnhofsvorstadt, 85 m², 3. OG',
                'beschreibung': 'Die Quartiere aus der Spitzenzeit haben '
                                'große Zuschnitte und Hanglage über der '
                                'Weißen Elster – Zufahrt und Halteplatz sind vorher zu klären.',
                'args': {'objektart': 'wohnung', 'qm': 85,
                         'stockwerk': '3og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Ladenlokal im Erdgeschoss, 120 m², mittel',
                'beschreibung': 'Gewerbeflächen werden nach Grundfläche gerechnet. '
                'Einbauten und Regale gehen mit raus.',
                'args': {'objektart': 'gewerbe', 'qm': 120,
                         'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.kreisentsorgung.de/Wertstoffh%C3%B6fe/Wertstoffhof-Plauen/',
        'sperrmuell_quelle': 'https://www.vogtlandkreis.de/abholung',
        'lokal_text': [
            {'text': ('Zuständig für die Sperrmüllabholung ist der Vogtlandkreis; '
                      'Auskunft gibt die Beratungsstelle Abfallwirtschaft unter 03741'
                      ' 300 2292. Die Gebührensätze weist der Landkreis auf seiner '
                      'Seite als gültig ab 2022 aus.'),
             'quellen': [('Vogtlandkreis, Abholung',
                          'https://www.vogtlandkreis.de/abholung')]},
            {'text': ('Kostenlos angenommen werden am Wertstoffhof unter anderem '
                      'Elektroschrott, Papier und Pappe, Problemabfälle in '
                      'Kleinstmengen, Schrott, kommunaler Sperrmüll und '
                      'Weihnachtsbäume. Gebühren fallen für Sperrmüll und '
                      'Siedlungsabfall aus Haushalten, Grüngut, Fenster, Türen und '
                      'Reifen an.'),
             'quellen': [('Kreisentsorgung Vogtland, Wertstoffhof Plauen',
                          'https://www.kreisentsorgung.de/Wertstoffh%C3%B6fe/Wertstoffhof-Plauen/')]},
            {'text': ('Plauen ist in 39 Stadtteile gegliedert; sechs davon haben als '
                      'Ortschaften eigene Ortschaftsräte: Neundorf, Jößnitz, '
                      'Kauschwitz, Straßberg, Großfriesen und Oberlosa. Zu den '
                      'Stadtteilen zählen außerdem Altstadt, Bahnhofsvorstadt, '
                      'Neustadt, Haselbrunn, Hofer Vorstadt, Reißiger Vorstadt, '
                      'Syratal, Thiergarten und Reinsdorf.'),
             'quellen': [('Stadt Plauen, Stadtteile und Ortschaften',
                          'https://www.plauen.de/Verwaltung-und-Stadtrat/Stadtinformationen/Zahlen-und-Fakten/Stadtteile-und-Ortschaften/')]},
            {'text': ('In Plauen nimmt der Sozialkeller der Diakonie in der '
                      'Friedensstraße 24 gut erhaltene Kleidung, Kindersachen, '
                      'Bettwäsche und Haushaltswaren an, allerdings nur dienstags '
                      'und mittwochs von 9 bis 13 Uhr sowie donnerstags von 13 bis '
                      '18 Uhr. Möbel nimmt der DIAshop Vogtland entgegen, wenn sie '
                      'modern und gut erhalten sind; seine Filialen liegen im '
                      'vogtländischen Auerbach und Reichenbach, nicht in Plauen '
                      'selbst.'),
             'quellen': [('Diakonie Plauen, Sozialkeller mit Kleiderbörse',
                          'https://diakonie-plauen.de/sozialkeller-mit-kleiderboerse/'),
                         ('DIAshop Vogtland',
                          'https://www.diashop-vogtland.de/')]},
            {'text': ('Das Amtsgericht Plauen in der Europaratstraße 13 ist die '
                      'Anlaufstelle für Nachlasssachen, sofern der Verstorbene '
                      'zuletzt in seinem Bezirk wohnte. Für Anliegen im '
                      'Nachlassgericht, im Grundbuchamt und an der '
                      'Rechtsantragstelle verlangt das Gericht vorab eine '
                      'Terminvereinbarung; die allgemeinen Öffnungszeiten stehen '
                      'auf seiner Seite.'),
             'quellen': [('Amtsgericht Plauen, Öffnungszeiten',
                          'https://www.justiz.sachsen.de/agpl/oeffnungszeiten-3978.html')]},
        ],
        'faq_zusatz': ('In Plauen nimmt der Wertstoffhof der Kreisentsorgung Vogtland '
                       'an der Klopstockstraße 15 Selbstanlieferungen an; Sperrmüll '
                       'holt der Vogtlandkreis auf Antrag ab.'),
    },
    'bautzen': {
        'ortsteile': ['Innenstadt', 'Gesundbrunnen', 'Südvorstadt',
                      'Westvorstadt', 'Ostvorstadt', 'Kleinwelka',
                      'Burk', 'Stiebitz', 'Niederkaina', 'Oberkaina',
                      'Salzenforst', 'Schmochtitz', 'Auritz',
                      'Nordostring'],
        'traeger': ('Landkreis Bautzen (Sperrmüll) und Veolia (Wertstoffhof)'),
        'quelle': ('https://www.landkreis-bautzen.de/landratsamt/dienstleistung/sperrmuellentsorgung/204'),
        'hof': ('Wertstoffhof Bautzen, Zeppelinstraße 1, betrieben von Veolia. '
                'Geöffnet Mo–Mi 8:00–12:00 und 12:30–18:00 Uhr, Do–Fr '
                '8:00–12:00 und 12:30–16:00 Uhr (November bis Februar) '
                'beziehungsweise bis 17:00 Uhr (März bis Oktober), dazu am '
                'ersten und dritten Samstag im Monat 8:00–12:00 Uhr. Bezahlt '
                'wird nur noch mit Karte.'),
        'sperrmuell': ('Einmal pro Jahr holt der Landkreis bis zu 4 m³ je privatem '
                       'Haushalt kostenlos ab. Bestellung über das Online-Formular '
                       '„Sperrmüllkarte-Online“; den Termin nennt das '
                       'Entsorgungsunternehmen etwa eine Woche vorher.'),
        'bebauung': ('Bautzen ist zweisprachig sorbisch-deutsch und hat eine auf '
                     'einem Granitfelsen liegende Altstadt mit Türmen und '
                     'Stadtmauer. Die Gassen dort sind eng und steil.'),
        'beispiele': [
            {
                'titel': 'Altstadtwohnung in der Oberstadt, 70 m², 2. OG',
                'beschreibung': 'Die Gassen auf dem Granitfelsen sind eng und '
                                'steil; mit längeren Tragewegen ist zu rechnen.',
                'args': {'objektart': 'wohnung', 'qm': 70,
                         'stockwerk': '2og', 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Einfamilienhaus in Kleinwelka, 120 m², voll',
                'beschreibung': 'Außerhalb der Oberstadt: ein Grundstück mit Keller und '
                'Dachboden.',
                'args': {'objektart': 'haus', 'qm': 120, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Kellerverschlag am Gesundbrunnen, 16 m², voll',
                'beschreibung': 'Kellerentrümpelung ohne die Wohnung darüber '
                                '– der häufigste Einzelauftrag in den '
                                'Wohnblöcken der Vorstädte.',
                'args': {'objektart': 'keller', 'qm': 16, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.veolia.de/ueber-uns/geschaeftsfelder/standorte-und-dienstleistungen/bautzen-wertstoffhof',
        'lokal_text': [
            {'text': ('Der Wertstoffhof in der Zeppelinstraße 1 wird von Veolia '
                      'betrieben, Telefon 03591 4900 73. Zwischen 12:00 und 12:30 Uhr'
                      ' ist Mittagspause. Seit dem 1. Juli 2025 wird dort nur noch '
                      'bargeldlos mit Karte bezahlt.'),
             'quellen': [('Veolia, Wertstoffhof Bautzen',
                          'https://www.veolia.de/ueber-uns/geschaeftsfelder/standorte-und-dienstleistungen/bautzen-wertstoffhof')]},
            {'text': ('Für größere Mengen gibt es Container, die spätestens zwei '
                      'Werktage vor dem Wunschtermin bestellt werden. Seit dem 1. '
                      'Juli 2026 kostet die Abholung eines Absetzcontainers bis 10 m³'
                      ' 104,38 € und die eines Abrollcontainers bis 36 m³ '
                      '130,47 €; bis 30. Juni 2026 waren es 34,07 € und 41,55 €. Die '
                      'Miete liegt zwischen 34,89 € und 261,67 € monatlich.'),
             'quellen': [('Landkreis Bautzen, Sperrmüllentsorgung',
                          'https://www.landkreis-bautzen.de/landratsamt/dienstleistung/sperrmuellentsorgung/204')]},
            {'text': ('Das Stadtportal gliedert die Stadt, zweisprachig '
                      'Bautzen/Budyšin, in 30 Stadtteile. Sechs bilden die Kernstadt:'
                      ' Innenstadt, Nordostring, Gesundbrunnen, Westvorstadt, '
                      'Südvorstadt und Ostvorstadt. Dazu kommen 24 dörfliche '
                      'Stadtteile, darunter Teichnitz, Burk, Nadelwitz, Oberkaina, '
                      'Kleinwelka und Großwelka. Ortschaftsräte bestehen in '
                      'Kleinwelka, Niederkaina, Salzenforst-Bolbritz und Stiebitz.'),
             'quellen': [('Stadt Bautzen, Stadtteile (PDF)',
                          'https://www.bautzen.de/fileadmin/media/statistik_wahlen/grundkarte_stt_2022.pdf'),
                         ('Ortschaftsräte',
                          'https://www.bautzen.de/buerger-rathaus-politik/stadtpolitik/ortschaftsraete/kleinwelka')]},
            {'text': ('Im Landkreis Bautzen holen Haushalte Schadstoffe am '
                      'Schadstoffmobil ab, ohne dass dafür weitere Kosten anfallen; '
                      'je Abgabe gelten Grenzen wie 10 Kilogramm Altfarben, 5 Liter '
                      'Altöl und 5 Kilogramm Pflanzenschutzmittel, Lithiumbatterien '
                      'sind ausgenommen. Ganzjährig geht es auch am Wertstoffhof in '
                      'der Zeppelinstraße 1 gegen Entgelt. Elektroaltgeräte und '
                      'Batterien nimmt derselbe Hof kostenlos an.'),
             'quellen': [('Landkreis Bautzen, Abfallkalender 2026, S. 35 und 50',
                          'https://www.landkreis-bautzen.de/download/Abfallamt/Abfallkalender_2026.pdf')]},
            {'text': ('„Ritas Möbel“ des Caritasverbands Oberlausitz im Bautzener '
                      'Stadtteil Gesundbrunnen, Platz der Völkerfreundschaft 8, '
                      'verkauft gespendete Möbel und Elektrogeräte an Menschen mit '
                      'geringem Einkommen. Wer Möbel abgeben möchte, vereinbart '
                      'einen Termin; die Mitarbeiter sehen sich die Stücke an und '
                      'holen sie kostenlos ab. Wer einen Haushalt auflöst, findet '
                      'auf der Seite des Dienstes ausdrücklich diese Möglichkeit '
                      'genannt.'),
             'quellen': [('Caritasverband Oberlausitz, Sozialer Möbeldienst',
                          'https://www.caritas-oberlausitz.de/hilfe-und-beratung/sozialer-moebeldienst/sozialer-moebeldienst')]},
        ],
        'faq_zusatz': ('In Bautzen nimmt der Wertstoffhof an der Zeppelinstraße 1 '
                       'Selbstanlieferungen an; der Landkreis holt Sperrmüll einmal im'
                       ' Jahr bis 4 m³ kostenlos ab.'),
    },
    'goerlitz': {
        'ortsteile': ['Innenstadt', 'Nikolaivorstadt', 'Südstadt',
                      'Rauschwalde', 'Weinhübel', 'Königshufen', 'Biesnitz',
                      'Klingewalde', 'Ludwigsdorf', 'Schlauroth', 'Kunnerwitz',
                      'Hagenwerder', 'Historische Altstadt', 'Klein Neundorf',
                      'Deutsch-Ossig', 'Tauchritz', 'Ober-Neundorf'],
        'traeger': 'EGLZ Entsorgungsgesellschaft Görlitz-Löbau-Zittau',
        'quelle': 'https://www.abfall-eglz.de/',
        'hof': ('Wertstoffhof Görlitz (EGLZ), Heilige-Grab-Straße 69: Mo, Mi und '
                'Fr 9–16 Uhr, Di und Do 9–17 Uhr, Sa 9–12 Uhr. Sperrmüll wird '
                'gegen Sperrmüllkarte angenommen, dazu Elektro- und '
                'Elektronikaltgeräte, Schrott, Papier, Leichtverpackungen, Glas '
                'und Batterien. Auskunft der EGLZ: 03585 4169-0.'),
        'sperrmuell': ('Zweimal im Jahr können je 2 m³ angemeldet werden, Einzelstücke '
                       'bis 50 kg. Abgeholt wird binnen vier Wochen, Bereitstellung am '
                       'Abholtag bis 6:00 Uhr, frühestens am Vorabend ab 16:00 Uhr. '
                       'Anmeldung online oder unter 03585 4169-0. Haushaltsauflösungen '
                       'fallen nicht unter die Sammlung.'),
        'beispiele': [
            {
                'titel': 'Wohnung in Nikolaivorstadt, 90 m², 3. OG, voll',
                'args': {'objektart': 'wohnung', 'qm': 90, 'stockwerk': '3og', 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus in Innenstadt, 150 m², voll',
                'args': {'objektart': 'haus', 'qm': 150, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung in Königshufen, 58 m², 4. OG mit Aufzug, mittel',
                'args': {'objektart': 'wohnung', 'qm': 58, 'stockwerk': '4og', 'aufzug': True, 'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.abfall-eglz.de/wertstoffhoefe',
        'sperrmuell_quelle': 'https://www.abfall-eglz.de/service/sperrmuellentsorgung',
        'lokal_text': [
            {'text': ('Auf dem Görlitzer Wertstoffhof, Heilige-Grab-Straße 69, '
                      'nimmt die EGLZ Sperrmüll gegen Vorlage der Sperrmüllkarte '
                      'an, außerdem Elektro- und Elektronikaltgeräte, Schrott, '
                      'Papier, Leichtverpackungen, Glas und Batterien (ohne '
                      'Starterbatterien). Montags, mittwochs und freitags ist von 9 '
                      'bis 16 Uhr geöffnet, dienstags und donnerstags bis 17 Uhr, '
                      'samstags von 9 bis 12 Uhr. Entladen müssen Anlieferer '
                      'selbst.'),
             'quellen': [('EGLZ, Wertstoffhöfe',
                          'https://www.abfall-eglz.de/wertstoffhoefe')]},
            {'text': ('Zweimal im Jahr kann Sperrmüll angemeldet werden, je Abfuhr '
                      'bis 2 m³ und mit Einzelteilen bis 50 kg. Anmeldung per Karte '
                      'aus dem Abfallkalender oder online, Abholung binnen vier '
                      'Wochen; bereitzustellen ist am Abholtag bis 6 Uhr, '
                      'frühestens am Vorabend ab 16 Uhr. Haushaltsauflösungen '
                      'fallen nicht unter die Sammlung, ebenso wenig Türen, '
                      'Fenster, Gartenzäune und Sanitärkeramik.'),
             'quellen': [('EGLZ, Sperrmüllentsorgung',
                          'https://www.abfall-eglz.de/service/sperrmuellentsorgung')]},
            {'text': ('Elektroaltgeräte lassen sich mit der Sperrmüllabholung '
                      'anmelden oder am Wertstoffhof abgeben. Schadstoffe sammelt '
                      'das Schadstoffmobil, das die EGLZ durch Veolia betreiben '
                      'lässt, an festen Standplätzen wie Marienplatz, '
                      'Sechsstädteplatz, Tivoli und Schlesischer Straße; vier '
                      'Termine je Jahr sind vorgesehen.'),
             'quellen': [('EGLZ, Sperrmüllentsorgung',
                          'https://www.abfall-eglz.de/service/sperrmuellentsorgung'),
                         ('EGLZ, Schadstoffmobil',
                          'https://www.abfall-eglz.de/service/schadstoffmobil')]},
            {'text': ('Gut erhaltene Möbel, Elektrogeräte und weiße Ware finden im '
                      'Sozialkaufhaus Görlitz einen zweiten Besitzer: Auf über '
                      '4.000 Quadratmetern in der Christoph-Lüders-Straße 46a wird '
                      'verkauft, ohne dass Nachweise nötig sind. Geöffnet ist '
                      'montags bis freitags von 10 bis 18 Uhr und samstags von 10 '
                      'bis 12 Uhr.'),
             'quellen': [('Sozialer Möbeldienst Görlitz, Sozialkaufhaus',
                          'https://goerlitzsozial.de/sozialkaufhaus/')]},
            {'text': ('Nachlassgericht ist laut Justizportal das Amtsgericht '
                      'Görlitz am Postplatz 18. Die Stadt besteht aus neun '
                      'Stadtteilen von der Historischen Altstadt bis Klingewalde '
                      'und den Ortsteilen Ober-Neundorf, Ludwigsdorf, Schlauroth, '
                      'Kunnerwitz, Klein Neundorf, Deutsch-Ossig, Hagenwerder und '
                      'Tauchritz. Weinhübel erhielt bis 1973 rund 4.000 Wohnungen '
                      'im Typ IW 64.'),
             'quellen': [('Justizportal, Orts- und Gerichtsverzeichnis (Nachlasssachen, PLZ 02826)',
                          'https://www.justizadressen.nrw.de/de/justiz/gericht?ang=nachlass&plzort=02826+Görlitz'),
                         ('Justiz Sachsen, Amtsgericht Görlitz',
                          'https://www.justiz.sachsen.de/aggr/kontakt-anreise-datenschutz-3916.html'),
                         ('Stadt Görlitz, Stadt- und Ortsteile',
                          'https://www.goerlitz.de/Stadt-_Ortsteile.html')]},
        ],
        'faq_zusatz': ('Geräumtes aus Görlitz geht an den Wertstoffhof '
                       'Heilige-Grab-Straße, in die Sperrmüllabholung der EGLZ '
                       '(Haushaltsauflösungen ausgenommen) oder ins Sozialkaufhaus.'),
    },

    # ══ Randgebiet Hannover / Braunschweig ═══════════════════════════════
    #
    # Sieben dieser Staedte gehoeren zum aha-Zweckverband und teilen sich
    # dadurch dieselbe Sperrmuellregelung. Die wird hier bewusst **wortgleich**
    # wiederholt statt siebenmal umformuliert: Umformulierter Fuelltext ist
    # genau das, was diese Datei vermeiden soll. Unterschieden werden die
    # Seiten ueber den Wertstoffhof und den Gebaeudebestand - die sind
    # tatsaechlich verschieden.

    'hannover': {
        'ortsteile': ['Mitte', 'List', 'Linden-Mitte', 'Linden-Nord',
                      'Linden-Süd', 'Vahrenwald', 'Südstadt', 'Bult',
                      'Ricklingen', 'Bothfeld', 'Kirchrode', 'Bemerode',
                      'Döhren', 'Herrenhausen', 'Stöcken', 'Kleefeld',
                      'Misburg-Nord', 'Misburg-Süd', 'Anderten'],
        'traeger': 'aha Zweckverband Abfallwirtschaft Region Hannover',
        'quelle': 'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe',
        'hof': ('Wertstoffhöfe der aha im Stadtgebiet: Mengendamm 15 (List), '
                'Wietzegraben 43 (Sahlkamp), Bornumer Straße 143 (Bornum), '
                'Schörlingstraße 3a (Linden-Mitte), Hansastraße 7 (Nordhafen), '
                'Tiestestraße 10 (Südstadt), Gertrud-Knebusch-Straße 2 (Nordstadt) '
                'und Döhrbruch 8, dazu die Deponie Hannover-Lahe, Moorwaldweg 312. '
                'Die Höfe öffnen Di 9–18:30, Mi–Fr 9–16, Sa 9–14 Uhr, montags '
                'geschlossen; die Deponien Mo–Fr 7–16:30, Sa 9–14 Uhr.'),
        'sperrmuell': ('aha holt bis zu 5 m³ Sperrabfall gebührenfrei ab; Einzelstücke '
                       'dürfen höchstens 2 m lang sein und nicht mehr als 75 kg wiegen. '
                       'Anmeldung unter (0800) 999 11 99 oder online, Bereitstellung bis '
                       '6 Uhr am Fahrbahnrand. Der Sperrabfall-Express kommt bei '
                       'Anmeldung bis 11 Uhr am nächsten Werktag (außer samstags) und '
                       'kostet 99,00 € per Gebührenbescheid (aha, Stand 10/2026). Am '
                       'Wertstoffhof ist täglich 1 m³ kostenfrei.'),
        'beispiele': [
            {
                'titel': 'Wohnung, 95 m², 4. OG, voll',
                'args': {'objektart': 'wohnung', 'qm': 95, 'stockwerk': '4og', 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 70 m², 4. OG mit Aufzug, mittel',
                'args': {'objektart': 'wohnung', 'qm': 70, 'stockwerk': '4og', 'aufzug': True, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Einfamilienhaus in Bothfeld, 140 m², voll',
                'args': {'objektart': 'haus', 'qm': 140, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe',
        'sperrmuell_quelle': 'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle',
        'lokal_text': [
            {'text': ('aha betreibt im Stadtgebiet neun Annahmestellen: Mengendamm '
                      'in der List, Wietzegraben im Sahlkamp, Bornumer Straße, '
                      'Schörlingstraße in Linden-Mitte, Hansastraße am Nordhafen, '
                      'Tiestestraße in der Südstadt, Gertrud-Knebusch-Straße in der '
                      'Nordstadt, Döhrbruch sowie die Deponie Lahe am Moorwaldweg. '
                      'Die Höfe öffnen dienstags bis 18:30 Uhr, mittwochs bis '
                      'freitags bis 16:00 Uhr und samstags bis 14:00 Uhr, montags '
                      'bleiben sie zu.'),
             'quellen': [('aha, Standortdaten der Annahmestellen',
                          'https://www.aha-region.de/app-fileadmin/annahmestellen/addresses.json'),
                         ('aha, Wertstoffhöfe',
                          'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe')]},
            {'text': ('Je Tag und Haushalt nimmt der Hof bis 1 m³ kostenlos. '
                      'Größere Mengen holt aha bei Anmeldung unter (0800) 999 11 99 '
                      'oder online ab: bis 5 m³, einzelne Stücke höchstens 2 m lang '
                      'und 75 kg schwer, bereitgestellt bis 6 Uhr am Fahrbahnrand. '
                      'Eilig? Der Sperrabfall-Express kommt bei Anmeldung bis 11 '
                      'Uhr am nächsten Werktag außer samstags und kostet 99,00 € '
                      '(aha, Stand 10/2026).'),
             'quellen': [('aha, Sperrabfälle',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle'),
                         ('aha, Sperrabfall-Express',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle/sperrabfall-express')]},
            {'text': ('Fernseher, Waschmaschinen und anderes Elektro gehört nicht '
                      'in den Sperrmüll. Großgeräte, höchstens zwei je Tag, nehmen '
                      'unter anderem die Höfe Schörlingstraße und Hannover-Lahe an; '
                      'Kleingeräte bis 50 cm Kantenlänge gehen auf jeden Hof. '
                      'Sonderabfälle aus Haushalten bleiben in kleineren Mengen '
                      'kostenlos, ab 30 kg fallen Gebühren an; Asbest und große '
                      'Batterien nimmt nur die Deponie Lahe.'),
             'quellen': [('aha, Wertstoffhöfe',
                          'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe'),
                         ('aha, Elektrogeräte',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/elektrogeraete'),
                         ('aha, Sonderabfälle',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sonderabfaelle')]},
            {'text': ('Weitergeben statt wegwerfen: Die gemeinnützige fairKauf eG '
                      'nimmt Möbel, Hausrat und Elektroartikel an, größere Mengen '
                      'in der zentralen Spendenannahme Vahrenwalder Straße 207; '
                      'Matratzen, Federbetten und PC bleiben ausgeschlossen. Große '
                      'Stücke holt fairKauf im Einzugsgebiet kostenfrei ab, nach '
                      'Anruf unter 0511 357659-0 und mit mehreren Werktagen '
                      'Vorlauf. Der kommunale Verschenkmarkt hannoverteilt.de '
                      'bringt Sofas und Lampen direkt zu Abholern.'),
             'quellen': [('fairKauf eG, Sachspenden',
                          'https://fairkauf-hannover.de/sachspenden/'),
                         ('hannover teilt',
                          'https://www.hannoverteilt.de'),
                         ('aha, Sperrabfälle',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle')]},
            {'text': ('Ende 2024 zählte Hannover 70.211 Wohngebäude, 58,7 % davon '
                      'Ein- und Zweifamilienhäuser. Die Wohnungen liegen trotzdem '
                      'fast alle in Mehrfamilienhäusern (84,9 %); im Stadtbezirk '
                      'Mitte sind es 97,3 %, in Bothfeld-Vahrenheide dagegen nur '
                      '63,5 %. Im Schnitt hat eine Wohnung 78,1 m².'),
             'quellen': [('Landeshauptstadt Hannover, Strukturdaten 2026 (PDF), Gebäude und Wohnungen',
                          'https://www.hannover.de/content/download/1070489/file/Strukturdaten%202026.pdf')]},
            {'text': ('Die Landeshauptstadt gliedert sich in 13 Stadtbezirke von '
                      'Mitte bis Nord, mit 558.767 Einwohnern am 31.12.2025. '
                      'Zuständiges Nachlassgericht ist das Amtsgericht Hannover, '
                      'Volgersweg 1, 30175 Hannover; es betreut auch Hemmingen, '
                      'Laatzen, Langenhagen und Seelze.'),
             'quellen': [('Landeshauptstadt Hannover, Strukturdaten 2026 (PDF)',
                          'https://www.hannover.de/content/download/1070489/file/Strukturdaten%202026.pdf'),
                         ('Amtsgericht Hannover, Zuständigkeiten',
                          'https://amtsgericht-hannover.niedersachsen.de/startseite/wir_uber_uns/zustandigkeiten/einfuhrung_graphische_darstellung_des_instanzenzuges/zustandigkeiten-63680.html'),
                         ('Amtsgericht Hannover, Kontakt',
                          'https://amtsgericht-hannover.niedersachsen.de/startseite/kontakt/')]},
        ],
        'faq_zusatz': ('Das Geräumte geht in Hannover an einen der aha-Wertstoffhöfe (bis '
                       '1 m³ täglich kostenfrei), über die aha-Sperrabfallabholung oder '
                       'gut erhalten an fairKauf und hannoverteilt.de.'),
    },
    'garbsen': {
        'ortsteile': ['Altgarbsen', 'Garbsen-Mitte', 'Auf der Horst',
                      'Berenbostel', 'Havelse', 'Horst', 'Frielingen',
                      'Heitlingen', 'Meyenfeld', 'Osterwald Oberende',
                      'Osterwald Unterende', 'Schloß Ricklingen', 'Stelingen'],
        'traeger': 'aha Zweckverband Abfallwirtschaft Region Hannover',
        'quelle': 'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe',
        'hof': ('Wertstoffhof Garbsen, Heinrich-Nordhoff-Ring 1, 30826 Garbsen '
                '(Osterwald Oberende): Di 9–18:30, Mi–Fr 9–16, Sa 9–14 Uhr, '
                'montags geschlossen. Grüngutannahmestellen in Berenbostel (Auf '
                'dem Kampe 50) und Schloß Ricklingen.'),
        'sperrmuell': ('aha holt bis zu 5 m³ Sperrabfall gebührenfrei ab; Einzelstücke '
                       'dürfen höchstens 2 m lang sein und nicht mehr als 75 kg wiegen. '
                       'Anmeldung unter (0800) 999 11 99 oder online, Bereitstellung bis '
                       '6 Uhr am Fahrbahnrand. Der Sperrabfall-Express kommt bei '
                       'Anmeldung bis 11 Uhr am nächsten Werktag (außer samstags) und '
                       'kostet 99,00 € per Gebührenbescheid (aha, Stand 10/2026). Am '
                       'Wertstoffhof ist täglich 1 m³ kostenfrei.'),
        'beispiele': [
            {
                'titel': 'Scheune in Berenbostel, 140 m², voll',
                'args': {'objektart': 'scheune', 'qm': 140, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung in Auf der Horst, 68 m², 4. OG mit Aufzug, voll',
                'args': {'objektart': 'wohnung', 'qm': 68, 'stockwerk': '4og', 'aufzug': True, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus in Frielingen, 130 m², voll',
                'args': {'objektart': 'haus', 'qm': 130, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.aha-region.de/app-fileadmin/annahmestellen/addresses.json',
        'sperrmuell_quelle': 'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle',
        'lokal_text': [
            {'text': ('Am Heinrich-Nordhoff-Ring 1 in Osterwald nimmt der '
                      'aha-Wertstoffhof Garbsen an, dienstags von 9:00 bis 18:30 '
                      'Uhr, mittwochs bis freitags von 9:00 bis 16:00 Uhr und '
                      'samstags von 9:00 bis 14:00 Uhr. Je Tag und Haushalt bleibt '
                      'bis 1 m³ kostenlos. Für Grünschnitt gibt es zusätzlich '
                      'Annahmestellen in Berenbostel am Weg Auf dem Kampe und in '
                      'Schloß Ricklingen.'),
             'quellen': [('aha, Standortdaten der Annahmestellen',
                          'https://www.aha-region.de/app-fileadmin/annahmestellen/addresses.json'),
                         ('aha, Wertstoffhöfe',
                          'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe')]},
            {'text': ('Abgeholt wird Sperrabfall regionsweit durch aha, kostenlos '
                      'bis 5 m³; kein Stück darf länger als 2 m oder schwerer als '
                      '75 kg sein. Terminvergabe und Fragen laufen über (0800) 999 '
                      '11 99 oder das Online-Formular, am Abholtag steht alles bis '
                      '6 Uhr am Fahrbahnrand, Holz gesondert. Der Express-Termin '
                      'für nächsten Werktag kostet 99,00 € (aha, Stand 10/2026).'),
             'quellen': [('aha, Sperrabfälle',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle'),
                         ('aha, Sperrabfall-Express',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle/sperrabfall-express')]},
            {'text': ('Waschmaschine, Herd oder Möbel mit fest eingebauter Elektrik '
                      'gelten als Elektroschrott und gehören nicht in den '
                      'Sperrmüll; Großgeräte nehmen nur bestimmte aha-Standorte an, '
                      'höchstens zwei je Person und Tag. Spraydosen, Chemikalien '
                      'und Lacke kommen als Sonderabfall bis 30 kg kostenlos zum '
                      'Hof.'),
             'quellen': [('aha, Elektrogeräte',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/elektrogeraete'),
                         ('aha, Sonderabfälle',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sonderabfaelle')]},
            {'text': ('Möbel in gutem Zustand finden im Sozialen Kaufhaus in der '
                      'Thomas-Mann-Straße 1 eine zweite Verwendung; die Region '
                      'Hannover führt es mit Öffnungszeiten montags bis freitags '
                      'von 9 bis 18 Uhr. Die Kaufhäuser verkaufen überwiegend '
                      'Spenden, nehmen aber nichts an, was als Sperrmüll gilt. '
                      'Kleidung geht an die DRK-Kleiderkammer am Planetenring 10.'),
             'quellen': [('Region Hannover, Soziales Kaufhaus Garbsen',
                          'https://www.hannover.de/Media/02-GIS-Objekte/Organisationsdatenbank/Landeshauptstadt-Hannover/Soziales/Sozialkaufh%C3%A4user-und-Kleiderkammern/Soziales-Kaufhaus-Garbsen'),
                         ('Region Hannover, Sozialkaufhäuser und Gebrauchtbörse',
                          'https://www.hannover.de/Leben-in-der-Region-Hannover/Soziales/Sozialleistungen-weitere-Hilfen/Sozialkaufh%C3%A4user-und-Gebrauchtb%C3%B6rse-f%C3%BCr-Stadt-und-Region-Hannover')]},
            {'text': ('Dreizehn Stadtteile bilden Garbsen, von Altgarbsen und Auf '
                      'der Horst über Berenbostel und Havelse bis Osterwald Ober- '
                      'und Unterende; die Stadt entstand 1974 aus elf ehemals '
                      'selbständigen Ortsteilen und zählte im September 2021 63.022 '
                      'Einwohner. Nachlasssachen gehören zum Amtsgericht Neustadt '
                      'am Rübenberge (Postfach 11 20, 31519 Neustadt, Tel. 05032 '
                      '9690).'),
             'quellen': [('Stadt Garbsen, Die Stadtteile',
                          'https://www.garbsen.de/portal/seiten/die-stadtteile-904000169-21200.html'),
                         ('Amtsgericht Neustadt, Aufgaben des Gerichts',
                          'https://www.amtsgericht-neustadt.niedersachsen.de/informationen/aufgaben_gerichts/aufgaben-des-gerichts-65978.html'),
                         ('Amtsgericht Neustadt, Kontakt',
                          'https://www.amtsgericht-neustadt.niedersachsen.de/startseite/kontakt/kontakt/kontakt-65980.html')]},
        ],
        'faq_zusatz': ('Das Geräumte geht in Garbsen auf den aha-Wertstoffhof '
                       'Heinrich-Nordhoff-Ring 1, über die aha-Sperrabfallabholung oder '
                       'gut erhalten ins Soziale Kaufhaus Thomas-Mann-Straße 1.'),
    },
    'langenhagen': {
        'ortsteile': ['Engelbostel', 'Godshorn', 'Kaltenweide', 'Krähenwinkel',
                      'Schulenburg'],
        'traeger': 'aha Zweckverband Abfallwirtschaft Region Hannover',
        'quelle': 'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle/sperrabfallabholung',
        'hof': ('Das aha-Standortverzeichnis führt in Langenhagen keinen '
                'Wertstoffhof, wohl aber drei Grüngutannahmestellen: Kaltenweide '
                '(Kananoher Straße, Ecke Auf der Heide), Krähenwinkel (Walsroder '
                'Straße 209) und Schulenburg (Dorfstraße 28).'),
        'sperrmuell': ('aha holt bis zu 5 m³ Sperrabfall gebührenfrei ab; Einzelstücke '
                       'dürfen höchstens 2 m lang sein und nicht mehr als 75 kg wiegen. '
                       'Anmeldung unter (0800) 999 11 99 oder online, Bereitstellung bis '
                       '6 Uhr am Fahrbahnrand. Der Sperrabfall-Express kommt bei '
                       'Anmeldung bis 11 Uhr am nächsten Werktag (außer samstags) und '
                       'kostet 99,00 € per Gebührenbescheid (aha, Stand 10/2026).'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus in Kaltenweide, 140 m², voll',
                'args': {'objektart': 'haus', 'qm': 140, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 70 m², 3. OG, voll',
                'args': {'objektart': 'wohnung', 'qm': 70, 'stockwerk': '3og', 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Gewerbefläche, 250 m², mittel',
                'args': {'objektart': 'gewerbe', 'qm': 250, 'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.aha-region.de/app-fileadmin/annahmestellen/addresses.json',
        'sperrmuell_quelle': 'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle/sperrabfallabholung',
        'lokal_text': [
            {'text': ('Einen eigenen Wertstoffhof führt das aha-Standortverzeichnis '
                      'in Langenhagen nicht; dafür stehen drei '
                      'Grüngutannahmestellen bereit: in Kaltenweide an der '
                      'Kananoher Straße, in Krähenwinkel an der Walsroder Straße '
                      '209 und in Schulenburg in der Dorfstraße 28. Sperriges und '
                      'Schadstoffe laufen über die Höfe der Region, etwa die '
                      'Deponie Burgdorf oder die Höfe im Stadtgebiet Hannover.'),
             'quellen': [('aha, Standortdaten der Annahmestellen',
                          'https://www.aha-region.de/app-fileadmin/annahmestellen/addresses.json')]},
            {'text': ('Beim Sperrmüll ist aha regionsweit zuständig: Abholung bis 5 '
                      'm³ kostenlos, Stücke höchstens 2 m lang und 75 kg, '
                      'Terminvergabe unter (0800) 999 11 99 oder online, '
                      'Bereitstellung bis 6 Uhr am Fahrbahnrand. Gegen 99,00 € '
                      '(aha, Stand 10/2026) gibt es den Express-Termin am nächsten '
                      'Werktag, wenn bis 11 Uhr angemeldet wird.'),
             'quellen': [('aha, Sperrabfälle',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle'),
                         ('aha, Sperrabfall-Express',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle/sperrabfall-express')]},
            {'text': ('Elektro- und Sondermüll haben eigene Wege: Kleingeräte und '
                      'Bildschirme nehmen die Wertstoffhöfe, Großgeräte nur '
                      'ausgewählte Standorte wie die Deponien Lahe und Burgdorf. '
                      'Möbel mit fest verbauter Elektrik zählen als Elektroschrott. '
                      'Sonderabfälle bis 30 kg aus Haushalten bleiben kostenlos; '
                      'alte Batterien über 500 g sind seit 2026 ein Fall für das '
                      'Zwischenlager Lahe.'),
             'quellen': [('aha, Elektrogeräte',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/elektrogeraete'),
                         ('aha, Sonderabfälle',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sonderabfaelle')]},
            {'text': ('Brauchbares bleibt vor Ort: Im City Center am Marktplatz 5 '
                      'führt die gemeinnützige fairKauf eG eine Filiale, die Möbel, '
                      'Hausrat und Kleidung zur Spende annimmt; Umzugskartons ohne '
                      'Termin zu den Öffnungszeiten, größere Möbel nach Anruf '
                      'mit kostenfreier Abholung. Kleidung nimmt außerdem die '
                      'DRK-Kleiderkammer in der Wilhelm-Hirte-Straße 29, dienstags '
                      'und donnerstags zu festen Stunden.'),
             'quellen': [('fairKauf eG',
                          'https://fairkauf-hannover.de/'),
                         ('Region Hannover, DRK-Kleiderkammer Langenhagen',
                          'https://www.hannover.de/Media/02-GIS-Objekte/Organisationsdatenbank/LHH-Region/Sozialkaufh%C3%A4user-und-Kleiderkammern/DRK-Kleiderkammer-Langenhagen')]},
            {'text': ('Langenhagen besteht aus dem Hauptort und fünf Ortsteilen mit '
                      'Ortschaftsverfassung: Engelbostel, Godshorn, Kaltenweide, '
                      'Krähenwinkel und Schulenburg; zusammen sind es nach dem '
                      'Melderegister 57.054 Einwohner (16.10.2025). Nachlassgericht '
                      'ist das Amtsgericht Hannover am Volgersweg 1, denn ein '
                      'eigenes Amtsgericht besteht in Langenhagen nicht.'),
             'quellen': [('Stadt Langenhagen, Stadtgliederung und Ortsteile',
                          'https://www.langenhagen.de/portal/seiten/stadtgliederung-und-ortsteile-900000033-30890.html'),
                         ('Amtsgericht Hannover, Kontakt',
                          'https://amtsgericht-hannover.niedersachsen.de/startseite/kontakt/')]},
        ],
        'faq_zusatz': ('Das Geräumte geht aus Langenhagen an die aha-Höfe der Region, '
                       'über die aha-Sperrabfallabholung oder gut erhalten an die '
                       'fairKauf-Filiale im City Center.'),
    },
    'burgdorf': {
        'ortsteile': ['Beinhorn', 'Dachtmissen', 'Heeßel', 'Hülptingsen',
                      'Otze', 'Ramlingen-Ehlershausen', 'Schillerslage',
                      'Sorgensen', 'Weferlingsen'],
        'traeger': 'aha Zweckverband Abfallwirtschaft Region Hannover',
        'quelle': 'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe',
        'hof': ('Deponie Burgdorf, Steinwedeler Straße, 31303 Burgdorf (aha): '
                'Mo–Fr 7–16:30 Uhr, Sa 9–14 Uhr. Grüngutannahmestellen in Otze '
                '(Burgdorfer Straße 51) und Ramlingen (Goldkuhle).'),
        'sperrmuell': ('aha holt bis zu 5 m³ Sperrabfall gebührenfrei ab; Einzelstücke '
                       'dürfen höchstens 2 m lang sein und nicht mehr als 75 kg wiegen. '
                       'Anmeldung unter (0800) 999 11 99 oder online, Bereitstellung bis '
                       '6 Uhr am Fahrbahnrand. Der Sperrabfall-Express kommt bei '
                       'Anmeldung bis 11 Uhr am nächsten Werktag (außer samstags) und '
                       'kostet 99,00 € per Gebührenbescheid (aha, Stand 10/2026). Am '
                       'Wertstoffhof ist täglich 1 m³ kostenfrei.'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus, 100 m², voll',
                'args': {'objektart': 'haus', 'qm': 100, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus, 135 m², mittel',
                'args': {'objektart': 'haus', 'qm': 135, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Scheune, 120 m², voll',
                'args': {'objektart': 'scheune', 'qm': 120, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.aha-region.de/app-fileadmin/annahmestellen/addresses.json',
        'sperrmuell_quelle': 'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle',
        'lokal_text': [
            {'text': ('Statt eines Wertstoffhofs betreibt aha in der Steinwedeler '
                      'Straße die Deponie Burgdorf: montags bis freitags von 7:00 '
                      'bis 16:30 Uhr und samstags von 9:00 bis 14:00 Uhr, also auch '
                      'montags, wenn die Höfe der Region ruhen. Haushalte geben '
                      'dort bis 1 m³ täglich kostenlos ab; Grüngut nehmen '
                      'Annahmestellen in Otze (Burgdorfer Straße 51) und in '
                      'Ramlingen (Goldkuhle) entgegen.'),
             'quellen': [('aha, Standortdaten der Annahmestellen',
                          'https://www.aha-region.de/app-fileadmin/annahmestellen/addresses.json'),
                         ('aha, Wertstoffhöfe',
                          'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe')]},
            {'text': ('Wer nicht fahren will, meldet Sperrabfall bei aha an, per '
                      'Telefon unter (0800) 999 11 99 oder online. Kostenlos geholt '
                      'werden bis 5 m³, jedes Stück höchstens 2 m lang und 75 kg '
                      'schwer. Bereitgestellt wird bis 6 Uhr, Holz getrennt. Bis 11 '
                      'Uhr bestellt, kommt der Express am nächsten Werktag, außer '
                      'samstags, für 99,00 € (aha, Stand 10/2026).'),
             'quellen': [('aha, Sperrabfälle',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle'),
                         ('aha, Sperrabfall-Express',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle/sperrabfall-express')]},
            {'text': ('Für Großgeräte wie Kühlschrank oder Herd führt der Weg zur '
                      'Deponie, die zu den wenigen Annahmestellen mit Großgeräten '
                      'zählt; je Person und Tag sind zwei erlaubt. Größere Mengen '
                      'Elektroschrott nimmt sie nach Voranmeldung. Batterien über '
                      '500 g, Asbest und Ähnliches bleiben dem Zwischenlager Lahe '
                      'vorbehalten.'),
             'quellen': [('aha, Wertstoffhöfe',
                          'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe'),
                         ('aha, Elektrogeräte',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/elektrogeraete'),
                         ('aha, Sonderabfälle',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sonderabfaelle')]},
            {'text': ('Bei Kleidung hilft die DRK-Kleiderkammer in Drei Eichen 5A: '
                      'montags von 14:00 bis 16:30 Uhr wird angenommen, donnerstags '
                      'im selben Zeitfenster ausgegeben. Für Möbel empfiehlt aha '
                      'ein soziales Kaufhaus der Region oder den Verschenkmarkt '
                      'hannoverteilt.de, statt gut Erhaltenes in den Sperrmüll zu '
                      'stellen.'),
             'quellen': [('Region Hannover, DRK-Kleiderkammer Burgdorf',
                          'https://www.hannover.de/Media/02-GIS-Objekte/Organisationsdatenbank/LHH-Region/Sozialkaufh%C3%A4user-und-Kleiderkammern/DRK-Kleiderkammer-Burgdorf'),
                         ('aha, Sperrabfälle',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle'),
                         ('hannover teilt',
                          'https://www.hannoverteilt.de')]},
            {'text': ('Seit der Gebietsreform 1974 gehören neun Ortschaften zu '
                      'Burgdorf: Beinhorn, Dachtmissen, Heeßel, Hülptingsen, Otze, '
                      'Ramlingen-Ehlershausen, Schillerslage, Sorgensen und '
                      'Weferlingsen. Auf 112,3 km² lebten zum 30.06.2024 laut '
                      'Landesamt für Statistik 31.156 Menschen. Nachlasssachen '
                      'bearbeitet das Amtsgericht Burgdorf, Schloßstraße 4, '
                      'zuständig auch für die Gemeinde Uetze.'),
             'quellen': [('Stadt Burgdorf, Burgdorf und seine Ortschaften',
                          'https://www.burgdorf.de/portal/seiten/burgdorf-und-seine-ortschaften-902000286-20500.html?vs=1'),
                         ('Stadt Burgdorf, Zahlen und Daten',
                          'https://www.burgdorf.de/portal/seiten/zahlen-daten-das-wichtigste-in-kuerze-902000158-20500.html?vs=1'),
                         ('Amtsgericht Burgdorf, Aufgaben und Zuständigkeit',
                          'https://www.amtsgericht-burgdorf.niedersachsen.de/wir_ueber_uns/aufgaben_und_zustaendigkeit/aufgaben-und-zustandigkeit-64302.html')]},
        ],
        'faq_zusatz': ('Das Geräumte geht in Burgdorf zur aha-Deponie Steinwedeler '
                       'Straße, über die aha-Sperrabfallabholung oder gut erhalten an die '
                       'Kleiderkammer des DRK.'),
    },
    'lehrte': {
        'ortsteile': ['Ahlten', 'Aligse', 'Arpke', 'Hämelerwald', 'Immensen',
                      'Kolshorn', 'Röddensen', 'Sievershausen', 'Steinwedel',
                      'Lehrte'],
        'traeger': 'aha Zweckverband Abfallwirtschaft Region Hannover',
        'quelle': 'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe',
        'hof': ('Der zuständige Wertstoffhof Lehrte/Sehnde liegt am Borsigring in '
                'Sehnde. Geöffnet Di 9:00–18:30 Uhr, Mi–Fr 9:00–16:00 Uhr, Sa '
                '9:00–14:00 Uhr, montags geschlossen.'),
        'sperrmuell': ('aha holt bis zu 5 m³ Sperrabfall gebührenfrei ab; Einzelstücke '
                       'dürfen höchstens 2 m lang sein und nicht mehr als 75 kg wiegen. '
                       'Anmeldung unter (0800) 999 11 99 oder online, Bereitstellung bis '
                       '6 Uhr am Fahrbahnrand. Der Sperrabfall-Express kommt bei '
                       'Anmeldung bis 11 Uhr am nächsten Werktag (außer samstags) und '
                       'kostet 99,00 € per Gebührenbescheid (aha, Stand 10/2026). Am '
                       'Wertstoffhof ist täglich 1 m³ kostenfrei.'),
        'beispiele': [
            {
                'titel': 'Wohnung, 72 m², 3. OG, voll',
                'args': {'objektart': 'wohnung', 'qm': 72, 'stockwerk': '3og', 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus, 110 m², voll',
                'args': {'objektart': 'haus', 'qm': 110, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus, 200 m², voll',
                'args': {'objektart': 'haus', 'qm': 200, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.hannover.de/Media/02-GIS-Objekte/Lokationsdatenbank/Region-Hannover/Entsorgung/Entsorgung/Wertstoffh%C3%B6fe/Wertstoffhof-Lehrte-Sehnde',
        'sperrmuell_quelle': 'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle',
        'lokal_text': [
            {'text': ('Zuständig ist der aha-Wertstoffhof Lehrte/Sehnde am '
                      'Borsigring in Sehnde. Dienstags ist von 9:00 bis 18:30 Uhr '
                      'geöffnet, mittwochs bis freitags bis 16:00 Uhr, samstags von '
                      '9:00 bis 14:00 Uhr; montags bleibt das Tor zu. '
                      'Privathaushalte geben dort einmal am Tag bis zu 1 m³ '
                      'kostenlos ab. Zwei Großgeräte je Person und Tag nimmt Sehnde '
                      'ebenfalls an.'),
             'quellen': [('hannover.de, Wertstoffhof Lehrte/Sehnde',
                          'https://www.hannover.de/Media/02-GIS-Objekte/Lokationsdatenbank/Region-Hannover/Entsorgung/Entsorgung/Wertstoffh%C3%B6fe/Wertstoffhof-Lehrte-Sehnde'),
                         ('aha, Wertstoffhöfe',
                          'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe')]},
            {'text': ('aha holt Sperrabfall bis 5 m³ kostenlos ab: Einzelstücke bis '
                      '2 m Länge und 75 kg, Anmeldung per Hotline (0800) 999 11 99 '
                      'oder online. Am Abholtag steht alles bis 6 Uhr am '
                      'Fahrbahnrand, Holz gesondert. Wer es eilig hat, bucht den '
                      'Sperrabfall-Express für 99,00 € (Stand 10/2026): Anruf bis '
                      '11 Uhr, Abholung am nächsten Werktag außer samstags.'),
             'quellen': [('aha, Sperrabfälle',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle'),
                         ('aha, Sperrabfall-Express',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle/sperrabfall-express')]},
            {'text': ('Elektrogeräte nimmt aha kostenlos zurück: Kleingeräte bis 50 '
                      'cm Kantenlänge und bis zu zwei Fernseher oder Monitore je '
                      'Person am Wertstoffhof, Großgeräte nur an ausgewählten '
                      'Standorten, darunter Sehnde. Sonderabfälle aus Haushalten '
                      'nehmen die Wertstoffhöfe in kleineren Mengen kostenlos an, '
                      'über 30 kg wird eine Gebühr fällig.'),
             'quellen': [('aha, Elektrogeräte',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/elektrogeraete'),
                         ('aha, Sonderabfälle',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sonderabfaelle')]},
            {'text': ('Brauchbares muss nicht in den Container: Das Soziale '
                      'Kaufhaus Lehrte der LABORA in der Burgdorfer Straße 37 '
                      'verkauft Möbel, Hausrat und Kleidung. Das Service-Team prüft '
                      'angebotene Möbel vor Ort und holt sie nach Terminabsprache '
                      'kostenlos ab. Zum Verschenken bietet aha den Online-Markt '
                      'hannoverteilt.de, Kleidung nimmt die DRK-Kleiderkammer in '
                      'der Ringstraße 9.'),
             'quellen': [('LABORA, Soziales Kaufhaus',
                          'https://www.labora.de/seite/805275/soka.html'),
                         ('Region Hannover, Sozialkaufhäuser und Gebrauchtbörse',
                          'https://www.hannover.de/Leben-in-der-Region-Hannover/Soziales/Sozialleistungen-weitere-Hilfen/Sozialkaufh%C3%A4user-und-Gebrauchtb%C3%B6rse-f%C3%BCr-Stadt-und-Region-Hannover'),
                         ('hannover teilt',
                          'https://www.hannoverteilt.de')]},
            {'text': ('Wird ein Nachlass abgewickelt, ist das Amtsgericht Lehrte in '
                      'der Schlesischen Straße 1 zuständig; sein Bezirk umfasst '
                      'Lehrte und Sehnde. Zu Erbschein, Ausschlagung oder '
                      'Testamentsverwahrung empfiehlt das Gericht einen vorherigen '
                      'Anruf unter 05132 826-153 oder -154. Zur Stadt gehören die '
                      'Ortsteile Ahlten, Aligse, Arpke, Hämelerwald, Immensen, '
                      'Kolshorn, Röddensen, Sievershausen und Steinwedel.'),
             'quellen': [('Amtsgericht Lehrte, Zuständigkeit',
                          'https://amtsgericht-lehrte.niedersachsen.de/wir_ueber_uns/zustaendigkeit/zustandigkeiten-195191.html'),
                         ('Amtsgericht Lehrte, Kontakt',
                          'https://amtsgericht-lehrte.niedersachsen.de/startseite/kontakt/kontaktinformationen_und_formular/kontakt-64800.html'),
                         ('Stadt Lehrte, Ortsteile',
                          'https://www.lehrte.de/ortsteile/')]},
        ],
        'faq_zusatz': ('Das Geräumte geht in Lehrte an den aha-Wertstoffhof Lehrte/Sehnde '
                       'am Borsigring, in die kostenlose aha-Sperrabfallabholung (bis 5 '
                       'm³) oder, wenn es noch gut ist, ins Soziale Kaufhaus Lehrte.'),
    },
    'springe': {
        'ortsteile': ['Alferde', 'Altenhagen I', 'Alvesrode', 'Bennigsen',
                      'Boitzum', 'Stadt Eldagsen', 'Gestorf', 'Holtensen',
                      'Lüdersen', 'Mittelrode', 'Völksen', 'Springe'],
        'traeger': 'aha Zweckverband Abfallwirtschaft Region Hannover',
        'quelle': 'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe',
        'hof': ('Wertstoffhof Springe, Oppelner Straße. Geöffnet Di 9:00–18:30 '
                'Uhr, Mi–Fr 9:00–16:00 Uhr, Sa 9:00–14:00 Uhr, montags '
                'geschlossen.'),
        'sperrmuell': ('aha holt bis zu 5 m³ Sperrabfall gebührenfrei ab; Einzelstücke '
                       'dürfen höchstens 2 m lang sein und nicht mehr als 75 kg wiegen. '
                       'Anmeldung unter (0800) 999 11 99 oder online, Bereitstellung bis '
                       '6 Uhr am Fahrbahnrand. Der Sperrabfall-Express kommt bei '
                       'Anmeldung bis 11 Uhr am nächsten Werktag (außer samstags) und '
                       'kostet 99,00 € per Gebührenbescheid (aha, Stand 10/2026). Am '
                       'Wertstoffhof ist täglich 1 m³ kostenfrei.'),
        'beispiele': [
            {
                'titel': 'Scheune, 150 m², voll',
                'args': {'objektart': 'scheune', 'qm': 150, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus, 110 m², voll',
                'args': {'objektart': 'haus', 'qm': 110, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung in Bennigsen, 75 m², 1. OG, voll',
                'args': {'objektart': 'wohnung', 'qm': 75, 'stockwerk': '1og', 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.hannover.de/Media/02-GIS-Objekte/Lokationsdatenbank/Region-Hannover/Entsorgung/Entsorgung/Wertstoffh%C3%B6fe/Wertstoffhof-Springe',
        'sperrmuell_quelle': 'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle',
        'lokal_text': [
            {'text': ('Der aha-Wertstoffhof Springe an der Oppelner Straße ist '
                      'dienstags von 9:00 bis 18:30 Uhr offen, mittwochs bis '
                      'freitags von 9:00 bis 16:00 Uhr und samstags von 9:00 bis '
                      '14:00 Uhr; montags geschlossen. Bis 1 m³ je Tag nehmen die '
                      'Mitarbeiter aus Privathaushalten ohne Gebühr, darunter '
                      'Sperrabfälle und Textilien.'),
             'quellen': [('hannover.de, Wertstoffhof Springe',
                          'https://www.hannover.de/Media/02-GIS-Objekte/Lokationsdatenbank/Region-Hannover/Entsorgung/Entsorgung/Wertstoffh%C3%B6fe/Wertstoffhof-Springe'),
                         ('aha, Wertstoffhöfe',
                          'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe')]},
            {'text': ('Bis zu 5 m³ Sperrabfall holt aha gebührenfrei vor der Tür '
                      'ab, jedes Stück höchstens 2 m lang und 75 kg schwer. '
                      'Terminvergabe per Hotline (0800) 999 11 99 oder online. '
                      'Schneller geht der Express: Anruf bis 11 Uhr, Abholung am '
                      'nächsten Werktag, 99,00 € per Bescheid (Stand 10/2026). '
                      'Möbel mit nicht ausbaubarer Elektronik zählen nicht zum '
                      'Sperrabfall.'),
             'quellen': [('aha, Sperrabfälle',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle'),
                         ('aha, Sperrabfall-Express',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle/sperrabfall-express')]},
            {'text': ('Für Großgeräte führt aha eine eigene Standortliste; Springe '
                      'steht darin nicht, genannt werden etwa Sehnde, Burgdorf, '
                      'Bissendorf und die Deponie Kolenfeld. Kleingeräte bis 50 cm '
                      'Kantenlänge gehen dagegen auf jeden Wertstoffhof. '
                      'Sonderabfälle bis 30 kg bleiben kostenlos.'),
             'quellen': [('aha, Elektrogeräte',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/elektrogeraete'),
                         ('aha, Sonderabfälle',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sonderabfaelle')]},
            {'text': ('Die Stadt Springe unterhält in der Hamelner Straße 24 ein '
                      'Möbellager: gebrauchte Möbel für Menschen aus Springe mit '
                      'SGB-II- oder SGB-XII-Bescheid oder Möbelbezugsschein, '
                      'donnerstags 10–12 und 14–15:30 Uhr. Kleidung nimmt die '
                      'DRK-Kleiderkammer An der Bleiche 4–6; Verschenkbares lässt '
                      'sich auf hannoverteilt.de einstellen.'),
             'quellen': [('Stadt Springe, Möbellager',
                          'https://www.springe.de/buergerservice/dienstleistungen/moebellager-900000228-0.html'),
                         ('Region Hannover, Sozialkaufhäuser und Gebrauchtbörse',
                          'https://www.hannover.de/Leben-in-der-Region-Hannover/Soziales/Sozialleistungen-weitere-Hilfen/Sozialkaufh%C3%A4user-und-Gebrauchtb%C3%B6rse-f%C3%BCr-Stadt-und-Region-Hannover'),
                         ('hannover teilt',
                          'https://www.hannoverteilt.de')]},
            {'text': ('Springe besteht aus zwölf Stadtteilen, vom Kernort Springe '
                      'über Bennigsen, Völksen und die Stadt Eldagsen bis Boitzum; '
                      'die Stadt zählt 30.338 Einwohner (Stand 30.06.2026). '
                      'Nachlasssachen führt das Amtsgericht Springe, Zum Oberntor '
                      '2: Testamente, Erbscheine, Nachlasspflegschaft; ein Termin '
                      'ist nötig.'),
             'quellen': [('Stadt Springe, Stadtteile',
                          'https://www.springe.de/freizeitinspringe/stadtmarketing/stadtteile/'),
                         ('Amtsgericht Springe, Nachlasssachen',
                          'https://amtsgericht-springe.niedersachsen.de/startseite/service/nachlasssachen/informationen-zu-nachlasssachen-im-allgmeinen-233155.html'),
                         ('Landgericht Hannover, Amtsgericht Springe',
                          'https://www.landgericht-hannover.niedersachsen.de/startseite/die_amtsgerichte/amtsgericht_springe/amtsgericht-springe-58695.html')]},
        ],
        'faq_zusatz': ('Das Geräumte nimmt in Springe der aha-Wertstoffhof an der '
                       'Oppelner Straße an; Sperrabfall holt aha bis 5 m³ gebührenfrei '
                       'ab, gut erhaltene Möbel für Bedürftige das Möbellager der Stadt '
                       'in der Hamelner Straße 24.'),
    },
    'wunstorf': {
        'ortsteile': ['Steinhude', 'Luthe', 'Bokeloh', 'Kolenfeld',
                      'Großenheidorn', 'Klein Heidorn', 'Blumenau mit Liethe',
                      'Idensen', 'Mesmerode', 'Wunstorf'],
        'traeger': 'aha Zweckverband Abfallwirtschaft Region Hannover',
        'quelle': 'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe',
        'hof': ('Wertstoffhof der Deponie Wunstorf im Ortsteil Kolenfeld (31515): '
                'Mo–Fr 7:00–16:30 Uhr, Sa 9:00–14:00 Uhr.'),
        'sperrmuell': ('aha holt bis zu 5 m³ Sperrabfall gebührenfrei ab; Einzelstücke '
                       'dürfen höchstens 2 m lang sein und nicht mehr als 75 kg wiegen. '
                       'Anmeldung unter (0800) 999 11 99 oder online, Bereitstellung bis '
                       '6 Uhr am Fahrbahnrand. Der Sperrabfall-Express kommt bei '
                       'Anmeldung bis 11 Uhr am nächsten Werktag (außer samstags) und '
                       'kostet 99,00 € per Gebührenbescheid (aha, Stand 10/2026). Am '
                       'Wertstoffhof ist täglich 1 m³ kostenfrei.'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus in Steinhude, 90 m², voll',
                'args': {'objektart': 'haus', 'qm': 90, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 68 m², 2. OG, voll',
                'args': {'objektart': 'wohnung', 'qm': 68, 'stockwerk': '2og', 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus, 120 m², voll',
                'args': {'objektart': 'haus', 'qm': 120, 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe',
        'sperrmuell_quelle': 'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle',
        'lokal_text': [
            {'text': ('Der aha-Wertstoffhof an der Deponie Wunstorf liegt im '
                      'Ortsteil Kolenfeld; man fährt durch das Deponietor und dann '
                      'links. Geöffnet ist werktags von 7:00 bis 16:30 Uhr, '
                      'samstags von 9:00 bis 14:00 Uhr. Haushalte geben bis zu 1 m³ '
                      'am Tag kostenlos ab, größere Mengen nimmt die Deponie nach '
                      'Voranmeldung gegen Gebühr, Altholz etwa mit 94,52 € je Tonne '
                      '(Stand 10/2026).'),
             'quellen': [('aha, Wertstoffhöfe',
                          'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe'),
                         ('aha, Deponie Wunstorf',
                          'https://www.aha-region.de/service/fuehrungen/ueber-die-deponie-wunstorf'),
                         ('aha, Abfallbehandlung und Deponien',
                          'https://www.aha-region.de/entsorgung-und-recycling/abfallbehandlung-und-deponien')]},
            {'text': ('Von der Haustür holt aha Sperrabfall bis 5 m³ gebührenfrei '
                      'ab, Einzelteile bis 2 m und 75 kg. Bestellt wird per Hotline '
                      '(0800) 999 11 99 oder online, bereitgestellt am Abholtag bis '
                      '6 Uhr. Holz kommt in ein zweites Fahrzeug und gehört deshalb '
                      'zusammen. Möbel mit fest eingebauter Elektronik, Glas und '
                      'Baustellenabfälle nimmt die Abholung nicht mit.'),
             'quellen': [('aha, Sperrabfälle',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle'),
                         ('aha, Sperrabfall-Express',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sperrabfaelle/sperrabfall-express')]},
            {'text': ('Großgeräte nimmt aha nur an wenigen Standorten an, in der '
                      'Region Wunstorf in Kolenfeld, zwei Stück je Person und Tag. '
                      'Kleingeräte und Bildschirme gehen auf jeden Wertstoffhof. '
                      'Sonderabfälle aus Haushalten nimmt aha in kleineren Mengen '
                      'kostenlos an, über 30 kg wird eine Gebühr fällig.'),
             'quellen': [('aha, Wertstoffhöfe',
                          'https://www.aha-region.de/entsorgung-und-recycling/wertstoffhoefe'),
                         ('aha, Elektrogeräte',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/elektrogeraete'),
                         ('aha, Sonderabfälle',
                          'https://www.aha-region.de/abfaelle-und-wertstoffe/sonderabfaelle')]},
            {'text': ('Gebrauchte Möbel nimmt der IcksPlus Möbelmarkt in der '
                      'Adolph-Brosang-Straße 18 als Spende an, ebenso intakte '
                      'moderne Kleidung und Haushaltsware; Spendenannahme Mo–Fr '
                      '10–17:30 Uhr und Sa 10–15:30 Uhr. Möbel holt das Team gern '
                      'zu Hause ab, vorab am besten anrufen (05031 9554-44) und ein '
                      'Foto schicken. Kleidung nimmt außerdem der Kleiderladen in '
                      'der Nordstraße 11.'),
             'quellen': [('IcksPlus Möbelmarkt, Spenden',
                          'https://www.icks-plus.de/spenden/'),
                         ('Region Hannover, Sozialkaufhäuser und Gebrauchtbörse',
                          'https://www.hannover.de/Leben-in-der-Region-Hannover/Soziales/Sozialleistungen-weitere-Hilfen/Sozialkaufh%C3%A4user-und-Gebrauchtb%C3%B6rse-f%C3%BCr-Stadt-und-Region-Hannover')]},
            {'text': ('Für Nachlasssachen aus Wunstorf ist das Amtsgericht Neustadt '
                      'am Rübenberge am Ludwig-Enneccerus-Platz 2 zuständig, dessen '
                      'Bezirk auch Garbsen und Neustadt umfasst. Verwahrung von '
                      'Testamenten und Erbscheinsanträge laufen dort nur nach '
                      'Terminvergabe. Die Stadt gliedert sich in zehn Ortschaften, '
                      'darunter Steinhude, Luthe, Bokeloh und Kolenfeld.'),
             'quellen': [('Amtsgericht Neustadt a. Rbge., Aufgaben',
                          'https://www.amtsgericht-neustadt.niedersachsen.de/startseite/informationen/aufgaben_des_gerichts/aufgaben-des-gerichts-65978.html'),
                         ('Amtsgericht Neustadt a. Rbge., Nachlasssachen',
                          'https://www.amtsgericht-neustadt.niedersachsen.de/startseite/service/nachlasssachen/ubersicht/'),
                         ('Stadt Wunstorf, Ortschaften',
                          'https://www.wunstorf.de/rathaus-politik/stadtgeschichte/ortschaften/')]},
        ],
        'faq_zusatz': ('Das Geräumte lässt sich in Wunstorf am aha-Wertstoffhof an der '
                       'Deponie Kolenfeld abgeben, über die kostenlose '
                       'aha-Sperrabfallabholung (bis 5 m³) entsorgen oder, wenn noch gut, '
                       'beim IcksPlus Möbelmarkt abgeben.'),
    },
    'braunschweig': {
        'ortsteile': ['Mitte', 'Weststadt', 'Östliches Ringgebiet',
                      'Westliches Ringgebiet', 'Braunschweig-Süd',
                      'Südstadt-Rautheim-Mascherode', 'Lehndorf-Watenbüttel',
                      'Nordstadt-Schunteraue', 'Hondelage-Volkmarode',
                      'Wabe-Schunter-Beberbach', 'Südwest',
                      'Nördliche Schunter-/Okeraue'],
        'traeger': 'ALBA Braunschweig GmbH im Auftrag der Stadt Braunschweig',
        'quelle': 'https://www.braunschweig.de/vv/produkte/0/alba/sperrmuell.php',
        'hof': ('Wertstoffhof der ALBA Braunschweig, Frankfurter Straße 251, 38122 '
                'Braunschweig (nur Privatanlieferer): Mo–Mi 9:00–16:45 Uhr, Do '
                '11:00–20:00 Uhr, Fr 9:00–16:45 Uhr. Restabfall und Sperrmüll '
                'kosten 15,00 € je Anlieferung bis 3 m³, Papier, Metalle, '
                'Kunststoffe und Elektrogeräte werden kostenlos angenommen; '
                'größere Mengen nur im AEZ Watenbüttel.'),
        'sperrmuell': ('Die Abholung ist hier nicht kostenlos: ALBA berechnet 20,00 € je '
                       '5 m³, jede weitere angefangene Menge von 5 m³ kostet erneut 20,00 '
                       '€ (Stand 10/2026). Bestellt wird online, im Kundenzentrum, mit '
                       'Wertmarke und Sperrmüllkarte per Post oder per Überweisung.'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus, 110 m², voll',
                'args': {'objektart': 'haus', 'qm': 110, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung in Weststadt, 68 m², 4. OG mit Aufzug, mittel',
                'args': {'objektart': 'wohnung', 'qm': 68, 'stockwerk': '4og', 'aufzug': True, 'fuellgrad': 'mittel'},
            },
            {
                'titel': 'Wohnung, 75 m², 3. OG, voll',
                'args': {'objektart': 'wohnung', 'qm': 75, 'stockwerk': '3og', 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://alba-bs.de/service/kunden-zentren.html',
        'sperrmuell_quelle': 'https://alba-bs.de/service/abfallentsorgung/sperrmuell.html',
        'lokal_text': [
            {'text': ('In Braunschweig nimmt ALBA am Wertstoffhof Frankfurter '
                      'Straße 251 ab: montags bis mittwochs 9:00–16:45 Uhr, '
                      'donnerstags 11:00–20:00 Uhr, freitags 9:00–16:45 Uhr. '
                      'Restabfall und Sperrmüll kosten 15,00 € je Anlieferung bis 3 '
                      'm³ (Stand 10/2026), Papier, Metall, Kunststoffe, Textilien '
                      'und Elektroaltgeräte nichts. Größere Mengen gehen zum AEZ '
                      'Watenbüttel, Celler Heerstraße 335.'),
             'quellen': [('ALBA Braunschweig, Kundenzentren',
                          'https://alba-bs.de/service/kunden-zentren.html')]},
            {'text': ('Die Sperrmüllabholung im Auftrag der Stadt kostet 20,00 € je '
                      'angefangene 5 m³ (Stand 10/2026). Buchen lässt sie sich '
                      'online, im Kundenzentrum, mit Wertmarke und Karte oder per '
                      'Überweisung; bereitgestellt wird am Abholtag bis 6:00 Uhr im '
                      'öffentlichen Verkehrsraum. Wer Möbel nicht selbst '
                      'herausstellen kann, kann Sperrmüll-Plus mit Demontage und '
                      'Heraustragen für 250,00 € bis 5 m³ zuzüglich 20,00 € Gebühr '
                      'beauftragen.'),
             'quellen': [('ALBA Braunschweig, Sperrmüll',
                          'https://alba-bs.de/service/abfallentsorgung/sperrmuell.html'),
                         ('Stadt Braunschweig, Sperrmüll',
                          'https://www.braunschweig.de/vv/produkte/0/alba/sperrmuell.php')]},
            {'text': ('Elektrogeräte gibt ALBA kostenlos an AEZ und Wertstoffhof '
                      'zurück; Elektrokleingeräte nehmen außerdem 47 '
                      'Wertstoffstationen auf. Schadstoffe bis 20 Liter je Gebinde '
                      'gehören ebenfalls an die beiden Höfe oder ans '
                      'Schadstoffmobil; Asbest braucht eine '
                      'Anlieferungsgenehmigung.'),
             'quellen': [('ALBA Braunschweig, Elektrogeräte',
                          'https://alba-bs.de/service/abfallentsorgung/elektro.html'),
                         ('ALBA Braunschweig, Schadstoffe',
                          'https://alba-bs.de/service/abfallentsorgung/schadstoff.html'),
                         ('ALBA Braunschweig, Kundenzentren',
                          'https://alba-bs.de/service/kunden-zentren.html')]},
            {'text': ('Noch brauchbare Möbel nimmt die Möbelhalle der Lebenshilfe '
                      'im Rebenpark, Geysostraße 20, werktags bis 15:30 Uhr an; '
                      'nach Absprache holt das Team sie auch zu Hause ab, im '
                      'Zeitfenster 8–10, 10–12 oder 13–15 Uhr. Verkauft wird im '
                      'FAIRKAUF-Kaufhaus in der Stecherstraße 4.'),
             'quellen': [('Lebenshilfe Braunschweig, FAIRKAUF Möbelhalle',
                          'https://www.lebenshilfe-braunschweig.de/einkaufen/fairkauf-moebelhalle/')]},
            {'text': ('Die Stadt gliedert sich in zwölf Stadtbezirke von Mitte über '
                      'Weststadt und Östliches Ringgebiet bis '
                      'Wabe-Schunter-Beberbach; 254.469 Menschen leben hier (Stand '
                      '31.12.2025). Nachlassfälle gehören vor die Nachlassabteilung '
                      'des Amtsgerichts Braunschweig, An der Martinikirche 8.'),
             'quellen': [('Stadt Braunschweig, Einwohnerzahlen nach Stadtbezirken',
                          'https://www.braunschweig.de/politik_verwaltung/statistik/ez_stadtbezirke.php'),
                         ('Amtsgericht Braunschweig, Nachlassabteilung',
                          'https://www.amtsgericht-braunschweig.niedersachsen.de/startseite/wir_uber_uns/unsere_zustandigkeiten/nachlassabteilung/nachlassabteilung-70698.html')]},
        ],
        'faq_zusatz': ('Das Geräumte lässt sich in Braunschweig am ALBA-Wertstoffhof '
                       'Frankfurter Straße 251 abgeben, über die ALBA-Sperrmüllabholung '
                       '(20,00 € je 5 m³, Stand 10/2026) abholen lassen oder, wenn noch '
                       'gut, der Möbelhalle der Lebenshilfe geben.'),
    },
    'salzgitter': {
        'ortsteile': ['Lebenstedt', 'Salzgitter-Bad', 'Thiede',
                      'Gebhardshagen', 'Salder', 'Lichtenberg', 'Hallendorf',
                      'Watenstedt', 'Engelnstedt', 'Bruchmachtersen',
                      'Ringelheim', 'Barum'],
        'traeger': 'Städtische Regiebetriebe Salzgitter (SRB)',
        'quelle': 'https://service.salzgitter.de/dienstleistungen/-/egov-bis-detail/dienstleistung/4393/show',
        'hof': ('Entsorgungszentrum Salzgitter (EZS), Abfallentsorgungsanlage '
                'Diebesstieg 50: Mo–Fr im Sommer 7:00–17:30 Uhr, im Winter '
                '7:30–16:30 Uhr, Sa 8–13 Uhr. Anlieferung aus Privathaushalten nur '
                'mit vorheriger Zeitraum-Reservierung unter entsorgungszentrum.de. '
                'Die Abgabe von Sperrmüll ist gebührenpflichtig, Elektroaltgeräte '
                'aus Haushalten werden kostenlos angenommen.'),
        'sperrmuell': ('Die Abholung durch den SRB ist gebührenpflichtig: 40,00 € bis 5 '
                       'm³, 30,00 € je weiterer angefangener m³ (Stand 10/2026). Bestellt '
                       'wird schriftlich über die Sperrmüllkarte; Karten gibt es im '
                       'BürgerCenter Rathaus Lebenstedt, im Kleinen Rathaus Bad sowie '
                       'beim SRB am Korbmacherweg 5.'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus in Lebenstedt, 100 m², voll',
                'args': {'objektart': 'haus', 'qm': 100, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Scheune, 130 m², voll',
                'args': {'objektart': 'scheune', 'qm': 130, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 65 m², 2. OG, voll',
                'args': {'objektart': 'wohnung', 'qm': 65, 'stockwerk': '2og', 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www2.salzgitter.de/leben/srb/diebesstieg.php',
        'sperrmuell_quelle': 'https://www.salzgitter.de/leben/srb/sperrmuell.php',
        'lokal_text': [
            {'text': ('Auf der Abfallentsorgungsanlage Diebesstieg 50 nimmt das '
                      'Entsorgungszentrum (EZS) Abfälle aus Privathaushalten '
                      'an, jedoch nur nach vorheriger Zeitraum-Reservierung auf '
                      'entsorgungszentrum.de. Geöffnet ist im Sommer montags bis '
                      'freitags 7:00–17:30 Uhr, im Winter 7:30–16:30 Uhr, samstags '
                      '8:00–13:00 Uhr. Sperrmüll kostet dort Gebühr, '
                      'Elektroaltgeräte nicht.'),
             'quellen': [('Stadt Salzgitter, Diebesstieg',
                          'https://www2.salzgitter.de/leben/srb/diebesstieg.php'),
                         ('Entsorgungszentrum Salzgitter, Privatkunden',
                          'https://entsorgungszentrum.de/privatkunden/')]},
            {'text': ('Die Sperrmüllabholung der Städtischen Regiebetriebe kostet '
                      '40,00 € bis 5 m³ und 30,00 € je weiterer angefangener m³ '
                      '(Stand 10/2026). Bestellt wird schriftlich mit der '
                      'Sperrmüllkarte, erhältlich im BürgerCenter Lebenstedt, im '
                      'Kleinen Rathaus in Bad, beim SRB am Korbmacherweg 5 und im '
                      'Abfallkalender. Elektrogeräte stehen getrennt,'),
             'quellen': [('Stadt Salzgitter, Sperrmüll',
                          'https://www.salzgitter.de/leben/srb/sperrmuell.php'),
                         ('Stadt Salzgitter, Serviceportal Sperrmüll',
                          'https://service.salzgitter.de/dienstleistungen/-/egov-bis-detail/dienstleistung/4393/show')]},
            {'text': ('Schadstoffe aus Privathaushalten nimmt das '
                      'Sonderabfallzwischenlager am Diebesstieg kostenlos an; '
                      'ausgenommen sind Altöl und Reifen. Elektroaltgeräte aus '
                      'Haushalten bleiben ebenfalls gebührenfrei.'),
             'quellen': [('Entsorgungszentrum Salzgitter, Privatkunden',
                          'https://entsorgungszentrum.de/privatkunden/'),
                         ('Stadt Salzgitter, Serviceportal',
                          'https://service.salzgitter.de/dienstleistungen/-/egov-bis-detail/dienstleistung/4393/show')]},
            {'text': ('Zu gut zum Wegwerfen: Das Caritas FairKaufhaus in der '
                      'Albert-Schweitzer-Straße 30 verkauft gebrauchte Möbel, '
                      'Haushaltsartikel und Kleidung, montags bis freitags 10–18 '
                      'Uhr. Nach kostenfreier Besichtigung holt die Caritas '
                      'verwendbare Stücke ab. Online verschenkt oder tauscht man '
                      'auf verschenkmarkt-salzgitter.de.'),
             'quellen': [('Caritas Salzgitter, FairKaufhaus',
                          'https://www.caritas-sz.de/einrichtungen/fairkaufhaus/'),
                         ('Verschenkmarkt Salzgitter',
                          'https://www.verschenkmarkt-salzgitter.de/')]},
            {'text': ('Salzgitter gliedert sich laut Wikipedia (Sekundärquelle) in '
                      '31 Stadtteile in sieben Ortschaften und kennt keine '
                      'Kernstadt. Das Amtsgericht in der '
                      'Joachim-Campe-Straße 15 in Lebenstedt führt das '
                      'Nachlassgericht für die Stadt und die Samtgemeinde '
                      'Baddeckenstedt; Erbausschlagungen sind seit dem 01.03.2026 '
                      'nur nach Terminabsprache möglich.'),
             'quellen': [('Amtsgericht Salzgitter, Bezirk und Zuständigkeit',
                          'https://amtsgericht-salzgitter.niedersachsen.de/gericht/allgemeines/bezirk-und-zustandigkeit-166823.html'),
                         ('Amtsgericht Salzgitter, Nachlassgericht',
                          'https://amtsgericht-salzgitter.niedersachsen.de/startseite/service/nachlassgericht/'),
                         ('Wikipedia, Salzgitter (Sekundärquelle)',
                          'https://de.wikipedia.org/wiki/Salzgitter')]},
        ],
        'faq_zusatz': ('Das Geräumte lässt sich vor Ort am Entsorgungszentrum '
                       'Diebesstieg (mit Reservierung), über die SRB-Sperrmüllabholung '
                       '(ab 40,00 €, Stand 10/2026) oder beim Caritas FairKaufhaus '
                       'abgeben.'),
    },
    'peine': {
        'ortsteile': ['Vöhrum', 'Stederdorf', 'Schwicheldt', 'Dungelbeck',
                      'Woltorf', 'Handorf', 'Essinghausen', 'Duttenstedt',
                      'Eixe', 'Röhrse', 'Rosenthal', 'Berkum', 'Schmedenstedt',
                      'Wendesse'],
        'traeger': ('Abfallwirtschafts- und Beschäftigungsbetriebe des Landkreises '
                    'Peine (AB Peine)'),
        'quelle': 'https://www.ab-peine.de/Abfallinfo/Sperrm%C3%BCll/',
        'hof': ('Abfallentsorgungszentrum (AEZ) Stedum, Hildesheimer Straße 15, '
                '31249 Hohenhameln: Mo, Di, Do und Fr 8–16 Uhr, Mi 8–17 Uhr, Sa '
                '8–12 Uhr. Zusätzlich der Wertstoffhof in der Fritz-Stegen-Allee: '
                'Di–Fr 8–16 Uhr, Sa 8–12 Uhr, montags geschlossen. Kundenzentrum '
                'der AB Peine: 05171 7791-66.'),
        'sperrmuell': ('Bis zu 4 m³ je Haushalt und Jahr sind gebührenfrei, abgeholt oder '
                       'in Stedum angeliefert. Wichtig: Das Kontingent ist mit der ersten '
                       'Anlieferung aufgebraucht – auch dann, wenn es weniger als 4 m³ '
                       'waren. Abgeholt wird auf Bestellung mit schriftlichem Termin.'),
        'beispiele': [
            {
                'titel': 'Wohnung, 70 m², 3. OG, voll',
                'args': {'objektart': 'wohnung', 'qm': 70, 'stockwerk': '3og', 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus in Vöhrum, 130 m², voll',
                'args': {'objektart': 'haus', 'qm': 130, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 60 m², 1. OG, voll',
                'args': {'objektart': 'wohnung', 'qm': 60, 'stockwerk': '1og', 'fuellgrad': 'voll'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.ab-peine.de/Standorte/Abfallentsorgungszentrum/',
        'sperrmuell_quelle': 'https://www.ab-peine.de/Abfallinfo/Sperrm%C3%BCll/',
        'lokal_text': [
            {'text': ('Das Abfallentsorgungszentrum (AEZ) in Stedum liegt an der '
                      'Hildesheimer Straße 15 in Hohenhameln und nimmt Restmüll, '
                      'Sperrmüll, Wertstoffe, haushaltsübliche Schadstoffe und '
                      'Elektroaltgeräte an. Geöffnet ist montags, dienstags, '
                      'donnerstags und freitags 8–16 Uhr, mittwochs bis 17 Uhr, '
                      'samstags 8–12 Uhr. In der Stadt selbst gibt es den Wertstoffhof '
                      'Fritz-Stegen-Allee, montags geschlossen.'),
             'quellen': [('A+B Peine, Abfallentsorgungszentrum',
                          'https://www.ab-peine.de/Standorte/Abfallentsorgungszentrum/'),
                         ('A+B Peine, Wertstoffhof Peine',
                          'https://www.ab-peine.de/Standorte/Wertstoffh%C3%B6fe/Wertstoffhof-Peine/')]},
            {'text': ('Je Haushalt und Jahr sind 4 m³ Sperrmüll gebührenfrei, '
                      'abgeholt oder in Stedum angeliefert. Das Kontingent ist mit '
                      'der ersten Anlieferung verbraucht, auch bei weniger Menge. '
                      'Darüber kostet es 28,00 € je angefangene 4 m³ (Stand '
                      '10/2026); der Express in drei Werktagen 50,00 €. Bestellt '
                      'wird im Kundenportal, per Formular, Telefon oder E-Mail, '
                      'bereitgestellt bis 6:30 Uhr nach Fraktionen.'),
             'quellen': [('A+B Peine, Sperrmüll',
                          'https://www.ab-peine.de/Abfallinfo/Sperrm%C3%BCll/')]},
            {'text': ('Elektroaltgeräte nimmt der Landkreis am AEZ Stedum '
                      '(Sonderabfallzwischenlager) und am Wertstoffhof Fritz-Stegen-Allee an. '
                      'Dort sind außerdem Hohlglas, Altkleider, Papier, Gelber Sack '
                      'und Metall kostenfrei.'),
             'quellen': [('A+B Peine, Abfallentsorgungszentrum',
                          'https://www.ab-peine.de/Standorte/Abfallentsorgungszentrum/'),
                         ('A+B Peine, Wertstoffhof Peine',
                          'https://www.ab-peine.de/Standorte/Wertstoffh%C3%B6fe/Wertstoffhof-Peine/'),
                         ('A+B Peine, Elektroaltgeräte',
                          'https://www.ab-peine.de/Abfallinfo/Elektroaltger%C3%A4te/')]},
            {'text': ('Das Soziale Kaufhaus Peine der LABORA in der Stederdorfer '
                      'Straße 28 verkauft Möbel, Haushaltswaren und Kleidung, Mo–Fr '
                      '9–18 und Sa 9–14 Uhr. Möbelspenden prüft der Service vor Ort '
                      'und holt sie nach Terminabsprache kostenlos ab.'),
             'quellen': [('LABORA, Soziales Kaufhaus',
                          'https://www.labora.de/seite/805275/soka.html')]},
            {'text': ('Zur Stadt zählen Ortschaften wie Vöhrum, Stederdorf, Woltorf, '
                      'Handorf und Essinghausen, insgesamt vierzehn Namen seit der '
                      'Gebietsreform 1974. Nachlasssachen bearbeitet das '
                      'Amtsgericht Peine am Amthof, dessen Bezirk auch Edemissen, '
                      'Hohenhameln, Ilsede und Lengede umfasst; Termin unter 05171 '
                      '705-0.'),
             'quellen': [('Stadt Peine, Ortschaften',
                          'https://www.peine.de/de/stadtleben/ortschaften/'),
                         ('Amtsgericht Peine, Zuständigkeit',
                          'https://amtsgericht-peine.niedersachsen.de/startseite/wir_uber_uns/zustandigkeit/zustandigkeit-59988.html')]},
        ],
        'faq_zusatz': ('Das Geräumte lässt sich vor Ort am AEZ Stedum oder am Wertstoffhof '
                       'Fritz-Stegen-Allee abgeben, über die Sperrmüllabholung (4 m³ gebührenfrei, '
                       'Stand 10/2026) abholen lassen oder beim Sozialen Kaufhaus der LABORA '
                       'unterbringen.'),
    },
    'celle': {
        'ortsteile': ['Blumlage/Altstadt', 'Neuenhäusen', 'Hehlentor',
                      'Westercelle', 'Altencelle', 'Klein Hehlen',
                      'Groß Hehlen', 'Vorwerk', 'Garßen', 'Wietzenbruch',
                      'Altenhagen', 'Scheuen', 'Boye', 'Bostel', 'Hustedt',
                      'Lachtehausen', 'Neustadt/Heese'],
        'traeger': 'Zweckverband Abfallwirtschaft Celle (ZAC)',
        'quelle': 'https://www.zacelle.de/',
        'hof': ('Der ZAC betreibt Annahmestellen in Altencelle (Braunschweiger '
                'Heerstraße 111), Hambühren, Hermannsburg und Höfer bei '
                'Scharnhorst. Verwaltung: Braunschweiger Heerstraße 109, 29227 '
                'Celle; 05141 7502-222 ist die Bestell- und Servicenummer.'),
        'sperrmuell': ('Standardabholung 36,00 € bis 6 m³, im Voraus zu zahlen, mit etwa '
                       'sechs Wochen Vorlauf; Bestellung online oder unter 05141 '
                       '7502-222. Selbst angeliefert kostet Sperrmüll an den Anlagen '
                       '134,00 € je Tonne (Mindestgebühr 8,40 €), Stand 10/2026.'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus, 120 m², voll',
                'args': {'objektart': 'haus', 'qm': 120, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 70 m², 2. OG, voll',
                'args': {'objektart': 'wohnung', 'qm': 70, 'stockwerk': '2og', 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus in Westercelle, 130 m², mittel',
                'args': {'objektart': 'haus', 'qm': 130, 'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://www.zacelle.de/entsorgungsanlagen/standorte-oeffnungszeiten',
        'sperrmuell_quelle': 'https://www.zacelle.de/sperrmuell',
        'lokal_text': [
            {'text': ('Der ZAC betreibt '
                      'Annahmestellen in Altencelle (Braunschweiger Heerstraße '
                      '111), Hambühren, Hermannsburg und Höfer bei Scharnhorst. '
                      'Altencelle und Hambühren sind werktags von 8 bis 16 Uhr und '
                      'samstags von 8 bis 13 Uhr offen; Höfer bleibt montags '
                      'geschlossen. Sperrmüll kostet dort 134,00 € je Tonne bei '
                      '8,40 € Mindestgebühr (Stand 10/2026).'),
             'quellen': [('ZAC Celle, Standorte und Öffnungszeiten',
                          'https://www.zacelle.de/entsorgungsanlagen/standorte-oeffnungszeiten'),
                         ('ZAC Celle, Sperrmüll an den Annahmestellen',
                          'https://www.zacelle.de/sperrmuell/annahmestellen')]},
            {'text': ('Wer abholen lässt, zahlt für Sperrmüll Standard 36,00 € bis '
                      '6 m³ im Voraus und rechnet mit etwa sechs Wochen Vorlauf; '
                      'Bestellung online oder unter 05141 7502-222. Einzelstücke '
                      'dürfen höchstens 75 kg wiegen, bereitzustellen ist am '
                      'Abfuhrtag bis 6 Uhr. Aus Keller oder Wohnung holt Service '
                      'Plus ab, ab 31,00 € je Stück; der Express-Service innerhalb '
                      'von drei Werktagen kostet 236,00 €.'),
             'quellen': [('ZAC Celle, Sperrmüll',
                          'https://www.zacelle.de/sperrmuell'),
                         ('ZAC Celle, Sperrmüllabfuhr bestellen',
                          'https://www.zacelle.de/sperrmuell/sperrmuellabfuhr-bestellen'),
                         ('ZAC Celle, Sperrmüll-Service Express',
                          'https://www.zacelle.de/sperrmuell/sperrmuell-service-express'),
                         ('ZAC Celle, Sperrmüll-Service Plus',
                          'https://www.zacelle.de/sperrmuell/sperrmuell-service-plus')]},
            {'text': ('Schadstoffe nehmen Altencelle, Hermannsburg, Höfer und '
                      'Hambühren in haushaltsüblichen Mengen bis 25 kg oder 20 '
                      'Liter kostenlos. Elektroaltgeräte gehen an alle Anlagen, '
                      'außer Kühlgeräten auch zur Lebenshilfe in Altencelle (Alte '
                      'Dorfstraße 4) und in Bergen. Asbest-Kleinmengen und bis zu '
                      'fünf Big Bags Dämmwolle werden angenommen.'),
             'quellen': [('ZAC Celle, Schadstoffe',
                          'https://www.zacelle.de/abfallarten/schadstoffe'),
                         ('ZAC Celle, Elektrogeräte',
                          'https://www.zacelle.de/abfallarten/elektrogeraete')]},
            {'text': ('Gut erhaltener Hausrat hat in der Stadt drei Anlaufstellen der '
                      'Lebenshilfe Celle: Kaufladen Blumlage 38, Allerhand in der '
                      'Mummenhofstraße 13 und Neufundland, Neustadt 63. Sie nehmen '
                      'Haushaltswaren, Porzellan und Kleidung an; Möbel und '
                      'Elektrogeräte lehnen sie ab, Abholung gibt es nicht.'),
             'quellen': [('Kaufladen Celle, Spenden',
                          'https://www.kaufladen-celle.de/5-0-Spenden.html'),
                         ('Allerhand Celle, Spenden',
                          'https://allerhand-celle.de/5-0-Spenden.html'),
                         ('Neufundland Celle, Spenden',
                          'https://www.neufundland-celle.de/5-0-Spenden.html')]},
            {'text': ('Celle gliedert sich in 17 Ortsteile, von Blumlage/Altstadt '
                      'über Neustadt/Heese und Westercelle bis Wietzenbruch. '
                      'Nachlassfragen klärt das Amtsgericht Celle, Mühlenstraße 8: '
                      'Einen Termin vereinbart man telefonisch, Zentrale 05141 '
                      '206-0.'),
             'quellen': [('Stadt Celle, Ortsteile',
                          'https://www.celle.de/Stadt/%C3%9Cber-Celle/Ortsteile/'),
                         ('Amtsgericht Celle, Nachlassgericht',
                          'https://www.amtsgericht-celle.niedersachsen.de/startseite/wir_uber_uns/nachlassgericht/nachlass-und-erbangelegenheiten-132211.html')]},
        ],
        'faq_zusatz': ('Das Geräumte lässt sich vor Ort an den ZAC-Anlagen (Altencelle, '
                       'Hambühren, Hermannsburg, Höfer) abgeben, über die '
                       'ZAC-Sperrmüllabholung (ab 36,00 €, Stand 10/2026) abholen lassen; '
                       'Hausrat nehmen die Lebenshilfe-Läden.'),
    },
    'hameln': {
        'ortsteile': ['Altstadt', 'Mitte', 'Wehl', 'Nord', 'Ost', 'Süd',
                      'West', 'Afferde', 'Hilligsfeld', 'Halvestorf',
                      'Haverbeck', 'Hastenbeck', 'Sünteltal', 'Klein Berkel',
                      'Rohrsen', 'Tündern', 'Wehrbergen', 'Wangelist'],
        'traeger': 'Kreisabfallwirtschaft Hameln-Pyrmont (KAW)',
        'quelle': 'https://kaw.hameln-pyrmont.de/Abfuhrmodalit%C3%A4ten/Sperrm%C3%BCll/',
        'hof': ('Entsorgungspark Hameln der KAW, Zum Sachsengrund 15, an der '
                'Kreisstraße 60 zwischen Afferde und Hilligsfeld; bezahlt wird '
                'bargeldlos per EC-Karte. Kundenservice: Ohsener Straße 98, 31789 '
                'Hameln.'),
        'sperrmuell': ('Zweimal im Jahr sind je 4 m³ gebührenfrei. Anmeldung online, per '
                       'Brief oder Postkarte oder im Kundenservice; der Sperrmüll-Blitz '
                       'ist gebührenpflichtig.'),
        'beispiele': [
            {
                'titel': 'Einfamilienhaus, 130 m², voll',
                'args': {'objektart': 'haus', 'qm': 130, 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Wohnung, 75 m², 3. OG, voll',
                'args': {'objektart': 'wohnung', 'qm': 75, 'stockwerk': '3og', 'fuellgrad': 'voll'},
            },
            {
                'titel': 'Einfamilienhaus in Klein Berkel, 120 m², mittel',
                'args': {'objektart': 'haus', 'qm': 120, 'fuellgrad': 'mittel'},
            },
        ],
        'stand_iso': '2026-10',
        'hof_quelle': 'https://kaw.hameln-pyrmont.de/Standorte/Entsorgungspark/',
        'sperrmuell_quelle': 'https://kaw.hameln-pyrmont.de/Abfuhrmodalit%C3%A4ten/Sperrm%C3%BCll/',
        'lokal_text': [
            {'text': ('Der Entsorgungspark Hameln der Kreisabfallwirtschaft liegt '
                      'Zum Sachsengrund 15. Von März bis Oktober ist montags bis '
                      'freitags 14 bis 17 Uhr und samstags 8 bis 12:30 Uhr '
                      'geöffnet, im Winter kürzer. Hausmüll und Sperrmüll kosten '
                      '6,00 € je angefangene 100 Liter, Holz 3,00 €, Elektrogeräte, '
                      'Metall und Papier nichts (Stand 10/2026). Schadstoffe nimmt '
                      'der Park nicht an.'),
             'quellen': [('KAW Hameln-Pyrmont, Entsorgungspark',
                          'https://kaw.hameln-pyrmont.de/Standorte/Entsorgungspark/'),
                         ('KAW Hameln-Pyrmont, Gebühren Entsorgungspark',
                          'https://kaw.hameln-pyrmont.de/Service/Geb%C3%BChren/Entsorgungspark/')]},
            {'text': ('Zweimal im Jahr holt die KAW bis 4 m³ Sperrmüll gebührenfrei '
                      'ab. Anmeldung online, per Karte oder im Kundenservice '
                      'Ohsener Straße 98. Am Abfuhrtag ist alles bis 6:00 Uhr nach '
                      'Fraktionen getrennt bereitzustellen; kein Stück über 70 kg '
                      'und 2,20 m Länge. Eilige buchen den gebührenpflichtigen '
                      'Sperrmüll-Blitz.'),
             'quellen': [('KAW Hameln-Pyrmont, Sperrmüll',
                          'https://kaw.hameln-pyrmont.de/Abfuhrmodalit%C3%A4ten/Sperrm%C3%BCll/')]},
            {'text': ('Schadstoffe sammelt in Hameln die PreZero Service Mitte in '
                      'der Dieselstraße 7 jeden ersten Samstag im Monat von 10 bis '
                      '12 Uhr; Elektrogeräte werden dort nicht angenommen, sie '
                      'gehören in den Entsorgungspark.'),
             'quellen': [('KAW Hameln-Pyrmont, Schadstoffsammelstellen',
                          'https://kaw.hameln-pyrmont.de/Standorte/Schadstoffsammelstellen/')]},
            {'text': ('Der Zweite Markt der AIBP in der Stüvestraße 45 verkauft auf '
                      '1.500 m² Möbel, Hausrat und Kleidung, montags bis freitags 8 '
                      'bis 17 Uhr. Gut erhaltene Gebrauchtwaren holt der Verein '
                      'nach Terminabsprache kostenlos ab; Anruf unter 05281 9325-0.'),
             'quellen': [('AIBP, Second-Hand-Kaufhäuser',
                          'https://www.aibp.de/second-hand-kaufhaeuser/'),
                         ('AIBP, Möbeldienst',
                          'https://www.aibp.de/moebeldienst-und-hausmeisterservice/'),
                         ('Stadt Hameln, FamilienApp Second Hand',
                          'https://familienapp.hameln.de/infos/second-hand-in-hameln/')]},
            {'text': ('Zu Hameln gehören sieben statistische Bezirke von Altstadt '
                      'bis Wehl und elf Ortschaften, darunter Afferde, Hastenbeck, '
                      'Klein Berkel und Tündern; 59.048 Menschen leben hier (Stand '
                      '31.12.2024). Das Nachlassgericht sitzt im Amtsgericht Hameln '
                      'am Zehnthof 1 und ist für den ganzen Landkreis zuständig.'),
             'quellen': [('Stadt Hameln, Hamelns Ortsteile',
                          'https://www.hameln.de/de/buergerservice-verwaltung/blick-in-die-geschichte/hamelns-ortsteile'),
                         ('Amtsgericht Hameln, Zuständigkeit',
                          'https://www.amtsgericht-hameln.niedersachsen.de/startseite/wir_uber_uns/zustandigkeit/zustandigkeit-70638.html')]},
        ],
        'faq_zusatz': ('Das Geräumte nimmt in Hameln der KAW-Entsorgungspark (Zum '
                       'Sachsengrund 15) an; gebrauchte Möbel holt der Zweite Markt der '
                       'AIBP nach Absprache kostenlos ab.'),
    },
}


#: EIG83 (24.09.2026): In Sachsen und Sachsen-Anhalt heisst eine Raeumung oft
#: "Beraeumung" (so nennt es services.py selbst). Gesucht wird das Wort auch:
#: "beraeumung meissen" Pos. 7,1, "beraeumung dresden" 53 Impressionen - aber
#: keine der Stadtseiten enthielt es. city.html nennt es einmal im Satz ueber
#: den Leistungen, nur in den Laendern, in denen man es sagt.
REGIONALES_WORT = {
    'Sachsen': 'Beräumung',
    'Sachsen-Anhalt': 'Beräumung',
}


def regionales_wort(bundesland):
    """Das regionale Wort fuer "Raeumung" in diesem Bundesland - oder ``''``."""
    return REGIONALES_WORT.get(bundesland, '')


def stand(slug):
    """``(iso, deutsch)`` des Recherchestands einer Stadt.

    Seit dem 24.09.2026 kann ein Eintrag ein eigenes ``stand_iso`` tragen -
    Leipzig und die drei neuen Umlandorte sind im September recherchiert und
    sollen nicht den August behaupten. Ohne Feld gilt ``STAND_ISO``.
    """
    iso = (LOKAL.get(slug) or {}).get('stand_iso') or STAND_ISO
    return iso, _stand_deutsch(iso)


def parken_stand(slug):
    """``(iso, deutsch)`` fuer die Parken-Karte - eigener Stand, sonst der des Eintrags."""
    iso = (LOKAL.get(slug) or {}).get('parken_stand_iso')
    return (iso, _stand_deutsch(iso)) if iso else stand(slug)


def lokal(slug):
    """Die Ortsangaben zu einem Stadt-Slug - oder ``None``.

    ``None`` ist ein zulaessiger Zustand: Fuer eine Stadt ohne recherchierte
    Angaben blendet das Template den Abschnitt aus. Lieber kein Abschnitt als
    ein erfundener.
    """
    return LOKAL.get(slug)


def beispiele(slug, stadtname=''):
    """Die durchgerechneten Ortsbeispiele einer Stadt - oder ``[]``.

    Baugleich zu ``services.beispiel_preise()``: In ``LOKAL`` stehen nur die
    *Eingaben*, den Preis liefert ``berechne_preis()``. Der sichtbare Rechenweg
    (``details['schritte']``) entsteht dabei in derselben Rechnung und ist
    damit garantiert der Weg zu genau diesem Preis.

    ``stadtname`` wird als ``stadtort`` durchgereicht, damit der
    Standortrabatt greift - genau wie er es taete, wenn der Besucher die Stadt
    im Rechner eintraegt. Das macht die Beispiele nebenbei stadtspezifisch:
    In den 25 Rabattstaedten stehen andere Zahlen als anderswo.

    ``[]`` ist ein zulaessiger Zustand. Eine Stadt ohne recherchierten
    Gebaeudebestand bekommt keine erfundenen Beispiele, sondern keinen
    Abschnitt - dieselbe Regel wie fuer jedes andere Feld hier.
    """
    daten = LOKAL.get(slug) or {}
    aus = []
    for b in daten.get('beispiele', ()):
        preis, details = _berechne_preis(stadtort=stadtname, **b['args'])
        aus.append({
            'titel': b['titel'],
            # Optional seit 02.10.2026: Beschreibungen, die auf drei und mehr
            # Stadtseiten wortgleich standen ("Keller, Dachboden und Garage
            # sind im Hauspreis enthalten." 37-mal), sind entfallen - den
            # Rechenweg zeigt das Beispiel selbst.
            'beschreibung': b.get('beschreibung', ''),
            'preis': preis,
            'preis_txt': f"{_euro(preis)} €",
            'schritte': details['schritte'],
        })
    return aus
