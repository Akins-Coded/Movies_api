from datetime import date
from typing import Any, Dict

import pytest
from django.urls import reverse
from django.db.models import Max
from rest_framework.test import APIClient
from rest_framework import status

from films.models import Film, Comment
from films import services


# ----------------------------
# Fixtures
# ----------------------------

@pytest.fixture()
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture()
def film_factory(db):
    def _make(**overrides):
        # Film.pk == SWAPI id (PositiveIntegerField, primary_key=True)
        # Ensure unique default id to avoid PK collisions across factory calls
        next_id = overrides.pop("id", (Film.objects.aggregate(Max("id"))["id__max"] or 0) + 1)
        defaults = {
            "id": next_id,
            "title": overrides.pop("title", "A New Hope"),
            "release_date": overrides.pop("release_date", date(1977, 5, 25)),
        }
        return Film.objects.create(**defaults, **overrides)
    return _make


@pytest.fixture()
def comment_factory(db, film_factory):
    def _make(**overrides):
        film = overrides.pop("film", film_factory())  # FK required
        defaults = {
            "text": overrides.pop("text", "May the Force be with you."),
        }
        return Comment.objects.create(film=film, **defaults, **overrides)
    return _make


# ----------------------------
# Smoke / routing
# ----------------------------

@pytest.mark.django_db
def test_drf_api_root_available(api_client):
    # DRF default API root exposed by DefaultRouter under /api/
    resp = api_client.get("/api/")
    assert resp.status_code == 200, f"Expected DRF API root at /api/, got {resp.status_code}"
    # API root should advertise collection links
    payload = resp.json()
    assert "films" in payload and "comments" in payload, "API root is missing expected links"


# ----------------------------
# Films endpoints
# ----------------------------

@pytest.mark.django_db
def test_list_films_pagination_and_shape(api_client, film_factory, settings):
    # Settings use LimitOffsetPagination with PAGE_SIZE=10 (see settings)
    # Create 12 films to test pagination window
    for i in range(1, 13):
        film_factory(id=i, title=f"Film {i}", release_date=date(1977, 5, (i % 28) + 1))

    url = reverse("film-list")  # router basename="film"
    resp = api_client.get(url)  # first page
    assert resp.status_code == status.HTTP_200_OK

    data = resp.json()
    # LimitOffsetPagination shape
    for key in ("count", "next", "previous", "results"):
        assert key in data, f"Pagination key '{key}' missing from response"

    assert data["count"] == 12, "Total count should match created films"
    assert len(data["results"]) == 10, "Page size should be 10 by default"

    # follow next link if present and ensure remaining results
    if data["next"]:
        resp2 = api_client.get(data["next"])
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert len(data2["results"]) == 2, "Second page should contain remaining 2 films"

    # Validate basic fields from FilmSerializer
    sample = data["results"][0]
    for key in ("id", "title", "release_date"):
        assert key in sample, f"Film item missing field '{key}'"


@pytest.mark.django_db
def test_retrieve_film(api_client, film_factory):
    film = film_factory(id=42, title="The Answer", release_date=date(1980, 1, 1))
    url = reverse("film-detail", kwargs={"pk": film.pk})
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    payload = resp.json()
    assert payload["id"] == 42 and payload["title"] == "The Answer"


@pytest.mark.django_db
def test_retrieve_film_not_found(api_client):
    url = reverse("film-detail", kwargs={"pk": 9999})
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_404_NOT_FOUND, "Unknown film id should be 404"


# ----------------------------
# Comments endpoints
# ----------------------------

@pytest.mark.django_db
def test_list_comments(api_client, comment_factory):
    comment_factory(text="c1")
    comment_factory(text="c2")
    url = reverse("comment-list")
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    payload = resp.json()
    assert isinstance(payload, list), "Assuming comments list view returns a bare list"
    assert len(payload) >= 2, "Expected at least 2 comments listed"


@pytest.mark.django_db
def test_create_comment_success(api_client, film_factory):
    film = film_factory(id=7)
    url = reverse("comment-list")
    body = {"film": film.pk, "text": "Great movie!"}
    resp = api_client.post(url, data=body, format="json")
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    payload = resp.json()
    assert payload["film"] == film.pk
    assert payload["text"] == "Great movie!"
    assert "id" in payload and "created_at" in payload, "Expected id/created_at on creation"


