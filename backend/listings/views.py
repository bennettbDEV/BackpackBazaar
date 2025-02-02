from django_filters import rest_framework as filters
from rest_framework import filters as rest_filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Listing, SavedListing
from .serializers import ListingSerializer
from .tasks import generate_tags
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
        request_data = request.data
        request_data["author_id"] = request.user

        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        #tags = validated_data.pop("tags", [])
        tags = ""
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
        listing = self.get_object()
        # Check if already saved
        if SavedListing.objects.filter(user=request.user, listing=listing).exists():
            return Response({"detail": "Listing is already saved."}, status=status.HTTP_400_BAD_REQUEST)

        SavedListing.objects.create(user=request.user, listing=listing)
        return Response({"detail": "Listing saved successfully."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], permission_classes=[IsAuthenticated])
    def remove_saved_listing(self, request, pk=None):
        listing = self.get_object()
        saved_listing = SavedListing.objects.filter(user=request.user, listing=listing)
        if saved_listing.exists():
            saved_listing.delete()
            return Response({"detail": "Listing removed from saved listings."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Listing was not saved."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def list_saved_listings(self, request):
        saved_listings = SavedListing.objects.filter(user=request.user)
        listing_serializer = self.get_serializer([saved.listing for saved in saved_listings], many=True)
        return Response(listing_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like_listing(self, request, pk=None):
        listing = self.get_object()
        ListingService.like_listing(listing)
        return Response(
            {"detail": "Listing liked successfully."}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def dislike_listing(self, request, pk=None):
        listing = self.get_object()
        ListingService.dislike_listing(listing)
        return Response(
            {"detail": "Listing disliked successfully."}, status=status.HTTP_200_OK
        )
