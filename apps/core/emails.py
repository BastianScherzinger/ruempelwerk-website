"""HTML-E-Mails und ihr Versand - ueber SMTP oder die Resend-HTTP-API.

Aus ``views.py`` herausgeloest (F6). Reines Verschieben, kein Verhalten geaendert.

WELCHEN WEG DIESE DATEI NIMMT (seit 06.09.2026)
-----------------------------------------------
``settings.MAIL_WEG`` entscheidet, und zwar an genau **einer** Stelle in diesem
Modul: :func:`_absenden`. Die neun Versandfunktionen darunter bauen weiterhin
denselben Resend-Payload wie zuvor - sie wissen nicht, wohin er geht.

⚠ **Der frueher hier stehende Satz "Railway blockiert ausgehendes SMTP" war
richtig und ist es nicht mehr.** Railway sperrt SMTP auf den Tarifen Free,
Trial und Hobby; dieser Arbeitsbereich laeuft auf **Pro**. Nachgesehen am
06.09.2026 in der Railway-Dokumentation *und* im Tarif-Bildschirm des Kontos -
nicht vermutet, weil genau diese Sorte abgelaufener Annahme monatelang eine
Entscheidung getragen hat. **Woran sie haengt: am Tarif.** Faellt der
Arbeitsbereich auf Hobby zurueck, faellt SMTP mit.

Der Resend-Weg bleibt vollstaendig erhalten und ist der Rueckweg: Wer
``EMAIL_HOST_PASSWORD`` aus der Umgebung entfernt, sendet wieder ueber Resend,
ohne dass eine Zeile Code geaendert wird. Fuer diesen Weg gilt weiterhin: Jeder
Request braucht den Header ``User-Agent: Ruempelwerk-Website/1.0``, sonst
antwortet Cloudflare mit Error 1010.

Der Versand laeuft immer in einem Daemon-Thread, damit der Request nicht
blockiert.

Adress-Konvention: ``CONTACT_EMAIL`` ist die oeffentlich angezeigte Adresse,
``ADMIN_EMAILS`` sind die Empfaenger-Postfaecher (Liste, aus der Umgebungs-
variablen ``ADMIN_EMAIL`` kommagetrennt gelesen). Nie vertauschen.

RUECKGABEWERT DER VERSANDFUNKTIONEN (seit 06.09.2026, P8/C3)
-----------------------------------------------------------
``_send_anfrage_email``, ``_send_koop_emails``, ``_send_bewerbung_emails`` und
``_send_rechner_emails`` geben ``True`` zurueck, wenn die **Benachrichtigung an
ADMIN_EMAILS** hinausgegangen ist, sonst ``False``. ``views._versand_ausfuehren``
vermerkt daran ``mail_gesendet`` am Datensatz, und der stuendliche Nachzuegler
holt nach, was ``False`` geblieben ist.

**Warum die Admin-Mail den Ausschlag gibt und nicht die Kundenbestaetigung:**
Verlorengeht bei einer ausgefallenen Admin-Mail ein **Auftrag** - der Betrieb
erfaehrt nie, dass jemand angefragt hat. Eine ausgefallene Kundenbestaetigung
kostet Hoeflichkeit, nicht Geschaeft, und ein Nachzuegler, der sie wiederholte,
riskierte dafuer eine doppelte Mail im Postfach eines Kunden, dessen Anfrage
laengst bearbeitet ist. Was diese Regel **nicht** leistet: Eine
Kundenbestaetigung, die allein scheitert, wird nie wiederholt und faellt
niemandem auf - sie steht nur als ``logger.error`` im Log.

``True``/``False`` heisst ausserdem: *die Resend-API hat den Request
angenommen*. Ob die Mail zugestellt wird, weiss diese Datei nicht.
"""

import html as _html
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

# Zeitzusagen kommen aus den Daten, nicht aus dem f-String (Befund K2). Die
# Bestaetigungsmail ist eine schriftliche Zusage an einen namentlich bekannten
# Kunden - sie war die schwerste der neun Stellen, an denen "max. 2 Stunden"
# stand, obwohl nur 4 von 54 Staedten eine Stundenzusage haben.
from .data.zusagen import (ANGEBOT_BEI_BESICHTIGUNG as _ZUSAGE_ANGEBOT,
                           ANTWORT as _ZUSAGE_REAKTION)
# Preise mit deutschem Tausenderpunkt (EIG161): ``f'{preis:,}'`` schrieb
# "1,450 €" - im Deutschen liest sich das als eins Komma vier fuenf.
from .data.pricing import euro
from .data.firma import FIRMA as _FIRMA, INHABER as _INHABER


def _mail_fuss():
    """Fußzeile jeder Mail: Jahr zur Laufzeit, Name aus firma.py (EIG248).

    Bis zum 24.09.2026 stand hier fünfmal „© 2026“ fest, dreimal davon mit einem
    falschen Firmennamen (ohne „Mittel“).
    """
    from datetime import date
    return (f'&copy; {date.today().year} {_html.escape(_FIRMA)} '
            f'&middot; Inh. {_html.escape(_INHABER)}')


logger = logging.getLogger('apps.core')


def _kein_versandweg(was):
    """Kein Versandweg konfiguriert - ERROR fuer die Fehlerwache, Alarm per Telegram.

    Bis zum 24.09.2026 stand an diesen sechs Stellen ``logger.warning``. Die
    Fehlerwache sieht erst ab ERROR; ein Deploy ohne ``RESEND_API_KEY`` und
    ohne ``EMAIL_HOST_PASSWORD`` haette jede Benachrichtigung verschluckt,
    ohne dass es irgendwo aufgefallen waere. Die Fehlerwache selbst meldet
    ueber genau diesen Weg - deshalb zusaetzlich der Telegram-Alarm.
    """
    logger.error('%s übersprungen: kein Versandweg konfiguriert '
                 '(weder EMAIL_HOST_PASSWORD noch RESEND_API_KEY)', was)
    from . import telegram
    telegram.alarm('Kein Mailversand möglich: weder EMAIL_HOST_PASSWORD noch '
                   'RESEND_API_KEY gesetzt. Anfragen stehen nur im Dashboard.',
                   'kein-versandweg')


# ── Der einzige Punkt, an dem diese Datei das Netz beruehrt ─────────────────
#
# Vorher stand ``urllib.request.urlopen`` **neunmal** in dieser Datei, einmal je
# Versandfunktion. Neun Kopien heisst: neun Stellen, die man beim Anbieterwechsel
# findet - oder eben nicht. Jetzt gibt es eine.
#
# ``_absenden`` nimmt denselben ``urllib.request.Request``, den die neun
# Funktionen ohnehin bauen, und entscheidet erst hier, was damit geschieht. Die
# Funktionen darunter sind **unveraendert**: derselbe Payload, dieselbe
# Protokollierung, dieselben Rueckgabewerte. Das war Absicht - ein Anbieterwechsel
# ist kein Anlass, 900 Zeilen einer Datei anzufassen, an der Auftraege haengen.
#
# WAS DIESE FUNKTION NICHT LEISTET: Sie sagt nichts darueber, ob eine Mail
# **zugestellt** wird. Auf dem SMTP-Weg heisst ihr ``True`` nur "der Mailserver
# hat die Nachricht angenommen", auf dem Resend-Weg "die API hat den Request
# angenommen". Ein Bounce faellt danach an und ist von hier aus unsichtbar -
# genau daran ist am 25.08.2026 zwoelf Tage lang niemandem aufgefallen, dass
# ``oliver@...`` gar nicht existiert. Der Beleg fuer Zustellung steht im
# Postfach, nicht im Log.


