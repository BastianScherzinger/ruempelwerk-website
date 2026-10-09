# -*- coding: utf-8 -*-
"""Strukturierte Daten (JSON-LD) als Python-Dicts statt als Template-Text (F5).

Warum das die wichtigste Architekturentscheidung im Plan ist: Solange Schema als
Django-Template zusammengesetzt wird, sind drei Fehlerklassen strukturell
moeglich - und alle drei sind hier schon aufgetreten:

* **Dezimalkomma.** ``USE_I18N=True`` mit ``LANGUAGE_CODE='de-de'`` rendert
  ``51,3397`` statt ``51.3397`` und macht damit den ganzen Block zu ungueltigem
  JSON. Das war auf 184 Stadtseiten der Fall. Der Workaround ``|unlocalize``
  muss auf *jeder einzelnen Zahl* stehen - eine Disziplinregel, die genau einmal
  vergessen werden muss.
* **Kommafehler in Schleifen.** ``{% for x in y %},{...}{% endfor %}`` laeuft,
  ist aber bei jeder Aenderung eine Falle.
* **Preiszahlen von Hand.** In ``dienstleistungen.html`` standen
  ``"minPrice": "420"``, ``"180"`` und ``"580"`` - alle drei falsch, und
  unauffindbar fuer einen Grep nach Eurobetraegen, weil kein Waehrungszeichen
  danebensteht.

``json.dumps()`` kann keines dieser Probleme erzeugen: Floats bekommen immer
einen Punkt, Kommata sitzen richtig, und nicht serialisierbare Werte werfen einen
Fehler statt still falsch auszugeben. Preise kommen aus ``data/pricing.py``.

Die ``@id``-Anker (``…/#business``, ``…/#website``) bleiben stabil - andere
Bloecke verweisen darauf, und G1 baut daraus spaeter einen ``@graph``.
"""

from django.templatetags.static import static
from django.utils.html import strip_tags

from .data import auszeichnungen as _auszeichnungen
from .data import reviews as _reviews
from .data import city_lokal as _city_lokal
# G13: die abgeglichenen Wikidata-Entitaeten der 54 Staedte. Erzeugt von
# seo-geo-plan/tools/wikidata_abgleich.py, jede Q-ID gegen P31 UND
# Koordinate geprueft - siehe den Modulkopf dort.
from .data import wikidata as _wikidata
from .data.feste_dateien import LOGO_PFAD as _LOGO_PFAD
# knowsAbout der Personen: die Leistungen, die der Betrieb wirklich
# anbietet - aus services.py, nicht getippt.
from .data.services import alle_leistungen as _alle_leistungen
from .data.jobs import gueltig_bis as _gueltig_bis
from .data.zusagen import RECHNER_DAUER as _RECHNER_DAUER
from .data.pricing import (_PER_QM_PREISE, _PREISSTAND_ISO, euro as _euro)
# Die Stammdaten stehen seit G5 in data/firma.py - eine Quelle fuer Name,
# Adresse, Telefon und Steuernummer. Vorher standen sie hier UND von Hand im
# Impressum; fuer 'sameAs' ist genau diese Doppelpflege der Sargnagel, weil
# eine abweichende Schreibweise die Verknuepfung entwertet.
# Die Namen bleiben hier verfuegbar, damit nichts nachgezogen werden muss.
from .data.firma import (                                          # noqa: F401
    FIRMA, LEGALNAME, INHABER, TELEFON, TELEFON_ANZEIGE, STRASSE, ORT, PLZ,
    ZEITEN,
    BUNDESLAND, LAND, LAND_CODE, GEO, STEUERNUMMER,
)

# ── Einsatzgebiet (EIG358, 02.10.2026) ──────────────────────────────────────
# **Eine** Quelle fuer die Gebiete, die ein Leistungs-Knoten nennt. Bis dahin
# standen an drei Stellen drei verschiedene Listen (vier Staedte im Katalog,
# sechs plus drei Laender auf den Leistungsseiten, 23 Gebiete am Betrieb).
# Belegt ist nur die Betriebsstaette Halle (data/firma.py); alles andere ist
# **Einsatzgebiet**, kein Standort. Die sechs Staedte sind die, die auch
# Navigation und Startseitentext nennen (cities.standorte_nav); der Betriebs-
# knoten fuehrt sie immer mit (siehe business_schema), damit kein Leistungs-
# knoten ein Gebiet nennt, das der Betrieb selbst nicht nennt.
GEBIET_STAEDTE = ('Halle (Saale)', 'Leipzig', 'Magdeburg', 'Dresden',
                  'Chemnitz', 'Hannover')
GEBIET_LAENDER = ('Sachsen-Anhalt', 'Sachsen', 'Niedersachsen')


def _laender():
    return [{'@type': 'AdministrativeArea', 'name': n} for n in GEBIET_LAENDER]


# ── Bewertungen ─────────────────────────────────────────────────────────────


def bewertung():
    """Durchschnitt und Anzahl - taeglich abgeglichen, nicht mehr eingetippt.

    Vorher stand hier eine Konstante mit Pruefdatum daneben. Die war beim
    Eintippen richtig ("5.0 bei 8") und zum Zeitpunkt der Pruefung um mehr als
    das Doppelte daneben ("4.9 bei 18"). Eine Zahl, die sich ohne Deployment
    aendert, gehoert nicht in den Quelltext - sie kommt jetzt aus
    ``data/reviews.py``, das die Datenbank liest und auf die uebernommene
    Liste zurueckfaellt.
    """
    return _reviews.stand()


# KV11: Tage und Uhrzeiten kommen aus data/firma.py (eine Quelle).
OEFFNUNGSZEITEN = [
    {'@type': 'OpeningHoursSpecification',
     'dayOfWeek': list(tage), 'opens': von, 'closes': bis}
    for tage, von, bis in ZEITEN
]


def _adresse(ort=ORT, plz=PLZ, region=BUNDESLAND, strasse=STRASSE):
    a = {'@type': 'PostalAddress', 'addressLocality': ort, 'postalCode': plz,
         'addressRegion': region, 'addressCountry': 'DE'}
    if strasse:
        a['streetAddress'] = strasse
    return a


def _geo(lat, lng):
    # float, nicht str: json.dumps schreibt immer einen Punkt.
    return {'@type': 'GeoCoordinates', 'latitude': float(lat), 'longitude': float(lng)}


def _orte(namen, bundesland=None):
    """Ortsliste fuer ``areaServed`` - mit ``sameAs``, wo es belegt ist (G13).

    **Das ``sameAs`` gehoert an den Ort, nicht an den Betrieb.** Steht es am
    ``LocalBusiness``-Knoten, sagt das Schema "dieser Betrieb *ist* die Stadt
    Halle" - das ist keine Ungenauigkeit, sondern eine falsche Aussage ueber die
    Entitaet, und damit das Gegenteil dessen, was G13 erreichen soll.

    Orte ohne eigene Seite (Markkleeberg, Bad Duerrenberg …) stehen in
    ``nearby``, sind aber nicht abgeglichen. Sie bleiben ohne ``sameAs`` -
    lieber keine Verknuepfung als eine geratene.

    **Jeder Ort traegt sein Bundesland** (EIG241, 24.09.2026). Ein Ortsname
    allein ist mehrdeutig - "Neustadt", "Burg", "Borsdorf" gibt es mehrfach.
    ``bundesland`` ist der Rueckfall fuer Orte ohne eigene Seite (das Land der
    Stadt, deren Nachbar sie sind); ``cities.bundesland_von`` kennt die
    Ausnahmen jenseits der Landesgrenze.
    """
    from .data.cities import bundesland_von
    aus = []
    for n in namen:
        ort = {'@type': 'City', 'name': n}
        same = _wikidata.same_as_fuer_name(n)
        if same:
            ort['sameAs'] = same
        land = bundesland_von(n, bundesland)
        if land:
            ort['containedInPlace'] = {'@type': 'AdministrativeArea',
                                       'name': land}
        aus.append(ort)
    return aus


def _ort_mit_kette(name, bundesland):
    """Die eigene Stadt einer Stadtseite, eingeordnet bis Deutschland (G13).

    ``containedInPlace`` beantwortet die Frage, die bei gleichnamigen Orten
    offenbleibt: Halle (Saale) liegt in Sachsen-Anhalt, Halle (Westf.) nicht.
    Zusammen mit ``sameAs`` auf Wikidata ist der Ort damit doppelt bestimmt -
    einmal ueber die Normdaten-ID, einmal ueber die Verwaltungskette.

    Bundesland und Land tragen **bewusst keine Q-ID**: Es liegt keine
    abgeglichene Liste der Bundeslaender im Projekt, und eine getippte Q-ID
    waere genau die Sorte unbelegter Verknuepfung, die G13 verhindern soll.
    """
    ort = _orte([name], bundesland)[0]
    ort['containedInPlace'] = {
        '@type': 'AdministrativeArea',
        'name': bundesland,
        'containedInPlace': {'@type': 'Country', 'name': LAND},
    }
    return ort


# Einmal beim ersten Zugriff gebaut. Ein Modul-Level-Aufruf von
# alle_leistungen() waere ein Import-Nebeneffekt und wuerde services.py schon
# beim Laden von schema.py durchrechnen.
class _LeistungsNamen:
    def __iter__(self):
        return iter(_alle_leistungen())


_LEISTUNGSNAMEN = _LeistungsNamen()


