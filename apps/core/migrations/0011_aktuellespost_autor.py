from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_aktuellesbild'),
    ]

    operations = [
        migrations.AddField(
            model_name='aktuellespost',
            name='autor',
            field=models.CharField(
                blank=True,
                choices=[
                    ('oliver',    'Oliver Pohl'),
                    ('christoph', 'Christoph Regner'),
                    ('viktor',    'Viktor Grebe'),
                ],
                max_length=20,
                verbose_name='Autor',
            ),
        ),
    ]
