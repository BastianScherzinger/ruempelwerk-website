# Rümpelwerk Mitteldeutschland – Website

Django-Website von Rümpelwerk Mitteldeutschland.

## Lokal starten

```bash
python -m venv .venv
.venv/Scripts/activate        # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # Werte eintragen
python manage.py migrate
python manage.py createcachetable rw_cache
python manage.py runserver
```

## Betrieb

`Procfile` / `railway.json` starten `start.sh` (Migrationen, Cache-Tabelle,
CSS, `collectstatic`, Google-Bewertungen, gunicorn). Benötigte Umgebungs-
variablen stehen in `.env.example` und `config/settings.py`
(u. a. `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`,
Mailzugang, `ADMIN_EMAIL`, optional `GOOGLE_PLACES_API_KEY`, `CLOUDINARY_URL`).
