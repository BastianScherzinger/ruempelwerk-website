"""Die drei eigenen Middlewares - und warum ihre Reihenfolge festliegt.

* ``CanonicalDomainMiddleware`` ist der **erste** Eintrag in ``MIDDLEWARE``,
  noch vor Djangos ``SecurityMiddleware``: Sie leitet ``www.…`` und die
  Altdomain pfaderhaltend auf die kanonische Adresse - **GET/HEAD mit 301,
  alles andere mit 308**, denn ein 301 auf einen POST wirft die Daten weg.
* ``SecurityHeadersMiddleware`` setzt die Sicherheitskopfzeilen, allen voran
  die CSP (mit ``unsafe-eval`` nur auf ``/ueber-uns/``, wegen des
  TrustLocal-Widgets), und schreibt das Besuchsprotokoll mit anonymisierter
  IP.
* ``HtmlEinrueckungMiddleware`` muss der **letzte** Eintrag bleiben. Die
  Antwortphase laeuft von unten nach oben; nur so rechnet ``CommonMiddleware``
  das ``Content-Length`` auf dem bereits gekuerzten HTML aus, und nur so
  bildet ``ConditionalGetMiddleware`` den ETag ueber dem ausgelieferten Stand.

Beide Reihenfolgen rechnet ``apps/core/tests/test_middleware.py`` nach, statt
sie zu behaupten. Die Vorgeschichte steht in ``docs/architektur.md``.
"""

import ipaddress
import logging
import re
import uuid
from django.http import HttpResponsePermanentRedirect
from .antispam import client_ip
from .models import PageVisit

logger = logging.getLogger('apps.core')

# ── Kanonische Domain ────────────────────────────────────────────────────────
# Die Seite ist unter mehreren Hosts erreichbar. Ohne Weiterleitung fuehrt
# Google sie als getrennte Seiten und teilt die Signale auf: Die Search Console
# zeigte fuer die Startseite 532 Impressionen auf Position 10,7 (nackt) neben
# 38 Impressionen auf Position 53,5 (www) – dieselbe Seite, zwei Eintraege.
#
# Kanonisch ist die WWW-LOSE Form. Das ist keine freie Wahl, sondern der
# Ist-Zustand: SITE_URL, der ausgelieferte <link rel="canonical">, die
# Sitemap-Zeile in robots.txt und die staerkeren Rankings zeigen alle dorthin.
#
# Der Redirect kann NICHT bei Cloudflare liegen (so stand es in HANDOFF.md):
# Cloudflare proxied diese Domains nicht mehr, DNS loest direkt auf Railway auf
# (keine cf-ray-Header). Deshalb hier in der Anwendung.
#
# Schleifenfrei, weil _CANONICAL_HOST selbst nie in _REDIRECT_HOSTS steht.
# Genau diese Absicherung fehlte dem frueheren Redirect, der deswegen entfernt
# wurde. Railway-interne *.up.railway.app bleiben unangetastet, sonst brechen
# Healthchecks und Deployment-Previews.
_CANONICAL_HOST = 'ruempelwerk-mitteldeutschland.de'

_REDIRECT_HOSTS = frozenset({
    'www.ruempelwerk-mitteldeutschland.de',
    # Altdomain: war die urspruenglich indexierte Seite. Ohne diesen 301
    # verfaellt ihre komplette Autoritaet.
    'deutsches-ruempelwerk.com',
    'www.deutsches-ruempelwerk.com',
})


class _PermanentRedirectKeepMethod(HttpResponsePermanentRedirect):
    """308 statt 301 – erhaelt Methode und Body.

    Ein 301 auf einen POST ist datenvernichtend: Browser wiederholen ihn als
    GET ohne Body. Wer das CMS unter ``/<STATS_PATH>/aktuelles/neu/`` ueber die
    www-Adresse aufruft, haette beim Hochladen eines Beitrags Text und Bilder
    verloren und waere kommentarlos auf der Login-Seite gelandet.
    """
    status_code = 308