def _person(site_url, key, anker=None, jobtitle='Regionalleiter'):
    """Ein ``Person``-Knoten aus ``AUTOR_META`` - oder ``None``, wenn es den
    Schluessel nicht gibt.

    **Der Import steht in der Funktion, nicht oben.** ``models.py`` laedt beim
    Import Djangos Model-Maschinerie; ein Modulimport hier zoege sie in jeden
    Aufruf von ``schema.py`` hinein und riskierte einen Zirkel ueber die Apps.

    **Foto nur, wo es eines gibt.** ``AUTOR_META['christoph']['foto']`` ist
    ``None`` - Christoph Regner hat als einziger kein Bild. Der Knoten bekommt
    dann **kein** ``image``, statt auf einen generischen Platzhalter zu zeigen:
    Ein Symbolbild, das als Foto einer benannten Person ausgegeben wird, ist
    eine falsche Aussage ueber diese Person, und ein leeres Feld ist besser als
    ein falsches.

    ``worksFor`` statt ``employee`` am Unternehmen: Ob die vier Regionalleiter
    angestellt, Partner oder selbststaendig sind, steht nirgends im Projekt.
    ``worksFor`` sagt "arbeitet fuer" und ist damit die Aussage, die belegt ist.
    """
    from .models import AUTOR_META

    meta = AUTOR_META.get(key)
    if not meta:
        return None
    d = {
        '@type': 'Person',
        '@id': f'{site_url}/#{anker.lstrip("#") if anker else "person-" + key}',
        'name': meta['name'],
        'jobTitle': jobtitle,
        'worksFor': {'@id': f'{site_url}/#business'},
        # Die Region ist die einzige belegte Aussage darueber, wofuer diese
        # Person zustaendig ist - sie steht so auf /ueber-uns/ und auf den
        # Stadtseiten ihres Gebiets.
        'areaServed': _orte([t.strip() for t in meta['region'].split('&')]),
        'knowsAbout': [l['name'] for l in _LEISTUNGSNAMEN],
    }
    if meta.get('foto'):
        d['image'] = f'{site_url}{static(meta["foto"])}'
    return d


def personen_schema(site_url, keys):
    """Die ``Person``-Knoten fuer eine Seite - nur die, die dort **sichtbar** sind.

    Regel 12: Sichtbarer Inhalt und Schema muessen uebereinstimmen. Deshalb
    stehen die Regionalleiter nicht site-weit im Graphen, sondern auf
    ``/ueber-uns/`` (alle vier) und auf den Stadtseiten ihres Gebiets (der
    zustaendige). Nebenbei spart das JSON-LD auf 80 Seiten.
    """
    aus = []
    for k in keys:
        # Der Inhaber behaelt seinen site-weiten Anker. Ohne das bekaeme er
        # auf /ueber-uns/ und auf den Stadtseiten von Leipzig und Halle einen
        # zweiten Knoten (#person-oliver) neben dem #owner aus dem
        # LocalBusiness - zwei @id fuer denselben Menschen, und damit fuer
        # eine Antwortmaschine zwei Personen. Genau das soll G6 verhindern.
        eigen = _person_anker(k)
        aus.append(_person(site_url, k, anker=eigen[0], jobtitle=eigen[1])
                   if eigen else _person(site_url, k))
    return [p for p in aus if p]


def _person_anker(key):
    """(@id-Anker, jobTitle) fuer Personen mit eigener Rolle, sonst None."""
    from .models import AUTOR_META

    meta = AUTOR_META.get(key) or {}
    if meta.get('name') == INHABER:
        return ('#owner', 'Inhaber und Gründer')
    return None


# ── Site-weite Bloecke ──────────────────────────────────────────────────────

def website_schema(site_url):
    return {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': f'{site_url}/#website',
        'url': f'{site_url}/',
        'name': FIRMA,
        'description': ('Professionelle Entrümpelung und Haushaltsauflösung zum Festpreis '
                        'in Sachsen-Anhalt, Sachsen und Niedersachsen.'),
        'inLanguage': 'de-DE',
        'publisher': {'@id': f'{site_url}/#business'},
    }


#: EIG19/EIG130 (24.09.2026): Die echten Masse von
#: ``static/images/ruempelwerk_logo.jpeg``. Hier standen 800 x 800 - derselbe
#: Zahlendreher, den P8/D3 beim og:image behoben hatte, nur eine Ebene tiefer.
#: ``test_schema.LogoMasseTests`` liest die Datei mit Pillow und vergleicht;
#: wer das Logo austauscht, bekommt dort den Hinweis, statt still zu luegen.
LOGO_DATEI = 'images/ruempelwerk_logo.jpeg'
LOGO_BREITE, LOGO_HOEHE = 1015, 1024


def business_schema(site_url, contact_email, staedte=()):
    """Der zentrale LocalBusiness-Knoten. ``@id`` ist der Anker fuer alles andere.

    Kein ``aggregateRating`` und kein ``review`` im eigenen Schema (Entscheidung
    06.10.2026): selbst veroeffentlichte Bewertungen fuer LocalBusiness zeigt Google
    nicht als Sterne, und es ist richtlinienkritisch (self-serving reviews). Die
    sichtbare Bewertungsanzeige mit Quelle/Stand bleibt davon unberuehrt.
    """
    # Feste Adresse ohne Hash (SEO-Audit 25.09.2026, K2): Google fuehrt das
    # Logo unter dieser URL im Knowledge Panel; die gehashte stirbt beim
    # naechsten Bildwechsel. Die Datei bleibt LOGO_DATEI (data/feste_dateien.py).
    logo = f'{site_url}{_LOGO_PFAD}'
    d = {
        '@context': 'https://schema.org',
        '@type': ['LocalBusiness', 'HomeAndConstructionBusiness'],
        '@id': f'{site_url}/#business',
        'name': FIRMA,
        'legalName': LEGALNAME,
        'description': ('Entrümpelung, Haushaltsauflösung, Wohnungsauflösung, '
                        'Kellerentrümpelung, Nachlassräumung, Gewerbeentrümpelung '
                        'und Sanierung. Festpreis nach Besichtigung, besenrein.'),
        'url': site_url,
        'telephone': TELEFON,
        'email': contact_email,
        # Kein foundingDate: unbestaetigt (2024/2025/2026 je nach Quelle);
        # 01.10.2026: Gruendungsjahr weglassen (Offen Nr. 28 / KV09).
        # Bildrechte wie an jedem Galeriebild (Search Console, 16.09.2026):
        # Google prueft jedes ImageObject auf dieselben fuenf Felder.
        'logo': dict({'@type': 'ImageObject', 'url': logo, 'contentUrl': logo,
                      'width': LOGO_BREITE, 'height': LOGO_HOEHE},
                     **bild_rechte(site_url)),
        'image': logo,
        'address': _adresse(),
        'geo': _geo(*GEO),
        'openingHoursSpecification': OEFFNUNGSZEITEN,
        'priceRange': '€€',
        'currenciesAccepted': 'EUR',
        # ── G5: die Entitaet eindeutig machen ────────────────────────────
        # 'sameAs' ist die ausdrueckliche Aussage "das bin auch ich". Ohne sie
        # bleiben Website und Unternehmensprofil fuer ein Sprachmodell zwei
        # unverbundene Textmengen - und im Zweifel zitiert es den Wettbewerber,
        # bei dem es sich sicher ist.
        #
        # Hier stehen **drei** Profile, und jedes ist belegt: das
        # Google-Unternehmensprofil (data/reviews.py, seit dem 14.08.2026 mit
        # echten Rezensionen abgeglichen) sowie Trustlocal und
        # werkenntdenbesten (data/auszeichnungen.py) - beide am 01.10.2026
        # live geprueft: Name "Ruempelwerk Mitteldeutschland", Cansteinstrasse
        # 14 in Halle ("Cansteinstr. 14" auf dem Portal), dieselben
        # Telefonziffern. Facebook, Instagram, Gelbe Seiten, Das Oertliche,
        # 11880, wlw, Cylex und ProvenExpert nennt der Plan als Kandidaten -
        # keines davon ist nachgewiesen. Eine erfundene Profil-URL waere
        # schlimmer als gar keine: ein 'sameAs' auf eine fremde oder tote
        # Seite verknuepft die Entitaet mit dem Falschen. Wer ein weiteres
        # Profil anlegt oder findet, ergaenzt die Liste hier - und prueft
        # vorher, dass Name, Adresse und Telefonnummer dort so stehen wie in
        # data/firma.py.
        'sameAs': [_reviews.stand()['profil_url'],
                   _auszeichnungen.TRUSTLOCAL['profil_url'],
                   _auszeichnungen.WKDB['profil_url']],
        'hasMap': _reviews.stand()['profil_url'],
        # Steuernummer statt vatID: Eine USt-IdNr. nennt das Impressum nicht,
        # und eine erfundene waere eine falsche Tatsachenbehauptung.
        'taxID': STEUERNUMMER,
        # Der Inhaber als eigener Knoten mit stabiler @id (G6, ausgebaut am
        # 27.08.2026). Was hier steht, ist **belegt**: Rolle und Foto stehen so
        # auf /ueber-uns/, knowsAbout ist die Liste der Leistungsseiten.
        #
        # Was hier **nicht** steht, ist so wichtig wie das, was dasteht: keine
        # 'description' mit Jahren Erfahrung, keine Qualifikation. Das waeren
        # Tatsachenbehauptungen ueber eine reale Person, und im Repository ist
        # keine davon nachgewiesen. Dieselbe Regel, aus der bei G5 nur
        # belegte Profile in 'sameAs' stehen.
        'founder': _person(site_url, 'oliver', anker='#owner',
                           jobtitle='Inhaber und Gründer'),
    }
    if staedte:
        # Die Gebiete der Leistungsknoten gehoeren immer dazu (EIG358).
        namen = list(staedte) + [n for n in GEBIET_STAEDTE if n not in staedte]
        d['areaServed'] = _orte(namen) + _laender()
    return d


