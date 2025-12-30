# builds/urls.py

#_________________________________________________________________________________________________________________________ (akn)

from django.urls import path
from . import views

# This is a best practice for Django apps. It helps avoid URL name collisions.
app_name = 'builds'

urlpatterns = [
    # The path for our workbench.
    # <int:build_id> is a path converter. It captures an integer from the URL
    # and passes it as an argument named 'build_id' to our view function.
    path('<int:build_id>/', views.workbench_view, name='workbench'),

    path('create/', views.create_build_view, name='create'),

    path('share/<int:build_id>/', views.share_build_view, name='share_build'),

    # This is the URL for our new Curated Guides page.
    path('guides/', views.guides_view, name='guides'),

    path('clone/<int:build_id>/', views.clone_build_view, name='clone_build'),

    # This URL will handle the HTMX POST request.
    path('<int:build_id>/add-component/', views.add_component_to_build, name='add_component'),
    
    path('<int:build_id>/status/', views.update_build_status, name='update_status'),

    path('<int:build_id>/remove-component/', views.remove_component_from_build, name='remove_component'),

    path('<int:build_id>/search-components/', views.search_components, name='search_components'),

    path('delete/<int:build_id>/', views.delete_build_view, name='delete_build'),

    path('edit-form/<int:build_id>/', views.get_build_edit_form, name='get_edit_form'),
    path('save-changes/<int:build_id>/', views.save_build_changes, name='save_build_changes'),
    path('view-card/<int:build_id>/', views.get_view_card, name='get_view_card'),

    # This creates the URL /builds/wishlist/ and gives it the name 'wishlist'.
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/', views.add_to_wishlist_view, name='add_to_wishlist'),
    path('wishlist/remove/', views.remove_from_wishlist_view, name='remove_from_wishlist'),
    
]

#_________________________________________________________________________________________________________________________