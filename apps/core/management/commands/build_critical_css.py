"""Erzeugt das Inline-CSS fuer den Seitenkopf (`components/critical/<seite>.html`).

Warum das noetig ist
--------------------
`static/css/ruempelwerk.css` ist das komplette Designsystem in einer Datei und
blockierte als `<link rel="stylesheet">` das erste Rendering. PageSpeed mass
dafuer 160 ms Blockierzeit und 170 ms "Verzoegerung beim Rendering des
Elements" im LCP – der Hero konnte erst gezeichnet werden, wenn die ganze
Datei geparst war.

Loesung: Die Regeln, die oberhalb der Falz gebraucht werden, stehen inline im
`<head>` (siehe `components/rw_css.html`); die vollstaendige Datei wird
asynchron nachgeladen. Damit rendert der Hero ohne Netzwerk-Runde.

Eine Datei je Seite
-------------------
Frueher gab es *einen* gemeinsamen Block fuer alle Seiten. Der enthielt die
Vereinigung aller Klassen – gemessen bestanden dadurch **56 %** des Inline-CSS
einer durchschnittlichen Seite aus Regeln fuer Klassen, die es auf ihr gar
nicht gibt (`/impressum/` trug den kompletten Hero und den Preisrechner mit).
Deshalb bekommt jedes Template seine eigene Datei unter
``templates/components/critical/``.

``rw_critical_css.html`` (der alte gemeinsame Block) wird weiter erzeugt und
dient als Rueckfalloption: Bindet eine Seite `rw_css.html` ohne ``crit_page``
ein, bekommt sie ihn. Das ist zwar gross, aber nie unvollstaendig – eine neu
angelegte Seite, bei der die Variable vergessen wurde, rendert also korrekt
statt ungestylt.

Wie ausgewaehlt wird
--------------------
Nicht per Hand gepflegte Liste – die veraltet. Stattdessen datengetrieben:

1. Aus jedem oeffentlichen Template werden die Klassen der ersten
   ``--body-lines`` Zeilen nach ``<body`` eingesammelt (das deckt Navigation,
   Hero und Breadcrumb zuverlaessig ab).
2. Dazu die Klassen der immer sichtbaren Komponenten (Navigation, Cookie-
   Banner, Bottom-Nav) – die stehen per Include am Seitenende, sind aber
   `position: fixed` und damit sofort im Blick.
3. Behalten wird jede Regel, deren Selektor eine dieser Klassen enthaelt,
   sowie Element-Selektoren (``*``, ``body``, ``h1`` …), ``:root`` und alle
   ``@font-face``-Bloecke.

``@font-face`` MUSS mit hinein: die Schriften stehen auf ``font-display:
optional``. Kaemen sie erst mit dem nachgeladenen CSS, waeren sie fuer den
ersten Seitenaufruf zu spaet und der Browser bliebe beim Fallback.

Aufruf nach jeder groesseren CSS-Aenderung::

    python manage.py build_critical_css

Das Ergebnis wird ins Repo eingecheckt; ``--check`` verifiziert im Deploy oder
lokal, ob die Dateien noch zum CSS passen.
"""

import re
import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

try:
    from rcssmin import cssmin
except ImportError:  # pragma: no cover
    cssmin = None

# Komponenten, die auf jeder Seite sofort sichtbar sind (fixed/sticky).
_ALWAYS_TEMPLATES = (
    'components/rw_nav.html',
    'components/rw_cookie_banner.html',
)

# Klassenfamilien, die komplett mitkommen, sobald die Seite auch nur ein
# Mitglied benutzt. Der Zeilen-Heuristik entgehen sonst Teile, die zwar weiter
# unten im Template stehen, aber trotzdem im ersten Bild landen – der Hero ist
# der klassische Fall (Trustbar und Foto-Overlay stehen hinter dem Text).
# Die Bindung an ein tatsaechlich benutztes Mitglied ist wichtig: ohne sie
# trugen auch Seiten ganz ohne Hero (Impressum, AGB) dessen 6,8 KiB mit.
_FAMILY_PREFIXES = ('rw-hero', 'rw-nav', 'rw-cc-', 'rw-bottom-nav')

