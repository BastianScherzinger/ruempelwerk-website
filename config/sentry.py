"""Optionale Weiterleitung an Sentry - aus, solange ``SENTRY_DSN`` leer ist (VL19).

**Das Monitoring im Betrieb ist nicht diese Datei**, sondern die eigene
Fehlerwache (``apps/core/fehlerwache.py``, seit dem 16.09.2026): Datenbank,
Dashboard, Sammelmail, ohne Drittanbieter. Diese Datei bleibt fuer den Fall,
dass der Betrieb spaeter zusaetzlich Sentry will - dann gelten die
Voraussetzungen unten.

**Warum es das gibt.** Ein 500 auf dieser Website fiel bisher nur auf, wenn
jemand zufaellig ins Railway-Log sah. Der teuerste Fall ist belegt: Jede
Bewerbung ueber eine Stellenseite endete wochenlang in einem ``NameError``
(CLAUDE.md, "Vor jedem Commit"), und das Log stand die ganze Zeit offen da.
Ein Monitoring meldet den ersten Fehler, statt auf den Leser zu warten.

**Warum es trotzdem aus ist.** Ohne ``SENTRY_DSN`` in der Umgebung tut diese
Datei nichts - kein Import von ``sentry_sdk``, keine Verbindung. Einschalten
ist eine Entscheidung des Betriebs, keine Code-Aenderung, und sie hat eine
Voraussetzung: Sentry verarbeitet Fehlerberichte im Auftrag, also gehoeren ein
Vertrag zur Auftragsverarbeitung und ein Absatz in die Datenschutzerklaerung
dazu (``doku/80-AUFGABEN.md``). Empfohlen ist ein Projekt in der EU-Region.

**Was nie hinausgeht.** ``send_default_pii=False`` haelt IP-Adresse, Nutzer und
Cookies zurueck. ``_ohne_personendaten`` entfernt zusaetzlich den Request-Rumpf
- dort stehen Name, E-Mail und Telefon aus den Formularen - sowie Query-String
und die Proxy-Kopfzeilen mit der Client-IP (Regel 19). Uebrig bleiben Pfad,
Methode, Stacktrace und Fassung.

WAS DIESE DATEI NICHT LEISTET
-----------------------------
* **Sie meldet nur, was eine Ausnahme wirft oder als ERROR geloggt wird.** Ein
  still verschluckter Fehler (``except: pass``) oder eine Seite, die 200
  liefert und Falsches zeigt, erreicht Sentry nie.
* **Sie prueft nicht, ob jemand die Meldungen liest.** Ein Konto ohne
  Benachrichtigung ist ein zweites Log, das niemand oeffnet.
* **Sie wirkt nicht rueckwirkend** und nicht auf Fehler vor dem Laden der
  Settings (Importfehler beim Start stehen weiter nur im Railway-Log).
"""

import logging

logger = logging.getLogger(__name__)

# Kopfzeilen, die eine Person oder Sitzung erkennbar machen.
_KOPF_WEG = {'cookie', 'authorization', 'x-forwarded-for', 'x-real-ip',
             'x-envoy-external-address', 'cf-connecting-ip', 'true-client-ip'}


def _ohne_personendaten(event, hint=None):
    """``before_send``: nimmt alles heraus, was eine Person erkennbar macht."""
    anfrage = event.get('request')
    if isinstance(anfrage, dict):
        for feld in ('data', 'cookies', 'query_string', 'env'):
            anfrage.pop(feld, None)
        kopf = anfrage.get('headers')
        if isinstance(kopf, dict):
            for name in list(kopf):
                if name.lower() in _KOPF_WEG:
                    kopf.pop(name)
    event.pop('user', None)
    return event


def einrichten(dsn, umgebung='production', fassung=''):
    """Schaltet Sentry ein, wenn ``dsn`` gesetzt ist. Gibt zurueck, ob es laeuft."""
    if not dsn:
        return False
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
    except ImportError:                                     # pragma: no cover
        logger.warning('SENTRY_DSN ist gesetzt, sentry-sdk aber nicht '
                       'installiert - Fehler-Monitoring bleibt aus')
        return False
    sentry_sdk.init(
        dsn=dsn,
        integrations=[DjangoIntegration()],
        environment=umgebung,
        release=fassung or None,
        send_default_pii=False,
        # Nur Fehler, keine Leistungsmessung - die kostet Kontingent und
        # sagt fuer eine Website dieser Groesse nichts, was PageSpeed nicht
        # schon sagt.
        traces_sample_rate=0.0,
        before_send=_ohne_personendaten,
    )
    return True
