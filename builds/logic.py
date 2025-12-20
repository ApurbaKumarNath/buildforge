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
    Calculates a recommended PSU wattage based on the components in a build.
    Since we don't have real TDP, we'll use estimates based on performance tier.
    """
    total_tdp = 0
    
   
    # Base power draw for other components
    base_power_others = 50  # Motherboard, RAM, fans, etc.
    total_tdp += base_power_others

    for item in components_in_build:
        component = item.component
        
        
        if component.tdp:
           
            total_tdp += component.tdp * item.quantity

    if total_tdp <= base_power_others:
        return "Add a CPU and GPU to estimate wattage."

    # Add a safety margin (e.g., 30% headroom)
    recommended_wattage = total_tdp * 1.3

    # Round up to the nearest common PSU wattage (e.g., 550, 650, 750)
    standard_psu_sizes = [450, 550, 650, 750, 850, 1000, 1200, 1600]
    for size in standard_psu_sizes:
        if size >= recommended_wattage:
            return f"Recommended PSU: ~{size}W (Estimated load: {total_tdp}W)"
            
    return f"Recommended PSU: >{standard_psu_sizes[-1]}W (High-power build)"

#__________________________________________________________________________________________________________________________ 