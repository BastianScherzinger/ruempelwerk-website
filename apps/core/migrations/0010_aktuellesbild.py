import apps.core.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_aktuellespost_upload_path'),
    ]

    operations = [
        migrations.CreateModel(
            name='AktuellesBild',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bild', models.ImageField(upload_to=apps.core.models._aktuelles_upload_path, verbose_name='Bild')),
                ('reihenfolge', models.PositiveSmallIntegerField(default=0)),
                ('post', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='bilder',
                    to='core.aktuellespost',
                )),
            ],
            options={
                'verbose_name': 'Post-Bild',
                'verbose_name_plural': 'Post-Bilder',
                'ordering': ['reihenfolge', 'pk'],
            },
        ),
    ]
