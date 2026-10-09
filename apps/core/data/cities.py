"""Staedte-Stammdaten der programmatischen lokalen SEO.

Aus ``views.py`` herausgeloest (F6). Reines Verschieben, kein Verhalten geaendert.
Importiert absichtlich nichts aus ``apps.core`` - dieses Paket muss von
``context_processors`` wie von ``views`` aus erreichbar bleiben, ohne Zirkel.
"""

# 'randgebiet': True kennzeichnet Staedte, die nur bei groesseren Auftraegen
# angefahren werden (Raum Hannover, mit Oliver am 13.08.2026 geklaert). Diese
# Seiten duerfen KEINE kurze Reaktionszeit versprechen - sonst erzeugen sie
# Anfragen, die abgesagt werden muessen. city.html wertet das Flag aus.
_CITY_DATA = {
    # ── Sachsen (Leipzig/Halle Hauptstandort) ──────────────────────────────
    'leipzig': {
        'name': 'Leipzig', 'state': 'Sachsen', 'region': 'Region Leipzig',
        'standort': 'Leipzig & Halle', 'branch': 'Leipzig',
        'nearby': ['Halle (Saale)', 'Schkeuditz', 'Borna', 'Delitzsch', 'Taucha', 'Markkleeberg', 'Markranstädt', 'Zwenkau', 'Wurzen'],
        'zip': '04109', 'lat': 51.3397, 'lng': 12.3731,
        'intro_hook': 'Im Herzen Sachsens – von Gohlis bis Connewitz, von Grünau bis Reudnitz',
        'response': '2–4 Stunden',
    },
    'halle': {
        'name': 'Halle (Saale)', 'state': 'Sachsen-Anhalt', 'region': 'Mitteldeutschland',
        'standort': 'Leipzig & Halle', 'branch': 'Halle',
        'nearby': ['Leipzig', 'Merseburg', 'Schkeuditz', 'Bitterfeld-Wolfen', 'Weißenfels', 'Bad Dürrenberg', 'Querfurt'],
        'zip': '06108', 'lat': 51.4825, 'lng': 11.9706,
        'intro_hook': 'In der Saalestadt – von der Altstadt bis Neustadt, Silberhöhe bis Südstadt',
        'response': '2–4 Stunden',
    },
    'schkeuditz': {
        'name': 'Schkeuditz', 'state': 'Sachsen', 'region': 'Nordsachsen',
        'standort': 'Leipzig & Halle', 'branch': 'Leipzig',
        'nearby': ['Leipzig', 'Halle (Saale)', 'Merseburg', 'Delitzsch', 'Markranstädt'],
        'zip': '04435', 'lat': 51.3984, 'lng': 12.2209,
        'intro_hook': 'Direkt am Flughafen Leipzig/Halle',
        'response': '2–3 Stunden',
    },
    'markranstaedt': {
        'name': 'Markranstädt', 'state': 'Sachsen', 'region': 'Landkreis Leipzig',
        'standort': 'Leipzig & Halle', 'branch': 'Leipzig',
        'nearby': ['Leipzig', 'Merseburg', 'Schkeuditz', 'Bad Dürrenberg'],
        'zip': '04420', 'lat': 51.2984, 'lng': 12.2209,
        'intro_hook': 'Im Neuseenland westlich von Leipzig – Ihr regionaler Profi',
        'response': '1 Werktag',
    },
    'borna': {
        'name': 'Borna', 'state': 'Sachsen', 'region': 'Südraum Leipzig',
        'standort': 'Leipzig & Halle', 'branch': 'Leipzig',
        'nearby': ['Leipzig', 'Grimma', 'Geithain', 'Altenburg', 'Markkleeberg'],
        'zip': '04552', 'lat': 51.1264, 'lng': 12.4969,
        'intro_hook': 'Im Südraum Leipzig – für das Kohlerevier und das Neuseenland',
        'response': '1 Werktag',
    },
    'delitzsch': {
        'name': 'Delitzsch', 'state': 'Sachsen', 'region': 'Nordsachsen',
        'standort': 'Leipzig & Halle', 'branch': 'Leipzig',
        'nearby': ['Leipzig', 'Eilenburg', 'Bitterfeld-Wolfen', 'Schkeuditz', 'Taucha'],
        'zip': '04509', 'lat': 51.5269, 'lng': 12.3422,
        'intro_hook': 'Im Nordsächsischen zwischen Leipzig und Bitterfeld',
        'response': '1 Werktag',
    },
    'merseburg': {
        'name': 'Merseburg', 'state': 'Sachsen-Anhalt', 'region': 'Saalekreis',
        'standort': 'Leipzig & Halle', 'branch': 'Halle',
        'nearby': ['Halle (Saale)', 'Leipzig', 'Bad Dürrenberg', 'Weißenfels', 'Schkeuditz', 'Querfurt'],
        'zip': '06217', 'lat': 51.3536, 'lng': 11.9919,
        'intro_hook': 'An der Saale im Chemiedreieck',
        'response': '1 Werktag',
    },
    'querfurt': {
        'name': 'Querfurt', 'state': 'Sachsen-Anhalt', 'region': 'Saalekreis',
        'standort': 'Leipzig & Halle', 'branch': 'Halle',
        'nearby': ['Merseburg', 'Halle (Saale)', 'Sangerhausen', 'Weißenfels', 'Naumburg (Saale)'],
        'zip': '06268', 'lat': 51.3833, 'lng': 11.6000,
        'intro_hook': 'Im Westen des Saalekreises – zwischen Burg Querfurt und der Querfurter Platte',
        'response': '1 Werktag',
    },
    'weissenfels': {
        'name': 'Weißenfels', 'state': 'Sachsen-Anhalt', 'region': 'Burgenlandkreis',
        'standort': 'Leipzig & Halle', 'branch': 'Halle',
        'nearby': ['Halle (Saale)', 'Merseburg', 'Naumburg (Saale)', 'Zeitz', 'Bad Dürrenberg', 'Querfurt'],
        'zip': '06667', 'lat': 51.2019, 'lng': 11.9689,
        'intro_hook': 'Im Burgenlandkreis zwischen Saale und Unstrut',
        'response': '1 Werktag',
    },
    'zeitz': {
        'name': 'Zeitz', 'state': 'Sachsen-Anhalt', 'region': 'Burgenlandkreis',
        'standort': 'Leipzig & Halle', 'branch': 'Halle',
        'nearby': ['Halle (Saale)', 'Weißenfels', 'Naumburg (Saale)', 'Leipzig', 'Merseburg'],
        'zip': '06712', 'lat': 51.0483, 'lng': 12.1378,
        'intro_hook': 'Im Burgenlandkreis südlich von Halle – für Zeitz und das Elster-Saale-Land',
        'response': '1 Werktag',
    },
    'naumburg': {
        'name': 'Naumburg (Saale)', 'state': 'Sachsen-Anhalt', 'region': 'Burgenlandkreis',
        'standort': 'Leipzig & Halle', 'branch': 'Halle',
        'nearby': ['Weißenfels', 'Merseburg', 'Halle (Saale)', 'Zeitz', 'Apolda'],
        'zip': '06618', 'lat': 51.1539, 'lng': 11.8097,
        'intro_hook': 'Domstadt an der Saale – zum Festpreis',
        'response': '1 Werktag',
    },
    'taucha': {
        'name': 'Taucha', 'state': 'Sachsen', 'region': 'Nordsachsen',
        'standort': 'Leipzig & Halle', 'branch': 'Leipzig',
        'nearby': ['Leipzig', 'Eilenburg', 'Wurzen', 'Schkeuditz', 'Delitzsch'],
        'zip': '04425', 'lat': 51.3786, 'lng': 12.4947,
        'intro_hook': 'Direkt an der Stadtgrenze Leipzig',
        'response': '1–2 Stunden',
    },
    'eilenburg': {
        'name': 'Eilenburg', 'state': 'Sachsen', 'region': 'Nordsachsen',
        'standort': 'Leipzig & Halle', 'branch': 'Leipzig',
        'nearby': ['Leipzig', 'Delitzsch', 'Taucha', 'Torgau', 'Wurzen', 'Bitterfeld-Wolfen'],
        'zip': '04838', 'lat': 51.4619, 'lng': 12.6303,
        'intro_hook': 'An der Mulde im Nordsächsischen',
        'response': '1 Werktag',
    },
    'torgau': {
        'name': 'Torgau', 'state': 'Sachsen', 'region': 'Nordsachsen',
        'standort': 'Leipzig & Halle', 'branch': 'Leipzig',
        'nearby': ['Leipzig', 'Eilenburg', 'Riesa', 'Delitzsch', 'Oschatz'],
        'zip': '04860', 'lat': 51.5625, 'lng': 13.0022,
        'intro_hook': 'Historische Elbestadt im Nordsächsischen – zwischen Leipzig und Dresden',
        'response': '1 Werktag',
    },
    'grimma': {
        'name': 'Grimma', 'state': 'Sachsen', 'region': 'Landkreis Leipzig',
        'standort': 'Leipzig & Halle', 'branch': 'Leipzig',
        'nearby': ['Leipzig', 'Borna', 'Wurzen', 'Colditz', 'Trebsen'],
        'zip': '04668', 'lat': 51.2367, 'lng': 12.7167,
        'intro_hook': 'Muldestadt im Landkreis Leipzig',
        'response': '1 Werktag',
    },
    # ── Leipziger Umland, seit 24.09.2026 (Search Console: fuer Markkleeberg,
    # Wurzen und Zwenkau gab es Suchanfragen, aber keine Seite). Koordinaten
    # und PLZ aus den Wikipedia-Infoboxen; 'response' wie die uebrigen Orte
    # im Landkreis Leipzig (Borna, Grimma, Markranstaedt) - vom Betrieb noch
    # zu bestaetigen. Ortsangaben in city_lokal.py.
    'markkleeberg': {
        'name': 'Markkleeberg', 'state': 'Sachsen', 'region': 'Landkreis Leipzig',
        'standort': 'Leipzig & Halle', 'branch': 'Leipzig',
        'nearby': ['Leipzig', 'Zwenkau', 'Markranstädt', 'Borna'],
        'zip': '04416', 'lat': 51.2803, 'lng': 12.3767,
        'intro_hook': 'Direkt südlich von Leipzig – zwischen Cospudener und Markkleeberger See',
        'response': '1 Werktag',
    },
    'wurzen': {
        'name': 'Wurzen', 'state': 'Sachsen', 'region': 'Landkreis Leipzig',
        'standort': 'Leipzig & Halle', 'branch': 'Leipzig',
        'nearby': ['Leipzig', 'Grimma', 'Eilenburg', 'Taucha', 'Oschatz'],
        'zip': '04808', 'lat': 51.3667, 'lng': 12.7333,
        'intro_hook': 'Die Domstadt an der Mulde, rund 30 km östlich von Leipzig',
        'response': '1 Werktag',
    },
    'zwenkau': {
        'name': 'Zwenkau', 'state': 'Sachsen', 'region': 'Landkreis Leipzig',
        'standort': 'Leipzig & Halle', 'branch': 'Leipzig',
        'nearby': ['Leipzig', 'Markkleeberg', 'Markranstädt', 'Borna'],
        'zip': '04442', 'lat': 51.2175, 'lng': 12.3242,
        'intro_hook': 'Am Zwenkauer See im Leipziger Neuseenland',
        'response': '1 Werktag',
    },
    'bitterfeld': {
        'name': 'Bitterfeld-Wolfen', 'state': 'Sachsen-Anhalt', 'region': 'Anhalt-Bitterfeld',
        'standort': 'Leipzig & Halle', 'branch': 'Halle',
        'nearby': ['Halle (Saale)', 'Leipzig', 'Dessau-Roßlau', 'Delitzsch', 'Köthen'],
        'zip': '06749', 'lat': 51.6239, 'lng': 12.3219,
        'intro_hook': 'Im Chemiedelta zwischen Halle und Leipzig',
        'response': '1 Werktag',
    },
    # ── Sachsen-Anhalt (Magdeburg) ─────────────────────────────────────────
    'magdeburg': {
        'name': 'Magdeburg', 'state': 'Sachsen-Anhalt', 'region': 'Mitteldeutschland',
        'standort': 'Magdeburg', 'branch': 'Magdeburg',
        'nearby': ['Wolmirstedt', 'Schönebeck (Elbe)', 'Haldensleben', 'Stendal', 'Burg (bei Magdeburg)'],
        'zip': '39104', 'lat': 52.1205, 'lng': 11.6276,
        'intro_hook': 'In der Elbestadt – Sachsen-Anhalts Landeshauptstadt professionell entrümpelt',
        'response': '1 Werktag',
    },
    'halberstadt': {
        'name': 'Halberstadt', 'state': 'Sachsen-Anhalt', 'region': 'Harzregion',
        'standort': 'Magdeburg', 'branch': 'Magdeburg',
        'nearby': ['Magdeburg', 'Wernigerode', 'Quedlinburg', 'Oschersleben', 'Blankenburg'],
        'zip': '38820', 'lat': 51.8961, 'lng': 11.0519,
        'intro_hook': 'Am Harzrand – für den Landkreis Harz und Umgebung',
        'response': '1 Werktag',
    },
    'stendal': {
        'name': 'Stendal', 'state': 'Sachsen-Anhalt', 'region': 'Altmark',
        'standort': 'Magdeburg', 'branch': 'Magdeburg',
        'nearby': ['Magdeburg', 'Havelberg', 'Tangermünde', 'Genthin', 'Gardelegen'],
        'zip': '39576', 'lat': 52.6058, 'lng': 11.8589,
        'intro_hook': 'In der Altmark – Ihr verlässlicher Entrümpelungsdienst',
        'response': '1–2 Werktage',
    },
    'dessau': {
        'name': 'Dessau-Roßlau', 'state': 'Sachsen-Anhalt', 'region': 'Mitteldeutschland',
        'standort': 'Magdeburg', 'branch': 'Magdeburg',
        'nearby': ['Magdeburg', 'Halle (Saale)', 'Bitterfeld-Wolfen', 'Köthen (Anhalt)', 'Lutherstadt Wittenberg', 'Zerbst'],
        'zip': '06844', 'lat': 51.8333, 'lng': 12.2364,
        'intro_hook': 'Bauhaus-Stadt an Elbe und Mulde',
        'response': '1 Werktag',
    },
    'lutherstadt-wittenberg': {
        'name': 'Lutherstadt Wittenberg', 'state': 'Sachsen-Anhalt', 'region': 'Wittenberg',
        'standort': 'Magdeburg', 'branch': 'Magdeburg',
        'nearby': ['Dessau-Roßlau', 'Halle (Saale)', 'Bitterfeld-Wolfen', 'Jessen', 'Kemberg'],
        'zip': '06886', 'lat': 51.8667, 'lng': 12.6333,
        'intro_hook': 'Lutherstadt an der Elbe – Welterbe-Stadt professionell entrümpelt',
        'response': '1 Werktag',
    },
    'koethen': {
        'name': 'Köthen (Anhalt)', 'state': 'Sachsen-Anhalt', 'region': 'Anhalt-Bitterfeld',
        'standort': 'Leipzig & Halle', 'branch': 'Halle',
        'nearby': ['Halle (Saale)', 'Dessau-Roßlau', 'Bitterfeld-Wolfen', 'Bernburg (Saale)', 'Aschersleben'],
        'zip': '06366', 'lat': 51.7520, 'lng': 11.9722,
        'intro_hook': 'Im Herzen von Anhalt – zwischen Saale und Elbe',
        'response': '1 Werktag',
    },
    'wernigerode': {
        'name': 'Wernigerode', 'state': 'Sachsen-Anhalt', 'region': 'Harzregion',
        'standort': 'Magdeburg', 'branch': 'Magdeburg',
        'nearby': ['Halberstadt', 'Quedlinburg', 'Thale', 'Blankenburg (Harz)'],
        'zip': '38855', 'lat': 51.8333, 'lng': 10.7833,
        'intro_hook': 'Bunte Stadt im Harz – Ihr Entrümpelungspartner',
        'response': '1–2 Werktage',
    },
    'quedlinburg': {
        'name': 'Quedlinburg', 'state': 'Sachsen-Anhalt', 'region': 'Harzregion',
        'standort': 'Magdeburg', 'branch': 'Magdeburg',
        'nearby': ['Halberstadt', 'Wernigerode', 'Aschersleben', 'Sangerhausen', 'Thale'],
        'zip': '06484', 'lat': 51.7897, 'lng': 11.1456,
        'intro_hook': 'UNESCO-Welterbe-Stadt am Harz – behutsam und professionell',
        'response': '1–2 Werktage',
    },
    'bernburg': {
        'name': 'Bernburg (Saale)', 'state': 'Sachsen-Anhalt', 'region': 'Salzlandkreis',
        'standort': 'Magdeburg', 'branch': 'Magdeburg',
        'nearby': ['Halle (Saale)', 'Magdeburg', 'Aschersleben', 'Köthen (Anhalt)'],
        'zip': '06406', 'lat': 51.7989, 'lng': 11.7356,
        'intro_hook': 'Im Salzlandkreis zwischen Saale und Bode',
        'response': '1 Werktag',
    },
    'sangerhausen': {
        'name': 'Sangerhausen', 'state': 'Sachsen-Anhalt', 'region': 'Mansfeld-Südharz',
        'standort': 'Magdeburg', 'branch': 'Halle',
        'nearby': ['Halle (Saale)', 'Eisleben', 'Nordhausen', 'Merseburg', 'Querfurt'],
        'zip': '06526', 'lat': 51.4722, 'lng': 11.2983,
        'intro_hook': 'Rosarium-Stadt im Mansfeld-Südharz – professionell entrümpelt',
        'response': '1 Werktag',
    },
    'aschersleben': {
        'name': 'Aschersleben', 'state': 'Sachsen-Anhalt', 'region': 'Salzlandkreis',
        'standort': 'Magdeburg', 'branch': 'Magdeburg',
        'nearby': ['Halberstadt', 'Magdeburg', 'Bernburg (Saale)', 'Quedlinburg', 'Sangerhausen'],
        'zip': '06449', 'lat': 51.7556, 'lng': 11.4722,
        'intro_hook': 'Älteste Stadt Sachsen-Anhalts – zuverlässige Entrümpelung',
        'response': '1 Werktag',
    },
    # ── Niedersachsen (Hannover) ───────────────────────────────────────────
    'hannover': {
        'name': 'Hannover', 'state': 'Niedersachsen', 'region': 'Region Hannover',
        'standort': 'Hannover', 'branch': 'Hannover',
        'nearby': ['Langenhagen', 'Garbsen', 'Lehrte', 'Peine', 'Burgdorf', 'Ronnenberg', 'Sehnde'],
        'zip': '30159', 'lat': 52.3759, 'lng': 9.7320,
        'intro_hook': 'Niedersachsens Landeshauptstadt – von List bis Linden, von Vahrenwald bis Döhren',
        'randgebiet': True, 'response': '1 Werktag',
    },
    'braunschweig': {
        'name': 'Braunschweig', 'state': 'Niedersachsen', 'region': 'Braunschweiger Land',
        'standort': 'Hannover', 'branch': 'Hannover',
        'nearby': ['Wolfsburg', 'Salzgitter', 'Peine', 'Hildesheim', 'Gifhorn'],
        'zip': '38100', 'lat': 52.2689, 'lng': 10.5268,
        'intro_hook': 'Löwenstadt Braunschweig – von der Weststadt bis zum Östlichen Ringgebiet',
        'randgebiet': True, 'response': '1 Werktag',
    },
    'celle': {
        'name': 'Celle', 'state': 'Niedersachsen', 'region': 'Hannover Umland',
        'standort': 'Hannover', 'branch': 'Hannover',
        'nearby': ['Hannover', 'Uelzen', 'Gifhorn', 'Peine', 'Burgdorf'],
        'zip': '29221', 'lat': 52.6258, 'lng': 10.0826,
        'intro_hook': 'Fachwerkstadt an der Aller – zuverlässig im Celler Land',
        'randgebiet': True, 'response': '1 Werktag',
    },
    'hameln': {
        'name': 'Hameln', 'state': 'Niedersachsen', 'region': 'Weserbergland',
        'standort': 'Hannover', 'branch': 'Hannover',
        'nearby': ['Hannover', 'Hildesheim', 'Bad Pyrmont', 'Springe', 'Bad Münder'],
        'zip': '31785', 'lat': 52.1038, 'lng': 9.3608,
        'intro_hook': 'Rattenfänger-Stadt – professionelle Entrümpelung im Weserbergland',
        'randgebiet': True, 'response': '1 Werktag',
    },
    'salzgitter': {
        'name': 'Salzgitter', 'state': 'Niedersachsen', 'region': 'Braunschweiger Land',
        'standort': 'Hannover', 'branch': 'Hannover',
        'nearby': ['Braunschweig', 'Hildesheim', 'Wolfenbüttel', 'Goslar'],
        'zip': '38226', 'lat': 52.1547, 'lng': 10.3669,
        'intro_hook': 'Im Städtedreieck Braunschweig–Hildesheim–Goslar',
        'randgebiet': True, 'response': '1 Werktag',
    },
    'langenhagen': {
        'name': 'Langenhagen', 'state': 'Niedersachsen', 'region': 'Region Hannover',
        'standort': 'Hannover', 'branch': 'Hannover',
        'nearby': ['Hannover', 'Garbsen', 'Wedemark', 'Burgwedel', 'Isernhagen'],
        'zip': '30851', 'lat': 52.4467, 'lng': 9.7361,
        'intro_hook': 'Nördlich von Hannover – direkt am Flughafen Hannover',
        'randgebiet': True, 'response': '1 Werktag',
    },
    'garbsen': {
        'name': 'Garbsen', 'state': 'Niedersachsen', 'region': 'Region Hannover',
        'standort': 'Hannover', 'branch': 'Hannover',
        'nearby': ['Hannover', 'Neustadt am Rübenberge', 'Wunstorf', 'Seelze'],
        'zip': '30823', 'lat': 52.4258, 'lng': 9.5997,
        'intro_hook': 'Westlich von Hannover – in der Region Hannover',
        'randgebiet': True, 'response': '1 Werktag',
    },
    'peine': {
        'name': 'Peine', 'state': 'Niedersachsen', 'region': 'Braunschweiger Land',
        'standort': 'Hannover', 'branch': 'Hannover',
        'nearby': ['Hannover', 'Braunschweig', 'Hildesheim', 'Wolfsburg', 'Lehrte'],
        'zip': '31224', 'lat': 52.3208, 'lng': 10.2258,
        'intro_hook': 'Zwischen Hannover und Braunschweig – im Landkreis Peine',
        'randgebiet': True, 'response': '1 Werktag',
    },
    'burgdorf': {
        'name': 'Burgdorf', 'state': 'Niedersachsen', 'region': 'Region Hannover',
        'standort': 'Hannover', 'branch': 'Hannover',
        'nearby': ['Hannover', 'Celle', 'Lehrte', 'Uetze', 'Isernhagen'],
        'zip': '31303', 'lat': 52.4508, 'lng': 10.0075,
        'intro_hook': 'Östlich von Hannover – für Burgdorf und den Landkreis Hannover',
        'randgebiet': True, 'response': '1 Werktag',
    },
    'lehrte': {
        'name': 'Lehrte', 'state': 'Niedersachsen', 'region': 'Region Hannover',
        'standort': 'Hannover', 'branch': 'Hannover',
        'nearby': ['Hannover', 'Peine', 'Burgdorf', 'Sehnde', 'Uetze'],
        'zip': '31275', 'lat': 52.3733, 'lng': 9.9781,
        'intro_hook': 'Eisenbahn-Knotenpunkt östlich von Hannover',
        'randgebiet': True, 'response': '1 Werktag',
    },
    'wunstorf': {
        'name': 'Wunstorf', 'state': 'Niedersachsen', 'region': 'Region Hannover',
        'standort': 'Hannover', 'branch': 'Hannover',
        'nearby': ['Hannover', 'Neustadt am Rübenberge', 'Garbsen', 'Nienburg (Weser)'],
        'zip': '31515', 'lat': 52.4261, 'lng': 9.4333,
        'intro_hook': 'Westlich von Hannover an der Leine',
        'randgebiet': True, 'response': '1 Werktag',
    },
    'springe': {
        'name': 'Springe', 'state': 'Niedersachsen', 'region': 'Region Hannover',
        'standort': 'Hannover', 'branch': 'Hannover',
        'nearby': ['Hannover', 'Hameln', 'Bad Münder am Deister', 'Barsinghausen'],
        'zip': '31832', 'lat': 52.2089, 'lng': 9.5511,
        'intro_hook': 'Südwestlich von Hannover im Deister-Vorland',
        'randgebiet': True, 'response': '1 Werktag',
    },
    # ── Sachsen (Dresden/Chemnitz) ────────────────────────────────────────
    'dresden': {
        'name': 'Dresden', 'state': 'Sachsen', 'region': 'Elbtal/Osterzgebirge',
        'standort': 'Dresden & Chemnitz', 'branch': 'Dresden',
        'nearby': ['Radebeul', 'Meißen', 'Pirna', 'Freital', 'Heidenau', 'Coswig (Sachsen)'],
        'zip': '01067', 'lat': 51.0504, 'lng': 13.7373,
        'intro_hook': 'In der Elbmetropole Sachsens – von der Neustadt bis Striesen, von Plauen bis Blasewitz',
        'response': '1 Werktag',
    },
    'chemnitz': {
        'name': 'Chemnitz', 'state': 'Sachsen', 'region': 'Westerzgebirge',
        'standort': 'Dresden & Chemnitz', 'branch': 'Chemnitz',
        'nearby': ['Glauchau', 'Zwickau', 'Freiberg', 'Hohenstein-Ernstthal', 'Limbach-Oberfrohna'],
        'zip': '09111', 'lat': 50.8279, 'lng': 12.9214,
        'intro_hook': 'Drittgrößte Stadt Sachsens – Ihr Entrümpelungsprofi in Westsachsen',
        'response': '1 Werktag',
    },
    'pirna': {
        'name': 'Pirna', 'state': 'Sachsen', 'region': 'Sächsische Schweiz',
        'standort': 'Dresden & Chemnitz', 'branch': 'Dresden',
        'nearby': ['Dresden', 'Heidenau', 'Bad Schandau', 'Sebnitz', 'Neustadt in Sachsen'],
        'zip': '01796', 'lat': 50.9636, 'lng': 13.9358,
        'intro_hook': 'Tor zur Sächsischen Schweiz – für Pirna und den Landkreis',
        'response': '1 Werktag',
    },
    'meissen': {
        'name': 'Meißen', 'state': 'Sachsen', 'region': 'Elbtal',
        'standort': 'Dresden & Chemnitz', 'branch': 'Dresden',
        'nearby': ['Dresden', 'Radebeul', 'Coswig (Sachsen)', 'Riesa', 'Großenhain'],
        'zip': '01662', 'lat': 51.1642, 'lng': 13.4769,
        'intro_hook': 'Porzellanstadt an der Elbe – professionelle Entrümpelung im Meißner Land',
        'response': '1 Werktag',
    },
    'zwickau': {
        'name': 'Zwickau', 'state': 'Sachsen', 'region': 'Westerzgebirge',
        'standort': 'Dresden & Chemnitz', 'branch': 'Chemnitz',
        'nearby': ['Chemnitz', 'Glauchau', 'Plauen', 'Crimmitschau', 'Werdau'],
        'zip': '08056', 'lat': 50.7200, 'lng': 12.4967,
        'intro_hook': 'Robert-Schumann-Stadt in Westsachsen – für Zwickau und den Landkreis',
        'response': '1 Werktag',
    },
    'freiberg': {
        'name': 'Freiberg', 'state': 'Sachsen', 'region': 'Erzgebirge',
        'standort': 'Dresden & Chemnitz', 'branch': 'Chemnitz',
        'nearby': ['Chemnitz', 'Dresden', 'Brand-Erbisdorf', 'Großschirma', 'Flöha'],
        'zip': '09599', 'lat': 50.9133, 'lng': 13.3422,
        'intro_hook': 'Silberbergstadt im Erzgebirge – zwischen Chemnitz und Dresden',
        'response': '1 Werktag',
    },
    'riesa': {
        'name': 'Riesa', 'state': 'Sachsen', 'region': 'Elbtal',
        'standort': 'Dresden & Chemnitz', 'branch': 'Dresden',
        'nearby': ['Meißen', 'Dresden', 'Torgau', 'Großenhain', 'Strehla', 'Zeithain'],
        'zip': '01587', 'lat': 51.3069, 'lng': 13.2944,
        'intro_hook': 'Elbstadt zwischen Dresden und Leipzig',
        'response': '1 Werktag',
    },
    'plauen': {
        'name': 'Plauen', 'state': 'Sachsen', 'region': 'Vogtland',
        'standort': 'Dresden & Chemnitz', 'branch': 'Chemnitz',
        'nearby': ['Zwickau', 'Chemnitz', 'Reichenbach im Vogtland', 'Oelsnitz (Vogtland)'],
        'zip': '08523', 'lat': 50.4975, 'lng': 12.1358,
        'intro_hook': 'Vogtlandmetropole – für Plauen und den Vogtlandkreis',
        'response': '1 Werktag',
    },
    'glauchau': {
        'name': 'Glauchau', 'state': 'Sachsen', 'region': 'Westsachsen',
        'standort': 'Dresden & Chemnitz', 'branch': 'Chemnitz',
        'nearby': ['Zwickau', 'Chemnitz', 'Meerane', 'Waldenburg', 'Hohenstein-Ernstthal'],
        'zip': '08371', 'lat': 50.8228, 'lng': 12.5392,
        'intro_hook': 'Im Landkreis Zwickau',
        'response': '1 Werktag',
    },
    'radebeul': {
        'name': 'Radebeul', 'state': 'Sachsen', 'region': 'Elbtal',
        'standort': 'Dresden & Chemnitz', 'branch': 'Dresden',
        'nearby': ['Dresden', 'Meißen', 'Coswig (Sachsen)', 'Moritzburg'],
        'zip': '01445', 'lat': 51.1075, 'lng': 13.6653,
        'intro_hook': 'Karl-May-Stadt – direkt vor den Toren Dresdens',
        'response': '1 Werktag',
    },
    'freital': {
        'name': 'Freital', 'state': 'Sachsen', 'region': 'Sächsisches Bergland',
        'standort': 'Dresden & Chemnitz', 'branch': 'Dresden',
        'nearby': ['Dresden', 'Pirna', 'Heidenau', 'Bannewitz', 'Wilsdruff'],
        'zip': '01705', 'lat': 50.9989, 'lng': 13.6483,
        'intro_hook': 'Südlich von Dresden im Weißeritztal',
        'response': '1 Werktag',
    },
    'coswig': {
        'name': 'Coswig (Sachsen)', 'state': 'Sachsen', 'region': 'Elbtal',
        'standort': 'Dresden & Chemnitz', 'branch': 'Dresden',
        'nearby': ['Dresden', 'Meißen', 'Radebeul', 'Weinböhla', 'Großenhain'],
        'zip': '01640', 'lat': 51.1297, 'lng': 13.5789,
        'intro_hook': 'Zwischen Meißen und Dresden im idyllischen Elbtal',
        'response': '1 Werktag',
    },
    'heidenau': {
        'name': 'Heidenau', 'state': 'Sachsen', 'region': 'Sächsische Schweiz',
        'standort': 'Dresden & Chemnitz', 'branch': 'Dresden',
        'nearby': ['Dresden', 'Pirna', 'Freital', 'Dohna', 'Lohmen'],
        'zip': '01809', 'lat': 50.9839, 'lng': 13.8589,
        'intro_hook': 'Zwischen Dresden und der Sächsischen Schweiz',
        'response': '1 Werktag',
    },
    'bautzen': {
        'name': 'Bautzen', 'state': 'Sachsen', 'region': 'Oberlausitz',
        'standort': 'Dresden & Chemnitz', 'branch': 'Dresden',
        'nearby': ['Dresden', 'Görlitz', 'Hoyerswerda', 'Kamenz', 'Bischofswerda'],
        'zip': '02625', 'lat': 51.1814, 'lng': 14.4244,
        'intro_hook': 'Im Oberlausitzer Bergland – für Bautzen und den Landkreis Bautzen',
        'response': '1–2 Werktage',
    },
    'goerlitz': {
        'name': 'Görlitz', 'state': 'Sachsen', 'region': 'Oberlausitz',
        'standort': 'Dresden & Chemnitz', 'branch': 'Dresden',
        'nearby': ['Bautzen', 'Zittau', 'Löbau', 'Niesky', 'Weißwasser'],
        'zip': '02826', 'lat': 51.1522, 'lng': 14.9875,
        'intro_hook': 'Östlichste Stadt Deutschlands – für die Oberlausitz',
        'response': '1–2 Werktage',
    },
}


