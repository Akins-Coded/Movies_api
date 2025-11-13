from __future__ import annotations
from django.db import models


class Film(models.Model):
    # Mirror SWAPI IDs so clients can use the same ids
    id = models.PositiveIntegerField(primary_key=True)  # swapi_id
    title = models.CharField(max_length=255, db_index=True)
    release_date = models.DateField()
    
    class Meta:
        ordering = ["release_date", "id"]

    def __str__(self) -> str:
        return f"{self.title} ({self.release_date})"


class Comment(models.Model):
    film = models.ForeignKey(
        Film, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.CharField(max_length=500)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [
            models.Index(fields=["film", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Comment({self.film_id}): {self.text[:20]}"
