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

    class Meta:
        model = Comment
        fields = ["id", "film", "text", "ip_address", "created_at"]
        read_only_fields = ["id", "ip_address", "created_at"]

    def validate_text(self, value: str) -> str:
        """Basic validation for comment text length and emptiness."""
        if not value or not value.strip():
            raise serializers.ValidationError("Comment text is required.")
        if len(value) > 500:
            raise serializers.ValidationError(
                "Comment cannot exceed 500 characters."
            )
        return value
