# builds/views.py

#_________________________________________________________________________________________________________________________ (akn)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseForbidden
from .models import Build, BuildComponent
from catalog.models import Component
from django.shortcuts import get_object_or_404
from .logic import detect_bottleneck, calculate_psu_wattage
from django.db.models import Q, Sum, F, DecimalField, CharField
from django.db import models
from .forms import BuildForm
from django.db.models.functions import Cast
from django.utils import timezone

# This is the view for our new homepage.
def home_view(request):
    # This view now handles both displaying builds and creating new ones.
    if request.method == 'POST':
        # This block runs only when the "Create Build" form is submitted.
        # We only allow logged-in users to create builds.
        if request.user.is_authenticated:
            form = BuildForm(request.POST)
            if form.is_valid():
                # The form is valid, but DON'T save it to the database yet.
                # commit=False gives us the model object without saving.
                new_build = form.save(commit=False)
                
                # Now, we manually assign the current logged-in user to the build.
                new_build.user = request.user
                
                # Now we can save it to the database with the user assigned.
                new_build.save()
                
                # Redirect to the new workbench page for the build they just created.
                return redirect('builds:workbench', build_id=new_build.id)
        # If a non-logged-in user somehow POSTs, just redirect them.
        return redirect('home')

    # This part runs for a normal GET request (just visiting the page).
    builds = None
    if request.user.is_authenticated:
        # Start with the base queryset for the current user
        builds = Build.objects.filter(user=request.user)

        # === THIS IS THE NEW SEARCH LOGIC ===
        # Check if a search query 'q' is in the GET parameters
        search_query = request.GET.get('q', None)
        if search_query:
            # If a query exists, filter the builds queryset further.
            # Q objects allow for OR conditions.
            # This searches for the query in both the name and description fields.
            builds = builds.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )
        # ====================================

        # Always order the final result
        builds = builds.order_by('-date_created')
    
    # We create an empty instance of the form to display on the page.
    form = BuildForm()
    
    context = {
        'builds': builds,
        'form': form, # Add the form to the context
        'request': request, # Pass the request object for the partial template
    }
    return render(request, 'home.html', context)


# @login_required is a "decorator". It's a simple and powerful way to protect a view.
# If a non-logged-in user tries to access this URL, Django will automatically
# redirect them to the login page.
# builds/views.py -> workbench_view

def _get_build_scaffold(build):
    """
    A helper function to build the complete scaffold dictionary for a given build.
    This avoids repeating this complex logic in multiple views.
    """
    scaffold = {
        'CPU': None, 'Motherboard': None, 'GPU': None,
        'RAM': [], 'Storage': [], 'PSU': None, 'Case': None,
    }
    
    # Define the number of storage slots you want to show in the UI
    TOTAL_STORAGE_SLOTS = 2

    components_in_build = BuildComponent.objects.filter(build=build).select_related(
        'component__cpu', 'component__gpu', 'component__motherboard', 
        'component__ram', 'component__storage', 'component__psu', 'component__case'
    )
    motherboard = None

    for item in components_in_build:
        component_type = item.component.get_type()
        
        if component_type in ['CPU', 'Motherboard', 'GPU', 'PSU', 'Case']:
            scaffold[component_type] = item
            if component_type == 'Motherboard':
                motherboard = item.component.motherboard
        elif component_type == 'RAM':
            for _ in range(item.quantity):
                scaffold['RAM'].append(item)
        
        # === THE FIX FOR STORAGE SLOTS ===
        elif component_type == 'Storage':
            # We treat each drive as a separate slot, even if it's the same component with quantity > 1
            for _ in range(item.quantity):
                scaffold['Storage'].append(item)
        # =================================

    # --- Handle Dynamic RAM Slots ---
    ram_slots_total = 4
    if motherboard and hasattr(motherboard, 'ram_slots'):
        ram_slots_total = motherboard.ram_slots
    
    scaffold['RAM'] = scaffold['RAM'][:ram_slots_total]
    for _ in range(ram_slots_total - len(scaffold['RAM'])):
        scaffold['RAM'].append(None)

    # --- Handle Fixed Storage Slots ---
    scaffold['Storage'] = scaffold['Storage'][:TOTAL_STORAGE_SLOTS]
    for _ in range(TOTAL_STORAGE_SLOTS - len(scaffold['Storage'])):
        scaffold['Storage'].append(None)
        
    return scaffold

# builds/views.py -> workbench_view

