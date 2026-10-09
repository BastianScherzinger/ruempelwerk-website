"""Die vier Lead-Modelle als eine Liste - fuer Dashboard, Tagesreport und Waechter.

Seit 24.09.2026 (Paket 1). Vorher kannte das Dashboard unter ``STATS_PATH``
die Anfragen gar nicht, und der Tagesreport nannte nur Besucherzahlen. Wer
wissen wollte, ob Anfragen ankommen, musste in die Django-Verwaltung - und
dass der Preisrechner zwei Wochen lang jede Einsendung verlor, sah niemand.

Diese Datei rechnet nur; sie verschickt nichts und aendert nichts.

WAS SIE NICHT LEISTET: Sie zaehlt, was gespeichert ist. Eine Einsendung, die
schon beim Speichern scheiterte (wie der Rechner bis 24.09.2026), steht in
keiner Zahl - dafuer gibt es den Notfallversand in ``views._lead_speichern``
und die Fehlerwache.
"""

import datetime

from django.utils import timezone


def modelle():
    """``(schluessel, Anzeige, Model)`` - in der Reihenfolge des Dashboards."""
    from .models import (
        Anfrage, Besichtigungstermin, Bewerbung, Kooperationsanfrage,
        PreisAngebot,
    )
    return (
        ('anfrage', 'Anfrage', Anfrage),
        ('rechner', 'Preisrechner', PreisAngebot),
        ('kooperation', 'Kooperation', Kooperationsanfrage),
        ('bewerbung', 'Bewerbung', Bewerbung),
        # Terminbuchung (Bauplan §5): dieselbe Liste unter STATS_PATH/anfragen/
        # zeigt jetzt auch Besichtigungstermine, ohne eigenen Code - genau der
        # Grund, warum diese Datei eine Liste von Modellen ist statt vier
        # Einzelaufrufen.
        ('termin', 'Besichtigungstermin', Besichtigungstermin),
    )


def offen_nicht_zugestellt():
    """Datensaetze, fuer die eine Mail vorgesehen war, die nie hinausging."""
    return sum(m.objects.filter(mail_gewollt=True, mail_gesendet=False).count()
               for _, _, m in modelle())


def zahlen_fuer_tag(tag):
    """Die Zahlen fuer den Tagesreport - ``tag`` ist ein Datum in Ortszeit."""
    from .models import Anfrage
    start = timezone.make_aware(datetime.datetime.combine(tag, datetime.time.min))
    zeitraum = {'erstellt_am__gte': start,
                'erstellt_am__lt': start + datetime.timedelta(days=1)}
    zahlen = {}
    for schluessel, _, model in modelle():
        qs = model.objects.filter(**zeitraum)
        if model is Anfrage:
            zahlen['verdacht'] = qs.filter(verdacht=True).count()
            qs = qs.filter(verdacht=False)
        zahlen[{'anfrage': 'anfragen', 'bewerbung': 'bewerbungen'}.get(
            schluessel, schluessel)] = qs.count()
    zahlen['offen'] = offen_nicht_zugestellt()
    return zahlen


def liste(tage=60):
    """Alle Leads der letzten ``tage`` Tage, neueste zuerst, als einfache dicts."""
    grenze = timezone.now() - datetime.timedelta(days=tage)
    eintraege = []
    for schluessel, anzeige, model in modelle():
        for obj in model.objects.filter(erstellt_am__gte=grenze):
            eintraege.append(_eintrag(schluessel, anzeige, obj))
    eintraege.sort(key=lambda e: e['erstellt_am'], reverse=True)
    return eintraege


def _eintrag(schluessel, anzeige, obj):
    details, ort = '', ''
    if schluessel == 'anfrage':
        details = obj.get_leistung_display()
        ort = obj.adresse
    elif schluessel == 'rechner':
        details = f'{obj.leistung_label}, {obj.groesse_label} · {obj.pmin} €'
        ort = obj.ort
    elif schluessel == 'kooperation':
        details = f'{obj.firma} · {obj.get_art_display()}'
    elif schluessel == 'bewerbung':
        details = obj.stelle_anzeige()
    elif schluessel == 'termin':
        details = (f'{obj.get_besichtigungsart_display()} · '
                   f'{obj.get_objektart_display()} · '
                   f'{timezone.localtime(obj.beginn):%d.%m.%Y %H:%M} Uhr · '
                   f'{obj.get_status_display()}')
        ort = obj.adresse
    verdacht = bool(getattr(obj, 'verdacht', False))
    return {
        'art': schluessel,
        'art_anzeige': anzeige,
        'pk': obj.pk,
        'erstellt_am': obj.erstellt_am,
        'name': obj.name,
        'email': obj.email,
        'telefon': getattr(obj, 'telefon', ''),
        'ort': ort,
        'details': details,
        'text': getattr(obj, 'zusatz_info', '') or getattr(obj, 'nachricht', '')
                or getattr(obj, 'hinweis', ''),
        'verdacht': verdacht,
        'mail_gewollt': obj.mail_gewollt,
        'mail_gesendet': obj.mail_gesendet,
        'push_gesendet': obj.push_gesendet,
        # Rot im Dashboard: gewollt, aber nicht rausgegangen.
        'nicht_zugestellt': obj.mail_gewollt and not obj.mail_gesendet,
    }
