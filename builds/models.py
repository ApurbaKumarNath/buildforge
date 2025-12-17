# builds/models.py

#_____________________________________________________________________________________________________________________________ (akn)

from django.db import models
# This allows us to easily reference our CustomUser model from settings.py
from django.conf import settings
from django.db.models import Sum, F, DecimalField

# This model represents a single PC build created by a user.
class Build(models.Model):
    # This is a ForeignKey, creating a many-to-one relationship.
    # One user can have MANY builds, but one build belongs to ONE user.
    # settings.AUTH_USER_MODEL is the correct way to reference your user model.
    # on_delete=models.CASCADE means if a user is deleted, all their builds are also deleted.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True) # Automatically set when created

    # This creates the many-to-many relationship between Build and Component.
    # We use the 'through' parameter to specify a custom intermediate table.
    # We need this because we want to store extra data on the relationship (the 'quantity').
    components = models.ManyToManyField('catalog.Component', through='BuildComponent')

    def __str__(self):
        return f"'{self.name}' by {self.user.username}"
    
    def calculate_total_price(self):
        """
        Calculates the total price of all components in the build.
        This is a highly efficient way to do it with a single database query.
        """
        # self.buildcomponent_set.all() gets all the BuildComponent items related to this build.
        # .aggregate() is a powerful Django function for performing calculations on a queryset.
        # Sum() is the aggregation function we want to use.
        # F('component__price') refers to the 'price' field on the related 'component' model.
        # F('quantity') refers to the 'quantity' field on the BuildComponent model itself.
        # We multiply them together for each item.
        # output_field=DecimalField() ensures the result is treated as a decimal, preventing errors.
        total = self.buildcomponent_set.aggregate(
            total_price=Sum(F('component__price') * F('quantity'), output_field=DecimalField())
        )['total_price']

        # The aggregate function returns a dictionary, e.g., {'total_price': 1250.50}.
        # If the build is empty, the result will be None, so we return 0.00 instead.
        return total or 0.00
    # ========================

    def __str__(self):
        return f"'{self.name}' by {self.user.username}"


# This is the "linking table" or "intermediate model".
# It connects a Build to a Component and adds the 'quantity' field.
class BuildComponent(models.Model):
    build = models.ForeignKey(Build, on_delete=models.CASCADE)
    component = models.ForeignKey('catalog.Component', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        # This ensures that a component can only be added to a build once.
        # You can't have two rows for "Intel i9" in the same build; you just change the quantity.
        unique_together = ('build', 'component')

    def __str__(self):
        return f"{self.quantity}x {self.component.name} in {self.build.name}"
    
# ==============================================================================
# WISHLIST MODEL
# ==============================================================================
class WishlistItem(models.Model):
    # If the user is deleted, their wishlist should disappear.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # If the component is deleted from the database, remove it from all wishlists.
    component = models.ForeignKey('catalog.Component', on_delete=models.CASCADE)
    
    # Useful to know when they added it (maybe for price tracking later).
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user shouldn't be able to add the exact same item to their wishlist twice.
        unique_together = ('user', 'component')
        # Optional: Order by newest added first
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.user.username} wants {self.component.name}"


#_____________________________________________________________________________________________________________________________