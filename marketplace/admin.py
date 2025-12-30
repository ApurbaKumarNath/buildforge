# marketplace/admin.py

from django.contrib import admin
# Import the models from THIS app (marketplace), not from builds.
from .models import MarketplaceListing, Comment

# This class customizes how listings are displayed in the admin panel.
class MarketplaceListingAdmin(admin.ModelAdmin):
    # These fields will be displayed in the main list view.
    list_display = ('title', 'seller', 'status', 'price', 'date_listed')
    # These fields can be used to filter the list.
    list_filter = ('status', 'date_listed')
    # This adds a search bar.
    search_fields = ('title', 'description', 'seller__username')

# This class customizes the display for comments.
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'listing', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('body', 'author__username', 'listing__title')

# Now, we register our marketplace models with their custom admin classes.
admin.site.register(MarketplaceListing, MarketplaceListingAdmin)
admin.site.register(Comment, CommentAdmin)