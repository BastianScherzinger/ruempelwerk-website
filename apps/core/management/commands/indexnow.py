# -*- coding: utf-8 -*-
"""URLs per IndexNow bei Bing, Yandex und Seznam melden.

**Warum das hier steht, obwohl es die Search Console gibt:** Google hat den
Sitemap-Ping (``/ping?sitemap=…``) im Juni 2023 abgeschaltet; eine Sitemap
laesst sich dort nur noch von Hand im Browser einreichen. IndexNow ist der
einzige Weg, der ohne angemeldete Sitzung funktioniert - und er bedient Bing.
Das ist nicht nur Bing: Bings Index speist die Websuche von ChatGPT, und damit
haengt an dieser Meldung ein GEO-Kanal, kein bloss zweitrangiger Suchdienst.

**Google wird davon nicht bedient.** Wer die Ausgabe dieses Commands liest,
darf daraus nicht schliessen, dass Google die Seiten kennt. Dafuer bleibt der
Gang in die Search Console noetig (siehe seo-geo-plan/STAND.md).

Die URL-Liste kommt aus denselben Sitemap-Klassen wie ``/sitemap-*.xml`` -
eine zweite Liste hier waere die naechste Quelle, die auseinanderlaeuft.

    python manage.py indexnow --trocken     # zeigen, was gemeldet wuerde
    python manage.py indexnow               # melden
    python manage.py indexnow --nur services
"""
import json
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.sitemaps import _canonical_domain, _PRODUCTION_DOMAIN

# Der Endpunkt verteilt die Meldung an alle teilnehmenden Suchdienste
# (Bing, Yandex, Seznam, Naver). Einer reicht - mehrere anzusprechen ist
# ausdruecklich nicht noetig und gilt als Mehrfachmeldung.
_ENDPUNKT = 'https://api.indexnow.org/indexnow'

# Cloudflare vor api.indexnow.org antwortet ohne User-Agent mit 1010 - dieselbe
# Falle wie bei der Resend-API.
_UA = 'Ruempelwerk-Website/1.0'


class Command(BaseCommand):
    """Meldet die Sitemap-URLs an IndexNow - und nur von der echten Domain aus.

    Drei Sperren, bevor etwas hinausgeht: kein Schluessel, kein Lauf; ein
    anderer Host als die Produktionsdomain, kein Lauf (mit ``--trotzdem`` zu
    uebergehen); ``--trocken`` zeigt nur. Google bedient das nicht - dafuer
    bleibt der Gang in die Search Console noetig.
    """

    help = 'Meldet die Sitemap-URLs per IndexNow (Bing/Yandex/Seznam).'

    def add_arguments(self, parser):
        parser.add_argument('--trocken', action='store_true',
                            help='nur zeigen, nichts senden')
        parser.add_argument('--trotzdem', action='store_true',
                            help='auch melden, wenn der Host nicht die '
                                 'Produktionsdomain ist')
        parser.add_argument('--nur', default='',
                            help='nur ein Sitemap-Segment '
                                 '(main, services, jobs, cities)')

    def handle(self, *args, **opt):
        key = getattr(settings, 'INDEXNOW_KEY', '').strip()
        if not key:
            self.stderr.write('INDEXNOW_KEY ist leer - nichts zu tun.')
            return

        # _canonical_domain() liefert die NACKTE Domain ohne Schema
        # (so braucht die Sitemap sie). IndexNow will beides: 'host' ohne
        # Schema, die URLs mit.
        host = _canonical_domain()
        basis = 'https://%s' % host

        # Sperre gegen den teuersten Bedienfehler: Auf einer Entwicklungsmaschine
        # steht SITE_URL auf localhost. Eine Meldung mit diesem Host waere nicht
        # nur wirkungslos, sie wuerde den Schluessel gegen eine Domain
        # verbrennen, ueber die wir keine Verfuegungsgewalt haben.
        if host != _PRODUCTION_DOMAIN and not opt['trotzdem']:
            self.stderr.write(self.style.ERROR(
                'Host ist "%s", erwartet "%s". Gemeldet wird nur die '
                'Produktionsdomain. Mit --trotzdem uebergehen.'
                % (host, _PRODUCTION_DOMAIN)))
            return

        urls = self._urls(opt['nur'])
        if not urls:
            self.stderr.write('Keine URLs gefunden - Segment falsch geschrieben?')
            return

        self.stdout.write('%d URLs, Host %s' % (len(urls), host))
        for u in urls[:5]:
            self.stdout.write('   %s' % u)
        if len(urls) > 5:
            self.stdout.write('   ... und %d weitere' % (len(urls) - 5))

        schluesseldatei = '%s/%s.txt' % (basis.rstrip('/'), key)
        self.stdout.write('Schluesseldatei: %s' % schluesseldatei)

        if opt['trocken']:
            self.stdout.write(self.style.WARNING('Trockenlauf - nichts gesendet.'))
            return
        self._senden(host, key, schluesseldatei, urls)

    def _senden(self, host, key, schluesseldatei, urls):
        """Die Meldung an ``_ENDPUNKT`` schicken und das Ergebnis ausgeben.

        Aus ``handle`` herausgezogen (P08, 24.09.2026), Verhalten unveraendert;
        belegt durch ``IndexNowSendenTests``, die vor der Aufteilung gruen waren.
        """
        nutzlast = json.dumps({
            'host': host,
            'key': key,
            'keyLocation': schluesseldatei,
            'urlList': urls,
        }).encode('utf-8')

        req = urllib.request.Request(
            _ENDPUNKT, data=nutzlast, method='POST',
            headers={'Content-Type': 'application/json; charset=utf-8',
                     'User-Agent': _UA})
        try:
            with urllib.request.urlopen(req, timeout=30) as f:
                code, text = f.status, f.read().decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            code, text = e.code, e.read().decode('utf-8', 'replace')
        # audit-ok P02: jeder Abruffehler wird auf stderr gemeldet und beendet den Befehl
        except Exception as e:                                    # noqa: BLE001
            self.stderr.write(self.style.ERROR('Netzwerkfehler: %s' % e))
            return

        # 200 = angenommen, 202 = angenommen, Schluessel wird noch geprueft.
        # 403 heisst fast immer: Die Schluesseldatei ist nicht erreichbar.
        if code in (200, 202):
            self.stdout.write(self.style.SUCCESS(
                'HTTP %d - %d URLs angenommen.' % (code, len(urls))))
        elif code == 403:
            self.stderr.write(self.style.ERROR(
                'HTTP 403 - Schluessel abgelehnt. Ist %s oeffentlich '
                'erreichbar und enthaelt sie exakt den Schluessel?'
                % schluesseldatei))
        else:
            self.stderr.write(self.style.ERROR(
                'HTTP %d: %s' % (code, text[:300])))

    # ------------------------------------------------------------------
    def _urls(self, nur):
        """Alle URLs aus den registrierten Sitemap-Klassen, absolut."""
        from config.urls import sitemaps

        basis = 'https://%s' % _canonical_domain()
        raus = []
        for name, klasse in sitemaps.items():
            if nur and name != nur:
                continue
            sm = klasse()
            for eintrag in sm.items():
                raus.append(basis + sm.location(eintrag))
        # Reihenfolge stabil, Doppelte raus (ein Pfad koennte in zwei
        # Segmenten stehen - das waere ein Fehler, aber kein Grund, ihn
        # doppelt zu melden).
        gesehen, eindeutig = set(), []
        for u in raus:
            if u not in gesehen:
                gesehen.add(u)
                eindeutig.append(u)
        return eindeutig
