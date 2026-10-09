# -*- coding: utf-8 -*-
"""Die Belegstellen der Wissenstexte - jede Adresse genau einmal (GE43).

**Warum es dieses Modul gibt.** Die Messung vom 17.09.2026 fand sechs von acht
Ratgeberseiten ohne eine einzige nachpruefbare Quelle. Die Texte nannten ihre
Fundstellen zwar ("§35a EStG", "BGH, Az. VIII ZR 124/05") - aber nirgends die
Stelle zum Nachschlagen, und eine Fundstelle, die niemand aufschlagen kann, ist
eine Behauptung mit Aktenzeichen.

Gebraucht wird die Liste von **zwei** Datenmodulen: ``ratgeber.py`` fuer die
fuenf Artikel und die Uebersicht, ``services.py`` fuer
``/entruempelung-kosten/`` - den Ratgeber unter einem Leistungs-Slug
(``services.RATGEBER_SEITEN``). ``ratgeber.py`` importiert aus ``services.py``,
also darf ``services.py`` nicht zurueckimportieren; deshalb steht die Tabelle
hier und nicht in einem der beiden. Regel 1, fuer die sechste Sorte Angabe.

**Der Beleg ist seit dem 01.10.2026 ein echter Verweis** (GE43). Bis dahin
stand er nur als Text da: Der Regelkatalog raet zum Verlinken, aber ein
zusaetzliches ``<a>`` je Artikel veraendert die Zahl der Elemente und Links im
Koerper, und daran haengt die Designwache des Paketlaufs. Der Betrieb hat den
Link am 01.10.2026 trotzdem gewollt - ein Beleg, den man nur abtippen kann, ist
weniger wert. Der Beleg steht an zwei Stellen:

* als **Satz mit Link** (``<a href=... rel="noopener">``), angehaengt an den
  letzten Absatz des Abschnitts, zu dem er gehoert - ``einsetzen()``. Der
  Absatz laeuft in allen Vorlagen durch ``|safe``; ``satz()`` maskiert deshalb
  jeden Wert selbst. Wer den Beleg als **reinen Text** braucht (Schema,
  llms.txt, Feed), nimmt ``satz_text()`` - dort darf kein HTML stehen;
* als ``citation`` im ``Article``- bzw. ``CollectionPage``-Knoten
  (``schema._citation``), wo Antwortmaschinen ihn maschinell lesen.

Beides aus **dieser** Liste, nie zweimal getippt (Regel 12).

⚠ **Eine tote Adresse ist schlechter als keine** - dieselbe Ueberlegung wie bei
``sameAs`` (Regel 25). Kein Werkzeug dieses Projekts merkt es: ``check_seo``
und ``manage.py test`` laufen ohne Netz und rufen keine fremde Seite auf. Wer
eine Quelle ergaenzt, ruft sie einmal von Hand auf und traegt den Stand unten
nach.

Aufgenommen wird nur, was den Satz im Text wirklich traegt: die Norm im
Volltext beim Herausgeber. Der Ratgeber eines fremden Anbieters waere keine
Quelle, sondern eine zweite Meinung.

Regel 4: Das Modul importiert nichts - auch nichts aus ``data/``.
"""

from html import escape as _escape

__all__ = ['QUELLEN', 'STAND_ISO', 'kurzadresse', 'satz', 'satz_text',
           'einsetzen', 'aus_schluesseln']

#: Wann die Adressen zuletzt von Hand aufgerufen wurden. Eine Erinnerung,
#: keine Messung - siehe den Hinweis oben.
STAND_ISO = '2026-10-02'

