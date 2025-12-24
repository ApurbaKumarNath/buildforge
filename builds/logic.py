# builds/logic.py

#__________________________________________________________________________________________________________________________ (akn)

def detect_bottleneck(cpu_item, gpu_item):
    """
    Analyzes a CPU and GPU BuildComponent item pair using a tier system.
    This is the robust method, as the item contains the link to the component.
    """
    if not cpu_item or not gpu_item:
        return ('none', 'Select a CPU and GPU to check for bottlenecks.')

    # THE FIX: We access the parent component directly from the item.
    # This is guaranteed to be the full Component object with all its fields.
    cpu_component = cpu_item.component
    gpu_component = gpu_item.component

    tier_map = {'Entry': 1, 'Mid': 2, 'High': 3}
    
    # Now, this access is guaranteed to work because we are on the Component model.
    cpu_tier = tier_map.get(cpu_component.performance_tier, 0)
    gpu_tier = tier_map.get(gpu_component.performance_tier, 0)

    if cpu_tier == 0 or gpu_tier == 0:
        return ('info', 'Performance tier not set for CPU or GPU.')

    tier_difference = abs(cpu_tier - gpu_tier)

    if tier_difference >= 2:
        level = 'major'
        if cpu_tier > gpu_tier:
            message = f"Major Bottleneck: Your '{cpu_component.name}' is significantly more powerful than your '{gpu_component.name}'. The GPU will severely limit performance."
        else:
            message = f"Major Bottleneck: Your '{gpu_component.name}' is significantly more powerful than your '{cpu_component.name}'. The CPU will severely limit performance."
    elif tier_difference == 1:
        level = 'minor'
        if cpu_tier > gpu_tier:
            message = f"Minor Bottleneck Risk: Your '{cpu_component.name}' is in a higher performance tier than your '{gpu_component.name}'. This is generally okay."
        else:
            message = f"Minor Bottleneck Risk: Your '{gpu_component.name}' is in a higher performance tier than your '{cpu_component.name}'. This is generally okay."
    else:
        level = 'good'
        message = 'CPU and GPU are well-balanced.'
    
    return (level, message)

def calculate_psu_wattage(components_in_build):
    """
    Calculates a recommended PSU wattage by summing the actual TDP values
    of all components in the build from the database.
    """
    total_tdp = 0
    
    # We can add a small base value to account for things that don't have a TDP,
    # like motherboard chipsets, fans, and SSDs. 50W is a safe estimate.
    base_power_others = 50
    total_tdp += base_power_others

    # Loop through every single item in the build.
    for item in components_in_build:
        # Get the actual component object.
        component = item.component
        
        # Check if the component has a valid TDP value in the database.
        # The 'is not None' check is important to avoid errors if TDP is blank.
        if component.tdp is not None and component.tdp > 0:
            # Add the component's TDP multiplied by its quantity to the total.
            total_tdp += (component.tdp * item.quantity)

    # If the total is still just our base value, it means no components with TDP were found.
    if total_tdp <= base_power_others:
        return "Add components with TDP values (like a CPU or GPU) to estimate wattage."

    # Add a safety margin for efficiency and future upgrades.
    # 1.3 to 1.5 is a good range (30-50% headroom). Let's use 1.4 for a 40% margin.
    recommended_wattage = total_tdp * 1.4

    # Round up to the nearest common PSU wattage for a clean recommendation.
    standard_psu_sizes = [450, 550, 650, 750, 850, 1000, 1200, 1600]
    for size in standard_psu_sizes:
        if size >= recommended_wattage:
            # Provide a more informative message to the user.
            return f"Recommended PSU: ~{size}W (Estimated Load: {total_tdp}W)"
            
    # If the build is extremely high-power, recommend the highest standard size.
    return f"Recommended PSU: >{standard_psu_sizes[-1]}W (High-power build, Estimated Load: {total_tdp}W)"

#__________________________________________________________________________________________________________________________ 