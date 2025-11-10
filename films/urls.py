from django.urls import path
from .views import FilmListAPIView, CommentListCreateAPIView


urlpatterns = [
path("films/", FilmListAPIView.as_view(), name="films-list"),
path("films/<int:film_id>/comments/", CommentListCreateAPIView.as_view(), name="films-comments"),
]