#: Schluessel -> Norm. ``name`` steht so im Fliesstext und im Schema.
QUELLEN = {
    'estg-35a': {
        'name': '§ 35a Einkommensteuergesetz',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/estg/__35a.html',
    },
    'bgb-546': {
        'name': '§ 546 Bürgerliches Gesetzbuch',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__546.html',
    },
    'bgb-1922': {
        'name': '§ 1922 Bürgerliches Gesetzbuch',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__1922.html',
    },
    'krwg-17': {
        'name': '§ 17 Kreislaufwirtschaftsgesetz',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/krwg/__17.html',
    },
    'krwg-53': {
        'name': '§ 53 Kreislaufwirtschaftsgesetz',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/krwg/__53.html',
    },
    'altholzv-1': {
        'name': '§ 1 Altholzverordnung (AltholzV)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/altholzv/__1.html',
        'abruf': '2026-10-01',
    },
    'altholzv-2': {
        'name': '§ 2 Altholzverordnung (AltholzV)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/altholzv/__2.html',
        'abruf': '2026-10-01',
    },
    'altholzv-3': {
        'name': '§ 3 Altholzverordnung (AltholzV)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/altholzv/__3.html',
        'abruf': '2026-10-01',
    },
    'altholzv-5': {
        'name': '§ 5 Altholzverordnung (AltholzV)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/altholzv/__5.html',
        'abruf': '2026-10-01',
    },
    'altholzv-10': {
        'name': '§ 10 Altholzverordnung (AltholzV)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/altholzv/__10.html',
        'abruf': '2026-10-01',
    },
    'altholzv-anhang-3': {
        'name': 'Anhang III Altholzverordnung (AltholzV)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/altholzv/anhang_iii.html',
        'abruf': '2026-10-01',
    },
    'uba-altholz': {
        'name': 'Altholz',
        'herausgeber': 'Umweltbundesamt',
        'url': 'https://www.umweltbundesamt.de/altholz',
        'abruf': '2026-10-01',
    },
    'leipzig-altholz': {
        'name': 'Merkblatt zum Umgang mit Altholz (Stand 04.2022)',
        'herausgeber': 'Stadt Leipzig, Amt für Umweltschutz',
        'url': 'https://www.leipzig.de/service-portal/formulare/formular/merkblatt-umgang-mit-altholz/download',
        'abruf': '2026-10-01',
    },
    'alttex-krwg-20': {
        'name': '§ 20 Kreislaufwirtschaftsgesetz (KrWG)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/krwg/__20.html',
        'abruf': '2026-10-01',
    },
    'alttex-halle': {
        'name': 'Hinweise zur Sammlung von Alttextilien (13.02.2025)',
        'herausgeber': 'Stadt Halle (Saale)',
        'url': 'https://halle.de/verwaltung-stadtrat/presseportal/nachrichten/nachricht/hinweise-zur-sammlung-von-alttextilien',
        'abruf': '2026-10-01',
    },
    'alttex-leipzig-container': {
        'name': 'Kleidercontainer und Sammlung von Alttextilien',
        'herausgeber': 'Stadt Leipzig',
        'url': 'https://www.leipzig.de/service-portal/themen-und-lebenslagen/abfall-und-sauberkeit/kleidercontainer',
        'abruf': '2026-10-01',
    },
    'alttex-dresden': {
        'name': 'Alttextilien – Abfalltrennung',
        'herausgeber': 'Landeshauptstadt Dresden',
        'url': 'https://www.dresden.de/de/stadtraum/umwelt/abfall-stadtreinigung/abfallberatung/trennung/Alttextilien.php',
        'abruf': '2026-10-01',
    },
    'alttex-aha': {
        'name': 'Altkleider',
        'herausgeber': 'aha Zweckverband Abfallwirtschaft Region Hannover',
        'url': 'https://www.aha-region.de/abfaelle-und-wertstoffe/altkleider',
        'abruf': '2026-10-01',
    },
    'asbest-uba': {
        'name': 'Asbest (Themenseite, Stand 30.07.2024)',
        'herausgeber': 'Umweltbundesamt',
        'url': 'https://www.umweltbundesamt.de/themen/gesundheit/umwelteinfluesse-auf-den-menschen/chemische-stoffe/asbest',
        'abruf': '2026-10-01',
    },
    'asbest-gefstoffv-11': {
        'name': '§ 11 Gefahrstoffverordnung',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/gefstoffv_2010/__11.html',
        'abruf': '2026-10-01',
    },
    'asbest-gefstoffv-11a': {
        'name': '§ 11a Gefahrstoffverordnung',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/gefstoffv_2010/__11a.html',
        'abruf': '2026-10-01',
    },
    'krwg-20': {
        'name': '§ 20 Kreislaufwirtschaftsgesetz',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/krwg/__20.html',
        'abruf': '2026-10-01',
    },
    'asbest-zaw': {
        'name': 'Abfallarten und Entgelte (Abfall-ABC)',
        'herausgeber': 'Zweckverband Abfallwirtschaft Westsachsen',
        'url': 'https://www.zaw-sachsen.de/entsorgung/abfall-abc/',
        'abruf': '2026-10-01',
    },
    'uba-ratgeber-haushalt': {
        'name': 'Ratgeber „Abfälle im Haushalt“ (Stand Dezember 2020)',
        'herausgeber': 'Umweltbundesamt',
        'url': 'https://www.umweltbundesamt.de/system/files/medien/1410/publikationen/2020_abfaelle_im_haushalt_bf.pdf',
        'abruf': '2026-10-01',
    },
    'battdg-gesamt': {
        'name': 'Batterierecht-Durchführungsgesetz (BattDG), Gesamtnorm',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/battdg/BJNR0E90B0025.html',
        'abruf': '2026-10-01',
    },
    'battdg-6': {
        'name': '§ 6 Batterierecht-Durchführungsgesetz (Pflichten des Endnutzers)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/battdg/__6.html',
        'abruf': '2026-10-01',
    },
    'battdg-14': {
        'name': '§ 14 Batterierecht-Durchführungsgesetz (Rücknahmepflichten der Händler)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/battdg/__14.html',
        'abruf': '2026-10-01',
    },
    'battdg-15': {
        'name': '§ 15 Batterierecht-Durchführungsgesetz (Annahmepflicht der öffentlich-rechtlichen Entsorgungsträger)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/battdg/__15.html',
        'abruf': '2026-10-01',
    },
    'battdg-18': {
        'name': '§ 18 Batterierecht-Durchführungsgesetz (Rücknahmepflichten der Händler)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/battdg/__18.html',
        'abruf': '2026-10-01',
    },
    'battdg-20': {
        'name': '§ 20 Batterierecht-Durchführungsgesetz (Mitwirkung von öffentlich-rechtlichen Entsorgungsträgern)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/battdg/__20.html',
        'abruf': '2026-10-01',
    },
    'uba-batterien-akkus': {
        'name': 'Batterien und Akkus richtig nutzen und fachgerecht entsorgen',
        'herausgeber': 'Umweltbundesamt',
        'url': 'https://www.umweltbundesamt.de/umwelttipps-fuer-den-alltag/batterien-akkus-richtig-nutzen-fachgerecht',
        'abruf': '2026-10-01',
    },
    'uba-lithium-akkus': {
        'name': 'Sicherer Umgang mit Lithium-Batterien und Akkus',
        'herausgeber': 'Umweltbundesamt',
        'url': 'https://www.umweltbundesamt.de/umwelttipps-fuer-den-alltag/sicherer-umgang-lithium-batterien-akkus',
        'abruf': '2026-10-01',
    },
    'daten-bsi-loeschen': {
        'name': 'Daten auf Festplatten, Datenträgern und Smartphones sicher löschen',
        'herausgeber': 'Bundesamt für Sicherheit in der Informationstechnik (BSI)',
        'url': 'https://www.bsi.bund.de/DE/Themen/Verbraucherinnen-und-Verbraucher/Informationen-und-Empfehlungen/Cyber-Sicherheitsempfehlungen/Daten-sichern-verschluesseln-und-loeschen/Daten-endgueltig-loeschen/daten-endgueltig-loeschen_node.html',
        'abruf': '2026-10-01',
    },
    'daten-elektrog-18': {
        'name': '§ 18 Elektro- und Elektronikgerätegesetz (ElektroG)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/elektrog_2015/__18.html',
        'abruf': '2026-10-01',
    },
    'elektrog-10': {
        'name': '§ 10 Elektro- und Elektronikgerätegesetz (Getrennte Erfassung)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/elektrog_2015/__10.html',
        'abruf': '2026-10-01',
    },
    'elektrog-13': {
        'name': '§ 13 Elektro- und Elektronikgerätegesetz (Sammlung durch die öffentlich-rechtlichen Entsorgungsträger)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/elektrog_2015/__13.html',
        'abruf': '2026-10-01',
    },
    'elektrog-14': {
        'name': '§ 14 Elektro- und Elektronikgerätegesetz (Bereitstellen der abzuholenden Altgeräte durch die öffentlich-rechtlichen Entsorgungsträger)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/elektrog_2015/__14.html',
        'abruf': '2026-10-01',
    },
    'elektrog-17': {
        'name': '§ 17 Elektro- und Elektronikgerätegesetz (Rücknahmepflicht der Vertreiber)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/elektrog_2015/__17.html',
        'abruf': '2026-10-01',
    },
    'uba-elektroaltgeraete': {
        'name': 'Wohin mit dem Elektroschrott? Alte Elektrogeräte richtig entsorgen',
        'herausgeber': 'Umweltbundesamt',
        'url': 'https://www.umweltbundesamt.de/umwelttipps-fuer-den-alltag/wohin-dem-elektroschrott-alte-elektrogeraete',
        'abruf': '2026-10-01',
    },
    'nachlass-bgb-1942': {
        'name': '§ 1942 BGB – Anfall und Ausschlagung der Erbschaft',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__1942.html',
        'abruf': '2026-10-01',
    },
    'nachlass-bgb-1943': {
        'name': '§ 1943 BGB – Annahme und Ausschlagung der Erbschaft',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__1943.html',
        'abruf': '2026-10-01',
    },
    'nachlass-bgb-1944': {
        'name': '§ 1944 BGB – Ausschlagungsfrist',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__1944.html',
        'abruf': '2026-10-01',
    },
    'nachlass-bgb-1945': {
        'name': '§ 1945 BGB – Form der Ausschlagung',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__1945.html',
        'abruf': '2026-10-01',
    },
    'nachlass-bgb-1953': {
        'name': '§ 1953 BGB – Wirkung der Ausschlagung',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__1953.html',
        'abruf': '2026-10-01',
    },
    'nachlass-bgb-1959': {
        'name': '§ 1959 BGB – Geschäftsführung vor der Ausschlagung',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__1959.html',
        'abruf': '2026-10-01',
    },
    'nachlass-bgb-1960': {
        'name': '§ 1960 BGB – Sicherung des Nachlasses; Nachlasspfleger',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__1960.html',
        'abruf': '2026-10-01',
    },
    'nachlass-justiz-nrw': {
        'name': 'Erbfall, Annahme und Ausschlagung der Erbschaft',
        'herausgeber': 'Justiz Nordrhein-Westfalen (justiz.nrw.de)',
        'url': 'https://www.justiz.nrw.de/BS/lebenslagen/familie/Nachlassverfahren/erbschein_ausschlagung',
        'abruf': '2026-10-01',
    },
    'gewabfv-1': {
        'name': '§ 1 Gewerbeabfallverordnung (GewAbfV)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/gewabfv_2017/__1.html',
        'abruf': '2026-10-01',
    },
    'gewabfv-2': {
        'name': '§ 2 Gewerbeabfallverordnung (GewAbfV)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/gewabfv_2017/__2.html',
        'abruf': '2026-10-01',
    },
    'gewabfv-3': {
        'name': '§ 3 Gewerbeabfallverordnung (GewAbfV)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/gewabfv_2017/__3.html',
        'abruf': '2026-10-01',
    },
    'gewabfv-4': {
        'name': '§ 4 Gewerbeabfallverordnung (GewAbfV)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/gewabfv_2017/__4.html',
        'abruf': '2026-10-01',
    },
    'gewabfv-5': {
        'name': '§ 5 Gewerbeabfallverordnung (GewAbfV)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/gewabfv_2017/__5.html',
        'abruf': '2026-10-01',
    },
    'gewabfv-8': {
        'name': '§ 8 Gewerbeabfallverordnung (GewAbfV)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/gewabfv_2017/__8.html',
        'abruf': '2026-10-01',
    },
    'krwg-3': {
        'name': '§ 3 Kreislaufwirtschaftsgesetz (KrWG)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/krwg/__3.html',
        'abruf': '2026-10-01',
    },
    'krwg-7': {
        'name': '§ 7 Kreislaufwirtschaftsgesetz (KrWG)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/krwg/__7.html',
        'abruf': '2026-10-01',
    },
    'schadstoff-uba-haushalt': {
        'name': 'Abfälle im Haushalt (Themenseite)',
        'herausgeber': 'Umweltbundesamt',
        'url': 'https://www.umweltbundesamt.de/themen/abfaelle-im-haushalt',
        'abruf': '2026-10-01',
    },
    'schadstoff-uba-toilette': {
        'name': 'Was darf nicht in die Toilette?',
        'herausgeber': 'Umweltbundesamt',
        'url': 'https://www.umweltbundesamt.de/themen/was-darf-nicht-in-die-toilette',
        'abruf': '2026-10-01',
    },
    'krwg-9': {
        'name': '§ 9 Kreislaufwirtschaftsgesetz',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/krwg/__9.html',
        'abruf': '2026-10-01',
    },
    'krwg-15': {
        'name': '§ 15 Kreislaufwirtschaftsgesetz',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/krwg/__15.html',
        'abruf': '2026-10-01',
    },
    'schadstoff-halle-abfallabc': {
        'name': 'Schadstoffhaltige Haushaltsabfälle und Altmedikamente',
        'herausgeber': 'Stadt Halle (Saale)',
        'url': 'https://halle.de/leben-in-halle/klimaschutz-und-umwelt/abfall-und-abwasser/abfall-abc/schadstoffhaltige-haushaltsabfaelle',
        'abruf': '2026-10-01',
    },
    'schadstoff-halle-mobil': {
        'name': 'Neuer Standort: Schadstoffmobil steht künftig auf dem Hallmarkt (Mitteilung vom 24.06.2024)',
        'herausgeber': 'Stadt Halle (Saale)',
        'url': 'https://halle.de/verwaltung-stadtrat/presseportal/nachrichten/nachricht/neuer-standort-schadstoffmobil-steht-kuenftig-auf-dem-hallmarkt',
        'abruf': '2026-10-01',
    },
    'nachlass-bgb-2259': {
        'name': '§ 2259 BGB – Ablieferungspflicht',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__2259.html',
        'abruf': '2026-10-01',
    },
    'nachlass-bgb-2300': {
        'name': '§ 2300 BGB – Erbvertrag: Ablieferung, Eröffnung',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__2300.html',
        'abruf': '2026-10-01',
    },
    'nachlass-famfg-343': {
        'name': '§ 343 FamFG – Örtliche Zuständigkeit',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/famfg/__343.html',
        'abruf': '2026-10-01',
    },
    'nachlass-famfg-344': {
        'name': '§ 344 FamFG – Besondere örtliche Zuständigkeit',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/famfg/__344.html',
        'abruf': '2026-10-01',
    },
    'nachlass-famfg-348': {
        'name': '§ 348 FamFG – Eröffnung von Verfügungen von Todes wegen',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/famfg/__348.html',
        'abruf': '2026-10-01',
    },
    'nachlass-bgb-2255': {
        'name': '§ 2255 BGB – Widerruf durch Vernichtung oder Veränderungen',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__2255.html',
        'abruf': '2026-10-01',
    },
    'nachlass-stgb-274': {
        'name': '§ 274 StGB – Urkundenunterdrückung',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/stgb/__274.html',
        'abruf': '2026-10-01',
    },
    'nachlass-ao-147': {
        'name': '§ 147 AO – Ordnungsvorschriften für die Aufbewahrung von Unterlagen',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/ao_1977/__147.html',
        'abruf': '2026-10-01',
    },
    'nachlass-hgb-257': {
        'name': '§ 257 HGB – Aufbewahrung von Unterlagen',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/hgb/__257.html',
        'abruf': '2026-10-01',
    },
    'nachlass-ustg-14b': {
        'name': '§ 14b UStG – Aufbewahrung von Rechnungen',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/ustg_1980/__14b.html',
        'abruf': '2026-10-01',
    },
    'nachlass-ustg-14': {
        'name': '§ 14 UStG – Ausstellung von Rechnungen',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/ustg_1980/__14.html',
        'abruf': '2026-10-01',
    },
    'nachlass-bgb-195': {
        'name': '§ 195 BGB – Regelmäßige Verjährungsfrist',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__195.html',
        'abruf': '2026-10-01',
    },
    'nachlass-bgb-199': {
        'name': '§ 199 BGB – Beginn der regelmäßigen Verjährungsfrist',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__199.html',
        'abruf': '2026-10-01',
    },
    'nachlass-bsi-con6': {
        'name': 'IT-Grundschutz-Kompendium, Baustein CON.6 Löschen und Vernichten (Edition 2023)',
        'herausgeber': 'Bundesamt für Sicherheit in der Informationstechnik',
        'url': 'https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Grundschutz/IT-GS-Kompendium_Einzel_PDFs_2023/03_CON_Konzepte_und_Vorgehensweisen/CON_6_Loeschen_und_Vernichten_Edition_2023.pdf?__blob=publicationFile&v=3',
        'abruf': '2026-10-01',
    },
    'nachlass-tlfdi-datentraeger': {
        'name': 'Orientierungshilfe Datenträgervernichtung entsprechend dem Schutzbedarf der Daten (Stand Juli 2017)',
        'herausgeber': 'Thüringer Landesbeauftragter für den Datenschutz und die Informationsfreiheit',
        'url': 'https://tlfdi.de/fileadmin/tlfdi/gesetze/orientierungshilfen/datentragervernichtung.pdf',
        'abruf': '2026-10-01',
    },
    'bgb-1833': {
        'name': '§ 1833 BGB – Aufgabe von Wohnraum des Betreuten',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__1833.html',
        'abruf': '2026-10-01',
    },
    'bgb-1814': {
        'name': '§ 1814 BGB – Voraussetzungen der Betreuung',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__1814.html',
        'abruf': '2026-10-01',
    },
    'bgb-1820': {
        'name': '§ 1820 BGB – Vorsorgevollmacht und Kontrollbetreuung',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__1820.html',
        'abruf': '2026-10-01',
    },
    'bgb-1821': {
        'name': '§ 1821 BGB – Pflichten des Betreuers; Wünsche des Betreuten',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__1821.html',
        'abruf': '2026-10-01',
    },
    'justiz-sachsen-betreuung': {
        'name': 'Betreuungsabteilung / Betreuungsgericht (Amtsgericht Leipzig)',
        'herausgeber': 'Sächsische Justiz',
        'url': 'https://www.justiz.sachsen.de/agl/informationen-zu-den-abteilungen-4007.html',
        'abruf': '2026-10-01',
    },
    'zpo-885': {
        'name': '§ 885 ZPO – Herausgabe von Grundstücken oder Schiffen',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/zpo/__885.html',
        'abruf': '2026-10-01',
    },
    'zpo-885a': {
        'name': '§ 885a ZPO – Beschränkter Vollstreckungsauftrag',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/zpo/__885a.html',
        'abruf': '2026-10-01',
    },
    'bgb-562-pfandrecht': {
        'name': '§ 562 BGB – Umfang des Vermieterpfandrechts',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__562.html',
        'abruf': '2026-10-01',
    },
    'justiz-nrw-herausgabe': {
        'name': 'Die Herausgabevollstreckung (Räumung und Kosten)',
        'herausgeber': 'Justiz Nordrhein-Westfalen',
        'url': 'https://www.justiz.nrw/BS/lebenslagen/zivilrecht/Zwangsvollstreckung/Herausgabevollstreckung',
        'abruf': '2026-10-01',
    },
    'chemnitz-asr-sperrabfall': {
        'name': 'Sperrabfall',
        'herausgeber': 'Abfallentsorgungs- und Stadtreinigungsbetrieb der Stadt Chemnitz (ASR)',
        'url': 'https://www.asr-chemnitz.de/leistungen/abfallentsorgung/sperrabfall',
        'abruf': '2026-10-01',
    },
    'chemnitz-asr-wertstoffhoefe': {
        'name': 'Wertstoffhöfe',
        'herausgeber': 'Abfallentsorgungs- und Stadtreinigungsbetrieb der Stadt Chemnitz (ASR)',
        'url': 'https://www.asr-chemnitz.de/leistungen/abfallentsorgung/wertstoffhoefe',
        'abruf': '2026-10-01',
    },
    'chemnitz-asr-faq': {
        'name': 'Häufige Fragen',
        'herausgeber': 'Abfallentsorgungs- und Stadtreinigungsbetrieb der Stadt Chemnitz (ASR)',
        'url': 'https://www.asr-chemnitz.de/haeufige-fragen/abfallentsorgung',
        'abruf': '2026-10-01',
    },
    'chemnitz-asr-spezielle-leistungen': {
        'name': 'Spezielle Leistungen',
        'herausgeber': 'Abfallentsorgungs- und Stadtreinigungsbetrieb der Stadt Chemnitz (ASR)',
        'url': 'https://www.asr-chemnitz.de/leistungen/abfallentsorgung/gebuehren/spezielle-leistungen',
        'abruf': '2026-10-01',
    },
    'chemnitz-asr-elektro': {
        'name': 'Elektro(nik)geräte',
        'herausgeber': 'Abfallentsorgungs- und Stadtreinigungsbetrieb der Stadt Chemnitz (ASR)',
        'url': 'https://www.asr-chemnitz.de/leistungen/abfallentsorgung/elektronikgeraete',
        'abruf': '2026-10-01',
    },
    'chemnitz-asr-problemabfall': {
        'name': 'Problemabfall',
        'herausgeber': 'Abfallentsorgungs- und Stadtreinigungsbetrieb der Stadt Chemnitz (ASR)',
        'url': 'https://www.asr-chemnitz.de/leistungen/abfallentsorgung/private-haushalte/problemabfall',
        'abruf': '2026-10-01',
    },
    'chemnitz-awvc-annahme': {
        'name': 'Wohin mit meinem Müll?',
        'herausgeber': 'Abfallwirtschaftsverband Chemnitz (AWVC)',
        'url': 'https://www.awvc.de/entsorgung/wohin-mit-meinem-muell/',
        'abruf': '2026-10-01',
    },
    'dresden-srd-sperrmuell': {
        'name': 'Stadtreinigung Dresden (SRD) – Ohne Abzocke: Sperrmüll von zu Hause entsorgen lassen',
        'herausgeber': 'Stadtreinigung Dresden GmbH',
        'url': 'https://www.srdresden.de/aktuelles/detail/ohne-abzocke-sperrmuell-von-zu-hause-entsorgen-lassen',
        'abruf': '2026-10-01',
    },
    'dresden-srd-haushalte': {
        'name': 'Stadtreinigung Dresden (SRD) – Private Haushalte',
        'herausgeber': 'Stadtreinigung Dresden GmbH',
        'url': 'https://www.srdresden.de/dienstleistungen/private-haushalte',
        'abruf': '2026-10-01',
    },
    'dresden-srd-hoefe': {
        'name': 'Stadtreinigung Dresden (SRD) – Wertstoffhöfe',
        'herausgeber': 'Stadtreinigung Dresden GmbH',
        'url': 'https://www.srdresden.de/ueber-uns/wertstoffhoefe/',
        'abruf': '2026-10-01',
    },
    'dresden-srd-az': {
        'name': 'Stadtreinigung Dresden (SRD) – A bis Z',
        'herausgeber': 'Stadtreinigung Dresden GmbH',
        'url': 'https://www.srdresden.de/dienstleistungen/a-bis-z',
        'abruf': '2026-10-01',
    },
    'sperrmuell-halle-abfallabc': {
        'name': 'Sperrmüll',
        'herausgeber': 'Stadt Halle (Saale)',
        'url': 'https://halle.de/leben-in-halle/klimaschutz-und-umwelt/abfall-und-abwasser/abfall-abc/sperrmuell',
        'abruf': '2026-10-01',
    },
    'sperrmuell-halle-hws': {
        'name': 'Sperrmüll',
        'herausgeber': 'Hallesche Wasser und Stadtwirtschaft GmbH (HWS)',
        'url': 'https://hws-halle.de/produkte-dienstleistungen/entsorgung/sperrmuell-elektrogeraete',
        'abruf': '2026-10-01',
    },
    'sperrmuell-halle-bestellung': {
        'name': 'Wir holen Ihren Sperrmüll für Sie ab',
        'herausgeber': 'Hallesche Wasser und Stadtwirtschaft GmbH (HWS)',
        'url': 'https://hws-halle.de/sperrmuellbestellen',
        'abruf': '2026-10-01',
    },
    'sperrmuell-halle-portal': {
        'name': 'Sperrmüll Entsorgung (Serviceportal)',
        'herausgeber': 'Stadt Halle (Saale)',
        'url': 'https://halle.de/serviceportal/dienstleistungen/leistung/sperrmuell-entsorgung/28742543',
        'abruf': '2026-10-01',
    },
    'sperrmuell-halle-portal-abfall': {
        'name': 'Abfall, Sperrmüll (Serviceportal)',
        'herausgeber': 'Stadt Halle (Saale)',
        'url': 'https://halle.de/serviceportal/dienstleistungen/leistung/abfall-sperrmuell/290721174',
        'abruf': '2026-10-01',
    },
    'sperrmuell-halle-abrufkarte': {
        'name': 'Sperrmüllentsorgung auf Abruf: Sperrmüllabrufkarte (Formular, Stand 2023)',
        'herausgeber': 'Hallesche Wasser und Stadtwirtschaft GmbH (HWS) und Stadt Halle (Saale)',
        'url': 'https://halle.de/fileadmin/Binaries/Umwelt/Allgemein_Umwelt/Abfallformulare/neu_2-67-0021_HWS-Sperrmuell_Sperrmuellabrufkarte_2023__20022023_.pdf',
        'abruf': '2026-10-01',
    },
    'sperrmuell-halle-markt': {
        'name': 'Standorte & Öffnungszeiten',
        'herausgeber': 'Hallesche Wasser und Stadtwirtschaft GmbH (HWS)',
        'url': 'https://hws-halle.de/produkte-dienstleistungen/wertstoffmarkt/standorte-oeffnungszeiten',
        'abruf': '2026-10-01',
    },
    'sperrmuell-halle-pressemeldung': {
        'name': 'Saubere Entsorgungssammelstellen: Wie man Sperrmüll, Elektrogeräte & Co. richtig entsorgt (19.06.2025)',
        'herausgeber': 'Stadt Halle (Saale)',
        'url': 'https://halle.de/verwaltung-stadtrat/presseportal/nachrichten/nachricht/saubere-entsorgungssammelstellen-wie-man-sperrmuell-elektrogeraete-co-richtig-entsorgt',
        'abruf': '2026-10-01',
    },
    'sperrmuell-halle-elektro': {
        'name': 'Elektro- und Elektronikaltgeräte (Abfall-ABC)',
        'herausgeber': 'Stadt Halle (Saale)',
        'url': 'https://halle.de/leben-in-halle/klimaschutz-und-umwelt/abfall-und-abwasser/abfall-abc/elektro-und-elektronikaltgeraete',
        'abruf': '2026-10-01',
    },
    'sperrmuell-halle-bau': {
        'name': 'Bau- und Abbruchabfälle (Abfall-ABC)',
        'herausgeber': 'Stadt Halle (Saale)',
        'url': 'https://halle.de/leben-in-halle/klimaschutz-und-umwelt/abfall-und-abwasser/abfall-abc/bau-und-abbruchabfaelle',
        'abruf': '2026-10-01',
    },
    'magdeburg-sperrmuell': {
        'name': 'Sperrmüllentsorgung',
        'herausgeber': 'Landeshauptstadt Magdeburg, Städtischer Abfallwirtschaftsbetrieb',
        'url': 'https://www.magdeburg.de/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Recycling-und-Entsorgung/Sperrm%C3%BCll/',
        'abruf': '2026-10-01',
    },
    'magdeburg-wertstoffhoefe': {
        'name': 'Wertstoffhöfe',
        'herausgeber': 'Landeshauptstadt Magdeburg, Städtischer Abfallwirtschaftsbetrieb',
        'url': 'https://www.magdeburg.de/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Recycling-und-Entsorgung/Wertstoffh%C3%B6fe/',
        'abruf': '2026-10-01',
    },
    'magdeburg-wertstoffhof-abgeben': {
        'name': 'Abfälle am Wertstoffhof abgeben',
        'herausgeber': 'Landeshauptstadt Magdeburg, Städtischer Abfallwirtschaftsbetrieb',
        'url': 'https://www.magdeburg.de/Start/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Recyclinghof.php?object=tx,37.14051.1&ModID=10&FID=37.549.1',
        'abruf': '2026-10-01',
    },
    'magdeburg-schadstoffe': {
        'name': 'Schadstoffsammlung',
        'herausgeber': 'Landeshauptstadt Magdeburg, Städtischer Abfallwirtschaftsbetrieb',
        'url': 'https://www.magdeburg.de/B%C3%BCrger-Stadt/Leben-in-Magdeburg/Umwelt/Abfall/Recycling-und-Entsorgung/Schadstoffmobil/',
        'abruf': '2026-10-01',
    },
    # 02.10.2026 (Ratgeber-Pruefung): Das Anwendungsschreiben selbst. Die Kopie
    # auf bundesfinanzministerium.de lieferte beim Abruf 404; diese Fassung
    # stellt das Finanzministerium Mecklenburg-Vorpommern bereit (Volltext mit
    # Anlage 1, dort "Haushaltsaufloesung" und "Sperrmuellabfuhr" in der Spalte
    # "nicht beguenstigt", gegen die Spaltenposition im PDF geprueft).
    'bmf-35a': {
        'name': 'BMF-Schreiben vom 09.11.2016 zu § 35a EStG (IV C 8 - S 2296-b/07/10003 :008)',
        'herausgeber': 'Bundesministerium der Finanzen, bereitgestellt vom Finanzministerium Mecklenburg-Vorpommern',
        'url': 'https://www.steuerportal-mv.de/static/Regierungsportal/Finanzministerium/Steuerportal/Dateien/Downloads/Anwendungsschreiben_zu_35a_EStG,_09.11.2016.pdf',
        'abruf': '2026-10-02',
    },
    'ddg-5': {
        'name': '§ 5 Digitale-Dienste-Gesetz',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/ddg/__5.html',
        'abruf': '2026-10-02',
    },
    'krwg-50': {
        'name': '§ 50 Kreislaufwirtschaftsgesetz',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/krwg/__50.html',
        'abruf': '2026-10-02',
    },
    'gefstoffv-5a': {
        'name': '§ 5a Gefahrstoffverordnung',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/gefstoffv_2010/__5a.html',
        'abruf': '2026-10-02',
    },
    'bgb-1858': {
        'name': '§ 1858 Bürgerliches Gesetzbuch',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__1858.html',
        'abruf': '2026-10-02',
    },
    'bgb-858': {
        'name': '§ 858 Bürgerliches Gesetzbuch',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__858.html',
        'abruf': '2026-10-02',
    },
    'dresden-stadt-sperrmuell': {
        'name': 'Sperrmüll',
        'herausgeber': 'Landeshauptstadt Dresden',
        'url': 'https://www.dresden.de/de/stadtraum/umwelt/abfall-stadtreinigung/entsorgung/cr/sperrmuell.php',
        'abruf': '2026-10-02',
    },
    # ── Leistungsseiten (02.10.2026, Zweig fix/2026-10-02-leistungen) ──────
    # Die Verwaltungsauffassung zu § 35a EStG. Das Gesetz selbst nennt keine
    # Beispiele; welche Leistung die Finanzaemter anerkennen, steht im
    # Anwendungsschreiben des BMF. Die Anlage 1 fuehrt die Haushaltsaufloesung
    # in der Spalte "nicht beguenstigt" (Fassung nach der Aenderung vom
    # 01.09.2021, die nur Strassenreinigung und Winterdienst neu fasst).
    # bundesfinanzministerium.de liefert das Schreiben nicht mehr unter einer
    # stabilen Adresse aus; die Abdrucke der Landesfinanzverwaltungen sind
    # amtlich und wurden am 02.10.2026 gelesen.
    'bmf-35a-anlage1': {
        'name': 'Anlage 1 zum BMF-Schreiben zu § 35a EStG: Beispielhafte '
                'Aufzählung begünstigter und nicht begünstigter haushaltsnaher '
                'Dienstleistungen und Handwerkerleistungen',
        'herausgeber': 'Bundesministerium der Finanzen, bereitgestellt von der '
                       'Thüringer Steuerverwaltung',
        'url': 'https://finanzamt.thueringen.de/fileadmin/user_upload/Anlage_1_BMF-Schreiben___35a_EStG_1.docx.pdf',
        'abruf': '2026-10-02',
    },
    'bmf-35a-2016': {
        'name': 'BMF-Schreiben vom 9. November 2016 zu § 35a EStG '
                '(Rdnr. 3: Umzug, Rdnr. 39: Arbeits- und Fahrtkosten)',
        'herausgeber': 'Bundesministerium der Finanzen, bereitgestellt vom '
                       'Finanzministerium Mecklenburg-Vorpommern',
        'url': 'https://www.steuerportal-mv.de/static/Regierungsportal/Finanzministerium/Steuerportal/Dateien/Downloads/Anwendungsschreiben_zu_35a_EStG,_09.11.2016.pdf',
        'abruf': '2026-10-02',
    },
    'bgb-564': {
        'name': '§ 564 BGB – Fortsetzung des Mietverhältnisses mit dem Erben; '
                'außerordentliche Kündigung',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__564.html',
        'abruf': '2026-10-02',
    },
    'bgb-2040': {
        'name': '§ 2040 BGB – Verfügung über Nachlassgegenstände',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/bgb/__2040.html',
        'abruf': '2026-10-02',
    },
    # ── Halteverbot (02.10.2026, Zweig fix/2026-10-02-halteverbot) ─────────
    # Die Behoerdenseiten der vier Staedte zum Halteverbot bei Umzug und
    # Be-/Entladen, am 02.10.2026 im Volltext gelesen. Halle nennt auf
    # derselben Seite zwei Antragsfristen (sieben Werktage / 14 Tage) - der
    # Artikel nennt beide. Leipzig: Seite und Antragsformular (Stand 09.2024)
    # getrennt, weil nur das Formular die Eingangsfrist und den Inhalt des
    # Verkehrszeichenplans nennt.
    'halteverbot-halle': {
        'name': 'Straßensperrung wegen Umzug beantragen (Serviceportal)',
        'herausgeber': 'Stadt Halle (Saale)',
        'url': 'https://halle.de/serviceportal/dienstleistungen/leistung/strassensperrung-wegen-umzug-beantragen/391549757',
        'abruf': '2026-10-02',
    },
    'halteverbot-magdeburg': {
        'name': 'Umzug - Aufstellen von Verkehrszeichen für Möbelumzug',
        'herausgeber': 'Landeshauptstadt Magdeburg, Straßenverkehrsbehörde',
        'url': 'https://www.magdeburg.de/index.php?object=tx,698.8844&ModID=10&FID=37.809.1',
        'abruf': '2026-10-02',
    },
    'halteverbot-dresden': {
        'name': 'Umzug (Möbeltransport)',
        'herausgeber': 'Landeshauptstadt Dresden, Straßen- und Tiefbauamt',
        'url': 'https://www.dresden.de/de/rathaus/dienstleistungen/umzug-moebeltransport.php',
        'abruf': '2026-10-02',
    },
    'halteverbot-leipzig': {
        'name': 'Genehmigung für das Stellen von Haltverboten bei (Möbel-)Umzug',
        'herausgeber': 'Stadt Leipzig',
        'url': 'https://www.leipzig.de/service-portal/dienstleistung/antrag-fuer-eine-haltverbotszone-bei-umzug-598ad33d5cc1a',
        'abruf': '2026-10-02',
    },
    'halteverbot-leipzig-formular': {
        'name': 'Antrag auf Anordnung einer Haltverbotszone für einen '
                'Möbelumzug mit Informationsblatt (Formular, Stand 09.2024)',
        'herausgeber': 'Stadt Leipzig, Mobilitäts- und Tiefbauamt',
        'url': 'https://www.leipzig.de/buergerservice-und-verwaltung/aemter-und-behoerdengaenge/formulare/formular/antrag-haltverbotszone-umzug/download',
        'abruf': '2026-10-02',
    },
    'stvo-45': {
        'name': '§ 45 Straßenverkehrs-Ordnung',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/stvo_2013/__45.html',
        'abruf': '2026-10-02',
    },
    'stvo-anlage-2': {
        'name': 'Anlage 2 zur Straßenverkehrs-Ordnung (Zeichen 283 und 286)',
        'herausgeber': 'Bundesministerium der Justiz',
        'url': 'https://www.gesetze-im-internet.de/stvo_2013/anlage_2.html',
        'abruf': '2026-10-02',
    },
}


