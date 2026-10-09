"""Alle Views der oeffentlichen Website - 85 Seiten aus einer Handvoll Vorlagen.

Der Aufbau folgt den Daten, nicht der Seitenzahl: ``city_page`` bedient alle 54
Stadtseiten, ``service_page`` die neun Leistungsseiten, ``matrix_page`` die
Kombinationen Leistung x Stadt. Eine neue Seite ist deshalb ein Eintrag in
``apps/core/data/``, keine neue View - und der City-Catch-All muss das
**letzte** Muster in ``urls.py`` bleiben (Regel 5).

Was hier ausserdem haengt:

* die vier Formulare (``anfrage``, ``preisangebot``, ``kooperation``,
  ``job_detail``) - jedes mit Rate-Limit, Spam-Abwehr und Duplikatsperre
  **vor** dem Speichern (Regel 18), und jedes mit Mailversand in einem
  Hintergrund-Thread, den der stuendliche Nachzuegler absichert,
* die Dateien, die Crawler am Standardpfad erwarten: ``robots.txt``,
  ``llms.txt``, ``llms-full.txt``, ``security.txt``, ``favicon.ico``,
* die drei Scheduler-Funktionen ``send_due_reminders``,
  ``compile_daily_stats`` und ``send_daily_report``, aufgerufen aus
  ``apps.py`` - sie sind trotz ihres Platzes hier **keine** Views.

Preiszahlen, Zeitzusagen, Bewertungen und Stammdaten stehen nie in dieser
Datei, sondern in ``apps/core/data/`` (Regeln 1, 2, 24, 25).

Die Datei traegt ein UTF-8-BOM - eigene Skripte brauchen
``encoding='utf-8-sig'`` (``docs/fallen.md``).
"""

import datetime
import html as _html
import hmac
import json
import logging
import re as _re
import threading
import urllib.request
import urllib.error
from django.shortcuts import render, redirect
from django.http import (
    HttpResponsePermanentRedirect, HttpResponse, HttpResponseNotAllowed,
    JsonResponse, Http404, RawPostDataException,
)
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.conf import settings
from django.utils.html import strip_tags
from .context_processors import _safe_site_url
from .forms import AnfrageForm, TerminForm
from .antispam import (
    client_ip, ist_spam, mail_budget_erschoepft, mail_budget_ok, pruefen, rate_limited,
)
# Dauerhafte Weiterleitungen laufen ueber diese eine Funktion: GET/HEAD 301,
# alles andere 308. Ein nackter 301 auf einen POST wirft den Rumpf weg.
# Kein Zirkel: middleware.py importiert aus views.py nichts.
from .middleware import dauerhaft_weiter
# Frueher Import, nicht unten bei den uebrigen data-Namen: Diese beiden werden
# auf MODULEBENE gebraucht (``_STANDORT_REIHENFOLGE``), nicht erst beim Aufruf.
# Ein Zirkel ist ausgeschlossen - kein Modul unter data/ importiert aus
# apps.core (Regel 4).
from .data import firma as _firma
from .data import cities as _cities
from .data.cities import REGIONEN as _REGIONEN
from .data import feste_dateien as _feste


def _cities_wort():
    """Das Zahlwort zur Aufrufzeit - siehe Begruendung in ``ueber_uns``."""
    return _cities.REGIONEN_WORT

logger = logging.getLogger('apps.core')


def _doppelt(model, felder, minuten=15):
    """True, wenn **woertlich dieselbe** Einsendung gerade eben schon ankam.

    Der Bot vom 25.08.2026 schickte dieselbe Kombination im Minutentakt
    erneut. Auch ein Mensch, der nach dem Absenden ungeduldig neu laedt,
    profitiert davon: Er loest keine zweite Benachrichtigung aus.

    WARUM DER SCHLUESSEL DEN INHALT ENTHAELT (geaendert am 06.09.2026, P8/C1)
    ----------------------------------------------------------------------
    Bis dahin bestand der Schluessel an allen drei Aufrufstellen aus **Name
    und E-Mail**. Der Inhalt ging nicht ein - und damit ging der Fall
    verloren, den dieses Formular am haeufigsten sieht:

        Ein Interessent schickt um 14:02 eine Anfrage fuer eine Wohnung in
        Halle. Um 14:09 faellt ihm ein, dass auch der Keller im Nachbarhaus
        geraeumt werden soll, und er schickt eine zweite - andere Adresse,
        andere Leistungsart, andere Beschreibung. Sie wurde verworfen, nicht
        gespeichert, keine Mail. Er sah "Danke! Ihre Anfrage wurde
        gespeichert."

    Dasselbe auf ``/preisangebot/``: Wer zwei Objekte durchrechnet und sich
    beide Angebote schicken laesst, bekam das zweite nie - **genau wofuer der
    Rechner gebaut ist.**

    Die Feldliste kommt deshalb seitdem von der **Aufrufstelle**, und sie
    enthaelt je Modell die Felder, die eine Einsendung von einer anderen
    unterscheiden:

    ``Anfrage``               ``name, email, leistung, adresse, zusatz_info``
    ``Kooperationsanfrage``   ``name, email, art, nachricht``
    ``PreisAngebot``          ``name, email, leistung_label, groesse_label,
                              pmin, pmax``
    ``Bewerbung``             ``name, email, stelle, nachricht``

    Nicht in den Schluessel gehoert, was denselben Vorgang nur anders
    schreibt: ``telefon`` (mal mit, mal ohne Vorwahl) und ``firma``. Wer dort
    ein Feld ergaenzt, das ein Browser beim Neuladen veraendern kann, macht
    die Sperre wirkungslos, ohne dass etwas rot wird.

    GEGENRECHNUNG NACH REGEL 18 - kommt der Bot dadurch neu durch?
    -------------------------------------------------------------
    **Nein**, und das ist nachgerechnet, nicht abgeschrieben (der Beleg steht
    als eigener Test in ``test_views.py``). Der Angreifer vom 25.08.2026
    schickte dieselbe Kombination im Minutentakt und variierte **nur die
    Wegwerf-Adresse**. Gegen ihn hat die Duplikatsperre nie getragen: Sie
    greift ausschliesslich bei **gleicher** Mailadresse, und genau die
    wechselte er. Was ihn stoppt, sind drei andere Instanzen:

    * :func:`antispam.ist_spam` - er fuehrte kein JavaScript aus
      (``kein-js``, +3) und POSTete unmittelbar nach dem GET
      (``token-fehlt``/``zu-schnell``, +3): Score 6 bei Schwelle 5;
    * :func:`antispam.rate_limited` - fuenf Einsendungen je IP und Stunde,
      dazu ein Zaehler auf dem /24;
    * :func:`antispam.mail_budget_ok` - 15 Admin-Mails je Stunde ueber alle
      Formulare zusammen.

    Ein Schluessel, der mehr Felder enthaelt, kann nur **weniger** verwerfen.
    Alles, was der erweiterte Schluessel jetzt durchlaesst, hatte vorher schon
    dieselbe Mailadresse **und** denselben Namen - ein Muster, das der
    Angreifer gerade nicht zeigte.

    WAS DIESE FUNKTION NICHT LEISTET
    --------------------------------
    * Sie liest und schreibt nicht atomar. Zwei gleichzeitige, identische
      POSTs sehen beide "nichts da" und kommen beide durch.
    * Sie erkennt keine Umformulierung. Ein Zeichen Unterschied im Freitext
      ist eine neue Einsendung - hier bewusst, denn der Preis eines
      Fehlurteils ist auf dieser Seite **ein verlorener Auftrag**, nicht eine
      Mail zu viel.
    """
    from django.utils import timezone
    grenze = timezone.now() - datetime.timedelta(minutes=minuten)
    return model.objects.filter(erstellt_am__gte=grenze, **felder).exists()


# ── Mailversand: Thread, Erfolgsvermerk und Nachzuegler (P8/C3) ─────────────
#
# Der Versand laeuft in einem ``daemon=True``-Thread, damit der Request nicht
# zehn Sekunden auf Resend wartet. ``daemon=True`` heisst aber auch: Beim
# Beenden des Prozesses wird der Thread **ohne Aufraeumen abgebrochen**.
# Gunicorn recycelt Worker, jedes Deployment beendet alle. Trifft das einen
# Thread zwischen ``start()`` und der Rueckkehr von
# ``urlopen(..., timeout=10)``, verschwindet die Mail **ohne Logeintrag** -
# der ``except``-Zweig in ``emails.py`` kommt gar nicht mehr zum Zug.
#
# Deshalb vermerkt jeder Versand seinen Erfolg am Datensatz, und ein
# stuendlicher Nachzuegler holt nach, was liegengeblieben ist. Warum es dafuer
# ZWEI Felder braucht und nicht eines, steht im Docstring von
# ``models.VersandStatus``.

#: Vorlauf, bevor der Nachzuegler einen Datensatz anfasst. Kuerzer waere ein
#: Wettlauf mit dem noch laufenden Thread (der wartet bis zu 10 s je Mail,
#: zwei Mails je Einsendung).
_NACHZUEGLER_VORLAUF_MINUTEN = 15

#: Obergrenze. Eine Benachrichtigung ueber eine Anfrage von vor drei Wochen
#: ist keine Benachrichtigung mehr, sondern eine Irritation - und ein
#: Datensatz, der dauerhaft scheitert, wuerde sonst stuendlich das Log fuellen
#: und das Mailbudget belasten. Was hier herausfaellt, ist ein Fall fuer einen
#: Menschen; sichtbar bleibt er im Admin an ``mail_gesendet=False``.
_NACHZUEGLER_MAX_TAGE = 7


def _versand_ausfuehren(model, pk, funktion, args):
    """Verschickt und vermerkt den Erfolg. Gibt zurueck, ob es geklappt hat.

    Absichtlich eine eigene, benannte Funktion und nicht ein Lambda im
    Thread: So laesst sie sich **synchron** pruefen. Was ein Thread in die
    Datenbank schreibt, ist innerhalb einer ``TestCase``-Transaktion nicht
    verlaesslich beobachtbar - ein Test darauf waere entweder flatterhaft
    oder immer gruen.

    Ausnahmen werden hier NICHT geschluckt; das macht der Aufrufer, der weiss,
    ob er in einem Thread laeuft (dort darf nichts nach oben durchschlagen)
    oder im Nachzuegler (dort wird die Beanspruchung zurueckgerollt).
    """
    erfolg = bool(funktion(*args))
    if erfolg:
        model.objects.filter(pk=pk).update(mail_gesendet=True)
    return erfolg


def _versand_im_hintergrund(model, pk, funktion, args):
    """Startet den Versand im Daemon-Thread - der erste Versuch.

    Schlaegt er fehl oder wird er vom naechsten Deploy abgeschnitten, bleibt
    ``mail_gesendet=False`` stehen und :func:`_mail_nachzuegler` holt ihn
    nach. Deshalb wird hier **nichts vorab** auf ``True`` gesetzt: Ein
    optimistischer Vermerk waere genau der Fehler, den C3 behebt.
    """
    def _lauf():
        erfolg = None
        try:
            erfolg = _versand_ausfuehren(model, pk, funktion, args)
        except Exception:                                       # noqa: BLE001
            # Ein Fehler im Thread darf niemanden mitreissen, aber still darf
            # er auch nicht sein - sonst ist wieder niemand da, der es merkt.
            erfolg = False
            logger.warning('Versand-Thread abgebrochen | %s id=%s',
                           model.__name__, pk, exc_info=True)
        finally:
            # Der Thread hat eine eigene DB-Verbindung geoeffnet. Ohne diese
            # Zeile bleibt sie bis zum Prozessende stehen; bei Railways
            # Verbindungsobergrenze summiert sich das ueber Wochen.
            from django.db import connections
            connections.close_all()

    threading.Thread(target=_lauf, daemon=True).start()


# ── Telegram-Push (24.09.2026) ──────────────────────────────────────────────
#
# Derselbe Aufbau wie beim Mailversand, aber **getrennt**: eigener Thread,
# eigenes Feld (``push_gesendet``), eigener Nachzuegler. Ein haengender
# Telegram-Aufruf darf keine Mail aufhalten und umgekehrt. Ausgeloest wird der
# Push an genau derselben Entscheidung wie die Mail (``mail_gewollt``): kein
# Push fuer Spam, Verdacht, Duplikat oder Notbremse.

def _push_ausfuehren(model, pk):
    """Schickt den Push zu einem Datensatz und vermerkt den Erfolg (synchron)."""
    from . import telegram
    obj = model.objects.filter(pk=pk).first()
    if obj is None:
        return False
    if telegram.senden(telegram.nachricht_fuer(obj)):
        model.objects.filter(pk=pk).update(push_gesendet=True)
        return True
    return False


def _push_im_hintergrund(model, pk):
    """Startet den Push im Daemon-Thread - nur, wenn Telegram eingerichtet ist."""
    from . import telegram
    if not telegram.aktiv():
        return

    def _lauf():
        try:
            _push_ausfuehren(model, pk)
        except Exception:                                       # noqa: BLE001
            logger.error('Push-Thread abgebrochen | %s id=%s',
                         model.__name__, pk, exc_info=True)
        finally:
            from django.db import connections
            connections.close_all()

    threading.Thread(target=_lauf, daemon=True).start()


def _benachrichtigen(model, pk, funktion, args):
    """Mail **und** Push fuer einen gespeicherten Lead - jeder im eigenen Thread.

    Aufgerufen wird diese Funktion nur nach Spam-Abwehr, Duplikatsperre und
    Mail-Budget.
    """
    _versand_im_hintergrund(model, pk, funktion, args)
    _push_im_hintergrund(model, pk)


# audit-ok P16: Ausnahmeklasse, keine View - wird in _lead_speichern geworfen und endet bewusst in der 500-Seite samt Fehlerwache
class LeadNichtGesichert(Exception):
    """Speichern gescheitert **und** kein Notfallkanal hat den Betrieb erreicht."""


def _lead_speichern(erzeugen, art, funktion, args, push_felder):
    """Speichert einen Lead - und meldet ihn trotzdem, wenn das scheitert.

    **Warum (24.09.2026):** Der Preisrechner scheiterte vom 06. bis
    24.09.2026 bei **jeder** Einsendung am Speichern (eine Spalte ``ort`` mit
    NOT NULL in der Produktionsdatenbank, die das Model nicht kannte - siehe
    Migration 0020). Weil der Versand erst nach dem Speichern startete, ging
    mit dem Datensatz auch die Benachrichtigung verloren, und der Kunde sah
    einen 500.

    Jetzt: Scheitert ``erzeugen()`` an der Datenbank, steht das als
    ``logger.error`` in der Fehlerwache, und Mail und Push gehen **direkt aus
    den Formulardaten** hinaus - ohne Datensatz, also ohne Nachzuegler, aber
    der Betrieb erfaehrt von der Anfrage. Gibt den Datensatz oder ``None``
    zurueck.

    **EIG303 (27.09.2026):** Der Notfallversand laeuft seitdem **in der
    Anfrage**, nicht mehr im Hintergrund, und meldet zurueck, ob ueberhaupt ein
    Kanal den Betrieb erreicht hat. Vorher startete er einen Thread, dessen
    Ergebnis niemand las - gab das Mailbudget keinen Versand frei und scheiterte
    auch der Push, existierte weder ein Datensatz noch ein Nachzuegler, und der
    Kunde bekam trotzdem "eingegangen" zu lesen. Hat kein Kanal getragen,
    wirft die Funktion ``LeadNichtGesichert``: Die 500-Seite nennt Telefon und
    WhatsApp, und die Fehlerwache sieht den Verlust. Ausgenommen ist der
    Verdacht (leere ``args``): Er ist kein Kunde, sein Verlust ist gewollt.
    """
    from django.db import DatabaseError, transaction
    try:
        with transaction.atomic():
            return erzeugen()
    except DatabaseError:
        logger.error('Lead NICHT gespeichert - Notfallversand | %s', art,
                     exc_info=True)

    from . import telegram
    mail_ok = mail_budget_ok()

    gesichert = False
    if mail_ok:
        admin_ok = False
        try:
            admin_ok = bool(funktion(*args))
        except Exception:                                       # noqa: BLE001
            logger.error('Notfallversand Mail fehlgeschlagen | %s', art,
                         exc_info=True)
        gesichert = admin_ok
    try:
        if telegram.senden(telegram.nachricht(art, push_felder)):
            gesichert = True
    except Exception:                                           # noqa: BLE001
        logger.error('Notfallversand Push fehlgeschlagen | %s', art,
                     exc_info=True)

    if args and not gesichert:
        logger.error('Lead VERLOREN - weder Mail noch Push haben getragen | %s | '
                     'mail_budget=%s', art, 'frei' if mail_ok else 'erschoepft')
        raise LeadNichtGesichert(art)
    return None


def _push_nachzuegler():
    """Holt Pushes nach, deren Thread gestorben ist oder deren Aufruf scheiterte.

    Dieselben Regeln wie :func:`_mail_nachzuegler`: nur ``mail_gewollt=True``
    (nie Spam, Verdacht, Duplikat, Notbremse), 15 Minuten Vorlauf, hoechstens
    sieben Tage, atomarer Claim auf ``push_gesendet``. Ohne Telegram-
    Konfiguration tut er nichts.

    ⚠ Wird Telegram erst eingeschaltet, holt der erste Lauf die Anfragen der
    letzten sieben Tage nach - einmal. Das ist gewollt (nichts geht verloren),
    steht aber in ``docs/betrieb.md``, damit es niemanden ueberrascht.
    """
    from django.utils import timezone
    from . import telegram
    from .leads import modelle

    if not telegram.aktiv():
        return 0
    jetzt = timezone.now()
    gesendet = 0
    for _, _, model in modelle():
        offen = model.objects.filter(
            mail_gewollt=True, push_gesendet=False,
            erstellt_am__lte=jetzt - datetime.timedelta(minutes=_NACHZUEGLER_VORLAUF_MINUTEN),
            erstellt_am__gte=jetzt - datetime.timedelta(days=_NACHZUEGLER_MAX_TAGE),
        )
        for obj in list(offen):
            if not model.objects.filter(pk=obj.pk, push_gesendet=False) \
                    .update(push_gesendet=True):
                continue
            try:
                erfolg = telegram.senden(telegram.nachricht_fuer(obj))
            except Exception:                                   # noqa: BLE001
                logger.error('Push-Nachzuegler fehlgeschlagen | %s id=%s',
                             model.__name__, obj.pk, exc_info=True)
                erfolg = False
            if erfolg:
                gesendet += 1
            else:
                model.objects.filter(pk=obj.pk).update(push_gesendet=False)
    if gesendet:
        logger.info('Push-Nachzuegler | %d Push(es) nachgeholt', gesendet)
    return gesendet


#: Ab so vielen Stunden ohne Mail meldet der Waechter einen Datensatz.
_WAECHTER_STUNDEN = 2


def _versand_waechter():
    """Stuendlich: "Mail gewollt, nicht gesendet, aelter als 2 Std." melden.

    Der Nachzuegler holt still nach; ob er es schafft, sagte bis zum
    24.09.2026 niemand. Dieser Waechter schreibt dann eine ``logger.error``-
    Zeile (die Fehlerwache macht daraus ein ``Fehlerereignis``) und schickt
    einen Telegram-Alarm - denn wenn der Mailweg kaputt ist, erreicht auch die
    Sammelmail der Fehlerwache niemanden.

    Betrachtet wird das Fenster des Nachzueglers (bis sieben Tage); was
    darueber hinausfaellt, meldet der Nachzuegler selbst einmal ("gibt auf").
    Gibt die Zahl der gemeldeten Datensaetze zurueck.
    """
    from django.utils import timezone
    from . import telegram
    from .leads import modelle

    jetzt = timezone.now()
    je_art = {}
    for _, anzeige, model in modelle():
        n = model.objects.filter(
            mail_gewollt=True, mail_gesendet=False,
            erstellt_am__lte=jetzt - datetime.timedelta(hours=_WAECHTER_STUNDEN),
            erstellt_am__gte=jetzt - datetime.timedelta(days=_NACHZUEGLER_MAX_TAGE),
        ).count()
        if n:
            je_art[anzeige] = n
    gesamt = sum(je_art.values())
    if gesamt:
        aufstellung = ', '.join(f'{k}: {v}' for k, v in je_art.items())
        logger.error('Waechter: %d Benachrichtigung(en) gewollt, aber seit ueber '
                     '%d Std. nicht gesendet | %s', gesamt, _WAECHTER_STUNDEN,
                     aufstellung)
        telegram.alarm(f'{gesamt} Anfrage(n) seit über {_WAECHTER_STUNDEN} Std. '
                       f'ohne Mail ({aufstellung}). Mailweg prüfen.', 'waechter')
    return gesamt


#: Spamverdacht (Variante A) wird nach so vielen Tagen geloescht.
VERDACHT_AUFBEWAHRUNG_TAGE = 30


def _verdacht_aufraeumen():
    """Naechtlich: Verdachtsfaelle aelter als 30 Tage loeschen.

    Hier und nicht in ``leads_aufraeumen``: Jene Frist (730 Tage) gilt fuer
    echte Anfragen. Ein Verdacht ist nie beantwortet worden und hat keinen
    Grund, zwei Jahre zu liegen. Die Nachweiszeile nennt nur die Zahl.
    """
    from django.utils import timezone
    from .models import Anfrage as _Anfrage
    grenze = timezone.now() - datetime.timedelta(days=VERDACHT_AUFBEWAHRUNG_TAGE)
    geloescht, _ = _Anfrage.objects.filter(verdacht=True,
                                           erstellt_am__lt=grenze).delete()
    if geloescht:
        logger.info('Verdacht-Aufraeumer | %d Datensatz/-saetze geloescht '
                    '(aelter als %d Tage)', geloescht, VERDACHT_AUFBEWAHRUNG_TAGE)
    return geloescht


def _mail_nachzuegler():
    """Holt Benachrichtigungen nach, deren Thread den Deploy nicht ueberlebt hat.

    Laeuft stuendlich aus ``apps/core/apps.py``, neben ``send_due_reminders``,
    und benutzt denselben **atomaren Claim**: erst ``update()`` auf
    ``mail_gesendet=True``, dann senden, bei Misserfolg zurueckrollen. Zwei
    gunicorn-Worker koennen so nie dieselbe Mail zweimal schicken.

    **Er nimmt ausschliesslich ``mail_gewollt=True`` UND
    ``mail_gesendet=False``** - und das ist die teuerste Falle des ganzen
    Plans P8. Seit C1 wird auch eine woertlich gleiche Wiederholung
    gespeichert, und wenn ``mail_budget_ok()`` zuschlaegt, ist das Ausbleiben
    der Mail eine **Entscheidung**. Ein Nachzuegler, der nur auf
    ``mail_gesendet=False`` sieht, hoebe beide Entscheidungen wieder auf und
    stellte genau das zu, was gerade unterdrueckt worden ist. Seit dem
    24.09.2026 (Variante A) wird ausserdem der **Spamverdacht** gespeichert -
    immer mit ``mail_gewollt=False``, genau damit dieser Filter ihn nie
    zustellt. Eindeutiger Spam bleibt ungespeichert.

    ``mail_budget_ok()`` wird hier **nicht** erneut gezaehlt: Der Zaehler
    gehoert an den ersten Versuch. Sonst frisst ein Nachzuegler mit zwanzig
    liegengebliebenen Datensaetzen das Budget des naechsten echten Kunden.

    WAS DIESE FUNKTION NICHT LEISTET
    --------------------------------
    * Sie merkt nicht, ob die Mail **zugestellt** wird. ``True`` heisst: die
      Resend-API hat den Request angenommen.
    * Sie unterscheidet nicht zwischen "Thread gestorben" und "Resend war
      unerreichbar". Beides sieht gleich aus und wird gleich behandelt.
    * Sie holt nichts nach, was aelter ist als
      ``_NACHZUEGLER_MAX_TAGE`` Tage.
    """
    from django.utils import timezone
    from .models import (Anfrage as _Anfrage, Bewerbung as _Bewerbung,
                         Kooperationsanfrage as _Koop,
                         PreisAngebot as _PreisAngebot)

    jetzt = timezone.now()
    fruehestens = jetzt - datetime.timedelta(days=_NACHZUEGLER_MAX_TAGE)
    spaetestens = jetzt - datetime.timedelta(minutes=_NACHZUEGLER_VORLAUF_MINUTEN)

    # Je Modell die Funktion, die die Argumente aus dem Datensatz baut. Die
    # Namen der Versandfunktionen werden dabei erst beim Aufruf aufgeloest -
    # so greift eine Ersetzung im Test, und so steht hier keine zweite Liste,
    # die auseinanderlaufen kann.
    auftraege = (
        (_Anfrage, lambda o: (_send_anfrage_email, (
            o.name, o.get_leistung_display(), o.email, o.telefon, o.adresse,
            o.zusatz_info))),
        (_PreisAngebot, lambda o: (_send_rechner_emails, (
            o.name, o.email, o.leistung_label, o.groesse_label, o.pmin,
            o.ort))),
        (_Koop, lambda o: (_send_koop_emails, (
            o.name, o.firma, o.email, o.telefon, o.get_art_display(),
            o.nachricht))),
        (_Bewerbung, lambda o: (_send_bewerbung_emails, (
            o.name, o.email, o.stelle_anzeige(), o.nachricht, o.telefon))),
    )

    gesendet = 0
    for model, bauen in auftraege:
        offen = model.objects.filter(
            mail_gewollt=True, mail_gesendet=False,
            erstellt_am__lte=spaetestens, erstellt_am__gte=fruehestens,
        )
        for obj in list(offen):
            beansprucht = model.objects.filter(
                pk=obj.pk, mail_gesendet=False,
            ).update(mail_gesendet=True)
            if not beansprucht:
                continue                      # ein anderer Worker war schneller
            funktion, args = bauen(obj)
            try:
                erfolg = bool(funktion(*args))
            except Exception as exc:                            # noqa: BLE001
                logger.error('Nachzuegler fehlgeschlagen | %s id=%s | %s',
                             model.__name__, obj.pk, exc)
                erfolg = False
            if erfolg:
                gesendet += 1
            else:
                # Zurueckrollen, damit der naechste Lauf es erneut versucht -
                # genau wie in send_due_reminders.
                model.objects.filter(pk=obj.pk).update(mail_gesendet=False)

    if gesendet:
        logger.info('Mail-Nachzuegler | %d Benachrichtigung(en) nachgeholt',
                    gesendet)

    # Wer in dieser Stunde aus dem Sieben-Tage-Fenster faellt, wird nie mehr
    # versucht. Bis zum 24.09.2026 geschah das still; jetzt einmal als ERROR
    # (Fehlerwache) und als Telegram-Alarm. Das Ein-Stunden-Band sorgt dafuer,
    # dass jeder Datensatz genau einen Lauf lang gemeldet wird.
    aufgegeben = sum(
        model.objects.filter(
            mail_gewollt=True, mail_gesendet=False,
            erstellt_am__lt=fruehestens,
            erstellt_am__gte=fruehestens - datetime.timedelta(hours=1),
        ).count()
        for model, _ in auftraege)
    if aufgegeben:
        from . import telegram
        logger.error('Mail-Nachzuegler gibt auf | %d Benachrichtigung(en) nach '
                     '%d Tagen nicht zugestellt - im Dashboard unter Anfragen',
                     aufgegeben, _NACHZUEGLER_MAX_TAGE)
        telegram.alarm(f'{aufgegeben} Anfrage(n) nach {_NACHZUEGLER_MAX_TAGE} '
                       'Tagen nie per Mail zugestellt - bitte im Dashboard ansehen.',
                       'nachzuegler-gibt-auf')
    return gesendet


