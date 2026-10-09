"""Die sechs Teil-Sitemaps und der Index - jede URL aus den Daten, keine Liste.

``MainSitemap`` (feste Seiten), ``ServiceSitemap`` (neun Leistungsseiten),
``CitySitemap`` (54 Stadtseiten), ``MatrixSitemap`` (Leistung x Stadt),
``JobsSitemap`` (drei Stellen) und ``ImageSitemap`` (die eigenen Fotos).
Getrennt sind sie, weil die Search Console Indexierungsquoten **je Sitemap**
zeigt - in einer Sammeldatei waere nicht ablesbar, ob die neuen Seiten
ankommen.

Drei Regeln haengen an dieser Datei:

* ``impressum``/``datenschutz``/``agb`` stehen nirgends hier - sie sind
  ``noindex``, und eine ``noindex``-URL in der Sitemap ist ein
  GSC-Fehler (Regel 21). Dasselbe gilt fuer weiterleitende Adressen.
* ``lastmod`` kommt nie aus ``date.today()`` (Regel 22), sondern aus
  ``data/lastmod.py`` - und fuer die beiden CMS-Seiten aus ``max(erstellt_am)``
  der veroeffentlichten Beitraege.
* Kein Rueckfall ist still: Faellt eine Abfrage aus, schreibt die Stelle eine
  Warnung. Von aussen sieht ein fehlender Abschnitt sonst wie eine
  Entscheidung aus.

``datetime`` wird hier seit D2 nicht mehr gebraucht: Jedes feste Datum steht in
``apps/core/data/lastmod.py``, jedes bewegliche kommt aus der Datenbank. Wer
hier wieder einen Kalender braucht, prueft vorher Regel 22.
"""

import logging
from django.contrib.sitemaps import Sitemap
from django.conf import settings
from django.urls import reverse
from .data import _CITY_DATA, _JOB_DATA  # seit F6 aus data/, nicht mehr aus views
from .data.services import _SERVICE_DATA
from .data.matrix import matrix_kombinationen
# Seit D2 (06.09.2026) stehen die vier lastmod-Konstanten nicht mehr hier,
# sondern in apps/core/data/lastmod.py - der WebPage-Knoten braucht dieselben
# Daten, und zwei Listen fuer dieselbe Aussage laufen auseinander (Regel 12).
# Die Namen bleiben hier importiert, weil check_seo._pruefe_lastmod sie per
# getattr(sm, name) sucht und test_sitemaps.py sie ueber das Modul liest.
# Gemeint sind CONTENT_LASTMOD, CITY_LASTMOD, SERVICE_LASTMOD und
# MATRIX_LASTMOD: Im Quelltext dieser Datei steht keiner von ihnen noch
# einmal, sie sehen deshalb wie vergessene Einfuhren aus. Wer sie entfernt,
# nimmt der lastmod-Warnung von check_seo die Zahlen, gegen die sie prueft -
# und der Lauf bleibt gruen, weil getattr dann schlicht nichts findet.
from .data.lastmod import (CONTENT_LASTMOD, CITY_LASTMOD, SERVICE_LASTMOD,
                           MATRIX_LASTMOD, CMS_PFADE,
                           fuer_pfad as _lastmod_aus_daten)
# Die eigenen Fotos der festen Seiten (TS19, 06.09.2026) - bis dahin kannte
# die Bildsitemap nur den CMS-Bestand.
from .data.bilder import (SEITEN_BILDER, HERO_BILD, HERO_TITEL_STADT,
                          HERO_TITEL_LEISTUNG, HERO_TITEL_MATRIX)


# Ohne www – muss zu _CANONICAL_SITE_URL und der Middleware passen, sonst
# listet die Sitemap URLs, die sofort per 301 woandershin zeigen.
_PRODUCTION_DOMAIN = 'ruempelwerk-mitteldeutschland.de'

_log_sitemap = logging.getLogger('apps.core')


def _canonical_domain():
    url = getattr(settings, 'SITE_URL', f'https://{_PRODUCTION_DOMAIN}')
    domain = url.replace('https://', '').replace('http://', '').rstrip('/')
    # Railway-interne Domains niemals in die Sitemap lassen
    if '.railway.app' in domain or '.up.railway.app' in domain:
        return _PRODUCTION_DOMAIN
    return domain


def _cms_lastmod(pfad):
    """Das echte Aenderungsdatum der beiden CMS-Seiten - Befund D1 (06.09.2026).

    ``/aktuelles/`` und ``/galerie/`` beziehen ihren Inhalt vollstaendig aus
    dem CMS. Bis zum 06.09.2026 meldeten beide ein festes Datum (26.08.2026):
    Veroeffentlichte Oliver einen Beitrag, behauptete die Sitemap weiter, die
    Seite sei seit dem 26.08. unveraendert. Das ist derselbe Fehler wie ein
    mitwanderndes ``date.today()`` (Regel 22), nur andersherum und leiser - und
    **keine** der drei Pruefungen konnte ihn finden: Die lastmod-Warnung in
    ``check_seo`` haelt die vier Konstanten gegen das Commit-Datum ihrer
    Datenmodule, und CMS-Inhalte stehen in keinem Datenmodul.

    Genommen wird ``max(erstellt_am)`` ueber die **veroeffentlichten**
    Beitraege. Fuer ``/galerie/`` laeuft der Weg ueber ``AktuellesBild`` zum
    Beitrag: Das Bild selbst hat kein eigenes Zeitfeld, sein Datum ist das
    seines Beitrags.

    **Kein ``date.today()`` und kein ``timezone.now()``** - dieses Datum
    bewegt sich nur, wenn wirklich etwas veroeffentlicht wurde. Genau das
    unterscheidet eine Aggregation von einem Kalenderaufruf, und darauf zielt
    Regel 22.

    Rueckgabe ``None``, wenn nichts da ist oder die Abfrage scheitert - der
    Aufrufer faellt dann auf das feste Datum zurueck, mit ``logger.warning``.
    """
    from django.db.models import Max
    from django.utils import timezone
    from .models import AktuellesBild, AktuellesPost

    if pfad == '/aktuelles/':
        wert = (AktuellesPost.objects
                .filter(veroeffentlicht=True)
                .aggregate(m=Max('erstellt_am'))['m'])
    else:
        wert = (AktuellesBild.objects
                .filter(post__veroeffentlicht=True)
                .aggregate(m=Max('post__erstellt_am'))['m'])
    if not wert:
        return None
    # ``erstellt_am`` ist ein DateTimeField und mit USE_TZ=True zeitzonenbewusst
    # (UTC). Ein Beitrag, der um 00:30 Berliner Zeit erscheint, stuende in UTC
    # noch auf dem Vortag - das Datum waere also einen Tag zu alt. Deshalb erst
    # in die Ortszeit, dann auf das Datum kuerzen. Die Abfrage auf ``is_aware``
    # deshalb, weil ``localtime`` bei einem naiven Wert (USE_TZ=False) wirft.
    if timezone.is_aware(wert):
        wert = timezone.localtime(wert)
    return wert.date()


