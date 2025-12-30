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
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_listed = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Available')

    # The user who is selling the item.
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    



class Comment(models.Model):
    """
    Represents a single comment made by a user on a MarketplaceListing.
    """
    # ForeignKey to MarketplaceListing: This creates the relationship.
    # Each comment belongs to ONE listing. A listing can have MANY comments.
    # on_delete=models.CASCADE: If a listing is deleted, all its comments are also deleted.
    # related_name='comments': Allows us to easily get all comments for a listing,
    # e.g., my_listing.comments.all()
    listing = models.ForeignKey(
        MarketplaceListing, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )

    # ForeignKey to the User model: This tracks who wrote the comment.
    # on_delete=models.CASCADE: If a user deletes their account, their comments are also deleted.
    # This is a different choice than we made for Reviews, which is fine.
    # It's a design decision: are comments valuable without the author? Maybe not.
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )

    # TextField is used for the main body of the comment, allowing for multi-line text.
    body = models.TextField()

    # DateTimeField with auto_now_add=True automatically sets the timestamp
    # to the moment the comment is first created in the database.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This makes the default ordering for comments be from oldest to newest.
        # When we display them, we can easily reverse this if we want.
        ordering = ['created_at']

    def __str__(self):
        # This provides a helpful, readable representation in the Django admin panel.
        # e.g., "Comment by apurba on 'Selling my old GPU'"
        return f"Comment by {self.author.username} on '{self.listing.title}'"


    
#_____________________________________________________________________________________________________________________________ 