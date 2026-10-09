"""Telegram-Webhook: weitere Handys melden sich selbst an (seit 24.09.2026).

**Wozu.** Der Push (``telegram.py``) ging bis dahin nur an die IDs in
``TELEGRAM_CHAT_IDS``; jedes weitere Handy hiess: ID ermitteln, in Railway
eintragen, neu deployen. Jetzt oeffnet der Inhaber einen Einladungslink
``https://t.me/<bot>?start=<CODE>`` (``manage.py telegram_einrichten
--einladungslink``), tippt auf *Starten* - fertig.

**Warum nicht jeder, der den Bot findet.** Der Bot ist oeffentlich
auffindbar. Eingetragen wird deshalb nur, wer den Code aus
``TELEGRAM_EINLADUNG`` mitschickt; ohne Code oder mit falschem gibt es eine
freundliche Absage, und nach ``MAX_FEHLVERSUCHE`` je Stunde und Chat gar keine
Antwort mehr. Jede Anmeldung wird **allen bisherigen Empfaengern gemeldet** -
ein durchgesickerter Link faellt also sofort auf. Abhilfe dann: den Code in
Railway aendern und den Eintrag in der Django-Verwaltung deaktivieren.

**Drei Schranken vor der Logik:**

1. Der Pfad ``/telegram/<TELEGRAM_WEBHOOK_PFAD>/`` - ohne Umgebungswert oder
   mit falschem Pfad eine 404 wie jede unbekannte Adresse.
2. Der Kopf ``X-Telegram-Bot-Api-Secret-Token`` muss ``TELEGRAM_WEBHOOK_SECRET``
   gleichen (``compare_digest``), sonst 403. Den Kopf setzt Telegram selbst,
   weil ``telegram_webhook --setzen`` ihn als ``secret_token`` hinterlegt.
3. Hoechstens ``MAX_BYTES`` Rumpf.

Danach antwortet die View **immer 200** - auch bei kaputtem JSON oder
fremden Updates. Alles andere liesse Telegram dasselbe Update stundenlang
wiederholen. Die Antworten an die Chats laufen im Hintergrund-Thread
(``_hintergrund``), damit Telegram nicht auf die Bot-API warten muss.

WAS DIESE DATEI NICHT LEISTET
-----------------------------
* **Gruppen.** Nur private Chats; Nachrichten aus Gruppen und Kanaelen werden
  still verworfen.
* **Feste Empfaenger austragen.** ``/stop`` wirkt nur auf die Datenbank -
  ``TELEGRAM_CHAT_IDS`` aendert nur Railway.
* **Datenschutz-Text.** Die Empfaenger sind Mitarbeiter des Betriebs; die
  Datenschutzerklaerung nennt Telegram bereits als Empfaenger.
"""

import hmac
import html
import json
import logging
import threading

from django.conf import settings
from django.core.cache import cache
from django.db import connection, transaction
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

from . import telegram

logger = logging.getLogger('apps.core')

#: Hoechstens so viele **aktive** selbst angemeldete Empfaenger.
MAX_EMPFAENGER = 5

#: Ein Update mit einer Textnachricht ist ein paar hundert Byte gross.
MAX_BYTES = 64 * 1024

#: Falsche oder fehlende Codes je Chat und Stunde, die noch beantwortet werden.
MAX_FEHLVERSUCHE = 5
_FEHLVERSUCH_SEKUNDEN = 3600

TEXT_ANGEMELDET = ('Angemeldet: Sie bekommen ab jetzt jede neue Anfrage von '
                   'ruempelwerk-mitteldeutschland.de.')
TEXT_SCHON_ANGEMELDET = ('Sie sind bereits angemeldet und bekommen jede neue '
                         'Anfrage von ruempelwerk-mitteldeutschland.de.')
TEXT_ABSAGE = ('Dieser Bot ist nur für das Team von Rümpelwerk. '
               'Bitte den Einladungslink verwenden.')
TEXT_VOLL = ('Die Anmeldung ist gerade nicht möglich: Es sind bereits '
             f'{MAX_EMPFAENGER} Handys angemeldet. Bitte beim Betreiber der '
             'Website melden.')
TEXT_ABGEMELDET = ('Abgemeldet: Sie bekommen keine Anfragen mehr. Zum erneuten '
                   'Anmelden den Einladungslink noch einmal öffnen.')
