# catalog/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case
from django.db.models import Q

# This map is our secure way of translating a URL part into a database model.
# The keys MUST be lowercase.
COMPONENT_MODEL_MAP = {
    'cpu': CPU,
    'gpu': GPU,
    'motherboard': Motherboard,
    'ram': RAM,
    'storage': Storage,
    'psu': PSU,
    'case': Case,
}

def catalog_chooser_view(request):
    """
    This view's only job is to display the category selection page.
    """
    # We pass the list of available component types to the template.
    component_types = COMPONENT_MODEL_MAP.keys()
    context = {'component_types': component_types}
    return render(request, 'catalog/catalog_chooser.html', context)


def component_list_view(request, component_type):
    """
    This view is dynamic. It displays a filtered and sorted list of components.
    """
    # Ensure the URL is case-insensitive (e.g., /catalog/CPU/ works).
    component_type_slug = component_type.lower()
    
    # Find the correct database model from our map.
    ModelClass = COMPONENT_MODEL_MAP.get(component_type_slug)

    # If the URL is invalid (e.g., /catalog/toast/), show a "Page Not Found" error.
    if not ModelClass:
        raise Http404("Component type not found")

    # Start with all components of the correct type.
    components = ModelClass.objects.all()

    # --- Filtering and Sorting Logic ---
    search_query = request.GET.get('q', '')
    sort_order = request.GET.get('sort', 'name') # Default to sorting by name.

    # Apply the search filter if the user typed something.
    if search_query:
        components = components.filter(
            Q(name__icontains=search_query) | 
            Q(manufacturer__icontains=search_query)
        )

    # Apply the sorting order based on the user's selection.
    if sort_order == 'price_asc':
        components = components.order_by('price')
    elif sort_order == 'price_desc':
        components = components.order_by('-price') # The '-' means descending.
    else: # Default sort
        components = components.order_by('name')
        
    # --- Prepare data for the template ---
    context = {
        'components': components,
        'component_type_display': component_type_slug.replace('_', ' ').title(),
        'component_type_slug': component_type_slug,
        'search_query': search_query,
        'sort_order': sort_order,
    }

    # If this is an HTMX request (from search/sort), only send back the grid part.
    if request.htmx:
        return render(request, 'catalog/partials/component_grid.html', context)
    
    # For the first page load, send the full page.
    return render(request, 'catalog/component_list.html', context)


