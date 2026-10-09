"""Wurzel-Routen: Verwaltung, robots/llms/Sitemaps, Statistik, dann die Website.

Die Reihenfolge ist tragend — alles mit einem einzigen Pfadsegment muss vor
``apps.core.urls`` stehen, dessen letztes Pattern ein Catch-All ist.
"""

from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from apps.core.sitemaps import (
    MainSitemap, JobsSitemap, CitySitemap, ServiceSitemap, MatrixSitemap,
    RatgeberSitemap, AktuellesSitemap, ImageSitemap, image_sitemap, sitemap_index,
)
from apps.core.telegram_webhook import webhook as telegram_webhook
from apps.core.data.feste_dateien import FESTE_DATEIEN
from apps.core.views import (
    robots_txt, favicon_ico, feste_datei, security_txt, llms_txt, llms_full_txt, indexnow_key,
)

sitemaps = {
    'main':     MainSitemap,
    'services': ServiceSitemap,
    'matrix':   MatrixSitemap,
    # Der Ratgeber (T4, 16.09.2026) - eigene Datei, eigene Indexierungsquote.
    'ratgeber': RatgeberSitemap,
    # GBP-Beitraege Stufe 1 (Bauplan §7) - eigene Datei, eigene
    # Indexierungsquote, leer solange kein importierter Beitrag alle drei
    # Bedingungen erfuellt (siehe AktuellesSitemap-Docstring).
    'aktuelles': AktuellesSitemap,
    'jobs':     JobsSitemap,
    'cities':   CitySitemap,
    # Bildsitemap (D5, 06.09.2026). Sie steht hier und nicht nur an ihrer
    # eigenen Route, weil DREI Stellen diese Registrierung lesen: der
    # Sitemap-Index, die 'Sitemap:'-Zeilen in robots.txt (views.robots_txt)
    # und die Seitenliste von check_seo/indexnow. Genau daran ist es schon
    # einmal schiefgegangen - sitemap-services.xml stand im Index, in
    # robots.txt aber nicht, weil dort ein handgepflegter Tupel stand.
    #
    # Ausgeliefert wird sie trotzdem von der eigenen Route weiter unten:
    # Djangos Sammel-View kennt nur EIN Template, und in sitemap.xml gibt es
    # keinen image:-Namensraum. Meldet ImageSitemap.items() eine leere Liste,
    # faellt der Abschnitt aus Index und robots.txt heraus
    # (sitemaps.aktive_abschnitte) und antwortet unter seiner Adresse mit 404.
    #
    # Seit TS19 (06.09.2026) nennt sie neben den freigegebenen Galeriebildern
    # die festen Fotos aus apps/core/data/bilder.py - die liegen im
    # Repository, der leere Fall tritt also nur noch nach einem
    # unvollstaendigen collectstatic ein.
    'images':   ImageSitemap,
}

