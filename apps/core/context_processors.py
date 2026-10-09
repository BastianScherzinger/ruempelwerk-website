"""Context-Processors: Stammdaten, Preise, Leistungsmenü, Bewertungen, Zeitzusagen.

Eingetragen in ``TEMPLATES`` in ``config/settings.py``. Hier steht auch die
kanonische Adresse (``_safe_site_url``), die ``canonical``, Schema und Feed teilen.
"""

from django.conf import settings

from .data.pricing import js_konstanten, preis_context
from .data import firma

# Ohne www – das ist die kanonische Form (s. CanonicalDomainMiddleware).
_CANONICAL_SITE_URL = 'https://ruempelwerk-mitteldeutschland.de'


def _safe_site_url():
    """Liefert IMMER eine absolute URL inklusive Schema.

    SITE_URL kommt aus der Umgebung und stand in Produktion ohne Schema drin
    ('ruempelwerk-mitteldeutschland.de'). Fehlt das 'https://', wertet der
    Browser canonical/hreflang/og:url als *relativen* Pfad – der canonical der
    Startseite zeigte dadurch auf /ruempelwerk-mitteldeutschland.de/, eine
    Seite, die es nicht gibt. Deshalb hier hart normalisieren statt sich auf
    die Umgebungsvariable zu verlassen.
    """
    url = (getattr(settings, 'SITE_URL', '') or '').strip().rstrip('/')
    if not url or '.railway.app' in url:
        return _CANONICAL_SITE_URL
    if not url.startswith(('https://', 'http://')):
        url = 'https://' + url.lstrip('/')
    return url


def global_context(request):
    """Firmendaten, Seitenadresse, Kontaktadressen und Messkennungen für alle Seiten."""
    return {
        # Die Stammdaten (Name, Adresse, Telefon, Steuernummer) kommen aus
        # data/firma.py - seit G5 die einzige Quelle dafuer. Das Impressum hatte
        # sie bis dahin ein zweites Mal von Hand stehen.
        **firma.context(),
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Rümpelwerk Mitteldeutschland'),
        'SITE_URL': _safe_site_url(),
        'DEBUG': settings.DEBUG,
        'ADMIN_EMAIL': getattr(settings, 'ADMIN_EMAIL', ''),
        'CONTACT_EMAIL': getattr(settings, 'CONTACT_EMAIL', ''),
        # EIG246 (25.09.2026): Ohne diesen Schalter geht seit dem 17.09.2026
        # keine Mail an eine eingetippte Adresse (emails._absenden). Rechner
        # und Startseite versprechen das Angebot per E-Mail nur, wenn er an ist.
        'KUNDENMAIL_AN_ABSENDER': getattr(settings, 'KUNDENMAIL_AN_ABSENDER', False),
        # Google-Ads-Conversion-Tracking. Beide Werte sind leer, solange die
        # Env-Variablen fehlen – rw_seo.html und rw_js.html schalten dann still
        # ab. Sie gehoeren in den globalen Context und nicht in einzelne Views,
        # weil Anfrage, Angebot, Anruf und WhatsApp auf verschiedenen Seiten
        # ausgeloest werden; eine Seite ohne die Werte waere eine Seite ohne
        # Conversion-Meldung, und genau solche Luecken faellt niemandem auf.
        'GOOGLE_ADS_ID': getattr(settings, 'GOOGLE_ADS_CONVERSION_ID', ''),
        'GOOGLE_ADS_LABELS': getattr(settings, 'GOOGLE_ADS_LABELS', None) or {},
        # ChatGPT Ads (OpenAI Measurement Pixel), aus demselben Grund hier und
        # nicht in einzelnen Views. Leer heisst: kein SDK, kein Ereignis.
        'OPENAI_PIXEL_ID': getattr(settings, 'OPENAI_PIXEL_ID', ''),
    }


