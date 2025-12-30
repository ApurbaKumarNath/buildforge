from django.shortcuts import render

# Create your views here.
# marketplace/views.py

from django.shortcuts import render, get_object_or_404
from .models import MarketplaceListing, Comment

def marketplace_list_view(request):
    """
    This view fetches and displays all 'Available' marketplace listings.
    """
    # Query the database for all listings where the status is 'Available'.
    # Order them by date_listed in descending order (newest first).
    # .select_related('seller') is a performance optimization to fetch the related
    # user data in the same query, preventing extra queries in the template.
    listings = MarketplaceListing.objects.filter(status='Available').select_related('seller').order_by('-date_listed')
    
    context = {
        'listings': listings,
    }
    return render(request, 'marketplace/marketplace_list.html', context)


def listing_detail_view(request, listing_id):
    """
    This view fetches and displays a single listing and its associated comments.
    """
    # Fetch the specific listing by its primary key. If not found, show a 404 page.
    listing = get_object_or_404(MarketplaceListing, pk=listing_id)
    
    # Fetch all comments related to this listing.
    # We use the 'related_name' we defined in the model ('comments').
    # .select_related('author') is another optimization for the comment's author.
    comments = listing.comments.select_related('author').all()
    
    context = {
        'listing': listing,
        'comments': comments,
    }
    return render(request, 'marketplace/listing_detail.html', context)