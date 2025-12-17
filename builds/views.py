# builds/views.py

#_________________________________________________________________________________________________________________________ (akn)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Build, BuildComponent
from catalog.models import Component
from django.shortcuts import get_object_or_404
from .logic import detect_bottleneck, calculate_psu_wattage
from django.db.models import Q
from django.http import HttpResponse
from django.db import models
from .forms import BuildForm

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
        builds = Build.objects.filter(user=request.user).order_by('-date_created')
    
    # We create an empty instance of the form to display on the page.
    form = BuildForm()
    
    context = {
        'builds': builds,
        'form': form, # Add the form to the context
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

@login_required
def add_component_to_build(request, build_id):
    if request.method == 'POST':
        build = get_object_or_404(Build, pk=build_id, user=request.user)
        component_id = request.POST.get('component_id')
        component = get_object_or_404(Component, pk=component_id)

        component_type = component.get_type()
        UNIQUE_COMPONENT_TYPES = ['CPU', 'Motherboard', 'GPU', 'PSU', 'Case']

        if component_type in UNIQUE_COMPONENT_TYPES:
            # This logic is for swapping a unique component like a CPU.
            # It finds any existing component of the same type and deletes it.
            BuildComponent.objects.filter(
                build=build,
                component__in=Component.objects.filter(**{f'{component_type.lower()}__isnull': False})
            ).delete()
            BuildComponent.objects.create(build=build, component=component, quantity=1)
        else:
            # This logic handles stackable items like RAM and Storage.
            # 1. Find the motherboard to check slot limits (for RAM).
            motherboard_item = BuildComponent.objects.filter(build=build, component__motherboard__isnull=False).first()
            ram_slots_total = motherboard_item.component.motherboard.ram_slots if motherboard_item else 4
            
            # 2. Count current sticks/drives.
            current_items_count = BuildComponent.objects.filter(
                build=build,
                component__in=Component.objects.filter(**{f'{component_type.lower()}__isnull': False})
            ).aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0

            # 3. Check limits before adding.
            limit = float('inf') # Default to no limit
            if component_type == 'RAM':
                limit = ram_slots_total
            elif component_type == 'Storage':
                # We defined this in our helper function, let's use it here too.
                TOTAL_STORAGE_SLOTS = 2
                limit = TOTAL_STORAGE_SLOTS

            if current_items_count < limit:
                build_component, created = BuildComponent.objects.get_or_create(
                    build=build,
                    component=component,
                    defaults={'quantity': 1}
                )
                if not created:
                    build_component.quantity += 1
                    build_component.save()
        
        # === THE SIMPLIFIED PART ===
        # After any modification, just call the master helper function.
        scaffold = _get_build_scaffold(build)
        context = {'scaffold': scaffold, 'build': build} # Pass build for the remove URL
        
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
#_________________________________________________________________________________________________________________________