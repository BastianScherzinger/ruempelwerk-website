/* Laufband der Startseite (01.10.2026).
   Ohne dieses Skript steht das Band still (eine Liste, kein Pause-Knopf nötig).
   Mit Skript läuft es, solange der Besucher keine reduzierte Bewegung wünscht,
   und bekommt einen sichtbaren Pause-Knopf (WCAG 2.2.2). Die Bewegung selbst
   ist reines CSS (transform). Kein rankingrelevanter Text entsteht hier. */
(function () {
  'use strict';
  var band = document.getElementById('rw-laufband');
  if (!band) return;
  var knopf = band.querySelector('.rw-laufband-pause');
  var schluessel = 'rw-laufband-pause';
  var reduziert = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;

  function lesen() {
    try { return window.sessionStorage.getItem(schluessel) === '1'; } catch (e) { return false; }
  }
  function schreiben(an) {
    try { window.sessionStorage.setItem(schluessel, an ? '1' : '0'); } catch (e) { /* ohne Speicher geht es auch */ }
  }
  function pausieren(an) {
    band.classList.toggle('rw-laufband--pause', an);
    if (knopf) knopf.setAttribute('aria-pressed', an ? 'true' : 'false');
  }
  // Die zweite, gleiche Liste fuer die nahtlose Schleife entsteht erst hier
  // (spart DOM-Elemente im HTML); sie ist aria-hidden, also reine Optik.
  function verdoppeln() {
    var spur = band.querySelector('.rw-laufband-spur');
    var liste = spur && spur.querySelector('.rw-laufband-liste');
    if (!liste || spur.children.length > 1) return;
    var kopie = liste.cloneNode(true);
    kopie.setAttribute('aria-hidden', 'true');
    spur.appendChild(kopie);
  }
  function anwenden() {
    var still = reduziert && reduziert.matches;
    if (!still) verdoppeln();
    band.classList.toggle('rw-laufband--an', !still);
  }

  anwenden();
  pausieren(lesen());
  if (reduziert) {
    if (reduziert.addEventListener) reduziert.addEventListener('change', anwenden);
    else if (reduziert.addListener) reduziert.addListener(anwenden);
  }
  if (knopf) {
    knopf.addEventListener('click', function () {
      var an = knopf.getAttribute('aria-pressed') !== 'true';
      pausieren(an);
      schreiben(an);
    });
  }
})();
