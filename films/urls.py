from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, FilmViewSet

router = DefaultRouter()
router.register(r"films", FilmViewSet, basename="film")
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = [
    path("", include(router.urls)),
]
