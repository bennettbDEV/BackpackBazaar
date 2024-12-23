from rest_framework import serializers
from .models import Listing


class ListingSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50), write_only=True
    )
    tags_out = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "id",
            "title",
            "condition",
            "description",
            "price",
            "image",
            "likes",
            "dislikes",
            "tags",
            "tags_out",
            "created_at",
            "last_modified_at",
            "author_id",
        ]
        read_only_fields = [
            "likes",
            "dislikes",
            "created_at",
            "last_modified_at",
            "author_id",
        ]

    def get_tags_out(self, obj):
        return [tag.tag_name for tag in obj.tags.all()]
