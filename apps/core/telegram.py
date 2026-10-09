"""Telegram-Push: jede echte Anfrage sofort aufs Handy (seit 24.09.2026).

**Warum es das gibt.** Bis dahin erreichte eine Anfrage den Betrieb nur per
Mail - und genau dieser eine Weg war vom 06. bis 24.09.2026 fuer den
Preisrechner tot, ohne dass es jemand merkte (jede Einsendung endete in einem
500, siehe Migration ``0020``). Ein zweiter, unabhaengiger Kanal meldet eine
Anfrage auch dann, wenn der Mailweg ausfaellt, und er meldet den Ausfall des
Mailwegs selbst (:func:`alarm`) - sonst meldet nur der kaputte Kanal sich
selbst, also niemand.

**Konfiguration:** ``TELEGRAM_BOT_TOKEN`` und ``TELEGRAM_CHAT_IDS``
(kommagetrennt) aus der Umgebung; dazu seit 24.09.2026 die Handys, die sich
selbst per Einladungslink angemeldet haben (``TelegramEmpfaenger``, Webhook
in ``telegram_webhook.py``). Ohne Token oder ohne jeden Empfaenger ist der Push
still aus - kein Fehler, keine Warnung je Anfrage, eine INFO-Zeile beim Start
(``apps.py``). Einrichtung: ``docs/betrieb.md``, Abschnitt
„Telegram-Benachrichtigung“, und ``manage.py telegram_einrichten``.

**Was hineingeht - und was nicht.** Art der Anfrage, Name, Telefon, PLZ/Ort,
Objekt/Leistung, ggf. Richtpreis, ein Link ins Dashboard. **Keine
E-Mail-Adresse des Kunden, keine vollstaendige Nachricht, keine Strasse.**
Telegram ist ein weiterer Empfaenger personenbezogener Daten (die
Datenschutzerklaerung nennt ihn, Paket 2); je weniger in der Nachricht steht,
desto weniger liegt dort.

**Der Token erscheint nie im Log.** Er steckt in der URL der Bot-API; jede
Fehlermeldung laeuft durch :func:`_ohne_token`, bevor sie geloggt wird.

WAS DIESE DATEI NICHT LEISTET
-----------------------------
* **Zustellung.** ``True`` heisst: Telegram hat ``sendMessage`` mit
  ``ok: true`` beantwortet. Ob das Handy die Nachricht anzeigt (Ton aus,
  Chat stummgeschaltet), weiss niemand.
* **Mehrere Empfaenger atomar.** Bei zwei Chat-IDs gilt die Nachricht als
  gesendet, sobald **einer** sie bekommen hat - sonst schickte der
  Nachzuegler dem anderen ein Duplikat. Der gescheiterte steht als
  ``logger.error`` in der Fehlerwache.
"""

import html
import json
import logging
import re
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger('apps.core')

#: Die Bot-API. ``{token}`` wird nur hier eingesetzt und nie geloggt.
_API = 'https://api.telegram.org/bot{token}/{methode}'

#: Obergrenze je Aufruf. Der Versand laeuft im Hintergrund-Thread, aber ein
#: haengender Aufruf haelt dort eine Datenbankverbindung.
TIMEOUT_SEKUNDEN = 8

#: Telegram lehnt Nachrichten ueber 4096 Zeichen ab.
_MAX_ZEICHEN = 4000

#: Ein Alarm derselben Sorte hoechstens einmal je Stunde.
_ALARM_SPERRE_SEKUNDEN = 3600


def _token():
    return (getattr(settings, 'TELEGRAM_BOT_TOKEN', '') or '').strip()


def env_chat_ids():
    """Die festen Empfaenger - aus ``settings.TELEGRAM_CHAT_IDS`` (Liste)."""
    roh = getattr(settings, 'TELEGRAM_CHAT_IDS', []) or []
    if isinstance(roh, str):
        roh = roh.split(',')
    return [str(c).strip() for c in roh if str(c).strip()]