@login_required
def workbench_view(request, build_id):
    build = get_object_or_404(Build, pk=build_id, user=request.user)
    
    # Call the helper function to get the scaffold
    scaffold = _get_build_scaffold(build)

    # --- Determine Available Components ---
    components_in_build = BuildComponent.objects.filter(build=build)
    unique_types_in_build = ['CPU', 'Motherboard', 'GPU', 'PSU', 'Case']
    unique_component_ids_to_exclude = []
    for item in components_in_build:
        if item.component.get_type() in unique_types_in_build:
            unique_component_ids_to_exclude.append(item.component.id)
    all_components = Component.objects.exclude(id__in=unique_component_ids_to_exclude).order_by('name')

    # --- Perform Calculations ---
    cpu_item = scaffold['CPU']
    gpu_item = scaffold['GPU']
    
    # Pass these complete items to the updated function.
    bottleneck_level, bottleneck_message = detect_bottleneck(cpu_item, gpu_item)
    # The PSU calculator already uses the correct approach, so it stays the same.
    psu_recommendation = calculate_psu_wattage(components_in_build)

    total_price = build.calculate_total_price()

    context = {
        'build': build,
        'scaffold': scaffold,
        'all_components': all_components,
        'bottleneck_level': bottleneck_level,
        'bottleneck_message': bottleneck_message,
        'psu_recommendation': psu_recommendation,
        'total_price': total_price,
    }

    return render(request, 'builds/workbench.html', context)

# This is the new view for the public share page.
# Notice there is NO @login_required decorator. This page is accessible to everyone.
def share_build_view(request, build_id):
    # We use get_object_or_404 to fetch the build. If a build with this ID
    # doesn't exist, it will automatically show a "Page Not Found" error.
    # CRUCIALLY, we are NOT checking if build.user == request.user.
    build = get_object_or_404(Build, pk=build_id)

    # We use the same powerful _get_build_scaffold helper function.
    # This is a great example of code reuse (DRY principle).
    scaffold = _get_build_scaffold(build)
    
    # We also need to fetch all the components to pass to the PSU calculator.
    components_in_build = BuildComponent.objects.filter(build=build)

    # --- Perform the same calculations as the workbench ---
    # This ensures the public view shows the same intelligence.
    cpu_item = scaffold['CPU']
    gpu_item = scaffold['GPU']
    bottleneck_level, bottleneck_message = detect_bottleneck(cpu_item, gpu_item)
    psu_recommendation = calculate_psu_wattage(components_in_build)
    total_price = build.calculate_total_price()

    # We package up all the data into a context dictionary.
    context = {
        'build': build,
        'scaffold': scaffold,
        'bottleneck_level': bottleneck_level,
        'bottleneck_message': bottleneck_message,
        'psu_recommendation': psu_recommendation,
        'total_price': total_price,
    }

    # We will render a NEW template called 'share_build.html'.
    return render(request, 'builds/share_build.html', context)

# This is the new view for the public guides page.
# It does not require a login.
def guides_view(request):
    # Step 1: Annotate to create the 'total_price' field.
    all_guides = Build.objects.filter(user__is_staff=True).annotate(
        total_price=Sum(
            F('components__price') * F('buildcomponent__quantity'),
            output_field=DecimalField()
        )
    )

    # Step 2: Apply a single, universal filter if a search query exists.
    search_query = request.GET.get('q', None)
    if search_query:
        # We need to tell Cast what kind of text field to use.
        # This is the robust way to do it.
        all_guides = all_guides.annotate(
            total_price_str=Cast('total_price', output_field=CharField())
        ).filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            # Now we filter on the new annotated string field.
            Q(total_price_str__icontains=search_query)
        )

    # Step 3: Order the final, filtered queryset.
    guide_builds = all_guides.order_by('total_price')

    context = {
        'guide_builds': guide_builds,
        'request': request,
    }
    
    if request.htmx:
        return render(request, 'builds/partials/guides_list.html', context)
    
    return render(request, 'builds/guides.html', context)

# This view must be protected. Only logged-in users can clone builds.
@login_required
def clone_build_view(request, build_id):
    # This action should only be performed via a POST request for security.
    if request.method == 'POST':
        # Step 1: Get the original build we want to clone.
        original_build = get_object_or_404(Build, pk=build_id)

        # Step 2: Create a brand new Build instance from scratch.
        # This is more explicit and safer than copying the object.
        new_build = Build.objects.create(
            user=request.user, # Assign to the current logged-in user
            name=f"Copy of {original_build.name}",
            description=original_build.description
        )
        # The date_created is handled automatically by the model.

        # Step 3: Get all the component entries from the original build.
        original_components = original_build.buildcomponent_set.all()

        # Step 4: Loop through the original components and create a new one for each.
        # This is the most reliable way to ensure correct creation.
        for item in original_components:
            BuildComponent.objects.create(
                build=new_build,          # Link to our new build
                component=item.component, # Link to the SAME component
                quantity=item.quantity    # Copy the quantity
            )

        # Step 5: Redirect the user to their new workbench.
        return redirect('builds:workbench', build_id=new_build.id)

    # If someone tries to access this URL with a GET request, just send them home.
    return redirect('home')

