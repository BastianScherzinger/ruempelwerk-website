/* TrustLocal erst auf Klick laden (Rechtsprüfung 26.09.2026).

   WAS VORHER WAR: Beide TrustLocal-Komponenten (rw_trustlocal.html auf
   /ueber-uns/, rw_trustlocal_score.html auf den Leistungs- und Stadtseiten)
   banden das Anbieter-Skript direkt mit <script async> ein. Beim Seitenaufruf
   ging die IP-Adresse jedes Besuchers an static.trustlocal.de und
   trustlocal.de - ohne Einwilligung, gestützt nur auf lit. f.

   WAS JETZT PASSIERT: Im HTML steht statt des Skripts ein Knopf mit
   data-rw-trustlocal="<Skript-Adresse>". Erst sein Klick hängt das Skript
   an - vorher gibt es keine Verbindung zu TrustLocal. Dasselbe Muster wie die
   Zwei-Klick-Karte in rw_karte.js, und aus denselben Gründen:

   1. Die Zustimmung wird NICHT gespeichert. Kein localStorage, kein Cookie -
      sonst bräuchte es dafür einen eigenen Widerruf.
   2. Der Knopf steht mit `hidden` im HTML und wird erst hier sichtbar. Ohne
      JavaScript lädt das Widget ohnehin nicht; ein Knopf, der nichts tut,
      wäre schlechter als keiner (rw_trustlocal.html hat dafür <noscript>).
   3. Die Skripte finden ihre Platzhalter (.trustlocal-review-widget bzw.
      .trustlocal-widget) selbst, sobald sie laufen - sie warten nicht auf
      DOMContentLoaded (am 26.09.2026 im Anbieter-Code nachgesehen). Deshalb
      genügt es, das Skript nachträglich einzuhängen.

   FALLE: static.trustlocal.de muss in script-src der CSP stehen bleiben
   (apps/core/middleware.py), /ueber-uns/ braucht dort weiter 'unsafe-eval'.
   Sonst lädt das Widget nach dem Klick stumm nicht. */
(function () {
  'use strict';

  var knoepfe = document.querySelectorAll('[data-rw-trustlocal]');
  for (var i = 0; i < knoepfe.length; i++) {
    knoepfe[i].hidden = false;
  }

  function laden(knopf) {
    var quelle = knopf.getAttribute('data-rw-trustlocal');
    if (!quelle) return;

    var skript = document.createElement('script');
    skript.src = quelle;
    skript.async = true;
    document.body.appendChild(skript);

    // Knopf samt Hinweis entfernen; der Hinweis ist mit aria-describedby
    // am Knopf, beide stehen im selben Rahmen.
    var rahmen = knopf.closest('[data-rw-trustlocal-rahmen]') || knopf;
    rahmen.remove();
  }

  document.addEventListener('click', function (ereignis) {
    var knopf = ereignis.target.closest('[data-rw-trustlocal]');
    if (knopf) laden(knopf);
  });
})();