@pytest.mark.django_db
def test_create_comment_validation_errors(api_client, film_factory):
    film = film_factory(id=9)
    url = reverse("comment-list")

    # Empty/whitespace text -> serializer error from validate_text
    resp = api_client.post(url, data={"film": film.pk, "text": "   "}, format="json")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    msg = resp.json().get("text")
    assert msg, "Expected validation error on text"
    # serializer raises "Comment text is required."
    assert any("required" in m.lower() for m in (msg if isinstance(msg, list) else [msg]))

    # Too long text (>500)
    too_long = "x" * 501
    resp2 = api_client.post(url, data={"film": film.pk, "text": too_long}, format="json")
    assert resp2.status_code == status.HTTP_400_BAD_REQUEST
    msg2 = resp2.json().get("text")
    assert msg2, "Expected validation error for max length > 500"


@pytest.mark.django_db
def test_create_comment_invalid_film_fk(api_client):
    url = reverse("comment-list")
    resp = api_client.post(url, data={"film": 999999, "text": "Hello"}, format="json")
    # DRF ModelSerializer FK validation typically yields 400 with "Invalid pk..."
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "film" in resp.json(), "Expect field-level error for invalid film pk"


@pytest.mark.django_db
def test_create_comment_malformed_json_returns_400(api_client, film_factory):
    # Send invalid JSON payload to ensure robust error reporting
    film = film_factory(id=11)
    url = reverse("comment-list")
    # Content is not JSON but declared as such
    resp = api_client.post(url, data="not json", content_type="application/json")
    assert resp.status_code in {status.HTTP_400_BAD_REQUEST, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE}


# ----------------------------
# Services: SWAPI sync integration (mocked HTTP)
# ----------------------------

class _FakeResp:
    def __init__(self, status_code: int, payload: Dict[str, Any]):
        self.status_code = status_code
        self._payload = payload

    def raise_for_status(self):
        if self.status_code >= 400:
            from requests import HTTPError
            raise HTTPError(f"status {self.status_code}")

    def json(self):
        return self._payload


@pytest.mark.django_db
def test_fetch_and_sync_films_paginates_and_prunes(monkeypatch):
    """
    services.fetch_and_sync_films should:
      - page through results
      - upsert films by id/title/release_date
      - delete local films that are no longer present upstream
    """

    # Page 1 -> two films, has next
    page1 = _FakeResp(
        200,
        {
            "results": [
                {"url": "https://swapi.dev/api/films/1/", "title": "Film 1", "release_date": "1977-05-25"},
                {"url": "https://swapi.dev/api/films/2/", "title": "Film 2", "release_date": "1980-05-21"},
            ],
            "next": "https://swapi.dev/api/films/?page=2",
        },
    )
    # Page 2 -> one film, no next
    page2 = _FakeResp(
        200,
        {
            "results": [
                {"url": "https://swapi.dev/api/films/3/", "title": "Film 3", "release_date": "1983-05-25"},
            ],
            "next": None,
        },
    )

    calls = {"n": 0}

    def fake_get(url, timeout=15):
        calls["n"] += 1
        return page1 if calls["n"] == 1 else page2

    # Seed a stale film that should be pruned
    Film.objects.create(id=99, title="Stale", release_date=date(1999, 1, 1))

    monkeypatch.setattr("films.services.requests.get", fake_get)
    services.fetch_and_sync_films()

    ids = list(Film.objects.order_by("id").values_list("id", flat=True))
    assert ids == [1, 2, 3], f"Expected only upstream ids [1,2,3], found {ids}"

    # Titles persisted
    titles = list(Film.objects.order_by("id").values_list("title", flat=True))
    assert titles == ["Film 1", "Film 2", "Film 3"]


@pytest.mark.django_db
def test_fetch_and_sync_films_http_error_bubbles(monkeypatch):
    class _Err:
        def raise_for_status(self):  # always error
            from requests import HTTPError
            raise HTTPError("Boom")
        def json(self):
            return {}

    def fake_get(url, timeout=15):
        return _Err()

    monkeypatch.setattr("films.services.requests.get", fake_get)

    with pytest.raises(Exception) as exc:
        services.fetch_and_sync_films()
    assert "Boom" in str(exc.value)


# ----------------------------
# Method/verb constraints (sanity)
# ----------------------------

@pytest.mark.django_db
def test_disallowed_methods(api_client, film_factory):
    film = film_factory(id=55)
    list_url = reverse("film-list")
    detail_url = reverse("film-detail", kwargs={"pk": film.pk})

    # Typically Film endpoints are read-only (depending on your ViewSet)
    # Ensure unsafe methods are blocked (adjust if you allow them)
    for method in ("post", "put", "patch", "delete"):
        resp = getattr(api_client, method)(list_url if method == "post" else detail_url, data={})
        assert resp.status_code in {status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED}, \
            f"{method.upper()} should be blocked (got {resp.status_code})"