# Element-/Struktur-Selektoren ohne Klasse: immer kritisch (Reset, Typografie).
_BARE_OK = {
    '*', '*::before', '*::after', ':root', 'html', 'body', 'a', 'img', 'svg',
    'picture', 'p', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'li', 'button',
    'input', 'select', 'textarea', 'strong', 'em', 'span', 'section', 'main',
    'header', 'nav', 'figure', 'figcaption', 'video', 'label',
}

# ``class="…"`` – und zwar auch dann, wenn ein Django-Tag darin steht.
#
# ⚠ Bis zum 18.09.2026 stand hier ``class="([^"{}]*)"``: ein Attribut mit
# ``{% if … %}`` darin wurde **komplett uebersprungen**, samt der statischen
# Klasse davor. Auf den Formularseiten traegt fast jedes Feld so ein Attribut
# (``class="rw-form-input{% if form.name.errors %} …--error{% endif %}"``) -
# also fehlten ``.rw-form-input`` und ``.rw-form-textarea`` im kritischen CSS
# von ``/anfrage/``, obwohl das Formular dort ueber der Falz steht. Aufgefallen
# ist es wie immer nur daran, dass das Erzeugnis schrumpfte (Regel 26): Die
# eingecheckte Datei stammte noch aus einer nachsichtigeren Fassung und liess
# sich nicht mehr reproduzieren.
#
# Die Tags werden vor dem Zerlegen durch ein Leerzeichen ersetzt, damit aus
# ``rw-form-input{% if … %}`` wieder der Name ``rw-form-input`` wird. Was das
# NICHT loest: eine Klasse, die vollstaendig aus einer Variablen kommt
# (``class="{{ art }}"``) - die steht nirgends im Quelltext und kann deshalb
# auch nicht eingesammelt werden.
_DJANGO_TAG_RE = re.compile(r'\{%.*?%\}|\{\{.*?\}\}|\{#.*?#\}', re.S)
_CLASS_RE = re.compile(r'class="([^"]*)"')


def _klassen_aus(text):
    """Alle Klassennamen aus den ``class="…"``-Attributen eines Templates."""
    namen = set()
    for m in _CLASS_RE.finditer(text):
        namen.update(_DJANGO_TAG_RE.sub(' ', m.group(1)).split())
    return namen
_SEL_CLASS_RE = re.compile(r'\.(-?[_a-zA-Z][\w-]*)')
_COMMENT_RE = re.compile(r'/\*.*?\*/', re.S)
# Klassen, die erst per JavaScript gesetzt werden – sie stehen in keinem
# class="…"-Attribut, muessen aber trotzdem kritisch sein. Prominentestes
# Beispiel: [data-rw-reveal] blendet Inhalte mit opacity:0 aus und erst
# `.visible` holt sie zurueck. Fehlte die zweite Regel im Inline-CSS, waere
# der halbe Seiteninhalt bis zum Nachladen unsichtbar.
_JS_CLASS_RE = re.compile(r"""classList\.(?:add|remove|toggle|contains)\(\s*['"]([\w-]+)""")

# {% include 'components/x.html' %} - die Zeilen-Heuristik muss dahinter sehen.
# Aufgefallen bei A15: Der Preisrechner wurde aus preisangebot.html in eine
# Komponente herausgeloest und stand danach als EINE Zeile im Template. Damit
# fielen seine Klassen aus dem Fenster der ersten 160 Body-Zeilen - obwohl er
# auf dieser Seite direkt unter dem Hero steht. Das Inline-CSS schrumpfte um
# 4,2 KiB, und genau die haetten oberhalb der Falz gefehlt.
_INCLUDE_RE = re.compile(r"""\{%\s*include\s+['"]([^'"]+)['"]""")

# Zustandsregeln sind fuer das erste Bild nie noetig – sie greifen erst,
# wenn der Nutzer zeigt oder tippt, und da ist das volle CSS laengst da.
_STATE_RE = re.compile(r':(?:hover|focus|focus-within|focus-visible|active|target)\b')