def _weg():
    """``'smtp'``, ``'resend'`` oder ``'aus'`` - **zur Aufrufzeit** bestimmt.

    ``settings.MAIL_WEG`` steht daneben und sagt dasselbe, wird aber beim Start
    berechnet, weil Django ``EMAIL_BACKEND`` zu diesem Zeitpunkt braucht. Diese
    Funktion liest die Zugangsdaten jedes Mal neu.

    **Warum das nicht Doppelpflege ist, sondern ihr Gegenteil:** Ein
    eingefrorener Wert laesst sich weder in einem Test noch in der Shell
    bewegen - ``override_settings(RESEND_API_KEY=...)`` haette ins Leere
    gegriffen, und die sieben Tests, die genau das tun, waeren stillschweigend
    an einem Versandweg vorbeigelaufen, den es im Test gar nicht gab.
    ``EinVersandwegTests`` haelt beide Stellen gegeneinander; laufen sie
    auseinander, ist der Lauf rot.
    """
    if getattr(settings, 'EMAIL_HOST_USER', '') and \
       getattr(settings, 'EMAIL_HOST_PASSWORD', ''):
        return 'smtp'
    if getattr(settings, 'RESEND_API_KEY', ''):
        return 'resend'
    return 'aus'


class _SmtpAntwort:
    """Sieht aus wie eine HTTP-Antwort - damit die neun Aufrufstellen bleiben.

    Bewusst eine Attrappe und keine Umschreibung der neun Funktionen: Die
    bestehenden ``with ... as resp``-Bloecke lesen ``resp.status`` und
    ``resp.read()`` und protokollieren beides. Eine Attrappe mit genau diesen
    zwei Faehigkeiten haelt neun sorgfaeltig formulierte Logzeilen am Leben,
    die sonst alle haetten neu geschrieben werden muessen.
    """

    def __init__(self, empfaenger):
        self.status = 200
        self._koerper = json.dumps(
            {'weg': 'smtp', 'to': empfaenger}, ensure_ascii=False)

    def read(self):
        return self._koerper.encode('utf-8')

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def _antwort_an(email):
    """Reply-To einer Benachrichtigung an den Betrieb: die Adresse des Anfragenden.

    Seit 24.09.2026 (MW21). Vorher trug jede Benachrichtigung ``CONTACT_EMAIL``
    als Reply-To - wer im Postfach auf "Antworten" drueckte, schrieb an den
    Betrieb selbst statt an den Kunden. Nur fuer Mails **an ``ADMIN_EMAILS``**:
    Eine Kundenmail behaelt ``CONTACT_EMAIL``, sonst antwortete der Kunde sich
    selbst. Eine ungueltige Adresse faellt auf ``CONTACT_EMAIL`` zurueck.
    """
    from django.core.exceptions import ValidationError
    from django.core.validators import validate_email
    email = (email or '').strip()
    try:
        validate_email(email)
    except ValidationError:
        return [settings.CONTACT_EMAIL]
    return [email]


def _eigene_adressen():
    """Die Adressen des Betriebs - nur an sie geht Post ohne ``KUNDENMAIL_AN_ABSENDER``."""
    adressen = list(getattr(settings, 'ADMIN_EMAILS', []))
    adressen += [getattr(settings, 'CONTACT_EMAIL', ''), getattr(settings, 'DEFAULT_FROM_EMAIL', '')]
    return {a.strip().lower() for a in adressen if a and a.strip()}


class _Unterdrueckt(_SmtpAntwort):
    """Antwort fuer eine Mail, die bewusst nicht rausging."""

    def __init__(self):
        self.status = 204
        self._koerper = json.dumps({'weg': 'unterdrueckt'})


def _absenden(req, timeout=10, an_fremde=False):
    """Schickt den Request - per SMTP oder per Resend, je nach ``MAIL_WEG``.

    **Ohne ``KUNDENMAIL_AN_ABSENDER`` nur an die eigenen Adressen** (seit
    17.09.2026). Jede Mail an eine eingetippte Adresse ist eine Mail an einen
    Fremden, wenn ein Bot das Formular ausfuellt - mit dessen Text im Namen.
    Fremde Empfaenger werden hier herausgefiltert; bleibt keiner uebrig, geht
    nichts raus und die Aufrufstelle bekommt Status 204. ``an_fremde=True``
    nur fuer ``pruefe_mail --senden``, wo ein Mensch den Empfaenger tippt.

    Wirft dieselben Ausnahmen wie ``urllib.request.urlopen``: Die neun
    Aufrufstellen fangen ``urllib.error.HTTPError`` und ``Exception`` und geben
    ``False`` zurueck. Eine ``SMTPException`` faellt in den zweiten Zweig, und
    der stuendliche Nachzuegler aus ``views.py`` holt die Mail nach. Deshalb
    hier **kein** ``fail_silently``: Ein verschluckter Fehler waere ein
    ``mail_gesendet=True`` fuer eine Mail, die nie ankam.
    """
    if not (an_fremde or getattr(settings, 'KUNDENMAIL_AN_ABSENDER', False)):
        daten = json.loads(req.data.decode('utf-8'))
        alle = daten['to'] if isinstance(daten['to'], list) else [daten['to']]
        eigene = _eigene_adressen()
        erlaubt = [a for a in alle if a.strip().lower() in eigene]
        if not erlaubt:
            logger.info('Mail an eingetippte Adresse unterdrueckt | %s',
                        daten.get('subject', '')[:60])
            return _Unterdrueckt()
        if erlaubt != alle:
            daten['to'] = erlaubt
            req.data = json.dumps(daten).encode('utf-8')
    if _weg() != 'smtp':
        return urllib.request.urlopen(req, timeout=timeout)

    daten = json.loads(req.data.decode('utf-8'))
    empfaenger = daten['to'] if isinstance(daten['to'], list) else [daten['to']]

    nachricht = EmailMultiAlternatives(
        subject=daten.get('subject', ''),
        body=daten.get('text') or '',
        from_email=daten.get('from') or settings.DEFAULT_FROM_EMAIL,
        to=empfaenger,
        # Antworten gehen an die oeffentliche Adresse, nicht an den Absender.
        # Bis zum 06.09.2026 stand unter jeder Kundenmail ein ``From``, das kein
        # Postfach hatte - **wer auf sein Angebot antwortete, bekam eine
        # Unzustellbarkeitsmeldung.** Ein gesetztes Reply-To macht diesen Fehler
        # unmoeglich, auch wenn jemand DEFAULT_FROM_EMAIL kuenftig wieder auf
        # etwas Totes stellt. Benachrichtigungen an den Betrieb bringen seit
        # 24.09.2026 ihr eigenes ``reply_to`` mit (``_antwort_an``, MW21).
        reply_to=daten.get('reply_to') or [settings.CONTACT_EMAIL],
    )
    if daten.get('html'):
        nachricht.attach_alternative(daten['html'], 'text/html')
    nachricht.send(fail_silently=False)
    return _SmtpAntwort(empfaenger)


# ── Gestaltete Mails: gemeinsame Bausteine (seit 26.09.2026) ────────────────
#
# Das HTML steht seitdem in ``templates/emails/`` (``basis.html`` + je eine
# Vorlage fuer Betrieb und Kunde) und nicht mehr in f-Strings.
# Djangos Autoescape maskiert jede Eingabe; ``|safe`` kommt dort nicht vor.
# Die Textfassungen der Mails stehen unveraendert unten in den
# Versandfunktionen - sie sind der Inhalt, das HTML ist die Aufmachung.
#
# Links zeigen immer auf die Live-Domain, nicht auf ``SITE_URL``: Lokal steht
# dort ``localhost``, und eine Mail wird ueberall gelesen, nur nicht dort.

_SITE = 'https://ruempelwerk-mitteldeutschland.de'
_DOMAIN = 'ruempelwerk-mitteldeutschland.de'


