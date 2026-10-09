"""Importiert Google-Business-Profil-Beitraege in ``AktuellesPost`` (Bauplan §7).

**GBP-Beitraege Stufe 1.** Oliver postet regelmaessig kurze Neuigkeiten im
Google-Unternehmensprofil ("Google Posts") - dieselben Texte sind auf der
eigenen Seite ungenutzt. Dieser Befehl liest einen JSON-Export (Format unten)
und legt fuer jeden neuen Beitrag einen ``AktuellesPost`` (Typ ``bericht``)
plus eine ``AktuellesQuelle``-Zeile an (Migration 0023 - eigene Tabelle statt
neuem Feld an ``AktuellesPost``, siehe deren Docstring in ``models.py``).

**Aufruf:**

    python manage.py gbp_beitraege_import pfad/zur/datei.json
    python manage.py gbp_beitraege_import pfad/zur/datei.json --trockenlauf

``--trockenlauf`` schreibt nichts, zeigt aber jede Entscheidung (Dublette /
importiert / unveroeffentlicht wegen Wortliste) - fuer eine Probe vor dem
echten Import.

**Erwartetes JSON:** eine Liste von Objekten, je Beitrag mindestens ``text``.
Optional ``id`` (die GBP-Kennung, fuer den Dublettencheck) und ``datum``
(``JJJJ-MM-TT``, das urspruengliche Post-Datum - ohne dieses Feld gilt der
Tag des Imports). Siehe ``apps/core/tests/fixtures/gbp_beitraege_beispiel.json``.

**Drei Sicherungen, bevor ein Beitrag live geht:**

1. **Emoji und Hashtags werden entfernt** (``_bereinigen``) - GBP-Texte sind
   fuer Social-Media-Optik geschrieben, nicht fuer eine seriöse Firmenseite;
   Regel: Funktion vor Design, hier: Seriosität vor Copy-Paste.
2. **Dublettencheck** ueber ``AktuellesQuelle.text_hash`` (Wortlaut, nach der
   Bereinigung) UND ``quelle_id`` (dieselbe GBP-Post-ID kann nicht zweimal
   importiert werden) - ein erneuter Lauf mit derselben oder einer erweiterten
   Exportdatei legt nichts doppelt an.
3. **Die Wortliste** (``_WORTLISTE_RISIKO`` + Ortsnamen ausserhalb von
   ``data/cities.py``) haelt Beitraege mit unbelegten oder falschen
   Behauptungen zurueck: ``veroeffentlicht=False``, damit ein Mensch erst
   nachsieht, bevor sie live gehen. Ohne Treffer wird sofort veroeffentlicht -
   Stufe 1 ist ein Automatismus mit Bremse, keine Vorab-Freigabe fuer jeden
   Beitrag (das waere keine Automatisierung mehr).

   * ``Festpreis``/``garantiert`` - widerspricht Regel 1 (jede Preiszahl kommt
     aus ``pricing.py``, nie eine Garantie ohne Besichtigung) und ist ein
     UWG-§5-Risiko (unbelegte Zusicherung).
   * ``bundesweit`` - der Betrieb bedient Halle/Leipzig und das Umland
     (``data/cities.py``), keine bundesweite Taetigkeit.
   * ``seit Jahren`` - eine Erfahrungsbehauptung, die nirgends belegt ist
     (anders als die echten Zahlen aus ``data/reviews.py``/``firma.py``).
   * ein Ortsname ausserhalb der bekannten Staedte - ein GBP-Post, der einen
     Auftrag in einer Stadt ausserhalb des Einsatzgebiets nennt, waere ein
     Local-SEO-Signal an die falsche Adresse.

**Was dieser Befehl NICHT tut:** Bilder importieren (Stufe 1 ist Text
    - Bilder bleiben Handarbeit im CMS, ``AktuellesBild``), die Wortliste
    pflegen (sie steht als Konstante hier, keine eigene Datenquelle) oder
    einen Beitrag veroeffentlichen, den ein Mensch zurueckgehalten hat -
    ein zweiter Lauf ueberschreibt ``veroeffentlicht`` nie, er ueberspringt
    die Dublette vollstaendig.
"""

import hashlib
import json
import logging
import re
import sys
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

logger = logging.getLogger('apps.core')

# ── Bereinigung ──────────────────────────────────────────────────────────────

