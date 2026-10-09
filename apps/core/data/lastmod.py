# -*- coding: utf-8 -*-
"""Jedes Aenderungsdatum dieser Website - eine Quelle fuer Sitemap und Schema (D2).

Bis zum 06.09.2026 standen die vier Konstanten in ``apps/core/sitemaps.py``.
Das war richtig, solange nur die Sitemap ein Datum ausgab. Seit D2 gibt es ein
zweites Ausgabefeld - ``dateModified`` im ``WebPage``-Knoten -, und damit
waeren es zwei Listen fuer dieselbe Aussage geworden. Genau davor warnt Regel
12: Sichtbares und Schema aus **einer** Quelle speisen, nie zwei pflegen. Die
Konstanten liegen deshalb hier, mit ihrer vollstaendigen Vorgeschichte;
``sitemaps.py`` und ``templatetags/rw_schema.py`` lesen beide von hier.

**Regel 4 gilt.** Dieses Modul importiert nichts aus ``apps.core`` und kein
Django - nur die drei Nachbarmodule unter ``data/`` (relative Importe, genau
wie ``matrix.py`` es mit ``cities.py`` macht). Es ist damit ohne konfiguriertes
Django benutzbar, und ``apps/core/tests/test_data.py`` prueft das per ``ast``.

**Warum die Pfade hier von Hand stehen und nicht aus ``reverse()`` kommen.**
``reverse()`` waere ein Django-Import auf Modulebene und damit ein Verstoss
gegen Regel 4. Die Kehrseite ist eine Doppelung: Aendert sich ein Pfad in
``apps/core/urls.py``, findet ``VERSATZ_TAGE`` ihn nicht mehr, und die Seite
faellt still auf ``CONTENT_LASTMOD`` ohne Versatz zurueck. Deshalb prueft
``apps/core/tests/test_sitemaps.py`` strukturell, dass die Schluessel dieser
Tabelle **genau** die Pfade der ``MainSitemap`` sind - ein umbenannter Pfad
macht den Testlauf rot, statt leise ein falsches Datum auszuliefern.

**Regel 22 gilt weiter: nie ``date.today()``.** Ein mitwanderndes Datum
behauptet jeden Tag, alle 85 Seiten seien soeben geaendert worden; Google
lernt daraus, dass das Signal wertlos ist. Die Konstanten werden **bei
inhaltlichen Aenderungen** hochgezogen, nicht bei jedem Deploy. Das gilt seit
D2 doppelt: ``dateModified`` ist eine Tatsachenbehauptung auf der Seite selbst,
nicht nur eine Angabe in einer XML-Datei, die kein Mensch liest.

WAS DIESES MODUL NICHT LEISTET
------------------------------
* **Es weiss nichts von der Datenbank.** ``/aktuelles/`` und ``/galerie/``
  beziehen ihren Inhalt vollstaendig aus dem CMS; fuer sie ist jedes feste
  Datum falsch, sobald Oliver etwas veroeffentlicht (Befund D1). Diese beiden
  Pfade bekommen ihr Datum deshalb in ``sitemaps.py::lastmod_fuer_pfad`` aus
  ``AktuellesPost`` - hier stehen nur ihre Rueckfallwerte. Ein Modell-Import
  waere hier auch gar nicht erlaubt: Regel 4, und ``test_data.py`` fuehrt die
  einzige Ausnahme (``reviews.py``) namentlich.
* **Es prueft nicht, ob ein Datum stimmt.** Dass es fest steht, ist pruefbar;
  ob es zur letzten inhaltlichen Aenderung passt, schaetzt ``check_seo`` als
  Warnung gegen die Commit-Historie der Datenmodule.
"""

import datetime

from .cities import _CITY_DATA
from .matrix import matrix_kombinationen
from .ratgeber import _RATGEBER_DATA
from .services import _SERVICE_DATA