_CLOUDINARY_MARKER = '/image/upload/'
# Qualitaetsstufe nach Ausgabebreite. Bis 480 px landet das Bild in einer
# Karte oder einem Thumbnail von ~200 CSS-px – dort ist q_auto:low nicht von
# eco zu unterscheiden, spart bei den detailreichen Vorher-/Nachher-Fotos aber
# rund die Haelfte (gemessen: 4 Bilder der Startseite 245,6 -> 112,0 KiB).
# Ab 640 px bleibt es bei eco, weil die Bilder dann gross dargestellt werden.
_CLOUDINARY_Q_SMALL = 'q_auto:low'
_CLOUDINARY_Q_LARGE = 'q_auto:eco'
_CLOUDINARY_Q_BREAK = 480
_CLOUDINARY_TRANSFORM = 'f_auto,{quality},c_limit,w_{width}'


def _cloudinary_quality(width):
    """Qualitaetsparameter fuer eine Ausgabebreite."""
    return _CLOUDINARY_Q_SMALL if width <= _CLOUDINARY_Q_BREAK else _CLOUDINARY_Q_LARGE


def _cloudinary_optimize(url, width):
    """Insert delivery transformations into a Cloudinary URL.

    Non-Cloudinary URLs (lokales MEDIA-Storage, wenn CLOUDINARY_URL nicht
    gesetzt ist) werden unveraendert durchgereicht. Bereits transformierte
    URLs bleiben ebenfalls unangetastet (idempotent).
    """
    if not url or _CLOUDINARY_MARKER not in url:
        return url
    head, _, tail = url.partition(_CLOUDINARY_MARKER)
    # Schon transformiert? (erstes Pfadsegment enthaelt Cloudinary-Parameter)
    first_seg = tail.split('/', 1)[0]
    if 'f_auto' in first_seg or 'q_auto' in first_seg or first_seg.startswith('w_'):
        return url
    transform = _CLOUDINARY_TRANSFORM.format(
        quality=_cloudinary_quality(width), width=width,
    )
    return f'{head}{_CLOUDINARY_MARKER}{transform}/{tail}'


# Kandidatenbreiten fuer das srcset. Eine feste Zielbreite reicht nicht:
# Die Vorher-/Nachher-Karten werden auf dem Handy mit ~330 CSS-px dargestellt,
# bekamen aber die 700er Variante – laut PageSpeed 94,5 KiB Ballast allein auf
# der Startseite. Mit srcset+sizes waehlt der Browser die passende Stufe und
# beruecksichtigt dabei auch das Geraeteverhaeltnis (Retina bleibt scharf).
#
# Die Leiter ist bewusst eng: Mit den alten Stufen 320/480/640 brauchte das
# Handy 339 Geraete-px und bekam die 480er Variante – laut PageSpeed 27 KiB
# Ballast pro Bild. Mit einer 360er Stufe trifft der Browser die Anforderung
# fast exakt. Zusaetzliche Stufen kosten nur ein paar Byte HTML (die URLs
# unterscheiden sich in zwei Zeichen und komprimieren entsprechend gut).
_SRCSET_WIDTHS = (240, 320, 360, 420, 480, 640, 900, 1200)


# audit-ok P16: keine View, sondern eine str-Unterklasse fuer Bild-URLs
# (gebaut in _safe_image_url, gerendert in den Templates).
class ResponsiveImageUrl(str):
    """URL-String mit zusaetzlichem ``srcset``- und ``alt``-Attribut.

    Bewusst eine ``str``-Unterklasse: alle bestehenden Templates rendern
    ``{{ url }}`` weiterhin unveraendert, neue koennen zusaetzlich
    ``{{ url.srcset }}`` ausgeben. Bei lokalem Storage (kein Cloudinary)
    bleibt ``srcset`` leer, das Template gibt dann kein Attribut aus.

    ``alt`` kam mit IS25 (12.09.2026) dazu und aus demselben Grund: Die
    Beitragsbilder auf ``/``, ``/aktuelles/`` und den neun Leistungsseiten
    standen im Markup mit ``alt="Vorher"``, ``alt="Nachher"`` oder dem
    Beitragstitel - dieselbe Zeichenkette fuer jedes Bild eines Beitrags,
    waehrend die gepflegte Beschreibung (``AktuellesBild.bildtext``) daneben
    ungenutzt in der Datenbank lag. Sie wandert jetzt mit der URL, weil beide
    zum selben Bild gehoeren und getrennt gefuehrt wieder auseinanderliefen.

    (Kein ``__slots__`` – fuer Unterklassen von ``str`` verbietet CPython
    nichtleere Slots.)
    """

    def __new__(cls, url, srcset='', alt='', srcset_kurz=''):
        obj = super().__new__(cls, url)
        obj.srcset = srcset
        # Drei Stufen statt acht fuer die Startseiten-Karten: dort zaehlt
        # jedes Byte HTML (check_seo 170 KiB, live mit CMS-Inhalten knapp).
        obj.srcset_kurz = srcset_kurz or srcset
        obj.alt = alt
        return obj


def _cloudinary_srcset(url, width, stufen=_SRCSET_WIDTHS):
    """Baue ein ``srcset`` mit allen Stufen bis einschliesslich ``width``.

    Groessere Stufen waeren sinnlos – ``c_limit`` skaliert nie hoch, sie
    lieferten also dieselben Pixel unter anderer URL.
    """
    if not url or _CLOUDINARY_MARKER not in url:
        return ''
    widths = [w for w in stufen if w < width] + [width]
    return ', '.join(f'{_cloudinary_optimize(url, w)} {w}w' for w in widths)


def _safe_image_url(field, width=900, alt=''):
    """Return the URL of an ImageField without raising exceptions.

    ``width`` begrenzt die ausgelieferte Bildbreite bei Cloudinary-Storage
    (``c_limit`` skaliert nur herunter, nie hoch) und ist zugleich die
    groesste Stufe des mitgelieferten ``srcset``. Bei lokalem Storage ohne
    Wirkung.

    ``alt`` wird nur durchgereicht - gebaut wird der Text in
    ``AktuellesBild.alt_texte()``, damit Seite und Bildsitemap dieselbe
    Zeichenkette nennen.
    """
    try:
        if field and field.name:
            raw = field.url
            return ResponsiveImageUrl(
                _cloudinary_optimize(raw, width),
                _cloudinary_srcset(raw, width),
                alt,
                _cloudinary_srcset(raw, width, stufen=(360, 640)),
            )
    except Exception:
        # ``None`` bleibt das Ergebnis - eine Seite ohne Bild ist besser als
        # eine Seite mit 500. Aber still darf es nicht sein: Genau hier
        # verschwindet ein Beitragsbild spurlos, wenn Cloudinary eine URL
        # anders formt als erwartet, und niemand erfaehrt es.
        logger.warning('Bild-URL konnte nicht gebaut werden (Feld=%r)',
                       getattr(field, 'name', field), exc_info=True)
    return None


def _enrich_posts(qs):
    """Attach safe image URLs and gallery images to each post."""
    from .models import AktuellesBild
    posts = list(qs)
    if not posts:
        return posts
    post_ids = [p.pk for p in posts]
    bilder_qs = AktuellesBild.objects.filter(post_id__in=post_ids).order_by('reihenfolge', 'pk')
    bild_map: dict = {}
    alle_bilder = []
    for b in bilder_qs:
        bild_map.setdefault(b.post_id, []).append(b)
        alle_bilder.append(b)
    # Die alt-Texte in einem Zug (IS25). ``vollstaendig=True``, weil hier
    # bereits **alle** Bilder dieser Beitraege liegen - es braucht keine
    # zweite Abfrage, um die Wiederholungen zu erkennen. Der Beitrag wird von
    # Hand gesetzt statt per ``select_related``: Er liegt schon geladen vor,
    # und ohne ihn faellt ``alt_text()`` fuer jedes Bild einzeln in die
    # Datenbank zurueck.
    post_map = {p.pk: p for p in posts}
    for b in alle_bilder:
        b.post = post_map[b.post_id]
    alt_map = AktuellesBild.alt_texte(alle_bilder, vollstaendig=True)
    from .models import AUTOR_META
    for post in posts:
        # Vorher/Nachher-Bilder stehen immer in einer halbbreiten Spalte -> kleinere Zielbreite.
        # Die beiden Altfelder tragen keinen ``bildtext`` - sie sind ein
        # Einzelbild ohne eigene Beschreibung, ihr alt-Text ist der Titel.
        post.bild_vor_url  = _safe_image_url(post.bild_vor, width=700,
                                             alt=f'{post.titel} – vorher')
        post.bild_nach_url = _safe_image_url(post.bild_nach, width=700,
                                             alt=f'{post.titel} – nachher')
        all_bilder = bild_map.get(post.pk, [])
        post.gallery_urls     = [u for b in all_bilder if not getattr(b, 'typ_bild', '') if (u := _safe_image_url(b.bild, width=900, alt=alt_map.get(b.pk, '')))]
        post.vor_gallery_urls = [u for b in all_bilder if getattr(b, 'typ_bild', '') == 'vor' if (u := _safe_image_url(b.bild, width=700, alt=alt_map.get(b.pk, '')))]
        post.nach_gallery_urls= [u for b in all_bilder if getattr(b, 'typ_bild', '') == 'nach' if (u := _safe_image_url(b.bild, width=700, alt=alt_map.get(b.pk, '')))]
        # Backward compat: fall back to single bild_vor/bild_nach fields if no gallery images
        if not post.vor_gallery_urls and post.bild_vor_url:
            post.vor_gallery_urls = [post.bild_vor_url]
        if not post.nach_gallery_urls and post.bild_nach_url:
            post.nach_gallery_urls = [post.bild_nach_url]
        post.autor_info = AUTOR_META.get(post.autor) if post.autor else None
    return posts


def home(request):
    """Die Startseite - lange Landingpage mit Rechner, Stimmen und FAQ.

    Sie zeigt die zwei neuesten veroeffentlichten Beitraege (Seitengewicht, 01.10.2026); alles andere kommt
    aus ``data/`` (Preise ueber ``preis_context``, Bewertungen ueber den
    Context-Processor). ``seo_path`` ist hier ``"/"`` - und nur hier (Regel 6).
    """
    from .models import AktuellesPost
    preview = _enrich_posts(AktuellesPost.objects.filter(veroeffentlicht=True)[:2])
    pk = preis_context()
    return render(request, 'home.html', {
        'aktuelles_preview': preview,
        # Antwort-zuerst-Block (G2). Die Suchanfrage mit den meisten
        # Impressionen ist die nach dem Preis, und die Startseite faengt sie
        # heute ab - also beantwortet sie sie auch, in den ersten 48 Woertern.
        'antwort_frage': _start_antwort()[0],
        'antwort_text': _start_antwort()[1],
        'rezensionen': reviews.fuer_seite(),
        # Sichtbare Bewertungsanzeige mit Quelle/Stand; seit 06.10.2026 steht
        # sie nicht mehr im Schema (kein aggregateRating/review).
        'bewertung': reviews.stand(),
        # Alle 54 Stadtseiten (Befund W3). Nur ein Link von der Startseite
        # bringt eine Seite auf Klicktiefe 1 - die Vorlage listete 30 hart
        # getippte Staedte, die uebrigen 24 lagen deshalb auf Tiefe 2.
        'ALLE_STADTSEITEN': alle_stadtseiten(),
        # Sichtbare FAQ und Schema aus derselben Liste (EIG145/GE36).
        'home_faq': S.home_faq_paare(pk['PREISE'], pk['PREISSTAND']),
        'schema_bloecke': [S.home_faq_schema(pk['PREISE'], pk['PREISSTAND'])],
    })


# ── Blaettern auf den beiden CMS-Seiten (P8/D4) ─────────────────────────────
#
# ``/aktuelles/`` und ``/galerie/`` haben alles gerendert, was das CMS hergab:
# kein ``[:n]``, keine Paginierung. Jeder Beitrag darf bis zu
# ``GALERIE_MAX_BILDER`` (50) Bilder haben - die Seiten wuchsen also mit jedem
# Eintrag, bis sie die 170-KiB-Schwelle rissen, gegen die ``check_seo`` jede
# Seite haelt.
#
# **Und check_seo kann das nie melden**, weil es gegen die leere lokale
# Datenbank misst. Genau daran stand die Startseite vor dem 01.09.2026 live
# bei rund 188 KiB, waehrend der Lauf gruen war. Die Pruefung dazu steht in
# ``test_views.py`` und kann nur dort stehen - nur der Testlauf stellt eine
# gefuellte Datenbank her.
#
# Gemessen am 06.09.2026, 30 Beitraege zu je 20 Bildern:
#
#   /aktuelles/   188,6 KiB  ->  111,5 KiB
#   /galerie/     212,2 KiB  ->   77,6 KiB
#
# Und im Haertefall, den das CMS ueberhaupt zulaesst (50 Bilder je Beitrag,
# ``GALERIE_MAX_BILDER``): ``/aktuelles/`` 150,7 KiB - immer noch unter der
# Schwelle. Genau daran haengt die Wahl von zehn Beitraegen je Seite; bei
# fuenfzehn reisst der Haertefall die Grenze wieder.
#
# **Geblaettert wird ueber einen Query-Parameter, nicht ueber neue Pfade**
# (Regel 5): ``path('<slug:city_slug>/', …)`` ist ein Catch-All und muss das
# letzte Pattern bleiben. Mit ``?seite=2`` stellt sich die Frage gar nicht
# erst, und es entsteht keine URL, die in eine Sitemap geraten koennte.

#: Beitraege je Seite auf /aktuelles/. Setzung, keine Messung - gemessen ist
#: nur, dass die Seite damit unter der Schwelle bleibt.
AKTUELLES_JE_SEITE = 10

#: Bilder je Seite auf /galerie/.
GALERIE_JE_SEITE = 24


def _blaettern(request, qs, je_seite):
    """Eine Seite aus ``qs`` plus die Angaben fuers Blaettern im Template.

    Unsinnige Werte (``?seite=zwei``, ``?seite=0``, ``?seite=99999``) fuehren
    zur ersten bzw. letzten Seite, **nie** zu einem 404: Eine kaputte URL aus
    einem alten Lesezeichen oder einem Crawler-Log soll eine Seite zeigen,
    keinen Fehler.

    Was diese Funktion nicht leistet: Sie setzt kein ``canonical`` und kein
    ``noindex``. Beides kommt aus ``rw_seo.html`` und zeigt weiterhin auf die
    unparametrisierte URL - die Folgeseiten sind damit Blaetterwerk, kein
    eigenes Thema.
    """
    from django.core.paginator import Paginator

    paginator = Paginator(qs, je_seite)
    try:
        nummer = int(request.GET.get('seite', 1))
    except (TypeError, ValueError):
        nummer = 1
    nummer = max(1, min(nummer, paginator.num_pages))
    seite = paginator.page(nummer)
    return seite, {
        'seite': seite,
        'seiten_gesamt': paginator.num_pages,
        'eintraege_gesamt': paginator.count,
        'seite_vorher': f'?seite={nummer - 1}' if seite.has_previous() else '',
        'seite_naechste': f'?seite={nummer + 1}' if seite.has_next() else '',
    }


# Wie viele Zeichen des Beitragstextes in die ``description`` eines
# ``BlogPosting`` wandern (GE15). Der Volltext steht schon im HTML daneben; ihn
# vollstaendig zu wiederholen, kostet auf einer Seite mit zehn Beitraegen
# mehrere KiB gegen eine Schwelle von 170 KiB, ohne Google etwas Neues zu
# sagen. Gekuerzt wird an der Wortgrenze - ein mitten im Wort abgeschnittener
# Satz sieht wie ein Fehler aus.
_BEITRAG_TEXT_ZEICHEN = 200


def _beitrag_schema_daten(posts):
    """Die Beitraege fuer ``schema.blog_schema`` - aus **denselben** Objekten,
    die ``aktuelles.html`` rendert (Regel 12, GE15).

    **Kundenzitate bleiben draussen.** Ein Beitrag vom Typ ``zitat`` ist eine
    fremde Aussage ueber den Betrieb, kein Text des Betriebs; ihn als
    ``BlogPosting`` mit dem Betrieb als ``author`` auszugeben, waere eine
    falsche Urheberangabe. Bewertungsinhalt hat in diesem Projekt seinen
    eigene Quelle (``data/reviews.py``, Regel 2); ins Schema kommen Bewertungen
    seit 06.10.2026 gar nicht mehr.
    """
    aus = []
    for p in posts:
        if p.typ == 'zitat':
            continue
        bilder = (getattr(p, 'gallery_urls', None)
                  or getattr(p, 'vor_gallery_urls', None)
                  or getattr(p, 'nach_gallery_urls', None) or [])
        text = ' '.join((p.inhalt or '').split())
        if len(text) > _BEITRAG_TEXT_ZEICHEN:
            text = text[:_BEITRAG_TEXT_ZEICHEN].rsplit(' ', 1)[0] + ' …'
        autor = (p.autor_info or {}).get('name') if getattr(p, 'autor_info', None) else ''
        aus.append({
            'id': p.pk,
            'titel': p.titel,
            'datum': p.datum,
            'text': text,
            'bild': str(bilder[0]) if bilder else '',
            'autor': autor,
        })
    return aus


def aktuelles(request):
    """Das Archiv der CMS-Beitraege, geblaettert zu ``AKTUELLES_JE_SEITE``.

    Die Folgeseiten laufen ueber ``?seite=`` und tragen dasselbe ``canonical``
    (``_blaettern``) - sie sind keine eigenen Adressen und stehen deshalb in
    keiner Sitemap. Denselben Bestand in derselben Reihenfolge liefert der
    RSS-Feed unter ``/aktuelles/feed/`` (``feeds.py``).
    """
    from .models import AktuellesPost
    seite, blaettern = _blaettern(
        request, AktuellesPost.objects.filter(veroeffentlicht=True),
        AKTUELLES_JE_SEITE,
    )
    # _enrich_posts laedt die Galeriebilder nach - erst NACH dem Blaettern,
    # sonst holt die Seite die Bilder aller Beitraege und spart nur am HTML.
    posts = _enrich_posts(seite.object_list)
    return render(request, 'aktuelles.html', dict(
        blaettern, posts=posts,
        **_antwort_ctx(_seiten_antwort('aktuelles')),
        # GE15: Blog + je ein BlogPosting. 'name' ist der sichtbare h1-Text
        # der Seite. Eine 'description' bekommt der Blog-Knoten bewusst nicht -
        # die Seitenbeschreibung traegt seit G9 der WebPage-Knoten, und
        # derselbe Satz an zwei Stellen ist die naechste Doppelung, die
        # auseinanderlaeuft (Regel 12).
        schema_bloecke=S.blog_schema(
            _safe_site_url(), '/aktuelles/', 'Aktuelles', None,
            _beitrag_schema_daten(posts)),
    ))


# ── Einzelseite eines importierten GBP-Beitrags (Bauplan §7) ────────────────
#
# ``Aktuelles`` selbst bleibt eine Liste ohne eigene Adresse je Karte; nur
# Beitraege MIT ``slug`` (heute: die per ``gbp_beitraege_import`` importierten)
# bekommen zusaetzlich diese Einzelseite. Ein Beitrag ohne Slug (das komplette
# bisherige CMS-Archiv) hat keine Route hierher - ``AktuellesPost.objects
# .get(slug=slug, ...)`` findet ihn nie, weil sein ``slug`` ``''`` ist und die
# URL ein nicht-leeres ``<slug:slug>``-Segment verlangt.

#: Anhaengsel an einen GBP-Titel fuers ``<title>`` (Regel: Laenge 30-65 Zeichen).
# Kurzer Anhang wie bei den Stellen- und Ratgeberseiten ('… | Rümpelwerk',
# siehe data/jobs.py, data/ratgeber.py) - NICHT der lange Firmenname. Ein
# langer Anhang (vorher: ' – Aktuelles – Rümpelwerk Mitteldeutschland', 44
# Zeichen) liess bei der 65-Zeichen-Grenze fuer den eigentlichen Beitragstitel
# nur ~20 Zeichen uebrig und schnitt ihn auf ein bis zwei Woerter zusammen
# ("Heute eine | ...") - ein Titel, der nichts mehr ueber den Beitrag sagt.
_GBP_TITEL_ANHANG = ' | Rümpelwerk'


def _gbp_seo_titel(titel):
    """Baut einen Titel aus einem beliebig langen GBP-Text, Ziel 65 Zeichen.

    ``post.titel`` kommt bereits gekuerzt aus dem Import
    (``gbp_beitraege_import._titel_aus_text``, max. 70 Zeichen) - hier wird
    nur noch der kurze Anhang angefuegt und, falls die Summe die uebliche
    Titellaenge sprengt, am Wortende weiter gekuerzt.
    """
    basis = (titel or '').strip() or 'Neuigkeit'
    voll = f'{basis}{_GBP_TITEL_ANHANG}'
    if len(voll) <= 65:
        return voll
    max_basis = 65 - len(_GBP_TITEL_ANHANG)
    gekuerzt = basis[:max_basis].rsplit(' ', 1)[0] or basis[:max_basis]
    return f'{gekuerzt}{_GBP_TITEL_ANHANG}'


def _gbp_seo_beschreibung(text):
    """Baut eine 70-165 Zeichen lange Description aus dem Beitragstext."""
    text = ' '.join((text or '').split())
    if len(text) > 165:
        text = text[:165].rsplit(' ', 1)[0] + '…'
    if len(text) < 70:
        zusatz = ' Aktuelles von Rümpelwerk Mitteldeutschland in Halle und Leipzig.'
        text = (text + zusatz)[:165]
    return text


#: Unter dieser Wortzahl bekommt ein importierter Beitrag ``noindex`` - ein
#: zu kurzer GBP-Post traegt als eigenstaendige Seite nichts zum Index bei
#: (duenner Inhalt) und stuende trotzdem in der Sitemap, wenn nichts ihn
#: davon abhielte (Regel 21 gilt sinngemaess: keine noindex-Seite bewerben).
GBP_MINDESTWORTE_FUER_INDEX = 80


def aktuelles_beitrag(request, jahr, slug):
    """Die Einzelseite eines importierten GBP-Beitrags unter
    ``/aktuelles/<jahr>/<slug>/`` (Bauplan §7, GBP-Beitraege Stufe 1).

    Nur veroeffentlichte Beitraege mit einem Slug im angefragten Jahr - ein
    unveroeffentlichter Import (Wortlisten-Treffer, siehe
    ``gbp_beitraege_import``) ist hier ein 404, genau wie ein falsches Jahr.
    """
    from .models import AktuellesPost

    try:
        post = AktuellesPost.objects.get(
            slug=slug, datum__year=jahr, veroeffentlicht=True)
    except AktuellesPost.DoesNotExist:
        raise Http404

    site_url = _safe_site_url()
    pfad = f'/aktuelles/{jahr}/{slug}/'
    wortanzahl = len((post.inhalt or '').split())
    noindex = wortanzahl < GBP_MINDESTWORTE_FUER_INDEX

    return render(request, 'aktuelles_beitrag.html', {
        'post': post,
        'seo_title': _gbp_seo_titel(post.titel),
        'seo_description': _gbp_seo_beschreibung(post.inhalt),
        'seo_path': pfad,
        'seo_noindex': noindex,
        # Der Brotkrumen kommt ueber seo_breadcrumb_name/-zwischen im Template
        # (wie job_detail.html), NICHT zusaetzlich hier als eigener
        # breadcrumb_schema()-Block - rw_head_schema() baut ihn aus
        # seo_breadcrumb_name selbst; ein zweiter Block waere ein doppeltes
        # BreadcrumbList im selben Graph (siehe Kommentar in rw_schema.py).
        #
        # Ohne Index kein Schema - ein BlogPosting fuer eine Seite zu
        # behaupten, die niemand finden soll, waere Regel 12 in anderer Form.
        'schema_bloecke': [] if noindex else [
            S.beitrag_schema(site_url, pfad, post.titel, post.datum,
                             text=_gbp_seo_beschreibung(post.inhalt)),
        ],
    })


