# -*- coding: utf-8 -*-
"""Die echten Google-Rezensionen – eine Quelle fuer Seite und Schema (F8).

Bis zum 14.08.2026 standen die sechs Texte als fertiges HTML in ``home.html``
und tauchten im JSON-LD gar nicht auf. Google ignoriert ein ``AggregateRating``
ohne einzelne ``Review``-Objekte ("self-serving"), und umgekehrt darf im Schema
nichts stehen, was auf der Seite nicht sichtbar ist. Beides kommt jetzt hierher.

**Seit dem 14.08.2026 abends wird taeglich abgeglichen.** Die Wahrheit steht
dann in der Datenbank (``GoogleRezension``/``GoogleBewertung``, gefuellt vom
Command ``sync_google_reviews``). Die Liste hier unten bleibt trotzdem stehen –
sie ist der **Rueckfall**, wenn die Datenbank leer ist, die Migration noch nicht
gelaufen ist oder bei Google kein API-Schluessel hinterlegt wurde. Ohne diesen
Rueckfall haette eine abgelaufene Rechnung bei Google die Kundenstimmen von der
Startseite genommen.

**Wer weder ins Schema noch auf die Seite darf, steht in ``NAHESTEHEND``** – als
*eine* Regel ueber den Namen, nicht als Feld an jedem Datensatz. Ein frisch
synchronisierter Datensatz koennte sonst still ohne die Kennzeichnung ankommen.
Google untersagt Bewertungen von Inhabern und Beteiligten im Markup. Bis zum
24.09.2026 standen sie trotzdem sichtbar als Kundenstimme auf der Startseite –
das ist das eigentliche Risiko (EIG22): Eine Bewertung des Website-Entwicklers
als Kundenstimme auszugeben, kann irrefuehrend im Sinne des § 5 UWG sein. Seitdem filtern ``fuer_seite()`` und
``fuers_schema()`` dieselbe Liste. Die Durchschnittszahl von Google bleibt davon
unberuehrt; sie ist Googles Zahl, nicht unsere Auswahl.

Abgetippt wird hier nichts: Die Texte sind woertliche Zitate.
"""

import logging
import unicodedata

_log = logging.getLogger('apps.core')

# Hoechstens so viele Karten auf der Startseite. Der Abschnitt soll nicht mit
# jeder neuen Bewertung laenger werden; das Schema bekommt exakt dieselben.
#
# Von 9 auf 12 erhoeht, nachdem der erste echte Abgleich vier bislang
# unbekannte Rezensionen mitbrachte und eine davon aus der Anzeige fiel. Die
# Zahl muss ueber dem Bestand liegen, sonst verschweigt die Seite eine echte
# Bewertung - und im Schema stuende dann weniger, als es gibt.
MAX_KARTEN = 12
# So viele Zitate zeigt die Startseite sichtbar (home.html: zwei). Das Review-Schema
# zeichnet genau diese aus - Bewertungen im Schema muessen auf der Seite stehen
# (Google-Richtlinie; bis 01.10.2026 standen 7 von 10 nur im JSON-LD).
STARTSEITE_ZITATE = 2

# Das Profil in Google Maps. Steht hier und nicht im Template, weil der Sync
# spaeter die ``googleMapsUri`` aus der API liefert und diese Adresse ablaest.
GOOGLE_PROFIL_FALLBACK = (
    'https://www.google.com/maps/place/R%C3%BCmpelwerk+Mitteldeutschland/'
    '@51.4702609,11.9652634,17z/data=!3m1!4b1!4m6!3m5!'
    '1s0x9d602ed74663a1:0xa6928b3e0473aca8!8m2!3d51.4702576!4d11.9678383!'
    '16s%2Fg%2F11nq1wtp7b'
)

# Personen, die dem Betrieb nahestehen. Weder sichtbar noch ausgezeichnet (EIG22).
NAHESTEHEND = {
    'bastian scherzinger',
}

