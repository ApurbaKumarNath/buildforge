# marketplace/urls.py

from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Example: /marketplace/
    # This will be the main page listing all items.
    path('', views.marketplace_list_view, name='list'),

    # Example: /marketplace/listing/1/
    # This will be the detail page for a single listing.
    path('listing/<int:listing_id>/', views.listing_detail_view, name='detail'),
]