# ── Der Galeriebestand ──────────────────────────────────────────────────────
#
# **Eine Quelle fuer drei Zusagen** (D5, 06.09.2026). Von der Frage "gibt es
# freigegebene Galeriebilder?" haengen inzwischen drei Dinge ab, die einander
# nicht widersprechen duerfen:
#
#   1. das ``noindex`` auf ``/galerie/`` (``galerie_leer`` in galerie.html),
#   2. ob ``/galerie/`` in ``sitemap-main.xml`` steht (``MainSitemap.items()``),
#   3. ob es ``sitemap-images.xml`` ueberhaupt gibt (``ImageSitemap``).
#
# Waeren das drei Abfragen, koennten sie auseinanderlaufen - und der teure
# Fall ist genau der leise: eine Bildsitemap, die Bilder auf einer Seite
# meldet, die per ``noindex`` gar nicht indexiert werden soll (Regel 21).
# Deshalb fragen alle drei ueber ``galerie_bilder()``.
#
# Warum das hier steht und nicht in ``apps/core/data/``: Regel 4 - ein
# Datenmodul darf keine Models importieren. Dieselbe Begruendung wie bei
# ``_cms_lastmod`` weiter oben.

#: Ausgabebreite der Galeriebilder in Pixeln.
#:
#: **Warum die Sitemap eine feste Breite nennen muss.** ``_safe_image_url``
#: backt die Breite in den Cloudinary-Pfad (``…/f_auto,q_auto:eco,c_limit,
#: w_900/…``). Naehme die Sitemap eine andere Breite als die Seite, stuenden
#: dort zwei URLs fuer dasselbe Foto - Google zaehlt sie als zwei Bilder und
#: findet keines davon auf der Seite wieder. Und wuerde die Breite je nach
#: Anzeigekontext gewaehlt, aenderte sich die URL bei jeder Layoutaenderung;
#: die Bildersuche faenge jedes Mal von vorn an.
#:
#: **Warum 900 und nicht das Original.** Cloudinary liefert das Original mit
#: bis zu 8 MB aus (docs/fallen.md). Was in der Sitemap steht, laedt Google
#: herunter. 900 px ist die groesste Stufe, die die Galerie selbst ausliefert
#: - damit ist der Eintrag zeichengleich mit dem ``src`` im Markup, und die
#: ``srcset``-Stufen darunter sind Varianten desselben Bildes, keine neuen.
GALERIE_BILD_BREITE = 900


def galerie_bilder():
    """Die freigegebenen Galeriebilder - **die einzige Definition des Bestands**.

    Reihenfolge wie auf der Seite: neueste Beitraege zuerst, innerhalb eines
    Beitrags die vom CMS gesetzte ``reihenfolge``. Die Sitemap braucht sie
    nicht, die Seite schon - und zwei Abfragen mit verschiedener Sortierung
    waeren wieder zwei Wahrheiten.

    Gibt ein QuerySet zurueck, keine Liste: ``views.galerie`` blaettert
    darueber (``Paginator``), ``galerie_hat_bilder`` fragt nur ``exists()``.
    """
    from .models import AktuellesBild
    return (AktuellesBild.objects
            .filter(post__veroeffentlicht=True)
            .select_related('post')
            .order_by('-post__datum', 'post_id', 'reihenfolge', 'pk'))


def galerie_hat_bilder():
    """Gibt es freigegebene Galeriebilder? - die Bedingung hinter dem ``noindex``.

    Faellt die Abfrage aus, lautet die Antwort ``False``: Eine Seite, die
    faelschlich auf ``noindex`` steht, ist reparabel; eine leere Seite im Index
    ist Thin Content und kostet Vertrauen fuer die ganze Domain.

    **Aber still darf der Rueckfall nicht sein** - dieselbe Begruendung wie
    beim Galerie-Zweig in ``items()`` und bei ``lastmod_fuer_pfad``: Von aussen
    ist sonst nicht zu unterscheiden, ob niemand Bilder freigegeben hat oder
    ob die Datenbank weg war. Das sieht wie eine Entscheidung aus und ist ein
    Ausfall.
    """
    try:
        return galerie_bilder().exists()
    except Exception:      # noqa: BLE001 - Sitemap darf nie an der DB scheitern
        _log_sitemap.warning('Galerie-Bestand nicht ermittelbar - /galerie/ '
                             'gilt fuer diese Antwort als leer', exc_info=True)
        return False


