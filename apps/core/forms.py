"""Die Django-Formulare der oeffentlichen Seite - genau eines.

Nur ``/anfrage/`` benutzt ein ``ModelForm``. Die drei anderen Formulare
(Preisrechner, Kooperation, Bewerbung) lesen ihre Felder in der View aus
``request.POST``, weil sie mehr tun, als ein Model zu fuellen: Der Rechner
nimmt JSON per ``fetch`` entgegen, die beiden anderen schicken zwei Mails.
"""

from django import forms
from django.core.validators import MaxLengthValidator

from .models import Anfrage, Besichtigungstermin


class AnfrageForm(forms.ModelForm):
    """Das Formular auf ``/anfrage/`` - sechs Felder, drei davon Pflicht.

    Pflicht sind ``leistung``, ``name`` und ``email``; ``zusatz_info``,
    ``telefon`` und ``adresse`` sind im Model ``blank=True`` und bleiben es
    hier. Das ist eine Entscheidung und keine Nachlaessigkeit: Ein Kunde, der
    nur Name und E-Mail hinterlaesst, soll durchkommen - genau dieser Fall ist
    am 01.09.2026 an der Spam-Abwehr gescheitert und hat sie ``kein-js`` von
    +4 auf +3 gekostet (Regel 18).

    Die Spam-Abwehr selbst steht **nicht** hier, sondern im Template
    (``{% rw_antispam %}``) und in der View (``rate_limited``, ``ist_spam``);
    ein ModelForm sieht weder IP noch Kopfzeilen.

    ``zusatz_info`` ist im Model ein ``TextField`` ohne Grenze. Das Formular
    begrenzt es auf ``ZUSATZ_MAX`` Zeichen (FO07, 17.09.2026) - dieselbe Zahl
    steht als ``maxlength`` in ``templates/anfrage.html`` und entspricht der
    Kürzung der drei übrigen Formulare in ``views.py``.
    """

    ZUSATZ_MAX = 2000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        feld = self.fields['zusatz_info']
        feld.max_length = self.ZUSATZ_MAX
        feld.validators.append(MaxLengthValidator(self.ZUSATZ_MAX))

    class Meta:
        model = Anfrage
        fields = ['leistung', 'zusatz_info', 'name', 'email', 'telefon', 'adresse']
        widgets = {
            'zusatz_info': forms.Textarea(attrs={
                'placeholder': 'Beschreiben Sie kurz Ihren Auftrag – z.B. Größe der Immobilie, besondere Gegebenheiten, Wunschtermin ...',
                'rows': 4,
            }),
            'name': forms.TextInput(attrs={'placeholder': 'Vor- und Nachname'}),
            'email': forms.EmailInput(attrs={'placeholder': 'ihre@email.de'}),
            'telefon': forms.TextInput(attrs={'placeholder': '+49 ...'}),
            'adresse': forms.TextInput(attrs={'placeholder': 'Straße, PLZ, Ort des Objekts'}),
        }


class TerminForm(forms.ModelForm):
    """Das Formular der Terminbuchung (``#f-termin`` / ``/termin/``, Bauplan §5).

    ``slot`` ist kein Feld von ``Besichtigungstermin`` - es traegt den
    ISO-Zeitstempel des gewaehlten Termins (``apps.core.termine.slot_datetime``
    liefert ihn, ``termine.slot_aus_wert`` liest ihn zurueck) und wird in der
    View auf ``beginn`` gemappt. Pflicht sind Termin, Objektart, Name und
    Adresse; Telefon und E-Mail sind wie bei ``/anfrage/`` beide optional -
    genau EINE Kontaktmoeglichkeit muss angegeben sein, das prueft
    ``clean()``, nicht die Feldpflicht.
    """

    slot = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Im Model ist ``adresse`` blank=True (dieselbe Spalte koennte auch
        # ohne Adresse gespeichert werden) - fuer die Terminbuchung ist sie
        # aber Pflicht: Ohne Adresse weiss Oliver nicht, wohin die
        # Besichtigung fuehrt.
        self.fields['adresse'].required = True
        # Die Art der Besichtigung hat einen Default (vor_ort): fehlt der Wert
        # (Formular ohne die Auswahl, alter Zwischenspeicher), gilt vor_ort.
        # Ein **ungueltiger** Wert bleibt ein Fehler (Whitelist, kein Freitext).
        self.fields['besichtigungsart'].required = False
        self.fields['besichtigungsart'].choices = list(Besichtigungstermin.ART_CHOICES)
        # Djangos ModelForm stellt jeder Auswahl ohne Vorgabe die Leerwahl
        # ("---------", value="") voran. Die Terminseite rendert die Objektart
        # als Karten (rw_termin.html) - dort war "---------" die erste, waehlbare
        # Karte, und ein Klick darauf schickte einen leeren Wert ab. Die Pflicht
        # bleibt (Model: kein blank), nur die Leerkarte entfaellt.
        self.fields['objektart'].choices = [
            (wert, label) for wert, label in self.fields['objektart'].choices if wert != '']

    class Meta:
        model = Besichtigungstermin
        fields = ['besichtigungsart', 'objektart', 'name', 'telefon', 'adresse', 'email', 'hinweis']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Vor- und Nachname'}),
            'telefon': forms.TextInput(attrs={'placeholder': 'für die Bestätigung'}),
            'adresse': forms.TextInput(attrs={'placeholder': 'Straße, PLZ, Ort'}),
            'email': forms.EmailInput(attrs={'placeholder': 'name@beispiel.de'}),
            'hinweis': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_besichtigungsart(self):
        return self.cleaned_data.get('besichtigungsart') or 'vor_ort'

    def clean(self):
        cleaned = super().clean()
        telefon = (cleaned.get('telefon') or '').strip()
        if cleaned.get('besichtigungsart') == 'video' and not telefon:
            # Der Videoanruf geht per WhatsApp auf genau diese Nummer - eine
            # E-Mail-Adresse allein reicht nicht.
            self.add_error('telefon', 'Für die Video-Besichtigung brauchen wir Ihre '
                           'Telefonnummer – Oliver Pohl ruft Sie per WhatsApp-Video an.')
            return cleaned
        if not telefon and not (cleaned.get('email') or '').strip():
            raise forms.ValidationError(
                'Bitte Telefonnummer oder E-Mail-Adresse angeben, damit Oliver '
                'Pohl den Termin bestätigen kann.')
        return cleaned
