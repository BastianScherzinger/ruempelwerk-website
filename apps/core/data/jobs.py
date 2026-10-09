"""Stellenanzeigen fuer /jobs/ und /jobs/<slug>/.

Aus ``views.py`` herausgeloest (F6). Reines Verschieben, kein Verhalten geaendert.
Importiert absichtlich nichts aus ``apps.core`` - dieses Paket muss von
``context_processors`` wie von ``views`` aus erreichbar bleiben, ohne Zirkel.

**``datum`` ist Pflicht.** Google verlangt ``datePosted`` fuer jede
Stellenanzeige; ohne das Feld war das JobPosting-Markup auf allen drei
Jobseiten ungueltig (gefunden am 14.08.2026 im Rich Results Test - kein
lokales Werkzeug meldet das). Der Wert ist das echte Datum der
Veroeffentlichung, nicht das heutige. **Wer eine Anzeige neu ausschreibt,
zieht das Datum mit hoch** - Google zeigt Stellen ungern, deren ``datePosted``
Monate zurueckliegt.

**``gehalt`` nur bei Bruttoangaben.** ``baseSalary`` meint im Schema den
Bruttolohn. Zwei der drei Anzeigen nennen im sichtbaren Text **netto**; diese
Zahl in ein Bruttofeld zu schreiben waere eine Falschangabe, also fehlt das
Feld dort. Es ist optional - fehlen ist erlaubt, falsch sein nicht.
"""

import datetime as _dt

#: EIG20/EIG82 (24.09.2026): Wie lange eine Anzeige ab ``datum`` gilt. Daraus
#: entsteht ``validThrough`` im JobPosting - Google empfiehlt das Feld, und
#: ohne es blieb eine Anzeige im Schema unbegrenzt "offen". Ein halbes Jahr
#: ist eine Festlegung, keine Zusage des Betriebs: Ist die Stelle danach noch
#: offen, wird sie neu ausgeschrieben und ``datum`` hochgezogen (siehe oben) -
#: das bestaetigt nur der Betrieb.
LAUFZEIT_TAGE = 180


def gueltig_bis(job):
    """``validThrough`` einer Anzeige als ISO-Datum: ``datum`` + Laufzeit."""
    return (_dt.date.fromisoformat(job['datum'])
            + _dt.timedelta(days=LAUFZEIT_TAGE)).isoformat()