def _absolut(url):
    """Eine Medien-URL absolut machen.

    Cloudinary liefert bereits absolute URLs. Ohne ``CLOUDINARY_URL`` (lokal,
    im Testlauf) steht dort ein ``/media/…``-Pfad - und eine Sitemap mit
    relativen Adressen ist fuer Google keine Sitemap.
    """
    if not url:
        return url
    if url.startswith(('http://', 'https://')):
        return url
    return 'https://%s%s' % (_canonical_domain(), url)


def galerie_bild_liste():
    """``[{'loc': …, 'titel': …}]`` fuer die Bildsitemap.

    ``titel`` kommt aus ``AktuellesBild.alt_texte()`` - **derselbe Aufruf**,
    aus dem auch das ``alt``-Attribut auf ``/galerie/`` entsteht. Er luegt
    nie: Ohne gepflegte Bildbeschreibung faellt er auf Beitragstitel plus
    "vorher"/"nachher" zurueck, statt einen Ort zu raten
    (siehe ``models.py::alt_text``).

    **Seit IS25 (12.09.2026) ueber die Sammelfunktion statt je Bild.** Der
    Rueckfall allein liefert fuer jedes Bild eines Beitrags dieselbe
    Zeichenkette; ``alt_texte()`` nummeriert genau diese Wiederholungen
    durch. Ueber ``alt_text()`` je Bild stuende hier wieder der unnummerierte
    Text - und damit eine andere Zeichenkette als auf der Seite.

    Bilder, deren URL sich nicht bauen laesst, fallen weg statt die ganze
    Sitemap zu verhindern; ``_safe_image_url`` schreibt fuer jedes davon eine
    Warnung ins Log.
    """
    from .models import AktuellesBild
    from .views import _safe_image_url
    bilder = list(galerie_bilder())
    # ``vollstaendig=True``: Das ist der Gesamtbestand, nicht eine Blaetterseite.
    alt_map = AktuellesBild.alt_texte(bilder, vollstaendig=True)
    aus = []
    for bild in bilder:
        url = _safe_image_url(bild.bild, width=GALERIE_BILD_BREITE)
        if url:
            aus.append({'loc': _absolut(str(url)),
                        'titel': alt_map.get(bild.pk) or bild.alt_text()})
    return aus


def statische_bild_liste(pfad):
    """``[{'loc': …, 'titel': …}]`` fuer die Fotos einer festen Seite (TS19).

    Die Datei kommt durch ``static()`` und nicht als fertige URL aus den
    Daten: In Produktion laeuft ``CompressedManifestStaticFilesStorage``, dort
    heisst ``sprinter1.webp`` in Wahrheit ``sprinter1.<hash>.webp``. Das
    Template baut seine ``src`` ueber denselben Weg ({% static %}) - damit
    nennen Seite und Sitemap zeichengleich dieselbe Adresse, und zwar auch
    nach dem naechsten Deploy. Eine ausgeschriebene URL waere genau der
    Fehler, gegen den ``GALERIE_BILD_BREITE`` weiter oben argumentiert.

    Faellt die Aufloesung fuer eine Datei aus - fehlender Manifest-Eintrag
    nach einem unvollstaendigen ``collectstatic`` -, faellt das Bild weg und
    die Sitemap bleibt gueltig. Still darf das nicht sein: Von aussen sieht
    ein fehlendes Bild wie eine Entscheidung aus.
    """
    from django.templatetags.static import static as _static_url
    aus = []
    for datei, titel in SEITEN_BILDER.get(pfad, ()):
        try:
            url = _static_url(datei)
        except Exception:      # noqa: BLE001 - Sitemap darf nie am Manifest scheitern
            _log_sitemap.warning('Statisches Bild %r nicht aufloesbar - es '
                                 'fehlt in der Bildsitemap von %s',
                                 datei, pfad, exc_info=True)
            continue
        aus.append({'loc': _absolut(url), 'titel': titel})
    return aus


def aktuelles_seite_bilder():
    """``[{'loc': …, 'titel': …}]`` - die Bilder, die ``/aktuelles/`` wirklich zeigt (TS19).

    **Dieselbe Quelle wie die Seite:** die erste Blaetterseite des
    Archivs (``AKTUELLES_JE_SEITE`` Beitraege, gleiche Sortierung), durch
    ``views._enrich_posts`` - dieselbe Funktion, die das Template fuettert.
    Genannt wird je Beitragstyp, was ``aktuelles.html`` auch ausgibt: bei
    ``bericht`` und ``zitat`` die Galerie, bei ``vorher_nachher`` die beiden
    Spalten. Der Titel ist der ``alt`` des Templates
    (``url.alt|default:post.titel``). **Nicht** genannt: die Portraits der
    Autoren (Entscheidung des Betriebs, siehe ``data/bilder.py``).

    Faellt die Abfrage aus, bleibt der Eintrag ohne Bild - mit Warnung.
    """
    from .models import AktuellesPost
    from .views import AKTUELLES_JE_SEITE, _enrich_posts
    aus, gesehen = [], set()
    try:
        posts = _enrich_posts(AktuellesPost.objects
                              .filter(veroeffentlicht=True)[:AKTUELLES_JE_SEITE])
        for post in posts:
            if post.typ == 'vorher_nachher':
                urls = list(post.vor_gallery_urls) + list(post.nach_gallery_urls)
            else:
                urls = list(post.gallery_urls)
            for url in urls:
                loc = _absolut(str(url))
                if loc in gesehen:
                    continue
                gesehen.add(loc)
                aus.append({'loc': loc,
                            'titel': getattr(url, 'alt', '') or post.titel})
    except Exception:          # noqa: BLE001 - Sitemap darf nie an der DB scheitern
        _log_sitemap.warning('Bilder von /aktuelles/ nicht ermittelbar - der '
                             'Eintrag bleibt ohne Bild', exc_info=True)
        return []
    return aus