def dienstleistungen(request):
    """Die Uebersicht ueber alle Leistungen - Verteiler zu den neun Seiten.

    Der Antwort-zuerst-Block (G2) kommt aus ``data/antworten.py``, nicht aus
    dem Template.
    """
    _frage, _antwort = _hub_antwort('dienstleistungen')
    vergleich = hub_vergleich()
    return render(request, 'dienstleistungen.html', {
        # Antwort-zuerst-Block (G2), Text aus data/antworten.py.
        'antwort_frage': _frage,
        'antwort_text': _antwort,
        # Alle Leistungen mit eigener Seite - aus _SERVICE_DATA, damit eine
        # neue Leistung hier nicht nachgetragen werden muss. Der Hub ist in
        # A14 das Elternteil der Leistungsseiten; ohne diese Liste fuehrte
        # der Weg dorthin nur ueber Navigation und Footer, also ueber
        # Bereiche, die auf jeder Seite stehen und deshalb wenig aussagen.
        'leistungen_seiten': [
            {'name': l['label'], 'url': l['url'],
             'text': l['hero_sub'], 'keyword': l['keyword']}
            for l in alle_leistungen()
        ],
        # G11: die Orientierungstabelle. Eine Liste, weil das Template
        # dieselbe Schleife benutzt wie die Leistungsseiten - waere es hier ein
        # Einzelwert, gaebe es zwei Renderwege fuer dieselbe Tabelle.
        'vergleiche': [vergleich],
        # GE13/GE17 (16.09.2026): Die Service-Knoten stehen seitdem auf
        # oberster Ebene des Graphen, die Liste verweist per @id auf sie -
        # und die beiden sichtbaren Frage-Antwort-Paare sind ausgezeichnet.
        'schema_bloecke': [
            S.service_list_schema(_safe_site_url(), S.LEISTUNGEN),
            S.faq_schema([(_frage, _antwort),
                          (vergleich['fazit_frage'], vergleich['fazit'])]),
        ],
    })


def ueber_uns(request):
    """Die Seite ueber den Betrieb - Team, Flotte, Werte, TrustLocal-Widget.

    Die einzige Seite mit ``unsafe-eval`` in der CSP (das Widget braucht es,
    siehe ``middleware._CSP_EVAL_PFADE``) und die einzige mit einer **zweiten**
    Bewertungsquelle neben ``reviews.stand()`` - deshalb steht das Widget hier
    und nirgends sonst (Regel 2).
    """
    from .models import AUTOR_META

    # G6: Die vier Regionalleiter als Person-Knoten - und zwar genau hier,
    # weil sie genau hier sichtbar sind (Regel 12). Site-weit stuenden sie auf
    # 85 Seiten im JSON-LD, ohne dass 81 davon eine Person zeigen.
    # Regel 14: Ein ``{{ }}`` in einem ``{% include ... with %}``-Argument wird
    # nicht interpoliert - die Description muss deshalb hier fertig sein und als
    # Variable hinein. Regel 7 verlangt sie ausserdem an ZWEI Stellen (eigenes
    # <meta> und Include-Argument); beide lesen jetzt denselben Wert, statt ihn
    # zweimal zu tippen. Bis zum 06.09.2026 stand die Zahl an beiden von Hand.
    # Zur AUFRUFZEIT aus dem Modul gelesen, nicht beim Import gebunden: Ein
    # ``from ... import REGIONEN_WORT`` friert den Wert im Namensraum dieser
    # Datei ein. Im Betrieb faellt das nicht auf (der Prozess startet neu),
    # aber es macht die Zusage unpruefbar - ein Test, der die Quelle aendert,
    # saehe weiterhin den alten Wert. Genau daran ist der erste Anlauf
    # gescheitert.
    from .data import cities as _cities
    from .data import firma as _firma
    # EIG02.10.: keine "eigenen Teams an vier Standorten" - belegt ist nur die
    # Betriebsstaette in Halle; die Regionalleiter sind Ansprechpartner.
    # 02.10.2026: "Familienbetrieb" hatte keinen Beleg (SEO-Audit N4) -
    # belegt ist "inhabergefuehrt" (firma.INHABER).
    beschreibung = (f'Inhabergeführter Entrümpelungsbetrieb aus {_firma.ORT} (Saale) '
                    f'mit Ansprechpartnern in {_cities.REGIONEN_WORT} Regionen. Wie wir '
                    f'arbeiten und wer Ihren Auftrag betreut. Jetzt anfragen.')
    return render(request, 'ueber-uns.html', {
        'team': [dict(AUTOR_META[k], key=k) for k in AUTOR_META],
        'seo_beschreibung': beschreibung,
        # IS06/IS13: Ort im Titel (firma.py), die H1 sagt es anders.
        'seo_title': f'Über uns – Entrümpelungsfirma aus {_firma.ORT} | Rümpelwerk',
        'schema_bloecke': S.personen_schema(_safe_site_url(), list(AUTOR_META)),
        **_antwort_ctx(_seiten_antwort('ueber_uns')),
    })


def kontakt(request):
    """``/kontakt/`` zeigt dauerhaft auf ``/anfrage/``.

    GET/HEAD 301, alles andere 308 (``dauerhaft_weiter``). Bis zum 18.09.2026
    stand hier ein nackter 301: Ein POST aus einem alten Lesezeichen oder von
    einer fremden Seite waere als GET ohne Rumpf auf ``/anfrage/`` gelandet –
    die Anfrage waere weg gewesen, ohne dass es jemandem auffaellt.

    Ein POST von einer **fremden** Seite scheitert ohnehin schon am
    CSRF-Schutz; gerettet wird hier der eigene Fall - ein altes Lesezeichen
    oder ein Formular, das noch auf ``/kontakt/`` zeigt.
    """
    return dauerhaft_weiter('/anfrage/', request)


def _lead_kennung(email):
    """SHA-256 der normalisierten E-Mail - fuer erweiterte Conversions.

    Google verlangt genau diese Normalisierung: Kleinschreibung, aussen
    getrimmt. Gehasht wird **hier**, nicht im Browser: Die Klartext-Adresse
    soll das HTML nie erreichen, auch nicht auf der eigenen Erfolgsseite.

    Was diese Funktion nicht leistet: Sie prueft nicht, ob die Adresse echt
    ist. Ein Tippfehler wird zu einem gueltigen Hash, der bei Google auf
    niemanden passt - er schadet nicht, er hilft nur nicht.
    """
    import hashlib
    sauber = (email or '').strip().lower()
    if not sauber:
        return ''
    return hashlib.sha256(sauber.encode('utf-8')).hexdigest()


# ── Dankmeldungen (EIG274/EIG304) ────────────────────────────────────────────
#
# Je Formular **eine** Funktion, die jeder Zweig aufruft: echte Einsendung,
# Spam, Verdacht, Duplikat. Der Bot soll keinen Unterschied sehen (Regel 18) -
# bis zum 01.10.2026 las er "Danke! Ihre Anfrage wurde gespeichert.", der
# Mensch "Danke, Anna! ... Unser Team meldet sich in ...". Der Unterschied war
# messbar und damit eine Lernhilfe. Was sich zwischen den Zweigen unterscheidet,
# ist ausschliesslich ``request.session['rw_lead_kennung']`` (Conversion) und
# die Speicherung - nie die sichtbare Meldung.

def _danke_anfrage(name, zusage=True):
    """Dankmeldung von ``/anfrage/``.

    ``zusage=False`` (EIG369): nur fuer eine **echte, einzelne** Anfrage, deren
    Mail und Push das Mailbudget unterdrueckt hat. Dann erfaehrt der Betrieb
    von ihr hoechstens ueber die Notbremse (eine Sammelmeldung je Stunde,
    ``antispam._notbremse_melden``) - die Zeitzusage waere nicht gedeckt.
    """
    if zusage:
        return (f'Danke, {name}! Ihre Anfrage wurde gespeichert. '
                f'Unser Team meldet sich in {_ZUSAGE_REAKTION}.')
    from .data import firma as _firma
    return (f'Danke, {name}! Ihre Anfrage wurde gespeichert. Wir melden uns '
            f'bei Ihnen. Wenn es eilt, rufen Sie uns gern an: '
            f'{_firma.TELEFON_ANZEIGE}.')


def _danke_termin(name):
    """Dankmeldung von ``/termin/``."""
    return (f'Danke, {name}! Ihre Terminanfrage ist eingegangen. '
            'Oliver ruft Sie zur Bestätigung an.')


def _danke_kooperation(name):
    """Dankmeldung von ``/kooperationspartner/``."""
    return (f'Danke, {name}! Ihre Kooperationsanfrage ist eingegangen. '
            'Wir melden uns bei Ihnen.')


def _danke_bewerbung(name):
    """Dankmeldung von ``/jobs/`` und den Stellenseiten."""
    return f'Danke, {name}! Deine Bewerbung ist eingegangen. Wir melden uns bei dir.'


#: Vorbelegung des Freitextfelds auf /anfrage/ (``?anliegen=<schluessel>``, EIG278).
ANFRAGE_ANLIEGEN = {
    'ratenzahlung': 'Ich interessiere mich für eine Ratenzahlung und bitte um '
                    'ein unverbindliches Angebot.',
}


def _anfrage_ctx(form, **zusatz):
    """Kontext von ``anfrage.html``: Formular plus der Satz unter "Wie geht es
    nach Ihrer Anfrage weiter?" - aus ``antworten.anfrage_faq()``, derselben
    Quelle, die das Schema liest (Regel 12, EIG368)."""
    from .data.antworten import anfrage_faq
    return {'form': form, 'nach_anfrage_antwort': anfrage_faq()[1], **zusatz}


# audit-ok K06: öffentliches Anfrageformular für Kunden – CSRF, rate_limited und ist_spam (Regel 18)
# offen-ok: absichtlich ohne Anmeldung, Besucher schicken hier eine Anfrage ab
def anfrage(request):
    """Das Anfrageformular - der Hauptweg fuer Auftraege.

    Reihenfolge im POST, und sie ist Absicht: Pruefung der Felder,
    **dann** Rate-Limit (EIG146: ein ungueltiger Versuch zaehlt nicht mehr),
    Spam-Abwehr, Duplikatsperre, speichern, dann Mail und Telegram-Push im
    Hintergrund. Ein abgewiesener Bot sieht dieselbe Erfolgsmeldung wie ein
    Kunde - wer eine Fehlerseite saehe, variierte, bis er durchkommt
    (Regel 18). Die Sperre dagegen ist eine ehrliche Auskunft: Sie rendert
    das Formular **mit den Eingaben** neu (Status 429), statt umzuleiten und
    den getippten Text wegzuwerfen.

    Grenzfaelle der Spam-Abwehr (Variante A, 24.09.2026) werden als
    ``verdacht=True`` gespeichert - ohne Mail, ohne Push, ohne Conversion.
    """
    if request.method == 'POST':
        form = AnfrageForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data

            if rate_limited(request, 'anfrage', limit=5):
                messages.error(request, 'Zu viele Anfragen in kurzer Zeit. Ihre '
                               'Eingaben sind noch da – bitte versuchen Sie es in '
                               'einer Stunde erneut oder rufen Sie uns an.')
                return render(request, 'anfrage.html', _anfrage_ctx(form), status=429)

            urteil = pruefen(
                request, 'anfrage',
                name=d['name'], email=d['email'],
                telefon=d.get('telefon', ''), adresse=d.get('adresse', ''),
                text=d.get('zusatz_info', ''),
            )
            # Verworfene Einsendungen bekommen dieselbe Erfolgsmeldung wie
            # echte und werden NICHT gespeichert. Ein Bot, der eine Fehlerseite
            # saehe, wuerde variieren, bis er durchkommt.
            # EIG369/Regel 18: Ist das Mailbudget erschoepft, sieht die echte
            # Anfrage die neutrale Meldung - dann muessen Spam, Verdacht und
            # Duplikat dieselbe sehen, sonst verraet der Text, wer durchkam.
            zusage_ok = not mail_budget_erschoepft()
            if urteil == 'spam':
                messages.success(request, _danke_anfrage(d['name'], zusage=zusage_ok))
                return redirect('core:anfrage')

            from .models import Anfrage as _Anfrage
            if urteil == 'verdacht':
                # ``mail_gewollt=False`` ist Pflicht: Der Nachzuegler nimmt nur
                # ``mail_gewollt=True`` - ohne das stellte er den Verdacht zu.
                obj = _lead_speichern(
                    lambda: _Anfrage.objects.create(
                        verdacht=True, mail_gewollt=False, **d),
                    'anfrage', lambda: False, (), {})
                logger.info('Anfrage als Verdacht gespeichert | id=%s',
                            getattr(obj, 'pk', '-'))
                messages.success(request, _danke_anfrage(d['name'], zusage=zusage_ok))
                return redirect('core:anfrage')

            # Der Schluessel enthaelt seit dem 06.09.2026 den **Inhalt**
            # (P8/C1). Vorher genuegten Name und Mail - und die zweite,
            # inhaltlich andere Anfrage derselben Person ging verloren.
            duplikat = _doppelt(_Anfrage, {
                'name': d['name'], 'email': d['email'],
                'leistung': d['leistung'],
                'adresse': d.get('adresse', ''),
                'zusatz_info': d.get('zusatz_info', ''),
            })

            leistung_anzeige = dict(_Anfrage.LEISTUNG_CHOICES).get(
                d['leistung'], d['leistung'])
            mail_args = (d['name'], leistung_anzeige, d['email'],
                         d.get('telefon', ''), d.get('adresse', ''),
                         d.get('zusatz_info', ''))
            from . import telegram as _telegram
            obj = _lead_speichern(
                form.save, 'anfrage', _send_anfrage_email, mail_args,
                {'name': d['name'], 'telefon': d.get('telefon', ''),
                 'ort': _telegram.plz_ort(d.get('adresse', '')),
                 'objekt': leistung_anzeige})
            if obj is None:
                # Speichern gescheitert, Notfallversand laeuft. Der Kunde
                # bekommt eine ehrliche Meldung ohne "gespeichert".
                messages.success(request, 'Danke! Ihre Anfrage ist bei uns '
                                 f'eingegangen. Unser Team meldet sich in {_ZUSAGE_REAKTION}.')
                return redirect('core:anfrage')

            # Anders als bei Spam wird ein Duplikat **gespeichert**: Kein Lead
            # darf stillschweigend verschwinden. Verworfen wird nur die
            # Benachrichtigung (Mail und Push).
            versand_gewollt = not duplikat and mail_budget_ok()
            if versand_gewollt:
                _benachrichtigen(_Anfrage, obj.pk, _send_anfrage_email, (
                    obj.name, obj.get_leistung_display(), obj.email,
                    obj.telefon, obj.adresse, obj.zusatz_info,
                ))
            else:
                # ``mail_gewollt=False`` haelt beide Nachzuegler davon ab, die
                # Entscheidung eine Stunde spaeter aufzuheben.
                _Anfrage.objects.filter(pk=obj.pk).update(mail_gewollt=False)

            # Kein Name, keine Adresse im Log (P8/A4).
            logger.info('Anfrage gespeichert | id=%s | %s | mail=%s',
                        obj.pk, obj.get_leistung_display(),
                        'ja' if versand_gewollt else 'nein')
            if duplikat:
                logger.warning(
                    'Doppelte Anfrage - keine zweite Mail | id=%s | ip=%s',
                    obj.pk, client_ip(request) or 'unbekannt',
                )
                messages.success(request, _danke_anfrage(d['name'], zusage=zusage_ok))
                return redirect('core:anfrage')

            # Erst hier - nach dem Speichern. Die Zweige darueber (Spam,
            # Verdacht, Duplikat) zeigen dieselbe Erfolgsmeldung und setzen
            # sie bewusst NICHT: Sonst meldete Google einen Lead fuer etwas,
            # das keiner ist oder schon einmal gezaehlt wurde.
            request.session['rw_lead_kennung'] = _lead_kennung(obj.email)
            # EIG369: Hat das Mailbudget Mail **und** Push dieser echten
            # Anfrage unterdrueckt, steht sie nur im Dashboard - dann keine
            # Zeitzusage. (Das Duplikat ist oben schon abgefangen: seine
            # Erstanfrage wurde gemeldet, die Zusage gilt.)
            messages.success(request, _danke_anfrage(obj.name, zusage=versand_gewollt))
            return redirect('core:anfrage')
    else:
        # EIG278: Der Ratenzahlungs-Knopf auf /dienstleistungen/ gibt sein Anliegen
        # mit. Nur ein fester Schluessel aus ANFRAGE_ANLIEGEN wird uebernommen,
        # nie ein Text aus der Adresse - sonst stuende Fremdtext im Formular.
        anliegen = ANFRAGE_ANLIEGEN.get(request.GET.get('anliegen', ''))
        form = AnfrageForm(initial={'zusatz_info': anliegen} if anliegen else None)
    # `pop` statt `get`: Die Kennung gilt fuer genau einen Seitenaufruf. Bliebe
    # sie stehen, meldete ein Neuladen der Danke-Seite eine zweite Conversion.
    return render(request, 'anfrage.html', _anfrage_ctx(
        form, lead_kennung=request.session.pop('rw_lead_kennung', '')))


# audit-ok K06: öffentliches Terminformular für Kunden – CSRF, rate_limited und pruefen (Regel 18)
# offen-ok: absichtlich ohne Anmeldung, Besucher buchen hier eine Besichtigung
def termin(request):
    """Terminbuchung „Besichtigung vor Ort, 25 Minuten“ (Bauplan §5, ``/termin/``).

    Dieselbe Reihenfolge und dieselben Bausteine wie ``anfrage()``: Formular-
    pruefung, Rate-Limit (ein ungueltiger Versuch zaehlt nicht), Spam-Abwehr
    (``pruefen``), dann **erst speichern, dann melden**
    (``_lead_speichern``-Muster) und schliesslich Mail **nur an
    ``ADMIN_EMAILS``** sowie Telegram-Push. Ein abgewiesener Bot sieht dieselbe
    Erfolgsmeldung wie ein Kunde (Regel 18).

    Die Seite selbst ist ``/termin/`` (``templates/termin.html``, bindet
    ``{% rw_termin als_h1=True form=form %}`` ein) - reines POST + Redirect,
    funktioniert ohne JavaScript. Seit 02.10.2026 ist das die einzige Stelle der
    Terminbuchung (vorher zusaetzlich ungebunden auf der Startseite unter
    ``#termin``); Hero, Navigation und Laufband verlinken hierher.
    """
    from django.utils import timezone as _tz
    from . import telegram as _telegram
    from . import termine as _termine
    from .data import zusagen as _zusagen
    from .models import Besichtigungstermin as _Termin

    # Titel/Description gehen NICHT als getippter Text "25 Minuten" in die
    # Vorlage - Regel 1/24: die Zahl kommt aus zusagen.py, hier in der View
    # zusammengebaut und als Variable uebergeben (Regel 14 - {{ }} wird in
    # einem include-with-Argument nicht interpoliert).
    seo_ctx = {
        'seo_titel': 'Besichtigung online buchen – Rümpelwerk Mitteldeutschland',
        'seo_beschreibung': (
            f'Kostenlose Besichtigung vor Ort in {_zusagen.BESICHTIGUNG_DAUER} '
            'online buchen – Termin bei Rümpelwerk Mitteldeutschland in Halle '
            'und Leipzig.'),
    }

    if request.method == 'POST':
        form = TerminForm(request.POST)
        beginn = _termine.slot_aus_wert(request.POST.get('slot', ''))
        gueltig = form.is_valid()
        if gueltig and beginn is None:
            form.add_error('slot', 'Bitte wählen Sie einen Termin aus.')
            gueltig = False
        if gueltig and not _termine.slot_im_zeitraum(beginn):
            form.add_error('slot', 'Dieser Termin liegt nicht im buchbaren '
                           'Zeitraum. Bitte wählen Sie einen anderen Termin.')
            gueltig = False

        if not gueltig:
            return render(request, 'termin.html', {'form': form, **seo_ctx}, status=400)

        d = form.cleaned_data

        if rate_limited(request, 'termin', limit=5):
            messages.error(request, 'Zu viele Anfragen in kurzer Zeit. Ihre '
                           'Eingaben sind noch da – bitte versuchen Sie es in '
                           'einer Stunde erneut oder rufen Sie uns an.')
            return render(request, 'termin.html', {'form': form, **seo_ctx}, status=429)

        urteil = pruefen(
            request, 'termin',
            name=d['name'], email=d.get('email', ''),
            telefon=d.get('telefon', ''), adresse=d.get('adresse', ''),
            text=d.get('hinweis', ''),
        )
        if urteil == 'spam':
            messages.success(request, _danke_termin(d['name']))
            return redirect('core:termin')

        slot_ok = _termine.slot_frei(beginn)
        # Gespeichert wird immer auf die volle Minute (Ortszeit).
        beginn = _termine.slot_normieren(beginn)

        class _SlotVergeben(Exception):
            """Der Slot-Constraint hat gegriffen (Race) - kein Datenbankausfall."""

        def _anlegen(**felder):
            from django.db import IntegrityError
            try:
                return _Termin.objects.create(**felder)
            except IntegrityError:
                raise _SlotVergeben() from None

        if urteil == 'verdacht':
            # Ein Spamverdacht belegt keinen Slot: ist er nicht frei (oder
            # gewinnt jemand das Rennen), wird nichts gespeichert - der Absender
            # sieht trotzdem den normalen Dank (kein Hinweis fuer Bots).
            if not slot_ok:
                logger.info('Terminverdacht auf nicht freien Slot - nicht gespeichert')
                messages.success(request, _danke_termin(d['name']))
                return redirect('core:termin')
            # ``mail_gewollt=False`` ist Pflicht: der Nachzuegler nimmt nur
            # ``mail_gewollt=True`` - ohne das stellte er den Verdacht zu.
            try:
                obj = _lead_speichern(
                lambda: _anlegen(
                    verdacht=True, mail_gewollt=False, beginn=beginn,
                    besichtigungsart=d['besichtigungsart'],
                    objektart=d['objektart'], name=d['name'],
                    telefon=d.get('telefon', ''), adresse=d.get('adresse', ''),
                    email=d.get('email', ''), hinweis=d.get('hinweis', '')),
                'termin', lambda: False, (), {})
            except _SlotVergeben:
                obj = None
            logger.info('Terminanfrage als Verdacht gespeichert | id=%s',
                        getattr(obj, 'pk', '-'))
            messages.success(request, _danke_termin(d['name']))
            return redirect('core:termin')

        # Doppelbuchung: Der Slot ist per DB-Constraint eindeutig - diese
        # Vorabpruefung fängt den haeufigen Fall (jemand anderes hat
        # zwischen Rendern und Absenden gebucht) mit einer ehrlichen
        # Meldung ab, statt die Buchung als Notfallversand zu verlieren.
        if not slot_ok:
            form.add_error(
                'slot', 'Dieser Termin ist gerade vergeben, bitte wählen Sie '
                'eine andere Zeit.')
            return render(request, 'termin.html', {'form': form, **seo_ctx}, status=409)

        duplikat = _doppelt(_Termin, {
            'name': d['name'], 'adresse': d.get('adresse', ''),
            'objektart': d['objektart'],
        })

        objektart_anzeige = dict(_Termin.OBJEKTART_CHOICES).get(
            d['objektart'], d['objektart'])
        lokal_beginn = _tz.localtime(beginn)
        termin_text = (f'{lokal_beginn:%d.%m.%Y} · '
                       f'{_termine.slot_anzeige(lokal_beginn.strftime("%H:%M"))}')
        art_anzeige = dict(_Termin.ART_CHOICES).get(
            d['besichtigungsart'], d['besichtigungsart'])
        # Das achte Argument (Art der Besichtigung) kommt zuletzt, damit die
        # sieben bisherigen Positionen von ``emails._formular_daten`` bleiben.
        mail_args = (d['name'], d.get('telefon', ''), d.get('email', ''),
                    d.get('adresse', ''), objektart_anzeige, termin_text,
                    d.get('hinweis', ''), art_anzeige)

        try:
            obj = _lead_speichern(
            lambda: _anlegen(
                beginn=beginn, besichtigungsart=d['besichtigungsart'],
                objektart=d['objektart'], name=d['name'],
                telefon=d.get('telefon', ''), adresse=d.get('adresse', ''),
                email=d.get('email', ''), hinweis=d.get('hinweis', '')),
            'termin', _send_termin_email, mail_args,
            {'name': d['name'], 'telefon': d.get('telefon', ''),
             'ort': _telegram.plz_ort(d.get('adresse', '')),
             'objekt': objektart_anzeige, 'wunschtermin': termin_text,
             'art': art_anzeige})
        except _SlotVergeben:
            form.add_error(
                'slot', 'Dieser Termin ist gerade vergeben, bitte wählen Sie '
                'eine andere Zeit.')
            return render(request, 'termin.html', {'form': form, **seo_ctx}, status=409)

        if obj is None:
            # Speichern gescheitert, Notfallversand lief. Ehrliche Meldung
            # ohne "gespeichert" - genau wie bei anfrage().
            messages.success(request, 'Danke! Ihre Terminanfrage ist bei uns '
                             'eingegangen. Oliver ruft Sie zur Bestätigung an.')
            return redirect('core:termin')

        versand_gewollt = not duplikat and mail_budget_ok()
        if versand_gewollt:
            _benachrichtigen(_Termin, obj.pk, _send_termin_email, mail_args)
        else:
            _Termin.objects.filter(pk=obj.pk).update(mail_gewollt=False)

        logger.info('Terminanfrage gespeichert | id=%s | mail=%s',
                    obj.pk, 'ja' if versand_gewollt else 'nein')
        if duplikat:
            logger.warning('Doppelte Terminanfrage - keine zweite Mail | id=%s | ip=%s',
                           obj.pk, client_ip(request) or 'unbekannt')
            messages.success(request, _danke_termin(d['name']))
            return redirect('core:termin')

        # Conversion "Besichtigung gebucht" - wie bei ``anfrage()`` erst hier, nach dem
        # Speichern: Spam, Verdacht, Duplikat und Slot-Konflikt zeigen dieselbe
        # Meldung oder bleiben auf dem Formular und setzen sie bewusst NICHT.
        # Ohne E-Mail-Hash (Datenschutz: Hash nur bei Anfrage und Angebot).
        # Nur mit ``TERMIN_CONVERSION`` - siehe ``config/settings.py``.
        if settings.TERMIN_CONVERSION:
            request.session['rw_termin_gebucht'] = True
        messages.success(request, _danke_termin(obj.name))
        return redirect('core:termin')

    form = TerminForm()
    # ``pop``: gilt fuer genau einen Seitenaufruf - ein Neuladen der Danke-Seite
    # meldete sonst eine zweite Conversion (wie ``rw_lead_kennung``).
    return render(request, 'termin.html', {
        'form': form, 'termin_gebucht': request.session.pop('rw_termin_gebucht', False),
        **seo_ctx})


