from django.contrib import admin
from .models import Comment
# Register your models here.

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
list_display = ("id", "film_id", "created_at")
search_fields = ("body",)
list_filter = ("film_id",)