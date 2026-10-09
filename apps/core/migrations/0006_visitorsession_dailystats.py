from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_kooperationsanfrage'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisitorSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(db_index=True, max_length=32)),
                ('date', models.DateField(db_index=True)),
                ('ip_hash', models.CharField(blank=True, max_length=40)),
                ('started_at', models.DateTimeField()),
                ('last_seen', models.DateTimeField()),
                ('page_count', models.PositiveIntegerField(default=1)),
            ],
            options={
                'verbose_name': 'Besucher-Session',
                'verbose_name_plural': 'Besucher-Sessions',
                'ordering': ['-date', '-started_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='visitorsession',
            constraint=models.UniqueConstraint(fields=['session_id', 'date'], name='unique_session_per_day'),
        ),
        migrations.CreateModel(
            name='DailyStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('unique_visitors', models.PositiveIntegerField(default=0)),
                ('total_sessions', models.PositiveIntegerField(default=0)),
                ('total_pageviews', models.PositiveIntegerField(default=0)),
                ('avg_session_seconds', models.PositiveIntegerField(default=0)),
                ('email_sent', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Tagesstatistik',
                'verbose_name_plural': 'Tagesstatistiken',
                'ordering': ['-date'],
            },
        ),
    ]
