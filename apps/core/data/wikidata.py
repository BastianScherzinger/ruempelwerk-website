# -*- coding: utf-8 -*-
"""Wikidata-Entitaeten der 54 Stadtseiten (G13) - **Beleg, nicht Behauptung**.

Erzeugt von ``seo-geo-plan/tools/wikidata_abgleich.py``. Nicht von Hand pflegen:
Wer eine Q-ID hier eintippt, umgeht genau die Pruefung, wegen der die Datei
existiert.

**Warum das ueberhaupt gebraucht wird.** Mehrere der 54 Staedte tragen einen
Namen, den es zweimal gibt - Halle (Saale) / Halle (Westf.), Coswig (Sachsen) /
Coswig (Anhalt), Naumburg (Saale) / Naumburg (Hessen). Ein ``sameAs`` auf den
Wikidata-Eintrag sagt einer Antwortmaschine, **welcher** Ort gemeint ist.

**Jede Q-ID ist gegen zwei Merkmale geprueft** (Einzelheiten im Werkzeug):
``P31`` muss eine Gemeinde oder Stadt nennen, und die Wikidata-Koordinate muss
zur Koordinate in ``cities.py`` passen. Die Koordinate steht hier mit drin,
damit ``check_seo`` das nachrechnen kann, **ohne bei jedem Lauf Wikidata zu
befragen** - eine Pruefung, die einen fremden Dienst braucht, haengt im Deploy.

**Was diese Datei nicht belegt:** ob die Stadt in ``cities.py`` die richtige ist.
Sie haelt zwei Quellen gegeneinander; stuenden in beiden dieselben falschen
Zahlen, waere der Abgleich gruen.
"""

from urllib.parse import quote

# Abrufdatum. Wikidata aendert sich - eine Q-ID ohne Stand ist eine Behauptung
# ohne Datum. Beim naechsten Abgleich mit hochziehen.
STAND = '2026-08-27'

# Toleranz des Koordinatenabgleichs in Kilometern. Grosszuegig, weil cities.py
# Ortsmitten nennt und Wikidata teils das Rathaus.
TOLERANZ_KM = 5.0