def _marke():
    """Stammdaten fuer Kopf und Fuss jeder Mail - aus firma.py (Regel 25)."""
    from datetime import date
    from .data import firma
    return {
        'firma': firma.FIRMA, 'inhaber': firma.INHABER,
        'strasse': firma.STRASSE, 'plz': firma.PLZ, 'ort': firma.ORT,
        'telefon': firma.TELEFON, 'telefon_anzeige': firma.TELEFON_ANZEIGE,
        'kontakt': settings.CONTACT_EMAIL, 'site': _SITE, 'domain': _DOMAIN,
        'jahr': date.today().year,
    }


def _render(vorlage, **kontext):
    """Rendert eine Mailvorlage - und liefert bei jedem Fehler ``''`` statt zu werfen.

    Funktion vor Design: Die HTML-Fassung wird gebaut, bevor der Versand
    beginnt. Wuerfe eine kaputte Vorlage, ginge mit ihr die Benachrichtigung
    verloren. So geht die Mail mit der Textfassung allein hinaus, und der
    Fehler steht als ERROR in der Fehlerwache.

    EIG337/EIG366: ``vorlage`` ist nie Nutzereingabe, sondern einer der
    festen Namen aus den Aufrufen unten in dieser Datei - ``admin.html``,
    ``kunde.html``.
    """
    try:
        from django.template.loader import render_to_string
        kontext['marke'] = _marke()
        return render_to_string(f'emails/{vorlage}', kontext)
    except Exception:                                           # noqa: BLE001
        logger.error('Mailvorlage %s nicht gerendert - Versand nur als Text',
                     vorlage, exc_info=True)
        return ''


def _tel_href(telefon):
    """Die waehlbare Form einer eingetippten Nummer - leer, wenn keine drinsteckt."""
    import re
    roh = re.sub(r'[^\d+]', '', telefon or '')
    return roh if sum(ch.isdigit() for ch in roh) >= 5 else ''


def _zeitpunkt(wann=None):
    """Datum und Uhrzeit in deutscher Ortszeit (``TIME_ZONE``, Europe/Berlin)."""
    from django.utils import timezone
    return timezone.localtime(wann or timezone.now()).strftime('%d.%m.%Y, %H:%M Uhr')


def _gueltige_adresse(email):
    """Die Adresse, wenn sie gueltig ist - sonst leer (dann kein Antworten-Knopf)."""
    from django.core.exceptions import ValidationError
    from django.core.validators import validate_email
    email = (email or '').strip()
    try:
        validate_email(email)
    except ValidationError:
        return ''
    return email


# ``art`` (der Formularschluessel) und der Modellname in der Django-Verwaltung
# sind fuer drei der vier alten Formulare zufaellig gleich - fuer die
# Terminbuchung nicht: ``art='termin'``, Model ``Besichtigungstermin``.
_ADMIN_MODELLNAME = {'termin': 'besichtigungstermin'}


def _admin_link(model_name, pk=None, suche=''):
    """Absolute Adresse in der Django-Verwaltung - mit Kennung direkt, sonst als Suche.

    Die Betriebsmail kennt die Kennung nicht (der Nachzuegler baut sie aus
    denselben Argumenten wie der erste Versuch); sie verlinkt deshalb die
    Suche nach der Mailadresse.
    """
    from urllib.parse import quote
    model_name = _ADMIN_MODELLNAME.get(model_name, model_name)
    pfad = str(getattr(settings, 'ADMIN_PATH', 'admin')).strip('/')
    basis = f'{_SITE}/{pfad}/core/{model_name}/'
    if pk:
        return f'{basis}{pk}/change/'
    return f'{basis}?q={quote(suche)}' if suche else basis


def _feld(label, wert, art=''):
    wert = '' if wert is None else str(wert)
    feld = {'label': label, 'wert': wert, 'art': art}
    if art == 'tel':
        feld['href'] = _tel_href(wert)
    return feld


#: Formular -> (Anzeige, Modellname). Die Schluessel sind die Modellnamen,
#: damit ``views._benachrichtigen`` sie aus ``model._meta.model_name`` nimmt.
_FORMULARE = {
    'anfrage': 'Anfrage',
    'preisangebot': 'Preisanfrage',
    'kooperationsanfrage': 'Kooperationsanfrage',
    'bewerbung': 'Bewerbung',
    'termin': 'Terminanfrage',
}


def _formular_daten(art, args):
    """Name, Adresse, Ort und Feldliste - aus denselben Argumenten wie die Versandfunktion.

    Die Reihenfolge der ``args`` ist die der vier ``_send_*``-Funktionen; so
    braucht weder die Betriebsmail noch die Kopie eine zweite Feldliste.
    """
    # Die Betreiber-Kopie kommt aus ``views._benachrichtigen`` mit dem
    # Modellnamen - bei der Terminbuchung ``besichtigungstermin``, nicht ``termin``.
    art = {v: k for k, v in _ADMIN_MODELLNAME.items()}.get(art, art)
    a = list(args) + [''] * 8
    if art == 'anfrage':
        name, leistung, email, telefon, adresse, zusatz = a[:6]
        from . import telegram
        ort = telegram.plz_ort(adresse or '')
        felder = [_feld('Leistung', leistung, 'stark'), _feld('Name', name),
                  _feld('E-Mail', email, 'mail'), _feld('Telefon', telefon, 'tel'),
                  _feld('Adresse des Objekts', adresse),
                  _feld('Zusätzliche Informationen', zusatz, 'lang')]
    elif art == 'preisangebot':
        name, email, leistung, groesse, preis, ort = a[:6]
        telefon = ''
        felder = [_feld('Name', name), _feld('E-Mail', email, 'mail'),
                  _feld('Leistung', leistung, 'stark'), _feld('Größe', groesse),
                  _feld('Ort', ort),
                  _feld('Richtpreis', f'{euro(preis)} €' if preis not in ('', None) else '')]
    elif art == 'kooperationsanfrage':
        name, firma, email, telefon, art_label, nachricht = a[:6]
        ort = ''
        felder = [_feld('Name', name), _feld('Firma', firma),
                  _feld('E-Mail', email, 'mail'), _feld('Telefon', telefon, 'tel'),
                  _feld('Art der Kooperation', art_label, 'stark'),
                  _feld('Nachricht', nachricht, 'lang')]
    elif art == 'bewerbung':
        name, email, stelle, nachricht, telefon = a[:5]
        ort = ''
        felder = [_feld('Name', name), _feld('E-Mail', email, 'mail'),
                  _feld('Telefon', telefon, 'tel'), _feld('Stelle', stelle, 'stark'),
                  _feld('Nachricht', nachricht, 'lang')]
    elif art == 'termin':
        name, telefon, email, adresse, objektart, termin_text, hinweis, art_anzeige = a[:8]
        ort = adresse
        felder = [_feld('Termin', termin_text, 'stark'),
                  _feld('Art', art_anzeige or 'Vor Ort', 'stark'),
                  _feld('Objektart', objektart),
                  _feld('Name', name), _feld('Telefon', telefon, 'tel'),
                  _feld('E-Mail', email, 'mail'),
                  _feld('Adresse des Objekts', adresse),
                  _feld('Hinweis', hinweis, 'lang')]
    else:
        raise ValueError(f'unbekanntes Formular: {art}')
    return {'art_titel': _FORMULARE[art], 'name': str(name or ''),
            'email': str(email or ''), 'telefon': str(telefon or ''),
            'ort': str(ort or ''), 'felder': felder}


def _kundenmail_hinweis():
    """Der Satz fuer den Betrieb: Hat der Absender selbst eine Mail bekommen?"""
    if getattr(settings, 'KUNDENMAIL_AN_ABSENDER', False):
        return 'Der Absender hat zusätzlich eine Bestätigung per Mail bekommen.'
    return ('Der Absender hat KEINE Bestätigung per Mail bekommen '
            '(Kundenmails sind abgeschaltet) – bitte selbst melden.')