# Fest verdrahtet - NICHT date.today(). Vorher wanderte jedes lastmod taeglich
# mit, die Sitemap behauptete also jeden Tag, alle 195 Seiten seien soeben
# geaendert worden. Google lernt daraus, dass das Signal wertlos ist, und
# ignoriert es. Beim naechsten inhaltlichen Umbau dieses Datum hochziehen.
# Hochgezogen zum Abschluss von Block 1 (14.08.2026): An diesem Tag haben alle
# 54 Stadtseiten recherchierte Ortsangaben und Ortsteillisten bekommen und die
# Startseite ihre Rezensionen im Markup. Das ist eine echte inhaltliche
# Aenderung - genau der Anlass, fuer den dieses Datum gedacht ist.
# Hochgezogen am 27.08.2026 (G2): Startseite und beide Hubs
# (/entrumpelung/, /dienstleistungen/) haben den Antwort-zuerst-Block
# bekommen - sichtbarer neuer Text ueber der Falz, nicht nur Markup.
# Hochgezogen am 16.09.2026 (GE23/IS19): Standorte, Ueber uns, Aktuelles,
# Galerie, Jobs samt drei Anzeigen, Kooperation und Preisrechner haben einen
# Antwortblock bekommen, /anfrage/ und /galerie/ einen erklaerenden Abschnitt,
# die Startseite ihre berichtigte FAQ und /entrumpelung/ die Standorttabelle.
# Hochgezogen am 17.09.2026 (PR06): Preistabellen und Rechner nennen den
# Stockwerk- und Sonderabfallzuschlag jetzt ehrlich ("entfällt" statt
# "kein Aufpreis"), der Rechner heisst das Ergebnis Richtpreis.
# Hochgezogen am 24.09.2026 (Pakete 1-5): Startseite mit Ort in Titel und
# Description (Halle/Leipzig), FAQPage-Paar auf /anfrage/ und /preisangebot/,
# dazu die Aenderungen der parallelen Pakete am Bestand.
# Hochgezogen am 25.09.2026 (SEO-Audit): Startseiten-FAQ und /entrumpelung/
# nennen dieselbe Stadtzahl wie der Footer, /dienstleistungen/ ohne
# "bester Preis" und mit Link auf die Renovierungsseite, /standorte/ ohne
# "Schnellsteinsatz", /ueber-uns/ ohne "Foto folgt".
# Hochgezogen am 01.10.2026 (Vollabarbeitung): Startseite mit Preis im
# Hero-Satz, "Richtpreis" statt "sofort", Kopfknopf "Termin buchen",
# /entrumpelung/ mit neuem Titel, Anfrage mit den Leistungsarten.
CONTENT_LASTMOD = datetime.date(2026, 10, 6)
# Eigenes Datum seit dem 22.08.2026 (Befund K1). Vorher hing es an
# CONTENT_LASTMOD und meldete fuer die 54 Stadtseiten weiter den 14.08. -
# obwohl sie am 21./22.08. den groessten Umbau ihrer Geschichte bekommen haben:
# Preisrechner, Ablauf mit HowTo-Schema, FAQ von 6 auf 9, durchgerechnete
# Ortsbeispiele, /entrumpelung/halle/ von 942 auf 2.003 Woerter. Google hat also
# genau in dem Moment "unveraendert" gelesen, in dem sich alles geaendert hat.
# Beim naechsten Umbau der Stadtseiten dieses Datum hochziehen, nicht das obere.
# Hochgezogen am 27.08.2026 (G2): Alle 54 Stadtseiten tragen jetzt einen
# Antwortblock mit Preis, Ortsteilen, Entfernung und Termin vor Ort.
# Hochgezogen am 04.09.2026: Die FAQ jeder Stadtseite hat zwei reine
# Textbausteine verloren und dafuer eine Antwort bekommen, die den
# Unterschied zwischen Haushaltsaufloesung und Nachlassraeumung wirklich
# erklaert; dazu traegt der LocalBusiness-Knoten je Stadt jetzt ein `image`
# (Befund des Google-Tests fuer Rich-Suchergebnisse vom selben Tag).
# Hochgezogen am 17.09.2026 (PR06): Jede Stadtseite versprach "kein Aufpreis
# fuer Treppen, Aufzug oder Sperrgut" und "ohne Anmeldung" - beides ist
# durch die tatsaechlichen Zu- und Abschlaege und das E-Mail-Tor ersetzt.
# Hochgezogen am 24.09.2026 (Paket 4): neue Titel und Descriptions, der
# Ablauf verspricht die Antwort statt den Termin (EIG138), "Beraeumung" in
# Sachsen/Sachsen-Anhalt, Leipzig mit allen Wertstoffhoefen und Halteverbot,
# drei neue Umlandseiten (Markkleeberg, Wurzen, Zwenkau).
# Hochgezogen am 01.10.2026: Kachel Nachlassraeumung nennt den Preis, die
# Ortszeile im Hero ist ein div, "Richtpreis berechnen" statt "Sofortpreis".
# Hochgezogen am 02.10.2026 (KV14/IS37): Jede Stadtseite traegt im Schluss-
# CTA Telefonnummer und Antwortzeit; der Ortsname steht nicht mehr in jeder
# Kartenueberschrift, in fuenf Staedten auch nicht mehr in jedem Ortsabsatz.
CITY_LASTMOD = datetime.date(2026, 10, 2)
# Eigenes Datum: Die Leistungsseiten entstehen in Block 2 und aendern sich
# unabhaengig vom Bestand. Beim Anlegen einer neuen Leistung hochziehen.
# Hochgezogen am 19.08.2026: acht neue Leistungsseiten (A5-A12) sind live
# gegangen, aus einer wurden neun. Das ist der Anlass, fuer den dieses eigene
# Datum gedacht ist - CONTENT_LASTMOD bleibt unberuehrt, weil sich am Bestand
# (Startseite, Stadtseiten) inhaltlich nichts geaendert hat.
# Hochgezogen am 27.08.2026 (G2): Die neun Leistungsseiten haben ueber ihrem
# Antwortabsatz jetzt die Frage, die er beantwortet (``answer_frage``).
# Hochgezogen am 16.09.2026: Jede Leistungsseite, auf die ein Ratgeberartikel
# verweist, zeigt jetzt den Abschnitt "Mehr im Ratgeber"; die Kostenseite ist
# als Article auch im og:type ausgezeichnet.
# Hochgezogen am 24.09.2026 (Offen Nr. 24): services.py hatte am 17.09.
# sichtbare Belegsaetze bekommen (GE43) und am 24.09. die Preis- und
# Zusagenkorrekturen aus Paket 3.
# Hochgezogen am 25.09.2026 (SEO-Audit, EIG271/EIG272): /gewerbeentruempelung/
# ohne unbestaetigte Zusagen zu Schutzklasse, Behaeltern und Wochenendarbeit.
# Hochgezogen am 01.10.2026 (IS42/GE23/EIG356): neue Titel und Descriptions
# von Wohnung, Keller, Nachlass und Sperrmuell, "Festpreis ab" in jedem
# Hero-Untertitel, Gewerbe ohne Nachtarbeit.
# Hochgezogen am 02.10.2026 (Leistungs-Durchgang, EIG397/EIG398): §35a-Aussagen
# nach BMF-Anlage 1 berichtigt, Fristen nach §564 BGB, Kostenabschnitt und
# GewAbfV-Nachweise auf /gewerbeentruempelung/, Kostenrechner gebuendelt auf
# /entruempelung-kosten/.
SERVICE_LASTMOD = datetime.date(2026, 10, 2)
# Charge 1 der Leistung-x-Stadt-Matrix (A13), live am 19.08.2026.
# Eigenes Datum, damit die naechste Charge das Datum der ersten
# nicht mitzieht.
# Hochgezogen am 27.08.2026 (G2): Die fuenf Antworttexte sind auf das
# G2-Format gebracht - Firmenname, Preisstand, 45-49 Woerter.
# Hochgezogen am 24.09.2026 (Paket 3): Preis- und Zusagenkorrekturen in
# matrix.py; die Leipziger Seiten zeigen dazu die neuen Ortsangaben.
# Hochgezogen am 01.10.2026 (GE23/EIG356): "Festpreis ab" im Hero-Untertitel,
# Gewerbe Leipzig mit "nach Absprache" statt Abend und Wochenende.
# Am 02.10.2026 (EIG396) auf diesem Datum belassen bzw. bestaetigt: Charge 2
# ist live (Haushaltsaufloesung Halle, Magdeburg, Dresden), und alle
# Matrixseiten haben neues Markup bekommen (Aufwaertslinks auch ohne
# Geschwister, Recherchestand je Stadt statt "August 2026").
MATRIX_LASTMOD = datetime.date(2026, 10, 2)
# Der Ratgeber (T4-T8), live am 16.09.2026: Uebersicht plus fuenf Artikel.
# Eigenes Datum, damit ein neuer Artikel nicht die Bestandsseiten mitzieht -
# und umgekehrt. Beim naechsten inhaltlichen Umbau eines Artikels hochziehen.
# Hochgezogen am 01.10.2026: Antwort des Seriositaets-Artikels nennt den
# Festpreis ab, Quellenlink "Website der Stadt bzw. des Entsorgungstraegers",
# Artikelkarten des Hubs als Liste.
# Bestaetigt am 02.10.2026 (Ratgeber-Pruefung): §35a-Artikel gegen das
# BMF-Schreiben berichtigt (Haushaltsaufloesung nicht beguenstigt, Erben,
# Umzug), Impressum nach §5 DDG, Entsorgungsnachweis, besenrein-Urteil,
# Glossar; dazu Berichtigungen in den Wissensartikeln. Das Datum ist schon
# der 02.10. und bleibt.
RATGEBER_LASTMOD = datetime.date(2026, 10, 2)