# Deklarationen, die auf das erste Bild keinen Einfluss haben. Sie machen in
# diesem Designsystem einen erheblichen Teil der Bytes aus (fast jede Regel
# hat eine transition-Zeile). Nachtraeglich gesetzte Uebergaenge loesen keine
# Animation aus, das Weglassen ist also auch optisch folgenlos.
_DROP_DECL_RE = re.compile(
    r'(?:^|;)\s*(?:transition|transition-[\w-]+|animation|animation-[\w-]+|'
    r'will-change|cursor|scroll-behavior|-webkit-tap-highlight-color|'
    r'user-select|-webkit-user-select|text-rendering)\s*:[^;}]*',
    re.I,
)


def _strip_decls(body):
    return _DROP_DECL_RE.sub('', body)


# Kommentare zaehlen nicht als Markup - und das ist keine Kosmetik, sondern
# eine Korrektur vom 27.08.2026. Die Auswahl oben nimmt die ersten
# ``--body-lines`` Zeilen nach ``<body``; jede Kommentarzeile in einer
# eingebundenen Komponente verdraengt dabei eine Zeile echtes Markup am Ende
# des Fensters. Der Antwortblock aus G2 (``rw_antwort.html``) brachte 30
# Zeilen Erklaerung mit - und **0,7 bis 3,9 KiB Regeln fielen aus dem
# kritischen CSS von vier Seiten**, darunter ``.rw-section``, das auf der
# Startseite direkt unter dem Hero gebraucht wird. Aufgefallen ist es nur
# daran, dass das Erzeugnis SCHRUMPFTE (Regel 26) - derselbe Beinahe-Fehler
# wie bei W4, wo ``.visible`` verschwand.
#
# Entfernt werden ganze Zeilen, nicht nur die Zeichen: Eine leergeraeumte
# Zeile fraesse das Fenster genauso auf wie die kommentierte.
_KOMMENTAR_RE = re.compile(
    r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}"
    r"|\{#.*?#\}"
    r"|<!--.*?-->", re.S)


def _ohne_kommentare(text):
    ohne = _KOMMENTAR_RE.sub('', text)
    return '\n'.join(z for z in ohne.splitlines() if z.strip())


_HEADER = (
    '{% load static %}{% comment %}\n'
    'AUTOMATISCH ERZEUGT von `python manage.py build_critical_css` – nicht von Hand aendern.\n'
    'Quelle: static/css/ruempelwerk.css. Enthaelt nur die Regeln oberhalb der Falz;\n'
    'die vollstaendige Datei wird in components/rw_css.html asynchron nachgeladen.\n'
    '{% endcomment %}'
)

# Relative url() muessen beim Inlining absolut werden: in einem <style>-Block
# loest der Browser sie gegen die SEITEN-URL auf, nicht gegen die CSS-Datei.
# Auf /entrumpelung/leipzig/ waere aus ../fonts/x.woff2 sonst
# /entrumpelung/fonts/x.woff2 – 404, und damit keine Schriften.
# {% static %} liefert zugleich den gehashten Dateinamen aus dem Manifest.
_FONT_URL_RE = re.compile(r"url\(['\"]?\.\./([^'\")]+)['\"]?\)")


# Inklusive BOM: ruempelwerk.css beginnt mit U+FEFF, und str.strip() ohne
# Argument entfernt das nicht. Der erste Block (@font-face Montserrat latin)
# fiel dadurch lautlos aus dem Inline-CSS – mit font-display:optional haette
# das bedeutet, dass die Headlines dauerhaft im Fallback bleiben.
_WS = '﻿ \t\r\n'


def _split_blocks(css):
    """Zerlege CSS in Toplevel-Bloecke [(prelude, body_or_None)].

    Ein einfacher Klammerzaehler reicht hier: die Datei enthaelt keine
    geschweiften Klammern in Strings oder URLs.
    """
    blocks = []
    depth = 0
    start = 0
    prelude_end = None
    for i, ch in enumerate(css):
        if ch == '{':
            if depth == 0:
                prelude_end = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                blocks.append((css[start:prelude_end].strip(_WS),
                               css[prelude_end + 1:i]))
                start = i + 1
    rest = css[start:].strip(_WS)
    if rest:
        blocks.append((rest, None))
    return blocks


