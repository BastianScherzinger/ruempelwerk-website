"""Das interne Dashboard **und** das CMS fuer ``/aktuelles/``, unter ``STATS_PATH``.

Der Zugang laeuft nicht ueber Djangos Auth, sondern ueber ein Passwort aus der
Umgebung und eine eigene Sitzungsmarke. Daraus folgt die wichtigste Regel
dieser Datei: **Jede View prueft ihre Anmeldung selbst.** Es gibt keinen
Dekorator und keine Middleware, die das nachholt - ein vergessenes ``if``
faellt niemandem auf, deshalb prueft ``apps/stats/tests/test_stats.py`` jede
Route einzeln.

Die zweite Sperre ist die Anmeldebremse: zehn Fehlversuche je Stunde und IP,
vierzig je ``/24``, und ohne verwertbare IP je Sitzung. Sie liegt im Cache
(``rw_cache``) und liest die IP ausschliesslich ueber ``client_ip`` (Regel 19)
- hinter Railways Proxy wechselt ``REMOTE_ADDR`` bei jedem Request, ein Limit
darauf zaehlt ewig bis eins.

Die Datei traegt ein UTF-8-BOM.
"""

import hmac
import datetime
import logging
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.cache import cache
from django.db.models import Sum
from django.views.decorators.http import require_http_methods

from apps.core.models import VisitorSession, DailyStats
# Regel 19: IP-Logik immer ueber ``client_ip``. Diese Datei hatte bis zum
# 06.09.2026 eine eigene Kopie - siehe den Block ueber ``_zaehler`` weiter
# unten. ``_subnetz`` traegt einen Unterstrich, wird hier aber bewusst
# mitimportiert statt nachgebaut: Eine zweite /24-Rechnung waere genau der
# Fehler, den dieser Umbau beseitigt. Wer sie in ``antispam.py`` aendert, soll
# sie an EINER Stelle aendern.
from apps.core.antispam import client_ip, _subnetz

logger = logging.getLogger('apps.stats')

_SESSION_KEY = 'stats_ok'
_MAX_ATTEMPTS = 10
_LOCKOUT_SECONDS = 3600  # 1 hour

# Wie viel mehr Fehlversuche ein ganzes /24 haben darf als eine einzelne IP.
# Derselbe Wert wie ``subnetz_faktor`` in ``antispam.rate_limited``.
_SUBNETZ_FAKTOR = 4

# Fehlversuchszaehler in der Sitzung - nur fuer den Fall, dass ``client_ip``
# keine verwertbare Adresse findet. Begruendung im Block darunter.
_SESSION_FAILS = 'stats_login_fails'


def _is_authenticated(request):
    return request.session.get(_SESSION_KEY) is True


# ── Bremse vor der Anmeldung ─────────────────────────────────────────────────
#
# WARUM HIER NICHT ``antispam.rate_limited`` STEHT (entschieden am 06.09.2026)
#
# Der naheliegende Umbau war, die drei Hilfsfunktionen ersatzlos zu streichen
# und ``rate_limited(request, 'stats_login', limit=10, window=3600)`` zu
# nehmen. Weniger Code, eine Quelle. Zwei Unterschiede im Verhalten sprechen
# dagegen, und beide kosten etwas Echtes:
#
# 1. ``rate_limited`` zaehlt **jeden Aufruf**, nicht nur die Fehlversuche. Vor
#    einem Anmeldeformular heisst das: Wer sich zehnmal korrekt anmeldet, ist
#    beim elften Mal ausgesperrt. Das ist dieselbe Fehlerklasse wie das Gewicht
#    ``kein-js`` = +4 vom 01.09.2026 - eine Abwehr, die den Richtigen trifft.
#    Deshalb bleibt der **Fehlversuchs**zaehler; ein erfolgreicher Login raeumt
#    ihn ab (wie ``AXES_RESET_ON_SUCCESS`` fuer den Django-Admin).
# 2. ``rate_limited`` gibt ``False`` zurueck, wenn ``client_ip`` nichts
#    Verwertbares findet ("nicht raten - die Score-Regeln greifen weiter").
#    Vor einem oeffentlichen Formular ist das richtig, vor einer Anmeldung
#    nicht: Dort gibt es keine Score-Regeln, die weiter greifen, sondern nur
#    noch das Passwort. Ohne IP wird deshalb zusaetzlich auf der **Sitzung**
#    gezaehlt.
#
# Uebernommen aus ``rate_limited`` wird alles, was dort richtig ist: die
# Adresse kommt aus ``client_ip`` (Regel 19 - der Envoy-Header zuerst, private
# Netze verworfen), und neben der Einzel-IP laeuft ein zweiter Zaehler auf dem
# ``_subnetz``, damit das Wechseln der letzten Stelle nichts bringt.
#
# WAS DIESE BREMSE NICHT KANN: Wer ohne verwertbare IP kommt UND bei jedem
# Versuch das Sitzungs-Cookie wegwirft, hat keinen Zaehler mehr, auf den er
# faellt. Ein globaler Sammelzaehler fuer den Fall waere moeglich, ist hier
# aber bewusst NICHT eingebaut: Er liesse sich von aussen dauerhaft vollhalten
# und wuerde damit den Betreiber selbst aussperren - ein Angreifer taeuschte
# eine Sperre vor, statt eine zu ueberwinden. In Produktion ist der Fall
# ausserdem keiner: Railways Envoy setzt ``X-Envoy-External-Address`` bei jedem
# Request. Faellt er doch einmal an, steht das als Warnung im Log (siehe
# ``_record_stats_failure``) - dann hat sich am Proxy etwas geaendert, und das
# gehoert gesehen, nicht stillschweigend abgefangen.


