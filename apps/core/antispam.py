"""Spam-Abwehr fuer die oeffentlichen Formulare.

Anlass: In der Nacht zum 25.08.2026 lief ueber Stunden ein Formular-Bot gegen
``/anfrage/``. Immer derselbe Name (``RobertPrant``), immer Leistung
``Entruempelung``, wechselnde Wegwerf-Adressen, alle 1-5 Minuten eine Mail ins
Postfach. Die vorhandene Abwehr hat aus drei Gruenden nichts gemerkt:

1. ``_is_rate_limited`` zaehlte auf ``REMOTE_ADDR``. Hinter Railways Proxy ist
   das nie der Client, sondern eine interne 100.64.0.x, die pro Request
   wechselt - der Zaehler kam nie ueber 1. Deshalb :func:`client_ip`.
2. Der Zaehler lag im LocMemCache, also pro Gunicorn-Worker getrennt und beim
   naechsten Deploy weg. Deshalb DatabaseCache (siehe settings ``CACHES``).
3. Der Honeypot ``website`` blieb leer - der Bot fuellt gezielt die sichtbaren
   Felder, nicht alle. Ein einzelnes Signal reicht also nicht.

Statt eines weiteren Einzelsignals bewertet :func:`score` mehrere Signale und
summiert sie. Ab :data:`BLOCK_SCHWELLE` wird verworfen. Das haelt echte Nutzer
mit ungewoehnlichem Setup (kein JavaScript, sehr schnelles Tippen) drin,
solange sie nur EIN Signal ausloesen, und faengt den Bot, der reihenweise
mehrere ausloest.

Das staerkste Signal ist :func:`js_proof`. Der Angreifer laedt nur die HTML-
Seiten, keine einzige CSS- oder JS-Datei - er fuehrt also kein JavaScript aus.
Ein Feld, das nur ein echter Browser korrekt fuellen kann, trifft ihn direkt.
Es blockt aber bewusst nicht allein (+3 < Schwelle 5), damit ein Mensch mit
abgeschaltetem JavaScript seine Anfrage trotzdem loswird.

WARUM kein-js NUR +3 WIEGT (geaendert am 01.09.2026, vorher +4)

Mit +4 ergab ``kein-js`` zusammen mit ``nur-email`` (+1) **genau 5** und damit
die Schwelle. Beide Signale loest ein voellig ehrlicher Interessent aus: JS aus,
und auf /anfrage/ sind Telefon und Adresse optional. Er sah die Erfolgsmeldung -
und gespeichert wurde nichts. Zwei Zusagen dieses Moduls hoben sich gegenseitig
auf.

Die Gegenrechnung nach Regel 18, vollstaendig - es gibt ausser ``nur-email`` und
``token-alt`` kein Signal mit Gewicht 1, alle uebrigen wiegen 2, 3, 4 oder 10.
Von blockt auf kommt-durch wechseln deshalb genau die Kombinationen, die vorher
auf **exakt 5** summierten und ``kein-js`` enthielten:

* ``kein-js`` + ``nur-email`` (5 -> 4): der Fall, um den es geht.
* ``kein-js`` + ``token-alt`` (5 -> 4): ein Mensch ohne JS mit einem laenger als
  sechs Stunden offenen Tab. Ein Bot POSTet 0-1 s nach dem GET und hat nie ein
  altes Token - dieses Paar ist kein Botmuster.

Alles andere blockt weiter, jeweils eine Stufe knapper:
``kein-js``+``zu-schnell`` 7->6, ``kein-js``+``token-fehlt`` 7->6,
``kein-js``+``name-zusammengeschrieben`` 6->5, ``kein-js``+``fremdschrift`` 7->6,
``kein-js``+``link-im-text`` 8->7, ``kein-js``+``spam-vokabular`` 8->7.
**Der Bot des Angriffs vom 25.08.2026 loeste kein-js UND zu-schnell aus** - er
kommt mit 6 weiterhin nicht durch. Kein einziges bisher geblocktes Botmuster
wird durchgelassen.

Zwei Signale seit dem 02.10.2026 (Bausteine aus DOKU-STANDARD 3a): ``domain-im-text``
(Adresse ohne ``http://``, +3) und ``markendomain-fremd`` (fremde Domain mit dem
Markennamen, +4). Gegenrechnung nach Regel 18: Kein Einzelsignal blockt allein
(3 und 4 liegen unter 5). Ein Mensch **mit** JavaScript, der im Text eine
Adresse nennt, hat 3 - er kommt durch; ein Mensch **ohne** JavaScript, der nur
seine E-Mail nennt und im Text eine Adresse mit Spam-Endung oder Pfad schreibt,
hat 3 + 3 + 1 = 7 und wuerde geblockt. Das ist der einzige neue Fall, in dem
ein echter Kunde verloren gehen kann; er ist sehr selten und steht in
``test_antispam.py`` festgehalten. Der Bot des Angriffs vom 04.09.2026 (Adresse
ohne Schema im Text) summiert mit ``kein-js`` und ``zu-schnell`` auf 9 und
kommt weiterhin nicht durch; neu ist nur, dass auch der Bot mit nachgebautem JS
und einer Adresse ohne Schema ein zweites Signal traegt.

Letzte Instanz ist :func:`mail_budget_ok`: eine harte Obergrenze an Admin-Mails
pro Stunde und Tag ueber ALLE Formulare hinweg. Selbst wenn jemand kuenftig
jedes einzelne Signal umgeht, laeuft das Postfach nicht mehr voll - die
Anfragen landen dann nur noch in der Datenbank.

WAS DIESE DATEI NICHT LEISTET (nachgerechnet am 25.08.2026 gegen :func:`score`,
nicht geschaetzt - die Projektregel dazu steht in CLAUDE.md: wer eine Pruefung
schreibt, schreibt dazu, welchen Fehler sie nicht finden kann):

* Baut ein Bot die FNV-Rechnung nach UND wechselt auf einen unauffaelligen
  Namen, bleiben nur ``zu-schnell`` (3) und ``nur-email`` (1) - Score 4, er
  kommt durch. Der im Live-Log gemessene Wert von 29 kam grossenteils aus
  BLOCK_NAMEN/BLOCK_MAILS und der Namensform, also aus Merkmalen, die der
  Angreifer einseitig aufgeben kann. Die inhaltlichen Signale sind Beiwerk;
  in diesem Fall tragen :func:`rate_limited`, die Duplikatsperre in views.py
  und :func:`mail_budget_ok`.
* Ein ferngesteuerter echter Browser besteht JS-Nachweis und Zeitfalle
  vollstaendig. Derselbe Fallback greift.
* Umgekehrt: Ein Mensch OHNE JavaScript, der in unter MIN_SEKUNDEN absendet,
  wird geblockt (3 + 3 = 6). Unwahrscheinlich - JS-los ist selten, und die
  Leistungsart ist ein Radio-Button, den Autofill nicht setzt -, aber keine
  theoretische Luecke.

Wer MIN_SEKUNDEN oder ein Gewicht aendert, rechnet BEIDE Richtungen nach:
schaerfer heisst hier immer auch, echte Anfragen zu verlieren.
"""

