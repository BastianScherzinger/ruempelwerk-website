/* rw_termin.js — Bedienung der Terminbuchung (Bauplan §5, Umbau 01.10.2026).
 * Keine onclick-Attribute (CSP) — die Knöpfe im Markup tragen
 * data-rw-click="rwTerminGeh|rwTerminTag" data-rw-arg="<Zahl>", gebunden über
 * static/js/rw_handler.js (dieselbe Delegation wie beim Preisrechner).
 *
 * OHNE dieses Skript funktioniert das Formular trotzdem: Alle drei
 * <fieldset data-rwt-stufe> und alle Tage stehen im HTML OHNE `hidden` — ein
 * Browser ohne JavaScript zeigt (und sendet) alles untereinander, nichts geht
 * verloren (die "Weiter"/"Zurück"-Knöpfe sind dann nur wirkungslose Zierde,
 * der Nutzer scrollt einfach weiter zum "Termin anfragen"-Knopf in Stufe 3).
 * Erst DIESES Skript (progressive enhancement)
 *   - blendet Stufe 2 und 3 aus und zeigt "Schritt 1 von 3",
 *   - zeigt die Tagesleiste und wählt den ersten Tag mit freiem Slot vor,
 *   - zeigt je Tag nur dessen Uhrzeiten und meldet den gewählten Termin mit
 *     Wochentag und Datum ("Gewählt: Freitag, 02.10., 10:00–10:25 Uhr"),
 *   - füllt die Zusammenfassung in Stufe 3 (Datum aus data-rwt-datum, nicht
 *     aus dem Label — das trägt nur die Uhrzeit),
 *   - wertet den Sprung #online-besichtigung aus (Banner) und wählt "per Video" vor.
 */