def _zaehler(request):
    """Die Cache-Schluessel dieses Requests mit ihrem jeweiligen Limit.

    Leer, wenn ``client_ip`` nichts Verwertbares liefert - dann uebernimmt der
    Sitzungszaehler.
    """
    ip = client_ip(request)
    if not ip:
        return []
    schluessel = [(f'stats_login_fail:{ip}', _MAX_ATTEMPTS)]
    netz = _subnetz(ip)
    if netz:
        schluessel.append(
            (f'stats_login_fail:net:{netz}', _MAX_ATTEMPTS * _SUBNETZ_FAKTOR)
        )
    return schluessel


def _stats_rate_limited(request) -> bool:
    """True, wenn dieser Request die erlaubten Fehlversuche erreicht hat."""
    for key, limit in _zaehler(request):
        if cache.get(key, 0) >= limit:
            return True
    if not client_ip(request):
        return request.session.get(_SESSION_FAILS, 0) >= _MAX_ATTEMPTS
    return False


def _record_stats_failure(request) -> None:
    for key, _limit in _zaehler(request):
        cache.set(key, cache.get(key, 0) + 1, timeout=_LOCKOUT_SECONDS)
    if not client_ip(request):
        request.session[_SESSION_FAILS] = (
            request.session.get(_SESSION_FAILS, 0) + 1
        )
        logger.warning(
            'Stats-Login: keine verwertbare Client-IP - es zaehlt nur die '
            'Sitzung. Hinter Railways Proxy darf das nicht vorkommen.'
        )


def _clear_stats_failures(request) -> None:
    for key, _limit in _zaehler(request):
        cache.delete(key)
    request.session.pop(_SESSION_FAILS, None)


def stats_login(request):
    """Die Anmeldemaske unter ``STATS_PATH`` - mit Bremse gegen Durchprobieren.

    Gezaehlt wird je IP, je ``/24`` und je Sitzung; die Bremse greift **vor**
    dem Passwortvergleich, sonst liesse sie sich mit wechselndem
    ``X-Forwarded-For`` umgehen.
    """
    if _is_authenticated(request):
        return redirect('stats:data')

    error = None
    if request.method == 'POST':
        # Nur noch zum Protokollieren. Gezaehlt wird ueber ``_zaehler``, damit
        # der Subnetz-Schluessel nicht an zwei Stellen gerechnet wird.
        ip = client_ip(request) or 'unbekannt'

        if _stats_rate_limited(request):
            error = 'Zu viele Fehlversuche. Bitte versuchen Sie es später erneut.'
            logger.warning('Stats-Login: Rate-Limit erreicht für IP %s', ip)
            return render(request, 'stats/login.html', {'error': error})

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        expected_user = getattr(settings, 'STATS_USER', '')
        expected_pass = getattr(settings, 'STATS_PASSWORD', '')

        # Reject if env vars not set
        if not expected_user or not expected_pass:
            error = 'Statistik-Zugang ist nicht konfiguriert.'
            logger.warning('Stats-Login: STATS_USER oder STATS_PASSWORD nicht gesetzt')
        else:
            # hmac.compare_digest requires same type; encode to bytes for safety
            ok_u = hmac.compare_digest(
                username.encode('utf-8'), expected_user.encode('utf-8')
            )
            ok_p = hmac.compare_digest(
                password.encode('utf-8'), expected_pass.encode('utf-8')
            )
            if ok_u and ok_p:
                _clear_stats_failures(request)
                request.session.cycle_key()  # prevent session fixation
                request.session[_SESSION_KEY] = True
                request.session.set_expiry(28800)  # 8h
                logger.info('Stats-Login erfolgreich von IP %s', ip)
                return redirect('stats:data')
            else:
                _record_stats_failure(request)
                error = 'Ungültige Zugangsdaten.'
                logger.warning('Stats-Login: Fehlgeschlagener Versuch von IP %s', ip)

    return render(request, 'stats/login.html', {'error': error})