_EXTRA_LANDING_CITIES = {
    # ── Bundesweit: Große Städte ──────────────────────────────────────────
    'duisburg': {
        'name': 'Duisburg', 'state': 'Nordrhein-Westfalen', 'region': 'Ruhrgebiet',
        'zip': '47051', 'lat': 51.4344, 'lng': 6.7623, 'response': '2–5 Werktage',
    },
    'bochum': {
        'name': 'Bochum', 'state': 'Nordrhein-Westfalen', 'region': 'Ruhrgebiet',
        'zip': '44787', 'lat': 51.4818, 'lng': 7.2162, 'response': '2–5 Werktage',
    },
    'wuppertal': {
        'name': 'Wuppertal', 'state': 'Nordrhein-Westfalen', 'region': 'Bergisches Land',
        'zip': '42103', 'lat': 51.2562, 'lng': 7.1508, 'response': '2–5 Werktage',
    },
    'bielefeld': {
        'name': 'Bielefeld', 'state': 'Nordrhein-Westfalen', 'region': 'Ostwestfalen-Lippe',
        'zip': '33602', 'lat': 52.0302, 'lng': 8.5325, 'response': '2–5 Werktage',
    },
    'mannheim': {
        'name': 'Mannheim', 'state': 'Baden-Württemberg', 'region': 'Rhein-Neckar',
        'zip': '68159', 'lat': 49.4875, 'lng': 8.4660, 'response': '2–5 Werktage',
    },
    'wiesbaden': {
        'name': 'Wiesbaden', 'state': 'Hessen', 'region': 'Rhein-Main',
        'zip': '65183', 'lat': 50.0782, 'lng': 8.2398, 'response': '2–5 Werktage',
    },
    'moenchengladbach': {
        'name': 'Mönchengladbach', 'state': 'Nordrhein-Westfalen', 'region': 'Niederrhein',
        'zip': '41061', 'lat': 51.1805, 'lng': 6.4428, 'response': '2–5 Werktage',
    },
    'gelsenkirchen': {
        'name': 'Gelsenkirchen', 'state': 'Nordrhein-Westfalen', 'region': 'Ruhrgebiet',
        'zip': '45879', 'lat': 51.5177, 'lng': 7.0857, 'response': '2–5 Werktage',
    },
    'kiel': {
        'name': 'Kiel', 'state': 'Schleswig-Holstein', 'region': 'Schleswig-Holstein',
        'zip': '24103', 'lat': 54.3233, 'lng': 10.1394, 'response': '2–5 Werktage',
    },
    'aachen': {
        'name': 'Aachen', 'state': 'Nordrhein-Westfalen', 'region': 'Rheinland',
        'zip': '52062', 'lat': 50.7762, 'lng': 6.0838, 'response': '2–5 Werktage',
    },
    'freiburg': {
        'name': 'Freiburg im Breisgau', 'state': 'Baden-Württemberg', 'region': 'Breisgau',
        'zip': '79098', 'lat': 47.9990, 'lng': 7.8421, 'response': '2–5 Werktage',
    },
    'krefeld': {
        'name': 'Krefeld', 'state': 'Nordrhein-Westfalen', 'region': 'Niederrhein',
        'zip': '47798', 'lat': 51.3388, 'lng': 6.5853, 'response': '2–5 Werktage',
    },
    'luebeck': {
        'name': 'Lübeck', 'state': 'Schleswig-Holstein', 'region': 'Schleswig-Holstein',
        'zip': '23552', 'lat': 53.8655, 'lng': 10.6866, 'response': '2–5 Werktage',
    },
    'oberhausen': {
        'name': 'Oberhausen', 'state': 'Nordrhein-Westfalen', 'region': 'Ruhrgebiet',
        'zip': '46045', 'lat': 51.4963, 'lng': 6.8618, 'response': '2–5 Werktage',
    },
    'mainz': {
        'name': 'Mainz', 'state': 'Rheinland-Pfalz', 'region': 'Rhein-Main',
        'zip': '55116', 'lat': 49.9988, 'lng': 8.2731, 'response': '2–5 Werktage',
    },
    'kassel': {
        'name': 'Kassel', 'state': 'Hessen', 'region': 'Nordhessen',
        'zip': '34117', 'lat': 51.3153, 'lng': 9.4953, 'response': '1–2 Werktage',
    },
    'hagen': {
        'name': 'Hagen', 'state': 'Nordrhein-Westfalen', 'region': 'Märkisches Sauerland',
        'zip': '58095', 'lat': 51.3671, 'lng': 7.4631, 'response': '2–5 Werktage',
    },
    'hamm': {
        'name': 'Hamm', 'state': 'Nordrhein-Westfalen', 'region': 'Westfalen',
        'zip': '59065', 'lat': 51.6739, 'lng': 7.8264, 'response': '2–5 Werktage',
    },
    'saarbruecken': {
        'name': 'Saarbrücken', 'state': 'Saarland', 'region': 'Saarland',
        'zip': '66111', 'lat': 49.2402, 'lng': 6.9969, 'response': '2–5 Werktage',
    },
    'muelheim': {
        'name': 'Mülheim an der Ruhr', 'state': 'Nordrhein-Westfalen', 'region': 'Ruhrgebiet',
        'zip': '45468', 'lat': 51.4297, 'lng': 6.8827, 'response': '2–5 Werktage',
    },
    'potsdam': {
        'name': 'Potsdam', 'state': 'Brandenburg', 'region': 'Hauptstadtregion',
        'zip': '14467', 'lat': 52.3906, 'lng': 13.0645, 'response': '2–3 Werktage',
    },
    'leverkusen': {
        'name': 'Leverkusen', 'state': 'Nordrhein-Westfalen', 'region': 'Rheinland',
        'zip': '51373', 'lat': 51.0459, 'lng': 6.9946, 'response': '2–5 Werktage',
    },
    'oldenburg': {
        'name': 'Oldenburg', 'state': 'Niedersachsen', 'region': 'Norddeutschland',
        'zip': '26122', 'lat': 53.1434, 'lng': 8.2142, 'response': '2–5 Werktage',
    },
    'osnabrueck': {
        'name': 'Osnabrück', 'state': 'Niedersachsen', 'region': 'Westfalen',
        'zip': '49074', 'lat': 52.2799, 'lng': 8.0472, 'response': '1–2 Werktage',
    },
    'heidelberg': {
        'name': 'Heidelberg', 'state': 'Baden-Württemberg', 'region': 'Rhein-Neckar',
        'zip': '69115', 'lat': 49.4094, 'lng': 8.6942, 'response': '2–5 Werktage',
    },
    'solingen': {
        'name': 'Solingen', 'state': 'Nordrhein-Westfalen', 'region': 'Bergisches Land',
        'zip': '42651', 'lat': 51.1657, 'lng': 7.0832, 'response': '2–5 Werktage',
    },
    'darmstadt': {
        'name': 'Darmstadt', 'state': 'Hessen', 'region': 'Rhein-Main',
        'zip': '64283', 'lat': 49.8728, 'lng': 8.6512, 'response': '2–5 Werktage',
    },
    'regensburg': {
        'name': 'Regensburg', 'state': 'Bayern', 'region': 'Oberpfalz',
        'zip': '93047', 'lat': 49.0134, 'lng': 12.1016, 'response': '2–5 Werktage',
    },
    'herne': {
        'name': 'Herne', 'state': 'Nordrhein-Westfalen', 'region': 'Ruhrgebiet',
        'zip': '44623', 'lat': 51.5375, 'lng': 7.2260, 'response': '2–5 Werktage',
    },
    'paderborn': {
        'name': 'Paderborn', 'state': 'Nordrhein-Westfalen', 'region': 'Ostwestfalen-Lippe',
        'zip': '33098', 'lat': 51.7189, 'lng': 8.7575, 'response': '2–5 Werktage',
    },
    'neuss': {
        'name': 'Neuss', 'state': 'Nordrhein-Westfalen', 'region': 'Rheinland',
        'zip': '41460', 'lat': 51.2043, 'lng': 6.6878, 'response': '2–5 Werktage',
    },
    'ingolstadt': {
        'name': 'Ingolstadt', 'state': 'Bayern', 'region': 'Oberbayern',
        'zip': '85049', 'lat': 48.7665, 'lng': 11.4257, 'response': '2–5 Werktage',
    },
    'offenbach': {
        'name': 'Offenbach am Main', 'state': 'Hessen', 'region': 'Rhein-Main',
        'zip': '63065', 'lat': 50.0955, 'lng': 8.7761, 'response': '2–5 Werktage',
    },
    'wuerzburg': {
        'name': 'Würzburg', 'state': 'Bayern', 'region': 'Unterfranken',
        'zip': '97070', 'lat': 49.7944, 'lng': 9.9294, 'response': '2–5 Werktage',
    },
    'ulm': {
        'name': 'Ulm', 'state': 'Baden-Württemberg', 'region': 'Donau-Iller',
        'zip': '89073', 'lat': 48.4011, 'lng': 9.9876, 'response': '2–5 Werktage',
    },
    'heilbronn': {
        'name': 'Heilbronn', 'state': 'Baden-Württemberg', 'region': 'Heilbronn-Franken',
        'zip': '74072', 'lat': 49.1427, 'lng': 9.2109, 'response': '2–5 Werktage',
    },
    'pforzheim': {
        'name': 'Pforzheim', 'state': 'Baden-Württemberg', 'region': 'Nordschwarzwald',
        'zip': '75172', 'lat': 48.8921, 'lng': 8.6941, 'response': '2–5 Werktage',
    },
    'goettingen': {
        'name': 'Göttingen', 'state': 'Niedersachsen', 'region': 'Südniedersachsen',
        'zip': '37073', 'lat': 51.5338, 'lng': 9.9352, 'response': '1–2 Werktage',
    },
    'recklinghausen': {
        'name': 'Recklinghausen', 'state': 'Nordrhein-Westfalen', 'region': 'Ruhrgebiet',
        'zip': '45657', 'lat': 51.6142, 'lng': 7.1979, 'response': '2–5 Werktage',
    },
    'bottrop': {
        'name': 'Bottrop', 'state': 'Nordrhein-Westfalen', 'region': 'Ruhrgebiet',
        'zip': '46236', 'lat': 51.5236, 'lng': 6.9224, 'response': '2–5 Werktage',
    },
    'bremerhaven': {
        'name': 'Bremerhaven', 'state': 'Bremen', 'region': 'Norddeutschland',
        'zip': '27568', 'lat': 53.5430, 'lng': 8.5800, 'response': '2–5 Werktage',
    },
    'reutlingen': {
        'name': 'Reutlingen', 'state': 'Baden-Württemberg', 'region': 'Neckar-Alb',
        'zip': '72764', 'lat': 48.4913, 'lng': 9.2041, 'response': '2–5 Werktage',
    },
    'erlangen': {
        'name': 'Erlangen', 'state': 'Bayern', 'region': 'Mittelfranken',
        'zip': '91052', 'lat': 49.5961, 'lng': 11.0044, 'response': '2–5 Werktage',
    },
    'trier': {
        'name': 'Trier', 'state': 'Rheinland-Pfalz', 'region': 'Moselland',
        'zip': '54290', 'lat': 49.7488, 'lng': 6.6378, 'response': '2–5 Werktage',
    },
    'moers': {
        'name': 'Moers', 'state': 'Nordrhein-Westfalen', 'region': 'Niederrhein',
        'zip': '47441', 'lat': 51.4526, 'lng': 6.6234, 'response': '2–5 Werktage',
    },
    'siegen': {
        'name': 'Siegen', 'state': 'Nordrhein-Westfalen', 'region': 'Siegerland',
        'zip': '57072', 'lat': 50.8743, 'lng': 8.0243, 'response': '2–5 Werktage',
    },
    'fuerth': {
        'name': 'Fürth', 'state': 'Bayern', 'region': 'Mittelfranken',
        'zip': '90762', 'lat': 49.4743, 'lng': 10.9897, 'response': '2–5 Werktage',
    },
    'koblenz': {
        'name': 'Koblenz', 'state': 'Rheinland-Pfalz', 'region': 'Mittelrhein',
        'zip': '56068', 'lat': 50.3533, 'lng': 7.5880, 'response': '2–5 Werktage',
    },
    'bergisch-gladbach': {
        'name': 'Bergisch Gladbach', 'state': 'Nordrhein-Westfalen', 'region': 'Bergisches Land',
        'zip': '51465', 'lat': 51.0000, 'lng': 7.1333, 'response': '2–5 Werktage',
    },
    'remscheid': {
        'name': 'Remscheid', 'state': 'Nordrhein-Westfalen', 'region': 'Bergisches Land',
        'zip': '42853', 'lat': 51.1799, 'lng': 7.1892, 'response': '2–5 Werktage',
    },
    # ── Thüringen (nahe Servicegebiet) ────────────────────────────────────
    'jena': {
        'name': 'Jena', 'state': 'Thüringen', 'region': 'Thüringen',
        'zip': '07743', 'lat': 50.9272, 'lng': 11.5861, 'response': '1–2 Werktage',
    },
    'gera': {
        'name': 'Gera', 'state': 'Thüringen', 'region': 'Thüringen',
        'zip': '07545', 'lat': 50.8772, 'lng': 12.0810, 'response': '1–2 Werktage',
    },
    'weimar': {
        'name': 'Weimar', 'state': 'Thüringen', 'region': 'Thüringen',
        'zip': '99423', 'lat': 50.9793, 'lng': 11.3290, 'response': '1–2 Werktage',
    },
    'nordhausen': {
        'name': 'Nordhausen', 'state': 'Thüringen', 'region': 'Harz-Thüringen',
        'zip': '99734', 'lat': 51.5037, 'lng': 10.7903, 'response': '1 Werktag',
    },
    'gotha': {
        'name': 'Gotha', 'state': 'Thüringen', 'region': 'Westthüringen',
        'zip': '99867', 'lat': 50.9487, 'lng': 10.7027, 'response': '1–2 Werktage',
    },
    'eisenach': {
        'name': 'Eisenach', 'state': 'Thüringen', 'region': 'Westthüringen',
        'zip': '99817', 'lat': 50.9800, 'lng': 10.3200, 'response': '1–2 Werktage',
    },
    # ── Brandenburg / Sachsen-Anhalt (nahe Berlin/Leipzig) ────────────────
    'cottbus': {
        'name': 'Cottbus', 'state': 'Brandenburg', 'region': 'Lausitz',
        'zip': '03046', 'lat': 51.7611, 'lng': 14.3339, 'response': '2–3 Werktage',
    },
    'potsdam-mittelmark': {
        'name': 'Brandenburg an der Havel', 'state': 'Brandenburg', 'region': 'Havelland',
        'zip': '14770', 'lat': 52.4128, 'lng': 12.5548, 'response': '2–3 Werktage',
    },
    # ── Mecklenburg-Vorpommern ─────────────────────────────────────────────
    'schwerin': {
        'name': 'Schwerin', 'state': 'Mecklenburg-Vorpommern', 'region': 'Mecklenburg',
        'zip': '19053', 'lat': 53.6288, 'lng': 11.4148, 'response': '2–5 Werktage',
    },
    'greifswald': {
        'name': 'Greifswald', 'state': 'Mecklenburg-Vorpommern', 'region': 'Vorpommern',
        'zip': '17489', 'lat': 54.0959, 'lng': 13.3817, 'response': '2–5 Werktage',
    },
    # ── Niedersachsen zusätzlich ───────────────────────────────────────────
    'lueneburg': {
        'name': 'Lüneburg', 'state': 'Niedersachsen', 'region': 'Lüneburger Heide',
        'zip': '21335', 'lat': 53.2509, 'lng': 10.4023, 'response': '1–2 Werktage',
    },
    'wolfenbuettel': {
        'name': 'Wolfenbüttel', 'state': 'Niedersachsen', 'region': 'Braunschweig',
        'zip': '38300', 'lat': 52.1619, 'lng': 10.5393, 'response': '1 Werktag',
    },
    'goslar': {
        'name': 'Goslar', 'state': 'Niedersachsen', 'region': 'Harz',
        'zip': '38640', 'lat': 51.9058, 'lng': 10.4293, 'response': '1 Werktag',
    },
    'bad-harzburg': {
        'name': 'Bad Harzburg', 'state': 'Niedersachsen', 'region': 'Harz',
        'zip': '38667', 'lat': 51.8822, 'lng': 10.5608, 'response': '1 Werktag',
    },
    'uelzen': {
        'name': 'Uelzen', 'state': 'Niedersachsen', 'region': 'Lüneburger Heide',
        'zip': '29525', 'lat': 52.9650, 'lng': 10.5650, 'response': '1–2 Werktage',
    },
    # ── Bayern zusätzlich ─────────────────────────────────────────────────
    'bamberg': {
        'name': 'Bamberg', 'state': 'Bayern', 'region': 'Oberfranken',
        'zip': '96052', 'lat': 49.8988, 'lng': 10.9028, 'response': '2–5 Werktage',
    },
    'bayreuth': {
        'name': 'Bayreuth', 'state': 'Bayern', 'region': 'Oberfranken',
        'zip': '95444', 'lat': 49.9456, 'lng': 11.5713, 'response': '2–5 Werktage',
    },
    # ── Sachsen zusätzlich ────────────────────────────────────────────────
    'hohenstein-ernstthal': {
        'name': 'Hohenstein-Ernstthal', 'state': 'Sachsen', 'region': 'Westsachsen',
        'zip': '09337', 'lat': 50.7994, 'lng': 12.7108, 'response': '1 Werktag',
    },
    'meerane': {
        'name': 'Meerane', 'state': 'Sachsen', 'region': 'Westsachsen',
        'zip': '08393', 'lat': 50.8536, 'lng': 12.4664, 'response': '1 Werktag',
    },
    'limbach-oberfrohna': {
        'name': 'Limbach-Oberfrohna', 'state': 'Sachsen', 'region': 'Westsachsen',
        'zip': '09212', 'lat': 50.8653, 'lng': 12.7542, 'response': '1 Werktag',
    },
    'auerbach': {
        'name': 'Auerbach/Vogtl.', 'state': 'Sachsen', 'region': 'Vogtland',
        'zip': '08209', 'lat': 50.5072, 'lng': 12.4000, 'response': '1 Werktag',
    },
    'annaberg-buchholz': {
        'name': 'Annaberg-Buchholz', 'state': 'Sachsen', 'region': 'Erzgebirge',
        'zip': '09456', 'lat': 50.5775, 'lng': 13.0019, 'response': '1 Werktag',
    },
    'markkleeberg': {
        'name': 'Markkleeberg', 'state': 'Sachsen', 'region': 'Südraum Leipzig',
        'zip': '04416', 'lat': 51.2744, 'lng': 12.3747, 'response': '1 Werktag',
    },
    # ── Sachsen-Anhalt zusätzlich ─────────────────────────────────────────
    'bitterfeld-wolfen': {
        'name': 'Bitterfeld-Wolfen', 'state': 'Sachsen-Anhalt', 'region': 'Anhalt-Bitterfeld',
        'zip': '06749', 'lat': 51.6237, 'lng': 12.3217, 'response': '1 Werktag',
    },
    'koethen': {
        'name': 'Köthen (Anhalt)', 'state': 'Sachsen-Anhalt', 'region': 'Anhalt',
        'zip': '06366', 'lat': 51.7520, 'lng': 11.9722, 'response': '1 Werktag',
    },
    'weissenfels': {
        'name': 'Weißenfels', 'state': 'Sachsen-Anhalt', 'region': 'Saalekreis',
        'zip': '06667', 'lat': 51.1997, 'lng': 11.9675, 'response': '1 Werktag',
    },
    'naumburg': {
        'name': 'Naumburg (Saale)', 'state': 'Sachsen-Anhalt', 'region': 'Burgenlandkreis',
        'zip': '06618', 'lat': 51.1517, 'lng': 11.8100, 'response': '1 Werktag',
    },
    'zeitz': {
        'name': 'Zeitz', 'state': 'Sachsen-Anhalt', 'region': 'Burgenlandkreis',
        'zip': '06712', 'lat': 51.0453, 'lng': 12.1411, 'response': '1 Werktag',
    },
    'schoenebeck': {
        'name': 'Schönebeck (Elbe)', 'state': 'Sachsen-Anhalt', 'region': 'Salzlandkreis',
        'zip': '39218', 'lat': 51.9983, 'lng': 11.7283, 'response': '1 Werktag',
    },
    'stassfurt': {
        'name': 'Staßfurt', 'state': 'Sachsen-Anhalt', 'region': 'Salzlandkreis',
        'zip': '39418', 'lat': 51.8664, 'lng': 11.5681, 'response': '1 Werktag',
    },
    'lutherstadt-wittenberg': {
        'name': 'Lutherstadt Wittenberg', 'state': 'Sachsen-Anhalt', 'region': 'Wittenberg',
        'zip': '06886', 'lat': 51.8656, 'lng': 12.6478, 'response': '1 Werktag',
    },
    'hettstedt': {
        'name': 'Hettstedt', 'state': 'Sachsen-Anhalt', 'region': 'Mansfeld-Südharz',
        'zip': '06333', 'lat': 51.6436, 'lng': 11.5044, 'response': '1 Werktag',
    },
    # ── Rheinland-Pfalz zusätzlich ────────────────────────────────────────
    'kaiserslautern': {
        'name': 'Kaiserslautern', 'state': 'Rheinland-Pfalz', 'region': 'Westpfalz',
        'zip': '67655', 'lat': 49.4401, 'lng': 7.7491, 'response': '2–5 Werktage',
    },
}


