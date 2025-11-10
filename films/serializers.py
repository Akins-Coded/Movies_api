from rest_framework import serializers
from .models import Comment




class FilmSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    release_date = serializers.DateField()
    comment_count = serializers.IntegerField()




class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("body",)
        extra_kwargs = {
        "body": {"max_length": 500}
        }   




class CommentListSerializer(serializers.ModelSerializer):
    class Meta:
    model = Comment
    fields = ("id", "film_id", "body", "created_at")
    read_only_fields = ('id', 'created_at', 'film_id')