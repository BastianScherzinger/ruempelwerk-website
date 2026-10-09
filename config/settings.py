"""Django-Einstellungen für Railway und die lokale Entwicklung.

Alles Veränderliche kommt über ``decouple`` aus der Umgebung; ohne
``DATABASE_URL`` läuft das Projekt auf SQLite.
"""

from pathlib import Path
from decouple import config, Csv
from django.core.exceptions import ImproperlyConfigured
import dj_database_url
import re

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Security ────────────────────────────────────────────────────────────────

DEBUG = config('DEBUG', default=False, cast=bool)

SECRET_KEY = config('SECRET_KEY', default='django-insecure-CHANGE_THIS_IN_PRODUCTION')
if not DEBUG and SECRET_KEY.startswith('django-insecure-'):
    raise RuntimeError('Unsicherer SECRET_KEY in Production! Setze die Env-Variable SECRET_KEY.')

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=Csv()
)

if not DEBUG:
    ALLOWED_HOSTS += [
        '.up.railway.app',
        'deutsches-ruempelwerk.com',
        'www.deutsches-ruempelwerk.com',
        'ruempelwerk-mitteldeutschland.de',
        'www.ruempelwerk-mitteldeutschland.de',
        # Railway ruft einen eingetragenen Healthcheck (/health/, BT11) mit
        # diesem Host auf - ohne den Eintrag antwortete Django mit 400 und
        # das Deploy scheiterte am eigenen Healthcheck.
        'healthcheck.railway.app',
    ]

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:8000,http://127.0.0.1:8000',
    cast=Csv()
)
if not DEBUG:
    CSRF_TRUSTED_ORIGINS += [
        'https://*.up.railway.app',
        'https://deutsches-ruempelwerk.com',
        'https://www.deutsches-ruempelwerk.com',
        'https://ruempelwerk-mitteldeutschland.de',
        'https://www.ruempelwerk-mitteldeutschland.de',
    ]

# ── Apps ─────────────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'axes',
    'apps.core',
    'apps.accounts',
    'apps.dashboard',
    'apps.stats',
]

_cloudinary_url = config('CLOUDINARY_URL', default='')
if _cloudinary_url:
    INSTALLED_APPS += ['cloudinary_storage', 'cloudinary']

# ── Middleware ────────────────────────────────────────────────────────────────

