"""``{% rw_antispam %}`` - die versteckten Felder der Spam-Abwehr.

Ein Tag fuer alle vier Formulare (Anfrage, Kooperation, Jobs, Preisrechner),
damit die Felder nicht viermal per Hand gepflegt werden muessen und beim
naechsten Formular nicht vergessen werden. Was der Block ausliefert und warum,
steht in ``apps/core/antispam.py``.

Der Preisrechner schickt JSON per fetch statt eines Formular-POST. Fuer ihn
legt das Skript die beiden Werte zusaetzlich unter ``window.RW_AS`` ab; das
Wizard-Skript haengt sie an den Request-Body.
"""

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ..antispam import form_token

register = template.Library()


# Berechnet den Nachweis, den antispam.js_proof serverseitig erwartet: FNV-1a
# ueber den Token, Base36. Laeuft ueber ALLE Formulare der Seite, damit der
# Block mehrfach eingebunden werden kann, ohne dass sich die Skripte in die
# Quere kommen. Ein Bot ohne JavaScript laesst rw_j leer und faellt auf.
_SKRIPT = """<script>(function(){
  function h(s){var x=2166136261;for(var i=0;i<s.length;i++){x^=s.charCodeAt(i)&0xFFFF;x=Math.imul(x,16777619)>>>0;}return (x>>>0).toString(36);}
  function fuellen(){
    var felder=document.querySelectorAll('input[name="rw_t"]');
    for(var i=0;i<felder.length;i++){
      var t=felder[i].value, form=felder[i].form;
      var ziel=form?form.querySelector('input[name="rw_j"]'):null;
      if(ziel){ziel.value=h(t);}
      window.RW_AS={t:t,j:h(t)};
    }
  }
  if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',fuellen);}else{fuellen();}
})();</script>"""


# audit-ok K18: fester Text aus diesem Modul, keine Eingabe und keine Datenbank.
_HONEYPOT = mark_safe(
    '<div style="position:absolute;left:-9999px;top:-9999px;'
    'width:1px;height:1px;overflow:hidden;" aria-hidden="true">'
    # Honeypot. Bleibt "website" - der Name steht so bereits in den
    # bestehenden Templates und in den Log-Meldungen.
    '<input type="text" name="website" tabindex="-1" autocomplete="off">'
    '</div>'
)
# audit-ok K18: fester Text aus diesem Modul; der Skriptblock muss byte-gleich
# bleiben, sein SHA-256 steht in _INLINE_SKRIPT_HASHES (CSP).
_NACHWEIS = mark_safe('<input type="hidden" name="rw_j" value="">' + _SKRIPT)


@register.simple_tag
def rw_antispam():
    # Der einzige veränderliche Wert ist der signierte Token - er geht durch
    # format_html und wird damit maskiert, auch wenn er heute nur aus Ziffern,
    # Doppelpunkt und Base64-Zeichen besteht.
    return format_html('{}<input type="hidden" name="rw_t" value="{}">{}',
                       _HONEYPOT, form_token(), _NACHWEIS)