# ── Entfernung zum zustaendigen Standort ────────────────────────────────────
#
# In F17 ergaenzt. Die damals 53 Stadtseiten waren zu 95 % textgleich, und nur 16 von
# ihnen waren indexiert. Was fehlte, war ein Unterschied, der *stimmt* - nicht
# umformulierter Fuelltext.
#
# Die Luftlinie zwischen Stadt und zustaendigem Standort ist so ein
# Unterschied: Sie steht schon in den Daten (lat/lng), ist nachrechenbar,
# variiert von 0 bis 88 km und sagt dem Leser genau das, was er wissen will -
# wie weit weg das Team sitzt. Nichts davon ist erfunden.
#
# Bewusst Luftlinie und nicht Fahrzeit: Eine Fahrzeit haengt von Strecke und
# Verkehr ab und waere geschaetzt. "Luftlinie" ist ehrlich und pruefbar.

import functools
import math as _math

# Sitz der sechs Teams - jeweils die Koordinaten der gleichnamigen Stadtseite.
#: EIG140 (24.09.2026): Alte Landingpage-Slugs, deren Ort eine Stadtseite
#: unter einem ANDEREN Slug hat. Sie standen nur in _EXTRA_LANDING_CITIES und
#: antworteten deshalb mit 410 "wir sind dort nicht vor Ort" - fuer
#: Bitterfeld-Wolfen, das die Startseite unter "Eigene Teams" fuehrt. Jetzt
#: 301 auf die Stadtseite (views.city_landing_page). Ein Slug, der selbst in
#: _CITY_DATA steht, braucht hier keinen Eintrag - er leitet ohnehin weiter.
LANDING_ALIASE = {
    'bitterfeld-wolfen': 'bitterfeld',
}