MIDDLEWARE = [
    # MUSS vorne stehen: kanonisiert den Host in EINEM Hop, bevor
    # SecurityMiddleware einen zweiten fuer http->https anhaengen wuerde.
    'apps.core.middleware.CanonicalDomainMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # GZip fuer HTML, Sitemaps und llms.txt (VL14, 17.09.2026). Live kam das
    # HTML bis dahin unkomprimiert (rund 145 KiB je Seite, Railway packt
    # nicht selbst). Der Platz ist gewaehlt, nicht beliebig:
    # * HINTER WhiteNoise - statische Dateien beantwortet WhiteNoise vorher
    #   selbst (und bringt eigene .gz/.br mit), sie erreichen GZip nie.
    # * VOR CommonMiddleware und ConditionalGetMiddleware - die Antwortphase
    #   laeuft von unten nach oben, gepackt wird also erst NACH dem Kuerzen,
    #   dem Content-Length und dem ETag. GZip macht den ETag schwach (W/),
    #   und Django vergleicht If-None-Match schwach: der 304 bleibt.
    # * BREACH/HTB: Seit Django 4.2 haengt die Middleware zufaellige Bytes an
    #   (max_random_bytes); das CSRF-Token wird ohnehin je Anfrage maskiert.
    # test_middleware.GzipTests prueft Kompression, 304 und den Fall ohne
    # Accept-Encoding.
    'django.middleware.gzip.GZipMiddleware',
    'apps.core.middleware.SecurityHeadersMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ETag + 304 (P8/E2, 06.09.2026). Steht DIREKT hinter CommonMiddleware,
    # und das ist kein Geschmack:
    #
    # * Die Antwortphase laeuft von unten nach oben. Alles, was UNTER diesem
    #   Eintrag steht, hat die Antwort also schon angefasst, wenn hier der
    #   ETag gebildet wird – insbesondere HtmlEinrueckungMiddleware ganz
    #   unten, die das HTML kuerzt. Der ETag entsteht damit ueber dem
    #   **ausgelieferten** Text. Stuende diese Zeile weiter unten, wechselte
    #   der ETag bei unveraendertem Inhalt, und kein Crawler bekaeme je einen
    #   304. Genau das prueft test_middleware.py nach, statt es zu glauben.
    # * CommonMiddleware laeuft danach und rechnet das Content-Length; bei
    #   einem 304 gibt es keinen Body, an dem es sich verrechnen koennte.
    #
    # Was das bringt und was nicht: Ein stabiler ETag entsteht nur, wo das
    # HTML zwischen zwei Aufrufen gleich ist. Auf den 75 Seiten mit Formular
    # ist es das nicht (Djangos CSRF-Token wird bei jedem Rendern neu
    # maskiert, und {% rw_antispam %} setzt einen Zeitstempel) – dort kostet
    # die Middleware eine MD5-Summe und liefert nie einen 304. Der Gewinn
    # liegt bei sitemap.xml, robots.txt, llms.txt und den formularlosen
    # Seiten, also genau bei dem, was Crawler regelmaessig wieder abholen.
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.RequestLoggingMiddleware',
    # MUSS hinten stehen - Spiegelbild zur Regel ganz oben: Die Antwortphase
    # laeuft von unten nach oben, der letzte Eintrag sieht die Antwort also
    # als ERSTER. Nur so rechnet CommonMiddleware das Content-Length auf dem
    # bereits gekuerzten HTML aus.
    'apps.core.middleware.HtmlEinrueckungMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ── Django-Axes Brute-Force-Schutz ────────────────────────────────────────────

AXES_FAILURE_LIMIT = 10
AXES_COOLOFF_TIME = 1
AXES_LOCKOUT_TEMPLATE = 'errors/lockout.html'
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_PARAMETERS = [['username', 'ip_address']]

# ── URLs / Templates ─────────────────────────────────────────────────────────

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.global_context',
                'apps.core.context_processors.preise',
                'apps.core.context_processors.leistungen_nav',
                'apps.core.context_processors.bewertung',
                'apps.core.context_processors.zusagen',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# ── Datenbank ─────────────────────────────────────────────────────────────────

_db_url = config('DATABASE_URL', default='')
if _db_url:
    DATABASES = {
        'default': dj_database_url.parse(
            _db_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ── Passwort-Validierung ──────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Sprache / Zeitzone ────────────────────────────────────────────────────────

LANGUAGE_CODE = 'de-de'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True

# ── Statische Dateien ─────────────────────────────────────────────────────────

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        # CSS wird vor collectstatic vom Management-Command `minify_css`
        # verkleinert (siehe start.sh) – ein Storage-Hook taugt dafuer nicht,
        # weil Django beim Hashen aus dem Quellverzeichnis liest.
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Cloudinary ────────────────────────────────────────────────────────────────

if _cloudinary_url:
    # Parse cloudinary://api_key:api_secret@cloud_name
    import re as _re
    _m = _re.match(r'cloudinary://([^:]+):([^@]+)@(.+)', _cloudinary_url)
    if _m:
        _api_key, _api_secret, _cloud_name = _m.group(1), _m.group(2), _m.group(3)
    else:
        _api_key = _api_secret = _cloud_name = ''

    STORAGES['default'] = {
        'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
    }
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': _cloud_name,
        'API_KEY':    _api_key,
        'API_SECRET': _api_secret,
        'MEDIA_TAG':  'firma-media',
    }
    # Also initialise the cloudinary SDK directly so it's available everywhere
    try:
        import cloudinary as _cld
        _cld.config(
            cloud_name=_cloud_name,
            api_key=_api_key,
            api_secret=_api_secret,
            secure=True,
        )
    except Exception:
        # Nicht ``pass``: Schlaegt die SDK-Initialisierung fehl, faellt die
        # Bildauslieferung still auf lokales Storage zurueck - die Seite
        # laeuft weiter, liefert aber unoptimierte Bilder ohne srcset, und
        # niemand sieht es. Ein Startfehler gehoert auf stderr; Railway
        # protokolliert das mit. Die dictConfig aus LOGGING greift hier noch
        # nicht (sie steht weiter unten), die Wurzel-Konfiguration reicht.
        import logging as _logging
        _logging.getLogger(__name__).warning(
            'Cloudinary-SDK konnte nicht initialisiert werden - '
            'Bilder laufen ueber das lokale Storage', exc_info=True)

# ── E-Mail ────────────────────────────────────────────────────────────────────

# ── Versandweg: SMTP oder Resend ─────────────────────────────────────────────
#
# Bis zum 06.09.2026 lief jede Mail ueber die Resend-HTTP-API. Der Grund stand
# im Docstring von ``apps/core/emails.py``: "Railway blockiert ausgehendes
# SMTP". **Das stimmte, gilt aber nicht mehr.** Railway sperrt SMTP auf den
# Tarifen Free, Trial und Hobby; dieser Arbeitsbereich laeuft auf **Pro**, und
# dort ist es erlaubt (nachgesehen in der Railway-Dokumentation und im
# Tarif-Bildschirm des Kontos, nicht vermutet). Eine Annahme, die einmal richtig
# war und still ablaeuft, ist die teuerste Sorte - deshalb steht hier, woran sie
# haengt: **am Tarif.** Faellt der Arbeitsbereich je auf Hobby zurueck, faellt
# SMTP mit, und die Seite muss zurueck auf einen HTTP-Anbieter.
#
# WARUM DER WEG SICH SELBST WAEHLT statt an einem Schalter zu haengen:
# Ein eigener Schalter waere eine dritte Angabe, die zu den beiden ohnehin
# noetigen (Passwort bzw. API-Schluessel) dazukaeme - und die man vergisst.
# So gilt: **Wer das SMTP-Passwort setzt, hat damit umgeschaltet. Wer es
# entfernt, ist zurueck bei Resend.** Der Rueckweg ist eine geloeschte Variable,
# kein Deploy.
#
# Die Reihenfolge ist Absicht: SMTP gewinnt, wenn beides gesetzt ist. Sonst
# haette ein vergessener RESEND_API_KEY die Umstellung stillschweigend
# verhindert - genau die Klasse Fehler, die dieser Umbau beendet.
EMAIL_HOST          = config('EMAIL_HOST',          default='smtp.ionos.de')
EMAIL_PORT          = config('EMAIL_PORT',          default=587, cast=int)
EMAIL_HOST_USER     = config('EMAIL_HOST_USER',     default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS       = config('EMAIL_USE_TLS',       default=True, cast=bool)
EMAIL_TIMEOUT       = config('EMAIL_TIMEOUT',       default=15, cast=int)

RESEND_API_KEY = config('RESEND_API_KEY', default='')

if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    MAIL_WEG = 'smtp'
elif RESEND_API_KEY:
    MAIL_WEG = 'resend'
else:
    MAIL_WEG = 'aus'

# Djangos eigenes Backend. ``emails.py`` benutzt es ueber ``_absenden``; es
# steht hier trotzdem vollstaendig, damit ``send_mail`` aus einem
# Management-Command oder der Shell denselben Weg nimmt und nicht ploetzlich
# in der Konsole landet.
if MAIL_WEG == 'smtp':
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='info@ruempelwerk-mitteldeutschland.de')

# Empfaenger aller Benachrichtigungen (Anfrage, Kooperation, Bewerbung,
# Preisrechner, Tagesreport). Kommagetrennt, damit weitere Adressen ohne
# Code-Aenderung dazukommen koennen - genau das war beim Nachtragen der
# zweiten Adresse noetig, als ADMIN_EMAIL noch ein einzelner String war.
ADMIN_EMAILS = [
    adresse.strip()
    for adresse in config(
        'ADMIN_EMAIL',
        default='info@ruempelwerk-mitteldeutschland.de',
    ).split(',')
    if adresse.strip()
]
# Einzelform bleibt fuer Stellen erhalten, die genau einen Empfaenger nennen.
ADMIN_EMAIL = ADMIN_EMAILS[0] if ADMIN_EMAILS else ''
CONTACT_EMAIL = config('CONTACT_EMAIL', default='info@ruempelwerk-mitteldeutschland.de')

# Automatische Mails an die Adresse, die jemand ins Formular tippt
# (Kooperation, Bewerbung, Richtangebot, Erinnerung). Standard AUS seit
# 17.09.2026: Auf einer anderen Seite haben Bots fremde Adressen eingetragen und
# die Seite hat sie mit dem eingetippten Namen angeschrieben. Durchgesetzt wird
# das an der einzigen Versandstelle, ``emails._absenden``.
KUNDENMAIL_AN_ABSENDER = config('KUNDENMAIL_AN_ABSENDER', default=False, cast=bool)


# Notbremse der Spam-Abwehr (apps/core/antispam.mail_budget_ok): So viele
# Benachrichtigungen darf die Seite hoechstens ausloesen. Alles darueber wird
# weiterhin gespeichert, nur nicht mehr zugestellt. Die Grenzen liegen deutlich
# ueber dem echten Aufkommen (einstellig pro Tag) und deutlich unter dem, was
# in der Angriffsnacht durchlief.
ADMIN_MAIL_LIMIT_STUNDE = config('ADMIN_MAIL_LIMIT_STUNDE', default=15, cast=int)
ADMIN_MAIL_LIMIT_TAG = config('ADMIN_MAIL_LIMIT_TAG', default=60, cast=int)

# Telegram-Push (apps/core/telegram.py, seit 24.09.2026): jede echte Anfrage
# zusaetzlich zur Mail sofort aufs Handy, dazu ein Alarm, wenn der Mailweg
# ausfaellt. Fehlt eins von beiden, ist der Push still aus. Einrichtung:
# docs/betrieb.md, "Telegram-Benachrichtigung", und manage.py telegram_einrichten.
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default='')
TELEGRAM_CHAT_IDS = [
    chat.strip()
    for chat in config('TELEGRAM_CHAT_IDS', default='').split(',')
    if chat.strip()
]
# Selbstanmeldung weiterer Empfaenger per Einladungslink (24.09.2026,
# apps/core/telegram_webhook.py). Alle drei leer = Webhook aus (404), es
# bleibt bei TELEGRAM_CHAT_IDS. PFAD ist der geheime Teil von
# /telegram/<PFAD>/, SECRET prueft den Kopf X-Telegram-Bot-Api-Secret-Token,
# EINLADUNG ist der Code im Link t.me/<bot>?start=<CODE> (A-Z a-z 0-9 _ -,
# hoechstens 64 Zeichen). Werte erzeugen: manage.py telegram_webhook --werte.
TELEGRAM_WEBHOOK_PFAD = config('TELEGRAM_WEBHOOK_PFAD', default='').strip().strip('/')
TELEGRAM_WEBHOOK_SECRET = config('TELEGRAM_WEBHOOK_SECRET', default='').strip()
TELEGRAM_EINLADUNG = config('TELEGRAM_EINLADUNG', default='').strip()

# ── Cache ─────────────────────────────────────────────────────────────────────
#
# Muss ueber Prozessgrenzen hinweg halten: Rate-Limits und Mail-Budget zaehlen
# sonst pro Gunicorn-Worker getrennt (zwei Worker = doppeltes Limit) und sind
# nach jedem Deploy zurueckgesetzt. Der Standard LocMemCache tut genau das -
# einer der Gruende, warum die alte Bremse in der Angriffsnacht nichts hielt.
#
# Datenbank statt Redis: Die Postgres-Instanz laeuft ohnehin, ein zusaetzlicher
# Dienst waere ein weiterer Ausfallpunkt fuer ein paar Zaehler. Die Tabelle legt
# start.sh an; lokal ohne Tabelle faellt Django auf einen Fehler zurueck, den
# der Dummy-Cache im DEBUG-Betrieb vermeidet.
if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'rw_cache',
            'TIMEOUT': 3600,
            # EIG183 (24.09.2026): Bei 5.000 Eintraegen warf der Ueberlauf ein
            # Drittel ALLER Eintraege weg - Sperrzaehler und Mail-Budget
            # eingeschlossen; ein Angreifer konnte die Bremse so selbst
            # leeren. Abgelaufenes raeumt Django vor dem Kappen ohnehin weg;
            # 50.000 liegt weit ueber dem echten Bestand (Zaehler leben
            # hoechstens einen Tag), und gekappt wird dann nur ein Zehntel.
            'OPTIONS': {'MAX_ENTRIES': 50000, 'CULL_FREQUENCY': 10},
        }
    }