def stats_view(request):
    """Das Dashboard: Besuche, Sitzungen, Leads und die Tageswerte.

    Die Zahlen kommen aus ``VisitorSession`` und ``DailyStats``, nicht aus
    ``PageVisit`` - jenes ist das Crawl-Protokoll und wird nach 30 Tagen
    geleert.
    """
    if not _is_authenticated(request):
        return redirect('stats:login')

    from django.utils.timezone import localdate
    today = localdate()
    yesterday = today - datetime.timedelta(days=1)

    # Live-Stats für heute (aus VisitorSession direkt aggregieren)
    today_sessions = VisitorSession.objects.filter(date=today)
    today_total_s   = today_sessions.count()
    today_visitors  = today_total_s  # Sitzungen = Besuche (IP-Tracking durch Railway-Proxy nicht möglich)
    today_pageviews = today_sessions.aggregate(s=Sum('page_count'))['s'] or 0
    durations = [
        (s.last_seen - s.started_at).total_seconds()
        for s in today_sessions
        if s.last_seen > s.started_at
    ]
    today_avg_sec = int(sum(durations) / len(durations)) if durations else 0

    # Historische Tagesdaten (letzte 30 Tage, ohne heute)
    history = list(DailyStats.objects.filter(date__lte=yesterday).order_by('-date')[:30])

    # Für das Balkendiagramm: max Besucher als Referenz
    all_visitors = [h.unique_visitors for h in history] + [today_visitors]
    max_visitors = max(all_visitors) if all_visitors else 1

    # Trend heute vs. gestern
    yesterday_stats = history[0] if history else None
    def trend(today_val, prev):
        if prev is None or prev == 0:
            return None
        diff = today_val - prev
        return {'diff': diff, 'up': diff >= 0}

    visitor_trend = trend(today_visitors, yesterday_stats.unique_visitors if yesterday_stats else None)

    # Chart-Daten: letzte 14 Tage + heute für Balkendiagramm
    chart_days = list(reversed(history[:13])) + [{
        'date': today, 'unique_visitors': today_visitors,
        'total_sessions': today_total_s, 'total_pageviews': today_pageviews,
        'avg_session_seconds': today_avg_sec, 'is_today': True,
    }]

    def fmt(sec):
        if not sec:
            return '–'
        m, s = divmod(sec, 60)
        return f'{m}:{s:02d} Min'

    # Trend-Pfeile für Tabelle vorberechnen
    history_rows = []
    for i, day in enumerate(history):
        prev = history[i + 1] if i + 1 < len(history) else None
        if prev:
            diff = day.unique_visitors - prev.unique_visitors
            t = '↑' if diff > 0 else ('↓' if diff < 0 else '→')
            t_class = 'up' if diff > 0 else ('down' if diff < 0 else '')
        else:
            t, t_class = '–', ''
        history_rows.append({
            'date':             day.date,
            'unique_visitors':  day.unique_visitors,
            'total_sessions':   day.total_sessions,
            'total_pageviews':  day.total_pageviews,
            'avg_fmt':          fmt(day.avg_session_seconds),
            'trend':            t,
            'trend_class':      t_class,
        })

    context = {
        'today':           today,
        'today_visitors':  today_visitors,
        'today_sessions':  today_total_s,
        'today_pageviews': today_pageviews,
        'today_avg_fmt':   fmt(today_avg_sec),
        'visitor_trend':   visitor_trend,
        'history_rows':    history_rows,
        'chart_days':      chart_days,
        'max_visitors':    max_visitors,
        'stats_path':      getattr(settings, 'STATS_PATH', ''),
        # Seit 24.09.2026: Anfragen, fuer die eine Mail vorgesehen war, die nie
        # hinausging - die eine Zahl, die auf der Startseite stehen muss.
        'offen_nicht_zugestellt': _offen_nicht_zugestellt(),
    }
    return render(request, 'stats/dashboard.html', context)


def _offen_nicht_zugestellt():
    try:
        from apps.core.leads import offen_nicht_zugestellt
        return offen_nicht_zugestellt()
    # audit-ok P02: Das Dashboard soll auch dann laden, wenn die Zaehlung
    # scheitert; der Fehler steht in der Fehlerwache.
    except Exception:
        logger.error('Dashboard: offene Anfragen nicht zaehlbar', exc_info=True)
        return None


@require_http_methods(['POST'])
def stats_logout(request):
    request.session.pop(_SESSION_KEY, None)
    return redirect('stats:login')


import datetime as _dt


def _stats_ctx(extra=None):
    """Base context for all stats/CMS pages."""
    ctx = {'stats_path': getattr(settings, 'STATS_PATH', '')}
    if extra:
        ctx.update(extra)
    return ctx