_STANDORT_SLUG = {
    'Leipzig': 'leipzig', 'Halle': 'halle', 'Magdeburg': 'magdeburg',
    'Dresden': 'dresden', 'Chemnitz': 'chemnitz', 'Hannover': 'hannover',
}


def standort_slug(city):
    """Slug der Standortstadt, deren Team diese Stadt betreut - oder None."""
    ziel = _STANDORT_SLUG.get((city or {}).get('branch'))
    return ziel if ziel in _CITY_DATA else None


#: Die Stadt, fuer die bewusst die STARTSEITE rankt (Entscheidung vom
#: 24.09.2026, Search Console 25.08.-21.09.: "entruempelung halle" Startseite
#: Pos. 6,9, Stadtseite Pos. 39-48). Die Stadtseite dieser Stadt bleibt die
#: Detailseite (Stadtteile, Wertstoffhoefe, Beispiele) und verlinkt die
#: Startseite mit dem Ortsnamen im Ankertext. Siehe docs/seo-technik.md.
STARTSEITE_STADT = 'halle'


#: EIG241 (24.09.2026): Orte aus ``nearby`` ohne eigene Stadtseite, die NICHT
#: im Bundesland der Stadt liegen, deren Nachbar sie sind. Alle uebrigen erben
#: das Land ihrer Stadt (``bundesland_von``). Geprueft an der vollstaendigen
#: Liste der 79 Nachbarorte ohne Seite am 24.09.2026.
_BUNDESLAND_ABWEICHEND = {
    'Altenburg': 'Thüringen',
    'Apolda': 'Thüringen',
    'Nordhausen': 'Thüringen',
    'Bad Dürrenberg': 'Sachsen-Anhalt',
}