# ── Google-Bewertungen (Places API) ───────────────────────────────────────────
#
# Ohne Schluessel laeuft der naechtliche Abgleich gar nicht erst an und die
# statische Liste in apps/core/data/reviews.py bleibt die Wahrheit. Eine
# abgelaufene Rechnung bei Google darf der Startseite nicht die Kundenstimmen
# nehmen.
#
# GOOGLE_PLACE_ID darf leer bleiben: Der Command sucht die Kennung beim ersten
# Lauf ueber GOOGLE_PLACE_QUERY und schreibt sie in die Datenbank. Place-IDs
# duerfen laut Nutzungsbedingungen unbegrenzt gespeichert werden.
GOOGLE_PLACES_API_KEY = config('GOOGLE_PLACES_API_KEY', default='')
GOOGLE_PLACE_ID = config('GOOGLE_PLACE_ID', default='')
GOOGLE_PLACE_QUERY = config(
    'GOOGLE_PLACE_QUERY',
    default='Rümpelwerk Mitteldeutschland, Cansteinstraße 14, 06110 Halle (Saale)',
)

# ── Google Ads: Conversion-Tracking ───────────────────────────────────────────
# Ohne GOOGLE_ADS_CONVERSION_ID passiert nichts: rw_seo.html konfiguriert dann
# kein AW-Ziel, rw_js.html meldet keine Conversion und die CSP-Zeile bleibt
# folgenlos. Lokal und in Vorschau-Deployments entstehen so keine Ads-Requests –
# dasselbe Rueckfall-Muster wie bei GOOGLE_PLACES_API_KEY.
#
# Warum das ueberhaupt gebraucht wird: Bis zum 19.08.2026 trug die Website nur
# das GA4-Tag. Google Ads hat deshalb nie eine echte Anfrage gesehen und
# stattdessen auf "Seitenaufruf", "Engagement" und "Route berechnen" optimiert –
# 564 EUR fuer drei belegbare Kontakte.
#
# Die Labels kommen als *eine* Variable, weil jede Conversion-Aktion in Google
# Ads ihr eigenes bekommt und vier getrennte Env-Namen nur Gelegenheit zum
# Vertippen waeren:
#   GOOGLE_ADS_LABELS=anfrage_submit:AbC-123,angebot_email:DeF-456,...
# Gemeldet wird ausschliesslich, was in _RW_ADS_EVENTS steht. Ein Tippfehler im
# Env-Wert faellt damit hinten runter, statt eine Phantom-Conversion anzulegen –
# und ein Ereignis ohne Label (scroll_depth, rechner_start) erreicht Ads nie.
# Diese vier sind bewusst die einzigen: Nur sie sind ein Kontaktversuch.
_RW_ADS_EVENTS = ('anfrage_submit', 'angebot_email', 'call_click', 'whatsapp_click',
                  'termin_gebucht')