def _build_admin_email(art, args, hinweis=''):
    """HTML der Benachrichtigung an ADMIN_EMAILS - ein Aufbau fuer alle vier Formulare.

    Wirft nie (siehe ``_render``): Im Fehlerfall ``''``, die Mail geht als Text.
    """
    try:
        d = _formular_daten(art, args)
    except Exception:                                           # noqa: BLE001
        logger.error('Betriebsmail-HTML %s nicht gebaut', art, exc_info=True)
        return ''
    return _render(
        'admin.html',
        art=d['art_titel'], kennung=f'Neue {d["art_titel"]}',
        titel=f'{d["art_titel"]} von {d["name"]}',
        preheader=' · '.join(x for x in (d['name'], d['ort'], d['telefon']) if x),
        zeitpunkt=_zeitpunkt(), felder=d['felder'],
        antwort_an=_gueltige_adresse(d['email']),
        antwort_betreff=f'Re: Ihre {d["art_titel"]} bei {_FIRMA}',
        telefon_href=_tel_href(d['telefon']),
        admin_url=_admin_link(art, suche=d['email']),
        hinweis=hinweis,
    )


def _build_html_email(name, leistung, email, telefon, adresse, zusatz_info):
    """HTML der Anfrage-Benachrichtigung (Name und Signatur seit F6 unveraendert)."""
    return _build_admin_email(
        'anfrage', (name, leistung, email, telefon, adresse, zusatz_info),
        hinweis=f'Zusage auf der Website: Rückmeldung in {_ZUSAGE_REAKTION}.')

def _send_anfrage_email(name, leistung, email, telefon, adresse, zusatz_info):
    """Benachrichtigung an ADMIN_EMAILS. True, wenn sie hinausgegangen ist."""
    # ``api_key`` wird nur noch fuer den Resend-Header gebraucht; ob
    # ueberhaupt versandt werden kann, entscheidet ``MAIL_WEG``.
    #
    # ⚠ Hier stand bis zum 06.09.2026 ``if not api_key: return``. Das war
    # richtig, solange Resend der einzige Weg war - und waere beim Wechsel
    # auf SMTP zur Falle geworden: Wer RESEND_API_KEY entfernt, haette
    # damit **jeden** Versand abgeschaltet, noch vor dem Engpass, und die
    # Logzeile haette einen Grund genannt, der nicht mehr der Grund ist.
    api_key = getattr(settings, 'RESEND_API_KEY', '')
    if _weg() == 'aus':
        _kein_versandweg('Mail-Versand')
        return False

    text = (
        f"Neue Anfrage über die Website:\n\n"
        f"Name:       {name}\n"
        f"Leistung:   {leistung}\n"
        f"E-Mail:     {email}\n"
        f"Telefon:    {telefon or '–'}\n"
        f"Adresse:    {adresse or '–'}\n\n"
        f"Zusatzinfo:\n{zusatz_info or '–'}"
    )
    html_body = _build_html_email(name, leistung, email, telefon, adresse, zusatz_info)

    payload = json.dumps({
        'from': settings.DEFAULT_FROM_EMAIL,
        'to': list(settings.ADMIN_EMAILS),
        'reply_to': _antwort_an(email),
        'subject': f'[Rümpelwerk] Neue Anfrage von {name}',
        'text': text,
        'html': html_body,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.resend.com/emails',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Ruempelwerk-Website/1.0',
        },
    )
    # ADMIN_EMAILS bleibt in diesen Zeilen stehen, die Kundenadressen sind
    # ueberall entfernt (P8/A4). Der Unterschied ist nicht Bequemlichkeit:
    # ADMIN_EMAILS sind die eigenen Postfaecher des Betriebs, kommen aus einer
    # Umgebungsvariablen und sind bei zwei Empfaengern die einzige Angabe, an
    # der sich eine Zustellstoerung ueberhaupt einem Postfach zuordnen laesst.
    # Eine Kundenadresse im Log leistet dagegen nichts, was der Datensatz in
    # der Datenbank nicht besser leistet.
    try:
        with _absenden(req, timeout=10) as resp:
            body = resp.read().decode('utf-8')
            logger.info(
                f'Mail gesendet | an={", ".join(settings.ADMIN_EMAILS)} | '
                f'status={resp.status} | response={body}'
            )
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        logger.error(
            f'Resend HTTP-Fehler | status={e.code} | '
            f'from={settings.DEFAULT_FROM_EMAIL} | to={", ".join(settings.ADMIN_EMAILS)} | '
            f'response={body}'
        )
    except Exception as e:
        logger.error(
            f'Mail-Versand fehlgeschlagen | to={", ".join(settings.ADMIN_EMAILS)} | '
            f'fehler={type(e).__name__}: {e}'
        )
    return False


def _build_termin_email(name, telefon, email, adresse, objektart, termin_text, hinweis,
                        art_anzeige='Vor Ort'):
    """HTML der Terminanfrage-Benachrichtigung (Bauplan §5).

    ``art_anzeige`` ist seit 01.10.2026 das achte Argument ("Vor Ort" oder "Per
    WhatsApp-Video") - mit Vorgabe, damit ein aelterer Aufrufer weiter laeuft.
    """
    video = 'video' in (art_anzeige or '').lower()
    return _build_admin_email(
        'termin', (name, telefon, email, adresse, objektart, termin_text, hinweis,
                   art_anzeige),
        hinweis=('Anfrage, keine feste Buchung - Oliver Pohl bestätigt '
                 'telefonisch (Bauplan §5). Keine Mail an den Kunden.'
                 + (' VIDEO-BESICHTIGUNG: Zum Termin per WhatsApp-Videoanruf auf '
                    'die angegebene Telefonnummer anrufen (keine Aufzeichnung).'
                    if video else '')))


def _send_termin_email(name, telefon, email, adresse, objektart, termin_text, hinweis,
                       art_anzeige='Vor Ort'):
    """Benachrichtigung an ADMIN_EMAILS für eine Terminanfrage.

    Genau wie ``_send_anfrage_email``: **nur** an ``settings.ADMIN_EMAILS`` -
    der Kunde bekommt laut Bauplan §5 keine Mail, solange
    ``KUNDENMAIL_AN_ABSENDER`` aus ist (Standard, Regel oben im Modulkopf).
    """
    api_key = getattr(settings, 'RESEND_API_KEY', '')
    if _weg() == 'aus':
        _kein_versandweg('Mail-Versand')
        return False

    text = (
        f'Neue Terminanfrage über die Website:\n\n'
        f'Termin:     {termin_text}\n'
        f'Art:        {art_anzeige or "Vor Ort"}\n'
        f'Objektart:  {objektart}\n'
        f'Name:       {name}\n'
        f'Telefon:    {telefon or "–"}\n'
        f'E-Mail:     {email or "–"}\n'
        f'Adresse:    {adresse or "–"}\n\n'
        f'Hinweis:\n{hinweis or "–"}'
    )
    html_body = _build_termin_email(name, telefon, email, adresse, objektart,
                                     termin_text, hinweis, art_anzeige)

    payload = json.dumps({
        'from': settings.DEFAULT_FROM_EMAIL,
        'to': list(settings.ADMIN_EMAILS),
        'reply_to': _antwort_an(email),
        'subject': (f'[Rümpelwerk] Terminanfrage (Video) von {name}'
                    if 'video' in (art_anzeige or '').lower()
                    else f'[Rümpelwerk] Terminanfrage von {name}'),
        'text': text,
        'html': html_body,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.resend.com/emails',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Ruempelwerk-Website/1.0',
        },
    )
    try:
        with _absenden(req, timeout=10) as resp:
            body = resp.read().decode('utf-8')
            logger.info(
                f'Mail gesendet | an={", ".join(settings.ADMIN_EMAILS)} | '
                f'status={resp.status} | response={body}'
            )
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        logger.error(
            f'Resend HTTP-Fehler | status={e.code} | '
            f'from={settings.DEFAULT_FROM_EMAIL} | to={", ".join(settings.ADMIN_EMAILS)} | '
            f'response={body}'
        )
    except Exception as e:
        logger.error(
            f'Mail-Versand fehlgeschlagen | to={", ".join(settings.ADMIN_EMAILS)} | '
            f'fehler={type(e).__name__}: {e}'
        )
    return False


