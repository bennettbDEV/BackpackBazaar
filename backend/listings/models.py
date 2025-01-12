from django.contrib.auth.models import User
from django.db import models


class Tag(models.Model):
    tag_name = models.CharField(max_length=50)


class Listing(models.Model):
    class ItemCondition(models.TextChoices):
        FACTORY_NEW = "FN", "Factory New"
        MINIMAL_WEAR = "MW", "Minimal Wear"
        FAIR = "FR", "Fair"
        WELL_WORN = "WW", "Well Worn"
        REFURBISHED = "RD", "Refurbished"
    title = models.CharField(max_length=50)
    condition = models.CharField(
        max_length=2,
        choices=ItemCondition,
        default=ItemCondition.FACTORY_NEW,
    )
    description = models.CharField(max_length=500)
    price = models.FloatField()
    image = models.ImageField(upload_to="listings/")
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True) # null=True has no effect according to docs
    created_at = models.DateField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    author_id = models.ForeignKey(User, on_delete=models.CASCADE)

class SavedListing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_listings")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)