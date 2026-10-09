"""Loescht das eigene Besuchsprotokoll (``PageVisit``) nach 30 Tagen.

**Warum es diesen Command gibt.** ``apps/core/middleware.py`` legt bei jedem
GET mit Status 200 eine Zeile ``PageVisit`` an: Pfad, gekuerzte IP,
vollstaendiger User-Agent, Zeitstempel. Geloescht wurde davon bis zum
06.09.2026 **nie etwas** - ``send_daily_report()`` raeumt ausschliesslich
``VisitorSession`` nach 90 Tagen auf, ``PageVisit`` kommt dort nicht vor.
Die Datenschutzerklaerung beschrieb bis dahin nur die Server-Logfiles von
Railway ("nach spaetestens 30 Tagen geloescht") und kannte das zweite,
dauerhafte Protokoll der Anwendung gar nicht (Befund A2).

**Die 30 Tage sind keine gegriffene Zahl.** Sie sind dieselbe Frist, die
Abschnitt 3 der Datenschutzerklaerung ohnehin nennt. Wer sie hier aendert,
aendert sie dort mit - das ist Regel 1 in einer anderen Sorte Zahl: eine
Frist hat genau eine Quelle, und die ist ``AUFBEWAHRUNG_TAGE`` hier.

Bedienung wie ``spam_aufraeumen``: ohne Argumente wird nur gezeigt, was
getroffen wuerde; erst ``--loeschen`` raeumt wirklich.

    python manage.py pagevisit_aufraeumen
    python manage.py pagevisit_aufraeumen --loeschen

Im Betrieb ruft ihn der Mitternachtszweig des Schedulers auf
(``apps/core/apps.py``), dort mit ``--loeschen`` und in einem eigenen
try-Block, damit ein Ausfall den Tagesreport nicht mitreisst.
"""

import datetime
import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import PageVisit

logger = logging.getLogger('apps.core')

# Dieselbe Frist, die Abschnitt 3 der Datenschutzerklaerung zusagt.
AUFBEWAHRUNG_TAGE = 30


class Command(BaseCommand):
    """Löscht Besuchsprotokoll-Einträge jenseits der Frist — nur mit ``--loeschen``."""

    help = ('Zeigt (und loescht mit --loeschen) Besuchsprotokoll-Eintraege, '
            f'die aelter als {AUFBEWAHRUNG_TAGE} Tage sind.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--loeschen',
            action='store_true',
            help='Die gefundenen Eintraege wirklich loeschen.',
        )

    def _sag(self, text, stil=None):
        """Ausgabe nur, wenn jemand zusieht.

        Der Scheduler ruft den Command mit ``verbosity=0`` auf. Ohne diese
        Bremse schriebe er jede Nacht drei Zeilen in Railways Logspeicher -
        ausgerechnet dorthin, wo dieser Command gerade aufraeumen soll.
        Die Nachweiszeile am Ende ist davon ausgenommen: Sie geht ueber den
        Logger, nicht ueber stdout.
        """
        if not self._leise:
            self.stdout.write(stil(text) if stil else text)

    def handle(self, *args, **optionen):
        self._leise = not optionen.get('verbosity', 1)
        grenze = timezone.now() - datetime.timedelta(days=AUFBEWAHRUNG_TAGE)
        alt = PageVisit.objects.filter(timestamp__lt=grenze)
        anzahl = alt.count()

        # Der Gesamtbestand wird nur ermittelt, wenn ihn auch jemand liest:
        # ``count()`` ohne Filter ist ein vollstaendiger Tabellendurchlauf und
        # waechst mit der Tabelle. Genau diese Zeile im internen Dashboard ist
        # als P8/E1 beanstandet - sie hier nachts stuendlich nachzubauen waere
        # derselbe Fehler an einer neuen Stelle.
        if not self._leise:
            self._sag(
                f'Besuchsprotokoll: {PageVisit.objects.count()} Zeilen gesamt, '
                f'davon {anzahl} aelter als {AUFBEWAHRUNG_TAGE} Tage '
                f'(vor {grenze:%Y-%m-%d %H:%M}).'
            )

        if not anzahl:
            self._sag('Nichts zu loeschen.', self.style.SUCCESS)
            return

        if not optionen['loeschen']:
            self._sag(
                'Nichts geloescht. Mit --loeschen ausfuehren, wenn die Zahl stimmt.'
            )
            return

        alt.delete()
        # Nachweisbarkeit ist Teil der Loeschpflicht (Art. 5 Abs. 2 DSGVO):
        # ohne Logzeile laesst sich spaeter nicht belegen, dass und wann
        # geloescht wurde.
        logger.info('Besuchsprotokoll aufgeraeumt | %s Zeilen ueber %s Tage',
                    anzahl, AUFBEWAHRUNG_TAGE)
        self._sag(f'{anzahl} Zeilen geloescht.', self.style.SUCCESS)
