from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import ListingSerializer
from .models import Listing
from .services.listing_services import ListingService
from rest_framework import filters as rest_filters
from django_filters import rest_framework as filters


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

        listing = ListingService.create_listing(
            author_id=request.user,
            title=validated_data["title"],
            condition=validated_data["condition"],
            description=validated_data["description"],
            price=validated_data["price"],
            image=validated_data["image"],
            tags=validated_data["tags"],
        )

        response_serializer = self.get_serializer(listing)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        listing = self.get_object()

        if listing.author_id != request.user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_403_FORBIDDEN)
        
        request_data = request.data.copy()
        request_data["author_id"] = request.user

        serializer = self.get_serializer(listing, data=request_data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        updated_listing = ListingService.update_listing(
            author_id=request.user,
            title=validated_data["title"],
            condition=validated_data["condition"],
            description=validated_data["description"],
            price=validated_data["price"],
            image=validated_data["image"],
            tags=validated_data["tags"],
        )

        response_serializer = self.get_serializer(updated_listing)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    def partial_update(self, request, pk=None):
        listing = self.get_object()
        print(listing.id)
        if listing.author_id != request.user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_403_FORBIDDEN)
        
        request_data = request.data.copy()

        serializer = self.get_serializer(listing, data=request_data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        updated_listing = ListingService.partial_update_listing(
            author_id=request.user,
            title=validated_data.get("title", listing.title),
            condition=validated_data.get("condition", listing.condition),
            description=validated_data.get("description", listing.description),
            price=validated_data.get("price", listing.price),
            image=validated_data.get("image", listing.image),
            tags=validated_data.get("tags", [tag.tag_name for tag in listing.tags.all()]),
        )

        response_serializer = self.get_serializer(updated_listing)
        return Response(response_serializer.data, status=status.HTTP_200_OK)