# Der Versatz in Tagen gegenueber CONTENT_LASTMOD, je Bestandsseite.
#
# Er stand bis zum 06.09.2026 als vierte Spalte in ``MainSitemap.pages`` und
# ist mit D2 hierher gewandert - aus demselben Grund wie die Konstanten: Der
# ``WebPage``-Knoten braucht denselben Wert, und zwei Tabellen fuer dieselbe
# Zahl laufen auseinander. Der Zweck des Versatzes ist unveraendert: Nicht
# jede Bestandsseite aendert sich zugleich, und elf identische Daten in einer
# Sitemap sind ein schwaecheres Signal als elf gestaffelte.
#
# Die Schluessel sind Pfade, keine URL-Namen: ``reverse()`` waere ein
# Django-Import und damit ein Verstoss gegen Regel 4 (siehe Modulkopf).
# Stand 01.10.2026: CONTENT_LASTMOD wurde von 28.09. auf 01.10. gehoben, weil
# Startseite, /anfrage/, /preisangebot/ und /entrumpelung/ sich an dem Tag
# inhaltlich geaendert haben. Alle anderen Seiten dieser Tabelle blieben
# unveraendert (nur Markup, WhatsApp-Link, Datenschutz-Fussnote) und tragen
# deshalb um die drei Tage Anhebung groesseren Versatz: Ihr Datum bleibt, was
# es am 28.09. war (Regel 22). Wer CONTENT_LASTMOD wieder hebt, rechnet fuer
# jede UNVERAENDERTE Seite denselben Betrag auf den Versatz.
VERSATZ_TAGE = {
    '/':                     0,
    '/dienstleistungen/':    0,   # 02.10.: Karten ohne unbelegte Aussagen
    '/anfrage/':             0,   # 02.10.: H1 (EIG398), Antwort rund um die Uhr (EIG394)
    '/preisangebot/':        0,   # 02.10.: Titel/H1 (EIG398)
    '/standorte/':           0,   # 02.10.: Antwortblock und Kerngebiet berichtigt
    '/ueber-uns/':           0,   # 02.10.: unbelegte Aussagen ersetzt (Familienbetrieb, Plattform-Satz)
    '/jobs/':                0,   # 02.10.: Einleitung ohne Buerojob-Widerspruch und ohne Wachstumsfloskel
    '/kooperationspartner/': 33,  # 28.09. - 30
    '/entrumpelung/':        0,   # 02.10.: Rechner-Link (EIG398)
    '/aktuelles/':           4,   # nur Rueckfall, das CMS datiert (28.09. - 1)
    '/galerie/':             4,   # nur Rueckfall, das CMS datiert (28.09. - 1)
}