# Cloudinary-Auslieferungs-URLs haben die Form
#   https://res.cloudinary.com/<cloud>/image/upload/<transformationen>/v123/pfad.jpg
# Ohne Transformationen liefert Cloudinary das **unveraenderte Original**
# (bis 8 MB pro Upload, s. GALERIE-Limit). Das war der Haupttreiber des
# 6,5-MB-Payloads im PageSpeed-Report. Wir schieben daher eine
# Auto-Format-/Auto-Qualitaets-/Breitenbegrenzung in den Upload-Pfad.

def _build_koop_email_kunde(name, firma, art_label):
    return _render(
        'kunde.html', art='Kooperationsanfrage', kennung='Kooperation',
        titel='Ihre Kooperationsanfrage', anrede=f'Hallo {name},',
        preheader='Ihre Kooperationsanfrage ist bei uns eingegangen.',
        absaetze=['vielen Dank für Ihre Kooperationsanfrage! Wir haben Ihre '
                  'Anfrage erhalten und melden uns bei Ihnen.'],
        angaben_label='Ihre Angaben',
        felder=[_feld('Firma', firma, 'stark'), _feld('Art der Kooperation', art_label)],
        knopf_text='Zur Kooperationsseite', knopf_url=f'{_SITE}/kooperationspartner/',
        kontakt_satz='Fragen vorab? Sie erreichen uns unter',
    )

def _send_koop_emails(name, firma, email, telefon, art_label, nachricht):
    """Bestaetigung an den Anfragenden + Benachrichtigung an ADMIN_EMAILS.

    Der Rueckgabewert bezieht sich auf die **Admin-Mail** - Begruendung im
    Modul-Docstring.
    """
    # ``api_key`` wird nur noch fuer den Resend-Header gebraucht; ob
    # ueberhaupt versandt werden kann, entscheidet ``MAIL_WEG``.
    #
    # ⚠ Hier stand bis zum 06.09.2026 ``if not api_key: return``. Das war
    # richtig, solange Resend der einzige Weg war - und waere beim Wechsel
    # auf SMTP zur Falle geworden: Wer RESEND_API_KEY entfernt, haette
    # damit **jeden** Versand abgeschaltet, noch vor dem Engpass, und die
    # Logzeile haette einen Grund genannt, der nicht mehr der Grund ist.
    api_key = getattr(settings, 'RESEND_API_KEY', '')
    if _weg() == 'aus':
        _kein_versandweg('Koop-Mail')
        return False

    html_kunde = _build_koop_email_kunde(name, firma, art_label)

    # Bestätigung an Anfragenden
    payload = json.dumps({
        'from': settings.DEFAULT_FROM_EMAIL,
        'to': [email],
        'subject': 'Ihre Kooperationsanfrage – Rümpelwerk Mitteldeutschland',
        'html': html_kunde,
        'text': (
            f"Hallo {name},\n\n"
            f"vielen Dank für Ihre Kooperationsanfrage!\n\n"
            f"Firma: {firma}\n"
            f"Art: {art_label}\n\n"
            f"Wir melden uns bei Ihnen.\n\n"
            f"Rümpelwerk Mitteldeutschland – Inh. Oliver Pohl"
        ),
    }).encode('utf-8')
    req = urllib.request.Request(
        'https://api.resend.com/emails',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Ruempelwerk-Website/1.0',
        },
    )
    try:
        with _absenden(req, timeout=10) as resp:
            logger.info(f'Koop-Kundenmail gesendet | status={resp.status}')
    except Exception as exc:
        logger.error(f'Koop-Kundenmail fehlgeschlagen | {exc}')

    # Benachrichtigung an Admin
    admin_payload = json.dumps({
        'from': settings.DEFAULT_FROM_EMAIL,
        'to': list(settings.ADMIN_EMAILS),
        'reply_to': _antwort_an(email),
        'subject': f'[Rümpelwerk] Neue Kooperationsanfrage von {name} ({firma})',
        'html': _build_admin_email(
            'kooperationsanfrage', (name, firma, email, telefon, art_label, nachricht),
            hinweis=_kundenmail_hinweis()),
        'text': (
            f"Neue Kooperationsanfrage:\n\n"
            f"Name:    {name}\n"
            f"Firma:   {firma}\n"
            f"E-Mail:  {email}\n"
            f"Telefon: {telefon or '–'}\n"
            f"Art:     {art_label}\n\n"
            f"Nachricht:\n{nachricht or '–'}"
        ),
    }).encode('utf-8')
    req2 = urllib.request.Request(
        'https://api.resend.com/emails',
        data=admin_payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Ruempelwerk-Website/1.0',
        },
    )
    try:
        with _absenden(req2, timeout=10) as resp:
            logger.info(f'Koop-Adminmail gesendet | status={resp.status}')
            return True
    except Exception as exc:
        logger.error(f'Koop-Adminmail fehlgeschlagen | {exc}')
    return False

def _build_bewerbung_email_kunde(name, stelle):
    return _render(
        'kunde.html', art='Bewerbung', kennung='Bewerbung',
        titel='Deine Bewerbung', anrede=f'Hallo {name},',
        preheader='Deine Bewerbung ist bei uns eingegangen.',
        absaetze=['vielen Dank für deine Bewerbung! Wir haben sie erhalten und '
                  'melden uns bei dir.'],
        angaben_label='Deine Angaben',
        felder=[_feld('Stelle / Wunschposition', stelle, 'stark')],
        knopf_text='Zur Jobs-Seite', knopf_url=f'{_SITE}/jobs/',
        kontakt_satz='Fragen? Du erreichst uns unter',
    )

def _send_bewerbung_emails(name, email, stelle, nachricht, telefon=''):
    """Bestaetigung an den Bewerber + Benachrichtigung an ADMIN_EMAILS.

    Der Rueckgabewert bezieht sich auf die **Admin-Mail** - Begruendung im
    Modul-Docstring.
    """
    # ``api_key`` wird nur noch fuer den Resend-Header gebraucht; ob
    # ueberhaupt versandt werden kann, entscheidet ``MAIL_WEG``.
    #
    # ⚠ Hier stand bis zum 06.09.2026 ``if not api_key: return``. Das war
    # richtig, solange Resend der einzige Weg war - und waere beim Wechsel
    # auf SMTP zur Falle geworden: Wer RESEND_API_KEY entfernt, haette
    # damit **jeden** Versand abgeschaltet, noch vor dem Engpass, und die
    # Logzeile haette einen Grund genannt, der nicht mehr der Grund ist.
    api_key = getattr(settings, 'RESEND_API_KEY', '')
    if _weg() == 'aus':
        _kein_versandweg('Bewerbungsmail')
        return False

    html_kunde = _build_bewerbung_email_kunde(name, stelle)

    payload = json.dumps({
        'from': settings.DEFAULT_FROM_EMAIL,
        'to': [email],
        'subject': 'Deine Bewerbung – Rümpelwerk Mitteldeutschland',
        'html': html_kunde,
        'text': (
            f"Hallo {name},\n\n"
            f"vielen Dank für deine Bewerbung!\n\n"
            f"Stelle: {stelle}\n\n"
            f"Wir melden uns bei dir.\n\n"
            f"Rümpelwerk Mitteldeutschland – Inh. Oliver Pohl"
        ),
    }).encode('utf-8')
    req = urllib.request.Request(
        'https://api.resend.com/emails',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Ruempelwerk-Website/1.0',
        },
    )
    try:
        with _absenden(req, timeout=10) as resp:
            logger.info(f'Bewerbungsmail an Bewerber gesendet | status={resp.status}')
    except Exception as exc:
        logger.error(f'Bewerbungsmail fehlgeschlagen | {exc}')

    admin_payload = json.dumps({
        'from': settings.DEFAULT_FROM_EMAIL,
        'to': list(settings.ADMIN_EMAILS),
        'reply_to': _antwort_an(email),
        'subject': f'[Rümpelwerk] Neue Bewerbung von {name} – {stelle}',
        'html': _build_admin_email(
            'bewerbung', (name, email, stelle, nachricht, telefon),
            hinweis=_kundenmail_hinweis()),
        'text': (
            f"Neue Spontanbewerbung:\n\n"
            f"Name:     {name}\n"
            f"E-Mail:   {email}\n"
            f"Telefon:  {telefon or '–'}\n"
            f"Stelle:   {stelle}\n\n"
            f"Nachricht:\n{nachricht or '–'}"
        ),
    }).encode('utf-8')
    req2 = urllib.request.Request(
        'https://api.resend.com/emails',
        data=admin_payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Ruempelwerk-Website/1.0',
        },
    )
    try:
        with _absenden(req2, timeout=10) as resp:
            logger.info(f'Bewerbungsmail an Admin gesendet | status={resp.status}')
            return True
    except Exception as exc:
        logger.error(f'Bewerbungsmail Admin fehlgeschlagen | {exc}')
    return False

