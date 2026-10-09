"""Telegram-Push, Spamverdacht - und die Reparatur des Preisrechners.

Drei Dinge, 24.09.2026:

1. ``push_gesendet`` an allen vier Lead-Modellen (``VersandStatus``). Der
   Altbestand wird einmalig auf ``True`` gesetzt - dieselbe Begruendung wie
   in ``0017``: Ohne diesen Schritt schickte der erste Lauf des
   Push-Nachzueglers jede Anfrage der letzten sieben Tage noch einmal aufs
   Handy.
2. ``Anfrage.verdacht`` (Variante A der Grenzfaelle der Spam-Abwehr).
3. **Der Preisrechner.** Die Produktionsdatenbank trug in
   ``core_preisangebot`` eine Spalte ``ort`` mit NOT NULL, die in keiner
   Migration und keinem Model dieses Projekts steht (vermutlich aus der
   Vorlage, von der das Projekt kopiert wurde). Jeder ``create()`` des
   Rechners endete damit in::

       IntegrityError: null value in column "ort" of relation
       "core_preisangebot" violates not-null constraint

   - belegt im Railway-Log am 01.09., 04.09. (2x), 07.09. (5x), 15.09.,
   16.09., 17.09., 22.09. und 24.09.2026. Bis zum 06.09. startete der
   Mailversand **vor** dem Speichern und kam noch hinaus; seitdem ging jede
   Rechner-Anfrage verloren, und der Kunde sah einen Fehler.

   Deshalb hier zwei Schritte, die beide nur anfassen, was sie vorfinden:

   * ``ort`` wird als Feld eingefuehrt. Existiert die Spalte schon (Produktion),
     bleibt sie, wie sie ist, und das Model beschreibt sie ab jetzt; fehlt sie
     (lokal, Test), wird sie angelegt.
   * Auf PostgreSQL verliert jede **weitere** Spalte der vier Lead-Tabellen,
     die kein Model kennt, ihr NOT NULL - falls ``ort`` nicht die einzige
     Altlast ist. Was geaendert wird, steht im Deploy-Log.

   Der Rueckweg laesst beides stehen: Eine Spalte zu loeschen, die vor dieser
   Migration schon da war, waere Datenverlust.
"""

from django.db import migrations, models


def _altbestand_push_erledigt(apps, schema_editor):
    for name in ('Anfrage', 'PreisAngebot', 'Kooperationsanfrage', 'Bewerbung'):
        apps.get_model('core', name).objects.update(push_gesendet=True)


def _ort_anlegen_wenn_fehlt(apps, schema_editor):
    PreisAngebot = apps.get_model('core', 'PreisAngebot')
    tabelle = PreisAngebot._meta.db_table
    verbindung = schema_editor.connection
    with verbindung.cursor() as cursor:
        spalten = {s.name for s in
                   verbindung.introspection.get_table_description(cursor, tabelle)}
    if 'ort' in spalten:
        print(f'\n  0020: {tabelle}.ort ist schon da - wird uebernommen, nicht angelegt')
        return
    feld = models.CharField(max_length=100, blank=True, default='',
                            verbose_name='Ort (Rechner)')
    feld.contribute_to_class(PreisAngebot, 'ort')
    schema_editor.add_field(PreisAngebot, feld)


def _fremde_pflichtspalten_lockern(apps, schema_editor):
    verbindung = schema_editor.connection
    if verbindung.vendor != 'postgresql':
        return
    qn = schema_editor.quote_name
    for name in ('Anfrage', 'PreisAngebot', 'Kooperationsanfrage', 'Bewerbung'):
        model = apps.get_model('core', name)
        tabelle = model._meta.db_table
        bekannt = {f.column for f in model._meta.concrete_fields}
        with verbindung.cursor() as cursor:
            cursor.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = current_schema() AND table_name = %s "
                "AND is_nullable = 'NO' AND column_default IS NULL",
                [tabelle])
            fremde = [r[0] for r in cursor.fetchall() if r[0] not in bekannt]
            for spalte in fremde:
                cursor.execute(f'ALTER TABLE {qn(tabelle)} '
                               f'ALTER COLUMN {qn(spalte)} DROP NOT NULL')
                print(f'\n  0020: {tabelle}.{spalte} - unbekannte Pflichtspalte, '
                      f'NOT NULL entfernt')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_fehlerereignis'),
    ]

    operations = [
        migrations.AddField(
            model_name='anfrage',
            name='push_gesendet',
            field=models.BooleanField(default=False, verbose_name='Telegram-Push gesendet'),
        ),
        migrations.AddField(
            model_name='preisangebot',
            name='push_gesendet',
            field=models.BooleanField(default=False, verbose_name='Telegram-Push gesendet'),
        ),
        migrations.AddField(
            model_name='kooperationsanfrage',
            name='push_gesendet',
            field=models.BooleanField(default=False, verbose_name='Telegram-Push gesendet'),
        ),
        migrations.AddField(
            model_name='bewerbung',
            name='push_gesendet',
            field=models.BooleanField(default=False, verbose_name='Telegram-Push gesendet'),
        ),
        migrations.RunPython(_altbestand_push_erledigt, migrations.RunPython.noop),
        migrations.AddField(
            model_name='anfrage',
            name='verdacht',
            field=models.BooleanField(
                default=False, verbose_name='Spamverdacht',
                help_text='Grenzfall der Spam-Abwehr: gespeichert, aber ohne Mail und Push.'),
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='preisangebot',
                    name='ort',
                    field=models.CharField(blank=True, default='', max_length=100,
                                           verbose_name='Ort (Rechner)'),
                ),
            ],
            database_operations=[
                migrations.RunPython(_ort_anlegen_wenn_fehlt, migrations.RunPython.noop),
            ],
        ),
        migrations.RunPython(_fremde_pflichtspalten_lockern, migrations.RunPython.noop),
    ]
