from django.db import transaction

from listings.models import Listing, Tag


class ListingService:
    @staticmethod
    @transaction.atomic
    def create_listing(author_id, title, condition, description, price, image, tags):
        listing = Listing.objects.create(
            author_id=author_id,
            title=title,
            condition=condition,
            description=description,
            price=price,
            image=image
        )

        # Handle tag creation and association
        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(tag_name=tag_name.strip())
            listing.tags.add(tag)

        return listing