def bundesland_von(name, rueckfall=None):
    """Bundesland eines Ortsnamens fuer ``containedInPlace`` im Schema.

    Reihenfolge: Stadt mit eigener Seite (auch ueber den Standortnamen,
    "Halle" -> Halle (Saale)), dann die Ausnahmeliste, dann ``rueckfall`` -
    das Land der Stadt, in deren ``nearby`` der Ort steht. Ohne Rueckfall und
    ohne Treffer ``None``: lieber keine Einordnung als eine geratene.
    """
    for c in _CITY_DATA.values():
        if name in (c['name'], c.get('branch')):
            return c['state']
    return _BUNDESLAND_ABWEICHEND.get(name, rueckfall)


def _luftlinie_km(a, b):
    R = 6371.0
    p1, p2 = _math.radians(a[0]), _math.radians(b[0])
    dphi = p2 - p1
    dlam = _math.radians(b[1] - a[1])
    h = _math.sin(dphi / 2) ** 2 + _math.cos(p1) * _math.cos(p2) * _math.sin(dlam / 2) ** 2
    return 2 * R * _math.asin(_math.sqrt(h))


def entfernung_zum_standort(city):
    """Luftlinie in km zum zustaendigen Team. ``None``, wenn die Stadt selbst
    der Standort ist - dann waere "0 km entfernt" eine seltsame Aussage."""
    ziel = _STANDORT_SLUG.get(city.get('branch'))
    if not ziel or ziel not in _CITY_DATA:
        return None
    basis = _CITY_DATA[ziel]
    if basis['name'] == city['name']:
        return None
    km = _luftlinie_km((basis['lat'], basis['lng']), (city['lat'], city['lng']))
    return int(round(km))


