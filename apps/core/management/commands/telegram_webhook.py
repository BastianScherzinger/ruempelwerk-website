"""Telegram-Webhook bei Telegram eintragen, pruefen oder entfernen.

    python manage.py telegram_webhook --werte    # drei Zufallswerte fuer Railway
    python manage.py telegram_webhook --setzen   # setWebhook auf SITE_URL/telegram/<PFAD>/
    python manage.py telegram_webhook --info     # getWebhookInfo
    python manage.py telegram_webhook --loeschen # deleteWebhook (zurueck zu getUpdates)

Braucht ``TELEGRAM_BOT_TOKEN``, fuer ``--setzen`` zusaetzlich
``TELEGRAM_WEBHOOK_PFAD`` und ``TELEGRAM_WEBHOOK_SECRET`` (und sinnvollerweise
``TELEGRAM_EINLADUNG``). Ablauf: ``docs/betrieb.md``, "Telegram-Benachrichtigung".

**Weder Token noch Secret noch Pfad werden ausgegeben** - ``--info`` zeigt die
hinterlegte URL nur bis ``/telegram/``. Mit gesetztem Webhook liefert
``getUpdates`` nichts mehr; ``telegram_einrichten`` sagt das dann.
"""

import re
import secrets

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.core import telegram

#: Zeichenvorrat, den Telegram fuer ``secret_token`` und Start-Parameter erlaubt.
_ERLAUBT = re.compile(r'^[A-Za-z0-9_-]{1,256}$')


def webhook_url():
    basis = (getattr(settings, 'SITE_URL', '') or '').rstrip('/')
    return f'{basis}/telegram/{settings.TELEGRAM_WEBHOOK_PFAD}/'


def _gekuerzt(url):
    """Die URL ohne den geheimen Pfad."""
    if not url:
        return '(keine)'
    teil = url.split('/telegram/', 1)
    return f'{teil[0]}/telegram/…' if len(teil) == 2 else url


class Command(BaseCommand):
    help = 'Setzt (--setzen), prueft (--info) oder entfernt (--loeschen) den Telegram-Webhook.'

    def add_arguments(self, parser):
        gruppe = parser.add_mutually_exclusive_group(required=True)
        gruppe.add_argument('--setzen', action='store_true',
                            help='setWebhook mit SITE_URL/telegram/<PFAD>/ und secret_token.')
        gruppe.add_argument('--info', action='store_true', help='getWebhookInfo anzeigen.')
        gruppe.add_argument('--loeschen', action='store_true',
                            help='deleteWebhook - danach geht getUpdates wieder.')
        gruppe.add_argument('--werte', action='store_true',
                            help='Drei Zufallswerte fuer PFAD, SECRET und EINLADUNG ausgeben.')

    def handle(self, *args, **optionen):
        if optionen['werte']:
            return self._werte()
        if not telegram._token():
            raise CommandError('TELEGRAM_BOT_TOKEN ist nicht gesetzt. '
                               '"railway run python manage.py telegram_webhook ..." benutzen.')
        if optionen['setzen']:
            return self._setzen()
        if optionen['loeschen']:
            return self._aufruf('deleteWebhook', {'drop_pending_updates': True},
                                'Webhook entfernt. getUpdates (telegram_einrichten) geht wieder.')
        return self._info()

    def _werte(self):
        self.stdout.write('In Railway setzen (Werte nirgends sonst ablegen):')
        self.stdout.write(f'  TELEGRAM_WEBHOOK_PFAD={secrets.token_urlsafe(24)}')
        self.stdout.write(f'  TELEGRAM_WEBHOOK_SECRET={secrets.token_urlsafe(32)}')
        self.stdout.write(f'  TELEGRAM_EINLADUNG={secrets.token_urlsafe(18)}')

    def _aufruf(self, methode, daten, erfolg):
        try:
            antwort = telegram.api_aufruf(methode, daten)
        except Exception as exc:                                # noqa: BLE001
            raise CommandError(f'Telegram nicht erreichbar: {telegram._ohne_token(exc)}') from None
        if not antwort.get('ok'):
            raise CommandError(f'Telegram lehnt {methode} ab: '
                               f'{telegram._ohne_token(antwort.get("description", ""))}')
        self.stdout.write(self.style.SUCCESS(erfolg))
        return antwort

    def _setzen(self):
        pfad = settings.TELEGRAM_WEBHOOK_PFAD
        secret = settings.TELEGRAM_WEBHOOK_SECRET
        if not pfad or not secret:
            raise CommandError('TELEGRAM_WEBHOOK_PFAD und TELEGRAM_WEBHOOK_SECRET muessen gesetzt '
                               'sein (Werte erzeugen: telegram_webhook --werte).')
        if not _ERLAUBT.match(secret):
            raise CommandError('TELEGRAM_WEBHOOK_SECRET darf nur A-Z, a-z, 0-9, _ und - enthalten.')
        if not re.match(r'^[A-Za-z0-9_-]{16,}$', pfad):
            raise CommandError('TELEGRAM_WEBHOOK_PFAD: mindestens 16 Zeichen aus A-Z, a-z, 0-9, _ -.')
        url = webhook_url()
        if not url.startswith('https://'):
            raise CommandError(f'SITE_URL muss mit https:// beginnen (Telegram verlangt TLS): '
                               f'{_gekuerzt(url)}')
        einladung = settings.TELEGRAM_EINLADUNG
        if not einladung:
            self.stdout.write(self.style.WARNING(
                'TELEGRAM_EINLADUNG ist leer - der Webhook laeuft, aber niemand kann sich anmelden.'))
        elif not re.match(r'^[A-Za-z0-9_-]{8,64}$', einladung):
            raise CommandError('TELEGRAM_EINLADUNG: 8-64 Zeichen aus A-Z, a-z, 0-9, _ - '
                               '(Grenze von Telegrams Start-Parameter).')
        self._aufruf('setWebhook', {
            'url': url,
            'secret_token': secret,
            'allowed_updates': ['message'],
            'drop_pending_updates': True,
        }, f'Webhook gesetzt: {_gekuerzt(url)}')

    def _info(self):
        try:
            antwort = telegram.api_aufruf('getWebhookInfo')
        except Exception as exc:                                # noqa: BLE001
            raise CommandError(f'Telegram nicht erreichbar: {telegram._ohne_token(exc)}') from None
        info = antwort.get('result') or {}
        url = info.get('url') or ''
        erwartet = webhook_url() if settings.TELEGRAM_WEBHOOK_PFAD else ''
        self.stdout.write(f'Webhook:           {_gekuerzt(url)}')
        if url:
            self.stdout.write('Passt zu SITE_URL/TELEGRAM_WEBHOOK_PFAD: '
                              + ('ja' if url == erwartet else 'NEIN - telegram_webhook --setzen'))
        self.stdout.write(f'Wartende Updates:  {info.get("pending_update_count", 0)}')
        self.stdout.write(f'Erlaubte Updates:  {", ".join(info.get("allowed_updates") or []) or "alle"}')
        if info.get('last_error_message'):
            self.stdout.write(self.style.WARNING(
                f'Letzter Fehler:    {telegram._ohne_token(info["last_error_message"])}'))
        else:
            self.stdout.write('Letzter Fehler:    keiner')