# Rueckfall-Liste. Quelle: Google-Unternehmensprofil "Ruempelwerk
# Mitteldeutschland", uebernommen am 14.08.2026 (damals 4,9 bei 18, davon 6 mit
# Text); am 03.10.2026 nachgezogen auf 5,0 bei 33 (live aus dem Sync).
# Kein ``datePublished``: Google zeigt im Profil nur relative Angaben
# ("vor 3 Monaten"); ein daraus geratenes Datum waere eine erfundene Zahl im
# Markup. Der Sync liefert spaeter das echte ``publishTime`` mit.
# Sichtbarer Hinweis neben jeder Bewertungszahl (§ 5b Abs. 3 UWG: ob und wie
# sichergestellt wird, dass Bewertungen von echten Kunden stammen). Der Stand
# (``stand_anzeige``) ist das Abrufdatum des letzten Abgleichs, nie getippt.
HINWEIS = ('Die Bewertungen stammen von Google und werden von uns nicht darauf '
           'geprüft, ob sie von Kunden stammen, die unsere Leistung genutzt '
           'haben; wie Google das prüft, beschreibt Google auf seinen Seiten.')

STAND = {'wert': '5.0', 'anzahl': '33', 'geprueft': '2026-10-03'}

REZENSIONEN = [
    {
        'name': 'Justin Clair',
        'initialen': 'JC',
        'sterne': 5,
        'text': (
            'Absolute Empfehlung! Wir haben eine 120 m² große Immobilie räumen lassen und '
            'sind mehr als zufrieden. Oliver Pohl hat sich von Anfang an persönlich um '
            'alles gekümmert, war jederzeit erreichbar und hat den Ablauf professionell '
            'organisiert. Das Team war pünktlich, freundlich und hat die komplette '
            'Räumung in nur zwei Tagen fachgerecht und sauber durchgeführt – am Ende '
            'alles besenrein übergeben. Jederzeit wieder!'
        ),
    },
    {
        'name': 'Katrin Janell',
        'initialen': 'KJ',
        'sterne': 5,
        'text': (
            'Ich bin absolut begeistert von dieser Firma! Der gesamte Ablauf war von '
            'Anfang bis Ende professionell organisiert, mein Umzug verlief reibungslos – '
            'keine Schäden, keine Kratzer, einfach perfekt. Nach vielen schlechten '
            'Erfahrungen mit anderen Firmen endlich ein Unternehmen, auf das man sich '
            'wirklich verlassen kann. Jederzeit wieder!'
        ),
    },
    {
        'name': 'Kay Reh',
        'initialen': 'KR',
        'sterne': 5,
        'text': (
            'Der beste Service und Kundenkontakt seit langem :) Die Beratung hat mir '
            'äußerst gut gefallen, die Nachbetreuung ist empfehlenswert und das '
            'Preis-Leistungs-Verhältnis ist absolut der Hammer. Danke für die schnelle '
            'Zusammenarbeit und die rasche Umsetzung. Sehr gerne wieder.'
        ),
    },
    {
        'name': 'Jenny Jacob',
        'initialen': 'JJ',
        'sterne': 5,
        'text': (
            'Ich bin sehr zufrieden mit der erbrachten Leistung. Von der ersten Beratung '
            'bis zur Fertigstellung wurde alles transparent, zuverlässig und '
            'kundenorientiert umgesetzt. Fragen wurden schnell beantwortet und auf '
            'Wünsche eingegangen. Ich kann die Firma uneingeschränkt weiterempfehlen.'
        ),
    },
    {
        'name': 'Simone John',
        'initialen': 'SJ',
        'sterne': 5,
        'text': (
            'Sehr freundlicher und hilfsbereiter Kontakt. Zuverlässiger und schneller '
            'Service und Beräumung. Immer wieder gern – vielen Dank nochmal für alles.'
        ),
    },
]


def _schluessel(name):
    """NFC-normalisierte Vergleichsform – siehe ``google_reviews``."""
    return unicodedata.normalize('NFC', (name or '')).strip().casefold()


def darf_ins_schema(name):
    return _schluessel(name) not in NAHESTEHEND


# ── Lesen ───────────────────────────────────────────────────────────────────
#
# Alle Zugriffe auf die Datenbank sind abgesichert: Diese Funktionen laufen bei
# jedem Aufruf der Startseite, und sie duerfen auch dann noch etwas liefern,
# wenn die Migration 0015 noch nicht durch ist (frischer Klon, `check_seo` auf
# einer leeren SQLite, ein Deploy mitten in `migrate`).