def db_chat_ids():
    """Die selbst angemeldeten Empfaenger (``TelegramEmpfaenger``, aktiv).

    Ohne Datenbank (Start, ``SimpleTestCase``, Ausfall) eine leere Liste -
    dann gehen Push und Alarm wenigstens an die festen Empfaenger.
    """
    try:
        from .models import TelegramEmpfaenger
        return list(TelegramEmpfaenger.objects.filter(aktiv=True)
                    .order_by('angemeldet_am').values_list('chat_id', flat=True))
    # audit-ok P02: Ein Datenbankfehler darf den Push an die festen
    # Empfaenger nicht mitreissen - gerade der Alarm soll dann noch rausgehen.
    except Exception as exc:                                    # noqa: BLE001
        logger.warning('Telegram-Empfaenger aus der Datenbank nicht lesbar: %s',
                       type(exc).__name__)
        return []


def chat_ids():
    """Alle Empfaenger: ``TELEGRAM_CHAT_IDS`` und die aktiven DB-Eintraege.

    Dedupliziert, Reihenfolge: erst die Umgebung, dann nach Anmeldedatum.
    """
    gesehen = []
    for chat in env_chat_ids() + db_chat_ids():
        if chat not in gesehen:
            gesehen.append(chat)
    return gesehen


def aktiv():
    """True, wenn Token **und** mindestens eine Chat-ID gesetzt sind."""
    return bool(_token() and chat_ids())


def _ohne_token(text):
    """Entfernt den Token aus jedem Text, der geloggt werden koennte."""
    text = str(text or '')
    token = _token()
    if token:
        text = text.replace(token, '[Token]')
    return re.sub(r'bot\d+:[\w-]+', 'bot[Token]', text)


def api_aufruf(methode, daten=None, timeout=TIMEOUT_SEKUNDEN):
    """Ruft die Bot-API auf und gibt die JSON-Antwort zurueck.

    Wirft bei Netz- und HTTP-Fehlern; ein ``HTTPError`` bekommt die
    ``description`` aus Telegrams Antwort (ohne Token) als Meldung.
    """
    url = _API.format(token=_token(), methode=methode)
    rumpf = json.dumps(daten or {}).encode('utf-8')
    anfrage = urllib.request.Request(
        url, data=rumpf,
        headers={'Content-Type': 'application/json',
                 'User-Agent': 'Ruempelwerk-Website/1.0'},
    )
    try:
        with urllib.request.urlopen(anfrage, timeout=timeout) as antwort:
            return json.loads(antwort.read().decode('utf-8') or '{}')
    except urllib.error.HTTPError as exc:
        try:
            beschreibung = json.loads(exc.read().decode('utf-8')).get('description', '')
        except (ValueError, AttributeError, OSError):
            beschreibung = ''
        raise RuntimeError(_ohne_token(
            f'HTTP {exc.code} {beschreibung}'.strip())) from None


#: Fehlertexte der Bot-API, nach denen ein Chat nie wieder erreichbar ist:
#: geloescht, Bot blockiert, Konto deaktiviert. Ein DB-Empfaenger wird dann
#: abgemeldet, statt bei jeder Anfrage erneut in der Fehlerwache zu landen.
_CHAT_WEG = ('chat not found', 'bot was blocked', 'user is deactivated',
             'bot was kicked', "bot can't initiate conversation")


def _chat_weg(text):
    text = str(text or '').lower()
    return any(merkmal in text for merkmal in _CHAT_WEG)


def _abmelden_wenn_weg(chat, meldung):
    """Deaktiviert einen DB-Empfaenger, den Telegram nicht mehr zustellt.

    True, wenn ein Eintrag deaktiviert wurde. Feste Empfaenger aus der
    Umgebung bleiben unberuehrt (die aendert nur Railway).
    """
    if not _chat_weg(meldung) or chat in env_chat_ids():
        return False
    try:
        from .models import TelegramEmpfaenger
        geaendert = TelegramEmpfaenger.objects.filter(
            chat_id=chat, aktiv=True).update(aktiv=False)
    except Exception as exc:                                    # noqa: BLE001
        logger.warning('Telegram-Empfaenger nicht abmeldbar: %s', type(exc).__name__)
        return False
    if geaendert:
        logger.warning('Telegram-Empfaenger abgemeldet (nicht mehr erreichbar) | '
                       'Chat %s | %s', chat, _ohne_token(meldung))
    return bool(geaendert)


