#api/views.py
'''
CLASSES: 
LoginView, StandardResultsSetPagination, UserViewSet, ListingViewSet, 
ServeImageView, 
'''
import mimetypes
import os
from django.conf import settings
from django.http import FileResponse
from django.views import View
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .handlers import ListingHandler, UserHandler
from .serializers import ListingSerializer, LoginSerializer, UserSerializer


class LoginView(TokenObtainPairView):
    """Handles API requests for logging in.

    Attributes:
        serializer_class (LoginSerializer): A serializer that validates and serializes login data.
        permission_classes (BasePermission): A permission class that dictates what type of user can make login requests.
        user_handler (UserHandler): A handler class that handles DB interactions related to users.
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_handler = UserHandler()

    # Login request
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        # If valid credentials
        if serializer.is_valid():
            user_data = serializer.validated_data
            response = self.user_handler.login(user_data)
            return response

        # If the serializer is invalid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        description="Retrieve a paginated list of all users.",
        responses={200: UserSerializer(many=True)},
    ),
    create=extend_schema(
        description="Register a user with the given info. Note: To upload an image, ensure the form is submitted as 'multipart/form-data'.",
        request=UserSerializer,
        responses={
            201: OpenApiExample(
                "Successful Response",
                value={
                    "id": 1,
                    "username": "johndoe",
                    "location": "New York",
                    "email": "johndoe@example.com",
                    "image": "/media/users/johndoe.jpg",  # Representing the relative url of the image on the server
                },
                response_only=True,
            )
        },
        examples=[
            OpenApiExample(
                "Create User Example",
                value={
                    "username": "johndoe",
                    "password": "password123",  # Note: this is a write-only field
                    "location": "New York",
                    "email": "johndoe@example.com",
                    "image": "johndoe.jpg",  # Representing a file being uploaded
                },
                request_only=True,
            )
        ],
    ),
    retrieve=extend_schema(
        description="Retrieve a specific user by ID.",
        responses={200: UserSerializer},
        parameters=[
            {
                "name": "pk",
                "in": "path",
                "required": True,
                "description": "The ID of the user to retrieve.",
                "schema": {"type": "integer", "example": 1},
            }
        ],
    ),
    partial_update=extend_schema(
        description="Partially update a specific user by ID. Only the fields provided in the request will be updated.",
        request=UserSerializer,
        responses={
            200: UserSerializer,  # Successful update will return the updated user data
        },
        examples=[
            OpenApiExample(
                "Partial Update Example",
                value={
                    "username": "john_doe_updated",  # Only updating the username in this example
                },
                request_only=True,
            )
        ],
    ),
    destroy=extend_schema(
        description="Deletes a specific user by ID.",
        responses={204: UserSerializer},
        parameters=[
            {
                "name": "pk",
                "in": "path",
                "required": True,
                "description": "The ID of the user to retrieve.",
                "schema": {"type": "integer", "example": 1},
            }
        ],
    ),
)
class UserViewSet(viewsets.GenericViewSet):
    """Handles all API requests related to Users.

    Attributes:
        serializer_class (UserSerializer): A serializer that validates and serializes user data.
        pagination_class (StandardResultsSetPagination): A pagination class that splits requests for all users into multiple pages.
        user_handler (UserHandler): A handler class that handles DB interactions related to users.
    """

    serializer_class = UserSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_handler = UserHandler()

    def get_permissions(self):
        # User must be authenticated if performing any action other than create/retrieve/list
        self.permission_classes = ([AllowAny] if (self.action in ["create", "retrieve", "list"]) else [IsAuthenticated])
        return super().get_permissions()

    def get_queryset(self):
        # Gets all users
        users = self.user_handler.list_users()
        return users

    # Crud actions
    def list(self, request):
        """Lists all user objects.

        Args:
            request (Request): DRF request object.

        Returns:
            Response: An object containing a list of all user objects.
        """

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # Fallback if pagination is not applicable
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """Creates a new User.

        Args:
            request (Request): DRF request object.

        Returns:
            Response: If request data is valid, the DRF Response object will contain authentication tokens.
            Response will always include an HTTP status.
        """

        # Serialize/Validate data
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            response = self.user_handler.register_user(validated_data)
            return response
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Retrieves the User with the specified id.

        Args:
            request (Request): DRF request object.
            pk (int, optional): The id of the User. Defaults to None.

        Returns:
            Response: A DRF Response object with the user's data, if the user exists.
            Response will always include an HTTP status.
        """

        user = self.user_handler.get_user(pk)
        if user:
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "User with that id not found."}, status=status.HTTP_404_NOT_FOUND,)

    def partial_update(self, request, pk=None):
        """Updates the specified user with the given data.

        Args:
            request (Request): DRF request object.
            pk (int, optional): The id of the User. Defaults to None.

        Returns:
            Response: A DRF Response object with an HTTP status.
        """

        try:
            response = self.user_handler.partial_update_user(request, pk)
            return response
        except Exception as e:
            print(str(e))
            return Response({"error": "Server error occured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR,)

    def destroy(self, request, pk=None):
        """Deletes the specified User.

        Args:
            request (Request): DRF request object.
            pk (int, optional): The id of the User. Defaults to None.

        Returns:
            Resposne: A DRF Response object with an HTTP status.
        """
        try:
            response = self.user_handler.delete_user(request, pk)
            return response
        except Exception as e:
            print(str(e))
            return Response({"error": "Server error occured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Blocks the specified user. This action prevents the blocked user from messaging the authenticated user.",
        parameters=[
            {
                "name": "pk",
                "in": "path",
                "required": True,
                "description": "The ID of the user to be blocked.",
                "schema": {"type": "integer"},
            }
        ],
        request=None,  # No request body needed for this POST request
        responses={
            204: OpenApiExample(
                "Successful Block",
                value={"message": "User blocked successfully."},
                response_only=True,
            ),
            400: OpenApiExample(
                "Invalid User ID",
                value={"error": "Invalid user ID."},
                response_only=True,
            ),
            500: OpenApiExample(
                "Internal Server Error",
                value={
                    "error": "An unexpected error occurred while blocking the user."
                },
                response_only=True,
            ),
        },
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def block_user(self, request, pk=None):
        """
        Blocks the specified user.

        Args:
            request (Request): DRF request object.
            pk (int): The ID of the user to be blocked.

        Returns:
            Response: A DRF Response object with an HTTP status.
        """

        try:
            blocker_id = request.user.id
            blocked_id = int(pk)

            # Call the handler method to block the user
            response = self.user_handler.block_user(blocker_id, blocked_id)
            return response

        except ValueError:
            return Response(
                {"error": "Invalid user ID."},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error blocking user: {e}")
            return Response({"error": "An unexpected error occurred while blocking the user."},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        description="Unblocks the specified user, allowing them to interact with the authenticated user again.",
        parameters=[
            {
                "name": "pk",
                "in": "path",
                "required": True,
                "description": "The ID of the user to be unblocked.",
                "schema": {"type": "integer"},
            }
        ],
        request=None,  # No request body needed for this POST request
        responses={
            204: OpenApiExample(
                "Successful Unblock",
                value={"message": "User unblocked successfully."},
                response_only=True,
            ),
            400: OpenApiExample(
                "Invalid User ID",
                value={"error": "Invalid user ID."},
                response_only=True,
            ),
            500: OpenApiExample(
                "Internal Server Error",
                value={
                    "error": "An unexpected error occurred while unblocking the user."
                },
                response_only=True,
            ),
        },
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def unblock_user(self, request, pk=None):
        """
        Unblocks the specified user.

        Args:
            request (Request): DRF request object.
            pk (int): The ID of the user to be unblocked.

        Returns:
            Response: A DRF Response object with an HTTP status.
        """

        try:
            blocker_id = request.user.id
            blocked_id = int(pk)

            # Call the handler method to unblock the user
            response = self.user_handler.unblock_user(blocker_id, blocked_id)
            return response

        # if error
        except ValueError:
            return Response(
                {"error": "Invalid user ID."}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f"Error unblocking user: {e}")
            return Response(
                {"error": "An unexpected error occurred while unblocking the user."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
    @extend_schema(
        description="Checks if the authenticated user has been blocked by the specified user.",
        parameters=[
            {
                "name": "pk",
                "in": "path",
                "required": True,
                "description": "The ID of the user to check against.",
                "schema": {"type": "integer"},
            }
        ],
        request=None,  # No request body needed for this GET request
        responses={
            200: OpenApiExample(
                "Successful Check",
                value={
                    "message": "User is blocked."
                },
                response_only=True,
            ),
            400: OpenApiExample(
                "Invalid User ID",
                value={"error": "Invalid user ID."},
                response_only=True,
            ),
            500: OpenApiExample(
                "Internal Server Error",
                value={
                    "error": "An unexpected error occurred while checking block status."
                },
                response_only=True,
            ),
        },
    )
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def is_user_blocked(self, request, pk=None):
        """
        Checks if the authenticated user has been blocked by the specified user.

        Args:
            request (Request): DRF request object.
            pk (int): The ID of the user to check against.

        Returns:
            Response: A DRF Response object with an HTTP status.
        """
        try:
            sender_id = request.user.id
            receiver_id = int(pk)

            # Call the handler method to check if the user is blocked
            response = self.user_handler.is_user_blocked(sender_id, receiver_id)
            return response
        
        #if error
        except ValueError:
            return Response({"error": "Invalid user ID."},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error checking block status: {e}")
            return Response({"error": "An unexpected error occurred while checking block status."},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def list_blocked_users(self, request):
        """
        Fetches all the user's blocked users.

        Args:
            request (Request): DRF request object.

        Returns:
            Response: A DRF Response object with an HTTP status.
        """
        
        try:
            user_id = request.user.id
            #Call the handler function to retrieve blocked users
            response = self.user_handler.list_blocked_users(user_id)
            #Return the list of blocked users
            return response
        except Exception as e:
            # Log the error for debugging
            print(f"Error in list_blocked_users: {e}")
            # Return a generic server error response
            return Response(
                {"error": "An unexpected error occurred while fetching blocked users."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Listing controller/handler
@extend_schema_view(
    list=extend_schema(
        description="Retrieve a paginated list of listings with optional filters, search, and ordering.",
        examples=[
            OpenApiExample(
                "List Listings Example",
                value=[
                    {
                        "id": 1,
                        "title": "Programming Textbook",
                        "condition": "Well Worn",
                        "description": "Modern Programming Languages 2nd Edition.",
                        "price": 49.99,
                        "image": "/media/listings/6544f1c8-f439-4502-9t3a-cb9428df139q",
                        "likes": 10,
                        "dislikes": 2,
                        "tags": ["programming", "textbook"],
                        "created_at": "2024-12-11 03:55:02",
                        "author_id": 5,
                    },
                    {
                        "id": 2,
                        "title": "Gaming Chair",
                        "condition": "Minimal Wear",
                        "description": "Ergonomic gaming chair with adjustable height.",
                        "price": 150.00,
                        "image": "/media/listings/4314f1c8-f469-4522-9fa6-cb9428df177e",
                        "likes": 25,
                        "dislikes": 1,
                        "tags": ["furniture", "gaming"],
                        "created_at": "2024-12-12 05:30:35",
                        "author_id": 3,
                    },
                ],
                response_only=True,
            )
        ],
    ),
    create=extend_schema(
        description="Update a specific listing partially by its ID. Requires authentication. Note: To upload an image, ensure the form is submitted as 'multipart/form-data'.",
        request=ListingSerializer,
        examples=[
            OpenApiExample(
                "Create Listing Example",
                value={
                    "title": "Programming Textbook",
                    "description": "Modern Programming Lanugages 2nd Edition by Adams Brooks Webber.",
                    "price": 49.99,
                    "condition": "Well Worn",
                    "tags": ["example", "sample", "listing"],
                    "image": "textbook.jpg",
                },
                request_only=True,
            )
        ],
    ),
    retrieve=extend_schema(
        description="Retrieve the details of a specific listing by its ID.",
        responses={200: ListingSerializer},
        examples=[
            OpenApiExample(
                "Retrieve Listing Example",
                value={
                    "id": 1,
                    "title": "Programming Textbook",
                    "condition": "Well Worn",
                    "description": "Modern Programming Languages 2nd Edition.",
                    "price": 49.99,
                    "image": "/media/listings/6544f1c8-f439-4502-9t3a-cb9428df139q",
                    "likes": 10,
                    "dislikes": 2,
                    "tags": ["programming", "textbook"],
                    "created_at": "2024-12-11 03:55:02",
                    "author_id": 5,
                },
                response_only=True,
            )
        ],
    ),
    partial_update=extend_schema(
        description="Partially update a specific listing by ID. Only the fields provided in the request will be updated.",
        request=ListingSerializer,
        responses={
            200: ListingSerializer,
        },
        examples=[
            OpenApiExample(
                "Partial Update Listing Example",
                value={
                    "price": 45.99,
                    "tags": ["updated", "new_price"],
                },
                request_only=True,
            ),
            OpenApiExample(
                "Partial Update Response Example",
                value={
                    "id": 1,
                    "title": "Programming Textbook",
                    "condition": "Well Worn",
                    "description": "Modern Programming Languages 2nd Edition.",
                    "price": 45.99,
                    "image": "textbook.jpg",
                    "likes": 10,
                    "dislikes": 2,
                    "tags": ["updated", "new_price"],
                    "created_at": "2024-12-11 03:55:02",
                    "author_id": 5,
                },
                response_only=True,
            ),
        ],
    ),
    destroy=extend_schema(
        description="Delete a specific listing by its ID. Requires authentication.",
        examples=[
            OpenApiExample(
                "Delete Listing Example",
                value={"message": "Listing deleted successfully."},
                response_only=True,
            )
        ],
    ),
)
class ListingViewSet(viewsets.GenericViewSet):
    """Handles all API requests related to Listings.

    Attributes:
        serializer_class (ListingSerializer): A serializer that validates and serializes listing data.
        pagination_class (StandardResultsSetPagination): A pagination class that splits requests for all listings into multiple pages.
        listing_handler (ListingHandler): A handler class that handles DB interactions related to listings.
    """

    serializer_class = ListingSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listing_handler = ListingHandler()

    def get_permissions(self):
        # User must be authenticated if performing any action other than retrieve/list
        self.permission_classes = ([AllowAny] if (self.action in ["list", "retrieve"]) else [IsAuthenticated])
        return super().get_permissions()

    def get_queryset(self):
        filters = {} # No filters by default

        search_term = self.request.query_params.get("search", None)
        ordering = self.request.query_params.get("ordering", None)
        
        # Add supported filters
        for param, value in self.request.query_params.items():
            if param in ["min_price", "max_price", "min_likes", "max_dislikes", "condition", "author_id"]:  # Allowed filters
                filters[param] = value

        # Get the filtered and sorted listings
        listings = self.listing_handler.list_filtered_listings(filters, search_term, ordering)

        # Return listings as Listing instances
        return listings

    # CRUD actions for ListingViewSet
    def list(self, request):
        valid_params = [
            "search",
            "ordering",
            "min_price",
            "max_price",
            "min_likes",
            "max_dislikes",
            "condition",
            "page",
            "author_id"
        ]
        valid_ordering_fields = [
            "title",
            "condition",
            "description",
            "price",
            "likes",
            "dislikes",
            "created_at",
        ]

        # Field validation
        for param, value in request.query_params.items():
            if param not in valid_params:
                return Response({"error": "Invalid parameter."}, status=status.HTTP_400_BAD_REQUEST)
            if param == "ordering" and value.lstrip("-") not in valid_ordering_fields:
                return Response({"error": "Invalid ordering parameter."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # Fallback if pagination is not applicable
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user_id = request.user.id

            response = self.listing_handler.create_listing(serializer.validated_data, user_id)
            return response
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        listing = self.listing_handler.get_listing(pk)
        if listing:
            serializer = self.get_serializer(listing)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Listing with that id not found."}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        try:
            response = self.listing_handler.partial_update_listing(request, pk)
            return response
        except Exception as e:
            print(str(e))
            return Response({"error": "Server error occured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        try:
            response = self.listing_handler.delete_listing(request, pk)
            return response
        except Exception as e:
            print(str(e))
            return Response({"error": "Server error occured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    '''
    Favorite/Save Listing actions

    -Router will automatically create a url based on the method name and details in the @action line
    -The url for this method will be listings/{pk}/favorite_listing/
    '''

    #Function: add listing to favorites
    @extend_schema(
        description="Adds a specific listing to the authenticated user's list of favorite listings.",
        request=None,
        responses={
            201: "Listing favorited successfully.",
            404: "Listing not found.",
            409: "Listing is already favorited",
            500: "Unexpected error occurred.",
        },
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite_listing(self, request, pk=None):
        """
        Adds a listing to the user's saved/favorite listings list.

        Args:
            request (Request): DRF request object.
            pk (int, optional): The id of the Listing. Defaults to None.

        Returns:
            Response: A DRF Response object with an HTTP status.
        """

        try:
            user_id = request.user.id
            response = self.listing_handler.add_favorite_listing(user_id, pk)
            return response
        except Exception as e:
            print(e)
            return Response({"ERROR: Unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    #Function: remove listing from favorites
    @extend_schema(
        description="Removes a specific listing from the authenticated user's list of favorite listings.",
        request=None,
        responses={
            204: "Listing removed from favorites successfully.",
            404: "Listing not found.",
            500: "Unexpected error occurred.",
        },
    )
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def remove_favorite_listing(self, request, pk=None):
        """Removes a listing from the user's saved/favorite listings list.

        Args:
            request (Request): DRF request object.
            pk (int, optional): The id of the Listing. Defaults to None.

        Returns:
            Response: A DRF Response object with an HTTP status.
        """

        try:
            user_id = request.user.id
            response = self.listing_handler.remove_favorite_listing(user_id, pk)
            return response
        except Exception as e:
            print(e)
            return Response({"ERROR: Unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    #Function: lists all the listings that have been 'favorited' by the user
    @extend_schema(
        description="Lists all of the user's favorite listings.",
        request=None,
        responses={
            200: "A list of favorite listings.",
            500: "Unexpected error occurred.",
        },
    )
    @action(detail=False, permission_classes=[IsAuthenticated])
    def list_favorite_listings(self, request):
        """
        Fetches all the user's saved/favorite listings.

        Args:
            request (Request): DRF request object.

        Returns:
            Response: A DRF Response object with an HTTP status.
        """
        
        try:
            user_id = request.user.id
            #Call the handler function to retrieve favorite listings
            response = self.listing_handler.list_favorite_listings(user_id)
            #Return the list of favorite listings
            return response
        except Exception as e:
            # Log the error for debugging
            print(f"Error in list_favorite_listings: {e}")
            # Return a generic server error response
            return Response(
                {"error": "Unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    '''
    Like/Dislike actions
    '''
    @extend_schema(
        description="Increments the like count for a specific listing.",
        request=None,
        responses={
            204: "Listing liked successfully.",
            404: "Listing not found.",
            500: "Unexpected error occurred.",
        },
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like_listing(self, request, pk=None):
        listing = self.listing_handler.get_listing(pk)
        if listing:
            # Use dot notation to access 'likes' if 'listing' is an object
            response = self.listing_handler.like_listing(pk, listing.likes)
            return response
        return Response({"error": "Listing with that id not found."}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        description="Increments the dislike count for a specific listing.",
        request=None,
        responses={
            204: "Listing disliked successfully.",
            404: "Listing not found.",
            500: "Unexpected error occurred.",
        },
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def dislike_listing(self, request, pk=None):
        listing = self.listing_handler.get_listing(pk)
        if listing:
            response = self.listing_handler.dislike_listing(pk, listing.dislikes)
            return response
        return Response({"error": "Listing with that id not found."}, status=status.HTTP_404_NOT_FOUND)


class ServeImageView(View):
    """Serve images with correct Content type.
    """

    def get(self, request, image_path):
        # Construct the full path to the image
        full_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, image_path))
        if not full_path.startswith(settings.MEDIA_ROOT):
            return Response({"error": "Invalid image path."}, status=status.HTTP_400_BAD_REQUEST)
        if not os.path.exists(full_path):
            return Response({"error": "Image not found."}, status=status.HTTP_404_NOT_FOUND)

        # Attempt to determine mime type using Mimetypes
        mime_type, _ = mimetypes.guess_type(full_path)
        mime_type = mime_type or "application/octet-stream"

        # Return file with the guessed Content type
        return FileResponse(open(full_path, "rb"), content_type=mime_type)