# -*- coding: utf-8 -*-
"""Externe Auszeichnungen/Nachweise (Bauplan §6) - Trustlocal und WKDB.

Zwei unabhaengige Drittquellen, die den Betrieb bewerten - **beide getrennt
von** ``reviews.py`` (der eigenen Google-Zahl, aus dem Google-Unternehmensprofil
bzw. taeglich synchronisiert). Genau wie bei den Google-Bewertungen (Regel 2)
gilt: Eine Zahl auf der Seite muss aus **dieser** Datei stammen, nie abgetippt
sein - und die drei Zahlen (Google, Trustlocal, WKDB) duerfen sich nicht
vermischen, weil sie unterschiedliche Skalen und Stichproben haben. Deshalb
gibt ``rw_nachweise.html`` (siehe dort) nie eine Google-Zahl aus.

Beide Quellen am 28.09.2026 direkt auf der jeweiligen Profilseite geprueft:

* **Trustlocal** - ``https://trustlocal.de/.../ruempelwerk-mitteldeutschland/``:
  Score 9,9 von 10, 32 Bewertungen, Abzeichen "Top Score 2026"; seit 01.10.2026
  zusaetzlich der hoehere Rang "Top Pro" (Abzeichen "Top Pro September 2026",
  Widget-API: topBadge top_pro_09_2026_DE, totalScore 0,9875). Dasselbe Profil
  speist auch das Live-Widget in ``rw_trustlocal.html``/``rw_trustlocal_score.html``
  (JS-Kachel) - hier stehen die Zahlen dagegen serverseitig als Text, fuer
  Crawler ohne JavaScript (Regel 11) und fuers Rechtstextabzeichen.
* **WKDB** ("wer kennt den BESTEN", ``werkenntdenbesten.de``) - Unternehmens-ID
  114147620: 5,0 von 5,0 aus 40 Bewertungen (ueber mehrere Portale
  aggregiert), Platz 2 unter den Entruempelungsfirmen in Halle.

Kein Import aus ``apps.core`` (Regel 4) - dies ist ein Datenmodul.
"""

__all__ = ['TRUSTLOCAL', 'WKDB']

#: Trustlocal-Profil und Top-Score-Abzeichen.
TRUSTLOCAL = {
    'name': 'Top Score 2026',
    'wert': '9,9',
    'skala': '10',
    'anzahl': '32',
    'geprueft': '2026-10-01',
    # Hoeherer Rang (seit 01.10.2026): Top Pro. 'name' bleibt der Top-Score-Titel.
    'rang': 'Top Pro',
    'rang_zeitraum': 'September 2026',
    'rang_badge_pfad': 'images/trustlocal-top-pro-09-2026.svg',   # 89 x 120
    'rang_icon_pfad': 'images/trustlocal-top-pro-icon.svg',       # 40 x 40
    'profil_url': (
        'https://trustlocal.de/sachsen-anhalt/halle-sachsen-anhalt/'
        'entrumpelung/r%C3%BCmpelwerk-mitteldeutschland/'
    ),
    # Lokal gespiegelt (siehe docs/betrieb.md) statt live von static.trustlocal.de
    # eingebunden - eine tote CDN-Adresse darf das Abzeichen nicht verschwinden
    # lassen, und ein fremdes Bild ohne eigene Kontrolle ueber seinen Inhalt
    # passt nicht zu einer Aussage, die die eigene Seite trifft.
    'badge_pfad': 'images/trustlocal-top-score-2026.svg',
}

#: WKDB ("wer kennt den BESTEN") - Sammelportal ueber mehrere Bewertungsquellen.
WKDB = {
    'anbieter': 'WKDB',
    'unternehmens_id': '114147620',
    'wert': '5,0',
    'skala': '5,0',
    'anzahl': '40',
    'platz': '2',
    'kategorie': 'Entrümpelung in Halle (Saale)',
    'geprueft': '2026-09-28',
    'profil_url': (
        'https://www.werkenntdenbesten.de/e/114147620/entruempelung/'
        'halle-saale/ruempelwerk-mitteldeutschland-bewertungen.html'
    ),
}
