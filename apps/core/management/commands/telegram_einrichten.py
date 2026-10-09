"""Telegram-Push einrichten: Chat-IDs finden und eine Testnachricht schicken.

    python manage.py telegram_einrichten          # zeigt die Chat-IDs aus getUpdates
    python manage.py telegram_einrichten --test   # Testnachricht an alle Empfaenger
    python manage.py telegram_einrichten --einladungslink   # t.me-Link mit TELEGRAM_EINLADUNG

Seit 24.09.2026 melden sich weitere Handys selbst an (Einladungslink,
``telegram_webhook.py``). **Ist der Webhook gesetzt, liefert getUpdates
nichts mehr** - der Befehl sagt das dann, statt eine leere Liste zu zeigen.

Ablauf (ausfuehrlich in ``docs/betrieb.md``, "Telegram-Benachrichtigung"):
Bot bei @BotFather anlegen, Token als ``TELEGRAM_BOT_TOKEN`` setzen, dem Bot
im Handy "/start" schicken, dann diesen Befehl ohne Argument - er listet, wer
dem Bot geschrieben hat, mit Chat-ID. Die ID kommt in ``TELEGRAM_CHAT_IDS``.

**Der Token wird nie ausgegeben**, auch nicht in Fehlermeldungen
(``telegram._ohne_token``). Der Befehl schreibt nichts in die Datenbank.
"""

import logging

from django.core.management.base import BaseCommand, CommandError

from apps.core import telegram

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Zeigt die Chat-IDs des Telegram-Bots (getUpdates) oder schickt mit --test eine Testnachricht.'

    def add_arguments(self, parser):
        parser.add_argument('--test', action='store_true',
                            help='Testnachricht an alle Empfaenger schicken.')
        parser.add_argument('--einladungslink', action='store_true',
                            help='Link t.me/<bot>?start=<TELEGRAM_EINLADUNG> ausgeben.')

    def handle(self, *args, **optionen):
        if not telegram._token():
            raise CommandError(
                'TELEGRAM_BOT_TOKEN ist nicht gesetzt. Lokal in .env eintragen oder '
                '"railway run python manage.py telegram_einrichten" benutzen.')
        if optionen['test']:
            return self._test()
        if optionen['einladungslink']:
            return self._einladungslink()
        return self._chat_ids_zeigen()

    def _chat_ids_zeigen(self):
        try:
            webhook = (telegram.api_aufruf('getWebhookInfo').get('result') or {}).get('url')
        except Exception as exc:                                # noqa: BLE001
            # Ohne Webhook-Auskunft geht der Befehl den getUpdates-Weg; schlaegt der
            # ebenfalls fehl, meldet ihn der CommandError unten. Token nie ins Protokoll.
            logger.warning('getWebhookInfo fehlgeschlagen: %s', telegram._ohne_token(exc))
            webhook = ''
        if webhook:
            self.stdout.write(self.style.WARNING(
                'Der Webhook ist gesetzt - getUpdates liefert dann nichts (Telegram '
                'schickt jede Nachricht an die Website). Neue Handys melden sich '
                'ueber den Einladungslink an (--einladungslink); die Liste steht im '
                'Dashboard unter Anfragen. Zurueck zu getUpdates: '
                'telegram_webhook --loeschen.'))
            return
        try:
            ich = telegram.api_aufruf('getMe')
            antwort = telegram.api_aufruf('getUpdates', {'limit': 100})
        except Exception as exc:                                # noqa: BLE001
            raise CommandError(f'Telegram nicht erreichbar: '
                               f'{telegram._ohne_token(exc)}') from None
        bot = (ich.get('result') or {}).get('username', '?')
        self.stdout.write(f'Bot: @{bot}')
        gesehen = {}
        for update in antwort.get('result') or []:
            nachricht = update.get('message') or update.get('my_chat_member') or {}
            chat = nachricht.get('chat') or {}
            if chat.get('id') is None:
                continue
            name = ' '.join(filter(None, (chat.get('first_name'), chat.get('last_name')))) \
                or chat.get('title') or chat.get('username') or '?'
            gesehen[chat['id']] = (name, chat.get('type', ''))
        if not gesehen:
            self.stdout.write(self.style.WARNING(
                'Noch niemand hat dem Bot geschrieben. Im Handy den Bot öffnen, '
                '"/start" senden und den Befehl erneut ausführen. (Telegram hält '
                'Nachrichten an den Bot nur etwa 24 Stunden bereit.)'))
            return
        self.stdout.write('Chats, die dem Bot geschrieben haben:')
        for chat_id, (name, art) in gesehen.items():
            self.stdout.write(f'  {chat_id}   {name} ({art})')
        self.stdout.write('\nDie gewünschte(n) ID(s) kommagetrennt in TELEGRAM_CHAT_IDS eintragen, '
                          'danach: python manage.py telegram_einrichten --test')

    def _einladungslink(self):
        from django.conf import settings
        code = getattr(settings, 'TELEGRAM_EINLADUNG', '')
        if not code:
            raise CommandError('TELEGRAM_EINLADUNG ist nicht gesetzt '
                               '(Wert erzeugen: telegram_webhook --werte).')
        try:
            ich = telegram.api_aufruf('getMe')
        except Exception as exc:                                # noqa: BLE001
            raise CommandError(f'Telegram nicht erreichbar: '
                               f'{telegram._ohne_token(exc)}') from None
        bot = (ich.get('result') or {}).get('username')
        if not bot:
            raise CommandError('getMe nannte keinen Bot-Namen.')
        self.stdout.write(f'https://t.me/{bot}?start={code}')
        self.stdout.write('Nur an das Team geben. Wer den Link oeffnet und "Starten" tippt, '
                          'bekommt jede Anfrage; alle bisherigen Empfaenger werden benachrichtigt.')

    def _test(self):
        if not telegram.chat_ids():
            raise CommandError('Kein Empfaenger - TELEGRAM_CHAT_IDS ist leer und niemand hat '
                               'sich angemeldet.')
        text = ('✅ <b>Testnachricht der Website Rümpelwerk</b>\n\n'
                'Wenn diese Nachricht ankommt, meldet die Website ab jetzt jede '
                'Anfrage hier.\n\n'
                + telegram.nachricht('anfrage', {
                    'name': 'Beispiel (Test)', 'telefon': '0000 000000',
                    'ort': '06110 Halle (Saale)', 'objekt': 'Entrümpelung'}))
        if telegram.senden(text):
            self.stdout.write(self.style.SUCCESS(
                f'Gesendet an {len(telegram.chat_ids())} Empfänger (mindestens einer hat sie bekommen).'))
        else:
            raise CommandError('Senden fehlgeschlagen - Details in der Fehlerwache bzw. im Log. '
                               'Häufig: falsche Chat-ID oder dem Bot wurde noch nie "/start" geschickt.')
