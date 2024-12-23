from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    tag_name = models.CharField(max_length=50)


class Listing(models.Model):
    class ItemCondition(models.TextChoices):
        FACTORY_NEW = "FN", _("Factory New")
        MINIMAL_WEAR = "MW", _("Minimal Wear")
        FAIR = "FR", _("Fair")
        WELL_WORN = "WW", _("Well Worn")
        REFURBISHED = "RD", _("Refurbished")
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