def _is_critical(selector, classes, families):
    """Gehoert die Regel ins Inline-CSS dieser Seite?"""
    for part in selector.split(','):
        part = part.strip()
        if not part or _STATE_RE.search(part):
            continue
        # :root traegt die Design-Tokens – ohne sie loesen saemtliche var()
        # ins Leere auf und die Seite kaeme farb- und schriftlos hoch.
        # Die Pseudo-Bereinigung unten wuerde ':root' zu '' eindampfen,
        # deshalb hier zuerst der direkte Vergleich.
        if part in _BARE_OK or ':root' in part:
            return True
        found = _SEL_CLASS_RE.findall(part)
        if found:
            if any(c in classes or c.startswith(families) for c in found):
                return True
            continue
        # Klassenloser Selektor: nur die bekannten Element-Selektoren.
        base = re.sub(r'::?[\w-]+(\([^)]*\))?', '', part).strip()
        base = re.sub(r'\[[^\]]*\]', '', base).strip()
        tokens = [t for t in re.split(r'[\s>+~]+', base) if t]
        if tokens and all(t in _BARE_OK for t in tokens):
            return True
        if not tokens and part.startswith('['):
            # z. B. [hidden] – der globale Sichtbarkeits-Fix
            return True
    return False


def _filter_block(prelude, body, classes, families):
    """Ein Block des Stylesheets, gefiltert - oder ``None``, wenn er entfaellt.

    Aus ``_filter`` herausgezogen (P09, 24.09.2026), Verhalten unveraendert:
    ``@font-face`` bleibt ganz, ``@media``/``@supports`` werden rekursiv
    gefiltert, jede andere At-Regel (darunter ``@keyframes`` - Animationen sind
    nie renderkritisch) entfaellt, eine normale Regel bleibt nur, wenn sie
    kritisch ist und nach ``_strip_decls`` noch etwas uebrig hat.
    """
    low = prelude.lower()
    if low.startswith('@font-face'):
        return f'{prelude}{{{body}}}'
    if low.startswith(('@media', '@supports')):
        inner = _filter(body, classes, families)
        return f'{prelude}{{{inner}}}' if inner.strip() else None
    if low.startswith('@'):
        return None
    if not _is_critical(prelude, classes, families):
        return None
    stripped = _strip_decls(body)
    return f'{prelude}{{{stripped}}}' if stripped.strip(' ;\n\t') else None


def _filter(css, classes, families):
    out = []
    for prelude, body in _split_blocks(css):
        if body is None:
            continue
        block = _filter_block(prelude, body, classes, families)
        if block is not None:
            out.append(block)
    return '\n'.join(out)


def _kritisches_css(raw, klassen):
    """Das fertige Inline-CSS fuer eine Klassenmenge: gefiltert, verkleinert,
    Schrift-URLs als ``{% static %}``."""
    # Eine Familie kommt nur komplett mit, wenn die Seite sie benutzt.
    families = tuple(p for p in _FAMILY_PREFIXES
                     if any(c.startswith(p) for c in klassen))
    css = _filter(raw, klassen, families)
    if cssmin is not None:
        css = cssmin(css)
    return _FONT_URL_RE.sub(
        lambda m: "url('{%% static \"%s\" %%}')" % m.group(1), css
    )


