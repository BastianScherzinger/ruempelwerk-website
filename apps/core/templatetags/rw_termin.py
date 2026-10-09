"""``{% rw_termin %}`` und ``{% rw_termin_kurz %}`` - die Terminbuchung (§5).

Zwei Inclusion-Tags: ``/termin/`` bindet die volle Komponente ein
(``components/rw_termin.html``, Tagesleiste, Uhrzeit-Chips + Formular), die
Stadtseiten nur den kurzen Verweisblock (``components/rw_termin_kurz.html``,
Link auf ``/termin/``; Bauplan §4: "Termin-Kurzblock, nicht das ganze Raster").
Seit 02.10.2026 steht der Kalender nicht mehr auf der Startseite (
Hinweis des Werbepartners 11880) - dort führen Hero, Navigation und
Laufband auf ``/termin/``.

Ein Inclusion-Tag rendert sein Template mit einem NEUEN, isolierten Context -
Stammdaten wie ``FIRMA_TELEFON`` kommen deshalb hier ausdruecklich aus
``data.firma.context()``, nicht aus dem Context-Processor der Seite (der
in diesem isolierten Rendering nicht greift). Aus demselben Grund braucht
``rw_termin`` ``takes_context=True``: Ohne das sieht die Komponente die
Erfolgs-/Fehlermeldungen aus ``django.contrib.messages`` nie - die Vorlage
zeigt dann nach einer Terminanfrage einfach nichts an, obwohl der View
``messages.success(...)`` gesetzt hat.
"""

from django import template

from .. import termine
from ..data import firma, zusagen
from ..forms import TerminForm

register = template.Library()


def _basis_context(als_h1, form):
    kal = termine.kalender()
    ctx = {
        'wochen': kal['tage'],
        'erster_frei': kal['erster_frei'],
        'feiertage_zu': kal['geschlossen'],
        'hat_nicht_frei': any(not sl['frei'] for t in kal['tage'] for sl in t['slots']),
        'form': form or TerminForm(),
        'als_h1': als_h1,
        'slot_dauer': termine.SLOT_DAUER_MINUTEN,
        # Regel 24: die Dauer kommt aus zusagen.py, nicht als getippte Zahl
        # aus termine.py - test_termine.py haelt beide Quellen zusammen.
        'ZUSAGE_BESICHTIGUNG_DAUER': zusagen.BESICHTIGUNG_DAUER,
        'ZUSAGE_ANTWORT_SPANNE': zusagen.ANTWORT,
        'ZUSAGE_ANGEBOT': zusagen.ANGEBOT_BEI_BESICHTIGUNG,
        # Seit 01.10.2026 (Regel 24): "ab morgen" und das Video-Angebot aus zusagen.py.
        'ZUSAGE_TERMIN_FRUEHESTENS': zusagen.TERMIN_FRUEHESTENS,
        'ZUSAGE_ANGEBOT_VIDEO': zusagen.ANGEBOT_NACH_VIDEO,
    }
    ctx.update(firma.context())
    return ctx


@register.inclusion_tag('components/rw_termin.html', takes_context=True)
def rw_termin(context, als_h1=False, form=None):
    """Die volle Komponente: Wochenraster, Formular, Oliver-Aside.

    ``als_h1``: True auf der eigenstaendigen Seite ``/termin/`` (dort ist es
    die einzige H1 der Seite); False, wenn die Komponente in eine Seite mit
    eigener H1 eingebunden wird (Startseite) - dann ist die Überschrift eine
    H2, wie in der Vorlage ``f.html`` (``#f-termin``).
    ``form``: ein bereits gebundenes, fehlerbehaftetes ``TerminForm`` nach
    einem gescheiterten POST - sonst ein leeres Formular.

    ``takes_context=True`` NUR um an ``context['messages']`` heranzukommen -
    die Erfolgs-/Fehlermeldung nach dem POST. Alles andere kommt weiter
    ausdruecklich aus ``_basis_context``/``firma.context()``, damit die
    Komponente unabhaengig vom Context-Processor der einbindenden Seite
    dieselben Werte zeigt.
    """
    ctx = _basis_context(als_h1, form)
    ctx['messages'] = context.get('messages')
    return ctx


@register.inclusion_tag('components/rw_termin_kurz.html')
def rw_termin_kurz():
    """Der Kurzblock fuer Stadtseiten: nur ein Verweis auf ``/termin/``."""
    ctx = {'ZUSAGE_BESICHTIGUNG_DAUER': zusagen.BESICHTIGUNG_DAUER,
           'ZUSAGE_TERMIN_FRUEHESTENS': zusagen.TERMIN_FRUEHESTENS}
    ctx.update(firma.context())
    return ctx
