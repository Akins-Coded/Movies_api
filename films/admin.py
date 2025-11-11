from django.contrib import admin

from .models import Comment, Film


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "release_date")
    search_fields = ("title",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "film", "created_at")
    search_fields = ("text",)
    list_filter = ("film",)