def webpage_schema(site_url, pfad, name, beschreibung=None,
                   speakable=(), mit_breadcrumb=False, geaendert=None):
    """Der ``WebPage``-Knoten je Seite - Traeger von ``speakable`` (G9).

    Bis zum 26.08.2026 hatte der Graph keinen Knoten fuer *die Seite selbst*:
    Er beschrieb die Firma, die Leistung und die Navigation, aber nicht das
    Dokument, auf dem der Besucher steht. ``speakable`` gehoert genau dorthin.

    ``speakable`` markiert die Passagen, die eine Sprachausgabe vorlesen soll -
    faktisch ein zusaetzliches Signal "das hier ist die Kernaussage". Uebergeben
    werden **CSS-Selektoren**, keine XPath-Ausdruecke: Ein Selektor bleibt
    lesbar und laesst sich gegen das gerenderte HTML pruefen. Genau das tut
    ``check_seo`` seit G9 - ein Selektor, der auf der Seite nichts trifft, ist
    eine Behauptung ueber Inhalt, den es nicht gibt.

    **Leer lassen ist erlaubt und richtig**, wo die Seite keine vorlesbare
    Kernaussage hat: Impressum, AGB, Formulare, Galerie. Ein ``speakable`` auf
    einer Rechtsseite waere kein Signal, sondern Rauschen.

    **``author`` (GE16, 04.09.2026): der Urheber des Textes, als Knoten.** Bis
    dahin beschrieb der Graph, *wovon* die Seite handelt (Service, FAQ, Ort) und
    *wozu* sie gehoert (``isPartOf``), aber nirgends, *wer* sie geschrieben hat.
    Fuer eine Antwortmaschine ist ein Text ohne benennbaren Urheber schwerer zu
    belegen als einer mit - und dieses Projekt hat den Urheber laengst als
    stabilen Knoten: ``…/#business``, den ``rw_head_schema`` auf **jeder** Seite
    in den Graph legt. Deshalb steht hier eine reine ``@id``-Referenz, wie bei
    ``provider`` und ``hiringOrganization``; ein zweites Mal getippter Firmenname
    waere die naechste Stelle, die bei der naechsten Umfirmierung stehenbleibt
    (Regel 25). ``LocalBusiness`` ist ein Untertyp von ``Organization`` und fuer
    ``author`` damit zulaessig.

    **Warum der Betrieb und nicht eine Person.** Wer die Saetze dieser Website
    verfasst hat, steht nirgends im Repository. Belegt ist nur, wer sie
    *verantwortet*: Das Impressum nennt Oliver Pohl nach § 55 Abs. 2 RStV. Das
    ist eine presserechtliche Rolle, keine Autorenzeile - die Seiten sind
    Unternehmenstexte ohne namentliche Zeichnung. Ein ``author`` auf ``#owner``
    haette also mehr behauptet als bekannt ist, und zwar ueber einen realen
    Menschen; dieselbe Zurueckhaltung wie bei ``sameAs`` (nur ein belegtes
    Profil) und beim Foto in ``_person()``.

    **``dateModified`` (D2, 06.09.2026): wann die Seite zuletzt geaendert
    wurde.** Bis dahin sagte die Sitemap das Google laengst, die Seite selbst
    aber niemandem - und der laufende Auftrag dieses Projekts ist GEO.
    Antwortmaschinen bevorzugen datierbare Aussagen; ``dateModified`` ist das
    eine Feld, mit dem eine Seite "dieser Preisstand ist von heute" sagt statt
    "irgendwann".

    ``geaendert`` ist ein ``datetime.date`` und wird als ``YYYY-MM-DD``
    ausgegeben - **niemals** ein lokalisiertes Format (Regel 3):
    ``isoformat()`` kennt kein Komma, ``LANGUAGE_CODE='de-de'`` kann daran
    nichts verderben.

    **Woher der Wert kommt, ist die eigentliche Entscheidung.**
    ``apps/core/sitemaps.py::lastmod_fuer_pfad`` liefert ihn - dieselbe
    Funktion, die auch das ``lastmod`` der Sitemap bestimmt. Zwei Listen fuer
    dasselbe Datum waeren Regel 12 in einer anderen Form, und sie waeren
    auseinandergelaufen; ``test_schema.py`` prueft die Gleichheit deshalb je
    Seitengattung gegen die ausgelieferte XML-Datei.

    **``dateModified`` ist eine Tatsachenbehauptung.** Wer sie an ein Datum
    haengt, das bei jedem Commit hochgezogen wird, hat ``date.today()`` durch
    die Hintertuer wieder eingefuehrt (Regel 22). Die Konstanten in
    ``data/lastmod.py`` werden **bei inhaltlichen Aenderungen** hochgezogen.
    Ohne ``geaendert`` bleibt das Feld weg - lieber keine Angabe als eine
    erfundene, dieselbe Zurueckhaltung wie beim ``datePublished`` einer
    Rezension ohne echtes Datum.
    """
    d = {
        '@context': 'https://schema.org',
        '@type': 'WebPage',
        '@id': f'{site_url}{pfad}#webpage',
        'url': f'{site_url}{pfad}',
        'name': name,
        'isPartOf': {'@id': f'{site_url}/#website'},
        'inLanguage': 'de-DE',
        'author': {'@id': f'{site_url}/#business'},
    }
    if beschreibung:
        d['description'] = beschreibung
    if geaendert:
        # isoformat() und nicht str(): Bei einem datetime waere sonst die
        # Uhrzeit mit drin, und die behauptet eine Genauigkeit, die es nicht
        # gibt. Schema.org erlaubt beides; YYYY-MM-DD ist die ehrliche Form.
        d['dateModified'] = geaendert.isoformat()[:10]
    if mit_breadcrumb:
        d['breadcrumb'] = {'@id': f'{site_url}{pfad}#breadcrumb'}
    if speakable:
        d['speakable'] = {
            '@type': 'SpeakableSpecification',
            'cssSelector': list(speakable),
        }
    return d


def breadcrumb_schema(site_url, name, pfad, zwischen=None):
    """``zwischen`` sind die Stufen zwischen Startseite und dieser Seite.

    Erlaubt ist ein einzelnes ``(Name, Pfad)`` oder eine Folge davon - damit
    ist die Liste beliebig tief (A16). Die Stadtseiten haengen unter
    Startseite > Standorte > Entrümpelung X, die Leistungsseiten unter
    Startseite > Dienstleistungen > Leistung.

    **Der sichtbare Brotkrumen muss dieselben Stufen zeigen.** Weichen beide
    voneinander ab, ist das ein Verstoss gegen Googles Regeln zu
    strukturierten Daten - dieselbe Fehlerklasse wie die FAQ auf den
    Stadtseiten, die im Schema sechs und auf der Seite fuenf Fragen hatte.
    """
    stufen = [('Startseite', '/')]
    if zwischen:
        # Ein einzelnes Paar ist ein Tupel aus zwei Strings; eine Folge von
        # Stufen enthaelt Tupel. Daran werden die beiden Faelle unterschieden.
        if isinstance(zwischen[0], str):
            stufen.append(tuple(zwischen))
        else:
            stufen.extend(tuple(z) for z in zwischen)
    stufen.append((name, pfad))
    return {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        # Seit G9 mit '@id': Der WebPage-Knoten verweist per 'breadcrumb' hierher,
        # statt die Liste ein zweites Mal zu fuehren. check_seo meldet einen
        # Verweis ins Leere - der Fall, an dem die JobPosting-Bloecke gescheitert
        # sind -, die beiden Stellen koennen also nicht auseinanderlaufen.
        '@id': f'{site_url}{pfad}#breadcrumb',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'name': n,
             'item': f'{site_url}{pf}'}
            for i, (n, pf) in enumerate(stufen, 1)
        ],
    }


def faq_schema(paare):
    """``paare`` ist eine Folge von (Frage, Antwort).

    Die Antworten duerfen im Quelltext ``<a href>`` tragen (sichtbar als Link,
    ``|safe`` in den Templates); das Schema bekommt **reinen Text** (Regel 12:
    dieselbe Quelle, gleicher Wortlaut ohne Auszeichnung).
    """
    return {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {'@type': 'Question', 'name': f,
             'acceptedAnswer': {'@type': 'Answer', 'text': strip_tags(a)}}
            for f, a in paare
        ],
    }


# ── Leistungen ──────────────────────────────────────────────────────────────

def _preis_angebot(objektart, name=None, beschreibung=None, site_url=None):
    """``Offer`` mit echtem ``priceSpecification`` (G10).

    **Was sichtbar auf der Seite steht und bis zum 25.08.2026 nicht im Schema:**
    Die Preistabelle nennt je Objektart **zwei** Zahlen - einen Richtwert je
    Quadratmeter (``rate``) und einen Mindestpreis (``min_preis``). Das Angebot
    trug nur den Mindestpreis, und zwar in einer nackten
    ``PriceSpecification``. Damit stand der eigentliche Preis - "44 € je m²" -
    maschinenlesbar nirgends, obwohl er die ganze Rechnung traegt.

    Jetzt eine ``UnitPriceSpecification``: ``price`` ist der Quadratmeterpreis,
    ``unitCode`` ``MTK`` (UN/CEFACT fuer Quadratmeter), ``referenceQuantity``
    sagt "je 1 m²", ``minPrice`` bleibt die Untergrenze. ``validFrom`` kommt aus
    ``_PREISSTAND_ISO`` - derselben Quelle, aus der die sichtbare Zeile
    "Preisstand: August 2026" entsteht (G12).

    **Die Falle, wegen der hier ``min`` und nicht ``min_txt`` steht** (Regel 1):
    ``preis_context()`` liefert beide Formen. ``min_txt`` ist ``'1.450'`` - mit
    Tausenderpunkt, weil das die Anzeigeform ist. In JSON waere das die Zahl
    1.450, also *ein Komma vier fuenf*. Hier kommen die Werte deshalb direkt aus
    ``_PER_QM_PREISE`` und sind ``int``; ``json.dumps`` schreibt sie unformatiert
    (Regel 3 - ``|unlocalize`` braucht es seit F5 nicht mehr, weil kein Template
    diese Zahl mehr anfasst).

    ``name``/``beschreibung`` fuellen ``itemOffered`` - gebraucht vom
    Leistungskatalog der Stadtseiten, damit dort nicht ein zweiter, halb
    gepflegter Angebotsbaustein entsteht.
    """
    werte = _PER_QM_PREISE[objektart]
    # **Zwei getrennte Spezifikationen, und das ist der Punkt.** Bis zum
    # 25.08.2026 standen 'price: 44' mit 'unitCode: MTK' und 'minPrice: 1450'
    # in **derselben** UnitPriceSpecification. schema.org definiert 'minPrice'
    # als Untergrenze **desselben** 'price' in **derselben** Einheit - gelesen
    # wurde also "mindestens 1.450 € je m²", das 33-fache des echten Preises.
    # Der Mindestpreis ist aber ein **Gesamtpreis** und keine Untergrenze je
    # Quadratmeter. Der 'description'-Text sagte das Richtige; Text wird nicht
    # ausgewertet.
    angebot = {
        '@type': 'Offer',
        'priceCurrency': 'EUR',
        'priceSpecification': [
            {
                # 1) Der Richtwert je Quadratmeter - die Zahl, nach der wirklich
                #    gerechnet wird. Roh aus pricing.py, nie aus 'rate_txt'.
                '@type': 'UnitPriceSpecification',
                'name': 'Richtwert je Quadratmeter',
                'priceCurrency': 'EUR',
                'price': werte['rate'],
                'unitCode': 'MTK',
                'referenceQuantity': {
                    '@type': 'QuantitativeValue', 'value': 1, 'unitCode': 'MTK'},
                'validFrom': '%s-01' % _PREISSTAND_ISO,
            },
            {
                # 2) Der Mindestpreis als Gesamtpreis des Auftrags. Eigene
                #    Spezifikation ohne 'unitCode' - genau deshalb.
                '@type': 'PriceSpecification',
                'name': 'Mindestpreis je Auftrag',
                'priceCurrency': 'EUR',
                'minPrice': werte['min_preis'],
                'validFrom': '%s-01' % _PREISSTAND_ISO,
                # Nur Beschreibungstext, kein Zahlenwert - hier ist der
                # Tausenderpunkt richtig und ungefaehrlich, weil er in einem
                # JSON-*String* steht und nicht in einer JSON-*Zahl*.
                'description': ('%s € je m², mindestens %s € je Auftrag'
                                % (werte['rate'], _euro(werte['min_preis']))),
            },
        ],
    }
    if site_url:
        # Wo das Angebot gilt. 'availableAtOrFrom' zeigt auf den einen
        # LocalBusiness-Knoten, den seit G1 jeder @graph mitfuehrt - eine
        # reine @id-Referenz reicht deshalb.
        angebot['availableAtOrFrom'] = {'@id': f'{site_url}/#business'}
        angebot['eligibleRegion'] = _laender()
    if name:
        dienst = {'@type': 'Service', 'name': name}
        if beschreibung:
            dienst['description'] = beschreibung
        angebot['itemOffered'] = dienst
    return angebot


