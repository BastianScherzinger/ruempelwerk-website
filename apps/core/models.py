"""Alle Models der oeffentlichen Website - Leads, Protokoll, CMS, Bewertungen.

Vier Gruppen, und die Trennung ist Absicht:

* **Leads** - ``Anfrage``, ``PreisAngebot``, ``Kooperationsanfrage``,
  ``Bewerbung``. Alle vier erben aus ``VersandStatus`` die beiden Felder
  ``mail_gewollt`` und ``mail_gesendet``, an denen der stuendliche
  Nachzuegler haengt (siehe dort, warum es zwei sein muessen).
* **Protokoll** - ``PageVisit``, ``VisitorSession``, ``DailyStats``. Die IP
  wird anonymisiert gespeichert, und geloescht wird nach Frist
  (``management/commands/pagevisit_aufraeumen.py``, 30 Tage).
* **CMS** - ``AktuellesPost`` und ``AktuellesBild``, der einzige Inhalt, der
  sich ohne Deploy aendert.
* **Bewertungen** - ``GoogleBewertung`` und ``GoogleRezension``, gefuellt vom
  Abgleich (``management/commands/sync_google_reviews.py``).
* **Betrieb** - ``Fehlerereignis``, geschrieben von der Fehlerwache
  (``apps/core/fehlerwache.py``), seit dem 16.09.2026.

Die Datei traegt ein UTF-8-BOM - eigene Skripte, die sie lesen, brauchen
``encoding='utf-8-sig'`` (``docs/fallen.md``).
"""

import logging

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

_log = logging.getLogger('apps.core')


class VersandStatus(models.Model):
    """Zwei Felder fuer den Mailversand - und warum es zwei sein muessen.

    Seit dem 06.09.2026 (P8/C3) holt ein stuendlicher Nachzuegler
    (``views._mail_nachzuegler``) Benachrichtigungen nach, die im
    Daemon-Thread verlorengegangen sind: ``daemon=True`` heisst, dass der
    Thread beim Beenden des Prozesses ohne Aufraeumen abgebrochen wird, und
    Gunicorn recycelt Worker bei jedem Deploy. Trifft das einen Thread
    zwischen ``start()`` und der Rueckkehr von ``urlopen(..., timeout=10)``,
    verschwindet die Mail **ohne Logeintrag** - der ``except``-Zweig kommt
    gar nicht mehr zum Zug.

    ``mail_gesendet`` allein reicht dafuer **nicht**. Seit P8/C1 wird auch
    eine woertlich gleiche Wiederholung gespeichert (kein Lead darf
    stillschweigend verschwinden), und wenn die Notbremse
    ``antispam.mail_budget_ok()`` zuschlaegt, ist das Ausbleiben der Mail eine
    **Entscheidung**, kein Ausfall. Ein Nachzuegler, der nur auf
    ``mail_gesendet=False`` sieht, hoebe beide Entscheidungen wieder auf und
    stellte genau das zu, was gerade unterdrueckt worden ist.

    Deshalb:

    * ``mail_gewollt``  - war fuer diesen Datensatz ueberhaupt eine
      Benachrichtigung vorgesehen? ``False`` bei Duplikat und bei
      erschoepftem Mail-Budget.
    * ``mail_gesendet`` - ist sie tatsaechlich rausgegangen?

    Der Nachzuegler nimmt ausschliesslich ``mail_gewollt=True`` **und**
    ``mail_gesendet=False``.
    """

    mail_gewollt = models.BooleanField(
        default=True, verbose_name='Benachrichtigung vorgesehen')
    mail_gesendet = models.BooleanField(
        default=False, verbose_name='Benachrichtigung gesendet')
    # Seit 24.09.2026 (Migration 0020): der Telegram-Push, unabhaengig von der
    # Mail. Er haengt an derselben Entscheidung ``mail_gewollt`` - kein Push
    # fuer Duplikat, Notbremse oder Verdacht -, wird aber getrennt vermerkt
    # und getrennt nachgeholt (``views._push_nachzuegler``): Ein
    # Telegram-Ausfall darf den Mailversand nie aufhalten und umgekehrt.
    push_gesendet = models.BooleanField(
        default=False, verbose_name='Telegram-Push gesendet')

    class Meta:
        abstract = True


class Anfrage(VersandStatus):
    """Eine Anfrage ueber ``/anfrage/`` - der Hauptweg fuer Auftraege.

    Pflicht sind Leistungsart, Name und E-Mail; Telefon, Adresse und Freitext
    sind freiwillig. Geloescht wird nach 730 Tagen
    (``management/commands/leads_aufraeumen.py``), und der Mailversand haengt
    an den beiden geerbten Feldern aus ``VersandStatus``.
    """

    LEISTUNG_CHOICES = [
        ('entruempelung', 'Entrümpelung'),
        ('sanierung', 'Sanierung & Reparatur'),
        ('komplett', 'Komplett-Paket (Entrümpelung + Sanierung)'),
        ('sonstiges', 'Sonstiges'),
    ]

    leistung = models.CharField(max_length=50, choices=LEISTUNG_CHOICES, verbose_name='Leistungsart')
    zusatz_info = models.TextField(blank=True, verbose_name='Zusätzliche Informationen')
    name = models.CharField(max_length=200, verbose_name='Name')
    email = models.EmailField(verbose_name='E-Mail')
    telefon = models.CharField(max_length=50, blank=True, verbose_name='Telefonnummer')
    adresse = models.CharField(max_length=500, blank=True, verbose_name='Adresse des Objekts')
    erstellt_am = models.DateTimeField(auto_now_add=True)
    # Variante A der Grenzfaelle (24.09.2026): Eine
    # Einsendung mit Score 5-9 ohne harte Botmerkmale wird nicht mehr still
    # verworfen, sondern als Verdacht gespeichert - IMMER mit
    # ``mail_gewollt=False`` (sonst stellte der Nachzuegler sie zu), sichtbar
    # im Dashboard, geloescht nach ``views.VERDACHT_AUFBEWAHRUNG_TAGE``.
    verdacht = models.BooleanField(
        default=False, verbose_name='Spamverdacht',
        help_text='Grenzfall der Spam-Abwehr: gespeichert, aber ohne Mail und Push.')

    class Meta:
        ordering = ['-erstellt_am']
        verbose_name = 'Anfrage'
        verbose_name_plural = 'Anfragen'

    def __str__(self):
        return f'{self.name} – {self.get_leistung_display()} – {self.erstellt_am:%Y-%m-%d %H:%M}'


