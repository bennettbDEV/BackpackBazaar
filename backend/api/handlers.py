# user_handler.py (created by CHASE)
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from api.serializers import UserSerializer
from db_utils.db_factory import DBFactory, DBType
from db_utils.queries import SQLiteDBQuery
from .models import User 
# Initialize specific query object
db_query = SQLiteDBQuery(DBFactory.get_db_connection(DBType.SQLITE))

class UserHandler:
    # login function
    def login(self, user_data):
        if user_data:
            # Get users id
            user = db_query.get_user_by_username(user_data["username"])
            user_data["id"] = user["id"]

            # Create tokens for the authenticated user
            refresh = RefreshToken.for_user(User(**user_data))
            access_token = str(refresh.access_token)

            # Return tokens in the response
            return Response(
                {
                    "access": access_token,
                    "refresh": str(refresh),
                }
            )
        else:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    # logout function
    def logout(self):
        # Implement logout logic here (e.g., clear session or tokens) EDIT LATER
        pass

    def list_users(self):
        # Public info so no checks needed, just retrieve users from db
        return db_query.get_all_users()

    def register_user(self, validated_data):
        # Check if user already exists
        new_username = validated_data["username"]
        if db_query.get_user_by_username(new_username):
            return Response({"error": "Username already exists."},status=status.HTTP_409_CONFLICT,)

        # Generate password
        validated_data["password"] = make_password(validated_data["password"])

        # Create user
        db_query.create_user(validated_data)

        # Get users id
        user = db_query.get_user_by_username(new_username)
        validated_data["id"] = user["id"]

        # Generate JWT token for the new user
        refresh = RefreshToken.for_user(User(**validated_data))
        access = str(refresh.access_token)

        # Form response
        return Response(
            {
                "access": access,
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )

    def get_user(self, id):
        return db_query.get_user_by_id(id)

    def partial_update_user(self, request, id):
        user = db_query.get_user_by_id(id)
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure user is updating their own account
        if request.user.id == int(id):
            existing_data = dict(user)
            new_data = request.data

            # Hash password, if user is changing password
            # Consider returning error here if we want to implement change password somewhere else
            if "password" in new_data:
                new_data["password"] = make_password(new_data["password"])

            # The "|" operator merges dictionaries + the later dict overwrites values from older dict if the keys are equal
            merged_data = existing_data | new_data
            
            serializer = UserSerializer(data=merged_data, partial=True)

            if serializer.is_valid():
                # Ensure new username isnt taken if it's being updated
                if "username" in new_data and db_query.get_user_by_username(new_data["username"]):
                    return Response({"error": "Username is already taken."}, status=status.HTTP_403_FORBIDDEN,)

                db_query.partial_update_user(id, serializer.validated_data)
                return Response({"detail": "User edited successfully."}, status=status.HTTP_204_NO_CONTENT,)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_403_FORBIDDEN)

    def delete_user(self, request, id):
        user = db_query.get_user_by_id(id)
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure user is deleting their own account
        if request.user.id == int(id):
            db_query.delete_user(id)
            return Response({"detail": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT,)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_403_FORBIDDEN)


class ListingHandler:
    def list_listings(self):
        pass

    def create_listing(self):
        pass

    def get_listing(self):
        pass

    def update_listing(self):
        pass

    def patrial_update_listing(self):
        pass

    def delete_listing(self):
        pass