_WIKIDATA = {
    'aschersleben': {'qid': 'Q486991', 'label': 'Aschersleben',
        'p31': ['Q42744322'], 'lat': 51.75, 'lng': 11.46667, 'abstand_km': 0.73,
        'wikipedia': 'Aschersleben', 'cities_name': 'Aschersleben'},
    'bautzen': {'qid': 'Q14835', 'label': 'Bautzen',
        'p31': ['Q42744322'], 'lat': 51.18139, 'lng': 14.42389, 'abstand_km': 0.04,
        'wikipedia': 'Bautzen', 'cities_name': 'Bautzen'},
    'bernburg': {'qid': 'Q14938', 'label': 'Bernburg',
        'p31': ['Q42744322'], 'lat': 51.8, 'lng': 11.73333, 'abstand_km': 0.2,
        'wikipedia': 'Bernburg (Saale)', 'cities_name': 'Bernburg (Saale)'},
    'bitterfeld': {'qid': 'Q7007', 'label': 'Bitterfeld-Wolfen',
        'p31': ['Q42744322'], 'lat': 51.6425, 'lng': 12.30763, 'abstand_km': 2.29,
        'wikipedia': 'Bitterfeld-Wolfen', 'cities_name': 'Bitterfeld-Wolfen'},
    'borna': {'qid': 'Q10744', 'label': 'Borna',
        'p31': ['Q42744322'], 'lat': 51.11667, 'lng': 12.5, 'abstand_km': 1.1,
        'wikipedia': 'Borna', 'cities_name': 'Borna'},
    'braunschweig': {'qid': 'Q2773', 'label': 'Braunschweig',
        'p31': ['Q1549591', 'Q42744322'], 'lat': 52.26917, 'lng': 10.52111, 'abstand_km': 0.39,
        'wikipedia': 'Braunschweig', 'cities_name': 'Braunschweig'},
    'burgdorf': {'qid': 'Q555618', 'label': 'Burgdorf',
        'p31': ['Q42744322'], 'lat': 52.44378, 'lng': 10.00783, 'abstand_km': 0.78,
        'wikipedia': 'Burgdorf (Region Hannover)', 'cities_name': 'Burgdorf'},
    'celle': {'qid': 'Q3933', 'label': 'Celle',
        'p31': ['Q42744322'], 'lat': 52.62556, 'lng': 10.0825, 'abstand_km': 0.03,
        'wikipedia': 'Celle', 'cities_name': 'Celle'},
    'chemnitz': {'qid': 'Q2795', 'label': 'Chemnitz',
        'p31': ['Q1549591', 'Q42744322'], 'lat': 50.83235, 'lng': 12.91891, 'abstand_km': 0.53,
        'wikipedia': 'Chemnitz', 'cities_name': 'Chemnitz'},
    'coswig': {'qid': 'Q8693', 'label': 'Coswig',
        'p31': ['Q515'], 'lat': 51.13333, 'lng': 13.58333, 'abstand_km': 0.51,
        'wikipedia': 'Coswig (Sachsen)', 'cities_name': 'Coswig (Sachsen)'},
    'delitzsch': {'qid': 'Q12052', 'label': 'Delitzsch',
        'p31': ['Q42744322'], 'lat': 51.52639, 'lng': 12.3425, 'abstand_km': 0.06,
        'wikipedia': 'Delitzsch', 'cities_name': 'Delitzsch'},
    'dessau': {'qid': 'Q3828', 'label': 'Dessau-Roßlau',
        'p31': ['Q42744322'], 'lat': 51.83333, 'lng': 12.23333, 'abstand_km': 0.21,
        'wikipedia': 'Dessau-Roßlau', 'cities_name': 'Dessau-Roßlau'},
    'dresden': {'qid': 'Q1731', 'label': 'Dresden',
        'p31': ['Q1549591', 'Q42744322'], 'lat': 51.04933, 'lng': 13.73814, 'abstand_km': 0.13,
        'wikipedia': 'Dresden', 'cities_name': 'Dresden'},
    'eilenburg': {'qid': 'Q12055', 'label': 'Eilenburg',
        'p31': ['Q42744322'], 'lat': 51.46083, 'lng': 12.63583, 'abstand_km': 0.4,
        'wikipedia': 'Eilenburg', 'cities_name': 'Eilenburg'},
    'freiberg': {'qid': 'Q14819', 'label': 'Freiberg',
        'p31': ['Q42744322'], 'lat': 50.91194, 'lng': 13.34278, 'abstand_km': 0.16,
        'wikipedia': 'Freiberg', 'cities_name': 'Freiberg'},
    'freital': {'qid': 'Q5870', 'label': 'Freital',
        'p31': ['Q22865', 'Q42744322'], 'lat': 51.01667, 'lng': 13.65, 'abstand_km': 1.98,
        'wikipedia': 'Freital', 'cities_name': 'Freital'},
    'garbsen': {'qid': 'Q4001', 'label': 'Garbsen',
        'p31': ['Q42744322'], 'lat': 52.41833, 'lng': 9.59806, 'abstand_km': 0.84,
        'wikipedia': 'Garbsen', 'cities_name': 'Garbsen'},
    'glauchau': {'qid': 'Q20071', 'label': 'Glauchau',
        'p31': ['Q42744322'], 'lat': 50.82333, 'lng': 12.54444, 'abstand_km': 0.37,
        'wikipedia': 'Glauchau', 'cities_name': 'Glauchau'},
    'goerlitz': {'qid': 'Q4077', 'label': 'Görlitz',
        'p31': ['Q42744322'], 'lat': 51.15632, 'lng': 14.99102, 'abstand_km': 0.52,
        'wikipedia': 'Görlitz', 'cities_name': 'Görlitz'},
    'grimma': {'qid': 'Q10780', 'label': 'Grimma',
        'p31': ['Q42744322'], 'lat': 51.23834, 'lng': 12.72875, 'abstand_km': 0.86,
        'wikipedia': 'Grimma', 'cities_name': 'Grimma'},
    'halberstadt': {'qid': 'Q7072', 'label': 'Halberstadt',
        'p31': ['Q42744322'], 'lat': 51.89583, 'lng': 11.04667, 'abstand_km': 0.36,
        'wikipedia': 'Halberstadt', 'cities_name': 'Halberstadt'},
    'halle': {'qid': 'Q2814', 'label': 'Halle (Saale)',
        'p31': ['Q42744322', 'Q1547289', 'Q1549591'], 'lat': 51.48278, 'lng': 11.96972, 'abstand_km': 0.07,
        'wikipedia': 'Halle (Saale)', 'cities_name': 'Halle (Saale)'},
    'hameln': {'qid': 'Q4062', 'label': 'Hameln',
        'p31': ['Q42744322'], 'lat': 52.10306, 'lng': 9.36, 'abstand_km': 0.1,
        'wikipedia': 'Hameln', 'cities_name': 'Hameln'},
    'hannover': {'qid': 'Q1715', 'label': 'Hannover',
        'p31': ['Q1549591', 'Q42744322'], 'lat': 52.37444, 'lng': 9.73861, 'abstand_km': 0.48,
        'wikipedia': 'Hannover', 'cities_name': 'Hannover'},
    'heidenau': {'qid': 'Q6715', 'label': 'Heidenau',
        'p31': ['Q42744322'], 'lat': 50.98333, 'lng': 13.86667, 'abstand_km': 0.55,
        'wikipedia': 'Heidenau (Sachsen)', 'cities_name': 'Heidenau'},
    'koethen': {'qid': 'Q1796771', 'label': 'Köthen',
        'p31': ['Q42744322'], 'lat': 51.75111, 'lng': 11.97361, 'abstand_km': 0.14,
        'wikipedia': 'Köthen (Anhalt)', 'cities_name': 'Köthen (Anhalt)'},
    'langenhagen': {'qid': 'Q4158', 'label': 'Langenhagen',
        'p31': ['Q42744322'], 'lat': 52.43944, 'lng': 9.74, 'abstand_km': 0.85,
        'wikipedia': 'Langenhagen', 'cities_name': 'Langenhagen'},
    'lehrte': {'qid': 'Q7057', 'label': 'Lehrte',
        'p31': ['Q42744322'], 'lat': 52.3725, 'lng': 9.97694, 'abstand_km': 0.12,
        'wikipedia': 'Lehrte', 'cities_name': 'Lehrte'},
    'leipzig': {'qid': 'Q2079', 'label': 'Leipzig',
        'p31': ['Q1549591', 'Q515', 'Q42744322'], 'lat': 51.34063, 'lng': 12.37473, 'abstand_km': 0.15,
        'wikipedia': 'Leipzig', 'cities_name': 'Leipzig'},
    'lutherstadt-wittenberg': {'qid': 'Q6837', 'label': 'Lutherstadt Wittenberg',
        'p31': ['Q42744322', 'Q1547289'], 'lat': 51.8671, 'lng': 12.6484, 'abstand_km': 1.04,
        'wikipedia': 'Lutherstadt Wittenberg', 'cities_name': 'Lutherstadt Wittenberg'},
    'magdeburg': {'qid': 'Q1733', 'label': 'Magdeburg',
        'p31': ['Q42744322', 'Q1549591', 'Q1547289', 'Q515'], 'lat': 52.13159, 'lng': 11.63996, 'abstand_km': 1.49,
        'wikipedia': 'Magdeburg', 'cities_name': 'Magdeburg'},
    'markranstaedt': {'qid': 'Q10770', 'label': 'Markranstädt',
        'p31': ['Q42744322'], 'lat': 51.30167, 'lng': 12.22111, 'abstand_km': 0.36,
        'wikipedia': 'Markranstädt', 'cities_name': 'Markranstädt'},
    'meissen': {'qid': 'Q8738', 'label': 'Meißen',
        'p31': ['Q42744322'], 'lat': 51.16361, 'lng': 13.4775, 'abstand_km': 0.08,
        'wikipedia': 'Meißen', 'cities_name': 'Meißen'},
    'merseburg': {'qid': 'Q14945', 'label': 'Merseburg',
        'p31': ['Q42744322'], 'lat': 51.35444, 'lng': 11.99278, 'abstand_km': 0.11,
        'wikipedia': 'Merseburg', 'cities_name': 'Merseburg'},
    'naumburg': {'qid': 'Q15986', 'label': 'Naumburg',
        'p31': ['Q42744322'], 'lat': 51.1521, 'lng': 11.80982, 'abstand_km': 0.2,
        'wikipedia': 'Naumburg (Saale)', 'cities_name': 'Naumburg (Saale)'},
    'peine': {'qid': 'Q6850', 'label': 'Peine',
        'p31': ['Q42744322'], 'lat': 52.32028, 'lng': 10.23361, 'abstand_km': 0.53,
        'wikipedia': 'Peine', 'cities_name': 'Peine'},
    'pirna': {'qid': 'Q6477', 'label': 'Pirna',
        'p31': ['Q42744322'], 'lat': 50.96222, 'lng': 13.94028, 'abstand_km': 0.35,
        'wikipedia': 'Pirna', 'cities_name': 'Pirna'},
    'plauen': {'qid': 'Q3952', 'label': 'Plauen',
        'p31': ['Q42744322'], 'lat': 50.495, 'lng': 12.13833, 'abstand_km': 0.33,
        'wikipedia': 'Plauen', 'cities_name': 'Plauen'},
    'quedlinburg': {'qid': 'Q40623', 'label': 'Quedlinburg',
        'p31': ['Q42744322'], 'lat': 51.79167, 'lng': 11.14722, 'abstand_km': 0.25,
        'wikipedia': 'Quedlinburg', 'cities_name': 'Quedlinburg'},
    'querfurt': {'qid': 'Q518204', 'label': 'Querfurt',
        'p31': ['Q42744322'], 'lat': 51.38333, 'lng': 11.6, 'abstand_km': 0.0,
        'wikipedia': 'Querfurt', 'cities_name': 'Querfurt'},
    'radebeul': {'qid': 'Q8762', 'label': 'Radebeul',
        'p31': ['Q42744322'], 'lat': 51.10333, 'lng': 13.67, 'abstand_km': 0.57,
        'wikipedia': 'Radebeul', 'cities_name': 'Radebeul'},
    'riesa': {'qid': 'Q8775', 'label': 'Riesa',
        'p31': ['Q42744322'], 'lat': 51.30806, 'lng': 13.29389, 'abstand_km': 0.13,
        'wikipedia': 'Riesa', 'cities_name': 'Riesa'},
    'salzgitter': {'qid': 'Q3200', 'label': 'Salzgitter',
        'p31': ['Q1549591', 'Q1549591', 'Q42744322'], 'lat': 52.15028, 'lng': 10.35931, 'abstand_km': 0.71,
        'wikipedia': 'Salzgitter', 'cities_name': 'Salzgitter'},
    'sangerhausen': {'qid': 'Q502434', 'label': 'Sangerhausen',
        'p31': ['Q42744322'], 'lat': 51.46667, 'lng': 11.3, 'abstand_km': 0.63,
        'wikipedia': 'Sangerhausen', 'cities_name': 'Sangerhausen'},
    'schkeuditz': {'qid': 'Q12058', 'label': 'Schkeuditz',
        'p31': ['Q42744322'], 'lat': 51.4, 'lng': 12.21667, 'abstand_km': 0.34,
        'wikipedia': 'Schkeuditz', 'cities_name': 'Schkeuditz'},
    'springe': {'qid': 'Q622891', 'label': 'Springe',
        'p31': ['Q42744322'], 'lat': 52.21667, 'lng': 9.55, 'abstand_km': 0.87,
        'wikipedia': 'Springe', 'cities_name': 'Springe'},
    'stendal': {'qid': 'Q7082', 'label': 'Stendal',
        'p31': ['Q42744322'], 'lat': 52.6, 'lng': 11.85, 'abstand_km': 0.88,
        'wikipedia': 'Stendal', 'cities_name': 'Stendal'},
    'taucha': {'qid': 'Q12050', 'label': 'Taucha',
        'p31': ['Q42744322'], 'lat': 51.38, 'lng': 12.49361, 'abstand_km': 0.17,
        'wikipedia': 'Taucha', 'cities_name': 'Taucha'},
    'torgau': {'qid': 'Q12062', 'label': 'Torgau',
        'p31': ['Q1547289'], 'lat': 51.56028, 'lng': 13.00556, 'abstand_km': 0.34,
        'wikipedia': 'Torgau', 'cities_name': 'Torgau'},
    'weissenfels': {'qid': 'Q14815', 'label': 'Weißenfels',
        'p31': ['Q42744322'], 'lat': 51.2, 'lng': 11.96667, 'abstand_km': 0.26,
        'wikipedia': 'Weißenfels', 'cities_name': 'Weißenfels'},
    'wernigerode': {'qid': 'Q15982', 'label': 'Wernigerode',
        'p31': ['Q42744322'], 'lat': 51.835, 'lng': 10.78528, 'abstand_km': 0.23,
        'wikipedia': 'Wernigerode', 'cities_name': 'Wernigerode'},
    'wunstorf': {'qid': 'Q14827', 'label': 'Wunstorf',
        'p31': ['Q42744322'], 'lat': 52.42377, 'lng': 9.43585, 'abstand_km': 0.31,
        'wikipedia': 'Wunstorf', 'cities_name': 'Wunstorf'},
    'zeitz': {'qid': 'Q16087', 'label': 'Zeitz',
        'p31': ['Q42744322', 'Q1547289'], 'lat': 51.04916, 'lng': 12.135, 'abstand_km': 0.22,
        'wikipedia': 'Zeitz', 'cities_name': 'Zeitz'},
    'zwickau': {'qid': 'Q3778', 'label': 'Zwickau',
        'p31': ['Q42744322'], 'lat': 50.71889, 'lng': 12.49611, 'abstand_km': 0.13,
        'wikipedia': 'Zwickau', 'cities_name': 'Zwickau'},
}

