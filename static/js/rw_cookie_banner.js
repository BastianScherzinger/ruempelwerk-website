/* Cookie-Consent-Banner (DSGVO, Consent Mode v2).
   Gehoert zu components/rw_cookie_banner.html. Der Consent-*Bootstrap*
   (gtag, rwLoadGtag) steht bewusst NICHT hier, sondern inline in
   components/rw_seo.html - er muss vor allem anderen laufen.

   Ausgelagert am 26.08.2026 (Befund W4): der Block lag inline auf jeder
   Seite und war damit nie cachebar. */
(function(){
  var el = document.getElementById('rw-cc');
  if (!el) return;

  // Auf internen Seiten kein Banner-Popup nötig – dort läuft kein Tracking.
  //
  // Frueher stand hier /^\/(stats|admin)(\/|$)/. Das hat nie gegriffen: Der
  // interne Bereich liegt unter dem GEHEIMEN Pfad aus STATS_PATH, und dort
  // folgt hinter „stats“ noch ein Bindestrich statt „/“ oder Zeilenende.
  // Der Banner erschien deshalb mitten im CMS.
  //
  // Der geheime Pfad darf hier NICHT eingesetzt werden: Diese Datei wird auf
  // jeder oeffentlichen Seite ausgeliefert und wuerde ihn an jeden Besucher
  // verraten – genau das, was das Weglassen in robots.txt verhindern soll.
  // Stattdessen meldet sich eine interne Seite selbst ab, per Attribut am
  // <html>-Element: <html lang="de" data-rw-no-consent>.
  var SKIP = document.documentElement.hasAttribute('data-rw-no-consent')
          || /^\/admin(\/|$)/.test(window.location.pathname);

  var KEY = 'rw_consent';
  var detail = document.getElementById('rw-cc-detail');
  var statBox = document.getElementById('rw-cc-stat');
  var btnSettings = document.getElementById('rw-cc-settings');
  var btnNecessary = document.getElementById('rw-cc-necessary');
  var btnAccept = document.getElementById('rw-cc-accept');
  var btnSave = document.getElementById('rw-cc-save');

  function getConsent(){
    var m = document.cookie.match(/(?:^|;\s*)rw_consent=([^;]+)/);
    return m ? m[1] : null;
  }
  function setCookie(val){
    var secure = location.protocol === 'https:' ? '; Secure' : '';
    document.cookie = KEY + '=' + val + '; path=/; max-age=' + (60*60*24*180) + '; SameSite=Lax' + secure;
  }
  function grantAnalytics(){
    try {
      if (window.gtag) {
        gtag('consent', 'update', {
          'ad_storage':'granted','analytics_storage':'granted',
          'ad_user_data':'granted','ad_personalization':'granted'
        });
      }
      if (window.rwLoadGtag) window.rwLoadGtag();
      // ChatGPT Ads: dieselbe Einwilligung, dieselbe Stelle. Beide Loader sind
      // gegen Mehrfachaufrufe geschuetzt.
      if (window.rwLoadOaiq) window.rwLoadOaiq();
    } catch(e){}
  }
  function resolve(val){
    setCookie(val);
    if (val === 'all') grantAnalytics();
    hide();
    try { window.dispatchEvent(new CustomEvent('rw:consent', {detail:{value:val}})); } catch(e){}
  }
  function show(){
    el.hidden = false;
    requestAnimationFrame(function(){ requestAnimationFrame(function(){ el.classList.add('rw-cc--show'); }); });
  }
  function hide(){
    el.classList.remove('rw-cc--show');
    setTimeout(function(){ el.hidden = true; }, 280);
  }
  function openSettings(){
    var open = detail.hidden;
    detail.hidden = !open;
    btnSettings.setAttribute('aria-expanded', String(open));
    btnSave.hidden = !open;
  }

  btnSettings.addEventListener('click', openSettings);
  btnNecessary.addEventListener('click', function(){ resolve('necessary'); });
  btnAccept.addEventListener('click', function(){ resolve('all'); });
  btnSave.addEventListener('click', function(){ resolve(statBox.checked ? 'all' : 'necessary'); });

  // Erneut öffnen (z. B. via Footer-Link „Cookie-Einstellungen")
  window.rwCookieReopen = function(){
    if (statBox) statBox.checked = getConsent() === 'all';
    show();
  };

  var existing = getConsent();
  if (existing) {
    // Einwilligung bereits erteilt → ggf. Analytics aktivieren, Banner nicht zeigen
    if (existing === 'all') grantAnalytics();
  } else if (!SKIP) {
    show();
  }
})();
