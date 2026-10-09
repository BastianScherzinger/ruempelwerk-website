"""Django-Verwaltung der öffentlichen Website: Leads, Bewerbungen, Besuche.

Erreichbar unter ``settings.ADMIN_PATH`` (siehe ``config/urls.py``).
"""

from django.contrib import admin
from .models import (
    Anfrage, Besichtigungstermin, Bewerbung, Kooperationsanfrage, PageVisit,
    PreisAngebot, Terminsperre, Terminvorlage, TelegramEmpfaenger,
)

# ``mail_gewollt`` und ``mail_gesendet`` stehen bei jedem Formularmodell in
# der Liste und als Filter (P8/C1 und C3). Das ist kein Zierrat: Die beiden
# Felder sind der einzige sichtbare Beleg dafuer, ob zu einem Lead ueberhaupt
# eine Benachrichtigung hinausgegangen ist.
#
# * ``mail_gewollt=False`` heisst: bewusst keine - Duplikat oder erschoepftes
#   Mail-Budget.
# * ``mail_gewollt=True`` und ``mail_gesendet=False`` bei einem Datensatz, der
#   aelter ist als ein paar Stunden, heisst: **der Nachzuegler hat es
#   aufgegeben** (aelter als sieben Tage, siehe ``views._NACHZUEGLER_MAX_TAGE``
#   oder Resend nimmt den Request dauerhaft nicht an). Genau dieser Filter ist
#   der Weg, so etwas zu finden - vorher gab es keinen.
_VERSAND_SPALTEN = ('mail_gewollt', 'mail_gesendet')


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ('path', 'ip_address', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('path', 'ip_address')
    readonly_fields = ('path', 'ip_address', 'user_agent', 'timestamp')


@admin.register(Anfrage)
class AnfrageAdmin(admin.ModelAdmin):
    list_display = ('name', 'leistung', 'email', 'telefon', 'erstellt_am') + _VERSAND_SPALTEN
    list_filter = ('leistung', 'erstellt_am') + _VERSAND_SPALTEN
    search_fields = ('name', 'email', 'adresse')
    readonly_fields = ('erstellt_am',)


@admin.register(PreisAngebot)
class PreisAngebotAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'leistung_label', 'pmin', 'pmax', 'erstellt_am', 'erinnerung_gesendet') + _VERSAND_SPALTEN
    list_filter = ('erinnerung_gesendet', 'erstellt_am') + _VERSAND_SPALTEN
    search_fields = ('name', 'email', 'leistung_label')
    readonly_fields = ('erstellt_am',)
    list_editable = ('erinnerung_gesendet',)


@admin.register(Kooperationsanfrage)
class KooperationsanfrageAdmin(admin.ModelAdmin):
    """Die Kooperationsanfragen standen bis zum 05.09.2026 in keiner Verwaltung.

    Der Mailversand aus ``emails.py`` lief, also erreichte jede Anfrage jemanden -
    aber es gab **keinen zweiten Weg** an die Eintraege. Genau diese Lage hat bei
    einer anderen betreuten Seite fuenf Tage lang jede Kundenanfrage verschluckt,
    weil niemand nachsehen konnte, ob eine Mail angekommen war.
    """

    list_display = ('name', 'firma', 'art', 'email', 'telefon', 'erstellt_am') + _VERSAND_SPALTEN
    list_filter = ('art', 'erstellt_am') + _VERSAND_SPALTEN
    search_fields = ('name', 'firma', 'email', 'nachricht')
    readonly_fields = ('erstellt_am',)


@admin.register(Bewerbung)
class BewerbungAdmin(admin.ModelAdmin):
    """Bewerbungen gab es bis zum 06.09.2026 ueberhaupt nur als E-Mail (P8/C2).

    Fiel der Versand aus - kein ``RESEND_API_KEY``, erschoepftes Mail-Budget,
    ein Thread, den der naechste Deploy abgeschnitten hat -, war die Bewerbung
    weg. Diese Liste ist der zweite Weg, den ``Anfrage``, ``PreisAngebot`` und
    ``Kooperationsanfrage`` seit jeher haben.

    ``stelle_anzeige`` statt ``stelle``: In der Spalte steht der Stellentitel,
    nicht der Slug - und bei einer frei eingegebenen Wunschposition (von
    ``/jobs/``) steht dort woertlich, was der Bewerber geschrieben hat.

    **Aufbewahrung: sechs Monate** nach Paragraph 26 BDSG / Paragraph 15 AGG,
    so wie es der Abschnitt "Bewerbungen" der Datenschutzerklaerung zusagt.
    Eingehalten wird die Frist von ``leads_aufraeumen``, nicht von dieser
    Ansicht.
    """

    list_display = ('name', 'stelle_anzeige', 'email', 'telefon',
                    'erstellt_am') + _VERSAND_SPALTEN
    list_filter = ('stelle', 'erstellt_am') + _VERSAND_SPALTEN
    search_fields = ('name', 'email', 'stelle', 'nachricht')
    readonly_fields = ('erstellt_am',)

    @admin.display(description='Stelle', ordering='stelle')
    def stelle_anzeige(self, obj):
        return obj.stelle_anzeige()


@admin.register(TelegramEmpfaenger)
class TelegramEmpfaengerAdmin(admin.ModelAdmin):
    """Selbst angemeldete Telegram-Handys (``telegram_webhook.py``).

    Hier - und nur hier - laesst sich ein Empfaenger von Hand abmelden
    (``aktiv`` aus), etwa wenn ein Einladungslink in falsche Haende geraten
    ist. Anlegen nicht: Eine Chat-ID von Hand gehoert in ``TELEGRAM_CHAT_IDS``.
    """
    list_display = ('name', 'chat_id', 'angemeldet_am', 'aktiv')
    list_filter = ('aktiv',)
    list_editable = ('aktiv',)
    readonly_fields = ('chat_id', 'name', 'angemeldet_am')


@admin.register(Besichtigungstermin)
class BesichtigungsterminAdmin(admin.ModelAdmin):
    """Terminanfragen (Bauplan §5) - die Wochenvorlage pflegt sich unter
    ``STATS_PATH/termine/``, hier steht nur der Datensatz selbst."""
    list_display = ('name', 'beginn', 'besichtigungsart', 'objektart', 'status',
                    'telefon', 'erstellt_am') + _VERSAND_SPALTEN
    list_filter = ('status', 'besichtigungsart', 'objektart',
                   'erstellt_am') + _VERSAND_SPALTEN
    search_fields = ('name', 'email', 'telefon', 'adresse')
    readonly_fields = ('erstellt_am',)
    list_editable = ('status',)


@admin.register(Terminvorlage)
class TerminvorlageAdmin(admin.ModelAdmin):
    list_display = ('get_wochentag_display', 'uhrzeiten', 'slotlaenge', 'aktiv')
    list_editable = ('aktiv',)


@admin.register(Terminsperre)
class TerminsperreAdmin(admin.ModelAdmin):
    list_display = ('datum', 'uhrzeit', 'grund')
    list_filter = ('datum',)

    def has_add_permission(self, request):
        return False
