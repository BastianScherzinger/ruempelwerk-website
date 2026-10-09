from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_visitorsession_dailystats'),
    ]

    operations = [
        migrations.CreateModel(
            name='AktuellesPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typ', models.CharField(
                    choices=[
                        ('bericht',        'Bericht'),
                        ('zitat',          'Zitat'),
                        ('vorher_nachher', 'Vorher / Nachher'),
                    ],
                    max_length=20,
                    verbose_name='Typ',
                )),
                ('titel',           models.CharField(max_length=300, verbose_name='Titel')),
                ('inhalt',          models.TextField(blank=True, verbose_name='Text / Inhalt')),
                ('zitat_autor',     models.CharField(blank=True, max_length=200, verbose_name='Zitatautor')),
                ('bild_vor',        models.ImageField(blank=True, null=True, upload_to='aktuelles/', verbose_name='Bild Vorher')),
                ('bild_nach',       models.ImageField(blank=True, null=True, upload_to='aktuelles/', verbose_name='Bild Nachher')),
                ('veroeffentlicht', models.BooleanField(default=False, verbose_name='Veröffentlicht')),
                ('datum',           models.DateField(verbose_name='Datum')),
                ('erstellt_am',     models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Aktuelles',
                'verbose_name_plural': 'Aktuelles',
                'ordering': ['-datum', '-erstellt_am'],
            },
        ),
    ]