def _aus_datenbank():
    try:
        from apps.core.models import GoogleRezension
        zeilen = list(
            GoogleRezension.objects.filter(sichtbar=True)
            .exclude(text='')[:MAX_KARTEN]
        )
    except Exception as exc:              # noqa: BLE001 – bewusst alles fangen
        _log.debug('Rezensionen aus der Datenbank nicht lesbar: %s', exc)
        return None
    if not zeilen:
        return None
    # ``datum`` nur, wenn Google es geliefert hat. Ein geschaetztes
    # ``datePublished`` waere eine erfundene Zahl im Markup – die abgetippten
    # sechs haben deshalb keins.
    return [{'name': z.name, 'initialen': z.initialen, 'sterne': z.sterne,
             'text': z.text, 'profil_url': z.profil_url,
             'datum': z.veroeffentlicht.date().isoformat() if z.veroeffentlicht else '',
             'relativ': z.relativ}
            for z in zeilen]


def _liste():
    """Die maßgebliche Liste: Datenbank, sonst die Rueckfall-Liste."""
    aus_db = _aus_datenbank()
    if aus_db is not None:
        return aus_db
    return [dict(r, profil_url='', datum='', relativ='')
            for r in REZENSIONEN[:MAX_KARTEN]]


def stand():
    """Durchschnitt, Anzahl und Datum der letzten Pruefung.

    Immer Strings mit Punkt als Dezimaltrenner – der Wert geht direkt ins
    JSON-LD, und ein Komma macht daraus ungueltiges JSON.
    """
    try:
        from apps.core.models import GoogleBewertung
        from django.utils import timezone
        s = GoogleBewertung.objects.first()
        if s:
            return _stand_felder(
                s.wert_txt, str(s.anzahl),
                timezone.localtime(s.geprueft_am).strftime('%Y-%m-%d'),
                s.profil_url)
    except Exception as exc:              # noqa: BLE001
        _log.debug('Bewertungsstand aus der Datenbank nicht lesbar: %s', exc)
    return _stand_felder(STAND['wert'], STAND['anzahl'], STAND['geprueft'], '')


def _stand_felder(wert, anzahl, geprueft, profil_url):
    # ``wert`` bleibt mit Punkt - er geht so ins JSON-LD. ``wert_anzeige`` ist
    # die deutsche Schreibweise fuer die sichtbare Seite. Beide aus einer
    # Quelle, damit sie nicht auseinanderlaufen koennen.
    return {'wert': wert, 'wert_anzeige': wert.replace('.', ','),
            'anzahl': anzahl, 'geprueft': geprueft,
            'stand_anzeige': _datum_anzeige(geprueft),
            'hinweis': HINWEIS,
            'profil_url': profil_url or GOOGLE_PROFIL_FALLBACK}


def _datum_anzeige(iso):
    """'2026-10-03' -> '03.10.2026' (sichtbarer Stand; Quelle bleibt ``geprueft``)."""
    try:
        j, m, t = iso.split('-')
        return '%02d.%02d.%04d' % (int(t), int(m), int(j))
    except (ValueError, AttributeError):
        return iso


def fuer_seite():
    """Die Liste fuers Template.

    ``sterne_liste``, weil Django-Templates kein ``range`` kennen und die
    Sterne-SVGs sonst wieder von Hand gezaehlt werden muessten – genau der
    Pflegefehler, vor dem CLAUDE.md warnt.

    Ohne ``NAHESTEHEND`` (EIG22): Eine Bewertung aus dem Umfeld des Betriebs
    erscheint nicht als Kundenstimme. Gefiltert wird VOR dem Durchzaehlen,
    sonst bekaeme die Kartenreihe eine Luecke in der Einblend-Verzoegerung.
    """
    kunden = [r for r in _liste() if darf_ins_schema(r['name'])][:STARTSEITE_ZITATE]
    return [dict(r, sterne_liste=range(r['sterne']), delay=(i % 3) + 1)
            for i, r in enumerate(kunden)]


def fuers_schema():
    """Die Rezensionen, die die Startseite sichtbar zeigt - und nur die."""
    return [r for r in _liste() if darf_ins_schema(r['name'])][:STARTSEITE_ZITATE]
