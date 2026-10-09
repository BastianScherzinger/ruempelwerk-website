"""Routen der öffentlichen Website.

Leistungs- und Matrixseiten werden aus den Daten erzeugt; der Stadt-Catch-All
``path('<slug:city_slug>/')`` bleibt das letzte Pattern (Regel 5).
"""

from django.urls import path
from . import views
from .feeds import AktuellesFeed, RatgeberFeed
from .data.ratgeber import _RATGEBER_DATA
from .data.services import _SERVICE_DATA
from .data.matrix import matrix_kombinationen

app_name = 'core'

# Leistungsseiten (Block 2). Erzeugt aus _SERVICE_DATA, damit eine neue Leistung
# genau eine Stelle braucht - und damit die Routen strukturell VOR dem Catch-All
# stehen: Sie werden unten zwischen die festen Pfade und
# path('<slug:city_slug>/') gehaengt. Eine von Hand nachgetragene Route landet
# sonst irgendwann darunter und wird von der Stadt-Logik gekapert (301/410/404).
_SERVICE_PATTERNS = [
    path(f'{slug}/', views.service_page, {'service_slug': slug},
         name=f'service_{slug}')
    for slug in _SERVICE_DATA
]

# Leistung x Stadt (A13, Charge 1). Zwei Segmente - sie koennen dem
# einsegmentigen Catch-All nicht in die Quere kommen. Trotzdem stehen sie aus
# demselben Grund wie die Leistungsseiten strukturell davor und werden aus den
# Daten erzeugt: Eine von Hand nachgetragene Route waere die erste, die beim
# naechsten Umbau an der falschen Stelle landet.
_MATRIX_PATTERNS = [
    path(f'{l_slug}/{s_slug}/', views.matrix_page,
         {'service_slug': l_slug, 'city_slug': s_slug},
         name=f'matrix_{l_slug}_{s_slug}')
    for l_slug, s_slug in matrix_kombinationen()
]

# Ratgeberartikel (T4). Aus den Daten erzeugt wie die Leistungsseiten - zwei
# Segmente, also ohne Konflikt mit dem Catch-All, aber aus demselben Grund
# nicht von Hand eingetragen. Ein unbekannter Slug ist damit eine 404, ohne
# dass die View ihn pruefen muss.
_RATGEBER_PATTERNS = [
    path(f'ratgeber/{slug}/', views.ratgeber_artikel, {'artikel_slug': slug},
         name=f'ratgeber_{slug}')
    for slug in _RATGEBER_DATA
]

urlpatterns = [
    path('', views.home, name='home'),
    path('dienstleistungen/', views.dienstleistungen, name='dienstleistungen'),
    path('ueber-uns/', views.ueber_uns, name='ueber_uns'),
    path('kontakt/', views.kontakt, name='kontakt'),
    path('anfrage/', views.anfrage, name='anfrage'),
    # Terminbuchung (Bauplan §5) - VOR dem Catch-All wie jede andere Route.
    path('termin/', views.termin, name='termin'),
    path('leistungen/', views.leistungen, name='leistungen'),
    path('impressum/', views.impressum, name='impressum'),
    path('datenschutz/', views.datenschutz, name='datenschutz'),
    path('agb/', views.agb, name='agb'),
    path('barrierefreiheit/', views.barrierefreiheit, name='barrierefreiheit'),
    path('standorte/', views.standorte, name='standorte'),
    path('preisangebot/', views.preisangebot, name='preisangebot'),
    # Hub VOR dem Stadt-Pattern und weit vor dem Catch-All: /entrumpelung/
    # lief bisher in path('<slug:city_slug>/') und endete als 404.
    path('entrumpelung/', views.entrumpelung_hub, name='entrumpelung_hub'),
    path('entrumpelung/<slug:city_slug>/', views.city_page, name='city_page'),
    path('kooperationspartner/', views.kooperation, name='kooperation'),
    path('jobs/', views.jobs, name='jobs'),
    path('jobs/<slug:job_slug>/', views.job_detail, name='job_detail'),
    path('aktuelles/', views.aktuelles, name='aktuelles'),
    # RSS der CMS-Beitraege (GE32), verlinkt im Kopf jeder Seite (rw_seo.html).
    path('aktuelles/feed/', AktuellesFeed(), name='aktuelles_feed'),
    # Einzelseite eines importierten GBP-Beitrags (Bauplan §7) - VOR dem
    # Catch-All wie jede andere Route, und vor allem VOR /aktuelles/<x>/, das
    # es nicht gibt (die Liste blaettert ueber ?seite=, keinen Pfad).
    path('aktuelles/<int:jahr>/<slug:slug>/', views.aktuelles_beitrag,
         name='aktuelles_beitrag'),
    path('galerie/', views.galerie, name='galerie'),
    path('ratgeber/', views.ratgeber_hub, name='ratgeber'),
    # RSS der Ratgeberartikel - der Feed, den doku/80-AUFGABEN.md unter
    # "Fehlt" fuehrte; verlinkt im Kopf jeder Seite (rw_seo.html).
    path('ratgeber/feed/', RatgeberFeed(), name='ratgeber_feed'),
    # Betrieb (17.09.2026): Gesundheitsadresse (BT11) und die uebliche
    # Feed-Adresse als 301 auf den Ratgeber-Feed (BT06). Beide VOR dem Catch-All.
    path('health/', views.health, name='health'),
    path('feed/', views.feed_weiterleitung, name='feed'),
] + _RATGEBER_PATTERNS + _SERVICE_PATTERNS + _MATRIX_PATTERNS + [
    # City landing pages – MUST be last (catch-all slug)
    path('<slug:city_slug>/', views.city_landing_page, name='city_landing'),
]
