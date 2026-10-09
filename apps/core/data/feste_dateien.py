"""Bilder, die unter einer festen Adresse ohne Hash erreichbar sein muessen.

SEO-Audit vom 25.09.2026, Punkte K1 und K2.

Alles unter ``/static/`` traegt in Produktion einen Hash im Dateinamen
(``CompressedManifestStaticFilesStorage``): ``og-default.4f1c….jpg``. Fuer
Bilder, die die eigene Seite einbindet, ist das richtig - der Hash macht sie
ein Jahr cachebar. Fuer vier Bilder ist es falsch, weil **fremde Systeme sich
die Adresse merken** und sie Wochen spaeter wieder abrufen:

* **Favicon** - Google zeigt es neben jedem Suchtreffer und holt es mit einem
  eigenen Crawler, der die Adresse speichert. Aendert sich das Bild, aendert
  sich der Hash; die alte Adresse ist nach dem Deploy eine 404, und bis zum
  naechsten Abruf steht neben dem Treffer die graue Weltkugel.
* **Apple-Touch-Icon** - iOS fragt ``/apple-touch-icon.png`` auf der Wurzel ab,
  unabhaengig vom ``<link>``.
* **Vorschaubild (og:image)** - WhatsApp, Facebook und LinkedIn cachen die
  Vorschau eines geteilten Links; die Bild-URL darin stirbt beim naechsten
  Bildwechsel. WhatsApp ist der Hauptkontaktweg dieses Betriebs.
* **Logo im Schema** - die Adresse, unter der Google das Logo des Betriebs fuer
  Knowledge Panel und Unternehmensprofil fuehrt.

Die Dateien selbst bleiben unter ``static/images/`` (eine Quelle); diese
Tabelle sagt nur, unter welcher **zweiten, festen** Adresse sie zusaetzlich
ausgeliefert werden. ``views.feste_datei`` liefert aus, ``config/urls.py``
legt die Routen an, ``rw_seo.html``, ``schema.py`` und die Kopfzeilen der
Templates verweisen auf die feste Adresse, und ``check_seo`` bildet sie fuer
die Massepruefung auf die Datei zurueck.

Regel 4: reine Daten, kein Import aus ``apps.core``.
"""

#: ``{fester Pfad ohne fuehrenden Schraegstrich: (Datei unter static/, Content-Type)}``
#:
#: ⚠ Jeder Pfad hat **genau ein Segment** und steht in ``config/urls.py`` vor
#: dem Catch-All - Punkte im Namen sind ohnehin kein gueltiger Stadt-Slug.
FESTE_DATEIEN = {
    # 48 x 48: Google verlangt ein quadratisches Favicon, empfohlen als
    # Vielfaches von 48 px. Bis zum 25.09.2026 lag hier ein 64 x 65 grosses
    # Bild - nicht quadratisch.
    'favicon.ico': ('images/favicon-48.png', 'image/png'),
    'favicon-192.png': ('images/favicon-192.png', 'image/png'),
    'apple-touch-icon.png': ('images/apple-touch-icon.png', 'image/png'),
    'og-image.jpg': ('images/og-default.jpg', 'image/jpeg'),
    'logo.jpg': ('images/ruempelwerk_logo.jpeg', 'image/jpeg'),
}

#: Die feste Adresse des Vorschaubilds und des Logos - an einer Stelle, damit
#: Template, Schema und Pruefung nicht drei Schreibweisen fuehren.
OG_BILD_PFAD = '/og-image.jpg'
LOGO_PFAD = '/logo.jpg'


def datei_fuer_pfad(pfad):
    """``'/og-image.jpg'`` -> ``'images/og-default.jpg'``, sonst ``None``."""
    eintrag = FESTE_DATEIEN.get(str(pfad or '').lstrip('/'))
    return eintrag[0] if eintrag else None
