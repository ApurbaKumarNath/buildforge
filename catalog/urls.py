# catalog/urls.py

from django.urls import path
from . import views

# This namespace is crucial for our templates to find the correct URLs.
app_name = 'catalog'

urlpatterns = [
    # This is the URL for the main category chooser page (e.g., /catalog/)
    path('', views.catalog_chooser_view, name='chooser'),
    
    # This is the dynamic URL for the component list page.
    # It captures the component type from the URL (e.g., /catalog/cpu/)
    path('<str:component_type>/', views.component_list_view, name='component_list'),
     
]