from django.db import migrations


def add_typ_bild_if_missing(apps, schema_editor):
    """Ergaenzt core_aktuellesbild.typ_bild, falls die Spalte fehlt.

    Recovery-Migration fuer den Fall, dass 0012 in der Produktion nicht
    durchlief (siehe 0004 und 0008 fuer dasselbe Muster).

    Die Pruefung laeuft ueber Djangos Introspection statt ueber
    ``information_schema``: Letzteres gibt es nur in PostgreSQL, wodurch
    ``manage.py migrate`` auf einer frischen SQLite-Datei abbrach - also
    genau im lokalen Setup, das settings.py ohne DATABASE_URL vorsieht.
    """
    connection = schema_editor.connection
    table = 'core_aktuellesbild'

    with connection.cursor() as cursor:
        if table not in connection.introspection.table_names(cursor):
            return
        columns = {
            col.name
            for col in connection.introspection.get_table_description(cursor, table)
        }
        if 'typ_bild' in columns:
            return
        cursor.execute(
            f'ALTER TABLE {table} '
            "ADD COLUMN typ_bild varchar(4) NOT NULL DEFAULT ''"
        )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_aktuellesbild_typ_bild'),
    ]

    operations = [
        migrations.RunPython(add_typ_bild_if_missing, migrations.RunPython.noop),
    ]
