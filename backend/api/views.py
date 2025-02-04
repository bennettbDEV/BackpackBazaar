import mimetypes
import os

from django.conf import settings
from django.http import FileResponse
from django.views import View
from rest_framework import status
from rest_framework.response import Response


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