class PreisAngebot(VersandStatus):
    """Ein abgeschlossener Durchgang des Preisrechners (``/preisangebot/``).

    ``pmin``/``pmax`` sind die **gerechnete** Spanne aus
    ``data/pricing.py::berechne_preis`` - sie wird gespeichert, weil sich die
    Preistabelle aendern kann und ein spaeteres Nachrechnen sonst eine andere
    Zahl ergaebe als die, die der Kunde gesehen hat. ``erinnerung_gesendet``
    gehoert zum stuendlichen Nachfassen (``views.send_due_reminders``).
    """

    name           = models.CharField(max_length=200, verbose_name='Name')
    email          = models.EmailField(verbose_name='E-Mail')
    leistung_label = models.CharField(max_length=300, verbose_name='Leistung')
    groesse_label  = models.CharField(max_length=500, blank=True, verbose_name='Größe / Positionen')
    pmin           = models.PositiveIntegerField(verbose_name='Preis min (€)')
    pmax           = models.PositiveIntegerField(verbose_name='Preis max (€)')
    erstellt_am    = models.DateTimeField(auto_now_add=True, verbose_name='Erstellt')
    erinnerung_gesendet = models.BooleanField(default=False, verbose_name='Erinnerung gesendet')
    # Der Ort aus dem Rechner (Feld ``stadtort``). ⚠ Die Produktionsdatenbank
    # trug eine Spalte ``ort`` (NOT NULL) aus der Vorlage, von der dieses
    # Model nichts wusste - JEDE Rechner-Einsendung endete deshalb bis zum
    # 24.09.2026 in einem IntegrityError und einem 500. Migration 0020 legt
    # das Feld nur an, wo die Spalte fehlt, und nimmt fremden Pflichtspalten
    # das NOT NULL.
    ort = models.CharField(max_length=100, blank=True, default='',
                           verbose_name='Ort (Rechner)')

    class Meta:
        ordering = ['-erstellt_am']
        verbose_name = 'Preisangebot'
        verbose_name_plural = 'Preisangebote'

    def __str__(self):
        return f'{self.name} – {self.leistung_label} – {self.pmin}–{self.pmax} € – {self.erstellt_am:%Y-%m-%d %H:%M}'


class Kooperationsanfrage(VersandStatus):
    """Eine Anfrage ueber ``/kooperationspartner/`` - Partner, nicht Kunden.

    Dieselbe Frist und derselbe Versandweg wie bei ``Anfrage``; getrennt
    gehalten, weil die Mail an den Betrieb anders aussieht und die Auswertung
    beide Sorten nie vermischen soll.
    """

    ART_CHOICES = [
        ('subunternehmer', 'Subunternehmer / Nachunternehmer'),
        ('handwerker', 'Handwerker-Partner'),
        ('immobilien', 'Immobilienverwaltung / Verwalter'),
        ('makler', 'Makler / Immobilienmakler'),
        ('sonstiges', 'Sonstiges'),
    ]
    name     = models.CharField(max_length=200, verbose_name='Name')
    firma    = models.CharField(max_length=200, verbose_name='Firmenname')
    email    = models.EmailField(verbose_name='E-Mail')
    telefon  = models.CharField(max_length=50, blank=True, verbose_name='Telefon')
    art      = models.CharField(max_length=50, choices=ART_CHOICES, verbose_name='Art der Kooperation')
    nachricht = models.TextField(blank=True, verbose_name='Nachricht')
    erstellt_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-erstellt_am']
        verbose_name = 'Kooperationsanfrage'
        verbose_name_plural = 'Kooperationsanfragen'

    def __str__(self):
        return f'{self.name} ({self.firma}) – {self.get_art_display()} – {self.erstellt_am:%Y-%m-%d %H:%M}'


class Bewerbung(VersandStatus):
    """Eine Bewerbung ueber ``/jobs/`` oder eine der drei Stellenseiten.

    **Warum es dieses Model gibt (P8/C2, 06.09.2026).** Bis dahin existierte
    eine Bewerbung ausschliesslich als E-Mail. Fuer ``Anfrage``,
    ``PreisAngebot`` und ``Kooperationsanfrage`` galt seit jeher das
    Gegenteil, und der Kommentar in ``views.anfrage()`` sagt auch warum:
    *"Die Anfrage steht jetzt in der Datenbank und im Dashboard. Faellt die
    Mail dem Budget zum Opfer, geht der Lead also nicht verloren."* Fuer
    Bewerbungen gab es diesen zweiten Weg nicht - und die Mail hing an drei
    Bedingungen, die alle stillschweigend scheitern koennen:
    ``mail_budget_ok()`` (60 Mails am Tag ueber **alle** Formulare),
    ein gesetzter ``RESEND_API_KEY`` (sonst nur ein ``logger.warning``) und
    ein Thread, der den naechsten Deploy ueberlebt (P8/C3).

    **``stelle`` traegt zwei Sorten Wert, und das ist Absicht.** Ueber eine
    der drei Stellenseiten kommt der **Slug** (``entruempelungshelfer``), auf
    ``/jobs/`` tippt der Bewerber seine Wunschposition selbst. Beides in ein
    Feld zu legen ist ehrlicher als ein zweites, meistens leeres: Was der
    Bewerber geschrieben hat, wird nicht in ein Schema gepresst, das es nicht
    gibt. Fuer die Anzeige loest :meth:`stelle_anzeige` den Slug in den
    Stellentitel auf - und erfindet nichts, wenn er unbekannt ist.

    **Aufbewahrung.** Bewerberdaten sind nach Paragraph 26 BDSG eine eigene
    Kategorie mit eigener Frist: sechs Monate nach Abschluss des Verfahrens
    (wegen Paragraph 15 AGG). Die Frist steht im Abschnitt "Bewerbungen" der
    Datenschutzerklaerung; eingehalten wird sie von ``leads_aufraeumen``.
    **Wer dieses Model anlegt, ohne es dort einzutragen, tauscht ein
    Datenverlustproblem gegen ein Aufbewahrungsproblem** - genau der Befund
    P8/A3, nur umgekehrt.
    """

    stelle = models.CharField(
        max_length=300, verbose_name='Stelle',
        help_text='Slug der Stellenseite oder die frei eingegebene '
                  'Wunschposition von /jobs/.')
    name = models.CharField(max_length=200, verbose_name='Name')
    email = models.EmailField(verbose_name='E-Mail')
    telefon = models.CharField(max_length=50, blank=True,
                               verbose_name='Telefonnummer')
    nachricht = models.TextField(blank=True, verbose_name='Nachricht')
    erstellt_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-erstellt_am']
        verbose_name = 'Bewerbung'
        verbose_name_plural = 'Bewerbungen'

    def __str__(self):
        return f'{self.name} – {self.stelle_anzeige()} – {self.erstellt_am:%Y-%m-%d %H:%M}'

    def stelle_anzeige(self):
        """Der lesbare Stellentitel - und nie eine Erfindung.

        Der Import steht bewusst in der Funktion: ``data/jobs.py`` darf nichts
        aus ``apps.core`` importieren (Regel 4), und ein Modulimport in die
        andere Richtung zoege die Datenmodule beim Laden der Models mit hoch.
        Ist der Slug unbekannt - eine geloeschte Stelle, oder der Freitext von
        ``/jobs/`` -, wird der gespeicherte Wert unveraendert gezeigt.
        """
        from .data.jobs import _JOB_DATA
        eintrag = _JOB_DATA.get(self.stelle)
        return eintrag['title'] if eintrag else self.stelle