def an_chat(chat, text):
    """Schickt ``text`` (HTML) an **einen** Chat. True bei ``ok: true``.

    Wirft nie. Meldet Telegram, dass der Chat weg ist, wird ein
    selbst angemeldeter Empfaenger deaktiviert (WARNING); jeder andere
    Fehler ist ein ``logger.error`` (Fehlerwache).
    """
    if not _token():
        return False
    try:
        antwort = api_aufruf('sendMessage', {
            'chat_id': chat,
            'text': text[:_MAX_ZEICHEN],
            'parse_mode': 'HTML',
            'link_preview_options': {'is_disabled': True},
        })
        if antwort.get('ok'):
            return True
        meldung = _ohne_token(antwort.get('description', ''))
        if not _abmelden_wenn_weg(chat, meldung):
            logger.error('Telegram-Versand abgelehnt | Chat %s | %s', chat, meldung)
    # audit-ok P02: Netz-, HTTP- und JSON-Fehler landen alle in der
    # Fehlerwache; der Aufrufer bekommt False und der Nachzuegler versucht es.
    except Exception as exc:                                    # noqa: BLE001
        meldung = _ohne_token(exc)
        if not _abmelden_wenn_weg(chat, meldung):
            logger.error('Telegram-Versand fehlgeschlagen | Chat %s | %s: %s',
                         chat, type(exc).__name__, meldung)
    return False


def senden(text, chats=None):
    """Schickt ``text`` (HTML) an alle Empfaenger. True, wenn einer ihn bekam.

    Empfaenger sind ``chat_ids()`` (Umgebung und Datenbank) oder die
    uebergebene Liste ``chats``. Ohne Konfiguration: ``False``, ohne Log -
    der Push ist dann bewusst aus. Jeder Fehler wird festgehalten und **nie**
    nach oben geworfen: Ein Telegram-Ausfall darf keinen Mailversand und
    keine Anfrage mitreissen.
    """
    if not _token():
        return False
    erfolg = False
    for chat in (chat_ids() if chats is None else chats):
        if an_chat(chat, text):
            erfolg = True
    return erfolg


# ── Nachricht bauen ─────────────────────────────────────────────────────────

def _e(wert):
    """Text fuer ``parse_mode=HTML``: nur ``<``, ``>`` und ``&`` escapen."""
    return html.escape(str(wert or '').strip(), quote=False)


_PLZ_ORT = re.compile(r'\b(\d{5})\s+([^\d,;\n]{2,60})')


def plz_ort(adresse):
    """``'Musterweg 1, 04103 Leipzig'`` -> ``'04103 Leipzig'``; sonst ``''``.

    Bewusst nur PLZ und Ort: Die Strasse steht in der Mail und im Dashboard,
    fuer die Entscheidung "zurueckrufen oder nicht" braucht es sie nicht.
    """
    treffer = _PLZ_ORT.search(adresse or '')
    if not treffer:
        return ''
    return f'{treffer.group(1)} {treffer.group(2).strip()}'


def dashboard_url():
    basis = (getattr(settings, 'SITE_URL', '') or '').rstrip('/')
    pfad = (getattr(settings, 'STATS_PATH', '') or '').strip('/')
    return f'{basis}/{pfad}/anfragen/'


_KOPF = {
    'anfrage': '🔔 <b>Neue Anfrage</b>',
    'preisangebot': '🧮 <b>Neue Preisrechner-Anfrage</b>',
    'kooperation': '🤝 <b>Neue Kooperationsanfrage</b>',
    'bewerbung': '👷 <b>Neue Bewerbung</b>',
    'termin': '📅 <b>Neue Terminanfrage</b>',
}


