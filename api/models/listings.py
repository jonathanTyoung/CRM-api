from django.db import models
from .users import User
from .leads import Lead

class Listing(models.Model):
    mls_id = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    sqft = models.IntegerField()
    photo_url = models.URLField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class LeadListing(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='listings')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