# Das fuenfte Ereignis (Besichtigung gebucht, KV07) ist **ausgeschaltet**, bis der
# Betrieb es freigibt. Seit 02.10.2026 nennt die Datenschutzerklaerung
# (Abschnitte 9 und 10) fuenf Ereignisse, und in Railway steht
# TERMIN_CONVERSION=True; die Vorgabe bleibt aus, damit eine neue Umgebung erst
# nach eigener Pruefung meldet
# (docs/betrieb.md, "Terminbuchung als Conversion"). Aus: keine Kennung in der
# Session, kein Ereignis im Browser - die Buchung selbst laeuft unveraendert.
TERMIN_CONVERSION = config('TERMIN_CONVERSION', default=False, cast=bool)

# Die Kennung wird hier geprueft und nicht im Template escaped. Grund: Django
# escaped in einem <script>-Block auch den Bindestrich ('AW-123'). Das ist
# gueltiges JavaScript, aber die ID ist danach in keinem Pruefskript und keinem
# "Seitenquelltext anzeigen" mehr auffindbar – ausgerechnet bei der Variable,
# deren Vorhandensein man verifizieren will.
#
# Ein gesetzter, aber falsch geschriebener Wert bricht den Start ab, statt still
# auf "kein Tracking" zu fallen. Wer die Variable setzt, will Conversions
# messen; ein Tippfehler (oder versehentlich die GA4-Kennung 'G-…') waere sonst
# wochenlang unsichtbar – genau der Fehler, den Phase 1 beheben soll. Die
# Variable ganz wegzulassen bleibt jederzeit erlaubt.
_ads_id_roh = config('GOOGLE_ADS_CONVERSION_ID', default='').strip()
if _ads_id_roh and not re.fullmatch(r'AW-\d{6,}', _ads_id_roh):
    raise ImproperlyConfigured(
        f'GOOGLE_ADS_CONVERSION_ID muss die Form "AW-123456789" haben, '
        f'bekommen: {_ads_id_roh!r}. Leer lassen schaltet das Ads-Tracking ab.'
    )