def galerie_seite_bilder():
    """``[{'loc': …, 'titel': …}]`` - die erste Blaetterseite von ``/galerie/`` (TS19).

    Wie ``views.galerie``: ``galerie_bilder()`` (die einzige Definition des
    Bestands), die ersten ``GALERIE_JE_SEITE``, ``alt_texte`` ueber genau diese
    Seite. Die Gesamtmenge steht weiter in ``sitemap-images.xml``; im Eintrag
    der Hauptsitemap stehen nur Bilder, die der Aufruf von ``/galerie/``
    wirklich im ``<main>`` zeigt.
    """
    from .models import AktuellesBild
    from .views import _safe_image_url, GALERIE_JE_SEITE
    aus = []
    try:
        bilder = list(galerie_bilder()[:GALERIE_JE_SEITE])
        alt_map = AktuellesBild.alt_texte(bilder)
        for bild in bilder:
            url = _safe_image_url(bild.bild, width=GALERIE_BILD_BREITE)
            if url:
                aus.append({'loc': _absolut(str(url)),
                            'titel': alt_map.get(bild.pk) or bild.alt_text()})
    except Exception:          # noqa: BLE001 - Sitemap darf nie an der DB scheitern
        _log_sitemap.warning('Bilder von /galerie/ nicht ermittelbar - der '
                             'Eintrag bleibt ohne Bild', exc_info=True)
        return []
    return aus


def lastmod_fuer_pfad(pfad):
    """**Die einzige Stelle, die das Aenderungsdatum einer URL bestimmt** (D2).

    Sowohl die Sitemap als auch der ``WebPage``-Knoten jeder Seite
    (``dateModified``, siehe ``templatetags/rw_schema.py``) fragen hier. Vorher
    haette es zwei Listen gegeben, und Regel 12 gilt fuer Daten wie fuer FAQ:
    Sichtbares und Schema aus einer Quelle, nie zwei pflegen.

    Der feste Teil steht in ``apps/core/data/lastmod.py`` (Regel 4: reine
    Daten, kein Django). Der bewegliche Teil - die beiden CMS-Seiten - steht
    hier, weil ein Datenmodul keine Models importieren darf.
    """
    if pfad in CMS_PFADE:
        try:
            echt = _cms_lastmod(pfad)
        except Exception:      # noqa: BLE001 - Sitemap darf nie an der DB scheitern
            # Dieselbe Begruendung wie beim Galerie-Zweig in ``items()``: Der
            # Rueckfall ist richtig, aber er darf nicht still sein. Faellt die
            # Abfrage aus, meldet die Seite wieder das feste Datum - und das
            # sieht aus wie eine Entscheidung, waehrend es ein Ausfall ist.
            _log_sitemap.warning('lastmod fuer %s nicht aus der Datenbank '
                                 'ermittelbar - es gilt das feste Datum',
                                 pfad, exc_info=True)
        else:
            if echt:
                return echt
            # Kein Fund ist kein Fehler: Solange nichts veroeffentlicht ist,
            # gibt es nichts zu datieren. Deshalb hier keine Warnung.
    return _lastmod_aus_daten(pfad)


def hero_bild(titel):
    """``[{'loc': …, 'titel': …}]`` mit dem Banner-Foto (TS19, 01.10.2026).

    Gleicher Weg wie ``statische_bild_liste``: Die Datei geht durch
    ``static()``, damit Sitemap und ``<img src>`` auch mit Manifest-Hash
    zeichengleich sind. Faellt die Aufloesung aus, bleibt der Eintrag ohne Bild
    (die Sitemap bleibt gueltig) - mit Warnung, nicht still.
    """
    from django.templatetags.static import static as _static_url
    try:
        url = _static_url(HERO_BILD)
    except Exception:          # noqa: BLE001 - Sitemap darf nie am Manifest scheitern
        _log_sitemap.warning('Banner-Foto %r nicht aufloesbar - es fehlt in den '
                             'Teil-Sitemaps', HERO_BILD, exc_info=True)
        return []
    return [{'loc': _absolut(url), 'titel': titel}]


class MitBildern:
    """Haengt jedem ``<url>`` die ``<image:image>``-Knoten seiner Seite an.

    Die Teil-Sitemaps werden mit ``sitemap_mit_bildern.xml`` ausgeliefert;
    das Template liest ``url.bilder``. Die Unterklasse liefert
    ``bilder(item)``. Das Bild steht im Eintrag der Seite selbst, weil die
    Auswertung der Search Console und Pruefwerkzeuge je ``<url>`` zaehlen.
    """

    def bilder(self, item):
        return []

    def get_urls(self, *args, **kwargs):
        urls = super().get_urls(*args, **kwargs)
        for u in urls:
            u['bilder'] = self.bilder(u['item'])
        return urls


