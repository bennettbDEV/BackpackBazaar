from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.services.user_services import UserService

from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        # User must be authenticated if performing any action other than create/retrieve/list
        self.permission_classes = ([AllowAny] if (self.action in ["create", "retrieve", "list"]) else [IsAuthenticated])
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = UserService.create_user(**serializer.validated_data)
            return Response(
                self.get_serializer(user).data, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = UserService.update_user(instance.id, **serializer.validated_data)
        return Response(self.get_serializer(user).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        UserService.delete_user(instance.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
