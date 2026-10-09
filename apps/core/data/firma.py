# -*- coding: utf-8 -*-
"""Die Stammdaten des Betriebs - Name, Adresse, Telefon, Steuernummer (G5).

Warum das eine eigene Datei ist
-------------------------------
``sameAs`` verknuepft die Website mit dem Google-Unternehmensprofil und sagt
damit: "Das bin auch ich." Die Verknuepfung ist aber nur so viel wert wie die
**NAP-Konsistenz** dahinter - Name, Adresse, Telefon muessen ueberall
zeichengenau gleich stehen. Eine abweichende Schreibweise entwertet sie:
"Cansteinstr. 14" und "Cansteinstraße 14" sind fuer einen Abgleich zwei
verschiedene Betriebe.

Bis zum 26.08.2026 standen diese Angaben an **zwei** Stellen: als Konstanten in
``schema.py`` (fuer das JSON-LD) und noch einmal von Hand im Impressum. Das ist
genau die Konstruktion, an der in diesem Projekt schon Preise, FAQ und
Zeitzusagen auseinandergelaufen sind - nur dass es hier nicht auffaellt,
sondern still die Entitaetserkennung schwaecht.

Jetzt gilt fuer die Stammdaten dieselbe Regel wie fuer Preise (Regel 1) und
Zeitzusagen (Regel 24): **eine Quelle.** ``check_seo`` prueft, dass keine Seite
eine andere Schreibweise der Adresse oder der Telefonnummer zeigt.

Kein Import aus ``apps.core`` (Regel 4) - dies ist ein Datenmodul.
"""

FIRMA = 'Rümpelwerk Mitteldeutschland'
INHABER = 'Oliver Pohl'
# Der Name, unter dem der Betrieb rechtlich auftritt. So steht er im Impressum
# und so gehoert er in 'legalName'.
LEGALNAME = f'{FIRMA} – Inh. {INHABER}'

STRASSE = 'Cansteinstraße 14'
PLZ = '06110'
ORT = 'Halle'
BUNDESLAND = 'Sachsen-Anhalt'
LAND = 'Deutschland'
LAND_CODE = 'DE'

# E.164 fuers Schema, deutsche Schreibweise fuer die Anzeige. Beide aus einer
# Quelle, damit die sichtbare Nummer und die im Markup nicht auseinanderlaufen.
TELEFON = '+491635027819'
TELEFON_ANZEIGE = '+49 163 5027819'

# Dieselbe Nummer im wa.me-Format: Landesvorwahl ohne '+' und ohne fuehrende
# Null. Aus TELEFON gerechnet, nicht abgetippt - sonst ist es die dritte
# Schreibweise derselben Nummer, und genau daran ist die NAP-Konsistenz in den
# Verzeichnissen schon einmal auseinandergelaufen (Regel 25).
#
# **Warum das hier steht und nicht im Template:** Bis zum 05.09.2026 stand
# '491635027819' an **zwoelf** Stellen in neun Templates, jedes Mal von Hand.
# Eine Nummernaenderung haette elf stille Ueberbleibsel hinterlassen - und ein
# WhatsApp-Knopf, der ins Leere fuehrt, sieht funktionsfaehig aus.
WHATSAPP = TELEFON.lstrip('+')


def whatsapp_link(text=''):
    """wa.me-Adresse mit vorformuliertem Text.

    ``text`` wird URL-kodiert; Zeilenumbrueche bleiben erhalten. Ohne Text
    kommt die nackte Adresse zurueck.
    """
    from urllib.parse import quote
    ziel = f'https://wa.me/{WHATSAPP}'
    return f'{ziel}?text={quote(text)}' if text else ziel


# Der Standardtext der Kontaktknoepfe. Eine Quelle, damit nicht neun Templates
# neun leicht verschiedene Anreden fuehren.
WHATSAPP_TEXT_STANDARD = (
    'Hallo Rümpelwerk! 👋\n\n'
    'Ich interessiere mich für Ihre Dienstleistungen und hätte gerne ein '
    'kostenloses Angebot.\n\n'
    'Anbei die Fotos des Objekts:'
)

# Sondertexte der WhatsApp-Knoepfe (EIG371, 01.10.2026): Sie standen bis dahin
# als fertig kodierte Links von Hand in elf Templates. Jetzt je Text eine
# Konstante hier und eine Kontextvariable in ``context()``; ein Template tippt
# keinen ``wa.me/...?text=`` mehr.
#: Fehler- und Hinweisseiten (500, 410) und die Startseite: ohne Fotobitte.
WHATSAPP_TEXT_KURZ = (
    'Hallo Rümpelwerk! 👋\n\n'
    'Ich interessiere mich für Ihre Dienstleistungen und hätte gerne ein '
    'kostenloses Angebot.'
)
#: Das Popup mit dem Fotohinweis.
WHATSAPP_TEXT_POPUP = (
    'Hallo Rümpelwerk! 👋\n\n'
    'Ich möchte gerne schnell ein Angebot und schicke Ihnen ein paar Fotos '
    'meines Objekts:'
)
#: Der Hinweis zur Ratenzahlung auf /dienstleistungen/.
WHATSAPP_TEXT_RATENZAHLUNG = (
    'Hallo Rümpelwerk! 👋\n\n'
    'Ich interessiere mich für eine Ratenzahlung und hätte gerne ein '
    'unverbindliches Angebot.\n\n'
    'Anbei die Fotos des Objekts:'
)

