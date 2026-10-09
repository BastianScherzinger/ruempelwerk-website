"""Loescht Formulardaten nach zwei Jahren - die Frist, die die Seite zusagt.

**Warum es diesen Command gibt.** ``templates/datenschutz.html``, Abschnitt 4
"Kontaktformular", sagt seit jeher zu: *"Sie werden geloescht, sobald sie fuer
den Zweck ihrer Erhebung nicht mehr erforderlich sind, spaetestens jedoch nach
2 Jahren."* Im ganzen Repository gab es bis zum 06.09.2026 keine Stelle, die
``Anfrage``, ``PreisAngebot`` oder ``Kooperationsanfrage`` jemals geloescht
haette (Befund A3). Die Zusage wurde also nicht gebrochen, weil jemand sie
missachtet haette, sondern weil **niemand sie eingebaut hat**.

**Warum es noch nicht aufgefallen ist:** Die Seite ist juenger als zwei Jahre.
Der erste Verstoss tritt von selbst ein, ohne dass jemand etwas tut - und dann
schweigend.

**730 Tage, nicht "ungefaehr zwei Jahre".** Die Zahl hier und die Zahl im Text
der Datenschutzerklaerung muessen dieselbe sein; steht dort "2 Jahre" und hier
900 Tage, ist die Zusage falsch, ohne dass irgendein Werkzeug es meldet.

Bedienung wie ``spam_aufraeumen``: ohne Argumente wird nur gezeigt, was
getroffen wuerde; erst ``--loeschen`` raeumt wirklich.

    python manage.py leads_aufraeumen
    python manage.py leads_aufraeumen --loeschen

Im Betrieb ruft ihn der Mitternachtszweig des Schedulers auf
(``apps/core/apps.py``), mit ``--loeschen`` und in einem eigenen try-Block.

**Was dieser Command nicht entscheidet.** Ob zwei Jahre die richtige Frist
sind. Bei einem Handwerksbetrieb koennen steuerliche Aufbewahrungspflichten
fuer *abgeschlossene Auftraege* dagegenstehen; das gehoert vom Betrieb
entschieden (P8, F1). Bis dahin gilt die Zahl, die auf der Seite steht - eine
Frist, die laenger laeuft als die Zusage, ist der schlechtere Fehler.
"""

import datetime
import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import (
    Anfrage, Besichtigungstermin, Bewerbung, Kooperationsanfrage, PreisAngebot,
)

logger = logging.getLogger('apps.core')

# Dieselbe Frist, die Abschnitt 4 der Datenschutzerklaerung zusagt: 2 Jahre.
AUFBEWAHRUNG_TAGE = 730

# Bewerbungen sind KEIN Fall fuer die Zwei-Jahres-Frist. Abschnitt 5 der
# Datenschutzerklaerung sagt fuer sie **sechs Monate** nach Abschluss des
# Verfahrens zu - Par. 26 Abs. 1 BDSG, und die sechs Monate kommen aus der
# Klagefrist des Par. 15 AGG.
#
# 180 statt 183 Tage, und gerechnet ab ``erstellt_am`` statt ab "Abschluss des
# Verfahrens": beides bewusst die sichere Richtung. Frueher zu loeschen bricht
# die Zusage nie, spaeter schon - und wann ein Verfahren abgeschlossen ist,
# weiss dieses Repository nicht.
BEWERBUNG_TAGE = 180

# Terminanfragen (Bauplan §5, Migration 0022): dieselbe Zwei-Jahres-Frist wie
# eine gewoehnliche Anfrage - eine Besichtigungsbuchung ist inhaltlich eine
# Anfrage mit Datum, keine eigene Kategorie mit eigener gesetzlicher
# Grundlage wie Bewerbungen (Par. 26 BDSG). Eine eigene Konstante, damit eine
# kuenftige Entscheidung des Betriebs (z. B. kuerzere Frist nach dem
# Besichtigungstermin) hier an EINER Stelle geaendert wird, nicht an der
# Anfrage-Frist mit.
BESICHTIGUNG_TAGE = 730

# Jedes Modell mit seiner eigenen Frist. Die Liste steht hier und nicht in der
# Schleife, damit ein neues Formularmodell an genau einer Stelle nachgetragen
# wird - ein vergessenes Modell faellt sonst niemandem auf, weil der Lauf
# trotzdem gruen ist. Genau das ist am 06.09.2026 beinahe passiert: ``Bewerbung``
# entstand mit P8/C2, waehrend dieser Command schon geschrieben war, und die
# Sechs-Monats-Zusage haette wieder nur im Text gestanden - der Befund A3, den
# dieser Command gerade behebt.
MODELLE = ((Anfrage, AUFBEWAHRUNG_TAGE),
           (PreisAngebot, AUFBEWAHRUNG_TAGE),
           (Kooperationsanfrage, AUFBEWAHRUNG_TAGE),
           (Bewerbung, BEWERBUNG_TAGE),
           (Besichtigungstermin, BESICHTIGUNG_TAGE))