def leistungen(request):
    """/leistungen/ -> /dienstleistungen/ (F12).

    Die Seite stand seit dem Initial Commit auf ``noindex, nofollow`` - das war
    nie eine bewusste Entscheidung, es kam mit der Projektkopie mit. Sie hatte
    kein canonical, kein JSON-LD, stand nicht in der Sitemap und hatte null
    eingehende interne Links. Sie konkurrierte also mit nichts, lag aber als
    totes, jederzeit versehentlich indexierbares Template im Repo.

    Ihre 602 Woerter Leistungstext (Haushaltsaufloesung, Wohnungsaufloesung,
    Messie-Wohnungen, jeweils mit Detaillisten) sind gute Vorlage fuer die acht
    Leistungsseiten aus Block 2. Sie stehen weiter in der Historie:

        git show f0774c5:templates/leistungen.html

    301 statt 410, weil die URL extern verlinkt sein koennte – und ueber
    ``dauerhaft_weiter``, damit ein POST 308 bekommt statt 301.
    """
    return dauerhaft_weiter('/dienstleistungen/', request)


def impressum(request):
    return render(request, 'impressum.html')


def datenschutz(request):
    """Die Datenschutzerklaerung."""
    from .emails import _weg
    # ``mail_resend``: der Absatz zum E-Mail-Dienst nennt Resend statt IONOS,
    # sobald der Versand tatsaechlich ueber Resend laeuft (_weg() liest zur
    # Aufrufzeit; SMTP gewinnt, wenn beides gesetzt ist).
    return render(request, 'datenschutz.html', {'mail_resend': _weg() == 'resend'})


def agb(request):
    return render(request, 'agb.html')



def barrierefreiheit(request):
    """Erklaerung zur Barrierefreiheit (RE12, 01.10.2026): freiwillig, noindex,
    nicht in der Sitemap (Regel 21). Der Betrieb ist Kleinstunternehmen
    (BFSG, Ausnahme fuer Dienstleistungen); Kontakt aus ``firma.py``."""
    return render(request, 'barrierefreiheit.html')


# ---------------------------------------------------------------------------
# Kooperationspartner
# ---------------------------------------------------------------------------

_KOOP_ART_LABELS = {
    'subunternehmer': 'Subunternehmer / Nachunternehmer',
    'handwerker':     'Handwerker-Partner',
    'immobilien':     'Immobilienverwaltung / Verwalter',
    'makler':         'Makler / Immobilienmakler',
    'sonstiges':      'Sonstiges',
}


# audit-ok K06: öffentliches Kooperationsformular – CSRF, rate_limited und ist_spam (Regel 18)
# offen-ok: absichtlich ohne Anmeldung, Besucher schicken hier eine Anfrage ab
def kooperation(request):
    """Das Partnerformular unter ``/kooperationspartner/``.

    Derselbe Ablauf wie ``anfrage``, nur mit ``Kooperationsanfrage`` als Model
    und zwei Mails: eine an den Absender, eine an den Betrieb.
    """
    if request.method == 'POST':
        name     = request.POST.get('name', '').strip()[:200]
        firma    = request.POST.get('firma', '').strip()[:200]
        email    = request.POST.get('email', '').strip()[:200]
        telefon  = request.POST.get('telefon', '').strip()[:50]
        art      = request.POST.get('art', '').strip()
        nachricht = request.POST.get('nachricht', '').strip()[:2000]

        errors = {}
        if not name:
            errors['name'] = 'Bitte geben Sie Ihren Namen ein.'
        if not firma:
            errors['firma'] = 'Bitte geben Sie Ihren Firmennamen ein.'
        if not email or not _re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
            errors['email'] = 'Bitte geben Sie eine gültige E-Mail-Adresse ein.'
        if art not in _KOOP_ART_LABELS:
            errors['art'] = 'Bitte wählen Sie eine Kooperationsart.'

        if errors:
            return render(request, 'kooperation.html', {
                'errors': errors,
                'post': request.POST,
                **_antwort_ctx(_seiten_antwort('kooperation')),
            })

        # Erst nach der Feldpruefung zaehlen (EIG146) - und bei Sperre mit den
        # Eingaben neu rendern statt umleiten.
        if rate_limited(request, 'kooperation', limit=5):
            messages.error(request, 'Zu viele Anfragen in kurzer Zeit. Ihre Eingaben '
                           'sind noch da – bitte versuchen Sie es später erneut.')
            return render(request, 'kooperation.html', {
                'post': request.POST,
                **_antwort_ctx(_seiten_antwort('kooperation')),
            }, status=429)

        art_label = _KOOP_ART_LABELS[art]

        from .models import Kooperationsanfrage

        # Dieses Formular verschickt auch eine Bestaetigung an die EINGEGEBENE
        # Adresse. Ohne Pruefung waere es ein Versandweg fuer fremde Postfaecher
        # unter unserer Absenderdomain - das kostet die Zustellbarkeit aller
        # echten Mails. Deshalb wird hier vor jedem Versand geprueft.
        if ist_spam(
            request, 'kooperation',
            name=name, email=email, telefon=telefon, text=f'{firma} {nachricht}',
        ):
            messages.success(request, _danke_kooperation(name))
            return redirect('core:kooperation')

        # Art und Nachricht gehoeren in den Schluessel (P8/C1): Wer sich
        # zuerst als Makler und dann zusaetzlich als Handwerker anbietet,
        # schickt zwei verschiedene Angebote, keine Wiederholung.
        duplikat = _doppelt(Kooperationsanfrage, {
            'name': name, 'email': email, 'art': art, 'nachricht': nachricht,
        })

        # Reihenfolge wie in ``anfrage()``: erst speichern, dann das Budget
        # fragen. ``mail_budget_ok()`` zaehlt hoch - wer es vor dem Speichern
        # aufruft und danach an der Datenbank scheitert, hat ein Kontingent
        # fuer nichts verbraucht.
        obj = _lead_speichern(
            lambda: Kooperationsanfrage.objects.create(
                name=name, firma=firma, email=email,
                telefon=telefon, art=art, nachricht=nachricht,
            ),
            'kooperation', _send_koop_emails,
            (name, firma, email, telefon, art_label, nachricht),
            {'name': name, 'firma': firma, 'telefon': telefon, 'objekt': art_label})
        if obj is None:
            messages.success(request, _danke_kooperation(name))
            return redirect('core:kooperation')
        versand_gewollt = not duplikat and mail_budget_ok()
        if versand_gewollt:
            _benachrichtigen(
                Kooperationsanfrage, obj.pk, _send_koop_emails,
                (name, firma, email, telefon, art_label, nachricht))
        else:
            Kooperationsanfrage.objects.filter(pk=obj.pk).update(mail_gewollt=False)

        # Ohne Name und Firma (P8/A4) - beides steht im Datensatz. Die Art der
        # Kooperation ist eine feste Auswahl.
        logger.info('Kooperationsanfrage eingegangen | id=%s | %s | mail=%s',
                    obj.pk, art_label, 'ja' if versand_gewollt else 'nein')

        messages.success(request, _danke_kooperation(name))
        return redirect('core:kooperation')

    return render(request, 'kooperation.html',
                  _antwort_ctx(_seiten_antwort('kooperation')))


def _bewerbung_speichern(stelle, name, email, telefon, nachricht):
    """Legt die Bewerbung an und setzt ``mail_gewollt`` nach der Duplikatsperre.

    Gemeinsam fuer ``/jobs/`` und die drei Stellenseiten - ein zweiter,
    fast gleicher Block waere genau die Konstruktion, wegen der auf den
    Detailseiten monatelang ein ``NameError`` in jedem POST stand, ohne dass
    es jemandem auffiel.

    In den Duplikatsschluessel gehen ``stelle`` und ``nachricht`` ein: Wer
    sich auf zwei verschiedene Stellen bewirbt, bewirbt sich zweimal
    (P8/C1). ``telefon`` bleibt draussen - mal mit, mal ohne Vorwahl ist
    derselbe Vorgang.
    """
    from .models import Bewerbung
    duplikat = _doppelt(Bewerbung, {
        'name': name, 'email': email, 'stelle': stelle, 'nachricht': nachricht,
    })
    anzeige = Bewerbung(stelle=stelle).stelle_anzeige()
    # Scheitert das Speichern, gehen Mail und Push direkt hinaus
    # (``_lead_speichern``); der Aufrufer bekommt dann ``None``.
    return _lead_speichern(
        lambda: Bewerbung.objects.create(
            stelle=stelle, name=name, email=email, telefon=telefon,
            nachricht=nachricht, mail_gewollt=not duplikat,
        ),
        'bewerbung', _send_bewerbung_emails,
        (name, email, anzeige, nachricht, telefon),
        {'name': name, 'telefon': telefon, 'objekt': anzeige})


# audit-ok K06: öffentliche Initiativbewerbung – CSRF, rate_limited und ist_spam (Regel 18)
# offen-ok: absichtlich ohne Anmeldung, Besucher schicken hier eine Anfrage ab
def jobs(request):
    """Die Stellenuebersicht mit Kurzbewerbung.

    Die Stellen stehen in ``data/jobs.py`` und speisen sowohl die Seite als
    auch die ``JobPosting``-Knoten im Schema (Regel 12). Eine Bewerbung wird
    seit dem 06.09.2026 als ``Bewerbung`` gespeichert und nicht nur gemailt -
    vorher war sie beim kleinsten Versandfehler weg.
    """
    if request.method == 'POST':
        name     = request.POST.get('name', '').strip()[:200]
        email    = request.POST.get('email', '').strip()[:200]
        telefon  = request.POST.get('telefon', '').strip()[:50]
        stelle   = request.POST.get('stelle', '').strip()[:300]
        nachricht = request.POST.get('nachricht', '').strip()[:2000]

        errors = {}
        if not name:
            errors['name'] = 'Bitte gib deinen Namen ein.'
        if not email or not _re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
            errors['email'] = 'Bitte gib eine gültige E-Mail-Adresse ein.'
        if not telefon:
            errors['telefon'] = 'Bitte gib deine Telefonnummer ein.'
        if not stelle:
            errors['stelle'] = 'Bitte gib an, als was du dich bewerben möchtest.'

        if errors:
            return render(request, 'jobs.html', {'errors': errors, 'post': request.POST,
                                                 **_antwort_ctx(_job_antwort(None))})

        # Erst nach der Feldpruefung zaehlen, bei Sperre mit Eingaben (EIG146).
        if rate_limited(request, 'jobs', limit=5):
            messages.error(request, 'Zu viele Anfragen in kurzer Zeit. Deine Eingaben '
                           'sind noch da – bitte versuche es später erneut.')
            return render(request, 'jobs.html', {
                'post': request.POST, **_antwort_ctx(_job_antwort(None))}, status=429)

        # Auch hier geht eine Bestaetigung an die eingegebene Adresse.
        if ist_spam(
            request, 'jobs',
            name=name, email=email, telefon=telefon, text=f'{stelle} {nachricht}',
        ):
            messages.success(request, _danke_bewerbung(name))
            return redirect('core:jobs')

        # Seit dem 06.09.2026 wird die Bewerbung gespeichert (P8/C2). Sie
        # existierte vorher ausschliesslich als Mail - fiel der Versand aus,
        # war sie weg, und im Log stand ihr Name im Klartext (P8/A4).
        # ``stelle`` traegt hier den frei eingegebenen Wunsch; auf den drei
        # Stellenseiten steht dort der Slug.
        from .models import Bewerbung
        obj = _bewerbung_speichern(stelle, name, email, telefon, nachricht)
        if obj is None:
            messages.success(request, _danke_bewerbung(name))
            return redirect('core:jobs')
        versand_gewollt = obj.mail_gewollt and mail_budget_ok()
        if versand_gewollt:
            _benachrichtigen(
                Bewerbung, obj.pk, _send_bewerbung_emails,
                (name, email, stelle, nachricht, telefon))
        else:
            Bewerbung.objects.filter(pk=obj.pk).update(mail_gewollt=False)

        logger.info('Bewerbung eingegangen | id=%s | ueber /jobs/ | mail=%s',
                    obj.pk, 'ja' if versand_gewollt else 'nein')

        messages.success(request, _danke_bewerbung(name))
        return redirect('core:jobs')

    return render(request, 'jobs.html', _antwort_ctx(_job_antwort(None)))




# audit-ok K06: öffentliche Bewerbung auf eine Stelle – CSRF, rate_limited und ist_spam (Regel 18)
# offen-ok: absichtlich ohne Anmeldung, Besucher schicken hier eine Anfrage ab
def job_detail(request, job_slug):
    """Eine einzelne Stellenanzeige, mit demselben Bewerbungsformular.

    Unbekannter Slug ist ein 404. Genau hier hat der erste POST-Test einen
    Fehler gefunden, den ``check_seo`` nie finden konnte: Die View rief eine
    Funktion auf, die es nicht mehr gab - im GET sah die Seite tadellos aus,
    jede Bewerbung endete im 500.
    """
    job = _JOB_DATA.get(job_slug)
    if not job:
        from django.http import Http404
        raise Http404

    if request.method == 'POST':
        # Bis zum 01.09.2026 stand hier ``_is_rate_limited(ip, …)`` auf
        # ``REMOTE_ADDR``. Die Funktion ist am 25.08.2026 mit der alten Bremse
        # entfernt worden, der Aufruf blieb stehen: **Jede Bewerbung ueber eine
        # der drei Detailseiten endete seitdem in einem NameError und damit in
        # einem 500.** Der Fehler war unsichtbar, weil die Seite im GET
        # einwandfrei aussieht und niemand die Formulare durchprobiert hat.
        # Gefunden hat ihn der erste POST-Test dieser Seite.
        #
        # Jetzt dieselbe Abwehr wie in ``jobs()``: ``rate_limited`` ueber
        # ``client_ip`` (Regel 19 - hinter Railways Proxy ist ``REMOTE_ADDR``
        # eine interne Adresse, die pro Request wechselt) und ``ist_spam``
        # statt eines einzelnen Honeypots (Regel 18 - genau die Bestueckung,
        # mit der ``/anfrage/`` in der Nacht zum 25.08.2026 geflutet wurde).
        name     = request.POST.get('name', '').strip()[:200]
        email    = request.POST.get('email', '').strip()[:200]
        telefon  = request.POST.get('telefon', '').strip()[:50]
        nachricht = request.POST.get('nachricht', '').strip()[:2000]

        errors = {}
        if not name:
            errors['name'] = 'Bitte gib deinen Namen ein.'
        if not email or not _re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
            errors['email'] = 'Bitte gib eine gültige E-Mail-Adresse ein.'
        if not telefon:
            errors['telefon'] = 'Bitte gib deine Telefonnummer ein.'

        if errors:
            # EIG129: auch im Fehlerzweig die anderen Stellen - bis zum
            # 24.09.2026 verschwand der Block nach einem Tippfehler.
            return render(request, 'job_detail.html', dict(
                _job_detail_ctx(job, job_slug),
                errors=errors, post=request.POST))

        # Erst nach der Feldpruefung zaehlen, bei Sperre mit Eingaben (EIG146).
        if rate_limited(request, f'job_{job_slug}', limit=5):
            messages.error(request, 'Zu viele Anfragen in kurzer Zeit. Deine Eingaben '
                           'sind noch da – bitte versuche es später erneut.')
            return render(request, 'job_detail.html', dict(
                _job_detail_ctx(job, job_slug), post=request.POST), status=429)

        # Auch hier geht eine Bestaetigung an die eingegebene Adresse - ohne
        # Pruefung waere das ein Versandweg fuer fremde Postfaecher unter der
        # eigenen Absenderdomain.
        if ist_spam(
            request, f'job_{job_slug}',
            name=name, email=email, telefon=telefon,
            text=f"{job['title']} {nachricht}",
        ):
            messages.success(request, _danke_bewerbung(name))
            return redirect('core:job_detail', job_slug=job_slug)

        # Reihenfolge wie in ``anfrage()``: Spam-Pruefung -> Duplikatsperre ->
        # speichern -> Mail-Budget -> Versand (P8/C2). Bis zum 06.09.2026
        # fehlten die Schritte zwei und drei ganz: Die Bewerbung existierte
        # ausschliesslich als Mail, und die haengt an drei Bedingungen, die
        # alle stillschweigend scheitern koennen.
        from .models import Bewerbung
        obj = _bewerbung_speichern(job_slug, name, email, telefon, nachricht)
        if obj is None:
            messages.success(request, _danke_bewerbung(name))
            return redirect('core:job_detail', job_slug=job_slug)
        versand_gewollt = obj.mail_gewollt and mail_budget_ok()
        if versand_gewollt:
            _benachrichtigen(
                Bewerbung, obj.pk, _send_bewerbung_emails,
                (name, email, job['title'], nachricht, telefon))
        else:
            Bewerbung.objects.filter(pk=obj.pk).update(mail_gewollt=False)

        # Ohne Name, Mail und Telefon (P8/A4). Bewerberdaten sind nach
        # Paragraph 26 BDSG eine eigene Kategorie, und Railways Logspeicher
        # hat weder eine Loeschfrist noch einen Abschnitt in der
        # Datenschutzerklaerung. Der Zweck der Zeile ist "es kam eine
        # Bewerbung an", nicht "wer" - das steht seit C2 im Datensatz, und
        # **erst deshalb** darf die Zeile ueberhaupt gekuerzt werden: Vorher
        # war das Log der einzige Ort, an dem stand, dass sie ankam.
        logger.info('Jobbewerbung eingegangen | id=%s | %s | mail=%s',
                    obj.pk, job_slug, 'ja' if versand_gewollt else 'nein')

        messages.success(request, _danke_bewerbung(name))
        return redirect('core:job_detail', job_slug=job_slug)

    return render(request, 'job_detail.html', _job_detail_ctx(job, job_slug))


def _job_detail_ctx(job, job_slug):
    """Der Seitenkontext einer Stellenseite - fuer GET, Fehler und Sperre gleich."""
    return {
        'job': job,
        **_antwort_ctx(_job_antwort(job)),
        # Die beiden anderen Stellen - Reihenfolge wie in _JOB_DATA, damit sie
        # auf allen drei Seiten dieselbe ist.
        'andere_jobs': [{'slug': s, 'title': d['title'], 'teaser': d['teaser'],
                         'badge': d['badge'], 'orte': d['orte']}
                        for s, d in _JOB_DATA.items() if s != job_slug],
        'schema_bloecke': [S.job_schema(_safe_site_url(), job)],
    }


# Reihenfolge wie die Standort-Bloecke auf der Seite. Die Namen selbst stehen
# seit dem 06.09.2026 in data/cities.py::REGIONEN - dort ist auch erklaert,
# warum dieses Projekt VIER Regionen und SECHS Standorte kennt und beides
# richtig ist (P8/G6).
_STANDORT_REIHENFOLGE = _REGIONEN


def standorte(request):
    """Servicegebiet als echte Uebersicht.

    Die Seite nannte bisher nur die vier Standorte und verlinkte keine einzige
    der damals 53 Stadtseiten (F18). Sie ist damit die natuerliche zweite Quelle
    interner Links neben den Nachbarorten auf den Stadtseiten selbst.
    """
    gruppen = []
    for standort in _STANDORT_REIHENFOLGE:
        staedte = sorted(
            ({'name': c['name'], 'slug': slug, 'randgebiet': bool(c.get('randgebiet'))}
             for slug, c in _CITY_DATA.items() if c['standort'] == standort),
            key=lambda x: x['name'],
        )
        if staedte:
            gruppen.append({'standort': standort, 'staedte': staedte,
                            'randgebiet': all(x['randgebiet'] for x in staedte)})
    gesamt = sum(len(g['staedte']) for g in gruppen)
    return render(request, 'standorte.html', {
        'schema_bloecke': [S.standorte_schema(_safe_site_url())],
        'standort_gruppen': gruppen,
        'staedte_gesamt': gesamt,
        # IS06: Zahl im Titel - dieselbe, die die Liste darunter zaehlt.
        'seo_title': f'Entrümpelung: Einsatzgebiet & {gesamt} Orte | Rümpelwerk',
        **_antwort_ctx(_seiten_antwort('standorte', staedte=gesamt)),
    })


def galerie(request):
    """Vorher-Nachher-Bilder aus dem CMS (F9).

    Die Seite war eine Platzhalterseite ("Demnaechst verfuegbar") und stand
    deshalb zu Recht auf noindex - eine leere Seite freizugeben waere Thin
    Content. Sie zeigt jetzt die echten Bilder, und das noindex faellt
    automatisch weg, sobald welche da sind. Kein Handgriff noetig, und kein
    Risiko, dass eine leere Seite versehentlich indexiert wird.

    **Seit D5 (06.09.2026) kommt der Bestand aus ``sitemaps.galerie_bilder``.**
    Dieselbe Abfrage beantwortet das ``noindex`` dieser Seite, den Eintrag von
    ``/galerie/`` in ``sitemap-main.xml`` und die Existenz von
    ``sitemap-images.xml``. Drei Aussagen ueber denselben Bestand duerfen
    nicht aus drei Abfragen kommen - die Falle steht in Regel 21: eine
    Bildsitemap, die Bilder auf einer ``noindex``-Seite meldet.
    """
    from .models import AktuellesBild
    from .sitemaps import GALERIE_BILD_BREITE, galerie_bilder

    seite, blaettern = _blaettern(request, galerie_bilder(), GALERIE_JE_SEITE)
    # IS25: Nicht ``b.alt_text()`` je Bild, sondern die gemeinsame Quelle -
    # sonst hiessen die elf Bilder eines Beitrags ohne gepflegte Beschreibung
    # alle gleich, und die Bildersuche saehe elfmal dieselbe Aussage.
    alt_map = AktuellesBild.alt_texte(seite.object_list)
    bilder = [
        {
            'url': _safe_image_url(b.bild, width=GALERIE_BILD_BREITE),
            'alt': alt_map.get(b.pk) or b.alt_text(),
            'typ': b.typ_bild,
            'titel': b.post.titel,
            'datum': b.post.datum,
        }
        for b in seite.object_list
    ]
    return render(request, 'galerie.html', dict(
        blaettern,
        bilder=bilder,
        **_antwort_ctx(_seiten_antwort('galerie')),
        # Der ImageObject-Knoten je Bild (D5) - aus **derselben** Liste, aus
        # der die <figure>-Elemente entstehen. Regel 12: zwei Listen fuer
        # dieselbe Aussage laufen auseinander, und im Schema faellt es
        # niemandem auf.
        schema_bloecke=S.galerie_bilder_schema(_safe_site_url(), bilder),
        # ``hat_bilder`` steuert das noindex und meint den **Gesamtbestand**,
        # nicht die aktuelle Seite: Sonst stuende Seite 2 einer gefuellten
        # Galerie auf noindex, sobald jemand ``?seite=99`` aufruft.
        hat_bilder=bool(blaettern['eintraege_gesamt']),
    ))