class PageVisit(models.Model):
    """Das eigene Besuchsprotokoll - eine Zeile je GET mit Status 200.

    **Warum ``timestamp`` seit dem 06.09.2026 einen Index traegt (P8/E1).**
    ``ordering = ['-timestamp']`` galt seit jeher, ein Index dazu nie. Jede
    Anzeige im Django-Admin (``list_display``, ``list_filter``) und jeder Lauf
    von ``pagevisit_aufraeumen`` (``filter(timestamp__lt=...)``) sortiert bzw.
    filtert damit ueber die ungeordnete Tabelle. Solange sie klein war, fiel
    das nicht auf; sie waechst aber mit jedem Seitenaufruf, und der einzige
    Grund, warum sie nicht unbegrenzt waechst, ist die 30-Tage-Loeschung aus
    A2/A3 - die selbst wieder ueber ``timestamp`` filtert.

    **Warum ``path`` bewusst KEINEN Index bekommen hat.** Es gibt keine
    Abfrage, die nach einem Pfad filtert. Die einzige Stelle, die ``path``
    ueberhaupt sucht, ist ``search_fields`` im Admin - und das erzeugt ein
    ``LIKE '%…%'``, das ein B-Tree-Index nicht bedienen kann. Ein Index dort
    kostete bei jedem Insert Schreibarbeit und braechte nichts. Wer eine
    Auswertung nach Pfad baut (z. B. "welche Seite holt der Crawler wie oft?"),
    traegt ihn dann nach - mit der Abfrage als Beleg.

    **Warum Bots weiter gespeichert werden - und nur markiert (P8/E1, Punkt 2).**
    Der Plan liess die Wahl zwischen "Bots gar nicht erst schreiben" und "ein
    Feld ``ist_bot``". Gemessen am 06.09.2026, bevor entschieden wurde:

    * Das interne Dashboard unter ``STATS_PATH`` (``apps/stats/views.py``)
      liest ``PageVisit`` **gar nicht** - es aggregiert ``VisitorSession`` und
      ``DailyStats``. Und dort sind Bots **schon immer** ausgenommen
      (``middleware.py``: ``if not _is_bot(ua) and consent == 'all'``). Die
      Besucherzahl, die der Betrieb liest, haengt also nicht an dieser Tabelle.
    * Die einzige Stelle, die eine ``PageVisit``-Zahl anzeigt, ist das
      Auth-Altbestands-Dashboard ``apps/dashboard`` - und dessen Adresse
      ``/dashboard/`` wird vom City-Catch-All verschluckt (Regel 5):
      ``resolve('/dashboard/')`` landet auf ``city_landing_page`` mit
      ``city_slug='dashboard'`` und endet in einem 404. Die Zahl ist heute
      also fuer niemanden sichtbar.

    Ein Filter waere damit gefahrlos gewesen - er haette aber Daten
    vernichtet, die dieses Projekt gebrauchen kann: **Dies ist das einzige
    Crawl-Protokoll, das die Seite hat.** Die Search Console sagt nicht, wann
    welcher Bot welche der 85 Seiten geholt hat; diese Tabelle sagt es. Und
    ``GPTBot``/``PerplexityBot``/``ClaudeBot`` tauchen in der GSC ueberhaupt
    nicht auf. Deshalb: markieren statt wegwerfen. Die Menge bleibt durch die
    30-Tage-Loeschung begrenzt, nicht durch das Wegwerfen von Evidenz.

    **Was dieses Feld nicht leistet:** ``_is_bot()`` erkennt Bots am
    User-Agent, und ein User-Agent ist eine Behauptung. Ein Scraper, der sich
    als Chrome ausgibt, steht hier als Mensch; ein Mensch mit ``curl`` steht
    als Bot. Die Zahl taugt fuer Groessenordnungen, nicht fuer Beweise.
    """

    path = models.CharField(max_length=512)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ist_bot = models.BooleanField(
        default=False, verbose_name='Bot (laut User-Agent)')

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Seitenaufruf'
        verbose_name_plural = 'Seitenaufrufe'

    def __str__(self):
        return f'{self.path} – {self.timestamp:%Y-%m-%d %H:%M}'


class VisitorSession(models.Model):
    """One row per browser session (identified by rwsid cookie) per day."""
    session_id  = models.CharField(max_length=32, db_index=True)
    date        = models.DateField(db_index=True)
    ip_hash     = models.CharField(max_length=40, blank=True)
    started_at  = models.DateTimeField()
    last_seen   = models.DateTimeField()
    page_count  = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['session_id', 'date'], name='unique_session_per_day'),
        ]
        ordering = ['-date', '-started_at']
        verbose_name = 'Besucher-Session'
        verbose_name_plural = 'Besucher-Sessions'

    def __str__(self):
        return f'{self.date} – {self.session_id[:8]} – {self.page_count} Seiten'


class DailyStats(models.Model):
    """Aggregated visitor statistics per calendar day."""
    date             = models.DateField(unique=True)
    unique_visitors  = models.PositiveIntegerField(default=0)
    total_sessions   = models.PositiveIntegerField(default=0)
    total_pageviews  = models.PositiveIntegerField(default=0)
    avg_session_seconds = models.PositiveIntegerField(default=0)
    email_sent       = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Tagesstatistik'
        verbose_name_plural = 'Tagesstatistiken'

    def __str__(self):
        return f'{self.date} – {self.unique_visitors} Besucher'


def _aktuelles_upload_path(instance, filename):
    import uuid, os
    ext = os.path.splitext(filename)[1].lower()
    return f'aktuelles/{uuid.uuid4().hex}{ext}'


