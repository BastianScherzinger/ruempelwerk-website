"""RSS-Feed fuer /aktuelles/ (GE32, 11.09.2026).

**Warum es ihn gibt.** ``/aktuelles/`` ist die einzige Seite dieser Website,
deren Inhalt sich ohne Deploy aendert - die Beitraege kommen aus dem CMS unter
``STATS_PATH``. Eine Antwortmaschine oder ein Aggregator erfuhr von einem
neuen Beitrag bisher erst beim naechsten Vollcrawl; die Sitemap nennt fuer
``/aktuelles/`` zwar ein ``lastmod`` aus ``max(erstellt_am)``, aber nicht, was
neu ist. Der Feed sagt es.

Gebaut mit ``django.contrib.syndication`` - Teil von Django, kein neues Paket,
und nicht in ``INSTALLED_APPS`` noetig, solange keine Feed-Templates benutzt
werden.

WAS DER FEED BEWUSST NICHT TUT
------------------------------
* **Keine Kundenzitate.** Dieselbe Entscheidung wie ``views._beitrag_schema_daten``
  (GE15): Ein Beitrag vom Typ ``zitat`` ist eine fremde Aussage ueber den
  Betrieb, kein Text des Betriebs. Bewertungsinhalt hat seine eigene Quelle
  (``data/reviews.py``, Regel 2).
* **Keine eigene Adresse je Beitrag.** Die Beitraege haben keine Detailseite.
  ``<link>`` zeigt deshalb auf ``/aktuelles/``, und ``<guid>`` traegt dieselbe
  Kennung wie das ``@id`` des ``BlogPosting`` im Schema - mit
  ``isPermaLink="false"``, weil ``#beitrag-<pk>`` im HTML kein Sprungziel ist.
* **Nur die erste Seite des Archivs.** Der Feed nimmt genau die
  ``AKTUELLES_JE_SEITE`` neuesten Beitraege, die auch ``/aktuelles/`` ohne
  ``?seite=`` zeigt. Nur so stimmt der ``<link>``: Jeder Beitrag im Feed steht
  wirklich auf der Seite, auf die er verweist.
* **Keine absoluten Adressen aus dem Request.** Django baut sie sonst aus
  ``request.get_host()``; hier kommen sie aus ``_safe_site_url()``, derselben
  Quelle wie ``canonical`` und Schema - ein Abruf ueber die Railway-Adresse
  soll keinen Feed mit Railway-Links ausliefern.

Verlinkt wird der Feed im Kopf **jeder** oeffentlichen Seite, ueber
``components/rw_seo.html`` (Regel 6).
"""

import datetime

from django.contrib.syndication.views import Feed
from django.utils import timezone

from .context_processors import _safe_site_url
from .data.firma import FIRMA
from .models import AUTOR_META, AktuellesPost

#: Pfad der Seite, deren Beitraege der Feed traegt.
_PFAD = '/aktuelles/'


class AktuellesFeed(Feed):
    """RSS-Feed unter ``/aktuelles/feed/`` mit den Beiträgen der ersten Archivseite."""

    title = f'Aktuelles – {FIRMA}'
    description = ('Berichte und Vorher-Nachher-Beiträge von abgeschlossenen '
                   'Entrümpelungen und Haushaltsauflösungen.')

    def link(self):
        return f'{_safe_site_url()}{_PFAD}'

    def feed_url(self):
        return f'{_safe_site_url()}{_PFAD}feed/'

    def items(self):
        # Erst in der Funktion importiert: views.py zieht beim Import die
        # Formulare, die Spam-Abwehr und alle Datenmodule nach sich.
        from .views import AKTUELLES_JE_SEITE
        erste_seite = AktuellesPost.objects.filter(
            veroeffentlicht=True)[:AKTUELLES_JE_SEITE]
        return [p for p in erste_seite if p.typ != 'zitat']

    def item_title(self, post):
        return post.titel

    def item_description(self, post):
        return post.inhalt

    def item_link(self, post):
        return self.link()

    item_guid_is_permalink = False

    def item_guid(self, post):
        return f'{_safe_site_url()}{_PFAD}#beitrag-{post.pk}'

    def item_pubdate(self, post):
        # ``datum`` ist ein reines Datum. Mitternacht in der Zeitzone des
        # Betriebs - eine Uhrzeit zu nennen, die niemand eingetragen hat,
        # waere eine Angabe ohne Quelle.
        return timezone.make_aware(
            datetime.datetime.combine(post.datum, datetime.time.min))

    def item_author_name(self, post):
        # Nur ein im CMS eingetragener Autor; ohne Eintrag bleibt das Feld leer
        # statt den Betrieb als Verfasser zu behaupten.
        return (AUTOR_META.get(post.autor) or {}).get('name') or None


class RatgeberFeed(Feed):
    """RSS der Ratgeberartikel unter ``/ratgeber/feed/`` (16.09.2026).

    Anders als ``AktuellesFeed`` hat hier jeder Eintrag eine eigene Adresse -
    ``link`` und ``guid`` sind die Artikel-URL, als Permalink. Das
    Erscheinungsdatum kommt aus ``data/lastmod.py::VEROEFFENTLICHT``, derselben
    Quelle wie ``datePublished`` im Article-Knoten; ohne belegtes Datum bleibt
    ``pubDate`` leer statt erfunden.
    """
    title = f'Ratgeber – {FIRMA}'
    description = ('Wissen rund um Entrümpelung und Haushaltsauflösung: Kosten, '
                   'Steuer, Begriffe und Wohnungsübergabe.')

    def link(self):
        return f'{_safe_site_url()}/ratgeber/'

    def feed_url(self):
        return f'{_safe_site_url()}/ratgeber/feed/'

    def items(self):
        from .data.ratgeber import alle_artikel
        return alle_artikel()

    def item_title(self, artikel):
        return artikel['h1']

    def item_description(self, artikel):
        return artikel['teaser']

    def item_link(self, artikel):
        return f"{_safe_site_url()}{artikel['url']}"

    def item_pubdate(self, artikel):
        from .data.lastmod import veroeffentlicht_fuer_pfad
        tag = veroeffentlicht_fuer_pfad(artikel['url'])
        if not tag:
            return None
        return timezone.make_aware(datetime.datetime.combine(tag, datetime.time.min))

    def item_author_name(self, artikel):
        return FIRMA