_WARN_SESSION_KEY = 'cms_warnungen'


def _cms_redirect_mit_warnung(request, post, warnungen):
    """Beitrag ist gespeichert, aber einzelne Bilder fehlen.

    Die Meldung wird ueber die Session an die Liste durchgereicht statt das
    Formular erneut zu rendern: Nach einem POST muss ein Redirect folgen,
    sonst laedt ein Neuladen der Seite den Beitrag ein zweites Mal hoch.
    """
    request.session[_WARN_SESSION_KEY] = warnungen
    return redirect('stats:cms_edit', pk=post.pk)


def cms_list(request):
    """Die Beitragsliste des CMS - Uebersicht, Status und Einstieg zum Bearbeiten."""
    if not _is_authenticated(request):
        return redirect('stats:login')
    from apps.core.models import AktuellesPost, AktuellesBild
    from apps.core.views import _safe_image_url
    raw_posts = list(AktuellesPost.objects.all())

    # Zaehlung getrennt nach Bildtyp. Die Uebersicht zeigte vorher nur
    # post.bild_vor an – ein Alt-Feld des Models, das ueber das CMS gar nicht
    # befuellt wird (Bilder landen als AktuellesBild-Zeilen). Folge: Bei
    # „Vorher/Nachher" stand dort rot „kein Bild", obwohl die Fotos da waren,
    # und bei Bericht/Zitat immer nur ein Strich.
    zaehler = {}
    erstes_bild = {}
    for b in AktuellesBild.objects.filter(post__in=raw_posts).order_by('reihenfolge', 'pk'):
        d = zaehler.setdefault(b.post_id, {'vor': 0, 'nach': 0, 'galerie': 0, 'ohne_text': 0})
        d['vor' if b.typ_bild == 'vor' else 'nach' if b.typ_bild == 'nach' else 'galerie'] += 1
        if not b.bildtext.strip():
            d['ohne_text'] += 1
        erstes_bild.setdefault(b.post_id, b.bild)

    for p in raw_posts:
        d = zaehler.get(p.pk, {'vor': 0, 'nach': 0, 'galerie': 0, 'ohne_text': 0})
        # Zeigt in der Liste, wo der alt-Text noch fehlt. Ohne diesen Hinweis
        # wuerde er nie nachgetragen - beim Hochladen fehlt dafuer die Zeit.
        p.n_ohne_bildtext = d['ohne_text']
        p.n_vor         = d['vor']
        p.n_nach        = d['nach']
        p.n_galerie     = d['galerie']
        p.gallery_count = d['vor'] + d['nach'] + d['galerie']
        # CMS-Liste zeigt nur kleine Vorschauen -> schmale Cloudinary-Variante
        p.thumb_url     = _safe_image_url(erstes_bild.get(p.pk) or p.bild_vor, width=400)
    cloudinary_ok = bool(getattr(settings, 'CLOUDINARY_STORAGE', {}).get('MEDIA_TAG'))
    return render(request, 'stats/cms_list.html', _stats_ctx({
        'posts': raw_posts,
        'cloudinary_ok': cloudinary_ok,
    }))


_MAX_BILD_BYTES = 8 * 1024 * 1024


def _add_bilder(post, new_files, typ_bild, warnungen, basis_text=''):
    """Haengt Bilder an einen Post. Sammelt Probleme in ``warnungen``.

    Frueher wurden zu grosse und fehlgeschlagene Bilder still mit ``continue``
    uebersprungen: Der Beitrag erschien danach, aber ohne Fotos, und niemand
    erfuhr warum. Handyfotos liegen regelmaessig ueber 8 MB – genau der Fall,
    der am haeufigsten auftritt.
    """
    from apps.core.models import AktuellesBild, GALERIE_MAX_BILDER

    if not new_files:
        return
    try:
        existing = AktuellesBild.objects.filter(post=post, typ_bild=typ_bild).count()
    except Exception:
        # Ohne ``typ_bild`` (alte Datenbank, fehlende Migration) zaehlt der
        # Rueckfall alle Bilder des Beitrags - das Bilderlimit greift dann
        # frueher als gedacht. Genau das ist die Beschwerde "ich kann kein
        # Bild mehr hochladen", und sie waere ohne diese Zeile nicht
        # aufzuklaeren.
        logger.warning('Bildzaehlung nach typ_bild nicht moeglich - gezaehlt '
                       'werden alle Bilder von Beitrag %s', post.pk,
                       exc_info=True)
        existing = AktuellesBild.objects.filter(post=post).count()

    frei = max(0, GALERIE_MAX_BILDER - existing)
    if len(new_files) > frei:
        warnungen.append(
            f'Nur {frei} von {len(new_files)} Bildern angenommen – '
            f'pro Beitrag sind maximal {GALERIE_MAX_BILDER} moeglich.'
        )

    for i, gf in enumerate(new_files[:frei]):
        name = getattr(gf, 'name', 'Bild')
        if gf.size > _MAX_BILD_BYTES:
            mb = gf.size / 1024 / 1024
            warnungen.append(f'„{name}" ({mb:.1f} MB) ist groesser als 8 MB und wurde nicht hochgeladen.')
            logger.warning('CMS: Bild %s zu gross (%d Bytes)', name, gf.size)
            continue
        try:
            AktuellesBild.objects.create(
                post=post, bild=gf, typ_bild=typ_bild, reihenfolge=existing + i,
                bildtext=basis_text[:180],
            )
        except Exception as exc:
            warnungen.append(f'„{name}" konnte nicht gespeichert werden: {exc}')
            logger.error('CMS Bild-Fehler (%s, typ=%r): %s', name, typ_bild, exc)


