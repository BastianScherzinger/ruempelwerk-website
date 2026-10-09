/* Basis-JS jeder oeffentlichen Seite: Tracking (rwTrack), Navigation,
   Reveal, Count-Up, Ausklapp-Mechaniken.
   Gehoert zu components/rw_js.html. Die Conversion-Labels kommen weiter
   als <script type="application/json" id="rw-ads-labels"> aus dem Template -
   sie haengen an einer Env-Variablen und koennen nicht statisch sein.

   Ausgelagert am 26.08.2026 (Befund W4): der Block lag inline auf jeder
   Seite und war damit nie cachebar. */
// ── Geschätzte Lead-Werte (EUR) je Conversion – HIER ANPASSEN ──
// Durchschnittlicher Auftragswert je echter Anfrage; für GA-ROI-Schätzung.
// angebot_email bekommt den real berechneten Preis dynamisch (überschreibt diesen Wert).
window.RW_LEAD_VALUES = {
  anfrage_submit: 650,   // geschätzter Ø-Auftragswert je Anfrage
  angebot_email:  650    // Fallback, falls kein berechneter Preis vorliegt
};

// ── Google-Ads-Conversion-Labels (leer, solange keine Env-Variable gesetzt ist) ──
var RW_ADS_LABELS = (function(){
  try {
    var el = document.getElementById('rw-ads-labels');
    return el ? JSON.parse(el.textContent) : {};
  } catch(e){ return {}; }
})();

// ── ChatGPT Ads: welches unserer Ereignisse als was gemeldet wird ──
// Bewusst dieselben vier wie bei Google Ads. `scroll_depth` und
// `rechner_start` stehen auch hier nicht drin: Nebensignale als Conversion zu
// zaehlen war der Fehler, der das alte Google-Konto 564 EUR gekostet hat, und
// er wird auf einer neuen Plattform nicht dadurch besser, dass sie neu ist.
//
// `lead_created` ist ein Standardereignis von OpenAI und traegt die Datenform
// `customer_action`; fuer Anruf und WhatsApp gibt es keins, sie gehen als
// eigenes Ereignis unter demselben Namen raus, den auch GA4 kennt.
var RW_OAI_EVENTS = {
  anfrage_submit: { ereignis: 'lead_created', typ: 'customer_action' },
  angebot_email:  { ereignis: 'lead_created', typ: 'customer_action' },
  call_click:     { eigen: true },
  whatsapp_click: { eigen: true },
  termin_gebucht: { ereignis: 'lead_created', typ: 'customer_action' }
};

// ── Google-Analytics Conversion-Events (feuern nur bei erteilter Einwilligung) ──
window.rwTrack = function(name, params){
  try {
    params = params || {};
    if (params.value == null && window.RW_LEAD_VALUES && window.RW_LEAD_VALUES[name] != null) {
      params.value = window.RW_LEAD_VALUES[name];
    }
    if (params.value != null && !params.currency) params.currency = 'EUR';
    // ChatGPT Ads zuerst, und ausdruecklich **vor** dem Ausstieg unten:
    // Beide Kanaele haengen an derselben Einwilligung, aber an verschiedenen
    // Skripten. Stuende die Meldung hinter `return`, verschwaende ein
    // ausgefallenes oder abgeschaltetes gtag.js den zweiten Kanal gleich mit -
    // still, ohne Fehler, und niemandem faellt es auf. Genau diese Sorte
    // stiller Kopplung hat auf dieser Seite schon einmal Monate gekostet
    // (Analytics auf 54 Stadtseiten, bis zum 19.08.2026).
    if (window.rwTrackOaiq) window.rwTrackOaiq(name, params);
    if (!(window.__rwGtagLoaded && typeof window.gtag === 'function')) return;
    // Der Hash gehoert zu Google Ads, nicht in die GA4-Ereignisparameter -
    // dort waere er ein Feld, das niemand auswertet und das in jedem Export
    // mitlaeuft.
    var ga = {};
    for (var k in params) if (k !== 'user_data_hash') ga[k] = params[k];
    window.gtag('event', name, ga);
    // Dieselbe Aktion zusaetzlich an Google Ads melden – aber nur die vier
    // Ereignisse mit hinterlegtem Label (Anfrage, Angebot, Anruf, WhatsApp).
    // scroll_depth und rechner_start haben bewusst keins: Genau solche
    // Nebensignale als Conversion zu zaehlen, hat das Konto bisher auf
    // "Seitenaufruf" und "Engagement" optimieren lassen.
    //
    // Die Einwilligungspruefung oben deckt beides ab – gtag.js ist erst
    // geladen, wenn ad_storage auf 'granted' steht.
    if (window.rwAdsId && RW_ADS_LABELS[name]) {
      // Erweiterte Conversions: die gehashte Kennung geht als `user_data`
      // mit, BEVOR das Conversion-Ereignis rausgeht - danach ignoriert gtag
      // sie fuer diese Conversion. Sie holt Messungen zurueck, die an
      // Browser-Beschraenkungen verloren gehen. Ohne Hash bleibt alles wie
      // bisher; der Aufruf entfaellt dann ganz.
      if (params.user_data_hash) {
        window.gtag('set', 'user_data', { sha256_email_address: params.user_data_hash });
      }
      var conv = { 'send_to': window.rwAdsId + '/' + RW_ADS_LABELS[name] };
      if (params.value != null) {
        conv.value = params.value;
        conv.currency = params.currency || 'EUR';
      }
      window.gtag('event', 'conversion', conv);
    }
  } catch(e){}
};