# ── Konzepte fuer about/mentions ────────────────────────────────────────────
# Nur Begriffe mit deutschem Wikipedia-Artikel und passendem Label. Zu
# "Entruempelung" gibt es in Wikidata keinen Sachartikel - die Suche liefert
# Fernsehfolgen; ein about darauf waere falsch, nicht ungenau.
_KONZEPTE = {
    'haushaltsaufloesung': {'qid': 'Q1504666', 'label': 'Haushaltsauflösung', 'wikipedia': 'Haushaltsauflösung'},
    'sperrmuell-entsorgung': {'qid': 'Q1488232', 'label': 'Sperrmüll', 'wikipedia': 'Sperrmüll'},
}


def eintrag(slug):
    """Der geprüfte Datensatz einer Stadt, oder None."""
    return _WIKIDATA.get(slug)


def qid(slug):
    """Nur die Q-ID - fuer sameAs im Schema."""
    e = _WIKIDATA.get(slug)
    return e['qid'] if e else None


def wikipedia_url(slug):
    """Der deutsche Wikipedia-Artikel, oder None wenn es keinen gibt."""
    e = _WIKIDATA.get(slug)
    if not e or not e.get('wikipedia'):
        return None
    return 'https://de.wikipedia.org/wiki/' + quote(
        e['wikipedia'].replace(' ', '_'), safe='/()_,-')