class MainSitemap(MitBildern, Sitemap):
    """Alle Hauptseiten + Jobs + Kooperation + Legal."""
    protocol = 'https'

    def get_domain(self, site=None):
        return _canonical_domain()

    # (url_name, priority, changefreq)
    #
    # Die vierte Spalte "days_since_update" ist am 06.09.2026 mit D2 nach
    # ``data/lastmod.py::VERSATZ_TAGE`` gewandert - dorthin, wo auch der
    # WebPage-Knoten sie findet. Sie hier stehen zu lassen haette bedeutet,
    # dieselbe Zahl an zwei Stellen zu pflegen; das ist genau der Zustand, den
    # D2 beendet.
    pages = [
        ('core:home',             1.0,  'weekly'),
        ('core:dienstleistungen', 0.9,  'monthly'),
        ('core:anfrage',          0.9,  'monthly'),
        ('core:preisangebot',     0.85, 'weekly'),
        ('core:standorte',        0.8,  'monthly'),
        ('core:ueber_uns',        0.75, 'monthly'),
        ('core:jobs',             0.75, 'weekly'),
        ('core:kooperation',      0.6,  'monthly'),
        # In F10 ergaenzt. /entrumpelung/ ist die Verteilerseite fuer die
        # Stadtseiten (F11), /aktuelles/ war indexierbar, stand aber in keiner
        # Sitemap - Google fand sie nur zufaellig ueber interne Links.
        ('core:entrumpelung_hub',  0.85, 'monthly'),
        ('core:aktuelles',        0.6,  'weekly'),
    ]

    # impressum / datenschutz / agb stehen bewusst NICHT hier: Sie sind
    # noindex, und eine noindex-URL in der Sitemap ist ein GSC-Fehler.
    # /galerie/ kommt dazu, sobald F9 das noindex entfernt hat.

    def items(self):
        """/galerie/ kommt erst dazu, wenn die Seite auch Bilder hat (F9/F10).

        Eine leere Seite in die Sitemap zu schreiben ist ein GSC-Fehler
        ("Gefunden - zurzeit nicht indexiert") und Thin Content. Die Seite
        traegt genau dann kein noindex, wenn Bilder da sind - beides haengt an
        derselben Bedingung, sie koennen also nicht auseinanderlaufen.

        **Seit D5 (06.09.2026) haengt eine dritte Aussage daran**, die
        Bildsitemap. Die Abfrage steht deshalb nicht mehr hier, sondern in
        ``galerie_hat_bilder()``; der Rueckfall samt Logzeile ebenfalls. Wer
        sie hier wieder ausschreibt, hat zwei Bedingungen fuer dieselbe Frage
        - und die zweite faellt erst auf, wenn sie schon auseinandergelaufen
        sind.
        """
        seiten = list(self.pages)
        if galerie_hat_bilder():
            seiten.append(('core:galerie', 0.6, 'weekly'))
        return seiten

    def location(self, item):
        return reverse(item[0])

    def bilder(self, item):
        """Die Inhaltsbilder der Seite - nur, was ihr ``<main>`` wirklich zeigt (TS19).

        * die festen Fotos aus ``data/bilder.py`` (``/`` und ``/ueber-uns/``),
        * ``/aktuelles/`` und ``/galerie/``: die erste Blaetterseite aus dem CMS
          (``aktuelles_seite_bilder``, ``galerie_seite_bilder``) - die
          Gesamtmenge der Galerie steht in ``sitemap-images.xml``, die
          Hauptdatei bliebe sonst nicht klein.

        Alle uebrigen Seiten (``/dienstleistungen/``, ``/anfrage/``,
        ``/preisangebot/``, ``/standorte/``, ``/jobs/``, ``/kooperationspartner/``,
        ``/entrumpelung/``) tragen im ``<main>`` nur Schmuck (``alt=""``) oder
        die Portraits der Regionalleiter und bleiben deshalb ohne Bild.
        """
        pfad = reverse(item[0])
        if pfad == '/aktuelles/':
            return aktuelles_seite_bilder()
        if pfad == '/galerie/':
            return galerie_seite_bilder()
        return statische_bild_liste(pfad)

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]

    def lastmod(self, item):
        """Seit D2 ueber den Pfad, nicht ueber eine eigene Spalte.

        ``/aktuelles/`` und ``/galerie/`` bekommen hier das echte Datum aus
        dem CMS (D1), alle uebrigen ihren Versatz aus ``data/lastmod.py``.
        Dieselbe Funktion beantwortet ``dateModified`` im WebPage-Knoten -
        deshalb koennen Sitemap und Schema nicht auseinanderlaufen.
        """
        return lastmod_fuer_pfad(reverse(item[0]))


class JobsSitemap(MitBildern, Sitemap):
    """Individuelle Stellenanzeigen /jobs/<slug>/"""
    protocol = 'https'
    changefreq = 'weekly'
    priority = 0.7

    def get_domain(self, site=None):
        return _canonical_domain()

    def items(self):
        return list(_JOB_DATA.keys())

    def location(self, slug):
        return f'/jobs/{slug}/'

    def lastmod(self, slug):
        return lastmod_fuer_pfad(self.location(slug))


class CitySitemap(MitBildern, Sitemap):
    """Die Stadtseiten unter /entrumpelung/<slug>/ – die einzigen Stadt-URLs.

    Wie viele es sind, sagt ``_CITY_DATA`` und sonst niemand: Hier stand bis
    zum 06.09.2026 "die 53 Stadtseiten", waehrend es 54 waren. Eine
    Bestandszahl im Kommentar ist der Vorlaeufer derselben Zahl im Template
    (Befund G1).

    Die frueheren Landingpages unter /<slug>/ sind entfernt (301 bzw. 410),
    siehe apps/core/views.py::city_landing_page. Sie duerfen hier nicht wieder
    auftauchen, sonst listet die Sitemap URLs, die sofort weiterleiten.
    """
    protocol = 'https'
    changefreq = 'monthly'
    priority = 0.8

    def get_domain(self, site=None):
        return _canonical_domain()

    def items(self):
        return list(_CITY_DATA.keys())

    def location(self, slug):
        return f'/entrumpelung/{slug}/'

    def bilder(self, slug):
        return hero_bild(HERO_TITEL_STADT.format(stadt=_CITY_DATA[slug]['name']))

    def lastmod(self, slug):
        return lastmod_fuer_pfad(self.location(slug))


