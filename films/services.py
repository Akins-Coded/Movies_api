from django.conf import settings
from django.core.cache import cache
import requests
from datetime import datetime


SWAPI_FILMS_CACHE_KEY = "swapi_films_all"
SWAPI_TTL_SECONDS = 60 * 60 * 6 # 6 hours

def _swapi_get(path: str):
    url = f"{settings.SWAPI_BASE_URL}{path}"
    resp = requests.get(url, timeout=20)
    if not resp.ok:
        raise requests.HTTPError(f"SWAPI error {resp.status_code}: {resp.text}")
    return resp.json()




def list_films():
    """
    Fetch all films from SWAPI, cache, and return a list of dicts with
    id, title, release_date (date),
    plus pass-through of entire item.
    """
    data = cache.get(SWAPI_FILMS_CACHE_KEY)
    if not data:
    # SWAPI films isn't paginated (6 films), but implement defensively
        page = _swapi_get("/films/")
        results = page.get("results", [])
        data = []
        for item in results:
        # Extract numeric id from URL like https://swapi.dev/api/films/1/
            url = item.get("url", "")
            try:
                film_id = int(url.strip("/").split("/")[-1])
            except Exception:
                continue
            release_date_str = item.get("release_date")
            release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()
            data.append({
                "id": film_id,
                "title": item.get("title"),
                "release_date": release_date,
                "_raw": item,
            })
        cache.set(SWAPI_FILMS_CACHE_KEY, data, SWAPI_TTL_SECONDS)
    return data




def film_exists(film_id: int) -> bool:
    films = list_films()
    return any(f["id"] == film_id for f in films)