_RE_HASHTAG = re.compile(r'#\w+', re.UNICODE)
# Emoji-Bereiche (Unicode-Bloecke fuer Symbole/Piktogramme/Fahnen) - kein
# vollstaendiger Emoji-Bereich, aber die, die in Google-Posts tatsaechlich
# auftauchen (Haken, Sterne, Herzen, Fahnen, Pfeile, Werkzeuge …).
_RE_EMOJI = re.compile(
    '['
    '\U0001F300-\U0001FAFF'
    '\U00002600-\U000027BF'
    '\U0001F1E6-\U0001F1FF'
    '\U00002190-\U000021FF'
    '\U00002B00-\U00002BFF'
    '\U0000FE0F'
    ']+', flags=re.UNICODE)


def _bereinigen(text):
    """Entfernt Emoji und Hashtags, glaettet Leerraum. Nie ``None``."""
    text = text or ''
    text = _RE_EMOJI.sub('', text)
    text = _RE_HASHTAG.sub('', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ── Wortliste (Bauplan §7) ───────────────────────────────────────────────────

#: Woerter/Wendungen, die einen importierten Beitrag zurueckhalten - siehe
#: Modulkopf fuer die Begruendung je Eintrag. Kleinschreibung, weil der
#: Vergleich selbst ``.lower()`` anwendet.
_WORTLISTE_RISIKO = ('festpreis', 'garantiert', 'garantie', 'bundesweit',
                     'seit jahren')

#: Grossstaedte ausserhalb des Einsatzgebiets, die in einem generischen
#: GBP-Post auftauchen koennten (Vorlagen-Text, falsch uebernommene Stadt
#: usw.). Kein Anspruch auf Vollstaendigkeit - Stufe 1 ist eine Bremse fuer
#: den haeufigen Fall, keine erschoepfende Ortserkennung.
_ORTE_KANDIDATEN = (
    'Berlin', 'Hamburg', 'München', 'Munich', 'Köln', 'Cologne', 'Frankfurt',
    'Stuttgart', 'Nürnberg', 'Bremen', 'Duisburg', 'Essen', 'Dortmund',
    'Bonn', 'Bielefeld', 'Mannheim', 'Karlsruhe', 'Wiesbaden', 'Münster',
    'Augsburg', 'Aachen', 'Mönchengladbach', 'Wuppertal', 'Kiel', 'Rostock',
)


def _bekannte_orte():
    """Alle Städtenamen aus ``data/cities.py`` - kein Treffer der Wortliste."""
    from apps.core.data import _CITY_DATA
    return {v['name'] for v in _CITY_DATA.values()}


def _wortliste_treffer(text):
    """Liste der Gruende, warum ein Beitrag unveroeffentlicht bleiben sollte."""
    niedrig = text.lower()
    gruende = [w for w in _WORTLISTE_RISIKO if w in niedrig]
    bekannt = _bekannte_orte()
    for ort in _ORTE_KANDIDATEN:
        if ort in bekannt:
            continue
        if re.search(r'\b%s\b' % re.escape(ort), text):
            gruende.append(f'Ort außerhalb des Einsatzgebiets: {ort}')
    return gruende


# ── Titel und Slug ───────────────────────────────────────────────────────────

_TITEL_MAX_ZEICHEN = 70


def _titel_aus_text(text):
    """Die erste Zeile oder die ersten Woerter als Titel - nie leer."""
    erste_zeile = (text.split('\n', 1)[0] or '').strip()
    quelle = erste_zeile if erste_zeile else text.strip()
    if not quelle:
        return 'Neuigkeit'
    if len(quelle) <= _TITEL_MAX_ZEICHEN:
        return quelle
    return quelle[:_TITEL_MAX_ZEICHEN].rsplit(' ', 1)[0] + '…'


def _eindeutiger_slug(basis_titel, jahr):
    """Ein im Jahr eindeutiger Slug - ``-2``, ``-3`` … bei einem Zusammenstoss."""
    from apps.core.models import AktuellesPost

    basis = slugify(basis_titel) or 'beitrag'
    slug = basis
    zaehler = 2
    while AktuellesPost.objects.filter(slug=slug, datum__year=jahr).exists():
        slug = f'{basis}-{zaehler}'
        zaehler += 1
    return slug


def _datum_parsen(wert):
    if not wert:
        return None
    try:
        return timezone.datetime.strptime(str(wert)[:10], '%Y-%m-%d').date()
    except ValueError:
        return None


class Command(BaseCommand):
    help = ('Importiert GBP-Beitraege (JSON) in AktuellesPost. '
           '--trockenlauf prueft nur, ohne zu schreiben.')

    def add_arguments(self, parser):
        parser.add_argument('datei', help='Pfad zur JSON-Exportdatei.')
        parser.add_argument('--trockenlauf', action='store_true',
                            help='Nur anzeigen, was passieren wuerde - '
                                 'nichts in die Datenbank schreiben.')

    def handle(self, *args, **opt):
        from apps.core.models import AktuellesPost, AktuellesQuelle

        # Windows-Konsolen laufen als cp1252 - dieselbe Falle wie in
        # check_seo.py (siehe deren Docstring): Titel/Wortlisten-Gruende
        # enthalten deutsche Umlaute, ohne diese Zeile bricht ein Lauf mit
        # vielen Beitraegen mit UnicodeEncodeError ab, statt seinen Bericht
        # fertig auszugeben.
        for strom in (sys.stdout, sys.stderr):
            try:
                strom.reconfigure(encoding='utf-8', errors='replace')
            except (AttributeError, ValueError):        # pragma: no cover
                pass

        pfad = Path(opt['datei'])
        if not pfad.exists():
            raise CommandError(f'Datei nicht gefunden: {pfad}')
        try:
            rohdaten = json.loads(pfad.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            raise CommandError(f'Ungueltiges JSON in {pfad}: {e}')
        if not isinstance(rohdaten, list):
            raise CommandError('Die JSON-Datei muss eine Liste von Beitraegen sein.')

        trockenlauf = opt['trockenlauf']
        importiert = uebersprungen = unveroeffentlicht = 0

        for i, eintrag in enumerate(rohdaten):
            if not isinstance(eintrag, dict):
                self.stdout.write(self.style.WARNING(
                    f'#{i}: kein Objekt - übersprungen'))
                uebersprungen += 1
                continue

            quelle_id = str(eintrag.get('id', '')).strip()
            text = _bereinigen(eintrag.get('text', ''))
            if not text:
                self.stdout.write(self.style.WARNING(
                    f'#{i} ({quelle_id or "ohne Kennung"}): leerer Text - übersprungen'))
                uebersprungen += 1
                continue

            text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
            dublette = AktuellesQuelle.objects.filter(Q(text_hash=text_hash) | (
                Q(quelle_id=quelle_id) & ~Q(quelle_id=''))) if quelle_id else \
                AktuellesQuelle.objects.filter(text_hash=text_hash)
            if dublette.exists():
                self.stdout.write(f'#{i} ({quelle_id or text_hash[:8]}): '
                                  'bereits importiert - übersprungen (Dublette)')
                uebersprungen += 1
                continue

            original_datum = _datum_parsen(eintrag.get('datum'))
            datum = original_datum or timezone.now().date()
            titel = _titel_aus_text(text)
            gruende = _wortliste_treffer(text)
            veroeffentlicht = not gruende

            if trockenlauf:
                status = ('unveroeffentlicht: ' + '; '.join(gruende)
                         if gruende else 'würde veröffentlicht')
                self.stdout.write(f'#{i} ({quelle_id or text_hash[:8]}) '
                                  f'"{titel}" -> {status}')
                if gruende:
                    unveroeffentlicht += 1
                importiert += 1
                continue

            with transaction.atomic():
                slug = _eindeutiger_slug(titel, datum.year)
                post = AktuellesPost.objects.create(
                    typ='bericht', titel=titel, inhalt=text,
                    veroeffentlicht=veroeffentlicht, datum=datum, slug=slug,
                )
                AktuellesQuelle.objects.create(
                    post=post, quelle='gbp', quelle_id=quelle_id,
                    text_hash=text_hash, original_datum=original_datum,
                )
            importiert += 1
            if gruende:
                unveroeffentlicht += 1
                self.stdout.write(self.style.WARNING(
                    f'"{titel}" importiert, aber UNVERÖFFENTLICHT '
                    f'(Wortliste: {", ".join(gruende)})'))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f'"{titel}" importiert und veröffentlicht'))

        self.stdout.write(
            f'\n{importiert} {"geprüft" if trockenlauf else "importiert"}, '
            f'{uebersprungen} übersprungen (Dubletten/leer), '
            f'{unveroeffentlicht} davon unveröffentlicht (Wortliste).')
