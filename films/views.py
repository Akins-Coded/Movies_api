from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models import Count
from django.core.exceptions import ValidationError


from .models import Comment
from .serializers import FilmSerializer, CommentCreateSerializer, CommentListSerializer
from .services import list_films, film_exists




class FilmListAPIView(generics.GenericAPIView):
    """
    GET /api/films/
    Returns films from SWAPI with id, title, release_date and comment_count.
    Sorted ascending by release_date.
    """
    serializer_class = FilmSerializer


    def get(self, request):
        films = list_films()
        # Comment counts
        counts = dict(
            Comment.objects.values("film_id").annotate(c=Count("id")).values_list("film_id", "c")
        )
        enriched = [
            {
                "id": f["id"],
                "title": f["title"],
                "release_date": f["release_date"],
                "comment_count": counts.get(f["id"], 0),
            }
            for f in films
        ]
        enriched.sort(key=lambda x: x["release_date"]) # ascending
        serializer = self.get_serializer(enriched, many=True)
        return Response(serializer.data)




class CommentListCreateAPIView(generics.GenericAPIView):
    """
    GET /api/films/{film_id}/comments/ -> list comments in ascending created_at
    POST /api/films/{film_id}/comments/ -> add a comment (<=500 chars)
    """
    serializer_class = CommentListSerializer


    def get(self, request, film_id: int):
        if not film_exists(film_id):
            return Response({"detail": "Film not found on SWAPI."}, status=status.HTTP_404_NOT_FOUND)
        qs = Comment.objects.filter(film_id=film_id).order_by("created_at", "id")
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


    def post(self, request, film_id: int):
        if not film_exists(film_id):
            return Response({"detail": "Film not found on SWAPI."}, status=status.HTTP_404_NOT_FOUND)
        create_serializer = CommentCreateSerializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        body = create_serializer.validated_data["body"].strip()
        if not body:
            return Response({"body": ["Comment cannot be empty."]}, status=status.HTTP_400_BAD_REQUEST)
        comment = Comment.objects.create(film_id=film_id, body=body)