"""Die Fehlerwache - eigenes Fehler-Monitoring, ohne Drittanbieter (VL19).

**Warum es das gibt.** Ein 500 auf dieser Website fiel bisher nur auf, wenn
jemand zufaellig ins Railway-Log sah. Der teuerste Fall ist belegt: Jede
Bewerbung ueber eine Stellenseite endete wochenlang in einem ``NameError``
(CLAUDE.md, "Vor jedem Commit"), und das Log stand die ganze Zeit offen da.

**Warum kein Sentry.** Ein externer Dienst verarbeitet Fehlerberichte im
Auftrag - mit Konto, Vertrag zur Auftragsverarbeitung und einem Absatz in der
Datenschutzerklaerung. Diese Wache braucht nichts davon: Die Berichte bleiben
in der eigenen Datenbank, die Meldung geht ueber den Mailweg, den die Website
ohnehin hat. ``config/sentry.py`` bleibt als ausgeschaltete Weiterleitung fuer
den Fall liegen, dass der Betrieb es spaeter doch will.

**Wie es arbeitet.**

1. ``FehlerwacheHandler`` haengt in ``settings.LOGGING`` an jedem Logger des
   Projekts und an ``django.request``. Jede Zeile ab ERROR - also jeder
   unbehandelte 500 und jedes ``logger.error(...)`` - wird zu einem
   ``Fehlerereignis``. Gleiche Fehler zaehlen hoch statt neue Zeilen
   anzulegen (``kennung``: Logger, Fehlerart, Stelle im Code).
2. ``fehler_melden()`` laeuft stuendlich im Scheduler (``apps.py``) und
   schickt **eine** Sammelmail an ``ADMIN_EMAILS``, wenn seit der letzten
   Meldung etwas Neues auflief. Ein Fehler, der tausendmal kommt, erzeugt
   hoechstens eine Mail pro Stunde, nicht tausend.
3. Das Dashboard (``STATS_PATH/fehler/``) zeigt die Liste; "erledigt"
   blendet einen Fehler aus, bis er wiederkommt.
4. Nach ``AUFBEWAHRUNG_TAGE`` ohne neues Auftreten wird ein Eintrag geloescht.

**Was nie gespeichert wird.** Kein Request-Rumpf (dort stehen Name, E-Mail
und Telefon aus den Formularen), kein Query-String, keine Cookies, keine IP.
E-Mail-Adressen, IP-Adressen und lange Ziffernfolgen im Text werden vor dem
Speichern ersetzt (``_schwaerzen``) - eine SMTP-Fehlermeldung nennt sonst den
Empfaenger.

WAS DIESE DATEI NICHT LEISTET
-----------------------------
* **Sie sieht nur, was als ERROR geloggt wird.** Ein verschluckter Fehler
  (``except: pass``) oder eine Seite, die 200 liefert und Falsches zeigt,
  erreicht sie nie. Ebenso wenig Fehler, bevor Django die Settings geladen
  hat (Importfehler beim Start stehen weiter nur im Railway-Log).
* **Sie meldet nichts, wenn der Mailweg selbst kaputt ist.** Dann steht der
  Fehler trotzdem in der Datenbank und im Dashboard - aber niemand bekommt
  eine Mail. Genau deshalb zeigt das Dashboard die Liste unabhaengig vom
  Versand.
* **Sie schreibt nicht, wenn die Datenbank der Fehler ist.** Faellt die
  Datenbank aus, landet nur eine Zeile auf ``stderr`` (Railway-Log).
"""

import datetime
import hashlib
import logging
import re
import sys
import threading
import traceback

#: Wie lange ein Eintrag nach seinem letzten Auftreten bleibt.
AUFBEWAHRUNG_TAGE = 30

#: Obergrenzen der Textfelder - ein Stacktrace kann beliebig lang werden.
_MELDUNG_MAX = 500
_VERLAUF_MAX = 8000

_zustand = threading.local()

_MAIL = re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+')
_IPV4 = re.compile(r'\b\d{1,3}(?:\.\d{1,3}){3}\b')
_IPV6 = re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{1,4}\b')
_ZIFFERN = re.compile(r'\d{6,}')
# Fuer die Kennung: Zahlen und Hex-Adressen machen denselben Fehler sonst zu
# hundert verschiedenen ("id=17", "at 0x7f...").
_VARIABEL = re.compile(r'0x[0-9a-fA-F]+|\d+')