class ServiceSitemap(MitBildern, Sitemap):
    """Die Leistungsseiten unter /<leistung>/ (Block 2).

    Eigene Teil-Sitemap und nicht ein Anhaengsel an MainSitemap: Die GSC zeigt
    Indexierungsquoten je Sitemap. Ob die neuen Leistungsseiten ankommen, ist
    genau die Frage, die Block 2 beantworten muss - in einer Sammeldatei mit 11
    Bestandsseiten waere sie nicht ablesbar.
    """
    protocol = 'https'
    changefreq = 'monthly'
    priority = 0.9

    def get_domain(self, site=None):
        return _canonical_domain()

    def items(self):
        return list(_SERVICE_DATA.keys())

    def location(self, slug):
        return f'/{slug}/'

    def bilder(self, slug):
        return hero_bild(HERO_TITEL_LEISTUNG.format(
            leistung=_SERVICE_DATA[slug]['name']))

    def lastmod(self, slug):
        return lastmod_fuer_pfad(self.location(slug))


class MatrixSitemap(MitBildern, Sitemap):
    """Leistung x Stadt (A13, Charge 1).

    Eigene Teil-Sitemap aus demselben Grund wie ServiceSitemap: Ob Google
    diese fuenf Seiten aufnimmt, ist die **Abnahmebedingung von A13**. In
    einer Sammeldatei mit 76 anderen URLs waere die Quote nicht ablesbar -
    und dann waere die Messung, von der Charge 2 und 3 abhaengen, wertlos.
    """
    protocol = 'https'
    changefreq = 'monthly'
    priority = 0.8

    def get_domain(self, site=None):
        return _canonical_domain()

    def items(self):
        return matrix_kombinationen()

    def location(self, paar):
        l_slug, s_slug = paar
        return f'/{l_slug}/{s_slug}/'

    def bilder(self, paar):
        l_slug, s_slug = paar
        return hero_bild(HERO_TITEL_MATRIX.format(
            leistung=_SERVICE_DATA[l_slug]['name'],
            stadt=_CITY_DATA[s_slug]['name']))

    def lastmod(self, paar):
        return lastmod_fuer_pfad(self.location(paar))


class RatgeberSitemap(MitBildern, Sitemap):
    """Der Ratgeber unter /ratgeber/ (T4, 16.09.2026) - Uebersicht plus Artikel.

    Eigene Teil-Sitemap aus demselben Grund wie ServiceSitemap: Ob die
    Wissensseiten in den Index kommen, ist die Frage, an der SU04 haengt, und
    in einer Sammeldatei waere die Quote nicht ablesbar.
    """
    protocol = 'https'
    changefreq = 'monthly'
    priority = 0.7

    def get_domain(self, site=None):
        return _canonical_domain()

    def items(self):
        from .data.ratgeber import _RATGEBER_DATA
        return [''] + list(_RATGEBER_DATA)

    def location(self, slug):
        return f'/ratgeber/{slug}/' if slug else '/ratgeber/'

    def lastmod(self, slug):
        return lastmod_fuer_pfad(self.location(slug))


class AktuellesSitemap(Sitemap):
    """Die Einzelseiten importierter GBP-Beitraege (Bauplan §7).

    Eigene Teil-Sitemap aus demselben Grund wie ``RatgeberSitemap``: eine
    eigene Indexierungsquote fuer eine neue Inhaltsart. Meldet nur Beitraege,
    die 1. veroeffentlicht sind, 2. einen Slug haben (nur importierte
    GBP-Beitraege bekommen bisher einen - das gesamte bisherige CMS-Archiv
    hat ``slug=''`` und keine Einzelseite) und 3. nicht ``noindex`` sind
    (mindestens ``GBP_MINDESTWORTE_FUER_INDEX`` Woerter, siehe
    ``views.aktuelles_beitrag`` - eine zu duenne Seite gehoert nicht
    beworben, Regel 21 sinngemaess). ``aktive_abschnitte`` blendet den
    Abschnitt von selbst aus, solange kein Beitrag alle drei Bedingungen
    erfuellt (siehe dort).
    """
    protocol = 'https'
    changefreq = 'yearly'
    priority = 0.4

    def get_domain(self, site=None):
        return _canonical_domain()

    def items(self):
        from .views import GBP_MINDESTWORTE_FUER_INDEX
        from .models import AktuellesPost
        aus = []
        for p in (AktuellesPost.objects
                 .filter(veroeffentlicht=True)
                 .exclude(slug='')):
            if len((p.inhalt or '').split()) >= GBP_MINDESTWORTE_FUER_INDEX:
                aus.append(p)
        return aus

    def location(self, post):
        return f'/aktuelles/{post.datum.year}/{post.slug}/'

    def lastmod(self, post):
        return post.erstellt_am


