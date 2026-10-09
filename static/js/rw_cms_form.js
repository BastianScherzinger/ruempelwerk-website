/* rw_cms_form.js — die Oberflaeche des CMS-Formulars unter STATS_PATH.
 *
 * Stand bis zum 08.09.2026 als 140-Zeilen-<script> am Ende von
 * templates/stats/cms_form.html. Ausgelagert fuer SI09: script-src traegt
 * seitdem SHA-256-Hashes statt 'unsafe-inline', und ein Block, der eine
 * Template-Variable enthaelt, laesst sich nicht hashen – sein Inhalt wechselt
 * mit der Umgebung. Genau das war hier der Fall: Die Loesch-Adresse setzte
 * `{{ stats_path }}` mitten in ein Template-Literal.
 *
 * Der Pfad kommt jetzt aus data-stats-path am <body>. Fehlt das Attribut,
 * bleibt der Wert leer und der Loeschaufruf ginge auf "/aktuelles/…" statt
 * unter den Dashboard-Pfad – deshalb bricht loeschAdresse dann ab, statt eine
 * falsche Adresse zu bauen.
 *
 * Was diese Datei nicht kann: pruefen, ob ein Upload wirklich ankommt. Sie
 * zeigt die Vorschau aus der lokalen Datei; ob der Server das Bild annimmt,
 * entscheidet sich erst beim Absenden.
 */
