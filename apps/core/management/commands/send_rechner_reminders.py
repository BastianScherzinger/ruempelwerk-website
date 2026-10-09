from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Sendet ausstehende 24h-Erinnerungs-E-Mails für Preisangebote'

    def handle(self, *args, **options):
        from apps.core.views import send_due_reminders
        count = send_due_reminders()
        self.stdout.write(self.style.SUCCESS(f'{count} Erinnerung(en) gesendet'))