import ipaddress
import logging
import re
import time

from django.conf import settings
from django.core import signing
from django.core.cache import cache

logger = logging.getLogger('apps.core')

# Ab dieser Summe wird verworfen. 5 ist so gewaehlt, dass kein Einzelsignal
# allein blockt, aber jede Zweierkombination aus den starken Signalen.
BLOCK_SCHWELLE = 5

# Mindest-Ausfuellzeit. Der Bot POSTet 0-1 s nach dem GET. Ein Mensch braucht
# fuer Leistungsart, Name, E-Mail und Adresse selbst mit Autofill mehr als das.
MIN_SEKUNDEN = 4

# Hoechstalter des Formular-Tokens. Laenger offene Tabs bekommen ein neues
# Formular, statt dass die Anfrage kommentarlos verschwindet - deshalb wertet
# ein abgelaufenes Token nur als Signal, nicht als Ablehnung.
MAX_SEKUNDEN = 6 * 3600


# ── Echte Client-IP ──────────────────────────────────────────────────────────
#
# Railway proxied ueber Envoy. ``X-Envoy-External-Address`` traegt genau eine
# Adresse: die des tatsaechlichen Clients, vom Proxy gesetzt und damit nicht
# faelschbar. ``X-Forwarded-For`` ist der Fallback; dort steht die Client-IP
# nach Konvention vorn, kann vom Client aber selbst mitgeschickt und so
# gefaelscht werden. Ein gefaelschter Eintrag verschiebt das Rate-Limit nur auf
# einen anderen Schluessel - unschoen, aber die Score-Regeln greifen weiterhin.

_PRIVAT = (
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('127.0.0.0/8'),
    # Railways internes Proxy-Netz - genau die 100.64.0.x aus den Logs.
    ipaddress.ip_network('100.64.0.0/10'),
)