GOOGLE_ADS_CONVERSION_ID = _ads_id_roh


def _parse_ads_labels(roh):
    """'anfrage_submit:AbC-123,call_click:DeF-456' -> {'anfrage_submit': 'AbC-123', …}

    Unbekannte Ereignisnamen und leere Labels werden verworfen, nicht gemeldet:
    Ein halb ausgefuellter Env-Wert soll die anderen drei Conversions nicht
    mitreissen.
    """
    paare = {}
    for teil in roh.split(','):
        name, trenner, label = teil.partition(':')
        name, label = name.strip(), label.strip()
        if trenner and name in _RW_ADS_EVENTS and label:
            paare[name] = label
    return paare


GOOGLE_ADS_LABELS = _parse_ads_labels(config('GOOGLE_ADS_LABELS', default=''))

# ── ChatGPT Ads: Measurement Pixel ────────────────────────────────────────────
# Dasselbe Rueckfall-Muster wie oben: Ohne OPENAI_PIXEL_ID laedt rw_seo.html das
# SDK nicht, rw_basis.js meldet nichts, die CSP-Zeilen bleiben folgenlos.
#
# Der Kanal ist seit dem 07.09.2026 in Arbeit (Konto adacct_6a9db25a…, Kampagne
# "Leads Halle"). Am Tag der Uebernahme stand die Kampagne auf "Serving", mass
# aber nichts: Die Datenquelle war angelegt, das Ereignis `lead_created`
# verknuepft – nur der Pixel fehlte auf der Website. Schritt 3 der Checkliste im
# Konto ("Implement and log the event") schliesst genau diese Zeile.
#
# ⚠ Die Kennung ist KEINE AW-Nummer und kein G-Tag: Sie ist die Id der
# *Datenquelle* aus Tools → Conversions, eine 16–32 Zeichen lange base62-Folge
# (z. B. 'JZJYAJuYhN577sYgCbbifL'). ⚠ Gross-/Kleinschreibung entscheidet: Am
# 07.09.2026 stand hier ein kleines 'c' statt des grossen 'C', und der Pixel lief
# einen Tag ins Leere - 404 auf die Konfiguration, 503 auf jedes Ereignis, und die
# Website meldete nichts. Wer hier versehentlich die Kontonummer
# (adacct_…) eintraegt, bekommt keinen Fehler von OpenAI, sondern schlicht nie
# ein Ereignis – deshalb bricht ein formal falscher Wert den Start ab, genau wie
# bei GOOGLE_ADS_CONVERSION_ID.
_oai_pixel_roh = config('OPENAI_PIXEL_ID', default='').strip()
if _oai_pixel_roh and not re.fullmatch(r'[A-Za-z0-9]{16,32}', _oai_pixel_roh):
    raise ImproperlyConfigured(
        f'OPENAI_PIXEL_ID muss eine 16-32 Zeichen lange Kennung aus Buchstaben '
        f'und Ziffern sein (Ads Manager → Tools → Conversions → Data Source), '
        f'bekommen: {_oai_pixel_roh!r}. Leer lassen schaltet den Pixel ab.'
    )
