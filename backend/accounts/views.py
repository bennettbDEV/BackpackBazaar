from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.services.user_services import UserService
from accounts.models import UserProfile

from accounts.models import UserBlock
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
            request_data = request.data.dict()
            location =  request_data.pop("location", None)
            image =  request.FILES.get("image", None)

            # If the profile field is not given, check if the location or image is given directly
            if request_data.get("profile") is None and (location is not None or image is not None):
                profile = {}
                if location is not None:
                    profile["location"] = location
                if image is not None:
                    profile["image"] = image
                request_data["profile"] = profile
            elif request_data.get("profile") is None:
                # If profile is none and location and image are none then just create blank profile
                request_data["profile"] = None

            serializer = self.get_serializer(data=request_data)
            serializer.is_valid(raise_exception=True)

            user = UserService.create_user(**serializer.validated_data)
            user_data = self.get_serializer(user).data

            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            token_data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }

            user_data.update(token_data)

            return Response(user_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(str(e))
            return Response({"error": "An error occured"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = False
        return self._update_profile(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self._update_profile(request, *args, **kwargs)

    def _update_profile(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        if request.user != instance:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_403_FORBIDDEN)

        # Grab profile fields from request data
        location = request.data.get("location", None)
        image = request.FILES.get("image", None)

        # Validate and update user fields
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = UserService.update_user(instance.id, **serializer.validated_data)

        # Update specific profile fields if given (if they werent nested in profile)
        # We use get_or_create to deal with edge case where user somehow doesnt have a profile
        profile, created = UserProfile.objects.get_or_create(user=instance, defaults={"location": "", "image": None})

        if profile:
            # Explicit check for fields to be "None"
            if location is not None:
                profile.location = location
            if image is not None:
                profile.image = image
            profile.save()

        response_data = self.get_serializer(user).data
        return Response(response_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user != instance:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_403_FORBIDDEN)
        
        UserService.delete_user(instance.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Extra actions
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def block_user(self, request, pk=None):
        blocked_user = self.get_object()
        block = UserBlock.objects.filter(user=request.user, blocked_user=blocked_user)

        if block.exists():
            return Response(
                {"detail": "User is already blocked."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif blocked_user == request.user:
            return Response(
                {"detail": "You can't block yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        UserBlock.objects.create(user=request.user, blocked_user=blocked_user)
        return Response(
            {"detail": "User blocked successfully."}, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def unblock_user(self, request, pk=None):
        blocked_user = self.get_object()
        block = UserBlock.objects.filter(user=request.user, blocked_user=blocked_user)
        if block.exists():
            block.delete()
            return Response(
                {"detail": "User unblocked successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {"detail": "User is not blocked."}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def is_user_blocked(self, request, pk=None):
        blocked_user = self.get_object()
        is_blocked = UserBlock.objects.filter(
            user=request.user, blocked_user=blocked_user
        ).exists()
        block_detail = "User is blocked." if is_blocked else "User is not blocked."
        return Response({"detail": block_detail}, status=status.HTTP_200_OK)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def list_blocked_users(self, request):
        blocked_users = UserBlock.objects.filter(user=request.user)
        blocked_user_data = [
            {"id": block.blocked_user.id, "username": block.blocked_user.username}
            for block in blocked_users
        ]
        return Response(blocked_user_data, status=status.HTTP_200_OK)
