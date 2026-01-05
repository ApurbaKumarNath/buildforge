# marketplace/urls.py

from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Example: /marketplace/
    # This will be the main page listing all items.
    path('', views.marketplace_list_view, name='list'),
    path('create/', views.create_listing, name='create'),
    
    # Example: /marketplace/listing/1/
    # This will be the detail page for a single listing.
    path('listing/<int:listing_id>/', views.listing_detail_view, name='detail'),
    path('listing/<int:listing_id>/edit/', views.edit_listing, name='edit'),
    path('listing/<int:listing_id>/delete/', views.delete_listing, name='delete'),
    path('listing/<int:listing_id>/comment/', views.add_comment, name='add_comment'),
]