def _save_post(post, files, daten=None):
    """Speichert den Beitrag samt Bildern.

    Rueckgabe: ``(fehler, warnungen)``. ``fehler`` ist ein String und bedeutet,
    dass nichts gespeichert wurde. ``warnungen`` ist eine Liste; der Beitrag ist
    dann gespeichert, aber einzelne Bilder fehlen.
    """
    daten = daten if daten is not None else {}
    warnungen = []
    if not post.titel:
        return 'Titel ist ein Pflichtfeld.', warnungen
    if not post.datum:
        return 'Datum ist ein Pflichtfeld.', warnungen
    try:
        post.full_clean(exclude=['bild_vor', 'bild_nach'])
        post.save()
    except Exception as exc:
        logger.error('CMS Speicherfehler: %s', exc)
        return f'Fehler: {exc}', warnungen

    if post.typ == 'vorher_nachher':
        for typ_bild, field_name in (('vor', 'bilder_vor'), ('nach', 'bilder_nach')):
            _add_bilder(post, files.getlist(field_name), typ_bild, warnungen,
                        basis_text=daten.get('bildtext_neu_' + typ_bild, '').strip())
    else:
        _add_bilder(post, files.getlist('bilder'), '', warnungen,
                    basis_text=daten.get('bildtext_neu', '').strip())

    _speichere_bildtexte(post, daten, warnungen)
    return None, warnungen


def _speichere_bildtexte(post, daten, warnungen):
    """Uebernimmt geaenderte Bildbeschreibungen (Felder ``bildtext_<pk>``).

    Damit laesst sich der alt-Text auch lange nach dem Hochladen nachtragen -
    genau das ist der Normalfall, weil beim Upload meist die Zeit fehlt.
    """
    from apps.core.models import AktuellesBild

    aenderungen = {}
    for schluessel, wert in daten.items():
        if not schluessel.startswith('bildtext_') or schluessel.startswith('bildtext_neu'):
            continue
        try:
            aenderungen[int(schluessel[len('bildtext_'):])] = wert.strip()[:180]
        except ValueError:
            continue
    if not aenderungen:
        return

    # Nur Bilder dieses Beitrags - eine fremde pk im Formular darf nichts
    # veraendern koennen.
    for bild in AktuellesBild.objects.filter(post=post, pk__in=aenderungen):
        neu_text = aenderungen[bild.pk]
        if neu_text != bild.bildtext:
            bild.bildtext = neu_text
            try:
                bild.save(update_fields=['bildtext'])
            except Exception as exc:                              # noqa: BLE001
                # Die Warnung sieht nur, wer gerade speichert - das Protokoll
                # hält den Fall auch danach fest (P02, 17.09.2026).
                logger.warning('CMS: Bildbeschreibung #%s nicht gespeichert: %s',
                               bild.pk, type(exc).__name__)
                warnungen.append('Bildbeschreibung #%s nicht gespeichert: %s' % (bild.pk, exc))