def service_schema(site_url, anker, name, beschreibung, objektart=None):
    d = {
        '@type': 'Service',
        '@id': f'{site_url}/dienstleistungen/#{anker}',
        'name': name,
        'description': beschreibung,
        'provider': {'@id': f'{site_url}/#business'},
        'areaServed': _orte(GEBIET_STAEDTE) + _laender(),
    }
    if objektart:
        d['offers'] = _preis_angebot(objektart, site_url=site_url)
    return d


def service_page_schema(site_url, daten):
    """``Service`` fuer eine eigene Leistungsseite (A3).

    Nicht zu verwechseln mit ``service_schema()``: Das beschreibt einen Eintrag
    im Katalog auf ``/dienstleistungen/`` und haengt seine ``@id`` an *diese*
    Seite. Eine Leistung mit eigener URL braucht ihre eigene ``@id`` und ein
    ``url``-Feld, sonst zeigen zwei Knoten mit demselben Anker auf zwei Seiten.

    ``provider`` ist **seit G1 wieder eine reine ``@id``-Referenz.** Vorher trug
    der Knoten Name, Telefon und Adresse ein zweites Mal mit, weil Google
    ``@id`` ueber getrennte ``<script>``-Bloecke hinweg nicht aufloest. Seit
    ``rw_head_schema`` alles in **einen** ``@graph`` legt und den
    LocalBusiness-Knoten auf jeder Seite mitfuehrt, findet Google ihn - und die
    Doppelung ist genau die Sorte, die dieses Projekt anderswo mit grossem
    Aufwand abgeschafft hat.
    """
    d = {
        '@context': 'https://schema.org',
        '@type': 'Service',
        '@id': f"{site_url}/{daten['slug']}/#service",
        'name': daten['name'],
        'serviceType': daten['name'],
        'description': daten['seo_description'],
        'url': f"{site_url}/{daten['slug']}/",
        'provider': {'@id': f'{site_url}/#business'},
        'areaServed': _orte(GEBIET_STAEDTE) + _laender(),
    }
    if daten.get('objektart'):
        d['offers'] = _preis_angebot(daten['objektart'], site_url=site_url)
    # G13, Punkt 4: das Thema der Seite als Normdatensatz. Nur zwei der neun
    # Leistungen haben einen belegten Wikidata-Begriff - "Entruempelung" selbst
    # hat in Wikidata **keinen Sachartikel**, dort stehen zwei Fernsehfolgen.
    # Ein 'about' darauf verknuepfte die Seite mit einer Sitcom-Episode; die
    # Begruendung steht ausfuehrlich in data/wikidata.py.
    konzept = _wikidata.konzept_same_as(daten['slug'])
    if konzept:
        d['about'] = {'@type': 'Thing',
                      'name': _wikidata.konzept(daten['slug'])['label'],
                      'sameAs': konzept}
    return d


def matrix_page_schema(site_url, m):
    """``Service`` fuer eine Leistung-x-Stadt-Seite (A13).

    Unterschied zu ``service_page_schema()``: ``areaServed`` ist **eine**
    Stadt mit Koordinaten, nicht die Liste aller sechs. Genau das ist der
    Zweck der Seite - ein Service-Knoten, der sechs Staedte nennt, sagt zu
    "Haushaltsaufloesung Leipzig" nichts, was die allgemeine Seite nicht
    schon sagt.

    ``provider`` ist seit G1 eine reine ``@id``-Referenz - Begruendung in
    ``service_page_schema()``.
    """
    l, stadt = m['leistung'], m['stadt']
    d = {
        '@context': 'https://schema.org',
        '@type': 'Service',
        '@id': f"{site_url}{m['url']}#service",
        'name': m['h1'],
        'serviceType': l['name'],
        'description': m['seo_description'],
        'url': f"{site_url}{m['url']}",
        'provider': {'@id': f'{site_url}/#business'},
        'areaServed': {
            '@type': 'City',
            'name': stadt['name'],
            'address': _adresse(ort=stadt['name'], plz=stadt['zip'],
                                region=stadt['state'], strasse=None),
            'geo': _geo(stadt['lat'], stadt['lng']),
        },
    }
    if l.get('objektart'):
        d['offers'] = _preis_angebot(l['objektart'], site_url=site_url)
    return d


def howto_schema(site_url, daten):
    """``HowTo`` aus ``ablauf`` - derselbe Text, den die Seite sichtbar zeigt.

    Bewusst aus den Daten und nicht aus dem Template: Ein HowTo, dessen Schritte
    von den sichtbaren abweichen, ist ein Verstoss gegen Googles Regeln zu
    strukturierten Daten - dieselbe Falle wie bei der FAQ auf den Stadtseiten,
    wo Schema und Seite auf 6 gegen 5 Fragen auseinandergelaufen waren.
    """
    return {
        '@context': 'https://schema.org',
        '@type': 'HowTo',
        'name': f"Ablauf einer {daten['name']}",
        'description': (f"In {len(daten['ablauf'])} Schritten von der Anfrage bis "
                        f"zur besenreinen Übergabe."),
        'step': [
            {'@type': 'HowToStep', 'position': i,
             'name': s['titel'], 'text': s['text'],
             'url': f"{site_url}/{daten['slug']}/#ablauf"}
            for i, s in enumerate(daten['ablauf'], 1)
        ],
    }


def service_list_schema(site_url, leistungen):
    """``leistungen``: Folge von (anker, name, beschreibung, objektart|None).

    Seit dem 16.09.2026 eine **Liste von Knoten**: die ``ItemList`` und
    dahinter je Leistung ein ``Service`` auf oberster Ebene des Graphen. Die
    Liste verweist per ``@id`` darauf. Vorher steckten die Service-Knoten
    verschachtelt in der Liste - fuer Google gleichwertig, aber Werkzeuge,
    die nur die oberste Ebene lesen (die Messung, ``GE13``), sahen
    auf ``/dienstleistungen/`` keine einzige Leistung.
    """
    dienste = [dict(service_schema(site_url, *l),
                    **{'@context': 'https://schema.org'}) for l in leistungen]
    return [{
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': f'Entrümpelungs- und Sanierungsleistungen von {FIRMA}',
        'description': ('Alle Leistungen: Haushaltsauflösung, Wohnungsauflösung, '
                        'Kellerentrümpelung, Nachlassräumung, Gewerbeentrümpelung '
                        'und Sanierung.'),
        'url': f'{site_url}/dienstleistungen/',
        '@id': f'{site_url}/dienstleistungen/#leistungen',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i,
             'item': {'@id': d['@id']}}
            for i, d in enumerate(dienste, 1)
        ],
    }] + dienste


def entruempelung_service_schema(site_url, staedte):
    """``Service`` fuer den Hub ``/entrumpelung/`` (GE13, 16.09.2026).

    Die Seite handelt von einer Leistung in vielen Staedten; ``areaServed``
    nennt deshalb die Staedte des Kerngebiets aus ``cities.py``. Das Angebot
    ist die Kellerstaffel, weil sie den Einstiegspreis der Seite traegt
    ("Eine Kellerentrümpelung beginnt bei …").
    """
    return {
        '@context': 'https://schema.org',
        '@type': 'Service',
        '@id': f'{site_url}/entrumpelung/#service',
        'name': 'Entrümpelung in Mitteldeutschland',
        'serviceType': 'Entrümpelung',
        'url': f'{site_url}/entrumpelung/',
        'provider': {'@id': f'{site_url}/#business'},
        'areaServed': _orte(staedte),
        'offers': _preis_angebot('keller', site_url=site_url),
    }


# ── Stadtseiten ─────────────────────────────────────────────────────────────