def leistungen_nav(request):
    """Die Leistungsseiten für Navigation und Footer (A2/A3).

    Navigation und Footer liegen auf jeder der ~21 öffentlichen Seiten. Würden
    die Links dort von Hand gepflegt, wäre jede neue Leistungsseite ein Eingriff
    an drei Stellen – und genau so entstehen Seiten ohne eingehende Links. Das
    war der dokumentierte Hauptgrund, warum die alten Landingpages nie indexiert
    wurden (F18).

    Nur Name und URL: Mehr braucht kein Menü, und der Rest der Daten (FAQ,
    Ablauf, Texte) hätte in jedem Seiten-Context nichts zu suchen.
    """
    from .data.cities import (alle_stadtseiten, standorte_nav, REGIONEN,
                              REGIONEN_WORT)
    from .data.services import alle_leistungen
    return {
        'LEISTUNGEN_NAV': [{'name': l['label'], 'url': l['url']}
                           for l in alle_leistungen()],
        # Die sechs Standorte fuer den Staedteblock im Footer. Aus demselben
        # Grund hier und nicht je View: Der Footer steht auf jeder Seite, und
        # eine Seite, deren View die Liste vergessen hat, waere eine Seite mit
        # leerem Block - genau die Sorte Luecke, die niemandem auffaellt.
        'STANDORTE_NAV': standorte_nav(),
        # ⚠ Nicht dasselbe wie STANDORTE_NAV, und das ist der Punkt: Das sind
        # die VIER Betreuungsregionen, jene die SECHS Staedte mit eigenem Team
        # ('Leipzig & Halle' ist EINE Region mit ZWEI Staedten). Der sichtbare
        # Text nannte die Vier bis zum 06.09.2026 an fuenf Stellen getippt,
        # waehrend der Footer darunter sechs Staedte auflistete - P8/G6. Die
        # Begruendung, warum beides richtig ist, steht in data/cities.py.
        'REGIONEN_ANZAHL': len(REGIONEN),
        'REGIONEN_WORT': REGIONEN_WORT,
        # EIG189: "Alle 54 Städte" stand im Footer getippt. Gezaehlt wird, was
        # eine eigene Seite hat - derselbe Name wie im 404-Kontext der Views.
        'STADTSEITEN_ANZAHL': len(alle_stadtseiten()),
    }


def bewertung(request):
    """Der Google-Bewertungsstand fuer JEDE Seite - aus data/reviews.py.

    Vorher lag ``bewertung`` nur im Context der Startseite, die Trustbar steht
    aber auf fuenf Seiten. Sie hat die Zahlen deshalb **hart im Template**
    getragen ("5,0" und "8 Google-Bewertungen") und war damit genau die
    Konstante, die der naechtliche Abgleich abschaffen sollte: Auf der
    Startseite standen 5,0 bei 22, in der Trustbar darueber 5,0 bei 8 - auf
    derselben Seite, wenige hundert Pixel auseinander.

    Als Context-Processor und nicht je View: Die Trustbar ist eine Komponente,
    die jede Seite einbinden darf. Wer sie einbindet, soll nicht daran denken
    muessen, den Stand in seine View zu legen - sonst entsteht die naechste
    Seite mit leerer Bewertungszeile.
    """
    from .data import auszeichnungen, reviews
    # ``trustlocal``: Rang/Symbol der Trustlocal-Zeile (Hero, Trustbar) - eine Quelle.
    return {'bewertung': reviews.stand(), 'trustlocal': auszeichnungen.TRUSTLOCAL}


def preise(request):
    """Stellt jedem Template die Preise zur Verfügung – aus data/pricing.py.

    Damit gilt für Preise dieselbe Regel wie für die Kontaktadressen: Der Wert
    kommt aus einer Quelle, nicht aus dem Template. Vorher standen 11 veraltete
    Preisangaben in drei Templates, die den Rechner um bis zu 67 % unterboten.

    ``PREISE_JS`` ist derselbe Satz Zahlen für den Wizard im Browser. Das
    Template gibt ihn per ``|json_script`` als ``application/json``-Block aus,
    nicht als JS-Literal: Die Doppelrechnung muss bleiben (der Server darf dem
    Client-Preis nicht trauen), aber sie darf nicht mehr auseinanderlaufen.
    """
    ctx = preis_context()
    ctx['PREISE_JS'] = js_konstanten()
    return ctx


def zusagen(request):
    """Die Zeitzusagen fuer JEDE Seite - aus data/zusagen.py (Befund K2).

    Dieselbe Begruendung wie bei ``bewertung`` und ``preise``: Das
    Antwortzeit-Versprechen steht auf der Startseite, der Anfrageseite, in
    ``ueber-uns``, ``dienstleistungen`` und in der Bestaetigungsmail. Solange
    es in jedem Template getippt war, stand dort ueber Monate ein Satz, den der
    Betrieb nur fuer 4 von 54 Staedten halten kann.

    Als Context-Processor und nicht je View, weil jede Vorlage die Zusage
    einbinden darf, ohne dass ihre View davon wissen muss.
    """
    from .data.zusagen import zusagen_context
    return zusagen_context()