@login_required
def delete_build_view(request, build_id):
    # This action must be a POST request for security.
    if request.method == 'POST':
        # Find the build to delete, ensuring it belongs to the current user.
        # This is the same critical security check as in the workbench.
        build_to_delete = get_object_or_404(Build, pk=build_id, user=request.user)
        
        # Perform the delete operation.
        build_to_delete.delete()
        
        # For an HTMX request, we should return an empty response with a 200 OK status.
        # This tells HTMX the operation was successful, and it can proceed with
        # swapping/removing the target element.
        return HttpResponse(status=200)

    # If a user tries to access this URL via GET, it's not allowed.
    # We return a "Forbidden" error.
    return HttpResponseForbidden()

@login_required
def add_component_to_build(request, build_id):
    if request.method == 'POST':
        build = get_object_or_404(Build, pk=build_id, user=request.user)
        component_id = request.POST.get('component_id')
        component_to_add = get_object_or_404(Component, pk=component_id)

        component_type = component_to_add.get_type()
        
        # --- Logic for Unique, Swappable Components ---
        if component_type in ['CPU', 'Motherboard', 'GPU', 'PSU', 'Case']:
            # Find if a component of the same type already exists.
            # This is a much more direct and safer way to query.
            existing_component_item = BuildComponent.objects.filter(
                build=build, 
                component__in=Component.objects.filter(**{f'{component_type.lower()}__isnull': False})
            ).first()

            # If one exists, delete it.
            if existing_component_item:
                existing_component_item.delete()
            
            # Create the new one.
            BuildComponent.objects.create(build=build, component=component_to_add, quantity=1)

            if component_type == 'Motherboard':
                # Get the new motherboard's slot count.
                new_ram_slot_limit = component_to_add.motherboard.ram_slots

                # Get all RAM items currently in the build.
                ram_items_in_build = BuildComponent.objects.filter(
                    build=build,
                    component__ram__isnull=False
                )

                # Calculate the total number of RAM sticks (sum of quantities).
                total_ram_sticks = ram_items_in_build.aggregate(
                    total=models.Sum('quantity')
                )['total'] or 0

                # If we have more sticks than the new limit, we must remove them.
                if total_ram_sticks > new_ram_slot_limit:
                    sticks_to_remove = total_ram_sticks - new_ram_slot_limit
                    
                    # We remove sticks one by one, starting from the last ones added
                    # (or by any consistent order).
                    for ram_item in ram_items_in_build.order_by('-id'):
                        if sticks_to_remove <= 0:
                            break # We've removed enough.
                        
                        if ram_item.quantity <= sticks_to_remove:
                            # If we need to remove more sticks than this item has, delete it entirely.
                            sticks_to_remove -= ram_item.quantity
                            ram_item.delete()
                        else:
                            # If this item has more sticks than we need to remove, just decrease quantity.
                            ram_item.quantity -= sticks_to_remove
                            ram_item.save()
                            sticks_to_remove = 0

        # --- Logic for Stackable Components (RAM, Storage) ---
        else:
            # Check if we are at the slot limit for this type.
            limit = float('inf')  # Default to no limit
            
            # Get the current count of items of this type.
            current_items_count = BuildComponent.objects.filter(
                build=build,
                component__in=Component.objects.filter(**{f'{component_type.lower()}__isnull': False})
            ).aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0

            if component_type == 'RAM':
                motherboard_item = BuildComponent.objects.filter(build=build, component__motherboard__isnull=False).first()
                limit = motherboard_item.component.motherboard.ram_slots if motherboard_item else 4
            elif component_type == 'Storage':
                TOTAL_STORAGE_SLOTS = 2 # As defined in your scaffold logic
                limit = TOTAL_STORAGE_SLOTS

            # Only add the component if we are not at the limit.
            if current_items_count < limit:
                # Try to get the exact same component to increment its quantity.
                build_component, created = BuildComponent.objects.get_or_create(
                    build=build,
                    component=component_to_add,
                    defaults={'quantity': 1}
                )
                if not created:
                    build_component.quantity += 1
                    build_component.save()
        
        # --- This part remains the same ---
        # After any modification, re-render the scaffold and send it back.
        scaffold = _get_build_scaffold(build)
        context = {'scaffold': scaffold, 'build': build}
        
        html = render(request, 'builds/partials/scaffold_list.html', context)
        response = HttpResponse(html)
        response['HX-Trigger'] = 'componentAdded'
        return response

    return redirect('home')