def kurzadresse(url):
    """``https://www.gesetze-im-internet.de/…`` -> ``gesetze-im-internet.de/…``.

    Im Fliesstext steht die kurze Form: Sie ist lesbar und laesst sich
    abtippen. Die vollstaendige Adresse steht im ``citation``-Eintrag.
    """
    return url.removeprefix('https://').removeprefix('http://').removeprefix('www.')


def _abruf_text(quelle):
    """``', abgerufen am 01.10.2026'`` - oder leer, wenn die Quelle kein Datum traegt.

    Seit dem 01.10.2026 tragen die Quellen der Wissensseiten das Datum, an dem sie
    zuletzt von Hand gelesen wurden (``abruf``, ISO). Bei Normen auf
    gesetze-im-internet.de ist das die einzige Fassungsangabe, die die Seite
    hergibt: Sie nennt kein Datum je Norm. Die aelteren Eintraege haben kein
    Feld und bleiben unveraendert.
    """
    abruf = quelle.get('abruf')
    if not abruf:
        return ''
    jahr, monat, tag = abruf.split('-')
    return f', abgerufen am {tag}.{monat}.{jahr}'


def satz_text(bezug, quelle):
    """Der Beleg als reiner Text - ohne jedes HTML (siehe oben).

    ``bezug`` sagt, **was** die Norm traegt. Ohne ihn stuende am Absatzende
    eine Adresse ohne Aussage, und der Leser muesste raten, wofuer sie da ist.
    """
    return (f"{bezug}. Quelle: {quelle['name']}, {quelle['herausgeber']} "
            f"({kurzadresse(quelle['url'])}{_abruf_text(quelle)}).")


