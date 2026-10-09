from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Reconcile VisitorSession unique_together → UniqueConstraint.
    Migration 0006 added the constraint via AddConstraint. This migration
    removes the unique_together alias so Django's autodetector stays clean.
    The database schema is unchanged (constraint already exists).
    """

    dependencies = [
        ('core', '0007_aktuellespost'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='visitorsession',
            unique_together=set(),
        ),
    ]
