# -*- coding: utf-8 -*-
"""Google-Rezensionen aus der Places API holen und zusammenfuehren.

**Warum das automatisch laufen muss.** Bis zum 14.08.2026 standen Durchschnitt
und Anzahl als Konstante im Code (``4.9`` bei ``18``), mit einem Pruefdatum
daneben. Das ist genau die Bauart, die in diesem Projekt schon zweimal
auseinandergelaufen ist - bei den Preisen und bei den Bewertungszahlen selbst,
die vorher ``5.0`` bei ``8`` behaupteten. Eine handgepflegte Zahl ist beim
Eintippen richtig und danach jeden Tag ein bisschen falscher. Ein
``AggregateRating``, das nicht mehr zum Profil passt, ist kein
Schoenheitsfehler, sondern ein Richtlinienverstoss.

**Drei Grenzen der API bestimmen das Design:**

1. **Hoechstens fuenf Rezensionen je Abruf** - unabhaengig davon, wie viele es
   gibt. Wir zeigen sechs. Der Sync darf deshalb **nie ersetzen, nur
   zusammenfuehren**; sonst loescht der erste erfolgreiche Lauf eine echte
   Bewertung. Was einmal gesehen wurde, bleibt stehen, bis es jemand von Hand
   entfernt.
2. **Rezensionen ohne Text liefert die API nicht mit.** ``userRatingCount``
   zaehlt sie trotzdem. Die Gesamtzahl ist also groesser als die Liste - das
   ist richtig so und kein Zeichen fuer einen fehlgeschlagenen Abruf.
3. **Zwischenspeichern hoechstens 30 Tage** (Nutzungsbedingungen der Places
   API; nur die Place-ID selbst ist davon ausgenommen). Ein Lauf pro Tag
   erfuellt das mit grossem Abstand.

**Ohne API-Schluessel passiert nichts.** Kein Fehler, kein leerer Abschnitt -
die statische Liste in ``data/reviews.py`` bleibt dann die Wahrheit. Eine
abgelaufene Rechnung bei Google darf der Startseite nicht die Kundenstimmen
nehmen.

Kosten: Der Feldsatz mit ``reviews`` faellt in die teuerste Stufe
("Enterprise"), die 1.000 Abrufe im Monat frei hat. Ein Lauf pro Tag sind 31.
"""

import json
import logging
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

_log = logging.getLogger('apps.core')

_DETAILS_URL = 'https://places.googleapis.com/v1/places/{place_id}'
_SUCHE_URL = 'https://places.googleapis.com/v1/places:searchText'

# Nur anfordern, was gebraucht wird - der Feldsatz bestimmt den Preis.
_FELDER_DETAILS = 'id,displayName,rating,userRatingCount,googleMapsUri,reviews'
_FELDER_SUCHE = 'places.id,places.displayName,places.formattedAddress'

# Derselbe User-Agent wie beim Mailversand. Google braucht ihn nicht, aber ein
# Request ohne UA aus einem Rechenzentrum wird gern von Zwischenschichten
# verworfen - denselben Fall gab es hier schon mit Cloudflare-Error 1010.
_UA = 'Ruempelwerk-Website/1.0'

_TIMEOUT = 15


class GoogleFehler(RuntimeError):
    """Der Abruf ist gescheitert. Der Aufrufer laesst den Altbestand stehen."""


def api_key():
    return (getattr(settings, 'GOOGLE_PLACES_API_KEY', '') or '').strip()


def _abrufen(url, feldmaske, daten=None):
    kopf = {
        'X-Goog-Api-Key': api_key(),
        'X-Goog-FieldMask': feldmaske,
        'User-Agent': _UA,
        'Accept': 'application/json',
    }
    rumpf = None
    if daten is not None:
        rumpf = json.dumps(daten).encode('utf-8')
        kopf['Content-Type'] = 'application/json'

    req = urllib.request.Request(url, data=rumpf, headers=kopf,
                                 method='POST' if daten is not None else 'GET')
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        # Der Fehlerrumpf von Google nennt den Grund im Klartext
        # ("API key not valid", "This API method requires billing") - ohne ihn
        # ist die Fehlersuche ein Ratespiel.
        try:
            detail = exc.read().decode('utf-8', 'replace')[:400]
        except Exception:
            # Der Abruf scheitert so oder so; verloren geht nur der Grund.
            # Das soll im Protokoll stehen, nicht still wegfallen.
            _log.warning('Fehlerrumpf der Places API nicht lesbar (HTTP %s)',
                         exc.code, exc_info=True)
            detail = ''
        raise GoogleFehler('HTTP %s: %s' % (exc.code, detail)) from exc
    except Exception as exc:
        raise GoogleFehler(str(exc)) from exc


def place_id_suchen(suchtext):
    """Die Place-ID einmalig ueber die Textsuche bestimmen.

    Damit muss niemand die kryptische ``ChIJ…``-Kennung von Hand heraussuchen.
    Das Ergebnis wird gespeichert und danach nicht mehr gesucht - Place-IDs
    sind laut Nutzungsbedingungen ausdruecklich unbegrenzt speicherbar.
    """
    antwort = _abrufen(_SUCHE_URL, _FELDER_SUCHE,
                       {'textQuery': suchtext, 'languageCode': 'de',
                        'regionCode': 'DE', 'maxResultCount': 1})
    treffer = antwort.get('places') or []
    if not treffer:
        raise GoogleFehler('Kein Treffer fuer %r' % suchtext)
    ort = treffer[0]
    return ort.get('id', ''), (ort.get('displayName') or {}).get('text', '')


def details_holen(place_id):
    """Bewertungsschnitt, Anzahl und bis zu fuenf Rezensionen."""
    url = _DETAILS_URL.format(place_id=urllib.parse.quote(place_id, safe=''))
    return _abrufen(url + '?languageCode=de', _FELDER_DETAILS)


# ── Aufbereitung ────────────────────────────────────────────────────────────

def namensschluessel(name):
    """Vergleichsform eines Autorennamens.

    Der Abgleich laeuft ueber den Namen, weil die alten sechs Rezensionen aus
    dem Markup keine Google-Kennung haben - sie wurden abgeschrieben, bevor es
    diesen Sync gab. NFC-Normalisierung ist Pflicht: Genau daran ist im
    Preisrechner schon einmal der Standortrabatt gescheitert, weil ein "oe" aus
    zwei Codepoints nicht gleich dem aus einem war.
    """
    return unicodedata.normalize('NFC', (name or '')).strip().casefold()


def initialen(name):
    teile = [t for t in (name or '').split() if t]
    if not teile:
        return '?'
    if len(teile) == 1:
        return teile[0][:2].upper()
    return (teile[0][0] + teile[-1][0]).upper()


def rezension_aufbereiten(roh):
    """Ein Places-API-Rezensionsobjekt in unsere Felder uebersetzen."""
    autor = roh.get('authorAttribution') or {}
    text = (roh.get('originalText') or roh.get('text') or {}).get('text', '')
    name = (autor.get('displayName') or '').strip()
    return {
        'quelle_id': roh.get('name', ''),          # stabile Google-Kennung
        'name': name,
        'initialen': initialen(name),
        'sterne': int(roh.get('rating') or 0),
        'text': (text or '').strip(),
        'profil_url': autor.get('uri', '') or '',
        'relativ': roh.get('relativePublishTimeDescription', '') or '',
        'veroeffentlicht': roh.get('publishTime', '') or '',
    }