# Crawler generativer Antwortmaschinen. Sie rendern kein JavaScript und
# lesen das rohe HTML - die Freigabe hier ist deshalb nur die halbe Miete
# (siehe F13).
_KI_CRAWLER = (
    'GPTBot', 'OAI-SearchBot', 'ChatGPT-User',
    'ClaudeBot', 'Claude-User', 'Claude-SearchBot',
    # 'anthropic-ai' ist die aeltere Kennung desselben Hauses wie ClaudeBot.
    # Wer den einen erlaubt und den anderen vergisst, erlaubt die Haelfte.
    'anthropic-ai',
    'PerplexityBot', 'Perplexity-User',
    # Meta AI antwortet in WhatsApp und Instagram. WhatsApp ist der
    # Haupt-Kontaktweg dieses Betriebs - die Zielgruppe sitzt dort bereits.
    'meta-externalagent',
    'Google-Extended', 'Applebot-Extended', 'CCBot', 'Bingbot',
)

# Reine SEO-Analysedienste und Crawler ohne Gegenleistung: kein Nutzen fuer
# uns, aber Last auf Railway.
#
# Bytespider (ByteDance/TikTok) steht bewusst HIER und nicht bei den
# KI-Crawlern. Er nennt in den Antworten keine sichtbare Quelle, faehrt
# nachweislich hohe Abrufraten, und ein regionaler Entruempelungsbetrieb in
# Mitteldeutschland hat dort kein Publikum. Inhalt hergeben, ohne genannt zu
# werden, ist Substanz gegen nichts. Die Entscheidung ist umkehrbar - sie
# steht mit Begruendung im Logbuch (G18, 19.08.2026).
_LAST_CRAWLER = ('AhrefsBot', 'SemrushBot', 'MJ12bot', 'DotBot', 'DataForSeoBot',
                 'Bytespider')


@never_cache
def health(request):
    """``/health/`` - schlanke Gesundheitsadresse für die Überwachung (BT11).

    Fragt die Datenbank mit ``SELECT 1`` an und antwortet ``200 ok`` als
    Klartext, sonst ``503``. Kein Template, keine Session, kein
    Besuchsprotokoll (``_SKIP_PREFIXES`` in ``middleware.py``), und
    ``X-Robots-Tag: noindex``, damit die Adresse nie im Index landet.

    Was sie NICHT prüft: den Mailweg (``pruefe_mail``), Cloudinary und ob die
    Seiten rendern (``check_seo``). Sie beantwortet nur „läuft der Prozess
    und erreicht er seine Datenbank?".
    """
    if request.method not in ('GET', 'HEAD'):
        return HttpResponseNotAllowed(['GET', 'HEAD'])
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    # audit-ok P02: jeder Datenbankfehler wird protokolliert und als 503 gemeldet
    except Exception as fehler:
        logger.warning('Health: Datenbank nicht erreichbar (%s)', type(fehler).__name__)
        antwort = HttpResponse('db', content_type='text/plain; charset=utf-8', status=503)
    else:
        antwort = HttpResponse('ok', content_type='text/plain; charset=utf-8')
    antwort['X-Robots-Tag'] = 'noindex'
    return antwort


def feed_weiterleitung(request):
    """``/feed/`` zeigt dauerhaft auf den Ratgeber-Feed (BT06).

    Feed-Leser und Prüfwerkzeuge fragen die übliche Adresse ab; der Feed
    selbst bleibt unter ``/ratgeber/feed/``, wo ihn ``rw_seo.html`` verlinkt.
    GET/HEAD bekommen 301; ein Feed nimmt nichts entgegen, alles andere 405.
    """
    if request.method not in ('GET', 'HEAD'):
        return HttpResponseNotAllowed(['GET', 'HEAD'])
    return HttpResponsePermanentRedirect('/ratgeber/feed/')


def robots_txt(request):
    """``/robots.txt`` - Crawler-Regeln und die Liste der Teil-Sitemaps.

    Die Sitemap-Zeilen kommen aus der Registrierung in ``config/urls.py``, nie
    aus einer zweiten Liste hier; genannt werden nur Abschnitte, die gerade
    wirklich URLs haben (``sitemaps.aktive_abschnitte``).
    """
    # _safe_site_url() erzwingt das Schema – ohne 'https://' wäre die
    # Sitemap-Zeile für Google eine ungültige Adresse.
    #
    # STATS_PATH steht hier BEWUSST NICHT mehr drin. Eine Disallow-Zeile
    # verbietet zwar das Crawlen, macht den Pfad dafür aber öffentlich lesbar –
    # robots.txt ist die erste Datei, die jeder Scanner abruft. Der
    # Statistikpfad ist nirgends verlinkt; ihn hier zu nennen war die einzige
    # Spur zu ihm. Geschützt wird er durch Login und Rate-Limit.
    #
    # Seit dem 06.09.2026 gilt dieselbe Ueberlegung fuer den Django-Admin:
    # Er haengt an ``settings.ADMIN_PATH`` (P8/B2). Ein geheimer Pfad waere
    # hier sofort wieder oeffentlich - die Zeile bliebe also nicht nur
    # wirkungslos, sie hoebe die Massnahme auf. Genannt wird deshalb nur
    # ``/admin/``, und zwar nur, wenn der Admin dort auch wirklich haengt:
    # Diesen Pfad probiert ohnehin jeder Scanner als Erstes, die Zeile
    # verraet dort nichts.
    #
    # Seit SI14 (10.09.2026) ist das der **Ausnahmefall** - der Vorgabewert
    # ist nicht mehr 'admin', die Zeile faellt also normalerweise weg. Sie
    # steht nur noch fuer den Fall, dass jemand ADMIN_PATH ausdruecklich auf
    # 'admin' zuruecksetzt. Der Schutz ist ohnehin Login, Rate-Limit und
    # django-axes, nicht die robots.txt.
    site_url = _safe_site_url()

    intern_zeilen = []
    if settings.ADMIN_PATH == 'admin':
        intern_zeilen.append("Disallow: /admin/")
    intern_zeilen += ["Disallow: /accounts/", "Disallow: /dashboard/"]
    intern = "\n".join(intern_zeilen)

    zeilen = [
        "# Klartextfassung fuer Sprachmodelle: /llms.txt (Verzeichnis)",
        "# Volltext mit Preisen, Ablaeufen und FAQ am Stueck: /llms-full.txt",
        "",
        "User-agent: *",
        "Allow: /",
        intern,
        "",
    ]

    # Die KI-Crawler sind durch "User-agent: *" technisch bereits
    # eingeschlossen. Der eigene Block aendert daran nichts - er
    # dokumentiert die Entscheidung und wird von manchen Crawlern anders
    # behandelt als der Sammelblock.
    for bot in _KI_CRAWLER:
        zeilen += ["User-agent: %s" % bot, "Allow: /", intern, ""]

    # Reine SEO-Analysedienste: kein Nutzen fuer uns, aber Last auf Railway.
    for bot in _LAST_CRAWLER:
        zeilen += ["User-agent: %s" % bot, "Disallow: /", ""]

    # Der Index zuerst, danach die Teil-Sitemaps einzeln. Mehrere
    # ``Sitemap:``-Zeilen sind erlaubt und ausdruecklich vorgesehen. Der Grund:
    # Google holt aus einem Index nur traege nach, und in der Search Console
    # zeigt die Zeile eines Index **null URLs** – er enthaelt ja keine, sondern
    # nur Verweise. Wer die Segmente auch einzeln findet, bekommt sie schneller
    # und bekommt Indexierungsquoten pro Bereich.
    #
    # Die Namen kommen aus der **Registrierung** in config/urls.py, nicht aus
    # einer zweiten Liste hier. Genau daran ist es schon schiefgegangen: Nach
    # dem Anlegen von ``sitemap-services.xml`` (Block 2) stand die Datei im
    # Index, in robots.txt aber nicht - der handgepflegte Tupel kannte sie
    # nicht. Eine neue Teil-Sitemap taucht jetzt automatisch hier auf.
    #
    # Seit D5 (06.09.2026) laeuft die Liste zusaetzlich durch
    # ``sitemaps.aktive_abschnitte``. Grund ist die Bildsitemap: Sie existiert
    # nur, solange Galeriebilder freigegeben sind, und antwortet sonst mit
    # 404. Eine ``Sitemap:``-Zeile auf eine 404 ist in der Search Console ein
    # gemeldeter Fehler - und sie stuende hier genau so lange, wie das CMS
    # leer ist, also im Zweifel monatelang.
    zeilen.append("Sitemap: %s/sitemap.xml" % site_url)
    try:
        from config.urls import sitemaps as _sitemaps
        from .sitemaps import aktive_abschnitte
        namen = [name for name, _ in aktive_abschnitte(_sitemaps)]
    except Exception:                                          # noqa: BLE001
        # Der Rueckfall ist richtig - eine robots.txt ohne Sitemap-Zeilen waere
        # schlechter als eine mit vier festen. Still darf er nicht sein: Die
        # feste Liste kennt weder ``matrix`` noch ``images``, und von aussen
        # sieht das Fehlen dieser beiden Zeilen wie eine Entscheidung aus.
        # Dieselbe Begruendung wie bei jedem Rueckfall in sitemaps.py.
        logger.warning('Sitemap-Abschnitte nicht ermittelbar - robots.txt '
                       'nennt die feste Liste', exc_info=True)
        namen = ['main', 'services', 'jobs', 'cities']
    for name in namen:
        zeilen.append("Sitemap: %s/sitemap-%s.xml" % (site_url, name))
    return HttpResponse("\n".join(zeilen) + "\n",
                        content_type='text/plain; charset=utf-8')


# ── Dateien, die Crawler am Standardpfad erwarten ───────────────────────────
# Alle drei tauchten in den Railway-Logs wiederholt als 404 auf.

_FESTE_DATEI_BYTES = {}


def feste_datei(request, datei):
    """Liefert ein Bild aus ``data/feste_dateien.py`` unter fester Adresse aus.

    SEO-Audit 25.09.2026 (K1/K2): Favicon, Apple-Touch-Icon, Vorschaubild
    und Logo liegen unter ``/static/`` mit Hash im Namen - fremde Systeme
    (Googles Favicon-Crawler, iOS, WhatsApp-Vorschau, Knowledge Panel)
    merken sich aber die Adresse. Deshalb zusaetzlich hier, ohne Hash.

    Bewusst ein echtes 200 statt eines Redirects auf die gehashte Datei -
    dem folgen viele Crawler an dieser Stelle nicht, und die Adresse, die
    sie sich merkten, waere wieder die gehashte. ``max-age`` ist ein Tag,
    nicht ein Jahr: Anders als die gehashte Datei kann sich der Inhalt
    unter derselben Adresse aendern. Den ETag setzt die
    ``ConditionalGetMiddleware``.
    """
    from .data.feste_dateien import FESTE_DATEIEN
    eintrag = FESTE_DATEIEN.get(datei)
    if not eintrag:
        raise Http404
    rel, content_type = eintrag
    inhalt = _FESTE_DATEI_BYTES.get(rel)
    if inhalt is None:
        from django.contrib.staticfiles import finders
        path = finders.find(rel)
        if not path:
            raise Http404
        with open(path, 'rb') as fh:
            inhalt = _FESTE_DATEI_BYTES[rel] = fh.read()
    response = HttpResponse(inhalt, content_type=content_type)
    response['Cache-Control'] = 'public, max-age=86400'
    return response


def favicon_ico(request):
    """/favicon.ico - Browser und Bots fragen den Standardpfad blind ab."""
    return feste_datei(request, 'favicon.ico')


# **Fester Zeitpunkt, von Hand gepflegt** (RFC 9116, EIG85/EIG128). Bis zum
# 24.09.2026 wurde ``Expires`` bei jedem Abruf als "jetzt + 365 Tage"
# gerechnet: Die Datei signalisierte Pflege, auch wenn niemand hinsah, und der
# Antworttext wechselte sekuendlich (kein 304). Dieselbe Fehlerklasse wie
# ``lastmod`` aus ``date.today()`` (Regel 22). Die RFC empfiehlt hoechstens ein
# Jahr Vorlauf. ``SecurityTxtTests`` in test_views.py wird 30 Tage vor Ablauf
# rot - dann Kontakt pruefen und das Datum um ein Jahr weiterziehen.
SECURITY_TXT_EXPIRES = '2027-09-01T00:00:00Z'


def security_txt(request):
    """RFC 9116 – /.well-known/security.txt (6x 404 in einer Woche)."""
    site_url = _safe_site_url()
    contact = getattr(settings, 'CONTACT_EMAIL', '')
    # Ohne Adresse stuende dort "Contact: mailto:" (EIG128). Die RFC erlaubt
    # auch eine https-Adresse - dann die Kontaktseite.
    kontakt = f"mailto:{contact}" if contact else f"{site_url}/kontakt/"
    content = (
        f"Contact: {kontakt}\n"
        f"Expires: {SECURITY_TXT_EXPIRES}\n"
        "Preferred-Languages: de, en\n"
        f"Canonical: {site_url}/.well-known/security.txt\n"
    )
    return HttpResponse(content, content_type='text/plain; charset=utf-8')


# audit-ok P16: in config/urls.py als re_path verdrahtet (name='indexnow_key');
# die Pruefung erkennt nur path()-Eintraege mit views.-Praefix.
def indexnow_key(request, key):
    """Liefert die IndexNow-Schluesseldatei unter /<schluessel>.txt.

    IndexNow prueft die Verfuegungsgewalt ueber die Domain, indem es diese
    Datei abruft: Ihr Inhalt muss exakt der Schluessel aus der Meldung sein.
    Deshalb ist der Schluessel oeffentlich - das ist kein Versehen, sondern
    das Verfahren.

    Ein fremder Wert bekommt 404, nicht die Datei mit dem echten Schluessel:
    Sonst wuerde jeder beliebige Aufruf die Pruefung bestehen.
    """
    erwartet = getattr(settings, 'INDEXNOW_KEY', '')
    if not erwartet or not hmac.compare_digest(key, erwartet):
        raise Http404
    return HttpResponse(erwartet, content_type='text/plain; charset=utf-8')


def _erster_satz(text):
    """Der erste Satz eines Antworttextes, mit Punkt.

    ``text.split('.')[0]`` waere der naheliegende Weg und ist falsch: Die
    Antworttexte enthalten Preise in deutscher Schreibweise, und "ab 1.450 EUR"
    bricht am **Tausenderpunkt**. In /llms.txt stand deshalb bis zum
    27.08.2026 die Zeile "Eine Haushaltsaufloesung in Leipzig kostet ab 1." -
    ein abgeschnittener Satz mit einer falschen Zahl, ausgerechnet in der
    Datei, die fuer Antwortmaschinen geschrieben ist.

    Ein Satzende ist hier ein Punkt, dem ein Leerzeichen oder das Textende
    folgt. Das reicht fuer diese Texte; ein Satzsegmentierer waere fuer drei
    Zeilen Ausgabe die falsche Abhaengigkeit.
    """
    treffer = _re.search(r'\.(?:\s|$)', text)
    return text[:treffer.start() + 1].strip() if treffer else text.strip()


def llms_txt(request):
    """/llms.txt – Klartext-Zusammenfassung für KI-Antwortmaschinen.

    Format nach llmstxt.org: H1 als erste Zeile, danach ein Blockquote mit der
    Kurzfassung, dann ``##``-Abschnitte, deren Einträge Markdown-Links sind
    (``- [Titel](URL): Beschreibung``). Lighthouse prüft genau diese Struktur.

    Wird aus denselben Konstanten gebaut wie die Website, damit Preise und
    Servicegebiet nicht auseinanderlaufen.
    """
    site_url = _safe_site_url()
    contact = getattr(settings, 'CONTACT_EMAIL', '')

    preise = '\n'.join(
        f"- **{_OBJEKTART_LABELS.get(k, k)}**: ab {v['min_preis']} EUR, "
        f"Richtwert {v['rate']} EUR/m²"
        for k, v in _PER_QM_PREISE.items()
    )
    staedte = '\n'.join(
        f"- [Entrümpelung {c['name']}]({site_url}/entrumpelung/{slug}/): "
        # 'response' ist der **Termin vor Ort**, nicht die Antwortzeit. Bis zum
        # 27.08.2026 stand hier "Rueckmeldung in {response}" - fuer 51 Staedte
        # also "Rueckmeldung in 1-2 Werktage". Genau die Verwechslung, wegen
        # der am 25.08. die richtige Zusage von sechs Stellen entfernt worden
        # ist (Regel 24). city.html sagt seit dem 21.08. "Termin vor Ort";
        # llms.txt hat es nur niemand nachgezogen, weil die Datei bis G7
        # ausserhalb jeder Pruefung stand.
        # Randgebiet: dort gilt "Termin nach Absprache", wie auf der Stadtseite
        # selbst (EIG141). Sonst die Dativform aus zusagen.py (EIG153).
        + (f"{c['state']}, Einsatzgebiet mit längerer Anfahrt – Termin nach Absprache"
           if c.get('randgebiet') else
           f"{c['state']}, Termin vor Ort in {c['response_dativ']}")
        for slug, c in sorted(_CITY_DATA.items(), key=lambda kv: kv[1]['name'])
    )
    # Leistungsseiten aus _SERVICE_DATA. Der Beschreibungstext ist der
    # Antwort-Absatz der Seite, also derselbe Satz, den auch ein Crawler dort
    # zuerst liest - keine zweite, eigens getippte Fassung.
    leistungen = '\n'.join(
        f"- [{l['name']}]({site_url}{l['url']}): {_erster_satz(l['answer'])}"
        for l in alle_leistungen()
        # EIG398: Die Kostenseite steht unten als "Entrümpelung Kosten
        # berechnen" mit dem Rechner - ihr erster Antwortsatz nennt ihn nicht.
        if l['slug'] != 'entruempelung-kosten'
    )
    # Leistung x Stadt (A13). Eigener Abschnitt und nicht unter
    # "Leistungen": Ein Sprachmodell, das nach "Haushaltsaufloesung
    # Leipzig" gefragt wird, soll die ortsgebundene Seite finden und
    # nicht die allgemeine.
    matrix_zeilen = '\n'.join(
        f"- [{m['h1']}]({site_url}{m['url']}): {_erster_satz(m['answer'])}"
        for m in (matrix(a, b) for a, b in matrix_kombinationen()) if m
    )

    # Die Ratgeberartikel (T4) - Wissensseiten, eigener Abschnitt.
    ratgeber_zeilen = '\n'.join(
        f"- [{a['h1']}]({site_url}{a['url']}): {_erster_satz(a['answer'])}"
        for a in _ratgeber.alle_artikel()
    )

    content = f"""# Rümpelwerk Mitteldeutschland

> Entrümpelung, Haushaltsauflösung und Sanierung zum Festpreis in Sachsen,
> Sachsen-Anhalt und Niedersachsen. Besenrein, Entsorgungsnachweis auf
> Wunsch. Verbindliches Angebot {_ZUSAGE_ANGEBOT}; per Video-Besichtigung
> {_ZUSAGE_ANGEBOT_VIDEO}, wenn alle Räume gezeigt wurden.

Inhabergeführter Betrieb mit Betriebsstätte in {firma.ORT} (Saale) und
Ansprechpartnern in {_cities_wort()} Regionen. Den Festpreis nennt der Betrieb bei der
Besichtigung, verbindlich im Angebot. Kontakt bevorzugt über
WhatsApp unter {firma.TELEFON_ANZEIGE}.

Diese Datei ist ein Verzeichnis. Wer die Antworten am Stück braucht – alle
Preise, Zu- und Abschläge, Leistungsumfänge, Abläufe und häufigen Fragen –,
findet sie unter {site_url}/llms-full.txt.

## Leistungen

{leistungen}
- [Alle Dienstleistungen]({site_url}/dienstleistungen/): Entrümpelung, Haushaltsauflösung, Nachlassräumung, Sanierung
- [Entrümpelung Kosten berechnen]({site_url}/entruempelung-kosten/): Kostenrechner mit allen Sätzen, Zuschlägen und durchgerechneten Beispielen; den Richtpreis zeigt der Rechner in {_RECHNER_DAUER} nach Angabe von Name und E-Mail. Das Festpreisangebot folgt nach der Besichtigung
- [Preisangebot anfordern]({site_url}/preisangebot/): derselbe Rechner als eigene Seite, mit Richtpreis nach Name und E-Mail
- [Entrümpelung anfragen]({site_url}/anfrage/): Formular für ein unverbindliches Angebot
- [Einsatzgebiet]({site_url}/standorte/): Servicegebiet und Ansprechpartner je Region

## Leistung in einer bestimmten Stadt

Diese Seiten nennen den zuständigen Entsorger, die kommunale
Sperrmüllregelung und den ortstypischen Gebäudebestand.

{matrix_zeilen}

## Ratgeber

Wissensseiten ohne Verkaufsabsicht – mit Fundstellen und den Preisen oben.

{ratgeber_zeilen}
- [Ratgeber-Übersicht mit Glossar]({site_url}/ratgeber/): Begriffe rund um Entrümpelung in je einem Satz

## Preise

Der Preis ergibt sich aus Objektart und Fläche – Richtwert je m², mindestens der
genannte Mindestpreis. Danach wirken Füllgrad, Stockwerk und Sonderabfall als
Zu- oder Abschläge. Der Kostenrechner ({site_url}/entruempelung-kosten/)
nennt einen unverbindlichen Richtwert, angezeigt nach Angabe von Name und
E-Mail. Bindend ist erst das schriftliche Angebot nach der kostenlosen
Besichtigung.

{preise}

## Servicegebiet

Antwort auf jede Anfrage in {_ZUSAGE_REAKTION}, {_ZUSAGE_GILT}; {_firma.ANFRAGEN_JEDERZEIT},
telefonisch und für Besichtigungen sind wir {_firma.ZEITEN_ANZEIGE} erreichbar. Der Termin vor Ort richtet sich nach dem Ort: im Kerngebiet in
{_ZUSAGE_TERMIN}, in {_ZUSAGE_SCHNELL_ORTE} in {_ZUSAGE_SCHNELL}. Größere
Aufträge werden auf Anfrage auch außerhalb übernommen.

{staedte}

## Unternehmen

- [Über uns]({site_url}/ueber-uns/): Inhaber, Team und Regionalleiter
- [Aktuelles]({site_url}/aktuelles/): Berichte von abgeschlossenen Aufträgen
- [Galerie]({site_url}/galerie/): Vorher-Nachher-Bilder
- [Stellenangebote]({site_url}/jobs/): offene Stellen im Betrieb
- [Kooperationspartner]({site_url}/kooperationspartner/): Zusammenarbeit mit Hausverwaltungen und Maklern

## Kontakt

- WhatsApp und Telefon: {firma.TELEFON_ANZEIGE}
- E-Mail: {contact}
- [Impressum]({site_url}/impressum/): Anbieterkennzeichnung
"""
    return HttpResponse(content, content_type='text/plain; charset=utf-8')


def _md_tabelle(kopf, zeilen):
    """Markdown-Tabelle. Eine Zeile je Liste, Spalten in der Reihenfolge des Kopfs."""
    aus = ['| ' + ' | '.join(kopf) + ' |',
           '|' + '|'.join(['---'] * len(kopf)) + '|']
    aus += ['| ' + ' | '.join(str(z) for z in zeile) + ' |' for zeile in zeilen]
    return '\n'.join(aus)


