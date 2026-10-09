/* Personen-Modal der Standorte-Seite. Gehoert zu templates/standorte.html.

   Ausgelagert am 26.08.2026 (Befund W4): der Block lag inline auf jeder
   Seite und war damit nie cachebar. */
// EIG264 (SEO-Audit 25.09.2026): Der Dialog war als aria-modal deklariert,
// setzte aber keinen Fokus - mit der Tastatur lief man hinter ihm weiter
// durch die Seite. Jetzt: Fokus auf "Schliessen", Tab bleibt im Dialog,
// beim Schliessen zurueck auf die Karte, die ihn geoeffnet hat.
var rwPersonAusloeser = null;

function rwPersonFokusziele(modal) {
  return Array.prototype.filter.call(
    modal.querySelectorAll('a[href], button, [tabindex]:not([tabindex="-1"])'),
    function (el) { return el.offsetParent !== null; });
}

function rwOpenPerson(el) {
  var modal = document.getElementById('rw-person-modal');
  rwPersonAusloeser = el;
  var name  = el.dataset.name;
  var title = el.dataset.title;
  var role  = el.dataset.role;
  var img   = el.dataset.img;
  var bio   = el.dataset.bio;
  var quote = el.dataset.quote;

  document.getElementById('rw-modal-name').textContent  = name;
  document.getElementById('rw-modal-title').textContent = title;
  document.getElementById('rw-modal-role').textContent  = role;
  document.getElementById('rw-modal-bio').textContent   = bio;
  document.getElementById('rw-modal-quote').textContent = '„' + quote + '“';

  var wrap = document.getElementById('rw-modal-photo-wrap');
  if (img) {
    // S05 (17.09.2026): Name und Adresse stammen aus data-Attributen und
    // gehen als Eigenschaften hinein, nie als HTML-Text.
    var foto = document.createElement('img');
    foto.src = img;
    foto.alt = name || '';
    foto.style.cssText = 'width:96px;height:96px;border-radius:50%;object-fit:cover;object-position:center 20%;border:3px solid var(--rw-orange);box-shadow:0 4px 16px rgba(22,163,74,0.25);';
    wrap.replaceChildren(foto);
  } else {
    // # audit-ok S05: fester Platzhalter ohne Variable (Silhouette als SVG)
    wrap.innerHTML = '<div style="width:96px;height:96px;border-radius:50%;background:var(--rw-bg-2);border:3px dashed var(--rw-border);display:flex;align-items:center;justify-content:center;color:var(--rw-text-3);"><svg xmlns=\'http://www.w3.org/2000/svg\' width=\'40\' height=\'40\' viewBox=\'0 0 24 24\' fill=\'currentColor\'><path d=\'M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z\'/></svg></div>';
  }

  modal.style.display = 'flex';
  document.body.style.overflow = 'hidden';
  var ziele = rwPersonFokusziele(modal);
  if (ziele.length) ziele[0].focus();
}

function rwClosePerson() {
  var modal = document.getElementById('rw-person-modal');
  if (modal.style.display === 'none') return;
  modal.style.display = 'none';
  document.body.style.overflow = '';
  if (rwPersonAusloeser && rwPersonAusloeser.focus) rwPersonAusloeser.focus();
  rwPersonAusloeser = null;
}

document.addEventListener('keydown', function(e) {
  var modal = document.getElementById('rw-person-modal');
  if (!modal || modal.style.display === 'none') return;
  if (e.key === 'Escape') { rwClosePerson(); return; }
  if (e.key !== 'Tab') return;
  var ziele = rwPersonFokusziele(modal);
  if (!ziele.length) return;
  var erstes = ziele[0], letztes = ziele[ziele.length - 1];
  if (e.shiftKey && document.activeElement === erstes) {
    e.preventDefault(); letztes.focus();
  } else if (!e.shiftKey && document.activeElement === letztes) {
    e.preventDefault(); erstes.focus();
  } else if (!modal.contains(document.activeElement)) {
    e.preventDefault(); erstes.focus();
  }
});
