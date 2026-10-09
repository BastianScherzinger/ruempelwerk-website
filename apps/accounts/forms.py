"""Formulare des Anmeldebereichs unter ``/accounts/`` (Django-Auth-Altbestand).

Die öffentliche Website benutzt keines davon; sie bedienen nur
``accounts/login.html`` und ``accounts/profile.html``.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import UserProfile


class LoginForm(AuthenticationForm):
    """Anmeldung mit Benutzername und Passwort, mit deutschen Beschriftungen."""

    username = forms.CharField(
        label='Benutzername',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Benutzername',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        label='Passwort',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        })
    )


class ProfileForm(forms.ModelForm):
    """Bearbeitet das ``UserProfile``; das Profilbild ist auf 2 MB begrenzt."""

    class Meta:
        model = UserProfile
        fields = ('avatar', 'bio', 'company', 'phone')
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'company': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'size') and avatar.size > 2 * 1024 * 1024:
            raise ValidationError('Bild darf maximal 2 MB groß sein.')
        return avatar