def _build_rechner_email_kunde(name, leistung_label, groesse_label, preis):
    return _render(
        'kunde.html', art='Richtangebot', kennung='Richtangebot',
        titel='Ihr Richtangebot', anrede=f'Hallo {name},',
        preheader=f'Ihr unverbindlicher Richtpreis: {euro(preis)} €',
        absaetze=['vielen Dank für Ihre Anfrage. Hier ist Ihr unverbindliches '
                  f'Richtangebot von {_FIRMA}.'],
        preis=euro(preis), preis_label='Richtpreis',
        preis_zusatz='inkl. Arbeit, Transport & Entsorgung',
        angaben_label='Ihre Angaben',
        felder=[_feld('Leistungsart', leistung_label, 'stark'),
                _feld('Objektgröße', groesse_label)],
        punkte=[f'Rückmeldung in {_ZUSAGE_REAKTION} nach der Anfrage.',
                'Kostenlose Besichtigung & verbindliches Angebot '
                f'{_ZUSAGE_ANGEBOT} – Festpreis, verbindlich im Angebot.',
                'Entsorgungsnachweis auf Wunsch · Besenreine Übergabe.'],
        knopf_text='Jetzt verbindlich anfragen', knopf_url=f'{_SITE}/anfrage/',
        kontakt_satz='Fragen zum Angebot? Sie erreichen uns unter',
        kleingedrucktes='Dieses Richtangebot ist unverbindlich. Der endgültige '
                        'Preis wird nach kostenloser Besichtigung festgelegt.',
    )


def _build_rechner_reminder_email(name, leistung_label, preis):
    return _render(
        'kunde.html', art='Erinnerung', kennung='Ihr Richtangebot',
        titel='Ihr Richtangebot von gestern', anrede=f'Hallo {name},',
        preheader='Ihr Richtangebot von gestern – können wir noch helfen?',
        absaetze=['gestern haben Sie auf unserer Website ein kostenloses '
                  'Richtangebot angefragt. Haben Sie alles Nötige gefunden – '
                  'oder können wir noch etwas für Sie tun?',
                  'Der endgültige Festpreis wird nach einer kostenlosen '
                  'Besichtigung vor Ort festgelegt und steht im verbindlichen Angebot.'],
        preis=euro(preis), preis_label='Ihr Richtpreis',
        preis_zusatz='unverbindlich · inkl. Arbeit & Entsorgung',
        angaben_label='Ihre Anfrage',
        felder=[_feld('Angefragte Leistung', leistung_label, 'stark')],
        knopf_text='Jetzt kostenlose Besichtigung anfragen',
        knopf_url=f'{_SITE}/anfrage/',
        kontakt_satz='Lieber direkt sprechen? Sie erreichen uns unter',
        kleingedrucktes='Sie erhalten diese E-Mail, weil Sie gestern auf unserer '
                        'Website ein Richtangebot angefordert haben.',
    )

def _send_rechner_reminder(angebot):
    # ``api_key`` wird nur noch fuer den Resend-Header gebraucht; ob
    # ueberhaupt versandt werden kann, entscheidet ``MAIL_WEG``.
    #
    # ⚠ Hier stand bis zum 06.09.2026 ``if not api_key: return``. Das war
    # richtig, solange Resend der einzige Weg war - und waere beim Wechsel
    # auf SMTP zur Falle geworden: Wer RESEND_API_KEY entfernt, haette
    # damit **jeden** Versand abgeschaltet, noch vor dem Engpass, und die
    # Logzeile haette einen Grund genannt, der nicht mehr der Grund ist.
    api_key = getattr(settings, 'RESEND_API_KEY', '')
    if _weg() == 'aus':
        _kein_versandweg('Reminder')
        return False

    preis = (angebot.pmin + angebot.pmax) // 2
    html = _build_rechner_reminder_email(angebot.name, angebot.leistung_label, preis)
    payload = json.dumps({
        'from': settings.DEFAULT_FROM_EMAIL,
        'to': [angebot.email],
        'subject': 'Ihr Richtangebot von gestern – alles geklärt?',
        'html': html,
        'text': (
            f"Hallo {angebot.name},\n\n"
            f"gestern haben Sie ein kostenloses Richtangebot angefragt.\n\n"
            f"Leistung: {angebot.leistung_label}\n"
            f"Richtpreis: {euro(preis)} €\n\n"
            f"Jetzt kostenlose Besichtigung anfragen:\n"
            f"https://ruempelwerk-mitteldeutschland.de/anfrage/\n\n"
            f"Rümpelwerk Mitteldeutschland – Inh. Oliver Pohl"
        ),
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.resend.com/emails',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Ruempelwerk-Website/1.0',
        },
    )
    with _absenden(req, timeout=10) as resp:
        # EIG302: Status 204 heisst "unterdrueckt" (Empfaenger nicht vom Betrieb,
        # ``KUNDENMAIL_AN_ABSENDER`` aus) - keine Mail ist rausgegangen, und das
        # Log darf nicht "gesendet" sagen. Rueckgabewert: ging wirklich eine raus?
        if resp.status == 204:
            logger.info(f'Reminder unterdrueckt | id={angebot.pk}')
            return False
        logger.info(f'Reminder gesendet | id={angebot.pk} | status={resp.status}')
        return True