def _validate_image(file):
    from django.core.exceptions import ValidationError
    # Only enforce size limit — Django's ImageField + Pillow already verifies
    # the file is a valid image. MIME-type strings from browsers are inconsistent
    # (e.g. 'image/jpg' vs the canonical 'image/jpeg') and caused false rejections.
    max_bytes = 8 * 1024 * 1024  # 8 MB
    size = getattr(file, 'size', None)
    if size and size > max_bytes:
        raise ValidationError('Bild darf maximal 8 MB groß sein.')


AUTOR_CHOICES = [
    ('oliver',    'Oliver Pohl'),
    ('christoph', 'Christoph Regner'),
    ('viktor',    'Viktor Grebe'),
]

# Die _sm-Variante ist 128x125 px / ~2,6 KB. Angezeigt werden die Bilder mit
# 30 px (/aktuelles/) bzw. 56 px (CMS-Formular) – die frueher hier eingetragenen
# .jpeg-Originale sind 500x490 px / ~33 KB und wurden auf /aktuelles/ dreimal
# geladen. Bei neuen Regionalleitern ebenfalls die _sm.webp eintragen.
# 'breite'/'hoehe' sind die ECHTEN Dateimasse, nicht die Anzeigegroesse.
# check_seo gleicht jedes width/height gegen die Datei ab; ohne die Werte hier
# muesste jedes Template sie abtippen - und beim naechsten Bildtausch stuende
# die falsche Zahl an vier Stellen. Christoph Regner hat noch kein Foto.
# 'rolle' ist die sichtbare Funktion (Oliver = Inhaber, 01.10.2026).
AUTOR_META = {
    'oliver':    {'name': 'Oliver Pohl',           'region': 'Leipzig & Halle', 'rolle': 'Inhaber · Leipzig & Halle',
                  'foto': 'images/regionalleiter_leipzig_sm.webp',  'breite': 128, 'hoehe': 125},
    'christoph': {'name': 'Christoph Regner',      'region': 'Magdeburg', 'rolle': 'Regionalleiter Magdeburg',
                  'foto': None,                                     'breite': 0,   'hoehe': 0},
    'viktor':    {'name': 'Viktor Grebe',          'region': 'Dresden & Chemnitz', 'rolle': 'Regionalleiter Dresden & Chemnitz',
                  'foto': 'images/regionalleiter_dresden_sm.webp',  'breite': 128, 'hoehe': 178},
}

GALERIE_MAX_BILDER = 50


class AktuellesPost(models.Model):
    """Ein Beitrag aus dem CMS - der einzige Inhalt ohne Deploy.

    Drei Sorten: ``bericht``, ``zitat`` und ``vorher_nachher``. Sichtbar wird
    ein Beitrag erst mit ``veroeffentlicht=True``; davon haengen ausserdem das
    ``lastmod`` von ``/aktuelles/`` und ``/galerie/``
    (``sitemaps.lastmod_fuer_pfad``), der RSS-Feed (``feeds.py``) und das
    ``BlogPosting`` im Schema ab. ``datum`` ist das Datum des Auftrags und
    wird vom CMS gesetzt, ``erstellt_am`` das der Veroeffentlichung.
    """

    TYP_CHOICES = [
        ('bericht',        'Bericht'),
        ('zitat',          'Zitat'),
        ('vorher_nachher', 'Vorher / Nachher'),
    ]

    typ             = models.CharField(max_length=20, choices=TYP_CHOICES, verbose_name='Typ')
    titel           = models.CharField(max_length=300, verbose_name='Titel')
    inhalt          = models.TextField(blank=True, verbose_name='Text / Inhalt')
    zitat_autor     = models.CharField(max_length=200, blank=True, verbose_name='Zitatautor')
    autor           = models.CharField(max_length=20, choices=AUTOR_CHOICES, blank=True, verbose_name='Autor')
    bild_vor        = models.ImageField(upload_to=_aktuelles_upload_path, blank=True, null=True,
                                        validators=[_validate_image], verbose_name='Bild Vorher')
    bild_nach       = models.ImageField(upload_to=_aktuelles_upload_path, blank=True, null=True,
                                        validators=[_validate_image], verbose_name='Bild Nachher')
    veroeffentlicht = models.BooleanField(default=False, verbose_name='Veröffentlicht')
    datum           = models.DateField(verbose_name='Datum')
    erstellt_am     = models.DateTimeField(auto_now_add=True)
    # Migration 0023 (Bauplan §7): fuer die Einzelseite /aktuelles/<jahr>/<slug>/.
    # Blank/leer heisst: dieser Beitrag hat (noch) keine eigene Seite - er
    # erscheint dann weiter nur in der Liste /aktuelles/, wie bisher.
    slug            = models.SlugField(max_length=220, blank=True, default='',
                                       verbose_name='Adresse (Slug)')

    class Meta:
        ordering = ['-datum', '-erstellt_am']
        verbose_name = 'Aktuelles'
        verbose_name_plural = 'Aktuelles'

    def __str__(self):
        return f'{self.get_typ_display()} – {self.titel} – {self.datum}'


