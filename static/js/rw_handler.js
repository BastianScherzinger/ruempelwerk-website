/* rw_handler.js — die Ereignisbindung, die frueher in on…="…"-Attributen stand.
 *
 * Warum es diese Datei gibt (SI32, 08.09.2026): Ein ``onclick="…"`` ist fuer
 * eine CSP ausfuehrbarer Code im Markup. Ein Nonce deckt ihn NICHT ab – CSP
 * kennt Nonces nur an ``<script>``-Bloecken, nie an Attributen. Solange also
 * ein einziges ``on…=`` im HTML steht, muss ``'unsafe-inline'`` im script-src
 * bleiben, und damit ist die ganze Richtlinie gegen eingeschleusten Code
 * entwertet. Das war der Grund, aus dem SI09 nicht zu schliessen war; der Weg
 * dorthin steht seit dem 08.09.2026 im Kopf von apps/core/middleware.py.
 *
 * Gezaehlt wurden am 08.09.2026 ueber templates/: 29 Attribute auf
 * oeffentlichen Seiten (rw_rechner.html 17, standorte.html 8, home.html 2,
 * jobs.html 2 – der Zaehler von 8 bzw. 1 in der alten Notiz zaehlte Zeilen,
 * nicht Attribute) und 12 unter templates/stats/. Sie sind allesamt hierher
 * gewandert, uebersetzt in ``data-rw-*``-Attribute.
 *
 * **Warum data-Attribute und keine festen Selektoren.** Drei der Knoepfe
 * (``.rw-rechner-back``) tragen dieselbe Klasse und rufen drei verschiedene
 * Funktionen auf – ohne Kennung waeren sie nur ueber ihre Position im Dokument
 * zu unterscheiden, und die ist genau das, was hier niemand anfassen darf. Ein
 * ``data-rw-click="rwGoStep" data-rw-arg="1"`` sagt dasselbe wie das alte
 * Attribut, an derselben Stelle, ohne eine Klasse oder Kennung zu aendern.
 *
 * **Warum Delegation am document.** Der Preisrechner baut Teile seiner
 * Oberflaeche zur Laufzeit; ein Listener je Element muesste danach nachgezogen
 * werden. Ausserdem loest die Delegation die Funktionsnamen erst beim Ereignis
 * auf – rw_rechner.js laeuft mit ``defer`` nach dieser Datei, seine Funktionen
 * existieren beim Binden also noch gar nicht.
 *
 * **Was diese Datei NICHT kann, und was das bedeutet:** Sie ruft ausschliesslich
 * Funktionen auf, die auf ``window`` stehen, und setzt Stile aus dem Attribut.
 * Beliebiger Ausdruck im Markup – ``onclick="a(); b.c = 1"`` – laesst sich
 * damit nicht abbilden. Das ist Absicht: Genau diese Freiheit ist der Grund,
 * warum 'unsafe-inline' noetig war. Wer sie zurueckholt, holt den Befund mit.
 *
 * **Und was sie nicht prueft:** ob die genannte Funktion existiert. Ein Tippfehler
 * in ``data-rw-click`` faellt still aus – wie ein Tippfehler im alten
 * ``onclick`` auch, nur ohne Konsolenfehler. Der Test dagegen steht in
 * apps/core/tests/test_middleware.py: er haelt jeden im Markup genannten Namen
 * gegen die JavaScript-Dateien.
 */