def cms_create(request):
    """Einen neuen Beitrag anlegen - sichtbar erst mit ``veroeffentlicht=True``.

    Zu grosse oder fehlerhafte Bilder werden nicht still uebersprungen, sondern
    als Warnung zurueckgemeldet (``_add_bilder``); Handyfotos liegen
    regelmaessig ueber der Grenze.
    """
    if not _is_authenticated(request):
        return redirect('stats:login')
    from apps.core.models import AktuellesPost
    error = None
    warnungen = []
    # Bei einem Fehler wird das Formular mit den eingegebenen Werten neu
    # gerendert. Vorher stand hier post=None – wer sich beim Datum vertippte,
    # bekam das leere Formular zurueck und musste alles neu schreiben.
    post = None
    if request.method == 'POST':
        post = AktuellesPost(
            typ=request.POST.get('typ', 'bericht'),
            titel=request.POST.get('titel', '').strip()[:300],
            inhalt=request.POST.get('inhalt', '').strip(),
            zitat_autor=request.POST.get('zitat_autor', '').strip()[:200],
            autor=request.POST.get('autor', ''),
            datum=request.POST.get('datum') or _dt.date.today(),
            veroeffentlicht='veroeffentlicht' in request.POST,
        )
        error, warnungen = _save_post(post, request.FILES, request.POST)
        if not error and not warnungen:
            return redirect('stats:cms_list')
        if not error:
            # Gespeichert, aber Bilder fehlen -> Meldung am bestehenden Beitrag
            return _cms_redirect_mit_warnung(request, post, warnungen)
    from apps.core.models import AUTOR_META, GALERIE_MAX_BILDER
    return render(request, 'stats/cms_form.html', _stats_ctx({
        'action': 'Erstellen', 'post': post, 'error': error,
        'warnungen': warnungen,
        'today': _dt.date.today().isoformat(),
        'gallery': [], 'gallery_slots': GALERIE_MAX_BILDER,
        'autor_meta': AUTOR_META,
    }))


def cms_edit(request, pk):
    """Einen Beitrag bearbeiten - Text, Datum, Autor, Bilder, Freigabe.

    Wird ein Beitrag hier veroeffentlicht, aendert sich das ``lastmod`` von
    ``/aktuelles/`` und ``/galerie/`` mit (``sitemaps.lastmod_fuer_pfad``).
    """
    if not _is_authenticated(request):
        return redirect('stats:login')
    from apps.core.models import AktuellesPost
    from django.http import Http404
    try:
        post = AktuellesPost.objects.get(pk=pk)
    except AktuellesPost.DoesNotExist:
        raise Http404
    error = None
    warnungen = []
    if request.method == 'POST':
        post.typ            = request.POST.get('typ', post.typ)
        post.titel          = request.POST.get('titel', '').strip()[:300]
        post.inhalt         = request.POST.get('inhalt', '').strip()
        post.zitat_autor    = request.POST.get('zitat_autor', '').strip()[:200]
        post.autor          = request.POST.get('autor', '')
        post.datum          = request.POST.get('datum') or post.datum
        post.veroeffentlicht = 'veroeffentlicht' in request.POST
        error, warnungen = _save_post(post, request.FILES, request.POST)
        if not error and not warnungen:
            return redirect('stats:cms_list')
        if not error:
            return _cms_redirect_mit_warnung(request, post, warnungen)
    from apps.core.models import AktuellesBild, AUTOR_META, GALERIE_MAX_BILDER
    from apps.core.views import _safe_image_url
    # Warnungen aus einem vorangegangenen Speichervorgang einmalig anzeigen
    warnungen = (warnungen or []) + (request.session.pop(_WARN_SESSION_KEY, None) or [])
    all_bilder = AktuellesBild.objects.filter(post=post)
    # Quadratische Thumbnail-Kacheln im CMS-Formular -> schmale Cloudinary-Variante
    gallery = [(b.pk, _safe_image_url(b.bild, width=400), b.bildtext)
                   for b in all_bilder if not b.typ_bild]
    gallery_vor = [(b.pk, _safe_image_url(b.bild, width=400), b.bildtext)
                   for b in all_bilder if b.typ_bild == 'vor']
    gallery_nach = [(b.pk, _safe_image_url(b.bild, width=400), b.bildtext)
                   for b in all_bilder if b.typ_bild == 'nach']
    return render(request, 'stats/cms_form.html', _stats_ctx({
        'action': 'Bearbeiten', 'post': post, 'error': error,
        'warnungen': warnungen,
        'today': _dt.date.today().isoformat(),
        'gallery': gallery,
        'gallery_vor': gallery_vor,
        'gallery_nach': gallery_nach,
        'gallery_slots': max(0, GALERIE_MAX_BILDER - len(gallery)),
        'autor_meta': AUTOR_META,
    }))


@require_http_methods(['POST'])
def cms_delete(request, pk):
    """Einen Beitrag loeschen - mitsamt seinen Bilddateien.

    Die Dateien verschwinden erst nach dem Commit und nur, wenn kein anderer
    Datensatz sie noch benutzt (``models._loeschen``).
    """
    if not _is_authenticated(request):
        return redirect('stats:login')
    from apps.core.models import AktuellesPost
    try:
        AktuellesPost.objects.filter(pk=pk).delete()
    except Exception:
        # Frueher stand hier ``pass``. Schlaegt das Loeschen fehl - eine
        # Fremdschluessel-Sperre, ein Cloudinary-Zeitausfall beim Aufraeumen
        # der Bilder -, dann landete der Redakteur trotzdem auf der Liste und
        # sah den Beitrag noch stehen, ohne einen Hinweis warum. Der Fehler
        # gehoert ins Protokoll; die Weiterleitung bleibt, damit das CMS bei
        # einem Teilerfolg nicht mit einem 500 antwortet.
        # Das Nachbar-View ``cms_delete_bild`` faengt gar nichts ab - der
        # Block hier war also nie ein Muster, sondern ein Einzelfall.
        logger.exception('CMS: Loeschen von AktuellesPost pk=%s fehlgeschlagen', pk)
    return redirect('stats:cms_list')