def city_schema(site_url, city, city_slug):
    """``Service`` je Stadt, mit Leistungskatalog aus den echten Preisen.

    **Bis zum 25.09.2026 stand hier ein ``LocalBusiness``** mit eigener
    ``PostalAddress`` (Stadtname, PLZ der Innenstadt), der Stadtmitte als
    ``geo``, Oeffnungszeiten und Telefon - 57-mal, einmal je Stadtseite. Belegt
    ist genau **eine** Betriebsstaette (``data/firma.py``, Halle); ob es
    weitere gibt, ist offen (G6). Ein Betriebsknoten mit Adresse in Zwenkau
    oder Celle behauptet einen Standort, den die sichtbare Seite nicht nennt
    (Regel 12), und genau diese Bauart - ein Standort je Stadt ohne echte
    Anschrift - fuehrt Google in seinen Richtlinien fuer lokale Unternehmen
    als Verstoss. SEO-Audit 25.09.2026, K3.

    Jetzt sagt der Knoten, was die Seite sagt: **eine Leistung in dieser
    Stadt**, erbracht vom einen Betrieb (``provider`` -> ``/#business``), mit
    der Stadt samt Verwaltungskette als ``areaServed``. Die Angebote bleiben
    dieselben. Sobald G6 echte Adressen liefert, gehoert ein Standort als
    eigener ``LocalBusiness`` mit ``streetAddress`` wieder hierher - dann
    belegt.
    """
    katalog = [
        ('keller', f"Kellerentrümpelung {city['name']}",
         f"Kellerentrümpelung in {city['name']} zum Festpreis, inklusive Entsorgung."),
        ('wohnung', f"Wohnungsauflösung {city['name']}",
         f"Vollständige Wohnungsräumung in {city['name']} – besenreine Übergabe."),
        ('haus', f"Haushaltsauflösung {city['name']}",
         f"Komplette Haushaltsauflösung in {city['name']} – Möbel, Hausrat, Sperrmüll."),
        ('gewerbe', f"Gewerbeentrümpelung {city['name']}",
         f"Räumung von Büros, Lagern und Werkstätten in {city['name']}."),
    ]
    return {
        '@context': 'https://schema.org',
        '@type': 'Service',
        '@id': f"{site_url}/entrumpelung/{city_slug}/#service",
        'name': f"Entrümpelung und Haushaltsauflösung {city['name']}",
        'serviceType': 'Entrümpelung',
        'description': (f"Entrümpelung und Haushaltsauflösung in {city['name']} "
                        f"({city['region']}, {city['state']}) zum Festpreis nach "
                        f"Besichtigung, besenrein, auf Wunsch mit Entsorgungsnachweis."),
        'url': f"{site_url}/entrumpelung/{city_slug}/",
        # Das Bild, das die Seite auch zeigt (Regel 12) - nicht das Logo.
        'image': f'{site_url}{static("images/hero-banner.jpg")}',
        'provider': {'@id': f'{site_url}/#business'},
        # Die eigene Stadt zuerst und mit Verwaltungskette (G13), die
        # Nachbarorte danach - sie sind Einsatzgebiet, nicht Standort.
        'areaServed': ([_ort_mit_kette(city['name'], city['state'])]
                       + _orte(list(city['nearby']), city['state'])),
        'hasOfferCatalog': {
            '@type': 'OfferCatalog',
            'name': f"Entrümpelung {city['name']}",
            # Seit G10 derselbe Baustein wie auf den Leistungsseiten. Vorher
            # stand hier ein zweiter, schlankerer Angebotsblock - zwei Stellen
            # mit derselben Aufgabe sind genau die Konstruktion, an der in
            # diesem Projekt schon FAQ und Preise auseinandergelaufen sind.
            'itemListElement': [_preis_angebot(art, name, besch, site_url)
                                for art, name, besch in katalog],
        },
    }


def city_faq_paare(city):
    """Die FAQ einer Stadtseite - sichtbarer Text und Schema aus derselben Quelle.

    IS21 (02.10.2026): Von acht Fragen bleibt eine. Die uebrigen sieben (Kosten,
    Termin, Steuer, Ratenzahlung, "Wie wird es guenstiger?",
    Haushaltsaufloesung/Nachlass, Entsorgungsweg) standen mit ihren Satzbauten
    auf allen 57 Seiten fast woertlich gleich; zusammen mit dem Ablauf machten
    sie den groessten Teil der Schablone aus. Preise und Termin stehen schon im
    Antwortblock, in den Beispielen und im Hero; Steuer, Raten und
    Haushaltsaufloesung gehoeren auf die Leistungs- und Kostenseiten. Die
    Antwort "guenstiger" behauptete ausserdem fuer jede der 57 Staedte einen
    Standort-Nachlass von 5 %, den nur 25 Staedte bekommen (pricing.py,
    ``_STANDORT_RABATT_STAEDTE``).

    Was bleibt, ist die Frage, die nur diese Stadt beantworten kann: wohin das
    Geraeumte kommt. Die Antwort ist ``faq_zusatz`` aus city_lokal.py - belegter
    Ortsfakt (Wertstoffhof, Sperrmuellweg) ohne allgemeinen Satzbau davor.
    Sichtbare FAQ und FAQ-Schema lesen beide diese Liste (Regel 12).
    """
    zusatz = ((_city_lokal.lokal(city.get('slug', '')) or {}).get('faq_zusatz') or '')
    if not zusatz:
        return []
    return [(f"Wohin kommt das Geräumte aus {city['name']}?", zusatz)]


# ── Jobs ────────────────────────────────────────────────────────────────────

def job_schema(site_url, job):
    """JobPosting fuer eine Stellenanzeige.

    Zwei Dinge sind hier am 14.08.2026 korrigiert worden, beide gefunden im
    Google Rich Results Test und von **keinem** lokalen Werkzeug meldbar - die
    Bloecke waren gueltiges JSON und trotzdem als Stellenanzeige unbrauchbar:

    * **``datePosted`` fehlte.** Google fuehrt es als Pflichtfeld; ohne das war
      das Element ungueltig und auf allen drei Jobseiten von Rich Results
      ausgeschlossen. Der Wert kommt aus ``_JOB_DATA['datum']``.
    * **``hiringOrganization`` war nur eine ``@id``-Referenz.** Innerhalb eines
      ``@graph`` waere das richtig, aber die Jobseiten lieferten getrennte
      ``<script>``-Bloecke, und Google loest die Referenz dort nicht auf -
      gemeldet als „Feld ``name`` fehlt". Als Notbehelf trug der Knoten Name,
      ``sameAs`` und Logo ein zweites Mal.

    **Seit G1 ist es wieder die reine Referenz** - der Graph enthaelt den
    LocalBusiness-Knoten auf jeder Seite, also findet Google ihn. Damit ist die
    urspruengliche Absicht wiederhergestellt, ohne den Fehler zu wiederholen:
    ``check_seo`` loest ``@id`` jetzt selbst im Graph auf und schlaegt an, wenn
    das Ziel fehlt.
    """
    d = {
        '@context': 'https://schema.org',
        '@type': 'JobPosting',
        'title': job['title'],
        'description': job.get('seo_description') or job.get('teaser', ''),
        'datePosted': job['datum'],
        # EIG20/EIG82: Ablauf aus data/jobs.py (datum + LAUFZEIT_TAGE).
        'validThrough': _gueltig_bis(job),
        'identifier': {'@type': 'PropertyValue', 'name': FIRMA, 'value': job['slug']},
        'hiringOrganization': {'@id': f'{site_url}/#business'},
        'employmentType': job.get('employment_type', 'FULL_TIME'),
        'jobLocation': {'@type': 'Place', 'address': _adresse()},
        'directApply': True,
        'url': f"{site_url}/jobs/{job['slug']}/",
    }
    # Optional und nur, wenn die Anzeige eine Bruttoangabe macht - siehe
    # Kopfkommentar in data/jobs.py.
    g = job.get('gehalt')
    if g:
        d['baseSalary'] = {
            '@type': 'MonetaryAmount',
            'currency': 'EUR',
            'value': {'@type': 'QuantitativeValue', 'minValue': g['min'],
                      'maxValue': g['max'], 'unitText': g['einheit']},
        }
    return d


# ── Startseite ──────────────────────────────────────────────────────────────
# **Eine Quelle fuer sichtbare FAQ und Schema** (EIG145/GE36, 16.09.2026).
# Bis dahin standen die neun Antworten zweimal da: von Hand in home.html und
# hier "1:1 aus dem frueheren Template-Block". Alle neun wichen im Wortlaut
# ab, eine davon so weit, dass die Messung sie als "nicht sichtbar"
# meldete - der Tatbestand fuer Spam in strukturierten Daten. Seitdem rendert
# home.html genau diese Liste, und das Schema nimmt denselben Text ohne Tags.
#
# Die Antworten duerfen <strong> und <a> enthalten (sie stehen im Quelltext,
# nicht in einem Formular). Platzhalter kommen aus pricing.py, zusagen.py und
# cities.py - eine getippte Zahl waere Regel 1 bzw. 24.
#
# Drei Antworten sind beim Umbau berichtigt worden, weil sie anderen Stellen
# der Website widersprachen: "eigene Teams" in dreissig Staedten und
# "deutschlandweit" (belegt sind die Standortstaedte; llms.txt sagt "groessere
# Auftraege auf Anfrage auch ausserhalb"), "keine Aufpreise fuer Treppen"
# (pricing.py kennt den Stockwerkzuschlag - er ist im Festpreis enthalten,
# nicht erlassen) und "oft noch in derselben Woche" (keine Quelle in
# zusagen.py).
_LINK = ' style="color:var(--rw-orange);"'
HOME_FAQ = [
    ('Was kostet eine Entrümpelung?',
     'Die <strong>Entrümpelungskosten</strong> hängen von Objektgröße, '
     'Inventarmenge und Stockwerk ab. Wir geben immer einen <strong>Festpreis '
     'nach kostenloser Besichtigung</strong>, verbindlich im Angebot. '
     'Kellerentrümpelungen beginnen bei {k} €, eine Wohnungsauflösung bei '
     '{w} €, eine Haushaltsauflösung bei {h} € (Preisstand: {stand}). Den '
     '<a href="/preisangebot/"' + _LINK + '>Richtpreis können Sie hier '
     'berechnen</a>.'),
    ('Wie schnell kann eine Entrümpelung durchgeführt werden?',
     'Auf jede Anfrage antworten wir innerhalb von {antwort} '
     'per Telefon oder E-Mail. Die kostenlose Besichtigung ist '
     '{besichtigung} buchbar. Der Termin vor Ort richtet sich nach dem Ort: in {schnell_orte} '
     'in {schnell}, im übrigen Kerngebiet in {termin}. Bei dringenden '
     'Wohnungsübergaben oder Nachlassfällen sagen Sie uns die Frist gleich '
     'bei der Anfrage.'),
    ('In welchen Städten und Regionen sind Sie tätig?',
     'Wir räumen in {gesamt} Städten in Sachsen-Anhalt, Sachsen und '
     'Niedersachsen, {kern} davon im Kerngebiet, von Leipzig und Halle (Saale) über Magdeburg und '
     'Dresden bis Chemnitz und Hannover. Jede Stadt hat eine eigene Seite mit '
     'Entsorger, Sperrmüllregel und Termin vor Ort – die vollständige Liste '
     'steht unter <a href="/entrumpelung/"' + _LINK + '>Entrümpelung nach '
     'Städten</a>. Größere Aufträge übernehmen wir auf Anfrage auch außerhalb '
     'dieses Gebiets.'),
    ('Was passiert mit dem Inventar bei einer Haushaltsauflösung?',
     'Bei jeder Haushaltsauflösung sortieren wir sorgfältig: '
     'Verwertbares wird an Secondhand-Stellen weitergegeben, Elektroschrott '
     'fachgerecht entsorgt, der Rest umweltgerecht recycelt. '
     'Auf Wunsch erhalten Sie einen Entsorgungsnachweis für '
     'Ihre Unterlagen.'),
    ('Kann ich die Entrümpelung von der Steuer absetzen?',
     'Teilweise. Räumen und Tragen im eigenen, bewohnten Haushalt kann als '
     'haushaltsnahe Dienstleistung (§35a EStG) zählen – 20 % der Arbeitskosten, '
     'höchstens 4.000 € im Jahr. Die komplette Haushaltsauflösung führt das '
     'Bundesfinanzministerium als nicht begünstigt. Nötig ist eine Rechnung mit '
     'ausgewiesenen Arbeitskosten – sprechen Sie uns darauf an. Mehr im Ratgeber: '
     '<a href="/ratgeber/entruempelung-steuerlich-absetzen/"' + _LINK + '>'
     'Entrümpelung steuerlich absetzen</a>.'),
    ('Bieten Sie auch Nachlassräumungen und Erbschaftsräumungen an?',
     'Ja, Nachlassräumungen und Erbschaftsräumungen gehören zu '
     'unseren Kernleistungen. Wir gehen sensibel vor, dokumentieren alles und '
     'entlasten Angehörige vollständig – von der ersten Besichtigung bis zur '
     'besenreinen Übergabe der geräumten Immobilie.'),
    ('Führen Sie auch Gewerbeentrümpelungen und Büroräumungen durch?',
     'Ja. Wir übernehmen Gewerbeentrümpelungen von Büros, '
     'Lagerhallen, Werkstätten und Gastronomiebetrieben – termingerecht und '
     'mit entsprechenden Entsorgungsnachweisen für Ihre Buchhaltung. Auch '
     'großvolumige Räumungen sind kein Problem.'),
    ('Was ist im Festpreis alles enthalten?',
     'Den <strong>Festpreis für die Entrümpelung</strong> erhalten Sie '
     'bei der Besichtigung, verbindlich im Angebot. Stockwerk, Füllgrad und '
     'Sonderabfall fließen dabei in den Preis ein; was im Angebot '
     'enthalten ist, steht dort.'),
    ('Bieten Sie Ratenzahlung für die Entrümpelung an?',
     'Ratenzahlung gibt es auf Anfrage – ob nach '
     'einem Umzug, einer Erbschaft, einer Trennung oder in einer wirtschaftlich '
     'schwierigen Phase. Jede Anfrage wird persönlich und vertraulich '
     'geprüft. Sprechen Sie uns einfach an – wir finden gemeinsam eine '
     'faire Lösung. <a href="/dienstleistungen/#ratenzahlung"' + _LINK + '>'
     'Mehr zur Ratenzahlung →</a>'),
]


