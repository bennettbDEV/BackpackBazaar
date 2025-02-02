from .classification import ListingTagClassifier
from listings.models import Listing, Tag

from huey.contrib.djhuey import db_task, on_commit_task

@db_task()
def add_listing_tags(listing_id: int, tags: list[str]):
    # This task executes queries. Once the task finishes, the connection
    # will be closed.
    try:
        listing = Listing.objects.get(id=listing_id)
    except Exception as e:
        print("Automatic addition of listing tags failed", e)
        return False
    for tag_name in tags:
        tag, _ = Tag.objects.get_or_create(tag_name=tag_name.strip())
        listing.tags.add(tag)
    
    listing.save()

@on_commit_task()
def generate_tags(listing_id: int, title: str, description: str):
    INCLUDE_DESC = False
    # This task executes queries. Once the task finishes, the connection
    # will be closed.
    ltg = ListingTagClassifier.ListingTagClassifier()
    ltg.load_model()

    # Include the description if INCLUDE_DESC is true, otherwise use only the title for tag predictions
    listing_text = [title.strip().lower() + description.strip().lower()] if INCLUDE_DESC else [title.strip().lower()]
    
    top_tags = ltg.predict_listing_tags(listing_text)
    add_listing_tags(listing_id, top_tags)