_JOB_DATA = {
    'entruempelungshelfer': {
        'slug': 'entruempelungshelfer',
        # Erstveroeffentlichung: Initial Commit 4a2a65f vom 12.06.2026.
        'datum': '2026-06-12',
        # Kein 'gehalt' und seit 02.10.2026 auch kein Stundenlohn im Text: Die
        # frueheren 13-15 EUR/Stunde lagen unter dem Mindestlohn (13,90 EUR,
        # EIG331); welchen Lohn der Inhaber zahlt, steht nirgends belegt.
        'seo_title': 'Entrümpelungshelfer (m/w/d) Leipzig & Halle | Rümpelwerk',
        # Eigene Description statt des Teasers: der ist als Fliesstext
        # geschrieben und mit 65-110 Zeichen zu kurz fuer ein Snippet.
        'seo_description': 'Einstieg ohne Vorwissen: Du packst mit an, wir zeigen dir den Rest. Vollzeit, Teilzeit oder Minijob in Leipzig und Halle. Jetzt bewerben.',
        'seo_path': '/jobs/entruempelungshelfer/',
        'seo_keywords': 'Entrümpelungshelfer Job, Helfer Haushaltsauflösung, Stelle Entrümpelung, Vollzeit Teilzeit Minijob Leipzig Halle Magdeburg',
        # 02.10.2026: Die Anzeige nennt Vollzeit, Teilzeit und Minijob; schema.org
        # erlaubt fuer employmentType eine Liste. Vorher stand nur FULL_TIME.
        'employment_type': ['FULL_TIME', 'PART_TIME'],
        'title': 'Entrümpelungshelfer (m/w/d)',
        'icon': '💪',
        'badge': 'Vollzeit / Teilzeit',
        'badge_style': 'background:var(--rw-orange);color:#fff;',
        'teaser': 'Kein Vorwissen nötig – du packst mit an, wir zeigen dir den Rest.',
        'aufgaben': [
            'Durchführung von Entrümpelungen, Haushaltsauflösungen und Kellerräumungen',
            'Transport von Räumgut zum Wertstoffhof oder Lager',
            'Unterstützung beim Be- und Entladen der Fahrzeuge',
            'Sortieren nach Holz, Metall, Elektrogeräten und Restmüll; Farben, Chemikalien und Ähnliches erkennen und getrennt beiseitestellen',
            'Besenreine Übergabe der geräumten Objekte',
        ],
        'verdienst': [
            'Die Vergütung besprechen wir im Gespräch',
            'Vollzeit, Teilzeit und Minijob möglich',
            'Pünktliche Bezahlung',
        ],
        'voraussetzungen': [
            'Keine Vorkenntnisse erforderlich – Tragen, Sortieren und Laden zeigen wir dir im Einsatz',
            'Körperliche Belastbarkeit und Zuverlässigkeit',
            'Deutsch-Grundkenntnisse',
            'Führerschein Klasse B von Vorteil',
        ],
        'wir_bieten': [
            'Fahrzeuge und Arbeitsmaterial stellt der Betrieb',
            'Festes, eingespieltes Team',
            'Flexible Einsatzzeiten nach Absprache',
            'Einsatzgebiete: Leipzig, Halle, Magdeburg, Hannover, Dresden, Chemnitz',
            'Möglichkeit zur Übernahme als Teamleiter',
        ],
        'orte': 'Leipzig · Halle · Magdeburg',
    },
    'teamleiter': {
        'slug': 'teamleiter',
        'datum': '2026-06-12',
        # Kein 'gehalt': die Anzeige nennt netto, baseSalary meint brutto.
        'seo_title': 'Teamleiter Entrümpelung, ab 2.600 € netto | Rümpelwerk',
        # Eigene Description statt des Teasers: der ist als Fliesstext
        # geschrieben und mit 65-110 Zeichen zu kurz fuer ein Snippet.
        'seo_description': 'Du leitest ein Team von 2–4 Leuten vor Ort: Tagesplanung, Kundenkontakt, Abnahme. Vollzeit, Firmenwagen, 2.600–3.200 € netto. Jetzt bewerben.',
        'seo_path': '/jobs/teamleiter/',
        'seo_keywords': 'Teamleiter Entrümpelung Job, Vorarbeiter Haushaltsauflösung, Teamleiter Vollzeit Mitteldeutschland',
        'employment_type': 'FULL_TIME',
        'title': 'Teamleiter Entrümpelung (m/w/d)',
        'icon': '🏆',
        'badge': 'Vollzeit',
        'badge_style': 'background:var(--rw-orange);color:#fff;',
        'teaser': 'Du leitest dein Team vor Ort – mit Verantwortung für Ablauf, Kunde und Übergabe und mit Firmenwagen.',
        'aufgaben': [
            'Leitung eines 2–4-köpfigen Entrümpelungsteams vor Ort',
            'Tagesplanung und Koordination der Einsätze',
            'Kundenkontakt und Abnahme nach Auftrag',
            'Sicherstellung einer besenreinen und ordentlichen Übergabe',
            'Entsorgungslogistik und Dokumentation',
        ],
        'verdienst': [
            '2.600–3.200 € netto/Monat je nach Erfahrung',
            'Firmenwagen auch zur Privatnutzung nach Absprache',
            'Pünktliche, zuverlässige Bezahlung',
        ],
        'voraussetzungen': [
            'Erfahrung in Entrümpelung, Handwerk oder vergleichbarem Bereich von Vorteil',
            'Führerschein Klasse B (Pflicht), C1 von Vorteil',
            'Führungserfahrung oder Bereitschaft zur Verantwortungsübernahme',
            'Zuverlässigkeit, Organisationstalent und Kundenkompetenz',
        ],
        'wir_bieten': [
            'Firmenwagen für den Einsatz',
            'Verantwortung und Aufstiegschancen',
            'Eingespieltes, verlässliches Team',
            'Kurze Wege: du sprichst direkt mit dem Inhaber',
            'Einsatzgebiete: Halle, Leipzig und Mitteldeutschland',
        ],
        'orte': 'Mitteldeutschland',
    },
    'innendienst': {
        'slug': 'innendienst',
        'datum': '2026-06-12',
        # Einzige Anzeige mit Bruttoangabe im sichtbaren Text.
        'gehalt': {'min': 2400, 'max': 3200, 'einheit': 'MONTH'},
        'seo_title': 'Innendienst Kundenservice Halle, ab 2.400 € | Rümpelwerk',
        # Eigene Description statt des Teasers: der ist als Fliesstext
        # geschrieben und mit 65-110 Zeichen zu kurz fuer ein Snippet.
        'seo_description': 'Schnittstelle zwischen Kunden, Außendienst und Organisation: Angebote, Termine, Rückfragen. Vollzeit in Halle (Saale). Jetzt bewerben.',
        'seo_path': '/jobs/innendienst/',
        'seo_keywords': 'Innendienst Job Halle, Kundenservice Stelle Halle, Bürojob Entrümpelung, Sachbearbeiter Halle',
        'employment_type': 'FULL_TIME',
        'title': 'Innendienst Mitarbeiter (m/w/d) Kundenservice',
        'icon': '📞',
        'badge': 'Vollzeit | Büro & Organisation',
        'badge_style': 'background:var(--rw-orange);color:#fff;',
        'teaser': 'Die Schnittstelle zwischen Kunden, Außendienst und Organisation. Einsatzort: Halle (Saale).',
        'aufgaben': [
            'Annahme und Bearbeitung von Kundenanfragen per Telefon, E-Mail und Online',
            'Erste Beratung: Umfang, Zugang, Termin und Besonderheiten eines Auftrags erfragen',
            'Koordination und Weiterleitung der Aufträge an den Außendienst',
            'Abstimmung zwischen Kunden, Teamleitern und Einsatzplanung',
            'Pflege und Verwaltung von Kundendaten',
            'Unterstützung bei Terminplanung und Tourenorganisation',
            'Sicherstellen eines reibungslosen Informationsflusses im gesamten Team',
        ],
        'verdienst': [
            'Ca. 2.400 – 3.200 € brutto/Monat (Vollzeit, verhandelbar)',
            'Je nach Erfahrung und Qualifikation',
        ],
        'voraussetzungen': [
            'Freundliches und sicheres Auftreten am Telefon und schriftlich',
            'Organisationstalent und strukturierte Arbeitsweise',
            'Gute Deutschkenntnisse in Wort und Schrift',
            'Sicherer Umgang mit PC, E-Mail und ggf. CRM-Systemen',
            'Teamfähigkeit und Verantwortungsbewusstsein',
            'Erfahrung im Büro oder Kundenservice von Vorteil, aber kein Muss',
        ],
        'wir_bieten': [
            'Fester Arbeitsplatz im Büro in Halle (Saale)',
            'Abwechslungsreiche Tätigkeit mit Verantwortung',
            'Direkte Zusammenarbeit mit Außendienst und Leitung',
            'Freundliches, familiäres Team',
            'Faire Vergütung und Entwicklungsmöglichkeiten',
            'Eintrittstermin nach Absprache',
        ],
        'orte': 'Halle (Saale)',
    },
}