def reagiert_in_stunden(city):
    """True, wenn die Reaktionszeit dieser Stadt in *Stunden* angegeben ist.

    Nur dann darf eine Seite mit Tempo werben. 45 der 54 Staedte stehen auf
    '1 Werktag'; ``city.html`` versprach ihnen bis zum 21.08.2026 trotzdem
    pauschal "Rueckmeldung garantiert innerhalb von 2 Stunden" - auf 39 Seiten
    ein Versprechen, das der Betrieb nicht halten kann, und auf derselben Seite
    ein Widerspruch zu ``{{ city.response }}`` weiter unten.

    Abgeleitet statt gepflegt: Ein zweites Feld waere die naechste Angabe, die
    von ``response`` abweicht. Wer neue Auspraegungen einfuehrt, muss nur darauf
    achten, dass Stundenangaben das Wort "Stunde" enthalten.
    """
    return 'Stunde' in (city.get('response') or '')


# ``stadt_ablauf()`` ist am 02.10.2026 entfallen (IS21): Der Sieben-Schritte-
# Ablauf stand auf allen 57 Stadtseiten fast wortgleich und gehoert auf die
# Leistungsseiten. Mit ihm ist das HowTo-Schema der Stadtseiten entfallen.


# ---------------------------------------------------------------------------
# Der Staedteblock "Entruempelung in weiteren Staedten" (Befund W3)
# ---------------------------------------------------------------------------
#
# **Was hier repariert wird.** Der Block stand bis zum 25.08.2026 mit hart
# getippten <a>-Tags in ``city.html`` **und** ``home.html`` - und listete
# **30 von 54** Staedten. Nicht 54. Gemessen mit ``check_seo --links``:
#
#     starke Klasse   56-65 kontextuelle Links, Klicktiefe 1   30 Staedte
#     schwache Klasse  3-18 kontextuelle Links, Klicktiefe 2   24 Staedte
#
# Sieben Staedte hatten exakt **drei** - Celle, Freiberg, Hameln, Langenhagen,
# Salzgitter, Springe, Wunstorf. Alle 24 haben am 22.08.2026 ihre recherchierten
# Ortsbeispiele bekommen: guter Inhalt auf Seiten, die Google kaum erreicht.
# Aufgefallen ist es nie, weil ``check_seo --links`` eine **Untergrenze** kennt
# ("mindestens 3 kontextuelle Links") und keine **Verteilung** bewertet: 3 und
# 65 sind beide "erfuellt".
#
# **Warum nicht einfach auf 54 aufblaehen.** 54 Links in einem Block auf
# 54 Seiten sind 2.916 Links, die alle gleich viel wert sind, also nichts -
# und sie kosten Seitengewicht, das mit 205 KiB je Stadtseite ohnehin der
# naechste Befund ist (W4). Stattdessen:
#
#   * **Die Startseite listet alle 54.** Sie ist **eine** Seite, und nur ein
#     Link von ``/`` bringt eine Stadtseite auf Klicktiefe 1. Das ist der
#     ganze Grund, warum 24 Seiten auf Tiefe 2 lagen.
#   * **Jede Stadtseite listet eine begruendete Auswahl** - die geographisch
#     naechsten Staedte plus die sechs Standorte. Dieselbe Logik, die
#     ``_nearby_links()`` schon vormacht, nur berechnet statt gepflegt.
#
# Eine neue Stadt ist damit **ein Eintrag in ``_CITY_DATA``** und sonst nichts.


