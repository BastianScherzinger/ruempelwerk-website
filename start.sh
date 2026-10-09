#!/bin/sh
set -e

echo ">>> [1/7] Migrations..."
python manage.py migrate --no-input

# Tabelle fuer den DatabaseCache. Traegt die Rate-Limit-Zaehler und das
# Mail-Budget der Spam-Abwehr, die beide ueber Worker- und Deploy-Grenzen
# hinweg halten muessen (siehe apps/core/antispam.py). Der Command ist
# idempotent: Existiert die Tabelle schon, meldet er das und tut nichts.
echo ">>> [2/7] Cache-Tabelle sicherstellen..."
python manage.py createcachetable rw_cache

# Inline-CSS fuer den Seitenkopf neu erzeugen, BEVOR minifiziert wird (danach
# fehlen die Kommentare, die den Aufbau lesbar halten). Der Schritt ist
# selbstheilend: sollte jemand ruempelwerk.css aendern und den Command lokal
# vergessen, passt das Ergebnis nach dem Deploy trotzdem. Faellt er aus,
# greift die eingecheckte Fassung.
echo ">>> [3/7] Critical CSS bauen..."
python manage.py build_critical_css || echo "    (uebersprungen - eingecheckte Fassung wird benutzt)"

# CSS verkleinern, BEVOR collectstatic hasht und komprimiert. Greift nur auf
# die Container-Kopie zu; die lesbare Fassung im Repo bleibt unveraendert.
# Schlaegt der Schritt fehl, laeuft das Deployment mit unminifiziertem CSS
# weiter - eine langsamere Seite ist besser als gar keine.
echo ">>> [4/7] CSS minifizieren..."
python manage.py minify_css || echo "    (uebersprungen)"

echo ">>> [5/7] Collectstatic..."
python manage.py collectstatic --no-input

# Google-Bewertungen einmal abgleichen. Sonst laeuft der erste Abgleich erst um
# Mitternacht, und bis dahin zeigt eine frische Datenbank die uebernommene
# Liste statt des aktuellen Stands. Ohne GOOGLE_PLACES_API_KEY tut der Command
# nichts und meldet das; faellt er aus, bleibt der letzte bekannte Stand
# stehen. Wie die CSS-Schritte bewusst weich - ein Ausfall bei Google ist kein
# Grund, ein Deployment abzubrechen.
echo ">>> [6/7] Google-Bewertungen abgleichen..."
python manage.py sync_google_reviews || echo "    (uebersprungen - bisheriger Stand bleibt)"

echo ">>> [7/7] Starting gunicorn on port ${PORT:-8000}..."
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --timeout 120 \
    --log-file - \
    --access-logfile -
