"""Besuchsprotokoll: Index auf ``timestamp``, Markierung ``ist_bot`` (P8/E1).

**Warum das eine Migration mit Ansage ist.** ``AddField`` mit ``default=False``
schreibt jede vorhandene Zeile um, und ``AlterField`` mit ``db_index=True``
baut den Index einmal vollstaendig auf. Beides sperrt die Tabelle
``core_pagevisit`` fuer die Dauer der Operation. Auf Railway laeuft
``manage.py migrate`` in ``start.sh`` **vor** dem ersten Request des neuen
Deploys – waehrend der Migration nimmt also noch der alte Container die
Aufrufe entgegen, und dessen ``PageVisit.objects.create()`` wartet dann auf
die Sperre. Das ist der Grund, warum die Zeilenzahl vor dem Deploy notiert
gehoert (Abnahme in P8/E1): Bei einer sehr grossen Tabelle waere ein
``CREATE INDEX CONCURRENTLY`` (``AddIndexConcurrently``, nur Postgres, nur
ausserhalb einer Transaktion) der richtige Weg.

Gemessen am 06.09.2026 spricht nichts dafuer, diesen Aufwand zu treiben: Die
Loeschung nach 30 Tagen aus A2/A3 begrenzt die Tabelle, und der Ausfall
betraefe ausschliesslich das Protokoll – ``PageVisit.objects.create()`` steht
in ``middleware.py`` in einem eigenen ``try``, ein Fehler dort kostet eine
Logzeile und keinen Seitenaufruf.

**Was diese Migration nicht tut:** Sie fuellt ``ist_bot`` fuer den Altbestand
nicht nach. Der User-Agent stuende dafuer zwar in der Tabelle, aber ein
Datenmigrationsschritt, der ``_is_bot()`` aus ``apps.core.middleware``
importiert, verdrahtet eine Migration mit heutigem Anwendungscode – aendert
sich ``_BOT_KEYWORDS``, aendert sich rueckwirkend, was diese Migration getan
haben soll. Alle Zeilen vor dem Deploy stehen deshalb auf ``False``, also als
Mensch. Nach 30 Tagen ist der Altbestand ohnehin geloescht und die Spalte
ueberall echt.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_bewerbung_und_versandstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagevisit',
            name='ist_bot',
            field=models.BooleanField(default=False, verbose_name='Bot (laut User-Agent)'),
        ),
        migrations.AlterField(
            model_name='pagevisit',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