// ── Dieselbe Aktion an ChatGPT Ads melden ───────────────────────────────────
// `__rwOaiqLoaded` setzt rw_seo.html erst nach `rw_consent=all` - die Pruefung
// ist damit dieselbe Einwilligung wie bei Google, nur fuer den zweiten Kanal.
// Ohne OPENAI_PIXEL_ID passiert hier nichts.
//
// ⚠ `amount` ist bei OpenAI die **kleinste Waehrungseinheit**: Die Doku zeigt
// `amount: 2599` fuer 25,99 USD. Unsere Werte stehen in Euro (RW_LEAD_VALUES,
// und der Preisrechner reicht den gerechneten Preis durch). Ohne das *100 waere
// ein Lead von 650 EUR im Konto als 6,50 EUR verbucht - eine Zahl, die
// plausibel genug aussieht, um nicht aufzufallen, und die jede spaetere
// Kosten-Nutzen-Rechnung verdirbt.
//
// Was diese Funktion NICHT kann: Sie prueft nicht, ob das Ereignis im Konto
// ueberhaupt angelegt und mit der Kampagne verknuepft ist. Ein Name, den die
// Datenquelle nicht kennt, geht hier fehlerfrei raus und taucht dort nie auf.
window.rwTrackOaiq = function(name, params){
  try {
    if (!(window.__rwOaiqLoaded && typeof window.oaiq === 'function')) return;
    var oai = RW_OAI_EVENTS[name];
    if (!oai) return;
    var daten = { type: oai.eigen ? 'custom' : oai.typ };
    if (params && params.value != null) {
      daten.amount = Math.round(params.value * 100);
      daten.currency = params.currency || 'EUR';
    }
    if (oai.eigen) {
      window.oaiq('measure', 'custom', daten, { custom_event_name: name });
    } else {
      window.oaiq('measure', oai.ereignis, daten);
    }
  } catch(e){}
};
(function(){
  // WhatsApp- und Telefon-Klicks global erfassen
  document.addEventListener('click', function(e){
    var a = e.target.closest ? e.target.closest('a') : null;
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (href.indexOf('wa.me') !== -1 || href.indexOf('api.whatsapp.com') !== -1) {
      window.rwTrack('whatsapp_click', { page: location.pathname });
    } else if (href.indexOf('tel:') === 0) {
      window.rwTrack('call_click', { page: location.pathname });
    }
  }, true);
  // Anfrage erfolgreich abgesendet.
  //
  // **Frueher haderte das an `.rw-alert-success`** - und die zeigt die Seite
  // absichtlich auch dann, wenn die Spam-Abwehr die Einsendung verworfen oder
  // die Duplikatsperre gegriffen hat (ein Bot, der eine Fehlerseite saehe,
  // wuerde variieren, bis er durchkommt). Google haette also Bots als Leads
  // gezaehlt. Jetzt haengt es an einer Kennung, die die View **nur nach
  // `form.save()`** in die Session legt.
  //
  // Die Kennung ist zugleich die Grundlage der erweiterten Conversions: der
  // SHA-256 der normalisierten E-Mail, in Python gerechnet - die
  // Klartext-Adresse erreicht das HTML nie.
  (function(){
    var el = document.getElementById('rw-lead-kennung');
    if (!el) return;
    var hash = '';
    try { hash = JSON.parse(el.textContent) || ''; } catch(e){}
    window.rwTrack('anfrage_submit', { page: location.pathname, user_data_hash: hash });
  })();
  // Besichtigung gebucht (KV07): dieselbe Technik wie die Anfrage - das Element
  // steht nur nach einer wirklich gespeicherten Buchung im HTML (View setzt die
  // Session-Kennung erst nach dem Speichern, nur mit TERMIN_CONVERSION). Kein
  // Wert und kein E-Mail-Hash: beides ist in der Datenschutzerklaerung nur fuer
  // Anfrage und Angebot genannt.
  if (document.getElementById('rw-termin-gebucht')) {
    window.rwTrack('termin_gebucht', { page: location.pathname });
  }
  // Scroll-Tiefe: 25 / 50 / 75 / 90 % – je einmal pro Seitenaufruf
  // scrollHeight/innerHeight direkt im Scroll-Handler zu lesen erzwingt ein
  // Layout, sobald sich davor etwas am DOM geaendert hat (Lazy-Bilder,
  // Reveal-Klassen) – das war der Rest des "erzwungenen dynamischen
  // Umbruchs" im Lighthouse-Report. Jetzt wird die Seitenhoehe gecacht und
  // die Auswertung in requestAnimationFrame gebuendelt: gelesen wird dann,
  // wenn der Browser das Layout ohnehin frisch hat.
  var marks = [25, 50, 75, 90], fired = {}, scrollable = -1, ticking = false;
  function measure(){
    var doc = document.documentElement;
    scrollable = doc.scrollHeight - window.innerHeight;
  }
  function evaluate(){
    ticking = false;
    if (scrollable < 0) measure();
    if (scrollable <= 0) return;
    var pct = (window.scrollY || document.documentElement.scrollTop) / scrollable * 100;
    for (var i = 0; i < marks.length; i++) {
      if (pct >= marks[i] && !fired[marks[i]]) {
        fired[marks[i]] = true;
        window.rwTrack('scroll_depth', { percent: marks[i], page: location.pathname });
      }
    }
    if (fired[90]) window.removeEventListener('scroll', onScroll);
  }
  function onScroll(){
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(evaluate);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  // Hoehe neu bestimmen, wenn sie sich geaendert haben kann.
  window.addEventListener('resize', function(){ scrollable = -1; }, { passive: true });
  // Bewusst KEIN measure() auf 'load': Genau dort sind gerade die Lazy-Bilder
  // eingetroffen, das Layout ist schmutzig, und scrollHeight zu lesen erzwang
  // laut Lighthouse 134 ms Layout am Stueck (der groesste Posten unter
  // "Erzwungener dynamischer Umbruch" – und Hauptthread-Zeit zaehlt in den
  // TBT-Wert). Gemessen wird jetzt erst beim ersten Scrollen, in evaluate():
  // dort ist das Layout frisch, weil der Browser fuer das Scrollen selbst
  // gerade eines gerechnet hat. Wer nicht scrollt, hat auch keine Scrolltiefe.
})();

const nav = document.getElementById('rw-nav');
window.addEventListener('scroll', () => nav.classList.toggle('scrolled', scrollY > 20), {passive:true});

// ── Bottom nav active state ──────────────────
(function setBottomNavActive() {
  var path = window.location.pathname;
  document.querySelectorAll('.rw-bottom-nav-item').forEach(function(item) {
    var p = item.dataset.path || item.getAttribute('href');
    if (p && (path === p || (p !== '/' && path.startsWith(p)))) {
      item.classList.add('active');
    }
  });
})();

const burger = document.getElementById('rw-burger');
const mobileMenu = document.getElementById('rw-mobile-menu');
burger.addEventListener('click', () => {
  const open = mobileMenu.classList.toggle('open');
  burger.classList.toggle('active', open);
  burger.setAttribute('aria-expanded', open);
});
mobileMenu.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => {
    mobileMenu.classList.remove('open');
    burger.classList.remove('active');
    burger.setAttribute('aria-expanded', 'false');
  });
});
document.addEventListener('click', (e) => {
  if (!mobileMenu.contains(e.target) && !burger.contains(e.target) && mobileMenu.classList.contains('open')) {
    mobileMenu.classList.remove('open');
    burger.classList.remove('active');
    burger.setAttribute('aria-expanded', 'false');
  }
});

