from django.db import models

# Create your models here.
  
class Comment(models.Model):
    film_id = models.PositiveIntegerField(db_index=True)
    body = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)


    class Meta:
        ordering = ["created_at"]


    def __str__(self):
        return f"Comment(film_id={self.film_id}, id={self.id})"