# **Geteilte Tabellen (02.10.2026).** ``core_anfrage``, ``core_preisangebot`` und
# ``core_pagevisit`` benutzt auch RTC-Service (gleiche Datenbank, gleiches
# App-Label). Ein ungefiltertes ``filter(erstellt_am__lt=...).delete()`` loescht
# dort also auch fremde Zeilen. Wo es ein sicheres Merkmal gibt, steht es hier:
#
# * ``Anfrage``: RTC schreibt nur seine eigenen Leistungsschluessel (klima,
#   elektro, ...); Ruempelwerk nur die aus ``Anfrage.LEISTUNG_CHOICES``. Wir
#   loeschen ausschliesslich Zeilen mit einem **eigenen** Schluessel - eine
#   spaeter bei RTC hinzukommende Leistung wird nie getroffen. (``sanierung``
#   und ``sonstiges`` benutzen beide Seiten; diese Zeilen trifft die Frist
#   bei beiden gleichzeitig, siehe ``docs/fallen.md``.)
# * ``PreisAngebot``: **kein** trennendes Merkmal ohne Migration - bleibt
#   ungefiltert, solange RTC dieselbe Frist (730 Tage) benutzt.
#   ``docs/fallen.md``, "Geteilte Tabellen mit RTC-Service".
EIGENE_ZEILEN = {
    Anfrage: {'leistung__in': [schluessel for schluessel, _ in Anfrage.LEISTUNG_CHOICES]},
}


class Command(BaseCommand):
    """Löscht Formulardaten jenseits der Aufbewahrungsfrist — nur mit ``--loeschen``."""

    help = ('Zeigt (und loescht mit --loeschen) Formulardaten, die aelter als '
            f'{AUFBEWAHRUNG_TAGE} Tage sind (Bewerbungen: {BEWERBUNG_TAGE}).')

    def add_arguments(self, parser):
        parser.add_argument(
            '--loeschen',
            action='store_true',
            help='Die gefundenen Datensaetze wirklich loeschen.',
        )

    def _sag(self, text, stil=None):
        """Ausgabe nur, wenn jemand zusieht.

        Der Scheduler ruft den Command mit ``verbosity=0`` auf. Ohne diese
        Bremse stuenden die Bestandszahlen jede Nacht in Railways Logspeicher.
        Die Nachweiszeile am Ende geht ueber den Logger und bleibt davon
        unberuehrt - sie ist Pflicht, die Bestandsliste ist Bequemlichkeit.
        """
        if not self._leise:
            self.stdout.write(stil(text) if stil else text)

    def handle(self, *args, **optionen):
        self._leise = not optionen.get('verbosity', 1)
        jetzt = timezone.now()
        self._sag(
            f'Grenzen: Formularanfragen aelter als {AUFBEWAHRUNG_TAGE} Tage, '
            f'Bewerbungen aelter als {BEWERBUNG_TAGE} Tage.'
        )

        gesamt = 0
        je_modell = []

        for model, tage in MODELLE:
            grenze = jetzt - datetime.timedelta(days=tage)
            alt = model.objects.filter(erstellt_am__lt=grenze,
                                       **EIGENE_ZEILEN.get(model, {}))
            anzahl = alt.count()
            gesamt += anzahl
            label = model._meta.verbose_name_plural

            # Der Gesamtbestand nur, wenn jemand zusieht: ein ungefiltertes
            # count() ist ein vollstaendiger Tabellendurchlauf (vgl. P8/E1).
            if not self._leise:
                self._sag(f'{label}: {anzahl} zu loeschen, aelter als '
                          f'{grenze:%Y-%m-%d} ({tage} Tage) '
                          f'(Bestand {model.objects.count()})')

            if anzahl and optionen['loeschen']:
                alt.delete()
                je_modell.append(f'{model.__name__}={anzahl}')
                self._sag(f'  {anzahl} geloescht', self.style.SUCCESS)

        if not gesamt:
            self._sag('Nichts zu loeschen.', self.style.SUCCESS)
            return

        if not optionen['loeschen']:
            self._sag(
                '\nNichts geloescht. Mit --loeschen ausfuehren, wenn die Zahlen stimmen.'
            )
            return

        # Bei personenbezogenen Loeschungen ist die Nachweisbarkeit Teil der
        # Pflicht (Art. 5 Abs. 2 DSGVO). Deshalb je Lauf eine Zeile mit der
        # Zahl je Modell - und bewusst ohne Namen oder Mailadressen: der
        # Zweck ist "es wurde geloescht", nicht "wessen Daten".
        logger.info('Formulardaten aufgeraeumt | %s | gesamt=%s | '
                    'Fristen=%s/%s Tage',
                    ', '.join(je_modell), gesamt,
                    AUFBEWAHRUNG_TAGE, BEWERBUNG_TAGE)
        self._sag(f'Insgesamt {gesamt} geloescht.', self.style.SUCCESS)