# (Anker, Name, Beschreibung, Objektart fuer den Mindestpreis)
LEISTUNGEN = [
    ('haushaltsaufloesung', 'Haushaltsauflösung',
     'Komplette Auflösung von Häusern und Wohnungen – Möbel, Elektrogeräte, Hausrat. Besenreine Übergabe, Entsorgungsnachweis auf Wunsch. Festpreis nach kostenloser Besichtigung.', 'haus'),
    ('wohnungsaufloesung', 'Wohnungsauflösung',
     'Vollständige Räumung von Wohnungen mit besenreiner Übergabe direkt an den Vermieter, zum Festpreis nach Besichtigung.', 'wohnung'),
    ('kellerentruempelung', 'Kellerentrümpelung',
     'Professionelle Kellerentrümpelung mit vollständiger Entsorgung und Reinigung. Festpreis nach Besichtigung.', 'keller'),
    ('nachlassraeumung', 'Nachlassräumung & Erbschaftsräumung',
     'Einfühlsame Nachlassräumung und Erbschaftsräumung mit vollständiger Dokumentation. Wir entlasten Angehörige von A bis Z – von der Besichtigung bis zur besenreinen Übergabe.', None),
    ('gewerbeentruempelung', 'Gewerbeentrümpelung & Büroräumung',
     'Räumung von Büros, Lagerhallen, Werkstätten und Gastronomiebetrieben – termingerecht mit Entsorgungsnachweisen.', 'gewerbe'),
    ('sanierung', 'Sanierung & Renovierung',
     'Malerarbeiten, Tapezieren, Bodenbeläge, Sanitär & Bad, Kleinreparaturen und Komplettrenovierung – alles aus einer Hand.', None),
]


# (Anker, Name, Beschreibung)
# Seit dem 02.10.2026 **Einsatzgebiete**, keine Standorte: Belegt ist nur die
# Betriebsstaette Halle (data/firma.py). "Hauptstandort mit groesstem Team",
# eigene Teams je Stadt und "kurzfristig" sind entfernt (keine Quelle).
STANDORTE = [
    ('leipzig', 'Entrümpelung Leipzig und Halle (Saale)',
     'Entrümpelung, Haushaltsauflösung und Wohnungsauflösung in Leipzig und Halle (Saale). Die Betriebsstätte liegt in Halle.'),
    ('magdeburg', 'Entrümpelung Magdeburg',
     'Wohnungsauflösung, Gewerbeentrümpelung und Kellerentrümpelung in Magdeburg und Sachsen-Anhalt.'),
    ('hannover', 'Entrümpelung Hannover',
     'Haushaltsräumung, Nachlassräumung und Entrümpelung in Hannover und Niedersachsen.'),
    ('dresden', 'Entrümpelung Dresden und Chemnitz',
     'Haushaltsauflösung, Erbschaftsräumung und Gewerberäumung in Dresden, Chemnitz und der Region Sachsen.'),
]
# Welche Orte je Einsatzgebiet gemeint sind (nur Orte aus GEBIET_STAEDTE).
_STANDORT_ORTE = {
    'leipzig': ('Leipzig', 'Halle (Saale)'),
    'magdeburg': ('Magdeburg',),
    'hannover': ('Hannover',),
    'dresden': ('Dresden', 'Chemnitz'),
}


def home_faq_paare(preise, preisstand):
    """Die FAQ der Startseite als (Frage, Antwort-HTML) - fuer home.html."""
    from .data.cities import _CITY_DATA
    from .data import zusagen as _z
    werte = {
        'k': preise['keller']['min_txt'],
        'w': preise['wohnung']['min_txt'],
        'h': preise['haus']['min_txt'],
        'stand': preisstand,
        'antwort': _z.ANTWORT,
        'besichtigung': _z.TERMIN_FRUEHESTENS,
        'schnell': _z.TERMIN_SCHNELL,
        'schnell_orte': _z.TERMIN_SCHNELL_ORTE,
        'termin': _z.TERMIN_REGEL,
        'kern': sum(1 for c in _CITY_DATA.values() if not c.get('randgebiet')),
        # EIG252/EIG267: dieselbe Zahl wie "Alle … Städte" im Footer.
        'gesamt': len(_CITY_DATA),
    }
    return [(f, a.format(**werte)) for f, a in HOME_FAQ]


def home_faq_schema(preise, preisstand):
    """FAQPage der Startseite - derselbe Text wie sichtbar, ohne Tags."""
    from django.utils.html import strip_tags
    return faq_schema([(f, strip_tags(a))
                       for f, a in home_faq_paare(preise, preisstand)])

def standorte_schema(site_url):
    """Die ``ItemList`` der Einsatzgebiete fuer ``/standorte/``.

    Eine Liste von **Leistungen je Einsatzgebiet** (``Service`` mit
    ``areaServed``), kein ``LocalBusiness`` je Ort. Belegt ist eine
    Betriebsstaette (``data/firma.py``); ein Betriebsknoten mit Halles Adresse
    unter dem Namen "Entruempelung Hannover" behauptete vier Niederlassungen,
    und mehrere Adressen zu behaupten ist bei Google ein Sperrgrund.
    """
    return {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': f'{FIRMA} – Einsatzgebiet',
        'description': ('Einsatzgebiet in Sachsen-Anhalt, Sachsen und Niedersachsen: '
                        'Halle, Leipzig, Magdeburg, Dresden, Chemnitz und Hannover. '
                        'Die Betriebsstätte liegt in Halle (Saale).'),
        'url': f'{site_url}/standorte/',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'item': {
                '@type': 'Service',
                '@id': f'{site_url}/standorte/#{anker}',
                'name': name, 'description': besch,
                'serviceType': 'Entrümpelung',
                'url': f'{site_url}/standorte/',
                'provider': {'@id': f'{site_url}/#business'},
                'areaServed': _orte(_STANDORT_ORTE[anker]),
            }}
            for i, (anker, name, besch) in enumerate(STANDORTE, 1)
        ],
    }


# ── Galerie ─────────────────────────────────────────────────────────────────

def _absolute_bild_url(site_url, url):
    """Eine Bild-URL absolut machen - JSON-LD kennt keine relativen Pfade.

    Cloudinary liefert bereits absolute URLs; ohne ``CLOUDINARY_URL`` (lokal
    und im Testlauf) steht dort ein ``/media/…``-Pfad.
    """
    text = str(url or '')
    if not text or text.startswith(('http://', 'https://')):
        return text
    return f'{site_url}{text}'


#: Wo Nutzungsbedingungen und Lizenzanfrage stehen - ein Abschnitt im
#: Impressum, ``id="bildrechte"``. ``test_schema.py`` prueft, dass es ihn gibt.
BILDRECHTE_PFAD = '/impressum/#bildrechte'