TEXT_FEST = ('Dieser Chat ist fest in der Konfiguration der Website eingetragen '
             'und lässt sich nicht per /stop abmelden. Bitte beim Betreiber der '
             'Website melden.')
TEXT_NICHT_ANGEMELDET = 'Dieser Chat ist nicht angemeldet.'


def _gleich(a, b):
    """Zeitkonstanter Vergleich; ein leerer Sollwert passt nie."""
    if not b:
        return False
    return hmac.compare_digest(str(a or '').encode('utf-8'), str(b).encode('utf-8'))


def _hintergrund(ziel):
    """Startet ``ziel`` im Daemon-Thread und schliesst danach dessen DB-Verbindung.

    Tests ersetzen diese Funktion durch einen direkten Aufruf.
    """
    def _lauf():
        try:
            ziel()
        # audit-ok P02: Der Thread darf nie still sterben - der Fehler geht in
        # die Fehlerwache.
        except Exception as exc:                                # noqa: BLE001
            logger.error('Telegram-Webhook: Hintergrund fehlgeschlagen | %s: %s',
                         type(exc).__name__, telegram._ohne_token(exc))
        finally:
            connection.close()
    threading.Thread(target=_lauf, daemon=True).start()


def _antwort_200():
    antwort = HttpResponse('ok', content_type='text/plain; charset=utf-8')
    antwort['X-Robots-Tag'] = 'noindex, nofollow'
    antwort['Cache-Control'] = 'no-store'
    return antwort


# csrf-ok: Aufrufer ist Telegram (kein Browser, kein Token); Anmeldung ueber geheimen Pfad und X-Telegram-Bot-Api-Secret-Token.
@csrf_exempt
def webhook(request, pfad):
    """``POST /telegram/<pfad>/`` - nimmt Updates von Telegram entgegen."""
    if not _gleich(pfad, getattr(settings, 'TELEGRAM_WEBHOOK_PFAD', '')):
        raise Http404
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    if not _gleich(request.headers.get('X-Telegram-Bot-Api-Secret-Token', ''),
                   getattr(settings, 'TELEGRAM_WEBHOOK_SECRET', '')):
        logger.warning('Telegram-Webhook: falscher oder fehlender Secret-Kopf')
        return HttpResponseForbidden('forbidden')

    try:
        laenge = int(request.META.get('CONTENT_LENGTH') or 0)
    except ValueError:
        laenge = 0
    if laenge > MAX_BYTES:
        logger.warning('Telegram-Webhook: Rumpf zu gross (%d Byte), verworfen', laenge)
        return _antwort_200()
    try:
        rumpf = request.body
        update = json.loads(rumpf.decode('utf-8')) if len(rumpf) <= MAX_BYTES else None
    # audit-ok P02: Kaputter Rumpf -> 200, sonst wiederholt Telegram ihn.
    except Exception:                                           # noqa: BLE001
        update = None
    if isinstance(update, dict):
        try:
            verarbeiten(update)
        except Exception as exc:                                # noqa: BLE001
            logger.error('Telegram-Webhook: Update nicht verarbeitet | %s: %s',
                         type(exc).__name__, telegram._ohne_token(exc))
    return _antwort_200()


# ── Logik ───────────────────────────────────────────────────────────────────

def _anzeigename(nachricht):
    """``'Oliver Pohl (@oliver)'`` aus ``from`` bzw. ``chat`` der Nachricht."""
    person = nachricht.get('from') or nachricht.get('chat') or {}
    name = ' '.join(filter(None, (str(person.get('first_name') or '').strip(),
                                  str(person.get('last_name') or '').strip())))
    benutzer = str(person.get('username') or '').strip()
    if benutzer:
        name = f'{name} (@{benutzer})' if name else f'@{benutzer}'
    return (name or 'ohne Namen')[:200]


def _befehl(text):
    """``'/start@ruempelbot  ABC'`` -> ``('/start', 'ABC')``."""
    teile = (text or '').strip().split(maxsplit=1)
    if not teile:
        return '', ''
    befehl = teile[0].split('@', 1)[0].lower()
    return befehl, (teile[1].strip() if len(teile) > 1 else '')


