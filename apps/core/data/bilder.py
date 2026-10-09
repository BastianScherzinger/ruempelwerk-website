"""Die eigenen Fotos der festen Seiten - Quelle der Bildsitemap (TS19).

Die Bildsitemap kannte bis zum 06.09.2026 genau einen Bestand: die
Vorher-Nachher-Fotos aus dem CMS (D5, ``sitemaps.ImageSitemap``). Damit stand
der zweite eigene Bildbestand dieses Betriebs in keiner Sitemap - die
Flottenfotos und das Logo auf ``/ueber-uns/``. Es sind eigene Aufnahmen, sie
tragen einen echten ``alt``-Text, und die Seite ist indexierbar.

**Warum hier nur eine Seite steht (Stand 06.09.2026; seit 01.10.2026 siehe
``HERO_BILD`` am Dateiende).** Die uebrigen 80 Seiten trugen dasselbe
``hero-banner`` und dieselben Hero-Motive - jedes davon mit ``alt=""``, also
ausdruecklich als Schmuck ausgewiesen. Ein dekoratives Bild 80-mal zur
Bildersuche anzumelden erhoeht die Zahl der ``<image:image>``-Knoten und sonst
nichts: Google zaehlt eindeutige Bild-URLs, nicht Nennungen, und ein Motiv ohne
Bildbezug zur Seite ist fuer die Bildersuche wertlos. Wer diese Datei
erweitert, prueft deshalb zuerst, ob das Bild einen ``alt``-Text hat - ohne
ihn gehoert es nicht hierher.

**Die Personenfotos des Teams fehlen bewusst.** Sie stehen oeffentlich im
Markup, aber sie in einer Sitemap aktiv zur Bildersuche anzumelden ist eine
Entscheidung ueber Bilder von Personen und damit eine des Betriebs, nicht des
Werkzeugs. Wer sie aufnehmen will, holt vorher das Einverstaendnis der
Abgebildeten.

WAS DIESE DATEI NICHT LEISTET
-----------------------------
* **Sie ist eine zweite Liste** - die erste steht im Template. Genau deshalb
  haelt ``test_sitemaps.StatischeBildSitemapTests`` jeden Eintrag gegen das
  gerenderte HTML: Datei **und** Titel muessen dort vorkommen, sonst ist der
  Lauf rot. Ohne diese Pruefung waere die Datei Regel 12 in anderer Form.
* **Sie sagt nichts ueber die Bildqualitaet.** Ob ein Foto in der Bildersuche
  etwas taugt, weiss nur ein Mensch.
* **Sie kennt keine Reihenfolge.** Die Bildsitemap ist eine Anmeldung, keine
  Rangfolge.

Regel 4: reine Daten, kein Django, kein Import aus ``apps.core``.
"""

