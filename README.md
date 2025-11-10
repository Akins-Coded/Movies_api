# Movies_api
# Films API (Django + DRF + SWAPI) with Comments and PythonAnywhere CD
- Deploys to PythonAnywhere with Continuous Deployment from GitHub.


## Endpoints
- `GET /api/films/` — list films with comment counts (sorted by release_date ↑)
- `GET /api/films/{film_id}/comments/` — list comments (ascending by `created_at`)
- `POST /api/films/{film_id}/comments/` — add comment `{ "body": "...<=500 chars..." }`
- Swagger UIs: `/swagger/` and `/redoc/`


## Local setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # and adjust values
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```


## Notes
- Films are **not stored** locally. They are fetched from SWAPI and **cached** (6 hours) to reduce network calls.
- Comments are stored locally in the database and keyed by SWAPI film ID.
- Return shapes and validation follow REST best practices; errors use RFC7807-like `{"detail": ...}` for 404 and a field map for 400 validation errors.


## Testing quickly with curl
```bash
curl -s http://127.0.0.1:8000/api/films/ | jq
curl -s -X POST http://127.0.0.1:8000/api/films/1/comments/ -H 'Content-Type: application/json' -d '{"body":"Hello there"}' | jq
curl -s http://127.0.0.1:8000/api/films/1/comments/ | jq
```


## Deploy to PythonAnywhere
### One-time setup on PythonAnywhere
1. Create a new **Web app** (Manual configuration). Choose Python 3.x.
2. On the server, clone your repo:
```bash
git clone https://github.com/<you>/<repo>.git
cd <repo>
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```
3. In the PythonAnywhere Web tab:
- **WSGI file** should point to `movies_api.wsgi`:
```python
import os, sys
path = '/home/<username>/<repo>'
if path not in sys.path:
sys.path.append(path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movies_api.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```
- Set environment variables under **Environment** (SECRET_KEY, DEBUG, ALLOWED_HOSTS, etc.)
- Set **Static files**: URL `/static/` → `/home/<username>/<repo>/staticfiles`
- Click **Reload**.


### Continuous Deployment from GitHub (Actions → SSH pull + reload)
This workflow SSHes into PythonAnywhere, pulls latest code, installs deps, migrates, collects static, then reloads.


- Add GitHub repository **secrets**:
- `PA_SSH_HOST` (usually `ssh.pythonanywhere.com`)
- `PA_USERNAME` (your PythonAnywhere username)
- `PA_SSH_KEY` (a private key with its public key added to your PythonAnywhere account)
- `PA_SITE_DOMAIN` (e.g., `<username>.pythonanywhere.com`)
- `PA_APP_DIR` (absolute path, e.g., `/home/<username>/<repo>`)
- `PA_VENV` (absolute path to venv, e.g., `/home/<username>/<repo>/.venv`)


- Ensure the corresponding **public key** is added under PythonAnywhere → Account → SSH keys.


# .github/workflows/deploy.yml
name: Deploy to PythonAnywhere


on: