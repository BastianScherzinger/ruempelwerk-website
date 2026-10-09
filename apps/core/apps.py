"""Die App-Konfiguration - und der einzige Scheduler dieses Projekts.

Es gibt keinen Cron und keinen Worker: Die wiederkehrenden Arbeiten haengen in
einem Hintergrund-Thread, den ``CoreConfig.ready()`` **nur im Serverbetrieb**
startet (nicht bei ``manage.py``-Befehlen, sonst liefe er bei jeder Migration
mit). Stuendlich laufen die Erinnerungen des Preisrechners und der
Mail-Nachzuegler, nachts die beiden Aufraeumer und alle sechs Stunden der
Bewertungsabgleich.

**Unter Windows laeuft der Zweig gar nicht** - er sichert sich mit ``fcntl``
gegen mehrere Gunicorn-Worker ab, und das Modul gibt es dort nicht. Lokal ist
jeder dieser Schritte deshalb nur als ``manage.py``-Befehl zu erreichen.
"""

import sys
from django.apps import AppConfig


def stunde_beanspruchen(jetzt):
    """True, wenn diese volle Stunde noch nicht gelaufen ist - und merkt sie vor.

    EIG86 (24.09.2026): Der Scheduler fuhr nach jedem Start **sofort** den
    Lauf der aktuellen Stunde. Ein Deploy zwischen 00:00 und 00:59 wiederholte
    damit Tagesreport und beide Loeschlaeufe, einer um 06:xx den
    Bewertungsabgleich. Jetzt steht die Stunde im (Datenbank-)Cache;
    ``cache.add`` legt nur an, was fehlt, also gewinnt genau ein Lauf je
    Stunde - auch ueber einen Neustart hinweg. Ohne Cache laeuft er lieber
    einmal zu oft als gar nicht.
    """
    try:
        from django.core.cache import cache
        return cache.add(f'scheduler:lauf:{jetzt:%Y%m%d%H}', 1, timeout=2 * 3600)
    # audit-ok P02: ohne Cache lieber doppelt laufen als gar nicht.
    except Exception:                                           # noqa: BLE001
        return True


