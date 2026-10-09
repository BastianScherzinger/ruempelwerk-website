# -*- coding: utf-8 -*-
"""Die Google-Bewertungen einmal abgleichen.

    python manage.py sync_google_reviews            # abgleichen
    python manage.py sync_google_reviews --zeigen   # nur anzeigen, nichts holen
    python manage.py sync_google_reviews --trocken  # holen, aber nichts speichern

Laeuft naechtlich aus ``apps/core/apps.py``. Der Command ist der Weg fuer
lokale Tests, weil der Scheduler unter Windows wegen ``fcntl`` nicht anlaeuft.

**Der Command bricht nie hart ab.** Fehlt der Schluessel oder antwortet Google
nicht, bleibt der letzte bekannte Stand stehen und es gibt Exitcode 0 mit einer
Meldung. Ein fehlgeschlagener Abgleich ist kein Grund, ein Deployment zu
stoppen – ``start.sh`` ruft ihn deshalb gar nicht erst auf.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.core import google_reviews as gr
from apps.core.data import reviews as statisch
from apps.core.models import GoogleBewertung, GoogleRezension


class Command(BaseCommand):
    """Holt Schnitt, Anzahl und Rezensionen aus dem Google-Profil (P13).

    Ohne ``GOOGLE_PLACES_API_KEY`` bleibt der Bestand aus ``data/reviews.py``
    stehen; ``--trocken`` zeigt nur, was sich aendern wuerde, ``--zeigen``
    geht gar nicht ins Netz.
    """

    help = 'Gleicht Bewertungsschnitt, Anzahl und Rezensionen mit Google ab.'

    def add_arguments(self, parser):
        parser.add_argument('--trocken', action='store_true',
                            help='Abrufen und anzeigen, aber nichts speichern.')
        parser.add_argument('--zeigen', action='store_true',
                            help='Nur den gespeicherten Stand ausgeben.')

    # ── Ausgabe ─────────────────────────────────────────────────────────────

    def _stand_zeigen(self):
        stand = GoogleBewertung.objects.first()
        if stand:
            self.stdout.write(
                f'Gesamtstand: {stand.wert_txt} bei {stand.anzahl} Bewertungen '
                f'(abgeglichen {timezone.localtime(stand.geprueft_am):%d.%m.%Y %H:%M})'
            )
            if stand.place_id:
                self.stdout.write(f'Place-ID:    {stand.place_id}')
        else:
            self.stdout.write(self.style.WARNING(
                'Noch kein Stand in der Datenbank – es gilt die statische Liste '
                'aus apps/core/data/reviews.py.'))

        anzahl = GoogleRezension.objects.count()
        sichtbar = GoogleRezension.objects.filter(sichtbar=True).count()
        self.stdout.write(f'Rezensionen: {anzahl} gespeichert, {sichtbar} sichtbar')
        for r in GoogleRezension.objects.all():
            marke = ' ' if r.sichtbar else '×'
            quelle = 'übernommen' if r.quelle_id.startswith('uebernommen:') else 'Google'
            self.stdout.write(
                f'  [{marke}] {r.sterne}★ {r.name:<22} {quelle:<11} {r.relativ}')

    # ── Grundbestand ────────────────────────────────────────────────────────

    def _grundbestand_anlegen(self):
        """Die von Hand uebernommenen Rezensionen in die Datenbank spiegeln.

        Muss **vor** dem ersten Abgleich passieren, sonst haette die Datenbank
        hinterher nur die fuenf Rezensionen, die die API hoechstens liefert –
        die sechste waere weg. Danach findet der Abgleich sie ueber den Namen
        wieder und ergaenzt die echte Google-Kennung.
        """
        if GoogleRezension.objects.exists():
            return 0
        jetzt = timezone.now()
        neu = []
        for r in statisch.REZENSIONEN:
            neu.append(GoogleRezension(
                quelle_id='uebernommen:' + gr.namensschluessel(r['name']),
                name=r['name'],
                initialen=r.get('initialen') or gr.initialen(r['name']),
                sterne=r['sterne'],
                text=r['text'],
                zuletzt_gesehen=jetzt,
            ))
        GoogleRezension.objects.bulk_create(neu)
        return len(neu)

    # ── Abgleich ────────────────────────────────────────────────────────────

    def _place_id_bestimmen(self, stand):
        aus_settings = (getattr(settings, 'GOOGLE_PLACE_ID', '') or '').strip()
        if aus_settings:
            return aus_settings
        if stand and stand.place_id:
            return stand.place_id
        suchtext = getattr(settings, 'GOOGLE_PLACE_QUERY', '') or ''
        place_id, name = gr.place_id_suchen(suchtext)
        self.stdout.write(self.style.SUCCESS(
            f'Place-ID gefunden: {place_id}  ({name})'))
        return place_id

    def _rezension_speichern(self, roh, jetzt):
        """Zusammenfuehren, nie ersetzen. Gibt 'neu' oder 'aktualisiert' zurueck."""
        vorhanden = GoogleRezension.objects.filter(quelle_id=roh['quelle_id']).first()
        if vorhanden is None:
            # Ueber den Namen suchen – so findet der erste Abgleich die von Hand
            # uebernommenen Rezensionen wieder, statt sie zu verdoppeln.
            schluessel = gr.namensschluessel(roh['name'])
            for kandidat in GoogleRezension.objects.all():
                if gr.namensschluessel(kandidat.name) == schluessel:
                    vorhanden = kandidat
                    break

        veroeffentlicht = parse_datetime(roh['veroeffentlicht']) if roh['veroeffentlicht'] else None
        felder = {
            'quelle_id': roh['quelle_id'],
            'name': roh['name'],
            'initialen': roh['initialen'],
            'sterne': roh['sterne'],
            'text': roh['text'],
            'profil_url': roh['profil_url'],
            'relativ': roh['relativ'],
            'veroeffentlicht': veroeffentlicht,
            'zuletzt_gesehen': jetzt,
        }
        if vorhanden is None:
            GoogleRezension.objects.create(**felder)
            return 'neu'
        for k, v in felder.items():
            setattr(vorhanden, k, v)
        vorhanden.save()
        return 'aktualisiert'

    # ── Einstieg ────────────────────────────────────────────────────────────

    def _speichern(self, daten, rohe, place_id):
        """Grundbestand, Rezensionen und Gesamtstand in **einer** Transaktion.

        Aus ``handle`` herausgezogen (P08, 24.09.2026), Verhalten unveraendert.
        Rueckgabe: (angelegter Grundbestand, {'neu': n, 'aktualisiert': m}).
        """
        jetzt = timezone.now()
        with transaction.atomic():
            gesetzt = self._grundbestand_anlegen()
            zaehler = {'neu': 0, 'aktualisiert': 0}
            for r in rohe:
                zaehler[self._rezension_speichern(r, jetzt)] += 1

            GoogleBewertung.objects.update_or_create(
                singleton=True,
                defaults={
                    'wert': round(float(daten.get('rating')), 1),
                    'anzahl': int(daten.get('userRatingCount')),
                    'place_id': place_id,
                    'profil_url': daten.get('googleMapsUri', '') or '',
                    'geprueft_am': jetzt,
                },
            )
        return gesetzt, zaehler

    def handle(self, *args, **opt):
        if opt['zeigen']:
            self._stand_zeigen()
            return

        if not gr.api_key():
            self.stdout.write(self.style.WARNING(
                'GOOGLE_PLACES_API_KEY ist nicht gesetzt – kein Abgleich.\n'
                'Es gilt weiter die statische Liste aus apps/core/data/reviews.py.'))
            return

        stand = GoogleBewertung.objects.first()
        try:
            place_id = self._place_id_bestimmen(stand)
            daten = gr.details_holen(place_id)
        except gr.GoogleFehler as exc:
            # Bewusst kein CommandError: Der letzte bekannte Stand bleibt gueltig,
            # und ein Abrufproblem bei Google ist kein Fehler dieser Anwendung.
            self.stderr.write(self.style.ERROR(f'Abgleich fehlgeschlagen: {exc}'))
            self.stdout.write('Der bisherige Stand bleibt unveraendert.')
            return

        wert = daten.get('rating')
        anzahl = daten.get('userRatingCount')
        rohe = [gr.rezension_aufbereiten(r) for r in (daten.get('reviews') or [])]
        rohe = [r for r in rohe if r['text'] and r['name'] and r['sterne']]

        self.stdout.write(f'Google meldet: {wert} bei {anzahl} Bewertungen, '
                          f'{len(rohe)} Rezensionen mit Text (API-Grenze: 5)')

        if opt['trocken']:
            for r in rohe:
                self.stdout.write(f'  {r["sterne"]}★ {r["name"]} – {r["text"][:70]}…')
            self.stdout.write(self.style.WARNING('Trockenlauf – nichts gespeichert.'))
            return

        if wert is None or not anzahl:
            self.stderr.write(self.style.ERROR(
                'Antwort ohne rating/userRatingCount – nichts gespeichert.'))
            return

        gesetzt, zaehler = self._speichern(daten, rohe, place_id)
        if gesetzt:
            self.stdout.write(f'Grundbestand angelegt: {gesetzt} übernommene Rezensionen')
        self.stdout.write(self.style.SUCCESS(
            f'Abgeglichen: {zaehler["neu"]} neu, {zaehler["aktualisiert"]} aktualisiert, '
            f'Gesamtstand {float(wert):.1f} bei {anzahl}'))