def dauerhaft_weiter(ziel, request):
    """Dauerhafte Weiterleitung, die keine Daten verliert.

    GET und HEAD bekommen **301** – das ist der Code, den Suchmaschinen als
    dauerhafte Adressaenderung werten, und darum geht es bei einer
    Weiterleitung fast immer. Alles andere bekommt **308**: Ein 301 auf einen
    POST ist datenvernichtend, der Browser wiederholt ihn als GET ohne Body.

    Diese Unterscheidung gehoert an **jede** dauerhafte Weiterleitung, nicht
    nur an die der kanonischen Domain. Am 18.09.2026 antwortete ``/kontakt/``
    noch mit einem nackten 301 auf ``/anfrage/`` – ein Formular, das (aus einem
    alten Lesezeichen, einem fremden Link oder einem Prospekt) dorthin postete,
    verlor stillschweigend seinen Rumpf. Wer eine neue Weiterleitung baut,
    ruft diese Funktion auf, statt ``HttpResponsePermanentRedirect`` direkt zu
    nehmen.

    Was sie **nicht** leistet: Sie entscheidet nicht, ob eine Weiterleitung
    ueberhaupt richtig ist (301 gegen 302 gegen 410), und sie kann einen
    POST auf ein Ziel, das gar keinen entgegennimmt, nur weiterreichen – dort
    wird dann ein 405 fallen. Das ist die ehrliche Antwort, kein stiller
    Datenverlust.
    """
    if request.method in ('GET', 'HEAD'):
        return HttpResponsePermanentRedirect(ziel)
    return _PermanentRedirectKeepMethod(ziel)