OPENAI_PIXEL_ID = _oai_pixel_roh

# ── Geheime Statistik-Seite ───────────────────────────────────────────────────
STATS_PATH     = config('STATS_PATH',     default='stats-ruempelwerk-intern')
STATS_USER     = config('STATS_USER',     default='')
STATS_PASSWORD = config('STATS_PASSWORD', default='')

if not DEBUG and STATS_PATH == 'stats-ruempelwerk-intern':
    import warnings
    warnings.warn(
        'STATS_PATH uses the default value. Set the STATS_PATH env var to a secret path in production.',
        stacklevel=2,
    )

# ── Django-Admin: derselbe Umgang wie mit der Statistik-Seite ────────────────
#
# Befund B2 vom 06.09.2026: Zwei Zugaenge zu denselben Daten, zwei voellig
# verschiedene Haertungsstufen. Der interne Bereich liegt hinter einem
# geheimen Pfad, der Django-Admin stand auf ``/admin/`` - oeffentlich
# auffindbar, und die Anmeldemaske verraet durch ihr Aussehen die Technik und
# grob die Django-Version.
#
# EIN GEHEIMER PFAD IST KEINE SICHERHEITSMASSNAHME, SONDERN LAERMREDUKTION.
# Er nimmt die Seite aus dem Blickfeld der Scanner, die blind ``/admin/``
# abklopfen - mehr nicht. Wer daraus schliesst, das Passwort duerfe schwaecher
# sein, hat es falsch verstanden. Es bremst weiterhin ``django-axes``
# (10 Versuche, Sperre auf username+ip_address).
#
# DER VORGABEWERT WAR BIS ZUM 10.09.2026 ``'admin'`` - UND GENAU DAS WAR DER
# FEHLER (SI14).
#
# Die Ueberlegung am 06.09. lautete: Ohne gesetzte Umgebungsvariable aendert
# sich nichts, der Deploy kann daran nicht brechen. Das stimmte, und es hatte
# eine Folge, die vier Tage spaeter messbar war: **Die Variable wurde nie
# gesetzt.** Am 10.09.2026 antwortete
# ``https://ruempelwerk-mitteldeutschland.de/admin/`` weiterhin mit einer
# Weiterleitung auf ``/admin/login/?next=/admin/`` und Status 200 - die
# Anmeldemaske stand offen erreichbar da, samt Djangos Aussehen, das die
# Technik und grob die Version verraet. Eine Massnahme, die erst durch einen
# Handgriff in einer fremden Oberfläche wirksam wird, ist keine Massnahme,
# sondern eine Absichtserklaerung.
#
# Der Vorgabewert ist deshalb jetzt derselbe Bauart wie der von STATS_PATH
# darueber: nicht zu erraten, im Repository sichtbar, ohne Umgebungsvariable
# wirksam. Das ist bewusst die **schwaechere** der beiden Stufen -
# wer den Quelltext hat, hat den Pfad. Gegen den Angreifer, um den es hier
# geht, hilft er trotzdem: Scanner klopfen ``/admin/`` blind ab, sie lesen
# kein Repository.
#
# EIN GEHEIMER PFAD BLEIBT LAERMREDUKTION, KEINE SICHERHEITSMASSNAHME.
# Zustaendig sind weiterhin das Passwort und ``django-axes`` (10 Versuche,
# Sperre auf username+ip_address).
#
# **Was das im Betrieb bedeutet:** Nach dem naechsten Deploy ist ``/admin/``
# eine 404. Der Zugang liegt unter dem Pfad, der hier steht - oder unter dem,
# den ADMIN_PATH in Railway nennt. Ein Lesezeichen auf ``/admin/`` laeuft ins
# Leere; das ist der Preis und er ist mit einem neuen Lesezeichen bezahlt.
#
# ``strip('/')`` faengt den haeufigsten Tippfehler beim Setzen der Variablen
# ab: '/geheim/' wuerde sonst zu '//geheim//' und die Route waere unerreichbar,
# ohne dass irgendetwas rot wird.
_ADMIN_PATH_VORGABE = 'verwaltung-ruempelwerk-intern'