def bild_rechte(site_url):
    """Die Rechteangaben, die Google an **jedem** ``ImageObject`` erwartet.

    Anlass ist die Search-Console-Meldung vom 16.09.2026, „Bild-Metadaten
    für strukturierte Daten“: fünf Probleme an den Galeriebildern -
    ``copyrightNotice``, ``license``, ``acquireLicensePage`` und
    ``creditText`` fehlten, und ``creator`` hatte einen „ungültigen
    Objekttyp“.

    **Warum ``creator`` einen ``@type`` braucht, obwohl der Knoten im Graph
    steht.** Bis dahin war ``creator`` eine reine ``@id``-Referenz auf
    ``…/#business`` - fuer ``provider`` und ``author`` genuegt das, weil
    Google diese Verweise im ``@graph`` aufloest. Die Pruefung der
    Bild-Metadaten tut es erkennbar nicht: Sie liest ein Objekt ohne Typ und
    meldet es. Deshalb steht hier ``Organization`` **mit** derselben ``@id`` -
    in JSON-LD verschmelzen beide Angaben zu einem Knoten, und
    ``LocalBusiness`` ist ein Untertyp von ``Organization``. Name und URL
    kommen mit, damit das Objekt auch ohne Aufloesung vollstaendig ist.

    **Was die vier Rechtefelder behaupten - und warum das belegt ist.** Die
    ausgezeichneten Bilder sind das Firmenlogo und die Vorher-Nachher-Fotos
    aus dem CMS, beides eigener Bestand des Betriebs (siehe
    ``galerie_bilder_schema``). ``copyrightNotice`` und ``creditText`` nennen
    deshalb den Betrieb. ``license`` und ``acquireLicensePage`` zeigen auf
    den Abschnitt „Bildrechte“ im Impressum: Dort steht, dass alle Rechte
    vorbehalten sind und wie man eine Nutzung anfragt. Das ist die
    gesetzliche Grundlage nach dem Urheberrechtsgesetz und keine neue
    Lizenz - bis zum 16.09.2026 fehlten die Felder mit der Begruendung, es
    gebe keine Lizenzseite. Die gibt es jetzt, und sie sagt nur, was
    ohnehin gilt.

    Das Jahr (``copyrightYear``) steht bewusst nicht hier: Die Fotos stammen
    aus verschiedenen Auftraegen, ein einziges Jahr waere fuer die meisten
    falsch.
    """
    return {
        'creator': {'@type': 'Organization', '@id': f'{site_url}/#business',
                    'name': FIRMA, 'url': site_url},
        'creditText': FIRMA,
        'copyrightNotice': f'© {FIRMA}',
        'copyrightHolder': {'@id': f'{site_url}/#business'},
        'license': f'{site_url}{BILDRECHTE_PFAD}',
        'acquireLicensePage': f'{site_url}{BILDRECHTE_PFAD}',
    }


def galerie_bilder_schema(site_url, bilder):
    """Ein ``ImageObject`` je **sichtbarem** Galeriebild (D5, 06.09.2026).

    Die Vorher-Nachher-Fotos sind der einzige originaere Bildbestand dieses
    Betriebs und standen bis zum 06.09.2026 in keinem Schema - der einzige
    ``ImageObject``-Knoten der ganzen Website war das Logo im
    LocalBusiness-Knoten.

    ``bilder`` ist **dieselbe Liste**, aus der ``galerie.html`` die
    ``<figure>``-Elemente rendert (Regel 12: sichtbarer Inhalt und Schema aus
    einer Quelle). Damit beschreibt der Graph genau die Bilder der gerade
    ausgelieferten Seite - beim Blaettern also die von Seite 2, nicht den
    Gesamtbestand. Die Bildsitemap meldet den Gesamtbestand; das ist eine
    andere Aussage an einen anderen Adressaten und bewusst nicht dieselbe
    Liste.

    ``caption`` ist ``AktuellesBild.alt_text()``, also zeichengleich mit dem
    ``alt``-Attribut daneben. ``creator`` ist der LocalBusiness-Knoten, der
    seit G1 im Graph **jeder** Seite steht - die Fotos sind im Betrieb
    entstanden, und das ist die einzige Urheberangabe, die dieses Repository
    belegen kann. Seit dem 16.09.2026 kommen ``creator`` und die vier
    Rechtefelder aus ``bild_rechte()``; die Begruendung steht dort.

    Was hier weiterhin bewusst NICHT steht: ``datePublished``. Ein
    Aufnahmedatum hat ``AktuellesBild`` nicht - das Datum des Beitrags ist der
    Tag des Auftrags, nicht der Tag der Aufnahme. Erfundene Felder sind hier
    derselbe Fehler wie ein ``sameAs`` ohne Beleg (G5).
    """
    knoten = []
    for bild in bilder or ():
        url = _absolute_bild_url(site_url, bild.get('url'))
        if not url:
            continue
        d = {
            '@context': 'https://schema.org',
            '@type': 'ImageObject',
            'contentUrl': url,
            **bild_rechte(site_url),
        }
        # Ohne gepflegte Bildbeschreibung faellt alt_text() auf den
        # Beitragstitel zurueck - der ist als caption richtig, aber leer darf
        # das Feld nie werden.
        if bild.get('alt'):
            d['caption'] = bild['alt']
        knoten.append(d)
    return knoten


# ── Ratgeber: Article und Blog (GE15, 10.09.2026) ───────────────────────────
#
# Der Graph beschrieb bis hierher die Firma (LocalBusiness), die Leistung
# (Service), die Navigation (BreadcrumbList), die Fragen (FAQPage), den Ablauf
# (HowTo) und das Dokument (WebPage). Was fehlte, war der Knoten fuer einen
# **Text**: Zwei Seiten dieser Website sind Ratgeber und keine Verkaufsseiten -
# /entruempelung-kosten/ erklaert auf 3.000 Woertern, wie ein Preis entsteht,
# und /aktuelles/ traegt zwoelf Berichte aus abgeschlossenen Auftraegen.
#
# Warum das mehr ist als ein weiterer Typname: ``Article`` ist der einzige
# Knoten, der ``datePublished`` **und** ``author`` zugleich fuehrt. Fuer eine
# Antwortmaschine ist das die Kombination, an der sie einen Text datiert und
# einem Urheber zuordnet - genau die beiden Angaben, die dieses Projekt seit
# D2 (dateModified) und GE16 (author) einzeln schon macht, aber nie an einem
# Textknoten.
#
# WAS DIESE BEIDEN BAUSTEINE NICHT LEISTEN
# ----------------------------------------
# * **Sie machen aus keiner Verkaufsseite einen Ratgeber.** Welche Seite hier
#   ausgezeichnet wird, entscheidet ``services.RATGEBER_SEITEN`` bzw. der Typ
#   des CMS-Beitrags - nicht dieser Baustein. Ein ``Article`` ueber einer
#   Leistungsseite waere dieselbe Sorte Behauptung wie ein ``sameAs`` ohne
#   Beleg (G5): formal gueltig, inhaltlich falsch.
# * **Sie pruefen nicht, ob die ``headline`` auf der Seite steht.** Regel 12
#   verlangt das; erzwungen wird es dadurch, dass die Aufrufer den sichtbaren
#   ``h1``-Text bzw. ``AktuellesPost.titel`` uebergeben, nicht einen zweiten
#   getippten Satz.
# * **Sie erfinden kein Datum.** Ohne belegtes ``veroeffentlicht`` faellt
#   ``datePublished`` weg, und dann faellt der ganze Knoten weg - ein
#   ``Article`` ohne Erscheinungsdatum ist fuer den Zweck wertlos.

def _citation(quellen):
    """``citation``-Eintraege aus den Quellen eines Ratgebers (GE43).

    Dieselbe Liste, aus der der sichtbare Beleg am Absatzende entsteht
    (``data/ratgeber.py``) - Regel 12. Bewusst ``CreativeWork`` und nicht
    ``Legislation``: Der Typ ist in schema.org noch im Entwurf, und ein Typ,
    den kein Auswerter kennt, sagt weniger als ein allgemeiner mit Name,
    Adresse und Herausgeber.
    """
    return [{'@type': 'CreativeWork', 'name': q['name'], 'url': q['url'],
             'publisher': {'@type': 'Organization', 'name': q['herausgeber']}}
            for q in (quellen or [])]


def article_schema(site_url, pfad, headline, beschreibung=None,
                   veroeffentlicht=None, geaendert=None, bild=None,
                   quellen=None):
    """Der ``Article``-Knoten einer Ratgeberseite (GE15).

    ``veroeffentlicht`` und ``geaendert`` sind ``datetime.date`` und kommen aus
    ``apps/core/data/lastmod.py`` - derselben Quelle, aus der die Sitemap ihr
    ``lastmod`` und der ``WebPage``-Knoten sein ``dateModified`` holen. Zwei
    Listen fuer dasselbe Datum waeren Regel 12 in anderer Form.

    **Ohne ``veroeffentlicht`` gibt die Funktion ``None`` zurueck.** Das ist
    keine Bequemlichkeit: ``datePublished`` ist das eine Feld, das ein Article
    von einer beliebigen WebPage unterscheidet. Wer es schaetzt, hat den Knoten
    entwertet und behauptet zugleich etwas Pruefbares, das nicht stimmt.

    ``author`` und ``publisher`` zeigen per ``@id`` auf ``…/#business`` - den
    LocalBusiness-Knoten, den ``rw_head_schema`` seit G1 in **jeden** Graph
    legt. Dieselbe Begruendung wie bei ``webpage_schema``: Wer die Saetze
    dieser Website verfasst hat, steht nirgends im Repository; belegt ist nur
    der Betrieb als Urheber. Ein ``author`` auf einen realen Menschen waere
    mehr behauptet als bekannt ist.

    ``mainEntityOfPage`` verknuepft den Text mit dem Dokument, auf dem er
    steht. Ohne diese Kante stehen zwei Knoten nebeneinander im Graph, und
    Google muss raten, ob der Article diese Seite meint oder eine andere.
    """
    if not veroeffentlicht:
        return None
    d = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        '@id': f'{site_url}{pfad}#article',
        'headline': headline,
        'url': f'{site_url}{pfad}',
        'mainEntityOfPage': {'@id': f'{site_url}{pfad}#webpage'},
        'isPartOf': {'@id': f'{site_url}/#website'},
        'inLanguage': 'de-DE',
        # isoformat() und nicht str(): Bei einem datetime waere die Uhrzeit
        # mit drin, und die behauptet eine Genauigkeit, die es nicht gibt.
        'datePublished': veroeffentlicht.isoformat()[:10],
        'author': {'@id': f'{site_url}/#business'},
        'publisher': {'@id': f'{site_url}/#business'},
    }
    if beschreibung:
        d['description'] = beschreibung
    # Googles Empfehlung fuer Article (nicht Pflicht). Eine reine URL, kein
    # ImageObject - die Bildrechte stehen am Vorschaubild nicht zur Debatte,
    # und ein ImageObject ohne sie waere genau der Befund vom 16.09.2026.
    if bild:
        d['image'] = bild
    # Ein 'dateModified' vor dem 'datePublished' ist ein Widerspruch - er
    # entstuende lautlos, sobald jemand ein Erscheinungsdatum nachtraegt, das
    # neuer ist als die Konstante der Seitengattung.
    if geaendert and geaendert >= veroeffentlicht:
        d['dateModified'] = geaendert.isoformat()[:10]
    # GE43: Woher der Text sein Recht hat - maschinenlesbar. Der Leser sieht
    # denselben Beleg als Satz am Ende des Abschnitts.
    if quellen:
        d['citation'] = _citation(quellen)
    return d