def _ist_privat(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True
    return any(ip in netz for netz in _PRIVAT)


def client_ip(request):
    """Die oeffentliche IP des Clients, oder ``''`` wenn keine zu finden ist."""
    envoy = request.META.get('HTTP_X_ENVOY_EXTERNAL_ADDRESS', '').strip()
    if envoy and not _ist_privat(envoy):
        return envoy

    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    for teil in xff.split(','):
        kandidat = teil.strip()
        if kandidat and not _ist_privat(kandidat):
            return kandidat

    remote = request.META.get('REMOTE_ADDR', '').strip()
    return '' if _ist_privat(remote) else remote


def _subnetz(ip_str):
    """/24 bzw. /64 - fasst IP-Rotation innerhalb eines Providers zusammen."""
    if not ip_str:
        return ''
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return ''
    if ip.version == 4:
        return str(ipaddress.ip_network(f'{ip}/24', strict=False))
    return str(ipaddress.ip_network(f'{ip}/64', strict=False))


def _zaehle(key, limit, window):
    """True, wenn ``key`` das Limit im Zeitfenster erreicht hat.

    **Das Fenster beginnt mit dem ersten Treffer und wird nie verlaengert**
    (EIG146, 24.09.2026). Bis dahin stand hier ``cache.set(key, n + 1,
    timeout=window)`` - jeder gezaehlte Treffer schob das Ende um eine volle
    Stunde hinaus. Wer um 14:00, 14:50 und 15:40 absandte, blieb bis 16:40
    gesperrt statt bis 15:00.

    Warum nicht ``cache.add`` + ``cache.incr``, wie im Plan vorgeschlagen:
    ``DatabaseCache`` (Produktion) hat kein eigenes ``incr``; das geerbte
    ``BaseCache.incr`` schreibt mit dem **Standard-Timeout** zurueck und
    verlaengert damit genau das, was es nicht soll. Deshalb traegt der Eintrag
    sein Ablaufdatum selbst: ``(anzahl, ende)``, und jedes Zurueckschreiben
    nimmt die Restzeit bis ``ende``.

    Nicht atomar: Zwei gleichzeitige Requests koennen denselben Stand lesen
    und einer zu viel durchrutschen. Fuer eine Missbrauchsbremse ist das
    belanglos, und es haelt den Code ohne Redis lauffaehig.
    """
    jetzt = time.time()
    eintrag = cache.get(key)
    if not isinstance(eintrag, (tuple, list)) or len(eintrag) != 2 \
            or eintrag[1] <= jetzt:
        # Neu, abgelaufen - oder ein alter Zaehler aus der Zeit vor dem
        # 24.09.2026 (eine nackte Zahl): Er beginnt ein frisches Fenster.
        cache.set(key, (1, jetzt + window), timeout=window)
        return limit < 1
    anzahl, ende = eintrag
    if anzahl >= limit:
        return True
    cache.set(key, (anzahl + 1, ende), timeout=max(1, int(ende - jetzt)))
    return False


def rate_limited(request, action, limit=5, window=3600, subnetz_faktor=4):
    """Zaehlt pro IP und zusaetzlich pro Subnetz.

    Der Subnetz-Zaehler kostet den Angreifer den billigsten Ausweg: Innerhalb
    eines /24 reicht es nicht, nach jedem Treffer die letzte Stelle zu
    wechseln. ``subnetz_faktor`` gibt dem Subnetz mehr Luft als der Einzel-IP,
    damit ein Buero hinter einer gemeinsamen Adresse nicht durch einen
    einzelnen Nutzer stillgelegt wird.
    """
    ip = client_ip(request)
    if not ip:
        # Ohne verwertbare IP nicht raten - die Score-Regeln greifen weiter.
        return False

    if _zaehle(f'rl:{action}:{ip}', limit, window):
        logger.warning('Rate-Limit erreicht | %s | ip=%s', action, ip)
        return True

    netz = _subnetz(ip)
    if netz and _zaehle(f'rl:{action}:net:{netz}', limit * subnetz_faktor, window):
        logger.warning('Rate-Limit erreicht | %s | subnetz=%s', action, netz)
        return True

    return False


def abgelaufene_zaehler_loeschen():
    """Loescht abgelaufene Eintraege aus dem Datenbank-Cache; gibt die Zahl zurueck.

    EIG249 (25.09.2026, auch Befund im SEO-Audit): Die Schluessel von
    :func:`rate_limited` und der
    Anmeldebremse in ``apps/stats`` tragen die **volle IP-Adresse**
    (``rl:anfrage:203.0.113.47``). Sie laufen nach einer Stunde ab - aber
    ``DatabaseCache`` loescht eine abgelaufene Zeile nur, wenn derselbe
    Schluessel noch einmal gelesen wird oder die Tabelle ``MAX_ENTRIES``
    (50.000, siehe settings) ueberschreitet. Bei der echten Last dieser Seite
    heisst das: nie. Die Adresse blieb also unbegrenzt in der Datenbank, und
    die Datenschutzerklaerung nannte die Speicherung gar nicht.

    Dieselbe Abfrage, die Django selbst vor dem Kappen ausfuehrt
    (``DatabaseCache._cull``), nur ohne das Kappen. Ohne ``DatabaseCache``
    (lokal ``LocMemCache``) gibt es nichts Dauerhaftes zu loeschen.
    """
    from django.core.cache import caches
    from django.core.cache.backends.db import DatabaseCache
    from django.db import connections, router
    from django.utils import timezone

    # ``cache`` ist ein Stellvertreter - das Backend dahinter liefert ``caches``.
    backend = caches['default']
    if not isinstance(backend, DatabaseCache):
        return 0
    db = router.db_for_write(backend.cache_model_class)
    verbindung = connections[db]
    tabelle = verbindung.ops.quote_name(backend._table)
    jetzt = timezone.now().replace(microsecond=0)
    if not settings.USE_TZ:
        jetzt = timezone.make_naive(jetzt)
    with verbindung.cursor() as cursor:
        # EIG336/EIG366: kein SQL-Einschleusen - ``tabelle`` und der Spaltenname
        # kommen aus ``quote_name()`` (Backend-Bezeichner, keine Nutzereingabe),
        # ``jetzt`` laeuft als gebundener Parameter (``%%s`` -> ``%s`` fuer die
        # DB-API) durch die Parameterliste, nicht durch die Formatierung.
        # audit-ok P07: Tabellen- und Spaltenname nur ueber quote_name() (kein Nutzerwert), der Zeitpunkt als gebundener Parameter
        cursor.execute(
            'DELETE FROM %s WHERE %s < %%s'
            % (tabelle, verbindung.ops.quote_name('expires')),
            [verbindung.ops.adapt_datetimefield_value(jetzt)],
        )
        return cursor.rowcount


# ── Formular-Token: Zeitmessung und JavaScript-Nachweis ──────────────────────

_signer = signing.Signer(salt='rw.antispam.formular')


def form_token():
    """Signierter Ausgabezeitpunkt. Gehoert als Hidden-Feld ``rw_t`` ins HTML."""
    return _signer.sign(str(int(time.time())))


def _token_alter(token):
    """Sekunden seit Ausgabe, oder ``None`` bei fehlender/kaputter Signatur."""
    if not token:
        return None
    try:
        ausgestellt = int(_signer.unsign(token))
    except (signing.BadSignature, ValueError):
        return None
    return int(time.time()) - ausgestellt


def _base36(n):
    """uint32 als Base36 - dasselbe Ergebnis wie ``(n>>>0).toString(36)``."""
    if n == 0:
        return '0'
    ziffern = '0123456789abcdefghijklmnopqrstuvwxyz'
    out = ''
    while n:
        out = ziffern[n % 36] + out
        n //= 36
    return out


def js_proof(token):
    """Wert, den der Browser aus ``rw_t`` errechnen muss (FNV-1a, Base36).

    Kein Sicherheitsmechanismus - der Algorithmus steht offen im Seitenquelltext
    und laesst sich nachbauen. Er unterscheidet nur, ob ueberhaupt JavaScript
    lief. Genau daran scheitert der aktuelle Angreifer, der keine einzige
    Ressource nachlaedt.
    """
    h = 2166136261
    for ch in token or '':
        h ^= ord(ch) & 0xFFFF
        h = (h * 16777619) & 0xFFFFFFFF
    return _base36(h)


# ── Inhaltliche Muster ───────────────────────────────────────────────────────

# Ein Name ohne Leerzeichen, aber mit Grossbuchstabe im Wortinneren:
# "RobertPrant", "JohnSmith". Menschen schreiben "Robert Prant".
_NAME_ZUSAMMEN = re.compile(r'^[A-ZÄÖÜ][a-zäöüß]+[A-ZÄÖÜ][a-zäöüß]+$')

_URL_MUSTER = re.compile(
    r'(https?://|www\.|\[url|\[link|<a\s+href)', re.IGNORECASE
)

# Adresse **ohne** Schema (Baustein "Adresse ohne http:// erkannt", DOKU-STANDARD
# 3a; die Masche vom 04.09.2026): ``spam-seite.ru`` oder ``seite.com/angebot``
# ohne ``http://`` und ohne ``www.``. Bewusst eng gefasst, weil ein deutscher
# Satz ohne Leerzeichen nach dem Punkt ("Danke.Bitte melden") sonst wie eine
# Adresse aussieht: der Name besteht nur aus Kleinbuchstaben, Ziffern und
# Bindestrich, steht nicht hinter ``@`` (E-Mail-Adressen sind keine Links) und
# traegt entweder eine Endung aus der Spam-Liste oder einen Pfad hinter dem
# ersten Schraegstrich. Gross geschriebene Woerter (Satzanfaenge) treffen nie.
_ENDUNGEN_SPAM = (
    'ru|su|xyz|top|click|site|online|shop|store|icu|vip|club|live|link|buzz|'
    'work|biz|info|pw|cc|ws|cn|tk|ml|ga|cf|gq|monster|rest|cyou|today'
)
_DOMAIN_OHNE_SCHEMA = re.compile(
    r'(?<![\w@.\-/])[a-z0-9][a-z0-9\-]{1,62}'
    r'(?:\.[a-z0-9][a-z0-9\-]{0,62})*'
    r'(?:\.(?:' + _ENDUNGEN_SPAM + r')\b(?![\w\-]*@)'
    r'|\.[a-z]{2,6}/[^\s]+)'
)

# Fremde Domain mit dem eigenen Markennamen (Baustein "fremde Domain mit
# eigenem Markennamen", Vertrauen erschleichen): ``ruempelwerk-service.xyz``
# als Absenderadresse oder im Text. Die eigenen Domains sind ausgenommen.
_MARKE_IN_DOMAIN = re.compile(
    r'(?<![\w.\-])((?:[a-z0-9\-]+\.)*[a-z0-9\-]*(?:ruempelwerk|rumpelwerk|'
    r'r\u00fcmpelwerk)[a-z0-9\-]*(?:\.[a-z0-9\-]+)+)(?![\w\-])', re.IGNORECASE
)
EIGENE_DOMAINS = frozenset({
    'ruempelwerk-mitteldeutschland.de', 'deutsches-ruempelwerk.com',
})


def _fremde_markendomain(text):
    """Steht im Text oder in der Adresse eine Domain mit dem Markennamen, die
    nicht dem Betrieb gehoert? Eigene Domains und deren Subdomains zaehlen nicht."""
    if not text:
        return False
    for treffer in _MARKE_IN_DOMAIN.finditer(text):
        domain = treffer.group(1).lower()
        if not any(domain == d or domain.endswith('.' + d) for d in EIGENE_DOMAINS):
            return True
    return False

# Kyrillisch, Griechisch, CJK, Hebraeisch, Arabisch. Eine Entruempelung in
# Mitteldeutschland wird nicht in diesen Schriften angefragt.
_FREMDSCHRIFT = re.compile(
    r'[Ѐ-ӿͰ-Ͽ一-鿿぀-ヿ'
    r'֐-׿؀-ۿ]'
)

# Woerter aus dem ueblichen Formspam-Repertoire (SEO-Angebote, Krypto, Pillen).
_SPAM_WOERTER = re.compile(
    r'\b(seo\s*(service|offer|agency)|backlink|crypto|bitcoin|forex|casino|'
    r'viagra|cialis|payday|loan\s*offer|escort|porn|xxx|dating|'
    r'increase\s*(your\s*)?(traffic|sales|ranking)|guest\s*post|'
    r'link\s*building|web\s*design\s*service|100%\s*free)\b',
    re.IGNORECASE,
)

# Konkrete Absender des laufenden Angriffs. Die Score-Regeln fangen ihn
# ohnehin; der Eintrag macht den Fall aktenkundig und wirkt sofort, falls er
# sein Verhalten umstellt, aber Name oder Adresse beibehaelt.
BLOCK_NAMEN = frozenset({
    'robertprant',
})

BLOCK_MAILS = frozenset({
    'elitetaxllc1@gmail.com',
    'ronald.langdon@gmail.com',
    'toddy-oss@fireworks.ai',
    'tim.denbesten@kv.com',
    'acromer@drillchem.com',
    'razzini@libero.it',
    'gnudicristian@libero.it',
})


def _text_signale(text, gruende):
    if not text:
        return 0
    punkte = 0
    if _URL_MUSTER.search(text):
        punkte += 4
        gruende.append('link-im-text')
    if _FREMDSCHRIFT.search(text):
        punkte += 3
        gruende.append('fremdschrift')
    if _SPAM_WOERTER.search(text):
        punkte += 4
        gruende.append('spam-vokabular')
    # +3 wie kein-js: allein blockt es nie (Schwelle 5), zusammen mit einem
    # zweiten Signal schon. Der Mensch mit JavaScript, der im Text eine Adresse
    # nennt, bleibt darunter; die Gegenrechnung steht in test_antispam.py.
    if _DOMAIN_OHNE_SCHEMA.search(text):
        punkte += 3
        gruende.append('domain-im-text')
    return punkte


def score(request, name='', email='', telefon='', adresse='', text='',
          honeypot_feld='website'):
    """Summe der Spam-Signale plus die Liste der Gruende.

    Alle Felder sind optional - die Formulare heissen unterschiedlich und
    liefern, was sie haben. Der Rueckgabewert wird bewusst auch unterhalb der
    Schwelle protokolliert, damit sich spaeter belegen laesst, wie knapp eine
    Entscheidung war.
    """
    punkte = 0
    gruende = []

    # 1. Honeypot - das eine Signal, das allein blockt. Ein Mensch kann ein
    #    display:none-Feld nicht befuellen, hier gibt es keinen Fehlalarm.
    if request.POST.get(honeypot_feld) or (
        request.content_type == 'application/json'
        and getattr(request, '_rw_json', {}).get(honeypot_feld)
    ):
        punkte += 10
        gruende.append('honeypot')

    # 2. JavaScript-Nachweis.
    token = request.POST.get('rw_t') or getattr(request, '_rw_json', {}).get('rw_t', '')
    beweis = request.POST.get('rw_j') or getattr(request, '_rw_json', {}).get('rw_j', '')
    if not beweis or beweis != js_proof(token):
        # +3 seit dem 01.09.2026, vorher +4. Grund und vollstaendige
        # Gegenrechnung im Modul-Docstring, Abschnitt WARUM kein-js NUR +3.
        punkte += 3
        gruende.append('kein-js')

    # 3. Zeitfalle.
    alter = _token_alter(token)
    if alter is None:
        punkte += 3
        gruende.append('token-fehlt')
    elif alter < MIN_SEKUNDEN:
        punkte += 3
        gruende.append(f'zu-schnell-{alter}s')
    elif alter > MAX_SEKUNDEN:
        punkte += 1
        gruende.append('token-alt')

    # 4. Bekannte Absender.
    if name.strip().lower().replace(' ', '') in BLOCK_NAMEN:
        punkte += 10
        gruende.append('name-gesperrt')
    if email.strip().lower() in BLOCK_MAILS:
        punkte += 10
        gruende.append('mail-gesperrt')

    # 5. Namensform.
    if _NAME_ZUSAMMEN.match(name.strip()):
        punkte += 2
        gruende.append('name-zusammengeschrieben')

    # 5b. Fremde Domain mit dem eigenen Markennamen: als Absenderadresse oder im
    #     Text. +4 - allein unter der Schwelle (kein Einzelsignal ausser dem
    #     Honeypot blockt allein), aber mit nur-email (+1) schon ein Grenzfall.
    #     Ein echter Kunde hat keine Adresse, die den Markennamen eines
    #     fremden Betriebs traegt; die eigenen Domains sind ausgenommen.
    if _fremde_markendomain(email) or _fremde_markendomain(text):
        punkte += 4
        gruende.append('markendomain-fremd')

    # 6. Inhalt.
    punkte += _text_signale(text, gruende)
    punkte += _text_signale(name, gruende)

    # 7. Kein einziger Rueckkanal ausser der E-Mail. Schwaches Signal - manche
    #    Interessenten geben wirklich nur ihre Adresse an -, deshalb nur +1.
    if not telefon.strip() and not adresse.strip():
        punkte += 1
        gruende.append('nur-email')

    return punkte, gruende


def ist_spam(request, aktion, **felder):
    """True, wenn die Einsendung verworfen werden soll. Protokolliert immer.

    Fuer Kooperation, Bewerbung und Rechner: dort gibt es keinen
    Verdachtszustand, ab der Schwelle wird verworfen. ``/anfrage/`` benutzt
    :func:`pruefen`.
    """
    return pruefen(request, aktion, verdacht_erlaubt=False, **felder) != 'ok'


# ── Grenzfaelle: Verdacht statt Verwerfen (Variante A, 24.09.2026) ──────────
#
# Ein Mensch ohne JavaScript bekommt ``kein-js`` (+3). Mit einem ueber sechs
# Stunden offenen Tab (``token-alt`` +1) und nur Name und E-Mail
# (``nur-email`` +1) steht er genau auf der Schwelle 5, mit einem Link im Text
# (``link-im-text`` +4) bei 7 - und wurde still verworfen, obwohl er
# "Danke! Ihre Anfrage wurde gespeichert." las. Seit Variante A wird ein
# solcher Grenzfall GESPEICHERT, als ``Anfrage.verdacht=True`` mit
# ``mail_gewollt=False``: keine Mail, kein Push, sichtbar und markiert im
# Dashboard, geloescht nach 30 Tagen.
#
# Wer NICHT Verdacht werden kann, sondern verworfen bleibt - die Merkmale,
# die ein Mensch im Browser nicht erzeugt:
#
# * ``honeypot`` - ein unsichtbares Feld, das kein Mensch fuellt;
# * ``name-gesperrt`` / ``mail-gesperrt`` - bekannte Absender (so der Bot vom
#   21.-24.09.2026 mit Score 18-21);
# * ``token-fehlt`` - der Browser schickt das versteckte Feld immer mit;
# * ``zu-schnell-*`` - unter MIN_SEKUNDEN nach dem Laden;
# * alles ab VERDACHT_OBERGRENZE Punkten.
#
# Gegenrechnung nach Regel 18 (beide Richtungen):
# * Der Bot vom 25.08.2026 (``kein-js`` + ``zu-schnell``, 6) und der vom
#   21.-24.09.2026 (``name-gesperrt``) bleiben verworfen - sie tragen je ein
#   hartes Merkmal. **Kein bisher verworfener Bot wird zugestellt**, denn ein
#   Verdacht loest nie eine Mail aus.
# * Was sich aendert, ist nur die TABELLE: Sie nimmt Grenzfaelle auf. Gegen
#   eine Flut steht :data:`VERDACHT_JE_STUNDE` - darueber wird wieder
#   verworfen wie bisher ("Spam bleibt ungespeichert" schuetzte die Tabelle
#   im Angriffsfall; die Obergrenze uebernimmt das).

#: Ab dieser Summe ist es kein Grenzfall mehr, sondern Spam.
VERDACHT_OBERGRENZE = 10

#: So viele Verdachtsfaelle speichert die Seite hoechstens je Stunde (alle
#: Absender zusammen). Echte Grenzfaelle sind selten; darueber ist es Flut.
VERDACHT_JE_STUNDE = 10

_HARTE_MERKMALE = ('honeypot', 'name-gesperrt', 'mail-gesperrt', 'token-fehlt',
                   'zu-schnell')


def ist_grenzfall(punkte, gruende):
    """True, wenn eine Einsendung ueber der Schwelle als Verdacht zaehlt."""
    if not (BLOCK_SCHWELLE <= punkte < VERDACHT_OBERGRENZE):
        return False
    return not any(g.startswith(h) for g in gruende for h in _HARTE_MERKMALE)


def _verdacht_platz_frei():
    schluessel = f'verdacht:h:{int(time.time()) // 3600}'
    anzahl = cache.get(schluessel, 0)
    if anzahl >= VERDACHT_JE_STUNDE:
        return False
    cache.set(schluessel, anzahl + 1, timeout=3600)
    return True


def pruefen(request, aktion, verdacht_erlaubt=True, **felder):
    """``'ok'``, ``'verdacht'`` oder ``'spam'``. Protokolliert immer.

    ``'verdacht'`` nur mit ``verdacht_erlaubt`` (``/anfrage/``) und nur fuer
    einen Grenzfall (:func:`ist_grenzfall`) unterhalb der Stundengrenze.
    """
    punkte, gruende = score(request, **felder)
    ip = client_ip(request) or 'unbekannt'

    if punkte >= BLOCK_SCHWELLE and verdacht_erlaubt \
            and ist_grenzfall(punkte, gruende) and _verdacht_platz_frei():
        logger.warning(
            'Einsendung als Verdacht gespeichert | %s | score=%d | %s | ip=%s',
            aktion, punkte, ','.join(gruende), ip,
        )
        return 'verdacht'

    if punkte >= BLOCK_SCHWELLE:
        # Ohne Name und Mailadresse (FO13, 17.09.2026): Eine verworfene
        # Einsendung kann ein echter Mensch sein, und das Railway-Log liegt
        # ausserhalb jeder Löschfrist. Die Gründe und der Score reichen, um
        # die Abwehr zu beurteilen (formularspam-nachlauf, Punkt 2).
        logger.warning(
            'SPAM verworfen | %s | score=%d | %s | ip=%s',
            aktion, punkte, ','.join(gruende), ip,
        )
        return 'spam'

    if punkte:
        logger.info(
            'Einsendung durchgelassen | %s | score=%d | %s | ip=%s',
            aktion, punkte, ','.join(gruende) or '-', ip,
        )
    return 'ok'


# ── Notbremse fuer das Postfach ──────────────────────────────────────────────

def _notbremse_melden(art, jetzt, grund):
    """Die erste Notbremse je Stunde als ERROR (Fehlerwache) und Telegram-Alarm.

    Bis zum 24.09.2026 stand hier nur ``logger.warning`` - die Fehlerwache
    sieht erst ab ERROR, die Notbremse blieb also unbemerkt, waehrend echte
    Anfragen ohne Mail liefen. Jede weitere Ausloesung in derselben Stunde
    bleibt WARNING: eine Zeile je Stunde, nicht eine je Anfrage.
    """
    if cache.add(f'mailbudget:{art}:gemeldet:{jetzt // 3600}', 1, timeout=3600):
        logger.error('Mail-Notbremse | %s | %s', art, grund)
        from . import telegram
        telegram.alarm(f'Mail-Notbremse: {grund}. Neue Anfragen stehen nur '
                       'noch im Dashboard.', 'notbremse')
    else:
        logger.warning('Mail-Notbremse | %s | %s', art, grund)


def mail_budget_ok(art='admin'):
    """False, sobald die Obergrenze an Admin-Mails erreicht ist.

    Der Zaehler laeuft ueber alle Formulare gemeinsam. Was hier abgelehnt wird,
    ist trotzdem in der Datenbank und im Dashboard sichtbar - es geht nur die
    Benachrichtigung verloren, nicht der Lead.

    Ausdruecklich KEIN Warnhinweis per Mail bei Erreichen der Grenze: Eine
    Warnung pro Ereignis waere derselbe Spam mit anderem Betreff. Das Erreichen
    steht im Log und im taeglichen Report.
    """
    grenze_stunde = getattr(settings, 'ADMIN_MAIL_LIMIT_STUNDE', 15)
    grenze_tag = getattr(settings, 'ADMIN_MAIL_LIMIT_TAG', 60)

    jetzt = int(time.time())
    stunden_key = f'mailbudget:{art}:h:{jetzt // 3600}'
    tages_key = f'mailbudget:{art}:d:{jetzt // 86400}'

    pro_stunde = cache.get(stunden_key, 0)
    pro_tag = cache.get(tages_key, 0)

    if pro_stunde >= grenze_stunde:
        _notbremse_melden(
            art, jetzt, f'{pro_stunde} Mails in dieser Stunde erreicht - '
                        'weitere Anfragen werden nur noch gespeichert')
        return False
    if pro_tag >= grenze_tag:
        _notbremse_melden(art, jetzt, f'Tagesgrenze {grenze_tag} erreicht')
        return False

    cache.set(stunden_key, pro_stunde + 1, timeout=3600)
    cache.set(tages_key, pro_tag + 1, timeout=86400)
    return True


def mail_budget_erschoepft(art='admin'):
    """True, wenn ``mail_budget_ok(art)`` jetzt ablehnen wuerde - **ohne zu zaehlen**.

    Fuer Zweige, die nie eine Mail ausloesen (Spam, Verdacht, Duplikat), aber
    dieselbe Dankmeldung zeigen muessen wie die echte Anfrage (Regel 18):
    Bei erschoepftem Budget sieht die echte Anfrage die neutrale Fassung, und
    ein Bot duerfte daran nicht erkennen, ob er durchkam. Kein Zaehler, keine
    Notbremsen-Meldung - das bleibt Sache von ``mail_budget_ok``.
    """
    jetzt = int(time.time())
    return (cache.get(f'mailbudget:{art}:h:{jetzt // 3600}', 0)
            >= getattr(settings, 'ADMIN_MAIL_LIMIT_STUNDE', 15)
            or cache.get(f'mailbudget:{art}:d:{jetzt // 86400}', 0)
            >= getattr(settings, 'ADMIN_MAIL_LIMIT_TAG', 60))