def stundenlauf(current_hour, log):
    """Ein Durchgang des Schedulers - jeder Schritt in einem eigenen ``try``.

    Aus der Schleife in :meth:`CoreConfig.ready` herausgezogen (24.09.2026),
    damit er sich ohne Endlosschleife und ohne ``fcntl`` pruefen laesst.
    """
    from django.core.management import call_command

    # Midnight: compile yesterday's stats and send report
    if current_hour == 0:
        try:
            from apps.core.views import send_daily_report
            send_daily_report()
        except Exception as exc:
            log.error(f'Daily-Report Fehler: {exc}')

        # Loeschfristen, seit dem 06.09.2026 (Befund A2/A3).
        #
        # Beide Aufraeumer stehen hier und nicht in start.sh: Sie brauchen
        # eine laufende Django-Umgebung und sollen genau einmal taeglich
        # laufen, nicht bei jedem Deploy.
        #
        # **Je ein eigener try-Block, und alle getrennt vom Report.** Ein
        # Ausfall des Aufraeumers darf den Tagesreport nicht mitreissen - und
        # umgekehrt darf ein Fehler im Report nicht dazu fuehren, dass die
        # zugesagte Loeschung ausfaellt. Genau diese Kopplung war der Grund,
        # warum PageVisit ueberhaupt nie geloescht wurde - und bis zum
        # 24.09.2026 hing die VisitorSession-Loeschung noch immer hinter dem
        # Report (EIG16).
        #
        # ``--loeschen`` ist hier gesetzt: Ohne das Argument zeigen die
        # Commands nur an.
        try:
            call_command('pagevisit_aufraeumen', loeschen=True, verbosity=0)
        except Exception as exc:
            log.error(f'Besuchsprotokoll-Aufraeumer Fehler: {exc}')

        try:
            call_command('leads_aufraeumen', loeschen=True, verbosity=0)
        except Exception as exc:
            log.error(f'Lead-Aufraeumer Fehler: {exc}')

        try:
            from apps.core.views import sitzungen_aufraeumen
            sitzungen_aufraeumen()
        except Exception as exc:
            log.error(f'Sitzungs-Aufraeumer Fehler: {exc}')

        # Spamverdacht (Variante A) nach 30 Tagen - eigene, kurze Frist.
        try:
            from apps.core.views import _verdacht_aufraeumen
            _verdacht_aufraeumen()
        except Exception as exc:
            log.error(f'Verdacht-Aufraeumer Fehler: {exc}')

    # Google-Bewertungen abgleichen - alle 6 Stunden (0, 6, 12, 18).
    # Vorher nur um Mitternacht: Der sichtbare Stand war bis zu 24 Stunden
    # alt (21 auf der Seite, 22 im Profil). Nicht stuendlich: 24 Abrufe
    # taeglich fuer ein paar Bewertungen im Monat waeren bezahlte Leerlaufzeit.
    # Die Places-API erlaubt das Zwischenspeichern hoechstens 30 Tage.
    # Eigener try-Block: Ein Ausfall bei Google darf nichts mitreissen.
    if current_hour % 6 == 0:
        try:
            call_command('sync_google_reviews', verbosity=0)
        except Exception as exc:
            log.error(f'Bewertungs-Abgleich Fehler: {exc}')

    # EIG249 (25.09.2026): Abgelaufene Sperrzaehler der Mengenbegrenzung tragen
    # die volle IP und blieben sonst unbegrenzt in ``rw_cache`` stehen. Stuendlich,
    # damit die Datenschutzerklaerung "nach spaetestens zwei Stunden" halten
    # kann (eine Stunde Laufzeit plus hoechstens eine bis zum naechsten Lauf).
    # Eigener try-Block wie ueberall hier.
    try:
        from apps.core.antispam import abgelaufene_zaehler_loeschen
        abgelaufene_zaehler_loeschen()
    except Exception as exc:
        log.error(f'Cache-Aufraeumer Fehler: {exc}')

    # Hourly: send due reminders
    try:
        from apps.core.views import send_due_reminders
        send_due_reminders()
    except Exception as exc:
        log.error(f'Reminder-Scheduler Fehler: {exc}')

    # Nachzuegler-Versand, seit dem 06.09.2026 (Befund P8/C3). Der
    # Mailversand laeuft in einem ``daemon=True``-Thread, den ein Deploy ohne
    # Aufraeumen abbricht; dieser Durchgang holt nach, was
    # ``mail_gewollt=True`` und ``mail_gesendet=False`` geblieben ist.
    # **Eigener try-Block, wie bei den Aufraeumern.**
    try:
        from apps.core.views import _mail_nachzuegler
        _mail_nachzuegler()
    except Exception as exc:
        log.error(f'Mail-Nachzuegler Fehler: {exc}')

    # Telegram-Push-Nachzuegler (24.09.2026) - getrennt vom Mail-Nachzuegler:
    # Ein Telegram-Ausfall darf keine Mail aufhalten und umgekehrt.
    try:
        from apps.core.views import _push_nachzuegler
        _push_nachzuegler()
    except Exception as exc:
        log.error(f'Push-Nachzuegler Fehler: {exc}')

    # Waechter (24.09.2026): "Mail gewollt, nicht gesendet, > 2 Std." als
    # ERROR (Fehlerwache) und Telegram-Alarm. NACH dem Nachzuegler, damit er
    # nur meldet, was auch der nicht retten konnte.
    try:
        from apps.core.views import _versand_waechter
        _versand_waechter()
    except Exception as exc:
        log.error(f'Versand-Waechter Fehler: {exc}')

    # Fehlerwache (VL19, 16.09.2026): eine Sammelmail ueber neue Fehler,
    # danach Eintraege jenseits der Frist loeschen. Eigener try-Block - und
    # ein Fehler hier wird selbst zu einem Fehlerereignis.
    try:
        from apps.core.fehlerwache import fehler_melden
        fehler_melden()
    except Exception as exc:
        log.error(f'Fehlerwache-Meldung fehlgeschlagen: {exc}')