class Command(BaseCommand):
    """Erzeugt je Seite das kritische CSS aus ``ruempelwerk.css``.

    Gesammelt werden die Klassen der ersten ``--body-lines`` Zeilen nach
    ``<body`` (Includes eingesetzt, Kommentare vorher entfernt - Regel 28) und
    die per ``classList`` gesetzten Klassen aus ``static/js/``. Wenn ein
    Erzeugnis nach einer Aenderung **schrumpft**, ist das ein Befund und keine
    Optimierung (Regel 26).
    """

    help = ('Baut templates/components/critical/<seite>.html und den '
            'gemeinsamen Rueckfall-Block aus ruempelwerk.css.')

    def add_arguments(self, parser):
        parser.add_argument('--body-lines', type=int, default=160,
                            help='Zeilen nach <body>, die als "above the fold" gelten. '
                                 '160 deckt auf allen 18 Seitentypen das obere Fuenftel '
                                 'des Markups lueckenlos ab (nachgemessen); mehr Zeilen '
                                 'ziehen fast nur noch Regeln unterhalb der Falz mit.')
        parser.add_argument('--check', action='store_true',
                            help='Nur pruefen, ob die Dateien aktuell sind (Exit 1, wenn nicht).')

    # ── Klassen einsammeln ────────────────────────────────────────────────
    def _always_classes(self, tpl_dir, js_dir=None):
        classes = set()
        for rel in _ALWAYS_TEMPLATES:
            classes.update(_klassen_aus((tpl_dir / rel).read_text(encoding='utf-8')))
        # Per JS gesetzte Klassen. Die Quellen sind seit dem 26.08.2026 ZWEI:
        # die Templates (dort steht noch der Consent-Bootstrap und der
        # Spam-Nachweis) UND static/js/. Beim Auslagern des Inline-JS
        # (Befund W4) fiel zuerst nur der Template-Zweig hier durch - und mit
        # ihm 1,9 KiB Regeln aus JEDEM der 20 Bloecke, darunter `.visible`.
        # Das ist genau der Fall, vor dem der Docstring von _JS_CLASS_RE
        # warnt: [data-rw-reveal] setzt opacity:0, und ohne `.visible` im
        # kritischen CSS bleibt der halbe Seiteninhalt bis zum Nachladen der
        # vollen Datei unsichtbar. Wer JS an eine dritte Stelle legt, traegt
        # sie hier nach.
        quellen = []
        for path in sorted(tpl_dir.rglob('*.html')):
            if 'critical' in path.parts or path.name.startswith('rw_critical_css'):
                continue
            quellen.append(path)
        if js_dir and js_dir.is_dir():
            quellen.extend(sorted(js_dir.rglob('*.js')))
        for path in quellen:
            classes.update(_JS_CLASS_RE.findall(path.read_text(encoding='utf-8')))
        return classes

    def _expand(self, tpl_dir, text, tiefe=0):
        """Includes an Ort und Stelle einsetzen, damit die Zeilenzaehlung stimmt.

        Komponenten aus ``_ALWAYS_TEMPLATES`` bleiben absichtlich eine Zeile:
        Ihre Klassen sind ohnehin auf jeder Seite kritisch, und ausgeschrieben
        wuerden sie das Zeilenfenster fuer den eigentlichen Seiteninhalt
        auffressen. Zwei Ebenen reichen; tiefer verschachtelt ist im Projekt
        nichts, und die Grenze schuetzt vor einem Include-Zirkel.

        **Kommentare fallen vor dem Einsetzen weg, nicht danach** - und das ist
        keine Reihenfolgefrage des Geschmacks. Am 27.08.2026 (nachmittags) hat
        genau das 2,6 KiB aus dem kritischen CSS der Startseite gekostet,
        darunter ``.rw-section-header`` und die gesamte ``.rw-prozess``-Familie:

        ``rw_antwort.html`` erklaert in seinem Kommentar den eigenen Aufruf und
        schreibt dafuer ein ``{% include 'components/rw_antwort.html' … %}``
        hin. Wurde zuerst expandiert, setzte das Werkzeug an dieser Stelle die
        **komplette Komponente** ein - mitsamt ihrem eigenen
        ``{% endcomment %}``. Dieses innere ``{% endcomment %}`` schloss dann
        den aeusseren Kommentar, und alles danach blieb als vermeintliches
        Markup stehen. Je ausfuehrlicher der Kommentar, desto mehr Zeilen
        Blindtext - 15 in diesem Fall, und damit rutschte der halbe
        Seiteninhalt aus dem 160-Zeilen-Fenster.

        Wer die Reihenfolge wieder umdreht, bekommt denselben Fehler zurueck,
        und er sieht wie eine harmlose Verkleinerung aus (Regel 26).
        """
        text = _ohne_kommentare(text)
        if '{%' not in text:
            return text

        def _sub(m):
            rel = m.group(1)
            if rel in _ALWAYS_TEMPLATES or tiefe >= 2:
                return m.group(0)
            datei = tpl_dir / rel
            if not datei.exists():
                return m.group(0)
            return self._expand(tpl_dir, datei.read_text(encoding='utf-8'), tiefe + 1)

        return _INCLUDE_RE.sub(_sub, text)

    def _page_classes(self, path, body_lines, tpl_dir):
        text = path.read_text(encoding='utf-8')
        idx = text.find('<body')
        if idx < 0:
            return None
        roh = _ohne_kommentare(self._expand(tpl_dir, text[idx:]))
        head = '\n'.join(roh.splitlines()[:body_lines])
        return _klassen_aus(head)

    @staticmethod
    def _clean(classes):
        """Django-Tags aus Klassenlisten wie class="{% if x %}a{% endif %} b"."""
        return {c for c in classes
                if c and not c.startswith(('{%', '{{', '%}', '}}'))
                and '{' not in c and '}' not in c}

    def _jobs(self, tpl_dir, js_dir, out_dir, body_lines):
        """(Zieldatei, Klassenmenge) je Seite, plus der gemeinsame Rueckfall."""
        always = self._always_classes(tpl_dir, js_dir)
        jobs = []
        alle = set(always)
        for path in sorted(tpl_dir.glob('*.html')):
            if path.name == 'base.html':      # Altbestand, eigenes CSS
                continue
            eigene = self._page_classes(path, body_lines, tpl_dir)
            if eigene is None:
                continue
            klassen = self._clean(always | eigene)
            alle |= klassen
            jobs.append((out_dir / path.name, klassen))
        jobs.append((tpl_dir / 'components' / 'rw_critical_css.html', self._clean(alle)))
        return jobs

    def _verwaiste(self, out_dir, jobs, check):
        """Dateien von geloeschten Templates entfernen, sonst bleiben sie als
        veraltete Kopien liegen und werden bei --check nie geprueft.

        Mit ``check`` wird nichts geloescht; die Namen kommen als
        ``'<name> (verwaist)'`` zurueck und zaehlen als veraltet.
        """
        gewollt = {t.name for t, _ in jobs if t.parent == out_dir}
        verwaist = [p for p in out_dir.glob('*.html') if p.name not in gewollt]
        if check:
            return [p.name + ' (verwaist)' for p in verwaist]
        for p in verwaist:
            p.unlink()
            self.stdout.write(self.style.WARNING(f'  entfernt: {p.name}'))
        return []

    def handle(self, *args, **options):
        # Wie in check_seo: Die Windows-Konsole liegt auf cp1252, die
        # Ausgabe enthaelt aber '→' und Umlaute (Befund W1).
        for strom in (sys.stdout, sys.stderr):
            try:
                strom.reconfigure(encoding='utf-8', errors='replace')
            except (AttributeError, ValueError):        # pragma: no cover
                pass

        base = Path(settings.BASE_DIR)
        css_path = base / 'static' / 'css' / 'ruempelwerk.css'
        tpl_dir = base / 'templates'
        out_dir = tpl_dir / 'components' / 'critical'
        out_dir.mkdir(parents=True, exist_ok=True)

        raw = _COMMENT_RE.sub('', css_path.read_text(encoding='utf-8'))
        full = css_path.stat().st_size
        jobs = self._jobs(tpl_dir, base / 'static' / 'js', out_dir,
                          options['body_lines'])

        stale, geschrieben, summe = [], 0, 0
        for target, klassen in jobs:
            css = _kritisches_css(raw, klassen)
            content = f'{_HEADER}{css}\n'
            old = target.read_text(encoding='utf-8') if target.exists() else ''

            if options['check']:
                if old.strip() != content.strip():
                    stale.append(target.name)
                continue

            if old != content:
                target.write_text(content, encoding='utf-8')
                geschrieben += 1
            if target.parent == out_dir:
                summe += len(css)
                self.stdout.write(
                    f'  {target.name:<26} {len(css)/1024:5.1f} KiB '
                    f'({len(css)/full*100:2.0f} %)'
                )

        stale.extend(self._verwaiste(out_dir, jobs, options['check']))

        if options['check']:
            if stale:
                raise SystemExit(
                    f'Veraltet: {", ".join(sorted(stale))} – '
                    '`python manage.py build_critical_css` ausfuehren.'
                )
            self.stdout.write(self.style.SUCCESS('Inline-CSS ist aktuell.'))
            return

        seiten = len(jobs) - 1
        self.stdout.write(self.style.SUCCESS(
            f'{seiten} Seiten, im Schnitt {summe/seiten/1024:.1f} KiB inline '
            f'(vollstaendiges CSS: {full/1024:.1f} KiB). '
            f'{geschrieben} Datei(en) geschrieben.'
        ))
