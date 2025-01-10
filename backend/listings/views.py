from django_filters import rest_framework as filters
from rest_framework import filters as rest_filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Listing
from .serializers import ListingSerializer
from .services.listing_services import ListingService


class ListingFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_likes = filters.NumberFilter(field_name="likes", lookup_expr="gte")
    max_dislikes = filters.NumberFilter(field_name="dislikes", lookup_expr="lte")

    class Meta:
        model = Listing
        fields = [
            "condition",
            "author_id",
        ]


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    filter_backends = [
        filters.DjangoFilterBackend,
        rest_filters.SearchFilter,
        rest_filters.OrderingFilter,
    ]
    filterset_class = ListingFilter

    search_fields = ["title", "description", "tags__tag_name"]
    ordering_fields = [
        "title",
        "condition",
        "description",
        "price",
        "likes",
        "dislikes",
        "created_at",
    ]

    def get_permissions(self):
        # User must be authenticated if performing any action other than retrieve/list
        self.permission_classes = (
            [AllowAny] if (self.action in ["list", "retrieve"]) else [IsAuthenticated]
        )
        return super().get_permissions()

    def create(self, request):
        request_data = request.data.copy()
        request_data["author_id"] = request.user

        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        tags = validated_data.pop("tags", [])
        listing = ListingService.create_listing(
            author_id=request.user,
            title=validated_data["title"],
            condition=validated_data["condition"],
            description=validated_data["description"],
            price=validated_data["price"],
            image=validated_data["image"],
            tags=tags,
        )

        response_serializer = self.get_serializer(listing)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        listing = self.get_object()

        if listing.author_id != request.user:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_403_FORBIDDEN
            )

        request_data = request.data.copy()

        serializer = self.get_serializer(listing, data=request_data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        tags = validated_data.pop("tags", [])
        updated_listing = ListingService.update_listing(
            listing_id=listing.id,
            title=validated_data["title"],
            condition=validated_data["condition"],
            description=validated_data["description"],
            price=validated_data["price"],
            image=validated_data["image"],
            tags=tags,
        )

        response_serializer = self.get_serializer(updated_listing)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        listing = self.get_object()
        if listing.author_id != request.user:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_403_FORBIDDEN
            )

        request_data = request.data.copy()

        serializer = self.get_serializer(listing, data=request_data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        tags = validated_data.pop("tags", None)

        updated_listing = ListingService.partial_update_listing(
            listing_id=listing.id,
            title=validated_data.get("title"),
            condition=validated_data.get("condition"),
            description=validated_data.get("description"),
            price=validated_data.get("price"),
            image=validated_data.get("image"),
            tags=tags,
        )

        response_serializer = self.get_serializer(updated_listing)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    # Additional actions

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def save_listing(self, request, pk=None):
        pass

    @action(detail=True, methods=["delete"], permission_classes=[IsAuthenticated])
    def remove_saved_listing(self, request, pk=None):
        pass

    @action(detail=False, permission_classes=[IsAuthenticated])
    def list_saved_listing(self, request):
        pass

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like_listing(self, request, pk=None):
        listing = self.get_object()
        response = ListingService.like_listing(listing)
        return response

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def dislike_listing(self, request, pk=None):
        listing = self.get_object()
        response = ListingService.dislike_listing(listing)
        return response