urlpatterns = [
    # Der Pfad kommt aus der Umgebung (B2, 06.09.2026). Der Vorgabewert war
    # bis zum 10.09.2026 'admin' und ist es seit SI14 nicht mehr: Die
    # Umgebungsvariable wurde nie gesetzt, und /admin/ stand vier Tage spaeter
    # noch genauso offen wie vorher. Die Begruendung samt der beiden Warnungen
    # steht in config/settings.py.
    #
    # Ein geheimer Pfad ist KEINE Sicherheitsmassnahme, sondern
    # Laermreduktion: Er haelt die Scanner fern, die blind '/admin/'
    # abklopfen. Das Passwort und die axes-Sperre bleiben unveraendert
    # zustaendig.
    #
    # In robots.txt wird der neue Pfad BEWUSST NICHT genannt - dieselbe
    # Ueberlegung wie bei STATS_PATH: Eine Disallow-Zeile verbietet zwar das
    # Crawlen, macht den Pfad aber oeffentlich lesbar. robots.txt ist die
    # erste Datei, die jeder Scanner abruft. Gegen Indexierung traegt Djangos
    # eigenes Admin-Template, das '<meta name="robots" content="NONE,NOARCHIVE">'
    # mitliefert.
    path(f'{settings.ADMIN_PATH}/', admin.site.urls),
    path('robots.txt', robots_txt, name='robots_txt'),
    # Standardpfade, die Crawler blind abfragen - liefen bisher auf 404.
    path('favicon.ico', favicon_ico, name='favicon_ico'),
    # Favicon, Apple-Touch-Icon, Vorschaubild und Logo zusaetzlich unter einer
    # festen Adresse ohne Hash (SEO-Audit 25.09.2026, K1/K2) - fremde Systeme
    # merken sich die Adresse. Die Liste steht in data/feste_dateien.py.
    *[path(datei, feste_datei, {'datei': datei}, name=f'feste_datei_{i}')
      for i, datei in enumerate(FESTE_DATEIEN) if datei != 'favicon.ico'],
    path('llms.txt', llms_txt, name='llms_txt'),
    # Die Langfassung (G7). Sie MUSS vor dem IndexNow-Muster weiter unten
    # stehen: 'llms-full' besteht ausschliesslich aus [A-Za-z0-9-] und ist
    # neun Zeichen lang - das Muster wuerde sie verschlucken und die Datei
    # als IndexNow-Schluessel behandeln. Genau davor warnt der Kommentar
    # dort, und dies ist der erste Fall, auf den er zutrifft.
    path('llms-full.txt', llms_full_txt, name='llms_full_txt'),
    path('.well-known/security.txt', security_txt, name='security_txt'),
    # IndexNow-Nachweisdatei. Muss auf der WURZEL liegen, nicht unter einem
    # Unterpfad - sonst gilt der Nachweis nur fuer diesen Pfad.
    #
    # Das Muster ist auf den erlaubten Zeichenvorrat eines IndexNow-Schluessels
    # begrenzt (8-128 aus [A-Za-z0-9-]). Ein offenes '<str:key>.txt' haette
    # JEDE kuenftige .txt-Route verschluckt, die nach dieser Zeile steht.
    re_path(r'^(?P<key>[A-Za-z0-9-]{8,128})\.txt$', indexnow_key,
            name='indexnow_key'),
    # Segmentiert (F10): Die GSC zeigt Indexierungsquoten pro Sitemap. Mit
    # einer flachen Datei sieht man nur eine Gesamtzahl - ab Block 2 mit ~50
    # zusaetzlichen URLs ist das nicht mehr auswertbar.
    #
    # Der Index kommt aus apps/core/sitemaps.py, nicht aus Django: Djangos
    # Index-View baut die Adressen aus dem Request-Host und wuerde auf einer
    # Railway-Preview-URL die falsche Domain ausliefern.
    path('sitemap.xml', sitemap_index, {'sitemaps': sitemaps},
         name='sitemap'),
    # MUSS vor der Sammelroute stehen (D5). 'sitemap-images.xml' passt auch
    # auf 'sitemap-<section>.xml'; wer die beiden Zeilen tauscht, bekommt die
    # Bildsitemap mit dem Standardtemplate ausgeliefert - gueltiges XML, aber
    # ohne ein einziges <image:image>. Der Ausfall ist still, die Datei sieht
    # richtig aus und enthaelt genau eine URL.
    path('sitemap-images.xml', image_sitemap, name='sitemap_images'),
    # Eigenes Template (TS19, 01.10.2026): wie Djangos sitemap.xml, aber mit
    # image:-Namensraum, damit Stadt-, Leistungs- und Matrixseiten ihr Foto im
    # eigenen <url>-Eintrag tragen (sitemaps.MitBildern).
    path('sitemap-<section>.xml', sitemap,
         {'sitemaps': sitemaps, 'template_name': 'sitemap_mit_bildern.xml'},
         name='django.contrib.sitemaps.views.sitemap'),
    # Telegram-Webhook (24.09.2026, apps/core/telegram_webhook.py). Der
    # zweite Teil ist geheim und kommt aus TELEGRAM_WEBHOOK_PFAD; die View
    # vergleicht ihn selbst und antwortet ohne Umgebungswert mit 404. Nicht
    # in der Sitemap, nicht in robots.txt (dieselbe Ueberlegung wie bei
    # ADMIN_PATH). Zwei Segmente, also ohnehin am Catch-All vorbei - steht
    # trotzdem VOR dem core-include, wie alles Nicht-Oeffentliche.
    path('telegram/<str:pfad>/', telegram_webhook, name='telegram_webhook'),
    # Geheime Statistikseite – VOR core-include, damit der City-Catch-All nicht greift
    path(f'{settings.STATS_PATH}/', include('apps.stats.urls')),
    # accounts/ und dashboard/ stehen VOR dem core-include, nicht dahinter.
    #
    # Der Grund ist derselbe wie bei STATS_PATH darueber: Das letzte Pattern in
    # apps/core/urls.py ist path('<slug:city_slug>/') und damit ein Catch-All
    # ueber JEDES einsegmentige Verzeichnis (Regel 5).
    #
    # '/accounts/login/' hat das ueberlebt, weil es ZWEI Segmente hat und der
    # Catch-All nur eines frisst. '/dashboard/' hat genau eines - es landete
    # deshalb bis zum 06.09.2026 in city_landing_page mit
    # city_slug='dashboard' und damit auf einer 404. Nachgewiesen mit
    # django.urls.resolve, nicht vermutet.
    #
    # Das war nicht folgenlos: settings.LOGIN_REDIRECT_URL zeigt auf
    # '/dashboard/'. **Jede erfolgreiche Anmeldung ueber /accounts/login/
    # endete auf einer 404-Seite.** Aufgefallen ist es niemandem, weil der
    # Bereich Altbestand ist und niemand sich dort anmeldet - genau die Sorte
    # Fehler, die jahrelang liegen bleibt.
    path('accounts/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('', include('apps.core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'apps.core.views.error_404'
handler500 = 'apps.core.views.error_500'