def _schwaerzen(text):
    """Ersetzt, was eine Person erkennbar machen kann."""
    text = _MAIL.sub('[E-Mail]', text or '')
    text = _IPV4.sub('[IP]', text)
    text = _IPV6.sub('[IP]', text)
    return _ZIFFERN.sub('[Zahl]', text)


def _stelle(tb):
    """``datei:zeile`` des tiefsten Rahmens im eigenen Code - sonst des tiefsten."""
    rahmen = traceback.extract_tb(tb) if tb else []
    eigene = [r for r in rahmen
              if ('apps' in r.filename or 'config' in r.filename)
              and 'site-packages' not in r.filename]
    ziel = (eigene or rahmen or [None])[-1]
    if ziel is None:
        return ''
    datei = ziel.filename.replace('\\', '/')
    for marke in ('/apps/', '/config/'):
        if marke in datei:
            datei = marke.strip('/') + '/' + datei.split(marke, 1)[1]
            break
    return f'{datei}:{ziel.lineno}'


def zerlegen(record):
    """Die Felder eines ``Fehlerereignis`` aus einem Log-Eintrag - ohne Datenbank."""
    art, verlauf, tb = 'Logzeile', '', None
    if record.exc_info and record.exc_info[0] is not None:
        typ, wert, tb = record.exc_info
        art = typ.__name__
        verlauf = ''.join(traceback.format_exception(typ, wert, tb))
    try:
        meldung = record.getMessage()
    # audit-ok P02: fehlerhafte %-Argumente oder ein __str__, das selbst wirft.
    # Protokollieren geht hier nicht (wir sind der Log-Handler), und der Rückfall
    # auf den Rohtext ist die Behandlung - nichts geht verloren.
    except Exception:
        meldung = str(record.msg)
    anfrage = getattr(record, 'request', None)
    pfad = getattr(anfrage, 'path', '') or ''
    methode = getattr(anfrage, 'method', '') or ''
    stelle = _stelle(tb) or f'{record.pathname.replace(chr(92), "/").split("/")[-1]}:{record.lineno}'

    # Die Kennung haengt an der Stelle im Code, nicht am Text: Derselbe
    # KeyError auf zwei Stadtseiten ist ein Fehler, nicht zwei.
    grundlage = '|'.join((record.name, art, stelle,
                          '' if tb else _VARIABEL.sub('#', str(record.msg))[:200]))
    return {
        # audit-ok K12: Gruppierungsschlüssel, kein Schutz - SHA-1 hält die
        # 40 Zeichen von Fehlerereignis.kennung (unique) und die bestehenden
        # Kennungen gültig; usedforsecurity=False sagt das auch Python.
        'kennung': hashlib.sha1(grundlage.encode('utf-8'),
                                usedforsecurity=False).hexdigest(),
        'quelle': record.name[:100],
        'art': art[:120],
        'meldung': _schwaerzen(meldung)[:_MELDUNG_MAX],
        'ort': stelle[:200],
        'pfad': pfad[:300],
        'methode': methode[:10],
        'verlauf': _schwaerzen(verlauf)[-_VERLAUF_MAX:],
    }


def festhalten(record):
    """Legt den Fehler an oder zaehlt ihn hoch. Gibt das Ereignis zurueck."""
    from django.db.models import F
    from django.db import IntegrityError
    from django.utils import timezone

    from .models import Fehlerereignis

    felder = zerlegen(record)
    jetzt = timezone.now()
    kennung = felder.pop('kennung')
    aktualisieren = dict(felder, anzahl=F('anzahl') + 1, zuletzt=jetzt, erledigt=False)
    if Fehlerereignis.objects.filter(kennung=kennung).update(**aktualisieren):
        return Fehlerereignis.objects.get(kennung=kennung)
    try:
        return Fehlerereignis.objects.create(kennung=kennung, erstmals=jetzt,
                                             zuletzt=jetzt, **felder)
    except IntegrityError:      # zwei Worker, derselbe Fehler, dieselbe Sekunde
        Fehlerereignis.objects.filter(kennung=kennung).update(**aktualisieren)
        return Fehlerereignis.objects.get(kennung=kennung)