def _send_rechner_emails(name, kunden_email, leistung_label, groesse_label, preis,
                         ort=''):
    """Richtangebot an den Kunden + Benachrichtigung an ADMIN_EMAILS.

    ``ort`` (seit 24.09.2026) ist das Ortsfeld des Rechners; es steht in der
    Admin-Mail, damit der Betrieb weiss, wohin es geht.

    Der Rueckgabewert bezieht sich auf die **Admin-Mail** - Begruendung im
    Modul-Docstring.
    """
    # ``api_key`` wird nur noch fuer den Resend-Header gebraucht; ob
    # ueberhaupt versandt werden kann, entscheidet ``MAIL_WEG``.
    #
    # ⚠ Hier stand bis zum 06.09.2026 ``if not api_key: return``. Das war
    # richtig, solange Resend der einzige Weg war - und waere beim Wechsel
    # auf SMTP zur Falle geworden: Wer RESEND_API_KEY entfernt, haette
    # damit **jeden** Versand abgeschaltet, noch vor dem Engpass, und die
    # Logzeile haette einen Grund genannt, der nicht mehr der Grund ist.
    api_key = getattr(settings, 'RESEND_API_KEY', '')
    if _weg() == 'aus':
        _kein_versandweg('Rechner-Mail')
        return False

    html_kunde = _build_rechner_email_kunde(name, leistung_label, groesse_label, preis)

    # E-Mail an Kunden
    payload = json.dumps({
        'from': settings.DEFAULT_FROM_EMAIL,
        'to': [kunden_email],
        'subject': 'Ihr Richtangebot – Rümpelwerk Mitteldeutschland',
        'html': html_kunde,
        'text': (
            f"Hallo {name},\n\n"
            f"hier ist Ihr Richtangebot von Rümpelwerk Mitteldeutschland:\n\n"
            f"Leistung: {leistung_label}\n"
            f"Größe: {groesse_label}\n"
            f"Richtpreis: {euro(preis)} €\n\n"
            f"Inkl. Arbeit, Transport & Entsorgung.\n"
            f"Kostenlose Besichtigung & verbindliches Angebot {_ZUSAGE_ANGEBOT}.\n\n"
            f"Jetzt anfragen: https://ruempelwerk-mitteldeutschland.de/anfrage/\n\n"
            f"Rümpelwerk Mitteldeutschland – Inh. Oliver Pohl"
        ),
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.resend.com/emails',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Ruempelwerk-Website/1.0',
        },
    )
    try:
        with _absenden(req, timeout=10) as resp:
            body = resp.read().decode('utf-8')
            logger.info(f'Rechner-Mail an Kunden gesendet | status={resp.status}')
    except urllib.error.HTTPError as exc:
        body = exc.read().decode('utf-8')
        logger.error(f'Rechner-Mail Fehler | status={exc.code} | response={body}')
    except Exception as exc:
        logger.error(f'Rechner-Mail fehlgeschlagen | fehler={type(exc).__name__}: {exc}')

    # Benachrichtigung an Admin
    admin_payload = json.dumps({
        'from': settings.DEFAULT_FROM_EMAIL,
        'to': list(settings.ADMIN_EMAILS),
        'reply_to': _antwort_an(kunden_email),
        'subject': f'[Rümpelwerk Rechner] Preisanfrage von {name}',
        'html': _build_admin_email(
            'preisangebot', (name, kunden_email, leistung_label, groesse_label, preis, ort),
            hinweis=_kundenmail_hinweis()),
        'text': (
            f"Neue Preisanfrage über den Preisrechner:\n\n"
            f"Name:     {name}\n"
            f"E-Mail:   {kunden_email}\n"
            f"Leistung: {leistung_label}\n"
            f"Größe:    {groesse_label}\n"
            f"Ort:      {ort or '–'}\n"
            f"Richtpreis: {euro(preis)} €\n\n"
            # Seit 17.09.2026 geht keine Mail an eine eingetippte Adresse
            # (KUNDENMAIL_AN_ABSENDER aus) - der Satz "wurde an den Kunden
            # gesendet" stimmte seitdem nicht mehr.
            + ("Das Richtangebot wurde auch an den Kunden gesendet."
               if getattr(settings, 'KUNDENMAIL_AN_ABSENDER', False) else
               "Der Kunde hat KEINE Mail bekommen (Kundenmails sind abgeschaltet) "
               "- bitte selbst melden.")
        ),
    }).encode('utf-8')

    req2 = urllib.request.Request(
        'https://api.resend.com/emails',
        data=admin_payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Ruempelwerk-Website/1.0',
        },
    )
    try:
        with _absenden(req2, timeout=10) as resp:
            logger.info(f'Rechner-Admin-Mail gesendet | status={resp.status}')
            return True
    except Exception as exc:
        logger.error(f'Rechner-Admin-Mail fehlgeschlagen | fehler={type(exc).__name__}: {exc}')
    return False

def _fmt_duration(seconds: int) -> str:
    """Format seconds as MM:SS string."""
    m, s = divmod(max(0, seconds), 60)
    return f'{m}:{s:02d} Min'

def _trend(today_val: int, prev_val: int) -> str:
    if prev_val == 0:
        return '–'
    diff = today_val - prev_val
    if diff > 0:
        return f'↑ +{diff}'
    if diff < 0:
        return f'↓ {diff}'
    return '→ ±0'

def _leads_block(leads):
    """(HTML, Text) der Anfragezahlen im Tagesreport - leer ohne ``leads``.

    Seit 24.09.2026 (Paket 1): Der Report nannte nur Besucherzahlen. Dass
    zwei Wochen lang keine einzige Rechner-Anfrage ankam, stand in keiner
    Zahl, die jemand jeden Morgen sah.
    """
    if not leads:
        return '', ''
    zeilen = [
        ('Anfragen', leads.get('anfragen', 0)),
        ('Preisrechner', leads.get('rechner', 0)),
        ('Kooperation', leads.get('kooperation', 0)),
        ('Bewerbungen', leads.get('bewerbungen', 0)),
        ('Spamverdacht (ohne Mail)', leads.get('verdacht', 0)),
    ]
    offen = leads.get('offen', 0)
    farbe = '#f87171' if offen else '#4ade80'
    html_zeilen = ''.join(
        f'<tr><td style="padding:4px 0;color:#9ca3af;font-size:13px;">{t}</td>'
        f'<td style="padding:4px 0;color:#e5e7eb;font-size:13px;text-align:right;font-weight:700;">{n}</td></tr>'
        for t, n in zeilen)
    html_zeilen += (
        f'<tr><td style="padding:8px 0 0;color:{farbe};font-size:13px;font-weight:700;">'
        f'Nicht zugestellt (gesamt)</td>'
        f'<td style="padding:8px 0 0;color:{farbe};font-size:13px;text-align:right;font-weight:700;">{offen}</td></tr>')
    html_block = (
        '<tr><td style="padding:24px 32px 0;">'
        '<p style="margin:0 0 8px;font-size:13px;color:#9ca3af;text-transform:uppercase;'
        'letter-spacing:1px;font-weight:700;">Anfragen gestern</p>'
        f'<table width="100%" cellpadding="0" cellspacing="0">{html_zeilen}</table>'
        '</td></tr>')
    text_block = ('Anfragen gestern:\n'
                  + ''.join(f'  {t}: {n}\n' for t, n in zeilen)
                  + f'  Nicht zugestellt (gesamt): {offen}\n\n')
    return html_block, text_block