def nachricht(art, felder):
    """Der Nachrichtentext zu einer Anfrage - aus einem einfachen dict.

    ``felder`` kennt: ``name``, ``telefon``, ``ort``, ``objekt``,
    ``richtpreis`` (int), ``firma``, ``wunschtermin``, ``art`` (Art der
    Besichtigung bei Terminanfragen, "Vor Ort" oder "Per WhatsApp-Video"). Eine E-Mail-Adresse
    wird hier nie gelesen, auch wenn sie im dict stuende.
    """
    from .data.pricing import euro

    kopf = _KOPF.get(art, '🔔 <b>Neue Einsendung</b>')
    if art == 'termin' and 'video' in str(felder.get('art') or '').lower():
        kopf = '📹 <b>Neue Video-Terminanfrage</b>'
    zeilen = [kopf, '']
    zeilen.append(f"Name: {_e(felder.get('name')) or '–'}")
    if felder.get('firma'):
        zeilen.append(f"Firma: {_e(felder['firma'])}")
    telefon = _e(felder.get('telefon'))
    # Die Nummer steht sichtbar und unformatiert da: Telegram macht daraus
    # selbst einen antippbaren Anruf-Link. Ein <a href="tel:..."> lehnt die
    # Bot-API ab (nur http/https/tg).
    zeilen.append(f'Telefon: {telefon}' if telefon
                  else 'Telefon: – (nur E-Mail angegeben, steht in der Mail)')
    if felder.get('ort'):
        zeilen.append(f"Ort: {_e(felder['ort'])}")
    if felder.get('objekt'):
        zeilen.append(f"Objekt: {_e(felder['objekt'])}")
    if felder.get('richtpreis'):
        zeilen.append(f"Richtpreis: {euro(felder['richtpreis'])} €")
    if felder.get('wunschtermin'):
        zeilen.append(f"Wunschtermin: {_e(felder['wunschtermin'])}")
    if felder.get('art'):
        zeilen.append(f"Art: {_e(felder['art'])}")
    zeilen += ['', f'<a href="{html.escape(dashboard_url(), quote=True)}">'
                   'Im Dashboard ansehen</a>']
    return '\n'.join(zeilen)


def felder_fuer(obj):
    """(art, felder) zu einem gespeicherten Datensatz der vier Formulare."""
    typ = type(obj).__name__
    if typ == 'Anfrage':
        return 'anfrage', {
            'name': obj.name, 'telefon': obj.telefon,
            'ort': plz_ort(obj.adresse), 'objekt': obj.get_leistung_display(),
        }
    if typ == 'PreisAngebot':
        return 'preisangebot', {
            'name': obj.name, 'ort': getattr(obj, 'ort', ''),
            'objekt': f'{obj.leistung_label}, {obj.groesse_label}'.strip(', '),
            'richtpreis': obj.pmin,
        }
    if typ == 'Kooperationsanfrage':
        return 'kooperation', {
            'name': obj.name, 'firma': obj.firma, 'telefon': obj.telefon,
            'objekt': obj.get_art_display(),
        }
    if typ == 'Bewerbung':
        return 'bewerbung', {
            'name': obj.name, 'telefon': obj.telefon,
            'objekt': obj.stelle_anzeige(),
        }
    if typ == 'Besichtigungstermin':
        from django.utils import timezone as _tz
        return 'termin', {
            'name': obj.name, 'telefon': obj.telefon,
            'ort': plz_ort(obj.adresse), 'objekt': obj.get_objektart_display(),
            'art': obj.get_besichtigungsart_display(),
            'wunschtermin': _tz.localtime(obj.beginn).strftime('%d.%m.%Y %H:%M Uhr'),
        }
    return 'sonstiges', {'name': getattr(obj, 'name', '')}


def nachricht_fuer(obj):
    return nachricht(*felder_fuer(obj))


# ── Alarm: wenn der Mailweg ausfaellt ───────────────────────────────────────

def alarm(text, sorte):
    """Kurze Warnung aufs Handy - hoechstens einmal je Stunde und ``sorte``.

    Fuer die Faelle, in denen der Mailweg selbst kaputt ist (kein Versandweg,
    Notbremse, Nachzuegler gibt auf, Waechter). Die Fehlerwache meldet
    dieselben Faelle per Mail - also ueber genau den Weg, der gerade nicht
    geht.
    """
    if not aktiv():
        return False
    try:
        from django.core.cache import cache
        if not cache.add(f'telegram:alarm:{sorte}', 1, _ALARM_SPERRE_SEKUNDEN):
            return False
    # audit-ok P02: ohne Cache lieber einmal zu oft warnen als gar nicht.
    except Exception:                                           # noqa: BLE001
        pass
    return senden(f'⚠️ <b>Website Rümpelwerk: Warnung</b>\n\n{_e(text)}\n\n'
                  f'<a href="{html.escape(dashboard_url(), quote=True)}">'
                  'Anfragen im Dashboard</a>')