class FehlerwacheHandler(logging.Handler):
    """Logging-Handler ab ERROR. Darf eine Anfrage nie selbst zum Absturz bringen."""

    def __init__(self, level=logging.ERROR):
        super().__init__(level=level)

    def emit(self, record):
        # Rueckkopplung: Ein Fehler beim Festhalten wuerde selbst geloggt und
        # landete wieder hier.
        if getattr(_zustand, 'aktiv', False):
            return
        _zustand.aktiv = True
        try:
            festhalten(record)
        # audit-ok P02: ein Log-Handler darf nie werfen; der Fehlschlag wird
        # unten auf stderr gemeldet (nicht über logging - das wäre eine Schleife).
        except Exception as exc:
            # **Bewusst nicht ueber logging:** das waere die Schleife von oben.
            # stderr landet im Railway-Log, und der eigentliche Fehler steht
            # dort ohnehin schon (Konsolen-Handler).
            try:
                sys.stderr.write(f'[Fehlerwache] nicht gespeichert: '
                                 f'{type(exc).__name__}\n')
            # Geschlossener Stream beim Herunterfahren (ValueError/OSError) oder
            # gar keiner (sys.stderr ist None, AttributeError) - dann gibt es
            # keinen Ort mehr, an den sich etwas melden liesse.
            except (OSError, ValueError, AttributeError):
                pass
        finally:
            _zustand.aktiv = False


def _mail_text(ereignisse):
    zeilen = ['Die Fehlerwache der Website hat seit der letzten Meldung '
              'Folgendes gesehen:', '']
    for e in ereignisse:
        zeilen += [
            f'- {e.art} in {e.ort or e.quelle}  ({e.anzahl}x, zuletzt '
            f'{e.zuletzt:%d.%m.%Y %H:%M} UTC)',
            f'  {e.meldung[:200]}',
        ]
        if e.pfad:
            zeilen.append(f'  Adresse: {e.methode} {e.pfad}')
    zeilen += ['', 'Details und "erledigt" im internen Dashboard unter "Fehler".',
               'Diese Mail enthält keine Formulardaten und keine IP-Adressen.']
    return '\n'.join(zeilen)


def fehler_melden(jetzt=None):
    """Stuendlich: eine Sammelmail ueber alles Neue, dann Altes loeschen.

    Gibt die Zahl der gemeldeten Fehler zurueck. Gemeldet gilt ein Fehler erst,
    wenn die Mail wirklich rausging - scheitert der Versand, versucht es der
    naechste Durchlauf wieder.
    """
    import json
    import urllib.request

    from django.conf import settings
    from django.db.models import F, Q
    from django.utils import timezone

    from .emails import _absenden, _weg
    from .models import Fehlerereignis

    jetzt = jetzt or timezone.now()
    Fehlerereignis.objects.filter(
        zuletzt__lt=jetzt - datetime.timedelta(days=AUFBEWAHRUNG_TAGE)).delete()

    neu = list(Fehlerereignis.objects.filter(erledigt=False).filter(
        Q(gemeldet_bis__isnull=True) | Q(zuletzt__gt=F('gemeldet_bis')))
        .order_by('-zuletzt')[:20])
    if not neu or _weg() == 'aus' or not list(settings.ADMIN_EMAILS):
        return 0

    betreff = f'[Rümpelwerk] Fehlerwache: {len(neu)} Fehler auf der Website'
    anfrage = urllib.request.Request(
        'https://api.resend.com/emails',
        data=json.dumps({
            'from': settings.DEFAULT_FROM_EMAIL,
            'to': list(settings.ADMIN_EMAILS),
            'subject': betreff,
            'text': _mail_text(neu),
        }).encode('utf-8'),
        headers={
            'Authorization': f"Bearer {getattr(settings, 'RESEND_API_KEY', '')}",
            'Content-Type': 'application/json',
            'User-Agent': 'Ruempelwerk-Website/1.0',
        },
    )
    # Kein try: Scheitert der Versand, faengt der Scheduler die Ausnahme und
    # schreibt sie ins Log - und die Ereignisse bleiben ungemeldet.
    with _absenden(anfrage, timeout=10):
        pass
    for e in neu:
        Fehlerereignis.objects.filter(pk=e.pk).update(gemeldet_bis=e.zuletzt)
    return len(neu)
