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
            image=image,
        )

        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(tag_name=tag_name)
            listing.tags.add(tag)

        return listing

    @staticmethod
    @transaction.atomic
    def update_listing(listing_id, title, condition, description, price, image, tags):
        # Retrieve listing to be updated:
        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            # We have no object
            return None
        
        listing.title = title
        listing.condition = condition
        listing.description = description
        listing.price = price
        listing.image = image
        listing.tags.clear()
        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(tag_name=tag_name.strip())
            listing.tags.add(tag)
        
        listing.save()
        return listing

    @staticmethod
    @transaction.atomic
    def partial_update_listing(
        listing_id, title, condition, description, price, image, tags
    ):
        # Retrieve listing to be updated:
        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            # We have no object
            return None
        
        if title:
            listing.title = title
        if condition:
            listing.condition = condition
        if description:
            listing.description = description
        if price:
            listing.price = price
        if image:
            listing.image = image
        if tags:
            listing.tags.clear()
            for tag_name in tags:
                tag, _ = Tag.objects.get_or_create(tag_name=tag_name.strip())
                listing.tags.add(tag)
        
        listing.save()
        return listing

    @staticmethod
    @transaction.atomic
    def save_listing():
        pass

    @staticmethod
    @transaction.atomic
    def remove_saved_listing():
        pass

    @staticmethod
    @transaction.atomic
    def like_listing(listing):
        listing.likes += 1
        listing.save()

    @staticmethod
    @transaction.atomic
    def dislike_listing(listing):
        listing.dislikes += 1
        listing.save()