# Die drei Stellenanzeigen unter /jobs/<slug>/. Sie haengen an CONTENT_LASTMOD,
# weil ihr Text in jobs.py steht und sich mit dem Bestand bewegt.
JOB_VERSATZ_TAGE = 0   # 02.10.2026: Anzeigentexte berichtigt (kein Branchenvergleich, Schema-Arbeitszeit)


# ── Erscheinungsdatum, nicht Aenderungsdatum (GE15, 10.09.2026) ──────────────
#
# ``datePublished`` beantwortet eine andere Frage als ``dateModified``: wann
# der Text **entstanden** ist, nicht wann er zuletzt angefasst wurde. Ein
# ``Article``-Knoten braucht beides; ohne das erste ist er unvollstaendig, und
# mit einem geschaetzten waere er falsch.
#
# **Deshalb steht hier nur, was belegt ist.** Der einzige Eintrag ist
# ``/entruempelung-kosten/``: Die Seite ist als A12 mit den sieben anderen
# neuen Leistungsseiten am 19.08.2026 live gegangen - dasselbe Datum, das
# 40 Zeilen weiter oben als Anlass fuer ``SERVICE_LASTMOD`` steht ("Hochgezogen
# am 19.08.2026: acht neue Leistungsseiten (A5-A12) sind live gegangen").
# Zwei unabhaengige Stellen im Repository nennen denselben Tag; das ist ein
# Beleg, keine Schaetzung.
#
# Wer eine weitere Ratgeberseite auszeichnet, traegt ihr Erscheinungsdatum
# hier ein - **und zwar nur, wenn er es belegen kann.** Fehlt der Eintrag,
# laesst ``schema.article_schema`` das Feld weg, statt eines zu erfinden;
# dieselbe Zurueckhaltung wie beim ``datePublished`` einer Rezension ohne
# echtes Datum.
#
# Die Beitraege unter ``/aktuelles/`` stehen hier **nicht**: Ihr
# Erscheinungsdatum ist ``AktuellesPost.datum`` und kommt damit aus der
# Datenbank, genau wie ihr ``lastmod`` (siehe Modulkopf, Regel 4).
VEROEFFENTLICHT = {
    '/entruempelung-kosten/': datetime.date(2026, 8, 19),
    # Die fuenf Ratgeberartikel sind am 16.09.2026 zusammen erschienen -
    # belegt durch den Commit, der sie anlegt, und durch RATGEBER_LASTMOD.
    # Ein neuer Artikel bekommt hier sein eigenes Datum, nicht dieses.
    **{f'/ratgeber/{slug}/': datetime.date(2026, 9, 16)
       for slug in _RATGEBER_DATA},
    # 02.10.2026: erschienen mit dem Commit, der den Artikel anlegt.
    '/ratgeber/halteverbot-entruempelung-beantragen/': datetime.date(2026, 10, 2),
}