class AktuellesBild(models.Model):
    """Gallery images attached to a Bericht or Zitat post (up to 10 per post)."""
    post        = models.ForeignKey(AktuellesPost, on_delete=models.CASCADE, related_name='bilder')
    bild        = models.ImageField(upload_to=_aktuelles_upload_path, verbose_name='Bild')
    typ_bild    = models.CharField(
        max_length=4, blank=True, default='',
        choices=[('vor', 'Vorher'), ('nach', 'Nachher')],
        verbose_name='Typ',
    )
    # Bildbeschreibung = alt-Text. Sie ist der einzige Weg, wie Google und die
    # Bildersuche erfahren, was auf dem Foto zu sehen ist - und der einzige,
    # wie Blinde es erfahren. Ort und Leistung gehoeren hinein
    # ("Haushaltsaufloesung in Halle-Neustadt, Kueche vor der Raeumung").
    #
    # Bewusst optional: Ein Pflichtfeld haette den Upload blockiert und dazu
    # gefuehrt, dass irgendetwas hineingetippt wird. Fehlt der Text, faellt die
    # Ausgabe auf eine neutrale Beschreibung zurueck - und das CMS zeigt an,
    # wie viele Bilder noch keinen haben, damit es nachtraeglich nachgeholt wird.
    bildtext = models.CharField(
        max_length=180, blank=True, default='',
        verbose_name='Bildbeschreibung',
        help_text='Was ist zu sehen? Mit Ort und Leistung, z. B. '
                  '"Haushaltsauflösung in Halle-Neustadt, Küche vor der Räumung".',
    )
    reihenfolge = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['reihenfolge', 'pk']
        verbose_name = 'Post-Bild'
        verbose_name_plural = 'Post-Bilder'

    def __str__(self):
        return f'Bild #{self.pk} zu {self.post}'

    def alt_text(self, nummer=None, gesamt=None):
        """Der alt-Text fuers Markup. Nie leer, nie erfunden.

        Ohne Beschreibung wird nur gesagt, was sicher stimmt: die Leistung aus
        dem Beitrag und ob es ein Vorher- oder Nachher-Bild ist. Einen Ort zu
        raten waere schlimmer als ihn wegzulassen.

        ``nummer``/``gesamt`` haengen eine Positionsangabe an - **aber nur,
        wenn derselbe Text im selben Beitrag mehrfach vorkommt**. Wer das
        entscheidet, ist ``alt_texte()``; ein einzelnes Bild kann es nicht
        wissen, es kennt seine Geschwister nicht.

        WARUM DAS NOETIG IST (IS25, 12.09.2026)
        ---------------------------------------
        Zwei Wege fuehren dazu, dass ein Beitrag zehn Bilder mit **einer**
        Zeichenkette ausliefert, und beide sind Normalbetrieb:

        1. Der Rueckfall oben. Ohne ``bildtext`` heissen alle Bilder eines
           Beitrags gleich - der Beitragstitel.
        2. ``apps/stats/views.py::_add_bilder`` schreibt die
           Sammelbeschreibung eines Uploads in **jedes** Bild des Stapels.
           Das ist gewollt (ein Text fuer zehn Fotos ist besser als keiner),
           erzeugt aber dieselbe Wiederholung.

        Fuer die Bildersuche und fuer einen Screenreader ist das derselbe
        Schaden: zehn Bilder, die sich nicht unterscheiden lassen. Die
        Positionsangabe loest das nicht inhaltlich - was auf Bild 7 zu sehen
        ist, weiss nur, wer dabei war -, aber sie macht die Bilder
        unterscheidbar und sagt dabei nichts Falsches.
        """
        if self.bildtext.strip():
            basis = self.bildtext.strip()
        else:
            stufe = {'vor': ' – vorher', 'nach': ' – nachher'}.get(self.typ_bild, '')
            basis = f'{self.post.titel}{stufe}'.strip()
        if nummer and gesamt and gesamt > 1:
            return f'{basis}, Bild {nummer} von {gesamt}'
        return basis

    @classmethod
    def alt_texte(cls, bilder, vollstaendig=False):
        """``{pk: alt-Text}`` fuer eine Menge Bilder - Dopplungen nummeriert.

        **Die einzige Stelle, die entscheidet, ob ein Bild eine Nummer
        bekommt.** Seite, Startseite, Leistungsseiten und die Bildsitemap
        fragen alle hier, damit dieselbe Bildadresse ueberall dieselbe
        Zeichenkette traegt - ``sitemaps.galerie_bild_liste`` sagt das
        ausdruecklich zu, und zwei Rechenwege fuer denselben Satz laufen
        auseinander (Regel 12).

        ``vollstaendig=True`` heisst: ``bilder`` enthaelt bereits **alle**
        Bilder der betroffenen Beitraege (so ruft ``_enrich_posts`` auf, das
        sie ohnehin geladen hat). Sonst werden die Geschwister nachgeladen -
        eine Abfrage, und sie ist noetig: ``/galerie/`` blaettert, und ohne
        die Geschwister hiesse dasselbe Bild auf Seite 2 "Bild 1 von 4" und
        in der Bildsitemap "Bild 9 von 12".

        WAS DIESE METHODE NICHT LEISTET
        -------------------------------
        * **Sie macht keinen alt-Text gut.** Sie macht zehn gleiche
          unterscheidbar. Was auf dem Foto zu sehen ist, steht danach immer
          noch nur dort, wo es jemand eingetragen hat (``bildtext``, im CMS).
        * **Sie erkennt keine Aehnlichkeit.** "Kueche vorher" und "Kueche
          vorher!" sind fuer sie zwei Texte. Absicht: Wer zwei Bilder
          unterschiedlich benannt hat, hat sie unterschieden.
        """
        bilder = list(bilder)
        if not bilder:
            return {}
        gruppe = bilder
        if not vollstaendig:
            try:
                gruppe = list(cls.objects
                              .filter(post_id__in={b.post_id for b in bilder})
                              .select_related('post')
                              .order_by('post_id', 'reihenfolge', 'pk'))
            except Exception:      # noqa: BLE001
                # Ein alt-Text ohne Nummer ist besser als eine Seite mit 500.
                # Still darf es nicht sein - sonst sieht die fehlende
                # Nummerierung wie eine Entscheidung aus.
                _log.warning('Geschwisterbilder nicht ladbar - alt-Texte '
                             'bleiben ohne Positionsangabe', exc_info=True)
                gruppe = bilder
        roh = {b.pk: b.alt_text() for b in gruppe}
        stapel = {}
        for b in gruppe:
            stapel.setdefault((b.post_id, roh[b.pk]), []).append(b)
        nummern = {}
        for gleiche in stapel.values():
            if len(gleiche) > 1:
                for i, b in enumerate(gleiche, 1):
                    nummern[b.pk] = (i, len(gleiche))
        return {b.pk: (b.alt_text(*nummern[b.pk]) if b.pk in nummern
                       else roh.get(b.pk) or b.alt_text())
                for b in bilder}


# ── Google-Bewertungen ───────────────────────────────────────────────────────
#
# Warum das in der Datenbank liegt und nicht als Konstante im Code: Der Wert
# aendert sich, ohne dass jemand etwas deployt. Vorher stand "5.0 bei 8" im
# Template, wahr war "4.9 bei 18" – die Zahl war beim Eintippen richtig und
# danach zwei Jahre lang falsch. Gefuellt wird beides vom Management-Command
# ``sync_google_reviews`` (naechtlich, siehe ``apps/core/apps.py``).