def satz(bezug, quelle):
    """Der sichtbare Beleg als HTML-Satz: der Name der Norm ist der Link.

    Gedacht fuer Absaetze, die mit ``|safe`` ausgegeben werden - alle Werte
    sind deshalb maskiert. ``rel="noopener"``: die Adresse ist fremd. Der
    sichtbare Text ist derselbe wie in :func:`satz_text`, die Kurzadresse
    bleibt zum Abtippen stehen.
    """
    link = (f'<a href="{_escape(quelle["url"], quote=True)}" rel="noopener">'
            f"{_escape(quelle['name'])}</a>")
    return (f"{_escape(bezug)}. Quelle: {link}, {_escape(quelle['herausgeber'])} "
            f"({_escape(kurzadresse(quelle['url']))}{_abruf_text(quelle)}).")


def aus_schluesseln(schluessel):
    """Mehrere Schluessel zu Quellen - fuer die Uebersichtsseite."""
    return [QUELLEN[s] for s in schluessel]


def einsetzen(daten):
    """Den Beleg an den letzten Absatz seines Abschnitts haengen.

    Erwartet in ``daten`` den Schluessel ``quellen`` - je Eintrag ein
    ``schluessel`` aus :data:`QUELLEN`, die ``abschnitt``-Kennung und den
    ``bezug``. Der Eintrag wird verbraucht; zurueck kommen die Quellen selbst,
    aus denen das Schema seinen ``citation``-Eintrag baut.

    **Angehaengt und nicht als eigener Absatz gefuehrt**: Ein neues ``<p>``
    waere ein neues Element, und daran haengt die Designwache. Darum muss der
    Abschnitt mindestens einen Absatz haben - eine Checkliste aus reinen
    ``schritte`` bekaeme sonst einen Absatz, den es vorher nicht gab.

    Ein Eintrag, dessen Abschnitt es nicht gibt, landet **nirgends**. Das
    faellt keinem Leser auf; dagegen steht ``test_ratgeber.py``, das jeden
    Beleg im ausgelieferten HTML wiederfindet.
    """
    gefunden = []
    for eintrag in daten.pop('quellen', None) or []:
        quelle = QUELLEN[eintrag['schluessel']]
        gefunden.append(quelle)
        text = satz(eintrag['bezug'], quelle)
        for abschnitt in daten.get('abschnitte') or []:
            if abschnitt.get('id') == eintrag['abschnitt'] and abschnitt.get('absaetze'):
                abschnitt['absaetze'][-1] += ' ' + text
                break
    return gefunden
