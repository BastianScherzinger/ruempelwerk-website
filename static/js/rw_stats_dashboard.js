/* rw_stats_dashboard.js — die Zaehleranimation der Kennzahlen im Dashboard.
 *
 * Stand bis zum 08.09.2026 als <script>-Block am Ende von
 * templates/stats/dashboard.html. Ausgelagert fuer SI09: script-src traegt
 * seitdem Hashes statt 'unsafe-inline', und jeder verbleibende Inline-Block
 * kostet einen davon. Dieser hier hatte keinen Grund, im Markup zu stehen –
 * er liest seine Zahlen ohnehin aus data-count, nicht aus dem Kontext.
 *
 * Was die Datei nicht kann: fehlende data-count-Attribute melden. Eine Kachel
 * ohne das Attribut bleibt bei ihrem gerenderten Text stehen (das ist "0"),
 * und das sieht aus wie eine gemessene Null.
 */
document.querySelectorAll('[data-count]').forEach(el => {
  const target = parseInt(el.dataset.count, 10);
  if (!target) { el.textContent = '0'; return; }
  const dur = Math.min(1200, 300 + target * 8);
  const start = performance.now();
  const tick = now => {
    const p = Math.min((now - start) / dur, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.round(ease * target);
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
});
