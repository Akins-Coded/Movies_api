from __future__ import annotations
import logging
from typing import Optional
import requests
from django.conf import settings
from django.db import transaction
from .models import Film

logger = logging.getLogger(__name__)

SWAPI_FILMS_URL = f"{settings.SWAPI_BASE_URL}/films/"


def _extract_id(url: str) -> int:
    """
    Extract the numeric ID from a SWAPI film URL, e.g.
    https://swapi.dev/api/films/1/ -> 1
    """
    return int(str(url).rstrip("/").split("/")[-1])


def fetch_and_sync_films() -> None:
    """
    Fetch films from SWAPI and upsert into the local DB in an idempotent way.
    Keeps a local cache in sync while treating SWAPI as the source of truth.

    This function:
      * Paginates through SWAPI
      * Upserts (by id) every film
      * Prunes local films not present upstream
    """
    next_url: Optional[str] = SWAPI_FILMS_URL
    seen_ids: set[int] = set()

    with transaction.atomic():
        while next_url:
            resp = requests.get(next_url, timeout=15)
            resp.raise_for_status()
            payload = resp.json()

            for f in payload.get("results", []):
                swapi_id = _extract_id(f["url"])
                seen_ids.add(swapi_id)
                Film.objects.update_or_create(
                    id=swapi_id,
                    defaults={
                        "title": f.get("title", ""),
                        "release_date": f.get("release_date"),
                    },
                )

            next_url = payload.get("next")

        # Remove stale films that no longer exist upstream
        Film.objects.exclude(id__in=seen_ids).delete()
        logger.info("SWAPI sync complete: %d films present", len(seen_ids))