@require_http_methods(['POST'])
def cms_delete_bild(request, post_pk, bild_pk):
    if not _is_authenticated(request):
        return redirect('stats:login')
    from apps.core.models import AktuellesBild
    AktuellesBild.objects.filter(pk=bild_pk, post_id=post_pk).delete()
    return redirect('stats:cms_edit', pk=post_pk)


# ── Fehlerwache (VL19, 16.09.2026) ──────────────────────────────────────────

def fehler_list(request):
    """Die Fehler der Website - offene zuerst, erledigte darunter."""
    if not _is_authenticated(request):
        return redirect('stats:login')
    from apps.core.fehlerwache import AUFBEWAHRUNG_TAGE
    from apps.core.models import Fehlerereignis
    alle = list(Fehlerereignis.objects.all()[:200])
    return render(request, 'stats/fehler.html', _stats_ctx({
        'offen': [e for e in alle if not e.erledigt],
        'erledigt': [e for e in alle if e.erledigt],
        'aufbewahrung': AUFBEWAHRUNG_TAGE,
    }))


@require_http_methods(['POST'])
def fehler_erledigt(request, pk):
    """Blendet einen Fehler aus - bis er wiederkommt (``festhalten`` setzt zurueck)."""
    if not _is_authenticated(request):
        return redirect('stats:login')
    from apps.core.models import Fehlerereignis
    Fehlerereignis.objects.filter(pk=pk).update(erledigt=True)
    return redirect('stats:fehler_list')


# ── Anfragen (Paket 1, 24.09.2026) ──────────────────────────────────────────

#: So weit reicht die Liste zurueck.
ANFRAGEN_TAGE = 60


def anfragen_list(request):
    """Alle Leads der letzten 60 Tage aus allen vier Formularen, mit Versandstatus.

    Rot: Mail gewollt, aber nicht gesendet. Markiert: Spamverdacht (Variante A,
    ohne Mail und Push). Dazu je Zeile, ob der Telegram-Push rausging.

    Bis zum 24.09.2026 kannte dieses Dashboard ``Anfrage`` gar nicht - Leads
    sah nur, wer ein Konto in der Django-Verwaltung unter ``ADMIN_PATH`` hatte.
    """
    if not _is_authenticated(request):
        return redirect('stats:login')
    from apps.core import telegram
    from apps.core.leads import liste
    from apps.core.models import TelegramEmpfaenger
    eintraege = liste(ANFRAGEN_TAGE)
    return render(request, 'stats/anfragen.html', _stats_ctx({
        'eintraege': eintraege,
        'tage': ANFRAGEN_TAGE,
        'telegram_aktiv': telegram.aktiv(),
        # Nur lesend (24.09.2026): wer sich per Einladungslink angemeldet hat.
        # Abmelden geht per /stop oder in der Django-Verwaltung.
        'telegram_empfaenger': list(TelegramEmpfaenger.objects.all()),
        'telegram_fest': len(telegram.env_chat_ids()),
        'anzahl_offen': sum(1 for e in eintraege if e['nicht_zugestellt']),
        'anzahl_verdacht': sum(1 for e in eintraege if e['verdacht']),
    }))


# ── Terminbuchung (Bauplan §5, Migration 0022) ──────────────────────────────
#
# Drei Aufgaben unter derselben Route: die Wochenvorlage (welche Uhrzeiten
# sind an welchem Wochentag offen), die Sperren (einzelne Nicht-Zeiten) und
# eine kurze Liste der naechsten Anfragen mit Statuspflege. Die vollstaendige
# Liste ueber alle vier alten Formulare UND Termine steht weiter unter
# ``anfragen/`` (``apps.core.leads.modelle()`` kennt ``Besichtigungstermin``
# seit diesem Bauabschnitt).

#: Wie weit die Anfragenliste auf dieser Seite zurueckreicht.
TERMINE_ANFRAGEN_TAGE = 60