class GoogleBewertung(models.Model):
    """Der Gesamtstand aus dem Google-Profil – genau eine Zeile.

    ``singleton`` ist ein konstantes True mit ``unique=True``: Damit kann eine
    zweite Zeile gar nicht erst entstehen, auch nicht, wenn zwei gunicorn-Worker
    gleichzeitig synchronisieren. Ein ``get_or_create`` auf ein Feld ohne
    Eindeutigkeit haette hier eine Wettlaufsituation.
    """

    singleton = models.BooleanField(default=True, unique=True, editable=False)
    wert = models.DecimalField(max_digits=2, decimal_places=1,
                               verbose_name='Durchschnitt')
    anzahl = models.PositiveIntegerField(verbose_name='Anzahl Bewertungen')
    place_id = models.CharField(max_length=200, blank=True)
    profil_url = models.URLField(blank=True, max_length=500)
    geprueft_am = models.DateTimeField(verbose_name='Zuletzt abgeglichen')

    class Meta:
        verbose_name = 'Google-Bewertung (Gesamtstand)'
        verbose_name_plural = 'Google-Bewertung (Gesamtstand)'

    def __str__(self):
        return f'{self.wert} bei {self.anzahl} Bewertungen'

    @property
    def wert_txt(self):
        """Fuers Schema: immer mit Punkt, nie mit Komma.

        ``str(Decimal)`` waere hier zufaellig richtig, aber ein ``floatformat``
        im Template waere es nicht – ``USE_I18N`` macht daraus ``4,9`` und
        damit ungueltiges JSON. Dieselbe Fehlerklasse wie bei den Koordinaten.
        """
        return f'{self.wert:.1f}'


class GoogleRezension(models.Model):
    """Eine einzelne Rezension.

    ``quelle_id`` ist die Kennung aus der Places API. Die sechs Rezensionen,
    die vor diesem Sync von Hand im Markup standen, haben keine – sie tragen
    ``uebernommen:<name>`` und bekommen die echte Kennung beim ersten Abgleich,
    der sie wiederfindet.

    ``zuletzt_gesehen`` ist bewusst **kein** Ablaufdatum. Die API liefert nur
    fuenf Rezensionen; eine, die heute nicht dabei ist, kann geloescht worden
    oder einfach nicht unter den Top 5 sein. Diese beiden Faelle sind von
    aussen nicht unterscheidbar, also wird nichts automatisch entfernt.
    """

    quelle_id = models.CharField(max_length=300, unique=True)
    name = models.CharField(max_length=120, verbose_name='Autor')
    initialen = models.CharField(max_length=4)
    sterne = models.PositiveSmallIntegerField()
    text = models.TextField()
    profil_url = models.URLField(blank=True, max_length=500)
    relativ = models.CharField(max_length=60, blank=True,
                               verbose_name='Zeitangabe („vor 3 Monaten“)')
    veroeffentlicht = models.DateTimeField(null=True, blank=True)
    sichtbar = models.BooleanField(default=True)
    zuletzt_gesehen = models.DateTimeField()
    angelegt_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        # ``nulls_last`` ist hier kein Detail: Die sechs von Hand uebernommenen
        # Rezensionen haben kein ``veroeffentlicht`` (Google zeigt im Profil nur
        # "vor 3 Monaten"). PostgreSQL sortiert NULL bei DESC nach vorn - die
        # aeltesten Eintraege haetten damit dauerhaft die besten Plaetze belegt
        # und die frisch abgeglichenen nach hinten gedraengt. Genau das ist beim
        # ersten Lauf am 14.08.2026 passiert.
        ordering = [models.F('veroeffentlicht').desc(nulls_last=True),
                    '-angelegt_am']
        verbose_name = 'Google-Rezension'
        verbose_name_plural = 'Google-Rezensionen'

    def __str__(self):
        return f'{self.name} ({self.sterne}★)'


# ── Bilddateien beim Loeschen mit aufraeumen ─────────────────────────────────
#
# Django loescht beim Entfernen eines Datensatzes nur die Zeile, nie die Datei.
# Ueber Cloudinary kostet jedes zurueckgebliebene Bild dauerhaft Speicher; beim
# Test am 12.08.2026 lagen nach einem geloeschten Beitrag vier JPEGs weiter da.
#
# Drei Vorkehrungen, weil das Loeschen einer entfernten Datei nicht umkehrbar
# ist und hier echte Kundeninhalte haengen:
#
#   1. Der Aufraeumer laeuft ausschliesslich als Reaktion auf ein tatsaechlich
#      geloeschtes Objekt. Er sucht von sich aus nie nach "Ueberfluessigem".
#   2. Er feuert erst in transaction.on_commit(). Bricht die Loeschung ab oder
#      wird die Transaktion zurueckgerollt, bleibt die Datei liegen – eine
#      verwaiste Datei ist harmlos, ein Beitrag ohne seine Bilder nicht.
#   3. Vorher wird geprueft, ob noch ein anderer Datensatz denselben Dateinamen
#      fuehrt. Bei den zufaelligen Namen aus _aktuelles_upload_path ist das die
#      Ausnahme, aber ein Duplikat wuerde sonst ein fremdes Bild mitreissen.
#
# Fehler werden geloggt und geschluckt: Ein Ausfall der Speicher-API darf das
# Loeschen im CMS nicht scheitern lassen.

def _datei_noch_referenziert(name: str) -> bool:
    """True, wenn irgendein anderer Datensatz dieselbe Datei fuehrt."""
    return (
        AktuellesBild.objects.filter(bild=name).exists()
        or AktuellesPost.objects.filter(bild_vor=name).exists()
        or AktuellesPost.objects.filter(bild_nach=name).exists()
    )


def _datei_aufraeumen(*fieldfiles):
    """Entfernt die Dateien hinter den uebergebenen Feldern nach dem Commit."""
    from django.db import transaction

    # Namen jetzt einsammeln – nach dem Commit ist die Instanz ggf. weg.
    namen = [(f, f.name) for f in fieldfiles if getattr(f, 'name', '')]
    if not namen:
        return

    def _loeschen():
        for fieldfile, name in namen:
            try:
                if _datei_noch_referenziert(name):
                    _log.info('Datei %s bleibt – noch von einem Datensatz benutzt', name)
                    continue
                fieldfile.delete(save=False)
                _log.info('Verwaiste Bilddatei entfernt: %s', name)
            except Exception as exc:
                _log.warning('Bilddatei %s konnte nicht entfernt werden: %s', name, exc)

    transaction.on_commit(_loeschen)


@receiver(post_delete, sender=AktuellesBild)
def _aktuellesbild_geloescht(sender, instance, **kwargs):
    _datei_aufraeumen(instance.bild)


@receiver(post_delete, sender=AktuellesPost)
def _aktuellespost_geloescht(sender, instance, **kwargs):
    # Die zugehoerigen AktuellesBild-Zeilen raeumt der Kaskaden-Delete ab und
    # loest dabei den Empfaenger darueber aus – hier bleiben nur die beiden
    # Alt-Felder des Models.
    _datei_aufraeumen(instance.bild_vor, instance.bild_nach)