def _fehlversuch_erlaubt(chat):
    """Zaehlt einen Fehlversuch; True, solange noch geantwortet werden darf."""
    schluessel = f'telegram:fehlversuch:{chat}'
    try:
        cache.add(schluessel, 0, _FEHLVERSUCH_SEKUNDEN)
        anzahl = cache.incr(schluessel)
    # audit-ok P02: ohne Cache lieber antworten als den Webhook abbrechen.
    except Exception:                                           # noqa: BLE001
        return True
    return anzahl <= MAX_FEHLVERSUCHE


def _antworten(chat, text):
    _hintergrund(lambda: telegram.an_chat(chat, html.escape(text, quote=False)))


def verarbeiten(update):
    """Ein Update auswerten. Nur Textnachrichten aus privaten Chats."""
    nachricht = update.get('message')
    if not isinstance(nachricht, dict):
        return
    chat_info = nachricht.get('chat') or {}
    if chat_info.get('type') != 'private' or chat_info.get('id') is None:
        return
    chat = str(chat_info['id'])
    befehl, argument = _befehl(nachricht.get('text'))

    if befehl == '/start':
        if chat in telegram.chat_ids():
            # Schon Empfaenger (fest oder angemeldet): kein Code noetig, und
            # die Antwort verraet niemandem etwas, der nicht ohnehin dazugehoert.
            _antworten(chat, TEXT_SCHON_ANGEMELDET)
        elif _gleich(argument, getattr(settings, 'TELEGRAM_EINLADUNG', '')):
            _anmelden(chat, _anzeigename(nachricht))
        elif _fehlversuch_erlaubt(chat):
            logger.info('Telegram-Webhook: /start ohne gueltigen Code | Chat %s', chat)
            _antworten(chat, TEXT_ABSAGE)
    elif befehl == '/stop':
        _abmelden(chat)


def _anmelden(chat, name):
    from .models import TelegramEmpfaenger

    if chat in telegram.env_chat_ids():
        _antworten(chat, TEXT_SCHON_ANGEMELDET)
        return
    bisherige = [c for c in telegram.chat_ids() if c != chat]
    with transaction.atomic():
        eintrag = (TelegramEmpfaenger.objects.select_for_update()
                   .filter(chat_id=chat).first())
        if eintrag and eintrag.aktiv:
            ergebnis = 'schon'
        elif TelegramEmpfaenger.objects.filter(aktiv=True).count() >= MAX_EMPFAENGER:
            ergebnis = 'voll'
        else:
            if eintrag:
                eintrag.aktiv = True
                eintrag.name = name
                eintrag.save(update_fields=['aktiv', 'name'])
            else:
                TelegramEmpfaenger.objects.create(chat_id=chat, name=name)
            ergebnis = 'neu'

    if ergebnis == 'schon':
        _antworten(chat, TEXT_SCHON_ANGEMELDET)
        return
    if ergebnis == 'voll':
        logger.warning('Telegram-Webhook: Anmeldung abgelehnt, %d Empfaenger erreicht '
                       '| %s', MAX_EMPFAENGER, name)
        _antworten(chat, TEXT_VOLL)
        return

    logger.warning('Telegram-Empfaenger angemeldet | Chat %s | %s', chat, name)
    meldung = (f'👤 <b>Neuer Empfänger angemeldet:</b> {html.escape(name, quote=False)}\n\n'
               'Nicht erwartet? Dann in Railway TELEGRAM_EINLADUNG ändern und den '
               'Eintrag in der Verwaltung deaktivieren.')

    def _senden():
        telegram.an_chat(chat, html.escape(TEXT_ANGEMELDET, quote=False))
        if bisherige:
            telegram.senden(meldung, chats=bisherige)
    _hintergrund(_senden)


def _abmelden(chat):
    from .models import TelegramEmpfaenger

    if chat in telegram.env_chat_ids():
        _antworten(chat, TEXT_FEST)
        return
    geaendert = TelegramEmpfaenger.objects.filter(chat_id=chat, aktiv=True).update(aktiv=False)
    if geaendert:
        logger.warning('Telegram-Empfaenger abgemeldet (/stop) | Chat %s', chat)
        _antworten(chat, TEXT_ABGEMELDET)
    elif _fehlversuch_erlaubt(chat):
        _antworten(chat, TEXT_NICHT_ANGEMELDET)
