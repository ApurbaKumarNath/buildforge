# catalog/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse, HttpResponseForbidden
from .models import Component, CPU, GPU, Motherboard, RAM, Storage, PSU, Case
from django.db.models import Q
from .models import Component, Review
from .forms import ReviewForm 
from django.contrib.auth.decorators import login_required
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

# catalog/views.py

def catalog_chooser_view(request):
    """
    Displays component categories AND a searchable/sortable list of ALL components.
    """
    # Part 1: Get the categories for the top grid.
    component_types = COMPONENT_MODEL_MAP.keys()

    # Part 2: Get the queryset for ALL components.
    all_components = Component.objects.all()

    # Part 3: Apply filtering and sorting from the request's GET parameters.
    search_query = request.GET.get('q', '')
    sort_order = request.GET.get('sort', 'name')

    if search_query:
        all_components = all_components.filter(
            Q(name__icontains=search_query) | 
            Q(manufacturer__icontains=search_query)
        )

    if sort_order == 'price_asc':
        all_components = all_components.order_by('price')
    elif sort_order == 'price_desc':
        all_components = all_components.order_by('-price')
    else:
        all_components = all_components.order_by('name')

    # Part 4: Create the final context dictionary.
    context = {
        'component_types': component_types,
        # THE FIX: We name the variable 'components' to match what the partial expects.
        'components': all_components, 
        'search_query': search_query,
        'sort_order': sort_order,
    }

    # Part 5: Handle HTMX requests from the filter bar.
    if request.htmx:
        # When filtering, we only need to re-render the grid part.
        # The partial 'component_grid.html' will correctly use the 'components' variable.
        return render(request, 'catalog/partials/component_grid.html', context)
    
    # For the initial page load, render the full chooser page.
    return render(request, 'catalog/catalog_chooser.html', context)


def component_list_view(request, component_type):
    """
    This view is dynamic. It displays a filtered and sorted list of components for a SPECIFIC type.
    """
    component_type_slug = component_type.lower()
    ModelClass = COMPONENT_MODEL_MAP.get(component_type_slug)

    if not ModelClass:
        raise Http404("Component type not found")

    components = ModelClass.objects.all()

    search_query = request.GET.get('q', '')
    sort_order = request.GET.get('sort', 'name')

    if search_query:
        components = components.filter(
            Q(name__icontains=search_query) | 
            Q(manufacturer__icontains=search_query)
        )

    if sort_order == 'price_asc':
        components = components.order_by('price')
    elif sort_order == 'price_desc':
        components = components.order_by('-price')
    else:
        components = components.order_by('name')
        
    context = {
        'components': components,
        'component_type_display': component_type_slug.replace('_', ' ').title(),
        'component_type_slug': component_type_slug,
        'search_query': search_query,
        'sort_order': sort_order,
    }

    if request.htmx:
        return render(request, 'catalog/partials/component_grid.html', context)
    
    return render(request, 'catalog/component_list.html', context)


def component_detail_view(request, component_id):
    """
    Handles displaying component details, showing reviews, AND processing new review submissions.
    """
    # --- Part 1: Fetch all necessary data from the database ---
    component = get_object_or_404(
        Component.objects.select_related('cpu', 'gpu', 'motherboard', 'ram', 'storage', 'psu', 'case'), 
        pk=component_id
    )
    reviews = Review.objects.filter(component=component).select_related('user').order_by('-date_posted')
    
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    # --- Part 2: Handle the form submission for NEW reviews ---
    if request.method == 'POST' and request.user.is_authenticated and not user_review:
        form = ReviewForm(request.POST)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.component = component
            new_review.user = request.user
            new_review.save()
            # Redirect to the same page to prevent re-submission on refresh
            return redirect('catalog:component_detail', component_id=component.id)
        else:
        # For a GET request, create an empty form
            form = ReviewForm()

    else:
        # For a GET request, create an empty form
        form = ReviewForm()

    # --- Part 3: Build the specifications dictionary (This is the part that was missing) ---
    specs = {}
    component_type = component.get_type()

    if component_type == "CPU":
        child = component.cpu
        specs = {"Socket": child.socket, "Core Count": child.core_count, "Clock Speed": child.clock_speed}
    elif component_type == "GPU":
        child = component.gpu
        specs = {"VRAM": child.vram_gb, "Clock Speed": child.gpu_clock_speed}
    elif component_type == "Motherboard":
        child = component.motherboard
        specs = {"Socket": child.socket, "Form Factor": child.form_factor, "RAM Slots": child.ram_slots}
    elif component_type == "RAM":
        child = component.ram
        specs = {"Capacity": child.capacity_gb, "Speed": child.speed_mhz}
    elif component_type == "Storage":
        child = component.storage
        specs = {"Storage type": child.storage_type, "Capacity (GB)": child.capacity_gb }
    elif component_type == "PSU":
        child = component.psu
        specs = {"Wattage": child.wattage, "Efficiency": child.efficiency_rating}
    elif component_type == "Case":
        child = component.case
        specs = {"Form Factor": child.form_factor, "Max GPU Length": child.max_gpu_length}

    # --- Part 4: Assemble the final context for the template ---
    context = {
        'component': component,
        'specs': specs,
        'component_type': component_type,
        'reviews': reviews,
        'form': form,
        'user_review': user_review,
    }

    return render(request, 'catalog/component_detail.html', context)


@login_required
def delete_review(request, review_id):
    """
    Deletes a review if the request is a POST and the user has permission.
    """
    # We only allow deletion via a POST request for security.
    # This prevents accidental deletion from search engine crawlers or simple links.
    if request.method == 'POST':
        # Find the specific review we want to delete.
        review = get_object_or_404(Review, pk=review_id)
        
        # Security Check: The person making the request must be the review's author OR a staff member (admin).
        if request.user == review.user or request.user.is_staff:
            # Get the component ID *before* deleting the review, so we know where to redirect back to.
            component_id = review.component.id
            
            # This is the database operation that removes the row.
            review.delete()
            
            # Redirect the user back to the component detail page they were on.
            return redirect('catalog:component_detail', component_id=component_id)
        else:
            # If the user doesn't have permission, return a "403 Forbidden" error.
            return HttpResponseForbidden("You do not have permission to delete this review.")
    
    # If someone tries to access this URL with a GET request, just send them home.
    return redirect('home')




@login_required
def get_review_edit_form(request, review_id):
    """
    Returns an HTML fragment containing the form to edit a review.
    This is called by HTMX when the user clicks 'Edit'.
    """
    # Get the review, ensuring the person requesting the form is the author.
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    # Create a form instance pre-filled with the existing review's data.
    form = ReviewForm(instance=review)
    # Render and return ONLY the partial template for the form.
    return render(request, 'catalog/partials/review_edit_form.html', {'form': form, 'review': review})


@login_required
def save_review_changes(request, review_id):
    """
    Saves the edited review data submitted via POST and returns the updated
    review display fragment.
    """
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    if request.method == 'POST':
        # Populate the form with the submitted data and the original review instance.
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save() # Save the changes to the database.
            # After saving, return the "display" partial with the updated review.
            return render(request, 'catalog/partials/review_display.html', {'review': review})
        else:
            # If the form is invalid (e.g., empty text), return the form
            # again, which will now contain the error messages.
            return render(request, 'catalog/partials/review_edit_form.html', {'form': form, 'review': review})
    
    # If it's not a POST request, do nothing.
    return redirect('catalog:component_detail', component_id=review.component.id)