class CanonicalDomainMiddleware:
    """Leitet alle Nebendomains pfaderhaltend auf die kanonische Domain.

    Steht als ERSTER Eintrag in MIDDLEWARE – vor SecurityMiddleware. Dadurch
    wird aus ``http://www.example.de/x`` ein einziger Hop direkt auf
    ``https://example.de/x``; laege sie dahinter, kaeme erst der http->https-
    Redirect und danach noch einer fuer den Host.

    GET und HEAD bekommen 301 – das ist der Code, den Suchmaschinen als
    dauerhafte Adressaenderung werten, und darum geht es hier. Alles andere
    bekommt 308, damit Formulare und Uploads nicht unterwegs zerfallen.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower()
        if host in _REDIRECT_HOSTS:
            target = f'https://{_CANONICAL_HOST}{request.get_full_path()}'
            return dauerhaft_weiter(target, request)
        return self.get_response(request)

# HINWEIS zu fonts.googleapis.com / fonts.gstatic.com:
# Die *oeffentlichen* Seiten laden seit dem Performance-Umbau KEINE Google Fonts
# mehr – Montserrat und Open Sans liegen als WOFF2 in static/fonts/ und werden
# in static/css/ruempelwerk.css per @font-face eingebunden.
#
# Es ist seit dem 06.09.2026 (P8/G2) genau **eine** Quelle uebrig, die die
# beiden Hosts noch braucht:
#   * templates/stats/*.html – die vier Vorlagen des internen Dashboards und
#     des CMS (dashboard.html, login.html, cms_list.html, cms_form.html) laden
#     JetBrains Mono und DM Sans ueber fonts.googleapis.com.
#
# Der Kommentar nannte bis dahin drei Quellen; zwei davon sind mit A1 entfallen
# (die 404- und die 500-Seite laden keine Google Fonts mehr, und
# static/css/base.css hat seinen @import Inter verloren). Gemessen am
# 06.09.2026: `grep -rn "fonts.googleapis" templates/` trifft ausschliesslich
# templates/stats/ – 12 Zeilen in vier Dateien, sonst nichts im Repository.
#
# **Der naechste Schritt, falls jemand die Eintraege loswerden will:** Diese
# vier Vorlagen auf selbst gehostete Schriften umstellen (oder auf den
# Systemschrift-Stack, den base.html seit A1 nutzt). Danach duerfen
# https://fonts.googleapis.com bei style-src und https://fonts.gstatic.com bei
# font-src **ersatzlos** verschwinden – es ist der letzte Rest Google-Schrift
# im ganzen Projekt. Vorher nicht: ohne die Hosts blockiert die CSP das
# Stylesheet, und das interne Dashboard steht in der Systemschrift da.
# ── Warum in script-src Hashes stehen und kein 'unsafe-inline' (SI09) ───────
# Bis zum 08.09.2026 stand hier ``'unsafe-inline'``. Es entwertet die
# Richtlinie gegen eingeschleusten Code vollstaendig: Erlaubt ist damit jedes
# Skript, das im HTML steht - also genau das, was ein XSS dort hineinschreibt.
#
# Der Grund, aus dem es so lange dastand, waren **inline Ereignis-Attribute**.
# Ein Nonce deckt die NICHT ab (CSP kennt Nonces nur an ``<script>``-Bloecken,
# nie an ``onclick="…"``), und ein Hash ebenso wenig. Nachgezaehlt am
# 08.09.2026 ueber templates/: 29 Attribute auf oeffentlichen Seiten
# (rw_rechner.html 17, standorte.html 8, home.html 2, jobs.html 2,
# rw_footer.html 1 - der Cookie-Knopf steht auf JEDER Seite) und 12 unter
# templates/stats/. Sie sind mit SI32 nach static/js/rw_handler.js gewandert
# und binden jetzt ueber ``data-rw-*``.
#
# **Warum Hashes und kein Nonce.** Ein Nonce muss je Anfrage neu sein. Damit
# aendert sich das HTML bei jedem Aufruf, der ETag wechselt mit, und die 304er
# aus P8/E2 waeren weg - gemessen 13 von 88 Adressen, 904,4 von 10.963 KiB
# (8,2 %). Ein Hash kostet das nicht: Das HTML bleibt byteweise gleich, der
# ETag bleibt stabil, und die Richtlinie ist genauso scharf. Der Preis steht an
# anderer Stelle: **Wer eine Zeile in einem der drei Bloecke aendert, muss den
# Hash hier nachziehen** - sonst blockiert der Browser den Block, und zwar
# still. Deshalb rechnet ``test_middleware.py`` jeden dieser Hashes ueber dem
# **ausgelieferten** HTML nach und nennt im Fehlerfall den richtigen Wert.
#
# Die drei Bloecke, die es noch gibt, und warum sie inline bleiben muessen:
#   1. rw_seo.html      - der Consent-Bootstrap. Er setzt die Standard-
#                         Einwilligung auf "abgelehnt", bevor irgendetwas
#                         laedt; als externe Datei liefe er zu spaet.
#   2. rw_css.html      - der Umschalter, der das nachgeladene Stylesheet von
#                         media="print" auf "all" setzt.
#   3. rw_antispam.py   - der JavaScript-Nachweis der Spam-Abwehr (Regel 18).
# Alle drei sind seit dem 08.09.2026 **statisch**: Die zwei Kennungen des
# Consent-Bootstraps kommen aus data-Attributen am Tag, und Attribute gehen in
# den Hash nicht ein. Waeren sie im Koerper geblieben, haette jede Umgebung
# ihren eigenen Hash.
#
# Ausgelagert wurden dafuer zwei weitere Bloecke, die kein Inline sein mussten:
# die Zaehleranimation des Dashboards (static/js/rw_stats_dashboard.js) und die
# Formularoberflaeche des CMS (static/js/rw_cms_form.js) - letztere setzte
# ``{{ stats_path }}`` in ein Template-Literal und war deshalb gar nicht
# hashbar.
#
# ``'unsafe-hashes'`` bzw. ``script-src-attr 'unsafe-inline'`` waeren die
# Abkuerzung gewesen, die Attribute stehen zu lassen - beide verworfen:
# Browser ohne Unterstuetzung fuer ``script-src-attr`` (Safari vor 15.4) fallen
# auf ``script-src`` zurueck und haetten dann einen toten Preisrechner, ohne
# dass es hier jemand sieht.
#
# ⚠ **Ein Hash hebt 'unsafe-inline' auf.** Sobald eine Quellenliste einen Hash
# oder ein Nonce enthaelt, ignoriert der Browser ein daneben stehendes
# 'unsafe-inline'. Wer hier einen vierten Inline-Block ergaenzt, ohne seinen
# Hash einzutragen, bekommt ihn also nicht "zur Sicherheit" ausgefuehrt - er
# faellt aus.
#
# ``object-src 'none'`` ist am 08.09.2026 dazugekommen: 'default-src' deckt
# Plugins zwar mit ab, aber nur solange niemand eine eigene Regel danebenstellt.
# Die Direktive kostet nichts - die Seite bindet kein <object>, <embed> und kein
# <applet> ein (nachgezaehlt: 0 Treffer in templates/).
_INLINE_SKRIPT_HASHES = (
    # components/rw_seo.html - Consent-Bootstrap (gtag + OpenAI-Pixel)
    "'sha256-46tOw/0aUOM7QjdAjwokCVpw2eXi1/x+59cKdcCQoDs='",
    # components/rw_css.html - Stylesheet von media="print" auf "all"
    "'sha256-V1tU2epY+lZbPUltl3VRewhN9PLZLr+K+SXAh9aCcgU='",
    # templatetags/rw_antispam.py::_SKRIPT - der JavaScript-Nachweis
    "'sha256-we6S1/pCsFlHx5t8kZ1VkYR0gIGtnU5DA1sf5uZpv+Y='",
)

_CSP = (
    "default-src 'self'; "
    # googleadservices: gtag.js laedt von dort das Conversion-Skript nach,
    # sobald ein AW-Ziel konfiguriert ist. Fehlt der Host, scheitert die
    # Conversion-Meldung still – dieselbe Fehlerklasse wie die 54 Stadtseiten,
    # die monatelang ohne Analytics liefen, ohne dass es jemand sah.
    # trustlocal: das Bewertungswidget auf /ueber-uns/. Ohne den Host laedt
    # es still nicht - dieselbe Fehlerklasse wie oben.
    # bzrcdn.openai.com: das SDK des ChatGPT-Ads-Pixels (oaiq.min.js). Es wird
    # erst nach der Einwilligung nachgeladen (rw_seo.html) - fehlt der Host,
    # scheitert es genau wie die beiden Faelle darueber **still**.
    "script-src 'self' " + ' '.join(_INLINE_SKRIPT_HASHES) + " https://www.googletagmanager.com https://*.googletagmanager.com https://www.googleadservices.com https://static.trustlocal.de https://bzrcdn.openai.com; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    # trustlocal liefert Poppins/Mulish fuer sein Widget mit. Ohne den Host
    # faellt es auf die Systemschrift zurueck - kein Ausfall, aber ein
    # sichtbarer Bruch mitten auf der Seite.
    "font-src 'self' https://fonts.gstatic.com https://static.trustlocal.de; "
    # Die Ads-Conversion selbst wird als Pixel gegen google.com/.de und
    # googleads.g.doubleclick.net geschickt – deshalb stehen sie bei img-src
    # *und* connect-src: gtag nimmt je nach Browser Bild oder fetch/Beacon.
    # bzr.openai.com steht aus demselben Grund bei img-src *und* connect-src wie
    # Googles Hosts: Der OpenAI-Pixel schickt sein Ereignis per fetch bzw.
    # sendBeacon und faellt, wo das nicht geht, auf eine Bildanfrage zurueck.
    "img-src 'self' data: blob: https://*.tile.openstreetmap.org https://tile.openstreetmap.org https://res.cloudinary.com https://*.cloudinary.com http://res.cloudinary.com http://*.cloudinary.com https://www.googletagmanager.com https://www.google-analytics.com https://*.google-analytics.com https://www.googleadservices.com https://googleads.g.doubleclick.net https://www.google.com https://www.google.de https://static.trustlocal.de https://trustlocal.de https://bzr.openai.com; "
    "frame-src https://www.openstreetmap.org; "
    # Kein <object>, <embed>, <applet> - und damit auch keine Flash- oder
    # PDF-Plugin-Umgehung der uebrigen Direktiven.
    "object-src 'none'; "
    # bzr.openai.com nimmt die Ereignisse entgegen, bzrcdn.openai.com liefert
    # zusaetzlich die Konfiguration je Pixel nach - beide Hosts nennt OpenAIs
    # eigene CSP-Tabelle, und beide fehlen bemerkt niemand von allein.
    "connect-src 'self' https://www.google-analytics.com https://*.google-analytics.com https://*.analytics.google.com https://www.googletagmanager.com https://www.googleadservices.com https://googleads.g.doubleclick.net https://www.google.com https://www.google.de https://trustlocal.de https://static.trustlocal.de https://bzr.openai.com https://bzrcdn.openai.com; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self';"
)


# ── Die eine Seite mit gelockerter CSP ──────────────────────────────────────
# Das TrustLocal-Widget auf /ueber-uns/ rendert mit Handlebars, und Handlebars
# kompiliert seine Templates ueber `new Function(...)`. Ohne 'unsafe-eval'
# bricht es mit "Error rendering widget: EvalError" ab - gemessen am
# 27.08.2026, nicht vermutet.
#
# **'unsafe-eval' steht deshalb NUR hier und nicht in _CSP.** Global erlaubt es
# jedem Skript auf allen 85 Seiten, Zeichenketten als Code auszufuehren - das
# ist der Unterschied zwischen "ein Widget darf sein Template kompilieren" und
# "eine XSS-Luecke wird ausnutzbar". Der Preis fuer das Widget ist eine
# schwaechere CSP; er wird auf **einer** Seite bezahlt statt auf allen.
#
# Warum ausgerechnet diese Seite vertretbar ist: /ueber-uns/ traegt **kein
# Formular** (nachgezaehlt: 0 `<form>`), 'form-action' bleibt ohnehin 'self',
# und der Host steht nicht bei 'frame-src'.
#
# Wer das Widget auf eine weitere Seite legt, traegt sie hier ein - und fragt
# sich vorher, ob diese Seite ein Formular hat.
_CSP_EVAL_PFADE = ('/ueber-uns/',)

# 'unsafe-eval' an script-src anhaengen, den Rest der Richtlinie unveraendert
# lassen. String-Ersetzung statt zweiter Konstante: Zwei vollstaendige
# CSP-Strings nebeneinander laufen garantiert auseinander - dieselbe Sorte
# Doppelpflege, die dieses Projekt an anderer Stelle abgeschafft hat.
_CSP_MIT_EVAL = _CSP.replace("script-src 'self'",
                             "script-src 'self' 'unsafe-eval'", 1)


# ── Cache-Control fuer HTML ─────────────────────────────────────────────────
# Gemessen am 06.09.2026 (P8/E2): Die Antwort einer oeffentlichen Seite trug
# **keinen** Cache-Control-Header. Dass trotzdem nichts zwischengespeichert
# wurde, lag allein an 'Vary: Cookie' – und das war ein Nebeneffekt, kein
# Vorsatz (siehe RequestLoggingMiddleware weiter unten). Ein Schutz, der aus
# einem Nebeneffekt besteht, verschwindet mit dem Nebeneffekt.
#
# Ohne Cache-Control darf ein zwischengeschalteter Cache eine 200er-Antwort
# **heuristisch** speichern (RFC 9111, 4.2.2) – und 75 der 81 Sitemap-Seiten
# tragen ein Formular mit CSRF-Token. Eine heuristisch gecachte Seite mit
# fremdem Token ist genau der Schaden, vor dem P8/E2 warnt.
#
# Deshalb steht der Header jetzt ausdruecklich da:
#   private   – nur der Browser des Besuchers darf speichern, kein Proxy,
#               kein CDN. Damit kann kein CSRF-Token und keine
#               Bewertungszahl (Regel 2) bei einem Fremden landen.
#   no-cache  – speichern erlaubt, ausliefern nur nach Rueckfrage. Zusammen
#               mit dem ETag aus ConditionalGetMiddleware wird daraus ein
#               304 fuer die Seiten, deren HTML sich nicht aendert.
#
# **Bewusst NICHT 'no-store':** no-store nimmt dem Browser auch den
# Back-Forward-Cache; der Zurueck-Knopf laedt die Seite dann neu. 'private'
# reicht fuer den Schutz vollstaendig aus.
#
# **Was dieser Header NICHT leistet:** Er macht keine einzige Seite schneller.
# Er verhindert, dass eine Seite falsch gecacht wird. Der Fall "82 statische
# Seiten mit public, max-age=300 ausliefern" ist am 06.09.2026 geprueft und
# **verworfen** worden – nachgezaehlt kamen dafuer 5 von 81 Seiten in Frage
# (alle anderen tragen ein Formular), und die Startseite, die einzige davon
# mit Gewicht, traegt die aggregateRating aus der Datenbank.
_CACHE_CONTROL_HTML = 'private, no-cache'


class SecurityHeadersMiddleware:
    """Sicherheitskopfzeilen, Cache-Steuerung und das Besuchsprotokoll.

    Drei Dinge in einer Middleware, weil alle drei jede Antwort betreffen: die
    CSP (auf ``/ueber-uns/`` mit ``unsafe-eval``, siehe ``_CSP_EVAL_PFADE``),
    ``Cache-Control: private, no-cache`` auf jeder HTML-Antwort samt ``Vary:
    Cookie`` nur dort, wo ein CSRF-Token steht, und der ``PageVisit``-Eintrag
    mit anonymisierter IP.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Die Kanonisierung zwischen www und nackter Domain macht
        # CanonicalDomainMiddleware (s. o.), nicht mehr der canonical-Tag allein.
        response = self.get_response(request)
        csp = (_CSP_MIT_EVAL if request.path in _CSP_EVAL_PFADE else _CSP)
        response.setdefault('Content-Security-Policy', csp)
        response.setdefault('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
        # setdefault, nicht Zuweisung: Djangos Admin setzt per @never_cache
        # eine schaerfere Richtlinie, und die muss gewinnen. (Nachgesehen am
        # 06.09.2026: In apps/ steht kein einziges @never_cache – die Seiten
        # unter STATS_PATH bekommen also diesen allgemeinen Header. 'private'
        # haelt sie aus jedem gemeinsamen Cache heraus, das ist vertretbar;
        # eine bewusste Entscheidung ist es nicht, und sie steht deshalb im
        # Test test_never_cache_wird_nicht_ueberschrieben ausgeschrieben.)
        # Nur HTML – sitemap.xml, llms.txt und robots.txt sind
        # oeffentlich und tragen weder Token noch Bewertungszahl; sie bekommen
        # von ConditionalGetMiddleware einen stabilen ETag und damit 304er
        # fuer Crawler, was hier der eigentliche Gewinn ist.
        if response.get('Content-Type', '').startswith('text/html'):
            response.setdefault('Cache-Control', _CACHE_CONTROL_HTML)
        # EIG61 (24.09.2026): Jeder Host ausser der kanonischen Domain bekommt
        # 'X-Robots-Tag: noindex'. Die Railway-Adresse *.up.railway.app
        # liefert dieselben Seiten aus (sie wird oben bewusst NICHT
        # umgeleitet, sonst brechen Healthchecks und Previews) - ohne den
        # Header kann Google sie als Dublette indexieren. Ein Header aendert
        # den ETag nicht: der wird ueber dem Rumpf gebildet.
        if _host_ohne_port(request) != _CANONICAL_HOST:
            response.setdefault('X-Robots-Tag', 'noindex')
        return response


def _host_ohne_port(request):
    """Der angefragte Host ohne Port, klein geschrieben."""
    return request.get_host().split(':')[0].lower()

_SKIP_PREFIXES = ('/static/', '/media/', '/favicon.ico', '/health/')

_BOT_KEYWORDS = (
    'bot', 'spider', 'crawl', 'google', 'bing', 'slurp', 'baidu',
    'facebookexternalhit', 'python-urllib', 'python-requests',
    'curl', 'wget', 'go-http', 'okhttp', 'apache-httpclient',
    'google-read-aloud', 'googlebot', 'bingbot', 'yandex',
)

def _is_bot(user_agent: str) -> bool:
    ua = user_agent.lower()
    return any(k in ua for k in _BOT_KEYWORDS)


def _anonymize_ip(ip):
    """Kuerzt eine IP-Adresse so, dass sie keinem Anschluss mehr zuzuordnen ist.

    IPv4 auf /24 (letztes Feld 0), IPv6 auf /48 (EIG64, 24.09.2026). Bis dahin
    wurde bei IPv6 nur das letzte der acht Felder genullt - ein Haushalt
    bekommt aber ein ganzes /56- oder /64-Praefix, die gespeicherte Adresse
    blieb also dem Anschluss zuordenbar. /48 ist das, was die
    Datenschutzerklaerung seitdem nennt; wer die Laenge aendert, zieht den
    Satz dort (Abschnitt 3, "Eigenes Besuchsprotokoll") nach.
    """
    if not ip:
        return None
    try:
        adresse = ipaddress.ip_address(ip.strip())
    except ValueError:
        return None
    praefix = 24 if adresse.version == 4 else 48
    return str(ipaddress.ip_network(f'{adresse}/{praefix}', strict=False).network_address)


class RequestLoggingMiddleware:
    """Protokolliert jeden Aufruf – und traegt seit dem 06.09.2026 nicht mehr
    die Zwischenspeicherung der ganzen Website ab.

    **Der Befund P8/E2, und wo er wirklich herkam.** Live gemessen am
    06.09.2026 trug jede Antwort ``Vary: Cookie``. Der Verdacht lag auf
    ``SessionMiddleware`` oder ``CsrfViewMiddleware``. Nachgemessen wurde es
    mit einem Spion auf ``django.utils.cache.patch_vary_headers``, und die
    Antwort war eine andere: ``SessionMiddleware`` setzt den Header genau
    dann, wenn ``request.session.accessed`` wahr ist – und der **einzige**
    Zugriff auf die Session einer formularlosen Seite (gemessen auf
    ``/impressum/`` und ``/galerie/``: genau 1 Zugriff) kam aus der Zeile
    darunter, aus ``middleware.py`` selbst:

        uid = user.pk if (user and user.is_authenticated) else 'anon'

    ``request.user`` ist ein ``SimpleLazyObject``. Wer ihn auswertet, loest
    ``auth.get_user(request)`` aus, das liest ``request.session[…]``, das
    setzt ``accessed = True``, und das ergibt ``Vary: Cookie`` – auf **jeder**
    Seite, auch auf den 6, die kein Formular tragen.

    Bezahlt wurde das fuer eine Zeile, die im Betrieb **nie erscheint**: Der
    Logger ``apps.core`` steht ohne DEBUG auf INFO (``config/settings.py``),
    ``logger.debug(...)`` verwirft die Nachricht also. Der Argumentwert wird
    aber vor dem Aufruf berechnet – der Logger kann nichts sparen, was der
    Aufrufer schon ausgegeben hat. Deshalb steht die Ermittlung jetzt hinter
    ``logger.isEnabledFor(logging.DEBUG)``.

    **Was das aendert und was nicht.** Seiten ohne CSRF-Token verlieren
    ``Vary: Cookie``; Seiten mit Formular behalten es, weil
    ``CsrfViewMiddleware`` es beim Setzen des ``csrftoken``-Cookies selbst
    anhaengt. Der Header steht damit genau dort, wo er hingehoert. Weil er
    aber, sobald der Besucher das Cookie einmal hat, auch dort wegfaellt,
    darf er nicht laenger der einzige Schutz sein: Den uebernimmt seitdem der
    ausdrueckliche ``Cache-Control: private, no-cache`` in
    ``SecurityHeadersMiddleware``.

    **Was diese Aenderung NICHT leistet:** Sie macht die Seite nicht messbar
    schneller. Fuer einen anonymen Besucher ohne ``sessionid``-Cookie kostete
    der Zugriff keine Datenbankabfrage (``session_key is None`` → leeres
    Dict); gespart wird eine Abfrage nur bei Besuchern, die aus einer
    frueheren Anmeldung noch ein Session-Cookie mitbringen. Der Gewinn ist
    der Header, nicht die Zeit. Und unter ``DEBUG=True`` ist ``Vary: Cookie``
    weiterhin ueberall da – die Logzeile wird dann ja gebraucht.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        skip = any(path.startswith(p) for p in _SKIP_PREFIXES)

        # Die Abfrage auf den Loglevel ist der Punkt der ganzen Uebung, siehe
        # Docstring: request.user auszuwerten setzt Vary: Cookie auf JEDER
        # Seite, und die Nachricht wird im Betrieb ohnehin verworfen.
        if not skip and logger.isEnabledFor(logging.DEBUG):
            user = getattr(request, 'user', None)
            uid = user.pk if (user and user.is_authenticated) else 'anon'
            logger.debug('%s %s [user=%s]', request.method, path, uid)

        # Read session cookie before processing (so we have it for tracking)
        sid = request.COOKIES.get('rwsid') if not skip else None

        response = self.get_response(request)

        if not skip and request.method == 'GET' and response.status_code == 200:
            ua = request.META.get('HTTP_USER_AGENT', '')
            # Regel 19: dieselbe IP-Ermittlung wie die Spam-Abwehr. Bis zum
            # 24.09.2026 stand hier der erste Eintrag aus X-Forwarded-For -
            # den schickt der Absender selbst mit. client_ip() nimmt zuerst
            # X-Envoy-External-Address, die Railways Proxy setzt.
            ip = _anonymize_ip(client_ip(request))

            # Einmal ermitteln, zweimal benutzt: fuer die Markierung der Zeile
            # und fuer das Session-Tracking weiter unten. Vorher lief _is_bot()
            # nur fuer das Session-Tracking – deshalb stand in PageVisit
            # jahrelang nicht drin, ob die Zeile von einem Crawler stammt.
            ist_bot = _is_bot(ua)

            try:
                PageVisit.objects.create(
                    path=path[:512],
                    ip_address=ip,
                    user_agent=ua[:512],
                    # P8/E1: markieren statt wegwerfen. Die Begruendung samt
                    # Messung steht im Docstring von PageVisit – kurz: dies
                    # ist das einzige Crawl-Protokoll dieser Website, und die
                    # Besucherzahl, die der Betrieb liest, kommt aus
                    # VisitorSession und nicht aus dieser Tabelle.
                    ist_bot=ist_bot,
                )
            except Exception as e:
                logger.warning('PageVisit konnte nicht gespeichert werden: %s', e)

            # Session-Tracking (Statistik-Cookie rwsid) – nur mit Einwilligung
            # (Cookie-Banner: rw_consent=all). Bots werden ohnehin übersprungen.
            consent = request.COOKIES.get('rw_consent')
            if not ist_bot and consent == 'all':
                if not sid:
                    sid = uuid.uuid4().hex
                try:
                    _track_visitor_session(sid, ip or '')
                except Exception as e:
                    logger.warning('Session-Tracking Fehler: %s', e)

                from django.conf import settings as _dj_settings
                response.set_cookie(
                    'rwsid', sid,
                    max_age=1800,
                    httponly=True,
                    samesite='Lax',
                    secure=not _dj_settings.DEBUG,
                )

        return response


def _track_visitor_session(session_id: str, ip_hash: str) -> None:
    from django.utils import timezone
    from django.db import models as db_models
    from .models import VisitorSession

    from django.utils.timezone import localdate
    now = timezone.now()
    today = localdate()

    session, created = VisitorSession.objects.get_or_create(
        session_id=session_id,
        date=today,
        defaults={
            'ip_hash': ip_hash,
            'started_at': now,
            'last_seen': now,
            'page_count': 1,
        },
    )
    if not created:
        VisitorSession.objects.filter(pk=session.pk).update(
            last_seen=now,
            page_count=db_models.F('page_count') + 1,
        )


# ── Einrueckung aus dem ausgelieferten HTML ─────────────────────────────────
# Gemessen am 01.09.2026 (Aufgabe 1 "Seitengewicht: Puffer schaffen"):
# Von den 165,5 KiB der Seite /entruempelung-kosten/ sind **14,6 KiB** reine
# Einrueckung - Leerzeichen am Zeilenanfang, die es nur gibt, weil die
# Vorlagen eingerueckt geschrieben sind. Median ueber alle 81 Sitemap-Seiten:
# 154,1 -> 140,9 KiB. Das ist nach den Ortschips der groesste rein
# mechanische Posten, und er steht auf JEDER Seite.
#
# Warum das gefahrlos ist: HTML faltet jede Folge von Leerraum in EIN
# Leerzeichen (CSS 'white-space: normal'). "\n      <p>" und "\n<p>" rendern
# identisch. Entfernt wird deshalb ausschliesslich die Einrueckung NACH einem
# Zeilenumbruch; der Umbruch selbst bleibt stehen, es werden nie zwei Zeilen
# zusammengezogen und nie zwei Woerter aneinandergeklebt. Genau daran
# scheitert Djangos {% spaceless %}, das Leerraum ZWISCHEN Tags restlos
# entfernt und aus "<strong>a</strong> <em>b</em>" ein "ab" macht.
#
# Vier Container sind ausgenommen, weil in ihnen Leerraum bedeutungstragend
# ist bzw. der Inhalt gar kein HTML ist:
#   <pre> und <textarea>  - 'white-space: pre', jedes Leerzeichen zaehlt
#   <script>              - JSON-LD und die Skripte; ein Template-Literal
#                           wuerde seinen Inhalt aendern
#   <style>               - das kritische CSS
# Nachgesehen: In static/css/ruempelwerk.css steht 'white-space' 30-mal, aber
# nie mit 'pre'/'pre-wrap'/'pre-line' - nur 'nowrap'. Es gibt also keine
# weitere Stelle, an der Leerraum erhalten bleiben muesste.
#
# **Was diese Middleware NICHT leistet:** Sie macht die Auslieferung nicht um
# 13 KiB schneller. Ueber die Leitung geht gzip-komprimiertes HTML, und
# Einrueckung ist das, was ein Kompressor am besten wegpackt - gemessen
# bleiben davon **1,1 bis 1,2 KiB** je Seite uebrig. Der Gewinn ist der
# unkomprimierte Umfang, den der Browser parst, und der Kopfraum unter der
# Schwelle von check_seo. Wer daraus "die Seite ist jetzt 8 % schneller"
# macht, hat die Zahl falsch gelesen.
#
# Sie ersetzt auch keine inhaltliche Diaet: 30,6 KiB Preisrechner-Markup auf
# 69 Seiten sind nach wie vor der groesste Einzelposten der Website, und die
# Middleware ruehrt daran nicht.
_SCHUTZ_RE = re.compile(r'<(pre|textarea|script|style)\b[^>]*>.*?</\1\s*>',
                        re.S | re.I)
_EINRUECKUNG_RE = re.compile(r'\n[ \t]+')


def _ohne_einrueckung(html):
    """Entfernt die Einrueckung ausserhalb der geschuetzten Container."""
    teile = []
    pos = 0
    for m in _SCHUTZ_RE.finditer(html):
        teile.append(_EINRUECKUNG_RE.sub('\n', html[pos:m.start()]))
        teile.append(m.group(0))
        pos = m.end()
    teile.append(_EINRUECKUNG_RE.sub('\n', html[pos:]))
    return ''.join(teile)


class HtmlEinrueckungMiddleware:
    """Streicht die Einrueckung aus jeder HTML-Antwort.

    Steht als LETZTER Eintrag in MIDDLEWARE. Die Antwortphase laeuft von
    innen nach aussen, der letzte Eintrag ist also der erste, der die Antwort
    sieht - dadurch rechnet CommonMiddleware das 'Content-Length' auf dem
    bereits gekuerzten Text aus. Umgekehrt stuende dort eine zu grosse Zahl.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Streaming-Antworten haben kein .content; bereits kodierte
        # (gzip) duerfen nicht angefasst werden; alles ausser text/html
        # ist entweder Nutzlast (Bilder) oder leerraumempfindlich
        # (sitemap.xml wird nicht angefasst, llms.txt schon gar nicht).
        if getattr(response, 'streaming', False):
            return response
        if response.has_header('Content-Encoding'):
            return response
        if not response.get('Content-Type', '').startswith('text/html'):
            return response
        try:
            html = response.content.decode(response.charset)
        except (UnicodeDecodeError, AttributeError):    # pragma: no cover
            return response
        response.content = _ohne_einrueckung(html).encode(response.charset)
        return response