def same_as(slug):
    """Die belegten sameAs-URLs einer Stadt - Wikidata zuerst, dann Wikipedia.

    Leere Liste, wenn nichts belegt ist. **Nie raten:** Ein sameAs auf die
    falsche Entitaet verknuepft den Ort mit dem Falschen und ist schlechter
    als gar keins.
    """
    e = _WIKIDATA.get(slug)
    if not e:
        return []
    aus = ['https://www.wikidata.org/wiki/' + e['qid']]
    w = wikipedia_url(slug)
    if w:
        aus.append(w)
    return aus


# Namen -> Slug. Die Schema-Bausteine bekommen Ortsnamen uebergeben
# (``areaServed``, ``nearby``), keine Slugs. Der Index wird einmal beim Import
# gebaut; ``label`` kommt aus Wikidata, ``name`` aus cities.py - beide Formen
# muessen treffen ("Bernburg" vs. "Bernburg (Saale)").
_NACH_NAME = {}
for _slug, _e in _WIKIDATA.items():
    for _n in (_e.get('label'), _e.get('cities_name')):
        if _n:
            _NACH_NAME.setdefault(_n, _slug)


def slug_fuer_name(name):
    """Slug zu einem Ortsnamen, oder None fuer Orte ohne eigene Seite."""
    return _NACH_NAME.get(name)


def same_as_fuer_name(name):
    """sameAs-URLs zu einem Ortsnamen - leer, wenn der Ort nicht belegt ist."""
    slug = _NACH_NAME.get(name)
    return same_as(slug) if slug else []


def alle():
    return dict(_WIKIDATA)


def konzept(slug):
    """Das belegte Wikidata-Konzept einer Leistungsseite, oder None.

    Nur zwei der neun Leistungen haben eines - siehe den Kommentar oben.
    """
    return _KONZEPTE.get(slug)


def konzept_same_as(slug):
    """about-URLs einer Leistungsseite - leere Liste, wenn nichts belegt ist."""
    k = _KONZEPTE.get(slug)
    if not k:
        return []
    return ['https://www.wikidata.org/wiki/' + k['qid'],
            'https://de.wikipedia.org/wiki/' + quote(
                k['wikipedia'].replace(' ', '_'), safe='/()_,-')]