ADMIN_PATH = (config('ADMIN_PATH', default=_ADMIN_PATH_VORGABE).strip('/')
              or _ADMIN_PATH_VORGABE)

# Die Warnung meldet sich jetzt bei **zwei** Zustaenden, und der erste ist der
# ernstere: Wer ADMIN_PATH ausdruecklich auf 'admin' setzt, macht die
# Massnahme rueckgaengig, ohne dass irgendetwas rot wird.
if not DEBUG and ADMIN_PATH == 'admin':
    import warnings
    warnings.warn(
        'ADMIN_PATH is set back to "admin". The Django admin login is publicly '
        'reachable again - set the ADMIN_PATH env var to a secret path.',
        stacklevel=2,
    )
elif not DEBUG and ADMIN_PATH == _ADMIN_PATH_VORGABE:
    import warnings
    warnings.warn(
        'ADMIN_PATH uses the value from settings.py, which is readable in the '
        'repository. Set the ADMIN_PATH env var to a secret path in production.',
        stacklevel=2,
    )

# ── Auth Redirects ────────────────────────────────────────────────────────────

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ── Security Headers ─────────────────────────────────────────────────────────

X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Railway beendet HTTPS am Proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ── Das CSRF-Cookie ist seit dem 08.09.2026 HttpOnly (SI16) ──────────────────
# Django selbst nennt HttpOnly auf diesem Cookie "keine praktische
# Zusatzsicherheit" - CSRF schuetzt vor fremden Domains, und wer schon
# JavaScript in dieser Seite ausfuehrt, braucht das Token nicht. Es steht
# trotzdem auf True, weil es nichts kostet und jede Sicherheitspruefung von
# aussen ein Cookie ohne HttpOnly als Mangel meldet.
#
# **Es kostet nur dann nichts, wenn kein JavaScript das Cookie liest.** Genau
# zwei Stellen holen sich das Token, und beide lesen es seit dem 08.09.2026 aus
# dem DOM statt aus dem Cookie:
#   * static/js/rw_rechner.js (``getCsrf``) - der Preisrechner schickt seinen
#     Abschluss als JSON per fetch. Das Feld dafuer liefert
#     ``{% csrf_token %}`` in templates/components/rw_rechner.html, und zwar
#     unbedingt, nicht in einem {% if %}.
#   * templates/stats/cms_form.html - "Bild loeschen" im CMS. Das Feld liefert
#     das Logout-Formular in der Kopfzeile derselben Seite.
# Wer eines der beiden ``{% csrf_token %}`` entfernt, nimmt dem Aufruf sein
# Token: Der Rechner meldet dann einen Fehler, den kein Test sieht - beide
# Wege sind JavaScript. apps/core/tests/test_cookies.py haelt die Paarung fest.
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 1209600  # 2 Wochen

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ── Upload-Limits ─────────────────────────────────────────────────────────────