class ImageSitemap(Sitemap):
    """Die eigenen Fotos fuer die Bildersuche (D5, 06.09.2026; TS19 gleichentags).

    **Warum es diese Teil-Sitemap gibt.** Die Galeriebilder sind der
    originaerste Bildbestand dieses Betriebs - beschriftet
    (``AktuellesBild.bildtext``), in passenden Breiten ausgeliefert - und
    standen bis zum 06.09.2026 in keiner Sitemap und in keinem Schema.
    "entruempelung vorher nachher" ist eine Suchanfrage mit Bildabsicht; es
    fehlte nur die Anmeldung.

    **Seit TS19 nennt sie zwei Bestaende**, und der Unterschied zwischen
    ihnen ist der Kern der Sache:

    1. die **festen Fotos** der Seiten aus ``data/bilder.py`` - heute die
       Flotte und das Logo auf ``/ueber-uns/``. Sie liegen im Repository, es
       gibt sie also immer.
    2. die **Galeriebilder** aus dem CMS, sobald welche freigegeben sind.

    Was hier **nicht** steht, ist die eigentliche Entscheidung: das
    ``hero-banner`` und die uebrigen Hero-Motive der 80 anderen Seiten. Sie
    tragen ``alt=""``, sind also ausdruecklich Schmuck. Sie aufzunehmen haette
    aus 2 gemeldeten Seiten 82 gemacht, ohne ein einziges zusaetzliches Motiv
    fuer die Bildersuche - Google zaehlt eindeutige Bild-URLs, nicht
    Nennungen. Die Begruendung im Langen steht in ``data/bilder.py``.

    **Ein ``<url>``-Eintrag je Seite, darin viele ``<image:image>``.** Die
    Bildsitemap sagt nicht "dieses Bild ist eine Seite", sondern "auf dieser
    Seite liegen diese Bilder". Fuer die Galerie ist das ``/galerie/``; die
    Folgeseiten des Blaetterwerks laufen ueber ``?seite=`` und tragen dasselbe
    ``canonical`` (siehe ``views._blaettern``), sie sind also keine eigenen
    Adressen und duerfen hier nicht auftauchen (Regel 21, zweiter Satz:
    weiterleitende URLs ebenso wenig).

    WAS DIESE SITEMAP NICHT LEISTET
    -------------------------------
    * **Sie nennt alle freigegebenen Bilder unter ``/galerie/``, auch die auf
      Seite 2 und 3.** Das ist eine bewusste Ungenauigkeit: Die Alternative
      waere, ``/galerie/?seite=2`` mitzulisten - eine Adresse, die per
      ``canonical`` auf ``/galerie/`` zeigt und damit in keine Sitemap gehoert.
      Ein Bild, das Google in der Sitemap findet, aber nicht auf der Seite,
      wird schlicht nicht aufgenommen; eine kanonisierte URL in der Sitemap
      waere ein gemeldeter Fehler. Ab 1.000 Bildern ist die Grenze von Google
      je ``<url>``-Eintrag erreicht - dann muss hier nach Seiten gruppiert
      werden.
    * **``<image:title>`` wertet Google seit August 2022 nicht mehr aus** -
      unterstuetzt ist nur noch ``<image:loc>``. Das Feld steht trotzdem drin:
      Es ist im Schema der Erweiterung weiter gueltig, andere Suchmaschinen
      lesen es, und es kostet nichts. Wer es entfernt, verliert nichts bei
      Google und etwas bei Bing.
    * **Sie prueft nicht, ob die Bild-URL erreichbar ist.** Gebaut wird sie aus
      dem ``ImageField`` bzw. aus ``static()``; ob Cloudinary oder WhiteNoise
      sie ausliefert, sagt nur der Abruf.
    * **Sie sagt nichts darueber, ob ein Bild in der Bildersuche ankommt.**
      Eine Sitemap ist eine Anmeldung, keine Aufnahme.
    """
    protocol = 'https'
    changefreq = 'weekly'
    priority = 0.6

    def get_domain(self, site=None):
        return _canonical_domain()

    def items(self):
        """Je Seite mit eigenen Fotos ein Eintrag - die Galerie nur mit Bildern.

        **Die leere Liste bleibt moeglich und bleibt der Kern der Falle aus
        D5**: Eine Bildsitemap mit leerem ``<urlset>`` und Status 200 taucht in
        der Search Console als Fehler auf. Der Abschnitt verschwindet dann
        vollstaendig - aus dem Index, aus der robots.txt
        (``aktive_abschnitte``) und als 404 unter seiner eigenen Adresse
        (``image_sitemap``).

        Seit TS19 tritt dieser Fall im Betrieb nicht mehr ein, weil die festen
        Fotos aus ``data/bilder.py`` im Repository liegen. Der Zweig bleibt
        trotzdem stehen: Er greift, wenn ``collectstatic`` unvollstaendig war
        und ``statische_bild_liste`` deshalb nichts aufloesen konnte. Eine
        Datei mit Status 200 und leerem Inhalt waere dann die schlechtere
        Antwort.

        **Was sich durch TS19 nicht aendert:** Die Galeriebilder haengen
        weiterhin an genau einer Abfrage (``galerie_bilder()``) - derselben,
        an der auch das ``noindex`` auf ``/galerie/`` und der Eintrag in
        ``sitemap-main.xml`` haengen. Ein Bild auf einer ``noindex``-Seite
        anzumelden ist Regel 21 eine Ebene tiefer, und daran aendert ein
        zweiter Bestand nichts.
        """
        eintraege = []
        for pfad in SEITEN_BILDER:
            fotos = statische_bild_liste(pfad)
            if fotos:
                eintraege.append({'pfad': pfad, 'bilder': fotos})
        galerie = galerie_bild_liste()
        if galerie:
            eintraege.append({'pfad': reverse('core:galerie'),
                              'bilder': galerie})
        return eintraege

    def location(self, eintrag):
        return eintrag['pfad']

    def lastmod(self, eintrag):
        return lastmod_fuer_pfad(eintrag['pfad'])