def alle_stadtseiten():
    """Alle 54 Staedte mit eigener Seite, alphabetisch - fuer die Startseite.

    Randgebiet-Staedte sind **mit dabei**: Ihre Seiten stehen in der Sitemap,
    also muessen sie auch erreichbar sein. Das Flag wird mitgegeben, damit die
    Vorlage sie kennzeichnen kann, ohne die Daten ein zweites Mal zu lesen.
    """
    return [{'name': c['name'], 'slug': slug,
             'randgebiet': bool(c.get('randgebiet'))}
            for slug, c in sorted(_CITY_DATA.items(),
                                  key=lambda kv: kv[1]['name'])]


@functools.lru_cache(maxsize=1)
def _nachbarschaft(k=8):
    """slug -> die ``k`` naechsten Staedte, **symmetrisch abgeschlossen**.

    Warum symmetrisch. Eine reine "k naechste"-Auswahl ist gerichtet: Goerlitz
    hat zwoelf Nachbarn, aber keiner von ihnen hat Goerlitz unter seinen zwoelf
    naechsten - die Stadt liegt am Rand. Gemessen bekam sie dadurch **4**
    eingehende kontextuelle Links, waehrend Merseburg 21 hatte. Das ist
    dieselbe Zweiklassigkeit wie vor der Reparatur, nur eine Etage tiefer.

    Der symmetrische Abschluss haengt zu ``naechste(A)`` alle B dazu, fuer die
    A unter den naechsten von B steht. Damit gilt: **jede** Stadt bekommt
    mindestens ``k`` eingehende Links aus diesem Block, unabhaengig davon, wo
    sie liegt. Die Aussage bleibt wahr - "das sind die Staedte, zu denen wir
    von hier aus am kuerzesten fahren, und die, fuer die wir der kuerzeste Weg
    sind".

    Gecacht, weil das Ergebnis eine Konstante ist und der Aufbau 54x54
    Entfernungen rechnet - je Stadtseite einmal waere Verschwendung.
    """
    kern = {s for s in _STANDORT_SLUG.values() if s in _CITY_DATA}

    def naechste(slug):
        e = _CITY_DATA[slug]
        rest = sorted((s for s in _CITY_DATA if s != slug and s not in kern),
                      key=lambda s: _luftlinie_km(
                          (e['lat'], e['lng']),
                          (_CITY_DATA[s]['lat'], _CITY_DATA[s]['lng'])))
        return rest[:k]

    nah = {slug: set(naechste(slug)) for slug in _CITY_DATA}
    aus = {}
    for slug in _CITY_DATA:
        rueck = {a for a, ziele in nah.items() if slug in ziele and a != slug}
        aus[slug] = frozenset((nah[slug] | rueck) - kern - {slug})
    return aus


