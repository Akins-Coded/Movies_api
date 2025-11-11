# films/serializers.py
from rest_framework import serializers

from .models import Comment, Film


class FilmSerializer(serializers.ModelSerializer):
    """Read-only film serializer including precomputed comment_count."""
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Film
        fields = ["id", "title", "release_date", "comment_count"]
        read_only_fields = ["id", "title", "release_date", "comment_count"]


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for creating and listing comments."""
    text = serializers.CharField(allow_blank=True, max_length=500)
    class Meta:
        model = Comment
        fields = ["id", "film", "text", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_text(self, value: str) -> str:
        """Basic validation for comment text length and emptiness."""
        if not value or not value.strip():
            raise serializers.ValidationError("Comment text is required.")
        if len(value) > 500:
            raise serializers.ValidationError(
                "Comment cannot exceed 500 characters."
            )
        return value
    
class FilmDetailSerializer(FilmSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(FilmSerializer.Meta):
        fields = FilmSerializer.Meta.fields + ["comments"]
