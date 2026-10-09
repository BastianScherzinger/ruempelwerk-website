from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_fix_pagevisit'),
    ]

    operations = [
        migrations.CreateModel(
            name='Kooperationsanfrage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('firma', models.CharField(max_length=200, verbose_name='Firmenname')),
                ('email', models.EmailField(max_length=254, verbose_name='E-Mail')),
                ('telefon', models.CharField(blank=True, max_length=50, verbose_name='Telefon')),
                ('art', models.CharField(
                    choices=[
                        ('subunternehmer', 'Subunternehmer / Nachunternehmer'),
                        ('handwerker', 'Handwerker-Partner'),
                        ('immobilien', 'Immobilienverwaltung / Verwalter'),
                        ('makler', 'Makler / Immobilienmakler'),
                        ('sonstiges', 'Sonstiges'),
                    ],
                    max_length=50,
                    verbose_name='Art der Kooperation',
                )),
                ('nachricht', models.TextField(blank=True, verbose_name='Nachricht')),
                ('erstellt_am', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Kooperationsanfrage',
                'verbose_name_plural': 'Kooperationsanfragen',
                'ordering': ['-erstellt_am'],
            },
        ),
    ]