# ── Regionen und Standorte: zwei Zahlen, die nicht dasselbe meinen ──────────
#
# ⚠ **Dieses Modul kennt VIER Regionen und SECHS Standorte, und beides ist
# richtig.** Die sichtbare Seite hat den Unterschied bis zum 06.09.2026 nicht
# gemacht: Der Fliesstext sagte "Von unseren 4 Standorten", waehrend die
# Footer-Ueberschrift "Unsere Standorte" **sechs** Staedte auflistete
# (STANDORTE_NAV). Zwei Zahlen fuer dasselbe Wort, auf derselben Seite - fuer
# einen Leser irritierend, fuer eine Antwortmaschine ein Widerspruch in der
# Entitaet. Gefunden als P8/G6.
#
#   REGIONEN (4)      = Betreuungsgebiete, je eines mit einem Regionalleiter.
#                       'Leipzig & Halle' ist EIN Gebiet mit ZWEI Staedten.
#   standorte_nav (6) = Staedte, in denen ein Team sitzt.
#
# Die Zahl 4 stand vorher an fuenf Stellen getippt (home.html, standorte.html
# zweimal, ueber-uns.html zweimal) und in llms.txt ein sechstes Mal. Sie kommt
# jetzt aus REGIONEN - Regel 1 fuer die siebte Sorte Zahl.
#
# **Was hier NICHT entschieden ist:** welches der beiden Woerter "Standort"
# heissen soll. Das ist eine Frage an den Betrieb, keine an den Code; solange
# sie offen ist, bleibt der sichtbare Text unveraendert bei "4 Standorten" und
# nur seine Quelle wechselt.
REGIONEN = ('Leipzig & Halle', 'Magdeburg', 'Hannover', 'Dresden & Chemnitz')

#: Ausgeschrieben, weil der Fliesstext auf /ueber-uns/ und in llms.txt die
#: Zahl als Wort nennt ("an vier Standorten") und die Ziffer dort ein Bruch
#: waere. Ueber vier hinaus faellt die Zuordnung auf die Ziffer zurueck - eine
#: erfundene Zahlwortliste bis zwanzig waere Aufwand fuer einen Fall, den es
#: nicht gibt, und ein stiller Fehler, sobald es ihn doch gibt.
_ZAHLWORT = {1: 'einem', 2: 'zwei', 3: 'drei', 4: 'vier', 5: 'fuenf', 6: 'sechs'}
REGIONEN_WORT = _ZAHLWORT.get(len(REGIONEN), str(len(REGIONEN)))


def standorte_nav():
    """Die sechs Standorte fuer den Footer - Name und Slug, sonst nichts.

    Speist den site-weiten Staedteblock. Bis zum 25.08.2026 standen dort
    **30 hart getippte** ``<a>``-Tags, dieselben wie in ``home.html`` und
    ``city.html`` - die dritte Kopie derselben Liste. Reihenfolge wie in
    ``_STANDORT_SLUG``, also nach Groesse des Standorts, nicht alphabetisch.
    """
    return [{'name': _CITY_DATA[s]['name'], 'slug': s}
            for s in _STANDORT_SLUG.values() if s in _CITY_DATA]


# ── Wer eine Stadt betreut (G6, 27.08.2026) ─────────────────────────────────
# Der Schluessel zeigt auf ``AUTOR_META`` in ``models.py``; hier steht nur die
# Zuordnung, nicht der Name - sonst stuende er zweimal (Regel 12).
#
# Die Abbildung haengt am **branch**, nicht am Slug: So ist jede der 54 Staedte
# abgedeckt, nicht nur die sechs Standorte. ``matrix.py`` hatte dafuer eine
# eigene Slug-Liste; sie ruft jetzt hierher, damit es bei einer neuen Stadt
# nicht zwei Stellen sind.
_BRANCH_LEITER = {
    'Leipzig':   'oliver',
    'Halle':     'oliver',
    'Magdeburg': 'christoph',
    'Dresden':   'viktor',
    'Chemnitz':  'viktor',
}


def leiter_key(city):
    """Der ``AUTOR_META``-Schluessel des zustaendigen Regionalleiters, oder None."""
    if not city:
        return None
    return _BRANCH_LEITER.get(city.get('branch'))


# ── Ankertext-Varianten (P1, 27.08.2026) ────────────────────────────────────
# Gemessen am 27.08.2026 mit ``tools/ankertexte.py``: Von 78 kontextuellen
# Links auf /entrumpelung/halle/ trugen **56 denselben Text** ("Halle (Saale)",
# 72 %). Der Ankertext sagt Google, *wofuer* eine Seite steht - "Halle (Saale)"
# sagt "das ist ein Ort", nicht "hier wird entruempelt".
#
# **Die Variante haengt an der Quellseite, nicht am Ziel.** Das ist der Kern:
# Innerhalb einer Seite tragen alle Chips dieselbe Form, die Liste bleibt also
# optisch geschlossen - aber ueber 54 Stadtseiten verteilt sich das Signal auf
# vier Formulierungen. Haetten wir je Ziel variiert, stuenden auf einer Seite
# vier verschiedene Bauformen nebeneinander; das sieht nach Zufall aus und ist
# es dann auch.
#
# Alle vier Varianten beschreiben, was die Zielseite wirklich zeigt. Ein
# Ankertext wie "Haushaltsaufloesung Halle" waere hier **falsch**: Die
# Stadtseite fuehrt alle Leistungen, nicht diese eine - und irrefuehrende
# Ankertexte sind ein bekanntes Abwertungsmuster, also schlechter als
# Wiederholung.
_ANKER_VARIANTEN = (
    '{name}',
    'Entrümpelung {name}',
    'Entrümpelung in {name}',
    'Entrümpler {name}',
)


def anker_variante(quelle_slug, name):
    """Ankertext fuer einen Link von ``quelle_slug`` auf die Stadt ``name``.

    Deterministisch aus der Quelle abgeleitet (Quersumme der Zeichen), nicht
    zufaellig: Zwei Laeufe desselben Standes muessen dasselbe HTML erzeugen,
    sonst schwankt das Seitengewicht und ``check_seo`` vergleicht bei jedem
    Lauf gegen etwas anderes.

    **Was das nicht leistet:** Es verteilt Formulierungen, es verbessert keine.
    Ob die Variante zum Ziel passt, entscheidet die Liste oben - hier wird nur
    ausgewaehlt.
    """
    if not quelle_slug:
        return name
    i = sum(ord(z) for z in quelle_slug) % len(_ANKER_VARIANTEN)
    return _ANKER_VARIANTEN[i].format(name=name)


def weitere_staedte(city_slug):
    """Die begruendete Auswahl fuer den Block auf **einer** Stadtseite.

    Zusammensetzung:

    1. **Die sechs Standorte** (Leipzig, Halle, Magdeburg, Dresden, Chemnitz,
       Hannover). Sie sind die Seiten mit echter Nachfrage; wer auf einer
       kleinen Stadtseite landet, sucht als Naechstes oft die grosse. Und sie
       sind die Seiten, auf die die Google-Ads-Kampagnen zeigen (Regel 23).
    2. **Die Nachbarschaft** aus ``_nachbarschaft()`` - die geographisch
       naechsten Staedte plus die, fuer die diese Stadt der naechste Nachbar
       ist. Luftlinie aus ``lat``/``lng``, wie ``entfernung_zum_standort()``:
       nachrechenbar und nicht geschaetzt.

    Sortiert nach Entfernung, damit die Reihenfolge etwas bedeutet und nicht
    von der Reihenfolge im Dict abhaengt. Die eigene Stadt faellt heraus - eine
    Seite, die nur sich selbst verlinkt, ist nicht verlinkt.

    Die Nachbarorte aus ``nearby`` bleiben **drin**, obwohl sie weiter oben auf
    der Seite schon als Link stehen: Ein zweiter Link auf dieselbe URL kostet
    nichts, und sie herauszurechnen machte die Zahl der Links je Seite von der
    Pflege des ``nearby``-Feldes abhaengig - genau die Art stiller Kopplung,
    die den alten Block zerbrochen hat.

    Ergebnis, gemessen mit ``check_seo --links``: 13 bis 21 Links je Seite
    statt 30 hart getippter, **alle 54** Stadtseiten auf Klicktiefe 1, und der
    schwaechste Wert steigt von 3 auf 8.
    """
    eigen = _CITY_DATA.get(city_slug)
    if not eigen:
        return []
    kern = [s for s in _STANDORT_SLUG.values()
            if s != city_slug and s in _CITY_DATA]
    nachbarn = sorted(
        _nachbarschaft().get(city_slug, ()),
        key=lambda s: _luftlinie_km(
            (eigen['lat'], eigen['lng']),
            (_CITY_DATA[s]['lat'], _CITY_DATA[s]['lng'])))
    return [{'name': _CITY_DATA[s]['name'], 'slug': s,
             'anker': anker_variante(city_slug, _CITY_DATA[s]['name'])}
            for s in kern + nachbarn]