def llms_full_txt(request):
    """/llms-full.txt - die Langfassung von /llms.txt (G7).

    ``llms.txt`` ist ein **Verzeichnis**: Links mit einem Satz Beschreibung. Ein
    System, das eine Frage beantworten will, muss von dort aus jede Seite
    einzeln abrufen. Diese Datei liefert stattdessen die ausformulierten
    Antworten am Stueck - Preise, Modifikatoren, Leistungen, Ablauf, FAQ,
    Servicegebiet - als eine Datei, aus der eine vollstaendige Antwort gebaut
    werden kann.

    **Es wird nichts getippt.** Jede Zahl kommt aus ``data/pricing.py``, jede
    Zeitangabe aus ``data/zusagen.py``, jeder Beschreibungstext aus
    ``data/services.py``, ``data/matrix.py`` oder ``data/cities.py`` - dieselben
    Quellen, aus denen die Seiten entstehen. Eine zweite Textfassung waere
    genau die Konstruktion, an der in diesem Projekt schon Preise und FAQ
    auseinandergelaufen sind (Regel 12). ``check_seo`` prueft die Datei seit G7
    wie eine Seite: jede Euro-Zahl gegen ``pricing.py``, jede Zeitzusage gegen
    ``zusagen.py``.

    **Groesse:** Der Plan setzt 100 KB als Grenze. ``check_seo`` meldet, wenn
    sie ueberschritten wird - eine Datei, die kein Modell mehr am Stueck liest,
    verfehlt ihren Zweck.
    """
    site_url = _safe_site_url()
    contact = getattr(settings, 'CONTACT_EMAIL', '')
    P = preis_context()
    mod = P['PREIS_MOD_LISTE']

    # ── Preise ───────────────────────────────────────────────────────────
    grundpreise = _md_tabelle(
        ['Objektart', 'Mindestpreis', 'Richtwert', 'typische Größe',
         'Beispielpreis'],
        [[z['label'], f"{z['min_txt']} €", f"{z['rate']} €/m²",
          f"{z['qm_typisch']} m²", z['beispiel_txt']]
         for z in P['PREISE_LISTE']])

    fuellgrad = _md_tabelle(
        ['Füllgrad', 'Faktor'],
        [[z['label'], z['faktor_txt']] for z in mod['fuellgrad']])
    stockwerk = _md_tabelle(
        ['Stockwerk (ohne Aufzug)', 'Aufpreis'],
        [[z['label'], z['aufpreis_txt']] for z in mod['stockwerk']])
    sonderabfall = _md_tabelle(
        ['Sonderabfall', 'Aufpreis'],
        [[z['label'], z['aufpreis_txt']] for z in mod['sonderabfall']])
    san = P['PREIS_SANIERUNG']
    kleinrep = _md_tabelle(
        ['Kleinreparatur', 'Pauschale'],
        [[i['label'], f"{i['preis_txt']} €"] for i in san['items']]
        + [['Sonstiges (frei beschrieben)', f"{san['sonstiges_txt']} €"]])

    # ── Leistungen im Volltext ───────────────────────────────────────────
    teile = []
    for l in alle_leistungen():
        block = ['### %s' % l['name'], '',
                 '%s%s' % (site_url, l['url']), '',
                 l['answer'], '']
        if l.get('leistungsumfang'):
            block += ['**Enthalten:**', '']
            block += ['- %s' % strip_tags(z) for z in l['leistungsumfang']]
            block += ['']
        if l.get('abgrenzung'):
            block += ['**Nicht enthalten:**', '']
            block += ['- %s' % strip_tags(z) for z in l['abgrenzung']]
            block += ['']
        if l.get('ablauf'):
            block += ['**Ablauf:**', '']
            block += ['%d. **%s** - %s' % (i, s['titel'], strip_tags(s['text']))
                      for i, s in enumerate(l['ablauf'], 1)]
            block += ['']
        if l.get('faq'):
            block += ['**Häufige Fragen:**', '']
            for frage, antwort in l['faq']:
                # Regel 12: im llms-Text derselbe Wortlaut als reiner Text.
                block += ['*%s*' % frage, '', strip_tags(antwort), '']
        teile.append('\n'.join(block))
    leistungen_voll = '\n'.join(teile)

    matrix_voll = '\n'.join(
        '### %s\n\n%s%s\n\n%s\n' % (m['h1'], site_url, m['url'], m['answer'])
        for m in (matrix(a, b) for a, b in matrix_kombinationen()) if m)

    # Die Ratgeberartikel mit Antwort und Fragen - wie die Leistungen oben.
    ratgeber_teile = []
    for a in _ratgeber.alle_artikel():
        block = ['### %s' % a['h1'], '', '%s%s' % (site_url, a['url']), '',
                 a['answer'], '']
        # Nur die ersten beiden Fragen: mit 22 Artikeln sprengte die volle
        # Liste die 100-KB-Grenze (SU07, 02.10.2026). Alle Fragen stehen auf
        # der Artikelseite, deren Adresse oben steht.
        for frage, antwort in a['faq'][:2]:
            block += ['*%s*' % frage, '', strip_tags(antwort), '']
        ratgeber_teile.append('\n'.join(block))
    ratgeber_voll = '\n'.join(ratgeber_teile)

    # ── Servicegebiet ────────────────────────────────────────────────────
    # 'response' ist der Termin VOR ORT, nicht die Antwortzeit. Die beiden sind
    # am 25.08.2026 schon einmal verwechselt worden und haben die richtige
    # Zusage von sechs Stellen gekostet (K2). Die Spalte heisst deshalb so,
    # wie sie gemeint ist.
    gebiet = _md_tabelle(
        ['Stadt', 'Bundesland', 'Termin vor Ort', 'Seite'],
        [[c['name'], c['state'],
          'nach Absprache' if c.get('randgebiet') else c['response'],
          f"{site_url}/entrumpelung/{slug}/"]
         for slug, c in sorted(_CITY_DATA.items(), key=lambda kv: kv[1]['name'])])

    # **Alle** Eintraege aus pricing.py (EIG144). Bis zum 24.09.2026 filterte
    # hier ``if s in _CITY_DATA`` - Slugs sind ASCII, die Eintraege nicht, und
    # so fielen Koethen, Meissen, Markranstaedt, Hildesheim und Wolfsburg still
    # aus der Liste, obwohl der Rechner ihnen den Nachlass gibt.
    from .data.pricing import ort_normalisiert as _ort_normalisiert

    def _rabatt_name(eintrag):
        c = _CITY_DATA.get(_ort_normalisiert(eintrag).replace(' ', '-'))
        return c['name'] if c else eintrag[:1].upper() + eintrag[1:]
    rabatt_staedte = ', '.join(
        sorted(_rabatt_name(s) for s in _STANDORT_RABATT_STAEDTE))

    content = f"""# Rümpelwerk Mitteldeutschland - Volltext

> Entrümpelung, Haushaltsauflösung und Sanierung zum Festpreis in Sachsen,
> Sachsen-Anhalt und Niedersachsen. Diese Datei ist die Langfassung von
> {site_url}/llms.txt: alle Preise, Zu- und Abschläge, Leistungen, Abläufe
> und häufigen Fragen am Stück, damit eine Antwort daraus vollständig gebaut
> werden kann, ohne jede Seite einzeln abzurufen.

Preisstand: {P['PREISSTAND']}. Alle Zahlen dieser Datei stammen aus derselben
Quelle wie der Preisrechner der Website.

## Unternehmen

Rümpelwerk Mitteldeutschland ist ein inhabergeführter Betrieb mit Betriebsstätte in
{firma.ORT} (Saale) und Ansprechpartnern in {_cities_wort()} Regionen; Inhaber
ist Oliver Pohl. Der Betrieb räumt Wohnungen, Häuser,
Keller, Gewerbeobjekte, Scheunen und Grundstücke und übernimmt anschließend auf
Wunsch Maler- und Kleinreparaturarbeiten. Gearbeitet wird zum Festpreis: Der
Preis wird bei einer kostenlosen Besichtigung ermittelt und steht im
verbindlichen Angebot. Jede Räumung endet besenrein; einen
Entsorgungsnachweis gibt es auf Wunsch. Das
Servicegebiet umfasst Sachsen-Anhalt, Sachsen und Niedersachsen mit
{len(_CITY_DATA)} Städten. Der bevorzugte Kontaktweg ist WhatsApp unter
{firma.TELEFON_ANZEIGE}. Auf jede Anfrage antwortet der Betrieb in {_ZUSAGE_REAKTION}, {_ZUSAGE_GILT};
das verbindliche Angebot gibt es {_ZUSAGE_ANGEBOT}.

## Preise

Der Preis ergibt sich aus Objektart und Fläche: Richtwert je Quadratmeter mal
Fläche, mindestens aber der Mindestpreis der Objektart. Auf diese Grundsumme
wirken die Modifikatoren - **die Reihenfolge ist bindend**, weil der Füllgrad
multiplikativ, die Aufpreise additiv wirken:

1. Grundpreis = größerer Wert aus Mindestpreis und (Richtwert × Quadratmeter)
2. Stockwerkzuschlag, wenn kein Aufzug vorhanden ist (nur Wohnung und Keller)
3. Füllgradfaktor (multiplikativ)
4. Sonderabfallzuschlag
5. optionale Malerarbeiten und Kleinreparaturen
6. Standortnachlass, wenn das Objekt in einer Standortstadt liegt

### Grundpreise

{grundpreise}

Die Spalte "Beispielpreis" ist die fertige Rechnung für die typische Größe bei
Füllgrad mittel, Erdgeschoss, ohne Sonderabfall.

### Füllgrad

{fuellgrad}

### Stockwerk

{stockwerk}

Der Zuschlag entfällt, wenn ein Aufzug vorhanden ist, und gilt nur für
Wohnungen und Keller.

### Sonderabfall

{sonderabfall}

### Malerarbeiten und Kleinreparaturen

Malerarbeiten kosten {san['maler_rate']} €/m², mindestens
{san['maler_min_txt']} €.

{kleinrep}

### Standortnachlass

In diesen Orten sinkt der Endpreis um
{P['PREIS_MODIFIKATOREN']['rabatt_prozent']} Prozent, höchstens bis zum
Mindestpreis der Objektart: {rabatt_staedte}.

## Zeitzusagen

- Antwort auf eine Anfrage: {_ZUSAGE_REAKTION}, {_ZUSAGE_GILT}; {_firma.ANFRAGEN_JEDERZEIT}
- Geschäftszeiten (Telefon, Besichtigung): {_firma.ZEITEN_LANG}
- Besichtigungstermin online buchbar: {_ZUSAGE_TERMIN_AB} (Montag bis Samstag, ohne Sonn- und Feiertage)
- Verbindliches Festpreisangebot: {_ZUSAGE_ANGEBOT} (Besichtigung vor Ort); bei einer
  Video-Besichtigung per WhatsApp {_ZUSAGE_ANGEBOT_VIDEO}, wenn alle Räume gezeigt wurden
- Termin vor Ort im Kerngebiet: in {_ZUSAGE_TERMIN}, in {_ZUSAGE_SCHNELL_ORTE} in
  {_ZUSAGE_SCHNELL}
- Preisrechner auf der Website: Ergebnis in {_RECHNER_DAUER}

Antwortzeit und Termin vor Ort sind zwei verschiedene Zusagen. Die Antwortzeit
gilt überall gleich; der Termin vor Ort hängt vom Ort ab und steht je Stadt in
der Tabelle unter "Servicegebiet".

## Leistungen

{leistungen_voll}
## Leistung in einer bestimmten Stadt

Diese Seiten nennen zusätzlich den zuständigen Entsorger, die kommunale
Sperrmüllregelung und den ortstypischen Gebäudebestand.

{matrix_voll}
## Ratgeber

{ratgeber_voll}
## Servicegebiet

{gebiet}

Größere Aufträge werden auf Anfrage auch außerhalb übernommen.

## Kontakt

- WhatsApp und Telefon: {firma.TELEFON_ANZEIGE}
- E-Mail: {contact}
- Anfrageformular: {site_url}/anfrage/
- Kostenrechner: {site_url}/entruempelung-kosten/
- Anbieterkennzeichnung: {site_url}/impressum/

## Stand

- Preisstand: {P['PREISSTAND']}
- Kurzfassung dieser Datei: {site_url}/llms.txt
"""
    return HttpResponse(content, content_type='text/plain; charset=utf-8')


# audit-ok P16: Fehlerseite, verdrahtet ueber handler404 in config/urls.py -
# eine URL haette sie gerade NICHT haben duerfen.
def error_404(request, exception=None):
    """Die Fehlerseite - mit **gerechneter** Bestandszahl (G1, 06.09.2026).

    Die Seite nannte "53 Orte mit eigener Seite"; ``cities.py`` kennt 54. Die
    Zahl war getippt - Regel 1 in einer sechsten Sorte Zahl, neben Preisen,
    Bewertungen, Zeitzusagen und Stammdaten.

    **Warum der Wert hier hereingegeben werden muss und nicht von selbst
    ankommt:** ``handler404`` ruft diese View ohne den Kontext einer normalen
    View auf. Was trotzdem ankommt, sind die Context-Processors (``render``
    baut einen ``RequestContext``) - daher stammt das ``{{ ZUSAGE_RECHNER }}``
    weiter unten auf derselben Seite. Eine Stadtzahl liefert keiner von ihnen;
    sie waere ein sechster Context-Processor fuer **eine** Zeile auf **einer**
    Seite und liefe dafuer auf allen 85. Deshalb der Weg ueber den View-Context.

    ``alle_stadtseiten()`` und nicht ``len(_CITY_DATA)``: Es ist dieselbe
    Funktion, aus der die Startseite ihre Staedteliste baut. Waeren die
    Randgebiet-Staedte eines Tages ausgenommen, aendert sich beides zugleich.
    """
    return render(request, 'errors/404.html',
                  {'STADTSEITEN_ANZAHL': len(alle_stadtseiten())}, status=404)


# audit-ok P16: Fehlerseite, verdrahtet ueber handler500 in config/urls.py.
def error_500(request):
    return render(request, 'errors/500.html', status=500)


# ---------------------------------------------------------------------------
# Preisrechner
# ---------------------------------------------------------------------------

# Alle Preiskonstanten und die Rechnung selbst liegen in apps/core/data/pricing.py
# und speisen von dort aus Templates, Wizard-JS und llms.txt gleichermaßen (F2).
# Hier nur re-importiert, damit bestehende Namen im Modul weiterlaufen.
# Staedte und Jobs liegen seit F6 in apps/core/data/, die HTML-Mails samt
# Versand in apps/core/emails.py. Hier re-importiert, damit bestehende Namen
# (auch in sitemaps.py, apps.py und den Skripten) unveraendert weiterlaufen.
from .data.antworten import (hub_antwort as _hub_antwort,
                            job_antwort as _job_antwort,
                            rechner_antwort as _rechner_antwort,
                            seiten_antwort as _seiten_antwort,
                            start_antwort as _start_antwort,
                            stadt_antwort as _stadt_antwort)


def _antwort_ctx(frage_und_text):
    """(Frage, Text) aus ``data/antworten.py`` als Kontext fuer ``rw_antwort.html``.

    GE23 (16.09.2026): Die Seiten ohne eigene Leistung bekommen denselben
    Antwort-zuerst-Block wie die Hubs. Der Text steht nie in der View.
    """
    frage, text = frage_und_text
    return {'antwort_frage': frage, 'antwort_text': text}
from .data.cities import (  # noqa: E402,F401
    _CITY_DATA, _EXTRA_LANDING_CITIES, alle_stadtseiten, reagiert_in_stunden,
    weitere_staedte,
)
from .data.jobs import _JOB_DATA  # noqa: E402,F401
from .data.services import (  # noqa: E402,F401
    _SERVICE_DATA, RATGEBER_SEITEN, alle_leistungen, beispiel_preise,
    hub_vergleich, leistung,
)
from .data.cities import leiter_key as _leiter_key  # noqa: E402
from .data import ratgeber as _ratgeber  # noqa: E402
from .data.matrix import matrix, matrix_beispiele, matrix_kombinationen  # noqa: E402
from .data import reviews  # noqa: E402
from .data import city_lokal  # noqa: E402
# Die Aufzaehlung der schnellen Staedte kommt fertig aus zusagen.py. Hier stand
# bis zum 25.08.2026 eine **woertliche Kopie** von zusagen._und() - inklusive
# des IndexError, den sie auf leerer Liste wirft (S4). Doppelpflege ist genau
# das, wogegen dieser Block angetreten ist.
from .data.zusagen import (  # noqa: E402
    ANGEBOT_BEI_BESICHTIGUNG as _ZUSAGE_ANGEBOT,
    ANTWORT as _ZUSAGE_REAKTION,
    TERMIN_REGEL as _ZUSAGE_TERMIN,
    TERMIN_SCHNELL as _ZUSAGE_SCHNELL,
    TERMIN_SCHNELL_ORTE as _ZUSAGE_SCHNELL_ORTE,
    RECHNER_DAUER as _RECHNER_DAUER,
    TERMIN_FRUEHESTENS as _ZUSAGE_TERMIN_AB,
    ANGEBOT_NACH_VIDEO as _ZUSAGE_ANGEBOT_VIDEO,
    ANTWORT_GILT as _ZUSAGE_GILT,
)
from . import schema as S  # noqa: E402
from .emails import (  # noqa: E402,F401
    _build_html_email, _send_anfrage_email,
    _build_koop_email_kunde, _send_koop_emails,
    _build_bewerbung_email_kunde, _send_bewerbung_emails,
    _build_rechner_email_kunde, _build_rechner_reminder_email,
    _send_rechner_reminder, _send_rechner_emails,
    _fmt_duration, _trend, _send_daily_report_email,
    _send_termin_email,
)
# Regel 25: Stammdaten aus einer Quelle. Bis zum 06.09.2026 stand die
# Rufnummer hier VIERMAL getippt - zweimal in llms.txt, zweimal in
# llms-full.txt. Uebersehen wurde das, weil
# KontaktnummerAusEinerQuelleTests nur templates/ durchsuchte; seit
# diesem Datum liest sie auch apps/**/*.py (P8/G7).
from .data import firma  # noqa: E402
from .data.pricing import preis_context  # noqa: E402
from .data.pricing import (  # noqa: E402
    _PER_QM_PREISE, _MALER_PER_QM, _STOCKWERK_AUFPREIS, _FUELLGRAD_FAKTOR,
    _SONDERABFALL_AUFPREIS, _KLEIN_SAN_ITEMS, _KLEIN_SONSTIGES_AUFPREIS,
    _STOCKWERK_OBJEKTE, _SONDERABFALL_OBJEKTE, _STANDORT_RABATT_STAEDTE,
    _OBJEKTART_LABELS, auswahl_text, berechne_preis, euro,
)


