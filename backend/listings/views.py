from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import ListingSerializer
from .models import Listing
from .services.listing_services import ListingService


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    def get_permissions(self):
        # User must be authenticated if performing any action other than retrieve/list
        self.permission_classes = (
            [AllowAny] if (self.action in ["list", "retrieve"]) else [IsAuthenticated]
        )
        return super().get_permissions()

    def create(self, request):
        request_data = request.data.copy()
        request_data["author"] = request.user

        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        listing = ListingService.create_listing(
            author=request.user,
            title=validated_data["title"],
            condition=validated_data["condition"],
            description=validated_data["description"],
            price=validated_data["price"],
            image=validated_data["image"],
            tags=validated_data["tags"],
        )

        response_serializer = self.get_serializer(listing)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)