def veroeffentlicht_fuer_pfad(pfad):
    """Das belegte Erscheinungsdatum einer URL - oder ``None``.

    ``None`` ist der Normalfall und kein Mangel: Fuer die allermeisten Seiten
    dieses Projekts ist nicht belegt, wann sie entstanden sind, und ein
    ``datePublished`` ist eine Tatsachenbehauptung (Regel 22, dieselbe
    Ueberlegung wie bei ``dateModified``).
    """
    return VEROEFFENTLICHT.get(pfad)

# Die beiden Seiten, deren Inhalt vollstaendig aus dem CMS kommt. Hier stehen
# sie nur, damit ``sitemaps.py`` und die Tests **eine** Liste dafuer haben -
# das echte Datum holt ``sitemaps.py`` aus der Datenbank (D1).
CMS_PFADE = ('/aktuelles/', '/galerie/')


def _segmente(pfad):
    return [t for t in (pfad or '').split('/') if t]


def fuer_pfad(pfad):
    """Das Aenderungsdatum einer URL - ohne Datenbank, rein aus den Daten.

    Die Reihenfolge der Abfragen ist nicht beliebig. ``/entrumpelung/`` ist der
    Hub und steht in ``VERSATZ_TAGE``; ``/entrumpelung/halle/`` ist eine
    Stadtseite. Und ``/haushaltsaufloesung/`` ist eine Leistungsseite, waehrend
    ``/haushaltsaufloesung/leipzig/`` eine Matrixseite ist. Wer die Abfragen
    umstellt, bekommt fuer die zweistufigen Pfade das Datum der einstufigen -
    und das faellt nicht auf, weil beide Daten plausibel aussehen.

    Unbekannte Pfade bekommen ``CONTENT_LASTMOD``. Das betrifft die drei
    Rechtsseiten (noindex, stehen in keiner Sitemap) und alles, was kuenftig
    dazukommt, ohne hier eingetragen zu werden - ein Datum, das zu alt ist, ist
    die harmlosere Luege als eines, das zu neu ist.
    """
    if pfad in VERSATZ_TAGE:
        return CONTENT_LASTMOD - datetime.timedelta(days=VERSATZ_TAGE[pfad])

    teile = _segmente(pfad)

    if teile and teile[0] == 'ratgeber':
        return RATGEBER_LASTMOD

    if len(teile) == 2:
        if teile[0] == 'entrumpelung' and teile[1] in _CITY_DATA:
            return CITY_LASTMOD
        if teile[0] == 'jobs':
            return CONTENT_LASTMOD - datetime.timedelta(days=JOB_VERSATZ_TAGE)
        if (teile[0], teile[1]) in set(matrix_kombinationen()):
            return MATRIX_LASTMOD
    elif len(teile) == 1 and teile[0] in _SERVICE_DATA:
        return SERVICE_LASTMOD

    return CONTENT_LASTMOD
