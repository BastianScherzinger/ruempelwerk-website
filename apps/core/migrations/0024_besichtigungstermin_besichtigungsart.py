"""Besichtigungsart am Besichtigungstermin: vor Ort oder per WhatsApp-Video (01.10.2026).

Ein Feld an der EIGENEN Tabelle ``core_besichtigungstermin`` (laut 0022 nicht von
der RTC-Seite mitgenutzt). ``default`` fuellt alte Zeilen; ``db_default`` (Django 5) setzt den Wert in der
Datenbank - ein alter Container im Rolling-Deploy schreibt INSERTs ohne diese
Spalte, und die NOT-NULL-Spalte braucht dafuer einen DB-Default.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_gbp_aktuelles_quelle'),
    ]

    operations = [
        migrations.AddField(
            model_name='besichtigungstermin',
            name='besichtigungsart',
            field=models.CharField(
                choices=[('vor_ort', 'Vor Ort'), ('video', 'Per WhatsApp-Video')],
                default='vor_ort', db_default='vor_ort', max_length=10,
                verbose_name='Art der Besichtigung'),
        ),
    ]
