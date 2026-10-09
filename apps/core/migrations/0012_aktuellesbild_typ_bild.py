from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_aktuellespost_autor'),
    ]

    operations = [
        migrations.AddField(
            model_name='aktuellesbild',
            name='typ_bild',
            field=models.CharField(
                blank=True, default='', max_length=4,
                choices=[('vor', 'Vorher'), ('nach', 'Nachher')],
                verbose_name='Typ',
            ),
        ),
    ]
