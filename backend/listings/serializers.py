from rest_framework import serializers
from .models import Listing


class ListingSerializer(serializers.ModelSerializer):
    tags = serializers.CharField(write_only=True)
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
    
    def validate_tags(self, value):
        return [tag.strip() for tag in value.split(',') if tag.strip()]
