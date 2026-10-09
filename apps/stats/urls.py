from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [
    path('',        views.stats_login,  name='login'),
    path('data/',   views.stats_view,   name='data'),
    path('logout/', views.stats_logout, name='logout'),
    path('aktuelles/',                                    views.cms_list,        name='cms_list'),
    path('aktuelles/neu/',                                views.cms_create,      name='cms_create'),
    path('aktuelles/<int:pk>/',                           views.cms_edit,        name='cms_edit'),
    path('aktuelles/<int:pk>/del/',                       views.cms_delete,      name='cms_delete'),
    path('aktuelles/<int:post_pk>/bild/<int:bild_pk>/del/', views.cms_delete_bild, name='cms_delete_bild'),
    path('anfragen/',                                     views.anfragen_list,   name='anfragen_list'),
    path('fehler/',                                       views.fehler_list,     name='fehler_list'),
    path('fehler/<int:pk>/erledigt/',                     views.fehler_erledigt, name='fehler_erledigt'),
    # Terminbuchung (Bauplan §5): Wochenvorlage, Sperren, Statuspflege.
    path('termine/',                                      views.termine_uebersicht,   name='termine_uebersicht'),
    path('termine/vorlage/',                              views.termine_vorlage_speichern, name='termine_vorlage_speichern'),
    path('termine/sperre/neu/',                           views.termine_sperre_anlegen,   name='termine_sperre_anlegen'),
    path('termine/sperre/<int:pk>/del/',                  views.termine_sperre_loeschen,  name='termine_sperre_loeschen'),
    path('termine/<int:pk>/status/',                      views.termine_status_setzen,    name='termine_status_setzen'),
]