def blog_schema(site_url, pfad, name, beschreibung, beitraege):
    """``Blog`` plus je ein ``BlogPosting`` fuer /aktuelles/ (GE15).

    ``beitraege`` ist **dieselbe Liste**, aus der ``aktuelles.html`` die
    ``<article>``-Karten rendert (Regel 12) - beim Blaettern also die Beitraege
    von Seite 2, nicht der Gesamtbestand. Dieselbe Entscheidung wie bei
    ``galerie_bilder_schema``.

    Erwartet wird je Beitrag ein ``dict`` mit ``titel``, ``datum``, optional
    ``text``, ``bild`` und ``autor``. Die Aufbereitung steht in der View, damit
    dieser Baustein ohne Datenbank testbar bleibt.

    WAS HIER BEWUSST NICHT PASSIERT
    -------------------------------
    * **Kundenzitate werden nicht zu Artikeln.** Ein Beitrag vom Typ ``zitat``
      ist eine Kundenstimme, kein Text des Betriebs; ihn als ``BlogPosting``
      mit ``author`` = Ruempelwerk auszugeben, waere eine falsche Urheberangabe
      - und Bewertungsinhalt kommt in diesem Projekt nicht ins Schema
      (Entscheidung 06.10.2026). Aussortiert wird in der View, siehe dort.
    * **Kein ``articleBody``.** Der Volltext steht schon im HTML daneben; ihn
      ein zweites Mal in JSON zu schreiben, kostet auf einer Seite mit zehn
      Beitraegen mehrere KiB und sagt Google nichts Neues (Seitengewicht,
      Schwelle 170 KiB). ``description`` traegt den Anfang des Textes.
    * **Keine eigene Adresse je Beitrag.** Die Beitraege haben keine
      Detailseite; ``url`` zeigt deshalb auf ``/aktuelles/`` selbst. Ein
      erfundener Fragmentlink waere ein Sprungziel, das es im HTML nicht gibt.

    ``datePublished`` und ``dateModified`` tragen **denselben** Wert:
    ``AktuellesPost`` fuehrt genau ein inhaltliches Datum (``datum``).
    ``erstellt_am`` ist der Zeitpunkt des Hochladens, nicht der einer
    Aenderung - es als ``dateModified`` auszugeben, waere eine Behauptung
    ueber eine Ueberarbeitung, die nie stattgefunden hat.
    """
    posts = []
    for b in beitraege or ():
        datum = b.get('datum')
        titel = (b.get('titel') or '').strip()
        if not datum or not titel:
            continue
        tag = datum.isoformat()[:10]
        d = {
            '@context': 'https://schema.org',
            '@type': 'BlogPosting',
            '@id': f'{site_url}{pfad}#beitrag-{b["id"]}',
            'headline': titel,
            'url': f'{site_url}{pfad}',
            'mainEntityOfPage': {'@id': f'{site_url}{pfad}#webpage'},
            'isPartOf': {'@id': f'{site_url}{pfad}#blog'},
            'inLanguage': 'de-DE',
            'datePublished': tag,
            'dateModified': tag,
            'publisher': {'@id': f'{site_url}/#business'},
        }
        # Der Autor steht im CMS-Feld und ist damit belegt - anders als bei
        # den uebrigen Seiten dieser Website, deren Verfasser nirgends
        # festgehalten ist. Als vollstaendiger Knoten und nicht als '@id':
        # Die Person-Knoten der vier Regionalleiter stehen nur auf
        # /ueber-uns/, ein Verweis von hier liefe ins Leere (check_seo prueft
        # '@id'-Verweise ohne Ziel).
        if b.get('autor'):
            d['author'] = {'@type': 'Person', 'name': b['autor']}
        else:
            d['author'] = {'@id': f'{site_url}/#business'}
        if b.get('text'):
            d['description'] = b['text']
        bild = _absolute_bild_url(site_url, b.get('bild'))
        if bild:
            d['image'] = bild
        posts.append(d)
    if not posts:
        # Ohne Beitraege ist ein Blog-Knoten eine Behauptung ueber Inhalt, den
        # es auf dieser Seite nicht gibt - dieselbe Ueberlegung wie bei der
        # leeren Bildsitemap, die sich lieber ganz abmeldet.
        return []
    blog = {
        '@context': 'https://schema.org',
        '@type': 'Blog',
        '@id': f'{site_url}{pfad}#blog',
        'name': name,
        'url': f'{site_url}{pfad}',
        'inLanguage': 'de-DE',
        'publisher': {'@id': f'{site_url}/#business'},
        'blogPost': [{'@id': p['@id']} for p in posts],
    }
    if beschreibung:
        blog['description'] = beschreibung
    return [blog] + posts


def beitrag_schema(site_url, pfad, titel, datum, text=None, bild=None, autor=None):
    """``BlogPosting`` fuer die EIGENE Adresse eines Beitrags (Bauplan §7).

    Anders als ``blog_schema`` (ein Eintrag je Beitrag, ``url`` zeigt auf die
    **Liste** ``/aktuelles/``, weil es dort keine Einzeladresse gibt): Dieser
    Knoten steht auf der Einzelseite ``/aktuelles/<jahr>/<slug>/`` selbst, die
    seit Migration 0023 fuer importierte GBP-Beitraege existiert. ``url`` und
    ``mainEntityOfPage`` zeigen deshalb auf **diese** Seite, nicht auf die
    Liste - sonst behauptete das Schema eine Adresse, die im HTML nicht steht
    (Regel 12).

    ``datum`` ist ``AktuellesPost.datum`` (das inhaltliche Datum des
    Beitrags) - dasselbe Feld, das die Liste sortiert. Kein ``dateModified``:
    ein importierter Beitrag wird nicht nachtraeglich bearbeitet, ihn zu
    behaupten waere eine Ueberarbeitung, die nie stattgefunden hat (dieselbe
    Regel wie in ``blog_schema``).
    """
    tag = datum.isoformat()[:10]
    d = {
        '@context': 'https://schema.org',
        '@type': 'BlogPosting',
        '@id': f'{site_url}{pfad}#beitrag',
        'headline': titel,
        'url': f'{site_url}{pfad}',
        'mainEntityOfPage': {'@id': f'{site_url}{pfad}#webpage'},
        'isPartOf': {'@id': f'{site_url}/aktuelles/#blog'},
        'inLanguage': 'de-DE',
        'datePublished': tag,
        'dateModified': tag,
        'publisher': {'@id': f'{site_url}/#business'},
    }
    if autor:
        d['author'] = {'@type': 'Person', 'name': autor}
    else:
        d['author'] = {'@id': f'{site_url}/#business'}
    if text:
        d['description'] = text
    bild_url = _absolute_bild_url(site_url, bild) if bild else ''
    if bild_url:
        d['image'] = bild_url
    return d


# ── Ratgeber: Uebersicht und Glossar (T4, 16.09.2026) ───────────────────────

def ratgeber_hub_schema(site_url, gruppen, quellen=None):
    """``CollectionPage`` mit ``ItemList`` fuer ``/ratgeber/`` (T4).

    ``gruppen`` ist dieselbe Liste, aus der die Karten der Seite entstehen
    (``ratgeber.hub()['gruppen']``) - Regel 12. Die Eintraege verweisen per
    ``@id`` auf die ``Article``-Knoten ihrer Seiten; dort stehen sie mit
    Datum und Autor, hier nur als Verzeichnis.
    """
    eintraege = [e for g in gruppen for e in g['eintraege']]
    knoten = {
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        '@id': f'{site_url}/ratgeber/#sammlung',
        'name': f'Ratgeber – {FIRMA}',
        'url': f'{site_url}/ratgeber/',
        'isPartOf': {'@id': f'{site_url}/#website'},
        'about': {'@id': f'{site_url}/#business'},
        'inLanguage': 'de-DE',
        'mainEntity': {
            '@type': 'ItemList',
            '@id': f'{site_url}/ratgeber/#artikel',
            'numberOfItems': len(eintraege),
            'itemListElement': [
                {'@type': 'ListItem', 'position': i, 'name': e['titel'],
                 'url': f"{site_url}{e['url']}"}
                for i, e in enumerate(eintraege, 1)
            ],
        },
    }
    # GE43: Die Uebersicht nennt die Normen, auf die ihre Artikel sich
    # stuetzen - dieselbe Liste, aus der ihr sichtbarer Satz entsteht.
    if quellen:
        knoten['citation'] = _citation(quellen)
    return knoten


def glossar_schema(site_url, eintraege):
    """``DefinedTermSet`` aus dem sichtbaren Glossar von ``/ratgeber/``.

    Jeder Begriff zeigt per ``url`` auf sein Sprungziel in der ``<dl>`` -
    ``anker`` kommt aus ``ratgeber.glossar_anker()``, derselben Funktion,
    die das ``id``-Attribut setzt.
    """
    satz = f'{site_url}/ratgeber/#glossar'
    return {
        '@context': 'https://schema.org',
        '@type': 'DefinedTermSet',
        '@id': satz,
        'name': 'Glossar Entrümpelung und Haushaltsauflösung',
        'url': satz,
        'inLanguage': 'de-DE',
        'publisher': {'@id': f'{site_url}/#business'},
        'hasDefinedTerm': [
            {'@type': 'DefinedTerm',
             '@id': f"{site_url}/ratgeber/#{e['anker']}",
             'name': e['begriff'], 'description': e['text'],
             'url': f"{site_url}/ratgeber/#{e['anker']}",
             'inDefinedTermSet': {'@id': satz}}
            for e in eintraege
        ],
    }