class Fehlerereignis(models.Model):
    """Ein Fehler der Website, zusammengefasst ueber alle Wiederholungen (VL19).

    Geschrieben von ``fehlerwache.FehlerwacheHandler``, gemeldet von
    ``fehlerwache.fehler_melden()``, geloescht nach ``AUFBEWAHRUNG_TAGE`` ohne
    neues Auftreten. **Keine Personendaten:** kein Request-Rumpf, keine IP;
    Mailadressen und IPs im Text sind vor dem Speichern ersetzt.

    ``gemeldet_bis`` ist der ``zuletzt``-Stand, ueber den schon eine Mail
    rausging. Kommt der Fehler danach wieder, ist ``zuletzt`` groesser - und
    der naechste Durchlauf meldet ihn erneut, einmal.
    """

    kennung = models.CharField(max_length=40, unique=True)
    quelle = models.CharField('Logger', max_length=100)
    art = models.CharField('Fehlerart', max_length=120)
    meldung = models.CharField(max_length=500, blank=True)
    ort = models.CharField('Stelle im Code', max_length=200, blank=True)
    pfad = models.CharField(max_length=300, blank=True)
    methode = models.CharField(max_length=10, blank=True)
    verlauf = models.TextField('Stacktrace', blank=True)
    anzahl = models.PositiveIntegerField(default=1)
    erstmals = models.DateTimeField()
    zuletzt = models.DateTimeField(db_index=True)
    gemeldet_bis = models.DateTimeField(null=True, blank=True)
    erledigt = models.BooleanField(default=False)

    class Meta:
        ordering = ['-zuletzt']
        verbose_name = 'Fehlerereignis'
        verbose_name_plural = 'Fehlerereignisse'

    def __str__(self):
        return f'{self.art} in {self.ort or self.quelle} ({self.anzahl}x)'


# ── Terminbuchung (Migration 0022, Bauplan §5) ──────────────────────────────
#
# Drei NEUE Tabellen - die geteilte Supabase-Datenbank traegt auch RTC, und
# Migration 0022 darf deshalb keine Spalte einer fremden Tabelle anfassen
# (docs/fallen.md, "Migrationen treffen RTC mit"). Alle drei Models sind
# eigenstaendig und ohne Fremdschluessel auf irgendetwas ausserhalb dieses Apps.


class Terminvorlage(models.Model):
    """Die Wochenvorlage: welche Uhrzeiten sind an welchem Wochentag offen.

    ``wochentag`` folgt Pythons ``date.weekday()`` (0 = Montag ... 5 = Samstag).
    Sonntag hat bewusst KEINE Zeile - Sonntage sind immer geschlossen, das
    steht nicht in der Wochenvorlage, weil Oliver es sonst versehentlich
    aendern koennte (Bauplan §5: "Sonn- und Feiertage sind geschlossen").

    Fehlt fuer einen Wochentag eine (aktive) Zeile, greift der Fallback in
    ``apps/core/termine.py`` (Mo-Sa 08/10/12/14/16 Uhr) - die Website bleibt
    also auch ohne gepflegte Vorlage buchbar, und Migration 0022 legt die
    Standardvorlage zusaetzlich als echte Datenzeilen an (Datenmigration).
    """

    MONTAG, DIENSTAG, MITTWOCH, DONNERSTAG, FREITAG, SAMSTAG = range(6)
    WOCHENTAG_CHOICES = [
        (MONTAG, 'Montag'), (DIENSTAG, 'Dienstag'), (MITTWOCH, 'Mittwoch'),
        (DONNERSTAG, 'Donnerstag'), (FREITAG, 'Freitag'), (SAMSTAG, 'Samstag'),
    ]

    wochentag = models.PositiveSmallIntegerField(
        choices=WOCHENTAG_CHOICES, unique=True, verbose_name='Wochentag')
    # Liste von "HH:MM"-Zeichenketten, z. B. ["08:00", "10:00", "12:00"].
    uhrzeiten = models.JSONField(default=list, verbose_name='Uhrzeiten')
    slotlaenge = models.PositiveSmallIntegerField(
        default=25, verbose_name='Slotlänge (Minuten)')
    aktiv = models.BooleanField(default=True, verbose_name='Aktiv')

    class Meta:
        ordering = ['wochentag']
        verbose_name = 'Terminvorlage'
        verbose_name_plural = 'Terminvorlagen'

    def __str__(self):
        return f'{self.get_wochentag_display()}: {", ".join(self.uhrzeiten) or "geschlossen"}'


class Terminsperre(models.Model):
    """Eine von Oliver gesperrte Zeit oder ein ganz gesperrter Tag.

    ``uhrzeit=None`` heisst: der ganze Tag ist gesperrt. Eine Sperre ist eine
    ECHTE Nicht-Zeit (Fahrten, Auftraege) - sie erscheint auf der Seite genau
    wie ein gebuchter Termin als "nicht frei" (Bauplan §5, UWG §5: kein
    erfundener "vergeben"-Anschein, aber auch keine Unterscheidung nach aussen
    zwischen Sperre und echter Buchung).
    """

    datum = models.DateField(verbose_name='Datum')
    uhrzeit = models.TimeField(
        null=True, blank=True, verbose_name='Uhrzeit',
        help_text='Leer = der ganze Tag ist gesperrt.')
    grund = models.CharField(
        max_length=200, blank=True, default='', verbose_name='Grund (intern)')
    erstellt_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['datum', 'uhrzeit']
        constraints = [
            models.UniqueConstraint(fields=['datum', 'uhrzeit'],
                                    name='unique_sperre_je_datum_uhrzeit'),
        ]
        verbose_name = 'Terminsperre'
        verbose_name_plural = 'Terminsperren'

    def __str__(self):
        zeit = self.uhrzeit.strftime('%H:%M') if self.uhrzeit else 'ganzer Tag'
        return f'{self.datum} – {zeit}' + (f' ({self.grund})' if self.grund else '')