def termine_uebersicht(request):
    """Wochenvorlage an/aus je Uhrzeit, Sperren anlegen/loeschen, Anfragenliste."""
    if not _is_authenticated(request):
        return redirect('stats:login')
    from django.utils import timezone
    from apps.core import termine
    from apps.core.models import Besichtigungstermin, Terminsperre, Terminvorlage

    vorlagen = {v.wochentag: v for v in Terminvorlage.objects.all()}
    wochentage = []
    for wochentag, label in Terminvorlage.WOCHENTAG_CHOICES:
        vorlage = vorlagen.get(wochentag)
        aktive_zeiten = set(vorlage.uhrzeiten) if vorlage else set(termine.SLOT_ZEITEN_STANDARD)
        wochentage.append({
            'wochentag': wochentag,
            'label': label,
            'aktiv': vorlage.aktiv if vorlage else True,
            'zeiten': [{'zeit': z, 'an': z in aktive_zeiten}
                      for z in termine.SLOT_ZEITEN_STANDARD],
        })

    grenze = timezone.now() - datetime.timedelta(days=TERMINE_ANFRAGEN_TAGE)
    anfragen = list(Besichtigungstermin.objects
                    .filter(erstellt_am__gte=grenze)
                    .order_by('-erstellt_am')[:200])

    return render(request, 'stats/termine.html', _stats_ctx({
        'wochentage': wochentage,
        'sperren': list(Terminsperre.objects.all()[:100]),
        'anfragen': anfragen,
        'status_choices': Besichtigungstermin.STATUS_CHOICES,
        'tage': TERMINE_ANFRAGEN_TAGE,
        'fehler': request.session.pop(_TERMINE_FEHLER_KEY, []),
        'vorlage_fehler': request.session.pop(_TERMINE_VORLAGE_FEHLER_KEY, []),
    }))


@require_http_methods(['POST'])
def termine_vorlage_speichern(request):
    """Speichert die Wochenvorlage - ein POST fuer alle Wochentage zugleich.

    Checkbox-Namen ``zeit_<wochentag>_<HH-MM>``; ein fehlendes Kaestchen
    heisst "aus". ``aktiv_<wochentag>`` schaltet den ganzen Tag.
    """
    if not _is_authenticated(request):
        return redirect('stats:login')
    from django.db import transaction

    from apps.core import termine
    from apps.core.models import Terminvorlage

    from .forms import TerminvorlageForm

    form = TerminvorlageForm(
        request.POST, [w for w, _l in Terminvorlage.WOCHENTAG_CHOICES],
        termine.SLOT_ZEITEN_STANDARD)
    if not form.is_valid():
        # Nichts speichern, Grund ueber die Session anzeigen (Post/Redirect/Get).
        request.session[_TERMINE_VORLAGE_FEHLER_KEY] = [
            str(f) for fehler in form.errors.values() for f in fehler]
        return redirect('stats:termine_uebersicht')
    with transaction.atomic():
        for wochentag, tag in form.tage.items():
            Terminvorlage.objects.update_or_create(
                wochentag=wochentag,
                defaults={'uhrzeiten': tag['uhrzeiten'], 'aktiv': tag['aktiv'],
                          'slotlaenge': termine.SLOT_DAUER_MINUTEN},
            )
    return redirect('stats:termine_uebersicht')


_TERMINE_VORLAGE_FEHLER_KEY = 'termine_vorlage_fehler'


_TERMINE_FEHLER_KEY = 'termine_fehler'


@require_http_methods(['POST'])
def termine_sperre_anlegen(request):
    """Legt eine neue Sperre an - Datum Pflicht, Uhrzeit leer = ganzer Tag."""
    if not _is_authenticated(request):
        return redirect('stats:login')
    from apps.core.models import Terminsperre

    from .forms import TerminsperreForm

    form = TerminsperreForm(request.POST)
    if not form.is_valid():
        # Fehler ueber die Session an die Uebersicht reichen (Post/Redirect/Get).
        request.session[_TERMINE_FEHLER_KEY] = [
            str(f) for fehler in form.errors.values() for f in fehler]
        return redirect('stats:termine_uebersicht')
    d = form.cleaned_data
    Terminsperre.objects.get_or_create(
        datum=d['datum'], uhrzeit=d['uhrzeit'] or None, defaults={'grund': d['grund']})
    return redirect('stats:termine_uebersicht')


@require_http_methods(['POST'])
def termine_sperre_loeschen(request, pk):
    if not _is_authenticated(request):
        return redirect('stats:login')
    from apps.core.models import Terminsperre
    Terminsperre.objects.filter(pk=pk).delete()
    return redirect('stats:termine_uebersicht')


@require_http_methods(['POST'])
def termine_status_setzen(request, pk):
    """Setzt den Status einer Terminanfrage (angefragt/bestaetigt/abgesagt)."""
    if not _is_authenticated(request):
        return redirect('stats:login')
    from apps.core.models import Besichtigungstermin
    status = request.POST.get('status', '')
    if status in dict(Besichtigungstermin.STATUS_CHOICES):
        Besichtigungstermin.objects.filter(pk=pk).update(status=status)
    return redirect('stats:termine_uebersicht')