@login_required
def update_build_status(request, build_id):
    build = get_object_or_404(Build, pk=build_id, user=request.user)
    
    # === SIMPLIFIED LOGIC ===
    # 1. Get the perfectly prepared scaffold.
    scaffold = _get_build_scaffold(build)
    
    # 2. Get all components for the PSU calculation.
    components_in_build = BuildComponent.objects.filter(build=build).select_related('component')

    # 3. Extract the CPU and GPU directly from the scaffold.
    # The .component is the base Component, .component.cpu is the specific CPU child.
    cpu_item = scaffold['CPU']
    gpu_item = scaffold['GPU']

    # Pass these complete items to our robust detect_bottleneck function.
    bottleneck_level, bottleneck_message = detect_bottleneck(cpu_item, gpu_item)
    # The PSU calculator was already correct, so it stays the same.
    psu_recommendation = calculate_psu_wattage(components_in_build)

    total_price = build.calculate_total_price()

    context = {
        'bottleneck_level': bottleneck_level,
        'bottleneck_message': bottleneck_message,
        'psu_recommendation': psu_recommendation,
        'total_price': total_price,
    }
    
    return render(request, 'builds/partials/system_status.html', context)

@login_required
def remove_component_from_build(request, build_id):
    if request.method == 'POST':
        build = get_object_or_404(Build, pk=build_id, user=request.user)
        component_id_to_remove = request.POST.get('component_id')
        
        try:
            item_to_remove = BuildComponent.objects.get(
                build=build, 
                component_id=component_id_to_remove
            )
            
            if item_to_remove.quantity > 1:
                item_to_remove.quantity -= 1
                item_to_remove.save()
            else:
                item_to_remove.delete()
        except BuildComponent.DoesNotExist:
            pass # Ignore if it's already gone

        # === THE SIMPLIFIED PART ===
        # After removing, just call the master helper function.
        scaffold = _get_build_scaffold(build)
        context = {'scaffold': scaffold, 'build': build} # Pass build for the remove URL
        
        html = render(request, 'builds/partials/scaffold_list.html', context)
        response = HttpResponse(html)
        response['HX-Trigger'] = 'componentRemoved'
        return response

    return redirect('home')

# This is our new view dedicated to searching for available components.
@login_required
def search_components(request, build_id):
    # Get the search term from the query parameters (e.g., /search/?q=intel)
    search_term = request.GET.get('q', '')

    # We still need the build to know which components to exclude.
    build = get_object_or_404(Build, pk=build_id, user=request.user)
    
    components_in_build = BuildComponent.objects.filter(build=build)
    
    # Get the IDs of components that are of a "unique" type (CPU, Mobo, etc.)
    # so we can exclude them from the search results if they are already in the build.
    unique_types_in_build = ['CPU', 'Motherboard', 'GPU', 'PSU', 'Case']
    unique_component_ids_to_exclude = []
    for item in components_in_build:
        if item.component.get_type() in unique_types_in_build:
            unique_component_ids_to_exclude.append(item.component.id)

    # Start with all components, excluding the unique ones already in the build.
    available_components = Component.objects.exclude(id__in=unique_component_ids_to_exclude)

    # If a search term was provided, filter the queryset.
    if search_term:
        # Q objects are used for complex queries. This line means:
        # "WHERE name CONTAINS search_term OR manufacturer CONTAINS search_term"
        # The 'i' in 'icontains' makes the search case-insensitive.
        available_components = available_components.filter(
            Q(name__icontains=search_term) | Q(manufacturer__icontains=search_term)
        )

    context = {
        'build': build,
        'all_components': available_components.order_by('name') # Pass the filtered list
    }

    # Render and return the partial template containing ONLY the list.
    return render(request, 'builds/partials/available_components_list.html', context)

@login_required
def get_build_edit_form(request, build_id):
    build = get_object_or_404(Build, pk=build_id, user=request.user)
    # Create a form instance pre-filled with the build's current data
    form = BuildForm(instance=build)
    context = {'build': build, 'form': form}
    # Return the edit form partial
    return render(request, 'builds/partials/build_card_edit.html', context)

@login_required
def save_build_changes(request, build_id):
    build = get_object_or_404(Build, pk=build_id, user=request.user)
    if request.method == 'POST':
        # Create a form instance with the submitted data AND the original build instance
        form = BuildForm(request.POST, instance=build)
        if form.is_valid():
            form.save() # Save the changes to the database
            # After saving, return the "view" partial with the updated data
            context = {'build': build, 'request': request} # Pass request for the absolute URL
            return render(request, 'builds/partials/build_card_view.html', context)
    # If form is not valid, return the edit form again with errors
    context = {'build': build, 'form': form}
    return render(request, 'builds/partials/build_card_edit.html', context)

@login_required
def get_view_card(request, build_id):
    """A simple view to handle the 'Cancel' action by returning the view partial."""
    build = get_object_or_404(Build, pk=build_id, user=request.user)
    context = {'build': build, 'request': request}
    return render(request, 'builds/partials/build_card_view.html', context)
#_________________________________________________________________________________________________________________________