(function () {
  'use strict';

  /* Stildeklarationen aus einem Attribut anwenden.
   * Schreibweise wie in CSS: "background:var(--rw-orange);color:#fff".
   * Ein leerer Wert ("transform:") entfernt die Eigenschaft – das ist die
   * Uebersetzung des alten ``this.style.transform=''``. */
  function stile(el, text) {
    if (!text) return;
    text.split(';').forEach(function (teil) {
      var pos = teil.indexOf(':');
      if (pos < 0) return;
      var name = teil.slice(0, pos).trim();
      var wert = teil.slice(pos + 1).trim();
      if (!name) return;
      if (wert) el.style.setProperty(name, wert);
      else el.style.removeProperty(name);
    });
  }

  function fn(name) {
    var f = name ? window[name] : null;
    return typeof f === 'function' ? f : null;
  }

  /* Das Argument des Aufrufs. Ohne data-rw-arg bekommt die Funktion das
   * Element selbst – das deckt ``rwSelectObjektart(this)`` ab und stoert die
   * argumentlosen Aufrufe nicht, die es einfach ignorieren. */
  function argument(el) {
    var roh = el.getAttribute('data-rw-arg');
    if (roh === null) return el;
    return /^-?\d+$/.test(roh) ? Number(roh) : roh;
  }

  function traeger(ziel, attribut) {
    return ziel && ziel.closest ? ziel.closest('[' + attribut + ']') : null;
  }

  /* ── Klick ──────────────────────────────────────────────────────────────
   * data-rw-prevent  → preventDefault (der Cookie-Link im Fuss)
   * data-rw-self     → nur, wenn direkt das Element getroffen wurde und nicht
   *                    ein Kind (der Klick neben den Dialog auf /standorte/) */
  document.addEventListener('click', function (ev) {
    var el = traeger(ev.target, 'data-rw-click');
    if (!el) return;
    if (el.hasAttribute('data-rw-self') && ev.target !== el) return;
    if (el.hasAttribute('data-rw-prevent')) ev.preventDefault();
    var f = fn(el.getAttribute('data-rw-click'));
    if (f) f(argument(el));
  });

  /* ── Tastatur fuer Nicht-Knoepfe (EIG261/EIG264, SEO-Audit 25.09.2026) ──
   * Die Objektwahl des Preisrechners und die Profilkarten auf /standorte/
   * sind <div>-Karten mit data-rw-click. Ein <div> reagiert weder auf
   * Enter noch auf Leertaste - mit der Tastatur blieb der Rechner deshalb
   * im ersten Schritt stehen. Im Markup tragen sie seitdem role="button"
   * und tabindex="0"; hier bekommen sie das Verhalten eines Knopfs dazu.
   * Echte <button>/<a> sind ausgenommen, die loesen den Klick selbst aus. */
  document.addEventListener('keydown', function (ev) {
    if (ev.key !== 'Enter' && ev.key !== ' ') return;
    var el = ev.target;
    if (!el || !el.getAttribute || el.getAttribute('role') !== 'button') return;
    if (!el.hasAttribute('data-rw-click')) return;
    var tag = (el.tagName || '').toLowerCase();
    if (tag === 'button' || tag === 'a' || tag === 'input') return;
    ev.preventDefault();
    var f = fn(el.getAttribute('data-rw-click'));
    if (f) f(argument(el));
  });

  /* ── Eingabe ────────────────────────────────────────────────────────────
   * Der alte Aufruf lautete ``rwQmInput(this.value)`` – der Wert, nicht das
   * Element. */
  document.addEventListener('input', function (ev) {
    var el = traeger(ev.target, 'data-rw-input');
    if (!el) return;
    var f = fn(el.getAttribute('data-rw-input'));
    if (f) f(el.value);
  });

  /* ── Wechsel ────────────────────────────────────────────────────────────
   * Bei Kontrollkaestchen der Zustand (``rwToggleMalerCheck(this.checked)``),
   * sonst der Wert. */
  document.addEventListener('change', function (ev) {
    var el = traeger(ev.target, 'data-rw-change');
    if (!el) return;
    var f = fn(el.getAttribute('data-rw-change'));
    if (!f) return;
    var art = (el.type || '').toLowerCase();
    f(art === 'checkbox' || art === 'radio' ? el.checked : el.value);
  });

  /* ── Zeigerwechsel ──────────────────────────────────────────────────────
   * Reine Stilwechsel, die frueher als onmouseover/onmouseout im Markup
   * standen. Sie feuern wie vorher auch dann, wenn der Zeiger zwischen
   * Element und Kind wechselt: ein Listener am Element verhaelt sich bei
   * Bubbling genauso wie das Attribut, das er ersetzt. */
  document.addEventListener('mouseover', function (ev) {
    var el = traeger(ev.target, 'data-rw-hover');
    if (el) stile(el, el.getAttribute('data-rw-hover'));
  });
  document.addEventListener('mouseout', function (ev) {
    var el = traeger(ev.target, 'data-rw-hover-aus');
    if (el) stile(el, el.getAttribute('data-rw-hover-aus'));
  });

  /* ── Rueckfrage vor dem Absenden ────────────────────────────────────────
   * Ersetzt ``onsubmit="return confirm('…')"`` im CMS. */
  document.addEventListener('submit', function (ev) {
    var el = traeger(ev.target, 'data-rw-confirm');
    if (!el) return;
    if (!window.confirm(el.getAttribute('data-rw-confirm'))) ev.preventDefault();
  });

  /* ── Ziehen und Ablegen (CMS-Uploadzone) ────────────────────────────────
   * dragover braucht das preventDefault, sonst nimmt der Browser die Datei
   * selbst entgegen und verlaesst die Seite. */
  document.addEventListener('dragover', function (ev) {
    var el = traeger(ev.target, 'data-rw-dragover');
    if (!el) return;
    ev.preventDefault();
    stile(el, el.getAttribute('data-rw-dragover'));
  });
  document.addEventListener('dragleave', function (ev) {
    var el = traeger(ev.target, 'data-rw-dragleave');
    if (el) stile(el, el.getAttribute('data-rw-dragleave'));
  });
  document.addEventListener('drop', function (ev) {
    var el = traeger(ev.target, 'data-rw-drop');
    if (!el) return;
    var f = fn(el.getAttribute('data-rw-drop'));
    if (f) f(ev);
  });

  /* ── Fehlgeschlagenes Bild ──────────────────────────────────────────────
   * ``error`` steigt nicht auf. Ohne die Erfassungsphase (drittes Argument
   * true) erreicht das Ereignis das document nie, und die Markierung fehlender
   * CMS-Bilder waere still verschwunden. */
  document.addEventListener('error', function (ev) {
    var el = ev.target;
    if (el && el.getAttribute && el.hasAttribute('data-rw-fehlerstil')) {
      stile(el, el.getAttribute('data-rw-fehlerstil'));
    }
  }, true);

  /* ── Aufklappmenue der Navigation (EIG123) ─────────────────────────────
   * "Unternehmen" war ein <span>: per Tastatur nicht erreichbar, und die
   * Links darunter bleiben bei visibility:hidden aus der Tab-Reihenfolge.
   * Jetzt ist es ein <button data-rw-menue aria-expanded>. Geoeffnet wird
   * per CSS (:hover, :focus-within, aria-expanded="true"); diese Stelle
   * haelt nur aria-expanded ehrlich und schliesst mit Escape. data-zu am
   * .rw-nav-dropdown blendet das Menue aus, obwohl der Fokus noch darin
   * steht – sonst hielte :focus-within es gegen Escape offen. */
  function menue(knopf, offen) {
    var huelle = knopf.closest('.rw-nav-dropdown');
    knopf.setAttribute('aria-expanded', offen ? 'true' : 'false');
    if (huelle) {
      if (offen) huelle.removeAttribute('data-zu');
      else huelle.setAttribute('data-zu', '');
    }
  }
  document.addEventListener('click', function (ev) {
    var knopf = traeger(ev.target, 'data-rw-menue');
    document.querySelectorAll('[data-rw-menue][aria-expanded="true"]')
      .forEach(function (k) { if (k !== knopf) menue(k, false); });
    if (knopf) menue(knopf, knopf.getAttribute('aria-expanded') !== 'true');
  });
  document.addEventListener('keydown', function (ev) {
    if (ev.key !== 'Escape') return;
    var huelle = ev.target.closest ? ev.target.closest('.rw-nav-dropdown') : null;
    var knopf = huelle ? huelle.querySelector('[data-rw-menue]') : null;
    if (!knopf) return;
    menue(knopf, false);
    knopf.focus();
  });
  /* Wer mit der Maus wieder hineinzeigt, bekommt das Menue zurueck; wer den
   * Fokus hinausbewegt, setzt es auf den Ausgangszustand. */
  document.addEventListener('mouseover', function (ev) {
    var huelle = ev.target.closest ? ev.target.closest('.rw-nav-dropdown[data-zu]') : null;
    if (huelle && !huelle.contains(ev.relatedTarget)) huelle.removeAttribute('data-zu');
  });
  document.addEventListener('focusout', function (ev) {
    var huelle = ev.target.closest ? ev.target.closest('.rw-nav-dropdown') : null;
    if (!huelle || huelle.contains(ev.relatedTarget)) return;
    var knopf = huelle.querySelector('[data-rw-menue]');
    if (knopf) knopf.setAttribute('aria-expanded', 'false');
    huelle.removeAttribute('data-zu');
  });
})();
