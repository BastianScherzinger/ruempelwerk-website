from django.db import migrations


def create_pagevisit_if_missing(apps, schema_editor):
    from django.db import connection
    if 'core_pagevisit' not in connection.introspection.table_names():
        model = apps.get_model('core', 'PageVisit')
        schema_editor.create_model(model)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_preisangebot'),
    ]

    operations = [
        migrations.RunPython(create_pagevisit_if_missing, migrations.RunPython.noop),
    ]
