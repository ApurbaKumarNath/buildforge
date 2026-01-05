from django.shortcuts import render

# Create your views here.
# marketplace/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import MarketplaceListing, Comment
from .forms import MarketplaceListingForm, CommentForm

def marketplace_list_view(request):
    """
    This view fetches and displays all 'Available' marketplace listings.
    """
    listings = MarketplaceListing.objects.filter(status='Available').select_related('seller').order_by('-date_listed')
    
    context = {
        'listings': listings,
    }
    return render(request, 'marketplace/marketplace_list.html', context)


def listing_detail_view(request, listing_id):
    """
    This view fetches and displays a single listing and its associated comments.
    """
    listing = get_object_or_404(MarketplaceListing, pk=listing_id)
    comments = listing.comments.select_related('author').all()
    form = CommentForm()
    
    context = {
        'listing': listing,
        'comments': comments,
        'form': form,
    }
    return render(request, 'marketplace/listing_detail.html', context)

@login_required
def create_listing(request):
    if request.method == 'POST':
        form = MarketplaceListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            return redirect('marketplace:detail', listing_id=listing.id)
    else:
        form = MarketplaceListingForm()
    return render(request, 'marketplace/marketplace_form.html', {'form': form, 'title': 'Create Listing'})

@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(MarketplaceListing, pk=listing_id)
    if listing.seller != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = MarketplaceListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            return redirect('marketplace:detail', listing_id=listing.id)
    else:
        form = MarketplaceListingForm(instance=listing)
    return render(request, 'marketplace/marketplace_form.html', {'form': form, 'title': 'Edit Listing'})

@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(MarketplaceListing, pk=listing_id)
    if listing.seller != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        listing.delete()
        return redirect('marketplace:list')
    
    return render(request, 'marketplace/delete_confirm.html', {'listing': listing})

@login_required
def add_comment(request, listing_id):
    listing = get_object_or_404(MarketplaceListing, pk=listing_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.listing = listing
            comment.author = request.user
            comment.save()
    return redirect('marketplace:detail', listing_id=listing_id)