# audit-ok P16: Scheduler-Funktion, aufgerufen aus apps/core/apps.py und aus
# manage.py send_rechner_reminders - eine oeffentliche URL waere hier falsch.
def send_due_reminders():
    """
    Finds PreisAngebot records that are 24–48h old and haven't received a reminder yet,
    and sends the reminder email. Safe against concurrent workers (optimistic DB claim).
    Returns the number of reminders sent.
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models import PreisAngebot

    now  = timezone.now()
    # ``mail_gewollt=True``: ``core_preisangebot`` teilt RTC-Service. RTC schreibt
    # dort immer ``mail_gewollt=False`` - ohne diesen Filter bekaemen RTC-Kunden
    # eine Ruempelwerk-Erinnerung (und RTCs eigene wuerde verbraucht). Zeilen,
    # fuer die nie eine Mail vorgesehen war (Duplikat, Notbremse), bekommen
    # ohnehin keine Erinnerung an ein Angebot, das sie nie erhielten.
    due  = list(PreisAngebot.objects.filter(
        mail_gewollt=True,
        erinnerung_gesendet=False,
        erstellt_am__lte=now - timedelta(hours=24),
        erstellt_am__gte=now - timedelta(hours=48),
    ))

    sent = 0
    for angebot in due:
        # Claim atomically so multiple workers never double-send
        claimed = PreisAngebot.objects.filter(
            pk=angebot.pk, erinnerung_gesendet=False,
        ).update(erinnerung_gesendet=True)
        if not claimed:
            continue
        try:
            # EIG302: Gezaehlt wird nur, was wirklich rausging. Eine
            # unterdrueckte Mail (Empfaenger nicht vom Betrieb) bleibt als
            # "abgearbeitet" markiert - ein Rueckgaengigmachen liesse den
            # Scheduler sie bis zum Ende des 48-Stunden-Fensters stuendlich
            # neu versuchen -, taucht aber nicht mehr als Erinnerung auf.
            if _send_rechner_reminder(angebot):
                sent += 1
        except Exception as exc:
            # Ohne Mailadresse (P8/A4): Die Kennung findet den Datensatz, die
            # Adresse steht darin. Ein Fehlerlog ist keine Beweisfuehrung
            # gegen einen Absender, sondern eine Betriebsmeldung.
            logger.error(f'Reminder fehlgeschlagen | id={angebot.pk} | {exc}')
            # Roll back so the next cycle can retry
            PreisAngebot.objects.filter(pk=angebot.pk).update(erinnerung_gesendet=False)

    if sent:
        logger.info(f'Erinnerungen gesendet: {sent}')
    return sent


# ── Tagesstatistiken ─────────────────────────────────────────────────────────

# audit-ok P16: Scheduler-Funktion, aufgerufen aus send_daily_report() und
# apps/core/apps.py - keine View.
def compile_daily_stats(date):
    """Aggregate VisitorSession records into DailyStats for the given date."""
    from .models import VisitorSession, DailyStats
    from django.db.models import Sum

    sessions = VisitorSession.objects.filter(date=date)

    total_sessions  = sessions.count()
    unique_visitors = total_sessions  # Sitzungen = Besuche (IP durch Railway-Proxy nicht verwertbar)
    total_pageviews = sessions.aggregate(s=Sum('page_count'))['s'] or 0

    durations = [
        (s.last_seen - s.started_at).total_seconds()
        for s in sessions
        if s.last_seen > s.started_at
    ]
    avg_seconds = int(sum(durations) / len(durations)) if durations else 0

    stats, _ = DailyStats.objects.update_or_create(
        date=date,
        defaults={
            'unique_visitors':     unique_visitors,
            'total_sessions':      total_sessions,
            'total_pageviews':     total_pageviews,
            'avg_session_seconds': avg_seconds,
        },
    )
    return stats


# audit-ok P16: Scheduler-Funktion, aufgerufen aus apps/core/apps.py (02:00
# Ortszeit) - keine View.
def send_daily_report():
    """Send the nightly visitor-stats email. Called by the scheduler at hour 0."""
    import datetime as dt
    from django.utils import timezone
    from .models import DailyStats

    yesterday = timezone.localdate() - dt.timedelta(days=1)

    # Idempotency guard
    if DailyStats.objects.filter(date=yesterday, email_sent=True).exists():
        return

    stats   = compile_daily_stats(yesterday)
    history = list(DailyStats.objects.filter(date__lt=yesterday).order_by('-date')[:7])

    # Seit 24.09.2026: die Anfragen von gestern und alles, was nie
    # zugestellt wurde. Scheitert das Zaehlen, geht der Report ohne sie raus.
    try:
        from .leads import zahlen_fuer_tag
        leads = zahlen_fuer_tag(yesterday)
    except Exception:                                           # noqa: BLE001
        logger.error('Tagesreport: Anfragezahlen nicht ermittelbar', exc_info=True)
        leads = None

    _send_daily_report_email(stats, history, leads)

    DailyStats.objects.filter(pk=stats.pk).update(email_sent=True)


#: So lange bleiben ``VisitorSession``-Zeilen (Datenschutzerklaerung).
SITZUNGEN_AUFBEWAHRUNG_TAGE = 90


# audit-ok P16: Scheduler-Funktion, aufgerufen aus apps/core/apps.py - keine View.
def sitzungen_aufraeumen():
    """``VisitorSession`` aelter als 90 Tage loeschen - eigener Schritt (EIG16).

    Bis zum 24.09.2026 stand das am Ende von ``send_daily_report()``: hinter
    dem Mailversand und hinter dessen ``return``, falls der Report schon
    verschickt war. Ein Fehler im Versand oder ein zweiter Lauf in derselben
    Nacht liess die Loeschung ausfallen - dieselbe Kopplung, an der bei
    ``PageVisit`` schon einmal die Frist gerissen ist.
    """
    import datetime as dt
    from django.utils import timezone
    from .models import VisitorSession
    grenze = timezone.localdate() - dt.timedelta(days=SITZUNGEN_AUFBEWAHRUNG_TAGE + 1)
    deleted, _ = VisitorSession.objects.filter(date__lt=grenze).delete()
    if deleted:
        logger.info(f'Session-Cleanup: {deleted} alte Einträge gelöscht')
    return deleted


@ensure_csrf_cookie
# audit-ok K06: öffentlicher Preisrechner – CSRF, rate_limited und ist_spam (Regel 18)
# offen-ok: absichtlich ohne Anmeldung, Besucher schicken hier eine Anfrage ab
def preisangebot(request):
    """Der Preisrechner - GET rendert den Wizard, POST nimmt JSON entgegen.

    Gerechnet wird **serverseitig** mit ``data/pricing.py::berechne_preis``;
    die Zahlen aus dem Browser werden nie uebernommen. Der Eingang ist
    doppelt abgesichert: Gueltiges JSON, das kein Objekt ist, und ein
    Formular-POST, dessen Eingabestrom die CSRF-Middleware schon verbraucht
    hat, ergeben beide ein 400 statt eines 500 (LOG-362, 07.09.2026).
    """
    if request.method == 'POST':
        # Dies ist die einzige Stelle der Website, die einen Request-Body selbst
        # auspackt - und sie hatte bis zum 07.09.2026 zwei Wege in einen 500
        # (LOG-362, drei Treffer im Betriebslog am 07.09.). Beide enden hier in
        # einem 400: Eine unbrauchbare Einsendung ist ein Eingabefehler des
        # Absenders, kein Serverfehler.
        #
        # 1) ``RawPostDataException`` ist KEIN ``ValueError``. Bei einem POST mit
        #    ``multipart/form-data`` wertet die CSRF-Middleware ``request.POST``
        #    aus und verbraucht dabei den Eingabestrom; ``request.body`` wirft
        #    danach, und das ``except`` unten sieht davon nichts.
        try:
            rumpf = request.body
        except RawPostDataException:
            return JsonResponse({'ok': False, 'error': 'Ungültige Anfrage'}, status=400)

        try:
            data = json.loads(rumpf.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            return JsonResponse({'ok': False, 'error': 'Ungültige Anfrage'}, status=400)

        # 2) ``null``, ``[]``, ``5``, ``"text"`` und ``true`` sind gueltiges
        #    JSON und kommen am ``except`` vorbei - nur ist das Ergebnis kein
        #    Dictionary, und ``data.get('name')`` weiter unten war damit ein
        #    ``AttributeError``. Die naechste Zeile wusste das schon
        #    (``if isinstance(data, dict)``), zwei Zeilen spaeter war es wieder
        #    vergessen. Deshalb wird hier abgebrochen statt notdurftig ersetzt:
        #    Wer keinen Namen und keine Adresse schickt, bekaeme ohnehin ein 400.
        if not isinstance(data, dict):
            return JsonResponse({'ok': False, 'error': 'Ungültige Anfrage'}, status=400)

        # Der Rechner schickt JSON statt eines Formular-POST. antispam.score
        # liest die Felder deshalb aus diesem Zwischenspeicher, wenn request.POST
        # leer ist.
        request._rw_json = data

        name      = str(data.get('name', '')).strip()[:200]
        email_raw = str(data.get('email', '')).strip()[:200]
        if not name:
            return JsonResponse({'ok': False, 'error': 'Bitte geben Sie Ihren Namen ein.'}, status=400)
        if not email_raw or not _re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email_raw):
            return JsonResponse({'ok': False, 'error': 'Bitte geben Sie eine gültige E-Mail-Adresse ein.'}, status=400)

        objektart = str(data.get('objektart', '')).strip()
        # Fuers Speichern und fuer die Nachricht in der Schreibweise des
        # Kunden, fuer die Preisrechnung klein (Standortnachlass).
        ort_roh   = str(data.get('stadtort',  '')).strip()[:100]
        stadtort  = ort_roh.lower()

        if objektart not in _PER_QM_PREISE:
            return JsonResponse({'ok': False, 'error': 'Bitte wählen Sie eine Objektart.'}, status=400)

        try:
            qm_roh = data.get('qm') or 0
            # EIG284/306/307: ``true`` ist in Python ein int (1) und kame als
            # "1 m²" durch; ``Infinity``/``1e999`` parst json.loads zu einem
            # float, und int(inf) wirft OverflowError (kein ValueError) - 500.
            if isinstance(qm_roh, bool):
                raise ValueError
            qm = int(qm_roh)
            if not (1 <= qm <= 9999):
                raise ValueError
        except (TypeError, ValueError, OverflowError):
            return JsonResponse({'ok': False, 'error': 'Bitte geben Sie eine gültige Fläche ein.'}, status=400)

        # EIG277: Stockwerk, Fuellgrad und Sonderabfall muessen Schluessel der
        # Preistabelle sein. ``berechne_preis`` behandelt einen unbekannten
        # Wert still als 0 EUR Aufpreis (Stockwerk, Sonderabfall) bzw. als
        # Faktor 1,20 (Fuellgrad) - der Preis stuende dann auf einer Angabe,
        # die es im Rechner gar nicht gibt. Fehlt ein Feld, gilt wie im
        # Wizard-JS der Vorgabewert; die Funktion selbst bleibt tolerant.
        stockwerk    = str(data.get('stockwerk', 'eg'))
        fuellgrad    = str(data.get('fuellgrad', 'mittel'))
        sonderabfall = str(data.get('sonderabfall', 'keine'))
        if (stockwerk not in _STOCKWERK_AUFPREIS
                or fuellgrad not in _FUELLGRAD_FAKTOR
                or sonderabfall not in _SONDERABFALL_AUFPREIS):
            return JsonResponse({'ok': False, 'error': 'Bitte prüfen Sie Ihre Angaben und rechnen Sie neu.'}, status=400)

        # Die Rechnung selbst steht in data/pricing.py – dieselbe Funktion
        # liefert auch die Beispielpreise der Preistabelle, und das Wizard-JS
        # spiegelt exakt sie. Der Client-Preis wird weiterhin ignoriert.
        klein_items_raw = data.get('klein_items', [])
        if not isinstance(klein_items_raw, list):
            klein_items_raw = []
        # Nur bekannte Positionen: Eine unbekannte Kennung kostete nichts,
        # haette aber das Etikett "+ Kleine Reparaturen" ausgeloest.
        klein_items     = [i for i in klein_items_raw
                           if isinstance(i, str) and i in _KLEIN_SAN_ITEMS][:20]
        klein_sonstiges = str(data.get('klein_sonstiges', ''))[:500]

        preis, details = berechne_preis(
            objektart=objektart,
            qm=qm,
            stockwerk=stockwerk,
            aufzug=str(data.get('aufzug', 'nein')) == 'ja',
            fuellgrad=fuellgrad,
            sonderabfall=sonderabfall,
            with_maler=bool(data.get('with_maler')),
            klein_items=klein_items,
            klein_sonstiges=klein_sonstiges,
            stadtort=stadtort,
        )
        maler_label = ' + Malerarbeiten' if data.get('with_maler') else ''
        klein_label = ' + Kleine Reparaturen' if (klein_items or klein_sonstiges.strip()) else ''

        leistung_label = _OBJEKTART_LABELS.get(objektart, objektart) + maler_label + klein_label
        # EIG276: Die Angaben, die den Preis bestimmen, gehoeren zum
        # Datensatz - Fuellgrad, Stockwerk und Reparaturen sah der Betrieb
        # bisher nirgends. ``groesse_label`` ("Groesse / Positionen") reist
        # ohnehin in Mail, Telegram-Push, Nachzuegler und Duplikatschluessel;
        # ein neues Feld braeuchte eine Migration und vier weitere Stellen.
        groesse_label  = (f'{qm} m² (' + auswahl_text(
            objektart, stockwerk=stockwerk,
            aufzug=str(data.get('aufzug', 'nein')) == 'ja',
            fuellgrad=fuellgrad, sonderabfall=sonderabfall,
            klein_items=klein_items, klein_sonstiges=klein_sonstiges) + ')')[:500]

        # Erst nach der Feldpruefung zaehlen (EIG146): Ein Tippfehler in der
        # Flaeche kostet keinen Versuch mehr.
        if rate_limited(request, 'preisangebot', limit=10):
            return JsonResponse({'ok': False, 'error': 'Zu viele Anfragen. Bitte warten Sie eine Stunde.'}, status=429)

        # Der Rechner schickt das Angebot an die eingegebene Adresse und legt
        # eine Erinnerung an, die spaeter noch einmal zustellt. Beides waere
        # ohne Pruefung fremdnutzbar - siehe Kooperationsformular.
        from .models import PreisAngebot
        if ist_spam(
            request, 'preisangebot',
            name=name, email=email_raw, text=klein_sonstiges,
        ):
            # Nach aussen wie ein Erfolg - der Bot lernt nichts dazu.
            return JsonResponse({'ok': True})

        # Leistung, Groesse und Preis gehoeren in den Schluessel (P8/C1).
        # Genau hier war der Verlust am teuersten: Wer zwei Objekte
        # durchrechnet und sich beide Angebote schicken laesst, bekam das
        # zweite nie - **wofuer der Rechner gebaut ist**.
        duplikat = _doppelt(PreisAngebot, {
            'name': name, 'email': email_raw,
            'leistung_label': leistung_label, 'groesse_label': groesse_label,
            'pmin': preis, 'pmax': preis,
        })

        # Erst speichern, dann verschicken. Bis zum 06.09.2026 stand der
        # Thread-Start VOR dem ``create()`` - der Datensatz hatte in dem
        # Moment noch keine Kennung, an der sich ein Erfolg vermerken liesse.
        #
        # Und seit dem 24.09.2026 ueber ``_lead_speichern``: Vom 06. bis
        # 24.09.2026 scheiterte GENAU DIESER create() bei jeder Einsendung
        # (fremde NOT-NULL-Spalte ``ort`` in der Produktions-DB, Migration
        # 0020). Scheitert das Speichern noch einmal, gehen Mail und Push
        # trotzdem hinaus, und der Kunde sieht keinen 500.
        mail_args = (name, email_raw, leistung_label, groesse_label, preis, ort_roh)
        angebot = _lead_speichern(
            lambda: PreisAngebot.objects.create(
                name=name,
                email=email_raw,
                leistung_label=leistung_label,
                groesse_label=groesse_label,
                pmin=preis,
                pmax=preis,
                ort=ort_roh,
            ),
            'preisangebot', _send_rechner_emails, mail_args,
            {'name': name, 'ort': ort_roh,
             'objekt': f'{leistung_label}, {groesse_label}', 'richtpreis': preis})
        if angebot is None:
            return JsonResponse({'ok': True})
        versand_gewollt = not duplikat and mail_budget_ok()
        if versand_gewollt:
            _benachrichtigen(PreisAngebot, angebot.pk, _send_rechner_emails, mail_args)
        else:
            PreisAngebot.objects.filter(pk=angebot.pk).update(mail_gewollt=False)

        rabatt_hinweis = ' | Standort-Rabatt' if details['standort_rabatt'] else ''
        # Ohne Namen (P8/A4) - er steht im Datensatz.
        logger.info('Preisrechner | id=%s | %s | %s EUR%s | mail=%s',
                    angebot.pk, leistung_label, preis, rabatt_hinweis,
                    'ja' if versand_gewollt else 'nein')
        return JsonResponse({'ok': True})

    # Title und Description kommen aus der View, nicht aus dem Template: Die
    # Description nennt Preise, und {{ }} innerhalb eines {% include with %}-
    # Arguments wird von Django NICHT interpoliert - og:description trug sonst
    # den rohen Template-Text.
    return render(request, 'preisangebot.html', {
        # GE23: Der Hero-Absatz beantwortet die Frage (data/antworten.py).
        'hero_antwort': _rechner_antwort(),
        # EIG398: "Kosten berechnen" buendelt seit dem 02.10.2026
        # /entruempelung-kosten/; diese Seite bedient das Anfordern.
        'seo_title': 'Preisangebot anfordern: Entrümpelung | Rümpelwerk',
        'seo_description': (
            'Preisangebot anfordern: '
            f"Keller ab {euro(_PER_QM_PREISE['keller']['min_preis'])} €, "
            f"Wohnung ab {euro(_PER_QM_PREISE['wohnung']['min_preis'])} €, "
            f"Haus ab {euro(_PER_QM_PREISE['haus']['min_preis'])} €. "
            # EIG246/EIG254: Seit dem 17.09.2026 geht ohne den Schalter
            # KUNDENMAIL_AN_ABSENDER keine Mail an eine eingetippte Adresse -
            # "Angebot per E-Mail" nur, solange die Mail auch rausgeht.
            + ('Kostenlos, unverbindlich, Angebot per E-Mail.'
               if getattr(settings, 'KUNDENMAIL_AN_ABSENDER', False) else
               f'Kostenlos, unverbindlich, Antwort in {_ZUSAGE_REAKTION}.')
        ),
    })


# ---------------------------------------------------------------------------
# Leistungsseiten  /<leistung>/   (Block 2, A2/A3)
# ---------------------------------------------------------------------------
#
# Ein Template fuer alle Leistungen, Inhalt aus apps/core/data/services.py -
# dieselbe Aufteilung wie bei den Stadtseiten. Die Routen werden in urls.py aus
# _SERVICE_DATA erzeugt und stehen dort VOR dem Catch-All; ohne das wuerde
# city_landing_page /haushaltsaufloesung/ als unbekannte Stadt abfangen und
# einen 404 liefern.


def _leistung_verwandte(daten):
    """``related``-Slugs zu Links aufloesen.

    Solange eine verwandte Leistung noch keine eigene Seite hat, zeigt der Link
    auf ihren Anker in ``/dienstleistungen/``. Ein Link auf eine 404 waere
    schlechter als kein Link - dieselbe Regel wie bei den Nachbarstaedten (F18).
    """
    aus = []
    for slug in daten.get('related', ()):
        andere = leistung(slug)
        if andere:
            aus.append({'name': andere['label'], 'url': andere['url'],
                        'text': andere['answer'][:150], 'eigen': True})
        else:
            eintrag = next((l for l in S.LEISTUNGEN if l[0] == slug), None)
            if eintrag:
                aus.append({'name': eintrag[1], 'url': f'/dienstleistungen/#{slug}',
                            'text': eintrag[2], 'eigen': False})
    return aus


def _leistung_staedte(daten):
    """Staedte-Slugs zu Namen und Links aufloesen - Ortsnamen nur in cities.py.

    ``url`` zeigt auf die Matrixseite, sobald es sie fuer diese Kombination
    gibt (A13), sonst auf die allgemeine Stadtseite. Das raeumt zugleich eine
    alte Unstimmigkeit aus: Der Ankertext lautet "Haushaltsaufloesung Leipzig",
    das Ziel war aber /entrumpelung/leipzig/ - eine Seite ueber alle
    Leistungen. Ein Ankertext, der etwas anderes verspricht als das Ziel,
    schwaecht beide Seiten.
    """
    gebaut = set(matrix_kombinationen())
    aus = []
    for slug in daten.get('staedte', ()):
        stadt = _CITY_DATA.get(slug)
        if not stadt:
            continue
        eigen = (daten['slug'], slug) in gebaut
        aus.append({
            'name': stadt['name'], 'slug': slug, 'state': stadt['state'],
            'url': (f"/{daten['slug']}/{slug}/" if eigen
                    else f'/entrumpelung/{slug}/'),
            'eigen': eigen,
        })
    return aus


def service_page(request, service_slug):
    """Eine der neun Leistungsseiten, vollstaendig aus ``data/services.py``.

    Diese Seiten sind Landingpages laufender Werbekampagnen (Regel 23) - wer
    hier etwas aendert, aendert bezahlte Werbung mit.
    """
    daten = leistung(service_slug)
    if not daten:
        raise Http404
    site_url = _safe_site_url()
    pfad = f'/{service_slug}/'

    from .models import AktuellesPost
    referenzen = _enrich_posts(
        AktuellesPost.objects.filter(veroeffentlicht=True, typ='vorher_nachher')[:2]
    )

    # /entruempelung-kosten/ ist mit 4.100+ Woertern die laengste
    # Leistungsseite und bekommt laut Bauplan §4 den Rechner "im grossen
    # Format" statt in der Hero-Spalte der anderen acht - eigenes Template
    # heisst auch eigene, kleinere Critical-CSS-Datei (siehe
    # templates/service_kosten.html, komment am Kopf).
    template_name = ('service_kosten.html' if service_slug == 'entruempelung-kosten'
                      else 'service.html')

    return render(request, template_name, {
        'l': daten,
        'beispiele': beispiel_preise(service_slug),
        # Überschrift der gemeinsamen Preistabelle. Gehört in die View, nicht
        # ins Template: Dort stünde sie 8-mal, sobald alle Leistungen da sind.
        'preistabelle_titel': f"Was kostet eine {daten['name']}?",
        # Ueberschrift ueber dem eingebetteten Rechner (A15).
        # EIG398: Die Kostenseite traegt ihren eigenen Rechnertitel
        # ("Entruempelungskosten berechnen") - aus "Entruempelung berechnen"
        # wird sonst kein Satz.
        'rechner_titel': daten.get('rechner_titel') or f"{daten['name']} berechnen",
        'rechner_titel_em': f'in {_RECHNER_DAUER}',
        # PR06: Der Rechner zeigt den Preis erst nach Name und E-Mail
        # (rw_rechner.html, "rw-gate") - die Zeile darf nichts anderes sagen.
        'rechner_sub': ('Dieselbe Rechnung, die auch im Angebot steht. Kostenlos; '
                        'den Preis zeigt der Rechner nach Angabe von Name und '
                        'E-Mail – oder Sie fragen direkt per WhatsApp.'),
        'verwandte': _leistung_verwandte(daten),
        'staedte': _leistung_staedte(daten),
        # Artikel, die auf diese Leistung verweisen (T4) - der Rueckweg.
        # Die Kostenseite selbst ist ein Ratgeber und bekommt sie ebenso.
        'ratgeber_artikel': _ratgeber.artikel_zu_leistung(service_slug),
        # EIG29: og:type folgt dem Graph. rw_seo.html liest seo_type aus dem
        # durchgereichten Kontext; nur die Ratgeberseite ist ein Article.
        'seo_type': 'article' if service_slug in RATGEBER_SEITEN else '',
        'referenzen': referenzen,
        'seo_title': daten['seo_title'],
        'seo_description': daten['seo_description'],
        'seo_keywords': daten['seo_keywords'],
        # Kommt aus der View, nie hart "/" - genau das hat das entfernte
        # city_landing.html getan und auf 131 Seiten ein zweites Canonical auf
        # die Startseite gesetzt.
        'seo_path': pfad,
        'schema_bloecke': [
            S.service_page_schema(site_url, daten),
            S.breadcrumb_schema(site_url, daten['label'], pfad,
                                zwischen=('Dienstleistungen', '/dienstleistungen/')),
            S.faq_schema(daten['faq']),
            S.howto_schema(site_url, daten),
            # Article - aber nur fuer die Ratgeberseite unter den neun Slugs
            # (GE15). Welche das ist, steht in data/services.py; die Liste ist
            # dort begruendet, samt der Frage, warum die anderen acht draussen
            # bleiben. ``article_schema`` gibt ``None`` zurueck, wenn das
            # Erscheinungsdatum nicht belegt ist - ``_knoten()`` im Templatetag
            # laesst leere Bloecke fallen.
            #
            # ``headline`` ist der sichtbare ``h1``-Text der Seite
            # (``l.h1`` in service.html, Zeile 59), nicht ein zweiter
            # getippter Satz: Regel 12 verlangt, dass Schema und Sichtbares
            # dieselbe Quelle haben.
            _artikel_schema(site_url, pfad, daten)
            if service_slug in RATGEBER_SEITEN else None,
        ],
    })


def ratgeber_hub(request):
    """/ratgeber/ - Uebersicht der Wissensseiten mit Glossar (T4, 16.09.2026).

    Karten, Glossar und Schema kommen aus ``data/ratgeber.hub()`` - eine
    Liste fuer Sichtbares und Graph (Regel 12).
    """
    site_url = _safe_site_url()
    h = _ratgeber.hub()
    return render(request, 'ratgeber.html', {
        'h': h,
        'seo_title': h['seo_title'],
        'seo_description': h['seo_description'],
        'schema_bloecke': [
            S.ratgeber_hub_schema(site_url, h['gruppen'], quellen=h['quellen']),
            S.glossar_schema(site_url, h['glossar']),
            # GE17: Die Frage ueber dem Antwortblock ist sichtbar - also auch
            # ausgezeichnet, mit demselben Text.
            S.faq_schema([(h['answer_frage'], h['answer'])]),
        ],
    })


def ratgeber_artikel(request, artikel_slug):
    """Ein Ratgeberartikel unter ``/ratgeber/<slug>/`` (T6-T8).

    Die Route wird aus ``_RATGEBER_DATA`` erzeugt; ein unbekannter Slug kommt
    hier nie an. Die Pruefung bleibt trotzdem, falls jemand die Route von
    Hand eintraegt.
    """
    from django.templatetags.static import static
    from .data.lastmod import veroeffentlicht_fuer_pfad
    from .sitemaps import lastmod_fuer_pfad

    a = _ratgeber.artikel(artikel_slug)
    if not a:
        raise Http404
    site_url = _safe_site_url()
    pfad = a['url']
    leistungen = []
    for slug in a['leistungen']:
        eintrag = leistung(slug)
        if eintrag:
            leistungen.append({'name': eintrag['label'], 'url': eintrag['url'],
                               'text': eintrag['answer'][:150]})
    return render(request, 'ratgeber_artikel.html', {
        'a': a,
        'leistungen': leistungen,
        'staedte': [{'name': _CITY_DATA[s]['name'], 'url': f'/entrumpelung/{s}/'}
                    for s in a['staedte'] if s in _CITY_DATA],
        'weitere': [w for w in _ratgeber.alle_artikel()
                    if w['slug'] != artikel_slug],
        'lokal': (_ratgeber.lokal_staedte()
                  if any(x.get('lokal') for x in a['abschnitte']) else []),
        'seo_title': a['seo_title'],
        'seo_description': a['seo_description'],
        'seo_keywords': a['seo_keywords'],
        'seo_path': pfad,
        'schema_bloecke': [
            S.article_schema(
                site_url, pfad, a['h1'], beschreibung=a['seo_description'],
                veroeffentlicht=veroeffentlicht_fuer_pfad(pfad),
                geaendert=lastmod_fuer_pfad(pfad),
                bild=f"{site_url}{_feste.OG_BILD_PFAD}",
                # GE43: dieselbe Liste, die den sichtbaren Beleg am
                # Absatzende erzeugt (data/ratgeber.py) - Regel 12.
                quellen=a['quellen']),
            S.breadcrumb_schema(site_url, a['titel'], pfad,
                                zwischen=('Ratgeber', '/ratgeber/')),
            S.faq_schema(a['faq']),
        ],
    })


def _artikel_schema(site_url, pfad, daten):
    """Der ``Article``-Knoten einer Ratgeber-Leistungsseite (GE15).

    Beide Daten kommen aus ``apps/core/data/lastmod.py`` - dieselbe Quelle,
    aus der die Sitemap ihr ``lastmod`` und der ``WebPage``-Knoten sein
    ``dateModified`` holen (Regel 22, D2). Eine zweite Fallunterscheidung an
    dieser Stelle waere die naechste Liste, die auseinanderlaeuft.
    """
    from .sitemaps import lastmod_fuer_pfad
    from .data.lastmod import veroeffentlicht_fuer_pfad
    return S.article_schema(
        site_url, pfad, daten['h1'],
        beschreibung=daten.get('seo_description'),
        veroeffentlicht=veroeffentlicht_fuer_pfad(pfad),
        geaendert=lastmod_fuer_pfad(pfad),
        # GE43: dieselbe Liste, die den sichtbaren Beleg am Absatzende
        # erzeugt (data/quellen.py) - Regel 12.
        quellen=daten.get('quellen'),
    )


def matrix_page(request, service_slug, city_slug):
    """Leistung x Stadt - Charge 1 aus A13.

    Bewusst **eine** View fuer alle Kombinationen: Der Inhalt liegt in
    ``data/matrix.py``, die Darstellung in ``service_city.html``. Eine neue
    Kombination ist ein Eintrag, keine neue Funktion.
    """
    m = matrix(service_slug, city_slug)
    if not m:
        raise Http404
    site_url = _safe_site_url()
    l = m['leistung']

    from .models import AUTOR_META
    leiter = AUTOR_META.get(m['leiter_key'] or '')
    _ort_beispiele = matrix_beispiele(m)

    return render(request, 'service_city.html', {
        'm': m,
        'l': l,
        'stadt': m['stadt'],
        'lokal': m['lokal'],
        'leiter': leiter,
        # Eigene Ortsbeispiele der Matrixseite (Charge 2), mit dem
        # Standortnachlass gerechnet - sonst die allgemeinen der Leistung.
        'beispiele': _ort_beispiele or beispiel_preise(service_slug),
        'beispiele_mit_nachlass': bool(_ort_beispiele),
        'geschwister': _matrix_geschwister(service_slug, city_slug),
        'rechner_titel': f"{l['name']} in {m['stadt']['name']} berechnen",
        'rechner_titel_em': f'in {_RECHNER_DAUER}',
        'rechner_sub': ('Dieselbe Rechnung, die auch im Angebot steht. '
                        'Ein Nachlass für Ihren Ort ist, wo er gilt, schon eingerechnet.'),
        'seo_title': m['seo_title'],
        'seo_description': m['seo_description'],
        'seo_keywords': m['seo_keywords'],
        'seo_path': m['url'],
        'schema_bloecke': [
            S.matrix_page_schema(site_url, m),
            # Vierstufig: Startseite > Dienstleistungen > Leistung > Stadt.
            # Der sichtbare Brotkrumen im Template zeigt dieselben Stufen -
            # weichen sie ab, ist das ein Verstoss gegen Googles Regeln.
            S.breadcrumb_schema(
                site_url, m['stadt']['name'], m['url'],
                zwischen=(('Dienstleistungen', '/dienstleistungen/'),
                          (l['label'], l['url']))),
            S.faq_schema(m['faq']),
            # HowTo aus derselben Liste, die das Template sichtbar ausgibt
            # (G8). Die fuenf Matrixseiten waren die einzige Seitenklasse
            # ohne HowTo - Leistungs- und Stadtseiten haben es seit A3 bzw.
            # dem 21.08.2026. howto_schema() erwartet name/slug/ablauf; der
            # Slug ist hier zweistufig ("haushaltsaufloesung/leipzig").
            S.howto_schema(site_url, {
                'name': f"{l['name']} in {m['stadt']['name']}",
                'slug': m['url'].strip('/'),
                'ablauf': m['ablauf'],
            }),
        ],
    })


def _matrix_der_stadt(city_slug):
    """Alle gebauten Matrixseiten einer Stadt, fuer die Stadtseite."""
    raus = []
    for l_slug, s_slug in matrix_kombinationen():
        if s_slug != city_slug:
            continue
        m = matrix(l_slug, s_slug)
        if m:
            raus.append(m)
    return raus


def _matrix_geschwister(service_slug, city_slug):
    """Die anderen Matrixseiten derselben Stadt - fuer die "Passt dazu"-Karten.

    Sie sind zugleich die interne Verlinkung, die A13 verlangt (>=3 eingehende
    kontextuelle Links je Seite): Bei fuenf Leipzig-Seiten bekommt jede vier
    aus dieser Liste, dazu je einen von der Leistungsseite und der Stadtseite.
    """
    raus = []
    for l_slug, s_slug in matrix_kombinationen():
        if s_slug != city_slug or l_slug == service_slug:
            continue
        andere = matrix(l_slug, s_slug)
        if andere:
            raus.append(andere)
    return raus


# ---------------------------------------------------------------------------
# Stadtseiten (Programmatische lokale SEO)
# ---------------------------------------------------------------------------



def _stadt_slug_index():
    """Ortsname -> Slug, tolerant gegen Schreibweisen.

    Die Eintraege in ``nearby`` sind Freitext ("Halle (Saale)", "Dessau-Rosslau"),
    die Slugs dagegen kurz ("halle", "dessau"). Ein naives slugify traf deshalb
    daneben; deshalb wird auf beide Formen indiziert.
    """
    index = {}
    for slug, c in _CITY_DATA.items():
        index[_ort_key(c['name'])] = slug
        index[slug] = slug
    return index


def _ort_key(name):
    k = name.lower().split('(')[0].strip()
    for a, b in (('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue'), ('ß', 'ss'), (' ', '-'), ('.', '')):
        k = k.replace(a, b)
    return k


def _nearby_links(city, city_slug):
    """Nachbarorte mit Ziel-Slug, wo es eine Seite gibt.

    Grund (F18): 23 der damals 53 Stadtseiten hatten null eingehende interne Links und
    standen entsprechend auf "Gefunden - zurzeit nicht indexiert". Das Feld
    ``nearby`` existierte laengst, wurde aber nur als Text ausgegeben. Als Links
    gerendert loest es 166 der 260 Eintraege auf und hebt 51 der 53 Seiten auf
    mindestens einen thematischen Link - ohne eine einzige neue Zeile Inhalt.

    Orte ohne eigene Seite bleiben bewusst Text: ein Link auf eine 404 waere
    schlechter als kein Link.
    """
    index = _stadt_slug_index()
    orte = []
    for name in city['nearby']:
        ziel = index.get(_ort_key(name))
        orte.append({'name': name, 'slug': ziel if ziel and ziel != city_slug else ''})
    return orte


def entrumpelung_hub(request):
    """/entrumpelung/ — Verteilerseite fuer die 57 Stadtseiten (F11).

    Es gab 53 URLs unter /entrumpelung/<slug>/, aber kein Verzeichnis-Index:
    Der Aufruf lief in den Catch-All und endete als 404. Fuer Crawler ist eine
    Ebene ohne Index ein Sackgassen-Signal, fuer Nutzer, die die URL kuerzen,
    eine Fehlerseite.
    """
    site_url = _safe_site_url()
    pk = preis_context()

    # Nach Bundesland gruppiert, Randgebiet getrennt ausgewiesen.
    laender = {}
    for slug, c in _CITY_DATA.items():
        laender.setdefault(c['state'], []).append({
            'name': c['name'], 'slug': slug,
            'randgebiet': bool(c.get('randgebiet')),
            'region': c['region'],
        })
    gruppen = [
        {'state': land,
         'staedte': sorted(st, key=lambda x: x['name']),
         'randgebiet': all(x['randgebiet'] for x in st)}
        for land, st in sorted(laender.items(),
                               key=lambda kv: -len([x for x in kv[1] if not x['randgebiet']]))
    ]
    kern = sum(1 for c in _CITY_DATA.values() if not c.get('randgebiet'))

    _frage, _antwort = _hub_antwort('entrumpelung')
    # IS18 (16.09.2026): Die Seite hatte 398 Eigenwoerter bei 600 gefordert.
    # Dazu kommt keine Fuellprosa, sondern eine Uebersicht aus den Daten -
    # die sechs Standortstaedte mit Entsorger und Termin vor Ort, jede Zahl
    # aus cities.py/zusagen.py, jeder Entsorger aus city_lokal.py.
    standorte = [s for s in _ratgeber.STANDORTE if s in _CITY_DATA]
    standort_vergleich = {
        'anker': 'standorte-tabelle',
        'titel': 'Sechs Städte des Einsatzgebiets im Überblick',
        'kopf': ['Stadt', 'Bundesland', 'Kommunaler Entsorger',
                 'Termin vor Ort'],
        'zeilen': [
            [_CITY_DATA[s]['name'], _CITY_DATA[s]['state'],
             (city_lokal.lokal(s) or {}).get('traeger', '–'),
             _CITY_DATA[s]['response']]
            for s in standorte
        ],
        'fazit_frage': 'Wie schnell ist ein Team für die Entrümpelung vor Ort?',
        'fazit': (
            f'Das hängt vom Ort ab: In {_ZUSAGE_SCHNELL_ORTE} ist ein Team in '
            f'{_ZUSAGE_SCHNELL} vor Ort, im übrigen Kerngebiet in '
            f'{_ZUSAGE_TERMIN}. Auf jede Anfrage antwortet Rümpelwerk '
            f'Mitteldeutschland innerhalb von {_ZUSAGE_REAKTION}, die '
            f'Besichtigungstermine sind {_ZUSAGE_TERMIN_AB} buchbar.'
        ),
    }
    return render(request, 'entrumpelung_hub.html', {
        'vergleiche': [standort_vergleich],
        'standort_links': [{'name': _CITY_DATA[s]['name'],
                            'url': f'/entrumpelung/{s}/'} for s in standorte],
        # Antwort-zuerst-Block (G2), Text aus data/antworten.py.
        'antwort_frage': _frage,
        'antwort_text': _antwort,
        'gruppen': gruppen,
        'staedte_gesamt': len(_CITY_DATA),
        'staedte_kern': kern,
        # EIG252/EIG267 (SEO-Audit 25.09.2026): Titel, H1 und Footer nennen
        # dieselbe Zahl - alle Stadtseiten, nicht nur das Kerngebiet.
        # IS42 (01.10.2026): Nutzen und Preis im Titel statt Verzeichnis.
        'seo_title': (
            f"Entrümpelung in {len(_CITY_DATA)} Städten: Preise ab "
            f"{pk['PREISE']['keller']['min_txt']} € | Rümpelwerk"
        ),
        'seo_description': (
            f"Entrümpelung ab {pk['PREISE']['keller']['min_txt']} € in "
            f"{len(_CITY_DATA)} Städten in Sachsen-Anhalt, Sachsen, Niedersachsen. "
            f"Stadt wählen, Preis berechnen, Besichtigung vereinbaren."
        ),
        # Kein breadcrumb_schema hier: entrumpelung_hub.html uebergibt
        # seo_breadcrumb_name="Entrümpelung" an rw_seo.html, und rw_head_schema
        # baut daraus denselben zweistufigen Brotkrumen. Bis G1 standen beide
        # in getrennten <script>-Bloecken und fielen niemandem auf; im @graph
        # lagen sie als zwei identische BreadcrumbList nebeneinander.
        'schema_bloecke': [
            # GE13/GE17 (16.09.2026): die Leistung, um die es auf der Seite
            # geht, und die beiden sichtbaren Frage-Antwort-Paare.
            S.entruempelung_service_schema(
                site_url, [c['name'] for c in _CITY_DATA.values()
                           if not c.get('randgebiet')]),
            S.faq_schema([(_frage, _antwort),
                          (standort_vergleich['fazit_frage'],
                           standort_vergleich['fazit'])]),
            {
                '@context': 'https://schema.org',
                '@type': 'CollectionPage',
                '@id': f'{site_url}/entrumpelung/#sammlung',
                'name': 'Entrümpelung in Mitteldeutschland',
                'url': f'{site_url}/entrumpelung/',
                'isPartOf': {'@id': f'{site_url}/#website'},
                'about': {'@id': f'{site_url}/#business'},
                'mainEntity': {
                    '@type': 'ItemList',
                    'numberOfItems': len(_CITY_DATA),
                    'itemListElement': [
                        {'@type': 'ListItem', 'position': i,
                         'name': f"Entrümpelung {c['name']}",
                         'url': f'{site_url}/entrumpelung/{slug}/'}
                        for i, (slug, c) in enumerate(
                            sorted(_CITY_DATA.items(), key=lambda kv: kv[1]['name']), 1)
                    ],
                },
            },
        ],
    })


def _city_description(city):
    """Die Meta-Description einer Stadtseite - nach PIXELBREITE gedeckelt.

    Google schneidet Snippets nach rund 920 px ab, nicht nach einer Zeichenzahl.
    Der Nachsatz "Team aus <Ort>" ist ein Verkaufsargument (kein Callcenter),
    aber bei langen Stadtnamen sprengt er die Breite: "Lutherstadt Wittenberg"
    lag mit ihm bei 926 px. Statt eines Sonderfalls fuer diese eine Stadt faellt
    der Nachsatz ab einer Gesamtlaenge weg - das haelt auch fuer den naechsten
    langen Namen, den jemand ergaenzt.

    Der Schwellwert ist an der echten Messung geeicht
    (seo-geo-plan/tools/seo_snippets.py, Arial 14 px): 135 Zeichen liegen
    zuverlaessig unter 920 px, 140 nicht mehr. **Nach jeder Aenderung an
    diesem Text das Skript laufen lassen** - Zeichen sind nur ein Naeherungswert
    fuer Pixel, und deutsche Umlaute wiegen anders als Grossbuchstaben.

    Die Handlungsaufforderung steht seit dem 06.09.2026 am ENDE, nicht mehr in
    der Mitte (IS11). Sie stand vorher schon da - nur hinter ihr kam noch der
    Nachsatz, und ein Snippet, das mit "Antwort in 2-5 Werktagen." aufhoert,
    fordert zu nichts auf. Umgestellt, nicht ergaenzt: Der Deckel liegt bei 135
    Zeichen, ein zusaetzlicher Satz haette eine belegte Angabe verdraengt.

    **Seit dem 12.09.2026 beginnt sie mit "Jetzt".** Der Satz forderte sprachlich
    schon vorher zum Klick auf - nur steht das Verb "berechnen" in keiner Liste,
    mit der eine Messung eine Handlungsaufforderung erkennt, und was nicht
    erkannt wird, zaehlt nicht. Das eine Wort kostet sechs Zeichen, und die
    gehen genau dort verloren, wo es ohnehin eng war: Bei sieben Staedten mit
    langem Namen (Bernburg (Saale), Bitterfeld-Wolfen, Coswig (Sachsen),
    Dessau-Rosslau, Naumburg (Saale), Quedlinburg, Wernigerode) faellt jetzt
    der Nachsatz "Team aus <Ort>" weg. Das ist der Tausch, den dieser Deckel
    vorsieht - kein Sonderfall, sondern die Regel, fuer die er gebaut wurde.
    """
    ab = f"{euro(_PER_QM_PREISE['keller']['min_preis'])} €"
    cta = f" Jetzt Preis in {_RECHNER_DAUER} berechnen."
    if city.get('randgebiet'):
        return (f"Entrümpelung & Haushaltsauflösung {city['name']} ab {ab}. "
                "Anfahrt und Termin nach Absprache." + cta)
    # EIG138 (24.09.2026): "Termin vor Ort in", nicht "Antwort in" - response
    # ist die Hinfahrt, die Antwort sind ueberall 2 Stunden (Regel 24).
    # Dativ aus zusagen.response_dativ ("in 1–2 Werktagen", EIG153).
    termin = f" Termin vor Ort in {city.get('response_dativ') or city['response']}."
    # EIG33 (24.09.2026): ein Merkmal, das nur diese Stadt hat - die ersten
    # Ortsteile aus city_lokal.py. Vorher trugen alle Staedte derselben
    # Filiale dieselbe Formel ("Team aus Leipzig, Antwort in 1 Werktag"),
    # die Snippets unterschieden sich also nur im Stadtnamen. Das Wort
    # "Haushaltsaufloesung" steht seit EIG18 im Titel, hier bleibt dafuer
    # Platz fuer die Ortsteile. Von lang nach kurz, der erste unter dem Deckel.
    # Als Aufzaehlung ("Plagwitz, Connewitz und Umgebung"), nicht als "in X":
    # Viele Ortsteile tragen einen Artikel ("im Paulusviertel", "in der
    # Altstadt"). Ortsteile, die im Stadtnamen stecken ("Bitterfeld" bei
    # Bitterfeld-Wolfen) oder ihn enthalten ("Heidenau-Sued"), sagen nichts
    # Neues und fallen heraus.
    ortsteile = [o for o in ((city_lokal.lokal(city.get('slug', '')) or {})
                             .get('ortsteile') or ())
                 if o not in city['name'] and city['name'] not in o]
    kandidaten = []
    if len(ortsteile) >= 2:
        kandidaten.append(f"Entrümpelung {city['name']} ab {ab} – {ortsteile[0]}, "
                          f"{ortsteile[1]} und Umgebung." + termin + cta)
    if ortsteile:
        kandidaten.append(f"Entrümpelung {city['name']} ab {ab} – {ortsteile[0]} "
                          f"und Umgebung." + termin + cta)
    kandidaten.append(f"Entrümpelung & Haushaltsauflösung {city['name']} ab "
                      f"{ab}. Region {city['branch']}." + termin + cta)
    for text in kandidaten:
        if len(text) <= 135:
            return text
    return (f"Entrümpelung & Haushaltsauflösung {city['name']} ab {ab}."
            + termin + cta)


def _city_title(city):
    """Der Seitentitel einer Stadtseite (EIG18, 24.09.2026).

    Gesucht wird nicht nur "Entruempelung {Stadt}", sondern ebenso oft
    "Haushaltsaufloesung {Stadt}" und "... Kosten/Preise" (Search Console,
    28 Tage bis 21.09.2026: Magdeburg, Dresden, Wittenberg). Der Titel nennt
    deshalb beide Leistungen und die Preise. Die Marke faellt dafuer weg - sie
    passt nicht mehr unter 60 Zeichen, und Google zeigt den Websitenamen
    ohnehin ueber dem Titel an.

    Bis 60 Zeichen die lange Form (Namen bis 17 Zeichen, also auch
    "Bitterfeld-Wolfen"), darueber die kurze - heute nur "Lutherstadt
    Wittenberg". Pixel geprueft mit seo-geo-plan/tools/seo_snippets.py
    (Grenze 580 px). Titelaenderungen aendern das Anzeigenumfeld (Regel 23).
    """
    lang = f"Entrümpelung & Haushaltsauflösung {city['name']} – Preise"
    if len(lang) <= 60:
        return lang
    return f"Entrümpelung {city['name']} – Haushaltsauflösung"


def _leiter_meta(city):
    """Der Regionalleiter einer Stadt als Dict fuer das Template - oder None.

    Enthaelt ``foto``/``breite``/``hoehe`` aus ``AUTOR_META``; bei Christoph
    Regner ist ``foto`` ``None``, und das Template zeigt dann die Variante ohne
    Bild. Ein generischer Platzhalter waere schlechter als keines - er
    behauptete ein Foto einer Person, das keine Person zeigt.
    """
    from .models import AUTOR_META

    key = _leiter_key(city)
    if not key:
        return None
    meta = AUTOR_META.get(key)
    return dict(meta, key=key) if meta else None


from .data.cities import (STARTSEITE_STADT as _STARTSEITE_STADT,  # noqa: E402
                          standort_slug as _standort_slug)


def city_page(request, city_slug):
    """Eine der 54 Stadtseiten unter ``/entrumpelung/<slug>/``.

    Alles kommt aus ``data/cities.py`` und ``data/city_lokal.py``: Ortsteile,
    Wertstoffhof, Sperrmuellregelung, Beispiele, Nachbarorte. Auch diese Seiten
    sind Werbe-Zielseiten (Regel 23). Die Zeitzusage der Seite ist der **Termin
    vor Ort** (``city['response']``), nicht die Antwortzeit - das sind zwei
    verschiedene Zusagen (Regel 24).
    """
    from django.http import Http404
    city = _CITY_DATA.get(city_slug)
    if not city:
        raise Http404
    city = dict(city)
    city['slug'] = city_slug
    # Nur Staedte mit einer Reaktionszeit in *Stunden* duerfen mit Tempo werben.
    # 45 der 54 stehen auf '1 Werktag'; das Template versprach ihnen bis zum
    # 21.08.2026 pauschal "innerhalb von 2 Stunden" - auf 39 Seiten falsch und
    # im Widerspruch zu city.response weiter unten auf derselben Seite.
    city['schnell'] = reagiert_in_stunden(city)
    site_url = _safe_site_url()
    _pk = preis_context()
    faq_paare = S.city_faq_paare(city)
    _lok = city_lokal.lokal(city_slug) or {}
    _frage, _antwort = _stadt_antwort(city, _lok)
    _matrix_seiten = _matrix_der_stadt(city_slug)
    return render(request, 'city.html', {
        # Antwort-zuerst-Block (G2). Vier Satzbauten, gefuellt mit dem
        # Vokabular, das nur diese Stadt hat (Ortsteile, Entfernung, Termin) -
        # siehe data/antworten.py, Abschnitt zur Aehnlichkeit.
        'antwort_frage': _frage,
        'antwort_text': _antwort,
        'city': city,
        'city_slug': city_slug,
        # Die Matrixseiten dieser Stadt (A13). Leer fuer alle Staedte ausser
        # denen einer gebauten Charge - das Template blendet den Abschnitt
        # dann aus. Das ist zugleich der zweite eingehende kontextuelle Link
        # je Matrixseite, den A13 verlangt.
        'matrix_seiten': _matrix_seiten,
        # Ziel der fuenf "Leistung + Stadt"-Kacheln oben auf der Seite
        # (EIG341/EIG342): Gibt es fuer diese Stadt eine gebaute Matrixseite
        # zur Leistung, fuehrt die Kachel dorthin - genau der Anker, den sie
        # zeigt ("Haushaltsauflösung Leipzig"), statt auf den Rechner. Ohne
        # Matrixseite bleibt der Rechner das Ziel; das Template faellt dafuer
        # selbst auf '/preisangebot/' zurueck.
        'kat_urls': {m['leistung_slug']: m['url'] for m in _matrix_seiten},
        # Die Matrixseiten der Standortstadt, verlinkt aus ihrem Umland
        # (24.09.2026). /haushaltsaufloesung/leipzig/ und
        # /nachlassraeumung/leipzig/ waren Google laut Search Console "nicht
        # bekannt"; jede Umlandseite des Leipziger Teams gibt ihnen jetzt einen
        # kontextuellen Link mit "Leistung Stadt" als Ankertext.
        'matrix_region': (
            _matrix_der_stadt(_standort_slug(city))
            if _standort_slug(city) not in (None, city_slug) else []),
        'matrix_region_stadt': (_CITY_DATA.get(_standort_slug(city)) or {}).get('name', ''),
        # Halle: Die Startseite rankt fuer "entruempelung halle" und ist
        # bewusst die Halle-URL; die Stadtseite verlinkt sie (seo-technik.md).
        'startseite_link': city_slug == _STARTSEITE_STADT,
        # EIG83: "Beraeumung" in Sachsen und Sachsen-Anhalt (city_lokal.py).
        'raeum_wort': city_lokal.regionales_wort(city['state']),
        # Ratgeberartikel, die diese Stadt nennen (heute: die sechs
        # Standortstaedte) - ein Satz unter den Ortsangaben.
        'ratgeber_artikel': _ratgeber.artikel_zu_stadt(city_slug),
        # Recherchierte Ortsangaben (F17). None fuer Staedte ohne Daten - das
        # Template blendet den Abschnitt dann aus, statt Platzhalter zu zeigen.
        'lokal': city_lokal.lokal(city_slug),
        # Maschinenlesbar fuer <time datetime="…"> (G12). Beide Werte
        # kommen aus derselben Quelle, siehe data/stand.py - seit dem
        # 24.09.2026 je Stadt (city_lokal.stand), Leipzig ist neuer.
        'lokal_stand': city_lokal.stand(city_slug)[1],
        'lokal_stand_iso': city_lokal.stand(city_slug)[0],
        # Die Parken-Karte kann einen aelteren Stand tragen (Leipzig: 09.2024).
        'lokal_parken_stand': city_lokal.parken_stand(city_slug)[1],
        'lokal_parken_stand_iso': city_lokal.parken_stand(city_slug)[0],
        # Durchgerechnete Ortsbeispiele. Leer fuer Staedte ohne 'beispiele' -
        # das Template blendet den Abschnitt dann aus, wie bei jedem anderen
        # Feld aus city_lokal. Der Stadtname geht als 'stadtort' mit, damit der
        # Standortrabatt greift wie im Rechner.
        'beispiele': city_lokal.beispiele(city_slug, city['name']),
        # Laengen sind ausgereizt: Titel und Description waehlen ihre Form nach
        # der Zeichenzahl (_city_title, _city_description). Wer hier Text
        # ergaenzt, misst mit seo_snippets.py gegen ALLE Staedte nach, nicht
        # nur gegen Leipzig. Ortsteile und response bringen echte Varianz
        # hinein; wortgleiche Descriptions waeren das falsche Signal.
        'seo_title': _city_title(city),
        # Seit dem 21.08.2026 steht der Preisrechner auf dieser Seite - deshalb
        # darf das Snippet ihn nennen. "Preis in <RECHNER_DAUER> berechnen"
        # ist der einzige Grund zum Klicken, den die Franchise-Wettbewerber in
        # Halle und Leipzig nicht auch anbieten (siehe ADS.md, Wettbewerb).
        # Laenge nach Pixeln geprueft, nicht nach Zeichen: seo_snippets.py.
        'seo_description': _city_description(city),
        'seo_keywords': (
            f"Entrümpelung {city['name']}, Haushaltsauflösung {city['name']}, "
            f"Wohnungsauflösung {city['name']}, Kellerentrümpelung {city['name']}, "
            f"Nachlassräumung {city['name']}, Entrümpelung {city['state']}, "
            f"Entrümpelungsfirma {city['name']}, Haushaltsauflösung {city['region']}"
        ),
        'seo_path': f"/entrumpelung/{city_slug}/",
        'SITE_URL': site_url,
        'ADMIN_EMAIL': getattr(settings, 'ADMIN_EMAIL', ''),
        'nearby_links': _nearby_links(city, city_slug),
        # Der Block "Entruempelung in weiteren Staedten" - begruendete Auswahl
        # aus den Daten statt 30 hart getippter <a>-Tags (Befund W3).
        'weitere_staedte': weitere_staedte(city_slug),
        # Dieselbe Liste speist sichtbare FAQ und Schema - sie koennen
        # nicht mehr auseinanderlaufen.
        # JSON-LD kommt seit F5 aus apps/core/schema.py, nicht mehr aus dem
        # Template. Damit ist das Dezimalkomma-Problem strukturell erledigt.
        # G6: der zustaendige Regionalleiter, sichtbar und im Graphen. Die
        # Zuordnung kommt aus cities.leiter_key() - eine Quelle fuer alle 54
        # Staedte, dieselbe, die auch die Matrixseiten benutzen.
        'leiter': _leiter_meta(city),
        'schema_bloecke': [
            S.city_schema(site_url, city, city_slug),
            *S.personen_schema(site_url, [_leiter_key(city)] if _leiter_key(city) else []),
            S.breadcrumb_schema(site_url, f"Entrümpelung {city['name']}",
                                f'/entrumpelung/{city_slug}/',
                                zwischen=('Standorte', '/standorte/')),
            S.faq_schema(faq_paare),
        ],
        'city_faq': faq_paare,
    })


# ---------------------------------------------------------------------------
# City Landing Pages  /<city_slug>/   (homepage-style, alle deutschen Städte)
# ---------------------------------------------------------------------------


# ── Abgeschaltete Stadt-Landingpages ────────────────────────────────────────
# Unter /<stadt>/ lagen einmal 131 Landingpages. Sie sind entfernt, weil sie
# der Sichtbarkeit geschadet haben:
#
#   * Fuer die 53 Staedte aus _CITY_DATA gab es die Stadt DOPPELT – einmal hier
#     und einmal unter /entrumpelung/<stadt>/. Beide Seiten waren self-canonical
#     und zu 88 % textgleich, konkurrierten also in der Suche gegeneinander.
#   * Die uebrigen 78 kamen aus _EXTRA_LANDING_CITIES und waren untereinander zu
#     99 % identisch (nur der Stadtname wurde eingesetzt), hatten keinen einzigen
#     internen Link und standen auf Position 85-90. Google stufte sie als
#     Doorway-Pages ein: "Gefunden – zurzeit nicht indexiert" fuer 159 Seiten.
#
# Beide Dicts bleiben bestehen: _CITY_DATA speist die echten Stadtseiten,
# _EXTRA_LANDING_CITIES liefert hier noch den Stadtnamen fuer die 410-Seite.
_LANDING_REDIRECTS = frozenset(_CITY_DATA)
# EIG140: Aliase (cities.LANDING_ALIASE) leiten auf eine andere Stadtseite
# weiter und gehoeren deshalb nicht zu den 410ern.
from .data.cities import LANDING_ALIASE as _LANDING_ALIASE  # noqa: E402
_LANDING_GONE = (frozenset(_EXTRA_LANDING_CITIES) - _LANDING_REDIRECTS
                 - frozenset(_LANDING_ALIASE))


def city_landing_page(request, city_slug):
    """Catch-All fuer /<slug>/ – bedient nur noch die abgeschalteten Landingpages.

    Muss das LETZTE Pattern in urls.py bleiben, sonst kapert es echte Routen.
    """
    # Servicegebiet: die Detailseite hat den reicheren Inhalt und saemtliche
    # internen Links – dorthin dauerhaft weiterleiten, damit die Signale der
    # alten URL uebergehen statt verloren zu sein.
    if city_slug in _LANDING_REDIRECTS:
        # GET/HEAD 301, alles andere 308: Die abgeschalteten Landingpages
        # trugen selbst ein Anfrageformular, ihre Adressen stehen in altem
        # Werbematerial. Ein 301 auf einen POST von dort haette die Anfrage
        # stillschweigend verworfen.
        return dauerhaft_weiter(f'/entrumpelung/{city_slug}/', request)
    if city_slug in _LANDING_ALIASE:
        return dauerhaft_weiter(
            f'/entrumpelung/{_LANDING_ALIASE[city_slug]}/', request)

    # Ausserhalb des Servicegebiets: 410 statt 404. Das ist die ehrliche
    # Antwort ("gab es, ist weg") und Google raeumt sie schneller aus dem Index.
    if city_slug in _LANDING_GONE:
        return render(
            request, 'gone.html',
            {'city_name': _EXTRA_LANDING_CITIES[city_slug].get('name', '')},
            status=410,
        )

    raise Http404