# Geprueft und korrigiert am 27.08.2026. Hier stand 51.4942 / 11.9647 -
# **2,7 km neben der eigenen Adresse.** Der alte Wert ist nirgends belegt; er
# zeigt auf die Gegend noerdlich der Altstadt, nicht auf die Cansteinstraße.
#
# Belegt ist der neue Wert doppelt, und die beiden Quellen sind voneinander
# unabhaengig:
#
#   * das eigene Google-Unternehmensprofil - die Maps-URL in data/reviews.py
#     traegt als Ortsmarke !3d51.4702576!4d11.9678383;
#   * Nominatim/OpenStreetMap zur Adresse "Cansteinstraße 14, 06110 Halle
#     (Saale)": 51.4702495 / 11.9678340, also rund 10 m daneben - dieselbe
#     Hausnummer, dasselbe Gebaeude.
#
# Uebernommen ist die Zahl aus dem **Unternehmensprofil**, nicht die von
# Nominatim: 'geo' und 'sameAs' zeigen dann auf denselben Punkt, und genau
# darum geht es bei G5 - eine Koordinate, die 2,7 km neben der eigenen
# Adresse liegt, widerspricht dem eigenen sameAs-Ziel. Es geht dabei nichts
# kaputt, es wird nur still schwaecher.
#
# ``check_seo`` haelt beide Quellen seit dem 27.08.2026 zusammen.
GEO = (51.4702576, 11.9678383)

# Geschaeftszeiten (KV11, 01.10.2026) - EINE Quelle fuer Schema, Footer,
# /ueber-uns/, /anfrage/, llms.txt und /barrierefreiheit/. 01.10.2026:
# "muss nicht minutengenau sein, nur ueberall gleich und passend zu den anderen
# Daten." Passend heisst: Besichtigungen laufen Mo-Sa (``termine.py``, Slots
# 08-16 Uhr, 25 Minuten je Termin), die Antwort auf eine Anfrage in 2 Stunden
# (``zusagen.ANTWORT``). Telefon und Besichtigung bis 03.10.2026 Mo-Sa 8-18 Uhr; Anfragen
# per Formular und WhatsApp sind jederzeit moeglich, und die Antwort in 2 Stunden
# gilt rund um die Uhr (``zusagen.ANTWORT_GILT``, Entscheidung 02.10.2026,
# EIG394) - die Geschaeftszeiten begrenzen sie nicht. Sonn- und Feiertage: keine Besichtigung (``feiertage.py``).
#
# 03.10.2026: Die Zeiten folgen dem **Google-Unternehmensprofil**, nicht
# umgekehrt - abgefragt ueber Places API (New), regularOpeningHours:
# Mo-Fr 8-19, Sa 8-13, So 9-12 Uhr. Vorher stand hier Mo-Sa 8-18 Uhr, und das
# Profil widersprach der Seite an jedem Tag ausser Mo-Fr morgens (NAP/Zeiten-
# Konsistenz). Sonntag ist nur Telefon - Besichtigungen bleiben Mo-Sa
# (``termine.zeiten_fuer_wochentag``), samstags nur bis 13 Uhr.
#: (Tage, von, bis) je Block - speist das Schema (``schema.OEFFNUNGSZEITEN``).
ZEITEN = (
    (('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'), '08:00', '19:00'),
    (('Saturday',), '08:00', '13:00'),
    (('Sunday',), '09:00', '12:00'),
)
#: Anzeigetext, ueberall wortgleich.
ZEITEN_ANZEIGE = 'Mo–Fr 8–19, Sa 8–13, So 9–12 Uhr'
#: Fuer Fliesstext (llms.txt, Erklaerung zur Barrierefreiheit).
ZEITEN_LANG = 'Montag bis Freitag 8 bis 19 Uhr, Samstag 8 bis 13 Uhr, Sonntag 9 bis 12 Uhr'
#: Der Zusatz zu den Anfragewegen - dieselbe Aussage wie ``zusagen.ANTWORT``.
ANFRAGEN_JEDERZEIT = 'Anfragen per Formular und WhatsApp sind jederzeit möglich'

# Oeffentlich im Impressum genannt - kein Geheimnis, aber ein
# Unterscheidungsmerkmal, das im Schema als 'taxID' zaehlt.
STEUERNUMMER = '110/257/08816'
FINANZAMT = 'Finanzamt Leipzig'


def context():
    """Die Stammdaten fuers Template. Speist den Context-Processor."""
    return {
        'FIRMA_NAME': FIRMA,
        'FIRMA_INHABER': INHABER,
        'FIRMA_STRASSE': STRASSE,
        'FIRMA_PLZ': PLZ,
        'FIRMA_ORT': ORT,
        'FIRMA_LAND': LAND,
        'FIRMA_TELEFON': TELEFON,
        'FIRMA_TELEFON_ANZEIGE': TELEFON_ANZEIGE,
        'FIRMA_WHATSAPP': WHATSAPP,
        'FIRMA_WHATSAPP_LINK': whatsapp_link(WHATSAPP_TEXT_STANDARD),
        'FIRMA_WHATSAPP_LINK_KURZ': whatsapp_link(WHATSAPP_TEXT_KURZ),
        'FIRMA_WHATSAPP_LINK_POPUP': whatsapp_link(WHATSAPP_TEXT_POPUP),
        'FIRMA_WHATSAPP_LINK_RATENZAHLUNG': whatsapp_link(WHATSAPP_TEXT_RATENZAHLUNG),
        'FIRMA_ZEITEN': ZEITEN_ANZEIGE,
        'FIRMA_ZEITEN_LANG': ZEITEN_LANG,
        'FIRMA_ANFRAGEN_JEDERZEIT': ANFRAGEN_JEDERZEIT,
        'FIRMA_STEUERNUMMER': STEUERNUMMER,
        'FIRMA_FINANZAMT': FINANZAMT,
    }