#: ``{Pfad: ((Datei unter static/, Titel), …)}``
#:
#: **Seit 01.10.2026 steht auch die Startseite hier** (TS19): Ihre zehn
#: Foto-Motive im ``<main>`` (Vorher/Nachher-Reihen, Flotte) tragen einen echten
#: ``alt``. Nicht aufgenommen sind dort das Trustlocal-Abzeichen (eine Grafik,
#: kein Foto) und die Portraits der Regionalleiter (siehe oben).
#:
#: **Der Pfad ist der der Seite, auf der das Bild steht** - die Bildsitemap
#: sagt "auf dieser Seite liegen diese Bilder", nicht "dieses Bild ist eine
#: Seite". Er muss deshalb eine indexierbare, in ``sitemap-main.xml``
#: gelistete Adresse sein; ein Bild auf einer ``noindex``-Seite anzumelden ist
#: Regel 21 eine Ebene tiefer.
#:
#: **Die Datei wird nicht ausgeschrieben, sondern durch ``static()``
#: geschickt** (``sitemaps.statische_bild_liste``). In Produktion laeuft
#: ``CompressedManifestStaticFilesStorage``, dort traegt jede Datei einen Hash
#: im Namen. Eine hier ausgeschriebene URL zeigte auf eine Adresse, die es nur
#: lokal gibt - und die Sitemap naennte ein anderes Bild als die Seite.
#:
#: **Der Titel ist woertlich der ``alt``-Text aus dem Template.** Nicht, weil
#: Google ``<image:title>`` auswertet (seit August 2022 nicht mehr), sondern
#: weil jede andere Zeichenkette eine zweite Beschreibung desselben Bildes
#: waere - und die zweite ist immer die, die niemand nachzieht.
#: **Die Titel beschreiben seit IS25 (12.09.2026), was zu sehen ist.** Vorher
#: standen hier sieben Wortstapel aus Markenname und Bauteil - "Rümpelwerk
#: Sprinter", "Rümpelwerk Sprinter Seite", "Rümpelwerk Sprinter Detail". Sie
#: waren nicht falsch, sie sagten nur nichts: Wer "Sprinter Detail" liest,
#: weiss nicht, ob er ein Rad, ein Fahrerhaus oder einen leeren Laderaum vor
#: sich hat - und genau das ist die Frage, die ein alt-Text beantwortet.
#: Beschrieben ist, was auf der Datei zu sehen ist, nicht was die Seite
#: verkaufen will.
SEITEN_BILDER = {
    '/': (
        ('images/halle-fensterfront.webp',
         'Geräumte Gewerbehalle mit Fensterfront und leerem Teppichboden'),
        ('images/keller-vorher-720.webp',
         'Kellerraum, bis unter die Decke vollgestellt'),
        ('images/keller-nachher-720.webp',
         'Derselbe Kellerraum, leer und besenrein'),
        ('images/halle-voll-720.webp',
         'Gewerbehalle mit Regalen vor der Räumung'),
        ('images/halle-leer-720.webp',
         'Geräumte Gewerbehalle mit leerem Teppichboden'),
        ('images/garten-vorher-720.webp',
         'Garten mit Bergen von Schnittgut'),
        ('images/garten-nachher-720.webp',
         'Derselbe Garten nach der Räumung'),
        ('images/wohnzimmer-vorher.webp',
         'Möbliertes Wohnzimmer vor einer Haushaltsauflösung'),
        ('images/transporter.webp',
         'Eigener Transporter mit geöffneten Hecktüren und leerem Laderaum'),
        ('images/lkw.webp',
         'Eigener Koffer-LKW mit Ladebordwand'),
    ),
    '/ueber-uns/': (
        ('images/ruempelwerk_logo.webp',
         'Firmenlogo: grünes Hausdach mit stilisiertem R über dem Schriftzug '
         'Rümpelwerk Mitteldeutschland'),
        ('images/sprinter1.webp',
         'Unser Sprinter mit geöffneten Hecktüren: leerer, holzverkleideter Laderaum'),
        ('images/sprinter2.webp',
         'Unser weißer Mercedes-Benz Sprinter mit Hochdach, schräg von vorn rechts'),
        ('images/sprinter3.webp',
         'Unser Sprinter im Seitenprofil: langer Radstand, geschlossener Kastenaufbau'),
        ('images/lkw1.webp',
         'Unser Koffer-LKW von hinten links, mit hochgeklappter Ladebordwand am Heck'),
        ('images/lkw2.webp',
         'Unser Koffer-LKW von vorn rechts: weißer Kofferaufbau auf Mercedes-Benz Fahrgestell'),
        ('images/lkw3.webp',
         'Fahrerhaus und Kofferaufbau unseres Koffer-LKW von der Fahrerseite'),
    ),
}


#: **Das Banner-Foto der Stadt-, Leistungs- und Matrixseiten** (TS19, 01.10.2026).
#:
#: Bis zum 01.10.2026 stand hier die Begruendung, es nicht aufzunehmen: Das
#: ``hero-banner`` trug ``alt=""``, war also ausdruecklich Schmuck. Seit die
#: Templates (``city.html``, ``rw_hero_service*.html``, ``service_city.html``)
#: einen beschreibenden ``alt`` setzen, ist es das Inhaltsbild dieser Seiten -
#: und die Sitemap nennt es mit **demselben Text** wie das Markup. Es steht
#: bewusst im ``<url>``-Eintrag **jeder** dieser Seiten und nicht in
#: ``sitemap-images.xml``: Dort wuerde es eine zweite ``<url>`` mit gleicher
#: Adresse neben dem Eintrag der Teil-Sitemap bilden. Google zaehlt eindeutige
#: Bild-URLs, die Mehrfachnennung kostet also nichts, aber sie meldet jede Seite
#: mit ihrem Bild.
#:
#: **Dritte Liste neben den Templates** - deshalb haelt
#: ``test_sitemaps.HeroBildSitemapTests`` jeden Titel gegen das gerenderte HTML.
#: Wer einen ``alt`` im Template aendert, aendert ihn hier mit, sonst ist der
#: Lauf rot.
#:
#: **Nicht aufgenommen:** die Portraits der Regionalleiter (Entscheidung des
#: Betriebs, siehe oben) und die CMS-Galeriebilder auf Leistungsseiten
#: (``sitemap-images.xml``, ``/galerie/``).
HERO_BILD = 'images/hero-banner.jpg'
HERO_TITEL_STADT = ('Besenrein entrümpelter, heller Wohnraum nach einer '
                    'Entrümpelung in {stadt} durch Rümpelwerk Mitteldeutschland')
HERO_TITEL_LEISTUNG = ('Besenrein geräumter, heller Wohnraum nach einer '
                       '{leistung} durch Rümpelwerk Mitteldeutschland')
HERO_TITEL_MATRIX = ('Besenrein geräumter Wohnraum nach einer {leistung} in '
                     '{stadt} durch Rümpelwerk Mitteldeutschland')
