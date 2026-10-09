/* Zwei-Klick-Karte fuer templates/standorte.html (P8, Befund A5).

   WAS VORHER WAR: Die Seite band vier OpenStreetMap-iframes direkt ein. Sie
   trugen loading="lazy" und referrerpolicy="no-referrer" - sauber gemacht,
   aber das verhindert nicht, dass beim Scrollen die IP jedes Besuchers an die
   OpenStreetMap Foundation (Vereinigtes Koenigreich) geht. Ohne Einwilligung,
   und ohne dass die Datenschutzerklaerung den Empfaenger ueberhaupt nannte.

   WAS JETZT PASSIERT: Im HTML steht statt des iframes ein Knopf. Erst sein
   Klick setzt den iframe ein - vorher gibt es keine Verbindung zu
   openstreetmap.org. Die Adresse steht in data-rw-karte, der Titel in
   data-rw-karte-titel.

   DREI DINGE, DIE HIER ABSICHT SIND:

   1. Ein echtes <button>, kein <div onclick>. Es ist ohne Maus erreichbar,
      meldet sich dem Screenreader als Bedienelement und laesst sich mit der
      Leertaste ausloesen - alles drei muesste man einem <div> von Hand
      beibringen.
   2. Die Zustimmung wird NICHT gespeichert. Kein localStorage, kein Cookie.
      Wer sie speichern wollte, brauechte dafuer eine Rechtsgrundlage und
      einen Widerruf - fuer eine Karte, die man ohnehin nur einmal je Besuch
      anschaut, waere das mehr Datenverarbeitung, nicht weniger.
   3. Der iframe behaelt loading="lazy" und referrerpolicy="no-referrer".
      Nach dem Klick geht die IP hin, der Referrer aber weiterhin nicht - der
      Anbieter erfaehrt nicht, von welcher Unterseite aus geklickt wurde.

   FALLE: `frame-src https://www.openstreetmap.org` muss in der CSP
   (apps/core/middleware.py) stehen bleiben. Wer die Zeile mit den iframes
   zusammen entfernt hat, baut eine Karte, die nach dem Klick stumm nicht
   erscheint - dieselbe Fehlerklasse, die bei TrustLocal vier Anlaeufe
   gekostet hat.

   Eingebunden am Ende von standorte.html mit `defer`, wie rw_standorte.js -
   und bewusst nicht ueber components/rw_js.html: Das Skript gehoert zu genau
   einer Seite, und rw_js.html steht auf allen 85. */
(function () {
  'use strict';

  function karteLaden(knopf) {
    var quelle = knopf.getAttribute('data-rw-karte');
    if (!quelle) return;

    var rahmen = document.createElement('iframe');
    rahmen.src = quelle;
    rahmen.title = knopf.getAttribute('data-rw-karte-titel') || 'Karte';
    rahmen.loading = 'lazy';
    rahmen.setAttribute('referrerpolicy', 'no-referrer');

    knopf.replaceWith(rahmen);

    // Den Fokus mitnehmen: Wer den Knopf mit der Tastatur ausgeloest hat,
    // stuende sonst mit dem Fokus auf einem Element, das es nicht mehr gibt -
    // der naechste Tab-Schritt beginnt dann wieder am Seitenanfang.
    rahmen.setAttribute('tabindex', '0');
    try { rahmen.focus({ preventScroll: true }); } catch (e) { /* aeltere Browser */ }
  }

  document.addEventListener('click', function (ereignis) {
    var knopf = ereignis.target.closest('[data-rw-karte]');
    if (knopf) karteLaden(knopf);
  });
})();
