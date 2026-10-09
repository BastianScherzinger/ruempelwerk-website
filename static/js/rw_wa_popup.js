/* WhatsApp-Popup. Gehoert zu components/rw_wa_popup.html.

   Ausgelagert am 26.08.2026 (Befund W4): der Block lag inline auf jeder
   Seite und war damit nie cachebar. */
(function(){
  var popup = document.getElementById('rw-wa-popup');
  if (!popup) return;

  // Nicht auf rechtlichen/internen Seiten anzeigen.
  // Der interne Bereich meldet sich ueber <html data-rw-no-consent> ab – der
  // fruehere Test auf /stats/ konnte nie greifen, weil der Pfad aus STATS_PATH
  // kommt und geheim bleibt (siehe components/rw_cookie_banner.html).
  var p = window.location.pathname;
  if (document.documentElement.hasAttribute('data-rw-no-consent')) return;
  if (/^\/admin(\/|$)/.test(p) || /^\/(impressum|datenschutz|agb)\/$/.test(p)) return;

  var closeBtn = document.getElementById('rw-wa-popup-close');
  var minBtn = document.getElementById('rw-wa-popup-min');
  var launcher = document.getElementById('rw-wa-launcher');
  var cta = document.getElementById('rw-wa-popup-cta');
  var KEY = 'rw_wa_popup_seen';
  var DELAY = 10000;
  var timer, armed = false;

  // Pro Sitzung nur einmal: nach „×" oder Absenden nicht mehr automatisch zeigen
  try { if (sessionStorage.getItem(KEY)) return; } catch(e){}

  function dismiss(){
    popup.classList.remove('rw-wa-popup--show');
    launcher.classList.remove('rw-wa-launcher--show');
    document.body.classList.remove('rw-wa-open');
    try { sessionStorage.setItem(KEY, '1'); } catch(e){}
    document.removeEventListener('keydown', onKey);
    setTimeout(function(){ popup.hidden = true; launcher.hidden = true; }, 260);
  }
  function onKey(e){ if (e.key === 'Escape') { if (!popup.hidden && popup.classList.contains('rw-wa-popup--show')) minimize(); } }

  function zeigeJetzt(){
    launcher.classList.remove('rw-wa-launcher--show');
    setTimeout(function(){ launcher.hidden = true; }, 200);
    popup.hidden = false;
    // doppelter rAF, damit die Eintritts-Transition greift
    requestAnimationFrame(function(){ requestAnimationFrame(function(){
      popup.classList.add('rw-wa-popup--show');
      document.body.classList.add('rw-wa-open');  // blendet die Floating-Buttons aus
    }); });
    document.addEventListener('keydown', onKey);
  }

  // Minimieren → Chat aus, Launcher-Blase ein (wieder öffenbar)
  function minimize(){
    popup.classList.remove('rw-wa-popup--show');
    setTimeout(function(){ popup.hidden = true; }, 260);
    launcher.hidden = false;
    requestAnimationFrame(function(){ requestAnimationFrame(function(){
      launcher.classList.add('rw-wa-launcher--show');
    }); });
    document.body.classList.add('rw-wa-open'); // FABs bleiben aus, Launcher ist der Zugang
  }

  closeBtn.addEventListener('click', dismiss);
  minBtn.addEventListener('click', minimize);
  launcher.addEventListener('click', zeigeJetzt);
  cta.addEventListener('click', function(){ try { sessionStorage.setItem(KEY,'1'); } catch(e){} });

  // Steht der Consent-Banner noch auf dem Schirm? Er ist fixed am unteren
  // Rand mit z-index 9500, das Popup sitzt mit 9000 in derselben Ecke –
  // beide gleichzeitig heisst: Der Banner schneidet den Chat an, und der
  // WhatsApp-Knopf liegt halb darunter.
  //
  // Geprueft wird ausschliesslich das hidden-Attribut. Das ist Absicht:
  //   * rw-cc--show scheidet aus – die Klasse setzt der Banner per doppeltem
  //     requestAnimationFrame, und rAF laeuft in einem Hintergrund-Tab nicht.
  //   * getBoundingClientRect() scheidet ebenfalls aus – im Hintergrund-Tab
  //     ist innerWidth 0 und das Layout eines fixed/left:0/right:0-Elements
  //     kollabiert auf 0 Hoehe. Nachgemessen: Der Chat kam so trotzdem hoch.
  // hidden dagegen faellt synchron in show() weg und wird in hide() gesetzt.
  function bannerOffen(){
    var cc = document.getElementById('rw-cc');
    return !!cc && !cc.hidden;
  }

  function show(){
    // Nicht vordraengeln: Solange der Banner offen ist, spaeter erneut versuchen.
    if (bannerOffen()) { timer = setTimeout(show, 3000); return; }
    // Handy (<= 768 px): nicht von selbst aufklappen – das Fenster deckte dort
    // 41–46 % des Bildschirms ab, auch das Terminbuch. Nur die Blase zeigen;
    // Tippen oeffnet den Chat wie gewohnt (01.10.2026).
    if (window.matchMedia && window.matchMedia('(max-width: 768px)').matches) { minimize(); return; }
    zeigeJetzt();
  }

  function arm(){ if (armed) return; armed = true; timer = setTimeout(show, DELAY); }

  // Erst nach der Cookie-Entscheidung starten, damit das Popup den Banner nicht überdeckt
  if (/(?:^|;\s*)rw_consent=/.test(document.cookie)) {
    arm();
  } else {
    window.addEventListener('rw:consent', arm, {once:true});
    // Fallback, falls (aus welchem Grund auch immer) keine Entscheidung kommt.
    // Frueher armierte er blind nach 20 s: Wer den Banner offen liegen liess –
    // beim Lesen des Textes reichen 30 s locker – bekam das Chatfenster quer
    // ueber den Banner gelegt. Deshalb nur armieren, wenn der Banner weg ist;
    // ansonsten weiter auf die Entscheidung warten (show() prueft zusaetzlich).
    setTimeout(function(){ if (!bannerOffen()) arm(); }, 20000);
  }
})();
