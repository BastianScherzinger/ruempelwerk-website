import apps.core.models
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Record the upload_to change from static string 'aktuelles/'
    to the callable _aktuelles_upload_path (UUID-based).
    No database schema change – Django only needs this to silence the warning.
    """

    dependencies = [
        ('core', '0008_fix_visitorsession_constraint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aktuellespost',
            name='bild_vor',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=apps.core.models._aktuelles_upload_path,
                validators=[apps.core.models._validate_image],
                verbose_name='Bild Vorher',
            ),
        ),
        migrations.AlterField(
            model_name='aktuellespost',
            name='bild_nach',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=apps.core.models._aktuelles_upload_path,
                validators=[apps.core.models._validate_image],
                verbose_name='Bild Nachher',
            ),
        ),
    ]
