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

    # This URL will handle the HTMX POST request.
    path('<int:build_id>/add-component/', views.add_component_to_build, name='add_component'),
    
    path('<int:build_id>/status/', views.update_build_status, name='update_status'),

    path('<int:build_id>/remove-component/', views.remove_component_from_build, name='remove_component'),

    path('<int:build_id>/search-components/', views.search_components, name='search_components'),
]

#_________________________________________________________________________________________________________________________