document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const id = a.getAttribute('href').slice(1);
    if (!id) return;
    const el = document.getElementById(id);
    if (el) { e.preventDefault(); el.scrollIntoView({behavior:'smooth', block:'start'}); }
  });
});

const reveals = document.querySelectorAll('[data-rw-reveal]');
const ro = new IntersectionObserver(entries => {
  entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add('visible'); ro.unobserve(en.target); } });
}, {threshold: 0.1, rootMargin: '0px 0px -40px 0px'});
reveals.forEach(el => ro.observe(el));

// ── Mobile: prozess scroll dots ──────────────────
(function(){
  var steps = document.querySelector('.rw-prozess-steps');
  var dots  = document.querySelectorAll('.rw-prozess-scroll-dot');
  if(!steps || !dots.length) return;
  // scrollWidth/clientWidth aendern sich nur beim Umbruch – einmal messen
  // statt bei jedem Scroll-Event (sonst: erzwungenes Layout pro Event).
  var range = -1, last = -1;
  window.addEventListener('resize', function(){ range = -1; }, {passive:true});
  steps.addEventListener('scroll', function(){
    if (range < 0) range = steps.scrollWidth - steps.clientWidth;
    var idx = range > 0 ? Math.round(steps.scrollLeft / range * (dots.length - 1)) : 0;
    if (idx === last) return;              // nichts zu tun -> kein DOM-Schreiben
    last = idx;
    dots.forEach(function(d,i){ d.style.background = i===idx ? 'var(--rw-orange)' : ''; });
  }, {passive:true});
})();