# Achtung: DATA_UPLOAD_MAX_MEMORY_SIZE begrenzt NUR die normalen Formularfelder.
# Dateien zaehlen nicht mit (django/http/multipartparser.py prueft den Zaehler
# ausschliesslich im FIELD-Zweig) – der Wert bremst also keinen Bildupload aus.
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
# Ab dieser Groesse landet eine hochgeladene Datei auf der Platte statt im RAM.
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# Das CMS erlaubt GALERIE_MAX_BILDER (50) Bilder je Beitrag, beim Typ
# „Vorher/Nachher" 50 vorher UND 50 nachher. Djangos Standard ist 100 – genau
# an der Grenze. Wird sie ueberschritten, bricht der Request mit einem nackten
# 400 ab, ohne dass im CMS eine Meldung erscheint. Deshalb etwas Luft.
DATA_UPLOAD_MAX_NUMBER_FILES = 120

# ── Logging ───────────────────────────────────────────────────────────────────

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] [{levelname}] {name}: {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        # Fehlerwache (VL19, 16.09.2026): jede Zeile ab ERROR wird ein
        # Fehlerereignis in der eigenen Datenbank - apps/core/fehlerwache.py.
        'fehlerwache': {
            'class': 'apps.core.fehlerwache.FehlerwacheHandler',
            'level': 'ERROR',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'fehlerwache'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'fehlerwache'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'fehlerwache'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps.core': {
            'handlers': ['console', 'fehlerwache'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'apps.accounts': {
            'handlers': ['console', 'fehlerwache'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'apps.dashboard': {
            'handlers': ['console', 'fehlerwache'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'apps.stats': {
            'handlers': ['console', 'fehlerwache'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'fehlerwache'],
        'level': 'INFO',
    },
}

# ── Fehler-Monitoring (VL19, 16.09.2026) ──────────────────────────────────────
# Das Monitoring im Betrieb ist die eigene Fehlerwache (Handler oben,
# apps/core/fehlerwache.py) - ohne Drittanbieter. Sentry ist nur eine
# zusaetzliche, ausgeschaltete Weiterleitung: aus, solange SENTRY_DSN leer ist
# (config/sentry.py). RAILWAY_GIT_COMMIT_SHA setzt Railway selbst.
from config.sentry import einrichten as _sentry_einrichten  # noqa: E402
SENTRY_AKTIV = _sentry_einrichten(
    config('SENTRY_DSN', default=''),
    umgebung=config('SENTRY_ENVIRONMENT', default='production'),
    fassung=config('RAILWAY_GIT_COMMIT_SHA', default=''),
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

APPEND_SLASH = True

# ── Site-Meta ─────────────────────────────────────────────────────────────────

SITE_NAME = config('SITE_NAME', default='Rümpelwerk Mitteldeutschland')
# Der Default steht OHNE www. Die kanonische Domain ist die nackte
# (CanonicalDomainMiddleware leitet www per 301 dorthin), und derselbe Wert
# steht in _CANONICAL_SITE_URL (context_processors.py) und _PRODUCTION_DOMAIN
# (sitemaps.py) - die drei muessen zusammenpassen. Vorher nannte der Default
# 'www.': Faellt SITE_URL in der Umgebung einmal weg, zeigten canonical,
# hreflang, og:url und jede Sitemap-URL auf eine Adresse, die sofort
# weiterleitet.
SITE_URL = config('SITE_URL', default='https://ruempelwerk-mitteldeutschland.de')

# ── IndexNow ─────────────────────────────────────────────────────────────────
# Der Schluessel ist KEIN Geheimnis - das Verfahren verlangt ausdruecklich,
# dass er unter https://<domain>/<schluessel>.txt oeffentlich abrufbar ist.
# Genau das beweist die Verfuegungsgewalt ueber die Domain. Deshalb darf er
# im Code stehen; ueber die Umgebung ist er trotzdem austauschbar.
INDEXNOW_KEY = config('INDEXNOW_KEY',
                      default='85b4df002d6ce24b8b732ab4e08d43a1')