(function () {
  'use strict';

  const statsPath = (document.body && document.body.dataset.statsPath) || '';

  // Show/hide image sections based on post type
  const typSel = document.getElementById('id_typ');
  const vorherGrp = document.getElementById('vorher-group');
  const nachherGrp = document.getElementById('nachher-group');
  const galerieGrp = document.getElementById('galerie-group');

  function updateBilderUI() {
    const v = typSel ? typSel.value : '';
    const isVN = v === 'vorher_nachher';
    if (vorherGrp) vorherGrp.style.display = isVN ? '' : 'none';
    if (nachherGrp) nachherGrp.style.display = isVN ? '' : 'none';
    if (galerieGrp) galerieGrp.style.display = !isVN ? '' : 'none';
  }

  if (typSel) {
    typSel.addEventListener('change', updateBilderUI);
    updateBilderUI();
  }

  // Bild löschen via AJAX – kein verschachteltes <form> nötig
  // Token aus dem DOM, nicht aus dem Cookie: CSRF_COOKIE_HTTPONLY steht seit
  // dem 08.09.2026 auf True, JavaScript sieht das Cookie also nicht mehr.
  // Das Feld liefert der csrf_token-Tag im Logout-Formular der Kopfzeile –
  // er steht auf jeder CMS-Seite, auch beim Anlegen eines neuen Beitrags.
  const csrfToken = (document.querySelector('[name=csrfmiddlewaretoken]') || {}).value || '';

  function loeschAdresse(postPk, bildPk) {
    if (!statsPath) return '';
    return '/' + statsPath + '/aktuelles/' + postPk + '/bild/' + bildPk + '/del/';
  }

  document.querySelectorAll('.btn-bild-del').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!confirm('Bild wirklich löschen?')) return;
      const ziel = loeschAdresse(btn.dataset.postPk, btn.dataset.bildPk);
      if (!ziel) return;
      btn.disabled = true;
      btn.textContent = '…';
      try {
        const res = await fetch(ziel, {
          method: 'POST',
          headers: { 'X-CSRFToken': csrfToken }
        });
        if (res.ok || res.redirected) {
          btn.closest('div').remove();
        } else {
          btn.disabled = false;
          btn.textContent = '🗑 Löschen';
        }
      } catch {
        btn.disabled = false;
        btn.textContent = '🗑 Löschen';
      }
    });
  });

  // ── Galerie Upload-Zone & Live-Vorschau ──────────────
  const fileInput = document.getElementById('id_bilder');
  const newPreview = document.getElementById('new-preview');
  const newThumbs = document.getElementById('new-thumbs');
  const newCountLbl = document.getElementById('new-count-label');
  const uploadZone = document.getElementById('upload-zone');

  function showPreviews(files) {
    if (!newThumbs || !files || !files.length) return;
    newThumbs.replaceChildren();
    Array.from(files).forEach((f, i) => {
      const wrap = document.createElement('div');
      wrap.style.cssText = 'position:relative;';
      const img = document.createElement('img');
      img.style.cssText = 'width:100%;aspect-ratio:1;object-fit:cover;border-radius:8px;border:1px solid rgba(0,255,136,.25);';
      const reader = new FileReader();
      reader.onload = e => { img.src = e.target.result; };
      reader.readAsDataURL(f);
      wrap.appendChild(img);
      newThumbs.appendChild(wrap);
    });
    newCountLbl.textContent = `${files.length} neue${files.length === 1 ? 's' : ''} Bild${files.length === 1 ? '' : 'er'} ausgewählt`;
    newPreview.style.display = '';
    if (uploadZone) {
      uploadZone.style.borderColor = '#00ff88';
      uploadZone.style.background = 'rgba(0,255,136,.07)';
      uploadZone.querySelector('div:nth-child(2)').textContent = `✓ ${files.length} Bild${files.length === 1 ? '' : 'er'} bereit`;
    }
  }

  if (fileInput) {
    fileInput.addEventListener('change', () => showPreviews(fileInput.files));
  }

  // Bleibt auf window: rw_handler.js bindet das Ablegen ueber
  // data-rw-drop="handleDrop" und schlaegt den Namen dort nach.
  window.handleDrop = function (e) {
    e.preventDefault();
    if (!fileInput) return;
    const dt = new DataTransfer();
    Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/')).forEach(f => dt.items.add(f));
    fileInput.files = dt.files;
    showPreviews(fileInput.files);
    if (uploadZone) {
      uploadZone.style.borderColor = 'rgba(0,255,136,.25)';
      uploadZone.style.background = 'rgba(0,255,136,.03)';
    }
  };

  // Live-Vorschau für VN-Bilder
  function makeVnPreview(inputId, previewId, borderColor) {
    const inp = document.getElementById(inputId);
    const wrap = document.getElementById(previewId);
    if (!inp || !wrap) return;
    inp.addEventListener('change', () => {
      wrap.replaceChildren();
      if (!inp.files.length) { wrap.style.display = 'none'; return; }
      const grid = document.createElement('div');
      grid.style.cssText = 'display:grid;grid-template-columns:repeat(auto-fill,minmax(80px,1fr));gap:6px;';
      Array.from(inp.files).forEach(f => {
        const img = document.createElement('img');
        img.style.cssText = `width:100%;aspect-ratio:1;object-fit:cover;border-radius:6px;border:1px solid ${borderColor};`;
        const reader = new FileReader();
        reader.onload = e => { img.src = e.target.result; };
        reader.readAsDataURL(f);
        grid.appendChild(img);
      });
      const lbl = document.createElement('div');
      lbl.style.cssText = 'font-family:var(--font);font-size:0.62rem;color:var(--muted);margin-top:4px;';
      lbl.textContent = `${inp.files.length} Bild${inp.files.length === 1 ? '' : 'er'} ausgewählt`;
      wrap.appendChild(grid);
      wrap.appendChild(lbl);
      wrap.style.display = '';
    });
  }
  makeVnPreview('id_bilder_vor', 'preview-vor', 'rgba(0,255,136,.4)');
  makeVnPreview('id_bilder_nach', 'preview-nach', 'rgba(34,197,94,.5)');

  // Autor-Karten: visuelles Highlight bei Auswahl
  function updateAutorCards() {
    document.querySelectorAll('.autor-radio').forEach(radio => {
      const card = radio.closest('label').querySelector('.autor-card');
      if (radio.checked) {
        card.style.borderColor = '#00ff88';
        card.style.background = 'rgba(0,255,136,0.08)';
      } else {
        card.style.borderColor = 'rgba(255,255,255,0.06)';
        card.style.background = 'rgba(255,255,255,0.02)';
      }
    });
  }
  document.querySelectorAll('.autor-radio').forEach(r => r.addEventListener('change', updateAutorCards));
  updateAutorCards();
})();
