from __future__ import annotations

from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .models import Comment, Film
from .serializers import CommentSerializer, FilmSerializer
from .services import fetch_and_sync_films


def _get_client_ip(request) -> str | None:
    """Best-effort real client IP extraction."""
    ip = request.META.get("HTTP_X_FORWARDED_FOR")
    if ip:
        return ip.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class FilmViewSet(viewsets.ModelViewSet):
    """
    Read-only films endpoint.
    List/Retrieve will sync from SWAPI first, then serve from DB.
    """
    queryset = Film.objects.all().order_by("release_date")
    serializer_class = FilmSerializer
    http_method_names = ["get"]  # read-only

    def list(self, request, *args, **kwargs):
        
        qs = (
            Film.objects.annotate(comment_count=Count("comments"))
            .order_by("release_date", "id")
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)

    def retrieve(self, request, *args, **kwargs):
      
        film = self.get_object()
        # Add computed field for single retrieve (serializer has it read-only)
        film.comment_count = film.comments.count()  # type: ignore[attr-defined]
        ser = self.get_serializer(film)
        return Response(ser.data)

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        """
        Nested comments endpoint under films using default router.

        GET  /api/films/{id}/comments/
        POST /api/films/{id}/comments/
        """
        try:
            film = Film.objects.get(pk=pk)
        except Film.DoesNotExist:
            raise NotFound("Film not found.")

        if request.method.lower() == "get":
            qs = film.comments.order_by("created_at", "id")
            serializer = CommentSerializer(qs, many=True)
            return Response(serializer.data)

        # POST
        data = {**request.data, "film": film.id}
        serializer = CommentSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        obj = serializer.save(ip_address=_get_client_ip(request))
        return Response(
            CommentSerializer(obj).data, status=status.HTTP_201_CREATED
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Comments endpoint; supports list/create/delete."""
    queryset = Comment.objects.all().order_by("created_at", "id")
    serializer_class = CommentSerializer
    http_method_names = ["get", "post", "delete"]

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        data = CommentSerializer(qs, many=True).data
        return Response(data, status=status.HTTP_200_OK)
