"""Das Auth-Altbestands-Dashboard unter ``/dashboard/``.

⚠ **Diese Seite ist zurzeit nicht erreichbar.** Gemessen am 06.09.2026:
``resolve('/dashboard/')`` landet auf ``apps.core.views.city_landing_page``
mit ``city_slug='dashboard'`` und endet in einem 404. Grund ist Regel 5 – der
City-Catch-All ist das letzte Pattern in ``apps/core/urls.py``, und
``config/urls.py`` bindet ``apps.core.urls`` **vor** ``dashboard/`` ein. Wer
die Seite wieder erreichbar machen will, zieht ihre Zeile in
``config/urls.py`` vor die von ``apps.core.urls`` – das ist eine Aenderung an
einer Datei, die nichts mit dieser hier zu tun hat, und sie gehoert in einen
eigenen Vorgang.

Der Grund, warum die Abfragen hier trotzdem am 06.09.2026 repariert worden
sind (P8/E1, Punkt 3): ``PageVisit.objects.count()`` ohne Filter ist ein
vollstaendiger Tabellendurchlauf, der mit der Tabelle waechst. Eine Seite,
die heute niemand aufrufen kann, wird morgen wieder freigeschaltet – und dann
steht der Fehler unveraendert da, mit einer Tabelle, die inzwischen ein Jahr
alt ist.
"""

import datetime
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils import timezone

from apps.core.models import PageVisit

logger = logging.getLogger('apps.dashboard')

# Derselbe Zeitraum, den ``pagevisit_aufraeumen`` als Aufbewahrungsfrist
# nennt. Laenger zu zaehlen ist sinnlos: Aelteres wird geloescht, die Zahl
# waere also ohnehin dieselbe – nur teurer ermittelt. Kuerzer zu zaehlen
# waere eine zweite, konkurrierende Frist.
_ZEITRAUM_TAGE = 30


@login_required
def index(request):
    """Kennzahlen des Altbestands-Dashboards.

    **Was sich am 06.09.2026 an den Zahlen geaendert hat** – das gehoert in
    denselben Vorgang wie die Aenderung selbst, sonst sieht der Betrieb einen
    Einbruch ohne Erklaerung:

    * ``total_visits`` zaehlte bisher **jede jemals gespeicherte** Zeile,
      Bots eingeschlossen. Jetzt zaehlt es die Aufrufe **ohne Bots** aus den
      letzten 30 Tagen. Beide Aenderungen zusammen machen die Zahl kleiner –
      und zum ersten Mal vergleichbar, weil sie sich auf einen festen
      Zeitraum bezieht statt auf "seit dem letzten Aufsetzen der Datenbank".
    * ``bot_visits`` steht daneben und weist genau das aus, was aus der
      ersten Zahl herausgenommen wurde. Bots verschwinden also nicht, sie
      stehen nur nicht mehr in derselben Spalte wie Menschen.

    **Was diese Zahlen nicht sind:** Sie zaehlen Seitenaufrufe, keine
    Besucher, und die Bot-Erkennung liest den User-Agent, also eine
    Behauptung (siehe Docstring von ``PageVisit``). Die belastbare
    Besucherzahl steht im internen Dashboard unter ``STATS_PATH`` und kommt
    aus ``VisitorSession``/``DailyStats``.
    """
    seit = timezone.now() - datetime.timedelta(days=_ZEITRAUM_TAGE)
    letzte = PageVisit.objects.filter(timestamp__gte=seit)

    context = {
        'total_users': User.objects.count(),
        'zeitraum_tage': _ZEITRAUM_TAGE,
        'total_visits': letzte.filter(ist_bot=False).count(),
        'bot_visits': letzte.filter(ist_bot=True).count(),
        # [:10] ist eine LIMIT-Abfrage, kein Tabellendurchlauf – die
        # Sortierung ``-timestamp`` bedient seit P8/E1 ein Index.
        'recent_visits': PageVisit.objects.all()[:10],
    }
    logger.debug('Dashboard geladen von %s', request.user.username)
    return render(request, 'dashboard/index.html', context)
