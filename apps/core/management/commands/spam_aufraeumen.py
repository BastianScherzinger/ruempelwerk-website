"""Zeigt und loescht die Anfragen, die der Formular-Bot hinterlassen hat.

Bewusst KEIN Automatismus und kein Schritt in start.sh: Ein Filter, der von
selbst Datensaetze loescht, loescht irgendwann den falschen. Der Command zeigt
ohne Argumente nur an, was er treffen wuerde; geloescht wird erst mit
``--loeschen``.

    python manage.py spam_aufraeumen
    python manage.py spam_aufraeumen --loeschen

Die Muster stammen aus ``apps/core/antispam`` und beschreiben den Angriff vom
25.08.2026. Neu eingehender Spam wird von der Abwehr abgefangen, bevor er in
die Datenbank kommt - dieser Command raeumt nur den Altbestand.
"""

from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.core.antispam import BLOCK_MAILS, BLOCK_NAMEN
from apps.core.models import Anfrage, Kooperationsanfrage, PreisAngebot


class Command(BaseCommand):
    """Zeigt den Spam-Altbestand der Formulare; löscht ihn nur mit ``--loeschen``."""

    help = 'Zeigt (und loescht mit --loeschen) Spam-Eintraege des Formular-Bots.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--loeschen',
            action='store_true',
            help='Die gefundenen Eintraege wirklich loeschen.',
        )

    def _treffer(self, model):
        bedingung = Q()
        for name in BLOCK_NAMEN:
            # iexact statt icontains: "Robert Prant" als echter Kunde bliebe
            # damit unangetastet, weil der Bot ohne Leerzeichen schreibt.
            bedingung |= Q(name__iexact=name)
        for mail in BLOCK_MAILS:
            bedingung |= Q(email__iexact=mail)
        return model.objects.filter(bedingung)

    def handle(self, *args, **optionen):
        gesamt = 0

        for model in (Anfrage, Kooperationsanfrage, PreisAngebot):
            treffer = self._treffer(model)
            anzahl = treffer.count()
            gesamt += anzahl

            label = model._meta.verbose_name_plural
            if not anzahl:
                self.stdout.write(f'{label}: nichts gefunden')
                continue

            self.stdout.write(self.style.WARNING(f'{label}: {anzahl} Treffer'))
            for eintrag in treffer[:20]:
                self.stdout.write(
                    f'  {eintrag.erstellt_am:%Y-%m-%d %H:%M} | '
                    f'{eintrag.name} | {eintrag.email}'
                )
            if anzahl > 20:
                self.stdout.write(f'  ... und {anzahl - 20} weitere')

            if optionen['loeschen']:
                treffer.delete()
                self.stdout.write(self.style.SUCCESS(f'  {anzahl} geloescht'))

        if not gesamt:
            self.stdout.write(self.style.SUCCESS('Keine Spam-Eintraege gefunden.'))
        elif not optionen['loeschen']:
            self.stdout.write(
                '\nNichts geloescht. Mit --loeschen ausfuehren, wenn die Liste stimmt.'
            )