def image_sitemap(request):
    """``/sitemap-images.xml`` - eigene View wegen des eigenen Templates.

    Djangos ``sitemaps.views.sitemap`` kennt genau **ein** Template je Aufruf;
    die Sammelroute ``sitemap-<section>.xml`` liefert deshalb fuer alle
    Abschnitte ``sitemap.xml`` aus, und darin gibt es keinen
    ``image:``-Namensraum. Diese Route steht in ``config/urls.py`` **vor** der
    Sammelroute und faengt den Abschnitt ab.

    **Ohne Bilder antwortet sie mit 404**, nicht mit einem leeren
    ``<urlset>``. Begruendung siehe ``ImageSitemap.items``. Dieselbe Antwort
    gibt Django fuer einen Abschnitt, den es nicht gibt.

    Seit TS19 ist das der Ausnahmefall: Die festen Fotos aus ``data/bilder.py``
    liegen im Repository, die Sitemap hat also auch ohne freigegebene
    Galeriebilder Inhalt. Der 404-Zweig bleibt fuer den Fall stehen, dass sich
    keine einzige Datei aufloesen laesst - dann ist er die richtige Antwort.
    """
    from django.contrib.sitemaps.views import sitemap as _django_sitemap
    from django.http import Http404

    karte = ImageSitemap()
    if not karte.items():
        raise Http404('Keine freigegebenen Galeriebilder - keine Bildsitemap')
    return _django_sitemap(request, {'images': karte}, section='images',
                           template_name='sitemap_images.xml')


def aktive_abschnitte(sitemaps):
    """Die Teil-Sitemaps, die gerade wirklich URLs haben (D5).

    Sowohl der Index (``sitemap_index``) als auch die ``Sitemap:``-Zeilen in
    ``robots.txt`` (``views.robots_txt``) nennen die Abschnitte aus der
    Registrierung in ``config/urls.py``. Seit es einen Abschnitt gibt, der
    zeitweise leer ist, reicht die Registrierung als Auskunft nicht mehr: Ein
    Verweis auf eine Datei, die mit 404 antwortet, ist in der Search Console
    ein gemeldeter Fehler.

    Eine Funktion fuer beide Aufrufer, aus demselben Grund wie
    ``galerie_hat_bilder()``: Zwei Filter fuer dieselbe Frage laufen
    auseinander, und der Fehler faellt erst auf, wenn Google ihn meldet.

    Was sie nicht leistet: Sie ruft ``items()`` auf, nicht die URL. Ein
    Abschnitt mit Eintraegen, dessen View aus einem anderen Grund scheitert,
    steht hier trotzdem drin.
    """
    aus = []
    for name, klasse in sitemaps.items():
        try:
            sm = klasse() if isinstance(klasse, type) else klasse
            hat_eintraege = bool(sm.items())
        except Exception:                                      # noqa: BLE001
            # Wie ueberall in dieser Datei: Der Rueckfall ist richtig, aber er
            # darf nicht still sein. Ein Abschnitt, der wegen eines Ausfalls
            # aus robots.txt und Index verschwindet, sieht von aussen wie eine
            # Entscheidung aus.
            _log_sitemap.warning('Teil-Sitemap %r nicht auswertbar - sie fehlt '
                                 'in dieser Ausgabe', name, exc_info=True)
            hat_eintraege = False
        if hat_eintraege:
            aus.append((name, klasse))
    return aus


def _neuestes_lastmod(klasse):
    """Das juengste ``lastmod`` einer Teil-Sitemap - oder ``None``.

    Bewusst defensiv: Faellt die Ermittlung fuer eine Sitemap aus, entfaellt
    nur deren ``lastmod``. Ein Index ohne Datum ist gueltig, ein Index mit
    Serverfehler nicht.
    """
    try:
        sm = klasse() if isinstance(klasse, type) else klasse
        werte = [sm.lastmod(item) if callable(getattr(sm, 'lastmod', None))
                 else sm.lastmod
                 for item in sm.items()]
        werte = [w for w in werte if w]
        return max(werte) if werte else None
    except Exception:                                          # noqa: BLE001
        # Derselbe Grundsatz wie in aktive_abschnitte: Der Rueckfall ist
        # richtig, aber ein Index ohne Datum soll im Protokoll erklaert sein.
        _log_sitemap.warning('lastmod fuer %r nicht ermittelbar - der Index '
                             'nennt fuer diesen Abschnitt kein Datum',
                             klasse, exc_info=True)
        return None


def sitemap_index(request, sitemaps):
    """Sitemap-Index von Hand (F10).

    Djangos ``sitemaps.views.index`` baut die Adressen aus dem *Request-Host*.
    Auf einer Railway-Preview-URL stuende dort also ``…up.railway.app`` - und
    eine Preview-Domain darf niemals in einer Sitemap landen. Die Teil-Sitemaps
    umgehen das ueber ``get_domain()``; fuer den Index gibt es keinen solchen
    Haken, deshalb dieser Weg.

    Seit D5 laeuft die Registrierung durch ``aktive_abschnitte``: Ein leerer
    Abschnitt - heute nur ``images`` - wird nicht genannt, weil seine Adresse
    dann mit 404 antwortet.
    """
    from django.http import HttpResponse
    from django.utils.xmlutils import SimplerXMLGenerator
    import io

    basis = f'https://{_canonical_domain()}'
    puffer = io.StringIO()
    xml = SimplerXMLGenerator(puffer, 'utf-8')
    xml.startDocument()
    xml.startElement('sitemapindex',
                     {'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'})
    for name, klasse in aktive_abschnitte(sitemaps):
        xml.startElement('sitemap', {})
        xml.addQuickElement('loc', f'{basis}/sitemap-{name}.xml')
        # ``lastmod`` gehoert auch an den Index. Ohne die Angabe hat Google
        # keinen Anhaltspunkt, ob sich eine Teil-Sitemap ueberhaupt geaendert
        # hat, und holt sie entsprechend traege ab - genau der Grund, warum
        # nach dem Einreichen tagelang nichts passiert.
        stand = _neuestes_lastmod(klasse)
        if stand:
            xml.addQuickElement('lastmod', stand.isoformat())
        xml.endElement('sitemap')
    xml.endElement('sitemapindex')
    xml.endDocument()
    return HttpResponse(puffer.getvalue(), content_type='application/xml')