class CoreConfig(AppConfig):
    """Startet in ``ready()`` den stuendlichen Hintergrund-Thread (siehe Modul)."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'

    def ready(self):
        # Only start the reminder thread in web-server mode.
        # Management commands (migrate, collectstatic, etc.) must not spawn it.
        argv = sys.argv
        if argv and 'manage.py' in argv[0]:
            cmd = argv[1] if len(argv) > 1 else ''
            if cmd not in ('runserver', 'runserver_plus', ''):
                return

        import threading
        import time
        import datetime
        import logging

        from django.utils import timezone

        log = logging.getLogger('apps.core')

        # Telegram-Push: eine Zeile beim Start genuegt - ohne Konfiguration
        # ist er still aus, nicht fehlerhaft.
        from . import telegram
        if telegram.aktiv():
            log.info('Telegram-Push: an (%d Empfaenger)', len(telegram.chat_ids()))
        else:
            log.info('Telegram-Push: aus (TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_IDS '
                     'nicht gesetzt)')

        def _sleep_until_next_hour():
            """Sleep until the start of the next clock hour (+10s buffer)."""
            # Ortszeit aus settings.TIME_ZONE, nicht die Uhr des Containers (UTC).
            now = timezone.localtime()
            next_hour = (now + datetime.timedelta(hours=1)).replace(
                minute=0, second=10, microsecond=0,
            )
            seconds = (next_hour - now).total_seconds()
            time.sleep(max(30, seconds))

        def _reminder_loop():
            time.sleep(30)          # Let Django fully initialize first

            # Use an exclusive file lock so only one gunicorn worker runs the loop.
            # fcntl.flock is atomic and automatically released when the process dies.
            # This is more reliable than pg_try_advisory_lock when using a
            # transaction-mode connection pooler (e.g. Supabase Supavisor).
            #
            # Ohne ``fcntl`` (Windows) endet der Thread hier geordnet (FO01,
            # 18.09.2026). Vorher brach er mit ``ModuleNotFoundError`` ab, und
            # der Traceback stand 30 s nach dem Start des lokalen Servers in
            # dessen Ausgabe - mitten in jeder Formularprobe, die ihn als
            # Serverfehler des Formulars las.
            try:
                import fcntl
            except ImportError:
                log.info('Scheduler: kein fcntl (Windows) - laeuft hier nicht, '
                         'die Schritte gibt es als manage.py-Befehle')
                return
            _LOCK_PATH = '/tmp/rw_scheduler.lock'
            try:
                lock_fh = open(_LOCK_PATH, 'w')
                fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (OSError, IOError):
                log.info('Reminder-Scheduler: anderer Worker hält Lock – dieser Worker überspringt')
                return
            # Keep lock_fh alive (don't close) to hold the lock for the loop lifetime

            log.info('Scheduler gestartet (stuendlich Erinnerungen, 6-stuendlich Bewertungen, Mitternacht Report)')
            while True:
                # Europe/Berlin (P11, 17.09.2026): Mit der Containeruhr lief der
                # "Mitternachts"-Bericht um 02:00 Ortszeit.
                jetzt = timezone.localtime()
                if stunde_beanspruchen(jetzt):
                    stundenlauf(jetzt.hour, log)
                else:
                    log.info('Scheduler: diese Stunde lief schon (Neustart) - '
                             'naechster Lauf zur vollen Stunde')
                _sleep_until_next_hour()

        t = threading.Thread(target=_reminder_loop, daemon=True, name='rechner-reminders')
        t.start()
