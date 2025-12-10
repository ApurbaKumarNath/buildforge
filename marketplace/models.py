# marketplace/models.py

#_____________________________________________________________________________________________________________________________ (akn)

from django.db import models
from django.conf import settings

class MarketplaceListing(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Sold', 'Sold'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='listings/', null=True, blank=True)
    date_listed = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Available')

    # The user who is selling the item.
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
#_____________________________________________________________________________________________________________________________ 