// ── Stats: Count-Up beim Sichtbarwerden (einmalig) ──
(function(){
  var nums = document.querySelectorAll('[data-rw-countup]');
  if (!nums.length) return;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function run(el){
    var target = parseInt(el.getAttribute('data-rw-countup'), 10) || 0;
    if (reduce) { el.textContent = target; return; }
    var dur = 1400, start = null;
    function step(ts){
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3); // easeOutCubic
      el.textContent = Math.round(eased * target);
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = target;
    }
    requestAnimationFrame(step);
  }
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      if (en.isIntersecting) { run(en.target); io.unobserve(en.target); }
    });
  }, {threshold: 0.4});
  nums.forEach(function(el){ io.observe(el); });
})();

// ── Layout-Messungen aus dem kritischen Pfad nehmen ──────────────────
// scrollHeight/clientHeight zu lesen erzwingt immer ein Layout. Direkt beim
// Seitenaufbau kostete das ~126 ms Hauptthread-Zeit ("Erzwungener dynamischer
// Umbruch" im Lighthouse-Report). Die Messungen sind fuer die erste Anzeige
// nicht noetig - sie entscheiden nur, ob ein "Mehr lesen"-Button erscheint.
// Deshalb laufen sie erst, wenn der Browser Leerlauf hat.
function rwWhenIdle(fn){
  if ('requestIdleCallback' in window) { requestIdleCallback(fn, { timeout: 2000 }); }
  else { setTimeout(fn, 1); }
}

