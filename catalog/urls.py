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
    path('component/<int:component_id>/', views.component_detail_view, name='component_detail'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),

    path('review/edit-form/<int:review_id>/', views.get_review_edit_form, name='get_review_edit_form'),
    path('review/save/<int:review_id>/', views.save_review_changes, name='save_review_changes'),
     
]