(function () {
  'use strict';

  var VIDEO_HASH = '#online-besichtigung';

  function formular() {
    return document.querySelector('.rw-termin-form');
  }

  function stufen(form) {
    return form.querySelectorAll('[data-rwt-stufe]');
  }

  function aktiveStufe(form) {
    var alle = stufen(form);
    for (var i = 0; i < alle.length; i++) {
      if (!alle[i].hasAttribute('hidden')) return Number(alle[i].getAttribute('data-rwt-stufe'));
    }
    return 1;
  }

  function markerAktiv(form, nummer) {
    var marker = form.querySelectorAll('[data-rwt-stufenmarker]');
    for (var i = 0; i < marker.length; i++) {
      var nr = Number(marker[i].getAttribute('data-rwt-stufenmarker'));
      marker[i].classList.toggle('ist-aktiv', nr === nummer);
      marker[i].classList.toggle('ist-erledigt', nr < nummer);
    }
    var text = form.querySelector('[data-rwt-schritttext]');
    var stufe = form.querySelector('[data-rwt-stufe="' + nummer + '"]');
    if (text && stufe) {
      text.textContent = 'Schritt ' + nummer + ' von 3 · ' + (stufe.getAttribute('data-rwt-titel') || '');
    }
  }

  function wert(form, name) {
    var feld = form.querySelector('[name="' + name + '"]');
    return feld ? (feld.value || '').trim() : '';
  }

  function istVideo(form) {
    var v = form.querySelector('#termin-art-video');
    return !!(v && v.checked);
  }

  function gewaehlterSlot(form) {
    return form.querySelector('input[name="slot"]:checked:not(:disabled)');
  }

  /* "Freitag, 02.10., 08:00–08:25 Uhr": Datum steht einmal je Tag am Fieldset
   * (data-rwt-datum), die Uhrzeit im Label, das Ende folgt aus der Dauer am
   * Formular (data-rwt-dauer) – so trägt nicht jeder der ~50 Slots den ganzen Text. */
  function slotAnzeige(form, slot) {
    var tag = slot.closest('.rw-termin-tag');
    var von = slot.parentNode ? (slot.parentNode.textContent || '').replace(/nicht frei/g, '').trim() : '';
    var datum = tag ? tag.getAttribute('data-rwt-datum') : '';
    var m = /^(\d{1,2}):(\d\d)$/.exec(von);
    if (!m || !datum) return ausIso(form, slot.value);
    var ende = Number(m[1]) * 60 + Number(m[2]) + (Number(form.getAttribute('data-rwt-dauer')) || 25);
    var zwei = function (n) { return (n < 10 ? '0' : '') + n; };
    return datum + ', ' + von + '–' + zwei(Math.floor(ende / 60) % 24) + ':' + zwei(ende % 60) + ' Uhr';
  }

  /* Rohwert "2026-10-05T08:00:00+02:00" nie zeigen: Wochentag, TT.MM. und Zeit
   * stehen im Wert selbst (Ortszeit des Servers, daher ohne Zeitzonenrechnung). */
  var WOCHENTAGE = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'];
  function ausIso(form, wertText) {
    var m = /^(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d)/.exec(wertText || '');
    if (!m) return '–';
    var tag = new Date(Date.UTC(Number(m[1]), Number(m[2]) - 1, Number(m[3])));
    var ende = Number(m[4]) * 60 + Number(m[5]) + (Number(form.getAttribute('data-rwt-dauer')) || 25);
    var zwei = function (n) { return (n < 10 ? '0' : '') + n; };
    return WOCHENTAGE[tag.getUTCDay()] + ', ' + m[3] + '.' + m[2] + '., ' + m[4] + ':' + m[5] +
      '–' + zwei(Math.floor(ende / 60) % 24) + ':' + zwei(ende % 60) + ' Uhr';
  }

  function labelText(form, name, klasse) {
    var eingabe = form.querySelector('input[name="' + name + '"]:checked');
    if (!eingabe) return '–';
    var label = eingabe.closest('label');
    if (!label) return eingabe.value;
    var teil = klasse ? label.querySelector('.' + klasse) : null;
    return ((teil || label).textContent || '').replace(/nicht frei/g, '').trim() || eingabe.value;
  }

  function uebersichtFuellen(form) {
    var slot = gewaehlterSlot(form);
    var tel = wert(form, 'telefon');
    var mail = wert(form, 'email');
    var daten = {
      slot: slot ? slotAnzeige(form, slot) : '–',
      besichtigungsart: labelText(form, 'besichtigungsart', 'rw-termin-art-titel'),
      objektart: labelText(form, 'objektart'),
      adresse: wert(form, 'adresse') || '–',
      kontakt: [wert(form, 'name'), tel, mail].filter(Boolean).join(' · ') || '–'
    };
    var ziel = form.querySelectorAll('[data-rwt-review]');
    for (var i = 0; i < ziel.length; i++) {
      var feld = ziel[i].getAttribute('data-rwt-review');
      ziel[i].textContent = daten[feld] !== undefined ? daten[feld] : '–';
    }
  }

  /* Der gewählte Termin als Zeile unter den Uhrzeiten; "Weiter" ist erst
   * mit einem gewählten Termin bedienbar. */
  function slotAnzeigen(form) {
    var slot = gewaehlterSlot(form);
    var zeile = form.querySelector('[data-rwt-gewaehlt]');
    var text = form.querySelector('[data-rwt-gewaehlt-text]');
    if (zeile && text) {
      if (slot) {
        text.textContent = slotAnzeige(form, slot);
        zeile.removeAttribute('hidden');
      } else {
        zeile.setAttribute('hidden', '');
      }
    }
    var weiter = form.querySelector('[data-rwt-weiter]');
    if (weiter) {
      weiter.setAttribute('aria-disabled', slot ? 'false' : 'true');
    }
  }

  /* Tagesleiste: schaltet, welcher Tag sichtbar ist (Klasse .rwt-tag-aus, wirkt
   * nur, wenn die Leiste per JS sichtbar ist: .rwt-js am Formular). */
  window.rwTerminTag = function (index) {
    var form = formular();
    if (!form) return;
    var tage = form.querySelectorAll('.rw-termin-tag');
    for (var i = 0; i < tage.length; i++) {
      var istZiel = tage[i].getAttribute('data-rwt-tagindex') === String(index);
      tage[i].classList.toggle('rwt-tag-aus', !istZiel);
    }
    var leiste = form.querySelector('.rw-termin-tagleiste');
    var tabs = form.querySelectorAll('.rw-termin-tagtab');
    for (var j = 0; j < tabs.length; j++) {
      var aktiv = tabs[j].getAttribute('data-rw-arg') === String(index);
      tabs[j].setAttribute('aria-pressed', aktiv ? 'true' : 'false');
      if (aktiv && leiste) {
        // nur die Leiste selbst verschieben, nie die Seite
        leiste.scrollLeft = tabs[j].offsetLeft - (leiste.clientWidth - tabs[j].offsetWidth) / 2;
      }
    }
  };

  function fehlerZeigen(form, text) {
    var stufe = form.querySelector('[data-rwt-stufe="2"]');
    if (!stufe) return;
    var hinweis = stufe.querySelector('#rwt-js-fehler');
    if (!hinweis) {
      hinweis = document.createElement('p');
      hinweis.className = 'rw-form-error';
      hinweis.id = 'rwt-js-fehler';
      hinweis.setAttribute('role', 'alert');
      var legende = stufe.querySelector('legend');
      if (legende && legende.nextSibling) stufe.insertBefore(hinweis, legende.nextSibling);
      else stufe.appendChild(hinweis);
    }
    hinweis.textContent = text;
  }

  function kontaktPruefen(form) {
    if (!wert(form, 'name')) return 'Bitte geben Sie Ihren Namen an.';
    if (!wert(form, 'adresse')) return 'Bitte geben Sie die Adresse des Objekts an.';
    if (!form.querySelector('input[name="objektart"]:checked')) return 'Bitte wählen Sie die Objektart.';
    if (istVideo(form) && !wert(form, 'telefon')) {
      return 'Für die Video-Besichtigung brauchen wir Ihre Telefonnummer – wir rufen Sie per WhatsApp-Video an.';
    }
    if (!wert(form, 'telefon') && !wert(form, 'email')) {
      return 'Bitte geben Sie Telefonnummer oder E-Mail-Adresse an.';
    }
    return '';
  }

  /* Nach einem Stufenwechsel den Formularanfang ins Bild holen, falls er
   * hinter der Kopfzeile oder weit oberhalb liegt. */
  function formularAnfangZeigen(form) {
    var r = form.getBoundingClientRect();
    if (r.top < 80 || r.top > window.innerHeight * 0.6) {
      window.scrollTo(0, Math.max(0, window.pageYOffset + r.top - 88));
    }
  }

  window.rwTerminGeh = function (nummer) {
    var form = formular();
    if (!form) return;

    // Stufe 1 -> 2: ohne gewählten Termin nicht weiterlassen.
    if (nummer === 2 && !gewaehlterSlot(form)) {
      var hinweis = form.querySelector('#rwt-slot-fehler');
      if (!hinweis) {
        hinweis = document.createElement('p');
        hinweis.className = 'rw-form-error';
        hinweis.id = 'rwt-slot-fehler';
        hinweis.setAttribute('role', 'alert');
        var woche = form.querySelector('.rw-termin-woche');
        if (woche) woche.parentNode.insertBefore(hinweis, woche);
      }
      hinweis.textContent = 'Bitte zuerst einen Termin wählen.';
      return;
    }
    // Stufe 2 -> 3: Pflichtangaben vorab prüfen (der Server prüft sie erneut).
    if (nummer === 3 && aktiveStufe(form) === 2) {
      var meldung = kontaktPruefen(form);
      if (meldung) {
        fehlerZeigen(form, meldung);
        return;
      }
      var alt = form.querySelector('#rwt-js-fehler');
      if (alt) alt.parentNode.removeChild(alt);
    }

    var alle = stufen(form);
    for (var i = 0; i < alle.length; i++) {
      var istZiel = alle[i].getAttribute('data-rwt-stufe') === String(nummer);
      if (istZiel) alle[i].removeAttribute('hidden');
      else alle[i].setAttribute('hidden', '');
    }
    markerAktiv(form, nummer);
    if (nummer === 3) uebersichtFuellen(form);
    formularAnfangZeigen(form);
  };

  /* Sprung aus dem Banner: "per WhatsApp-Video" vorwählen, zurück zu Stufe 1. */
  function videoVorwaehlen() {
    var form = formular();
    if (!form) return;
    var video = form.querySelector('#termin-art-video');
    if (video) video.checked = true;
    if (aktiveStufe(form) !== 1) window.rwTerminGeh(1);
  }

  function hashPruefen() {
    if (window.location.hash === VIDEO_HASH) videoVorwaehlen();
  }

  function init() {
    var form = formular();
    if (!form) return;
    form.classList.add('rwt-js');

    var alle = stufen(form);
    for (var i = 0; i < alle.length; i++) {
      if (alle[i].getAttribute('data-rwt-stufe') !== '1') {
        alle[i].setAttribute('hidden', '');
      }
    }
    var schritt = form.querySelector('[data-rwt-schritttext]');
    if (schritt) schritt.removeAttribute('hidden');
    markerAktiv(form, 1);

    // "Ändern"-Knöpfe der Zusammenfassung: nur mit Skript nützlich, deshalb nicht
    // fünfmal im HTML (Seitengewicht). data-rwt-zu = Stufe, zu der der Knopf springt.
    var zeilen = form.querySelectorAll('[data-rwt-zu]');
    for (var z = 0; z < zeilen.length; z++) {
      var dd = document.createElement('dd');
      dd.className = 'rw-termin-aendern';
      var kn = document.createElement('button');
      kn.type = 'button';
      kn.className = 'textknopf';
      kn.setAttribute('data-rw-click', 'rwTerminGeh');
      kn.setAttribute('data-rw-arg', zeilen[z].getAttribute('data-rwt-zu'));
      var dt = zeilen[z].previousElementSibling;
      kn.appendChild(document.createTextNode('Ändern'));
      var sr = document.createElement('span');
      sr.className = 'rwt-sr';
      sr.textContent = ' (' + (dt ? dt.textContent : '') + ')';
      kn.appendChild(sr);
      dd.appendChild(kn);
      zeilen[z].parentNode.appendChild(dd);
    }

    // Tag: der des schon gewählten Termins (nach einem Fehler), sonst der erste freie.
    var leiste = form.querySelector('.rw-termin-tagleiste');
    if (leiste) {
      leiste.removeAttribute('hidden');
      var start = Number(leiste.getAttribute('data-rwt-erster')) || 0;
      var gewaehlt = gewaehlterSlot(form);
      var tag = gewaehlt && gewaehlt.closest('.rw-termin-tag');
      if (tag) start = Number(tag.getAttribute('data-rwt-tagindex')) || 0;
      window.rwTerminTag(start);
    }
    slotAnzeigen(form);

    form.addEventListener('change', function (ev) {
      var name = ev.target && ev.target.name;
      if (name === 'slot') {
        slotAnzeigen(form);
        var alt = form.querySelector('#rwt-slot-fehler');
        if (alt) alt.parentNode.removeChild(alt);
      }
    });

    // Nach einem Serverfehler direkt zur Stufe mit der ersten Fehlermeldung.
    var fehler = form.querySelector('[data-rwt-stufe="2"] .rw-form-error');
    if (fehler && gewaehlterSlot(form)) window.rwTerminGeh(2);
    else if (form.querySelector('#rwt-form-fehler') && gewaehlterSlot(form)) window.rwTerminGeh(2);

    hashPruefen();
  }

  window.addEventListener('hashchange', hashPruefen);

  // Zweiter Klick auf denselben Banner-Link löst kein hashchange aus.
  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a[href$="' + VIDEO_HASH + '"]') : null;
    if (a) videoVorwaehlen();
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