// ── Ausklapp-Mechaniken: EIN gemeinsamer Messlauf ────────────────────
// Aktuelles-Karten, Google-Reviews und generische Absaetze klappen alle drei
// lange Texte auf. Frueher hatte jede ihren eigenen Idle-Callback – die
// laufen aber in derselben Leerlaufphase direkt hintereinander, also machte
// die Schreibphase der einen das Layout fuer die Lesephase der naechsten
// ungueltig. Genau dieses Muster meldet Lighthouse als "erzwungenen
// dynamischen Umbruch". Jetzt gilt strikt: erst alles messen, dann alles
// schreiben – ein Layout fuer die ganze Seite.
rwWhenIdle(function(){
  // ── 1. Lesephase – ab hier bis zur Markierung nichts ins DOM schreiben ──

  // (a) Aktuelles: die Klemm-Klasse steht schon im Markup, also direkt messen
  var newsPairs = [];
  document.querySelectorAll('[data-rw-clamp]').forEach(function(el){
    var btn = el.nextElementSibling;
    if (!btn || !btn.classList.contains('rw-news-toggle')) return;
    newsPairs.push([el, btn]);
  });
  var newsCut = newsPairs.map(function(p){ return p[0].scrollHeight - p[0].clientHeight > 4; });

  // (b/c) Reviews und Absaetze sind noch UNgeklemmt. Erst die Klasse setzen
  // und dann scrollHeight lesen waere wieder Schreiben-vor-Lesen. Deshalb
  // wird die natuerliche Hoehe mit der Hoehe verglichen, die die Klasse
  // zulassen wuerde: Zeilenhoehe x -webkit-line-clamp.
  function overflows(el, lines){
    var cs = getComputedStyle(el);
    var lh = parseFloat(cs.lineHeight);
    if (!lh) lh = (parseFloat(cs.fontSize) || 16) * 1.7;   // line-height: normal
    return el.getBoundingClientRect().height > lh * lines + 1;
  }
  // Die Zeilenzahlen muessen zu ruempelwerk.css passen
  // (.rw-review-text--clamp = 5, .rw-readmore-clamp = 4).
  var reviews = Array.prototype.slice.call(document.querySelectorAll('.rw-review-text'));
  var reviewCut = reviews.map(function(t){ return overflows(t, 5); });
  var paras = Array.prototype.slice.call(document.querySelectorAll('[data-rw-readmore]'));
  var paraCut = paras.map(function(el){ return overflows(el, 4); });

  // ── 2. Schreibphase ────────────────────────────────────────────────────

  newsPairs.forEach(function(p, i){
    if (!newsCut[i]) return;
    var el = p[0], btn = p[1];
    btn.hidden = false;
    btn.addEventListener('click', function(){
      var open = el.classList.toggle('rw-clamp--open');
      btn.textContent = open ? 'Weniger anzeigen' : 'Mehr lesen';
    });
  });

  // Inhalt der Mehr-lesen-Knoepfe als Elemente (S05, 17.09.2026) - dasselbe
  // Markup wie vorher: <span class="…-ico">+</span><span class="…-txt">…</span>.
  function rwKnopfInhalt(btn, praefix){
    var ico = document.createElement('span');
    ico.className = praefix + '-ico';
    ico.setAttribute('aria-hidden', 'true');
    ico.textContent = '+';
    var txt = document.createElement('span');
    txt.className = praefix + '-txt';
    txt.textContent = 'Mehr lesen';
    btn.appendChild(ico);
    btn.appendChild(txt);
  }

  reviews.forEach(function(t, idx){
    // Nur klemmen und einen Toggle anbieten, wenn der Text wirklich laenger ist
    if (!reviewCut[idx]) return;
    t.classList.add('rw-review-text--clamp');
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'rw-review-more';
    btn.setAttribute('aria-expanded', 'false');
    rwKnopfInhalt(btn, 'rw-review-more');
    btn.addEventListener('click', function(e){
      e.stopPropagation();   // nicht zur klickbaren Karte/Maps-Link durchreichen
      var open = t.classList.toggle('rw-review-text--open');
      btn.setAttribute('aria-expanded', String(open));
      btn.querySelector('.rw-review-more-ico').textContent = open ? '–' : '+';
      btn.querySelector('.rw-review-more-txt').textContent = open ? 'Weniger anzeigen' : 'Mehr lesen';
    });
    t.insertAdjacentElement('afterend', btn);
  });

  paras.forEach(function(el, idx){
    if (!paraCut[idx]) return;
    el.classList.add('rw-readmore-clamp');
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'rw-readmore-btn';
    btn.setAttribute('aria-expanded', 'false');
    rwKnopfInhalt(btn, 'rw-readmore');
    btn.addEventListener('click', function(){
      var open = el.classList.toggle('rw-readmore-open');
      btn.setAttribute('aria-expanded', String(open));
      btn.querySelector('.rw-readmore-ico').textContent = open ? '–' : '+';
      btn.querySelector('.rw-readmore-txt').textContent = open ? 'Weniger anzeigen' : 'Mehr lesen';
    });
    el.insertAdjacentElement('afterend', btn);
  });
});

// ── Reviews: ganze Karte klickbar → Google Maps ──
(function(){
  var MAPS = 'https://www.google.com/maps/place/R%C3%BCmpelwerk+Mitteldeutschland/@51.4702609,11.9652634,17z/data=!3m1!4b1!4m6!3m5!1s0x9d602ed74663a1:0xa6928b3e0473aca8!8m2!3d51.4702576!4d11.9678383!16s%2Fg%2F11nq1wtp7b';
  document.querySelectorAll('.rw-review-card').forEach(function(card){
    if (card.querySelector('.rw-review-link')) return;
    var nameEl = card.querySelector('.rw-review-name');
    var name = nameEl ? nameEl.textContent.trim() : 'Kunde';
    var a = document.createElement('a');
    a.className = 'rw-review-link';
    a.href = MAPS; a.target = '_blank'; a.rel = 'noopener';
    a.setAttribute('aria-label', 'Bewertung von ' + name + ' auf Google ansehen');
    card.appendChild(a);
  });
})();

// (Die generischen „Mehr lesen"-Absaetze [data-rw-readmore] werden oben im
//  gemeinsamen Messlauf mitbehandelt – siehe Schreibphase (c).)
