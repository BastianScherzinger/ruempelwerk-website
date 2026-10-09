"""Minifiziert die CSS-Quelldateien – gedacht als Deploy-Schritt vor collectstatic.

Warum nicht im Static-Storage? Django liest beim Hashen aus dem QUELL-Storage.
Eine Minifizierung, die erst in STATIC_ROOT eingreift, landet deshalb nicht in
der ausgelieferten `<name>.<hash>.css` – nachgemessen: die gehashte Datei blieb
unveraendert gross. Deshalb hier, VOR collectstatic.

Der Aufruf steht in `start.sh`. Auf Railway ist das Repo im Container eine
Wegwerfkopie – die lesbare Fassung im Git bleibt unangetastet. Lokal daher
normalerweise NICHT ausfuehren; mit --dry-run kann man die Ersparnis prüfen.
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

try:
    from rcssmin import cssmin
except ImportError:  # pragma: no cover
    cssmin = None


class Command(BaseCommand):
    """Verkleinert die CSS-Dateien beim Deploy; lokal nur mit ``--dry-run`` aufrufen."""

    help = 'Minifiziert alle .css unter STATICFILES_DIRS (in-place).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Nur berichten, nichts schreiben.',
        )

    def handle(self, *args, **options):
        if cssmin is None:
            # Kein harter Fehler: ein fehlender Minifier darf das Deployment
            # nicht aufhalten, die Seite funktioniert auch unminifiziert.
            self.stdout.write(self.style.WARNING(
                'rcssmin nicht installiert – CSS-Minifizierung uebersprungen.'
            ))
            return

        dry = options['dry_run']
        dirs = [Path(d) for d in getattr(settings, 'STATICFILES_DIRS', [])]
        total_before = total_after = 0
        touched = 0

        for base in dirs:
            if not base.is_dir():
                continue
            for path in sorted(base.rglob('*.css')):
                if path.name.endswith('.min.css'):
                    continue
                original = path.read_text(encoding='utf-8')
                minified = cssmin(original)
                # Nur uebernehmen, wenn wirklich kleiner – schuetzt davor,
                # bei einem Minifier-Fehler Unsinn zu schreiben.
                if not minified or len(minified) >= len(original):
                    continue
                total_before += len(original)
                total_after += len(minified)
                touched += 1
                if not dry:
                    path.write_text(minified, encoding='utf-8')
                self.stdout.write(
                    f'  {path.name}: {len(original)/1024:.1f} KiB -> '
                    f'{len(minified)/1024:.1f} KiB'
                )

        if not touched:
            self.stdout.write('Keine CSS-Datei veraendert.')
            return

        saved = (total_before - total_after) / 1024
        verb = 'wuerde sparen' if dry else 'gespart'
        self.stdout.write(self.style.SUCCESS(
            f'{touched} Datei(en), {saved:.1f} KiB {verb}.'
        ))