class Besichtigungstermin(VersandStatus):
    """Eine Anfrage fuer die kostenlose Besichtigung vor Ort (25 Minuten).

    Erbt aus ``VersandStatus`` wie die vier Lead-Models - damit haengen
    derselbe stuendliche Mail- und Push-Nachzuegler und dieselbe
    Anfragen-Liste im Dashboard automatisch daran (Bauplan §5).

    ``beginn`` ist per DB-Constraint eindeutig, solange ``status`` nicht
    ``abgesagt`` ist - eine Doppelbuchung desselben Slots ist damit auf
    Datenbankebene ausgeschlossen, nicht nur in der View geprueft
    (``IntegrityError`` -> "gerade vergeben, bitte andere Zeit").
    """

    OBJEKTART_CHOICES = [
        ('Keller', 'Keller'), ('Wohnung', 'Wohnung'), ('Haus', 'Haus'),
        ('Gewerbe', 'Gewerbe'), ('Garten', 'Garten'), ('Scheune', 'Scheune'),
    ]
    STATUS_CHOICES = [
        ('angefragt', 'Angefragt'), ('bestaetigt', 'Bestätigt'),
        ('abgesagt', 'Abgesagt'),
    ]

    ART_CHOICES = [
        ('vor_ort', 'Vor Ort'), ('video', 'Per WhatsApp-Video'),
    ]

    beginn = models.DateTimeField(verbose_name='Termin (Beginn)')
    dauer = models.PositiveSmallIntegerField(default=25, verbose_name='Dauer (Minuten)')
    # Seit 01.10.2026 (Migration 0024): vor Ort oder WhatsApp-Videoanruf. ``default`` fuer
    # alte Zeilen, ``db_default`` fuer einen Rolling-Deploy (alter Container
    # schreibt INSERTs ohne die Spalte). Bei ``video`` ist die Telefonnummer Pflicht (TerminForm).
    besichtigungsart = models.CharField(
        max_length=10, choices=ART_CHOICES, default='vor_ort',
        db_default='vor_ort',
        verbose_name='Art der Besichtigung')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='angefragt', verbose_name='Status')
    objektart = models.CharField(max_length=20, choices=OBJEKTART_CHOICES,
                                 verbose_name='Objektart')
    adresse = models.CharField(max_length=500, blank=True, verbose_name='Adresse des Objekts')
    name = models.CharField(max_length=200, verbose_name='Name')
    telefon = models.CharField(max_length=50, blank=True, verbose_name='Telefon')
    email = models.EmailField(blank=True, verbose_name='E-Mail')
    hinweis = models.TextField(blank=True, verbose_name='Hinweis')
    # Optionale Verknuepfung, falls die Buchung aus einer bestehenden Anfrage
    # heraus entsteht - heute noch ungenutzt, aber ohne sie muesste eine
    # spaetere Verknuepfung eine Migration nachreichen.
    anfrage = models.ForeignKey('Anfrage', null=True, blank=True,
                                on_delete=models.SET_NULL,
                                related_name='termine', verbose_name='Anfrage')
    verdacht = models.BooleanField(
        default=False, verbose_name='Spamverdacht',
        help_text='Grenzfall der Spam-Abwehr: gespeichert, aber ohne Mail und Push.')
    erstellt_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['beginn']
        constraints = [
            models.UniqueConstraint(
                fields=['beginn'],
                condition=~models.Q(status='abgesagt'),
                name='unique_aktiver_termin_slot'),
        ]
        verbose_name = 'Besichtigungstermin'
        verbose_name_plural = 'Besichtigungstermine'

    def __str__(self):
        return f'{self.name} – {self.beginn:%d.%m.%Y %H:%M} – {self.get_status_display()}'


# ── GBP-Beiträge → „Aktuelles" (Migration 0023, Bauplan §7) ─────────────────

class AktuellesQuelle(models.Model):
    """Herkunft eines importierten Beitrags - eigene Tabelle statt neuem Feld.

    **Warum eine eigene Tabelle statt eines neuen Felds an ``AktuellesPost``
    (Bauplan Paragraf 7).** Der Plan sieht ein Feld ``quelle``/``quelle_id``
    an ``AktuellesPost`` vor, *falls* geklaert ist, dass RTC diese Tabelle
    nicht mitbenutzt. Diese Pruefung ist im Rahmen dieses Auftrags nicht mit
    Sicherheit zu fuehren (kein RTC-Code liegt in diesem Worktree) - deshalb
    die vorsichtigere Variante: eine eigene, neue Tabelle, die per
    ``OneToOneField`` an einen Beitrag haengt. Migration 0023 legt
    ausschliesslich diese neue Tabelle an (und das ``slug``-Feld an der
    eigenen Tabelle ``AktuellesPost``), keine Spalte einer fremden Tabelle.
    """

    post = models.OneToOneField(AktuellesPost, on_delete=models.CASCADE,
                                related_name='quelle_info')
    quelle = models.CharField(max_length=20, default='gbp', verbose_name='Quelle')
    quelle_id = models.CharField(max_length=200, blank=True, default='',
                                 verbose_name='Kennung in der Quelle')
    text_hash = models.CharField(max_length=64, unique=True,
                                 verbose_name='Hash des Originaltexts')
    original_datum = models.DateField(null=True, blank=True,
                                      verbose_name='Ursprüngliches Datum')
    importiert_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Aktuelles-Quelle'
        verbose_name_plural = 'Aktuelles-Quellen'

    def __str__(self):
        return f'{self.quelle}:{self.quelle_id or self.text_hash[:8]} -> {self.post_id}'


class TelegramEmpfaenger(models.Model):
    """Ein Handy, das sich selbst fuer den Telegram-Push angemeldet hat (0021).

    Angelegt ausschliesslich vom Webhook (``apps/core/telegram_webhook.py``),
    und nur mit dem Einladungscode aus ``TELEGRAM_EINLADUNG`` - der Bot
    @ruempelbot ist oeffentlich auffindbar, der Code nicht. Empfaenger jedes
    Pushs sind ``TELEGRAM_CHAT_IDS`` (Umgebung) **und** die aktiven Zeilen hier
    (``telegram.chat_ids()``, dedupliziert).

    ``aktiv=False`` setzt ``/stop`` oder ``telegram.senden``, wenn Telegram
    den Chat nicht mehr kennt oder der Bot blockiert wurde. Die Zeile bleibt
    stehen, damit das Dashboard zeigt, wer einmal angemeldet war; ein neuer
    ``/start <Code>`` reaktiviert sie. Hoechstens ``telegram_webhook.MAX_EMPFAENGER``
    aktive Zeilen.
    """

    chat_id = models.CharField('Chat-ID', max_length=32, unique=True)
    name = models.CharField(max_length=200, blank=True)
    angemeldet_am = models.DateTimeField(auto_now_add=True)
    aktiv = models.BooleanField(default=True)

    class Meta:
        ordering = ['angemeldet_am']
        verbose_name = 'Telegram-Empfänger'
        verbose_name_plural = 'Telegram-Empfänger'

    def __str__(self):
        return f'{self.name or self.chat_id} ({"aktiv" if self.aktiv else "abgemeldet"})'
