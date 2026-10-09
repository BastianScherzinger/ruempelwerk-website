/* Preisrechner-Wizard (A15). Gehoert zu components/rw_rechner.html und
   components/rw_rechner_js.html; laeuft immer NACH static/js/rw_basis.js
   (benutzt window.rwTrack).
   Die Preise kommen aus apps/core/data/pricing.py und stehen als
   <script type="application/json" id="rw-preise-daten"> im HTML - hier
   steht KEINE Zahl (Regel 1 in CLAUDE.md).

   Ausgelagert am 26.08.2026 (Befund W4): der Block lag inline auf jeder
   Seite und war damit nie cachebar. */
(function() {

  // ── Preise: eine Quelle, gerendert aus apps/core/data/pricing.py ──
  // Diese Zahlen NICHT hier ändern. Der Server rechnet mit denselben Werten
  // neu und traut dem hier berechneten Preis nicht – aber beide Rechnungen
  // dürfen nicht mehr auseinanderlaufen. Genau das war passiert: „Köthen"
  // gab serverseitig 5 Prozent Rabatt, den der Wizard nie angezeigt hat.
  const P = JSON.parse(document.getElementById('rw-preise-daten').textContent);

  const PER_QM_PREISE    = P.perQm;
  const MALER_PER_QM     = P.maler;
  const STOCKWERK_AP     = P.stockwerk;
  const FUELLGRAD_F      = P.fuellgrad;
  const SONDERABFALL_AP  = P.sonderabfall;
  const STANDORT_STAEDTE = P.standortStaedte;
  const STANDORT_FREMD   = P.standortFremd || [];

  // Reine Optik, deshalb hier und nicht in Python.
  const KLEIN_ICONS = {
    wasserhahn: '<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.4-2.4 2.6-2.6z"/></svg>',
    tuer: '<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 22V4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v18M2 22h20M14 12h.01"/></svg>',
    fenster_r: '<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="3" width="16" height="18" rx="1"/><path d="M4 12h16M12 3v18"/></svg>',
    wand_loch: '<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9h18M3 15h18M8 3v6M16 3v6M12 9v6M8 15v6M16 15v6"/><rect x="3" y="3" width="18" height="18" rx="1"/></svg>',
    schimmel: '<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/><path d="M2 21c0-3 1.85-5.36 5.08-6"/></svg>',
    fliesen: '<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 12h18M12 3v18"/></svg>',
    sockelleisten: '<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M16 3 21 8 8 21 3 16z"/><path d="M9 11l2 2M12 8l2 2M6 14l2 2"/></svg>',
    dichtungen: '<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.7s6 5.4 6 9.3a6 6 0 0 1-12 0c0-3.9 6-9.3 6-9.3z"/></svg>',
    steckdosen: '<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 2v6M15 2v6M7 8h10v3a5 5 0 0 1-10 0zM12 16v6"/></svg>',
  };
  // S05 (17.09.2026): Texte aus den Daten werden vor dem Einsetzen in HTML
  // maskiert. Sie kommen heute aus pricing.py - maskiert wird trotzdem, damit
  // ein Anfuehrungszeichen oder ein & in einer Bezeichnung nichts zerbricht.
  const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const KLEIN_ITEMS = P.kleinItems.map(it => ({
    id: it.id, label: it.label, preis: it.preis, emoji: KLEIN_ICONS[it.id] || '',
  }));


  // ── WhatsApp-Direktkontakt ──────────────────────────────────────────────
  // Die Nummer kommt aus apps/core/data/firma.py ueber den Context-Processor
  // (Regel 25) - hier steht sie NICHT. Fehlt der Block, bleiben die Knoepfe
  // aus, statt auf eine erfundene Nummer zu zeigen.
  const WA_NUMMER = (function(){
    try {
      var el = document.getElementById('rw-wa-nummer');
      return el ? JSON.parse(el.textContent) : '';
    } catch(e){ return ''; }
  })();

  // Baut die vorformulierte Nachricht aus dem, was der Nutzer schon eingegeben
  // hat. Ohne diese Daten muesste er im Chat alles noch einmal tippen - und
  // genau das ist die Huerde, an der der zweite Weg (`/anfrage/`) in 30 Tagen
  // null Kontakte gebracht hat.
  function waNachricht(preis) {
    const z = [];
    z.push('Hallo Ruempelwerk! \u{1F44B}');
    z.push('');
    const art = OBJEKTART_LABELS[state.objektart];
    if (art && state.qm) {
      z.push('Ich habe Ihren Preisrechner benutzt:');
      z.push('\u2022 Objekt: ' + art + ', ' + state.qm + ' m\u00B2');
    } else if (art) {
      z.push('Ich habe Ihren Preisrechner benutzt:');
      z.push('\u2022 Objekt: ' + art);
    } else {
      z.push('Ich haette gerne ein Angebot fuer eine Entruempelung.');
    }
    if (state.stadtort) z.push('\u2022 Ort: ' + state.stadtort);
    const fg = (FUELLGRAD_SUBS[state.objektart] || {})[state.fuellgrad];
    if (fg) z.push('\u2022 Zustand: ' + fg);
    if (preis) z.push('\u2022 Richtangebot laut Rechner: ' + fmt(preis) + ' \u20AC');
    z.push('');
    z.push(preis
      ? 'Passt das so? Ich schicke Ihnen gern Fotos.'
      : 'Was wuerde das ungefaehr kosten? Ich schicke Ihnen gern Fotos.');
    return z.join('\n');
  }

  // Setzt die Adresse eines WhatsApp-Knopfes. Der Klick selbst wird nicht hier
  // gezaehlt: rw_basis.js hoert global auf jedes <a href="wa.me...">, und ein
  // zweites rwTrack an derselben Stelle waere eine doppelte Conversion.
  function waKnopfSetzen(id, preis) {
    const el = document.getElementById(id);
    if (!el) return;
    if (!WA_NUMMER) { el.style.display = 'none'; return; }
    el.href = 'https://wa.me/' + WA_NUMMER + '?text=' + encodeURIComponent(waNachricht(preis));
    el.target = '_blank';
  }

  // ── Erweiterte Conversions ─────────────────────────────────────────────
  // Google normalisiert vor dem Hashen: trimmen, kleinschreiben. Genau
  // dieselbe Regel wendet `_lead_kennung()` in apps/core/views.py an - beide
  // Wege muessen denselben Hash liefern, sonst zaehlt Google zwei Personen.
  async function emailKennung(email) {
    try {
      const sauber = (email || '').trim().toLowerCase();
      if (!sauber || !window.crypto || !crypto.subtle) return '';
      const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(sauber));
      return Array.from(new Uint8Array(buf))
        .map(b => b.toString(16).padStart(2, '0')).join('');
    } catch (e) { return ''; }
  }

  const OBJEKTART_LABELS = P.objektartLabels;
  const OBJEKTART_ICONS = {
    keller:'<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="m21 8-9-5-9 5v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v9"/></svg>', wohnung:'<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 6h2M13 6h2M9 10h2M13 10h2M9 14h2M13 14h2M10 22v-4h4v4"/></svg>', haus:'<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/></svg>', gewerbe:'<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 21V11l5 3V11l5 3V11l5 3v7z"/><path d="M3 21h18M8 21v-4M13 21v-4"/></svg>', garten:'<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/><path d="M2 21c0-3 1.85-5.36 5.08-6"/></svg>', scheune:'<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/></svg>',
  };

  const FUELLGRAD_SUBS = {
    keller:  { leicht:'Fast leer',          mittel:'Normal befüllt',    voll:'Voll beladen',         verschmutzt:'Schrott/Gerümpel',    messi:'Extremfall/Messie' },
    wohnung: { leicht:'Kaum möbliert',       mittel:'Normal möbliert',   voll:'Vollständig möbliert', verschmutzt:'Stark verschmutzt',   messi:'Messie-Wohnung' },
    haus:    { leicht:'Kaum möbliert',       mittel:'Normal möbliert',   voll:'Vollständig möbliert', verschmutzt:'Stark verschmutzt',   messi:'Messie-Haus' },
    gewerbe: { leicht:'Leer/kaum bestückt',  mittel:'Normal bestückt',   voll:'Vollständig bestückt', verschmutzt:'Stark verschmutzt',   messi:'Schrott überall' },
    garten:  { leicht:'Wenig aufzuräumen',   mittel:'Mittlerer Aufwand', voll:'Stark zugewachsen',    verschmutzt:'Schrott/Bauschutt',   messi:'Jahrelang nicht geräumt' },
    scheune: { leicht:'Fast leer',           mittel:'Normal befüllt',    voll:'Voll bepackt',         verschmutzt:'Stark verschmutzt',   messi:'Jahrelang nicht geräumt' },
  };

  // ── State ──
  let state = {
    objektart: null,
    qm: null,
    stockwerk: 'eg', aufzug: false,
    fuellgrad: 'mittel',
    sonderabfall: 'keine',
    withMaler: false,
    kleinItems: [], kleinSonstiges: '',
    stadtort: '', standortRabatt: false,
  };

  // ── Preisberechnung pro m² (identisch mit Python-Backend) ──
  function berechne() {
    const o = state.objektart;
    if (!o || !state.qm) return null;
    const rates = PER_QM_PREISE[o];
    if (!rates) return null;

    let preis = Math.max(rates.minPreis, Math.round(rates.rate * state.qm));

    // Stockwerk (welche Objektarten, sagt Python)
    if (P.stockwerkObjekte.includes(o)) {
      if (!state.aufzug) {
        preis += STOCKWERK_AP[state.stockwerk] || 0;
      }
    }

    // Füllgrad
    const f = FUELLGRAD_F[state.fuellgrad] || 1.20;
    preis = Math.round(preis * f);

    // Sonderabfall (welche Objektarten, sagt Python)
    if (P.sonderabfallObjekte.includes(o)) {
      preis += SONDERABFALL_AP[state.sonderabfall] || 0;
    }

    // Basis (vor Add-ons, für Aufschlüsselung)
    const rawBasis = preis;

    // Malerarbeiten (per m²)
    let rawMaler = 0;
    if (state.withMaler) {
      rawMaler = Math.max(MALER_PER_QM.minPreis, Math.round(MALER_PER_QM.rate * state.qm));
      preis += rawMaler;
    }

    // Kleine Reparaturen
    let rawKlein = 0;
    state.kleinItems.forEach(id => {
      const it = KLEIN_ITEMS.find(i => i.id === id);
      if (it) rawKlein += it.preis;
    });
    if (state.kleinSonstiges.trim()) rawKlein += P.kleinSonstiges;
    preis += rawKlein;

    // Standort-Rabatt, gedeckelt am Mindestpreis (EIG165) - wie pricing.py
    const df = state.standortRabatt ? P.standortFaktor : 1.0;
    preis = Math.max(rates.minPreis, Math.round(preis * df));

    return {
      preis,
      pBasis: Math.max(rates.minPreis, Math.round(rawBasis * df)),
      pMaler: Math.round(rawMaler * df),
      pKlein: Math.round(rawKlein * df),
    };
  }

  // ── Standort-Check: ganze Wörter, nicht Teilstrings (EIG126) ──
  // Spiegelt pricing.py::ort_normalisiert und hat_standort_rabatt. Vorher
  // traf „Hallesche Straße, Bitterfeld" den Eintrag 'halle'.
  const UMSCHRIFT = { 'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss' };
  function woerter(text) {
    const t = String(text || '').normalize('NFC').toLowerCase()
      .replace(/[äöüß]/g, c => UMSCHRIFT[c]);
    return t.split(/[^\p{L}\p{N}]+/u).filter(Boolean);
  }
  function hatStandortRabatt(val) {
    const w = woerter(val);
    if (!w.length) return false;
    // EIG255: „Halle (Westf.)" ist nicht Halle (Saale).
    if (w.some(x => STANDORT_FREMD.includes(x))) return false;
    return STANDORT_STAEDTE.some(eintrag => {
      const teile = woerter(eintrag);
      for (let i = 0; i + teile.length <= w.length; i++) {
        if (teile.every((t, k) => w[i + k] === t)) return true;
      }
      return false;
    });
  }
  // Nur für den Gleichheitstest in apps/core/tests/test_pricing.py, der
  // diese Datei in Node ausführt - keine Oberfläche liest das.
  window.rwRechnerKern = { berechne: () => berechne(), hatStandortRabatt, state };

  window.rwCheckStandort = function(val) {
    state.stadtort = val;
    state.standortRabatt = hatStandortRabatt(val);
    const badge = document.getElementById('rw-standort-badge');
    if (state.standortRabatt) {
      badge.style.display = '';
      badge.classList.add('rw-animate-discount');
    } else {
      badge.style.display = 'none';
      badge.classList.remove('rw-animate-discount');
    }
  };

  // ── Objektart auswählen (single-select) ──
  window.rwSelectObjektart = function(card) {
    const oa = card.dataset.objektart;
    document.querySelectorAll('.rw-rechner-leistung-card').forEach(c => {
      c.classList.remove('selected');
      c.setAttribute('aria-pressed', 'false');
    });
    {
      // Erneuter Klick auf die gewaehlte Karte hebt die Wahl nicht auf (Voreinstellung "Haus").
      card.classList.add('selected');
      card.setAttribute('aria-pressed', 'true');
      card.classList.add('rw-card-pop');
      setTimeout(() => card.classList.remove('rw-card-pop'), 400);
      state.objektart = oa;
      // Conversion-Event: Preisrechner gestartet (einmal pro Seitenaufruf)
      if (!window.__rwRechnerStarted && window.rwTrack) {
        window.__rwRechnerStarted = true;
        window.rwTrack('rechner_start', { objektart: oa });
      }
    }
    document.getElementById('rw-next-1').disabled = !state.objektart;
  };

  // ── Step 2 vorbereiten ──
  window.rwGoStep2 = function() {
    const o = state.objektart;
    if (!o) return;

    // Abschnittsüberschrift
    // # audit-ok S05: OBJEKTART_ICONS sind feste SVG-Konstanten in dieser Datei
    document.getElementById('rw-s2-icon').innerHTML = OBJEKTART_ICONS[o] || OBJEKTART_ICONS.scheune;
    document.getElementById('rw-s2-title').textContent = (OBJEKTART_LABELS[o] || '') + ' – Details';

    // Stockwerk nur für die Objektarten, die Python dafür vorsieht
    const showSW = P.stockwerkObjekte.includes(o);
    document.getElementById('rw-stockwerk-wrap').style.display = showSW ? '' : 'none';
    document.getElementById('rw-aufzug-wrap').style.display = 'none';

    // Sonderabfall nur für die Objektarten, die Python dafür vorsieht
    document.getElementById('rw-sonderabfall-wrap').style.display = P.sonderabfallObjekte.includes(o) ? '' : 'none';

    // Füllgrad-Untertexte anpassen
    const subs = FUELLGRAD_SUBS[o] || FUELLGRAD_SUBS.keller;
    document.getElementById('fg-leicht-sub').textContent      = subs.leicht;
    document.getElementById('fg-mittel-sub').textContent      = subs.mittel;
    document.getElementById('fg-voll-sub').textContent        = subs.voll;
    document.getElementById('fg-verschmutzt-sub').textContent = subs.verschmutzt;
    document.getElementById('fg-messi-sub').textContent       = subs.messi;

    // m²-Feld zurücksetzen
    state.qm = null;
    const qmInput = document.getElementById('rw-qm-input');
    if (qmInput) qmInput.value = '';
    const qmHint = document.getElementById('rw-qm-hint');
    if (qmHint) qmHint.style.display = 'none';

    // Klein-Reparaturen-Checkliste rendern
    renderKleinItems();

    // Reset optionals
    state.withMaler = false;
    const malerCb = document.getElementById('rw-with-maler');
    if (malerCb) malerCb.checked = false;
    document.getElementById('rw-maler-hint').style.display = 'none';

    state.kleinItems = []; state.kleinSonstiges = '';
    const ta = document.getElementById('rw-klein-sonstiges');
    if (ta) ta.value = '';
    document.getElementById('rw-live-price').style.display = 'none';

    // Reset Stockwerk
    const swEg = document.getElementById('sw-eg');
    if (swEg) swEg.checked = true;
    state.stockwerk = 'eg'; state.aufzug = false;

    // Reset Füllgrad
    const fgMittel = document.getElementById('fg-mittel');
    if (fgMittel) fgMittel.checked = true;
    state.fuellgrad = 'mittel';

    // Reset Sonderabfall
    const saKeinen = document.getElementById('sa-keine');
    if (saKeinen) saKeinen.checked = true;
    state.sonderabfall = 'keine';

    checkStep2Valid();
    rwGoStep(2);
  };

  // ── m²-Eingabe → Live-Preis ──
  window.rwQmInput = function(val) {
    const qm = parseInt(val, 10);
    const hint = document.getElementById('rw-qm-hint');
    if (!qm || qm < 1) {
      state.qm = null;
      if (hint) hint.style.display = 'none';
      checkStep2Valid(); return;
    }
    state.qm = qm;

    // Basispreis (ohne Füllgrad / Aufschläge) live anzeigen
    const rates = PER_QM_PREISE[state.objektart];
    if (hint && rates) {
      const pBasis = Math.max(rates.minPreis, Math.round(rates.rate * qm));
      hint.innerHTML =
        `<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg> <strong>${qm} m²</strong> &nbsp;·&nbsp; ` +
        `${rates.rate} €/m² &nbsp;·&nbsp; ` +
        `Basispreis: <strong style="color:var(--rw-orange);">${pBasis.toLocaleString('de-DE')} €</strong>` +
        `<span style="opacity:0.65;font-size:0.8em;"> (Endpreis nach Füllgrad & Details)</span>`;
      hint.style.display = '';
    }
    updateMalerHint();
    checkStep2Valid();
  };

  // ── Klein-Reparaturen-Checkliste rendern ──
  function renderKleinItems() {
    const wrap = document.getElementById('rw-klein-items');
    // # audit-ok S05: Kennung, Bezeichnung und Preis gehen durch esc(); das Symbol ist eine feste SVG-Konstante
    wrap.innerHTML = KLEIN_ITEMS.map((it, i) => `
      <div class="rw-rechner-check-item" style="animation-delay:${i * 0.04}s">
        <input type="checkbox" id="ki-${esc(it.id)}" value="${esc(it.id)}">
        <label for="ki-${esc(it.id)}" class="rw-rechner-check-label">
          <span class="rw-rechner-check-indicator"><svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg></span>
          <span>${it.emoji} ${esc(it.label)}</span>
          <span class="rw-rechner-check-price">${esc(it.preis)} €</span>
        </label>
      </div>
    `).join('');
    wrap.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.addEventListener('change', () => {
      state.kleinItems = Array.from(wrap.querySelectorAll('input:checked')).map(c => c.value);
      updateLivePreis();
    }));
    const ta = document.getElementById('rw-klein-sonstiges');
    if (ta) ta.oninput = () => { state.kleinSonstiges = ta.value; updateLivePreis(); };
  }

  // ── Live-Preis (Kleine Reparaturen) ──
  function updateLivePreis() {
    let gesamt = 0;
    state.kleinItems.forEach(id => {
      const it = KLEIN_ITEMS.find(i => i.id === id);
      if (it) gesamt += it.preis;
    });
    if (state.kleinSonstiges.trim()) gesamt += P.kleinSonstiges;
    const el = document.getElementById('rw-live-price');
    const val = document.getElementById('rw-live-price-val');
    if (!gesamt) { el.style.display = 'none'; return; }
    el.style.display = 'flex';
    val.textContent = gesamt.toLocaleString('de-DE') + ' €';
  }

  // ── Malerarbeiten-Hinweis ──
  function updateMalerHint() {
    const hint = document.getElementById('rw-maler-hint');
    const priceEl = document.getElementById('rw-maler-hint-price');
    if (!state.withMaler || !state.qm) { hint.style.display = 'none'; return; }
    const mPreis = Math.max(MALER_PER_QM.minPreis, Math.round(MALER_PER_QM.rate * state.qm));
    priceEl.textContent = mPreis.toLocaleString('de-DE') + ' €';
    hint.style.display = '';
  }

  // ── Malerarbeiten Toggle ──
  window.rwToggleMaler = function() {
    const body = document.getElementById('rw-maler-body');
    const head = document.getElementById('rw-maler-head');
    const tog  = document.getElementById('rw-maler-toggle');
    const isHidden = body.style.display === 'none';
    body.style.display = isHidden ? '' : 'none';
    tog.textContent = isHidden ? '−' : '+';
    head.setAttribute('aria-expanded', isHidden ? 'true' : 'false');
  };

  window.rwToggleMalerCheck = function(checked) {
    state.withMaler = checked;
    updateMalerHint();
  };

  // ── Kleine Reparaturen Toggle ──
  window.rwToggleKlein = function() {
    const body = document.getElementById('rw-klein-body');
    const head = document.getElementById('rw-klein-head');
    const tog  = document.getElementById('rw-klein-toggle');
    const isHidden = body.style.display === 'none';
    body.style.display = isHidden ? '' : 'none';
    tog.textContent = isHidden ? '−' : '+';
    head.setAttribute('aria-expanded', isHidden ? 'true' : 'false');
  };

  // ── Step 2 Validierung ──
  function checkStep2Valid() {
    document.getElementById('rw-next-2').disabled = !state.qm;
  }

  // ── Zum Ergebnis (zeigt Gate: erst Name + E-Mail) ──
  window.rwGoToResult = function() {
    document.getElementById('rw-gate').style.display = '';
    document.getElementById('rw-result-reveal').style.display = 'none';
    document.getElementById('rw-email-error').classList.remove('visible');
    document.getElementById('rw-email-name').value = '';
    document.getElementById('rw-email-addr').value = '';
    const btn = document.getElementById('rw-gate-submit');
    btn.disabled = false;
    document.getElementById('rw-gate-submit-text').textContent = 'Angebot jetzt anzeigen →';
    document.getElementById('rw-email-success').style.display = 'none';
    // Der Ausweg am Gate traegt noch keinen Preis - den nennt die Antwort.
    // Er muss hier stehen, nicht im Absenden-Zweig: Wer keine E-Mail geben
    // will, klickt ihn, *bevor* er absendet.
    waKnopfSetzen('rw-wa-gate', null);
    rwGoStep(3);
  };

  // ── Preis enthüllen + E-Mail automatisch senden ──
  window.rwRevealAndSend = async function() {
    const name  = document.getElementById('rw-email-name').value.trim();
    const email = document.getElementById('rw-email-addr').value.trim();
    const hp    = document.getElementById('rw-website').value;
    const errEl = document.getElementById('rw-email-error');
    const btn   = document.getElementById('rw-gate-submit');
    const btnTx = document.getElementById('rw-gate-submit-text');

    errEl.classList.remove('visible');
    if (!name)  { showErr('Bitte geben Sie Ihren Namen ein.'); return; }
    if (!email || !email.includes('@')) { showErr('Bitte geben Sie eine gültige E-Mail ein.'); return; }

    btn.disabled = true;
    btnTx.textContent = 'Wird geladen…';

    const result = berechne();
    if (!result) {
      showErr('Fehler bei der Berechnung. Bitte gehen Sie zurück.');
      btn.disabled = false;
      btnTx.textContent = 'Angebot jetzt anzeigen →';
      return;
    }
    const { preis, pBasis, pMaler, pKlein } = result;

    // Gate ausblenden, Ergebnis einblenden
    document.getElementById('rw-gate').style.display = 'none';
    document.getElementById('rw-result-reveal').style.display = '';

    // Der Knopf am Ergebnis traegt den gerechneten Preis mit. Damit beginnt
    // das Gespraech mit einer Zahl statt mit einer Frage.
    waKnopfSetzen('rw-wa-ergebnis', preis);

    // Aufschlüsselung
    const hasAddons = (state.withMaler && pMaler > 0) || (pKlein > 0);
    const bdEl = document.getElementById('rw-price-breakdown');
    bdEl.style.display = hasAddons ? '' : 'none';
    if (hasAddons) {
      document.getElementById('rw-price-label-basis').textContent = OBJEKTART_LABELS[state.objektart] || 'Entrümpelung';
      document.getElementById('rw-price-val-basis').textContent = fmt(pBasis) + ' €';
      const malerRow = document.getElementById('rw-price-bd-maler');
      malerRow.style.display = (state.withMaler && pMaler > 0) ? '' : 'none';
      if (state.withMaler && pMaler > 0) document.getElementById('rw-price-val-maler').textContent = fmt(pMaler) + ' €';
      const kleinRow = document.getElementById('rw-price-bd-klein');
      kleinRow.style.display = (pKlein > 0) ? '' : 'none';
      if (pKlein > 0) document.getElementById('rw-price-val-klein').textContent = fmt(pKlein) + ' €';
    }

    animateCounter('rw-price-val', preis, 900);

    const rabattBadge = document.getElementById('rw-rabatt-badge');
    rabattBadge.style.display = state.standortRabatt ? '' : 'none';
    if (state.standortRabatt) rabattBadge.classList.add('rw-animate-discount');

    let hintText = 'inkl. MwSt., Arbeitslohn, Transport & Entsorgung · Festpreis nach Besichtigung';
    if (hasAddons) hintText = 'Entrümpelung + optionale Zusatzleistungen, inkl. MwSt. · Festpreis nach Besichtigung';
    document.getElementById('rw-result-hint').textContent = hintText;

    const fuellLabels = {
      leicht:'Wenig befüllt', mittel:'Normal befüllt', voll:'Stark befüllt',
      verschmutzt:'Stark verschmutzt', messi:'Extremfall / Messie',
    };
    let tags = [{ icon: OBJEKTART_ICONS[state.objektart], text: OBJEKTART_LABELS[state.objektart] }];
    if (state.qm) tags.push({ icon:'<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M16 3 21 8 8 21 3 16z"/><path d="M9 11l2 2M12 8l2 2M6 14l2 2"/></svg>', text: state.qm + ' m²' });
    tags.push({ icon:'<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="m21 8-9-5-9 5v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v9"/></svg>', text: fuellLabels[state.fuellgrad] || '' });
    if (state.withMaler) tags.push({ icon:'<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M9.06 11.9 2.5 18.5a2.12 2.12 0 0 0 3 3l6.6-6.56"/><path d="M20.7 4.6a1 1 0 0 0-1.4 0l-8.9 8.9 2.7 2.7 8.9-8.9a1 1 0 0 0 0-1.4z"/></svg>', text: 'Malerarbeiten inklusive' });
    if (state.kleinItems.length) {
      state.kleinItems.slice(0,2).forEach(id => {
        const it = KLEIN_ITEMS.find(i => i.id === id);
        if (it) tags.push({ icon: it.emoji, text: it.label });
      });
      if (state.kleinItems.length > 2) tags.push({ icon:'<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>', text: (state.kleinItems.length - 2) + ' weitere Reparaturen' });
    }
    if (state.standortRabatt) tags.push({ icon:'<svg class="rw-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>', text: Math.round((1 - P.standortFaktor) * 100) + ' % Standort-Nachlass' });

    // # audit-ok S05: Symbole sind feste SVG-Konstanten, der Text geht durch esc()
    document.getElementById('rw-result-summary').innerHTML = tags.filter(t => t.text).map(t =>
      `<span class="rw-rechner-result-tag">${t.icon} ${esc(t.text)}</span>`
    ).join('');

    const incl = document.getElementById('rw-result-includes');
    const baseItems = ['Arbeitslohn vollständig enthalten','Transportkosten inklusive','Entsorgungsgebühren inklusive','Besenreine Übergabe inklusive','Entsorgungsnachweis auf Wunsch'];
    const extraItems = [];
    if (state.withMaler) extraItems.push('Malerarbeiten fachgerecht inklusive');
    if (state.kleinItems.length || state.kleinSonstiges.trim()) extraItems.push('Kleine Reparaturen inklusive');
    // # audit-ok S05: nur die festen Zeilen aus baseItems/extraItems, zusätzlich durch esc()
    incl.innerHTML = [...baseItems, ...extraItems].map(t =>
      `<div class="rw-rechner-result-include">${esc(t)}</div>`
    ).join('');

    // E-Mail automatisch senden
    try {
      const resp = await fetch('/preisangebot/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
        body: JSON.stringify({
          name, email, website: hp,
          // Zeit-Token und JavaScript-Nachweis der Spam-Abwehr. Gesetzt vom
          // Skript des rw_antispam-Tags, geprueft in apps/core/antispam.py.
          rw_t: (window.RW_AS || {}).t || '',
          rw_j: (window.RW_AS || {}).j || '',
          objektart:       state.objektart || '',
          stadtort:        state.stadtort,
          qm:              state.qm || 0,
          stockwerk:       state.stockwerk,
          aufzug:          state.aufzug ? 'ja' : 'nein',
          fuellgrad:       state.fuellgrad,
          sonderabfall:    state.sonderabfall,
          with_maler:      state.withMaler,
          klein_items:     state.kleinItems,
          klein_sonstiges: state.kleinSonstiges,
        }),
      });
      const d = await resp.json();
      if (d.ok) {
        document.getElementById('rw-email-success').style.display = 'flex';
        // Conversion-Event: Angebot per E-Mail angefordert (hohe Kaufabsicht)
        // value = real berechneter Richtpreis (für GA-ROI-Schätzung)
        // Der Hash wird erst hier gerechnet - er kostet einen Tick, und die
        // Erfolgsmeldung soll nicht darauf warten. `await` ist erlaubt: die
        // umgebende Funktion ist ohnehin `async`.
        const kennung = await emailKennung(email);
        const daten = {
          objektart: state.objektart || '',
          value: (result && result.preis) ? result.preis : undefined,
          user_data_hash: kennung
        };
        if (window.rwTrack) {
          window.rwTrack('angebot_email', daten);
        } else if (window.__rwGtagLoaded && typeof window.gtag === 'function') {
          // Notweg (FO08, 18.09.2026): Dies ist der einzige Anfrageweg der
          // Seite, der auf derselben Seite endet – ohne Danke-Seite gibt es
          // kein zweites Signal. Fehlt rw_basis.js (Ladefehler, ein Hash, den
          // der Browser nicht bekommt), rechnet der Rechner weiter, schickt
          // die Anfrage weiter – und **niemand zaehlt sie**. Dann zaehlt
          // wenigstens GA4 mit.
          //
          // Doppelt zaehlen kann das nicht: Der Zweig laeuft nur, wenn es
          // rwTrack ueberhaupt nicht gibt (`else if`). Die Ads-Conversion
          // bleibt aus – ihre Labels liegen in rw_basis.js und sind hier gar
          // nicht erreichbar –, und dieselbe Einwilligungspruefung wie dort
          // steht davor (__rwGtagLoaded wird erst nach `rw_consent=all`
          // gesetzt).
          window.gtag('event', 'angebot_email', {
            objektart: daten.objektart,
            value: daten.value, currency: 'EUR'
          });
        }
      }
    } catch(e) { /* Preis ist bereits sichtbar */ }

    function showErr(msg) { errEl.textContent = msg; errEl.classList.add('visible'); }
  };

  // ── Count-Up-Animation ──
  function animateCounter(elId, target, duration) {
    const el = document.getElementById(elId);
    if (!el) return;
    const start = performance.now();
    function step(now) {
      const t = Math.min((now - start) / duration, 1);
      const ease = 1 - Math.pow(1 - t, 3);
      el.textContent = Math.round(target * ease).toLocaleString('de-DE');
      if (t < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function fmt(n) { return n.toLocaleString('de-DE'); }

  // ── Vollständiger Reset ──
  window.rwResetAll = function() {
    state.objektart = null;
    state.qm = null; state.stockwerk = 'eg'; state.aufzug = false;
    state.fuellgrad = 'mittel'; state.sonderabfall = 'keine';
    state.withMaler = false; state.kleinItems = []; state.kleinSonstiges = '';
    state.stadtort = ''; state.standortRabatt = false;
    const qmInput = document.getElementById('rw-qm-input');
    if (qmInput) qmInput.value = '';
    const qmHint = document.getElementById('rw-qm-hint');
    if (qmHint) qmHint.style.display = 'none';

    document.querySelectorAll('.rw-rechner-leistung-card').forEach(c => {
      c.classList.remove('selected');
      c.setAttribute('aria-pressed', 'false');
    });
    const si = document.getElementById('rw-stadtort');
    if (si) si.value = '';
    const badge = document.getElementById('rw-standort-badge');
    if (badge) { badge.style.display = 'none'; badge.classList.remove('rw-animate-discount'); }
    // Auf Stadtseiten zurück auf den vorbelegten Ort, nicht auf leer (EIG164).
    if (si && si.defaultValue) { si.value = si.defaultValue; window.rwCheckStandort(si.value); }

    document.getElementById('rw-next-1').disabled = true;
    rwGoStep(1);
  };

  // ── Step Navigation ──
  window.rwGoStep = function(n) {
    document.querySelectorAll('.rw-rechner-panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.rw-rechner-step').forEach(s => {
      const sn = parseInt(s.dataset.step);
      s.classList.remove('active', 'done');
      if (sn === n) s.classList.add('active');
      else if (sn < n) s.classList.add('done');
    });
    document.getElementById('rw-step-' + n).classList.add('active');
    const top = document.getElementById('rw-steps').getBoundingClientRect().top + window.scrollY - 100;
    window.scrollTo({ top, behavior: 'smooth' });
  };


  function getCsrf() {
    // Nur aus dem DOM. Der frühere Rückfall auf document.cookie ist am
    // 08.09.2026 entfallen: Das csrftoken-Cookie ist seitdem HttpOnly
    // (CSRF_COOKIE_HTTPONLY, SI16), JavaScript sieht es also gar nicht mehr –
    // ein Rückfall, der immer '' liefert, verdeckt nur den Fehler.
    // Das Feld liefert der csrf_token-Tag in components/rw_rechner.html, und
    // zwar unbedingt: Wo dieses Skript läuft, steht auch der Rechner.
    const el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
  }

  // ── Step-2 Radio-Listener ──
  document.querySelectorAll('input[name="stockwerk"]').forEach(r => r.addEventListener('change', function() {
    state.stockwerk = this.value;
    const showAufzug = (this.value !== 'eg');
    document.getElementById('rw-aufzug-wrap').style.display = showAufzug ? '' : 'none';
    if (!showAufzug) {
      const aufzugCb = document.getElementById('rw-aufzug');
      if (aufzugCb) aufzugCb.checked = false;
      state.aufzug = false;
    }
  }));
  document.getElementById('rw-aufzug').addEventListener('change', function() { state.aufzug = this.checked; });
  document.querySelectorAll('input[name="fuellgrad"]').forEach(r => r.addEventListener('change', function() { state.fuellgrad = this.value; }));
  document.querySelectorAll('input[name="sonderabfall"]').forEach(r => r.addEventListener('change', function() { state.sonderabfall = this.value; }));

  // ── Vorbelegter Ort (Stadt- und Matrixseiten, EIG164) ──
  // Das Feld kommt mit value="<Stadt>" aus rw_rechner.html; ohne diesen
  // Aufruf zeigte der Rechner keinen Nachlass, bis jemand hineintippt.
  (function stadtortVorbelegt() {
    const si = document.getElementById('rw-stadtort');
    if (si && si.value) window.rwCheckStandort(si.value);
  })();

  // ── Vorauswahl: ?objekt= oder data-rw-objektart ──
  // Zwei Quellen, ein Unterschied: Der Parameter kommt vom Hero-Mini-Rechner
  // der Startseite, also von einem Klick — dorthin darf gescrollt werden.
  // Das Attribut setzt die Leistungsseite selbst; dort haette ein Sprung zum
  // Rechner den Besucher ungefragt am Text vorbeigeschoben.
  (function applyPreselect() {
    try {
      var wrap = document.querySelector('.rw-rechner-wrap[data-rw-objektart]');
      var vomKlick = (new URLSearchParams(window.location.search).get('objekt') || '').toLowerCase();
      var oa = vomKlick || (wrap ? (wrap.getAttribute('data-rw-objektart') || '').toLowerCase() : '');
      if (!Object.prototype.hasOwnProperty.call(P.perQm, oa)) return;
      var card = document.querySelector('.rw-rechner-leistung-card[data-objektart="' + oa + '"]');
      if (!card) return;
      window.rwSelectObjektart(card);
      if (!vomKlick) return;
      var anchor = document.getElementById('rw-steps');
      if (anchor) requestAnimationFrame(function() {
        window.scrollTo({ top: anchor.getBoundingClientRect().top + window.scrollY - 90, behavior: 'smooth' });
      });
    } catch(e) {}
  })();

})();
