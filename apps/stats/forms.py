"""Formulare des internen Dashboards (nur angemeldet erreichbar)."""

from django import forms


class TerminsperreForm(forms.Form):
    """Eine neue Terminsperre: Datum Pflicht, Uhrzeit leer = ganzer Tag.

    Vorher gingen ``datum``/``uhrzeit`` ungeprueft in ``get_or_create``; ein
    ungueltiger Wert endete in einer verschluckten Ausnahme und der Nutzer sah
    nichts. Jetzt kommt eine Fehlermeldung zurueck, die die Seite anzeigt.
    """

    datum = forms.DateField(
        input_formats=['%Y-%m-%d', '%d.%m.%Y'],
        error_messages={'required': 'Bitte ein Datum angeben.',
                        'invalid': 'Das Datum ist ungültig (Format TT.MM.JJJJ).'})
    uhrzeit = forms.TimeField(
        required=False, input_formats=['%H:%M', '%H:%M:%S'],
        error_messages={'invalid': 'Die Uhrzeit ist ungültig (Format HH:MM).'})
    grund = forms.CharField(
        required=False, max_length=200,
        error_messages={'max_length': 'Der Grund darf höchstens 200 Zeichen lang sein.'})

    def clean_grund(self):
        return (self.cleaned_data.get('grund') or '').strip()


class TerminvorlageForm(forms.Form):
    """Die Wochenvorlage: pro Wochentag ``aktiv_<tag>`` und ``zeit_<tag>_<HH-MM>``.

    Ein Kaestchen steht fuer "an", ein fehlendes fuer "aus" - so schickt es der
    Browser. Geprueft wird, was ein Browser nie schicken wuerde: ein unbekannter
    Wochentag (Sonntag hat bewusst keine Zeile), eine Uhrzeit ausserhalb der
    Standardzeiten oder ein Kaestchenwert, der kein "an" ist. Dann wird nichts
    gespeichert und die Uebersicht nennt den Grund (FO06).
    """

    ANWERTE = {'on', 'true', '1'}

    def __init__(self, daten, wochentage, zeiten, *args, **kwargs):
        super().__init__(daten, *args, **kwargs)
        self.wochentage = [int(w) for w in wochentage]
        self.zeiten = list(zeiten)
        self.tage = {}

    def _an(self, name):
        return (self.data.get(name) or '').strip().lower() in self.ANWERTE

    def clean(self):
        erlaubt = {f'aktiv_{w}' for w in self.wochentage}
        erlaubt |= {f'zeit_{w}_{z.replace(":", "-")}'
                    for w in self.wochentage for z in self.zeiten}
        for name in self.data:
            if not name.startswith(('aktiv_', 'zeit_')):
                continue  # csrfmiddlewaretoken u. a. gehoeren nicht zur Vorlage
            if name not in erlaubt:
                raise forms.ValidationError(
                    'Unbekanntes Feld in der Wochenvorlage - bitte die Seite neu laden.')
            if not self._an(name):
                raise forms.ValidationError(
                    'Ungültiger Wert in der Wochenvorlage - bitte die Seite neu laden.')
        for w in self.wochentage:
            self.tage[w] = {
                'aktiv': self._an(f'aktiv_{w}'),
                'uhrzeiten': [z for z in self.zeiten
                              if self._an(f'zeit_{w}_{z.replace(":", "-")}')],
            }
        return self.cleaned_data