def _send_daily_report_email(stats, history, leads=None):
    import html as _html
    leads_html, leads_text = _leads_block(leads)
    # ``api_key`` wird nur noch fuer den Resend-Header gebraucht; ob
    # ueberhaupt versandt werden kann, entscheidet ``MAIL_WEG``.
    #
    # ⚠ Hier stand bis zum 06.09.2026 ``if not api_key: return``. Das war
    # richtig, solange Resend der einzige Weg war - und waere beim Wechsel
    # auf SMTP zur Falle geworden: Wer RESEND_API_KEY entfernt, haette
    # damit **jeden** Versand abgeschaltet, noch vor dem Engpass, und die
    # Logzeile haette einen Grund genannt, der nicht mehr der Grund ist.
    api_key = getattr(settings, 'RESEND_API_KEY', '')
    if _weg() == 'aus':
        _kein_versandweg('Daily-Report')
        return

    prev = history[0] if history else None
    visitor_trend = _trend(stats.unique_visitors, prev.unique_visitors if prev else 0)

    # Build history rows
    history_rows = ''
    for h in reversed(history):
        history_rows += (
            f'<tr>'
            f'<td style="padding:6px 12px;color:#9ca3af;font-size:13px;">{h.date.strftime("%d.%m.%Y")}</td>'
            f'<td style="padding:6px 12px;color:#e5e7eb;font-size:13px;text-align:center;">{h.unique_visitors}</td>'
            f'<td style="padding:6px 12px;color:#e5e7eb;font-size:13px;text-align:center;">{h.total_sessions}</td>'
            f'<td style="padding:6px 12px;color:#e5e7eb;font-size:13px;text-align:center;">{h.total_pageviews}</td>'
            f'<td style="padding:6px 12px;color:#e5e7eb;font-size:13px;text-align:center;">{_fmt_duration(h.avg_session_seconds)}</td>'
            f'</tr>'
        )
    # Today row (highlighted)
    history_rows += (
        f'<tr style="background:rgba(22,163,74,0.15);">'
        f'<td style="padding:6px 12px;color:#4ade80;font-size:13px;font-weight:700;">'
        f'{stats.date.strftime("%d.%m.%Y")} ← gestern</td>'
        f'<td style="padding:6px 12px;color:#4ade80;font-size:13px;font-weight:700;text-align:center;">{stats.unique_visitors}</td>'
        f'<td style="padding:6px 12px;color:#4ade80;font-size:13px;font-weight:700;text-align:center;">{stats.total_sessions}</td>'
        f'<td style="padding:6px 12px;color:#4ade80;font-size:13px;font-weight:700;text-align:center;">{stats.total_pageviews}</td>'
        f'<td style="padding:6px 12px;color:#4ade80;font-size:13px;font-weight:700;text-align:center;">{_fmt_duration(stats.avg_session_seconds)}</td>'
        f'</tr>'
    )

    html_body = f'''<!DOCTYPE html>
<html lang="de">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0f172a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;padding:32px 16px;">
<tr><td align="center">
<table width="100%" style="max-width:580px;background:#1e293b;border-radius:12px;overflow:hidden;border:1px solid #334155;">

  <!-- Header -->
  <tr><td style="background:#16a34a;padding:24px 32px;">
    <p style="margin:0;font-size:13px;color:#dcfce7;letter-spacing:1px;text-transform:uppercase;font-weight:700;">Rümpelwerk Mitteldeutschland</p>
    <h1 style="margin:8px 0 0;font-size:22px;color:#ffffff;font-weight:800;">📊 Tagesbericht – {_html.escape(stats.date.strftime("%d.%m.%Y"))}</h1>
  </td></tr>

  <!-- KPI cards -->
  <tr><td style="padding:28px 32px 0;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td width="25%" style="text-align:center;padding:0 6px;">
          <div style="background:#0f172a;border-radius:10px;padding:16px 8px;border:1px solid #334155;">
            <div style="font-size:28px;font-weight:900;color:#4ade80;">{stats.unique_visitors}</div>
            <div style="font-size:11px;color:#9ca3af;margin-top:4px;text-transform:uppercase;letter-spacing:0.5px;">Besucher</div>
            <div style="font-size:11px;color:#16a34a;margin-top:3px;font-weight:700;">{visitor_trend}</div>
          </div>
        </td>
        <td width="25%" style="text-align:center;padding:0 6px;">
          <div style="background:#0f172a;border-radius:10px;padding:16px 8px;border:1px solid #334155;">
            <div style="font-size:28px;font-weight:900;color:#60a5fa;">{stats.total_sessions}</div>
            <div style="font-size:11px;color:#9ca3af;margin-top:4px;text-transform:uppercase;letter-spacing:0.5px;">Sitzungen</div>
          </div>
        </td>
        <td width="25%" style="text-align:center;padding:0 6px;">
          <div style="background:#0f172a;border-radius:10px;padding:16px 8px;border:1px solid #334155;">
            <div style="font-size:28px;font-weight:900;color:#f59e0b;">{stats.total_pageviews}</div>
            <div style="font-size:11px;color:#9ca3af;margin-top:4px;text-transform:uppercase;letter-spacing:0.5px;">Seitenaufrufe</div>
          </div>
        </td>
        <td width="25%" style="text-align:center;padding:0 6px;">
          <div style="background:#0f172a;border-radius:10px;padding:16px 8px;border:1px solid #334155;">
            <div style="font-size:18px;font-weight:900;color:#e879f9;">{_fmt_duration(stats.avg_session_seconds)}</div>
            <div style="font-size:11px;color:#9ca3af;margin-top:4px;text-transform:uppercase;letter-spacing:0.5px;">Ø Dauer</div>
          </div>
        </td>
      </tr>
    </table>
  </td></tr>
  {leads_html}

  <!-- History table -->
  <tr><td style="padding:28px 32px;">
    <p style="margin:0 0 12px;font-size:13px;color:#9ca3af;text-transform:uppercase;letter-spacing:1px;font-weight:700;">Verlauf letzte Tage</p>
    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
      <tr style="border-bottom:1px solid #334155;">
        <th style="padding:6px 12px;color:#6b7280;font-size:11px;text-align:left;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Datum</th>
        <th style="padding:6px 12px;color:#6b7280;font-size:11px;text-align:center;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Besucher</th>
        <th style="padding:6px 12px;color:#6b7280;font-size:11px;text-align:center;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Sitzungen</th>
        <th style="padding:6px 12px;color:#6b7280;font-size:11px;text-align:center;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Aufrufe</th>
        <th style="padding:6px 12px;color:#6b7280;font-size:11px;text-align:center;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Ø Dauer</th>
      </tr>
      {history_rows}
    </table>
    {'<p style="margin:12px 0 0;font-size:12px;color:#6b7280;font-style:italic;">Erster Tagesbericht – noch keine Vergleichsdaten vorhanden.</p>' if not history else ''}
  </td></tr>

  <!-- Footer -->
  <tr><td style="padding:20px 32px;border-top:1px solid #334155;">
    <p style="margin:0;font-size:12px;color:#6b7280;text-align:center;">
      Rümpelwerk Mitteldeutschland · Automatischer Tagesbericht · {_html.escape(stats.date.strftime("%d.%m.%Y"))}
    </p>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>'''

    text_body = (
        f"Tagesbericht {stats.date.strftime('%d.%m.%Y')}\n\n"
        f"Besucher:        {stats.unique_visitors}\n"
        f"Sitzungen:       {stats.total_sessions}\n"
        f"Seitenaufrufe:   {stats.total_pageviews}\n"
        f"Ø Sitzungsdauer: {_fmt_duration(stats.avg_session_seconds)}\n\n"
        f"Trend Besucher (vs. Vortag): {visitor_trend}\n\n"
        + leads_text
        + ('Verlauf:\n' + '\n'.join(
            f"  {h.date.strftime('%d.%m.')}: {h.unique_visitors} Besucher, {_fmt_duration(h.avg_session_seconds)}"
            for h in reversed(history)
        ) if history else 'Erster Bericht – noch keine Vergleichsdaten.')
    )

    payload = json.dumps({
        'from': settings.DEFAULT_FROM_EMAIL,
        'to': list(settings.ADMIN_EMAILS),
        'subject': (f'[Rümpelwerk] 📊 Tagesbericht {stats.date.strftime("%d.%m.%Y")} – '
                    f'{stats.unique_visitors} Besucher'
                    + (f' · {leads.get("anfragen", 0) + leads.get("rechner", 0)} Anfragen'
                       if leads else '')
                    + (f' · ⚠ {leads["offen"]} nicht zugestellt'
                       if leads and leads.get('offen') else '')),
        'text': text_body,
        'html': html_body,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.resend.com/emails',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Ruempelwerk-Website/1.0',
        },
    )
    try:
        with _absenden(req, timeout=10) as resp:
            logger.info(f'Daily-Report gesendet | {stats.date} | {stats.unique_visitors} Besucher | status={resp.status}')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        logger.error(f'Daily-Report HTTP-Fehler | status={e.code} | response={body}')
    except Exception as e:
        logger.error(f'Daily-Report Versand fehlgeschlagen | {type(e).__name__}: {e}')


# ─────────────────────────────────────────────────────────────────────────────
